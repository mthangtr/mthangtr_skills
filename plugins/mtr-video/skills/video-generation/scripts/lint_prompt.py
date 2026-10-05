#!/usr/bin/env python3
"""lint_prompt.py prompt.md manifest.json --profile references/models/<id>/profile.json [--unit-duration 12]
Pre-submit lint for one generation call (references/generation-craft.md sections 3, 4, 7).
All limits (min block length, reference counts and seconds, dialogue length, words per block, tag syntax)
come from the model profile.
Exit 0 = pass (warnings allowed), 1 = errors."""
import json, re, sys, argparse

KEYWORD_SOUP = ["cinematic", "8k", "4k", "masterpiece", "ultra-detailed", "ultra detailed", "hyper-realistic",
                "hyperrealistic", "award-winning", "award winning", "best quality", "trending on artstation",
                "epic", "stunning", "breathtaking", "hollywood-style", "octane render", "unreal engine"]
# Bare emotion words. Vietnamese entries (sad, happy, angry, moved, afraid) are detection data for Vietnamese prompts.
BARE_EMOTION = ["sad", "happy", "angry", "emotional", "scared", "nervous", "heartbroken", "joyful", "depressed",
                "buồn", "vui", "giận", "xúc động", "sợ hãi"]
CAMERA_MOVES = ["push-in", "push in", "dolly in", "dolly out", "pull back", "pull-back", "pan ", "pans ", "tilt",
                "orbit", "crane", "boom up", "tracking", "truck", "zoom", "whip pan", "handheld", "steadicam", "arc "]
TC = re.compile(r"\[(\d{1,2}):(\d{2})\s*[–-]\s*(\d{1,2}):(\d{2})\]")
# Vietnamese-specific letters: used to detect a prompt that mixes Vietnamese and English outside dialogue.
VI = re.compile(r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("prompt"); ap.add_argument("manifest")
    ap.add_argument("--profile", required=True); ap.add_argument("--unit-duration", type=float, default=None); a = ap.parse_args()
    prof = json.load(open(a.profile, encoding="utf-8"))
    R = prof.get("references", {}); SH = prof.get("shots", {}); PR = prof.get("prompt", {})
    min_block = SH.get("min_shot_s", 0); max_line = PR.get("max_words_per_dialogue_line", 15)
    wpb = PR.get("words_per_block", [25, 60]); tag_re = R.get("tag_regex")
    text = open(a.prompt, encoding="utf-8").read(); low = text.lower()
    man = json.load(open(a.manifest, encoding="utf-8")); refs = man.get("refs", [])
    E, W = [], []
    # keyword soup
    hits = [k for k in KEYWORD_SOUP if re.search(r"\b" + re.escape(k) + r"\b", low)]
    if hits: E.append(f"keyword soup: {hits}")
    # timecode blocks
    blocks = list(TC.finditer(text)); spans = []
    for m in blocks:
        s = int(m.group(1)) * 60 + int(m.group(2)); e = int(m.group(3)) * 60 + int(m.group(4)); spans.append((s, e, m.start()))
        if e - s < min_block: E.append(f"block {m.group(0)} shorter than {min_block}s (profile min_shot_s)")
    for (s0, e0, _), (s1, e1, _) in zip(spans, spans[1:]):
        if s1 != e0: E.append(f"timecode gap/overlap between {e0}s and {s1}s")
    if spans and not SH.get("timecode_prompting", True): W.append("timecoded blocks used but the profile says the model has no timecode prompting")
    if len(spans) > 1 and not SH.get("multi_shot_in_call", True): E.append("several shots in one call but the model cannot cut inside a call")
    if a.unit_duration and spans and abs(spans[-1][1] - a.unit_duration) > 0.5:
        E.append(f"timeline ends at {spans[-1][1]}s but unit is {a.unit_duration}s")
    # per-block checks
    bounds = [p for _, _, p in spans] + [len(text)]
    for i, (s, e, p) in enumerate(spans):
        blk = text[p:bounds[i + 1]].split("\n[", 1)[0]; bl = blk.lower()
        moves = sorted({m.strip() for m in CAMERA_MOVES if m in bl})
        if len(moves) > 1 and "@video" not in bl: W.append(f"[{s}-{e}s] several camera moves {moves}")
        words = len(re.findall(r"\w+", blk))
        if words > wpb[1] + 10: W.append(f"[{s}-{e}s] {words} words (profile target {wpb[0]}-{wpb[1]} per block)")
        quotes = re.findall(r'"([^"]+)"', blk)
        if len(quotes) > 1: W.append(f"[{s}-{e}s] {len(quotes)} dialogue lines (1 per block)")
        for q in quotes:
            if len(q.split()) > max_line: E.append(f"[{s}-{e}s] dialogue line > {max_line} words: {q[:40]}...")
        for emo in BARE_EMOTION:
            # "trông" = looks, "cảm thấy" = feels, "rất" = very (Vietnamese detection data)
            if re.search(r"\b(is|looks|feels|seems|trông|cảm thấy)\s+(very\s+|rất\s+)?" + re.escape(emo) + r"\b", bl):
                E.append(f"[{s}-{e}s] bare emotion '{emo}' without physical cue")
    # language: outside quotes
    outside = re.sub(r'"[^"]*"', "", text)
    if VI.search(outside) and re.search(r"\b(the|and|with|camera|shot)\b", outside.lower()):
        E.append("mixed Vietnamese and English outside dialogue: use one prompt language")
    # avoid list
    m = re.search(r"\[AVOID\](.*)", text, re.S)
    if m:
        n = len([x for x in re.split(r"[.\n;]", m.group(1)) if x.strip()])
        if n > 6: W.append(f"AVOID has {n} items (max 6)")
    # camera vs playblast
    if any(r.get("type") == "video_url" for r in refs) and ("@video" in low or "previs" in low):
        if re.search(r"camera (slowly )?(pushes|dollies|orbits|pans|cranes)", low):
            W.append("prompt describes a camera path while @Video controls camera: risk of conflict")
    # manifest limits
    n_img = sum(r.get("type") == "image_url" for r in refs); n_vid = sum(r.get("type") == "video_url" for r in refs)
    n_aud = sum(r.get("type") == "audio_url" for r in refs)
    if n_img > R.get("images_max", 99) or n_vid > R.get("videos_max", 99) or n_aud > R.get("audio_max", 99):
        E.append(f"ref limits exceeded img={n_img}/{R.get('images_max')} vid={n_vid}/{R.get('videos_max')} aud={n_aud}/{R.get('audio_max')}")
    vs = sum(r.get("duration_s", 0) for r in refs if r.get("type") == "video_url")
    au = sum(r.get("duration_s", 0) for r in refs if r.get("type") == "audio_url")
    if R.get("video_total_s_max") is not None and vs > R["video_total_s_max"]: E.append(f"total reference video {vs}s > {R['video_total_s_max']}s")
    if R.get("audio_total_s_max") is not None and au > R["audio_total_s_max"]: E.append(f"total reference audio {au}s > {R['audio_total_s_max']}s")
    if n_aud and not n_img and R.get("audio_requires_image"): E.append("audio reference requires at least one image reference")
    ri, rv = R.get("recommended_images", [0, 99]), R.get("recommended_videos", [0, 99])
    if n_img > ri[1] * 2 or n_vid > rv[1] * 2: W.append(f"{n_img} images / {n_vid} videos: well above the recommended {ri} / {rv}")
    for r in refs:
        tag = r.get("tag", "")
        if not r.get("job"): E.append(f"{tag or r.get('file')}: missing 'job'")
        if r.get("role") and R.get("roles") and r["role"] not in R["roles"]: E.append(f"{tag or r.get('file')}: role {r['role']} not supported {R['roles']}")
        if tag_re and tag and tag.lower() not in low: W.append(f"{tag} not referenced in prompt")
    if tag_re:
        for tag in set(re.findall(tag_re, text)):
            if tag not in {r.get("tag") for r in refs}: E.append(f"{tag} used in prompt but not in manifest")
    print(json.dumps({"pass": not E, "errors": E, "warnings": W, "blocks": len(spans),
                      "refs": {"images": n_img, "videos": n_vid, "audio": n_aud}}, ensure_ascii=False, indent=2))
    sys.exit(0 if not E else 1)

if __name__ == "__main__":
    main()
