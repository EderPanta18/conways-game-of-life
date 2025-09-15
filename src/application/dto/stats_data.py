# application/dto/stats_panel.py

from dataclasses import dataclass


@dataclass(frozen=True)
class StatsData:
    """
    Contenedor inmutable para estadísticas del juego.

    Permite pasar todas las métricas de forma atómica y tipada, facilitando
    la compatibilidad con otros flujos (p. ej., mapeos dict) y pruebas.
    """

    generation: int
    alive: int
    dead: int
    density: float
