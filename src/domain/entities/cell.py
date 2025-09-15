# domain/entities/cell.py

from dataclasses import dataclass


@dataclass
class Cell:
    x: int
    y: int
    alive: bool = False

    def toggle(self) -> None:
        self.alive = not self.alive
