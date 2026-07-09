# Generate Director — Comic-Story Pipeline

## When To Use

You are the **Generate Director** for the comic-story pipeline. Your job is to produce all panel images using the **locked** character expression headshots, core_traits, scene master_descriptions, and style parameters from the preview stage — with **per-panel variation** in expression, pose, camera angle, and atmosphere.

This stage runs **automatically** (no human approval required) because the character and scene decisions were already confirmed in the preview stage.

## Pre-Generation Conventions (HARD RULES)

### Image Resolution: Square 1:1 Default, 9:16 Allowed

All panel images are generated at **square 1:1 aspect ratio** by default — either `1024×1024` or `1080×1080`. This is the native format for comic panels.

**When `shot_list.aspect_ratio` is `"9:16"`:** Use the resolution specified in `shot_list.image_size` (typically `1440×2560`) instead of square. This is appropriate for pure black-and-white line-comic styles where the extra vertical space serves as natural white space for text placement, eliminating the need for artificial composition instructions. The 9:16 format also matches the final video output directly without white padding.

**Why square is the default:**
- **No distortion**: 1:1 images fit naturally into douyin/xiaohongshu's 9:16 vertical player without stretching
- **Clean look**: White padding matches line-comic, clean-comic, and warm-illustration styles seamlessly
- **Consistent composition**: Every panel has the same framing — no surprises between panels
- **Preview-friendly**: Square images look better in the preview stage for character/scene review

**When to use 9:16:**
- Pure B&W line art styles where the entire canvas is used as comic space
- When `shot_list.aspect_ratio` is explicitly set to `"9:16"`

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
| Tool | `image_selector` | Image generation (routes to Seedream, passes image_paths array for multi-reference anchoring) |

## Three Critical Rules (READ BEFORE GENERATING ANYTHING)

### Rule 1: Multi-Reference Anchoring — Use `image_paths` Array

Seedream 4.0+ supports **up to 14 reference images per call** via the `image` parameter as an array. Use `image_paths` (plural) to pass **all relevant anchors simultaneously** — no more picking a "primary character" and sacrificing the rest.

**Anchor selection logic — per-panel decision tree:**

```
For each panel, collect anchors from three categories:

1. CHARACTER IDENTITY — for EVERY character appearing in the panel:
   → character_<name>_ref.png   (full-body reference image from preview stage)
   ALWAYS include. Never skip a character that appears in the panel.

2. EXPRESSION — for each character whose target emotion has a headshot:
   → <name>_expr_<emotion>.png   (expression headshot from preview stage)
   Include when the emotion exactly matches or is a close synonym.
   Skip when no matching headshot exists — text handles the expression.
   Partial match (e.g., "shrug" for "自嘲") is better than no match.

3. SCENE — conditional on scene reuse count across panels:
   → scene_<name>_sample.png   (scene reference from preview stage)
   SAFE: scene appears in ≤ 2 panels total → include for composition anchoring
   UNSAFE: scene appears in 3+ panels → skip, use text-only for variety
```

**Decision examples:**

| Panel has | Scene freq | Anchors to pass via `image_paths` |
|-----------|-----------|-----------------------------------|
| 小王 + 张总, both have matching headshots | 餐厅 (6 panels) | `[xiaowang_ref, xiaowang_expr_X, zhangzong_ref, zhangzong_expr_Y]` — 4 refs, NO scene |
| 小王 only, no matching headshot | 餐厅 (6 panels) | `[xiaowang_ref]` — identity only, text handles expression |
| 小王 + 张总, no matching headshots | 台阶 (1 panel) | `[xiaowang_ref, zhangzong_ref, scene_doorstep_sample]` — scene is safe to anchor |
| 无角色 (establishing/IP outro) | 纯白背景 | `[]` — text-only generation |

**Why multi-reference instead of composite images:**
- No need to pre-bake composite images (headshot + full-body side-by-side)
- Each reference is a clean, distinct signal — character identity OR expression, not a confusing hybrid
- ALL appearing characters get identity anchoring, not just the "primary" one
- Seedream merges features from all references into one coherent image

**API detail:** `image_selector` routes `image_paths` (array) to Seedream's `image` parameter. 1 image → string, 2-14 images → array.

### Rule 2: Scene Reference Images — Conditional, Not Banned

The old rule was "never pass scene references." The new rule is **conditional on reuse count:**

| Scene appears in | Action | Rationale |
|-----------------|--------|-----------|
| **1 panel** only | ✅ Pass scene reference | No risk of identical backgrounds — it's the only panel with this scene |
| **2 panels** | ✅ Pass scene reference, but vary camera_angle + atmosphere in prompt | Two panels with different angles won't look identical |
| **3+ panels** | ❌ Skip scene reference | Text-only scene variety via different `camera_angle` + `atmosphere` per panel |

### Rule 3: Expression MUST Vary Per Panel

Expression headshots provide the target emotion signal. The prompt's `per_panel_expression` reinforces and contextualizes the expression for THIS panel's scene and action. Seedream reconciles: character identity (ref) + target expression (ref) + scene context (prompt).

**Never reuse the same expression across panels.** Each panel's `expression` map from `shot_list` defines unique facial_expression + body_language + action for this specific moment.

**When no matching expression headshot exists:** Omit it — the character ref + text description handles the expression. Don't force a mismatched headshot (e.g., don't use "warm" for "determined").

### Rule 4: Composition-Aware White Space — Leave Room for Text

Real comics don't paste text on top of a full image — they **plan the composition around the text before drawing.** Every prompt MUST include a composition instruction that leaves white space on the side opposite to where the text will go.

**The rule:** Text at top → characters lower. Text at bottom → characters higher. Text in center → characters on sides.

**Composition instruction — generated from `shot_list.panels[].text_overlay.position`:**

| `text_overlay.position` | Composition instruction (insert into prompt) |
|--------------------------|----------------------------------------------|
| `center_top` (标题在上) | "构图——角色偏下，画面上方三分之一留白，留给标题文字" |
| `bottom` (旁白在下) | "构图——角色偏上，画面下方三分之一留白，留给旁白文字" |
| `center` (文字居中) | "构图——角色分列左右两侧，画面中央和上方留出充足空白放文字" |
| `emphasis` (冲击大字) | "构图——主体动作居中偏上，画面下方留白给强调文字，上方留给效果线" |
| `corner` (角落小字) | "构图——角色主体偏左上，右下角留白给角落文字" |

**Why this matters:**
- A line-comic with white background has NO natural place to hide text — white space must be created intentionally
- Text pasted on a full composition looks like a slide, not a comic
- Seedream follows composition instructions well when given explicit direction like "characters in lower half, leave top third empty"
- The caption stage will place text in the预留空白区, not over the artwork

**How to apply — modify the prompt template to include composition instruction BEFORE character/scene details:**

```
{style_prefix}，
{scene_description}，
{composition_instruction}，    ← NEW: 构图留白指令
从这个角度拍摄：{camera_angle}，
...
```

---

## Process

### 1. Verify Lock State

Before generating any image, verify:
- `preview_manifest.character_anchors` has all characters with `reference_image_path` (the .png files exist and are readable)
- `shot_list.panels` defines every panel with `expression`, `camera_angle`, and `atmosphere`
- `style_decision.style_lock` is populated (≥ 3 keywords)

### 2. Prepare Per-Panel References

For each panel, determine **all** reference images to pass via `image_paths`:

```
Step A — Count scene frequency across ALL panels:
  For each scene in scene_registry:
    count how many panels use this scene
    → this determines whether scene refs are SAFE or UNSAFE

Step B — For each panel, collect anchors:

  identity_refs = []
  For each character in panel.character_anchors:
    ref = preview_manifest.character_anchors[char].reference_image_path
    identity_refs.append(ref)  # ALWAYS include

  expression_refs = []
  For each character in panel.character_anchors:
    target_emotion = panel.expression[char].emotion
    headshot = find matching expression headshot in preview_manifest
    if headshot exists and emotion matches (exact or close synonym):
      expression_refs.append(headshot.image_path)
    # Skip if no match — don't force a wrong headshot

  scene_refs = []
  scene_name = panel.scene_template
  if scene_frequency[scene_name] <= 2:
    scene_refs.append(preview_manifest.scene_samples[scene_name].reference_image_path)

  panel.image_paths = identity_refs + expression_refs + scene_refs
```

**Reference count per panel type:**

| Panel type | Typical ref count | Example |
|-----------|------------------|---------|
| Solo character, no matching headshot, frequent scene | 1 | `[xiaowang_ref]` |
| Solo character + matching headshot, frequent scene | 2 | `[xiaowang_ref, xiaowang_expr_shocked]` |
| Two characters, one has headshot, frequent scene | 3 | `[xiaowang_ref, zhangzong_ref, zhangzong_expr_warm]` |
| Two characters, both have headshots, frequent scene | 4 | `[xiaowang_ref, xiaowang_expr_X, zhangzong_ref, zhangzong_expr_Y]` |
| Two characters + rare scene | 3-5 | above + scene ref |
| No characters (IP outro / establishing shot) | 0 | `[]` — text-only generation |

### 3. Construct Prompts — The CORRECT Way

For each panel in `shot_list.panels`, build the prompt using this template:

```
{style_decision.image_prompt_prefix},
{scene_registry[panel.scene_template].master_description}，
{composition_instruction}，        ← 根据 text_overlay.position 生成的构图留白指令
从这个角度拍摄：{panel.camera_angle}，
光线与氛围：{panel.atmosphere}，
角色——{character_registry[name].core_traits}，
此刻——{panel.expression[name].facial_expression}，
身体动态——{panel.expression[name].body_language}，
画面内容：{panel.visual_description}，
{EP_STATE.style_lock keywords joined with commas}
```

**Composition instruction — map `text_overlay.position` to a Chinese构图指令:**

| `position` value | Instruction to insert |
|------------------|----------------------|
| `center_top` | "构图——角色偏下，画面上方三分之一留白，留给标题文字。角色不要太靠上" |
| `bottom` | "构图——角色偏上，画面下方三分之一留白，留给旁白文字" |
| `center` | "构图——角色分列左右两侧，画面中央和上方留出充足空白放文字" |
| `emphasis` | "构图——主体动作居中偏上，画面下方留白给强调文字，上方留给速度和效果线" |
| `corner` | "构图——角色主体偏左上，右下角留白给角落文字" |

**For panels with `text_overlay: null`:** Omit the composition instruction — generate a full-frame image.

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

### 5. Generate Panels (Sequential with Multi-Reference Images)

Generate panels **sequentially** (not in parallel) to maintain consistency:

```
For each panel in order:
  1. Identify ALL characters appearing in this panel
  2. Look up each character's target emotion from panel.expression
  3. Collect identity refs (character reference images) — one per character
  4. Collect expression refs (matching headshots) — where available
  5. Check scene frequency — include scene ref only if scene appears in ≤ 2 panels
  6. Combine: image_paths = identity_refs + expression_refs + scene_refs
  7. Construct the full prompt (template from Step 3)
  8. Call image_selector with:
     - prompt: <full constructed prompt>
     - image_paths: <array of all collected reference paths>  (omit if empty)
     - size: shot_list.image_size (e.g., "1440x2560" for 9:16) or "4K" (2048x2048) for square 1:1
     - preferred_provider: "volcengine"
     - output_path: projects/<name>/assets/images/panel_{panel_number:02d}.png
  9. Save to: projects/<name>/assets/images/panel_{panel_number:02d}.png
  10. Record in asset_manifest with ALL reference images used and anchor strategy
```

**For text-only panels (no characters):**
- Omit `image_paths` entirely (pure text-to-image)
- No `generation_mode` needed

### 6. Post-Generation Quality Check

After each panel is generated, verify:
1. Image file exists and is readable (PIL can open it)
2. Visual check: do ALL characters look like their reference images? (multi-character identity consistency)
3. Visual check: is the expression different from previous panels? (expression variety)
4. Visual check: is the scene composition different from previous panels of the same scene? (scene variety)
5. If any check fails: re-generate with adjusted prompt or anchor selection (max 1 retry per panel to stay within budget)

### 7. Build Asset Manifest

```yaml
asset_manifest:
  version: "1.0"
  multi_ref_enabled: true
  panels:
    - panel_number: 1
      image_path: "projects/<name>/assets/images/panel_01.png"
      prompt_used: "<full prompt>"
      reference_images_used: ["character_xiaowang_ref.png", "xiaowang_expr_shocked.png", "character_zhangzong_ref.png"]
      anchor_strategy: "小王角色+震惊表情 + 张总角色"
      seed: 3001
      camera_angle: "中景平视，从门口看向餐厅内部全景"
      atmosphere: "明亮白炽灯"
      tool_used: "image_selector"
      provider: "seedream_volcengine"
      generated_at: <timestamp>
  total_panels: N
  style_lock_used: [...]
  expression_variety_check: "PASSED — all character expressions are unique across panels"
  scene_variety_check: "PASSED — all scene panels use different camera angles"
  budget_spent: X.XX
```
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
- [ ] EVERY character appearing in a panel has a reference image in `image_paths` (character identity anchoring)
- [ ] Expression headshots are included where matching emotions exist (per-panel expression anchoring)
- [ ] Scene refs are included ONLY for scenes appearing in ≤ 2 panels (conditional scene anchoring)
- [ ] Reference coverage rate ≥ 100% for character identity (every character in every panel has a ref)
- [ ] All images use the same `style_lock` keywords
- [ ] `core_traits` matches preview_manifest verbatim in every prompt
- [ ] `master_description` matches preview_manifest verbatim in every prompt
- [ ] Every panel with `text_overlay` has a composition instruction matching its `text_overlay.position` (Rule 4)
- [ ] White space预留区 is on the correct side: top text → characters lower, bottom text → characters higher
- [ ] Expression variety check: every panel's expression is different from every other panel for the same character
- [ ] Scene variety check: same scene uses different `camera_angle` and `atmosphere` per panel
- [ ] Budget ≤ 90% of configured budget
- [ ] `asset_manifest` artifact is schema-valid

## Common Pitfalls

- **Old habit: passing only ONE reference for multi-character panels**: This is the #1 cause of the "other character looks wrong" bug. Use `image_paths` (array) to pass ALL characters' reference images. Every character in the panel gets identity anchoring.
- **Forgetting to pass reference images at all**: Text-only description without any character reference → character looks different in every panel. Every panel with characters MUST have at least the character reference images.
- **Using scene references for frequent scenes**: If a scene appears in 3+ panels, passing the scene reference makes every panel's background identical. Skip scene refs for high-frequency scenes — use text variety instead.
- **Wrong emotion matching**: When looking up expression headshots, match the emotion field. A close synonym (e.g., "耸肩" for "自嘲") is better than no match. But don't force a completely wrong headshot (e.g., "温暖" for "决心").
- **Using `image_path` (singular) instead of `image_paths` (plural)**: The old singular param still works but only passes one image. Always use the plural form when you have multiple anchors.
- **Paraphrasing core_traits**: Must be copied character-for-character from preview_manifest. Even a synonym change can alter Seedream's output.
- **Using the same expression for all panels**: The #2 user complaint after inconsistency. Each panel must have a UNIQUE per_panel_expression. Check the expression map from shot_list — never reuse an expression.
- **Using the same camera angle for the same scene**: Rotate through the scene's camera_angles library.
- **Forgetting style_lock**: Every single prompt must end with the style_lock keywords.
- **Generating in parallel**: Generate sequentially. This allows you to check each image and adjust if needed, and avoids rate-limiting issues.
- **Not checking image quality**: After each generation, verify the image is not corrupted and the character expression actually changed.
- **Skipping characters in multi-character panels**: If a panel has 3 characters, pass 3 character refs. Don't pick one "primary" and skip the rest — multi-ref makes this unnecessary.
- **Generating full-frame images with no white space for text**: The #3 user complaint. Every prompt MUST include a composition instruction based on `text_overlay.position`. Text at bottom → characters higher. Text at top → characters lower. Full-frame images with text pasted on top look like slides, not comics.
- **Using wrong composition direction**: If `text_overlay.position` is `center_top`, characters go LOWER, not higher. If `bottom`, characters go HIGHER. Getting this backwards means the text covers the artwork.
- **Ignoring doorstep/outdoor scene text placement**: When characters sit on steps (bottom of frame), text should go at top (sky area), not bottom. Adjust `text_overlay.position` in `shot_list` accordingly during shot planning.
- **Forgetting the composition instruction entirely**: Easy to skip when writing prompts manually. Always check: does this prompt tell Seedream where to leave white space?
