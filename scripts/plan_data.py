"""Curate the raster trace of the main-floor plan into build data (metres).

Input : scripts/trace/trace_raw.json  (pixels, from scripts/trace/vectorize.py)
Output: scripts/structure.json        (metres; origin front-left, +Y to the back)

Run:  uv run --with shapely python scripts/plan_data.py
"""
import json
import math
import os

from shapely.geometry import Polygon, box, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "trace", "trace_raw.json")))

PX_PER_M = 22.41 / 0.3048          # calibrated on game room, garage, primary suite labels
X_REF, Y_REF = 72.0, 1972.0        # px of front-left exterior corner
CEIL = 3.048                       # 10 ft


def m(p):
    return ((p[0] - X_REF) / PX_PER_M, (Y_REF - p[1]) / PX_PER_M)


def rect(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def seg(p0, p1, thick):
    """Rectangle polygon around a centreline segment."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * thick / 2, dx / L * thick / 2
    return Polygon([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny),
                    (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)])


def diamond(c, r):
    return Polygon([(c[0], c[1] - r), (c[0] + r, c[1]), (c[0], c[1] + r), (c[0] - r, c[1])])


# ------------------------------------------------------------------ walls
DROP_BBOX = [  # auto polygons replaced by clean manual geometry (bbox in px)
    (1217, 1210, 1482, 1360), (1151, 996, 1468, 1349), (940, 920, 1021, 967),
    (1519, 894, 1622, 1168), (1506, 873, 1530, 894), (1583, 748, 1611, 822),
    (1196, 681, 1242, 740), (1506, 388, 1623, 769), (1937, 1847, 2008, 1903),
    (1915, 730, 2070, 782), (1547, 145, 1656, 322), (1076, 859, 1084, 868),
    (1134, 792, 1139, 802), (1225, 595, 1242, 600), (1233, 508, 1242, 514),
    (1333, 409, 1339, 420), (1419, 404, 1426, 415), (1225, 400, 1252, 427),
    (251, 1897, 285, 1903), (1562, 420, 1602, 427), (854, 956, 860, 967),
    (767, 948, 774, 961), (717, 1189, 725, 1198), (1139, 1759, 1163, 1766),
    (917, 1759, 940, 1766),
]


def is_dropped(poly):
    x0, y0, x1, y1 = poly.bounds
    for b in DROP_BBOX:
        if all(abs(a - c) <= 4 for a, c in zip((x0, y0, x1, y1), b)):
            return True
    return False


auto = []
dropped = 0
for w in raw["walls"]:
    p = Polygon(w["outer"], w["holes"]).buffer(0)
    if p.is_empty:
        continue
    if is_dropped(p):
        dropped += 1
        continue
    auto.append(p)

manual = [
    rect(1205, 1341, 1459, 1349),                 # stair north wall
    rect(1447, 1234, 1459, 1361),                 # garage west wall (upper piece)
    seg((1205, 1262.75), (1287, 1344.75), 9.5),   # pantry SW wall
    seg((1207, 1260), (1486, 981), 9),            # kitchen / pantry wall (range wall)
    rect(1151, 1336, 1210, 1349), rect(1201, 1255, 1210, 1340),   # coffee bar
    rect(941, 948, 985, 968),                     # family back wall, right end
    Polygon([(973.5, 948), (1225, 696.5), (1243, 709.5), (984.5, 968)]),  # kitchen ext. diagonal
    rect(1225, 400, 1243, 709.5),                 # dining left (exterior)
    rect(1225, 400, 1623, 420),                   # dining top (exterior)
    rect(1599, 388, 1611, 427), rect(1603, 427, 1611, 686),       # dining / hall wall
    rect(1555, 420, 1603, 436), rect(1555, 666, 1611, 674),       # hutch niche ends
    rect(1555, 666, 1562, 739), seg((1553, 730.25), (1606, 783.25), 9.5),  # linen closet
    rect(1611, 641, 1623, 650),
    rect(1603, 748, 1611, 792), diamond((1597, 806), 13),         # pier B
    rect(1603, 790, 1612, 819),
    diamond((1518, 884), 12),                                     # pier A
    seg((1519, 895), (1607, 983), 10),            # pantry NE wall
    rect(1603, 975, 1611, 1147), rect(1547, 1134, 1623, 1147),
    seg((1450, 1240.75), (1550, 1140.75), 13),    # garage diagonal wall
    rect(1446, 883, 1510, 892), seg((1450, 954), (1484, 986), 9),  # pantry door wall + return
    rect(1997, 1847, 2009, 1903), rect(1941, 1892, 2009, 1903),   # garage front right
    rect(1916, 741, 2058, 748), rect(2058, 730, 2070, 782),
    rect(1547, 160, 1612, 307), rect(1612, 178, 1632, 290),       # outdoor / primary fireplace mass
    rect(1599, 140, 1612, 325),                                   # primary suite west wall behind it
]

# ------------------------------------------------------------------ openings
# (bbox centre x, y) -> type ; matched against auto-detected gaps
CUR = [
    ((1658, 60), "window"), ((1950, 60), "window"), ((1656, 411), "door"),
    ((1467, 407), "drop"), ((1852, 413), "fill"), ((1853, 450), "drop"),
    ((1656, 646), "door"), ((161, 737), "window"), ((260, 737), "window"),
    ((358, 737), "window"), ((1883, 744), "door"), ((1883, 931), "door"),
    ((541, 958), "extdoor"), ((814, 958), "window_low"), ((533, 1060), "door"),
    ((1655, 1140), "door"), ((648, 1150), "drop"), ((177, 1195), "ddoor"),
    ((1246, 1341), "drop"), ((177, 1345), "door"), ((394, 1345), "door"),
    ((541, 1345), "door"), ((567, 1442), "portal"), ((1040, 1450), "cased_wide"),
    ((818, 1495), "ddoor"), ((440, 1597), "door"), ((578, 1597), "door"),
    ((124, 1644), "door"), ((1040, 1756), "drop"), ((769, 1773), "window_low"),
    ((1040, 1773), "frontdoor"), ((1311, 1773), "window_low"),
    ((165, 1898), "window_small"), ((1816, 1898), "window_small"),
    ((1915, 1895), "window_small"), ((487, 1943), "window_low"),
    ((1596, 1943), "window_low"), ((1040, 1965), "arch_ext"),
    ((78, 1495), "window_low"), ((349, 1394), "door"), ((349, 1693), "door"),
    ((447, 1012), "arch"), ((634, 1012), "arch"), ((634, 1394), "arch"),
    ((627, 1490), "door"), ((638, 1202), "fill"), ((912, 1852), "arch_ext"),
    ((1170, 1854), "arch_ext"), ((1170, 1607), "ddoor_glass"),
    ((1231, 641), "drop"), ((1242, 468), "drop"), ((1453, 1393), "door"),
    ((1558, 551), "niche"), ((1606, 112), "window"), ((1605, 355), "extdoor"),
    ((1605, 718), "door"), ((1607, 899), "portal"), ((1704, 537), "ddoor"),
    ((1742, 1035), "door"), ((1829, 697), "door"), ((2003, 1745), "garage"),
    ((2004, 1394), "garage"), ((2065, 534), "window"), ((2065, 677), "window_high"),
    ((2065, 838), "window_high"), ((1579, 1110), "drop"), ((1500, 1189), "drop"),
]

SPEC = {  # type: (sill, head, arch)
    "door": (0, 2.44, False), "ddoor": (0, 2.44, False), "ddoor_glass": (0, 2.44, False),
    "extdoor": (0, 2.44, False), "frontdoor": (0, 2.95, True), "garage": (0, 2.44, False),
    "slider": (0, 2.44, False), "window": (0.75, 2.44, False), "window_low": (0.6, 2.44, False),
    "window_small": (1.45, 2.44, False), "window_high": (1.85, 2.44, False),
    "arch": (0, 2.6, True), "arch_ext": (0, 2.75, True), "cased_wide": (0, 2.75, False),
    "niche": (0, 2.6, False), "door_arch": (0, 2.44, True),
}

ops = []  # dict(type, poly(px), c, u, w, t)


def add_op(kind, poly, c, u, w, t, name=None):
    ops.append({"type": kind, "poly": poly, "c": c, "u": u, "w": w, "t": t, "name": name})


used = set()
for (cx, cy), kind in CUR:
    best, bd = None, 1e9
    for o in raw["openings"]:
        d = math.hypot(o["c"][0] - cx, o["c"][1] - cy)
        if d < bd:
            best, bd = o, d
    if bd > 14:
        print("WARN: no auto opening near", (cx, cy), kind, "nearest", round(bd, 1))
        continue
    used.add(best["id"])
    if kind == "drop":
        continue
    xs = [p[0] for p in best["poly"]]
    ys = [p[1] for p in best["poly"]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if best["axis"] == "H":
        add_op(kind, rect(x0, y0, x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2), (1, 0), x1 - x0, y1 - y0)
    else:
        add_op(kind, rect(x0, y0, x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2), (0, 1), y1 - y0, x1 - x0)
for o in raw["openings"]:
    if o["id"] not in used:
        print("WARN: uncurated auto opening", o["id"], o["axis"], o["c"], o["len_ft"])


def op_rect(kind, x0, y0, x1, y1, axis, name=None):
    if axis == "H":
        add_op(kind, rect(x0, y0, x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2), (1, 0), abs(x1 - x0), abs(y1 - y0), name)
    else:
        add_op(kind, rect(x0, y0, x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2), (0, 1), abs(y1 - y0), abs(x1 - x0), name)


def op_seg(kind, p0, p1, thick, name=None):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    u = ((p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L)
    add_op(kind, seg(p0, p1, thick), ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), u, L, thick, name)


op_rect("window_low", 1252, 400, 1506, 420, "H", "dining_back_windows")
op_rect("slider", 1225, 428, 1243, 681, "V", "dining_slider")
op_seg("slider", (1010.8, 926.2), (1201.7, 735.3), 22.5, "kitchen_slider")
op_seg("door", (1476, 1214.75), (1524, 1166.75), 13.5, "garage_pantry_door")
op_rect("door_arch", 1446, 892, 1455, 952, "V", "pantry_door")
op_seg("arch", (1524, 878), (1591, 811), 12, "kitchen_mudroom_arch")
op_rect("window_small", 247, 1892, 289, 1904, "H", "jj_window_2")
op_rect("window", 2000, 1010, 2009, 1056, "V", "utility_window")
op_rect("portal", 1147, 1349, 1155, 1438, "V", "stair_portal")

walls_px = unary_union(auto + manual)

# widen each opening to the full thickness of the wall it sits in
for o in ops:
    if o["type"] in ("portal",) or o["u"] not in ((1, 0), (0, 1)):
        continue
    x0, y0, x1, y1 = o["poly"].bounds
    bands = []
    for side in (0, 1):
        if o["u"] == (1, 0):
            probe = rect(x0 - 9, y0 - 26, x0 - 1, y1 + 26) if side == 0 else rect(x1 + 1, y0 - 26, x1 + 9, y1 + 26)
        else:
            probe = rect(x0 - 26, y0 - 9, x1 + 26, y0 - 1) if side == 0 else rect(x0 - 26, y1 + 1, x1 + 26, y1 + 9)
        hit = walls_px.intersection(probe)
        if hit.is_empty:
            continue
        for g in getattr(hit, "geoms", [hit]):
            bx0, by0, bx1, by1 = g.bounds
            lo, hi = (by0, by1) if o["u"] == (1, 0) else (bx0, bx1)
            c0, c1 = (y0, y1) if o["u"] == (1, 0) else (x0, x1)
            if hi < c0 - 1 or lo > c1 + 1:
                continue
            if 5 <= hi - lo <= 27:
                bands.append((lo, hi))
    if bands:
        lo = min(b[0] for b in bands)
        hi = max(b[1] for b in bands)
        if hi - lo <= 27:
            if o["u"] == (1, 0):
                o["poly"] = rect(x0, lo, x1, hi)
                o["c"] = ((x0 + x1) / 2, (lo + hi) / 2)
            else:
                o["poly"] = rect(lo, y0, hi, y1)
                o["c"] = ((lo + hi) / 2, (y0 + y1) / 2)
            o["t"] = hi - lo

# snap opening ends to the real wall jambs (closes 1-6 px slivers left by the trace)
for o in ops:
    if o["u"] not in ((1, 0), (0, 1)):
        continue
    x0, y0, x1, y1 = o["poly"].bounds
    if o["u"] == (1, 0):
        a = walls_px.intersection(rect(x0 - 8, y0 + 1, x0 + 0.01, y1 - 1))
        b = walls_px.intersection(rect(x1 - 0.01, y0 + 1, x1 + 8, y1 - 1))
        if not a.is_empty:
            x0 = a.bounds[2]
        if not b.is_empty:
            x1 = b.bounds[0]
        o["w"] = x1 - x0
    else:
        a = walls_px.intersection(rect(x0 + 1, y0 - 8, x1 - 1, y0 + 0.01))
        b = walls_px.intersection(rect(x0 + 1, y1 - 0.01, x1 - 1, y1 + 8))
        if not a.is_empty:
            y0 = a.bounds[3]
        if not b.is_empty:
            y1 = b.bounds[1]
        o["w"] = y1 - y0
    o["poly"] = rect(x0, y0, x1, y1)
    o["c"] = ((x0 + x1) / 2, (y0 + y1) / 2)

fills = [o["poly"] for o in ops if o["type"] == "fill"]
cuts = [o["poly"] for o in ops if o["type"] not in ("fill",)]
solid_px = unary_union([walls_px] + fills).difference(unary_union(cuts)).buffer(0)
closed_px = unary_union([walls_px] + [o["poly"].buffer(0.9) for o in ops]).buffer(0)


def to_m_poly(p):
    p = orient(Polygon([m(c) for c in p.exterior.coords],
                       [[m(c) for c in r.coords] for r in p.interiors]), 1.0)
    return {"outer": [[round(x, 4), round(y, 4)] for x, y in p.exterior.coords[:-1]],
            "holes": [[[round(x, 4), round(y, 4)] for x, y in r.coords[:-1]] for r in p.interiors]}


def polys(g):
    return [p for p in getattr(g, "geoms", [g]) if p.area > 4]


out = {"ceil": CEIL, "px_per_m": PX_PER_M, "ref_px": [X_REF, Y_REF]}
out["walls"] = [to_m_poly(p) for p in polys(solid_px)]

rooms = []
foot = []
for p in polys(closed_px):
    foot.append(Polygon(p.exterior))
    for r in p.interiors:
        rp = Polygon(r)
        if rp.area / PX_PER_M ** 2 < 0.35:
            continue
        rooms.append(rp)
foot_px = unary_union(foot).buffer(0)
out["footprint"] = [to_m_poly(p) for p in polys(foot_px)]

# name rooms by seed points (px)
SEEDS = {
    "great_room": (880, 1200), "foyer": (1040, 1620), "office": (1310, 1600),
    "primary_suite": (1800, 230), "primary_bath": (1900, 600), "primary_wc": (1760, 700),
    "primary_closet": (1880, 840), "primary_hall": (1655, 520), "family_foyer": (1650, 900),
    "utility": (1870, 1060), "garage": (1730, 1500), "pantry": (1420, 1200),
    "mud_vestibule": (1575, 900), "hutch_niche": (1582, 550), "linen": (1582, 700),
    "stair": (1300, 1395), "bedroom_2": (780, 1640), "bedroom_3": (490, 1760),
    "bedroom_4": (210, 1500), "game_room": (250, 960), "jj_bath_a": (110, 1770),
    "jj_bath_b": (240, 1770), "hall_bath": (540, 1210), "powder": (533, 1106),
    "holiday": (330, 1270), "storage_a": (140, 1230), "storage_b": (140, 1300),
    "closet_b3": (430, 1520), "closet_b2": (820, 1470), "bed_hall": (480, 1395),
    "back_vestibule": (541, 1012), "portico": (1040, 1860), "bed_hall_s": (577, 1493),
}
room_out = []
for i, rp in enumerate(sorted(rooms, key=lambda r: -r.area)):
    name = None
    for k, s in SEEDS.items():
        if rp.contains(Point(s)):
            name = k if name is None else name + "+" + k
    c = rp.representative_point()
    d = to_m_poly(rp)
    d.update({"name": name or f"room_{i}", "area": round(rp.area / PX_PER_M ** 2, 2),
              "seed_px": [round(c.x), round(c.y)], "c": [round(v, 3) for v in m((c.x, c.y))]})
    room_out.append(d)
out["rooms"] = room_out

op_out = []
for i, o in enumerate(ops):
    if o["type"] in ("fill",):
        continue
    c = m(o["c"])
    u = (o["u"][0], -o["u"][1])
    d = {"id": i, "name": o["name"] or f"{o['type']}_{i}", "type": o["type"],
         "c": [round(c[0], 4), round(c[1], 4)], "u": [round(u[0], 5), round(u[1], 5)],
         "w": round(o["w"] / PX_PER_M, 4), "t": round(o["t"] / PX_PER_M, 4),
         "poly": to_m_poly(o["poly"])["outer"]}
    if o["type"] in SPEC:
        d["sill"], d["head"], d["arch"] = SPEC[o["type"]]
    # exterior if a point just off either side of the wall lies outside the footprint
    n = (-o["u"][1], o["u"][0])
    off = o["t"] / 2 + 6
    a = Point(o["c"][0] + n[0] * off, o["c"][1] + n[1] * off)
    b = Point(o["c"][0] - n[0] * off, o["c"][1] - n[1] * off)
    ina, inb = foot_px.contains(a), foot_px.contains(b)
    d["exterior"] = not (ina and inb)
    # outward normal in metres (points to the outside for exterior openings)
    nm = (n[0], -n[1])
    d["n_out"] = [nm[0], nm[1]] if (inb and not ina) else [-nm[0], -nm[1]]
    op_out.append(d)
out["openings"] = op_out
json.dump(out, open(os.path.join(HERE, "structure.json"), "w"))

fx0, fy0, fx1, fy1 = foot_px.bounds
print("walls", len(out["walls"]), "openings", len(op_out), "rooms", len(room_out), "dropped auto", dropped)
print("footprint m: %.2f x %.2f  area %.1f m2" % ((fx1 - fx0) / PX_PER_M, (fy1 - fy0) / PX_PER_M, foot_px.area / PX_PER_M ** 2))
for r in room_out:
    print(f"  {r['name']:22s} {r['area']:7.2f} m2  seed {r['seed_px']}")

# ------------------------------------------------------------------ debug image (optional)
if os.environ.get("PLAN_DEBUG"):
    import cv2
    import numpy as np
    Wd, Hd = raw["size"]
    img = np.full((Hd, Wd, 3), 255, np.uint8)

    def draw(g, col):
        for p in getattr(g, "geoms", [g]):
            if p.is_empty or p.geom_type != "Polygon":
                continue
            cv2.fillPoly(img, [np.array(p.exterior.coords, np.int32)], col)
            for r in p.interiors:
                cv2.fillPoly(img, [np.array(r.coords, np.int32)], (255, 255, 255))
    draw(closed_px, (90, 90, 90))
    flood = img.copy()
    mask2 = np.zeros((Hd + 2, Wd + 2), np.uint8)
    cv2.floodFill(flood, mask2, (2, 2), (255, 220, 170))
    img = flood
    COL = {"portal": (0, 200, 255), "fill": (0, 0, 0)}
    for o in ops:
        col = COL.get(o["type"], (0, 160, 0) if "window" in o["type"] or o["type"] == "slider" else (0, 0, 230))
        cv2.fillPoly(img, [np.array(o["poly"].exterior.coords, np.int32)], col)
    for r in room_out:
        cv2.putText(img, r["name"][:14], (r["seed_px"][0] - 40, r["seed_px"][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 0, 150), 1)
    cv2.imwrite(os.environ["PLAN_DEBUG"], cv2.resize(img, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA))
