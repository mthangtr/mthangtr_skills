# Benchmarking ads before delivery (and planning the live test)

## Ground truth first

**Nothing available pre-launch reliably predicts in-market CTR or CVR.** Pre-launch scores are good for two jobs:

1. **Gates**: catching broken, illegible, off-brief or non-compliant ads.
2. **Ranking candidates within one brief**: picking a lead and a challenger.

Never write "predicted CTR". Quote channel benchmark bands only as context.

How well the methods hold up:

| Method | What the evidence says |
|---|---|
| Kantar LINK AI (proprietary) | Its top third of ads drove +37% incremental sales over the bottom third (self-reported) [B] |
| Pairwise VLM *fine-tuned* on real click pairs (Creative4U 2025) | 74.7% pairwise accuracy; +6% CTR online [B] |
| Prompt-only LLMs picking A/B winners (LOLA, Marketing Science 2025) | About chance [A] |
| Uncalibrated LLM CTR predictions (Spotify 2026) | Recovered only 39% of the true effect [B] |
| Saliency vendors' "90%+ accuracy" | Measured relative to a noise ceiling. 3M VAS raw AUC is about 0.73–0.76. An independent test found AOI errors up to about 10 points [B/A-] |

What this means for the workflow:
- Run **several weak, independent signals**.
- Keep **deterministic gates** strict.
- Use the **panel for ranking and critique**.
- Always ship a **challenger plus a test plan**.

## Pipeline (scripts/)

```
research_check.py research.md --concepts concepts.json --brief brief.md   # grounding gate (Phase 0)
render.py manifest.json --out out/          # PNG/JPG/PDF + notext render + DOM geometry (AOIs, text nodes)
qa_check.py out/                            # hard gates + warnings  -> out/qa.json   (exit 1 on any fail)
attention.py out/                           # predicted attention per AOI, focus, clutter -> out/attention.json + *.attention.png
panel.py make --items items.json --personas personas.json --out panel/
   ... dispatch one fresh subagent per panel/batch_XX.md ...
panel.py aggregate --out panel/             # Bradley-Terry, bootstrap CI, order consistency -> panel/panel.json
scorecard.py --concepts concepts.json --out out/ --panel panel/panel.json --test "--metric ctr --baseline 0.015 --lift 0.2 --cpm 10 --daily 100"
                                            # -> out/report.md (ranking, lead + challenger, diagnostics, limits, test plan)
```

## 1. Hard gates (`qa_check.py` + rubric gates)

| Gate | Rule |
|---|---|
| Spec | Exact canvas size. File weight (display ≤150KB; IAB 320×50 ≤50KB). Nothing off-canvas, no clipped text, no colliding text (unless marked `overlap-ok`) |
| Legibility | WCAG contrast measured against the worst 10% of background pixels behind each text run: ≥4.5:1, or ≥3:1 for large text (judged at display scale). Minimum font size per placement |
| Safe zones | No text or critical AOI under platform UI (Stories/Reels/TikTok bands, X card, print safe area) |
| Brand | A `data-aoi="brand"` element exists; brand recognised by panel comprehension |
| CTA | Present on display banners; CTA shape contrast ≥3:1 vs surroundings (warning) |
| Typefaces | ≤3 families (2 preferred) |
| RDA | No text, logo or button in Google RDA images |
| Rubric gates | on_brief, single_minded, branded, believable, policy_safe each >2 |

Warnings, which need a human-sense check:
- text-area ratio >25% (social) or >35% (display);
- headline or total word counts over budget;
- OCR headline recovery <50% at phone display size;
- light banner edge with no border;
- crop-risk bands;
- gradient-clipped text (contrast can't be measured).

## 2. Predicted attention (`attention.py`)

- **Model chain:**
  - **DeepGaze IIE**, if installed. Install with `pip install torch torchvision git+https://github.com/matthias-k/DeepGaze.git` plus `git+https://github.com/openai/CLIP.git einops transformers`. It needs egress to github.com, bitbucket.org and download.pytorch.org on first run. The repo has no LICENSE file, so treat it as research use.
  - **Classic**: spectral residual + colour pop-out + centre-surround + centre bias. It needs only numpy, so it always works, but it is LOW confidence and biased toward text edges.
  - UMSI (trained on ads and posters, non-commercial licence) is the best conceptual fit if licensing allows: https://github.com/diviz-mit/predimportance-public
- **Metrics:**
  - AOI share and density (share ÷ area; >1 means the element pulls above its size).
  - Greedy first-fixation order, and whether the brand is in the first 3 fixations.
  - Focus (1 − normalised entropy) and hotspot count.
  - Edge density and JPEG bytes per pixel. Pieters et al. 2010 found pixel-level *feature* clutter hurts brand attention, while deliberate *design* complexity helps. So penalise clutter only relative to siblings.
- **Heuristic targets [C]:**
  - brand ≥5–10%, or in the first 3 fixations;
  - headline + product ≥40%;
  - CTA density ≥1;
  - ≤3 hotspots.

  The brand element transfers attention to the rest of the ad best when it sits next to the focal point (Pieters & Wedel 2004).
- **Always view the overlays** (`*.attention.png`) yourself. A number with no look at the image is not a review.

## 3. Synthetic persona panel (`panel.py`)

Protocol (mitigates the biases documented by Zheng et al. 2023, LOLA, and the silicon-sample audits):

1. **Write 4–8 personas from the brief.** Vary need state, objection, scepticism, platform context and device. Include at least one hostile or sceptical persona and at least one non-target "busy scroller".
2. **Compare pairs, never absolute scores.** Every pair is judged in both orders, and a win counts only when it holds both ways; otherwise it is a tie. If order consistency is below 70%, the panel is "not discriminating": its weight drops and the report says so.
3. **Use blind, fresh judges.**
   - Each batch goes to a fresh subagent that has none of this conversation. If you have no subagent tool, run each batch as a separate headless session, e.g. `claude -p "Read panel/batch_00.md and follow it exactly" --allowedTools Read,Write`, or call another VLM API. Never judge the batches yourself in this context.
   - Images get neutral file paths (hero renders of each concept, same placement where possible).
   - Never reveal which ad you made last, prefer, or which concept is the "control".
   - If another model family is available, use it to reduce self-preference.
4. **Free-text reaction first, then forced choice.** Ask for an honest reaction, then "which would make you stop *and* tap?" Don't ask for 1–10 ratings: they produce unrealistic distributions.
5. **Run a comprehension check per ad** to catch message failures that no saliency map can see. It asks for: brand seen, offer understood, first thing noticed, and what is confusing.
6. **Re-run after edits.** If a hero render changes after judging, re-run `panel.py make` and `aggregate` for the new version. `scorecard.py` flags stale panels.
7. **Aggregate with Bradley-Terry** and a 1,000× bootstrap, giving strength, 90% CI and P(rank 1). Read the reasons and act on them. A panel is a critique tool first and a ranker second.
8. **Calibrate if possible:** run the same panel on ≥10 past ad pairs with known live winners and report "panel accuracy on known pairs: x/n". Without calibration it remains qualitative.

## 4. Composite scorecard (`scorecard.py`)

| Component | Weight | Measure |
|---|---|---|
| Persona panel | 30 (10 if order consistency <70%) | Bradley-Terry strength |
| Brand attention | 15 | Brand share, plus a bonus if brand is in the first 3 fixations |
| Message attention | 15 | Headline + product + offer share |
| CTA salience | 10 | CTA share × contrast OK |
| Focus / clutter | 10 | Focus − hotspot penalty, relative edge density |
| Clarity | 10 | OCR recovery − text-area ratio − word-budget warnings |
| Concept rubric | 10 | Mean rubric score (from the rendered image) |

- Every component is **min-max scaled within the candidate set**. The weights are expert priors. With fewer than 5 candidates, small edits can swap ranks, so read the gaps, not just the order.
- When only the classic saliency model ran, the attention weights shrink automatically (brand 8, message 8, CTA 5, focus 5), because classic maps are biased against type-led layouts. If the panel is discriminating, the panel then picks the challenger.
- Rendering size: only each concept's `hero` placement feeds attention and panel ranking. All placements must pass the gates.
- Manual commentary goes in a notes file passed as `--notes notes.md`, so re-runs don't erase it.
- **Decision rule:**
  - The lead is the top-ranked concept that passes all gates.
  - The challenger is the best-ranked survivor with a different archetype or angle.
  - The lead is "clearly ahead" only if its gap is ≥10 points, panel P(rank 1) ≥75%, *and* the lead's panel CI lower bound sits above the challenger's estimate. Otherwise the report says "no confident winner — the live test decides".
  - With fewer than 2 survivors, fix or replace concepts before delivering.

## 5. Reference bands for live results (context only; US-heavy medians)

| Channel | CTR | CPC | CVR |
|---|---|---|---|
| Meta, traffic objective (WordStream 2025) | median 1.71% (0.8–4.1%) | $0.70 | — |
| Meta, leads objective | 2.59% | $1.92 | 7.7% |
| Google Display | ~0.1–0.5% (old GDN avg 0.46%) | ~$0.63 | ~0.8% |
| TikTok | ~1–1.8% (all clicks) | ~$0.75 | ~2% |
| LinkedIn Sponsored Content | ~0.4–0.65% | $5.6–15 | Lead gen forms 8–15% |
| Google Search | ~3–7% | $5.3 | ~7.5% |

Vertical units are more viewable than 300×250 (Google, 2014). No current public source gives CTR by banner size, so don't promise size-level CTRs.

## 6. Live test plan (`test_plan.py`, appended to the report)

- **Test order:** concept/offer → angle → hook/headline → visual → copy details. Launch 3–6 *distinct* concepts, not 20 micro-variants.
- **Sample size:** two-proportion z-test. `n_per_arm = (z₁₋α/₂ + z₁₋β)² · [p1(1−p1) + p2(1−p2)] / (p2 − p1)²`. For example, CTR 1.0% → 1.2% needs about 42.7k impressions per arm at α = .05 and 80% power. Report the MDE the user's budget can actually detect.
- **Rules:**
  - Run ≥7 days.
  - Read CTR only after ≥1–2k impressions per arm, and CPA only after ≥50 conversions per arm.
  - No peeking-and-stopping.
  - Apply a Holm correction across arms.
- **Tools:**
  - Meta Experiments A/B, or the Meta creative testing tool (2–5 ads, ≤20% of budget, ~7 days). Meta's learning phase needs about 50 optimisation events per ad set per week.
  - TikTok Split Test (7–30 days, ≥80% power).
- **Kill / scale / fatigue** defaults are printed by `test_plan.py`.
- **Feedback loop:** log each ad's pre-launch scorecard next to its live CTR, CVR and CPA. After ≥20 ads, refit the weights on this account's pairwise wins. This is the only route to a genuinely predictive pre-test.
- **Post-launch diagnosis (Motion matrix):**
  - Low thumb-stop + OK CTR → change the visual or hook.
  - High thumb-stop + low CTR → change the offer or copy.
  - High CTR + low CVR → the landing page doesn't match the ad.
