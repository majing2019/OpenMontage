# Script Director - Character Animation Pipeline

## Goal

Write scripts as performable animation beats, not just narration.

## Process

1. Lock audio architecture:
   - music-only,
   - narrator,
   - character dialogue,
   - narrator plus character sounds/dialogue.
2. Break the story into beats that can be acted with poses.
3. For each beat, state what changes visually:
   - emotion,
   - gaze,
   - body pose,
   - prop interaction,
   - camera,
   - environment.

## Writing Rules

- Prefer short visual beats with readable holds.
- Avoid action that needs many unique hand-drawn poses unless approved.
- Dialogue should be short enough for mouth-shape approximation.
- Silent/music-led scenes need stronger physical acting notes.

## Output Notes

In the `script` artifact metadata, include:

- `audio_architecture`,
- `character_beats`,
- `required_emotions`,
- `required_actions`.

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

