#!/usr/bin/env python3
"""validate_shotlist.py shotlist.json [--genre drama] [--models-dir DIR]
Validate 03_shotlist.json against the schema, the gate metrics in references/knowledge.md (sections 7, 8, 10)
and the limits of each unit's video model profile (film.video_model or units[].video_model,
read from video-generation/references/models/<id>/profile.json).
Exit code 0 = pass, 1 = errors. Warnings do not fail the gate but must be reviewed."""
import json, sys, os, statistics, argparse
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "..", "references", "shotlist.schema.json")
MODELS = os.path.join(HERE, "..", "..", "video-generation", "references", "models")

def load_profile(models_dir, mid, cache):
    if mid not in cache:
        path = os.path.join(models_dir, mid, "profile.json")
        cache[mid] = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None
    return cache[mid]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--genre", default=None); ap.add_argument("--models-dir", default=MODELS)
    a = ap.parse_args()
    data = json.load(open(a.path, encoding="utf-8"))
    errors, warns = [], []
    try:
        import jsonschema
        v = jsonschema.Draft202012Validator(json.load(open(SCHEMA, encoding="utf-8")))
        for e in sorted(v.iter_errors(data), key=lambda e: list(e.path)):
            errors.append(f"schema: {'/'.join(map(str, e.path))}: {e.message}")
    except ImportError:
        errors.append("jsonschema not installed (pip install jsonschema): schema check is mandatory for the gate")

    shots = {s["id"]: s for s in data.get("shots", [])}
    unit_of = {}
    for u in data.get("units", []):
        for i in u.get("shot_ids", []):
            if i in unit_of: errors.append(f"{i}: in two units ({unit_of[i]}, {u['id']})")
            unit_of[i] = u["id"]
    for i in shots:
        if i not in unit_of: errors.append(f"{i}: not assigned to any unit")
    film = data.get("film", {}); profiles = {}
    default_model = film.get("video_model")
    genre = a.genre or data.get("film", {}).get("genre")
    # Units
    for u in data.get("units", []):
        ids = u.get("shot_ids", [])
        missing = [i for i in ids if i not in shots]
        if missing: errors.append(f"{u['id']}: unknown shot ids {missing}")
        mid = u.get("video_model") or default_model
        prof = load_profile(a.models_dir, mid, profiles) if mid else None
        if not prof:
            errors.append(f"{u['id']}: no model profile '{mid}' (set film.video_model; add a profile per video-generation/references/adding-a-model.md)")
            prof = {"output": {"duration_s": {"min": 0, "max": 1e9}, "ratios": [], "fps": []}, "shots": {"min_shot_s": 0, "max_shots_per_call": 99, "multi_shot_in_call": True}, "audio": {}}
        o, sp = prof["output"], prof["shots"]
        dmin, dmax = o["duration_s"]["min"], o["duration_s"]["max"]
        total = sum(shots[i].get("duration_s", 0) + shots[i].get("handle_s", 0) for i in ids if i in shots)
        if total > dmax: errors.append(f"{u['id']}: {total:.1f}s incl. handles > {dmax}s ({mid} max per call)")
        if total < dmin: errors.append(f"{u['id']}: {total:.1f}s < {dmin}s ({mid} minimum)")
        allowed = o["duration_s"].get("allowed")
        if allowed and not any(abs(total - x) <= 0.1 for x in allowed): errors.append(f"{u['id']}: {total:.1f}s not in {mid} allowed durations {allowed}")
        if not sp.get("multi_shot_in_call") and len(ids) > 1: errors.append(f"{u['id']}: {mid} cannot cut inside one call; use one shot per unit")
        if len(ids) > sp.get("max_shots_per_call", 99): errors.append(f"{u['id']}: {len(ids)} shots > {sp['max_shots_per_call']} ({mid})")
        ratio = u.get("gen_ratio_override") or film.get("gen_ratio")
        if o.get("ratios") and ratio not in o["ratios"]: errors.append(f"{u['id']}: gen_ratio {ratio} not supported by {mid} {o['ratios']}")
        if o.get("fps") and film.get("fps") not in o["fps"]: warns.append(f"{u['id']}: {mid} outputs {o['fps']} fps, project is {film.get('fps')} fps: conform in post")
        has_dialogue = any((shots[i].get("action") or {}).get("dialogue") for i in ids if i in shots)
        if has_dialogue and not prof.get("audio", {}).get("dialogue_lip_sync"): warns.append(f"{u['id']}: dialogue but {mid} has no lip-sync: plan ADR / lip-sync in post")
        for i in ids:
            if i in shots and shots[i].get("duration_s", 0) < sp.get("min_shot_s", 0):
                errors.append(f"{i}: duration_s {shots[i]['duration_s']} < {sp['min_shot_s']}s ({mid} min shot; trim in post via edit.target_cut_s)")
        if abs(total - u.get("duration_s", total)) > 0.1:
            errors.append(f"{u['id']}: duration_s {u.get('duration_s')} != sum of shots+handles {total:.2f}")
        t = 0.0
        for i in ids:
            if i not in shots: continue
            sh = shots[i]; span = sh.get("unit_time_s")
            if sh.get("unit") != u["id"]: errors.append(f"{i}: unit field {sh.get('unit')} != {u['id']}")
            if span:
                if abs(span[0] - t) > 0.05: errors.append(f"{i}: unit_time_s starts {span[0]} (expected {t:.2f}, gap/overlap)")
                if abs((span[1] - span[0]) - (sh.get("duration_s", 0) + sh.get("handle_s", 0))) > 0.05:
                    errors.append(f"{i}: unit_time_s span != duration_s + handle_s")
                t = span[1]
            else:
                t += sh.get("duration_s", 0) + sh.get("handle_s", 0)
        if len(ids) < 1: errors.append(f"{u['id']}: empty unit")
        scenes = {shots[i]["scene"] for i in ids if i in shots}
        if len(scenes) > 1: errors.append(f"{u['id']}: spans scenes {sorted(scenes)}")
        speakers = {shots[i].get("action", {}).get("speaker") for i in ids if i in shots} - {None, ""}
        if len(speakers) > 2: errors.append(f"{u['id']}: {len(speakers)} speakers > 2")
    # Shots
    for s in shots.values():
        cam = s.get("camera", {}); mv = cam.get("move")
        if mv and mv != "static":
            mot = cam.get("motivation", {})
            reason = (mot.get("reason") or "").lower()
            # "đẹp" = Vietnamese for "pretty": kept as data so non-English shot lists are checked too
            if mot.get("type") in (None, "none_static") or any(w in reason for w in ("cinematic", "dynamic", "pretty", "beautiful", "đẹp", "epic")):
                errors.append(f"{s['id']}: move '{mv}' without real motivation")
        if s.get("action", {}).get("complexity") == "high" and mv not in ("static", None):
            errors.append(f"{s['id']}: high-complexity action with moving camera")
        p = s.get("performance")
        if p:
            if len(p.get("observable_behavior", [])) < 2: errors.append(f"{s['id']}: < 2 observable cues")
            if s.get("size") in ("ews", "ws") and any("micro" in c.lower() for c in p.get("observable_behavior", [])):
                warns.append(f"{s['id']}: micro-expression cue in a wide shot")
    # Intensity >=4 at most once per scene
    per_scene = Counter(s["scene"] for s in shots.values() if (s.get("performance") or {}).get("intensity", 0) >= 4)
    for sc, n in per_scene.items():
        if n > 1: warns.append(f"{sc}: intensity>=4 used {n} times (max 1, at turning point)")
    # Distribution metrics (section 8)
    n = len(shots) or 1
    moves = Counter(s.get("camera", {}).get("move") for s in shots.values())
    static = moves.get("static", 0) / n; push = moves.get("push_in", 0) / n
    center = sum(1 for s in shots.values() if s.get("composition", {}).get("subject_position") == "center") / n
    durs = [(s.get("edit") or {}).get("target_cut_s") or s.get("duration_s", 0) for s in shots.values()]
    cv = statistics.pstdev(durs) / statistics.mean(durs) if len(durs) > 1 and statistics.mean(durs) else 0
    if genre == "drama" and static < 0.40: warns.append(f"static {static:.0%} < 40% for drama")
    if push > 0.25: warns.append(f"push_in {push:.0%} > 25%")
    if center > 0.40: warns.append(f"centered framing {center:.0%} > 40%")
    if len(durs) > 3 and cv < 0.35: warns.append(f"shot-length CV {cv:.2f} < 0.35 (monotonous rhythm)")
    for sc in {s["scene"] for s in shots.values()}:
        ss = [s for s in shots.values() if s["scene"] == sc]
        cu = sum(1 for s in ss if s.get("size") in ("cu", "ecu")) / len(ss)
        if cu > 0.5: warns.append(f"{sc}: close-ups {cu:.0%} > 50%")
    print(json.dumps({"pass": not errors, "errors": errors, "warnings": warns,
                      "metrics": {"shots": len(shots), "static": round(static, 2), "push_in": round(push, 2),
                                  "center": round(center, 2), "duration_cv": round(cv, 2)}},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()
