---
name: how-to-gtm
description: Use when the user asks how to take the current project to market, get its first users or customers, grow past a plateau, choose acquisition channels, position or price it, or plan a launch, size its market, or study its competitors and users — including Vietnamese phrasings such as "chiến lược GTM", "go to market", "tìm user đầu tiên", "growth cho project này" — or when /how-to-gtm is invoked.
---

# How to GTM

## Overview

A GTM strategy is only as good as the evidence behind it. Derive it from what this project actually is — its user, its price, its stage, and the channels its product can fit — never from a generic list of marketing tactics.

Three rules drive every recommendation:

- **Stage decides the tools.** Before product-market fit, growth is manual and founder-led. Scaling tools used before the stage gate burn money.
- **One primary channel per stage.** Distribution follows a power law: companies with product–channel fit get 70%+ of growth from one channel.
- **Products fit channels, prices fit channels.** The channel sets the rules; ARPU decides which CAC you can afford.
- **Real data, not guesses.** Market size, user behavior, competitor prices and channels come from sources fetched on the internet in this session, each with its URL. A number from memory is a guess until a source confirms it.

## When to Use

- GTM, launch plan, "how do I get users/customers", growth stalled, which channel, positioning, pricing tied to acquisition.
- Not for: writing one ad or one post (just write it), fundraising strategy, or pure pricing math with no GTM question.

## Process

### 1. Gather evidence from the repo first

Explore the repo the way its structure suggests, and look for each signal below. Record every finding with its file path; a signal you looked for and did not find is also a finding.

| Signal | Where it usually lives |
|---|---|
| What it does, for whom | README, landing page source, `docs/`, `CLAUDE.md` |
| Price and model | pricing page, payment code (Stripe, Paddle, PayOS, VNPay, MoMo…), plan configs |
| B2B vs B2C | org/workspace/team models, roles, SSO, seat billing |
| Network effects | invites, referrals, sharing, public profiles, two-sided roles (buyer/seller, host/guest, tutor/student), bookings, payouts |
| Stage and traction | analytics events, waitlist, onboarding, `CHANGELOG`, git history (first commit, recent cadence, contributors) |
| SEO/UGC potential | public routes generated from data or user content, sitemap |
| Prior GTM thinking | `docs/gtm/`, marketing folders, issues about launch or users |

Read environment variable names from `.env.example` or config code only; never open `.env` files or print secret values.

### 2. Fill the Context Card

Every slot is tagged `[evidence: path]` or `[assumption]`:

- **Product:** one sentence.
- **ICP:** who, pain, current alternative, where they gather, buying trigger.
- **Type:** B2C / B2B self-serve / B2B sales-assisted / marketplace / developer tool.
- **Price and ACV:** amount, or "free" / "unknown".
- **Network effects:** none / same-side / two-sided (name the hard side).
- **Stage:** 0 pre-launch · 1 pre-PMF (0→1K) · 2 PMF, searching for a channel (1K→10K) · 3 scaling an engine (10K→100K).
- **Stage evidence:** the observation that sets the stage.

Stage is set by evidence, not user count:
- PMF evidence = Sean Ellis survey ≥40% "very disappointed" among recently active users, or cohort retention curves that flatten. Without it, the stage is 0 or 1.
- Stage 2 = PMF evidence exists and no single channel yet delivers most new users at a stable CAC.
- Stage 3 = one channel or engine already works; the question is loops, a second engine, or ceilings.

Then ask the user at most 3 questions — only those whose answer would change the strategy — each with the default you will assume. If the user wants speed or does not answer, proceed on the defaults.

### 3. Research the market on the internet

The repo tells you what the product is. Only the market tells you how many people have the problem, how they behave, what they already pay for, and which channels already work. Research before choosing any channel.

Use WebSearch and WebFetch. When the Task tool is available, dispatch one research subagent per question in parallel, each returning findings with URLs. Follow `references/market-research.md`: it defines the research questions, query patterns in every relevant language, and how to rank sources.

A first run is complete when:
- every research question in the protocol has an answer or is listed as a gap;
- at least 15 searches were run and at least 8 pages were fetched and read (a search snippet is not a source);
- every competitor named in the strategy has its pricing and store or product page fetched.

Record findings in `docs/gtm/research.md`, one row per finding: claim · number · source URL · publisher and data year · access date · confidence. When sources disagree, keep both rows and state which one you use and why.

If no web tool is available, or the user asks to skip or shorten research, say so in the first line of the reply, tag every market number `[memory, unverified]`, and list the exact searches the user should run.

### 4. Choose motion, channels, engine

Read the section of `references/playbook.md` for the diagnosed stage, and `references/benchmarks.md` for thresholds. For every candidate channel, write one line of product–channel fit (why this product works in this channel) and one line of channel–model fit (can ARPU pay this CAC). Each fit reason cites at least one research finding: where the ICP gathers, which channels competitors grow through, price anchors, search demand, or seasonality. Select:

- Stage 0–1: 2–3 manual tactics from the seven-tactic menu.
- Stage 2: an inner circle of 3 channels to test cheaply, then one to focus on.
- Stage 3: one primary growth engine, its loop, and the trigger for adding a second engine.

### 5. Write the strategy

Save to `docs/gtm/strategy.md` unless the user names another path, and write in the user's language. The document is these sections, in this order:

1. **Verdict** — three sentences: the stage, the primary motion/channel, the one action for this week.
2. **Context Card** — from step 2.
3. **Market evidence** — market size and trend, target-user behavior, a competitor table (price, positioning, main channels, top review complaints), where the ICP gathers with audience sizes, and seasonality. Every number carries a `[R#]` reference to a row in `research.md`.
4. **Why this strategy** — evidence from the repo and the research → choice, plus at least two rejected alternatives and the reason each lost.
5. **30/60/90-day plan** — founder-sized actions, each with a weekly target number.
6. **Metrics** — one primary metric for the stage, 2–3 secondary, and the gate criteria for the next stage.
7. **Experiments** — up to 3, each with hypothesis, test, cost, success threshold, kill threshold.
8. **Product and code changes** — what the repo needs for this strategy (analytics events, PMF survey, onboarding to the aha moment, invite/referral, SEO pages), with the file paths where each would go.
9. **Assumptions and open questions.**

Close the chat reply with the verdict and the path to the file.

### 6. Check before saving

- Every chosen channel cites a Context Card fact in its fit reason.
- The stage claim cites evidence or is tagged `[assumption]`.
- Swap test: the document would not fit a different repo unchanged.
- Each Metrics and Experiments entry contains a number.
- Every market number has a `[R#]` reference, or is tagged `[estimate]` with its calculation shown.
- Every chosen channel cites at least one research finding.

### 7. Re-runs

If `docs/gtm/strategy.md` exists, read it first, compare against new evidence, update the affected sections, re-fetch any research row older than 90 days that drives a decision, and append a dated entry to a `## Changelog` section at the end.

## Quick Reference

| Stage | Primary metric | Main lever | Typical wrong move |
|---|---|---|---|
| 0–1 | PMF score, cohort retention | Founder recruits users by hand; 1 narrow ICP | Paid ads, big launch, growth hire |
| 2 | CAC and payback per channel | Bullseye testing, activation | Testing 6+ channels at once |
| 3 | Output of the main loop, NRR | One engine + loop, cross-functional growth team | Diversifying channels for its own sake |