"""Patrón Command: descuentos como objetos con undo/redo."""

from .aplicar_descuento_fijo_command import AplicarDescuentoFijoCommand
from .aplicar_descuento_porcentaje_command import AplicarDescuentoPorcentajeCommand
from .carrito_compra_command import CarritoCompraCommand, DescuentoVigente
from .command import Command
from .gestor_promociones import GestorPromociones
from .remover_descuento_command import RemoverDescuentoCommand

__all__ = [
    "AplicarDescuentoFijoCommand",
    "AplicarDescuentoPorcentajeCommand",
    "CarritoCompraCommand",
    "Command",
    "DescuentoVigente",
    "GestorPromociones",
    "RemoverDescuentoCommand",
]
