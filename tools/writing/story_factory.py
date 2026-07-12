"""Story Factory — automated comic story ideation tool for short-form Douyin videos.

Generates structured story seeds with 5-beat narratives, character archetypes,
visual suggestions, and style keywords ready for Seedream image generation.

Includes a lightweight `pitch` mode that produces 5-8 one-sentence story ideas
for a fast brainstorming round before committing to a full seed.

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
from ._polarity_engine import collide, get_dimension_names
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
    {"role": "妈妈", "description": "中年亚洲女性，温柔但倔强，用看似笨拙的方式表达关心", "emotional_state": "操心但故作轻松", "visual_notes": "50岁左右亚洲女性，齐肩短发，微胖，常穿碎花围裙或米色开衫，笑起来眼睛弯弯",
     "physiological": "50岁，女性，体型微胖，齐肩短发带自然卷，戴老花镜，手背有褐斑",
     "sociological": "退休或半退休家庭主妇，照顾家庭三代人，经济依赖子女，社交圈缩小到广场舞和菜市场",
     "psychological": "内心恐惧失去家庭价值，通过过度照顾获得存在感，习惯性忽略自己的需求",
     "sacred_flaw": "相信'只有我能照顾好这个家'——实际是控制欲和被需要的需求在驱动",
     "trauma_origin": "年轻时可能因为事业放弃自我，把全部身份绑在'母亲'角色上",
     "desire_want": "让每个人吃得健康、穿得暖和、不出差错",
     "desire_need": "学会放手，接受孩子们已经长大了，找到属于自己的生活",
     "opponent_mirror": "子女的独立行为映射了她无法接受的'被抛弃'恐惧",
     "action_under_pressure": "频繁打电话、送食物、假装路过检查、把关心变成控制"},
    {"role": "爸爸", "description": "中年男性，沉默寡言，用行动代替语言", "emotional_state": "内心柔软但表面严肃", "visual_notes": "55岁左右亚洲男性，短发带灰，身材中等，常穿深色夹克或格子衬衫，额头有皱纹",
     "physiological": "55岁，男性，中等身材开始发福，短发灰白，有老花镜但不常戴，走路微驼",
     "sociological": "即将退休或刚退休的蓝领/中层管理，一辈子靠工作定义自己，不善表达感情",
     "psychological": "相信'男人就该扛着'，把所有脆弱藏起来，用沉默代替沟通，害怕被认为软弱",
     "sacred_flaw": "相信'不表达=不影响'——实际是情感隔离导致了关系的疏远",
     "trauma_origin": "成长在'男人不能哭'的时代，父亲也是个沉默的人",
     "desire_want": "维持家庭的物质稳定，不被任何人担心",
     "desire_need": "学会表达爱，接受自己也需要被照顾",
     "opponent_mirror": "子女的情感需求映射了他无法面对的'我不会爱'恐惧",
     "action_under_pressure": "更加沉默，偷偷做事情（如偷偷修东西、偷偷查资料），在夜里独自承担"},
    {"role": "打工人", "description": "20-30岁上班族，疲惫但还在撑着", "emotional_state": "表面平静内心崩溃中", "visual_notes": "25-30岁亚洲男性或女性，黑眼圈，穿休闲西装或卫衣，背包永远在肩膀上",
     "physiological": "28岁，长期熬夜导致黑眼圈和微驼，体型偏瘦或过劳肥，手机不离手",
     "sociological": "一二线城市白领，租房，远离家乡，社交主要靠同事和网友，存款不足以买房",
     "psychological": "在'坚持'和'放弃'之间反复拉扯，用忙碌逃避思考人生方向，对未来焦虑但不敢停下",
     "sacred_flaw": "相信'再忍忍就好了'——实际是在用忍耐逃避选择",
     "trauma_origin": "从小被教育'吃得苦中苦方为人上人'，把忍耐等同于美德",
     "desire_want": "升职加薪，被认可，证明自己的选择是对的",
     "desire_need": "找到真正想做的事，而不是别人觉得应该做的事",
     "opponent_mirror": "那些'已经放弃'的人映射了ta不敢面对的'也许放弃才是对的'念头",
     "action_under_pressure": "更加拼命工作，刷手机逃避，在深夜突然崩溃然后第二天装作无事"},
    {"role": "陌生人", "description": "不知名的路人，可能成为故事的关键人物", "emotional_state": "平静但有自己的故事", "visual_notes": "任何年龄，穿着普通但有一个细节特征（如围巾、帽子、背包挂件）",
     "physiological": "年龄不定，普通外貌，但有一个辨识特征（围巾、手套、背包挂件、步态）",
     "sociological": "在城市中独自生活的普通人，有自己的日常轨迹，与主角的生命只有短暂的交集",
     "psychological": "有自己的故事和伤痛，但已经学会了与之共处，偶尔的善意是出于'我也被帮助过'",
     "sacred_flaw": "相信'不介入是最好的善良'——实际是害怕建立联系后被辜负",
     "trauma_origin": "曾经帮助过别人却遭到误解或伤害，学会了保持距离",
     "desire_want": "过好自己的日子，不被打扰",
     "desire_need": "重新相信人与人之间的连接是值得的",
     "opponent_mirror": "主角的脆弱映射了ta回避的自己曾经的脆弱",
     "action_under_pressure": "短暂犹豫后做出一个小小的善意举动——然后迅速离开"},
    {"role": "孩子", "description": "5-10岁的小孩，纯真但偶尔说出让人意外的话", "emotional_state": "天真无邪", "visual_notes": "7岁左右亚洲小孩，短发或扎辫子，校服或T恤，表情丰富",
     "physiological": "7岁，身材小巧，表情极其丰富且不掩饰，动作直接，声音响亮",
     "sociological": "小学生，世界由家庭和学校组成，对成人世界充满好奇但理解有限",
     "psychological": "用最简单的逻辑理解世界，没有成人式的复杂动机，说真话因为还不知道要撒谎",
     "sacred_flaw": "没有'神圣缺陷'——孩子的 sacred flaw 就是'没有缺陷'，这反而让成人感到被映照",
     "trauma_origin": "可能还没有创伤——或者创伤正在形成中（如父母争吵、被忽视）",
     "desire_want": "玩、被关注、得到想要的东西",
     "desire_need": "被认真对待——而不是被当成'只是个孩子'",
     "opponent_mirror": "映射了成人丢失的纯真和直接",
     "action_under_pressure": "直接说出大人不敢说的话，用简单的行动做大人做不到的事"},
    {"role": "老板", "description": "严厉但有温度的上司", "emotional_state": "表面严肃内心关心", "visual_notes": "40-50岁亚洲男性，西装革履，戴眼镜，严肃表情但偶尔露出微笑",
     "physiological": "45岁，精瘦有力，穿着讲究但不炫耀，戴金丝眼镜，握手有力",
     "sociological": "从底层打拼上来的管理者，经历过公司从创业到成熟，手下的年轻人像当年的自己",
     "psychological": "用严厉掩饰关心——因为过去的经历告诉他'心软会被人利用'，但内心仍然柔软",
     "sacred_flaw": "相信'严格要求才是真的负责'——实际是把控制的焦虑包装成关心",
     "trauma_origin": "年轻时被心软的上司坑过，发誓'我绝不会犯同样的错'",
     "desire_want": "团队出业绩，公司发展，证明自己的管理方式是对的",
     "desire_need": "学会信任别人，接受'不完美但真实的关心'比'完美但冰冷的严格'更有效",
     "opponent_mirror": "下属的犯错映射了他对自己当年犯同样错的记忆",
     "action_under_pressure": "更加严厉，但在所有人都下班后独自加班帮下属解决问题"},
    {"role": "老人", "description": "70岁以上，经历过很多但还在认真活着", "emotional_state": "平静中带感慨", "visual_notes": "75岁左右亚洲人，满头白发，微驼，穿深色棉衣或中山装，手上纹路深",
     "physiological": "75岁，行动缓慢但坚定，满头白发，手上有深深的纹路，眼神却异常清澈",
     "sociological": "退休老人，独居或与老伴相依，每天有固定的散步路线，是社区里的'活历史'",
     "psychological": "经历过太多失去，已经学会了不期待，但内心的柔软从未消失——只是藏得很深",
     "sacred_flaw": "相信'不期待就不会失望'——实际是用自我保护阻止了最后可能的温暖",
     "trauma_origin": "失去过重要的人（配偶、朋友、事业），学会了'一个人也行'",
     "desire_want": "安安静静过完剩下的日子，不给任何人添麻烦",
     "desire_need": "重新允许自己被需要、被在乎——接受'依赖不是负担'",
     "opponent_mirror": "年轻人的热情映射了他已经放弃的'也许生活还能不一样'的念头",
     "action_under_pressure": "表面上说'没事没事'，但在无人的时候默默做了一些温暖的事"},
    {"role": "年轻人", "description": "大学生或刚毕业的年轻人，充满希望又有点迷茫", "emotional_state": "热情但焦虑", "visual_notes": "22岁左右亚洲人，穿卫衣牛仔裤，背双肩包，眼睛明亮",
     "physiological": "22岁，精力充沛但作息混乱，穿着随性但有自己的一套审美，永远在赶路",
     "sociological": "应届毕业生或大三/大四学生，面临就业和未来的十字路口，朋友圈里同龄人差距开始拉大",
     "psychological": "充满理想但现实不断打脸，在'做自己'和'被社会接受'之间撕裂，用理想主义掩饰焦虑",
     "sacred_flaw": "相信'只要努力就能成功'——实际是害怕承认运气和出身的作用",
     "trauma_origin": "从小被夸'聪明的孩子'，害怕有一天发现自己其实很普通",
     "desire_want": "找到一份体面的工作，证明自己的价值",
     "desire_need": "接受'普通'不等于'失败'，找到自己的节奏而不是追赶别人的",
     "opponent_mirror": "已经'安定下来'的同龄人映射了对'我选错了吗'的恐惧",
     "action_under_pressure": "表面更加自信和亢奋，深夜在备忘录里写下自我怀疑"},
    {"role": "外卖小哥", "description": "匆忙但善良的外卖骑手", "emotional_state": "赶时间但内心温和", "visual_notes": "25-35岁亚洲男性，穿着黄色或蓝色骑手服，戴头盔，皮肤晒黑",
     "physiological": "30岁，常年日晒导致皮肤黝黑粗糙，手上有茧，身材精瘦有力，夏天汗水浸透骑手服",
     "sociological": "从农村或小城镇来到大城市，靠体力劳动养家，每天与倒计时赛跑，被算法驱动",
     "psychological": "把生活的苦藏在笑脸后面，用幽默消解疲惫，对时间极度敏感因为每一秒都是钱",
     "sacred_flaw": "相信'吃苦就能出头'——实际是系统性困境让个人努力收效甚微",
     "trauma_origin": "可能背负家庭债务或孩子的学费，不敢停下来",
     "desire_want": "准时送达每一单，拿到好评，多跑几单多赚一点",
     "desire_need": "被当作一个'人'而不是一个'配送工具'来看待",
     "opponent_mirror": "点外卖的顾客映射了他'如果我读了书是不是就不会这样'的不甘",
     "action_under_pressure": "咬紧牙关继续跑，但在某个等红绿灯的瞬间突然发呆"},
    {"role": "服务员", "description": "餐厅或便利店的员工，默默观察着每个人", "emotional_state": "客气但心里有自己的判断", "visual_notes": "20-30岁，穿制服，围裙，面带职业微笑，但眼睛很亮",
     "physiological": "25岁，站一整天导致腿脚酸痛，但训练有素的站姿，微笑时眼角有细纹",
     "sociological": "服务业从业者，见惯了人情冷暖，每天观察不同顾客的故事，是城市的'隐形观察者'",
     "psychological": "职业性的礼貌下隐藏着敏锐的观察力和判断力，对人性有独到理解但不轻易表露",
     "sacred_flaw": "相信'观察就够了'——实际是用旁观者身份逃避参与生活的责任",
     "trauma_origin": "曾经试图帮助顾客却遭到投诉，学会了'不介入是职业素养'",
     "desire_want": "做好本职工作，不被投诉，安稳过每一天",
     "desire_need": "从旁观者变成参与者——用自己的观察力去做一些有意义的事",
     "opponent_mirror": "陷入困境的顾客映射了自己曾经旁观他人困境时的愧疚",
     "action_under_pressure": "职业微笑之下做了一个微小的打破规则的决定"},
    {"role": "闺蜜/兄弟", "description": "主角最好的朋友，嘴上毒但心里暖", "emotional_state": "吐槽但关键时刻靠得住", "visual_notes": "和主角年龄相仿，穿着随意，表情丰富",
     "physiological": "与主角同龄，穿着更随意，表情极其丰富，说话时手舞足蹈",
     "sociological": "与主角从小认识或大学同学，是主角唯一能真实面对的人，知道主角的所有秘密",
     "psychological": "用毒舌和吐槽掩饰关心——因为认真的关心会显得'太肉麻'，但关键时刻绝对靠谱",
     "sacred_flaw": "相信'吐槽才是真朋友'——实际是害怕真诚表达后被拒绝",
     "trauma_origin": "曾经认真表达关心却被嘲笑'太矫情'，学会了用玩笑包装真心",
     "desire_want": "和朋友一起玩闹，维持轻松的关系",
     "desire_need": "学会在需要的时候放下玩笑，真诚地说'我在乎你'",
     "opponent_mirror": "主角的脆弱映射了自己一直假装不在乎的同类脆弱",
     "action_under_pressure": "突然收起所有玩笑，说出一句极其认真的话"},
    {"role": "奶奶/外婆", "description": "高龄但精神矍铄的老太太", "emotional_state": "慈祥但倔强", "visual_notes": "75岁以上亚洲女性，银发盘髻或烫小卷，穿深色棉袄，手布满皱纹但动作利索",
     "physiological": "80岁，银发但梳理得一丝不苟，手布满皱纹但动作出奇地利索，走路用拐杖但不依赖",
     "sociological": "经历了大半世纪的中国历史，是家族记忆的活载体，对年轻一代有绝对的道德权威",
     "psychological": "倔强来源于'我什么都见过'的底气，但内心最柔软的地方是孙辈——唯一的软肋",
     "sacred_flaw": "相信'老人就该被尊敬'——实际是害怕被时代抛弃、被遗忘",
     "trauma_origin": "经历过动荡年代，学会了'只有自己坚强才能活下来'——但也因此不会求助",
     "desire_want": "被需要、被请教、被尊重——证明自己还有价值",
     "desire_need": "学会向年轻人展示脆弱，接受'被照顾不等于没用'",
     "opponent_mirror": "孙辈的忙碌映射了'他们不需要我了'的恐惧",
     "action_under_pressure": "嘴上说'不用管我'，但偷偷把最好的东西留给孙辈"},
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
                "enum": ["emotion_matrix", "what_if", "daily_catch", "random", "batch", "from_text", "from_video", "polarity", "pitch"],
                "description": "Generation mode. pitch: lightweight one-sentence story ideas for brainstorming. polarity: collide opposite poles from life dimensions to generate one-liner stories. from_text: analyze text → story seeds. from_video: analyze video → story seeds.",
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
            "dimension": {
                "type": "string",
                "description": f"Polarity dimension name for polarity mode. Options: {', '.join(get_dimension_names())}. None = random.",
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
            elif mode == "polarity":
                seeds = self._gen_polarity(inputs, count, rng, target_duration, char_count)
            elif mode == "random":
                seeds = self._gen_random(inputs, count, rng, target_duration, char_count)
            elif mode == "batch":
                seeds = self._gen_batch(inputs, count, rng, target_duration, char_count)
            elif mode == "from_text":
                seeds = self._gen_from_text(inputs, count, rng, target_duration, char_count)
            elif mode == "from_video":
                seeds = self._gen_from_video(inputs, count, rng, target_duration, char_count)
            elif mode == "pitch":
                seeds = self._gen_pitch(inputs, count, rng)
                # Pitch mode returns lightweight loglines, not full seeds.
                # Wrap them to match the expected output structure.
                result = ToolResult(
                    success=True,
                    data={
                        "pitches": seeds,
                        "generation_mode": "pitch",
                        "total": len(seeds),
                        "hint": "User picks one pitch → re-run with mode='from_text' using the chosen logline as text_content to develop the full story_seed.",
                    },
                    duration_seconds=round(time.time() - start, 3),
                    cost_usd=0.0,
                    seed=seed_val,
                )
                return result
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown mode: {mode}. "
                          f"Valid modes: emotion_matrix, what_if, daily_catch, random, batch, from_text, from_video, pitch",
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

    def _gen_polarity(
        self, inputs, count, rng, duration, char_count
    ) -> list[dict]:
        """Generate story seeds via polarity collision."""
        dimension_name = inputs.get("dimension")
        pattern_name = inputs.get("pattern")
        collisions = collide(
            dimension_name=dimension_name,
            count=count,
            rng=rng,
        )
        seeds = []
        for c in collisions:
            seeds.append(self._build_seed_from_polarity(
                collision=c,
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
        modes = ["emotion_matrix", "daily_catch", "random", "polarity"]
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
            elif mode == "polarity":
                all_seeds.extend(self._gen_polarity(batch_inputs, c, rng, duration, char_count))

        return all_seeds[:count]

    # ── pitch mode ───────────────────────────────────────────────────
    def _gen_pitch(
        self, inputs, count: int, rng
    ) -> list[dict]:
        """Generate lightweight one-sentence story pitches for brainstorming.

        Each pitch is a single sentence that captures the core story hook.
        No full 5-beat structure — just enough for the user to gauge interest.

        Source mix (when no input provided — "给我灵感"):
          ~40% polarity collisions — vivid conflict images from life dimensions
          ~30% what-if on daily observations — everyday moments transformed
          ~30% emotion matrix — random picks from 200+ pre-seeded concepts

        This gives pitch the same source diversity as batch, but in lightweight form.
        """
        from ._polarity_engine import collide

        text_content = inputs.get("text_content", "")
        emotion = inputs.get("emotion")
        scene = inputs.get("scene")

        # Ensure we generate at least 5 pitches for a good selection
        actual_count = max(count, 5)

        pitches: list[dict] = []

        if text_content:
            # ── has raw material: pure what-if on the text ──────────
            analysis = analyze_text(text_content)
            source = analysis.core_concept
            if source:
                whatif_results = transform(source, rules=None, rng=rng)
                for wr in whatif_results:
                    emotion_guess = EMOTIONS[rng.randint(0, len(EMOTIONS) - 1)]
                    style_key = EMOTION_STYLE_MAP.get(emotion_guess, "warm_illustration")
                    pitches.append({
                        "logline": wr.transformed_concept,
                        "emotion": emotion_guess,
                        "pattern_hint": wr.pattern_suggestion,
                        "twist_type": wr.rule_name,
                        "style_hint": style_key,
                        "seedream_keywords": STYLE_PRESETS.get(style_key, STYLE_PRESETS["warm_illustration"])["seedream_keywords"],
                        "source": "what_if",
                    })
            # Pad with matrix seeds to reach actual_count
            while len(pitches) < actual_count:
                matrix_seed = get_random_seed(emotion, scene, rng)
                if not matrix_seed:
                    continue
                pitches.append(self._matrix_seed_to_pitch(matrix_seed, rng))

        elif emotion or scene:
            # ── has direction: mix matrix + polarity ─────────────────
            # ~60% matrix (respecting the user's emotion/scene direction)
            matrix_target = max(3, int(actual_count * 0.6))
            while len([p for p in pitches if p.get("source") == "matrix"]) < matrix_target:
                matrix_seed = get_random_seed(emotion, scene, rng)
                if not matrix_seed:
                    continue
                pitches.append(self._matrix_seed_to_pitch(matrix_seed, rng))

            # ~40% polarity (random dimensions — surprise the user)
            polarity_count = actual_count - len(pitches)
            collisions = collide(count=polarity_count, rng=rng, compact=True)
            for c in collisions:
                style_key = EMOTION_STYLE_MAP.get(c.suggested_emotion, "warm_illustration")
                pitches.append({
                    "logline": c.one_liner,
                    "emotion": c.suggested_emotion,
                    "pattern_hint": c.pattern_hint,
                    "twist_type": "极性碰撞",
                    "style_hint": style_key,
                    "seedream_keywords": STYLE_PRESETS.get(style_key, STYLE_PRESETS["warm_illustration"])["seedream_keywords"],
                    "source": "polarity",
                    "polarity_dimension": c.dimension_name,
                    "polarity_pole_a": c.pole_a,
                    "polarity_pole_b": c.pole_b,
                })

        else:
            # ── no input ("给我灵感"): mix all three sources ────────
            sources = ["polarity", "what_if_observation", "matrix"]
            per_source = max(1, actual_count // len(sources))
            remainder = actual_count - per_source * len(sources)

            # Source 1: polarity collisions (~40%)
            p_count = per_source + (1 if remainder > 0 else 0)
            collisions = collide(count=p_count, rng=rng, compact=True)
            for c in collisions:
                style_key = EMOTION_STYLE_MAP.get(c.suggested_emotion, "warm_illustration")
                pitches.append({
                    "logline": c.one_liner,
                    "emotion": c.suggested_emotion,
                    "pattern_hint": c.pattern_hint,
                    "twist_type": "极性碰撞",
                    "style_hint": style_key,
                    "seedream_keywords": STYLE_PRESETS.get(style_key, STYLE_PRESETS["warm_illustration"])["seedream_keywords"],
                    "source": "polarity",
                    "polarity_dimension": c.dimension_name,
                    "polarity_pole_a": c.pole_a,
                    "polarity_pole_b": c.pole_b,
                })

            # Source 2: what-if on daily observations (~30%)
            w_count = per_source + (1 if remainder > 1 else 0)
            used_obs: set[str] = set()
            obs_attempts = 0
            while len([p for p in pitches if p.get("source") == "what_if_observation"]) < w_count and obs_attempts < w_count * 3:
                obs = get_daily_observation(rng)
                if obs in used_obs:
                    obs_attempts += 1
                    continue
                used_obs.add(obs)
                obs_attempts += 1
                whatif_results = transform(obs, rules=None, rng=rng)
                wr = rng.choice(whatif_results)
                emotion_guess = EMOTIONS[rng.randint(0, len(EMOTIONS) - 1)]
                style_key = EMOTION_STYLE_MAP.get(emotion_guess, "warm_illustration")
                pitches.append({
                    "logline": wr.transformed_concept,
                    "emotion": emotion_guess,
                    "pattern_hint": wr.pattern_suggestion,
                    "twist_type": wr.rule_name,
                    "style_hint": style_key,
                    "seedream_keywords": STYLE_PRESETS.get(style_key, STYLE_PRESETS["warm_illustration"])["seedream_keywords"],
                    "source": "what_if_observation",
                })

            # Source 3: emotion matrix random seeds (~30%)
            m_count = actual_count - len(pitches)
            while len([p for p in pitches if p.get("source") == "matrix"]) < m_count:
                matrix_seed = get_random_seed(None, None, rng)
                if not matrix_seed:
                    continue
                pitches.append(self._matrix_seed_to_pitch(matrix_seed, rng))

        # Deduplicate by logline — only trim duplicates within same source
        seen: set[str] = set()
        unique: list[dict] = []
        for p in pitches:
            if p["logline"] not in seen:
                seen.add(p["logline"])
                unique.append(p)

        # If dedup dropped us below actual_count, pad with matrix
        while len(unique) < actual_count:
            matrix_seed = get_random_seed(emotion, scene, rng)
            if not matrix_seed:
                continue
            p = self._matrix_seed_to_pitch(matrix_seed, rng)
            if p["logline"] not in seen:
                seen.add(p["logline"])
                unique.append(p)

        return unique[:actual_count]

    def _matrix_seed_to_pitch(self, matrix_seed, rng) -> dict:
        """Convert a MatrixSeed into a lightweight pitch dict."""
        emo = rng.choice(EMOTIONS)
        style_key = EMOTION_STYLE_MAP.get(emo, "warm_illustration")
        return {
            "logline": matrix_seed.logline,
            "emotion": emo,
            "pattern_hint": matrix_seed.pattern_name if matrix_seed.pattern_name else "日常英雄",
            "twist_type": _twist_type_from_emotion(emo),
            "style_hint": style_key,
            "seedream_keywords": STYLE_PRESETS.get(style_key, STYLE_PRESETS["warm_illustration"])["seedream_keywords"],
            "source": "matrix",
        }

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
        ending = _build_ending(pattern.category, emotion)

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
            "ending": ending["description"],
            "ending_type": ending["ending_type"],
            "closing_image_hint": ending["closing_image_hint"],
            "page_turn_hook": ending["page_turn_hook"],
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
        ending = _build_ending(pattern.category, emotion)

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
            "ending": ending["description"],
            "ending_type": ending["ending_type"],
            "closing_image_hint": ending["closing_image_hint"],
            "page_turn_hook": ending["page_turn_hook"],
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

    def _build_seed_from_polarity(
        self,
        collision,
        pattern_name: str | None,
        duration: float,
        char_count: int,
        rng: random.Random,
    ) -> dict:
        """Build a full story seed from a polarity collision result."""
        if pattern_name and pattern_name in PATTERN_BY_NAME:
            pattern = PATTERN_BY_NAME[pattern_name]
        elif collision.pattern_hint in PATTERN_BY_NAME:
            pattern = PATTERN_BY_NAME[collision.pattern_hint]
        else:
            candidates = EMOTION_PATTERN_MAP.get(collision.suggested_emotion, ["日常英雄"])
            pattern = PATTERN_BY_NAME.get(
                rng.choice(candidates), PATTERNS[0]
            )

        emotion = collision.suggested_emotion
        style_key = EMOTION_STYLE_MAP.get(emotion, "warm_illustration")
        style = STYLE_PRESETS[style_key]

        concise = _short_title(collision.one_liner, max_len=20)
        matrix_seed = _LightSeed(
            title=concise,
            logline=collision.one_liner,
            hook=collision.one_liner,
            pattern_name=pattern.name,
            character_roles=[],
            twist_hint=f"[{collision.dimension_name}] {collision.pole_a} ↔ {collision.pole_b}",
            visual_keywords=[],
        )

        beats = self._build_beats(pattern, duration, matrix_seed)
        characters = self._select_characters([], char_count, rng)

        seed_id = _make_seed_id(matrix_seed.title, pattern.name)
        ending = _build_ending(pattern.category, emotion)

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
            "ending": ending["description"],
            "ending_type": ending["ending_type"],
            "closing_image_hint": ending["closing_image_hint"],
            "page_turn_hook": ending["page_turn_hook"],
            "character_archetypes": characters,
            "suggested_style": style,
            "visual_keywords": matrix_seed.visual_keywords,
            "polarity_dimension": collision.dimension_name,
            "polarity_dimension_en": collision.dimension_name_en,
            "polarity_pole_a": collision.pole_a,
            "polarity_pole_b": collision.pole_b,
            "polarity_trigger": collision.trigger,
            "target_platform": "douyin",
            "target_duration_seconds": duration,
            "estimated_image_count": len(beats),
            "difficulty": pattern.difficulty,
            "generation_mode": f"polarity ({collision.dimension_name})",
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


def _build_ending(category: str, emotion: str, _opening_hint: str | None = None) -> dict:
    """Build ending with type, description, Snyder closing-image contrast, and page-turn hook.

    Sources:
    - Snyder Opening/Closing Image Contrast (Save the Cat)
    - 4 Resolution Types (positive, negative, ironic, open_ended)
    - Page Turn Suspense (manga: 右页最后一格 = prime悬念位)
    """
    # Ending descriptions by (category, emotion)
    descriptions = {
        ("comedy", "好笑"): "用一个苦笑或沉默的定格收场，不解释，让观众自己回味",
        ("comedy", "惊讶"): "画面定格在一个意外的表情上，让观众自己笑",
        ("emotional", "感动"): "用一个背影或侧脸收场，不说话——留白比煽情更有力量",
        ("emotional", "心酸"): "画面慢慢远去，用安静代替眼泪",
        ("emotional", "温暖"): "两个人各自离开，但观众知道他们心里有什么变了",
        ("suspense", "惊讶"): "回到平静表面，但观众已经知道了真相",
        ("suspense", "紧张"): "回到那个选择的瞬间，问观众：你会怎么做",
        ("slice_of_life", "治愈"): "同样的场景，但阳光不一样了——心情也变了",
        ("social", "惊讶"): "用一个令人意外的结果收尾，让观众想再看一遍",
        ("social", "温暖"): "问题解决了，但留一个小尾巴让观众思考",
    }

    # Ending type by category
    ending_type_map = {
        "comedy": "ironic",
        "emotional": "positive",
        "suspense": "open_ended",
        "slice_of_life": "positive",
        "social": "positive",
    }

    # Snyder closing-image hint: contrast with opening
    closing_image_hint = _snyder_closing(category, emotion)

    # Page-turn hook (manga technique): 右页最后一格的悬念设计
    page_turn_hook = _page_turn_hook(category, emotion)

    return {
        "description": descriptions.get((category, emotion), "用一个安静的定格收场，让观众自己感受"),
        "ending_type": ending_type_map.get(category, "positive"),
        "closing_image_hint": closing_image_hint,
        "page_turn_hook": page_turn_hook,
    }


def _snyder_closing(category: str, emotion: str) -> str:
    """Snyder Opening/Closing Image Contrast — the closing image must prove transformation.

    The closing panel should mirror the opening panel but show how the protagonist
    or situation has fundamentally changed.
    """
    contrasts = {
        ("comedy", "好笑"): "与开篇同样的场景，但主角的表情从认真变成了苦笑——观众才知道一切都是喜剧",
        ("comedy", "惊讶"): "与开篇同样的人，同样的位置，但周围人的反应完全相反",
        ("emotional", "感动"): "与开篇同样的场景，但这一次主角身边多了一个人，或者手里多了一样东西",
        ("emotional", "心酸"): "与开篇同样的人，但光线更暗了——时间已经过去，有些东西永远回不来了",
        ("emotional", "温暖"): "与开篇同样的日常场景，但主角的态度变了——同样的路，不同的心情",
        ("suspense", "惊讶"): "回到开篇的场景，但观众带着新的信息重新看——一切都不一样了",
        ("suspense", "紧张"): "同样的选择瞬间再次出现，但这次主角的眼神不同了",
        ("slice_of_life", "治愈"): "同样的场景和动作，但阳光/色调/细节变了——微妙但确定地",
        ("social", "惊讶"): "与开篇同样的问题场景，但主角的状态从困扰变成了从容",
        ("social", "温暖"): "开篇的痛点场景变成了无关紧要的背景——因为已经解决了",
    }
    return contrasts.get((category, emotion), "同样的场景，但观众带着故事的信息重新看，一切都不同了")


def _page_turn_hook(category: str, _emotion: str) -> str:
    """Page Turn Suspense — the last panel of a right page must create a hook.

    Manga technique: 右页最后一格 = prime悬念位, 左页第一格 = prime揭示位.
    The reader MUST turn the page to know the answer.
    """
    hooks = {
        "comedy": "在笑到最高点时，画面突然定格——下页揭晓这是什么反应",
        "emotional": "主角做了一个意想不到的动作——下页揭晓结果",
        "suspense": "一个关键信息刚刚出现——下页揭晓这意味着什么",
        "slice_of_life": "日常中突然出现了一个不寻常的细节——下页揭晓",
        "social": "方案的效果即将揭晓——下页展示结果",
    }
    return hooks.get(category, "主角做了一个让观众必须翻页才能知道结果的动作——悬念定格")


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


def _twist_type_from_emotion(emotion: str) -> str:
    """Map an emotion to a likely twist type for pitch labeling."""
    mapping = {
        "惊讶": "反转倒置",
        "感动": "视角翻转",
        "好笑": "类型转换",
        "紧张": "代价升级",
        "温暖": "视角翻转",
        "心酸": "时间跳跃",
        "愤怒": "代价升级",
        "治愈": "视角翻转",
    }
    return mapping.get(emotion, "视角翻转")
