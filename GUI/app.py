# gui/app.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



import tkinter as tk
from tkinter import filedialog, messagebox
import json
import numpy as np
from typing import List, Tuple, Optional

from planners.a_star import a_star, GRID_4_CONNECTED
from planners import a_star as a_star_cfg  # 修改連通度用
from planners.path_simplify import simplify

# ====== 參數集中（GUI 全域變數） ======
GRID_ROWS: int = 30
GRID_COLS: int = 40
CELL_PX: int   = 20          # 每格像素
BG_COLOR: str  = "#f0f0f0"
FREE_COLOR: str = "#ffffff"
OBST_COLOR: str = "#222222"
PATH_COLOR: str = "#1f77b4"
START_COLOR:str = "#2ca02c"
GOAL_COLOR: str = "#d62728"
SHOW_GRID_LINE: bool = True
GRIDLINE_COLOR: str = "#cccccc"
SMOOTH_AFTER_PLAN: bool = True
CELL_SIZE_M: float = 0.05     # 日後接 Isaac 時使用的解析度
# ======================================

Coord = Tuple[int, int]

class AStarGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("A* Planner (a-star-dev)")
        self.configure(bg=BG_COLOR)
        self.grid_data = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.uint8)  # 0=free,1=obst
        self.start: Optional[Coord] = (0, 0)
        self.goal: Optional[Coord]  = (GRID_ROWS-1, GRID_COLS-1)
        self.path: List[Coord] = []

        self.canvas = tk.Canvas(self, width=GRID_COLS*CELL_PX, height=GRID_ROWS*CELL_PX, bg=FREE_COLOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

        # Buttons
        tk.Button(self, text="New", command=self.new_grid).grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        tk.Button(self, text="Load", command=self.load_grid).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        tk.Button(self, text="Save", command=self.save_grid).grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        tk.Button(self, text="Run A*", command=self.run_astar).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        tk.Button(self, text="Clear Path", command=self.clear_path).grid(row=1, column=4, sticky="ew", padx=5, pady=5)
        self.conn_btn = tk.Button(self, text="4-connected", command=self.toggle_conn)
        self.conn_btn.grid(row=1, column=5, sticky="ew", padx=5, pady=5)

        # Hints
        hint = ("滑鼠左鍵：切換障礙/可走\n"
                "右鍵：設定起點   Shift+右鍵：設定終點\n"
                "Ctrl+S：存檔  Ctrl+O：開檔  Ctrl+N：新地圖")
        tk.Label(self, text=hint, bg=BG_COLOR, justify="left").grid(row=2, column=0, columnspan=6, sticky="w", padx=10)

        # Bindings
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Shift-Button-3>", self.on_shift_right_click)
        self.bind("<Control-s>", lambda e: self.save_grid())
        self.bind("<Control-o>", lambda e: self.load_grid())
        self.bind("<Control-n>", lambda e: self.new_grid())

        self.draw_all()

    # ---- Grid ops ----
    def new_grid(self):
        self.grid_data[:] = 0
        self.start = (0, 0)
        self.goal = (GRID_ROWS-1, GRID_COLS-1)
        self.path = []
        self.draw_all()

    def load_grid(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path: return
        with open(path, "r") as f:
            arr = np.array(json.load(f), dtype=np.uint8)
        if arr.ndim != 2:
            messagebox.showerror("錯誤", "JSON 格式需為 2D 0/1 陣列")
            return
        if arr.shape != self.grid_data.shape:
            messagebox.showerror("錯誤", f"尺寸須為 {GRID_ROWS}x{GRID_COLS}")
            return
        self.grid_data = arr
        self.path = []
        self.draw_all()

    def save_grid(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path: return
        with open(path, "w") as f:
            json.dump(self.grid_data.tolist(), f)
        messagebox.showinfo("訊息", f"已儲存地圖：{os.path.basename(path)}")

    # ---- Mouse ----
    def cell_from_xy(self, x, y) -> Coord:
        r = min(max(int(y // CELL_PX), 0), GRID_ROWS-1)
        c = min(max(int(x // CELL_PX), 0), GRID_COLS-1)
        return (r, c)

    def on_left_click(self, e):
        r, c = self.cell_from_xy(e.x, e.y)
        if (r, c) == self.start or (r, c) == self.goal:
            return
        self.grid_data[r, c] = 1 - self.grid_data[r, c]  # toggle
        self.path = []
        self.draw_all()

    def on_right_click(self, e):
        r, c = self.cell_from_xy(e.x, e.y)
        if self.grid_data[r, c] == 1:
            return
        self.start = (r, c)
        self.path = []
        self.draw_all()

    def on_shift_right_click(self, e):
        r, c = self.cell_from_xy(e.x, e.y)
        if self.grid_data[r, c] == 1:
            return
        self.goal = (r, c)
        self.path = []
        self.draw_all()

    # ---- Plan ----
    def run_astar(self):
        grid_list: List[List[int]] = self.grid_data.tolist()
        path = a_star(grid_list, self.start, self.goal)
        if path is None:
            messagebox.showwarning("無路徑", "找不到可行路徑（檢查起訖或障礙配置）")
            self.path = []
        else:
            if SMOOTH_AFTER_PLAN:
                path = simplify(grid_list, path)
            self.path = path
        self.draw_all()

    def clear_path(self):
        self.path = []
        self.draw_all()

    def toggle_conn(self):
        a_star_cfg.GRID_4_CONNECTED = not a_star_cfg.GRID_4_CONNECTED
        self.conn_btn.configure(text="4-connected" if a_star_cfg.GRID_4_CONNECTED else "8-connected")
        self.path = []
        self.draw_all()

    # ---- Render ----
    def draw_all(self):
        self.canvas.delete("all")
        # cells
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x0, y0 = c*CELL_PX, r*CELL_PX
                x1, y1 = x0 + CELL_PX, y0 + CELL_PX
                fill = OBST_COLOR if self.grid_data[r, c] == 1 else FREE_COLOR
                self.canvas.create_rectangle(x0, y0, x1, y1, outline=GRIDLINE_COLOR if SHOW_GRID_LINE else fill, fill=fill)
        # start / goal
        if self.start:
            r, c = self.start
            x0, y0 = c*CELL_PX, r*CELL_PX
            self.canvas.create_rectangle(x0, y0, x0+CELL_PX, y0+CELL_PX, outline=START_COLOR, width=2)
        if self.goal:
            r, c = self.goal
            x0, y0 = c*CELL_PX, r*CELL_PX
            self.canvas.create_rectangle(x0, y0, x0+CELL_PX, y0+CELL_PX, outline=GOAL_COLOR, width=2)
        # path
        if self.path:
            pts = []
            for (r, c) in self.path:
                xc = c*CELL_PX + CELL_PX/2
                yc = r*CELL_PX + CELL_PX/2
                pts.append((xc, yc))
            for i in range(len(pts)-1):
                x0, y0 = pts[i]
                x1, y1 = pts[i+1]
                self.canvas.create_line(x0, y0, x1, y1, fill=PATH_COLOR, width=2)

def main():
    app = AStarGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
