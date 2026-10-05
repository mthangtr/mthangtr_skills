# GTM Benchmarks

Contents: PMF survey · Retention · NRR · Activation · CAC payback and LTV:CAC · ACV → GTM motion

## PMF survey (Sean Ellis, as run by Superhuman)

- Survey only users who used the core product at least twice in the last two weeks. ~40 responses give a directional result.
- Questions: (1) How would you feel if you could no longer use the product? very / somewhat / not disappointed. (2) What type of people would most benefit? (3) Main benefit you get? (4) How can we improve it?
- Threshold: ≥40% "very disappointed" ≈ PMF. Slack scored 51% (731 users, 2015).
- Improve it: segment by the "very disappointed" personas; ignore "not disappointed" feedback; among "somewhat disappointed", act only on those who share the main benefit. Split the roadmap 50/50: double down on what lovers love, fix what holds the others back. Superhuman: 22% → 33% by segmenting → 58% within three quarters.
- Implementation in code: a one-time in-app or email survey triggered after the second core action within 14 days; store answers with user segment and acquisition source.

Source: https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/

## User retention at 6 months (Lenny Rachitsky and Casey Winters, 20 growth experts)

| Product type | Good | Great |
|---|---|---|
| Consumer social | ~25% | ~45% |
| Consumer transactional | ~30% | ~50% |
| Consumer subscription | ~40% | ~70% |
| SMB/mid-market SaaS | ~60% | ~80% |
| Enterprise SaaS | ~70–75% | ~90% |

Lower is acceptable when just starting, when CAC and marginal cost are very low, or when not building a venture-scale business. Read cohort curves: a curve that flattens means a durable core; a curve sliding to zero means no PMF yet.

## Net revenue retention at 12 months

| Model | Good | Great |
|---|---|---|
| Consumer SaaS | ~55% | ~80% |
| Land-and-expand, very small businesses | ~80% | ~100% |
| Land-and-expand SMB/mid-market | ~90% | ~110% |
| Bottom-up SaaS (Slack, Figma, Zoom) | ~100% | ~120% |
| Enterprise SaaS | ~110% | ~130% |

Source: https://www.lennysnewsletter.com/p/what-is-good-retention-issue-29

## Activation

The aha moment is the early behavior that separates retained from churned users. Classics: Facebook 7 friends in 10 days; Twitter 30 follows; Slack 2,000 messages per team; Dropbox a file on a second device.

Find it: split day-30 retained vs churned users → compare first-7-day behavior → pick the behavior with the biggest gap → take its earliest cheap version → validate on a new cohort. Window: 1–7 days consumer, 7–30 days B2B. Segment activation by channel.

Source: https://inblog.ai/glossary/activation-rate

## CAC payback and LTV:CAC

CAC payback = CAC ÷ (monthly ARPA × gross margin). Use fully loaded CAC (salaries, commissions, tools, agencies) and gross profit, per channel and segment — blended numbers hide bad channels.

| Segment | ACV (USD/yr) | Median payback | Target |
|---|---|---|---|
| SMB / self-serve | < 15K | 8–12 months | < 12 months |
| Mid-market | 15K–100K | 14–18 months | 12–18 months |
| Enterprise | > 100K | 18–24 months | 18–36 months |

Under 12 months = reinvest aggressively; over 24 months = likely a structural problem. LTV:CAC ≥ 3:1 is the common floor, but payback is the more urgent number for a startup.

Source: https://www.saashero.net/strategy/cac-payback-period-b2b-saas/

## ACV → GTM motion

| Motion | Fits when | ACV (USD/yr) | Time to pipeline |
|---|---|---|---|
| Product-led | Self-serve signup, short time-to-value, large market | < 5K–10K | 3–6 months |
| Sales-led | Several stakeholders, demos, customization, procurement | > 15K–20K | 1–3 months |
| Marketing-led | Buyers research before buying | 5K–100K | 6–12 months |
| Partner-led | Part of a larger solution; geographic reach | ≥ 20K | 12–18 months |
| Community-led | Technical practitioners, open source | varies | 12–24 months |

Pre-seed/seed: one primary motion. Consumer products are product-led by nature; most B2B SaaS ends up hybrid (PLG acquisition, sales for expansion).

Source: https://upliftgtm.com/blog/gtm-motions