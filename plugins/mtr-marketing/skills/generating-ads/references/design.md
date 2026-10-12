# Design rules for static / HTML ads

Tags: **[O]** official platform or W3C · **[R]** peer-reviewed / eye-tracking · **[I]** large industry dataset · **[P]** practitioner · **[W]** weak/contested.

## 1. Hierarchy (the default every layout starts from)

- **Exactly one dominant element.** It takes about 40–60% of the visual weight. Reading order:
  1. Visual (largest, highest contrast)
  2. Headline
  3. CTA, isolated by the accent colour
  4. Logo, small, in a corner. *Also* put a brand cue at or next to the focal point: a logo on the product or UI, the brand colour on the hero, or the pack shot. The brand element transfers attention best when it sits near the focal point (Pieters & Wedel 2004), and a corner-only logo usually misses the first fixations

  Ads that are hard to parse get skipped [R].
- **Three core elements:** visual, headline, CTA. Add the logo and at most one offer/proof badge. Nothing else [P].
- **Squint test:** blur the render. One blob should dominate, and the CTA should still be findable. `attention.py` automates a version of this.
- **Layout by shape:**
  - **Wide banners** (728×90, 970×250, 1200×628): logo/visual left → headline centre → CTA right. This Z-flow is widely taught, but the evidence for it is weak [W].
  - **Tall formats** (160×600, 300×600, 9:16, 2:3): stack top → bottom. Message at the top, visual in the middle, details and CTA at the bottom (Pinterest guidance) [O].
- **Alignment:** use one left edge *or* one centre axis per ad, never both.
- **Grid:** 8px base unit, or multiples of 24 on 1080 canvases.
- **Inner margin:** about 5–8% of the short side (64–96px on 1080; 12–16px on 300×250).

## 1b. Translating tone words into design moves

| Brief says | Do | Avoid |
|---|---|---|
| Premium / luxury | Restraint: lots of space, 1 focal object, serif or refined grotesk, muted deep palette + 1 accent, real photography, small price | Badges, starbursts, %-off shouting, gradients, many weights |
| Bold / challenger | Oversized type, saturated flat field, hard crops, one surprising object | Timid, centred-symmetric stock layouts |
| Playful / friendly | Rounded type, warm colours, hand-drawn SVG accents, a character or scenario | Corporate blue, stiff grids |
| Trustworthy / B2B | Real UI or data, clear hierarchy, human faces of real users, a source line under stats | Abstract 3D blobs, vague claims |
| Deal / urgency | Number as the biggest glyph, high contrast, a real deadline line | Fake timers, more than one offer |

Record the chosen moves as assumptions in `brief.md`.

## 2. Type sizes (canvas px)

A feed creative renders at about 0.35× on a phone, so 32px on a 1080 canvas is about 11px on screen. Use these floors; `qa_check.py` enforces the minimums.

| Canvas | Headline | Body/sub | CTA label | Legal floor |
|---|---|---|---|---|
| 1080×1080 / 1080×1350 | 64–120 | ≥32 (36–44 better) | ≥32 | 24 |
| 1080×1920 | 72–130 | ≥36 | ≥36 | 28 |
| 300×250 | 20–28 bold | 12–14 | 12–14 bold | 9–10 |
| 728×90 | 18–26 | 12–14 (often omit) | 12–14 | 9 |
| 320×50 | 14–18 | none | 11–13 | none |
| 160×600 | 18–24, 2–4 words/line | 12 | 12 | 9 |
| 300×600 | 24–36 | 13–16 | 14 | 10 |
| 970×250 | 28–44 | 14–18 | 16 | 10 |
| Billboard | 1 inch of letter height per 30 ft of viewing distance | | | |

- **Leading:** 0.95–1.15 for headlines, 1.25–1.4 for body text.
- **Weights:** headline weight 700–900. Avoid weights under 400 at small sizes.
- **Lines:** ≤3 headline lines, ≤25–30 characters per line in feed ads, 2–5 words per line in banners.
- **Typefaces:** ≤2 families; a third only for one narrow job such as price. Use ≤3 weights, and make each size step ≥1.5× the previous one.
  - Proven pairings: a condensed display face (Anton, Bebas Neue, Oswald) + a neutral sans (Inter, DM Sans); a serif display face (Playfair, DM Serif) + a sans; or one superfamily in two weights.
- **All caps:** only for ≤4 words, with +2–8% tracking. Never in Google RDA text. Condensed display faces (Anton, Bebas) are fine for longer headlines set in sentence case.
- **Numbers:**
  - Make the key number the largest glyph on the canvas.
  - Set "%"/"$" at 50–60% of the numeral height.
  - "$49" feels cheaper than "$49.00" (Coulter et al. 2012) [R].
  - A struck-through reference price must be genuine.

## 3. Colour

- **Contrast beats hue.** The evidence for colour psychology is weak (Elliot 2015 review) [R]. Do not write "orange = urgency" as if it were fact.
- **60 / 30 / ≤10 split:** dominant / secondary / accent. The accent appears **only** on the CTA, plus optionally the price badge (isolation / von Restorff effect). The rule is "the CTA is the most isolated colour on the canvas": if the brand accent fails contrast, use a darker or lighter tone of it, or an ink-coloured button on a light field. Never trade contrast for brand purity.
- **WCAG contrast:** text ≥4.5:1, large text ≥3:1, CTA shape vs background ≥3:1 [O]. Measure against the *worst* pixels behind the text. Over photos, use a scrim (`linear-gradient(rgba(0,0,0,.55), transparent)`) or a solid panel.
- **Feeds run in light and dark mode.**
  - Pure-white creatives vanish in light mode; pure-black ones vanish in dark mode.
  - A mid or saturated field, or a photo with its own edges, survives both.
  - On display banners with a white background, add a 1px inset border.
- **Brand colour:**
  - Use it as the frame or field.
  - If the brand primary is near-white or near-black, use a saturated brand secondary as the field.
  - Distinctive, consistent palettes help (Kantar×Meta: +67% short-term) [I].
- **Avoid red/green pairs:** about 8% of men can't tell them apart.

## 4. Imagery

| Approach | Wins for | Notes |
|---|---|---|
| Real product cutout on a solid/plain field | E-com, retargeting, display, small sizes | Strong silhouette, soft shadow. Not for Google RDA (no composites or all-white) |
| Lifestyle / in use with people | Meta/TikTok/Pinterest prospecting | Human connection: +81% effectiveness (Kantar×CreativeX for Meta, 55k creatives) [I] |
| Face with directed gaze | Any | Eyes or head turned toward the headline or product: ~4× more looks at the product (Palcu 2017) [R]. Generic stock people get ignored (NN/g) [R] |
| Device/UI mock-up | SaaS, apps, B2B | Show one real screen, cropped to the key moment, with one callout. Agents build UI in HTML well, so make it data-true |
| SVG illustration / type-only | Small banners, abstract services, weight limits | Use one illustration style per campaign |
| Native / UGC (notes, chat, tweet, review card) | TikTok, Reels, Stories, Meta prospecting | Must feel like content. No fabricated reviews or personas |
| Stat card | B2B, LinkedIn | Huge number plus a source line |

- **Assets you don't have:** the agent cannot photograph the real product. Ask for product photos, logo files and brand fonts.
  - If they're missing, design with an explicit placeholder and list it under **Required assets** in the report.
  - Never present a drawn imitation as the real product.
  - An image-generation model may be used for backgrounds or scenes only when the user allows it. Keep generated imagery text-free and composite real type over it in HTML.
- **Avoid the "AI look":** consumers distrust AI-looking ads (CivicScience: 37% view them negatively) [I]. Tells to avoid:
  - waxy skin, a purple-blue "tech glow", centred symmetric hero shots with bokeh;
  - generic 3D blobs, heavy glassmorphism;
  - the default Inter-on-gradient look;
  - nonsense text or extra fingers.

  Instead, use texture/grain, asymmetric layouts, deliberate type choices, hand-drawn SVG accents and real photography.
- **Avoid stock clichés:** handshakes, headset call centres, people laughing at salad, generic groups at a laptop.

## 5. Recompose per size (never squash one layout)

| Size | Recipe |
|---|---|
| 1080×1350 (4:5) | Headline in the top third. Hero in the middle. Proof and CTA at the bottom. Keep key items within the central 1080×1080 (grid crop) |
| 1080×1920 (9:16) | All critical items inside y 270–1250, x 120–900 (Meta ∩ TikTok safe box) |
| 300×250 | Visual in the top 55–60%. Headline 1–2 lines below. CTA ~110×32 bottom-right. Logo top-left at 60–80px |
| 728×90 | Logo (≤20% width) → 1-line headline (~50%) → CTA (~110×36). Vertical padding ≥10 |
| 160×600 | Logo top. Headline 2–4 words/line, 3 lines max. Product in the middle. Full-width CTA at the bottom |
| 300×600 | A mini poster: hero image in the top half, headline, one benefit line, CTA |
| 320×50 | Icon (≤40×40) + headline of ≤5 words + CTA chip (~70×28). Flat colours. ≤50KB by IAB LEAN |
| Google RDA 1200×628 / 1200×1200 | **No text, logo, buttons or borders.** Real scene, product in focus. Messages go in text assets |
| Poster/OOH | ≤7 words, 3 elements. Bold sans only. 10% safe margin. Test in greyscale at simulated distance |

## 6. Animation (display GIF/HTML5)

- Google GIF limits: ≤30 s and <5 fps; it must stop by 30 s [O].
- Common publisher rules: ≤3 loops, ≤15 s.
- The **first and last frames each carry the complete message** (logo, offer, CTA).
- No more than 3 flashes per second (WCAG 2.3.1). Respect `prefers-reduced-motion`.
- For video or motion-graphics versions, hand the locked concept card and key frames to the `making-motion-videos` skill (mtr-video).

## 7. Common mistakes (check visually after QA)

1. Everything is the same size, so there is no focal point.
2. A paragraph of copy in the image.
3. The CTA shares its colour with other elements.
4. The logo is so large it turns the ad into a brand poster.
5. Critical text sits under the platform UI.
6. Thin or script fonts at small sizes.
7. A white banner with no border.
8. Text baked into Google RDA images.
9. Fake play, close or download buttons.
10. Letterboxed images (Google requires images to fill the frame).
11. One layout scaled into every ratio.
12. Stock clichés or the AI look.
13. The ad promises something the landing page doesn't show.
14. A placeholder or drawn product shipped as if it were real.
