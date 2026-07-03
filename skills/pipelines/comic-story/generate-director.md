# Generate Director — Comic-Story Pipeline

## When To Use

You are the **Generate Director** for the comic-story pipeline. Your job is to produce all panel images using the **locked** character anchors, scene templates, and style parameters from the preview stage.

This stage runs **automatically** (no human approval required) because the character and scene decisions were already confirmed in the preview stage.

## Reference Inputs

- `schemas/artifacts/preview_manifest.schema.json` — Locked character anchors and scene templates
- `schemas/artifacts/shot_list.schema.json` — Panel definitions and text plans
- `skills/creative/character-consistency.md` — Character prompt construction rules

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `shot_list` | Panel definitions (visual_description, character_anchors, scene_texts) |
| Artifact | `preview_manifest` | Locked character anchors + scene samples |
| Artifact | `style_decision` | Locked style (style_lock, image_prompt_prefix, negative_prompt) |
| EP State | `style_lock` | Immutable style keywords |
| Tool | `image_selector` | Image generation (routes to Seedream) |

## Process

### 1. Verify Lock State

Before generating any image, verify:
- `style_decision.style_lock` is populated (≥ 3 keywords)
- `preview_manifest.character_anchors` has all characters with `anchor_description`
- `preview_manifest.scene_samples` has all scenes with `template_prefix`
- `shot_list.panels` defines every panel to generate

### 2. Construct Prompts Per Panel

For each panel in `shot_list.panels`:

**Base prompt template** (from preview_manifest):
```
{style_decision.image_prompt_prefix},
{scene.template_prefix},
{character.anchor_description for each character in panel},
{panel.visual_description},
{EP_STATE.style_lock keywords joined with commas}
```

**Scene text enhancement** (for panels with `scene_texts` where `method = ai_draw`):
- Quote the text content: `...写着'{content}'这几个字`
- Describe carrier material: `{carrier}上...`
- Add quality keywords: `清晰可读的汉字` `clear Chinese characters`
- Only for ≤5 character texts — longer texts are `post_only`

**Post-only scene text** (for panels with `method = post_only`):
- Generate the scene **without** the text content (e.g., blank phone screen, white chat background)
- The caption stage will overlay the text later

**CRITICAL RULES**:
1. **NEVER modify `anchor_description`** — use it verbatim from preview_manifest
2. **NEVER modify `template_prefix`** — use it verbatim from preview_manifest
3. **ALWAYS append `style_lock`** keywords to every prompt
4. **ALWAYS include negative prompt** from style_decision

### 3. Generate Panels

Generate panels sequentially (not in parallel) to maintain consistency:

1. For each panel in order:
   - Construct the prompt per the template above
   - Call `image_selector` with the prompt
   - Save to: `projects/<name>/assets/images/panel_{panel_number:02d}.png`
   - Record the generation in asset_manifest

### 4. Build Asset Manifest

```yaml
asset_manifest:
  version: "1.0"
  panels:
    - panel_number: 1
      image_path: "projects/<name>/assets/images/panel_01.png"
      prompt_used: "..."
      style_lock: [...]
      tool_used: "image_selector"
      provider: "seedream"
      generated_at: <timestamp>
  total_panels: N
  style_lock_used: [...]
  budget_spent: X.XX
```

### 5. Quality Gate

- [ ] All panel images exist and are readable (can be opened by PIL)
- [ ] All images use the same `style_lock` keywords
- [ ] `anchor_description` and `template_prefix` match preview_manifest verbatim
- [ ] Budget ≤ 90% of configured budget
- [ ] `asset_manifest` artifact is schema-valid

## Common Pitfalls

- **Paraphrasing character descriptions**: The anchor_description must be copied character-for-character. Even a synonym change can alter Seedream's output.
- **Forgetting style_lock**: Every single prompt must end with the style_lock keywords. Missing even one panel breaks visual consistency.
- **Generating in parallel**: Seedream batch requests can produce inconsistent results. Generate sequentially for maximum consistency.
- **Not checking image quality**: After each generation, verify the image is not corrupted and looks reasonable before moving to the next panel.
- **Ignoring budget**: Track cost per image. If approaching the 90% threshold, warn the EP.
