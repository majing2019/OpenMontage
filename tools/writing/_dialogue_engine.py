"""Dialogue template engine with subtext awareness for short-form comics.

Sources:
- McKee "Story" — Subtext Over Text principle
- Vorhaus "The Comic Toolbox" — Comic dialogue patterns
- Ge Fei "爆款短剧创作" — 15-character mobile limit
- O'Neil/Kneece "Comic Script Writing" — Bubble space constraints
- Eisner "Comics & Sequential Art" — Text as visual element

Zero external dependencies — pure local template matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Mobile constraints (from Ge Fei / 《爆款短剧创作》)
# ---------------------------------------------------------------------------

MAX_LINE_CHARS = 15       # 手机屏每行最多15个汉字
MAX_BUBBLES_PER_PANEL = 3  # 每格最多3个对话气泡
MAX_WORDS_PER_BUBBLE = 25  # 每个气泡最多25个英文词/等量中文


@dataclass
class DialogueLine:
    """One line of subtext-aware dialogue."""

    character: str
    surface_text: str          # 角色说出口的话
    subtext_meaning: str       # 实际含义
    emotion: str               # 情绪标签
    tone: str                  # 语气描述
    mobile_optimized: bool     # 是否≤15字
    delivery_hint: str = ""    # 表演提示（动作/表情/停顿）


# ---------------------------------------------------------------------------
# Subtext rules (from McKee "Subtext Over Text")
# ---------------------------------------------------------------------------

SUBTEXT_RULES: list[dict[str, str]] = [
    {
        "rule": "不要说出情绪名称",
        "bad": "我很生气",
        "good": "（沉默，把杯子重重放下）",
        "why": "直接说出情绪=没有潜台词，观众失去解读乐趣",
    },
    {
        "rule": "用动作替代情感表达",
        "bad": "我很想你",
        "good": "这是第三次路过你喜欢的面包店了",
        "why": "具体的动作比抽象的情感更有画面感和说服力",
    },
    {
        "rule": "说反话表达真实情感",
        "bad": "我很难过",
        "good": "没事，挺好的",
        "why": "反话让对话有层次——表面说的和心里想的不一样才有戏剧性",
    },
    {
        "rule": "转移话题=情感逃避",
        "bad": "我不想谈这个",
        "good": "对了，你吃饭了吗？",
        "why": "用看似无关的话题转移注意力，比直接拒绝更有信息量",
    },
    {
        "rule": "用问句隐藏判断",
        "bad": "你这样做不对",
        "good": "你确定要这样？",
        "why": "问句比陈述句更柔和，但潜台词是明确的否定",
    },
    {
        "rule": "重复=情感强调",
        "bad": "我真的很想你",
        "good": "（重复对方的话）'你回来了？'……'你真的回来了？'",
        "why": "重复对方的话表示这句话超出了预期——强化了情感冲击",
    },
    {
        "rule": "沉默=最有力的台词",
        "bad": "我不知道该说什么",
        "good": "（长久沉默后）……走吧",
        "why": "沉默让观众自己填补空白——往往比任何台词都有力量",
    },
    {
        "rule": "用具体代替抽象",
        "bad": "我过得很糟糕",
        "good": "泡面已经连吃第四天了",
        "why": "具体的细节触发画面感，抽象的形容词不会",
    },
]


# ---------------------------------------------------------------------------
# Therefore/But connection test (from Akers "Your Screenplay Sucks!")
# ---------------------------------------------------------------------------

CONNECTION_TESTS: list[dict[str, str]] = [
    {
        "rule": "Therefore/But 连接测试",
        "description": "场景之间的连接必须是 '因此' 或 '但是'，绝不能是 '然后'",
        "bad": "场景A发生了。然后场景B发生了。",
        "good": "场景A发生了，因此场景B不得不发生。/场景A发生了，但是场景B出人意料。",
        "why": "因果连接产生叙事动力，'然后'只是时间流逝",
    },
    {
        "rule": "每场景必须有价值变化",
        "description": "每个场景结束时，角色的情感状态必须和开始时不同",
        "test": "场景开始时角色是X状态，结束时是否变成了非X？",
        "why": "没有变化的场景=没有戏剧性=可以被删除",
    },
]


# ---------------------------------------------------------------------------
# Dialogue templates per character × emotion
# ---------------------------------------------------------------------------

DIALOGUE_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "妈妈": [
        {
            "emotion": "操心",
            "lines": ["记得吃饭", "多穿点衣服", "别熬夜", "给你寄了东西"],
            "subtext": "我想确认你还是需要我的",
            "tone": "唠叨但温暖",
            "delivery_hint": "一边做家务一边随口说，假装不经意",
        },
        {
            "emotion": "生气",
            "lines": ["我不管你了", "随便你", "你爱怎样怎样"],
            "subtext": "我很受伤，希望你来哄我",
            "tone": "冷淡中带委屈",
            "delivery_hint": "转身背对，肩膀微微僵硬",
        },
        {
            "emotion": "心疼",
            "lines": ["怎么瘦了", "是不是没好好吃饭", "别太累了"],
            "subtext": "我很想照顾你但不知道怎么做才对",
            "tone": "小心翼翼的温柔",
            "delivery_hint": "伸手想摸对方的脸，但又缩回去",
        },
        {
            "emotion": "释然",
            "lines": ["行了行了", "别弄了，去吧", "我没事"],
            "subtext": "我终于学会放手了——虽然心里还在疼",
            "tone": "假装轻松实则在忍",
            "delivery_hint": "摆摆手，笑容有点勉强，但眼睛是温柔的",
        },
        {
            "emotion": "唠叨",
            "lines": ["跟你说了多少遍了", "你怎么就不听呢", "总是这样"],
            "subtext": "我害怕失去对你的影响力",
            "tone": "急切但充满关切",
            "delivery_hint": "一边整理东西一边不停地说，语速越来越快",
        },
    ],
    "爸爸": [
        {
            "emotion": "沉默的爱",
            "lines": ["嗯", "知道了", "去吧", "……"],
            "subtext": "我不知道怎么说，但我在乎",
            "tone": "简短但沉重",
            "delivery_hint": "没有看对方，继续做自己的事，但手上的动作停了一瞬",
        },
        {
            "emotion": "隐忍",
            "lines": ["没事", "不累", "还撑得住"],
            "subtext": "我不能让你担心——这是我能做的全部了",
            "tone": "平静中带着倔强",
            "delivery_hint": "微微点头，嘴角向下压了一下，然后转身",
        },
        {
            "emotion": "骄傲",
            "lines": ["不错", "可以", "挺好"],
            "subtext": "我为你骄傲，但我说不出更温柔的话",
            "tone": "克制但眼底有光",
            "delivery_hint": "轻轻拍了一下肩膀，这是他能给的最高赞许",
        },
        {
            "emotion": "脆弱",
            "lines": ["……你妈呢", "饭做好了吗", "今天冷不冷"],
            "subtext": "我需要有人陪——但我不知道怎么开口",
            "tone": "假装日常实则寻找连接",
            "delivery_hint": "难得主动打电话，声音比平时轻",
        },
    ],
    "打工人": [
        {
            "emotion": "崩溃边缘",
            "lines": ["没事都行", "都行都行", "无所谓了"],
            "subtext": "我已经没有精力做任何选择了",
            "tone": "疲惫到麻木",
            "delivery_hint": "盯着手机屏幕，眼神空洞，声音没有起伏",
        },
        {
            "emotion": "自我怀疑",
            "lines": ["这样值得吗", "我真的可以吗", "也许我不行"],
            "subtext": "我开始怀疑坚持的意义了",
            "tone": "脆弱的坦诚",
            "delivery_hint": "深夜独处时突然说出，说完自己愣了一下",
        },
        {
            "emotion": "假装积极",
            "lines": ["冲冲冲", "加油", "没事的会好的"],
            "subtext": "我不说'加油'就真的撑不住了",
            "tone": "用力过猛的乐观",
            "delivery_hint": "表情夸张，但眼神疲惫——在给自己打气",
        },
        {
            "emotion": "小确幸",
            "lines": ["今天不错", "终于吃上了一顿好的", "难得准时下班"],
            "subtext": "我的快乐标准已经降得这么低了",
            "tone": "苦中作乐",
            "delivery_hint": "小小的笑容，带着一丝自嘲",
        },
    ],
    "孩子": [
        {
            "emotion": "天真",
            "lines": ["为什么大人要上班", "老师说的不对", "我长大不要这样"],
            "subtext": "孩子没有潜台词——他们的直接本身就是对成人世界的映照",
            "tone": "认真而纯粹",
            "delivery_hint": "睁大眼睛，歪着头，完全不在意大人的反应",
        },
        {
            "emotion": "直击",
            "lines": ["你是不是不开心", "你们为什么不笑了", "奶奶去哪了"],
            "subtext": "孩子能感知到大人否认的东西",
            "tone": "天真但准确到让人心碎",
            "delivery_hint": "没有任何修饰，就是最简单的问句",
        },
    ],
    "老板": [
        {
            "emotion": "严厉",
            "lines": ["重新做", "这不行", "我再说一遍"],
            "subtext": "我要求高标准是因为我在乎这个团队",
            "tone": "冰冷却有底线",
            "delivery_hint": "不看对方，指着文件说话——但语气里没有恶意",
        },
        {
            "emotion": "认可",
            "lines": ["可以", "不错", "就这样"],
            "subtext": "这就是我能给的最高评价了",
            "tone": "克制但明确",
            "delivery_hint": "微微点头，嘴角有一丝几乎看不出的上扬",
        },
        {
            "emotion": "背后关怀",
            "lines": ["（对其他人说）给他安排一下", "别让他加班了", "注意身体"],
            "subtext": "我不当面说因为那不是我的风格——但我会用行动",
            "tone": "表面公事公办实则在保护",
            "delivery_hint": "等对方不在场时才说，语气和面对员工时完全不同",
        },
    ],
    "老人": [
        {
            "emotion": "看透",
            "lines": ["年轻人，慢慢来", "不急", "日子长着呢"],
            "subtext": "我已经走完了你们正在走的路——你们会没事的",
            "tone": "平静中带着过来人的温度",
            "delivery_hint": "微笑，眼神像在看很远的地方",
        },
        {
            "emotion": "倔强",
            "lines": ["不用扶我", "我自己能行", "还没老到那份上"],
            "subtext": "我害怕失去最后一点独立——请尊重我的挣扎",
            "tone": "固执但脆弱",
            "delivery_hint": "推开伸过来的手，站起来的动作明显用了全力",
        },
        {
            "emotion": "怀念",
            "lines": ["以前啊……", "那时候不一样", "你还小不懂"],
            "subtext": "我在回忆中重新见到那些已经不在的人",
            "tone": "温柔但带着潮湿",
            "delivery_hint": "目光变得遥远，声音突然轻了很多",
        },
    ],
    "外卖小哥": [
        {
            "emotion": "赶时间",
            "lines": ["快到了", "马上到", "稍等一下"],
            "subtext": "每多一分钟都是钱和差评的风险",
            "tone": "急促但尽力礼貌",
            "delivery_hint": "一边打电话一边跑，声音在喘",
        },
        {
            "emotion": "日常温柔",
            "lines": ["路上小心", "今天的汤不错", "慢慢吃别急"],
            "subtext": "我在这个城市的唯一连接就是送东西给你们的这几分钟",
            "tone": "朴素的善意",
            "delivery_hint": "递东西时多停了一秒，带着一点不好意思的笑",
        },
    ],
    "闺蜜/兄弟": [
        {
            "emotion": "毒舌关心",
            "lines": ["你是不是傻", "我就知道你会这样", "说了你又不听"],
            "subtext": "我真的很担心你——但直接说太肉麻了",
            "tone": "嫌弃的外壳，柔软的内核",
            "delivery_hint": "翻白眼，但手已经伸过来帮忙了",
        },
        {
            "emotion": "认真时刻",
            "lines": ["我在呢", "有事说话", "别一个人扛"],
            "subtext": "放下所有玩笑——这个时刻我说的是真的",
            "tone": "突然的安静和认真",
            "delivery_hint": "收起笑容，看着对方的眼睛——和平时完全不同",
        },
    ],
    "奶奶/外婆": [
        {
            "emotion": "慈祥",
            "lines": ["来，吃这个", "奶奶给你留着呢", "饿了吧"],
            "subtext": "给你食物是我唯一还能做的事了",
            "tone": "温暖但带着一丝寂寞",
            "delivery_hint": "从围裙口袋里掏出特意留的食物，眼睛亮了起来",
        },
        {
            "emotion": "倔强",
            "lines": ["不用管我", "我自己能行", "走你的去吧"],
            "subtext": "别把我当老人看——我还有用",
            "tone": "固执但眼底有期待",
            "delivery_hint": "摆手但偷偷看对方有没有真的走",
        },
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_dialogue(character: str, emotion: str) -> list[DialogueLine]:
    """Get subtext-aware dialogue lines for a character in a given emotion."""
    templates = DIALOGUE_TEMPLATES.get(character, [])
    matching = [t for t in templates if t["emotion"] == emotion]
    if not matching:
        return []

    lines = []
    for tmpl in matching:
        for text in tmpl.get("lines", []):
            lines.append(DialogueLine(
                character=character,
                surface_text=str(text),
                subtext_meaning=str(tmpl.get("subtext", "")),
                emotion=emotion,
                tone=str(tmpl.get("tone", "")),
                mobile_optimized=len(str(text)) <= MAX_LINE_CHARS,
                delivery_hint=str(tmpl.get("delivery_hint", "")),
            ))
    return lines


def check_mobile_limit(text: str) -> bool:
    """Check if a dialogue line fits mobile screen constraints."""
    return len(text) <= MAX_LINE_CHARS


def truncate_for_mobile(text: str) -> str:
    """Truncate a dialogue line to fit mobile screen if needed."""
    if len(text) <= MAX_LINE_CHARS:
        return text
    return text[: MAX_LINE_CHARS - 1] + "…"


def validate_panel_dialogue(bubbles: list[str]) -> list[str]:
    """Validate a panel's dialogue against mobile constraints.

    Returns list of warnings if any constraint is violated.
    """
    warnings = []
    if len(bubbles) > MAX_BUBBLES_PER_PANEL:
        warnings.append(f"Too many bubbles: {len(bubbles)} > {MAX_BUBBLES_PER_PANEL}")
    for i, bubble in enumerate(bubbles):
        if len(bubble) > MAX_LINE_CHARS:
            warnings.append(
                f"Bubble {i+1} too long: {len(bubble)} chars > {MAX_LINE_CHARS} max"
            )
    return warnings
