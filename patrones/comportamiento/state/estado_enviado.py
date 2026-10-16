"""Patrón State - ``EstadoEnviado`` (ConcreteState: en tránsito, no cancelable).

Java vs Python:
- Es el estado "puente" de dos ciclos de imports (Confirmado <-> Enviado y Enviado <->
  Entregado), así que ``siguiente`` y ``anterior`` importan el estado destino de forma local.
- ``cancelar`` no cambia de estado: solo informa que un pedido en tránsito no se cancela
  (igual que Java). ``@Override`` -> ``typing.override``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from .pedido_context import PedidoContext


class EstadoEnviado(EstadoPedido):
    @override
    def siguiente(self, pedido: PedidoContext) -> None:
        from .estado_entregado import EstadoEntregado

        print("✓ Pedido entregado al cliente")
        pedido.estado = EstadoEntregado()

    @override
    def anterior(self, pedido: PedidoContext) -> None:
        from .estado_confirmado import EstadoConfirmado

        print("↩ Pedido devuelto a almacén (estado Confirmado)")
        pedido.estado = EstadoConfirmado()

    @override
    def cancelar(self, pedido: PedidoContext) -> None:
        print("⚠ No se puede cancelar un pedido en tránsito")
        print("   Por favor contacte al servicio de atención al cliente")

    @override
    def mostrar_estado(self) -> None:
        print("🚚 ENVIADO - En tránsito hacia el destino")

    @property
    @override
    def nombre_estado(self) -> str:
        return "ENVIADO"
