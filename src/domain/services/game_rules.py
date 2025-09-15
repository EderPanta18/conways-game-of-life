# domain/services/game_rules.py

import numpy as np

NEIGHBOR_OFFSETS = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]


def step(cells: np.ndarray) -> np.ndarray:
    """Siguiente generación con bordes sin wrap (fuera=muerto)."""
    h, w = cells.shape
    pad = np.pad(cells, 1, mode="constant", constant_values=0)
    nbrs = np.zeros_like(cells, dtype=np.uint8)
    for dx, dy in NEIGHBOR_OFFSETS:
        nbrs += pad[1 + dy : 1 + dy + h, 1 + dx : 1 + dx + w]
    next_cells = ((nbrs == 3) | ((cells == 1) & (nbrs == 2))).astype(np.uint8)
    return next_cells
