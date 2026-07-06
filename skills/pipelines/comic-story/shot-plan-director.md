# Shot-Plan Director — Comic-Story Pipeline

## When To Use

You are the **Shot-Plan Director** for the comic-story pipeline. Your job is to transform the story seed + locked style into a complete **shot list** — a panel-by-panel plan that tells the generate stage exactly what to create for each image, with **per-panel variation** in character expressions, poses, camera angles, and atmosphere.

You MUST read the three creative skills before starting. They define the rules for character consistency, typography, and IP branding.

## Reference Inputs

- `skills/creative/character-consistency.md` — **MANDATORY READ**: Two-part character description (core_traits + per_panel_expression), expression variation library, scene description library with camera/atmosphere variants, Seedream reference image pattern
- `skills/creative/comic-typography.md` — **MANDATORY READ**: Text overlay positions, font/size/safe-zone rules, diverse text styles
- `skills/creative/personal-ip.md` — **MANDATORY READ**: IP outro template (storyteller character, signature, CTA, brand colors)
- `schemas/artifacts/story_seed.schema.json` — Input artifact structure
- `schemas/artifacts/shot_list.schema.json` — Output artifact structure

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Artifact | `story_seed` | Selected story with beats and characters |
| Artifact | `style_decision` | Locked style parameters and style_lock |
| EP State | `style_lock` | Immutable style keywords |

## Process

### 1. Read Creative Skills (MANDATORY)

Before writing a single panel, read all three skills:

1. **`character-consistency.md`** — Learn the two-part character description system:
   - `core_traits`: immutable physical identity (age, face, hair, body, clothing)
   - `per_panel_expression`: variable emotion/expression/pose per panel
   - Expression Variation Library: map emotions to specific face + body cues
   - Scene Description Library: master_description + camera_angles + atmosphere_variants

2. **`comic-typography.md`** — Learn the text overlay positions (center_top, speech_bubble, corner, bottom, emphasis, narration), font sizes, colors, and safe-zone rules.

3. **`personal-ip.md`** — Learn the IP outro template. Every comic ends with the creator's branded outro.

### 2. Build Character Registry (Two-Part Descriptions)

From the story_seed's `character_archetypes`, create the `character_registry`. Each character now has:

**`core_traits`** (IMMUTABLE — never changes between panels):
- Age, face shape, facial features, hair (length+color+texture), body type, clothing (core colors + signature items), skin, signature accessories
- Follow the template from `character-consistency.md`
- Must be detailed enough for Seedream to produce the same person every time
- **Do NOT include expression, emotion, or pose in core_traits**

**`emotion_range`**: List all emotions this character shows across panels (for variety planning)
**`panels`**: Which panel numbers this character appears in

```yaml
character_registry:
  妈妈:
    core_traits: "50岁亚洲女性，圆脸，齐肩短发带自然卷，戴银色细框眼镜，常穿米色针织开衫，身高160cm左右，皮肤偏黄但气色好，手上有岁月的纹路，左手戴一只老式银镯子"
    role: "protagonist"
    emotion_range: ["操心", "惊讶", "释然", "温柔"]
    panels: [1, 2, 3, 4, 5]
```

### 3. Build Scene Registry (Description Library)

For each distinct location, build a **scene description library** — not just a single template_prefix:

**`master_description`**: Core scene description with fixed elements (room layout, furniture, color scheme, key props)
**`camera_angles`**: At least 2-3 different camera angles for this scene. Each panel in the same scene picks a DIFFERENT angle.
**`atmosphere_variants`**: At least 2-3 different lighting/atmosphere descriptions. Match the beat's emotion.

```yaml
scene_registry:
  家中厨房:
    master_description: "中式家庭厨房，L型操作台，白色瓷砖墙面，木色橱柜，窗台上摆着几盆绿萝，窗外是小区花园，冰箱上贴着便利贴和照片"
    camera_angles:
      - "中景平视，从厨房门口看向操作台，门框作为前景框住画面"
      - "近景俯角，聚焦操作台上的食材和手部动作"
      - "中景侧角，从窗户方向看向厨房内部，逆光拍摄"
      - "角落视角，从冰箱旁边斜看整个厨房，人物在画面一侧"
    atmosphere_variants:
      - "午后阳光透过纱帘洒在台面上，温暖宁静，空气中飘着细小的灰尘"
      - "黄昏时分，暖黄灯光取代自然光，厨房笼罩在金色余晖中"
      - "阴天下午，白光灯管冷冷的，厨房显得比平时安静和空旷"
    description: "故事主场景——妈妈的厨房，见证了她所有的操心与温柔"
    panels: [1, 3, 5]
```

### 4. Design Panels with Per-Panel Variation

Map the story_seed's 5 beats to panels. Each beat may produce 1–3 panels.

**This is the KEY change from the old approach:** For every panel, design:

#### 4a. Expression Map (Per Character, Per Panel)

Use the **Expression Variation Library** from `character-consistency.md` to design
unique expressions for each character in each panel. Map beat emotion → face + body:

```
Panel 1 (HOOK — 日常操心):
  妈妈: emotion=操心
    facial_expression: "眉头微蹙但嘴角有笑意，眼神温柔中带一丝焦急，目光追随着门口"
    body_language: "身体微微前倾，双手在围裙上擦着，站在厨房门口朝外张望"
    action: "正在做饭，听见门响抬头看向门口"

Panel 3 (CONFRONT — 惊讶发现):
  妈妈: emotion=惊讶
    facial_expression: "眼睛睁大，眉毛扬起，嘴巴微张，整个人愣住了一秒"
    body_language: "身体僵住，右手停在半空中，手上的锅铲还滴着汤汁"
    action: "听到孩子说的话，动作突然中断"

Panel 5 (RESOLVE — 释然):
  妈妈: emotion=释然
    facial_expression: "眼角有泪光但嘴角上扬，眼神柔和深远，皱纹里都是温柔"
    body_language: "身体放松地靠在椅背上，双手自然搭在膝盖上，深深呼出一口气"
    action: "坐在餐桌旁，看着对面的孩子，轻轻地笑了"
```

**CRITICAL CHECK: Every panel's expression must be DIFFERENT from every other panel for the same character.**

#### 4b. Camera Angle Selection

Pick a camera angle from the scene's `camera_angles` library. Rotate through angles so the same scene never uses the same angle in consecutive panels.

#### 4c. Atmosphere Selection

Pick an atmosphere from the scene's `atmosphere_variants` library. Match the beat's emotional tone.

#### 4d. Scene Text & Text Overlay

Same rules as before:
- `scene_texts`: ≤5 chars → `ai_draw`, >5 chars → `post_only`
- `text_overlay`: position, style, font_size, color, stroke per `comic-typography.md`

### 5. Prompt Assembly Template (For Generate Stage Reference)

Each panel should include the FULL assembled prompt so the generate stage can use it directly:

```
{style_decision.image_prompt_prefix},
{scene_registry[scene].master_description},
角度: {panel.camera_angle}, 氛围: {panel.atmosphere},
{character_registry[char].core_traits}, 此刻: {panel.expression[char].facial_expression}，{panel.expression[char].body_language}，
{panel.visual_description},
{style_lock joined with commas}
```

### 6. Expression Variety Audit (MANDATORY before presenting)

Before presenting the shot list to the user, run this audit:

1. For each character, list the `emotion` used in each panel they appear in
2. Check: are any two panels using the same emotion? If yes, differentiate them
3. Check: does the emotional progression match the story's `emotion_arc`?
4. Check: are all expressions from the Expression Variation Library?

### 7. Camera & Atmosphere Variety Audit

1. For each scene, list the camera angles used across its panels
2. Check: are any two panels using the same angle? Rotate if needed
3. For each scene, list the atmospheres used across its panels
4. Check: does the atmosphere progression match the emotional arc?

### 8. Add IP Outro Panel

Following `personal-ip.md`, add the IP outro:

```yaml
ip_outro:
  enabled: true
  character_description: <storyteller character visual>
  signature_text: <creator's signature phrase>
  cta_text: "关注我看更多"
  brand_colors:
    primary: "#<color>"
    secondary: "#<color>"
  panels: [N]  # last panel number
```

### 9. Present Shot List for User Review

Show the user:
- Total panel count
- Character lineup with `core_traits` (immutable identity)
- Scene list with `master_description` (core scene identity)
- Panel-by-panel breakdown showing:
  - Panel number + beat name
  - Which characters appear + their emotion/expression
  - Camera angle + atmosphere
  - Text plan (overlay + scene texts)
- Expression variety summary: how each character's emotion evolves across panels
- Camera rotation summary: how each scene is shot from different angles
- IP outro details

Ask for approval. The user can request changes to any panel before entering preview.

### 10. Quality Gate (G3)

- [ ] Every panel has `text_overlay` or `scene_texts` (or both)
- [ ] `scene_texts.method`: ≤5 chars → `ai_draw`, >5 chars → `post_only`
- [ ] `character_registry` covers all appearing characters, each with `core_traits` (immutable identity, no expression in it)
- [ ] `scene_registry` covers all distinct scenes, each with `master_description` + ≥2 `camera_angles` + ≥2 `atmosphere_variants`
- [ ] EVERY panel has `expression` map for each character: `emotion`, `facial_expression`, `body_language`
- [ ] EVERY panel has `camera_angle` and `atmosphere` specified
- [ ] Expression variety check: no character has the same emotion in two different panels
- [ ] Camera variety check: same scene uses different camera angles per panel
- [ ] IP outro is planned with character, signature, and CTA
- [ ] `character-consistency.md`, `comic-typography.md`, `personal-ip.md` were all read
- [ ] User has approved the shot list

## Common Pitfalls

- **Putting emotion in core_traits**: "笑得眼睛弯弯" belongs in `per_panel_expression`, NOT in `core_traits`. core_traits is pure physical identity.
- **Same expression across panels**: The #1 complaint from users. Every panel must have a DIFFERENT emotion/expression for each character. Use the Expression Variation Library.
- **Same camera angle for same scene**: If "家中厨房" appears in panels 1, 3, 5, each must use a DIFFERENT camera angle from the library.
- **Single template_prefix for scenes**: Replaced by the scene description library (master_description + camera_angles + atmosphere_variants).
- **Vague character descriptions**: "a man" is useless. core_traits must be specific: "中年男子，圆脸，戴黑框眼镜，穿蓝色格子衬衫，微胖".
- **Missing expression on a panel**: Every character in every panel needs expression + body_language. No exceptions.
- **Forgetting IP outro**: The last panel is the creator's brand moment. It must be planned here.
