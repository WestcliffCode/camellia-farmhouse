"""Stage 5: golden-hour sky and sun, practical lights, render settings. Owns COL-lights and WORLD-camellia."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-lights")
col = get_col("COL-lights")
scene = bpy.context.scene
K = json.loads(scene["camellia_shell"])
LAMPS = json.loads(scene.get("camellia_lamps", "[]"))
WARM = (1.0, 0.74, 0.50)
# Recessed cans are spot lights (not area lights) so the whole rig survives glTF export (KHR_lights_punctual).
CAN_GAIN = 3.0                       # a spot is a masked point light: ~3x the watts of the area disc it replaces
CAN_CONE = (math.radians(125), 0.6)
SUN_ELEV = math.radians(6.0)        # golden hour sliding into dusk
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

# ------------------------------------------------------------------ world: captured golden-hour sky + a sun lamp for the key
# The sky is the Poly Haven HDRI `magalies_field_sunset` (a real clear-sky sunset over a field). Its sun position is
# measured from the image, the map is rotated so that sun sits behind the house, and the sun lamp is aligned with it.
import shutil
HDRI_ID = "magalies_field_sunset"
hdr = next((i for i in bpy.data.images if HDRI_ID in i.name or HDRI_ID in i.filepath), None)
world = bpy.data.worlds.get("WORLD-camellia") or bpy.data.worlds.new("WORLD-camellia")
scene.world = world
world.use_nodes = True
nt = world.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
nt.links.new(bg.outputs[0], out.inputs["Surface"])
HDRI_SUN = None
SUN_COLOR = (1.0, 0.48, 0.20)                           # fallback when no captured sky is present
if hdr is not None:
    src = bpy.path.abspath(hdr.filepath)
    dst = os.path.join(TEX_DIR, os.path.basename(src) or HDRI_ID + "_2k.hdr")
    if hdr.packed_file is not None:
        with open(dst, "wb") as fh:
            fh.write(hdr.packed_file.data)
        hdr.unpack(method="REMOVE")
    elif os.path.abspath(src) != os.path.abspath(dst) and os.path.exists(src):
        shutil.copy(src, dst)
    hdr.filepath = "//textures/" + os.path.basename(dst)
    hdr.reload()
    hdr.use_fake_user = True
    w_, h_ = hdr.size
    px = np.empty(w_ * h_ * 4, np.float32)
    hdr.pixels.foreach_get(px)
    rgb_ = px.reshape(h_, w_, 4)[..., :3]
    lum = rgb_ @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    thr = np.partition(lum.ravel(), -200)[-200]
    ys_, xs_ = np.nonzero(lum >= thr)
    disc = rgb_[lum >= np.partition(lum.ravel(), -400)[-400]].mean(0)          # the captured sun disc
    SUN_COLOR = tuple(float(c) for c in disc / disc.max())                     # lamp takes its colour from the reference sky
    wts = lum[ys_, xs_]
    u = float(np.average((xs_ + 0.5) / w_, weights=wts))
    v = float(np.average((ys_ + 0.5) / h_, weights=wts))
    phi, theta = (u - 0.5) * 2 * math.pi, (v - 0.5) * math.pi
    s_dir = Vector((-math.cos(phi) * math.cos(theta), math.sin(phi) * math.cos(theta), math.sin(theta)))
    HDRI_SUN = (math.degrees(theta), math.degrees(math.atan2(s_dir.y, s_dir.x)), float(lum.max()))
    SUN_ELEV = max(math.radians(4.0), theta)          # lamp follows the captured sun (kept clear of the horizon line)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = hdr
    want = math.atan2(SUN_DIR_XY.y, SUN_DIR_XY.x)
    mp.inputs["Rotation"].default_value = (0.0, 0.0, math.atan2(s_dir.y, s_dir.x) - want)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.30        # dusk: the captured sky is dimmed so sun and practicals carry the scene
    print("HDRI sun: elevation %.1f deg, image azimuth %.1f deg, peak luminance %.0f; lamp elevation %.1f deg"
          % (HDRI_SUN[0], HDRI_SUN[1], HDRI_SUN[2], math.degrees(SUN_ELEV)))
else:
    sky = nt.nodes.new("ShaderNodeTexSky")
    types = enum_ids(bpy.types.ShaderNodeTexSky, "sky_type")
    sky.sky_type = next((t for t in types if "MULTI" in t), types[-1])
    sky.sun_elevation = SUN_ELEV
    for attr, val in (("sun_disc", False), ("sun_rotation", math.atan2(SUN_DIR_XY.x, SUN_DIR_XY.y))):
        if hasattr(sky, attr):
            setattr(sky, attr, val)
    bg.inputs["Strength"].default_value = 0.13
    nt.links.new(sky.outputs[0], bg.inputs["Color"])
    print("HDRI not found; using the procedural sky")
scene["camellia_hdri_sun"] = json.dumps(HDRI_SUN)

sd = bpy.data.lights.new("LGT-sun", "SUN")
sd.color = SUN_COLOR
# strength holds the luminance the scene was balanced at, whatever the measured colour (2.39 = 4.2 x the luminance of the old hand-set colour)
sd.energy = 2.39 / (0.2126 * SUN_COLOR[0] + 0.7152 * SUN_COLOR[1] + 0.0722 * SUN_COLOR[2])
scene["camellia_sun_color"] = json.dumps([round(c, 3) for c in SUN_COLOR])
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
    "great_room": (1.9, 16), "office": (1.6, 32), "primary_suite": (1.7, 20), "primary_bath": (1.6, 14),
    "bedroom_2": (1.9, 12), "bedroom_3": (1.9, 12), "bedroom_4": (1.9, 12), "game_room": (1.9, 14),
    "pantry": (1.7, 12), "family_foyer": (1.6, 12), "utility": (1.6, 12), "primary_closet": (1.6, 10),
    "primary_hall": (1.4, 10), "bed_hall": (1.6, 10), "bed_hall_s": (1.4, 10), "hall_bath": (1.4, 12),
    "powder": (1.2, 10), "jj_bath_a": (1.4, 11), "jj_bath_b": (1.4, 11), "back_vestibule": (1.3, 9),
    "garage": (2.2, 36), "foyer": (1.8, 10), "primary_wc": (1.2, 8), "closet_b3": (1.5, 8),
    "holiday": (1.5, 8), "mud_vestibule": (1.2, 8), "stair": (1.6, 9), "portico": (1.6, 10),
    "storage_a": (2.0, 7), "storage_b": (2.0, 8), "linen": (1.2, 5), "closet_b2": (2.0, 6), "hutch_niche": (1.6, 6),
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
            off = 0.35 if min(x1 - x0, y1 - y0) > 1.0 else 0.12
            if not all(pip((x + dx, y + dy), r["outer"]) for dx, dy in ((off, 0), (-off, 0), (0, off), (0, -off))):
                continue
            z = ceil_z(rn, x, y)
            add_light(f"LGT-can_{rn}_{i}{j}", "SPOT", (x, y, z - 0.012), watts * CAN_GAIN, size=0.05, spot=CAN_CONE)
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
uv_box(tob)

POWER = {"table": 22, "floor": 30, "pendant": 26, "chandelier": 55, "sconce": 12, "can": 12}
for i, (x, y, z, kind, rn) in enumerate(LAMPS):
    if kind == "can":
        add_light(f"LGT-{kind}_{rn}_{i}", "SPOT", (x, y, z), POWER[kind] * CAN_GAIN, size=0.05, spot=CAN_CONE)
    else:
        add_light(f"LGT-{kind}_{rn}_{i}", "POINT", (x, y, z), POWER[kind], size=0.05 if kind != "chandelier" else 0.3)

# kitchen under-cabinet strips and tray wash
KF = Frame(PX(1207, 1260), (1, 1))
ang = math.atan2(KF.u.y, KF.u.x)
for s0, s1 in ((1.04, 2.05), (3.31, 5.32)):
    n = max(2, round((s1 - s0) / 0.45))
    for k in range(n):
        c = KF.p(s0 + (k + 0.5) * (s1 - s0) / n, 0.062 + 0.2, 1.435)
        add_light("LGT-undercab", "SPOT", c, 9, size=0.02, spot=(math.radians(150), 0.8))
add_light("LGT-hood", "SPOT", KF.p(2.68, 0.36, 1.73), 36, size=0.05, spot=(math.radians(140), 0.7))
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
uv_box(lan)
# porch ceiling lights
for (x, y) in ((9.5, 1.6), (16.9, 1.6), (9.0, 15.2), (7.0, 15.2), (14.2, 19.0), (15.0, 22.4), (15.0, 24.8),
               (17.2, 22.4), (17.2, 24.8), (19.3, 22.4), (19.3, 24.8)):
    add_light("LGT-porch", "SPOT", (x, y, CEIL - 0.015), 24 * CAN_GAIN, size=0.05, spot=CAN_CONE)

# bonus room: cans along the flat collar, plus the dormer
ZC = K["ZF"] + 2.74 - 0.012
for yy in (2.2, 4.2, 6.2, 8.2, 10.2):
    add_light("LGT-can_bonus", "SPOT", (22.52, yy, ZC), 16 * CAN_GAIN, size=0.05, spot=CAN_CONE)
add_light("LGT-can_bonus_dormer", "SPOT", (25.2, 6.15, K["ZD"] - 0.012), 14 * CAN_GAIN, size=0.05, spot=CAN_CONE)
add_light("LGT-can_stair", "SPOT", (19.8, (K["YA0"] + K["YA1"]) / 2, K["ZA"] - 0.012), 12 * CAN_GAIN, size=0.05, spot=CAN_CONE)

print("cans", ncan, "lamp lights", len(LAMPS), "total lights", len([o for o in col.objects if o.type == "LIGHT"]))
