"""Patrón Iterator - ``CatalogoIterator`` (ConcreteIterator básico, secuencial).

Rol en el patrón: guarda la colección y una posición; ``next`` avanza.

Java vs Python:
- Es el iterador "manual" de GoF. Equivale a ``iter(lista)`` de Python, que ya
  trae este mismo comportamiento (salvo ``reset``) sin escribir la clase.
- Los iteradores filtrados/ordenados heredan de esta clase y solo cambian la
  lista que le pasan (en Java cada uno repetía los 3 métodos; aquí se reutilizan).
  Esta clase NO copia la lista: ve los cambios del catálogo, como en Java.
"""

from collections.abc import Sequence
from typing import override

from .item_catalogo import ItemCatalogo
from .iterator import Iterator


class CatalogoIterator(Iterator[ItemCatalogo]):
    """ConcreteIterator: recorrido secuencial."""

    def __init__(self, items: Sequence[ItemCatalogo]) -> None:
        self._items = items
        self._posicion = 0

    @override
    def has_next(self) -> bool:
        return self._posicion < len(self._items)

    @override
    def next(self) -> ItemCatalogo | None:
        if not self.has_next():
            return None
        item = self._items[self._posicion]
        self._posicion += 1
        return item

    @override
    def reset(self) -> None:
        self._posicion = 0
