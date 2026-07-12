# Story Factory Pipeline — 剧情与故事创作流水线

> Last updated: 2026-07-12 | Story Factory v0.1.0

## 概况

Story Factory 是 OpenMontage 的**纯故事创作流水线**——不生成图片或视频，只产出故事。目标是为抖音/TikTok/Reels 等短视频平台创作 60 秒以内的短篇叙事内容。

| 特性 | 说明 |
|------|------|
| 名称 | `story-factory` |
| 目标 | 从灵感输入到完整剧本，一键生成短篇故事 |
| 核心差异化 | 极性碰撞引擎、潜台词感知对话、三层冲突系统、Egri 角色深度 |
| 最终产出 | `story_script`（完整剧本 JSON）+ Markdown 导出 |
| 稳定性 | beta |

---

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│                    Story Factory                     │
│                                                     │
│  3 个生成引擎 (tools/writing/)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ polarization │ │   what-if    │ │   emotion    │ │
│  │   engine     │ │   engine     │ │   matrix     │ │
│  │ (10 维度)     │ │ (5 变换规则)  │ │ (200+ 种子)  │ │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │
│         └────────────────┼────────────────┘          │
│                          ▼                           │
│              ┌──────────────────────┐                │
│              │    🎯 Pitch Round     │                │
│              │   5-8 个一句话创意     │                │
│              └──────────┬───────────┘                │
│                         │ 用户选 1 个                 │
│                         ▼                            │
│              ┌──────────────────────┐                │
│              │    📖 Seed Round     │                │
│              │   完整 story_seed     │                │
│              │   (5 拍 + 角色 + 弧线) │               │
│              └──────────┬───────────┘                │
│                         │                            │
└─────────────────────────┼────────────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │  Stage 2: Develop    │
              │  完整剧本展开          │
              └──────────┬───────────┘
                          ▼
              ┌──────────────────────┐
              │  Stage 3: Review     │
              │  叙事质量审查          │
              └──────────────────────┘
```

### 三个生成引擎

所有引擎都遵循"YAML 数据 + Python 加载器"模式，新增内容只需编辑 YAML，零代码改动。

```
polarity_dims.yaml     ──→ _polarity_engine.py   ──→ 极性碰撞一句话
emotion_matrix.yaml    ──→ _emotion_matrix.py    ──→ 预置故事种子（86个）
日常观察 (同 YAML)      ──→ _whatif_engine.py     ──→ 5条规则变换
                              │
                              ▼
                       story_factory.py
                       9 种模式调度
```

---

## 生成模式详解

### 模式矩阵

| Mode | 输入要求 | 产出 | 来源混合 | 使用场景 |
|------|----------|------|----------|----------|
| `pitch` | 无 / emotion / text | 8 字段 logline | 见下文 | 灵感探索、方向筛选 |
| `polarity` | 无 / dimension | 一句话碰撞 | 纯 polarity | 要冲突驱动的创意 |
| `emotion_matrix` | emotion + scene | 完整 seed | 纯 matrix | 精确情绪×场景匹配 |
| `what_if` | source_concept | 完整 seed | 纯 what-if | 有原始概念要变换 |
| `daily_catch` | 无 | 完整 seed | 纯 daily observation | 从日常中发现故事 |
| `random` | emotion | 完整 seed | 纯 random matrix | 随机探索 |
| `batch` | 无 | 多个完整 seed | 4 种混合 | 批量生产、内容日历 |
| `from_text` | text_content | 完整 seed | text → what-if | 有文字素材 |
| `from_video` | video_source | 完整 seed | video → concept → what-if | 有视频素材 |

### pitch 模式（"给我灵感"）

**这是最主要的探索模式**。根据用户输入自动选择来源混合：

| 用户输入 | 来源分布 | 行为 |
|----------|----------|------|
| 什么都没有 | polarity 40% + what-if 30% + matrix 30% | 三种引擎混合，最大化多样性 |
| 有 emotion | matrix 60% + polarity 40% | 精准方向 + 冲突惊喜 |
| 有 text_content | what-if 5 条规则 + matrix 补充 | 概念变换为主 |

每个 pitch 包含的字段：

```json
{
  "logline": "一句话完整故事概念",
  "emotion": "好笑 | 感动 | 温暖 | 心酸 | 惊讶 | 紧张 | 愤怒 | 治愈",
  "pattern_hint": "故事模式（身份反转 / 误会连环 / 日常英雄 等）",
  "twist_type": "视角翻转 | 类型转换 | 时间跳跃 | 代价升级 | 反转倒置 | 极性碰撞",
  "style_hint": "warm_illustration | clean_comic | cinematic_drama | watercolor_nostalgia | ink_dramatic",
  "seedream_keywords": ["画风关键词数组"],
  "source": "polarity | matrix | what_if | what_if_observation"
}
```

polarity 来源的 pitch 额外携带：
- `polarity_dimension` — 冲突维度名
- `polarity_pole_a` / `polarity_pole_b` — 碰撞的两极

### batch 模式（批量生产）

跳过 pitch round，直出完整 story_seed。4 种来源均匀混合：

```
emotion_matrix  25%  — 情绪×场景精确匹配
daily_catch     25%  — 日常观察 + what-if 变换
random          25%  — 随机情绪+场景
polarity        25%  — 极性碰撞
```

---

## 极性碰撞引擎 (`_polarity_engine.py`)

### 设计原理

日常生活的戏剧性来自于对立两极的碰撞。引擎从 `polarity_dims.yaml` 加载 10 个维度，每个维度定义了：

```
pole_a (低/弱势端) × pole_b (高/强势端) × collision_trigger (相遇场景)
                    ↓
              一句话故事 hook
```

### 维度列表

| 维度 | 低极示例 | 高极示例 | 触发器示例 | 置信度 |
|------|----------|----------|------------|--------|
| 消费层级 | 39元/位的自助餐 | 前女友的现男友 | 拼桌 | 5 |
| 社交能量 | 社恐，一个人坐角落 | 维权时条理清晰骂到退群 | 私信里全是骂人的话 | 5 |
| 身份层级 | 实习生 | CEO | 电梯独处 | 4 |
| 情感距离 | 五年没联系的同学 | 前男友 | 货架出现她最爱的饮料 | 5 |
| 时间 | 三年前 | 现在 | 收到迟到的快递 | 5 |
| 公开/私密 | 深夜朋友圈仅自己可见 | 会议投屏 | demo 时 PPT 夹带了书签 | 5 |
| 给予/索取 | 三年每天带早餐 | 第一次开口求助 | 辞职当天群被解散 | 4 |
| 沉默/爆发 | 三年没说过"我累了" | 一封邮件发给全公司 | 没人反应过来 | 5 |
| 地盘/领地 | 前女友家 | 你的照片还贴在墙上 | 打开柜子看到你送的杯子 | 4 |
| 期待/落差 | 准备了半年的升职演讲 | 那个职位被裁了 | 继续上班但所有人眼神变了 | 4 |

### 扩展维度

添加新维度只需编辑 YAML，零代码改动：

```yaml
dimensions:
  - name: 城乡差距           # 新维度
    confidence: 4
    pole_a:
      values:
        - "过年回家发现村里装了路灯"
        - "城里的同事从没见过稻子"
    pole_b:
      values:
        - "CBD 的写字楼里永远不关的灯"
        - "打车到公司楼下，司机从没进过二环"
    collision_triggers:
      - "你的外卖地址是老家那个镇的名字"
      - "视频通话时他把镜头转过去给你看田"
```

引擎自动发现，默认情绪建议降级到 `["心酸", "温暖", "惊讶", "好笑"]`。

---

## 故事种子结构 (`story_seed`)

一个完整的 story_seed 包含 25 个字段：

```
┌─ 核心信息 ─────────────────────────────────────┐
│ seed_id, title, hook, logline                    │
│ pattern, pattern_category                        │
│ douyin_tags, difficulty                          │
├─ 情绪弧线 ─────────────────────────────────────┤
│ emotion_arc: { starts, peaks_at, ends }          │
├─ 叙事结构 ─────────────────────────────────────┤
│ beats[5]: { name, start_second, end_second,     │
│             description, visual_suggestion,      │
│             text_overlay, camera_hint }          │
│ twist, ending, ending_type                      │
│ closing_image_hint, page_turn_hook              │
├─ 角色 ──────────────────────────────────────────┤
│ character_archetypes[]: {                        │
│   role, description, emotional_state,           │
│   visual_notes, physiological, sociological,    │
│   psychological, sacred_flaw, trauma_origin,    │
│   desire_want, desire_need, opponent_mirror,    │
│   action_under_pressure                         │
│ }                                                │
├─ 视觉 ──────────────────────────────────────────┤
│ suggested_style: { color_palette, mood,          │
│   lighting, seedream_keywords[] }               │
│ visual_keywords[]                                │
├─ 极性（仅 polarity 来源）───────────────────────│
│ polarity_dimension, polarity_pole_a,             │
│ polarity_pole_b, polarity_trigger               │
└─ 元数据 ───────────────────────────────────────┤
│ version, generation_mode, generated_at          │
│ target_platform, target_duration_seconds        │
│ estimated_image_count                            │
└──────────────────────────────────────────────────┘
```

---

## 角色原型 (12 个)

每个角色包含 **Egri 三维 + Storr 神圣缺陷 + Truby 欲望对立**：

```
妈妈      爸爸      打工人    陌生人
孩子      老板      老人      年轻人
外卖小哥  服务员    闺蜜/兄弟   奶奶/外婆
```

每个角色的 14 个字段：
```
physiological   — 身体特征
sociological    — 社会地位
psychological   — 心理状态
sacred_flaw     — 神圣缺陷（驱动一切的自我欺骗信念）
trauma_origin   — 创伤来源
desire_want     — 角色以为自己想要的东西
desire_need     — 角色实际需要的东西（want ≠ need 是戏剧性的来源）
opponent_mirror — 对手映射（对方映照了自己不敢面对的部分）
action_under_pressure — 压力下的行为特征
```

---

## 对话引擎 (`_dialogue_engine.py`)

### 核心规则

| 规则 | 示例 |
|------|------|
| 不直接说出情绪 | 不说"我很生气"→ 说"（沉默，把杯子重重放下）" |
| 用动作替代情感 | 不说"我想你"→ 说"这是第三次路过你喜欢的面包店了" |
| 说反话 | 不说"我很难过"→ 说"没事，挺好的" |
| 转移话题 | 不说"我不想谈这个"→ 说"对了，你吃饭了吗？" |
| 用具体代替抽象 | 不说"我过得很糟糕"→ 说"泡面已经连吃第四天了" |
| 沉默是最有力的台词 | （长久沉默后）……走吧 |

### mobile 约束

```
每行 ≤ 15 汉字    →  check_mobile_limit()
每格 ≤ 3 气泡     →  validate_panel_dialogue()
每气泡 ≤ 25 字    →  truncate_for_mobile()
```

---

## Playbooks (18 个故事模式)

| 类别 | 模式 | 时间复杂度 | 适合 |
|------|------|-----------|------|
| 情感向 | 日常英雄, 陌生人温暖, 亲情反转 | 单时间线 | 温暖/催泪 |
| 反转向 | 身份反转, 隐藏真相, 五幕对称 | 单时间线 | 惊讶/悬疑 |
| 喜剧向 | 喜剧升级, 社死瞬间, 误会连环, 奇葩逻辑 | 单时间线 | 搞笑 |
| 回想向 | 时光对比, 如果当初 | 双时间线 | 怀旧/感慨 |
| 动作向 | 瞬间决定 | 实时 | 紧张/刺激 |
| 成长向 | 救猫咪节拍, 英雄之旅, 扁平到立体 | 多幕 | 励志 |
| 实用向 | 问题解决 | 线性 | 教程/科普 |
| 治愈向 | 打工人小确幸 | 日常 | 轻松/治愈 |

---

## Pipeline 三阶段

### Stage 1: Ideate

```
Round 1: Pitch Round
  ├── 判断用户意图 → 选择 mode
  ├── story_factory.execute(mode, ...)
  ├── 展示 5-8 个一句话创意
  └── 用户选 1 个

Round 2: Seed Round
  ├── 把选中 logline 喂给 from_text 模式
  ├── 产出完整 story_seed（5 拍 + 角色 + 情绪弧线）
  └── 展示给用户 → 确认 → 进入 Stage 2
```

**质量门 (G1)**：≥ 5 个 pitch，用户明确选择，hook 非空，beats 精确 5 拍，emotion_arc 完整，character 有 visual_notes。

### Stage 2: Develop

```
展开 story_seed 为完整剧本
  ├── 角色三维深度（Egri：生理/社会/心理）
  ├── 5 拍展开（每拍 1-2 段场景描述）
  ├── 潜台词对话（surface_text ≠ subtext_meaning）
  ├── 三层冲突（表面/中间/深层）
  ├── Therefore/But 因果链
  ├── 呼吸节奏（吸气/屏气/呼气）
  └── 移动端约束检查
```

### Stage 3: Review

```
叙事质量全面审查
  ├── Therefore/But 连接测试（禁止 "and then"）
  ├── 冲突深度审计（≥ 1 个深层冲突）
  ├── 角色维度验证（所有字段非空，desire_want ≠ desire_need）
  ├── 对话潜台词审计（no surface == subtext）
  ├── 价值变化审计（每场景 polarity 变化）
  ├── 呼吸节奏验证（无连续 2 场景同模式）
  └── Markdown 导出 → projects/<name>/story.md
```

---

## 测试例子

### 例 1：无输入灵感探索

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'pitch', 'count': 5, 'seed': 42})
for i, p in enumerate(r.data['pitches'], 1):
    print(f'{i}. [{p[\"source\"]}] {p[\"logline\"]}  ({p[\"emotion\"]})')
"
```

输出：
```
1. [polarity] 39元自助餐撞上了老板——排在你前面 (心酸)
2. [what_if_observation] 下雨天发现伞上有别人写的名字——是上一个落下伞的人 (感动)
3. [matrix] 地铁上，一个疲惫的人把座位让给了更需要的人 (温暖)
4. [polarity] 社恐，一个人坐角落吃饭撞上维权时骂到退群的人——你看到她私信里全是骂人的话 (好笑)
5. [what_if_observation] 电梯里遇到领导才发现走错了楼层 (好笑)
```

### 例 2：有情绪方向 + 展开完整种子

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()

# Round 1: 情绪方向 pitch
pitches = f.execute({'mode': 'pitch', 'emotion': '温暖', 'count': 5, 'seed': 99})

# 模拟用户选第一个
chosen = pitches.data['pitches'][0]
print(f'选中: {chosen[\"logline\"]}')

# Round 2: 展开为完整 seed
seed = f.execute({
    'mode': 'from_text',
    'text_content': chosen['logline'],
    'count': 1,
    'seed': 99,
})
s = seed.data['seeds'][0]
print(f'标题: {s[\"title\"]}')
print(f'模式: {s[\"pattern\"]} ({s[\"pattern_category\"]})')
print(f'情绪弧: {s[\"emotion_arc\"]}')
print(f'5拍结构:')
for b in s['beats']:
    print(f'  {b[\"beat_number\"]}. {b[\"name\"]} ({b[\"start_second\"]}s-{b[\"end_second\"]}s): {b[\"description\"][:50]}...')
print(f'角色: {[c[\"role\"] for c in s[\"character_archetypes\"]]}')
"
```

### 例 3：极性碰撞（指定维度）

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'polarity', 'dimension': '沉默/爆发', 'count': 3, 'seed': 7})
for s in r.data['seeds']:
    print(f'{s[\"logline\"]}')
    print(f'  维度: {s[\"polarity_dimension\"]}')
    print(f'  两极: {s[\"polarity_pole_a\"]} ↔ {s[\"polarity_pole_b\"]}')
    print(f'  触发器: {s[\"polarity_trigger\"]}')
    print()
"
```

输出示例：
```
三年没跟家人说过一句'我累了'——一封邮件发给了全公司——第二天他照常来上班，但所有人看他的眼神都变了
  维度: 沉默/爆发
  两极: 三年没跟家人说过一句'我累了' ↔ 一封邮件发给了全公司
  触发器: 第二天他照常来上班，但所有人看他的眼神都变了
```

### 例 4：批量生产

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'batch', 'count': 4, 'seed': 123})
for s in r.data['seeds']:
    print(f'{s[\"title\"]} | {s[\"generation_mode\"]} | {s[\"pattern\"]} | {s[\"emotion_arc\"][\"starts\"]} → {s[\"emotion_arc\"][\"ends\"]}')
"
```

### 例 5：对话引擎

```python
from tools.writing._dialogue_engine import get_dialogue, check_mobile_limit

# 获取"妈妈"在"操心"情绪下的潜台词对话
lines = get_dialogue("妈妈", "操心")
for line in lines:
    print(f'说: "{line.surface_text}"')
    print(f'  实际含义: {line.subtext_meaning}')
    print(f'  语气: {line.tone}')
    print(f'  表演: {line.delivery_hint}')
    print(f'  mobile优化: {line.mobile_optimized}')

# 检查移动端约束
check_mobile_limit("给你寄了东西")  # True (≤15字)
check_mobile_limit("我已经没有精力做任何选择了")  # False (>15字)
```

---

## 扩展指南

### 添加新的故事种子（情绪×场景矩阵）

编辑 `tools/writing/emotion_matrix.yaml`。有三种扩展方式：

**A. 给已有的情绪×场景组合加种子：**
```yaml
matrix:
  温暖:
    家庭:
      - title: 你的新故事标题
        logline: 一句话故事总结
        hook: 开篇抓人句子
        pattern_name: 日常英雄    # 必须是 _patterns.py 中已注册的模式名
        character_roles:
          - 主角
          - 配角
        twist_hint: 反转或揭示
        visual_keywords:
          - 场景关键词1
          - 场景关键词2
```

**B. 加一个新场景（如"菜市场"）：**
1. 在 `scenes:` 列表加 `- 菜市场`
2. 在每个 emotion 下加 `菜市场:` 条目和至少一个种子

**C. 加一个新情绪（如"恐惧"）：**
1. 在 `emotions:` 列表加 `- 恐惧`
2. 在 `matrix:` 下加 `恐惧:` 块，覆盖所有场景

所有扩展零代码改动——`_emotion_matrix.py` 自动发现。

### 添加新的日常观察

编辑 `tools/writing/emotion_matrix.yaml` 的 `daily_observations:` 列表。

### 添加新的极性维度

编辑 `tools/writing/polarity_dims.yaml`，在 `dimensions:` 列表中添加：

```yaml
  - name: 你的维度名
    name_en: Your Dimension Name
    description: 一句话描述这个维度的冲突来源
    confidence: 3   # 1-5，控制随机选中的权重
    pole_a:
      values:
        - "低极的具体状态1"
        - "低极的具体状态2"
    pole_b:
      values:
        - "高极的具体状态1"
        - "高极的具体状态2"
    collision_triggers:
      - "具体的相遇场景1"
      - "具体的相遇场景2"
```

无需改动任何 Python 代码。如需定制情绪/模式建议，在 `_polarity_engine.py` 的 map 中添加一行。

### 添加新的故事模式

编辑 `tools/writing/_patterns.py`，在 `PATTERNS` 列表中添加：

```python
StoryPattern(
    name="你的模式名",
    category="comedy | emotional | suspense | slice_of_life | social",
    beats=[...],  # 5 个 Beat
    difficulty="easy | medium | hard",
)
```

### 添加新的角色原型

编辑 `tools/writing/story_factory.py` 的 `CHARACTER_ARCHETYPES` 列表，添加：

```python
{"role": "角色名", "description": "一句话描述",
 "physiological": "...", "sociological": "...", "psychological": "...",
 "sacred_flaw": "...", "trauma_origin": "...",
 "desire_want": "...", "desire_need": "...",
 "opponent_mirror": "...", "action_under_pressure": "...",
 "emotional_state": "...", "visual_notes": "..."}
```

---

## 相关文件

| 层级 | 文件 | 用途 |
|------|------|------|
| Pipeline 定义 | `pipeline_defs/story-factory.yaml` | 3 阶段流水线元数据 |
| Stage 技能 | `skills/pipelines/story-factory/*.md` | 阶段导演指导 |
| 核心工具 | `tools/writing/story_factory.py` | 9 种模式的故事种子生成 |
| 极性引擎 | `tools/writing/_polarity_engine.py` | 极性碰撞引擎 |
| 极性数据 | `tools/writing/polarity_dims.yaml` | 10 个极性维度 |
| What-if 引擎 | `tools/writing/_whatif_engine.py` | 5 条变换规则 |
| 情绪矩阵引擎 | `tools/writing/_emotion_matrix.py` | YAML 加载器 + 公共 API |
| 情绪矩阵数据 | `tools/writing/emotion_matrix.yaml` | 8 情绪 × 10 场景 × 86 种子 + 35 日常观察 |
| 故事模式 | `tools/writing/_patterns.py` | 18 个故事模式 |
| 对话引擎 | `tools/writing/_dialogue_engine.py` | 潜台词对话 |
| 文本分析 | `tools/writing/_text_analyzer.py` | 文本→概念提取 |
| 视频转概念 | `tools/writing/_video_to_concept.py` | 视频→概念提取 |
| 产物 Schema | `schemas/artifacts/story_script.schema.json` | story_script 验证 |
| 创意技能 | `skills/creative/storytelling.md` | 叙事理论指导 |
| 创意技能 | `skills/creative/short-form.md` | 短篇创作指导 |
| 创意技能 | `skills/creative/comedy-framework.md` | 喜剧框架 |
| 创意技能 | `skills/creative/advertising-structure.md` | 钩子类型指导 |
