#!/usr/bin/env python3
"""temporal_qc.py - flag flicker / boiling / jump candidates in a take.
Usage: python temporal_qc.py take.mp4 --out take_temporal.csv [--z 3.5]
Outputs per-frame CSV + prints suspicious timestamps to extract as bursts (5.4)."""
import argparse, csv, cv2, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out", default="temporal.csv")
ap.add_argument("--z", type=float, default=3.5); ap.add_argument("--width", type=int, default=480)
ap.add_argument("--min-dluma", type=float, default=1.5)   # absolute floor, 0-255 luma units
a = ap.parse_args()
cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
prev = None; rows = []; i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    h, w = f.shape[:2]; f = cv2.resize(f, (a.width, int(h * a.width / w)))
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); luma = float(g.mean())
    r = dict(frame=i, t=round(i / fps, 3), luma=round(luma, 2), dluma=0.0, flow_mean=0.0, flow_p95=0.0, warp_resid=0.0)
    if prev is not None:
        flow = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.linalg.norm(flow, axis=2)
        hh, ww = g.shape; gx, gy = np.meshgrid(np.arange(ww), np.arange(hh))
        warped = cv2.remap(prev, (gx - flow[..., 0]).astype(np.float32), (gy - flow[..., 1]).astype(np.float32), cv2.INTER_LINEAR)
        # residual = change that motion cannot explain -> flicker, boiling, popping, morphing
        r.update(dluma=round(luma - rows[-1]["luma"], 2), flow_mean=round(float(mag.mean()), 3),
                 flow_p95=round(float(np.percentile(mag, 95)), 3),
                 warp_resid=round(float(np.abs(warped.astype(np.float32) - g.astype(np.float32)).mean()), 3))
    rows.append(r); prev = g; i += 1
with open(a.out, "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
def flag(key, floor=0.0):
    v = np.array([r[key] for r in rows[1:]], dtype=float)
    if len(v) < 5: return []
    med = np.median(v); mad = np.median(np.abs(v - med)) + 1e-6
    z = np.abs(v - med) / (1.4826 * mad)
    return [rows[j + 1]["t"] for j in np.where((z > a.z) & (np.abs(v) > floor))[0]]
for key, label, floor in [("dluma", "FLICKER? luma jump", a.min_dluma),
                          ("warp_resid", "BOILING/POP/MORPH? motion-unexplained change", 0.0),
                          ("flow_p95", "JUMP/SMEAR? motion spike", 0.0)]:
    hits = flag(key, floor); print(f"{label}: {len(hits)} frames", hits[:25])
print(f"frames={len(rows)} fps={fps:.3f} -> {a.out}")
