# Script Director — Book Recommend Pipeline

## When To Use

The user provides narration text + book information (title, author per book).
Your job: segment the text into visual beats, analyze the emotional mood of each
segment, assign motion priority tiers, extract concrete visual keywords for
image/video generation, extract book cover search queries, and propose fonts.
The user's text IS the video's voice. TTS narration is an optional add-on.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Input | User-provided narration text + book info | Raw material |
| Pipeline | `pipeline_defs/book-recommend.yaml` | Stage config, review criteria |

## Motion Priority Tiers

Each segment gets ONE of three motion tiers:

| Tier | What it gets | Budget hint | Visual character |
|------|-------------|-------------|------------------|
| `video` | AI video clip (Seedance, 4-5s) or stock video | $$$ | Real motion — camera movement, natural action |
| `animate` | Image→video or stock video (3-4s) | $$ | Gentle motion, can be stock footage |
| `still` | Still image + Ken Burns | $ | Quiet moments, breathing space |

**Rules for ai-generated mode:**
- `video` — emotional peaks, the climax. Max 30% of total segments.
- `animate` — emotional buildup, transition moments.
- `still` — quiet connective tissue, setup, gentle landing.

**For stock-footage mode:** All segments CAN be `video` since stock clips cost nothing.
The emotional arc still matters for pacing — peak segments get longer transitions.
`still` is still valid for quiet breathing moments.

## Process

### 1. Receive and Understand

Read the user's narration text and book info carefully. Note:
- The emotional arc — where does it start, peak, land?
- The rhythm — short punchy lines vs. flowing prose
- How many books are being recommended (drives format_mode choice)
- Which book/quote is THE one — the emotional peak that deserves video budget

### 2. Format Mode Selection (MANDATORY)

Present the user with three content structures:

**Option A — Single Book Deep Dive:**
- One book, full depth. Plot overview → key insights → memorable quotes → personal reflection
- Duration: 3-5 minutes
- Best for: Literary fiction, profound non-fiction, life-changing books

**Option B — Book List Quick Recs (Default):**
- 3-5 books, 20-40 seconds each. Fast-paced, hook-driven.
- Duration: 60-90 seconds
- Best for: "5 books that changed my thinking" style content

**Option C — Themed Book List:**
- Books grouped around a central theme (e.g., "anxiety relief", "cognitive upgrade")
- Each book gets screen time tied to theme relevance
- Duration: 2-3 minutes
- Best for: Curated lists with a clear thesis

Record the selection: `format_mode: "single-book" | "book-list" | "themed-list"`

### 3. Asset Mode Selection (MANDATORY)

**Option A — AI Generated (Default):**
- Assets: Seedream still images → optional Seedance image_to_video for peak segments
- Cost: ~$3.00
- Best for: Maximum creative control, unique cinematic aesthetics
- Motion budget rules apply

**Option B — Stock Footage:**
- Assets: Video clips from Pexels/Pixabay/Coverr via direct_clip_search
- Cost: $0.00
- Best for: Zero-budget runs, quick turnaround
- All segments can be `video` priority

Record the selection: `asset_mode: "ai-generated" | "stock-footage"`

### 4. Music & TTS Toggles (MANDATORY)

Ask the user two yes/no questions:

**Background Music?** (Default: No)
- Yes: Background music sourced from pixabay_music, mixed at low volume (~0.10)
- No: Silent video, subtitle-only delivery

**TTS Narration?** (Default: No)
- Yes: AI narration generated per segment via tts_selector. Music ducks during speech.
- No: Subtitles carry the entire voice

Record: `music_enabled: true | false`, `tts_enabled: true | false`

### 5. Segment the Text

Break the narration into 3-8 visual segments. Rules:
- Each segment is a self-contained thought or emotional beat
- Natural pauses: sentence breaks, paragraph breaks, emotional turns
- Vary segment length for rhythm — some short (3-5 words for impact), some longer
- Assign approximate display duration per segment:
  - Short impactful line: 4-5 seconds
  - Medium flowing sentence: 5-8 seconds
  - Long passage: 8-12 seconds

### 6. Assign Motion Priority and Visual Direction

For EACH segment, produce:

```yaml
segment_id: seg_01
text: "这本书改变了我对时间的理解"
mood: reflective
motion_priority: still          # still | animate | video
visual_keywords_image:
  - "sunlight streaming through old library window, dust motes, warm amber glow"
visual_keywords_video:
  - "slow push-in through library aisle, golden light, floating dust particles"
color_palette: warm-muted
duration_seconds: 5
book_ref: book_01               # which book this segment discusses
```

**Visual keyword rules:**
- MUST be concrete and imageable (a camera could capture it)
- MUST match the segment's emotional tone
- For ai-generated: Write in Chinese (Seedream/Seedance are Chinese-native models)
- For stock-footage: Write in English (stock APIs use English queries, Chinese returns nothing)
- Include lighting direction, color temperature, and composition hints
- Each segment gets 1-2 visual keyword groups

**For stock-footage — extra rules:**
- English concrete search terms: `"morning library sunlight"` not `"清晨图书馆"`
- Scene-focused: `"cozy reading nook window light"` not `"the quiet joy of reading"`
- Consider what EXISTS in stock libraries: nature, interiors, cityscapes, people reading

### 7. Book Metadata Extraction

For each book in the recommendation, extract:

```yaml
book_id: book_01
title: "原子习惯"
author: "James Clear"
cover_search_query: "Atomic Habits James Clear book cover high resolution"
quote: "You do not rise to the level of your goals. You fall to the level of your systems."
quote_segment: seg_02            # which segment this quote appears in (optional)
```

### 8. Propose Font Shortlist

Present 2-3 font options matching the text's character:

```
Option A: 宋体/衬线 — "Noto Serif SC" / "Source Han Serif"
  Best for: 文学典雅, 深度书评

Option B: 细黑体 — "Noto Sans SC Light"
  Best for: 现代简约, 知识型内容

Option C: 楷体 — "LXGW WenKai"
  Best for: 文艺手写感, 个人色彩
```

**Font family is user-approved; font SIZE is auto-calculated** via the font_size_formula
in the pipeline manifest. Record `selected_font` (family + weight) after user approval.

### 9. Write the Script Artifact

```json
{
  "version": "1.0",
  "title": "<video title derived from content>",
  "total_duration_seconds": <sum of segment durations>,
  "sections": [
    {
      "id": "seg_01",
      "text": "<exact narration text>",
      "start_seconds": 0,
      "end_seconds": 5,
      "label": "opening"
    }
  ],
  "metadata": {
    "format_mode": "book-list",
    "asset_mode": "ai-generated",
    "music_enabled": false,
    "tts_enabled": false,
    "books": [
      {
        "book_id": "book_01",
        "title": "原子习惯",
        "author": "James Clear",
        "cover_search_query": "Atomic Habits James Clear book cover high resolution",
        "quote": "You do not rise to the level of your goals...",
        "quote_segment": "seg_02"
      }
    ],
    "visual_direction": {
      "seg_01": {
        "mood": "reflective",
        "motion_priority": "still",
        "visual_keywords_image": ["sunlight through library window, warm glow"],
        "visual_keywords_video": ["slow push-in library aisle, golden light"],
        "color_palette": "warm-muted",
        "duration_seconds": 5,
        "book_ref": "book_01"
      }
    },
    "motion_budget": {
      "video_count": 1,
      "animate_count": 2,
      "still_count": 3,
      "rationale": "Single emotional peak at seg_03, buildup and landing as animate/still"
    },
    "font_shortlist": [
      {"name": "Noto Serif SC", "category": "serif", "rationale": "Literary, elegant"},
      {"name": "Noto Sans SC Light", "category": "sans-serif", "rationale": "Modern, clean"}
    ],
    "selected_font": "<set after user approval>",
    "text_character": "<one-line description of the text's mood>",
    "visual_universe": "<one-line description of the visual world>"
  }
}
```

### 10. Present and Get Approval

Before advancing, present to the user:
1. **Format mode** — single-book, book-list, or themed-list
2. **Asset mode** — ai-generated or stock-footage
3. **Music & TTS** — on/off decisions
4. **Segmentation + Motion Map** — emotional arc with motion priority labels
5. **Visual mood board** — keywords per segment, which gets the video budget
6. **Book metadata** — title, author, cover search queries, quote placements
7. **Font shortlist** — 2-3 options with reasoning

Wait for explicit approval on all items. Record `selected_font` in metadata.

## Quality Gate

- format_mode, asset_mode, music_enabled, tts_enabled recorded in metadata
- Text segmented into 3-8 natural beats
- Every segment has visual_keywords (Chinese for AI, English for stock)
- Motion priority is sparse (ai-generated: max 30% video) or intentional (stock: all-video OK)
- The emotional peak IS the video segment (if applicable)
- Book metadata complete with cover_search_query per book
- Font shortlist offers genuine stylistic contrast (2-3 options)
- Total duration feels unhurried and appropriate for the format_mode

## Common Pitfalls

- Making every segment `video` in ai-generated mode — burns budget, loses impact
- Using Chinese visual keywords for stock-footage mode — stock APIs need English
- Using abstract/poetic keywords for stock search — write what a search engine can find
- Forgetting to include cover_search_query for each book
- Same motion description for every video segment ("slow pan" × 5 = boring)
- Not asking about music/TTS — these are user decisions, not agent defaults
