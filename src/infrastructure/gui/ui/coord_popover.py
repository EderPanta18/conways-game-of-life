# infrastructure/gui/ui/coord_popover.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QGuiApplication


class CoordPopover(QWidget):
    def __init__(self, parent=None):
        flags = (
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        super().__init__(parent, flags)
        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating, True
        )  # no roba foco [7]
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )  # no consume eventos [2]
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )  # fondo de ventana transparente [2]
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Bubble interno con fondo sólido y bordes redondeados
        self._bubble = QWidget(self)
        self._bubble.setObjectName("Bubble")
        lay_outer = QVBoxLayout(self)
        lay_outer.setContentsMargins(0, 0, 0, 0)
        lay_outer.addWidget(self._bubble)

        lay = QVBoxLayout(self._bubble)
        lay.setContentsMargins(14, 10, 14, 10)  # padding interno más cómodo
        self.label = QLabel("", self._bubble)
        self.label.setObjectName("CoordLabel")
        lay.addWidget(self.label)

        # Estilo del bubble
        self._bubble.setStyleSheet("""
            QWidget#Bubble { background-color: rgba(20,20,20,0.95); border-radius: 8px; }
            QLabel#CoordLabel { color: white; font-weight: 700; letter-spacing: 0.5px; }
        """)  # border-radius y color sólidos con QSS [5][6]

        # Sombra aplicada al bubble
        shadow = QGraphicsDropShadowEffect(self._bubble)
        shadow.setBlurRadius(18.0)
        shadow.setOffset(0.0, 3.0)
        shadow.setColor(Qt.GlobalColor.black)
        self._bubble.setGraphicsEffect(shadow)  # sombra sin halo rectangular [4]

    def show_at(self, global_pos: QPoint, col: int, row_bl: int):
        self.label.setText(
            f"x: {col},  y: {row_bl}"
        )  # texto solicitado con etiquetas [5]
        self.adjustSize()
        pos = global_pos + QPoint(12, 12)
        screen = QGuiApplication.screenAt(pos)
        if screen:
            rect = screen.availableGeometry()
            x = min(pos.x(), rect.right() - self.width() - 2)
            y = min(pos.y(), rect.bottom() - self.height() - 2)
            pos = QPoint(int(max(rect.left() + 2, x)), int(max(rect.top() + 2, y)))
        self.move(pos)
        self.show()  # ventana tipo Tool, sin activar [3][7]

    def hide_now(self):
        self.hide()  # ocultar cuando salga del tablero [2]
