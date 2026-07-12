"""Story pattern library — 12 narrative patterns optimized for 60-second Douyin comics.

Each pattern defines a 5-beat structure with percentage-based timing
that scales to any target duration. Beats map to:
  HOOK → BUILD → CONFRONT → REVEAL → RESOLVE
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BeatTemplate:
    """One beat within a story pattern (supports variable beat counts)."""

    name: str
    start_pct: float  # 0.0–1.0, multiplied by target_duration
    end_pct: float
    narrative_function: str
    visual_hint: str
    text_overlay_hint: str
    conflict_level: str = "surface"  # surface | middle | deep
    conflict_intensity: float = 1.0  # 0.0–1.0, escalation within beat


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
    "惊讶": ["身份反转", "隐藏真相", "奇葩逻辑", "瞬间决定", "五幕对称", "英雄之旅"],
    "感动": ["日常英雄", "陌生人温暖", "亲情反转", "时光对比", "救猫咪节拍", "英雄之旅", "扁平到立体"],
    "好笑": ["误会连环", "社死瞬间", "打工人小确幸", "奇葩逻辑", "喜剧升级"],
    "紧张": ["隐藏真相", "瞬间决定", "误会连环", "社死瞬间", "五幕对称", "问题解决"],
    "温暖": ["陌生人温暖", "日常英雄", "亲情反转", "打工人小确幸", "救猫咪节拍", "扁平到立体"],
    "心酸": ["时光对比", "亲情反转", "如果当初", "隐藏真相", "救猫咪节拍", "英雄之旅"],
    "愤怒": ["隐藏真相", "瞬间决定", "身份反转", "五幕对称", "问题解决"],
    "治愈": ["打工人小确幸", "陌生人温暖", "日常英雄", "时光对比", "扁平到立体", "英雄之旅"],
}


# ---------------------------------------------------------------------------
# Additional Patterns (from professional storytelling frameworks)
# ---------------------------------------------------------------------------

# 13. 救猫咪节拍 — Save the Cat 15-Beat (Blake Snyder)
PATTERNS.append(StoryPattern(
    name="救猫咪节拍",
    name_en="Save the Cat Beat Sheet",
    description="Blake Snyder精确节拍表，从开篇画面到最终画面，11拍精确覆盖完整情感弧线",
    category="emotional",
    douyin_tags=["#情感", "#成长", "#治愈", "#泪目"],
    suggested_emotions=["感动", "温暖", "心酸", "治愈"],
    difficulty="advanced",
    sample_loglines=[
        "一个从不照顾人的男人，在意外中学会了为别人着想",
        "被所有人看不起的小角色，在关键时刻做出了改变所有人命运的选择",
        "固执的老人终于接受了年轻人的帮助，找到了新的生活",
    ],
    beats=[
        BeatTemplate("开篇画面", 0.0, 0.06, "HOOK",
                      "展示主角当前状态的视觉画面——'之前的生活'", "让观众看到主角的起点状态"),
        BeatTemplate("主题陈述", 0.06, 0.11, "BUILD",
                      "某人说出一句话，暗示故事的核心问题——主角还听不懂", "种子已埋下，观众开始期待"),
        BeatTemplate("铺垫", 0.11, 0.20, "BUILD",
                      "展示主角的日常生活、不足和困境", "让观众理解'为什么需要改变'"),
        BeatTemplate("催化剂", 0.20, 0.28, "CONFRONT",
                      "一个打破日常的事件发生，故事真正开始", "不可能再回到从前了"),
        BeatTemplate("犹豫", 0.28, 0.36, "CONFRONT",
                      "主角犹豫是否接受挑战，展示恐惧和顾虑", "内心的挣扎让观众更有代入感"),
        BeatTemplate("乐趣与游戏", 0.36, 0.50, "CONFRONT",
                      "主角尝试新事物，展现概念的核心魅力", "预告片里的精彩片段在这里",
                      conflict_level="surface"),
        BeatTemplate("中点", 0.50, 0.60, "REVEAL",
                      "伪胜利或伪失败——主角或观众重新定义目标", "故事从这里转折，方向变了",
                      conflict_level="middle", conflict_intensity=0.6),
        BeatTemplate("困境加深", 0.60, 0.72, "CONFRONT",
                      "外部压力增大，内部支持系统瓦解", "孤立无援，最黑暗之前",
                      conflict_level="middle", conflict_intensity=0.8),
        BeatTemplate("绝望时刻", 0.72, 0.82, "CONFRONT",
                      "看似一切都完了，'死亡的气息'", "到达情感最低点",
                      conflict_level="deep", conflict_intensity=0.95),
        BeatTemplate("黑夜灵魂", 0.82, 0.90, "REVEAL",
                      "在绝望中找到新的力量或顿悟", "真正的成长时刻——主角开始改变",
                      conflict_level="deep", conflict_intensity=0.7),
        BeatTemplate("结局", 0.90, 1.0, "RESOLVE",
                      "用新学到的东西解决问题，证明变化", "展示新的平衡，与开篇画面形成对比",
                      conflict_level="deep", conflict_intensity=0.3),
    ],
))

# 14. 英雄之旅 — Hero's Journey 12 Stages (Vogler/Campbell)
PATTERNS.append(StoryPattern(
    name="英雄之旅",
    name_en="Hero's Journey",
    description="坎贝尔神话结构，从平凡世界出发，经历试炼，获得顿悟，带着礼物回归",
    category="emotional",
    douyin_tags=["#成长", "#挑战", "#勇气", "#感动"],
    suggested_emotions=["感动", "惊讶", "温暖", "心酸"],
    difficulty="advanced",
    sample_loglines=[
        "一个普通人被迫面对自己最害怕的事，最后发现勇气就在恐惧背后",
        "孩子在寻找走失宠物的路上，学会了独立和责任",
        "加班到崩溃的打工人，在帮陌生人修车时找回了生活的意义",
    ],
    beats=[
        BeatTemplate("平凡世界", 0.0, 0.08, "HOOK",
                      "展示主角的日常状态——有缺陷但不自知", "让观众看到'改变的必要性'"),
        BeatTemplate("召唤", 0.08, 0.18, "BUILD",
                      "一个事件或消息迫使主角面对未知", "内心在抗拒，但外在在推动"),
        BeatTemplate("跨越门槛", 0.18, 0.30, "CONFRONT",
                      "主角迈出关键一步，进入'不归路'", "没有回头路了——故事正式展开",
                      conflict_level="surface", conflict_intensity=0.3),
        BeatTemplate("试炼与盟友", 0.30, 0.50, "CONFRONT",
                      "遇到困难，结识帮手（或发现意想不到的盟友）", "在挑战中成长，建立关系",
                      conflict_level="surface", conflict_intensity=0.5),
        BeatTemplate("深渊试炼", 0.50, 0.68, "REVEAL",
                      "最大的考验——面对内心最深处的恐惧", "主角必须'死亡'才能重生",
                      conflict_level="deep", conflict_intensity=1.0),
        BeatTemplate("获得奖赏", 0.68, 0.78, "REVEAL",
                      "从试炼中获得新的认知、能力或关系", "主角已经和出发时不同了",
                      conflict_level="middle", conflict_intensity=0.4),
        BeatTemplate("回归之路", 0.78, 0.88, "CONFRONT",
                      "带着改变回到日常世界，但还有最后的考验", "改变必须被证明是真实的",
                      conflict_level="middle", conflict_intensity=0.6),
        BeatTemplate("复活", 0.88, 0.94, "REVEAL",
                      "用新学到的东西通过最后的考验", "证明成长——旧的我已经死了",
                      conflict_level="deep", conflict_intensity=0.8),
        BeatTemplate("带回礼物", 0.94, 1.0, "RESOLVE",
                      "主角给社区/关系带来了改变", "世界因为这段旅程变得不同了",
                      conflict_level="deep", conflict_intensity=0.1),
    ],
))

# 15. 五幕对称 — Five-Act Symmetry (John Yorke)
PATTERNS.append(StoryPattern(
    name="五幕对称",
    name_en="Five-Act Symmetry",
    description="故事围绕中点的揭示对称展开，前半收敛到真相，后半从真相展开",
    category="suspense",
    douyin_tags=["#悬疑", "#反转", "#结构", "#深度"],
    suggested_emotions=["惊讶", "紧张", "心酸", "愤怒"],
    difficulty="advanced",
    sample_loglines=[
        "前半段你以为在追查别人，中点揭示——其实一直在追查自己",
        "看似是两个独立的故事线，中点揭示它们是同一件事的两面",
        "前半段主角在逃避，中点揭示逃避的原因，后半段转为面对",
    ],
    beats=[
        BeatTemplate("建立", 0.0, 0.10, "HOOK",
                      "展示表面正常的世界——但有一个微妙的裂缝", "裂缝是通向真相的入口"),
        BeatTemplate("探索", 0.10, 0.25, "BUILD",
                      "主角试图用旧方法应对新情况", "旧方法的局限开始暴露"),
        BeatTemplate("中点揭示", 0.25, 0.50, "REVEAL",
                      "故事的核心——主角瞥见真相，方向完全改变", "前面的所有情节被重新赋予意义",
                      conflict_level="deep", conflict_intensity=1.0),
        BeatTemplate("复杂化", 0.50, 0.75, "CONFRONT",
                      "真相带来更大的困难——知道真相反而更痛苦", "旧自我和新自我在激烈冲突",
                      conflict_level="deep", conflict_intensity=0.85),
        BeatTemplate("解决", 0.75, 1.0, "RESOLVE",
                      "主角做出最终选择，证明变化", "回到开篇的场景，但一切都不同了",
                      conflict_level="deep", conflict_intensity=0.2),
    ],
))

# 16. 扁平到立体 — Organic Character Arc (John Truby)
PATTERNS.append(StoryPattern(
    name="扁平到立体",
    name_en="Flat to Round",
    description="主角从单一维度开始，通过冲突和选择逐渐获得深度，最后变成一个立体的人",
    category="slice_of_life",
    douyin_tags=["#成长", "#人物", "#深度", "#共鸣"],
    suggested_emotions=["温暖", "治愈", "感动", "惊讶"],
    difficulty="intermediate",
    sample_loglines=[
        "一个只在乎业绩的销售，因为一个客户的故事学会了真正的倾听",
        "表面坚强的打工人，在一个深夜的加班中承认了自己的脆弱",
        "一直用笑面具掩饰的人，终于在一个陌生人面前卸下了伪装",
    ],
    beats=[
        BeatTemplate("表面展示", 0.0, 0.10, "HOOK",
                      "展示主角的表面人设——看起来很好但缺少什么", "观众隐约感到'这个人不太对'"),
        BeatTemplate("裂缝出现", 0.10, 0.25, "BUILD",
                      "一个小事件让主角的表面开始出现裂缝", "不是崩溃，是细微的不对劲",
                      conflict_level="surface"),
        BeatTemplate("被迫面对", 0.25, 0.55, "CONFRONT",
                      "无法再用旧方式应对，必须做出真实的选择", "选择不是非黑即白——是灰色的",
                      conflict_level="middle", conflict_intensity=0.7),
        BeatTemplate("自我揭示", 0.55, 0.78, "REVEAL",
                      "主角认识到自己的真实需求和缺陷", "不是被别人告诉的——是自己发现的",
                      conflict_level="deep", conflict_intensity=0.9),
        BeatTemplate("新平衡", 0.78, 1.0, "RESOLVE",
                      "用新认知做出的行动——不完美但真实", "世界没有变好，但主角变立体了",
                      conflict_level="deep", conflict_intensity=0.2),
    ],
))

# 17. 问题解决 — Problem-Solution (AIDA)
PATTERNS.append(StoryPattern(
    name="问题解决",
    name_en="Problem-Solution",
    description="展示痛点→引出方案→证明有效→促成行动，适用于产品/知识类内容",
    category="social",
    douyin_tags=["#干货", "#解决问题", "#实用", "#方法"],
    suggested_emotions=["惊讶", "温暖", "治愈"],
    difficulty="beginner",
    sample_loglines=[
        "你以为的头疼是因为没睡好，其实是颈椎出了问题——三个动作解决",
        "每次开会都说不到点子上？一个模板让你的发言有逻辑、有说服力",
        "为什么你总是存不下钱？不是因为收入低，而是踩了三个隐形坑",
    ],
    beats=[
        BeatTemplate("痛点冲击", 0.0, 0.10, "HOOK",
                      "直击观众的具体痛点——让观众点头'对对对就是我'", "用具体场景，不要抽象概念"),
        BeatTemplate("问题放大", 0.10, 0.22, "BUILD",
                      "展示这个问题的普遍性和严重性", "让观众意识到'这必须解决'",
                      conflict_level="surface"),
        BeatTemplate("方案登场", 0.22, 0.45, "CONFRONT",
                      "提出解决方案——简洁、具体、可执行", "观众的期待在这里得到满足",
                      conflict_level="middle", conflict_intensity=0.3),
        BeatTemplate("效果证明", 0.45, 0.70, "REVEAL",
                      "展示使用方案后的变化——前后对比", "用具体的数字或画面证明",
                      conflict_level="middle", conflict_intensity=0.5),
        BeatTemplate("行动号召", 0.70, 1.0, "RESOLVE",
                      "总结要点，引导行动——收藏/尝试/分享", "最后一句话让人想保存这个视频",
                      conflict_level="surface", conflict_intensity=0.1),
    ],
))

# 18. 喜剧升级 — Comic Escalation (Vorhaus)
PATTERNS.append(StoryPattern(
    name="喜剧升级",
    name_en="Comic Escalation",
    description="用Fish Out of Water+Rule of Three+不断升级的荒诞，制造持续笑声",
    category="comedy",
    douyin_tags=["#搞笑", "#升级", "#笑不活了", "#沙雕"],
    suggested_emotions=["好笑", "惊讶"],
    difficulty="intermediate",
    sample_loglines=[
        "第一天上班穿错制服，第二天叫错老板名字，第三天不小心删了整个数据库",
        "为了不早起发明了五个闹钟方案，结果每天被六个闹钟同时吵醒",
        "健身第一天练了三分钟，发了三十分钟朋友圈，被三个教练同时私信",
    ],
    beats=[
        BeatTemplate("反常登场", 0.0, 0.10, "HOOK",
                      "角色出现在不属于他的环境中——格格不入", "观众立刻感觉到'要出事了'"),
        BeatTemplate("第一次翻车", 0.10, 0.25, "BUILD",
                      "第一次尝试以意料之外的方式失败", "建立模式——观众开始期待更多",
                      conflict_level="surface", conflict_intensity=0.3),
        BeatTemplate("第二次翻车", 0.25, 0.45, "CONFRONT",
                      "第二次尝试，更努力，失败得更荒诞", "确认模式——Rule of Three的第二步",
                      conflict_level="surface", conflict_intensity=0.6),
        BeatTemplate("第三次升级", 0.45, 0.70, "REVEAL",
                      "第三次尝试——结果完全超出所有人预期", "Rule of Three的打破——最高潮",
                      conflict_level="middle", conflict_intensity=0.95),
        BeatTemplate("苦笑收场", 0.70, 1.0, "RESOLVE",
                      "当事人接受了荒诞的现实，用苦笑或沉默收场", "喜剧的余味——不解释，让观众回味",
                      conflict_level="surface", conflict_intensity=0.1),
    ],
))

# Rebuild lookups after adding new patterns
PATTERN_BY_NAME = {p.name: p for p in PATTERNS}
PATTERNS_BY_CATEGORY: dict[str, list[StoryPattern]] = {}
for p in PATTERNS:
    PATTERNS_BY_CATEGORY.setdefault(p.category, []).append(p)


# ---------------------------------------------------------------------------
# Hook Type Library (from 《爆款短剧创作》+ 《商业短片广告创作》)
# ---------------------------------------------------------------------------

HOOK_TYPES: list[dict[str, str]] = [
    {
        "type": "冲突进行中",
        "name_en": "Conflict in Progress",
        "description": "从矛盾已经发生的时刻开始，不铺垫背景",
        "template": "动作已经开始：{动作描述}，但{障碍出现}",
        "example": "妈妈已经进了同学群——正在发第一条消息",
        "timing_rule": "冲突必须在0-3秒内可见",
    },
    {
        "type": "结果预览",
        "name_en": "Result Preview",
        "description": "先展示高潮画面，然后倒叙",
        "template": "结局是这样的：{高潮画面}。但一切始于{起点}",
        "example": "最后妈妈退出了同学群——但这之前发生了什么",
        "timing_rule": "高潮画面必须在前2秒出现",
    },
    {
        "type": "极端对比",
        "name_en": "Extreme Contrast",
        "description": "并置两个截然相反的元素",
        "template": "一边{场景A}，一边{场景B}——它们不可能同时存在，但确实在",
        "example": "一边是温馨的家庭晚餐，一边是手机屏幕上妈妈发在同学群的消息",
        "timing_rule": "对比元素必须在1秒内同时出现",
    },
    {
        "type": "强力台词",
        "name_en": "Power Line",
        "description": "以一句令人难忘的台词开场",
        "template": "他说：{金句}",
        "example": "「我这辈子做过的最勇敢的事，就是承认我怕黑」",
        "timing_rule": "第1秒出文字",
    },
    {
        "type": "视觉冲击",
        "name_en": "Visual Shock",
        "description": "不解释，用画面直接震撼",
        "template": "{令人震撼的画面描述}",
        "example": "一个穿着外卖服的人在米其林餐厅里做菜",
        "timing_rule": "第1帧就是冲击画面",
    },
    {
        "type": "悬念提问",
        "name_en": "Suspense Question",
        "description": "提出观众必须知道答案的问题",
        "template": "为什么{不合理现象}？",
        "example": "为什么公司每天最晚走的人，其实是第一个到的？",
        "timing_rule": "前2秒提出问题",
    },
    {
        "type": "身份锚定",
        "name_en": "Identity Anchor",
        "description": "确立角色标签，让观众立即定位",
        "template": "{标签}。{反常行为}",
        "example": "外卖员。正在给客户写英文感谢卡",
        "timing_rule": "1秒内建立标签",
    },
    {
        "type": "情感触发",
        "name_en": "Emotional Trigger",
        "description": "直接触发特定情绪的细节",
        "template": "{触景生情的具体细节}",
        "example": "凌晨三点，手机亮了。不是闹钟，是妈妈的消息：'你睡了吗？'",
        "timing_rule": "前3秒情感到位",
    },
]


# ---------------------------------------------------------------------------
# Conflict Design Templates (from 叶茂中《冲突》+ Egri + McKee)
# ---------------------------------------------------------------------------

CONFLICT_TEMPLATES: list[dict[str, object]] = [
    {
        "name": "代际冲突",
        "surface": "两代人对同一件事有不同做法",
        "middle": "互相觉得对方不理解自己",
        "deep": "两种无法共存的生活哲学和价值体系",
        "escalation_beats": ["分歧出现", "双方坚持", "矛盾激化", "爆发冲突", "意外和解/顿悟"],
    },
    {
        "name": "职场冲突",
        "surface": "工作上的任务分歧或利益冲突",
        "middle": "能力被质疑，付出不被认可",
        "deep": "个人价值感和职业身份认同的危机",
        "escalation_beats": ["任务分歧", "暗中较劲", "公开对峙", "面临选择", "意外转机"],
    },
    {
        "name": "情感冲突",
        "surface": "两个人之间的误解或分歧",
        "middle": "各自有自己的委屈和难处",
        "deep": "对爱的不同理解——是放手还是抓紧",
        "escalation_beats": ["小事摩擦", "冷战升级", "积怨爆发", "差点失去", "重新理解"],
    },
    {
        "name": "自我冲突",
        "surface": "想做一件事但外在条件不允许",
        "middle": "内心的恐惧和外在的期待在拉扯",
        "deep": "我是谁 vs 别人希望我是谁",
        "escalation_beats": ["意识到问题", "尝试改变", "遇到挫折", "放弃边缘", "突破自我"],
    },
    {
        "name": "社交冲突",
        "surface": "在社交场合中的尴尬或面子问题",
        "middle": "在别人眼中的形象 vs 真实的自己",
        "deep": "被认可的渴望 vs 做真实自己的勇气",
        "escalation_beats": ["社交场合", "尴尬发生", "试图挽回", "更加尴尬", "意外解围"],
    },
    {
        "name": "生存冲突",
        "surface": "资源匮乏或环境恶劣的直接威胁",
        "middle": "在压力下暴露出人性的一面",
        "deep": "活着就够了 vs 活得有尊严",
        "escalation_beats": ["困境降临", "资源告急", "道德选择", "至暗时刻", "转机出现"],
    },
    {
        "name": "梦想冲突",
        "surface": "想追求梦想但现实不允许",
        "middle": "周围人的不理解甚至嘲笑",
        "deep": "妥协的安全 vs 未知的自由",
        "escalation_beats": ["梦想萌发", "现实打击", "坚持或放弃", "关键时刻", "做出选择"],
    },
    {
        "name": "规则冲突",
        "surface": "现有规则与个人需求之间的矛盾",
        "middle": "制度的冰冷 vs 个人的温情",
        "deep": "遵守规则是保护还是束缚",
        "escalation_beats": ["遇到规则", "试图绕过", "被发现", "规则与人情", "找到平衡"],
    },
]
