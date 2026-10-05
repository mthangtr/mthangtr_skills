# 04 — Shot Design & Directing (Skill 4 reference)

> **Model-agnostic note (v0.3.0):** this research was compiled with Seedance 2.5 as the reference video model. Every Seedance-specific number here (call length, ≤30 s units, ≥3 s shots, reference counts, 24 fps, 720p, 32 kHz audio, @Image tags, prices, policy) is an example from the `seedance-2.5` profile, not a pipeline rule. Read the real limits from the active profile (`video-generation/references/models/<id>/profile.json`) and apply `film-pipeline/references/shared-conventions.md`. Where this file says "skill 6", read `video-generation`; references like "06 §N" point to `video-generation/references/models/seedance-2.5/knowledge.md`.

> Purpose: knowledge for skill 4 (`shot-design`). Input: `story` (skill 2) + `visual-bible` (skill 3). Output: `shotlist.json` so that skill 5 (Blender previs) can build camera/blocking/light and skill 6 (Seedance 2.5) can generate video per generation unit ≤30s.
> Research date: 2026-10-02. Technical terms kept in English.

---

## 1) Core principles

1. **Emotion first, then story, then rhythm.** Walter Murch ranks the priorities of a cut: Emotion 51%, Story 23%, Rhythm 10%, Eye-trace 7%, 2D plane of screen 5%, 3D space 4%. Consequence for shot design: every shot must answer "what does the audience feel here?" before asking "where does the camera go?". Sacrificing some spatial continuity to preserve emotion is allowed; the reverse is NOT.
2. **Every technical choice serves POV.** Mackendrick: "If I move the camera, from whose point of view is the audience experiencing the action?" Every scene must declare a POV owner (the character the audience "stands with").
3. **A real film is 60–80% understandable with the sound off** (Mackendrick). Test: read the shotlist without the dialogue column — is the story still readable? If not, the shot design relies too heavily on dialogue.
4. **Movement must come from real behavior, not busywork** (Katz). The camera moves only when motivated: following a character, revealing information, a shift in power relations, or expressing a change in inner state.
5. **Restraint.** Murch: "You are being paid to make decisions" — do not cut just because there are many options. Fewer shots, but each shot has a reason.
6. **Acting is doing.** Acting = pursuing an objective through an action verb; emotion is the consequence (Weston, Ed Hooks). Shot design and performance direction are written in verbs, not in emotional adjectives.
7. **Intentional variety.** Modern film (intensified continuity, Bordwell) uses ASL 2–4s, lots of close framing, free-ranging camera — but that is a statistic, not a goal. For AI film, the biggest risk is UNIFORMITY (every shot alike in size, move, duration). Structured variety = a sign of authorship.
8. **Design for the edit room.** Every important beat needs at least 2 ways to cut (coverage options) or a clear reason for using a oner/camera cutting.
9. **For AI: one shot = one primary action + one primary camera instruction.** "If the subject action is complex, keep the camera still. If the camera must move, keep the subject action light."

---

## 2) Breakdown process (director's breakdown)

Run sequentially; each step writes an intermediate artifact (may live in `shotlist.json` → `scenes[].breakdown`).

### Step 0 — Beginner's mind read
Read the story once without analysis; note feelings, associations, questions (Weston: "permission to fail" before logical analysis). Write 3–5 sentences of "what I feel in this scene".

### Step 1 — Scene spine & conflict (McKee 5-step, via Screenplayology)
1. **Define conflict:** who drives the scene, what they want (objective), what blocks them (obstacle).
2. **Opening value:** the value at stake at the start of the scene (e.g. trust +, hope +).
3. **Break into beats:** beat = one action/reaction pair; a new beat starts when a character changes tactic.
4. **Closing value:** the value at the end of the scene (e.g. trust −). If opening = closing → the scene has no turn; consider cutting it.
5. **Turning point:** the moment of "the greatest gap between expectation and result". This is where the strongest shot goes (usually the closest framing or a change in camera grammar).

### Step 2 — Per-character playable layer (Weston toolkit)
For each main character in the scene:
- **Objective** (what they want from the other person) — written as "to make X …".
- **Action verbs per beat** — transitive verbs aimed at the partner: *to probe, to reassure, to corner, to seduce, to brush off, to beg, to challenge, to punish*.
- **Facts/given circumstances** — concrete events ("she lied to him last week"), not states ("feels betrayed").
- **Subtext image** — a concrete inner image.
- **Physical task/life** — a concrete manual task (picking a thread off a shirt, washing a cup) to occupy the conscious mind so the subconscious produces real expression.
- **Listening mode** — listening in order to do what (detect a lie, find an excuse to forgive…).
- **Status** high/low, and whether it changes during the scene.

### Step 3 — POV & camera stance
- **POV owner** of the scene/beat.
- **Objective vs subjective camera:** objective = observing (eye level, static/tripod, medium-wide, normal lens); subjective = close to the character (POV shot, tight OTS, light handheld following breathing rhythm, lens near human-eye, focus following what the character attends to). Rule: switching objective→subjective at the turning point is a powerful tool; using subjective for the whole film kills its effect.
- **Information strategy:** does the audience know more (suspense), the same (mystery alongside the character), or less (surprise) than the character? Decides what is seen in frame and when the reveal happens.

### Step 4 — Blocking
Place characters in space first, camera second (Katz: staging first, coverage second). See section 3.6 on blocking patterns. Record the floor plan as coordinates for Blender (section 9).

### Step 5 — Shot list
For each beat: choose shot(s) from the tables in section 3; mark which beats are "hero" (need the best shot, more generation budget) and which are "connective".

### Step 6 — Edit plan
Mark cut points, J/L cuts, estimated duration, rhythm curve (section 4.5).

### Step 7 — Lighting intent
One lighting block per scene, overridden at shot level if needed (section 5).

### Step 8 — AI unitization
Group shots into generation units ≤30s (section 7). Run the anti-pattern scan (section 8) and gate checklist (section 10).

---

## 3) Camera language reference tables

### 3.1 Shot sizes

| Code | Size | Frame | Psychological effect | Use when | Avoid when |
|---|---|---|---|---|---|
| EWS | Extreme wide | Person very small | Isolation, overwhelmed by environment, setting as character | Opening/closing an act, stressing loneliness or scale | Opening EVERY scene (anti-pattern "drone establishing") |
| WS/LS | Wide/Long | Full body + lots of environment | Geography, context, person–space relationship | Establishing space before cutting closer; full-body action | Subtle emotional beats |
| FS | Full | Head–feet fit the frame | Full body language, character groups | Blocking with movement, physical comedy | |
| MLS/MWS | Medium long | From the knees | Balance of character/environment | Walk-and-talk; transitioning between wide and medium | |
| CS | Cowboy | Mid-thigh up | Action energy, weapons/hands | Standoff, action | |
| MS | Medium | Waist up | Neutral, the "workhorse" of dialogue | Dialogue, important hand gestures | Turning point (lacks weight) |
| MCU | Medium close-up | Chest up | Prioritizes the face but keeps distance | Face-to-face dialogue, listening | |
| CU | Close-up | Face | Intimacy, reading emotion, micro-expression | Turning point, key reaction, decision | Continuous use (loses value) |
| ECU | Extreme close-up | Eyes/lips/object | Extreme focus, transformation, meaning of an object | Insert of a key detail, moment of realization | No new information to show |
| INS | Insert | Object/hands | Specific information (letter, bloodstain) | Plot info, cutaway to reset the axis | |

Framing types: **Single** (isolation, focus), **Two-shot** (connection, chemistry, power — the distance between the two people in frame = emotional distance), **Three-shot/group**, **OTS** (orients between speakers, emotional connection; dirty OTS = shoulder in frame, clean single = isolation), **POV** (puts the audience inside the character).

**Size progression rule:** move from far to near as tension rises in the scene; abrupt size jumps (wide→CU) are reserved for shock/reveal. Save the closest size for the turning point — if the scene is already in CU from the start, the turning point has nowhere left to "advance".

### 3.2 Camera angles (vertical) & height

| Angle | Effect | Use when |
|---|---|---|
| Eye level | Neutral, equal | Default; dialogue between equals |
| Shoulder level | Natural, flattering | Portraits, dialogue |
| Low angle | Power, threat, dominance | Character holds power / has just seized it |
| High angle | Weakness, being judged, smallness | Character has failed, is being watched |
| Overhead / bird's eye | Omniscience, fate, pattern | Revealing layout, "looking down on fate" moments |
| Ground level | Immersive, strange | Action, child/animal point of view |
| Dutch tilt | Unstable, something is wrong | Psychological breakdown — use rarely, with a reason |
| Aerial | Scale, geography | Once for opening/ending, not every scene |

**Rule:** the angle difference between two characters in shot/reverse = the status difference. If status reverses during the scene, the angle must change at the reversal beat. Angle unchanged throughout the scene = status unchanged.

### 3.3 Lens focal length (normalized to full-frame 35mm equivalent)

| Lens (FF eq.) | Group | Visual effect | Psychology | Use when |
|---|---|---|---|---|
| 14–24mm | Ultra wide | Exaggerates distance, distorts faces up close | Unease, overwhelm, comedy, psychological distortion | Large spaces, distorted POV, close-up comedy |
| 24–35mm | Wide | Lots of environment, movement toward camera feels faster | Immersive, dynamic, "in the room" | Wide/master, handheld close to character, staging in depth |
| 35–55mm | Normal | Close to the human eye | Honest, observational, objective | Default coverage, objective camera |
| 65–100mm | Short tele | Flattering faces, compressed background, shallow DOF | Intimacy, isolating the character | CU, MCU, tight OTS |
| 135mm+ | Tele | Strong spatial compression, lateral movement feels faster | Surveillance, trapped, voyeur, pressure | Surveillance, character hemmed in by a crowd |

- **Sensor/crop:** focal length is written as FF-equivalent so Blender (sensor width 36mm) and the Seedance prompt share one language. Blender: `camera.data.sensor_width = 36`, `lens = <mm>`. Super35 (~24.9mm) ≈ 1.4–1.5× crop if a cinematic look must be simulated.
- **Bipolar lens (Bordwell):** modern films tend toward wide for masters and long for singles/OTS. Usable, but better when the lens changes WITH emotion (e.g. gradually longer as the character becomes isolated).
- **Do not change lenses between shots of the same setup without a reason** — keeping a "lens family" per scene gives a unified feel.

### 3.4 Depth of field & focus

| Technique | Effect | Use when |
|---|---|---|
| Shallow (f/1.4–2.8 eq.) | Isolates the subject, intimacy | Emotional CU, character lost from the world |
| Deep (f/8+) | Audience reads the whole frame themselves | Staging in depth, multiple simultaneous actions, spatial relationships |
| Rack focus | Forces a shift of attention, reveal | New information appears on another plane |
| Soft focus | Dream, memory | Flashback, dream |
| Split diopter | Two planes sharp at once, stylized | Very rare |

**AI note:** "shallow DOF" + "bokeh" is the model's favorite default → easily becomes an anti-pattern. Specify DOF intentionally, and use deep focus for staging in depth.

### 3.5 Camera movement — effects & motivation

| Move | Effect | Motivated when | AI reliability (Seedance-class) |
|---|---|---|---|
| Static / locked-off | Focuses attention on performance & composition | Dialogue, comedy, observation, shots that need stability | Medium–high: must prompt "locked tripod" explicitly, model tends to drift/push-in on its own |
| Pan | Connects two horizontal points, follow | Following a gaze/action, horizontal reveal | High |
| Tilt | Height, vertical reveal | Looking up, measuring height, falling | High |
| Push-in (dolly in) | Adds weight, moves into the inner world | Character realizes / decides; information reaches them | High — but the MOST OVERUSED |
| Pull-out (dolly out) | Isolation, consequence, reveals context | After a shock; revealing a character alone | High |
| Tracking / follow | Accompanying, continuity | Character moves with purpose | Medium–high (if subject action is simple) |
| Truck/crab | Lateral sweep, parallel | Moving in parallel, reveal through foreground | Medium |
| Arc/orbit | Changes relationships, "rotates" the world around the character | Major shift in perception, a moment of connection between two people | Medium; identity drift, background morph; overused |
| Crane/jib up-down | Grand, shifts from individual → world | Opening/closing big scenes | Medium |
| Handheld | Energy, instability, documentary | Chaos, panic, subjective | Medium (easily becomes fake shake) |
| Whip pan | Energy, linking, comedic timing | Fast switch between two subjects | Low–medium |
| Zoom | Artificial, the machine's "gaze" | Stylized, documentary, 70s look | Medium |
| Dolly zoom | Distorted perception, vertigo | One moment of horrified realization | Low, needs testing |

**Motivation test (mandatory for every shot with a move):** fill in "Camera [move] BECAUSE [character/audience] [needs to/is] ___." If the sentence ends with "to look pretty/cinematic/dynamic" → change to static.
Three valid sources of motivation: (a) **subject-motivated** — following character movement; (b) **information-motivated** — reveal; (c) **emotion-motivated** — a change in inner state (only on beats with a turn).
Move speed must match the emotional tempo; start/end the move on action (the move starts when the character stands up, stops when they stop).

### 3.6 Composition & staging in depth

- **Rule of thirds / lead room / headroom:** the character looks toward the open space (lead room). Deliberately lacking lead room (looking into the frame edge) = blocked, suffocating.
- **Short-siding** (looking toward the near edge) to create unease; **centered symmetry** = power, ritual, Kubrick-esque — use intentionally, not by default.
- **Frame-within-frame** (doors, mirrors, window frames) = trapped, observed.
- **Spielberg — spatial division:** place the two sides in the two halves of the frame during ideological conflict; open the scene with a CU of a prop carrying subtext.
- **Kubrick — a single frame tells the whole story:** depth, eyelines leading the eye, shadows creating hierarchy, little movement.
- **Iñárritu — depth layering & reveals:** place actors at multiple depths, bring them in/out of frame to control focus; drop in the CU exactly at the key emotional moment.
- **Staging in depth (Katz/Welles/Renoir):** control emphasis with foreground/mid/background instead of cutting; use depth to dramatize isolation. One deep-staged shot can replace 3 coverage shots — very beneficial for AI (fewer shots, less continuity risk).

### 3.7 Blocking patterns (Katz)

| Pattern | Description | Use when |
|---|---|---|
| **I pattern** | Two people on one axis — the basic unit | 2-person dialogue |
| **A pattern** | One person in the middle, two on either side | Mediator, caught in the middle |
| **L pattern** | Two people off-axis, one deeper | One person evading, withholding information |
| **Triangle** | Three positions → every basic setup | 3-person group coverage |
| Profile face-to-face | Balanced confrontation | Standoff |
| One person with back turned | Withheld eye contact → tension | Concealment, shame, refusal |
| Back-to-back | Complete separation | Breakup |
| Line/convoy | Moving in a line | Group movement, hierarchy |

**Blocking = relationship:** changing distance = changing relationship. Every blocking change (sitting down, stepping forward, turning away) should coincide with a beat change. Reveal: a character steps into frame from hidden blocking, or the camera moves past the foreground.

---

## 4) Coverage & continuity rules

### 4.1 Triangle system & dialogue coverage menu (Katz)
Three camera positions on ONE side of the 180° axis are enough for: angular singles, OTS, two-shots, POV — all intercut without confusion. Standard menu for 2-person dialogue:
1. **Master/wide two-shot** — runs the whole scene (for AI: usually a separate unit or the opening stretch).
2. **OTS A→B** and **OTS B→A** (reverse) — same size, same lens, mirrored angle.
3. **Clean singles MCU/CU** of A and B — for inner beats.
4. **Reaction shots** — especially of the listener at the turning point.
5. **Inserts/cutaways** — objects, hands; used to reset the axis or compress time.

**Coverage vs camera cutting:** coverage = safe but dull; camera cutting = shoot only the storyboarded shots, risky but frees the staging. For AI, every shot costs generation budget → **hybrid**: camera cutting for connective beats, double coverage (2 options) only for the turning point and dialogue-heavy beats.

### 4.2 180° rule & eyeline
- Axis = the line connecting two characters (or character–object). Camera on one side → A always looks screen-right, B always looks screen-left.
- **Valid axis crossings:** (1) a neutral shot placed on the axis (head-on / directly behind the head) to reset; (2) a camera move crossing the axis within the same shot (the audience sees it); (3) a cutaway with no spatial orientation; (4) a character's movement creating a new axis within the shot.
- **Deliberate crossing** = signals disorientation/breakdown — only on beats that need that feeling; record `axis_break_intent`.
- **Eyeline match:** looking shot → shot of what is looked at; eyeline height must match (a standing person looks down at a seated one). Eyeline close to lens = intimate; far from lens = objective. **DO NOT look straight into the lens** unless intentionally breaking the fourth wall.

### 4.3 30° rule
Between two consecutive shots of the same subject: change the angle by ≥30° or change focal length noticeably (Wikipedia cites ~20mm; in practice: change at least one size step, e.g. MS→CU). Smaller changes = unintended jump cut ("different enough to signal that something changed, but not enough to re-evaluate the context" — Murch).

### 4.4 Screen direction, match on action
- **Screen direction:** if a character moves L→R, the next shot is still L→R, unless they are seen changing direction in frame. "Outbound" journeys usually L→R, "return" R→L (convention, not mandatory) — what matters is CONSISTENCY.
- **Match on action:** cut in the middle of an action (standing up, opening a door, turning the head) — the motion hides the cut. Design: shot A ends mid-motion, shot B starts with the same motion (0.5–1s overlap on each side so the editor can choose the frame).
- **Eye-trace:** the point of attention at the end of shot A should be near the point of attention at the start of shot B (Murch). Record `eye_trace_out` / `eye_trace_in` (thirds coordinates) for each shot.

### 4.5 Cutting points, rhythm, duration
- **Cut on thought / blink:** Murch — people blink when a thought completes; cut when the character (and audience) has just "understood". In performance direction, mark `thought_complete_at` on every shot.
- **J cut:** the next shot's audio comes in before its picture → leads, prepares, natural conversational rhythm. **L cut:** the previous shot's audio carries over onto the next picture → stays on the listener's reaction, reflection. Plan this at shot design: any reaction shot that will sit under the other person's line (L cut) must be designed longer than the line + 1s.
- **ASL data:** silent era ~5s; 1940 studio films had very long-ASL scenes (Shop Around the Corner opening ~82s/shot); contemporary films 2–4s (You've Got Mail ~4.1s) — Bordwell. Cutting et al. (143 films, 1935–2005): action films shorten ASL by up to ~50% in the final quarter; longer shots cluster at act boundaries; within each act there is a "scallop" shape — mid-act shots are up to ~1.1s shorter than at the start/end.
- **Applied to AI short film (proposed baseline, not a law):**

| Type | Suggested ASL | Shot range |
|---|---|---|
| Drama/quiet | 4–7s | 2–15s |
| Regular dialogue | 3–5s | 1.5–8s |
| Action/climax | 1.5–3s | 0.7–5s |
| Establishing/transition | 3–6s | 2–10s |
| Social vertical (Reels/TikTok) | 1.5–3s | 0.7–5s |

> ASL in the table is the **post-edit** length. In `shotlist.json`, `duration_s` is the generated segment length and must be ≥ 3 s; faster rhythm is achieved by trimming in post (record `edit.target_cut_s` if needed).

- **Rhythm curve:** long shots at the opening and closing of an act/scene, getting shorter toward the middle/climax, then one long "breathing" shot after the climax. Duration variance is mandatory: the coefficient of variation (stdev/mean) of durations within a scene ≥0.35, otherwise → monotonous.

### 4.6 Continuity props/state
Record state for every shot: prop positions, water level in a cup, which hand holds what, clothing (button undone?), wounds, light (time of day). This is what Seedance drifts on most across units.

---

## 5) Lighting intent notes (notes for previs)

Lighting intent is written at scene level, overridden at shot level. The language must translate to Blender (light type, relative position, energy ratio, color temp) and to the Seedance prompt (description of natural light sources).

### 5.1 Three functions (Stephen Burum, ASC)
1. **Shadow casting** — the key creates texture & facial structure (small source = hard, large = soft).
2. **Separation** — backlight/rim/set light creates light-dark planes, depth.
3. **Fill** — controls contrast = mood. Fill is placed near the camera; do not use fill to erase shadows.
- "Use as few lights as possible — if you can't see what each light is doing, turn some off."
- Day vs night differ in how light/dark areas are defined, not just in exposure.
- Actors look better on screen when facing toward the key.

### 5.2 Key/fill ratio

| Style | Ratio key:fill | Mood | Genre |
|---|---|---|---|
| High-key | ~1:1 – 2:1 | Optimistic, safe, open | Comedy, family, advertising |
| Normal drama | 2:1 – 4:1 | Natural, with depth | Drama |
| Low-key | 8:1 and above | Mystery, unease, moral conflict, isolation | Noir, thriller, horror |
| Silhouette | key ≈ 0 on the face | Anonymity, symbolism | Reveal, ending |

### 5.3 Key position & side of the face
- **Short-side (shadow side to camera):** the side of the face nearer the camera is in shadow → 3D, drama (default for serious dialogue).
- **Broad-side:** the lit side faces the camera → flat, open, high-key.
- **Rembrandt:** key ~45° above the eyes, triangle of light on the shadow-side cheek.
- **Butterfly/top:** glamour or (if hard, straight from above) menace, dark eye sockets.
- **Under-light:** unnatural, horror — only with a motivated source (fire, screen).

### 5.4 Motivated sources
The key must "come from" a source in the world: window, lamp, candle, screen, streetlight, fire. Record `motivated_source` for each scene; Blender places the light along that source's direction; the Seedance prompt mentions that source ("lit by a single window camera-left"). In-frame source (practical) + key from the same direction = believable.

### 5.5 Color temperature

| Source | Kelvin | Feel |
|---|---|---|
| Candle/fire | ~1800K | Warm, old, private |
| Tungsten/household lamp | ~3200K | Warm, safe, interior |
| Golden hour | ~3200K (warm) | Nostalgic, romantic |
| Neutral | ~4000K | Objective, mildly clinical |
| Daylight | ~5600K | Neutral baseline |
| Overcast | ~6500K | Cold, sad |
| Blue sky/shade, blue hour | 10000K+ | Cold, lonely |

- **Moonlight** by film convention = cold blue (a convention, not physics).
- **Intentional mixed temperature** (indoor tungsten vs window daylight) = tension between two worlds; only when intentional, "not an accident".
- Separation tip: slightly cool background, slightly warm subject (ASC talking-head).

### 5.6 Lighting arc
Lighting should change along the story arc (e.g. ratio rising gradually 2:1 → 8:1 as the character sinks into a secret). Record `lighting_arc` at film level for skill 7 (dailies) to check.

---

## 6) Performance direction

### 6.1 Principles
1. **No result direction.** Do not write "sad", "angrier", "scared". Write an action verb aimed at the partner:

| Result (forbidden) | Playable (use) |
|---|---|
| "Angrier" | "Make him feel the pain he caused" |
| "Scared" | "Beg for your life" |
| "Seductive" | "Invite her home" |
| "More threatening" | "Force him to back down" |
| "Show that you're angry" | "Threaten him into silence" |

2. **Facts instead of emotions:** "Remember that she lied to you last week."
3. **Physical task** occupies the hands → more natural expression.
4. **Purposeful listening** — the listener is half the scene ("Acting is doing; acting is also reacting" — Hooks).
5. **Play an action until something happens** to make the character play a different action (Hooks) → each shot holds ONE action; change action only when an event occurs (this is also the shot-splitting principle for AI).
6. **Thinking → conclusions; emotion → action** (Hooks). Show thought with a short pause BEFORE the action (micro-timing), not with emoting.
7. **A scene is a negotiation**; characters change tactic when blocked, they do not abandon the objective.
8. **Start in the middle** — the scene comes in "hot"; the first shot is already mid-action.
9. **Do not ask for a specific expression to be repeated** (Weston): what you want is the listening/the emotional event, not a forehead wrinkle.

### 6.2 Translating to AI generation (important)
Seedance does not "act" from a verb — it renders observable behavior. Therefore every shot has TWO layers:
- `intention` (verb + objective + subtext) — for Claude/editor to understand and keep the logic.
- `observable_behavior` — concrete physical cues, intensity cap, timing (seconds). This is the part that goes into the prompt.
Write cues on **intensity 1–5 (FACS A–E equivalent)**, default 2–3. Forbidden words: "dramatically, intensely, extremely, screaming, tears streaming" unless the beat requires it and the gate approves.

### 6.3 Levels by shot size
- **WS/FS:** emotion reads through posture, distance, walking pace, body orientation, large hand actions. The face is nearly unreadable → don't spend prompt on micro-expressions.
- **MS/MCU:** shoulders, hands, head direction, gaze, breathing visible in chest/shoulders.
- **CU/ECU:** "less is more" — eyes, lids, brows, mouth corners, dry swallow; one AU at low intensity is enough. The same level of acting as in a WS will be over-acting in a CU.
- **Micro-expressions:** ≤0.5s (Ekman), showing concealed emotion "leaking" out; macro expression 0.5–4s. Use micro-expressions to show SUBTEXT in CU: surface expression A, flash B in <0.5s, then back to A.

### 6.4 FACS reference
AU1 inner brow raiser · AU2 outer brow raiser · AU4 brow lowerer · AU5 upper lid raiser · AU6 cheek raiser · AU7 lid tightener · AU9 nose wrinkler · AU10 upper lip raiser · AU12 lip corner puller · AU14 dimpler · AU15 lip corner depressor · AU17 chin raiser · AU20 lip stretcher · AU23 lip tightener · AU24 lip pressor · AU25 lips part · AU26 jaw drop.

Prototypes (EMFACS): Happiness 6+12 · Sadness 1+4+15 · Surprise 1+2+5B+26 · Fear 1+2+4+5+7+20+26 · Anger 4+5+7+23 · Disgust 9+15+17 · Contempt R12A+R14A (one-sided). **Duchenne smile** = 6+12 (the eyes smile too); "Pan-Am smile" = 12 only → social/fake smile — a subtext tool.

### 6.5 Lookup table: emotion/intention → physical cues

| Emotion / intention | FACS core | CU/ECU cues (intensity 2–3) | WS/FS cues | Micro-timing | Over-acting to avoid |
|---|---|---|---|---|---|
| Genuine joy | 6+12 | Slight crinkle at eye corners, cheeks raised, smile reaches the eyes; short exhale through the nose | Shoulders relaxed, head slightly raised, lighter step, body oriented open toward the other person | Smile comes ~0.3–0.5s AFTER realization, fades slowly | Fixed toothy grin, constant nodding |
| Social/concealing smile | 12 (no 6) | Lips smile, eyes unchanged; smile drops fast when the other person turns away | Polite gestures, body angled slightly toward the exit | Switches on fast, drops abruptly | |
| Suppressed sadness | 1+4+15 (low), 17 | Inner brows lift slightly, mouth corners droop slightly, chin trembles slightly (AU17), eyes look down then recover; dry swallow | Shoulders slump, head bowed, slow movement, hands look for something to hold | Slower rhythm, pause before speaking | Streaming tears, sobbing, whole face scrunched |
| Grief breaking through (rare) | 1+4+15+17+25 | Lips open and trembling, broken rapid breathing, eyes squeezed shut | Body folds, loses center of gravity, slumps down | Bursts after a period of suppression | Only once per film |
| Fear | 1+2+4+5+20 (+26) | Eyes wide showing upper whites, brows raised and drawn together, lips stretched sideways, breath held | Backs away, shrinks, hands shield the body, freezes | Freeze 0.5–1s before reacting | Screaming, mouth wide open for long |
| Anxiety | 1+4 light, 24 | Quick darting glances, pressed lips, swallowing, blinking more | Hands busy with meaningless tasks (twisting a ring), weight shifting between feet | Irregular rhythm | Whole-body trembling |
| Suppressed anger | 4+5+7+23/24 | Brows lowered, lids tightened, lips pressed hard, jaw rigid, nostrils flared | Stands straight, moves closer, takes up space, decisive movements | Goes still BEFORE erupting; speaks slower | Shouting, flailing arms, constant glaring |
| Rage erupting | 4+5+7+23+25/26 | Bared teeth, neck tendons | Lunges, smashes objects | After buildup | |
| Contempt | R12A+R14A | ONE mouth corner raised, lids slightly lowered, head tilted/tipped back slightly | Partly turns back, looks down | Short, almost micro | Obvious eye-roll |
| Disgust | 9+15+17 (10) | Nose wrinkled, upper lip raised, head pulls back | Leans away, avoids touch | Fast reflex | |
| Surprise | 1+2+5B+26 | Brows raised, eyes open, mouth parted | Stops mid-motion | Very short (<1s) then shifts to another emotion | Holding the surprised face too long |
| Realization | 5→7, 25 light | Gaze stops, distant focus, one slow blink, lips part | Stops motion midway | Pause 1–2s = "thought complete" → cut point | Slapping the forehead |
| Decision/resolve | 7+24, 17 | Eyes locked on target, one exhale, jaw clenched | Stands straight, decisive first step | Inhale → pause → act | Dramatic nod |
| Shame | 1+4 light, 54/64 (head down, eyes down) | Eyes avert, blushing (hard for AI), pressed lips | Shrinks, turns away from the other person, partly covers face | Avoids eye contact when looked at | |
| Love/tenderness | 6+12 low, 1 light | Soft gaze, looks longer than normal, lips parted | Leans toward the other person, light touch | Holds the gaze 0.5s too long | Fixed "lovestruck" stare |
| Suspicion/probing | 4+7 light | Narrowed eyes, head tilted, long unblinking look | Keeps distance, arms crossed | Slow to answer | |
| Deception (lying) | Normal surface face + leaked micro | Micro-expression ≤0.5s of the true emotion; smile without AU6 | Self-touch (neck, nose), body oriented toward the exit | Answer comes unusually fast or slow | |
| Listening (active) | — | Natural blinking, eyes move between the speaker's two eyes, small reaction before the other finishes speaking | Body oriented toward the speaker, pauses physical task | Reacts ~0.2–0.5s after the trigger word | Steady rhythmic nodding |
| Exhaustion | 43 (eyes closed) for a while | Heavy lids, slow blinks, mouth parted | Weight sinks, leans on things | Every reaction delayed | |

FACS note: AU43 (eyes closed), AU54 (head down), AU64 (eyes down) belong to FACS's head/eye code group — double-check before using these code numbers in a spec (see section 11).

### 6.6 Avoiding over-acting (checklist)
- One main emotion + at most one subtext leak per shot.
- Intensity ≤3 for CU, except at the turning point.
- Use indirect behavior (hands, objects, breath) more than facial expression.
- Do not describe tears/screaming in the prompt unless it is the climax beat.
- Reactions come later than the trigger (real people need processing time).
- Characters do not "perform" emotion toward the camera; they are trying to achieve an objective, often hiding the emotion.

---

## 7) AI generation adaptation rules (reference model Seedance 2.5; limits from the active profile)

### 7.1 Confirmed capabilities (third-party sources, see section 11)
- Up to 30s of audio-video per pass; output 4–30s; 480p/720p/1080p confirmed via API (4K not confirmed).
- Reference: up to 30 images, 10 videos, 10 audio (EvoLink).
- Multi-shot within one generation: "setup, development, turn, resolution".
- Timestamp prompt `[0s] … | [3s] … | [6s] …`; timestamps are NOT frame-accurate, motion may start early/late.
- Multi-angle from one reference take (fal.ai): 13 angles from a 20.08s clip (~1.5s/shot) with a prompt containing LOCKED ELEMENTS, MOUTH MAP, WHERE HE LOOKS, CLOCK, COVERAGE, CONTINUITY BIBLE.
- ByteDance acknowledges weaknesses: physical plausibility of complex motion; stability when multiple subjects interact. Independent reports: identity/detail drift in long interactions, morphing, shape changes on rotation.

### 7.2 Generation unit rules
1. **Unit = one space-time continuity** (same location, same lighting state, same wardrobe), ≤30s, ending at a natural cut point.
2. **Shots per unit:** default 2–5 shots; max 6 for regular dialogue; ≥3s per generated segment (general convention; shorter shots in the edit are achieved by trimming in post) ("roughly 2–3 seconds per visible action"). Guidance from seedance.tv: 5s clip → 2–3 timestamps; 8–10s → 3–5 timestamps. Exception: the multi-angle workflow from one reference take (Blender previs render or real video) allows ~1.5s shots.
3. **One primary action + one primary camera instruction per segment.** No two simultaneous moves. Separate subject motion and camera motion in time (the character FINISHES standing up, only then does the camera pan).
4. **Camera budget:** if subject action is complex → static camera. If the camera travels → simple subject action.
5. **Hero shots are generated separately** (1-shot or few-shot units) to get many takes and select; connective shots are grouped into units.
6. **Complex multi-person interaction** (wrestling, handing over small objects, hugging) → split shots, prefer cutting around the contact (previous shot the hand offers, insert of the hand receiving) instead of one continuous shot.
7. **Every unit ends with a handle:** add 0.5–1s after the planned cut point (for match on action/L cut). Count handles against the 30s budget.
8. **Action overlap between units:** the last action of unit N is repeated at the start of unit N+1 (match on action), with state recorded explicitly.
9. **Previs-first:** a rough Blender render (clay/layout) of the unit serves as video reference → Seedance R2V preserves camera path, blocking, eyeline. This is the strongest way to prevent camera drift.

### 7.3 Continuity anchors repeated in EVERY unit prompt
- Character identity block (face features, age, hair, detailed wardrobe) — verbatim from the visual-bible.
- Screen position of each character (A camera-left, B camera-right) & the 180° axis.
- Eyeline target ("A looks at B's eyes, slightly right of lens").
- Lighting state (source, direction, kelvin, ratio).
- Prop state.
- Lens/ camera height family.
- Mouth map if there is dialogue (seconds speaking/seconds silent).

### 7.4 Moves: AI handles well vs badly (synthesized, needs testing per model)
**Well:** static locked-off (when prompted explicitly), slow push-in/pull-out, slow pan/tilt, follow tracking of one simple subject, crane reveal of an environment without people, simple rack focus.
**Risky:** orbit/arc around a human face (identity drift, background morph), handheld (fake/uneven shake), whip pan, dolly zoom, crowds, hands manipulating small objects, reading text, multiple people touching, rotating objects (shape changes), fast motion exceeding the duration ("overly fast action"), weightless "floaty glide".
**Fix pattern:** split up, cut around the difficult moment, use inserts to cover, use previs video as motion reference, add negative constraints ("no floaty hover, feet stay planted, no morphing").

### 7.5 Static shot prompt pattern (because the model tends to drift/push-in on its own)
Causes of drift: tight first frame, wording that suggests motion ("dynamic", "immersive", "dramatic reveal"), centered subject without anchors, long static stretches.
Prompt: "Locked eye-level medium-wide shot from one fixed tripod position. Framing, camera height, angle, horizon, focal length and subject scale remain unchanged for the full shot." + "Subject motion only: …" + "No zoom, push-in, pull-back, pan, tilt, orbit, dolly, roll, shake, drift or reframing." First frame has vertical lines on both sides, a level horizon, space around the subject. QC: compare first/last frame at the same size.

### 7.6 Economics
Measure "cost per accepted, continuity-safe second", not cost per generation (Hell Grind: 16,000+ clips → 253 usable shots). Run a 480p test before 1080p. The fewer risky shots in the shot design → the sharper the cost reduction.

---

## 8) Anti-AI shot patterns

| # | Pattern | Why it hurts | Detect (automatic rule on the shotlist) | Fix |
|---|---|---|---|---|
| 1 | **Every shot moves** | Loses anchoring; movement loses meaning; looks like an "AI demo reel" | % of shots with `camera.move != static` > 50% in a drama/dialogue scene | Default to static; keep only moves that pass the motivation test; target ≥40% static for drama |
| 2 | **Constant slow push-in** | Model default; "emphasizing" everything = emphasizing nothing | `push_in` > 25% of shots, or 2 consecutive push-ins | Push-in only on realization/decision beats; otherwise static or pull-out |
| 3 | **Gratuitous orbit** | Drift risk + meaningless | orbit/arc without `motivation.type == emotion_turn` | Replace with static + cut, or a lateral truck past the foreground |
| 4 | **Drone establishing every scene** | Repetitive, emotional distance, stock-footage trope | >1 aerial/EWS establishing per 3 scenes | Open the scene on a detail/insert, sound (J cut), or mid-action; establish late |
| 5 | **All close-ups** | No geography, suffocating, devalues the CU | CU/ECU > 50% of the scene; scene has no WS/MS | Add master/MS; save CU for the turning point |
| 6 | **All wides** | No intimacy, audience can't get into the characters | No shot ≤MCU in a scene with an emotion beat | Place at least 1 CU at the turning point |
| 7 | **Centered symmetry everywhere** | Model tends to center the subject; loses lead room, monotonous | `composition.subject_position == center` > 40% | Thirds, lead room, intentional short-siding; symmetry only for power/ritual |
| 8 | **Slow-motion everything** | Fake "epic", breaks rhythm, loses weight | `speed < 1.0` > 1 shot/scene or >10% of the film | Real-time by default; slo-mo ≤1–2 moments in the whole film, with a subjective reason |
| 9 | **Character looks straight into the lens** | Breaks the world, "stock photo"/advertising feel | `eyeline.target == lens` without `fourth_wall_intent` | Eyeline off-lens toward the partner; state a specific target in the prompt |
| 10 | **Generic "epic" angle** (low angle + backlight + smoke) | Not tied to real status | low angle not tied to a status beat | Angle per the status table (3.2) |
| 11 | **Gratuitous lens flare/bokeh/god rays** | Model's aesthetic default | flare without a `motivated_source` in frame | Remove; flare only when a real light source is in frame and meaningful |
| 12 | **Monotonous shot length** | No rhythm, every shot ~5s | CV(duration) < 0.35 within a scene; > 3 consecutive shots with the same duration ±0.5s | Apply the rhythm curve (4.5) |
| 13 | **Same size in succession** | Jump-cut feel, 30° rule | 2 consecutive shots of the same subject at the same size & angle difference <30° | Change ≥1 size step or ≥30° |
| 14 | **Shallow DOF by default on every shot** | Loses space, "AI portrait look" | Shallow DOF > 70% | Deep focus for staging in depth/wide |
| 15 | **Maxed-out expression** | Over-acting, uncanny | `performance.intensity >= 4` > 1 time/scene | Lower to 2–3, use indirect behavior |
| 16 | **No listener/reaction** | Dialogue is just speakers alternating | Dialogue scene has no shot with `type == reaction` | Add a reaction for the turning point, plan an L cut |
| 17 | **Camera and subject both move complexly** | Causes glide, rubbery motion | move != static AND action.complexity == high | Pick one of the two |
| 18 | **Every scene opens the same way** | Easily recognizable pattern | 3 consecutive scenes with the same opening size/move | Rotate: insert, mid-action, sound-first, wide |

---

## 9) `shotlist.json` schema + example

### 9.1 Conventions
- Time unit: seconds (float). Spatial unit (Blender): meters, Blender axis system (Z up), angles: degrees.
- Lens: mm full-frame equivalent (sensor 36×24).
- ID: `S{scene}` → `S01`, shot `S01_010` (steps of 10 to allow insertion), unit `U01`.
- All enum fields are written in lowercase snake_case.

### 9.2 Schema (JSON Schema draft 2020-12, condensed but with all fields)

> The canonical schema (updated after cross-review: `revision`, `film.gen_ratio`, `fps` = 24, `characters[].height_m/identity_block/costume_block`, `scenes[].location_id/props`, `shots[].duration_s` ≥ 3, `handle_s` default 0, `sfx`, `ambience`, `units[].status`) lives in **`shotlist.schema.json`** in the same folder. The schema is not copied here to avoid divergence.

### 9.3 Example — 6 shots, 2 units (S01: kitchen at night, two sisters, the older sister is about to reveal the house sale)

> The complete 6-shot / 2-unit example, validated by `scripts/validate_shotlist.py`, lives in **`shotlist.example.json`** in the same folder.

Quick check of the example: 6 shots, 2 units (17.5s, 15.5s ≤30s); exactly 1 push-in (motivated emotion_turn); 5/6 static; sizes WS→MCU→MS→ECU→CU→MCU; durations 6.5/3.5/7/3/6/6 (CV ≈0.28 — validator warns; accepted because the scene is short, the faster rhythm is created in post by trimming); axis holds C01 frame-right/C02 frame-left; L cut planned; eyeline not into the lens.

---

## 10) Gate checklist (skill 4 → skill 5)

**Breakdown**
- [ ] Every scene has opening_value ≠ closing_value and one turning_point_beat.
- [ ] Every beat has at least one intention in action-verb form (no emotional adjectives).
- [ ] POV owner & camera_stance declared for every scene.
- [ ] "Silent test": reading the shotlist without dialogue, the story is still understandable.

**Camera language**
- [ ] Every shot with move ≠ static has motivation.type ≠ none_static and a reason that does not contain "cinematic/dynamic/pretty".
- [ ] The turning point has the scene's closest-size shot or a clear change in grammar.
- [ ] No 30° rule violation between consecutive shots of the same subject.
- [ ] Angle reflects status, changes when status changes.

**Continuity**
- [ ] Axis & camera_side for every scene; every axis crossing has axis_break_intent or a neutral/cutaway/move.
- [ ] Screen positions consistent across units of the same scene.
- [ ] Eyeline target declared for shots with characters; no `lens` unless fourth_wall_intent.
- [ ] Prop/wardrobe state recorded in every unit; handoff_in/out match.

**Performance**
- [ ] Every shot with a character: intention + observable_behavior (≥2 cues) + intensity.
- [ ] Intensity ≥4 at most once/scene and only at the turning point.
- [ ] Cues fit the size (no micro-expressions for WS).

**Edit**
- [ ] Every dialogue scene has ≥1 reaction shot; L/J cuts are planned.
- [ ] Hero beats have coverage_alt.
- [ ] CV(duration) ≥0.35 across the whole film; rhythm curve fits the genre.

**AI**
- [ ] Every unit ≤30s (including handles), ≤6 shots, same location/lighting state.
- [ ] Every shot: one action.primary; complexity high ⇒ static camera.
- [ ] ai_risk is flagged; high-risk shots have a plan (covering insert, separate unit, previs ref).
- [ ] Anti-pattern scan (section 8) passes: static ≥40% (drama), push_in ≤25%, center ≤40%, slo-mo ≤10%, CU ≤50%/scene.

**Lighting**
- [ ] Every scene has motivated_source, key_fill_ratio, key_kelvin; lighting_arc matches the story.

---

## 11) Uncertain info (needs verification)

1. **Seedance 2.5 specs** come only from third-party sources (EvoLink, seedance.tv, fal.ai, atoms.dev) — official ByteDance documentation could not be read. 30 images/10 videos/10 audio reference, 4K, and timestamp accuracy need testing.
2. **Maximum shots per unit** (2–6) is a proposal inferred from the guidance "2–3s per action" and "3–5 timestamps for 8–10s"; the fal.ai example of 13 shots/20s applies only to the multi-angle workflow from a camera-locked reference take. Needs real benchmarking.
3. **The camera-move AI reliability table** is synthesized from general prompting guides (creatide, pippit) + ByteDance's self-reported weaknesses, not a quantitative Seedance 2.5 benchmark. The 40-camera-move test (gigwise) could not be fetched.
4. **ASL by platform/genre** in the 4.5 table is heuristic; the only hard data are Bordwell (2–4s contemporary) and Cutting et al. (act structure). No Cinemetrics data for short film/AI film.
5. **30° rule "20mm"**: figure from Wikipedia, not an industry standard; in practice one usually changes one size step.
6. **FACS codes AU43/AU54/AU64** (eyes closed/head down/eyes down) are from memory of the FACS head/eye codes, not checked against an opened page; mapping AU intensities A–E to 1–5 is an internal convention.
7. **Blue moonlight** is a film convention; the golden hour Kelvin in the source (~3200K) is approximate, in reality it varies 2500–3500K.
8. **Mackendrick, Katz, Weston, Hooks, Murch** were mostly read through summaries/excerpts (sobrief, thestickingplace, substack, actioncutprint PDF of Weston's magazine article, mikebattle notes), not the full books.
9. **Every Frame a Painting** (Kurosawa "composing movement") — the opened page had no content; not used as a basis.

---

## 12) Sources (only URLs that were opened and had content)

1. Seedance.tv — Seedance 2.5 Timestamp Prompts: https://www.seedance.tv/blog/seedance-2-5-timestamp-prompts
2. fal.ai — How To Create a Multi-Angle Video With Seedance 2.5: https://fal.ai/learn/tools/how-to-create-multi-angle-video-seedance-2-5
3. EvoLink — Seedance 2.5 vs 2.0 Migration Guide: https://evolink.ai/blog/seedance-2-5-vs-seedance-2-0
4. Atoms.dev — Seedance 2.5 Review: https://atoms.dev/blog/seedance-2-5-review-30-second-ai-video-production-workflow
5. David Bordwell — Intensified continuity revisited: https://www.davidbordwell.net/blog/2007/05/27/intensified-continuity-revisited/
6. Cutting, DeLong, Brunick — How Act Structure Sculpts Shot Lengths (Projections 2011): https://filmoterapia.pl/wp-content/uploads/2015/07/How-Act-Structure-Sculpts-Shot-Lengths-and-Shot-Transitions-in-Hollywood-Film.pdf
7. StudioBinder — Ultimate Guide to Camera Shots: https://www.studiobinder.com/blog/ultimate-guide-to-camera-shots/
8. StudioBinder — 180 Degree Rule: https://www.studiobinder.com/blog/what-is-the-180-degree-rule/
9. StudioBinder — Continuity Editing: https://www.studiobinder.com/blog/what-is-continuity-editing-in-film/
10. StudioBinder — L Cut / J Cut: https://www.studiobinder.com/blog/what-is-an-l-cut-in-film/
11. StudioBinder — Focal Length Explained: https://www.studiobinder.com/blog/focal-length-camera-lenses-explained/
12. StudioBinder — Key Light: https://www.studiobinder.com/blog/what-is-key-light-definition/
13. StudioBinder — Blocking and Staging (Spielberg, Kubrick, Iñárritu): https://www.studiobinder.com/blog/blocking-and-staging-scenes/
14. Wikipedia — 30-degree rule: https://en.wikipedia.org/wiki/30-degree_rule
15. Wikipedia — Low-key lighting: https://en.wikipedia.org/wiki/Low-key_lighting
16. Wikipedia — Facial Action Coding System: https://en.wikipedia.org/wiki/Facial_Action_Coding_System
17. Paul Ekman Group — Micro Expressions: https://www.paulekman.com/resources/micro-expressions/
18. No Film School — Walter Murch's Rule of Six: https://nofilmschool.com/editing-emotion-using-walter-murchs-rule-six-non-narrative-content
19. Mike Battle — In the Blink of an Eye notes: https://www.mikebattle.com/book-notes/in-the-blink-of-an-eye
20. Judith Weston — Directing the Actor (MovieMaker reprint): https://actioncutprint.com/files/DirectingActor-JudithWeston.pdf
21. Peter D. Marshall — Notes on Directing Actors: https://filmdirectingcoach.substack.com/p/take-3-my-notes-on-directing-actors-77d
22. Screenplayology — The Director and the Screenplay: https://www.screenplayology.com/content-sections/screenplay-style-use/1-3/
23. SoBrief — Film Directing Shot by Shot (Steven Katz) summary: https://sobrief.com/books/film-directing-shot-by-shot
24. The Sticking Place — Alexander Mackendrick: https://thestickingplace.com/alexander-mackendrick/
25. Adam Weaver — Ed Hooks' 7 Acting Principles: http://adweaver.blogspot.com/2012/12/7-acting-principle-ed-hooks.html
26. Acting Coach Scotland — Principles of Acting for Animators and Actors: https://www.actingcoachscotland.co.uk/blog/principles-acting-animators-and-actors
27. American Cinematographer — Lighting a Set with Stephen H. Burum, ASC: https://theasc.com/article/lighting-a-set/
28. American Cinematographer — Shot Craft: The Talking Head: https://theasc.com/article/shot-craft-the-talking-head-shooting-interviews/
29. GVM — Color Temperature for Video: https://gvmled.com/color-temperature-video-filmmaking-guide/
30. Creatide — Why AI Video Motion Looks Unnatural: https://creatide.ai/blog/why-ai-video-motion-looks-unnatural-and-how-to-fix-it
31. Pippit — Stop Unwanted Camera Movement in AI Video: https://www.pippit.ai/blog/stop-unwanted-camera-movement-ai-video
