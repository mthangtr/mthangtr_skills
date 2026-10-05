#!/usr/bin/env python3
"""build_request.py prompt.md manifest.json out_request.json --duration 12 --ratio 16:9 [--resolution 480p] [--seed N]
Build an Ark-format task body (BytePlus ModelArk / Volcano Engine) from the unit manifest and prompt.
Content order = manifest order, so @Image1/@Video1 tags match the array position.
Every ref needs a public or signed 'url' (upload local files to your storage first).
Model id and params come from third-party docs (knowledge.md section 7): confirm in the BytePlus console (test T2)."""
import json, argparse, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt"); ap.add_argument("manifest"); ap.add_argument("out")
    ap.add_argument("--duration", type=int, required=True); ap.add_argument("--ratio", required=True)
    ap.add_argument("--resolution", default="480p"); ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--no-audio", action="store_true"); ap.add_argument("--task-type", default=None,
                    choices=[None, "auto", "reference", "edit", "extend"])
    a = ap.parse_args()
    man = json.load(open(a.manifest, encoding="utf-8"))
    content = [{"type": "text", "text": open(a.prompt, encoding="utf-8").read().strip()}]
    for r in man.get("refs", []):
        if not r.get("url"):
            sys.exit(f"{r.get('tag')}: no 'url' (upload {r.get('file')} first)")
        t = r["type"]; key = t  # image_url / video_url / audio_url
        content.append({"type": t, key: {"url": r["url"]}, "role": r["role"]})
    if not 4 <= a.duration <= 30 and a.duration != -1:
        sys.exit("duration must be 4-30 (or -1 for edit)")
    body = {"model": man.get("model", "dreamina-seedance-2-5-260628"), "content": content,
            "resolution": a.resolution, "ratio": "adaptive" if a.task_type in ("edit", "extend") else a.ratio,
            "duration": a.duration, "seed": a.seed, "generate_audio": not a.no_audio,
            "watermark": False, "return_last_frame": True}
    if a.task_type: body["omni_reference_task_type"] = a.task_type
    json.dump(body, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {a.out}: {len(content) - 1} refs, {a.duration}s, {a.resolution}, seed {a.seed}")

if __name__ == "__main__":
    main()
