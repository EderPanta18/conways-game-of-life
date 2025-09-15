# ui/main/run_state.py

from PyQt6.QtCore import QTimer

from application.use_cases.game_controller import GameController
from ui.icons.icon_registry import icon


class RunStateBinder:
    """
    Sincroniza el estado de ejecución entre el controlador,
    el tablero y el panel de acciones.

    - Inicia/detiene la simulación con un QTimer.
    - Ajusta iconos de play/pausa y modo (mover/editar).
    - Deshabilita controles interactivos mientras corre.
    - Actualiza el cursor del tablero según el modo activo.
    """

    def __init__(
        self,
        controller: GameController,
        timer: QTimer,
        actions_panel,
        board,
        enable_controls_cb,
    ):
        self.controller = controller
        self.timer = timer
        self.actions_panel = actions_panel
        self.board = board
        self.enable_controls_cb = enable_controls_cb

    # -------------------------------------------------------------------------
    # Estado de ejecución
    # -------------------------------------------------------------------------

    def set_running(self, running: bool) -> None:
        self.controller.running = running
        self.actions_panel.setPlayIcon(icon("pause") if running else icon("play"))
        if running:
            self.controller.set_move_mode()
            self.actions_panel.setModeIcon(icon("move"))
            self.enable_controls_cb(False)
            self.timer.start()
        else:
            self.enable_controls_cb(True)
            self.timer.stop()
        self.board.update_cursor()

    # -------------------------------------------------------------------------
    # Modo (mover/editar)
    # -------------------------------------------------------------------------

    def toggle_mode(self) -> None:
        if self.controller.running:
            return
        if self.controller.mode == "move":
            self.controller.set_edit_mode()
        else:
            self.controller.set_move_mode()
        self.sync_mode_icon()
        self.board.update_cursor()

    def sync_mode_icon(self) -> None:
        self.actions_panel.setModeIcon(
            icon("move" if self.controller.mode == "move" else "edit")
        )
