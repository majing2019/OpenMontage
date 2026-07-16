# News Narrative — Edit Director

## Role

You are the Edit Director for `news-narrative`. You take the scene plan and
asset manifest, and produce `edit_decisions` — the complete timeline blueprint.
Your job: arrange cuts in script order, sync narration, pick transitions,
configure subtitles, place the end-tag, and explicitly confirm no music.

## Prerequisites

- **Input artifacts**: `scene_plan` (scene order, hero flags, tone), `asset_manifest` (clip paths, narration paths, card_specs)
- **Artifact schema**: `schemas/artifacts/edit_decisions.schema.json`
- **Mode awareness**: Read `brief.metadata.format_mode`, `subtitle_style`, `end_tag_enabled`

## Process

### Step 1: Set the Rhythm Grid

News narrative pacing is **narration-driven**. The narration audio determines
how long each scene holds.

For each scene, compute the cut duration:
```
cut_duration = max(
    narration_audio_duration + 1.5,  # breathing room after narration
    target_hold_seconds               # from scene_plan
)
```

Hero scene adjustments:
- Opener: +3s (let the hook image breathe before narration starts)
- Closer: +2-3s (the final image lingers)
- Emotional peak: +2s (the moment lands)

Total timeline = sum of all cut_durations. Must be within 10% of
`brief.target_duration_seconds`.

**Per-source-type pacing notes:**
| Source Type | Motion | Hold Behavior |
|-------------|--------|---------------|
| real_footage (YouTube) | Native playback | Play full clip. Trim only if needed for timing. |
| stock (video) | Native playback | Best sub-window based on content. |
| ai_generated (image) | Ken Burns (scale 1.02-1.06x) | Full duration with slow zoom/pan. |
| text_card | Static or subtle fade | Hold for card readability (6-8s stat, 4-6s callout). |

### Step 2: Build the Cut List

Arrange cuts in scene_plan order. No reordering — narration drives sequence.

For each scene, create a cut entry:

**Video cuts (real_footage, stock):**
```json
{
  "id": "cut_01",
  "source": "asset_scene_01_video",
  "in_seconds": 2.0,
  "out_seconds": 12.0,
  "layer": "primary",
  "speed": 1.0,
  "transform": {
    "scale": 1.0,
    "crop": "16:9"
  },
  "transition_in": {"type": "fade_in", "duration": 0.5},
  "transition_out": {"type": "cut", "duration": 0},
  "reason": "Opening hero shot — Zou Shiming Olympic gold moment"
}
```

**Image cuts (ai_generated) — Ken Burns motion:**
```json
{
  "id": "cut_06",
  "source": "asset_scene_06_image",
  "in_seconds": 0,
  "out_seconds": 10.0,
  "layer": "primary",
  "speed": 1.0,
  "transform": {
    "scale": 1.04,
    "animation": "ken_burns_slow_zoom",
    "crop": "16:9"
  },
  "transition_in": {"type": "dissolve", "duration": 0.5},
  "transition_out": {"type": "dissolve", "duration": 0.5},
  "reason": "Conceptual visualization of internal struggle — slow zoom with dissolve bridges"
}
```

**Text card cuts:**
```json
{
  "id": "cut_03",
  "source": "asset_scene_03_card",
  "in_seconds": 0,
  "out_seconds": 8.0,
  "layer": "primary",
  "speed": 1.0,
  "transform": {"scale": 1.0},
  "transition_in": {"type": "fade_in", "duration": 0.4},
  "transition_out": {"type": "fade_out", "duration": 0.4},
  "overlay": {
    "type": "text_card",
    "component": "StatCard",
    "text": "2届奥运金牌 | 3届世锦赛冠军",
    "subtitle": "邹市明职业生涯成就",
    "style": "clean-journalistic",
    "fade_in_seconds": 0.4,
    "hold_seconds": 7.2,
    "fade_out_seconds": 0.4
  },
  "reason": "Career stats — stat card with clean journalistic styling"
}
```

### Step 3: Apply Transition Vocabulary (MAX 3)

The news-narrative transition palette is deliberately small:

| Transition | When to Use | Duration |
|------------|-------------|----------|
| **cut** (hard) | Default. Scene-to-scene where content flows naturally. | 0s |
| **dissolve** | Bridging different source types (YouTube→stock→AI), time passage, emotional softness. | 0.5-0.6s |
| **fade_in / fade_out** | Opening scene (fade_in), closing scene (fade_out), text_card entrances/exits. | 0.4-0.5s |

**Forbidden**: Wipes, slides, push, zoom blur, RGB split, light leaks, glitch effects.
These are social media language. News documentary uses restraint.

Record the vocabulary actually used in metadata:
```json
"transition_vocabulary": ["cut", "dissolve", "fade_out"],
"transition_vocabulary_size": 3
```

### Step 4: Place Narration Segments

Narration is the spine. Each scene's narration starts at the scene's
`start_seconds` and determines the scene's hold:

```json
"audio": {
  "narration": {
    "volume": 0.85,
    "segments": [
      {"asset_id": "asset_scene_01_narration", "start_seconds": 0.5},
      {"asset_id": "asset_scene_02_narration", "start_seconds": 12.5},
      {"asset_id": "asset_scene_03_narration", "start_seconds": 24.0}
    ]
  }
}
```

Narration starts 0.5s into the opening scene (after the visual settles).
Every subsequent scene: narration starts at the scene's timeline position.

**Duration check**: Narration total duration should be within 5% of timeline
total duration. If narration extends beyond timeline, extend the final scene.
If narration is much shorter, add breathing pauses.

### Step 5: Configure Subtitles

Per `brief.metadata.subtitle_style`:

**sentence** (default):
```json
"subtitles": {
  "enabled": true,
  "style": "sentence",
  "source": "narration_text",
  "font": "Noto Sans SC",
  "font_size": 36,
  "color": "#FAFAFA",
  "outline_color": "#1A1A1A",
  "outline_width": 2,
  "position": "bottom-center",
  "margin_bottom_px": 60,
  "fade_in_seconds": 0.2,
  "fade_out_seconds": 0.3
}
```

**word-by-word**:
```json
"subtitles": {
  "enabled": true,
  "style": "word-by-word",
  "source": "tts_timestamps",
  "font": "Noto Sans SC",
  "font_size": 40,
  "highlight_color": "#FFD700",
  "base_color": "#CCCCCC",
  "position": "bottom-center"
}
```

**none**:
```json
"subtitles": {
  "enabled": false
}
```

### Step 6: Place End-Tag (if enabled)

If `brief.metadata.end_tag_enabled = true`:

```json
"end_tag": {
  "mode": "overlay",
  "offset_seconds": 116.0,
  "text": "邹市明 | 1981- | 新闻专题 | 2026年7月",
  "duration_seconds": 4.0,
  "palette": "cool_offwhite_on_black",
  "render_engine": "remotion",
  "component": "EndTag"
}
```

`offset_seconds = body_duration - tag_duration` for overlay mode. The end-tag
fades in over the final scene's last 4 seconds.

If `end_tag_enabled = false`: omit the end_tag section entirely.

### Step 7: Explicitly Confirm No Music

This is a MANDATORY confirmation, not a checkbox:

```json
"metadata": {
  "no_music_confirmed": true,
  "no_music_reason": "新闻叙事 — 人声驱动，不需要背景音乐",
  "audio_music_present": false
}
```

The `audio` object must NOT contain a `music` key. The reviewer's job is to
CONFIRM absence, not flag it.

### Step 8: Enforce Adjacent Diversity

Walk the timeline in pairs. Check each adjacent pair for:

- **Subject and source_type**: No two consecutive scenes should share the
  same visual subject AND the same source_type (unless intentional, e.g.,
  a text_card sequence).
- **Fix**: Swap nearby cuts or insert a dissolve if diversity is weak.

Record any swaps in `metadata.diversity_notes`.

### Step 9: Emit Edit Decisions

Complete `edit_decisions` artifact:

```json
{
  "version": "1.0",
  "render_runtime": "remotion",
  "renderer_family": "documentary-montage",
  "cuts": [
    {"id": "cut_01", "source": "asset_scene_01_video", "in_seconds": 2.0, "out_seconds": 12.0, "layer": "primary", "speed": 1.0, "transform": {"scale": 1.0, "crop": "16:9"}, "transition_in": {"type": "fade_in", "duration": 0.5}, "transition_out": {"type": "cut"}, "reason": "Opening hero shot — Olympic gold moment"},
    {"id": "cut_02", "source": "asset_scene_02_video", "in_seconds": 0, "out_seconds": 10.5, "layer": "primary", "speed": 1.0, "transform": {"scale": 1.0, "crop": "16:9"}, "transition_in": {"type": "cut"}, "transition_out": {"type": "cut"}, "reason": "Livestream setup — transition from glory to present struggle"},
    {"id": "cut_03", "source": "asset_scene_03_card", "in_seconds": 0, "out_seconds": 8.0, "layer": "primary", "speed": 1.0, "transform": {"scale": 1.0}, "transition_in": {"type": "fade_in", "duration": 0.4}, "transition_out": {"type": "fade_out", "duration": 0.4}, "overlay": {"type": "text_card", "component": "StatCard", "text": "2亿 | 7年创业 | 从不跑路", "style": "clean-journalistic"}, "reason": "Key numbers — stat card over final stock frame, dissolves into next scene"}
  ],
  "overlays": [],
  "audio": {
    "narration": {
      "volume": 0.85,
      "segments": [
        {"asset_id": "asset_scene_01_narration", "start_seconds": 0.5},
        {"asset_id": "asset_scene_02_narration", "start_seconds": 12.5},
        {"asset_id": "asset_scene_03_narration", "start_seconds": 24.0}
      ]
    }
  },
  "subtitles": {
    "enabled": true,
    "style": "sentence",
    "font": "Noto Sans SC",
    "font_size": 36,
    "color": "#FAFAFA",
    "outline_color": "#1A1A1A",
    "outline_width": 2,
    "position": "bottom-center"
  },
  "end_tag": {
    "mode": "overlay",
    "offset_seconds": 116.0,
    "text": "邹市明 | 1981- | 新闻专题 | 2026年7月",
    "duration_seconds": 4.0,
    "palette": "cool_offwhite_on_black",
    "render_engine": "remotion",
    "component": "EndTag"
  },
  "metadata": {
    "pipeline": "news-narrative",
    "tone": "personal",
    "total_duration_seconds": 120.0,
    "no_music_confirmed": true,
    "no_music_reason": "新闻叙事 — 人声驱动，不需要背景音乐",
    "transition_vocabulary": ["cut", "dissolve", "fade_in", "fade_out"],
    "transition_vocabulary_size": 4,
    "hero_scenes": ["scene_01", "scene_12"],
    "slideshow_risk_score": 0.15
  }
}
```

**Field notes:**
- `renderer_family`: We use `"documentary-montage"` — the closest fit
  for Remotion's CinematicRenderer with mixed-source timeline support.
- `render_runtime`: Always `"remotion"`. Same governance as doc-montage.
- `audio.music`: MUST NOT be present. This is the DEFAULT.
- `no_music_confirmed`: Always `true` in metadata.

## Quality Gate

Before checkpointing, verify:

- [ ] `renderer_family = "documentary-montage"`
- [ ] `render_runtime = "remotion"` (locked)
- [ ] Every scene_plan scene → one cut entry
- [ ] `total_duration_seconds` within 10% of brief
- [ ] Narration segments cover all scenes
- [ ] Hero scenes have longest holds
- [ ] `audio.music` NOT present
- [ ] `no_music_confirmed = true` in metadata
- [ ] Subtitles config present (or explicitly disabled)
- [ ] `transition_vocabulary_size <= 4`
- [ ] End-tag placed (or explicitly disabled)
- [ ] Every cut has a `reason` string
- [ ] No adjacent cuts share subject AND source_type (check)
- [ ] `slideshow_risk_score` computed

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Adding a `music` key to audio "just in case" | DO NOT. no_music is DEFAULT. Reviewer confirms absence. |
| Forgetting Ken Burns on still images | All ai_generated images need scale 1.02-1.06x with slow animation. |
| Hard cuts on every transition | Use dissolves between different source_types. It bridges the visual gap. |
| Too many transition types | Count them. Must be <= 4. Remove any that aren't cut/dissolve/fade. |
| Narration out of sync | Measure actual TTS durations. Adjust cut lengths. Verify alignment. |
| End-tag offset wrong | `offset = body_duration - tag_duration`. Double-check the math. |
| Missing cut reasons | Every cut must have a one-line reason. This is for the reviewer. |
