# Character & Scene Consistency for AI-Generated Comics

> Guidance for maintaining visual consistency across multiple AI-generated images
> when using Seedream API or similar image generation tools.

## The Problem

AI image generators like Seedream produce independent images. Each call starts fresh,
so character faces, clothing, and scene environments vary frame to frame. For comics that
need visual continuity, this is a critical issue.

## Solution: Two-Part Character Description

The key insight: **some traits must never change, others MUST change per panel.**

A single fixed `anchor_description` copied verbatim into every prompt causes the
**identical expression problem** — if the description says "笑得眼睛弯弯", Seedream
will produce the same smile in every panel, even when the beat calls for crying.

### Split the character description into two parts:

---

### Part 1: `core_traits` — NEVER changes (immutable identity)

These define the character's **physical identity**. They are included verbatim in every
prompt and ensure the character is recognizable across all panels.

**core_traits Template:**
```
[年龄]岁[性别]，[脸型]，[五官特征]，[发型：长度+颜色+质地]，
[体型：身高+体态]，[穿着：核心色系+标志性单品]，
[肤色/皮肤特征]，[标志性配饰或特征]
```

**Example — "妈妈" core_traits:**
```
50岁亚洲女性，圆脸，齐肩短发带自然卷，戴银色细框眼镜，
常穿米色针织开衫，身高160cm左右，皮肤偏黄但气色好，
手上有岁月的纹路，左手戴一只老式银镯子
```

**Rule: `core_traits` is copied verbatim into EVERY prompt for this character. Never modify it between panels.**

---

### Part 2: `per_panel_expression` — MUST vary per panel (emotion-driven)

These define the character's **current emotional state and action** in THIS specific panel.
They change with every panel based on the story beat's emotion.

**per_panel_expression Template:**
```
[表情：面部肌肉+眼神+嘴巴]，
[身体语言：姿势+手势+身体朝向]，
[当前动作：具体在做什么]，
[情绪氛围：这个瞬间的情感重量]
```

**Example expressions for "妈妈" across panels:**
```
# Panel 1 (HOOK beat — 操心):
表情略带担忧，眉头微蹙但嘴角有笑意，眼神温柔中带一丝焦急，
身体微微前倾，双手在围裙上擦着，站在厨房门口朝外张望

# Panel 3 (CONFRONT beat — 惊讶):
眼睛睁大，嘴巴微张，眉毛扬起，身体僵住一秒，
右手停在半空中，整个人的动作突然中断

# Panel 5 (RESOLVE beat — 释然):
眼角有泪光但嘴角上扬，眼神柔和深远，
身体放松地靠在椅背上，双手自然搭在膝盖上，深深呼出一口气
```

---

## Expression Variation Library (表情变化库)

When designing `per_panel_expression` for each panel, map the beat's emotion to specific
facial and body cues. **Never reuse the same expression across panels.**

| Emotion | Face | Eyes | Mouth | Body Language |
|---------|------|------|-------|---------------|
| 操心/担心 | 眉头微蹙 | 目光追随，带一丝焦虑 | 微微抿嘴 | 身体前倾，手不自觉地动 |
| 惊讶/震惊 | 眉毛扬起 | 睁大，瞳孔收缩 | 微张或张大 | 身体僵住，动作中断 |
| 开心/欣慰 | 面部舒展 | 弯成月牙，有光 | 嘴角上扬，露齿或不出 | 身体放松，肩膀下沉 |
| 生气/愤怒 | 眉头紧锁 | 锐利，直视 | 紧抿或咬牙切齿 | 身体紧绷，拳头握紧 |
| 悲伤/心酸 | 面部下垂 | 湿润，视线向下 | 嘴角下撇，颤抖 | 肩膀内收，身体缩小 |
| 尴尬/社死 | 面部僵硬 | 左右躲闪，不敢直视 | 不自然地扯嘴角 | 身体缩起，想找地方躲 |
| 困惑/不解 | 眉头微皱 | 眯起，歪头 | 微微张开，欲言又止 | 手托下巴或挠头 |
| 释然/放下 | 面部松弛 | 柔和，望向远方 | 轻轻呼气的嘴型 | 身体后靠，深呼吸 |
| 决心/坚定 | 面部紧绷 | 直视前方，不闪躲 | 紧闭或一字抿嘴 | 身体挺直，握拳或迈步 |
| 温柔/感动 | 面部柔和 | 湿润，目光温暖 | 微笑，可能有泪 | 身体前倾，想要靠近 |

**Critical rule: The expression in `per_panel_expression` must NOT contradict `core_traits`.** 
If `core_traits` says "戴眼镜", the expression can describe eyes behind the glasses but
shouldn't remove the glasses. If `core_traits` says "短发", don't describe long hair
movements.

---

### Part 3: Prompt Assembly — The CORRECT Way

**WRONG (old approach — causes identical expressions):**
```
{image_prompt_prefix}, {scene_template}, {character.anchor_description},
{panel.visual_description}, {style_lock}
```
The `anchor_description` includes "笑得眼睛弯弯" → locked smile in every panel.

**CORRECT (new approach — identity consistent, emotion varied):**
```
{image_prompt_prefix},
{scene_description} — 从这个角度: {camera_angle}, 氛围: {atmosphere},
{character.core_traits}, 此刻: {character.per_panel_expression},
{panel.visual_description},
{style_lock}
```

**Key difference:** `core_traits` stays the same. `per_panel_expression` changes every panel.
The character looks like the same person but shows different emotions.

---

## Scene Variation Strategy (场景变化策略)

The same scene appearing in multiple panels should NOT look identical.
Use these techniques to vary the scene while keeping it recognizable:

### 1. Camera Angle Rotation (镜头角度轮换)

For the same scene across panels, rotate through different angles:

| Panel # in scene | Camera Angle | Effect |
|-----------------|--------------|--------|
| 1st appearance | 中景平视 (eye-level mid-shot) | Establish the scene |
| 2nd appearance | 近景俯角 (close-up, slight high angle) | Focus on character emotion |
| 3rd appearance | 中景侧角 (mid-shot, side angle) | Show spatial relationship |
| 4th+ appearance | 特写或过肩 (close-up or over-shoulder) | Intimacy or tension |

### 2. Lighting/Atmosphere Shift (光线/氛围变化)

Match the lighting to the emotional beat:

| Beat | Atmosphere | Lighting |
|------|-----------|----------|
| HOOK | 日常感，平静 | 均匀自然光，无戏剧性 |
| BUILD | 微妙变化，暗流涌动 | 光线稍暗或色调微冷 |
| CONFRONT | 紧张，冲突 | 高对比度，阴影加深 |
| REVEAL | 真相浮现，情绪高峰 | 聚光效果，暖光或冷光极致化 |
| RESOLVE | 释然，回归平静 | 柔和光线，可能带夕阳光或晨光 |

### 3. Scene Description Library (场景描述库)

Instead of a single `template_prefix`, build a **scene description library** per scene:

```yaml
scene_registry:
  家中厨房:
    master_description: "中式家庭厨房，L型操作台，白色瓷砖墙面，木色橱柜，
      窗台上摆着几盆绿萝，窗外是小区花园"
    camera_angles:
      - "从厨房门口看向操作台，门框作为前景框住画面"
      - "从窗户方向看向厨房内部，逆光，人物成剪影"
      - "操作台特写，俯角，只看到手和台面上的食材"
      - "角落视角，从冰箱旁边斜看整个厨房"
    atmosphere_variants:
      - "午后阳光透过纱帘洒在台面上，空气中飘着细小的灰尘"
      - "黄昏时分，暖黄的灯光取代了自然光"
      - "阴天，白光灯管冷冷的，厨房显得比平时安静"
```

The `generate` stage picks: `master_description` + one `camera_angle` + one `atmosphere_variant`.

This ensures the same kitchen feels alive and varied across panels — not a static backdrop.

---

## Seedream Reference Image Pattern (角色参考图模式)

Seedream 4.0+ supports reference images for character consistency.
**The generate stage MUST pass reference images to `image_selector`.**

### Workflow:

1. **Preview stage** generates character neutral full-body images (正面站立全身像).
   Save these as `projects/<name>/assets/images/character_<name>_ref.png`.

2. **Preview stage** also generates **expression headshots** (表情大头照) — one close-up face
   shot per unique emotion per character. Save as
   `projects/<name>/assets/images/character_<name>_expr_<emotion>.png`.

3. **Preview stage** composites each headshot + full-body into a single **composite reference
   image** (合成参考图) — 1024×1024, full-body on left, headshot on right. Save as
   `projects/<name>/assets/images/character_<name>_composite_<emotion>.png`.

4. **Preview stage** also generates scene sample images (场景定妆照).
   Save these as `projects/<name>/assets/images/scene_<name>.png`.

5. **Generate stage** — for EVERY panel:
   - Pass the **composite reference image** matching the panel's target emotion as `reference_image`
   - The composite anchors BOTH identity (full-body left half) AND expression (headshot right half)
   - **Do NOT pass scene reference images** — scene images constrain composition too much
   - Instead, use the scene's `master_description` + varied `camera_angle` + `atmosphere` for scene diversity

### Why Composite Reference Images (合成参考图)

Seedream only accepts ONE reference image per call. The composite approach solves the
identity-vs-expression tradeoff by packing both signals into a single image.

```
┌──────────────┬──────────────┐
│              │              │
│  Full-body   │  Expression  │
│  (identity)  │  headshot    │
│              │  (emotion)   │
│              │              │
└──────────────┴──────────────┘
   512 × 1024  │  512 × 1024
          1024 × 1024 composite
```

| Reference Type | Anchors | Accuracy | When to Use |
|---------------|---------|----------|-------------|
| Neutral full-body (alone) | Identity only | Expression relies on text | Never — always use composite |
| Expression headshot (alone) | Expression + partial identity | Loses body/clothing detail | Never — always use composite |
| **Composite (both)** | **Identity + expression** | **Both from visual reference** | **Always** — for every character panel |

**Compositing rules:**
- Full-body on LEFT (identity anchor), headshot on RIGHT (expression anchor)
- Both halves resized to 512×1024, composite output is 1024×1024
- Light-gray (#F0F0F0) background for gaps from aspect ratio differences
- Generate via PIL after headshot is approved (no separate user review needed)

### Why Expression Headshots + Composites

**The problem with neutral-only references:**
- Seedream sees a neutral face and reads the prompt's expression text
- Text descriptions like "眉头微蹙" are open to interpretation — Seedream may produce
  a subtle frown instead of the worried expression the story needs
- Expression accuracy degrades across panels, especially for complex or subtle emotions

**The solution — expression headshots composited with full-body:**
- Seedream sees the target expression ON the correct face AND the full-body identity
  in a single composite reference image
- Both identity AND emotion are visually anchored — no ambiguity, no tradeoff
- Each panel gets the composite matching its specific emotion
- Result: strongest possible consistency — identity and expression both from visual reference

### Why scene reference images backfire:

Passing a scene reference image tells Seedream "make it look like THIS image."
Result: every panel in that scene has the **exact same composition, lighting, and angle**.
The character appears pasted in because Seedream is trying to reproduce the reference
image's composition while also drawing a character — a fundamentally conflicting instruction.

**Instead:** Use the scene sample image from preview only for HUMAN confirmation
("yes, this kitchen looks right"). Then generate panels with text descriptions that
vary the angle and atmosphere — Seedream produces naturally varied compositions.

---

## Quick Checklist Before Image Generation

- [ ] `core_traits` written for each recurring character (immutable identity)
- [ ] `per_panel_expression` designed for each character in each panel (emotion-driven variation)
- [ ] Scene description library built per scene (master + camera angles + atmosphere variants)
- [ ] Style lock keywords selected and locked
- [ ] Character reference images generated (preview stage) — neutral full-body + expression headshots + composites
- [ ] Expression headshots generated for ALL unique emotions per character
- [ ] Composite reference images generated (headshot + full-body side-by-side, 1024×1024)
- [ ] Generate stage will use composite_reference_path for every character panel
- [ ] Every panel prompt verified: `core_traits` (same) + `per_panel_expression` (varied) + `scene_description` + `camera_angle` + `atmosphere` + `style_lock`
- [ ] Expression variety check: no two panels have the same `per_panel_expression`
- [ ] Scene variety check: same scene across panels uses different camera angles and atmospheres

## Applying to OpenMontage

The `story_seed` output from Story Factory includes:
- `character_archetypes[].visual_notes` → use as `core_traits` base
- `suggested_style.seedream_keywords` → use as Style Lock
- `beats[].emotion` → drives `per_panel_expression` design

When the agent generates Seedream prompts, it should compose:
```
[image_prompt_prefix] +
[scene master_description] + [camera_angle] + [atmosphere] +
[character.core_traits] + [character.per_panel_expression] +
[panel action description] +
[style_lock]
```
