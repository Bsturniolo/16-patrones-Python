"""Patrón Iterator - ``Catalogo`` (ConcreteAggregate: el catálogo de productos).

Rol en el patrón: guarda los items y fabrica distintos iteradores sobre ellos,
ocultando que internamente es una ``list``.

Java vs Python:
- Además de los ``crear_iterator*`` (GoF), ``Catalogo`` es *iterable*:
  ``__iter__`` devuelve un iterador nuevo, así que ``for item in catalogo``
  funciona y se puede repetir. Eso es el patrón Iterator integrado en el lenguaje.
- Los métodos ``items_*`` son la versión pythonica con *generadores* (``yield``): producen
  los mismos elementos que los iteradores de clase en 1-3 líneas, pero NO son equivalentes
  en semántica:

  * Los iteradores GoF filtrados (``crear_iterator_por_categoria``, ``_en_stock``,
    ``_por_precio``, ``_por_popularidad``) arman su lista al *crearse*: son una foto fija
    del catálogo en ese momento (``crear_iterator``, el básico, en cambio comparte la
    lista y ve los cambios).
  * Los generadores son *perezosos*: no ejecutan nada hasta el primer ``next`` y recorren
    el catálogo vivo, así que ven los items agregados antes (o durante) el recorrido.
  * ``items_por_popularidad`` es perezoso solo hasta el primer ``next``: ``sorted`` necesita
    ver todos los elementos, así que ordena la colección completa de una vez (O(n log n))
    y a partir de ahí es una foto fija. No es un recorrido "en streaming".
- ``String.format("%-58s")`` -> f-string con ``:<58``; ``getTamanio()`` ->
  propiedad ``tamanio`` y ``len(catalogo)``.
"""

from collections.abc import Iterator as IteradorNativo
from typing import override

from .aggregate import Aggregate
from .catalogo_iterator import CatalogoIterator
from .catalogo_iterator_en_stock import CatalogoIteratorEnStock
from .catalogo_iterator_por_categoria import CatalogoIteratorPorCategoria
from .catalogo_iterator_por_popularidad import CatalogoIteratorPorPopularidad
from .catalogo_iterator_por_precio import CatalogoIteratorPorPrecio
from .item_catalogo import ItemCatalogo
from .iterator import Iterator


class Catalogo(Aggregate[ItemCatalogo]):
    """ConcreteAggregate: colección de ``ItemCatalogo``."""

    def __init__(self, nombre_catalogo: str) -> None:
        self._nombre_catalogo = nombre_catalogo
        self._items: list[ItemCatalogo] = []

    def agregar_item(self, item: ItemCatalogo) -> None:
        self._items.append(item)

    def remover_item(self, item: ItemCatalogo) -> None:
        if item in self._items:
            self._items.remove(item)

    @property
    def tamanio(self) -> int:
        return len(self._items)

    @property
    def nombre_catalogo(self) -> str:
        return self._nombre_catalogo

    # --- Iteradores GoF -----------------------------------------------------
    @override
    def crear_iterator(self) -> Iterator[ItemCatalogo]:
        """Crea un iterador simple que recorre todos los items."""
        return CatalogoIterator(self._items)

    def crear_iterator_por_categoria(self, categoria: str) -> Iterator[ItemCatalogo]:
        """Crea un iterador que filtra por categoría."""
        return CatalogoIteratorPorCategoria(self._items, categoria)

    def crear_iterator_en_stock(self) -> Iterator[ItemCatalogo]:
        """Crea un iterador que filtra por disponibilidad en stock."""
        return CatalogoIteratorEnStock(self._items)

    def crear_iterator_por_precio(
        self, precio_min: float, precio_max: float
    ) -> Iterator[ItemCatalogo]:
        """Crea un iterador que filtra por rango de precio."""
        return CatalogoIteratorPorPrecio(self._items, precio_min, precio_max)

    def crear_iterator_por_popularidad(self) -> Iterator[ItemCatalogo]:
        """Crea un iterador que ordena por popularidad."""
        return CatalogoIteratorPorPopularidad(self._items)

    # --- Protocolo de Python ---------------------------------------------------
    def __iter__(self) -> IteradorNativo[ItemCatalogo]:
        """Permite ``for item in catalogo`` (cada for obtiene un iterador nuevo)."""
        return self.crear_iterator()

    def __len__(self) -> int:
        return len(self._items)

    # --- Versión pythonica con generadores (perezosos; ver docstring del módulo) -----
    def items_por_categoria(self, categoria: str) -> IteradorNativo[ItemCatalogo]:
        """Genera los items de una categoría; perezoso, ve el catálogo vivo."""
        for item in self._items:
            if item.categoria.lower() == categoria.lower():
                yield item

    def items_en_stock(self) -> IteradorNativo[ItemCatalogo]:
        """Genera los items en stock; perezoso, ve el catálogo vivo."""
        for item in self._items:
            if item.en_stock:
                yield item

    def items_por_precio(
        self, precio_min: float, precio_max: float
    ) -> IteradorNativo[ItemCatalogo]:
        """Genera los items del rango de precio; perezoso, ve el catálogo vivo."""
        for item in self._items:
            if precio_min <= item.precio <= precio_max:
                yield item

    def items_por_popularidad(self) -> IteradorNativo[ItemCatalogo]:
        """Genera los items de mayor a menor popularidad (ordena todo en el primer ``next``)."""
        yield from sorted(self._items, key=lambda i: i.popularidad, reverse=True)

    def mostrar_catalogo(self) -> None:
        print("\n╔══════════════════════════════════════════════════════════════════════════╗")
        print(f"║  📚 CATÁLOGO: {self._nombre_catalogo:<58}║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print(f"║  {'Producto':<30} {'Precio':<10} {'Categoría':<12} {'Rating':<10} {'Stock':<6} ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")

        for item in self._items:
            estrellas = "★" * item.popularidad + "☆" * (5 - item.popularidad)
            stock = "✓" if item.en_stock else "✗"
            print(
                f"║  {item.nombre:<30} ${item.precio:<9.2f} {item.categoria:<12} "
                f"{estrellas:<10} {stock:<6} ║"
            )

        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print(f"Total de productos: {len(self._items)}\n")
