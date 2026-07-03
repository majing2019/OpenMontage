# Comic Creator System — 完整解决方案

## 实施状态

### ✅ 已完成

- **Phase 1**: Story Factory（故事选题工厂）— `tools/writing/` + `scripts/story_idea.py`
- **Phase 2**: 配套 Skill 文件 — 人物一致性、漫画排版、个人 IP

### 🔲 当前：comic-story 流水线

将以上所有组件串联成一条完整流水线，实现"一句话/视频 → 图片序列"。

---

## 流水线概况

```
一句话/段子/视频 → [ideate] → story_seed → [style-pick] → 画风确认
    → [shot-plan] → shot_list → [preview] → 角色三视图 + 场景样图
    → [generate] → 全量图片 → [caption] → 文字叠加到图片
    → [compose] → 最终图片序列（带 IP 结尾）
```

| 特性 | 说明 |
|------|------|
| 名称 | `comic-story` |
| 目标 | 从灵感输入到最终图片序列，一键生成抖音/小红书漫画内容 |
| 核心差异化 | 内置角色一致性（三视图确认）、漫画排版（文字叠加确认）、个人 IP 结尾 |
| 最终产出 | **图片序列**（PNG），非视频——用户可自行拼成视频或发布为图集 |
| 音乐 | 不适用（图片序列无音轨） |
| 稳定性 | beta（首次发布） |

---

## 流水线架构：Executive Producer 模式

comic-story 遵循项目既有的 Executive Producer 模式（参见 `skills/pipelines/explainer/executive-producer.md`、`skills/pipelines/cinematic/executive-producer.md`）。EP 是一个有状态的"大脑"，串行执行 7 个阶段，在每两个阶段之间做跨阶段质量检查。

### EP_STATE 累积状态

```yaml
EP_STATE:
  pipeline: comic-story
  playbook: <从 style-pick 阶段选定的 playbook 名称>
  target_duration_seconds: <来自 story_seed.target_duration_seconds，默认 60>
  budget_total_usd: <可配置，默认 $1.00>
  budget_spent_usd: 0.0
  budget_remaining_usd: <budget_total - budget_spent>
  output_format: "image_sequence"  # 固定为图片序列，非视频

  # ---- 漫画特有状态 ----
  style_decision: null          # style-pick 阶段产出：锁定的画风参数
  preview_manifest: null        # preview 阶段产出：锁定的角色锚定 + 场景模板
  character_registry: null      # shot-plan 阶段构建：角色锚定描述字典
  scene_registry: null          # shot-plan 阶段构建：场景模板描述字典
  style_lock: []                # 画风关键词数组（style-pick 锁定后不可变）
  image_consistency_score: null # generate 阶段的跨面板风格一致性评分
  reference_video_analysis: null # ideate 阶段的视频 5 维分析结果（传递给 style-pick）

  # ---- 7 阶段产出累积 ----
  artifacts:
    ideate: null        # → story_seed
    style_pick: null    # → style_decision
    shot_plan: null     # → shot_list
    preview: null       # → preview_manifest
    generate: null      # → asset_manifest
    caption: null       # → captioned_assets
    compose: null       # → render_report（图片序列验证报告 + 文件列表）

  # ---- 跨阶段追踪 ----
  revision_counts: {}       # stage_name → 已修订次数
  issues_log: []            # 所有问题及解决状态
  total_panels: 0           # 本次产出的面板总数
```

### EXECUTE_STAGE 模板

每个阶段的执行遵循以下流程：

```
EXECUTE_STAGE(stage_name):

  1. PREPARE
     - 从 pipeline_defs/comic-story.yaml 读取该阶段的 skill 路径
     - 注入 EP_STATE 作为上下文
     - 如有上轮修订反馈，一并注入

  2. SPAWN DIRECTOR
     - 读取该阶段的 director skill
     - Director 执行完整流程
     - Director 产出 canonical artifact

  3. REVIEW（EP 执行，非 Director）
     - Schema 验证产出物
     - 检查 pipeline manifest 中该阶段的 review_focus
     - 检查 success_criteria
     - 检查 playbook 约束
     - 执行该阶段的跨阶段质量门（见下表）

  4. GATE DECISION
     PASS  → 存入 EP_STATE，继续下一阶段
     REVISE → revision_counts[stage]++，若 < 3 则重跑，否则 PASS WITH WARNINGS
     SEND_BACK → 仅当下游发现 invalidate 上游工作时，最多 1 次/stage pair
```

### 反循环保护

| 限制 | 值 | 理由 |
|------|---|------|
| 每阶段最大修订次数 | 3 | 防止完美主义循环 |
| 每对阶段最大 send-back | 1 | 防止乒乓效应 |
| 总 send-back 上限 | 3 | 限制总返工量 |
| 预算硬上限 | 可配置（默认 $1.00） | 超出即停 |
| 最大挂钟时间 | 15 分钟 | 超时即 proceed with warnings |

达到任何限制 → **proceed with warnings，永不永久阻塞**。

---

## 7 个阶段

### Stage 1: `ideate` — 灵感 → 故事种子

- **工具**: `story_factory`（from_text/from_video/emotion_matrix/batch 模式）
- **产出**: `story_seed` artifact
- **审批**: 是（让用户从多个种子中选择一个）

#### 文本输入模式

直接调用 StoryFactory，从用户提供的一句话/段子/情绪/场景中生成 3-5 个故事种子候选。

#### 视频输入模式（双路径并行）

当用户提供视频 URL 时，ideate 阶段同时执行两条路径，分别提取语言内容和视觉风格：

```
用户视频 URL
  │
  ├── Path A（语言内容）→ _video_to_concept.py（已有）
  │     ├── Tier 1: TranscriptFetcher（YouTube 字幕，最快）
  │     ├── Tier 2: VideoAnalyzer + transcript_only
  │     └── Tier 3: VideoDownloader + Whisper（最慢但通用）
  │     └── 输出：转录文本 → StoryFactory._gen_from_video() → 故事种子
  │
  └── Path B（视觉风格）→ video-reference-analyst.md 协议（接入项目已有能力）
        ├── VideoAnalyzer（analysis_depth: "standard"）
        ├── Agent 视觉分析关键帧
        │     ├── 内容摘要
        │     ├── 色板分析（主色、辅助色、背景色）
        │     ├── 构图特征（居中、三分法、对称等）
        │     ├── 转场模式（硬切、叠化、滑动等）
        │     └── 文字排版（如果有：位置、字体、动画）
        ├── 5 维结构化输出（MANDATORY）：
        │     ├── Subject — 画面主体是什么
        │     ├── Subject Motion — 主体运动类型
        │     ├── Scene — 场景构成（含 overlay 分离）
        │     ├── Spatial Framing — 空间取景（景别、角度）
        │     └── Camera — 镜头运动（固定/摇/推/拉/跟）
        └── 输出：video_analysis_brief → 存入 EP_STATE.reference_video_analysis
              → 传递给 style-pick 阶段预填画风建议
```

两条路径**互补而非互斥**，同时执行：
- **Path A** 的转录文本 → 喂给 StoryFactory 生成故事种子（核心产出）
- **Path B** 的视觉分析 → 存入 EP_STATE.reference_video_analysis → style-pick 阶段读取后**预填画风建议**

#### 质量门 G1

| 检查项 | 要求 |
|--------|------|
| hook | 非空 |
| beats | 完整 5 beats（minItems:5） |
| emotion_arc | 含 starts/peaks_at/ends |
| character_archetypes | 至少 1 个有 visual_notes |
| suggested_style | 含 seedream_keywords |

### Stage 2: `style-pick` — 确定漫画画面风格

- **产出**: `style_decision` artifact
- **审批**: 是

画风来源采用 **Style Playbook 体系**管理（YAML 文件，复用项目的 `playbook_loader` 加载和 `validate_playbook` 校验机制）。5 种内置画风预设从 StoryFactory 的 Python dict 转为正式 Playbook 文件，同时支持用户从参考图或参考视频提取自定义画风。

#### 内置画风预设

| 名称 | Playbook 文件 | 风格描述 | 适合类型 |
|------|--------------|---------|---------|
| 温暖手绘 | `warm-illustration.yaml` | 柔和色调，手绘质感，日式生活插画 | 亲情、治愈、日常 |
| 电影感暗调 | `cinematic-drama.yaml` | 高对比度，戏剧性光影，暗调氛围 | 悬疑、反转、紧张 |
| 现代漫画风 | `clean-comic.yaml` | 干净线条，明亮色彩，夸张表情 | 搞笑、社死、段子 |
| 水墨黑白 | `ink-dramatic.yaml` | 黑白灰为主，少量红色点缀，东方美学 | 反转、冲击、深度 |
| 水彩怀旧 | `watercolor-nostalgia.yaml` | 淡雅水彩色，褪色老照片质感 | 时光、回忆、感动 |

#### 自定义画风库

用户在 style-pick 阶段主动提供参考素材（图片或视频）时，可将提取的画风保存为自定义预设，供后续项目复用。

每个自定义画风存放在 `styles/custom/<name>/` 目录下：

```
styles/custom/
  └── ghibli/                    # 用户命名，如"宫崎骏风"
      ├── style.yaml             # 画风参数（格式与内置 Playbook 兼容）
      └── reference/             # 参考素材（保存原图/抽帧 + 风格测试图）
          ├── source_01.png      # 用户提供的图片，或从视频中抽取的关键帧
          ├── source_02.png
          ├── source_video.mp4   # （如有）用户提供的原始参考视频
          └── test_render.png    # 风格测试图（Agent 生成，用于视觉确认）
```

下次运行 `style-pick` 时，自定义画风自动出现在预设列表中。展示时附带 `reference/test_render.png` 作为缩略预览。

**参考素材提取工作流**:
1. 用户提供参考（图片路径/URL，多个用逗号分隔；或视频 URL/路径）
2. **多图模式**: Agent 逐张分析，取共享特征作核心风格 + 独特特征作弹性空间
3. **视频模式**: `frame_sampler` 按时间间隔抽取 5-10 帧 → 同多图模式聚合
4. 将提取的参数转化为 Seedream 能理解的风格描述关键词
5. 生成一张风格测试图让用户确认"是这个感觉吗？"
6. 确认后锁定风格参数，作为后续所有图的 style_lock
7. 问用户"这个画风要保存起来以后复用吗？"——输入一个名称（如"宫崎骏风"），将 YAML + 参考素材一起写入 `styles/custom/<name>/`

#### 参考图输入类型

| 输入 | 处理方式 | 优势 |
|------|---------|------|
| 单张图片 | VLM 直接分析 | 最快 |
| 多张图片 | 逐张分析 → 取交集（共享特征）+ 并集（独特特征） | 更完整捕捉风格 |
| 视频 | `frame_sampler` 抽取 5-10 个关键帧 → 逐帧分析 → 聚合 | 捕捉动态风格 + 色彩时间线 |

#### 多图/视频聚合逻辑

1. 逐帧/逐图分析色板、光影、线条、笔触
2. 提取**共享特征**（每张都有的 = 核心风格）作为 style_lock
3. 标记**变化特征**（随时间/场景变化的 = 风格弹性空间）作为可选参考
4. 生成汇总报告：核心风格 + 弹性空间 + 推荐 Seedream 关键词

#### 消费视频分析结果

当 EP_STATE.reference_video_analysis 存在时（来自 Stage 1 视频模式的 Path B）：
1. 从分析结果中提取色板、光影、线条风格
2. 生成 Seedream 关键词建议（如 "暖色调, 手绘质感, 柔和线条"）
3. 生成一张风格测试图让用户确认"是这个感觉吗？"
4. 确认后，参考图的风格参数写入 style_decision.reference_analysis
5. 询问用户"这个画风要保存为自定义预设吗？" → 如是，保存到 `styles/custom/`

#### 质量门 G2

| 检查项 | 要求 |
|--------|------|
| style_lock | ≥ 3 个关键词 |
| image_prompt_prefix | 非空 |
| consistency_anchors | 非空 |
| reference_analysis | 参考素材模式时已填充 |

### Stage 3: `shot-plan` — 故事种子 + 画风 → 分镜表

- **技能**: 自动读取 `character-consistency.md` `comic-typography.md` `personal-ip.md`
- **产出**: `shot_list` artifact
- **审批**: 是（用户检查分镜表再进入生图）

**关键逻辑**: 每张图的文字分为两类——
- `scene_texts`: 场景自带文字（招牌、路牌等），自动判断该用 `ai_draw` 还是 `post_only`
- `text_overlay`: 叙事文字（钩子、气泡、旁白），标记为后期叠加

#### 质量门 G3

| 检查项 | 要求 |
|--------|------|
| panel 文字 | 每个 panel 都有 text_overlay 或 scene_texts（或两者都有） |
| scene_texts.method | ≤5 字 `ai_draw`、>5 字 `post_only` |
| character_registry | 覆盖所有登场角色且有 anchor_description |
| scene_registry | 覆盖所有不同场景 |
| IP 结尾 | 已规划 |

### Stage 4: `preview` — 角色三视图 + 场景定妆

- **流程**:
  1. 从 shot_list 提取所有登场角色，为每个角色生成**三视图**（正面/侧面/背面，共 1 张图，含完整角色描述）
  2. 为每个不同场景生成**1 张场景样图**（使用该场景的模板 + 角色锚定 + 锁定画风）
  3. 用户审核：角色像不像？场景对不对？确认后锁定角色和场景的 prompt 模板
- **工具**: `image_selector`（路由到 Seedream）
- **产出**: `preview_manifest`（角色定妆图 + 场景样图 + 锁定的 prompt 模板）
- **审批**: 是（**关键质量门**，确认后全量生图不再修改角色/场景）

#### 质量门 G4

| 检查项 | 要求 |
|--------|------|
| 角色锚定图 | 每个 character_registry 条目都有 |
| 场景样图 | 每个 scene_registry 条目都有 |
| 用户确认 | **确认后角色和场景描述锁定** |

### Stage 5: `generate` — 分镜表 → 全量图片

- **工具**: `image_selector`（使用 Stage 4 锁定的 prompt 模板 + 角色参考图批量生成）
- **产出**: `asset_manifest`
- **审批**: 否（自动生成，因为角色/场景已在 preview 确认）

#### 质量门 G5

| 检查项 | 要求 |
|--------|------|
| panel 图片 | 所有图片都存在且可读 |
| style_lock | 所有图片使用相同 style_lock |
| 预算 | ≤ 90%（如有预算设置） |

### Stage 6: `caption` — 在图片上叠加文字

- **两种文字分开处理**:
  1. **`text_overlay`（叙事文字）**: 用 PIL 渲染钩子标题、对话气泡、内心 OS、强调字、旁白到图片上
  2. **`scene_texts` 中 `post_only` 类型**: 对 AI 画不出来的场景文字（手机屏幕、微信界面、长段文字），用 PIL 合成到画面指定位置（含透视变换匹配角度）
  3. **`scene_texts` 中 `ai_draw` 类型**: 检查 AI 画出来的文字是否清晰——清晰则保留，乱码则改为 PIL 覆盖
- **逐张展示带文字的图片**，用户审核文字位置、大小、可读性
- **工具**: Python PIL/Pillow + FFmpeg drawtext
- **产出**: `captioned_assets`（带有文字的最终图片）
- **审批**: 是（**关键质量门**，文字排版效果确认）

#### 质量门 G6

| 检查项 | 要求 |
|--------|------|
| captioned 图片 | 所有图片存在 |
| 文字对比度 | ≥ 4.5:1 |
| 文字位置 | 遵循 comic-typography.md 规则 |
| ai_draw 文字 | 清晰可读，乱码则改为 PIL 覆盖 |

### Stage 7: `compose` — 验证 + 打包图片序列

- **流程**:
  1. 验证所有 captioned 图片完整性（存在、可读、无损坏）
  2. 统一命名并按 panel_number 排序（`panel_01.png`, `panel_02.png`, ...）
  3. 验证分辨率一致性（所有图片尺寸相同）
  4. 生成 `render_report`：图片列表 + 分辨率 + 总数 + 质量摘要
  5. 将最终图片序列输出到 `projects/<name>/renders/` 目录
- **工具**: Python 文件验证（无需 `video_compose`）
- **产出**: `render_report` + 图片序列文件（`renders/panel_*.png`）
- **审批**: 否

#### 质量门 G7

| 检查项 | 要求 |
|--------|------|
| 图片完整性 | 所有 captioned 图片存在且可读（PIL 验证无损坏） |
| 分辨率一致 | 所有图片宽高完全相同 |
| IP 结尾 | 最后一张图包含 IP 结尾 |
| 文件命名 | `panel_XX.png` 按 panel_number 顺序排列 |
| 图片总数 | 与 shot_list 的 panel 数量一致 |

### FINAL 门

| 检查项 | 要求 |
|--------|------|
| 端到端 | 角色一致性、排版效果、画风统一、IP 结尾出现在最后一张图 |

---

## shot_list Schema 设计

```json
{
  "art_style": "warm_illustration",
  "panels": [
    {
      "panel_number": 1,
      "duration_seconds": 4,
      "visual_description": "Seedream 生图用的画面描述",
      "character_anchors": ["妈妈的视觉锚定描述"],
      "scene_template": "场景模板前缀",
      "scene_texts": [
        {
          "content": "老王杂货",
          "carrier": "木质招牌",
          "length": 4,
          "method": "ai_draw"
        }
      ],
      "text_overlay": {
        "content": "画面上的叙事文字（钩子/旁白/对话）",
        "position": "center_top | speech_bubble | corner | bottom | emphasis",
        "style": "bold_title | body | whisper | impact | narration",
        "font_size": "60",
        "color": "#FFFFFF",
        "stroke": "#000000"
      },
      "style_lock": ["画风关键词"]
    }
  ],
  "ip_outro": { "..." },
  "character_registry": { "..." },
  "scene_registry": { "..." }
}
```

**两种文字，两种处理方式：**

| 字段 | 是什么 | 例子 | 谁处理 |
|------|--------|------|--------|
| `scene_texts` | 场景**自带**的文字（融在画面里）| 杂货店招牌、路牌、书封、手机屏幕内容 | **AI 画** 或 PIL 局部修补 |
| `text_overlay` | 叠加在画面**之上**的叙事文字 | 钩子标题、对话气泡、内心 OS、旁白 | **Stage 6 caption** 后期叠加 |

### 场景文字处理策略（`scene_texts`）

在 `shot-plan` 阶段，导演根据文字类型自动决定处理方式：

| 场景 | 方法 | 说明 |
|------|:---:|------|
| 招牌/路牌（1-5字） | `ai_draw` | Seedream 4.0 可胜任，prompt 明确写材质+内容+字号 |
| 书封/海报标题（3-8字） | `ai_draw` | 尝试 AI 画，caption 阶段检查：清晰则保留，乱码则 PIL 覆盖 |
| 手机屏幕内容 | `post_only` | AI 不可能画对，生成空白屏幕 → PIL 合成文字 |
| 微信聊天界面 | `post_only` | 用固定场景模板（白色聊天背景+气泡）→ PIL 叠加消息 |
| 长段文字（>10字） | `post_only` | 绝对不走 AI，全部 PIL 后期合成 |

**对于 `ai_draw` 方法的 prompt 增强规则**（`shot-plan-director.md` 中定义）：
- 引号包裹文字：`...写着'老王杂货'四个字`
- 描述载体材质：`木质招牌上...` `白色油漆字体`
- 结尾加质量词：`清晰可读的汉字` `clear Chinese characters`
- 字数 ≤ 5 时成功率 > 80%；超过 5 字自动降级为 `post_only`

**对于 `post_only` 方法的处理**（`caption-director.md` 中定义）：
- 生成不含关键文字的图（如"手机屏幕空白界面"）
- 在 caption 阶段用 PIL 将文字合成到指定位置
- 对于需要透视/倾斜的文字（如斜着的招牌），使用 PIL 透视变换匹配角度

---

## 画风 Playbook 详细设计

### Playbook 与 StoryFactory 的关系

StoryFactory 的 `STYLE_PRESETS` Python dict（`tools/writing/story_factory.py`）**保留不删**——CLI 直接使用且 `suggested_style` 字段依赖它。两者为**共存关系**：
- `STYLE_PRESETS` = 运行时的快速访问（CLI + 内部逻辑）
- `styles/*.yaml` Playbooks = Pipeline EP 阶段的正式画风来源（通过 `playbook_loader` 加载）
- 两者数据一致，维护时需同步更新

### STYLE_PRESETS → Playbook 字段映射

| StoryFactory Python 字段 | Playbook YAML 位置 | 转换方式 |
|--------------------------|-------------------|---------|
| `STYLE_PRESETS[x]["color_palette"]` | `visual_language.color_palette` | 描述性文字 → `primary`/`accent`/`background`/`text`/`muted` 数组 |
| `STYLE_PRESETS[x]["mood"]` | `identity.mood` | 直接使用 |
| `STYLE_PRESETS[x]["lighting"]` | `asset_generation.image_prompt_prefix` | 合并到前缀描述中 |
| `STYLE_PRESETS[x]["seedream_keywords"]` | `asset_generation.image_prompt_prefix` | 用逗号连接为自然语言前缀字符串 |

### Playbook 共性模板

所有 5 个漫画 playbook 共享以下结构：

```yaml
# === 所有漫画 playbook 共性 ===

identity:
  category: comic                    # 新增的 category 枚举值
  pace: moderate                     # 漫画视频统一节奏
  best_for: "60秒抖音/快手/小红书漫画短视频"

# 音频：漫画流水线不使用 TTS 和音乐
audio:
  voice_style: "none"
  music_mood: "none"
  music_volume: 0
  sfx_style: "none"
  ducking_threshold_db: -20

# 图片生成：漫画特化
asset_generation:
  image_negative_prompt: "photorealistic, 3D render, photograph, realistic photo"
  consistency_anchors:
    - "角色描述从 character_registry 逐字复用到每个 prompt"
    - "场景模板前缀从 scene_registry 逐字复用到每个 prompt"
    - "style_lock 关键词追加到每个 prompt 末尾"
  diagram_style: "none"

# 质量规则：漫画特化
quality_rules:
  - "所有角色在所有画面中必须使用完全相同的角色锚定描述"
  - "所有画面必须包含 style_lock 关键词"
  - "场景模板前缀在相同场景的所有画面中必须字面一致"
  - "文字叠加不得遮挡角色面部表情"
  - "画面内文字（scene_texts）≤5字用 ai_draw，>5字用 post_only"
```

### 5 个 Playbook 的个性字段

**`styles/warm-illustration.yaml`**（温暖手绘）
```yaml
identity:
  name: "Warm Illustration"
  mood: warm, healing, slice-of-life, gentle
  best_for: "亲情、治愈、日常、温暖瞬间"
visual_language:
  color_palette:
    primary: ["#E8D5B7", "#D4A574"]       # 米色、浅橙
    accent: ["#8B5E3C", "#C17F59"]        # 深棕、焦糖
    background: "#FFF8F0"                  # 暖白
    text: "#4A3728"                        # 深棕文字
    muted: "#D4C4B0"                       # 浅驼
  composition: 居中构图，暖色调笼罩，人物与背景融合度高
  texture: 柔和手绘质感，水彩边缘，笔触可见但不突兀
asset_generation:
  image_prompt_prefix: "温暖插画风格, 柔和色调, 手绘质感, 日式生活插画, 温馨氛围, 柔和线条, 柔和自然光, 午后暖阳"
```

**`styles/clean-comic.yaml`**（现代漫画风）
```yaml
identity:
  name: "Clean Comic"
  mood: light, humorous, modern, playful
  best_for: "搞笑、社死、段子、打工人日常"
visual_language:
  color_palette:
    primary: ["#FFFFFF", "#F5F5F5"]       # 白色、浅灰
    accent: ["#FF4444", "#44AA44", "#4488FF"]  # 红、绿、蓝点缀
    background: "#FFFFFF"
    text: "#222222"
    muted: "#CCCCCC"
  composition: 清晰前景，简洁背景，人物占画面主体，留白充足
  texture: 干净线条，无杂色，平涂色块，边线清晰
asset_generation:
  image_prompt_prefix: "现代漫画风格, 干净的线条, 明亮的色彩, 简笔画, 幽默感, 表情夸张, 均匀明亮光线"
```

**`styles/cinematic-drama.yaml`**（电影感暗调）
```yaml
identity:
  name: "Cinematic Drama"
  mood: tense, suspenseful, dramatic, intense
  best_for: "悬疑、反转、紧张、深度故事"
visual_language:
  color_palette:
    primary: ["#1A1A2E", "#16213E"]       # 深蓝
    accent: ["#C62828", "#FF6F00"]        # 暗红、深橙
    background: "#0D0D1A"                  # 近黑
    text: "#E8E8E8"                        # 浅灰文字
    muted: "#4A4A5A"                       # 暗灰
  composition: 大面积暗调，光源集中，人物在光影中，景深明显
  texture: 精细笔触，高细节渲染，暗部有噪点质感
asset_generation:
  image_prompt_prefix: "电影感插画, 高对比度, 戏剧性光影, 暗调画面, 氛围感, 细节丰富, 侧光逆光, 明暗对比强烈"
```

**`styles/watercolor-nostalgia.yaml`**（水彩怀旧）
```yaml
identity:
  name: "Watercolor Nostalgia"
  mood: nostalgic, wistful, gentle, emotional
  best_for: "时光、回忆、感动、青春纪念"
visual_language:
  color_palette:
    primary: ["#D4C5A9", "#BFA882"]       # 褪色暖色
    accent: ["#8B7355", "#A67B5B"]        # 复古棕
    background: "#F5EFE0"                  # 旧纸色
    text: "#5C4A32"                        # 深棕文字
    muted: "#C9B99A"                       # 浅米
  composition: 柔焦边缘，画面有"记忆"感，时光流逝的意境
  texture: 水彩晕染边缘，淡彩笔触，像褪了色的老照片
asset_generation:
  image_prompt_prefix: "水彩插画, 怀旧色调, 梦幻质感, 柔和笔触, 时光感, 温暖回忆, 梦幻柔光, 纱帘阳光"
```

**`styles/ink-dramatic.yaml`**（水墨黑白）
```yaml
identity:
  name: "Ink Dramatic"
  mood: intense, impactful, dramatic, powerful
  best_for: "反转、冲击、深度、力量感"
visual_language:
  color_palette:
    primary: ["#000000", "#333333"]       # 黑、深灰
    accent: ["#CC0000", "#990000"]        # 少量红色点缀
    background: "#F5F0EB"                  # 宣纸白
    text: "#111111"                        # 近黑文字
    muted: "#888888"                       # 灰
  composition: 大面积留白与浓墨对比，视觉焦点集中，极简有力
  texture: 水墨晕染，干笔飞白，版画质感，东方美学
asset_generation:
  image_prompt_prefix: "黑白水墨风格, 强烈对比, 极简色彩, 版画质感, 视觉冲击, 东方美学, 强烈明暗对比, 像木版画"
```

### 配套代码修改

| 文件 | 改动 |
|------|------|
| `schemas/styles/playbook.schema.json` | `identity.category` 枚举添加 `"comic"` 和 `"anime-illustration"` |
| `styles/playbook_loader.py` | `list_playbooks()` 额外扫描 `styles/custom/*.yaml`；`load_playbook()` fallback 到 `styles/custom/` |
| `styles/custom/.gitkeep` | 创建空目录，存放用户自定义画风预设 |

---

## 已完成的组件

### Phase 1: Story Factory

`tools/writing/story_factory.py`（BaseTool 子类），零外部依赖，纯本地运行。

- **5 种生成模式**: emotion_matrix、what_if、daily_catch、random、batch
- **12 个叙事模式**: 针对抖音漫画优化的故事结构（身份反转、误会连环、日常英雄等）
- **5 拍叙事结构**: HOOK → BUILD → CONFRONT → REVEAL → RESOLVE，比例化适配任意时长
- **输出**: story_seed（hook、5 拍含时间码和视觉建议、角色原型含 visual_notes、建议画风含 seedream_keywords）

### Phase 2: 一致性 + 排版 + IP

三个配套 skill 文件，在 shot-plan 和 caption 阶段被自动读取：

- **`skills/creative/character-consistency.md`**: 角色锚定描述模板（面部、发型、体型、穿着）+ Seedream 参考图模式 + 场景模板库
- **`skills/creative/comic-typography.md`**: 多样化文字位置（钩子标题、对话气泡、内心 OS、旁白、情绪强调、结尾 IP）+ 字体/大小/安全区规范
- **`skills/creative/personal-ip.md`**: 固定结尾模板（讲述者角色 + 签名语 + 关注引导）+ 品牌色/签名元素

---

## 需要创建和修改的文件

### Pipeline 清单
| 文件 | 说明 |
|------|------|
| `pipeline_defs/comic-story.yaml` | 流水线清单定义（7 阶段） |

### Artifact Schema
| 文件 | 说明 |
|------|------|
| `schemas/artifacts/style_decision.schema.json` | 画风选择 Schema（支持预设或参考图模式） |
| `schemas/artifacts/shot_list.schema.json` | 分镜表 JSON Schema |
| `schemas/artifacts/preview_manifest.schema.json` | 角色定妆 + 场景样图 Schema |
| `schemas/artifacts/captioned_assets.schema.json` | 文字叠加产出 Schema |

### 画风 Playbook
| 文件 | 说明 |
|------|------|
| `styles/warm-illustration.yaml` | 温暖手绘 |
| `styles/clean-comic.yaml` | 现代漫画风 |
| `styles/cinematic-drama.yaml` | 电影感暗调 |
| `styles/watercolor-nostalgia.yaml` | 水彩怀旧 |
| `styles/ink-dramatic.yaml` | 水墨黑白 |

### 自定义画风目录
| 文件 | 说明 |
|------|------|
| `styles/custom/.gitkeep` | 自定义画风存放目录占位 |

### 需要修改的文件
| 文件 | 改动 |
|------|------|
| `schemas/styles/playbook.schema.json` | identity.category 枚举添加 "comic", "anime-illustration" |
| `schemas/artifacts/__init__.py` | ARTIFACT_NAMES 添加 style_decision, shot_list, preview_manifest, captioned_assets |
| `lib/checkpoint.py` | ALL_KNOWN_STAGES 添加 comic 阶段名；CANONICAL_STAGE_ARTIFACTS 添加映射 |
| `styles/playbook_loader.py` | list_playbooks / load_playbook 支持 styles/custom/ 子目录 |

---

## 如何使用

在 Claude Code 中直接说类似：

```
"用 comic-story 流水线，帮我把这段文字变成漫画视频：[段子内容]"
"用 comic-story 流水线，从这个视频获取灵感：[URL]"
"帮我创作一期关于'加班的温暖瞬间'的漫画"
```

Agent 会自动逐阶段执行，每个关键节点暂停等待确认：

1. **`ideate`** → 生成 3-5 个故事种子，让用户选一个
2. **`style-pick`** → 展示画风预设，用户选择或提供参考图锁定视觉风格
3. **`shot-plan`** → 自动读取三个配套 skill，生成完整分镜表（用户审核）
4. **`preview`** → 生成角色三视图 + 场景样图，用户确认像不像/对不对
5. **`generate`** → 批量生成所有图片（角色/场景已锁定，自动进行）
6. **`caption`** → 在图片上叠加文字，用户审核文字位置和效果
7. **`compose`** → 验证图片完整性、统一命名、输出图片序列 → `projects/<name>/renders/panel_*.png`

---

## 实施顺序

### ✅ Phase 1: Story Factory（已完成）
1. ~~创建 `tools/writing/__init__.py`~~
2. ~~创建 `tools/writing/_patterns.py` — 12 个故事模式~~
3. ~~创建 `tools/writing/_emotion_matrix.py` — 情绪矩阵~~
4. ~~创建 `tools/writing/_whatif_engine.py` — What-if 引擎~~
5. ~~创建 `tools/writing/story_factory.py` — 主工具~~
6. ~~创建 `schemas/artifacts/story_seed.schema.json`~~
7. ~~更新 `schemas/artifacts/__init__.py`~~
8. ~~创建 `scripts/story_idea.py`~~

### ✅ Phase 2: 一致性 + 排版 + IP（已完成）
9. ~~创建 `skills/creative/character-consistency.md`~~
10. ~~创建 `skills/creative/comic-typography.md`~~
11. ~~创建 `skills/creative/personal-ip.md`~~

### 🔲 Phase 3: Schema 与注册
12. 修改 `schemas/styles/playbook.schema.json` — identity.category 添加 "comic", "anime-illustration"
13. 创建 `schemas/artifacts/style_decision.schema.json`
14. 创建 `schemas/artifacts/shot_list.schema.json`
15. 创建 `schemas/artifacts/preview_manifest.schema.json`
16. 创建 `schemas/artifacts/captioned_assets.schema.json`
17. 修改 `schemas/artifacts/__init__.py` — ARTIFACT_NAMES 添加 4 个新 schema
18. 修改 `lib/checkpoint.py` — ALL_KNOWN_STAGES + CANONICAL_STAGE_ARTIFACTS 添加 comic 阶段

### 🔲 Phase 4: 画风 Playbook YAML
19. 创建 `styles/warm-illustration.yaml`
20. 创建 `styles/clean-comic.yaml`
21. 创建 `styles/cinematic-drama.yaml`
22. 创建 `styles/watercolor-nostalgia.yaml`
23. 创建 `styles/ink-dramatic.yaml`
24. 创建 `styles/custom/.gitkeep`
25. 修改 `styles/playbook_loader.py` — 支持 custom/ 子目录

### 🔲 Phase 5: Pipeline Manifest
26. 创建 `pipeline_defs/comic-story.yaml`

### 🔲 Phase 6: 验证
27. Pipeline manifest 加载验证
28. Schema 验证
29. Playbook 验证
30. Checkpoint 阶段识别验证

---

## 验证方式

```bash
# 1. 流水线清单验证
python -c "
from lib.pipeline_loader import PipelineLoader
loader = PipelineLoader()
manifest = loader.load('comic-story')
print(f'流水线: {manifest[\"name\"]}, {len(manifest[\"stages\"])} 个阶段')
for s in manifest['stages']:
    print(f'  [{s[\"name\"]}] → {s[\"produces\"]} 审批: {s[\"human_approval_default\"]}')
"

# 2. Schema 验证
python -c "
from schemas.artifacts import validate_artifact, list_schemas
names = list_schemas()
for n in ['style_decision','shot_list','preview_manifest','captioned_assets']:
    assert n in names, f'{n} missing!'
print('All 4 new schemas registered')
validate_artifact('style_decision', {
    'version':'1.0','mode':'preset','style_lock':['a','b','c'],
    'image_prompt_prefix':'test','consistency_anchors':['x']
})
print('style_decision validates OK')
"

# 3. Playbook 验证
python -c "
from styles.playbook_loader import load_playbook, list_playbooks, validate_playbook
names = list_playbooks()
for p in ['warm-illustration','clean-comic','cinematic-drama','watercolor-nostalgia','ink-dramatic']:
    assert p in names, f'{p} not found in {names}'
    pb = load_playbook(p)
    assert pb['identity']['category'] == 'comic'
    validate_playbook(pb)
    print(f'{p}: OK (mood={pb[\"identity\"][\"mood\"]})')
"

# 4. Checkpoint 阶段识别
python -c "
from lib.checkpoint import ALL_KNOWN_STAGES, CANONICAL_STAGE_ARTIFACTS
comic_stages = ['ideate','style_pick','shot_plan','preview','generate','caption','compose']
for s in comic_stages:
    assert s in ALL_KNOWN_STAGES, f'{s} not in ALL_KNOWN_STAGES'
    if s in CANONICAL_STAGE_ARTIFACTS:
        print(f'{s} → {CANONICAL_STAGE_ARTIFACTS[s]}')
    else:
        print(f'{s} (uses existing mapping)')
"
```

5. **端到端验证**：从文本/视频 → 故事种子 → 画风选择 → 分镜 → 角色定妆 → 全量生图 → 文字叠加 → 图片序列输出，走通完整流程。检查：角色一致性、文字排版、画风统一、IP 结尾出现在最后一张图、图片序列完整且分辨率一致。

目标：建立一套完整的漫画创作系统，让选题不再靠灵感，让产出质量稳定可控。
