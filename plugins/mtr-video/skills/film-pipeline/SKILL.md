---
name: film-pipeline
description: >
  This skill should be used when the user starts, resumes or plans an AI film / video project as a whole, e.g.
  "start a film project", "make an AI film", "continue the film project", "what step are we on",
  "what's the next step", "project status", "estimate the film budget", "AI film budget", "production plan",
  or when another ai-film-studio skill needs the shared conventions, folder contract, gate status, validation
  tests T1–T10 or consent records. It orchestrates the 8 pipeline skills.
metadata:
  version: "0.3.0"
---

# Film pipeline (orchestrator)

Orchestrate the 8-step pipeline from concept to deliverable video. Do not produce creative content in this skill; read the project state, check gates, maintain the test plan and consent log, then hand off to the right skill.

## Common law (read before running any step)

Read `references/shared-conventions.md`. This file wins over every other file: model-agnostic rule (all model limits come from the active model profile), one project fps, `lens_mm` full-frame equivalent, `gen_ratio` separate from the delivery aspect, units sized by the model profile, audio resampled to 48 kHz, max 3 regeneration rounds per unit, IDs and folder structure, cost formula, test plan T1–T10.

## Pipeline

| # | Skill | Input | Main output | Gate |
|---|---|---|---|---|
| 1 | `concept-brainstorming` | Brief | `00_concept.md` | Rubric ≥ 75, no veto, user picks |
| 2 | `story-development` | Concept | `01_story/script.fountain`, beat sheet | `story-gate.md` pass, table read deviation ≤ 15% |
| 3 | `visual-bible` | Script | `02_bible/` + ref pack | Consistency test pass |
| 4 | `shot-design` | Script + bible | `03_shotlist.json` | Validator pass, user approves |
| 5 | `blender-previs` | Shotlist + bible | `04_previs/<unit>/v<###>/` | Self-check 0 errors, manifest complete |
| 6 | `video-generation` | Shotlist + bible + previs | `05_takes/<unit>/` | Lint pass, log + cost complete |
| 7 | `dailies-review` | Takes | `06_review/` + `edit_list.csv` | Every unit has a circled take |
| 8 | `post-assembly` | Edit list | `07_post/` deliverables | QC report pass |

Valid loops: 7 → 6 (R5/R6 regenerate), 7 → 5 or 7 → 4 (R7: fix previs or redesign the shot), 8 → 6 (`pickups.csv`). Do not skip a step while the previous gate has not passed, unless the user explicitly asks and accepts the risk (record it in `project_state.json → overrides`).

## Procedure

1. Locate the project folder (ask the user if there is none). If new, create the structure per shared-conventions §2 and `project_state.json` from `references/project-state-template.json`.
2. Read `project_state.json`: current step, gates passed, cost, tests T1–T10, which units are `stale`.
3. Report to the user in 2–3 lines: current step, missing gates, next step.
4. Model choice: make sure `film.video_model` is set and every model used has a valid profile (`video-generation/references/models/<id>/profile.json`); if not, hand off to `video-generation` to add it. Before steps 5–6 with a model for the first time, run its calibration tests T1–T7 (one 5–8 s test unit) and the pipeline tests T8–T10 once per project (shared-conventions §4); record results in `validation_tests.models.<id>` / `validation_tests.pipeline` and update the profile.
5. Invoke the corresponding skill. When the skill passes its gate, update `project_state.json` (gate, date, cumulative cost).
6. When `03_shotlist.json` bumps `revision`: mark the units in `changelog.units_affected` as `stale` and require rerunning previs/generate for them.

## Estimate

Use the formula in shared-conventions §1: `runtime_s × iteration_ratio × (1 + ref_video_s / output_s) × price/second`, plus a 30% buffer. Warn the user when generation cost exceeds 70% of budget; stop and ask when it exceeds 100%.

## Consent & rights

Maintain `consent_log` in `project_state.json`: for every voice, face, external asset, music track → source, license, date, evidence file. Do not move to step 8 while any entry lacks evidence.

## Orchestration principles

- The user is the director: the user picks the concept, approves the script, circles takes and locks picture. Claude proposes, ranks, and states risks before strengths.
- Run the anti-AI writing pass of `story-development` (knowledge.md §6) on any text others will read (pitch, synopsis, caption).
- Preserve evidence of human creative contribution (script, previs, edit decisions) for copyright purposes.
