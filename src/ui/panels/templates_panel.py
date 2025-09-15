# ui/panels/templates_panel.py

from typing import Optional

from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

from ui.icons.icon_registry import icon
from ui.widgets.animated_button import AnimatedIconButton
from .section_base import SectionBase


class TemplatesPanel(SectionBase):
    """
    Panel de plantillas.

    - Contiene botones para guardar y cargar configuraciones de tablero.
    - Emite señales públicas al presionar los botones, delegando la lógica a la ventana principal.
    """

    # Señales públicas
    saveClicked = pyqtSignal()
    loadClicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Plantillas", parent)

        # Construcción de UI
        self._build_buttons_row()

        # Señales
        self._connect_signals()

    # -------------------------------------------------------------------------
    # Construcción de UI
    # -------------------------------------------------------------------------
    def _build_buttons_row(self) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        self.btn_save = AnimatedIconButton(icon("save"), "Guardar plantilla")
        self.btn_load = AnimatedIconButton(icon("load"), "Cargar plantilla")

        row_layout.addWidget(self.btn_save, 0, Qt.AlignmentFlag.AlignHCenter)
        row_layout.addWidget(self.btn_load, 0, Qt.AlignmentFlag.AlignHCenter)

        self.layout.addWidget(row, 0, Qt.AlignmentFlag.AlignHCenter)

    # -------------------------------------------------------------------------
    # Señales
    # -------------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self.btn_save.clicked.connect(self.saveClicked.emit)
        self.btn_load.clicked.connect(self.loadClicked.emit)

    # -------------------------------------------------------------------------
    # API pública
    # -------------------------------------------------------------------------

    def setInteractiveEnabled(self, enabled: bool) -> None:
        self.btn_save.setEnabled(enabled)
        self.btn_load.setEnabled(enabled)
