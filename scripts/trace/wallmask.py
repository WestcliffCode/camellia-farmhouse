"""Build a cleaned wall-poche mask from the plan image.

Walls are gray-filled bands with dark outlines, >= ~7 px thick. Text is pure
black and thinner; fixtures and door swings are 1-2 px lines.
usage: wallmask.py src outdir [open_px]
"""
import sys
import cv2
import numpy as np

src, out = sys.argv[1], sys.argv[2]
kpx = int(sys.argv[3]) if len(sys.argv) > 3 else 6
img = cv2.imread(src)
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ink = (g < 222).astype(np.uint8) * 255
k = cv2.getStructuringElement(cv2.MORPH_RECT, (kpx, kpx))
op = cv2.morphologyEx(ink, cv2.MORPH_OPEN, k)
n, lab, stats, _ = cv2.connectedComponentsWithStats(op, connectivity=8)
keep = np.zeros_like(op)
for i in range(1, n):
    x, y, w, h, a = stats[i]
    sel = lab[y:y + h, x:x + w] == i
    vals = g[y:y + h, x:x + w][sel]
    mean = float(vals.mean())
    frac_black = float((vals < 70).mean())
    # walls: mostly mid-gray. text/solid symbols: mostly black.
    if frac_black > 0.55 or a < 60:
        continue
    keep[y:y + h, x:x + w][sel] = 255
cv2.imwrite(out + "/wallmask.png", keep)
vis = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
vis = (vis * 0.35 + 160).clip(0, 255).astype(np.uint8)
vis[keep > 0] = (0, 0, 220)
cv2.imwrite(out + "/wallmask_overlay.png", cv2.resize(vis, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA))
print("components", n - 1, "kept px", int(keep.sum() / 255))
