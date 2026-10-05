# Seedance 2.5 — model knowledge (profile `seedance-2.5`)

> Scope: model-specific knowledge for the `video-generation` skill when `video_model = "seedance-2.5"`. Machine-readable limits live in `profile.json` next to this file; model-agnostic craft lives in `../../generation-craft.md`. Where this file says "skill 6", read `video-generation`. Rules here (e.g. ≤30 s units, ≥3 s shots, @Image tags) apply only to this model.
> Compiled: **2026-10-02**. Every figure carries a source and date. Lines tagged **[UNVERIFIED]** mean only one third-party source states it, or sources conflict.
> Important: the official docs pages of BytePlus ModelArk (`docs.byteplus.com/.../2607688` tutorial, `/2607689` prompt guide, `/1520757` create task) and Volcano Engine (`docs.volcengine.com/docs/ark/seedance-2-5`) render via JavaScript, so the fetch tool cannot read their content. The API schema below is therefore **cross-checked** across several gateways/resellers that use the same Ark format (`/api/v3/contents/generations/tasks`). Before running production, open the official docs page in a browser to reconfirm.

---

## 1) Specs table

| Parameter | Value | Source (date) | Status |
|---|---|---|---|
| Announcement date | 2026-06-23 (Volcano Engine conference) | Apiframe guide; Atlas Cloud; TechTimes (2026-07-03) | Verified (multiple sources) |
| Launch date | 2026-07-31 on Jimeng AI and Doubao Pro, "API access coming soon via BytePlus ModelArk" | ByteDance Seed blog (2026-07-31); TechNode (2026-07-31) | Verified (official) |
| ModelArk API | "API fully available now", branded *Dreamina Seedance 2.5* | BytePlus product page (read 2026-10-02); GitHub PR fact-check merged 2026-09-27 | Verified |
| Model ID | `dreamina-seedance-2-5-260628` (BytePlus), `doubao-seedance-2-5-260628` (Volcano and Ark-style gateways) | aiseedance25.app (verified 2026-08-15); APIYI; LaoZhang | **[UNVERIFIED]**: must probe in console |
| Duration per generation | 4–30s in one pass; `-1`/`auto` lets the model choose | BytePlus product page; Apiframe; fal; APIYI | Verified |
| Default duration | APIYI: `-1` (one test returned 10s); Venice: "default 10" | APIYI; Venice docs | Conflicting. **Always pass duration explicitly** |
| Extension | "multi-round extensions"; Jimeng has an ultra-long mode up to ~3 min; Dreamina has a "beta long-video mode" up to 180s | Seed blog; QbitAI (2026-07); Dreamina 2.5 page | Verified (UI). On the API, extend runs per task |
| Resolution | **Official: 480p / 720p**. Resellers offer 1080p (fal, APIYI, LaoZhang, Venice, Atlas). 4K "didn't ship" | BytePlus product page; Apiframe; fal "2.5 vs 2.0" (2026-08-13); CellCog (2026-08-22) | **Conflicting**, see section 14 |
| Measured pixels | 720p 16:9 = 1280×720; 9:16 = 720×1280; 21:9 = 1470×630 | Segmind review | Verified (one source, actually measured) |
| FPS | Fixed 24 fps; returns 1 extra frame (requesting 15s yields 361 frames = 15.042s) | APIYI; Segmind | Verified (2 sources) |
| Codec/container | H.264 High MP4 at 480/720p; H.265 at 1080p (APIYI); optional `mov` (`output_format`) | Segmind; APIYI; muapi GitHub | Verified / mov is [UNVERIFIED-official] |
| Bitrate | 9.5–14.3 Mbps (720p) | Segmind | One source |
| Audio output | Stereo AAC **32 kHz**, must be resampled to 48 kHz on ingest | Segmind | One source, check with ffprobe |
| Aspect ratio | `16:9, 9:16, 1:1, 4:3, 3:4, 21:9, adaptive` (muapi adds 9:21) | APIYI; LaoZhang; fal; EvoLink | Verified |
| Max references | 30 images + 10 videos + 10 audio (50 total) | Seed blog (official); BytePlus | Verified (official) |
| Image ref limits | <30 MB; side 300–6000 px; ratio 0.4–2.5; jpg/png/webp/bmp/tiff/gif/heic | APIYI; Atlas; fal | Verified (cross-checked) |
| Video ref limits | mp4/mov; each clip 2–30s (reference task) or 4–30s (edit/extend); **total ≤30s**; ≤200 MB | Venice; GitHub PR #110; Atlas; fal (1.8–30.2s) | Verified (cross-checked) |
| Audio ref limits | wav/mp3; 2–30s per clip; ≤15 MB; total ≤30s | Atlas; fal | Verified (cross-checked) |
| Audio-only reference | APIYI: 2.5 accepts audio alone. fal/Venice: must include at least 1 image or video | APIYI vs fal, Venice | **Conflicting**: always include 1 image |
| Audio generated with video | "unified multimodal audio-video joint-generation" architecture; `generate_audio` defaults to `true` | Seed blog; APIYI; fal | Verified |
| Dialogue languages | Chinese, English, Spanish, Indonesian, Malay, Thai, Arabic, Portuguese, **Vietnamese**, Japanese, Korean | Dreamina 2.5 page | Marketing page, Vietnamese needs testing |
| Multi-character | Improved "character voice consistency in multi-character scenarios" | Seed blog | Official |
| Editing | Timestamp-level editing (<1s error per QbitAI), green screen, camera perspective editing, reference-based/region editing | Seed blog; QbitAI | Official + hands-on |
| Clay/white model | Clay render, motion and creative reference; Maya/Blender plugins call Jimeng/Dreamina directly | Seed blog; QbitAI; Dreamina Blender workflow | Official |
| Prompt adherence | "~20% better than Seedance 2.0" | Apiframe; fal | Marketing, [UNVERIFIED] |
| Generation time | 60–227s (median 139s) for 10–20s 720p clips; APIYI: 720p/30s ~5.5 min; Reddit: queue sometimes ~40 min | Segmind; APIYI; Virse | Highly variable |
| Task retention | Signed video URL expires after ~24h; task queryable for 7 days | APIYI | Gateway, likely same as Ark |
| Weaknesses (official) | "physical plausibility of complex motions and the stability of scenes involving interactions among multiple subjects" | Seed blog | Official |

---

## 2) Access & pricing by platform

Prices change weekly. The table below is a snapshot as of the date on each row. Always compute **cost per accepted shot**, not per generation.

| Platform | Type | 480p /s | 720p /s | 1080p /s | Notes (source, date) |
|---|---|---|---|---|---|
| BytePlus ModelArk (official intl) | API, token billing | $0.1028 | $0.2312 | not available | CellCog 2026-08-22. Light/Production/Premium plans valid 3 months (BytePlus page). **Does not serve US, CA, UK, AU, NZ** (CellCog) |
| BytePlus LAS (managed) | API | $0.2056 | $0.4621 | — | CellCog |
| Volcano Engine Ark (CN) | API, token | ~¥9.60 / 5s 720p (price via APIYI) | | | APIYI, CN gateway |
| Replicate | API | $0.1028 | $0.2312 | — | CellCog |
| Apiframe | API | $0.15 | $0.34 | — | Apiframe guide; added 2026-08-07; charges only successful runs |
| fal.ai | API, queue | $0.2205 | $0.4730 | ~$1.14 | CellCog; fal has a 480p `draft` with a `draft_id` reusable for 7 days |
| EvoLink | API | $0.136–0.138 | $0.293–0.296 | $0.528–0.739 | EvoLink page; CellCog. Ref video billed cheaper ($0.084/$0.18) but input duration is added |
| Atlas Cloud | API | — | $0.134 (r2v) | upscale | Atlas page; self-registered portrait assets |
| WaveSpeed | API | $0.18 | $0.36 (Turbo $0.20) | Turbo $0.21 | CellCog |
| LaoZhang (Ark gateway) | API | | ~$1.37 / 5s 720p | ~$3.09 / 5s | $12.60 / 1M tokens |
| Jimeng AI (CN) | UI | | ~215 credits / 8s 720p | | CellCog; plans ~¥41–79/month |
| Dreamina (intl) | UI | | ~296 credits / 8s 720p | | CellCog; Dreamina page lists "$0.04–0.05/sec" by plan; paid plans remove the Dreamina watermark. Initial rollout **excludes the US**, requires 16+ (Leadde) |
| Doubao Pro | UI | | | | Seed blog |

**Token formula (Ark):** `tokens ≈ (input_video_seconds + output_seconds) × width × height × 24 / 1024` (APIYI; aiseedance25). Example 720p, 5s, no video input: 5×1280×720×24/1024 = **108,000 tokens**, matching LaoZhang's ~$1.37 estimate at $12.60/M. Consequences:
- **Reference video costs by duration**: a 10s playblast used as ref for a 10s output is billed as 20s, even though the per-second rate is lower (CellCog; EvoLink).
- All aspect ratios within a tier cost the same (APIYI).
- The most reliable billing field is `usage.completion_tokens`. Log this field for every task (aiseedance25).
- 400 `InvalidParameter` errors and 403 moderation errors are not billed. Gateways may pre-charge then settle (2 log lines) (APIYI; LaoZhang).

**Pipeline recommendation:** iterate at **480p** (or `draft` on fal), lock the take, then re-render at 720p with the same seed and prompt. The seed only keeps results "in the same neighborhood", not identical (muapi GitHub), so the 720p round must still be reviewed.

---

## 3) Core principles

1. **References determine form, the prompt determines intent.** Camera and layout come from the clay playblast, identity from character sheet images, voice from the audio ref. The prompt is left to direct performance, lighting, materials and pacing. "Seedance will give you a low angle. It will not give you the same low angle twice unless you show it one" (CozyClay).
2. **One narrow job per reference.** State explicitly `@Video1 controls only camera motion and blocking. Do not copy surface, color or lighting from @Video1` (fal prompting guide). Five clearly labeled refs beat forty mixed ones (Picsart).
3. **Write what is observable, not adjectives.** "She turns toward the window and pauses", not "make it emotional" (Dreamina prompt guide). This matches `physical_cues` in the shotlist.
4. **Complexity scales with duration.** Each shot in a unit should be **≥3s**: a prompt demanding 5 cuts in 15s failed (Segmind). Each time block has only one main action and one main camera move.
5. **Write causality in sequence:** contact → resulting motion → sound → reaction (fal). This reduces physics errors, the model's official main weakness.
6. **One language per prompt.** Mixing languages increases text and pronunciation errors (heyuan110; Morphic).
7. **Short constraints, grouped at the end** (Dreamina): "No cuts. No extra people. No subtitles. No face drift."
8. **Change only one variable per iteration** (fal; Picsart; seedance.tv).
9. **Order matters:** earlier refs are weighted higher (muapi GitHub), and instructions at the start of the prompt are followed better than those at the end (heyuan110). So put identity and the main action first.
10. **Measure by "cost per accepted, continuity-safe shot"** (atoms.dev). Real-world example: one team generated over 16,000 clips to get 253 usable shots for a 22-minute film.

---

## 4) Workflow per generation unit

Input from skills 4 and 5 (field names per `shot-design/references/shotlist.schema.json`): `units[]` with `id`, `duration_s` (4–30), `shot_ids`, `continuity_anchors`, `mouth_map`, `handoff_in/out`, `previs_ref`, `status`; each shot in `shots[]` with `id`, `unit_time_s` [start, end], `size`, `angle`, `lens_mm`, `camera.move/speed/direction`, `action.primary/dialogue/speaker`, `performance.intention/observable_behavior/intensity`, `sfx`, `ambience`; `characters[].identity_block/costume_block/reference_images/voice_ref`; `film.gen_ratio`. Plus clay stills, seg pass and playblast `.mp4` in `04_previs/<unit>/v<###>/`. Do not generate a unit with `status = "stale"`.

1. **Unit preflight**
   - Total duration ≤30s, each shot ≥3s, dialogue per shot ≤1 short line (see section 9).
   - A unit with >2 characters in physical interaction (hugging, grappling, passing objects) gets flagged `risk: multi_subject`; consider splitting the unit.
   - Playblast 4–30s long (≥4s required if it may later be used as an edit source). Playblast must be "flat greybox, no outlines, gizmos or UI" (CozyClay), with clean silhouettes (Portotheme).
2. **Build reference manifest** (section 6): assign roles and `@ImageN/@VideoN/@AudioN` labels in the exact order of the `content` array.
3. **Compile prompt** per the template in section 5. A single-shot prompt is about 60–100 words. A 30s multi-shot unit may be longer, but each time block should be only 25–50 words.
4. **Lint prompt** against the anti-AI checklist in section 10.
5. **Draft pass:** 480p, explicit `duration`, 2–3 different seeds, `return_last_frame: true`.
6. **Dailies (skill 7):** score 7 axes: face, clothing, body scale, background, lighting, motion, camera continuity (Virse), plus lip-sync and audio.
7. **Fix pass:** change only one variable at a time. If the error is local, use an edit task instead of regenerating everything.
8. **Final pass:** run 720p (or 1080p if the provider confirms native) with the locked seed and prompt. Download immediately since URLs expire after 24h. Save `last_frame_url`.
9. **Ingest:** measure real pixels with ffprobe, trim the extra frame, resample audio 32→48 kHz, write `generation_log.jsonl` (task_id, model, seed, params, tokens, cost, verdict).

---

## 5) Prompt template & rules

### Standard template (combining Dreamina 8-part and timecode format)

```
[FORMAT] {duration}s, {ratio}, {n} shots, one continuous scene{, no cuts | cuts at timecodes below}.
[REFERENCES] @Image1 is {CHAR_A} — face, hair, wardrobe only. @Image2 is {CHAR_B} — identity only.
@Video1 controls only camera path, framing and blocking; do not copy its grey clay surfaces or flat lighting.
@Image3 controls only color palette and lighting mood. @Audio1 is {CHAR_A}'s voice timbre only.
[WORLD] {location, time of day, weather, 2–3 concrete set details}. Light: {source + direction + quality}.
[TIMELINE]
[00:00–00:06] Shot 1 — {framing}, {one camera move}. {subject} {one physical action with start → end}. {sound}.
[00:06–00:14] Shot 2 — ...  {CHAR_A} says: "{one short line}" — {CHAR_B} listens, mouth closed.
...
[LOOK] {lens feel, grain, texture: physical descriptors, not hype words}.
[AUDIO] {ambience}, {key SFX on cue}, {music: none | description}.
[KEEP] Same faces and wardrobe as references throughout. {props states}.
[AVOID] No extra people. No on-screen text. No face drift. No warped hands.
```

### Detailed rules

**Element order:** format → subject/refs → action → environment → camera → look → timing → audio and constraints (Dreamina official guide). When using timecodes, merge action and camera into each block.

**Timecode:** use `[00:00–00:06]` or `0–6s:`. Each block continues the physical state of the previous block rather than resetting (fal). If a cut is needed, write "Cut to:" or "Shot 2 —". For a single continuous take, write "one continuous take, no cuts". Timestamp control has about 1s error (QbitAI), so do not place key beats less than 1s apart.

**Camera vocabulary the model understands** (Luma; issastash; Dreamina; muapi):
- Shot size: extreme wide, wide (WS), medium (MS), medium close-up (MCU), close-up (CU), extreme close-up, over-the-shoulder, POV.
- Movement: static/locked-off tripod, slow push-in / dolly in, pull-back reveal, dolly left/right, tracking shot, orbit, crane up/boom up, low-angle tilt up, handheld, Steadicam, whip pan, rack focus, Hitchcock zoom (dolly zoom), aerial/drone.
- Lens: shallow depth of field, wide-angle 24mm feel, telephoto compression, anamorphic.
- Rule: **one main move per shot**. "push-in, then pan left, zoom out, orbit" is wrong (issastash). Each move should be tied to a specific event, e.g. "as she sits, camera eases in" (fal).
- If a playblast exists, **do not re-describe the camera path in detail** in the prompt. Write only "camera follows @Video1 exactly", to avoid conflicts (see section 10, pattern 5).

**Direct performance with physical cues:** turn each `intention` into 1–2 visible behaviors, like "jaw tightens, eyes drop to the cup, thumb stops tapping". Describe the emotion only once per block; do not repeat it (seedance.tv lip-sync).

**Dialogue:**
- Put it in **straight double quotes** (fal "2.5 vs 2.0": lip-sync is triggered by quoted dialogue).
- State who speaks and who is silent: `MARA says: "..." — JONAH listens silently` (seedance.tv voice).
- One short line per block, about ≤12–15 words or ≤4s of speech. Commas create pauses, periods end the line. Spell out numbers and abbreviations (seedance.tv).
- One language per segment. For bilingual dialogue, split by turn (seedance.tv).
- Vietnamese: Dreamina lists it as supported, but there is no public test of tone-mark quality and lip-sync yet. **A 5s isolated test is mandatory** before use.

**Length:** single shot 60–100 words. Beyond 150 words instructions get diluted, and of 8 requests usually only 4–5 are executed (heyuan110; issastash). A 30s multi-shot unit can be longer, but each block must be tight. General principle: "the shortest prompt that fully specifies production" (Dreamina).

**Negative/avoid:** grouped at the end, short, specific. Example: "No cuts. No slow motion. No duplicated objects. No text. No music." (fal). Do not list 20 things to avoid.

**Prompt language:** use English across the whole pipeline for consistency, and because upstream/downstream skills also use English. There are reports that Seedance 2's filter is stricter with English and Chinese prompts pass more easily (mitte.ai on X, via Morphic). But ByteDance advises against mixing languages, since mixing breaks pronunciation. If an English prompt is flagged, **translate the whole thing** into Chinese, not part of it. Dialogue alone must stay in the language the character speaks.

**On-screen text:** avoid entirely. Titles and subtitles are left to post (skill 8). If text is unavoidable, write the prompt in the same language as the text and use common words (heyuan110).

---

## 6) Reference strategy & manifest format

### Reference roles by purpose

| Purpose | Best ref type | Recommended count | Notes |
|---|---|---|---|
| Character identity | Character sheet (front, 3/4, profile) + wardrobe sheet, neutral background | 2–4 images per character | Real human faces are blocked (section 12). Overly photoreal AI images may also be blocked (ruoqijin, applies to 2.0). Prefer stylized character sheets or register in the asset library |
| Layout / camera / blocking | **Clay playblast** (video), plus a clay still of the first frame | 1 video per unit | The model treats the blockout as "the spatial truth of the shot" (Portotheme) |
| Motion / choreography | Video motion ref (animated playblast, or mocap render) | 1 | Write "motion only, do not copy appearance" (Luma) |
| Style / look | 1–2 approved key frames from the visual bible | 1–2 | Do not name film stocks or studios as this may trigger moderation (Segmind) |
| Environment | Approved set/location images | 1–3 | |
| Prop / product | Multi-angle images | 1–3 | Products tend to "change shape during rotation" (atoms.dev) |
| Voice | Clean 8–15s audio, single speaker, no music/reverb (seedance.tv) | 1 per speaking character | Total audio ≤30s |
| Music / rhythm | Audio track | 0–1 | Not needed if music will be cut in post |
| Continuity from previous unit | Previous unit's `last_frame`, as image ref or first_frame | 1 | See section 8 |

**Practical ref budget per unit:** 5–12 refs is enough. The maximum of 50 is capacity, not a target. "Reference capacity ≠ reference adherence": there are cases where many refs were supplied and the character's body proportions still drifted (Virse).

**Ref conflicts:**
- Image is daytime but the prompt says night → align the prompt with the ref (issastash).
- Clay playblast has flat lighting → state explicitly "do not copy lighting or grey surfaces from @Video1".
- Two style images contradict each other → drop one.
- Pushing reference strength to max (the UI has a slider) turns characters into "cardboard cutouts". Keep around 70–80% (heyuan110, about 2.0).

**Using clay render / playblast (from skill 5):**
- Export a playblast exactly as long as the unit (4–30s), 24 fps, same aspect ratio as output, no UI or gizmos.
- ~~Use a different clay color per character~~ → **Shared convention (shared-conventions §1):** clay is strictly grey; to distinguish characters, also send a seg pass (one color per character) and write in the prompt "the red stand-in in @Video2 is @Image1". Coloring the clay directly is **[UNVERIFIED]**; use it only if an A/B test (T3) shows it is better.
- Official sample prompt from the Dreamina Blender plugin: "Transform this Blender viewport blockout into a Hollywood-style cinematic shot. Preserve the original camera angle, character placement, and scene composition..." (Dreamina Blender workflow). When writing your own prompt, drop "Hollywood-style" (keyword soup) and replace it with a concrete lighting description.
- When the camera is wrong, go back to Blender and re-block. Do not try to fix it with the prompt (Portotheme).

### Manifest format (`05_takes/<unit>/manifest_<unit>_r<round>.json`; file paths under `02_bible/refs/...` and `04_previs/...`)

```json
{
  "unit_id": "U03",
  "model": "dreamina-seedance-2-5-260628",
  "refs": [
    {"tag": "@Image1", "type": "image_url", "role": "reference_image",
     "file": "02_bible/refs/char/linh_sheet_front.png", "job": "LINH identity: face, hair, wardrobe",
     "do_not_copy": ["background", "pose", "lighting"]},
    {"tag": "@Image2", "type": "image_url", "role": "reference_image",
     "file": "02_bible/refs/char/linh_sheet_34.png", "job": "LINH identity, 3/4 angle"},
    {"tag": "@Image3", "type": "image_url", "role": "reference_image",
     "file": "02_bible/refs/keyframes/U03_look.png", "job": "palette + light mood only",
     "do_not_copy": ["characters", "composition"]},
    {"tag": "@Video1", "type": "video_url", "role": "reference_video",
     "file": "04_previs/U03_playblast.mp4", "duration_s": 12.0,
     "job": "camera path, framing, blocking, timing",
     "do_not_copy": ["clay surfaces", "flat grey lighting"]},
    {"tag": "@Audio1", "type": "audio_url", "role": "reference_audio",
     "file": "02_bible/refs/voice/LINH_01_ref.wav", "duration_s": 11.2, "job": "LINH voice timbre only"}
  ],
  "totals": {"images": 3, "videos": 1, "video_seconds": 12.0, "audios": 1, "audio_seconds": 11.2},
  "checks": {"video_seconds_le_30": true, "audio_seconds_le_30": true, "images_le_30": true,
             "no_real_faces": true, "has_image_with_audio": true}
}
```

Convention: the `@ImageN` index is the **order of appearance in the content array** per type (the first image is `@Image1`). Never put asset IDs in the prompt. Always reference by position (APIYI).

---

## 7) API guide

### Endpoint (Ark format, shared by BytePlus and Volcano)

- BytePlus: `POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks` (endpoint from the BytePlus Seedance 1.0 blog, same API family)
- Query: `GET .../api/v3/contents/generations/tasks/{task_id}`
- There are also List and Cancel/Delete task (per the BytePlus Video generation API page index)
- Auth: `Authorization: Bearer $ARK_API_KEY`

### Request parameters (cross-checked: APIYI, LaoZhang, Venice, BytePlus blog)

| Field | Value | Notes |
|---|---|---|
| `model` | `dreamina-seedance-2-5-260628` | probe first |
| `content[]` | `{type:"text", text}`, `{type:"image_url", image_url:{url}, role}`, `video_url`, `audio_url` | `role` ∈ `first_frame`, `last_frame`, `reference_image`, `reference_video`, `reference_audio`. URL can be https, base64 data URI, or `asset://` |
| `resolution` | `480p` / `720p` (`1080p` depending on route) | lowercase |
| `ratio` | `16:9`…`adaptive` | edit/extend/first-frame on 2.5 **require `adaptive`** (APIYI) |
| `duration` | 4–30 or `-1` | `-1` for edit |
| `seed` | integer (-1 means random) | |
| `generate_audio` | bool, default true | |
| `watermark` | bool, default false | |
| `return_last_frame` | bool | returns `content.last_frame_url` |
| `output_format` | `mp4` / `mov` | 2.5 only (APIYI) |
| `omni_reference_task_type` | `auto` / `reference` / `edit` / `extend` | 2.5 only (APIYI; GitHub PR #110) |
| `callback_url` | string | webhook (EvoLink; muapi) |
| `camera_fixed` | bool | Exists in the 1.x family (`--camerafixed`). **[UNVERIFIED] for 2.5**: do not rely on it. To lock the camera, use the prompt "locked-off tripod" plus a static playblast |

### Sample request: reference-to-video for one unit

```json
POST /api/v3/contents/generations/tasks
{
  "model": "dreamina-seedance-2-5-260628",
  "content": [
    {"type": "text", "text": "12s, 16:9, two shots... (full prompt in section 11)"},
    {"type": "image_url", "image_url": {"url": "https://cdn.example/linh_front.png"}, "role": "reference_image"},
    {"type": "image_url", "image_url": {"url": "https://cdn.example/linh_34.png"}, "role": "reference_image"},
    {"type": "image_url", "image_url": {"url": "https://cdn.example/U03_look.png"}, "role": "reference_image"},
    {"type": "video_url", "video_url": {"url": "https://cdn.example/U03_playblast.mp4"}, "role": "reference_video"},
    {"type": "audio_url", "audio_url": {"url": "https://cdn.example/LINH_01_ref.wav"}, "role": "reference_audio"}
  ],
  "resolution": "480p",
  "ratio": "16:9",
  "duration": 12,
  "seed": 418207,
  "generate_audio": true,
  "watermark": false,
  "return_last_frame": true
}
```

Task creation response: `{"id": "cgt-2026xxxxxxxx"}`

### Query response (sample per LaoZhang)

```json
{
  "id": "cgt-example-task-id",
  "model": "dreamina-seedance-2-5-260628",
  "status": "succeeded",
  "ratio": "16:9",
  "duration": 12,
  "resolution": "480p",
  "content": {
    "video_url": "https://...signed...mp4",
    "last_frame_url": "https://...jpeg"
  },
  "usage": {"completion_tokens": 87300, "total_tokens": 87300}
}
```

Statuses: `queued` → `running` → `succeeded` | `failed` | `expired` (some gateways return `completed`, `cancelled`). Success is `succeeded`, not "completed" (APIYI).

### Polling & batching

```python
import time, requests
H = {"Authorization": f"Bearer {KEY}", "Accept-Encoding": "identity"}  # avoids spurious gzip errors on some gateways (APIYI)
def run(task_body):
    tid = requests.post(f"{BASE}/contents/generations/tasks", json=task_body, headers=H).json()["id"]
    time.sleep(25)                       # wait 20–30s before the first poll
    deadline = time.time() + 20*60       # budget >=15 min
    while time.time() < deadline:
        t = requests.get(f"{BASE}/contents/generations/tasks/{tid}", headers=H).json()
        if t["status"] == "succeeded": return t   # download video_url IMMEDIATELY (expires ~24h)
        if t["status"] in ("failed", "expired", "cancelled"): return t
        time.sleep(15)                   # poll every 10–20s
```

- Batch: submit variations (different seeds) of multiple units in parallel, limiting concurrency to the account quota. Plan in **batches** rather than real time, because generation time varies up to 3x (Segmind).
- Errors: 400 `InvalidParameter` (e.g. `InvalidParameter.TaskTypeConstraint` when setting a specific ratio for edit/extend) is reported immediately at submit. For 403 moderation, fix the asset or prompt. For a `failed` task, check the error field and try another seed (APIYI).
- Other APIs: fal uses `fal.queue.submit("bytedance/seedance-2.5/reference-to-video")` with `image_urls/video_urls/audio_urls`, `task: reference|editing|extension`, `draft`. Replicate has `bytedance/seedance-2.5`. muapi/Apiframe have `images_list/videos_list/audios_list`. **Field names differ per provider**, so the skill needs an adapter layer.

### Cost log (one line of `generation_log.jsonl`)

```json
{"ts":"2026-10-02T09:14:03Z","unit":"U03","take":"U03_t2","provider":"byteplus","model":"dreamina-seedance-2-5-260628",
 "task_id":"cgt-...","seed":418207,"res":"480p","dur_out":12,"dur_ref_video":12,"tokens":124416,
 "usd_est":0.0,"wall_s":141,"status":"succeeded","verdict":"pending_dailies","prompt_sha":"9f2c..."}
```

---

## 8) Continuity chaining & extension

**Three ways to join units, ranked by reliability:**

1. **Extend task** (`omni_reference_task_type: "extend"`, `ratio: "adaptive"`, 4–30s source video). The model continues from the source video's last frame. Write the prompt as "Extend @Video1, ..." (Venice) or "Continue from @Video1. ... Maintain same lighting/character/style" (issastash). Duration counts only the **new part** (issastash), and the output contains only the new content (Venice). muapi recommends MOV when chaining edit/extend to avoid repeated recompression. The source video counts toward billing (token formula).
2. **Last frame → first_frame:** set `return_last_frame: true` on unit N, then use `last_frame_url` as `role: "first_frame"` for unit N+1. This guarantees a pixel-matched join frame, but **[UNVERIFIED]**: in the 2.0 family, first-frame mode and multimodal reference may be mutually exclusive, and APIYI reports that first-frame tasks on 2.5 force `ratio: adaptive`. Test whether it can be combined with `reference_video` (playblast).
3. **Last frame as reference_image** plus the line "@Image4 is the exact final state of the previous shot: {state description}". Softer and compatible with the playblast. Use when method 2 cannot be combined.

**Continuity rules:**
- In unit N+1, the playblast must start at exactly the pose and camera position of unit N's last frame (easy in Blender; skill 5 should export an extra 0.5s overlap).
- Re-anchor identity every 2–3 extensions by re-supplying the character sheet (issastash), since identity drifts with the number of rounds.
- Keep the same aspect ratio, resolution, seed family, voice ref, and room tone described in the prompt (extensions changing room tone is a documented issue, seedance.tv voice).
- Prefer **cutting at unit boundaries** (cut on action or on eyeline) over forcing a continuous join. That is why skill 4 should place unit boundaries right at cut points.
- Stitch: the prompt pattern "@Video1 + [transition] + followed by @Video2" auto-trims the join (Venice). Can be used to join two good takes, but review carefully.

**Editing instead of regenerating:**
- Edit task: "Strictly edit @Video1, changing only {X}" (Venice), with `duration: -1`, `ratio: adaptive`. Billed by ceil(ref video duration).
- Timestamp edit: "At 00:07–00:09, replace the mug in her hand with a glass; keep everything else identical." Error about 1s (QbitAI).
- Risk: local edits sometimes "alter more than the requested region" (atoms.dev). Diff the whole clip against the original.

---

## 9) Failure modes → mitigation

| Failure | Symptom | Cause | Mitigation |
|---|---|---|---|
| Identity drift | Face, hair, body proportions gradually change toward the end of 30s | Weak refs, extreme emotion, unit too long | 2–4 sheet images per character placed first in the array; the line "Same face and wardrobe as @Image1 throughout"; split units to 15–20s; re-anchor when extending |
| Body scale drift | Face holds but height/proportions change (Virse) | No full-body ref | Add a full-body sheet; playblast with fixed proxy height |
| Broken multi-subject interaction | Hands pass through bodies, objects switch owners | Official weakness | Fewer subjects per block; write causality step by step; change camera angle to hide contact; split into an insert shot |
| Complex motion physics | Running, jumping, falling look "floaty" | Official weakness | Use an animated playblast as motion ref; only one "fast" element per block (issastash); describe the endpoint: "lands, knees bend, stops" |
| Deformed hands/fingers | Extra fingers, broken grips | No model guarantees this (fal) | Reduce hand close-ups; simple hand actions; avoid "deformed hands"; pick good takes; inpaint/edit |
| Product/prop morph | Object changes shape when rotating (atoms.dev) | | Multi-angle prop images; slow rotation; "label and shape unchanged" |
| Lip-sync late/drifting | Mouth opens late, drifts progressively | Leading silence, line too long, face small or turned (seedance.tv) | One short line per block; start speaking early; MCU or tighter, face toward camera; isolated 5s test; less greedy prompt (fewer SFX, fewer camera moves) |
| Wrong speaker | Listener also moves lips | Speaker not stated | "X says: ... — Y listens, mouth closed" |
| Voice drift between shots | Timbre changes | Missing voice ref, contradictory adjectives | Clean 8–15s voice ref; a "voice identity card" repeated verbatim in every unit (seedance.tv) |
| Audio artifacts | Distortion, music bleeding in, 32 kHz | | Write "no music" if music is done in post; resample; replace dialogue with ADR/TTS in skill 8 if needed |
| Camera ignores instructions | Changes direction mid-clip, jerky | Stacked moves, prompt contradicts video ref | One move per shot; with a playblast, let the playblast decide; "cut to" instead of chaining moves |
| Scenes blending | Two locations merge | Too many scenes crammed into a short clip | Each shot ≥3s; write "Cut to" explicitly |
| Garbled text | Nonsense lettering | | Do not render text; leave it to post |
| Missing middle action | Jumps straight from start to end | No time blocks | Add intermediate blocks (fal) |
| End-of-clip drift | Last 5–8s wander | Prompt only describes the opening | Describe through the full 30s, including the "settle" beat (Picsart) |
| Overly smooth "AI look" | Plastic skin, flat lighting, slow-mo | Keyword soup, no light source | Describe real light sources; "natural skin texture, subtle film grain, handheld micro-movement"; "no slow motion" |
| Moderation reject | 403 or failed | Real faces, IP, age words, film stock/studio names, prompt too short | Section 12; write full production language (Morphic); remove brand and studio names |
| 720p breaks up in close-ups | Pixelation on face CUs (Segmind) | Resolution limit | Avoid prolonged ECUs; upscale in post (skill 8) |

---

## 10) Anti-AI prompt patterns (before → after)

**P1. Keyword soup**
- Before: `cinematic, 8k, masterpiece, ultra-detailed, hyperrealistic, award-winning, a woman in a cafe`
- Why it fails: these tokens carry no observable information. They push output toward a "stock AI" look (smooth skin, fake bokeh) and occupy the start of the prompt, where weighting is highest (heyuan110).
- After: `A woman in her 40s, grey wool cardigan, sits at a window table in a small Hanoi café at 7 a.m. Cool daylight from the street window on her left, warm tungsten bulb behind the counter. Medium shot, locked-off. Natural skin texture, light film grain.`

**P2. Stacked adjectives / conflicting styles**
- Before: `elegant, gritty, dreamy, glossy, documentary, surreal lighting`
- Why: the directions cancel each other out, diluting intent (Picsart).
- After: `Overcast documentary look: soft even daylight, muted greens, slight handheld sway.`

**P3. Emotion word with no physical cue**
- Before: `He feels devastated and heartbroken.`
- Why: the model cannot "act" an adjective, so it usually produces a generic frown or nothing.
- After: `He reads the message, stops scrolling, lowers the phone to his knee. His jaw tightens; he exhales through his nose and looks at the floor.`

**P4. Too many actions in one segment**
- Before: `[0–4s] She runs in, drops her bag, hugs her brother, picks up the cat and turns on the TV.`
- Why: 5 beats in 4s, so the model drops or merges actions, often producing morphing (Luma).
- After: `[0–5s] She pushes the door open and stops in the doorway, bag sliding off her shoulder. [5–10s] Her brother stands up from the sofa; she crosses the room and hugs him, chin on his shoulder.` (The cat and TV move to another unit.)

**P5. Camera prompt contradicts motion ref**
- Before: `@Video1 for camera. Fast orbit around them, then crane up and whip pan to the window.`
- Why: the playblast says one camera path, the text says another; the result is jitter and mid-clip direction changes.
- After: `Camera path, framing and timing follow @Video1 exactly. Do not copy its grey clay surfaces or flat lighting.`

**P6. Dialogue too long**
- Before: `[0–6s] MAI says: "I've been thinking about everything that happened last summer, and honestly I don't know if I can forgive you, because you never even called."`
- Why: a roughly 8s line crammed into a 6s block, so lip-sync drifts (seedance.tv; heyuan110).
- After: `[0–5s] MAI says: "You never even called." — Then she looks away. [5–10s] MAI, quieter: "Not once." — KHOA stays silent, mouth closed.`

**P7. Vague subject**
- Before: `A man walks down a street at night.`
- After: `KHOA (@Image1), late 20s, faded navy bomber jacket, walks past shuttered shopfronts on a narrow wet street; a single sodium streetlight behind him throws his shadow ahead.`

**P8. "Fast" and "lots of movement" everywhere**
- Before: `fast camera, fast running, lots of dynamic movement, explosive energy`
- Why: multiple fast elements at once reliably cause jitter (issastash).
- After: `Camera tracks steadily alongside at running speed; only the runner moves fast. Background traffic is slow.`

**P9. Overlong negative prompt**
- Before: 25 items "no blur, no ugly, no bad anatomy, no low quality..."
- After: `No cuts. No extra people. No on-screen text. No music.` (only errors actually seen in dailies)

**P10. Storytelling instead of describing the shot (moderation-prone and vague)**
- Before: `Mai is sad because her father, a former soldier, abandoned her as a child.`
- Why: backstory cannot be filmed, and age words make the filter stricter (Morphic).
- After: `MCU of MAI holding an old military photograph; her thumb rubs the edge of the frame. Window light from the right.`

**P11. Mixed languages**
- Before: `Cô gái đứng ở ban công, golden hour, camera dolly in, cô ấy nói "I miss you".` [The girl stands on the balcony, golden hour, camera dolly in, she says "I miss you".]
- After: the whole prompt in English, only the dialogue line kept in the character's language: `... LAN says in Vietnamese: "Em nhớ anh."` [I miss you.] The dialogue line goes in its own segment.

**P12. Naming studios, film stocks, IP**
- Before: `in the style of Pixar / shot on Kodak Vision3 like a Wes Anderson film`
- Why: moderation risk (Segmind) and IP risk.
- After: `Symmetrical centered framing, pastel pink-and-mint palette, flat frontal light, deadpan stillness.`

---

## 11) Three complete examples

### Example A: Dialogue scene (18s unit, 2 characters, 3 shots)

Manifest: `@Image1` LINH sheet front, `@Image2` LINH sheet 3/4, `@Image3` KHOA sheet front, `@Image4` kitchen keyframe (light/palette only), `@Video1` playblast U07 18s (camera + blocking), `@Audio1` LINH voice 10s, `@Audio2` KHOA voice 9s.
Params: `480p → 720p`, `16:9`, `duration: 18`, `generate_audio: true`, `return_last_frame: true`, 3 seeds.

```
18s, 16:9, three shots in one small kitchen at night.
@Image1 and @Image2 are LINH: face, short black bob, mustard sweater. @Image3 is KHOA: face, buzz cut, grey work shirt.
@Image4 sets palette and light only. @Video1 sets camera path, framing, blocking and timing only; do not copy its clay surfaces or flat light.
@Audio1 is LINH's voice timbre; @Audio2 is KHOA's voice timbre.
Light: one warm pendant bulb above the table, cool blue spill from the window behind KHOA.
[00:00–00:06] Shot 1 — medium two-shot, locked-off. KHOA sets two bowls of noodles on the table, sits; LINH does not look up from her phone. Chopsticks click on ceramic.
[00:06–00:12] Shot 2 — MCU on LINH, slow push-in. She puts the phone face down. LINH says: "Mẹ gọi lại chưa?" [Has Mom called back?] KHOA listens, mouth closed.
[00:12–00:18] Shot 3 — MCU on KHOA over LINH's shoulder. He stops stirring, holds the chopsticks still. KHOA says: "Chưa. Ăn đi em." [Not yet. Eat up.] He pushes her bowl closer.
Natural skin texture, light grain. Ambience: fridge hum, distant motorbikes. No music.
Same faces and wardrobe throughout. No extra people. No on-screen text.
```

(The bracketed English glosses are for the reader only; strip them before submitting the prompt.)

Risks to check in dailies: Vietnamese lip-sync (tone marks), whether the listener moves their lips, whether bowls and chopsticks morph.

### Example B: Action/motion (12s unit, 1 character, continuous take)

Manifest: `@Image1` runner sheet full-body, `@Image2` runner face CU, `@Image3` alley location still, `@Video1` playblast U12 12s with running and crate-vault animation (camera tracking with the motion).
Params: `16:9`, `duration: 12`, `generate_audio: true`.

```
12s, 16:9, one continuous take, no cuts.
@Image1 and @Image2 are DUY: lean build, red windbreaker, black cargo pants, white sneakers. @Image3 is the alley: wet cobbles, hanging cables, steel shutters.
@Video1 controls camera path, DUY's body motion and timing only; do not copy clay surfaces or lighting.
Dusk; cold blue sky, one orange shop sign as the key light from frame right.
[00:00–00:04] DUY sprints toward camera down the alley; camera tracks backward at his speed. Footsteps slap on wet stone.
[00:04–00:08] He plants his left foot, vaults the stacked crates with one hand on the top crate; the top crate shifts a few centimeters and scrapes.
[00:08–00:12] He lands, knees bend, one hand touches the ground, then he pushes off and runs out of frame left. Camera settles to a stop.
Only DUY moves fast; background is still. Puddle splashes match each footfall.
Same face and clothes throughout. No slow motion. No extra people. No music.
```

Note: the crate vault falls squarely in the "complex motion physics" weakness zone, so run 3–4 seeds. If the hand passes through the crate, split into 2 shots (run up, then cut to a landing insert).

### Example C: Stylized montage (24s unit, 4 shots, with cuts, no dialogue)

Manifest: `@Image1` paper-cutout style frame (visual bible), `@Image2` stylized HOA character sheet, `@Image3`–`@Image4` location sketches, `@Audio1` approved 24s music (beat ref).
Params: `16:9`, `duration: 24`, `generate_audio: true` (SFX only; the original music track is used in post).

```
24s, 16:9, four shots with hard cuts on the beat of @Audio1.
@Image1 sets the look only: layered paper-cutout textures, visible paper fibers, soft drop shadows, limited palette of indigo, ochre and off-white. @Image2 is HOA: round face, indigo áo bà ba, conical hat. @Image3 and @Image4 are the rice field and the river market.
[00:00–00:06] Shot 1 — wide, slow lateral dolly right. Paper rice stalks sway in layers; HOA walks along the dyke, small in frame.
[00:06–00:12] Cut to Shot 2 — medium, locked-off. HOA bends and lifts a basket of rice; paper grains spill from the edge.
[00:12–00:18] Cut to Shot 3 — wide, top-down. Paper boats drift across a river of folded blue strips; HOA's boat enters from bottom of frame.
[00:18–00:24] Cut to Shot 4 — close-up, slow push-in. HOA looks up as a paper sun rises behind layered hills; she smiles, eyes crinkling.
Motion stays slightly stepped like stop-motion at 12 drawings per second.
Audio: paper rustle, water lapping, no voices. Keep @Audio1 timing for cuts.
Same character design throughout. No photoreal textures. No on-screen text.
```

Note: "12 drawings per second" requests a motion feel. Output is still 24 fps. If the model smooths it out, build frame-holds in post. **[UNVERIFIED]** that the model honors this instruction.

---

## 12) Policy / legal

- **Real human faces:** the public Seedance 2.x API does not accept image or video refs containing real human faces (Virse; Venice: "Person-bearing media is not supported on the public Seedance API"; ruoqijin citing a Volcengine rule dated 2026-04-02). Valid options: (a) register in ModelArk's **private virtual portrait / asset library** and reference via `asset://` (APIYI; BytePlus page 2333565 exists but its content could not be read); (b) Atlas Cloud self-registered assets, on condition "only use a real person's likeness if you have their authorization"; (c) use fictional characters and stylized character sheets. Photoreal AI images may be blocked by the face detector (ruoqijin, applies to 2.0). The CN enterprise channel requires a large commitment agreement (ruoqijin). Real actors require a **written release before generation** (Creatide).
- **Incident timeline:** 2026-02-09 Jimeng paused real-person reference. 2026-02-13 Disney sent a cease-and-desist, Paramount followed. 2026-03-16 two US Senators demanded Seedance be shut down (Wikipedia; TechTimes). Global relaunch 2026-03-24 with "no real-person uploads + C2PA watermarking + IP filtering" (ruoqijin). TechTimes dates C2PA from 2026-03-30. No court ruling as of 2026-07.
- **IP:** copyrighted characters and brands are hard-blocked (Morphic). Do not prompt by character, studio or film name. Naming film stocks or studios has caused rejections (Segmind).
- **Minors:** the words "child, kid, young, boy, girl" make the filter stricter on the whole prompt (Morphic). If the script has children, describe by role ("the younger sibling") and use stylized sheets. Never use images of real children. Dreamina requires users to be 16+ (Leadde).
- **Watermark/provenance:** the API defaults to `watermark: false` (APIYI). The Dreamina UI has a watermark on the free plan, removed on paid plans (Dreamina page). C2PA embedded since 03/2026 (TechTimes; ruoqijin). **Do not strip C2PA**, and disclose the film as AI-generated (per labeling requirements in many markets; legal details are outside the scope of the sources opened).
- **Commercial use:** commercial rights vary by platform and plan. Read the current ToS of the exact surface in use (Creatide). BytePlus advertises film, advertising and previs use cases (BytePlus page). Dreamina states "commercial ready" for paid plans. **[UNVERIFIED]**: original ToS not read.
- **Region:** BytePlus intl does not serve US/CA/UK/AU/NZ (CellCog). Dreamina 2.5 initially not available in the US (Leadde). Users in Vietnam fall within the Asia region, but check in the account.

---

## 13) Gate checklist (before handing off to skill 7)

**Pre-submit (per unit)**
- [ ] Unit 4–30s; each shot ≥3s; ≤1 short dialogue line per block; speaker and silent listener stated explicitly.
- [ ] Manifest valid: images ≤30, videos ≤10 and total ≤30s, audio ≤10 and total ≤30s, ≥1 image if audio is present, no real faces or IP, every ref has `job` and `do_not_copy`.
- [ ] Playblast has correct aspect ratio, 24 fps, no UI, length matches unit, pose and camera match the previous unit's last frame.
- [ ] Prompt passes the section 10 lint: no keyword soup, no bare emotion, one camera move per shot, no conflict with `@Video1`, one language, avoid list ≤6 items.
- [ ] `duration`, `ratio`, `resolution`, `seed`, `return_last_frame: true` set explicitly.
- [ ] Cost estimated (token formula) and within the unit budget.

**Post-generate**
- [ ] Video and last frame downloaded within 24h; ffprobe confirms pixels, fps, frame count, audio sample rate.
- [ ] Log written with all fields: task_id, seed, tokens, cost, wall time.
- [ ] ≥2 takes for every risky unit (multi_subject, action, Vietnamese dialogue).
- [ ] Preliminary self-score on the 7 axes and lip-sync done before sending to dailies.
- [ ] The selected take at 720p final uses the same seed and prompt as the approved draft.

---

## 14) Uncertain / conflicting information

1. **Resolution:** BytePlus official, Apiframe and fal (2026-08-13) state 480p/720p. APIYI, LaoZhang, Venice, Atlas and the fal API (later) offer 1080p. CellCog and muapi say reseller 1080p/4K is upscaled, not native. Dreamina marketing says "4K"; TechTimes says 4K 10-bit was announced on 2026-06-23. **Decision:** master at 720p, measure real pixels, treat 1080p as an option to A/B against upscaling in post.
2. **Model ID:** prefixes `dreamina-` (BytePlus) and `doubao-` (Volcano) both carry the `260628` suffix. Must probe in console.
3. **Default duration:** `-1` (APIYI) or 10 (Venice). Always pass explicitly.
4. **Audio-only ref on 2.5:** APIYI says yes, fal and Venice say no.
5. **`camera_fixed` on 2.5:** no source confirms it.
6. **first_frame combined with reference_video:** compatibility not confirmed.
7. **Vietnamese dialogue quality:** only named in the language list (Dreamina). No independent evaluation.
8. **Chinese vs English prompt:** evidence that the filter is easier on Chinese is anecdotal only (mitte.ai, applies to 2.0).
9. **Pricing:** ranges from $0.10 to $0.47/s for 720p depending on provider (snapshot 2026-08 to 2026-09), with expiring promos. Recheck before every render batch.
10. **Max extension length:** UI about 3 min (Jimeng/Dreamina beta). On the API it is per round; unclear whether there is a round limit.
11. **How strictly photoreal AI faces are blocked on 2.5:** data mostly from 2.0.
12. **Output frame rate:** fixed at 24 fps per 2 sources. No fps parameter seen.

---

## 15) Sources (only URLs actually opened)

Official ByteDance / BytePlus / Volcano:
- https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5 (2026-07-31)
- https://www.byteplus.com/en/product/seedance (read 2026-10-02)
- https://www.byteplus.com/en/blog/seedance-1-0-pro-guide-api-pricing (Ark endpoint, 1.x family)
- https://docs.byteplus.com/en/docs/ModelArk/2607688 (2.5 tutorial, opened but content renders via JS, unreadable)
- https://docs.byteplus.com/en/docs/ModelArk/2607689 (2.5 prompt guide, same as above)
- https://docs.byteplus.com/en/docs/ModelArk/1520757 (create task, updated 2026-09-28, same as above)
- https://docs.byteplus.com/en/docs/ModelArk/Video_Generation_API (index: create/retrieve/list/cancel)
- https://docs.byteplus.com/en/docs/ModelArk/2333565 (private virtual portrait library, same as above)
- https://docs.volcengine.com/docs/ark/seedance-2-5?lang=zh (empty when fetched)
- https://dreamina.capcut.com/seedance/seedance-2-5
- https://dreamina.capcut.com/seedance/seedance-2-5-prompt
- https://dreamina.capcut.com/seedance/seedance-2-5-blender-model-workflow

API providers / gateways:
- https://apiframe.ai/guides/seedance-2-5-guide
- https://fal.ai/models/bytedance/seedance-2.5/reference-to-video/api
- https://fal.ai/models/bytedance/seedance-2.5/image-to-video/api
- https://fal.ai/learn/devs/seedance-2-5-vs-seedance-2-0 (2026-08-13)
- https://fal.ai/learn/devs/seedance-2-5-prompting-guide
- https://replicate.com/bytedance/seedance-2.5/api/schema (only metadata readable)
- https://docs.apiyi.com/en/api-capabilities/seedance2/overview
- https://docs.laozhang.ai/en/api-capabilities/seedance2-video-generation
- https://docs.venice.ai/guides/media/seedance-2-0
- https://www.atlascloud.ai/models/bytedance/seedance-2.5/reference-to-video
- https://evolink.ai/seedance-2-5
- https://aiseedance25.app/seedance-2-5-api
- https://github.com/Anil-matcha/awesome-seedance-2.5-api-prompts
- https://github.com/thoxakihiko/seedance-prompt-forge/pull/2 (merged 2026-09-27)
- https://github.com/Aayush-hoichoi/Seedance2.0/pull/110

News / reviews / pricing:
- https://technode.com/2026/07/31/bytedance-launches-seedance-2-5-video-generation-model/
- https://www.techtimes.com/articles/319639/20260703/bytedance-seedance-25-launches-this-week-30-second-ai-video-carries-copyright-cloud.htm
- https://www.qbitai.com/2026/07/464329.html
- https://kie.ai/blog/seedance-2-5-release-deep-dive
- https://cellcog.ai/blog/seedance-2-5-pricing/ (prices verified 2026-08-22)
- https://blog.segmind.com/seedance-2-5-review-five-real-world-use-cases-and-exactly-what-each-one-costs/
- https://atoms.dev/blog/seedance-2-5-review-30-second-ai-video-production-workflow
- https://www.virse.ai/blog/seedance-2-5-reddit-review
- https://leadde.ai/blog/where-to-use-seedance-2-5
- https://en.wikipedia.org/wiki/Seedance_2.0

Prompt craft / practitioner:
- https://lumalabs.ai/learning-center/articles/how-to-prompt-seedance-2.0
- https://github.com/issastash/AI_Complete_Prompting_Guides/blob/main/Seedance_2.0_Complete_Prompting_Guide.md
- https://picsart.com/blog/seedance-2-5-prompting-guide/
- https://www.heyuan110.com/posts/ai/2026-07-11-seedance-2-prompt-guide/
- https://morphic.com/resources/how-to/seedance-2-prompts-flagged-how-to-fix
- https://cozyclay.org/seedance-camera-control/
- https://www.portotheme.com/from-blender-blockout-to-final-shot-how-seedance-2-5s-3d-white-model-previz-changes-3d-workflows/
- https://www.seedance.tv/blog/seedance-2-5-lip-sync-issues
- https://www.seedance.tv/blog/how-to-keep-voices-consistent-in-seedance-2-5

Policy:
- https://creatide.ai/blog/seedance-25-copyright-faces-ip-and-commercial-use-risks (2026-08-29)
- https://ruoqijin.com/blog/seedance-access-and-face-policy
