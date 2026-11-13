"""Vectorize the wall mask: snapped wall polygons + candidate openings.

usage: vectorize.py plan_image wallmask.png out_dir
Writes out_dir/trace_raw.json and annotated quadrant images.
All coordinates are plan-image pixels (x right, y down).
"""
import json
import math
import sys

import cv2
import numpy as np

plan_path, mask_path, out = sys.argv[1:4]
plan = cv2.imread(plan_path)
gray = cv2.cvtColor(plan, cv2.COLOR_BGR2GRAY)
mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
mask = (mask > 127).astype(np.uint8) * 255
H, W = mask.shape
PX_PER_FT = 22.41


# ---------------------------------------------------------------- polygons
def cluster(vals, weights, tol=2.6):
    """1-D clustering; returns function mapping value -> cluster centre."""
    order = np.argsort(vals)
    centres, cur, curw = [], [], []
    for i in order:
        v, w = vals[i], weights[i]
        if cur and v - cur[-1] > tol:
            centres.append(float(np.average(cur, weights=curw)))
            cur, curw = [], []
        cur.append(v)
        curw.append(w)
    if cur:
        centres.append(float(np.average(cur, weights=curw)))
    centres = np.array(centres)

    def snap(v):
        return float(centres[np.argmin(np.abs(centres - v))])
    return snap


contours, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
polys = []
poly_ci = []
for ci, c in enumerate(contours):
    ap = cv2.approxPolyDP(c, 2.0, True).reshape(-1, 2).astype(float)
    if len(ap) >= 3:
        polys.append(ap)
        poly_ci.append(ci)

hy, hw_, vx, vw_ = [], [], [], []
edge_kind = []
for p in polys:
    kinds = []
    n = len(p)
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        dx, dy = b - a
        L = math.hypot(dx, dy)
        ang = abs(math.degrees(math.atan2(dy, dx))) % 180
        if L >= 4 and (ang < 12 or ang > 168):
            kinds.append("H")
            hy += [a[1], b[1]]
            hw_ += [L, L]
        elif L >= 4 and abs(ang - 90) < 12:
            kinds.append("V")
            vx += [a[0], b[0]]
            vw_ += [L, L]
        else:
            kinds.append("D")
    edge_kind.append(kinds)

snap_y = cluster(np.array(hy), np.array(hw_))
snap_x = cluster(np.array(vx), np.array(vw_))

snapped = []
by_ci = {}
for p, kinds, ci in zip(polys, edge_kind, poly_ci):
    n = len(p)
    q = p.copy()
    for i in range(n):
        prev_k, next_k = kinds[(i - 1) % n], kinds[i]
        for k in (prev_k, next_k):
            if k == "H":
                q[i][1] = snap_y(p[i][1])
            elif k == "V":
                q[i][0] = snap_x(p[i][0])
    # drop duplicate / collinear points
    cleaned = []
    for i in range(n):
        a, b, c = q[(i - 1) % n], q[i], q[(i + 1) % n]
        if np.hypot(*(b - a)) < 0.5:
            continue
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cross) < 1e-6:
            continue
        cleaned.append([round(float(b[0]), 2), round(float(b[1]), 2)])
    if len(cleaned) >= 3:
        snapped.append(cleaned)
        by_ci[ci] = cleaned

wall_polys = []
for ci, outer in by_ci.items():
    if hier[0][ci][3] != -1:
        continue
    holes = [by_ci[cj] for cj in by_ci if hier[0][cj][3] == ci]
    wall_polys.append({"outer": outer, "holes": holes})


# ---------------------------------------------------------------- openings
def gaps_h(m, g, max_gap_px, corner_px, min_run=26):
    """Candidate gaps along horizontal wall bands of binary mask m."""
    kh = cv2.getStructuringElement(cv2.MORPH_RECT, (min_run, 1))
    hwalls = cv2.morphologyEx(m, cv2.MORPH_OPEN, kh)
    # A: between collinear horizontal bands
    ka = cv2.getStructuringElement(cv2.MORPH_RECT, (max_gap_px, 1))
    ca = cv2.morphologyEx(hwalls, cv2.MORPH_CLOSE, ka)
    gap_a = cv2.bitwise_and(ca, cv2.bitwise_not(m))
    # B: band end facing any wall within corner_px
    kb = cv2.getStructuringElement(cv2.MORPH_RECT, (corner_px, 1))
    cb = cv2.morphologyEx(m, cv2.MORPH_CLOSE, kb)
    near = cv2.dilate(hwalls, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * corner_px + 1, 1)))
    gap_b = cv2.bitwise_and(cv2.bitwise_and(cb, near), cv2.bitwise_not(m))
    gap = cv2.bitwise_or(gap_a, gap_b)
    # only keep rows belonging to bands (remove 1-2 px slivers)
    gap = cv2.morphologyEx(gap, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(gap, connectivity=8)
    res = []
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if w < 14 or h < 5 or h > 30 or a < 0.6 * w * h:
            continue
        if x <= 1 or y <= 1 or x + w >= m.shape[1] - 1 or y + h >= m.shape[0] - 1:
            continue  # closing artefact at the image border
        band = g[y:y + h, x + 2:x + w - 2]
        ink = float((band < 150).mean()) if band.size else 0.0
        res.append((x, y, x + w, y + h, ink))
    return res


MAXGAP = int(18.5 * PX_PER_FT)
CORNER = int(3.6 * PX_PER_FT)
openings = []


def add(poly, axis, ink):
    p = np.array(poly, float)
    L = max(np.hypot(*(p[1] - p[0])), np.hypot(*(p[2] - p[1])))
    T = min(np.hypot(*(p[1] - p[0])), np.hypot(*(p[2] - p[1])))
    openings.append({
        "id": len(openings),
        "axis": axis,
        "poly": [[round(float(x), 1), round(float(y), 1)] for x, y in p],
        "c": [round(float(p[:, 0].mean()), 1), round(float(p[:, 1].mean()), 1)],
        "len_ft": round(L / PX_PER_FT, 2),
        "thick_px": round(T, 1),
        "ink": round(ink, 2),
    })


for (x0, y0, x1, y1, ink) in gaps_h(mask, gray, MAXGAP, CORNER):
    add([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "H", ink)
mt, gt = mask.T.copy(), gray.T.copy()
for (y0, x0, y1, x1, ink) in gaps_h(mt, gt, MAXGAP, CORNER):
    add([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "V", ink)

# diagonals: rotate by 45 deg and repeat both passes
diag = math.hypot(W, H)
S = int(diag) + 4
M = cv2.getRotationMatrix2D((W / 2, H / 2), 45, 1.0)
M[0, 2] += S / 2 - W / 2
M[1, 2] += S / 2 - H / 2
Minv = cv2.invertAffineTransform(M)
mr = cv2.warpAffine(mask, M, (S, S), flags=cv2.INTER_NEAREST)
gr = cv2.warpAffine(gray, M, (S, S), flags=cv2.INTER_LINEAR, borderValue=255)
# keep only diagonal walls in the rotated frame: bands that are axis aligned THERE
# (axis-aligned originals become diagonal and vanish under directional opening)


def back(pts):
    pts = np.array(pts, float)
    return (Minv[:, :2] @ pts.T).T + Minv[:, 2]


for (x0, y0, x1, y1, ink) in gaps_h(mr, gr, int(9 * PX_PER_FT), CORNER, min_run=40):
    add(back([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), "D1", ink)
mrt, grt = mr.T.copy(), gr.T.copy()
for (y0, x0, y1, x1, ink) in gaps_h(mrt, grt, int(9 * PX_PER_FT), CORNER, min_run=40):
    add(back([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), "D2", ink)

json.dump({"px_per_ft": PX_PER_FT, "size": [W, H], "walls": wall_polys, "openings": openings},
          open(out + "/trace_raw.json", "w"))
print("polys", len(snapped), "verts", sum(len(p) for p in snapped), "openings", len(openings))

# ---------------------------------------------------------------- annotate
vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
vis = (vis * 0.45 + 135).clip(0, 255).astype(np.uint8)
SC = 1.5
vis = cv2.resize(vis, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
for p in snapped:
    cv2.polylines(vis, [(np.array(p) * SC).astype(np.int32)], True, (200, 90, 0), 2)
for o in openings:
    pts = (np.array(o["poly"]) * SC).astype(np.int32)
    col = (0, 150, 0) if o["ink"] > 0.12 else (0, 0, 230)
    cv2.fillPoly(vis, [pts], col)
    cx, cy = int(o["c"][0] * SC), int(o["c"][1] * SC)
    cv2.putText(vis, str(o["id"]), (cx - 12, cy - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 5)
    cv2.putText(vis, str(o["id"]), (cx - 12, cy - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (120, 0, 120), 2)
cv2.imwrite(out + "/trace_annot_full.png", vis)
hh, ww = vis.shape[:2]
k = 0
for r in range(2):
    for c in range(2):
        y0, x0 = int(r * hh / 2), int(c * ww / 2)
        tile = vis[max(0, y0 - 40):min(hh, y0 + hh // 2 + 40), max(0, x0 - 40):min(ww, x0 + ww // 2 + 40)]
        cv2.imwrite(f"{out}/trace_annot_{r}{c}.png", tile)
        k += 1
