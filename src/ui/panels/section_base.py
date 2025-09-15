# ui/panels/section_base.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from ui.theme import SECTION_BG, TEXT_PRIMARY


class SectionBase(QFrame):
    """
    Contenedor base para secciones del panel lateral.

    Aplica estilo consistente (fondo, bordes, tipografía) y
    construye un layout vertical con un título centrado.
    """

    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        # Construcción de UI
        self._init_frame_chrome()
        self._build_layout(title)

    # --------------------------
    # Construcción de UI
    # --------------------------

    def _init_frame_chrome(self) -> None:
        """Configura estilo visual del contenedor (fondo y QSS)."""
        self.setObjectName("SectionBase")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            f"""
            QFrame#SectionBase {{
                background-color: {SECTION_BG};
                border-radius: 10px;
            }}
            QLabel#SectionTitle {{
                color: {TEXT_PRIMARY};
                font-weight: 700;
                letter-spacing: 0.5px;
                background: transparent;
            }}
            QLabel {{ color: {TEXT_PRIMARY}; background: transparent; }}
            """
        )

    def _build_layout(self, title: str) -> None:
        """Crea el layout principal y agrega el título centrado."""
        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 14)
        self.layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(8)
