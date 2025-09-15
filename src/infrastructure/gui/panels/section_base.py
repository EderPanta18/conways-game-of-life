# infrastructure/gui/panels/section_base.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from infrastructure.gui.theme import SECTION_BG, TEXT_PRIMARY


class SectionBase(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("SectionBase")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#SectionBase {{
                background-color: {SECTION_BG};
                border-radius: 10px;
            }}
            QLabel#SectionTitle {{
                color: {TEXT_PRIMARY};
                font-weight: 700;      /* negrita */
                letter-spacing: 0.5px;
                background: transparent;
            }}
            QLabel {{ color: {TEXT_PRIMARY}; background: transparent; }}
        """)
        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 14)
        self.layout.setSpacing(10)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(8)  # espacio extra bajo el título
