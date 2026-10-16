"""Patrón Iterator: recorrido de un catálogo con filtros y orden."""

from .aggregate import Aggregate
from .catalogo import Catalogo
from .catalogo_iterator import CatalogoIterator
from .catalogo_iterator_en_stock import CatalogoIteratorEnStock
from .catalogo_iterator_por_categoria import CatalogoIteratorPorCategoria
from .catalogo_iterator_por_popularidad import CatalogoIteratorPorPopularidad
from .catalogo_iterator_por_precio import CatalogoIteratorPorPrecio
from .item_catalogo import ItemCatalogo
from .iterator import Iterator

__all__ = [
    "Aggregate",
    "Catalogo",
    "CatalogoIterator",
    "CatalogoIteratorEnStock",
    "CatalogoIteratorPorCategoria",
    "CatalogoIteratorPorPopularidad",
    "CatalogoIteratorPorPrecio",
    "ItemCatalogo",
    "Iterator",
]
