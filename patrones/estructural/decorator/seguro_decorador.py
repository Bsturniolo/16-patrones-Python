"""Patrón Decorator - ``SeguroDecorador`` (ConcreteDecorator: +10% del precio envuelto).

Java vs Python: ``String.format("%.2f")`` se traduce a ``f"{x:.2f}"``.
Nota: el 10% se calcula sobre el precio del producto envuelto (que ya puede
incluir otros decoradores), no sobre el precio base original.
"""

from typing import Final, override

from .producto_decorador import ProductoDecorador


class SeguroDecorador(ProductoDecorador):
    PORCENTAJE_SEGURO: Final = 0.10  # 10% del precio envuelto

    @override
    def mostrar_info(self) -> None:
        self._producto_decorado.mostrar_info()
        costo_seguro = self._producto_decorado.precio * self.PORCENTAJE_SEGURO
        print(f"  + Seguro contra daños (${costo_seguro:.2f})")

    @property
    @override
    def precio(self) -> float:
        return self._producto_decorado.precio * (1 + self.PORCENTAJE_SEGURO)

    @property
    @override
    def nombre(self) -> str:
        return f"{self._producto_decorado.nombre} [Con seguro]"
