"""Patrón Template Method: esqueleto fijo de procesamiento de pedidos."""

from .procesador_pedido import ProcesadorPedido
from .procesador_pedido_express import ProcesadorPedidoExpress
from .procesador_pedido_internacional import ProcesadorPedidoInternacional
from .procesador_pedido_nacional import ProcesadorPedidoNacional

__all__ = [
    "ProcesadorPedido",
    "ProcesadorPedidoExpress",
    "ProcesadorPedidoInternacional",
    "ProcesadorPedidoNacional",
]
