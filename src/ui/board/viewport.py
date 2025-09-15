# ui/board/viewport.py

import math

from dataclasses import dataclass

from PyQt6.QtCore import QRect, QPoint, QSize

from config.settings import BASE_CELL_PX, ZOOM_MIN, ZOOM_MAX


@dataclass
class Viewport:
    """
    Gestiona el área visible (viewport) del tablero en la UI.

    - Controla el zoom (tamaño de las celdas en pantalla).
    - Maneja los desplazamientos (offsets).
    - Calcula qué parte de la grilla es visible según el tamaño del widget.
    """

    base_cell_size: int = BASE_CELL_PX  # Tamaño base de una celda (en píxeles)
    min_pct: int = ZOOM_MIN  # Zoom mínimo (en %)
    max_pct: int = ZOOM_MAX  # Zoom máximo (en %)
    cell_size: int = BASE_CELL_PX  # Tamaño actual de celda
    offset_x: float = 0.0  # Desplazamiento horizontal en píxeles
    offset_y: float = 0.0  # Desplazamiento vertical en píxeles
    _min_cell_dynamic: int = 1  # Tamaño dinámico mínimo de celda calculado

    # --------------------------
    # Zoom
    # --------------------------

    def zoom_percent(self) -> int:
        """Devuelve el zoom actual en porcentaje."""
        pct = int(round(self.cell_size / max(1, self.base_cell_size) * 100))
        return max(self.min_pct, min(self.max_pct, pct))

    def recalc_min_cell(self, widget_size: QSize, grid_w: int, grid_h: int) -> None:
        """
        Recalcula el tamaño mínimo dinámico de celda,
        asegurando que todo el tablero pueda caber en pantalla.
        """
        if grid_w <= 0 or grid_h <= 0:
            self._min_cell_dynamic = 1
            return

        # Tamaño de celda necesario para que todo el tablero entre en el widget
        need_w = math.ceil(widget_size.width() / max(1, grid_w))
        need_h = math.ceil(widget_size.height() / max(1, grid_h))
        dyn = max(need_w, need_h)

        # Ajuste entre zoom nominal mínimo y máximo
        min_nominal = max(1, int(self.base_cell_size * self.min_pct / 100))
        max_nominal = max(1, int(self.base_cell_size * self.max_pct / 100))
        self._min_cell_dynamic = max(min_nominal, min(dyn, max_nominal))

    def ensure_min_zoom_and_center(
        self, widget_size: QSize, grid_w: int, grid_h: int
    ) -> None:
        """
        Asegura que el zoom no sea menor al permitido dinámicamente
        y centra el tablero si es más pequeño que el widget.
        """
        max_nominal = max(1, int(self.base_cell_size * self.max_pct / 100))
        self.cell_size = max(self._min_cell_dynamic, min(self.cell_size, max_nominal))
        self.clamp_offsets(widget_size, grid_w, grid_h, center_if_smaller=True)

    def set_zoom_percent(
        self, pct: int, anchor_px: QPoint | None, widget_size: QSize
    ) -> bool:
        """
        Ajusta el zoom al porcentaje `pct`.
        El punto `anchor_px` sirve como ancla (centro del zoom).
        Retorna True si hubo cambio real de zoom.
        """
        pct = max(self.min_pct, min(self.max_pct, int(pct)))
        new_size = int(round(self.base_cell_size * pct / 100))
        if new_size == self.cell_size:
            return False

        # Centro de referencia (por defecto, el centro del widget)
        if anchor_px is None:
            cx = widget_size.width() // 2
            cy = widget_size.height() // 2
        else:
            cx, cy = anchor_px.x(), anchor_px.y()

        old = self.cell_size
        # Convertir a coordenadas del "mundo"
        world_x = self.offset_x + cx
        world_y = self.offset_y + cy

        # Cambiar tamaño de celda
        self.cell_size = new_size

        # Ajustar offsets para mantener el punto ancla fijo en pantalla
        fx = world_x / max(1, old)
        fy = world_y / max(1, old)
        self.offset_x = fx * self.cell_size - cx
        self.offset_y = fy * self.cell_size - cy
        return True

    # --------------------------
    # Cálculo de áreas visibles
    # --------------------------

    def board_rect(self, grid_w: int, grid_h: int) -> QRect:
        """Rectángulo (en px) que ocupa el tablero completo en la pantalla."""
        return QRect(
            int(-self.offset_x),
            int(-self.offset_y),
            int(grid_w * self.cell_size),
            int(grid_h * self.cell_size),
        )

    def visible_range(
        self, clip: QRect, grid_w: int, grid_h: int
    ) -> tuple[int, int, int, int] | None:
        """
        Devuelve el rango visible de celdas dentro del área `clip`.
        Retorna (col_inicio, col_fin, fila_inicio, fila_fin) o None si nada es visible.
        """
        if clip.isEmpty():
            return None

        # Convertir coordenadas de clip a "mundo"
        left_w = self.offset_x + clip.left()
        right_w = self.offset_x + clip.right()
        top_w = self.offset_y + clip.top()
        bottom_w = self.offset_y + clip.bottom()

        # Calcular columnas y filas visibles
        start_col = max(0, int(left_w // self.cell_size))
        end_col = min(grid_w, int(math.ceil((right_w + 1) / self.cell_size)))
        start_row = max(0, int(top_w // self.cell_size))
        end_row = min(grid_h, int(math.ceil((bottom_w + 1) / self.cell_size)))

        if start_col >= end_col or start_row >= end_row:
            return None
        return start_col, end_col, start_row, end_row

    def cell_under_pos(
        self, pos: QPoint, grid_w: int, grid_h: int
    ) -> tuple[int, int, bool]:
        """
        Devuelve (col, fila, dentro_tablero) de la celda bajo la posición de pantalla `pos`.
        """
        col = int((self.offset_x + pos.x()) // self.cell_size)
        row_top = int((self.offset_y + pos.y()) // self.cell_size)
        inside = 0 <= col < grid_w and 0 <= row_top < grid_h
        return col, row_top, inside

    # --------------------------
    # Desplazamiento
    # --------------------------

    def pan(
        self, dx_px: float, dy_px: float, widget_size: QSize, grid_w: int, grid_h: int
    ) -> None:
        """Desplaza el tablero en píxeles (dx, dy)."""
        self.offset_x += dx_px
        self.offset_y += dy_px
        self.clamp_offsets(widget_size, grid_w, grid_h, center_if_smaller=True)

    def clamp_offsets(
        self, widget_size: QSize, grid_w: int, grid_h: int, *, center_if_smaller: bool
    ) -> None:
        """
        Limita los offsets para que el tablero no se salga de los bordes.
        Si el tablero es más pequeño que el widget, puede centrarse.
        """
        board_w = grid_w * self.cell_size
        board_h = grid_h * self.cell_size

        # Restricción horizontal
        if board_w <= widget_size.width():
            self.offset_x = (
                (-(widget_size.width() - board_w) / 2.0) if center_if_smaller else 0.0
            )
        else:
            max_x = board_w - widget_size.width()
            self.offset_x = max(0.0, min(self.offset_x, float(max_x)))

        # Restricción vertical
        if board_h <= widget_size.height():
            self.offset_y = (
                (-(widget_size.height() - board_h) / 2.0) if center_if_smaller else 0.0
            )
        else:
            max_y = board_h - widget_size.height()
            self.offset_y = max(0.0, min(self.offset_y, float(max_y)))
