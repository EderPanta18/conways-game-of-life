# infrastructure/gui/panels/stats_panel.py

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from infrastructure.gui.ui.animated_button import AnimatedIconButton
from infrastructure.gui.panels.section_base import SectionBase
from infrastructure.gui.icon_registry import icon


class StatsPanel(SectionBase):
    saveClicked = pyqtSignal()
    loadClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Estadísticas", parent)
        self.lbl_gen = QLabel("Generación: 0")
        self.lbl_alive = QLabel("Vivas: 0")
        self.lbl_dead = QLabel("Muertas: 0")
        self.lbl_density = QLabel("Densidad: 0.00")
        for lbl in (
            self.lbl_gen,
            self.lbl_alive,
            self.lbl_dead,
            self.lbl_density,
        ):
            lbl.setStyleSheet("font-weight: 500;")
            self.layout.addWidget(lbl, 0, Qt.AlignmentFlag.AlignHCenter)

        # espacio ligero antes de los botones (sin contar título)
        self.layout.addSpacing(10)

        row = QWidget()
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(0, 0, 0, 0)
        row_l.setSpacing(10)  # espacio ligero en X entre botones
        self.btn_save = AnimatedIconButton(icon("save"), "Guardar plantilla")
        self.btn_load = AnimatedIconButton(icon("load"), "Cargar plantilla")
        row_l.addWidget(self.btn_save)
        row_l.addWidget(self.btn_load)
        self.layout.addWidget(row, 0, Qt.AlignmentFlag.AlignHCenter)

        self.btn_save.clicked.connect(self.saveClicked.emit)
        self.btn_load.clicked.connect(self.loadClicked.emit)

    def setStats(self, generation: int, alive: int, dead: int, density: float):
        self.lbl_gen.setText(f"Generación: {generation}")
        self.lbl_alive.setText(f"Vivas: {alive}")
        self.lbl_dead.setText(f"Muertas: {dead}")
        self.lbl_density.setText(f"Densidad: {density:.2f}")

    def setInteractiveEnabled(self, enabled: bool):
        self.btn_save.setEnabled(enabled)
        self.btn_load.setEnabled(enabled)
