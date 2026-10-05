#!/usr/bin/env python3
"""Measure a rendered film. Needs ffmpeg/ffprobe on PATH and numpy.

  python3 qa.py report <film.mp4>                 # everything below + PASS/FAIL table against the quality bar
  python3 qa.py sheets <film.mp4> [--strip 2.4,4.0]  # contact.png, phone.png, frame0.png, last.png, strip_<t>.png
  python3 qa.py frozen <film.mp4> [--thr 0.35] [--max-hold 0.6]
  python3 qa.py pops   <film.mp4>
  python3 qa.py space  <film.mp4>                 # content bounding box per sampled frame (empty-frame detector)
  python3 qa.py loudness <film.mp4|mix.wav>

Numbers measure; they do not judge taste. Always LOOK at the sheets too.
"""
import json, os, subprocess, sys
import numpy as np

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=kw.pop("text", True), **kw)

def probe(f):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,nb_frames:format=duration",
             "-of", "json", f])
    j = json.loads(r.stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = v["r_frame_rate"].split("/")
    return dict(w=int(v["width"]), h=int(v["height"]), fps=float(num) / float(den),
                dur=float(j["format"]["duration"]), audio=any(s["codec_type"] == "audio" for s in j["streams"]))

def gray_frames(f, w=192, h=108, fps=None):
    vf = (f"fps={fps}," if fps else "") + f"scale={w}:{h}:flags=area,format=gray"
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", vf, "-f", "rawvideo", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8)
    return a.reshape(-1, h, w).astype(np.float32)

def diffs(fr):
    return np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))  # mean abs luma diff, 0..255

def frozen(f, thr=0.35, max_hold=0.6, sample_fps=10):
    # luma diff between samples 0.1 s apart (calibrated: <0.35/255 reads as "nothing moves").
    # Film grain/noise hides holds: measure a grain-free render.
    p = probe(f); fr = gray_frames(f, 320, 180, sample_fps); d = diffs(fr); fps = sample_fps
    still = d < thr
    holds, start = [], None
    for i, s in enumerate(list(still) + [False]):
        if s and start is None: start = i
        if not s and start is not None:
            holds.append(((start + 1) / fps, (i + 1) / fps)); start = None
    end = len(d) / fps
    if holds and holds[-1][1] >= end - 0.15:                    # the final CTA may hold up to 2 s
        a, b = holds[-1]; holds[-1] = (a, max(a, b - 2.0))
    holds = [(a, b) for a, b in holds if b - a >= 0.2 - 1e-9]  # a single slow 0.1 s sample is not a hold
    long_ = [(a, b) for a, b in holds if b - a > max_hold]
    total = sum(b - a for a, b in holds)
    return dict(frozen_total_s=round(total, 2), holds_over_max=[(round(a, 2), round(b, 2)) for a, b in long_],
                per_30s=round(total / p["dur"] * 30, 2))

def pops(f, k=3.0, floor=1.0):
    # an isolated one-frame spike: much bigger than BOTH neighbours. Fast eased moves span several
    # frames and do not trigger; a hard cut does (fine if it is an intended cut on a beat - say so).
    p = probe(f); d = diffs(gray_frames(f)); out = []
    for i in range(1, len(d) - 1):
        if d[i] > floor and d[i] > k * max(d[i - 1], d[i + 1], 0.05):
            out.append(round((i + 1) / p["fps"], 3))
    return out  # single-frame spikes: a cut on a beat is fine IF intended; anything else is a pop to fix

def space(f, sample_fps=2):
    # span of sharp content (edges, so flat colour fields and glows don't count as background or content):
    # max(width share, height share) of the 2nd-98th percentile box of edge pixels. < 0.45 = small subject.
    fr = gray_frames(f, 320, 180, sample_fps); res = []
    for i, g in enumerate(fr):
        gx = np.abs(np.diff(g, axis=1))[:-1, :]; gy = np.abs(np.diff(g, axis=0))[:, :-1]; m = (gx + gy) > 40
        if m.sum() < 20: res.append((i / sample_fps, 0.0)); continue
        ys, xs = np.nonzero(m)
        x0, x1 = np.percentile(xs, [2, 98]); y0, y1 = np.percentile(ys, [2, 98])
        res.append((i / sample_fps, float(max((x1 - x0) / 319, (y1 - y0) / 179))))
    return res

def edge_density(g):
    gx = np.abs(np.diff(g, axis=1))[:-1, :]; gy = np.abs(np.diff(g, axis=0))[:, :-1]
    return float(((gx + gy) > 40).mean())

def frame0_coverage(f):
    # share of sharp-edge pixels in frame 0 at 640x360: a lone dot or a glow scores ~0, a set headline ~1-3 %
    return edge_density(gray_frames(f, 640, 360)[0])

def loudness(f):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"])
    txt = r.stderr; tail = txt[txt.rfind("Summary:"):]
    def grab(key):
        for line in tail.splitlines():
            if line.strip().startswith(key):
                try: return float(line.split(":")[1].split()[0])
                except Exception: return None
    return dict(I_LUFS=grab("I:"), LRA_LU=grab("LRA:"), TruePeak_dBFS=grab("Peak:"))

def sheets(f, strips=()):
    p = probe(f); base = os.path.splitext(f)[0]
    n = int(p["dur"] * 2); cols = 6; rows = max(1, -(-n // cols))
    cmds = [
        ["-vf", f"fps=2,scale=320:-2,tile={cols}x{rows}", "-frames:v", "1", base + "_contact.png"],
        ["-vf", f"fps=1,scale=360:-2,tile=5x{max(1, -(-int(p['dur']) // 5))}", "-frames:v", "1", base + "_phone.png"],
        ["-vf", "select=eq(n\\,0)", "-frames:v", "1", base + "_frame0.png"],
    ]
    for c in cmds: run(["ffmpeg", "-y", "-v", "error", "-i", f] + c)
    run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.1", "-i", f, "-frames:v", "1", base + "_last.png"])
    for t in strips:
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(max(0, t - 0.1)), "-i", f, "-vf", "scale=320:-2,tile=12x1",
             "-frames:v", "1", f"{base}_strip_{t}.png"])
    return [base + s for s in ("_contact.png", "_phone.png", "_frame0.png", "_last.png")] + [f"{base}_strip_{t}.png" for t in strips]

def report(f):
    p = probe(f); fz = frozen(f); pp = pops(f); sp = space(f); cov = frame0_coverage(f)
    lo = loudness(f) if p["audio"] else None
    sparse = [round(t, 1) for t, a in sp if a < 0.45]
    files = sheets(f)
    # status: True = PASS, False = FAIL, None = WARN (heuristic: look at the sheet and decide)
    rows = [
        ("frame 0 is a finished composition (edge density >= 0.3%; X uses it as the thumbnail)", f"{cov*100:.2f}%", cov >= 0.003),
        ("frozen time <= 1 s per 30 s", f"{fz['per_30s']} s/30s", fz["per_30s"] <= 1.0),
        ("no hold > 0.6 s (final CTA may hold 2 s)", str(fz["holds_over_max"]) if fz["holds_over_max"] else "none",
         not fz["holds_over_max"]),
        ("single-frame pops (explain each or fix)", str(pp) if pp else "none", not pp),
        ("sampled frames whose sharp content spans < 45% of width and height (heuristic: lead subject fills 60-85%)",
         str(sparse) if sparse else "none", True if not sparse else None),
    ]
    if lo:
        rows += [("integrated loudness -14 +-1 LUFS (calm: -16..-19 ok if intended)", f"{lo['I_LUFS']}",
                  lo["I_LUFS"] is not None and -15.0 <= lo["I_LUFS"] <= -13.0),
                 ("true peak <= -1 dBFS", f"{lo['TruePeak_dBFS']}", lo["TruePeak_dBFS"] is not None and lo["TruePeak_dBFS"] <= -1.0)]
    else:
        rows.append(("audio track present", "none", False))
    print(f"{f}: {p['w']}x{p['h']} {p['fps']:.2f} fps {p['dur']:.2f} s")
    for name, val, ok in rows: print(f"  [{ {True: 'PASS', False: 'FAIL', None: 'WARN'}[ok] }] {name}: {val}")
    print("  sheets to LOOK at:", *files, sep="\n    ")
    return all(ok is not False for _, _, ok in rows)

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    mode, f = sys.argv[1], sys.argv[2]
    args = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    if mode == "report": sys.exit(0 if report(f) else 2)
    elif mode == "sheets": print(*sheets(f, [float(x) for x in args.get("--strip", "").split(",") if x]), sep="\n")
    elif mode == "frozen": print(frozen(f, float(args.get("--thr", 0.35)), float(args.get("--max-hold", 0.6))))
    elif mode == "pops": print(pops(f))
    elif mode == "space": print([(round(t, 1), round(a, 2)) for t, a in space(f)])
    elif mode == "loudness": print(loudness(f))
    else: print(__doc__); sys.exit(1)
