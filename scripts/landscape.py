"""Landscape: instances of the Poly Haven tree `tree_small_02` around the lot. Owns COL-landscape."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/furnish_lib.py").read())

wipe_col("COL-landscape")
col = get_col("COL-landscape")
TREE = "tree_small_02_LOD0"
src = get_col("COL-assets_src")
tc = bpy.data.collections.get(TREE)
if tc is not None:
    if tc.name in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.unlink(tc)
    if tc.name not in src.children:
        src.children.link(tc)
lc = _layer_col("COL-assets_src")
if lc:
    lc.exclude = True
# (x, y, scale, facing angle in degrees)
TREES = [(-7.0, -8.5, 2.1, 20), (1.5, -10.5, 1.6, 140), (-12.0, 4.0, 2.4, 250), (25.5, -9.5, 1.9, 70),
         (42.5, -8.0, 2.3, 300), (44.0, 12.0, 2.0, 190), (-10.0, 22.0, 2.2, 95), (-4.0, 38.0, 2.5, 10),
         (9.0, 46.0, 2.3, 220), (27.0, 44.0, 2.6, 160), (40.0, 30.0, 2.2, 330), (-22.0, -6.0, 2.6, 45),
         (58.0, 2.0, 2.7, 280), (-26.0, 30.0, 2.8, 120)]
n = 0
for x, y, sc, ang in TREES:
    a = math.radians(ang)
    e = place(TREE, x, y, z=-0.17, facing=(math.cos(a), math.sin(a)), col=col, scale=sc)
    n += 1 if e else 0
print("trees", n)
