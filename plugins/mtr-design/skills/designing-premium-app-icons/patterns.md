# Icon Dialects

Eight visual dialects seen across ~70 contemporary premium icons. They are starting languages, not templates: a concept picks a dialect, then its form moves (see `creative.md`) bend it. The `fgBox` ranges (foreground bounding box as % of the 1024 canvas) are the dialect's default; a Crop or Offset move overrides them on purpose.

## Audience → candidate patterns

| Audience | Strongest patterns |
|---|---|
| Pro / B2B / developer / AI / finance | P3 Mono glyph, P4 One symbol + one accent, P7 Lettermark, P2 Glass object |
| Consumer playful / social / games / young adults | P1 Mascot, P5 Mesh gradient + white glyph, P4 |
| Utility / system tool | P6 UI-as-icon, P3, P2 |
| Lifestyle / travel / wellness / content | P8 Flat scene, P4, P1 |

First-thought clichés to flag in the brief read: sleep → moon + stars · security → shield/lock/keyhole · monitoring → pulse line/ring · chat → speech bubble · finance → coin/up-arrow · photos → mountain + sun · AI → four-point sparkle · music → note.

---

## P1 — Mascot with eyes
- **Build:** one blob silhouette (cat-ear head, flame, drop, rounded block) + two vertical oval eyes in the upper-middle; mouth optional and tiny. Eye gap ≈ 1–1.5× eye width.
- **Size:** fgBox 60–80%, or crop off the bottom edge by 10–25% for intimacy (`bleeds: true` is fine).
- **Palette:** one saturated background hue (pink, violet, orange, red) with a slightly lighter top; body near-white on saturated, or near-black on pastel; eyes are the inverse of the body.
- **Layers:** background / body / eyes.
- **Traps:** limbs, props, a second character, gradients on the body.

## P2 — Glass object (Liquid Glass)
- **Build:** 2–3 overlapping simple shapes (stacked cards, drop, speaker cone, layered squares), slightly offset to show depth.
- **Size:** fgBox 50–65%.
- **Palette:** a tinted near-black or warm off-white background (from the palette reference, not system greys); shapes in light/mid tones with at most one colored shape.
- **Layers:** one layer per overlapping shape; the glass effect is added by Icon Composer, so fills stay flat and opaque.
- **Traps:** faking glass with blur, opacity or highlight gradients in the files.

## P3 — Mono glyph
- **Build:** one geometric glyph built on a grid (circles, 45° cuts, constant stroke ≥ 80 px).
- **Size:** fgBox 50–62%, centered.
- **Palette:** white on #000–#111, or black on #fff/#f5f5f7. Nothing else.
- **Layers:** background / glyph (split the glyph only if one part should float above the rest).
- **Traps:** thin strokes, gradient glyphs, tiny counters that close up at 29 px.

## P4 — One symbol + one accent
- **Build:** a bold neutral-colored symbol plus one small accent shape (dot, segment, notch) in a vivid color, *or* a symbol in a deep hue on a pale tint of the same hue.
- **Size:** fgBox 50–65%.
- **Palette:** 3 colors max: background, symbol, accent. In the tint variant, the background is the symbol hue at roughly 15–25% saturation and high lightness.
- **Layers:** background / symbol / accent.
- **Traps:** a second accent, an accent so small it disappears at 29 px (min ≈ 10% of canvas).

## P5 — Mesh gradient + white glyph
- **Build:** a background of 2–3 radial color blobs that blend, with a single bold solid-white glyph on top.
- **Size:** glyph fgBox 50–60%, stroke ≥ 90 px.
- **Palette:** analogous blob stops (purple→pink, orange→pink, green→cyan). The glyph is #fff.
- **Layers:** background (the gradient) / glyph.
- **Traps:** complementary stops that turn muddy in the middle, a linear top-to-bottom gradient (reads dated), a thin glyph.

## P6 — UI-as-icon
- **Build:** one system control drawn large: a toggle, a password field, a lock inside a device frame, a card. Simplified to its silhouette.
- **Size:** fgBox 65–80%.
- **Palette:** a neutral (black, white or graphite) plus one system color for the active state.
- **Layers:** background / control body / control state (knob, dots, glyph).
- **Traps:** real UI detail (status bars, text), more than one control.

## P7 — Lettermark
- **Build:** 1–2 characters *constructed*, not typed: slanted, cut, a ligature, or a stroke that turns into a symbol. Converted to paths.
- **Size:** fgBox 50–65%.
- **Palette:** P3 or P4 rules, or a single solid brand color background with a white letter.
- **Layers:** background / letter (/ accent part).
- **Traps:** a stock font left unmodified, 3+ letters, a wordmark.

## P8 — Flat scene
- **Build:** a horizon in the lower third bleeding to both edges, and one subject (sun, plane, figure) in the upper-middle. At most 3 depth planes.
- **Size:** subject 30–45% wide, ground full width. The script lists full-width planes under `scenery` and measures only the subject.
- **Palette:** 3 tones of one hue for sky and ground + 1 contrasting subject color.
- **Layers:** sky / ground planes / subject.
- **Traps:** a 4th plane, small details (birds, windows), photographic gradients.
