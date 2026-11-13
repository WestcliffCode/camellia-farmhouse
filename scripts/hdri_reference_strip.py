"""Reference half of the lighting board: the captured sky, shown exactly as the renders see it.

Run in background Blender on the saved file:
  Blender -b project-files/camellia-farmhouse.blend -P scripts/hdri_reference_strip.py
Writes output/renders/lighting_reference/sky_strip.png (the full panorama above the horizon, sun centred, with the
world strength and the scene's view transform and exposure applied) and sky_stats.json (linear colours measured in it).
"""
import bpy, json, math, os
import numpy as np

ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
OUT = os.path.join(ROOT, "output/renders/lighting_reference")
os.makedirs(OUT, exist_ok=True)
scene = bpy.context.scene
world = scene.world
env = next(n for n in world.node_tree.nodes if n.type == "TEX_ENVIRONMENT")
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
strength = bg.inputs["Strength"].default_value
hdr = env.image
w, h = hdr.size
px = np.empty(w * h * 4, np.float32)
hdr.pixels.foreach_get(px)
im = px.reshape(h, w, 4)[..., :3]
lum = im @ np.array([0.2126, 0.7152, 0.0722], np.float32)
ys, xs = np.nonzero(lum >= np.partition(lum.ravel(), -400)[-400])
u0, v0 = float(xs.mean()) / w, float(ys.mean()) / h
disc = im[ys, xs].mean(0)

# roll the panorama so the sun is centred; keep the band from just below the horizon to 50 degrees up
im = np.roll(im, int(round((0.5 - u0) * w)), axis=1)
y0, y1 = int(h * (0.5 - 6 / 180)), int(h * (0.5 + 50 / 180))
band = im[y0:y1] * strength
bh, bw = band.shape[:2]
tmp = bpy.data.images.new("__sky_strip", bw, bh, alpha=False, float_buffer=True)
rgba = np.ones((bh, bw, 4), np.float32)
rgba[..., :3] = band
tmp.pixels.foreach_set(rgba.ravel())
scene.render.image_settings.file_format = "PNG"
tmp.save_render(os.path.join(OUT, "sky_strip.png"), scene=scene)      # applies AgX and the scene exposure


def region(du_deg, dv0, dv1, centre=0.5):
    """Mean linear colour of a patch of the rolled panorama: du_deg either side of `centre`, elevations dv0..dv1."""
    x0, x1 = int(w * (centre - du_deg / 360)), int(w * (centre + du_deg / 360))
    r0, r1 = int(h * (0.5 + dv0 / 180)), int(h * (0.5 + dv1 / 180))
    cols = np.arange(x0, x1) % w
    return [float(c) for c in im[r0:r1][:, cols].reshape(-1, 3).mean(0)]


stats = {
    "hdri": os.path.basename(bpy.path.abspath(hdr.filepath)),
    "world_strength": strength,
    "exposure": scene.view_settings.exposure,
    "view_transform": scene.view_settings.view_transform,
    "sun_elevation_deg": (v0 - 0.5) * 180,
    "sun_disc": [float(c) for c in disc / disc.max()],
    "glow_near_sun": region(14, 0, 10),
    "sky_opposite": region(25, 10, 50, centre=0.0),
    "zenith": region(180, 60, 88),
    "lamp_color": list(bpy.data.objects["LGT-sun"].data.color),
    "lamp_energy": bpy.data.objects["LGT-sun"].data.energy,
}
json.dump(stats, open(os.path.join(OUT, "sky_stats.json"), "w"), indent=1)

# swatches of those measured colours through the same view transform (16 px each)
for key in ("sun_disc", "glow_near_sun", "sky_opposite", "zenith"):
    c = np.array(stats[key], np.float32)
    # sky patches at the strength the renders use; the sun disc (clipped in the capture) at a fixed mid luminance to show its hue
    c = c * (0.6 / float(c @ np.array([0.2126, 0.7152, 0.0722], np.float32)) if key == "sun_disc" else strength)
    sw = bpy.data.images.new("__sw", 16, 16, alpha=False, float_buffer=True)
    sw.pixels.foreach_set(np.tile(np.array([*c, 1.0], np.float32), 256))
    sw.save_render(os.path.join(OUT, f"swatch_{key}.png"), scene=scene)
    bpy.data.images.remove(sw)
print("sky strip", bw, bh, "stats", json.dumps(stats)[:300])
