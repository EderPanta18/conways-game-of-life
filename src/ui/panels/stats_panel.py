# ui/panels/stats_panel.py

from typing import Optional

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt

from application.dto.stats_data import StatsData
from .section_base import SectionBase


class StatsPanel(SectionBase):
    """
    Panel de estadísticas.

    - Muestra en pantalla las métricas principales del juego (generación, vivas, muertas, densidad).
    - Crea etiquetas alineadas y estiladas en el layout del contenedor.
    - Actualiza dinámicamente el texto de cada etiqueta a partir de valores numéricos.
    - Expone un método para recibir directamente un objeto StatsData y refrescar la vista.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Estadísticas", parent)

        # Configuración de formato (constante simple; ajustar si se requiere)
        self._density_decimals: int = 2

        # Construcción de UI
        self._build_metric_labels()

    # -------------------------------------------------------------------------
    # Construcción de UI
    # -------------------------------------------------------------------------

    def _build_metric_labels(self) -> None:
        self.lbl_gen = QLabel("Generación: 0")
        self.lbl_alive = QLabel("Vivas: 0")
        self.lbl_dead = QLabel("Muertas: 0")
        self.lbl_density = QLabel("Densidad: 0.00")

        for lbl in (self.lbl_gen, self.lbl_alive, self.lbl_dead, self.lbl_density):
            lbl.setStyleSheet("font-weight: 500;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.layout.addWidget(lbl, 0, Qt.AlignmentFlag.AlignHCenter)

        self.layout.addSpacing(10)

    # -------------------------------------------------------------------------
    # API pública
    # -------------------------------------------------------------------------

    def setStats(self, generation: int, alive: int, dead: int, density: float) -> None:
        self.lbl_gen.setText(f"Generación: {int(generation)}")
        self.lbl_alive.setText(f"Vivas: {int(alive)}")
        self.lbl_dead.setText(f"Muertas: {int(dead)}")
        self.lbl_density.setText(
            f"Densidad: {float(density):.{self._density_decimals}f}"
        )

    def set_stats_data(self, stats: StatsData) -> None:
        self.setStats(stats.generation, stats.alive, stats.dead, stats.density)
