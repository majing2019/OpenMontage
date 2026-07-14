# Asset Director — Healing Text Pipeline

## 0. Asset Mode Routing (READ FIRST)

**Before starting any asset work, read `script.metadata.asset_mode`:**

- If `asset_mode == "ai-generated"` (or not set — default): Continue with
  the existing two-phase AI generation workflow below (Sections 1-2 +
  Phase 1-2).
- If `asset_mode == "stock-footage"`: Skip to **Section S: Stock-Footage
  Workflow** at the end of this document. The AI generation sections do
  not apply.

The two workflows share only the manifest-writing convention and the
quality gate check. Everything else differs.

**Also check `script.metadata.tts_enabled`:**

- If `tts_enabled == true`: After completing the standard asset workflow
  (Phase 1-2 for ai-generated, or Section S for stock-footage), proceed to
  **Section T: TTS Narration Generation** below.
- If `tts_enabled == false` (or not set — default): Skip Section T entirely.
  The pipeline proceeds unchanged.

## When To Use

The script is segmented and approved with motion priorities assigned.
**ALL video clips are produced via image_to_video — never text_to_video.**
This gives maximum control over composition (Seedream nails the frame) and
lets Seedance focus on what it does best: adding natural, subtle motion.

Production runs in TWO phases with a mandatory user approval gate between them:

**Phase 1 — Still Images:** Every segment gets a cinematic still image via Seedream.
The user reviews and approves ALL images before any video generation.

**Phase 2 — Image-to-Video:** Only `video` and `animate` segments proceed to
image_to_video. `still` segments stop at Phase 1. The approved image is the
first frame — Seedance adds motion.

| Priority | Phase 1 (all segments) | Phase 2 (video/animate only) |
|----------|----------------------|------------------------------|
| `video` | Seedream still (cinematic, 2560×1440) | `seedance_volcengine` image_to_video (5s, 1080p) |
| `animate` | Seedream still (cinematic, 2560×1440) | `seedance_volcengine` image_to_video (4s, 1080p) |
| `still` | Seedream still (cinematic, 2560×1440) | _(none — still image is the final asset)_ |

All assets must be silent (no audio tracks). All must support subtitle overlay.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/asset_manifest.schema.json` | Artifact validation |
| Prior artifact | `state.artifacts["script"]["script"]` | Segments + motion priorities + keywords |
| Tools | `seedance_volcengine`, `image_selector`, `direct_clip_search`, `pexels_video`, `pexels_image`, `pixabay_video`, `pixabay_image`, `video_selector` | Generation and stock |
| Layer 3 skills | `.agents/skills/healing-text-prompt-guide/SKILL.md` (**MANDATORY**), `.agents/skills/seedance-2-0/SKILL.md`, `.agents/skills/fpv-video-prompting/SKILL.md`, `.agents/skills/seedream-prompt-patterns/`, `.agents/skills/visual-taste/SKILL.md`, `.agents/skills/ai-video-gen/SKILL.md`, `.agents/skills/volcengine-ark/SKILL.md` | Provider-specific prompt craft + healing-text exclusive templates |

## Stock Sourcing Strategy

Free stock is the fallback layer. Three sources, queried in priority order:

| Priority | Tool | Sources | Content |
|:---:|------|--------|---------|
| 1 | `direct_clip_search` | **Unsplash + Pexels** + archive.org + NASA + Wikimedia | 图片 + 视频，一次搜索覆盖多个源 |
| 2 | `pexels_image` / `pexels_video` | Pexels only | 单独搜 Pexels（当 direct_clip_search 不够精确时） |
| 3 | `pixabay_image` / `pixabay_video` | Pixabay only | 单独搜 Pixabay（前两个都找不到时兜底） |

`direct_clip_search` is the preferred stock tool — it queries Unsplash and Pexels
simultaneously, and Unsplash's photography quality is the best match for the
cinematic healing aesthetic. Use it first. Fall back to individual searches only
when you need more control over results.

## 0. Cinematic Prompt Engineering Guide (READ FIRST)

> **NOTE:** This section (Section 0) applies ONLY when `selected_playbook` is
> `cinematic-drama` or not set. For `warm-illustration` and `literary-illustration`,
> skip to **Section 0.5: Style-Aware Asset Strategy** below.

**The authoritative prompt engineering guide for this pipeline is now in `.agents/skills/healing-text-prompt-guide/SKILL.md`.**

The guide below is kept as a quick reference for lighting and film stock terminology.
ALWAYS prefer the healing-text-prompt-guide patterns (Chinese-language, time-segmented,
concrete scene descriptions) over the English cinematic formula below when writing
actual generation prompts.

### Quick Reference: Lighting Catalog

Healing content lives in natural, atmospheric light. Pick the lighting that
matches the segment's emotional mood:

| Mood | Lighting | Prompt Fragment |
|------|----------|----------------|
| 温暖/希望 | Golden hour backlight | `golden hour backlight, warm rim light on subject, soft amber glow, long shadows` |
| 安静/忧郁 | Blue hour twilight | `blue hour twilight, cool ambient light, distant warm lights, calm stillness` |
| 平和/治愈 | Overcast soft diffused | `overcast soft diffused light, no harsh shadows, even natural illumination, peaceful` |
| 内省/沉思 | Window light | `light streaming through window, dust motes in sunbeams, chiaroscuro, quiet interior` |
| 梦幻/朦胧 | Misty atmospheric | `misty atmospheric light, god rays through fog, ethereal glow, layers of haze` |
| 安全感/温暖 | Rain + tungsten | `rain on window, soft bokeh city lights through wet glass, cool tungsten glow, cozy` |
| 静谧/神圣 | Forest dappled | `dappled sunlight filtering through tree canopy, soft forest floor glow, sacred quiet` |

### Lens & Film Parameters (Always Include)

These are the cinematic anchor — they tell the model "this is a photograph, not a
painting." Include this block in EVERY prompt:

```
shot on Hasselblad 500CM with 85mm lens at f/2.8,
shallow depth of field, soft bokeh in background,
anamorphic lens characteristics,
35mm film aesthetic
```

**Why each element matters:**
- `Hasselblad 500CM` — medium format film camera; triggers the model's association with professional photography
- `85mm f/2.8` — portrait focal length with natural compression; shallow DOF separates subject from background
- `anamorphic lens` — horizontal lens flares, oval bokeh, wider cinematic aspect; hallmark of movie frames
- `35mm film aesthetic` — analog texture, not digital perfection; the difference between "AI look" and "film look"

### Film Stock & Color Science (Pick One Per Video)

Choose ONE film stock reference for the entire video. All segments share it for
visual consistency:

| Film Stock | Color Character | Best For |
|-----------|----------------|----------|
| `Kodak Portra 400 color science, warm pastel tones` | 暖色柔和，肤色奶油感 | 温暖怀旧、阳光治愈 |
| `Fujifilm Pro 400H, soft greens and blues, pastel` | 青绿柔和，日系清新 | 安静、森林、雨景 |
| `cinematic color grading, teal and orange, warm mids` | 好莱坞电影调色 | 气势、史诗感、力量 |
| `Kodak Ektachrome, cool shadows, crisp highlights` | 冷调通透，高光锐利 | 冬季、雪景、孤独美 |
| `cinematic desaturated, muted tones, low contrast` | 低饱和、柔和对比 | 沉思、忧郁、安静的力量 |

### Post-Processing (Always Include)

```
fine film grain, subtle vignette, pro-mist 1/4 diffusion filter,
warm color grading, 8K resolution, photorealistic,
negative space in upper third for text overlay
```

### Complete Image Prompt Templates

Use these as starting points. Replace `[scene]` with the segment's visual keywords,
and pick the lighting + film stock that matches the mood.

**Template A — Golden Hour / Warm (hope, peace, gratitude):**
```
Cinematic photography, [scene], golden hour backlight, warm rim light, soft amber
glow, negative space in upper third for text overlay, shot on Hasselblad 500CM
with 85mm lens at f/2.8, shallow depth of field, anamorphic lens, 35mm film
aesthetic, Kodak Portra 400 color science, fine film grain, subtle vignette,
pro-mist 1/4 diffusion, 8K resolution, photorealistic
```

**Template B — Blue Hour / Cool (quiet, reflection, solitude):**
```
Cinematic photography, [scene], blue hour twilight, cool ambient light, distant
warm lights on horizon, negative space in upper third for text overlay, shot on
Hasselblad 500CM with 85mm lens at f/2.8, shallow depth of field, anamorphic lens,
35mm film aesthetic, Fujifilm Pro 400H color science, fine film grain, subtle
vignette, pro-mist 1/4 diffusion, 8K resolution, photorealistic
```

**Template C — Mist/Atmospheric (dream, memory, ethereal):**
```
Cinematic photography, [scene], misty atmospheric light, god rays through soft fog,
ethereal layers of haze, negative space in upper third for text overlay, shot on
Hasselblad 500CM with 85mm lens at f/2.8, shallow depth of field, anamorphic lens,
35mm film aesthetic, Kodak Portra 400 color science, fine film grain, pro-mist 1/4
diffusion, dreamy soft focus, 8K resolution, photorealistic
```

**Template D — Rain/Interior (cozy, safe, introspective):**
```
Cinematic photography, [scene], rain on window, soft bokeh lights through wet glass,
warm tungsten interior glow against cool exterior, negative space in center for text
overlay, shot on Hasselblad 500CM with 50mm lens at f/1.4, very shallow depth of
field, anamorphic lens, 35mm film aesthetic, cinestill 800T color science, fine film
grain, cozy intimate atmosphere, 8K resolution, photorealistic
```

### Visual Consistency Anchor (CRITICAL)

Every image in the same video MUST share an identical suffix. Before generating
any assets, build the `CINEMATIC_SUFFIX` for this project by picking ONE lighting
type + ONE film stock. Then append it to every prompt:

```python
# Build ONCE per project, reuse for ALL segments
CINEMATIC_SUFFIX = """
shot on Hasselblad 500CM with 85mm lens at f/2.8,
shallow depth of field, anamorphic lens, 35mm film aesthetic,
{picked_film_stock} color science, fine film grain, subtle vignette,
pro-mist 1/4 diffusion, 8K resolution, photorealistic
"""

# Each segment only varies the scene + lighting
seg_prompt = f"{segment_scene}, {segment_lighting}, negative space in upper third for text overlay, {CINEMATIC_SUFFIX}"
```

### Common Cinematic Failures & Fixes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Image looks "too clean" / AI-ish | Missing texture parameters | Add `fine film grain, subtle vignette, analog photography feel` |
| Drifts into illustration/cartoon | Missing photography anchors | Add `photorealistic, shot on Hasselblad, 35mm film aesthetic, documentary photography` |
| No room for subtitles | Missing negative space instruction | Add `negative space in upper third for text overlay` (position based on subtitle placement) |
| Colors feel cold and digital | Missing film stock reference | Add `Kodak Portra 400 color science, warm color grading` or pick another film stock |
| Flat lighting, no depth | Missing light source + DOF | Add specific light direction (`backlight from left`) + `shallow depth of field at f/2.8` |
| Surreal/abstract instead of real scene | Prompt too poetic | Replace abstract concepts with camera-capturable descriptions: "loneliness" → "single chair by window at dusk" |
| Image too busy/distracting | Missing focal point | Add `simple composition, single focal element, uncluttered background` |

---

## 0.5. Style-Aware Asset Strategy

The asset generation approach depends on `script.metadata.selected_playbook`.
Read the selected playbook from `styles/` directory FIRST — it provides the
`image_prompt_prefix`, `image_negative_prompt`, and `style_lock` keywords.

### If warm-illustration (Style A — 治愈插画风)

- **Playbook**: `styles/warm-illustration.yaml`
- **Image prompt prefix** (from playbook): `温暖插画风格, 柔和色调, 手绘质感, 日式生活插画, 温馨氛围, 柔和线条, 柔和自然光, 午后暖阳`
- **Negative prompt** (from playbook): `photorealistic, 3D render, photograph, realistic photo`
- **Color palette**: 米色/浅橙 primary, 深棕/焦糖 accent, 暖白 (#FFF8F0) background
- **Quality check**: Soft hand-drawn texture is CORRECT. Do NOT reject illustration quality.
- **Text area**: Large negative space in center-top of image
- **Prompt template**: Use healing-text-prompt-guide Template D (§1.4)

### If literary-illustration (Style B — 文学摄影风)

- **Playbook**: `styles/literary-illustration.yaml`
- **Image prompt prefix** (from playbook): `轻文艺插画风格, 莫兰迪灰调配色, 奶油纸张底色, 炭灰色手工线条, 大面积留白, 静谧克制氛围, 做旧纸质肌理, 极简角色设计, 散文书籍插画质感`
- **Negative prompt** (from playbook): `photorealistic, 3D render, photograph, bright neon, vibrant, pure black, pure white, cartoon, anime, heavy lines`
- **Color palette**: 莫兰迪灰调 primary, 低饱和 accent, 奶油纸色 (#F5F0EB) background
- **Quality check**: Morandi palette, cream paper, hand-drawn lines are CORRECT. Reject vivid colors.
- **Text area**: Large white space (大面积留白) in center of image
- **Prompt template**: Use healing-text-prompt-guide Template E (§1.4)

### If cinematic-drama (Original — backward compatible)

- Use Section 0 cinematic templates unchanged (Hasselblad, film stock, photorealistic).
- All requirements from the original asset director apply.

### Illustration-Style Video Motion

For illustration styles, image_to_video motion should be even more restrained than
cinematic. The illustration aesthetic is inherently static — motion should feel like
a gentle breath, not camera work:

```
One continuous shot, locked tripod, completely static camera —
no push-in, no dolly, no pan, no tilt, no zoom, no cuts,
no handheld movement of any kind.
Gentle illustration motion — elements sway subtly, light shifts slowly.
No 3D, no photorealistic rendering — maintain hand-drawn illustration aesthetic.

Beat-by-beat:
0-2s: Absolute stillness. The illustration is alive but frozen.
2-4s: ONE subtle element begins to move — [leaves rustle / steam rises / light shifts].
Movement is barely perceptible, like a deep breath.
4-5s: Motion STABILIZES. Frame returns to near-stillness.

No music, no audio — silent clip.
```

---

## Asset Strategy — Image-First (Two-Phase)

**ALL videos are image_to_video.** Never text_to_video in this pipeline.
Seedream controls the frame. Seedance adds motion. This separation of concerns
produces dramatically more consistent, cinematic results for landscape footage.

```
Phase 1                    Phase 2
───────                    ───────
all 6 segments       →     USER APPROVAL GATE (MANDATORY)
  │                         │
  └─ Seedream still image   ├─ video segments   → seedance image_to_video (5s)
     (2560×1440, 16:9)     ├─ animate segments → seedance image_to_video (4s)
                            └─ still segments   → done (still image is final)

Fallback (if image_to_video fails): pexels_video stock footage
Fallback (if image generation fails): pexels_image stock photo
```

**The approval gate between phases is MANDATORY.** The user must see and approve
every still image before a single video frame is generated. This prevents wasting
video generation budget on images the user doesn't like.

## Process

### 0. Read Healing-Text Prompt Guide (MANDATORY — DO NOT SKIP)

**BEFORE writing ANY image or video prompt, read `.agents/skills/healing-text-prompt-guide/SKILL.md`.**

Key rules:
1. ALL prompts MUST be in Chinese — Seedance/Seedream are Chinese-native models
2. Image prompts: concrete scene descriptions (清晨五点半 > dawn), layered detail
3. Video prompts: describe ONLY motion, not the scene (the image already defines the scene)
4. Every prompt MUST include negative constraints
5. Specify exact time of day and weather — be specific

### 1. Read Layer 3 Skills (MANDATORY)

```bash
python -c "
from tools.tool_registry import registry
registry.discover()
tool = registry.get('seedance_volcengine')
print('Skills:', tool.agent_skills)
"
```

Read `.agents/skills/seedance-2-0/SKILL.md` and `.agents/skills/ai-video-gen/SKILL.md`.

---

## Phase 1 — Generate All Still Images

### Phase 1.1: Write Image Prompts

**Read the selected playbook from script metadata FIRST.**

- If `selected_playbook` is `warm-illustration` or `literary-illustration`:
  - Use the playbook's `asset_generation.image_prompt_prefix` as the STYLE ANCHOR for every prompt
  - Use the playbook's `asset_generation.image_negative_prompt` as negative constraints
  - Append `style_lock` keywords from the playbook (if it has them — `literary-illustration` does)
  - Follow `.agents/skills/healing-text-prompt-guide/SKILL.md` Template D or E (§1.4)
  - Write ALL prompts in Chinese (as the prompt guide requires)
  - Specify `画面中央偏上大面积留白用于叠加文字` (negative space at center-top for text)
  - Do NOT include photography terms (Hasselblad, 35mm, film grain, photorealistic, 8K)

- If `selected_playbook` is `cinematic-drama` or not set:
  - Follow `.agents/skills/healing-text-prompt-guide/SKILL.md` Templates A/B/C (§1.2)
  - Use Section 0 cinematic templates (Hasselblad, film stock, etc.)
  - `画面上方三分之一留白` for text overlay

Every prompt includes (regardless of style):
- Concrete scene description in Chinese (time, place, weather, season)
- Lighting direction and quality
- Composition and negative space for text overlay
- Color palette matching the selected playbook

### Phase 1.2: Generate via Seedream

```python
seedream = registry.get('seedream_volcengine')
result = seedream.execute({
    "prompt": "<Chinese scene description>",
    "size": "2560x1440",
    "output_path": "projects/<proj>/assets/images/seg_XX.png",
})
```

Generate ALL segments — `video`, `animate`, and `still` — as still images first.

### Phase 1.3: Image Quality Check (Style-Aware)

- [ ] Resolution is 2560×1440 (cinematic) or 1440×2560 (illustration native for 9:16)
- [ ] **Style A (warm-illustration)**: Soft hand-drawn texture, warm palette, intentionally non-photorealistic ✓
- [ ] **Style B (literary-illustration)**: Morandi palette, cream paper texture, visible hand-drawn lines ✓
- [ ] **cinematic-drama**: Photorealistic — no cartoon, no 3D, no illustration drift
- [ ] Negative space in designated area for text overlay (center-top for illustration, upper third for cinematic)
- [ ] Color palette matches the selected playbook's palette
- [ ] No people (unless explicitly requested)
- [ ] Visual quality matches the selected style — illustration should look illustrated, not photographic

**Remediation:** Bad image → retry with adjusted prompt (max 1 retry).
Retry failed → fall back to pexels_image.

### Phase 1.4: USER APPROVAL GATE (MANDATORY)

Present ALL generated images to the user. The user must explicitly approve
before any video generation begins. Show:
1. Each image with its segment text and motion priority
2. Which segments will receive image_to_video (video + animate)
3. Estimated video generation cost

**Do not proceed to Phase 2 until the user says yes.**

### Phase 1.5: Source Background Music

After images are approved but BEFORE video generation:

1. **Determine music mood** from the selected playbook and text emotional arc:

   | Selected Playbook | Search Query |
   |-------------------|-------------|
   | `warm-illustration` | `gentle piano warm soft healing emotional instrumental` |
   | `literary-illustration` | `ambient calm reflective minimal piano contemplative instrumental` |
   | `cinematic-drama` | `cinematic ambient atmospheric healing piano strings` |

2. **Search via pixabay_music** (free, no API key required):

```python
from tools.tool_registry import registry
registry.discover()
music_tool = registry.get('pixabay_music')
result = music_tool.execute({
    "query": "<style-specific mood query from table above>",
    "min_duration": 30,
    "max_duration": 300,
    "output_path": "projects/<proj>/assets/music/bg_music.mp3",
})
```

3. **User approval**: Present the music choice to the user. They can:
   - Approve the selected track
   - Request a different mood/genre (max 2 retries with new search queries)
   - Provide their own track via `music_library/` drop path
   - Skip music entirely (pipeline degrades gracefully to silent)

4. **Verify**: Music duration >= planned video duration. If shorter, note `loop: true`
   for compose stage configuration.

**Fallback**: If `pixabay_music` is unavailable or returns no results, offer the user
the option to drop an MP3 into `music_library/` or proceed without music.

---

## T: TTS Narration Generation (`tts_enabled == true`)

This section is shared by both ai-generated and stock-footage workflows.
Both workflows route here after completing their standard asset generation
and music sourcing steps.

### Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `state.artifacts["script"]["script"]` | Segment text for narration |
| Prior artifact | `state.artifacts["assets"]["asset_manifest"]` | Music asset path (for preview) |
| Tools | `tts_selector` | TTS generation with auto-provider routing |
| Agent Skill | `.agents/skills/text-to-speech` / `.agents/skills/elevenlabs` | Provider-specific prompting and voice guidance |

### T.1 Voice Selection

1. **Determine preferred TTS provider** based on text language:
   - Chinese text (detected from script sections): prefer `doubao_tts`
     (natural Mandarin, character-level timestamps)
   - Non-Chinese text: prefer `elevenlabs_tts` (multilingual, high quality)

2. **Use tts_selector with rank operation** to check provider availability:
   ```python
   from tools.tool_registry import registry
   registry.discover()
   tts = registry.get('tts_selector')
   result = tts.execute({
       "operation": "rank",
       "text": script.sections[0].text,
       "task_context": {"language": "zh", "style": "healing narration"}
   })
   ```

3. **Select voice_id** for the chosen provider:
   - doubao_tts: Use a warm, gentle female or male voice appropriate for
     healing content. Check `DOUBAO_SPEECH_VOICE_TYPE` env var or provider docs.
   - elevenlabs_tts: Use a calm, warm voice (e.g., "Matilda", "Charlie")

4. **Record voice selection** for the asset manifest metadata.

### T.2 Sample Preview (MANDATORY -- User Approval Gate)

Before batch-generating narration for all segments:

1. **Generate narration for the FIRST segment only**:
   ```python
   tts = registry.get('tts_selector')
   result = tts.execute({
       "text": script.sections[0].text,
       "voice_id": "<selected_voice>",
       "preferred_provider": "<doubao | elevenlabs>",
       "output_path": "projects/<proj>/assets/narration/seg_01_preview.mp3"
   })
   ```

2. **Play the sample for the user**. Present:
   - Voice quality and naturalness
   - Speaking pace (not too fast for healing content)
   - Emotional tone match with the text
   - Duration of the sample vs. planned segment duration

3. **If the user rejects**:
   - Try a different voice_id (max 3 attempts)
   - Try a different provider (e.g., switch from doubao to elevenlabs)
   - Adjust speech_rate parameter (doubao: -20 to -30 for slower, more contemplative pace)

4. **Do NOT proceed to batch generation until the user approves the voice.**

### T.3 Batch Generate Narration Per Segment

For each script section in order:

1. **Generate narration**:
   ```python
   tts = registry.get('tts_selector')
   result = tts.execute({
       "text": section.text,
       "voice_id": "<approved_voice>",
       "preferred_provider": "<approved_provider>",
       "speech_rate": -20,    # doubao_tts: slower for healing content
       "output_path": f"projects/<proj>/assets/narration/seg_{idx:02d}.mp3"
   })
   ```

2. **Verify duration**: Check `result.data["audio_duration_seconds"]` against
   the segment's planned duration. If narration is significantly longer (>120%)
   or shorter (<80%) than the planned segment, note this — the compose stage
   may need to adjust segment pacing.

3. **Store duration metadata** for compose stage timing.

### T.4 Record Narration Assets in Manifest

Add narration entries to the asset_manifest `assets` array:

```json
{
  "id": "narration_seg_01",
  "type": "audio",
  "subtype": "narration",
  "path": "assets/narration/seg_01.mp3",
  "source_tool": "tts_selector",
  "scene_id": "seg_01",
  "provider": "<doubao | elevenlabs>",
  "model": "<seed-tts-2.0 | eleven_multilingual_v2>",
  "duration_seconds": 4.2,
  "format": "mp3"
}
```

Add narration metadata to `asset_manifest.metadata`:

```json
"narration": {
    "enabled": true,
    "provider": "doubao",
    "voice_id": "<approved_voice>",
    "segments_generated": 5,
    "total_narration_duration_seconds": 22.5,
    "sample_approved": true
}
```

**If `tts_enabled == false`**, no narration entries or metadata are added.

### T.5 Quality Gate (narration)

- Narration generated for EVERY script segment
- All narration audio files exist on disk
- Durations are within 80-120% of planned segment durations
- Voice is consistent across all segments (same voice_id)
- `tts_enabled: true` and narration metadata recorded in manifest

---

## Phase 2 — Image-to-Video (Motion Segments Only)

Only `video` and `animate` segments proceed. `still` segments are done.

### Phase 2.1: Write Video Prompts

Video prompts describe ONLY the motion, not the scene. The image already
provides the composition. Follow the Higgsfield methodology from
`.agents/skills/seedance-2-0/SKILL.md`:

- Open with shot-structure declaration: `One continuous shot, locked tripod...`
- Camera negation: `no push-in, no dolly, no pan, no tilt, no zoom, no cuts`
- Beat-by-beat with ALL CAPS action markers: `RAMPS TO SLOW MOTION`, `DRIFTS`
- Realism enforcement: `no 3D, no cartoon, no VFX aesthetic`

### Phase 2.2: Generate Videos

**Video segments (5s):**
```python
result = seedance.execute({
    "prompt": "<motion-only description>",
    "operation": "image_to_video",
    "image_path": "projects/<proj>/assets/images/seg_XX.png",
    "model_variant": "standard",
    "duration": "5",
    "aspect_ratio": "16:9",
    "resolution": "1080p",
    "generate_audio": False,
    "output_path": "projects/<proj>/assets/video/seg_XX.mp4",
})
```

**Animate segments (4s):**
Same as above but `duration: "4"`.

### Phase 2.3: Video Quality Check

- [ ] Duration matches specification (5s for video, 4s for animate)
- [ ] NO audio track (verify with ffprobe)
- [ ] Resolution is 1080p (1920×1080)
- [ ] Motion is gentle, cinematic — not jerky, not surreal
- [ ] Composition matches the approved still image (it's the first frame)
- [ ] Photorealistic throughout — no AI-warping artifacts
- [ ] No camera movement unless explicitly described in prompt

**Remediation:** Bad video → retry with simplified motion description (max 1 retry).
Retry failed → fall back to pexels_video stock footage.

### Phase 2.4: Strip Audio (MANDATORY)

```bash
ffprobe -v error -show_entries stream=codec_type <video_file>
# If audio exists, strip it:
ffmpeg -i <video_file> -an -c:v copy <video_file>_silent.mp4
mv <video_file>_silent.mp4 <video_file>
```

---

## Write Asset Manifest

```json
{
  "version": "1.0",
  "assets": [
    {
      "id": "vid_seg_03",
      "type": "video",
      "path": "assets/video/seg_03.mp4",
      "source_image": "assets/images/seg_03.png",
      "source_tool": "seedance_volcengine",
      "operation": "image_to_video",
      "scene_id": "seg_03",
      "image_prompt": "<Chinese scene prompt>",
      "video_prompt": "<motion-only prompt>",
      "provider": "volcengine",
      "model": "doubao-seedance-2-0-260128",
      "subtype": "generated",
      "resolution": "1920x1080",
      "duration_seconds": 5.0
    },
    {
      "id": "img_seg_01",
      "type": "image",
      "path": "assets/images/seg_01.png",
      "source_tool": "seedream_volcengine",
      "scene_id": "seg_01",
      "prompt": "<Chinese scene prompt>",
      "provider": "volcengine",
      "model": "doubao-seedream-5-0-260128",
      "subtype": "generated",
      "resolution": "2560x1440"
    },
    {
      "id": "music_bg",
      "type": "music",
      "path": "assets/music/bg_music.mp3",
      "source_tool": "pixabay_music",
      "prompt": "<search query>",
      "provider": "pixabay",
      "license": "Pixabay Content License (free, no attribution required)",
      "duration_seconds": 120.0,
      "format": "mp3"
    }
  ],
  "metadata": {
    "asset_strategy": "image-first-two-phase",
    "selected_playbook": "<warm-illustration | literary-illustration | cinematic-drama>",
    "phase1_images_generated": 6,
    "phase2_videos_generated": 3,
    "all_audio_stripped": true,
    "music_source": "pixabay_music",
    "music_duration_seconds": 120.0
  }
}
```

## Quality Gate

- One asset per script segment (no gaps)
- `video` tier segments have actual .mp4 video files (image_to_video), not text_to_video
- ALL video clips verified silent (no audio tracks)
- All files exist on disk and are readable
- **Style A/B (illustration)**: Asset generation matches the selected playbook's visual language — images are intentionally non-photorealistic
- **cinematic-drama**: Photorealistic, cinematic aesthetic throughout — no cartoon, no 3D, no illustration
- Color palette consistent across all images (matches selected playbook)
- All video clips match their approved source image composition
- Music asset exists and duration covers video length (if music was approved)
- `selected_playbook` is recorded in asset manifest metadata

## Common Pitfalls

- Using text_to_video instead of image_to_video — text_to_video is FORBIDDEN in this pipeline
- Skipping the Phase 1 → Phase 2 approval gate — user MUST approve images before video gen
- Writing video prompts that re-describe the scene — only describe motion
- Image_to_video producing unnatural warping — use simpler, slower motion descriptions
- Not reading Layer 3 skills → generic prompts → wasted generation budget

---

## S: Stock-Footage Workflow (`asset_mode == "stock-footage"`)

### S.0 Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `state.artifacts["script"]["script"]` | Segments + stock search keywords from `visual_keywords_image` |
| Tools | `direct_clip_search`, `color_grade`, `pixabay_music`, `pexels_video`, `pixabay_video` | Stock search + color grading + music |
| Stock adapters | `tools/video/stock_sources/` (15 sources) | Pexels, Pixabay Video, Coverr, Unsplash, etc. |

Read `script.metadata.visual_direction.<seg_id>.visual_keywords_image` for
search query construction. The script director writes these as English
concrete search terms for stock-footage mode (not Chinese AI prompts).

### S.1 Phase 1: Stock Search (Dual Orientation)

For EACH script segment, search for video clips in BOTH orientations.
**Why separate searches:** The same stock clip rarely works for both
16:9 and 9:16. Searching separately with orientation filters ensures
each aspect ratio gets properly framed footage.

#### S.1.1 Construct Search Queries

Read `visual_keywords_image` from each segment's visual_direction.
These should already be English concrete terms from the script stage.
Add orientation-appropriate modifiers:

| Keyword | Horizontal Query | Vertical Query |
|---------|-----------------|----------------|
| "misty forest path morning sunlight" | "misty forest path morning sunlight wide landscape nature" | "misty forest sunlight vertical portrait nature" |
| "rain on window cozy warm interior" | "rain on window cozy warm interior" | "rain window closeup vertical drops glass" |

Keep queries short (3-6 words) — stock APIs match better with fewer keywords.

#### S.1.2 Run direct_clip_search — Horizontal (16:9)

```python
direct_clip_search = registry.get('direct_clip_search')
h_result = direct_clip_search.execute({
    "output_dir": "projects/<proj>/assets/video/horizontal",
    "queries": [
        {"query": "misty forest path morning sunlight landscape", "slot_id": "seg_01", "kind": "video"},
        {"query": "cozy rain on window warm interior", "slot_id": "seg_02", "kind": "video"},
        # ... one query per segment
    ],
    "sources": ["pexels", "pixabay_video", "coverr"],
    "clips_per_query": 3,
    "filters": {
        "orientation": "landscape",
        "min_duration": <segment_duration_seconds>,
        "min_width": 1920
    },
    "extract_thumbnails": True,
    "skip_existing": True
})
```

**Source priority:** `pexels` first (largest catalogue, best quality), then
`pixabay_video` (community clips, broad coverage), then `coverr` (free HD
nature/cinematic).

#### S.1.3 Run direct_clip_search — Vertical (9:16)

```python
v_result = direct_clip_search.execute({
    "output_dir": "projects/<proj>/assets/video/vertical",
    "queries": [
        {"query": "misty forest sunlight vertical portrait nature", "slot_id": "seg_01", "kind": "video"},
        {"query": "rain window closeup vertical glass drops", "slot_id": "seg_02", "kind": "video"},
        # ... one query per segment
    ],
    "sources": ["pexels", "pixabay_video", "coverr"],
    "clips_per_query": 3,
    "filters": {
        "orientation": "portrait",
        "min_duration": <segment_duration_seconds>,
        "min_width": 1080
    },
    "extract_thumbnails": True,
    "skip_existing": True
})
```

**Important note on Pixabay orientation:** The Pixabay Video API does NOT
support server-side orientation filtering. `direct_clip_search` applies
orientation filtering client-side using width/height ratio. This means
searches filtered via `orientation: "portrait"` may receive fewer results
from pixabay_video than expected.

#### S.1.4 Handle Search Failures

If a segment returns zero clips for a given orientation:
1. **Broaden the query** — remove specific modifiers, try more generic terms
2. **Try additional sources:** `["pexels", "pixabay_video", "coverr", "mixkit", "unsplash"]`
3. **Still nothing?** Flag segment for manual review, note in manifest
4. **Last resort:** Reuse a clip from another segment with similar mood

### S.2 Phase 2: Clip Selection + Color Grade

#### S.2.1 Present Clips for Human Selection

**The agent does NOT pick clips. The human does.** After search completes,
present the clips directory to the user and let them watch the actual
video files to decide.

**Step 1 — Open the clips folder so the user can watch videos:**

```bash
# macOS
open projects/<proj>/assets/video/horizontal/clips/
open projects/<proj>/assets/video/vertical/clips/
```

**Step 2 — Print the slot-to-clip mapping** (from `direct_clip_search` result data)
so the user knows which clip belongs to which segment:

```
=== HORIZONTAL ===
seg_01 | pexels_36026712 | 8.0s | https://www.pexels.com/video/majestic-foggy-mountain-...
seg_01 | pexels_34659069 | 26.0s | https://www.pexels.com/video/majestic-drone-view-...
seg_01 | pexels_29392993 | 10.0s | https://www.pexels.com/video/misty-mountains-...
seg_02 | pexels_36408448 | 12.0s | https://www.pexels.com/video/water-drops-on-glass-...
...
```

The user can:
- Watch the `.mp4` files directly in Finder/Explorer (Quick Look on macOS, press Space)
- Click the source URLs to see the clip on Pexels/Pixabay with full context
- Compare clips side by side

**Step 3 — Ask the user to pick one clip per segment per orientation.** The user
tells the agent: "For seg_01 horizontal, use pexels_36026712. For seg_01 vertical,
use pexels_34142319." etc.

**Step 4 — The agent copies the selected clips** into `selected/` named by segment ID:

```bash
cp projects/<proj>/assets/video/horizontal/clips/<user_selected_clip>.mp4 \
   projects/<proj>/assets/video/horizontal/selected/seg_01.mp4
```

#### S.2.2 Apply Color Grade

Apply `cinematic_warm` grade to ALL selected clips for visual consistency.
Different stock sources have different color profiles — grading unifies them.

```python
color_grade = registry.get('color_grade')
for seg_id in ["seg_01", "seg_02", ...]:
    for orientation in ["horizontal", "vertical"]:
        color_grade.execute({
            "input_path": f"projects/<proj>/assets/video/{orientation}/selected/{seg_id}.mp4",
            "output_path": f"projects/<proj>/assets/video/{orientation}/graded/{seg_id}.mp4",
            "profile": "cinematic_warm",
            "intensity": 0.8,
            "codec": "libx264",
            "crf": 18
        })
```

**Why intensity 0.8:** Full intensity (1.0) can look over-processed with
stock footage. 0.8 provides perceptible warm unity without looking
artificial. The blend filter in `color_grade` handles this natively.

**Verification:** Spot-check 2-3 graded vs original clips to confirm
warmth is perceptible but not heavy-handed. The goal is visual
CONSISTENCY, not a dramatic look.

#### S.2.3 Strip Audio (MANDATORY)

All stock clips must be silent before compose:

```bash
for ori in horizontal vertical; do
  for seg in assets/video/${ori}/graded/seg_*.mp4; do
    has_audio=$(ffprobe -v error -show_entries stream=codec_type "$seg" | grep -c audio || true)
    if [ "$has_audio" -gt 0 ]; then
      ffmpeg -i "$seg" -an -c:v copy "${seg}.silent.mp4" -y && mv "${seg}.silent.mp4" "$seg"
    fi
  done
done
```

### S.3 Phase 3: Music

#### S.3.1 Try pixabay_music First

```python
music_tool = registry.get('pixabay_music')
result = music_tool.execute({
    "query": "<mood-based query from playbook>",
    "min_duration": <total_video_duration_seconds>,
    "max_duration": 300,
    "output_path": "projects/<proj>/assets/music/bg_music.mp3",
})
```

**Music mood mapping:**

| Selected Playbook / Style | Search Query |
|---------------------------|-------------|
| `warm-illustration` | `gentle piano warm soft healing emotional instrumental` |
| `literary-illustration` | `ambient calm reflective minimal piano contemplative instrumental` |
| `cinematic-drama` | `cinematic ambient atmospheric healing piano strings` |

#### S.3.2 Music Fallbacks (if pixabay_music unavailable)

Attempt in order:
1. **music_gen (ElevenLabs):** `registry.get('music_gen')` — requires ELEVENLABS_API_KEY
2. **suno_music:** `registry.get('suno_music')` — requires SUNO_API_KEY
3. **No music — graceful degradation:** Mark `music_absent: true` in manifest.
   Compose stage will produce a silent video. This is acceptable for
   stock-footage mode (not a pipeline failure).

#### S.3.3 User Approval

Present music selection to user. They can:
- Approve the selected track
- Request a different mood (max 2 retries)
- Provide their own track via `music_library/` drop path
- Skip music entirely

**If `tts_enabled == true`:** After music approval, proceed to **Section T: TTS
Narration Generation** (above) for voice selection and narration batch generation.
Return here for the Section S.4 approval gate with narration assets included.

### S.4 USER APPROVAL GATE (MANDATORY — After Phase 2)

Present ALL selected + graded clips to the user. Show:
1. Thumbnail grid for each segment (horizontal + vertical side by side)
2. Source attribution (Pexels/Pixabay/Coverr, creator name, license type)
3. Duration check: each clip covers its segment duration
4. Color grade confirmation (cinematic_warm, intensity 0.8)
5. Music selection (or "no music — silent video" if degraded)

**Do not proceed to compose until the user approves.**

### S.5 Write Asset Manifest

```json
{
  "version": "1.0",
  "assets": [
    {
      "id": "seg_01_horizontal",
      "type": "video",
      "path": "assets/video/horizontal/graded/seg_01.mp4",
      "source_tool": "direct_clip_search",
      "scene_id": "seg_01",
      "provider": "pexels",
      "subtype": "stock",
      "license": "Pexels License (free, no attribution required)",
      "original_url": "https://www.pexels.com/video/...",
      "resolution": "1920x1080",
      "duration_seconds": 9.0,
      "segment_duration_seconds": 6.0,
      "color_graded": true,
      "grade_profile": "cinematic_warm",
      "grade_intensity": 0.8,
      "audio_stripped": true
    },
    {
      "id": "seg_01_vertical",
      "type": "video",
      "path": "assets/video/vertical/graded/seg_01.mp4",
      "source_tool": "direct_clip_search",
      "scene_id": "seg_01",
      "provider": "pexels",
      "subtype": "stock",
      "license": "Pexels License (free, no attribution required)",
      "original_url": "https://www.pexels.com/video/...",
      "resolution": "1080x1920",
      "duration_seconds": 7.5,
      "segment_duration_seconds": 6.0,
      "color_graded": true,
      "grade_profile": "cinematic_warm",
      "grade_intensity": 0.8,
      "audio_stripped": true
    },
    {
      "id": "music_bg",
      "type": "music",
      "path": "assets/music/bg_music.mp3",
      "source_tool": "pixabay_music",
      "prompt": "cinematic ambient atmospheric healing piano strings",
      "provider": "pixabay",
      "license": "Pixabay Content License (free, no attribution required)",
      "duration_seconds": 120.0,
      "format": "mp3"
    }
  ],
  "metadata": {
    "asset_mode": "stock-footage",
    "asset_strategy": "dual-orientation-stock-search",
    "selected_playbook": "<from script.metadata>",
    "stock_sources_used": ["pexels", "pixabay_video", "coverr"],
    "all_audio_stripped": true,
    "all_color_graded": true,
    "grade_profile": "cinematic_warm",
    "grade_intensity": 0.8,
    "music_source": "pixabay_music",
    "music_duration_seconds": 120.0,
    "music_absent": false,
    "total_horizontal_clips": 6,
    "total_vertical_clips": 6
  }
}
```

**Key differences from AI-generated asset manifest:**
- `subtype: "stock"` instead of `"generated"`
- `provider`, `license`, `original_url` populated for every asset
- `color_graded`, `grade_profile`, `grade_intensity` fields on each clip
- `segment_duration_seconds` hints for trim in compose stage
- No `image_prompt` or `video_prompt` fields (no AI generation)
- Dual orientation: separate asset entries for horizontal and vertical
- `asset_mode: "stock-footage"` in metadata

### S.6 Quality Gate (stock-footage)

- One video asset per segment per orientation (no gaps)
- ALL clips are stock video (subtype: "stock"), no AI-generated assets
- ALL video clips verified silent (no audio tracks)
- All graded clips exist on disk (graded/ directory)
- Color grade applied to ALL clips with consistent profile and intensity
- Resolution meets minimum: 1920x1080 horizontal, 1080x1920 vertical
- Music asset exists OR `music_absent: true` in manifest
- Every stock clip has `provider`, `license`, `original_url` recorded
- `asset_mode: "stock-footage"` recorded in manifest metadata

### S.7 Common Pitfalls (stock-footage)

- **Using Chinese or abstract search queries** → Pexels/Pixabay need English concrete terms. "清晨雾中山路" returns zero results; "misty forest morning path" works.
- **Expecting exact scene matches** → Stock libraries are finite. Be flexible — a close-enough mood clip is better than no clip.
- **Skipping orientation-specific search** → "Just crop the 16:9 video for 9:16" produces ugly results. Search separately.
- **Applying color grade at intensity 1.0** → Stock footage looks over-processed. Use 0.8.
- **Re-applying color grade in compose** → Grade is pre-applied in asset stage. Compose must NOT re-grade.
- **Forgetting to strip audio** → Stock clips often have ambient sound. Must strip before compose.
- **Treating missing music as pipeline failure** → Silent video is valid output. Mark `music_absent: true`.
