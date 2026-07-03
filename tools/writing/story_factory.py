"""Story Factory — automated comic story ideation tool for short-form Douyin videos.

Generates structured story seeds with 5-beat narratives, character archetypes,
visual suggestions, and style keywords ready for Seedream image generation.

Zero external dependencies — pure local computation.
"""

from __future__ import annotations

import hashlib
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

from ._emotion_matrix import (
    EMOTIONS,
    SCENES,
    get_random_seed,
)
from ._patterns import (
    EMOTION_PATTERN_MAP,
    PATTERNS,
    PATTERN_BY_NAME,
    StoryPattern,
)
from ._whatif_engine import get_daily_observation, transform
from ._text_analyzer import TextAnalysisResult, analyze_text
from ._video_to_concept import extract_concept_from_video


@dataclass
class _LightSeed:
    """Lightweight seed stand-in for what-if generated seeds."""
    title: str = ""
    logline: str = ""
    hook: str = ""
    pattern_name: str = ""
    character_roles: list[str] = field(default_factory=list)
    twist_hint: str = ""
    visual_keywords: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Character archetype pool
# ---------------------------------------------------------------------------

CHARACTER_ARCHETYPES: list[dict[str, str]] = [
    {"role": "妈妈", "description": "中年亚洲女性，温柔但倔强，用看似笨拙的方式表达关心", "emotional_state": "操心但故作轻松", "visual_notes": "50岁左右亚洲女性，齐肩短发，微胖，常穿碎花围裙或米色开衫，笑起来眼睛弯弯"},
    {"role": "爸爸", "description": "中年男性，沉默寡言，用行动代替语言", "emotional_state": "内心柔软但表面严肃", "visual_notes": "55岁左右亚洲男性，短发带灰，身材中等，常穿深色夹克或格子衬衫，额头有皱纹"},
    {"role": "打工人", "description": "20-30岁上班族，疲惫但还在撑着", "emotional_state": "表面平静内心崩溃中", "visual_notes": "25-30岁亚洲男性或女性，黑眼圈，穿休闲西装或卫衣，背包永远在肩膀上"},
    {"role": "陌生人", "description": "不知名的路人，可能成为故事的关键人物", "emotional_state": "平静但有自己的故事", "visual_notes": "任何年龄，穿着普通但有一个细节特征（如围巾、帽子、背包挂件）"},
    {"role": "孩子", "description": "5-10岁的小孩，纯真但偶尔说出让人意外的话", "emotional_state": "天真无邪", "visual_notes": "7岁左右亚洲小孩，短发或扎辫子，校服或T恤，表情丰富"},
    {"role": "老板", "description": "严厉但有温度的上司", "emotional_state": "表面严肃内心关心", "visual_notes": "40-50岁亚洲男性，西装革履，戴眼镜，严肃表情但偶尔露出微笑"},
    {"role": "老人", "description": "70岁以上，经历过很多但还在认真活着", "emotional_state": "平静中带感慨", "visual_notes": "75岁左右亚洲人，满头白发，微驼，穿深色棉衣或中山装，手上纹路深"},
    {"role": "年轻人", "description": "大学生或刚毕业的年轻人，充满希望又有点迷茫", "emotional_state": "热情但焦虑", "visual_notes": "22岁左右亚洲人，穿卫衣牛仔裤，背双肩包，眼睛明亮"},
    {"role": "外卖小哥", "description": "匆忙但善良的外卖骑手", "emotional_state": "赶时间但内心温和", "visual_notes": "25-35岁亚洲男性，穿着黄色或蓝色骑手服，戴头盔，皮肤晒黑"},
    {"role": "服务员", "description": "餐厅或便利店的员工，默默观察着每个人", "emotional_state": "客气但心里有自己的判断", "visual_notes": "20-30岁，穿制服，围裙，面带职业微笑，但眼睛很亮"},
    {"role": "闺蜜/兄弟", "description": "主角最好的朋友，嘴上毒但心里暖", "emotional_state": "吐槽但关键时刻靠得住", "visual_notes": "和主角年龄相仿，穿着随意，表情丰富"},
    {"role": "奶奶/外婆", "description": "高龄但精神矍铄的老太太", "emotional_state": "慈祥但倔强", "visual_notes": "75岁以上亚洲女性，银发盘髻或烫小卷，穿深色棉袄，手布满皱纹但动作利索"},
]

# ---------------------------------------------------------------------------
# Visual style presets (Seedream prompt keywords)
# ---------------------------------------------------------------------------

STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "warm_illustration": {
        "color_palette": "暖色调，米色、浅橙、深棕为主色",
        "mood": "温馨、治愈",
        "lighting": "柔和自然光，午后暖阳，或者室内暖黄灯光",
        "seedream_keywords": [
            "温暖插画风格", "柔和色调", "手绘质感",
            "日式生活插画", "温馨氛围", "柔和线条",
        ],
    },
    "cinematic_drama": {
        "color_palette": "对比强烈，深蓝、暗红、灰白",
        "mood": "紧张、悬念、深沉",
        "lighting": "戏剧性光影，明暗对比，侧光或逆光",
        "seedream_keywords": [
            "电影感插画", "高对比度", "戏剧性光影",
            "暗调画面", "氛围感", "细节丰富",
        ],
    },
    "clean_comic": {
        "color_palette": "明亮干净的色彩，黑白为主加点缀色",
        "mood": "轻松、幽默、现代",
        "lighting": "均匀明亮，漫画式的平面光感",
        "seedream_keywords": [
            "现代漫画风格", "干净的线条", "明亮的色彩",
            "简笔画", "幽默感", "表情夸张",
        ],
    },
    "watercolor_nostalgia": {
        "color_palette": "淡雅水彩色，像褪了色的老照片",
        "mood": "怀旧、感慨、时光",
        "lighting": "梦幻般的柔光，像透过纱帘的阳光",
        "seedream_keywords": [
            "水彩插画", "怀旧色调", "梦幻质感",
            "柔和笔触", "时光感", "温暖回忆",
        ],
    },
    "ink_dramatic": {
        "color_palette": "以黑白灰为主，少量红色点缀",
        "mood": "强烈、反转、冲击",
        "lighting": "强烈的明暗对比，像木版画",
        "seedream_keywords": [
            "黑白水墨风格", "强烈对比", "极简色彩",
            "版画质感", "视觉冲击", "东方美学",
        ],
    },
}

# Emotion → style mapping
EMOTION_STYLE_MAP: dict[str, str] = {
    "惊讶": "cinematic_drama",
    "感动": "watercolor_nostalgia",
    "好笑": "clean_comic",
    "紧张": "cinematic_drama",
    "温暖": "warm_illustration",
    "心酸": "watercolor_nostalgia",
    "愤怒": "ink_dramatic",
    "治愈": "warm_illustration",
}


class StoryFactory(BaseTool):
    """Generate structured comic story ideas for 60-second Douyin videos."""

    name = "story_factory"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "story_generation"
    provider = "openmontage"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies: list[str] = []
    install_instructions = "No setup required — this tool runs locally with zero dependencies."

    capabilities = ["story_ideation", "comic_planning", "short_form_narrative"]

    best_for = [
        "Generating 60-second Douyin comic story ideas",
        "Batch story ideation for content calendars",
        "Writer's block — constrained creative exploration",
        "Mood-to-story translation",
        "Inspiration-to-story from text jokes or anecdotes",
        "Video-to-story concept extraction and adaptation",
    ]
    not_good_for = [
        "Feature-length scripts",
        "Novel plotting",
        "Non-fiction documentary scripting",
    ]

    agent_skills = ["storytelling"]

    input_schema = {
        "type": "object",
        "required": ["mode"],
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["emotion_matrix", "what_if", "daily_catch", "random", "batch", "from_text", "from_video"],
                "description": "Generation mode. from_text: analyze text → story seeds. from_video: analyze video → story seeds.",
            },
            "emotion": {
                "type": "string",
                "description": f"Target emotion. Options: {', '.join(EMOTIONS)}",
            },
            "scene": {
                "type": "string",
                "description": f"Scene/location. Options: {', '.join(SCENES)}",
            },
            "source_concept": {
                "type": "string",
                "description": "Source idea for what_if transformations (one sentence)",
            },
            "text_content": {
                "type": "string",
                "description": "Raw text inspiration for from_text mode (joke, anecdote, story snippet of any length)",
            },
            "video_source": {
                "type": "string",
                "description": "Video URL or local file path for from_video mode",
            },
            "pattern": {
                "type": "string",
                "description": f"Force a specific story pattern. Options: {', '.join(p.name for p in PATTERNS)}",
            },
            "count": {
                "type": "integer",
                "minimum": 1,
                "maximum": 20,
                "default": 1,
                "description": "Number of seeds to generate",
            },
            "seed": {
                "type": "integer",
                "description": "Random seed for reproducible output",
            },
            "character_count": {
                "type": "integer",
                "minimum": 1,
                "maximum": 4,
                "default": 2,
                "description": "Number of character archetypes per story",
            },
            "target_platform": {
                "type": "string",
                "default": "douyin",
                "enum": ["douyin", "tiktok", "instagram", "youtube_shorts", "generic"],
            },
            "target_duration_seconds": {
                "type": "number",
                "default": 60,
                "minimum": 15,
                "maximum": 90,
            },
        },
    }

    output_schema = {
        "type": "object",
        "properties": {
            "seeds": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Generated story seed objects",
            },
            "generation_mode": {"type": "string"},
            "total": {"type": "integer"},
        },
    }

    # ── Status (always available — no dependencies) ──────────────────────
    def get_status(self):
        from tools.base_tool import ToolStatus
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:  # noqa: ARG002
        return 0.0

    # ── Execute ─────────────────────────────────────────────────────────
    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()

        mode = inputs["mode"]
        count = min(max(inputs.get("count", 1), 1), 20)
        seed_val = inputs.get("seed")
        rng = random.Random(seed_val)
        target_duration = inputs.get("target_duration_seconds", 60)
        char_count = inputs.get("character_count", 2)

        try:
            if mode == "emotion_matrix":
                seeds = self._gen_emotion_matrix(inputs, count, rng, target_duration, char_count)
            elif mode == "what_if":
                seeds = self._gen_whatif(inputs, count, rng, target_duration, char_count)
            elif mode == "daily_catch":
                seeds = self._gen_daily_catch(inputs, count, rng, target_duration, char_count)
            elif mode == "random":
                seeds = self._gen_random(inputs, count, rng, target_duration, char_count)
            elif mode == "batch":
                seeds = self._gen_batch(inputs, count, rng, target_duration, char_count)
            elif mode == "from_text":
                seeds = self._gen_from_text(inputs, count, rng, target_duration, char_count)
            elif mode == "from_video":
                seeds = self._gen_from_video(inputs, count, rng, target_duration, char_count)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown mode: {mode}. "
                          f"Valid modes: emotion_matrix, what_if, daily_catch, random, batch, from_text, from_video",
                )
        except Exception as exc:
            return ToolResult(success=False, error=f"Story generation failed: {exc}")

        result = ToolResult(
            success=True,
            data={
                "seeds": seeds,
                "generation_mode": mode,
                "total": len(seeds),
            },
            duration_seconds=round(time.time() - start, 3),
            cost_usd=0.0,
            seed=seed_val,
        )
        return result

    # ── Mode dispatchers ───────────────────────────────────────────────
    def _gen_emotion_matrix(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        emotion = inputs.get("emotion")
        scene = inputs.get("scene")
        pattern_name = inputs.get("pattern")
        seeds = []
        for _ in range(count):
            matrix_seed = get_random_seed(emotion, scene, rng)
            if not matrix_seed:
                continue
            seeds.append(self._build_seed(
                matrix_seed=matrix_seed,
                pattern_name=pattern_name,
                emotion=emotion or rng.choice(EMOTIONS),
                duration=duration,
                char_count=char_count,
                rng=rng,
            ))
        return seeds

    def _gen_whatif(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        source = inputs.get("source_concept")
        if not source:
            # Fall back to a daily observation as source
            source = get_daily_observation(rng)
        results = transform(source, rules=None, rng=rng)
        pattern_name = inputs.get("pattern")
        seeds = []
        for r in results[:count]:
            seeds.append(self._build_seed_from_whatif(
                whatif=r,
                source_concept=source,
                pattern_name=pattern_name,
                duration=duration,
                char_count=char_count,
                rng=rng,
            ))
        return seeds

    def _gen_daily_catch(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        pattern_name = inputs.get("pattern")
        seeds = []
        used: set[str] = set()
        for _ in range(count):
            obs = get_daily_observation(rng)
            # Avoid duplicates
            while obs in used and len(used) < len(getattr(self, '_daily_pool', [])):
                obs = get_daily_observation(rng)
            used.add(obs)
            # Light what-if transform on the observation
            whatif_results = transform(obs, rules=None, rng=rng)
            wr = rng.choice(whatif_results)
            seeds.append(self._build_seed_from_whatif(
                whatif=wr,
                source_concept=obs,
                pattern_name=pattern_name,
                duration=duration,
                char_count=char_count,
                rng=rng,
            ))
        return seeds

    def _gen_random(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        pattern_name = inputs.get("pattern")
        seeds = []
        for _ in range(count):
            # Random emotion + scene from matrix
            emotion = rng.choice(EMOTIONS)
            scene = rng.choice(SCENES)
            matrix_seed = get_random_seed(emotion, scene, rng)
            if matrix_seed:
                seeds.append(self._build_seed(
                    matrix_seed=matrix_seed,
                    pattern_name=pattern_name,
                    emotion=emotion,
                    duration=duration,
                    char_count=char_count,
                    rng=rng,
                ))
        return seeds

    def _gen_batch(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        """Mix all modes to produce diverse batch output."""
        all_seeds: list[dict] = []
        modes = ["emotion_matrix", "daily_catch", "random"]
        per_mode = max(1, count // len(modes))
        remainder = count - per_mode * len(modes)

        for i, mode in enumerate(modes):
            c = per_mode + (1 if i < remainder else 0)
            batch_inputs = dict(inputs)
            batch_inputs["mode"] = mode
            if mode == "emotion_matrix":
                all_seeds.extend(self._gen_emotion_matrix(batch_inputs, c, rng, duration, char_count))
            elif mode == "daily_catch":
                all_seeds.extend(self._gen_daily_catch(batch_inputs, c, rng, duration, char_count))
            elif mode == "random":
                all_seeds.extend(self._gen_random(batch_inputs, c, rng, duration, char_count))

        return all_seeds[:count]

    # ── from_text / from_video modes ────────────────────────────────────

    def _gen_from_text(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        """Generate story seeds from raw text inspiration (joke, anecdote)."""
        text_content = inputs.get("text_content", "")
        if not text_content:
            return []

        analysis = analyze_text(text_content)
        return self._build_seeds_from_analysis(analysis, inputs, count, rng, duration, char_count)

    def _gen_from_video(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        """Generate story seeds from a video URL or local file."""
        video_source = inputs.get("video_source", "")
        if not video_source:
            return []

        output_dir = inputs.get("output_dir")
        analysis = extract_concept_from_video(video_source, output_dir=output_dir)

        if not analysis.core_concept:
            return []

        return self._build_seeds_from_analysis(analysis, inputs, count, rng, duration, char_count)

    def _build_seeds_from_analysis(
        self,
        analysis: TextAnalysisResult,
        inputs: dict,
        count: int,
        rng: random.Random,
        duration: float,
        char_count: int,
    ) -> list[dict]:
        """Shared pipeline: analysis → what-if transform → story seeds."""
        source_concept = analysis.core_concept
        pattern_name = inputs.get("pattern")

        whatif_results = transform(source_concept, rules=None, rng=rng)

        seeds = []
        for r in whatif_results[:count]:
            seeds.append(self._build_seed_from_whatif(
                whatif=r,
                source_concept=source_concept,
                pattern_name=pattern_name,
                duration=duration,
                char_count=char_count,
                rng=rng,
                emotion_override=analysis.emotion_guess,
                character_hints=analysis.character_hints,
                origin_mode="from_text" if inputs.get("mode") == "from_text" else "from_video",
            ))
        return seeds

    # ── Seed builders ──────────────────────────────────────────────────
    def _build_seed(
        self,
        matrix_seed,
        pattern_name: str | None,
        emotion: str,
        duration: float,
        char_count: int,
        rng: random.Random,
    ) -> dict:
        """Build a full story seed from a matrix seed + pattern."""
        # Resolve pattern
        if pattern_name and pattern_name in PATTERN_BY_NAME:
            pattern = PATTERN_BY_NAME[pattern_name]
        elif matrix_seed.pattern_name in PATTERN_BY_NAME:
            pattern = PATTERN_BY_NAME[matrix_seed.pattern_name]
        else:
            # Pick a pattern fitting the emotion
            candidates = EMOTION_PATTERN_MAP.get(emotion, ["日常英雄"])
            pattern = PATTERN_BY_NAME.get(
                rng.choice(candidates), PATTERNS[0]
            )

        style_key = EMOTION_STYLE_MAP.get(emotion, "warm_illustration")
        style = STYLE_PRESETS[style_key]

        beats = self._build_beats(pattern, duration, matrix_seed)
        characters = self._select_characters(
            matrix_seed.character_roles, char_count, rng
        )

        seed_id = _make_seed_id(matrix_seed.title, pattern.name)

        return {
            "version": "1.0",
            "seed_id": seed_id,
            "title": matrix_seed.title,
            "hook": matrix_seed.hook,
            "logline": matrix_seed.logline,
            "pattern": pattern.name,
            "pattern_category": pattern.category,
            "douyin_tags": pattern.douyin_tags,
            "emotion_arc": {
                "starts": emotion,
                "peaks_at": _emotion_peak(emotion),
                "ends": _emotion_end(emotion),
            },
            "beats": beats,
            "twist": matrix_seed.twist_hint,
            "ending": _build_ending(pattern.category, emotion),
            "character_archetypes": characters,
            "suggested_style": style,
            "visual_keywords": matrix_seed.visual_keywords,
            "target_platform": "douyin",
            "target_duration_seconds": duration,
            "estimated_image_count": len(beats),
            "difficulty": pattern.difficulty,
            "generation_mode": "emotion_matrix",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _build_seed_from_whatif(
        self,
        whatif,
        source_concept: str,  # noqa: ARG002
        pattern_name: str | None,
        duration: float,
        char_count: int,
        rng: random.Random,
        emotion_override: str | None = None,
        character_hints: list[str] | None = None,
        origin_mode: str = "what_if",
    ) -> dict:
        """Build a full story seed from a what-if result."""
        if pattern_name and pattern_name in PATTERN_BY_NAME:
            pattern = PATTERN_BY_NAME[pattern_name]
        elif whatif.pattern_suggestion in PATTERN_BY_NAME:
            pattern = PATTERN_BY_NAME[whatif.pattern_suggestion]
        else:
            pattern = rng.choice(PATTERNS)

        emotion = emotion_override if emotion_override else rng.choice(EMOTIONS)
        style_key = EMOTION_STYLE_MAP.get(emotion, "warm_illustration")
        style = STYLE_PRESETS[style_key]

        # Build a lightweight matrix seed from what-if
        # Extract a concise version for title/logline, keep full concept for twist
        concise = _short_title(whatif.transformed_concept, max_len=20)
        matrix_seed = _LightSeed(
            title=concise,
            logline=f"{source_concept}——经过'{whatif.rule_name}'变换后：{concise}",
            hook=whatif.hook_suggestion,
            pattern_name=pattern.name,
            character_roles=[],
            twist_hint=f"{whatif.rule_name}：{whatif.transformed_concept}",
            visual_keywords=[],
        )

        beats = self._build_beats(pattern, duration, matrix_seed)
        char_roles = character_hints if character_hints else []
        characters = self._select_characters(char_roles, char_count, rng)

        seed_id = _make_seed_id(matrix_seed.title, pattern.name)

        return {
            "version": "1.0",
            "seed_id": seed_id,
            "title": matrix_seed.title,
            "hook": matrix_seed.hook,
            "logline": matrix_seed.logline,
            "pattern": pattern.name,
            "pattern_category": pattern.category,
            "douyin_tags": pattern.douyin_tags,
            "emotion_arc": {
                "starts": emotion,
                "peaks_at": _emotion_peak(emotion),
                "ends": _emotion_end(emotion),
            },
            "beats": beats,
            "twist": whatif.transformed_concept,
            "ending": _build_ending(pattern.category, emotion),
            "character_archetypes": characters,
            "suggested_style": style,
            "visual_keywords": matrix_seed.visual_keywords,
            "target_platform": "douyin",
            "target_duration_seconds": duration,
            "estimated_image_count": len(beats),
            "difficulty": pattern.difficulty,
            "generation_mode": f"{origin_mode} ({whatif.rule_name})",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _build_beats(self, pattern: StoryPattern, duration: float, matrix_seed) -> list[dict]:
        """Convert pattern beat templates to timed beats with visual suggestions."""
        beats = []
        for i, bt in enumerate(pattern.beats):
            start_s = round(bt.start_pct * duration, 1)
            end_s = round(bt.end_pct * duration, 1)
            beats.append({
                "beat_number": i + 1,
                "name": bt.name,
                "start_second": start_s,
                "end_second": end_s,
                "description": _beat_description(bt, matrix_seed, i),
                "visual_suggestion": _beat_visual(bt, matrix_seed, i),
                "text_overlay": _beat_text(bt, matrix_seed, i),
                "camera_hint": _beat_camera(bt, i),
            })
        return beats

    def _select_characters(
        self, role_hints: list[str], count: int, rng
    ) -> list[dict]:
        """Select character archetypes, preferring matching role hints."""
        selected: list[dict] = []
        used_roles: set[str] = set()

        # First, match hints
        for hint in role_hints[:count]:
            for arch in CHARACTER_ARCHETYPES:
                if arch["role"] not in used_roles and _role_match(hint, arch["role"]):
                    selected.append(arch)
                    used_roles.add(arch["role"])
                    break

        # Fill remaining slots
        while len(selected) < count:
            candidates = [a for a in CHARACTER_ARCHETYPES if a["role"] not in used_roles]
            if not candidates:
                break
            arch = rng.choice(candidates)
            selected.append(arch)
            used_roles.add(arch["role"])

        return selected


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _make_seed_id(title: str, pattern: str) -> str:
    raw = f"{title}:{pattern}:{uuid.uuid4().hex[:8]}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _role_match(hint: str, role: str) -> bool:
    """Loose matching between a role hint and a character archetype."""
    hint_chars = set(hint)
    role_chars = set(role)
    return len(hint_chars & role_chars) > 0


def _emotion_peak(emotion: str) -> str:
    peaks = {
        "惊讶": "震惊", "感动": "落泪", "好笑": "爆笑",
        "紧张": "紧绷", "温暖": "动容", "心酸": "沉默",
        "愤怒": "爆发", "治愈": "释然",
    }
    return peaks.get(emotion, emotion)


def _emotion_end(emotion: str) -> str:
    ends = {
        "惊讶": "理解", "感动": "温暖", "好笑": "会心一笑",
        "紧张": "放松", "温暖": "平静", "心酸": "释怀",
        "愤怒": "反思", "治愈": "力量",
    }
    return ends.get(emotion, emotion)


def _build_ending(category: str, emotion: str) -> str:
    endings = {
        ("comedy", "好笑"): "用一个苦笑或沉默的定格收场，不解释，让观众自己回味",
        ("comedy", "惊讶"): "画面定格在一个意外的表情上，让观众自己笑",
        ("emotional", "感动"): "用一个背影或侧脸收场，不说话——留白比煽情更有力量",
        ("emotional", "心酸"): "画面慢慢远去，用安静代替眼泪",
        ("emotional", "温暖"): "两个人各自离开，但观众知道他们心里有什么变了",
        ("suspense", "惊讶"): "回到平静表面，但观众已经知道了真相",
        ("suspense", "紧张"): "回到那个选择的瞬间，问观众：你会怎么做",
        ("slice_of_life", "治愈"): "同样的场景，但阳光不一样了——心情也变了",
    }
    return endings.get((category, emotion), "用一个安静的定格收场，让观众自己感受")


def _beat_description(bt, matrix_seed, index) -> str:
    templates = [
        f"开场画面：{matrix_seed.logline[:30]}...",
        f"推进场景：展示更多细节，让观众对'{matrix_seed.title}'产生好奇",
        f"冲突升级：围绕'{matrix_seed.title}'的核心矛盾展开",
        f"揭示真相：{matrix_seed.twist_hint[:40]}",
        f"情感收尾：用一个细节或动作定格，不说教",
    ]
    return templates[index] if index < len(templates) else bt.narrative_function


def _beat_visual(_bt, matrix_seed, index) -> str:  # noqa: ARG001
    kw = ", ".join(matrix_seed.visual_keywords) if matrix_seed.visual_keywords else "日常场景"
    visuals = [
        f"全景开场，展示场景环境。风格：{kw}。画面要有张力，第一帧就吸引眼球",
        f"中景，角色在场景中的日常行为。{kw}。光线柔和但有层次",
        f"特写或快速切换，展示冲突的细节。{kw}。画面节奏加快",
        f"关键画面揭示：{matrix_seed.twist_hint[:30]}。{kw}。这一帧要让观众想倒回去看",
        f"全景或特写收尾，{kw}。留白，用画面情绪代替文字",
    ]
    return visuals[index] if index < len(visuals) else ""


def _beat_text(_bt, matrix_seed, index) -> str:  # noqa: ARG001
    texts = [
        matrix_seed.hook,
        "日常叙述，不露声色地推进",
        "加速叙述，矛盾升级",
        matrix_seed.twist_hint[:20] if len(matrix_seed.twist_hint) > 20 else matrix_seed.twist_hint,
        "（画面留白，不写文字）",
    ]
    return texts[index] if index < len(texts) else ""


def _beat_camera(_bt, index) -> str:  # noqa: ARG001
    cameras = [
        "全景/远景开场，建立场景感",
        "中景，跟随角色动作",
        "特写切换，加快节奏",
        "特写或反应镜头，揭示关键信息",
        "远景或背影，慢慢远离，留白收场",
    ]
    return cameras[index] if index < len(cameras) else "中景"


def _short_title(text: str, max_len: int = 15) -> str:
    """Extract a short title from a longer concept string."""
    # Try to find the first meaningful phrase
    if len(text) <= max_len:
        return text
    # Cut at first punctuation or conjunction
    for i, c in enumerate(text):
        if c in "，。、；！？" and i > 3:
            return text[:i]
    return text[:max_len] + "…"
