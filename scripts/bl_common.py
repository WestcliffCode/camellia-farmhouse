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
