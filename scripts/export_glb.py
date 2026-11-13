"""Stage 8: export GLB packages for Unreal / other DCCs.
  Blender -b project-files/camellia-farmhouse.blend -P scripts/export_glb.py
Writes project-files/export/*.glb (+Y up, metres, materials and textures embedded)."""
import os
import bpy

ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
OUT = os.path.join(ROOT, "project-files", "export")
os.makedirs(OUT, exist_ok=True)
GROUPS = {
    "camellia_structure": ["COL-structure", "COL-shell", "COL-floors", "COL-openings", "COL-cladding"],
    "camellia_millwork": ["COL-millwork"],
    "camellia_exterior": ["COL-exterior", "COL-site"],
    "camellia_cameras_lights": ["COL-cameras", "COL-lights"],
    "camellia_landscape": ["COL-landscape"],        # 14 instances of one Poly Haven tree (shared mesh)
}
fcol = bpy.data.collections.get("COL-furniture")
if fcol:
    for c in fcol.children:
        GROUPS["camellia_" + c.name.replace("COL-", "")] = [c.name]


def objs(cname):
    c = bpy.data.collections.get(cname)
    return list(c.all_objects) if c else []


vl = bpy.context.view_layer
# bake the walkthrough camera (path + track-to constraints) to plain keyframes so the GLB carries the move.
# This runs in the background session only; the saved .blend keeps the live constraints.
try:
    for o in vl.objects:
        o.select_set(False)
    walk = bpy.data.objects["CAM-walkthrough"]
    walk.select_set(True)
    vl.objects.active = walk
    bpy.context.scene.frame_set(1)
    bpy.ops.nla.bake(frame_start=1, frame_end=1080, step=4, only_selected=True, visual_keying=True,
                     clear_constraints=True, bake_types={"OBJECT"})
    print("BAKED walkthrough camera")
except Exception as e:
    print("BAKE FAILED", e)
for name, cols in GROUPS.items():
    for o in vl.objects:
        o.select_set(False)
    n = 0
    for cn in cols:
        for o in objs(cn):
            if o.name in vl.objects:
                o.hide_set(False)
                o.select_set(True)
                n += 1
    if n == 0:
        print("SKIP", name)
        continue
    path = os.path.join(OUT, name + ".glb")
    kw = dict(filepath=path, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
              export_cameras="cameras" in name, export_lights="lights" in name,
              export_animations="cameras" in name)
    try:
        bpy.ops.export_scene.gltf(**kw)
        print(f"EXPORTED {name}: {n} objects, {os.path.getsize(path) / 1e6:.1f} MB")
    except Exception as e:
        print("EXPORT FAILED", name, e)
