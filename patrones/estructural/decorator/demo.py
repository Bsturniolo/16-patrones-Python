"""Demostración del patrón Decorator (sección 5 de Main.java)."""

from ...consola import configurar_utf8
from ...creacional.factory import Producto, ProductoFactory
from .envoltura_regalo_decorador import EnvolturaRegaloDecorador
from .garantia_extendida_decorador import GarantiaExtendidaDecorador
from .seguro_decorador import SeguroDecorador


def demo() -> None:
    print(">>> 5. PATRÓN DECORATOR <<<")

    # Producto simple
    tablet = ProductoFactory.crear_electronico("iPad Pro", 799.99, 12)
    tablet.mostrar_info()
    print(f"Precio base: ${tablet.precio}\n")

    # Producto con envoltura de regalo
    tablet_con_envoltura: Producto = EnvolturaRegaloDecorador(tablet)
    print("Con decorador de envoltura:")
    tablet_con_envoltura.mostrar_info()
    print(f"Precio total: ${tablet_con_envoltura.precio}\n")

    # Producto con múltiples decoradores
    laptop_premium = ProductoFactory.crear_electronico("MacBook Pro", 1499.99, 12)
    laptop_con_seguro: Producto = SeguroDecorador(laptop_premium)
    laptop_con_garantia: Producto = GarantiaExtendidaDecorador(laptop_con_seguro, 24)
    laptop_completa: Producto = EnvolturaRegaloDecorador(laptop_con_garantia)

    print("Producto con múltiples decoradores:")
    laptop_completa.mostrar_info()
    print(f"Precio total: ${laptop_completa.precio:.2f}")
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
