# Generate Director — Comic-Story Pipeline

## When To Use

You are the **Generate Director** for the comic-story pipeline. Your job is to produce all panel images using the **locked** character expression headshots, core_traits, scene master_descriptions, and style parameters from the preview stage — with **per-panel variation** in expression, pose, camera angle, and atmosphere.

This stage runs **automatically** (no human approval required) because the character and scene decisions were already confirmed in the preview stage.

## Pre-Generation Conventions (HARD RULES)

### Image Resolution: Always Square 1:1

All panel images MUST be generated at **square 1:1 aspect ratio** — either `1024×1024` or `1080×1080`. This is the native format for comic panels. Never generate at 720×1280 or any vertical/rectangular resolution.

The square images will be composited into the 9:16 vertical video frame later by the compose stage — centered with white padding. This preserves the original composition without any stretching or cropping.

### Why Square + White Padding?

- **No distortion**: 1:1 images fit naturally into douyin/xiaohongshu's 9:16 vertical player without stretching
- **Clean look**: White padding matches line-comic, clean-comic, and warm-illustration styles seamlessly
- **Consistent composition**: Every panel has the same framing — no surprises between panels
- **Preview-friendly**: Square images look better in the preview stage for character/scene review

## Reference Inputs

- `schemas/artifacts/shot_list.schema.json` — Panel definitions with expression maps, camera_angle, atmosphere
- `schemas/artifacts/preview_manifest.schema.json` — Locked character expression headshots, reference image paths, and core_traits
- `skills/creative/character-consistency.md` — Two-part description system, expression variation library, scene variation strategy
- `.agents/skills/volcengine-ark/SKILL.md` — Seedream reference image API (image_url / image_path)

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `shot_list` | Panel definitions (visual_description, expression map, camera_angle, atmosphere, scene_texts) |
| Artifact | `preview_manifest` | Locked expression headshots + character reference images + core_traits |
| Artifact | `style_decision` | Locked style (style_lock, image_prompt_prefix, negative_prompt) |
| EP State | `style_lock` | Immutable style keywords |
| Tool | `image_selector` | Image generation (routes to Seedream, passes image_path as reference) |

## Three Critical Rules (READ BEFORE GENERATING ANYTHING)

### Rule 1: Composite Reference Images Are Passed to Seedream

For EVERY character panel, pass the primary character's **composite reference image** (headshot + full-body side-by-side) via `image_path` to `image_selector`.

**Selection logic:**
```
For each panel:
  primary_character = the most prominent/foreground character
  panel_emotion = panel.expression[primary_character].emotion

  matching_composite = preview_manifest.character_anchors
    .find(primary_character).expression_headshots
    .find(emotion == panel_emotion).composite_reference_path

  reference_image = matching_composite
```

**Why composite reference images:**
- Seedream only accepts ONE reference image per call — the composite packs both signals into a single image
- Left half (full-body): anchors the character's complete physical identity — body type, clothing, proportions
- Right half (headshot): anchors the target expression — facial cues, emotion on the correct face
- Seedream sees both simultaneously: "make THIS person (left) show THIS emotion (right)"
- Result: strongest possible consistency — no tradeoff between identity and expression accuracy

**API detail:** `image_selector` accepts `image_path` (local file path, auto-converted to base64) which routes to Seedream's `image` parameter. Seedream supports ONE reference image per call.

**When multiple characters appear in a panel:** Pass the composite of the most prominent/foreground character. The other character(s) rely on text description (core_traits + per_panel_expression) for consistency.

### Rule 2: Scene Reference Images Are NEVER Passed

Passing a scene reference image forces Seedream to reproduce the exact composition, lighting, and angle — causing **identical backgrounds in every panel** with the character looking pasted in.

Instead, scene variety comes from **text only**: different `camera_angle` + `atmosphere` per panel, built from the `scene_registry`'s description library.

### Rule 3: Expression MUST Vary Per Panel

The composite reference anchors visual identity (full-body left) and target emotion (headshot right). The prompt's `per_panel_expression` reinforces and contextualizes the expression for THIS panel's scene and action. Seedream reconciles all three signals: "make THIS person (left half) show THIS emotion (right half) in THIS scene (from prompt)."

**Never reuse the same expression across panels.** Each panel's `expression` map from `shot_list` defines unique facial_expression + body_language + action for this specific moment.

---

## Process

### 1. Verify Lock State

Before generating any image, verify:
- `preview_manifest.character_anchors` has all characters with `reference_image_path` (the .png files exist and are readable)
- `shot_list.panels` defines every panel with `expression`, `camera_angle`, and `atmosphere`
- `style_decision.style_lock` is populated (≥ 3 keywords)

### 2. Prepare Per-Panel References

For each panel, determine the **composite reference image** to pass:

```
Panel reference mapping:
  Panel with 1 character   → pass that character's composite_reference_path (matching emotion)
  Panel with 2+ characters → pass the foreground/main character's composite_reference_path
  Panel with no characters (establishing shot) → NO reference image (text-only)

Composite selection:
  For the primary character in this panel:
    1. Look up panel.expression[primary_character].emotion
    2. Find the matching entry in preview_manifest.character_anchors[primary].expression_headshots
    3. Use that entry's composite_reference_path as image_path
```

### 3. Construct Prompts — The CORRECT Way

For each panel in `shot_list.panels`, build the prompt using this template:

```
{style_decision.image_prompt_prefix},
{scene_registry[panel.scene_template].master_description}，
从这个角度拍摄：{panel.camera_angle}，
光线与氛围：{panel.atmosphere}，
角色——{character_registry[name].core_traits}，
此刻——{panel.expression[name].facial_expression}，
身体动态——{panel.expression[name].body_language}，
画面内容：{panel.visual_description}，
{EP_STATE.style_lock keywords joined with commas}
```

**Example — Panel 1 (Kitchen scene, Mom worrying):**
```
温暖插画风格，柔和色调，手绘质感，
中式家庭厨房，L型操作台，白色瓷砖墙面，木色橱柜，窗台上摆着几盆绿萝，
窗外是小区花园，冰箱上贴着便利贴和照片，
从这个角度拍摄：中景平视，从厨房门口看向操作台，门框作为前景框住画面，
光线与氛围：午后阳光透过纱帘洒在台面上，温暖宁静，空气中飘着细小的灰尘，
角色——50岁亚洲女性，圆脸，齐肩短发带自然卷，戴银色细框眼镜，
常穿米色针织开衫，身高160cm左右，皮肤偏黄但气色好，手上有岁月的纹路，
左手戴一只老式银镯子，
此刻——眉头微蹙但嘴角有笑意，眼神温柔中带一丝焦急，目光追随着门口，
身体动态——身体微微前倾，双手在围裙上擦着，站在厨房门口朝外张望，
画面内容：妈妈正在切菜，听见门响抬头看向门口，阳光在她侧脸上勾出柔和的光晕，
温暖插画风格，柔和色调，手绘质感，日式生活插画
```

**Example — Panel 3 (Same kitchen, Mom shocked — different angle + atmosphere):**
```
温暖插画风格，柔和色调，手绘质感，
中式家庭厨房，L型操作台，白色瓷砖墙面，木色橱柜，窗台上摆着几盆绿萝，
窗外是小区花园，冰箱上贴着便利贴和照片，
从这个角度拍摄：近景特写，聚焦人物面部和手部，逆光让表情更戏剧化，
光线与氛围：黄昏时分，暖黄灯光取代自然光，厨房笼罩在紧张的金色余晖中，
角色——50岁亚洲女性，圆脸，齐肩短发带自然卷，戴银色细框眼镜，
常穿米色针织开衫，身高160cm左右，皮肤偏黄但气色好，手上有岁月的纹路，
左手戴一只老式银镯子，
此刻——眼睛睁大，眉毛扬起，嘴巴微张，整个人愣住了一秒，
身体动态——身体僵住，右手停在半空中，手上的锅铲还滴着汤汁，
画面内容：妈妈听到孩子说出的真相，动作完全中断，锅铲悬在半空，
温暖插画风格，柔和色调，手绘质感，日式生活插画
```

**Notice the differences between Panel 1 and Panel 3:**
- `core_traits` (角色——) is IDENTICAL → same person
- `camera_angle` is DIFFERENT (中景平视 vs 近景特写) → scene feels alive
- `atmosphere` is DIFFERENT (午后阳光 vs 黄昏紧张光线) → mood matches beat
- `per_panel_expression` (此刻——) is COMPLETELY DIFFERENT → varied emotion
- `visual_description` is DIFFERENT → unique action per panel

### 4. Scene Text Enhancement

For panels with `scene_texts` where `method = ai_draw`:
- Quote the text content: `...写着'{content}'这几个字`
- Describe carrier material: `{carrier}上...`
- Add quality keywords: `清晰可读的汉字` `clear Chinese characters`
- Only for ≤5 character texts — longer texts are `post_only`

**Post-only scene text** (for panels with `method = post_only`):
- Generate the scene **without** the text content (e.g., blank phone screen, white chat background)
- The caption stage will overlay the text later

### 5. Generate Panels (Sequential with Reference Images)

Generate panels **sequentially** (not in parallel) to maintain consistency:

```
For each panel in order:
  1. Identify the primary character for this panel
  2. Look up panel.expression[primary_character].emotion
  3. Find matching composite_reference_path in preview_manifest.character_anchors
  4. Construct the full prompt (template from Step 3)
  5. Call image_selector with:
     - prompt: <full constructed prompt>
     - negative_prompt: <from style_decision>
     - image_path: <composite_reference_path — headshot + full-body side-by-side>
     - generation_mode: "edit"
     - width: 1024, height: 1024  (or as configured)
  6. Save to: projects/<name>/assets/images/panel_{panel_number:02d}.png
  7. Record in asset_manifest with ALL generation parameters (including which composite was used)
```

**For establishing shots (no characters):**
- Omit `image_path` and `generation_mode`
- Use `generation_mode: "generate"` (plain text-to-image, no reference)

### 6. Post-Generation Quality Check

After each panel is generated, verify:
1. Image file exists and is readable (PIL can open it)
2. Visual check: does the character look like the reference image? (identity consistency)
3. Visual check: is the expression different from previous panels? (expression variety)
4. Visual check: is the scene composition different from previous panels of the same scene? (scene variety)
5. If any check fails: re-generate with adjusted prompt (max 1 retry per panel to stay within budget)

### 7. Build Asset Manifest

```yaml
asset_manifest:
  version: "1.0"
  panels:
    - panel_number: 1
      image_path: "projects/<name>/assets/images/panel_01.png"
      prompt_used: "<full prompt>"
      reference_image_used: "projects/<name>/assets/images/character_mama_composite_caoxin.png"
      reference_type: "composite"
      matched_emotion: "操心"
      primary_character: "妈妈"
      camera_angle: "中景平视，从厨房门口看向操作台"
      atmosphere: "午后阳光透过纱帘"
      character_expression: "操心——眉头微蹙，眼神温柔焦急"
      style_lock: [...]
      tool_used: "image_selector"
      provider: "seedream"
      generation_mode: "edit"
      generated_at: <timestamp>
  total_panels: N
  style_lock_used: [...]
  reference_images_used: [...]
  headshot_usage_rate: "X/N panels used composite reference images (Y panels used text-only, no characters)"
  expression_variety_check: "PASSED — all character expressions are unique across panels"
  scene_variety_check: "PASSED — all scene panels use different camera angles"
  budget_spent: X.XX
```

### 8. Expression & Scene Variety Audit (MANDATORY)

Before marking this stage complete, run two audits:

**Expression Variety Audit:**
```
For each character, list the expression used in each panel they appear in:
  Panel 1: 操心 (worry)
  Panel 2: 困惑 (confusion)
  Panel 3: 惊讶 (shock)
  Panel 4: 决心 (determination)
  Panel 5: 释然 (release)

Are any two panels using the same expression? → SHOULD BE NO
Does the progression match the emotion_arc? → SHOULD BE YES
```

**Scene Variety Audit:**
```
For each scene, list the camera_angle used in each panel:
  家中厨房:
    Panel 1: 中景平视，从厨房门口看向操作台
    Panel 3: 近景特写，聚焦人物面部和手部
    Panel 5: 中景侧角，从窗户方向看向厨房内部

Are any two panels using the same angle? → SHOULD BE NO
```

### 9. Quality Gate (G5)

- [ ] All panel images exist and are readable (can be opened by PIL)
- [ ] EVERY character panel used a reference image via `image_path` (composite reference image with matching emotion)
- [ ] Composite match rate ≥ 80% (most panels should use a matching composite, not text-only)
- [ ] All images use the same `style_lock` keywords
- [ ] `core_traits` matches preview_manifest verbatim in every prompt
- [ ] `master_description` matches preview_manifest verbatim in every prompt
- [ ] Expression variety check: every panel's expression is different from every other panel for the same character
- [ ] Scene variety check: same scene uses different `camera_angle` and `atmosphere` per panel
- [ ] Budget ≤ 90% of configured budget
- [ ] `asset_manifest` artifact is schema-valid

## Common Pitfalls

- **Forgetting to pass reference images**: This is the #1 cause of character inconsistency. Every character panel MUST include `image_path` pointing to the composite reference image from the preview stage.
- **Using individual images instead of composites**: The composite packs both identity (full-body) and expression (headshot) into a single image. Passing only the headshot loses body/identity detail; passing only the full-body loses expression detail. Always use the composite.
- **Wrong emotion matching**: When looking up the composite, match on the panel's `expression[character].emotion` field exactly. A partial match or synonym will fail to find the composite.
- **Paraphrasing core_traits**: Must be copied character-for-character from preview_manifest. Even a synonym change can alter Seedream's output.
- **Passing scene reference images**: DO NOT pass scene images as reference. They cause the "identical background" problem. Scene variety comes from text descriptions only.
- **Using the same expression for all panels**: The #2 user complaint after inconsistency. Each panel must have a UNIQUE per_panel_expression. Check the expression map from shot_list — never reuse an expression.
- **Using the same camera angle for the same scene**: Rotate through the scene's camera_angles library. A kitchen should look different in each panel.
- **Forgetting style_lock**: Every single prompt must end with the style_lock keywords.
- **Generating in parallel**: Generate sequentially. This allows you to check each image and adjust if needed, and avoids rate-limiting issues.
- **Not checking image quality**: After each generation, verify the image is not corrupted and the character expression actually changed.
- **Wrong primary character for reference**: When multiple characters appear, choose the one in the foreground or the one whose face is most visible. Wrong choice → supporting character looks wrong, main character looks right.
