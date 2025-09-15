# domain/entities/grid.py

import numpy as np

from config.settings import (
    MIN_SIZE,
    MAX_SIZE,
)
from domain.entities.cell import Cell


class Grid:
    """Tablero del Juego de la Vida respaldado por un arreglo NumPy uint8 (0=muerta, 1=viva)."""

    def __init__(self, width: int, height: int) -> None:
        # Valida que el tamaño esté dentro de los límites definidos en la configuración
        if not (MIN_SIZE <= width <= MAX_SIZE and MIN_SIZE <= height <= MAX_SIZE):
            raise ValueError(f"Tamaño fuera de límites [{MIN_SIZE}..{MAX_SIZE}]")

        # Se asegura de que width y height sean enteros
        self.width = int(width)
        self.height = int(height)

        # Inicializa la grilla como una matriz de ceros (todas las celdas muertas)
        # dtype=uint8 => valores 0 o 1 (eficiente en memoria)
        self.cells = np.zeros((self.height, self.width), dtype=np.uint8)

    # --------------------------
    # Mutaciones básicas de celdas
    # --------------------------

    def toggle_cell(self, x: int, y: int) -> None:
        """Invierte el estado de una celda (muerta→viva, viva→muerta)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y, x] ^= 1  # XOR con 1: cambia 0→1 o 1→0

    def get_cell(self, x: int, y: int) -> Cell:
        """Devuelve un objeto Cell con las coordenadas y el estado actual."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return Cell(x=x, y=y, alive=bool(self.cells[y, x]))
        raise IndexError("Coordenadas fuera de rango")

    def set_cell(self, cell: Cell) -> None:
        """Fija el estado de una celda usando un objeto Cell."""
        if 0 <= cell.x < self.width and 0 <= cell.y < self.height:
            self.cells[cell.y, cell.x] = 1 if cell.alive else 0

    # --------------------------
    # Utilidades sobre el contenido de la grilla
    # --------------------------

    def randomize(self, p: float = 0.5) -> None:
        """Rellena la grilla con celdas vivas según una probabilidad `p` (entre 0 y 1)."""
        self.cells = (np.random.random((self.height, self.width)) < p).astype(np.uint8)

    def clear(self) -> None:
        """Limpia la grilla (todas las celdas muertas)."""
        self.cells.fill(0)

    def count_alive(self) -> int:
        """Cuenta el total de celdas vivas en la grilla."""
        return int(self.cells.sum())

    def count_dead(self) -> int:
        """Cuenta el total de celdas muertas en la grilla."""
        return int(self.width * self.height - self.count_alive())
