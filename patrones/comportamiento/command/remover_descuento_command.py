"""Patrón Command - ``RemoverDescuentoCommand`` (ConcreteCommand: quita el descuento).

Rol en el patrón: recuerda el descuento removido (porcentual o fijo) para restaurarlo al
deshacer.

Java vs Python: misma estructura. Quirk de Java mantenido: si no había
descuento previo, ``deshacer`` no hace nada (ni imprime).
"""

from typing import override

from .carrito_compra_command import SIN_DESCUENTO, CarritoCompraCommand, DescuentoVigente
from .command import Command


class RemoverDescuentoCommand(Command):
    """ConcreteCommand: quitar descuento."""

    def __init__(self, carrito: CarritoCompraCommand) -> None:
        self._carrito = carrito
        self._descuento_anterior: DescuentoVigente = SIN_DESCUENTO

    @override
    def ejecutar(self) -> None:
        self._descuento_anterior = self._carrito.descuento_vigente
        self._carrito.remover_descuento()

    @override
    def deshacer(self) -> None:
        if self._descuento_anterior != SIN_DESCUENTO:
            self._carrito.restaurar_descuento(self._descuento_anterior)
            print(f"⟲ Comando deshecho: {self.descripcion}")

    @property
    @override
    def descripcion(self) -> str:
        return "Remover descuento aplicado"
