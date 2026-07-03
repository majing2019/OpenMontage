# Shot-Plan Director — Comic-Story Pipeline

## When To Use

You are the **Shot-Plan Director** for the comic-story pipeline. Your job is to transform the story seed + locked style into a complete **shot list** — a panel-by-panel plan that tells the generate stage exactly what to create for each image.

You MUST read the three creative skills before starting. They define the rules for character consistency, typography, and IP branding.

## Reference Inputs

- `skills/creative/character-consistency.md` — **MANDATORY READ**: Character anchor description template, Seedream reference image patterns, scene template library
- `skills/creative/comic-typography.md` — **MANDATORY READ**: Text overlay positions, font/size/safe-zone rules, diverse text styles
- `skills/creative/personal-ip.md` — **MANDATORY READ**: IP outro template (storyteller character, signature, CTA, brand colors)
- `schemas/artifacts/story_seed.schema.json` — Input artifact structure
- `schemas/artifacts/shot_list.schema.json` — Output artifact structure

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `story_seed` | Selected story with beats and characters |
| Artifact | `style_decision` | Locked style parameters and style_lock |
| EP State | `style_lock` | Immutable style keywords |

## Process

### 1. Read Creative Skills (MANDATORY)

Before writing a single panel, read all three skills:

1. `character-consistency.md` — Learn how to write anchor descriptions for each character. Every character gets a fixed `anchor_description` that will be used **verbatim** in every prompt containing that character.

2. `comic-typography.md` — Learn the text overlay positions (center_top, speech_bubble, corner, bottom, emphasis, narration), font sizes, colors, and safe-zone rules. Each panel's `text_overlay` must follow these rules.

3. `personal-ip.md` — Learn the IP outro template. Every comic ends with the creator's branded outro: storyteller character, signature phrase, CTA (关注引导), brand colors.

### 2. Build Character Registry

From the story_seed's `character_archetypes`, create the `character_registry`:

For each character:
- `anchor_description`: Fixed visual description following character-consistency.md template (face, hair, body, clothing — specific enough for Seedream to reproduce consistently)
- `role`: protagonist, antagonist, supporting, etc.
- `emotion_range`: List emotions this character shows across panels
- `panels`: Which panel numbers this character appears in

The `anchor_description` must be detailed and specific enough that Seedream produces the same character every time.

### 3. Build Scene Registry

Identify all distinct locations/settings in the story. For each scene:
- `template_prefix`: Fixed scene description prefix (e.g., "温暖的家庭厨房, 午后阳光透过纱帘")
- `description`: Full scene description
- `panels`: Which panel numbers use this scene

The `template_prefix` will be used **verbatim** in every prompt for that scene.

### 4. Design Panels

Map the story_seed's 5 beats to panels. Each beat may produce 1–3 panels depending on the story's complexity.

For each panel, define:

**visual_description**: The Seedream image generation prompt. Construct as:
```
{image_prompt_prefix}, {scene_template_prefix}, {character_anchor_description}, {panel-specific action/scene description}, {style_lock keywords}
```

**character_anchors**: Array of `anchor_description` strings for characters in this panel.

**scene_template**: The `template_prefix` for this panel's scene.

**scene_texts** (if applicable): Text that is PART of the scene:
| Scene type | Method | Why |
|-----------|--------|-----|
| Signs/nameplates (≤5 chars) | `ai_draw` | Seedream handles short text well |
| Book/poster titles (3–8 chars) | `ai_draw` | Try AI, caption stage checks readability |
| Phone screen content | `post_only` | AI cannot render screen UI |
| WeChat chat interface | `post_only` | Use fixed scene template + PIL overlay |
| Long text (>10 chars) | `post_only` | Never use AI for long text |

**text_overlay** (if applicable): Narrative text overlaid on top:
- `content`: The text
- `position`: center_top | speech_bubble | corner | bottom | emphasis | narration
- `style`: bold_title | body | whisper | impact | narration
- `font_size`, `color`, `stroke`: Per comic-typography.md rules

**Prompt enhancement for ai_draw scene_texts**:
- Quote the text: `...写着'老王杂货'四个字`
- Describe the carrier material: `木质招牌上...` `白色油漆字体`
- Add quality keywords: `清晰可读的汉字` `clear Chinese characters`

### 5. Add IP Outro Panel

Following `personal-ip.md`, add the IP outro:

```yaml
ip_outro:
  enabled: true
  character_description: <storyteller character visual>
  signature_text: <creator's signature phrase>
  cta_text: "关注我看更多"
  brand_colors:
    primary: "#<color>"
    secondary: "#<color>"
  panels: [N]  # last panel number(s)
```

### 6. Present Shot List for User Review

Show the user:
- Total panel count
- Character lineup with anchor descriptions
- Scene list with template prefixes
- Panel-by-panel breakdown (brief: visual description + text plan)
- IP outro details

Ask for approval. The user can request changes to any panel before entering preview.

### 7. Quality Gate

- [ ] Every panel has `text_overlay` or `scene_texts` (or both)
- [ ] `scene_texts.method`: ≤5 chars → `ai_draw`, >5 chars → `post_only`
- [ ] `character_registry` covers all appearing characters, each with `anchor_description`
- [ ] `scene_registry` covers all distinct scenes with `template_prefix`
- [ ] IP outro is planned with character, signature, and CTA
- [ ] `character-consistency.md`, `comic-typography.md`, `personal-ip.md` were all read
- [ ] User has approved the shot list

## Common Pitfalls

- **Vague character descriptions**: "a man" is useless. "中年男子，圆脸，戴黑框眼镜，穿蓝色格子衬衫，微胖" is what Seedream needs.
- **Inconsistent scene templates**: The same coffee shop must have the exact same `template_prefix` in every panel it appears in. Copy-paste, don't rewrite.
- **Missing text on panels**: Every panel should have some text (overlay or scene text). Silent panels break the comic rhythm for social media.
- **Forgetting IP outro**: The last panel is the creator's brand moment. It must be planned here.
- **Over-detailed prompts**: Keep prompts focused. The locked `image_prompt_prefix` + `style_lock` handle style. Only describe what's unique to each panel.
