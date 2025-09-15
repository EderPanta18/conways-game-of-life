# infrastructure/gui/panels/side_stack.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout


class SideStack(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.v = QVBoxLayout(self)
        self.v.setContentsMargins(12, 18, 12, 18)  # menos margen en X
        self.v.setSpacing(24)  # separación base mayor

    def resizeEvent(self, e):
        h = max(1, self.height())
        self.v.setSpacing(max(24, int(h * 0.12 / 2)))  # ~12% vertical
        super().resizeEvent(e)
