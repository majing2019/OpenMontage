# Storytelling & Narrative Structure for Explainer Videos

> Sources: YouTube Creator Academy, Derek Muller PhD thesis (U. Sydney 2008), Kurzgesagt production
> methodology (Philipp Dettmer), 3Blue1Brown (Grant Sanderson), Richard Mayer "Multimedia Learning"
> (Cambridge UP, 2001/2020)

## The Explainer Arc Template

For a **3-minute explainer video** (scale proportionally for other lengths):

```
[0:00 - 0:08]  HOOK
               Pattern interrupt or counterintuitive claim. 1-2 sentences max.
               Visual: striking image or animation that creates curiosity.

[0:08 - 0:30]  TENSION / INFORMATION GAP
               "Here's what most people think... but that's not quite right."
               Establish stakes: why should I care?
               Visual: show the misconception or the puzzle.

[0:30 - 0:50]  CONCEPT 1 (Foundation)
               Simplest building block needed. ONE idea, ONE visual.
               End with a "but" or "therefore" transition.

[0:50 - 1:15]  CONCEPT 2 (Complication)
               Build on Concept 1. Introduce the wrinkle.
               Visual: transform/evolve the previous visual.

[1:15 - 1:20]  PALETTE CLEANSER
               Brief pause, visual gag, or "let that sink in" moment.
               Gives working memory a beat to consolidate.

[1:20 - 1:50]  CONCEPT 3 (Key Insight)
               The "aha" moment. Core of the video.
               1-3 seconds of deliberate silence after the reveal.
               Visual: the most polished animation in the video.

[1:50 - 2:20]  PROOF / EXAMPLE
               Concrete demonstration: "Watch what happens when..."
               Visual: show the insight working in a specific case.

[2:20 - 2:45]  IMPLICATIONS / "SO WHAT?"
               Connect back to the real world. "This means that..."
               Scale from specific back to general.

[2:45 - 3:00]  REFRAME + CLOSE
               Callback to the hook. Restate the core insight in one sentence.
               Optional: open a new curiosity gap.
```

## Scaling by Duration

| Length | Concepts | Hook | Tension | Core | Proof | Close |
|--------|----------|------|---------|------|-------|-------|
| 1 min | 1-2 | 5s | 10s | 30s | 10s | 5s |
| 2 min | 2-3 | 8s | 15s | 60s | 25s | 12s |
| 3 min | 3-5 | 8s | 22s | 100s | 30s | 15s |
| 5 min | 5-8 | 10s | 30s | 180s | 50s | 20s |

## Anti-Subjective Rule

> Hooks, beats, and section descriptions in OpenMontage scripts must describe the **visual cause** of the emotion, not the emotion itself. The CMU/Harvard CHAI study showed that subjective phrasing varies wildly across annotators and across model interpretations — so it does not constrain pixels and it doesn't reliably guide downstream generation tools.
>
> | Avoid | Use instead |
> |---|---|
> | "epic reveal" | "wide aerial pull-back; subject silhouetted against rising sun" |
> | "inspiring moment" | "low angle on the subject's face; light catches the edge of a tear" |
> | "moody atmosphere" | "low-key key light, lifted shadows by 2 stops, fog volumetrics" |
> | "powerful music swell" | "music drops out at 0:42, holds 1.5s of silence, returns with low taiko at half tempo" |
>
> The rule applies to script narration AND to the metadata fields scene-director consumes. For the universal vocabulary that names these visual primitives, see `skills/creative/video-gen-prompting.md`.

## Subject Transitions in the Script

When a script beat introduces a new subject, kills one off, or hands focus from one subject to another, **name the transition explicitly** so the scene-director doesn't have to infer it. The CMU/Harvard taxonomy uses four labels:

| Label | What it means |
|---|---|
| **revealing** | A new subject enters frame or is uncovered (door opens, camera pans to find them, fog clears). |
| **disappearing** | An existing subject leaves frame or is removed (walks out, fades, eclipsed). |
| **switching** | Focus jumps from subject A to subject B (cut, rack focus, camera whip). |
| **complex-alternating** | Multiple subjects trade focus repeatedly within a beat (debate cross-cutting, ensemble action). |

Add 1-2 sentences in the beat describing the mechanism (cut, pan, reveal-by-light, etc.). This propagates into the scene_plan as a transition primitive.

## Hook Types

| Type | Pattern | Best For |
|------|---------|----------|
| **Contrarian** | "Everything you've been told about X is wrong." | Veritasium-style science/myth-busting |
| **Outcome** | "By the end of this video, you'll understand X." | 3Blue1Brown-style math/concept |
| **Mystery** | "In 1987, something impossible happened..." | Kurzgesagt-style story-driven |
| **Stakes** | "This one mistake costs people X every year." | Practical/how-to content |

## The 30-Second Rule

YouTube data shows **50% of viewer drop-off happens in the first 30 seconds**. The hook + tension
setup MUST be complete by second 30. Retention curves that survive the 30-second cliff typically
retain 40-60% through the full video.

## The "But-Therefore" Method

Never connect sections with "and then." Always use **"but"** or **"therefore."**

**Bad:** "Atoms have electrons, AND THEN those electrons have energy levels, AND THEN..."

**Good:** "Atoms have electrons, BUT they don't behave like tiny planets, THEREFORE we need a
completely new model..."

Applied structure:
```
SETUP:     Here's what you think you know about X.
BUT:       Here's why that's wrong / incomplete / surprising.
THEREFORE: We need to understand Y (the real mechanism).
BUT:       Y creates a new puzzle...
THEREFORE: The actual answer is Z.
THEREFORE: This changes how you should think about X.
```

## Misconception-First Approach (Research-Backed)

Derek Muller's PhD research (University of Sydney, 2008) showed that **videos presenting common
misconceptions FIRST, then refuting them, produce significantly higher learning gains** than videos
that simply present correct information. Viewers who watched "misconception-first" videos scored
higher on post-tests and reported higher engagement.

Apply this: always consider opening with what the audience *thinks* is true before revealing what
*actually* is.

## Guided Discovery (3Blue1Brown Method)

Don't explain the answer. **Reconstruct the reasoning path** so the viewer feels they discovered it.

1. **The Question** — Pose a specific, concrete question
2. **The Naive Attempt** — Show the obvious approach; let it partially work, then break
3. **The Key Insight** — Introduce ONE new idea. Pause visually for 2-3 seconds of silence.
4. **The Build** — Apply the insight step by step. Each step feels inevitable.
5. **The Generalization** — "Notice this pattern works beyond our specific example..."

**Progressive Revelation:** Never show the full picture at once. Build visuals layer by layer.
Each layer arrives exactly when the narration references it.

## Camera Intent Per Beat

When writing a beat, attach one line of camera intent so the scene-director doesn't have to invent it from a blank slate. Use the universal vocabulary in `skills/creative/video-gen-prompting.md` (Subject / Subject Motion / Scene / Spatial Framing / Camera). One line is enough — the scene-director will expand it.

Example beat:

```
[0:30] Concept 1 — atoms aren't tiny planets
Narration: "We grew up imagining electrons as tiny planets orbiting the nucleus..."
Camera intent: medium shot of stylized atom; slow rotation; deep focus.
```

The camera-intent line is consumed verbatim by the scene-director's 5-aspect spec — keep it concrete, no mood adjectives.

## Pacing Rules

| Rule | Value | Source |
|------|-------|--------|
| Narration speed | 150-160 wpm | Kurzgesagt standard (conversational is 170-190) |
| New visual element | Every 3-5 seconds | Kurzgesagt production rules |
| Concept density | Max 1 new concept per 30-45 seconds | Mayer's Segmenting Principle |
| Pattern interrupt | Every 45-90 seconds | YouTube retention data |
| Deliberate silence | 1-3 seconds after key insights | 3Blue1Brown technique |
| Palette cleanser | Every 45-60 seconds | Kurzgesagt production rules |

## Mayer's Multimedia Learning Principles (Applied)

These are the most relevant research-backed rules from cognitive science:

1. **Segmenting** — Max 1 new concept per 30-45 seconds. A 3-min video = 4-6 concept segments.
2. **Signaling** — Use verbal signposts every 30-45 seconds ("Here's where it gets interesting").
3. **Temporal Contiguity** — Narration and visuals must be simultaneous. Learning drops ~30% when offset even by a few seconds.
4. **Coherence** — Remove interesting-but-irrelevant content. "Seductive details" reduce learning by 20-30% on transfer tests.
5. **Modality** — Use narration (audio) + visuals (animation), NOT on-screen text + visuals. Spoken words + pictures outperform written words + pictures.

## Applying to OpenMontage

When writing a **script artifact** for the animated-explainer pipeline:

1. Choose a hook type from the table above based on the topic
2. Structure sections using the Explainer Arc template
3. Apply "but-therefore" connectors between sections
4. Consider the misconception-first approach for science/technical topics
5. Set `narration_wpm: 155` in the script to calculate accurate timing
6. Plan visual changes every 3-5 seconds in the scene_plan
7. Mark "silence" beats in the script for key insights
8. Validate: total concepts should not exceed the scaling table above

---

## Ending Techniques

### Snyder Opening/Closing Image Contrast (Save the Cat)

> Source: Blake Snyder "Save the Cat!" (2005)

The closing image must **visually prove** that the protagonist has changed. It should mirror the opening image but show a transformation.

| Opening Image | Closing Image | What It Proves |
|-------------|--------------|---------------|
| Lonely person eating alone | Same restaurant, but someone is with them | Connection found |
| Cluttered desk, stressed | Same desk, but clean — one item removed = change started | Change is real |
| Character running away | Character walking toward something | Direction reversed |

**Application**: When writing a story seed, include both `opening_image_hint` and `closing_image_hint` fields. The closing image should directly contrast the opening.

### 4 Resolution Types

| Type | When to Use | Example |
|------|-------------|---------|
| **Positive** | Hero achieves goal through growth | Problem solved, lesson learned |
| **Negative** | Hero fails but grows | Didn't succeed, but became wiser |
| **Ironic** | Surface success masks hidden cost, or vice versa | Got what was wanted but lost something more valuable |
| **Open-ended** | Leave the audience thinking | Life continues, no definitive answer — most realistic |

**Rule**: Never use the ending to preach. Let the audience draw the conclusion from the contrast.

### Page Turn Suspense (Manga Technique)

> Source: 《漫画密码》, 《你与大师一步之遥：漫画脚本篇》

The **last panel of a right page** is the prime suspense location. The **first panel of a left page** is the prime reveal/impact location.

**Formula**: Present a question + new悬念 = page ending → reader MUST turn → reveal on next page.

**Application in OpenMontage**: Include a `page_turn_hook` field in story seeds — one sentence describing what makes the reader/viewer want to continue to the next beat.

### Elixir Return (Hero's Journey)

> Source: Vogler "The Writer's Journey" (1998)

The hero must bring back a **gift for the community** — not just for themselves. Knowledge, experience, love, or peace. The story has universal meaning only when the hero's growth benefits others.

---

## Conflict Design Framework

### McKee's Value Change Per Scene

> Source: Robert McKee "Story" (1997)

**Every scene must produce a value change** — positive to negative, or negative to positive. If a scene ends in the same state it began, delete it.

| Scene Start | Scene End | Value Change |
|-------------|-----------|-------------|
| Hope → | Despair | ✅ (negative change) |
| Ignorance → | Knowledge | ✅ (positive change) |
| Status quo → | Status quo | ❌ (no change — delete or revise) |

**Application**: When writing beats, explicitly note the emotional polarity at the start and end. If unchanged, the beat needs a turning point.

### Gap Theory (Story Energy Source)

> Source: McKee "Story", Storr "The Science of Storytelling"

**Story energy = gap between expectation and reality.**

1. Character takes action expecting result X
2. Reality delivers result Y (different from X)
3. This gap forces the character into a more extreme choice
4. The gap between expectation and reality **is** what keeps the audience engaged

**Application**: Design each beat so that the character's expectation is violated. The gap doesn't need to be dramatic — even small gaps ("I thought they'd say yes, they said no") create energy.

### Egri's Rising Conflict

> Source: Lajos Egri "The Art of Dramatic Writing" (1942)

Conflict must **escalate gradually**, with each step logically caused by the previous one.

| Type | Description | Avoid? |
|------|-------------|--------|
| **Static** | Equal opposing forces, no progress | ❌ Always avoid |
| **Jumping** | Sudden escalation without causality | ❌ Always avoid |
| **Rising** | Gradual escalation, each step from previous | ✅ Ideal |

**Three-Level Conflict Depth** (from 叶茂中《冲突》):

| Level | Chinese | What It Is | Examples |
|-------|---------|-----------|----------|
| Surface | 表层 | Functional/practical problem | How to do X, schedule conflict |
| Middle | 中层 | Emotional/relational opposition | Misunderstanding, hurt feelings |
| Deep | 深层 | Value/identity contradiction | Freedom vs security, self vs group |

**Best stories use all three levels** — surface conflict hooks attention, middle conflict creates empathy, deep conflict gives lasting impact.

### Information Gap Theory (Storr)

> Source: Will Storr "The Science of Storytelling" (2019)

**Curiosity = brain detecting information gaps.** It works like hunger — an unsatisfied gap demands to be filled.

**How to use:**
1. Open a gap that is **too large to ignore** but **small enough to understand**
2. Feed information **incrementally** — never resolve all gaps at once
3. Each resolved gap should **open a new gap** to maintain momentum
4. The final gap is the core dramatic question — resolved at the climax

**The Change Detection Opening**: Begin with **change/anomaly**, not normal state. "Something's wrong" triggers the brain's change-detection system, which demands attention.

---

## Therefore/But Connection Test

> Source: William M. Akers "Your Screenplay Sucks!" (2008)

**Scene connections must be "therefore" or "but" — never "and then."**

| Connection | Meaning | Effect |
|------------|---------|--------|
| Therefore | Causal consequence | Narrative drive forward |
| But | Contradiction / surprise | Narrative drive via tension |
| And then | No connection | Narrative death — delete or revise |

**Quick test**: Replace the transition between any two beats with "and then." If the sentence still makes sense, the beats aren't connected strongly enough. Fix by finding the causal link or contrast between them.

**Extended: McKee's scene-level test**: Replace "and then" with "because" or "but" — if neither works, the scene sequence has a structural problem.

---

## Character Depth System

> Sources: Egri "The Art of Dramatic Writing", Storr "The Science of Storytelling", Truby "The Anatomy of Story"

### 3D Character Model (Egri)

Every character should have three dimensions:

| Dimension | Chinese | Questions | Purpose |
|-----------|---------|----------|---------|
| Physiological | 生理 | Age, body, appearance, health | Visual design, physical behavior |
| Sociological | 社会 | Class, job, education, family, religion | Social context, relationships |
| Psychological | 心理 | Temperament, beliefs, complexes, values | Motivation, inner conflict |

### Sacred Flaw (Storr)

Every compelling character has a **deeply flawed but sacredly held worldview**:

```
Trauma → False conclusion → Rigid belief → Behavior patterns
```

The character's **growth** = recognizing and revising this belief. The story proves one lifestyle superior through consequences.

### Desire vs. Need (Truby)

| Component | What It Is | Example |
|-----------|-----------|---------|
| **Desire (Want)** | External, conscious goal | "I want to get promoted" |
| **Need** | Internal growth requirement | "I need to learn to collaborate" |
| **Opponent as Mirror** | Represents what hero refuses to see | The team player who challenges the lone wolf |

The story's ending: the character achieves (or fails to achieve) the **Want**, but the audience judges success by whether they grew toward the **Need**.

### Character = Action Under Pressure (McKee)

Characters are revealed through **choices under pressure**, not through stated traits or backstory dumps. Greater pressure → deeper revelation → more authentic character.

**Application in OpenMontage**: The `story_factory` CHARACTER_ARCHETYPES now include all these fields (`sacred_flaw`, `desire_want`, `desire_need`, `opponent_mirror`, `action_under_pressure`). Use them in the story generation pipeline.
