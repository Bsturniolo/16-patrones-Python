"""Patrón Strategy - ``PagoEfectivo`` (ConcreteStrategy: efectivo con 5% de descuento).

Java vs Python:
- ``printf("%.2f")`` -> f-string con ``:.2f``.
- Nota: igual que en Java, la línea "Pagando $X" muestra el monto SIN descuento y la
  siguiente línea el total ya descontado.
"""

from typing import override

from .estrategia_pago import EstrategiaPago


class PagoEfectivo(EstrategiaPago):
    """Paga en efectivo aplicando 5% de descuento."""

    @override
    def pagar(self, monto: float) -> None:
        print(f"Pagando ${monto} en efectivo. Se aplicó 5% descuento.")
        print(f"Total a pagar: ${monto * 0.95:.2f}")
