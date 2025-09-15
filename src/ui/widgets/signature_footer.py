# ui/widgets/signature_footer.py

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt

from ui.theme import TEXT_PRIMARY


class SignatureFooter(QWidget):
    """
    Firma del autor para mostrar en el pie de la barra lateral.

    - Renderizar una etiqueta centrada, sin fondo propio (hereda del padre).
    - Ofrecer una opacidad sutil para no competir visualmente con los paneles.

    Notas:
    - Este widget está pensado para usarse como overlay (fuera de layout) y
      anclarse con move() desde el contenedor (SideStack).
    """

    def __init__(
        self, text: str = "Desarrollado", parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._opacity_value: float = 0.65  # opacidad por defecto

        self._build_ui(text)
        self._apply_style()

    # ---------------------------------------------------------------------
    # Construcción de UI
    # ---------------------------------------------------------------------

    def _build_ui(self, text: str) -> None:
        """Crea la etiqueta y el layout simple centrado."""
        # Contenedor sin fondo para heredar el del padre
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setStyleSheet("background: transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 6, 0, 6)
        lay.setSpacing(0)

        self._label = QLabel(text, self)
        self._label.setObjectName("SignatureFooterLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Opacidad sutil mediante efecto gráfico
        self._opacity_effect = QGraphicsOpacityEffect(self._label)
        self._opacity_effect.setOpacity(self._opacity_value)
        self._label.setGraphicsEffect(self._opacity_effect)

        lay.addWidget(self._label, 1, Qt.AlignmentFlag.AlignHCenter)

    def _apply_style(self) -> None:
        """Aplica el estilo del texto de la firma."""
        self._label.setStyleSheet(
            f"""
            QLabel#SignatureFooterLabel {{
                color: {TEXT_PRIMARY};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
            """
        )

    # ---------------------------------------------------------------------
    # API pública
    # ---------------------------------------------------------------------

    def setText(self, text: str) -> None:
        """Actualiza el texto visible de la firma."""
        self._label.setText(text)
        self.updateGeometry()
