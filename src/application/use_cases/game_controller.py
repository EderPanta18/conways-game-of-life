# application/use_cases/game_controller.py

from typing import Literal

from domain.entities.grid import Grid
from domain.services.game_rules import step
from application.dto.stats_data import StatsData


class GameController:
    """Orquesta el ciclo del Juego y expone casos de uso a la UI."""

    def __init__(self, grid: Grid):
        self.grid = grid
        self.running: bool = False  # Indica si el juego está en ejecución
        self.mode: Literal["move", "edit"] = "move"  # Modo actual de la UI
        self.generation: int = 0  # Contador de generaciones

    # --------------------------
    # Control de ejecución y modos
    # --------------------------

    def toggle_run(self) -> None:
        """Alterna entre pausado y en ejecución."""
        self.running = not self.running
        if self.running:
            self.mode = "move"  # Solo se puede correr en modo "move"

    def set_move_mode(self) -> None:
        """Fuerza el modo movimiento."""
        self.mode = "move"

    def set_edit_mode(self) -> None:
        """Permite edición solo si el juego está pausado."""
        if not self.running:
            self.mode = "edit"

    # --------------------------
    # Evolución
    # --------------------------

    def do_step(self) -> None:
        """Avanza una generación aplicando las reglas del juego."""
        self.grid.cells = step(self.grid.cells)
        self.generation += 1

    # --------------------------
    # Edición de contenido
    # --------------------------

    def randomize(self, p: float = 0.5) -> None:
        """Llena aleatoriamente la grilla (solo si está pausado)."""
        if not self.running:
            self.grid.randomize(p)
            self.generation = 0

    def clear(self) -> None:
        """Limpia la grilla (solo si está pausado)."""
        if not self.running:
            self.grid.clear()
            self.generation = 0

    # --------------------------
    # Cambio de tamaño
    # --------------------------

    def resize_grid(self, width: int, height: int, preserve: bool = True) -> None:
        """Redimensiona la grilla, opcionalmente preservando su contenido."""
        if self.running:
            return
        if not preserve:
            # Nueva grilla vacía
            self.grid = Grid(width, height)
            self.generation = 0
            return
        # Crear nueva grilla y copiar contenido hasta donde alcance
        old = self.grid
        new = Grid(width, height)
        h = min(old.height, new.height)
        w = min(old.width, new.width)
        new.cells[:h, :w] = old.cells[:h, :w]
        self.grid = new

    # --------------------------
    # Estadísticas
    # --------------------------

    def stats(self) -> StatsData:
        """Devuelve métricas actuales de la simulación."""
        alive = self.grid.count_alive()
        total = self.grid.width * self.grid.height
        dead = total - alive
        density = alive / total if total else 0.0
        return StatsData(
            generation=self.generation,
            alive=alive,
            dead=dead,
            density=density,
        )
