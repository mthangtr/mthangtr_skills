#!/usr/bin/env bash
# loudnorm2pass.sh IN OUT.wav [I] [TP] [LRA]
# Defaults: -14 LUFS / -1 dBTP / LRA 11 (web). EBU: -23 -1 ; ATSC: -24 -2.
# Netflix -27 is DIALOG-GATED: verify with a dialog-gated meter, not loudnorm.
set -euo pipefail
IN="$1"; OUT="$2"; I="${3:--14}"; TP="${4:--1}"; LRA="${5:-11}"
JSON=$(ffmpeg -hide_banner -nostats -i "$IN" -vn \
  -af "loudnorm=I=${I}:TP=${TP}:LRA=${LRA}:print_format=json" -f null - 2>&1 \
  | sed -n '/^{/,/^}/p')
get() { echo "$JSON" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
MI=$(get input_i); MTP=$(get input_tp); MLRA=$(get input_lra); MT=$(get input_thresh); OFF=$(get target_offset)
echo "pass1: I=$MI TP=$MTP LRA=$MLRA thresh=$MT offset=$OFF"
ffmpeg -hide_banner -y -i "$IN" -vn \
  -af "loudnorm=I=${I}:TP=${TP}:LRA=${LRA}:measured_I=${MI}:measured_TP=${MTP}:measured_LRA=${MLRA}:measured_thresh=${MT}:offset=${OFF}:linear=true:print_format=summary,aresample=48000" \
  -c:a pcm_s24le "$OUT" 2>&1 | grep -E "Normalization Type|Output Integrated|Output True Peak"
