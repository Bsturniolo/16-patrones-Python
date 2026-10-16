"""Patrón Iterator - ``CatalogoIteratorPorCategoria`` (ConcreteIterator: filtra por categoría).

Rol en el patrón: recorre solo los items de una categoría.

Java vs Python: ``equalsIgnoreCase`` -> comparación con ``.lower()``. El filtro se calcula al
crear el iterador (foto fija), igual que en Java. La versión con generador
(``Catalogo.items_por_categoria``) es perezosa y ve los cambios del catálogo.
"""

from collections.abc import Sequence

from .catalogo_iterator import CatalogoIterator
from .item_catalogo import ItemCatalogo


class CatalogoIteratorPorCategoria(CatalogoIterator):
    """ConcreteIterator: filtro por categoría."""

    def __init__(self, items: Sequence[ItemCatalogo], categoria: str) -> None:
        super().__init__([i for i in items if i.categoria.lower() == categoria.lower()])
