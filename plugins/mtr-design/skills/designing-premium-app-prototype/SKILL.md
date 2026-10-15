---
name: designing-premium-app-prototype
description: Use when designing or prototyping an app UI, dashboard, screen flow or landing page that should feel premium, minimal, monochrome, black-and-white, "expensive" or "like Linear/Vercel/Apple", or when an interface looks generic, noisy, text-heavy or AI-generated.
---

# Designing a Premium App Prototype

## Overview

Premium = **precision, not effects**. Hierarchy comes from type, space and contrast; feedback happens where the hand is; tools appear on intent. Every default you did not choose on purpose is the "averaged" look users read as AI slop.

**Process:** decide product → decide system → build screens → audit. Do not open a file before step 1 is written down.

## 1. Product: only what earns a screen

Write these down first, one line each:

- **The loop.** The 3–5 states a core object moves through (Draft → Ready → Building → Review → Merged for a spec; Imported → Uncategorized → Categorized → Reviewed for transactions). Screens map to states, not to database tables.
- **The decisions.** For each screen: which decision does the user make here? A screen with no decision is a panel, a disclosure or nothing.
- **One "Needs you" queue** on home: only items blocked on the user, each with ONE verb button (Review / Answer / Decide). Everything else is a list below it.
- **Effort reducers** (pick only ones that remove a whole step): AI asks one-keypress questions instead of the user writing; review by goal/criterion instead of by file; a decision made mid-flow writes itself back to the source; batch actions in ⌘K.

Must-have test: if removing a feature doesn't break the loop or a decision, cut it.

## 2. System: the defaults

Use these unless the brand or user says otherwise. Changing one is fine; leaving one unchosen is not.

**Theme.** Light by default. Dark only when the product lives in dark contexts (media, terminals) — then design it as its own token set, not an inversion; elevation = lighter surfaces, not shadows.

**Color (monochrome, no hue at all):**

| Token | Light | Use |
|---|---|---|
| bg | #FAFAF9 | rails, page ground |
| surface | #FFFFFF | content |
| sunk | #F3F3F1 | hover rows, code bg, added lines |
| line | #E7E7E4 | hairlines |
| line-strong | #D4D4D0 | inputs, secondary buttons |
| ink | #111110 | text, primary button, focus ring |
| ink-2 | #5C5C58 | secondary text (≥4.5:1) |
| ink-3 | #74746F | metadata only (≈4.5:1) |

Errors, destructive and diff states are told apart by **shape, sign, weight and border** (icon `!`, `+`/`−` gutter, border-strong), never by red/green. If a client insists on one hue, use it for errors only.

**Type — one face per role, not Inter/Geist/Roboto by default:**
- UI chrome: a grotesk with character (e.g. Schibsted Grotesk, Hanken Grotesk, Söhne, Neue Haas).
- Reading content (specs, docs, summaries, narratives): a serif (e.g. Newsreader, Source Serif). If the product has little long text, use the serif for page titles and the landing headline only. This alone separates the product from templates.
- IDs, code, amounts, dates: a mono with tabular figures (e.g. IBM Plex Mono).
- Scale with real contrast: 11–12 meta · 13–14 UI · 17–20 reading · 34–40 page title · 56–64 marketing hero only. Weights 400/500/600 only. Headings sentence case, tracking −0.01 to −0.02em. No uppercase tracked eyebrows.
- Signed values (money, deltas, diffs): `+` / `−` sign and weight, never green/red.

**Shape.** Radius 6 (controls) / 8–10 (cards). No pills for metadata. No shadows; popovers get a 1 px line border. No gradients, glass, glow, colored side borders.

**Motion.** 80–150 ms, `cubic-bezier(0.2,0,0,1)`. Spinners only for live work; respect `prefers-reduced-motion`. No bounce, parallax, marquee, shimmer, scroll reveals.

## 3. Interaction recipes

Build each of these exactly; they are where "premium" is felt.

| Moment | Recipe |
|---|---|
| Copy | Icon swaps copy → check for 1.5 s. Width never changes. No toast, no "Copied!" text. |
| Reversible destructive (delete, archive) | Act immediately; inline/snackbar "Archived · Undo ⌘Z" for 5 s. No confirm modal. |
| Consequential commit (anything that moves money, triggers work, ships, or sends outside: approve, merge, pay, send) | Hold-to-confirm 600 ms: a fill grows inside the button; release early cancels. Button then becomes the next state ("Building →", "Scheduled →"). |
| Background work finished | The object's status shape fills and it moves into "Needs you"; tab title shows the count "(2) App". Optional opt-in bell for notifications. No toast. |
| Save | Autosave. Header shows "Saving" → "Saved · 2s". No Save button. |
| Loading | Optimistic UI. Skeleton only if > 300 ms, static (no shimmer). |
| Form error | Validate on blur; field border → ink + `!` icon; one-line fix message. |
| Press | `:active { transform: scale(.97) }`. |
| Focus | 2 px ink ring, 2 px offset, `:focus-visible` only. |
| AI question | Dotted underline on the vague phrase; question in the margin with 2–3 chips + keys 1/2/3; answer rewrites the text, shows "Answered · Undo". |
| AI suggestion | Inline insertion highlighted in sunk + underline; accept Y / reject N icon chips. |
| Mid-process interrupt | Pause only the affected part ("AC-3 paused · the rest keeps going"); one question, chips; decision is written back to the source. |
| Status | Shape fills as the object progresses: dashed circle → ring → quarter → half → filled. Blocked/error = ring with `!`. Tooltip gives the word. |

## 4. Text budget

Remove, then compress, then hide — in that order.

- **Icon-only** is allowed for universal verbs in familiar positions: close, search, copy, link, more ⋯, edit, delete, settings, back, send, attach, panel toggle, notify. Each gets `aria-label` + tooltip (450 ms delay) that includes the shortcut: `Copy ID  ⌘⇧C`.
- **Label stays** on: the primary CTA, domain-specific verbs (Approve & build, Request changes), and the one verb button per "Needs you" row.
- Metadata as icon + number: `? 2`, `✓ 4/6`, `3h` (full timestamp in tooltip). Avatars instead of names. Counts instead of sentences.
- Empty state: one line + nothing else ("Nothing here."). Primary actions already exist in the header.
- Hover targets ≥ 32 px desktop / 44 px touch even when the icon is 15 px.

## 5. Hide with intent (progressive disclosure)

- Row actions: `opacity:0`, shown on `:hover` **and** `:focus-within`; always shown under `@media (hover:none)`.
- Overflow in `⋯`; every action also reachable in ⌘K; shortcuts surface only in tooltips.
- Text in tiers: primary always, secondary in ink-2, tertiary (IDs, files read, logs) behind a chevron disclosure.
- Side panels (agent chat, details) are toggleable, not permanent.
- Never hide the primary action of a screen.

## 6. Build the prototype

- Desktop web, 1440 wide, fluid: content `max-width` 640–960 depending on reading vs. list; rail 56 px icon-only nav that becomes a top row under 640 px.
- One artboard/page per state of the loop, linked so the flow is clickable (row → detail → approve → progress → review → home). Use a design-canvas artifact type when available; otherwise one self-contained HTML per screen.
- Make the recipes in §3 actually work (state + handlers), not just drawn.
- Add one **micro-interactions board**: 6–8 cells, each one recipe live with a 1-line caption.
- Real, specific copy and plausible data. No lorem ipsum, no invented stats.
- Real `<button>`, `<a href>`, `<label>`; 4.5:1 text contrast.

## 7. Audit before delivering

Go through every item; fix, then re-check. Ask of each element: **chosen or defaulted?**

- [ ] No Inter/Geist/Roboto-everywhere, no serif-italic accent word in a sans hero
- [ ] No hue (or exactly one, errors only); no gradient, glow, glass, colored side border, pill metadata
- [ ] No hero badge, three identical icon cards, stats row, logo marquee, 1-2-3 steps
- [ ] No toast for copy/save/approve; no confirm modal for reversible actions
- [ ] Every icon-only control has aria-label + tooltip with shortcut
- [ ] Hover-revealed actions also on focus and touch
- [ ] Each screen has one obvious decision; home has the "Needs you" queue
- [ ] Copy is specific to this product (a headline that fits any SaaS = rewrite)
- [ ] Dark mode, if any, is a separate token set

## Common mistakes

| Mistake | Fix |
|---|---|
| Geist/Inter + #0A0A0A dark by default "to feel like Vercel" | That is the Vercel-clone tell. Light, characterful grotesk + serif content. |
| Red for errors and delete | Icon + border + undo carry the meaning in monochrome. |
| "✓ Copied" label or toast | Swap the icon only. |
| Text labels on every button "for accessibility" | aria-label + tooltip covers a11y for universal icons; label only domain verbs. |
| Typed-name confirm for delete | Undo window. Reserve hold-to-confirm for commits that trigger work. |
| Shimmer skeleton on every fetch | Optimistic; static skeleton after 300 ms. |
| Feature list from the data model | Screens from the loop's states and decisions. |
| Trust-badge line under the hero ("256-bit · No ads") | Show the real product; one specific sentence. |
| Client says "like Vercel" so you go dark Geist | Deliver the feeling (precision, restraint, speed), not the clone; say so in one line. Dark only on explicit request. |
