---
name: business-brainstorming
description: Validate startup ideas or discover high-potential market opportunities using a rigorous 6-block business framework. Use when user wants to brainstorm business ideas, validate a product concept, research market sizing TAM SAM SOM, analyze customer pain, competitive moat, ICP, unit economics, or produce a complete startup documentation file. Triggers on business brainstorming, idea validation, market research for startups, startup framework, product validation, no-idea market discovery.
---

# Business Brainstorming

## Overview

Produce a complete, evidence-based startup documentation file by systematically filling the 6-Block Framework. Supports two modes: (1) validate a user-provided idea, or (2) discover and rank market opportunities when the user has no idea yet. Always ground every claim in real research data.

## 6-Block Framework (Core Structure)

Every output document must cover these blocks in order:

1. **Market** — TAM / SAM / SOM (bottom-up preferred) + Why Now
2. **Pain** — Real pain intensity, frequency, current cost, evidence from users
3. **Solution** — Concrete approach + strict MVP Scope (Must-have only)
4. **Edge** — Moat + Positioning + USP + Competitive alternatives matrix
5. **Customer** — Persona → ICP (narrow) → Distribution channels
6. **Value & Economics** — Outcomes → Deliveries → Pricing → Unit Economics (LTV, CAC, LTV:CAC, payback) + Willingness-to-Pay evidence

Bonus section (required): **Key Assumptions & Risks** + **Validation Scorecard**.

## Operating Modes

### Mode A — Idea Validation (user provides an idea)
1. Clarify the idea in one sentence if needed.
2. Run deep research across all 6 blocks.
3. Score the idea honestly (see Validation Scorecard).
4. Highlight fatal gaps and recommended next experiments.
5. Output a full documentation file.

### Mode B — Opportunity Discovery (user has no idea)
1. Ask for constraints (industry preference, skills, capital, geography, B2B/B2C, etc.) if not given.
2. Research trending pains, underserved markets, and emerging Why-Now signals.
3. Generate 3–5 high-potential opportunity areas.
4. Score each against the 6 blocks.
5. Deep-dive the top 1–2 into full documentation files.
6. Recommend which one to pursue first and why.

## Research Protocol (Mandatory)

Always use available research tools aggressively before filling any block:

- Web search for market reports, industry data, competitor funding, search volume, trends.
- Browse specific pages (G2, Capterra, Reddit, LinkedIn, company sites, Statista summaries, etc.).
- Cross-check numbers from multiple sources.
- Prefer primary signals (user complaints, review gaps, search trends, hiring data) over pure analyst reports.
- For Pain and Willingness-to-Pay: mine real user language from Reddit, forums, review sites, Twitter/X, support tickets if available.
- Never invent market sizes or customer quotes. If data is weak, explicitly mark as “Low confidence – needs primary research”.

## Filling Methods (Scientific Approach)

### 1. Market
- Bottom-up: # of reachable ICP × realistic ARPU.
- Top-down only as sanity check.
- Why Now: technology shift, regulation, behavior change, funding wave, or cost curve.

### 2. Pain
- Look for frequency × intensity × current cost (time + money + emotion).
- Evidence hierarchy: observed behavior > stated complaints > surveys.
- Use Jobs-to-be-Done framing.

### 3. Solution
- Define the core job the product does.
- MVP Scope = only features required to deliver the primary Outcome for the ICP.
- Prefer Concierge / Wizard-of-Oz / Smoke-test paths when possible.

### 4. Edge
- Build a simple competitive matrix (direct + indirect + status-quo).
- Identify at least one credible Moat path (network, data, switching cost, process, brand, scale economies…).
- Write a clear Positioning statement.

### 5. Customer
- ICP must be narrow enough that you can name real people or companies.
- Distribution: list channels ranked by expected CAC and speed of learning.

### 6. Value & Economics
- Outcomes = measurable results the customer cares about.
- Pricing hypothesis grounded in current alternatives or value-based.
- Calculate rough LTV, CAC, LTV:CAC, payback. Flag if LTV:CAC < 3 or payback > 12 months.
- Willingness-to-Pay evidence: existing spend, pre-order signals, or strong interview language.

## Output Requirements

Always produce a single Markdown documentation file with this structure:

```markdown
# [Idea / Opportunity Name] — Business Validation Document

**Date:** YYYY-MM-DD
**Mode:** Idea Validation / Opportunity Discovery
**Confidence Level:** High / Medium / Low

## Executive Summary
(3–5 sentences + overall recommendation)

## 1. Market
...

## 2. Pain
...

## 3. Solution
...

## 4. Edge
...

## 5. Customer
...

## 6. Value & Economics
...

## Key Assumptions & Risks
(Top 5 assumptions ranked by risk)

## Validation Scorecard
| Block          | Score (1-10) | Evidence Strength | Notes |
|----------------|--------------|-------------------|-------|
| Market         |              |                   |       |
| Pain           |              |                   |       |
| Solution       |              |                   |       |
| Edge           |              |                   |       |
| Customer       |              |                   |       |
| Value & Econ   |              |                   |       |
| **Overall**    |              |                   |       |

## Recommended Next Experiments
(3–5 concrete, cheap tests ranked by learning value)

## Sources
(List all key URLs and data points used)
```

Save the file in the working directory with a clear name, e.g. `validation-[idea-slug]-[date].md`.

## Decision Rules

- If overall score < 6 or any critical block (Pain, Willingness-to-Pay, Edge) < 5 → recommend “Do not build yet”.
- If data is insufficient → list exact primary research needed (number of interviews, specific questions, smoke-test design).
- Always separate “What we know from research” vs “What still needs primary validation”.
- Be ruthlessly honest. Optimism bias kills more startups than lack of ideas.

## Constraints & Style

- Write in the same language the user is using.
- Keep the final document scannable (clear headings, tables, bullet points).
- Cite sources inline or in the Sources section.
- When generating ideas in Mode B, prefer problems that already show spending or intense workarounds.

## Example Triggers

- “Validate this idea: AI tool for X”
- “I have no idea, help me find a good B2B SaaS opportunity”
- “Research the market for [problem] and fill the full framework”
- “Build me the complete business documentation for this concept”
