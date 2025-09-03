# viz/plot_path.py

import argparse, json, numpy as np
import matplotlib.pyplot as plt

# ====== 參數集中 ======
FIG_OUT = "a_star_demo.png"
CELL_SIZE_M = 0.05
PATH_LINEWIDTH = 2.0
# ======================

def load_grid(json_path=None, npy_path=None):
    if json_path:
        with open(json_path, "r") as f:
            return np.array(json.load(f), dtype=np.uint8)
    return np.load(npy_path).astype(np.uint8)

def load_path(txt_path):
    pts = []
    with open(txt_path, "r") as f:
        for line in f:
            r, c = map(int, line.strip().split(","))
            pts.append((r, c))
    return np.array(pts, dtype=int)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid_json", type=str)
    ap.add_argument("--grid_npy", type=str)
    ap.add_argument("--path_txt", type=str, required=True)
    ap.add_argument("--out", type=str, default=FIG_OUT)
    args = ap.parse_args()

    grid = load_grid(args.grid_json, args.grid_npy)
    path = load_path(args.path_txt)

    H, W = grid.shape
    plt.figure()
    plt.imshow(grid, origin="upper", interpolation="nearest")
    ys = path[:,0]; xs = path[:,1]
    plt.plot(xs, ys, linewidth=PATH_LINEWIDTH)
    plt.scatter([xs[0]],[ys[0]], marker="o")
    plt.scatter([xs[-1]],[ys[-1]], marker="x")
    plt.title(f"A* Path | {H}x{W} | cell={CELL_SIZE_M}m")
    plt.xlabel("col"); plt.ylabel("row")
    plt.tight_layout()
    plt.savefig(args.out, dpi=200)
    print("saved:", args.out)

if __name__ == "__main__":
    main()
