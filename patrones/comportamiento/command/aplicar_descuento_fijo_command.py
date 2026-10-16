"""Patrón Command - ``AplicarDescuentoFijoCommand`` (ConcreteCommand: monto fijo, con undo).

Rol en el patrón: igual que el porcentual, pero el receptor guarda un MONTO (no un
porcentaje del total del momento) y lo resta del total.

Estado de deshacer: ver ``AplicarDescuentoPorcentajeCommand`` (snapshot por ejecución;
``GestorPromociones`` guarda una copia del comando en cada ejecución).

Java vs Python: misma estructura; ``double`` -> ``float``. La validación (monto >= 0) la
hace el receptor, que lanza ``ValueError`` al ejecutar.
"""

from typing import override

from .carrito_compra_command import SIN_DESCUENTO, CarritoCompraCommand, DescuentoVigente
from .command import Command


class AplicarDescuentoFijoCommand(Command):
    """ConcreteCommand: descuento de monto fijo."""

    def __init__(self, carrito: CarritoCompraCommand, monto: float, razon: str) -> None:
        self._carrito = carrito
        self._monto = float(monto)
        self._razon = razon
        self._descuento_anterior: DescuentoVigente = SIN_DESCUENTO

    @override
    def ejecutar(self) -> None:
        anterior = self._carrito.descuento_vigente
        self._carrito.aplicar_descuento_fijo(self._monto, self._razon)
        self._descuento_anterior = anterior  # solo si el receptor aceptó el descuento

    @override
    def deshacer(self) -> None:
        self._carrito.restaurar_descuento(self._descuento_anterior)
        print(f"⟲ Comando deshecho: {self.descripcion}")

    @property
    @override
    def descripcion(self) -> str:
        return f"Aplicar descuento fijo de ${self._monto} - {self._razon}"
