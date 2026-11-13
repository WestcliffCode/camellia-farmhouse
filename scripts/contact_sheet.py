"""contact_sheet.py out.png cols tile_w img1 img2 ... : labelled grid of renders for quick review."""
import sys, os, cv2, numpy as np
out, cols, tw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
tiles = []
for p in sys.argv[4:]:
    im = cv2.imread(p)
    if im is None:
        continue
    th = int(im.shape[0] * tw / im.shape[1])
    im = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
    cv2.putText(im, os.path.basename(p)[:-4], (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3)
    cv2.putText(im, os.path.basename(p)[:-4], (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    tiles.append(im)
h = max(t.shape[0] for t in tiles)
rows = []
for i in range(0, len(tiles), cols):
    row = [np.pad(t, ((0, h - t.shape[0]), (0, 0), (0, 0))) for t in tiles[i:i + cols]]
    while len(row) < cols:
        row.append(np.zeros((h, tw, 3), np.uint8))
    rows.append(np.hstack(row))
cv2.imwrite(out, np.vstack(rows))
