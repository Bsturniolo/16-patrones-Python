"""Patrón Decorator - ``GarantiaExtendidaDecorador`` (ConcreteDecorator: $2.50 por mes).

Java vs Python: el estado extra (``meses_extra``) vive en el decorador, igual que
el campo ``mesesExtra`` de Java.
"""

from typing import Final, override

from ...creacional.factory import Producto
from .producto_decorador import ProductoDecorador


class GarantiaExtendidaDecorador(ProductoDecorador):
    COSTO_POR_MES: Final = 2.50

    def __init__(self, producto: Producto, meses_extra: int) -> None:
        super().__init__(producto)
        self._meses_extra = meses_extra

    @override
    def mostrar_info(self) -> None:
        self._producto_decorado.mostrar_info()
        costo_total = self._meses_extra * self.COSTO_POR_MES
        print(f"  + Garantía extendida +{self._meses_extra} meses (${costo_total:.2f})")

    @property
    @override
    def precio(self) -> float:
        return self._producto_decorado.precio + (self._meses_extra * self.COSTO_POR_MES)

    @property
    @override
    def nombre(self) -> str:
        nombre_envuelto = self._producto_decorado.nombre
        return f"{nombre_envuelto} [Garantía extendida +{self._meses_extra} meses]"
