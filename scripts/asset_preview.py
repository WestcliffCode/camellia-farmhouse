"""Preview a converted or raw asset library: front and three-quarter views, each part in its own colour (raw) or
with its assigned materials (converted).
  Blender -b assets_incoming/_converted/<slot>_raw.blend -P scripts/asset_preview.py -- <out prefix> [random]"""
import bpy, math, random, sys
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
prefix, rand = args[0], len(args) > 1 and args[1] == "random"
scene = bpy.context.scene
obs = [o for o in bpy.data.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
lo = Vector((min(p[i] for p in pts) for i in range(3)))
hi = Vector((max(p[i] for p in pts) for i in range(3)))
c, size = (lo + hi) / 2, (hi - lo).length
if rand:
    random.seed(4)
    for o in obs:
        m = bpy.data.materials.new("__rnd")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*[random.uniform(0.08, 0.9) for _ in range(3)], 1)
        b.inputs["Roughness"].default_value = 0.6
        o.data.materials.clear()
        o.data.materials.append(m)
w = bpy.data.worlds.new("__w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
scene.world = w
sd = bpy.data.lights.new("__s", "SUN")
sd.energy = 3.0
so = bpy.data.objects.new("__s", sd)
scene.collection.objects.link(so)
cd = bpy.data.cameras.new("__c")
cd.lens = 50
cam = bpy.data.objects.new("__c", cd)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.device = "GPU"
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = "METAL"
    pr.get_devices()
    for d in pr.devices:
        d.use = d.type == "METAL"
except Exception as e:
    print(e)
scene.render.resolution_x, scene.render.resolution_y = 900, 900
scene.render.image_settings.file_format = "PNG"
# the model's front is unknown at this stage: look from four sides and one three-quarter view from above
for name, d in (("xneg", (-1, 0, 0.12)), ("xpos", (1, 0, 0.12)), ("yneg", (0, -1, 0.12)), ("ypos", (0, 1, 0.12)), ("top34", (-0.7, -0.7, 0.75))):
    v = Vector(d).normalized()
    cam.location = c + v * size * 1.9
    cam.rotation_euler = (-v).to_track_quat("-Z", "Y").to_euler()
    so.rotation_euler = (-(v + Vector((0.3, 0.2, 0.6)))).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = f"{prefix}_{name}.png"
    bpy.ops.render.render(write_still=True)
print("PREVIEWS", prefix)
