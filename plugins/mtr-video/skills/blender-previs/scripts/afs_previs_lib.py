# Assembled from references/knowledge.md section 8. Syntax-checked; NOT yet run in Blender 5.x — see section 12 for runtime checks.
# afs_previs_lib.py  — Blender 5.1+  (Python 3.13)
import bpy, bmesh, math, json, os, re
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

PROJECT = "AFS"
FPS = 24
FRAME_H = {"ecu": 0.15, "cu": 0.35, "mcu": 0.60, "ms": 0.95, "cowboy": 1.35,
           "mws": 1.60, "fs": 2.10, "ws": 5.0, "ews": 15.0}       # metres visible at subject
DOF_FSTOP = {"deep": None, "medium": 4.0, "shallow": 2.0}           # None = DOF off
SPEED_MPS = {"imperceptible": 0.06, "slow": 0.25, "medium": 0.7, "fast": 1.4}

def ensure_collection(name, parent=None, scene=None):
    scene = scene or bpy.context.scene
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    parent = parent or scene.collection
    if coll.name not in parent.children:
        parent.children.link(coll)
    return coll

def purge_object(name):
    ob = bpy.data.objects.get(name)
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)

def new_object(name, data, coll):
    """Delete-and-recreate by name => idempotent. data=None makes an Empty."""
    purge_object(name)
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    return ob

def sec_to_frames(s, fps=FPS):
    return int(round(s * fps))

def iter_fcurves(id_):
    """Blender 4.4+/5.x layered actions: Action.layers[].strips[].channelbag(slot).fcurves"""
    ad = getattr(id_, "animation_data", None)
    if not ad or not ad.action:
        return
    slot = ad.action_slot
    for layer in ad.action.layers:
        for strip in layer.strips:
            cb = strip.channelbag(slot) if slot else None
            if cb:
                yield from cb.fcurves

def set_interpolation(id_, interp="BEZIER", easing="AUTO", handle="AUTO_CLAMPED"):
    for fc in iter_fcurves(id_):
        for kp in fc.keyframe_points:
            kp.interpolation = interp          # 'CONSTANT' | 'LINEAR' | 'BEZIER' | 'SINE' ...
            kp.easing = easing                 # 'AUTO' | 'EASE_IN' | 'EASE_OUT' | 'EASE_IN_OUT'
            kp.handle_left_type = handle
            kp.handle_right_type = handle
        fc.update()


def setup_unit_scene(unit, shots, res=(1920, 1080), start=1001, set_coll="SET"):
    """unit: dict from shotlist.units[]; shots: list of shot dicts of this unit."""
    name = unit["id"]
    sc = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
    us = sc.unit_settings
    us.system, us.scale_length, us.length_unit = 'METRIC', 1.0, 'METERS'
    r = sc.render
    r.fps, r.fps_base = FPS, 1.0
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    r.pixel_aspect_x = r.pixel_aspect_y = 1.0
    r.use_motion_blur = False
    sc.frame_start = start
    sc.frame_end = start + sec_to_frames(unit["duration_s"]) - 1
    vs = sc.view_settings
    vs.view_transform = 'Standard'   # no AgX tonemapping on data passes
    vs.look = 'None'                 # [UNSURE-5.x] look identifiers; 'None' valid in 4.x/5.x
    vs.exposure, vs.gamma = 0.0, 1.0
    if sc.world is None:
        sc.world = bpy.data.worlds.get("WRL_previs") or bpy.data.worlds.new("WRL_previs")
    sc.world.color = (0.62, 0.66, 0.70)          # Workbench render background = World viewport color
    sc["afs_unit"] = name
    shared = bpy.data.collections.get(set_coll)
    if shared and shared.name not in sc.collection.children:
        sc.collection.children.link(shared)       # same SET in every unit scene
    if bpy.context.window:
        bpy.context.window.scene = sc
    frames = {s["id"]: [start + sec_to_frames(s["unit_time_s"][0]),
                        start + sec_to_frames(s["unit_time_s"][1]) - 1] for s in shots}
    return {"scene": sc.name, "frame_range": [sc.frame_start, sc.frame_end], "shots": frames}


def _add_cyl(bm, r, depth, center, seg=16):
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r, depth=depth,
                          matrix=Matrix.Translation(center))

def add_human_proxy(char_id, height=1.75, loc=(0, 0, 0), facing_deg=0.0,
                    color=(0.75, 0.75, 0.75, 1.0), coll_name="CHR", limbs=False):
    """Pill-style stand-in. Faces -Y at facing_deg=0. Root empty at feet."""
    coll = ensure_collection(coll_name)
    s = height / 1.75
    root = new_object(f"CHR_{char_id}", None, coll)
    root.empty_display_type, root.empty_display_size = 'PLAIN_AXES', 0.3
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(facing_deg))
    root["eye_height"] = 0.93 * height
    root["height"] = height
    me_name = f"CHR_{char_id}_body"
    old = bpy.data.meshes.get(me_name)
    purge_object(me_name)
    if old:
        bpy.data.meshes.remove(old)
    me = bpy.data.meshes.new(me_name)
    bm = bmesh.new()
    _add_cyl(bm, 0.15 * s, 0.85 * s, (0, 0, 0.425 * s))            # legs block
    _add_cyl(bm, 0.20 * s, 0.62 * s, (0, 0, 1.16 * s))             # torso
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.115 * s,
                              matrix=Matrix.Translation((0, 0, 1.635 * s)))   # head, top = height
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=8,      # "nose" = facing
                          radius1=0.035 * s, radius2=0.0, depth=0.08 * s,
                          matrix=Matrix.Translation((0, -0.14 * s, 1.63 * s)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    if limbs:
        for x in (-0.25, 0.25):
            _add_cyl(bm, 0.045 * s, 0.62 * s, (x * s, 0, 1.15 * s), seg=8)
    bm.to_mesh(me); bm.free()
    body = bpy.data.objects.new(me_name, me)
    coll.objects.link(body)
    body.parent = root
    body.color = color            # used by Workbench color_type='OBJECT' (seg pass)
    return {"root": root.name, "body": body.name, "eye_height": root["eye_height"]}


def block_walk(char_id, waypoints, start_frame, speed=1.35, scene=None, ease_ends=True):
    """waypoints: [(x,y), ...] metres. Root faces travel direction (-Y forward)."""
    scene = scene or bpy.context.scene
    root = bpy.data.objects[f"CHR_{char_id}"]
    root.animation_data_clear()
    f = float(start_frame); prev = None; yaw = root.rotation_euler.z
    for i, (x, y) in enumerate(waypoints):
        p = Vector((x, y, root.location.z))
        if prev is not None:
            seg = p - prev
            f += seg.length / speed * scene.render.fps
            yaw = math.atan2(seg.y, seg.x) + math.pi / 2
            if i == 1:  # face direction from the start
                root.rotation_euler.z = yaw
                root.keyframe_insert("rotation_euler", index=2, frame=start_frame)
        root.location = p
        root.keyframe_insert("location", frame=round(f))
        root.rotation_euler.z = yaw
        root.keyframe_insert("rotation_euler", index=2, frame=round(f))
        prev = p
    set_interpolation(root, "LINEAR")
    if ease_ends:   # ease only first/last key
        for fc in iter_fcurves(root):
            kps = fc.keyframe_points
            for kp in (kps[0], kps[-1]):
                kp.interpolation = 'BEZIER'
            fc.update()
    return {"end_frame": round(f), "speed_mps": speed}


def create_shot_camera(shot, subject_id, scene=None, sensor_w=36.0,  # FF-equivalent, see §5.1
 azimuth_deg=0.0,
                       distance=None, aim_offset_z=0.0):
    """Rig: RIG_root (dolly base, animated) -> CAM (Track To -> RIG_aim)."""
    scene = scene or bpy.context.scene
    sid = shot["id"]
    coll = ensure_collection(f"CAM_{scene.name}", scene=scene)
    subj = bpy.data.objects[f"CHR_{subject_id}"]
    eye = subj.get("eye_height", 1.63)
    aim_pt = subj.matrix_world.translation + Vector((0, 0, eye + aim_offset_z))
    res = (scene.render.resolution_x, scene.render.resolution_y)
    sensor_h = sensor_w * res[1] / res[0]
    d = distance or FRAME_H[shot["size"]] * shot["lens_mm"] / sensor_h
    fwd = (subj.matrix_world.to_quaternion() @ Vector((0, -1, 0)))
    fwd.z = 0; fwd.normalize()
    dir_ = Matrix.Rotation(math.radians(azimuth_deg), 3, 'Z') @ fwd   # 0 = in front of subject
    cam_h = shot.get("camera_height_m", eye)

    root = new_object(f"RIG_{sid}_root", None, coll)
    root.empty_display_type, root.empty_display_size = 'CUBE', 0.15
    root.location = (aim_pt.x + dir_.x * d, aim_pt.y + dir_.y * d, cam_h)
    aim = new_object(f"RIG_{sid}_aim", None, coll)
    aim.empty_display_type, aim.empty_display_size = 'SPHERE', 0.08
    aim.location = aim_pt

    cd = bpy.data.cameras.get(f"CAM_{sid}") or bpy.data.cameras.new(f"CAM_{sid}")
    cd.type = 'PERSP'
    cd.lens_unit, cd.lens = 'MILLIMETERS', float(shot["lens_mm"])
    cd.sensor_fit, cd.sensor_width = 'HORIZONTAL', sensor_w
    cd.clip_start, cd.clip_end = 0.05, 1000.0
    fst = DOF_FSTOP.get(shot.get("dof", "deep"))
    cd.dof.use_dof = fst is not None
    cd.dof.focus_object = aim
    if fst:
        cd.dof.aperture_fstop = fst
    cam = new_object(f"CAM_{sid}", cd, coll)
    cam.parent = root                      # local (0,0,0) => sits on root
    con = cam.constraints.new('TRACK_TO')
    con.target, con.track_axis, con.up_axis = aim, 'TRACK_NEGATIVE_Z', 'UP_Y'
    for k, v in (("shot_id", sid), ("size", shot["size"]), ("lens_mm", shot["lens_mm"]),
                 ("subject", subject_id), ("distance_m", round(d, 3))):
        cam[k] = v
    return {"camera": cam.name, "distance_m": round(d, 3), "height_m": cam_h,
            "hfov_deg": round(math.degrees(2 * math.atan(sensor_w / 2 / cd.lens)), 2)}


def animate_move(shot, frame_in, frame_out, move=None, amount=None, speed=None,
                 start_delay_s=0.0, ease=True):
    move = move or shot["camera"]["move"]
    sid = shot["id"]
    root = bpy.data.objects[f"RIG_{sid}_root"]; aim = bpy.data.objects[f"RIG_{sid}_aim"]
    root.animation_data_clear()
    if move in ("static", "handheld"):
        return {"move": move, "keys": 0}
    f0 = frame_in + sec_to_frames(start_delay_s); f1 = frame_out
    dur = max(1, f1 - f0) / FPS
    dist = (amount if amount is not None else
            (speed or SPEED_MPS[shot["camera"].get("speed", "slow")]) * dur)
    p0 = root.location.copy()
    fwd = aim.location - p0; fwd.z = 0; fwd.normalize()
    right = fwd.cross(Vector((0, 0, 1)))
    if move == "push_in":    p1 = p0 + fwd * dist
    elif move == "pull_out": p1 = p0 - fwd * dist
    elif move in ("track", "truck"):
        sign = -1 if "left" in shot["camera"].get("direction", "") else 1
        p1 = p0 + right * dist * sign
    elif move == "crane_up":   p1 = p0 + Vector((0, 0, dist))
    elif move == "crane_down": p1 = p0 - Vector((0, 0, dist))
    elif move == "arc":
        return animate_arc(shot, f0, f1, math.degrees(dist / max((aim.location - p0).length, 0.1)))
    elif move in ("pan", "tilt"):
        return animate_pan_tilt(shot, f0, f1, move, amount_deg=amount)
    elif move == "zoom":
        return animate_zoom(shot, f0, f1, factor=amount)
    else:
        raise ValueError(f"move {move} not handled (whip_pan/dolly_zoom: build manually, high AI risk)")
    root.location = p0; root.keyframe_insert("location", frame=f0)
    root.location = p1; root.keyframe_insert("location", frame=f1)
    set_interpolation(root, "BEZIER" if ease else "LINEAR")
    return {"move": move, "dist_m": round(dist, 3), "speed_mps": round(dist / dur, 3),
            "frames": [f0, f1]}


PAN_DEG_PER_S = {"imperceptible": 1.5, "slow": 4.0, "medium": 9.0, "fast": 20.0}   # slow ~ 1 frame width / 7-10 s at 50mm FF [HEURISTIC]

def animate_pan_tilt(shot, f0, f1, move, amount_deg=None):
    """Rotate the aim empty around the camera position: pan = around Z, tilt = around camera right axis."""
    sid = shot["id"]
    root = bpy.data.objects[f"RIG_{sid}_root"]; aim = bpy.data.objects[f"RIG_{sid}_aim"]
    aim.animation_data_clear()
    dur = max(1, f1 - f0) / FPS
    deg = amount_deg if amount_deg is not None else PAN_DEG_PER_S[shot["camera"].get("speed", "slow")] * dur
    direction = shot["camera"].get("direction", "")
    if any(w in direction for w in ("left", "down")):
        deg = -deg
    cam_pos = root.location.copy()
    v = aim.location - cam_pos
    if move == "pan":
        rot = Matrix.Rotation(math.radians(deg), 3, 'Z')
    else:
        axis = v.cross(Vector((0, 0, 1))); axis.normalize()
        rot = Matrix.Rotation(math.radians(-deg), 3, axis)
    a0 = aim.location.copy(); a1 = cam_pos + rot @ v
    aim.location = a0; aim.keyframe_insert("location", frame=f0)
    aim.location = a1; aim.keyframe_insert("location", frame=f1)
    set_interpolation(aim, "BEZIER")
    return {"move": move, "deg": round(deg, 2), "deg_per_s": round(abs(deg) / dur, 2), "frames": [f0, f1]}

def animate_zoom(shot, f0, f1, factor=None):
    """Keyframe focal length. factor >1 = zoom in. Default: slow 1.25x over the move."""
    sid = shot["id"]
    cd = bpy.data.cameras[f"CAM_{sid}"]
    if cd.animation_data:
        cd.animation_data_clear()
    factor = factor or {"imperceptible": 1.08, "slow": 1.25, "medium": 1.5, "fast": 2.0}[shot["camera"].get("speed", "slow")]
    if "out" in shot["camera"].get("direction", ""):
        factor = 1 / factor
    l0 = cd.lens
    cd.keyframe_insert("lens", frame=f0)
    cd.lens = l0 * factor; cd.keyframe_insert("lens", frame=f1)
    cd.lens = l0
    return {"move": "zoom", "lens_mm": [round(l0, 1), round(l0 * factor, 1)], "frames": [f0, f1]}

def animate_arc(shot, f0, f1, degrees):
    sid = shot["id"]
    root = bpy.data.objects[f"RIG_{sid}_root"]; aim = bpy.data.objects[f"RIG_{sid}_aim"]
    coll = root.users_collection[0]
    piv = new_object(f"RIG_{sid}_pivot", None, coll)
    piv.location = (aim.location.x, aim.location.y, 0.0)
    bpy.context.view_layer.update()
    mw = root.matrix_world.copy()
    root.parent = piv; root.matrix_world = mw              # keep transform
    piv.rotation_euler.z = 0; piv.keyframe_insert("rotation_euler", index=2, frame=f0)
    piv.rotation_euler.z = math.radians(degrees); piv.keyframe_insert("rotation_euler", index=2, frame=f1)
    set_interpolation(piv, "BEZIER")
    return {"move": "arc", "degrees": round(degrees, 2), "frames": [f0, f1]}

def add_handheld(shot, frame_in, strength=0.02, scale=18.0):
    """Shake the AIM point (Track To overrides camera rotation, so rotational noise on camera is lost)."""
    aim = bpy.data.objects[f"RIG_{shot['id']}_aim"]
    aim.keyframe_insert("location", frame=frame_in)
    for fc in iter_fcurves(aim):
        if fc.data_path == "location":
            for m in list(fc.modifiers):
                fc.modifiers.remove(m)
            n = fc.modifiers.new('NOISE')
            n.scale, n.strength, n.phase = scale, strength, 17.3 * (fc.array_index + 1)
    return {"handheld": True, "strength_m": strength}


def bind_markers(scene, shot_frames):
    """shot_frames: {shot_id: [f_in, f_out]} from setup_unit_scene."""
    for m in [m for m in scene.timeline_markers if m.name.startswith("S")]:
        scene.timeline_markers.remove(m)
    for sid, (f_in, _) in sorted(shot_frames.items(), key=lambda kv: kv[1][0]):
        m = scene.timeline_markers.new(sid, frame=f_in)
        m.camera = bpy.data.objects[f"CAM_{sid}"]
    first = min(shot_frames.items(), key=lambda kv: kv[1][0])[0]
    scene.camera = bpy.data.objects[f"CAM_{first}"]
    return {"markers": [(m.name, m.frame) for m in scene.timeline_markers]}


def add_light(name, ltype, loc, energy, kelvin, coll, target=None, size=1.0,
              spot_deg=None, motivation=""):
    ld = bpy.data.lights.get(name)
    if ld is not None and ld.type != ltype:
        purge_object(name); bpy.data.lights.remove(ld); ld = None
    ld = ld or bpy.data.lights.new(name, ltype)
    ld.energy = energy
    ld.color = (1.0, 1.0, 1.0)
    ld.use_temperature, ld.temperature = True, float(kelvin)   # Blender 5.x
    if ltype == 'AREA':
        ld.shape, ld.size = 'DISK', size
    if ltype == 'SPOT':
        ld.spot_size, ld.spot_blend = math.radians(spot_deg or 40), 0.25
    ob = new_object(name, ld, coll)
    ob.location = loc
    ob["motivation"] = motivation
    if target is not None:
        c = ob.constraints.new('TRACK_TO')
        c.target, c.track_axis, c.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
    return ob

def three_point(subject_id, cam_name, key_side="left", ratio=4.0, key_w=200.0,
                key_k=5600, fill_k=5600, rim_k=6500, coll_name="LGT"):
    coll = ensure_collection(coll_name)
    subj = bpy.data.objects[f"CHR_{subject_id}"]; cam = bpy.data.objects[cam_name]
    tgt_name = f"LGT_{subject_id}_target"
    tgt = new_object(tgt_name, None, coll)
    tgt.location = subj.matrix_world.translation + Vector((0, 0, subj.get("eye_height", 1.63) - 0.1))
    to_cam = cam.matrix_world.translation - tgt.location; to_cam.z = 0; to_cam.normalize()
    s = 1 if key_side == "left" else -1
    def at(az_deg, dist, h):
        v = Matrix.Rotation(math.radians(az_deg), 3, 'Z') @ to_cam
        return tgt.location + v * dist + Vector((0, 0, h))
    add_light("LGT_key", 'AREA', at(45 * s, 3.0, 1.6), key_w, key_k, coll, tgt, 1.0, motivation="window")
    add_light("LGT_fill", 'AREA', at(-50 * s, 3.5, 0.6), key_w / ratio, fill_k, coll, tgt, 2.0, motivation="bounce")
    add_light("LGT_rim", 'AREA', at(160 * -s, 2.5, 1.2), key_w * 0.75, rim_k, coll, tgt, 0.5, motivation="practical behind")
    return {"lights": ["LGT_key", "LGT_fill", "LGT_rim"], "ratio": ratio}


def _emission_override(name, build):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if mat.node_tree is None:              # pre-5.0 safety; in 5.x node_tree always exists
        mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    build(nt, out)
    return mat

def clay_material(grey=0.6):
    def b(nt, out):
        p = nt.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = (grey, grey, grey, 1)
        p.inputs['Roughness'].default_value = 0.85
        nt.links.new(p.outputs['BSDF'], out.inputs['Surface'])
    return _emission_override("MAT_afs_clay", b)

def depth_material(near, far):
    def b(nt, out):
        cd = nt.nodes.new('ShaderNodeCameraData')
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.clamp = True
        mr.inputs['From Min'].default_value = near   # float-mode inputs (first match)
        mr.inputs['From Max'].default_value = far
        mr.inputs['To Min'].default_value = 1.0      # near = white
        mr.inputs['To Max'].default_value = 0.0      # far  = black
        em = nt.nodes.new('ShaderNodeEmission')
        nt.links.new(cd.outputs['View Distance'], mr.inputs['Value'])
        nt.links.new(mr.outputs['Result'], em.inputs['Color'])
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return _emission_override("MAT_afs_depth", b)

def black_world():
    w = bpy.data.worlds.get("WRL_afs_black") or bpy.data.worlds.new("WRL_afs_black")
    nt = w.node_tree
    bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None) or nt.nodes.new('ShaderNodeBackground')
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_WORLD'), None) or nt.nodes.new('ShaderNodeOutputWorld')
    bg.inputs['Color'].default_value = (0, 0, 0, 1); bg.inputs['Strength'].default_value = 0.0
    if not bg.outputs['Background'].is_linked:
        nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    w.color = (0, 0, 0)
    return w

def set_pass(scene, mode, near=0.5, far=30.0):
    vl = scene.view_layers[0]
    vl.material_override = None
    vl.world_override = None                      # Blender 5.0+
    r = scene.render; r.film_transparent = False
    im = r.image_settings; im.color_depth = '8'
    sh = scene.display.shading
    if mode in ("clay", "seg"):
        r.engine = 'BLENDER_WORKBENCH'
        scene.display.render_aa = '8'
        sh.show_specular_highlight = False
        sh.show_object_outline = False             # outlines read as drawn lines
        sh.show_xray = False
        if mode == "clay":
            sh.light, sh.color_type = 'STUDIO', 'SINGLE'
            sh.single_color = (0.72, 0.72, 0.72)
            sh.show_cavity, sh.cavity_type = True, 'BOTH'
            sh.show_shadows, sh.shadow_intensity = True, 0.45
        else:
            sh.light, sh.color_type = 'FLAT', 'OBJECT'
            sh.show_cavity = False; sh.show_shadows = False
    elif mode in ("depth", "litclay"):
        r.engine = 'BLENDER_EEVEE'                 # 5.x id (4.2-4.5 was BLENDER_EEVEE_NEXT)
        scene.eevee.taa_render_samples = 16
        if mode == "depth":
            vl.material_override = depth_material(near, far)
            vl.world_override = black_world()
            im.color_depth = '16'                  # PNG master; mp4 preview is 8-bit
        else:
            vl.material_override = clay_material()
    else:
        raise ValueError(mode)
    return {"pass": mode, "engine": r.engine}


def check_shot(scene, shot, subject_id, f_in, f_out, samples=5):
    cam = bpy.data.objects[f"CAM_{shot['id']}"]
    root = bpy.data.objects[f"CHR_{subject_id}"]
    body = [c for c in root.children if c.type == 'MESH']
    res_x = scene.render.resolution_x
    hfov = 2 * math.atan(cam.data.sensor_width / 2 / cam.data.lens)
    max_deg_per_frame = math.degrees(hfov) / (7 * scene.render.fps)        # RED 7-second rule
    issues, rows, prev_fwd = [], [], None
    frames = sorted(set(round(f_in + i * (f_out - f_in) / (samples - 1)) for i in range(samples)))
    for f in range(f_in, f_out + 1):
        scene.frame_set(f)
        fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        if prev_fwd is not None:
            ang = math.degrees(prev_fwd.angle(fwd, 0.0))
            if ang > max_deg_per_frame * 1.5:
                issues.append(f"f{f}: camera rotates {ang:.2f} deg/frame > {max_deg_per_frame:.2f} (judder risk)")
        prev_fwd = fwd
        if f not in frames:
            continue
        dg = bpy.context.evaluated_depsgraph_get()
        pts = [ob.matrix_world @ Vector(c) for ob in body for c in ob.bound_box]
        ndc = [world_to_camera_view(scene, cam, p) for p in pts]
        top = max(p.y for p in ndc); bottom = min(p.y for p in ndc)
        eye_w = root.matrix_world @ Vector((0, 0, root.get("eye_height", 1.63)))
        eye = world_to_camera_view(scene, cam, eye_w)
        look = world_to_camera_view(scene, cam, eye_w + (root.matrix_world.to_quaternion() @ Vector((0, -0.5, 0))))
        # occlusion: ray from camera to eye
        o = cam.matrix_world.translation; v = eye_w - o
        hit, loc, nrm, idx, hob, _ = scene.ray_cast(dg, o, v.normalized(), distance=v.length)
        blocked = hit and hob is not None and hob.name not in {b.name for b in body}
        # camera inside any SET mesh bbox
        inside = []
        for ob in scene.objects:
            if ob.type != 'MESH' or ob in body:
                continue
            lp = ob.matrix_world.inverted() @ o
            bb = [Vector(c) for c in ob.bound_box]
            mn = Vector((min(c.x for c in bb), min(c.y for c in bb), min(c.z for c in bb)))
            mx = Vector((max(c.x for c in bb), max(c.y for c in bb), max(c.z for c in bb)))
            if all(mn[i] < lp[i] < mx[i] for i in range(3)):
                inside.append(ob.name)
        rows.append({"frame": f, "eye_xy": [round(eye.x, 3), round(eye.y, 3)],
                     "top_y": round(top, 3), "bottom_y": round(bottom, 3), "depth_m": round(eye.z, 2),
                     "blocked_by": hob.name if blocked else None, "cam_inside": inside})
        size = shot["size"]
        if eye.z <= 0: issues.append(f"f{f}: subject behind camera")
        if size in ("cu", "mcu", "ms", "cowboy", "mws") and not (0.82 <= top <= 0.98):
            issues.append(f"f{f}: headroom off (head top y={top:.2f}, want 0.82-0.98)")
        if size in ("cu", "mcu", "ms") and not (0.55 <= eye.y <= 0.78):
            issues.append(f"f{f}: eyeline y={eye.y:.2f} not near upper third")
        if size == "fs" and (bottom < 0.02 or top > 0.97):
            issues.append(f"f{f}: full shot crops feet/head")
        dx = look.x - eye.x
        if abs(dx) > 0.01 and shot.get("composition", {}).get("lead_room", "normal") == "normal":
            if (dx > 0 and eye.x > 0.55) or (dx < 0 and eye.x < 0.45):
                issues.append(f"f{f}: no lead room (looking {'right' if dx > 0 else 'left'} at x={eye.x:.2f})")
        if blocked: issues.append(f"f{f}: eyeline blocked by {hob.name}")
        if inside: issues.append(f"f{f}: camera inside {inside}")
    return {"shot": shot["id"], "ok": not issues, "issues": issues[:20], "samples": rows}


def clean_viewport_to_camera(scene):
    win = bpy.context.window_manager.windows[0]
    win.scene = scene
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    sp = area.spaces.active
    sp.overlay.show_overlays = False
    sp.show_gizmo = False
    sp.shading.type = 'SOLID'
    sp.region_3d.view_perspective = 'CAMERA'
    return win, area, next(r for r in area.regions if r.type == 'WINDOW')

def playblast(scene, filepath_noext):
    win, area, region = clean_viewport_to_camera(scene)
    scene.render.image_settings.media_type = 'IMAGE'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = filepath_noext + "_####"
    with bpy.context.temp_override(window=win, area=area, region=region, scene=scene):
        bpy.ops.render.opengl(animation=True, view_context=True)
    return {"written": filepath_noext}


def out_base(root_dir, unit_id, pas, ver):
    d = os.path.join(root_dir, unit_id, f"v{ver:03d}")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{PROJECT}_{unit_id}_{pas}_v{ver:03d}")

def render_still(scene, frame, path_noext):
    im = scene.render.image_settings
    im.media_type, im.file_format, im.color_mode = 'IMAGE', 'PNG', 'RGB'
    scene.frame_set(frame)
    scene.render.filepath = path_noext
    bpy.ops.render.render(write_still=True, scene=scene.name)
    return {"still": path_noext + ".png", "frame": frame}

def render_sequence_chunk(scene, base, f0, f1):
    """Call repeatedly (e.g. 48 frames per MCP call) to avoid timeouts."""
    im = scene.render.image_settings
    im.media_type, im.file_format, im.color_mode = 'IMAGE', 'PNG', 'RGB'
    scene.render.filepath = base + "_####"
    scene.render.use_overwrite = False            # resumable
    bpy.ops.render.render(animation=True, scene=scene.name, frame_start=f0, frame_end=f1)
    return {"chunk": [f0, f1]}

def set_video_output(scene, base):
    """Native mp4. [UNSURE-5.x] enum ids carried from 4.x; verify via bl_rna if it throws."""
    im = scene.render.image_settings
    im.media_type = 'VIDEO'                        # 5.x
    im.file_format = 'FFMPEG'
    ff = scene.render.ffmpeg
    ff.format, ff.codec = 'MPEG4', 'H264'
    ff.constant_rate_factor = 'HIGH'
    ff.ffmpeg_preset = 'GOOD'
    ff.gopsize = scene.render.fps
    ff.audio_codec = 'NONE'
    im.color_mode = 'RGB'
    scene.render.filepath = base                   # Blender appends frame range (e.g. _0001-0420.mp4): rename after render, or prefer encode_png_sequence()
    return {"video": base}


from bpy_extras import anim_utils

def bake_object(ob, scene):
    """Bakes constraints/parents to plain keys. Run on a COPY for export; keep live rig."""
    opts = anim_utils.BakeOptions(only_selected=False, do_pose=False, do_object=True,
        do_visual_keying=True, do_constraint_clear=True, do_parents_clear=True, do_clean=False,
        do_location=True, do_rotation=True, do_scale=False, do_bbone=False, do_custom_props=False)
    act = anim_utils.bake_action(ob, action=None,
                                 frames=range(scene.frame_start, scene.frame_end + 1), bake_options=opts)
    if act and (ob.animation_data is None or ob.animation_data.action is not act):
        ob.animation_data_create(); ob.animation_data.action = act
    return {"baked": ob.name, "action": act.name if act else None}

def export_camera_json(scene, cam, path):
    data = {"fps": scene.render.fps, "sensor_mm": cam.data.sensor_width, "frames": []}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        m = cam.matrix_world
        data["frames"].append({"f": f, "loc": [round(x, 4) for x in m.translation],
            "quat": [round(x, 5) for x in m.to_quaternion()], "lens": cam.data.lens,
            "focus_m": cam.data.dof.focus_distance})
    with open(path, "w") as fh:
        json.dump(data, fh)
    return {"camera_json": path, "frames": len(data["frames"])}


def save_version(dir_, scene_id):
    os.makedirs(dir_, exist_ok=True)
    pat = re.compile(rf"{PROJECT}_{scene_id}_previs_v(\d{{3}})\.blend$")
    vers = [int(m.group(1)) for f in os.listdir(dir_) if (m := pat.match(f))]
    ver = max(vers, default=0) + 1
    path = os.path.join(dir_, f"{PROJECT}_{scene_id}_previs_v{ver:03d}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)   # copy=True: working file unchanged
    return {"saved": path, "version": ver}



# ---- Usage pattern (one MCP execute_blender_code call per step) ----
# # call 1
# import sys, importlib; sys.path.insert(0, "<PLUGIN_ROOT>/skills/blender-previs/scripts")
# import afs_previs_lib as afs; importlib.reload(afs)
# result = afs.setup_unit_scene(unit, shots)          # unit/shots json.loads from shotlist
# # call 2
# result = afs.add_human_proxy("C01", 1.72, (0, 0, 0), 0, (0.85, 0.15, 0.1, 1))
# # call 3
# result = afs.create_shot_camera(shots[1], "C01", azimuth_deg=20)
# # call 4
# result = afs.animate_move(shots[1], 1001 + 60, 1001 + 215)
# # call 5
# result = afs.check_shot(bpy.context.scene, shots[1], "C01", 1061, 1215)
# # then: get_screenshot_of_area_as_image("VIEW_3D", 200000)


def encode_png_sequence(seq_pattern, out_mp4, fps=24, crf=16, start_number=1001):
    """Return the ffmpeg command (run it on the machine that holds the frames, outside Blender).
    seq_pattern like '/path/AFS_U01_clay_v003_%04d.png'. Output follows knowledge.md section 7.2."""
    return (f'ffmpeg -y -framerate {fps} -start_number {start_number} -i "{seq_pattern}" '
            f'-c:v libx264 -profile:v high -pix_fmt yuv420p -crf {crf} -g {fps} -an -movflags +faststart "{out_mp4}"')
