#!/usr/bin/env python3
"""assemble.py edit_list.csv out.mov [fps] [WxH] - frame-accurate trim+concat in one ffmpeg pass.
Input: 06_review/edit_list.csv (shot_id,file,in_sec,out_sec,note). Point `file` at CONFORMED clips (conform.sh guarantees an audio track).
Clips are fitted inside WxH without distortion (letterbox/pillarbox pad)."""
import csv, subprocess, sys
csv_path, out = sys.argv[1], sys.argv[2]
fps = sys.argv[3] if len(sys.argv) > 3 else "24"
w, h = (sys.argv[4] if len(sys.argv) > 4 else "1920x1080").split("x")
rows = list(csv.DictReader(open(csv_path, newline="")))
cmd, parts = ["ffmpeg", "-hide_banner", "-y"], []
for i, r in enumerate(rows):
    cmd += ["-i", r["file"]]
    a, b = r["in_sec"], r["out_sec"]
    parts.append(
        f"[{i}:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps={fps},"
        f"scale={w}:{h}:flags=lanczos:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv422p10le[v{i}];"
        f"[{i}:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
        f"aresample=48000,aformat=channel_layouts=stereo[a{i}];")
concat = "".join(f"[v{i}][a{i}]" for i in range(len(rows)))
fc = "".join(parts) + f"{concat}concat=n={len(rows)}:v=1:a=1[v][a]"
cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
        "-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "pcm_s24le", out]
subprocess.run(cmd, check=True)
