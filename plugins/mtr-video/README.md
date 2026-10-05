# ai-film-studio

An AI film/video pipeline from concept to QC-passed deliverable, using Claude + Blender (Blender Lab MCP) + any AI video generation model. The pipeline is model-agnostic: each video model is described by a profile, and every model-dependent rule reads its limits from that profile.

## Skills

| Skill | Step | Job |
|---|---|---|
| `film-pipeline` | Orchestration | Project state, gates, common law, model selection, test plan |
| `concept-brainstorming` | 1 | Diverge → converge, rubric, AI-feasibility, lock concept |
| `story-development` | 2 | Treatment, beat sheet, Fountain script, anti-AI writing pass, rough units |
| `visual-bible` | 3 | Look, color script, character/location/prop/voice ref packs, consistency test |
| `shot-design` | 4 | Director's breakdown, camera language, performance cues, `shotlist.json` + profile-aware validator |
| `blender-previs` | 5 | Build previs via MCP, clay/seg/depth passes, manifest |
| `video-generation` | 6 | Model profiles, call strategy, reference manifests, prompts, lint, adapters, cost |
| `dailies-review` | 7 | Take QC, artifact taxonomy, rubric, fix routes, escalation |
| `post-assembly` | 8 | Edit, finishing, sound, mix, delivery specs, QC, legal |

Each skill has `references/knowledge.md` (research dated 02/10/2026, with sources). The common law is in `skills/film-pipeline/references/shared-conventions.md`.

## Video models

- Profiles live in `skills/video-generation/references/models/<id>/` (`profile.json` + `knowledge.md`), schema in `model-profile.schema.json`.
- Included: `seedance-2.5` (third-party verified, 2026-10-02) with an API adapter for BytePlus ModelArk.
- Add another model (Veo, Kling, Runway, Sora, Wan, Hailuo, Luma…) with `skills/video-generation/references/adding-a-model.md`: research, profile, optional adapter, calibration tests T1–T7.
- A project sets `film.video_model` and may override per unit (`units[].video_model`).

## Requirements

- Blender 5.1+ with Blender Lab MCP (running on a dedicated machine/VM, with Auto Run Python Scripts off).
- Access to at least one video model (API or UI). API keys go in environment variables, never in files.
- ffmpeg, Python 3 (`jsonschema`, `opentimelineio`, `opencv-python`, `numpy`); optional: DaVinci Resolve, Topaz Video AI, iZotope RX.

## Verification status (v0.3.0)

- Test-run on sample clips/data: `validate_shotlist.py` (with the Seedance profile and a single-shot test profile), `lint_prompt.py` (both profiles), `validate_profile.py`, `export_edit_list.py`, `qc_take.sh`, `conform.sh`, `assemble.py`, Seedance `build_request.py`; the remaining ffmpeg/OTIO scripts were tested during the research phase.
- Not yet run: Seedance adapter `client.py` (endpoint and parameters from third-party sources), `afs_previs_lib.py` in Blender 5.x (syntax-checked only), `identity_track.py` (requires a model download; InsightFace models are non-commercial only).
- Run the calibration tests T1–T7 for each model and T8–T10 once per project before production use.
