"""Patrón Iterator - ``CatalogoIteratorPorPrecio`` (ConcreteIterator: rango de precio inclusivo).

Rol en el patrón: recorre solo los items con ``precio_min <= precio <= precio_max``.

Java vs Python: la comparación encadenada ``min <= x <= max`` reemplaza el
``&&`` de Java. Es una foto fija tomada al crear el iterador; ``Catalogo.items_por_precio`` es
la versión con generador, que en cambio es perezosa y ve los cambios del catálogo.
"""

from collections.abc import Sequence

from .catalogo_iterator import CatalogoIterator
from .item_catalogo import ItemCatalogo


class CatalogoIteratorPorPrecio(CatalogoIterator):
    """ConcreteIterator: filtro por rango de precio."""

    def __init__(self, items: Sequence[ItemCatalogo], precio_min: float, precio_max: float) -> None:
        super().__init__([i for i in items if precio_min <= i.precio <= precio_max])
