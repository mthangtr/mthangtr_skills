---
name: generating-ads
description: Use when asked to create, design, brainstorm, refresh or pick advertising creatives — social feed/story/carousel ads, display banners, HTML5 ads, posters, OOH — or when asked which ad will perform or convert best.
---

# Generating Ads

## Overview

The ad people ship is usually the first idea, built once and judged by eye. This skill swaps that for evidence: insight-led concepts, a deliberately diverse set, and a benchmark the agent can actually run before calling anything final.

**Core principle:** effective creative is *divergent × relevant* (Rosengren 2020 meta-analysis). No pre-launch method predicts CTR. So generate wide, gate hard, rank honestly, and hand over a lead, a challenger and a live test plan.

**Iron law:** NO FINAL AD WITHOUT `out/report.md` FROM THE BENCHMARK, AND NEVER FEWER THAN 2 DISTINCT CONCEPTS PASSING GATES.

Motion or video versions: lock the concept here, then hand the concept card and key frames to the `making-motion-videos` skill (mtr-video).

## Workflow (each phase leaves a file)

| Phase | Do | Output | Read |
|---|---|---|---|
| 0. Research | Ask the user once (if reachable) for reviews, competitors and past ads. "We've done our homework" without documents means no material. Mine VOC, log real competitor ads with days running, take market notes. Write the synthesis (cliché zone, gaps, sophistication) and insight candidates. `research_check.py research.md` must pass | `research.md` (from `templates/research.md`) | references/research.md |
| 1. Brief | Fill every brief field. The insight quotes an `I##`; persona, objections and triggers cite `V##`. Label inferences "Assumptions". Classify awareness level and sophistication | `brief.md` | references/strategy.md |
| 2. Diverge | Write ≥15 concept seeds using ≥3 techniques, including gap mining. Drop the first 25% and anything in the cliché zone. Pick 3–5 that meet the diversity rules, one of them a wild card. Every card carries `"evidence": [I/V/A IDs]`, then run `research_check.py research.md --concepts concepts.json --brief brief.md` | `concepts.md`, `concepts.json` (cards + claims ledger) | references/ideation.md |
| 3. Build | Start from `templates/ad.html`. Recompose for each placement. Render, look at every PNG at full and thumbnail size, fix, re-render | `html/`, `manifest.json`, `out/*.png` | references/design.md, platform-specs.md, engineering.md |
| 4. Benchmark | `qa_check.py` → `attention.py` → panel (fresh blind judges: subagents, or `claude -p` per batch if no subagent tool) → score the rubric from the renders → `scorecard.py --research research.md --test … --notes notes.md`. Fix the gate failures and re-run until ≥2 concepts pass. Re-run the panel after editing a hero render | `out/report.md` | references/benchmarking.md |
| 5. Deliver | Export the lead and challenger in every placement. Write the platform copy fields. Present the report | `deliver/` | references/engineering.md |

All scripts live in `scripts/`. Run them with `python scripts/<name>.py --help`.

## Pressure cases

- **A stakeholder mandates one idea.** Build theirs as the *control*, fully crafted and shown first. Add ≥2 cheap challengers from other archetypes and benchmark all of them. Report the result neutrally.
- **Deadline.** Use the fast path, never skip phases:
  - research in fast mode, about 5 min (≥10 VOC, ≥5 ads, ≥2 insights; set `Mode: fast`);
  - still ≥15 one-line seeds (they take two minutes);
  - 3 concepts built in the hero placement;
  - gates, attention and a 3-persona panel;
  - all other sizes only for the lead and challenger.

  This takes minutes, not hours.
- **Sources blocked** (Meta Ad Library, Reddit…). Use the Claude in Chrome browser tools if connected, then user screenshots, then competitor landing pages and search snippets. Never bypass a blocked fetch with curl or a headless browser. With truly nothing, set `Status: ASSUMED`, and the report says so.
- **Missing assets or facts.** Use visible placeholders. Put every number, rating, review, price and deadline in the claims ledger. UNVERIFIED claims and missing assets go under "Required before launch". Never present a drawn product or an invented stat as real.

## Final message contract

Deliver these, in this order:

1. The lead and the challenger, with one line each on the concept and the insight it rests on (cite the `I##` and research status).
2. The scorecard table and the confidence statement from `report.md`.
3. The top fixes already applied, plus open diagnostics.
4. "Required before launch": assets, UNVERIFIED claims, CMYK/print steps.
5. The live test plan: arms, sample size and budget, kill/scale rules.
6. The validity limits sentence: pre-launch ranking, not a CTR forecast.

## Rationalizations (all mean: go back and do the step)

| Excuse | Reality |
|---|---|
| "The CMO said no alternatives" | Their idea becomes the control. Challengers cost minutes; the live test decides |
| "No time for a benchmark" | The whole pipeline runs in minutes. Unmeasured "best" is a guess |
| "I generated ideas in my head" | Unwritten ideas can't be checked for clichés or diversity. Write ≥15 |
| "I looked at it; it's clearly best" | Self-review is biased toward your own work. Gates plus a blind panel |
| "Numbers are illustrative" | They will ship. Ledger them as UNVERIFIED or remove them |
| "Safe zones are roughly 250/340" | Use the placement keys; QA checks exact bands |
| "Two headline variants = two concepts" | That's an iteration. Concepts differ in angle *and* visual world |
| "No subagent tool, so I'll judge the pairs myself" | You are not blind. Use `claude -p` per batch or another model's API; otherwise report "panel not run" |
| "I tweaked it after the panel; close enough" | The panel judged a different ad. Re-run it or label the result stale |
| "No time for research; the insight is obvious" | Obvious insights produce cliché ads. Fast mode takes about 5 minutes |
| "The ad library is blocked, so skip ads" | Use the fallback ladder: browser tool → user screenshots → landing pages → search snippets |
| "I know this category's clichés already" | Your memory is the cliché. The cliché zone comes from logged competitor ads |
| "The panel picked A, so A wins" | An uncalibrated panel is near chance. Report confidence and ship a challenger |

## Red flags — stop

- Writing a concept before `research.md` passes `research_check.py`, or a concept card with no `evidence`.
- Writing HTML before `brief.md` and the concept seeds exist.
- One concept, or concepts that share a layout and differ only in copy or colour.
- Saying "best", "highest-converting" or giving a predicted CTR without `report.md`.
- A judge subagent that knows which ad you prefer.
- Final files still holding placeholders that aren't listed as required.
