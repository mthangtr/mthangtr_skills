# 08 — Post-Assembly: Edit, Finishing, Sound, Delivery & QC for AI footage

> **Model-agnostic note (v0.3.0):** this research was compiled with Seedance 2.5 as the reference video model. Every Seedance-specific number here (call length, ≤30 s units, ≥3 s shots, reference counts, 24 fps, 720p, 32 kHz audio, @Image tags, prices, policy) is an example from the `seedance-2.5` profile, not a pipeline rule. Read the real limits from the active profile (`video-generation/references/models/<id>/profile.json`) and apply `film-pipeline/references/shared-conventions.md`. Where this file says "skill 6", read `video-generation`; references like "06 §N" point to `video-generation/references/models/seedance-2.5/knowledge.md`.

> Scope: Skill 8 of the `ai-film-studio` plugin. Inputs are Seedance 2.5 clips that have passed dailies (skill 7), the planned shotlist/EDL (skill 4), the Blender previs (skill 5) and the visual bible (skill 3); output is a master + deliverables that pass professional QC.
> Research date: 2026-10-02. All platform specs cite source and date; these specs change frequently, so re-check them before every delivery.
> All ffmpeg/Python commands in this document were test-run on ffmpeg 6.1.1 and OpenTimelineIO 0.18.1 (Linux), except items marked "not tested".

---

## 1. Core principles

1. **Emotion comes first, continuity second.** Walter Murch's Rule of Six ranks cut criteria: Emotion 51%, Story 23%, Rhythm 10%, Eye-trace 7%, 2D plane of screen 5%, 3D space 4%. If a cut is emotionally right but breaks continuity, keep it; if it is continuity-correct but emotionally dead, drop it. For AI footage this is especially valuable: small continuity errors between generations (buttons, hair) are ignored by the audience if the emotional rhythm is right.
2. **"Every blink is a thought. Every thought is a cut."** Per Murch, the natural cut point is when a thought ends. Every cut needs a reason: new information, a reaction, or a change of idea. Cutting because "the AI clip ran out at 5 seconds" is the wrong reason.
3. **AI footage is raw material, not a finished product.** Treat each Seedance clip like a camera take: there is a usable part (usually the middle) and a broken part (the head and tail of a clip often show morphing, face drift, lighting jumps). The editor picks the best frames, not the whole clip.
4. **Finish in non-destructive order:** conform → edit → lock → upscale/denoise → color → texture (grain/halation) → titles → encode. No later step may force redoing an earlier one. Never grade on an 8-bit H.264 file that has been recompressed multiple times; always work on a 10-bit mezzanine (ProRes 422 HQ or DNxHR HQX).
5. **Sound is half the film.** Seedance native audio is useful as a guide track and sometimes usable for ambience, but dialogue, Foley and music almost always have to be replaced or re-layered to meet mix specs and split D/M/E stems.
6. **Deliver to spec, not by feel.** Loudness, true peak, color tags, frame rate, captions and AI disclosure are all pass/fail criteria. Run QC before anyone sees the "final" version.
7. **Document human contribution.** Per the US Copyright Office (Part 2, 01/2025), prompts alone do not create authorship, but human selection, arrangement and modification can be protected. Logs of edit decisions, grade, mix and sound design are important evidence.

---

## 2. Overall workflow (ingest → QC)

| # | Stage | Input | Main work | Output / Gate |
|---|-----------|---------|-----------|---------------|
| 0 | **Ingest** | Seedance clips (MP4 H.264, 480p/720p, 24 fps, AAC audio), shotlist CSV, previs | Standard naming `<shot_id>_<unit>_T<nn>_r<round>` (e.g. `S01_010_U01_T03_r2`), checksum (md5/xxhash), ffprobe metadata, store prompt/seed in a sidecar JSON | Read-only `05_takes/` folder + `media_manifest.csv` |
| 1 | **Conform** | Original clips | Normalize to CFR (24 fps), timeline size, ProRes 422 HQ, Rec.709 tags, PCM 48k/24-bit | `01_conform/*.mov` |
| 2 | **Assembly** | Shotlist + conform | Auto-build script order (OTIO → EDL/XML, or ffmpeg concat) | `assembly_v001` (long, not yet paced) |
| 3 | **Rough cut** | Assembly | Pick takes, trim broken heads/tails, scene structure, temp music/temp VO | Rough cut + list of shots to regenerate sent back to skill 6 |
| 4 | **Fine cut** | Rough + regen | Frame-level pacing, J/L cuts, cutaways to hide errors, temp mix | Fine cut approved by director/client |
| 5 | **Picture lock** | Fine cut | Freeze timing. Export EDL/XML/AAF + reference video with burned-in TC | `LOCK_v01` — after this milestone every change must go through a change list |
| 6 | **Finishing** | Lock | Upscale, denoise/deflicker, VFX cleanup, color match, grade, texture | Graded textless master |
| 7 | **Sound** | Lock + OMF/AAF | Dialogue edit, ADR/TTS, Foley, SFX, ambience, music | DAW session with stems |
| 8 | **Mix** | Sound edit | Mix to target loudness, D/M/E stems, M&E | Printmaster + stems |
| 9 | **Deliver** | Picture + mix | ProRes master, per-platform encodes, captions, thumbnails, metadata, C2PA | Deliverables package |
| 10 | **QC** | Deliverables | Check picture/audio/sync/captions/legal (section 8) | Pass/Fail QC report |
| 11 | **Archive** | Everything | Package project, prompts, licenses, consent | `ARCHIVE_<project>_<date>` |

**Recommended folder structure**

```
project/07_post/          (per shared-conventions §2; original takes in 05_takes/ are read-only)
  01_conform/     ProRes 422 HQ, CFR, tagged, media_manifest.csv
  02_assembly/    otio/, edl/, xml/ generated from 06_review/edit_list.csv
  03_edit/        NLE project, ref_exports/, change lists
  04_finish/      cleanup, Topaz outputs (UPSCALE_<model>_<scale>), Resolve DRP, LUTs, stills
  05_sound/       dialogue/, sfx/, foley/, music/, stems/, mix/
  06_deliver/     master/, web/, social/, captions/, thumbs/
  qc/             reports, loudness logs
  pickups.csv     shots needing extra generation → skill 6
  archive/        licenses/, consent/, prompts/
```

---

## 3. Editing craft for AI footage

### 3.1 Cutting stages

- **Assembly:** lay every shot in script order, keeping handles. The goal is to see the whole story, not the pacing. Usually 30–60% longer than the final cut.
- **Rough cut:** pick the best take per shot, drop redundant shots, define structure. This is when to build the **regen list**: any broken shot that cannot be saved by edit or VFX goes back to skill 6 with specific notes (which frame, what error).
- **Fine cut:** refine frame by frame, overlap audio (J/L cuts), add cutaways/inserts, check pacing across the whole film. Review at real speed, not by scrubbing.
- **Lock:** freeze timing. After lock, change only via versioned change lists; sound and color run in parallel off the lock.

### 3.2 Pacing and cut points

- **Cut on action:** cut mid-movement (reaching hand, head turn, standing up); the viewer's eye follows the motion so the "jump" goes unnoticed. With AI, motion is often slower and smoother than reality; cut earlier, before the action finishes, to keep energy.
- **Eye-trace:** place shot B's subject near where the viewer's eye is at the end of shot A. In 9:16 this matters even more because the frame is narrow.
- **J-cut / L-cut:** let the next shot's audio start before its picture (J) or let the previous shot's audio run over the next picture (L). This is the strongest tool for hiding that AI clips were generated independently: a continuous audio layer "stitches" the shots together.
- **Varied rhythm:** shot lengths must vary. Working rule: never have more than 3 consecutive shots whose lengths differ by less than 10%. In tense scenes shots get progressively shorter; in emotional scenes hold long on reactions.
- **Hold reactions:** the audience feels through the listener's face. If an AI clip has good expression but bad lip-sync, use it as a reaction shot with off-screen dialogue.
- **Montage:** use only to compress time or build meaning through juxtaposition (match cuts on shape, color, motion). Montage is not a way to use up all the pretty clips.

### 3.3 Editing around AI artifacts

| Artifact | Typical location | Handling in edit |
|----------|-------------------|------------------------|
| Morphing / face drift | First and last 0.3–1s of a clip, or when the character turns away | Trim head/tail; use the middle; default drop the first 8–12 frames and last 6–12 frames (24 fps), then adjust |
| Wrong hands/fingers | Close-ups of manipulation | Cutaway to face/object; reframe (punch-in 10–20% after upscale) |
| Gibberish text/signage | Background | Reframe, light blur, or VFX text replacement (Fusion/After Effects) |
| Light/color jumps between clips | Shot boundaries | Color match in finishing; cut on motion to hide |
| Wrong physics (objects passing through each other) | Object interaction | Cut before the moment of contact; use sound design to imply the action off-screen |
| Lip-sync drift | Long dialogue | Cut to reaction/over-the-shoulder; off-screen dialogue; ADR |
| In-clip multi-shot (Seedance cuts internally in one pass) | Anywhere | Treat each sub-shot as a separate clip; split at internal cut points (ffmpeg `scdet` helps find them) |

**Golden rule:** if an error is only visible when paused, it may be acceptable for web; if it is visible at real speed, it must be fixed (trim, cutaway, VFX or regen).

### 3.4 Automating the first assembly

Pipeline: `06_review/edit_list.csv` (from skill 7 via `export_edit_list.py`, with `in_sec/out_sec`; subtract extra head/tail when cutting) → `shotlist_to_otio.py` → `.otio` + `.edl` (CMX3600) + `.xml` (FCP7 XML) → import into Resolve/Premiere. In parallel, `assemble.py` renders a quick-review version with ffmpeg. Note: CMX3600 EDL holds only one video track and reel names get truncated (OTIO notes `OTIO TRUNCATED REEL NAME`); use FCP7 XML when you need multiple tracks/markers. Run on conformed files so source timecode matches timeline fps. Scripts in section 7.

---

## 4. Finishing AI footage (upscale, denoise, grade)

### 4.1 Source reality

- Seedance 2.5 (launched 31/07/2026): per a summary of BytePlus API docs, model `dreamina-seedance-2-5-260628` outputs **480p and 720p, 24 fps, 4–30s per pass, with native audio**; 1080p/4K was **not** in the API docs at the time that page was written. Some resellers (Artlist, Morphic) advertise 1080p or 4K — see section 12. Design the pipeline for the worst case: **720p24, 8-bit 4:2:0, heavily compressed H.264**.
- Consequences: (a) must upscale 1.5× (→1080p) or 3× (→4K); (b) banding and macroblocking in dark/sky areas; (c) no color headroom for heavy grading.

### 4.2 Image processing order (verified in practice)

```
Conform (CFR 24, ProRes 422 HQ)
 → VFX cleanup at native resolution (paint, patch, text replacement)
 → Deflicker (if there is luma flicker)
 → LIGHT denoise / deblock (only when needed)
 → Upscale (Topaz / Resolve) → ProRes 422 HQ or 4444
 → Color: match → primary → secondary → look
 → Texture: grain, halation, softness, vignette (last)
 → Titles/graphics (no grain on text)
 → Encode deliverables
```

Reason: upscaling amplifies everything, including errors; grain must be added **after** upscale and after grade, otherwise the upscaler treats grain as detail and "repaints" it into patterns.

### 4.3 Upscale — tools and settings (September–October 2026)

| Tool / Model | Use when | Starting settings | Risk |
|-----------------|----------|---------------------|--------|
| **Topaz Starlight Precise 2.6** (diffusion) | 480/720p AI footage needing realism, reducing "plastic" | 720→1080 (1.5×) or →2160; Speed Boost (per Topaz: up to 10× faster at 2× credits) for review versions; run the final at full quality | May "invent" different detail between shots → check character face consistency |
| **Topaz Starlight Fast 3** | Dailies/preview upscale, tight deadlines | Per Topaz: ~4× faster than Precise | Less detail |
| **Topaz Astra 2** | Stylized content needing "creative" upscale | Low Creativity (0.1–0.3) for a live-action look | High Creativity → changes character identity |
| **Topaz Proteus (Natural)** | Conservative 2× upscale without creating new detail | Default; disable/reduce sharpen | Safest for identity, less "wow" |
| **Topaz Apollo** | Frame interpolation / slow-mo | 24→48 for 50% slow-mo; do not use to convert 24→30 for film | Ghosting around hands/hair |
| **Topaz Hyperion 2.5** | SDR→HDR (if HDR is mandatory) | Only when the client requires HDR | HDR from an 8-bit 720p source rarely passes high-end QC |
| **DaVinci Resolve Super Scale** (Studio) | In-timeline upscale, fast | Clip Attributes → Super Scale 2×, low Sharpness/Noise Reduction | Less "reconstruction" than diffusion |
| **Resolve 21 AI UltraSharpen** | Clarifying soft images, upscaling difficult footage | Test on 1–2 shots first | New feature (04/2026), test for halo |
| **Practical-RIFE 4.22.lite** (open source) | Interpolation for diffusion-model video | `inference_video.py --exp=1`; `--scale=0.5` for 4K | Needs GPU; artifacts at occlusions |

**Upscale rules:**
- Export from the upscaler to **ProRes 422 HQ or 4444**, not H.264.
- Keep one model for an entire scene (consistency). Name files `S01_010_U01_T03_STARLIGHTP26_2160.mov`.
- Check at 100% zoom: eyes, teeth, hair, high-contrast edges (halo), text.
- Disable or reduce sharpening in the upscaler; sharpen afterwards (if needed) by hand in very small amounts.
- If the deliverable is only social 1080×1920, 720p→1080p upscale is enough; 4K only when genuinely required (YouTube 4K for better bitrate is the only valid web reason).

### 4.4 Denoise, deflicker, temporal stabilization

- **Denoise:** AI footage is usually *too clean* rather than noisy; the common problem is **compression noise/macroblocking**. Use light temporal denoise (Resolve Temporal NR: Frames 2–3, low Luma/Chroma threshold; ffmpeg `hqdn3d=1.5:1.5:3:3`) to smooth blocks, then add grain to mask banding. Heavy denoise = "plastic skin".
- **Deflicker:** Resolve Studio has Deflicker (Resolve FX); ffmpeg has `deflicker=size=5:mode=pm`. Apply only to shots with luma flicker (usually from diffusion), not to the whole timeline.
- **Temporal "boiling" (boiling texture):** reduce with light temporal NR or a very light `tmix=frames=2` on background areas (masked). If the "boil" is on the face → regen.
- **Stabilization:** AI camera moves can have micro-jitter; Resolve Stabilizer (Perspective/Similarity, Smooth 0.25–0.4), or accept it if it fits a handheld style.

### 4.5 Frame-rate conformance

- Seedance 2.5 outputs 24 fps (per the summarized BytePlus docs). **The timeline should be 24 fps** (or 23.976 if a North American broadcast client requires it).
- **24 → 25 (PAL/EU broadcast):** the standard method is a 4.17% *speed-up* (every frame kept, the film gets shorter), audio pitch-corrected. Do not blend frames.
- **24 → 30/29.97:** not required for social; YouTube/TikTok/Instagram accept 24 fps. If the client mandates 30: use 2:3 pulldown or optical flow (RIFE/Apollo/Resolve Optical Flow) and QC artifacts. ffmpeg `minterpolate` is for preview only.
- **Stray-fps clips** (e.g. a clip from another source at 30 fps): if the content was built for 24, *retime* (`setpts`) instead of dropping frames; if it is real motion, use `fps=24` (drop) or optical flow.
- Always check for VFR: `ffprobe -show_entries stream=r_frame_rate,avg_frame_rate`; if the two values differ → conform to CFR before editing.

### 4.6 Color management & grading (Resolve)

**Suggested project settings (per Cullen Kelly / Frame.io, adjusted for AI sources):**
- Color science: DaVinci YRGB Color Managed, Processing: Custom.
- Timeline color space: **DaVinci Wide Gamut / DaVinci Intermediate**.
- Input color space for AI clips: **Rec.709 Gamma 2.4** (AI sources are display-referred, not log). Check each clip, since Resolve sometimes auto-assigns the wrong input.
- Output: **Rec.709 Gamma 2.4** for broadcast/OTT masters (BT.1886 reference display). For web deliverables viewed mainly on Macs/phones, consider also exporting a "Rec.709-A" version (tag 1-1-1), or keep Gamma 2.4 and tag BT.709 (1-1-1) — decide upfront and be consistent.
- Output DRT: Luminance Mapping (or DaVinci DRT).

**Sample node tree for AI footage:**
```
01 Input check (CST if needed)
02 Balance / Exposure (match shot-to-shot)
03 Contrast (pivot ~0.435 in DWG/Intermediate)
04 Skin (Qualifier or Magic Mask v2 → hue vs hue, reduce skin saturation 5–10%)
05 Secondaries (Magic Mask for subject/background; Resolve 21: "render in place" cache matte)
06 Look (Film Look Creator, Color Blend 40–70%)
07 Texture (Grain, Halation, Bloom) — or keep on a Timeline node
08 Vignette (light, -0.2 to -0.4 stop)
Timeline: Output gamut limiter / broadcast safe
```

**Color match between generations:** use one hero frame per scene (taken from the visual bible), Shot Match (Resolve) as a starting point, then correct by hand using scopes (waveform, vectorscope, parade). Match blacks and whites first, skin next, background colors last.

**Grading for a "non-AI look":**
- **Skin tone:** place on the vectorscope skin-tone line; AI tends to push skin to saturated orange or plastic pink → reduce sat 5–15%, separate hue slightly.
- **Contrast:** AI is often "HDR-ish" (open shadows, compressed highlights). Drop blacks deeper, let highlights clip softly (roll-off), allow dark areas to be truly dark.
- **Avoid default teal-orange;** take the palette from the visual bible, not from presets.
- **Lens softness:** very light blur (0.3–0.8 px Gaussian) to break the "digital" sharpness on edges and hair (invideo recommends grade → grain → blur last).
- **Halation:** Film Look Creator or Dehancer; low strength, only around strong highlights.
- **Grain:** 35mm preset, low intensity; check at 100% then play back to judge cadence (grain is temporal). Grain must be *moving* (temporal), not a static overlay. Grain also helps prevent banding after web compression — but too much grain gets broken into blocks by the encoder; for web, use fine grain and a high enough bitrate.
- **Gate weave / flicker:** almost off; use only when the style requires it (retro).

### 4.7 VFX cleanup

- Magic Mask v2 (Resolve 20.1+) to isolate people/objects; Resolve 21 adds render-in-place matte.
- Paint/patch in Fusion for gibberish text, extra fingers (frame-by-frame if short).
- Face consistency: if a face deviates from the character sheet, prefer regen over deepfake-style face replacement (legal/ethical issues and Art. 50).
- Do cleanup **before** upscale when using paint, or **after** upscale when high resolution is needed for roto — pick one and be consistent per shot.

---

## 5. Sound design & mix

### 5.1 Keep or replace the model's native audio?

| Layer | Keep when | Replace when |
|-----|---------|----------|
| Dialogue | Almost never for professional deliverables; use as guide/temp | Always replace when you need clean stems, need to change lines, there are artifacts (distorted, robotic voice), or the voice does not match between clips |
| Ambience | Static setting, acceptable quality, no artifacts | When ambience jumps at every cut (the clearest sign of stitched clips) |
| Sync SFX | Small hits that match picture | SFX important to the story, needing control |
| Music | Never for the final (no stem separation, unclear rights) | Always |

Key reason: native audio is pre-mixed (D+M+E on one track), so you cannot build an M&E, cannot mix to spec, and different generations have different tone.

### 5.2 Dialogue

- **Dialogue edit:** one track per character; fill room tone between lines; 2–10 ms crossfade on every edit to avoid clicks.
- **Cleanup (iZotope RX 11/12, Resolve Voice Isolation, Dialogue Matcher 20.1):** iZotope's strategy: several light passes are more transparent than one heavy pass; always keep the original for comparison. Suggested order: De-click/Mouth De-click → De-hum → Dialogue Isolate / Spectral De-noise (light) → De-reverb (light) → EQ → compression. Dialogue Isolate for continuous background noise; Spectral Repair for intermittent noise.
- **ADR via TTS / voice clone:**
  - Clone a voice only with **written consent** from the voice owner (ElevenLabs ToS 31/03/2026: upload only your own voice or a voice you are authorized to use). Store consent in `00_docs/consent/`.
  - The ElevenLabs Free plan **may not be used commercially**; a paid plan is required.
  - Resolve 21 has an AI Speech Generator (text-to-speech with adjustable speed, pitch, inflection) — check commercial-use terms before using it in a delivered version.
  - Technique: generate many takes, splice syllables, add room tone and reverb matching the shot's space; EQ to cut some of the "studio clean" quality. Lip-sync: prefer adjusting the edit (slip audio a few frames) over AI lipsync on the face.
- **Off-screen dialogue** is AI footage's friend: put lines over reactions, wide shots, or the character's back.

### 5.3 Sound design layers

1. **Continuous ambience/room tone across cuts** (2–3 layer bed: air, distant, detail). This is the layer that "stitches" AI shots together; cut ambience at scene changes, not at shot changes.
2. **Foley:** footsteps, cloth, handled objects. AI footage has no real Foley; missing Foley makes the film "float".
3. **Hard SFX:** doors, cars, impacts — frame-accurate sync.
4. **Design/texture:** drones, risers — use sparingly, with motivation.
5. **Music:** score or licensed; allow deliberate silence.

Avoid default "trailer" whoosh/impact libraries on every transition (section 10).

### 5.4 Music and licensing (status 10/2026)

- **Suno:** settlement with Warner (25/11/2025): new "licensed" models launch in 2026, old models are retired, audio downloads only for paid accounts (capped), free songs cannot be downloaded. UMG and Sony are still suing Suno (D. Mass.), with a second suit filed 18/09/2026.
- **Udio:** settled with UMG (30/10/2025) and Warner (19/11/2025); per OpusClip (04/2026) Udio became a "walled garden" — no free download/export. Sony is still suing Udio (second suit 20/07/2026).
- **Consequences for commercial films:** AI music is a risk zone. Priority: (1) a human composer with a work-for-hire contract or clear license; (2) a production music library with a sync license for specific media/territory/term; (3) AI music only when the subscription plan permits commercial use, archive a dated ToS snapshot from the day of use, and understand that the output may not be copyrightable (risk of others reusing it).
- Keep a cue sheet (cue name, source, duration, license ID) for every delivery.

### 5.5 Mix, stems, loudness

**Minimum stems:** DX (dialogue), MX (music), FX (effects + Foley + ambience), summing to the printmaster (Netflix requires stems that "equal the mix when combined"). Add a full **M&E** (Music & Effects, with Foley fill replacing whatever lives in the dialogue track) if dubbing is possible. Format: WAV/BWF LPCM 48 kHz / 24-bit.

**Loudness target table**

| Destination | Integrated | Measured by | True peak max | Source (accessed 10/2026) |
|------|-----------|---------|---------------|-------------------------------|
| EBU R128 (European broadcast) | **-23.0 LUFS** (±1.0 LU for live/special; file-based typically ±0.5) | Whole programme, BS.1770 | **-1 dBTP** | EBU R128 v5 (11/2023); Fora Soft |
| ATSC A/85 / CALM Act (US TV, commercials) | **-24 LKFS** | Anchor element (dialogue) | -2 dBTP (common practice, see section 12) | Fora Soft; ATSC A/85:2013 |
| Netflix (near-field) | **-27 LKFS ±2 LU** | **Dialog-gated**, BS.1770 | **-2 dBTP** (limiter recommended at -2.3) | Netflix Sound Mix Spec v1.6 |
| Spotify (video podcast/music) | -14 LUFS (normalization; Loud -11, Quiet -19) | BS.1770 | < -1 dBTP; < -2 dBTP if master is louder than -14 | Spotify for Artists |
| YouTube / TikTok / Instagram / Meta ads | **-14 LUFS** in practice (YouTube turns down louder content; no official public spec) | Whole programme | -1 dBTP | Industry practice (section 12) |
| Festival/cinema (DCP) | LUFS not used; mix in a room calibrated to 85 dBC (Leq(m) for trailers/commercials) | — | — | Industry experience (section 12) |

**Process to hit target:**
1. Mix by ear at a fixed monitor level (79–82 dB SPL for small rooms when mixing TV/web).
2. Dialogue is the anchor: set dialogue level steadily first (short-term meter around target + 0–3 LU during dialogue).
3. True-peak limiter on the master bus at -1.0 (web), -1.0 (EBU), -2.0/-2.3 (Netflix/ATSC).
4. Measure the whole programme (Resolve Fairlight Loudness meter, iZotope Insight, or ffmpeg `ebur128`).
5. Adjust overall gain (no extra compression) to hit target; normalize first, then check true peak (Fora Soft warns that reversing the order recreates peaks).
6. ffmpeg 2-pass `loudnorm` is the *final normalization step for web*, not a substitute for mixing. If loudnorm reports "Dynamic" instead of "Linear" → it is compressing dynamics; go back to the DAW and lower peaks.
7. For Netflix -27 dialog-gated: ffmpeg `loudnorm`/`ebur128` do **not** dialog-gate; use a meter with Dialogue Intelligence (Dolby Media Meter or equivalent).
8. LRA: web/mobile 6–11 LU; broadcast/film allows wider. A 9:16 mix for phones should have a narrower LRA than the 16:9 version.

---

## 6. Delivery specs by platform

### 6.1 Master (mezzanine) — always create first

| Item | Recommended value |
|-----|---------------------|
| Codec | Apple ProRes 422 HQ (10-bit 4:2:2) — or ProRes 4444 if there is alpha/graphics; DNxHR HQX for Avid environments |
| Reference data rate | 1080p24 ProRes 422 HQ ≈ 176 Mb/s; 2160p24 ≈ 707 Mb/s (Apple ProRes White Paper, 04/2022) |
| Resolution | 1920×1080 or 3840×2160 (UHD); separate vertical master 1080×1920 if there is a real reframe |
| Frame rate | 24 (or 23.976 / 25 as required) CFR |
| Color | Rec.709 primaries, BT.1886 / Gamma 2.4 transfer, Rec.709 matrix; tag 1-1-1; video (legal) range |
| Audio | PCM 48 kHz/24-bit; stereo printmaster + stems (DX/MX/FX) + M&E |
| Variants | Textless master (no text/subtitles), titled version, burned-in subs version (if needed) |

### 6.2 Platform spec table

| Platform | Container / codec | Resolution & aspect | Bitrate | Audio | Notes | Source (date) |
|----------|-------------------|---------------------|---------|-------|---------|--------------|
| **YouTube** (upload) | MP4, H.264 High, progressive, 2 consecutive B-frames, closed GOP = ½ fps, moov at the front (faststart) | Per source; 16:9 | 1080p24–30: **8 Mb/s**; 1440p: 16; 2160p: **35–45 Mb/s** (SDR) | AAC-LC or Opus, 48 kHz, stereo **384 kb/s**, 5.1: 512 kb/s | Color BT.709 (primaries, transfer, matrix). Upload 4K to get a better playback codec/bitrate | YouTube Help 1722171 (accessed 02/10/2026) |
| **TikTok Ads** | .mp4/.mov/.mpeg/.avi | 9:16, 1:1, 16:9; minimum 720×1280 / 640×640 / 1280×720 | ≥ 516 kb/s | (not stated) | ≤ 500 MB; duration depends on placement (5–60s Pangle). In practice: deliver 1080×1920 H.264 | TikTok Ads Help (02/10/2026) |
| **Instagram Reels** | MP4/MOV, H.264 + AAC | 1080×1920 (9:16) | ≥ 3.5 Mb/s (third-party recommendation) | AAC | 3–90s; ≤ 1 GB; 30 fps recommended, 24/60 supported | Sendcove (updated 04/2026, third party) |
| **Instagram Feed** | MP4/MOV | 1080×1350 (4:5) recommended; 1:1; 1.91:1 | — | AAC | ≤ 60 minutes, ≤ 4 GB | Sendcove (04/2026) |
| **Meta Ads (FB/IG Reels/Stories)** | MP4/MOV H.264 | 9:16 for Reels/Stories; 4:5 for Feed; 1:1 | Per Ads Manager | AAC | Leave a safe zone of ~14% at top and ~35% at bottom for Reels (UI overlay) — check the current Meta template | Meta page blocks crawlers; see section 12 |
| **Spotify (video)** | — | — | — | -14 LUFS normalization | Applies to audio | Spotify for Artists |
| **Netflix (high-quality reference)** | IMF/ProRes per project spec | — | — | -27 LKFS dialog-gated, -2 dBTP, 48k/24, DX/MX/FX stems summing = mix | Subtitles: max 42 characters/line, 2 lines, 20 cps (adult) / 17 cps (children), 5/6s–7s | Netflix Partner Help (v1.6; Timed Text Style Guide) |
| **DCP (cinema/festival)** | JPEG2000 intra-frame, MXF; SMPTE (recommended) or Interop | 2K Flat 1998×1080, 2K Scope 2048×858 (4K: 3996×2160 / 4096×1716) | ≤ 250 Mb/s | 48 kHz/24-bit PCM, 5.1 (7.1/Atmos optional) | XYZ 12-bit, gamma 2.6. SMPTE supports 24/25/48. Tools: DCP-o-matic (free), Resolve Studio, easyDCP | Knut Erik Evensen (2021); container sizes from the DCI standard (see section 12) |

**General notes for social:**
- Upload a high-quality version (H.264 CRF 16–18 or 10–20 Mb/s 1080p) because the platform will recompress.
- 9:16 must be truly **reframed** in the NLE (position keyframes following the subject), not blind center-cropped. If the project is mainly vertical, ask skill 6 to generate 9:16 directly (Seedance supports 9:16).
- Safe zones: keep text and faces in the central area; place burned-in captions higher than the bottom edge (large MarginV) to avoid the UI.
- When uploading, enable the platform's AI label (section 9).

### 6.3 Captions / subtitles

- **SRT** for web/social (YouTube, Meta, TikTok accept SRT); **WebVTT** for web players; **IMSC1.1 (TTML)** for OTT/Netflix-style; **mov_text** when embedding soft subs in MP4.
- Rules (from the Netflix English Timed Text Style Guide): ≤ 42 characters/line, ≤ 2 lines, ≤ 20 cps (adult), min 5/6 second (20 frames @24), max 7 seconds; break lines after punctuation, before conjunctions/prepositions; do not separate articles from nouns or first names from last names; "bottom-heavy pyramid" shape.
- Vietnamese: count characters by accented grapheme; check that the font renders diacritics (for burn-in use a font with full Vietnamese support such as Inter, Be Vietnam Pro, Noto Sans).
- Social: burn-in (open captions) increases retention for sound-off viewing; still provide a soft SRT for accessibility.
- SDH: add sound descriptions `[door closes]`, speaker identification.

### 6.4 Thumbnails, metadata, archival

- Thumbnail: pick a real frame from the film (do not generate a thumbnail that misrepresents the content); 1280×720 (YouTube), 1080×1920 cover for Reels/TikTok with a central safe area.
- Metadata: title, description with an AI disclosure line (section 9), credits (including AI tools), language, music rights, C2PA manifest if used.
- Archival: ProRes master + stems + captions + project files (DRP, DAW session, OTIO) + prompts/seeds + licenses + consent + QC reports. Two copies in two locations, with checksums.

---

## 7. ffmpeg / OTIO script library

> Place in `skills/08-post-assembly/scripts/`. Commands tested on ffmpeg 6.1.1. File names and parameters are examples.

### 7.1 Source check (ingest)

```bash
# Inspect stream properties; detect VFR (r_frame_rate != avg_frame_rate)
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate,pix_fmt,color_space,color_transfer,color_primaries \
  -show_entries format=duration -of compact INPUT.mp4

# Checksum manifest
for f in 01_ingest/*.mp4; do echo "$(md5sum "$f" | cut -d' ' -f1),$f"; done > 01_ingest/media_manifest.csv

# Find internal cuts inside a multi-shot Seedance clip (scene-change score)
ffmpeg -hide_banner -i INPUT.mp4 -vf "scdet=threshold=10" -f null - 2>&1 | grep scdet
```

### 7.2 Conform to mezzanine (`conform.sh`)

> Canonical version: `scripts/conform.sh` (fixed after review: keeps native resolution by default, no upscaling before picture lock; W H only pad onto the canvas; automatically adds a silent track when a clip has no audio).
Note: the lanczos scale here is only to get a uniform timeline for editing. Upscaling for the final is done with Topaz/Resolve after lock, from the original source files (relink), not from the lanczos-scaled files.

### 7.3 Edit list → OTIO / EDL / FCP XML (`shotlist_to_otio.py`, canonical version in `scripts/`)

```python
#!/usr/bin/env python3
"""shotlist_to_otio.py edit_list.csv out_basename [fps]
Build a first assembly timeline from a shotlist CSV (shot_id,file,in_sec,out_sec,note)
and write .otio + CMX3600 .edl + FCP7 .xml (Resolve/Premiere importable).
Requires: pip install opentimelineio OpenTimelineIO-Plugins"""
import csv, os, subprocess, sys
import opentimelineio as otio

csv_path, base = sys.argv[1], sys.argv[2]
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 24.0
RT, TR = otio.opentime.RationalTime, otio.opentime.TimeRange

def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(out.stdout.strip())

tl = otio.schema.Timeline(name=os.path.basename(base))
v1 = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
a1 = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)
tl.tracks.extend([v1, a1])

with open(csv_path, newline="") as f:
    for row in csv.DictReader(f):
        start = RT(round(float(row["in_sec"]) * fps), fps)
        dur = RT(round((float(row["out_sec"]) - float(row["in_sec"])) * fps), fps)
        url = os.path.abspath(row["file"])
        for track in (v1, a1):
            clip = otio.schema.Clip(
                name=row["shot_id"],
                media_reference=otio.schema.ExternalReference(
                    target_url=url,
                    available_range=TR(RT(0, fps), RT(round(media_duration(url) * fps), fps))),
                source_range=TR(start, dur),
                metadata={"ai_film_studio": {"note": row.get("note", ""), "file": row["file"]}},
            )
            if track is v1 and row.get("note"):
                clip.markers.append(otio.schema.Marker(
                    name=row["note"], marked_range=TR(RT(0, fps), RT(1, fps)),
                    color=otio.schema.MarkerColor.RED))
            track.append(clip)

otio.adapters.write_to_file(tl, base + ".otio")
otio.adapters.write_to_file(tl, base + ".xml", adapter_name="fcp_xml")
edl_tl = otio.schema.Timeline(name=tl.name)          # CMX3600 = one video track only
edl_tl.tracks.append(v1.deepcopy())
otio.adapters.write_to_file(edl_tl, base + ".edl", adapter_name="cmx_3600")
print(f"timeline duration: {otio.opentime.to_timecode(tl.duration(), fps)}  clips: {len(v1)}")
```
Sample CSV:
```
shot_id,file,in_sec,out_sec,note
S01_010,01_conform/S01_010_U01_T01.mov,0.5,5.0,trim head/tail artifacts
S01_020,01_conform/S01_020_U01_T02.mov,0.4,4.2,
```
Test note: the `fcp_xml` adapter requires `available_range` on the media reference (if missing it fails with `NoneType ... start_time`). `fcpx_xml` (FCPX) is not in the installed 0.18.1 plugin package.

### 7.4 Quick-review assembly render (`assemble.py`)

> Canonical version: `scripts/assemble.py` (reads `06_review/edit_list.csv`; fit + pad to canvas; input must be conformed clips).
Use the `concat` filter (re-encode) instead of the concat demuxer `-f concat -c copy`, because demuxer copy can only cut at keyframes and requires every input to share the same codec/params.

### 7.5 Quick texture / finishing with ffmpeg (preview or small projects)

```bash
# Light lens softness + temporal grain + soft vignette (apply AFTER upscale and grade)
ffmpeg -i GRADED.mov -vf "gblur=sigma=0.4,noise=alls=6:allf=t+u,vignette=angle=PI/5:mode=forward,format=yuv422p10le" \
  -c:v prores_ks -profile:v 3 -c:a copy \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 TEXTURED.mov

# Mild temporal denoise / deblock before upscale (compression cleanup)
ffmpeg -i SRC.mov -vf "hqdn3d=1.5:1.5:3:3" -c:v prores_ks -profile:v 3 -c:a copy DENOISED.mov

# Deflicker a single shot (luma pumping)
ffmpeg -i SHOT.mov -vf "deflicker=size=5:mode=pm" -c:v prores_ks -profile:v 3 -c:a copy SHOT_dfl.mov

# Preview-only frame interpolation 24->30 (use RIFE/Topaz Apollo/Resolve Optical Flow for finals)
ffmpeg -i IN.mov -vf "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" -c:v libx264 -crf 18 OUT_30p.mp4

# 24 -> 25 PAL speed-up (no frame blending), audio tempo-corrected
ffmpeg -i IN.mov -vf "setpts=PTS*24/25" -r 25 -af "atempo=25/24" \
  -c:v prores_ks -profile:v 3 -c:a pcm_s24le OUT_25p.mov
```
ffmpeg's `noise` is simple digital grain (strength 0–100; `t` = temporal, `u` = uniform). For finals, use Film Look Creator/Dehancer or real grain scans to get grain structure and luma-dependent response.

### 7.6 RIFE (Practical-RIFE) — interpolation

```bash
# 2x interpolation (24 -> 48) for slow-motion; --scale 0.5 for 4K sources
python3 inference_video.py --exp=1 --video=S01_040.mp4
python3 inference_video.py --exp=1 --video=SH040_4k.mp4 --scale=0.5
# Repo recommends Practical-RIFE 4.22.lite for diffusion-generated video post-processing. (not tested: requires GPU)
```

### 7.7 2-pass loudness (`loudnorm2pass.sh`) and QC measurement

```bash
#!/usr/bin/env bash
# loudnorm2pass.sh IN OUT.wav [I] [TP] [LRA]
# Defaults: -14 LUFS / -1 dBTP / LRA 11 (web). EBU: -23 -1 ; ATSC: -24 -2.
# Netflix -27 is DIALOG-GATED: verify with a dialog-gated meter, not loudnorm.
set -euo pipefail
IN="$1"; OUT="$2"; I="${3:--14}"; TP="${4:--1}"; LRA="${5:-11}"
JSON=$(ffmpeg -hide_banner -nostats -i "$IN" -vn \
  -af "loudnorm=I=${I}:TP=${TP}:LRA=${LRA}:print_format=json" -f null - 2>&1 \
  | sed -n '/^{/,/^}/p')
get() { echo "$JSON" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
MI=$(get input_i); MTP=$(get input_tp); MLRA=$(get input_lra); MT=$(get input_thresh); OFF=$(get target_offset)
echo "pass1: I=$MI TP=$MTP LRA=$MLRA thresh=$MT offset=$OFF"
ffmpeg -hide_banner -y -i "$IN" -vn \
  -af "loudnorm=I=${I}:TP=${TP}:LRA=${LRA}:measured_I=${MI}:measured_TP=${MTP}:measured_LRA=${MLRA}:measured_thresh=${MT}:offset=${OFF}:linear=true:print_format=summary,aresample=48000" \
  -c:a pcm_s24le "$OUT" 2>&1 | grep -E "Normalization Type|Output Integrated|Output True Peak"
```
Test result: input -22.3 LUFS → output -13.8 LUFS, "Normalization Type: Linear". The `loudnorm` filter defaults are I=-24, TP=-2, LRA=7 — always state parameters explicitly. `aresample=48000` is required because loudnorm internally upsamples to 192 kHz.

```bash
# qc_audio.sh FILE -> integrated, LRA, true peak (BS.1770 / R128 scanner)
ffmpeg -hide_banner -nostats -i "$1" -vn -filter_complex ebur128=peak=true -f null - 2>&1 | sed -n '/Summary:/,$p'
```

### 7.8 Mux and encode deliverables

```bash
# Master: graded picture + final mix (PCM)
ffmpeg -i TEXTURED.mov -i MIX_PRINTMASTER.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s24le -shortest MASTER_ProResHQ.mov

# Add stems as extra tracks (mix, DX, MX, FX) in the master
ffmpeg -i MASTER_ProResHQ.mov -i DX.wav -i MX.wav -i FX.wav -map 0:v -map 0:a -map 1:a -map 2:a -map 3:a \
  -c copy -metadata:s:a:0 title=MIX -metadata:s:a:1 title=DX -metadata:s:a:2 title=MX -metadata:s:a:3 title=FX MASTER_stems.mov

# YouTube 1080p24 H.264 (closed GOP = half frame rate, 2 B-frames, faststart, BT.709 tags)
ffmpeg -i MASTER_ProResHQ.mov -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p \
  -b:v 10M -maxrate 12M -bufsize 20M -bf 2 -g 12 -x264-params "keyint=12:min-keyint=12:open-gop=0" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 384k -ar 48000 -movflags +faststart YT_1080p24.mp4

# YouTube 2160p24 (after real upscale): -b:v 40M -maxrate 45M -bufsize 80M

# Vertical 9:16 (center crop shown; do real reframing in the NLE for finals)
ffmpeg -i MASTER_ProResHQ.mov -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -maxrate 15M -bufsize 30M \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart SOCIAL_1080x1920.mp4

# HEVC 10-bit high-quality web/client review (hvc1 tag for Apple playback)
ffmpeg -i MASTER_ProResHQ.mov -c:v libx265 -preset slow -crf 18 -pix_fmt yuv420p10le -tag:v hvc1 \
  -x265-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" \
  -c:a aac -b:a 320k -movflags +faststart REVIEW_HEVC.mp4

# DNxHR HQX mezzanine (Avid / broadcast houses)
ffmpeg -i MASTER_ProResHQ.mov -c:v dnxhd -profile:v dnxhr_hqx -pix_fmt yuv422p10le -c:a pcm_s24le MASTER_DNxHR_HQX.mxf
```
x264 `-tune grain` preserves grain better when there is a lot of grain (with a higher bitrate).

### 7.9 Subtitles

```bash
# Burn-in (open captions) - font must support Vietnamese diacritics
ffmpeg -i YT_1080p24.mp4 -vf "subtitles=subs_vi.srt:force_style='FontName=Inter,FontSize=22,Outline=1,Shadow=0,MarginV=60'" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart YT_1080p24_burned.mp4

# Soft subtitles in MP4 (mov_text), language-tagged
ffmpeg -i YT_1080p24.mp4 -i subs_vi.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=vie YT_1080p24_softsub.mp4

# SRT -> WebVTT
ffmpeg -i subs_vi.srt subs_vi.vtt
```

### 7.10 Thumbnails and automated QC

```bash
# Representative-frame thumbnail
ffmpeg -i MASTER_ProResHQ.mov -vf "thumbnail=48,scale=1280:720" -frames:v 1 -update 1 thumb.jpg

# Black frames, freeze frames, silence gaps
ffmpeg -hide_banner -nostats -i DELIVERABLE.mp4 \
  -vf "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=-60dB:d=0.5" \
  -af "silencedetect=n=-60dB:d=1" -f null - 2>&1 | grep -E "black_|freeze_|silence_"

# Out-of-range (illegal) luma/chroma report: signalstats per frame (YMIN<64 or YMAX>940 for 10-bit legal)
ffmpeg -i MASTER_ProResHQ.mov -vf "signalstats,metadata=print:key=lavfi.signalstats.YMAX:file=ymax.log" -f null -

# Verify tags of a deliverable
ffprobe -v error -show_entries stream=codec_type,codec_name,profile,pix_fmt,width,height,r_frame_rate,color_space,color_transfer,color_primaries,sample_rate,channels -of compact DELIVERABLE.mp4
```

### 7.11 C2PA content credentials (c2patool)

```bash
# Read existing credentials (e.g., if Seedance/BytePlus embeds a manifest)
c2patool S01_010_U01_T01.mp4
# Add a manifest declaring AI generation + human editing; output must keep same extension
c2patool MASTER.mp4 -m manifest.json -o MASTER_c2pa.mp4
```
```json
{
  "claim_generator_info": [{"name": "ai-film-studio", "version": "1.0"}],
  "assertions": [
    {"label": "c2pa.actions",
     "data": {"actions": [
       {"action": "c2pa.created",
        "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"},
       {"action": "c2pa.edited"}
     ]}}
  ]
}
```
Note: the key/certificate in the manifest file is for dev/test only (per the c2patool docs); production needs a real signer (`--signer-path`). Platform re-encoding may strip the manifest. (Not tested: c2patool not installed in the test environment.)

---

## 8. QC checklist

### Picture
- [ ] Correct resolution, aspect, SAR 1:1, CFR fps, progressive scan.
- [ ] Correct color tags (BT.709 1-1-1), consistent between master and deliverables; compare display in QuickTime, VLC, Chrome, phone.
- [ ] Levels: luma/chroma within legal range for broadcast (EBU R103 v3.0 sets tolerances for digital signals; common practice: 10-bit 64–940 with slight excursions allowed); not mandatory for web, but avoid hard-clipped whites/blacks.
- [ ] No unintended black frames/flash frames/freezes (`blackdetect`, `freezedetect`).
- [ ] No AI artifacts visible at real speed: head/tail clip morphing, hands, text, eyes, teeth, physics.
- [ ] Upscale: no halo around edges, no "waxy skin", no detail flicker (texture boil).
- [ ] Character consistency between shots (face, hair, costume) against the character sheet.
- [ ] Banding in sky/dark areas after encode; if present → add fine grain/dither or raise bitrate.
- [ ] Titles/graphics within title-safe; spelling; complete credits.
- [ ] 9:16 version: subject and text outside the UI zones.

### Audio
- [ ] Integrated loudness within target tolerance; true peak below threshold; reasonable LRA.
- [ ] No clipping, clicks, pops, dropouts, or noise-floor jumps at cuts.
- [ ] Stems sum to the printmaster (null test: phase-invert the stem sum against the mix → near silence).
- [ ] Phase/mono compatibility (phones often play mono).
- [ ] Correct channel mapping (L/R; 5.1: L R C LFE Ls Rs).
- [ ] 48 kHz / 24-bit for the master.

### Sync
- [ ] Lip-sync within ±1 frame (acceptable is usually audio at most ~1 frame early, at most ~2 frames late).
- [ ] SFX hits match picture; no drift across the programme (check beginning, middle, end).

### Captions
- [ ] Timing matches, no overlaps; ≤ 42 characters/line, ≤ 2 lines, ≤ 20 cps.
- [ ] Spelling, Vietnamese diacritics render correctly; captions do not cover faces/important text.
- [ ] Correct platform format (SRT/VTT/IMSC), language tag.

### Legal / metadata
- [ ] AI disclosure per platform and EU AI Act (section 9) enabled/recorded.
- [ ] Licenses for music, SFX, fonts, stock; cue sheet.
- [ ] Consent for voice clones / likeness; no use of a real person's likeness without consent.
- [ ] No unintended third-party logos/brands appearing in the AI footage.
- [ ] Credits list AI tools and humans.
- [ ] C2PA manifest (if used) readable on the delivered file.

**QC report template:** table with `Timecode | Category | Severity (1 Critical / 2 Major / 3 Minor / FYI) | Description | Action | Status`. One Critical issue = Fail.

---

## 9. Legal: disclosure, copyright, licensing

> Not legal advice. Information as of 10/2026; consult a lawyer for commercial release.

### 9.1 EU AI Act — Article 50 (applies from 02/08/2026)
- **Deployers** (those using an AI system to create deepfake images/audio/video) must disclose that the content is artificially generated/manipulated.
- **Artistic/creative/fictional work exception:** the obligation is limited to disclosing the existence of AI-generated content "in an appropriate manner that does not hamper the display or enjoyment of the work" — e.g. a line in the credits/description or a small icon; a large on-screen watermark is not required.
- **Providers** (such as ByteDance) must mark output in machine-readable form; for systems already on the market before then, the Digital Omnibus grants a narrow extension to **02/12/2026** only for the provider-side marking obligation (Jones Walker, 16/07/2026). The Omnibus does **not** postpone the deployer's deepfake disclosure obligation.
- **Code of Practice on marking & labelling** (Paul Weiss, 04/08/2026): the deepfake test is objective (no intent to deceive needed, "plausible realism" is enough); the Commission provides 3 standard icons (fully AI-generated, AI-modified, a basic icon with a second information layer), which must be recognizable without interaction; audio-only content needs a spoken disclaimer; content released before 02/08/2026 does not need retroactive labelling.
- **Action for skill 8:** if the film is distributed in the EU and has realistic-looking scenes/people → add disclosure (credits + description + EU icon where appropriate), keep the provider's C2PA/metadata, do not strip metadata.

### 9.2 Platform AI labels
- **YouTube:** must enable "AI use" (Altered or synthetic content) when realistic content shows a real person saying/doing something they did not do, alters real events/places, or creates a realistic scene that never happened. Not needed for clearly fantastical content, color correction, upscaling. The label appears on the player for photorealistic content; YouTube may auto-apply the label when it detects C2PA. Violations can lead to labelling, content removal, or YPP suspension.
- **TikTok:** must label content "completely generated or significantly edited by AI" that has realistic images/audio/video (toggle "AI-generated content"); auto-labels when C2PA is present. Prohibits the likeness of minors under 18 or of private individuals without consent, and content that misleads about events/crises or public figures.
- **Meta:** "AI info" for ads featuring AI-generated photorealistic human subjects; "Made with AI" / AI info for organic posts; reads C2PA/IPTC (per Coinis, 2026 — third party).
- **Practice:** for photorealistic AI films, **always enable the label** on every platform. Low cost, large avoided risk.

### 9.3 Copyright of AI output (US)
- **US Copyright Office, Copyright and AI Part 2: Copyrightability (01/2025):** prompts alone do not provide enough control to confer authorship; protection is available for (a) human expressive inputs still perceptible in the output, (b) creative human selection, arrangement and modification — but protection does not extend to the AI-generated parts; (c) using AI as an assistive tool does not remove protection from a human-created work.
- **Thaler v. Perlmutter:** the Supreme Court denied certiorari on **02/03/2026**; the human-authorship requirement stands.
- **Consequences:** the protectable parts of the film lie in the script, the edit (selection & arrangement), sound design, human-composed music, grade, and real human VO. Keep logs: EDLs of every version, decision notes, project files. When registering copyright in the US, disclose and exclude substantial AI-generated parts.
- Seedance/BytePlus/Dreamina terms on commercial use rights for output must be checked and archived (dated ToS snapshot) — skill 6 is responsible for obtaining them, skill 8 checks them in the archive package.

### 9.4 Voice & music licensing
- ElevenLabs (ToS updated 31/03/2026): Free = non-commercial only; Paid = commercial subject to the Prohibited Use Policy; users retain rights to output as between them and ElevenLabs; upload only your own voice or an authorized voice.
- Cloning an actor's voice: the contract must state scope (project, media, territory, term), right of withdrawal, compensation; refer to SAG-AFTRA consent principles when working with union actors (not researched in depth in this document).
- AI music: see 5.4. Library music: check license scope (online/broadcast/paid ads/festival usually differ). Content ID: whitelist the channel in advance if the library music is registered with Content ID.

---

## 10. Anti-AI patterns in post (signs of a "cheap AI film")

| Pattern | Why it gives itself away | Fix |
|---------|-----------|----------|
| **Metronomic pacing** (every shot 3–5s because gen clips are 5s) | Nobody cuts like that; exposes the generation unit | Vary lengths; hold long on reactions; cut fast on action |
| **Every cut on the music beat** | Looks like a slideshow template | Cut on emotion/action; only about 1/3 of cuts near the beat, deliberately off by a few frames |
| **Wall-to-wall music from start to finish** | Hides missing sound design; ear fatigue | Include ambience-only/silent passages; motivated music ins/outs |
| **Heavy teal-orange, high saturation** | Default look of AI and presets | Palette from the visual bible; skin on the skin line; reduce sat |
| **Over-sharpened upscale, halo** | White outlines around edges, "steel-wire" hair | Disable sharpen; conservative model; light 0.3–0.8 px blur; grain |
| **Plastic denoise (plastic skin)** | Skin without pores, waxy face | Light denoise; Starlight to reduce plastic; grain + texture |
| **Keeping clip head/tail artifacts** | Morphing, face drift at shot start/end | Trim first 8–12 frames, last 6–12 frames; use the middle |
| **Stock whoosh/impact on every transition** | "YouTube template" sound | SFX sourced within the scene; transitions via ambience/J-cuts |
| **Unmotivated speed ramps** | Hides slow AI motion with a gimmick | Ramp only when the story needs it; prefer cutting |
| **Constantly drifting camera on every shot** | Every AI clip does a "gentle dolly in" | Intercut static (lock-off) shots, stabilize or pick static takes; ask skill 6 for varied camera |
| **Ambience jumping at every cut** | Each clip has different native audio | Replace with a continuous ambience bed per scene |
| **No Foley** | Characters "float", weightless | Add footsteps, cloth, hand-object contact |
| **Static or overly heavy grain** | Obvious overlay, encoder breaks it into blocks | Temporal, fine grain; check after encode |
| **Effect transitions (glitch, zoom, morph) to join clips** | Hides continuity with gimmicks | Straight cuts; meaningful match cuts |
| **Interpolated slow-motion on everything** | Ghosting, fake "dreamy" feel | Only when needed, check artifacts |
| **Constant fade to black between scenes** | Lacks transition structure | Transition via sound, matching images |
| **AI dialogue without room tone/reverb** | Voice "pasted" onto picture | Spatial reverb, room tone, EQ for mic distance |

---

## 11. Gate checklist (skill 8 gate criteria)

**Gate A — Assembly ready**
- [ ] Every clip ingested, checksummed, with metadata (prompt/seed) attached.
- [ ] Conformed to CFR 24 fps, ProRes 422 HQ, BT.709 tags.
- [ ] Shotlist assembly rendered; regen list sent to skill 6.

**Gate B — Picture lock**
- [ ] Director/client approved the fine cut in writing.
- [ ] No artifacts visible at real speed (or a specific VFX/regen plan exists).
- [ ] Varied pacing; edit checked against the anti-pattern list in section 10.
- [ ] EDL/XML/AAF + reference video with burned-in TC exported; change list v01 created.

**Gate C — Finishing**
- [ ] Upscaled with a consistent model per scene; checked at 100% zoom.
- [ ] Color matched via scopes; correct skin tone; look per the visual bible.
- [ ] Texture added after grade, checked after a test encode.
- [ ] Textless master exported.

**Gate D — Sound & mix**
- [ ] Clean dialogue, complete DX/MX/FX stems, null test passed.
- [ ] Loudness and true peak meet target for each deliverable (`ebur128` log saved in `07_post/qc/`).
- [ ] Music/SFX licenses and voice consent archived.

**Gate E — Delivery & QC**
- [ ] Every deliverable from table 6.2 required for the project encoded and verified with ffprobe.
- [ ] Captions meet the rules; burned-in for social if required.
- [ ] QC report: 0 Critical, 0 unresolved Major.
- [ ] AI disclosure/platform labels/credits/C2PA handled.
- [ ] Archive fully packaged, two copies, checksums.

---

## 12. Uncertain information / to re-check

1. **Seedance 2.5 resolution:** the summary of BytePlus API docs (seedance2-video.com) says 480p/720p, 24 fps, 4–30s; Artlist advertises "4K", Morphic advertises "native 1080p". This may differ between the API, Dreamina and partners, or be platform-side upscaling. Check with ffprobe on real output.
2. **YouTube/TikTok/Instagram loudness:** no official public spec was opened in this research; -14 LUFS / -1 dBTP is industry practice.
3. **ATSC A/85 true peak and tolerance** (-2 dBTP, ±2 dB): common practice; the Production Expert page on the A/85 update returned error 429, so details of the new version are unverified.
4. **EBU R128 tolerance:** the R128 v5 summary states ±1.0 LU for live/special; Fora Soft states ±0.5 LU for file-based. Check each broadcaster's spec.
5. **Netflix cites BS.1770-1** in spec v1.6 (per the fetched page); the version actually used for measurement may be newer — use a meter with a Netflix mode.
6. **Meta Ads specs and safe zones:** the Facebook Business page blocks crawlers; the safe-zone figures (~14% top, ~35% bottom) are practice from common templates — check Ads Manager.
7. **Instagram specs** taken from a third-party source (Sendcove, 04/2026).
8. **Resolve features:** Resolve 21 (announced 04/2026, final 06/2026, 21.1 at IBC 09/2026, 21.1.1 on 01/10/2026). Super Scale, UltraNR, Voice Isolation, Deflicker are pre-existing features (not mentioned in the 20.1 guide/Resolve 21 article that were read) — check the actual menus. Direct OTIO import into Resolve/Premiere was not verified in this research; FCP7 XML/EDL is the safe route.
9. **Topaz:** model names/versions change monthly (Starlight Precise 2.5→2.6, Starlight Fast 3 released 09/2026). Speed figures are Topaz's.
10. **Suno/Udio:** commercial terms for the new "licensed" models change constantly; UMG/Sony vs Suno and Sony vs Udio litigation is ongoing.
11. **4K DCP containers** (3996×2160, 4096×1716) and the 85 dBC level: from knowledge of DCI/SMPTE standards; no official source opened in this research.
12. **USCO Part 2 release date** (29/01/2025) from prior knowledge; the opened PDF did not show the date in the excerpt.
13. **EU icons:** the specific design and placement requirements for artistic works require reading the original Code of Practice.
14. RIFE and c2patool were not run in the test environment (the 24→25 speed-up command was tested and produced 25/1).

---

## 13. Sources (only URLs actually opened)

1. EBU R 128 (v5, 11/2023) — https://tech.ebu.ch/docs/r/r128.pdf
2. EBU R 103 — https://tech.ebu.ch/publications/r103
3. Netflix Sound Mix Specifications & Best Practices v1.6 — https://partnerhelp.netflixstudios.com/hc/en-us/articles/360001794307-Netflix-Sound-Mix-Specifications-Best-Practices-v1-6
4. Netflix Timed Text Style Guide: General Requirements — https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements
5. Netflix English (USA) Timed Text Style Guide — https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide
6. YouTube recommended upload encoding settings — https://support.google.com/youtube/answer/1722171
7. YouTube altered or synthetic content disclosure — https://support.google.com/youtube/answer/14328491
8. Spotify loudness normalization — https://support.spotify.com/us/artists/article/loudness-normalization/
9. TikTok Ads video specifications — https://ads.tiktok.com/help/article/video-ads-specifications
10. TikTok AI-generated content — https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content
11. Instagram video specs (Sendcove, 04/2026) — https://www.sendcove.app/integrations/instagram/video-specs
12. Meta AI content labeling 2026 (Coinis) — https://coinis.com/blog/meta-ai-content-labeling-facebook-instagram-ads-2026
13. Fora Soft: EBU R128, BS.1770, ATSC A/85 — https://www.forasoft.com/learn/audio-for-video/articles-audio/loudness-normalization-ebu-r128-bs1770-atsc-a85
14. Apple ProRes White Paper (04/2022) — https://www.apple.com/final-cut-pro/docs/Apple_ProRes_White_Paper.pdf
15. DCP format guide (Knut Erik Evensen) — https://www.knuterikevensen.com/2021/06/30/what-is-the-dcp-format/
16. No Film School: Murch's Rule of Six — https://nofilmschool.com/editing-emotion-using-walter-murchs-rule-six-non-narrative-content
17. LRB, John Lahr "Every Blink" (Murch) — https://www.lrb.co.uk/the-paper/v47/n19/john-lahr/every-blink
18. Frame.io: Resolve color management cheat sheet — https://blog.frame.io/2023/12/04/color-management-cheat-sheet-davinci-resolve/
19. DaVinci Resolve 20.1 New Features Guide — https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20.1_New_Features_Guide.pdf?_v=1756105210000
20. Newsshooter: DaVinci Resolve 21 announced (04/2026) — https://www.newsshooter.com/2026/04/13/blackmagic-design-announces-davinci-resolve-21-major-update-adds-new-photo-page/
21. Film Look Creator guide (Resolve 21) — https://videomontazher.com/en/color/resolve-fx/film-look-creator
22. invideo: grain & blur for AI video — https://invideo.io/faq/does-adding-film-grain-and-blur-to-ai-generated-video/
23. invideo: Topaz models compared (08/2026) — https://invideo.io/blog/topaz-video-enhancement-models/
24. Topaz Labs September 2026 updates — https://www.topazlabs.com/updates/sep2026
25. RIFE (hzwer/ECCV2022-RIFE) — https://github.com/hzwer/ECCV2022-RIFE
26. OpenTimelineIO adapters — https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html
27. iZotope: remove background noise from dialogue — https://www.izotope.com/community/blog/how-to-remove-background-noise-from-dialogue-recordings
28. fal.ai Seedance 2.0 — https://fal.ai/seedance-2.0
29. Seedance 2.5 specs (third-party summary of BytePlus docs) — https://seedance2-video.com/seedance-2-5
30. EU AI Act Article 50 — https://artificialintelligenceact.eu/article/50/
31. Jones Walker: Omnibus & Article 50 (16/07/2026) — https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html?id=102nbon
32. Paul Weiss: EU finalises transparency rules (08/2026) — https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content
33. C2PA — https://c2pa.org/
34. c2patool usage — https://github.com/contentauth/c2pa-rs/blob/main/cli/docs/usage.md
35. US Copyright Office, Copyright and AI Part 2 (PDF) — https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf
36. Holland & Knight: Thaler cert denied (03/2026) — https://www.hklaw.com/en/insights/publications/2026/03/the-final-word-supreme-court-refuses-to-hear-case-on-ai-authorship
37. AI Lawsuit Tracker: UMG v. Suno/Udio — https://ailawsuittracker.com/cases/umg-v-suno/
38. Music Business Worldwide: WMG–Suno deal — https://www.musicbusinessworldwide.com/warner-music-group-settles-with-suno-strikes-first-of-its-kind-deal-with-ai-song-generator/
39. OpusClip: AI music news April 2026 — https://www.opus.pro/blog/ai-music-news-april-2026
40. ElevenLabs Terms of Use (31/03/2026) — https://elevenlabs.io/terms-of-use
41. FFmpeg filters documentation (index; option details taken from local `ffmpeg -h filter=...`) — https://ffmpeg.org/ffmpeg-filters.html
