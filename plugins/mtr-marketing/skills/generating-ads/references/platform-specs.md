# Platform specs (checked Oct 2026; verify in the platform preview before launch)

Placement keys match `scripts/qa_check.py → PLACEMENTS`. **[O]** = official doc. **[I]** = industry aggregator. Meta and LinkedIn help pages often block fetching, and aggregators sometimes disagree, so treat [I] numbers as working values.

## Meta (Facebook / Instagram / Threads)

| Key | Size | Notes |
|---|---|---|
| `meta_feed_4x5` | 1080×1350 (hi-res 1440×1800) | Recommended feed ratio. Keep key items inside the central 1080×1080, because grid and preview crops cut the 4:5 edges [I]. QA flags only a warning here: the logo or legal line may sit in these bands if the ad still reads when cropped |
| `meta_feed_1x1` | 1080×1080 | Carousel cards: 2–10 cards, 1:1, about 45-character headline per card |
| `meta_story_9x16` | 1080×1920 | **Safe zone: keep clear top 269px (14%), bottom 672px (35%), sides 65px (6%)** [I, matches the Ads Manager overlay] |
| 1.91:1 | 1200×628 | Right column / link ads |

Text fields:
- Primary text truncates at about 125 characters.
- Headline is about 27 characters (FB feed) to 40.
- Description is about 25–30 characters.

Keep image text complementary to these fields, not a duplicate. The 20% text rule was retired, but low-text images still tend to deliver better [I/W].

## TikTok

- `tiktok_9x16`, 1080×1920 safe zone: keep clear top 240, bottom 660, left/right 120, plus the right 300px below y = 840 (the like/comment rail) [I].
- Image ads: 720×1280 (also 1200×628 and 640×640 on Pangle).
- Carousel [O, TikTok playbook]:
  - 2–35 images at 9:16, ≤100KB each. Music is required.
  - **3 or 7–9 images** perform best.
  - Card 1 is the hook. The CTA comes after the benefits.
- Ad text 1–100 characters; brand name 2–20.

## Combined vertical safe box

Use `universal_9x16` when one 9:16 file serves both Meta and TikTok. Keep critical content inside **x 120–900, y 270–1250**.

## Google Ads, uploaded image/HTML5 display [O]

Source: https://support.google.com/google-ads/answer/1722096

- **Image ads:**
  - GIF/JPG/PNG, **≤150KB**.
  - Animated GIF: ≤30 s and <5 fps.
- **Sizes (`display_WxH`):**
  - Rectangle/square: 300×250, 336×280, 250×250, 200×200, 240×400, 250×360, 580×400.
  - Skyscraper: 120×600, 160×600, 300×600, 300×1050.
  - Leaderboard: 468×60, 728×90, 930×180, 970×90, 970×250, 980×120.
  - Mobile: 300×50, 320×50, 320×100.
  - **Top 5 sizes cover about 95% of inventory: 300×250, 728×90, 160×600, 320×50, 300×600.** Ship these first.
- **HTML5 ZIP:**
  - ≤600KB, ≤40 files, relative paths only.
  - Must include `<meta name="ad.size" content="width=300,height=250">`.
  - External sources limited to Google Fonts and Google-hosted GSAP/CreateJS/jQuery.
  - Write explicit SVG end tags (`<path></path>`).
  - Account eligibility: older than 90 days and more than $9k lifetime spend.
  - AMPHTML: ≤600KB; the whole ad is clickable.
- **Image quality policy:**
  - The image must fill the frame, with no letterboxing.
  - No blur, sideways images, strobing, illegible text, or imitation system warnings or buttons.
- **IAB LEAN initial-load weights:**
  - 300×250, 728×90, 160×600: 150KB.
  - 970×250 and 300×1050: 250KB.
  - **320×50: 50KB.**
- **Borders:** many publishers require a ≥1px contrasting border on white or light banners. Google doesn't state this, but it does no harm, so add it by default.

## Google Responsive Display / Demand Gen [O]

| Asset | Spec |
|---|---|
| Landscape image | 1.91:1, 1200×628 (min 600×314), up to 15 |
| Square image | 1:1, 1200×1200 (min 300×300), up to 15 |
| Logo | 1:1 1200×1200, 4:1 1200×300; transparent background preferred |
| Headline | ≤30 characters (×5) |
| Long headline | ≤90 characters |
| Description | ≤90 characters (×5) |
| Business name | ≤25 characters |

RDA image rules:
- **No overlaid text, logo or button. No border, rounded corners or collage.**
- Blank space ≤80%. Use a real setting, not an all-white composite.
- Text assets in sentence case; no ALL CAPS.

Placement keys: `google_rda_1.91x1`, `google_rda_1x1`.

## LinkedIn [I]

- Images: 1200×627 / 1200×1200 / 1080×1350 (4:5). JPG/PNG ≤5MB.
- Intro text ≤150 characters; headline ≤70.
- Carousel: 2–10 cards at 1080×1080.
- 1:1 or 4:5 gets more feed height than 1.91:1.

## Pinterest [O]

- 2:3 at 1000×1500; taller pins may be cut off.
- Title shows about 40 characters in the feed.
- Logo on every pin; product shown in real use.
- Keep the bottom-right ~15% free of UI icons.

## X [I]

- 1:1 1200×1200 or 1.91:1 1200×628.
- Website card overlays its headline at the bottom-left, so keep that area clear (`x_card_1.91x1`).

## Print and OOH

- **Poster:**
  - Trim size + **3mm (0.125in) bleed** on every side. Keep text ≥5mm inside the trim; QA uses 8mm from the bleed edge.
  - 300 DPI at final size. Export PDF/X-4.
  - Placement keys: `print_a3_bleed` (303×426mm), `print_a2_bleed` (426×600mm).
- **Colour:**
  - Chromium outputs sRGB. Convert to CMYK (FOGRA39/GRACoL) with Ghostscript or the printer's RIP.
  - Saturated RGB oranges, greens and blues will dull.
  - Use rich black (C60 M40 Y40 K100) for large areas and K-only for small text.
  - State in the report that the file is RGB unless you converted it.
- **Fonts:** Chromium embeds variable fonts as Type 3. Use static TTF/OTF weights for print files.
- **Billboard (`ooh_billboard`):**
  - ≤7 words and 3 elements.
  - 1 inch of letter height per 30 ft of viewing distance.
  - 10% safe margin.
  - DOOH slots run 8–30 s, usually 15 s.

## Platform-independent

Every ad has a stated placement key, so QA can apply the right zones. If a placement is new, add an entry to `PLACEMENTS` (or a `"spec"` override in the manifest) from the platform's current doc, and cite it in the report.
