"""Place converted manufacturer models in the scene (run inside Blender, after millwork, furnish_rooms and lighting).

For every slot in scripts/asset_overrides.json whose library exists in assets_incoming/_converted/, the collection
ASSET-<slot> is linked (not appended, so the models stay out of the scene file), parked in COL-assets_src and instanced at the slot's position (an INST- empty in the room's
furniture collection, like the Poly Haven pieces). millwork.py leaves the modeled version out for the same slots.
Re-runnable: earlier instances and library data for the slot are removed first.
"""
import bpy, json, math, os
from mathutils import Vector
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/furnish_lib.py").read().split("\ndef furnish_materials")[0])

CONV = os.path.join(ROOT, "assets_incoming/_converted")
OV = json.load(open(os.path.join(ROOT, "scripts/asset_overrides.json")))
FRAMES = {"kitchen_wall": (Frame(PX(1207, 1260), (1, 1)), "COL-furn_kitchen")}     # the range wall frame from millwork.py
src = get_col("COL-assets_src")
placed = {}
for slot, cfg in OV.items():
    lib = os.path.join(CONV, slot + ".blend")
    if not os.path.exists(lib):
        print("no library for", slot, "- the modeled version stays")
        continue
    name = "ASSET-" + slot
    for o in [o for o in bpy.data.objects if o.instance_collection and o.instance_collection.name == name]:
        bpy.data.objects.remove(o)
    for old in [c for c in bpy.data.collections if c.name == name and c.library is None]:     # an earlier appended copy
        for o in list(old.objects):
            me = o.data
            bpy.data.objects.remove(o)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        bpy.data.collections.remove(old)
    c = next((c for c in bpy.data.collections if c.name == name and c.library is not None), None)
    if c is not None:
        c.library.reload()
        c = next(c for c in bpy.data.collections if c.name == name and c.library is not None)
    else:
        # linked, not appended: manufacturer and purchased models stay in the git-ignored assets_incoming folder and
        # the scene file only refers to them, so they never reach the public repository
        with bpy.data.libraries.load(lib, link=True, relative=True) as (a, b):
            b.collections = [name]
        c = b.collections[0]
    if c.name not in [k.name for k in src.children if k.library is not None]:
        src.children.link(c)
    F, room_col = FRAMES[cfg["frame"]]
    lo, hi = _col_bbox(c)
    depth = hi.y - lo.y
    x, y = F.xy(cfg["s"], cfg["d_back"] + depth / 2)
    front = (F.n.x, F.n.y)
    e = place(name, x, y, z=0.0, facing=front, col=bpy.data.collections[room_col], name="INST-" + name)
    e.instance_collection = c                          # place() looks collections up by name; make sure it is the linked one
    placed[slot] = (F, cfg, depth, hi.z - lo.z, e)
    print("placed", slot, "size", [round(hi[i] - lo[i], 3) for i in range(3)], "faces", sum(len(o.data.polygons) for o in c.objects))

# one copy of each appliance material, whichever library it came from
for m in list(bpy.data.materials):
    base = m.name.rsplit(".", 1)[0]
    if m.library is None and m.name != base and base.startswith("MAT-app_") and base in bpy.data.materials:
        m.user_remap(bpy.data.materials[base])
        bpy.data.materials.remove(m)

if "range_kitchen" in placed:
    # the brass pots move onto the new range's grates: rear-left and front-right burners
    F, cfg, depth, top, e = placed["range_kitchen"]
    C = bpy.data.collections["COL-furn_kitchen"]
    for o in [o for o in C.objects if o.instance_collection and o.instance_collection.name in ("brass_pot_01", "brass_pot_02")]:
        bpy.data.objects.remove(o)
    for asset, ds, dd in (("brass_pot_01", -0.443, 0.183), ("brass_pot_02", 0.147, 0.474)):
        x, y = F.xy(cfg["s"] + ds, cfg["d_back"] + dd)
        place(asset, x, y, z=top, facing=(1, -1), col=C)

if "fridge_kitchen" in placed:
    # the glass door shows the interior, so it gets the refrigerator's own light
    F, cfg, depth, top, e = placed["fridge_kitchen"]
    old = bpy.data.objects.get("LGT-app_fridge")
    if old is not None:
        bpy.data.objects.remove(old)
    ld = bpy.data.lights.new("LGT-app_fridge", "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = 6.0, (1.0, 0.97, 0.92), 0.05
    lo_ = bpy.data.objects.new("LGT-app_fridge", ld)
    lo_.location = (*F.xy(cfg["s"], cfg["d_back"] + depth * 0.55), 1.72)
    get_col("COL-lights").objects.link(lo_)
print("assets placed:", sorted(placed))
