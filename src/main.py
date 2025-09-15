# main.py

import sys
from PyQt6.QtWidgets import QApplication
from domain.entities.grid import Grid
from application.use_cases.game_controller import GameController
from infrastructure.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    grid = Grid(100, 100)
    controller = GameController(grid)
    win = MainWindow(controller)
    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
