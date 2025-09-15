# ui/panels/side_stack.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtCore import Qt


class SideStack(QWidget):
    """
    Contenedor vertical para paneles laterales.

    Expone un layout público (`v`) y ajusta el espaciado
    dinámicamente según el alto del widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Parámetros visuales
        self._margin_x = 12
        self._margin_y = 18
        self._base_spacing = 24
        self._spacing_ratio = 0.12  # ~12% de la altura
        self._spacing_divisor = 2  # mantiene el comportamiento original

        # Overlay de pie de página (footer) fuera del layout
        self._footer = None
        self._footer_margin = 5  # separación desde el borde inferior

        # Parámetros responsivos (no afectan si hay mucha altura)
        self._min_spacing = 5  # espaciado mínimo al comprimir
        self._h_min = 480  # altura donde inicia compresión
        self._h_max = 900  # altura donde termina compresión

        # Construcción de UI
        self._build_layout()

    # --------------------------
    # Construcción de UI
    # --------------------------

    def _build_layout(self) -> None:
        """Crea el layout vertical con márgenes y espaciado inicial."""
        self.v = QVBoxLayout(self)
        self.v.setContentsMargins(
            self._margin_x, self._margin_y, self._margin_x, self._margin_y
        )
        self.v.setSpacing(self._base_spacing)

    # --------------------------
    # Overlay (footer “absolute”)
    # --------------------------

    def set_footer(self, footer: QWidget, bottom_margin: int = 7) -> None:
        """
        Ancla un widget como footer superpuesto, centrado en X y pegado al borde inferior.
        El footer no participa del layout: se posiciona con move() y se eleva con raise_().
        """
        if footer.parent() is not self:
            footer.setParent(self)
        footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        footer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        footer.setStyleSheet("background: transparent;")
        self._footer = footer
        self._footer_margin = int(bottom_margin)
        footer.resize(footer.sizeHint())
        self._position_footer()
        footer.show()

    def _position_footer(self) -> None:
        """Calcula y aplica la posición del footer como overlay “bottom: 0” centrado en X."""
        if not self._footer:
            return
        w = self._footer.width() or self._footer.sizeHint().width()
        h = self._footer.height() or self._footer.sizeHint().height()
        x = max(0, (self.width() - w) // 2)
        y = max(0, self.height() - h - self._footer_margin)
        self._footer.move(int(x), int(y))
        self._footer.raise_()

    # --------------------------
    # Eventos
    # --------------------------

    def resizeEvent(self, e: QResizeEvent) -> None:
        """
        Ajusta el espaciado vertical en función de la altura del contenedor.

        Regla:
        Espaciado = max(espaciado_base, int(altura * ratio / divisor))
        """
        height_px = max(1, self.height())
        dynamic_spacing = max(
            self._base_spacing,
            int(height_px * self._spacing_ratio / self._spacing_divisor),
        )
        self.v.setSpacing(dynamic_spacing)

        # NUEVO: compresión responsiva para alturas bajas (sin eliminar la regla original)
        # Factor t en [0..1] entre h_min y h_max; a menor altura, menor spacing.
        if height_px <= self._h_min:
            t = 0.0
        elif height_px >= self._h_max:
            t = 1.0
        else:
            t = (height_px - self._h_min) / float(self._h_max - self._h_min)

        responsive_spacing = int(
            round(self._min_spacing + (self._base_spacing - self._min_spacing) * t)
        )
        final_spacing = int(min(dynamic_spacing, responsive_spacing * 0.9))
        self.v.setSpacing(final_spacing)

        # Reposicionar overlay “bottom: 0” al cambiar tamaño
        self._position_footer()

        super().resizeEvent(e)
