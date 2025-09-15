# application/resources.py

import sys
from pathlib import Path
from PyQt6.QtCore import QDir


def _root():
    # Carpeta raíz de recursos: PyInstaller o proyecto
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))


def install_search_paths():
    root = _root()
    # Alias para buscar iconos y otros assets en la app
    QDir.setSearchPaths("icons", [str(root / "assets" / "icons")])
