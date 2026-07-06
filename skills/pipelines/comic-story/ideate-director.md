# Ideate Director — Comic-Story Pipeline

## When To Use

You are the **Ideate Director** for the comic-story pipeline. Your job is to transform the user's input (a text snippet, joke, emotion, scene description, or video URL) into a **chosen story seed** that becomes the foundation for everything downstream.

The ideate stage now has **two rounds**:

1. **Pitch Round** — Generate 5–8 one-sentence story ideas. The user picks one. Fast and lightweight.
2. **Seed Round** — Develop the chosen pitch into a full `story_seed` with 5-beat structure, character archetypes, and style suggestions.

## Reference Inputs

- `tools/writing/story_factory.py` — StoryFactory tool (the primary generation engine)
- `skills/meta/video-reference-analyst.md` — Protocol for video input analysis (if video URL provided)
- `skills/creative/personal-ip.md` — IP branding context (to inform seed character design)

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Tool | `story_factory` | Story seed generation (pitch, from_text, from_video, emotion_matrix, batch modes) |
| Tool | `video_analyzer`, `transcript_fetcher`, `video_downloader` | Video input processing (if video URL) |
| Schema | `story_seed.schema.json` | Output validation |

## Process

### Round 1: Pitch Round (轻量级头脑风暴)

**Goal:** Present the user with 5–8 **one-sentence story ideas** (loglines only). No 5-beat structure, no character archetypes — just the core hook in one sentence.

#### 1a. Determine Input Mode

Classify the user's input:

| Input | Mode | Tool path |
|-------|------|-----------|
| Text, joke, emotion, scene description | `pitch` | StoryFactory pitch mode with text_content |
| Video URL | `from_video` → then `pitch` | Path A transcript → concept → pitch |
| Emotion keywords | `pitch` | StoryFactory pitch mode with emotion |
| No specific input ("给我一些灵感") | `pitch` | StoryFactory pitch mode (random seeds) |

#### 1b. Generate Pitches

Call `story_factory` with `mode: "pitch"`:
- For text input: pass `text_content` — the what-if engine generates 5+ diverse angles
- For video input: first run Path A transcript extraction, then feed the core concept to pitch mode
- For emotion/scene: pass `emotion` and/or `scene` for targeted inspiration
- Always request at least 5 pitches (`count: 5` minimum)

**Each pitch is a dict with:**
```json
{
  "logline": "一句完整的话描述这个故事——起承转合都在这一句里",
  "emotion": "好笑 | 感动 | 温暖 | 心酸 | 惊讶 | 紧张 | 愤怒 | 治愈",
  "pattern_hint": "故事类型提示（身份反转 / 误会连环 / 日常英雄 等）",
  "twist_type": "视角翻转 | 类型转换 | 时间跳跃 | 代价升级 | 反转倒置",
  "style_hint": "warm_illustration | clean_comic | cinematic_drama | watercolor_nostalgia | ink_dramatic",
  "seedream_keywords": ["画风关键词数组"]
}
```

#### 1c. Present Pitches to User

Display ALL pitches clearly. For each pitch, show:

```
🎬 第 N 个创意
   一句话：{logline}
   情绪：{emotion}  |  类型：{pattern_hint}  |  推荐画风：{style_hint}
```

**Presentation rules:**
- Show every pitch as a **single sentence** — the user should be able to read and compare all of them in under 30 seconds
- Number them (1–N) so the user can pick by number
- Include the emotion + pattern hint as metadata tags, not as narrative
- After the list, ask: **"哪个最有感觉？告诉我编号，我把这个创意扩展成完整故事。"**

#### 1d. Wait for User Selection

The user picks one pitch (by number or by describing what they liked). Record the chosen pitch.

**If the user doesn't like any pitch:**
- Ask: "想要换个方向吗？给我一个关键词或情绪，我重新生成一批。"
- Re-run pitch mode with the new guidance
- Max 2 rounds of re-pitching before moving forward with the best available

### Round 2: Seed Round (完整故事种子)

**Only run after the user has selected a pitch in Round 1.**

#### 2a. Video Input Mode — Dual-Path Parallel

When the original user input includes a video URL, and this wasn't already done in Round 1, execute **two paths simultaneously**:

**Path A — Language Content** (produces the story seed):
1. Try Tier 1: `transcript_fetcher` (YouTube subtitles, fastest)
2. Fallback Tier 2: `video_analyzer` with transcript_only
3. Fallback Tier 3: `video_downloader` + Whisper (slowest but universal)
4. Feed transcript text → `StoryFactory._gen_from_video()` → story seeds

**Path B — Visual Style** (feeds style-pick stage):
1. Run `video_analyzer` with analysis_depth "standard"
2. Agent visual analysis of key frames:
   - Content summary
   - Color palette (primary, secondary, background)
   - Composition (centered, rule-of-thirds, symmetry)
   - Transition patterns (hard cut, dissolve, slide)
   - Text overlay style (position, font, animation)
3. Produce 5-dimension structured output (MANDATORY):
   - **Subject** — what is the main visual subject
   - **Subject Motion** — type of subject movement
   - **Scene** — scene composition (with overlay separation)
   - **Spatial Framing** — shot size and angle
   - **Camera** — camera movement (fixed/pan/push/pull/follow)
4. Store result in `EP_STATE.reference_video_analysis`

The two paths are **complementary, not mutually exclusive**:
- Path A transcript → StoryFactory → story seeds (primary output)
- Path B visual analysis → EP_STATE.reference_video_analysis → style-pick reads for style suggestions

#### 2b. Generate Full Story Seed

Feed the **chosen pitch's logline** as `text_content` to StoryFactory's `from_text` mode. This produces a complete `story_seed` with:

- **hook**: Opening line that grabs attention
- **beats**: Complete 5-beat structure (HOOK → BUILD → CONFRONT → REVEAL → RESOLVE), each with timing, visual_suggestion, text_overlay, and camera_hint
- **emotion_arc**: starts, peaks_at, ends
- **character_archetypes**: At least 1 character with `visual_notes` for image generation
- **suggested_style**: With `seedream_keywords` array (pre-filled from the pitch's `style_hint`)

#### 2c. Present the Full Seed

Display the developed seed to the user:
- Title and hook
- Logline (the one-sentence summary they chose)
- Emotional arc flow
- Character lineup with visual descriptions
- Brief panel-by-panel overview (how the 5 beats map to images)
- Suggested art style

### 3. Quality Gate (G1)

- [ ] At least 5 pitches were presented in Round 1
- [ ] User has explicitly selected one pitch
- [ ] hook is non-empty and attention-grabbing
- [ ] beats has exactly 5 beats with timing (minItems:5, maxItems:5)
- [ ] emotion_arc contains starts, peaks_at, ends
- [ ] character_archetypes has at least 1 entry with visual_notes
- [ ] suggested_style includes seedream_keywords
- [ ] (Video mode) EP_STATE.reference_video_analysis is populated
- [ ] Chosen pitch is recorded in the story_seed metadata

## Common Pitfalls

- **Skipping the pitch round**: Always present one-sentence ideas first. Full seeds are too heavy for the initial creative moment. The user needs to pick a direction before you invest in structure.
- **Generating fewer than 5 pitches**: The user needs choice. 5 is the minimum. 7–8 is better.
- **Missing visual_notes**: Without visual_notes on characters, the preview stage cannot generate consistent character anchors.
- **Ignoring video visual analysis**: Path B feeds style-pick. Skipping it means style-pick starts from scratch instead of having grounded suggestions.
- **Over-complicated stories**: Comic shorts work best with simple, relatable stories. One clear twist, one emotional beat.
- **Wrong pitch → seed mapping**: The chosen pitch's `style_hint` should pre-fill the `suggested_style` in the seed. Don't override it arbitrarily.
