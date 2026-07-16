"""Prompt Validator — enforce skill-derived rules on generated prompts.

Architecture:
    1. Each skill in .agents/skills/<name>/ can contain a rules.json
    2. The validator reads which skills are active from the pipeline manifest's agent_skills
    3. Auto-discovers rules from each active skill directory
    4. Validates image/video prompts against aggregated rules
    5. Returns a pass/fail report with specific violations

Extensibility:
    Add a new skill → drop it in .agents/skills/<name>/ with a rules.json →
    add the skill name to the pipeline manifest's agent_skills →
    validator picks it up automatically. No code changes needed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

AGENT_SKILLS_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rule_name: str
    passed: bool
    detail: str = ""
    source_skill: str = ""


@dataclass
class ValidationReport:
    prompt_type: str          # "image" or "video"
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        lines = [f"Prompt validation ({self.prompt_type}): {status}"]
        for c in self.checks:
            icon = "✅" if c.passed else "❌"
            lines.append(f"  {icon} [{c.source_skill}] {c.rule_name}: {c.detail}")
        if self.violations:
            lines.append("Violations:")
            for v in self.violations:
                lines.append(f"  - {v}")
        if self.suggestions:
            lines.append("Suggestions:")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rule loading
# ---------------------------------------------------------------------------

def _load_skill_rules(skill_name: str) -> Optional[dict[str, Any]]:
    """Load rules.json from a skill directory, if it exists."""
    rules_path = AGENT_SKILLS_DIR / skill_name / "rules.json"
    if not rules_path.is_file():
        return None
    try:
        with open(rules_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def discover_rules(skill_names: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Load and merge prompt_checks from all active skills.

    Returns:
        {"image": [rule_dict, ...], "video": [rule_dict, ...]}
    """
    merged: dict[str, list[dict[str, Any]]] = {"image": [], "video": []}
    for name in skill_names:
        rules = _load_skill_rules(name)
        if not rules:
            continue
        for prompt_type in ("image", "video"):
            checks = rules.get("prompt_checks", {}).get(prompt_type, [])
            if isinstance(checks, list):
                for check in checks:
                    check["_source_skill"] = name
                    merged[prompt_type].append(check)
    return merged


# ---------------------------------------------------------------------------
# Validation engine
# ---------------------------------------------------------------------------

def _check_required_pattern(prompt: str, pattern: str, source: str) -> CheckResult:
    """Check that a literal substring or regex pattern exists in the prompt."""
    if pattern.startswith("regex:"):
        import re
        pat = pattern.removeprefix("regex:")
        passed = bool(re.search(pat, prompt))
    else:
        passed = pattern in prompt
    detail = f"Found '{pattern[:60]}'" if passed else f"Missing '{pattern[:60]}'"
    return CheckResult(
        rule_name=f"required: {pattern[:50]}",
        passed=passed,
        detail=detail,
        source_skill=source,
    )


def _check_forbidden_pattern(prompt: str, pattern: str, source: str) -> CheckResult:
    """Check that a forbidden substring or regex does NOT appear."""
    if pattern.startswith("regex:"):
        import re
        pat = pattern.removeprefix("regex:")
        found = bool(re.search(pat, prompt))
    else:
        found = pattern in prompt
    detail = f"Forbidden '{pattern[:60]}' NOT found" if not found else f"Forbidden '{pattern[:60]}' FOUND"
    return CheckResult(
        rule_name=f"forbidden: {pattern[:50]}",
        passed=not found,
        detail=detail,
        source_skill=source,
    )


def _check_min_length(prompt: str, min_chars: int, source: str) -> CheckResult:
    passed = len(prompt) >= min_chars
    detail = f"Length {len(prompt)} >= {min_chars}" if passed else f"Length {len(prompt)} < {min_chars}"
    return CheckResult(
        rule_name=f"min_length: {min_chars} chars",
        passed=passed,
        detail=detail,
        source_skill=source,
    )


def _check_min_count(prompt: str, pattern: str, min_count: int, source: str) -> CheckResult:
    count = prompt.count(pattern)
    passed = count >= min_count
    detail = f"'{pattern[:40]}' appears {count} times (min {min_count})" if passed else f"'{pattern[:40]}' appears {count} times (need {min_count})"
    return CheckResult(
        rule_name=f"min_count: '{pattern[:30]}' >= {min_count}",
        passed=passed,
        detail=detail,
        source_skill=source,
    )


def validate(prompt: str, prompt_type: str, skill_names: list[str]) -> ValidationReport:
    """Validate a prompt against all rules from the given skills.

    Args:
        prompt: The prompt text to validate.
        prompt_type: "image" or "video".
        skill_names: List of skill names whose rules should be applied.

    Returns:
        ValidationReport with pass/fail and per-rule results.
    """
    if prompt_type not in ("image", "video"):
        return ValidationReport(
            prompt_type=prompt_type,
            passed=False,
            violations=[f"Unknown prompt_type '{prompt_type}'. Must be 'image' or 'video'."],
        )

    all_rules = discover_rules(skill_names)
    rules = all_rules.get(prompt_type, [])

    if not rules:
        return ValidationReport(
            prompt_type=prompt_type,
            passed=True,
            suggestions=[f"No rules found for prompt_type='{prompt_type}' in skills: {skill_names}"],
        )

    checks: list[CheckResult] = []
    violations: list[str] = []
    suggestions: list[str] = []

    for rule in rules:
        source = rule.get("_source_skill", "unknown")
        check_type = rule.get("type", "required_pattern")

        if check_type == "required_pattern":
            c = _check_required_pattern(prompt, rule["pattern"], source)
        elif check_type == "forbidden_pattern":
            c = _check_forbidden_pattern(prompt, rule["pattern"], source)
        elif check_type == "min_length":
            c = _check_min_length(prompt, rule.get("min_chars", 100), source)
        elif check_type == "min_count":
            c = _check_min_count(prompt, rule["pattern"], rule.get("min_count", 1), source)
        else:
            c = CheckResult(
                rule_name=f"unknown_type: {check_type}",
                passed=True,
                detail=f"Unknown rule type '{check_type}' — skipped",
                source_skill=source,
            )

        checks.append(c)
        if not c.passed:
            violations.append(f"[{c.source_skill}] {c.rule_name}: {c.detail}")
            suggestion = rule.get("suggestion", "")
            if suggestion:
                suggestions.append(f"[{c.source_skill}] {suggestion}")

    all_passed = len(violations) == 0
    return ValidationReport(
        prompt_type=prompt_type,
        passed=all_passed,
        checks=checks,
        violations=violations,
        suggestions=suggestions,
    )


def validate_from_manifest(prompt: str, prompt_type: str, manifest: dict) -> ValidationReport:
    """Convenience: validate using agent_skills declared in a pipeline manifest."""
    from lib.pipeline_loader import get_all_agent_skill_names
    skill_names = get_all_agent_skill_names(manifest)
    return validate(prompt, prompt_type, skill_names)
