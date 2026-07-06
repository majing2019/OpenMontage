# Compose Director — Comic-Story Pipeline

## When To Use

You are the **Compose Director** for the comic-story pipeline. Your job is to **validate the captioned image sequence and compose it into a final MP4 slideshow video** with transition effects between panels.

The output is a **video file** (`final.mp4`), not just a PNG image sequence. This pipeline uses **FFmpeg xfade** for transitions — not `video_compose`.

## Reference Inputs

- `schemas/artifacts/shot_list.schema.json` — Panel count, duration_seconds, and IP outro definition
- `schemas/artifacts/captioned_assets.schema.json` — Captioned panel image paths

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `captioned_assets` | Final captioned panel images |
| Artifact | `shot_list` | Panel count, duration_seconds, IP outro definition |
| Artifact | `style_decision` | Color palette for validation context |
| Tool | `ffmpeg` (system binary) | Video composition via xfade filter |

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
- Resize to match the majority resolution using PIL (LANCZOS for downscale, BICUBIC for upscale)
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

### 4. Stage Panels (Already 720×1280 from Caption Stage)

Captioned panel images arrive at **720×1280** from the caption stage — no resizing needed. Simply copy them to the staging directory for FFmpeg:

```
projects/<name>/assets/images/staging/
  panel_01.png  (copy of captioned_panel_01.png)
  panel_02.png
  ...
```

The caption stage handles all layout: image scaling, vertical centering, caption band placement, and white padding. The compose stage just assembles these ready-to-use frames.

### 5. Compose Video with FFmpeg xfade

Build an FFmpeg command that creates a slideshow video with fade transitions between panels.

**Parameters:**
- Target resolution: 720×1280 (9:16 竖屏)
- Frame rate: 30 fps
- Transition: `xfade` with `fade` effect
- Transition duration: 0.5 seconds
- Per-panel duration: from `shot_list.panels[i].duration_seconds`
- Output codec: H.264 (libx264)
- No audio track

**Duration per panel after transition adjustment:**
Each panel needs to be extended to accommodate the outgoing transition. For N panels with xfade:
- First panel: shows for `duration_seconds` seconds, then transitions out
- Middle panels: transition in from previous (overlapping 0.5s), show for `duration_seconds`, transition out
- Last panel: transitions in from previous, shows for remaining duration

**FFmpeg command construction:**

For a simple 2-panel case:
```bash
ffmpeg -loop 1 -t 5 -i panel_01.png \
       -loop 1 -t 5 -i panel_02.png \
       -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=4.5[v]" \
       -map "[v]" -c:v libx264 -pix_fmt yuv420p -r 30 -vf "scale=720:1280" final.mp4
```

For N panels, chain xfade filters sequentially. The `offset` for each transition is cumulative:
```
offset_1 = duration_panel_1 - transition_duration
offset_2 = offset_1 + duration_panel_2 - transition_duration
offset_k = offset_(k-1) + duration_panel_k - transition_duration
```

**Python helper to build the FFmpeg command:**

```python
import subprocess

panels = sorted_panels  # ordered by panel_number
durations = [p.duration_seconds for p in panels]
transition_duration = 0.5
n = len(panels)

# Build input arguments
inputs = []
for p in panels:
    inputs.extend(["-loop", "1", "-t", str(d), "-i", p.resized_path])

# Build xfade filter chain
# Start with [0:v] as base
if n == 1:
    # Single panel — just convert to video, no transition needed
    filter_complex = "[0:v]scale=720:1280,format=yuv420p[v]"
else:
    parts = []
    prev_label = "0:v"
    offset = durations[0] - transition_duration

    for i in range(1, n):
        next_label = f"[v{i}]" if i < n - 1 else "[v]"
        parts.append(f"[{prev_label}][{i}:v]xfade=transition=fade:duration={transition_duration}:offset={offset:.1f}{next_label}")
        if i < n - 1:
            prev_label = f"v{i}"
            offset += durations[i] - transition_duration

    filter_complex = ",".join(parts) + ",scale=720:1280,format=yuv420p[v]"
    # Fix: xfade already outputs at correct size if inputs are resized, scale is safety net
    # Actually xfade outputs need to be chained properly
    # Simpler approach: build chain correctly
```

**Simpler approach — use concat with xfade chain:**

```python
def build_ffmpeg_xfade_command(panels, durations, output_path):
    """Build FFmpeg command for N-panel slideshow with fade transitions."""
    n = len(panels)
    transition_dur = 0.5

    if n == 1:
        return [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(durations[0]), "-i", panels[0],
            "-vf", "scale=720:1280,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-r", "30", "-t", str(durations[0]),
            output_path
        ]

    # Build inputs
    args = ["ffmpeg", "-y"]
    for i, (panel, dur) in enumerate(zip(panels, durations)):
        args.extend(["-loop", "1", "-t", str(dur), "-i", panel])

    # Build xfade filter chain
    filter_parts = []
    offset = durations[0] - transition_dur

    for i in range(1, n):
        if i == 1:
            in_left = "0:v"
        else:
            in_left = f"[v{i-1}]"
        in_right = f"{i}:v"

        if i == n - 1:
            out_label = "[v]"
        else:
            out_label = f"[v{i}]"

        filter_parts.append(
            f"[{in_left}][{in_right}]xfade=transition=fade:duration={transition_dur}:offset={offset:.1f}{out_label}"
        )
        if i < n - 1:
            offset += durations[i] - transition_dur

    filter_complex = ";".join(filter_parts) + ";[v]scale=720:1280,format=yuv420p[vout]"

    args.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-r", "30",
        output_path
    ])

    return args
```

**Execute:**
```bash
python -c "
import subprocess, json

panels = [...]  # sorted resized panel paths
durations = [...]  # from shot_list.panels[i].duration_seconds
output = 'projects/<name>/renders/final.mp4'

# Build and run command (use helper function above)
result = subprocess.run(build_ffmpeg_xfade_command(panels, durations, output),
                        capture_output=True, text=True)
if result.returncode != 0:
    print('FFmpeg error:', result.stderr)
else:
    print('Video created successfully')
"
```

**Edge cases:**
- **Single panel**: No xfade needed. Convert one image to a short video clip.
- **Panel duration ≤ 1 second**: Skip transition for that panel boundary — use cut instead of fade. Adjust the xfade chain to use `transition=fadeblack` or simply concat without xfade for that segment.
- **Resolution mismatch**: All panels must be resized to 720×1280 before xfade (xfade requires identical input dimensions).

### 6. Verify Output Video

Use ffprobe to validate the output:

```bash
ffprobe -v quiet -print_format json -show_format -show_streams projects/<name>/renders/final.mp4
```

Verify:
- [ ] File exists and is non-empty
- [ ] Video codec is h264
- [ ] Resolution is 720×1280
- [ ] Frame rate is 30 fps
- [ ] Duration is approximately: Σ(durations) - (N-1) × 0.5s (within ±1s tolerance)
- [ ] No audio stream (or silent audio if ffmpeg auto-added one — acceptable)

If verification fails:
- Check the FFmpeg stderr for filter errors
- Common issue: xfade offset exceeds input duration → adjust offsets
- Common issue: resolution mismatch between inputs → re-run resize step

### 7. Generate Render Report

```yaml
render_report:
  version: "1.0"
  output_format: "mp4"
  output_directory: "projects/<name>/renders/"
  output_file: "final.mp4"
  total_panels: N
  video:
    codec: "h264"
    resolution: "720x1280"
    fps: 30
    duration_seconds: XX.X
    transition_type: "xfade_fade"
    transition_duration_seconds: 0.5
    file_size_bytes: XXXXXXXX
  panels:
    - panel_number: 1
      source_image: "captioned_panel_01.png"
      duration_seconds: 4
    - panel_number: 2
      source_image: "captioned_panel_02.png"
      duration_seconds: 3
    - ...
  ip_outro_present: true
  validation:
    all_images_valid: true
    resolution_consistent: true
    video_codec_correct: true
    video_resolution_correct: true
    video_duration_within_tolerance: true
    ip_outro_in_last_panel: true
    total_matches_shot_list: true
  issues: []
  generated_at: <timestamp>
```

### 8. Cleanup Staging Files

After successful video creation, remove the temporary staging directory:
```
projects/<name>/assets/images/staging/  → delete
```

Keep the source captioned images in place — they are the canonical assets.

### 9. Quality Gate

- [ ] All captioned images exist and are valid (PIL verify passes)
- [ ] All images resized to 720×1280 consistently
- [ ] IP outro is present in the last panel
- [ ] FFmpeg xfade command executed without errors
- [ ] Output final.mp4 exists and is non-empty
- [ ] Video codec is h264, resolution is 720×1280, fps is 30
- [ ] Video duration is within ±1s of expected
- [ ] `render_report` artifact is schema-valid

## Common Pitfalls

- **Corrupted images**: Rare but possible after PIL text overlay. Always verify before packaging.
- **Mixed resolutions**: If Seedream produces different sizes, all panels must be resized to 720×1280 before xfade. xfade requires identical input dimensions.
- **xfade offset errors**: The offset must equal the accumulated duration minus transition overlaps. Off-by-one errors in the offset chain cause FFmpeg to fail with "offset is too large" or produce a video with missing frames.
- **Missing IP outro**: The last panel MUST be the IP outro. If it's a regular story panel, the IP branding is missing.
- **Wrong panel order**: Panel numbering must be sequential. Gaps or out-of-order panels break the story flow.
- **Over-writing source images**: Always resize to staging/ directory, never modify the source captioned images.
- **FFmpeg not installed**: Verify `ffmpeg` is available on the system before attempting composition. This is a required dependency for this stage.
- **Single-panel video**: A single panel still needs to be converted to video (no xfade). Don't forget this edge case.
