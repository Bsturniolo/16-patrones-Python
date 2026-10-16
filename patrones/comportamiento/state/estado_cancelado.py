"""Patrón State - ``EstadoCancelado`` (ConcreteState terminal: ninguna transición).

Java vs Python:
- No crea ningún otro estado (todas las operaciones solo avisan por consola), así que no
  necesita imports locales: es el único estado sin ciclo con los demás.
- Java usa ``instanceof``/``getNombreEstado()`` para comparar estados; aquí basta
  ``isinstance`` o la propiedad ``nombre_estado``.
- ``@Override`` -> ``typing.override``; ``getNombreEstado()`` -> propiedad abstracta.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from .pedido_context import PedidoContext


class EstadoCancelado(EstadoPedido):
    @override
    def siguiente(self, pedido: PedidoContext) -> None:
        print("⚠ No se puede avanzar un pedido cancelado")

    @override
    def anterior(self, pedido: PedidoContext) -> None:
        print("⚠ No se puede retroceder un pedido cancelado")

    @override
    def cancelar(self, pedido: PedidoContext) -> None:
        print("⚠ El pedido ya está cancelado")

    @override
    def mostrar_estado(self) -> None:
        print("❌ CANCELADO - Pedido cancelado (estado final)")

    @property
    @override
    def nombre_estado(self) -> str:
        return "CANCELADO"
