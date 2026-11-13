"""Score the final renders against a stated bar and write output/render_qc.md.
  uv run --with opencv-python-headless --with numpy python scripts/render_qc.py output/renders/final"""
import sys, os, glob, cv2, numpy as np
d = sys.argv[1]
BAR = {"interior": dict(mean=(85, 205), clipped=8.0, crushed=6.0, warm=1.10),
       "exterior": dict(mean=(55, 190), clipped=4.0, crushed=12.0, warm=0.95)}
rows, fails = [], 0
for f in sorted(glob.glob(os.path.join(d, "*.png"))):
    n = os.path.basename(f)[:-4]
    if n.startswith("elev_"):
        continue
    kind = "exterior" if n.startswith("ext_") or n == "outdoor_living" else "interior"
    im = cv2.imread(f).astype(np.float32)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mean = float(lum.mean())
    clipped = float((lum > 250).mean() * 100)
    crushed = float((lum < 6).mean() * 100)
    warm = float(r.mean() / max(b.mean(), 1e-3))
    bar = BAR[kind]
    ok = bar["mean"][0] <= mean <= bar["mean"][1] and clipped <= bar["clipped"] and crushed <= bar["crushed"] and warm >= bar["warm"]
    fails += not ok
    rows.append(f"| {n} | {kind} | {mean:.0f} | {clipped:.1f} | {crushed:.1f} | {warm:.2f} | {'pass' if ok else 'FAIL'} |")
out = ["# Render quality check", "",
       "Bar (8-bit display values). Interiors: mean luminance 85-205, clipped (>250) at most 8%, crushed (<6) at most 6%, "
       "red/blue ratio at least 1.10 (warm light). Exteriors: mean 55-190, clipped at most 4%, crushed at most 12%, red/blue at least 0.95.", "",
       "| View | Kind | Mean luminance | Clipped % | Crushed % | R/B | Result |", "| --- | --- | --- | --- | --- | --- | --- |"] + rows
out += ["", f"{len(rows) - fails} of {len(rows)} views pass."]
open("output/render_qc.md", "w").write("\n".join(out) + "\n")
print(f"{len(rows) - fails} of {len(rows)} pass")
print("\n".join(r for r in rows if "FAIL" in r))
