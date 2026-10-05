---
name: dailies-review
description: >
  This skill should be used when the user needs generated takes reviewed, scored or fixed, e.g. "review take",
  "review the generated clips", "check AI video defects", "check continuity", "choose a take", "circle take",
  "dailies", "QC footage", "clip has broken hands / face", "lip-sync is off", "should I regenerate".
  It acts as script supervisor + VFX supervisor + QC operator and routes each take to accept, fix or regenerate.
metadata:
  version: "0.3.0"
---

# Dailies review

Review each take in `05_takes/<unit>/` against `03_shotlist.json`, score it, classify defects, choose (circle) a take and decide the fix route. Output to `06_review/`: `review_log.csv`, a markdown note per unit, contact sheets, `fix_notes.yaml` for skill 5/6. Detailed knowledge: `references/knowledge.md`. Scripts: `scripts/`. Common law: `../film-pipeline/references/shared-conventions.md`.

## Principles (knowledge.md §1)

- The shotlist is the contract: score by beat, framing, lens, move, duration, dialogue, continuity, not by "does it look nice".
- Claude sees only frames, not motion. Every judgment about motion is inferred from dense frames + metrics and must be escalated when needed (§8).
- Separate technical QC (file, codec, fps, black/freeze, loudness) from creative QC (beat, performance, continuity, artifacts).
- Name defects with the shared codes (`AI-ID`, `HD`, `PH`, `FL`, `FLT`, `AU`…, taxonomy §4).
- Choose the cheapest fix route that still meets the standard. Measure by cost per accepted second; max 3 regeneration rounds per unit.
- Audio is half the take: do not circle before measuring and listening to the audio.
- After a timestamp-edit, re-QC the unedited parts too.

## Per-take procedure (knowledge.md §2)

0. **Ingest & naming**: apply standard names, ffprobe.
1. **Automatic technical QC**: `scripts/qc_take.sh take.mp4 <duration> 24 06_review/qc` (spec, black/freeze/silence, loudness, peak). Exit 2 = technical fail → route R5.
2. **Contact sheet** with burned-in timecode (command in §5) → review the whole.
3. **Temporal pass**: `python3 scripts/temporal_qc.py take.mp4 --out take_temporal.csv` to find flicker, boiling, jump candidates; extract consecutive frame runs around each flagged point, crop into hands/eyes/text.
4. **Identity & continuity**: compare against the ref pack and the previous unit's last frame (checklist C1–C14 in §3). Optionally use `scripts/identity_track.py` (the InsightFace model is non-commercial only; commercial projects need a replacement model).
5. **Audio pass**: loudness, waveform/spectrogram, dialogue words correct, lip-sync.
6. **Score & decide**: rubric §6.1 (Beat 0.25 · Artifacts 0.20 · Performance 0.15 · Camera 0.15 · Continuity 0.15 · Audio 0.10). Any criterion = 0 is a gate fail. Follow decision tree §6.2.
7. **Human review gate**: send the user short escalation questions in the format `[Take] [timestamp] [issue] [yes/no question] [consequence]`.

## Fix routes

R0 accept · R1 trim/cut-around · R2 fix in post · R3 timestamp-edit · R4 extend · R5 regenerate with the same prompt · R6 regenerate with changed prompt/refs · R7 return to previs/shot design · R8 escalate. Each failed round must record "what changed"; no blind re-rolls. R6/R7 export `fix_notes.yaml` for skill 6 or 5.

## Mandatory escalation to a human (knowledge.md §8)

Motion quality (AI float, performance rhythm, foot sliding); every hero take before circling; lip-sync and voice quality; defects at the S1/S2 boundary; performance choices between two takes with equal scores; likeness, brand, sensitive content; hitting 80% of the regeneration budget; route R7; metrics and eyes disagree; regions too small to read.

## Anti-patterns (knowledge.md §9)

Accepting "good enough" artifacts; looking at only a few isolated frames; skipping audio; leaving to post what should be regenerated; endless regeneration; drifting from the shotlist; not re-QCing after an edit.

## Gate (knowledge.md §10)

Every unit has a circled take with `human_confirmed=Y` for hero takes; no S3 left in the in/out range to be used; continuity with adjacent units checked; `review_log.csv` complete (`in_sec`/`out_sec` in decimal seconds); cost updated in `project_state.json`.

Export the edit list for post: `python3 scripts/export_edit_list.py 06_review/review_log.csv 03_shotlist.json 05_takes 06_review/edit_list.csv`. When all units for a scene are ready, move to `post-assembly`.
