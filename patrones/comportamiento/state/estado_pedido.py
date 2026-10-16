"""Patrón State - interfaz ``EstadoPedido``.

Rol GoF: *State*. Declara las operaciones cuyo comportamiento depende del estado.
Cada estado concreto decide qué imprime y a qué estado transiciona.

Java vs Python:
- ``interface`` -> ``abc.ABC``; ``getNombreEstado()`` -> propiedad abstracta ``nombre_estado``.
- ``PedidoContext`` solo se necesita para anotar tipos: import bajo ``TYPE_CHECKING``
  (los estados no lo usan en ejecución; así el módulo del contexto puede importar a los
  estados sin que estos vuelvan a importarlo).
- Alternativa pythonica: un ``enum.Enum`` + tabla de transiciones. Se mantienen clases
  por estado para mostrar el patrón GoF (comportamiento encapsulado en cada estado).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pedido_context import PedidoContext


class EstadoPedido(ABC):
    """Interfaz State para el ciclo de vida de un pedido."""

    @abstractmethod
    def siguiente(self, pedido: PedidoContext) -> None:
        """Avanza al estado siguiente del ciclo de vida (si corresponde)."""

    @abstractmethod
    def anterior(self, pedido: PedidoContext) -> None:
        """Retrocede al estado anterior (si corresponde)."""

    @abstractmethod
    def cancelar(self, pedido: PedidoContext) -> None:
        """Cancela el pedido si el estado lo permite."""

    @abstractmethod
    def mostrar_estado(self) -> None:
        """Imprime la descripción del estado."""

    @property
    @abstractmethod
    def nombre_estado(self) -> str:
        """Nombre en mayúsculas del estado (``NUEVO``, ``CONFIRMADO``...)."""
