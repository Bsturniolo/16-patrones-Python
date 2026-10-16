"""Patrón Observer - interfaz ``Observer``.

Rol GoF: *Observer*. Define el contrato que deben cumplir quienes quieren ser
notificados por el sujeto observable (``Tienda``).

Java vs Python:
- En Java es una ``interface``. Aquí usamos ``abc.ABC`` para que la intención sea
  explícita y no se pueda instanciar. La alternativa pythonica moderna sería un
  ``typing.Protocol`` (tipado estructural) o incluso un simple ``Callable[[str], None]``;
  mantenemos la clase abstracta para que se vea la estructura GoF.
"""

from abc import ABC, abstractmethod


class Observer(ABC):
    """Interfaz Observer: reacciona cuando el sujeto publica un mensaje."""

    @abstractmethod
    def actualizar(self, mensaje: str) -> None:
        """Recibe la notificación del sujeto."""
