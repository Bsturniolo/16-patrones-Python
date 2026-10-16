"""Patrón Iterator - ``ItemCatalogo`` (elemento que se recorre; no es un rol GoF).

Rol en el patrón: es el tipo de elemento ``T`` de la colección (no es parte
estructural del patrón, solo el dato que se itera).

Java vs Python:
- ``getX()`` / ``isEnStock()`` -> propiedades de solo lectura.
- ``"★".repeat(n)`` -> ``"★" * n``; ``String.format("%-30s $%-8.2f ...")`` ->
  f-string con los mismos anchos (``{x:<30}``, ``{precio:<8.2f}``).
- ``toString()`` -> ``__str__`` (redefine ``object.__str__``, por eso lleva ``@override``).
"""

from typing import override


class ItemCatalogo:
    """Producto del catálogo (popularidad de 1 a 5 estrellas)."""

    def __init__(
        self,
        nombre: str,
        precio: float,
        categoria: str,
        en_stock: bool,
        popularidad: int,
    ) -> None:
        self._nombre = nombre
        self._precio = precio
        self._categoria = categoria
        self._en_stock = en_stock
        self._popularidad = min(5, max(1, popularidad))  # Entre 1 y 5

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio(self) -> float:
        return self._precio

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def en_stock(self) -> bool:
        return self._en_stock

    @property
    def popularidad(self) -> int:
        return self._popularidad

    def mostrar_info(self) -> None:
        estrellas = "★" * self._popularidad + "☆" * (5 - self._popularidad)
        stock = "✓ En stock" if self._en_stock else "✗ Agotado"
        print(f"{self._nombre:<30} ${self._precio:<8.2f} [{self._categoria}] {estrellas} {stock}")

    @override
    def __str__(self) -> str:
        return f"{self._nombre} (${self._precio}) - {self._categoria}"
