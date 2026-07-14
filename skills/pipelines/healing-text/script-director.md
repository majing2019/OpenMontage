# Script Director — Healing Text Pipeline

## When To Use

The user provides a passage of healing/zen text (essay, prose, golden quotes).
Your job: segment it into visual beats, analyze the emotional mood of each
segment, assign a motion priority tier, extract concrete visual keywords for
video/image generation, and propose a font shortlist that matches the text's
character. The text itself IS the video's voice by default. When `tts_enabled`
is selected, optional narration adds a spoken layer alongside the text overlay —
but subtitles always remain.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Input | User-provided text passage | Raw material |
| Playbook | `styles/warm-illustration.yaml` or `styles/literary-illustration.yaml` | Style-specific visual parameters, color palette, typography, prompt prefix |
| Agent Skill | `.agents/skills/visual-taste/SKILL.md` | Font selection aesthetic principles — avoid typography slop, match font character to text mood |
| Agent Skill | `.agents/skills/seedream-prompt-patterns/` | Reference examples for high-quality Chinese visual keywords — study how concrete scene descriptions differ from abstract adjectives |

## Motion Priority Tiers

Each segment gets ONE of three motion tiers. This controls the asset budget:

| Tier | What it gets | Budget hint | Visual character |
|------|-------------|-------------|------------------|
| `video` | AI video clip (Seedance, 4-5s) | $$$ | Real cinematic motion — waves, wind, light |
| `animate` | Image→video or stock video (3-4s) | $$ | Gentle motion, can be stock footage |
| `still` | Cinematic still image + Ken Burns | $ | Quiet moments, breathing space |

**Rules for assigning motion priority:**

- **video** — emotional peaks, the climax, the most powerful line in the passage.
  Maximum 30% of total segments (1-2 segments in a typical 5-segment piece).
  These are your budget anchors — spend here.

- **animate** — emotional buildup, transition moments, vivid descriptions.
  These carry the flow but don't need full AI video.

- **still** — quiet connective tissue, setup, gentle landing. Ken Burns is enough.

The emotional arc should look like:
```
still → animate → VIDEO (peak) → animate → still (landing)
```

**For stock-footage mode:** All segments can be `motion_priority: video` since
stock clips cost nothing. A 6-segment piece with all-video is valid and produces
a polished edit. The emotional arc still matters for pacing (peak gets longer
transition, larger subtitle), but you are not constrained by AI generation budget.
The `still` tier is still valid if you want a quiet breathing moment, but every
segment CAN be video when matching stock footage exists.

## Process

### 1. Receive and Understand the Text

Read the user's text carefully. Note:

- The overall emotional arc (where does it start, peak, and land?)
- The rhythm — short punchy lines vs. flowing prose
- The imagery already present in the words
- The target emotional state for the viewer
- Which line is THE one — the emotional peak that deserves a video budget

### 1.5. Style Selection (MANDATORY — before segmentation)

Present the user with two visual styles. They MUST pick one before you proceed.

**Style A — 治愈插画风 (Warm Illustration):**
- Vibe: 柔和手绘质感, 温馨治愈, 日式生活插画
- Colors: 米色/浅橙 primary, 深棕/焦糖 accent, 暖白 (#FFF8F0) background
- Font: Rounded sans-serif (Noto Sans SC weight 400-700) or 手写体
- Text: White or dark brown, top-center overlay
- Best for: 亲情、治愈、日常、温暖瞬间、可爱温馨的正能量
- Reference: `styles/warm-illustration.yaml`

**Style B — 文学摄影风 (Literary Illustration):**
- Vibe: 炭灰线描, 莫兰迪灰调, 大面积留白, 散文书籍插画
- Colors: 莫兰迪灰调 primary, 低饱和 accent, 奶油纸色 (#F5F0EB) background
- Font: Serif (Noto Serif SC weight 400-600) or 仿宋
- Text: Charcoal (#3C3833), top-center overlay with optional band
- Best for: 情感叙事、散文漫笔、深夜独白、有深度的故事、文艺向
- Reference: `styles/literary-illustration.yaml`

Record the selected style in script metadata as:
```json
"selected_playbook": "warm-illustration"   /* or "literary-illustration" */
"text_overlay_position": "top-center"
```

### 1.6. Asset Mode Selection (MANDATORY — alongside style selection)

Present the user with two asset sourcing modes. They MUST pick one before you proceed:

**Mode A — AI Generated (Default):**
- Assets: Seedream still images (Phase 1) → Seedance image_to_video (Phase 2)
- Cost: ~$3.00 (API generation costs)
- Best for: Maximum creative control, unique cinematic aesthetics, precise visual alignment with text
- Motion budget rules apply: `video`/`animate`/`still` tier assignment drives cost
- Every segment starts as a Seedream still image — user approves images before video generation

**Mode B — Stock Footage:**
- Assets: All video clips from free stock sites (Pexels, Pixabay Video, Coverr)
- Cost: $0.00 (free stock + local color grading)
- Best for: Zero-budget runs, quick turnaround, all-video timeline, pure scenic/nature content
- All segments can be `motion_priority: video` since there is no per-clip cost
- Search queries are English concrete scene terms (stock APIs use English, not Chinese)
- Color grading (`cinematic_warm`) is applied to unify clips from different sources

**IMPORTANT — Playbook still matters for stock-footage:**
The selected playbook (warm-illustration / literary-illustration) still determines:
- Color palette preferences and text styling (font, text color, shadow)
- Composition preferences (top-center text position)
- Music mood/search query for background music

But AI prompt templates and generation-specific sections of the playbook
(like `asset_generation.image_prompt_prefix`) do NOT apply in stock-footage mode.

Record the selected mode in script metadata:
```json
"asset_mode": "ai-generated"   /* default — or "stock-footage" */
```

### 1.7. TTS Narration Mode (OPTIONAL -- alongside asset mode)

Ask the user whether they want TTS narration. This is independent of asset_mode
and can be combined with either ai-generated or stock-footage.

**Mode A — TTS Narration (Opt-in):**
- Each text segment gets a spoken narration track via tts_selector
- Voice is user-approved (sample preview before batch generation)
- Background music automatically ducks during narration (~0.08) and
  rises between segments (~0.12)
- Subtitles remain active (dual-channel: read + listen)
- Best for: accessibility, passive consumption, emotional warmth
- Preferred TTS: doubao_tts for Chinese text (natural Mandarin,
  character-level timestamps)
- **Voice catalog:** `skills/pipelines/healing-text/voice-preview.html` — 93 个音色可试听

**Mode B — No Narration (Default):**
- Text-only video with background music
- Subtitles carry the entire voice
- Pipeline behavior is unchanged from v3.0

**Voice pre-selection (MANDATORY when tts_enabled=true):**

When the user selects TTS narration, the agent MUST guide them through voice
selection BEFORE advancing to the asset stage:

1. **Open the voice catalog** for the user:
   ```
   试听页面: skills/pipelines/healing-text/voice-preview.html
   你可以在浏览器打开试听 93 个音色，选择喜欢的告诉我 voice_id
   ```
   Or open it directly: `open skills/pipelines/healing-text/voice-preview.html`

2. **Recommend a shortlist** based on the healing text's mood:
   - 温柔暖愈 → 推荐女声：vivi 2.0、温柔妈妈、鸡汤妹妹、柔美女友
   - 文艺散文 → 推荐女声：知性灿灿、知性女声、温柔淑女；男声：悠悠君子、儒雅逸辰
   - 深情独白 → 推荐男声：深夜播客、温暖阿虎、磁性解说
   - 清新日常 → 推荐女声：邻家女孩、小何、清新女声

3. **Wait for the user to pick** a `voice_id` before closing the script checkpoint.
   Record it in script metadata.

Record the selection in script metadata:
```json
"tts_enabled": true,              /* or false (default) */
"tts_voice_id": "zh_female_jitangmei_uranus_bigtts",
"tts_speech_rate": -20
```

**IMPORTANT:** TTS narration is independent of asset_mode. All four combinations
are valid: (ai-generated + tts), (ai-generated + no-tts), (stock-footage + tts),
(stock-footage + no-tts).

### 1.8. Opening Template — Emotion-Guided 片头 (MANDATORY)

基于参考视频 `projects/examples/情感励志4.mp4` 的开头分析，每条 healing-text
视频必须包含一个 **5-7秒双层片头**，结构如下：

**片头四段式：**

```
0.0 – 1.5s：引语卡 (Hook)
  黑底
  小号/中号白字，居中偏下
  引语 = 吸引点击的引入句，如 "最近的焦虑都被这段话治愈了"
  字体：Noto Sans SC Light，字号约 24-30px（720p 竖屏）

1.5 – 3.5s：标题卡 (Title)
  黑底，引语消失
  大号衬线白字，居中
  标题 = 对全文的 4-8 字核心总结，如 "放下焦虑 与自己和解"
  字体：Noto Serif SC 600，字号约 56-64px（720p 竖屏）
  可带极简文字动画（spring fade-in from below）

3.5 – 5.5s：渐入过渡 (Fade Transition)
  标题保持，底部开始浮现 seg_01 画面（暗色版）
  画面从黑底 crossfade 到 seg_01 背景图
  顶部标题在 4.5s 开始淡出

5.5 – end：完全进入 seg_01
  标题消失，seg_01 文字和画面完全呈现
  音乐在 0-3s 内渐入至正常音量
```

**引语生成规则 (hook_line)：**
- 必须用第一人称或第二人称，制造共鸣感
- 模式 1（焦虑/情绪类）："最近[情绪]都被这段话[动词]了"
- 模式 2（温暖/治愈类）："如果你也[感受]，这段话送给你"
- 模式 3（力量/成长类）："[数字]年前读到的这段话，至今记得"
- 模式 4（文学/散文类）："这段话，我反复读了很多遍"
- Agent 根据原文情绪选择最合适的模式，生成一句 10-20 字引语

**标题生成规则 (title_line)：**
- 4-8 字，是对全文核心情绪的凝练总结，不是节选
- warm-illustration：偏意象化（"温柔地爱自己"、"等风也等你"）
- literary-illustration：偏哲思化（"与自己和解"、"风吹过麦浪"）
- 标题必须让观众 2 秒内看懂这段视频"讲什么"

**技术实现：**
- compose 阶段：`seg_opening` 作为固定前奏，不关联脚本 segment
- asset 阶段不需要为片头单独生成素材（纯色底 + 文字渲染）
- Remotion：两个 `<Sequence>` 嵌套，文字用 spring 动画
- FFmpeg：两个 `drawtext` 帧序列 concat 拼接

**脚本 artifact 新增 opening 字段：**
```json
"opening": {
    "hook_line": "最近所有的不安，都被这段话治愈了",
    "title_line": "放下焦虑，与自己和解",
    "hook_style": "anxiety-relief",
    "duration_seconds": 5.5
}
```

Record the opening object in script metadata.

### 2. Segment the Text

Break the passage into 3-8 visual segments. Rules:

- Each segment should be a self-contained thought or emotional beat
- Natural pauses: sentence breaks, paragraph breaks, or emotional turns
- Segments should vary in length for rhythm — some short (3-5 words for impact),
  some longer (10-20 words for flow)
- Assign approximate display duration per segment:
  - Short impactful line: 4-5 seconds
  - Medium flowing sentence: 5-8 seconds
  - Long passage: 8-12 seconds

### 3. Assign Motion Priority and Visual Direction

For EACH segment, produce:

```yaml
segment_id: seg_01
text: "生活不是等待暴风雨过去"
mood: quiet-determination
motion_priority: still          # still | animate | video
visual_keywords_video:          # used when motion_priority=video or animate
  - "gentle waves lapping on a rocky shore at golden hour, slow-motion, cinematic wide shot, soft mist, warm amber light"
visual_keywords_image:          # used when motion_priority=still (or as fallback)
  - "rain on window, soft focus, golden hour light breaking through clouds, shallow depth of field"
visual_style: cinematic-photographic
color_palette: warm-muted
duration_seconds: 5
```

**CRITICAL — Different prompt styles per tier:**

For `video` segments, the prompt must describe MOTION:
- Camera movement: "slow push-in", "gentle pan right", "static tripod with subtle parallax"
- Subject movement: "leaves rustling in breeze", "clouds drifting across mountain", "waves lapping shore"
- Atmospheric: "mist rolling through valley", "golden light shifting through trees"

For `animate` segments:
- Describe the scene + the desired subtle motion
- "Forest path with dappled sunlight shifting through canopy, slow forward dolly, shallow depth of field"

For `still` segments:
- Standard photographic prompt (no motion needed)
- Focus on composition, lighting, and negative space for text overlay

**Visual keyword rules (all tiers):**
- MUST be concrete and imageable (a camera could capture it)
- MUST match the segment's emotional tone
- PREFER natural scenes with atmospheric lighting (sunset, rain, forest, ocean, mountain)
- AVOID abstract concepts — describe what it LOOKS like
- Include lighting direction and color temperature hints
- Each segment gets 1-2 visual keyword groups

**For stock-footage mode — visual keyword rules differ:**

Visual keywords for stock-footage must be:
- **English search terms** (stock APIs use English queries, Chinese returns nothing)
- **Concrete and searchable** — a stock search engine must be able to match them
- **Scene-focused:** `"misty mountain sunrise"`, `"rain on window cozy"`, `"golden hour forest path"`, `"ocean waves at sunset"`
- **NOT poetic or abstract:** `"the quiet courage of being"` will return zero results on Pexels
- **Consider what EXISTS in stock libraries** — nature, water, sky, forest, mountains, cityscapes, interiors, food, technology
- Each segment gets 1-2 English search query variants for coverage

**Example stock-footage visual_keywords:**
```yaml
visual_keywords_stock:
  horizontal: "misty forest path morning sunlight landscape"
  vertical: "misty forest sunlight vertical portrait nature"
```

**Contrast with AI-generated mode visual_keywords:**
```yaml
# ai-generated (Chinese, poetic, prompt-engineered):
visual_keywords_image:
  - "轻文艺插画风格, 莫兰迪灰调配色, 奶油纸张底色, 炭灰色手工线条, 大面积留白..."

# stock-footage (English, searchable, concrete):
visual_keywords_image:
  - "misty morning mountain landscape foggy forest"
```

### 4. Propose Font Shortlist (Style-Aware)

Font choices must match the selected playbook. Present 2-3 options.

**Font reference:** The pipeline ships a live HTML preview at
`skills/pipelines/healing-text/font-preview.html` — open it in a browser to see
every candidate font rendered with sample healing-text. Organized by playbook
(warm-illustration vs literary-illustration) with system vs downloadable tags.

**Font family is user-approved; font SIZE is auto-calculated.** The compose stage
will compute the exact font size per orientation using `transition_defaults.text.font_size_formula`
(based on video dimensions + longest text line). You do NOT need the user to pick a size.
Record `selected_font` (family + weight) but leave `font_size` to the compose stage.

**If warm-illustration (Style A):**
```
Option A: 圆体/手写 — "ZCOOL KuaiLe" / "Ma Shan Zheng"
  Best for: 亲切可爱, 治愈日常

Option B: 圆黑体 — "Noto Sans SC" weight 400
  Best for: 温暖现代, 干净清爽

Option C: 楷体 — "LXGW WenKai"
  Best for: 文艺手写感, 亲切自然
```

**If literary-illustration (Style B):**
```
Option A: 宋体/衬线 — "Noto Serif SC" / "Source Han Serif"
  Best for: 文学典雅, 散文质感

Option B: 仿宋 — "FangSong"
  Best for: 散文质感, 克制优雅

Option C: 细黑体 — "Noto Sans SC Light"
  Best for: 克制简约, 现代文艺
```

Include:
- Font name (system-available or Google Fonts)
- One-line description of what mood it conveys
- Example text rendered in that font

**The user MUST approve the font before advancing.**

### 5. Write the Script Artifact

```json
{
  "version": "1.0",
  "title": "<core theme>",
  "total_duration_seconds": <sum>,
  "sections": [
    {
      "id": "seg_01",
      "text": "<exact text>",
      "start_seconds": 0,
      "end_seconds": 5,
      "label": "opening"
    }
  ],
  "metadata": {
    "asset_mode": "<ai-generated | stock-footage>",
    "tts_enabled": false,
    "selected_playbook": "<warm-illustration | literary-illustration>",
    "text_overlay_position": "top-center",
    "visual_direction": {
      "seg_01": {
        "mood": "quiet-determination",
        "motion_priority": "still",
        "visual_keywords_video": ["gentle waves on rocky shore, slow-motion, golden hour"],
        "visual_keywords_image": ["rain on window, soft focus, golden hour light"],
        "color_palette": "warm-muted",
        "duration_seconds": 5
      }
    },
    "motion_budget": {
      "video_count": 1,
      "animate_count": 2,
      "still_count": 2,
      "rationale": "Single emotional peak at seg_03 ('而是学会在雨中起舞'), buildup and landing as animate/still"
    },
    "font_shortlist": [
      {"name": "ZCOOL KuaiLe", "category": "handwritten", "rationale": "Intimate, personal"},
      {"name": "Noto Serif SC", "category": "serif", "rationale": "Literary, elegant"}
    ],
    "selected_font": "<set after user approval>",
    "text_character": "gentle reflection on resilience",
    "visual_universe": "atmospheric nature cinematography, warm tones, golden hour, mist, water"
  }
}
```

### 6. Present and Get Approval

Before advancing, present to the user:

1. **Style selection** — confirm the chosen visual style (warm-illustration or literary-illustration)
2. **Segmentation + Motion Map** — show the emotional arc with motion priority labels
3. **Visual mood board** — keywords per segment, highlighting which gets the video budget
4. **Font shortlist** — 2-3 options with reasoning (matched to selected style)
5. **TTS narration choice** — confirm whether the user wants spoken narration

Wait for explicit approval on all four. Record `selected_font` and `selected_playbook` in metadata.

## Quality Gate

- Selected playbook is recorded in metadata (`selected_playbook`)
- `tts_enabled` is recorded in metadata (true or false)
- Text overlay position is set to `top-center` in metadata
- Font shortlist matches the selected playbook's typography recommendations
- Motion priority is sparse — at most 30% of segments get `video`
- The emotional peak IS the video segment
- Video-priority segments have motion-rich prompt descriptions
- Still segments still have beautiful, cinematic image prompts
- Font shortlist offers genuine stylistic contrast
- Total duration feels unhurried
- Segment count is proportional to text length

## Common Pitfalls

- Making every segment `video` — burns budget, loses impact (ai-generated mode)
- Making ALL segments `video` in stock-footage mode: fine for budget, but still vary pacing — peak gets longer transition + larger subtitle
- Making NO segment `video` — might as well use the v1 still-image pipeline
- Abstract video prompts that produce surreal/weird motion
- Same motion description for every video segment ("slow pan" × 5 = boring)
- Forgetting that video prompts need MOTION description, not just scene description
- **For stock-footage:** using Chinese or abstract visual keywords → stock APIs need English concrete search terms
- **For stock-footage:** expecting exact scene matches → stock libraries are finite; be flexible with clip selection
- **For stock-footage:** mixing AI prompt style keywords (Hasselblad, film grain, 莫兰迪) into stock search queries → search engines parse these as literal terms and return nothing
- **For stock-footage:** forgetting to set `asset_mode` in metadata → asset director will try AI generation (wrong workflow)
