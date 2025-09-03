# planners/bidirectional_astar.py

from typing import List, Tuple, Optional, Dict
import heapq

# ====== 參數集中 ======
GRID_4_CONNECTED: bool = True
DIAGONAL_COST: float = 1.41421356237
ALLOW_DIAGONAL_THROUGH_CORNERS: bool = False
TIE_BREAK_EPS: float = 1e-6
# ======================

Coord = Tuple[int, int]

def _heuristic(a: Coord, b: Coord) -> float:
    if GRID_4_CONNECTED:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (max(dx, dy) - min(dx, dy)) + DIAGONAL_COST * min(dx, dy)

def _neighbors(p: Coord, H: int, W: int):
    r, c = p
    nbrs = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
    if not GRID_4_CONNECTED:
        nbrs += [(r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1)]
    return [(nr, nc) for (nr, nc) in nbrs if 0 <= nr < H and 0 <= nc < W]

def _blocked(grid, a: Coord, b: Coord) -> bool:
    if grid[b[0]][b[1]] == 1:
        return True
    if not GRID_4_CONNECTED and not ALLOW_DIAGONAL_THROUGH_CORNERS:
        ar, ac = a; br, bc = b
        if ar != br and ac != bc:
            if grid[ar][bc] == 1 and grid[br][ac] == 1:
                return True
    return False

def _step_cost(a: Coord, b: Coord) -> float:
    if GRID_4_CONNECTED or (a[0] == b[0] or a[1] == b[1]):
        return 1.0
    return DIAGONAL_COST

def _reconstruct(came_f: Dict[Coord, Coord], came_b: Dict[Coord, Coord], meet: Coord) -> List[Coord]:
    # fwd: start->meet, bwd: goal->meet
    path_f = [meet]
    cur = meet
    while cur in came_f:
        cur = came_f[cur]
        path_f.append(cur)
    path_f.reverse()
    path_b = []
    cur = meet
    while cur in came_b:
        cur = came_b[cur]
        path_b.append(cur)
    return path_f + path_b  # meet 重複一次沒關係，可視需要去重

def bidir_a_star(grid: List[List[int]], start: Coord, goal: Coord) -> Optional[List[Coord]]:
    H, W = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return None
    if start == goal:
        return [start]

    # for

