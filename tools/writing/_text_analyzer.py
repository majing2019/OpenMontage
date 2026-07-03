"""Pure-Python Chinese text analyzer for extracting story concepts.

Rule-based analysis of arbitrary-length Chinese text (jokes, anecdotes,
short stories) to extract: core concept, emotion, characters, scenes,
and reversal/punchline points.

No external dependencies — uses only `re` from stdlib.

The extracted core_concept feeds directly into the what-if engine
as `source_concept` for story seed generation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ._emotion_matrix import SCENES


@dataclass
class TextAnalysisResult:
    """Output of text analysis — ready to feed into Story Factory."""

    core_concept: str
    """1-2 sentence summary suitable as source_concept for what-if engine."""

    emotion_guess: str | None = None
    """Best-guess emotion from the EMOTIONS list, or None if unclear."""

    character_hints: list[str] = field(default_factory=list)
    """Role names found in text (e.g. ["妈妈", "外卖小哥"])."""

    reversal_point: str | None = None
    """The sentence containing the punchline/reversal, or None."""

    scene_hints: list[str] = field(default_factory=list)
    """Location words found (e.g. ["地铁", "办公室"])."""

    original_length: int = 0
    """Character count of the input text."""


# ── Sentence splitting ──────────────────────────────────────────────────

_CHINESE_SENTENCE_RE = re.compile(r"[。！？.!?\n]+")
_CONCEPT_MAX_CHARS = 60


def _split_sentences(text: str) -> list[str]:
    """Split Chinese/English text into sentences."""
    raw = re.split(_CHINESE_SENTENCE_RE, text)
    return [s.strip() for s in raw if s.strip()]


# ── Reversal / punchline detection ──────────────────────────────────────

# Contrast markers: words that signal a reversal or reveal
_CONTRAST_MARKERS = [
    "但是", "结果", "原来", "没想到", "其实", "然而",
    "谁知", "谁想到", "哪知道", "哪想到", "不料",
    "却发现", "才知道", "才明白", "才意识到", "才反应过来",
    "万万没想到", "突然", "忽然", "竟然", "居然",
]

# Question-answer pattern
_QUESTION_RE = re.compile(r".*？$")


def _find_reversal_point(sentences: list[str]) -> str | None:
    """Find the sentence most likely to be the punchline/reversal.

    Priority order:
    1. Sentence containing a contrast marker (highest weight)
    2. Sentence answering a preceding question
    3. Short punchline after long setup (classic joke structure)
    """
    # Priority 1: contrast markers
    for s in sentences:
        for marker in _CONTRAST_MARKERS:
            if marker in s:
                return s

    # Priority 2: question → answer pattern
    for i in range(len(sentences) - 1):
        if _QUESTION_RE.match(sentences[i]):
            return sentences[i + 1]

    # Priority 3: length-drop heuristic (long setup, short punchline)
    if len(sentences) >= 2:
        avg_len = sum(len(s) for s in sentences[:-1]) / max(len(sentences) - 1, 1)
        last_sent = sentences[-1]
        if avg_len > 20 and len(last_sent) < avg_len * 0.5:
            return last_sent

    # Fallback: last meaningful sentence
    return sentences[-1] if sentences else None


# ── Core concept extraction ─────────────────────────────────────────────

def _extract_core_concept(_text: str, reversal_point: str | None,  # noqa: ARG001
                          sentences: list[str]) -> str:
    """Extract a 1-2 sentence summary from the text.

    If reversal found: takes the sentence before reversal + reversal.
    Otherwise: takes first 1-2 meaningful sentences.
    Truncates to CONCEPT_MAX_CHARS.
    """
    if reversal_point and reversal_point in sentences:
        idx = sentences.index(reversal_point)
        # Take the sentence right before the reversal as setup
        setup = sentences[idx - 1] if idx > 0 else sentences[0] if len(sentences) > idx + 1 else ""
        if setup:
            concept = f"{setup}——{reversal_point}"
        else:
            concept = reversal_point
    else:
        # Take first 1-2 sentences
        concept = "——".join(sentences[:2])

    # Truncate
    if len(concept) > _CONCEPT_MAX_CHARS:
        concept = concept[:_CONCEPT_MAX_CHARS - 1] + "…"

    return concept.strip()


# ── Emotion guessing ────────────────────────────────────────────────────

_EMOTION_KEYWORDS: dict[str, list[str]] = {
    "惊讶": ["惊讶", "没想到", "万万没想到", "竟然", "居然", "吓了一跳", "目瞪口呆",
             "反转", "神转折", "懵了", "不敢相信", "天哪", "我的天"],
    "感动": ["感动", "泪", "哭了", "眼眶", "暖心", "泪目", "鼻子一酸", "哽咽",
             "泣不成声", "湿润", "暖到了"],
    "好笑": ["笑", "哈哈", "搞笑", "尴尬", "社死", "翻车", "无语", "笑喷",
             "笑死", "笑疯", "奇葩", "离谱", "绷不住"],
    "紧张": ["紧张", "害怕", "慌", "心跳", "倒计时", "手心出汗", "发抖",
             "屏住呼吸", "惊险", "千钧一发"],
    "温暖": ["温暖", "暖", "善良", "温柔", "递", "帮助", "感动", "拥抱",
             "阳光", "暖意", "善举", "不约而同"],
    "心酸": ["心酸", "难过", "沉默", "一个人", "独自", "孤独", "委屈",
             "不容易", "辛苦", "打工", "奔波", "疲惫"],
    "愤怒": ["愤怒", "气死", "忍不了", "凭什么", "不公平", "暴怒", "火冒三丈",
             "气炸", "忍无可忍", "欺人太甚"],
    "治愈": ["治愈", "释然", "平静", "放下", "微笑", "和解", "接纳",
             "释怀", "松弛", "自洽", "和解"],
}


def _guess_emotion(text: str, reversal_point: str | None) -> str | None:
    """Guess the dominant emotion from keyword matching.

    Scans the reversal point first (higher weight), then full text.
    """
    # Priority: reversal sentence, then full text
    search_texts = [reversal_point] if reversal_point else []
    search_texts.append(text)

    scores: dict[str, int] = {}
    for search in search_texts:
        weight = 2 if search == reversal_point else 1
        for emotion, keywords in _EMOTION_KEYWORDS.items():
            for kw in keywords:
                if kw in search:
                    scores[emotion] = scores.get(emotion, 0) + weight

    if scores:
        return max(scores, key=scores.get)  # type: ignore[arg-type]
    return None


# ── Character extraction ────────────────────────────────────────────────

_CHARACTER_ROLES: list[str] = [
    "妈妈", "爸爸", "孩子", "老板", "老人", "外卖小哥", "服务员",
    "奶奶", "外婆", "爷爷", "外公", "男朋友", "女朋友",
    "同事", "室友", "邻居", "陌生人", "司机", "保安", "保洁阿姨",
    "医生", "护士", "老师", "学生", "外卖员", "快递员",
]


def _extract_characters(text: str) -> list[str]:
    """Extract character role mentions from text."""
    found: list[str] = []
    seen: set[str] = set()

    for role in _CHARACTER_ROLES:
        if role in text and role not in seen:
            found.append(role)
            seen.add(role)

    # Broader pattern matches
    if any(kw in text for kw in ["加班", "上班", "下班", "工位", "开会", "摸鱼"]) and "打工人" not in seen:
        found.append("打工人")
        seen.add("打工人")
    if any(kw in text for kw in ["大学生", "毕业", "实习"]) and "年轻人" not in seen:
        found.append("年轻人")
        seen.add("年轻人")

    return found[:4]


# ── Scene extraction ────────────────────────────────────────────────────

_EXTRA_SCENES: list[str] = [
    "家里", "公司", "路边", "公交车上", "出租车上",
    "火车站", "机场", "菜市场", "书店", "咖啡馆",
]


def _extract_scenes(text: str) -> list[str]:
    """Extract location/scene mentions from text."""
    found: list[str] = []
    seen: set[str] = set()

    for scene in SCENES + _EXTRA_SCENES:
        if scene in text and scene not in seen:
            found.append(scene)
            seen.add(scene)

    return found[:3]


# ── Main entry point ────────────────────────────────────────────────────

def analyze_text(text: str) -> TextAnalysisResult:
    """Analyze Chinese text and extract story concept.

    Args:
        text: Any length of Chinese text (joke, anecdote, story).

    Returns:
        TextAnalysisResult with core_concept, emotion, characters, etc.
    """
    text = text.strip()
    if not text:
        return TextAnalysisResult(core_concept="", original_length=0)

    sentences = _split_sentences(text)
    reversal = _find_reversal_point(sentences)
    core = _extract_core_concept(text, reversal, sentences)
    emotion = _guess_emotion(text, reversal)
    characters = _extract_characters(text)
    scenes = _extract_scenes(text)

    # If no core concept was extractable, use truncated text
    if not core:
        core = text[:_CONCEPT_MAX_CHARS]

    return TextAnalysisResult(
        core_concept=core,
        emotion_guess=emotion,
        character_hints=characters,
        reversal_point=reversal,
        scene_hints=scenes,
        original_length=len(text),
    )
