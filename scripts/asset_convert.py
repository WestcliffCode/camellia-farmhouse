"""Step 2 of bringing in a manufacturer model: turn the raw import into a clean library file.

  Blender -b assets_incoming/_converted/<slot>_raw.blend -P scripts/asset_convert.py -- <slot>

Manufacturer OBJ files come with no usable materials (one grey, or none), so each slot has rules below that sort its
parts into materials by name or by size and position. Parts are then joined per material, the model is turned so its
front faces -Y (the project convention for placed assets) and set on z = 0, and the result is saved as
assets_incoming/_converted/<slot>.blend holding one collection, ASSET-<slot>.
All materials are single Principled BSDFs with plain values, so they export.
"""
import bpy, math, os, sys
from mathutils import Matrix, Vector

slot = sys.argv[sys.argv.index("--") + 1]
ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
OUT = os.path.join(ROOT, "assets_incoming/_converted")


def mat(name, color, rough, metal=0.0, transmission=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
        b.inputs["IOR"].default_value = ior
    m.diffuse_color = (*color, 1.0)
    return m


M = {
    "steel": mat("MAT-app_stainless", (0.62, 0.63, 0.64), 0.27, metal=1.0),
    "iron": mat("MAT-app_cast_iron", (0.008, 0.008, 0.009), 0.72),      # matte black enamelled cast iron
    "dark": mat("MAT-app_black", (0.02, 0.02, 0.022), 0.35),
    "glass": mat("MAT-app_glass", (1.0, 1.0, 1.0), 0.0, transmission=1.0),
    "glass_tint": mat("MAT-app_glass_tint", (0.30, 0.31, 0.32), 0.0, transmission=1.0),
    "liner": mat("MAT-app_liner", (0.72, 0.73, 0.74), 0.32, metal=0.85),
    "bin": mat("MAT-app_bin_clear", (0.92, 0.95, 0.96), 0.12, transmission=0.9),
}
obs = [o for o in bpy.data.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
LO = Vector((min(p[i] for p in pts) for i in range(3)))
HI = Vector((max(p[i] for p in pts) for i in range(3)))


def box(o):
    ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p[i] for p in ps) for i in range(3)))
    hi = Vector((max(p[i] for p in ps) for i in range(3)))
    return lo, hi, hi - lo


def rule_range(o):
    """Viking 48 in range, Rhino export: front faces +X, 753 unnamed solids. Sorted by where they are."""
    lo, hi, s = box(o)
    z = lo.z - LO.z                                    # height above the floor
    if s.x < 0.012 and s.y > 0.25 and 0.20 < s.z < 0.28 and lo.x > 0.24 and 0.30 < z < 0.36:
        return "glass_tint" if lo.x > 0.285 else "glass"            # oven door panes: the outer one is tinted
    if z > 0.868 and hi.x < 0.26:
        return "iron"                                  # grates, burner caps and heads sit above the cooktop pan
    return "steel"


FRIDGE = {"Object013": "glass", "Object014": "glass", "Object015": "glass", "Object017": "glass",
          "Box006": "bin", "Box007": "bin", "Box005": "liner", "Object016": "liner", "Object009": "dark",
          "Box004": "dark", "Object012": "dark", "Object011": "dark", "Line007": "dark"}


def rule_fridge(o):
    """Sub-Zero PRO 36 in glass-door refrigerator, 3ds Max export: 24 named parts, front faces -Y."""
    return FRIDGE.get(o.name.split(".")[0] if o.name.count(".") and o.name.split(".")[-1].isdigit() else o.name, "steel")


RULES = {"range_kitchen": (rule_range, -90.0), "fridge_kitchen": (rule_fridge, 0.0)}     # rule, turn about Z to face -Y
# CAD exports are tessellated far more finely than a render needs and carry every internal part. For slots listed
# here: parts that cannot be seen from the front, the top or the front quarters are dropped, and the rest are welded
# and reduced. `front` is the raw model's front direction.
REDUCE = {"range_kitchen": {"front": Vector((1, 0, 0))}}
rule, turn = RULES[slot]
kind = {o.name: rule(o) for o in obs}
report = {"faces_in": sum(len(o.data.polygons) for o in obs), "parts_in": len(obs)}


def seen_parts(front):
    """Names of parts hit first by any ray from 29 viewpoints in front of and above the model (glass counts as clear)."""
    scene = bpy.context.scene
    for o in obs:
        o.hide_viewport = "glass" in kind[o.name]
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    c, rad = (LO + HI) / 2, (HI - LO).length / 2
    side = Vector((0, 0, 1)).cross(front).normalized()
    seen = set()
    views = [(az, el) for az in (-75, -50, -25, 0, 25, 50, 75) for el in (5, 25, 45, 65)] + [(0, 86)]
    step = 0.004
    n = int(2 * rad / step)
    for az, el in views:
        a, e = math.radians(az), math.radians(el)
        d = -((front * math.cos(a) + side * math.sin(a)) * math.cos(e) + Vector((0, 0, 1)) * math.sin(e))   # ray direction
        right = d.cross(Vector((0, 0, 1))).normalized() if abs(d.z) < 0.99 else side
        up = right.cross(d).normalized()
        o0 = c - d * (rad * 3)
        for i in range(n):
            for j in range(n):
                p = o0 + right * ((i + 0.5) * step - rad) + up * ((j + 0.5) * step - rad)
                ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, p, d, distance=rad * 6)
                if ok:
                    seen.add(ob.name)
    for o in obs:
        o.hide_viewport = False
    bpy.context.view_layer.update()
    return seen


def reduce_part(o):
    """Weld the part's patches together, collapse it (flat areas go first), and reset its shading to smooth with
    sharp edges at 35 degrees. The finer the original tessellation, the harder it is reduced."""
    import bmesh
    me = o.data
    n0 = len(me.polygons)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-5)
    bm.to_mesh(me)
    bm.free()
    ca = me.attributes.get("custom_normal")
    if ca is not None:
        me.attributes.remove(ca)
    if n0 >= 300:
        md = o.modifiers.new("reduce", "DECIMATE")
        md.decimate_type = "COLLAPSE"
        md.ratio = 0.2 if n0 > 8000 else 0.28 if n0 > 3000 else 0.38 if n0 > 1000 else 0.5
        dg = bpy.context.evaluated_depsgraph_get()
        new = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        o.modifiers.clear()
        o.data = new
        me = new
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try:
        me.set_sharp_from_angle(angle=math.radians(35))
    except AttributeError:
        pass
    me.update()
    # face-area-weighted normals keep flat panels flat next to small fillets, which is what stops reduced CAD meshes
    # from showing wavy reflections
    wn = o.modifiers.new("weighted", "WEIGHTED_NORMAL")
    wn.keep_sharp, wn.weight, wn.mode = True, 100, "FACE_AREA"
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    o.modifiers.clear()
    o.data = new


if slot in REDUCE:
    import json
    cache = os.path.join(OUT, slot + "_seen.json")          # the visibility pass takes minutes; keep its answer
    if os.path.exists(cache):
        seen = set(json.load(open(cache)))
    else:
        seen = seen_parts(REDUCE[slot]["front"])
        json.dump(sorted(seen), open(cache, "w"))
    hidden = [o for o in obs if o.name not in seen and len(o.data.polygons) >= 200 and "glass" not in kind[o.name]]
    report["hidden_parts"] = len(hidden)
    report["hidden_faces"] = sum(len(o.data.polygons) for o in hidden)
    for o in hidden:
        obs.remove(o)
        bpy.data.objects.remove(o)
    for o in obs:
        if "glass" not in kind[o.name]:
            reduce_part(o)
    report["faces_out"] = sum(len(o.data.polygons) for o in obs)
groups = {}
for o in obs:
    groups.setdefault(kind[o.name], []).append(o)
# Low-polygon shells arrive with normals smoothed across their corners, which renders as blobby highlights on flat
# panels. Rebuild those parts from bare vertices and faces so they shade flat.
for o in obs:
    if slot not in REDUCE and len(o.data.polygons) < 300:
        me = o.data
        flat = bpy.data.meshes.new(me.name + "_flat")
        flat.from_pydata([v.co[:] for v in me.vertices], [], [p.vertices[:] for p in me.polygons])
        flat.update()
        o.data = flat
col = bpy.data.collections.new("ASSET-" + slot)
bpy.context.scene.collection.children.link(col)
R = Matrix.Rotation(math.radians(turn), 4, "Z")
out = []
for key, members in groups.items():
    faces = sum(len(o.data.polygons) for o in members)
    for o in members:
        o.data.materials.clear()
        o.data.materials.append(M[key])
    a = members[0]
    if len(members) > 1:
        with bpy.context.temp_override(active_object=a, selected_editable_objects=members, selected_objects=members):
            bpy.ops.object.join()
    a.name = f"GEO-{slot}_{key}"
    a.data.name = a.name
    a.data.transform(R @ a.matrix_world)               # bake placement and the turn into the mesh
    a.matrix_world = Matrix.Identity(4)
    for c in list(a.users_collection):
        c.objects.unlink(a)
    col.objects.link(a)
    if "glass" in key or key == "bin":
        a.visible_shadow = False                       # project convention: light passes through glass
    out.append((key, len(members), faces))
# back-centre of the footprint to the origin, floor to z = 0
ps = [Vector(v.co) for o in col.objects for v in o.data.vertices]
lo = Vector((min(p[i] for p in ps) for i in range(3)))
hi = Vector((max(p[i] for p in ps) for i in range(3)))
T = Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -hi.y, -lo.z)))
for o in col.objects:
    o.data.transform(T)
    o.data.update()
for o in [o for o in bpy.data.objects if o.name not in col.objects]:
    bpy.data.objects.remove(o)
for m in [m for m in bpy.data.materials if m.users == 0]:
    bpy.data.materials.remove(m)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, slot + ".blend"))
print("CONVERTED", slot, "size", [round(hi[i] - lo[i], 3) for i in range(3)], "groups", out, "report", report)
