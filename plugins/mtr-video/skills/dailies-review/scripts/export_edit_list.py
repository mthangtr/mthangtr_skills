#!/usr/bin/env python3
"""export_edit_list.py review_log.csv 03_shotlist.json takes_dir out_edit_list.csv
Turn circled takes in the review log into a per-shot edit list (shot_id,file,in_sec,out_sec,note)
for post-assembly/scripts/assemble.py and shotlist_to_otio.py.
Per shot, the in/out = the shot's unit_time_s window intersected with the take's circled in/out range."""
import csv, json, os, sys

def main(log, shotlist, takes_dir, out):
    sl = json.load(open(shotlist, encoding="utf-8"))
    shots = {s["id"]: s for s in sl["shots"]}
    rows = []
    for r in csv.DictReader(open(log, encoding="utf-8")):
        if (r.get("decision") or "").upper() not in ("CIRCLE", "CIRCLE-COND"):
            continue
        t_in = float(r["in_sec"]) if r.get("in_sec") else 0.0
        t_out = float(r["out_sec"]) if r.get("out_sec") else float(r.get("duration_s") or 1e9)
        path = os.path.join(takes_dir, r["unit"], r["file"])
        for sid in [x.strip() for x in r["shot_ids"].split(";") if x.strip()]:
            sh = shots.get(sid)
            if not sh:
                print(f"warn: {sid} not in shotlist", file=sys.stderr); continue
            a, b = sh.get("unit_time_s", [t_in, t_out])
            i, o = max(a, t_in), min(b, t_out)
            if o - i <= 0.04:
                print(f"warn: {sid} has no usable range in {r['file']}", file=sys.stderr); continue
            rows.append({"shot_id": sid, "file": path, "in_sec": f"{i:.3f}", "out_sec": f"{o:.3f}",
                         "note": f"{r.get('review_id','')} {r.get('route','')} {r.get('fix_notes','')}".strip()})
    order = {s["id"]: n for n, s in enumerate(sl["shots"])}
    rows.sort(key=lambda x: order.get(x["shot_id"], 1e9))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["shot_id", "file", "in_sec", "out_sec", "note"])
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} shots -> {out}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
