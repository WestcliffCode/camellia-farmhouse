"""Shared Blender helpers for the Camellia farmhouse build.

Loaded with exec() inside Blender by the stage scripts; every stage is
rebuildable: it removes only the collections it owns, then recreates them.
"""
import json
import math
import os

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
S = json.load(open(os.path.join(ROOT, "scripts", "structure.json")))
CEIL = S["ceil"]
FT = 0.3048


def PX(x, y):
    """Plan-image pixel -> metres."""
    return ((x - S["ref_px"][0]) / S["px_per_m"], (S["ref_px"][1] - y) / S["px_per_m"])


def face_in(bm, pts, toward):
    """Add a face whose normal points toward the given point (interior shells)."""
    vs = [bm.verts.new(p) for p in pts]
    try:
        f = bm.faces.new(vs)
    except ValueError:
        return None
    f.normal_update()
    c = f.calc_center_median()
    if f.normal.dot(Vector(toward) - c) < 0:
        f.normal_flip()
    return f


def get_col(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


def wipe_col(name):
    """Remove a collection this job owns, with its objects and orphaned meshes."""
    col = bpy.data.collections.get(name)
    if col is None:
        return
    for child in list(col.children):
        wipe_col(child.name)
    for ob in list(col.objects):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Light):
                bpy.data.lights.remove(data)
            elif isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
    bpy.data.collections.remove(col)


def new_obj(name, bm, col, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def add_prism(bm, outer, holes, z0, z1, caps=(True, True)):
    """Extrude a 2-D polygon with holes (CCW outer, CW holes) between z0 and z1."""
    rings = [outer] + list(holes)
    vb, vt = [], []
    for ring in rings:
        vb.append([bm.verts.new((x, y, z0)) for x, y in ring])
        vt.append([bm.verts.new((x, y, z1)) for x, y in ring])
    for rb, rt in zip(vb, vt):
        n = len(rb)
        for i in range(n):
            j = (i + 1) % n
            try:
                bm.faces.new((rb[i], rb[j], rt[j], rt[i]))
            except ValueError:
                pass
    flat_b = [v for r in vb for v in r]
    flat_t = [v for r in vt for v in r]
    tris = tessellate_polygon([[Vector((x, y, 0.0)) for x, y in ring] for ring in rings])
    for a, b, c in tris:
        if caps[1]:
            try:
                f = bm.faces.new((flat_t[a], flat_t[b], flat_t[c]))
                if f.calc_area() > 1e-9:
                    f.normal_update()
                    if f.normal.z < 0:
                        f.normal_flip()
            except ValueError:
                pass
        if caps[0]:
            try:
                f = bm.faces.new((flat_b[a], flat_b[b], flat_b[c]))
                if f.calc_area() > 1e-9:
                    f.normal_update()
                    if f.normal.z > 0:
                        f.normal_flip()
            except ValueError:
                pass


def add_box(bm, c, u, half_w, half_t, z0, z1):
    """Box centred at c (x, y), long axis u (unit 2-D), between z0 and z1."""
    ux, uy = u
    nx, ny = -uy, ux
    pts = [(c[0] - ux * half_w - nx * half_t, c[1] - uy * half_w - ny * half_t),
           (c[0] + ux * half_w - nx * half_t, c[1] + uy * half_w - ny * half_t),
           (c[0] + ux * half_w + nx * half_t, c[1] + uy * half_w + ny * half_t),
           (c[0] - ux * half_w + nx * half_t, c[1] - uy * half_w + ny * half_t)]
    add_prism(bm, pts, [], z0, z1)


def add_profile(bm, c, u, half_t, prof, flip=False):
    """Extrude a profile [(s, z)] lying in the wall plane across the wall thickness."""
    ux, uy = u
    nx, ny = -uy, ux
    front = [bm.verts.new((c[0] + ux * s + nx * half_t, c[1] + uy * s + ny * half_t, z)) for s, z in prof]
    back = [bm.verts.new((c[0] + ux * s - nx * half_t, c[1] + uy * s - ny * half_t, z)) for s, z in prof]
    n = len(prof)
    tris = tessellate_polygon([[Vector((s, z, 0.0)) for s, z in prof]])
    for a, b, d in tris:
        for vs in ((front[a], front[b], front[d]), (back[d], back[b], back[a])):
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
    for i in range(n):
        j = (i + 1) % n
        try:
            bm.faces.new((front[i], back[i], back[j], front[j]))
        except ValueError:
            pass


def arch_profile(w, spring, top, ztop, seg=20):
    """Lintel above an elliptical arch: solid between the arc and ztop."""
    pts = [(-w / 2, ztop), (-w / 2, spring)]
    for i in range(1, seg):
        a = math.pi * i / seg
        pts.append((-w / 2 * math.cos(a), spring + (top - spring) * math.sin(a)))
    pts += [(w / 2, spring), (w / 2, ztop)]
    return pts


def arch_spring(o):
    """Spring height of an arched opening: semicircle when the wall allows it."""
    return max(o["head"] - o["w"] / 2, o["head"] - 0.95)


def fix_normals(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def room(name):
    for r in S["rooms"]:
        if r["name"] == name:
            return r
    raise KeyError(name)


def room_bounds(name):
    r = room(name)
    xs = [p[0] for p in r["outer"]]
    ys = [p[1] for p in r["outer"]]
    return min(xs), min(ys), max(xs), max(ys)


def save():
    bpy.ops.wm.save_mainfile()


def pip(pt, ring):
    """Point-in-polygon (ring of (x, y))."""
    x, y = pt[0], pt[1]
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


def in_footprint(pt):
    return any(pip(pt, f["outer"]) for f in S["footprint"])


def uv_box(ob, layer="UVMap"):
    """World-scale box UVs in metres: u along the horizontal tangent, v up the face."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.get(layer) or bm.loops.layers.uv.new(layer)
    Z = Vector((0, 0, 1))
    for f in bm.faces:
        n = f.normal
        if abs(n.z) > 0.999 or n.length < 1e-6:
            for l in f.loops:
                l[uv].uv = (l.vert.co.x, l.vert.co.y)
        else:
            t = Z.cross(n).normalized()
            b = n.cross(t).normalized()
            for l in f.loops:
                l[uv].uv = (l.vert.co.dot(t), l.vert.co.dot(b))
    bm.to_mesh(me)
    bm.free()


def externalize_images():
    """Move packed Poly Haven textures to project-files/textures and reference them relatively."""
    tex = os.path.join(ROOT, "project-files", "textures")
    os.makedirs(tex, exist_ok=True)
    n = 0
    for img in bpy.data.images:
        if img.packed_file is None or img.source != "FILE":
            continue
        base = os.path.basename(img.filepath) or (img.name + ".png")
        dst = os.path.join(tex, base)
        with open(dst, "wb") as fh:
            fh.write(img.packed_file.data)
        img.unpack(method="REMOVE")
        img.filepath = "//textures/" + base
        img.reload()
        n += 1
    return n


def set_in(node, name, value):
    """Set a node input by name, tolerating disabled / renamed sockets."""
    for s in node.inputs:
        if s.name == name:
            try:
                s.default_value = value
            except Exception:
                pass
            return True
    return False


def assign(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


MATN = {
    "white": "MAT-paint_white", "charcoal": "MAT-paint_charcoal", "ceiling": "MAT-paint_ceiling",
    "trim": "MAT-trim_white", "siding": "MAT-siding_dark", "black": "MAT-metal_black",
    "hw": "MAT-hardware_black", "quartz": "MAT-quartz", "steel": "MAT-stainless", "brass": "MAT-brass",
    "porcelain": "MAT-porcelain", "mirror": "MAT-mirror", "glassdark": "MAT-glass_dark", "glass": "MAT-glass",
    "oak": "MAT-oak", "timber": "MAT-timber", "limestone": "MAT-limestone", "brick": "MAT-brick",
    "tile": "MAT-tile_marble", "floor_oak": "MAT-floor_oak", "concrete": "MAT-concrete",
}


def MAT(key):
    return bpy.data.materials[MATN.get(key, key)]


class Frame:
    """2-D working frame: s along u, d along the left normal of u, z up."""

    def __init__(self, origin, u):
        L = math.hypot(u[0], u[1])
        self.o = Vector((origin[0], origin[1]))
        self.u = Vector((u[0] / L, u[1] / L))
        self.n = Vector((-self.u.y, self.u.x))

    def p(self, s, d, z=0.0):
        v = self.o + self.u * s + self.n * d
        return (v.x, v.y, z)

    def xy(self, s, d):
        v = self.o + self.u * s + self.n * d
        return (v.x, v.y)


WORLD = Frame((0, 0), (1, 0))      # s = x, d = y


class Builder:
    """Collects boxes per material key, then emits one object per key."""

    def __init__(self, name, col):
        self.name, self.col, self.bms = name, col, {}

    def bm(self, key):
        if key not in self.bms:
            self.bms[key] = bmesh.new()
        return self.bms[key]

    def box(self, key, F, s0, s1, d0, d1, z0, z1):
        b = self.bm(key)
        s0, s1 = min(s0, s1), max(s0, s1)
        d0, d1 = min(d0, d1), max(d0, d1)
        vs = [b.verts.new(F.p(s, d, z)) for z in (z0, z1) for (s, d) in ((s0, d0), (s1, d0), (s1, d1), (s0, d1))]
        for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            b.faces.new([vs[i] for i in idx])

    def hexa(self, key, pts8):
        """Arbitrary 8-corner solid: 4 bottom points then 4 top points (same winding)."""
        b = self.bm(key)
        vs = [b.verts.new(p) for p in pts8]
        for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            b.faces.new([vs[i] for i in idx])

    def cyl(self, key, center, r, z0, z1, seg=16, r2=None):
        b = self.bm(key)
        m = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2,
                                  depth=z1 - z0)
        for v in m["verts"]:
            v.co.x += center[0]
            v.co.y += center[1]
            v.co.z += (z0 + z1) / 2

    def rod(self, key, a, b_, r, seg=10):
        """Cylinder between two 3-D points."""
        b = self.bm(key)
        a, b_ = Vector(a), Vector(b_)
        d = b_ - a
        m = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
        rot = d.to_track_quat("Z", "Y").to_matrix()
        mid = (a + b_) / 2
        for v in m["verts"]:
            v.co = rot @ v.co + mid

    def ellipsoid(self, key, center, rx, ry, rz, seg=20):
        b = self.bm(key)
        m = bmesh.ops.create_uvsphere(b, u_segments=seg, v_segments=seg // 2, radius=1.0)
        for v in m["verts"]:
            v.co = Vector((v.co.x * rx + center[0], v.co.y * ry + center[1], v.co.z * rz + center[2]))

    def finish(self, smooth_keys=()):
        out = []
        for key, b in self.bms.items():
            bmesh.ops.recalc_face_normals(b, faces=b.faces)
            ob = new_obj(f"GEO-{self.name}_{key}", b, self.col, smooth=key in smooth_keys)
            assign(ob, MAT(key))
            uv_box(ob)
            out.append(ob)
        self.bms = {}
        return out


def cab_doors(B, key, F, s0, s1, d_face, z0, z1, n, pulls="v", gap=0.004):
    """Shaker-style door or drawer fronts across s0..s1 on the plane d = d_face (facing +d)."""
    w = (s1 - s0) / n
    for i in range(n):
        a, b = s0 + i * w + gap / 2, s0 + (i + 1) * w - gap / 2
        B.box(key, F, a, b, d_face, d_face + 0.016, z0 + gap / 2, z1 - gap / 2)
        fr = 0.055
        for (sa, sb, za, zb) in ((a, a + fr, z0, z1), (b - fr, b, z0, z1), (a + fr, b - fr, z0, z0 + fr),
                                 (a + fr, b - fr, z1 - fr, z1)):
            B.box(key, F, sa, sb, d_face + 0.016, d_face + 0.021, za + gap / 2, zb - gap / 2)
        if pulls == "v":
            sx = b - 0.035 if i % 2 == 0 else a + 0.035
            zc = z0 + 0.22 if z0 > 1.2 else z1 - 0.22
            B.box("hw", F, sx - 0.006, sx + 0.006, d_face + 0.021, d_face + 0.05, zc - 0.07, zc + 0.07)
        elif pulls == "h":
            B.box("hw", F, (a + b) / 2 - 0.08, (a + b) / 2 + 0.08, d_face + 0.021, d_face + 0.05,
                  (z0 + z1) / 2 - 0.006, (z0 + z1) / 2 + 0.006)


def base_cabinet(B, F, s0, s1, d_wall, z_top=0.885, depth=0.6, key="trim", n=None, drawers=False, top="quartz",
                 overhang=0.02, splash=0.0):
    """Base cabinet run against the plane d = d_wall, extending toward +d."""
    n = n or max(1, round((s1 - s0) / 0.5))
    B.box("hw", F, s0, s1, d_wall + 0.02, d_wall + depth - 0.07, 0.0, 0.10)                  # toe kick
    B.box(key, F, s0, s1, d_wall, d_wall + depth - 0.016, 0.10, z_top)
    if drawers:
        cab_doors(B, key, F, s0, s1, d_wall + depth - 0.016, 0.10, z_top - 0.2, n, pulls="h")
        cab_doors(B, key, F, s0, s1, d_wall + depth - 0.016, z_top - 0.2, z_top, n, pulls="h")
    else:
        cab_doors(B, key, F, s0, s1, d_wall + depth - 0.016, 0.10, z_top, n)
    if top:
        B.box(top, F, s0 - overhang, s1 + overhang, d_wall, d_wall + depth + overhang + 0.02, z_top, z_top + 0.03)
    if splash > 0:
        B.box(top or "quartz", F, s0, s1, d_wall, d_wall + 0.015, z_top + 0.03, z_top + 0.03 + splash)
