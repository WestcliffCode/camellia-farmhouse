"""Stage 3b: fixed millwork - base and crown, panel moulding, kitchen, coffee bar, pantry shelving,
fireplaces, foyer beam, stair rail, gable trusses and porch brackets."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-millwork")
col = get_col("COL-millwork")
K = json.loads(bpy.context.scene["camellia_shell"])
Z = Vector((0, 0, 1))

# ------------------------------------------------------------------ base and crown from the wall faces
NO_TRIM = {"garage", "portico", "stair"}
NO_CROWN = {"primary_suite", "game_room", "foyer"}
CHARCOAL = {"primary_suite", "office", "powder"}
walls = bpy.data.objects["GEO-walls"]
B = Builder("trim", get_col("COL-trim", col))
nb = nc = 0
for p in walls.data.polygons:
    n = p.normal
    if abs(n.z) > 0.1 or p.material_index > 1:
        continue
    c = p.center
    r = room_at((c.x + n.x * 0.25, c.y + n.y * 0.25))
    if r is None or r["name"] in NO_TRIM or r["name"].startswith("room_"):
        continue
    vs = [walls.data.vertices[i].co for i in p.vertices]
    t = Z.cross(n).normalized()
    ss = [v.dot(t) for v in vs]
    zs = [v.z for v in vs]
    if max(ss) - min(ss) < 0.12:
        continue
    d = vs[0].dot(n)
    F = Frame((n.x * d, n.y * d), (t.x, t.y))
    key = "charcoal" if r["name"] in CHARCOAL else "trim"
    if min(zs) < 0.01:
        B.box(key, F, min(ss), max(ss), -0.014, 0.0, 0.012, 0.152)
        nb += 1
    if max(zs) > CEIL - 0.01 and r["name"] not in NO_CROWN:
        B.box(key, F, min(ss), max(ss), -0.018, 0.0, CEIL - 0.10, CEIL)
        B.box(key, F, min(ss), max(ss), -0.042, 0.0, CEIL - 0.035, CEIL)
        nc += 1
B.finish()

# ------------------------------------------------------------------ panel moulding in the charcoal rooms
B = Builder("moulding", col)


def panels(F, s0, s1, cols_n, rows=((0.24, 0.92), (1.08, 2.78)), margin=0.22, gap=0.2):
    w = (s1 - s0 - 2 * margin - gap * (cols_n - 1)) / cols_n
    for i in range(cols_n):
        a = s0 + margin + i * (w + gap)
        b = a + w
        for z0, z1 in rows:
            for (sa, sb, za, zb) in ((a, b, z0, z0 + 0.028), (a, b, z1 - 0.028, z1), (a, a + 0.028, z0, z1), (b - 0.028, b, z0, z1)):
                B.box("charcoal", F, sa, sb, 0.0, 0.012, za, zb)


x0, y0, x1, y1 = room_bounds("primary_suite")
panels(Frame((x1, y0), (0, 1)), 0.0, y1 - y0, 3)
panels(Frame((x0, y0), (1, 0)), 0.0, x1 - x0, 3)             # south wall (behind the entry)
ox0, oy0, ox1, oy1 = room_bounds("office")
panels(Frame((ox1, oy0), (0, 1)), 0.0, oy1 - oy0, 3)
panels(Frame((ox1, oy1), (-1, 0)), 0.0, ox1 - ox0, 3)
B.finish()

# ------------------------------------------------------------------ foyer beam, stair rail
B = Builder("details", col)
fx0, fy0, fx1, fy1 = K["FOYER"]
B.box("oak", WORLD, (fx0 + fx1) / 2 - 0.1, (fx0 + fx1) / 2 + 0.1, fy0, fy1, 5.10, 5.33)
ya = K["YA1"] - 0.07
B.rod("hw", (K["SX0"] + 0.1, ya, 0.95), (K["GW"], ya, K["ZF"] + 0.92), 0.02)
B.rod("hw", (K["GW"], ya, K["ZF"] + 0.92), (K["XW"] - 0.3, ya, K["ZF"] + 0.92), 0.02)
B.finish()

# ------------------------------------------------------------------ kitchen
B = Builder("kitchen", col)
A = PX(1207, 1260)
KF = Frame(A, (1, 1))                 # s: SW -> NE along the range wall, d: toward the kitchen
D0 = 0.062                            # wall face
LEN = 5.36
# fridge bay
B.box("steel", KF, 0.08, 0.99, D0 + 0.02, D0 + 0.76, 0.02, 2.12)
B.box("hw", KF, 0.525, 0.535, D0 + 0.76, D0 + 0.765, 0.05, 2.1)
for sx in (0.49, 0.57):
    B.box("steel", KF, sx - 0.01, sx + 0.01, D0 + 0.765, D0 + 0.81, 0.9, 1.7)
B.box("trim", KF, 0.03, 0.07, D0, D0 + 0.72, 0.0, 2.95)
B.box("trim", KF, 1.0, 1.04, D0, D0 + 0.72, 0.0, 2.95)
B.box("trim", KF, 0.07, 1.0, D0, D0 + 0.70, 2.14, 2.95)
cab_doors(B, "trim", KF, 0.07, 1.0, D0 + 0.70, 2.16, 2.93, 2)
# base runs, counters, splash
for s0, s1 in ((1.04, 2.05), (3.31, LEN - 0.04)):
    base_cabinet(B, KF, s0, s1, D0, drawers=(s0 > 3), top=None)
    B.box("quartz", KF, s0, s1 + 0.02, D0, D0 + 0.64, 0.885, 0.915)
    B.box("quartz", KF, s0, s1, D0, D0 + 0.015, 0.915, 1.45)
    # uppers to the ceiling with a glass-front top row
    B.box("trim", KF, s0, s1, D0, D0 + 0.34, 1.45, 2.95)
    n = max(2, round((s1 - s0) / 0.5))
    cab_doors(B, "trim", KF, s0, s1, D0 + 0.34, 1.45, 2.38, n)
    cab_doors(B, "trim", KF, s0, s1, D0 + 0.34, 2.38, 2.95, n, pulls=None)
    B.box("trim", KF, s0, s1, D0, D0 + 0.40, 2.95, CEIL)
# range
B.box("steel", KF, 2.07, 3.29, D0 + 0.02, D0 + 0.70, 0.10, 0.90)
B.box("hw", KF, 2.07, 3.29, D0 + 0.02, D0 + 0.71, 0.0, 0.10)
B.box("hw", KF, 2.09, 3.27, D0 + 0.04, D0 + 0.68, 0.90, 0.925)
B.box("glassdark", KF, 2.14, 2.88, D0 + 0.70, D0 + 0.712, 0.22, 0.74)
B.box("glassdark", KF, 2.92, 3.24, D0 + 0.70, D0 + 0.712, 0.22, 0.74)
B.box("steel", KF, 2.14, 3.24, D0 + 0.712, D0 + 0.75, 0.76, 0.78)
for k in range(8):
    sc = 2.17 + k * 0.148
    xy = KF.xy(sc, D0 + 0.72)
    B.rod("hw", (xy[0], xy[1], 0.84), (KF.xy(sc, D0 + 0.75)[0], KF.xy(sc, D0 + 0.75)[1], 0.84), 0.02)
for (sc, dc) in ((2.3, 0.2), (2.68, 0.2), (3.06, 0.2), (2.3, 0.5), (2.68, 0.5), (3.06, 0.5)):
    B.cyl("hw", KF.xy(sc, D0 + dc), 0.085, 0.925, 0.945, seg=12)
B.box("quartz", KF, 2.05, 3.31, D0, D0 + 0.015, 0.915, 1.80)
# oak hood
B.box("oak", KF, 2.05, 3.31, D0, D0 + 0.60, 1.74, 1.92)


def hood_pt(s, d, z):
    return KF.p(s, d, z)


B.hexa("oak", [hood_pt(2.07, D0, 1.92), hood_pt(3.29, D0, 1.92), hood_pt(3.29, D0 + 0.58, 1.92), hood_pt(2.07, D0 + 0.58, 1.92),
               hood_pt(2.22, D0, 2.72), hood_pt(3.14, D0, 2.72), hood_pt(3.14, D0 + 0.42, 2.72), hood_pt(2.22, D0 + 0.42, 2.72)])
B.box("oak", KF, 2.20, 3.16, D0, D0 + 0.44, 2.72, CEIL)
# pot filler
pf = KF.xy(2.68, D0 + 0.02)
B.rod("brass", (pf[0], pf[1], 1.38), (KF.xy(2.68, D0 + 0.3)[0], KF.xy(2.68, D0 + 0.3)[1], 1.38), 0.012)
# island
kc = PX(1244.5, 959)
IF = Frame(kc, (1, 1))
IL, IW = 1.8, 0.55
B.box("hw", IF, -IL + 0.06, IL - 0.06, -IW + 0.06, 0.30, 0.0, 0.10)
B.box("oak", IF, -IL, IL, -IW, 0.36, 0.10, 0.885)
for i in range(4):                                             # framed oak panels on the seating side
    a = -IL + 0.06 + i * (2 * IL - 0.12) / 4
    b = a + (2 * IL - 0.12) / 4 - 0.05
    for (sa, sb, za, zb) in ((a, b, 0.14, 0.2), (a, b, 0.80, 0.86), (a, a + 0.06, 0.14, 0.86), (b - 0.06, b, 0.14, 0.86)):
        B.box("oak", IF, sa, sb, 0.36, 0.372, za, zb)
cab_doors(B, "oak", IF, IL, -IL, -IW, 0.10, 0.885, 6)          # cabinet fronts on the working side
# quartz top around the sink cut-out
T0, T1 = 0.885, 0.925
SS0, SS1, SD0, SD1 = -0.42, 0.42, -0.50, -0.08
B.box("quartz", IF, -IL - 0.06, SS0, -IW - 0.05, 0.70, T0, T1)
B.box("quartz", IF, SS1, IL + 0.06, -IW - 0.05, 0.70, T0, T1)
B.box("quartz", IF, SS0, SS1, -IW - 0.05, SD0, T0, T1)
B.box("quartz", IF, SS0, SS1, SD1, 0.70, T0, T1)
B.box("steel", IF, SS0, SS1, SD0, SD1, 0.66, 0.67)
for (sa, sb, da, db) in ((SS0 - 0.005, SS0, SD0, SD1), (SS1, SS1 + 0.005, SD0, SD1), (SS0, SS1, SD0 - 0.005, SD0), (SS0, SS1, SD1, SD1 + 0.005)):
    B.box("steel", IF, sa, sb, da, db, 0.66, T1 - 0.002)
fa = IF.xy(0.0, SD1 + 0.06)
B.cyl("brass", fa, 0.016, T1, T1 + 0.42, seg=12)
B.rod("brass", (fa[0], fa[1], T1 + 0.41), (IF.xy(0.0, SD1 - 0.16)[0], IF.xy(0.0, SD1 - 0.16)[1], T1 + 0.41), 0.014)
B.rod("brass", (IF.xy(0.0, SD1 - 0.16)[0], IF.xy(0.0, SD1 - 0.16)[1], T1 + 0.41), (IF.xy(0.0, SD1 - 0.16)[0], IF.xy(0.0, SD1 - 0.16)[1], T1 + 0.30), 0.014)
# oak beams in the tray
TRAY = CEIL + FT
for sc in (-1.9, -0.95, 0.0, 0.95, 1.9):
    B.box("oak", IF, sc - 0.07, sc + 0.07, -0.95, 0.95, TRAY - 0.20, TRAY)
# coffee bar (recess left of the fridge)
cx1 = PX(1201, 0)[0]
cy0, cy1 = PX(0, 1336)[1], PX(0, 1257)[1]
CF = Frame((cx1, cy0), (0, 1))        # d: into the nook (toward -x)
base_cabinet(B, CF, 0.0, cy1 - cy0, 0.0, depth=0.58, n=2)
B.box("quartz", CF, 0.0, cy1 - cy0, 0.0, 0.015, 0.915, 1.45)
for zz in (1.5, 1.95):
    B.box("oak", CF, 0.03, cy1 - cy0 - 0.03, 0.0, 0.26, zz, zz + 0.04)
# pantry shelving on the pantry side of the range wall
PF = Frame(A, (1, 1))
for zz in (0.45, 0.9, 1.35, 1.8, 2.25):
    B.box("oak", PF, 0.55, LEN - 0.55, -D0 - 0.36, -D0, zz, zz + 0.03)
for sc in (0.55, 2.0, 3.4, LEN - 0.58):
    B.box("trim", PF, sc, sc + 0.03, -D0 - 0.36, -D0, 0.0, 2.3)
B.finish()

# ------------------------------------------------------------------ fireplaces
B = Builder("fireplace", col)
fxw = PX(646, 0)[0]                   # family room west wall, inner face
FF = Frame((fxw, 10.47), (0, -1))     # d: into the room (+x); s: toward -y
# hearth, chimney breast with a firebox, mantel
B.box("limestone", FF, -1.25, 1.25, 0.0, 0.95, 0.012, 0.40)
B.box("limestone", FF, -1.02, -0.52, 0.0, 0.46, 0.40, CEIL)
B.box("limestone", FF, 0.52, 1.02, 0.0, 0.46, 0.40, CEIL)
B.box("limestone", FF, -0.52, 0.52, 0.0, 0.46, 1.22, CEIL)
B.box("hw", FF, -0.52, 0.52, 0.0, 0.05, 0.40, 1.22)
B.box("hw", FF, -0.52, -0.50, 0.05, 0.40, 0.40, 1.22)
B.box("hw", FF, 0.50, 0.52, 0.05, 0.40, 0.40, 1.22)
B.box("hw", FF, -0.5, 0.5, 0.05, 0.40, 1.20, 1.22)
for k in range(3):                                           # log set
    B.rod("timber", FF.p(-0.3 + 0.05 * k, 0.15 + 0.07 * k, 0.47 + 0.02 * k), FF.p(0.3 - 0.05 * k, 0.17 + 0.07 * k, 0.47 + 0.02 * k), 0.045)
B.box("oak", FF, -1.12, 1.12, 0.46, 0.68, 1.42, 1.60)
# flanking oak cabinets and floating shelves
for sa, sb in ((1.05, 2.0), (-2.0, -1.05)):
    base_cabinet(B, FF, sa, sb, 0.0, z_top=0.86, depth=0.46, key="oak", n=2, top="oak", overhang=0.0)
    for zz in (1.42, 1.98):
        B.box("oak", FF, sa + 0.02, sb - 0.02, 0.0, 0.28, zz, zz + 0.05)
# primary suite fireplace (stone bump on the west wall)
px1 = PX(1632, 0)[0]
PFp = Frame((px1, (PX(0, 178)[1] + PX(0, 290)[1]) / 2), (0, -1))
B.box("limestone", PFp, -0.82, 0.82, -0.29, 0.05, 0.012, 3.3)
B.box("hw", PFp, -0.48, 0.48, 0.05, 0.062, 0.32, 0.95)
B.box("glassdark", PFp, -0.42, 0.42, 0.062, 0.066, 0.38, 0.89)
B.box("oak", PFp, -0.9, 0.9, 0.05, 0.27, 1.32, 1.50)
# outdoor fireplace: hearth and firebox on the brick mass
ofx = PX(1547, 0)[0]
OF = Frame((ofx, (PX(0, 160)[1] + PX(0, 307)[1]) / 2), (0, 1))      # d: toward -x (outdoor living)
B.box("brick", OF, -1.1, 1.1, 0.0, 0.5, 0.0, 0.40)
B.box("hw", OF, -0.55, 0.55, 0.0, 0.03, 0.42, 1.25)
B.box("limestone", OF, -1.05, 1.05, 0.0, 0.22, 1.45, 1.60)
B.finish()

# ------------------------------------------------------------------ exterior timber: gable trusses, porch brackets
B = Builder("extimber", col)


def beam(a, b, w=0.16):
    B.rod("timber", a, b, w / math.sqrt(2), seg=4)


GWx = K["GW"]
for x0, x1 in ((0.0, PX(634, 0)[0]), (GWx, PX(2009, 0)[0])):
    xm, yv = (x0 + x1) / 2, PX(0, 1903)[1] - 0.13
    apex = CEIL + (x1 - x0) / 2 * (10.0 / 12.0)
    zt = 4.75
    hw = (apex - zt) / (10.0 / 12.0)
    beam((xm - hw - 0.25, yv, zt - 0.2), (xm + hw + 0.25, yv, zt - 0.2), 0.2)      # tie beam
    beam((xm, yv, zt - 0.2), (xm, yv, apex - 0.28), 0.18)                            # king post
    beam((xm - hw, yv, zt - 0.2), (xm, yv, apex - 0.3), 0.18)                        # rafters
    beam((xm + hw, yv, zt - 0.2), (xm, yv, apex - 0.3), 0.18)
    beam((xm - hw * 0.5, yv, zt + (apex - zt) * 0.5 - 0.25), (xm, yv, zt - 0.1), 0.13)   # struts
    beam((xm + hw * 0.5, yv, zt + (apex - zt) * 0.5 - 0.25), (xm, yv, zt - 0.1), 0.13)
for px in (650, 887, 1193, 1427):
    x = PX(px, 0)[0]
    for sgn in (-1, 1):
        if (px == 650 and sgn < 0) or (px == 1427 and sgn > 0):
            continue
        beam((x, 0.75, 2.15), (x + sgn * 0.6, 0.75, CEIL - 0.3), 0.11)
B.finish()
print("trim boxes", nb, nc, "millwork objects", len(col.all_objects))
