# Script Director - Avatar Spokesperson Pipeline

## When To Use

Turn the approved brief into scene-safe spoken copy for an avatar presenter. The quality bar is not literary flourish. It is spoken clarity, believable pacing, and one clean point per scene.

## Reference Inputs

- `docs/avatar-spokesperson-best-practices.md`
- `skills/creative/storytelling.md`

## Process

### 1. Write For Speech, Not For Slides

Prefer:

- short sentences,
- direct verbs,
- one idea per beat,
- explicit transitions,
- conversational emphasis.

If the copy sounds like a brochure when read aloud, rewrite it.

### 2. Break Into Scene-Safe Chunks

Avatar scenes are easier to manage when each section is compact. A useful starting point is:

- hook,
- value statement,
- proof or feature beat,
- CTA.

### 3. Keep On-Screen Text Light

The presenter is already carrying attention. Use on-screen text only for:

- product names,
- short proof points,
- CTA copy,
- legal or compliance text that must appear.

### 4. Use Metadata For Delivery Notes

Recommended metadata keys:

- `scene_copy_map`
- `cta_language`
- `pronunciation_notes`
- `supplied_script_source`
- `legal_text_requirements`

### 5. Quality Gate

- the copy sounds spoken,
- scene lengths are realistic,
- CTA placement is clear,
- text overlays are restrained.

### Mid-Production Fact Verification

If you encounter uncertainty during script writing:
- Use `web_search` to verify factual claims before committing them to the script
- Use `web_search` to find reference images for visual accuracy
- Log verification in the decision log: `category="visual_accuracy_check"`

Every factual claim in the script should be traceable to the `research_brief`.
If you make a claim that isn't in the research, do additional research and
add the source. Do not invent statistics, dates, or attributions.

## Common Pitfalls

- Overstuffing one scene because the script reads well on paper.
- Duplicating the same sentence in speech and large text overlays.
- Writing humor or improvisational beats the avatar path cannot sell.

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

