# Preview Director — Comic-Story Pipeline

## When To Use

You are the **Preview Director** for the comic-story pipeline. Your job is to generate **character anchor images** (three-view sheets) and **scene sample images** (定妆照) so the user can confirm character appearances and scene settings before the full batch generation.

**This is the most critical quality gate in the pipeline.** Once the user approves here, character and scene descriptions are LOCKED. The generate stage must use them verbatim.

## Reference Inputs

- `skills/creative/character-consistency.md` — Character anchor description template and Seedream reference image patterns
- `schemas/artifacts/shot_list.schema.json` — Input structure (character_registry, scene_registry)
- `schemas/artifacts/preview_manifest.schema.json` — Output structure

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `shot_list` | Character and scene registries |
| Artifact | `style_decision` | Locked style (style_lock, image_prompt_prefix) |
| EP State | `style_lock` | Immutable style keywords |
| Tool | `image_selector` | Image generation (routes to Seedream) |

## Process

### 1. Generate Character Three-View Sheets

For each character in `shot_list.character_registry`:

**Prompt construction**:
```
{style_decision.image_prompt_prefix},
角色三视图展示：正面、侧面、背面，
{character.anchor_description},
全身像，白色背景，站立姿势，
{EP_STATE.style_lock keywords joined with commas}
{style_decision.image_negative_prompt}
```

Key rules:
- One image per character, showing all three views (front, side, back)
- Use the **exact** `anchor_description` from the character_registry — do NOT paraphrase or modify
- Append all `style_lock` keywords at the end
- Include the negative prompt

Save to: `projects/<name>/assets/images/character_<name>.png`

### 2. Generate Scene Sample Images

For each scene in `shot_list.scene_registry`:

**Prompt construction**:
```
{style_decision.image_prompt_prefix},
{scene.template_prefix},
{character_anchor for main character in this scene},
场景定妆照，展示整体氛围和光线，
{EP_STATE.style_lock keywords joined with commas}
{style_decision.image_negative_prompt}
```

Key rules:
- One image per scene
- Include the most prominent character for that scene
- Use the **exact** `template_prefix` from the scene_registry — do NOT paraphrase
- This is a "定妆照" (costume test) — meant to confirm the scene looks right before full production

Save to: `projects/<name>/assets/images/scene_<name>.png`

### 3. Present to User for Approval

Show each character anchor image and scene sample image. For each:

**Character review**:
- "这个角色像你想象中的吗？"
- Check: face, hair, body type, clothing all match the story intent
- If wrong: revise the `anchor_description` and regenerate (max 3 revisions)

**Scene review**:
- "这个场景氛围对不对？"
- Check: lighting, colors, composition match the story setting
- If wrong: revise the `template_prefix` and regenerate (max 3 revisions)

### 4. Lock and Save Preview Manifest

After user approval, build the `preview_manifest` artifact:

```yaml
preview_manifest:
  version: "1.0"
  character_anchors:
    - character_name: "妈妈"
      image_path: "projects/<name>/assets/images/character_mama.png"
      anchor_description: "中年女性，温柔圆脸..."
      views: [front, side, back]
      approved: true
  scene_samples:
    - scene_name: "家庭厨房"
      image_path: "projects/<name>/assets/images/scene_kitchen.png"
      template_prefix: "温暖的家庭厨房..."
      characters_included: ["妈妈", "小明"]
      approved: true
  prompt_templates:
    character_panel: "{image_prompt_prefix}, {scene_template}, {character_anchor}, {action}, {style_lock}"
    scene_only: "{image_prompt_prefix}, {scene_template}, {atmosphere}, {style_lock}"
  style_lock: [...from EP_STATE]
  image_prompt_prefix: "...from style_decision"
```

**CRITICAL**: The `anchor_description` and `template_prefix` in the preview_manifest are now LOCKED. The generate stage must copy them verbatim into every prompt.

### 5. Quality Gate

- [ ] Every character in `character_registry` has a generated anchor image
- [ ] Every scene in `scene_registry` has a generated scene sample image
- [ ] User has confirmed: characters look correct, scenes match expectations
- [ ] All images are saved to the project assets directory
- [ ] `preview_manifest` artifact is schema-valid

## Common Pitfalls

- **Modifying anchor descriptions during generation**: If the first render doesn't look right, revise the description in `character_registry`, NOT in the prompt. The registry is the source of truth.
- **Skipping the user review**: This is a `human_approval_default: true` stage. Always present images and wait for confirmation.
- **Generating too many characters at once**: Generate one character at a time so the user can give focused feedback.
- **Using different style keywords**: Always use the same `style_lock` for preview as for the final panels. The preview IS the style reference.
- **Low-quality anchors**: If a character anchor looks bad, regenerate it now. A bad anchor will produce bad panels in every subsequent stage.
