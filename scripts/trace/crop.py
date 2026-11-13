"""Crop a region of an image, optionally upscale: crop.py src out x0 y0 x1 y1 [scale]"""
import sys, cv2
src, out, x0, y0, x1, y1 = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
s = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
img = cv2.imread(src)
c = img[y0:y1, x0:x1]
if s != 1.0:
    c = cv2.resize(c, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)
cv2.imwrite(out, c)
print(c.shape)
