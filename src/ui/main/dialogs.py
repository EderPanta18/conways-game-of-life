# ui/main/dialogs.py

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QFileDialog


def ask_save_json(parent: QWidget, title: str = "Guardar plantilla") -> str:
    """
    Abre un diálogo de guardado y garantiza extensión .json si falta.
    Devuelve ruta (str) o cadena vacía si se cancela.
    """
    path, _ = QFileDialog.getSaveFileName(parent, title, filter="JSON (*.json)")
    if not path:
        return ""
    p = Path(path)
    if p.suffix.lower() != ".json":
        p = p.with_suffix(".json")
    return str(p)


def ask_open_json(parent: QWidget, title: str = "Cargar plantilla") -> str:
    """
    Abre un diálogo de apertura con filtro JSON.
    Devuelve ruta (str) o cadena vacía si se cancela.
    """
    path, _ = QFileDialog.getOpenFileName(parent, title, filter="JSON (*.json)")
    return path or ""
