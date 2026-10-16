"""Patrón State - ``EstadoEntregado`` (ConcreteState: pedido entregado).

Estado "final" para avanzar/cancelar, pero (igual que en Java) ``anterior`` permite
procesar una devolución volviendo a ``EstadoEnviado``.

Java vs Python:
- ``EstadoEnviado`` crea un ``EstadoEntregado`` y este crea un ``EstadoEnviado``: ciclo de
  imports entre módulos, resuelto con el import local dentro de ``anterior``.
- Los mensajes de consola se conservan idénticos a Java; ``@Override`` -> ``typing.override``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from .pedido_context import PedidoContext


class EstadoEntregado(EstadoPedido):
    @override
    def siguiente(self, pedido: PedidoContext) -> None:
        print("⚠ El pedido ya ha sido entregado (estado final)")

    @override
    def anterior(self, pedido: PedidoContext) -> None:
        from .estado_enviado import EstadoEnviado

        print("↩ Procesando devolución del pedido...")
        pedido.estado = EstadoEnviado()

    @override
    def cancelar(self, pedido: PedidoContext) -> None:
        print("⚠ No se puede cancelar un pedido ya entregado")
        print("   Para devoluciones, use el proceso de retroceso")

    @override
    def mostrar_estado(self) -> None:
        print("📬 ENTREGADO - Pedido entregado exitosamente")

    @property
    @override
    def nombre_estado(self) -> str:
        return "ENTREGADO"
