"""Patrón Iterator - ``CatalogoIteratorEnStock`` (ConcreteIterator: solo items en stock).

Rol en el patrón: recorre solo los items con ``en_stock`` verdadero.

Java vs Python: el filtro es una comprensión de lista en vez del ``for`` + ``if``
de Java. Es una foto fija tomada al crear el iterador; ``Catalogo.items_en_stock`` es la
versión con generador, que en cambio es perezosa y ve los cambios del catálogo.
"""

from collections.abc import Sequence

from .catalogo_iterator import CatalogoIterator
from .item_catalogo import ItemCatalogo


class CatalogoIteratorEnStock(CatalogoIterator):
    """ConcreteIterator: solo items en stock."""

    def __init__(self, items: Sequence[ItemCatalogo]) -> None:
        super().__init__([i for i in items if i.en_stock])
