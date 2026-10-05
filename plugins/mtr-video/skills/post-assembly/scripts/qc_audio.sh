#!/usr/bin/env bash
# qc_audio.sh FILE -> integrated, LRA, true peak (BS.1770 / R128 scanner)
ffmpeg -hide_banner -nostats -i "$1" -vn -filter_complex ebur128=peak=true -f null - 2>&1 | sed -n '/Summary:/,$p'
