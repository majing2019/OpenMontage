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
- `styles/clean-comic.yaml` — Clean comic preset
- `styles/line-comic.yaml` — Line comic preset (黑白线条漫画)
- `styles/cinematic-drama.yaml` — Cinematic drama preset
- `styles/watercolor-nostalgia.yaml` — Watercolor nostalgia preset
- `styles/ink-dramatic.yaml` — Ink dramatic preset
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

Show all available styles:

```
BUILT-IN PRESETS
├── 🎨 Warm Illustration — 温暖手绘 (亲情、治愈、日常)
├── 💬 Clean Comic — 现代漫画风 (搞笑、社死、段子)
├── ✏️ Line Comic — 黑白线条漫画 (段子、吐槽、条漫)
├── 🎬 Cinematic Drama — 电影感暗调 (悬疑、反转、紧张)
├── 🎨 Watercolor Nostalgia — 水彩怀旧 (时光、回忆、感动)
└── 🖊️ Ink Dramatic — 水墨黑白 (反转、冲击、深度)

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
