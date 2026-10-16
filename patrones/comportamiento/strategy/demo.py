"""Demo del patrón Strategy (sección 4 de Main.java).

Los productos son los creados en la sección Factory de Main.java; aquí se recrean
(sin imprimir) para que la demo sea autónoma.
"""

from ...consola import configurar_utf8
from ...creacional.factory import ProductoFactory
from .carrito_compra import CarritoCompra
from .pago_efectivo import PagoEfectivo
from .pago_paypal import PagoPayPal
from .pago_tarjeta import PagoTarjeta


def demo() -> None:
    libro1 = ProductoFactory.crear_libro("Cien Años de Soledad", 25.99, "Gabriel García Márquez")
    libro2 = ProductoFactory.crear_libro("Don Quijote", 19.99, "Miguel de Cervantes")
    laptop = ProductoFactory.crear_electronico("Laptop HP", 899.99, 24)
    telefono = ProductoFactory.crear_electronico("iPhone 15", 999.99, 12)

    print(">>> 4. PATRÓN STRATEGY <<<")

    # Carrito 1 - Pago con tarjeta
    carrito1 = CarritoCompra()
    carrito1.agregar_producto(libro1)
    carrito1.agregar_producto(laptop)
    carrito1.estrategia_pago = PagoTarjeta("4532-1234-5678-9012")
    carrito1.checkout()

    # Carrito 2 - Pago en efectivo
    carrito2 = CarritoCompra()
    carrito2.agregar_producto(telefono)
    carrito2.agregar_producto(libro2)
    carrito2.estrategia_pago = PagoEfectivo()
    carrito2.checkout()

    # Carrito 3 - Pago con PayPal
    carrito3 = CarritoCompra()
    carrito3.agregar_producto(laptop)
    carrito3.agregar_producto(telefono)
    carrito3.estrategia_pago = PagoPayPal("usuario@email.com")
    carrito3.checkout()


if __name__ == "__main__":
    configurar_utf8()
    demo()
