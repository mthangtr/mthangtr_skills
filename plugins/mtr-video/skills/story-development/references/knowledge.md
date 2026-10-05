# 02 — Story Development (Treatment → Beat Sheet → Screenplay)

> **Model-agnostic note (v0.3.0):** this research was compiled with Seedance 2.5 as the reference video model. Every Seedance-specific number here (call length, ≤30 s units, ≥3 s shots, reference counts, 24 fps, 720p, 32 kHz audio, @Image tags, prices, policy) is an example from the `seedance-2.5` profile, not a pipeline rule. Read the real limits from the active profile (`video-generation/references/models/<id>/profile.json`) and apply `film-pipeline/references/shared-conventions.md`. Where this file says "skill 6", read `video-generation`; references like "06 §N" point to `video-generation/references/models/seedance-2.5/knowledge.md`.

> `references/` document for Skill 2 of the `ai-film-studio` plugin. Scope: short films 1–15 min and short-form 15–90s (ad, social). Skill outputs: `treatment.md`, `beatsheet.md`, `script.fountain`, `story-gate.md`. Research date: 2026-10-02.

---

## 1. Core principles

1. **One character, one want, one conflict.** A short film focuses on "one or two main characters and a single conflict" (Greenlight Coverage). Backstage: "Simple wants, complex actions." Richard Price: "The bigger the issue, the smaller you write" — pick the smallest manageable piece of the big issue.
2. **Do not cram a feature into a short.** Sundance programmer Adam Piron: "don't try to cram in a full three acts or how you would normally structure a feature." Landon Zakheim: "make it as short as it can be, while being as long as it needs to be." Under 15 min is "easiest to program" (Emily Doe, Sundance).
3. **Start immediately.** Establish protagonist + goal on the first page; the inciting incident may already have happened before FADE IN (Backstage).
4. **Every scene must turn.** McKee: a scene is "an action through conflict in more or less continuous time and space that turns the value-charged condition of a character's life." Unchanged value = nonevent → cut it or merge its information into another scene.
5. **Film is a visual medium.** A dialogue-driven script is the "Not Cinematic" flaw (The Script Lab). Prefer visible action over words; "characters are what they do" (Bang2write).
6. **The big idea must be tellable concisely.** "It's not just about the BIG idea. It's about the big idea that can be told concisely" (Danny Manus, Script Mag). A short still needs resolution/finality.
7. **Point of view > formula.** Programmers prioritize originality and a distinct POV (Sundance). For AI-assisted writing this is risk #1: LLMs produce "median output" — a statistically average combination (Coyote Tracks). The skill must force out specific, personal, strange details.
8. **Design for AI production from the first word.** Every scene must split into generation units ≤30s (Seedance 2.5), few characters speaking simultaneously, "shootable" action (see section 8).

---

## 2. Process

Fixed sequence; every step has an artifact and a gate. Do not write the screenplay until the beat sheet passes.

### Step 0 — Input from Skill 1
Receive logline + format (length, aspect ratio, platform) + tone. If missing, ask at most 3 questions: *Target length? Who is the protagonist and what specifically do they want? What should the audience feel in the final second?*

### Step 1 — Story spine (5 lines, before the treatment)
```
PROTAGONIST: [specific name, not an LLM default name — see section 6] + 1 visual trait + 1 signature behavior
WANT (external, visible on screen): ...
NEED (internal, theme): ...
OBSTACLE / OPPOSITION: ...
TURN + ENDING IMAGE: the final image (not a line of dialogue)
```
Want = plot, Need = theme; the tension between the two creates drama — achieving the want without filling the need (No Film School). For films <3 min the want alone may suffice; need is optional, implicit.

### Step 2 — Treatment (0.5–2 pages, present-tense prose)
- Paragraph 1: the world + protagonist through one defining action ("the single action that reveals everything about your character" — Backstage).
- Paragraphs 2–3: progression through the main turns, stating the value shift from +/– to –/+.
- Final paragraph: climax and ending image. Do not write "a story about love and loss" — write events.
- Attach: character list (≤3 speaking for films ≤3 min, ≤5 for 10–15 min), location list (≤3 for ≤3 min), tone references.

### Step 3 — Beat sheet
Pick a template from section 3 by length. Each beat = 1 line: `[timecode] BEAT NAME — specific event — value: X(+)→X(–)`. Write it in Fountain using `#` sections + `=` synopses so the beat sheet lives inside the script file.

### Step 4 — First draft (Fountain)
Write fast, not perfect (Backstage step 3). Before writing each scene: fill in the scene card (section 4.1).

### Step 5 — Revision passes (in order, one goal per pass)
| Pass | Question | Tool |
|---|---|---|
| P1 Structure | Does every scene turn? Continuous escalation? Is the climax decided by the protagonist? | Value table: list scene → start/end value. Any "=" scene gets cut/merged (McKee). |
| P2 Character | Is the protagonist active (causes events) or passive (events happen to them)? Does every character have a reason to exist? | Count: protagonist decisions ≥ external events. A character whose deletion would not change the story → delete. |
| P3 Dialogue | On-the-nose? Do all characters sound the same? Could dialogue be replaced by action? | Hide character names — can you guess who speaks? Rule: every line must reveal character or advance plot (Backstage). |
| P4 Visual | Does every scene have at least 1 unique image? Do action lines describe what the camera can see? | Delete every unfilmable interior description ("she remembers..."). |
| P5 Anti-AI | Scan for section 6 patterns. | Checklist + grep word list. |
| P6 Trim | Can you enter later? Can you leave earlier? | "Enter late, leave early": start at the tensest point, end before resolving (Ben Scharf/Goldman). |
| P7 Production | Does every scene split into ≤30s units? Speakers/unit ≤2? | Section 8. |

### Step 6 — Table read for AI (TTS read-aloud)
Script Reader Pro: the #1 way to kill on-the-nose dialogue is to *recognize it* — read aloud, table read. AI version:
1. Export dialogue by character, assign each character a different TTS voice (or use Seedance's own native audio at the animatic stage).
2. Read the whole thing aloud, timed. Listen for: lines nobody would say out loud, lines longer than one breath, two characters who sound like one person.
3. Compare actual duration to beat timing; if off by >15%, trim.
4. Speed rule of thumb: 30s ad ≈ 70–85 spoken words (Celtx) → ~2.5 words/second in English. Leave room for pauses/reactions: dialogue occupies ≤60% of unit duration.

### Step 7 — Timing
- Page-to-minute: data from 2,520 scripts shows 1 page ≈ 55 seconds on average; comedy/dialogue-heavy scripts run longer per page (ratio 1.15), "trust the camera" films have a lower ratio (Stephen Follows). Short scripts have a ratio of ~0.8 (fewer pages than minutes).
- For shorts ≤3 min **do not use page count** — compute from beat timecodes + TTS read + action estimate (count each action line ≈ 2–4s, each shot ≥2s).

---

## 3. Structure templates (beat timings)

Choose structure by the nature of the story: clear conflict → compressed 3-act / Story Circle; no antagonist, moment/reinterpretation type → Kishōtenketsu; ad → hook–problem–turn–payoff–CTA.

### 3.1 30s (ad / social / micro-story) — "Hook–Turn–Payoff" = 1 generation unit
| Timecode | Beat | Notes |
|---|---|---|
| 0–3s | HOOK | Unusual image or visual question. No logo, no weather, no "establishing". "If the first five seconds are generic, the audience may never reach the good part" (Celtx). |
| 3–12s | SETUP / DESIRE | Character + want/problem shown through action. |
| 12–22s | TURN | A single surprise (product, discovery, role reversal). |
| 22–27s | PAYOFF | Value reverses, emotional peak. |
| 27–30s | BUTTON / CTA | Ad: specific imperative CTA. Story: ending image or punchline. |
Ad core flow (Celtx): hook → problem/desire → solution → benefit → emotional payoff → CTA. Total dialogue ≤ 70–85 words; ideally ≤40 to leave space.

### 3.2 60s — Kishōtenketsu or mini 3-act (2–3 units)
**Kishōtenketsu** (Ki introduces, Shō develops, Ten is an unexpected twist "often unrelated" to the first two parts, Ketsu unifies/reinterprets — Mythic Scribes; Brad Guigar stresses that tension comes from *reinterpretation*, not conflict):
| 0–12s Ki | 12–30s Shō | 30–45s Ten | 45–60s Ketsu |
|---|---|---|---|
| Character + habit | Deepen, audience bonds, expectation forms | A strange element intrudes, redefines everything | Image linking Ki/Shō with Ten — "ah, so it was..." |

**Mini 3-act 60s:** 0–5 hook+setup / 5–15 inciting / 15–40 attempt+complication (2 steps) / 40–52 climax choice / 52–60 resolution image.

### 3.3 3 min — Compressed 3-act / Story Circle (6–9 units)
Story Circle (Harmon, StudioBinder): 1 YOU (comfort zone) → 2 NEED (want something) → 3 GO (unfamiliar situation) → 4 SEARCH (adapt) → 5 FIND (get it) → 6 TAKE (pay heavy price) → 7 RETURN → 8 CHANGE.
| Timecode | Circle | 3-act | Value |
|---|---|---|---|
| 0:00–0:15 | 1 You | Opening image + hook | status quo (±) |
| 0:15–0:30 | 2 Need | Inciting incident | want switches on |
| 0:30–0:50 | 3 Go | Lock-in / Act 1 break | enter unfamiliar territory |
| 0:50–1:30 | 4 Search | Complications (2 escalating steps) | ↑ stakes |
| 1:30–1:50 | 5 Find | Midpoint win/false victory | + |
| 1:50–2:20 | 6 Take | Price / all-is-lost | – – |
| 2:20–2:45 | 7 Return | Climax choice (protagonist decides) | reversal |
| 2:45–3:00 | 8 Change | Final image mirroring the opening | new value |
Max 3 locations, 2–3 speaking characters, 4–7 scenes.

### 3.4 10 min — Compressed Save the Cat (20–30 units)
Save the Cat 15 beats by % (applied to 10:00). A short does not need all 15 — merge as follows:
| Timecode | Beat (merged) |
|---|---|
| 0:00–0:30 | Opening Image |
| 0:30–1:00 | Theme Stated (implicit, through action or 1 oblique line) + Set-up |
| 1:00–1:20 | Catalyst |
| 1:20–2:00 | Debate (shortened or dropped) |
| 2:00–2:30 | Break into Two |
| 2:30–5:00 | Fun & Games (promise of premise) — B story if any, only 1 |
| 5:00 | Midpoint (false win/false defeat, stakes raised) |
| 5:00–7:00 | Bad Guys Close In |
| 7:00–7:30 | All Is Lost |
| 7:30–8:00 | Dark Night (can be just 1 silent shot) |
| 8:00–8:15 | Break into Three |
| 8:15–9:30 | Finale |
| 9:30–10:00 | Final Image (mirrors/inverts Opening Image) |
Constraints: max 1 subplot; 4–8 locations; ≤5 speaking characters; Danny Manus recommends festival shorts of 4–8 min + credits; keep credits short (2 min of credits on a 10-min film "plays very awkwardly" — Mike Plante, Sundance).

### 3.5 Scaling rules
- Each doubling of length: +1 escalation step, not +1 character.
- 15–90s: 1 turn. 3 min: 2 major turns. 10–15 min: 3–4 major turns + midpoint.

---

## 4. Scene and dialogue craft rules

### 4.1 Scene card (mandatory before every scene)
```
SCENE #: __  LOCATION/TIME: __   DURATION TARGET: __s  UNITS: __
POV CHARACTER: __     GOAL in the scene (action verb): __
OBSTACLE (who/what blocks): __
TACTICS (2–3 approaches the character tries): __
TURN (moment the value reverses): __   VALUE: __(+/–) → __(–/+)
GAP: character expects __, actual result __
ENTER at: __ (as late as possible)   EXIT at: __ (before resolve)
VISUAL SIGNATURE (1 image only this scene has): __
SPEAKERS: __ (≤2 / unit)
```
McKee: the gap between expectation and result is the engine. A scene with no turn = delete.

### 4.2 Scene rules
- **Enter late, leave early.** No greeting, arriving, sitting-down scenes. Start when tension already exists; end while the question still hangs. Exception: the entrance itself reveals character.
- **Do not open with:** BLACK, weather, a character waking up, walking, eating, long set dressing (Bang2write).
- **The opening visual** must signal genre + tone + character type + situation at once.
- **Escalation:** conflict evolves "every few pages"; for a short — every scene's stakes must be higher than the previous scene's (Script Lab).
- **Active protagonist:** the climax must be the protagonist's *choice*, not deus ex machina / rescue by someone else.
- **Exposition = ammunition:** only deliver information when a character needs it to win an argument; "Have Characters Argue About the Exposition" (ScreenCraft). Spread thin, not thick.
- **Logic holes:** every ability that resolves the climax must be planted earlier (avoid "the protagonist suddenly becomes a swordsman" — Coyote Tracks).

### 4.3 Character rules
- Introduce characters through action, ≤ ~4 lines of impact (Danny Manus). Character description in action: age + 1 visual detail that conveys personality, no "stunning/beautiful" (Script Mag lists it as a red flag).
- Visual characterization: recurring props/habits (a pocket watch, the way shoelaces are tied) — both tell the story and aid consistency when generating (feed into the Skill 3 visual-bible).
- Economy: do not leave "MAN", "WOMAN" for many pages; give a name or a specific role (BARISTA, BRIDGE KEEPER).
- Every supporting character must pressure or redirect the protagonist.

### 4.4 Dialogue rules
1. **Subtext:** characters talk about something else; emotion shows through action. ScreenCraft: at a funeral, they discuss the football game, the food — not the grief (The Big Chill). Will Hunting never says "I don't want to be here".
2. **Show, don't tell:** if a character recounts an event, film that event (Script Reader Pro). "We'd rather see a character cry than hear them say 'I'm sad'" (ScreenCraft).
3. **Short:** McKee — audiences tire of long dialogue after 10–15 seconds; use short exchanges. A monologue >4–6 lines is "false movement" (Bang2write).
4. **On-the-nose is valid** only when: surprising, deliberately repeated ("It's not your fault"), or the thematic climax (ScreenCraft).
5. **Silence is a line.** Write it explicitly in action: `She doesn't answer. Pushes the teacup across.` — but do not overuse "the silence was deafening" (section 6).
6. **Voice test:** hide the names — each character must have different vocabulary, rhythm, sentence length, and things they avoid. Assign each character: 1 verbal tic, 1 topic they always steer toward, 1 thing they never say directly.
7. **Asymmetry:** real conversation is not symmetrical — people answer a different question, interrupt, go silent, answer with a question. Banned pattern: A asks – B answers fully – A responds emotionally – B sums up.
8. **Minimal parentheticals:** "(sadly)" is a red flag (Script Mag). Use only for small simultaneous actions or to specify the addressee.

### 4.5 Writing dialogue for AI dialogue generation (models with native audio; researched on Seedance 2.5)
- Short, speakable lines ("You actually came" to leave room for pause/reaction — Picsart). "Long written dialogue can overwhelm the timing of a short scene."
- 1 language / prompt; state language + accent + delivery before the line (OpenArt): `Spoken language: American English. She says it fast and annoyed: {I told you this would happen.}`
- Speakers: ≤2 characters speaking in 1 unit (our heuristic; OpenArt only says ≤8 people/product to keep consistency, and their dialogue example is a two-shot). Each line gets its own timestamp range (`8–14s: ...`).
- Lines ≤12 words; ≤3 lines/character/unit; avoid overlap/dual dialogue (Fountain `^`) within a generated unit — do dual dialogue only in post with separate audio.
- Translation: a translation can be significantly longer/shorter → rewrite for naturalness, do not translate literally (Picsart).
- Avoid hard-to-pronounce proper names, long numbers, abbreviations; write numbers out as words in dialogue.

---

## 5. Fountain format cheat-sheet

Source: fountain.io/syntax. A `.fountain` file is plain text.

| Element | Rule | Force |
|---|---|---|
| Title page | `Key: value` at the top of the file (Title, Credit, Author, Draft date, Contact); multi-line values indented ≥3 spaces/tab | — |
| Scene heading | Line starting with `INT` `EXT` `EST` `INT./EXT` `INT/EXT` `I/E` + period or space; blank line before and after | `.` at line start (`.SNIPER SCOPE POV`) |
| Scene number | `INT. HOUSE - DAY #1A#` | — |
| Action | Any paragraph not matching another element; line breaks preserved; tab = 4 spaces | `!` at line start (uppercase action) |
| Character | ALL CAPS line, blank line before, NO blank line after; must contain ≥1 letter. Extensions: `MOM (O.S.)`, `(V.O.)`, `(CONT'D)` | `@` (`@McCLANE`) |
| Dialogue | Immediately after Character/Parenthetical | — |
| Parenthetical | `(...)` after Character or within Dialogue | — |
| Dual dialogue | `^` after the second character's name | — |
| Transition | ALL CAPS ending in `TO:`, blank line before/after | `>` at line start (`>Burn to White.`) |
| Centered | `>THE END<` | — |
| Lyrics | `~` at line start | always forced |
| Notes | `[[note]]` — inline or on its own line | — |
| Boneyard | `/* ... */` (ignored when rendering, keeps old drafts) | — |
| Sections | `#` Act, `##` Sequence, `###` Scene — not shown when rendered | — |
| Synopses | `= summary line` — not shown when rendered | — |
| Page break | Line containing only `===` (≥3) | — |
| Emphasis | `*italic*` `**bold**` `***bold italic***` `_underline_`; escape `\*` | — |

**Plugin convention:** `#` = act/structure beat, `##` = beat from the beat sheet (with timecode), `=` = synopsis value change, `[[UNIT ...]]` = generation unit note for Skill 4/6.

### Example scene (60s Kishōtenketsu, 2 units)
```fountain
Title: Ông Tư's Clocks
Credit: written by
Author: [user]
Draft date: 2026-10-02

# KI — 0:00–0:12
= Ông Tư sets the clocks for the whole neighborhood; value: order (+)

EXT. VŨNG TÀU FISH MARKET - DAWN

Nine clocks hang on a wooden stall, all reading 5:47. ÔNG TƯ (70, tank top, loupe clipped to his forehead) turns the knob of the tenth to match.

[[UNIT 1: 0–15s, 1 speaker, camera: slow push-in]]

# SHŌ — 0:12–0:30
= Bé Na brings a broken watch; expectation: it can be fixed

BÉ NA (8) sets a pink plastic wristwatch on the stall, its glass face cracked.

BÉ NA
It's my mom's. It stopped.

Ông Tư flips it over. The hands are stopped at 3:12.

ÔNG TƯ
Stopped long?

Bé Na shrugs. Looks out toward the sea.

# TEN — 0:30–0:45
= He doesn't fix it; value: order → doubt

[[UNIT 2: 15–30s, 2 speakers max]]

Ông Tư sets the loupe down. Doesn't open the case. He takes off his own watch, sets the hands to 3:12, and straps it onto Bé Na's wrist.

# KETSU — 0:45–0:60
= The whole stall stops at 3:12; value: the time of those who stay (+)

Bé Na leaves. Ông Tư turns back to the stall and, one by one, turns each clock.

Nine of them. All 3:12.

>THE END<
```
Note: no line explains that Bé Na's mother has died — the information lives in the action and the repeated number.

---

## 6. Anti-AI writing patterns

Compiled sources: Wikipedia "Signs of AI writing" (via Beutler Ink, StartupNaama — the original page blocks fetching), Antislop paper (arXiv 2510.15061, ICLR 2026), Max Read "Who is Elara Voss?", Coyote Tracks, LessWrong. Antislop measures: "Elara" appears 85,513× more often than in human text; "unsettlingly" 3,833×; "shimmered" 2,882×; "stammered" 2,043×; "heart hammered ribs" 1,192×; "voice trembling slightly" 731×; "said voice devoid" 693×; "felt profound sense" 550×; the "It's not X, it's Y" construction 6.3×. Slop fingerprints differ between model families → the list must be updated per model (Opus 5.5 may have its own tells — see section 10).

### 6.1 Grep list of words/phrases (case-insensitive) — every hit must be justified or deleted
`delve, tapestry, testament, intricate, pivotal, underscore, meticulous, vibrant, interplay, landscape (figurative), foster, crucial, enhance, showcasing, highlighting, enduring, a profound sense, the weight of, something shifted, something in her/his (eyes|voice) (changed|softened), barely above a whisper, voice trembling, heart hammered, unsettlingly, shimmered, stammered, devoid of, a breath (she|he) didn't know, the silence was (deafening|heavy), hung in the air, palpable, electric (tension), echoed through, in that moment, for the first time in (years|forever), it was as if, couldn't help but, a mix of X and Y, little did (she|he) know, Elara, Kael, Voss, Thorne, Aris, Elias Vance, Erebus, Whispering Woods`

### 6.2 Pattern table: detect → fix
| # | Pattern | Detect | Fix rule | Before → After |
|---|---|---|---|---|
| 1 | Abstract-noun gravitas ("the weight of", "a testament to", "tapestry") | Abstract noun as the emotional subject; "the weight of the crown" repeated 8–45 times/novel (Coyote Tracks) | Replace with an object + an action the camera can see | "She felt the weight of his absence." → "She still sets out two pairs of chopsticks. Puts one pair back." |
| 2 | "Something shifted" / vague interiority | A sentence describing change with no concrete agent | State the exact behavior that changes | "Something shifted between them." → "He pulls his chair closer. This time she doesn't back away." |
| 3 | Character declares emotion | Dialogue containing "I feel", "I'm scared", "I'm angry", "You hurt me" | Move the emotion into action/another topic (subtext) | "I'm terrified of losing you." → "What time's your flight tomorrow? … Where'd you leave your jacket?" |
| 4 | Everyone shares one articulate voice | Hiding names, you can't guess who speaks; complete sentences, standard grammar, identical vocabulary (Coyote Tracks: "all characters speak identically") | Voice sheet per character (tic, sentence length, what they avoid); allow fragments, bad grammar, slang | Old man: "Indeed, the sea has always been my greatest teacher." → "The sea? It took two of my boats." |
| 5 | Symmetric ping-pong | A asks–B answers fully–A exclaims–B concludes; turns of equal length | Break the symmetry: dodge the question, answer with action, interrupt, one talks a lot while the other is nearly silent | A: "Why did you leave?" B: "Because I was afraid." → A: "Why'd you leave?" B: (peels the label off a beer bottle) "This beer's expired." |
| 6 | Therapy-speak | "boundaries", "process my feelings", "healing journey", "validate", "I hear you", "trauma" in everyday dialogue | Characters speak per their profession/age/region; emotion comes out clumsily | "I need to set boundaries to protect my peace." → "I'm not coming home Saturday. Stop calling, Mom." |
| 7 | Tidy moral / theme stated at the end | Final line of dialogue or VO sums up the lesson ("Sometimes, the greatest journey...") | End on an image; the theme may only be spoken if spoken *wrongly*/ironically | "And she realized home was never a place." → Final image: she hangs the old key on a hook in the new apartment. |
| 8 | Hope montage / bow ending | Ends with a sunrise, smiles, every thread resolved | LessWrong: better an "evocative lingering image rather than wrapping everything up with a bow". Leave 1 open question; a winning value comes at a price | Montage of sun rising, hugging → One shot: two people at opposite ends of a bench, hands resting between them, not yet touching. |
| 9 | Weather/sound cliché: rain, whispering, "deafening" silence | Rain in a sad scene; "whisper" >1 time/page; "the silence" as subject | Choose weather counter to the emotion or neutral; write silence as the specific sounds that remain | "Rain poured as she whispered goodbye. The silence was deafening." → "Harsh sun. The ceiling fan rattles. She says goodbye in a normal voice." |
| 10 | Rule of three | Chain of 3 adjectives/3 parallel clauses ("cold, dark, and unforgiving") | Pick the 1 sharpest detail; or 2; or an asymmetric 4 | "The room was cold, empty, and silent." → "The fridge unplugged, its door ajar." |
| 11 | Negative parallelism "not X, but Y" / "It's not X. It's Y." | Regex `not (just )?\w+.*(but|it's)` (6.3× per Antislop) | State Y directly or show Y | "This isn't a job. It's a calling." → "Fourth night shift this week, and she still goes out herself to buy pastries for the whole station." |
| 12 | Em-dash overuse | >1 em dash / 100 words in action | Use periods, line breaks (short action lines are screenplay standard) | "He turns — slowly — and sees her — finally." → "He turns around. She's standing there." |
| 13 | LLM default names | Elara, Kael, Voss, Thorne, Aris, Elias Vance, Dr. ___ "on the verge of breakthrough", an AI named Erebus (Max Read, Antislop) | Names drawn from a specific context (region, generation, profession); check they are not on the blocklist | "Dr. Elara Voss" → "Chị Hạnh, night-shift technician at the Côn Đảo monitoring station" |
| 14 | Intensifier sensory slop | "heart hammered against ribs", "voice trembling slightly", "unsettlingly", "shimmered", "stammered" | Screenplays do not describe internal organs; write what can be filmed or cut it | "Her heart hammered as she stammered." → "She says the line again, slower." |
| 15 | Decorative bit characters | Someone singing in the courtyard, a child laughing in the distance, an old man nodding sagely (LessWrong) | Delete every background character with no plot impact; every extra is a generation cost | "In the courtyard below, a child sang softly." → (delete) |
| 16 | False range / abstraction | Fake-spectrum "From X to Y" ("from bustling markets to quiet temples") | One location, one detail | "From the neon streets to the silent rooftops, the city breathed." → "A karaoke sign flickers above his head." |
| 17 | Compulsive summary / treadmill | Scene or dialogue restates what the audience just saw; "Overall/In the end" in VO | Cut; trust the audience | B: "So you're saying you lied to me all along?" (after we've already seen it) → delete the line, keep the reaction. |
| 18 | Unmotivated emotional beat | Character cries/explodes with no trigger in the scene | Plant a specific trigger ≥1 scene earlier; or lower the intensity | — |
| 19 | Generic imagery | Descriptions like "a small café", "an old house" with no distinct detail | Each location gets 1 distinctive detail (also an anchor for the visual-bible) | "A cozy café." → "A sock-filter coffee stall, red plastic tables, a TV playing muted cải lương opera." |
| 20 | Escalating conspiracy / inflated stakes | Adding organizations, villains, "the fate of the world" (Coyote Tracks "cascading conspiracies") | Personal, small-scale stakes; one opposition | — |
| 21 | Over-explained subtext ("laying it on thick") | Good dialogue followed by explanatory action ("She says this, but means she misses him.") | Delete the explanation; if the audience won't get it, fix the action, don't add annotation | — |

### 6.3 Anti-AI pass procedure
1. Grep the 6.1 list → for each hit: delete / replace / mark `[[KEEP: reason]]`.
2. Count: em dashes/100 words; triplets; "not X but Y" sentences; dialogue turns with "I feel/I'm + emotion".
3. Voice test (names hidden) for every pair of characters.
4. Ending test: is the last line an image or a lesson?
5. Specificity test: every scene has ≥1 detail that a different LLM could not guess from the logline.

---

## 7. Script-reader red flags (coverage criteria)

Standard coverage scores: Premise/Concept, Structure, Character, Dialogue, Pacing, Visual/Cinematic, Originality, Production viability → Pass / Consider / Recommend.

**Story (The Script Lab):** plot lacking events; characters not layered/flawed/changed; no escalation; loose structure (intro too long); unnatural/exposition-heavy dialogue; logic holes and convenient resolutions; derivative; not cinematic.

**Page 1 (Bang2write):** dull opening (BLACK, weather, camera angles, walking/eating); no strong visual; characters introduced through talking; overloaded dialogue, monologues >4–6 lines; long set dressing, passive characters.

**Craft/format (Script Mag "20 Little Things"):** overused "We see"; addressing the reader ("Dear reader"); dense action blocks; scene headings longer than 1 line; flashbacks piled up early; "(sadly)" parentheticals; "!!!"/"???"; citing other films; excessive wardrobe description; "MAN/WOMAN" for many pages; describing women as "stunning/beautiful", age/ethnic stereotypes.

**Short-film specific (Sundance, Danny Manus):** long opening credits; music overpowering the scene; credits long relative to the film; forcing feature structure; no resolution; too many locations/characters; children/animals/VFX that cannot be handled (for AI: animals and children are feasible but consistency is poor — see section 8).

**AI-specific red flags (our addition):** every section 6 pattern; all characters speaking in one voice; lesson ending; "median" premise (ending guessable from the logline).

---

## 8. AI-production adaptation rules

### 8.1 Generation-unit math
- 1 unit = 1 Seedance 2.5 run ≤30s (multi-shot within a unit via timestamps `0–5s:`; whole seconds, no gaps, 1 action/timestamp range — OpenArt).
- Each scene carries `[[UNIT n: start–end, speakers, camera]]`. Scene >30s → split at a natural beat (a turn or a thought cut), never mid-line of dialogue.
- Clips ≤20s are more reliable to re-edit (region edit) (OpenArt) → important scenes should be written as 15–20s units.
- Prompt drift happens when only the beginning is described in detail (Picsart) → every unit in the script must have a clear *end state* (final pose/position/emotion) — write it into the unit's last action line.

### 8.2 Characters & dialogue
- ≤2 speaking characters / unit; ≤3 characters with clearly visible faces / unit (heuristic; consistency drops with crowds).
- No overlapping dialogue; no dual dialogue within a generated unit.
- Each main character needs a stable ref (Skill 3) → avoid costume changes mid-film unless it is a beat; each change = a new ref set.
- 1 language / unit.

### 8.3 "Unshootable" or high-risk action → rewrite
| Avoid | Because | Replace with |
|---|---|---|
| Interiority ("she remembers her childhood") | cannot be filmed | flash cut to 1 specific image, or an evocative prop |
| Complex hand interaction (tying knots, playing an instrument note by note, writing legible text) | hands/text error-prone | cut to a close-up of the result; simple insert shot |
| Important on-screen text (letters, long messages) | text rendering unreliable | ≤3 words, or add in post (Skill 8), or VO |
| Crowds with specific interactions | consistency | crowd as blurred background, 1–2 focal characters |
| Multi-step physical cause-effect chains (dominoes, complex collisions) | physics drift | 1 action/timestamp range, cut between steps |
| Character gradually changing appearance within 1 shot | identity drift | cut before/after |
| Multiple camera moves in 1 beat | "Stacking camera moves" is an error (OpenArt) | 1 camera move/beat; note it in `[[UNIT]]` |
| Action continuity across multiple units (a glass of water slowly emptying) | hard to match | avoid continuous states; use cut on action |

### 8.4 Writing for refs & previs
- Each location: 1 distinctive descriptive sentence + fixed time of day (Danny Manus: keep time-of-day consistent) → used by Skill 3/5.
- Meaningful props: list a props list at the end of the script (Fountain note `[[PROPS: ...]]`).
- Write action lines in the order the camera sees, each line ≈ 1 shot idea — helps Skill 4 extract the shot list.

---

## 9. Gate checklist (story-gate.md — all must PASS before Skill 3)

**Concept/structure**
- [ ] 1-sentence logline: specific protagonist + want + obstacle + stakes.
- [ ] Chosen structure template matches length; beat timecodes total = target ±10%.
- [ ] Every scene has an explicit value change (+→– / –→+); no "=" scenes.
- [ ] Climax decided by the protagonist; every payoff has a plant.
- [ ] Ending is an image, not a lesson line.

**Character/dialogue**
- [ ] Number of speaking characters within limits (≤3 for ≤3 min; ≤5 for 10–15 min).
- [ ] Voice test passes (distinguishable with names hidden).
- [ ] No dialogue directly declaring emotion (except exceptions marked `[[KEEP]]`).
- [ ] No monologue >4 lines (short-form: >2 lines).

**Anti-AI**
- [ ] Grep 6.1 = 0 unhandled hits.
- [ ] Em dash ≤1/100 words; no decorative triplets; no decorative "not X but Y".
- [ ] Character names not on the blocklist.
- [ ] Every scene has ≥1 distinctive detail.

**Format/timing**
- [ ] `script.fountain` parses (scene headings, characters, transitions follow the rules).
- [ ] TTS table read complete; read duration within ≤15% of beat timing.
- [ ] Short-form: hook within 0–3s; ad has a specific CTA; ≤85 spoken words/30s.

**Production**
- [ ] Every scene has `[[UNIT]]` ≤30s, preferring 15–20s for difficult scenes.
- [ ] ≤2 speakers/unit; 1 language/unit; no overlap.
- [ ] No unhandled actions from table 8.3 remain.
- [ ] Locations/props/characters lists exported for Skill 3.

---

## 10. Uncertain info (needs verification)

1. **Wikipedia "Signs of AI writing"** could not be fetched directly (blocked) — the list comes via Beutler Ink and StartupNaama summaries; the word list changes with model generation (GPT-4 → 4o → 5). No public data on Claude Opus 5.5's own tells → the skill should self-learn: run 20 drafts, count repeated n-grams, update the blocklist.
2. **Antislop coefficients** (85,513× "Elara"...) were measured on a specific set of 2025 models; magnitudes may differ for 2026 models.
3. **Seedance 2.5 speakers/unit limit:** "≤8 people/product" comes from the OpenArt guide (third party); "≤2 speakers/unit" and "≤12 words/line" are our heuristics, with no official ByteDance benchmark. Lip-sync accuracy, max dialogue length per speaker: not documented (OpenArt explicitly marks them unspecified). The bracket syntax `{}` `< >` `（）` belongs to the OpenArt wrapper — may differ in the native API/other platforms; Skill 6 to confirm.
4. **Page-to-minute 55s/page** is a feature average (Stephen Follows); no data for shorts <3 min → use TTS + beat timing.
5. **Save the Cat % for shorts:** the allocation in 3.4 is a compression we derived from Blake Snyder's standard %, not an official template for shorts.
6. **The 4–8 min festival threshold** (Danny Manus) is personal opinion; Sundance says "no perfect length", <15 min is easiest to program.
7. The ~2.5 words/s rate is derived from "70–85 words/30s" (Celtx) — Vietnamese and other languages must be measured separately with TTS.

---

## 11. Sources (opened)

- Fountain syntax — https://fountain.io/syntax
- Greenlight Coverage, 12 Tips for Writing a Short Film — https://glcoverage.com/2024/12/25/tips-for-writing-short-film/
- Backstage, How to Write a Great Short Film — https://www.backstage.com/magazine/article/how-to-write-a-short-film-77787/
- Sundance, Advice for Makers of Short Films from Sundance Programmers — https://www.sundance.org/blogs/pep-talks-and-advice-for-makers-of-short-films-from-our-sundance-programmers/
- Script Magazine (Danny Manus), Elements of Great Short Films — https://scriptmag.com/features/notes-margins-elements-great-short-films
- Script Magazine, 20 Little Things That Make Script Readers Hate Your Screenplay — https://scriptmag.com/features/20-little-things-make-script-readers-hate-screenplay
- The Script Lab, 10 Most Common Problems in Amateur Screenplays — https://thescriptlab.com/features/screenwriting-101/11980-10-most-common-problems-in-amateur-screenplays/
- Bang2write, Top 5 Mistakes on Page 1 — https://bang2write.com/2024/04/top-5-mistakes-writers-make-on-page-1-of-their-screenplays.html
- McKee, Do Your Scenes Turn? — https://mckeestory.com/do-your-scenes-turn/
- Kortina, notes on McKee's Story — https://kortina.nyc/notes/mckee--story/
- StudioBinder, Dan Harmon Story Circle — https://www.studiobinder.com/blog/dan-harmon-story-circle/
- Mythic Scribes, Kishōtenketsu for Beginners — https://mythicscribes.com/plot/kishotenketsu/
- Brad Guigar, Kishōtenketsu — https://bradguigar.substack.com/p/kishotenketsu-storytelling-without-173
- No Film School, Character Want vs Need — https://nofilmschool.com/character-want-vs-need
- Ben Scharf, Enter late leave early — https://medium.com/@BenScharf/the-old-golden-rule-of-scene-writing-explained-based-on-the-actual-use-of-a-scene-9b36432c400c
- Script Reader Pro, On the Nose Dialogue — https://www.scriptreaderpro.com/on-the-nose-dialogue/
- ScreenCraft, How to Avoid On-the-Nose Dialogue — https://screencraft.org/blog/how-to-avoid-writing-on-the-nose-dialogue/
- Stephen Follows, Is the page-per-minute rule correct? — https://stephenfollows.com/p/is-the-page-per-minute-rule-correct
- Celtx, How to Write an Advertisement Script — https://blog.celtx.com/how-to-write-an-advertisement-script
- Beutler Ink, How to Spot AI Writing (per Wikipedia) — https://www.beutlerink.com/blog/how-to-spot-ai-writing
- StartupNaama, Wikipedia's AI Writing Guide — https://startupnaama.com/2026/07/22/wikipedias-ai-writing-guide-is-the-best-prompt-engineering-resource-nobodys-talking-about/
- Antislop (arXiv 2510.15061) — https://arxiv.org/html/2510.15061v2
- Max Read, Who is Elara Voss? — https://maxread.substack.com/p/who-is-elara-voss
- Coyote Tracks, Creative Writing and AI's Failure Modes — https://coyotetracks.org/blog/ai-writing/
- LessWrong, Ok, AI Can Write Pretty Good Fiction Now — https://www.lesswrong.com/posts/b6sTwHF3hmheFvvpu/ok-ai-can-write-pretty-good-fiction-now
- Yale Review (Sorrentino), Machine Stories — https://yalereview.org/article/christopher-sorrentino-machine-stories
- Picsart, Seedance 2.5 prompting guide — https://picsart.com/blog/seedance-2-5-prompting-guide/
- OpenArt, Seedance 2.5 Prompt Guide — https://openart.ai/blog/seedance-2-5-prompt-guide/
