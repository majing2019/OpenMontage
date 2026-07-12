"""Emotion × Scene matrix — pre-seeded story concepts for quick ideation.

8 emotions × 10 scenes × 2-3 seeds each = ~200 story starters.
Each seed references a story pattern from _patterns.py.

All data lives in emotion_matrix.yaml. Add emotions, scenes, or seeds there —
no code changes required.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Public data (loaded from YAML at import time)
# ---------------------------------------------------------------------------

EMOTIONS: list[str] = []
SCENES: list[str] = []
DAILY_OBSERVATIONS: list[str] = []

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MatrixSeed:
    """One story concept from the emotion-scene matrix."""

    title: str
    logline: str
    hook: str
    pattern_name: str
    character_roles: list[str] = field(default_factory=list)
    twist_hint: str = ""
    visual_keywords: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Matrix loading (auto-discovers all entries in YAML)
# ---------------------------------------------------------------------------

_MATRIX: dict[str, dict[str, list[MatrixSeed]]] = {}
_YAML_PATH = Path(__file__).parent / "emotion_matrix.yaml"
_LOADED = False


def _load_matrix() -> None:
    """Load the emotion-scene matrix from YAML at import time.

    To add emotions/scenes/seeds: edit emotion_matrix.yaml. No code changes needed.
    """
    global EMOTIONS, SCENES, DAILY_OBSERVATIONS, _MATRIX, _LOADED
    if _LOADED:
        return

    import yaml

    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    EMOTIONS = list(data.get("emotions", []))
    SCENES = list(data.get("scenes", []))
    DAILY_OBSERVATIONS = list(data.get("daily_observations", []))

    raw_matrix: dict = data.get("matrix", {})
    for emotion, scenes in raw_matrix.items():
        _MATRIX[emotion] = {}
        for scene, seed_list in (scenes or {}).items():
            _MATRIX[emotion][scene] = [
                MatrixSeed(
                    title=s.get("title", ""),
                    logline=s.get("logline", ""),
                    hook=s.get("hook", ""),
                    pattern_name=s.get("pattern_name", ""),
                    character_roles=list(s.get("character_roles", [])),
                    twist_hint=s.get("twist_hint", ""),
                    visual_keywords=list(s.get("visual_keywords", [])),
                )
                for s in (seed_list or [])
            ]

    _LOADED = True


def reload_matrix() -> None:
    """Force-reload the matrix from YAML (e.g. after editing the file)."""
    global _MATRIX, EMOTIONS, SCENES, DAILY_OBSERVATIONS, _LOADED
    _MATRIX = {}
    EMOTIONS = []
    SCENES = []
    DAILY_OBSERVATIONS = []
    _LOADED = False
    _load_matrix()


# ── Public API (identical to before — all callers unchanged) ────────────


# Eager-load at import time so EMOTIONS / SCENES / DAILY_OBSERVATIONS
# are populated before callers read them as module-level constants.
_load_matrix()


def get_seeds(emotion: str | None, scene: str | None) -> list[MatrixSeed]:
    """Retrieve seeds from the matrix, with optional filtering."""
    seeds: list[MatrixSeed] = []

    emotions = [emotion] if emotion else EMOTIONS
    scenes = [scene] if scene else SCENES

    for e in emotions:
        for s in scenes:
            seeds.extend(_MATRIX.get(e, {}).get(s, []))

    return seeds


def get_random_seed(
    emotion: str | None = None,
    scene: str | None = None,
    rng: random.Random | None = None,
) -> MatrixSeed | None:
    """Get a random seed from the matrix, optionally filtered."""
    rng = rng or random.Random()
    seeds = get_seeds(emotion, scene)
    return rng.choice(seeds) if seeds else None
