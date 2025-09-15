# infrastructure/gui/ui/animated_button.py

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
from infrastructure.gui.theme import (
    BTN_BASE_BG,
    BTN_HOVER_BG,
    BTN_DISABLED_OPACITY,
    ICON_TINT_HOVER,
)


class AnimatedIconButton(QPushButton):
    hoverProgressChanged = pyqtSignal(float)

    def __init__(self, icon: QIcon, tooltip: str = "", radius=12, parent=None):
        super().__init__(parent)
        self._hoverProgress = 0.0
        self._base = QColor(BTN_BASE_BG)
        self._hover = QColor(BTN_HOVER_BG)
        self._radius = radius
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setCheckable(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(44, 44)
        self.setIcon(icon)
        self.setIconSize(QSize(22, 22))
        self._anim = QPropertyAnimation(self, b"hoverProgress", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

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
        super().setEnabled(enabled)
        if not enabled:
            self._hoverProgress = 0.0
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        progress = self._hoverProgress if self.isEnabled() else 0.0

        # Fondo animado (igual)
        r = self._base.red() + (self._hover.red() - self._base.red()) * progress
        g = self._base.green() + (self._hover.green() - self._base.green()) * progress
        b = self._base.blue() + (self._hover.blue() - self._base.blue()) * progress
        bg = QColor(int(r), int(g), int(b))
        if not self.isEnabled():
            p.setOpacity(BTN_DISABLED_OPACITY)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        rect = self.rect().adjusted(0, 0, -1, -1)
        p.drawRoundedRect(rect, self._radius, self._radius)

        # Icono: rect destino fijo según iconSize(), centrado
        icon_sz = self.iconSize()
        dest = QRectF(
            (self.width() - icon_sz.width()) / 2.0,
            (self.height() - icon_sz.height()) / 2.0,
            float(icon_sz.width()),
            float(icon_sz.height()),
        )

        pm: QPixmap = self.icon().pixmap(icon_sz)  # pixmap al tamaño lógico solicitado
        if pm.isNull():
            p.end()
            return

        if progress > 0.5:
            pm = self._tint_pixmap(pm, QColor(ICON_TINT_HOVER))
            if pm.isNull():
                p.end()
                return

        # Fuente completa del pixmap
        src = QRectF(0.0, 0.0, float(pm.width()), float(pm.height()))
        p.drawPixmap(dest, pm, src)
        p.end()

    def _tint_pixmap(self, pm: QPixmap, color: QColor) -> QPixmap:
        if pm.isNull() or pm.width() == 0 or pm.height() == 0:
            return pm
        tinted = QPixmap(pm.size())
        # preservar DPR para evitar reescalados en HiDPI
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
