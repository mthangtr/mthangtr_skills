# Strategy: brief, insight, awareness, psychology, policy

Evidence tags: **[S]** meta-analysis / large databank / official policy · **[M]** single study or large vendor dataset · **[P]** practitioner consensus.

## Why bother (what actually moves results)

- Creative quality explains ~47% of the sales lift from advertising; reach 22%, brand 15%, targeting 9% (Nielsen 2017) [M] https://www.marketingcharts.com/television-80662
- Effective creativity = **divergent (original) × relevant (appropriate)**. Either alone fails. Creativity works more through liking and "this brand made an effort" than through memory. It helps unfamiliar/challenger brands slightly more (Rosengren et al., J. Marketing 2020 meta-analysis [S] https://www.ama.org/2020/07/02/when-and-how-advertising-creativity-works/ ; Smith, MacKenzie, Yang et al., Marketing Science 2007 [S]).
- Emotional/fame campaigns are ~2× as likely to drive top profit growth long term; rational works for short activation (Binet & Field, IPA) [S]. Creativity pays most when **consistent over time** (IPA 2019) [S].

## 1. Brief (REQUIRED before ideation)

Fill every field. Infer missing ones from the request, then list each inference under "Assumptions" in the report. Only 6% of agencies say client briefs give clear strategic direction (IPA BetterBriefs) [M], so expect gaps.

| Field | Rule |
|---|---|
| Objective + funnel stage | Awareness (reach, recall, thumb-stop), consideration (CTR, LPV), conversion (CVR, CPA, ROAS) or retention. This drives the awareness level and the archetypes. |
| Audience | One primary persona: situation/trigger moment, current alternative, awareness level, main objection. On Meta Andromeda, *creative is the targeting*: write for a pain or persona, not an age bracket [P]. |
| Insight | A human tension in the customer's words: "I want X but Y gets in the way". It must be traceable to evidence (VOC, reviews, search, data). |
| Single-minded proposition (SMP) | One benefit, one sentence, customer side. Test: does it fit a 6-word headline? |
| Reasons to believe (RTB) | Max 3: mechanism, numbers, reviews, guarantee, awards. **Only facts supplied or verifiable.** |
| Brand assets / mandatories | Logo, colours, fonts, character, tagline, legal lines, offer terms. |
| Offer + CTA | Real offer and real deadline only. |
| Tone | 3 adjectives + 1 "not" ("witty, warm, confident; not snarky"). |
| Placements | List exact placements (see platform-specs.md). |
| Evaluation criteria | Set before ideation (benchmarking.md), so selection isn't taste. |

## 2. Insight mining

Done in Phase 0. See research.md for the method, sources, access workarounds and thresholds. The brief's **Insight** field must quote an `I##` from `research.md`. The **Audience** objection and trigger must cite V IDs.

Frameworks used there:
- **Message mining** (Wiebe/Copyhackers).
- **JTBD forces:** push, pull, anxiety, habit. Ads amplify push and pull, and defuse anxiety and habit with RTBs.
- **Category entry points:** one CEP per ad, rotated across the set (Ehrenberg-Bass).
- **Concrete customer language beats vague language** (Packer & Berger 2021).

## 3. Awareness level (Schwartz) → message and archetype

| Level | Lead with | Fitting archetypes | Product/price prominence |
|---|---|---|---|
| Unaware | Identity, curiosity, surprising fact, a CEP scene. Not the product | Visual metaphor, meme, anti-ad, stat shock, editorial look, founder story | Low (brand asset still visible) |
| Problem-aware | The pain, vividly, in their words; a hint that a fix exists | PAS panel, notes-app confession, relatable meme, before/after (where allowed) | Medium |
| Solution-aware | Why *this kind* of solution and why your mechanism is different | Feature callouts, mechanism diagram, us-vs-them, comparison table | Medium-high |
| Product-aware | Proof and objection handling | Review collage, testimonial, stat, press badge, FAQ/objection buster | High |
| Most aware | The offer: price, deadline, guarantee. Short | Offer-led, price anchor, bundle, real countdown | Highest |

The more aware the audience, the shorter and more direct the ad.

**Market sophistication** (how many similar claims the audience has heard). Classify it from the competitor scan [P]:

1. First to market: simple claim.
2. Second: bigger or more specific claim.
3. Claims exhausted: a **new mechanism** (how it works).
4. Mechanisms copied: an improved mechanism.
5. Jaded market: **identification**. Sell identity, brand world and humour, not claims.

If every competitor already claims your benefit, do not shout it louder. Move to mechanism (stage 3–4) or identity (stage 5).

## 4. Psychology (use ethically; test, don't assume)

| Principle | Static-ad application | Evidence |
|---|---|---|
| Processing fluency | One message, big type, high contrast, simple layout | [S] Alter & Oppenheimer 2009 |
| Distinctive brand assets | Same colour, logo, character and pack shot in every ad; uniqueness matters most | [M-S] Ehrenberg-Bass |
| Brand early and prominent | A brand cue in the first fixation zone. The DBA may be colour or product, not only the logo | [M] Google ABCD |
| Social proof | Real counts and ratings, named testimonials, "people like you" | [M] Goldstein et al. 2008. Fake reviews are illegal under the FTC 2024 rule [S] |
| Concreteness | Specific numbers, nouns, scenes, product in use | [M] |
| Anchoring | Genuine struck-through reference price, per-day cost, comparison to an expensive alternative | [S] effect; FTC deceptive-pricing guides |
| Loss framing | "Stop losing 3 h/week" vs gain framing: **test both** | [M, contested] Gal & Rucker 2018 |
| Scarcity / urgency | Only real deadlines and stock; fake timers are deceptive (FTC dark patterns) | [M]/[S] |
| Pratfall / honesty | Admit a flaw for credibility ("Ugly. Works.") | [M] |
| Risk reversal | Guarantee, free returns, cancel anytime next to the CTA | [P] |
| Emotion | Lead brand/awareness ads with a feeling (humour, warmth, surprise) | [S] Binet & Field; [M] System1, Kantar |
| Characters / fluent devices | A recurring mascot or scenario: +50% dwell time | [M] IPA/System1 |
| Attention ≠ effect | Thumb-stop only counts if the brand and message are taken away too | [M] Kantar |
| Faces + gaze | A face looking at the product or headline: ~4× more looks at the product | [M] Palcu et al. 2017 |

## 5. Claims ledger (REQUIRED)

Every number, rating, review, award, "#1", "clinically proven", price and deadline that appears in an ad goes into `concepts.json → claims[]` as `{"text": "...", "source": "<brief/url/user>" | "UNVERIFIED"}`. You may render a placeholder while designing. The report must list every UNVERIFIED claim under **Required before launch**. Never present an invented stat as real.

## 6. Policy pitfalls (check before the benchmark)

- **Meta personal attributes** [S]: never assert or imply that the viewer has a race, religion, age, sexual orientation, disability, health or medical condition, **financial hardship**, criminal record, etc.
  - ✗ "Are you struggling with debt?"
  - ✓ "Debt help from licensed advisors"
  - Generic "you" is fine.
  - https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes/
- **Meta health and appearance** [S]:
  - No before/after for weight loss.
  - No zoomed body parts.
  - No negative self-image.
  - No person on a scale.
- **Claims:**
  - Substantiate every objective claim.
  - Comparative ads must be truthful and verifiable.
  - Testimonials must be real and representative (FTC Endorsement Guides; Fake Reviews Rule 2024) [S].
- **Disguise formats** (notes app, tweet, news look):
  - No fake system buttons (play, close-X, download).
  - No fake publisher logos.
  - No implied endorsements.
  - Google disapproves ads that look like system warnings [S].
- **Sensitive categories** (credit, housing, employment, politics, alcohol, gambling, crypto, health, dating) carry extra rules. Flag them in the report and recommend legal review.
