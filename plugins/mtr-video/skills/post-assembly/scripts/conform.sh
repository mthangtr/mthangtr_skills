#!/usr/bin/env bash
# conform.sh IN OUT [FPS] [W H]  -> ProRes 422 HQ mezzanine, CFR, Rec.709 tagged, 48k/24-bit PCM stereo
# Default keeps NATIVE resolution (no upscale before picture lock; upscale happens in finishing).
# Pass W H only to fit/pad onto a timeline canvas; the image is never enlarged.
# Clips without an audio stream get a silent 48k stereo track so concat/OTIO tools never break.
set -euo pipefail
IN="$1"; OUT="$2"; FPS="${3:-24}"; W="${4:-}"; H="${5:-}"
GEO=""
if [ -n "$W" ] && [ -n "$H" ]; then
  GEO="scale=w='min(iw,${W})':h='min(ih,${H})':flags=lanczos:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2,"
fi
CMD=(ffmpeg -hide_banner -y -i "$IN")
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | grep -q .; then
  MAP=(-map 0:v:0 -map 0:a:0)
else
  CMD+=(-f lavfi -i anullsrc=r=48000:cl=stereo)
  MAP=(-map 0:v:0 -map 1:a:0 -shortest)
fi
"${CMD[@]}" "${MAP[@]}" \
  -vf "fps=${FPS},${GEO}setsar=1,format=yuv422p10le" \
  -c:v prores_ks -profile:v 3 -vendor apl0 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a pcm_s24le -ar 48000 -ac 2 \
  "$OUT"
