"""Stage 5: golden-hour sky and sun, practical lights, render settings. Owns COL-lights and WORLD-camellia."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-lights")
col = get_col("COL-lights")
scene = bpy.context.scene
K = json.loads(scene["camellia_shell"])
LAMPS = json.loads(scene.get("camellia_lamps", "[]"))
WARM = (1.0, 0.74, 0.50)
SUN_ELEV = math.radians(11.0)
SUN_DIR_XY = Vector((-0.34, 1.0)).normalized()      # where the sun sits, seen from the house (behind it, a little left)


def enum_ids(rna_type, prop):
    return [i.identifier for i in rna_type.bl_rna.properties[prop].enum_items]


# ------------------------------------------------------------------ render engine and colour
try:
    scene.render.engine = "CYCLES"
except TypeError as e:
    print("engine:", e)
cy = scene.cycles
cy.device = "GPU"
cy.samples = 384
cy.preview_samples = 32
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02
cy.use_denoising = True
cy.max_bounces = 10
cy.diffuse_bounces = 5
cy.glossy_bounces = 4
cy.transmission_bounces = 10
cy.transparent_max_bounces = 16
cy.sample_clamp_indirect = 8.0
cy.caustics_reflective = False
cy.caustics_refractive = False
vs = scene.view_settings
if "AgX" in enum_ids(bpy.types.ColorManagedViewSettings, "view_transform"):
    vs.view_transform = "AgX"
try:
    vs.look = "AgX - Medium High Contrast"
except TypeError:
    pass
vs.exposure = 0.6
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

# ------------------------------------------------------------------ world: physical sky for ambient + a sun lamp for the key
world = bpy.data.worlds.get("WORLD-camellia") or bpy.data.worlds.new("WORLD-camellia")
scene.world = world
world.use_nodes = True
nt = world.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
sky = nt.nodes.new("ShaderNodeTexSky")
types = enum_ids(bpy.types.ShaderNodeTexSky, "sky_type")
pick = next((t for t in types if "MULTI" in t), None) or next((t for t in types if "NISHITA" in t), None) or types[-1]
sky.sky_type = pick
for attr, val in (("sun_elevation", SUN_ELEV), ("sun_disc", False), ("sun_intensity", 1.0),
                  ("air_density", 1.0), ("ozone_density", 1.0)):
    if hasattr(sky, attr):
        try:
            setattr(sky, attr, val)
        except Exception:
            pass
for attr in ("dust_density", "aerosol_density"):
    if hasattr(sky, attr):
        try:
            setattr(sky, attr, 2.0)
        except Exception:
            pass
# rotate the sky so its glow sits behind the sun lamp (sky's sun is at +Y when rotation is 0)
if hasattr(sky, "sun_rotation"):
    sky.sun_rotation = math.atan2(SUN_DIR_XY.x, SUN_DIR_XY.y)
bg.inputs["Strength"].default_value = 0.22
nt.links.new(sky.outputs[0], bg.inputs["Color"])
nt.links.new(bg.outputs[0], out.inputs["Surface"])
print("sky type", pick, "of", types)

sd = bpy.data.lights.new("LGT-sun", "SUN")
sd.energy = 5.5
sd.color = (1.0, 0.63, 0.36)
sd.angle = math.radians(1.6)
sun = bpy.data.objects.new("LGT-sun", sd)
col.objects.link(sun)
to_sun = Vector((SUN_DIR_XY.x * math.cos(SUN_ELEV), SUN_DIR_XY.y * math.cos(SUN_ELEV), math.sin(SUN_ELEV)))
sun.rotation_euler = to_sun.to_track_quat("Z", "Y").to_euler()      # a sun lamp shines along its -Z
sun.location = (13, 40, 12)


# ------------------------------------------------------------------ practicals
def add_light(name, kind, loc, power, size=0.08, color=WARM, rot=None, spot=None, shape=None, size_y=None):
    d = bpy.data.lights.new(name, kind)
    d.energy = power
    d.color = color
    if kind == "AREA":
        d.shape = shape or "DISK"
        d.size = size
        if size_y:
            d.size_y = size_y
    else:
        d.shadow_soft_size = size
    if spot:
        d.spot_size, d.spot_blend = spot
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    ob.visible_camera = False
    ob.visible_transmission = False
    ob.visible_glossy = False
    col.objects.link(ob)
    return ob


def ceil_z(room_name, x, y):
    if room_name in ("primary_suite", "game_room"):
        x0, y0, x1, y1 = room_bounds(room_name)
        return CEIL + ((x1 - x0) / 2 - abs(x - (x0 + x1) / 2)) * (5.0 / 12.0)
    if room_name == "garage":
        return 2.743
    if room_name == "foyer":
        return 4.27
    return CEIL


kt = K["KITCHEN_TRAY"]
CAN_ROOMS = {  # room: (spacing, watts)
    "great_room": (1.9, 16), "office": (1.7, 14), "primary_suite": (1.9, 13), "primary_bath": (1.6, 14),
    "bedroom_2": (1.9, 12), "bedroom_3": (1.9, 12), "bedroom_4": (1.9, 12), "game_room": (1.9, 14),
    "pantry": (1.7, 12), "family_foyer": (1.6, 12), "utility": (1.6, 12), "primary_closet": (1.6, 10),
    "primary_hall": (1.4, 10), "bed_hall": (1.6, 10), "bed_hall_s": (1.4, 10), "hall_bath": (1.4, 12),
    "powder": (1.2, 10), "jj_bath_a": (1.4, 11), "jj_bath_b": (1.4, 11), "back_vestibule": (1.3, 9),
    "garage": (2.6, 22), "foyer": (1.8, 10), "primary_wc": (1.2, 8), "closet_b3": (1.5, 8),
    "holiday": (1.5, 8), "mud_vestibule": (1.2, 8), "stair": (1.6, 9), "portico": (1.6, 10),
}
trim = bmesh.new()
ncan = 0
for rn, (sp, watts) in CAN_ROOMS.items():
    r = room(rn)
    x0, y0, x1, y1 = room_bounds(rn)
    nx = max(1, round((x1 - x0) / sp))
    ny = max(1, round((y1 - y0) / sp))
    for i in range(nx):
        for j in range(ny):
            x = x0 + (i + 0.5) * (x1 - x0) / nx
            y = y0 + (j + 0.5) * (y1 - y0) / ny
            if not pip((x, y), r["outer"]) or any(pip((x, y), h) for h in r["holes"]):
                continue
            if rn == "great_room" and pip((x, y), kt):
                continue
            # keep cans off the walls
            if not all(pip((x + dx, y + dy), r["outer"]) for dx, dy in ((0.35, 0), (-0.35, 0), (0, 0.35), (0, -0.35))):
                continue
            z = ceil_z(rn, x, y)
            add_light(f"LGT-can_{rn}_{i}{j}", "AREA", (x, y, z - 0.012), watts, size=0.11)
            m = bmesh.ops.create_circle(trim, cap_ends=True, radius=0.055, segments=16)
            for v in m["verts"]:
                v.co = Vector((v.co.x + x, v.co.y + y, z - 0.004))
            ncan += 1
tob = new_obj("GEO-can_lenses", trim, col)
lens = bpy.data.materials.get("MAT-can_lens") or bpy.data.materials.new("MAT-can_lens")
lens.use_nodes = True
lb = next(n for n in lens.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
set_in(lb, "Base Color", (1, 0.9, 0.78, 1))
set_in(lb, "Emission Color", (1.0, 0.78, 0.55, 1))
set_in(lb, "Emission Strength", 6.0)
assign(tob, lens)

POWER = {"table": 22, "floor": 30, "pendant": 26, "chandelier": 55, "sconce": 12, "can": 12}
for i, (x, y, z, kind, rn) in enumerate(LAMPS):
    if kind == "can":
        add_light(f"LGT-{kind}_{rn}_{i}", "AREA", (x, y, z), POWER[kind], size=0.11)
    else:
        add_light(f"LGT-{kind}_{rn}_{i}", "POINT", (x, y, z), POWER[kind], size=0.05 if kind != "chandelier" else 0.3)

# kitchen under-cabinet strips and tray wash
KF = Frame(PX(1207, 1260), (1, 1))
ang = math.atan2(KF.u.y, KF.u.x)
for s0, s1 in ((1.04, 2.05), (3.31, 5.32)):
    c = KF.p((s0 + s1) / 2, 0.062 + 0.2, 1.435)
    add_light("LGT-undercab", "AREA", c, 9 * (s1 - s0), size=s1 - s0, size_y=0.03, shape="RECTANGLE", rot=(0, 0, ang))
add_light("LGT-hood", "AREA", KF.p(2.68, 0.36, 1.73), 14, size=0.5)
# fireplace glow
add_light("LGT-fire_family", "POINT", (PX(646, 0)[0] + 0.25, 10.47, 0.62), 18, size=0.12, color=(1.0, 0.42, 0.14))
# exterior lanterns: front door, garage doors, back porch
ext = bmesh.new()
for (x, y, z) in ((11.9, -0.12, 2.15), (14.45, -0.12, 2.15), (26.45, 5.9, 2.3), (26.45, 0.75, 2.3), (26.45, 10.9, 2.3),
                  (6.0, 14.05, 2.2), (20.6, 22.2, 2.2)):
    add_light("LGT-lantern", "POINT", (x, y, z), 20, size=0.04)
    m = bmesh.ops.create_cube(ext, size=1.0)
    for v in m["verts"]:
        v.co = Vector((v.co.x * 0.14 + x, v.co.y * 0.14 + y, v.co.z * 0.06 + z + 0.2))
lan = new_obj("GEO-lantern_caps", ext, col)
assign(lan, MAT("hw"))
# porch ceiling lights
for (x, y) in ((9.5, 1.6), (16.9, 1.6), (9.0, 15.2), (16.5, 23.6), (14.2, 19.0)):
    add_light("LGT-porch", "AREA", (x, y, CEIL - 0.015), 14, size=0.12)

# bonus room: cans along the flat collar, plus the dormer
ZC = K["ZF"] + 2.74 - 0.012
for yy in (2.2, 4.2, 6.2, 8.2, 10.2):
    add_light("LGT-can_bonus", "AREA", (22.52, yy, ZC), 16, size=0.11)
add_light("LGT-can_bonus_dormer", "AREA", (25.2, 6.15, K["ZD"] - 0.012), 14, size=0.11)
add_light("LGT-can_stair", "AREA", (19.8, (K["YA0"] + K["YA1"]) / 2, K["ZA"] - 0.012), 12, size=0.11)

print("cans", ncan, "lamp lights", len(LAMPS), "total lights", len([o for o in col.objects if o.type == "LIGHT"]))
