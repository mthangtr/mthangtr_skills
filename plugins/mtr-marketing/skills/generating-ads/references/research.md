# Phase 0 — Research (VOC, competitor ads, market)

**Goal:** replace imagination with evidence before any idea exists. Research supplies the two halves of effective creative: *relevance* comes from customer language, and *divergence* comes from knowing what competitors already say and show.

- **Output:** `research.md`, built from `templates/research.md`, checked by `scripts/research_check.py`.
- **Time box:** full mode 10–15 min; fast mode (deadline) about 5 min. Never zero.

| Item | Full | Fast |
|---|---|---|
| VOC verbatims (V##) | ≥20 | ≥10 |
| Competitor ads logged (A##) | ≥10 | ≥5 |
| Insight candidates (I##), each citing ≥2 evidence IDs | ≥3 | ≥2 |
| Synthesis: pains, objections, cliché zone, gaps, sophistication | required | required |

Every concept card later carries `"evidence": ["I01", ...]`. `scorecard.py --research research.md` kills concepts that cite nothing.

## 1. Order of operations

1. **User material first.** If the user is reachable, ask once for anything they already have. If they are unattended or unreachable, skip the question, write "user unreachable" in the header and continue. A stakeholder saying "we've done our homework" without documents counts as no material:
   - reviews, survey/NPS answers, support tickets, sales-call notes;
   - competitor names;
   - past ads, with results if known;
   - brand guidelines.

   This is the highest-quality evidence. Tag it `user` as the source.
2. **Product facts.** Read the brand site or landing page. Record what is true (features, price, guarantees) in `brief.md`, not here.
3. **Competitors.** Name 3–6. Include direct rivals, the substitute ("spreadsheets", "doing nothing"), and the category leader. Use `WebSearch` with queries like "best <category> app", "<brand> alternatives" and "<brand> vs".
4. **VOC mining.** Pull verbatims about the problem, your product and competitors (see §3).
5. **Ad research.** Log real competitor ads (see §4).
6. **Market notes.** Record pricing norms, seasonality and trigger moments (CEPs), category vocabulary and regulation.
7. **Synthesis**, then **insights** (§5).

If you have a subagent tool, run steps 4 and 5 in parallel, with one subagent each writing rows in the template format. You then merge the rows and write the synthesis yourself.

## 2. Access matrix and compliance

Tested from a cloud sandbox in Oct 2026; re-test in your environment.

| Source | WebFetch / WebSearch | Better route |
|---|---|---|
| WebSearch | ✓, but often titles + URLs only, no snippet text | Use it to find pages, then WebFetch them for verbatims |
| App Store pages (`apps.apple.com`) | ✓ ratings + review snippets | — |
| Competitor websites and landing pages | ✓ usually | — |
| Capterra, review roundups ("<competitor> reviews" blog posts), forum threads, trade press | ✓ often (best B2B VOC) | — |
| Google Play, G2, Trustpilot, Amazon, some App Store pages | Often errors or blocks | Browser tool, or user export |
| Reddit | Blocked | WebSearch snippets (`site:reddit.com <pain>`), browser tool |
| **Meta Ad Library** | **robots-disallowed** | Claude in Chrome (user's browser), or user screenshots/links |
| TikTok Creative Center Top Ads, Google Ads Transparency Center, LinkedIn Ad Library | JS-rendered: fetch returns an empty shell | Claude in Chrome, or user screenshots |
| Meta Ad Library API | Official, but needs a verified developer token. Commercial ads are returned mainly when delivered in the EU; no performance data | Rarely worth it for a single campaign |

**Compliance rule.** When WebFetch reports a site blocked or disallowed, do **not** fetch it another way: no curl, no Python requests, no headless Playwright, no caches or mirrors. The legitimate routes are:
- the Claude in Chrome browser tools, if they are connected (the user's own browser session, used interactively);
- material the user supplies;
- search snippets.

Record in the header what was tried and what was blocked.

**Fallback ladder for ads:**
1. Browser tool on the ad libraries.
2. User screenshots or links.
3. Competitor landing pages and social profiles: their own pages often reuse ad headlines and offers.
4. Articles or "swipe file" posts that show competitor ads (WebSearch: `"<competitor>" facebook ad examples`).

Mark rows from 3–4 with `days running = unknown`.

## 3. VOC: where and how

- **Query bank** (WebSearch to find pages, then WebFetch to read them; review roundups and forum threads quote real users):
  - `"<problem phrase>" reddit`, `site:reddit.com <category> "I wish"`
  - `"<competitor>" review "but"`, `"<competitor>" "switched to"`, `"<competitor>" "cancelled"`
  - `<category> complaints`, `"I hate" <task>`, `"nobody told me" <topic>`
  - App Store pages of the 2–3 biggest competitors: read the critical reviews (1–3★) for unmet needs, and the 5★ reviews for the outcomes people value.
- **Rules:**
  - Keep exact words in quote marks; don't paraphrase.
  - Tag every row. One row is one idea.
  - Prefer surprising phrasing ("it's like a second boss") over generic praise ("great app").
  - Mix sources: no more than half the rows from one site.
  - Note persona signals (job, life stage, tenure).
- **Use:** verbatims feed insights and headline language. A quote may appear *in an ad* only with permission and a real source (FTC Endorsement Guides). Otherwise it is inspiration, not a testimonial.

## 4. Ad research: what to log

For each competitor, in the browser tool or from screenshots:

- **Filters:** active ads, your country, all platforms.
- **Days running:** today minus "Started running on". Ads still running after more than 60 days are the best public proxy for winners, because advertisers kill losers. Many variants of one concept is another tell that the concept wins.
- **For each logged ad, record:**
  - archetype (ideation.md §3);
  - hook or headline (verbatim);
  - offer;
  - format (static, video, carousel);
  - visual world (UGC, product render, meme…);
  - CTA;
  - landing page promise.
- **Sample across competitors:** about 2–3 per competitor, newest plus longest-running. Don't take 10 from one brand.
- **Do not** copy executions. Extract the *mechanic* (e.g., "comparison table vs the old way") and the *gap*.

## 5. Synthesis → insights

- **Frequency count:** for each tag, which pains, objections and desires recur? Rank them by count and cite the V IDs.
- **Cliché zone:**
  - Any claim, visual or archetype seen in ≥3 competitor ads is cliché. Cite the A IDs.
  - This list *replaces* the from-memory cliché inventory in ideation.
- **Gaps:**
  - Lay the logged ads on the angle × archetype grid and list the empty cells that VOC says matter.
  - A gap with VOC support is the strongest concept seed there is.
- **Winning formats:** patterns among the long-runners (archetype, offer type, lo-fi vs polished).
- **Sophistication stage** (strategy.md §3):
  - Stage 1–2: few competitors make the claim.
  - Stage 3–4: everyone claims the benefit, so mechanisms appear.
  - Stage 5: claims are ignored, so identity and humour rule.

  Justify the stage with A IDs.
- **Insight candidates:**
  - Write each as a tension in customer words: "I want X, but Y gets in the way". Each cites ≥2 evidence IDs, ideally from two sources (a VOC pain plus a competitor gap).
  - An insight no competitor ad addresses is gold.
  - An insight that every competitor already addresses must be attacked from a new angle, not repeated.

## 6. Special cases

| Case | Do |
|---|---|
| No identifiable competitors (new category) | Research the *substitute* behaviour and the problem space. Use adjacent categories for ad formats |
| B2B | G2/Capterra (via browser or user), LinkedIn Ad Library, job posts and community threads for pain language. Use market notes for buying committees and objections |
| Local / small business | Google Maps reviews of local rivals (browser tool), their Facebook pages, local search ads |
| Brand has existing ads with results | Log them as A rows with real metrics in the Offer/Days cells. They outrank any proxy |
| No web and nothing from the user | Set Status: ASSUMED and list what was tried. Build the brief from first principles. The report states that every insight is unvalidated, and the test plan should prioritise testing *angles* |

## 7. Common mistakes

- **Summarising instead of quoting.** Paraphrase kills the specific language that makes headlines work.
- **Only reading competitors' 5★ reviews.** Unmet needs live in the 1–3★ reviews.
- **Logging ads without days running.** You can't tell winners from tests.
- **Copying a competitor's best ad.** It sits in the cliché zone by definition, and copying it is a legal risk.
- **Researching for an hour.** Respect the time box; thresholds are minimums, not targets.
- **Treating research quotes as testimonials** in the final ad.
