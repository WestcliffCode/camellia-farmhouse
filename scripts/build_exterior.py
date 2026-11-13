"""Stage 2d: roofs, gable walls, dormers, chimneys, porches and site slab."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-exterior")
col = get_col("COL-exterior")
K = json.loads(bpy.context.scene["camellia_shell"])
PITCH = 10.0 / 12.0
RT = 0.22          # roof slab thickness
WT = 0.11          # gable wall thickness

roof = bmesh.new()       # shingle roofs
metal = bmesh.new()      # standing-seam porch roofs
gwall = bmesh.new()      # gable / upper walls (clad later)


def slab(bm, poly, holes, zfun, thick=RT):
    n0 = len(bm.verts)
    add_prism(bm, poly, holes, 0.0, 1.0)
    bm.verts.ensure_lookup_table()
    for v in list(bm.verts)[n0:]:
        v.co.z = zfun(v.co.x, v.co.y) - (1.0 - v.co.z) * thick


def rect_ccw(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rect_cw(x0, y0, x1, y1):
    return [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]


def wall_piece(c, u, sa, sb, zlo, ztop, t=WT):
    """Vertical wall slab between s=sa..sb (along u from c), from zlo up to ztop(s)."""
    pts = [(sa, zlo), (sb, zlo)]
    zb, za = ztop(sb), ztop(sa)
    if zb > zlo + 1e-4:
        pts.append((sb, zb))
    if sa < 0 < sb:
        pts.append((0.0, ztop(0.0)))
    if za > zlo + 1e-4:
        pts.append((sa, za))
    if len(pts) >= 3:
        add_profile(gwall, c, u, t / 2, pts)


def gable(x0, y0, x1, y1, axis, plate, pitch=PITCH, over=0.45, rake=0.30, ends=(True, True),
          holes_a=(), holes_b=(), base=None, cut=None, bm=None):
    """Gable roof. axis 'y': ridge runs along Y, slopes fall to x0 (a) and x1 (b).
    ends = build a gable wall + rake overhang at the low / high end of the ridge.
    cut = (end_index, sa, sb, ztop) leaves a passage in that gable wall."""
    bm = bm or roof
    base = CEIL if base is None else base
    oa, ob = (over, over) if isinstance(over, (int, float)) else over
    wall_plate = plate
    plate = plate + RT        # heel: the slab underside meets the wall plate, so nothing dips below a ceiling
    if axis == "y":
        xm, half = (x0 + x1) / 2, (x1 - x0) / 2
        ya, yb = y0 - (rake if ends[0] else 0), y1 + (rake if ends[1] else 0)
        slab(bm, rect_ccw(x0 - oa, ya, xm, yb), list(holes_a), lambda x, y: plate + (x - x0) * pitch)
        slab(bm, rect_ccw(xm, ya, x1 + ob, yb), list(holes_b), lambda x, y: plate + (x1 - x) * pitch)
        for i, yy in enumerate((y0, y1)):
            if ends[i]:
                c = (xm, yy + (WT / 2 if i == 0 else -WT / 2))
                _gable_wall(c, (1, 0), half, wall_plate, pitch, base, cut if cut and cut[0] == i else None)
    else:
        ym, half = (y0 + y1) / 2, (y1 - y0) / 2
        xa, xb = x0 - (rake if ends[0] else 0), x1 + (rake if ends[1] else 0)
        slab(bm, rect_ccw(xa, y0 - oa, xb, ym), list(holes_a), lambda x, y: plate + (y - y0) * pitch)
        slab(bm, rect_ccw(xa, ym, xb, y1 + ob), list(holes_b), lambda x, y: plate + (y1 - y) * pitch)
        for i, xx in enumerate((x0, x1)):
            if ends[i]:
                c = (xx + (WT / 2 if i == 0 else -WT / 2), ym)
                _gable_wall(c, (0, 1), half, wall_plate, pitch, base, cut if cut and cut[0] == i else None)
    return plate + half * pitch


def _gable_wall(c, u, half, plate, pitch, base, cut):
    def ztop(s):
        return plate + 0.12 + (half - abs(s)) * pitch
    lim = half - max(0.0, (base - (plate + 0.12)) / pitch) - 0.001
    if cut is None:
        wall_piece(c, u, -lim, lim, base, ztop)
    else:
        _, sa, sb, zc = cut
        wall_piece(c, u, -lim, sa, base, ztop)
        wall_piece(c, u, sa, sb, zc, ztop)
        wall_piece(c, u, sb, lim, base, ztop)


def band(x0, y0, x1, y1, z0, z1):
    add_prism(gwall, rect_ccw(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), [], z0, z1)


# ------------------------------------------------------------------ key plan lines (m)
XL = 0.0
X_WING_L = PX(634, 0)[0]          # 7.644  right edge of the bedroom wing
X_PORT0, X_PORT1 = PX(906, 0)[0], PX(1176, 0)[0]
X_DIN = PX(1225, 0)[0]            # 15.682 dining left wall
GW = K["GW"]                      # 18.701 garage west wall, outer
X_HALL = PX(1612, 0)[0]           # 20.946
X_PS0, X_PS1 = PX(1599, 0)[0], PX(2009, 0)[0]
XR = PX(2009, 0)[0]               # 26.345
Y_FRONT = PX(0, 1780)[1]          # 2.611 front wall of foyer / bed 2 / office
Y_JJ = PX(0, 1903)[1]             # 0.938
Y_B3 = PX(0, 1949)[1]             # 0.313
Y_FAMB = PX(0, 948)[1]            # 13.927 family back wall
Y_GAME = PX(0, 731)[1]            # 16.879
Y_DIN = PX(0, 400)[1]             # 21.381
Y_PSB = PX(0, 53)[1]              # 26.100
PL1 = 4.27                        # main block plate (14 ft)

# ------------------------------------------------------------------ roofs
# G1 main block, ridge E-W; east gable wall leaves the stair passage open
yc1 = (Y_FRONT + Y_FAMB) / 2
RIDGE1 = gable(X_WING_L, Y_FRONT, GW + 0.164, Y_FAMB, "x", PL1,
               holes_a=[rect_cw(X_PORT0 + 0.02, Y_FRONT - 0.6, X_PORT1 - 0.02, 4.3)],   # foyer vault rises through here
               cut=(1, K["YA0"] - yc1, K["YA1"] - yc1, K["ZA"] + 0.05))
band(X_WING_L, Y_FRONT, GW, Y_FRONT + WT, CEIL, PL1 + 0.1)            # front band above the porch roof
band(X_WING_L, Y_FAMB - WT, X_DIN, Y_FAMB, CEIL, PL1 + 0.1)           # back band above the porch roof
# G2 bedroom wing, ridge N-S, and the bedroom-3 brick gable in front of it
gable(XL, Y_JJ, X_WING_L, Y_GAME, "y", CEIL, over=(0.45, 0.0))
gable(PX(285, 0)[0], Y_B3, X_WING_L, Y_JJ, "y", CEIL, ends=(True, False))
# G3 garage / service wing, ridge N-S, with cut-outs for the stair alcove and the bonus dormer
Y_BUMP = PX(0, 1001)[1] - 0.1          # the bath / closet bump-out starts here; no east eave beyond it
gable(GW, Y_JJ, XR, Y_BUMP, "y", CEIL, over=(0.0, 0.45), ends=(True, False),
      holes_a=[rect_cw(GW + 0.17, K["YA0"] - 0.14, K["XA"] + 0.05, K["YA1"] + 0.14)],
      holes_b=[rect_cw(K["XDS"] - 0.05, K["YD0"] - 0.14, XR + 0.6, K["YD1"] + 0.14)])
gable(GW, Y_BUMP, XR, Y_DIN, "y", CEIL, over=(0.0, 0.0), ends=(False, True))
gable(GW, Y_B3, PX(1811, 0)[0], Y_JJ, "y", CEIL, ends=(True, False))      # garage front brick gable
# G4 primary suite
gable(X_PS0, Y_DIN - 0.4, X_PS1, Y_PSB, "y", CEIL, over=(0.0, 0.45), ends=(False, True))
# G5 dining / kitchen wing
gable(X_DIN, 12.4, X_HALL, Y_DIN, "y", CEIL, over=(0.0, 0.0), ends=(False, True))
# G6 outdoor living, low gable
gable(PX(1035, 0)[0] - 0.15, Y_DIN, X_PS0, PX(0, 70)[1] + 0.15, "x", CEIL + 0.25, pitch=5.0 / 12.0,
      ends=(True, False), base=CEIL + 0.25)
# portico cross gable over the foyer vault
PLP = 4.75
gable(X_PORT0, 0.0, X_PORT1, 6.8, "y", PLP, ends=(True, False))
band(X_PORT0, 0.0, X_PORT0 + WT, Y_FRONT, CEIL, PLP + 0.1)
band(X_PORT1 - WT, 0.0, X_PORT1, Y_FRONT, CEIL, PLP + 0.1)
# stair connector cross gable on the garage roof
PLC = 5.5
gable(GW + 0.16, K["YA0"] - 0.2, K["XA"] + 1.1, K["YA1"] + 0.2, "x", PLC, over=0.2, ends=(False, False))
for yy in (K["YA0"] - 0.2 + WT / 2, K["YA1"] + 0.2 - WT / 2):
    xe = GW + (PLC - CEIL) / PITCH
    add_profile(gwall, (GW, yy), (1, 0), WT / 2, [(0.16, CEIL + 0.14), (xe - GW, PLC), (0.16, PLC)])

# front dormers on the main roof
for cx in (13.18 - 3.6, 13.18 + 3.6):
    yf = 3.45
    zroof = PL1 + RT + (yf - Y_FRONT) * PITCH
    pld = zroof + 1.25
    gable(cx - 0.85, yf, cx + 0.85, yf + 2.6, "y", pld, over=0.2, rake=0.25, ends=(True, False), base=zroof - 0.25)
    for sx in (cx - 0.85 + WT / 2, cx + 0.85 - WT / 2):                 # cheeks
        add_profile(gwall, (sx, yf), (0, 1), WT / 2,
                    [(0.0, zroof - 0.25), ((pld - zroof) / PITCH, pld), (0.0, pld)])
    # dormer window
    add_prism(gwall, rect_ccw(cx - 0.45, yf - 0.03, cx + 0.45, yf + 0.02), [], zroof + 0.15, pld + 0.1)

# bonus-room shed dormer (east slope of the garage roof)
YD0, YD1, XD, ZF, ZD = K["YD0"], K["YD1"], K["XD"], K["ZF"], K["ZD"]
slab(roof, rect_ccw(K["XDS"] - 0.9, YD0 - 0.45, XD + 0.6, YD1 + 0.45), [],
     lambda x, y: ZD + 0.55 - (x - K["XDS"]) * 0.11, 0.18)
NW, WW = 4, 0.80
gap = (YD1 - YD0 - NW * WW) / (NW + 1)
edges = [YD0 - 0.14]
for k in range(NW):
    edges += [YD0 + gap + k * (WW + gap), YD0 + gap + k * (WW + gap) + WW]
edges.append(YD1 + 0.14)
for k in range(len(edges) - 1):
    ya, yb = edges[k], edges[k + 1]
    if k % 2 == 0:
        band(XD, ya, XD + 0.14, yb, CEIL - 0.3, ZD + 0.2)
    else:
        band(XD, ya, XD + 0.14, yb, CEIL - 0.3, K["WS"])
        band(XD, ya, XD + 0.14, yb, K["WH"], ZD + 0.2)
for yy in (YD0 - 0.07, YD1 + 0.07):                                       # cheeks
    add_profile(gwall, (K["XDS"], yy), (1, 0), 0.07,
                [(0.0, ZD + 0.2), (XD + 0.14 - K["XDS"], ZD + 0.2), (XD + 0.14 - K["XDS"], CEIL + 0.15),
                 (K["XE"] - K["XDS"] + 0.3, K["ZK"] + 0.3)])

# primary bath bump-out: low shed roof (brick block on the right elevation)
XB0, XB1 = XR - 0.2, PX(2070, 0)[0]
slab(roof, rect_ccw(XB0, PX(0, 1001)[1] - 0.3, XB1 + 0.35, PX(0, 427)[1] + 0.3), [],
     lambda x, y: CEIL + 0.75 - (x - XB0) * 0.25, 0.18)
band(XB1 - WT, PX(0, 1001)[1], XB1, PX(0, 427)[1], CEIL, CEIL + 0.45)

# ------------------------------------------------------------------ porches
porch = bmesh.new()      # slabs / steps (concrete)
timber = bmesh.new()     # posts and beams
pceil = bmesh.new()      # porch ceilings (wood)

Y_PORCH = 0.55
for xa, xb in ((X_WING_L, X_PORT0), (X_PORT1, GW)):
    add_prism(porch, rect_ccw(xa, Y_PORCH, xb, Y_FRONT), [], -0.30, 0.0)
    add_prism(pceil, rect_ccw(xa, Y_PORCH + 0.1, xb, Y_FRONT), [], CEIL, CEIL + 0.02)
    add_prism(timber, rect_ccw(xa, Y_PORCH + 0.1, xb, Y_PORCH + 0.3), [], CEIL - 0.3, CEIL)   # beam
    slab(metal, rect_ccw(xa, Y_PORCH - 0.25, xb, Y_FRONT), [],
         lambda x, y: 3.25 + (y - Y_PORCH) * 0.33, 0.10)
for px in (650, 887, 1193, 1427):
    x = PX(px, 0)[0]
    add_prism(timber, rect_ccw(x - 0.1, Y_PORCH + 0.1, x + 0.1, Y_PORCH + 0.3), [], 0.0, CEIL - 0.3)

BP = [(5.277, Y_FAMB), (12.26, Y_FAMB), (X_DIN, 17.35), (X_DIN, Y_DIN), (X_PS0, Y_DIN),
      (X_PS0, 25.95), (13.10, 25.95), (13.10, 18.53), (11.17, 16.60), (5.277, 16.60)]
add_prism(porch, BP, [], -0.30, 0.0)
add_prism(pceil, BP, [], CEIL, CEIL + 0.02)
# lean-to roof behind the main block and over the kitchen triangle
slab(roof, [(5.0, Y_FAMB), (X_DIN + 0.1, Y_FAMB), (X_DIN + 0.1, 17.6), (12.6, 17.6), (11.3, 16.95), (5.0, 16.95)],
     [], lambda x, y: 4.18 - (y - Y_FAMB) * 0.22, 0.18)
slab(roof, [(11.0, 16.6), (X_DIN + 0.1, 16.6), (X_DIN + 0.1, Y_DIN + 0.2), (12.8, Y_DIN + 0.2), (12.8, 18.6)],
     [], lambda x, y: CEIL + 0.42 - (X_DIN - x) * 0.05, 0.18)
POSTS = [(8.2, 16.50), (11.167, 16.525), (13.098, 18.484), (13.098, 22.1), (13.098, 25.72), (16.9, 25.80)]
for x, y in POSTS:
    add_prism(timber, rect_ccw(x - 0.1, y - 0.1, x + 0.1, y + 0.1), [], 0.0, CEIL - 0.28)
BEAMS = [((5.277, 16.50), (11.167, 16.525)), ((11.167, 16.525), (13.098, 18.484)),
         ((13.098, 18.484), (13.098, 25.72)), ((13.098, 25.80), (X_PS0, 25.80))]
for a, b in BEAMS:
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    add_box(timber, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ((b[0] - a[0]) / L, (b[1] - a[1]) / L), L / 2 + 0.1, 0.1,
            CEIL - 0.28, CEIL)
    add_box(timber, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ((b[0] - a[0]) / L, (b[1] - a[1]) / L), L / 2 + 0.1, 0.03,
            CEIL, CEIL + 0.34)                                               # fascia up to the roof

# ------------------------------------------------------------------ chimneys
chim = bmesh.new()
add_prism(chim, rect_ccw(7.15, 9.95, 8.05, 11.0), [], CEIL, 10.3)
add_prism(chim, rect_ccw(7.08, 9.88, 8.12, 11.07), [], 10.3, 10.42)
add_prism(chim, rect_ccw(20.06, 23.05, 20.95, 24.25), [], CEIL, 7.9)
add_prism(chim, rect_ccw(19.99, 22.98, 21.02, 24.32), [], 7.9, 8.02)

# ------------------------------------------------------------------ objects
for nm, b in (("GEO-roof_shingle", roof), ("GEO-roof_metal", metal), ("GEO-upper_walls", gwall),
              ("GEO-porch_slab", porch), ("GEO-porch_timber", timber), ("GEO-porch_ceiling", pceil),
              ("GEO-chimneys", chim)):
    ob = new_obj(nm, b, col)
    fix_normals(ob)
print("ridge main %.2f" % RIDGE1, [(o.name, len(o.data.polygons)) for o in col.objects])
