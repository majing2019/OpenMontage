# Compose Director — Comic-Story Pipeline

## When To Use

You are the **Compose Director** for the comic-story pipeline. Your job is to **validate and package** the final image sequence — verify completeness, enforce consistent naming, check resolution, and output the final panel files.

This pipeline does NOT use `video_compose`. The output is a **PNG image sequence**, not a video.

## Reference Inputs

- `schemas/artifacts/shot_list.schema.json` — Panel count and IP outro definition
- `schemas/artifacts/captioned_assets.schema.json` — Captioned panel image paths

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `captioned_assets` | Final captioned panel images |
| Artifact | `shot_list` | Panel count, IP outro definition |
| Artifact | `style_decision` | Color palette for validation context |

## Process

### 1. Validate Image Integrity

For each captioned panel in `captioned_assets.panels`:

```python
from PIL import Image

img = Image.open(panel.image_path)
img.verify()  # Raises if corrupted
img = Image.open(panel.image_path)  # Re-open after verify
width, height = img.size
```

Check:
- [ ] File exists at the declared path
- [ ] PIL can open the file without errors
- [ ] Image is not corrupted (verify passes)
- [ ] Image format is PNG
- [ ] Record width and height for resolution consistency check

If any image fails validation:
- Attempt to regenerate from the uncaptioned source + text overlay
- If regeneration fails, log the issue and proceed with warnings

### 2. Validate Resolution Consistency

All panels MUST have identical width and height:

```
expected_width = panels[0].width
expected_height = panels[0].height

for panel in panels[1:]:
    assert panel.width == expected_width
    assert panel.height == expected_height
```

If resolution mismatch is detected:
- Identify the outlier panels
- Attempt to resize to match the majority resolution
- If resize quality is unacceptable, log and proceed with warnings

### 3. Verify IP Outro

Check that the **last panel** contains the IP outro:

- Verify the last panel number matches `shot_list.ip_outro.panels`
- Visually confirm the last panel has:
  - Storyteller character
  - Signature text
  - CTA text (关注引导)
  - Brand colors

If the IP outro is missing from the last panel, this is a critical finding.

### 4. Rename and Organize Files

Copy/rename captioned images to final output directory:

```
projects/<name>/renders/
  panel_01.png
  panel_02.png
  panel_03.png
  ...
  panel_XX.png  (last panel = IP outro)
```

Naming rules:
- Zero-padded: `panel_01.png`, `panel_02.png`, etc.
- Sequential by `panel_number` from shot_list
- Total count must match `shot_list.panels` count (including IP outro panels)

### 5. Generate Render Report

```yaml
render_report:
  version: "1.0"
  output_format: "image_sequence"
  output_directory: "projects/<name>/renders/"
  total_panels: N
  resolution:
    width: W
    height: H
  files:
    - panel_01.png
    - panel_02.png
    - ...
    - panel_XX.png
  ip_outro_present: true
  validation:
    all_images_valid: true
    resolution_consistent: true
    ip_outro_in_last_panel: true
    total_matches_shot_list: true
  issues: []
  generated_at: <timestamp>
```

### 6. Quality Gate

- [ ] All captioned images exist and are valid (PIL verify passes)
- [ ] All images have identical resolution (width and height)
- [ ] IP outro is present in the last panel
- [ ] File naming follows `panel_XX.png` sequential format
- [ ] Total panel count matches `shot_list.panels` count
- [ ] Final images are in `projects/<name>/renders/`
- [ ] `render_report` artifact is schema-valid

## Common Pitfalls

- **Corrupted images**: Rare but possible after PIL text overlay. Always verify before packaging.
- **Mixed resolutions**: If Seedream produces different sizes on different calls, all panels must be resized to match. Check early.
- **Missing IP outro**: The last panel MUST be the IP outro. If it's a regular story panel, the IP branding is missing.
- **Wrong panel order**: Panel numbering must be sequential. Gaps or out-of-order panels break the story flow.
- **Over-writing source images**: Always copy to the renders/ directory, never modify the source captioned images.
