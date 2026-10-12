# Engineering: building, rendering and exporting ads from HTML

## Project layout (per campaign)

```
campaign/
  research.md       # Phase 0 evidence: VOC bank, competitor ad log, market notes, synthesis, insights (templates/research.md)
  brief.md          # brief citing research IDs + assumptions
  concepts.md       # ≥15 seeds → shortlisted concept cards (human-readable)
  concepts.json     # concept cards + claims ledger + rubric (machine-readable, read by scorecard.py)
  personas.json     # panel personas
  html/             # one HTML per concept × placement (recomposed, not scaled)
    fonts/ assets/  # local fonts, logo SVG, product photos supplied by the user
  manifest.json     # list of ads to render
  out/              # renders, *.dom.json, qa.json, attention.json, report.md
  panel/            # judge batches, verdicts, panel.json
  deliver/          # final exports only
```

## HTML contract (what the scripts rely on)

Start from `templates/ad.html`.

- The body **is** the canvas. Give `html, body` the exact width and height and `overflow: hidden`. Use absolute or grid layout; nothing should depend on the viewport.
- Tag measurable elements with `data-aoi`: `brand`, `headline`, `product`, `cta`, `offer`, `proof`, `face`, `legal`. Without these tags, attention and safe-zone checks can't see the elements.
- Text inside a product or UI mock-up sits under `data-aoi="product"` and is excluded from the word budget.
- A deliberate text-on-text overlay (a stamp, a handwritten correction) needs `data-aoi="overlap-ok"` on the overlaying element; otherwise QA fails text overlaps.
- **Local fonts** via `@font-face` with relative URLs, and `font-display: block`. `render.py` waits for `document.fonts.ready`.
  - Open-licence fonts can be fetched from `https://raw.githubusercontent.com/google/fonts/main/ofl/<family>/<File>.ttf` (the github.com/raw form may 403 behind proxies) when network allows.
  - Use static weights for print (variable fonts embed as Type 3 in PDF).
- Use `text-wrap: balance` on headlines. Use CSS custom properties for the palette, with one accent reserved for the CTA.
- Images go in `assets/`, referenced by relative path. Use SVG for logos and icons.
- SVG text is measured through its `fill`, so set `fill` explicitly.
- Design-time safe-zone guides: open `file.html?guides=meta_story_9x16`. Renders never include the query string.

## manifest.json

```json
{"ads": [
  {"id": "c1-feed",  "html": "html/c1-feed.html",  "width": 1080, "height": 1350, "placement": "meta_feed_4x5",   "concept": "c1"},
  {"id": "c1-story", "html": "html/c1-story.html", "width": 1080, "height": 1920, "placement": "meta_story_9x16", "concept": "c1"},
  {"id": "c1-mrec",  "html": "html/c1-mrec.html",  "width": 300,  "height": 250,  "placement": "display_300x250", "concept": "c1", "format": "jpg", "quality": 82},
  {"id": "c1-a3",    "html": "html/c1-a3.html",    "width_mm": 303, "height_mm": 426, "placement": "print_a3_bleed", "concept": "c1", "format": "pdf"}
]}
```

- Optional fields:
  - `"scale": 2` renders at 2× for hi-res social.
  - `"spec": {...}` overrides QA thresholds for a new placement.
  - `"wait_ms"` adds a wait before capture.
- Chromium: `render.py` uses Playwright's default browser. Pass `--chromium PATH` or set `CHROMIUM_PATH` if needed. Don't run `playwright install` where a browser is preinstalled.

## Export recipes

**Display ≤150KB:**
- Prefer JPG at q80–85 for photographic ads.
- For flat ads, use PNG quantised with Pillow:
  ```python
  Image.open(p).quantize(colors=64, method=Image.MEDIANCUT).save(p, optimize=True)
  ```
- Re-run `qa_check.py` after compressing.

**Animated GIF banner (frames from CSS states):**
- Render each frame by toggling a `data-frame` attribute on the body, then screenshot.
- Assemble the GIF with Pillow:
  ```python
  frames[0].save("ad.gif", save_all=True, append_images=frames[1:], duration=[2500, 2500, 3000], loop=2, optimize=True)
  ```
- Limits: <5 fps, ≤30 s total, 3 loops max.
- The final frame must carry logo, offer and CTA.

**HTML5 ZIP (Google Ads / CM360):**
- Keep `index.html` with `<meta name="ad.size" content="width=300,height=250">` and the exit handler.
- Include only relative assets and ≤40 files. Total ≤600KB.
- For Google Ads, whole-ad clicks are handled by the platform. For CM360/DV360, use the clickTag pattern:
  ```html
  <script>var clickTag = "https://www.example.com";</script>
  <a href="javascript:window.open(window.clickTag)" style="position:absolute;inset:0;z-index:9" aria-label="Brand: offer — CTA"></a>
  ```
- Animate with CSS keyframes or GSAP from Google's CDN, and stop by 30 s.
- Zip with `cd ad && zip -r ../ad_300x250.zip .` so there is no parent folder.
- Validate in Google's HTML5 validator before upload.

**Print PDF:**
- `render.py` with `format: pdf` and `width_mm`/`height_mm` that include bleed. The page uses `@page { margin: 0 }` with backgrounds printed.
- Add crop marks via SVG if the printer asks.
- Convert to CMYK when required:
  ```bash
  gs -o out_cmyk.pdf -sDEVICE=pdfwrite -sColorConversionStrategy=CMYK -dProcessColorModel=/DeviceCMYK in.pdf
  ```
  Then flag the expected colour shift.

**Platform text assets:**
- Write `deliver/<concept>_copy.md` with the primary text, headline, description, alt text ("Brand: offer, CTA") and the RDA headline/description sets, within the character limits (platform-specs.md).

## Assets and honesty

- Use real logo, product photos and brand fonts when supplied.
- When they're missing, design with a visible placeholder. List each item under **Required assets** in the report, and keep `"source": "UNVERIFIED"` claims out of final files.
- If the user allows an image model, use it only for text-free scenes or textures. Composite all type in HTML, and judge "AI look" tells at the visual review.

## Visual review loop (after every render)

Read the actual PNGs yourself, at full size *and* at phone-thumbnail size (about 360px wide). Fix what you see, re-render, and repeat until clean. Then run the benchmark. Typical catches that scripts miss:
- awkward line breaks and widows;
- optical misalignment;
- a product that looks fake;
- an accent colour that leaks outside the CTA;
- illegible text over busy imagery;
- something that looks like a fake UI button.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Fonts fall back to DejaVu | Wrong relative path, or the font file failed to load. Check `fonts_loaded` in `*.dom.json` |
| Contrast fail on text over an image | Add a scrim/panel, or move the text to a calm area. QA measures the worst 10% of pixels behind the text |
| "element off canvas" | Hidden overflow is still flagged if it contains text or an AOI. Remove it or clip it on purpose with a non-text element |
| DeepGaze import fails | Expected in sandboxes. Classic saliency runs automatically and the report labels it low confidence |
| OCR recovery 0% on a stylised headline | Tesseract weakness with display fonts. Check legibility visually at thumbnail size before trusting it |
