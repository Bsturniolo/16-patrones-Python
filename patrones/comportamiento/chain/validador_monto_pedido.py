"""Patrón Chain of Responsibility - ``ValidadorMontoPedido`` (ConcreteHandler).

Único validador con lógica real: el total del pedido (productos + envío + envoltura)
debe estar entre 10.00 y 5000.00, ambos límites inclusivos.

Java vs Python:
- ``private static final double`` -> constantes de clase en MAYÚSCULAS (``typing.Final``).
- Los mensajes de error concatenan el ``double`` crudo en Java (``$10.0``, ``$5000.0``);
  en Python f"{10.0}" produce el mismo texto. El total válido usa ``%.2f`` -> ``:.2f``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, override

from .validador_pedido import ValidadorPedido

if TYPE_CHECKING:
    from ...creacional.builder.pedido import Pedido


class ValidadorMontoPedido(ValidadorPedido):
    MONTO_MINIMO: Final[float] = 10.00
    MONTO_MAXIMO: Final[float] = 5000.00

    @override
    def validar(self, pedido: Pedido) -> bool:
        print("[OK] Validando monto del pedido...")

        total = pedido.calcular_total()

        if total < self.MONTO_MINIMO:
            print(f"  [X] ERROR: El monto mínimo es ${self.MONTO_MINIMO}")
            return False

        if total > self.MONTO_MAXIMO:
            print(f"  [X] ERROR: El monto máximo es ${self.MONTO_MAXIMO}")
            return False

        print(f"  Monto válido: ${total:.2f}")
        return self._validar_siguiente(pedido)
