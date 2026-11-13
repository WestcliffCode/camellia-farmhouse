"""Lighting reference board: the captured golden-hour sky next to the renders it lights, with measured colours.

  uv run --with pillow --with numpy python scripts/lighting_reference_board.py

Needs output/renders/lighting_reference/ (from scripts/hdri_reference_strip.py) and output/renders/final/.
Writes output/renders/lighting_reference_board.png and output/lighting_reference.md.
All colours on the board are display-referred (after the same AgX view transform and exposure), so the reference
swatches and the render measurements are like for like.
"""
import colorsys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = "/Users/westcliff/Dev/3d-architecture/camellia-luxury-farmhouse"
REF = os.path.join(ROOT, "output/renders/lighting_reference")
FIN = os.path.join(ROOT, "output/renders/final")
VIEWS = ["ext_back", "game_room", "kitchen", "foyer", "primary_suite", "family"]
W = 2400
PAD = 24


def font(sz, bold=False):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz, index=1 if bold and p.endswith(".ttc") else 0)
    return ImageFont.load_default()


def hue(rgb):
    return colorsys.rgb_to_hsv(*[c / 255 for c in rgb])[0] * 360


def rb(rgb):
    return rgb[0] / max(rgb[2], 1e-6)


def measure(path):
    """Sunlit patches = the brightest unclipped warm pixels; shade = the lower-middle of the luminance range."""
    a = np.asarray(Image.open(path).convert("RGB"), np.float32)
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    ok = a.max(-1) < 250
    lo, hi = np.percentile(lum[ok], [88, 98])
    sun = a[ok & (lum >= lo) & (lum <= hi) & (a[..., 0] > a[..., 2] * 1.08)]
    slo, shi = np.percentile(lum, [15, 40])
    shade = a[(lum >= slo) & (lum <= shi)]
    return sun.mean(0), shade.mean(0), float(len(sun)) / lum.size


stats = json.load(open(os.path.join(REF, "sky_stats.json")))
ref = {k: np.asarray(Image.open(os.path.join(REF, f"swatch_{k}.png")).convert("RGB"), np.float32).reshape(-1, 3).mean(0)
       for k in ("sun_disc", "glow_near_sun", "sky_opposite", "zenith")}
rows = [(v, *measure(os.path.join(FIN, v + ".png"))) for v in VIEWS]

strip = Image.open(os.path.join(REF, "sky_strip.png")).convert("RGB")
sh = int(strip.height * (W - 2 * PAD) / strip.width)
tw = (W - 4 * PAD) // 3
th = tw * 9 // 16
H = 110 + sh + 60 + 2 * (th + 46) + 40 + 230
board = Image.new("RGB", (W, H), (18, 18, 20))
d = ImageDraw.Draw(board)
d.text((PAD, 20), "Camellia farmhouse: golden-hour lighting against its reference sky", font=font(40, True), fill=(240, 236, 228))
d.text((PAD, 72), f"Reference: Poly Haven HDRI {stats['hdri']} (a photographed clear sunset, sun {stats['sun_elevation_deg']:.1f} degrees above the "
       f"horizon), shown with the renders' own view transform ({stats['view_transform']}, exposure {stats['exposure']:+.1f}) and world strength "
       f"{stats['world_strength']:.2f}. Sun centred.", font=font(22), fill=(190, 186, 178))
y = 110
board.paste(strip.resize((W - 2 * PAD, sh), Image.LANCZOS), (PAD, y))
y += sh + 14
d.text((PAD, y), "Renders lit by that sky and a sun lamp aligned with its sun and coloured from its sun disc:", font=font(24, True), fill=(240, 236, 228))
y += 46
for i, (v, sun, shade, frac) in enumerate(rows):
    x = PAD + (i % 3) * (tw + PAD)
    yy = y + (i // 3) * (th + 46)
    board.paste(Image.open(os.path.join(FIN, v + ".png")).convert("RGB").resize((tw, th), Image.LANCZOS), (x, yy))
    d.text((x, yy + th + 8), v.replace("_", " "), font=font(22), fill=(200, 196, 188))
y += 2 * (th + 46) + 10

# measured colours
d.text((PAD, y), "Measured colours (display-referred): reference sky on the left, sunlit patches and shade in each render on the right",
       font=font(24, True), fill=(240, 236, 228))
y += 44
SW = 120


def swatch(x, label, rgb, sub):
    d.rectangle([x, y, x + SW, y + SW], fill=tuple(int(round(c)) for c in rgb))
    d.text((x, y + SW + 6), label, font=font(18, True), fill=(230, 226, 218))
    d.text((x, y + SW + 30), sub, font=font(17), fill=(170, 166, 158))


x = PAD
for key, label in (("sun_disc", "sun disc"), ("glow_near_sun", "glow by sun"), ("sky_opposite", "sky opposite"), ("zenith", "zenith")):
    swatch(x, label, ref[key], f"hue {hue(ref[key]):.0f}  R/B {rb(ref[key]):.2f}")
    x += SW + 60
x += 40
d.line([x - 30, y, x - 30, y + SW + 50], fill=(90, 88, 84), width=2)
for v, sun, shade, frac in rows:
    swatch(x, v.replace("_", " ")[:13], sun, f"sun: hue {hue(sun):.0f} R/B {rb(sun):.2f}")
    d.rectangle([x + SW // 2, y + SW // 2, x + SW, y + SW], fill=tuple(int(round(c)) for c in shade))
    d.text((x, y + SW + 52), f"shade: R/B {rb(shade):.2f}", font=font(17), fill=(170, 166, 158))
    x += SW + 110
board.save(os.path.join(ROOT, "output/renders/lighting_reference_board.png"))

glow_h = hue(ref["glow_near_sun"])
disc_h = hue(ref["sun_disc"])
lines = ["# Lighting reference comparison", "",
         f"Reference: Poly Haven HDRI `{stats['hdri']}`, a photographed clear sunset with the sun {stats['sun_elevation_deg']:.1f} degrees above the horizon. "
         "It is the scene's sky, and the sun lamp takes both its direction and its colour from the sun in that photograph.", "",
         "Board: `output/renders/lighting_reference_board.png` (sky panorama and renders under the same view transform and exposure).", "",
         "| Reference patch | display RGB | hue | R/B |", "|---|---|---|---|"]
for key, label in (("sun_disc", "sun disc (lamp colour)"), ("glow_near_sun", "sky glow within 14 degrees of the sun"),
                   ("sky_opposite", "sky opposite the sun"), ("zenith", "zenith")):
    c = ref[key]
    lines.append(f"| {label} | {c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f} | {hue(c):.0f} | {rb(c):.2f} |")
lines += ["", "| Render | sunlit patches RGB | hue | R/B | hue vs sun disc | hue vs sky glow | shade RGB | shade hue |", "|---|---|---|---|---|---|---|---|"]
n_ok = 0
for v, sun, shade, frac in rows:
    dh_d = (hue(sun) - disc_h + 180) % 360 - 180
    dh_g = (hue(sun) - glow_h + 180) % 360 - 180
    n_ok += min(disc_h, glow_h) - 12 <= hue(sun) <= max(disc_h, glow_h) + 12
    lines.append(f"| {v} | {sun[0]:.0f}, {sun[1]:.0f}, {sun[2]:.0f} | {hue(sun):.0f} | {rb(sun):.2f} | {dh_d:+.0f} | {dh_g:+.0f} | "
                 f"{shade[0]:.0f}, {shade[1]:.0f}, {shade[2]:.0f} | {hue(shade):.0f} |")
lines += ["", f"Criterion: the sunlit patches in a render should sit in the hue range the photograph spans between its sun disc ({disc_h:.0f}) and the sky glow "
          f"around it ({glow_h:.0f}), within 12 degrees. Views meeting it: {n_ok} of {len(rows)}.", "",
          "What the comparison does not show: the shade in these views is warm as well (hues in the table), not the cool blue of the sky opposite the sun. "
          "Indoors the shade is filled by 2700-3000 K lamps and light bounced off oak floors; the cool sky colour appears only in the sky seen through "
          "street-side windows and in the exterior views. The sunlit patches are less saturated than the sun disc swatch because the view transform "
          "desaturates bright values and the patches fall on white walls and pale floors."]
open(os.path.join(ROOT, "output/lighting_reference.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
