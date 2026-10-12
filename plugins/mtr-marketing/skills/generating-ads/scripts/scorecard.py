#!/usr/bin/env python3
"""Combine QA gates + predicted attention + persona panel + concept rubric into one benchmark report.

Usage:
    python scripts/scorecard.py --concepts concepts.json --out out/ [--panel panel/panel.json] \
        [--test "--metric ctr --baseline 0.015 --lift 0.2 --cpm 10 --daily 100"] [--report report.md]

concepts.json: [{"id": "c1", "name": "...", "archetype": "...", "angle": "...", "awareness": "...",
                 "hero": "c1-feed", "rubric": {"on_brief": 1-5, "single_minded": .., "branded": .., "divergent": ..,
                 "relevant": .., "emotional": .., "believable": .., "stopping_power": .., "direction": .., "policy_safe": .., "portfolio": ..}}]
Rubric gate items (on_brief, single_minded, branded, believable, policy_safe) <= 2 -> concept killed.

Weights (expert priors, NOT fitted; refit on live results after >=20 ads):
  panel 30 (drops to 10 if order-consistency < 70%), brand attention 15, message attention 15,
  CTA salience 10, focus/clutter 10, clarity 10, concept rubric 10.
Every component is min-max scaled WITHIN this candidate set -> ranking only, never a CTR forecast.
"""
import argparse, json, shlex, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
GATES = ["on_brief", "single_minded", "branded", "believable", "policy_safe"]
BASE_W = {"panel": 30, "brand_attention": 15, "message_attention": 15, "cta_salience": 10, "focus": 10, "clarity": 10, "concept_rubric": 10}


def pct(vals):
    """min-max scale to [0,1] within the set (keeps magnitude, unlike ranks: a tiny raw difference
    stays a tiny score difference). None -> 0.5 (neutral). All-equal -> 0.5."""
    idx = [i for i, v in enumerate(vals) if v is not None]
    out = [0.5] * len(vals)
    if len(idx) <= 1:
        return out
    v = np.array([vals[i] for i in idx], dtype=float)
    span = v.max() - v.min()
    if span < 1e-9:
        return out
    for k, i in enumerate(idx):
        out[i] = float((v[k] - v.min()) / span)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--concepts", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--panel", default=None)
    ap.add_argument("--test", default=None, help="args for test_plan.py, quoted")
    ap.add_argument("--report", default=None)
    ap.add_argument("--research", default=None, help="research.md; concepts must cite its IDs in \"evidence\"")
    ap.add_argument("--notes", default=None, help="markdown file appended to the report (survives re-runs)")
    a = ap.parse_args()
    out = Path(a.out)
    concepts = json.loads(Path(a.concepts).read_text())
    qa = json.loads((out / "qa.json").read_text()) if (out / "qa.json").exists() else []
    att = {r["id"]: r for r in json.loads((out / "attention.json").read_text())} if (out / "attention.json").exists() else {}
    panel = json.loads(Path(a.panel).read_text()) if a.panel and Path(a.panel).exists() else None
    missing = [n for n, ok in [("qa.json (run qa_check.py)", qa), ("attention.json (run attention.py)", att), ("panel.json (run panel.py)", panel)] if not ok]

    research = None
    if a.research and Path(a.research).exists():
        from research_check import check as rcheck
        research = rcheck(a.research, fast=None, concepts=a.concepts)
    rows = []
    for c in concepts:
        cid = c["id"]
        q = [r for r in qa if r.get("concept") == cid]
        hero = c.get("hero") or (q[0]["id"] if q else None)
        at = att.get(hero, {})
        rub = c.get("rubric", {})
        gate_fail = [f"rubric:{g}={rub[g]}" for g in GATES if g in rub and rub[g] <= 2]
        if research and research["status"] != "ASSUMED" and cid in research["concept_issues"]:
            gate_fail.append("ungrounded: " + research["concept_issues"][cid])
        qa_fail = [f"{r['id']}: {f}" for r in q for f in r["fails"]]
        qa_warn = [f"{r['id']}: {w}" for r in q for w in r["warnings"]]
        hq = next((r for r in q if r["id"] == hero), q[0] if q else {"metrics": {}})
        m = hq.get("metrics", {})
        sh = at.get("aoi_share", {})
        brand = (sh.get("brand", 0) + (0.10 if "brand" in at.get("in_first3", []) else 0)) if at else None
        message = (sh.get("headline", 0) + sh.get("product", 0) + sh.get("offer", 0)) if at else None
        cta = None
        if at and "cta" in sh:
            cta = sh["cta"] * (1.0 if (m.get("cta_vs_bg_contrast") or 3) >= 3 else 0.5)
        focus = None
        if at:
            focus = at.get("focus", 0) - 0.03 * max(0, at.get("peaks", 1) - 3)
        clutter = at.get("edge_density") if at else None
        ocr = m.get("ocr_headline_recovery")
        clarity = (0.5 if ocr is None else ocr) - (m.get("text_area_ratio") or 0) - 0.05 * len([w for w in hq.get("warnings", []) if "words" in w])
        pnl = panel["items"].get(cid) if panel else None
        rows.append(dict(id=cid, name=c.get("name", cid), archetype=c.get("archetype"), angle=c.get("angle"), hero=hero,
                         killed=bool(gate_fail or qa_fail), gate_fail=gate_fail, qa_fail=qa_fail, qa_warn=qa_warn,
                         raw=dict(panel=pnl["bt_strength"] if pnl else None, brand_attention=brand, message_attention=message,
                                  cta_salience=cta, focus=focus, clutter=clutter, clarity=clarity,
                                  concept_rubric=float(np.mean(list(rub.values()))) if rub else None),
                         att=at, pnl=pnl, metrics=m))

    w = dict(BASE_W)
    disc = panel.get("discriminating", False) if panel else False
    if not panel:
        w["panel"] = 0
    elif not disc:
        w["panel"] = 10
    models = {r["att"].get("model") for r in rows if r["att"]}
    low_att = bool(models) and models <= {"classic"}
    if low_att:  # classic saliency is biased toward text edges / against type-led layouts -> shrink its say
        w.update(brand_attention=8, message_attention=8, cta_salience=5, focus=5)
    tot_w = sum(w.values())
    comps = ["panel", "brand_attention", "message_attention", "cta_salience", "focus", "clarity", "concept_rubric"]
    P = {k: pct([r["raw"][k] for r in rows]) for k in comps}
    clut = pct([(-r["raw"]["clutter"] if r["raw"]["clutter"] is not None else None) for r in rows])
    P["focus"] = [0.7 * f + 0.3 * c for f, c in zip(P["focus"], clut)]
    for i, r in enumerate(rows):
        r["pct"] = {k: round(P[k][i], 2) for k in comps}
        r["score"] = round(100 * sum(w[k] * P[k][i] for k in comps) / tot_w, 1)
    alive = sorted([r for r in rows if not r["killed"]], key=lambda r: -r["score"])
    dead = [r for r in rows if r["killed"]]

    L = ["# Pre-launch ad benchmark report", ""]
    if missing:
        L += [f"> **Incomplete benchmark** — missing: {', '.join(missing)}. Scores below exclude those components.", ""]
    L += ["Scores are min-max scaled **within this candidate set** (0-100); with <5 candidates small edits can swap ranks. They rank candidates for this brief; they are **not** CTR/CVR predictions.",
          f"Weights: {', '.join(f'{k} {v}' for k, v in w.items())}" + ("" if disc or not panel else "  (panel down-weighted: order consistency < 70%)") + ("  (attention down-weighted: classic saliency only)" if low_att else ""), "",
          "| Rank | Concept | Archetype / angle | Score | Panel P(top) | Brand attn | Message attn | CTA attn | Focus | Gates |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    fmt = lambda v: "–" if v is None else f"{v:.0%}"
    for i, r in enumerate(alive + dead):
        sh = r["att"].get("aoi_share", {})
        L.append(f"| {i + 1 if not r['killed'] else 'X'} | {r['name']} | {r['archetype']} / {r['angle']} | {r['score'] if not r['killed'] else 'killed'} | "
                 f"{fmt(r['pnl']['p_rank1']) if r['pnl'] else '–'} | {fmt(sh.get('brand'))} | {fmt((sh.get('headline', 0) + sh.get('product', 0) + sh.get('offer', 0)) if sh else None)} | "
                 f"{fmt(sh.get('cta'))} | {r['att'].get('focus', '–')} | {'PASS' if not r['killed'] else 'FAIL'} |")
    L.append("")
    if not alive:
        L += ["## Recommendation", "- **No concept passed the gates.** Nothing is deliverable yet: fix the gate failures below and re-run.", ""]
    if alive:
        top = alive[0]
        pool = [r for r in alive[1:] if r["archetype"] != top["archetype"] or r["angle"] != top["angle"]] or alive[1:]
        if low_att and disc and all(r["pnl"] for r in pool):
            pool = sorted(pool, key=lambda r: -r["pnl"]["bt_strength"])  # attention is low-confidence: let the panel pick the challenger
        ch = pool[0] if pool else None
        gap = top["score"] - ch["score"] if ch else None
        sep = True
        if top["pnl"] and ch is not None and ch["pnl"]:
            sep = top["pnl"]["ci90"][0] > ch["pnl"]["bt_strength"]  # lead's lower bound above challenger's estimate
        confident = ch is not None and gap is not None and gap >= 10 and (not top["pnl"] or (top["pnl"]["p_rank1"] >= 0.75 and sep))
        L += ["## Recommendation", f"- **Lead:** {top['name']} (score {top['score']})."]
        if ch:
            L.append(f"- **Challenger (different concept, launch alongside):** {ch['name']} (score {ch['score']}, gap {gap:.1f}).")
        if ch is None:
            L.append("- **Only one concept passed the gates.** Fix or replace the killed concepts before delivering: a live test needs ≥2 distinct concepts.")
        else:
            L.append("- Confidence: " + ("lead is clearly ahead on pre-launch signals (still verify live)." if confident else
                                         "**no confident winner** — scores are close or the panel is uncertain (P(top) < 75% or overlapping CI); let the live A/B test decide."))
        L.append("")
    L.append("## Diagnostics and fixes")
    for r in alive + dead:
        notes = []
        sh, at = r["att"].get("aoi_share", {}), r["att"]
        if r["killed"]:
            notes += [f"GATE FAIL {x}" for x in r["gate_fail"] + r["qa_fail"]]
        if sh:
            if sh.get("brand", 0) < 0.05:
                notes.append(f"brand gets {sh.get('brand', 0):.0%} of predicted attention (<5%): enlarge/move logo next to the focal point or use a stronger brand asset")
            if "brand" not in at.get("in_first3", []):
                notes.append("brand not in first 3 predicted fixations")
            dn = at.get("aoi_density", {})
            if "cta" in dn and dn["cta"] < 1.0:
                notes.append(f"CTA pulls less attention than its size (density {dn['cta']:.1f}, share {sh.get('cta', 0):.0%}): isolate it with the accent colour, more space around it")
            if at.get("first_fix", ["?"])[0] == "background":
                notes.append("first predicted fixation lands on background/decoration, not on a message element")
            if at.get("peaks", 0) > 4:
                notes.append(f"{at['peaks']} competing hotspots: remove or quiet secondary elements")
        if r["pnl"]:
            comp = (panel.get("comprehension", {}) if panel else {}).get(r["id"], [])
            conf = [x["confusing"] for x in comp if x.get("confusing") and x["confusing"].lower() not in ("nothing", "none", "")]
            if conf:
                notes.append("panel confusion: " + " | ".join(conf[:3]))
            nobrand = [x for x in comp if (x.get("brand_seen") or "none").lower() == "none"]
            if comp and len(nobrand) / len(comp) > 0.3:
                notes.append(f"{len(nobrand)}/{len(comp)} personas did not register the brand")
        notes += [f"warn {x}" for x in r["qa_warn"][:6]]
        L.append(f"- **{r['name']}**: " + ("; ".join(notes) if notes else "no issues flagged"))
    unverified = [(c.get("name", c["id"]), cl["text"]) for c in concepts for cl in c.get("claims", [])
                  if str(cl.get("source", "UNVERIFIED")).upper() == "UNVERIFIED"]
    no_ledger = [c.get("name", c["id"]) for c in concepts if "claims" not in c]
    req = [(c.get("name", c["id"]), x) for c in concepts for x in c.get("required", [])]
    ph = sorted({(r.get("concept"), p) for r in qa for p in r.get("metrics", {}).get("placeholders", [])})
    stale = []
    if panel:
        import os
        for r in rows:
            im = panel.get("images", {}).get(r["id"])
            if im and im.get("mtime") and os.path.exists(im["image"]) and os.path.getmtime(im["image"]) > im["mtime"] + 1:
                stale.append(r["name"])
    L += ["", "## Required before launch"]
    if not research:
        L.append("- **No research.md supplied**: insights and concepts are ungrounded assumptions (run Phase 0).")
    elif research["status"] == "ASSUMED":
        L.append("- **Research status ASSUMED**: no customer or competitor evidence was available; validate insights before scaling spend.")
    elif not research["pass"]:
        L.append(f"- Research below threshold ({research['counts']}): " + "; ".join(research["fails"][:4]))
    if unverified:
        L += [f"- UNVERIFIED claim in **{n}**: \"{t}\" — supply a source or remove it." for n, t in unverified]
    if no_ledger:
        L.append(f"- No claims ledger for: {', '.join(no_ledger)} — list every number/rating/review/price shown (strategy.md §5).")
    L += [f"- Required for **{n}**: {x}" for n, x in req]
    L += [f"- Placeholder still visible in {c}: \"{p}\"" for c, p in ph]
    if not unverified and not no_ledger and not req and not ph:
        L.append("- All claims shown in the ads have a source; no placeholders or open requirements recorded.")
    if stale:
        L += ["", f"> **Stale panel:** {', '.join(stale)} changed after the panel judged it. Re-run `panel.py make/aggregate` (or state that the panel saw an earlier version)."]
    L += ["", "## Evidence used and its limits",
          f"- Attention model: {', '.join(sorted({r['att'].get('model', 'none') for r in rows}))}. Saliency predicts free-viewing gaze in the first seconds on a static screen; not feed scrolling, not persuasion. Classic maps over-weight text edges: low confidence.",
          f"- Persona panel: {'order consistency ' + format(panel['order_consistency'], '.0%') if panel else 'not run'}. LLM panels are homogeneous and order-biased; uncalibrated, they are near chance at picking real A/B winners. Use as qualitative critique + tie-breaker.",
          "- Concept rubric is scored by the creating agent (self-preference risk); it carries 10% weight.",
          "- Weights are expert priors. Only live data decides; see test plan."]
    if a.test:
        from test_plan import plan
        ta = argparse.ArgumentParser()
        for k in ("--metric", "--baseline", "--lift", "--arms", "--cpm", "--cpc", "--daily", "--budget"):
            ta.add_argument(k, type=str if k == "--metric" else float, default=None)
        t = ta.parse_args(shlex.split(a.test))
        L += ["", plan(t.metric or "ctr", t.baseline, t.lift, int(t.arms or max(2, min(len(alive), 3))), t.cpm, t.cpc, t.daily, t.budget)]
    if a.notes and Path(a.notes).exists():
        L += ["", "## Notes", Path(a.notes).read_text()]
    report = Path(a.report or out / "report.md")
    report.write_text("\n".join(L) + "\n")
    (out / "scorecard.json").write_text(json.dumps([{k: v for k, v in r.items() if k not in ("att", "pnl")} for r in rows], indent=1, default=str))
    print("\n".join(L))


if __name__ == "__main__":
    main()
