#!/usr/bin/env python3
"""Blind pairwise synthetic-persona panel: job builder + Bradley-Terry aggregator.

The judging itself is done by FRESH-CONTEXT subagents (or another VLM API) that look at the images.
This script only makes the jobs fair (both orders, anonymised, shuffled) and aggregates honestly.

1) Build jobs:
    python scripts/panel.py make --items items.json --personas personas.json --out panel/
   items.json    : [{"id": "c1", "image": "out/c1-feed.png"}, ...]   (one hero placement per concept)
   personas.json : [{"name": "skeptical-freelancer", "profile": "34, designer, ... scrolling IG on phone, objection: ..."}, ...]
   -> panel/batch_XX.md   one prompt per judge subagent (persona x subset of ordered pairs + comprehension asks)
   -> panel/jobs.json     key mapping (keep away from judges)

2) Dispatch one fresh subagent per batch file. Tell it: "Read panel/batch_XX.md and follow it exactly.
   Write only the JSON lines it asks for to panel/verdicts_XX.jsonl". Do NOT tell judges which ad you prefer,
   which concept is which, or how they were made. Prefer a different model family than the generator.

3) Aggregate:
    python scripts/panel.py aggregate --out panel/
   -> panel/panel.json : Bradley-Terry strength, 90% bootstrap CI, P(rank 1), order-consistency rate,
                         per-persona winners, comprehension answers, top reasons.
"""
import argparse, itertools, json, random, re
from pathlib import Path
import numpy as np

JUDGE_HEADER = """# Ad reaction task (persona panel)

You are role-playing this person. Stay in character; react like a real person, not a marketer.

**Persona:** {name}
{profile}

Context: you are scrolling on your phone. Each ad gets about 1–2 seconds of your attention unless something makes you stop.
Open each image with the Read tool before answering. Judge only what you see. Do not guess how the ads were made.

For every job below, write ONE JSON object per line (JSON Lines) to `{verdict_file}` and nothing else.
"""

PAIR_JOB = """
## Job {job}: pairwise
First image: `{first}`
Second image: `{second}`
1. In 1–3 sentences, describe your honest gut reaction to each ad as this persona (what you noticed first, what you understood, what you felt).
2. Then decide: which one would make you more likely to stop scrolling AND tap to find out more? If you genuinely would not prefer either, answer "tie".
JSON: {{"job": "{job}", "reaction_first": "...", "reaction_second": "...", "winner": "first"|"second"|"tie", "reason": "<one sentence, concrete: quote the words or describe the element that decided it>"}}
"""

COMP_JOB = """
## Job {job}: comprehension
Image: `{image}`
Look at it for a moment as this persona. Without overthinking:
JSON: {{"job": "{job}", "brand_seen": "<brand name you saw, or 'none'>", "offer_understood": "<one sentence: what is being offered and why you'd want it>", "first_noticed": "<the very first thing your eye went to>", "confusing": "<anything unclear, or 'nothing'>"}}
"""


def make(items_path, personas_path, out, pairs_per_batch=6, seed=7):
    rng = random.Random(seed)
    items = json.loads(Path(items_path).read_text())
    personas = json.loads(Path(personas_path).read_text())
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    pairs = list(itertools.combinations(range(len(items)), 2))
    if len(items) > 8:  # sample ~3 N log N pairs
        k = min(len(pairs), int(3 * len(items) * np.log(len(items))))
        pairs = rng.sample(pairs, k)
    jobs, batches = {}, []
    jid = 0
    for p_i, persona in enumerate(personas):
        ordered = []
        for a, b in pairs:
            ordered += [(a, b), (b, a)]
        rng.shuffle(ordered)
        comp = list(range(len(items)))
        rng.shuffle(comp)
        chunks = [ordered[i:i + pairs_per_batch] for i in range(0, len(ordered), pairs_per_batch)] or [[]]
        for c_i, chunk in enumerate(chunks):
            bname = f"batch_{len(batches):02d}"
            vfile = str(out / f"verdicts_{len(batches):02d}.jsonl")
            body = JUDGE_HEADER.format(name=persona["name"], profile=persona.get("profile", ""), verdict_file=vfile)
            if c_i == 0:  # comprehension first, before seeing comparisons
                for it in comp:
                    j = f"j{jid:04d}"; jid += 1
                    jobs[j] = {"type": "comp", "persona": persona["name"], "item": items[it]["id"]}
                    body += COMP_JOB.format(job=j, image=items[it]["image"])
            for a, b in chunk:
                j = f"j{jid:04d}"; jid += 1
                jobs[j] = {"type": "pair", "persona": persona["name"], "first": items[a]["id"], "second": items[b]["id"]}
                body += PAIR_JOB.format(job=j, first=items[a]["image"], second=items[b]["image"])
            (out / f"{bname}.md").write_text(body)
            batches.append(bname)
    import os
    mt = {i["id"]: {"image": i["image"], "mtime": os.path.getmtime(i["image"]) if os.path.exists(i["image"]) else None} for i in items}
    (out / "jobs.json").write_text(json.dumps({"items": [i["id"] for i in items], "images": mt, "jobs": jobs}, indent=1))
    print(f"{len(batches)} judge batches written to {out}/ (one fresh subagent per batch). "
          f"{sum(1 for j in jobs.values() if j['type']=='pair')} ordered pair judgments, "
          f"{sum(1 for j in jobs.values() if j['type']=='comp')} comprehension checks.")


def bradley_terry(n, comps, iters=500, prior=0.1):
    """comps: list of (winner, loser, weight). MM algorithm (Hunter 2004) with symmetric pseudo-counts."""
    W = np.full((n, n), prior); np.fill_diagonal(W, 0)
    for w, l, wt in comps:
        W[w, l] += wt
    p = np.ones(n)
    for _ in range(iters):
        wins = W.sum(1)
        denom = np.array([sum((W[i, j] + W[j, i]) / (p[i] + p[j]) for j in range(n) if j != i) for i in range(n)])
        p_new = wins / denom
        p_new /= np.exp(np.mean(np.log(p_new)))
        if np.allclose(p, p_new, rtol=1e-8):
            break
        p = p_new
    return np.log(p)


def _parse_lines(path):
    out = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", line)
            if m:
                try:
                    out.append(json.loads(m.group(0)))
                except json.JSONDecodeError:
                    pass
    return out


def aggregate(out, n_boot=1000, seed=11):
    out = Path(out)
    meta = json.loads((out / "jobs.json").read_text())
    ids, jobs = meta["items"], meta["jobs"]
    idx = {k: i for i, k in enumerate(ids)}
    verdicts = {}
    for f in sorted(out.glob("verdicts_*.jsonl")):
        for v in _parse_lines(f):
            if v.get("job") in jobs:
                verdicts[v["job"]] = v
    missing = [j for j in jobs if j not in verdicts]

    # pair up both orders per persona
    units = {}  # (persona, frozenset) -> list of winning item ids or 'tie'
    reasons = {k: [] for k in ids}
    for j, v in verdicts.items():
        meta_j = jobs[j]
        if meta_j["type"] != "pair":
            continue
        w = v.get("winner", "tie")
        win = meta_j["first"] if w == "first" else meta_j["second"] if w == "second" else "tie"
        units.setdefault((meta_j["persona"], frozenset([meta_j["first"], meta_j["second"]])), []).append(win)
        if win != "tie" and v.get("reason"):
            reasons[win].append(v["reason"])
    comps_units, consistent, complete = [], 0, 0
    for (persona, pair), wins in units.items():
        a, b = sorted(pair)
        if len(wins) >= 2:
            complete += 1
            if wins[0] == wins[1] and wins[0] != "tie":
                consistent += 1
                comps_units.append([(idx[wins[0]], idx[b if wins[0] == a else a], 1.0)])
            else:  # order-dependent or tie -> tie
                comps_units.append([(idx[a], idx[b], 0.5), (idx[b], idx[a], 0.5)])
        else:
            comps_units.append([(idx[a], idx[b], 0.25), (idx[b], idx[a], 0.25)])  # half-observed -> weak tie
    consistency = consistent / complete if complete else 0.0
    n = len(ids)
    flat = [c for u in comps_units for c in u]
    strength = bradley_terry(n, flat) if flat else np.zeros(n)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot if comps_units else 0):
        sample = [c for k in rng.integers(0, len(comps_units), len(comps_units)) for c in comps_units[k]]
        boots.append(bradley_terry(n, sample, iters=200))
    boots = np.array(boots) if boots else np.zeros((1, n))
    p_top = (boots.argmax(1)[:, None] == np.arange(n)).mean(0)
    lo, hi = np.percentile(boots, 5, axis=0), np.percentile(boots, 95, axis=0)

    win_rate = {}
    for i, k in enumerate(ids):
        tot = sum(wt for u in comps_units for (w, l, wt) in u if w == i or l == i)
        won = sum(wt for u in comps_units for (w, l, wt) in u if w == i)
        win_rate[k] = round(won / tot, 3) if tot else None

    per_persona = {}
    for (persona, pair), wins in units.items():
        for w in wins:
            if w != "tie":
                per_persona.setdefault(persona, {}).setdefault(w, 0)
                per_persona[persona][w] += 1
    comp = {}
    for j, v in verdicts.items():
        if jobs[j]["type"] == "comp":
            comp.setdefault(jobs[j]["item"], []).append({"persona": jobs[j]["persona"], **{k: v.get(k) for k in ("brand_seen", "offer_understood", "first_noticed", "confusing")}})

    ranking = sorted(ids, key=lambda k: -strength[idx[k]])
    result = {
        "ranking": ranking,
        "items": {k: {"bt_strength": round(float(strength[idx[k]]), 3), "ci90": [round(float(lo[idx[k]]), 3), round(float(hi[idx[k]]), 3)],
                      "p_rank1": round(float(p_top[idx[k]]), 3), "win_rate": win_rate[k], "reasons": reasons[k][:8]} for k in ids},
        "order_consistency": round(consistency, 3),
        "discriminating": consistency >= 0.7,
        "per_persona_wins": per_persona,
        "comprehension": comp,
        "missing_jobs": missing,
        "images": meta.get("images", {}),
        "note": "Synthetic panel = qualitative signal for ranking within this brief only. Uncalibrated LLM panels are near chance at predicting real A/B winners; never quote as predicted CTR.",
    }
    (out / "panel.json").write_text(json.dumps(result, indent=1))
    print(f"order consistency {consistency:.0%} ({'OK' if consistency >= 0.7 else 'LOW: panel not discriminating -> report no confident difference'}); missing jobs: {len(missing)}")
    for k in ranking:
        it = result["items"][k]
        print(f"  {k}: BT {it['bt_strength']:+.2f}  CI90 [{it['ci90'][0]:+.2f},{it['ci90'][1]:+.2f}]  P(top)={it['p_rank1']:.0%}  win={it['win_rate']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("--items", required=True); m.add_argument("--personas", required=True)
    m.add_argument("--out", default="panel"); m.add_argument("--pairs-per-batch", type=int, default=6)
    g = sub.add_parser("aggregate"); g.add_argument("--out", default="panel")
    a = ap.parse_args()
    if a.cmd == "make":
        make(a.items, a.personas, a.out, a.pairs_per_batch)
    else:
        aggregate(a.out)


if __name__ == "__main__":
    main()
