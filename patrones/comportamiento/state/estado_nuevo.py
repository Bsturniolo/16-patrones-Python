"""Patrón State - ``EstadoNuevo`` (ConcreteState: estado inicial).

Java vs Python:
- Los estados se crean entre sí y forman ciclos: ``EstadoNuevo.siguiente`` crea un
  ``EstadoConfirmado`` y ``EstadoConfirmado.anterior`` crea un ``EstadoNuevo`` (idem
  Confirmado <-> Enviado y Enviado <-> Entregado). Con un módulo por clase (como en Java) un
  ``import`` a nivel de módulo en ambos sentidos fallaría con ``ImportError`` (módulo
  parcialmente inicializado). La solución es hacer el import *dentro del método*, cuando ya
  están cargados los dos módulos.
- Alternativas: poner todos los estados en un único módulo (sin imports entre ellos) o usar
  un ``enum.Enum`` con una tabla de transiciones.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from .pedido_context import PedidoContext


class EstadoNuevo(EstadoPedido):
    @override
    def siguiente(self, pedido: PedidoContext) -> None:
        from .estado_confirmado import EstadoConfirmado

        print("✓ Pedido confirmado y en proceso de pago")
        pedido.estado = EstadoConfirmado()

    @override
    def anterior(self, pedido: PedidoContext) -> None:
        print("⚠ El pedido ya está en el estado inicial")

    @override
    def cancelar(self, pedido: PedidoContext) -> None:
        from .estado_cancelado import EstadoCancelado

        print("✓ Pedido cancelado desde estado Nuevo")
        pedido.estado = EstadoCancelado()

    @override
    def mostrar_estado(self) -> None:
        print("🆕 NUEVO - Pedido recibido, pendiente de confirmación")

    @property
    @override
    def nombre_estado(self) -> str:
        return "NUEVO"
