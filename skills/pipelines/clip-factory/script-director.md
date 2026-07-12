# Script Director - Clip Factory Pipeline

## When To Use

This stage converts the long-form source into a ranked candidate list and then into the final clip selections. You are mining for standout moments, not summarizing the entire source.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Prior artifact | `state.artifacts["idea"]["brief"]` | Batch goals and platform targets |
| Tools | `transcriber`, `scene_detect` | Transcript-first selection and visual checks |

## Process

### 1. Transcribe The Full Source

Use `transcriber` first. The transcript is the search surface for hooks, not an afterthought.

Use `scene_detect` only to sanity-check visual boundaries, speaker changes, or slide changes near promising moments.

### 2. Score Candidate Moments

Use the brief's ranking criteria and evaluate each moment on:

- `hook`
- `coherence`
- `value`
- `energy`
- `platform_fit`

This mirrors the way modern clipping products talk about virality and clip quality, while keeping the judgment transparent.

### 3. Apply The Standalone Test

Every approved clip must make sense to a cold viewer.

Reject or widen clips that contain:

- unresolved pronouns,
- references to earlier context,
- long lead-ins before the point lands,
- endings that stop before the payoff.

### 4. Select The Final Batch

Pick the smallest set that best satisfies the batch goal.

Maintain diversity across:

- source sections,
- speakers,
- clip families,
- energy levels.

### 5. Use Metadata For Ranking Truth

The script schema is small, so store the richer batch analysis in `script.metadata`.

Recommended metadata keys:

- `candidate_clips`
- `selected_clip_ids`
- `ranking_model`
- `rejected_candidates`
- `source_coverage_map`
- `platform_assignments`

Each candidate should record:

- source in/out,
- hook text,
- reason selected or rejected,
- scoring dimensions,
- likely crop viability.

### 6. Quality Gate

- the top-ranked clips are genuinely the strongest, not just the earliest found,
- every selected clip passes the standalone test,
- the set covers the source deliberately instead of clustering in one section,
- low-quality candidates are rejected honestly.

### Mid-Production Fact Verification

If you encounter uncertainty during script writing:
- Use `web_search` to verify factual claims before committing them to the script
- Use `web_search` to find reference images for visual accuracy
- Log verification in the decision log: `category="visual_accuracy_check"`

Every factual claim in the script should be traceable to the `research_brief`.
If you make a claim that isn't in the research, do additional research and
add the source. Do not invent statistics, dates, or attributions.

## Common Pitfalls

- Trusting first-pass candidate timestamps without transcript-level review.
- Selecting too many calm, same-energy clips.
- Preserving chronological order instead of ranking by quality.
- Treating transcript quality issues as minor when they affect selection accuracy.

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

