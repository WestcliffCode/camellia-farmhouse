"""Camera rig check -> output/camera_rig_check.md
  Blender -b project-files/camellia-farmhouse.blend -P scripts/check_camera_rig.py

Still cameras: each has a marker that binds it to its own frame, sits in open air (not inside geometry, at least
0.15 m from the nearest surface), and its centre ray lands on something at a sensible distance.
Walkthrough: the camera object, its Follow Path and Track To constraints and their targets exist; evaluated at every
frame 1..1080 the camera stays inside the house footprint, never comes closer than 0.25 m to a surface, never jumps,
and no straight segment between consecutive positions crosses geometry (it never passes through a wall or a door leaf).
"""
import bpy, math, os
from mathutils import Vector
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

scene = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
frame0 = scene.frame_current
DIRS = [Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        for e in (-0.9, -0.45, 0.0, 0.45, 0.9) for a in [i * math.pi / 8 for i in range(16)]] + [Vector((0, 0, 1)), Vector((0, 0, -1))]


def clearance(p):
    best = 99.0
    for d in DIRS:
        ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, p, d, distance=5.0)
        if ok:
            best = min(best, (loc - p).length)
    return best


out = ["# Camera rig check", ""]
problems = []
marker_of = {m.camera.name: m.frame for m in scene.timeline_markers if m.camera}
stills = sorted((o for o in bpy.data.objects if o.type == "CAMERA" and o.name != "CAM-walkthrough"), key=lambda o: o.name)
out += [f"## Still cameras ({len(stills)})", "", "| Camera | type | lens | marker frame | clearance m | centre ray hits | at m |", "|---|---|---|---|---|---|---|"]
for cam in stills:
    p = cam.matrix_world.translation.copy()
    fwd = (cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
    cl = clearance(p)
    ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, p, fwd, distance=400.0)
    fr = marker_of.get(cam.name)
    ortho = cam.data.type == "ORTHO"
    lens = f"ortho {cam.data.ortho_scale:.1f} m" if ortho else f"{cam.data.lens:.0f} mm"
    out.append(f"| {cam.name} | {'ortho' if ortho else 'persp'} | {lens} | {fr if fr is not None else '-'} | {cl:.2f} | {ob.name[:28] if ok else 'sky'} | {(loc - p).length:.1f} |" if ok
               else f"| {cam.name} | {'ortho' if ortho else 'persp'} | {lens} | {fr if fr is not None else '-'} | {cl:.2f} | sky | - |")
    if fr is None:
        problems.append(f"{cam.name}: no marker binds it to a frame")
    if cl < 0.15:
        problems.append(f"{cam.name}: only {cl:.2f} m from a surface")
    if not ok:
        problems.append(f"{cam.name}: centre ray hits nothing")
frames = [f for f in marker_of.values()]
if len(frames) != len(set(frames)):
    problems.append("two cameras share a marker frame")

# walkthrough
walk = bpy.data.objects.get("CAM-walkthrough")
out += ["", "## Walkthrough", ""]
if walk is None:
    problems.append("CAM-walkthrough is missing")
else:
    cons = {c.type: c for c in walk.constraints}
    fp, tt = cons.get("FOLLOW_PATH"), cons.get("TRACK_TO")
    out.append(f"- Camera `CAM-walkthrough`, lens {walk.data.lens:.0f} mm; constraints: {', '.join(c.type for c in walk.constraints)}.")
    if fp is None or fp.target is None:
        problems.append("walkthrough: Follow Path constraint or its curve is missing")
    else:
        out.append(f"- Follow Path target `{fp.target.name}` (curve with {sum(len(s.bezier_points) + len(s.points) for s in fp.target.data.splines)} control points).")
    if tt is None or tt.target is None:
        problems.append("walkthrough: Track To constraint or its aim target is missing")
    else:
        out.append(f"- Track To target `{tt.target.name}`.")
    F0, F1 = 1, 1080
    prev = None
    min_cl, min_cl_f, max_step, max_step_f, outside, crossings, max_turn = 99.0, 0, 0.0, 0, 0, [], 0.0
    prev_fwd = None
    length = 0.0
    zs = []
    for f in range(F0, F1 + 1):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        mw = walk.evaluated_get(dg).matrix_world
        p = mw.translation.copy()
        fwd = (mw.to_quaternion() @ Vector((0, 0, -1))).normalized()
        zs.append(p.z)
        if not in_footprint((p.x, p.y)):
            outside += 1
        if f % 4 == 1:
            cl = clearance(p)
            if cl < min_cl:
                min_cl, min_cl_f = cl, f
        if prev is not None:
            seg = p - prev
            length += seg.length
            if seg.length > max_step:
                max_step, max_step_f = seg.length, f
            if seg.length > 1e-5:
                ok, loc, nor, idx, ob, _ = scene.ray_cast(dg, prev, seg.normalized(), distance=seg.length)
                if ok:
                    crossings.append((f, ob.name))
            turn = math.degrees(prev_fwd.angle(fwd))
            max_turn = max(max_turn, turn)
        prev, prev_fwd = p, fwd
    scene.frame_set(frame0)
    out += [f"- Frames {F0}-{F1} at {scene.render.fps} fps ({(F1 - F0 + 1) / scene.render.fps:.0f} s); path length travelled {length:.1f} m; eye height {min(zs):.2f}-{max(zs):.2f} m.",
            f"- Frames with the camera outside the house footprint: {outside}.",
            f"- Smallest distance to any surface: {min_cl:.2f} m (frame {min_cl_f}; sampled every 4th frame, 82 directions).",
            f"- Largest move between consecutive frames: {max_step * 100:.1f} cm (frame {max_step_f}); largest turn between consecutive frames: {max_turn:.2f} degrees.",
            f"- Segments between consecutive positions that cross geometry: {len(crossings)}{' ' + str(crossings[:5]) if crossings else ''}."]
    if outside:
        problems.append(f"walkthrough leaves the footprint on {outside} frames")
    if min_cl < 0.25:
        problems.append(f"walkthrough comes within {min_cl:.2f} m of a surface at frame {min_cl_f}")
    if crossings:
        problems.append(f"walkthrough passes through geometry at {len(crossings)} frames")
    if max_step > 0.15:
        problems.append(f"walkthrough jumps {max_step:.2f} m at frame {max_step_f}")
out += ["", "## Result", "", ("No problems found." if not problems else "Problems:")] + [f"- {p}" for p in problems]
open(os.path.join(ROOT, "output/camera_rig_check.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out[-14:]))
print("PROBLEMS", len(problems))
