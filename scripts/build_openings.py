"""Stage 2b: windows, sliders, interior and exterior doors, garage doors.

Object naming carries the material role for Stage 3:
  GEO-winframe_*  dark metal/clad frame      GEO-glass_*   glazing
  GEO-doorleaf_*  painted or oak door leaf   GEO-jamb_*    painted jamb + casing
  GEO-doorhw_*    hardware                   GEO-garagedoor_*
"""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-openings")
col = get_col("COL-openings")
col_win = get_col("COL-windows", col)
col_door = get_col("COL-doors", col)
walls = bpy.data.objects["GEO-walls"]

CLOSETS = ("closet", "storage", "holiday", "linen", "pantry", "hutch")
CIRC = {"great_room", "bed_hall", "bed_hall_s", "primary_hall", "family_foyer",
        "back_vestibule", "foyer", "mud_vestibule", "stair", "garage"}
KEEP_CLOSED = {"garage_pantry_door"}


def pip(pt, ring):
    x, y = pt
    inside = False
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


def room_at(pt):
    for r in S["rooms"]:
        if pip(pt, r["outer"]):
            return r
    return None


class Local:
    """Opening-local frame: s along the wall, d across it (+ = n side), z up."""

    def __init__(self, o, n=None):
        self.c = Vector(o["c"])
        self.u = Vector(o["u"])
        self.n = Vector(n) if n is not None else Vector((-o["u"][1], o["u"][0]))

    def p(self, s, d, z):
        v = self.c + self.u * s + self.n * d
        return (v.x, v.y, z)

    def box(self, bm, s0, s1, d0, d1, z0, z1):
        vs = [bm.verts.new(self.p(s, d, z)) for z in (z0, z1) for (s, d) in ((s0, d0), (s1, d0), (s1, d1), (s0, d1))]
        for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            bm.faces.new([vs[i] for i in idx])


def finish(name, bm, c):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, c)


# ------------------------------------------------------------------ windows
def build_window(o):
    L = Local(o, o["n_out"])
    w, t, z0, z1 = o["w"], o["t"], o["sill"], o["head"]
    dc = t / 2 - 0.075                      # frame centre, set back from the outside face
    fd, fw = 0.045, 0.05                    # half depth, frame bar width
    bmf, bmg = bmesh.new(), bmesh.new()
    L.box(bmf, -w / 2, -w / 2 + fw, dc - fd, dc + fd, z0, z1)
    L.box(bmf, w / 2 - fw, w / 2, dc - fd, dc + fd, z0, z1)
    L.box(bmf, -w / 2 + fw, w / 2 - fw, dc - fd, dc + fd, z0, z0 + fw)
    L.box(bmf, -w / 2 + fw, w / 2 - fw, dc - fd, dc + fd, z1 - fw, z1)
    units = max(1, round(w / 1.15))
    inner = w - 2 * fw
    uw = inner / units
    gridded = o["exterior"] and o["n_out"][1] < -0.5 and o["type"] in ("window_low", "window_small")
    for k in range(units):
        a = -w / 2 + fw + k * uw
        b = a + uw
        if k > 0:
            L.box(bmf, a - 0.03, a + 0.03, dc - fd, dc + fd, z0 + fw, z1 - fw)
            a += 0.03
        if k < units - 1:
            b -= 0.03
        sb = 0.035                           # sash bar
        L.box(bmf, a, a + sb, dc - 0.025, dc + 0.025, z0 + fw, z1 - fw)
        L.box(bmf, b - sb, b, dc - 0.025, dc + 0.025, z0 + fw, z1 - fw)
        L.box(bmf, a + sb, b - sb, dc - 0.025, dc + 0.025, z0 + fw, z0 + fw + sb)
        L.box(bmf, a + sb, b - sb, dc - 0.025, dc + 0.025, z1 - fw - sb, z1 - fw)
        L.box(bmg, a + sb, b - sb, dc - 0.004, dc + 0.004, z0 + fw + sb, z1 - fw - sb)
        if gridded:
            gh = z1 - z0 - 2 * (fw + sb)
            rows = 3 if gh > 1.4 else 2
            for r in range(1, rows):
                zz = z0 + fw + sb + gh * r / rows
                L.box(bmf, a + sb, b - sb, dc - 0.012, dc + 0.012, zz - 0.011, zz + 0.011)
            mid = (a + b) / 2
            L.box(bmf, mid - 0.011, mid + 0.011, dc - 0.012, dc + 0.012, z0 + fw + sb, z1 - fw - sb)
    finish("GEO-winframe_" + o["name"], bmf, col_win)
    finish("GEO-glass_" + o["name"], bmg, col_win)
    # interior stool / exterior sill board
    bms = bmesh.new()
    L.box(bms, -w / 2 - 0.04, w / 2 + 0.04, -t / 2 - 0.035, dc - fd, z0 - 0.03, z0)
    finish("GEO-winstool_" + o["name"], bms, col_win)


def build_slider(o):
    L = Local(o, o["n_out"])
    w, t, z1 = o["w"], o["t"], o["head"]
    dc = t / 2 - 0.09
    bmf, bmg = bmesh.new(), bmesh.new()
    fw = 0.05
    L.box(bmf, -w / 2, -w / 2 + fw, dc - 0.07, dc + 0.07, 0, z1)
    L.box(bmf, w / 2 - fw, w / 2, dc - 0.07, dc + 0.07, 0, z1)
    L.box(bmf, -w / 2 + fw, w / 2 - fw, dc - 0.07, dc + 0.07, z1 - fw, z1)
    L.box(bmf, -w / 2 + fw, w / 2 - fw, dc - 0.07, dc + 0.07, 0, 0.02)
    panels = max(2, round(w / 1.25))
    pw = (w - 2 * fw) / panels
    for k in range(panels):
        a = -w / 2 + fw + k * pw
        b = a + pw + (0.03 if k < panels - 1 else 0)
        dd = dc + (0.028 if k % 2 else -0.028)
        st = 0.055
        L.box(bmf, a, a + st, dd - 0.022, dd + 0.022, 0.02, z1 - fw)
        L.box(bmf, b - st, b, dd - 0.022, dd + 0.022, 0.02, z1 - fw)
        L.box(bmf, a + st, b - st, dd - 0.022, dd + 0.022, 0.02, 0.02 + 0.09)
        L.box(bmf, a + st, b - st, dd - 0.022, dd + 0.022, z1 - fw - st, z1 - fw)
        L.box(bmg, a + st, b - st, dd - 0.004, dd + 0.004, 0.11, z1 - fw - st)
    finish("GEO-winframe_" + o["name"], bmf, col_win)
    finish("GEO-glass_" + o["name"], bmg, col_win)


# ------------------------------------------------------------------ doors
def leaf_mesh(W, Ht, style, arch_rise=0.0):
    """Door leaf in hinge-local coords: x 0..W, y -0.02..0.02, z 0..Ht. Returns (bm_solid, bm_glass)."""
    bm, bg = bmesh.new(), bmesh.new()

    def bx(b, x0, x1, y0, y1, z0, z1):
        vs = [b.verts.new((x, y, z)) for z in (z0, z1) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            b.faces.new([vs[i] for i in idx])
    st = 0.115 if style == "shaker" else 0.07
    th = 0.02
    bx(bm, 0, st, -th, th, 0, Ht)
    bx(bm, W - st, W, -th, th, 0, Ht)
    bx(bm, st, W - st, -th, th, Ht - st, Ht)
    bx(bm, st, W - st, -th, th, 0, st * (2.0 if style == "shaker" else 1.4))
    if style == "shaker":
        mid = Ht * 0.38
        bx(bm, st, W - st, -th, th, mid - st / 2, mid + st / 2)
        bx(bm, st, W - st, -0.008, 0.008, st * 2.0, mid - st / 2)
        bx(bm, st, W - st, -0.008, 0.008, mid + st / 2, Ht - st)
    else:
        z0 = st * 1.4
        bx(bg, st, W - st, -0.004, 0.004, z0, Ht - st)
        rows = 4 if style == "steel" else (3 if style == "oakglass" else 0)
        for r in range(1, rows):
            zz = z0 + (Ht - st - z0) * r / rows
            bx(bm, st, W - st, -0.012, 0.012, zz - 0.012, zz + 0.012)
        if style in ("steel", "oakglass") and W > 0.6:
            bx(bm, W / 2 - 0.012, W / 2 + 0.012, -0.012, 0.012, z0, Ht - st)
    return bm, bg


def handle_mesh(W, side=1):
    bm = bmesh.new()
    for sgn in (-1, 1):
        y = sgn * 0.02
        m1 = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.026, radius2=0.026, depth=0.008)
        for v in m1["verts"]:
            x, yy, z = v.co
            v.co = (W - 0.07 + x, y + sgn * 0.004 + 0 * yy, 1.0 + yy) if False else (W - 0.07 + x, y + sgn * z, 1.0 + yy)
        m2 = bmesh.ops.create_cube(bm, size=1.0)
        for v in m2["verts"]:
            v.co = (W - 0.07 - 0.055 + v.co.x * 0.13, y + sgn * 0.045 + v.co.y * 0.016, 1.0 + v.co.z * 0.016)
        m3 = bmesh.ops.create_cube(bm, size=1.0)
        for v in m3["verts"]:
            v.co = (W - 0.07 + v.co.x * 0.016, y + sgn * 0.025 + v.co.y * 0.05, 1.0 + v.co.z * 0.016)
    return bm


def place_leaf(name, bm, bg, hinge_xy, base_dir, angle, hw=True, W=0.8):
    """Leaf origin at the hinge; closed leaf lies along base_dir; angle opens it (radians, CCW)."""
    ob = finish("GEO-doorleaf_" + name, bm, col_door)
    rot = math.atan2(base_dir[1], base_dir[0]) + angle
    ob.location = (hinge_xy[0], hinge_xy[1], 0.012)
    ob.rotation_euler = (0, 0, rot)
    if bg is not None and len(bg.verts):
        g = finish("GEO-glass_door_" + name, bg, col_door)
        g.parent = ob
    elif bg is not None:
        bg.free()
    if hw:
        h = finish("GEO-doorhw_" + name, handle_mesh(W), col_door)
        h.parent = ob
    return ob


def ray_dist(origin, direction, maxd=3.0):
    hit, loc, nrm, idx = walls.ray_cast(Vector(origin), Vector(direction).normalized(), distance=maxd)
    return (Vector(loc) - Vector(origin)).length if hit else maxd


def jamb_and_casing(o, L, casing=True):
    w, t, z1 = o["w"], o["t"], o["head"]
    bm = bmesh.new()
    jt = 0.019
    L.box(bm, -w / 2, -w / 2 + jt, -t / 2 - 0.002, t / 2 + 0.002, 0, z1)
    L.box(bm, w / 2 - jt, w / 2, -t / 2 - 0.002, t / 2 + 0.002, 0, z1)
    L.box(bm, -w / 2 + jt, w / 2 - jt, -t / 2 - 0.002, t / 2 + 0.002, z1 - jt, z1)
    if casing:
        cw, ct = 0.09, 0.019
        for sgn in (-1, 1):
            d0, d1 = (t / 2, t / 2 + ct) if sgn > 0 else (-t / 2 - ct, -t / 2)
            L.box(bm, -w / 2 - cw + 0.006, -w / 2 + 0.006, d0, d1, 0, z1 + cw - 0.006)
            L.box(bm, w / 2 - 0.006, w / 2 + cw - 0.006, d0, d1, 0, z1 + cw - 0.006)
            L.box(bm, -w / 2 + 0.006, w / 2 - 0.006, d0, d1, z1 - 0.006, z1 + cw - 0.006)
    finish("GEO-jamb_" + o["name"], bm, col_door)


def build_door(o):
    L = Local(o)
    w, t, z1 = o["w"], o["t"], o["head"]
    kind = o["type"]
    c, u, n = L.c, L.u, L.n
    ra = room_at(tuple(c + n * (t / 2 + 0.25)))
    rb = room_at(tuple(c - n * (t / 2 + 0.25)))
    na = ra["name"] if ra else "outside"
    nb = rb["name"] if rb else "outside"

    def is_closet(nm):
        return any(k in nm for k in CLOSETS)
    # side the leaf swings into: +1 = n side, -1 = -n side
    if is_closet(na) and not is_closet(nb):
        into, closed = -1, True
    elif is_closet(nb) and not is_closet(na):
        into, closed = 1, True
    elif na in CIRC and nb not in CIRC:
        into, closed = -1, False
    elif nb in CIRC and na not in CIRC:
        into, closed = 1, False
    else:
        aa = ra["area"] if ra else 0
        ab = rb["area"] if rb else 0
        into, closed = (1 if aa >= ab else -1), False
    if "garage" in (na, nb) or "outside" in (na, nb) or o["name"] in KEEP_CLOSED:
        closed = True
    if kind == "door_arch":
        closed = False
    style = {"ddoor_glass": "steel", "door_arch": "oakglass"}.get(kind, "shaker")
    jamb_and_casing(o, L, casing=(kind != "door_arch"))
    Ht = z1 - 0.03
    inset = t / 2 - 0.03                       # leaf plane sits near the swing-side face
    if kind in ("ddoor", "ddoor_glass"):
        W = (w - 0.044) / 2
        for sgn in (-1, 1):
            hinge = c + u * (sgn * (w / 2 - 0.02)) + n * (into * inset)
            base = -u * sgn                      # closed leaf points to the centre
            ang = 0.0 if closed else math.radians(88) * (-sgn * into)
            bm, bg = leaf_mesh(W, Ht, style)
            if sgn > 0:                          # mirror so the stile/handle sits at the meeting edge
                pass
            place_leaf(f"{o['name']}_{'a' if sgn < 0 else 'b'}", bm, bg, hinge, base, ang, W=W)
        return
    W = w - 0.044
    # choose the hinge jamb whose open leaf ends up closest to a wall
    best = None
    for sgn in (-1, 1):
        hinge = c + u * (sgn * (w / 2 - 0.02)) + n * (into * inset)
        mid = hinge + n * (into * (W * 0.6))
        dist = ray_dist((mid.x, mid.y, 1.0), tuple(u * sgn) + (0.0,))
        if best is None or dist < best[0]:
            best = (dist, sgn, hinge)
    _, sgn, hinge = best
    base = -u * sgn
    ang = 0.0 if closed else math.radians(86) * (-sgn * into)
    bm, bg = leaf_mesh(W, Ht, style)
    place_leaf(o["name"], bm, bg, hinge, base, ang, W=W)


def build_extdoor(o):
    L = Local(o, o["n_out"])
    w, t, z1 = o["w"], o["t"], o["head"]
    dc = t / 2 - 0.08
    bm = bmesh.new()
    fw = 0.05
    L.box(bm, -w / 2, -w / 2 + fw, dc - 0.06, dc + 0.06, 0, z1)
    L.box(bm, w / 2 - fw, w / 2, dc - 0.06, dc + 0.06, 0, z1)
    L.box(bm, -w / 2 + fw, w / 2 - fw, dc - 0.06, dc + 0.06, z1 - fw, z1)
    finish("GEO-winframe_" + o["name"], bm, col_win)
    W = w - 2 * fw - 0.01
    lm, lg = leaf_mesh(W, z1 - fw - 0.02, "glass")
    hinge = L.c + L.u * (-w / 2 + fw + 0.005) + L.n * dc
    ob = place_leaf(o["name"], lm, lg, hinge, L.u, 0.0, W=W)
    ob.name = "GEO-doorleaf_dark_" + o["name"]


def arch_ring(w, spring, top, band, seg=24):
    """Closed profile of an arched frame of given band width (outer + inner loops as one polygon)."""
    outer = [(-w / 2, 0), (-w / 2, spring)]
    for i in range(1, seg):
        a = math.pi * i / seg
        outer.append((-w / 2 * math.cos(a), spring + (top - spring) * math.sin(a)))
    outer += [(w / 2, spring), (w / 2, 0)]
    wi, ti = w - 2 * band, top - band
    inner = [(wi / 2, 0), (wi / 2, spring)]
    for i in range(1, seg):
        a = math.pi * i / seg
        inner.append((wi / 2 * math.cos(a), spring + (ti - spring) * math.sin(a)))
    inner += [(-wi / 2, spring), (-wi / 2, 0)]
    return outer + inner


def build_frontdoor(o):
    L = Local(o, o["n_out"])
    w, t, top = o["w"], o["t"], o["head"]
    sp = arch_spring(o)
    dc = t / 2 - 0.08
    Lf = Local(o, o["n_out"])
    Lf.c = L.c + L.n * dc
    bm = bmesh.new()
    add_profile(bm, tuple(Lf.c), tuple(L.u), 0.06, arch_ring(w, sp, top, 0.06))
    # leaves: steel stiles + muntins, kept closed
    wi = w - 0.12
    L.box(bm, -0.03, 0.03, dc - 0.03, dc + 0.03, 0, top - 0.06)                 # meeting stile
    for sgn in (-1, 1):
        L.box(bm, sgn * (wi / 2 - 0.05) - 0.025, sgn * (wi / 2 - 0.05) + 0.025, dc - 0.025, dc + 0.025, 0, sp)
        L.box(bm, sgn * wi / 4 - 0.01, sgn * wi / 4 + 0.01, dc - 0.012, dc + 0.012, 0.25, top - 0.25)
        x0, x1 = (0.03, wi / 2) if sgn > 0 else (-wi / 2, -0.03)
        L.box(bm, x0, x1, dc - 0.025, dc + 0.025, 0, 0.25)
    for zz in (0.25 + (sp - 0.25) * k / 3 for k in range(1, 4)):
        L.box(bm, -wi / 2, wi / 2, dc - 0.012, dc + 0.012, zz - 0.01, zz + 0.01)
    finish("GEO-winframe_" + o["name"], bm, col_win)
    bg = bmesh.new()
    inner = [(-wi / 2, 0.25), (-wi / 2, sp)]
    for i in range(1, 24):
        a = math.pi * i / 24
        inner.append((-wi / 2 * math.cos(a), sp + (top - 0.06 - sp) * math.sin(a)))
    inner += [(wi / 2, sp), (wi / 2, 0.25)]
    add_profile(bg, tuple(Lf.c), tuple(L.u), 0.004, inner)
    finish("GEO-glass_" + o["name"], bg, col_win)
    bh = bmesh.new()
    for sgn in (-1, 1):
        L.box(bh, sgn * 0.07 - 0.012, sgn * 0.07 + 0.012, dc - 0.07, dc + 0.07, 0.95, 1.25)
    finish("GEO-doorhw_" + o["name"], bh, col_door)


def build_garage(o):
    L = Local(o, o["n_out"])
    w, t, z1 = o["w"], o["t"], o["head"]
    bm = bmesh.new()
    dc = t / 2 - 0.06
    rows = 4
    ph = z1 / rows
    for r in range(rows):
        L.box(bm, -w / 2 + 0.01, w / 2 - 0.01, dc - 0.025, dc + 0.025, r * ph + 0.006, (r + 1) * ph - 0.006)
    cols_n = max(2, round(w / 1.4))
    for k in range(cols_n + 1):
        s = -w / 2 + 0.03 + (w - 0.06) * k / cols_n
        L.box(bm, s - 0.03, s + 0.03, dc + 0.025, dc + 0.04, 0.02, z1 - 0.02)
    for r in range(rows + 1):
        zz = min(max(r * ph, 0.05), z1 - 0.05)
        L.box(bm, -w / 2 + 0.03, w / 2 - 0.03, dc + 0.025, dc + 0.04, zz - 0.04, zz + 0.04)
    finish("GEO-garagedoor_" + o["name"], bm, col_door)


count = {}
for o in S["openings"]:
    k = o["type"]
    if k.startswith("window"):
        build_window(o)
    elif k == "slider":
        build_slider(o)
    elif k in ("door", "ddoor", "ddoor_glass", "door_arch"):
        build_door(o)
    elif k == "extdoor":
        build_extdoor(o)
    elif k == "frontdoor":
        build_frontdoor(o)
    elif k == "garage":
        build_garage(o)
    else:
        continue
    count[k] = count.get(k, 0) + 1
print(count, "objects:", len(col_win.objects), len(col_door.objects))
