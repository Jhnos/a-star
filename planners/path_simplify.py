# planners/path_simplify.py

from typing import List, Tuple
import numpy as np

# ====== 參數集中 ======
# 無
# ======================

Coord = Tuple[int, int]

def _grid_los(grid: np.ndarray, a: Coord, b: Coord) -> bool:
    (r0, c0), (r1, c1) = a, b
    dr, dc = abs(r1 - r0), abs(c1 - c0)
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        if grid[r, c] == 1:
            return False
        if (r, c) == (r1, c1):
            break
        e2 = 2 * err
        if e2 > -dc:
            err -= dc; r += sr
        if e2 < dr:
            err += dr; c += sc
    return True

def simplify(grid: List[List[int]], path: List[Coord]) -> List[Coord]:
    if not path: return path
    arr = np.array(grid, dtype=np.uint8)
    keep = [path[0]]
    last = path[0]
    for i in range(1, len(path)-1):
        if _grid_los(arr, last, path[i+1]):
            continue
        keep.append(path[i])
        last = path[i]
    keep.append(path[-1])
    return keep
