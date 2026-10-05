# Market Research Protocol

Contents: Research questions · Query patterns · Worked example (Japanese-learning app) · Source ranking · Rules for numbers · research.md format · From research to decisions

The goal is the most complete, most accurate picture of the market this project enters: real numbers, real user behavior, real competitor moves. Every claim that shapes the strategy must trace to a page you fetched.

## Research questions

Answer all seven, then add questions specific to the product.

1. **Market size and trend.** How many people or companies have this problem in the target geography? Is the number growing? What drives the growth?
2. **User behavior.** What triggers the need? How do users look for a solution: which keywords, in which language, on which platforms? What do they use today? How often? When do they give up, and why? Is demand seasonal?
3. **Competitors and alternatives.** Direct competitors, indirect ones, and "do nothing / use a spreadsheet / hire someone". For each: price, positioning, platforms, ratings and review counts, estimated traffic or downloads, and how they acquire users.
4. **Voice of the customer.** Exact phrases users use in reviews, Reddit, Facebook groups, forums, and comments: what they love, what makes them quit, what they wish existed.
5. **Channels and audiences.** Named communities with member counts, creators and their audience sizes, publications, events, app store categories and rankings, search keywords with volume where available.
6. **Willingness to pay.** Competitor prices in local currency, free alternatives, typical budgets, payment methods users prefer.
7. **Constraints.** Regulation, platform policies, payment rails, or certification that affect GTM.

## Query patterns

- Search in every language the market uses: the user's language, English, and the language of the domain. A Vietnamese product for Japanese learners needs Vietnamese, English, and Japanese queries.
- Start broad, then narrow: `<category> market size <country> <year>` → `<official body> statistics <topic>` → the report itself.
- Go to primary sources: when an article quotes a number, search for and fetch the original report or dataset.
- Competitors: search the category plus "app", "pricing", "alternatives", "vs"; then fetch each competitor's pricing page and store listing.
- Behavior: `<category> reddit`, `why I quit <category>`, `<category> app review`, forum and Facebook-group threads in the local language.
- Seasonality: exam dates, fiscal years, holidays, hiring seasons, school calendars relevant to the ICP.
- Run at least two differently worded searches for any number that drives a decision.

## Worked example: a Japanese-learning app for Vietnamese learners

| Question | Example searches | Pages to fetch |
|---|---|---|
| Market size | `Japan Foundation survey Japanese-language education abroad Vietnam`; `số người học tiếng Nhật tại Việt Nam`; `JLPT applicants by country statistics`; `海外日本語教育機関調査 ベトナム 学習者数` | The Japan Foundation survey page, the JLPT official statistics page |
| Triggers | `Vietnamese workers Japan Japanese language requirement`; `du học Nhật Bản yêu cầu JLPT` | Official program or visa requirement pages, recent news on labor migration |
| Seasonality | `JLPT test dates Vietnam registration` | Official JLPT schedule and registration pages |
| Competitors | `app học tiếng Nhật tốt nhất`; each candidate name + `pricing` | App Store and Google Play listings (rating, review count, price), pricing pages |
| Why users quit | `r/LearnJapanese why did you stop`; `học tiếng Nhật bỏ cuộc vì`; 1–3 star reviews of the top competitors | Reddit threads, forum threads, review pages |
| Channels | `nhóm học tiếng Nhật facebook`; `kênh YouTube dạy tiếng Nhật`; TikTok creators teaching Japanese in Vietnamese | Group and channel pages showing member or subscriber counts |

Treat any competitor names you already know as candidates to verify, and search for the ones you do not know.

## Source ranking

Cite the highest tier available and record the tier as confidence.

1. **High:** government and statistics offices, official bodies (exam organizers, regulators), company filings, official pricing pages, app store listings.
2. **Medium:** industry reports with a stated methodology, established media, investor or analyst reports.
3. **Medium-low:** founder interviews, company blogs, operator essays.
4. **Behavior only:** Reddit, forums, Facebook groups, reviews. Use these for language, motivations, and complaints, never for market size.
5. **Leads only:** SEO "statistics" listicles and aggregators. Use them to find the primary source. Cite one only when no primary source exists, with confidence low.

## Rules for numbers

- Fetch the page and record the exact figure, the year of the data, the geography, and the definition (for example: "registered learners at institutions" is not the same as "people learning").
- Prefer data from the last two years; label older data with its year.
- Market size needs two independent sources, or one source plus a bottom-up estimate shown step by step (for example: learners × share using apps × share who pay × price).
- Separate the total market from the reachable market for the chosen channel.
- Third-party traffic and download numbers are estimates; label them that way.
- A number without a fetched source is `[estimate]` with its calculation, or it is removed.

## research.md format

```markdown
# Market research — <project> — <date>

| # | Claim | Number | Source (URL) | Publisher, data year | Accessed | Confidence |
|---|---|---|---|---|---|---|
| R1 | Japanese learners in Vietnam (institutions) | … | https://… | Japan Foundation, 2024 | 2026-09-28 | High |

## Conflicts
R3 vs R7: different definitions of "learner"; strategy uses R3 because …

## Gaps
Things searched for but not found, with the searches tried. Each gap becomes a user question or an experiment.
```

## From research to decisions

| Finding | Feeds |
|---|---|
| Where the ICP gathers, with audience sizes | Stage 0–1 tactic "go where they gather"; the first 100 users list |
| Channels competitors grow through | Product–channel fit evidence, or a crowded channel to avoid |
| Review complaints and quit reasons | Positioning, the wedge feature, onboarding and retention fixes |
| Price anchors and free alternatives | Pricing and channel–model fit |
| Search keywords and volume | Whether SEO or ASO is viable |
| Seasonality | Launch timing and the campaign calendar |
| Constraints | Channels or claims to rule out |