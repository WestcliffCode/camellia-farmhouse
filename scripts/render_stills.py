"""Render still cameras in a background Blender:
  Blender -b project-files/camellia-farmhouse.blend -P scripts/render_stills.py -- --cams family,kitchen --pct 50 --samples 96 --out output/renders/preview
--cams all renders every CAM-* still camera (not the walkthrough).
--preset sunrise swaps in the second lighting preset (sun in front of the house) for this session only."""
import sys
import time
import os
import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = {"cams": "family", "pct": "50", "samples": "96", "out": "output/renders/preview", "exposure": None, "preset": "sunset"}
for i in range(0, len(argv), 2):
    opt[argv[i].lstrip("-")] = argv[i + 1]
scene = bpy.context.scene
scene.render.resolution_percentage = int(opt["pct"])
scene.cycles.samples = int(opt["samples"])
scene.cycles.device = "GPU"
if opt["exposure"] is not None:
    scene.view_settings.exposure = float(opt["exposure"])
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "METAL"
except Exception as e:
    print("device setup:", e)
if opt["preset"] == "sunrise":
    bpy.data.objects["LGT-sun"].hide_render = True
    am = bpy.data.objects["LGT-sun_sunrise"]
    am.hide_render = False
    am.hide_viewport = False
    scene.world = bpy.data.worlds["WORLD-camellia_sunrise"]
    print("preset: sunrise")
names = [o.name[4:] for o in bpy.data.objects if o.type == "CAMERA" and o.name != "CAM-walkthrough"] if opt["cams"] == "all" else opt["cams"].split(",")
out = os.path.abspath(opt["out"])
os.makedirs(out, exist_ok=True)
for n in names:
    cam = bpy.data.objects.get("CAM-" + n)
    if cam is None:
        print("no camera", n)
        continue
    for m in scene.timeline_markers:     # markers bind cameras to frames; unbind them in this (unsaved) session
        m.camera = None
    scene.frame_set(1)
    scene.camera = cam
    scene.render.filepath = os.path.join(out, n + ".png")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED {n} in {time.time() - t:.1f}s -> {scene.render.filepath}")
