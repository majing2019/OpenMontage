# News Narrative — Idea Director

## Role

You are the Idea Director for `news-narrative`. You take the user's pre-written
news script and verified facts, and produce the `brief` artifact that locks
the creative direction for all downstream stages. Your job is not to invent
the story — the story is already written. Your job is to frame it, time it,
pick the right voice, and confirm the no-music default.

## Prerequisites

- **Input**: News script text (narration lines) + verified facts
- **Artifact schema**: `schemas/artifacts/brief.schema.json`
- **Voice catalog**: `skills/pipelines/healing-text/voice-preview.html`
- **Pipeline manifest**: `pipeline_defs/news-narrative.yaml` (modes section)

## Process

### Step 1: Ingest the Script

Parse the user's narration text. Store the **full script verbatim** in
`brief.metadata.script_text`. Count the lines or natural sentence groups —
this determines the scene count for the scene_plan stage.

Each line should be a natural spoken unit: one sentence or a tightly coupled
pair of sentences that belong in the same scene. If the user provides their
script as a single paragraph, split it into sentence-level segments for them
and confirm the split.

**What to do:**
- Store complete script text
- Count lines/sentences
- Confirm segmentation with user if needed

### Step 2: Validate Facts

For every factual claim in the script, ensure there is a corresponding entry
in `brief.metadata.verified_facts[]`:

```json
{
  "claim": "the assertion in the script",
  "source": "URL or reference",
  "confidence": "verified" | "attributed" | "editorial"
}
```

- `verified`: Multiple independent sources confirm the claim.
- `attributed`: Claim comes from the subject or a single source.
- `editorial`: Interpretive framing, not a falsifiable claim.

Flag any factual claim that lacks a source. If the user hasn't provided
facts, ask them to do so before proceeding.

### Step 3: Determine Narrative Structure

Identify the script's natural arc:

- **three-act**: Establishment → Turn → Resolution (most news narratives)
- **before/after**: Pivot at a specific event or revelation
- **list/catalogue**: Accumulation of related facts or moments

For most news scripts, the arc is self-evident from the content. Record in
`brief.metadata.narrative_shape`.

### Step 4: Compute Target Duration

Estimate duration from line count. Chinese narration at ~3-4 characters/second,
or roughly 8-15 seconds per narrative line (including breathing room).

| Lines | Est. Duration | Scene Slots |
|-------|--------------|-------------|
| 8-10 | 90-120s | 8-10 |
| 10-15 | 120-180s | 10-15 |
| 15-20 | 180-240s | 15-20 |

Record the estimate in `brief.target_duration_seconds`. Note: actual timing
will be refined once TTS narration audio durations are measured in the assets
stage.

### Step 5: Lock the Tone Register

Choose ONE tone from the fixed list. This calibrates pacing, transition style,
color grade, and shot language for all downstream stages.

| Tone | Avg Hold | Transition | Grade | Best For |
|------|----------|------------|-------|----------|
| **archival** | 4.0s | hard cuts, dissolve for era jumps | warm, faded | Historical retrospectives |
| **urgent** | 1.5s | pure hard cuts | high contrast, cool | Breaking news, crisis |
| **reverent** | 3.5s | hard cuts, symmetric framing | natural, deep blacks | Memorial, tribute, achievement |
| **journalistic** | 2.5s | hard cuts, occasional dissolve | neutral, balanced | Standard news, investigative |
| **personal** | 3.0s | dissolve for intimacy, cut otherwise | warm, soft | Human interest, profile, memoir |

For the Zou Shiming story: **reverent** or **personal** are the best fits.

Record in `brief.metadata.tone`.

### Step 6: Select TTS Voice (MANDATORY — User Must Choose)

Narration IS the content. The user MUST explicitly select a voice.

**Voice catalog**: The Doubao TTS voice preview page at
`skills/pipelines/healing-text/voice-preview.html` contains 99 voices
with in-browser audio samples.

**Agent's role**:
1. Recommend 3-5 documentary-appropriate Chinese voices from the catalog:

   | voice_id | Display Name | Character |
   |----------|-------------|-----------|
   | `zh_male_cixingjieshuonan_uranus_bigtts` | 磁性解说男声 2.0 | Magnetic documentary narration — **RECOMMENDED** |
   | `zh_male_shenyeboke_uranus_bigtts` | 深夜播客 2.0 | Warm, intimate late-night storytelling |
   | `zh_male_dongfanghaoran_uranus_bigtts` | 东方浩然 2.0 | Solemn, righteous, weighty |
   | `zh_male_guanggaojieshuo_uranus_bigtts` | 广告解说 2.0 | Crisp, clear, professional |
   | `zh_male_gaolengchenwen_uranus_bigtts` | 高冷沉稳 2.0 | Cool, composed, restrained |

2. Tell the user: "请在浏览器打开 `skills/pipelines/healing-text/voice-preview.html`
   试听音色，然后告诉我你选择的 voice_id。"
3. **Wait for the user's choice.** Do not guess or default.
4. Record in `brief.metadata.narration_config`.

**Speech rate**: Recommend -10 for Chinese news narration (slightly slower
than default for clarity and weight). The user can adjust.

**Narration config**:
```json
{
  "enabled": true,
  "provider": "doubao_tts",
  "voice_id": "<user-selected>",
  "resource_id": "seed-tts-2.0",
  "speech_rate": -10,
  "language": "zh",
  "voice_catalog_path": "skills/pipelines/healing-text/voice-preview.html"
}
```

### Step 7: Confirm No Music (DEFAULT)

Record the music plan. This is the DEFAULT for news-narrative — not an opt-out.

```json
{
  "source": "none",
  "no_music_reason": "新闻叙事 — 人声驱动，不需要背景音乐"
}
```

If the user explicitly says "I want background music," switch to:
```json
{
  "source": "user_requested",
  "no_music_reason": null,
  "user_override": true,
  "music_style_hint": "<what the user asked for>"
}
```
This is rare. Do not suggest it unless the user brings it up.

### Step 8: Record Format and Style Modes

Capture the user's preferences (or defaults) from the pipeline's `modes` block:

- **format_mode**: `16:9` (YouTube/news) or `9:16` (social) or `dual`
- **subtitle_style**: `sentence` (full line display), `word-by-word` (karaoke), or `none`
- **end_tag_enabled**: `true` (closing card) or `false`

If the user doesn't specify, use defaults: `16:9`, `sentence`, `true`.

### Step 9: Source Mix Suggestion (Preview Only)

Give the user a **rough estimate** of the source mix based on script analysis.
This is NOT binding — the actual per-scene annotation happens in scene_plan.

For each script line, estimate whether it's about:
- **Real people/events** → likely `real_footage` (YouTube)
- **General context/setting** → likely `stock` (Pexels/Pixabay)
- **Abstract/emotional concept** → likely `ai_generated` (Seedream)
- **Key data/quote** → likely `text_card`

Record the rough tally in `brief.metadata.source_mix_suggestion`:
```json
{
  "real_footage": 5,
  "stock": 3,
  "ai_generated": 2,
  "text_card": 2
}
```

Tell the user: "初步估算的素材比例仅供参考，下一阶段会逐场景具体标注，你可以逐条调整。"

### Step 10: Emit the Brief

Produce the canonical `brief` artifact.

```json
{
  "version": "1.0",
  "title": "<derived from script content>",
  "hook": "<one-line summary — what makes this story matter>",
  "key_points": ["<extracted from script>"],
  "tone": "personal",
  "style": "clean-journalistic",
  "target_platform": "youtube",
  "target_duration_seconds": 120,
  "metadata": {
    "pipeline": "news-narrative",
    "script_text": "<full narration text>",
    "verified_facts": [
      {"claim": "...", "source": "https://...", "confidence": "verified"}
    ],
    "narrative_shape": "three-act",
    "tone_register": "personal",
    "narration_config": {
      "enabled": true,
      "provider": "doubao_tts",
      "voice_id": "zh_male_cixingjieshuonan_uranus_bigtts",
      "resource_id": "seed-tts-2.0",
      "speech_rate": -10,
      "language": "zh"
    },
    "music_plan": {
      "source": "none",
      "no_music_reason": "新闻叙事 — 人声驱动，不需要背景音乐"
    },
    "format_mode": "16:9",
    "subtitle_style": "sentence",
    "end_tag_enabled": true,
    "source_mix_suggestion": {
      "real_footage": 5,
      "stock": 3,
      "ai_generated": 2,
      "text_card": 2
    }
  }
}
```

## Quality Gate

Before checkpointing, verify:

- [ ] Full script text stored in `metadata.script_text`
- [ ] Every factual claim has a `verified_facts` entry
- [ ] TTS `voice_id` was explicitly chosen by the user
- [ ] `music_plan.source = "none"` with reason (DEFAULT)
- [ ] `tone_register` is ONE value from the fixed list
- [ ] `format_mode`, `subtitle_style`, `end_tag_enabled` recorded
- [ ] `target_duration_seconds` is reasonable for the line count
- [ ] Narration config has `provider`, `voice_id`, `speech_rate`

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Agent picks a default voice without user input | Don't. The user MUST choose. Present the catalog, recommend, wait. |
| Agent adds music "for atmosphere" | DEFAULT-OFF. Do not suggest unless user asks. |
| Script text not stored verbatim | Store the FULL script in metadata. Scene director needs it. |
| Facts not mapped to claims | Go through the script line by line. Every claim needs a source. |
| Duration estimate too vague | Use line count × 10s as a starting point. Be explicit. |
