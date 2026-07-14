---
name: healing-text-prompt-guide
description: |
  Healing-text pipeline 专属提示词工程指南。融合 Seedance 中文视频提示词最佳实践、
  Seedream 高质量图片提示词模式、FPV 沉浸式镜头语言和反 slop 审美原则。
  MANDATORY: Asset director must read this BEFORE writing any generation prompt.
---

# Healing-Text 提示词工程指南

## 核心原则

治愈系视频的本质是：**让风景替人说话**。文字是灵魂，画面是呼吸。
所有提示词服务于一个目标——让观众感受到文字背后的情绪，而不是被画面分散注意力。

## 一、图片提示词（Seedream）

### 1.1 提示词结构（归藏方法论 — Seedream 验证有效）

```
[格式声明]：[场景主体 —— 从远到近分层]。
[光影与氛围 —— 集中写在 1-2 句]。
[构图与留白 —— 精确到位置和比例]。
[风格与质感 —— 集中声明在末尾]。
```

**每条 prompt 必须包含：**
- 格式声明开头："一张针对[主题]的治愈系风光摄影作品"
- 分层场景：远景 → 中景 → 前景 → 微距细节
- 光影集中写：光源方向 + 光线质感 + 大气效果
- 留白精确声明："画面上方三分之一留白" 而非 "negative space"
- 风格集中末尾：电影调色参考 + 画质关键词

### 1.2 治愈系图片模板

**模板 A — 壮阔自然（用于开场/高潮）：**
```
[具体地点]的[时刻]，[天气现象]，[光线如何进入画面]。
前景[具体元素]，中景[层次]，远景[氛围]。
构图[广角/中景/特写]，画面[上方/中央/下方]留白用于叠加文字。
[质感细节]：[水面波纹/树叶飘落/云雾流动/光斑]。
```

**模板 B — 静物/微观（用于安静段落）：**
```
微距镜头，[具体物体]在[环境]中。
[光线]从[方向]柔和洒落，在[表面]投下[阴影形状]。
浅景深，背景完全虚化为[色调]色块。
画面[构图比例]留白。
```

**模板 C — 氛围空镜（用于过渡/落地）：**
```
[地点]的[季节]。[天气]下的[场景]。
没有人物，只有[动态元素]轻轻[动作]。
色调[具体色彩倾向]，整体像[胶片类型/名画/著名摄影风格]。
安静、空旷、呼吸感。
```

### 1.3 治愈系常见场景关键词库

| 情绪 | 场景元素 | 光线 | 色调 |
|------|---------|------|------|
| 自由/坚定 | 山顶、悬崖、孤树、鹰、天际线 | 逆光、剪影、晨光破云 | 金色 + 深蓝 |
| 挣扎/内省 | 逆流的落叶、雨窗、独木舟、迷宫小径 | 阴天柔光、暗角光束 | 冷蓝 + 暖琥珀 |
| 觉醒/突破 | 碎裂的冰面、破茧、日出、闪电、隧道出口 | 裂缝漏光、丁达尔 | 冰蓝 + 爆裂金 |
| 释然/接纳 | 静水倒影、漂浮、晚霞、白鸽 | 暮光、水平光 | 暖橙 + 柔紫 |
| 平静/治愈 | 樱花飘落、溪流、麦田、树影婆娑 | 斑驳柔光、逆光光斑 | 粉白 + 暖绿 |

### 1.4 插画风图片模板（治愈插画风 / 文学摄影风）

> 当 `script.metadata.selected_playbook` 为 `warm-illustration` 或
> `literary-illustration` 时使用此模板，替代上面的摄影风格模板。
> 读取对应 playbook 的 `asset_generation.image_prompt_prefix` 和 `style_lock` 关键词。

**通用结构（插画风）：**
```
[playbook.image_prompt_prefix]。
[场景主体 —— 具体到角色动作/物体/环境细节，用中文自然描述]。
[光影与氛围 —— 柔和自然光描述]。
[构图与留白 —— 画面中央偏上大面积留白用于叠加文字]。
[playbook.style_lock 关键词（逐字复制）]。
```

**模板 D — 治愈插画风 (warm-illustration)：**

读取 `styles/warm-illustration.yaml` 的 `image_prompt_prefix`：
```
温暖插画风格, 柔和色调, 手绘质感, 日式生活插画, 温馨氛围, 柔和线条, 柔和自然光, 午后暖阳
```

完整示例：
```
温暖插画风格, 柔和色调, 手绘质感, 日式生活插画, 温馨氛围, 柔和线条, 柔和自然光, 午后暖阳,
午后窗台上一只橘猫蜷缩在阳光里，旁边放着一杯冒着热气的奶茶，
窗台上还散落着几本翻开的旧书，窗外是模糊的绿色树影随风轻摇，
柔和自然光从左侧洒入，午后暖阳色调在猫毛上泛起金色的光晕，
画面中央偏上大面积留白用于叠加文字，温馨治愈的呼吸感。
```

**模板 E — 文学摄影风 (literary-illustration)：**

读取 `styles/literary-illustration.yaml` 的 `image_prompt_prefix`：
```
轻文艺插画风格, 莫兰迪灰调配色, 奶油纸张底色, 炭灰色手工线条, 大面积留白, 静谧克制氛围, 做旧纸质肌理, 极简角色设计, 散文书籍插画质感
```

完整示例：
```
轻文艺插画风格, 莫兰迪灰调配色, 奶油纸张底色, 炭灰色手工线条,
大面积留白, 静谧克制氛围, 做旧纸质肌理, 极简角色设计, 散文书籍插画质感,
雨后的青石板小路，一把透明雨伞靠在木门边，远处是模糊的黛色山影，
门框上挂着几片湿润的绿叶，石板路上倒映着天空的灰蓝色，
柔和的灰调光线，空气中弥漫雨后泥土气息，
画面中央大面积奶油色留白用于叠加文字，像翻开一本散文集的内页。
```

**插画风关键词规则：**

- **必须**包含 playbook 的 `image_prompt_prefix`（逐字复制）
- **必须**包含 playbook 的 `style_lock` 关键词（如有 — `literary-illustration` 有）
- **必须**声明留白位置：`画面中央偏上大面积留白用于叠加文字`
- 负面约束使用 playbook 的 `image_negative_prompt`
- **不要**出现 `photorealistic`、`Hasselblad`、`8K resolution`、`35mm film` 等摄影术语
- **不要**出现 `negative space`（用中文 `留白` 代替）
- 场景描述**必须是中文自然语言**（"午后窗台上" > "afternoon windowsill"）

> **注意：** 上面的模板 A/B/C（摄影风格）仅在 `selected_playbook` 为 `cinematic-drama`
> 或未设置时使用。`warm-illustration` 和 `literary-illustration` 必须使用模板 D/E。

## 二、视频提示词（Seedance 2.0 image_to_video）

**本 Pipeline 使用 image_to_video 生成所有视频片段。**
图片已经锁定了构图 —— 视频 prompt 只描述运动。

### 2.1 核心原则

视频 prompt 只写三件事：
1. **镜头声明 + 否定**（第一句）：`One continuous shot, locked tripod, no push-in, no dolly, no pan, no tilt, no zoom, no cuts`
2. **逐秒运动描述**（主体）：`0-2s: stillness... 2-4s: RAMPS TO SLOW MOTION as [movement]...`
3. **负面约束**（结尾）：`no 3D, no cartoon, no VFX aesthetic, no camera movement...`

**不要**重复描述场景 —— 图片已经定义了场景，重复描述会让 Seedance 困惑。

### 2.2 图生视频模板

```
One continuous shot, [camera identity + what it ISN'T doing].
Photorealistic, 35mm film grain, no 3D, no cartoon, no VFX aesthetic.

Beat-by-beat:
0-2s: [初始状态 —— 画面静止或最微小的运动，建立氛围]
2-4s: [核心运动 —— 用 ALL CAPS 标记动作动词：RAMPS TO SLOW MOTION, DRIFTS, SPREADS]
4-5s: [收尾 —— 运动 STABILIZES，画面 HOLD 在新状态]

Visual quality: [film stock reference].
no music, no audio — silent clip.
[负面约束清单]
```

### 2.3 治愈系镜头运动词典

| 场景 | 镜头运动 | 速度 |
|------|---------|------|
| 远景山脉 + 云雾 | 静态三脚架，让云自己流动 | 0 |
| 水面倒影 + 涟漪 | 极缓慢下降（crane down），接近水面 | 极慢 |
| 阳光穿过树叶 | 静态，让光斑自然晃动 | 0 |
| 花瓣飘落 | 极缓慢向上仰拍（tilt up），跟随一片花瓣 | 极慢 |
| 冰面碎裂 | 静态三脚架 + 极缓推近（slow push-in），让裂痕自然扩散 | 极慢 |

**治愈系禁止的镜头：**
- 手持晃动、快速摇镜、快速推拉、跳切、旋转、鱼眼、希区柯克变焦
- 任何超过 1x 的缩放

### 2.4 负面约束清单（每次都要加）

```
不要 3D 渲染，不要卡通，不要 AI 塑料感，
不要快速镜头运动，不要手持晃动，不要跳切，
不要人物，不要文字，不要 Logo，不要 UI 元素，
不要超现实特效，不要科幻感，不要恐怖元素，
不要色彩过饱和，不要高对比度。
```

## 三、图生视频提示词（本 Pipeline 唯一视频路径）

图生视频的 prompt **只描述运动**，不需要重复场景。
图片已经锁定了构图和色调 —— Seedance 只需要知道"动什么、怎么动"。

### 3.1 模板

```
One continuous shot, [camera identity: locked tripod / slow crane / static POV],
no push-in, no dolly, no pan, no tilt, no zoom, no cuts.
Photorealistic, 35mm film grain, no 3D, no cartoon, no VFX aesthetic.

Beat-by-beat:
0-2s: [初始状态，几乎静止，氛围建立]
2-4s: [核心运动 —— 用 ALL CAPS 标记：RAMPS TO SLOW MOTION / DRIFTS / SPREADS / GLOWS]
4-5s: [收尾 —— 运动 STABILIZES，画面 HOLD]

Visual quality: [Fujifilm Pro 400H / Kodak Portra 400] color science.
no music, no audio — silent clip.
no camera movement, no people, no text, no logos, no buildings.
```

### 3.2 运动幅度指南

| 场景类型 | 运动内容 | 幅度 |
|---------|---------|------|
| 水面/涟漪 | 波纹扩散、倒影晃动 | 微小 |
| 云/雾 | 飘移、翻涌、消散 | 微小-适度 |
| 光 | 光斑晃动、光束移动、亮度变化 | 微小 |
| 叶/花瓣 | 飘落、摇曳、旋转 | 微小 |
| 冰/雪 | 碎裂扩散（慢动作）、飘落 | 适度 |
| 瀑布/溪流 | 水流持续运动 | 自然流动 |

**原则：幅度永远偏小。治愈系不需要剧烈运动。让人发现"原来画面在动"比"画面动得很厉害"高级得多。**

## 四、反 AI-Slop 检查清单

### Phase 1 — 图片 prompt 自查

- [ ] 是否用中文写 prompt？Seedream 是中文模型
- [ ] 场景描述是否像描述一张亲眼见过的照片，而非堆砌摄影术语？
- [ ] 是否描述了具体时刻、地点、天气、季节？（"四月京都哲学之道" > "cherry blossom pond"）
- [ ] 是否明确了留白位置和比例？
- [ ] 画面中是否确保没有人物？
- [ ] 是否避免了 "cinematic photography"、"8K"、"Hasselblad" 等空洞词汇？

### Phase 2 — 视频 prompt 自查

- [ ] 是否以 shot-structure 声明开头？（`One continuous shot, locked tripod...`）
- [ ] 是否同时声明了相机 IS 和 ISN'T 做什么？（`no push-in, no dolly, no pan...`）
- [ ] 是否包含 realism enforcement？（`no 3D, no cartoon, no VFX aesthetic — photorealistic textures...`）
- [ ] 是否用了 beat-by-beat 时间轴 + ALL CAPS 动作标记？
- [ ] 是否没有重复描述场景？（场景已经由图片定义了）
- [ ] 运动幅度是否符合治愈系要求？（微小/适度，不剧烈）
- [ ] 是否以 `no music, no audio — silent clip` 和完整负面约束结尾？

## 五、示例：完整的 Phase 1 图片 + Phase 2 视频 Prompt

### 图片 prompt（Phase 1 — Seedream）

```
清晨五点半，黄山狮子峰崖边。脚下云海翻涌如白色海洋漫过悬崖边缘，
晨光从东方云层裂缝中射出数道金色光柱。一棵孤松扎根在崖边岩石上，
松针挂着晨露逆光闪烁，晶莹剔透。远处群峰如岛屿浮在云海之上，
层层叠叠隐入晨雾。广角横幅，画面上方三分之一是淡金色天空留白，
用于叠加文字。空气中可见细小水雾在光束中漂浮，晨光暖金色调，
安静而壮阔。整体像黄山画派的水墨意境与风光摄影的结合，有呼吸感。
```

### 视频 prompt（Phase 2 — Seedance image_to_video）

拿到用户确认的图片后，写运动 prompt。**只描述运动，不重复场景：**

```
One continuous shot, locked tripod perspective, static camera —
no push-in, no dolly, no pan, no tilt, no zoom, no cuts,
no handheld movement of any kind.
Photorealistic, 35mm film grain, anamorphic lens characteristics,
subtle halation on highlights,
no 3D, no cartoon, no VFX aesthetic —
photorealistic textures, authentic natural lighting, grounded in reality.

Beat-by-beat:
0-2s: Absolute stillness. Clouds below the cliff edge DRIFT slowly,
rolling like a white ocean in extreme slow motion.
First golden light beams PIERCE through the cloud layer.
Ice crystals and mist particles SUSPENDED in the air, barely moving.
2-4s: The sea of clouds SURGES gently over the cliff edge,
cascading downward like a slow-motion waterfall.
Golden light beams INTENSIFY and SHIFT angle subtly as the sun rises.
The lone pine's needles CATCH the backlight, GLOWING at the edges.
4-5s: Cloud movement STABILIZES into a gentle, breathing rhythm.
Light beams HOLD steady. The frame SETTLES into perfect stillness
— the same composition as the first frame, now alive with subtle motion.

Visual quality: Fujifilm Pro 400H color science — warm amber light
contrasting with cool blue shadows in the cloud depths.
Fine film grain throughout. Shallow depth of field on the pine needles.

no music, no audio — silent clip.

no 3D rendering, no cartoon, no VFX aesthetic,
no camera movement of any kind, no cuts, no zoom,
no people, no text, no logos, no buildings,
no oversaturated colors, no high contrast.
```

**关键点：视频 prompt 里完全没有"山顶""孤松""云海"这些词 —— 图片已经定义了这些。Seedance 只需要知道云怎么动、光怎么变、镜头怎么（不）动。**
