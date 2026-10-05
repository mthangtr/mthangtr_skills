# 07 — Dailies Review / QC for AI footage (model-agnostic; researched on Seedance 2.5)

> **Model-agnostic note (v0.3.0):** this research was compiled with Seedance 2.5 as the reference video model. Every Seedance-specific number here (call length, ≤30 s units, ≥3 s shots, reference counts, 24 fps, 720p, 32 kHz audio, @Image tags, prices, policy) is an example from the `seedance-2.5` profile, not a pipeline rule. Read the real limits from the active profile (`video-generation/references/models/<id>/profile.json`) and apply `film-pipeline/references/shared-conventions.md`. Where this file says "skill 6", read `video-generation`; references like "06 §N" point to `video-generation/references/models/seedance-2.5/knowledge.md`.

> Research for skill 7 of the `ai-film-studio` plugin. Role: **script supervisor + VFX supervisor + QC operator** in one person. Input: takes from skill 6 (`video-generation`), `shotlist.json` (skill 4), visual bible (skill 3), previs (skill 5). Output: review log, circled takes, fix notes with clear routes for skill 6 / skill 8.
> Compiled: 2026-10-02. The ffmpeg commands and `temporal_qc.py` in section 5 were test-run on ffmpeg 6.1.1 + OpenCV 4.x/5.0 (synthetic test clip). The InsightFace/CLIP snippets have **not been test-run** in this environment (models must be downloaded).

---

## 1. Core principles

1. **The shotlist is the contract.** Each take is scored against `shotlist.json` (beat, framing, lens, camera move, duration, dialogue, continuity tags), not on whether it "looks nice". A beautiful take that misses the beat is still NG (no good).
2. **Claude cannot watch video, only frames.** Every motion judgment is an *inference* from dense frames + metrics. The Artifact-Bench paper (2026) shows the best MLLM reaches only ~47.5% accuracy at detecting video artifacts, <10% on the task of pinpointing a specific artifact, while human experts reach 87.7%. Reason: "temporal-spatial artifacts … cannot be identified from isolated frames alone" and small artifacts are lost in token compression. ⇒ Claude must (a) extract dense frames in suspect regions, (b) crop/zoom small regions (hands, eyes, text), (c) use numeric metrics for temporal issues, (d) **escalate** to a human whatever is only visible on playback.
3. **Two separate QC layers:** *Technical QC* (file, codec, frame rate, black/freeze, loudness, clipping — Netflix Production QC style) and *Creative/Continuity QC* (beat, performance, continuity, AI artifacts). A technical fail is a hard fail, not up for debate.
4. **Name defects with a shared code.** Borrowed from the Netflix Production QC Glossary: every defect has a code (I-, C-, A-, L-, G-, V-, M-) so everyone speaks the same language. Here it is extended with an `AI-` family for generative artifacts (section 4).
5. **Cheapest fix route that still meets the bar.** Priority order: accept → trim/cut-around → fix in post → timestamp-edit (Seedance partial editing) → extend/regenerate with the same prompt (different seed) → regenerate with changed prompt/reference → back to previs/shot design. But **do not** push to post what post cannot fix (identity drift, wrong physics, wrong lip-sync).
6. **Measure "cost per accepted second"**, not number of generations. Each unit has a **regeneration budget** (section 6.4). Budget exhausted ⇒ escalate, change the shot design, do not keep generating indefinitely.
7. **Check the edges of the take.** First/last frames determine cuts and extensions; continuity between unit N and N+1 is checked on last-frame(N) vs first-frame(N+1).
8. **Audio is half the take.** Seedance 2.5 generates audio simultaneously; voice inconsistency and lip-sync failure are reported failure patterns. Never circle a take whose audio has not been listened to/measured.
9. **A partial edit must be fully re-QC'd.** After a timestamp-edit, re-check the parts that were *not* edited too (face, voice, props, text) — the atoms.dev review stresses verifying that the edit does not change "every unaffected frame, voice, product detail".
10. **Take notes like a script supervisor:** one log line per take, with timecode, description, decision, reason. The editor (skill 8) only needs to read the log to know which take and which segment to use.

---

## 2. Review process for each take / unit

A **unit** = one generation (≤30s) that may contain 1 or more shots from the shotlist. A unit has several **takes** (variants). Process:

### Step 0 — Ingest & naming
- Name per shared-conventions §2: `<unit>_T<nn>_r<round>.mp4`, e.g. `U02_T04_r1.mp4`; timestamp-edit/extension versions add the suffix `_e<n>` (`U02_T04_r1_e1.mp4`). Shot IDs use `S03_040` as in the shotlist.
- `ffprobe` to get metadata (resolution, fps, duration, audio channels, sample rate) → compare with project spec (section 5.1). Wrong fps/res ⇒ Technical fail (I-201/C-301 equivalent).
- Store prompt, seed, reference IDs, model version next to the file (sidecar JSON) — without them it cannot be reproduced.

### Step 1 — Automated Technical QC (no viewing needed)
Run `qc_take.sh` (section 5.8): blackdetect, freezedetect, scdet (unintended cuts), silencedetect, ebur128 (integrated, LRA, true peak), astats (clipping/peak count), duration vs shotlist. Any hard-fail ⇒ stop, log `TECH-FAIL`, do not spend effort on creative review.

### Step 2 — Rough visual pass (contact sheet)
- Contact sheet at 1 frame / 0.5s with burned-in timecode (section 5.3). View the whole unit on 1–2 images.
- Check: framing/composition vs shotlist & previs frame, whether the beat happens, correct character, lighting/time of day, unintended cuts.
- Place alongside: character reference sheet (visual bible) + previs still of the shot.

### Step 3 — Temporal pass (dense)
- Run `temporal_qc.py` → list of timestamps suspected of flicker / boiling / jump.
- For each suspect region + each "hot spot" (hand touching object, head turn, occlusion, character entering/exiting frame, fast camera move, mouth speaking): extract a **burst** of 12–24 consecutive frames (section 5.4), view as a filmstrip. This is the only way Claude "sees" morphing, popping, object permanence failure.
- Crop-zoom 2–4× on hands, face, eyes, text, logos (section 5.5).

### Step 4 — Identity & continuity pass
- Face embedding similarity vs reference (section 5.10) over time: detects gradual identity drift across 30s.
- Continuity checklist (section 3) against the circled take of the previous/next shot: first/last frame side-by-side.

### Step 5 — Audio pass
- Waveform + spectrogram image (section 5.7): look for clipping (flat peaks), music bleed (sustained harmonic bands under dialogue), dropouts (gaps), noise floor, "metallic" frequency regions (narrow bright repeating streaks at 2–8 kHz).
- Check dialogue against the script: if an ASR tool is available (e.g. Whisper), transcribe and compare text + language (wrong language/garbled words). If not, escalate.
- Lip-sync: SyncNet (section 5.11) if available; otherwise, burst mouth frames at bilabial sounds (p/b/m) against waveform onsets; a human must still confirm via escalation.

### Step 6 — Score & decide
- Score the rubric (section 6), apply the decision tree, choose a route. Write the review log (section 7).
- Circle at most 1 **hero take** + 1 **alt/safety take** per shot. Specify the usable *in/out points* (a 30s take may only use 4.2s–11.8s).

### Step 7 — Human review gate
- Collect the "ESCALATE" items into a **review packet** for a human (section 8): take link, timestamp, specific yes/no question. The human plays it for real at full speed + half speed + loop (FilmDaft recommendation) and then confirms.

---

## 3. Continuity checklist

Based on the standard script supervisor forms (Continuity/Editor's Log, Facing Page, Lined Script, Daily Progress Report) and the facing page items: wardrobe, props, hair & make-up, action, screen direction, watch/time, eyeline diagram. Each item is checked within the **take** (intra-shot, where AI often fails) and **between shots** (inter-shot).

| # | Item | What to check | Reference source to compare | Typical AI failure |
|---|---|---|---|---|
| C1 | Wardrobe | Color, style, layers (jacket open/closed), buttons, logos, dirt/wetness | Visual bible character sheet; last frame of previous shot | Garment shifts color slightly within the take, collar/buttons disappear, patterns "swim" |
| C2 | Props | Present/absent, which hand holds it, liquid level in glass, position on table, state (light on/off, door open) | Shotlist continuity tags; previs | Prop disappears when occluded (object permanence), switches hands, duplicates |
| C3 | Hair & make-up | Hairstyle, bangs, hair tucked behind ear, wounds/blood, lipstick, beard | Character sheet; previously circled take | Hair parting flips side, wound switches side (mirror) |
| C4 | Body position / action | Start/end pose, sitting/standing, action match for the cut | Lined script / beat; previs blocking | Action not completed, start differs from end of previous shot |
| C5 | Eyeline | Gaze direction matches the off-screen subject; eyeline diagram | Previs camera/character positions | Eyes look straight into camera, eyes misaligned, looking the wrong way |
| C6 | Screen direction / 180° rule | Characters/vehicles move left→right consistently; who is frame left | Previs top-down; shotlist `axis` | Model "flips" the layout on angle change; generating each shot separately easily crosses the axis |
| C7 | Lighting continuity | Key light direction, shadow hardness, color temperature, practicals | Visual bible lighting plan; previs light | Shadow direction changes between shots, practical on/off, flicker |
| C8 | Time of day | Sun angle, sky color, shadow length | Shotlist `time_of_day` | Sky turns to sunset within 10s |
| C9 | Weather / atmosphere | Rain, wet road surface, fog, wind (hair/leaves) | Shotlist; previous shot | Rain stops abruptly, road dry in the next shot |
| C10 | Set dressing / background | Background objects, signs, parked cars, background people | Previs set; establishing shot | Background warping, number of windows changes |
| C11 | Camera spec | Lens feel (FOV), DOF, camera height, move | Shotlist `lens`, `move`; previs | Wrong zoom/dolly, rack focus does not happen |
| C12 | Timing / duration | Beat lands on time, action speed | Shotlist `duration`, beat timing | Action too slow (AI float) or skips ahead |
| C13 | Dialogue continuity | Correct line, correct speaker, correct language, overlap | Script | Invented dialogue, changed words, wrong speaker |
| C14 | Sound continuity | Room tone, ambience, no music in the dialogue stem | Sound plan | Ambience changes between shots of the same scene, music bleed |

**How to check inter-shot:** create a side-by-side image `last frame of hero take shot N` | `first frame of candidate shot N+1` (section 5.2), check C1–C10. For cut on action: compare the last 3 frames of N with the first 3 frames of N+1.

**Note format (facing page style) for each circled shot:**
```
S03 / S03_050 — circled U02_T04_r1 (in 02.10 – out 09.75)
WARDROBE: Mai — moss-green jacket, ZIPPER OPEN, red scarf wrapped once
PROPS: coffee cup in LEFT hand, ~1/2 full; phone face-down on table, right corner
HAIR/MU: low ponytail, left strand tucked behind ear; no lipstick
ACTION: ending: Mai sets the cup down, looks out the window (frame left)
EYELINE: Mai → frame left (window); Huy off-screen frame right
DIRECTION: Mai frame right, Huy frame left (axis A)
LIGHT: window key frame left, 4300K, soft shadows; desk lamp OFF
TOD/WEATHER: late afternoon, light rain outside the glass
```

---

## 4. AI artifact taxonomy

Classification framework synthesized from Artifact-Bench (Surface / Structural / Temporal-Semantic), Skyra (Low-level Forgery vs Violation of Laws: Color/Light, Texture, Motion Forgery, Object Inconsistency, Interaction Inconsistency, Causality, Commonsense, Unnatural Movement), VideoPhy-2 (conservation of mass/momentum, gravity, material properties, fluid, object permanence), VBench (subject/background consistency, temporal flickering, motion smoothness, dynamic degree) and creators' practical notes.

### 4.1 Severity levels

| Level | Name | Definition | Default action |
|---|---|---|---|
| S0 | Note | Visible when scrutinizing frames, not visible at normal speed / audience will not notice | Accept, note it |
| S1 | Minor | Visible if you look for it, not in the main area of attention, does not break the beat | Accept or fix in post if cheap |
| S2 | Major | A normal audience will notice; in the main area or prolonged; breaks continuity | Do not circle as-is: timestamp-edit / cut-around / regenerate |
| S3 | Critical | Breaks the illusion, breaks story/identity, hard technical defect, legal/safety issue | Reject take; regenerate with changes or back to previs |

**Modifiers raising severity +1:** artifact is on the main character's face/hands/eyes; lies within the usable time range (in/out); lasts > 0.5s; occurs at a cut point (first/last 1s) when cut-on-action is needed; appears repeatedly in every take (⇒ prompt/shot design defect, not a random defect). **Lowering −1:** lies outside the intended in/out points; will be masked by grade/DOF/grain/motion blur in post; shot < 1s in a fast montage.

### 4.2 Fix routes (route codes used in the log)

| Code | Route | When |
|---|---|---|
| R0 | ACCEPT | S0/S1 acceptable |
| R1 | TRIM | Use in/out points to avoid the defective segment |
| R2 | POST | Grade, stabilize, deflicker, paint/cleanup, crop/reframe, grain, replace text with a title, audio repair/replace (skill 8) |
| R3 | T-EDIT | Seedance timestamp-level partial edit on a specific segment/character |
| R4 | EXTEND | Extend a good take (duration short/beat not finished) |
| R5 | REGEN-SAME | Regenerate with the same prompt/refs, different seed (random defect, 1/N takes) |
| R6 | REGEN-CHANGED | Change prompt/refs/duration/camera move/simplify the action |
| R7 | BACK-TO-PREVIS | Shot design not feasible for the model (axis crossed, action too complex, multiple people interacting) → skill 4/5 |
| R8 | ESCALATE | Needs a human decision (section 8) |

### 4.3 Taxonomy table (artifact → detect → severity → route)

| Code | Artifact | Detection from frames/tools | Typical severity | Fix route |
|---|---|---|---|---|
| AI-ID1 | **Identity drift** (character's face drifts gradually within the take, or differs between shots) | Face embedding cosine vs reference over time (InsightFace/ArcFace); compare contact sheet next to character sheet; a gradual decline is drift, a sudden drop is a swap | S2 if clearly declining; S3 if it becomes a different person | R1 if only at end of take; R3 on the drifting segment; R6 add/change reference image, shorten duration; do not fix in post |
| AI-ID2 | **Identity swap / blending** between 2 characters (A's features transfer to B) | B's embedding moves toward A; burst when the 2 people get close/occlude each other | S3 | R6 (clearly separate references, reduce interaction), R7 if the 2-person shot is complex |
| AI-FM1 | **Face morphing / melting** (facial features flow during head turns, smiling, speaking) | 24-frame burst over the head turn; crop face 3×; warp_resid spike in the face region | S2–S3 | R3, R5; if repeated in every take → R6 (reduce head-turn angle, closer/wider) |
| AI-HD1 | **Hands: extra/fused/missing fingers**, third hand, wrong joints | Crop hands 3–4× on every frame where hands are clear; count fingers on bursts; watch when holding objects | S1 if hands small/motion blurred; S2–S3 if close-up | R1, R3, R6 (composition hides hands, simple hand action), R2 paint only for 1–3 frames |
| AI-LB1 | **Extra/missing limbs**, legs merging while walking | Dense contact sheet while walking/running; burst on footsteps | S3 | R5/R6 |
| AI-OP1 | **Object permanence failure** (object disappears/appears after occlusion, duplicates) | Compare frames before & after occlusion; scdet does not catch it; props checklist C2 | S2–S3 | R3 if short; R6 (avoid occlusion, describe prop clearly in prompt) |
| AI-OP2 | **Object deformation** (prop changes shape when rotating — reported for Seedance 2.5 "products changing shape during rotation") | Burst during rotation; compare with prop reference | S2 (S3 if hero prop/product) | R6 (reduce rotation), R7 use previs/3D as the authoritative source |
| AI-PH1 | **Physics violations** (gravity, inertia, collisions passing through objects, wrong fluids, objects moving with no force applied) — VideoPhy-2: mass & momentum errors make up the majority | Burst around the interaction; ask "cause → effect" frame by frame; abnormal flow_p95 spike | S2–S3 | R6 (simplify the action, split the action into 2 shots), R7 |
| AI-PH2 | **Causality / irreversibility violation** (glass breaks then heals, water flows backward, door opens with nobody opening it) | Burst; compare before/after state | S3 | R6/R7 |
| AI-PH3 | **Interaction failure** (hand passes through object, grip without contact, feet sliding on the floor — foot sliding) | Crop the contact region; compare foot position against the ground across the burst | S2 | R3, R6 |
| AI-TX1 | **Texture swimming / boiling** (fabric, skin, grass, bricks "boiling") | High `warp_resid` while flow is low; burst crop of the texture region; VBench temporal flickering on static regions | S1–S2 | R2 (light deflicker/temporal denoise, grain) if mild; R5/R6 |
| AI-TX2 | **Plastic / waxy skin**, over-smooth | Crop face; compare with reference | S1 | R2 (grain, texture), R6 if excessive |
| AI-FL1 | **Flicker** (brightness/color flickering between frames) | `dluma` spike (temporal_qc), signalstats YAVG plot; Netflix L-100 "abrupt brightness level changes" | S1–S2 | R2 deflicker if global; R5 if local |
| AI-BG1 | **Warping background** (straight lines bend, architecture swims during camera moves) | Burst during the camera move; check straight lines (columns, door frames); background consistency (CLIP) | S1–S2 | R1, R2 (stabilize cannot fix warping — avoid), R6 (simpler camera move) |
| AI-BG2 | **Background drift / rearrange** (background objects change, windows added/removed) | Compare first/last frames; first/last side-by-side | S1–S2 | R1, R3 |
| AI-TP1 | **Temporal inconsistency / popping** (discrete 1–2 frame change) | 1–2 frame `warp_resid` spike; short freezedetect; burst | S2 | R2 (paint/frame replace) if 1 frame; R3 |
| AI-TP2 | **Unintended cut / scene jump** within a take | `scdet`/PySceneDetect detects a cut where the shotlist specifies 1 shot | S2–S3 | R1 (use a portion) or R5 |
| AI-TT1 | **Text garbling** (text, signs, screens nonsensical/changing) | Crop text; OCR (if available) across the burst — a changing string = defect | S1 background; S2–S3 if the text is story/legal | R2 (replace with title/insert) — the right strategy is not to let the model render important text |
| AI-LS1 | **Lip-sync drift** (mouth out of sync with audio, increasingly late) | SyncNet AV offset/confidence; burst mouth frames at p/b/m sounds vs waveform onset | S2 (S3 if facial close-up) | R3 (edit the dialogue segment), R6; post can only fix a constant offset (slip audio) |
| AI-EY1 | **Eye direction errors** (misaligned eyes, looking at camera, misaligned pupils, abnormal blinking) | Crop eyes 4×; eyeline checklist C5 | S2 | R3, R6 (describe eyeline clearly, gaze-direction reference) |
| AI-MS1 | **Motion smear / ghosting** (smears, multiple images during fast motion that are not natural motion blur) | Burst during fast motion; high flow_p95 + abnormally blurry frames | S1–S2 | R6 (reduce action/camera speed); R2 limited |
| AI-FLT1 | **"AI float" / unnatural micro-motion** (character drifts, unintended slow-mo motion, constant slight swaying, weightless feet, hair/fabric moving with no wind) | Hardest to see from frames: flow_mean low and steadily uniform when the beat needs to be decisive; compare the number of frames the action occupies vs shotlist timing; **always escalate** | S1–S2 | R6 (strong verbs, specific timing "in 1 second"), R2 light speed ramp (risky) |
| AI-CAM1 | **Camera mismatch** (move/lens/framing differs from shotlist/previs) | Contact sheet vs previs stills; global flow field (pan → uniform horizontal flow) | S2 if it breaks coverage | R6 (clear camera prompt, use previs video reference), R2 reframe/crop if resolution allows |
| AI-CAM2 | **Unstable / jittery camera**, unintended (Netflix G-100/G-101 equivalent) | Global flow with high-frequency oscillation | S1–S2 | R2 stabilize; R5 |
| AI-CL1 | **Color / exposure anomaly** (clipped highlights, crushed blacks, color shift within the take) | signalstats YMIN/YMAX, BRNG; histogram; compare to grade reference | S1 | R2 grade |
| AI-CMP1 | **Compression / low quality** (blocking, banding — Netflix I-304, I-502) | Crop dark gradient/sky regions | S1–S2 | R2 (deband, grain), regen at a higher quality tier |
| AI-AU1 | **Metallic / robotic voice**, phasey | Spectrogram: narrow/repeating streaks, lacking natural harmonics; **escalate for listening** | S2 | R3 (audio), replace with standard TTS/VO in skill 8 |
| AI-AU2 | **Clipping / distortion** (Netflix A-200) | astats Peak_level ≈ 0 dBFS, large Peak_count; ebur128 true peak > −1 dBTP; flat-topped waveform | S2 | R2 if mild (declip); usually replace audio |
| AI-AU3 | **Wrong language / garbled words / invented dialogue** | ASR transcript vs script; detected language | S3 if story dialogue | R3 the dialogue segment; R6; or strip audio, VO in post |
| AI-AU4 | **Music bleeding** into the dialogue stem / unrequested music | Spectrogram: stable sustained harmonics, regular rhythm; listen | S1–S2 | R2 (source separation – limited quality), R6 prompt "no music" |
| AI-AU5 | **Voice inconsistency** (character's voice changes between takes/shots) | Compare speaker embedding (if available) or escalate for listening | S2 | R6 with audio reference; or replacement VO |
| AI-AU6 | **Dropout / silence / sync drift** (Netflix A-303, A-309 MOS) | silencedetect; waveform | S2 | R5 or replace |
| TECH-1 | **Black / freeze / dropped frame** (Netflix I-702/I-703/I-704) | blackdetect, freezedetect, frame count vs duration×fps | S3 (if within in/out) | R1/R5 |
| TECH-2 | **Wrong spec** (fps, resolution, aspect, duration, codec) | ffprobe vs project spec | S3 | R5 with correct parameters |
| SAFE-1 | Unintended **likeness / brand / logo / sensitive content** | Look at the contact sheet; real logos/signs | S3 | R8 mandatory escalate |

**Tips for reading from frames (for Claude):**
- Morphing: track one feature (mole, earring, button) across the burst — if its position/shape changes inconsistently with the motion ⇒ morph.
- Object permanence: mark every object before occlusion, re-check immediately after it is revealed.
- Physics: write out the expected cause-effect chain (touch → tip → fall → stop) and then find the corresponding frames; a missing step or reversed order = defect.
- AI float: count the frames the main action occupies; compare with natural timing (e.g. sitting down ~1s = 24 frames). 2× slower = flag.

---

## 5. Tooling commands / scripts

All commands below run on ffmpeg 6.1 (except where noted). Variables: `IN=take.mp4`, output directory `qc/`.

### 5.1 Metadata & spec check
```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt:format=duration \
  -of json "$IN"
ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name,sample_rate,channels -of json "$IN"
# exact frame count (slower, decodes):
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$IN"
```
Check: `nb_read_frames ≈ duration × fps` (off by > 1 frame ⇒ suspect dropped frames).

### 5.2 First / last frame + side-by-side for continuity
```bash
ffmpeg -y -i "$IN" -frames:v 1 qc/first.png
ffmpeg -y -sseof -0.1 -i "$IN" -frames:v 1 -update 1 qc/last.png
# last of shot N | first of shot N+1
ffmpeg -y -i qc/N_last.png -i qc/N1_first.png -filter_complex "[0][1]hstack=inputs=2" qc/cont_N_N1.png
```

### 5.3 Interval frame extraction + timecoded contact sheet
```bash
# 2 fps stills for detailed viewing
ffmpeg -y -i "$IN" -vf "fps=2,scale=480:-2" qc/f_%04d.jpg
# contact sheet: 1 frame / 0.5s, 4x4 = 8s per sheet, burned-in timestamp
ffmpeg -y -i "$IN" -vf "fps=2,scale=320:-2,\
drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,\
tile=4x4:padding=4:margin=4" qc/sheet_%02d.jpg
```
For a 30s take at fps=2 → 60 frames → 4 sheets of 4×4. If `drawtext` fails on fonts, add `fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`. Note: `pts` after the `fps` filter still follows the original timeline, so timestamps match the take.

### 5.4 Burst (consecutive frames) around a suspect timestamp
```bash
T=12.40   # seconds
# 24 consecutive frames starting 0.5s before T, as a 6x4 filmstrip
ffmpeg -y -ss $(python3 -c "print(max(0,$T-0.5))") -i "$IN" -frames:v 24 \
  -vf "scale=320:-2,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=14:fontcolor=yellow,tile=6x4" \
  -update 1 qc/burst_${T}.jpg
```
(`-ss` before `-i` resets pts to 0 → the burned-in timestamp is relative to the burst start; record the offset in the log.)

### 5.5 Crop/zoom small regions (hands, eyes, text)
```bash
# crop w:h:x:y in source pixels, upscale 3x for inspection
ffmpeg -y -ss 12.0 -i "$IN" -frames:v 12 \
  -vf "crop=240:180:820:400,scale=iw*3:ih*3:flags=lanczos,tile=4x3" -update 1 qc/hand_12s.jpg
```

### 5.6 Technical detectors (black, freeze, scene cut, silence) — one pass
```bash
ffmpeg -hide_banner -nostats -i "$IN" \
  -vf "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=0.003:d=0.5,scdet=t=10" \
  -af "silencedetect=n=-50dB:d=0.5" -f null - 2>&1 \
  | grep -E "black_start|freeze_start|freeze_duration|lavfi.scd|silence_start|silence_end"
```
Actual options (verified with `ffmpeg -h filter=...`): blackdetect `d` (default 2s), `pic_th` (0.98), `pix_th` (0.1); freezedetect `n` noise (0.001), `d` (2s); scdet `threshold` 0–100 (default 10); silencedetect `n`, `d`, `mono`. Lower `d` to 0.1–0.5 because AI takes are short. A short 0.3–0.5s freeze in an AI take is usually a model "stall" — check the burst.

PySceneDetect (when you need CSV + images per scene):
```bash
pip install scenedetect[opencv]
scenedetect -i "$IN" detect-adaptive --threshold 3.0 list-scenes save-images --num-images 3 --width 640
scenedetect -i "$IN" detect-content --threshold 27 list-scenes   # hard cuts
scenedetect -i "$IN" detect-threshold --threshold 12             # fades to/from black
```
Shotlist specifies 1 shot but >1 scene is detected ⇒ AI-TP2 or a large morph.

### 5.7 Audio: loudness, peaks, waveform, spectrogram
```bash
# EBU R128 integrated loudness, LRA, true peak
ffmpeg -hide_banner -nostats -i "$IN" -af ebur128=peak=true -f null - 2>&1 | tail -14
# peak/clipping stats per channel
ffmpeg -hide_banner -nostats -i "$IN" -af astats=metadata=0 -f null - 2>&1 \
  | grep -E "Peak level dB|Peak count|RMS level dB|Flat factor|Noise floor dB"
# images Claude can view
ffmpeg -y -i "$IN" -lavfi "showspectrumpic=s=1024x512:legend=1" qc/spec.png
ffmpeg -y -i "$IN" -filter_complex "aformat=channel_layouts=mono,showwavespic=s=1600x240:colors=white" \
  -frames:v 1 qc/wave.png
# short-term loudness log per 100ms (for spotting jumps)
ffmpeg -hide_banner -nostats -i "$IN" -af ebur128=framelog=verbose -f null - 2>&1 | grep -E "^\[Parsed_ebur128.*t:" | head
```
Reference thresholds: Netflix: dialog-gated −27 LKFS ±2 LU, true peak ≤ −2 dBTP (measuring dialog gating requires the Dolby algorithm — ffmpeg ebur128 only measures program-gated BS.1770); low-dialogue films (≤15%) use −24 LKFS program-gated. EBU R128: −23 LUFS program. At **dailies**, the goal is not deliver-spec but defect detection: true peak > −1 dBTP or a large `Peak count` at ~0 dBFS ⇒ suspect clipping; `Flat factor` > 0 ⇒ flat peaks. Loudness normalization happens in skill 8.

ASR (optional, not test-run here): `whisper take.wav --model small --language vi --output_format srt` → compare transcript with script; if `--language` auto-detect returns a different language ⇒ AI-AU3.

### 5.8 `qc_take.sh` — automated technical pass
> Canonical version: `scripts/qc_take.sh take.mp4 [expected_duration_s] [expected_fps] [out_dir]` (fixed after review: compares fps/duration with expected values, fails on black frames, exits 2 on technical fail, outputs to `06_review/qc/`).
Hard-fail rules for Claude to apply after reading `tech_summary.txt`: fps ≠ expected; |duration − expected| > 0.5s (when expected is fixed); black/freeze within the planned in/out; cuts > 0 when the shotlist specifies 1 continuous shot; no audio stream when the shot has dialogue.

### 5.9 `temporal_qc.py` — flicker / boiling / jump candidates (tested)
```python
#!/usr/bin/env python3
"""temporal_qc.py - flag flicker / boiling / jump candidates in a take.
Usage: python temporal_qc.py take.mp4 --out take_temporal.csv [--z 3.5]
Outputs per-frame CSV + prints suspicious timestamps to extract as bursts (5.4)."""
import argparse, csv, cv2, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out", default="temporal.csv")
ap.add_argument("--z", type=float, default=3.5); ap.add_argument("--width", type=int, default=480)
ap.add_argument("--min-dluma", type=float, default=1.5)   # absolute floor, 0-255 luma units
a = ap.parse_args()
cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
prev = None; rows = []; i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    h, w = f.shape[:2]; f = cv2.resize(f, (a.width, int(h * a.width / w)))
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); luma = float(g.mean())
    r = dict(frame=i, t=round(i / fps, 3), luma=round(luma, 2), dluma=0.0, flow_mean=0.0, flow_p95=0.0, warp_resid=0.0)
    if prev is not None:
        flow = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.linalg.norm(flow, axis=2)
        hh, ww = g.shape; gx, gy = np.meshgrid(np.arange(ww), np.arange(hh))
        warped = cv2.remap(prev, (gx - flow[..., 0]).astype(np.float32), (gy - flow[..., 1]).astype(np.float32), cv2.INTER_LINEAR)
        # residual = change that motion cannot explain -> flicker, boiling, popping, morphing
        r.update(dluma=round(luma - rows[-1]["luma"], 2), flow_mean=round(float(mag.mean()), 3),
                 flow_p95=round(float(np.percentile(mag, 95)), 3),
                 warp_resid=round(float(np.abs(warped.astype(np.float32) - g.astype(np.float32)).mean()), 3))
    rows.append(r); prev = g; i += 1
with open(a.out, "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
def flag(key, floor=0.0):
    v = np.array([r[key] for r in rows[1:]], dtype=float)
    if len(v) < 5: return []
    med = np.median(v); mad = np.median(np.abs(v - med)) + 1e-6
    z = np.abs(v - med) / (1.4826 * mad)
    return [rows[j + 1]["t"] for j in np.where((z > a.z) & (np.abs(v) > floor))[0]]
for key, label, floor in [("dluma", "FLICKER? luma jump", a.min_dluma),
                          ("warp_resid", "BOILING/POP/MORPH? motion-unexplained change", 0.0),
                          ("flow_p95", "JUMP/SMEAR? motion spike", 0.0)]:
    hits = flag(key, floor); print(f"{label}: {len(hits)} frames", hits[:25])
print(f"frames={len(rows)} fps={fps:.3f} -> {a.out}")
```
Interpretation: this is a **candidate filter**, not a verdict. The robust z-score (median/MAD) adapts automatically to each take. Consecutive flagged frames = one event; extract a burst at the first timestamp. High `warp_resid` with low `flow_mean` ⇒ local texture boiling/flicker; high `warp_resid` with high flow ⇒ may just be occlusion/fast motion — the burst must be viewed. The idea is similar to VBench temporal flickering (mean absolute difference) and EvalCrafter's warping error, but self-contained and CPU-only. Requires `pip install opencv-python numpy`.

### 5.10 Identity similarity (face embedding / CLIP) — snippet not test-run
```python
# identity_track.py - cosine similarity of the main face per sampled frame vs reference image(s)
# pip install insightface onnxruntime opencv-python numpy
# LICENSE: insightface code is MIT, but bundled pretrained models (buffalo_l) are NON-COMMERCIAL research only.
import sys, cv2, numpy as np
from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l"); app.prepare(ctx_id=-1, det_size=(640, 640))  # ctx_id=-1 -> CPU
def emb(img):
    faces = app.get(img)
    if not faces: return None
    f = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))  # largest face
    return f.normed_embedding
ref = np.mean([emb(cv2.imread(p)) for p in sys.argv[2:]], axis=0); ref /= np.linalg.norm(ref)
cap = cv2.VideoCapture(sys.argv[1]); fps = cap.get(cv2.CAP_PROP_FPS) or 24; step = max(1, int(fps / 4)); i = 0
print("t,cos_sim")
while True:
    ok, fr = cap.read()
    if not ok: break
    if i % step == 0:
        e = emb(fr); print(f"{i/fps:.2f},{'' if e is None else round(float(np.dot(e, ref)), 3)}")
    i += 1
# usage: python identity_track.py take.mp4 ref_front.png ref_34.png > id.csv
```
Interpretation (thresholds **must be calibrated per project**, see section 11): compute a baseline by running on takes a human has approved as "the right person"; flag when sim < baseline − 0.10 or when there is a steady decline > 0.05 per 10s (drift). Empty frames (no face detected) when the character should be clearly visible ⇒ possibly a severe morph.

Non-face alternative (props, wardrobe, background, animated characters): CLIP image-image cosine (`model.encode_image` for reference and frame, L2-normalize, dot product) — VBench uses DINO for subject consistency and CLIP for background consistency with the formula: compare each frame with the first frame and the immediately preceding frame. Mind model licenses for commercial use.

### 5.11 Lip-sync (optional)
SyncNet (`joonson/syncnet_python`): `python run_pipeline.py --videofile take.mp4 --reference T04 --data_dir out/ && python run_syncnet.py --videofile take.mp4 --reference T04 --data_dir out/` → AV offset (frames), min dist, confidence. |offset| ≥ 2 frames or confidence below the project baseline ⇒ flag AI-LS1. A constant offset can be slipped in post; an offset that changes over time = drift ⇒ T-EDIT/REGEN.

### 5.12 Metric benchmark (when batch comparison is needed)
VBench: `pip install vbench` then `vbench evaluate --videos_path $DIR --dimension subject_consistency --mode=custom_input` (usable custom-input dimensions: subject_consistency, background_consistency, motion_smoothness, dynamic_degree, aesthetic_quality, imaging_quality; temporal_flickering requires filtering for static videos). Use it to **rank takes** or compare prompt configurations, not to replace human review. VideoPhy-2 has an auto-evaluator (1–5 scale for semantic adherence & physical commonsense) — optional for physics-heavy shots.

---

## 6. Scoring rubric + decision tree

### 6.1 Rubric (each criterion 0–5)

| Criterion | Weight | 5 | 3 | 1 | 0 = gate fail |
|---|---|---|---|---|---|
| **B — Story beat delivered** | 0.25 | Beat clear, on time, matches intent | Beat present but weak/off-timing | Ambiguous | Beat does not happen / wrong meaning |
| **P — Performance** | 0.15 | Correct emotion, natural, believable micro-expressions | Correct emotion, slightly stiff/float | Wrong tone | Unintentionally comic / breaks character |
| **C — Camera match** | 0.15 | Framing, lens, move, duration match shotlist/previs | Minor deviation, still cuttable | Clear deviation, affects coverage | 180° axis crossed / wrong shot type |
| **K — Continuity** | 0.15 | Matches all items C1–C14 with adjacent shots | 1–2 S1 deviations | Fixable S2 deviation | S3 deviation (main wardrobe/prop/identity) |
| **A — Artifacts (visual)** | 0.20 | Not visible at normal speed | Only S0/S1 | ≥1 S2 within in/out | Any S3 within in/out |
| **S — Audio** | 0.10 | Correct dialogue, in sync, clean, no clipping | Minor fixable defects | Must be partially replaced | Wrong dialogue/language, broken sync (if the shot uses original audio) |

`Score = Σ weight × score` (0–5). Any criterion = 0 ⇒ **gate fail**, regardless of total. If the shot does not use original audio (replaced by VO/score), set S = n/a and redistribute the weights.

### 6.2 Decision tree
```
TECH hard-fail? ── yes → REJECT (R5 same prompt; if repeated 2 times → check gen parameters) 
   │ no
Any gate-fail (criterion = 0)? ── yes ─┐
   │ no                                │
Score ≥ 4.0 and no S2 in in/out? → CIRCLE (R0/R1)                │
Score 3.0–3.9 or S2 present:                                      │
   ├─ Defect outside the needed in/out?          → CIRCLE with TRIM (R1)
   ├─ Defect is grade/global flicker/grain/text/replaceable audio? → CIRCLE-COND + POST note (R2)
   ├─ Defect localized ≤ ~5s, 1 character/1 region? → T-EDIT (R3), re-QC the whole take
   └─ Duration short / beat not finished?        → EXTEND (R4)
Gate-fail / Score < 3.0: ◄──────────────────────────────────────┘
   ├─ Only this take is defective (other takes, same prompt OK)? → use another take or R5
   ├─ Defect repeats in ≥ 50% of takes with the same prompt?     → R6 REGEN-CHANGED (change prompt/refs/simplify)
   └─ Defect repeats after ≥ 2 rounds of R6 / shot exceeds model capability
      (multiple people interacting, complex physics, rotating hero prop)? → R7 BACK-TO-PREVIS / redesign
Budget exhausted (6.4)? → R8 ESCALATE: choose best-available + post plan, or cut/redesign the shot
Any SAFE-1 / likeness / legal? → R8 ESCALATE (mandatory, regardless of score)
```

### 6.3 Comparing multiple takes of the same shot
1. Eliminate gate-fail takes. 2. Rank by B, then A (beat & artifacts matter most). 3. On a tie → choose the take with better continuity with the **circled hero take of the adjacent shot** (do not choose on isolated beauty). 4. Circle hero + 1 distinct alt (the alt serves as cover in the edit).

### 6.4 Regeneration budget (cost cap)
- Default per unit: **at most 3 rounds** (round = 1 batch of N takes), e.g. 4 takes/round ⇒ ≤12 takes; at most 2 timestamp-edits on the same take.
- Track `cost_per_accepted_second = total gen cost of the unit / usable circled seconds`. Exceeding the project budget (declared in skill 1/6) ⇒ stop & escalate.
- After each failed round, a **deliberate change is mandatory** (recorded in the log as "what changed"); no blind re-rolls.

---

## 7. Review log template

### 7.1 CSV (machine-readable; `in_sec`/`out_sec` are decimal seconds from the start of the take; `scripts/export_edit_list.py` converts to `edit_list.csv` for skill 8)
```csv
review_id,date,scene,shot_ids,unit,take,version,file,prompt_hash,seed,duration_s,in_sec,out_sec,tech_pass,score_B,score_P,score_C,score_K,score_A,score_S,score_total,gate_fail,artifacts,decision,route,circled,fix_notes,escalate,escalate_q,reviewer,human_confirmed,gen_round,cost_units
R0142,2026-10-02,S03,"S03_040;S03_050",U02,T04,v1,U02_T04_r1.mp4,9f2c1a,771234,28.4,2.10,9.75,Y,5,4,4,4,3,3,4.05,N,"AI-HD1@06.20(S1);AI-TX1@14.0-16.5(S1)",CIRCLE,R1,HERO,"Use 02.10-09.75; 06.20 finger fuse hidden by motion blur",Y,"Is hand at 06.20 noticeable at 1x?",claude,PENDING,1,4
R0143,2026-10-02,S03,"S03_040;S03_050",U02,T02,v1,U02_T02_r1.mp4,9f2c1a,118823,28.4,,,Y,3,3,4,1,2,3,2.6,N,"AI-ID1@18-28(S2);AI-OP1@11.4 cup vanishes(S3)",REJECT,R6,,"Cup disappears behind arm; add 'cup stays on table' + shorter unit",N,,claude,,1,4
```
Artifact codes in the form `CODE@timestamp(severity)`, multiple separated by `;`.

### 7.2 Markdown (human-readable)
```markdown
## Dailies — S03 / Unit U02 (S03_040–S03_050) — 2026-10-02 — round 1/3
Shotlist: S03_040 MCU Mai sets down cup, 50mm, static, 4s | S03_050 OTS Huy→Mai, slow push-in, 6s
Prompt hash 9f2c1a · 4 takes · budget used 4/12 takes

| Take | Tech | B | P | C | K | A | S | Tot | Decision | In–Out | Key notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T04 | ✔ | 5 | 4 | 4 | 4 | 3 | 3 | 4.05 | ⭕ HERO (R1) | 02.10–09.75 | fused finger 06.20 (S1, blur) |
| T01 | ✔ | 4 | 3 | 4 | 4 | 3 | 3 | 3.55 | ALT (R2) | 01.00–09.00 | background flicker 03–05s → deflicker |
| T02 | ✔ | 3 | 3 | 4 | 1 | 2 | 3 | 2.60 | ✖ (R6) | – | cup vanishes 11.4 (AI-OP1 S3), ID drift 18s+ |
| T03 | ✖ | – | – | – | – | – | – | – | ✖ TECH (R5) | – | freeze 0.6s @ 07.3 |

**Continuity carried forward (from T04):** red scarf wrapped once; cup in left hand ~1/2; lamp off; light rain.
**Next round changes:** none needed (circled).
**Escalations:** (1) T04 06.20 hand — is it noticeable at 1x? (2) T04 lip-sync 07.8–09.5 — confirm.
**Post notes → skill 8:** T01 deflicker 03–05s if the alt is used; T04 audio: keep dialogue, replace ambience.
```

### 7.3 Fix note for skill 6 (regenerate / T-EDIT)
```yaml
unit: S03_U02
from_take: T02
route: R6
problem: "AI-OP1 cup vanishes behind Mai's arm at 11.4s; AI-ID1 Mai's face drifts after 18s"
evidence: [qc/S03_U02_T02/burst_11.4.jpg, qc/S03_U02_T02/id.csv]
change:
  prompt_add: "the white ceramic cup remains on the table, fully visible, throughout"
  references: [mai_front.png, mai_34.png]   # add 3/4 view
  duration_s: 15        # split unit: shorter to reduce drift
  camera: "static, no push-in on S03_040"
keep: [wardrobe, lighting, blocking from previs S03_040]
acceptance: "cup visible every frame; id cos_sim >= baseline-0.10 throughout"
```

---

## 8. Escalation rules (when Claude must hand off to a human)

Claude **must** escalate (not decide on its own) when:
1. **Motion quality needs real playback:** AI float, timing/acting rhythm, motion smoothness, whether a camera move "feels" right, slight foot sliding, micro-jitter. Frames are not enough to conclude.
2. **Any circled HERO take** — a human gives final confirmation at 1x, 0.5x, loop before handoff to skill 8 (`human_confirmed=Y`).
3. **Lip-sync and voice quality:** metallic voice, voice inconsistency, vocal emotion, accent/language — even if ASR + SyncNet give clear results, a human still needs to listen to the hero take.
4. **Severity on the S1/S2 boundary** where the decision changes the route (accept vs regenerate).
5. **Competing performance/creative judgments:** two takes with equal scores but different acting choices.
6. **Likeness, brand, logo, legal text, sensitive content, children, violence** (SAFE-1) — always.
7. **Budget:** reaching 80% of the regeneration budget or cost/accepted-second exceeding target.
8. **Route R7** (back to previs/shot design) — plan changes need director approval.
9. **Metrics and eyes disagree:** e.g. temporal_qc flags a lot but the frames look fine, or vice versa.
10. **Region too small/hard to read** (distant hands, small eyes, small text) even after cropping.

**Escalation question format** (so the human can answer quickly): `[Take] [timestamp range] [suspected issue] [yes/no question] [consequence of each answer]`, e.g.: "U02_T04_r1 06.0–06.6 — fingers fused while setting down the cup. Visible at 1x? Yes → T-EDIT 05.5–07.0; No → keep as-is."

---

## 9. Anti-patterns

| Anti-pattern | Why it is wrong | Do this instead |
|---|---|---|
| **Accept "good enough" artifacts** because many gens were already spent | S2 played full screen breaks the illusion; audiences notice hands/faces first | Apply severity + modifiers consistently; record the reason if lowering the bar, escalate |
| **Judge single frames only** / only look at the first frame or thumbnail | Temporal artifacts (morph, popping, flicker, float) are invisible on 1 frame — confirmed by Artifact-Bench | Contact sheet + temporal_qc + bursts around every hot spot |
| **Sparse uniform sampling then concluding** (1 fps for 30s) | Misses 2–6 frame events | 2 fps for sheets, 24-frame consecutive bursts for suspect regions |
| **Ignoring audio** | Seedance generates audio with the video; wrong dialogue/language/clipping are S2–S3 defects | Audio pass mandatory; spectrogram + ebur128 + astats; ASR if available |
| **Fix in post what should be regenerated** | Identity drift, physics, lip-sync, morphs cannot be fixed in post at reasonable cost | Post only for grade, global deflicker, grain, text, 1–3 frame paint, audio replace |
| **Regenerate what post could fix cheaply** | Wastes budget, may lose a good performance | Global flicker, color, text → R2 |
| **Endless regeneration** / blind re-rolls | Cost cap blown, nothing learned | 3-round budget; each round records "what changed"; repeated defect → R6/R7 |
| **Drifting from shotlist** (circling a "prettier" take with different framing/beat) | Breaks coverage and continuity, editor cannot cut it | Score C and B against the shotlist; propose shotlist changes via escalation, not unilaterally |
| **Circling without in/out points** | Editor must re-watch all 30s | Always record in/out, reason |
| **No re-QC after T-EDIT/extension** | The edit may change face/voice/prop in unedited parts; extension joins expose a seam | Re-run all passes on the new version; check the seam ±1s around the join point |
| **Comparing continuity to the reference instead of the adjacent shot** | The reference may be correct while two consecutive shots still mismatch | Compare both: visual bible and last/first frame of adjacent shot |
| **Trusting metrics absolutely** | CLIP/face/flow thresholds depend on content, lighting, angle | Calibrate a baseline on human-approved takes; metrics only flag |
| **Vague logs** ("a bit weird in the middle") | Not actionable for skill 6/8 | Artifact code + timestamp + severity + route + evidence file |
| **Handling each take independently** | Misses systematic prompt defects | Count defect frequency across takes with the same prompt (≥50% → prompt defect) |

---

## 10. Gate checklist (before handoff to skill 8)

**Per unit**
- [ ] Every take has passed the technical pass; log `tech_summary.txt` stored next to the file.
- [ ] Every take has rubric scores or a reject reason; artifacts recorded as `CODE@time(Sx)`.
- [ ] Each shot in the shotlist has exactly 1 HERO (+ at most 1 ALT) with in/out points.
- [ ] HERO has no S3 and no unresolved S2 within in/out.
- [ ] Continuity note (facing page) for each HERO; side-by-side with adjacent shots checked.
- [ ] HERO audio: no clipping, dialogue matches script & language, sync checked; or marked "audio replace" for skill 8.
- [ ] Identity check (embedding or eyes + reference) for main characters in the HERO.
- [ ] Every T-EDIT/EXTEND version fully re-QC'd.
- [ ] Clear post notes for each HERO using R2.
- [ ] Escalations answered by a human; `human_confirmed=Y` for every HERO.
- [ ] Budget: number of rounds and cost/accepted-second recorded.

**Per scene / film**
- [ ] Total HERO duration matches (±10%) the scene's target timing.
- [ ] Screen direction & 180° axis consistent across the scene (check with the sequence of first-frames of every HERO in cut order).
- [ ] Time of day / weather / lighting progress plausibly across the scene.
- [ ] No shot left in an unresolved R6/R7 state (or a cut/replace decision has been made).
- [ ] Review log CSV fully exported for skill 8.

---

## 11. Uncertain info (unverified / needs re-checking)

- **Seedance 2.5 specs:** 30s/pass, up to ~50 references, partial/timestamp editing, extension "up to double the original length", simultaneously generated audio — per news articles and third-party reviews (xenospectrum, atoms.dev); ByteDance has not published native resolution, per-reference-type limits, or edit preservation metrics. The exact timestamp-edit API syntax must be checked against official docs when skill 6 integrates it.
- **Metric thresholds** (face cos_sim baseline −0.10, z=3.5, min-dluma 1.5, SyncNet offset ≥2 frames) are **proposed heuristics**, not validated on Seedance footage. Calibrate on 10–20 human-approved takes from the project itself.
- **InsightFace pretrained models** (buffalo_l) are non-commercial research only per PyPI — commercial films need a replacement model or a license. Likewise check CLIP/DINO/SyncNet licenses if integrated into a product.
- **Netflix loudness**: −27 LKFS ±2 LU dialog-gated, −2 dBTP taken from secondary sources (production-expert, knuterikevensen); Netflix's official spec page redirects to a page requiring JavaScript, could not be read. ffmpeg does not measure dialog-gated.
- **Snippets identity_track.py, SyncNet, Whisper, VBench** not test-run in this environment (need model downloads/GPU). `qc_take.sh` was assembled from commands that were run individually.
- **Artifact-Bench** (arXiv 2605.18984, 2026) figures 47.5%/87.7% are per HTML v1; may change in later versions. The MLLMs tested do not include the exact Claude configuration of this plugin.
- **Severity scale S0–S3 and rubric weights** are this document's own design (synthesized from QC practice), not an existing industry standard; the Netflix Production QC Glossary does not define a standard severity.

---

## 12. Sources (opened)

1. Netflix — The Production QC Glossary: https://partnerhelp.netflixstudios.com/hc/en-us/articles/21890106462611-The-Production-QC-Glossary
2. Veneratech — Delivering to Netflix QC requirements: https://www.veneratech.com/delivering-to-netflix-qc-requirements-in-a-nutshell-and-how-to-comply-with-them
3. Production Expert — Understanding Loudness Part 4 (Netflix/broadcast): https://www.production-expert.com/production-expert-1/understanding-loudness-part-4-creating-loudness-compliant-mixes-for-broadcast-and-netflix
4. Knut Erik Evensen — Measuring the Netflix loudness level: https://www.knuterikevensen.com/2022/06/04/measuring-the-netflix-loudness-level/
5. Wikipedia — Script supervisor: https://en.wikipedia.org/wiki/Script_supervisor
6. ScriptSupervisor.com.br — Script supervisor template: the 4 forms: https://scriptsupervisor.com.br/blog/script-supervisor-template/
7. Wikipedia — Dailies: https://en.wikipedia.org/wiki/Dailies
8. Keheka — Tech Check Checklist for Compositors: https://www.keheka.com/tech-check-checklist/
9. VBench paper (arXiv 2311.17982): https://arxiv.org/abs/2311.17982 and PDF https://arxiv.org/pdf/2311.17982
10. VBench GitHub: https://github.com/Vchitect/VBench ; project page https://vchitect.github.io/VBench-project/
11. EvalCrafter (arXiv 2310.11440): https://arxiv.org/abs/2310.11440
12. VideoPhy-2 project page: https://videophy2.github.io/
13. Artifact-Bench (arXiv 2605.18984): https://arxiv.org/html/2605.18984v1
14. Skyra — AI-generated video detection via grounded artifact reasoning: https://arxiv.org/html/2512.15693v1
15. FilmDaft — Aspect ratios, motion and temporal artifacts in AI video: https://filmdaft.com/aspect-ratios-motion-and-temporal-artifacts-in-ai-video/
16. NemoVideo — Why your AI videos look fake (and how to fix them): https://www.nemovideo.com/blog/why-ai-videos-look-fake-how-to-fix
17. Xenospectrum — Seedance 2.5 extends to 30 seconds, 50 references, partial editing: https://xenospectrum.com/en/seedance-2-5-video-editing/
18. Atoms.dev — Seedance 2.5 review / production workflow: https://atoms.dev/blog/seedance-2-5-review-30-second-ai-video-production-workflow
19. PySceneDetect CLI docs: https://www.scenedetect.com/docs/latest/cli.html
20. FFmpeg Filters documentation: https://ffmpeg.org/ffmpeg-filters.html (option names/defaults cross-checked locally via `ffmpeg -h filter=<name>`, ffmpeg 6.1.1)
21. InsightFace on PyPI: https://pypi.org/project/insightface/
22. OpenAI CLIP GitHub: https://github.com/openai/CLIP
23. OpenCV optical flow tutorial: https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html
24. SyncNet (joonson/syncnet_python): https://github.com/joonson/syncnet_python
