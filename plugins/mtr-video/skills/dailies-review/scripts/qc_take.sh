#!/usr/bin/env bash
# usage: qc_take.sh take.mp4 [expected_duration_s] [expected_fps] [out_dir=06_review/qc]
# exit 0 = technical pass, 2 = technical FAIL (fps/duration mismatch, black/freeze frames, no audio stream)
set -euo pipefail
IN="$1"; EXP_DUR="${2:-}"; EXP_FPS="${3:-24}"
OUT_ROOT="${4:-06_review/qc}"
B="$(basename "${IN%.*}")"; D="$OUT_ROOT/$B"; mkdir -p "$D"
ffprobe -v error -show_streams -show_format -of json "$IN" > "$D/probe.json"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$IN")
ffmpeg -y -loglevel error -i "$IN" -frames:v 1 "$D/first.png"
ffmpeg -y -loglevel error -sseof -0.1 -i "$IN" -frames:v 1 -update 1 "$D/last.png"
ffmpeg -y -loglevel error -i "$IN" -vf "fps=2,scale=320:-2,drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=4x4:padding=4:margin=4" "$D/sheet_%02d.jpg"
ffmpeg -hide_banner -nostats -i "$IN" \
  -vf "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=0.003:d=0.5,scdet=t=10" \
  -af "silencedetect=n=-50dB:d=0.5,ebur128=peak=true,astats=metadata=0" -f null - 2> "$D/detect.log" || true
ffmpeg -y -loglevel error -i "$IN" -lavfi "showspectrumpic=s=1024x512:legend=1" "$D/spec.png" || true
ffmpeg -y -loglevel error -i "$IN" -filter_complex "aformat=channel_layouts=mono,showwavespic=s=1600x240:colors=white" -frames:v 1 "$D/wave.png" || true
{
  echo "take=$B duration=$DUR fps=$FPS expected_dur=${EXP_DUR:-na} expected_fps=$EXP_FPS"
  echo "black:   $(grep -c black_start "$D/detect.log" || true)"
  echo "freeze:  $(grep -c freeze_start "$D/detect.log" || true)"
  echo "cuts:    $(grep -c 'lavfi.scd.time' "$D/detect.log" || true)"
  echo "silence: $(grep -c silence_start "$D/detect.log" || true)"
  grep -E "^\s+I:|^\s+LRA:|^\s+Peak:" "$D/detect.log" | sed 's/^ */loud: /' || true
} | tee "$D/tech_summary.txt"

# ---- pass/fail ----
FAIL=0
FPS_NUM=$(python3 -c "f='$FPS'.split('/'); print(round(float(f[0])/float(f[1] if len(f)>1 else 1),3))")
if python3 -c "import sys; sys.exit(0 if abs($FPS_NUM-$EXP_FPS)<0.01 else 1)"; then :; else echo "FAIL fps $FPS_NUM != $EXP_FPS" | tee -a "$D/tech_summary.txt"; FAIL=1; fi
if [ -n "$EXP_DUR" ]; then
  if python3 -c "import sys; sys.exit(0 if abs($DUR-$EXP_DUR)<=0.1 else 1)"; then :; else echo "FAIL duration $DUR != $EXP_DUR (±0.1s; some models add frames, see profile ingest.extra_frames)" | tee -a "$D/tech_summary.txt"; FAIL=1; fi
fi
if [ "$(grep -c black_start "$D/detect.log" || true)" -gt 0 ]; then echo "FAIL black frames" | tee -a "$D/tech_summary.txt"; FAIL=1; fi
if [ "$(grep -c freeze_start "$D/detect.log" || true)" -gt 0 ]; then echo "WARN freeze detected (check if intentional)" | tee -a "$D/tech_summary.txt"; fi
if ! ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | grep -q .; then echo "WARN no audio stream" | tee -a "$D/tech_summary.txt"; fi
if [ "$FAIL" -eq 0 ]; then echo "TECH PASS" | tee -a "$D/tech_summary.txt"; exit 0; else echo "TECH FAIL" | tee -a "$D/tech_summary.txt"; exit 2; fi
