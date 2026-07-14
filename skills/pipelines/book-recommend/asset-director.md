# Asset Director — Book Recommend Pipeline

## 0. Asset Mode Routing (READ FIRST)

**Before starting any asset work, read `script.metadata.asset_mode`:**

- If `asset_mode == "ai-generated"` (or not set — default): Continue with the
  AI-generated workflow below (Sections 1-3 + Phase 1-2).
- If `asset_mode == "stock-footage"`: Skip to **Section S: Stock-Footage
  Workflow** at the end of this document.

**Also check `script.metadata.music_enabled` and `script.metadata.tts_enabled`:**

- `music_enabled == true`: Source background music after visual assets (Section 4).
- `tts_enabled == true`: Generate TTS narration after visual assets (Section T).
- Both default to `false` — skip the corresponding sections.

## When To Use

The script is segmented and approved with motion priorities and book metadata.
You need to:
1. Retrieve book covers for every book in the recommendation
2. Generate or source visual assets per segment (images, video clips)
3. Optionally source background music and/or generate TTS narration

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/asset_manifest.schema.json` | Artifact validation |
| Prior artifact | `state.artifacts["script"]["script"]` | Segments + motion priorities + keywords + books |
| Tools | `image_selector`, `video_selector`, `direct_clip_search`, `color_grade` | Generation and stock |
| Layer 3 skills | `.agents/skills/seedream-prompt-patterns/`, `.agents/skills/seedance-2-0/SKILL.md`, `.agents/skills/flux-best-practices/SKILL.md`, `.agents/skills/visual-taste/SKILL.md` | Provider-specific prompt craft |

---

## 1. Book Cover Retrieval (ALL MODES — DO FIRST)

Book covers are the core visual anchor. Retrieve them BEFORE any other asset work.

### 1.1 Compile Cover Search Queries

Read `script.metadata.books[].cover_search_query` for each book.
These were written by the script director. Verify each query is concrete enough
for image search.

### 1.2 Search for Book Covers

For each book, search via web image search or book APIs:

**Option A — Web Image Search:**
Use a web search tool to find high-resolution book cover images. Search for:
- `"{book_title} {author} book cover high resolution"`
- Prefer official publisher covers over user-uploaded photos
- Look for clean, front-facing covers without stickers or damage

**Option B — Book APIs (if available):**
- Google Books API: `https://www.googleapis.com/books/v1/volumes?q={title}+{author}`
- Open Library Covers API: `https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg`

### 1.3 Download and Normalize

```bash
# Download the best cover found
# Normalize: ensure minimum 800px on longest edge
# Save to:
projects/<proj>/assets/covers/book_01.png
projects/<proj>/assets/covers/book_02.png
```

### 1.4 Quality Check Per Cover

- [ ] Image is the correct book and edition
- [ ] Resolution adequate for display (min 800px longest edge)
- [ ] Clean front cover, no stickers, no heavy shadows
- [ ] Saved in `assets/covers/` directory

---

## 2. AI-Generated Workflow (`asset_mode == "ai-generated"`)

Production runs in TWO phases with a mandatory user approval gate between them.

**Phase 1 — Still Images:** Every segment gets a still image via `image_selector`.
The user reviews and approves ALL images before any video generation.

**Phase 2 — Image-to-Video:** Only `video` and `animate` segments proceed to
image_to_video. `still` segments stop at Phase 1.

| Priority | Phase 1 (all segments) | Phase 2 (video/animate only) |
|----------|----------------------|------------------------------|
| `video` | Still image (2560×1440) | image_to_video (5s, 1080p) |
| `animate` | Still image (2560×1440) | image_to_video (4s, 1080p) |
| `still` | Still image (2560×1440) | _(none — still image is final)_ |

### Phase 1: Generate All Still Images

#### Phase 1.1: Write Image Prompts

Read visual_keywords_image from each segment's visual_direction in the script.
Write complete prompts:

- Use Chinese for Seedream-compatible models
- Include scene description, lighting, composition, color palette
- **CRITICAL: Leave negative space for text overlay** — the compose stage will
  overlay text, so the image should not have busy areas where text goes
- Each image should feel like it belongs in the same visual universe
- For book-themed imagery: libraries, reading nooks, nature metaphors, abstract
  concepts visualized as concrete scenes

#### Phase 1.2: Generate via Image Selector

```python
image_selector = registry.get('image_selector')
result = image_selector.execute({
    "prompt": "<Chinese scene description>",
    "size": "2560x1440",
    "output_path": "projects/<proj>/assets/images/seg_XX.png",
})
```

Generate ALL segments — `video`, `animate`, and `still` — as still images first.

#### Phase 1.3: Image Quality Check

- [ ] Resolution is 2560×1440 (or appropriate for 16:9 display)
- [ ] Composition has space for text + book cover overlay
- [ ] Color palette consistent across all images
- [ ] Visual style matches the selected direction
- [ ] No AI artifacts that would distract from the book recommendation

**Remediation:** Bad image → retry with adjusted prompt (max 1 retry).
Failed retry → fall back to pexels_image.

#### Phase 1.4: USER APPROVAL GATE (MANDATORY)

Present ALL generated images to the user. Show:
1. Each image with its segment text, motion priority, and associated book
2. Which segments will receive image_to_video (video + animate)
3. Estimated video generation cost

**Do not proceed to Phase 2 until the user says yes.**

### Phase 2: Image-to-Video (Motion Segments Only)

Only `video` and `animate` segments proceed. `still` segments are done.

#### Phase 2.1: Write Video Prompts

Video prompts describe ONLY the motion, not the scene. The image already
provides the composition.

- Open with shot-structure: "One continuous shot, locked tripod..."
- Camera negation: "no push-in, no dolly, no pan, no tilt, no zoom, no cuts"
- Small, natural motion: light shifting, pages turning, gentle breeze
- Beat-by-beat with ALL CAPS action markers

#### Phase 2.2: Generate Videos

```python
video_selector = registry.get('video_selector')
result = video_selector.execute({
    "prompt": "<motion-only description>",
    "operation": "image_to_video",
    "image_path": "projects/<proj>/assets/images/seg_XX.png",
    "duration": "5",
    "aspect_ratio": "16:9",
    "resolution": "1080p",
    "generate_audio": False,
    "output_path": "projects/<proj>/assets/video/seg_XX.mp4",
})
```

- Video segments: 5s duration
- Animate segments: 4s duration

#### Phase 2.3: Strip Audio (MANDATORY)

```bash
ffprobe -v error -show_entries stream=codec_type <video_file>
# If audio exists, strip it:
ffmpeg -i <video_file> -an -c:v copy <video_file>_silent.mp4
mv <video_file>_silent.mp4 <video_file>
```

---

## 3. Source Background Music (`music_enabled == true`)

If `music_enabled == false`, skip this section entirely.

### 3.1 Determine Music Mood

Match the search query to the text's emotional character:

| Text Mood | Search Query |
|-----------|-------------|
| Reflective / Literary | `ambient calm reflective minimal piano contemplative instrumental` |
| Motivational / Energetic | `uplifting inspirational gentle build ambient instrumental` |
| Warm / Cozy | `gentle piano warm soft acoustic emotional instrumental` |
| Thought-provoking | `ambient atmospheric deep thinking cinematic instrumental` |

### 3.2 Search via pixabay_music

```python
music_tool = registry.get('pixabay_music')
result = music_tool.execute({
    "query": "<mood-based query>",
    "min_duration": 30,
    "max_duration": 300,
    "output_path": "projects/<proj>/assets/music/bg_music.mp3",
})
```

### 3.3 User Approval

Present the music choice. User can approve, try a different mood (max 2 retries),
provide their own track via `music_library/`, or skip.

---

## T: TTS Narration Generation (`tts_enabled == true`)

If `tts_enabled == false`, skip this section entirely.

### T.1 Voice Selection

1. For Chinese text: prefer `doubao_tts` (natural Mandarin)
2. Use `tts_selector` with rank operation to check availability
3. Select a voice matching the content tone (warm, calm, articulate)

### T.2 Sample Preview (MANDATORY)

Generate narration for the FIRST segment only. Play for user.
If rejected: try different voice (max 3 attempts) or different provider.
**Do not batch generate until the user approves the voice.**

### T.3 Batch Generate

For each script section: generate narration via `tts_selector`.
Verify duration is within 80-120% of planned segment duration.
Store in `projects/<proj>/assets/narration/seg_XX.mp3`.

---

## 4. Write Asset Manifest

```json
{
  "version": "1.0",
  "assets": [
    {
      "id": "cover_book_01",
      "type": "image",
      "subtype": "book_cover",
      "path": "assets/covers/book_01.png",
      "source_tool": "web_search",
      "scene_id": null,
      "book_id": "book_01",
      "book_title": "原子习惯",
      "book_author": "James Clear",
      "resolution": "800x1200"
    },
    {
      "id": "img_seg_01",
      "type": "image",
      "subtype": "generated",
      "path": "assets/images/seg_01.png",
      "source_tool": "image_selector",
      "scene_id": "seg_01",
      "prompt": "<Chinese scene prompt>",
      "resolution": "2560x1440"
    },
    {
      "id": "vid_seg_03",
      "type": "video",
      "subtype": "generated",
      "path": "assets/video/seg_03.mp4",
      "source_image": "assets/images/seg_03.png",
      "source_tool": "video_selector",
      "operation": "image_to_video",
      "scene_id": "seg_03",
      "resolution": "1920x1080",
      "duration_seconds": 5.0,
      "audio_stripped": true
    }
  ],
  "metadata": {
    "asset_mode": "ai-generated",
    "asset_strategy": "image-first-two-phase",
    "phase1_images_generated": 6,
    "phase2_videos_generated": 2,
    "all_audio_stripped": true,
    "music_enabled": false,
    "tts_enabled": false,
    "books_with_covers": 3
  }
}
```

## Quality Gate

- Book cover exists on disk for EVERY book in script.metadata.books
- One visual asset per script segment (image or video)
- AI-generated: Phase 1 user approval before Phase 2 video generation
- ALL video clips verified silent (no audio tracks)
- Music asset exists OR music_enabled=false in manifest metadata
- TTS narration assets exist OR tts_enabled=false in manifest metadata
- All file paths resolve to existing, readable files
- Color palette and visual style consistent across all assets

## Common Pitfalls

- Retrieving low-res or wrong-edition book covers → damage the recommendation's credibility
- Using text_to_video instead of image_to_video → composition drift, less control
- Skipping the Phase 1 → Phase 2 approval gate → wasted video generation budget
- Writing video prompts that re-describe the scene → only describe motion
- Forgetting to strip audio from generated videos → compose stage audio conflicts
- Searching stock with Chinese keywords in stock-footage mode → zero results

---

## S: Stock-Footage Workflow (`asset_mode == "stock-footage"`)

### S.1 Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `script` | Segments + English stock search keywords |
| Tools | `direct_clip_search`, `color_grade` | Stock search + color grading |

Read `script.metadata.visual_direction.<seg_id>.visual_keywords_image` for
search query construction. These should be English concrete search terms
(as written by the script director for stock-footage mode).

### S.2 Phase 1: Stock Search

For EACH script segment, search for video clips:

```python
direct_clip_search = registry.get('direct_clip_search')
result = direct_clip_search.execute({
    "output_dir": "projects/<proj>/assets/video/",
    "queries": [
        {"query": "<English visual keywords from script>", "slot_id": "seg_01", "kind": "video"},
        # ... one query per segment
    ],
    "sources": ["pexels", "pixabay_video", "coverr"],
    "clips_per_query": 3,
    "filters": {
        "orientation": "landscape",
        "min_duration": <segment_duration_seconds>,
        "min_width": 1920
    },
    "extract_thumbnails": True,
    "skip_existing": True
})
```

**If zero results for a segment:**
1. Broaden the query (remove specific modifiers)
2. Try additional sources: `["pexels", "pixabay_video", "coverr", "mixkit"]`
3. Still nothing? Flag for manual review, note in manifest
4. Last resort: reuse a clip from another segment with similar mood

### S.3 Phase 2: Human Clip Selection

**The agent does NOT pick clips. The human does.**

1. Open the clips folder so user can watch videos
2. Print slot-to-clip mapping with source URLs
3. User picks one clip per segment
4. Agent copies selected clips into `selected/` directory

### S.4 Phase 3: Color Grade

```python
color_grade = registry.get('color_grade')
for seg_id in segments:
    color_grade.execute({
        "input_path": f"projects/<proj>/assets/video/selected/{seg_id}.mp4",
        "output_path": f"projects/<proj>/assets/video/graded/{seg_id}.mp4",
        "profile": "cinematic_warm",
        "intensity": 0.8,
        "codec": "libx264",
        "crf": 18
    })
```

### S.5 Phase 4: Strip Audio

All stock clips must be silent before compose:

```bash
for seg in assets/video/graded/seg_*.mp4; do
  has_audio=$(ffprobe -v error -show_entries stream=codec_type "$seg" | grep -c audio || true)
  if [ "$has_audio" -gt 0 ]; then
    ffmpeg -i "$seg" -an -c:v copy "${seg}.silent.mp4" -y && mv "${seg}.silent.mp4" "$seg"
  fi
done
```

### S.6 USER APPROVAL GATE (MANDATORY)

Present ALL selected + graded clips:
1. Thumbnail grid per segment
2. Source attribution (provider, creator, license)
3. Duration check: each clip covers its segment
4. Color grade confirmation

### S.7 Stock-Footage Asset Manifest

Key differences from AI-generated manifest:
- `subtype: "stock"` instead of `"generated"`
- `provider`, `license`, `original_url` populated per clip
- `color_graded`, `grade_profile`, `grade_intensity` fields
- No `image_prompt` or `video_prompt` fields
- `asset_mode: "stock-footage"` in metadata
