---
name: volcengine-ark
description: |
  Volcengine Ark (火山引擎方舟) — Seedance 2.0 video generation + Seedream image generation.
  Use when: (1) User has ARK_API_KEY configured, (2) User prefers Alipay/Chinese payment,
  (3) Generating cinematic video clips with native audio sync, (4) High-res image generation
  with native Chinese prompt understanding, (5) Draft preview mode for low-cost video prompt
  validation before full generation.
metadata:
  openclaw:
    requires:
      env_any:
        - ARK_API_KEY
---

# Volcengine Ark — Seedance 2.0 + Seedream

Single API key (`ARK_API_KEY`) unlocks both video (Seedance 2.0) and image (Seedream) generation
on ByteDance's Volcengine Ark platform. No international credit card needed — supports Alipay.

## Tools

| Tool | Capability | Models |
|------|-----------|--------|
| `seedance_volcengine` | `video_generation` | Seedance 2.0 (standard/fast) |
| `seedream_volcengine` | `image_generation` | Seedream 4.0/4.5/5.0/5.0-lite |

## Authentication

```
ARK_API_KEY=ark-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

获取: https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
⚠️ 账户余额需 >= 200 元才能使用 Seedance 2.0 / Seedream 模型。

## Env Var Pitfall (CRITICAL)

**Empty env vars MUST NOT have inline `#` comments.** python-dotenv treats `KEY=  # comment` as
value `"# comment"`, not empty. This caused `seedance_volcengine` to send comment text as the
model ID, returning 404.

```bash
# ❌ WRONG — dotenv reads "# 快速版 接入点 ID" as the value
ARK_ENDPOINT_FAST=          # 快速版 接入点 ID

# ✅ CORRECT — comment on preceding line, or comment out entire line
# 快速版 接入点 ID（留空使用默认模型）
#ARK_ENDPOINT_FAST=
```

The tool now strips `#` comments and validates model ID format as defense-in-depth.

## Seedance 2.0 — Video Generation

### API Flow

Async: submit → poll → download. Uses Volcengine Ark REST API (not SDK).

```
POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
GET  https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}
```

### Model Variant Constraints

| Parameter | Standard | Fast |
|-----------|:--:|:--:|
| Max resolution | 1080p | 720p |
| `draft` (preview mode) | ✅ 480p | ❌ 400 error |
| `seed` | ❌ ignored | ❌ ignored |
| `service_tier: flex` | ❌ ignored | ❌ ignored |
| `return_last_frame` | ✅ | ✅ |
| `generate_audio` | ✅ | ✅ |

`draft`, `seed`, `service_tier` are Seedance 1.x parameters. 2.0 rejects or ignores them.
`draft` + fast → 400 "the specified parameter draft is not supported for model X in t2v".

### Resolution + Variant Validation

```python
# Invalid combinations the tool already catches:
# - fast + 1080p → error
# - draft + non-480p → error
# - draft + fast → 400 from API (not yet caught by tool — consider adding validation)
```

### Performance Benchmarks

| Variant | Res | Dur | Audio | Wall Time | ~Cost (USD) |
|---------|-----|-----|-------|-----------|------|
| Fast | 720p | 5s | No | ~100s | ~$0.18 |
| Fast | 720p | 5s | Yes | ~167s | ~$0.32 |
| Standard | 720p | 5s | Yes | ~120-300s | ~$0.45 |
| Standard | 1080p | 5s | Yes | ~120-300s | ~$0.65 |

Audio generation adds ~60s wall time and roughly doubles cost.
Draft mode (standard only, 480p): ~60s, ~60% of normal cost — use for prompt validation.

### Prompt Guidance

- **Language:** Chinese prompts work best (native Mandarin understanding).
  English also well-supported. Japanese, Indonesian, Spanish, Portuguese also documented.
- **Camera direction:** Use terms like "无人机航拍" (drone), "推镜" (dolly in),
  "跟拍" (tracking), "特写" (close-up), "慢动作" (slow motion).
- **Cinematic quality:** Add "电影感" (cinematic), "4K", "高画质" (high quality),
  "暖色调" (warm tones), "柔和焦外" (soft bokeh).
- **Audio:** When `generate_audio=True`, the model generates synced ambient sound,
  speech (from quoted dialogue in prompt), and basic SFX.
- **Duration:** 5s is the sweet spot. Longer durations increase cost linearly but
  don't always improve quality.

### Endpoint ID Override

Optional — set `ARK_ENDPOINT_STANDARD` / `ARK_ENDPOINT_FAST` to `ep-xxx` endpoint
IDs from the Volcengine console to route through custom inference endpoints.
When set, these override the default model name strings.

## Seedream — Image Generation

### API Flow

Synchronous REST API. No polling needed.

```
POST https://ark.cn-beijing.volces.com/api/v3/images/generations
```

### Model Choice

| Variant | Best For | Speed | Cost |
|---------|----------|-------|------|
| `5_0` | Best quality, latest capabilities | Normal | Normal |
| `5_0_lite` | Fast & cheap, good enough quality | Fast | Low |
| `4_5` | Previous gen, stable | Normal | Normal |
| `4_0` | Mature, reliable fallback | Normal | Low |

### Size Options

| Keyword | Resolution | ~Cost (USD) |
|---------|-----------|------|
| `2K` | 1024×1024 | ~$0.01 |
| `3K` | 1536×1536 | ~$0.01 |
| `4K` | 2048×2048 | ~$0.01 |

Custom `WxH` also supported (total pixels 3,686,400–16,777,216).

### Performance

- 2K image: ~13s (Seedream 4.0), ~15-30s (5.0)
- 3K/4K: ~25s+
- `output_format` (png vs jpeg) only available on 5.0 and 5.0 lite

### Prompt Guidance

- **Chinese prompts:** Native understanding. Detail-rich descriptions produce best results.
- **Style keywords:** "写实" (photorealistic), "插画风格" (illustration), "赛博朋克" (cyberpunk),
  "水墨画" (ink wash), "油画" (oil painting).
- **Composition:** "广角" (wide angle), "特写" (close-up), "浅景深" (shallow DOF),
  "对称构图" (symmetrical composition).
- **Image-to-image:** Pass `image_url` or `image_path` for reference-based generation.

## When NOT to Use Volcengine

- User doesn't have Alipay/Chinese payment → suggest fal.ai (`FAL_KEY`) or HeyGen (`HEYGEN_API_KEY`)
- Need real-time generation → both tools have 13s-180s latency
- Budget-constrained without Volcengine account → suggest free stock (Pexels/Pixabay)
- Need >15s video clips → Seedance 2.0 max is 15s
- Need 4K video → Seedance max is 1080p
