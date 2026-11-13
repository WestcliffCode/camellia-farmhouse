"""Stage 3a: material library, world-scale UVs and material assignment for the architecture.

Poly Haven sets must already be imported (see DESIGN_SYSTEM.md for ids). Re-runnable.
"""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

print("externalized images:", externalize_images())


# ------------------------------------------------------------------ material library
# Every material is a single Principled BSDF fed by image textures or plain values, so glTF/FBX export keeps it.
def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def solid(name, color, rough=0.5, metal=0.0, bump=0.0, bump_scale=60.0, **extra):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    set_in(b, "Base Color", (*color, 1.0))
    set_in(b, "Roughness", rough)
    set_in(b, "Metallic", metal)
    for k, v in extra.items():
        set_in(b, k, v)
    if bump > 0:
        add_normal_tex(nt, b, strength=bump * 4.0, scale=bump_scale / 10.0)
    mat.diffuse_color = (*color, 1.0)
    mat.use_fake_user = True
    return mat


def derive(src, name, size, sat=1.0, val=1.0, hue=0.5, rough_mul=1.0, normal=1.0, rot=0.0):
    """Copy a Poly Haven material; UVs are in metres, so Mapping scale = 1 / real size.
    Colour and roughness adjustments are baked into new texture files, not left as shader nodes."""
    old = bpy.data.materials.get(name)
    if old:
        old.name = name + "__old"
    mat = bpy.data.materials[src].copy()
    mat.name = name
    if old:                       # keep every existing assignment pointing at the rebuilt material
        old.user_remap(mat)
        bpy.data.materials.remove(old)
    nt = mat.node_tree
    b = principled(mat)
    mp = next(n for n in nt.nodes if n.type == "MAPPING")
    mp.inputs["Scale"].default_value = (1.0 / size, 1.0 / size, 1.0)
    mp.inputs["Rotation"].default_value = (0.0, 0.0, rot)
    for l in list(nt.links):
        if l.to_node.type == "OUTPUT_MATERIAL" and l.to_socket.name == "Displacement":
            nt.links.remove(l)
    col_link = next((l for l in nt.links if l.to_node == b and l.to_socket.name == "Base Color"), None)
    if col_link and col_link.from_node.type == "TEX_IMAGE" and (sat != 1.0 or val != 1.0 or hue != 0.5):
        col_link.from_node.image = bake_tint(col_link.from_node.image, name + "_Diffuse", hue, sat, val)
    r_link = next((l for l in nt.links if l.to_node == b and l.to_socket.name == "Roughness"), None)
    if r_link and r_link.from_node.type == "TEX_IMAGE" and rough_mul != 1.0:
        r_link.from_node.image = bake_scale(r_link.from_node.image, name + "_Rough", rough_mul)
    for n in nt.nodes:
        if n.type == "NORMAL_MAP":
            set_in(n, "Strength", normal)
    mat.use_fake_user = True
    return mat


def slab(src, name, size, box, sat, val, rough):
    """Poly Haven's stone sets are all tiled floors, and a countertop is one slab: crop a single tile from inside its
    grout lines (size = metres the source image covers; box = x0, y0, x1, y1 as fractions of it, origin bottom-left), mirror it into a seam-free repeat,
    lighten it and save it as a new texture. Polished stone: plain roughness, no normal map."""
    srcm = bpy.data.materials[src]
    sb = principled(srcm)
    simg = next(l.from_node.image for l in srcm.node_tree.links if l.to_node == sb and l.to_socket.name == "Base Color")
    w, h = simg.size
    x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)
    path = os.path.join(TEX_DIR, f"{name}_Diffuse_{src}_slab.png")
    if not os.path.exists(path):
        tile = _pixels(simg)[y0:y1, x0:x1]
        rep = np.concatenate([np.concatenate([tile, tile[:, ::-1]], 1), np.concatenate([tile[::-1], tile[::-1, ::-1]], 1)], 0)
        tmp = _write_tex(rep, path, name + "_Diffuse_src")
        img = bake_tint(tmp, name + "_Diffuse", 0.5, sat, val)
    else:
        img = bake_tint(_load_tex(path, name + "_Diffuse_src"), name + "_Diffuse", 0.5, sat, val)
    old = bpy.data.materials.get(name)
    if old:
        old.name = name + "__old"
    mat = bpy.data.materials.new(name)
    if old:
        old.user_remap(mat)
        bpy.data.materials.remove(old)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0 / (2 * (x1 - x0) / w * size), 1.0 / (2 * (y1 - y0) / h * size), 1.0)
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tx.inputs["Vector"])
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    set_in(b, "Roughness", rough)
    mat.use_fake_user = True
    return mat


def glass(name, tint=(1, 1, 1), rough=0.0):
    """Plain transmissive Principled. Glass objects are excluded from shadow rays so sunlight passes."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_in(b, "Base Color", (*tint, 1.0))
    set_in(b, "Roughness", rough)
    set_in(b, "IOR", 1.45)
    set_in(b, "Transmission Weight", 1.0)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    mat.use_fake_user = True
    return mat


def grass(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    img = ramp_image("TEX-lawn", [(0.0, (0.03, 0.065, 0.015)), (0.45, (0.05, 0.10, 0.022)), (1.0, (0.10, 0.16, 0.035))],
                     n=1024, beta=1.3, seed=5, detail=0.35)
    image_color(nt, b, img, 1.0 / 9.0)
    add_normal_tex(nt, b, strength=1.2, scale=1.5)
    set_in(b, "Roughness", 0.9)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    mat.use_fake_user = True
    return mat


M = {}
M["floor_oak"] = derive("oak_wood_planks", "MAT-floor_oak", 1.5, sat=0.72, val=1.0, rough_mul=1.15)
M["limestone"] = derive("concrete_brick_wall_001", "MAT-limestone", 1.7, sat=0.45, val=1.35)
M["brick"] = derive("brick_wall_003", "MAT-brick", 2.2, sat=1.0, val=1.15, hue=0.503)
M["shingle"] = derive("roof_slates_03", "MAT-roof_shingle", 3.0, sat=0.35, val=0.42)
M["concrete"] = derive("concrete_floor", "MAT-concrete", 2.08, sat=0.18, val=1.25)
M["tile"] = derive("floor_tiles_04", "MAT-tile_marble", 2.4, sat=0.5, val=1.2, rough_mul=0.8)
M["oak"] = derive("oak_veneer_03", "MAT-oak", 1.0, sat=1.15, val=0.85, hue=0.51)
M["timber"] = derive("oak_veneer_03", "MAT-timber", 1.0, sat=1.5, val=0.7, hue=0.51, rough_mul=1.2)
M["oak_ceiling"] = derive("oak_veneer_03", "MAT-oak_ceiling", 1.0, sat=1.4, val=0.62, hue=0.51)
M["white"] = solid("MAT-paint_white", (0.86, 0.85, 0.82), 0.55, bump=0.05)
M["charcoal"] = solid("MAT-paint_charcoal", (0.075, 0.08, 0.085), 0.5, bump=0.05)
M["ceiling"] = solid("MAT-paint_ceiling", (0.9, 0.9, 0.88), 0.7)
M["trim"] = derive("beige_wall_001", "MAT-trim_white", 3.0, sat=0.10, val=2.8, rough_mul=0.52, normal=0.5)   # painted millwork and cabinetry: Poly Haven smooth painted plaster, whitened
M["siding"] = solid("MAT-siding_dark", (0.04, 0.042, 0.045), 0.62, bump=0.08, bump_scale=120)
M["metal_black"] = solid("MAT-metal_black", (0.012, 0.012, 0.014), 0.38, metal=0.7)
M["hw_black"] = solid("MAT-hardware_black", (0.01, 0.01, 0.01), 0.3, metal=0.9)
M["roof_metal"] = solid("MAT-roof_metal", (0.03, 0.031, 0.034), 0.36, metal=0.9)
M["garage_door"] = solid("MAT-garage_door", (0.05, 0.052, 0.056), 0.45)
M["quartz"] = slab("marble_01", "MAT-quartz", 1.5, (0.070, 0.566, 0.453, 0.779), sat=0.18, val=1.75, rough=0.14)   # counters: one Poly Haven marble tile as a slab
M["steel"] = solid("MAT-stainless", (0.55, 0.56, 0.57), 0.24, metal=1.0)
# range hood: the same values as MAT-app_stainless on the manufacturer appliances (scripts/asset_convert.py), so the
# hood matches the range. Kept as a separate local material because the appliances' own material is linked.
M["hood"] = solid("MAT-hood_stainless", (0.62, 0.63, 0.64), 0.27, metal=1.0)
M["brass"] = solid("MAT-brass", (0.78, 0.57, 0.27), 0.28, metal=1.0)
M["porcelain"] = solid("MAT-porcelain", (0.9, 0.9, 0.9), 0.08)
M["mirror"] = solid("MAT-mirror", (0.9, 0.9, 0.9), 0.02, metal=1.0)
M["glass_dark"] = solid("MAT-glass_dark", (0.01, 0.012, 0.015), 0.05)
M["glass"] = glass("MAT-glass")
M["grass"] = grass("MAT-grass")

# ------------------------------------------------------------------ walls: split at the brick wainscot, classify faces
WAINSCOT = 0.95
PAINT = {"primary_suite": "charcoal", "office": "charcoal", "powder": "charcoal"}
walls = bpy.data.objects["GEO-walls"]
bm = bmesh.new()
bm.from_mesh(walls.data)
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, WAINSCOT), plane_no=(0, 0, 1))
slots = ["white", "charcoal", "brick", "siding"]
walls.data.materials.clear()
for s in slots:
    walls.data.materials.append(M[s])


def ext_kind(c, n):
    x, y, z = c
    brick_full = ((y < 1.0 and (2.7 < x < 7.8 or 18.5 < x < 23.8)) or (11.2 < x < 15.2 and y < 2.75)
                  or x > 26.9 or (x > 26.3 and 13.0 < y < 21.5) or (19.9 < x < 21.0 and 22.5 < y < 24.8))
    if brick_full:
        return "brick"
    siding_full = ((n.y < -0.5 and 2.3 < y < 3.0 and 7.5 < x < 18.9) or (y > 13.5 and 5.0 < x < 20.9))
    if siding_full:
        return "siding"
    return "brick" if z < WAINSCOT else "siding"


siding_faces = []      # (verts world, normal) for battens
for f in bm.faces:
    c = f.calc_center_median()
    n = f.normal
    if abs(n.z) > 0.5:
        f.material_index = 0
        continue
    p = c + n * 0.25
    if in_footprint((p.x, p.y)):
        r = room_at((p.x, p.y))
        if r and r["name"] == "portico":
            f.material_index = slots.index("brick")
        else:
            f.material_index = slots.index(PAINT.get(r["name"], "white") if r else "white")
    else:
        k = ext_kind(c, n)
        f.material_index = slots.index(k)
        if k == "siding":
            siding_faces.append(([v.co.copy() for v in f.verts], n.copy()))
bm.to_mesh(walls.data)
bm.free()

upper = bpy.data.objects["GEO-upper_walls"]
upper.data.materials.clear()
for s in ("siding", "brick", "glass_dark"):
    upper.data.materials.append(M[s])
for p in upper.data.polygons:
    x, y, z = p.center
    n = p.normal
    if (y < 1.0 and (2.7 < x < 7.8 or 18.5 < x < 23.8)) or (11.2 < x < 15.2 and y < 2.75) or x > 26.9:
        p.material_index = 1
    elif y < 3.47 and n.y < -0.5 and (abs(x - 9.58) < 0.47 or abs(x - 16.78) < 0.47) and z > 4.9:
        p.material_index = 2
    else:
        p.material_index = 0
        q = (x + n.x * 0.25, y + n.y * 0.25)
        faces_room = z < 4.4 and room_at(q) is not None      # inner face of a gable above a vaulted room
        if n.x < -0.5 and x > 25.9 and 3.6 < y < 8.7:        # inside face of the bonus dormer wall
            faces_room = True
        if abs(n.z) < 0.1 and not faces_room:
            siding_faces.append(([upper.data.vertices[i].co.copy() for i in p.vertices], n.copy()))

# ------------------------------------------------------------------ board-and-batten strips
wipe_col("COL-cladding")
ccol = get_col("COL-cladding")
bm = bmesh.new()
SP, BW, BT = 0.406, 0.045, 0.018
Z = Vector((0, 0, 1))
nb = 0
for verts, n in siding_faces:
    t = Z.cross(n).normalized()
    ss = [v.dot(t) for v in verts]
    s0, s1 = min(ss), max(ss)
    if s1 - s0 < 0.05:
        continue
    d = verts[0].dot(n)
    k = math.ceil((s0 + 0.01) / SP)
    while k * SP < s1 - 0.01:
        s = k * SP
        zs = []
        m = len(verts)
        for i in range(m):
            a, b = verts[i], verts[(i + 1) % m]
            sa, sb = a.dot(t), b.dot(t)
            if (sa - s) * (sb - s) < 0 and abs(sb - sa) > 1e-9:
                zs.append(a.z + (b.z - a.z) * (s - sa) / (sb - sa))
        if len(zs) >= 2 and max(zs) - min(zs) > 0.08:
            z0, z1 = min(zs), max(zs)
            base = t * s + n * d
            base.z = 0
            pts = []
            for zz in (z0, z1):
                for (ds, dn) in ((-BW / 2, 0), (BW / 2, 0), (BW / 2, BT), (-BW / 2, BT)):
                    q = base + t * ds + n * dn
                    pts.append(bm.verts.new((q.x, q.y, zz)))
            for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                bm.faces.new([pts[i] for i in idx])
            nb += 1
        k += 1
bat = new_obj("GEO-battens", bm, ccol)
fix_normals(bat)
assign(bat, M["siding"])

# ------------------------------------------------------------------ floor finishes
wipe_col("COL-floors")
fcol = get_col("COL-floors")
TILE_ROOMS = {"primary_bath", "primary_wc", "hall_bath", "powder", "jj_bath_a", "jj_bath_b", "utility"}
NO_FINISH = {"garage", "portico", "stair"}
bo, bt = bmesh.new(), bmesh.new()
for r in S["rooms"]:
    if r["name"] in NO_FINISH or r["name"].startswith("room_"):
        continue
    add_prism(bt if r["name"] in TILE_ROOMS else bo, r["outer"], r["holes"], 0.0, 0.012, caps=(False, True))
for o in S["openings"]:
    if o["type"].startswith("window") or o["type"] in ("garage",):
        continue
    c = Vector(o["c"])
    n = Vector((-o["u"][1], o["u"][0]))
    ra = room_at(tuple(c + n * (o["t"] / 2 + 0.2)))
    rb = room_at(tuple(c - n * (o["t"] / 2 + 0.2)))
    names = {r["name"] for r in (ra, rb) if r}
    if not names or names & {"garage"} and len(names) == 1:
        continue
    tile = names and names <= TILE_ROOMS
    add_box(bt if tile else bo, o["c"], o["u"], o["w"] / 2 + 0.01, o["t"] / 2 + 0.012, 0.0, 0.011)
fo = new_obj("GEO-floor_oak", bo, fcol)
ft = new_obj("GEO-floor_tile", bt, fcol)
assign(fo, M["floor_oak"])
assign(ft, M["tile"])

# ------------------------------------------------------------------ everything else by object name
RULES = [
    ("GEO-slab", "concrete"), ("GEO-ceiling_", "ceiling"), ("GEO-bonus_shell", "white"),
    ("GEO-floor_bonus", "floor_oak"), ("GEO-winframe_", "metal_black"), ("GEO-glass_", "glass"),
    ("GEO-winstool_", "trim"), ("GEO-doorleaf_dark_", "metal_black"), ("GEO-doorleaf_pantry_door", "oak"),
    ("GEO-doorleaf_ddoor_glass", "metal_black"), ("GEO-doorleaf_", "trim"), ("GEO-jamb_", "trim"),
    ("GEO-doorhw_", "hw_black"), ("GEO-garagedoor_", "garage_door"), ("GEO-roof_shingle", "shingle"),
    ("GEO-roof_metal", "roof_metal"), ("GEO-porch_slab", "concrete"), ("GEO-porch_timber", "timber"),
    ("GEO-porch_ceiling", "oak_ceiling"), ("GEO-chimneys", "brick"),
]
done = 0
for ob in bpy.data.objects:
    if ob.type != "MESH" or not ob.name.startswith("GEO-"):
        continue
    if ob.name in ("GEO-walls", "GEO-upper_walls", "GEO-battens", "GEO-floor_oak", "GEO-floor_tile"):
        continue
    for prefix, key in RULES:
        if ob.name.startswith(prefix):
            assign(ob, M[key])
            done += 1
            break
assign(bpy.data.objects["GEO-ceiling_primary_suite"], M["charcoal"])
for ob in bpy.data.objects:
    if ob.type == "MESH" and (ob.name.startswith("GEO-glass_") or ob.name.endswith("_glass")):
        ob.visible_shadow = False
# stair: oak treads, white risers and sides
st = bpy.data.objects["GEO-stair"]
st.data.materials.clear()
st.data.materials.append(M["white"])
st.data.materials.append(M["floor_oak"])
for p in st.data.polygons:
    p.material_index = 1 if p.normal.z > 0.5 else 0

# ------------------------------------------------------------------ site
wipe_col("COL-site")
scol = get_col("COL-site")
bm = bmesh.new()
add_prism(bm, [(-90, -70), (120, -70), (120, 110), (-90, 110)], [], -0.6, -0.16)
g = new_obj("GEO-ground", bm, scol)
assign(g, M["grass"])
bm = bmesh.new()
add_prism(bm, [(12.3, -14.0), (14.1, -14.0), (14.1, 0.0), (12.3, 0.0)], [], -0.3, -0.12)        # front walk
add_prism(bm, [(26.3, 0.8), (36.5, 0.8), (36.5, 11.3), (26.3, 11.3)], [], -0.3, -0.02)          # garage apron
add_prism(bm, [(30.5, -14.0), (36.5, -14.0), (36.5, 0.8), (30.5, 0.8)], [], -0.3, -0.12)        # drive to street
add_prism(bm, [(-90, -21.0), (120, -21.0), (120, -14.0), (-90, -14.0)], [], -0.3, -0.13)        # street
pv = new_obj("GEO-paving", bm, scol)
assign(pv, M["concrete"])

# ------------------------------------------------------------------ UVs for everything this job built
nuv = 0
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name.startswith("GEO-"):
        uv_box(ob)
        nuv += 1
print("battens", nb, "siding faces", len(siding_faces), "assigned", done, "uv objects", nuv)
