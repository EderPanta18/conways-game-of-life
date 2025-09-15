# infrastructure/gui/panels/config_panel.py

from PyQt6.QtWidgets import QWidget, QGridLayout, QSpinBox, QLabel, QSlider, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from infrastructure.gui.panels.section_base import SectionBase
from infrastructure.gui.icon_registry import icon
from infrastructure.gui.ui.animated_button import AnimatedIconButton
from domain.entities.grid import MIN_SIZE, MAX_SIZE

DEFAULT_W = 100
DEFAULT_H = 100
DEFAULT_ZOOM = 100


class ConfigPanel(SectionBase):
    applySize = pyqtSignal(int, int)
    zoomChanged = pyqtSignal(int)
    gridToggled = pyqtSignal(bool)
    resetRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Configuración", parent)

        # --- Dimensiones (grid) + aplicar ---
        top_row = QWidget()
        grid = QGridLayout(top_row)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        self.spin_w = QSpinBox()
        self.spin_h = QSpinBox()
        for sp in (self.spin_w, self.spin_h):
            sp.setRange(MIN_SIZE, MAX_SIZE)
            sp.setValue(DEFAULT_W if sp is self.spin_w else DEFAULT_H)
            sp.setSingleStep(10)
            sp.setAlignment(Qt.AlignmentFlag.AlignRight)

        grid.addWidget(
            QLabel("Ancho:"),
            0,
            0,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        grid.addWidget(self.spin_w, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(
            QLabel("Alto:"),
            1,
            0,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        grid.addWidget(self.spin_h, 1, 1, Qt.AlignmentFlag.AlignVCenter)

        self.btn_apply = AnimatedIconButton(
            icon("resize"), "Aplicar dimensiones (Ancho/Alto)"
        )
        grid.addWidget(
            self.btn_apply,
            0,
            2,
            2,
            1,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)

        # --- Zoom ---
        zoom_row = QWidget()
        zoom_l = QHBoxLayout(zoom_row)
        zoom_l.setContentsMargins(0, 0, 0, 0)
        zoom_l.setSpacing(8)
        zoom_label = QLabel("Zoom:")
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(50, 1000)
        self.slider_zoom.setPageStep(50)
        self.slider_zoom.setSingleStep(10)
        self.slider_zoom.setValue(DEFAULT_ZOOM)
        zoom_l.addWidget(zoom_label, 0, Qt.AlignmentFlag.AlignVCenter)
        zoom_l.addWidget(self.slider_zoom, 1)

        # --- Botones: Mostrar bordes (toggle) + Restablecer ---
        toggles_row = QWidget()
        toggles_l = QHBoxLayout(toggles_row)
        toggles_l.setContentsMargins(0, 0, 0, 0)
        toggles_l.setSpacing(10)

        toggles_row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        toggles_row.setStyleSheet("background: transparent;")

        self.btn_grid = AnimatedIconButton(icon("grid"), "Mostrar bordes de casilla")
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)

        self.btn_reset = AnimatedIconButton(
            icon("reset"), "Restablecer configuración por defecto"
        )

        toggles_l.addStretch(1)
        toggles_l.addWidget(self.btn_grid, 0, Qt.AlignmentFlag.AlignHCenter)
        toggles_l.addWidget(self.btn_reset, 0, Qt.AlignmentFlag.AlignHCenter)
        toggles_l.addStretch(1)

        # --- Ensamble usando self.vbox (heredado y tipado en SectionBase) ---
        self.layout.addWidget(top_row)
        self.layout.addSpacing(8)
        self.layout.addWidget(zoom_row)
        self.layout.addSpacing(8)
        self.layout.addWidget(toggles_row)

        # Señales
        self.btn_apply.clicked.connect(self._emit_apply)
        self.spin_w.editingFinished.connect(self._emit_apply)
        self.spin_h.editingFinished.connect(self._emit_apply)
        self.slider_zoom.valueChanged.connect(lambda v: self.zoomChanged.emit(int(v)))
        self.btn_grid.toggled.connect(self.gridToggled.emit)
        self.btn_reset.clicked.connect(self._on_reset_clicked)

    def _emit_apply(self):
        self.applySize.emit(int(self.spin_w.value()), int(self.spin_h.value()))

    def _on_reset_clicked(self):
        self.spin_w.setValue(DEFAULT_W)
        self.spin_h.setValue(DEFAULT_H)
        if self.slider_zoom.value() != DEFAULT_ZOOM:
            self.slider_zoom.blockSignals(True)
            self.slider_zoom.setValue(DEFAULT_ZOOM)
            self.slider_zoom.blockSignals(False)
        if not self.btn_grid.isChecked():
            self.btn_grid.setChecked(True)
            self.gridToggled.emit(True)
        self._emit_apply()
        self.zoomChanged.emit(DEFAULT_ZOOM)
        self.resetRequested.emit()

    def setZoom(self, pct: int):
        if pct != self.slider_zoom.value():
            self.slider_zoom.blockSignals(True)
            self.slider_zoom.setValue(int(pct))
            self.slider_zoom.blockSignals(False)

    def setInteractiveEnabled(self, enabled: bool):
        self.spin_w.setEnabled(enabled)
        self.spin_h.setEnabled(enabled)
        self.btn_apply.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        # el zoom y los toggles permanecen activos incluso en ejecución
