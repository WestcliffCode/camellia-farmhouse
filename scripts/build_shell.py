"""Stage 2c: non-flat ceilings, garage lid, stair, stairwell and bonus-room interior shell."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-shell")
col = get_col("COL-shell")
ccol = bpy.data.collections["COL-ceilings"]
PITCH = 10.0 / 12.0

# ---------------------------------------------------------------- foyer barrel vault (springs at 14 ft)
x0, y0, x1, y1 = room_bounds("foyer")
cx, mid = (x0 + x1) / 2, ((x0 + x1) / 2, (y0 + y1) / 2, 3.5)
SPRING, RISE = 4.27, 1.05
bm = bmesh.new()
for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
    face_in(bm, [(a[0], a[1], CEIL), (b[0], b[1], CEIL), (b[0], b[1], SPRING), (a[0], a[1], SPRING)], mid)
SEG = 28
arc = [(cx - (x1 - x0) / 2 * math.cos(math.pi * i / SEG), SPRING + RISE * math.sin(math.pi * i / SEG)) for i in range(SEG + 1)]
for i in range(SEG):
    (xa, za), (xb, zb) = arc[i], arc[i + 1]
    f = face_in(bm, [(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], mid)
    if f:
        f.smooth = True
for yy in (y0, y1):
    face_in(bm, [(x, yy, z) for x, z in arc], mid)
new_obj("GEO-ceiling_foyer", bm, ccol)
FOYER = (x0, y0, x1, y1)

# ---------------------------------------------------------------- cathedral ceilings (vault off 10 ft)
for nm, pitch in (("primary_suite", 5.0 / 12.0), ("game_room", 5.0 / 12.0)):
    x0, y0, x1, y1 = room_bounds(nm)
    cx = (x0 + x1) / 2
    zr = CEIL + (x1 - x0) / 2 * pitch
    mid = (cx, (y0 + y1) / 2, 2.0)
    bm = bmesh.new()
    face_in(bm, [(x0, y0, CEIL), (cx, y0, zr), (cx, y1, zr), (x0, y1, CEIL)], mid)
    face_in(bm, [(x1, y0, CEIL), (cx, y0, zr), (cx, y1, zr), (x1, y1, CEIL)], mid)
    for yy in (y0, y1):
        face_in(bm, [(x0, yy, CEIL), (x1, yy, CEIL), (cx, yy, zr)], mid)
    new_obj("GEO-ceiling_" + nm, bm, ccol)

# ---------------------------------------------------------------- tray ceilings (boxed to 11 ft)
TRAY = CEIL + FT


def tray(room_name, ring):
    """Rebuild a flat ceiling with a rectangular recess. ring = 4 (x, y) corners."""
    old = bpy.data.objects.get("GEO-ceiling_" + room_name)
    if old:
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        bpy.data.meshes.remove(me)
    r = room(room_name)
    area = sum(ring[i][0] * ring[(i + 1) % 4][1] - ring[(i + 1) % 4][0] * ring[i][1] for i in range(4))
    cw = ring if area < 0 else ring[::-1]
    bm = bmesh.new()
    add_prism(bm, r["outer"], list(r["holes"]) + [cw], CEIL, CEIL + 0.02)
    c = (sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4, CEIL)
    for i in range(4):
        a, b = ring[i], ring[(i + 1) % 4]
        face_in(bm, [(a[0], a[1], CEIL), (b[0], b[1], CEIL), (b[0], b[1], TRAY), (a[0], a[1], TRAY)], c)
    face_in(bm, [(p[0], p[1], TRAY) for p in ring], c)
    new_obj("GEO-ceiling_" + room_name, bm, ccol)


kc = PX(1244.5, 959)
ku, kn = (0.70711, 0.70711), (-0.70711, 0.70711)
KL, KW = 2.38, 0.95
KITCHEN_TRAY = [(kc[0] + ku[0] * a * KL + kn[0] * b * KW, kc[1] + ku[1] * a * KL + kn[1] * b * KW)
                for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
tray("great_room", KITCHEN_TRAY)
a, b = PX(1217, 1723), PX(1407, 1490)
tray("office", [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])])

# ---------------------------------------------------------------- garage lid / bonus floor
ZF = 3.10                                    # bonus-room finished floor
g = room("garage")
bm = bmesh.new()
add_prism(bm, g["outer"], g["holes"], 2.743, ZF)
new_obj("GEO-ceiling_garage", bm, ccol)

# ---------------------------------------------------------------- stair to the bonus room
SX0 = PX(1150, 0)[0]
YA0, YA1 = PX(0, 1438)[1], PX(0, 1349)[1]
GW = PX(1447, 0)[0]                          # outer face of garage west wall
NR = 17
RISER, TREAD = ZF / NR, (GW - SX0) / (NR - 1)
bm = bmesh.new()
for i in range(NR - 1):
    xa = SX0 + i * TREAD
    add_prism(bm, [(xa, YA0), (xa + TREAD, YA0), (xa + TREAD, YA1), (xa, YA1)], [], 0.0, (i + 1) * RISER)
add_prism(bm, [(GW, YA0), (GW + 0.2, YA0), (GW + 0.2, YA1), (GW, YA1)], [], 2.6, ZF)
stair = new_obj("GEO-stair", bm, col)
fix_normals(stair)

# ---------------------------------------------------------------- stairwell + bonus room shell (inward faces)
XW, XE = GW + 1.76, PX(2009, 0)[0] - 1.76    # knee walls
ZK = ZF + 1.22
XR0, XR1, ZR = 22.29, 22.76, ZF + 2.74       # flat collar
Y0, Y1 = PX(0, 1892)[1], PX(0, 1147)[1]
XB = SX0 + (CEIL - 2.2) / (RISER / TREAD)    # where stair headroom lifts above the 10 ft ceiling
ZA = 5.25                                    # stair-top / alcove ceiling
XA = XW + (ZA - ZK) / PITCH                  # where the alcove ceiling meets the west slope
YD0, YD1, XD, ZD = 3.8, 8.5, 26.0, ZF + 2.44  # dormer
XDS = XE - (ZD - ZK) / PITCH                 # where the dormer ceiling meets the east slope
ctr = ((XW + XE) / 2, (Y0 + Y1) / 2, ZF + 1.2)
bm = bmesh.new()


def q(pts, toward=ctr):
    return face_in(bm, pts, toward)


# stairwell
sc = ((XB + XA) / 2, (YA0 + YA1) / 2, 3.6)
q([(SX0 - 0.15, YA0, CEIL), (XB, YA0, CEIL), (XB, YA1, CEIL), (SX0 - 0.15, YA1, CEIL)], (XB, (YA0 + YA1) / 2, 1.0))
q([(XB, YA0, CEIL), (GW, YA0, ZA), (GW, YA1, ZA), (XB, YA1, CEIL)], sc)
q([(GW, YA0, ZA), (XA, YA0, ZA), (XA, YA1, ZA), (GW, YA1, ZA)], sc)
for yy in (YA0, YA1):
    q([(XB, yy, CEIL), (XW, yy, CEIL), (XW, yy, ZK), (XA, yy, ZA), (GW, yy, ZA)], sc)
# bonus room: west side
for ya, yb in ((Y0, YA0), (YA1, Y1)):
    q([(XW, ya, ZF), (XW, yb, ZF), (XW, yb, ZK), (XW, ya, ZK)])
    q([(XW, ya, ZK), (XW, yb, ZK), (XR0, yb, ZR), (XR0, ya, ZR)])
q([(XA, YA0, ZA), (XA, YA1, ZA), (XR0, YA1, ZR), (XR0, YA0, ZR)])
# east side
for ya, yb in ((Y0, YD0), (YD1, Y1)):
    q([(XE, ya, ZF), (XE, yb, ZF), (XE, yb, ZK), (XE, ya, ZK)])
    q([(XE, ya, ZK), (XE, yb, ZK), (XR1, yb, ZR), (XR1, ya, ZR)])
q([(XDS, YD0, ZD), (XDS, YD1, ZD), (XR1, YD1, ZR), (XR1, YD0, ZR)])
q([(XR0, Y0, ZR), (XR1, Y0, ZR), (XR1, Y1, ZR), (XR0, Y1, ZR)])
for yy in (Y0, Y1):
    q([(XW, yy, ZF), (XE, yy, ZF), (XE, yy, ZK), (XR1, yy, ZR), (XR0, yy, ZR), (XW, yy, ZK)])
# dormer
dc = ((XE + XD) / 2, (YD0 + YD1) / 2, ZF + 1.2)
q([(XDS, YD0, ZD), (XD, YD0, ZD), (XD, YD1, ZD), (XDS, YD1, ZD)], dc)
XDI = XD - 0.03                       # interior faces sit 3 cm inside the exterior dormer walls
for yy in (YD0 + 0.03, YD1 - 0.03):
    q([(XE, yy, ZF), (XD, yy, ZF), (XD, yy, ZD), (XDS, yy, ZD), (XE, yy, ZK)], dc)
NW, WW, WS, WH = 4, 0.80, ZF + 0.80, ZF + 2.05     # dormer windows
span = YD1 - YD0
gap = (span - NW * WW) / (NW + 1)
edges = [YD0]
for k in range(NW):
    edges += [YD0 + gap + k * (WW + gap), YD0 + gap + k * (WW + gap) + WW]
edges.append(YD1)
for k in range(len(edges) - 1):
    ya, yb = edges[k], edges[k + 1]
    if k % 2 == 0:
        q([(XDI, ya, ZF), (XDI, yb, ZF), (XDI, yb, ZD), (XDI, ya, ZD)], dc)
    else:
        q([(XDI, ya, ZF), (XDI, yb, ZF), (XDI, yb, WS), (XDI, ya, WS)], dc)
        q([(XDI, ya, WH), (XDI, yb, WH), (XDI, yb, ZD), (XDI, ya, ZD)], dc)
shell = new_obj("GEO-bonus_shell", bm, col)

# bonus floor finish (thin, separate object for its own material)
bm = bmesh.new()
add_prism(bm, [(XW, Y0), (XE, Y0), (XE, Y1), (XW, Y1)], [], ZF, ZF + 0.012)
add_prism(bm, [(XE, YD0), (XD, YD0), (XD, YD1), (XE, YD1)], [], ZF, ZF + 0.012)
add_prism(bm, [(GW, YA0), (XW, YA0), (XW, YA1), (GW, YA1)], [], ZF, ZF + 0.012)
new_obj("GEO-floor_bonus", bm, col)

# dormer window units
wcol = bpy.data.collections["COL-windows"]
for nm in [o.name for o in wcol.objects if "bonus_dormer" in o.name]:
    bpy.data.objects.remove(bpy.data.objects[nm], do_unlink=True)
bmf, bmg = bmesh.new(), bmesh.new()


def bx(b, xa, xb, ya, yb, za, zb):
    add_prism(b, [(xa, ya), (xb, ya), (xb, yb), (xa, yb)], [], za, zb)


for k in range(NW):
    ya = YD0 + gap + k * (WW + gap)
    yb = ya + WW
    xf0, xf1 = XD + 0.03, XD + 0.12
    bx(bmf, xf0, xf1, ya, ya + 0.045, WS, WH)
    bx(bmf, xf0, xf1, yb - 0.045, yb, WS, WH)
    bx(bmf, xf0, xf1, ya + 0.045, yb - 0.045, WS, WS + 0.045)
    bx(bmf, xf0, xf1, ya + 0.045, yb - 0.045, WH - 0.045, WH)
    bx(bmf, xf0 + 0.03, xf1 - 0.03, (ya + yb) / 2 - 0.011, (ya + yb) / 2 + 0.011, WS + 0.045, WH - 0.045)
    for r in (1, 2):
        zz = WS + (WH - WS) * r / 3
        bx(bmf, xf0 + 0.03, xf1 - 0.03, ya + 0.045, yb - 0.045, zz - 0.011, zz + 0.011)
    bx(bmg, XD + 0.07, XD + 0.078, ya + 0.045, yb - 0.045, WS + 0.045, WH - 0.045)
new_obj("GEO-winframe_bonus_dormer", bmf, wcol)
new_obj("GEO-glass_bonus_dormer", bmg, wcol)

# numbers the exterior script needs
bpy.context.scene["camellia_shell"] = json.dumps({
    "FOYER": FOYER, "SX0": SX0, "YA0": YA0, "YA1": YA1, "GW": GW, "XW": XW, "XE": XE, "ZF": ZF, "ZK": ZK,
    "ZA": ZA, "XA": XA, "YD0": YD0, "YD1": YD1, "XD": XD, "ZD": ZD, "XDS": XDS, "Y0": Y0, "Y1": Y1,
    "WS": WS, "WH": WH, "KITCHEN_TRAY": KITCHEN_TRAY})
print("shell ok", "XW %.2f XE %.2f XA %.2f XDS %.2f XB %.2f riser %.3f tread %.3f" % (XW, XE, XA, XDS, XB, RISER, TREAD))
