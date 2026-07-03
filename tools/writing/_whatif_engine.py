"""What-if transformation engine — 5 rules to twist any concept into fresh story ideas.

Takes a source concept (one sentence) and applies transformation rules
to generate multiple story variations.
"""

from __future__ import annotations

from dataclasses import dataclass

from ._emotion_matrix import DAILY_OBSERVATIONS


@dataclass
class WhatIfResult:
    """One transformed concept from a what-if rule."""

    rule_name: str
    rule_name_en: str
    transformed_concept: str
    hook_suggestion: str
    pattern_suggestion: str
    emotional_shift: str  # e.g. "anger -> empathy"


WHATIF_RULES: list[dict] = [
    {
        "name": "视角翻转",
        "name_en": "Perspective Flip",
        "description": "从另一个角色的视角重新讲述同一个故事",
        "template": "从{角色}的视角来看：{原始概念}。但其实{角色}也有自己的故事——{翻转点}",
        "hook_hint": "你以为{表面事实}，但{另一角色}看到的是{隐藏事实}",
        "pattern_bias": ["亲情反转", "身份反转", "隐藏真相"],
        "emotional_shift": "旁观 → 共情",
    },
    {
        "name": "类型转换",
        "name_en": "Genre Shift",
        "description": "把严肃变搞笑，或把搞笑变感人",
        "template": "{原始概念}——但如果这是一个{类型}故事呢？{转换点}",
        "hook_hint": "一切看起来很正常，直到{荒谬/感人的转折点出现}",
        "pattern_bias": ["误会连环", "奇葩逻辑", "日常英雄"],
        "emotional_shift": "平淡 → 爆发",
    },
    {
        "name": "时间跳跃",
        "name_en": "Time Jump",
        "description": "展示这件事5年前或5年后的样子",
        "template": "{原始概念}——5年{前/后}，{时间变化后的场景}",
        "hook_hint": "那时候{角色}还不知道，这件事会改变一切",
        "pattern_bias": ["时光对比", "如果当初", "日常英雄"],
        "emotional_shift": "现在 → 感慨",
    },
    {
        "name": "代价升级",
        "name_en": "Stakes Escalation",
        "description": "事情的后果远比表面看起来的严重",
        "template": "{原始概念}——但这件事引发的连锁反应是{严重后果}",
        "hook_hint": "看起来只是一件小事，但{连锁反应的开始}",
        "pattern_bias": ["瞬间决定", "隐藏真相", "误会连环"],
        "emotional_shift": "轻松 → 紧张",
    },
    {
        "name": "反转倒置",
        "name_en": "Inversion",
        "description": "把预期的结果完全反过来",
        "template": "{原始概念}——但如果结果完全相反呢？{反转结果}",
        "hook_hint": "所有人都以为会{预期结果}，结果{意外结果}",
        "pattern_bias": ["身份反转", "社死瞬间", "陌生人温暖"],
        "emotional_shift": "预期 → 意外",
    },
]


def transform(
    source_concept: str,
    rules: list[str] | None = None,
    rng=None,
) -> list[WhatIfResult]:
    """Apply what-if rules to a source concept.

    Args:
        source_concept: A one-sentence story idea or observation.
        rules: Optional list of rule names to apply. None = all rules.
        rng: Random instance for reproducibility.

    Returns:
        List of WhatIfResult, one per applied rule.
    """
    import random
    rng = rng or random.Random()

    if rules:
        active = [r for r in WHATIF_RULES if r["name"] in rules]
    else:
        active = list(WHATIF_RULES)

    results: list[WhatIfResult] = []

    for rule in active:
        transformed = _apply_rule(source_concept, rule, rng)
        results.append(transformed)

    return results


def _apply_rule(source: str, rule: dict, rng) -> WhatIfResult:
    """Apply a single rule to generate a what-if variation."""

    name = rule["name"]

    if name == "视角翻转":
        perspectives = [
            ("旁观者", "看到的全貌和当事人完全不同"),
            ("对手方", "也有自己的委屈和无奈"),
            ("未来的自己", "回头看这件事，才理解了当时不懂的事"),
            ("另一个人", "默默在旁边承受了你不知道的部分"),
        ]
        p = rng.choice(perspectives)
        concept = f"{source}——但从{p[0]}的角度看，{p[1]}"
        hook = f"你以为你了解真相，但{p[0]}看到的完全不同"
        pattern = rng.choice(rule["pattern_bias"])

    elif name == "类型转换":
        directions = [
            ("喜剧", "同样的场景，换一个角度就成了段子"),
            ("催泪", "看似搞笑的事背后有一个让人心酸的原因"),
            ("悬疑", "一个普通场景里藏着一个不为人知的秘密"),
            ("治愈", "用最温柔的方式重新讲述这个日常"),
        ]
        d = rng.choice(directions)
        concept = f"{source}——如果这是个{d[0]}故事：{d[1]}"
        hook = f"表面上{source[:20]}...但真相是{d[0]}级别的"
        pattern = rng.choice(rule["pattern_bias"])

    elif name == "时间跳跃":
        directions = [
            ("前", "这件事发生前的某一天，一切都还不一样"),
            ("后", "这件事之后很久，某个人还记得"),
        ]
        d = rng.choice(directions)
        years = rng.choice([1, 3, 5, 10])
        concept = f"{source}——{years}年{d[0]}，这件事已经被忘记了——直到某天"
        hook = f"{years}年后，{source[:15]}...已经变成了另一个人"
        pattern = rng.choice(rule["pattern_bias"])

    elif name == "代价升级":
        escalations = [
            "这个小小的事件改变了一个人的决定，而那个决定改变了一切",
            "看起来微不足道，但这件事被另一个人看到了，引发了蝴蝶效应",
            "没有人意识到这个动作的重量，直到很久以后才明白",
        ]
        e = rng.choice(escalations)
        concept = f"{source}——但后果远超想象：{e}"
        hook = f"一件小事。但{source[:15]}...最后谁也没想到"
        pattern = rng.choice(rule["pattern_bias"])

    elif name == "反转倒置":
        inversions = [
            "结果完全相反——你以为的输家才是真正的赢家",
            "所有人都在笑，但真正该哭的是笑的人自己",
            "反过来了：被同情的人其实比同情他的人更幸福",
        ]
        inv = rng.choice(inversions)
        concept = f"{source}——反转：{inv}"
        hook = f"所有人以为{source[:15]}...但事实恰好相反"
        pattern = rng.choice(rule["pattern_bias"])

    else:
        concept = source
        hook = source
        pattern = "日常英雄"

    return WhatIfResult(
        rule_name=rule["name"],
        rule_name_en=rule["name_en"],
        transformed_concept=concept,
        hook_suggestion=hook,
        pattern_suggestion=pattern,
        emotional_shift=rule["emotional_shift"],
    )


def get_daily_observation(rng=None) -> str:
    """Pick a random daily life observation for daily_catch mode."""
    import random
    rng = rng or random.Random()
    return rng.choice(DAILY_OBSERVATIONS)
