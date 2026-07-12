# Script Director — Talking Head Pipeline

## When to Use

You have a brief and raw talking-head footage. Your job is to transcribe the footage and structure it into a script artifact with timestamped sections.

Unlike the explainer pipeline (which writes a script from scratch), you're extracting and structuring existing speech.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Prior artifacts | `state.artifacts["idea"]["brief"]` | Content context |
| Tools | `transcriber` (WhisperX) | Speech-to-text with timestamps |

## Process

### Step 1: Transcribe

Use the transcriber tool to get word-level timestamps:
- Model: `large-v3` for best quality, `base` for speed
- Enable word-level alignment for precise timing
- Note language detection result

### Step 2: Segment into Sections

Group the transcript into logical sections:
- Detect topic changes by content
- Respect natural pauses (> 1.5s silence = potential section break)
- Each section gets: id, text, start_seconds, end_seconds

### Step 3: Enhance Section Metadata

For each section, add:
- Enhancement cues (where overlays, b-roll, or text cards could go)
- Speaker notes (emphasis, pace changes detected in audio)

### Step 4: Build Script Artifact

Assemble the structured script with:
- Total duration (from transcript)
- All sections with timestamps
- Enhancement cues per section

### Step 5: Self-Evaluate

| Criterion | Question |
|-----------|----------|
| **Transcription accuracy** | Are the words correct? (Spot-check a few sections) |
| **Timestamp accuracy** | Do section boundaries align with actual speech? |
| **Coverage** | Does the script span the full footage duration? |

### Step 6: Submit

Validate the script against the schema and persist via checkpoint.

### Mid-Production Fact Verification

If you encounter uncertainty during script writing:
- Use `web_search` to verify factual claims before committing them to the script
- Use `web_search` to find reference images for visual accuracy
- Log verification in the decision log: `category="visual_accuracy_check"`

Every factual claim in the script should be traceable to the `research_brief`.
If you make a claim that isn't in the research, do additional research and
add the source. Do not invent statistics, dates, or attributions.

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

