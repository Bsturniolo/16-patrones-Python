"""Patrón Chain of Responsibility - ``ValidadorStock`` (ConcreteHandler).

Simulación: todos los productos tienen stock (igual que en Java).

Java vs Python:
- El ``if/else`` sobre una constante ``true`` se conserva para mostrar la estructura
  de un validador real (la rama de error es inalcanzable en la simulación).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .validador_pedido import ValidadorPedido

if TYPE_CHECKING:
    from ...creacional.builder.pedido import Pedido


class ValidadorStock(ValidadorPedido):
    @override
    def validar(self, pedido: Pedido) -> bool:
        print("[OK] Validando disponibilidad de stock...")

        # Simulación: todos los productos tienen stock
        stock_disponible = True

        if stock_disponible:
            print("  Stock disponible para todos los productos")
            return self._validar_siguiente(pedido)
        print("  [X] ERROR: Stock insuficiente")
        return False
