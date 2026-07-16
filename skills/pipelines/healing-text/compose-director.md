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

## Runtime Routing (MANDATORY — Remotion ONLY)

This pipeline **REQUIRES Remotion. FFmpeg path is FORBIDDEN.**

The healing aesthetic depends on:
- `<TransitionSeries>` with spring easing for smooth segment crossfade
- `<Sequence>` for self-contained per-segment video + audio + subtitle
- `<Audio>` component for per-segment narration playback (no external mixing needed)
- Spring-animated text fades via `useCurrentFrame()` + `interpolate()`

**Why FFmpeg is forbidden:** FFmpeg concat (demuxer or filter_complex) has proven
unreliable for healing-text: resolution/fps mismatches cause silent failures where
all segments show the same clip; audio_mixer.full_mix silently drops tracks at
non-zero start_seconds; SRT subtitles can't animate; crossfade has no easing.

**Why Remotion solves all of this:**
- Each segment is a `<Sequence>` — a self-contained bubble. Video + narration +
  subtitle all live inside the same Sequence. When the Sequence ends, everything
  stops. No alignment needed.
- `<TransitionSeries>` handles crossfade with `spring()` or `easing.out(exp)` —
  smooth and cinematic, not linear.
- `<Audio>` per Sequence plays narration directly from the MP3 file. No external
  mixing, no audio_mixer, no start_seconds bugs.
- `useCurrentFrame()` + `interpolate()` gives per-frame control over subtitle
  opacity — fade in 0.7s, hold, fade out 0.5s per pipeline spec.

### Asset Mode Pre-Check

Read `script.metadata.asset_mode` (defaults to `"ai-generated"` if absent).
Read `script.metadata.tts_enabled` (defaults to `false` if absent).

Both ai-generated and stock-footage modes use the SAME Remotion composition.
The only difference: ai-generated has still images (needs Ken Burns), stock-footage
has all video clips (native playback). Remotion handles both identically via
`<Img>` vs `<Video>` components.

### Narration sync (when tts_enabled=true)

**No external audio mixing.** Each `<Sequence>` includes its own `<Audio>` component:

```tsx
<Sequence from={segStartFrame} durationInFrames={segDurationFrames}>
  <Video src={segmentVideo} />
  <Audio src={segmentNarration} />
  <AnimatedSubtitle text={segmentText} font="Noto Serif SC" fontSize={bodyFont} />
</Sequence>
```

The narration plays ONLY within its Sequence. When Remotion advances past
`segStartFrame + segDurationFrames`, the `<Audio>` component unmounts and the
sound stops. The next Sequence starts playing its own narration. No bleed.

**Segment duration formula (unchanged):**
```
segFrames = fps × (narration_duration_seconds + 0.7)  // padding for visual hold
```

### Renderer family routing (style-aware):
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

Every healing-text video MUST start with a 5-7 second opening sequence.
Read `script.opening` for hook_line, title_line, hook_style, and duration.

**CRITICAL: The opening is NOT a black card.** The asset stage MUST search
for a background video that matches the opening's emotional tone, generate
TTS narration for the hook_line, and provide the video file. The compose
stage overlays hook text + title text onto this video, synchronized with
the hook TTS narration.

**Reference:** `projects/examples/情感励志4.mp4`

**Asset requirements (checked at compose preflight):**
- [ ] `assets/video/opening/background_9x16.mp4` exists (NOT a generated black frame)
- [ ] `assets/audio/opening_hook.mp3` exists (TTS narration of hook_line)
- [ ] Hook clip duration matches opening.duration_seconds (~5.5s)

**Scene structure:**

```
seg_opening (5.0-7.0s total):
  0.0 – 5.5s: Title — STATIC, NO ANIMATION
    Background: opening background video (searched from stock, color-graded)
    Text overlay: opening.title_line, large white serif, DEAD CENTER
    Font: Noto Serif SC 600 (literary) or "Songti SC" (system Song/Ming)
    Font size: 1.3× body font size
    Style: STATIC — no spring, no scale, no character-by-character reveal.
           The title is a calm, permanent presence on the opening video.
           It does NOT fade in, does NOT fade out, does NOT move.
    Color: white (#FFFFFF) — opening backgrounds are selected for warm/golden
           light, and white serif text on a warm sunrise reads as elegant
           and cinematic (like a movie title card).

  0.0 – 2.0s: Hook — FADE IN/OUT, LOWER-CENTER
    Audio: opening_hook.mp3 (TTS of hook_line, same voice as body)
    Text overlay: opening.hook_line, small white sans-serif, LOWER-CENTER
    Position: y=h*0.65 (NOT center — title sits at center, hook sits below)
    Font: Heiti SC (STHeiti) or Noto Sans SC Light
    Font size: max(0.6× body font, 24px)
    Style: fade in 0.8s, hold, fade out 0.2s (alpha expression via HealingSubtitle)
    Color: white at 85% opacity (less prominent than the title)

  5.5s+: Transition to seg_01
    Title gone (Sequence ends at 5.5s — see Remotion implementation below)
    seg_01 video and subtitle fully visible via crossfade
    Music at normal playback volume
```

**Remotion implementation (mandatory — no FFmpeg):**

The opening renders as a `<TransitionSeries.Sequence>`:
```tsx
<TransitionSeries.Sequence durationInFrames={openingFrames}>
  {/* Background video */}
  <OffthreadVideo src={openingVideo} muted style={cover} />
  {/* STATIC title — no spring, no animate, just text */}
  <div style={{ position: "absolute", inset: 0,
    justifyContent: "center", alignItems: "center" }}>
    <span style={{
      fontFamily: "'Songti SC', 'Noto Serif SC', serif",
      fontSize: titleFontSize,
      color: "#FFFFFF",
      fontWeight: 600,
    }}>
      {title_line}
    </span>
  </div>
  {/* Hook subtitle with fade-in/out (healing_subtitle overlay) */}
  <HealingSubtitle
    text={hook_line}
    fontSize={hookFontSize}
    color="#FFFFFF"
    fadeInSeconds={0.8} fadeOutSeconds={0.2}
    segmentDurationSeconds={openingDuration}
  />
</TransitionSeries.Sequence>
```

**Why no animation on the title:** Healing-text is a quiet, meditative
format. A spring-animated title that bounces in character-by-character
reads as flashy and disrupts the contemplative mood. A static serif title
on a beautiful video background is understated and elegant — it lets the
image and the words do the work without drawing attention to the typography.

**Timeline shift:** All script sections shift by `opening.duration_seconds`.
seg_01 start_seconds = opening duration (not 0).

**Opening metadata in render_report:**
```json
"opening": {
    "hook_line": "如果你也曾在追逐中感到疲惫，这段话送给你",
    "title_line": "幸福不在远方",
    "duration_seconds": 5.5,
    "has_background_video": true,
    "has_hook_tts": true
}
```

### 2. Prepare Subtitle Track (EMBEDDED in each cut — MANDATORY)

**Subtitles are NOT a separate overlay layer.** They are embedded inside each
cut's `TransitionSeries.Sequence`, rendered as a sibling of the video. This is
the only way to guarantee subtitle fade stays in sync with the video crossfade.

**Why embedded, not overlay:** If subtitles are a separate `<Sequence>` layer
positioned by absolute time, they use a different timing model than the
`<TransitionSeries>` video layer (which overlaps sequences for crossfade). The
two drift apart — subtitle fades don't match the video blend. By embedding the
subtitle inside the same Sequence as its video, both share the same local
timeline (`useCurrentFrame()` starts at 0 when the Sequence begins) and the
same lifecycle (mounted/unmounted together).

**Embed subtitle fields directly on each cut:**
```json
{
  "id": "seg_01", "type": "video",
  "source": "path/to/seg_01.mp4",
  "in_seconds": 5.5, "out_seconds": 14.0,
  "subtitleText": "你以为幸福在远方等你，其实幸福就在你身边等你发现。",
  "subtitleFontSize": 32,
  "subtitleColor": "#1A1A1A",
  "subtitleShadow": "0 2px 16px rgba(255,255,255,0.55)",
  "subtitleEndSeconds": null
}
```

**Subtitle fade syncs with the video crossfade.** The `HealingSubtitle`
component's `fadeInSeconds` and `fadeOutSeconds` are set to the SAME value as
`crossfadeSeconds` (0.8s). Because the subtitle lives inside the Sequence, its
fade-in begins exactly when the video crossfade-in begins, and its fade-out
ends as the Sequence exits. No drift possible.

**Special cases (controlled via cut fields):**

| Case | Field | Behavior |
|------|-------|----------|
| Opening: video no fade-in, subtitle fades in | first cut gets `noIntroFade=true` (video) but subtitle still uses its own fade curve | Video snaps visible; subtitle fades in over 0.8s |
| Last segment linger | `subtitleEndSeconds` set < `out_seconds` | Subtitle fades out at `subtitleEndSeconds`; video Sequence continues to `out_seconds` for the linger duration (pure image + music) |
| Hook on opening | `subtitleVerticalPosition: 0.65` | Hook sits lower-center; title sits dead-center. No overlap. |

**Do NOT use the `overlays[]` array for healing-text body subtitles.**
Overlays are a separate timing layer and will drift from the TransitionSeries
video crossfade. Body subtitles belong on cuts.

- **Adaptive text color from CENTER-REGION luma (MANDATORY):**
  Text sits in the center of the frame — analyzing the full frame's luma is
  wrong when the edges are bright but the center is dark (or vice versa).
  The pipeline manifest's `text_color_formula` defines the rule:

  1. For each body segment, crop the video to the text region: center 60% width × 40% height
  2. Analyze the cropped region's average luma:
     `ffprobe -f lavfi "movie=$VIDEO,crop=iw*0.6:ih*0.4:(iw-ow)/2:(ih-oh)/2,signalstats" -show_entries frame_tags=lavfi.signalstats.YAVG`
  3. Center luma > `light_threshold` (128) → use STRONG dark text: `#1A1A1A` (pure near-black,
     stronger contrast than the old #3C3833 charcoal)
  4. Center luma ≤ 128 → use PURE white: `#FFFFFF` (stronger contrast than the old #F0F8FA cool white)
  5. ONE consistent color for the entire segment — recompute per segment

- **Text shadow for contrast (MANDATORY):**
  - Light center (dark text #1A1A1A): `textShadow: "0 2px 16px rgba(255,255,255,0.55)"` (white glow — makes dark letters pop on bright video)
  - Dark center (white text #FFFFFF): `textShadow: "0 2px 16px rgba(0,0,0,0.65)"` (black glow — makes white letters pop on dark video)
  - Shadow is stronger than before (0.55–0.65 vs old 0.5–0.7) to ensure legibility

- **Resolution-adaptive font sizing (MANDATORY — TWO-TIER):**
  Font size is **auto-calculated** from video width + longest text line.
  See `transition_defaults.text.font_size_formula` in the pipeline manifest.
  All body segments use the SAME font size — never vary between segments.
  The opening title uses 1.3× body size; the opening hook uses 0.6× body size.

  ```
  # Step 1: Determine tier from the longest text line across ALL body segments
  longest_chars = max(len(seg.text) for seg in body_segments)

  # Step 2: Select fill_ratio tier
  if longest_chars <= font_size_formula.long_char_threshold:  # ≤ 10 chars
      fill_ratio = font_size_formula.short_text.target_fill_ratio[orientation]
  else:
      fill_ratio = font_size_formula.long_text.target_fill_ratio[orientation]

  # Step 3: Compute and clamp
  font_size = clamp(width × fill_ratio / longest_chars,
                    font_size_formula.min_font[orientation],
                    font_size_formula.max_font[orientation])
  ```

  **Why two tiers:** The reference video (情感励志4) has 3-5 character lines
  like "在雨中起舞". Applying the same 0.72 fill_ratio to 20-character lines
  like "幸福不是拥有更多，是感到自己被需要" produces ~39px → clamped to 44px
  minimum — which overflows at 44×20=880px on a 1080px screen with character
  spacing. The long_text tier (0.42 ratio) gives 1080×0.42/20≈23px → clamped
  to 32px, leaving comfortable margins.

  **Example (9:16, 1080×1920, longest line 20 chars):**
    Tier: long_text (20 > 10)
    font_size = clamp(1080 × 0.42 / 20, 32, 52) = clamp(22.7, 32, 52) = 32px ✅

  **Example (9:16, 1080×1920, longest line 6 chars):**
    Tier: short_text (6 ≤ 10)
    font_size = clamp(1080 × 0.72 / 6, 32, 52) = clamp(129.6, 32, 52) = 52px ✅

- **Text position (USER CHOICE — read from script metadata):**
  Read `script.metadata.text_overlay_position`:
  - `"center"` → text_position.center (alignment=5, margin_v=0). Best for
    literary/philosophical content where the text IS the visual focus.
  - `"top_center"` → text_position.top_center (alignment=8, margin_v=60).
    Best for short punchy social-media text competing with platform UI.
  - Default per playbook: literary-illustration → "center",
    warm-illustration → "top_center".
  - The script director MUST ask the user. Never assume.

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
SEG_01 (video)    GAP   SEG_02 (video)    GAP   SEG_03 (video)    ...
┌────────────┐    ██   ┌────────────┐    ██   ┌────────────┐
│Stock video │    ██   │Stock video │    ██   │Stock video │
│color graded│    ██   │color graded│    ██   │color graded│
│Trim to dur │    ██   │Trim to dur │    ██   │Trim to dur │
│[subtitle]  │    ██   │[subtitle]  │    ██   │[subtitle]  │
└────────────┘    ██   └────────────┘    ██   └────────────┘
                  0.3s                    0.3s
```

No Ken Burns. No still images. Every clip plays natively. Trim each
to exactly its segment duration. Cross-dissolve transitions via
`<TransitionSeries>` + `fade()` — outgoing fades out WHILE incoming
fades in (see §4 Transitions for implementation).

**Video underflow:** If a stock clip is shorter than the segment duration,
Remotion's `<OffthreadVideo>` freezes on the last frame. This is acceptable
— the narration finishes over a held image. If the clip is < 60% of
segment duration, pick a longer clip from the search candidates instead
(see §4a Video Underflow).

**Peak segment treatment:**
The `video` tier segment (emotional peak) gets special treatment:
- Subtitle enters slightly later (0.5s into the clip) for dramatic pause
- Slightly larger font size for emphasis (+10%)
- Longer hold before fade-out
- Crossfade transition is slightly longer (1.2s instead of 1.0s) for impact

### 3a. TTS-Driven Segment Timing (SINGLE source of truth)

**Narration durations are the single source of truth.** The entire timeline —
video, audio, and subtitles — flows from them. There is only ONE computation:

```
For each body segment:
  video_start  = previous_video_end        (continuous, NO gaps)
  video_dur    = narration_dur + PAUSE + CROSSFADE
  video_end    = video_start + video_dur
  tts_end      = video_start + narration_dur
  subtitle_end = video_end                 (embedded in Sequence, auto-fades)

For the last segment:
  video_dur    = narration_dur + PAUSE + CROSSFADE + LINGER
  subtitle_end = video_start + narration_dur + PAUSE + LINGER
               (subtitle stays visible through the linger, fades at the end)

PAUSE    = 0.5s   (silence between narration end and subtitle fade start)
CROSSFADE = 0.8s  (from transition_defaults.video.crossfade_duration_seconds)
LINGER   = 2.0s   (from transition_defaults.video.last_segment_linger_seconds)
```

**Why this guarantees alignment:** The audio mix (adelay+amix) places each
narration at `video_start`. The subtitle is embedded in the Sequence at
`video_start`. The video Sequence starts at `video_start`. They all share
the same `video_start` — derived once from narration durations. There is
no second computation that can drift.

**Example — single-source timeline computation:**
```
Narration: seg_01=7.8s, seg_02=6.8s, seg_03=7.3s, seg_04=8.8s, seg_05=7.8s, seg_06=6.0s

seg_01: video 5.5-14.6s (7.8+0.5+0.8=9.1s) | TTS 5.5-13.3s | subtitle 5.5-14.6s
seg_02: video 14.6-22.7s (6.8+0.5+0.8=8.1s) | TTS 14.6-21.4s | subtitle 14.6-22.7s
seg_03: video 22.7-31.3s (7.3+0.5+0.8=8.6s) | TTS 22.7-30.0s | subtitle 22.7-31.3s
seg_04: video 31.3-41.4s (8.8+0.5+0.8=10.1s)| TTS 31.3-40.1s | subtitle 31.3-41.4s
seg_05: video 41.4-50.5s (7.8+0.5+0.8=9.1s) | TTS 41.4-49.2s | subtitle 41.4-50.5s
seg_06: video 50.5-59.8s (6.0+0.5+0.8+2.0=9.3s) | TTS 50.5-56.5s | subtitle 50.5-59.8s

Check: TTS→fade_gap = 0.5s for EVERY segment. Audio adelay positions = video_start.
All three timelines (video, audio, subtitle) derived from the same computation.
```

**Synchronization check before compose:**
- [ ] Each body segment narration file exists and has a known duration
- [ ] Video clip is at least as long as narration + padding (trim from start if longer)
- [ ] If a video clip is too short, flag it — don't silently loop or stretch
- [ ] Subtitles use `healing_subtitle` overlays on the TTS-driven timeline (not SRT/ASS)
- [ ] Audio mixer timeline uses TTS-driven start times for speech tracks
- [ ] **Narration NEVER bleeds into the next segment**: check that
      `narration_end_time < segment_end_time` for every segment
- [ ] **Audio resampled to 48kHz before AAC encoding**: audio_mixer may output
      192kHz WAV — FFmpeg AAC encoder produces SILENCE at non-standard rates.
      Always resample: `ffmpeg -i mixed.wav -ar 48000 -ac 2 mixed_48k.wav`

**Why this matters:** Without TTS-driven switching, the video either cuts off
mid-sentence or lingers awkwardly after the voice stops. With TTS-driven
switching, the visual rhythm follows the spoken rhythm — the hallmark of
a professionally edited healing-text video.

**Audio resampling is MANDATORY:** The `audio_mixer` tool may output WAV at
non-standard sample rates (192kHz has been observed). FFmpeg's AAC encoder
silently produces near-silent output when fed 192kHz mono WAV — the only
audible content is the loudest peaks (typically the opening hook). Always
resample the mixed WAV to 48kHz stereo (`-ar 48000 -ac 2`) before muxing
into the final MP4.

### 4. Transitions (cross-dissolve — NO black frames)

All transition timings come from `transition_defaults.video` in the manifest.

**MANDATORY: Use cross-dissolve, never black-frame gaps.** Adjacent segments
MUST overlap so the outgoing video fades out WHILE the incoming video fades
in. A visible black frame between segments reads as a glitch, not a breath.

**Implementation — Remotion `<TransitionSeries>` + `fade()`:**
```tsx
import { TransitionSeries, fade } from "@remotion/transitions";

<TransitionSeries>
  {segments.map((seg, i) => (
    <>
      <TransitionSeries.Sequence durationInFrames={seg.frames}>
        <SegmentScene cut={seg} />
      </TransitionSeries.Sequence>
      {/* cross-dissolve: outgoing + incoming overlap and blend */}
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: Math.round(CROSSFADE * fps) })}
      />
    </>
  ))}
</TransitionSeries>
```

**Crossfade durations (from `transition_defaults.video`):**
| Context | Duration |
|---------|----------|
| Standard segment → segment | `crossfade_duration_seconds` (0.8s) |
| Into / out of peak segment | `crossfade_peak_duration_seconds` (1.2s) |

**Why `<TransitionSeries>` and not plain `<Sequence>`:** plain Sequences placed
back-to-back produce a hard cut at the boundary — the background color flashes
for one frame (the "black frame" glitch). TransitionSeries overlaps adjacent
sequences and blends them with `fade()`, producing a seamless cross-dissolve.

**Text fade independence:**
Subtitles fade in/out on their own schedule (see §2 healing_subtitle). Because
each subtitle lives in its own TransitionSeries.Sequence bounded by the segment
duration, the subtitle's fade-out completes as the segment ends — naturally
coordinated with the crossfade. No text appears during the blend window.

### 4a. Video Underflow — narration must always finish

**Problem:** A segment's duration is `narration + 0.7s padding`. The stock
video clip may be SHORTER than this. If the video ends before the narration,
the viewer sees text being read over a frozen/black frame.

**Rule: Remotion `<OffthreadVideo>` freezes on the last frame by default.**
When a video clip is shorter than its segment, it stops at its final frame
and holds there until the segment ends. This is the desired behavior — the
narration finishes over a held image, which reads as intentional (a
deliberate pause on a key frame).

**Do NOT:** loop the video, speed it up to fit, or truncate the narration.
Both look broken.

**Validation (per segment before render):**
- [ ] `segment_duration >= narration_duration + 0.5s` (narration always fits)
- [ ] If `video_clip_duration < segment_duration`, confirm OffthreadVideo
      freeze behavior is acceptable (held last frame). If the clip is shorter
      than ~60% of the segment, pick a longer clip from the search results.
- [ ] After render: scrub to each segment's final 1s — narration must
      complete before the crossfade to the next segment begins.

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
