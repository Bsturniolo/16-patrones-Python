"""Patrón Composite - ``Categoria`` (Composite: agrupa productos y subcategorías).

Java vs Python:
- ``instanceof`` -> ``isinstance``.
- ``remover`` de Java ignora un elemento ausente (``List.remove``); en Python
  ``list.remove`` lanzaría ``ValueError``, así que se protege para mantener el
  comportamiento.
- ``getHijos()`` devuelve una copia defensiva, igual que en Java.
- Quirk de Java mantenido: ``cantidad_productos`` solo cuenta ``ProductoItem`` y
  ``Categoria`` anidadas; los productos dentro de un ``PaqueteProductos`` no se cuentan
  (aunque su precio SÍ entra en ``precio_total``). Además usa ``isinstance``, lo que
  rompe el tratamiento uniforme del patrón: una solución más fiel sería declarar
  ``cantidad_productos`` en el componente. Se conserva por paridad y está probado.
- Validación agregada: no se puede agregar una categoría a sí misma ni crear ciclos.
"""

from typing import override

from .componente_catalogo import ComponenteCatalogo
from .producto_item import ProductoItem


class Categoria(ComponenteCatalogo):
    def __init__(self, nombre: str) -> None:
        super().__init__(nombre, 0.0)  # Las categorías no tienen precio propio
        self._hijos: list[ComponenteCatalogo] = []

    @override
    def agregar(self, componente: ComponenteCatalogo) -> None:
        self._validar_nuevo_hijo(componente)
        self._hijos.append(componente)

    @override
    def _contiene(self, otro: ComponenteCatalogo) -> bool:
        return any(hijo is otro or hijo._contiene(otro) for hijo in self._hijos)

    @override
    def remover(self, componente: ComponenteCatalogo) -> None:
        if componente in self._hijos:
            self._hijos.remove(componente)

    @override
    def mostrar_detalle(self, nivel: int) -> None:
        indent = self._obtener_indentacion(nivel)
        print(f"{indent}[Categoría] {self._nombre} (Total: ${self.precio_total:.2f})")
        for hijo in self._hijos:
            hijo.mostrar_detalle(nivel + 1)

    @property
    @override
    def precio_total(self) -> float:
        total = 0.0
        for hijo in self._hijos:
            total += hijo.precio_total
        return total

    @property
    def cantidad_productos(self) -> int:
        cantidad = 0
        for hijo in self._hijos:
            if isinstance(hijo, ProductoItem):
                cantidad += 1
            elif isinstance(hijo, Categoria):
                cantidad += hijo.cantidad_productos
        return cantidad

    @property
    def hijos(self) -> list[ComponenteCatalogo]:
        return list(self._hijos)
