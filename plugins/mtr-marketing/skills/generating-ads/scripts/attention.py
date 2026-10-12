#!/usr/bin/env python3
"""Predicted-attention + clutter metrics for rendered ads (pre-launch proxy, NOT a CTR forecast).

Usage:
    python scripts/attention.py out/                 # all out/*.dom.json
    python scripts/attention.py out/ --model auto|deepgaze|classic

Model chain (label is written to the output so reports state which one produced numbers):
  deepgaze : DeepGaze IIE (pip install git+https://github.com/matthias-k/DeepGaze.git; needs torch and
             egress to github/bitbucket/download.pytorch.org on first run; repo has no LICENSE -> research use)
  classic  : blend of spectral-residual + frequency-tuned colour pop-out + luminance centre-surround,
             with a centre bias (numpy/OpenCV only). Instant, CPU, but biased toward text edges -> treat as LOW confidence.

Per ad writes <id>.attention.png (heatmap overlay) and aggregates out/attention.json with:
  aoi_share     share of predicted attention inside each data-aoi box (brand/headline/cta/product/...)
  aoi_density   share / area fraction (>1 = element pulls more than its size)
  first_fix     greedy fixation order (inhibition of return), top 6
  in_first3     AOIs reached in the first 3 predicted fixations
  focus         1 - normalized entropy of the map (higher = single clear focal point)
  peaks         number of separated hotspots >= 50% of max (1-3 good, >4 scattered)
  edge_density  Canny edge pixel fraction (feature clutter proxy, Pieters et al. 2010)
  jpeg_bpp      JPEG bytes/pixel at q90 (feature-complexity proxy used by Pieters et al. 2010)
Clutter numbers are only meaningful relative to the other candidates of the same size.
"""
import argparse, io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None


def _norm(m):
    m = m.astype(np.float64)
    m -= m.min()
    s = m.sum()
    return m / s if s > 0 else np.full_like(m, 1.0 / m.size)


def _blur(m, sigma):
    if cv2 is not None:
        return cv2.GaussianBlur(m, (0, 0), sigma)
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(m, sigma)


def center_bias(h, w):
    y, x = np.mgrid[0:h, 0:w]
    sy, sx = h * 0.35, w * 0.35
    return np.exp(-(((x - w / 2) ** 2) / (2 * sx ** 2) + ((y - h / 2) ** 2) / (2 * sy ** 2)))


def _spectral_residual(gray):
    """Hou & Zhang 2007, numpy implementation (works without opencv-contrib)."""
    g = np.asarray(Image.fromarray(gray).resize((64, max(8, int(64 * gray.shape[0] / gray.shape[1]))), Image.BILINEAR), dtype=np.float64)
    f = np.fft.fft2(g)
    logamp, phase = np.log(np.abs(f) + 1e-9), np.angle(f)
    k = np.ones((3, 3)) / 9.0
    pad = np.pad(logamp, 1, mode="edge")
    avg = sum(pad[i:i + logamp.shape[0], j:j + logamp.shape[1]] * k[i, j] for i in range(3) for j in range(3))
    sr = np.abs(np.fft.ifft2(np.exp(logamp - avg + 1j * phase))) ** 2
    sr = np.asarray(Image.fromarray(sr.astype(np.float32)).resize((gray.shape[1], gray.shape[0]), Image.BILINEAR), dtype=np.float64)
    return sr


def _center_surround(lum, w):
    """Itti-style multi-scale luminance contrast (difference of Gaussians)."""
    out = np.zeros_like(lum)
    for c, s in [(w / 100, w / 25), (w / 50, w / 12), (w / 25, w / 6)]:
        out += np.abs(_blur(lum, c) - _blur(lum, s))
    return out


def classic_saliency(rgb):
    """rgb uint8 HxWx3 at working resolution -> probability map.
    Blend: spectral residual (Hou & Zhang 2007) + frequency-tuned colour pop-out (Achanta 2009)
    + multi-scale luminance centre-surround (Itti 1998), with a mild centre bias."""
    h, w = rgb.shape[:2]
    gray = np.asarray(Image.fromarray(rgb).convert("L"))
    maps = [_norm(_blur(_spectral_residual(gray), max(2, w / 60)))]
    if cv2 is not None:
        bgr = rgb[..., ::-1].copy()
        lab = cv2.cvtColor(cv2.GaussianBlur(bgr, (5, 5), 0), cv2.COLOR_BGR2LAB).astype(np.float64)
    else:
        lab = rgb.astype(np.float64)
    d = lab - lab.reshape(-1, 3).mean(0)
    ft = np.sqrt(d[..., 0] ** 2 + 4.0 * (d[..., 1] ** 2 + d[..., 2] ** 2))  # chroma singletons pop out pre-attentively
    maps.append(_norm(_blur(ft, max(2, w / 60))))
    maps.append(_norm(_blur(_center_surround(gray.astype(np.float64), w), max(2, w / 80))))
    sal = np.mean([m / m.max() for m in maps], axis=0)
    sal = sal * (0.6 + 0.4 * center_bias(h, w))
    return _norm(_blur(sal, max(1.5, w / 120)))


_DG = None


def deepgaze_saliency(rgb):
    global _DG
    import torch
    import deepgaze_pytorch
    if _DG is None:
        _DG = deepgaze_pytorch.DeepGazeIIE(pretrained=True).eval()
    h, w = rgb.shape[:2]
    img = torch.tensor(rgb.transpose(2, 0, 1)[None].astype(np.float32))
    cb = torch.tensor(np.zeros((1, h, w), dtype=np.float32))  # uniform centre bias (log density)
    with torch.no_grad():
        logd = _DG(img, cb).numpy()[0, 0]
    return _norm(np.exp(logd - logd.max()))


def fixations(sal, k=6, radius=None):
    s = sal.copy()
    h, w = s.shape
    r = radius or 0.06 * max(h, w)
    y, x = np.mgrid[0:h, 0:w]
    pts = []
    for _ in range(k):
        i = int(np.argmax(s))
        py, px = divmod(i, w)
        pts.append((px, py))
        s[(x - px) ** 2 + (y - py) ** 2 <= r * r] = 0
    return pts


def count_peaks(sal):
    sal = _blur(sal, max(2, sal.shape[1] / 30))  # merge glyph-level speckle into regions
    m = sal / sal.max()
    mask = (m >= 0.5).astype(np.uint8)
    if cv2 is None:
        from scipy.ndimage import label
        return int(label(mask)[1])
    n, _ = cv2.connectedComponents(mask)
    return int(n - 1)


def analyse(dom_path, model):
    dom = json.loads(Path(dom_path).read_text())
    stem = str(dom_path)[:-len(".dom.json")]
    im = Image.open(f"{stem}.png").convert("RGB")
    cw, ch = dom["canvas"]["w"], dom["canvas"]["h"]
    work = 512 / max(im.size) if max(im.size) > 512 else 1.0
    small = im.resize((max(8, int(im.width * work)), max(8, int(im.height * work))), Image.LANCZOS)
    rgb = np.asarray(small)
    used = "classic"
    if model in ("auto", "deepgaze"):
        try:
            sal = deepgaze_saliency(rgb)
            used = "deepgaze_iie"
        except Exception as e:
            if model == "deepgaze":
                sys.exit(f"DeepGaze unavailable: {e}")
            sal = classic_saliency(rgb)
    else:
        sal = classic_saliency(rgb)
    h, w = sal.shape
    sx, sy = w / cw, h / ch

    shares, density = {}, {}
    masks = {}
    for a in dom["aois"]:
        b = a["box"]
        x0, y0 = int(max(0, b["x"]) * sx), int(max(0, b["y"]) * sy)
        x1, y1 = int(np.ceil(min(cw, b["x"] + b["w"]) * sx)), int(np.ceil(min(ch, b["y"] + b["h"]) * sy))
        m = masks.setdefault(a["aoi"], np.zeros_like(sal, dtype=bool))
        m[y0:y1, x0:x1] = True
    for name, m in masks.items():
        shares[name] = round(float(sal[m].sum()), 3)
        density[name] = round(float(sal[m].sum() / max(m.mean(), 1e-6)), 2)

    fx = fixations(sal)
    order = []
    for px, py in fx:
        hit = [n for n, m in masks.items() if m[py, px]]
        order.append(hit[0] if hit else "background")
    first3 = sorted({o for o in order[:3] if o != "background"})

    ent = -(sal[sal > 0] * np.log(sal[sal > 0])).sum() / np.log(sal.size)
    gray = np.asarray(im.convert("L"))
    edge = float((cv2.Canny(gray, 100, 200) > 0).mean()) if cv2 is not None else None
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=90)
    bpp = buf.tell() / (im.width * im.height)

    # overlay
    heat = (sal / sal.max() * 255).astype(np.uint8)
    heat = np.asarray(Image.fromarray(heat).resize(im.size, Image.BILINEAR))
    if cv2 is not None:
        col = cv2.applyColorMap(heat, cv2.COLORMAP_JET)[..., ::-1]
    else:
        col = np.stack([heat, np.zeros_like(heat), 255 - heat], -1)
    over = (np.asarray(im) * 0.55 + col * 0.45).astype(np.uint8)
    ov = Image.fromarray(over)
    try:
        from PIL import ImageDraw
        d = ImageDraw.Draw(ov)
        rr = max(6, int(0.012 * max(im.size)))
        for i, (px, py) in enumerate(fx[:3]):
            X, Y = px / sx * (im.width / cw), py / sy * (im.height / ch)
            d.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=(255, 255, 255), width=max(2, rr // 3))
            d.text((X + rr + 2, Y - rr), str(i + 1), fill=(255, 255, 255))
    except Exception:
        pass
    ov.save(f"{stem}.attention.png")

    return {"id": dom["id"], "concept": dom.get("concept"), "placement": dom.get("placement"), "model": used,
            "confidence": "medium" if used == "deepgaze_iie" else "low",
            "aoi_share": shares, "aoi_density": density, "first_fix": order, "in_first3": first3,
            "focus": round(float(1 - ent), 3), "peaks": count_peaks(sal),
            "edge_density": round(edge, 4) if edge is not None else None, "jpeg_bpp": round(bpp, 4),
            "overlay": f"{stem}.attention.png"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--model", default="auto", choices=["auto", "deepgaze", "classic"])
    a = ap.parse_args()
    res = [analyse(p, a.model) for p in sorted(Path(a.out_dir).glob("*.dom.json"))]
    for r in res:
        s = ", ".join(f"{k} {v:.0%}" for k, v in sorted(r["aoi_share"].items(), key=lambda kv: -kv[1]))
        print(f"{r['id']} [{r['model']}]: {s} | first3={r['in_first3']} focus={r['focus']} peaks={r['peaks']} edges={r['edge_density']}")
    (Path(a.out_dir) / "attention.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
