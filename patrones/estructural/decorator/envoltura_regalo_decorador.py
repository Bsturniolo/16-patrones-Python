"""Patrón Decorator - ``EnvolturaRegaloDecorador`` (ConcreteDecorator: +$3.50).

Java vs Python: ``private static final`` pasa a constante de clase en MAYÚSCULAS anotada con
``typing.Final`` (mypy rechaza reasignarla, el equivalente estático de ``final``).
``print`` de un float imprime ``3.5``, igual que la concatenación de un double en Java.
"""

from typing import Final, override

from .producto_decorador import ProductoDecorador


class EnvolturaRegaloDecorador(ProductoDecorador):
    COSTO_ENVOLTURA: Final = 3.50

    @override
    def mostrar_info(self) -> None:
        self._producto_decorado.mostrar_info()
        print(f"  + Envoltura de regalo (${self.COSTO_ENVOLTURA})")

    @property
    @override
    def precio(self) -> float:
        return self._producto_decorado.precio + self.COSTO_ENVOLTURA

    @property
    @override
    def nombre(self) -> str:
        return f"{self._producto_decorado.nombre} [Con envoltura de regalo]"
