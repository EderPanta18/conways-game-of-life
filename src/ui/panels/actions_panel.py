# ui/panels/actions_panel.py

from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QHBoxLayout

from ui.icons.icon_registry import icon
from ui.widgets.animated_button import AnimatedIconButton
from .section_base import SectionBase


class ActionsPanel(SectionBase):
    """
    Panel de acciones.

    - Centraliza los botones principales de control de la simulación.
    - Emite señales al presionar cada botón (iniciar/pausar, mover/editar, randomizar, limpiar).
    - Mantiene el botón de play siempre activo para poder pausar incluso en ejecución.
    - Permite cambiar dinámicamente los íconos de play y modo según el estado del programa.
    """

    # Señales consumidas por la ventana principal
    toggleRun = pyqtSignal()
    toggleMode = pyqtSignal()
    randomize = pyqtSignal()
    clearClicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Acciones", parent)
        # Separación vertical entre botones
        self.layout.setSpacing(14)

        # Construcción UI
        self._build_buttons_row()

        # Conexiones de señales
        self._connect_signals()

    # -------------------------------------------------------------------------
    # Construcción de UI
    # -------------------------------------------------------------------------

    def _build_buttons_row(self) -> None:
        """
        Crea la fila de botones de acción y la agrega al layout principal.
        """
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        self.btn_play = AnimatedIconButton(icon("play"), "Iniciar / Pausar")
        self.btn_mode = AnimatedIconButton(
            icon("move"), "Mover ↔ Edición (solo en pausa)"
        )
        self.btn_rand = AnimatedIconButton(icon("dice"), "Randomizar tablero")
        self.btn_clear = AnimatedIconButton(icon("clear"), "Limpiar tablero")

        # Ensamble centrado
        for btn in (self.btn_play, self.btn_mode, self.btn_rand, self.btn_clear):
            row_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)

        self.layout.addWidget(row, 0, Qt.AlignmentFlag.AlignHCenter)

    # -------------------------------------------------------------------------
    # Señales
    # -------------------------------------------------------------------------

    def _connect_signals(self) -> None:
        """
        Conecta los clics de los botones a las señales públicas del panel.
        """
        self.btn_play.clicked.connect(self.toggleRun.emit)
        self.btn_mode.clicked.connect(self.toggleMode.emit)
        self.btn_rand.clicked.connect(self.randomize.emit)
        self.btn_clear.clicked.connect(self.clearClicked.emit)

    # -------------------------------------------------------------------------
    # API consumida por la ventana principal / binder de ejecución
    # -------------------------------------------------------------------------

    def setPlayIcon(self, ic: QIcon) -> None:
        """
        Actualiza el icono del botón de reproducción/pausa.
        """
        self.btn_play.setIcon(ic)

    def setModeIcon(self, ic: QIcon) -> None:
        """
        Actualiza el icono del botón de cambio de modo (mover/editar).
        """
        self.btn_mode.setIcon(ic)

    def setInteractiveEnabled(self, enabled: bool) -> None:
        """
        Habilita/inhabilita los controles de edición y contenido.

        Nota:
        - Se mantiene el botón de play activo incluso si enabled es False
          (para poder pausar mientras corre). Si se desea deshabilitarlo,
          ajustar explícitamente desde la ventana principal.
        """
        self.btn_mode.setEnabled(enabled)
        self.btn_rand.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)
        # self.btn_play permanece habilitado para permitir pausar en ejecución.
