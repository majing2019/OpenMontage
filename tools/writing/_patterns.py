"""Story pattern library — 12 narrative patterns optimized for 60-second Douyin comics.

Each pattern defines a 5-beat structure with percentage-based timing
that scales to any target duration. Beats map to:
  HOOK → BUILD → CONFRONT → REVEAL → RESOLVE
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BeatTemplate:
    """One beat within a 5-beat story pattern."""

    name: str
    start_pct: float  # 0.0–1.0, multiplied by target_duration
    end_pct: float
    narrative_function: str
    visual_hint: str
    text_overlay_hint: str


@dataclass
class StoryPattern:
    """A reusable narrative structure for short-form comics."""

    name: str
    name_en: str
    description: str
    category: str  # emotional | comedy | suspense | slice_of_life | social
    douyin_tags: list[str] = field(default_factory=list)
    beats: list[BeatTemplate] = field(default_factory=list)
    suggested_emotions: list[str] = field(default_factory=list)
    difficulty: str = "beginner"  # beginner | intermediate | advanced
    sample_loglines: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 12 Patterns
# ---------------------------------------------------------------------------

PATTERNS: list[StoryPattern] = [
    # 1. 身份反转
    StoryPattern(
        name="身份反转",
        name_en="Identity Reversal",
        description="最后几帧揭示某人的真实身份，让观众重新理解前面的所有情节",
        category="comedy",
        douyin_tags=["#反转", "#身份", "#意想不到", "#结尾神转折"],
        suggested_emotions=["好笑", "惊讶", "温暖"],
        difficulty="intermediate",
        sample_loglines=[
            "一直以为是普通外卖小哥，最后发现是公司新来的CEO",
            "地铁上凶巴巴的大妈，到家后温柔地给流浪猫倒牛奶",
            "严厉的班主任深夜在朋友圈发emo文案",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "某人出现在一个不太合理的场景中", "一句引发好奇的陈述"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "展示这个人的日常行为，埋下微妙线索", "日常叙述，不露声色"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "某个事件让这个人的行为达到荒诞或极致", "加速叙述，矛盾升级"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "一个关键信息揭示此人真实身份", "让观众重新解读前面的画面"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "用一个反应镜头或细节定格", "留白，让观众自己笑"),
        ],
    ),
    # 2. 误会连环
    StoryPattern(
        name="误会连环",
        name_en="Misunderstanding Cascade",
        description="一个微小的错误判断引发连锁反应，越来越离谱",
        category="comedy",
        douyin_tags=["#误会", "#社死", "#搞笑", "#连环翻车"],
        suggested_emotions=["好笑", "紧张", "惊讶"],
        difficulty="beginner",
        sample_loglines=[
            "把老板的'先放着'理解成'不用做了'",
            "群聊里回错人，把吐槽发到了工作群",
            "以为女朋友说的'随便'是真的随便",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "一个看似正常但暗藏陷阱的对话/消息", "让观众感到'不对劲'"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "当事人按错误理解采取行动", "越努力越离谱"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "误会叠加误会，局面完全失控", "节奏加快，信息密度增大"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "真相大白，但为时已晚", "一方崩溃，另一方懵了"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "用尴尬的表情或沉默收场", "不解释，让尴尬说话"),
        ],
    ),
    # 3. 日常英雄
    StoryPattern(
        name="日常英雄",
        name_en="Everyday Hero",
        description="一个看似微不足道的举动，在特定语境下展现了非凡的勇气或善良",
        category="emotional",
        douyin_tags=["#感动", "#人间有爱", "#泪目", "#日常"],
        suggested_emotions=["感动", "温暖", "心酸"],
        difficulty="beginner",
        sample_loglines=[
            "暴雨中外卖员用自己的雨衣盖住陌生人的快递",
            "幼儿园小朋友把唯一的饼干掰一半给哭的同学",
            "加班到深夜的程序员帮保洁阿姨修好了拖把",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "一个困难或悲伤的场景开场", "先让情绪下沉"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "展示困境中的人和环境", "细节渲染，引发共情"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "某人不经意地做了一件小事", "不刻意，像呼吸一样自然"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "揭示这个小事对当事人意味着什么", "视角拉远，看到影响"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "英雄本人毫不知情地离开或继续生活", "不煽情，用背影或侧脸"),
        ],
    ),
    # 4. 时光对比
    StoryPattern(
        name="时光对比",
        name_en="Time Contrast",
        description="同一场景/人物在两个时间点的并列对比，展现变化和感慨",
        category="emotional",
        douyin_tags=["#回忆", "#时光", "#成长", "#泪目"],
        suggested_emotions=["心酸", "温暖", "感动"],
        difficulty="intermediate",
        sample_loglines=[
            "小时候爸爸背我走过的路，现在我扶着他走",
            "十年前的毕业照和今天的同学聚会",
            "奶奶年轻时做的菜和现在做同一道菜",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "现在的某个瞬间触发回忆", "一句话引出两个时空"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "回忆中的场景（更暖的色调，白色边框如拍立得）", "过去时的叙述"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "切回现在，同一场景已经变了", "对比的冲击力在于细节差异"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "发现某个东西没变——是那个人还在", "情感落点：物是人非中的人是"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "两个时空的同一个微笑或同一个动作", "不说话，让画面重叠"),
        ],
    ),
    # 5. 隐藏真相
    StoryPattern(
        name="隐藏真相",
        name_en="Hidden Truth",
        description="表面正常的生活场景下，隐藏着一个令人意外的真相",
        category="suspense",
        douyin_tags=["#悬疑", "#真相", "#反转", "#细思极恐"],
        suggested_emotions=["紧张", "惊讶", "心酸"],
        difficulty="advanced",
        sample_loglines=[
            "每天准时到公司的人，其实公司三个月前就倒闭了",
            "朋友圈里的完美生活，只有一个人能看到",
            "妈妈每天给儿子打电话，儿子三个月没接了",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "展示一个看似正常的日常场景", "让观众放松警惕"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "细节开始出现微妙的不对劲", "暗示但不揭示，让观众察觉到'哪里不对'"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "不协调感越来越强，但表面仍然正常", "观众开始猜测真相"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "用一个关键画面揭示真相", "让观众倒回去重新理解前面的画面"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "回到正常表象，但观众已经知道了", "用平静收场，比哭更有力"),
        ],
    ),
    # 6. 陌生人温暖
    StoryPattern(
        name="陌生人温暖",
        name_en="Stranger's Kindness",
        description="公共空间中陌生人之间短暂的温暖连接，不煽情但让人心里一动",
        category="emotional",
        douyin_tags=["#温暖", "#陌生人", "#感动", "#治愈"],
        suggested_emotions=["温暖", "治愈", "感动"],
        difficulty="beginner",
        sample_loglines=[
            "公交车上哭泣的女孩，旁边大妈默默递过来一颗糖",
            "雨天没伞，一个陌生人共享了半把伞",
            "深夜便利店，店员多说了一句'路上小心'",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "公共空间，某人独自处于低谷", "一句话交代情绪状态"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "周围人各自忙碌，没人注意到", "孤独感渲染"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "某个陌生人做了一个微小但精准的善意举动", "不说话，用一个动作"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "这个善意的意义远超举动本身", "当事人第一次抬头/第一次笑"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "两人各自离开，不再见面", "用背影，不回头"),
        ],
    ),
    # 7. 社死瞬间
    StoryPattern(
        name="社死瞬间",
        name_en="Social Death",
        description="极其尴尬的社交场景+一个意想不到的救赎反转",
        category="comedy",
        douyin_tags=["#社死", "#尴尬", "#搞笑", "#笑不活了"],
        suggested_emotions=["好笑", "紧张", "惊讶"],
        difficulty="beginner",
        sample_loglines=[
            "在全公司群里吐槽老板，手滑发到公司大群",
            "去面试发现面试官是前任",
            "在电梯里放了个屁，电梯停了，进来的是暗恋对象",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "一个看似正常的社交场景", "用'如果当时知道后面会发生什么'的心态"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "当事人状态放松，在正常社交", "越放松，后面的反转越痛"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "社死瞬间降临，所有人的反应", "密集的尴尬细节"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "反转：有人用幽默化解了尴尬，或者发现别人更尴尬", "从地狱到天堂"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "当事人苦笑或装作无事发生", "用表情收场，不解释"),
        ],
    ),
    # 8. 打工人小确幸
    StoryPattern(
        name="打工人小确幸",
        name_en="Worker's Small Joy",
        description="在压抑的工作日常中，一个小小的胜利带来巨大的快乐",
        category="slice_of_life",
        douyin_tags=["#打工人", "#日常", "#治愈", "#共鸣"],
        suggested_emotions=["治愈", "好笑", "温暖"],
        difficulty="beginner",
        sample_loglines=[
            "周五下午6:01准时关电脑的感觉",
            "被客户折磨一天后，吃到食堂最后一份红烧肉",
            "摸鱼时写的方案，结果被老板表扬了",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "展示工作场景的压抑或枯燥", "用细节：PPT、加班灯、冷外卖"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "打工人的一天（加速快进）", "用重复画面表达日常"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "某个微小的好事突然出现", "和前面的压抑形成强烈反差"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "这个小事带来的快乐远超预期", "用夸张表达快乐"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "回到日常，但心情已经不同了", "同样的办公室，但阳光不一样了"),
        ],
    ),
    # 9. 亲情反转
    StoryPattern(
        name="亲情反转",
        name_en="Family Twist",
        description="从子女角度看到的烦人父母行为，最后揭示父母行为背后的真正原因",
        category="emotional",
        douyin_tags=["#亲情", "#父母", "#感动", "#泪目", "#扎心"],
        suggested_emotions=["感动", "心酸", "温暖"],
        difficulty="intermediate",
        sample_loglines=[
            "嫌妈妈啰嗦，后来发现她是在练习怎么跟医生说话",
            "爸爸总说'我没事'，直到看到他的体检报告",
            "妈妈偷偷学的抖音语录，是为了跟孩子有共同话题",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "展示一个烦人的/不理解的父母行为", "从子女视角的吐槽语气"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "这个行为持续发生，子女越来越不耐烦", "展示不耐烦的细节"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "子女忍不住发火/说出伤人的话", "关键时刻：父母没有反驳"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "后来偶然发现父母行为背后的真正原因", "用一个小细节或物品揭示"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "子女想道歉但不知道怎么说", "用一个动作代替语言"),
        ],
    ),
    # 10. 如果当初
    StoryPattern(
        name="如果当初",
        name_en="What If Fork",
        description="从同一个决定点出发，展示两条截然不同的人生路径",
        category="emotional",
        douyin_tags=["#如果", "#选择", "#人生", "#感慨"],
        suggested_emotions=["心酸", "惊讶", "温暖"],
        difficulty="advanced",
        sample_loglines=[
            "如果当初没辞职，现在可能已经升主管了（但也不会遇到她）",
            "如果当初接了那个电话，就不会错过最后的告别",
            "如果当初选了理科，现在的人生会是怎样",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "一个人生的关键选择瞬间", "用'如果'开头"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "展示路径A（没有选择的那条路）的想象", "画面更亮，色调更暖"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "切回路径B（实际选择的路）的现实", "色调变冷，现实更粗粝"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "在路径B中发现了一个路径A永远不会有的东西", "关键：不是遗憾，是感悟"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "两个时空的人做出了同样的表情", "不评价哪个更好，让观众自己想"),
        ],
    ),
    # 11. 奇葩逻辑
    StoryPattern(
        name="奇葩逻辑",
        name_en="Absurd Logic",
        description="从一个荒谬的前提出发，用完全一本正经的态度推导出更荒谬的结论",
        category="comedy",
        douyin_tags=["#搞笑", "#脑洞", "#沙雕", "#奇葩"],
        suggested_emotions=["好笑", "惊讶"],
        difficulty="intermediate",
        sample_loglines=[
            "既然上班是为了赚钱，那不上班是不是就省了通勤费",
            "如果每个人都是一个宇宙，那宇宙是不是也在上班",
            "我妈说吃鱼聪明，那为什么鱼会被钓上来",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "一本正经地说出一个荒谬的前提", "表情严肃，画面正经"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "用正常的逻辑一步步推演", "每一步听起来都好像有道理"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "推演到越来越荒谬的结论", "周围人的表情从不解到崩溃"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "最后一击：结论荒谬到无法反驳", "用权威的语气说出最离谱的话"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "当事人完全没意识到问题，觉得自己很有道理", "用一个自信的表情收场"),
        ],
    ),
    # 12. 瞬间决定
    StoryPattern(
        name="瞬间决定",
        name_en="Split-Second Decision",
        description="一个瞬间的选择导致两种截然不同的结果，制造紧张感和反思",
        category="suspense",
        douyin_tags=["#选择", "#人生", "#悬念", "#深思"],
        suggested_emotions=["紧张", "惊讶", "心酸"],
        difficulty="advanced",
        sample_loglines=[
            "红灯前3秒，决定闯还是不闯",
            "看到有人落水，犹豫的那两秒",
            "辞职信写好了，手指在发送键上停住",
        ],
        beats=[
            BeatTemplate("钩子", 0.0, 0.08, "HOOK",
                          "一个需要立刻做决定的瞬间", "用特写：手指、眼神、倒计时"),
            BeatTemplate("铺垫", 0.08, 0.25, "BUILD",
                          "放慢时间，展示内心纠结", "画面分裂为两个选项"),
            BeatTemplate("冲突", 0.25, 0.58, "CONFRONT",
                          "做出选择的那一刻，一切加速", "动作快，画面节奏突然加快"),
            BeatTemplate("揭示", 0.58, 0.80, "REVEAL",
                          "展示选择的后果（或展示另一种可能）", "用一个关键画面定格后果"),
            BeatTemplate("收尾", 0.80, 1.0, "RESOLVE",
                          "回到那个瞬间，再看一眼另一个选项", "让观众思考：你会怎么选"),
        ],
    ),
]

# Quick lookup
PATTERN_BY_NAME: dict[str, StoryPattern] = {p.name: p for p in PATTERNS}

# Category groupings
PATTERNS_BY_CATEGORY: dict[str, list[StoryPattern]] = {}
for p in PATTERNS:
    PATTERNS_BY_CATEGORY.setdefault(p.category, []).append(p)

# Emotion → pattern mapping (which emotions pair well with which patterns)
EMOTION_PATTERN_MAP: dict[str, list[str]] = {
    "惊讶": ["身份反转", "隐藏真相", "奇葩逻辑", "瞬间决定"],
    "感动": ["日常英雄", "陌生人温暖", "亲情反转", "时光对比"],
    "好笑": ["误会连环", "社死瞬间", "打工人小确幸", "奇葩逻辑"],
    "紧张": ["隐藏真相", "瞬间决定", "误会连环", "社死瞬间"],
    "温暖": ["陌生人温暖", "日常英雄", "亲情反转", "打工人小确幸"],
    "心酸": ["时光对比", "亲情反转", "如果当初", "隐藏真相"],
    "愤怒": ["隐藏真相", "瞬间决定", "身份反转"],
    "治愈": ["打工人小确幸", "陌生人温暖", "日常英雄", "时光对比"],
}
