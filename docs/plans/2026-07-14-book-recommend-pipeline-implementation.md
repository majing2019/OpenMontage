# Book Recommend Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the `book-recommend` pipeline — a 4-stage pipeline for social-media book recommendation videos with dual AI-generated/stock-footage asset modes, dual 16:9/9:16 export, and mandatory book cover compositing.

**Architecture:** Follows the `healing-text` pipeline pattern: script → assets → compose → publish. The user provides narration text + book info; the pipeline segments it, retrieves book covers, generates or searches for visual assets, and composes via Remotion with a cover+visual+text layout system.

**Tech Stack:** YAML pipeline manifest, Markdown stage director skills, existing JSON artifact schemas (script, asset_manifest, render_report, publish_log), Remotion composition, existing tool registry (image_selector, video_selector, direct_clip_search, video_compose, audio_mixer, etc.)

---

### Task 1: Pipeline Manifest

**Files:**
- Create: `pipeline_defs/book-recommend.yaml`

**Step 1: Write the pipeline manifest**

Create `pipeline_defs/book-recommend.yaml` with the full manifest designed in the design doc:
- name, version, description, category, stability
- 4 modes: format_mode, asset_mode, music_enabled, tts_enabled
- orchestration config (agent-driven, $3 budget)
- required_skills and agent_skills
- transition_defaults with cover_layout, text_overlay, font_size_formula
- 4 stages: script, assets, compose, publish (all human_approval_default: true)
- Each stage with: skill path, produces, required_artifacts_in, tools_available, required_tools, review_focus, success_criteria

**Step 2: Validate manifest against schema**

```bash
python3 -c "
from lib.pipeline_loader import PipelineLoader
loader = PipelineLoader()
manifest = loader.load('book-recommend')
print('Pipeline loaded successfully:', manifest.name)
print('Stages:', [s['name'] for s in manifest.stages])
"
```

**Step 3: Commit**

```bash
git add pipeline_defs/book-recommend.yaml
git commit -m "feat: add book-recommend pipeline manifest

Four-stage pipeline for book recommendation videos.
Supports 4 modes: format_mode (single-book/book-list/themed-list),
asset_mode (ai-generated/stock-footage), music_enabled, tts_enabled.
All stages require human approval."
```

---

### Task 2: Script Director Skill

**Files:**
- Create: `skills/pipelines/book-recommend/script-director.md`

**Step 1: Write the script director skill**

Create the markdown file. Key sections:

1. **When To Use** — User provides narration text + book info. Agent segments text, assigns visual direction, plans motion priority, proposes fonts.

2. **Input** — User narration text, book metadata (title, author per book), format_mode selection

3. **Process:**
   - Receive and understand the text's emotional arc
   - **Format mode selection** — present single-book / book-list / themed-list options
   - **Asset mode selection** — ai-generated vs stock-footage
   - **Music & TTS toggles** — ask user (both default off)
   - Segment the text by natural pauses (3-8 segments)
   - Assign motion priority (peak=video, animate=image_to_video, still=image)
   - Extract visual keywords per segment (Chinese for AI, English for stock)
   - Extract book metadata per book (title, author, cover_search_query, quote)
   - Propose font shortlist (2-3 options matching mood)
   - Write script artifact per existing `schemas/artifacts/script.schema.json`

4. **Script artifact structure** — uses existing schema, extends metadata with:
   - `format_mode`, `asset_mode`, `music_enabled`, `tts_enabled`
   - `books[]` array with title, author, cover_search_query, quotes
   - `visual_direction` per segment (mood, motion_priority, visual_keywords_image, visual_keywords_video, color_palette)
   - `font_shortlist`, `selected_font`

5. **Quality Gate** — Checks from the manifest's review_focus

6. **Common Pitfalls**

**Step 2: Commit**

```bash
git add skills/pipelines/book-recommend/script-director.md
git commit -m "feat: add book-recommend script director skill"
```

---

### Task 3: Asset Director Skill

**Files:**
- Create: `skills/pipelines/book-recommend/asset-director.md`

**Step 1: Write the asset director skill**

Key sections:

1. **Asset Mode Routing** — Read `script.metadata.asset_mode`, route to AI-generated or stock-footage workflow

2. **Book Cover Retrieval (ALL modes)** — For every book:
   - Search for high-res cover via web search or book APIs
   - Download and normalize to consistent size
   - Verify cover matches the correct edition/language
   - Store in `projects/<proj>/assets/covers/`

3. **AI-Generated Workflow:**
   - Phase 1: Generate still images per segment via image_selector (preferring seedream)
   - Phase 1.5: User approval gate on all images
   - Phase 2: video-priority segments get image_to_video via video_selector/seedance
   - Music if enabled: pixabay_music
   - TTS if enabled: tts_selector

4. **Stock-Footage Workflow:**
   - Phase 1: direct_clip_search for each segment (dual orientation)
   - Phase 2: Present clips for human selection → color grade → strip audio
   - Music if enabled: pixabay_music
   - TTS if enabled: tts_selector

5. **Asset Manifest** — per existing schema, extended with:
   - `books[]` with cover paths and metadata
   - `asset_mode` in metadata
   - Cover assets as type "image" subtype "book_cover"

6. **Quality Gate** — Cover exists for every book, all assets on disk, music/tts present or explicitly absent

**Step 2: Commit**

```bash
git add skills/pipelines/book-recommend/asset-director.md
git commit -m "feat: add book-recommend asset director skill"
```

---

### Task 4: Compose Director Skill

**Files:**
- Create: `skills/pipelines/book-recommend/compose-director.md`

**Step 1: Write the compose director skill**

Key sections:

1. **When To Use** — Script + asset_manifest are approved. Compose via Remotion with cover layout.

2. **Cover Layout System:**
   - 16:9: cover left 30%, visual right 70%
   - 9:16: cover top 35%, visual bottom 65%
   - Text overlays auto-sized via font formula (target_fill_ratio: 0.30 for 16:9, 0.65 for 9:16)

3. **Motion Rules:**
   - Still images: Ken Burns (scale ≤ 1.08x)
   - Video clips: play natively
   - Crossfade transitions between segments

4. **Audio:**
   - music_enabled: background music at ~0.10 volume
   - tts_enabled: narration synced, music ducks during speech
   - Neither: silent with subtitles

5. **Export:** Both 16:9 and 9:16, render_runtime locked to 'remotion'

6. **Quality Gate** — Cover visible in every segment, both AR files exist, text readable

**Step 2: Commit**

```bash
git add skills/pipelines/book-recommend/compose-director.md
git commit -m "feat: add book-recommend compose director skill"
```

---

### Task 5: Publish Director Skill

**Files:**
- Create: `skills/pipelines/book-recommend/publish-director.md`

**Step 1: Write the publish director skill**

Simple wrapper following healing-text publish pattern:
- Record export paths and metadata
- Generate thumbnail concept showing cover + title
- Record format_mode, asset_mode, music_enabled, tts_enabled in publish_log
- File naming includes platform and AR suffix

**Step 2: Commit**

```bash
git add skills/pipelines/book-recommend/publish-director.md
git commit -m "feat: add book-recommend publish director skill"
```

---

### Task 6: Validation & Smoke Test

**Step 1: Validate pipeline manifest**

```bash
python3 -c "
from lib.pipeline_loader import PipelineLoader
loader = PipelineLoader()
manifest = loader.load('book-recommend')
print('Name:', manifest.name)
print('Stages:', len(manifest.stages))
for s in manifest.stages:
    print(f'  {s[\"name\"]}: skill={s[\"skill\"]}, produces={s[\"produces\"]}')
print('Modes:', list(manifest.modes.keys()) if hasattr(manifest, 'modes') else 'N/A')
"
```

**Step 2: Verify all skill files exist**

```bash
ls -la skills/pipelines/book-recommend/
```

**Step 3: Verify all referenced tools exist in registry**

```bash
python3 -c "
from tools.tool_registry import registry
registry.discover()
required = ['image_selector', 'video_selector', 'direct_clip_search', 'video_compose', 'color_grade', 'audio_mixer']
for tool in required:
    t = registry.get(tool)
    status = 'AVAILABLE' if t and t.is_available() else 'UNAVAILABLE'
    print(f'{tool}: {status}')
"
```

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: validate book-recommend pipeline end-to-end"
```
