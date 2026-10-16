"""Patrón Iterator - ``CatalogoIteratorPorPopularidad`` (ConcreteIterator: más popular primero).

Rol en el patrón: recorre una copia ordenada; el catálogo original no se altera.

Java vs Python: ``Collections.sort`` + ``Comparator`` anónimo -> ``sorted`` con
``key`` y ``reverse=True``. Ambos ordenamientos son estables, así que los items
con igual popularidad conservan su orden original. El orden se calcula al crear el iterador
(foto fija); ``Catalogo.items_por_popularidad`` también ordena todo, pero recién en el
primer ``next``.
"""

from collections.abc import Sequence

from .catalogo_iterator import CatalogoIterator
from .item_catalogo import ItemCatalogo


class CatalogoIteratorPorPopularidad(CatalogoIterator):
    """ConcreteIterator: orden por popularidad descendente."""

    def __init__(self, items: Sequence[ItemCatalogo]) -> None:
        super().__init__(sorted(items, key=lambda i: i.popularidad, reverse=True))
