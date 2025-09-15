# ui/panels/config_panel.py

from typing import Optional

from PyQt6.QtWidgets import QWidget, QGridLayout, QSpinBox, QLabel, QSlider, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt

from config.settings import DEFAULT_WIDTH, DEFAULT_HEIGHT, ZOOM_MIN, ZOOM_MAX
from domain.entities.grid import MIN_SIZE, MAX_SIZE
from ui.icons.icon_registry import icon
from ui.widgets.animated_button import AnimatedIconButton
from .section_base import SectionBase


class ConfigPanel(SectionBase):
    """
    Panel de configuración.

    - Permite ajustar las dimensiones de la grilla mediante spinners numéricos.
    - Controla el nivel de zoom con un deslizador horizontal.
    - Ofrece botones para mostrar/ocultar la rejilla y restablecer valores por defecto.
    - Emite señales al aplicar cambios o al modificar zoom/toggles.
    - Restaura automáticamente los valores iniciales cuando se solicita un reset.
    """

    applySize = pyqtSignal(int, int)
    zoomChanged = pyqtSignal(int)
    gridToggled = pyqtSignal(bool)
    resetRequested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Configuración", parent)

        # Construcción de UI
        self._build_size_row()
        self.layout.addSpacing(8)
        self._build_zoom_row()
        self.layout.addSpacing(8)
        self._build_toggle_row()

        # Señales
        self._connect_signals()

    # -------------------------------------------------------------------------
    # Construcción de UI
    # -------------------------------------------------------------------------

    def _build_size_row(self) -> None:
        size_row = QWidget()
        size_row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        size_row.setStyleSheet("background: transparent;")
        size_grid = QGridLayout(size_row)
        size_grid.setContentsMargins(0, 0, 0, 0)
        size_grid.setHorizontalSpacing(8)
        size_grid.setVerticalSpacing(6)

        self.spin_w = QSpinBox()
        self.spin_h = QSpinBox()
        for spinner in (self.spin_w, self.spin_h):
            spinner.setRange(MIN_SIZE, MAX_SIZE)
            spinner.setValue(
                DEFAULT_WIDTH if spinner is self.spin_w else DEFAULT_HEIGHT
            )
            spinner.setSingleStep(10)
            spinner.setAlignment(Qt.AlignmentFlag.AlignRight)

        size_grid.addWidget(
            QLabel("Ancho:"),
            0,
            0,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        size_grid.addWidget(self.spin_w, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        size_grid.addWidget(
            QLabel("Alto:"),
            1,
            0,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        size_grid.addWidget(self.spin_h, 1, 1, Qt.AlignmentFlag.AlignVCenter)

        self.btn_apply = AnimatedIconButton(
            icon("resize"), "Aplicar dimensiones (Ancho/Alto)"
        )
        size_grid.addWidget(
            self.btn_apply,
            0,
            2,
            2,
            1,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )
        size_grid.setColumnStretch(1, 1)
        size_grid.setColumnStretch(2, 0)

        self.layout.addWidget(size_row)

    def _build_zoom_row(self) -> None:
        zoom_row = QWidget()
        zoom_row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        zoom_row.setStyleSheet("background: transparent;")
        zoom_layout = QHBoxLayout(zoom_row)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(8)

        zoom_label = QLabel("Zoom:")
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(ZOOM_MIN, ZOOM_MAX)
        self.slider_zoom.setPageStep(50)
        self.slider_zoom.setSingleStep(10)
        self.slider_zoom.setValue(100)

        zoom_layout.addWidget(zoom_label, 0, Qt.AlignmentFlag.AlignVCenter)
        zoom_layout.addWidget(self.slider_zoom, 1)

        self.layout.addWidget(zoom_row)

    def _build_toggle_row(self) -> None:
        toggles_row = QWidget()
        toggles_row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        toggles_row.setStyleSheet("background: transparent;")
        toggles_layout = QHBoxLayout(toggles_row)
        toggles_layout.setContentsMargins(0, 0, 0, 0)
        toggles_layout.setSpacing(10)

        toggles_row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        toggles_row.setStyleSheet("background: transparent;")

        self.btn_grid = AnimatedIconButton(icon("grid"), "Mostrar bordes de casilla")
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)

        self.btn_reset = AnimatedIconButton(
            icon("reset"), "Restablecer configuración por defecto"
        )

        toggles_layout.addStretch(1)
        toggles_layout.addWidget(self.btn_grid, 0, Qt.AlignmentFlag.AlignHCenter)
        toggles_layout.addWidget(self.btn_reset, 0, Qt.AlignmentFlag.AlignHCenter)
        toggles_layout.addStretch(1)

        self.layout.addWidget(toggles_row)

    # -------------------------------------------------------------------------
    # Señales
    # -------------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self.btn_apply.clicked.connect(self._on_apply_clicked)
        self.spin_w.editingFinished.connect(self._on_apply_clicked)
        self.spin_h.editingFinished.connect(self._on_apply_clicked)
        self.slider_zoom.valueChanged.connect(self._on_zoom_changed)
        self.btn_grid.toggled.connect(self.gridToggled.emit)
        self.btn_reset.clicked.connect(self._on_reset_clicked)

    # -------------------------------------------------------------------------
    # Slots internos
    # -------------------------------------------------------------------------

    def _on_apply_clicked(self) -> None:
        self.applySize.emit(int(self.spin_w.value()), int(self.spin_h.value()))

    def _on_zoom_changed(self, value: int) -> None:
        self.zoomChanged.emit(int(value))

    def _on_reset_clicked(self) -> None:
        self.spin_w.setValue(DEFAULT_WIDTH)
        self.spin_h.setValue(DEFAULT_HEIGHT)

        if self.slider_zoom.value() != 100:
            self.slider_zoom.blockSignals(True)
            self.slider_zoom.setValue(100)
            self.slider_zoom.blockSignals(False)

        if not self.btn_grid.isChecked():
            self.btn_grid.setChecked(True)
            self.gridToggled.emit(True)

        self._on_apply_clicked()
        self.zoomChanged.emit(100)
        self.resetRequested.emit()

    # -------------------------------------------------------------------------
    # API pública
    # -------------------------------------------------------------------------

    def setZoom(self, pct: int) -> None:
        if pct != self.slider_zoom.value():
            self.slider_zoom.blockSignals(True)
            self.slider_zoom.setValue(int(pct))
            self.slider_zoom.blockSignals(False)

    def setInteractiveEnabled(self, enabled: bool) -> None:
        self.spin_w.setEnabled(enabled)
        self.spin_h.setEnabled(enabled)
        self.btn_apply.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        # El zoom y el toggle de rejilla permanecen activos incluso en ejecución.
