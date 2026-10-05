---
name: post-assembly
description: >
  This skill should be used when the user needs AI-generated takes edited and finished into a deliverable,
  e.g. "edit the film from the takes", "assemble the approved clips", "rough cut", "picture lock", "make the final
  cut", "color grade", "upscale AI video", "sound design", "mix the audio", "loudness", "subtitles", "export for
  YouTube/TikTok", "export for delivery", "deliverables", "QC the final", "AI disclosure". It covers assembly,
  finishing, sound, mix, delivery, QC and archive.
metadata:
  version: "0.3.0"
---

# Post-assembly & delivery

Take the circled takes in `06_review/` to a QC-passed deliverables package in `07_post/` (use `07_post/qc/` for QC logs). Detailed knowledge: `references/knowledge.md`. Scripts: `scripts/`. Common law: `../film-pipeline/references/shared-conventions.md`.

## Principles (knowledge.md §1)

- Cut for emotion first, then story, then rhythm (Murch). Every cut has a reason: new information, a reaction or a change of thought.
- AI footage is raw material, like a camera take: the middle is usually usable, heads/tails often break. By default trim the first 8–12 frames and last 6–12 frames of each clip.
- Finish non-destructively in this order: conform → edit → lock → cleanup/deflicker → light denoise → upscale → grade → texture (grain/halation) → titles → encode.
- Sound is half the film. Model-generated dialogue and music almost always need replacing; use native audio as a guide track.
- Deliver to spec: loudness, true peak, color tags, fps, captions, AI disclosure are pass/fail criteria.
- Preserve evidence of human creative contribution (edit decisions, change lists) for copyright purposes.

## Procedure (knowledge.md §2)

0. **Ingest**: keep take names per shared-conventions §2 (`<unit>_T<nn>_r<round>`; on conform add the shot prefix: `S01_010_U01_T03_r2`), checksum, ffprobe, attach prompt/seed.
1. **Conform**: `scripts/conform.sh IN OUT 24` → `07_post/01_conform/`, ProRes 422 HQ, CFR, Rec.709 tags, PCM 48 kHz/24-bit, keep native resolution (pass W H only to pad onto the canvas, never scale up). Clips without audio get a silent track added.
2. **Assembly** from `06_review/edit_list.csv` (edit the `file` column to point to the conformed versions): `scripts/shotlist_to_otio.py` (OTIO/EDL/FCP7 XML for Resolve/Premiere) or `scripts/assemble.py` (quick viewing copy, fit + pad to canvas).
3. **Rough cut**: pick takes per the review log, trim broken heads/tails, temp music/VO. Record missing shots in `07_post/pickups.csv` (shot_id,unit,reason,needed_s,priority) for `video-generation`.
4. **Fine cut**: frame-level rhythm, J/L cuts, cutaways to hide defects. The user approves.
5. **Picture lock**: freeze timing, export EDL/XML + a reference with burned-in TC; every later change goes through a change list.
6. **Finishing** (§4): cleanup, deflicker, upscale (one consistent model per scene, check at 100% zoom), color management DaVinci Wide Gamut → Rec.709 Gamma 2.4, color match via scopes, grade per the visual bible, texture last.
7. **Sound** (§5): dialogue edit + cleanup, ADR via TTS/voice clone (only with written consent; no free plans for commercial use), Foley, SFX, ambience continuous across cuts, licensed music.
8. **Mix**: DX/MX/FX stems summed into a printmaster, M&E if needed; use `scripts/loudnorm2pass.sh` and `scripts/qc_audio.sh` to hit and measure the target.
9. **Deliver** (§6): ProRes master, per-platform encodes, captions, thumbnail, metadata, C2PA.
10. **QC** (§8): picture, audio, sync, captions, legal → QC report.
11. **Archive**: project, prompts, licenses, consent, two copies, checksums.

## Loudness targets (knowledge.md §5)

| Platform | Target | True peak |
|---|---|---|
| YouTube / TikTok / Instagram / Meta | −14 LUFS (industry practice, no public spec) | −1 dBTP |
| EBU R128 broadcast | −23 LUFS | −1 dBTP |
| ATSC A/85 (US TV) | −24 LKFS | −2 dBTP |
| Netflix | −27 LKFS ±2, dialog-gated | −2 dBTP |

ffmpeg cannot measure dialog-gated loudness; Netflix requires dedicated tools. Per-platform delivery specs (codec, bitrate, aspect, captions 42 characters/line, 20 characters/second) are in §6.

## Legal (knowledge.md §9, not legal advice)

EU AI Act Art. 50 applies from 02/08/2026 (artistic/fictional works still need disclosure at a level that does not spoil the experience); apply AI labels per YouTube/TikTok/Meta; C2PA content credentials; prompts alone do not create authorship in the US; AI music is still disputed; voice clones require consent. Remind the user to check with a lawyer for commercial projects.

## Anti-AI post patterns (knowledge.md §10)

Machine-even rhythm; every cut landing on the music beat; music wall-to-wall from start to end; overdone teal-orange grade; over-sharpened upscale with halos; denoise making skin plastic; keeping artifacts at clip heads/tails; generic stock whooshes; unmotivated speed ramps; ambience jumping at every cut.

## Gate (knowledge.md §11)

A Assembly → B Picture lock (user approves in writing) → C Finishing → D Sound & mix (loudness log saved in `07_post/qc/`) → E Delivery & QC (0 Critical, 0 Major; disclosure/C2PA handled; archive complete). When passed: update `project_state.json` and report the list of deliverables and their location to the user.
