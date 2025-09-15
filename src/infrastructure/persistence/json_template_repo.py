# infrastructure/persistence/json_template_repo.py

import numpy as np
import json

from typing import Any, Sequence, TypedDict, NotRequired, cast

from domain.entities.grid import Grid, MIN_SIZE, MAX_SIZE
from domain.entities.cell import Cell
from application.ports.template_repo import TemplateRepository


class TemplateTD(TypedDict, total=False):
    """Esquema esperado del archivo de plantilla."""

    width: int
    height: int
    alive: NotRequired[list[Sequence[int]]]  # lista de pares [x, y]


class JsonTemplateRepository(TemplateRepository):
    """Repositorio de plantillas en formato JSON."""

    def save(self, grid: Grid, path: str) -> None:
        ys, xs = np.where(grid.cells == 1)
        data: TemplateTD = {
            "width": int(grid.width),
            "height": int(grid.height),
            "alive": [[int(x), int(y)] for x, y in zip(xs, ys)],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path: str) -> Grid:
        with open(path, "r", encoding="utf-8") as f:
            data_raw: Any = json.load(f)

        # Validación mínima de esquema
        if (
            not isinstance(data_raw, dict)
            or "width" not in data_raw
            or "height" not in data_raw
        ):
            raise ValueError("Plantilla inválida -> faltan 'width'/'height'.")

        # Conversión segura a int
        try:
            width = int(data_raw["width"])
            height = int(data_raw["height"])
        except (TypeError, ValueError):
            raise ValueError("Plantilla inválida -> 'width'/'height' no son enteros.")

        # Límites del dominio
        if not (MIN_SIZE <= width <= MAX_SIZE and MIN_SIZE <= height <= MAX_SIZE):
            raise ValueError(f"Tamaño fuera de límites [{MIN_SIZE}..{MAX_SIZE}].")

        g = Grid(width, height)

        # Celdas vivas: lista de secuencias [x, y]; descartar items inválidos
        alive_raw: Any = data_raw.get("alive", [])
        if isinstance(alive_raw, list):
            for item_any in alive_raw:
                item = cast(Sequence[Any], item_any)
                if len(item) >= 2:
                    try:
                        x = int(item[0])
                        y = int(item[1])
                    except (TypeError, ValueError):
                        continue
                    if 0 <= x < g.width and 0 <= y < g.height:
                        g.set_cell(Cell(x, y, True))

        return g
