# ui/icons/icon_registry.py

from PyQt6.QtGui import QIcon

ICONS_DIR = "assets/icons"


def icon(name: str) -> QIcon:
    """Devuelve un QIcon .svg o .png."""
    ic = QIcon(f"icons:{name}.svg")
    if not ic.isNull():
        return ic
    return QIcon(f"icons:{name}.png")
