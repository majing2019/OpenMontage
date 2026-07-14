# Compose Director — Healing Text Pipeline

## When To Use

All assets are generated: video clips for emotional peaks, animated/still images
for flow and quiet segments, the font is approved, background music is sourced,
and the script defines timing. Now assemble everything in Remotion: native video
clips playing in sequence, still images with gentle Ken Burns, top-center text
overlays, background music, and dual aspect-ratio export.

Background music is mixed in via Remotion `<Audio>` component. Video source clips
must be silent (stripped by asset director). The compose stage adds the music bed.
Music volume is approximately 0.12 with 2s fade-in and 3s fade-out.

When `tts_enabled` is true, narration audio is mixed with the music bed using
sidechain ducking. Music volume dips during speech (~0.08) and rises between
segments (~0.12). Subtitles remain active regardless of narration state.

## Runtime Routing (MANDATORY)

This pipeline **REQUIRES Remotion**. The healing aesthetic depends on:
- Native video clip playback with smooth crossfade transitions
- Gentle Ken Burns (slow zoom/pan) on still images only
- Spring-animated text fades (top-center position)
- Per-character text reveal for emphasis lines
- Responsive layout for dual aspect ratio
- Background music via `<Audio>` component

**For ai-generated mode:** `render_runtime` MUST be `"remotion"`. FFmpeg-only fallback = slideshow = not acceptable.

**For stock-footage mode (all video clips):** `render_runtime: "ffmpeg"` is ACCEPTABLE. When every segment is a video clip (no still images, no Ken Burns), FFmpeg concat with crossfade transitions produces identical visual quality to Remotion. Remotion is still PREFERRED if available (text animation, spring easing, audio mixing), but FFmpeg is a valid production path.

### Asset Mode Pre-Check

Read `script.metadata.asset_mode` (defaults to `"ai-generated"` if absent):

**If `asset_mode == "stock-footage"`:**
- ALL assets are video clips (no still images). Ken Burns motion is NOT needed.
- Color grade is pre-applied by asset director — do NOT re-grade in compose.
- Music: if no music asset in manifest, produce silent video (graceful degradation, not a failure).
- Subtitle burn via FFmpeg subtitles filter is acceptable (Remotion's per-character reveal is a nice-to-have, not required).
- Crossfade transitions via FFmpeg `xfade` or fade-in/out at clip boundaries.

**If `asset_mode == "ai-generated"` (or not set — default):**
- All existing Remotion requirements apply unchanged.
- `render_runtime` MUST be `"remotion"`. FFmpeg-only fallback = slideshow = not acceptable.

### TTS Mode Pre-Check

Read `script.metadata.tts_enabled` (defaults to `false` if absent):

**If `tts_enabled == true`:**
- Narration audio assets exist in the asset_manifest (type: "audio", subtype: "narration")
- Music ducking is REQUIRED during narration segments
- Two compose paths for audio:
  1. **Remotion path (preferred)**: Pre-mix narration + music via `audio_mixer.full_mix`,
     then pass the mixed audio as `audio.music.src` to video_compose
  2. **FFmpeg path (stock-footage fallback)**: Use `audio_mixer.full_mix` to produce
     a mixed audio track, then mux into the final video
- Segment durations should be influenced by narration duration (see Section 3a)

**If `tts_enabled == false` (or not set):**
- All existing compose behavior applies unchanged
- No narration assets expected in manifest

**Renderer family routing (style-aware):**
- `warm-illustration` and `literary-illustration` → `render_grammar: "healing-text-illustration"` (routes to `Explainer` composition)
- `cinematic-drama` → `render_grammar: "healing-text-cinematic"` (routes to `CinematicRenderer` composition)

Read `script.metadata.selected_playbook` to determine the renderer family.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/render_report.schema.json` | Artifact validation |
| Prior artifacts | `state.artifacts["script"]["script"]`, `state.artifacts["assets"]["asset_manifest"]` | Segments + timings + asset paths |
| Tools | `video_compose`, `subtitle_gen`, `color_grade` | Composition, subtitles, finishing |
| Font | `script.metadata.selected_font` | Approved font |
| Agent Skill | `.agents/skills/remotion/SKILL.md` | Remotion scene types, cut schemas, spring physics |
| Agent Skill | `.agents/skills/remotion-best-practices/SKILL.md` | Remotion quality patterns, performance |
| Agent Skill | `.agents/skills/visual-taste/SKILL.md` | Subtitle layout aesthetics — spacing, weight, color harmony, anti-slop |

## Mandatory Remotion Preflight

```bash
python -c "
from tools.tool_registry import registry
registry.discover()
info = registry.get('video_compose').get_info()
print('Render engines:', info.get('render_engines'))
"
```

If Remotion is not in `render_engines`, STOP. Do not substitute.

## Process

### 1. Verify All Video Clips Are Silent

Before composing, confirm every video asset has no audio:

```bash
for f in projects/<project>/assets/video/*.mp4; do
  has_audio=$(ffprobe -v error -show_entries stream=codec_type "$f" | grep -c audio || true)
  if [ "$has_audio" -gt 0 ]; then
    echo "WARNING: $f has audio — stripping now"
    ffmpeg -i "$f" -an -c:v copy "${f}.silent.mp4" -y && mv "${f}.silent.mp4" "$f"
  fi
done
```

### 1a. Opening Template — Emotion-Guided 片头 (MANDATORY)

Every healing-text video MUST start with a 5-7 second two-part opening:
a hook line, then a title summary. Read `script.opening` for hook_line,
title_line, and style. This scene is NOT part of any script section —
it's a fixed prelude assembled in compose.

**Reference:** `projects/examples/情感励志4.mp4`

**Scene structure (Remotion):**

```
seg_opening (5.0-7.0s total):
  0.0 – 1.5s: Hook Card
    Background: solid black (#000000)
    Text: opening.hook_line, small white sans-serif, center-lower
    Font: Noto Sans SC Light, ~28px (720p vertical, scaled for target resolution)
    Animation: fade in 0.5s, hold, fade out 0.5s

  1.5 – 3.5s: Title Card
    Background: solid black
    Text: opening.title_line, large white serif, center
    Font: Noto Serif SC 600 (literary) or Noto Sans SC 500 (warm)
    Font size: ~60px (720p vertical, scaled via font_size_formula)
    Animation: spring fade-in from below (spring tension=80), hold, fade out at 4.5s

  3.5 – 5.5s: Fade Transition
    seg_01 background image fades in (opacity 0→1, 2s ease)
    Title fades out (opacity 1→0 by 4.5s)
    Music reaches full volume (fade 0→0.12, 3s)

  5.5s+: Main Content
    Title gone, seg_01 image and subtitle fully visible
    Music at normal playback volume
```

**For ffmpeg path (stock-footage only):** Render two short video segments
with `drawtext` and concat:

```bash
# Hook card (1.5s black + hook text)
ffmpeg -f lavfi -i "color=c=black:s=1080x1920:d=1.5" \
  -vf "drawtext=text='最近的焦虑都被这段话治愈了':fontsize=28:\
       fontcolor=white@0.9:x=(w-tw)/2:y=h*0.55" hook.mp4

# Title card (2s black + title text)
ffmpeg -f lavfi -i "color=c=black:s=1080x1920:d=2" \
  -vf "drawtext=text='放下焦虑 与自己和解':fontsize=60:\
       fontcolor=white:x=(w-tw)/2:y=(h-th)/2" title.mp4

# Concat: hook + title + main video
ffmpeg -i hook.mp4 -i title.mp4 -i main_video.mp4 \
  -filter_complex "[0][1][2]concat=n=3:v=1:a=0" final.mp4
```

**Timeline shift:** All script sections shift by `opening.duration_seconds`.
seg_01 start_seconds = opening duration (not 0).

**Opening metadata in render_report:**
```json
"opening": {
    "hook_line": "最近所有的不安，都被这段话治愈了",
    "title_line": "放下焦虑，与自己和解",
    "duration_seconds": 5.5
}
```

### 2. Prepare Subtitle Track

Extract subtitle timing from the script artifact. Each section = one subtitle cue:

```
seg_01 (still):  "生活不是等待暴风雨过去"    00:00-00:05
seg_02 (animate): "而是学会..."              00:05-00:10
seg_03 (video):   "在雨中起舞"  ← peak       00:10-00:15  ← THE moment
seg_04 (animate): "每一滴雨..."              00:15-00:20
seg_05 (still):   "都是生命的礼物"            00:20-00:25
```

Subtitle styling:
- Font: `script.metadata.selected_font`
- **Position: top center** (approximately 15-20% from top edge)
  - For 9:16: slightly higher (12-15% from top) to clear platform UI
  - For 16:9: 18-20% from top for comfortable reading
- **Color (style-aware):**
  - `warm-illustration`: white text with warm shadow (`0 2px 8px rgba(74,55,40,0.4)`)
  - `literary-illustration`: charcoal text (#3C3833) with optional band (`rgba(245,240,235,0.92)`)
  - `cinematic-drama`: white text with dark shadow (`0 2px 8px rgba(0,0,0,0.6)`)
- **Resolution-adaptive font sizing (MANDATORY):**
  Font size is **auto-calculated** from video width + longest text line. Do not hardcode.
  See `transition_defaults.text.font_size_formula` for canonical values.
  All segments use the SAME font size — never vary between segments.

  ```
  font_size = clamp(width × fill_ratio / longest_chars, min_font, max_font)

  Fill ratios (from reference video 情感励志4):
    9:16 → 0.72  (text fills ~72% of screen width — very wide)
    16:9 → 0.40  (traditional subtitle width)

  Example (9:16, 1080×1920, longest line 13 chars):
    font_size = clamp(1080 × 0.72 / 13, 44, 64) = clamp(59.8, 44, 64) = 60px
  ```
- **Text position (MANDATORY):**
  See `transition_defaults.text.text_position`:
  - Both orientations: Alignment=5 (middle-center), MarginV=0
  - Text is centered vertically and horizontally in the frame

- **Character spacing**: For 9:16 vertical, increase Spacing from 2 to 4-6.
  Reference video has noticeably wider character spacing ("字间有呼吸感").

- **Auto-adaptive text color (MANDATORY):**
  Analyze the average luma of the concatenated silent video:
  - Average luma > 128 (light video) → dark text (#3C3833)
  - Average luma ≤ 128 (dark video) → light text (#F0F8FA, cool white with subtle blue tint)
  - Reference: 情感励志4 uses cool near-white RGB(240,248,250)
  - ONE consistent color for the entire video — never change between segments
  - Background band: ALWAYS fully transparent for vertical video
  - Outline: NONE for vertical video (clean look matching reference style)
- Animation: fade in/fade out per pipeline `transition_defaults.text` (default: 0.7s in, 0.5s out)
- Multi-line: generous line spacing per `transition_defaults.text.line_height_ratio` (default: 1.6×)
- **Text fades are independent of video crossfade** — see "Text Fade Independence" below

### 3. Design the Visual Timeline

The timeline alternates asset types. Remotion handles each differently:

```
SEG_01 (still)        SEG_02 (animate)      SEG_03 (video)        SEG_04 (animate)     SEG_05 (still)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Still image      │  │ Video clip      │  │ AI VIDEO CLIP   │  │ Animated img    │  │ Still image     │
│ Ken Burns 1.02→  │  │ (stock/img2vid) │  │ (Seedance)      │  │ (stock/img2vid) │  │ Ken Burns 1.02→ │
│ 1.08x slow zoom  │  │ Native playback │  │ Native playback │  │ Native playback │  │ 1.08x, pan up   │
│                  │  │                 │  │ ← THE PEAK      │  │                 │  │                  │
│ [subtitle]       │  │ [subtitle]      │  │ [BIG subtitle]  │  │ [subtitle]      │  │ [subtitle]       │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
    0-5s                 5-10s                10-15s                15-20s               20-25s
```

**Asset type handling:**

| Asset type | Remotion treatment | Duration source |
|------------|-------------------|-----------------|
| `video` (generated) | Play natively at 1.0× speed | Video file duration (4-5s) |
| `video` (stock) | Play natively, trim to segment duration | Segment `end - start` |
| `image` (still) | Ken Burns: scale 1.02→1.08, spring easing | Segment duration |
| `image` (animated) | If already video, play natively; else Ken Burns | Segment or file duration |

**Ken Burns on still images (ONLY):**
- Scale: 1.02 → 1.08 (barely perceptible)
- Pan direction: vary — left, right, up, center-stable
- Easing: `spring()` with low tension
- Do NOT apply Ken Burns to video clips — they already have motion

**Stock-footage timeline (all video clips):**
When every segment is a stock video clip, the timeline simplifies:

```
SEG_01 (video)         SEG_02 (video)         SEG_03 (video)         ...
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Stock video     │  │ Stock video     │  │ Stock video     │
│ (color graded)  │  │ (color graded)  │  │ (color graded)  │
│ Native playback │  │ Native playback │  │ Native playback │
│ Trim to seg dur │  │ Trim to seg dur │  │ Trim to seg dur │
│ [subtitle]      │  │ [subtitle]      │  │ [subtitle]      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

No Ken Burns. No still images. Every clip plays natively. Trim each
to exactly its segment duration. Fade-in/fade-out transitions between
all segments. This is a pure video edit with text overlay.

**Peak segment treatment:**
The `video` tier segment (emotional peak) gets special treatment:
- Subtitle enters slightly later (0.5s into the clip) for dramatic pause
- Slightly larger font size for emphasis (+10%)
- Longer hold before fade-out
- Crossfade transition is slightly longer (1.2s instead of 1.0s) for impact

### 3a. TTS-Aware Segment Timing (when tts_enabled)

When narration is enabled, segment durations should account for the actual
narration audio duration rather than the script director's initial estimates.

**Timing adjustment rules:**

1. For each segment, check the narration asset's `duration_seconds`
2. If narration duration differs from planned segment duration by >15%:
   - **Narration longer**: Extend segment duration to fit narration + 1s padding
   - **Narration shorter**: Keep planned segment duration (extra space is breathing room)
3. Recalculate `start_seconds` / `end_seconds` for all subsequent segments
4. Update `total_duration_seconds` in the timeline
5. Music duration must cover the new total (if loop was already true, this is automatic)

**Example:**
```
Planned:  seg_01: 0-5s,  seg_02: 5-10s, seg_03: 10-15s
Narration: seg_01: 4.2s, seg_02: 6.8s,  seg_03: 3.5s

Adjusted: seg_01: 0-5.2s, seg_02: 5.2-12.0s, seg_03: 12.0-15s
(seg_02 extended to fit 6.8s narration + 0.5s padding)
```

### 4. Transitions

All transition timings come from the pipeline manifest's `transition_defaults` section.
If the user or project overrides these in `edit_decisions.metadata`, use the override values.

**Between segments (video crossfade):**
- Cross-dissolve: `transition_defaults.video.crossfade_duration_seconds` (1.0s)
- Peak segment: `transition_defaults.video.crossfade_peak_duration_seconds` (1.2s)
- Breathing pause: `transition_defaults.video.breathing_pause_seconds` (0.4s, image only, no text)

**Text fade independence (CRITICAL):**
Text subtitles fade IN and OUT on their own schedule, completely independent of the
video crossfade between clips. This ensures clean readability — text never overlaps
during a video blend.

- Outgoing subtitle: fades out BEFORE the video crossfade begins
  (subtitle fade-out completes at least 0.3s before the video blend starts)
- Incoming subtitle: fades in AFTER the video crossfade completes
  (subtitle fade-in starts at least 0.3s after the video blend ends)
- Text fade timings from `transition_defaults.text`:
  - fade_in: 0.7s
  - fade_out: 0.5s

This means the viewer always sees either:
1. Pure video blend (no text) — during the crossfade overlap window, OR
2. Clean text on a stable frame — before the blend starts or after it ends

**Video-to-video transition:**
- Crossfade overlap: the two clips blend during the transition
- Both clips play during the overlap (1.0s crossfade)

**Video-to-image transition:**
- Video fades out as image fades in
- Image begins Ken Burns motion only after transition completes

### 5. Dual Aspect Ratio

**16:9 (横屏):**
- Video clips: play at native 16:9
- Images: full frame with slight letterbox if desired
- Subtitle: lower third, centered
- Ken Burns: horizontal pan preferred

**9:16 (竖屏):**
- Video clips: center-crop from 16:9 source (or regenerate at 9:16 if budget allows)
- Images: center-crop, focus on the most visually dense area
- Subtitle: slightly higher (lower quarter), 80px bottom padding for platform UI
- Ken Burns: vertical pan preferred

**Option for better 9:16:** If the video-priority segment is critical for mobile,
consider generating a separate 9:16 version via Seedance:

```python
seedance_volcengine.execute({
    "prompt": "<same prompt>",
    "aspect_ratio": "9:16",
    ...
})
```

This avoids ugly center-crops of the peak moment. Ask the user if they want this
(extra cost: ~1 additional video generation for the peak segment).

### 6. Color Grade

Apply consistent warm grade across ALL assets (video and image):

- Warmth: +200K color temperature
- Contrast: +5-8%
- Vignette: 3-5% edge darkening
- Film grain: 3-5% opacity overlay
- All segments share identical grade parameters

**For illustration styles**: Film grain should be lighter or omitted (2% or none).
The illustration aesthetic has its own texture from the hand-drawn style.
For `literary-illustration`, skip film grain entirely — the paper texture is the grain.

Use `color_grade` tool if available, or Remotion CSS filters.

### 6.5. Background Music Integration

Read the music asset from the asset_manifest (type: "music", id: "music_bg").
If no music asset exists, skip this section (graceful degradation to silent).

**Via Remotion `<Audio>` component (preferred):**
The music is passed as a composition prop, not mixed externally. Remotion handles
volume curves and fade in/out natively:

```python
video_compose.execute({
    ...
    "audio": {
        "music": {
            "src": "<music_asset_path from asset_manifest>",
            "volume": 0.12,
            "fadeInSeconds": 2,
            "fadeOutSeconds": 3,
            "loop": True   # if music shorter than video
        }
    }
})
```

**Volume guidance by style** (from `transition_defaults.music.volume_by_playbook`):
| Selected Playbook | Volume | Fade In | Fade Out |
|-------------------|--------|---------|----------|
| `warm-illustration` | 0.12 | 2s | 3s |
| `literary-illustration` | 0.10 | 2.5s | 3s |
| `cinematic-drama` | 0.12 | 2s | 3s |

**Fallback via audio_mixer (if Remotion audio fails):**
```python
audio_mixer.execute({
    "operation": "segmented_music",
    "video_path": "renders/final_silent.mp4",
    "music_path": "<music_asset_path>",
    "music_volume": 0.12,
    "segments": [{"start": 0, "end": <video_duration>}],
    "fade_duration": 0.5,
    "output_path": "renders/final_with_music.mp4"
})
```

**Music must NOT be applied to source video clips** — only to the final composed video.

### 6.6. Narration + Music Mixing (when tts_enabled)

When `tts_enabled == true`, narration and music must be mixed with ducking.

**Read narration assets from the asset_manifest** (type: "audio", subtype: "narration").
Build the narration timeline from segment start_seconds and narration durations.

**Step 1: Pre-mix via audio_mixer.full_mix (MANDATORY for both Remotion and FFmpeg paths)**

The current Remotion Explainer component does NOT implement sidechain ducking
in its `<Audio>` layers — it plays narration and music at independent static
volumes. Therefore, narration + music must be pre-mixed externally:

```python
from tools.tool_registry import registry
registry.discover()
mixer = registry.get('audio_mixer')

# Build tracks list: one narration per segment + one music track
tracks = []
for section in script.sections:
    narration_asset = next(
        a for a in asset_manifest.assets
        if a.get("subtype") == "narration" and a.get("scene_id") == section.id
    )
    tracks.append({
        "path": narration_asset["path"],
        "role": "speech",
        "start_seconds": section.start_seconds,
    })

music_asset = next(a for a in asset_manifest.assets if a.get("type") == "music")
tracks.append({
    "path": music_asset["path"],
    "role": "music",
    "volume": 0.12,     # base music volume (between speech segments)
})

result = mixer.execute({
    "operation": "full_mix",
    "tracks": tracks,
    "ducking": {
        "enabled": True,
        "music_volume_during_speech": 0.08,   # from transition_defaults.music.ducking
        "attack_ms": 200,
        "release_ms": 500
    },
    "normalize": True,
    "output_path": "projects/<proj>/assets/audio/mixed_narration_music.wav"
})
```

**Step 2a: Remotion path — use pre-mixed audio as the sole music source**

```python
video_compose.execute({
    ...
    "audio": {
        "music": {
            "src": "projects/<proj>/assets/audio/mixed_narration_music.wav",
            "volume": 1.0,              # already mixed at correct levels
            "fadeInSeconds": 2,
            "fadeOutSeconds": 3,
            "loop": False               # pre-mixed, correct duration
        }
        # NOTE: NO narration prop — narration is already mixed into the music track
    }
})
```

**Step 2b: FFmpeg path — mux pre-mixed audio into the final video**

```bash
ffmpeg -i final_subtitled.mp4 -i mixed_narration_music.wav \
  -c:v copy -c:a aac -b:a 192k -shortest \
  final_16x9.mp4
```

**Ducking parameters reference (from transition_defaults.music.ducking):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| `music_volume_during_speech` | 0.08 | Audible but subdued during narration |
| `music_volume_between_speech` | 0.12 | Recovery level (set via track volume) |
| `attack_ms` | 200 | Fast duck on speech onset |
| `release_ms` | 500 | Gradual recovery after speech ends |

### 7b. FFmpeg Composition (stock-footage mode)

When `render_runtime: "ffmpeg"` is selected (stock-footage only, all video clips):

**Video assembly with crossfade transitions:**

```bash
# Build concat with fade-in/out at clip boundaries
ffmpeg -i seg_01.mp4 -i seg_02.mp4 -i seg_03.mp4 ... \
  -filter_complex "
    [0:v]trim=duration=6,setpts=PTS-STARTPTS[v0];
    [1:v]trim=duration=5,setpts=PTS-STARTPTS,fade=in:st=0:d=1,fade=out:st=4:d=1[v1];
    [2:v]trim=duration=5,setpts=PTS-STARTPTS,fade=in:st=0:d=1,fade=out:st=4:d=1[v2];
    # ... peak segment gets longer fade (1.2s)
    [v0][v1][v2]...concat=n=6:v=1:a=0[outv]
  " -map "[outv]" -r 24 -c:v libx264 -crf 20 final_silent.mp4
```

**Subtitle burn (resolution-adaptive, per playbook style):**

```bash
# 16:9 — horizontal (base font size)
ffmpeg -i final_silent_16x9.mp4 -vf \
  "subtitles=subtitles.srt:force_style='FontName=Noto Serif SC,FontSize=38,PrimaryColour=&HFF3C3833&,OutlineColour=&HFFF5F0EB&,Outline=3,BorderStyle=4,BackColour=&H80000000&,Alignment=2,MarginV=180'" \
  -c:v libx264 -crf 20 final_16x9.mp4

# 9:16 — vertical (scaled font: base × vertical_font_scale)
ffmpeg -i final_silent_9x16.mp4 -vf \
  "subtitles=subtitles.srt:force_style='FontName=Noto Serif SC,FontSize=61,PrimaryColour=&HFF3C3833&,OutlineColour=&HFFF5F0EB&,Outline=3,BorderStyle=4,BackColour=&H80000000&,Alignment=2,MarginV=250'" \
  -c:v libx264 -crf 20 final_9x16.mp4
```

**Music mix (if music asset available):**

```bash
ffmpeg -i final_subtitled.mp4 -i bg_music.mp3 \
  -filter_complex "[1:a]volume=0.12,afade=t=in:d=2,afade=t=out:st=<duration-3>:d=3[bg];[0:a][bg]amix=inputs=2:duration=first[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -shortest final_with_music.mp4
```

### 7. Render

Apply consistent warm grade across ALL assets (video and image):

- Warmth: +200K color temperature
- Contrast: +5-8%
- Vignette: 3-5% edge darkening
- Film grain: 3-5% opacity overlay
- All segments share identical grade parameters

Use `color_grade` tool if available, or Remotion CSS filters.

### 7. Render

```python
video_compose.execute({
    "composition_type": "healing-text-illustration",  # or healing-text-cinematic based on playbook
    "render_runtime": "remotion",
    "script_artifact": <script>,
    "asset_manifest": <asset_manifest>,
    "font_family": <selected_font>,
    "outputs": [
        {"aspect_ratio": "16:9", "resolution": "1920x1080", "fps": 24},
        {"aspect_ratio": "9:16", "resolution": "1080x1920", "fps": 24}
    ],
    "color_grade": {"warmth": 200, "contrast": 1.06, "vignette": 0.04, "film_grain": 0.03},
    "ken_burns": {"scale_start": 1.02, "scale_end": 1.08, "easing": "spring", "image_only": true},
    "transitions": {"type": "crossfade", "duration_seconds": 1.0, "breathing_pause": 0.4},  # from transition_defaults.video
    "peak_segment": {
        "segment_id": "seg_03",
        "subtitle_delay_seconds": 0.5,
        "font_scale": 1.1,
        "transition_duration_seconds": 1.2
    },
    "subtitle": {
        "font_family": <selected_font>,
        "color": "#FFFFFF",        # or playbook text color for illustration styles
        "shadow": "0 2px 8px rgba(0,0,0,0.6)",
        "position": "top-center",  # CHANGED from "lower-third"
        "fade_in_seconds": 0.7,   # from transition_defaults.text
        "fade_out_seconds": 0.5    # from transition_defaults.text
    },
    "audio": {
        "music": {
            "src": <mixed_audio_path if tts_enabled else music_asset_path>,
            "volume": 1.0 if tts_enabled else 0.12,
            "fadeInSeconds": 2,
            "fadeOutSeconds": 3,
            "loop": True if not tts_enabled else False
        }
    }
})
```

### 8. Validate Output

```bash
# Check both outputs exist and have correct properties
for f in projects/<project>/renders/final_16x9.mp4 projects/<project>/renders/final_9x16.mp4; do
  echo "=== $f ==="
  ffprobe -v error -show_entries stream=codec_type,width,height,duration,r_frame_rate "$f"
  # Verify: music audio stream present
  audio_count=$(ffprobe -v error -show_entries stream=codec_type "$f" | grep -c audio || true)
  echo "Audio streams: $audio_count (should be 1 — background music)"
done
```

Confirm:
- Both files exist and play correctly
- 16:9 is 1920×1080, 9:16 is 1080×1920
- 24 fps
- Music audio track present (AAC codec)
- Duration matches script within ±3%
- Text overlay at top-center, crisp and readable on both formats

## Render Report

```json
{
  "version": "1.0",
  "outputs": [
    {"path": "renders/final_16x9.mp4", "format": "mp4", "codec": "h264",
     "resolution": "1920x1080", "fps": 24, "duration_seconds": 25.0,
     "platform_target": "bilibili_youtube"},
    {"path": "renders/final_9x16.mp4", "format": "mp4", "codec": "h264",
     "resolution": "1080x1920", "fps": 24, "duration_seconds": 25.0,
     "platform_target": "douyin_kuaishou_xiaohongshu_shipinhao"}
  ],
  "render_time_seconds": 18.5,
  "render_grammar": "cinematic-trailer",
  "metadata": {
    "pipeline": "healing-text",
    "pipeline_version": "3.0",
    "font_used": "Noto Serif SC",
    "composition_type": "healing-text-illustration",
    "render_runtime": "remotion",
    "tts_enabled": <true | false>,
    "narration_provider": "<doubao | elevenlabs>",
    "narration_voice_id": "<voice_id>",
    "audio": "<pre-mixed-narration-music | background-music>",
    "audio_mixing": "<pre-mixed-narration-music | music-only>",
    "music_source": "pixabay_music",
    "music_volume": 0.12,
    "selected_playbook": "warm-illustration",
    "asset_mode": "<ai-generated | stock-footage>",
    "asset_source": "<seedance_ai | pexels_stock_video>",
    "video_clips_included": 1,
    "stock_clips": 0,
    "all_stock_video": false,
    "music_absent": false,
    "color_graded": false,
    "asset_types": ["video", "video", "video", "image", "image"]
  }
}
```

## Quality Gate

- Both 16:9 and 9:16 outputs exist and are valid
- Music audio track present at approximately 0.12 volume (if music was sourced)
- Text overlay positioned at TOP-CENTER (not lower-third)
- Duration matches script within tolerance
- Subtitle text matches script segments word-for-word
- Video clips play natively, still images have gentle Ken Burns
- Peak segment has special subtitle treatment
- Transitions are smooth — no jarring cuts
- Color grade is warm and consistent across ALL asset types
- 24fps cinematic frame rate
- **stock-footage**: No Ken Burns on any clip (all are video, play natively)
- **stock-footage**: Color grade is pre-applied — verify consistency, no re-grading
- **stock-footage**: Music absence is NOT a failure (music_absent flag in render_report)

## Common Pitfalls

- Applying Ken Burns to already-moving video clips → double motion, looks bad
- Peak segment blending in with the rest → lost emotional impact
- 9:16 center-crop cutting off key visual elements → check crops manually
- Video clips with different durations causing timeline gaps → pad or trim
- Crossfading video clips at the wrong moment (mid-motion → jarring)
- Text overlay at lower-third instead of top-center → wrong position for social media style
- Music volume too high (distracting) → should be background texture, not foreground
- Using `cinematic-drama` renderer for illustration styles → wrong visual treatment
- **stock-footage**: Applying Ken Burns to stock video clips → double motion
- **stock-footage**: Re-applying color grade in compose → double grading, over-processed
- **stock-footage**: Treating missing music as pipeline failure → silent video is valid output
- **stock-footage**: Using Remotion-only mindset when FFmpeg would produce identical results (all-video clips)
