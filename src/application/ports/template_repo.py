# application/ports/template_repo.py

from abc import ABC, abstractmethod

from domain.entities.grid import Grid


class TemplateRepository(ABC):
    """Puerto de persistencia de plantillas (interfaz agnóstica de infraestructura)."""

    @abstractmethod
    def save(self, grid: Grid, path: str) -> None: ...

    @abstractmethod
    def load(self, path: str) -> Grid: ...
