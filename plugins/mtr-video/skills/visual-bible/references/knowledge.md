# 03 — Visual Bible / Visual Development & Reference Assets

> **Model-agnostic note (v0.3.0):** this research was compiled with Seedance 2.5 as the reference video model. Every Seedance-specific number here (call length, ≤30 s units, ≥3 s shots, reference counts, 24 fps, 720p, 32 kHz audio, @Image tags, prices, policy) is an example from the `seedance-2.5` profile, not a pipeline rule. Read the real limits from the active profile (`video-generation/references/models/<id>/profile.json`) and apply `film-pipeline/references/shared-conventions.md`. Where this file says "skill 6", read `video-generation`; references like "06 §N" point to `video-generation/references/models/seedance-2.5/knowledge.md`.

> Knowledge file for Skill 3 (`visual-bible`). Goal: turn concept + story (Skills 1–2) into a **hard-locked set of visual rules** + **a clean set of reference assets** that Skills 4 (shot-design), 5 (blender-previs), 6 (video-generation) and 7 (dailies-review) can reuse without guessing. Research date: 2026-10-02.

---

## 1. Core principles

1. **The bible is law, not mood.** A mood board inspires; a bible *commands*. Every entry must have a checkable value (hex, lens name, frame ratio, fixed descriptor sentence, file ID). If Skill 7 cannot use an entry to judge "on-model / off-model", that entry is not specific enough. In animation studios, the model sheet exists precisely to define "on-model" for hundreds of artists working simultaneously (wherecreativityworks) — here the "artists" are the individual Seedance generations.
2. **Start from the character.** Ralph Eggleston (Pixar production designer, who introduced the color script on Toy Story): *"Start from the character and then everything else will follow."* Color, shape, set and light all serve the character's emotion in each beat — not "to look pretty".
3. **Color is a piece of music over time (color script).** A color script "is an illustration of the story and at the same time an illustration of the characters' emotions throughout the story" (Eggleston, vfxscience). The palette changes per act/beat; a color is "withheld" for the payoff moment (WALL·E: green = hope, hidden until the plant appears).
4. **Shape language + silhouette test.** Round = friendly/safe, square = stable/stubborn, triangle = dangerous/dynamic (cg-wire). A character must be recognizable from the black silhouette alone. Square WALL·E vs round EVE = will vs programming.
5. **Costume is biography.** The breakdown artist imagines the character's entire life and "the traces events leave on the clothes"; the standard instruction is "take the newness off" — never look "off-the-rack" (drainmag). For AI, this is also weapon no. 1 against the "AI look".
6. **One source of truth per attribute.** Each reference holds only ONE role (identity, outfit, style, lighting, location, motion, voice). Conflicting references = averaged, washed-out, drifting output (xmk, clipdance, magichour).
7. **Few and clean > many and messy.** "Three excellent character angles are more useful than twelve mediocre ones" (mindstudio); "using all 12 slots often gives worse results because the model tries to satisfy too many constraints" (vicsee). Seedance 2.5 allows 30 images/10 videos/10 audio — that is a ceiling, not a target.
8. **Frozen vocabulary.** Copy the fixed descriptor block verbatim between prompts; "swapping synonyms changes reference weighting and drift accumulates" (xmk). Not "brunette" one time and "dark brown hair" another (sagnik).
9. **Imperfection is intentional.** The model's default is smooth skin, flattering light, symmetry, brand-new. The bible must *actively* specify wear, dirt, asymmetry, motivated light.
10. **Keep structure and identity separate.** Blender clay/blockout locks *structure* (staging, scale, camera, depth), not *identity* (mixar). Identity comes from character refs; look comes from style frames.

---

## 2. Process (Skill 3 workflow)

**Input:** concept one-pager (Skill 1), script/beat sheet (Skill 2), duration, intended platform/aspect ratio.
**Output:** `02_bible/bible.md` + folder `02_bible/refs/` + `02_bible/descriptors.yaml` (fixed text blocks for Skill 6 to paste).

| Step | Task | Deliverable | Suggested time (short ≤ 3 min) |
|---|---|---|---|
| 0 | **Look statement**: 3 sentences — how this film *looks*, how it *feels*, what it must *not* resemble | `look_statement` | 15' |
| 1 | **Mood board / look book** (real films, real photos, paintings as reference) → extract rules, do not copy | 12–24 reference images + caption "what to take from this image" | 1h |
| 2 | **Format & camera rules**: aspect ratio, lens package, camera movement grammar, film stock/grain | Lens/Format section | 20' |
| 3 | **Color script**: 1 color frame/beat (5–12 frames for a short), hex palette per act | `color_script.png` + hex table | 1h |
| 4 | **Character bible**: shape language, costume (with wear), turnaround, expressions, scale lineup | `refs/char/<ID>/…` | 1–3h/character |
| 5 | **Location/set bible**: plan, key angles, lighting key, time-of-day, set dressing & wear | `refs/loc/<ID>/…` | 1h/location |
| 6 | **Prop sheets**: hero props, multiple views, scale, wear | `refs/prop/<ID>/…` | 20'/prop |
| 7 | **Style frames**: 3–6 "final look" frames (character in location under the correct lighting key) | `refs/style/SF_xx` | 1h |
| 8 | **Voice bible**: voice casting, clean samples, speech manner | `refs/voice/<ID>/…` | 30'/character |
| 9 | **Consistency test**: run 1 short Seedance clip (5–8s) per main character with the ref pack → score drift | `tests/` + notes | 1h |
| 10 | **Gate** (section 7) → handoff to Skill 4 | signed checklist | — |

Process notes:
- Mood board → **extract rules**: for each reference image write 1 line "Take: hard top light, sodium-vapor orange; Ignore: composition, people". This is also the role-assignment discipline when feeding images to the model (xmk: "Use Image 2 only for lighting. Do not copy background, objects, people, composition").
- A traditional lookbook (nofilmschool, moviemaker) contains: logline, synopsis, character, cinematography approach, color palette, locations, VFX, editing style, music. Our bible keeps those sections but converts them into *spec* form.
- Deakins does not make look books for himself; he prioritizes **staging sketches + lighting diagrams** (rogerdeakins forum). → Our bible must have a **lighting key diagram** for each scene, not just pretty images. A short "sizzle reel" of reference footage + music is also a useful tool to lock the mood (1–2 clips can be supplied as style video refs — take only the look, not the content).
- Eggleston on Incredibles 2, when short on time: roughly blocked "color themes and ideas", painted a few scenes, then worked directly with the DP. → For a short, the color script may be only 5–8 frames, but it must NOT be skipped.

---

## 3. Bible document template (with filled-in example)

Running example: 2'30" short **"The Radio Repair Shop" ("Tiệm sửa radio")** — a rainy night in Hà Nội, 1994; old Mr. Tư (68) repairs a radio for little Linh (9), who is waiting for news of her fisherman father at sea; the radio picks up a signal at the end of the film.

### 3.0 Header & Look statement
```markdown
# VISUAL BIBLE — TIEM_SUA_RADIO — v1.2 (2026-10-02)
project_code: TSR
runtime: 150s | delivery: 2.39:1 letterbox inside 16:9 (gen 16:9, crop in post) | 24 fps
look_statement:
  - Looks like: 35mm tungsten night film, yellow desk-lamp light in a cramped room, cold blue rain outside.
  - Feels like: warm but weary, patient, a small hope.
  - Does NOT resemble: glossy nostalgia commercial, Hollywood teal-orange, "cinematic 8k".
references_films: "In the Mood for Love" (cramped framing, controlled saturated color), "The Scent of Green Papaya" ("Mùi đu đủ xanh") (slow pacing, wood textures)
```

### 3.1 Style & rendering rules
```yaml
medium: photoreal live-action look   # or: stylized 3D / 2D painterly — pick ONE
style_block (paste verbatim into every prompt): >
  35mm film look, Kodak Vision3 500T, visible fine organic grain, gentle halation
  around practical lights, soft highlight roll-off, natural skin texture with pores,
  motivated practical lighting, muted color with warm tungsten accents.
negative_block: >
  no glossy skin, no beauty retouching, no HDR, no lens flare unless motivated,
  no teal-and-orange grade, no oversaturation, no centered symmetrical hero pose.
texture_rules: every surface shows use — wood worn at the edges, damp-stained walls, glass with fingerprints/dust.
```

### 3.2 Color script & palette
| Beat | Timing | Emotion | Key color | Accent | Value/contrast | Main hex |
|---|---|---|---|---|---|---|
| B1 Opening | 0–25s | lonely, cold | rain-blue street outside | distant desk-lamp yellow | low-key, high contrast | #22313A #3E5560 #C98A3A |
| B2 Meeting | 25–60s | shy | tungsten yellow | blue through the door | mid-key | #C98A3A #6B4A2E #2C3B40 |
| B3 Repair | 60–110s | patient, bonding | warm amber | red radio LED | warm, soft contrast | #B8732E #8C2F24 #3A2A1E |
| B4 Disappointment | 110–130s | deflated | grey-blue creeping in | — | desaturate 30% | #4A555A #6E6A60 |
| B5 Signal | 130–150s | hope | warm yellow + **green** (withheld until here: the radio tuning light) | — | brightest in the film | #D9A54A #6FA36B |

Rule: the **complementary** cold-blue/warm-yellow scheme = inside-vs-outside conflict (studiobinder: complementary = "high-contrast tension… conflict"); green is an **associative/withheld color** that appears only in B5 (learned from WALL·E). No more than 3 dominant hues per frame.

### 3.3 Lens / format rules
```yaml
aspect_ratio: 2.39:1 (protect 2.39 inside the 16:9 gen frame)   # reason: cramped room + the gap between grandfather and child
lens_package: spherical primes 32mm (wide in the room), 50mm (coverage), 85mm (CU of hands/radio). NOTHING below 24mm, NO zoom.
camera_grammar: mostly static/tripod & slow push-in; light handheld only in B4. No drone, no orbit.
depth_of_field: moderately shallow (T2–T2.8 look), background shapes still readable.
framing: off-center, rule-of-thirds, use door frames/shelves as frame-in-frame; tight headroom in CU.
frame_rate: 24fps, natural motion blur (180° shutter look).
```
Rationale: 2.39 is good for balancing multiple characters and placing characters at the two edges of the frame to express their relationship, but hard for facial close-ups (use a "haircut" crop); 1.85/1.66 are the "go-to formats for character drama"; 1.33/1.37 force a single main piece of information, intimate to the point of claustrophobia (shutterangle). Choose the ratio by the *spatial relationships of the story*, then lock it.

### 3.4 Character bible (one entry per character)
```yaml
id: C01_ONG_TU
role: protagonist
essence: "Patient, taciturn, his hands better than his words."
shape_language: square-round (round sloping shoulders, square jaw) → trustworthy, soft
silhouette_hooks: [tortoiseshell reading glasses low on the nose, singlet + wide-shouldered khaki jacket, slightly hunched back]
identity_block (paste verbatim): >
  Vietnamese man, 68, lean, slightly hunched, short grey crew-cut thinning at crown,
  deep forehead lines, sun-spotted skin, tortoiseshell reading glasses low on nose,
  small mole under left eye.
costume_block: >
  faded olive-khaki work jacket (#6B6A4A) with frayed cuffs and a solder burn on right
  sleeve, off-white cotton undershirt yellowed at collar, dark grey trousers (#3A3A3A),
  worn plastic sandals.
wear_and_story: right sleeve has a solder burn; right index finger has a callus + nicotine stain.
palette: muted olive/khaki — NEVER wears saturated colors.
expressions_needed: neutral, focused (squinting), slight smile at the eye corners, tired, mildly surprised
scale: 1.63 m — see lineup with C02 (1.30 m)
refs: refs/char/C01/ (see section 4)
voice: refs/voice/C01/
continuity: glasses always on the face except shot B3-07; jacket taken off from B3 onward.
forbidden: no beard, no wristwatch, no clean new shirt.
```

### 3.5 Location / set bible
```yaml
id: LOC01_TIEM_RADIO_INT_NIGHT
description: 3x4m room, Old Quarter shopfront, iron folding gate half drawn, wooden shelves full of old radios.
layout: plan view refs/loc/LOC01/LOC01_plan.png (workbench on the left, door on the right, camera mostly from the inner corner)
key_angles: LOC01_A (wide from the inner corner toward the door), LOC01_B (reverse toward the workbench), LOC01_C (top-down on the workbench)
lighting_key:
  key: tungsten desk-lamp bulb 2700K, from upper left, hard, narrow
  fill: almost none — bounce from the wooden tabletop
  ambient: cold blue 6500K light + sodium streetlight through the door, rain-wet
  practicals: red radio LED, green tuning light (B5 ONLY)
  ratio: key:fill ≈ 8:1, low-key
set_dressing: electronic components, copper wire spools, 1994 tear-off calendar, chipped teapot; yellow lime-wash walls with damp stains.
wear: peeling paint at the base of the walls, dust on the high shelves, rainwater streaks at the door.
blender_previs: LOC01.blend (Skill 5) — real scale, door height 2.1m.
```

### 3.6 Prop sheet
```yaml
id: PR01_RADIO_NATIONAL
hero: true
description: two-band National transistor radio, brown leather case worn at the edges, metal grille dented at the top-right corner, red tuning needle.
views: front, back (battery cover open), 3/4, top; close-up of the dial
scale: 24x15x7 cm — fits in the little girl's two hands
states: S1 broken (cover open, wires exposed), S2 repaired, S3 switched on (green tuning light)
```
(Note: if using a real brand name for a prop, consider the logo — a fictional name may be used to avoid incorrectly rendered logos.)

### 3.7 Sound / voice bible
```yaml
C01_ONG_TU:
  voice: Northern Vietnamese male, deep, slightly hoarse, slow, short clipped phrases
  source: recording of a real actor's voice (preferred) | TTS clone (state tool + consent explicitly)
  files: refs/voice/C01/C01_voice_neutral_v01.wav (10–15s), C01_voice_soft_v01.wav
room_tone: rain on a corrugated iron roof, ceiling fan, radio static (refs/sfx/)
music_rule: no background music B1–B3; one soft đàn bầu (monochord) motif in B5.
```

---

## 4. Reference image specs for AI consistency

### 4.1 Engine limits (for budgeting refs)
- **Seedance 2.5** (released 2026-07-31): up to **30 images + 10 videos + 10 audio = 50 inputs**, 4–30s clips per pass, extendable; each ref can be assigned a role (identity, product, palette, camera style, voice); lip-sync from dialogue in double quotes (imaginetovideo, apiframe).
- Seedance 2.0 (for comparison; many guides are still written for this version): 9 images, 3 videos (≤15s total), 3 audio (≤15s total, each file 2–15s, MP3/WAV <15MB), tags `@Image1…@Image9`, `@Video1`, `@Audio1`; audio must accompany a visual ref (vicsee, magichour).
- Seedream (for generating image refs): 4.5 supports up to 14 refs; the 5.0 Pro guide recommends ≤10 refs, "the fewest needed to convey the request" (evolink, xmk).

### 4.2 Standard ref set for EACH main character ("Character Ref Pack")
| # | File | Content | Framing | Notes |
|---|---|---|---|---|
| 1 | `C01_id_front_v01.png` | Front-facing face, neutral expression | head & shoulders | "primary facial identity reference" |
| 2 | `C01_id_34L_v01.png` | 3/4 left | head & shoulders | 3/4 is usually the strongest image — carries both face and proportions (sagnik, clipdance) |
| 3 | `C01_id_profileL_v01.png` | profile | head & shoulders | for side/orbit shots |
| 4 | `C01_turn_full_v01.png` | full-body turnaround front/3-4/side/back on 1 sheet or 4 separate files | full body | outfit + proportions; back view when there are shots from behind |
| 5 | `C01_outfit_v01.png` | costume worn on the body, close-up of material & wear | waist-up/full | "wardrobe slips first" → needs its own ref (xmk) |
| 6 | `C01_expr_sheet_v01.png` | 4–6 required expressions | head | include only when the shot needs that expression |
| 7 | `C01_scale_lineup_v01.png` | standing next to C02 + a reference object (2.1m door) | full | prevents height errors between clips |

**Each generation sends only 2–4 images from the pack** (front or 3/4 + full-body outfit + 1 image matching the shot's angle). Recommended total refs/shot: 3–5 images + 1–2 videos (clipdance, vicsee), even though the ceiling is 30/10/10.

### 4.3 Ref shooting/render spec
- **Lighting:** neutral, soft, even (overcast/large softbox), **same light direction across the whole pack**; no colored rim, no gels. "Storytelling" light lives in the style frames, not in identity refs (clipdance: inconsistent lighting between refs causes mismatch).
- **Background:** plain, neutral grey (~#808080) or grey-white; no props, no other people. Multiple people in an image without prioritization = "two faces blend" (xmk).
- **Expression:** neutral for identity; other expressions go in the expression sheet.
- **Outfit:** **exactly one** costume (the film's main outfit) across every pack image; a second outfit = a separate pack `C01_outfitB_*`.
- **Resolution:** minimum 1080p on the short side, 2K preferred; PNG or high-quality JPEG, avoid WebP/AVIF, avoid compression artifacts (clipdance, seedanceai.cc "export the highest-resolution reference you have").
- **Framing:** identity = head & shoulders with a clear face; at least one waist-up/full-body image (clipdance: "waist-up minimum").
- **Style match:** refs must share the film's *medium* — do not mix photoreal headshots with an anime mood board (clipdance).
- **No text, no watermark, no UI, no borders** on ref images.
- **Already "dirtied":** refs already have real skin and costume wear — the model will not add them on its own. If the ref is smooth, the video will be even smoother.

### 4.4 Avoiding ref conflicts
- One image = one role; state the role in the prompt: "Identity from @Image1. Outfit from @Image2. Lighting only from @Image3 — do not copy people or furniture" (vicsee, magichour, xmk).
- If two images show two different versions of the same character → **drop one** or state explicitly which image is authoritative (magichour).
- Re-anchor with the **original ref**, not with a generated frame (seedanceai.cc) — generated frames carry accumulated drift. Intentional exception: use the last frame to chain continuity between clips (vicsee), but the identity ref is still the original image.
- Style ref: use 3–5 small swatches (vicsee) or 1–2 style frames; state explicitly which attributes to take ("muted earth-tone palette, soft film grain, diffused highlights") — "do not copy the subject" alone is not enough (xmk).
- Reference strength (if the UI exposes it): ~70–80%; >85% rigid, <60% drifts (seedanceai.cc — third-party source, needs testing).

### 4.5 How to create image refs in 2026
1. **Seedream 5.0 Pro/Lite or 4.5** (same ByteDance family — close to Seedance's "visual language"): first create 1 standard front identity image, then use that very image as the ref to generate 3/4, profile, full-body, outfit ("Use Image 1 as the only identity reference. Preserve face shape, eyes, nose, mouth, skin tone, age, mole under left eye. Neutral grey seamless background, soft even studio light, neutral expression"). Seedream prompt formula: role of each image → what to preserve → scene → match lighting → "do not copy/change" → aspect ratio (xmk). State the resolution explicitly as "2K"/"4K", do not write "high resolution" (evolink). One style/medium per generation.
2. **Blender render** (Skill 5): for props/sets where geometry matters and for the **scale lineup** — render clay or simple lookdev; clay "is the most useful pass" for locking forms (mixar). Clay locks only structure, not the face.
3. **Real photographs** (real actors/props, with consent): strongest for realism; shoot to the 4.3 spec.
4. After creation: **review at full size** face, hands, text, logos (xmk); fix one error at a time, do not rewrite the whole prompt.
5. **Lock the version**: approved ref → `_v01` locked; any change → `_v02` and record a changelog in the bible.

### 4.6 Location, prop, lighting, motion refs
- Location: 1 wide establishing + 1–2 key angles empty of people, correct time-of-day, + plan view. "Use @Image4 for the room's layout and lighting" (magichour).
- Hero prop: front + 3/4 + detail; record dimensions; "preserve exact silhouette, dimensions, controls, logo placement" (xmk).
- Camera/motion: 3–5s greybox clip from Blender, correct aspect ratio, grey geometry, grey figures; **remove grid, outlines, UI, frame counter** because they will be rendered as objects (cozyclay). Seedance "matches what it sees; it does not read a camera description out of it".

### 4.7 Voice reference
- Seedance: audio refs must accompany visual refs; in 2.0 each file is 2–15s (magichour); 2.5 allows up to 10 audio clips. Recommendation: **8–15s/clip, 1 speaker, dry (no reverb), no background music**, same microphone & room for every clip of a character, correct language/regional accent.
- If cloning via TTS (e.g. ElevenLabs Instant Voice Clone) to get clean dialogue and then cutting it into refs: 1–2 minutes of clean audio total, no more than 3 minutes; level −23 to −18 dB RMS, true peak −3 dB; MP3 ≥192 kbps; keep pace/intonation/accent consistent because the model copies both performance style and breathing (elevenlabs docs).
- Always record the voice source + consent in the bible; do not clone a real person's voice without permission.

---

## 5. Style vocabulary bank (grounded descriptors)

Use as a "menu" — pick and **lock** one combination for the whole film, write it into `style_block`.

**Film stock / sensor**
- `Kodak Vision3 500T`: tungsten ~3200K, rich amber practicals, grain "present and organic", more visible in the shadows; use for night, tungsten-lit interiors, mixed lighting (holygrain).
- `Kodak Vision3 250D`: daylight ~5500K, fine clean grain, clean color separation; daytime exteriors, architecture (holygrain).
- Others: `Kodak Portra 400 (stills look)`, `Fuji Eterna (muted, cool greens)`, `16mm reversal`, `Super 8 home movie`, `digital Alexa-like clean, low contrast` — *noted as not yet tested for effectiveness in Seedance; treat as aesthetic descriptors*.
- Texture: `fine organic film grain`, `gentle halation around highlights`, `soft highlight roll-off`, `slight gate weave` (only when stylized), `mild lens vignetting`, `subtle chromatic aberration at frame edges`.

**Lighting (always motivated)**
- `motivated practical lighting from a desk lamp`, `single hard key from camera left`, `low-key, 8:1 contrast`, `soft overcast daylight` (sagnik uses it as a "lighting lock"), `north-window soft light`, `sodium-vapor streetlight spill`, `fluorescent tube overhead, slightly green`, `candle/oil-lamp flicker`, `blue hour ambient`, `practical-only lighting`, `negative fill, deep shadows`, `bounce from warm wooden table`.

**Palette / grade**
- `muted palette with warm tungsten accents`, `desaturated earth tones`, `analogous warm ochres and browns`, `complementary cold blue exterior vs warm amber interior`, `monochromatic green cast` (Matrix-style, meaning "sick/artificial"), `limited palette of three hues`, `lifted blacks, low contrast` or `rich deep blacks` — pick one.
- Include **hex** in the bible; in prompts use precise color names ("charcoal grey jacket", not "dark jacket") (sagnik).

**Camera/lens (match the lens package)**
- `35mm spherical lens, eye-level`, `50mm, shallow depth of field, background readable`, `85mm close-up`, `static tripod shot`, `slow push-in`, `locked-off wide`, `handheld, subtle breathing movement`, `off-center composition, subject on left third`, `frame within a frame (doorway)`.

**Surfaces / realism**
- `natural skin texture with visible pores, fine wrinkles, uneven skin tone, stray hairs`, `natural facial asymmetry`, `worn fabric, frayed cuffs, faded color`, `scuffed, dusty surfaces, fingerprints on glass`, `lived-in set dressing`.

**How to write prompts (recommendation for Skill 6)**: subject identity → scene → action beats → camera → consistency constraints (vicsee five-part); fixed block copied verbatim, variable block changed per shot (xmk). The Seedream guide recommends positive description instead of negation (evolink); xmk finds negatives should only be reinforcement. → Keep `negative_block` short; all primary anti-AI-look measures must live in **positive descriptors + refs**.

---

## 6. Anti-AI visual patterns

| Pattern | Why it happens | Detect (Skill 7 checks) | Fix (descriptor / reference strategy) |
|---|---|---|---|
| **Plastic / waxy skin** | Training data has many retouched images; video prioritizes inter-frame stability, so it smooths chaotic detail such as pores (upsampler, ourcodeworld) | Zoom 200% on cheeks/forehead: no pores, uniform waxy highlights | Identity ref must have real skin; descriptor `visible pores, fine wrinkles, uneven skin tone, sun spots`; hard/side light to reveal texture; post: restoration/upscale that adds texture, *not* blur |
| **Over-smooth face, too symmetrical** | Model pulls toward a symmetrical "average face" (upsampler) | Flip the frame horizontally — face looks almost identical | Asymmetric features in identity_block (mole on the left, uneven eyebrows); `natural facial asymmetry` |
| **Same-face syndrome** (all characters look alike) | No separate refs; multiple faces in one ref image; model "face averaging" (vicsee) | Place characters side by side: same nose, same chin | One separate pack per character, 1 image = 1 person; write "Image 1 is the only identity reference. Do not blend faces" (xmk); design clearly different shape language (round vs square vs triangle); clearly different age, build, skin tone |
| **HDR glow / bloom everywhere** | Default "pretty" aesthetic, stock-photo tonemapping | Lifted shadows, halos around every edge | `low-key`, `deep shadows`, `negative fill`; allow halation only around practicals; negative `no HDR, no bloom` |
| **Teal-orange everywhere** | Blockbuster grades dominate the data; "cinematic" ≈ teal-orange | Vectorscope/histogram: cyan shadows + orange skin in every shot | Own hex palette per color script; specific palette descriptors; style frames with clearly different color; drop the word "cinematic" |
| **Everything golden hour** | The most common "pretty" photo; vague prompts about time | Every exterior has slanted golden sun + flare | Specify time-of-day + concrete light source per scene (lighting key); use `overcast`, `noon flat light`, `blue hour`, `fluorescent` per the story |
| **Symmetric centered hero framing** | Model defaults to balanced composition (upsampler "symmetry overload") | Subject dead center, looking straight at camera, low-angle "hero" | Camera grammar in the bible: off-center, thirds, frame-in-frame; use a Blender greybox clip to lock composition (cozyclay) |
| **Generic "cinematic 8k" look** | Empty keywords pull toward the dataset average | Looks like a stock trailer / commercial | Ban the words `cinematic, 8k, ultra-detailed, masterpiece` in prompts; replace with specific stock/lens/lighting |
| **Over-saturated** | Saturated social-media images; model amplifies | Orange-red skin, neon green | `muted`, `desaturated earth tones`, limit to 3 hues; style refs already graded correctly |
| **Overdesigned costume** | Model adds "fantasy" details (straps, buckles, armor) | Costume nobody could wear day-to-day, too many accessories | Short, specific, everyday costume_block; "forbidden" list; separate outfit ref |
| **No wear/dirt/imperfection** (everything brand-new) | Clean product/stock images; model does not know the backstory | No scratches, dust, fabric creases | "Take the newness off" (drainmag): write wear_and_story for every costume/prop/set; descriptor `worn, faded, scuffed, dusty`; aged refs |
| **Uncanny eyes** (staring, misplaced catchlights, eyes not converging) | Inconsistent lighting, contradictory eye reflections (upsampler) | Catchlight does not match the light source; eyes look in two directions; no blinking | One clear key source → correct catchlight; sharp eye refs; actions with an eyeline target ("looks down at the radio"); keep motion simple in shots showing the face (sagnik) |
| **Background incoherent / impossible space** | Model creates "plausible-looking but impossible spaces" (upsampler) | Doors leading nowhere, curved shelves | Location ref + plan; Blender blockout at real scale (mixar) |
| **Repeating patterns / crowd clones** | Copy-pasted instances (upsampler) | Repeated crowds/shelves of goods | Reduce crowds; describe diversity; build set dressing in Blender |
| **Gibberish text/signage** | Text rendering limits (framestrategy, upsampler) | Warped, unreadable text | Avoid text in frame, or put short text in double quotes (3–5 words) when creating refs with Seedream; add text in post |
| **Wardrobe/prop drift between clips** | Identity holds better than costume; "wardrobe instructions slip first" (xmk) | Compare outfit against `C01_outfit` | Separate outfit ref on every gen; precise color names + hex; same costume_block verbatim |

---

## 7. Gate checklist (before moving on to Skill 4)

**General rules**
- [ ] 3-sentence look statement includes a "Does NOT resemble…" sentence.
- [ ] ONE medium chosen (photoreal / stylized 3D / 2D) — no mixing.
- [ ] `style_block` + `negative_block` written, ≤ 60 words per block, containing no "cinematic/8k/masterpiece".
- [ ] Aspect ratio, lens package, camera grammar, fps locked + storytelling rationale.

**Color**
- [ ] Color script: 1 frame/beat (≥5 frames for a short), each frame with emotion + hex.
- [ ] At least one associative/withheld color tied to a meaning.
- [ ] No default teal-orange unless a reason is stated explicitly.

**Characters** (each main character)
- [ ] identity_block + costume_block verbatim, with ≥2 asymmetric/identifying features.
- [ ] Silhouette test passes (black silhouette distinguishable from other characters).
- [ ] Ref pack: front, 3/4, profile, full-body outfit (+ back if needed) — same lighting, plain background, 1 outfit, ≥1080p, no text.
- [ ] Expression sheet for the expressions actually present in the script.
- [ ] Scale lineup.
- [ ] Wear & story for the costume.
- [ ] Consistency test clip run; drift recorded; refs adjusted if needed.

**Location / Prop**
- [ ] Each location: plan, 1–3 key angles, lighting key (key/fill/ambient/practicals/ratio), time-of-day, wear.
- [ ] Hero prop: ≥3 views, dimensions, states.
- [ ] Locations/props where geometry matters → Blender asset created or planned for Skill 5.

**Sound**
- [ ] Clean voice ref for each speaking character (8–15s, dry, 1 speaker), consent recorded explicitly.
- [ ] Room tone/ambience per location.

**Records**
- [ ] All files follow the naming convention; approved refs have a `_vNN` lock + changelog.
- [ ] `descriptors.yaml` exported for Skill 6; `ref_manifest.csv` (file → role → character/location → which beats it is used for).
- [ ] No ref impersonates a real person/real brand without rights.

### File / naming convention
```
<PROJECT>/02_bible/   (per contract shared-conventions §2)
  bible.md                       # this document
  descriptors.yaml         # style_block, negative_block, identity/costume blocks
  ref_manifest.csv         # file,role,entity,beats,version,status
  color_script.png
  refs/char/C01/C01_id_front_v01.png
  refs/char/C01/C01_id_34L_v01.png
  refs/char/C01/C01_turn_full_v01.png
  refs/char/C01/C01_outfitA_v01.png
  refs/char/C01/C01_expr_sheet_v01.png
  refs/loc/LOC01/LOC01_A_wide_night_v01.png
  refs/loc/LOC01/LOC01_plan_v01.png
  refs/prop/PR01/PR01_front_S1_v01.png
  refs/style/SF01_B3_desk_v01.png
  refs/voice/C01/C01_voice_neutral_v01.wav
  refs/motion/S01_010_greybox_v01.mp4  # canonical copy lives in 04_previs/    # from Skill 5
  tests/C01_consistency_t01.mp4
```
ID convention: character `C01`, location `LOC01`, prop `PR01` (matches the `shotlist.json` pattern `^C[0-9]{2}$`). File convention: `<ENTITY>_<view|role>_<variant>_v<NN>.<ext>`; no diacritics, no spaces; character/location/prop IDs are shared across Skills 4–8 (the shot list references by ID, not by name).

---

## 8. Uncertain info (needs verification / real-world testing)

1. **Seedance 2.5 output resolution**: apiframe and imaginetovideo state only 480p/720p via API (the 4K advertised before launch is not available); morphic/mindstudio state 1080p/4K. → Skill 6 must check the actual tier of the platform in use; refs should be ≥1080p regardless.
2. **Clay render reference**: the prompt brief says Seedance 2.5 supports clay render refs; the "official" documentation summarized by apiframe/imaginetovideo does not mention 3D/clay input, only "white-model blocking". Community practice (cozyclay, mixar) shows greybox clips used as video refs work. → Treat as ordinary video/image refs.
3. **One or many face images?** vicsee recommends 1 face image to avoid "face averaging"; mindstudio/sagnik/clipdance recommend multiple angles (front, 3/4, side). Reconciling hypothesis: multiple angles from *the same consistent image set* are fine; multiple *different* images of one face cause averaging. → A/B test in step 9.
4. **Tag & weight syntax**: Seedance 2.0 uses `@Image1…`; 2.5 has "role tagging" and mindstudio says there are per-ref weights — no official ByteDance documentation describing the syntax has been found. "Reference strength 70–80%" comes from a third-party site.
5. **Seedance 2.5 audio limits** (per-clip length, total duration): no official numbers found; the 2–15s figure is for 2.0.
6. The effectiveness of film stock names (500T, 250D…) in video prompts has not been publicly benchmarked — use them as aesthetic descriptors and check by eye; always pair them with a style frame.
7. Seedream versions/limits (4.5: 14 refs; 5.0 Pro: ≤10 recommended; output 1024–2K…) may differ by API provider.
8. Many Seedance sources are reseller/aggregator blogs (not ByteDance) with marketing motives; figures should be retested.

---

## 9. Sources (opened)

- https://www.animationartconservation.com/design-with-a-purpose,-an-interview-with-ralph-eggleston.html
- https://vfxscience.com/2018/07/15/color-scripting-incredibles-2/
- https://wherecreativityworks.com/model-sheets/
- https://blog.cg-wire.com/character-shape-language/
- http://drainmag.com/making-time-a-conversation-on-aging-film-costumes/
- https://www.studiobinder.com/blog/how-to-use-color-in-film-50-examples-of-movie-color-palettes/
- https://www.shutterangle.com/2012/film-video-aspect-ratio-artistic-choice/
- https://www.holygrain.com/blog/kodak-vision3-500t-vs-250d/
- https://nofilmschool.com/film-lookbook
- https://www.moviemaker.com/show-and-tell-strengthen-your-lookbook-with-this-checklist/
- https://www.rogerdeakins.com/forums/topic/what-information-should-a-look-book-be-included/
- https://www.mindstudio.ai/blog/seedance-2-5-multimodal-reference-system-explained
- https://apiframe.ai/guides/seedance-2-5-guide
- https://imaginetovideo.com/blog/seedance-2-5-official-release-and-integration-plan
- https://magichour.ai/blog/seedance-20-reference-guide
- https://vicsee.com/blog/seedance-2-0-omni-reference
- https://www.seedanceai.cc/capabilities/consistency
- https://sagnikbhattacharya.com/blog/seedance-reference-images-characters
- https://clipdance.ai/blog/ai-video-reference-images-guide
- https://cozyclay.org/seedance-camera-control/
- https://www.mixar.app/blog/blender-blockout-to-video
- https://www.xmk.com/seedream/blog/seedream-5-0-pro-reference-images
- https://evolink.ai/blog/seedream-prompt-guide-best-practices-2026
- https://upsampler.com/blog/make-ai-images-look-real
- https://ourcodeworld.com/articles/read/4731/how-to-make-ai-video-faces-look-real-4-easy-steps
- https://framestrategy.substack.com/p/the-ai-aesthetic
- https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/instant-voice-cloning
