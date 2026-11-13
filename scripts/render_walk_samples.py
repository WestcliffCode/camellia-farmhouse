"""Render sample frames of the walkthrough: Blender -b file -P scripts/render_walk_samples.py -- f1,f2,... pct samples outdir"""
import sys, os, bpy
a = sys.argv[sys.argv.index("--") + 1:]
frames = [int(x) for x in a[0].split(",")]
scene = bpy.context.scene
scene.render.resolution_percentage = int(a[1]); scene.cycles.samples = int(a[2]); scene.cycles.device = "GPU"
out = os.path.abspath(a[3]); os.makedirs(out, exist_ok=True)
for f in frames:
    scene.frame_set(f)
    scene.camera = bpy.data.objects["CAM-walkthrough"]
    scene.render.filepath = os.path.join(out, f"walk_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", f)
