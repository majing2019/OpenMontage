"""Pipeline manifest loader.

Loads and validates pipeline YAML manifests from pipeline_defs/.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import yaml
import jsonschema

PIPELINE_DEFS_DIR = Path(__file__).resolve().parent.parent / "pipeline_defs"
SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "schemas"
    / "pipelines"
    / "pipeline_manifest.schema.json"
)


def _load_manifest_schema() -> dict:
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_pipeline(name: str, defs_dir: Optional[Path] = None) -> dict[str, Any]:
    """Load and validate a pipeline manifest by name.

    Args:
        name: Pipeline name (without .yaml extension).
        defs_dir: Override directory for pipeline definitions.

    Returns:
        Validated pipeline manifest dict.
    """
    defs_dir = defs_dir or PIPELINE_DEFS_DIR
    path = defs_dir / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Pipeline manifest not found: {path}")

    with open(path) as f:
        manifest = yaml.safe_load(f)

    schema = _load_manifest_schema()
    jsonschema.validate(instance=manifest, schema=schema)

    return manifest


def list_pipelines(defs_dir: Optional[Path] = None) -> list[str]:
    """List all available pipeline manifest names."""
    defs_dir = defs_dir or PIPELINE_DEFS_DIR
    return [p.stem for p in defs_dir.glob("*.yaml")]


def _condition_is_active(condition: Optional[str], context: Optional[dict[str, Any]]) -> bool:
    """Evaluate a simple manifest condition against runtime context."""
    if not condition:
        return True
    if not context:
        return False
    return bool(context.get(condition))


def get_reference_input_config(manifest: dict) -> dict[str, Any]:
    """Return reference-input configuration, defaulting to disabled."""
    return manifest.get("reference_input", {}) or {}


def pipeline_supports_reference_input(manifest: dict) -> bool:
    """Whether the manifest declares support for reference-video input."""
    return bool(get_reference_input_config(manifest).get("supported", False))


def get_stage_sub_stages(
    manifest: dict,
    stage_name: str,
    *,
    context: Optional[dict[str, Any]] = None,
    include_inactive: bool = True,
) -> list[dict[str, Any]]:
    """Return sub-stage definitions for a stage.

    By default this returns all declared sub-stages so agents can inspect the
    full workflow shape. Pass ``include_inactive=False`` with context to filter
    to active sub-stages only.
    """
    for stage in manifest["stages"]:
        if stage["name"] != stage_name:
            continue
        sub_stages = list(stage.get("sub_stages", []))
        if include_inactive:
            return sub_stages
        return [
            sub_stage
            for sub_stage in sub_stages
            if _condition_is_active(sub_stage.get("condition"), context)
        ]
    return []


def get_stage_order(
    manifest: dict,
    *,
    include_sub_stages: bool = False,
    context: Optional[dict[str, Any]] = None,
) -> list[str]:
    """Extract the ordered list of stage names from a manifest.

    ``include_sub_stages=True`` exposes declarative sample/preview units to the
    agent without turning them into mandatory checkpoint stages. Sub-stages are
    emitted as ``<stage>.<sub_stage>``.
    """
    order: list[str] = []
    for stage in manifest["stages"]:
        order.append(stage["name"])
        if not include_sub_stages:
            continue
        for sub_stage in get_stage_sub_stages(
            manifest,
            stage["name"],
            context=context,
            include_inactive=context is None,
        ):
            order.append(f"{stage['name']}.{sub_stage['name']}")
    return order


def get_required_tools(manifest: dict) -> set[str]:
    """Collect tools across stages, sub-stages, and reference-input analysis."""
    tools: set[str] = set()
    for stage in manifest["stages"]:
        tools.update(stage.get("preferred_tools", []))
        tools.update(stage.get("fallback_tools", []))
        tools.update(stage.get("tools_available", []))
        for sub_stage in stage.get("sub_stages", []):
            tools.update(sub_stage.get("tools_available", []))
    tools.update(get_reference_input_config(manifest).get("analysis_tools", []))
    return tools


def get_stage_skill(manifest: dict, stage_name: str) -> Optional[str]:
    """Get the skill path for an instruction-driven stage."""
    for stage in manifest["stages"]:
        if stage["name"] == stage_name:
            return stage.get("skill")
    return None


def get_stage_review_focus(manifest: dict, stage_name: str) -> list[str]:
    """Get the review focus items for a stage."""
    for stage in manifest["stages"]:
        if stage["name"] == stage_name:
            return stage.get("review_focus", [])
    return []


# ---------------------------------------------------------------------------
# Capability-Extension Enforcement
# ---------------------------------------------------------------------------

class ExtensionNotPermitted(PermissionError):
    """Raised when a capability extension is used but not permitted by the pipeline."""


def check_extension_permitted(
    manifest: dict,
    extension_type: str,
) -> None:
    """Enforce that a capability extension is permitted by the pipeline manifest.

    Args:
        manifest: Loaded pipeline manifest dict.
        extension_type: One of 'custom_scripts', 'custom_playbooks',
                        'custom_skills', 'custom_tools'.

    Raises:
        ExtensionNotPermitted: If the extension is not allowed.
    """
    valid_extensions = {"custom_scripts", "custom_playbooks", "custom_skills", "custom_tools"}
    if extension_type not in valid_extensions:
        raise ValueError(
            f"Unknown extension type {extension_type!r}. "
            f"Valid types: {sorted(valid_extensions)}"
        )

    extensions = manifest.get("extensions", {})
    if not extensions.get(extension_type, False):
        raise ExtensionNotPermitted(
            f"Pipeline {manifest.get('name', 'unknown')!r} does not permit "
            f"{extension_type}. Set extensions.{extension_type}: true in the "
            f"pipeline manifest to allow this."
        )


def get_permitted_extensions(manifest: dict) -> dict[str, bool]:
    """Return the extension permission flags for a pipeline."""
    defaults = {
        "custom_scripts": False,
        "custom_playbooks": False,
        "custom_skills": False,
        "custom_tools": False,
    }
    extensions = manifest.get("extensions", {})
    return {k: extensions.get(k, v) for k, v in defaults.items()}


# ---------------------------------------------------------------------------
# Agent Skills — Layer 3 knowledge required for quality output
# ---------------------------------------------------------------------------

def get_agent_skills(manifest: dict) -> dict[str, list[str]]:
    """Return the agent_skills declared by the pipeline manifest.

    Returns a dict keyed by capability domain (e.g. 'prompt_craft', 'composition',
    'animation', 'quality'), each value a list of skill names.

    Returns an empty dict when the manifest does not declare agent_skills.
    """
    return dict(manifest.get("agent_skills", {}) or {})


def get_all_agent_skill_names(manifest: dict) -> list[str]:
    """Return a flat, deduplicated list of all agent skill names across all domains."""
    seen: set[str] = set()
    result: list[str] = []
    for skills in get_agent_skills(manifest).values():
        for name in skills:
            if name not in seen:
                seen.add(name)
                result.append(name)
    return result


AGENT_SKILL_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"


def resolve_agent_skill_path(skill_name: str) -> Optional[Path]:
    """Resolve an agent skill name to its SKILL.md path on disk.

    Returns None when the skill directory or SKILL.md does not exist.
    """
    skill_dir = AGENT_SKILL_DIR / skill_name
    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_file():
        return skill_file
    return None


def validate_agent_skills(manifest: dict) -> dict[str, list[str]]:
    """Check that all declared agent_skills exist on disk.

    Returns ``{'found': [...], 'missing': [...]}`` so callers can surface
    missing skills without failing the entire pipeline load.
    """
    found: list[str] = []
    missing: list[str] = []
    for name in get_all_agent_skill_names(manifest):
        if resolve_agent_skill_path(name):
            found.append(name)
        else:
            missing.append(name)
    return {"found": found, "missing": missing}
