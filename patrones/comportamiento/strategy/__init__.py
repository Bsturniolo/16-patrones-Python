"""Patrón Strategy: algoritmos de pago intercambiables."""

from .carrito_compra import CarritoCompra
from .estrategia_pago import EstrategiaPago
from .pago_efectivo import PagoEfectivo
from .pago_paypal import PagoPayPal
from .pago_tarjeta import PagoTarjeta

__all__ = ["CarritoCompra", "EstrategiaPago", "PagoEfectivo", "PagoPayPal", "PagoTarjeta"]
