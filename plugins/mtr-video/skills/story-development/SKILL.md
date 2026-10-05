---
name: story-development
description: >
  This skill should be used when the user needs to turn a locked concept into a treatment, beat sheet or
  screenplay for a short film, ad or AI video, e.g. "write the screenplay", "write the script", "beat sheet",
  "treatment", "fix the dialogue", "punch up dialogue", "review the script", "Fountain script", "literary
  screenplay". It also marks rough [[UNIT]] blocks per scene; final unit grouping belongs to shot-design.
metadata:
  version: "0.3.0"
---

# Story development

From `00_concept.md`, produce `01_story/`: story spine, treatment, beat sheet, and `script.fountain` that has gone through 7 revision passes and a table read, with each scene split into rough `[[UNIT]]` blocks sized for the chosen video model (max call length from its profile; default to ≤ 15–20 s if the model is not chosen yet). Detailed knowledge: `references/knowledge.md`. Common law: `../film-pipeline/references/shared-conventions.md`.

## Procedure (knowledge.md §2)

1. **Read the input** from skill 1: logline, turn, ending image, AI constraints, runtime.
2. **Write a 5-line story spine** before writing the treatment.
3. **Treatment** of 0.5–2 pages, present-tense prose, describing only what can be seen and heard.
4. **Beat sheet** using the template matching the runtime (knowledge.md §3: 30 s, 60 s, 3', 10'). Total beat timecode = target ±10%.
5. **First draft** in Fountain (cheat-sheet §5). Write action lines in the order the camera sees them, each line ≈ one shot idea.
6. **Revision passes in order**, one goal per pass: P1 Structure (value change in every scene) → P2 Character (active protagonist) → P3 Dialogue (speaker identifiable with names hidden) → P4 Visual (delete unfilmable interiority) → P5 Anti-AI → P6 Trim (enter late, leave early) → P7 Production (split into units).
7. **Table read with TTS**: one voice per character, timed. If it deviates > 15% from beat timing, trim.
8. **Hand off**: script, beat sheet, list of characters/locations/props for skill 3, `story-gate.md`.

Present to the user after step 4 (beat sheet approval) and after step 7 (script approval). Do not write a full draft before the user approves the beat sheet.

## Core craft rules (knowledge.md §4)

- Every scene: who wants what, what blocks it, opening and closing values differ. Cut or merge a scene whose value does not change.
- Dialogue carries subtext. Characters do not announce their emotions. Replace any line of dialogue that can be replaced by action.
- Short-form: hook within 0–3 s; ads ≤ 85 words of dialogue/30 s; dialogue takes ≤ 60% of unit duration.
- The ending is an image, not a moral.

## Anti-AI writing pass (P5, mandatory)

Read knowledge.md §6 (21 patterns with grep list). Groups to block:

- Signature LLM phrases ("a testament to", "the weight of", "something shifted", "tapestry"), the "not X, it's Y" construction, decorative triplets, em dashes > 1/100 words.
- All characters speaking in the same fluent voice; symmetrical exchanges; therapy-speak; expository monologue.
- Tidy endings with a moral, hopeful montages, rain/whisper/silence clichés.
- Default LLM names (Elara, Kael, Thorne, Voss…): name characters from the film's specific cultural context.

Run the grep list, fix each hit per the fix column, then reread the full text. This pass also applies to every text in other skills that viewers will read.

## Adapting for AI production (knowledge.md §8)

- Write `[[UNIT n: start–end, speakers, camera]]` for each scene. Unit ≤ the model's max call length (profile `output.duration_s.max`); prefer 15–20 s for difficult scenes, or one shot per unit if the model cannot cut inside a call. Split at a beat, never mid-line.
- End each unit with a clear end state (pose, position, emotion) to prevent drift.
- ≤ 2 speakers, ≤ 3 clearly visible faces per unit; no overlapping dialogue; 1 language per unit.
- Rewrite risky actions per table §8.3: interiority, complex hand manipulation, long on-screen text, interacting crowds, multi-step physical chains, appearance changes within one shot.

## Gate (knowledge.md §9)

Every item in `story-gate.md` must pass: structure, character/dialogue, anti-AI (grep 0 unresolved hits), format (Fountain parses, table read deviation ≤ 15%), production (every scene has units, no unresolved risky actions). The user approves the script. Then move to `visual-bible`.
