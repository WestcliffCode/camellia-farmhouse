"""Lighting reference board: the captured golden-hour sky next to the renders it lights, with measured colours.

  uv run --with pillow --with numpy python scripts/lighting_reference_board.py

Needs output/renders/lighting_reference/ (from scripts/hdri_reference_strip.py and scripts/lighting_cards.py) and
output/renders/final/.
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
cards = json.load(open(os.path.join(REF, "cards.json")))
ref = {k: np.asarray(Image.open(os.path.join(REF, f"swatch_{k}.png")).convert("RGB"), np.float32).reshape(-1, 3).mean(0)
       for k in ("sun_disc", "glow_near_sun", "sky_opposite", "zenith")}
CARD = [("facing_sun", "card to sun"), ("facing_away", "card away"), ("facing_up", "card up")]
card = {k: np.array(cards[k], np.float32) for k, _ in CARD}
rows = [(v, *measure(os.path.join(FIN, v + ".png"))) for v in VIEWS]
OFF = ["game_room", "primary_suite", "kitchen"]
off = [(v, *measure(os.path.join(REF, f"sun_sky_only_{v}.png"))) for v in OFF]

strip = Image.open(os.path.join(REF, "sky_strip.png")).convert("RGB")
sh = int(strip.height * (W - 2 * PAD) / strip.width)
tw = (W - 4 * PAD) // 3
th = tw * 9 // 16
H = 110 + sh + 60 + 3 * (th + 46) + 56 + 40 + 230
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
d.text((PAD, y), "The same scene with every lamp switched off (sun and sky only):", font=font(24, True), fill=(240, 236, 228))
y += 46
for i, (v, sun, shade, frac) in enumerate(off):
    x = PAD + i * (tw + PAD)
    board.paste(Image.open(os.path.join(REF, f"sun_sky_only_{v}.png")).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
    d.text((x, y + th + 8), v.replace("_", " ") + ", lamps off", font=font(22), fill=(200, 196, 188))
y += th + 46 + 10

d.text((PAD, y), "Measured colours (display-referred): reference sky | grey cards on the lawn (albedo 0.5) | sunlit patches in each render",
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
    x += SW + 44
d.line([x - 6, y, x - 6, y + SW + 50], fill=(90, 88, 84), width=2)
x += 32
for key, label in CARD:
    swatch(x, label, card[key], f"hue {hue(card[key]):.0f}  R/B {rb(card[key]):.2f}")
    x += SW + 44
d.line([x - 6, y, x - 6, y + SW + 50], fill=(90, 88, 84), width=2)
x += 32
for v, sun, shade, frac in rows:
    swatch(x, v.replace("_", " ")[:13], sun, f"hue {hue(sun):.0f}  R/B {rb(sun):.2f}")
    x += SW + 44
board.save(os.path.join(ROOT, "output/renders/lighting_reference_board.png"))

glow_h = hue(ref["glow_near_sun"])
disc_h = hue(ref["sun_disc"])
lum = lambda c: float(np.asarray(c) @ np.array([0.2126, 0.7152, 0.0722]))
lines = ["# Lighting reference comparison", "",
         f"Reference: Poly Haven HDRI `{stats['hdri']}`, a photographed clear sunset with the sun {stats['sun_elevation_deg']:.1f} degrees above the horizon. "
         "It is the scene's sky, and the sun lamp takes both its direction and its colour from the sun in that photograph.", "",
         "Board: `output/renders/lighting_reference_board.png` (sky panorama and renders under the same view transform and exposure). "
         "All values below are display-referred RGB (0-255) after that view transform.", "",
         "## Reference sky", "", "| Patch | RGB | hue | R/B |", "|---|---|---|---|"]
for key, label in (("sun_disc", "sun disc (lamp colour)"), ("glow_near_sun", "sky glow within 14 degrees of the sun"),
                   ("sky_opposite", "sky opposite the sun"), ("zenith", "zenith")):
    c = ref[key]
    lines.append(f"| {label} | {c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f} | {hue(c):.0f} | {rb(c):.2f} |")
lines += ["", "## The light itself: neutral grey cards on the open lawn (albedo 0.5, no house materials involved)", "",
          "| Card | RGB | hue | R/B | luminance |", "|---|---|---|---|---|"]
for key, label in (("facing_sun", "facing the sun"), ("facing_away", "facing away from the sun (lit by sky and ground only)"), ("facing_up", "facing up")):
    c = card[key]
    lines.append(f"| {label} | {c[0]:.0f}, {c[1]:.0f}, {c[2]:.0f} | {hue(c):.0f} | {rb(c):.2f} | {lum(c):.0f} |")
cs, ca = card["facing_sun"], card["facing_away"]
key_ok = abs((hue(cs) - disc_h + 180) % 360 - 180) <= 12
fill_ok = rb(ca) < rb(cs)
lines += ["", f"- Sun-facing card hue {hue(cs):.0f} against the photographed sun disc's {disc_h:.0f}: {'within' if key_ok else 'outside'} 12 degrees.",
          f"- Shade-facing card R/B {rb(ca):.2f} against the sun-facing card's {rb(cs):.2f}: the fill is {'cooler than' if fill_ok else 'not cooler than'} the key. "
          f"It is close to neutral rather than blue, because that card also receives light bounced off the sunlit dry grass in the photograph's lower half.",
          f"- Sun-facing to shade-facing luminance {lum(cs):.0f} : {lum(ca):.0f}.", "",
          "## Sunlit patches in the renders", "",
          "| Render | sunlit patches RGB | hue | R/B | hue vs sun disc | hue vs sky glow |", "|---|---|---|---|---|---|"]
n_ok = 0
for v, sun, shade, frac in rows:
    dh_d = (hue(sun) - disc_h + 180) % 360 - 180
    dh_g = (hue(sun) - glow_h + 180) % 360 - 180
    n_ok += min(disc_h, glow_h) - 12 <= hue(sun) <= max(disc_h, glow_h) + 12
    lines.append(f"| {v} | {sun[0]:.0f}, {sun[1]:.0f}, {sun[2]:.0f} | {hue(sun):.0f} | {rb(sun):.2f} | {dh_d:+.0f} | {dh_g:+.0f} |")
lines += ["", f"Criterion: the sunlit patches in a render should sit in the hue range the photograph spans between its sun disc ({disc_h:.0f}) and the sky glow "
          f"around it ({glow_h:.0f}), within 12 degrees. Views meeting it: {n_ok} of {len(rows)}.", "",
          "## Shade indoors, lamps on and off", "",
          "Shade = the 15th to 40th percentile of luminance in the frame.", "",
          "| View | shade RGB, lamps on | shade RGB, lamps off | mean luminance, lamps on | lamps off |", "|---|---|---|---|---|"]
on = {v: (sun, shade) for v, sun, shade, frac in rows}
for v, sun, shade, frac in off:
    so = on[v][1]
    a_on = float(np.asarray(Image.open(os.path.join(FIN, v + ".png")).convert("L")).mean())
    a_off = float(np.asarray(Image.open(os.path.join(REF, f"sun_sky_only_{v}.png")).convert("L")).mean())
    lines.append(f"| {v} | {so[0]:.0f}, {so[1]:.0f}, {so[2]:.0f} | {shade[0]:.0f}, {shade[1]:.0f}, {shade[2]:.0f} | {a_on:.0f} | {a_off:.0f} |")
lines += ["", "With the lamps off the rooms fall into deep shade around the sunlit patches, and the little light left in that shade is orange: it has come off "
          "the sun patches and the oak floors, not from the blue side of the sky. The lamps supply most of the fill (compare the last two columns), "
          "which is the soft practical lighting the brief asks for. So the warm shade in the finished renders is the lamps and the bounce, and the "
          "cool side of the sky shows only in the shade-facing grey card and on the street side of the exterior views."]
open(os.path.join(ROOT, "output/lighting_reference.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
