# Compose Director — Book Recommend Pipeline

## When To Use

The script and asset_manifest are approved. All book covers, visual assets,
and optional music/TTS narration are on disk. Your job: compose everything
into a polished video with format-mode-appropriate layout, exporting in both
16:9 and 9:16 aspect ratios.

## ⚠️ CRITICAL: Format Mode Determines Layout

The layout strategy is FUNDAMENTALLY different between `single-book` and
`book-list` modes. Using the wrong layout ruins the video.

### Single-Book Mode (Deep Dive)

**The book cover appears ONLY in the intro (first ~8s).** After the intro,
the visual is FULL-SCREEN with subtitles only. The cover is NOT pasted on
every frame — that would be visually oppressive and redundant since only
one book is being discussed.

```
INTRO (first ~8s):
┌──────────────────────────────────────────┐
│  ┌────────┐                              │
│  │  BOOK  │   今日好书                   │
│  │  COVER │   《小王子》                  │
│  │        │   安托万·德·圣-埃克苏佩里      │
│  └────────┘                              │
└──────────────────────────────────────────┘

BODY (rest of video):
┌──────────────────────────────────────────┐
│                                          │
│          FULL-SCREEN VISUAL              │
│          (video clip)                    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │  字幕文本 (SRT, bottom overlay)    │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

### Book-List Mode (Multiple Books)

The book cover IS present in every segment as the visual anchor — the viewer
needs to know which book each segment is discussing. This is the original
cover-layout system from the pipeline manifest `transition_defaults.cover_layout`.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/render_report.schema.json` | Artifact validation |
| Schema | `schemas/artifacts/final_review.schema.json` | Review artifact |
| Prior artifacts | `script`, `asset_manifest` | Segments, timings, asset paths |
| Tools | `video_compose`, `subtitle_gen`, `audio_mixer` | Composition, subtitles, audio |
| Agent Skills | `.agents/skills/remotion/SKILL.md` | Remotion patterns (if using Remotion) |

## 1. Confirm Configuration

Before composing, read and confirm:

```
From script.metadata:
  - format_mode: single-book | book-list | themed-list  ← DETERMINES LAYOUT
  - music_enabled: true | false
  - tts_enabled: true | false
  - selected_font: <font family + weight>

From asset_manifest:
  - asset_mode: ai-generated | stock-footage
  - Book cover paths per book
  - Visual asset paths per segment
  - Music path (if enabled)
  - Narration paths (if tts_enabled)
```

## 2. Subtitle Approach (ALL MODES — MANDATORY)

**Never use ffmpeg `drawtext` filter with inline Chinese text.** The
`drawtext` filter has well-known issues with:
- Multi-byte UTF-8 characters and escape sequences interacting badly
- `\n` newlines not rendering correctly across ffmpeg versions
- Font fallback when the primary font lacks certain glyphs

**Correct approach: Use the `subtitle_gen` tool to create SRT files,
then burn them in via ffmpeg's `subtitles` filter or `video_compose`
`burn_subtitles` operation.**

```python
subtitle_gen = registry.get('subtitle_gen')
result = subtitle_gen.execute({
    "script_path": "projects/<proj>/artifacts/script.json",
    "narration_dir": "projects/<proj>/assets/narration/",
    "font_family": "Noto Serif SC",
    "output_path": "projects/<proj>/assets/subtitles.srt",
})
# Then burn into video:
video_compose.execute({
    "operation": "burn_subtitles",
    "input_path": "<composed_video>",
    "subtitle_path": "projects/<proj>/assets/subtitles.srt",
    "subtitle_style": {"font": "Noto Serif SC", "font_size": 32},
    "output_path": "projects/<proj>/renders/final_16x9.mp4",
})
```

**If `subtitle_gen` is unavailable**, use ffmpeg with an SRT file (never inline text):

```bash
# 1. Write SRT file (proper UTF-8 file, not inline text)
# 2. Burn via subtitles filter:
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:force_style='FontName=PingFang SC,FontSize=32'" output.mp4
```

## 3. Single-Book Layout Workflow

### 3.1 Determine Intro Duration

The intro should be the FIRST segment's narration duration plus 2 seconds.
Minimum 6s, maximum 12s.

```
intro_duration = min(max(seg_01_narration_duration + 2, 6), 12)
```

### 3.2 Build Intro Composition (via Remotion BookRecommendIntro)

The intro is rendered by the `BookRecommendIntro` Remotion component. It has
three phases:

- **Phase 1 (~1.5s):** Hook text "今天分享的是" fades in over a static image
  (first carousel image), then fades out.
- **Phase 2 (~2.8s):** Rapid image carousel — 15-20 searched stock images
  switch every 0.15-0.20s (see `intro_layout.carousel.switch_interval_seconds`).
  The book title "《小王子》" rotates/spins as an overlay.
- **Phase 3 (~2.0s):** Book cover scales in from center, title settles at top,
  author name fades in below.

**CRITICAL: The carousel images come from `assets/images/intro_carousel/`**
— they are searched via `pixabay_image` / `pexels_image` using book-theme
keywords. NEVER use frames extracted from body video clips. See asset-director
Section I.

**The switch speed is configurable.** Pass `switchInterval` to the Remotion
component. A value of 0.15-0.18s gives the rapid-cut effect seen in the
healing-text reference videos.

**Props passed to BookRecommendIntro:**
```python
{
    "images": ["project-assets/intro_001.jpg", ...],  # 15-20 carousel images
    "coverImage": "project-assets/book_cover.png",
    "hookText": "今天分享的是",
    "title": "《书名》",
    "author": "作者名",
    "phase1Duration": 1.5,
    "phase2Duration": 2.8,
    "phase3Duration": 2.0,
    "switchInterval": 0.18,  # from intro_layout.carousel.switch_interval_seconds
}

### 3.3 Build Body (Full-Screen Visual)

After the intro, all remaining segments play as full-screen visuals with
SRT subtitles burned at the bottom. The video clips play consecutively
with crossfade transitions.

### 3.4 Audio Mix

- Narration tracks aligned to segment start times
- Background music at 0.10 volume (0.08 during narration)
- 2s music fade-in, 3s music fade-out

## 4. Book-List Layout Workflow (Multiple Books)

For `book-list` and `themed-list` modes, use the cover-per-segment layout
from `pipeline_defs/book-recommend.yaml` `transition_defaults.cover_layout`:

- **16:9**: Cover left 30%, visual right 70%
- **9:16**: Cover top 35%, visual bottom 65%

Each segment's cover is the book being discussed in that segment. When the
same book spans multiple segments, keep the cover visible (don't animate it
away and back).

## 5. Font Sizing (For Subtitles)

Font size is auto-calculated using the formula from `pipeline_defs/book-recommend.yaml`
`transition_defaults.text_overlay.font_size_formula`.

## 6. Motion Rules

### Still Images
- Gentle Ken Burns: scale 1.0 → 1.08x over duration

### Video Clips
- Play natively, no additional motion
- Trim or loop to match segment duration

### Transitions Between Segments
- Video→Video: crossfade 1.0s
- Breathing pause: 0.3s

## 7. Audio

### Music + TTS (both enabled)
- Music volume: 0.10 between segments
- Music ducks to 0.08 during narration (attack 200ms, release 500ms)
- Narration at full volume
- 2s fade-in, 3s fade-out

### TTS Only
- Narration aligned to segment timing
- No background music

## 8. Render

Use `video_compose` with `operation: "render"` and `render_runtime: "remotion"`
when Remotion is available. For single-book mode, the Remotion composition
should handle the intro→body transition cleanly.

**FFmpeg fallback** (when Remotion composition is unavailable):
- Build intro segment: cover + text overlay via `overlay` filter
- Build body: concat video clips with crossfade via `xfade` filter
- Burn SRT subtitles via `subtitles` filter
- Mix audio: narration tracks + music

## 9. Quality Check

### Layout
- [ ] Single-book: cover ONLY in intro, NOT on every frame
- [ ] Book-list: cover in correct zone for every segment
- [ ] Visual asset fills screen (single-book) or its zone (book-list)
- [ ] Subtitles readable, not occluded
- [ ] Font family matches approved selection
- [ ] 16:9 and 9:16 layouts both correct

### Motion
- [ ] Still images have gentle Ken Burns
- [ ] Video clips play natively
- [ ] Transitions smooth

### Audio
- [ ] Narration synced to segment timing
- [ ] Music mixed correctly with ducking
- [ ] No audio clipping

### Export
- [ ] Both 16:9 and 9:16 files exist and pass ffprobe
- [ ] Duration within ±5% of planned total

## 10. Write Render Report

The render report must include both outputs with format-specific metadata.

## Root Cause: Common Pitfalls (READ BEFORE COMPOSING)

| # | Pitfall | Why It Happens | Prevention |
|---|---------|---------------|------------|
| 1 | **Cover on every frame in single-book mode** | Compose-director applies book-list layout universally | Check `format_mode` FIRST; single-book → intro-only cover |
| 2 | **Chinese text garbled (乱码)** | `drawtext` filter with inline Chinese + `\n` + escape chars breaks UTF-8 | Use SRT subtitles via `subtitle_gen` or ffmpeg `subtitles` filter; NEVER use `drawtext` with inline Chinese text |
| 3 | **Stiff per-segment composition** | Building each segment as independent video then concatenating creates jarring cuts | Single-book: build continuous visual montage, then overlay narration + subtitles |
| 4 | **Font doesn't render Chinese** | Font file doesn't contain CJK glyphs | Verify font supports Chinese before composing; PingFang SC, Noto Serif SC, Source Han Serif are safe |
| 5 | **Remotion composition missing** | BookRecommend scene type not registered in remotion-composer | Check `remotion-composer/src/Root.tsx` for available compositions before locking `render_runtime: "remotion"` |
