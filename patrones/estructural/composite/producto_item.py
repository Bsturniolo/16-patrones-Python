"""Patrón Composite - ``ProductoItem`` (Leaf: producto individual del catálogo).

Java vs Python:
- Java: ``class ProductoItem extends ComponenteCatalogo``; la hoja hereda de la
  base ``agregar``/``remover`` que lanzan ``UnsupportedOperationException``.
  Python: misma herencia; esos métodos lanzan ``NotImplementedError`` (ver
  ``ComponenteCatalogo`` para el matiz con ``TypeError``).
- ``getDescripcion()`` -> propiedad ``descripcion``; ``String`` que puede ser
  ``null`` -> ``str | None``. El chequeo ``!= null && !isEmpty()`` de Java se
  reduce en Python a ``if self._descripcion:`` (``None`` y ``""`` son falsos).
- Las hojas no tienen hijos, así que no necesitan validar ciclos.
"""

from typing import override

from .componente_catalogo import ComponenteCatalogo


class ProductoItem(ComponenteCatalogo):
    def __init__(self, nombre: str, precio: float, descripcion: str | None) -> None:
        super().__init__(nombre, precio)
        self._descripcion = descripcion

    @override
    def mostrar_detalle(self, nivel: int) -> None:
        indent = self._obtener_indentacion(nivel)
        print(f"{indent}[Producto] {self._nombre} - ${self._precio:.2f}")
        if self._descripcion:  # equivale a "!= null && !isEmpty()"
            print(f"{indent}  Descripción: {self._descripcion}")

    @property
    @override
    def precio_total(self) -> float:
        return self._precio

    @property
    def descripcion(self) -> str | None:
        return self._descripcion
