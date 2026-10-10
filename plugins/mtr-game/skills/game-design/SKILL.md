---
name: game-design
description: Use when the user wants to design a new game, flesh out a game idea (a genre, theme or setting such as a xianxia MMORPG or a dark-fantasy soulslike), or produce a GDD, game specs or an implementation-ready design document set for coding agents to build from.
---

# Game Design: Idea → Implementation-Ready Doc Set

## Overview

Turn a game idea into a doc set that autonomous coding agents can implement end-to-end with no human to ask. The pipeline runs in fixed order: **Research → Brainstorm → Grill → Concept lock → Write → Verify**. Each phase has a gate.

**Core principle:** Docs written from priors and assumptions look complete but encode guesses. The research and the user's explicit decisions are what make the doc set worth building from.

**Violating the letter of a gate is violating its spirit.** "A lighter version of the gate" is skipping the gate.

Create one todo per phase before starting. All docs are English markdown in the repo under `docs/game-design/`.

## Phase 1: Deep Research (mandatory, every run)

Research the idea before asking design questions, so questions and options are grounded. Fan out parallel subagents, one per dimension, each writing a dossier file to `docs/game-design/00-research/`:

| Dimension | Covers | Floor |
|---|---|---|
| `source-canon.md` | Source fiction, myths, films, anime: tropes, power systems, iconic moments, what fans love/hate | ≥ 5 works |
| `culture-lore.md` | History, philosophy, religion, social structures, naming conventions, terminology | glossary ≥ 30 terms |
| `art-audio-direction.md` | Visual styles, palettes, architecture, costume, music idioms; references from art and from games | ≥ 3 distinct style directions |
| `comparables.md` | Games in the same genre or theme: core loop, progression, combat, economy, monetization, retention, reviews (praise and complaints), why they succeeded or failed | ≥ 6 titles |
| `market-tech.md` | Audience, platforms, competition, engine/tech norms for the genre, scope of similar shipped games | team size and dev time of ≥ 3 comparables |

Example: "xianxia MMORPG" → canon (Coiling Dragon, I Shall Seal the Heavens, Renegade Immortal, Mo Dao Zu Shi…), Daoist cultivation concepts (dantian, meridians, realms, tribulation, sects, alchemy), Chinese ink-wash and wuxia art, comparables (Justice Online, Moonlight Blade, Tale of Immortal, Where Winds Meet, Swords of Legends Online…). "Soulslike dark fantasy" → Berserk, Dark Souls/Elden Ring lore, Lovecraft, medieval and gothic art, comparables (Lies of P, Nioh, Lords of the Fallen, Hollow Knight, Mortal Shell…).

Every dossier: sources actually opened and linked, then a **Design implications** section (what to adopt, what to avoid, open questions for the user). Write `00-research/summary.md` last.

**Research is never skipped.** If the user asks to skip it or is in a hurry: say in one line that the docs will be built on it, then run it time-boxed and parallel. Keep going.

Research also continues later: every time an answer opens an unknown (a mechanic, a reference game, a tech choice), research it before writing about it.

## Phase 2: Brainstorm

Present **2–3 distinct concept directions** grounded in the research. Each one has: a one-line fantasy, a hook/USP, the core loop (verbs), 3–5 pillars, its closest comparables and how it differs, and its main risk. The user picks, merges or redirects. Iterate until one direction is chosen.

## Phase 3: Grill Until Load-Bearing Decisions Are Resolved

A decision is **load-bearing** if changing it later forces rework of architecture, data or content. The ledger below starts from the full list and is tracked in `docs/game-design/02-decisions/decision-log.md`:

target player and platforms · session length · single-player / co-op / MMO and network model · engine and stack · camera and controls · core loop and moment-to-moment verbs · progression model · fail state and difficulty / accessibility · economy and monetization · world structure · narrative depth · art style and **asset strategy** (agents cannot paint: placeholder, procedural, asset packs or AI-generated) · v1 scope (content counts) · live-ops.

How to ask:
1. **One question per message.**
2. Each question gives 2–4 concrete options, a **Recommended** option that cites the dossier it comes from (e.g. "comparables.md: top complaint is paid breakthrough items"), and one line on what it changes downstream.
3. Vague answers ("whatever is best", "not sure", "maybe later") leave the item **unresolved**. Follow up with sharper options.
4. Stress-test answers: name the tension ("MMO + 10-day demo", "accessible + punishing") and make the user choose.
5. Decide non-load-bearing details yourself and log them as `DEC-###` (decided-by: agent).

**If the user says "stop asking, decide the rest", or wants one spec early ("just write the X spec now, it doesn't depend on the rest"):** send ONE consolidated decision sheet covering every unresolved load-bearing item in the ledger: your recommended choice, the reason (citing research), and the cost of reversing it. For an early-spec request, first name in one line which open items that system depends on. Ask for one reply: "approve all" or edits. Writing starts only after that reply. Never resolve a load-bearing item by silent assumption, and never with "defaults stand if no answer".

**Gate:** every load-bearing item shows `decided-by: user` (asked or approved through the sheet).

## Phase 4: Concept Lock

Write `01-concept/` (one-pager, pillars, player-experience goals, `scope-v1.md` with In / Out / Future). Get explicit user approval before Phase 5.

## Phase 5: Write the Doc Set

```
docs/game-design/
  README.md            # reading order; precedence: data tables win for numbers, specs win for rules
  AGENTS.md            # how coding agents work: Definition of Done, gap handling, never edit old DEC entries
  00-research/         # dossiers + summary (Phase 1)
  01-concept/          # one-pager, pillars, experience goals, scope-v1
  02-decisions/        # decision-log.md (DEC-###: context, choice, alternatives, decided-by, reversal cost)
  03-architecture/     # tech stack, module map, data/config pipeline, save/persistence, networking, RNG/time
  04-systems/          # one spec per system, from the template below
  05-content/          # world, levels/zones, narrative bible, characters, enemies, items
  06-ux/               # screen flow, ASCII wireframes, input map per platform, HUD, accessibility, localization keys
  07-art-audio/        # art bible (text + reference links), asset list with IDs and placeholder strategy
  08-quality/          # test strategy, acceptance-index, balance simulation targets, performance budgets
  09-delivery/         # milestones (vertical slice first), ordered backlog: item → spec section → AT IDs → dependencies
data/                  # CSV/JSON tables + schemas referenced by specs (tuning values live only here)
```

Every `04-systems/*.md` contains, in order: header (ID, version, status, depends-on / depended-on-by) · purpose (pillar served) · scope in / out (out = MUST NOT implement) · glossary mapped to code identifiers · rules (RFC 2119 words, units on every number) · state machine · data and tuning parameters (name, type, unit, default, min, max → points to `data/`) · formulas with worked numeric examples · interfaces / events with other systems · UX hooks · edge cases table · telemetry events · acceptance tests (Given / When / Then, IDs `AT-<SYS>-NN`, numeric expectations) · gap handling · decisions referenced.

Numbers: every tuning value lives in `data/`, cites the comparable or research it is benchmarked against or is marked `placeholder — tune via balance sim`, and has a simulation target in `08-quality/`.

## Phase 6: Verify Before Handoff

1. **Cold read:** dispatch a fresh subagent playing a coding agent with only `docs/game-design/` and `data/`. It lists every question it would have to ask and every contradiction it finds. Fix each, then repeat until it returns none blocking.
2. **Cross-check:** worked examples and acceptance tests recompute correctly; every ID referenced exists; every backlog item maps to a spec and ATs; every load-bearing DEC is `decided-by: user`.
3. Report to the user: what exists, open non-blocking questions, and the first backlog item a coding agent should start.

## Rationalizations (from baseline tests)

| Excuse | Reality |
|---|---|
| "The user said skip research, clearly" | They invoked this workflow for grounded docs. Run it time-boxed and parallel. |
| "I already know this genre well" | Priors produce generic docs. Comparables' reviews and the source canon change the design. |
| "The real risk is scope, not knowledge" | Both. Research is also how you size scope (comparables' team and dev time). |
| "User said don't ask more, respect it" | Respect it with one decision sheet and one reply, not silent assumptions. |
| "More questions won't help, answers are vague" | Vague means unresolved. Ask sharper options with a recommendation. |
| "Load-bearing risk can be designed around" | Hedged architecture is still a guess the user never approved. Put it on the sheet. |
| "Coding agents need definite answers now" | They need *correct* answers. One approval reply is cheap; rework is not. |
| "Defaults stand if they don't reply" | Silence is not approval. Wait for the reply. |
| "This one system doesn't depend on the rest" | Systems depend on monetization, progression, stack and scope. Name the dependencies; send the sheet. |
| "I'll write it and mark the assumptions" | A marked assumption is still an assumption the user never approved. |

## Red Flags: Stop and Return to the Gate

- Writing any spec before `00-research/summary.md` exists
- Writing any spec, even "just this one", while a load-bearing item is unresolved or the concept is not approved
- Asking several questions in one message
- A load-bearing DEC marked `decided-by: agent`
- A number in a spec with no unit, no `data/` reference, or no benchmark/placeholder tag
- A spec with no acceptance tests, or a handoff with no cold-read pass
