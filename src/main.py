# main.py

import sys

from PyQt6.QtWidgets import QApplication

from config.settings import DEFAULT_WIDTH, DEFAULT_HEIGHT
from domain.entities.grid import Grid
from application.use_cases.game_controller import GameController
from application.resources import install_search_paths
from infrastructure.persistence.json_template_repo import JsonTemplateRepository
from ui.main_window import MainWindow


def create_app() -> QApplication:
    """
    Configura y devuelve la aplicación Qt.
    """
    return QApplication(sys.argv)


def create_controller() -> GameController:
    """
    Construye la grilla y el controlador principal del juego.
    """
    grid = Grid(DEFAULT_WIDTH, DEFAULT_HEIGHT)
    return GameController(grid)


def create_main_window(controller: GameController) -> MainWindow:
    """
    Instancia la ventana principal con sus dependencias.
    """
    template_repo = JsonTemplateRepository()
    return MainWindow(controller, template_repo)


def main() -> None:
    """
    Orquesta la inicialización completa:
    - Crea la app Qt.
    - Configura el controlador y ventana principal.
    - Lanza el bucle de eventos.
    """
    app = create_app()
    install_search_paths()
    controller = create_controller()
    win = create_main_window(controller)

    win.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
