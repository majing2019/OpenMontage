# Book Recommend Pipeline — Design

Date: 2026-07-14

## Summary

A `book-recommend` pipeline for social media book recommendation videos (Douyin, Xiaohongshu). The user provides narration text + book info; the pipeline handles segmentation, visual planning, book cover retrieval, AI-generated or stock footage, and Remotion composition with dual 16:9 + 9:16 export.

The design references the `healing-text` pipeline for its mode-switching architecture and four-stage structure, with adaptations for book covers as the core visual anchor.

## Modes (4 toggles)

| Mode | Default | Options |
|------|---------|---------|
| `format_mode` | `book-list` | `single-book` / `book-list` / `themed-list` |
| `asset_mode` | `ai-generated` | `ai-generated` (Seedream+Seedance, ~$3) / `stock-footage` (Pexels/Pixabay, free) |
| `music_enabled` | `false` | `true` / `false` |
| `tts_enabled` | `false` | `true` / `false` |

## Stages (all require human approval)

```
script → assets → compose → publish
```

### Stage 1: Script
- **Input:** User's narration text + book info (title, author, etc.)
- **Output:** Segmented script with visual_keywords (CN+EN), mood, motion_priority per segment
- **Agent work:** Text segmentation by natural pauses, visual direction planning

### Stage 2: Assets
- **Input:** Confirmed script
- **Output:** asset_manifest — book covers, visuals (images/video clips), optional music and TTS
- **Agent work:** Cover retrieval via search, image generation or stock clip search, music/tts if enabled

### Stage 3: Compose
- **Input:** Script + asset_manifest
- **Output:** render_report — dual 16:9 + 9:16 video files
- **Agent work:** Remotion composition with cover layout + visual zone + auto-adaptive text overlay, crossfade transitions

### Stage 4: Publish
- **Output:** publish_log with metadata, thumbnails, platform-ready exports

## Cover Layout

| Aspect Ratio | Cover Position | Visual Zone |
|-------------|----------------|-------------|
| 16:9 | Left 30% | Right 70% |
| 9:16 | Top 35% | Bottom 65% |

Text overlay auto-sized via font formula; auto-adaptive color (light/dark based on luma analysis).

## Key Differences from healing-text

1. Book cover is a mandatory visual element in every segment (not present in healing-text)
2. User provides the narration text directly (healing-text generates segmentation from submitted text)
3. `format_mode` controls content structure (single-book vs book-list vs themed-list)
4. Cover layout system replaces healing-text's pure text-overlay approach
5. Music and TTS are off by default (healing-text has music always on)
