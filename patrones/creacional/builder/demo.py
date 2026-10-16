"""Demostración del patrón Builder (sección 6 de Main.java)."""

from ...consola import configurar_utf8
from ..factory import Producto, ProductoFactory
from .pedido import Pedido


def demo() -> None:
    # Productos creados en las secciones previas de Main.java (Factory / Decorator).
    libro1 = ProductoFactory.crear_libro("Cien Años de Soledad", 25.99, "Gabriel García Márquez")
    laptop = ProductoFactory.crear_electronico("Laptop HP", 899.99, 24)
    telefono = ProductoFactory.crear_electronico("iPhone 15", 999.99, 12)
    tablet = ProductoFactory.crear_electronico("iPad Pro", 799.99, 12)

    print(">>> 6. PATRÓN BUILDER <<<")

    # Pedido simple
    productos1: list[Producto] = [libro1, tablet]
    pedido1 = (
        Pedido.PedidoBuilder(productos1, "Calle Principal 123, Madrid")
        .con_metodo_envio("Standard")
        .construir()
    )

    pedido1.mostrar_resumen()
    print(f"Total del pedido: ${pedido1.calcular_total():.2f}")
    print()

    # Pedido complejo con todas las opciones
    productos2: list[Producto] = [laptop, telefono]
    pedido2 = (
        Pedido.PedidoBuilder(productos2, "Avenida Libertad 456, Barcelona")
        .con_metodo_envio("Express")
        .es_regalo_flag(True)
        .con_envoltura_regalo(True)
        .con_mensaje_regalo("¡Feliz cumpleaños!")
        .con_notas_especiales("Entregar por la mañana")
        .construir()
    )

    pedido2.mostrar_resumen()
    print(f"Total del pedido: ${pedido2.calcular_total():.2f}")
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
