# infrastructure/gui/board_widget.py

from typing import Any, cast
import numpy as np
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QImage
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from infrastructure.gui.theme import ALIVE, BOARD_BG, GRID_LINE
from infrastructure.gui.ui.coord_popover import CoordPopover


class BoardWidget(QWidget):
    zoomChanged = pyqtSignal(int)  # porcentaje de zoom

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setMouseTracking(True)
        self._last_tooltip_cell = (-1, -1)
        self._popover = CoordPopover(self)  # ventana flotante no bloqueante [1]
        self._popover.hide()
        self.base_cell_size = 12  # 100%
        self.min_pct = 50  # min 50%
        self.max_pct = 1000  # max 1000%
        self.show_grid = True  # NUEVO: bordes de casilla visibles por defecto
        self.cell_size = self.base_cell_size
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._dragging = False
        self._last_pos = QPoint()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setStyleSheet(f"background-color: {BOARD_BG};")
        self._recalc_min_cell()
        self._ensure_min_zoom_and_center()
        self._emit_zoom()
        self.update_cursor()

    # ---- cursores por modo ----
    def update_cursor(self):
        if self.controller.mode == "move":
            self.setCursor(
                Qt.CursorShape.OpenHandCursor
                if not self._dragging
                else Qt.CursorShape.ClosedHandCursor
            )
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

    # ---- límites dinámicos de zoom ----
    def _recalc_min_cell(self):
        g = self.controller.grid
        if not g or g.width == 0 or g.height == 0:
            self._min_cell_dynamic = 1
            return
        need_w = math.ceil(self.width() / max(1, g.width))
        need_h = math.ceil(self.height() / max(1, g.height))
        dyn = max(need_w, need_h)
        min_nominal = max(1, int(self.base_cell_size * self.min_pct / 100))
        max_nominal = max(1, int(self.base_cell_size * self.max_pct / 100))
        self._min_cell_dynamic = max(min_nominal, min(dyn, max_nominal))

    def _ensure_min_zoom_and_center(self):
        g = self.controller.grid
        if not g:
            return
        max_nominal = max(1, int(self.base_cell_size * self.max_pct / 100))
        self.cell_size = max(self._min_cell_dynamic, min(self.cell_size, max_nominal))
        self._clamp_offsets(center_if_smaller=True)
        self._emit_zoom()

    # ---- API pública ----
    def set_zoom_percent(self, pct: int, anchor_to_cursor: bool = False):
        pct = max(self.min_pct, min(self.max_pct, int(pct)))
        new_size = int(round(self.base_cell_size * pct / 100))
        if new_size == self.cell_size:
            self._emit_zoom()
            return
        if anchor_to_cursor:
            cx = self.mapFromGlobal(self.cursor().pos()).x()
            cy = self.mapFromGlobal(self.cursor().pos()).y()
        else:
            cx = self.width() // 2
            cy = self.height() // 2
        old = self.cell_size
        world_x = self.offset_x + cx
        world_y = self.offset_y + cy
        self.cell_size = new_size
        fx = world_x / max(1, old)
        fy = world_y / max(1, old)
        self.offset_x = fx * self.cell_size - cx
        self.offset_y = fy * self.cell_size - cy
        self._recalc_min_cell()
        self._ensure_min_zoom_and_center()
        self.update(self.rect())

    def set_show_grid(self, show: bool):
        self.show_grid = bool(show)
        self.update(self.rect())

    # ---- eventos ----
    def resizeEvent(self, event):
        self._recalc_min_cell()
        self._ensure_min_zoom_and_center()
        super().resizeEvent(event)

    def paintEvent(self, event):
        g = self.controller.grid
        if g is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

        p.fillRect(event.rect(), QColor(BOARD_BG))

        board_w_px = g.width * self.cell_size
        board_h_px = g.height * self.cell_size
        board_rect = QRect(
            int(-self.offset_x), int(-self.offset_y), int(board_w_px), int(board_h_px)
        )

        clip = event.region().boundingRect().intersected(board_rect)
        if clip.isEmpty():
            p.end()
            return

        left_w = self.offset_x + clip.left()
        right_w = self.offset_x + clip.right()
        top_w = self.offset_y + clip.top()
        bottom_w = self.offset_y + clip.bottom()

        start_col = max(0, int(left_w // self.cell_size))
        end_col = min(g.width, int(math.ceil((right_w + 1) / self.cell_size)))
        start_row = max(0, int(top_w // self.cell_size))
        end_row = min(g.height, int(math.ceil((bottom_w + 1) / self.cell_size)))
        if start_col >= end_col or start_row >= end_row:
            p.end()
            return

        cs = self.cell_size
        ox, oy = self.offset_x, self.offset_y

        # Raster celdas (igual que ya tienes)
        img_w, img_h = clip.width(), clip.height()
        image = QImage(img_w, img_h, QImage.Format.Format_RGB32)
        bg_qrgb = QColor(BOARD_BG).rgb()
        alive_qrgb = QColor(ALIVE).rgb()
        image.fill(bg_qrgb)

        sub = g.cells[start_row:end_row, start_col:end_col]
        if sub.size:
            ys, xs = (sub == 1).nonzero()
            if xs.size:
                bpl = image.bytesPerLine()
                bits = image.bits()
                assert bits is not None
                bits.setsize(bpl * img_h)
                mv = memoryview(cast(Any, bits))
                arr8 = np.frombuffer(mv, dtype=np.uint8).reshape((img_h, bpl))
                arr32 = arr8.view(np.uint32).reshape((img_h, bpl // 4))
                for y, x in zip(ys, xs):
                    vx = int((start_col + x) * cs - ox) - clip.left()
                    vy = int((start_row + y) * cs - oy) - clip.top()
                    bx0 = max(0, vx)
                    by0 = max(0, vy)
                    bx1 = min(img_w, vx + cs)
                    by1 = min(img_h, vy + cs)
                    if bx0 >= bx1 or by0 >= by1:
                        continue
                    arr32[by0:by1, bx0:bx1] = alive_qrgb

        # 1) Blit de celdas
        p.drawImage(clip.topLeft(), image)

        # 2) Grilla como bordes (encima) con 1 px exacto
        if self.show_grid and cs >= 6:
            p.save()
            p.setClipRect(clip)
            pen = QPen(QColor(GRID_LINE))
            pen.setCosmetic(True)  # 1 px fijo en pantalla
            pen.setWidth(0)  # 0 => cosmético (1 px)
            p.setPen(pen)
            # verticales en coordenadas enteras
            for c in range(start_col, end_col + 1):
                x = int(c * cs - ox)
                if x < clip.left() or x > clip.right():
                    continue
                p.drawLine(x, clip.top(), x, clip.bottom())
            # horizontales en coordenadas enteras
            for r in range(start_row, end_row + 1):
                y = int(r * cs - oy)
                if y < clip.top() or y > clip.bottom():
                    continue
                p.drawLine(clip.left(), y, clip.right(), y)
            p.restore()

        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.controller.mode == "move":
                self._dragging = True
                self.update_cursor()
                self._last_pos = event.position().toPoint()
            elif self.controller.mode == "edit" and not self.controller.running:
                self._toggle_cell_at(event.position().toPoint())
        self._update_coord_popover(
            event.position().toPoint()
        )  # persistente al presionar [4]
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.controller.mode == "move" and self._dragging:
            pos = event.position().toPoint()
            dx = pos.x() - self._last_pos.x()
            dy = pos.y() - self._last_pos.y()
            self._last_pos = pos
            self._pan(-dx, -dy)
            self.update(self.rect())
        self._update_coord_popover(
            event.position().toPoint()
        )  # sigue durante drag/zoom/click [4]
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.update_cursor()
        self._update_coord_popover(
            event.position().toPoint()
        )  # persistente al soltar [4]
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        old = self.cell_size
        mp = event.position()
        world_x = self.offset_x + mp.x()
        world_y = self.offset_y + mp.y()
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 1 / 1.1

        self._recalc_min_cell()
        max_nominal = max(1, int(self.base_cell_size * self.max_pct / 100))
        new_size = int(round(self.cell_size * factor))
        new_size = max(self._min_cell_dynamic, min(new_size, max_nominal))
        if new_size == self.cell_size:
            return

        self.cell_size = new_size
        fx = world_x / max(1, old)
        fy = world_y / max(1, old)
        self.offset_x = fx * self.cell_size - mp.x()
        self.offset_y = fy * self.cell_size - mp.y()
        self._clamp_offsets(center_if_smaller=True)
        self._emit_zoom()
        self.update(self.rect())
        self._update_coord_popover(
            event.position().toPoint()
        )  # no desaparece con zoom [4]
        super().wheelEvent(event)

    def leaveEvent(self, event):
        self._popover.hide_now()
        self._last_tooltip_cell = (-1, -1)  # ocultar al salir [4]
        super().leaveEvent(event)

    # ---- utilidades ----
    def _emit_zoom(self):
        pct = int(round(self.cell_size / self.base_cell_size * 100))
        pct = max(self.min_pct, min(self.max_pct, pct))
        self.zoomChanged.emit(pct)

    def _pan(self, dx_px: float, dy_px: float):
        self.offset_x += dx_px
        self.offset_y += dy_px
        self._clamp_offsets(center_if_smaller=True)

    def _clamp_offsets(self, center_if_smaller: bool):
        g = self.controller.grid
        board_w = g.width * self.cell_size
        board_h = g.height * self.cell_size
        if board_w <= self.width():
            self.offset_x = (
                -(self.width() - board_w) / 2.0 if center_if_smaller else 0.0
            )
        else:
            max_x = board_w - self.width()
            self.offset_x = max(0.0, min(self.offset_x, float(max_x)))
        if board_h <= self.height():
            self.offset_y = (
                -(self.height() - board_h) / 2.0 if center_if_smaller else 0.0
            )
        else:
            max_y = board_h - self.height()
            self.offset_y = max(0.0, min(self.offset_y, float(max_y)))

    def _toggle_cell_at(self, p: QPoint):
        g = self.controller.grid
        col = int((self.offset_x + p.x()) // self.cell_size)
        row = int((self.offset_y + p.y()) // self.cell_size)
        if 0 <= col < g.width and 0 <= row < g.height:
            g.toggle_cell(col, row)
            # Invalida sólo la celda en pantalla
            vx = int(col * self.cell_size - self.offset_x)
            vy = int(row * self.cell_size - self.offset_y)
            self.update(QRect(vx, vy, self.cell_size, self.cell_size))

    def _cell_under_pos(self, pos: QPoint):
        g = self.controller.grid
        if not g:
            return (-1, -1, False)
        col = int((self.offset_x + pos.x()) // self.cell_size)
        row_top = int((self.offset_y + pos.y()) // self.cell_size)
        inside = 0 <= col < g.width and 0 <= row_top < g.height
        return (col, row_top, inside)

    def _update_coord_popover(self, pos: QPoint):
        g = self.controller.grid
        if not g:
            self._popover.hide_now()
            self._last_tooltip_cell = (-1, -1)
            return  # [4]
        col, row_top, inside = self._cell_under_pos(pos)
        if not inside:
            if self._popover.isVisible():
                self._popover.hide_now()
                self._last_tooltip_cell = (-1, -1)  # [4]
            return
        row_bl = g.height - 1 - row_top  # origen abajo-izquierda [21]
        if (col, row_bl) != self._last_tooltip_cell:
            self._last_tooltip_cell = (col, row_bl)
        # Mostrar o actualizar posición cerca del cursor (coordenadas globales)
        self._popover.show_at(
            self.mapToGlobal(pos), col, row_bl
        )  # texto "x: .., y: .." [14]
