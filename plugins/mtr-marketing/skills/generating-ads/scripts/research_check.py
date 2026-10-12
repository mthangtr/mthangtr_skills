#!/usr/bin/env python3
"""Lint research.md (from templates/research.md) before ideation, and expose its evidence IDs.

Usage:
    python scripts/research_check.py research.md            # full thresholds
    python scripts/research_check.py research.md --fast     # deadline thresholds
    python scripts/research_check.py research.md --concepts concepts.json   # also check concept grounding

Thresholds (full / fast):
  VOC verbatims V##        >= 20 / 10   (each with a source; quotes in quote marks)
  Competitor ads A##       >= 10 / 5    (each with a source; days running filled for >= half)
  Insight candidates I##   >= 3  / 2    (each citing >= 2 existing V/A/M IDs)
  Synthesis sections present and non-empty: Pains, Objections, Cliché zone, Gaps, Market sophistication
Status ASSUMED is allowed only with an explanation of what was tried; it never passes as GROUNDED.
Exit 1 on failure.
"""
import argparse, json, re, sys
from pathlib import Path

ROW = re.compile(r"^\|\s*([VAMI]\d{2,3})\s*\|(.*)\|\s*$")
SRC = re.compile(r"(https?://\S+|\buser\b|\bbrief\b|\bscreenshot\b|\bclient\b)", re.I)
FULL = dict(V=20, A=10, I=3)
FAST = dict(V=10, A=5, I=2)
SECTIONS = ["Pains", "Objections", "Cliché zone", "Gaps", "Market sophistication"]


def parse(path):
    text = Path(path).read_text()
    rows = {}
    for line in text.splitlines():
        m = ROW.match(line.strip())
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            if any(cells):
                rows[m.group(1)] = cells
    status = re.search(r"^Status:\s*(\w+)", text, re.M)
    status = status.group(1).upper() if status and "|" not in status.group(0) else "UNSET"
    sections = {}
    for name in SECTIONS:
        m = re.search(r"^#+\s*" + re.escape(name) + r".*?$(.*?)(?=^#+\s|\Z)", text, re.M | re.S | re.I)
        body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S) if m else ""
        lines = [l.strip() for l in body.splitlines() if l.strip() and l.strip() not in ("- …", "…")]
        lines = [l for l in lines if not re.fullmatch(r"-?\s*…?\s*(\([^)]*…?[^)]*\))?", l) and "Stage <1-5>" not in l]
        sections[name] = bool(lines)
    return text, rows, status, sections


def check(path, fast=None, concepts=None, brief=None):
    text, rows, status, sections = parse(path)
    if fast is None:  # read "Mode: fast" from the header
        fast = bool(re.search(r"Mode:\s*fast\b", text.split("## ")[0], re.I))
    th = FAST if fast else FULL
    fails, warns = [], []
    ids = set(rows)
    V = {k: v for k, v in rows.items() if k[0] == "V" and v[0] not in ("", '"…"')}
    A = {k: v for k, v in rows.items() if k[0] == "A" and any(c not in ("", "…", '"…"') for c in v[:4])}
    I = {k: v for k, v in rows.items() if k[0] == "I"}
    src = lambda k, v: (v[2] if len(v) > 2 else "") if k[0] == "V" else v[-1]
    nosrc = [k for k, v in {**V, **A}.items() if not SRC.search(src(k, v))]
    if status == "UNSET":
        fails.append("set the Status line to exactly one of GROUNDED / PARTIAL / ASSUMED")
    if status == "ASSUMED":
        if not re.search(r"Blocked/unavailable:\s*\S", text):
            fails.append("Status ASSUMED without listing what was tried/blocked")
        warns.append("research ASSUMED: every concept is ungrounded; report must say so")
    else:
        if len(V) < th["V"]:
            fails.append(f"VOC verbatims {len(V)} < {th['V']}")
        if len(A) < th["A"]:
            fails.append(f"competitor ads {len(A)} < {th['A']}")
        if nosrc:
            fails.append(f"rows without a source: {', '.join(sorted(nosrc)[:10])}")
        days = [v for v in A.values() if len(v) >= 6 and re.search(r"\d", v[5])]
        if A and len(days) < len(A) / 2:
            warns.append("days-running missing for most competitor ads (long-runners are the performance proxy)")
        for name, ok in sections.items():
            if not ok:
                fails.append(f"synthesis section empty: {name}")
    if len(I) < th["I"]:
        fails.append(f"insight candidates {len(I)} < {th['I']}")
    for k, v in I.items():
        cited = set(re.findall(r"\b[VAM]\d{2,3}\b", " ".join(v)))
        bad = cited - ids
        if len(cited & ids) < 2 and status != "ASSUMED":
            fails.append(f"{k} cites {len(cited & ids)} existing evidence IDs (< 2)")
        if bad:
            fails.append(f"{k} cites missing IDs: {', '.join(sorted(bad))}")
    if brief and Path(brief).exists():
        bi = set(re.findall(r"\bI\d{2,3}\b", Path(brief).read_text()))
        if not (bi & set(I)):
            fails.append("brief.md does not cite any existing insight ID (I##)")
    concept_issues = {}
    if concepts:
        for c in json.loads(Path(concepts).read_text()):
            ev = set(c.get("evidence", []))
            ok = ev & ids
            if not ok:
                concept_issues[c["id"]] = "cites no existing research ID (add \"evidence\": [\"I01\", ...])"
            elif ev - ids:
                concept_issues[c["id"]] = f"cites missing IDs {sorted(ev - ids)}"
    return {"status": status, "mode": "fast" if fast else "full", "counts": {"V": len(V), "A": len(A), "M": sum(1 for k in rows if k[0] == 'M'), "I": len(I)},
            "pass": not fails, "fails": fails, "warnings": warns, "ids": sorted(ids), "concept_issues": concept_issues}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("research")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--concepts", default=None)
    ap.add_argument("--brief", default=None)
    a = ap.parse_args()
    r = check(a.research, True if a.fast else None, a.concepts, a.brief)
    print(f"{'PASS' if r['pass'] else 'FAIL'}  research status={r['status']} counts={r['counts']}")
    for f in r["fails"]:
        print("   FAIL:", f)
    for w in r["warnings"]:
        print("   warn:", w)
    for cid, msg in r["concept_issues"].items():
        print(f"   concept {cid}: {msg}")
    sys.exit(0 if r["pass"] and not r["concept_issues"] else 1)


if __name__ == "__main__":
    main()
