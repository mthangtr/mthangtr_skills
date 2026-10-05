# Adding a video model

The pipeline is model-agnostic: shot design, previs, review and post read model limits from a profile. Adding a model means writing its profile, its knowledge file, optionally an API adapter, and calibrating it.

## 1. Research (before writing anything)

Use web search and open primary sources first (vendor docs, model card, API reference, pricing page), then reputable third-party docs and practitioner reports. Record the date of every number. Collect:

- Output: fps, resolutions (native vs upscaled), ratios, min/max duration or fixed durations, extension.
- Shots: can one call contain several cuts? timecoded prompting? minimum useful shot length?
- References: image/video/audio counts and total seconds, tag syntax, roles (first/last frame, style, identity, motion, camera).
- Control: first/last frame, camera-following video reference, structure references (clay, depth, pose, edges), timestamp edit, seed, camera lock.
- Audio: native audio, dialogue lip-sync, languages, sample rate.
- Prompting guidance from the vendor: order, length, negative prompt field, dialogue format.
- Access: providers, API shape, pricing per second per resolution, whether reference seconds are billed, regions, URL expiry.
- Policy: real faces, photoreal AI faces, IP, watermark, C2PA, commercial terms.
- Known weaknesses.

## 2. Write the files

1. Copy `models/_template/` to `models/<id>/` (lowercase id, e.g. `veo-3.1`, `kling-3.0`). The folder name must equal `id`.
2. Fill `profile.json`. Set `verification` to the weakest source behind the numbers. Put every unconfirmed number in `open_questions` with its test ID.
3. Write `knowledge.md` with the same structure as `models/seedance-2.5/knowledge.md`: specs table with source and date per row, access and pricing, model-specific prompt rules, reference strategy, API notes, failure modes, examples, policy, open questions, sources.
4. Run `python3 scripts/validate_profile.py references/models/<id>/profile.json`.

## 3. Adapter (only for API use)

Create `scripts/adapters/<id>/` with two scripts that keep the same command-line contract as `scripts/adapters/seedance-2.5/`:

- `build_request.py prompt.md manifest.json out_request.json --duration S --ratio R [--resolution RES] [--seed N] [--task-type ...]` → provider-specific request body.
- `client.py request.json out.mp4 --unit U --take T [--log 05_takes/generation_log.jsonl] [--price-per-s P] [--ref-video-s S]` → submit, poll, download video (and last frame if returned), append one log line with the shared fields (ts, unit, take, model, task_id, seed, res, dur_out, dur_ref_video, usd_est, wall_s, status, verdict, prompt_sha).

Read API keys from environment variables only. Set `access[].adapter` to the folder name. UI-only models need no adapter: save prompt + manifest and log manually in the same format.

## 4. Calibrate (T1–T7, per model)

Run one short test unit (5–8 s) per question and write results into `project_state.json → validation_tests.<model id>` and back into the profile (`verification: "calibrated"` once all relevant tests pass):

| Test | Question |
|---|---|
| T1 | Actual output resolution, fps, duration and audio format (`ffprobe`) |
| T2 | API model id and parameters behave as documented |
| T3 | Which previs references work: clay, clay + depth, clay + seg, playblast, start frame only |
| T4 | Identity: one face image vs several angles (face-embedding similarity) |
| T5 | Continuity: last frame → first frame, alone and with a camera reference |
| T6 | Dialogue in each language the project needs: pronunciation, lip-sync |
| T7 | Policy: are photoreal AI faces or stylized likenesses blocked |

## 5. Using several models in one project

Set `film.video_model` as the default and `units[].video_model` to override per unit (for example one model for dialogue units with lip-sync, another for wide motion shots). Shot-design validates each unit against its own profile. Keep fps and color pipeline consistent: conform every model's output to `film.fps` in post.
