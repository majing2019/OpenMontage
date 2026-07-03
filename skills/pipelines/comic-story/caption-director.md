# Caption Director — Comic-Story Pipeline

## When To Use

You are the **Caption Director** for the comic-story pipeline. Your job is to overlay text onto the generated panel images — both narrative text (`text_overlay`) and scene text corrections (`scene_texts` with `post_only` or garbled `ai_draw` text).

This stage requires **user approval** because text placement and readability directly affect the final product quality.

## Reference Inputs

- `skills/creative/comic-typography.md` — **MANDATORY READ**: Text overlay positions, font/size/safe-zone rules
- `schemas/artifacts/shot_list.schema.json` — Panel text definitions
- `schemas/artifacts/preview_manifest.schema.json` — Panel images (source)

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `shot_list` | Panel text_overlay and scene_texts definitions |
| Artifact | `asset_manifest` | Panel image paths |
| Artifact | `style_decision` | Color palette for text styling |
| Skill | `creative/comic-typography.md` | Typography rules and safe zones |

## Process

### 1. Read Typography Rules (MANDATORY)

Read `comic-typography.md` before processing any text. Key rules:
- **Safe zones**: Text must not overlap character facial expressions
- **Position mapping**: Each `text_overlay.position` maps to specific pixel coordinates
- **Font sizes**: Minimum sizes for readability on mobile
- **Color and stroke**: Ensure contrast ≥ 4.5:1 against the image background
- **Diverse styles**: bold_title, body, whisper, impact, narration each have distinct styling

### 2. Process Each Panel

For each panel in order:

#### A. Text Overlay Processing (`text_overlay`)

From `shot_list.panels[i].text_overlay`:

1. **Position calculation**: Map the `position` field to pixel coordinates
   - `center_top`: Top center, below safe zone
   - `speech_bubble`: Above or near the speaking character's head
   - `corner`: Bottom-left or bottom-right corner
   - `bottom`: Bottom center, above safe zone
   - `emphasis`: Center of frame, large impact text
   - `narration`: Top or bottom band, serif font, muted color

2. **Style application**: Map `style` to font properties
   - `bold_title`: Large, bold, white with black stroke
   - `body`: Medium, regular weight
   - `whisper`: Small, light, italic-like, muted color
   - `impact`: Very large, bold, red/yellow accent
   - `narration`: Medium, serif, semi-transparent background band

3. **Render with PIL**:
   - Open panel image
   - Apply text with specified font, size, color, stroke
   - Check contrast ratio (text color vs. background at text position)
   - Save captioned image to: `projects/<name>/assets/images/captioned_panel_{panel_number:02d}.png`

#### B. Scene Text Processing (`scene_texts`)

For each scene_text in the panel:

**`ai_draw` method — check readability**:
1. Open the generated panel image
2. Check if the AI-rendered text is clear and correct
3. If **clear and correct**: keep as-is, no PIL overlay needed
4. If **garbled or incorrect**: apply PIL overlay as fixup (same as post_only)
   - Record in `scene_text_fixups` with reason

**`post_only` method — PIL overlay**:
1. Calculate position based on `carrier` description
   - Phone screen: center of device area
   - Sign: at the sign location
   - Chat interface: inside the chat bubble area
2. Render text with PIL using appropriate font and size
3. For angled/tilted text (e.g., slanted signs): use PIL perspective transform to match the angle
4. Apply to the panel image

### 3. Present Captioned Panels for Review

Show each captioned panel to the user. For each panel:

- Display the image with all text overlays applied
- Highlight: text position, font size, color, stroke
- Ask: "文字位置、大小、可读性 OK 吗？"
- If user requests changes: adjust position, size, or color and re-apply (max 3 revisions per panel)

### 4. Build Captioned Assets Manifest

```yaml
captioned_assets:
  version: "1.0"
  panels:
    - panel_number: 1
      image_path: "projects/<name>/assets/images/captioned_panel_01.png"
      source_image_path: "projects/<name>/assets/images/panel_01.png"
      text_overlays_applied:
        - content: "加班第一天"
          position: center_top
          style: bold_title
          font_size: "60"
          color: "#FFFFFF"
          stroke: "#000000"
      scene_text_fixups: []
      contrast_ratio: 8.5
  text_overlay_summary:
    total_panels: N
    panels_with_text_overlay: M
    panels_with_scene_text_fixup: K
    all_pass_contrast_check: true
    typography_rules_followed: true
  typography_rules: [...from comic-typography.md]
```

### 5. Quality Gate

- [ ] All captioned images exist and are readable
- [ ] Text contrast ratio ≥ 4.5:1 (WCAG AA) for all overlays
- [ ] Text positions follow `comic-typography.md` rules
- [ ] No text overlaps character facial expressions (safe zones respected)
- [ ] `ai_draw` text checked: clear text kept, garbled text replaced with PIL
- [ ] `post_only` text rendered correctly with PIL
- [ ] User has approved the typography quality
- [ ] `captioned_assets` artifact is schema-valid

## Common Pitfalls

- **Text too small**: Mobile viewers need larger text. Minimum 40px for body text, 60px for titles.
- **Poor contrast**: White text on bright backgrounds, or dark text on dark backgrounds. Always check contrast ratio.
- **Text over faces**: The most common mistake. Always position text in designated safe zones AWAY from character expressions.
- **Missing PIL perspective**: Angled signs need perspective-matched text. Flat text on a tilted surface looks obviously wrong.
- **Skipping the readability check on ai_draw text**: Seedream sometimes produces garbled characters even for short text. Always check.
- **Inconsistent styling**: Use the same font family and color scheme across all panels unless the story specifically calls for a change.
