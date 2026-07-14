# Publish Director — Book Recommend Pipeline

## When To Use

The video is rendered and approved. Both 16:9 and 9:16 exports exist.
Your job: package everything for distribution, generate thumbnails,
write metadata, and record the publishing log.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/publish_log.schema.json` | Artifact validation |
| Prior artifact | `render_report` | Output paths, durations, metadata |
| Prior artifact | `final_review` | Quality sign-off |
| Optional | `script` | Book metadata for thumbnail and SEO |

## Process

### 1. Verify Exports

Confirm both files exist and are playable:

```bash
ls -la projects/<proj>/renders/final_16x9.mp4
ls -la projects/<proj>/renders/final_9x16.mp4

ffprobe -v error -show_entries format=duration,size \
  projects/<proj>/renders/final_16x9.mp4
ffprobe -v error -show_entries format=duration,size \
  projects/<proj>/renders/final_9x16.mp4
```

### 2. Generate Thumbnail Concept

For each aspect ratio, describe a thumbnail concept. The thumbnail should:
- Feature the primary book cover prominently
- Include a text hook (the video title or best quote)
- Be visually striking at small sizes (mobile feed)
- Match the video's visual style

If tools are available, generate thumbnail images. If not, write a detailed
description the user can use with external tools.

### 3. Write Platform Metadata

For each target platform, prepare:

**Douyin / TikTok:**
- Title (max 55 chars, hook-driven)
- Hashtags (5-8 relevant tags)
- Cover image recommendation

**Xiaohongshu (小红书):**
- Title (max 20 chars)
- Description (max 1000 chars, keyword-rich)
- Hashtags (5-10 relevant tags)

### 4. Write Publish Log

```json
{
  "version": "1.0",
  "published_at": "<ISO timestamp>",
  "exports": [
    {
      "aspect_ratio": "16:9",
      "file": "renders/final_16x9.mp4",
      "duration_seconds": 75.0,
      "platforms": ["douyin", "xiaohongshu"]
    },
    {
      "aspect_ratio": "9:16",
      "file": "renders/final_9x16.mp4",
      "duration_seconds": 75.0,
      "platforms": ["douyin", "xiaohongshu"]
    }
  ],
  "thumbnail_concept": {
    "16:9": "Book cover centered with title overlay, warm library background",
    "9:16": "Book cover top-third with title text, visual frame behind"
  },
  "platform_metadata": {
    "douyin": {
      "title": "3本书改变了我对时间的理解",
      "hashtags": ["#读书推荐", "#好书分享", "#认知升级", "#阅读", "#自我提升"]
    },
    "xiaohongshu": {
      "title": "改变时间观的3本书",
      "description": "这三本书彻底改变了我对时间的理解...",
      "hashtags": ["#读书笔记", "#好书推荐", "#认知提升", "#阅读分享", "#自我成长"]
    }
  },
  "metadata": {
    "pipeline": "book-recommend",
    "pipeline_version": "1.0",
    "format_mode": "book-list",
    "asset_mode": "ai-generated",
    "music_enabled": false,
    "tts_enabled": false,
    "books": [
      {"title": "原子习惯", "author": "James Clear"},
      {"title": "深度工作", "author": "Cal Newport"},
      {"title": "思考快与慢", "author": "Daniel Kahneman"}
    ],
    "render_runtime": "remotion"
  }
}
```

### 5. Present Summary to User

Summarize for the user:
1. **Export paths** — where both files are
2. **Durations** — how long each is
3. **Thumbnail concept** — what the cover image should look like
4. **Platform-ready metadata** — copy-paste titles and hashtags
5. **Distribution checklist** — which platforms this is ready for

## Quality Gate

- Both AR exports exist and are playable
- File naming includes AR suffix (e.g., _16x9, _9x16)
- Thumbnail concept captures book cover + title hook
- Platform metadata complete with hashtags
- format_mode, asset_mode, music_enabled, tts_enabled recorded in publish log
- Book list recorded in publish log metadata
- render_runtime recorded

## Common Pitfalls

- Same file name for both AR variants → overwrite risk, use _16x9 and _9x16 suffixes
- Missing platform metadata → users need copy-paste ready captions
- Generic thumbnail concept → thumbnail should feature the book cover
- Forgetting to record mode choices → downstream analytics need these
