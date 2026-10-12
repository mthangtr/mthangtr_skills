#!/usr/bin/env python3
"""Render ad HTML files to PNG/JPG/PDF with headless Chromium and record DOM geometry.

Usage:
    python scripts/render.py manifest.json [--out out/]

manifest.json:
{
  "ads": [
    {"id": "c1-feed", "html": "html/c1.html", "width": 1080, "height": 1350,
     "placement": "meta_feed_4x5", "concept": "c1", "format": "png"},
    {"id": "c1-poster", "html": "html/c1-poster.html", "width_mm": 303, "height_mm": 426,
     "placement": "print_a3_bleed", "concept": "c1", "format": "pdf"}
  ]
}

HTML contract (see references/engineering.md):
  * The canvas is the <body> (or #ad) at exactly width x height CSS px, overflow hidden.
  * Tag key elements with data-aoi="brand|headline|product|cta|offer|face|proof|legal".
  * Fonts must be local (@font-face url(...) relative) or system; Google Fonts allowed if network permits.

Outputs per ad in --out:
  <id>.png (or .jpg/.pdf), <id>.notext.png (text made transparent; used for contrast sampling),
  <id>.dom.json (AOI boxes, text nodes with computed styles, overflow flags, font families).
"""
import argparse, json, os, sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright missing: pip install playwright (do not download browsers if Chromium is preinstalled)")

DOM_JS = r"""
() => {
  const root = document.querySelector('#ad') || document.body;
  const rb = root.getBoundingClientRect();
  const box = r => ({x: r.left - rb.left, y: r.top - rb.top, w: r.width, h: r.height});
  const aois = [...document.querySelectorAll('[data-aoi]')].map(el => ({
    aoi: el.dataset.aoi, box: box(el.getBoundingClientRect()), text: (el.innerText || '').trim().slice(0, 200)
  }));
  const texts = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const n = walker.currentNode;
    if (!n.textContent.trim()) continue;
    const el = n.parentElement;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    const rects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0);
    if (!rects.length) continue;
    const aoiEl = el.closest('[data-aoi]');
    texts.push({
      text: n.textContent.trim().slice(0, 200),
      rects: rects.map(box),
      font_size_px: parseFloat(cs.fontSize),
      font_weight: parseInt(cs.fontWeight) || 400,
      font_family: cs.fontFamily,
      color: (el instanceof SVGElement && cs.fill && cs.fill.startsWith('rgb')) ? cs.fill : cs.color,
      aoi: aoiEl ? aoiEl.dataset.aoi : null,
      overflow_x: el.scrollWidth > el.clientWidth + 1 && cs.overflow !== 'visible',
      overflow_y: el.scrollHeight > el.clientHeight + 1 && cs.overflow !== 'visible'
    });
  }
  const offCanvas = [...root.querySelectorAll('*')].filter(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const hasText = [...el.childNodes].some(c => c.nodeType === 3 && c.textContent.trim());
    if (!hasText && !el.dataset.aoi) return false;
    return r.left < rb.left - 0.5 || r.top < rb.top - 0.5 || r.right > rb.right + 0.5 || r.bottom > rb.bottom + 0.5;
  }).map(el => ({tag: el.tagName, aoi: el.dataset.aoi || null, text: (el.innerText||'').slice(0,60), box: box(el.getBoundingClientRect())}));
  // Families actually used to render: document.fonts tells which faces loaded.
  const loaded = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g,''));
  return {canvas: {w: rb.width, h: rb.height}, aois, texts, off_canvas: offCanvas, fonts_loaded: [...new Set(loaded)]};
}
"""

HIDE_TEXT_CSS = "text,tspan{fill:transparent!important;stroke:transparent!important}*{color:transparent!important;text-decoration-color:transparent!important;-webkit-text-stroke:0!important;text-shadow:none!important;caret-color:transparent!important}"


def mm_to_px(mm):
    return round(mm / 25.4 * 96)


def render(manifest_path, out_dir, chromium_path=None):
    manifest = json.loads(Path(manifest_path).read_text())
    base = Path(manifest_path).parent
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    launch = {"args": ["--font-render-hinting=none", "--disable-lcd-text"]}
    exe = chromium_path or os.environ.get("CHROMIUM_PATH")
    if exe:
        launch["executable_path"] = exe
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        for ad in manifest["ads"]:
            fmt = ad.get("format", "png")
            if fmt == "pdf":
                w, h = mm_to_px(ad["width_mm"]), mm_to_px(ad["height_mm"])
            else:
                w, h = ad["width"], ad["height"]
            scale = ad.get("scale", 1)
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=scale)
            page = ctx.new_page()
            page.goto((base / ad["html"]).resolve().as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(ad.get("wait_ms", 150))
            dom = page.evaluate(DOM_JS)
            dom.update({k: ad.get(k) for k in ("id", "placement", "concept", "format")})
            dom["viewport"] = {"w": w, "h": h, "scale": scale}
            stem = out / ad["id"]
            if fmt == "pdf":
                page.pdf(path=f"{stem}.pdf", width=f"{ad['width_mm']}mm", height=f"{ad['height_mm']}mm",
                         print_background=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
                page.screenshot(path=f"{stem}.png", clip={"x": 0, "y": 0, "width": w, "height": h})
            elif fmt == "jpg":
                page.screenshot(path=f"{stem}.jpg", type="jpeg", quality=ad.get("quality", 85),
                                clip={"x": 0, "y": 0, "width": w, "height": h})
                page.screenshot(path=f"{stem}.png", clip={"x": 0, "y": 0, "width": w, "height": h})
            else:
                page.screenshot(path=f"{stem}.png", clip={"x": 0, "y": 0, "width": w, "height": h})
            page.add_style_tag(content=HIDE_TEXT_CSS)
            page.wait_for_timeout(50)
            page.screenshot(path=f"{stem}.notext.png", clip={"x": 0, "y": 0, "width": w, "height": h})
            dom["deliverable"] = f"{stem}.{fmt}"
            Path(f"{stem}.dom.json").write_text(json.dumps(dom, indent=1))
            results.append({"id": ad["id"], "deliverable": dom["deliverable"], "aois": len(dom["aois"]),
                            "off_canvas": len(dom["off_canvas"])})
            ctx.close()
        browser.close()
    for r in results:
        warn = "  <-- elements off canvas" if r["off_canvas"] else ""
        noaoi = "  <-- no data-aoi tags (attention/QA will be weak)" if not r["aois"] else ""
        print(f"{r['id']}: {r['deliverable']}{warn}{noaoi}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--out", default="out")
    ap.add_argument("--chromium", default=None, help="Chromium executable (or set CHROMIUM_PATH)")
    a = ap.parse_args()
    render(a.manifest, a.out, a.chromium)
