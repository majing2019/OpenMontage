# Script Director - Screen Demo Pipeline

## When To Use

You are turning the inspected recording into a timestamped procedural script. Unlike explainer work, you are not inventing the flow. You are synchronizing language to actions the viewer will literally see.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Prior artifact | `state.artifacts["idea"]["brief"]` | Brief with workflow, critical moments, and source notes |
| Tools | `transcriber`, `frame_sampler`, `audio_enhance` | Audio/transcript inspection and spot checks |

## Process

### 1. Decide The Script Mode

Use the brief metadata to choose one of three modes:

| Voiceover Status | Strategy |
|-----------------|----------|
| `voiced` | Transcribe, tighten, and preserve the speaker's phrasing where possible |
| `silent` | Write text-led or optional TTS-ready narration around the actions |
| `partial` | Transcribe the existing speech and bridge only where necessary |

If the recording is silent and TTS was not available in preflight, do not pretend there will be narration later. Write the script so the video can still work with captions, hook cards, and step labels.

### 2. Build The Action Map

The action map is the real backbone of this stage. Use `frame_sampler` and `transcriber` together to log:

- exact task boundaries,
- clicks worth highlighting,
- typed input worth slowing down,
- waits worth speeding up or cutting,
- the result moment to preserve in real time.

Store detailed action information in `script.metadata.interaction_map`. Keep `sections` clean and schema-valid.

Useful `interaction_map` fields:

- `timestamp_seconds`
- `action_type`
- `target`
- `importance`
- `suggested_treatment` (`realtime`, `speed_up`, `cut`, `highlight`, `zoom`)

### 3. Write Sections By Step

Each `script.sections[]` entry should correspond to a real user step, not a thematic paragraph.

Good section labels:

- `Open the settings panel`
- `Paste the API token`
- `Run the build`
- `Verify the live result`

Every section should do three things:

- say what is happening,
- say why it matters,
- leave clear cues for highlights, zooms, or speed changes.

### 4. Keep The Narration Procedural

Use the research-backed rules:

- narrate intent and effect, not obvious cursor motion,
- keep wording short and direct,
- avoid jargon unless the target audience clearly expects it,
- keep the action on screen synchronized with the wording,
- preserve the speaker's natural voice if the source already has narration.

### 5. Mark Pacing Decisions

Use section-level notes and `metadata.speed_plan` to call out:

| Speed Factor | When to Use | Example |
|-------------|-------------|---------|
| `0.75-1.0x` | Important click or result | Small control, key validation moment |
| `1.5-2.0x` | routine typing or navigation | filling obvious fields |
| `3.0-6.0x` | installs, builds, loading | dependency install, compile |
| `cut` | no learning value | long idle wait |

Do not put critical proof moments inside sped-up sections.

### 6. Use Metadata For Screen-Specific Detail

Recommended `script.metadata` fields:

- `interaction_map`
- `speed_plan`
- `chapter_candidates`
- `pronunciation_guides`
- `callout_candidates`
- `sections_needing_zoom`

### 7. Quality Gate

| Criterion | Question |
|-----------|----------|
| **Action coverage** | Is every critical moment from the brief annotated with a timestamp? |
| **Narration sync** | Does each narration segment align with what's happening on screen? |
| **Speed marking** | Are dead-time segments marked for acceleration or removal? |
| **Enhancement density** | Are highlights reserved for true attention shifts rather than every click? |
| **Technical accuracy** | Are all software names, commands, and UI elements named correctly? |
| **Word economy** | Is narration concise and procedural? |

### Mid-Production Fact Verification

If you encounter uncertainty during script writing:
- Use `web_search` to verify factual claims before committing them to the script
- Use `web_search` to find reference images for visual accuracy
- Log verification in the decision log: `category="visual_accuracy_check"`

Every factual claim in the script should be traceable to the `research_brief`.
If you make a claim that isn't in the research, do additional research and
add the source. Do not invent statistics, dates, or attributions.

## Common Pitfalls

- Narrating the cursor instead of the outcome.
- Letting spoken timing drift away from the visual action.
- Keeping builds and loading screens in real time.
- Writing a silent-recording script that secretly depends on unavailable TTS.

## Universal Quality Enhancements

### Therefore/But Connection Test

> Source: William Akers "Your Screenplay Sucks!" (2008)

Every beat/scene transition must connect via **"therefore"** (causal) or **"but"** (contradiction) — never "and then."

**Quick test**: Between any two consecutive beats, mentally insert "therefore" or "but." If neither word fits naturally, the beats aren't connected strongly enough. Revise one beat so a causal or contrasting link emerges.

| Connection | Meaning | Effect on Audience |
|------------|---------|-------------------|
| Therefore | Beat B is a consequence of Beat A | Forward narrative drive |
| But | Beat B contradicts Beat A's expectation | Tension, surprise, engagement |
| And then | No logical connection | Confusion, disengagement |

### Information Gap Per Beat

> Source: Storr "The Science of Storytelling" (2019), Heath brothers "Made to Stick" (2007)

Each beat should either **open a new information gap** or **partially close an existing gap** — but never fully close all gaps until the climax.

- **Beat opening a gap**: Pose a question, hint at something unseen, create an expectation
- **Beat partially closing a gap**: Reveal some information but leave a new question
- **Climax beat**: Close the core dramatic question — this is the only moment all gaps resolve

If a beat neither opens nor closes a gap, it's likely filler. Either add a reveal, a reversal, or cut it.

### 30-Second Emotional Density Rule (60s+ videos)

> Source: 葛飞《爆款短剧与微电影创作》

For scripts longer than 60 seconds, ensure at least one **emotional stimulation point** (reveal, reversal, tone shift, or new information) occurs every ~30 seconds. If a 30-second window has no emotional change, the audience's attention will wane.

### Scene Value Change (McKee)

> Source: Robert McKee "Story" (1997)

Each beat/scene should begin and end in **different emotional polarity** (positive↔negative). If a beat starts and ends in the same state, it adds nothing to the narrative.

