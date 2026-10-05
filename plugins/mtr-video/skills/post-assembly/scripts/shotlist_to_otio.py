#!/usr/bin/env python3
"""shotlist_to_otio.py edit_list.csv out_basename [fps]
Input: 06_review/edit_list.csv produced by dailies-review/scripts/export_edit_list.py.
Build a first assembly timeline from a shotlist CSV (shot_id,file,in_sec,out_sec,note)
and write .otio + CMX3600 .edl + FCP7 .xml (Resolve/Premiere importable).
Requires: pip install opentimelineio OpenTimelineIO-Plugins"""
import csv, os, subprocess, sys
import opentimelineio as otio

csv_path, base = sys.argv[1], sys.argv[2]
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 24.0
RT, TR = otio.opentime.RationalTime, otio.opentime.TimeRange

def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(out.stdout.strip())

tl = otio.schema.Timeline(name=os.path.basename(base))
v1 = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
a1 = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)
tl.tracks.extend([v1, a1])

with open(csv_path, newline="") as f:
    for row in csv.DictReader(f):
        start = RT(round(float(row["in_sec"]) * fps), fps)
        dur = RT(round((float(row["out_sec"]) - float(row["in_sec"])) * fps), fps)
        url = os.path.abspath(row["file"])
        for track in (v1, a1):
            clip = otio.schema.Clip(
                name=row["shot_id"],
                media_reference=otio.schema.ExternalReference(
                    target_url=url,
                    available_range=TR(RT(0, fps), RT(round(media_duration(url) * fps), fps))),
                source_range=TR(start, dur),
                metadata={"ai_film_studio": {"note": row.get("note", ""), "file": row["file"]}},
            )
            if track is v1 and row.get("note"):
                clip.markers.append(otio.schema.Marker(
                    name=row["note"], marked_range=TR(RT(0, fps), RT(1, fps)),
                    color=otio.schema.MarkerColor.RED))
            track.append(clip)

otio.adapters.write_to_file(tl, base + ".otio")
otio.adapters.write_to_file(tl, base + ".xml", adapter_name="fcp_xml")
edl_tl = otio.schema.Timeline(name=tl.name)          # CMX3600 = one video track only
edl_tl.tracks.append(v1.deepcopy())
otio.adapters.write_to_file(edl_tl, base + ".edl", adapter_name="cmx_3600")
print(f"timeline duration: {otio.opentime.to_timecode(tl.duration(), fps)}  clips: {len(v1)}")
