#!/usr/bin/env python3
"""validate_profile.py references/models/<id>/profile.json
Check a video model profile against references/model-profile.schema.json plus sanity rules.
Exit 0 = valid, 1 = errors."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "..", "references", "model-profile.schema.json")

def main(path):
    p = json.load(open(path, encoding="utf-8")); errors, warns = [], []
    try:
        import jsonschema
        for e in jsonschema.Draft202012Validator(json.load(open(SCHEMA))).iter_errors(p):
            errors.append(f"schema: {'/'.join(map(str, e.path))}: {e.message}")
    except ImportError:
        errors.append("jsonschema not installed (pip install jsonschema)")
    o, s, r = p.get("output", {}), p.get("shots", {}), p.get("references", {})
    d = o.get("duration_s", {})
    if d and d.get("min", 0) > d.get("max", 0): errors.append("output.duration_s.min > max")
    if s.get("min_shot_s", 0) > d.get("max", 1e9): errors.append("shots.min_shot_s > output.duration_s.max")
    if not s.get("multi_shot_in_call") and s.get("max_shots_per_call", 1) != 1: errors.append("max_shots_per_call must be 1 when multi_shot_in_call is false")
    if os.path.basename(os.path.dirname(os.path.abspath(path))) != p.get("id"): errors.append("profile id must equal its folder name")
    kn = os.path.join(os.path.dirname(path), p.get("knowledge", "knowledge.md"))
    if not os.path.exists(kn): warns.append(f"knowledge file missing: {kn}")
    for a in p.get("access", []):
        if a.get("adapter") and not os.path.isdir(os.path.join(HERE, "adapters", a["adapter"])):
            errors.append(f"adapter folder missing: scripts/adapters/{a['adapter']}")
    if p.get("verification") == "unverified": warns.append("profile is unverified: run calibration tests T1-T7 before production")
    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warns}, indent=2)); sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(sys.argv[1])
