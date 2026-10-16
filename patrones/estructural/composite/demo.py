"""Demostración del patrón Composite (sección 10 de Main.java)."""

from ...consola import configurar_utf8
from .categoria import Categoria
from .paquete_productos import PaqueteProductos
from .producto_item import ProductoItem


def demo() -> None:
    print(">>> 10. PATRÓN COMPOSITE <<<")

    # Crear categorías
    electronica = Categoria("Electrónica")
    computadoras = Categoria("Computadoras")
    accesorios = Categoria("Accesorios")

    # Agregar productos a categorías
    computadoras.agregar(ProductoItem("MacBook Pro", 1499.99, "Laptop profesional"))
    computadoras.agregar(ProductoItem("Dell XPS", 1299.99, "Laptop ultraligera"))

    accesorios.agregar(ProductoItem("Mouse Logitech", 29.99, "Mouse inalámbrico"))
    accesorios.agregar(ProductoItem("Teclado Mecánico", 89.99, "RGB retroiluminado"))

    # Crear jerarquía
    electronica.agregar(computadoras)
    electronica.agregar(accesorios)

    print("\n--- Estructura del catálogo ---")
    electronica.mostrar_detalle(0)

    # Crear paquete con descuento
    paquete_gamer = PaqueteProductos("Paquete Gamer", 15.0)
    paquete_gamer.agregar(ProductoItem("Laptop Gaming", 1299.99, "Alto rendimiento"))
    paquete_gamer.agregar(ProductoItem("Mouse Gaming", 59.99, "12000 DPI"))
    paquete_gamer.agregar(ProductoItem("Auriculares", 79.99, "Sonido 7.1"))

    print("\n--- Paquete especial ---")
    paquete_gamer.mostrar_detalle(0)
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
