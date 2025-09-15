# ui/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QApplication,
    QMessageBox,
)

from PyQt6.QtCore import Qt, QTimer, QSignalBlocker
from PyQt6.QtGui import QFont

from application.use_cases.game_controller import GameController
from application.ports.template_repo import TemplateRepository
from ui.icons.icon_registry import icon
from ui.board.board_widget import BoardWidget
from ui.panels.side_stack import SideStack
from ui.panels.config_panel import ConfigPanel
from ui.panels.actions_panel import ActionsPanel
from ui.panels.stats_panel import StatsPanel
from ui.panels.templates_panel import TemplatesPanel
from ui.widgets.signature_footer import SignatureFooter
from ui.main.run_state import RunStateBinder
from ui.main.dialogs import ask_save_json, ask_open_json
from ui.main.shortcuts import install_main_shortcuts
from ui.main.view_ops import ensure_initial_focus, reset_view
from .theme import APP_BG, PANEL_BG


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.

    - Aloja el tablero central (BoardWidget) y una barra lateral con paneles.
    - Gestiona la interacción entre controlador, paneles y vista del tablero.
    - Encapsula atajos, menús y persistencia de plantillas.
    - Maneja el ciclo de ejecución con un QTimer y sincroniza estadísticas.
    """

    def __init__(self, controller: GameController, template_repo: TemplateRepository):
        super().__init__()
        self.controller = controller
        self.template_repo = template_repo

        # Cromado y fuente global
        self._init_window_chrome()
        self._apply_global_font()

        # Raíz y barra lateral
        central, root = self._build_central()
        self.setCentralWidget(central)

        self.board = BoardWidget(controller=self.controller)
        side = self._build_side()

        root.addWidget(self.board, 9)
        root.addWidget(side, 1)

        # Paneles laterales
        self.config_panel = ConfigPanel()
        self.actions_panel = ActionsPanel()
        self.stats_panel = StatsPanel()
        self.templates_panel = TemplatesPanel()

        side.v.addStretch(1)
        side.v.addWidget(self.config_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addWidget(self.actions_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addWidget(self.stats_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addWidget(self.templates_panel, 0, Qt.AlignmentFlag.AlignHCenter)
        side.v.addStretch(1)

        # Firma como overlay anclado abajo (no altera distribución de paneles)
        self.signature_footer = SignatureFooter("Desarrollado por EdeRev")
        side.set_footer(self.signature_footer, bottom_margin=5)

        # Señales de paneles
        self._connect_signals()

        # Atajos y foco inicial
        self.shortcuts = install_main_shortcuts(
            self, on_toggle_run=self.on_toggle_run, on_toggle_mode=self.on_toggle_mode
        )
        ensure_initial_focus(self.board)

        # Timer y binder de estado de ejecución
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.on_tick)

        self.run_binder = RunStateBinder(
            controller=self.controller,
            timer=self.timer,
            actions_panel=self.actions_panel,
            board=self.board,
            enable_controls_cb=self._set_controls_enabled,
        )

        # Primera pintura de estadísticas
        self._refresh_stats()

    # -------------------------------------------------------------------------
    # Construcción de UI
    # -------------------------------------------------------------------------

    def _init_window_chrome(self) -> None:
        """Configura título, fondo y tamaño mínimo de la ventana."""
        self.setWindowTitle("Juego de la Vida")
        self.setWindowIcon(icon("logo"))
        self.setStyleSheet(f"background-color: {APP_BG};")
        self.setMinimumSize(1000, 700)

    def _build_central(self) -> tuple[QWidget, QHBoxLayout]:
        """Crea el central widget y su layout raíz horizontal."""
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        return central, root

    def _build_side(self) -> SideStack:
        """Crea el contenedor lateral (SideStack) con su propio fondo."""
        side = SideStack()
        side.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        side.setStyleSheet(f"background-color: {PANEL_BG};")
        return side

    def _connect_signals(self) -> None:
        """Conecta señales de paneles y sincroniza tablero ↔ panel config."""
        # Config
        self.config_panel.applySize.connect(self.on_apply_size)
        self.config_panel.zoomChanged.connect(self.on_zoom_from_panel)
        self.config_panel.gridToggled.connect(self.on_grid_toggled)
        self.config_panel.resetRequested.connect(self.on_reset_defaults)
        # Actions
        self.actions_panel.toggleRun.connect(self.on_toggle_run)
        self.actions_panel.toggleMode.connect(self.on_toggle_mode)
        self.actions_panel.randomize.connect(self.on_randomize)
        self.actions_panel.clearClicked.connect(self.on_clear)
        # Templates
        self.templates_panel.saveClicked.connect(self.on_save)
        self.templates_panel.loadClicked.connect(self.on_load)
        # Board ↔ Config
        self.board.zoomChanged.connect(self.config_panel.setZoom)

    # -------------------------------------------------------------------------
    # Global UI
    # -------------------------------------------------------------------------

    def _apply_global_font(self) -> None:
        """Aplica la fuente global de la aplicación."""
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        QApplication.setFont(font)

    def _set_controls_enabled(self, enabled: bool) -> None:
        """Habilita/inhabilita paneles interactivos según el estado de ejecución."""
        self.config_panel.setInteractiveEnabled(enabled)
        self.actions_panel.setInteractiveEnabled(enabled)
        self.templates_panel.setInteractiveEnabled(enabled)

    # -------------------------------------------------------------------------
    # Acciones
    # -------------------------------------------------------------------------

    def on_toggle_run(self) -> None:
        self.run_binder.set_running(not self.controller.running)
        self._refresh_stats()

    def on_toggle_mode(self) -> None:
        self.run_binder.toggle_mode()

    def on_randomize(self) -> None:
        self.controller.randomize(0.5)
        self._refresh_stats()
        self.board.update()

    def on_clear(self) -> None:
        self.controller.clear()
        self._refresh_stats()
        self.board.update()

    def on_apply_size(self, w: int, h: int) -> None:
        if self.controller.running:
            return
        self.controller.resize_grid(w, h, preserve=True)
        reset_view(self.board)
        self._refresh_stats()
        self.board.update()

    def on_zoom_from_panel(self, pct: int) -> None:
        self.board.set_zoom_percent(int(pct), anchor_to_cursor=False)

    # -------------------------------------------------------------------------
    # Panel config
    # -------------------------------------------------------------------------

    def on_grid_toggled(self, checked: bool) -> None:
        self.board.set_show_grid(bool(checked))

    def on_reset_defaults(self) -> None:
        self.board.set_show_grid(True)

    # -------------------------------------------------------------------------
    # Persistencia (diálogos JSON)
    # -------------------------------------------------------------------------

    def on_save(self) -> None:
        path = ask_save_json(self, "Guardar plantilla")
        if not path:
            return
        try:
            self.template_repo.save(self.controller.grid, path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al guardar plantilla",
                f"No se pudo guardar el archivo.\n\nDetalle:\n{e}",
                QMessageBox.StandardButton.Ok,
            )

    def on_load(self) -> None:
        path = ask_open_json(self, "Cargar plantilla")
        if not path:
            return
        try:
            new_grid = self.template_repo.load(path)

            with (
                QSignalBlocker(self.config_panel.spin_w),
                QSignalBlocker(self.config_panel.spin_h),
            ):
                self.config_panel.spin_w.setValue(
                    new_grid.width
                )  # usa setters del widget [2]
                self.config_panel.spin_h.setValue(new_grid.height)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al cargar plantilla",
                f"No se pudo cargar el archivo.\n\nDetalle:\n{e}",
                QMessageBox.StandardButton.Ok,
            )
            return
        self.controller.grid = new_grid
        self.controller.generation = 0
        reset_view(self.board)
        self._refresh_stats()
        self.board.update()

    # -------------------------------------------------------------------------
    # Ticking (timer)
    # -------------------------------------------------------------------------

    def on_tick(self) -> None:
        """Itera la simulación cuando está en ejecución y refresca UI."""
        if self.controller.running:
            self.controller.do_step()
            self._refresh_stats()
            self.board.update()

    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------

    def _refresh_stats(self) -> None:
        """Obtiene métricas del controlador y las refleja en el panel."""
        st = self.controller.stats()
        self.stats_panel.set_stats_data(st)
