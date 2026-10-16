"""Patrón Chain of Responsibility - ``ValidadorPedido`` (Handler abstracto).

Rol GoF: *Handler*. Cada eslabón valida algo y, si todo va bien, pasa el pedido al
siguiente; la cadena se corta en el primer fallo y devuelve ``False``.

Java vs Python:
- ``abstract class`` -> ``abc.ABC``; ``protected`` -> guion bajo por convención
  (``_validar_siguiente``, ``_siguiente``).
- ``Pedido`` solo se usa para anotar tipos, así que se importa bajo ``TYPE_CHECKING``
  (evita acoplar en tiempo de ejecución el paquete chain con builder).
- ``set_siguiente`` devuelve el eslabón enlazado (Java: ``void``) para armar la cadena en
  una sola expresión: ``stock.set_siguiente(direccion).set_siguiente(monto)``.
- Por eso ``set_siguiente`` sigue siendo un *método* y no una propiedad con setter: una
  asignación (``stock.siguiente = direccion``) no devuelve nada y no se puede encadenar, y
  el nombre ``set_siguiente`` es el ``setNext`` de GoF, reconocible para quien viene de Java.
- Pythonico alternativo: una lista de funciones validadoras recorrida con ``all(...)``
  (cortocircuita igual). Se mantiene la cadena de objetos para mostrar el patrón.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...creacional.builder.pedido import Pedido


class ValidadorPedido(ABC):
    """Handler abstracto de la cadena de validación."""

    def __init__(self) -> None:
        self._siguiente: ValidadorPedido | None = None

    def set_siguiente(self, siguiente: ValidadorPedido) -> ValidadorPedido:
        """Enlaza el siguiente eslabón y lo devuelve, para poder encadenar las llamadas.

        ``a.set_siguiente(b).set_siguiente(c)`` equivale a ``a -> b -> c``. (En Java el método
        devuelve ``void``; devolver el eslabón enlazado es una mejora de ergonomía.)
        """
        self._siguiente = siguiente
        return siguiente

    @abstractmethod
    def validar(self, pedido: Pedido) -> bool:
        """Valida el pedido; ``True`` si pasa este eslabón y todos los siguientes."""

    def _validar_siguiente(self, pedido: Pedido) -> bool:
        if self._siguiente is not None:
            return self._siguiente.validar(pedido)
        return True
