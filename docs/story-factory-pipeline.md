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
polarity_dims.yaml     ──→ _polarity_engine.py   ──→ prompt ──→ Agent 脑洞 → 碰撞一句话
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
| 什么都没有 | what-if 50% + matrix 50% | 两种引擎混合，最大化多样性 |
| 有 emotion | matrix 100% | 精准情绪×场景匹配 |
| 有 text_content | what-if 5 条规则 + matrix 补充 | 概念变换为主 |

> 注：pitch 模式不再自动包含极性碰撞。如需极性灵感，使用 `mode='polarity'` 两步 Agent 流程。

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

跳过 pitch round，直出完整 story_seed。3 种来源均匀混合：

```
emotion_matrix  33%  — 情绪×场景精确匹配
daily_catch     33%  — 日常观察 + what-if 变换
random          33%  — 随机情绪+场景
```

> 注：polarity 模式采用两步 Agent 驱动流程，不在 batch 中自动混合。使用 `mode='polarity'` 单独获取极性碰撞故事。

---

## 极性碰撞引擎 (`_polarity_engine.py`)

### 设计原理

日常生活的戏剧性来自于对立两极的碰撞。引擎从 `polarity_dims.yaml` 加载 10 个**抽象轴定义**（零预制值），组装创意 prompt，交给 Agent 即时脑洞生成具体的 pole_a、pole_b、trigger、one_liner。

```
polarity_dims.yaml          _polarity_engine.py           Agent (Claude Code)
──────────────────          ──────────────────            ──────────────────
抽象轴定义                   加载 + 组装 prompt             即兴生成具体值
- axis_description          build_collision_prompt()      → pole_a, pole_b
- pole_a_direction          build_batch_prompts()           trigger, one_liner
- pole_b_direction          complete_collision()
- collision_mechanism
- cross_axis_hooks
```

每个维度定义了：**轴线描述**（量什么）、**两端方向**（pole_a/b_direction，纯描述无具体值）、**碰撞机制**（两端如何被关进同一个空间）、**跨轴钩子**（适合和哪些维度交叉融合）。

### 维度列表

| 维度 | 轴线 | pole_a 方向 | pole_b 方向 | 置信度 |
|------|------|------------|------------|--------|
| 消费行为 | 花钱态度 | 极端节俭，每一分钱都算清楚 | 完全不在乎价格，花钱是呼吸 | 5 |
| 社交自我 | 同一人的社交表现 | 极度退缩：聚餐坐角落、群不说话 | 极度外放：维权电话一小时、直播不停 | 5 |
| 权力位差 | 组织中的权力地位 | 底端：实习生、外包、保洁阿姨 | 顶端：创始人、一号位 | 5 |
| 亲疏折叠 | 同一段关系的亲密度 | 曾经的亲密：知道所有食物过敏 | 现在的陌生：朋友圈横线、擦肩不停 | 5 |
| 时间差 | 信息到达的时间 | 应该在那个时刻发生的 | 现在才发生的 | 4 |
| 可见边界 | 信息的可见范围 | 完全私密：备忘录日记、仅自己可见 | 完全公开：投屏、年会大屏 | 5 |
| 付出天平 | 关系中的付出方向 | 持续单向给予，已成默认设置 | 第一次需要被接住 | 4 |
| 表达压强 | 同一人的表达强度 | 完全压抑：三年不说"我累了" | 完全释放：一封邮件发给全公司 | 5 |
| 空间叠层 | 同一空间的占有痕迹 | 前任占有者的痕迹 | 现任占有者的现实 | 4 |
| 预期塌方 | 预期 vs 现实 | 长期准备、仔细构建的预期 | 实际发生的版本：门关上了 | 5 |

### 跨轴融合

每个维度可通过 `cross_axis_hooks` 声明适合交叉的其他维度。Agent 同时拿到两个轴的描述后自己找碰撞点——比如"消费行为 × 权力位差"就是经典的"廉价自助餐厅遇到老板"模式。

### 扩展维度

添加新维度只需编辑 YAML，零代码改动：

```yaml
dimensions:
  - name: 新维度名
    axis_description: 这个维度在量什么——从一端到另一端的完整光谱
    pole_a_direction: 低端是什么样的。纯描述方向，不说具体例子。
    pole_b_direction: 高端是什么样的。与pole_a是同一类东西的另一端。
    collision_mechanism: 两端如何被关进同一个空间/场景
    cross_axis_hooks:
      - partner: 权力位差
        fusion: 当这个维度的两端恰好也处于权力位差的两端时，碰撞升级为...
    emotions: [心酸, 温暖, 惊讶]
    patterns: [日常英雄, 时光对比]
    confidence: 3
```

引擎自动发现所有维度。`emotions` 和 `patterns` 为 Agent 提供创作方向建议。

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
│ polarity_pole_b, polarity_trigger,               │
│ polarity_cross_axis (跨轴融合时)                  │
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

## 使用指南

### 快速上手

所有模式通过 `StoryFactory.execute()` 调用，传入 `mode` 和可选参数：

```python
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
```

#### 场景一：灵感探索（最常用）

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'pitch', 'count': 5, 'seed': 42})
for i, p in enumerate(r.data['pitches'], 1):
    print(f'{i}. [{p[\"source\"]}] {p[\"logline\"]}  ({p[\"emotion\"]})')
"
```

`pitch` 模式的输出包含 8 个字段：`logline`、`emotion`、`pattern_hint`、`twist_type`、`style_hint`、`seedream_keywords`、`source`，polarity 来源额外携带 `polarity_dimension`、`polarity_pole_a`、`polarity_pole_b`。

#### 场景二：有明确情绪方向

```bash
# 给情绪，引擎自动偏重 matrix 匹配
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'pitch', 'emotion': '温暖', 'count': 5, 'seed': 99})
for i, p in enumerate(r.data['pitches'], 1):
    print(f'{i}. [{p[\"source\"]}] {p[\"logline\"]}')
"
```

#### 场景三：极性碰撞（Agent 脑洞）

极性碰撞采用**两步流程**：引擎组装 prompt → Agent 即兴脑洞 → 引擎完成种子。

```bash
# Step 1: 获取创意 prompt
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'polarity', 'count': 5, 'cross_ratio': 0.4, 'seed': 42})
for i, p in enumerate(r.data['prompts'], 1):
    tag = f\"[{p['dimension']}]\"
    if p['cross_axis']:
        tag += f\" x [{p['cross_axis']}]\"
    print(f'{i}. {tag} | {p[\"emotion\"]} | {p[\"pattern\"]}')
"
```

输出示例：
```
1. [表达压强] | 感动 | 身份反转
2. [权力位差] x [消费行为] | 心酸 | 身份反转
3. [亲疏折叠] x [时间差] | 治愈 | 如果当初
```

然后将 prompt 交给 LLM Agent 即兴生成具体的 pole_a、pole_b、trigger、one_liner：

```bash
# Step 2: 用 Agent 的输出完成种子
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
agent_outputs = [
    {
        'pole_a': '每天午休一个人去消防通道吃盒饭，三年没在公司群里发过一个字',
        'pole_b': '周会开到一半站起来，把手机连上投影仪放了四十张截图',
        'trigger': '第四十一张图是他半年前就写好的辞职信',
        'one_liner': '一个三年没主动发过言的人在全员大会上放了四十张截图——最后一张是他半年前就写好的辞职信',
        'dimension': '表达压强',
    },
    # ...更多 Agent 输出
]
r = f.execute({
    'mode': 'polarity_complete',
    'agent_outputs': agent_outputs,
    'seed': 42,
})
for s in r.data['seeds']:
    print(f'{s[\"title\"]}: {s[\"logline\"][:80]}...')
    print(f'  维度: {s[\"polarity_dimension\"]}', end='')
    if s.get('polarity_cross_axis'):
        print(f' x {s[\"polarity_cross_axis\"]}')
    else:
        print()
"
```

`cross_ratio` 参数控制跨轴融合的比例（0.0 = 纯单轴，0.5 = 半跨轴）。可用维度通过 `get_dimension_names()` 动态获取。

#### 场景四：有文本素材（段子 / 笑话 / 故事片段）

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({
    'mode': 'from_text',
    'text_content': '昨天点外卖，骑手打电话说到了，我下楼发现他举着手机在拍夕阳',
    'count': 2,
    'seed': 42,
})
for s in r.data['seeds']:
    print(f'{s[\"title\"]}: {s[\"logline\"]}')
    print(f'  模式: {s[\"pattern\"]} ({s[\"pattern_category\"]})')
    print(f'  情绪弧: {s[\"emotion_arc\"][\"starts\"]} → {s[\"emotion_arc\"][\"peaks_at\"]} → {s[\"emotion_arc\"][\"ends\"]}')
"
```

`from_text` 模式内部流程：`analyze_text()` 提取核心概念 → 情感猜测 → 角色暗示 → what-if 变换 → 完整 story_seed。

#### 场景五：批量生产（内容日历）

```bash
python -c "
from tools.writing.story_factory import StoryFactory
f = StoryFactory()
r = f.execute({'mode': 'batch', 'count': 8, 'seed': 123})
for s in r.data['seeds']:
    print(f'{s[\"title\"]} | {s[\"generation_mode\"]} | {s[\"pattern\"]} | {s[\"emotion_arc\"][\"starts\"]} → {s[\"emotion_arc\"][\"ends\"]}')
"
```

batch 模式按 25%/25%/25%/25% 均匀混合 `emotion_matrix`、`daily_catch`、`random`、`polarity` 四种引擎。

#### 场景六：从 pitch 到完整 seed 的完整流程

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

### 模式选择指南

| 你的需求 | 推荐模式 | 原因 |
|----------|----------|------|
| "给我一些灵感" | `pitch` | 三引擎混合，轻量快速，5-8 个方向供选择 |
| "我要冲突感强的" | `polarity` + Agent | 纯极性碰撞，两步流程：prompt → Agent 脑洞 → 完成种子 |
| "我有一段文字素材" | `from_text` | 自动分析文本中的概念并变换为故事 |
| "我有个视频想改编" | `from_video` | 提取视频概念 → 故事种子 |
| "我想精确控制情绪和场景" | `emotion_matrix` | 8 情绪 × 10 场景精确匹配 |
| "给我一个概念，变出几个版本" | `what_if` | 5 条变换规则，一个概念变出多个方向 |
| "从日常中找故事" | `daily_catch` | 35 条日常观察 + what-if 变换 |
| "随便来几个" | `random` | 随机情绪 + 场景，适合探索 |
| "给我批量出一周内容" | `batch` | 4 引擎均匀混合，跳过 pitch 直出完整 seed |

### 对话引擎

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

### 完整 Pipeline 流程示例

一个从零到完整剧本的典型交互流程：

```
1. 用户：  "给我一些温暖的故事灵感"
   Agent:  执行 pitch mode (emotion=温暖) → 展示 5-8 个一句话创意
   
2. 用户：  "第二个不错"
   Agent:  执行 from_text mode → 产出完整 story_seed（25 字段）
           → 展示 5 拍结构、角色、情绪弧线
   
3. 用户确认后 → Stage 2 (Develop):
           展开每拍为完整场景描述 → 生成潜台词对话
           → 构建三层冲突 → Therefore/But 因果链
           
4. Stage 3 (Review):
           叙事质量审查 → 因果链测试 → 冲突深度审计
           → 对话潜台词审计 → Markdown 导出
```

### 典型输出示例

polarity 模式输出（prompt 阶段）：
```
1. [表达压强] | 感动 | 身份反转
2. [权力位差] x [消费行为] | 心酸 | 日常英雄
3. [亲疏折叠] | 治愈 | 时光对比
4. [空间叠层] x [时间差] | 惊讶 | 隐藏真相
5. [社交自我] | 惊讶 | 奇葩逻辑
```

polarity_complete 模式输出示例（Agent 脑洞完成后）：
```
一个记了二十年超市小票的人和一个搬家扔掉十二个未拆快递的人，除夕夜在便利店同时抓住最后一盒水饺——他脱口而出'比上周贵了一块三'，她脱口而出'才二十三？'
  维度: 消费行为
  两极: 每周五晚上八点半准时出现在超市临期食品区 ↔ 外卖App年度账单二十三万
  触发器: 除夕夜，两人同时把手伸向最后一盒三全水饺
```

### 参数速查

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mode` | string | **必填** | 见"模式选择指南" |
| `emotion` | string | — | 好笑/感动/温暖/心酸/惊讶/紧张/愤怒/治愈 |
| `scene` | string | — | 家庭/办公室/地铁/便利店/医院/校园/街道/餐厅/公园/夜市 |
| `source_concept` | string | — | what_if 模式的原始概念 |
| `dimension` | string | — | polarity 模式的维度名（见极性维度列表） |
| `text_content` | string | — | from_text 模式的文本素材 |
| `video_source` | string | — | from_video 模式的视频 URL 或本地路径 |
| `pattern` | string | — | 强制指定故事模式名（18 个可选） |
| `count` | int | 1 | 生成数量（1-20） |
| `seed` | int | — | 随机种子，固定可复现 |
| `character_count` | int | 2 | 每故事角色数（1-4） |
| `target_duration_seconds` | float | 60 | 目标时长（15-90 秒） |
| `target_platform` | string | douyin | douyin/tiktok/instagram/youtube_shorts/generic |

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
    axis_description: 这个维度在量什么——从一端到另一端的完整光谱
    pole_a_direction: 低端方向描述。纯描述这类人/状态的典型特征，不说具体例子。
    pole_b_direction: 高端方向描述。与pole_a是同一类东西的另一端。
    collision_mechanism: 两端如何被关进同一个空间/场景
    cross_axis_hooks:
      - partner: 另一个维度名
        fusion: 两个维度交叠时的融合描述
    emotions: [心酸, 温暖, 惊讶]
    patterns: [日常英雄, 时光对比]
    confidence: 3   # 1-5，控制随机选中的权重
```

无需改动任何 Python 代码。Agent 会根据这些方向性描述即兴生成具体的 pole_a、pole_b、trigger 值。

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
| 极性引擎 | `tools/writing/_polarity_engine.py` | Agent 驱动的极性碰撞引擎（prompt 组装 + 碰撞完成） |
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
