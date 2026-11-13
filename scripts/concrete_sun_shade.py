"""Where, in the exterior renders, is the same material in sun and in shade?

  Blender -b project-files/camellia-farmhouse.blend -P scripts/concrete_sun_shade.py

For each exterior camera a 160 x 90 grid of camera rays is cast. Pixels whose first hit is MAT-concrete (paving, porch
slabs, driveway: one neutral grey material) are split into sunlit (surface turned to the sun and a clear line to it)
and shade (everything else). The pixel lists go to output/renders/lighting_reference/concrete_pixels.json;
scripts/lighting_reference_board.py reads the colours at those pixels out of the final renders.
"""
import bpy, json, os
from mathutils import Vector

ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
CAMS = ["ext_front", "ext_front_left", "ext_garage", "ext_back"]
MAT = "MAT-concrete"
NX, NY = 160, 90
scene = bpy.context.scene
for m in list(scene.timeline_markers):
    m.camera = None
dg = bpy.context.evaluated_depsgraph_get()
sun = bpy.data.objects["LGT-sun"]
to_sun = (sun.matrix_world.to_quaternion() @ Vector((0, 0, 1))).normalized()


def mat_at(ob, idx):
    try:
        me = ob.evaluated_get(dg).data
        m = me.materials[me.polygons[idx].material_index]
        return m.name if m else ""
    except Exception:
        return ""


def clear_to_sun(p):
    ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, p, to_sun, distance=500)
    n = 0
    while ok and "glass" in mat_at(ob, idx).lower() and n < 6:
        ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, loc + to_sun * 0.02, to_sun, distance=500)
        n += 1
    return not ok


res = {}
for name in CAMS:
    cam = bpy.data.objects["CAM-" + name]
    mw = cam.matrix_world
    tr, br, bl, tl = [mw @ v for v in cam.data.view_frame(scene=scene)]
    o = mw.translation
    sunlit, shade = [], []
    for j in range(NY):
        for i in range(NX):
            u, v = (i + 0.5) / NX, (j + 0.5) / NY                    # v from the top
            target = tl + (tr - tl) * u + (bl - tl) * v
            d = (target - o).normalized()
            ok, loc, nor, idx, ob, _ = scene.ray_cast(dg, o, d, distance=500)
            if not ok or mat_at(ob, idx) != MAT:
                continue
            lit = nor.dot(to_sun) > 0.02 and clear_to_sun(loc + nor * 0.01)
            (sunlit if lit else shade).append((round(u, 4), round(v, 4)))
    res[name] = {"sunlit": sunlit, "shade": shade}
    print(name, "concrete pixels sunlit", len(sunlit), "shade", len(shade))
out = os.path.join(ROOT, "output/renders/lighting_reference/concrete_pixels.json")
json.dump(res, open(out, "w"))
print("wrote", out)
