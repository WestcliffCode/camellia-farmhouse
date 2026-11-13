"""Direct-sun coverage per room for a set of sun azimuths (run inside Blender on the built scene).

For every room: a 15 x 15 grid at six heights from 0.4 to 2.7 m (so beams from high windows count); a point counts as sunlit when a ray toward the sun leaves the house
without hitting anything but glass. Trees, porches and furniture are included. Prints a table; the chosen azimuth
in the first column is the sunset preset lighting.py uses, the second is its sunrise preset.
"""
import bpy, math
from mathutils import Vector
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

AZIMUTHS = (-28.0, 152.0, -18.8, -45.0, 135.0, 165.0)      # first two: the sunset and sunrise presets          # degrees from the house's back axis toward the west
ELEV = math.radians(4.1)
scene = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()


def is_glass(ob, idx):
    try:
        me = ob.evaluated_get(dg).data
        m = me.materials[me.polygons[idx].material_index]
        return bool(m) and "glass" in m.name.lower()
    except Exception:
        return False


def sunlit(p, d):
    ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, p, d, distance=400)
    n = 0
    while ok and is_glass(ob, idx) and n < 6:
        ok, loc, nor, idx, ob, mw = scene.ray_cast(dg, loc + d * 0.02, d, distance=400)
        n += 1
    return not ok


pts = {}
for r in S["rooms"]:
    xs = [p[0] for p in r["outer"]]
    ys = [p[1] for p in r["outer"]]
    P = []
    for i in range(15):
        for j in range(15):
            x = min(xs) + (i + 0.5) / 15 * (max(xs) - min(xs))
            y = min(ys) + (j + 0.5) / 15 * (max(ys) - min(ys))
            if pip((x, y), r["outer"]) and not any(pip((x, y), h) for h in r.get("holes", [])):
                P += [Vector((x, y, z)) for z in (0.4, 0.9, 1.4, 1.9, 2.3, 2.7)]
    pts[r["name"]] = P

res = {}
for az in AZIMUTHS:
    a = math.radians(az)
    d = Vector((math.sin(a) * math.cos(ELEV), math.cos(a) * math.cos(ELEV), math.sin(ELEV)))
    res[az] = {nm: sum(sunlit(p, d) for p in P) for nm, P in pts.items()}

names = sorted((n for n in pts if any(res[a][n] for a in res)), key=lambda n: -res[AZIMUTHS[0]][n])
print("room".ljust(18), *[f"{a:>10}" for a in AZIMUTHS])
for n in names:
    print(n.ljust(18), *[f"{res[a][n]:4d}/{len(pts[n]):<4d}".rjust(10) for a in AZIMUTHS])
print("summed fraction".ljust(18), *[f"{sum(res[a][n] / max(len(pts[n]), 1) for n in names):10.2f}" for a in AZIMUTHS])
