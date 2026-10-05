# Video generation craft (model-agnostic)

These rules hold for any current text/image/video-to-video model. Numbers that depend on a model (durations, reference limits, word counts, fps, prices) are never written here: read them from the active profile `models/<id>/profile.json`. Much of the field evidence behind these rules was gathered on Seedance 2.x in 2026 (see `models/seedance-2.5/knowledge.md` for sources); treat each rule as a strong default and confirm it during a model's calibration (T1–T7).

## 1. Core principles

1. **References decide form, the prompt decides intent.** Camera and layout come from previs (playblast or start frame), identity from character sheets, voice from audio refs. The prompt directs performance, light, material and timing.
2. **One narrow job per reference, stated in the prompt.** "Ref A controls only camera motion and blocking; do not copy its surfaces or lighting." A few well-labeled refs beat many mixed ones; reference capacity is not reference adherence.
3. **Write what the camera can see.** "She turns toward the window and pauses", not "make it emotional". Source: `performance.observable_behavior` in the shotlist.
4. **Complexity scales with duration.** One main action and one camera move per shot or time block; respect the profile's `shots.min_shot_s`.
5. **Write causality in order:** contact → resulting motion → sound → reaction. This reduces physics errors, the weakest area of every current model.
6. **Front-load what matters.** Identity and the primary action go first; models weight early tokens and early references more.
7. **One language per prompt.** Dialogue stays in the character's spoken language.
8. **Short constraints, grouped at the end** (or in the model's negative-prompt field if the profile has one). At most ~6 items.
9. **Change one variable per iteration** and log what changed.
10. **Measure cost per accepted, continuity-safe second**, not cost per generation.

## 2. Mapping a unit to model calls

Pick the strategy from the profile:

| Profile capability | Strategy |
|---|---|
| `shots.multi_shot_in_call = true` | One call per unit; timecoded blocks per shot; unit length ≤ `output.duration_s.max` |
| `multi_shot_in_call = false` | One call per shot; the unit is assembled in edit; continuity carried by start frames |
| `control.video_reference_camera = true` | Send the previs playblast as camera/blocking reference; do not redescribe the camera path |
| Only `control.first_frame` | Render a look-developed start frame from the clay first frame + character refs (image model), then image-to-video; describe the camera move in words |
| `control.last_frame = true` | Constrain both ends for match cuts and handoffs |
| `output.extension = true` | Extend instead of regenerating when only duration is missing |
| `control.edit_by_timestamp = true` | Fix local defects by edit instead of regenerating |

If a shot needs a capability the model lacks (lip-sync, a camera reference, a long take), either switch model for that unit (a project may use several profiles; record `video_model` per unit) or redesign the shot in shot-design.

## 3. Prompt structure

Use the profile's `prompt.template` order. Default order when the profile is silent:

```
[FORMAT]     duration, ratio, number of shots, cuts or one continuous take
[REFERENCES] what each reference controls and what it must not copy
[WORLD]      location, time of day, 2–3 concrete set details; light source + direction + quality
[TIMELINE]   one block per shot: framing, one camera move, one physical action with start → end state, sound
[LOOK]       lens feel, grain, texture as physical descriptors (from descriptors.yaml), never hype words
[AUDIO]      ambience, key SFX on cue, music: none | description
[KEEP]       same faces/wardrobe as references; prop states
[AVOID]      ≤ 6 short, specific items
```

- Paste `identity_block`, `costume_block` and `style_block` verbatim from `02_bible/descriptors.yaml`.
- Dialogue: straight double quotes; name the speaker and the silent listener (`A says: "…" — B listens, mouth closed`); one short line per block; numbers as words. Respect `prompt.max_words_per_dialogue_line`.
- Describe the whole duration including the settle beat at the end; undescribed tails drift.
- No on-screen text; titles and subtitles are made in post.

## 4. Reference strategy

| Purpose | Reference | Notes |
|---|---|---|
| Identity | Character sheet front, 3/4, profile + outfit, neutral light and background | Place first; re-anchor with original refs, never with generated frames |
| Body scale | Full-body sheet or scale lineup | Prevents height drift |
| Layout / camera / blocking | Clay playblast or clay first frame | Clay is strictly grey; map characters with the seg pass |
| Motion | Animated playblast or motion reference | "Motion only, do not copy appearance" |
| Look | 1–2 approved style frames | Name the attributes to take (palette, light), not the picture |
| Environment / props | Approved location and multi-angle prop images | Hero props rotate slowly or not at all |
| Voice | Clean single-speaker sample, no music or reverb | Only if `audio.native` and the model accepts audio refs |
| Continuity | Previous unit's last frame | As first frame, or as a reference image describing the exact end state |

Stay inside `references.recommended_*`; never exceed `*_max` or `*_total_s_max`. Resolve conflicts before sending: a day image with a night prompt, two contradicting style frames, a previs with flat light (say "do not copy lighting from the previs").

Manifest (`05_takes/<unit>/manifest_<unit>_r<round>.json`) per reference: `tag` (if the model has tag syntax), `type`, `role`, `file`, `url` (when uploaded), `duration_s` (video/audio), `job`, `do_not_copy`.

## 5. Continuity between calls

Ranked by reliability (check what the profile supports):

1. Extension of the previous clip.
2. Previous last frame → next first frame (pixel-matched join; check compatibility with a camera reference in T5).
3. Previous last frame as a reference image + an exact end-state description.

Rules: previs of unit N+1 starts at unit N's end pose and camera; keep ratio, resolution, seed family, voice ref and described room tone; re-supply character sheets every 2–3 extensions; prefer cutting at unit boundaries (cut on action, on eyeline) over forced continuous joins.

## 6. Failure modes → mitigation

| Failure | Mitigation |
|---|---|
| Identity drift late in the clip | Sheets first in the reference list; "same face and wardrobe as <ref> throughout"; shorter calls |
| Body scale drift | Full-body ref; previs proxies at fixed height |
| Multi-subject interaction breaks | Fewer subjects per block; step-by-step causality; hide contact with framing; insert shots |
| Floaty or impossible motion | Motion reference; one fast element per block; describe the end point ("lands, knees bend, stops") |
| Hands and fingers | Fewer hand close-ups; simple actions; choose takes; local edit |
| Prop morphing on rotation | Multi-angle prop refs; slow rotation; "shape and label unchanged" |
| Lip-sync late or drifting | One short line per block; MCU or tighter, face toward camera; isolated test first |
| Wrong speaker | Name the speaker and the silent listener |
| Voice drift | Same voice ref and verbatim voice description every call |
| Camera ignores instructions | One move per shot; with a camera reference, let it decide; use cuts instead of chained moves |
| Scenes blending | Respect min shot length; write "Cut to" |
| End-of-clip drift | Describe the full duration |
| Smooth "AI look" | Real light sources; skin texture, grain; "no slow motion" |
| Moderation reject | Profile `policy`; remove real likeness, IP, studio/film-stock names; write full production language |
| Close-ups break up at low resolution | Avoid long ECUs; upscale in post |

## 7. Anti-AI prompt patterns (before → after)

1. **Keyword soup.** "cinematic, 8k, masterpiece, ultra-detailed" → concrete subject, light source, framing, texture.
2. **Stacked or conflicting styles.** "elegant, gritty, dreamy, glossy" → one look described physically.
3. **Emotion word with no physical cue.** "He feels devastated" → "He lowers the phone to his knee; his jaw tightens; he looks at the floor."
4. **Too many actions per block.** Five beats in four seconds → one action per block; move the rest to another shot.
5. **Camera text contradicting the camera reference.** → "Camera path, framing and timing follow the previs reference exactly."
6. **Dialogue longer than the block.** → split the line across blocks or shots.
7. **Vague subject.** "A man walks down a street" → named character with ref, wardrobe, specific street, light source.
8. **"Fast" everywhere.** → only one fast element; the rest steady.
9. **Overlong negative list.** → ≤ 6 specific items.
10. **Mixed prompt languages.** → one language; dialogue in its spoken language.

`scripts/lint_prompt.py` checks patterns 1, 3, 4 (partially), 6, 9, 10 plus profile limits.

## 8. Economics

- Drafts at the lowest useful resolution, 2–3 seeds; finals only after dailies approval, with locked seed and prompt.
- Cost per call = output seconds × price + billed reference seconds (`access[].bills_reference_video_seconds`).
- Download outputs immediately when `ingest.url_expiry_h` is set.
- Track everything in `05_takes/generation_log.jsonl`.
