"""Patrón Command - interfaz ``Command`` (declara ejecutar/deshacer).

Rol en el patrón: encapsula una petición como objeto, de modo que el invoker
(``GestorPromociones``) pueda ejecutarla, guardarla y deshacerla sin conocer
al receptor.

Java vs Python:
- ``interface`` -> ``abc.ABC``. Las subclases concretas marcan sus métodos con
  ``typing.override``.
- ``getDescripcion()`` -> propiedad abstracta ``descripcion`` (``@property`` +
  ``@abstractmethod``): se lee como un atributo (``comando.descripcion``) y cada comando
  concreto está obligado a definirla.
- En Python un comando simple puede ser *cualquier callable* o un closure
  (``lambda: carrito.remover_descuento()``). Aquí mantenemos la clase porque
  necesitamos ``deshacer`` y una descripción, es decir, un comando con estado;
  para comandos sin undo un ``Callable[[], None]`` bastaría.
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """Command: contrato de toda operación ejecutable y reversible."""

    @abstractmethod
    def ejecutar(self) -> None:
        """Ejecuta la operación."""

    @abstractmethod
    def deshacer(self) -> None:
        """Revierte la operación."""

    @property
    @abstractmethod
    def descripcion(self) -> str:
        """Texto legible que describe el comando (para el historial)."""
