---
name: blender-previs
description: >
  This skill should be used when the user wants to build previs / layout in Blender from a shot list, usually
  through the Blender MCP, e.g. "build previs", "previs a scene", "build the scene in Blender", "set up the
  camera from the shot list", "set up the camera in Blender", "blocking in Blender", "clay render", "playblast",
  "render references for the video model". It produces clay/seg/depth passes, first/last frames and a manifest per unit.
metadata:
  version: "0.3.0"
---

# Blender previs

For each generation unit in `03_shotlist.json`, build the Blender scene with correct scale, camera, blocking and lighting, then export references for the video model to `04_previs/<unit>/v<ver>/`. Detailed knowledge: `references/knowledge.md`. Code library: `scripts/afs_previs_lib.py`. Common law: `../film-pipeline/references/shared-conventions.md`.

## Before starting

1. Confirm the Blender MCP is connected (call `get_objects_summary`). If not, tell the user and stop.
2. Safety check (knowledge.md §9.5): Blender runs on a machine/VM with no sensitive data, Auto Run Python Scripts is off, the MCP binds to localhost only. Remind the user once if not yet confirmed.
3. Load the library into the Blender session: read `scripts/afs_previs_lib.py`, send it via `execute_blender_code` as `import types, sys; m = types.ModuleType("afs_previs_lib"); exec(SRC, m.__dict__); sys.modules["afs_previs_lib"] = m`. Subsequent calls use `import afs_previs_lib as afs`.
4. The library has only passed a syntax check and has not been run on Blender 5.x. On first use, run each function and verify the result; look up any doubtful API with `search_api_docs` / `get_python_api_docs` first (5.x change list: knowledge.md §4; runtime checkpoints: §12). When you fix a bug, tell the user so the plugin can be updated.

## Principles (knowledge.md §1)

- Previs is for making decisions, not for looking good: primitives + mannequins are enough. Spatially correct beats visually finished.
- Real scale, units in meters (people 1.60–1.85 m, eyes ≈ 0.93 × height, doors 2.0–2.1 m, tables 0.75 m).
- Virtual camera = real camera: `lens = shotlist.lens_mm`, `sensor_width = 36` (full-frame equivalent), `camera_height_m`, DOF per `dof`.
- 24 fps: frame = round(duration_s × 24). Pan no faster than one frame width per ~7 s.
- Build only what the camera sees or what creates occlusion/shadow/eyeline.
- Reference images must be clean: turn off overlays, grid, gizmos, text, motion paths.
- Human stand-ins are pills; use a distinct color in the seg pass to map characters.

## Per-unit procedure (knowledge.md §2)

0. Read the unit + shots and the unit's model profile (`video-generation/references/models/<id>/profile.json`); compute frame ranges; confirm the total is within the profile's `output.duration_s`; render only the reference types the profile supports (`control.video_reference_camera`, `control.structure_reference`, `first_frame`).
1. Snapshot state (`get_objects_summary`); ensure there are no unexpected duplicate names.
2. `setup_unit_scene`: units, 24 fps, resolution per aspect, color management Standard.
3. Set blockout (`SET_*`, ≤ ~40 objects, CC0 assets if needed).
4. Human proxies `CHR_<C01>` per `characters_in_frame`, height from `characters[].height_m`, position and facing from `scenes[].blocking` marks.
5. Blocking animation per `action.primary` and `screen_direction` (walking 1.2–1.5 m/s).
6. `create_shot_camera` for each shot; distance derived from `size` and lens. The function does not yet read `blocking.marks`, `axis.camera_side`, `angle`, `focus` itself: compute `azimuth_deg` from the 180° axis and camera side, set `aim_offset_z`/camera height per `angle`, and record the choices in the manifest.
7. `animate_move` per `camera.move`, `speed`, `direction` (supports push_in, pull_out, track/truck, crane, arc, pan, tilt, zoom; whip_pan and dolly_zoom must be built by hand and are flagged high-risk).
8. `bind_markers`: exactly one marker per shot.
9. Lighting per the scene's `lighting` (lit-clay pass only).
10. `check_shot` on the whole unit + a VIEW_3D screenshot in camera view to inspect framing yourself.
11. Render passes: clay (Workbench) → seg → depth → lit-clay (hero units). Render a PNG sequence, then encode mp4 with the command returned by `encode_png_sequence()` (run ffmpeg on the machine holding the frames). Do not use Blender's direct video output because the frame range is inserted into the file name.
12. First/last stills per shot, `export_camera_json`, manifest.
13. `save_version` (copy=True, version only increments).

Make each `execute_blender_code` call do one thing (≤ ~60 lines), wrap it in try/except, return `result`. Verify by numbers, then by eye. Split long renders into 24–48 frame chunks to avoid timeouts.

## Output specs (knowledge.md §7)

- Video ref: 24 fps, 1920×1080 (draft 1280×720), H.264 High yuv420p CRF 14–18, no audio, no motion blur, exact frame count, correct output aspect.
- Clay = strictly gray; color only in the seg pass (one color per character, used for mapping "red stand-in = @Image1"). Depth: near white, far black, one fixed near/far for the whole unit.
- Render at exactly `film.gen_ratio` (e.g. 21:9 for a film delivered at 2.39:1), no letterbox.
- A 3–5 s camera test is more reliable than a long clip.
- Naming: `AFS_<unit>_<pass>_v<ver>.mp4`, `AFS_<shot>_<pass>_first_v<ver>.png`, manifest JSON including lens/sensor/height/distance and measured move speed.
- Write the ref paths into `units[].previs_ref` for `video-generation` to read.

## Anti-patterns (knowledge.md §10)

Overly detailed sets; wrong scale; lens/sensor not matching the shotlist; unmotivated lighting; camera passing through geometry; moves too fast causing strobing at 24 fps; missing headroom/lead room; renders with busy textures or wrong aspect that mislead the AI; forgetting to bake animation; one giant script failing midway; using context-dependent `bpy.ops` to delete objects.

## Gate (knowledge.md §11)

- [ ] Each shot: lens matches the shotlist, `sensor_width` recorded in the manifest, camera height ±5 cm, distance within ±10% of the value `create_shot_camera` computes from size + lens (table §5.3 is for an S35 sensor; convert if used) or a reason given.
- [ ] `check_shot` 0 blocking errors (framing, occlusion, camera-in-geometry, speed).
- [ ] Passes correctly named, correct frame count, no overlays.
- [ ] Manifest + camera JSON + `.blend` version saved.
- [ ] The user views the screenshot/thumbnail of each shot and approves.

When passed: update `project_state.json` (`units_done`) and move that unit to `video-generation`.
