# ui/widgets/coord_popover.py

from typing import Optional

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QGuiApplication


class CoordPopover(QWidget):
    """
    Ventana flotante ligera ("popover") que muestra coordenadas cerca del cursor.

    - Se renderiza como un bubble translúcido con sombra y bordes redondeados.
    - No roba foco ni intercepta eventos de ratón: es puramente informativo.
    - Se posiciona dinámicamente en pantalla para no salirse del área visible.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        # Flags de ventana
        flags = (
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        super().__init__(parent, flags)

        # Atributos de ventana
        self._configure_window_attributes()

        # Construcción de UI
        self._build_ui()

        # Estilos del bubble (QSS) y sombra
        self._apply_styles()
        self._apply_shadow()

    # -------------------------------------------------------------------------
    # Configuración de ventana
    # -------------------------------------------------------------------------

    def _configure_window_attributes(self) -> None:
        # Mostrar sin activar: no roba foco al aparecer
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        # Transparente para eventos de ratón: el puntero atraviesa el popover
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        # Fondo de ventana translúcido: permite dibujar solo el "bubble"
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # No acepta foco por teclado
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # -------------------------------------------------------------------------
    # Construcción de UI
    # -------------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Contenedor "bubble" con fondo sólido y bordes redondeados
        self._bubble = QWidget(self)
        self._bubble.setObjectName("Bubble")

        # Layout externo sin márgenes (la ventana pinta el fondo translúcido)
        lay_outer = QVBoxLayout(self)
        lay_outer.setContentsMargins(0, 0, 0, 0)
        lay_outer.addWidget(self._bubble)

        # Contenido interno con padding cómodo
        lay = QVBoxLayout(self._bubble)
        lay.setContentsMargins(14, 10, 14, 10)

        self.label = QLabel("", self._bubble)
        self.label.setObjectName("CoordLabel")
        lay.addWidget(self.label)

    # -------------------------------------------------------------------------
    # Estilo y efectos
    # -------------------------------------------------------------------------

    def _apply_styles(self) -> None:
        # Estilo del bubble y la etiqueta; el fondo de ventana queda translúcido
        self._bubble.setStyleSheet(
            """
            QWidget#Bubble { background-color: rgba(20,20,20,0.95); border-radius: 8px; }
            QLabel#CoordLabel { color: white; font-weight: 700; letter-spacing: 0.5px; }
            """
        )

    def _apply_shadow(self) -> None:
        # Sombra perimetral suave aplicada al bubble
        shadow = QGraphicsDropShadowEffect(self._bubble)
        shadow.setBlurRadius(18.0)
        shadow.setOffset(0.0, 3.0)
        shadow.setColor(Qt.GlobalColor.black)
        self._bubble.setGraphicsEffect(shadow)

    # -------------------------------------------------------------------------
    # API pública
    # -------------------------------------------------------------------------

    def show_at(self, global_pos: QPoint, col: int, row_bl: int) -> None:
        """
        Muestra el popover cerca del punto global indicado, ajustando a la
        pantalla para no salir del área disponible.
        """
        # Texto solicitado con etiquetas "x: .., y: .."
        self.label.setText(f"x: {col},  y: {row_bl}")
        # Ajustar tamaño al contenido antes de colocar
        self.adjustSize()

        # Offset pequeño para no tapar exactamente el cursor
        pos = global_pos + QPoint(12, 12)

        # Limitar a la geometría disponible de la pantalla bajo el punto
        screen = QGuiApplication.screenAt(pos)
        if screen:
            rect = screen.availableGeometry()
            x = min(pos.x(), rect.right() - self.width() - 2)
            y = min(pos.y(), rect.bottom() - self.height() - 2)
            pos = QPoint(int(max(rect.left() + 2, x)), int(max(rect.top() + 2, y)))

        self.move(pos)
        self.show()  # Ventana tipo Tool: aparece sin activar

    def hide_now(self) -> None:
        """Oculta el popover inmediatamente."""
        self.hide()
