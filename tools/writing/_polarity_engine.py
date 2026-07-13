"""Polarity collision engine — agent-driven story hook generation.

Sources:
- McKee "Story" — Story Climax as collision of opposing forces
- Egri "The Art of Dramatic Writing" — Dialectical conflict (thesis × antithesis)
- Truby "The Anatomy of Story" — Story Need as gap between poles

Architecture (v3 — Agent-Driven):
  polarity_dims.yaml defines ABSTRACT AXES (no concrete values).
  build_collision_prompt() assembles a creative brief from axis definitions.
  The agent (Claude Code) generates specific pole_a, pole_b, trigger, one_liner.
  complete_collision() packages agent output back into a PolarityCollision.

Zero external dependencies. Add new dimensions to the YAML; no code changes needed.
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
    one_liner: str            # The generated story hook (agent-authored)
    confidence: int           # 1-5, from the source dimension
    suggested_emotion: str    # Emotion this collision tends to produce
    pattern_hint: str         # Story pattern that fits this collision type
    cross_axis: str | None = None  # Name of cross-axis dimension, if fused


# ---------------------------------------------------------------------------
# Dimension loading (auto-discovers all entries in YAML)
# ---------------------------------------------------------------------------

_DIMENSIONS_CACHE: list[dict] | None = None
_YAML_PATH = Path(__file__).parent / "polarity_dims.yaml"


def load_dimensions() -> list[dict]:
    """Load all polarity dimensions from the YAML file.

    Returns a list of dimension dicts, each containing abstract axis definitions:
      - name, name_en, axis_description, confidence
      - pole_a_direction, pole_b_direction (descriptive, not concrete values)
      - collision_mechanism
      - cross_axis_hooks (list of partner dimensions with fusion descriptions)
      - emotions, patterns (lists for the agent to choose from)

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
# Fallback defaults (used when a dimension lacks its own emotions/patterns)
# ---------------------------------------------------------------------------

_FALLBACK_EMOTIONS = ["心酸", "温暖", "惊讶", "好笑"]
_FALLBACK_PATTERNS = ["日常英雄", "亲情反转", "瞬间决定"]


def _get_emotions(dim: dict) -> list[str]:
    return dim.get("emotions") or _FALLBACK_EMOTIONS


def _get_patterns(dim: dict) -> list[str]:
    return dim.get("patterns") or _FALLBACK_PATTERNS


# ---------------------------------------------------------------------------
# Prompt building — assembles creative briefs for the agent
# ---------------------------------------------------------------------------


def build_collision_prompt(
    dimension_name: str,
    cross_dim_name: str | None = None,
    rng: random.Random | None = None,
) -> dict:
    """Build a structured creative prompt for one polarity collision.

    Args:
        dimension_name: The primary axis to collide on.
        cross_dim_name: Optional secondary axis for cross-axis fusion.
        rng: Random instance for reproducibility (used for emotion/pattern selection).

    Returns:
        A dict with:
          - dimension: str (primary axis name)
          - cross_axis: str | None
          - emotion: str (suggested emotion, picked from the dimension's pool)
          - pattern: str (suggested pattern, picked from the dimension's pool)
          - confidence: int
          - prompt_text: str (the complete creative brief for the agent)
    """
    rng = rng or random.Random()
    dims = load_dimensions()

    # Find primary dimension
    primary = _find_dim(dims, dimension_name)
    if primary is None:
        raise ValueError(f"Unknown dimension: {dimension_name}")

    # Find cross-axis dimension if specified
    cross = None
    cross_fusion = None
    if cross_dim_name:
        cross = _find_dim(dims, cross_dim_name)
        if cross is None:
            raise ValueError(f"Unknown cross-axis dimension: {cross_dim_name}")
        # Find the fusion description from either primary or cross hooks
        cross_fusion = _find_fusion(primary, cross_dim_name) or _find_fusion(cross, dimension_name)

    # Pick emotion and pattern from the primary dimension's pools
    emotion = rng.choice(_get_emotions(primary))
    pattern = rng.choice(_get_patterns(primary))

    # Build the prompt
    prompt = _assemble_prompt(primary, cross, cross_fusion, emotion, pattern)

    return {
        "dimension": dimension_name,
        "cross_axis": cross_dim_name,
        "emotion": emotion,
        "pattern": pattern,
        "confidence": primary.get("confidence", 3),
        "prompt_text": prompt,
    }


def build_batch_prompts(
    count: int = 5,
    cross_ratio: float = 0.3,
    spread: bool = True,
    rng: random.Random | None = None,
) -> list[dict]:
    """Build a batch of collision prompts with controlled diversity.

    Args:
        count: Number of prompts to generate.
        cross_ratio: Fraction of prompts that use cross-axis fusion (0.0–1.0).
        spread: If True, try to use different dimensions for each prompt.
        rng: Random instance for reproducibility.

    Returns:
        List of prompt dicts (see build_collision_prompt return format).
    """
    rng = rng or random.Random()
    dims = load_dimensions()

    prompts: list[dict] = []
    cross_count = round(count * cross_ratio)
    single_count = count - cross_count

    # Build a pool of dimensions, cycling if count > len(dims)
    dim_pool = list(dims)
    if spread:
        rng.shuffle(dim_pool)
    # Repeat pool to cover the count
    while len(dim_pool) < single_count:
        extra = list(dims)
        rng.shuffle(extra)
        dim_pool.extend(extra)

    # Single-axis prompts
    for i in range(single_count):
        dim = dim_pool[i]
        prompts.append(build_collision_prompt(dim["name"], rng=rng))

    # Cross-axis prompts
    for i in range(cross_count):
        # Pick a primary dimension that has cross_axis_hooks
        dims_with_hooks = [d for d in dims if d.get("cross_axis_hooks")]
        if not dims_with_hooks:
            break
        primary = rng.choice(dims_with_hooks)
        # Pick a partner from its hooks
        hook = rng.choice(primary["cross_axis_hooks"])
        partner_name = hook["partner"]
        # Verify partner exists
        if _find_dim(dims, partner_name):
            prompts.append(build_collision_prompt(
                primary["name"], cross_dim_name=partner_name, rng=rng
            ))
        else:
            # Partner not found, fall back to single-axis
            prompts.append(build_collision_prompt(primary["name"], rng=rng))

    # Trim to exact count
    return prompts[:count]


# ---------------------------------------------------------------------------
# Completion — packages agent output back into collision objects
# ---------------------------------------------------------------------------


def complete_collision(
    pole_a: str,
    pole_b: str,
    trigger: str,
    one_liner: str,
    dimension_name: str,
    cross_dim_name: str | None = None,
    emotion: str | None = None,
    pattern: str | None = None,
    rng: random.Random | None = None,
) -> PolarityCollision:
    """Package agent-generated values into a PolarityCollision.

    Args:
        pole_a: Agent-generated low-end value.
        pole_b: Agent-generated high-end value.
        trigger: Agent-generated collision trigger.
        one_liner: Agent-generated one-sentence story hook.
        dimension_name: The primary axis used.
        cross_dim_name: Optional cross-axis dimension.
        emotion: Optional emotion override. If None, picked from dimension's pool.
        pattern: Optional pattern override. If None, picked from dimension's pool.
        rng: Random instance for reproducibility.

    Returns:
        A complete PolarityCollision ready for seed building.
    """
    rng = rng or random.Random()
    dims = load_dimensions()
    primary = _find_dim(dims, dimension_name)

    if primary is None:
        raise ValueError(f"Unknown dimension: {dimension_name}")

    if emotion is None:
        emotion = rng.choice(_get_emotions(primary))
    if pattern is None:
        pattern = rng.choice(_get_patterns(primary))

    return PolarityCollision(
        dimension_name=dimension_name,
        dimension_name_en=primary.get("name_en", dimension_name),
        pole_a=pole_a,
        pole_b=pole_b,
        trigger=trigger,
        one_liner=one_liner,
        confidence=primary.get("confidence", 3),
        suggested_emotion=emotion,
        pattern_hint=pattern,
        cross_axis=cross_dim_name,
    )


def complete_collisions(
    agent_outputs: list[dict],
    rng: random.Random | None = None,
) -> list[PolarityCollision]:
    """Batch-complete collisions from a list of agent outputs.

    Args:
        agent_outputs: List of dicts, each with:
            - pole_a, pole_b, trigger, one_liner (required)
            - dimension (required)
            - cross_axis, emotion, pattern (optional)
        rng: Random instance for reproducibility.

    Returns:
        List of PolarityCollision objects.
    """
    rng = rng or random.Random()
    results: list[PolarityCollision] = []

    for ao in agent_outputs:
        results.append(complete_collision(
            pole_a=ao["pole_a"],
            pole_b=ao["pole_b"],
            trigger=ao["trigger"],
            one_liner=ao["one_liner"],
            dimension_name=ao["dimension"],
            cross_dim_name=ao.get("cross_axis"),
            emotion=ao.get("emotion"),
            pattern=ao.get("pattern"),
            rng=rng,
        ))

    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_dim(dims: list[dict], name: str) -> dict | None:
    """Find a dimension by name."""
    for d in dims:
        if d["name"] == name:
            return d
    return None


def _find_fusion(dim: dict, partner_name: str) -> str | None:
    """Find the fusion description for a cross-axis partner."""
    for hook in dim.get("cross_axis_hooks") or []:
        if hook.get("partner") == partner_name:
            return hook.get("fusion")
    return None


def _assemble_prompt(
    primary: dict,
    cross: dict | None,
    fusion: str | None,
    emotion: str,
    pattern: str,
) -> str:
    """Assemble the creative prompt text for the agent."""

    lines = [
        "你是一个短篇故事创意生成器。请根据以下极性碰撞维度，即兴生成具体的碰撞元素。",
        "",
        "## 核心规则",
        "",
        "1. **pole_a 和 pole_b 必须是同一光谱的两端**——比如都是消费行为、都是社交表现、都是权力地位。不要把不同种类的东西放在对立两端。",
        "2. **值必须极其具体**——用真实的场景、物、行为、数字、原话，不要用形容词堆砌。'泡面吃到第三天' 优于 '生活很拮据'。",
        "3. **触发器是碰撞发生的具体瞬间**——谁在什么时间、什么地点、做了什么或看到了什么，导致两极被迫面对面。必须是令人心头一紧的细节。",
        "4. **one_liner 是完整的一句话故事**——用 pole_a + trigger + pole_b 自然地讲出一个不超过100字的画面。像电影开场的第一个镜头。",
        "",
        "---",
        "",
        f"## 主轴：{primary['name']}",
        "",
        f"**轴线描述**：{primary['axis_description'].strip()}",
        "",
        f"**pole_a 方向（低端）**：{primary['pole_a_direction'].strip()}",
        "",
        f"**pole_b 方向（高端）**：{primary['pole_b_direction'].strip()}",
        "",
        f"**碰撞机制**：{primary['collision_mechanism'].strip()}",
        "",
    ]

    if cross and fusion:
        lines.extend([
            "---",
            "",
            f"## 跨轴融合：{cross['name']}",
            "",
            f"**融合说明**：{fusion.strip()}",
            "",
            f"**{cross['name']}的轴线**：{cross['axis_description'].strip()}",
            "",
            f"**{cross['name']}的 pole_a 方向**：{cross['pole_a_direction'].strip()}",
            "",
            f"**{cross['name']}的 pole_b 方向**：{cross['pole_b_direction'].strip()}",
            "",
            "**跨轴要求**：pole_a 和 pole_b 不仅要体现主轴的两端，还要自然地嵌入 {cross['name']}的元素。碰撞点要同时激活两个维度。",
            "",
        ])

    lines.extend([
        "---",
        "",
        f"**建议情绪**：{emotion}",
        f"**建议模式**：{pattern}",
        "",
        "## 输出格式",
        "",
        "请严格按以下JSON格式输出（不要加```json标记，直接输出纯JSON）：",
        "",
        "{",
        f'  "pole_a": "具体、生动的低端值（一句话，像电影场景中的一个细节）",',
        f'  "pole_b": "具体、生动的高端值（一句话，与pole_a属于同一种东西的另一端）",',
        f'  "trigger": "碰撞发生的具体瞬间——谁在什么时间地点，做了什么/看到了什么",',
        f'  "one_liner": "完整的一句话故事，自然地连接pole_a、trigger和pole_b，不超过100字"',
        "}",
        "",
        "只输出JSON，不要任何解释。",
    ])

    return "\n".join(lines)
