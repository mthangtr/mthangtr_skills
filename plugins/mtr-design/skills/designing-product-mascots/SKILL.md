---
name: designing-product-mascots
description: Use when asked to design, explore, redesign or package a mascot, character, avatar or agent persona for a product, brand, app or AI agent; when asked for mascot variants or concepts; when a mascot looks generic, AI-made or "same as everyone"; or when a chosen mascot must become reusable assets to embed in apps, docs, slides and social.
---

# Designing Product Mascots

## Overview

A mascot is a **system**, not a drawing: a character DNA, a set of states, and a package other people can embed without asking you. The work has three gates, in order:

1. **Diverge** wide enough that the user has a real choice.
2. **Audit** every variant against AI-slop tells before the user sees it.
3. **Package** only the variant the user picked (or explicitly told you to pick), into the fixed file contract below.

**Violating the letter of a gate is violating its spirit.** "Quick demo", "they'll pick my favourite anyway" and "warm colours already avoid the AI look" are the three excuses this skill exists to stop.

Reply to the user in their language; file names, code and token names stay English.

## When to Use

- New mascot / character / avatar / agent face for any product
- "Give me options", "make it less generic", "it looks AI-generated"
- Turning an existing or chosen mascot into an embeddable kit
- Adding states (thinking, working, error…) to an agent's avatar

Not for: logos without a character (use a logo/brand process), illustration scenes, photoreal avatars of real people (refuse impersonation).

## Phase 0 — Brief (max 5 questions, then go)

Ask in one message, or — if the user is absent or in a hurry — assume and **write the assumptions at the top of the contact sheet**:

| Slot | Why it changes the design |
|---|---|
| Product + who uses it (locale, age, B2B/B2C) | Metaphor pool, cultural references, tone |
| Mascot's **job**: identity among many agents / status of background work / trust at onboarding / brand & social | Decides whether states are mandatory (they are for any AI agent) |
| Surfaces: app sidebar (24–32px), docs, slides, social, merch | Minimum-size constraints |
| Existing brand tokens (colours, type) | Palette strategy; never invent over an existing brand |
| Sensitive domain (money, health, kids, legal) | Pull toward abstract / matter-of-fact; ban baby-schema extremes for 18+ products |

## Phase 1 — Diverge: the Variant Matrix

Anti-slop rules only remove the bad. Uniqueness comes from four things this phase forces: a **competitive exclusion list**, **concepts with a twist**, **many cheap thumbnails before any detailed drawing**, and a **swap test**.

**Step 0 — Competitive scan.** Search the web for 8–12 mascots: the product's direct competitors, its category, and the current big-tech agent mascots (Meta Jolly, OpenAI dots, Grok Bot, Copilot Mico, Notion faces, Duolingo Duo). Write one row each: archetype · shape · palette · face system. This table is the **exclusion list**: no variant may match any row on 3+ of those 4 columns.

**Step 1 — Mine two layers.** Write both lists before any concept:

- *Objects* (20+): nouns, tools, places, local cultural objects from the product's world. Café bookkeeping → receipt spike, phin filter, abacus, ice cube…
- *Truths* (10+): behaviours, tensions, insider jokes, small rituals of the users and of the work itself. → "owners count cash at 11pm with one eye closed", "the receipt drawer that never closes", "regulars who pay next week".

Tech words (brain, chip, spark, bot, orb, circuit) are banned from both lists.

**Step 2 — Concept cards (12+).** Combine one object (or archetype) with one truth. Each card has exactly these fields:

| Field | Example |
|---|---|
| Name | Thạch |
| Metaphor | house gecko on every café wall |
| Twist — an unexpected behaviour or trait drawn from a truth | clicks its tongue three times when the books balance (Vietnamese folk: gecko clicks = luck) |
| Job link — how the twist shows what the product *does* (not just where it lives) | the tongue-clicks are the "books balanced" signal; the sticky toes are "nothing gets lost" |
| Signature detail people will retell | toe pads that stick a receipt to any surface |
| One-line backstory | lived behind the cash drawer for 12 years, has seen every unpaid tab |
| Swap test | Rename the brand to its closest competitor. Does the card still fit equally well? Yes = generic, rewrite the twist |

A card without a twist, without a job link, or one that passes the swap test for a competitor, is cut. Local colour alone is not a concept: a mascot that says "Hanoi" but not "dispatch" fails Fit.

**Step 3 — Thumbnails (24+).** For the surviving cards, draw rough **black silhouettes only** (no face, no colour, 64px cells, 2–3 per card with different poses or shape languages) on one thumbnail sheet. If an image-generation tool is available in the session, it may be used here for rough exploration; nothing from it ships without being redrawn as SVG. Pick the 6 strongest by: silhouette readable at 64px, distinct from each other and from the exclusion list, twist visible in the pose.

**Step 4 — Fill the matrix.** The picked thumbnails become the variants: **6** by default, or the number the user names. Swap a pick for the next-best thumbnail when the matrix needs it. Every pair of variants must differ on **at least 3 of these 6 axes**, and across the set each axis must take at least 3 different values:

| Axis | Values to spread across |
|---|---|
| Archetype source | animal · object/tool · abstract shape · invented creature · glyph/letterform · material/substance · no-face (pure form + motion) |
| Shape language | round/soft · square/stable · triangular/kinetic · irregular/organic · modular (assembled parts) |
| Face system | no face · eyes only · one eye/profile · eyes as negative space · face in an unexpected place · full face (max 1 variant) |
| Rendering style | monoline · flat cut-paper · risograph 2-colour with offset · pixel grid · geometric construction · ink-brush/hand-wobble · stencil/stamp · bold blocks with no outline |
| Palette strategy | from brand tokens · single colour + black · 2-colour print · high-contrast duotone · local/cultural palette · material-native colour |
| Personality (Buck axes) | figurative ↔ abstract × matter-of-fact ↔ feisty — place each variant, spread over all 4 quadrants |

Required inside the set: **1 wildcard** (the option you'd least expect to win), **1 no-face or eyes-only option**, **1 option that survives as a 16px glyph**.

Write the matrix as a table (variant × 6 axes + a **"states via"** column saying which part moves for thinking/working/waiting) **before** drawing. If two rows share 4+ values, change one before drawing it.

**Rendering for review:** look at variants as a browser renders them — headless Chromium via Playwright (`page.set_content(svg)` → `screenshot`). cairosvg is only a parse check: it silently drops filters and masks, so a cairosvg PNG does not show what users will see.

**Step 5 — Draw.** Author each variant as SVG (viewBox `0 0 512 512`). For anything beyond a few shapes, write a small parametric generator (`build/<slug>.py` that emits the SVG) so craft passes and later poses change parameters, not hand-edited paths. Use the **group contract** (needed later for states); the ids are fixed, their order in the file is free (an accessory may sit behind the body):

```
<g id="m-body"> … </g>      main mass
<g id="m-face">              (empty group allowed for no-face variants)
  <g id="m-eyes">…</g>
  <g id="m-mouth">…</g>      (optional)
</g>
<g id="m-acc"> … </g>        accessories / props
<g id="m-fx"> … </g>         marks, motion lines, stamps (optional)
```

SVG gotchas found in testing: a pose tilt goes on an inner `<g>` inside each contract group (CSS state transforms override a transform attribute on the group itself); a dark-mode paper rim is a geometric copy of the outline drawn behind, not a `feMorphology` dilate filter (it washes out at 16–32px); riso `mix-blend-mode: multiply` needs `isolation: isolate` on the root; silhouettes are separate rim-free copies, not a CSS `brightness(0)`.

No `<text>` in mascot art: letters are drawn as paths or omitted. No external fonts or images. A wobble filter (`feTurbulence`/`feDisplacementMap`) goes on the root `<svg>` or inside each contract group, never on a wrapper around them (it breaks state animation).

**Step 6 — Craft pass (every variant, twice).** Render to PNG, look at it, then redraw against this bar. Divergent but crude is still slop.

| Check | Pass when |
|---|---|
| Silhouette | Black-filled shape is recognisable as *this* character, not "a square" or "a snake" |
| Size contrast | Clear big / medium / small parts (≈ 60 / 30 / 10); no parts of equal weight |
| Line of action | One readable curve or lean through the body; not stiff and frontal unless that is the concept |
| Construction | Consistent stroke weight; overlaps are intentional; joints and contacts actually touch |
| Appeal | You would put it on a sticker or a plush; one specific detail people will remember |
| Expressiveness | The "states via" part can visibly change pose at 48px |

A variant that fails 2+ checks after the second pass is replaced, not shown. The same pass runs again on the chosen variant after every change request ("make it less like X").

## Phase 2 — Anti-Slop Audit (gate before the user sees anything)

Score every variant. **Any P0 = redraw it before presenting.** Two or more P1 = fix or justify in one line on the contact sheet.

| Sev | Tell | What it looks like | Fix direction |
|---|---|---|---|
| P0 | AI-tech cliché | robot, brain, chip, circuit lines, sparkle ✨, glowing orb, chat-bubble head, antenna | Go back to the metaphor list |
| P0 | AI palette | purple→blue / cyan-on-black gradients, neon glow, gradient fills on the body | One dominant colour + one sharp accent, flat |
| P0 | Kawaii template | dot eyes + arc smile + blush circles + stick limbs, frontal and symmetrical | Change the face system axis; asymmetry; drop blush |
| P0 | Object-with-a-face | an existing object with the kawaii template stuck on (receipt with face, bean with face) | Transform the object (its parts become anatomy) or pick another archetype |
| P0 | Style monoculture | all variants share stroke weight, palette and rendering style — only the concept differs | Re-run the matrix: rendering style must take ≥3 values |
| P0 | Placeholder craft | rough SVG built from primitive rects/circles, limbs that don't connect, equal-weight parts — reads as stand-in art | Craft pass (Phase 1 Step 6) |
| P0 | Swappable | passes the swap test for a competitor; no twist visible in the art | Back to concept cards |
| P0 | Category collision | matches an exclusion-list row on 3+ columns | Change archetype or shape language |
| P0 | Glossy 3D render look | Pixar/clay sheen, subsurface glow, multiple eye highlights, soft studio shadow, Funko proportions | Flat or print-based rendering; one highlight max |
| P1 | "Tasteful default" palette | cream/beige + espresso brown + terracotta red, or untouched zinc/slate | Derive palette from brand or locale, not from "warm = safe" |
| P1 | Corporate Memphis | lilac/coral blobs, tiny heads, noodle limbs | Different proportions; heavier forms |
| P1 | Mascot-industry default | Labubu/Fall-Guys bean, fluffy egg, blobby Pixar critter (the 2026 Jolly/dots gravity well) | Push the shape-language axis to square/triangular/modular |
| P1 | Text in the art | brand name, "PAID", labels inside the character | Remove; text lives beside the mascot, never in it |
| P1 | Dark-mode loss | body or outline vanishes on a dark background | Add a light keyline / paper rim, or a dark-mode colour pair in tokens |
| P1 | Size collapse | unreadable at 32px, or two variants identical as silhouettes | Simplify; test silhouette (black fill) |
| P2 | Decorative motion | bounce/elastic easing, pulsing dot when nothing changed | Motion only for state changes |
| P2 | Centered-on-gradient presentation | variant shown on a soft gradient or glow | Present on flat light AND dark backgrounds |

Record the audit as a row per variant: `P0: none · P1: tasteful-palette (kept: brand colour) · silhouette OK at 32px`.

**Blind judge (after the audit, before the user).** The author is the worst judge of its own work. If the session can start a subagent, give it only the rendered variants (PNG, no names, no rationale, no audit) plus the one-paragraph brief, and ask it to score each 1–5 on:

- **Originality** — "I have not seen this mascot before, and a competitor could not use it"
- **Appeal** — "I'd want it as a sticker; it has a memorable detail"
- **Fit** — "It obviously belongs to this product and its users"
- **Craft** — "It looks finished, not like stand-in art"

plus, per variant, its first read ("what is this?") and what existing mascot or cliché it reminds it of. Any variant with Originality, Fit or Craft below 3, whose first read is a different object than intended, or that the judge says "reminds me of <existing mascot>", goes back to Step 5. Show the judge's scores on the contact sheet. No subagent available → do the same scoring yourself in a separate pass, looking only at the PNGs, and label it "self-judged".

## Phase 3 — Present, then gate on the pick

Build one **contact sheet** (single HTML page; publish it as an artifact when the session can): per variant —

- the art at 256px on light and on dark background
- the same at 32px and as a black silhouette at 32px
- name, its concept card (metaphor, twist, signature detail, backstory), its 6 axis values, its audit row, the blind-judge scores
- assumptions from Phase 0 and the exclusion list at the top; the thumbnail sheet linked at the bottom

Say plainly on the sheet that code-drawn SVG is concept fidelity: the concept, silhouette, states and system are final-quality; the line work can be handed to an illustrator (give them the concept card, construction sheet and group contract) without redoing the system.

Then ask the user to **pick one, or remix** ("A's body + D's palette + C's face system"). What happens next depends on one observable fact — what the user has said in this conversation:

- **User named a variant or a remix** → Phase 4.
- **User explicitly delegated the choice** ("just package your favourite", "you choose") → show the contact sheet anyway, state your #1 and why, then Phase 4 on #1. Name the runner-up so they can swap.
- **Neither** → rank your top 2 with reasons and stop at the contact sheet. A request for options is not a delegation.

## Phase 4 — Refine the chosen variant

1. **Construction sheet:** proportions on a grid (body : head : eye ratio), stroke weight, colour tokens, clear space = height of `m-eyes`.
2. **Icon cut:** a simplified version that reads at 16 and 24px (fewer parts, thicker strokes, its own tighter viewBox crop allowed — not a scaled-down master).
3. **Expressions (rest):** neutral, curious, pleased, concerned, sleepy — made by changing parts inside `m-eyes`/`m-mouth`/`m-acc` only (alternate eyelids, pupils, mouths as hidden sub-elements toggled by class), never by redrawing the body. Each expression must differ from neutral in **at least two parts** (e.g. eye + accessory angle) so they read at 64px; if the face is tiny, state the minimum readable size in GUIDELINES.md.
4. **Agent states** (mandatory for any AI agent; optional otherwise):

| State | Meaning | Motion (CSS, on the group contract) |
|---|---|---|
| idle | nothing needs you | slow breathe on `m-body` (scale 1→1.02, 4s), blink every ~5s |
| thinking | planning | `m-eyes` glance left/right |
| working | doing the task | steady loop on `m-acc` or `m-fx` (no bounce) |
| waiting | needs approval/input | motion stops, eyes face the user, badge colour = attention token |
| error | blocked / failed | neutral-concerned face, no comedy, no shake longer than 300ms |
| done | finished | one settle beat, then idle |

At `waiting` and `error` the mascot never jokes and never pressures — permission and payment screens get a neutral mascot or none.

## Phase 5 — Package (fixed file contract)

```
<slug>-mascot/
  README.md                  what each file is + copy-paste embed snippets
  GUIDELINES.md              do/don't, clear space, min sizes, voice, expression guardrails, partner usage
  manifest.json              name, version, colours, states, expressions, file list
  svg/master.svg             full colour, group contract intact
  svg/mono.svg               single colour using currentColor
  svg/silhouette.svg         solid shape
  svg/icon.svg               simplified cut for 16–32px
  svg/expressions/<name>.svg
  svg/states/<state>.svg     static key pose per state
  web/mascot.css             state animations keyed on [data-state], reduced-motion respected
  web/mascot.js              zero-dependency <x-mascot> web component
  web/Mascot.jsx             thin React wrapper around the web component
  web/demo.html              every state + expression, light and dark
  tokens/colors.css | colors.json | tailwind.js
  png/master-{64,128,256,512,1024}.png, png/mono-{black,white}-512.png
  favicon/favicon.svg, favicon.ico, apple-touch-icon.png
  social/avatar-1080.png, og-1200x630.png, (story-1080x1920.png if social is a surface)
  slides/mascot-sheet.png    one-page overview for decks
  slides/construction-sheet.png
  build/                     the generator scripts that regenerate every file above
```

Copy on social images (taglines) is placeholder: mark it as such in README.md and ask the user for sign-off.

Web component pattern (adapt names; inline the SVG markup from `svg/master.svg` and the CSS):

```js
// web/mascot.js — usage: <x-mascot state="working" expression="curious" size="48"></x-mascot>
const SVG = `<!-- paste svg/master.svg here; write filter/gradient ids as __ID__-name -->`;
const CSS = `/* paste web/mascot.css here */`;
let n = 0;
class XMascot extends HTMLElement {
  static observedAttributes = ['state', 'expression', 'size', 'label'];
  constructor() {
    super();
    const uid = `m${++n}`; // unique ids per instance, so filters don't collide on one page
    this.attachShadow({ mode: 'open' }).innerHTML = `<style>${CSS}</style>${SVG.replaceAll('__ID__', uid)}`;
  }
  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }
  render() {
    const svg = this.shadowRoot.querySelector('svg');
    const s = this.getAttribute('size') || '48';
    svg.setAttribute('width', s); svg.setAttribute('height', s);
    svg.dataset.state = this.getAttribute('state') || 'idle';
    svg.dataset.expression = this.getAttribute('expression') || 'neutral';
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', this.getAttribute('label') || `Mascot, ${svg.dataset.state}`);
  }
}
customElements.define('x-mascot', XMascot);
```

```css
/* web/mascot.css — every animation keys on the group contract */
svg [id^="m-"] { transform-box: fill-box; transform-origin: center; }
[data-state="idle"] #m-body { animation: breathe 4s ease-in-out infinite; }
[data-state="thinking"] #m-eyes { animation: glance 1.6s ease-in-out infinite; }
[data-state="working"] #m-acc { animation: work 1.2s linear infinite; }
@keyframes breathe { 50% { transform: scale(1.02); } }
@keyframes glance { 25% { transform: translateX(-4%); } 75% { transform: translateX(4%); } }
@keyframes work { to { transform: rotate(360deg); } }  /* replace with the variant's own working motion */
@media (prefers-reduced-motion: reduce) { svg * { animation: none !important; } }
```

**Verify before handing over** (each item checked, not assumed):

- [ ] Every SVG parses, and every PNG was rendered in headless Chromium and you **looked** at it
- [ ] Two `<x-mascot>` instances on one page render correctly (no id collisions)
- [ ] `grep -L 'id="m-body"' svg/**/*.svg` finds nothing in master/states/expressions
- [ ] No `<text>`, no external font, no `<image href="http`
- [ ] `demo.html` shows all states animating; reduced-motion stops them
- [ ] icon.svg readable at 16px; mono.svg follows `currentColor` on dark
- [ ] Audit row re-run on the final art: still zero P0
- [ ] Zip the folder and deliver it; give the user the 3 most-used snippets (img tag, web component, favicon links) in the reply

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "Demo is tomorrow, skip states" | For an AI agent the states ARE the mascot's job. The CSS above takes minutes. |
| "They'll pick my top one anyway" | Then the contact sheet costs nothing. Packaging the wrong variant costs the whole package. |
| "Warm café colours avoid the AI look" | Cream + espresso + terracotta is the most common "tasteful" AI default. Audit it. |
| "My variants are all different concepts" | Same stroke, palette and face template = one variant in four costumes. Check the axes table. |
| "A face makes it friendly" | Dot eyes + smile + blush is the template every generator outputs. Change the face system. |
| "Brand name in the art helps recall" | It breaks localisation, small sizes and partner usage. Text sits beside the mascot. |
| "I'll add the guidelines later" | Without GUIDELINES.md the first partner meme decides your brand. |
| "The object itself is the concept" | An object is a metaphor, not a character. Without a twist from a user truth it fails the swap test. |
| "I already know the best idea, skip thumbnails" | The first idea is the one everyone has. 24 silhouettes cost minutes. |
| "I checked it myself, no need for a judge" | You know the backstory, so you see what isn't drawn. The judge sees only the PNG. |

## Red Flags — stop and go back a phase

- Drawing before the exclusion list, concept cards and thumbnail sheet exist
- A concept card whose twist could be pasted onto a competitor
- Fewer than 3 rendering styles across the set
- Any variant you'd describe as "cute blob with eyes"
- Packaging started with neither a pick nor an explicit delegation from the user
- A variant shown without its second craft pass
- A state or expression made by redrawing the body
- "Looks fine" said about an SVG you never rendered
