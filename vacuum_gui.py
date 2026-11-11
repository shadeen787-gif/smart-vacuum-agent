"""
Goal-Based Smart Vacuum Cleaner - Graphical Simulation
Agent type : Goal-based agent
Language   : Python 3 + tkinter (comes built-in with Python)

Goals (in order):
  1. Clean every dirty cell in the room.
  2. Return to the charging base.

Agent cycle: Perceive -> Update goal -> Plan (BFS) -> Act
"""

import random
import tkinter as tk
from collections import deque

ROWS, COLS = 9, 12
CELL = 56
BASE = (0, 0)
DIRT_COUNT = 12

# Furniture: (row, col) cells that block the vacuum
OBSTACLES = {
    (1, 3), (2, 3), (3, 3),          # sofa
    (5, 6), (5, 7), (6, 6),          # table
    (3, 9), (4, 9),                  # shelf
    (7, 2), (7, 3),                  # bed
}

# Colors
C_FLOOR = "#f4efe6"
C_GRID = "#e0d8c8"
C_OBST = "#6b5b4b"
C_DIRT = "#8d5a2b"
C_BASE = "#3ba55d"
C_TRAIL = "#cfe8ff"
C_PATH = "#ff9f1c"
C_BOT = "#1f6feb"
BG = "#1e1f26"
FG = "#f0f0f0"


class Room:
    def __init__(self):
        self.obstacles = set(OBSTACLES)
        free = [(r, c) for r in range(ROWS) for c in range(COLS)
                if (r, c) not in self.obstacles and (r, c) != BASE]
        self.dirt = set(random.sample(free, DIRT_COUNT))

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < ROWS and 0 <= c < COLS and pos not in self.obstacles


class GoalBasedVacuum:
    def __init__(self, room):
        self.room = room
        self.pos = BASE
        self.moves = 0
        self.cleaned = 0
        self.goal = "CLEAN ALL DIRT"
        self.path = []
        self.trail = {BASE}

    def perceive(self):
        return set(self.room.dirt)

    def update_goal(self, dirt):
        if dirt:
            self.goal = "CLEAN ALL DIRT"
        elif self.pos != BASE:
            self.goal = "RETURN TO BASE"
        else:
            self.goal = "DONE"

    def plan(self, targets):
        queue = deque([(self.pos, [])])
        visited = {self.pos}
        while queue:
            cur, path = queue.popleft()
            if cur in targets:
                return path
            r, c = cur
            for nxt in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if self.room.in_bounds(nxt) and nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return []

    def step(self):
        dirt = self.perceive()
        self.update_goal(dirt)
        if self.goal == "DONE":
            self.path = []
            return "DONE"
        if self.pos in dirt:
            self.room.dirt.remove(self.pos)
            self.cleaned += 1
            return "SUCK"
        targets = dirt if self.goal == "CLEAN ALL DIRT" else {BASE}
        self.path = self.plan(targets)
        if self.path:
            self.pos = self.path[0]
            self.trail.add(self.pos)
            self.moves += 1
            return "MOVE"
        return "IDLE"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Goal-Based Smart Vacuum - Simulation")
        root.configure(bg=BG)
        self.running = False
        self.job = None

        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                bg=C_FLOOR, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=12, pady=12)

        panel = tk.Frame(root, bg=BG)
        panel.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="n")

        def label(text, size=11, bold=False):
            return tk.Label(panel, text=text, bg=BG, fg=FG, anchor="w",
                            font=("Arial", size, "bold" if bold else "normal"))

        label("Smart Vacuum Agent", 15, True).pack(fill="x", pady=(0, 2))
        label("Type: Goal-Based Agent", 10).pack(fill="x", pady=(0, 12))

        self.v_goal = tk.StringVar()
        self.v_action = tk.StringVar()
        self.v_dirt = tk.StringVar()
        self.v_moves = tk.StringVar()
        self.v_clean = tk.StringVar()
        for var in (self.v_goal, self.v_action, self.v_dirt,
                    self.v_moves, self.v_clean):
            tk.Label(panel, textvariable=var, bg=BG, fg=FG, anchor="w",
                     font=("Consolas", 11)).pack(fill="x", pady=2)

        tk.Label(panel, text="", bg=BG).pack()
        self.btn_start = tk.Button(panel, text="Start", width=14,
                                   command=self.toggle)
        self.btn_start.pack(pady=3)
        tk.Button(panel, text="Step", width=14,
                  command=self.one_step).pack(pady=3)
        tk.Button(panel, text="New Room", width=14,
                  command=self.reset).pack(pady=3)

        label("Speed", 10).pack(fill="x", pady=(12, 0))
        self.speed = tk.Scale(panel, from_=1, to=10, orient="horizontal",
                              bg=BG, fg=FG, highlightthickness=0, length=140)
        self.speed.set(5)
        self.speed.pack()

        legend = tk.Frame(panel, bg=BG)
        legend.pack(fill="x", pady=(14, 0))
        for color, text in ((C_BOT, "Vacuum"), (C_DIRT, "Dirt"),
                            (C_OBST, "Furniture"), (C_BASE, "Base"),
                            (C_PATH, "Planned path"), (C_TRAIL, "Cleaned trail")):
            row = tk.Frame(legend, bg=BG)
            row.pack(fill="x", pady=1)
            tk.Label(row, bg=color, width=2).pack(side="left")
            tk.Label(row, text=" " + text, bg=BG, fg=FG,
                     font=("Arial", 9)).pack(side="left")

        self.reset()

    # ---------- control ----------
    def reset(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
        self.running = False
        self.btn_start.config(text="Start")
        self.room = Room()
        self.agent = GoalBasedVacuum(self.room)
        self.last_action = "-"
        self.refresh()

    def toggle(self):
        if self.agent.goal == "DONE":
            return
        self.running = not self.running
        self.btn_start.config(text="Pause" if self.running else "Start")
        if self.running:
            self.loop()

    def loop(self):
        if not self.running:
            return
        self.one_step()
        if self.agent.goal == "DONE":
            self.running = False
            self.btn_start.config(text="Start")
            return
        delay = int(900 / self.speed.get())
        self.job = self.root.after(delay, self.loop)

    def one_step(self):
        if self.agent.goal == "DONE":
            return
        self.last_action = self.agent.step()
        self.refresh()

    # ---------- drawing ----------
    def cell_box(self, pos, pad=0):
        r, c = pos
        return (c * CELL + pad, r * CELL + pad,
                (c + 1) * CELL - pad, (r + 1) * CELL - pad)

    def center(self, pos):
        r, c = pos
        return c * CELL + CELL / 2, r * CELL + CELL / 2

    def refresh(self):
        cv = self.canvas
        cv.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                p = (r, c)
                fill = C_TRAIL if p in self.agent.trail else C_FLOOR
                cv.create_rectangle(*self.cell_box(p), fill=fill, outline=C_GRID)
        for p in self.room.obstacles:
            cv.create_rectangle(*self.cell_box(p, 3), fill=C_OBST,
                                outline="", width=0)
        cv.create_rectangle(*self.cell_box(BASE, 4), fill=C_BASE, outline="")
        cv.create_text(*self.center(BASE), text="BASE", fill="white",
                       font=("Arial", 9, "bold"))
        for p in self.room.dirt:
            x, y = self.center(p)
            for dx, dy, s in ((-8, -4, 9), (7, -6, 7), (0, 8, 10), (9, 6, 6)):
                cv.create_oval(x + dx - s / 2, y + dy - s / 2,
                               x + dx + s / 2, y + dy + s / 2,
                               fill=C_DIRT, outline="")
        if self.agent.path:
            pts = [self.center(self.agent.pos)]
            pts += [self.center(p) for p in self.agent.path]
            if len(pts) > 1:
                cv.create_line(*[v for pt in pts for v in pt], fill=C_PATH,
                               width=3, dash=(6, 4))
                ex, ey = pts[-1]
                cv.create_oval(ex - 6, ey - 6, ex + 6, ey + 6,
                               outline=C_PATH, width=2)
        x, y = self.center(self.agent.pos)
        color = "#ffd166" if self.last_action == "SUCK" else C_BOT
        cv.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color,
                       outline="white", width=2)
        cv.create_oval(x - 7, y - 7, x + 7, y + 7, fill="white", outline="")

        self.v_goal.set(f"Goal   : {self.agent.goal}")
        self.v_action.set(f"Action : {self.last_action}")
        self.v_dirt.set(f"Dirt left : {len(self.room.dirt)}")
        self.v_moves.set(f"Moves : {self.agent.moves}")
        self.v_clean.set(f"Cleaned : {self.agent.cleaned}")
        if self.agent.goal == "DONE":
            cv.create_rectangle(COLS * CELL / 2 - 150, ROWS * CELL / 2 - 30,
                                COLS * CELL / 2 + 150, ROWS * CELL / 2 + 30,
                                fill="#000000", outline="white")
            cv.create_text(COLS * CELL / 2, ROWS * CELL / 2,
                           text="Room clean - back at base!", fill="white",
                           font=("Arial", 14, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
