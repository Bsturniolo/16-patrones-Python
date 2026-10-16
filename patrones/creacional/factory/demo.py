"""Demo del patrón Factory (sección 2 de Main.java)."""

from ...consola import configurar_utf8
from .producto_factory import ProductoFactory


def demo() -> None:
    print(">>> 2. PATRÓN FACTORY <<<")
    libro1 = ProductoFactory.crear_libro("Cien Años de Soledad", 25.99, "Gabriel García Márquez")
    libro2 = ProductoFactory.crear_libro("Don Quijote", 19.99, "Miguel de Cervantes")
    laptop = ProductoFactory.crear_electronico("Laptop HP", 899.99, 24)
    telefono = ProductoFactory.crear_electronico("iPhone 15", 999.99, 12)

    libro1.mostrar_info()
    libro2.mostrar_info()
    laptop.mostrar_info()
    telefono.mostrar_info()
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
