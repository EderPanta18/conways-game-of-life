# ui/main/view_ops.py

from PyQt6.QtCore import QTimer, Qt


def ensure_initial_focus(widget) -> None:
    """
    Transfiere foco cuando el event loop arranca, para evitar conflictos
    con el motivo de foco al crear la ventana.
    """
    widget.setFocusPolicy(widget.focusPolicy() or Qt.FocusPolicy.StrongFocus)
    QTimer.singleShot(
        0, lambda: widget.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
    )


def reset_view(board) -> None:
    """
    Resetea offsets y centra la vista; usa API pública cuando esté disponible.
    """
    board.vp.offset_x = 0.0
    board.vp.offset_y = 0.0
    board._recalc_and_center()  # TODO: exponer API pública en BoardWidget
