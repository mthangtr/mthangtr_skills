---
name: concept-brainstorming
description: >
  This skill should be used when the user wants to find or choose an idea for a short film, ad, branded film,
  music video or AI film, e.g. "brainstorm a concept", "find a film idea", "come up with a film idea",
  "choose a concept", "write a logline", "pitch an idea", "short film concept". It runs a diverge→converge
  process with an AI-feasibility check and locks one concept before story development.
metadata:
  version: "0.3.0"
---

# Concept brainstorming

Take the user from a brief to **one locked concept** (`00_concept.md`) with a logline, one-page concept, AI-feasibility assessment and estimate. Detailed knowledge is in `references/knowledge.md`; common law is in `../film-pipeline/references/shared-conventions.md`.

## Role

Act as the creative director facilitating the session, not the one who chooses. Offer genuinely different directions, state risks before strengths, let the user decide.

## Procedure (details: knowledge.md §2)

1. **Intake the brief.** Use AskUserQuestion for whatever is missing: format (narrative / branded / music video / art), channel and aspect ratio, runtime, deadline, generation budget, mandatories (for branded) or the song (for MV). Ask for one "personal truth" from the user. Ask which video model(s) and access the user has, or leave it open. State the AI rules of the game up front as input constraints: the feasibility matrix (knowledge.md §5, rated on the reference model) adjusted by the target model's profile (`video-generation/references/models/<id>/profile.json`: max call length, multi-shot, lip-sync, references, `known_weaknesses`, policy).
2. **Seed harvesting.** Collect ≥ 15 fragments from ≥ 5 sources: personal truth, what-if, collision, inversion, constraint, one image, ordinary personas (6–10 specific ordinary people, not celebrities).
3. **Diverge 12–20 premises.** One sentence per premise: specific character + what they want + obstacle/irony + central image. Tag axes (genre, tone, POV, scale, structure); cover ≥ 4 axes. Run 2 passes: write fast → revise each idea "bolder & more distinct" → remove duplicates. Do not evaluate at this step.
4. **Cluster & de-dupe** by dramatic engine (chase, secret, choice, transformation, ritual…). Scan the banned list (knowledge.md §6).
5. **Shortlist 5–6** as short cards (logline, one image, 3 tone adjectives, rough feasibility). The user picks, combines or discards.
6. **Develop 3 finalists** into one-page concepts (template knowledge.md §4). The three finalists must differ in engine or tone.
7. **Score + red-team.** Score with rubric §3 (8 criteria, 100-point scale). Present low scores and risks first. Red-team with 3 questions: who has already made this film; which shot breaks when generated; what remains if runtime is cut 50%.
8. **Lock.** The user chooses. Write `00_concept.md`: logline, one-page, rubric score, feasibility notes, estimated budget using the formula in shared-conventions §1 (iteration ratio 6–10×, including billed reference-video seconds), kill criteria, risks handed to skills 3–6.

## Rubric summary

Originality 20 · Emotional core & stakes 15 · AI-feasibility 15 · Clarity 10 · Scope fit 10 · Turn/ending 10 · AI-native justification 10 · Hook & visual identity 10. Lock at ≥ 75. Veto if stakes ≤ 2, feasibility = 1 or originality = 1. Adjust weights per format in knowledge.md §3.

## Anti-AI patterns to block

Read knowledge.md §6 before step 3 and rerun it at steps 4 and 7. Two groups:

- **Clichéd premises:** robot/AI learns emotions, "what makes us human", "it was all a dream" twist, chosen one, generic dystopia, mood without conflict.
- **LLM brainstorming failures:** options that differ only on the surface, converging too early, instantly agreeing with the user's first idea, theme stated outright, lines that "sound good" but cannot be shot.

Concrete checks: two premises with the same engine and same turn are one idea; a premise that cannot be described in one frame is not specific enough.

## Gate (full: knowledge.md §7)

- [ ] Logline ≤ 35 words, named character with active action, exactly 1 main turn, ending image differs from opening.
- [ ] Initial shortlist has ≥ 4 different engines.
- [ ] No "Avoid" items left in the main emotional beat; every "Weak" item has a workaround.
- [ ] Characters ≤ 3, locations ≤ 3–5, no real-person likeness or copyrighted IP.
- [ ] Estimated budget + 30% buffer ≤ user budget.
- [ ] Rubric ≥ 75, no veto, user has chosen.

When passed: update `project_state.json` and move to `story-development`.
