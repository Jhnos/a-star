# planners/a_star.py

from typing import List, Tuple, Optional, Dict
import heapq

# ====== 參數集中 ======
GRID_4_CONNECTED: bool = True           # True=4向；False=8向
DIAGONAL_COST: float = 1.41421356237    # 8向時的斜向成本
ALLOW_DIAGONAL_THROUGH_CORNERS: bool = False  # 禁止斜向貼角穿越
TIE_BREAK_EPS: float = 1e-6             # 打破啟發式平手
# ======================

Coord = Tuple[int, int]

def _heuristic(a: Coord, b: Coord) -> float:
    if GRID_4_CONNECTED:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (max(dx, dy) - min(dx, dy)) + DIAGONAL_COST * min(dx, dy)  # Octile

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

def _reconstruct(came_from: Dict[Coord, Coord], cur: Coord):
    path = [cur]
    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path

def a_star(grid: List[List[int]], start: Coord, goal: Coord) -> Optional[List[Coord]]:
    H, W = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return None

    g = {start: 0.0}
    h0 = _heuristic(start, goal)
    came: Dict[Coord, Coord] = {}
    open_heap = [(h0, 0.0, start)]
    in_open = {start}

    while open_heap:
        _, _, cur = heapq.heappop(open_heap)
        in_open.discard(cur)
        if cur == goal:
            return _reconstruct(came, cur)

        for nb in _neighbors(cur, H, W):
            if _blocked(grid, cur, nb):
                continue
            ng = g[cur] + _step_cost(cur, nb)
            if ng < g.get(nb, float("inf")):
                came[nb] = cur
                g[nb] = ng
                hn = _heuristic(nb, goal)
                fn = ng + hn + TIE_BREAK_EPS * hn
                if nb not in in_open:
                    in_open.add(nb)
                    import heapq as _hq
                    _hq.heappush(open_heap, (fn, hn, nb))
    return None

if __name__ == "__main__":
    grid = [
        [0,0,0,0,0],
        [1,1,0,1,0],
        [0,0,0,1,0],
        [0,1,0,0,0],
        [0,1,0,1,0],
    ]
    print("Path:", a_star(grid, (0,0), (4,4)))
