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
  0.0 – 1.5s: Hook Phase
    Background: opening background video (searched from stock, color-graded)
    Audio: opening_hook.mp3 (TTS of hook_line, same voice as body)
    Text overlay: opening.hook_line, small white sans-serif, center-lower
    Font: Noto Sans SC Light, font_size per two-tier formula (hook tier: 0.6× body size)
    Animation: fade in 0.5s, hold, fade out 0.5s

  1.5 – 5.5s: Title Phase
    Background: same opening video continues (or crossfade to seg_01)
    Text overlay: opening.title_line, large serif, center
    Font: Noto Serif SC 600 (literary) or Noto Sans SC 500 (warm)
    Font size: 1.3× body font size (title is larger than segment text)
    Animation: fade in 0.5s, hold until 4.5s, fade out by 5.5s

  5.5s+: Main Content
    Title gone, seg_01 video and subtitle fully visible
    Music at normal playback volume
```

**FFmpeg implementation (stock-footage path):**

Do NOT use `color=c=black` as the background. Do NOT use SRT for the opening
— the hook line and title need DIFFERENT positions and font sizes, which SRT
cannot express in a single style.

**CRITICAL — Opening text uses TWO SEPARATE FFmpeg passes.** Chaining multiple
`drawtext` filters with `enable` clauses in one `-vf` chain is fragile: when
one filter's `enable` window expires, it can drop frames and break downstream
filters. Two independent passes — one per text element — then overlay.

**CRITICAL — Use `textfile=` NOT `text=` for Chinese text.** FFmpeg's `drawtext`
filter reads the `text=` parameter as a C string. Chinese characters embedded
directly in the argument can get mangled by shell escaping, locale settings,
or FFmpeg's internal UTF-8 handling. ALWAYS write Chinese text to a temporary
UTF-8 file and reference it via `textfile=`. The file MUST be UTF-8 encoded
without BOM.

```bash
# Write text to UTF-8 files (do this in Python or with printf, never echo)
printf '%s' '幸福不在远方' > /tmp/title.txt
printf '%s' '如果你也曾在追逐中感到疲惫，这段话送给你' > /tmp/hook.txt
```

**MANDATORY: Test font CJK support before rendering.** Not all fonts work with
FFmpeg's drawtext for Chinese glyphs — even when the font file contains CJK
characters. PingFang.ttc is a known failure case on macOS. ALWAYS run a quick
test before committing:

```bash
printf '测试' > /tmp/font_test.txt
ffmpeg -f lavfi -i color=c=black:s=200x200:d=0.1 \
  -vf "drawtext=textfile=/tmp/font_test.txt:fontfile=/path/to/font:fontsize=30:fontcolor=white:x=10:y=10" \
  -vframes 1 /tmp/font_check.png
# If font_check.png < 5KB, the font does NOT work — pick another.
```

**Known working fonts for Chinese drawtext on macOS:**
| Font | Path | Style | Use for |
|------|------|-------|---------|
| Songti SC | `/System/Library/Fonts/Supplemental/Songti.ttc` | Serif | Title |
| Heiti SC | `/System/Library/Fonts/STHeiti Medium.ttc` | Sans-serif | Hook, labels |
| Arial Unicode | `/System/Library/Fonts/Supplemental/Arial Unicode.ttf` | Sans-serif | Hook fallback |
| PingFang | DO NOT USE — FFmpeg drawtext cannot render CJK glyphs from PingFang.ttc |

**Pass 1 — Title text (dead center, ENTIRE opening 0–5.5s, serif, white):**
```bash
BODY_FONT_SIZE=32
TITLE_FONT_SIZE=$((BODY_FONT_SIZE * 13 / 10))

ffmpeg -i background.mp4 -t 5.5 \
  -vf "drawtext=textfile=/tmp/title.txt:\
       fontfile=/System/Library/Fonts/Supplemental/Songti.ttc:\
       fontsize=${TITLE_FONT_SIZE}:fontcolor=white:\
       x=(w-tw)/2:y=(h-th)/2:enable='between(t,0,5.5)'" \
  -c:v libx264 -crf 18 -an opening_title.mp4
```

**Pass 2 — Hook text (lower-center, FADE IN/OUT, sans-serif):**
```bash
HOOK_FONT_SIZE=$((BODY_FONT_SIZE * 6 / 10))
if [ $HOOK_FONT_SIZE -lt 24 ]; then HOOK_FONT_SIZE=24; fi

# Alpha fade expression:
#   0.0–0.3s: invisible (alpha=0)
#   0.3–1.1s: fade IN  (alpha 0 → 0.85)
#   1.1–1.8s: hold     (alpha=0.85)
#   1.8–2.0s: fade OUT (alpha 0.85 → 0)
ALPHA_EXPR="if(lt(t,0.3), 0, if(lt(t,1.1), 0.85*(t-0.3)/0.8, if(lt(t,1.8), 0.85, if(lt(t,2.0), 0.85*(2.0-t)/0.2, 0))))"

ffmpeg -i opening_title.mp4 \
  -vf "drawtext=textfile=/tmp/hook.txt:\
       fontfile=/System/Library/Fonts/STHeiti Medium.ttc:\
       fontsize=${HOOK_FONT_SIZE}:fontcolor=white:\
       alpha='${ALPHA_EXPR}':\
       x=(w-tw)/2:y=h*0.65:enable='between(t,0,2.0)'" \
  -c:v libx264 -crf 18 -an opening_final.mp4
```

**Key rules for opening text:**
- `textfile=` (NOT `text=`) for ALL Chinese text — avoids encoding corruption
- `fontfile=` with a CONFIRMED-WORKING CJK font path — test first
- **Title stays visible for the ENTIRE opening** (0–5.5s). It is the visual anchor.
- **Hook fades IN/OUT** with an alpha expression — cinematic layered text effect
- Two separate FFmpeg passes — avoids `enable` window expiration breaking the chain
- Hook minimum 24px — smaller Chinese text is illegible on mobile
- Verify after rendering: extract frames at 0.5s (hook fading in), 1.5s (both visible), 3.0s (title only)

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

### 2. Prepare Subtitle Track (`healing_subtitle` Remotion overlay — MANDATORY)

**Subtitles MUST fade in and fade out.** Subtitles that appear/disappear
instantly look amateur and clash with the healing aesthetic.

Since this pipeline is Remotion-only (no FFmpeg, no SRT/ASS files), subtitles
are rendered as **`healing_subtitle` overlays**. Each segment's subtitle is one
overlay entry. The `HealingSubtitle` component
(`remotion-composer/src/components/HealingSubtitle.tsx`) uses
`useCurrentFrame()` + `interpolate()` to produce a smooth opacity curve:

```
opacity = interpolate(frame, [0, fadeIn, fadeOutStart, total], [0, 1, 1, 0])
```

- **Fade IN**: `transition_defaults.text.fade_in_seconds` (default 0.7s)
- **Fade OUT**: `transition_defaults.text.fade_out_seconds` (default 0.5s)
- A gentle 12px→0 upward drift accompanies the fade-in for a "breathing" feel

**Overlay entry structure (per body segment):**
```json
{
  "id": "sub_seg_01",
  "type": "healing_subtitle",
  "text": "你以为幸福在远方等你，其实幸福就在你身边等你发现。",
  "in_seconds": 5.5,
  "out_seconds": 14.0,
  "fontSize": 32,
  "color": "#3C3833",
  "fadeInSeconds": 0.7,
  "fadeOutSeconds": 0.5
}
```

**Why `healing_subtitle` overlay (not SRT/ASS, not text_card cut):**
- SRT/ASS are external subtitle files — incompatible with Remotion's React render
- The generic `TextCard` cut has an opaque background + Inter font, wrong for healing
- `healing_subtitle` is a transparent overlay: Chinese-serif text centered on the
  video, no background box, with per-frame opacity control

**Text fades are independent of segment boundaries.** Because each subtitle
lives inside its own `<Sequence>` (bounded by `in_seconds`/`out_seconds`), the
fade-out completes exactly as the Sequence ends — the next segment's subtitle
fades in fresh. No overlap, no abrupt cut. This is the synchronization guarantee:
**video, narration, and subtitle all share the same Sequence, so they start
and stop together.**

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
to exactly its segment duration. Crossfade transitions between segments.

**Segment gap via Remotion `<TransitionSeries>`:**

Read `transition_defaults.video.segment_gap_seconds` (default 0.3s).
Remotion's `<TransitionSeries>` with `layout="none"` automatically inserts
a brief hold between sequences. Combined with `spring()` easing on the
crossfade transition, this creates the natural 0.3s breathing space
between segments without manual black-frame insertion.

**Why Remotion doesn't need concat normalization:** Remotion renders each
frame independently from the source clips. There is no filter_complex
that silently fails on resolution mismatches. Each `<Sequence>` plays
its assigned video file; if the file exists, it renders. Period.

**Peak segment treatment:**
The `video` tier segment (emotional peak) gets special treatment:
- Subtitle enters slightly later (0.5s into the clip) for dramatic pause
- Slightly larger font size for emphasis (+10%)
- Longer hold before fade-out
- Crossfade transition is slightly longer (1.2s instead of 1.0s) for impact

### 3a. TTS-Driven Segment Timing (when tts_enabled)

**TTS narration DRIVES video segment switching.** The viewer's experience is:
hear the sentence → see the video → sentence ends → video switches. Video
segments exist to accompany the spoken word, not the other way around.

Each segment's video duration is determined by its narration, not by the
script director's initial estimate:

```
video_duration = narration_duration + padding (0.5–1.0s)
```

The padding gives a brief visual hold after the voice stops — the viewer
absorbs the last words while the image lingers, then the next segment begins.

**How to compute the timeline (MANDATORY when tts_enabled=true):**

1. For each body segment, read `narration.duration_seconds` from the asset manifest
2. Set segment video duration: `narration_duration + 0.7s` (default padding)
3. Compute cumulative start times from these durations
4. Include `segment_gap_seconds` (0.3s black) between segments
5. The script's `start_seconds` / `end_seconds` are IGNORED — they were estimates
   written before narration was generated

**Example — script estimates vs TTS-driven reality:**

```
Segment    Script (estimate)    Narration actual    Video duration (narration + 0.7s)
seg_01     7.0s                  7.8s                8.5s
seg_02     7.0s                  6.8s                7.5s
seg_03     8.0s                  7.3s                8.0s
seg_04     7.0s                  8.8s                9.5s
seg_05     7.0s                  7.8s                8.5s
seg_06     9.0s                  6.0s                6.7s

Timeline: 0 → 8.5 → 16.3 (8.5+7.5+0.3gap) → 24.6 → 34.4 → 43.2 → 50.2s
(script estimated 50.5s — TTS-driven is 50.2s — close enough)
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

### 4. Transitions

All transition timings come from the pipeline manifest's `transition_defaults` section.
If the user or project overrides these in `edit_decisions.metadata`, use the override values.

**Between segments (video crossfade):**
- Cross-dissolve: `transition_defaults.video.crossfade_duration_seconds` (1.0s)
- Peak segment: `transition_defaults.video.crossfade_peak_duration_seconds` (1.2s)
- Breathing pause: `transition_defaults.video.breathing_pause_seconds` (0.4s, image only, no text)

**Text fade independence (CRITICAL):**
Text subtitles fade IN and OUT on their own schedule, completely independent of the
video crossfade between clips. This ensures clean readability — text never overlaps
during a video blend.

- Outgoing subtitle: fades out BEFORE the video crossfade begins
  (subtitle fade-out completes at least 0.3s before the video blend starts)
- Incoming subtitle: fades in AFTER the video crossfade completes
  (subtitle fade-in starts at least 0.3s after the video blend ends)
- Text fade timings from `transition_defaults.text`:
  - fade_in: 0.7s
  - fade_out: 0.5s

This means the viewer always sees either:
1. Pure video blend (no text) — during the crossfade overlap window, OR
2. Clean text on a stable frame — before the blend starts or after it ends

**Video-to-video transition:**
- Crossfade overlap: the two clips blend during the transition
- Both clips play during the overlap (1.0s crossfade)

**Video-to-image transition:**
- Video fades out as image fades in
- Image begins Ken Burns motion only after transition completes

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
