"""Patrón State - ``EstadoConfirmado`` (ConcreteState: pago procesado).

Java vs Python:
- Crea tres estados distintos (Enviado, Nuevo, Cancelado); los dos primeros forman ciclo con
  su módulo (``EstadoNuevo`` crea ``EstadoConfirmado`` y viceversa), por eso cada import es
  local al método que lo necesita. En Java las clases se resuelven sin orden de carga y no
  hace falta.
- ``@Override`` -> ``typing.override``; ``getNombreEstado()`` -> propiedad abstracta.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from .pedido_context import PedidoContext


class EstadoConfirmado(EstadoPedido):
    @override
    def siguiente(self, pedido: PedidoContext) -> None:
        from .estado_enviado import EstadoEnviado

        print("✓ Pedido enviado al almacén para preparación")
        pedido.estado = EstadoEnviado()

    @override
    def anterior(self, pedido: PedidoContext) -> None:
        from .estado_nuevo import EstadoNuevo

        print("↩ Pedido devuelto a estado Nuevo")
        pedido.estado = EstadoNuevo()

    @override
    def cancelar(self, pedido: PedidoContext) -> None:
        from .estado_cancelado import EstadoCancelado

        print("✓ Pedido cancelado. Procesando reembolso...")
        pedido.estado = EstadoCancelado()

    @override
    def mostrar_estado(self) -> None:
        print("✅ CONFIRMADO - Pago procesado, preparando para envío")

    @property
    @override
    def nombre_estado(self) -> str:
        return "CONFIRMADO"
