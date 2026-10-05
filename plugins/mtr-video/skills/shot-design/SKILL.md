---
name: shot-design
description: >
  This skill should be used when the user needs a director's breakdown, shot list, coverage plan, blocking,
  camera language or performance direction for a scene, e.g. "shot list", "scene breakdown", "design the shots",
  "director's breakdown", "blocking", "camera angles", "direct the performance", "character expressions",
  "storyboard", "shooting script", "split into generation units", "song-to-shot map", or needs to create or
  validate shotlist.json.
metadata:
  version: "0.3.0"
---

# Shot design & directing

From the script + visual bible, create `03_shotlist.json`: the central contract read by `blender-previs` and `video-generation`. Detailed knowledge: `references/knowledge.md`. Schema: `references/shotlist.schema.json`, example: `references/shotlist.example.json`. Common law: `../film-pipeline/references/shared-conventions.md`.

## Principles (knowledge.md §1)

- Decision priority: Emotion > Story > Rhythm (Murch). Every shot serves a declared POV.
- Silent test: the shot list with the dialogue column removed still tells the story.
- Move the camera only with a motive: following a character, a reveal, a shift in power relations, an inner state.
- Acting is doing: write performance with action verbs and observable behavior, not emotional adjectives.
- For AI: one shot = one primary action + one primary camera instruction. Keep the camera still when the action is complex.

## Procedure (knowledge.md §2)

0. Read the script as a first-time viewer and note reactions.
1. Scene spine (McKee): conflict, opening value, beats, closing value, turning point. Put the strongest shot at the turning point.
2. Playable layer for each character (Weston): objective, action verb, facts, physical task, listening.
3. POV owner and camera stance (subjective/objective) for each scene.
4. Blocking (Katz: I/A/L/triangle), marks in meters, 180° axis.
5. Shot list: size, angle, lens (mm full-frame equivalent), DOF, move + motivation, composition, eyeline.
6. Edit plan: reaction shots, J/L cuts, coverage_alt for hero beats, shot-length rhythm.
7. Lighting intent: motivated source, key/fill ratio, Kelvin.
8. AI unitization: group shots into units, attach continuity anchors, mouth map, handoff. Set `film.video_model` (default model profile) and, where a unit needs another model, `units[].video_model`. Set `film.gen_ratio` (a ratio from the profile's `output.ratios` that contains the delivery frame, e.g. 2.39:1 → 21:9).

Music video: before step 5, build a song map from the waveform/song structure (intro, verse, chorus, drop) with timecodes; record for each shot the musical beat it lands on; never cut a unit across an important lyric; change the visual grammar at chorus/drop.

When the shotlist already has previs/takes and must be changed: bump `revision`, write `changelog.units_affected`, set `units[].status = "stale"`.

Present the user with a summary table of the shot list per scene (not JSON) for approval before finalizing the file.

## Lookup tables (knowledge.md §3–6)

- §3: size / angle / lens / DOF / move → effect → when to use, with AI reliability level.
- §4: coverage, 180°/30°, eyeline, screen direction, match on action, cut points; ASL by genre.
- §5: lighting ratio and Kelvin.
- §6: emotion/intention → physical cues table for close-ups and wides, with FACS AUs and micro-timing. Every shot with a character must have `intention`, `observable_behavior` (≥ 2 cues) and `intensity` 1–5; intensity ≥ 4 at most once per scene, at the turning point.

## Generation unit rules (knowledge.md §7)

- Unit = one model call: one continuous stretch with the same location, lighting state and wardrobe. Length and shot count come from the unit's model profile (`output.duration_s`, `shots.max_shots_per_call`; one shot per unit if `multi_shot_in_call` is false). Hero shots may be 1-shot units.
- Each shot's `duration_s` is the generated length, ≥ the profile's `shots.min_shot_s`. Record a faster rhythm in `edit.target_cut_s` and cut it in post.
- If no profile exists for the chosen model yet, create it first (`video-generation/references/adding-a-model.md`); unit design depends on it.
- No two camera moves at once; the character finishes the action before the camera moves.
- Generate hero shots separately to get many takes; group connective shots into units.
- Complex multi-person interaction: split shots, cut around the contact point.
- Repeat the final action of unit N at the start of unit N+1 for match on action; add a 0.5–1 s handle.
- Repeat continuity anchors verbatim in every unit: identity block, screen position, eyeline, lighting state, prop state, lens family, mouth map.
- Safe moves: static, slow push/pull, slow pan/tilt, simple follow tracking. Risky: orbit around a face, handheld, whip pan, dolly zoom, crowds, small hand manipulation.

## Anti-AI shot patterns (knowledge.md §8)

Block: every shot moving, slow push-ins everywhere, unmotivated orbits, drone establishing on every scene, all close-ups or all wides, balanced centered framing all the time, rampant slow motion, characters looking straight into the camera, generic "epic" angles, unmotivated lens flares, uniform shot lengths. Measured thresholds: static ≥ 40% (drama), push-in ≤ 25%, centered ≤ 40%, slow-mo ≤ 10%, CU ≤ 50% per scene, shot-length CV ≥ 0.35.

## Validate

Run `python3 scripts/validate_shotlist.py 03_shotlist.json` (requires `jsonschema`). Errors: schema violations, missing model profile, unit length/shot count/ratio outside the unit's profile limits, `unit_time_s` gaps/overlaps or mismatch with `duration_s + handle_s`, shots shorter than the profile's `min_shot_s`, shots belonging to no unit or to two units, > 2 speakers per unit, moves without motivation, complex action with a moving camera, < 2 cues. Warnings: fps mismatch with the model (conform in post), dialogue on a model without lip-sync, anti-pattern thresholds and rhythm CV (computed from `edit.target_cut_s` if present). Fix all errors; for each warning, fix it or record a reason.

## Gate (knowledge.md §10)

Breakdown, camera language, continuity, performance, edit, AI, lighting: the whole checklist passes, the validator reports no errors, the user approves the summary table. When passed: update `project_state.json` and move to `blender-previs`.
