"""Explore the plan image: gray-level histogram and a first wall-poche mask."""
import sys
import cv2
import numpy as np

src, out = sys.argv[1], sys.argv[2]
img = cv2.imread(src, cv2.IMREAD_COLOR)
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print("shape", img.shape)
hist = np.bincount(g.ravel(), minlength=256)
for lo in range(0, 256, 16):
    print(f"{lo:3d}-{lo+15:3d}: {hist[lo:lo+16].sum():9d}")
# candidate poche: mid gray
for lo, hi in ((90, 200), (110, 190), (120, 180)):
    m = ((g >= lo) & (g <= hi)).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    mo = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
    print(lo, hi, "raw", int(m.sum() / 255), "opened", int(mo.sum() / 255))
m = ((g >= 110) & (g <= 190)).astype(np.uint8) * 255
k = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
mo = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
cv2.imwrite(out + "/mask_open.png", mo)
vis = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
vis = (vis * 0.35 + 160).clip(0, 255).astype(np.uint8)
vis[mo > 0] = (0, 0, 220)
cv2.imwrite(out + "/mask_overlay.png", cv2.resize(vis, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA))
