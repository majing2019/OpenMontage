# Caption Director — Comic-Story Pipeline

## When To Use

You are the **Caption Director** for the comic-story pipeline. Your job is to overlay narrative caption text onto panel images AND resize them to the final video resolution (720×1280) in one step.

This stage requires **user approval** because text readability directly affects the final product.

## Core Convention: Caption Stage = Final Resolution

The caption stage produces **720×1280** images ready for video composition. No further resizing happens downstream.

## Reference Inputs

- `skills/creative/comic-typography.md` — Text overlay positions, font rules, safe zones
- `schemas/artifacts/shot_list.schema.json` — Panel `text_overlay` definitions
- `schemas/artifacts/style_decision.json` — Color palette context

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `shot_list` | Panel text_overlay content per panel |
| Artifact | `asset_manifest` | Panel image paths (1080×1080 source) |
| Skill | `creative/comic-typography.md` | Typography rules |

## Hard Rules

### Rule 1: Uniform Caption Style

ALL panels use the **exact same** caption style — position, font, font size, color. The only thing that varies is the text content.

| Property | Value |
|----------|-------|
| Font | PingFang SC Regular (macOS system font, index 3 in PingFang.ttc) |
| Font size | **36px fixed** — never shrinks for long text |
| Text color | `#FFFFFF` (white) |
| Stroke | `#000000` (black), 2px width |
| Band color | Semi-transparent black, alpha=160 (~63% opacity) |
| Band position | Right below the image, no gap |
| Text alignment | Centered horizontally within band |
| Text padding | 20px from top of band |

### Rule 2: Band Grows, Font Never Shrinks

- Short text (1 line): band is ~86px tall (line height + 40px padding)
- Medium text (2 lines): band is ~130px tall
- Long text (3+ lines): band grows accordingly
- **Never reduce font size.** The 36px font is the minimum for mobile readability.

### Rule 3: Image + Band Centered Vertically

The 1080×1080 source image is scaled to 720×720 and placed above the caption band (no gap). The entire image+band block is centered vertically in the 720×1280 canvas. White padding (255,255,255) fills the remaining space — this matches all comic art styles (line-comic, clean-comic, warm-illustration).

### Rule 4: No Scene Text Overlays

Scene texts (speech bubbles, phone screens, inner monologues) are **already drawn by the AI** during the generate stage. Do NOT overlay them again with PIL. Only apply `text_overlay` (narration caption).

## Process

### 1. For Each Panel

```python
TARGET_W, TARGET_H = 720, 1280
FONT_SIZE = 36
BAND_ALPHA = 160
MARGIN_X = 60
BAND_SIDE_PAD = 20  # inner padding above/below text

# Load and scale source
img = Image.open("panel_XX.png")  # 1080×1080
scale = TARGET_W / img.width
new_h = int(img.height * scale)
img_resized = img.resize((TARGET_W, new_h), Image.LANCZOS)

# Measure text to determine band height
content = shot_list.panels[i].text_overlay.content  # skip if empty
if content:
    font = ImageFont.truetype(PINGFANG_TTC, 36, index=3)
    lines = wrap_text(content, font, max_width=TARGET_W - 120)
    line_h = measure_line_height(font)
    band_h = line_h * len(lines) + BAND_SIDE_PAD * 2
else:
    band_h = 0

# Center image+band vertically
img_y = (1280 - (new_h + band_h)) // 2
band_y = img_y + new_h

# Create white canvas
canvas = Image.new("RGBA", (720, 1280), (255, 255, 255, 255))
canvas.paste(img_resized, (0, img_y))

# Draw caption band and text
if content:
    band = Image.new("RGBA", (720, band_h), (0, 0, 0, 160))
    canvas.paste(band, (0, band_y))

    draw = ImageDraw.Draw(canvas)
    text_y = band_y + BAND_SIDE_PAD
    for i, line in enumerate(lines):
        line_y = text_y + i * line_h
        # Center each line
        lw = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
        line_x = (720 - lw) // 2
        draw_text_with_stroke(draw, line, (line_x, line_y), font, "#FFF", "#000", 2)

# Save
canvas.convert("RGB").save("captioned_panel_XX.png", "PNG")
```

### 2. Text Wrapping: Break at Sentences

Prefer breaking at sentence-ending punctuation so each line is a complete phrase:

```
Break AFTER: 。！？…—
Break AFTER: ，；：、(fallback)
Otherwise: break at character boundary
```

### 3. Panel 13 (IP Outro)

The last panel has an **empty** `text_overlay.content`. Skip the caption band entirely — the IP outro (character + signature + CTA) is already drawn in the image by the generate stage.

### 4. Output

Save to: `projects/<name>/assets/images/captioned_panel_{panel_number:02d}.png`

All outputs are **720×1280 RGB PNG** — ready for FFmpeg composition without further processing.

## Quality Gate

- [ ] All captioned images exist at 720×1280
- [ ] Font size is exactly 36px on every panel (check visually)
- [ ] Band is flush against image bottom, no gap
- [ ] Image+band block is vertically centered
- [ ] Text does not overlap character facial expressions
- [ ] No duplicate text (scene_texts NOT overlaid)
- [ ] Panel 13 has no caption band
- [ ] `captioned_assets` artifact is schema-valid

## Common Pitfalls

- **Shrinking font for long text**: Never do this. Grow the band instead.
- **Double-overlaying scene text**: AI already drew speech bubbles, phone messages, etc. Only overlay `text_overlay`.
- **Stretching images**: Scale preserving aspect ratio, fill empty space with white.
- **Inconsistent band height**: Band height varies by text length but all other properties (font, color, padding) are identical.
