# ui/board/board_widget.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal

from ui.theme import BOARD_BG
from ui.widgets.coord_popover import CoordPopover
from .viewport import Viewport
from .grid_painter import GridPainter


class BoardWidget(QWidget):
    """
    Widget del tablero principal.

    - Renderiza la grilla, maneja zoom/pan.
    - Permite editar celdas y muestra coordenadas del mouse.
    """

    zoomChanged = pyqtSignal(int)  # Emite cuando cambia el zoom (en %)

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setMouseTracking(True)

        # Estado visual y renderizado
        self.vp = Viewport()
        self.painter = GridPainter(self.vp)

        # Popover con coordenadas del mouse
        self._last_tooltip_cell = (-1, -1)
        self._popover = CoordPopover(self)
        self._popover.hide()

        # Flags de vista y estilos de fondo
        self.show_grid = True
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setStyleSheet(f"background-color: {BOARD_BG};")

        # Estado de interacción
        self._dragging = False
        self._last_pos = QPoint()
        self._recalc_and_center()
        self._emit_zoom()
        self.update_cursor()

    # --------------------------
    # Cursores según modo
    # --------------------------

    def update_cursor(self):
        if self.controller.mode == "move":
            self.setCursor(
                Qt.CursorShape.OpenHandCursor
                if not self._dragging
                else Qt.CursorShape.ClosedHandCursor
            )
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

    # --------------------------
    # Utilidades internas
    # --------------------------

    def _recalc_and_center(self):
        """Recalcula el tamaño mínimo de celda y centra la vista."""
        g = self.controller.grid
        if not g:
            return
        self.vp.recalc_min_cell(self.size(), g.width, g.height)
        self.vp.ensure_min_zoom_and_center(self.size(), g.width, g.height)

    def _emit_zoom(self):
        """Emite la señal con el zoom actual (%)."""
        self.zoomChanged.emit(self.vp.zoom_percent())

    # --------------------------
    # API pública
    # --------------------------

    def set_zoom_percent(self, pct: int, anchor_to_cursor: bool = False):
        """Cambia el zoom con opción de anclar al cursor."""
        anchor = self.mapFromGlobal(self.cursor().pos()) if anchor_to_cursor else None
        changed = self.vp.set_zoom_percent(pct, anchor, self.size())
        if changed:
            self._recalc_and_center()
            self.update(self.rect())
        self._emit_zoom()

    def set_show_grid(self, show: bool):
        """Muestra u oculta la rejilla de fondo."""
        self.show_grid = bool(show)
        self.update(self.rect())

    # --------------------------
    # Eventos Qt
    # --------------------------

    def resizeEvent(self, event):
        self._recalc_and_center()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Dibuja el tablero y la rejilla."""
        g = self.controller.grid
        if g is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        p.fillRect(event.rect(), QColor(BOARD_BG))
        self.painter.paint(p, event.region().boundingRect(), g.cells, self.show_grid)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.controller.mode == "move":
                # Inicia arrastre (pan)
                self._dragging = True
                self.update_cursor()
                self._last_pos = event.position().toPoint()
            elif self.controller.mode == "edit" and not self.controller.running:
                # Alterna celda en modo edición
                self._toggle_cell_at(event.position().toPoint())
        self._update_coord_popover(event.position().toPoint())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.controller.mode == "move" and self._dragging:
            # Pan del tablero
            pos = event.position().toPoint()
            dx, dy = pos.x() - self._last_pos.x(), pos.y() - self._last_pos.y()
            self._last_pos = pos
            g = self.controller.grid
            self.vp.pan(-dx, -dy, self.size(), g.width, g.height)
            self.update(self.rect())
        self._update_coord_popover(event.position().toPoint())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.update_cursor()
        self._update_coord_popover(event.position().toPoint())
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Zoom con la rueda del mouse."""
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 1 / 1.1
        pct = int(round(self.vp.zoom_percent() * factor))
        self.set_zoom_percent(pct, anchor_to_cursor=True)
        self._update_coord_popover(event.position().toPoint())
        super().wheelEvent(event)

    def leaveEvent(self, event):
        self._popover.hide_now()
        self._last_tooltip_cell = (-1, -1)
        super().leaveEvent(event)

    # --------------------------
    # Utilidades
    # --------------------------

    def _toggle_cell_at(self, p: QPoint):
        """Activa/desactiva una celda en coordenadas de tablero."""
        g = self.controller.grid
        col = int((self.vp.offset_x + p.x()) // self.vp.cell_size)
        row = int((self.vp.offset_y + p.y()) // self.vp.cell_size)
        if 0 <= col < g.width and 0 <= row < g.height:
            g.toggle_cell(col, row)
            vx = int(col * self.vp.cell_size - self.vp.offset_x)
            vy = int(row * self.vp.cell_size - self.vp.offset_y)
            self.update(QRect(vx, vy, self.vp.cell_size, self.vp.cell_size))

    def _cell_under_pos(self, pos: QPoint):
        g = self.controller.grid
        return self.vp.cell_under_pos(pos, g.width, g.height)

    def _update_coord_popover(self, pos: QPoint):
        """Muestra/oculta el popover de coordenadas según el mouse."""
        g = self.controller.grid
        if not g:
            self._popover.hide_now()
            self._last_tooltip_cell = (-1, -1)
            return
        col, row_top, inside = self._cell_under_pos(pos)
        if not inside:
            if self._popover.isVisible():
                self._popover.hide_now()
                self._last_tooltip_cell = (-1, -1)
            return
        row_bl = g.height - 1 - row_top
        if (col, row_bl) != self._last_tooltip_cell:
            self._last_tooltip_cell = (col, row_bl)
        self._popover.show_at(self.mapToGlobal(pos), col, row_bl)
