# infrastructure/gui/panels/actions_panel.py

from PyQt6.QtCore import pyqtSignal, Qt
from infrastructure.gui.ui.animated_button import AnimatedIconButton
from infrastructure.gui.panels.section_base import SectionBase
from infrastructure.gui.icon_registry import icon


class ActionsPanel(SectionBase):
    toggleRun = pyqtSignal()
    toggleMode = pyqtSignal()
    randomize = pyqtSignal()
    clearClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Acciones", parent)
        self.layout.setSpacing(14)  # separación en Y entre botones
        self.btn_play = AnimatedIconButton(icon("play"), "Iniciar / Pausar")
        self.btn_mode = AnimatedIconButton(
            icon("move"), "Mover ↔ Edición (solo en pausa)"
        )
        self.btn_rand = AnimatedIconButton(icon("dice"), "Randomizar tablero")
        self.btn_clear = AnimatedIconButton(icon("clear"), "Limpiar tablero")
        for b in (self.btn_play, self.btn_mode, self.btn_rand, self.btn_clear):
            self.layout.addWidget(b, 0, Qt.AlignmentFlag.AlignHCenter)
        self.btn_play.clicked.connect(self.toggleRun.emit)
        self.btn_mode.clicked.connect(self.toggleMode.emit)
        self.btn_rand.clicked.connect(self.randomize.emit)
        self.btn_clear.clicked.connect(self.clearClicked.emit)

    def setPlayIcon(self, ic):
        self.btn_play.setIcon(ic)

    def setModeIcon(self, ic):
        self.btn_mode.setIcon(ic)

    def setInteractiveEnabled(self, enabled: bool):
        self.btn_mode.setEnabled(enabled)
        self.btn_rand.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)
