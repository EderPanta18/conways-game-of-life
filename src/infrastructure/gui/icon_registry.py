# infrastructure/gui/icon_registry.py

from PyQt6.QtGui import QIcon

ICONS_DIR = "assets/icons"


def icon(name: str) -> QIcon:
    """
    Retorna un QIcon desde assets/icons/<name>.svg o .png.
    """
    svg = f"{ICONS_DIR}/{name}.svg"
    if QIcon(svg) and not QIcon(svg).isNull():
        return QIcon(svg)

    png = f"{ICONS_DIR}/{name}.png"
    return QIcon(png)
