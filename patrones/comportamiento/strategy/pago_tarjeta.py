"""Patrón Strategy - ``PagoTarjeta`` (ConcreteStrategy: pago con tarjeta).

Java vs Python:
- ``substring(length - 4)`` -> slicing ``numero[-4:]``.
- Java concatena el ``double`` crudo (``"$" + monto``); en Python f"{monto}" imprime el
  ``float`` con la misma representación más corta (p. ej. ``925.98``).
"""

from typing import override

from .estrategia_pago import EstrategiaPago


class PagoTarjeta(EstrategiaPago):
    """Paga con tarjeta; muestra solo los últimos 4 dígitos."""

    def __init__(self, numero_tarjeta: str) -> None:
        self._numero_tarjeta = numero_tarjeta

    @override
    def pagar(self, monto: float) -> None:
        ultimos_digitos = self._numero_tarjeta[-4:]
        print(f"Pagando ${monto} con tarjeta terminada en {ultimos_digitos}")
