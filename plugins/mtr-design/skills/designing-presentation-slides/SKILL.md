---
name: designing-presentation-slides
description: Use when creating, outlining, rewriting, or reviewing slides, a PowerPoint or .pptx deck, pitch, training or sharing session, or slidedoc (làm slide, thuyết trình, bài trình bày, chia sẻ nội bộ), especially when someone asks for "keywords only", titles read as topics or questions, bullets are fragments, or the deck will be emailed or read later.
---

# Designing Presentation Slides

## Overview

A deck is an argument written in complete sentences, then designed. Order of work: **big idea → storyline → copy → design.**

**Core principle:** someone who only reads the slides, without the speaker, still understands what is claimed, why, and what to do next.

**Violating the letter of these rules is violating the spirit.** "Concise" means fewer sentences, never broken sentences.

## Slide contract (every content slide)

Each slide IS exactly these parts, in order:

1. **Title** = one conclusion sentence (subject + verb + so-what) with at most one number, ≤20 words (count them). Reasons ("vì…", "để…", "nên…") go in the body. Never a topic ("Quy trình của team"), a question ("Code review mang lại gì?"), or a label ("Bug production: 15 → 38").
2. **Body** = 1–4 lines that prove the title. Each line is a clause with subject and verb, ≤20 words. A number always sits inside a sentence that says what it means.
3. **Source line** when the body has data: the source the user gave, or `[Nguồn: cần bổ sung]`.

Speaker notes add delivery detail; they never carry meaning the slide lacks.

| ❌ Fragment / topic | ✅ Contract |
|---|---|
| Bug lọt production | Bug lọt lên production tăng từ 15 (Q2) lên 38 (Q3) |
| QA quá tải → test không kịp → bug lọt | Một QA kiểm thử cho 8 Dev nên phần test bị cắt khi sát deadline |
| Khi bạn là reviewer | Reviewer nên trả lời PR nhỏ trong 4 giờ để PR không bị chờ |
| Bạn đang nghĩ gì về code review? | Code review là cách cả team cùng chịu trách nhiệm cho chất lượng code |

## Output: a .pptx file

The deliverable is a PowerPoint file (.pptx), unless the user asks for text only.

**REQUIRED SUB-SKILL:** Use the pptx skill (`anthropic-skills:pptx`) to build, validate, and visually QA the file. Where the two skills differ, this table wins:

| Topic | Use |
|---|---|
| Canvas | `pres.layout = "LAYOUT_WIDE"` (13.33" × 7.5") |
| Fonts | Calibri or Arial (render Vietnamese, ship with Office). Other fonts only when the user names them |
| Sizes, live deck | Title 28–32pt bold · free body text 20–24pt · sentence inside a card or under a stat 20pt · card/stat label 16–18pt bold · source and page number 12pt |
| Sizes, pre-read | Title 24–28pt · body 14–16pt · source 10–12pt |
| Title length | Sentence titles wrap to 2 lines; size the title box for 2 lines |
| Vertical fill | The content block spans the body area: from 0.3" under the title to 0.5" above the footer. Short content → larger chart, bigger numbers, taller cards with text vertically centered, or fewer, larger cards |
| Palette | Brand colors when the user gives them. Otherwise ask once for brand colors before building. If nobody can answer, pick the palette from the pptx skill's table that fits the topic and name it in the reply |
| Speaker notes | `slide.addNotes()`; delivery detail only |
| Visual element | Chart, big number, icon row, or comparison cards from the pptx skill. Each card or stat = short label + one full sentence under it |

### Workflow

1. Write the deck as data first: `slides.json` = `[{"title": "...", "body": ["..."], "source": "...", "notes": "..."}]`. Card labels go in their own field, not in `body`.
2. Run the copy check below on `slides.json`. Fix every flag (a before/after arrow such as "15 → 38" may stay) and rerun until clean.
3. Build the .pptx from `slides.json` with the pptx skill, as a structured deck.
4. Run the pptx skill's QA (validate.py, render to images, inspect every slide), then run `markitdown deck.pptx` and confirm the titles read in order as the story.
5. In the renders, an empty band taller than 1/4 of the slide below the content means the slide fails Vertical fill. Resize and re-render.

```python
# check_copy.py: python3 check_copy.py slides.json
import json, re, sys
words = r"tăng mạnh|rất nhiều|chữa cháy|tuyệt vời|đột phá|vô cùng"
title_flag = re.compile(r"[!?✔👉→↑↓]|" + words)
body_flag = re.compile(r"[!✔👉→↑↓]|" + words)
for i, s in enumerate(json.load(open(sys.argv[1])), 1):
    t = s["title"]
    if len(t.split()) > 20: print(i, "title > 20 words:", t)
    if len(t.split()) < 6: print(i, "title may be a topic, not a conclusion:", t)
    if title_flag.search(t): print(i, "title flag:", t)
    for b in s.get("body", []):
        if len(b.split()) < 5: print(i, "fragment:", b)
        if body_flag.search(b): print(i, "body flag:", b)
```

## Storyline

- Write the big idea first: one sentence <25 words, with stance and reason.
- Pyramid: big idea → 3–5 MECE key points → evidence. Each title summarizes what sits under it.
- Pick order by audience:
  - **Top-down** (answer first) for executives and decisions.
  - **Bottom-up** (context → evidence → conclusion) for skeptical or new audiences, training, sharing. Slide 1 or 2 must state the question the talk answers.
- Open with SCQA (Situation, Complication, Question, Answer). Close with a decision or next steps: who, what, by when.
- Write all titles first (ghost deck); reading them in sequence must tell the whole story.

## Neutral copy

- State facts and numbers instead of intensity words (tăng mạnh, rất nhiều, chữa cháy, tuyệt vời, đột phá, vô cùng).
- No "!", emoji, ✔, 👉, ALL CAPS, or →/↑/↓ standing in for verbs. "A → B" is allowed only for before/after values.
- Unmeasured benefits are labeled as targets or assumptions. Claims not in the data are cut.
- Source names, dates, owners, and deadlines come from the user. Missing ones become placeholders: `[ngày]`, `[người phụ trách]`, `[Nguồn: cần bổ sung]`.
- Parallel grammar across sibling bullets; one term per concept; expand acronyms on first use.

## Keyword pressure

When a manager, client, or time limit says "chỉ cần keyword", "đừng viết câu dài", or "anh sẽ nói": keep the contract, cut volume.

- Fewer lines per slide (1–2), shorter clauses, bigger numbers inside sentences.
- Notes are not a substitute: emailed decks and PDFs are read without notes.

| Excuse | Reality |
|---|---|
| "Sếp yêu cầu chỉ keyword" | The ask is brevity. A 10-word sentence is brief and survives forwarding. |
| "Lập luận nằm trong speaker notes" | Readers of the emailed deck do not open notes. |
| "Title đã là câu kết luận, body keyword cũng được" | Body fragments leave numbers without meaning. Body follows the contract too. |
| "Bài chia sẻ/đào tạo thì tiêu đề câu hỏi cho gần gũi" | A question title leaves the reader without the answer. State the answer. |

## Red flags: rewrite before delivering

- A title with no verb, or ending in "?"
- A bullet of 1–4 words, or a line built on arrows
- "Toàn bộ lập luận nằm trong speaker notes"
- Emoji, "!", or intensity words without numbers
- A title over 20 words
- A source, date, or owner the user never gave

## Design reference

### Layout
- 16:9 wide canvas, margins ≥0.5", 12-column grid. Title, body, footer (source, page number) fixed in the same place on every slide; build the slide master first.
- Left-align text. Center only title slides and single quotes. Keep whitespace; most important content top-left.
- CRAP: Contrast, Repetition, Alignment, Proximity.

### Typography
- Sizes and fonts: see the table in "Output: a .pptx file".
- Max 2 fonts; one family with several weights is enough. Line length about 50–75 characters.

### Color
- 1 background, 1 text color, 1–2 greys, 1 accent. Accent marks only what the title talks about.
- Color meaning stays constant across the deck. Contrast ≥4.5:1. Never color as the only signal.

### Charts
- Trend → line. Compare items → sorted horizontal bar. Composition → stacked bar. Change A to B → waterfall. No 3D; avoid pie.
- Remove chart junk; label directly instead of legends; accent only the data point the title names; always show unit, period, source.

### Images and motion
- Images must illustrate the point; one consistent icon set; animation only to build content in order (Appear/Fade).

## Final check (run, fix, then deliver)

- [ ] Titles only, read in order, tell the full story
- [ ] Every slide matches the slide contract
- [ ] Bottom-up decks state the guiding question on slide 1–2
- [ ] Ends with decision or next steps: who, what, when
- [ ] No red flags remain
- [ ] `check_copy.py` is clean, validate.py passes, every rendered slide inspected
- [ ] No rendered slide has an empty band taller than 1/4 of the slide
- [ ] Palette is the user's brand colors, or the reply names the palette chosen
