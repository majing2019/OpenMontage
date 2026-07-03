# Character & Scene Consistency for AI-Generated Comics

> Guidance for maintaining visual consistency across multiple AI-generated images
> when using Seedream API or similar image generation tools.

## The Problem

AI image generators like Seedream produce independent images. Each call starts fresh,
so character faces, clothing, and scene environments vary frame to frame. For comics that
need visual continuity, this is a critical issue.

## Solution: Prompt Engineering Anchors

### 1. Character Anchor (角色锚定)

Before generating any images, create a fixed **Character Anchor** description for each
recurring character. This anchor is appended to EVERY prompt that includes that character.

**Character Anchor Template:**

```
角色名: [固定描述]
- 年龄感: [年龄段, 如"25-30岁"]
- 脸型: [如"圆脸/方脸/瓜子脸"]
- 五官特征: [标志性特征, 如"单眼皮/厚嘴唇/高鼻梁"]
- 发型: [长度+颜色+质地, 如"齐肩黑色直发"]
- 体型: [身高+体态, 如"165cm微胖"]
- 穿着: [核心色系+标志性单品, 如"总穿深蓝色卫衣"]
- 表情习惯: [如"爱皱眉/笑起来眼睛弯弯"]
```

**Example — "妈妈" Character Anchor:**

```
50岁亚洲女性，圆脸，齐肩短发带自然卷，戴银色细框眼镜，
常穿米色针织开衫，身高160cm左右，笑起来眼睛弯弯，
皮肤偏黄但气色好，手上有岁月的纹路
```

**Rule: This exact text block is appended to every prompt containing this character.**

### 2. Scene Template (场景模板)

For scenes that appear multiple times in one story, create a **Scene Template**.
Every image in that scene starts with the same description prefix.

**Common Scene Templates:**

| Scene | Template Prefix |
|-------|----------------|
| 微信群聊 | 手机屏幕特写，白色聊天背景，绿色气泡（对方），白色气泡（自己），顶部标题栏显示群名，底部输入栏，iPhone比例 |
| 微信朋友圈 | 手机屏幕，朋友圈界面，白色背景，用户头像+名字+文字+配图，点赞和评论区域 |
| 家中客厅 | 温馨中式客厅，米色布艺沙发靠窗，原木茶几上摆着茶杯，暖黄色落地灯，墙上小画框，下午阳光斜照 |
| 餐桌 | 中式家庭餐桌，木质桌面，几道家常菜，碗筷摆放整齐，头顶暖黄吊灯 |
| 办公室 | 现代办公室，灰色格子间，荧光灯，电脑屏幕亮着，桌上有咖啡杯和文件 |
| 地铁车厢 | 北京地铁车厢，白色灯管，橙色座椅，窗外隧道黑影，拉着扶手的乘客 |

**Rule: Use the same Scene Template text exactly for all images in that scene.**

### 3. Seedream Reference Image Pattern

Seedream 4.0+ supports reference images:

1. **Step 1 — Character Headshot:** Generate a single "定妆照" (casting photo) for each
   character. Use a neutral background, full-body or half-body front view. Save this image.

2. **Step 2 — Reference in Prompts:** For every subsequent image containing that character,
   pass the headshot as a reference image. This significantly improves consistency.

3. **Prompt for Headshot:**
   ```
   [Character Anchor], 正面半身照，中性表情，白色背景，插画风格，
   清晰的五官细节，用于角色设定参考图
   ```

### 4. Style Lock (画风锁定)

Lock the art style across all images in one story:

```
画风关键词 (append to every prompt):
温暖插画风格, 手绘质感, 柔和色调, 日式生活漫画,
统一画风, 一致的线条粗细
```

**Rule: The style keywords NEVER change within one story.**

## Quick Checklist Before Image Generation

- [ ] Character Anchor written for each recurring character
- [ ] Scene Template written for each recurring location
- [ ] Style lock keywords selected
- [ ] Character headshots generated (if using reference images)
- [ ] Every prompt verified: starts with Scene Template, includes Character Anchor, ends with Style Lock

## Applying to OpenMontage

The `story_seed` output from Story Factory includes:
- `character_archetypes[].visual_notes` → use as Character Anchor
- `suggested_style.seedream_keywords` → use as Style Lock
- `visual_keywords` → use as Scene Template starting point

When the agent generates Seedream prompts, it should compose:
```
[Scene Template] + [specific scene action] + [Character Anchor] + [Style Lock]
```
