"""Stage 6: still cameras for every room, exterior heroes and a walkthrough rig. Owns COL-cameras."""
exec(open("/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse/scripts/bl_common.py").read())

wipe_col("COL-cameras")
col = get_col("COL-cameras")
scene = bpy.context.scene
K = json.loads(scene["camellia_shell"])
ZB = K["ZF"]

# name: (location, target, lens mm, shift_y)   interiors are levelled so verticals stay upright
STILLS = [
    ("ext_front", (13.2, -21.0, 1.75), (13.2, 4.0), 32, 0.16),
    ("ext_front_left", (-9.5, -17.0, 1.75), (11.0, 5.0), 28, 0.14),
    ("ext_back", (10.5, 40.0, 1.75), (14.0, 16.0), 30, 0.14),
    ("ext_garage", (41.0, -9.0, 1.75), (24.0, 6.0), 30, 0.14),
    ("foyer", (13.17, 6.75, 1.55), (13.17, 2.8), 15, 0.16),
    ("family", (14.3, 8.3, 1.55), (9.6, 11.2), 18, -0.06),
    ("family_from_hearth", (8.7, 12.95, 1.55), (13.6, 9.3), 18, -0.06),
    ("kitchen", (12.6, 13.2, 1.55), (17.2, 11.6), 18, -0.04),
    ("kitchen_from_dining", (17.5, 16.9, 1.55), (15.3, 12.6), 18, -0.04),
    ("dining", (16.25, 15.75, 1.5), (18.6, 19.6), 17, -0.04),
    ("primary_suite", (21.45, 21.85, 1.55), (24.4, 25.0), 16, -0.04),
    ("primary_suite_fire", (25.75, 25.45, 1.5), (21.4, 22.9), 17, -0.04),
    ("primary_bath", (22.7, 18.55, 1.55), (26.3, 19.9), 15, -0.04),
    ("office", (18.35, 3.15, 1.5), (15.9, 5.9), 15, -0.04),
    ("bedroom_2", (7.95, 6.35, 1.5), (10.8, 4.2), 16, -0.05),
    ("bedroom_3", (4.55, 0.8, 1.5), (6.9, 3.2), 16, -0.05),
    ("bedroom_4", (0.55, 8.1, 1.5), (2.8, 5.2), 16, -0.05),
    ("game_room", (1.6, 10.85, 1.5), (3.2, 15.6), 15, 0.0),
    ("bonus_room", (22.5, 10.7, ZB + 1.45), (22.6, 3.0), 16, -0.05),
    ("hall_bath", (6.6, 10.75, 1.5), (5.2, 9.6), 14, -0.05),
    ("jj_bath", (1.6, 4.15, 1.5), (0.8, 1.6), 14, -0.05),
    ("mudroom", (21.25, 12.1, 1.5), (22.4, 16.2), 15, -0.04),
    ("utility", (23.05, 13.75, 1.5), (25.5, 11.6), 15, -0.05),
    ("pantry", (19.95, 13.95, 1.5), (17.0, 11.2), 15, -0.03),
    ("primary_closet", (23.0, 15.4, 1.5), (26.8, 15.5), 15, -0.04),
    ("garage", (25.3, 10.4, 1.6), (20.0, 3.5), 16, 0.0),
    ("storage", (2.2, 8.0, 1.5), (1.2, 9.7), 16, -0.04),
    ("linen_hall", (21.9, 17.0, 1.5), (20.3, 17.0), 14, -0.04),
    ("outdoor_living", (13.9, 21.9, 1.6), (19.6, 23.8), 17, 0.02),
    # close-ups of the pieces modeled for this house (upholstery, bed, bath fixtures, range wall)
    ("detail_sofa", (11.0, 12.3, 1.15), (12.9, 10.5), 32, -0.06),
    ("detail_bed", (22.6, 23.3, 1.25), (23.7, 25.6), 30, -0.08),
    ("detail_bath", (23.3, 19.0, 1.35), (25.9, 20.2), 24, -0.06),
    ("detail_range", (15.5, 13.5, 1.45), (17.05, 11.86), 30, -0.04),
]
cams = []
for name, loc, tgt, lens, shift in STILLS:
    cd = bpy.data.cameras.new("CAM-" + name)
    cd.lens = lens
    cd.sensor_width = 36
    cd.shift_y = shift
    cd.clip_start, cd.clip_end = 0.05, 500
    ob = bpy.data.objects.new("CAM-" + name, cd)
    ob.location = loc
    d = Vector((tgt[0] - loc[0], tgt[1] - loc[1], 0.0))
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    col.objects.link(ob)
    cams.append(ob)

# ------------------------------------------------------------------ walkthrough: camera and aim target ride one path
WAY = [(13.17, 3.3), (13.17, 6.4), (12.3, 9.5), (13.2, 12.3), (14.0, 14.31), (16.2, 16.2), (16.75, 18.0),
       (17.3, 16.2), (19.2, 16.2), (19.95, 15.55), (20.55, 14.85), (21.6, 15.2), (21.55, 17.3), (21.55, 19.6),
       (21.6, 22.0), (22.6, 23.0), (23.2, 23.4)]
cu = bpy.data.curves.new("CRV-walkthrough", "CURVE")
cu.dimensions = "3D"
cu.resolution_u = 24
sp = cu.splines.new("BEZIER")
sp.bezier_points.add(len(WAY) - 1)
for bp, (x, y) in zip(sp.bezier_points, WAY):
    bp.co = (x, y, 1.55)
    bp.handle_left_type = bp.handle_right_type = "AUTO"
cu.use_path = True
path = bpy.data.objects.new("CRV-walkthrough", cu)
col.objects.link(path)
FRAMES = 1080            # 45 s at 24 fps
scene.frame_start, scene.frame_end = 1, FRAMES
scene.render.fps = 24
cd = bpy.data.cameras.new("CAM-walkthrough")
cd.lens = 18
cd.clip_start, cd.clip_end = 0.05, 500
walk = bpy.data.objects.new("CAM-walkthrough", cd)
aim = bpy.data.objects.new("CAM-walkthrough_aim", None)
aim.empty_display_size = 0.15
for ob in (walk, aim):
    col.objects.link(ob)
for ob, lead in ((walk, 0.0), (aim, 0.055)):
    c = ob.constraints.new("FOLLOW_PATH")
    c.target = path
    c.use_fixed_location = True
    c.use_curve_follow = False
    c.offset_factor = lead
    c.keyframe_insert("offset_factor", frame=1)
    c.offset_factor = 0.945 + lead
    c.keyframe_insert("offset_factor", frame=FRAMES)
t = walk.constraints.new("TRACK_TO")
t.target = aim
t.track_axis, t.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
# linear speed along the path
for ob in (walk, aim):
    ad = ob.animation_data
    if ad and ad.action:
        try:
            fcs = ad.action.fcurves
        except AttributeError:
            fcs = [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
        for fc in fcs:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"

# timeline markers: frames 1-1080 = walkthrough camera, frames 2001+ = one still camera per frame
for m in list(scene.timeline_markers):
    scene.timeline_markers.remove(m)
for i, ob in enumerate(cams):
    mk = scene.timeline_markers.new(ob.name, frame=2001 + i)      # stills live after the walkthrough range
    mk.camera = ob
mk = scene.timeline_markers.new("walkthrough", frame=1)
mk.camera = walk
# orthographic elevation cameras, for checking the roof and facades against the elevation sheets
for k, (name, loc, rz) in enumerate((("elev_front", (13.6, -60, 4.6), 0), ("elev_back", (13.6, 90, 4.6), 180),
                                    ("elev_right", (90, 13.0, 4.6), 90), ("elev_left", (-60, 13.0, 4.6), -90))):
    cd = bpy.data.cameras.new("CAM-" + name)
    cd.type, cd.ortho_scale, cd.clip_end = "ORTHO", 34, 300
    ob = bpy.data.objects.new("CAM-" + name, cd)
    ob.location, ob.rotation_euler = loc, (math.radians(90), 0, math.radians(rz))
    col.objects.link(ob)
    mk = scene.timeline_markers.new(ob.name, frame=2101 + k)        # elevation cameras: frames 2101-2104
    mk.camera = ob
scene.camera = bpy.data.objects["CAM-family"]
print("cameras", len(cams) + 1, "walkthrough frames", FRAMES)
