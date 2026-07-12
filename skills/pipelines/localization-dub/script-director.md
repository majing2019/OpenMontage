# Script Director - Localization Dub Pipeline

## When To Use

Turn the approved localization brief into a transcript-backed, reviewable script package for every target language. This stage should create text truth before any dubbing audio is generated.

## Reference Inputs

- `docs/localization-dubbing-best-practices.md`
- `skills/creative/storytelling.md`

## Process

### 1. Build Source Transcript Truth

Start with the source transcript and fix obvious errors in:

- names,
- terminology,
- speaker allocation,
- numbers,
- CTA phrasing.

### 2. Produce Reviewable Target Copy

For each target language, generate text that can be reviewed before synthesis. Record where terms should remain unchanged.

### 3. Preserve Structure Where Practical

Keep section timing and sequence aligned to the source unless the translation clearly needs a different pacing strategy.

### 4. Use Metadata For Localization Control

Recommended metadata keys:

- `source_transcript_status`
- `target_language_sections`
- `glossary_terms`
- `protected_terms`
- `pronunciation_notes`
- `review_status_by_language`

### 5. Quality Gate

- the source transcript is strong enough to trust,
- target-language copy exists for every planned deliverable,
- glossary terms are preserved,
- the script package can be reviewed before audio generation.

### Mid-Production Fact Verification

If you encounter uncertainty during script writing:
- Use `web_search` to verify factual claims before committing them to the script
- Use `web_search` to find reference images for visual accuracy
- Log verification in the decision log: `category="visual_accuracy_check"`

Every factual claim in the script should be traceable to the `research_brief`.
If you make a claim that isn't in the research, do additional research and
add the source. Do not invent statistics, dates, or attributions.

## Common Pitfalls

- Generating audio from an unreviewed transcript.
- Letting product names drift across languages.
- Treating translation text as final timing without acknowledging length drift.

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

