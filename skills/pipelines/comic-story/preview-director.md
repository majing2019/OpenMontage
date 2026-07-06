# Preview Director — Comic-Story Pipeline

## When To Use

You are the **Preview Director** for the comic-story pipeline. Your job is to generate **character anchor images** (neutral full-body reference), **expression headshots** (大头照 — one per unique emotion per character), and **scene sample images** (定妆照) so the user can confirm character appearances, expression quality, and scene settings before the full batch generation.

**This is the most critical quality gate in the pipeline.** Once the user approves here, character `core_traits`, expression headshots, and scene `master_description` are LOCKED. The expression headshots you generate here will be passed directly to Seedream as `reference_image` inputs in the generate stage — each panel receives the headshot matching its target emotion.

## Reference Inputs

- `skills/creative/character-consistency.md` — Two-part character description system, Seedream reference image patterns, scene description library
- `schemas/artifacts/shot_list.schema.json` — Input structure (character_registry with core_traits, scene_registry with master_description)
- `schemas/artifacts/preview_manifest.schema.json` — Output structure

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `shot_list` | Character and scene registries (with core_traits and master_description) |
| Artifact | `style_decision` | Locked style (style_lock, image_prompt_prefix) |
| EP State | `style_lock` | Immutable style keywords |
| Tool | `image_selector` | Image generation (routes to Seedream) |

## Process

### 1. Generate Character Reference Images (角色参考图)

For each character in `shot_list.character_registry`:

**IMPORTANT:** The images generated here will be used as **Seedream reference images** in the generate stage. They MUST be clean, clear character portraits — not action shots.

**Prompt construction:**
```
{style_decision.image_prompt_prefix},
角色设定参考图：{character.core_traits}，
正面站立全身像，中性表情（嘴巴自然闭合，眼睛平视前方），
双手自然垂在身体两侧，纯浅灰色背景，均匀柔和光线，
用于AI生图时作为角色一致性参考图，
{EP_STATE.style_lock keywords joined with commas}
{style_decision.image_negative_prompt}
```

**Key rules:**
- Use the **exact** `core_traits` from the character_registry — do NOT paraphrase
- Generate a **neutral expression** reference image (not smiling, not frowning — neutral face for maximum flexibility in downstream generation)
- Full-body standing pose, front view, clean light-gray background
- Append all `style_lock` keywords at the end
- Include the negative prompt
- **This image becomes the `reference_image` passed to Seedream in the generate stage**

**Save to:** `projects/<name>/assets/images/character_<name>_ref.png`

**Record the path** in `character_registry[character].reference_image_path` for the generate stage to use.

### 1b. Generate Expression Headshots (表情大头照)

For each character in `shot_list.character_registry`, collect all **unique emotions** from `shot_list.panels`:

```
For each character:
  unique_emotions = deduplicate(
    panel.expression[character_name].emotion
    for each panel where character_name appears
  )
```

Then generate **one close-up headshot per unique emotion**.

**Prompt construction for each emotion headshot:**
```
{style_decision.image_prompt_prefix},
角色表情参考图：{character.core_traits}，
{facial_expression_from_expression_library}，
大头照，面部特写，纯浅灰色背景，均匀柔和光线，
表情自然生动，情感真实，
用于AI生图时作为角色表情一致性参考图，
{EP_STATE.style_lock keywords joined with commas}
{style_decision.image_negative_prompt}
```

**Facial expression sourcing:** Use the `character-consistency.md` Expression Variation Library (表情变化库) to map each emotion to specific facial cues. For example:
- 操心 → "眉头微蹙，目光追随带一丝焦虑，微微抿嘴"
- 惊讶 → "眉毛扬起，眼睛睁大瞳孔收缩，嘴巴微张"
- 开心 → "面部舒展，眼睛弯成月牙有光，嘴角上扬"
- 悲伤 → "面部下垂，眼睛湿润视线向下，嘴角下撇"

**Key rules:**
- Use the **exact** `core_traits` from the character_registry — do NOT paraphrase
- Each headshot is a **close-up face shot** (大头照), NOT full-body — the focus is the face and expression
- Neutral light-gray background (same as the full-body reference for consistency)
- These images will be used as **Seedream reference_image** in the generate stage — they anchor BOTH identity AND expression
- Generate one headshot per unique emotion per character (not per panel — deduplicate first)

**Save to:** `projects/<name>/assets/images/character_<name>_expr_<emotion>.png`
(Use pinyin or English for emotion in filename: e.g., `character_mama_expr_caoxin.png`, `character_mama_expr_jingya.png`)

**Record each headshot** in the preview manifest under `character_anchors[character].expression_headshots`:
```yaml
expression_headshots:
  - emotion: "操心"
    headshot_path: "projects/<name>/assets/images/character_mama_expr_caoxin.png"
    composite_reference_path: "projects/<name>/assets/images/character_mama_composite_caoxin.png"
    facial_expression: "眉头微蹙，目光追随带一丝焦虑，微微抿嘴"
  - emotion: "惊讶"
    headshot_path: "projects/<name>/assets/images/character_mama_expr_jingya.png"
    composite_reference_path: "projects/<name>/assets/images/character_mama_composite_jingya.png"
    facial_expression: "眉毛扬起，眼睛睁大瞳孔收缩，嘴巴微张"
```

### 1c. Generate Composite Reference Images (合成参考图)

For each expression headshot, **composite it with the neutral full-body reference** into a single side-by-side image. This composite becomes the reference_image passed to Seedream in the generate stage.

**Why composite:** Seedream only accepts ONE reference image per call. By compositing the headshot (expression) and full-body (identity) side by side, Seedream sees both in a single reference — anchoring identity AND expression simultaneously.

**Compositing method (PIL):**
```python
from PIL import Image

def create_composite(headshot_path, fullbody_path, output_path, size=(1024, 1024)):
    headshot = Image.open(headshot_path).resize((512, 1024))
    fullbody = Image.open(fullbody_path).resize((512, 1024))
    composite = Image.new("RGB", size, (240, 240, 240))  # light-gray background
    composite.paste(fullbody, (0, 0))      # left: full-body (identity)
    composite.paste(headshot, (512, 0))    # right: headshot (expression)
    composite.save(output_path)
```

**Layout convention:**
```
┌──────────────┬──────────────┐
│              │              │
│  Full-body   │  Expression  │
│  (identity)  │  headshot    │
│              │  (emotion)   │
│              │              │
└──────────────┴──────────────┘
   512 × 1024  │  512 × 1024
          1024 × 1024 composite
```

**Key rules:**
- Full-body on the LEFT (identity anchor), headshot on the RIGHT (expression anchor)
- Both halves resized to 512×1024, composite is 1024×1024
- Light-gray background fills any gaps from aspect ratio differences
- Generate ONE composite per headshot (i.e., one per unique emotion per character)

**Save to:** `projects/<name>/assets/images/character_<name>_composite_<emotion>.png`

**Record the composite path** in `expression_headshots[].composite_reference_path` (see Step 1b above).

### 2. Generate Scene Sample Images (场景定妆照 — 仅用于人工确认)

For each scene in `shot_list.scene_registry`:

**Prompt construction:**
```
{style_decision.image_prompt_prefix},
{scene.master_description}，
{scene.camera_angles[0]}，{scene.atmosphere_variants[0]}，
场景定妆照，展示整体环境氛围，
{EP_STYLE.state_lock keywords joined with commas}
{style_decision.image_negative_prompt}
```

**Key rules:**
- Use the **exact** `master_description` from the scene_registry — do NOT paraphrase
- Pick the first/default camera angle and atmosphere for the sample
- This is a **scene establishment shot** — no characters needed (or minimal presence)
- **Scene images are for HUMAN CONFIRMATION only** — they are NOT passed as reference_image to Seedream in the generate stage. Why: passing a scene reference image forces Seedream to reproduce the exact same composition, lighting, and angle in every panel, causing the "identical background + pasted character" problem.

**Save to:** `projects/<name>/assets/images/scene_<name>_sample.png`

**Record the path** in `scene_registry[scene].reference_image_path` (for documentation only).

### 3. WHY: Reference Image Strategy

This is the key design decision for the preview and generate stages:

| Image Type | Used As Seedream Reference? | Why |
|-----------|---------------------------|-----|
| Character neutral reference image | **Component of composite** — left half | Anchors character visual identity (full-body) |
| Character expression headshot | **Component of composite** — right half | Anchors target expression (close-up face) |
| **Composite reference image** | **YES** — passed as `reference_image` | Single image combining identity + expression for Seedream |
| Scene sample image | **NO** — human confirmation only | Scene reference images constrain composition → identical backgrounds every panel |

**How composite reference images work:**
- Seedream only accepts ONE reference image per call
- The composite puts the full-body (identity) and headshot (expression) side by side in a single 1024×1024 image
- Seedream sees both signals simultaneously: "make THIS person (left half) show THIS emotion (right half)"
- Result: strongest possible consistency — identity anchored by full-body view, expression anchored by close-up example
- The generate stage picks the composite matching each panel's emotion

**Why scene reference images backfire:**

**Why scene reference images backfire:**
- Passing a scene image tells Seedream "make the background look exactly like THIS"
- Seedream prioritizes the reference image's composition over the prompt's camera_angle and atmosphere
- Every panel in that scene gets identical framing, lighting, and composition
- The character looks "pasted in" because Seedream is trying to reproduce the reference composition while separately rendering a character — a conflicting instruction

**The correct approach for scene variety:**
- Use text descriptions only: `master_description` + varied `camera_angle` + varied `atmosphere`
- Seedream generates a naturally composed scene from text that fits the angle and mood
- The character is integrated organically because the prompt describes them IN the scene as a unified whole

### 3. Present to User for Approval

Show each character reference image, expression headshots, and scene sample image. For each:

**Character review (physical identity)**:
- "这个角色的样子对吗？"
- Check: face, hair, body type, clothing all match the story intent
- **Important:** The reference image shows a neutral expression. This is intentional — it confirms the physical identity.
- If wrong: revise the `core_traits` in character_registry and regenerate (max 3 revisions)

**Expression headshot review (per character, per emotion)**:
- "这个角色的[emotion]表情自然吗？"
- Check: the facial expression matches the emotion label, identity is consistent with the neutral reference
- If wrong: revise the facial_expression description and regenerate that specific headshot (max 3 revisions per headshot)

**Composite reference review (automated — no user action needed)**:
- After headshot approval, composites are generated automatically (PIL side-by-side)
- No separate user review — composite quality inherits from headshot + full-body approval
- Remind the user: "合成参考图（全身照+表情大头照）将自动生成，用于AI生图时的角色一致性参考。"

**Scene review**:
- "这个场景的氛围对不对？"
- Check: lighting, colors, composition match the story setting
- Remind the user: "实际生成的每个画面的角度和光线会根据剧情情绪变化，这张只是确认场景基调。"
- If wrong: revise the `master_description` in scene_registry and regenerate (max 3 revisions)

### 4. Lock and Save Preview Manifest

After user approval, build the `preview_manifest` artifact:

```yaml
preview_manifest:
  version: "1.0"
  character_anchors:
    - character_name: "妈妈"
      reference_image_path: "projects/<name>/assets/images/character_mama_ref.png"
      core_traits: "50岁亚洲女性，圆脸，齐肩短发带自然卷..."
      expression_headshots:
        - emotion: "操心"
          headshot_path: "projects/<name>/assets/images/character_mama_expr_caoxin.png"
          composite_reference_path: "projects/<name>/assets/images/character_mama_composite_caoxin.png"
          facial_expression: "眉头微蹙，目光追随带一丝焦虑，微微抿嘴"
        - emotion: "惊讶"
          headshot_path: "projects/<name>/assets/images/character_mama_expr_jingya.png"
          composite_reference_path: "projects/<name>/assets/images/character_mama_composite_jingya.png"
          facial_expression: "眉毛扬起，眼睛睁大瞳孔收缩，嘴巴微张"
        - emotion: "释然"
          headshot_path: "projects/<name>/assets/images/character_mama_expr_shiran.png"
          composite_reference_path: "projects/<name>/assets/images/character_mama_composite_shiran.png"
          facial_expression: "面部松弛，眼神柔和望向远方，轻轻呼气的嘴型"
      approved: true
      usage: "Composite reference images (headshot + full-body) passed as reference_image to Seedream in generate stage."
  scene_samples:
    - scene_name: "家中厨房"
      reference_image_path: "projects/<name>/assets/images/scene_kitchen_sample.png"
      master_description: "中式家庭厨房，L型操作台..."
      approved: true
      usage: "HUMAN CONFIRMATION ONLY — NOT passed as reference_image. Scene variety comes from text descriptions."
  prompt_templates:
    character_panel: "{image_prompt_prefix}, {scene.master_description}, 角度: {camera_angle}, 氛围: {atmosphere}, {character.core_traits}, 此刻: {expression.facial_expression}，{expression.body_language}，{panel.visual_description}, {style_lock}"
    scene_establishing: "{image_prompt_prefix}, {scene.master_description}, {camera_angle}, {atmosphere}, {style_lock}"
  style_lock: [...from EP_STATE]
  image_prompt_prefix: "...from style_decision"
  reference_image_strategy:
    character_images: "Composite reference images (headshot + full-body side-by-side) passed as reference_image to Seedream — anchors both identity AND target expression in a single image."
    scene_images: "NOT passed as reference_image — human confirmation only. Scene variety via text descriptions."
```

**CRITICAL**: The `core_traits`, `expression_headshots` (with composite references), and `master_description` in the preview_manifest are now LOCKED. The generate stage must copy `core_traits` verbatim into every prompt and select the matching composite_reference_path as `reference_image` for character panels.

### 5. Quality Gate (G4)

- [ ] Every character in `character_registry` has a generated reference image with neutral expression
- [ ] Every character has expression headshots for ALL unique emotions from the shot_list
- [ ] Every expression headshot has a composite reference image (headshot + full-body side-by-side)
- [ ] Every composite_reference_path is recorded for the generate stage
- [ ] Every character reference image path is recorded (used as composite component)
- [ ] Every scene in `scene_registry` has a generated scene sample image
- [ ] User understands: composite reference images (headshot + full-body) will be used as Seedream reference_image for matching panels
- [ ] User has confirmed: characters look correct, expressions are natural, scenes match expectations
- [ ] All images are saved to the project assets directory
- [ ] `preview_manifest` artifact is schema-valid

## Common Pitfalls

- **Skipping reference image generation**: Character reference images are the backbone of consistency. Without them, the generate stage is text-only and character drift is inevitable.
- **Expressive reference images**: A smiling reference image will bias ALL panels toward smiling. Use NEUTRAL expressions for the full-body reference image. Expression headshots handle the emotion anchoring separately.
- **Missing expression headshots**: If a character shows 5 emotions across panels but you only generate 3 headshots, the generate stage falls back to the neutral reference for the missing 2 emotions — losing expression accuracy. Always cover ALL unique emotions.
- **Generating full-body shots for headshots**: Expression headshots MUST be close-up face shots (大头照), not full-body. The full-body identity anchor comes from the neutral reference image; the headshot provides the expression signal. Both are composited into a single 1024×1024 reference.
- **Skipping composite generation**: Without composites, you can only pass ONE image (headshot OR full-body) to Seedream, losing either identity or expression anchoring. Always generate composites after headshot approval.
- **Passing scene images as references**: This is the #1 cause of "identical background + pasted character" syndrome. Scene images are for human eyes only.
- **Modifying core_traits during generation**: If the first render doesn't look right, revise `core_traits` in `character_registry`, NOT in the prompt. The registry is the source of truth.
- **Skipping the user review**: This is a `human_approval_default: true` stage. Always present images and wait for confirmation.
- **Generating too many characters at once**: Generate one character at a time so the user can give focused feedback.
- **Using different style keywords**: Always use the same `style_lock` for preview as for the final panels.
- **Low-quality reference images**: If a character reference looks bad, regenerate it now. A bad reference image will produce bad panels in every subsequent stage.
