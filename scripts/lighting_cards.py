"""Measure the light itself, independent of the house's materials (background Blender, nothing is saved to the .blend):

  Blender -b project-files/camellia-farmhouse.blend -P scripts/lighting_cards.py

1. Three neutral grey cards (albedo 0.5) on the open lawn behind the house: one facing the sun, one facing away from
   it, one facing up. Each is rendered square-on through the scene's view transform -> card_*.png and cards.json.
   A golden-hour sky gives a warm sun-facing card and a cooler card on the side lit only by the sky.
2. Two interiors rendered with every lamp and glowing shade switched off (sun and sky only), to show what the
   daylight alone does indoors -> sun_sky_only_<view>.png.
"""
import bpy, json, math, os
import numpy as np
from mathutils import Vector

ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
OUT = os.path.join(ROOT, "output/renders/lighting_reference")
os.makedirs(OUT, exist_ok=True)
scene = bpy.context.scene
for m in list(scene.timeline_markers):
    scene.timeline_markers.remove(m)
scene.frame_set(2001)
scene.render.image_settings.file_format = "PNG"
scene.cycles.samples = 96
sun = bpy.data.objects["LGT-sun"]
to_sun = (sun.matrix_world.to_quaternion() @ Vector((0, 0, 1))).normalized()
flat = Vector((to_sun.x, to_sun.y, 0)).normalized()

# a spot on the lawn with a clear line to the sun and nothing near
dg = bpy.context.evaluated_depsgraph_get()
spot = None
for x, y in ((-14, 36), (0, 40), (13, 44), (30, 40), (40, 34), (-20, 28)):
    p = Vector((x, y, 1.2))
    if not scene.ray_cast(dg, p, to_sun, distance=500)[0] and not scene.ray_cast(dg, p, -flat, distance=6)[0]:
        spot = p
        break
assert spot is not None, "no open spot found"

grey = bpy.data.materials.new("__card_grey")
grey.use_nodes = True
b = next(n for n in grey.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
b.inputs["Roughness"].default_value = 1.0
for nm in ("Specular IOR Level", "Specular"):
    if nm in b.inputs:
        b.inputs[nm].default_value = 0.0

cards = {"facing_sun": flat, "facing_away": -flat, "facing_up": Vector((0, 0, 1))}
res = {"spot": list(spot)}
cam_d = bpy.data.cameras.new("__card_cam")
cam_d.type = "ORTHO"
cam_d.ortho_scale = 0.5
cam = bpy.data.objects.new("__card_cam", cam_d)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.resolution_x = scene.render.resolution_y = 64
scene.render.resolution_percentage = 100
made = []
for i, (key, n) in enumerate(cards.items()):
    me = bpy.data.meshes.new("__card")
    s = 0.5
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("__card_" + key, me)
    ob.data.materials.append(grey)
    ob.location = spot + Vector((0, 0, 0.0)) + flat.cross(Vector((0, 0, 1))) * (i - 1) * 4.0      # 4 m apart, side by side
    ob.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    scene.collection.objects.link(ob)
    made.append((key, ob, n))
for key, ob, n in made:
    cam.location = ob.location + n * 1.5
    cam.rotation_euler = (-n).to_track_quat("-Z", "Y").to_euler()
    path = os.path.join(OUT, f"card_{key}.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    px = np.array(img.pixels[:], np.float32).reshape(-1, 4)[:, :3]
    res[key] = [float(v) * 255 for v in px.mean(0)]
    bpy.data.images.remove(img)
json.dump(res, open(os.path.join(OUT, "cards.json"), "w"), indent=1)
print("CARDS", json.dumps(res))
for key, ob, n in made:
    bpy.data.objects.remove(ob)

# interiors with sun and sky only
for ob in bpy.data.objects:
    if ob.type == "LIGHT" and ob.name != "LGT-sun":
        ob.hide_render = True
for m in bpy.data.materials:
    if m.node_tree:
        for nd in m.node_tree.nodes:
            if nd.type == "BSDF_PRINCIPLED" and "Emission Strength" in nd.inputs:
                nd.inputs["Emission Strength"].default_value = 0.0
scene.render.resolution_x, scene.render.resolution_y = 960, 540
for view in ("game_room", "primary_suite", "kitchen"):
    scene.camera = bpy.data.objects["CAM-" + view]
    scene.render.filepath = os.path.join(OUT, f"sun_sky_only_{view}.png")
    bpy.ops.render.render(write_still=True)
print("done")
