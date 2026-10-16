"""Demo del patrón Chain of Responsibility (sección 7 de Main.java).

Los pedidos son los armados en la sección Builder de Main.java (aquí se recrean sin
imprimir su resumen para que la demo sea autónoma).
"""

from ...consola import configurar_utf8
from ...creacional.builder.pedido import Pedido
from ...creacional.factory import ProductoFactory
from .validador_direccion import ValidadorDireccion
from .validador_metodo_pago import ValidadorMetodoPago
from .validador_monto_pedido import ValidadorMontoPedido
from .validador_stock import ValidadorStock


def demo() -> None:
    libro1 = ProductoFactory.crear_libro("Cien Años de Soledad", 25.99, "Gabriel García Márquez")
    laptop = ProductoFactory.crear_electronico("Laptop HP", 899.99, 24)
    telefono = ProductoFactory.crear_electronico("iPhone 15", 999.99, 12)
    tablet = ProductoFactory.crear_electronico("iPad Pro", 799.99, 12)

    pedido1 = (
        Pedido.PedidoBuilder([libro1, tablet], "Calle Principal 123, Madrid")
        .con_metodo_envio("Standard")
        .construir()
    )
    pedido2 = (
        Pedido.PedidoBuilder([laptop, telefono], "Avenida Libertad 456, Barcelona")
        .con_metodo_envio("Express")
        .es_regalo_flag(True)
        .con_envoltura_regalo(True)
        .con_mensaje_regalo("¡Feliz cumpleaños!")
        .con_notas_especiales("Entregar por la mañana")
        .construir()
    )

    print(">>> 7. PATRÓN CHAIN OF RESPONSIBILITY <<<")

    # Configurar la cadena de validadores
    validador_stock = ValidadorStock()
    validador_direccion = ValidadorDireccion()
    validador_monto = ValidadorMontoPedido()
    validador_pago = ValidadorMetodoPago()

    # set_siguiente devuelve el eslabón enlazado: la cadena se arma en una sola expresión
    validador_stock.set_siguiente(validador_direccion).set_siguiente(validador_monto).set_siguiente(
        validador_pago
    )

    print("\n=== VALIDANDO PEDIDO 1 ===")
    if validador_stock.validar(pedido1):
        print("\n[OK][OK][OK] PEDIDO VALIDADO EXITOSAMENTE [OK][OK][OK]\n")
    else:
        print("\n[X][X][X] PEDIDO RECHAZADO [X][X][X]\n")

    print("=== VALIDANDO PEDIDO 2 ===")
    if validador_stock.validar(pedido2):
        print("\n[OK][OK][OK] PEDIDO VALIDADO EXITOSAMENTE [OK][OK][OK]\n")
    else:
        print("\n[X][X][X] PEDIDO RECHAZADO [X][X][X]\n")


if __name__ == "__main__":
    configurar_utf8()
    demo()
