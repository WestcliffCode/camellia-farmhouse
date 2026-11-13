"""Step 1 of bringing in a manufacturer model: import the OBJ into an empty file at real-world scale and describe it.

  Blender -b --factory-startup -P scripts/asset_import_raw.py -- <slot> <obj path> <scale to metres> <up axis> <forward axis>

Writes assets_incoming/_converted/<slot>_raw.blend (the parts as imported, Z up, metres) and <slot>_parts.json
(one row per part: name, bounding box, face count, source material), which is what the per-slot conversion rules
in scripts/asset_convert.py are written against.
"""
import bpy, json, os, sys
from mathutils import Vector

slot, path, scale, up, fwd = sys.argv[sys.argv.index("--") + 1:][:5]
ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
OUT = os.path.join(ROOT, "assets_incoming/_converted")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=path, global_scale=float(scale), up_axis=up, forward_axis=fwd,
                      use_split_groups=True, use_split_objects=True)      # CAD exports name their parts with "g" lines
bpy.context.view_layer.update()
parts = []
lo_all, hi_all = Vector((1e9,) * 3), Vector((-1e9,) * 3)
for ob in bpy.data.objects:
    if ob.type != "MESH":
        continue
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    lo_all = Vector((min(lo_all[i], lo[i]) for i in range(3)))
    hi_all = Vector((max(hi_all[i], hi[i]) for i in range(3)))
    parts.append({"name": ob.name, "lo": [round(v, 4) for v in lo], "hi": [round(v, 4) for v in hi],
                  "faces": len(ob.data.polygons), "mats": [m.name for m in ob.data.materials if m]})
json.dump({"lo": list(lo_all), "hi": list(hi_all), "parts": parts}, open(os.path.join(OUT, slot + "_parts.json"), "w"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, slot + "_raw.blend"))
print("IMPORTED", slot, "parts", len(parts), "faces", sum(p["faces"] for p in parts),
      "size m", [round(hi_all[i] - lo_all[i], 3) for i in range(3)], "lo", [round(v, 3) for v in lo_all])
