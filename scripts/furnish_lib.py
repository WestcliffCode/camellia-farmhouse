"""Stage 4 library: Poly Haven asset instancing and procedural furniture / fixture builders.

exec() after bl_common.py. Poly Haven models are imported once (each lands in a collection named by
its asset id); organise_assets() parks those collections under COL-assets_src and place() instances them.
"""
PH_ASSETS = ["modern_arm_chair_01", "side_table_01", "modern_coffee_table_01", "coffee_table_round_01",
             "dining_chair_02", "mid_century_lounge_chair", "steel_frame_shelves_01", "steel_frame_shelves_03",
             "drawer_cabinet", "modern_wooden_cabinet", "potted_plant_01", "potted_plant_02", "potted_plant_04",
             "ceramic_vase_01", "ceramic_vase_03", "wooden_bowl_01", "decorative_book_set_01",
             "modern_ceiling_lamp_01"]
LAMPS = []          # (x, y, z, kind, room) for the lighting stage


def _layer_col(name, root=None):
    root = root or bpy.context.view_layer.layer_collection
    if root.name == name:
        return root
    for c in root.children:
        r = _layer_col(name, c)
        if r:
            return r
    return None


def organise_assets():
    src = get_col("COL-assets_src")
    scn = bpy.context.scene.collection
    for aid in PH_ASSETS:
        c = bpy.data.collections.get(aid)
        if c is None:
            print("MISSING ASSET", aid)
            continue
        if c.name in scn.children:
            scn.children.unlink(c)
        if c.name not in src.children:
            src.children.link(c)
    # three shelf-length book groups cut from the decorative set
    books = bpy.data.collections.get("decorative_book_set_01")
    if books:
        for nm, (a, b) in {"ASSET-books_a": (-0.01, 0.56), "ASSET-books_b": (0.62, 1.16), "ASSET-books_c": (1.2, 1.78)}.items():
            g = bpy.data.collections.get(nm) or bpy.data.collections.new(nm)
            if g.name not in src.children:
                src.children.link(g)
            for ob in books.objects:
                if a <= ob.location.x <= b and ob.name not in g.objects:
                    g.objects.link(ob)
            g["x0"] = a
    lc = _layer_col("COL-assets_src")
    if lc:
        lc.exclude = True


def _col_bbox(c):
    lo, hi = Vector((1e9, 1e9, 1e9)), Vector((-1e9, -1e9, -1e9))
    for ob in c.all_objects:
        if ob.type != "MESH":
            continue
        for corner in ob.bound_box:
            w = ob.matrix_world @ Vector(corner)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi


def place(asset, x, y, z=0.0, facing=(0, -1), col=None, scale=1.0, anchor="bottom", name=None):
    """Instance a Poly Haven asset collection. Models face -Y; `facing` is where the front should point."""
    c = bpy.data.collections.get(asset)
    if c is None:
        print("MISSING", asset)
        return None
    lo, hi = _col_bbox(c)
    e = bpy.data.objects.new(name or f"INST-{asset}", None)
    e.instance_type = "COLLECTION"
    e.instance_collection = c
    e.empty_display_size = 0.2
    rot = math.atan2(facing[1], facing[0]) + math.pi / 2
    e.rotation_euler = (0, 0, rot)
    e.scale = (scale, scale, scale)
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    off = Vector((-cx * scale, -cy * scale, 0.0))
    off.rotate(__import__("mathutils").Euler((0, 0, rot)))
    zoff = -lo.z * scale if anchor == "bottom" else -hi.z * scale
    e.location = (x + off.x, y + off.y, z + zoff)
    (col or bpy.context.scene.collection).objects.link(e)
    return e


# ------------------------------------------------------------------ extra materials
def _fabric(name, color, rough=0.92, sheen=0.35, bump=0.12, scale=420.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_in(b, "Base Color", (*color, 1.0))
    set_in(b, "Roughness", rough)
    set_in(b, "Sheen Weight", sheen)
    add_normal_tex(nt, b, strength=bump * 5.0, scale=scale / 30.0)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    mat.diffuse_color = (*color, 1.0)
    mat.use_fake_user = True
    return mat


def _art(name, c1, c2, c3, scale=1.6, seed=1):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    img = ramp_image("TEX-" + name[4:], [(0.0, c1), (0.42, c1), (0.5, c2), (0.6, c3), (1.0, c3)], n=768, beta=2.3, seed=seed)
    image_color(nt, b, img, 1.0 / scale)
    set_in(b, "Roughness", 0.85)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    mat.use_fake_user = True
    return mat


def _shade(name, color):
    """Lamp shade: matte, softly self-lit. Shade objects are excluded from shadow rays so the bulb lights the room."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_in(b, "Base Color", (*color, 1.0))
    set_in(b, "Roughness", 0.9)
    set_in(b, "Emission Color", (1.0, 0.72, 0.45, 1.0))
    set_in(b, "Emission Strength", 2.2)
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    mat.use_fake_user = True
    return mat


def furnish_materials():
    F_ = {"fab_oat": (0.58, 0.53, 0.45), "fab_white": (0.80, 0.78, 0.73), "fab_sage": (0.30, 0.36, 0.28),
          "fab_rust": (0.45, 0.19, 0.11), "fab_navy": (0.05, 0.08, 0.15), "fab_char": (0.10, 0.10, 0.11),
          "fab_grey": (0.42, 0.42, 0.41), "rug_cream": (0.70, 0.66, 0.58), "rug_blue": (0.30, 0.36, 0.42),
          "rug_warm": (0.55, 0.42, 0.32), "curtain": (0.84, 0.82, 0.77), "towel": (0.86, 0.85, 0.83)}
    for k, c in F_.items():
        big = k.startswith("rug")
        _fabric("MAT-" + k, c, bump=0.3 if big else 0.12, scale=260.0 if big else 420.0)
        MATN[k] = "MAT-" + k
    m = _fabric("MAT-leather_tan", (0.36, 0.20, 0.11), rough=0.48, sheen=0.0, bump=0.06, scale=180.0)
    MATN["leather"] = m.name
    _art("MAT-art_a", (0.82, 0.78, 0.70), (0.42, 0.47, 0.42), (0.12, 0.15, 0.18), 1.8, seed=21)
    _art("MAT-art_b", (0.85, 0.82, 0.76), (0.62, 0.38, 0.24), (0.20, 0.17, 0.15), 1.5, seed=22)
    _art("MAT-art_c", (0.80, 0.80, 0.78), (0.30, 0.38, 0.46), (0.08, 0.10, 0.14), 1.3, seed=23)
    MATN.update({"art_a": "MAT-art_a", "art_b": "MAT-art_b", "art_c": "MAT-art_c"})
    _shade("MAT-lamp_shade", (0.88, 0.84, 0.76))
    MATN["shade"] = "MAT-lamp_shade"
    mat = bpy.data.materials.get("MAT-ceramic_matte") or bpy.data.materials.new("MAT-ceramic_matte")
    mat.use_nodes = True
    b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    set_in(b, "Base Color", (0.82, 0.80, 0.75, 1))
    set_in(b, "Roughness", 0.45)
    mat.use_fake_user = True
    MATN["ceramic"] = mat.name
    _fabric("MAT-mat_rubber", (0.03, 0.03, 0.035), rough=0.8, sheen=0.0, bump=0.2, scale=200.0)
    MATN["rubber"] = "MAT-mat_rubber"
    bs = bpy.data.materials.get("MAT-basin") or bpy.data.materials.new("MAT-basin")
    bs.use_nodes = True
    bn = next(n for n in bs.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    set_in(bn, "Base Color", (0.78, 0.82, 0.83, 1))
    set_in(bn, "Roughness", 0.05)
    bs.use_fake_user = True
    MATN["basin"] = bs.name
    bl = bpy.data.materials.get("MAT-bulb") or bpy.data.materials.new("MAT-bulb")
    bl.use_nodes = True
    bb = next(n for n in bl.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    set_in(bb, "Base Color", (1.0, 0.85, 0.65, 1))
    set_in(bb, "Emission Color", (1.0, 0.72, 0.42, 1))
    set_in(bb, "Emission Strength", 25.0)
    bl.use_fake_user = True
    MATN["bulb"] = bl.name


SOFT = ("fab_", "leather", "rug_", "towel", "porcelain")


def soften(obs, width=0.03):
    for ob in obs:
        key = ob.name.rsplit("_", 2)
        if not any(s in ob.name for s in SOFT) or "rug_" in ob.name:
            continue
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width = width
        bv.segments = 3
        bv.limit_method = "ANGLE"
        for p in ob.data.polygons:
            p.use_smooth = True
        wn = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        wn.keep_sharp = True
    for ob in obs:
        if ob.name.endswith(("_glass", "_shade")):
            ob.visible_shadow = False


def facing_frame(x, y, facing):
    """Frame whose d axis points along `facing` (front of the piece); origin = back-centre on the floor."""
    return Frame((x, y), (facing[1], -facing[0]))


# ------------------------------------------------------------------ seating and beds
def sofa(B, x, y, facing, w=2.4, depth=0.95, fab="fab_oat", accent=("fab_sage", "fab_white"), seats=3, base=0.0):
    F = facing_frame(x, y, facing)
    z = base
    for sx in (-w / 2 + 0.08, w / 2 - 0.08):
        for dd in (0.08, depth - 0.08):
            B.box("hw", F, sx - 0.025, sx + 0.025, dd - 0.025, dd + 0.025, z, z + 0.12)
    B.box(fab, F, -w / 2, w / 2, 0.0, depth, z + 0.12, z + 0.40)
    B.box(fab, F, -w / 2, w / 2, 0.0, 0.2, z + 0.40, z + 0.84)
    B.box(fab, F, -w / 2, -w / 2 + 0.2, 0.2, depth, z + 0.40, z + 0.63)
    B.box(fab, F, w / 2 - 0.2, w / 2, 0.2, depth, z + 0.40, z + 0.63)
    sw = (w - 0.4) / seats
    for i in range(seats):
        a = -w / 2 + 0.2 + i * sw
        B.box(fab, F, a + 0.01, a + sw - 0.01, 0.22, depth + 0.02, z + 0.40, z + 0.53)
        B.box(fab, F, a + 0.02, a + sw - 0.02, 0.2, 0.40, z + 0.53, z + 0.90)
    for i, sx in enumerate((-w / 2 + 0.42, w / 2 - 0.42)):
        B.box(accent[i % len(accent)], F, sx - 0.22, sx + 0.22, 0.38, 0.52, z + 0.55, z + 0.95)


def bed(B, x, y, facing, size="queen", fab="fab_oat", accent="fab_sage"):
    w, ln = (1.93, 2.03) if size == "king" else (1.53, 2.03)
    F = facing_frame(x, y, facing)
    B.box(fab, F, -w / 2 - 0.08, w / 2 + 0.08, 0.0, 0.10, 0.0, 1.32)             # headboard
    B.box("oak", F, -w / 2 - 0.04, w / 2 + 0.04, 0.10, ln + 0.14, 0.14, 0.34)    # frame
    for sx in (-w / 2 + 0.05, w / 2 - 0.05):
        for dd in (0.2, ln + 0.05):
            B.box("oak", F, sx - 0.04, sx + 0.04, dd - 0.04, dd + 0.04, 0.0, 0.14)
    B.box("fab_white", F, -w / 2, w / 2, 0.12, ln + 0.10, 0.34, 0.60)            # mattress
    B.box("fab_white", F, -w / 2 - 0.03, w / 2 + 0.03, 0.62, ln + 0.13, 0.50, 0.66)   # duvet
    B.box(accent, F, -w / 2 - 0.04, w / 2 + 0.04, ln - 0.45, ln + 0.14, 0.52, 0.675)  # throw at the foot
    n = 2
    pw = w / n
    for i in range(n):
        a = -w / 2 + i * pw
        B.box("fab_white", F, a + 0.05, a + pw - 0.05, 0.14, 0.50, 0.60, 0.76)
        B.box(fab, F, a + 0.10, a + pw - 0.10, 0.44, 0.62, 0.60, 0.92)
    B.box(accent, F, -0.32, 0.32, 0.60, 0.72, 0.62, 0.88)


def bench(B, x, y, facing, w=1.3, fab="fab_oat"):
    F = facing_frame(x, y, facing)
    for sx in (-w / 2 + 0.06, w / 2 - 0.06):
        B.box("oak", F, sx - 0.03, sx + 0.03, 0.05, 0.40, 0.0, 0.36)
    B.box("oak", F, -w / 2, w / 2, 0.0, 0.45, 0.36, 0.40)
    B.box(fab, F, -w / 2 + 0.01, w / 2 - 0.01, 0.01, 0.44, 0.40, 0.48)


def stool(B, x, y, seat=0.66):
    for dx, dy in ((-0.15, -0.15), (0.15, -0.15), (0.15, 0.15), (-0.15, 0.15)):
        B.rod("hw", (x + dx, y + dy, 0.0), (x + dx * 0.75, y + dy * 0.75, seat - 0.03), 0.012, seg=8)
    for a, b in (((-0.15, -0.15), (0.15, -0.15)), ((0.15, -0.15), (0.15, 0.15)), ((0.15, 0.15), (-0.15, 0.15)), ((-0.15, 0.15), (-0.15, -0.15))):
        B.rod("hw", (x + a[0] * 0.9, y + a[1] * 0.9, 0.24), (x + b[0] * 0.9, y + b[1] * 0.9, 0.24), 0.009, seg=8)
    B.cyl("oak", (x, y), 0.18, seat - 0.03, seat + 0.01, seg=20)
    B.cyl("leather", (x, y), 0.17, seat + 0.01, seat + 0.045, seg=20)


# ------------------------------------------------------------------ tables and storage
def table(B, x, y, w, d, h=0.75, key="oak", legs="post", facing=(0, 1), thick=0.045):
    F = facing_frame(x, y, facing)
    B.box(key, F, -w / 2, w / 2, -d / 2, d / 2, h - thick, h)
    if legs == "trestle":
        for sx in (-w / 2 + 0.35, w / 2 - 0.35):
            B.box(key, F, sx - 0.05, sx + 0.05, -d / 2 + 0.12, d / 2 - 0.12, 0.0, h - thick)
        B.box(key, F, -w / 2 + 0.35, w / 2 - 0.35, -0.04, 0.04, 0.22, 0.30)
    elif legs == "steel":
        for sx in (-w / 2 + 0.06, w / 2 - 0.06):
            B.box("hw", F, sx - 0.02, sx + 0.02, -d / 2 + 0.05, d / 2 - 0.05, h - thick - 0.03, h - thick)
            for dd in (-d / 2 + 0.07, d / 2 - 0.07):
                B.box("hw", F, sx - 0.02, sx + 0.02, dd - 0.02, dd + 0.02, 0.0, h - thick)
    else:
        for sx in (-w / 2 + 0.07, w / 2 - 0.07):
            for dd in (-d / 2 + 0.07, d / 2 - 0.07):
                B.box(key, F, sx - 0.035, sx + 0.035, dd - 0.035, dd + 0.035, 0.0, h - thick)


def round_table(B, x, y, r=0.6, h=0.75, key="oak"):
    B.cyl(key, (x, y), r, h - 0.04, h, seg=40)
    B.cyl(key, (x, y), 0.07, 0.03, h - 0.04, seg=16)
    B.cyl(key, (x, y), 0.32, 0.0, 0.03, seg=28)


def dresser(B, x, y, facing, w=1.5, h=0.82, d=0.48, key="oak"):
    F = facing_frame(x, y, facing)
    for sx in (-w / 2 + 0.05, w / 2 - 0.05):
        B.box("hw", F, sx - 0.02, sx + 0.02, 0.05, d - 0.05, 0.0, 0.12)
    B.box(key, F, -w / 2, w / 2, 0.0, d - 0.016, 0.12, h)
    for r in range(3):
        z0 = 0.12 + r * (h - 0.12) / 3
        cab_doors(B, key, F, -w / 2, w / 2, d - 0.016, z0, z0 + (h - 0.12) / 3, 2, pulls="h")
    B.box(key, F, -w / 2 - 0.01, w / 2 + 0.01, 0.0, d + 0.01, h, h + 0.025)


def console(B, x, y, facing, w=1.4, h=0.82, d=0.36, key="oak"):
    F = facing_frame(x, y, facing)
    B.box(key, F, -w / 2, w / 2, 0.0, d, h - 0.045, h)
    B.box(key, F, -w / 2 + 0.04, w / 2 - 0.04, 0.03, d - 0.03, 0.18, 0.21)
    for sx in (-w / 2 + 0.05, w / 2 - 0.05):
        for dd in (0.05, d - 0.05):
            B.box("hw", F, sx - 0.018, sx + 0.018, dd - 0.018, dd + 0.018, 0.0, h - 0.045)


def rug(B, x, y, w, d, key="rug_cream", facing=(0, 1), z=0.012):
    F = facing_frame(x, y, facing)
    B.box(key, F, -w / 2, w / 2, -d / 2, d / 2, z, z + 0.012)


# ------------------------------------------------------------------ lamps, art, soft goods
def table_lamp(B, x, y, z, room="", h=0.55):
    B.cyl("ceramic", (x, y), 0.07, z, z + h * 0.5, seg=18, r2=0.045)
    B.cyl("brass", (x, y), 0.008, z + h * 0.5, z + h * 0.72, seg=8)
    B.cyl("shade", (x, y), 0.17, z + h * 0.62, z + h, seg=24, r2=0.12)
    LAMPS.append((x, y, z + h * 0.82, "table", room))


def floor_lamp(B, x, y, room="", z=0.0):
    B.cyl("hw", (x, y), 0.14, z, z + 0.02, seg=20)
    B.cyl("hw", (x, y), 0.012, z + 0.02, z + 1.45, seg=8)
    B.cyl("shade", (x, y), 0.21, z + 1.35, z + 1.68, seg=24, r2=0.16)
    LAMPS.append((x, y, z + 1.52, "floor", room))


def ring_chandelier(B, x, y, z_top, drop=1.2, r=0.55, n=10, room=""):
    zr = z_top - drop
    for k in range(40):
        a0, a1 = 2 * math.pi * k / 40, 2 * math.pi * (k + 1) / 40
        B.rod("hw", (x + r * math.cos(a0), y + r * math.sin(a0), zr), (x + r * math.cos(a1), y + r * math.sin(a1), zr), 0.02, seg=6)
    B.cyl("hw", (x, y), 0.012, zr + 0.6, z_top, seg=8)
    B.cyl("hw", (x, y), 0.06, z_top - 0.02, z_top, seg=16)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        B.rod("hw", (x + r * math.cos(a), y + r * math.sin(a), zr), (x, y, zr + 0.6), 0.005, seg=6)
    for k in range(n):
        a = 2 * math.pi * k / n
        cx, cy = x + r * math.cos(a), y + r * math.sin(a)
        B.cyl("ceramic", (cx, cy), 0.012, zr + 0.025, zr + 0.14, seg=8)
        B.ellipsoid("bulb", (cx, cy, zr + 0.165), 0.014, 0.014, 0.028, seg=8)
    LAMPS.append((x, y, zr + 0.1, "chandelier", room))


def art(B, x, y, facing, w=1.0, h=1.2, z=1.0, key="art_a", frame="hw"):
    F = facing_frame(x, y, facing)
    B.box(frame, F, -w / 2, w / 2, 0.0, 0.03, z, z + h)
    B.box(key, F, -w / 2 + 0.03, w / 2 - 0.03, 0.03, 0.034, z + 0.03, z + h - 0.03)


def round_mirror(B, x, y, facing, r=0.45, z=1.55):
    F = facing_frame(x, y, facing)
    for key, rr, d0, d1 in (("hw", r, 0.0, 0.025), ("mirror", r - 0.025, 0.025, 0.03)):
        b = B.bm(key)
        m = bmesh.ops.create_cone(b, cap_ends=True, segments=48, radius1=rr, radius2=rr, depth=d1 - d0)
        for v in m["verts"]:
            s, zz, dd = v.co.x, v.co.y, v.co.z
            v.co = Vector(F.p(s, (d0 + d1) / 2 + dd, z + zz))


def curtains(B, o, key="curtain", panel=0.55, top=2.62):
    """Two linen panels and a rod inside the room at a window opening `o`."""
    F = Frame(o["c"], o["u"])
    inward = Vector((-o["n_out"][0], -o["n_out"][1]))
    sgn = 1.0 if F.n.dot(inward) > 0 else -1.0
    d0 = sgn * (o["t"] / 2 + 0.07)
    w = o["w"]
    b = B.bm(key)
    for side in (-1, 1):
        s_in = side * (w / 2 - 0.05)
        s_out = side * (w / 2 + panel)
        N = 22
        rows = []
        for zz in (0.03, top):
            row = []
            for i in range(N + 1):
                s = s_in + (s_out - s_in) * i / N
                dd = d0 + sgn * 0.035 * math.sin(i * 1.9)
                row.append(b.verts.new(F.p(s, dd, zz)))
            rows.append(row)
        for i in range(N):
            b.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    a, e = F.p(-w / 2 - panel - 0.08, d0, top + 0.03), F.p(w / 2 + panel + 0.08, d0, top + 0.03)
    B.rod("hw", a, e, 0.012, seg=8)


# ------------------------------------------------------------------ bath and utility fixtures
def toilet(B, x, y, facing):
    F = facing_frame(x, y, facing)
    B.box("porcelain", F, -0.19, 0.19, 0.0, 0.19, 0.38, 0.80)
    B.box("porcelain", F, -0.20, 0.20, -0.005, 0.20, 0.80, 0.83)
    c = F.p(0.0, 0.44, 0.0)
    B.ellipsoid("porcelain", (c[0], c[1], 0.27), 0.19 if abs(F.u.x) > 0.5 else 0.25, 0.25 if abs(F.u.x) > 0.5 else 0.19, 0.2, seg=20)
    B.box("porcelain", F, -0.12, 0.12, 0.18, 0.48, 0.0, 0.22)
    c2 = F.p(0.0, 0.43, 0.0)
    B.ellipsoid("porcelain", (c2[0], c2[1], 0.415), 0.185 if abs(F.u.x) > 0.5 else 0.235, 0.235 if abs(F.u.x) > 0.5 else 0.185, 0.02, seg=20)


def vanity(B, x, y, facing, w=1.5, sinks=1, key="oak", room="", mirror=True, towers=False):
    F = facing_frame(x, y, facing)
    base_cabinet(B, F, -w / 2, w / 2, 0.0, z_top=0.83, depth=0.54, key=key, n=max(2, round(w / 0.5)), splash=0.1)
    for i in range(sinks):
        sc = (i + 0.5) * w / sinks - w / 2
        c = F.p(sc, 0.29, 0.0)
        elong = abs(F.u.x) > 0.5
        B.ellipsoid("porcelain", (c[0], c[1], 0.868), 0.24 if elong else 0.17, 0.17 if elong else 0.24, 0.018, seg=24)
        B.ellipsoid("basin", (c[0], c[1], 0.878), 0.20 if elong else 0.13, 0.13 if elong else 0.20, 0.012, seg=20)
        f = F.p(sc, 0.07, 0.0)
        B.cyl("brass", (f[0], f[1]), 0.012, 0.86, 1.06, seg=10)
        B.rod("brass", (f[0], f[1], 1.05), F.p(sc, 0.2, 1.05), 0.01, seg=8)
        if mirror:
            mw = min(0.8, w / sinks - 0.25)
            B.box("hw", F, sc - mw / 2, sc + mw / 2, 0.0, 0.02, 1.08, 2.08)
            B.box("mirror", F, sc - mw / 2 + 0.02, sc + mw / 2 - 0.02, 0.02, 0.024, 1.10, 2.06)
            LAMPS.append((*F.xy(sc, 0.12), 2.2, "sconce", room))
    if towers:
        for sx in (-w / 2 - 0.42, w / 2 + 0.02):
            B.box(key, F, sx, sx + 0.40, 0.0, 0.40, 0.0, 2.2)
            cab_doors(B, key, F, sx, sx + 0.40, 0.40, 0.9, 2.2, 1)


def tub(B, x, y, long_axis=(0, 1), w=0.82, ln=1.75, h=0.58):
    F = Frame((x, y), long_axis)
    elong = abs(F.u.x) > 0.5
    rx, ry = (ln / 2, w / 2) if elong else (w / 2, ln / 2)
    B.ellipsoid("porcelain", (x, y, h * 0.52), rx, ry, h * 0.56, seg=28)
    B.ellipsoid("basin", (x, y, h + 0.02), rx - 0.07, ry - 0.07, 0.03, seg=24)
    f = F.p(-ln / 2 - 0.12, 0.0, 0.0)
    B.cyl("brass", (f[0], f[1]), 0.016, 0.0, 0.95, seg=10)
    B.rod("brass", (f[0], f[1], 0.94), F.p(-ln / 2 + 0.12, 0.0, 0.94), 0.013, seg=8)


def shower(B, x0, y0, x1, y1, glass_sides, door_side=None, room=""):
    """Tiled shower in the rectangle; glass_sides is a subset of 'W','E','S','N' that are glazed."""
    for side in "WESN":
        if side in glass_sides:
            a, b = {"W": ((x0, y0), (x0, y1)), "E": ((x1, y0), (x1, y1)), "S": ((x0, y0), (x1, y0)), "N": ((x0, y1), (x1, y1))}[side]
            F = Frame(a, (b[0] - a[0], b[1] - a[1]))
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            B.box("glass", F, 0.0, L, -0.005, 0.005, 0.02, 2.15)
            B.box("hw", F, 0.0, L, -0.012, 0.012, 2.15, 2.17)
            B.box("hw", F, L * 0.48, L * 0.48 + 0.02, 0.01, 0.06, 0.95, 1.25)
        else:
            a, b = {"W": ((x0, y0), (x0, y1)), "E": ((x1, y1), (x1, y0)), "S": ((x1, y0), (x0, y0)), "N": ((x0, y1), (x1, y1))}[side]
            F = Frame(a, (b[0] - a[0], b[1] - a[1]))
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            c = F.p(L / 2, 0.02, 0)
            sgn = 1 if (x0 <= c[0] <= x1 and y0 <= c[1] <= y1) else -1
            B.box("tile", F, 0.0, L, 0.0, sgn * 0.012, 0.012, 2.6)
    B.box("tile", WORLD, x0, x1, y0, y1, 0.012, 0.02)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    B.cyl("hw", (cx, cy), 0.13, 2.25, 2.27, seg=20)
    B.cyl("hw", (cx, cy), 0.012, 2.27, CEIL, seg=8)
    LAMPS.append((cx, cy, CEIL - 0.03, "can", room))


def appliance(B, x, y, facing, w=0.69, d=0.72, h=0.98):
    F = facing_frame(x, y, facing)
    B.box("trim", F, -w / 2, w / 2, 0.0, d, 0.0, h)
    c = F.p(0.0, d + 0.012, h * 0.47)
    b = B.bm("glassdark")
    m = bmesh.ops.create_cone(b, cap_ends=True, segments=28, radius1=0.2, radius2=0.2, depth=0.02)
    rot = Vector((facing[0], facing[1], 0)).to_track_quat("Z", "Y").to_matrix()
    for v in m["verts"]:
        v.co = rot @ v.co + Vector(c)
    B.box("hw", F, -w / 2 + 0.05, w / 2 - 0.05, d, d + 0.01, h - 0.13, h - 0.04)


def shelf_wall(B, x, y, facing, w, levels=(0.4, 0.85, 1.3, 1.75), d=0.4, key="trim", rod_z=None):
    F = facing_frame(x, y, facing)
    for zz in levels:
        B.box(key, F, -w / 2, w / 2, 0.0, d, zz, zz + 0.025)
    for sx in (-w / 2, w / 2 - 0.02):
        B.box(key, F, sx, sx + 0.02, 0.0, d, 0.0, max(levels) + 0.025)
    if rod_z:
        B.rod("hw", F.p(-w / 2, d * 0.6, rod_z), F.p(w / 2, d * 0.6, rod_z), 0.014, seg=8)
        cols_ = ("fab_white", "fab_navy", "fab_oat", "fab_grey", "fab_sage", "fab_char")
        n = int(w / 0.075)
        for i in range(n):
            if i % 7 == 6:
                continue
            s = -w / 2 + 0.05 + i * 0.075
            B.box(cols_[(i * 5) % len(cols_)], F, s, s + 0.05, d * 0.6 - 0.22, d * 0.6 + 0.22, rod_z - 1.0 + (i % 3) * 0.12, rod_z - 0.03)


def stock(B, x, y, facing, w, d, levels, keys=("rug_warm", "fab_oat", "trim", "oak"), h=0.26, step=0.4, size=0.3):
    """Storage bins / folded stacks standing on the shelves of a shelf_wall."""
    F = facing_frame(x, y, facing)
    for zi, zz in enumerate(levels):
        n = int((w - 0.12) / step)
        for i in range(n):
            if (i + zi) % 5 == 4:
                continue
            s = -w / 2 + 0.08 + i * step
            hh = h * (0.7 + 0.3 * ((i * 3 + zi) % 3) / 2)
            B.box(keys[(i + zi * 2) % len(keys)], F, s, s + size, 0.04, d - 0.04, zz + 0.025, zz + 0.025 + hh)
