---
name: video-generation
description: >
  This skill should be used when the user wants to generate video clips for a shot list with any AI video
  model (Seedance, Veo, Kling, Runway, Sora, Wan, Hailuo, Luma or others), e.g. "generate the unit",
  "generate video from previs", "write a video prompt", "image-to-video", "attach references", "extend a clip",
  "fix a clip by timestamp", "which video model should I use", "add a new video model". It works from model
  profiles, compiles reference manifests and prompts, lints them, submits or logs calls and tracks cost.
metadata:
  version: "0.3.0"
---

# Video generation (model-agnostic)

Turn each unit in `03_shotlist.json` + references from `02_bible/` + previs from `04_previs/` into takes in `05_takes/<unit>/`, with prompt, manifest and cost log. The workflow does not depend on one model: every model-specific limit comes from a **model profile**.

Files:

- `references/generation-craft.md`: model-agnostic craft (principles, call strategy, prompt structure, references, continuity, failure modes, anti-AI prompt patterns).
- `references/models/<id>/profile.json`: limits and capabilities of one model (schema: `references/model-profile.schema.json`).
- `references/models/<id>/knowledge.md`: model-specific research, prompt rules, API notes, examples, sources.
- `references/adding-a-model.md`: how to research, profile, adapt and calibrate a new model.
- `scripts/lint_prompt.py`, `scripts/validate_profile.py`; API adapters in `scripts/adapters/<id>/`.
- Shared rules: `../film-pipeline/references/shared-conventions.md`.

Profiles available now: `seedance-2.5` (third-party verified, 2026-10-02). Template: `references/models/_template/`.

## 1. Choose the model

1. Read `film.video_model` and any `units[].video_model` in the shotlist. If none is set, ask the user which model and access they have (API or UI, provider, budget).
2. If the model has no profile, follow `references/adding-a-model.md`: research it with web search, write `profile.json` + `knowledge.md`, run `scripts/validate_profile.py`. Do not guess limits.
3. Compare the shotlist's needs with the profile: lip-sync dialogue, camera-following video reference, multi-shot calls, unit lengths, ratios. Report gaps. A project may use different models per unit (for example one for dialogue, one for motion).
4. If the profile's `verification` is not `calibrated` and T1–T7 have not run for this model, propose a 5–8 s test unit first (adding-a-model.md §4).

## 2. Per-unit procedure

1. **Preflight** against the profile: unit length within `output.duration_s` (or `allowed`), shot count ≤ `shots.max_shots_per_call`, each shot ≥ `shots.min_shot_s`, ratio in `output.ratios`, unit not `stale`. Mark `risk: multi_subject` if > 2 people interact physically. `shot-design/scripts/validate_shotlist.py` already checks these.
2. **Call strategy** (craft §2): one call per unit if the model cuts inside a call, otherwise one call per shot. With `control.video_reference_camera`, send the playblast; with only `first_frame`, build a look-developed start frame from the clay first frame + character refs using an image model, and describe the camera move in words.
3. **Reference manifest** (craft §4) → `05_takes/<unit>/manifest_<unit>_r<round>.json`. Stay within `references.recommended_*` and never above `*_max`. Clay is strictly grey; map characters with the seg pass.
4. **Prompt** → `prompt_<unit>_r<round>.md`, in the profile's `prompt.template` order (craft §3), plus the model-specific rules in its `knowledge.md`. Paste identity/costume/style blocks verbatim from `descriptors.yaml`.
5. **Lint**: `python3 scripts/lint_prompt.py prompt.md manifest.json --profile references/models/<id>/profile.json --unit-duration <s>`. Fix all errors.
6. **Draft** at the lowest useful resolution, 2–3 seeds:
   - API with an adapter (`access[].adapter`): `python3 scripts/adapters/<adapter>/build_request.py ...` then `python3 scripts/adapters/<adapter>/client.py request.json 05_takes/<unit>/<unit>_T<nn>_r<round>.mp4 --unit <unit> --take <take> --price-per-s <price> --ref-video-s <s>`. Keys only from environment variables.
   - UI or no adapter: give the user the prompt and the ordered reference list, then log the result manually in `05_takes/generation_log.jsonl` with the same fields.
7. Send takes to `dailies-review`.
8. **Fix pass**: one variable per round; use extension or timestamp edit when the profile supports them instead of full regeneration.
9. **Final** at the target resolution with the locked seed and prompt. Download immediately if `ingest.url_expiry_h` is set.
10. **Ingest**: ffprobe; trim `ingest.extra_frames`; resample audio to `ingest.resample_audio_hz`; name takes per shared-conventions §2; append to `generation_log.jsonl` (ts, unit, take, model, task_id, seed, res, dur_out, dur_ref_video, usd_est, wall_s, status, verdict, prompt_sha).

## 3. Continuity, dialogue, anti-patterns

- Continuity between calls: craft §5, using whatever the profile supports (extension, last → first frame, last frame as reference).
- Dialogue: craft §3. If `audio.dialogue_lip_sync` is false or the language is not in `audio.languages_tested`, test first (T6) or generate without dialogue and plan ADR/lip-sync in post.
- Anti-AI prompt patterns: craft §7, plus the model's own list in its `knowledge.md`.

## 4. Gate

Pre-submit: profile valid and selected; unit within profile limits; manifest within limits, no real likeness or IP unless the profile's policy and the consent log allow it; prompt passes lint; explicit parameters; estimated cost within budget (shared-conventions §1 formula with the profile's prices and reference billing).

Post-generate: downloaded, ffprobe confirmed, log complete, ≥ 2 takes for risky units, preliminary self-score on face, clothing, body scale, background, lighting, motion, camera continuity, lip-sync. Add cost to `project_state.json`; warn the user above 70% of budget. Then move to `dailies-review`.
