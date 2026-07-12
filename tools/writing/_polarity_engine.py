"""Polarity collision engine — collides opposite poles to produce one-liner stories.

Sources:
- McKee "Story" — Story Climax as collision of opposing forces
- Egri "The Art of Dramatic Writing" — Dialectical conflict (thesis × antithesis)
- Truby "The Anatomy of Story" — Story Need as gap between poles

Zero external dependencies — loads dimensions from polarity_dims.yaml at runtime.
Add new dimensions to the YAML file; no code changes required.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Pole:
    """One end of a polarity dimension."""
    value: str
    is_pole_a: bool  # True = low/stark end, False = high/power end


@dataclass
class PolarityCollision:
    """One collision result: pole_a × pole_b via trigger."""

    dimension_name: str
    dimension_name_en: str
    pole_a: str
    pole_b: str
    trigger: str
    one_liner: str            # The generated story hook
    confidence: int           # 1-5, from the source dimension
    suggested_emotion: str   # Emotion this collision tends to produce
    pattern_hint: str         # Story pattern that fits this collision type


# ---------------------------------------------------------------------------
# Dimension loading (auto-discovers all entries in YAML)
# ---------------------------------------------------------------------------

_DIMENSIONS_CACHE: list[dict] | None = None
_YAML_PATH = Path(__file__).parent / "polarity_dims.yaml"


def load_dimensions() -> list[dict]:
    """Load all polarity dimensions from the YAML file.

    Returns a list of dimension dicts, each containing:
      - name, name_en, description, confidence
      - pole_a.values (list[str])
      - pole_b.values (list[str])
      - collision_triggers (list[str])

    Auto-discovers new dimensions added to the YAML — no code changes needed.
    """
    global _DIMENSIONS_CACHE
    if _DIMENSIONS_CACHE is not None:
        return _DIMENSIONS_CACHE

    import yaml

    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    _DIMENSIONS_CACHE = list(data.get("dimensions") or [])
    return _DIMENSIONS_CACHE


def reload_dimensions() -> list[dict]:
    """Force-reload dimensions from YAML (e.g. after editing the file)."""
    global _DIMENSIONS_CACHE
    _DIMENSIONS_CACHE = None
    return load_dimensions()


def get_dimension_names() -> list[str]:
    """Return all available dimension names."""
    dims = load_dimensions()
    return [d["name"] for d in dims]


# ---------------------------------------------------------------------------
# Emotion / pattern mapping per dimension
# ---------------------------------------------------------------------------

# Each dimension has a bias toward certain emotions and story patterns.
# This mapping is used to generate suggested_emotion and pattern_hint.
# New dimensions default to generic values if not listed here.
DIMENSION_EMOTION_MAP: dict[str, list[str]] = {
    "消费层级": ["心酸", "温暖", "好笑"],
    "社交能量": ["好笑", "惊讶", "治愈"],
    "身份层级": ["紧张", "惊讶", "心酸"],
    "情感距离": ["心酸", "感动", "治愈"],
    "时间": ["感动", "心酸", "治愈"],
    "公开/私密": ["好笑", "紧张", "愤怒"],
    "给予/索取": ["感动", "心酸", "温暖"],
    "沉默/爆发": ["惊讶", "愤怒", "感动"],
    "地盘/领地": ["心酸", "惊讶", "治愈"],
    "期待/落差": ["心酸", "愤怒", "惊讶"],
}

DIMENSION_PATTERN_MAP: dict[str, list[str]] = {
    "消费层级": ["日常英雄", "误会连环", "亲情反转"],
    "社交能量": ["身份反转", "奇葩逻辑", "社死瞬间"],
    "身份层级": ["身份反转", "瞬间决定", "隐藏真相"],
    "情感距离": ["亲情反转", "时光对比", "陌生人温暖"],
    "时间": ["时光对比", "如果当初", "日常英雄"],
    "公开/私密": ["社死瞬间", "误会连环", "奇葩逻辑"],
    "给予/索取": ["日常英雄", "陌生人温暖", "亲情反转"],
    "沉默/爆发": ["身份反转", "瞬间决定", "隐藏真相"],
    "地盘/领地": ["时光对比", "隐藏真相", "亲情反转"],
    "期待/落差": ["瞬间决定", "反转倒置", "隐藏真相"],
}

_FALLBACK_EMOTIONS = ["心酸", "温暖", "惊讶", "好笑"]
_FALLBACK_PATTERNS = ["日常英雄", "亲情反转", "瞬间决定"]


# ---------------------------------------------------------------------------
# One-liner generation
# ---------------------------------------------------------------------------

_ONE_LINER_TEMPLATES: list[str] = [
    # Template with {pole_a}, {pole_b}, {trigger}
    "{pole_a}——{trigger}。{pole_b}。",
    "{trigger}。{pole_a}，{pole_b}。",
    "{pole_b}遇到了{pole_a}——{trigger}。",
    "你以为{pole_a}和{pole_b}不会有交集——直到{trigger}。",
    "{pole_a}。{pole_b}。{trigger}。",
]

_COMPACT_TEMPLATES: list[str] = [
    "{pole_a}撞上了{pole_b}——{trigger}",
    "{trigger}：{pole_a} × {pole_b}",
]


def _build_one_liner(
    pole_a: str,
    pole_b: str,
    trigger: str,
    compact: bool = False,
) -> str:
    """Assemble a one-liner from poles and trigger."""
    templates = _COMPACT_TEMPLATES if compact else _ONE_LINER_TEMPLATES
    template = random.choice(templates)
    return template.format(pole_a=pole_a, pole_b=pole_b, trigger=trigger)


# ---------------------------------------------------------------------------
# Core collision logic
# ---------------------------------------------------------------------------


def collide(
    dimension_name: str | None = None,
    count: int = 1,
    rng: random.Random | None = None,
    compact: bool = False,
) -> list[PolarityCollision]:
    """Generate story one-liners by colliding poles from polarity dimensions.

    Args:
        dimension_name: Optional specific dimension to use. None = random selection.
        count: Number of collisions to generate.
        rng: Random instance for reproducibility. None = creates its own.
        compact: If True, generate shorter one-liners (for pitch mode).

    Returns:
        List of PolarityCollision results.

    To add new dimensions: edit polarity_dims.yaml. No code changes needed.
    """
    rng = rng or random.Random()
    dims = load_dimensions()

    if dimension_name:
        dims = [d for d in dims if d["name"] == dimension_name]
        if not dims:
            return []

    results: list[PolarityCollision] = []
    used_combos: set[tuple[str, str, str]] = set()

    # Track which dimensions we've used to spread diversity
    dim_pool = list(dims)

    for _ in range(count):
        # Try up to 3 times to find a unique combination
        for _ in range(3):
            dim = rng.choice(dim_pool)
            pole_a = rng.choice(dim["pole_a"]["values"])
            pole_b = rng.choice(dim["pole_b"]["values"])
            trigger = rng.choice(dim["collision_triggers"])

            combo = (pole_a, pole_b, trigger)
            if combo not in used_combos:
                used_combos.add(combo)
                break
        else:
            # All combos exhausted (unlikely), just pick random
            dim = rng.choice(dim_pool)
            pole_a = rng.choice(dim["pole_a"]["values"])
            pole_b = rng.choice(dim["pole_b"]["values"])
            trigger = rng.choice(dim["collision_triggers"])

        one_liner = _build_one_liner(pole_a, pole_b, trigger, compact=compact)

        emotion = rng.choice(
            DIMENSION_EMOTION_MAP.get(dim["name"], _FALLBACK_EMOTIONS)
        )
        pattern = rng.choice(
            DIMENSION_PATTERN_MAP.get(dim["name"], _FALLBACK_PATTERNS)
        )

        results.append(PolarityCollision(
            dimension_name=dim["name"],
            dimension_name_en=dim.get("name_en", dim["name"]),
            pole_a=pole_a,
            pole_b=pole_b,
            trigger=trigger,
            one_liner=one_liner,
            confidence=dim.get("confidence", 3),
            suggested_emotion=emotion,
            pattern_hint=pattern,
        ))

    return results


def collide_batch(
    count: int = 5,
    rng: random.Random | None = None,
    spread: bool = True,
) -> list[PolarityCollision]:
    """Generate a diverse batch of collisions, one per dimension when possible.

    Args:
        count: Target number of collisions.
        rng: Random instance for reproducibility.
        spread: If True (default), try to use a different dimension for each
                collision to maximize diversity.

    Returns:
        List of PolarityCollision results.
    """
    rng = rng or random.Random()
    dims = load_dimensions()
    results: list[PolarityCollision] = []

    if spread and count <= len(dims):
        # One collision per unique dimension
        shuffled = list(dims)
        rng.shuffle(shuffled)
        for dim in shuffled[:count]:
            c = collide(dimension_name=dim["name"], count=1, rng=rng)
            results.extend(c)
    else:
        results = collide(count=count, rng=rng, spread=False)  # type: ignore[call-arg]

    return results


def get_random_dimension(rng: random.Random | None = None) -> dict | None:
    """Pick a random dimension, weighted by confidence score."""
    rng = rng or random.Random()
    dims = load_dimensions()
    if not dims:
        return None

    # Weight by confidence
    weights = [d.get("confidence", 3) for d in dims]
    return rng.choices(dims, weights=weights, k=1)[0]
