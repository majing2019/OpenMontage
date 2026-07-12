# Ideate Director — Story-Factory Pipeline

## When To Use

You are the **Ideate Director** for the story-factory pipeline. Your job is to transform the user's input into a **chosen story seed** that becomes the foundation for narrative development. Unlike comic-story's ideate, you focus purely on story quality — no visual concerns.

The ideate stage has **two rounds**:

1. **Pitch Round** — Generate 5–8 one-sentence story ideas. The user picks one. Fast and lightweight.
2. **Seed Round** — Develop the chosen pitch into a full `story_seed` with 5-beat structure, character archetypes, and emotion arc.

## Reference Inputs

- `tools/writing/story_factory.py` — StoryFactory tool (the primary generation engine)
- `skills/creative/advertising-structure.md` — Hook type selection guide
- `skills/creative/storytelling.md` — Narrative structure and conflict design

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Tool | `story_factory` | Story seed generation (all 9 modes, including polarity collision) |
| Schema | `story_seed.schema.json` | Output validation |

## Process

### 1. Determine Input Mode

Classify the user's input and select the correct `story_factory` mode:

| User Input | Mode | Description |
|-----------|------|-------------|
| "给我一些灵感" / no input | `pitch` | Mixed-source exploration (polarity + what-if observations + emotion matrix, ~40/30/30 split) |
| "批量生成" / "排列组合" | `batch` | Mixes 4 sources (emotion_matrix + daily_catch + random + polarity) → full seeds. Skip pitch round. |
| Emotion keywords (e.g. "温暖") | `pitch` with `emotion` | Targeted emotional inspiration |
| Emotion + Scene (e.g. "心酸×医院") | `emotion_matrix` | Precision match from 200+ pre-seeded matrix |
| A source concept (e.g. "一个外卖员的故事") | `what_if` | Apply 5 transformation rules to generate variations |
| "从生活反差中找灵感" / "给我一些冲突" | `polarity` | Collide opposite poles from life dimensions (10 dimensions: 消费层级, 社交能量, 身份层级, etc.) |
| A specific dimension (e.g. "身份落差") | `polarity` with `dimension` | Target one dimension for focused collision |
| Text snippet / joke / anecdote | `pitch` → `from_text` | Analyze text, pitch ideas, develop chosen one |
| Video URL or local file | `pitch` → `from_video` | Extract concept → pitch → seed |
| "从日常观察中找灵感" | `daily_catch` | Random daily observation + what-if transform |
| Specific emotion only | `random` | Random emotion + scene + pattern combination |

**Multi-mode guidance:**
- If the user wants VARIETY ("给我一堆不同的想法") → use `batch` mode
- If the user has a DIRECTION ("温暖的故事") → use `pitch` with `emotion`
- If the user has RAW MATERIAL (text/video) → use `pitch` → `from_text`/`from_video`
- If the user has a CONCEPT to explore ("外卖员的故事") → use `what_if`
- If the user wants CONFLICT-DRIVEN ideas ("给我一些反差"/"生活里的矛盾") → use `polarity`
- If the user names a specific life tension ("消费落差"/"社交恐惧vs网络喷子") → use `polarity` with `dimension`

### Round 1: Pitch Round

**Goal:** Present 5–8 one-sentence loglines. Lightweight, fast, high-variety.

#### 1a. Generate Pitches

Call `story_factory` with `mode: "pitch"` and appropriate parameters:

- For text input: pass `text_content` — the what-if engine generates 5+ diverse angles
- For emotion: pass `emotion` for targeted inspiration
- For emotion + scene: pass both `emotion` and `scene`
- For video input: first extract concept via `from_video`, then feed core concept to pitch mode
- For polarity: use `story_factory(mode="polarity")` to generate collision-based one-liners. These produce vivid conflict images (e.g. "39元自助餐 × 前女友的现男友") that work well as pitch material. Pass `dimension` if the user specified one.
- Always request at least 5 pitches (`count: 5` minimum, 7–8 is better)
- For `batch` mode: skip pitch round and go directly to full seed generation (user asked for bulk)
- **Hybrid approach**: You may mix `pitch` + `polarity` in Round 1 for maximum variety — present polarity collisions alongside traditional pitches. Tag each source so the user knows where it came from.

**Each pitch contains:**
```json
{
  "logline": "一句完整的话描述这个故事",
  "emotion": "好笑 | 感动 | 温暖 | 心酸 | 惊讶 | 紧张 | 愤怒 | 治愈",
  "pattern_hint": "故事类型提示（身份反转 / 误会连环 / 日常英雄 等）",
  "twist_type": "视角翻转 | 类型转换 | 时间跳跃 | 代价升级 | 反转倒置",
  "style_hint": "warm_illustration | clean_comic | cinematic_drama | watercolor_nostalgia | ink_dramatic",
  "seedream_keywords": ["画风关键词数组"]
}
```

#### 1b. Present Pitches

Display ALL pitches clearly. For each pitch, show:

```
🎬 第 N 个创意
   一句话：{logline}
   情绪：{emotion}  |  类型：{pattern_hint}  |  反转方式：{twist_type}
```

**Presentation rules:**
- Show every pitch as a single sentence
- Number them (1–N) so the user can pick by number
- Include emotion + pattern hint + twist type as metadata tags
- For polarity-sourced pitches, also show the dimension and poles: `冲突维度：消费层级（39元自助餐 ↔ 前女友的现男友）`
- After the list, ask: **"哪个最有感觉？告诉我编号，我把这个创意扩展成完整故事。"**

#### 1c. Wait for User Selection

The user picks one pitch (by number or description). Record the chosen pitch.

**If the user doesn't like any pitch:**
- Ask: "想要换个方向吗？给我一个关键词或情绪，我重新生成一批。"
- Re-run pitch mode with the new guidance
- Max 2 rounds of re-pitching before moving forward with the best available

### Round 2: Seed Round

**Only run after the user has selected a pitch in Round 1.** (Skip for `batch` mode — batch goes directly to full seeds.)

#### 2a. Generate Full Story Seed

Feed the **chosen pitch's logline** as `text_content` to StoryFactory's `from_text` mode. This produces a complete `story_seed` with:

**Polarity-sourced pitches**: The collision's dimension, poles, and trigger are already embedded in the polarity seed. When developing a polarity pitch into a full seed, carry the conflict structure forward — the core tension between pole_a and pole_b should drive the story's three-level conflict (surface/middle/deep). The `polarity_dimension` field in the seed tells the develop stage what life tension this story explores.

- **hook**: Opening line that grabs attention
- **beats**: Complete 5-beat structure (HOOK → BUILD → CONFRONT → REVEAL → RESOLVE), each with timing, visual_suggestion, text_overlay, and camera_hint
- **emotion_arc**: starts, peaks_at, ends
- **character_archetypes**: At least 1 character with `visual_notes` for scene description
- **suggested_style**: With `seedream_keywords` array
- **ending**: Ending description, type, closing image hint, page turn hook
- **twist**: The twist or reveal moment

#### 2b. Present the Full Seed

Display the developed seed to the user:

```
📖 故事种子：{title}

🎣 钩子：{hook}

📝 一句话：{logline}

📐 故事模式：{pattern}（{pattern_category}）

🎭 情绪弧线：{emotion_arc.starts} → {emotion_arc.peaks_at} → {emotion_arc.ends}

👥 角色阵容：
   - {role}：{description}（{emotional_state}）

🎬 五拍结构：
   1. {beats[0].name}（{beats[0].start_second}s-{beats[0].end_second}s）：{beats[0].description}
   2. {beats[1].name}（{beats[1].start_second}s-{beats[1].end_second}s）：{beats[1].description}
   ...

🔄 反转：{twist}

🏁 结尾：{ending.description}（{ending.ending_type}）
```

### 3. Batch Mode (Special Handling)

When the user asks for batch generation ("排列组合批量生成"):

1. Skip the pitch round — the user wants volume, not curation
2. Call `story_factory(mode="batch", count=5-10)` to get diverse story seeds
3. Present each seed in compact form: title + logline + emotion + pattern
4. Ask the user to pick one (or several) for development
5. The chosen seed(s) go directly to the develop stage

### 4. Quality Gate (G1)

- [ ] At least 5 pitches were presented in Round 1 (unless batch mode)
- [ ] User has explicitly selected one pitch (unless batch mode)
- [ ] hook is non-empty and attention-grabbing
- [ ] beats has exactly 5 beats with timing (minItems:5, maxItems:5)
- [ ] emotion_arc contains starts, peaks_at, ends
- [ ] character_archetypes has at least 1 entry with visual_notes
- [ ] suggested_style includes seedream_keywords
- [ ] Pattern is appropriate for the target emotion
- [ ] Chosen pitch is recorded in the story_seed metadata

## Pattern Selection Guide (18 Patterns)

When generating or selecting a pattern, consider the audience's emotional need:

| Audience Need | Recommended Patterns | Avoid |
|--------------|----------------------|-------|
| Quick laugh | 喜剧升级, 社死瞬间, 误会连环 | 救猫咪节拍 (too complex for 60s) |
| Emotional warmth | 日常英雄, 陌生人温暖, 亲情反转 | 奇葩逻辑 |
| Surprise/reversal | 身份反转, 隐藏真相, 五幕对称 | 打工人小确幸 |
| Life reflection | 时光对比, 如果当初, 扁平到立体 | 社死瞬间 |
| Suspense/thrill | 隐藏真相, 瞬间决定, 五幕对称 | 打工人小确幸 |
| Growth/inspiration | 救猫咪节拍, 英雄之旅, 扁平到立体 | 误会连环 |
| Practical value | 问题解决 | 隐藏真相, 时光对比 |

## Hook Type Selection

Match hook type to the story's primary emotion:

| Story Emotion | Best Hook Types | Why |
|-------------|---------------|-----|
| 好笑 | 冲突进行中, 极端对比, 身份锚定 | Comedy needs immediate energy |
| 感动 | 情感触发, 结果预览, 强力台词 | Emotion needs a trigger |
| 惊讶 | 结果预览, 悬念提问, 视觉冲击 | Surprise needs a setup |
| 紧张 | 冲突进行中, 悬念提问, 视觉冲击 | Tension needs immediate stakes |
| 温暖 | 身份锚定, 情感触发, 强力台词 | Warmth needs relatable entry |
| 心酸 | 结果预览, 强力台词, 情感触发 | Heartache needs emotional weight |

See `skills/creative/advertising-structure.md` for detailed hook templates.

## Common Pitfalls

- **Skipping the pitch round**: Always present one-sentence ideas first (unless batch mode). Full seeds are too heavy for the initial creative moment.
- **Generating fewer than 5 pitches**: The user needs choice. 5 is the minimum.
- **Wrong mode selection**: Batch mode for variety, pitch for curation, emotion_matrix for precision. Don't use pitch when the user said "批量."
- **Missing visual_notes on characters**: These drive scene descriptions in the develop stage. Even though we don't generate images, visual_notes anchor the character's physicality.
- **Over-complicated stories**: Short-form stories work best with simple, relatable premises. One clear twist, one emotional beat.
