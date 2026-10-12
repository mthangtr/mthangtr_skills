#!/usr/bin/env python3
"""Deterministic pre-flight QA (hard gates + warnings) for rendered ads.

Usage:
    python scripts/qa_check.py out/            # checks every out/*.dom.json
    python scripts/qa_check.py out/ --json out/qa.json

Reads <id>.dom.json, <id>.png, <id>.notext.png written by render.py.
Placement specs live in PLACEMENTS below (sources: references/platform-specs.md).
A manifest entry may override any spec key via "spec": {...} (copied into dom.json? no: pass --manifest).

Exit code 1 if any ad fails a hard gate.
"""
import argparse, json, re, sys, difflib
from pathlib import Path
import numpy as np
from PIL import Image

# display_scale: CSS px on canvas -> px seen by a viewer (feed 1080 canvas shows ~0.35x on a phone).
# safe: bands that platform UI covers: (top, bottom, left, right) in canvas px; extra: list of (x0,y0,x1,y1) no-go rects.
SOCIAL = dict(display_scale=0.35, min_text_px=28, legal_min_px=24, max_kb=30000, text_ratio_warn=0.25,
              need_cta=False, headline_words=8, total_words=25)
DISPLAY = dict(display_scale=1.0, min_text_px=11, legal_min_px=9, max_kb=150, text_ratio_warn=0.35,
               need_cta=True, headline_words=7, total_words=20, border_check=True)
PLACEMENTS = {
    "meta_feed_1x1":   dict(SOCIAL, size=(1080, 1080), safe=(0, 0, 0, 0)),
    "meta_feed_4x5":   dict(SOCIAL, size=(1080, 1350), safe=(0, 0, 0, 0), extra_warn=[(0, 0, 1080, 135), (0, 1215, 1080, 1350)]),
    "meta_story_9x16": dict(SOCIAL, size=(1080, 1920), safe=(269, 672, 65, 65), min_text_px=32, legal_min_px=28),
    "tiktok_9x16":     dict(SOCIAL, size=(1080, 1920), safe=(240, 660, 120, 120), extra=[(780, 840, 1080, 1920)], min_text_px=32, legal_min_px=28),
    "universal_9x16":  dict(SOCIAL, size=(1080, 1920), safe=(270, 670, 120, 120), extra=[(900, 840, 1080, 1920)], min_text_px=32, legal_min_px=28),
    "linkedin_1x1":    dict(SOCIAL, size=(1200, 1200), safe=(0, 0, 0, 0)),
    "linkedin_1.91x1": dict(SOCIAL, size=(1200, 628), safe=(0, 0, 0, 0), min_text_px=24, legal_min_px=20),
    "pinterest_2x3":   dict(SOCIAL, size=(1000, 1500), safe=(0, 0, 0, 0), extra=[(850, 1275, 1000, 1500)]),
    "x_1x1":           dict(SOCIAL, size=(1200, 1200), safe=(0, 0, 0, 0)),
    "x_card_1.91x1":   dict(SOCIAL, size=(1200, 628), safe=(0, 0, 0, 0), extra=[(0, 528, 700, 628)], min_text_px=24, legal_min_px=20),
    "google_rda_1.91x1": dict(SOCIAL, size=(1200, 628), safe=(0, 0, 0, 0), no_text=True, no_brand_required=True, max_kb=5120),
    "google_rda_1x1":    dict(SOCIAL, size=(1200, 1200), safe=(0, 0, 0, 0), no_text=True, no_brand_required=True, max_kb=5120),
    "print_a3_bleed":  dict(display_scale=1.0, size=None, min_text_px=12, legal_min_px=9, max_kb=None, text_ratio_warn=0.4,
                            need_cta=False, headline_words=9, total_words=40, print_safe_mm=8),
    "print_a2_bleed":  dict(display_scale=1.0, size=None, min_text_px=14, legal_min_px=10, max_kb=None, text_ratio_warn=0.4,
                            need_cta=False, headline_words=9, total_words=40, print_safe_mm=8),
    "ooh_billboard":   dict(display_scale=1.0, size=None, min_text_px=0, legal_min_px=0, max_kb=None, text_ratio_warn=0.3,
                            need_cta=False, headline_words=7, total_words=9, safe_pct=0.10),
}
for w, h in [(300, 250), (336, 280), (728, 90), (160, 600), (120, 600), (300, 600), (300, 1050), (970, 250),
             (970, 90), (468, 60), (320, 50), (300, 50), (320, 100), (250, 250), (200, 200), (580, 400), (930, 180),
             (980, 120), (240, 400), (250, 360)]:
    spec = dict(DISPLAY, size=(w, h), safe=(0, 0, 0, 0))
    if h <= 100:
        spec.update(headline_words=5, total_words=10)
    if (w, h) in [(320, 50), (300, 50)]:
        spec.update(iab_lean_kb=50, need_cta=False)
    PLACEMENTS[f"display_{w}x{h}"] = spec

CRITICAL_AOIS = {"brand", "headline", "cta", "offer", "proof", "product_name"}


def parse_rgba(s):
    m = re.findall(r"[\d.]+", s)
    v = [float(x) for x in m[:4]] + [1.0] * (4 - len(m[:4]))
    return np.array(v[:3]) / 255.0, v[3] if len(m) >= 4 else 1.0


def rel_lum(rgb):
    rgb = np.asarray(rgb, dtype=float)
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722


def contrast(l1, l2):
    hi, lo = np.maximum(l1, l2), np.minimum(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def intersects(b, r):
    x0, y0, x1, y1 = r
    return b["x"] < x1 and b["x"] + b["w"] > x0 and b["y"] < y1 and b["y"] + b["h"] > y0


def union_area(rects, W, H):
    m = np.zeros((H, W), dtype=bool)
    for b in rects:
        x0, y0 = max(0, int(b["x"])), max(0, int(b["y"]))
        x1, y1 = min(W, int(np.ceil(b["x"] + b["w"]))), min(H, int(np.ceil(b["y"] + b["h"])))
        if x1 > x0 and y1 > y0:
            m[y0:y1, x0:x1] = True
    return m.mean()


def check_one(dom_path, overrides=None):
    dom = json.loads(Path(dom_path).read_text())
    stem = str(dom_path)[:-len(".dom.json")]
    placement = dom.get("placement") or ""
    spec = dict(PLACEMENTS.get(placement, SOCIAL if dom["canvas"]["w"] >= 600 else DISPLAY))
    spec.update((overrides or {}).get(dom["id"], {}))
    fails, warns, metrics = [], [], {}
    if placement not in PLACEMENTS:
        warns.append(f"unknown placement '{placement}', generic {'social' if spec is SOCIAL else 'display'} rules used")

    png = np.asarray(Image.open(f"{stem}.png").convert("RGB")).astype(float) / 255.0
    notext = np.asarray(Image.open(f"{stem}.notext.png").convert("RGB")).astype(float) / 255.0
    scale = dom["viewport"].get("scale", 1)
    H, W = png.shape[:2]
    cw, ch = int(round(dom["canvas"]["w"])), int(round(dom["canvas"]["h"]))

    # 1. dimensions
    if spec.get("size") and (cw, ch) != tuple(spec["size"]):
        fails.append(f"canvas {cw}x{ch} != spec {spec['size'][0]}x{spec['size'][1]}")
    metrics["canvas"] = f"{cw}x{ch}"

    # 2. file weight
    deliverable = Path(dom["deliverable"])
    kb = deliverable.stat().st_size / 1024 if deliverable.exists() else None
    metrics["file_kb"] = round(kb, 1) if kb else None
    if kb and spec.get("max_kb") and dom.get("format") != "pdf" and kb > spec["max_kb"]:
        fails.append(f"file {kb:.0f}KB > {spec['max_kb']}KB (export JPG/quantize PNG, flatten gradients)")
    if kb and spec.get("iab_lean_kb") and kb > spec["iab_lean_kb"]:
        warns.append(f"file {kb:.0f}KB > IAB LEAN {spec['iab_lean_kb']}KB for this size")

    # 3. off-canvas / overflow
    for o in dom["off_canvas"]:
        if placement.startswith("print") and o.get("aoi") is None and not o.get("text"):
            continue
        fails.append(f"element off canvas: {o['tag']} aoi={o['aoi']} '{o['text'][:30]}'")
    for t in dom["texts"]:
        if t["overflow_x"] or t["overflow_y"]:
            fails.append(f"text clipped/overflowing: '{t['text'][:40]}'")

    texts = dom["texts"]
    aois = {}
    for a in dom["aois"]:
        aois.setdefault(a["aoi"], []).append(a)

    # 4. RDA: no text at all
    if spec.get("no_text") and texts:
        fails.append(f"Google RDA image must contain no text/logo/button ({len(texts)} text nodes found)")

    # 5. required elements
    if not spec.get("no_brand_required") and "brand" not in aois:
        fails.append("no data-aoi='brand' element (brand must be identifiable)")
    if "headline" not in aois and not spec.get("no_text"):
        warns.append("no data-aoi='headline' element")
    if spec.get("need_cta") and "cta" not in aois:
        fails.append("display banner without data-aoi='cta'")

    # 6. font size, contrast
    disp = spec["display_scale"]
    min_contrast, worst = 99.0, None
    for t in texts:
        floor = spec["legal_min_px"] if t["aoi"] == "legal" else spec["min_text_px"]
        if t["font_size_px"] < floor:
            fails.append(f"font {t['font_size_px']:.0f}px < {floor}px floor: '{t['text'][:40]}'")
        rgb, alpha = parse_rgba(t["color"])
        if alpha == 0:
            continue  # gradient/clip text: cannot evaluate, flagged below
        large = t["font_size_px"] * disp >= 24 or (t["font_size_px"] * disp >= 18.66 and t["font_weight"] >= 700)
        need = 3.0 if large else 4.5
        for b in t["rects"]:
            x0, y0 = int(max(0, b["x"]) * scale), int(max(0, b["y"]) * scale)
            x1, y1 = int(min(cw, b["x"] + b["w"]) * scale), int(min(ch, b["y"] + b["h"]) * scale)
            if x1 <= x0 or y1 <= y0:
                continue
            bg = notext[y0:y1, x0:x1].reshape(-1, 3)
            fg = rgb * alpha + bg * (1 - alpha)
            c = contrast(rel_lum(fg), rel_lum(bg))
            c10 = float(np.percentile(c, 10))  # worst-case background pixels behind text
            if c10 < min_contrast:
                min_contrast, worst = c10, t["text"][:40]
            if c10 < need:
                fails.append(f"contrast {c10:.2f}:1 < {need}:1 for '{t['text'][:40]}' (add scrim/panel or change color)")
                break
    metrics["min_contrast"] = round(min_contrast, 2) if min_contrast < 99 else None
    metrics["min_contrast_text"] = worst
    if any(parse_rgba(t["color"])[1] == 0 for t in texts):
        warns.append("transparent/gradient-clipped text found: contrast not measurable, verify visually")

    # 7. safe zones
    top, bottom, left, right = spec.get("safe", (0, 0, 0, 0))
    bands = []
    if top: bands.append((0, 0, cw, top))
    if bottom: bands.append((0, ch - bottom, cw, ch))
    if left: bands.append((0, 0, left, ch))
    if right: bands.append((cw - right, 0, cw, ch))
    bands += spec.get("extra", [])
    if spec.get("print_safe_mm"):
        m = spec["print_safe_mm"] / 25.4 * 96
        bands += [(0, 0, cw, m), (0, ch - m, cw, ch), (0, 0, m, ch), (cw - m, 0, cw, ch)]
    if spec.get("safe_pct"):
        sx, sy = cw * spec["safe_pct"], ch * spec["safe_pct"]
        bands += [(0, 0, cw, sy), (0, ch - sy, cw, ch), (0, 0, sx, ch), (cw - sx, 0, cw, ch)]
    for t in texts:
        for b in t["rects"]:
            if any(intersects(b, r) for r in bands):
                fails.append(f"text in unsafe zone (platform UI covers it): '{t['text'][:40]}'")
                break
    for name in CRITICAL_AOIS:
        for a in aois.get(name, []):
            if any(intersects(a["box"], r) for r in bands):
                fails.append(f"aoi '{name}' intersects unsafe zone")
    for r in spec.get("extra_warn", []):
        for t in texts:
            if any(intersects(b, r) for b in t["rects"]):
                warns.append(f"text in crop-risk band (grid/preview crop): '{t['text'][:30]}'")
                break

    # 8. text density / copy length
    all_rects = [b for t in texts for b in t["rects"]]
    ratio = union_area(all_rects, cw, ch) if all_rects else 0.0
    metrics["text_area_ratio"] = round(float(ratio), 3)
    if ratio > spec["text_ratio_warn"] and not spec.get("no_text"):
        warns.append(f"text covers {ratio:.0%} of canvas (> {spec['text_ratio_warn']:.0%}); intentional text-led native format?")
    words = lambda s: len(re.findall(r"[\w$%€£¥'’.-]+", s))
    hw = sum(words(a["text"]) for a in aois.get("headline", []))
    tw = sum(words(t["text"]) for t in texts if t["aoi"] not in ("legal", "product"))  # UI text inside product mock-ups excluded
    metrics.update(headline_words=hw, total_words=tw)
    if hw > spec["headline_words"]:
        warns.append(f"headline {hw} words > {spec['headline_words']}")
    if tw > spec["total_words"]:
        warns.append(f"{tw} words on canvas (excl. legal) > {spec['total_words']}")

    # 8a. overlapping text from different text nodes (collisions the eye catches, DOM can't prevent)
    def core(r):  # glyph core: line boxes include ascent/descent slack, tight leading makes them overlap harmlessly
        return {"x": r["x"] + 0.02 * r["w"], "y": r["y"] + 0.22 * r["h"], "w": 0.96 * r["w"], "h": 0.56 * r["h"]}

    def inter(a, b):
        a, b = core(a), core(b)
        w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
        h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
        return w * h if w > 0 and h > 0 else 0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            hit = False
            for ra in texts[i]["rects"]:
                for rb in texts[j]["rects"]:
                    small = min(ra["w"] * ra["h"], rb["w"] * rb["h"]) * 0.54
                    # ignore line-box slack: require >25% of the smaller glyph box and vertical overlap beyond leading
                    if small and inter(ra, rb) > 0.25 * small:
                        hit = True
            ok = any(texts[k].get("aoi") == "overlap-ok" for k in (i, j))
            if hit and not ok:
                fails.append(f"text overlap: '{texts[i]['text'][:25]}' x '{texts[j]['text'][:25]}'")

    # 8b. placeholders left in the design
    ph = [t["text"][:40] for t in texts if re.search(r"placeholder|product photo|lorem ipsum|\[\[|TBD|xx+%", t["text"], re.I)]
    if ph:
        warns.append("PLACEHOLDER content still in ad: " + " | ".join(sorted(set(ph))[:3]))
    metrics["placeholders"] = sorted(set(ph))

    # 9. typefaces
    fams = sorted({t["font_family"].split(",")[0].strip().strip('"\'') for t in texts})
    metrics["font_families"] = fams
    if len(fams) > 3:
        fails.append(f"{len(fams)} font families (max 2, 3 only for price/legal): {fams}")
    elif len(fams) == 3:
        warns.append(f"3 font families: {fams}")

    # 10. light edge without border on display
    if spec.get("border_check"):
        edge = np.concatenate([png[:2].reshape(-1, 3), png[-2:].reshape(-1, 3), png[:, :2].reshape(-1, 3), png[:, -2:].reshape(-1, 3)])
        if rel_lum(edge).mean() > 0.87:
            warns.append("light outer edge: add 1px inset border (box-shadow: inset 0 0 0 1px #BDBDBD) so the banner separates from the page")

    # 11. CTA button contrast vs surroundings (non-text, WCAG 1.4.11 >= 3:1)
    for a in aois.get("cta", []):
        b = a["box"]
        x0, y0, x1, y1 = [int(v * scale) for v in (b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"])]
        pad = max(4, int(0.15 * min(x1 - x0, y1 - y0)))
        inner = notext[max(0, y0):y1, max(0, x0):x1].reshape(-1, 3)
        ring = np.concatenate([
            notext[max(0, y0 - pad):max(0, y0), max(0, x0):x1].reshape(-1, 3),
            notext[y1:y1 + pad, max(0, x0):x1].reshape(-1, 3),
            notext[max(0, y0):y1, max(0, x0 - pad):max(0, x0)].reshape(-1, 3),
            notext[max(0, y0):y1, x1:x1 + pad].reshape(-1, 3)])
        if len(inner) and len(ring):
            c = float(contrast(rel_lum(np.median(inner, 0)), rel_lum(np.median(ring, 0))))
            metrics["cta_vs_bg_contrast"] = round(c, 2)
            if c < 3.0:
                warns.append(f"CTA shape contrast vs surroundings {c:.2f}:1 < 3:1 (CTA may not pop)")

    # 12. thumbnail legibility via OCR (optional)
    try:
        import pytesseract
        heads = " ".join(a["text"] for a in aois.get("headline", []))
        if heads and disp < 1:
            small = Image.open(f"{stem}.png").convert("L")
            small = small.resize((max(1, int(W * disp)), max(1, int(H * disp))), Image.LANCZOS)
            small = small.resize((small.width * 3, small.height * 3), Image.LANCZOS)  # OCR upsampling, legibility already lost if lost
            txt = pytesseract.image_to_string(small)
            norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
            r = difflib.SequenceMatcher(None, norm(heads), norm(txt)).find_longest_match(0, len(norm(heads)), 0, len(norm(txt)))
            ratio_ocr = r.size / max(1, len(norm(heads)))
            metrics["ocr_headline_recovery"] = round(ratio_ocr, 2)
            if ratio_ocr < 0.5:
                warns.append(f"headline only {ratio_ocr:.0%} OCR-recoverable at phone display size (legibility risk; stylised fonts also lower this)")
    except Exception as e:  # tesseract absent or failed: not a gate
        metrics["ocr_headline_recovery"] = None

    return {"id": dom["id"], "concept": dom.get("concept"), "placement": placement,
            "pass": not fails, "fails": sorted(set(fails)), "warnings": sorted(set(warns)), "metrics": metrics}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--json", default=None)
    ap.add_argument("--manifest", default=None, help="manifest with optional per-ad 'spec' overrides")
    a = ap.parse_args()
    overrides = {}
    if a.manifest:
        for ad in json.loads(Path(a.manifest).read_text())["ads"]:
            if "spec" in ad:
                overrides[ad["id"]] = ad["spec"]
    results = [check_one(p, overrides) for p in sorted(Path(a.out_dir).glob("*.dom.json"))]
    for r in results:
        print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['id']}  ({r['placement']})  {r['metrics']}")
        for f in r["fails"]:
            print(f"   FAIL: {f}")
        for w in r["warnings"]:
            print(f"   warn: {w}")
    Path(a.json or Path(a.out_dir) / "qa.json").write_text(json.dumps(results, indent=1))
    sys.exit(0 if all(r["pass"] for r in results) else 1)


if __name__ == "__main__":
    main()
