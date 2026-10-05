#!/usr/bin/env python3
"""Audio tools for code-rendered films. Needs ffmpeg on PATH and numpy.

  python3 audio.py drop  <track.mp3> [--from 8 --to 24]    # find the REAL drop by low-band energy (never trust a beat grid)
  python3 audio.py bpm   <track.mp3>                        # rough tempo from onset autocorrelation (verify by ear/grid)
  python3 audio.py peak  <sfx.wav>                          # offset of the loudest sample (place SFX by this, not by file start)
  python3 audio.py mix   <cues.json> --out out/mix.wav      # music offset to the drop + SFX by peak + two-pass loudnorm
  python3 audio.py synth <click|tick|pop|thump|whoosh|riser> --out sfx.wav [--dur 0.4]

cues.json:
{
  "duration": 8.0, "target_lufs": -14, "true_peak": -1.0,
  "music": {"file": "assets/track.mp3", "drop_in_song": 16.09, "drop_in_film": 4.0, "gain_db": -3, "fade_out": 0.6},
  "sfx": [
    {"file": "sfx/whoosh.mp3", "t": 3.85, "gain": 0.25, "align": "peak"},
    {"synth": "click", "t": 1.0, "gain": 0.2},
    {"synth": "riser", "t": 4.0, "dur": 1.2, "gain": 0.15, "align": "end"}
  ]
}
align: "peak" (default, the sample's loudest point lands on t), "start", or "end".
"""
import json, os, subprocess, sys, wave
import numpy as np

SR = 48000

def decode(path, sr=SR, ch=2):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"], capture_output=True)
    if r.returncode: sys.exit(f"cannot decode {path}: {r.stderr.decode()[-300:]}")
    return np.frombuffer(r.stdout, np.float32).reshape(-1, ch).copy()

def write_wav(path, x, sr=SR):
    x = np.clip(x, -1, 1); os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())

def band_energy(mono, sr, lo, hi, hop=0.02, win=0.04):
    n, h = int(win * sr), int(hop * sr); f = np.fft.rfftfreq(n, 1 / sr); m = (f >= lo) & (f < hi)
    w = np.hanning(n); out = []
    for i in range(0, len(mono) - n, h):
        out.append(float((np.abs(np.fft.rfft(mono[i:i + n] * w))[m] ** 2).sum()))
    return np.array(out), hop

def drop(path, t0=0.0, t1=None):
    x = decode(path, ch=1)[:, 0]; t1 = t1 or len(x) / SR
    e, hop = band_energy(x, SR, 20, 150)
    e = np.log10(e + 1e-9); k = int(0.4 / hop)          # compare 400 ms after vs before each 20 ms step
    score = np.array([e[i:i + k].mean() - e[max(0, i - k):i].mean() if i >= k else -9 for i in range(len(e) - k)])
    idx = [i for i in np.argsort(score)[::-1] if t0 <= i * hop + 0.02 <= t1]
    picks = []
    for i in idx:
        if all(abs(i - j) * hop > 1.0 for j in picks): picks.append(i)
        if len(picks) == 3: break
    return [(round(i * hop + 0.02, 3), round(float(score[i]), 2)) for i in picks]

def bpm(path):
    x = decode(path, ch=1)[:, 0][: SR * 60]
    e, hop = band_energy(x, SR, 20, 8000, hop=0.01, win=0.02)
    on = np.maximum(0, np.diff(np.log10(e + 1e-9))); on -= on.mean()
    ac = np.correlate(on, on, "full")[len(on) - 1:]
    lags = np.arange(len(ac)) * hop; ok = (lags > 60 / 180) & (lags < 60 / 60)
    best = lags[ok][np.argmax(ac[ok])]
    return round(60 / best, 1)

def peak_offset(x):
    return int(np.argmax(np.abs(x).max(axis=1)))

def synth(kind, dur=None, sr=SR):
    rng = np.random.default_rng(7)                         # seeded: same mix every time
    def env(n, a, d): t = np.arange(n) / sr; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    if kind in ("click", "tick"):
        n = int(0.04 * sr); t = np.arange(n) / sr; f = 3200 if kind == "click" else 6000
        y = np.sin(2 * np.pi * f * t) * env(n, 0.0005, 0.006) + rng.normal(0, 0.3, n) * env(n, 0.0002, 0.0015)
    elif kind == "pop":
        n = int(0.08 * sr); t = np.arange(n) / sr; f = 300 + 900 * t / 0.08
        y = np.sin(2 * np.pi * np.cumsum(f) / sr) * env(n, 0.001, 0.025)
    elif kind == "thump":
        n = int(0.3 * sr); t = np.arange(n) / sr; f = 45 + 75 * np.exp(-t / 0.04)
        y = np.sin(2 * np.pi * np.cumsum(f) / sr) * env(n, 0.002, 0.09)
    elif kind in ("whoosh", "riser"):
        d = dur or (0.45 if kind == "whoosh" else 1.2); n = int(d * sr)
        noise = rng.normal(0, 1, n); spec = np.fft.rfft(noise); fr = np.fft.rfftfreq(n, 1 / sr)
        spec *= ((fr > 250) & (fr < 7000)) * (1 / np.sqrt(np.maximum(fr, 1) / 250)); noise = np.fft.irfft(spec, n)
        noise /= np.abs(noise).max() + 1e-9
        shape = np.hanning(n) if kind == "whoosh" else (np.linspace(0, 1, n) ** 2.5)
        y = noise * shape
        if kind == "riser":
            t = np.arange(n) / sr; y += 0.25 * np.sin(2 * np.pi * np.cumsum(200 + 600 * (t / d) ** 2) / sr) * shape
    else:
        sys.exit(f"unknown synth {kind}")
    y = y / (np.abs(y).max() + 1e-9)
    return np.stack([y, y], 1).astype(np.float32)

def loudnorm(src, dst, target, tp):
    a = f"loudnorm=I={target}:TP={tp}:LRA=20"   # LRA=20: a narrower target makes loudnorm leave linear mode and undershoot
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", a + ":print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    a2 = (a + f":measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", a2 + ",aresample=48000,alimiter=limit=0.84:attack=1:release=50:level=false",
                    "-ar", str(SR), dst], check=True)          # limiter at -1.5 dBFS keeps true peak <= -1

def mix(cues_path, out):
    c = json.load(open(cues_path)); base = os.path.dirname(os.path.abspath(cues_path))
    n = int(c["duration"] * SR); bus = np.zeros((n, 2), np.float32); log = []
    m = c.get("music")
    if m:
        x = decode(os.path.join(base, m["file"])) * (10 ** (m.get("gain_db", 0) / 20))
        start = m.get("drop_in_song", 0) - m.get("drop_in_film", 0)       # song time at film t=0
        s = int(round(start * SR))
        seg = x[s:s + n] if s >= 0 else np.concatenate([np.zeros((-s, 2), np.float32), x[:n + s]])
        seg = seg[:n]; bus[:len(seg)] += seg
        fo = int(m.get("fade_out", 0.6) * SR); bus[n - fo:] *= np.linspace(1, 0, fo)[:, None]
        bus[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))[:, None]   # 5 ms fade-in: a full-level first sample clicks
        log.append(f"music: song starts at {start:.3f} s so its drop ({m.get('drop_in_song')}) lands on film {m.get('drop_in_film')} s")
    for e in c.get("sfx", []):
        x = synth(e["synth"], e.get("dur")) if "synth" in e else decode(os.path.join(base, e["file"]))
        x = x * e.get("gain", 0.2); al = e.get("align", "peak")
        off = peak_offset(x) if al == "peak" else (len(x) if al == "end" else 0)
        s = int(round(e["t"] * SR)) - off
        a, b = max(0, s), min(n, s + len(x))
        if b > a: bus[a:b] += x[a - s:b - s]
        log.append(f"sfx {e.get('synth') or os.path.basename(e['file'])} {al}@{e['t']:.3f}s gain {e.get('gain', 0.2)}")
    pk = np.abs(bus).max()
    if pk > 0.89: bus *= 0.89 / pk                          # headroom before loudnorm
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    tmp = os.path.abspath(out) + ".premaster.wav"; write_wav(tmp, bus)
    try: loudnorm(tmp, out, c.get("target_lufs", -14), c.get("true_peak", -1.0))
    finally: os.path.exists(tmp) and os.remove(tmp)
    print("\n".join(log)); print(f"-> {out} (verify: python3 qa.py loudness {out})")

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    mode, f = sys.argv[1], sys.argv[2]; a = dict(zip(sys.argv[3::2], sys.argv[4::2]))
    if mode == "drop": print("drop candidates (time s, strength):", drop(f, float(a.get("--from", 0)), float(a["--to"]) if "--to" in a else None))
    elif mode == "bpm": print("approx BPM:", bpm(f))
    elif mode == "peak": x = decode(f); print(f"peak at {peak_offset(x) / SR:.4f} s of {len(x) / SR:.3f} s")
    elif mode == "mix": mix(f, a.get("--out", "out/mix.wav"))
    elif mode == "synth": write_wav(a.get("--out", f + ".wav"), synth(f, float(a["--dur"]) if "--dur" in a else None)); print("ok")
    else: print(__doc__); sys.exit(1)
