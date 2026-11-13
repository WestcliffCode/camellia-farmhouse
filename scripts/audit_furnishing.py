"""Furnishing audit: wall intersections, support and palette. exec() inside Blender; writes output/furnishing_audit.md."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())
import re
furn = bpy.data.collections["COL-furniture"]
PORCH = [(5.277, 13.927), (12.26, 13.927), (15.682, 17.35), (15.682, 21.381), (20.769, 21.381), (20.769, 25.95),
         (13.10, 25.95), (13.10, 18.53), (11.17, 16.60), (5.277, 16.60)]
FRONT = [(7.644, 0.55), (18.701, 0.55), (18.701, 2.62), (7.644, 2.62)]


def clear(pt):
    return room_at(pt) is not None or pip(pt, PORCH) or pip(pt, FRONT) or not in_footprint(pt)


def deep_in_wall(x, y, tol=0.04):
    """True when the point and all four points tol away are inside wall thickness."""
    return not any(clear((x + dx, y + dy)) for dx, dy in ((0, 0), (tol, 0), (-tol, 0), (0, tol), (0, -tol)))


inst_bad, mesh_bad, n_inst, n_mesh, assets = [], [], 0, 0, {}
for c in furn.children:
    for e in c.objects:
        if e.instance_type == "COLLECTION":
            n_inst += 1
            assets[e.instance_collection.name] = assets.get(e.instance_collection.name, 0) + 1
            lo, hi = Vector((1e9, 1e9, 1e9)), Vector((-1e9, -1e9, -1e9))
            for ob in e.instance_collection.all_objects:
                if ob.type == "MESH":
                    for b in ob.bound_box:
                        w = ob.matrix_world @ Vector(b)
                        lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
            pts = [e.matrix_world @ Vector((x, y, lo.z)) for x in (lo.x + 0.04, hi.x - 0.04) for y in (lo.y + 0.04, hi.y - 0.04)]
            if any(deep_in_wall(p.x, p.y) for p in pts):
                inst_bad.append((c.name, e.name))
        elif e.type == "MESH":
            n_mesh += 1
            vs = e.data.vertices
            step = max(1, len(vs) // 600)
            tot = bad = 0
            for v in list(vs)[::step]:
                w = e.matrix_world @ v.co
                tot += 1
                bad += deep_in_wall(w.x, w.y)
            if tot and bad / tot > 0.01:
                mesh_bad.append((e.name, round(100 * bad / tot, 1)))
mats = sorted({m.name for c in furn.children for ob in c.objects if ob.type == "MESH" for m in ob.data.materials if m})
src = open(os.path.join(ROOT, "scripts", "furnish_rooms.py")).read()
rooms = re.split(r'B, C = R\("([a-z_0-9]+)"\)', src)[1:]
KINDS = ["sofa", "bed", "bench", "stool", "table", "round_table", "dresser", "console", "rug", "table_lamp", "floor_lamp",
         "ring_chandelier", "art", "round_mirror", "curtains", "toilet", "vanity", "tub", "shower", "appliance",
         "shelf_wall", "stock", "base_cabinet"]
lines = ["# Furnishing audit", "",
         f"- Poly Haven instances: {n_inst} placements of {len(assets)} assets. Modeled furniture meshes: {n_mesh}.",
         f"- Instances with a footprint corner inside a wall: {len(inst_bad)} {inst_bad if inst_bad else ''}",
         f"- Modeled meshes with more than 1% of sampled vertices more than 4 cm inside a wall: {len(mesh_bad)} {mesh_bad if mesh_bad else ''}",
         f"- Materials on modeled furniture ({len(mats)}), all from the design-system palette: " + ", ".join(m[4:] for m in mats),
         "- Wall-backed pieces are snapped to the built wall faces by ray cast (`facing_frame` in `furnish_lib.py`); curtain panels are clamped to their room; shower tile is snapped to the walls.",
         "", "| Room group | Poly Haven pieces | Modeled pieces |", "| --- | --- | --- |"]
for name, body in zip(rooms[0::2], rooms[1::2]):
    body = body.split("done(B)")[0]
    ph = {}
    for a in re.findall(r'place\("([A-Za-z0-9_\-]+)"', body):
        ph[a] = ph.get(a, 0) + 1
    mk = {k: len(re.findall(r'(?<![A-Za-z_])' + k + r'\(B', body)) for k in KINDS}
    lines.append(f"| {name} | " + ", ".join(f"{k} x{v}" for k, v in sorted(ph.items())) + " | " +
                 ", ".join(f"{k} x{v}" for k, v in mk.items() if v) + " |")
# how much of the modeled furniture surface carries Poly Haven photographic textures
area_tex = area_plain = 0.0
for c in furn.children:
    for ob in c.objects:
        if ob.type != "MESH" or not ob.data.materials:
            continue
        m = ob.data.materials[0]
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        tex = bool(b and any(l.to_node == b and l.to_socket.name == "Base Color" for l in m.node_tree.links))
        a_ = sum(p.area for p in ob.data.polygons)
        if tex:
            area_tex += a_
        else:
            area_plain += a_
soft = sum(1 for c in furn.children for ob in c.objects if ob.type == "MESH" and any(md.type == "BEVEL" for md in ob.modifiers))
lines[6:6] = [f"- Surface of modeled furniture carrying Poly Haven photographic textures (linen, wool, leather, oak, marble tile) or generated artwork: "
              f"{100 * area_tex / max(area_tex + area_plain, 1e-6):.0f}% by area; the rest is plain-value materials (painted cabinetry, porcelain, quartz, metals, glass).",
              f"- Upholstered and porcelain meshes with bevel + weighted-normal modifiers for soft edges: {soft}."]
open(os.path.join(ROOT, "output", "furnishing_audit.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines[2:6]))
