# infrastructure/persistence/file_handler.py

import json
import numpy as np
from domain.entities.grid import Grid, MIN_SIZE, MAX_SIZE
from domain.entities.cell import Cell


def save_template(grid: Grid, filepath: str):
    ys, xs = np.where(grid.cells == 1)
    data = {
        "width": int(grid.width),
        "height": int(grid.height),
        "alive": [[int(x), int(y)] for x, y in zip(xs, ys)],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _as_int(v):
    return int(v)  # deja que ValueError/TypeError suban si no es convertible [13]


def load_template(filepath: str) -> Grid:
    # 1) Leer JSON (puede lanzar OSError/JSONDecodeError)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)  # [21]

    # 2) Validar claves y tipos
    if not isinstance(data, dict) or "width" not in data or "height" not in data:
        raise ValueError("Plantilla inválida -> faltan 'width'/'height'.")  # [7]

    width = _as_int(data["width"])
    height = _as_int(data["height"])
    if not (MIN_SIZE <= width <= MAX_SIZE and MIN_SIZE <= height <= MAX_SIZE):
        raise ValueError(f"Tamaño fuera de límites [{MIN_SIZE}..{MAX_SIZE}].")  # [7]

    g = Grid(width, height)

    # 3) Cargar celdas vivas; ignorar pares inválidos
    alive = data.get("alive", [])
    if isinstance(alive, list):
        for item in alive:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                try:
                    x = _as_int(item)
                    y = _as_int(item[22])
                except Exception:
                    continue  # descarta par no convertible [13]
                if 0 <= x < g.width and 0 <= y < g.height:
                    g.set_cell(Cell(x, y, True))
    return g
