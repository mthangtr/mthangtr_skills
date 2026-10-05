---
name: visual-bible
description: >
  This skill should be used when the user needs the look of a film defined and locked before shot design or
  generation, e.g. "visual bible", "film style guide", "look book", "color script", "film color palette",
  "character sheet", "turnaround", "expression sheet", "character reference", "keep characters consistent",
  "character consistency", "character design", "voice reference", or when the look itself must change to remove
  the generic "AI look" (per-take defects go to dailies-review). It produces the bible and reference packs.
metadata:
  version: "0.3.0"
---

# Visual bible

Turn the script into **testable visual rules** and a clean reference set for downstream skills: `02_bible/bible.md`, `descriptors.yaml`, `ref_manifest.csv`, color script, ref packs for characters/locations/props/style/voice, and a consistency test. Detailed knowledge: `references/knowledge.md`. Common law: `../film-pipeline/references/shared-conventions.md`.

## Principles (knowledge.md §1)

- The bible commands, it does not inspire: every entry has a checkable value (hex, lens, aspect ratio, fixed descriptor sentence, file ID).
- Start from the characters; color follows emotion through each beat (color script).
- One reference holds one role only. Few and clean beats many and messy.
- Frozen vocabulary: copy `style_block`, `identity_block`, `costume_block` verbatim into every prompt; never substitute synonyms.
- Deliberate imperfection: specify wear, dirt, asymmetry, motivated lighting. The model by default makes everything smooth and new.
- Blender locks structure; character refs lock identity; style frames lock the look.

## Procedure (knowledge.md §2, template §3)

0. Write a 3-sentence look statement, including one "NOT like …" sentence.
1. Mood board of 12–24 images, each noting "what to take from this image".
2. Format & camera rules: aspect ratio, lens package, camera grammar, grain/film stock.
3. Color script: one color frame per beat (≥ 5 for a short), hex per act, at least one associative color.
4. Character bible: shape language, silhouette test, costume with wear and backstory, 7-image ref pack (§4.2).
5. Location bible: plan, 1–3 key angles, lighting key, time-of-day, wear.
6. Prop sheets for hero props: ≥ 3 views, dimensions, states.
7. Style frames: 3–6 "final look" frames.
8. Voice bible: 8–15 s samples, dry, single speaker, with consent recorded.
9. Consistency test: a 5–8 s clip for each main character with the ref pack; record drift level; adjust refs.
10. Gate → hand off to skill 4.

Present the look statement + color script for user approval before creating ref packs.

## Reference specs (knowledge.md §4)

- Ref pack per character: front, 3/4, profile, full-body turnaround, outfit, expression sheet, scale lineup.
- Same soft neutral lighting, plain gray background (~#808080), exactly one outfit, ≥ 1080p on the short side, high-quality PNG/JPEG, no text/watermark/border.
- Refs must be pre-"dirtied" (real skin, worn fabric) and in the same medium as the film.
- Send only 3–5 images + 1–2 videos per generation, even though the ceiling is 30/10/10.
- Re-anchor with original refs, not generated frames (unless deliberately chaining the last frame).
- Create refs with Seedream (same ByteDance family), Blender renders (props, sets, scale lineup) or real photos with consent. Lock approved refs as `_v01`; on change, use `_v02` + changelog.
- Check the chosen model's `policy` (real faces, photoreal AI faces, IP) in its profile; several models block real faces. Decide the character style early (calibration test T7).

## Anti-AI visual patterns (knowledge.md §6)

Block the 16 "AI look" patterns: waxy/plastic skin, overly smooth faces, same-face, uncanny eyes, HDR glow, default teal-orange, everything at golden hour, balanced centered hero framing, generic "cinematic 8k", oversaturation, overdesigned costumes, missing wear and dirt. Each pattern has a detection method and a fix via descriptor or reference strategy. Use the style vocabulary bank (§5) instead of advertising language.

## Gate (knowledge.md §7)

- [ ] Look statement, a single medium, `style_block` and `negative_block` ≤ 60 words, no "cinematic/8k/masterpiece".
- [ ] Color script covers all beats with hex; no default teal-orange without a reason.
- [ ] Each main character: verbatim identity/costume block with ≥ 2 identifying features, silhouette test passed, ref pack meets spec, consistency test run.
- [ ] Location, prop, voice refs complete; consent clearly recorded.
- [ ] Naming per §7 (IDs `C01`, `LOC01`, `PR01`); `descriptors.yaml` and `ref_manifest.csv` exported for skills 4–6.

When passed: update `project_state.json` and move to `shot-design`.
