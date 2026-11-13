"""Stage 2a: walls, lintels, sills, floor slab and flat ceilings from structure.json."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

# default startup objects are not part of the house
for nm in ("Cube", "Light", "Camera"):
    ob = bpy.data.objects.get(nm)
    if ob is not None and ob.users_collection and ob.users_collection[0].name == "Collection":
        bpy.data.objects.remove(ob, do_unlink=True)

wipe_col("COL-structure")
col = get_col("COL-structure")

# rooms with ceilings that are not a flat 10 ft plane (built in a later script)
SPECIAL_CEIL = {"foyer", "primary_suite", "game_room", "portico", "garage", "stair"}

# ---- walls
bm = bmesh.new()
for w in S["walls"]:
    add_prism(bm, w["outer"], w["holes"], 0.0, CEIL)
for o in S["openings"]:
    if o["type"] == "portal":
        continue
    half_w = o["w"] / 2 + 0.002
    half_t = o["t"] / 2
    if o.get("arch"):
        sp = arch_spring(o)
        add_profile(bm, o["c"], o["u"], half_t, arch_profile(o["w"] + 0.004, sp, o["head"], CEIL))
    elif o["head"] < CEIL - 0.01:
        add_box(bm, o["c"], o["u"], half_w, half_t, o["head"], CEIL)
    if o["sill"] > 0.01:
        add_box(bm, o["c"], o["u"], half_w, half_t, 0.0, o["sill"])
walls = new_obj("GEO-walls", bm, col)
fix_normals(walls)

# ---- floor slab (finished floor top at z = 0)
bm = bmesh.new()
for f in S["footprint"]:
    add_prism(bm, f["outer"], f["holes"], -0.30, 0.0)
slab = new_obj("GEO-slab", bm, col)

# ---- flat ceilings, one object per room
ccol = get_col("COL-ceilings", col)
for r in S["rooms"]:
    if r["name"] in SPECIAL_CEIL:
        continue
    bm = bmesh.new()
    add_prism(bm, r["outer"], r["holes"], CEIL, CEIL + 0.02)
    new_obj("GEO-ceiling_" + r["name"], bm, ccol)

print("walls verts", len(walls.data.vertices), "faces", len(walls.data.polygons))
print("dims", [round(v, 2) for v in walls.dimensions])
print("ceilings", len(ccol.objects))
