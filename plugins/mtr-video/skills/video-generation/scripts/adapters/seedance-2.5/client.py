#!/usr/bin/env python3
"""client.py request.json out_video.mp4 --unit U01 --take U01_T01_r1 [--log 05_takes/generation_log.jsonl] [--price-per-s 0.1028]
Submit an Ark task, poll until done, download video + last frame immediately (URLs expire ~24h), append a log line.
Env: ARK_API_KEY (required), ARK_BASE_URL (default https://ark.ap-southeast.bytepluses.com/api/v3).
[UNVERIFIED] Endpoint, statuses and fields follow third-party docs (knowledge.md section 7). Verify with test T2 before batch use.
Never print or store the API key."""
import json, os, sys, time, hashlib, argparse, urllib.request

def call(method, url, key, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("request"); ap.add_argument("out")
    ap.add_argument("--unit", required=True); ap.add_argument("--take", required=True)
    ap.add_argument("--log", default="05_takes/generation_log.jsonl"); ap.add_argument("--price-per-s", type=float, default=None)
    ap.add_argument("--ref-video-s", type=float, default=0.0); ap.add_argument("--timeout-min", type=int, default=20)
    a = ap.parse_args()
    key = os.environ.get("ARK_API_KEY") or sys.exit("set ARK_API_KEY")
    base = os.environ.get("ARK_BASE_URL", "https://ark.ap-southeast.bytepluses.com/api/v3").rstrip("/")
    body = json.load(open(a.request, encoding="utf-8")); t0 = time.time()
    tid = call("POST", f"{base}/contents/generations/tasks", key, body)["id"]
    print("task", tid); time.sleep(25); t = {}
    while time.time() - t0 < a.timeout_min * 60:
        t = call("GET", f"{base}/contents/generations/tasks/{tid}", key)
        if t.get("status") in ("succeeded", "failed", "expired", "cancelled"): break
        time.sleep(15)
    status = t.get("status", "timeout"); c = t.get("content", {})
    if status == "succeeded":
        urllib.request.urlretrieve(c["video_url"], a.out)
        if c.get("last_frame_url"):
            urllib.request.urlretrieve(c["last_frame_url"], os.path.splitext(a.out)[0] + "_last.png")
    dur = body.get("duration", 0)
    line = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "unit": a.unit, "take": a.take,
            "model": body.get("model"), "task_id": tid, "seed": body.get("seed"), "res": body.get("resolution"),
            "dur_out": dur, "dur_ref_video": a.ref_video_s, "tokens": (t.get("usage") or {}).get("total_tokens"),
            "usd_est": round(a.price_per_s * (dur + a.ref_video_s), 4) if a.price_per_s else None,
            "wall_s": round(time.time() - t0), "status": status, "verdict": "pending_dailies",
            "prompt_sha": hashlib.sha256(body["content"][0]["text"].encode()).hexdigest()[:12]}
    os.makedirs(os.path.dirname(a.log) or ".", exist_ok=True)
    open(a.log, "a", encoding="utf-8").write(json.dumps(line) + "\n")
    print(json.dumps(line, indent=2)); sys.exit(0 if status == "succeeded" else 1)

if __name__ == "__main__":
    main()
