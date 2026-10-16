"""Patrón State - ``PedidoContext`` (Context).

Rol GoF: *Context*. Mantiene el estado actual y le delega las operaciones; los propios
estados cambian el estado del contexto (transiciones encapsuladas en los estados).

Java vs Python:
- ``getEstado()/setEstado()`` -> propiedad ``estado`` con setter.
- Otros getters (``getNumeroPedido``, ``getMonto``) -> propiedades de solo lectura.
- ``String.format("%.2f")`` -> ``:.2f``.
- ``EstadoNuevo`` se importa a nivel de módulo: entre el contexto y los estados NO hay ciclo
  de imports (``pedido_context`` -> ``estado_nuevo`` -> ``estado_pedido``; el contexto solo se
  importa bajo ``TYPE_CHECKING`` en los estados). El ciclo real está *entre los propios
  estados*: ``EstadoNuevo`` crea un ``EstadoConfirmado`` (``siguiente``) y
  ``EstadoConfirmado`` crea un ``EstadoNuevo`` (``anterior``); lo mismo pasa con
  Confirmado <-> Enviado y Enviado <-> Entregado. Por eso son esos métodos los que hacen un
  import local (ver ``estado_nuevo.py``).
"""

from .estado_nuevo import EstadoNuevo
from .estado_pedido import EstadoPedido


class PedidoContext:
    """Pedido cuyo comportamiento depende de su estado actual."""

    def __init__(self, numero_pedido: str, monto: float) -> None:
        self._numero_pedido = numero_pedido
        self._monto = monto
        # Estado inicial: Nuevo
        self._estado_actual: EstadoPedido = EstadoNuevo()
        print(f"📦 Pedido {numero_pedido} creado por ${monto:.2f}")

    @property
    def estado(self) -> EstadoPedido:
        return self._estado_actual

    @estado.setter
    def estado(self, estado: EstadoPedido) -> None:
        self._estado_actual = estado

    @property
    def numero_pedido(self) -> str:
        return self._numero_pedido

    @property
    def monto(self) -> float:
        return self._monto

    # Delegar operaciones al estado actual
    def avanzar(self) -> None:
        self._estado_actual.siguiente(self)

    def retroceder(self) -> None:
        self._estado_actual.anterior(self)

    def cancelar(self) -> None:
        self._estado_actual.cancelar(self)

    def mostrar_estado(self) -> None:
        print(f"Pedido {self._numero_pedido}: ", end="")
        self._estado_actual.mostrar_estado()
