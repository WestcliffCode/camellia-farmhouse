"""Side-by-side: elevation drawing (left) and orthographic render (right). elev_compare.py out drawing render"""
import sys, cv2, numpy as np
out, a, b = sys.argv[1:4]
A, B = cv2.imread(a), cv2.imread(b)
h = 520
A = cv2.resize(A, (int(A.shape[1] * h / A.shape[0]), h), interpolation=cv2.INTER_AREA)
B = cv2.resize(B, (int(B.shape[1] * h / B.shape[0]), h), interpolation=cv2.INTER_AREA)
cv2.imwrite(out, np.hstack([A, B]))
