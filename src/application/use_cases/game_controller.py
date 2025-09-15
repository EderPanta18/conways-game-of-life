# application/use_cases/game_controller.py

from domain.entities.grid import Grid
from domain.services.game_rules import step


class GameController:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.running = False
        self.mode = "move"  # "move" | "edit"
        self.generation = 0

    def toggle_run(self):
        self.running = not self.running
        if self.running:
            self.mode = "move"

    def set_move_mode(self):
        self.mode = "move"

    def set_edit_mode(self):
        if not self.running:
            self.mode = "edit"

    def do_step(self):
        self.grid.cells = step(self.grid.cells)
        self.generation += 1

    def randomize(self, p: float = 0.5):
        if not self.running:
            self.grid.randomize(p)
            self.generation = 0

    def clear(self):
        if not self.running:
            self.grid.clear()
            self.generation = 0

    def resize_grid(self, width: int, height: int, preserve: bool = True):
        if self.running:
            return
        if not preserve:
            self.grid = Grid(width, height)
            self.generation = 0
            return
        old = self.grid
        new = Grid(width, height)
        h = min(old.height, new.height)
        w = min(old.width, new.width)
        new.cells[:h, :w] = old.cells[:h, :w]
        self.grid = new

    def stats(self):
        alive = self.grid.count_alive()
        total = self.grid.width * self.grid.height
        dead = total - alive
        density = alive / total if total else 0.0
        return {
            "generation": self.generation,
            "alive": alive,
            "dead": dead,
            "density": density,
        }
