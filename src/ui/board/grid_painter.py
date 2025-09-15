# ui/board/grid_painter.py

import numpy as np
import numpy.typing as npt

from typing import Any, cast

from PyQt6.QtGui import QPainter, QColor, QPen, QImage
from PyQt6.QtCore import QRect

from ui.theme import ALIVE, BOARD_BG, GRID_LINE
from .viewport import Viewport


class GridPainter:
    """
    Renderiza el tablero del Juego de la Vida en el widget.

    - Usa el Viewport para calcular el área visible.
    - Pinta fondo, celdas vivas y opcionalmente la rejilla.
    """

    def __init__(self, viewport: Viewport):
        self.vp = viewport  # Referencia al viewport (zoom, offset, etc.)

    def paint(
        self,
        p: QPainter,  # Pincel de Qt
        update_rect: QRect,  # Región a repintar (clip)
        cells: npt.NDArray[np.uint8],  # Matriz de celdas (0=muerta, 1=viva)
        show_grid: bool,  # Mostrar rejilla sí/no
    ) -> None:
        # Tipado explícito del shape para Pylance
        h, w = cast(tuple[int, int], tuple(cells.shape[:2]))

        # Área del tablero en pantalla
        board_rect = self.vp.board_rect(w, h)
        # Intersección con el área que realmente necesita repintado
        clip = update_rect.intersected(board_rect)
        if clip.isEmpty():
            return  # Nada que pintar

        cs = self.vp.cell_size
        ox, oy = self.vp.offset_x, self.vp.offset_y

        # --------------------------
        # Crear raster temporal (QImage) para pintar
        # --------------------------

        img_w, img_h = clip.width(), clip.height()
        image = QImage(img_w, img_h, QImage.Format.Format_RGB32)

        # Colores preconvertidos a QRgb
        bg_qrgb = QColor(BOARD_BG).rgb()
        alive_qrgb = QColor(ALIVE).rgb()

        # Llenar el fondo
        image.fill(bg_qrgb)

        # --------------------------
        # Pintar celdas vivas
        # --------------------------

        rng = self.vp.visible_range(clip, w, h)
        if rng is not None:
            start_col, end_col, start_row, end_row = rng
            # Submatriz de celdas visibles
            sub = cells[start_row:end_row, start_col:end_col]
            if sub.size:
                # Coordenadas relativas donde hay celdas vivas
                ys, xs = (sub == 1).nonzero()
                if xs.size:
                    # Acceso directo a los píxeles del QImage
                    bpl = image.bytesPerLine()
                    bits = image.bits()
                    assert bits is not None
                    bits.setsize(bpl * img_h)
                    mv = memoryview(cast(Any, bits))
                    arr8 = np.frombuffer(mv, dtype=np.uint8).reshape((img_h, bpl))
                    arr32 = arr8.view(np.uint32).reshape((img_h, bpl // 4))

                    # Rellenar rectángulos correspondientes a las celdas vivas
                    for y, x in zip(ys, xs):
                        vx = int((start_col + x) * cs - ox) - clip.left()
                        vy = int((start_row + y) * cs - oy) - clip.top()
                        bx0 = max(0, vx)
                        by0 = max(0, vy)
                        bx1 = min(img_w, vx + cs)
                        by1 = min(img_h, vy + cs)
                        if bx0 < bx1 and by0 < by1:
                            arr32[by0:by1, bx0:bx1] = alive_qrgb

        # --------------------------
        # Blit: copiar la imagen temporal al widget
        # --------------------------

        p.drawImage(clip.topLeft(), image)

        # --------------------------
        # Dibujar rejilla cosmética (líneas finas)
        # --------------------------

        if show_grid and cs >= 6 and rng is not None:
            start_col, end_col, start_row, end_row = rng
            p.save()
            p.setClipRect(clip)

            # Configurar pluma para líneas de 1 px (independientes del zoom)
            pen = QPen(QColor(GRID_LINE))
            pen.setCosmetic(True)
            pen.setWidth(0)  # "0" con cosmético => siempre 1 px
            p.setPen(pen)

            # Líneas verticales
            for c in range(start_col, end_col + 1):
                x = int(c * cs - ox)
                if clip.left() <= x <= clip.right():
                    p.drawLine(x, clip.top(), x, clip.bottom())

            # Líneas horizontales
            for r in range(start_row, end_row + 1):
                y = int(r * cs - oy)
                if clip.top() <= y <= clip.bottom():
                    p.drawLine(clip.left(), y, clip.right(), y)

            p.restore()
