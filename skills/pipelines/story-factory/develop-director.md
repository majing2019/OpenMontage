# Develop Director — Story-Factory Pipeline

## When To Use

You are the **Develop Director** for the story-factory pipeline. Your job is to transform a `story_seed` (5-beat structure from the ideate stage) into a rich, polished `story_script` — a complete narrative with character depth, subtext-aware dialogue, layered conflict, and structural quality markers.

This is the **core creative stage** of the pipeline. No tools are called — all work is pure agent-driven narrative craft, applying the creative skills.

You MUST read all required creative skills before starting. They define the rules for character depth, conflict design, dialogue craft, and pacing.

## Reference Inputs

- `skills/creative/storytelling.md` — **MANDATORY**: Conflict design (3-level: surface/middle/deep), character depth (Egri 3D, Storr sacred flaw, Truby desire/need), therefore/but method, ending techniques (Snyder contrast, manga page-turn, 4 resolution types), gap theory, McKee value change per scene
- `skills/creative/short-form.md` — **MANDATORY**: Breathing rhythm (inhale/hold/exhale), 30-second emotional density rule, mobile constraints (15 chars), panel rhythm control, SUCCESs framework
- `skills/creative/comedy-framework.md` — **CONDITIONAL** (read when pattern_category is "comedy"): Comedy formula (Truth + Pain + Distance), comic character formula, comedy techniques (Fish Out of Water, Rule of Three, Callback)
- `skills/creative/advertising-structure.md` — **REFERENCE**: Hook strategies, AIDA model
- `skills/creative/visual-grammar.md` — **REFERENCE**: Shot size emotional meanings (ELS through ECU), McCloud panel transitions, closure utilization
- `tools/writing/_dialogue_engine.py` — **REFERENCE**: 8 subtext rules, 9 character × multi-emotion dialogue templates, therefore/but connection tests, mobile constraints

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `story_seed` | 5-beat seed from ideate stage |
| Schema | `story_script.schema.json` | Output validation |
| Skill | `creative/storytelling.md` | Narrative framework |
| Skill | `creative/short-form.md` | Platform constraints + pacing |

## Process

### 1. Read Creative Skills (MANDATORY)

Before writing anything, read all four mandatory skills:

1. **`storytelling.md`** — Absorb the conflict design framework, character depth system, therefore/but method, ending techniques, and gap theory. These are the core tools for this stage.
2. **`short-form.md`** — Absorb breathing rhythm modes, 30-second emotional density rule, panel rhythm control, and mobile constraints.
3. **`comedy-framework.md`** — If the story's `pattern_category` is "comedy," read this for comedy-specific techniques.
4. **`advertising-structure.md`** — Reference for hook strategy alignment.

### 2. Absorb the Story Seed

Extract key information from the `story_seed` artifact:

- **Story identity**: title, hook, logline, pattern, pattern_category
- **Emotion arc**: starts → peaks_at → ends
- **Beats**: 5-beat structure with timing, descriptions, visual_suggestions
- **Characters**: archetypes with role, description, emotional_state, visual_notes
- **Twist**: The reveal/turning point
- **Ending**: Description, type, closing_image_hint, page_turn_hook
- **Platform**: target_platform, target_duration_seconds

### 3. Character Expansion

For each character in the story_seed `character_archetypes`, build a complete depth profile:

#### 3a. Map to Pre-built Archetypes

The `story_factory.py` CHARACTER_ARCHETYPES pool already contains full depth profiles for 12 common roles. If the character's `role` matches an entry, inherit its pre-built depth:

```
角色 → 预构建数据
妈妈 → physiological, sociological, psychological, sacred_flaw, trauma_origin, desire_want, desire_need, opponent_mirror, action_under_pressure
爸爸 → (同上所有字段)
打工人 → (同上)
...
```

If no match exists, synthesize dimensions from the archetype's `description` and `emotional_state`.

#### 3b. Fill All Required Fields

For each character, ensure:

| Field | Source | Quality Check |
|-------|--------|--------------|
| `physiological` | Egri dimension 1 | Age, body, appearance, health — specific enough to visualize |
| `sociological` | Egri dimension 2 | Class, job, education, family — social context |
| `psychological` | Egri dimension 3 | Temperament, beliefs, values — inner world |
| `sacred_flaw` | Storr | Trauma → false conclusion → rigid belief. Must be genuinely flawed, not a virtue in disguise |
| `trauma_origin` | Storr | Root cause of the sacred flaw — a specific past event or pattern |
| `desire_want` | Truby | External, conscious goal — what the character SAYS they want |
| `desire_need` | Truby | Internal growth requirement — what the character ACTUALLY needs to learn. **Must differ from desire_want** |
| `opponent_mirror` | Truby | What the opponent/antagonist reflects about the character's hidden fears |
| `action_under_pressure` | McKee | How this character acts when cornered — the truest revelation of character |

**Critical rule**: `desire_want` ≠ `desire_need`. If they're the same, the character has no arc — the story proves nothing. Fix this.

### 4. Scene Expansion

For each of the 5 beats from the story_seed, write a full scene:

#### 4a. Convert Beat to Scene

| Beat Field | Scene Field | Transformation |
|-----------|-------------|---------------|
| `beat_number` | `scene_number` | Direct mapping |
| `name` | `beat_name` | Direct mapping |
| `start_second / target_duration` | `start_pct` | Convert absolute time to proportion |
| `end_second / target_duration` | `end_pct` | Convert absolute time to proportion |
| `description` | `scene_description` | **Expand** from 1 line to 1-2 paragraphs of prose |
| `visual_suggestion` | `setting` + `shot_hint` | Extract location from visual suggestion |

#### 4b. Write Scene Description (1-2 Paragraphs)

Each scene description should:
- **Show, don't tell** — describe what the audience SEES and HEARS, not what they should feel
- **Name the setting** — where are we? What time of day? What's the atmosphere?
- **Show character action** — what are the characters DOING? Actions reveal character per McKee
- **Include sensory details** — one or two specific visual/auditory details that ground the scene
- **End with a value change** — the scene must end in a different emotional state than it began (McKee)

#### 4c. Design Three-Level Conflict

For EACH scene, fill all three conflict levels:

| Level | Question to Answer | Must NOT Be |
|-------|-------------------|-------------|
| **Surface** | What are the characters arguing about or dealing with on the surface? | Abstract or vague |
| **Middle** | What are they actually FEELING? What's the emotional subtext of this conflict? | Same as surface |
| **Deep** | What value or identity question is at stake? (freedom vs security, self vs group, truth vs comfort) | Missing — at least the climax scene MUST have deep conflict |

**Quick test**: Ask "Why does this conflict matter?" three times. If the answer gets deeper each time, the conflict has all three levels. If it stays the same, deepen it.

#### 4d. Assign Emotional Polarity

For every scene:
- `emotional_polarity_start` — the emotional state at the scene's start (e.g., "焦虑", "平静", "愤怒")
- `emotional_polarity_end` — the emotional state at the scene's end — **must differ from start**
- `value_change` — describe the change in McKee's format: "X → Y" (e.g., "希望 → 绝望", "无知 → 认知", "孤立 → 连接")

**Critical rule**: No scene ends in the same state it began. If emotional_polarity_start == emotional_polarity_end, the scene is static — delete it or add a turning point.

#### 4e. Assign Breathing Mode

From short-form.md's breathing rhythm system, assign each scene one mode:

| Mode | Chinese | Pattern | When to Use |
|------|---------|--------|-------------|
| `inhale` | 吸气 | Tension builds, details accumulate, pace quickens | Setup, complication, escalation |
| `hold` | 屏息 | Maximum anticipation, a key revelation, a turning point | The twist/reveal, the emotional peak |
| `exhale` | 呼气 | Release of tension, emotional payoff, resolution | After the climax, the closing scene |

**Rule**: The sequence should form a breath cycle — inhale → hold → exhale. No more than 2 consecutive scenes with the same mode.

#### 4f. Assign Shot Hint

From visual-grammar.md, assign a shot size for the scene's primary composition:

| Shot | Best For |
|------|----------|
| ELS (极端远景) | Establishing a new location, showing scale |
| LS (远景) | Scene establishment, character in environment |
| MS (中景) | Character interaction, dialogue, action |
| CU (特写) | Emotional peaks, key objects, reactions |
| ECU (极端特写) | Critical details, eyes, hands, a single tear |

### 5. Dialogue Writing

For scenes that benefit from character speech, write subtext-aware dialogue.

#### 5a. Apply the 8 Subtext Rules (from McKee / _dialogue_engine.py)

Every dialogue line must apply at least one of these rules:

| # | Rule | Bad Example | Good Example |
|---|------|-------------|-------------|
| 1 | **Don't name emotions** | "我很生气" | "（沉默，把杯子重重放下）" |
| 2 | **Use action instead of emotion words** | "我很想你" | "这是第三次路过你喜欢的面包店了" |
| 3 | **Say the opposite** | "我很难过" | "没事，挺好的" |
| 4 | **Change topic = emotional avoidance** | "我不想谈这个" | "对了，你吃饭了吗？" |
| 5 | **Questions hide judgment** | "你这样做不对" | "你确定要这样？" |
| 6 | **Repetition = emphasis** | "我真的很想你" | "你回来了？……你真的回来了？" |
| 7 | **Silence = most powerful line** | "我不知道该说什么" | "（长久沉默后）……走吧" |
| 8 | **Concrete over abstract** | "我过得很糟糕" | "泡面已经连吃第四天了" |

#### 5b. Reference Dialogue Templates

Consult `_dialogue_engine.py`'s DIALOGUE_TEMPLATES for character-specific inspiration. Each archetype (妈妈, 爸爸, 打工人, 孩子, 老板, 老人, 外卖小哥, 闺蜜/兄弟, 奶奶/外婆) has pre-built dialogue lines for multiple emotions, each with:
- `surface_text` — what the character says aloud
- `subtext` — what they really mean
- `tone` — how they say it
- `delivery_hint` — physical action or expression

**Don't copy-paste templates** — use them as creative springboards. Adapt to your story's specific context.

#### 5c. Enforce Mobile Constraints

From short-form.md and Ge Fei /《爆款短剧创作》:

- **Surface text ≤ 15 Chinese characters** per line (mobile screen width limit)
- **Max 3 dialogue bubbles per scene** (don't overcrowd)
- **Max 25 words per bubble** (English equivalent)
- Set `mobile_optimized: true` if within limits, `false` otherwise

#### 5d. Dialogue Quality Rules

- Every line must have `surface_text` ≠ `subtext_meaning` — if they're the same, there's no subtext
- `subtext_meaning` must describe the ACTUAL meaning, not just restate the surface
- `subtext_rule_applied` must reference one of the 8 rules above
- `delivery_hint` must be a concrete action/expression/pause, not an abstraction

### 6. Therefore/But Chain

For every adjacent pair of scenes, write a connection:

```
Scene N → [therefore / but] → Scene N+1
```

- **therefore** = causal consequence. Scene N CAUSES Scene N+1.
- **but** = contradiction or surprise. Scene N+1 is an unexpected result of Scene N.
- **NEVER "and then"** — this is narrative death. Just listing events in sequence is not storytelling.

For each connection, write a 1-2 sentence `explanation` describing the causal or contrastive logic.

**Quick test**: Replace the connector with "and then." If the sentence still makes sense without feeling flat, the connection is too weak. Fix by finding the causal link or tension between the two scenes.

### 7. Conflict Depth Summary

After all scenes are written, build the `conflict_depth_summary`:

- `has_deep_conflict` — at least one scene must have deep conflict (value/identity question). Usually the climax scene (REVEAL beat).
- `escalation_pattern` — verify conflict escalates per Egri: rising (gradual, each step from previous), not static (equal opposing forces) or jumping (sudden escalation without causality)
- `deepest_scene` — which scene number reaches the deepest conflict level

### 8. Breathing Rhythm Summary

After all breathing modes are assigned, build the `breathing_rhythm_summary`:

- `has_cycle` — the scene sequence should contain at least one full inhale → hold → exhale cycle
- `max_consecutive_same_mode` — count consecutive scenes with the same mode. Should be ≤ 2.

### 9. Output

Produce a schema-valid `story_script` JSON artifact. Also present a preview summary to the user:

```
📖 故事脚本：{title}

👥 角色（{total_characters}人）：
   - {name}（{role}）：{sacred_flaw 摘要} → 需要学会 {desire_need}

🎬 场景序列（{total_scenes}个场景）：
   场景1 [{beat_name}]：{setting} — {value_change}
   场景2 [{beat_name}]：{setting} — {value_change}
   ...

💬 对话亮点：
   - "{最有潜台词的一句对话}" — 实际含义：{subtext}

🔗 因果链：{场景1} → [therefore/but] → {场景2} → ...

🎭 冲突深度：最深在第{deepest_scene}场景（{deep_conflict_summary}）

🌬️ 呼吸节奏：{inhale_count}吸 → {hold_count}屏 → {exhale_count}呼
```

## Common Pitfalls

- **Surface-level characters**: Characters without sacred flaws or internal needs feel flat. Every character should have something they believe that isn't quite true.
- **Same desire_want and desire_need**: If the character's want equals their need, they have no arc. The story proves nothing.
- **Static scenes**: A scene that ends in the same emotional state it began has no dramatic purpose. Every scene must produce change.
- **No deep conflict**: Stories that only have surface-level conflict (arguments, misunderstandings) feel trivial. At least the climax must operate at the deep (value/identity) level.
- **Surface text = subtext**: If a character says exactly what they mean, there's no dramatic depth. Dialogue should always have a layer beneath.
- **"And then" connections**: Scenes connected by mere sequence ("and then this happened, and then that happened") lack narrative drive. Find the causal or contrastive link.
- **Flat breathing rhythm**: All inhale (constant tension) causes audience fatigue. All exhale (constant calm) causes boredom. The story needs a breath cycle.
- **Ignoring mobile constraints**: Dialogue lines longer than 15 Chinese characters won't fit on mobile screens. This is a hard technical limit for short-form platforms.
