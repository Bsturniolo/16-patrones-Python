"""Demostración del patrón Iterator (sección 16 de Main.java).

Los iteradores GoF implementan además el protocolo de Python (``__iter__``/``__next__``), así
que se recorren con ``for item in iterador``. El estilo explícito de Java sería::

    while it.has_next():
        item = it.next()  # devuelve ``ItemCatalogo | None``: habría que comprobar None

``next()`` puede devolver ``None`` (como Java), por eso la demo evita llamarlo a mano. Con
generadores el recorrido sería ``for item in catalogo_tech.items_por_categoria("Laptops")``.
"""

from itertools import islice

from ...consola import configurar_utf8
from .catalogo import Catalogo
from .item_catalogo import ItemCatalogo


def demo() -> None:
    print(">>> 16. PATRÓN ITERATOR <<<")

    # Crear catálogo con productos
    catalogo_tech = Catalogo("Tecnología 2025")

    catalogo_tech.agregar_item(ItemCatalogo("MacBook Pro M3", 1999.99, "Laptops", True, 5))
    catalogo_tech.agregar_item(ItemCatalogo("Dell XPS 15", 1599.99, "Laptops", True, 4))
    catalogo_tech.agregar_item(ItemCatalogo("HP Pavilion", 899.99, "Laptops", False, 3))
    catalogo_tech.agregar_item(ItemCatalogo("iPhone 15 Pro", 1199.99, "Smartphones", True, 5))
    catalogo_tech.agregar_item(ItemCatalogo("Samsung S24 Ultra", 1099.99, "Smartphones", True, 5))
    catalogo_tech.agregar_item(ItemCatalogo("Google Pixel 8", 699.99, "Smartphones", True, 4))
    catalogo_tech.agregar_item(ItemCatalogo("iPad Pro", 899.99, "Tablets", True, 5))
    catalogo_tech.agregar_item(ItemCatalogo("Surface Pro", 799.99, "Tablets", False, 4))
    catalogo_tech.agregar_item(ItemCatalogo("Mouse MX Master", 99.99, "Accesorios", True, 5))
    catalogo_tech.agregar_item(ItemCatalogo("Teclado Mecánico", 149.99, "Accesorios", True, 4))

    # Mostrar catálogo completo
    catalogo_tech.mostrar_catalogo()

    # Iterar por categoría - Laptops
    print("--- Filtrar por categoría: Laptops ---")
    iterador_laptops = catalogo_tech.crear_iterator_por_categoria("Laptops")
    for item in iterador_laptops:
        item.mostrar_info()
    print()

    # Iterar solo productos en stock
    print("--- Filtrar productos en stock ---")
    iterador_stock = catalogo_tech.crear_iterator_en_stock()
    contador = 0
    for item in iterador_stock:
        item.mostrar_info()
        contador += 1
    print(f"Total en stock: {contador}\n")

    # Iterar por rango de precio
    print("--- Filtrar por precio: $500 - $1000 ---")
    iterador_precio = catalogo_tech.crear_iterator_por_precio(500, 1000)
    for item in iterador_precio:
        item.mostrar_info()
    print()

    # Iterar por popularidad
    print("--- Ordenar por popularidad (Top 5) ---")
    iterador_popular = catalogo_tech.crear_iterator_por_popularidad()
    for posicion, item in enumerate(islice(iterador_popular, 5), start=1):
        print(f"{posicion}. ", end="")
        item.mostrar_info()
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
