"""Crop with a labelled pixel grid: gridcrop.py src out x0 y0 x1 y1 scale [step]"""
import sys, cv2
src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
s = float(sys.argv[7]); step = int(sys.argv[8]) if len(sys.argv) > 8 else 50
img = cv2.imread(src)
c = cv2.resize(img[y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
for gx in range((x0 // step + 1) * step, x1, step):
    X = int((gx - x0) * s)
    cv2.line(c, (X, 0), (X, c.shape[0]), (255, 170, 60), 1)
    cv2.putText(c, str(gx), (X + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 60, 0), 1)
for gy in range((y0 // step + 1) * step, y1, step):
    Y = int((gy - y0) * s)
    cv2.line(c, (0, Y), (c.shape[1], Y), (255, 170, 60), 1)
    cv2.putText(c, str(gy), (2, Y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 60, 0), 1)
cv2.imwrite(out, c)
print(c.shape)
