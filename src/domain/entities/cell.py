# domain/entities/cell.py

from dataclasses import dataclass


@dataclass
class Cell:
    """Celda del Juego de la Vida (coordenadas enteras y estado)."""

    x: int
    y: int
    alive: bool = False

    def toggle(self) -> None:
        """Alterna el estado de vida de la celda."""
        self.alive = not self.alive
