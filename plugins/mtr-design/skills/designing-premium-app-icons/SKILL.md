---
name: designing-premium-app-icons
description: Use when asked to design, generate, or redesign an app icon or a set of app icons (iOS, macOS, Android, PWA), including requests for premium, modern, creative, original, Liquid Glass, Icon Composer layers, mascot, glyph, lettermark, or gradient icon styles, and when output must be SVG.
---

# Designing Premium App Icons

## Overview

Generated icons fail in two ways. Unguided, they land on the category's first metaphor on an indigo gradient. Rule-following, they become a clean remix of an icon library: function → noun → one centered primitive, mirror-symmetric, uniform round-capped strokes, Apple system colors. Both are the **median** — the answer any model gives.

Premium here means **ownable and surprising, then legible**. The method: write the median down and kill it, mine the brief for material the median never touches, distort the form on purpose, and treat legibility as a gate rather than the goal.

Read `creative.md` (lenses, form moves, palette references, AI tells) before step 2 and `patterns.md` (dialects) before step 4.

## Deliverable contract

For each brief, produce these, in order:

1. **Brief read** — audience, brand hue if given, and **the median**: one sentence describing exactly what a generic model would draw (subject, placement, colors). Write it concretely enough that you could draw it.
2. **Raw material** — at least one line from each of the 5 lenses in `creative.md`.
3. **Thumbnails** — 12 one-line ideas, each tagged `lens · dialect · form move`. Then strike through (`~~…~~`) the median and the 4 thumbnails closest to it.
4. **Concept table** — 3 surviving thumbnails. Rows differ in lens and dialect; backgrounds span ≥ 2 families (neutral dark · neutral light · hue):

   | # | Idea | Lens | Dialect (P1–P8) | Form moves (≥ 2) | Background family | Palette reference |
   |---|------|------|-----------------|------------------|-------------------|-------------------|

5. **Palette contract per concept** — 2–4 hex. Each line `#hex — role — source`, source = brand color, the named palette reference, or a neutral that is **not** an Apple system value.
6. **Three built icons** — one folder each, written by a small generator script that imports `scripts/shapes.mjs` when a form move needs organic curves, brush strokes, wobble or grain.
7. **Review** — per concept: the sheet, gate verdicts, each remaining AI tell with its justification, and the ranking below with one recommendation.

## Folder layout (Icon Composer–ready)

```
<out>/<concept-slug>/layers/01-background.svg   full-bleed opaque 1024 square
<out>/<concept-slug>/layers/02-<part>.svg       transparent 1024 canvas, back → front
```

Every layer: `viewBox="0 0 1024 1024"`, one coordinate system, letterforms as paths. Foreground layers use flat fills. `01-background` may also carry the gradient or `stipple()` grain its dialect or palette reference calls for. The system adds mask, shadow, blur, specular and translucency, so none of those go in the files. The script renders `preview/icon-1024.png` (unmasked App Store master) — the answer to any request for a single flattened preview.

## Preview, gates, ranking

```bash
npm install --prefix <skill-dir>/scripts      # once, if node_modules is missing
node <skill-dir>/scripts/preview.mjs <out>/<concept-slug>
```

It prints metrics, ISSUES and AI-TELLS, and writes `preview/sheet.png` (default, mono, tinted, 180 → 29 px on dark and light). **Open the sheet and look at it.**

**Gates** — a concept that fails any gate is fixed or dropped:
- ISSUES is `none`.
- At 29 px the idea is identifiable; parts that vanished were decoration — delete them.
- Mono and Tinted tiles separate the subject from the background.
- Misread test: name what a stranger would call the 60 px tile. If the answer is another app category's symbol (chat bubble, lightbulb, media player, settings toggle), it fails.
- On the light-wallpaper row the icon's outline stays visible.

**AI tells** — each one the script reports is either removed or kept with a one-line reason tied to the idea ("symmetric because it is a face"). Aim for ≤ 1 per concept.

**Ranking** among concepts that pass the gates: most ownable (a competitor couldn't put their name on it) → most surprising → fewest tells. Legibility already passed; it does not break ties.

Report anything still failing instead of calling it done.

## Craft rules

- One idea per icon; a second metaphor is a different concept.
- Minimum stroke or gap ≈ 60 px so it survives 29 px.
- No words; a lettermark is 1–2 constructed characters.
- One hand per icon: geometric or organic, chosen on purpose and applied to every part.

## Common mistakes

| Observed in testing | Correction |
|---|---|
| Indigo→navy gradient "because it feels premium" | Every hex needs a source |
| Function → noun → centered primitive (toggle, paw, pause) | Median written down and struck; lenses supply the idea |
| Apple system colors (`#1c1c1e`, `#34c759`, `#0a84ff`) | Palette from a named reference; lint flags system values |
| Mirror symmetry and median placement by default | ≥ 2 form moves per concept; tells need a reason |
| Recommending the most on-brief idea that is mush at 29 px | Legibility is a gate before ranking |
| Shapes that read as another app's symbol (D → chat bubble, balloon → bulb) | Misread test at 60 px |
| 8–9 colors, details that vanish, three metaphors in one mark | 2–4 hex, 29 px gate, one idea |
