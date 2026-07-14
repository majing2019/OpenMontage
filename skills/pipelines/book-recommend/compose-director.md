# Compose Director — Book Recommend Pipeline

## When To Use

The script and asset_manifest are approved. All book covers, visual assets,
and optional music/TTS narration are on disk. Your job: compose everything
via Remotion into a polished video with the book cover layout system,
exporting in both 16:9 and 9:16 aspect ratios.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/render_report.schema.json` | Artifact validation |
| Schema | `schemas/artifacts/final_review.schema.json` | Review artifact |
| Prior artifacts | `script`, `asset_manifest` | Segments, timings, asset paths |
| Tools | `video_compose`, `audio_mixer` | Composition and audio mixing |
| Agent Skills | `.agents/skills/remotion/SKILL.md`, `.agents/skills/remotion-best-practices/SKILL.md` | Remotion patterns, quality, performance |

## 1. Confirm Configuration

Before composing, read and confirm:

```
From script.metadata:
  - format_mode: single-book | book-list | themed-list
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

## 2. Cover Layout System

The book cover is ALWAYS present in every segment. Layout adapts by aspect ratio.

### 16:9 Layout

```
┌──────────┬───────────────────────────────┐
│          │                               │
│  BOOK    │     VISUAL / VIDEO            │
│  COVER   │     (image or video clip)     │
│  30%     │     70%                       │
│          │                               │
│          │  ┌──────────────────────┐     │
│          │  │  Text overlay zone   │     │
│          │  │  (auto-sized font)   │     │
│          │  └──────────────────────┘     │
└──────────┴───────────────────────────────┘
```

- Cover zone: left 30% of frame width, vertically centered
- Visual zone: right 70% of frame width
- Text overlay: within the visual zone, positioned for readability

### 9:16 Layout

```
┌───────────────────┐
│                   │
│   BOOK COVER      │
│   top 35%         │
│                   │
├───────────────────┤
│                   │
│   VISUAL / VIDEO  │
│   bottom 65%      │
│                   │
│  ┌─────────────┐  │
│  │ Text overlay │  │
│  │ (auto-sized) │  │
│  └─────────────┘  │
│                   │
└───────────────────┘
```

- Cover zone: top 35% of frame height, horizontally centered
- Visual zone: bottom 65% of frame height
- Text overlay: within the visual zone, positioned for readability

## 3. Font Sizing

Font size is AUTO-CALCULATED using the formula from `pipeline_defs/book-recommend.yaml`
`transition_defaults.text_overlay.font_size_formula`:

```
font_size = clamp(
    video_width × target_fill_ratio / longest_chars,
    min_font,
    max_font
)
```

| Parameter | 16:9 | 9:16 |
|-----------|------|------|
| target_fill_ratio | 0.30 | 0.65 |
| min_font | 28 | 40 |
| max_font | 44 | 60 |

Use the SAME font size across all segments within each aspect ratio.

## 4. Text Color

Auto-adaptive based on background luma analysis:
- Analyze average luma of the visual zone (concatenated video)
- Light background (luma > 128) → dark text (`#1A1A1A`)
- Dark background (luma ≤ 128) → light text (`#F5F5F5`)
- ONE color for the entire video (not per-segment)

Apply `line_height_ratio: 1.6` for readability.

## 5. Motion Rules

### Still Images
- Apply gentle Ken Burns effect: scale from 1.0 to 1.08x max over segment duration
- Subtle parallax or drift within the safe area
- Never zoom into text overlay zone

### Video Clips
- Play natively at original speed
- No additional Ken Burns on already-moving footage
- Trim to segment duration if clip is longer

### Book Covers
- Covers are static — no motion on the cover itself
- Cover transitions: fade or slide when switching between books
- When the same book spans multiple segments, keep the cover visible

### Transitions Between Segments
- Video→Video: crossfade (1.0s)
- Video→Image: dissolve (0.8s)
- Image→Image: crossfade (0.8s)
- When the book changes: brief cover swap (fade out old → fade in new, 0.5s)
- Breathing pause between segments: 0.3s

## 6. Audio

### No Music, No TTS (Default)
- Silent video with subtitles only
- Subtitles display the exact text from `script.sections[].text`
- Subtitle timing matches segment start_seconds and end_seconds

### Music Only (`music_enabled == true`)
- Background music mixed at ~0.10 volume
- 2s fade-in at start, 3s fade-out at end
- If music is shorter than video: loop it
- If music is longer than video: trim to video duration + fade-out

### TTS Only (`tts_enabled == true`)
- Narration audio aligned to segment timing
- Narration plays at full volume
- Subtitles remain visible alongside narration (dual-channel)

### Music + TTS
- Music volume: 0.10 between segments
- Music ducks to 0.08 during narration (attack 200ms, release 500ms)
- Narration always at full volume, clear over music
- Subtitles remain visible

## 7. Render via Remotion

```python
video_compose = registry.get('video_compose')
result = video_compose.execute({
    "edit_decisions": {
        "render_runtime": "remotion",
        "cuts": [
            {
                "id": "seg_01",
                "type": "book_recommend_scene",
                "start": 0,
                "duration": 5.0,
                "cover_path": "assets/covers/book_01.png",
                "visual_path": "assets/images/seg_01.png",
                "text": "<segment text>",
                "font_family": "Noto Serif SC",
                # font_size is auto-calculated, not passed in
            },
            # ... one cut per segment
        ],
        "audio": {
            "music_path": "assets/music/bg_music.mp3",    # null if music_enabled=false
            "music_volume": 0.10,
            "narration_paths": {                            # null if tts_enabled=false
                "seg_01": "assets/narration/seg_01.mp3",
            }
        },
        "output": {
            "16:9": "projects/<proj>/renders/final_16x9.mp4",
            "9:16": "projects/<proj>/renders/final_9x16.mp4"
        }
    }
})
```

## 8. Quality Check

### Layout
- [ ] Book cover visible in every segment, correct zone
- [ ] Visual asset fills its zone without stretching
- [ ] Text overlay readable, not occluded by cover or visual elements
- [ ] Font family matches approved selection
- [ ] 16:9 and 9:16 layouts both visually correct

### Motion
- [ ] Still images have gentle Ken Burns (not static, not aggressive)
- [ ] Video clips play natively
- [ ] Transitions are smooth (no jarring cuts)
- [ ] Book cover transitions are clean

### Audio
- [ ] Music present and mixed correctly (if enabled)
- [ ] TTS narration synced to segments (if enabled)
- [ ] Music ducks during narration (if both enabled)
- [ ] Silent output correct (if neither enabled)

### Export
- [ ] Both 16:9 and 9:16 files exist
- [ ] Both pass ffprobe validation
- [ ] Duration within ±5% of planned total
- [ ] File size reasonable for the platform

## 9. Write Render Report

```json
{
  "version": "1.0",
  "outputs": {
    "16:9": {
      "path": "renders/final_16x9.mp4",
      "duration_seconds": 75.0,
      "resolution": "1920x1080",
      "codec": "h264",
      "file_size_mb": 45.2
    },
    "9:16": {
      "path": "renders/final_9x16.mp4",
      "duration_seconds": 75.0,
      "resolution": "1080x1920",
      "codec": "h264",
      "file_size_mb": 42.8
    }
  },
  "metadata": {
    "render_runtime": "remotion",
    "format_mode": "book-list",
    "asset_mode": "ai-generated",
    "music_enabled": false,
    "tts_enabled": false,
    "selected_font": "Noto Serif SC",
    "segment_count": 6,
    "book_count": 3
  }
}
```

## Common Pitfalls

- Book cover getting occluded by text overlay → always place text in visual zone, not cover zone
- Font too small/large → trust the auto-size formula, don't override manually
- Different font sizes per segment → use ONE size for the entire video per AR
- FFmpeg used instead of Remotion → Remotion is REQUIRED for cover+text compositing
- Ken Burns on video clips → video clips play natively, no additional motion
- Cover transitions too fast → book changes need a beat for the viewer to register
- Not verifying 9:16 layout → the vertical layout is different from horizontal, check both
