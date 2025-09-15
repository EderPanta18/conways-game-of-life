# ui/widgets/animated_button.py

from typing import Optional

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import (
    pyqtSignal,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
    Qt,
    QRectF,
    pyqtProperty,  # type: ignore
)
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap

from ui.theme import (
    BTN_BASE_BG,
    BTN_HOVER_BG,
    BTN_DISABLED_OPACITY,
    ICON_TINT_HOVER,
)


class AnimatedIconButton(QPushButton):
    """
    Botón personalizado con animación de fondo en hover e ícono centrado.

    - Interpola suavemente entre dos colores de fondo al entrar/salir del hover.
    - Aplica un tinte opcional al ícono cuando el hover está avanzado (>50%).
    - Expone una propiedad animable (`hoverProgress`) para controlar el estado visual.
    - Mantiene tamaño fijo y estilo consistente (sin foco, plano, cursor de mano).
    """

    hoverProgressChanged = pyqtSignal(float)

    def __init__(
        self,
        icon: QIcon,
        tooltip: str = "",
        radius: int = 12,
        parent: Optional[QPushButton] = None,
    ):
        super().__init__(parent)
        self._hoverProgress: float = 0.0
        self._base = QColor(BTN_BASE_BG)
        self._hover = QColor(BTN_HOVER_BG)
        self._radius = int(radius)

        self._setup_style(tooltip, icon)
        self._setup_animation()

    # ---------------------------------------------------------------------
    # Construcción de UI
    # ---------------------------------------------------------------------

    def _setup_style(self, tooltip: str, icon: QIcon) -> None:
        """Configura estilo y aspecto del botón."""
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setCheckable(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(44, 44)
        self.setIcon(icon)
        self.setIconSize(QSize(22, 22))

    def _setup_animation(self) -> None:
        """Crea y parametriza la animación de la propiedad hoverProgress."""
        self._anim = QPropertyAnimation(self, b"hoverProgress", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ---------------------------------------------------------------------
    # Eventos de entrada/salida (hover)
    # ---------------------------------------------------------------------

    def enterEvent(self, e):
        if not self.isEnabled():
            return
        self._anim.stop()
        self._anim.setStartValue(self._hoverProgress)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        if not self.isEnabled():
            return
        self._anim.stop()
        self._anim.setStartValue(self._hoverProgress)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(e)

    def setEnabled(self, enabled: bool) -> None:
        """Resetea el progreso y repinta al deshabilitar para evitar estados colgados."""
        super().setEnabled(enabled)
        if not enabled:
            self._hoverProgress = 0.0
        self.update()

    # ---------------------------------------------------------------------
    # Pintado
    # ---------------------------------------------------------------------

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        progress = self._hoverProgress if self.isEnabled() else 0.0
        self._paint_background(p, progress)
        self._paint_icon(p, progress)

        p.end()

    def _paint_background(self, p: QPainter, progress: float) -> None:
        """Pinta el fondo redondeado interpolando entre base y hover."""
        bg = self._lerp_color(self._base, self._hover, progress)
        if not self.isEnabled():
            p.setOpacity(BTN_DISABLED_OPACITY)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        rect = self.rect().adjusted(0, 0, -1, -1)
        p.drawRoundedRect(rect, self._radius, self._radius)

    def _paint_icon(self, p: QPainter, progress: float) -> None:
        """Pinta el icono centrado; aplica un tint en hover alto."""
        icon_sz = self.iconSize()
        dest = QRectF(
            (self.width() - icon_sz.width()) / 2.0,
            (self.height() - icon_sz.height()) / 2.0,
            float(icon_sz.width()),
            float(icon_sz.height()),
        )

        pm: QPixmap = self.icon().pixmap(icon_sz)
        if pm.isNull():
            return

        if progress > 0.5:
            pm = self._tint_pixmap(pm, QColor(ICON_TINT_HOVER))
            if pm.isNull():
                return

        src = QRectF(0.0, 0.0, float(pm.width()), float(pm.height()))
        p.drawPixmap(dest, pm, src)

    # ---------------------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------------------

    def _lerp_color(self, a: QColor, b: QColor, t: float) -> QColor:
        """Interpolación lineal de color por canal, t en [0..1]."""
        t = max(0.0, min(1.0, float(t)))
        r = a.red() + (b.red() - a.red()) * t
        g = a.green() + (b.green() - a.green()) * t
        b_ = a.blue() + (b.blue() - a.blue()) * t
        return QColor(int(r), int(g), int(b_))

    def _tint_pixmap(self, pm: QPixmap, color: QColor) -> QPixmap:
        """
        Aplica un tinte respetando el alfa del pixmap (SourceIn) y preserva DPR.
        """
        if pm.isNull() or pm.width() == 0 or pm.height() == 0:
            return pm

        tinted = QPixmap(pm.size())
        # Preservar DPR para nitidez en pantallas HiDPI
        try:
            tinted.setDevicePixelRatio(pm.devicePixelRatio())
        except Exception:
            pass

        tinted.fill(Qt.GlobalColor.transparent)
        qp = QPainter(tinted)
        qp.drawPixmap(0, 0, pm)
        qp.setCompositionMode(qp.CompositionMode.CompositionMode_SourceIn)
        qp.fillRect(tinted.rect(), color)
        qp.end()
        return tinted

    # ---------------------------------------------------------------------
    # Propiedad animable: hoverProgress
    # ---------------------------------------------------------------------

    def getHoverProgress(self) -> float:
        return self._hoverProgress

    def setHoverProgress(self, v: float):
        v = max(0.0, min(1.0, float(v)))
        if v != self._hoverProgress:
            self._hoverProgress = v
            self.hoverProgressChanged.emit(self._hoverProgress)
            self.update()

    hoverProgress = pyqtProperty(
        float, fget=getHoverProgress, fset=setHoverProgress, notify=hoverProgressChanged
    )
