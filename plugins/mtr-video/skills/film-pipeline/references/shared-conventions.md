# 00 — Shared conventions, common contract and test plan

> Result of the cross-review of the 8 research files (02/10/2026), made model-agnostic in v0.3.0. This file is the "common law" of the `ai-film-studio` plugin. When a domain file contradicts this file, this file wins.

## 1. Unified technical conventions

The pipeline is **model-agnostic**. Anything that depends on the video model (call length, shots per call, minimum shot length, output fps and resolution, ratios, reference limits, audio, prices, policy) is read from the active model profile: `video-generation/references/models/<id>/profile.json`, selected by `film.video_model` (default) or `units[].video_model` (per unit). Never hard-code one model's numbers in another skill. Values in brackets below are the current `seedance-2.5` profile, given only as an example.

| Item | Convention | Source |
|---|---|---|
| Model selection | `film.video_model` required in `03_shotlist.json`; per-unit override allowed. A model without a profile is added via `video-generation/references/adding-a-model.md` before use | video-generation |
| Frame rate | One project fps (`film.fps`: 24, 25 or 30) for previs, edit and finishing. Prefer the main model's `output.fps` [24]. Outputs at another fps are conformed in post; delivery may change fps | 08 §4 |
| Lens | `shotlist.lens_mm` = full-frame equivalent (36×24 sensor). Blender defaults to `sensor_width = 36`. The S35 distance table in 05 §5.3 must be converted | 04 §9.1, 05 §5.1 |
| Aspect ratio | `film.aspect_ratio` = delivery frame (e.g. 2.39:1). `film.gen_ratio` = ratio sent to the model, must be in the profile's `output.ratios` [16:9, 9:16, 1:1, 4:3, 3:4, 21:9] and contain the delivery frame; crop/letterbox in post | profile |
| Master resolution | Assume the profile's `output.native_max_resolution` [720p]; conform at native resolution, upscale after picture lock | 08 §4 |
| Generation unit | One model call. Length within the profile's `output.duration_s` [4–30 s] including handles; shots per unit ≤ `shots.max_shots_per_call` [6], exactly 1 if `multi_shot_in_call` is false; 1 location + 1 lighting state; ≤ 2 speakers | 02 §8, 04 §7 |
| Shot length | `duration_s` (generated segment) ≥ the profile's `shots.min_shot_s` [3 s]. Shorter on-screen shots go in `edit.target_cut_s` and are trimmed in post | 04 §7 |
| Handles | `handle_s` (default 0) only at a unit tail or before a match cut, usually 0.5 s. In post, by default trim the first 8–12 and last 6–12 frames of each clip | 04 §7.2, 08 §3 |
| Audio | Resample model audio to 48 kHz/24-bit on ingest (profile `ingest.resample_audio_hz`; [32 kHz source]). Dialogue and music are almost always replaced in post. If the model has no lip-sync, plan ADR/lip-sync in post | 08 §5 |
| References | Stay within the profile's `references.recommended_*` [3–5 images, 1–2 videos]; never exceed `*_max` / `*_total_s_max`. One clear role per reference | 03 §4, generation-craft §4 |
| Clay & character mapping | Clay pass strictly grey. Map characters with a seg pass (one color per character); do not color the clay unless calibration test T3 shows it helps for that model | 05 §7.1 |
| Regeneration | Max 3 rounds/unit, each round records exactly what changed; track "cost per accepted second" | 07 §6 |
| Cost estimate | `runtime_s × iteration_ratio × (output_s + billed_ref_s) / output_s × price_per_s` with the profile's prices and `bills_reference_video_seconds`. Iteration ratio 6–10× for narrative with previs (estimate) | 01 §9, profile |
| Prompt language | One language per prompt; dialogue in its spoken language; a language not in `audio.languages_tested` must pass T6 first | generation-craft §3 |

## 2. Project structure and naming (contract between skills)

IDs: scene `S01`, shot `S01_010`, unit `U01`, character `C01`, location `LOC01`, prop `PR01`. Take: `<unit>_T<nn>_r<round>` (e.g. `U01_T03_r2.mp4`). Every skill uses exactly these IDs; do not use `SH###`, `CH01`.

```
project/
  project_state.json         ← film-pipeline: step, gate, cost, tests T1–T10, consent log
  00_concept.md              ← skill 1
  01_story/                  ← skill 2: beat_sheet.md, script.fountain, story-gate.md, tableread/
  02_bible/                  ← skill 3: bible.md, descriptors.yaml, ref_manifest.csv, color_script.png,
                               refs/{char,loc,prop,style,voice}/, tests/
  03_shotlist.json           ← skill 4: per shot-design/references/shotlist.schema.json (with revision + changelog)
  04_previs/<unit>/v<###>/   ← skill 5: AFS_<unit>_<pass>_v<###>.mp4, AFS_<shot>_<pass>_first|last_v<###>.png,
                               AFS_<unit>_camera_v<###>.json, AFS_<unit>_previs_manifest_v<###>.json, .blend
  05_takes/<unit>/           ← skill 6 (video-generation): <unit>_T<nn>_r<round>.mp4, <unit>_T<nn>_r<round>_last.png,
                               manifest_<unit>_r<round>.json, prompt_<unit>_r<round>.md, request_<unit>_r<round>.json
  05_takes/generation_log.jsonl ← skill 6: one line per call (model, task_id, unit, take, seed, params, ref_s, out_s, cost)
  06_review/                 ← skill 7: review_log.csv, <unit>_r<round>.md, contact/, fix_notes.yaml,
                               edit_list.csv (shot_id,file,in_sec,out_sec,note — circled takes, decimal seconds)
  07_post/                   ← skill 8: 01_conform/, 02_assembly/, 03_edit/, 04_finish/, 05_sound/, 06_deliver/,
                               qc/, pickups.csv (shot_id,unit,reason,needed_s,priority), archive/
```

Rules:

- A skill writes only to its own folder, reads upstream folders, and never edits upstream artifacts; to request a change, create a send-back request (`fix_notes.yaml` for R6/R7, `pickups.csv` for 8 → 6).
- When `03_shotlist.json` changes after previs has run: bump `revision`, write a `changelog` entry with `units_affected`, set `units[].status = "stale"` for those units. The orchestrator does not allow generating stale units.
- The scripts `post-assembly/scripts/assemble.py` and `shotlist_to_otio.py` read `06_review/edit_list.csv`.

## 3. Anti-AI patterns index (shared library)

| Layer | File/section | Content |
|---|---|---|
| Concept | 01 §6 | 12 clichéd premises + 11 failure modes of LLM brainstorming |
| Writing | 02 §6 | 21 patterns + grep list (Antislop data), blocklist of default LLM names |
| Visual | 03 §6 | 16 "AI look" patterns (waxy skin, same-face, teal-orange…) |
| Shot design | 04 §8 | 18 patterns with measurable thresholds (static ≥ 40% for drama, push-in ≤ 25%, centered ≤ 40%) |
| Previs | 05 §10 | 17 Blender technical anti-patterns |
| Prompt | video-generation/generation-craft §7 (+ each model knowledge file) | Keyword soup, emotion without a physical cue… (before/after) |
| Review | 07 §9 | 14 review anti-patterns |
| Post | 08 §10 | 17 signs of a "cheap AI film" in edit/color/sound |

When packaging the plugin: collect these into `shared/anti-patterns/*.md`; each skill runs its own layer's checklist at its gate and reruns the Writing layer on every text the user will read.

## 4. Mandatory test plan before production use

T1–T7 are **per-model calibration tests**: run them once for every model a project uses (procedure in `video-generation/references/adding-a-model.md` §4), record results in `project_state.json → validation_tests.<model id>`, and update that model's profile. T8–T10 are pipeline tests, run once per project.

| # | Scope | Question | Impact |
|---|---|---|---|
| T1 | per model | Actual output resolution, fps, duration and audio format (`ffprobe`) | Upscale and conform strategy |
| T2 | per model | API model id and parameters behave as documented | Adapter scripts |
| T3 | per model | Which previs references work: clay, clay + depth, clay + seg, playblast, start frame only | Previs output spec |
| T4 | per model | Identity: one face image vs several angles (face-embedding similarity) | Reference pack |
| T5 | per model | Continuity: last frame → first frame, alone and with a camera reference | Unit chaining |
| T6 | per model | Dialogue in each project language: pronunciation, lip-sync | Native audio vs ADR |
| T7 | per model | Policy: photoreal AI faces, stylized likeness | Character style choice |
| T8 | pipeline | FFmpeg output parameter names in Blender 5.x | PNG sequence fallback |
| T9 | pipeline | Automatic QC thresholds (flicker, identity) calibrated on 10 human-approved takes | Dailies review |
| T10 | pipeline | Actual price per accepted second over one 60 s short | Concept-stage estimates |

## 5. Legal risks to include in gates (not legal advice)

- Each model's `policy` block (real faces, photoreal AI faces, IP, watermark, C2PA, commercial use) and `access[].regions_excluded` must be checked before generating. Example: the Seedance 2.5 public API rejects real human faces and BytePlus international does not serve US, CA, UK, AU, NZ.
- EU AI Act Art. 50 applies from 02/08/2026: artistic/fictional works still need disclosure at a level that does not spoil the experience (08 §9).
- US Copyright Office: prompts alone do not create authorship; the human creative contribution (script, edit, previs, sound) must be preserved as evidence (08 §9).
- InsightFace pretrained models are for non-commercial research only (07 §11) → replace them for commercial use.
- AI music (Suno/Udio) is still in litigation; the ElevenLabs free plan prohibits commercial use (08 §9).
