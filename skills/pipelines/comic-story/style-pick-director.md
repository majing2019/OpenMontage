# Style-Pick Director — Comic-Story Pipeline

## When To Use

You are the **Style-Pick Director** for the comic-story pipeline. Your job is to determine and lock the visual art style for all panels. The style decision is **immutable after this stage** — every downstream stage uses the same `style_lock` keywords.

You have three modes:
- **Preset mode**: User picks from 6 built-in comic presets
- **Reference image mode**: User provides image(s) to extract style from
- **Reference video mode**: User provides video to extract style from

## Reference Inputs

- `EP_STATE.reference_video_analysis` — 5-dimension analysis from ideate stage (if video input)
- `styles/warm-illustration.yaml` — Warm illustration preset
- `styles/warm-storybook.yaml` — Warm storybook preset (暖调故事感)
- `styles/clean-comic.yaml` — Clean comic preset
- `styles/korean-webtoon.yaml` — Korean webtoon preset (韩式网漫)
- `styles/literary-illustration.yaml` — Literary illustration preset (轻文艺插画)
- `styles/line-comic.yaml` — Line comic preset (黑白线条漫画)
- `styles/classic-manga.yaml` — Classic manga preset (日系经典漫画)
- `styles/cinematic-drama.yaml` — Cinematic drama preset
- `styles/cel-animation.yaml` — Cel animation preset (赛璐璐动画)
- `styles/watercolor-nostalgia.yaml` — Watercolor nostalgia preset
- `styles/new-chinese-ink.yaml` — New Chinese ink preset (新中式水墨)
- `styles/ink-dramatic.yaml` — Ink dramatic preset
- `styles/doodle-journal.yaml` — Doodle journal preset (涂鸦手账)
- `styles/rough-print.yaml` — Rough print preset (粗粝版画)
- `styles/collage-papercut.yaml` — Collage papercut preset (拼贴剪纸)
- `styles/vintage-lianhuanhua.yaml` — Vintage lianhuanhua preset (小人书怀旧)
- `styles/pixel-art.yaml` — Pixel art preset (像素风)
- `skills/creative/character-consistency.md` — Character design context for style compatibility

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `story_seed` | Selected story with suggested_style |
| EP State | `reference_video_analysis` | Video analysis (video input mode) |
| Playbooks | `styles/*.yaml` + `styles/custom/*.yaml` | Built-in + custom presets |
| Tool | `image_selector` | Style test image generation |
| Tool | `video_analyzer`, `frame_sampler` | Video style extraction |
| Schema | `style_decision.schema.json` | Output validation |

## Process

### 1. Check for Pre-filled Suggestions

If `EP_STATE.reference_video_analysis` exists (from ideate stage video Path B):

1. Extract color palette, lighting, line style, composition from the analysis
2. Generate Seedream keyword suggestions (e.g., "暖色调, 手绘质感, 柔和线条")
3. Present these as **pre-filled suggestions** to the user alongside the preset list

This gives the user a grounded starting point rather than starting from zero.

### 2. Present Style Options

Show all available styles grouped by emotional direction. With 65 built-in styles across 15 categories, guide the user to a shortlist based on their story's mood:

```
温度感 — 烟火气、治愈、怀旧、柔软
├── 🏠 Warm Illustration — 温暖手绘 (亲情、治愈、日常)
├── 🏠 Warm Storybook — 暖调故事感 (烟火气、打工人、人间冷暖)
├── 📚 Vintage Lianhuanhua — 小人书怀旧 (年代叙事、童年回忆)
├── 🎨 Watercolor Nostalgia — 水彩怀旧 (时光、回忆、感动)
├── 🖍️ Pastel Chalk — 粉彩粉笔 (温柔叙事、少女心、柔软日常)
├── 🧵 Embroidery — 刺绣风 (手工温度、外婆的故事、节日温情)
└── 📰 American Sunday Funnies — 美式星期天漫画 (温馨段子、家庭趣事)

精致感 — 潮流、文艺、动画感、清爽
├── ✨ Korean Webtoon — 韩式网漫 (年轻化、社交传播、都市故事)
├── 📖 Literary Illustration — 轻文艺插画 (情感叙事、深夜独白)
├── 🎬 Cel Animation — 赛璐璐动画 (青春故事、电影感、高颜值)
├── 💬 Clean Comic — 现代漫画风 (搞笑、社死、段子)
├── 🇪🇺 Ligne Claire — 欧式清线漫画 (冒险、科普、清爽叙事)
└── 🔷 Vector Flat — 扁平矢量 (职场吐槽、知识科普、现代生活)

东方古典 — 中国风、日本美学、东方传统
├── 🎋 New Chinese Ink — 新中式水墨 (中国故事、幽默讽刺)
├── 🖌️ Gongbi — 工笔画 (古典故事、精致美学)
├── ⛰️ Shan Shui — 山水画风 (天地辽阔、哲学叙事)
├── 🖊️ Ink Dramatic — 水墨黑白 (反转、冲击、深度)
├── 🎴 Ukiyo-e — 浮世绘 (古典故事、诗意叙事、日式美学)
├── ✂️ Chinese Papercut — 中国剪纸 (民俗故事、节庆吉祥)
└── 🎭 Shadow Puppet — 皮影戏 (民间故事、光影叙事)

戏剧感 — 反差、冲击、张力、暗调
├── 📺 Classic Manga — 日系经典漫画 (夸张表情、戏剧反转)
├── ✏️ Line Comic — 黑白线条漫画 (段子、吐槽、条漫)
├── 🎬 Cinematic Drama — 电影感暗调 (悬疑、反转、紧张)
├── 💀 Charcoal — 碳笔速写 (情感爆发、内心独白)
└── 🎭 Expressionist — 表现主义 (愤怒宣泄、焦虑共鸣、反精致)

手工感 — 笔触、纹理、创作痕迹
├── ✏️ Doodle Journal — 涂鸦手账 (日记体、朋友圈吐槽)
├── 🔪 Rough Print — 粗粝版画 (独立创作、态度表达)
├── ✂️ Collage Papercut — 拼贴剪纸 (创意表达、手工感)
├── 🖨️ Risograph — Riso印刷 (独立杂志感、小众审美)
├── ✏️ Pencil Sketch — 铅笔素描 (心情独白、草稿美学)
├── 📄 Origami Paper — 折纸风 (创意故事、几何美学)
└── 🖤 Scratchboard — 刮板画 (黑白反转、高对比、精细线描)

氛围暗调 — 霓虹、未来、夜色、故障
├── 🌃 Neon Noir — 霓虹暗调 (都市夜话、赛博朋克)
├── 🟣 Synthwave — 合成波复古 (80年代怀旧、复古科技)
├── 🌊 Vaporwave — 蒸汽波 (千禧年互联网、消费主义讽刺)
└── 📺 Glitch Art — 故障艺术 (数字崩溃、赛博故障美学)

波普与设计 — 视觉冲击、风格化、几何美学
├── 🎯 Pop Art — 波普艺术 (讽刺吐槽、反讽幽默、流行文化)
├── 🌸 Art Nouveau — 新艺术运动·穆夏风 (浪漫故事、唯美表达)
├── 🔲 Duotone — 双色调 (态度表达、品牌感、强对比)
├── 🔴 Constructivism — 构成主义 (态度宣言、革命性表达)
├── 🔷 Bauhaus — 包豪斯 (功能美学、理性叙事、几何纯粹)
├── 🟥 De Stijl — 风格派·蒙德里安 (秩序美学、纯粹和谐)
├── 🎨 Fauvism — 野兽派 (自由表达、狂野色彩、打破规则)
└── 🪟 Stained Glass — 彩绘玻璃 (神圣叙事、光与色彩)

萌系与极简 — 可爱、幽默、自黑、低面
├── 🐣 Chibi Q — Q版超萌 (萌系段子、可爱日常)
├── 🚶 Stick Figure — 火柴人 (极简吐槽、自黑幽默)
├── 🕹️ Pixel Art — 像素风 (游戏梗、互联网文化)
└── 💎 Low Poly — 低多边形 (游戏化叙事、3D几何美学)

艺术流派 — 从印象派到超现实
├── 🌅 Impressionism — 印象派 (光影叙事、瞬间美好)
├── 🌻 Van Gogh Style — 梵高风格 (燃烧情感、漩涡笔触)
├── 🌀 Surrealism — 超现实主义 (梦境叙事、荒诞寓言)
└── 🔷 Cubism — 立体主义 (多视角叙事、几何解体)

朋克谱系 — 蒸汽、柴油、太阳
├── ⚙️ Steam Punk — 蒸汽朋克 (奇幻冒险、维多利亚机械)
├── 🏭 Diesel Punk — 柴油朋克 (工业战火、钢板铆接)
└── 🌿 Solar Punk — 太阳朋克 (环保希望、绿色乌托邦)

机甲与科技 — 机械、科幻、工程
├── 🤖 Mecha — 机甲风 (机器人故事、钢铁美学)
└── 📐 Blueprint — 蓝图 (技术科普、工程图纸美学)

民间与世界 — 异域民俗、手工传统
├── 🕌 Persian Miniature — 波斯细密画 (传奇故事、诗意叙事)
├── 🪷 Madhubani — 印度民间画 (自然与生命、异域民俗)
└── 🦴 Cave Art — 岩画风 (寓言故事、原始叙事、神话感)

神秘与游戏 — 塔罗、镶嵌、少女、街头
├── 🔮 Tarot — 塔罗牌 (命运叙事、象征寓言、神秘学)
├── 🧩 Mosaic — 马赛克镶嵌 (永恒叙事、碎片拼合之美)
├── 🌸 Shoujo Manga — 少女漫画 (恋爱故事、少女心)
└── 🎨 Street Art — 街头涂鸦 (城市声音、反叛态度)

CUSTOM PRESETS (if any in styles/custom/)
└── [list custom presets with test_render.png thumbnails]

REFERENCE MODE
├── 📷 Upload reference image(s) → extract style
└── 🎥 Provide video URL → extract style from frames
```

If the story_seed has `suggested_style.seedream_keywords`, highlight the matching preset as recommended.

### 3. Execute Based on User's Choice

**Preset Mode**:
1. Load the selected playbook YAML
2. Extract `image_prompt_prefix` → becomes `style_decision.image_prompt_prefix`
3. Extract `image_negative_prompt` → becomes `style_decision.image_negative_prompt`
4. Extract `asset_generation.consistency_anchors` → becomes `style_decision.consistency_anchors`
5. Extract color palette from `visual_language.color_palette`
6. Generate `style_lock` keywords from the playbook name and mood

**Reference Image Mode (single image)**:
1. Use VLM to analyze the reference image
2. Extract: color palette, lighting, texture, composition, line style
3. Convert to Seedream keywords
4. Generate a **style test image** — show the user and ask "是这个感觉吗？"
5. On confirmation, lock style parameters

**Reference Image Mode (multiple images)**:
1. Analyze each image individually
2. Extract **shared features** (appearing in ALL images) → core style → `style_lock`
3. Extract **unique features** (varying across images) → elastic space
4. Generate aggregated report: core style + elastic space + recommended Seedream keywords
5. Generate a **style test image** — confirm with user

**Reference Video Mode**:
1. Use `frame_sampler` to extract 5–10 key frames at time intervals
2. Same aggregation as multi-image mode
3. Additionally extract temporal color shifts (color over time)
4. Generate **style test image** — confirm with user

### 4. Lock Style Parameters

After user confirmation, construct the `style_decision` artifact:

```yaml
style_decision:
  version: "1.0"
  mode: preset | reference_image | reference_video
  preset_name: <if preset mode>
  style_lock: [keyword1, keyword2, keyword3, ...]  # ≥ 3 keywords, IMMUTABLE
  image_prompt_prefix: "风格描述前缀"
  image_negative_prompt: "photorealistic, 3D render, ..."
  consistency_anchors: [...]
  color_palette: { primary: [], accent: [], background: "", text: "", muted: "" }
  mood: "warm, healing"
  decided_at: <timestamp>
```

Write `style_lock` into `EP_STATE.style_lock` — this array is appended to every single image generation prompt for the rest of the pipeline.

### 5. Offer to Save Custom Preset

If the style was extracted from references (not a built-in preset), ask:

> "这个画风要保存起来以后复用吗？输入一个名称（如'宫崎骏风'），下次可直接选用。"

If yes, save:
```
styles/custom/<user-name>/
  ├── style.yaml          # Style parameters (playbook-compatible format)
  └── reference/         # Reference materials
      ├── source_01.png   # Original reference images
      ├── source_02.png
      └── test_render.png # Style test image
```

### 6. Quality Gate

- [ ] style_lock has ≥ 3 keywords
- [ ] image_prompt_prefix is non-empty
- [ ] consistency_anchors is non-empty
- [ ] (Reference mode) reference_analysis is filled with source paths and test render
- [ ] (Video input) EP_STATE.reference_video_analysis was consumed for suggestions
- [ ] User has confirmed the style choice or style test image

## Common Pitfalls

- **Too few style_lock keywords**: Minimum 3. Fewer than that, Seedream will drift between panels.
- **Skipping the style test**: Always generate a test image for reference modes. The user needs to see before committing.
- **Modifying style after lock**: style_lock is immutable. If it needs changing, that's a send-back to this stage.
- **Ignoring suggested_style**: The story_seed's suggested_style often matches the story's emotional tone. Respect it unless the user explicitly overrides.
