"""Patrón Chain of Responsibility - ``ValidadorMetodoPago`` (ConcreteHandler).

Simulación: el método de pago siempre está autorizado (igual que en Java).

Java vs Python:
- Misma estructura que ``ValidadorDireccion``: un ``if`` sobre una constante ``true`` que
  imita una consulta real al medio de pago (la rama de rechazo es inalcanzable).
- El mensaje de error se conserva igual que en Java; ``@Override`` -> ``typing.override``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .validador_pedido import ValidadorPedido

if TYPE_CHECKING:
    from ...creacional.builder.pedido import Pedido


class ValidadorMetodoPago(ValidadorPedido):
    @override
    def validar(self, pedido: Pedido) -> bool:
        print("[OK] Validando método de pago...")

        # Simulación: verificar que el método de pago esté activo
        metodo_valido = True

        if metodo_valido:
            print("  Método de pago verificado y autorizado")
            return self._validar_siguiente(pedido)
        print("  [X] ERROR: Método de pago no autorizado")
        return False
