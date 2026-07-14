# Publish Director — Healing Text Pipeline

## When To Use

The video is rendered in both aspect ratios with background music (and optional
TTS narration). Package them for distribution with clear labeling, thumbnail
concepts featuring the peak video moment, and platform-ready metadata.

Video with background music. Music sourced from Pixabay (royalty-free).
When `tts_enabled`, narration is pre-mixed with music using sidechain ducking.
Social-media-first distribution targeting Xiaohongshu and similar platforms.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/publish_log.schema.json` | Artifact validation |
| Prior artifacts | `state.artifacts["compose"]["render_report"]`, `state.artifacts["script"]["script"]` | Output paths + content |
| Output files | `renders/final_16x9.mp4`, `renders/final_9x16.mp4` | The actual videos |

## Process

### 1. Organize Export Directory

```
projects/<project>/renders/
├── final_16x9.mp4          # Hero export (横屏, B站/YouTube)
├── final_9x16.mp4          # Social cutdown (竖屏, 抖音/快手/小红书/视频号)
└── thumbnails/
    ├── poster_16x9.png     # 横屏封面 — from peak video frame
    └── poster_9x16.png     # 竖屏封面 — from peak video frame (cropped)
```

### 2. Generate Thumbnails from Peak Moment

Extract the best frame from the peak video segment:

```bash
# Extract a frame at 1.5s into the peak video clip (usually a strong composition)
ffmpeg -i assets/video/seg_03.mp4 -ss 00:00:01.5 -vframes 1 thumbnails/poster_16x9.png

# Crop for 9:16
ffmpeg -i thumbnails/poster_16x9.png -vf "crop=ih*9/16:ih" thumbnails/poster_9x16.png
```

Or use the first visually striking frame from the rendered video. Overlay the
video title in the selected font for a clean poster.

### 3. Platform-Specific Notes

| Platform | File | Format | Tips |
|----------|------|--------|------|
| 抖音 | `final_9x16.mp4` | 竖屏 | 晚间 7-10 点发布治愈内容互动率最高 |
| 快手 | `final_9x16.mp4` | 竖屏 | 封面从高潮帧截取，吸引滑动停留 |
| 小红书 | `final_9x16.mp4` | 竖屏 | 治愈系笔记发布：封面图 + 一段文案 + 话题标签 #治愈 #情感 #晚安 #正能量. 晚间 9-11 点发布最佳 |
| 视频号 | `final_9x16.mp4` | 竖屏 | 微信生态，文艺内容传播好 |
| B站 | `final_16x9.mp4` | 横屏 | 适合合集/系列形式 |
| YouTube | `final_16x9.mp4` | 横屏 | 可加结尾画面留白 |

### 4. Write Publish Log

```json
{
  "version": "1.0",
  "hero_output": "renders/final_16x9.mp4",
  "derivative_outputs": [
    {
      "path": "renders/final_9x16.mp4",
      "purpose": "social-vertical",
      "platforms": ["douyin", "kuaishou", "xiaohongshu", "shipinhao"]
    }
  ],
  "poster_frames": [
    {"path": "thumbnails/poster_16x9.png", "aspect_ratio": "16:9", "source": "peak_video_frame"},
    {"path": "thumbnails/poster_9x16.png", "aspect_ratio": "9:16", "source": "peak_video_frame_cropped"}
  ],
  "metadata": {
    "pipeline": "healing-text",
    "pipeline_version": "3.0",
    "title": "<from script.title>",
    "duration_seconds": 25.0,
    "font_used": "<from script.metadata.selected_font>",
    "text_source": "user-provided",
    "tts_enabled": <true | false>,
    "narration_provider": "<doubao | elevenlabs>",
    "narration_voice_id": "<voice_id>",
    "audio": "<narration-plus-music | background-music>",
    "audio_source": "pixabay_music",
    "selected_playbook": "<from script.metadata.selected_playbook>",
    "asset_mode": "<from script.metadata.asset_mode>",
    "asset_source": "<stock | ai-generated>",
    "asset_strategy": "3-tier-motion-priority | stock_video_only",
    "video_clips_count": 1,
    "stock_sources": ["pexels", "pixabay_video"],
    "no_ai_generation": false,
    "distribution_notes": "Social-media-first healing video with background music and top-center text overlay. Best posted during evening hours (9-11pm for Xiaohongshu). Use hashtags: #治愈 #情感 #晚安 #正能量.",
    "distribution_notes_narration": "治愈系视频，含TTS语音朗读+背景音乐（自动ducking）。字幕保留，可静音观看。晚间9-11点发布最佳。Use hashtags: #治愈 #情感 #晚安 #正能量.",
    "distribution_notes_stock_footage": "纯实拍素材，无AI生成。所有视频来自 Pexels/Pixabay 免费素材库，Pexels License / Pixabay Content License，无需署名。小红书可标注'实拍素材'区别于AI生成内容，晚间9-11点发布最佳。"
  }
}
```

### 5. Final Checklist

Present to the user:

- [ ] Both video files exist and are playable
- [ ] Background music present and at correct volume on both outputs
- [ ] Peak moment (video tier segment) has visible cinematic motion
- [ ] Thumbnails capture the most beautiful frame
- [ ] File names are clear and self-documenting
- [ ] Both aspect ratios confirmed visually correct (check 9:16 crop)
- [ ] Subtitles are legible on both versions at feed-preview size
- [ ] Ready to post immediately — no manual cleanup needed
- [ ] `asset_mode` and `asset_source` are correctly recorded in publish metadata
- [ ] tts_enabled: Narration is clear and synchronized with text display
- [ ] tts_enabled: Music ducking is smooth (no abrupt volume changes)
- [ ] Stock footage mode: distribution notes include license info and source attribution
- [ ] Stock footage mode: no AI generation attribution needed (mark `no_ai_generation: true`)

## Quality Gate

- Hero and derivative exports are clearly labeled by platform intent
- File naming is self-documenting (`_16x9`, `_9x16`)
- Poster frames come from the peak video moment (not a random frame)
- Distribution notes are practical and actionable
- The renders directory is a drop-in for any platform
- `asset_mode` is recorded in publish log metadata
- Stock footage source attribution included where applicable

## Common Pitfalls

- Confusing the two files — label clearly with aspect ratio suffix
- Thumbnail from a still segment instead of the video peak — missed impact
- Forgetting that 9:16 platforms crop differently (safe zone: center 80%)
- Not mentioning the video is silent — platforms sometimes add default audio
- Stock footage mode: forgetting to record stock sources in publish metadata
- Stock footage mode: using AI generation attribution language for stock content
