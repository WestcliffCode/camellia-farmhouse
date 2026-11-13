"""Render the walkthrough animation at review quality:
  Blender -b project-files/camellia-farmhouse.blend -P scripts/render_walkthrough.py -- <width> <samples> <frame_step> <out_dir>
Encode afterwards with ffmpeg (see HANDOFF.md)."""
import sys, os, bpy
a = sys.argv[sys.argv.index("--") + 1:]
w, spp, step, out = int(a[0]), int(a[1]), int(a[2]), os.path.abspath(a[3])
os.makedirs(out, exist_ok=True)
s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = w, int(w * 9 / 16), 100
s.cycles.samples, s.cycles.device = spp, "GPU"
s.render.use_persistent_data = True      # keep geometry and textures loaded between frames
s.frame_start, s.frame_end, s.frame_step = 1, 1080, step
s.render.image_settings.file_format = "JPEG"
s.render.image_settings.quality = 90
s.render.filepath = os.path.join(out, "walk_")
bpy.ops.render.render(animation=True)
print("WALKTHROUGH DONE")
