"""Stage 4: furnish every room. Re-runnable; owns COL-furniture."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/furnish_lib.py").read())

wipe_col("COL-furniture")
ROOT_COL = get_col("COL-furniture")
organise_assets()
furnish_materials()
K = json.loads(bpy.context.scene["camellia_shell"])
OP = {o["name"]: o for o in S["openings"]}
TRAY = CEIL + FT
made = []


def R(name):
    c = get_col("COL-furn_" + name, ROOT_COL)
    return Builder("furn_" + name, c), c


def done(B):
    obs = B.finish()
    soften(obs)
    made.extend(obs)


# ------------------------------------------------------------------ family room
B, C = R("family")
rug(B, 11.0, 10.47, 3.4, 4.4, "rug_cream")
sofa(B, 13.1, 10.47, (-1, 0), w=2.6, fab="fab_oat", accent=("fab_sage", "fab_white"))
place("modern_arm_chair_01", 10.6, 12.55, facing=(0, -1), col=C)
place("modern_arm_chair_01", 10.6, 8.40, facing=(0, 1), col=C)
place("modern_coffee_table_01", 11.15, 10.47, facing=(1, 0), col=C)
for yy in (12.15, 8.80):
    place("side_table_01", 13.35, yy, facing=(-1, 0), col=C)
    table_lamp(B, 13.35, yy, 0.55, "family")
place("potted_plant_01", 14.25, 9.2, col=C)
FF = Frame((PX(646, 0)[0], 10.47), (0, -1))
B.box("glassdark", FF, -0.74, 0.74, 0.46, 0.49, 1.78, 2.62)
place("ASSET-books_a", 7.96, 8.95, z=1.47, facing=(1, 0), col=C)
place("ASSET-books_b", 7.96, 12.0, z=2.03, facing=(1, 0), col=C)
place("ceramic_vase_03", 7.96, 11.75, z=1.47, col=C)
place("ceramic_vase_01", 7.98, 8.75, z=2.03, col=C)
place("wooden_bowl_01", 8.02, 11.95, z=0.885, col=C)
art(B, 10.6, PX(0, 1438)[1], (0, 1), w=1.7, h=1.15, z=1.15, key="art_a", frame="oak")
console(B, 10.6, PX(0, 1438)[1], (0, 1), w=1.6)
place("ceramic_vase_01", 10.15, PX(0, 1438)[1] + 0.18, z=0.82, col=C)
place("ASSET-books_c", 11.0, PX(0, 1438)[1] + 0.18, z=0.82, facing=(0, 1), col=C)
place("potted_plant_04", 8.02, 9.0, z=0.885, col=C)
done(B)

# ------------------------------------------------------------------ kitchen
B, C = R("kitchen")
IF = Frame(PX(1244.5, 959), (1, 1))
for s in (-1.2, -0.4, 0.4, 1.2):
    stool(B, *IF.xy(s, 0.36 + 0.36))
for s in (-1.1, 0.0, 1.1):
    xy = IF.xy(s, 0.05)
    place("modern_ceiling_lamp_01", xy[0], xy[1], z=TRAY, anchor="top", col=C)
    LAMPS.append((xy[0], xy[1], TRAY - 0.78, "pendant", "kitchen"))
xy = IF.xy(-1.15, 0.25)
place("wooden_bowl_01", xy[0], xy[1], z=0.925, col=C)
xy = IF.xy(1.3, 0.15)
place("ceramic_vase_01", xy[0], xy[1], z=0.925, col=C)
place("potted_plant_04", 14.98, 9.5, z=0.915, col=C)
done(B)

# ------------------------------------------------------------------ dining
B, C = R("dining")
DX, DY = 18.1, 18.6
rug(B, DX, DY, 2.9, 4.0, "rug_warm")
table(B, DX, DY, 2.6, 1.1, legs="trestle", facing=(1, 0))
for dy in (-0.85, 0.0, 0.85):
    place("dining_chair_02", DX - 0.82, DY + dy, facing=(1, 0), col=C)
    place("dining_chair_02", DX + 0.82, DY + dy, facing=(-1, 0), col=C)
place("dining_chair_02", DX, DY - 1.62, facing=(0, 1), col=C)
place("dining_chair_02", DX, DY + 1.62, facing=(0, -1), col=C)
ring_chandelier(B, DX, DY, CEIL, drop=1.15, r=0.5, room="dining")
place("ceramic_vase_01", DX, DY, z=0.75, col=C)
place("potted_plant_01", 16.35, 20.65, col=C)
HF = facing_frame(20.82, 19.33, (-1, 0))
base_cabinet(B, HF, -1.5, 1.5, 0.0, depth=0.46, key="oak", n=6, top="quartz")
for zz in (1.35, 1.80, 2.25):
    B.box("oak", HF, -1.52, 1.52, 0.0, 0.30, zz, zz + 0.04)
place("ASSET-books_c", 20.66, 18.6, z=1.39, facing=(-1, 0), col=C)
place("ceramic_vase_03", 20.66, 20.1, z=1.39, col=C)
place("ceramic_vase_01", 20.64, 19.8, z=0.915, col=C)
place("wooden_bowl_01", 20.6, 18.8, z=0.915, col=C)
place("ASSET-books_a", 20.66, 19.9, z=1.84, facing=(-1, 0), col=C)
curtains(B, OP["dining_back_windows"])
done(B)

# ------------------------------------------------------------------ foyer
B, C = R("foyer")
console(B, 11.49, 5.4, (1, 0), w=1.5)
table_lamp(B, 11.68, 4.92, 0.82, "foyer")
place("ceramic_vase_03", 11.68, 5.9, z=0.82, col=C)
round_mirror(B, 11.49, 5.4, (1, 0))
rug(B, 13.17, 4.9, 1.8, 2.8, "rug_blue")
ring_chandelier(B, 13.17, 4.86, 5.10, drop=1.0, r=0.6, n=12, room="foyer")
place("potted_plant_02", 14.42, 3.22, col=C)
art(B, 14.85, 3.4, (-1, 0), w=0.8, h=1.0, z=1.2, key="art_c")
done(B)

# ------------------------------------------------------------------ office
B, C = R("office")
rug(B, 16.85, 4.95, 2.6, 3.0, "rug_blue")
table(B, 17.1, 4.95, 1.7, 0.8, legs="steel", facing=(-1, 0))
place("dining_chair_02", 17.85, 4.95, facing=(-1, 0), col=C)
place("steel_frame_shelves_03", 16.85, 7.15 - 0.37, facing=(0, -1), col=C)
place("mid_century_lounge_chair", 15.8, 3.6, facing=(0.6, 0.8), col=C)
floor_lamp(B, 16.6, 3.2, "office")
table_lamp(B, 17.2, 5.6, 0.75, "office", h=0.45)
place("potted_plant_04", 17.1, 4.3, z=0.75, col=C)
art(B, 18.70, 4.95, (-1, 0), w=1.2, h=0.9, z=1.3, key="art_c")
curtains(B, OP["window_low_26"])
done(B)

# ------------------------------------------------------------------ primary suite
B, C = R("primary")
rug(B, 23.55, 24.2, 3.6, 3.0, "rug_cream")
bed(B, 23.55, 25.94, (0, -1), "king", fab="fab_oat", accent="fab_rust")
for sx in (-1.35, 1.35):
    place("side_table_01", 23.55 + sx, 25.66, facing=(0, -1), col=C)
    table_lamp(B, 23.55 + sx, 25.66, 0.55, "primary_suite")
bench(B, 23.55, 23.72, (0, -1), w=1.5)
place("mid_century_lounge_chair", 25.35, 22.2, facing=(-0.7, 0.7), col=C)
floor_lamp(B, 25.8, 21.75, "primary_suite")
dresser(B, 24.0, 21.37, (0, 1), w=1.6)
art(B, 24.0, 21.37, (0, 1), w=1.3, h=0.85, z=1.15, key="art_b", frame="oak")
place("ceramic_vase_01", 23.45, 21.6, z=0.845, col=C)
place("potted_plant_02", 21.4, 25.45, col=C)
curtains(B, OP["window_0"], panel=0.35)
curtains(B, OP["window_1"], panel=0.35)
done(B)

# ------------------------------------------------------------------ bedrooms
B, C = R("bedroom_2")
rug(B, 9.9, 4.75, 2.4, 2.8, "rug_blue")
bed(B, 11.40, 4.75, (-1, 0), "queen", fab="fab_white", accent="fab_navy")
for dy in (-1.07, 1.07):
    place("side_table_01", 11.15, 4.75 + dy, facing=(-1, 0), col=C)
    table_lamp(B, 11.15, 4.75 + dy, 0.55, "bedroom_2")
dresser(B, 7.63, 4.3, (1, 0), w=1.4)
art(B, 7.63, 4.3, (1, 0), w=1.0, h=0.8, z=1.15, key="art_b")
place("potted_plant_04", 7.85, 3.85, z=0.845, col=C)
curtains(B, OP["window_low_24"])
done(B)

B, C = R("bedroom_3")
rug(B, 5.9, 2.3, 2.4, 2.8, "rug_cream")
bed(B, 7.48, 2.3, (-1, 0), "queen", fab="fab_oat", accent="fab_sage")
for dy in (-1.07, 1.07):
    place("side_table_01", 7.22, 2.3 + dy, facing=(-1, 0), col=C)
    table_lamp(B, 7.22, 2.3 + dy, 0.55, "bedroom_3")
dresser(B, 3.82, 1.75, (1, 0), w=1.3)
art(B, 3.82, 1.75, (1, 0), w=0.9, h=0.9, z=1.15, key="art_a", frame="oak")
place("ceramic_vase_03", 4.05, 2.15, z=0.845, col=C)
curtains(B, OP["window_low_30"])
done(B)

B, C = R("bedroom_4")
rug(B, 2.3, 6.2, 2.4, 2.4, "rug_warm")
bed(B, 2.65, 4.51, (0, 1), "queen", fab="fab_white", accent="fab_rust")
place("side_table_01", 1.55, 4.76, facing=(0, 1), col=C)
table_lamp(B, 1.55, 4.76, 0.55, "bedroom_4")
dresser(B, 3.71, 6.4, (-1, 0), w=1.2)
art(B, 3.71, 6.4, (-1, 0), w=0.9, h=0.7, z=1.15, key="art_c")
place("potted_plant_04", 3.5, 6.75, z=0.845, col=C)
curtains(B, OP["window_low_33"])
done(B)

# ------------------------------------------------------------------ game room
B, C = R("game_room")
rug(B, 2.6, 14.9, 3.0, 3.4, "rug_blue")
place("modern_wooden_cabinet", 0.42, 14.9, facing=(1, 0), col=C)
GFm = facing_frame(0.15, 14.9, (1, 0))
B.box("glassdark", GFm, -0.8, 0.8, 0.0, 0.04, 1.05, 1.95)
sofa(B, 4.86, 14.9, (-1, 0), w=2.4, fab="fab_grey", accent=("fab_rust", "fab_navy"))
place("coffee_table_round_01", 2.55, 14.9, col=C)
round_table(B, 2.5, 11.9, r=0.6)
for fx, fy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    place("dining_chair_02", 2.5 - fx * 0.95, 11.9 - fy * 0.95, facing=(fx, fy), col=C)
place("steel_frame_shelves_01", 4.93 - 0.26, 11.45, facing=(-1, 0), col=C)
place("steel_frame_shelves_01", 0.15 + 0.26, 12.3, facing=(1, 0), col=C)
floor_lamp(B, 4.5, 16.35, "game_room")
place("potted_plant_01", 0.65, 16.3, col=C)
done(B)

# ------------------------------------------------------------------ bonus room (floor at 3.10)
B, C = R("bonus")
ZB = K["ZF"] + 0.012
rug(B, 22.5, 4.6, 2.6, 3.2, "rug_warm", z=ZB)
sofa(B, K["XW"] + 0.03, 4.6, (1, 0), w=2.4, fab="fab_oat", accent=("fab_navy", "fab_sage"), base=ZB)
place("modern_coffee_table_01", 22.3, 4.6, z=ZB, facing=(1, 0), col=C)
sofa(B, 22.5, K["Y0"] + 0.03, (0, 1), w=2.2, fab="fab_white", accent=("fab_rust", "fab_oat"), base=ZB)
B.box("oak", WORLD, K["XD"] - 0.55, K["XD"], K["YD0"], K["YD1"], K["ZF"], K["ZF"] + 0.42)
B.box("fab_oat", WORLD, K["XD"] - 0.54, K["XD"] - 0.01, K["YD0"] + 0.02, K["YD1"] - 0.02, K["ZF"] + 0.42, K["ZF"] + 0.50)
for yy, key in ((K["YD0"] + 0.5, "fab_sage"), (K["YD1"] - 0.5, "fab_navy"), ((K["YD0"] + K["YD1"]) / 2, "fab_white")):
    B.box(key, WORLD, K["XD"] - 0.22, K["XD"] - 0.06, yy - 0.22, yy + 0.22, K["ZF"] + 0.50, K["ZF"] + 0.92)
place("steel_frame_shelves_01", 22.5, K["Y1"] - 0.27, z=ZB, facing=(0, -1), col=C)
place("mid_century_lounge_chair", 23.7, 9.7, z=ZB, facing=(-0.7, -0.7), col=C)
floor_lamp(B, 24.25, 10.55, "bonus", z=ZB)
done(B)

# ------------------------------------------------------------------ baths
B, C = R("primary_bath")
vanity(B, 24.22, 21.26, (0, -1), w=3.0, sinks=2, key="oak", room="primary_bath", towers=True)
tub(B, 26.38, 19.57, (0, 1))
shower(B, 25.31, 16.76, 27.0, 18.48, "WN", room="primary_bath")
toilet(B, 22.25, 17.34, (1, 0))
rug(B, 24.2, 20.3, 1.8, 0.7, "rug_cream")
place("potted_plant_04", 24.22, 21.02, z=0.86, col=C)
done(B)

B, C = R("hall_bath")
toilet(B, 5.05, 10.62, (1, 0))
tub(B, 5.48, 9.33, (0, 1), w=0.76, ln=1.5)
vanity(B, 7.48, 9.34, (-1, 0), w=1.3, key="trim", room="hall_bath")
toilet(B, 5.05, 11.8, (1, 0))
vanity(B, 7.48, 11.8, (-1, 0), w=0.8, key="oak", room="powder")
done(B)

B, C = R("jj_bath")
vanity(B, 1.86, 3.6, (-1, 0), w=1.1, key="trim", room="jj_bath_a")
toilet(B, 1.86, 2.62, (-1, 0))
shower(B, 0.12, 1.11, 1.84, 2.05, "N", room="jj_bath_a")
vanity(B, 2.01, 3.6, (1, 0), w=1.1, key="trim", room="jj_bath_b")
toilet(B, 2.01, 2.62, (1, 0))
shower(B, 2.03, 1.11, 3.69, 2.05, "N", room="jj_bath_b")
done(B)

# ------------------------------------------------------------------ service rooms
B, C = R("service")
UF = facing_frame(23.7, 11.40, (0, 1))
base_cabinet(B, UF, -0.9, 0.9, 0.0, key="trim", splash=0.1)
B.box("trim", UF, -0.9, 0.9, 0.0, 0.34, 1.45, 2.3)
cab_doors(B, "trim", UF, -0.9, 0.9, 0.34, 1.45, 2.3, 4)
appliance(B, 24.98, 11.40, (0, 1))
appliance(B, 25.72, 11.40, (0, 1))
B.box("oak", WORLD, 24.6, 26.1, 11.40, 11.78, 1.5, 1.54)
# mudroom bench with hooks and baskets
MF = facing_frame(22.66, 15.67, (-1, 0))
bench(B, 22.66, 15.67, (-1, 0), w=1.55, fab="fab_char")
B.box("trim", MF, -0.8, 0.8, 0.0, 0.02, 0.55, 1.95)
B.box("oak", MF, -0.8, 0.8, 0.0, 0.30, 1.95, 1.99)
for s in (-0.55, -0.18, 0.18, 0.55):
    B.rod("hw", MF.p(s, 0.02, 1.62), MF.p(s, 0.10, 1.66), 0.008, seg=8)
    B.box("rug_warm", MF, s - 0.15, s + 0.15, 0.04, 0.28, 2.0, 2.24)
# primary closet
shelf_wall(B, 23.45, 16.65, (0, -1), w=1.3, rod_z=1.7)
shelf_wall(B, 26.1, 16.65, (0, -1), w=1.7, rod_z=1.7)
shelf_wall(B, 23.45, 14.22, (0, 1), w=1.3, levels=(0.4, 0.8, 1.2, 1.6, 2.0))
shelf_wall(B, 26.1, 14.22, (0, 1), w=1.7, rod_z=1.7)
# bedroom closets
shelf_wall(B, 5.0, 7.15, (0, -1), w=2.2, rod_z=1.7)
shelf_wall(B, 10.14, 7.15, (0, -1), w=2.4, d=0.36, levels=(1.85,), rod_z=1.7)
shelf_wall(B, 3.87, 10.52, (0, -1), w=2.0, levels=(0.4, 0.85, 1.3, 1.75, 2.2))
done(B)

# ------------------------------------------------------------------ outdoor
B, C = R("outdoor")
rug(B, 18.0, 23.65, 3.0, 3.4, "rug_warm", z=0.0)
sofa(B, 16.5, 23.65, (1, 0), w=2.4, fab="fab_grey", accent=("fab_white", "fab_navy"))
place("modern_arm_chair_01", 18.4, 25.05, facing=(0, -1), col=C)
place("modern_arm_chair_01", 18.4, 22.25, facing=(0, 1), col=C)
place("coffee_table_round_01", 18.3, 23.65, col=C)
place("potted_plant_01", 13.65, 25.35, col=C)
place("modern_arm_chair_01", 8.5, 15.3, facing=(0, 1), col=C)
place("modern_arm_chair_01", 9.9, 15.3, facing=(0, 1), col=C)
place("side_table_01", 9.2, 15.2, col=C)
place("potted_plant_01", 10.95, 1.15, col=C)
place("potted_plant_01", 15.4, 1.15, col=C)
place("modern_arm_chair_01", 8.7, 1.75, facing=(0, -1), col=C)
place("modern_arm_chair_01", 9.95, 1.75, facing=(0, -1), col=C)
done(B)

# ------------------------------------------------------------------ garage: workbench, storage wall, bins, parking mats
B, C = R("garage")
GX = room_bounds("garage")[0]
table(B, GX + 0.42, 4.0, 2.0, 0.7, h=0.92, legs="steel", facing=(1, 0))
GF = facing_frame(GX, 4.0, (1, 0))
B.box("oak", GF, -1.0, 1.0, 0.0, 0.02, 1.15, 2.05)
for k, s in enumerate((-0.8, -0.55, -0.3, 0.0, 0.3, 0.6, 0.85)):
    B.rod("hw", GF.p(s, 0.03, 1.95), GF.p(s, 0.03, 1.95 - 0.25 - 0.08 * (k % 3)), 0.012, seg=6)
B.box("oak", GF, -1.0, 1.0, 0.0, 0.25, 2.1, 2.13)
stock(B, GX, 4.0, (1, 0), 2.0, 0.25, (2.105,), keys=("trim", "fab_grey", "rug_warm"), h=0.22)
GC = facing_frame(GX, 6.25, (1, 0))
B.box("hw", GC, -0.8, 0.8, 0.02, 0.50, 0.0, 0.10)
B.box("trim", GC, -0.8, 0.8, 0.0, 0.58, 0.10, 2.25)
cab_doors(B, "trim", GC, -0.8, 0.8, 0.58, 0.10, 1.15, 3)
cab_doors(B, "trim", GC, -0.8, 0.8, 0.58, 1.15, 2.25, 3)
B.cyl("siding", (GX + 0.45, 1.25), 0.27, 0.0, 0.95, seg=20)
B.cyl("siding", (GX + 0.45, 1.25), 0.29, 0.95, 0.99, seg=20)
B.cyl("hw", (GX + 1.15, 1.25), 0.27, 0.0, 0.95, seg=20)
B.cyl("hw", (GX + 1.15, 1.25), 0.29, 0.95, 0.99, seg=20)
for yy in (3.05, 6.6, 9.3):
    rug(B, 22.9, yy, 5.2, 2.3, "rubber", z=0.0)
place("steel_frame_shelves_01", 23.4, 11.22 - 0.27, facing=(0, -1), col=C)
place("steel_frame_shelves_01", 24.7, 11.22 - 0.27, facing=(0, -1), col=C)
stock(B, 23.4, 11.22 - 0.02, (0, -1), 1.0, 0.48, (0.52, 0.98, 1.42), keys=("trim", "rug_warm", "fab_grey"), h=0.3)
stock(B, 24.7, 11.22 - 0.02, (0, -1), 1.0, 0.48, (0.52, 0.98, 1.42), keys=("rug_warm", "trim", "fab_grey"), h=0.3)
done(B)

# ------------------------------------------------------------------ storage rooms, linen, pantry goods, hall runners
B, C = R("storage")
LV = (0.4, 0.9, 1.4, 1.9)
shelf_wall(B, 1.42, 9.92, (0, 1), w=2.3, d=0.36, levels=LV)
stock(B, 1.42, 9.92, (0, 1), 2.3, 0.36, LV)
shelf_wall(B, 1.42, 9.79, (0, -1), w=2.3, d=0.45, levels=LV)
stock(B, 1.42, 9.79, (0, -1), 2.3, 0.45, LV, keys=("trim", "rug_warm", "fab_grey", "oak"))
stock(B, 3.87, 10.52, (0, -1), 2.0, 0.40, (0.4, 0.85, 1.3, 1.75), keys=("fab_rust", "trim", "fab_sage", "rug_warm"))
LL = (0.4, 0.8, 1.2, 1.6, 2.0)
shelf_wall(B, 20.27, 17.0, (1, 0), w=1.15, d=0.3, levels=LL)
stock(B, 20.27, 17.0, (1, 0), 1.15, 0.3, LL, keys=("towel", "fab_white", "towel", "fab_oat"), h=0.2, step=0.34, size=0.28)
PFg = Frame(PX(1207, 1260), (1, 1))
for zi, zz in enumerate((0.45, 0.9, 1.35, 1.8, 2.25)):
    for k in range(15):
        if (k + zi) % 6 == 5:
            continue
        s0 = 0.64 + k * 0.28
        wd = 0.12 + 0.05 * ((k * 7 + zi * 3) % 3)
        hg = 0.14 + 0.05 * ((k * 5 + zi) % 4)
        key = ("ceramic", "oak", "trim", "fab_oat", "glassdark")[(k + zi * 2) % 5]
        if (k + zi) % 3 == 0:
            xy = PFg.xy(s0 + wd / 2, -0.25)
            B.cyl(key, xy, wd / 2, zz + 0.03, zz + 0.03 + hg, seg=14)
        else:
            B.box(key, PFg, s0, s0 + wd, -0.36, -0.14, zz + 0.03, zz + 0.03 + hg)
rug(B, 5.6, 7.85, 3.2, 0.85, "rug_warm")
art(B, 5.4, 8.47, (0, -1), w=0.7, h=0.9, z=1.2, key="art_b")
rug(B, 21.53, 19.6, 0.85, 2.4, "rug_blue")
art(B, 20.93, 19.6, (1, 0), w=0.8, h=1.0, z=1.2, key="art_a", frame="oak")
rug(B, 21.75, 13.3, 0.9, 2.8, "rug_blue")
rug(B, 6.37, 13.07, 1.6, 0.9, "rug_warm")
done(B)

bpy.context.scene["camellia_lamps"] = json.dumps(LAMPS)
print("furniture objects", len(made), "instances", sum(1 for o in ROOT_COL.all_objects if o.instance_type == "COLLECTION"), "lamps", len(LAMPS))
