# infrastructure/gui/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QFileDialog,
    QApplication,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence, QFont
from infrastructure.gui.board_widget import BoardWidget
from infrastructure.gui.panels.side_stack import SideStack
from infrastructure.gui.panels.config_panel import ConfigPanel
from infrastructure.gui.panels.actions_panel import ActionsPanel
from infrastructure.gui.panels.stats_panel import StatsPanel
from infrastructure.persistence.file_handler import save_template, load_template
from infrastructure.gui.icon_registry import icon
from infrastructure.gui.theme import APP_BG, PANEL_BG


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Juego de la Vida")
        self.setStyleSheet(f"background-color: {APP_BG};")
        self.setMinimumSize(1000, 800)
        self._apply_global_font()

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.board = BoardWidget(controller=self.controller)

        side_host = QWidget()
        side_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        side_host.setStyleSheet(f"background-color: {PANEL_BG};")
        side = SideStack()
        side_host.setLayout(side.v)

        self.config_panel = ConfigPanel()
        self.actions_panel = ActionsPanel()
        self.stats_panel = StatsPanel()

        side.v.addStretch(1)
        side.v.addWidget(self.config_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addWidget(self.actions_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addWidget(self.stats_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addStretch(1)

        root.addWidget(self.board, 9)
        root.addWidget(side_host, 1)

        # Conexiones
        self.config_panel.applySize.connect(self.on_apply_size)
        self.config_panel.zoomChanged.connect(self.on_zoom_from_panel)
        self.config_panel.gridToggled.connect(self.on_grid_toggled)  # NUEVO
        self.config_panel.resetRequested.connect(self.on_reset_defaults)  # NUEVO

        self.actions_panel.toggleRun.connect(self.on_toggle_run)
        self.actions_panel.toggleMode.connect(self.on_toggle_mode)
        self.actions_panel.randomize.connect(self.on_randomize)
        self.actions_panel.clearClicked.connect(self.on_clear)

        self.stats_panel.saveClicked.connect(self.on_save)
        self.stats_panel.loadClicked.connect(self.on_load)

        self.board.zoomChanged.connect(self.config_panel.setZoom)

        # Atajos (forma recomendada: crear y conectar señal activated)
        self._setup_shortcuts()
        self._ensure_initial_focus()

        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.on_tick)

        self._refresh_stats()

    def _apply_global_font(self):
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        QApplication.setFont(font)  # estático: evita problemas de tipado

    def _setup_shortcuts(self):
        self.sc_mode = QShortcut(QKeySequence(Qt.Key.Key_Q), self)
        self.sc_mode.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.sc_mode.setAutoRepeat(False)
        self.sc_mode.activated.connect(self.on_toggle_mode)

        self.sc_run_return = QShortcut(QKeySequence("Return"), self)
        self.sc_run_return.activated.connect(self.on_toggle_run)
        self.sc_run_enter = QShortcut(QKeySequence("Enter"), self)
        self.sc_run_enter.activated.connect(self.on_toggle_run)

    def _ensure_initial_focus(self):
        # Asegurar foco inicial en el tablero tras mostrarse la ventana
        self.board.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        QTimer.singleShot(
            0, lambda: self.board.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        )

    def on_grid_toggled(self, checked: bool):
        self.board.set_show_grid(bool(checked))

    def on_reset_defaults(self):
        # El panel ya envía applySize y zoomChanged; aquí solo aseguramos el estado visual
        self.board.set_show_grid(True)

    def _set_controls_enabled(self, enabled: bool):
        # Zoom queda siempre activo; tamaños se bloquean al ejecutar
        self.config_panel.setInteractiveEnabled(enabled)
        self.actions_panel.setInteractiveEnabled(enabled)
        self.stats_panel.setInteractiveEnabled(enabled)

    def on_toggle_run(self):
        self.controller.toggle_run()
        self.actions_panel.setPlayIcon(
            icon("pause") if self.controller.running else icon("play")
        )
        if self.controller.running:
            self.controller.set_move_mode()
            self.actions_panel.setModeIcon(icon("move"))
            self._set_controls_enabled(False)
            self.timer.start()
        else:
            self._set_controls_enabled(True)
            self.timer.stop()
        self.board.update_cursor()
        self._refresh_stats()

    def on_toggle_mode(self):
        if self.controller.running:
            return
        if self.controller.mode == "move":
            self.controller.set_edit_mode()
            self.actions_panel.setModeIcon(icon("edit"))
        else:
            self.controller.set_move_mode()
            self.actions_panel.setModeIcon(icon("move"))
        self.board.update_cursor()

    def on_randomize(self):
        self.controller.randomize(0.5)
        self._refresh_stats()
        self.board.update()

    def on_clear(self):
        self.controller.clear()
        self._refresh_stats()
        self.board.update()

    def on_apply_size(self, w: int, h: int):
        if self.controller.running:
            return
        self.controller.resize_grid(w, h, preserve=True)
        self.board.offset_x = 0.0
        self.board.offset_y = 0.0
        self.board._recalc_min_cell()
        self.board._ensure_min_zoom_and_center()
        self._refresh_stats()
        self.board.update()

    def on_zoom_from_panel(self, pct: int):
        self.board.set_zoom_percent(int(pct), anchor_to_cursor=False)

    def on_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar plantilla", filter="JSON (*.json)"
        )
        if path:
            save_template(self.controller.grid, path)

    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Cargar plantilla", filter="JSON (*.json)"
        )  # [9]
        if not path:
            return
        try:
            new_grid = load_template(
                path
            )  # puede lanzar (OSError/JSON/ValueError/TypeError) [7]
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al cargar plantilla",
                f"No se pudo cargar el archivo.\n\nDetalle:\n{e}",
                QMessageBox.StandardButton.Ok,
            )  # modal crítico, no cambia el estado actual [11][1]
            return

        # Solo aquí aplicar cambios porque la carga fue correcta
        self.controller.grid = new_grid
        self.board.offset_x = 0.0
        self.board.offset_y = 0.0
        self.controller.generation = 0
        self.board._recalc_min_cell()
        self.board._ensure_min_zoom_and_center()
        self._refresh_stats()
        self.board.update()

    def on_tick(self):
        if self.controller.running:
            self.controller.do_step()
            self._refresh_stats()
            self.board.update()

    def _refresh_stats(self):
        st = self.controller.stats()
        self.stats_panel.setStats(
            st["generation"], st["alive"], st["dead"], st["density"]
        )
