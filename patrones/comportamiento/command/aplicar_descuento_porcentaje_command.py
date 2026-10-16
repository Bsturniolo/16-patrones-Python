"""Patrón Command - ``AplicarDescuentoPorcentajeCommand`` (ConcreteCommand: porcentaje).

Rol en el patrón: guarda el descuento anterior al ejecutar para poder
restaurarlo en ``deshacer``.

Estado de deshacer: se guarda un snapshot (``DescuentoVigente``) cada vez que se ejecuta.
Por eso una MISMA instancia no debe ejecutarse dos veces seguidas sin más: la segunda
ejecución pisaría el snapshot de la primera. ``GestorPromociones`` lo resuelve guardando una
copia del comando en cada ejecución (nota de GoF: "si los comandos pueden tener estado y
ejecutarse más de una vez, hay que copiarlos antes de guardarlos en el historial").

Java vs Python: misma estructura; ``double`` -> ``float`` (se convierte para
que ``10`` se muestre como ``10.0`` igual que en Java). La validación del rango 0-100 la
hace el receptor, que lanza ``ValueError`` al ejecutar.
"""

from typing import override

from .carrito_compra_command import SIN_DESCUENTO, CarritoCompraCommand, DescuentoVigente
from .command import Command


class AplicarDescuentoPorcentajeCommand(Command):
    """ConcreteCommand: descuento porcentual."""

    def __init__(self, carrito: CarritoCompraCommand, porcentaje: float, razon: str) -> None:
        self._carrito = carrito
        self._porcentaje = float(porcentaje)
        self._razon = razon
        self._descuento_anterior: DescuentoVigente = SIN_DESCUENTO

    @override
    def ejecutar(self) -> None:
        anterior = self._carrito.descuento_vigente
        self._carrito.aplicar_descuento_porcentaje(self._porcentaje, self._razon)
        self._descuento_anterior = anterior  # solo si el receptor aceptó el descuento

    @override
    def deshacer(self) -> None:
        self._carrito.restaurar_descuento(self._descuento_anterior)
        print(f"⟲ Comando deshecho: {self.descripcion}")

    @property
    @override
    def descripcion(self) -> str:
        return f"Aplicar descuento del {self._porcentaje}% - {self._razon}"
