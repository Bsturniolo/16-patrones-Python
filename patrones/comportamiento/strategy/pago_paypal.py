"""Patrón Strategy - ``PagoPayPal`` (ConcreteStrategy: pago con PayPal).

Java vs Python:
- Es la estrategia más simple: solo imprime el monto y la cuenta. En Java el ``double`` se
  concatena crudo (``"$" + monto``) y en Python ``f"{monto}"`` produce el mismo texto para
  los valores de la demo (p. ej. ``1899.98``).
- Como ``email`` es un atributo privado por convención (``_email``), no se expone; Java lo
  guardaba en un campo ``private`` sin getter.
"""

from typing import override

from .estrategia_pago import EstrategiaPago


class PagoPayPal(EstrategiaPago):
    """Paga con una cuenta PayPal (identificada por su email)."""

    def __init__(self, email: str) -> None:
        self._email = email

    @override
    def pagar(self, monto: float) -> None:
        print(f"Pagando ${monto} con PayPal desde la cuenta: {self._email}")
