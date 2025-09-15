# ui/main/shortcuts.py

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence


def install_main_shortcuts(
    parent,
    *,
    on_toggle_run: Callable[[], None],
    on_toggle_mode: Callable[[], None],
) -> dict[str, QShortcut]:
    """
    Crea atajos y los retorna en un dict para posible gestión posterior.
    """

    def _shortcut(keys: str | QKeySequence, slot) -> QShortcut:
        sc = QShortcut(QKeySequence(keys) if isinstance(keys, str) else keys, parent)
        sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
        sc.setAutoRepeat(False)
        sc.activated.connect(slot)
        return sc

    shortcuts = {
        "mode": _shortcut("Q", on_toggle_mode),
        "run_return": _shortcut("Return", on_toggle_run),
        "run_enter": _shortcut("Enter", on_toggle_run),
    }
    return shortcuts
