# domain/entities/grid.py

import numpy as np
from domain.entities.cell import Cell

MIN_SIZE = 50
MAX_SIZE = 3000


class Grid:
    def __init__(self, width: int, height: int):
        if not (MIN_SIZE <= width <= MAX_SIZE and MIN_SIZE <= height <= MAX_SIZE):
            raise ValueError("Tamaño fuera de límites [50..10000]")
        self.width = width
        self.height = height
        self.cells = np.zeros((height, width), dtype=np.uint8)  # 0=muerta, 1=viva

    def toggle_cell(self, x: int, y: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y, x] ^= 1

    def get_cell(self, x: int, y: int) -> Cell:
        if 0 <= x < self.width and 0 <= y < self.height:
            return Cell(x=x, y=y, alive=bool(self.cells[y, x]))
        raise IndexError("Coordenadas fuera de rango")

    def set_cell(self, cell: Cell):
        if 0 <= cell.x < self.width and 0 <= cell.y < self.height:
            self.cells[cell.y, cell.x] = 1 if cell.alive else 0

    def randomize(self, p: float = 0.5):
        self.cells = (np.random.random((self.height, self.width)) < p).astype(np.uint8)

    def clear(self):
        self.cells.fill(0)

    def count_alive(self) -> int:
        return int(self.cells.sum())

    def count_dead(self) -> int:
        return int(self.width * self.height - self.count_alive())
