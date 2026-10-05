# 01 — Concept Brainstorming (Skill 1) — Reference Knowledge

> **Model-agnostic note (v0.3.0):** this research was compiled with Seedance 2.5 as the reference video model. Every Seedance-specific number here (call length, ≤30 s units, ≥3 s shots, reference counts, 24 fps, 720p, 32 kHz audio, @Image tags, prices, policy) is an example from the `seedance-2.5` profile, not a pipeline rule. Read the real limits from the active profile (`video-generation/references/models/<id>/profile.json`) and apply `film-pipeline/references/shared-conventions.md`. Where this file says "skill 6", read `video-generation`; references like "06 §N" point to `video-generation/references/models/seedance-2.5/knowledge.md`.

> Scope: short film (narrative), branded film, music video, AI film. Pipeline: Claude Opus 5.5 → Blender previs (Blender Lab MCP) → Seedance 2.5 → dailies → post.
> Research date: 2026-10-02. All pricing/model spec numbers change quickly: see section 9.

---

## 1. Core principles (ground rules, numbered)

1. **One situation, one protagonist, one emotional core.** "Keep it simple" is the most universal rule of shorts (StudioBinder). Combine characters, cut detours (Pixar rule #5).
2. **Do not make a "mini feature".** Do not cram in a full 3 acts (Adam Piron, Sundance). Mike Plante: nobody gets to make a feature because someone "saw the whole feature in a 10-minute short".
3. **One strong turn > many twists.** A short can carry exactly one weighty reversal (reveal, choice, shift in the power balance). The twist must *change the meaning* of what was already seen, not just surprise.
4. **Scope matches runtime.** A 90s idea must not be stretched to 8 minutes; a 15-minute idea must not be squeezed into 60s. Quick rule: number of "state-changing beats" ≈ runtime (minutes) × 2–3 for narrative; ≤ 3 beats for 30–60s.
5. **Shorter = more likely to be selected.** Plante: films < 10 minutes have twice the chance of being programmed; average submission is 12 minutes; > 15 minutes must be excellent. "Make it as short as it can be, while being as long as it needs to be" (Landon Zakheim).
6. **Hook within the first 5 seconds when played online.** SOTW: "You have five seconds!" — no long opening credits. YouTube ABCD: tight framing, a human element, unexpected imagery, fast pacing in the first 5s.
7. **Have conflict/challenge, not just mood.** "Safe is boring… challenge your characters and make them uncomfortable" (SOTW). The character must *want* something and *do* something (Pixar #13: passive is "poison").
8. **Personal reason: "Why must you tell THIS story?"** (Pixar #14). Sundance programmers repeat it: authenticity, voice, point of view > production value.
9. **Discard the first idea (and the 2nd, 3rd, 4th, 5th).** Pixar #12. With an LLM this is mandatory because the first output is the "average of the distribution" (section 6).
10. **Know the ending before the middle.** Pixar #7. A concept without an ending image is not yet a concept.
11. **The concept must have "the one image".** One central image (mental image) that the listener remembers after 1 sentence. Save the Cat: logline = irony + compelling mental image.
12. **Choose a concept that *plays to* AI's strengths, not one that *fights* its weaknesses.** Trillo: Sora blends surreal environments → he chose the idea "infinite zoom through time like false memories". "If you're hitting the wall of the limitations of AI… go out and shoot it with a camera."
13. **Style must have a reason.** "Don't make your film black and white just to prove that you've seen classic films" (SOTW). Every style choice must serve the idea.
14. **Do not make films about AI itself.** Jason Sondhi (SOTW) criticized "self-referential navel-gazing" and "grandiose faux-profundity" at AIFF. Jurors have started judging AI films by ordinary cinematic criteria, not by novelty.
15. **Humanity/emotion beats technique.** TechCrunch (AIFF 2024): the winning films won on a "heartfelt script"; AI parts that expose broken physics destroy emotional momentum.
16. **Write to the budget (generation budget).** "Write to the budget… limitation often sparks the best creative solutions" (The Collective Pitch). In this pipeline "budget" = seconds generated × iteration ratio × shot difficulty.

---

## 2. Process step by step

### Step 0 — Intake brief (5 minutes, mandatory questions)
- Format: narrative short / branded / music video / art film. Distribution channel: festival / YouTube / TikTok-Reels 9:16 / event screen.
- Target runtime, aspect ratio, deadline, generation budget (USD or credits).
- For branded: single-minded proposition (1 sentence the brand wants the viewer to believe), mandatories (logo, product, claim), taboos. For music video: the song, waveform/structure (verse/chorus/drop), what the artist wants/hates (Collective Pitch #11).
- The user's "personal truth": 1 memory, 1 obsession, 1 thing they believe that others do not. If the user has none → Claude asks 3 probing questions (section 2-Step 1).
- Known AI constraints (section 5) are stated up front as "rules of the game", not left to the end.

### Step 1 — Seed harvesting (collect "fragments", not yet ideas)
Lynch: ideas arrive as a "small fragment" — write it down immediately. Collect ≥ 15 raw seeds from ≥ 5 different sources:
- **Personal truth**: "What do you do when nobody is watching?", "Your most embarrassing/heartwarming moment this year?", "A strange family rule?"
- **What-if**: take an everyday law and bend one variable ("What if every lie made you 1 kg lighter?").
- **Collision**: combine 2 distant worlds (Reply AIFF 2025 *Instinct*: a Neanderthal meets a skyscraper in the forest; AIFF 2026 *THE WELL*: a rabbit investigates a wolf's death in a snowy trailer park).
- **Inversion/fairy-tale flip**: the reverse perspective of a familiar story (AIFF 2026 Silver *Where Knights Fall*: Rapunzel waits atop a kingdom full of the corpses of those who came to rescue her; *JAILBIRD*: a chicken's point of view). Upside-down logline (Save the Cat).
- **Constraint**: self-imposed rules (1 location; no dialogue; 1 color; only hands visible; the whole thing is 1 fake take; told through objects).
- **The one image**: start from 1 beautiful/strange image, then ask "who is here, what do they want, what stops them?" (AI Video School: "Start with a visually compelling moment or question").
- **Ordinary personas** (counter LLM homogenization, section 6): generate ideas "from the perspective" of 6–10 specific ordinary people (a 60-year-old sticky-rice vendor in Hải Phòng, a diver welding oil pipelines, a 4th grader afraid of the dark…). Study arXiv 2602.20408: ordinary personas > "Steve Jobs" persona; combining CoT + persona gives the highest diversity, surpassing human groups.
- **Pixar #20**: take the building blocks of a film you hate and rearrange them into something you like.

### Step 2 — Diverge: 12–20 premise lines
- Each premise is 1 sentence: *[specific character] + [what they want] + [obstacle/irony] + [central image]*.
- Force a spread across at least 4 different "axes" (genre, tone, POV, scale, structure). Tag each premise with its axis to check coverage.
- 2-pass CoT technique for the LLM: write short titles for 20 ideas → self-revise each idea to be "bolder & distinct" → remove duplicates → only then write premises (arXiv 2602.20408).
- No evaluation in this step. No long paragraphs (keep it "oblique", avoid ideas that look "already complete" — arXiv 2402.01536: LLMs homogenize because of "low inferential distance" between output and complete-looking ideas).

### Step 3 — Cluster & de-dupe
- Group premises by "engine" (dramatic mechanism: chase, secret, choice, transformation, ritual, misunderstanding…). Two premises with the same engine + same turn = one idea → keep the stronger one.
- Run the banned list (section 6). Every idea that hits a flag → revise or discard.

### Step 4 — Converge round 1: shortlist 5–6 (tissue session style)
- Like the CP+B tissue session: present 10–15 "green shoots" to gauge reactions, *not* only 3 "pretty" ideas (Maggie Malek: going into the final with 3 ideas and none of them landing "is a huge waste of time").
- Present to the user as short cards: logline + one image + tone in 3 adjectives + preliminary AI-feasibility. Ask the user to choose/combine/discard; *do not* decide on the user's behalf.

### Step 5 — Develop 3 finalists into one-page concepts (template in section 4)
- Each finalist must differ in engine or tone (not 3 surface variants).
- Add: 3–5 beat sketch, ending image, "why us/why now", estimated shot count, AI risks.

### Step 6 — Score with the rubric (section 3), red-team, choose 1
- Claude scores, but presents low scores/risks before high scores (anti-sycophancy). Springboards: AI judges disagree strongly with human experts → Claude's score is *advisory*; the user decides.
- 3 red-team questions: "Who has already made this film?" (find the 2 closest references and state the difference), "At which shot does this film break when generated?", "If you cut 50% of the runtime, what remains?".

### Step 7 — Gate & lock (section 7) → handoff to story-development
- Output: final logline, one-page concept, feasibility notes, estimated budget, list of risks passed on to skills 3–6.

### Suggested timebox
| Step | Concept 30–60s (ad/MV teaser) | Short 3–10 minutes |
|---|---|---|
| 0–1 | 10 minutes | 20–30 minutes |
| 2–3 | 15 minutes (12 premises) | 30 minutes (20 premises) |
| 4–6 | 15 minutes | 30–60 minutes |

---

## 3. Rubric / scoring table

Score 1–5 per criterion; score = Σ(score × weight) / 5 → 100-point scale. Default weights are for an AI narrative short; the secondary table adjusts by format. (Weights are a synthesized proposal; AIFF 2026 judges 4 criteria: composition, narrative cohesion, originality, creative AI technique — each juror 1–10.)

| # | Criterion | Weight | 1 point | 3 points | 5 points |
|---|---|---|---|---|---|
| A | **Originality / freshness** | 20 | Hits the banned list; "seen it 100 times" | Familiar but with its own angle | No close reference found; surprising collision/inversion |
| B | **Emotional core & stakes** | 15 | Mood without conflict | Has want/obstacle but vague stakes | Character wants something specific, clear loss, viewers see themselves in it |
| C | **Clarity (1-sentence test)** | 10 | Needs a paragraph to explain | Logline OK but lacks an image | 1-sentence logline + 1 image, a stranger can retell it |
| D | **Scope fit runtime** | 10 | Mini-feature/ multiple subplots | 1–2 beats too many | Exactly 1 situation, 1 turn, fits the runtime |
| E | **The turn / ending** | 10 | No turn or dream-twist | Has a turn but predictable | Turn changes the meaning of the whole film; strong ending image |
| F | **AI-feasibility** | 15 | Needs many "Avoid" items (section 5) | 1–2 risky shots, with workarounds | Designed around AI strengths; exposed errors barely affect meaning |
| G | **AI-native justification** | 10 | Cheaper/better shot on camera | AI only saves money | Only AI can do it (world, transformation, scale) — "bold choices unfeasible without AI" |
| H | **Hook (first 5s) & visual identity** | 10 | Slow open, logo/credits | Has a hook but generic | The very first frame raises a question; a distinct, recognizable style |

**Thresholds:** ≥ 75 can lock; 60–74 must fix the lowest criterion then rescore; < 60 discard. **Veto rules (regardless of total):** B ≤ 2, F = 1, or A = 1 → do not lock.

**Weight adjustments by format:**
| Format | Change |
|---|---|
| Branded film | +10 "Brand fit" (the proposition emerges through the story, the product is not a stuck-on prop), −5 A, −5 G |
| Music video | +10 "Song fit" (structure follows the waveform, idea matches lyric/tone), D becomes "sustains full song", −5 C, −5 E |
| Social 9:16 ≤ 60s | H ×2 (20), E 5, D 5 |
| Festival AI | Keep defaults; G and H matter for "creative AI technique" |

---

## 4. Templates

### 4.1 Logline formulas
- **Core (Save the Cat-style):** *When [inciting event], a [character with a contradictory adjective — irony] must [action/goal] before [stakes/clock], but [obstacle/irony].*
- **Short-film variant (1 situation):** *[Specific character] in [1 specific place] tries to [1 small task] — until [the single turn].*
- **Pixar story spine (to check causality):** Once upon a time ___. Every day ___. One day ___. Because of that ___. Because of that ___. Until finally ___.
- **Branded:** *[Character] believes [old belief] until [a moment] makes them see [proposition] — understood without naming the product.*
- **Music video:** *Throughout [the song], [central image/device] transforms from [A] → [B], in parallel with [the lyric's emotion].*
- **Upside-down test:** rewrite the logline from the antagonist's perspective or in a "true but warped" way (Wizard of Oz = "a girl kills someone, then forms a gang to kill again"). If the inverted version is still interesting → the premise has an engine.

**Logline QC (must pass all before use):** ≤ 35 words · has a specific character (not "a man") · has an action verb · has irony · evokes 1 image · contains no abstract theme name ("love", "humanity", "memory") · does not reveal the twist.

### 4.2 One-page concept template
```
TITLE (working):
FORMAT / RUNTIME / ASPECT / CHANNEL:
LOGLINE (≤35 words):
THE ONE IMAGE (1 sentence – the image viewers remember):
HOOK (0–5s – the first frame & the question it raises):
PROTAGONIST: who / wants what / fears what / 1 specific detail only they have
CONFLICT ENGINE: what stands in the way; why it cannot be avoided
THE TURN: (1 sentence) – at ~ % of runtime
ENDING IMAGE: (1 sentence) – how it differs from the opening image
EMOTIONAL CORE (1 sentence, in the language of feeling, not theme):
TONE: 5–6 adjectives + 2–3 references (films/paintings/MVs) + "differs from the references in that…"
WORLD & STYLE: (stylized? photoreal? reason)
WHY AI / WHY THIS STYLE:
WHY US / WHY NOW (personal truth):
BEAT SKETCH: 3–5 beats, 1 line per beat
PRODUCTION SHAPE: #characters, #locations, estimated #shots, dialogue (Y/N, how much)
AI-FEASIBILITY: Strong items used / Weak items + workaround / Avoid items (must = 0)
BUDGET EST: finished sec × iteration ratio × $/sec
RISKS & KILL CRITERIA: what outcome at previs/test-gen means changing the concept
```

### 4.3 Worked example (narrative AI short, 3 minutes, 16:9, festival + YouTube)

- **TITLE:** *The Last Lamp Keeper* (working)
- **LOGLINE:** A lighthouse keeper, replaced by automation, secretly lights a lamp nightly for her husband lost at sea — until the ship needing that light is the one sent to dismantle it. *(30 words; irony: the light saves the very people who came to erase it)*
- **THE ONE IMAGE:** The tiny oil lamp in her hand set beside the giant, switched-off LED lamp.
- **HOOK (0–5s):** Close-up of a wrinkled hand turning the oil lamp's knob, a white-out storm beyond the glass; question: why is she doing this on a night like this?
- **PROTAGONIST:** Mrs. Lành, 78; wants to keep up a ritual with her husband; fears being sent to a nursing home; detail: counts the light's rhythm with a lullaby.
- **CONFLICT ENGINE:** The lighthouse is automated and under a dismantling order; she breaks the rules every night.
- **THE TURN (~70%):** The automated system fails in the storm; the dismantling ship loses its way; only her oil lamp can guide it in.
- **ENDING IMAGE:** The next morning, the dismantling crew stand still, watching her; a young crew member holds out a hand, asking to learn how to turn the lamp's knob.
- **EMOTIONAL CORE:** The feeling of keeping a promise to someone who can no longer hear it.
- **TONE:** still, salty, warm, lonely, gentle, enduring. Ref: *The Lighthouse* (composition), Andrew Wyeth paintings (palette), *Costa Verde* (intimacy) — differs in its warm ending, not horror.
- **WORLD & STYLE:** Stylized painterly-realism (Wyeth tones), not photoreal → hides face drift, increases recognizability.
- **WHY AI:** Sea storm, ship, light piercing rain — expensive to shoot for real; one character, one location → identity control.
- **BEAT SKETCH:** (1) the night ritual; (2) the dismantling notice pasted on the door; (3) storm, LED goes out, ship lost; (4) she lights the lamp, counts the rhythm with the lullaby, the ship comes in; (5) morning, the handover.
- **PRODUCTION SHAPE:** 1 protagonist + 1 supporting group (distant, few faces), 2 locations (lamp room, pier), ~28 shots, dialogue ≤ 2 lines (the lullaby is hummed — off-screen/no tight lip-sync needed).
- **AI-FEASIBILITY:** Strong: weather, light, sea, single character, object close-ups. Weak + workaround: hand turning the lamp knob (close-up, slow motion, Blender previs as motion ref; insert object shots without clearly visible fingers); ship in the storm (wide, silhouette). Avoid = 0 (no interacting crowds, no text — the dismantling notice is an overlay in post).
- **BUDGET EST:** 180s × 8 (iteration ratio) × $0.23/s ≈ $330 + 480p drafts ≈ $60 → ~$400 generation.
- **KILL CRITERIA:** If a 3-shot test-gen shows Mrs. Lành's identity drifting beyond the acceptable level at 720p even with 10 reference images → switch to a stronger style (gouache/claymation) before writing the story.

Sample rubric score: A4 B5 C5 D5 E4 F4 G3 H4 → (4×20+5×15+5×10+5×10+4×10+4×15+3×10+4×10)/5 = (80+75+50+50+40+60+30+40)/5 = 85 → can lock.

---

## 5. AI-feasibility matrix (reference model Seedance 2.5 + Blender previs, 10/2026; re-rate per model profile)

| Concept element | Strong (play to it) | Weak (OK, but needs a workaround) | Avoid (do not make it a pillar of the concept) |
|---|---|---|---|
| Characters | 1 protagonist; stylized/animal/claymation characters; hidden face (mask, shadow, back) | 2 characters in the same frame, light interaction | ≥3 characters in tight physical interaction; a character that must look identical across 40+ shots in photoreal |
| Identity | Strong style (painterly, clay, anime) hides drift; distinctive costume/silhouette | Photoreal single person with many ref images + previs | Real actors/famous characters (legal risk; Seedance is known to readily produce likenesses of celebrities/IP) |
| Action | Slow, continuous movement, clear camera moves (dolly, orbit, crane) — Blender previs as motion ref | Moderate action, with short cuts; one action per shot | Fast fights, collisions, sports, precise physics (weightless, passing through objects) |
| Hands & objects | Hands distant/not the focus | Close-up of hands slowly manipulating 1 simple object | Story meaning depends on precise finger actions (pressing buttons, writing, playing an instrument on the right notes) |
| Text | No text in frame; text as overlay in post | Blurry background signage | Plot depends on reading text in frame (letters, screens, messages) — must be comped |
| Dialogue | No dialogue; voice-over; music; 1–2 short lines | Short dialogue in a single-person close-up (native audio may mispronounce) | Long two-person dialogue exchanges, long lip-sync |
| Crowds | Non-interacting background crowds; silhouettes | Crowds doing simple synchronized actions (2.5 is reported to handle crowd scenes well) | Crowds needing plot-meaningful individual behavior |
| World | Surreal, transformation (morph), dream-logic with rules, weather, giant scale, nature, montage | Realistic everyday world needing prop continuity | Complex rule systems that must be explained through exposition |
| Location | 1–3 controlled locations, built in Blender as layout ref | 4–6 locations | A journey through 15+ locations, each visited once |
| Structure | Montage, vignettes with a linking device (1 object, 1 camera move), fake one-take by stitching 30s segments | Linear narrative of 20–40 shots | Structures requiring absolute second-by-second continuity (heist, puzzle) |
| Sound | Music-driven (beat-aware sync), ambience | SFX synced to action | Instruments played correctly on screen |
| Brand | Product as a static/rotating hero object, conceptual scenes | Hand-held product | Logo/packaging with accurate text in frame (do in post) |

**Implications for the concept (heuristic):**
- Prefer concepts "told through images + music + 1 voice" over "told through dialogue".
- Connect shots with a *visual device* (shared object, match cut, continuous zoom — Trillo style) instead of performance continuity.
- Do not put the main emotional beat in a shot from the Avoid column. If it is unavoidable, design that shot to reveal little (wide, silhouette, cut-away, off-screen sound).
- Choose the style before choosing the final concept: style determines drift tolerance.
- Avoid "tangentially related vignettes strung together by narration and a soundtrack" (TechCrunch) — a montage must have progression/a turn.

---

## 6. Anti-AI patterns: pattern → why bad → detect → fix

### 6A. Clichéd AI-film premises (banned/flag list)
| # | Pattern | Why bad | Detect | Fix |
|---|---|---|---|---|
| 1 | **Robot/AI learns to love / feel** | The most average premise in the distribution; jurors have seen hundreds | An AI/robot/android as the central character + an "emotional" arc | Remove the AI from the character; move the arc to a specific person/object with lived-in detail |
| 2 | **"What makes us human?" / meta about AI art** | "Self-referential navel-gazing" (Sondhi) | Theme is about creativity, machines, humanity, the tool itself | Ask "would this film still stand if shot on a camera?" — if not, change the subject |
| 3 | **Dream/simulation twist** ("it was all a dream/simulation") | Negates the stakes; Pixar #19 (coincidence getting characters out of trouble = cheating) | Ending contains: wakes up, simulation, glitch reveal, coma | The turn must come from the character's choice; dream-logic is OK only if its rules are set from the start |
| 4 | **Generic dystopia** (rainy neon city, megacorp, surveillance) | The world has no specific detail; anyone can prompt it | Keywords: neon, cyberpunk, rain-soaked, totalitarian, the system | Shrink it: 1 specific social rule affecting 1 small habit of 1 person |
| 5 | **Chosen one / ancient prophecy** | Feature-scale, needs exposition | "destined", "prophecy", "only one who can" | An ordinary character chooses to do something hard; personal stakes |
| 6 | **Post-apocalyptic lone survivor / hitman / grief-only** | SOTW lists these as clichés unless subverted | Survivor walking through ruins; grief without action | Keep the grief but tie it to 1 specific action/ritual (like the example in section 4.3) |
| 7 | **Last human / last tree / dying planet ecology sermon** | Over-explained theme, moralizing | A line of dialogue/VO states the message outright | Show it through 1 contrasting image, do not say it |
| 8 | **Generic time loop** | The engine is too familiar | "relive the same day" | Use only if the loop's rules are tied to the character's personality and it is short, ≤3 cycles |
| 9 | **Memory-as-visual-trip without conflict** (drifting memories, pretty montage) | Mood-without-conflict; "aesthetic experience over narrative" (First Scattering) | No answer to "what does the character want?" | Add a goal and an obstacle within the memory |
| 10 | **Grandiose cosmic montage + philosophical VO** | "Grandiose faux-profundity" | VO uses words like: universe, infinite, consciousness, we are | Scale down to 1 person/1 place; if keeping it cosmic, it needs a concrete idea like *Total Pixel Space* (1 clear mathematical idea) |
| 11 | **Recreating celebrities/deceased people** | Ethical + legal ("grave-robbing" — Amanda Palmer, via TechRadar) | Real names in the premise | An inspired fictional character, no likeness |
| 12 | **Spectacle-only showcase** ("see what the model can do") | Novelty has expired; jurors judge by ordinary cinematic criteria | No named character | Apply rubric B; if < 3, discard |

### 6B. LLM brainstorming failure modes
| # | Failure mode | Why bad | Detect | Fix (mandatory procedure) |
|---|---|---|---|---|
| 1 | **Surface variations** (5 ideas with the same engine, only the setting changed) | Fake diversity; LLMs collapse knowledge into 1 distribution (arXiv 2602.20408: first-idea categories LLM 8.37 vs humans 14.51) | Tag engine/turn/tone; ≥2 ideas matching on all 3 → fail | Force each idea to differ on ≥2 axes; use ordinary personas; CoT "bolder & distinct" |
| 2 | **Converging too early / fixation** | The first idea locks in later ideas (LLM fixation ≈ human, β≈1.0) | Ideas 10–20 resemble ideas 1–3 | Generate titles first, shuffle, discard the first idea (Pixar #12); keep diverge and converge strictly separate |
| 3 | **Sycophancy** (praising the user's ideas, scoring everything high) | Destroys the filtering function; AI judges diverge from experts (Springboards) | Every idea ≥ 4/5; no "this idea is weak because…" sentence | Mandatory: list 2 weaknesses per idea before strengths; forced ranking (no ties); name existing references |
| 4 | **Mood without conflict** | No storytelling engine | Premise has only adjectives + space ("melancholic, dreamlike city at dusk") | Test: "Who wants what, what stands in the way, what changes?" — missing 1 → not yet a premise |
| 5 | **Over-explained theme** | Viewers get lectured; Pixar #3 (theme emerges at the end) | Logline/VO contains abstract theme words (hope, humanity, love, memory, identity) | Replace with a concrete action/object; delete dialogue lines that state the message |
| 6 | **Generic characters** ("a young woman", "the mother") | Adam Heine: characters "defined entirely by predictable jobs", nobody remembers their names | No name, age, specific detail, opinion | Each character needs: 1 strange habit, 1 strong opinion, 1 source of shame |
| 7 | **Ideas look finished too early** | Reduces user ownership (48% vs 64% in the homogenization study), reduces elaboration | Long, polished output at the diverge step | Diverge with fragments/oblique ideas; develop only after the user chooses |
| 8 | **Scale inflation** (proposing an epic for 60s) | Scope mismatch | > 3 locations / > 3 characters / exposition | Apply principle 4 (beats ≈ runtime×2–3) |
| 9 | **Tech-first concept** | Technique runs ahead of the idea | Concept described through effects ("seamless morph transitions") | Write the concept without mentioning tools, then add "why AI" |
| 10 | **Default aesthetic** (cinematic teal-orange, epic lighting, "8k hyperrealistic") | AI baseline; no voice | Style described with generic prompt keywords | Style must have a specific reference + a reason tied to the idea |
| 11 | **Hedging/no point of view** | Programmers look for "voice" | Idea ends with a vague open ending "for the audience to interpret" with no choice made | The character must choose; the filmmaker must have a point of view on that choice |

**Automatic flag keywords (scan logline + concept):** humanity, what makes us human, consciousness, simulation, dream, wakes up, chosen, prophecy, destiny, dystopian, neon, cyberpunk, rain-soaked, last human, memories flood, infinite, universe, we are all, journey of self-discovery, finds herself, learns to love, AI, robot, android, glitch (when used as a reveal), ethereal, haunting beauty, epic, breathtaking. → Having a keyword ≠ automatic discard, but you must justify why it is not a cliché.

---

## 7. Gate checklist before locking the concept

**Story**
- [ ] Logline ≤ 35 words, passes Logline QC (4.1).
- [ ] The protagonist has a name, a specific want, a unique detail, and takes active action.
- [ ] Exactly 1 main turn; the ending image is defined and differs from the opening.
- [ ] The Pixar story spine can be filled in without breaking a "because of that".
- [ ] Scope fits the runtime (beat count), not a mini-feature.
- [ ] The 0–5s hook can be described as 1 frame.

**Originality**
- [ ] Does not hit the 6A banned list, or a subversion has been justified.
- [ ] The 2 closest works and the specific differences have been named.
- [ ] The user has confirmed the "personal truth"/reason for making this film.
- [ ] The initial shortlist had ≥ 4 different engines (proof of genuine divergence).

**AI feasibility & production**
- [ ] Avoid items = 0 in the main emotional beats.
- [ ] Every Weak item has a workaround (previs, framing, post overlay, style).
- [ ] Style has been chosen and has a reason (drift tolerance).
- [ ] #characters ≤ 3, #locations ≤ 3–5 (short), minimal dialogue or a voice/lip-sync plan.
- [ ] No likeness of real people/copyrighted IP.
- [ ] Estimated budget ≤ user budget (with a 30% buffer).
- [ ] Kill criteria are written and will be tested in skills 3/5 (visual bible, previs) before spending money on generation.

**Format-specific**
- [ ] Branded: the proposition emerges through the story; the mandatory list has been placed; logo/text done in post.
- [ ] Music video: the concept runs the full song (waveform map), with a transformation at the chorus/drop; artist approval.
- [ ] Social 9:16: the first frame reads on mobile both without and with sound.

**Rubric**
- [ ] Total ≥ 75, no veto (B ≤ 2, F = 1, A = 1).
- [ ] The user made the choice (not Claude on its own).

---

## 8. Practitioner quotes / heuristics (short, sourced)

- "Shorter is better… Don't try to do a mini feature." — Mike Plante, Sundance senior shorts programmer (Filmmaker Magazine). Films < 10 minutes ≈ double the chance; ~70 shorts selected from ~8,700.
- "Make it as short as it can be, while being as long as it needs to be." — Landon Zakheim, Sundance.
- "Authenticity and voice can be more compelling than throwing large budgets and great production value at empty storytelling." — Landon Zakheim.
- "Don't try to cram in a full three acts." — Adam Piron, Sundance.
- "If your film is over 20 minutes, it really has to earn it!" — Irene Suico Soriano, Sundance.
- "You have five seconds!" / "Safe is boring." / "Don't make a film that looks and feels exactly like other films you already enjoy." — Short of the Week, *15 Things Wrong With Your Short Film*.
- "For everyone else, it's just someone else's kid." — SOTW (a film more fun to make than to watch).
- Average length ~13 minutes at SOTW/Sundance/SXSW; 10–15' made up 40% of SOTW 2021. — SOTW.
- "It's not there yet, but it feels close." Criticized "self-referential navel-gazing", "grandiose faux-profundity". — Jason Sondhi, SOTW, on AIFF 2025.
- "The human — not AI — contributions often make all the difference." — Kyle Wiggers, TechCrunch, AIFF 2024.
- "I generated almost 700 clips… used about 55 or 56." / "If you're hitting the wall of the limitations of AI… go out and shoot it with a camera." — Paul Trillo (No Film School).
- "Discount the 1st thing that comes to mind. And the 2nd, 3rd, 4th, 5th." / "Why must you tell THIS story?" — Emma Coats, Pixar's 22 rules.
- "If you catch an idea… it might just be a small fragment. You gotta write that idea down right away." — David Lynch (via Austin Kleon).
- "If we go into that final meeting with three ideas we think are beautiful, but none of them land… that is a huge waste of time." — Maggie Malek, CP+B (The Drum).
- "If you cannot summarize tone and mood in 5-6 adjectives, your vision needs clarification." / "Write to the budget." — The Collective Pitch (MV treatment).
- "By saying what the story is not, you can come closer to succinctly summarizing what it is." — Save the Cat.
- "Same person, same face, same clothes for thirty seconds of video. No tool does this reliably." — Piero Perilli (2026).
- AIFF 2026 winners are all small stories with specific characters, often inversion/collision: Grand Prix *A Face Only A Mother Could Love* (7:51), Gold *THE WELL* (a rabbit investigates a wolf's death, 5:30), Silver *Where Knights Fall* (Rapunzel, 3:36), *Costa Verde* (a boy with his first camera), *TAIRELL ISN'T REAL* (an influencer declared "not real" by the internet). — hollywood.ai. **Heuristic:** award-winning AI runtimes 3:30–8:00; a specific 1-sentence premise.

---

## 9. Budget/time reality + Uncertain/conflicting info

### Budget heuristic (use for estimates in Step 0 and the one-page)
- **Seedance 2.5 pricing:** ~$0.10–0.12/s at 480p, ~$0.23/s at 720p (MindStudio); OpenRouter "from $0.1028/s"; Fastlane: $0.10–0.30/s depending on provider. Native 720p (higher resolutions via resellers are upscales).
- **Iteration ratio (seconds/clips generated per second/clip used):**
  - Social/B-roll 1.2–1.7×; Brand 1.7–2.5×; Narrative 3.3–5×; Broadcast/commercial 20–27× (TopVidTools, per clip).
  - Trillo (Sora, 2024): ~700 clips → 55 used ≈ 12–13×.
  - Suggested defaults for a pipeline with Blender previs + refs: **narrative 6–10×**, MV/montage 4–6×, branded hero shot 10–20×.
- **Formula:** `cost ≈ finished_seconds × ratio × $/s(720p) + draft pass 480p (~20–30%)`.
  - 60s narrative, ratio 8, $0.23 → ~$110 + draft ~$30 ≈ **$140/finished minute**.
  - Reasonable range: **$70–$300 / finished minute** (generation only; excludes Claude, voice, music, labor). TopVidTools gives ~$20–58/minute on cheaper/2025–26 models → lower than my estimate because of different model pricing.
- **Time:** Trillo ~6 weeks for 1 MV of ~4 minutes (1 person). The concept must be locked before spending money; every concept change after generation multiplies the cost.

### Uncertain / conflicting
- **Seedance 2.5 release date:** the brief says 2026-07-31; Fastlane: 07/31 (consumer apps) and 08/07 (API); OpenRouter: 08/07; MindStudio: "published August 12" (possibly the review article's date). → Treat as 07/31 consumer, 08/07 API.
- **Reference limits:** brief: 30 images + 10 videos + 10 audio; OpenRouter/Fastlane: "up to 50 combined" references. The total (50) does not conflict, but the allocation has not been verified against official documentation (the official English documentation is "fragmented").
- **Lip-sync/dialogue:** MindStudio notes speech has "subtle distortions"; no data on long lip-sync yet → keep long dialogue as "Weak/Avoid".
- **Crowds:** MindStudio praises 2.5 for handling crowd scenes well — conflicts with general experience (crowds are a weakness). → Background crowds: Weak (worth trying); meaningfully interacting crowds: Avoid.
- **Prompt adherence:** MindStudio: "poor prompt adherence requiring multiple attempts" → supports higher ratios than the TopVidTools figures.
- **TopVidTools yield rates** come from an aggregator with an unclear methodology; use them as orders of magnitude.
- **Optimal length:** PremiumBeat 6–12'; StudioBinder 5–10'; Sundance (Doe) ≤ 15'; SOTW average 13'. For AI shorts in practice 3–8' (AIFF 2026). There is no single "optimal" number.
- **Genre blending:** StudioBinder advises choosing 1 genre; but many award-winning AI films are tone collisions (*Editorial*: horror twist + deadpan). → Allow blending if there is a clear dominant tone.
- **Rubric weights** are my own synthesis, not an industry standard; AIFF uses 4 equally weighted criteria.
- **LLM diversity research** was measured on product ideas/general tasks, not film concepts; the effectiveness of persona+CoT for film concepts is an inference.

---

## 10. Sources (opened)

1. https://www.shortoftheweek.com/news/impressions-3rd-ai-film-festival/
2. https://firstscattering.com/p/a-short-review-of-the-runway-ai-film
3. https://www.premiumbeat.com/blog/3-reasons-short-films-get-rejected-from-festivals/
4. https://www.studiobinder.com/blog/writing-short-films/
5. https://www.shortoftheweek.com/news/15-things-wrong-short-film/
6. https://www.sundance.org/blogs/pep-talks-and-advice-for-makers-of-short-films-from-our-sundance-programmers/
7. https://filmmakermagazine.com/99583-shorter-is-better-sundance-programmer-mike-plante-offers-advice-on-short-film-strategy-at-the-sundance-next-festival/
8. https://www.shortoftheweek.com/news/how-long-should-i-make-my-short-film/
9. https://arxiv.org/pdf/2402.01536 (Homogenization Effects of LLMs on Human Creative Ideation)
10. https://arxiv.org/html/2602.20408 (Barriers to Diversity in LLM-Generated Ideas)
11. https://springboards.ai/blog-posts/worlds-first-llm-benchmark-for-creativity-finds-ai-tools-are-more-similar-than-you-think
12. https://www.mindstudio.ai/blog/seedance-2-5-review-pricing
13. https://openrouter.ai/bytedance/seedance-2.5
14. https://www.usefastlane.ai/models/seedance-2-5
15. https://topvidtools.com/ai-video-real-cost-yield-rate/
16. https://pieroperilli.com/en/blog/ai-video-generation-2026-what-actually-works
17. https://kling.ai/blog/limitations-of-current-ai-video-generation-technology
18. https://hollywood.ai/awards/runway-ai-film-festival
19. https://techcrunch.com/2024/05/11/at-the-ai-film-festival-humanity-triumphed-over-tech
20. https://www.techradar.com/ai-platforms-assistants/the-entries-for-the-2025-reply-ai-film-festival-prove-that-using-ai-doesnt-have-to-mean-the-end-of-creativity
21. https://www.aerogrammestudio.com/2013/03/07/pixars-22-rules-of-storytelling/
22. https://savethecat.com/tips-and-tactics/how-to-write-an-upside-down-logline
23. https://www.thedrum.com/insight/2023/08/25/tissue-sessions-can-help-fend-cheaper-rivals-just-ask-crispin-porter-bogusky
24. https://nofilmschool.com/ai-music-video
25. https://ppc.land/mastering-youtube-advertising-with-the-abcd-framework/
26. https://thecollectivepitch.com/blog/11-ways-to-write-a-winning-music-video-treatment/
27. https://www.adamheine.com/2026/07/critiquing-ai-generated-short-film.html
28. https://aivideoschool.substack.com/p/are-ai-films-the-same-as-ai-slop
29. https://austinkleon.com/2020/09/24/david-lynch-on-ideas/
