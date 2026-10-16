"""Demo del patrón Template Method (sección 11 de Main.java).

Diferencia visible con la salida de Java: la línea ``[2] Procesando pago de ...`` muestra el
total calculado ($585.00, $985.00, $363.00) y no el monto original ($500.00, $750.00,
$300.00); ver "Diferencia con el Java original" en ``ProcesadorPedido``.
"""

from ...consola import configurar_utf8
from .procesador_pedido import ProcesadorPedido
from .procesador_pedido_express import ProcesadorPedidoExpress
from .procesador_pedido_internacional import ProcesadorPedidoInternacional
from .procesador_pedido_nacional import ProcesadorPedidoNacional


def demo() -> None:
    print(">>> 11. PATRÓN TEMPLATE METHOD <<<")

    # Procesar pedido nacional
    procesador_nacional: ProcesadorPedido = ProcesadorPedidoNacional()
    procesador_nacional.procesar_pedido("ORD-001-NAC", 500.00)

    # Procesar pedido internacional
    procesador_internacional: ProcesadorPedido = ProcesadorPedidoInternacional()
    procesador_internacional.procesar_pedido("ORD-002-INT", 750.00)

    # Procesar pedido express
    procesador_express: ProcesadorPedido = ProcesadorPedidoExpress()
    procesador_express.procesar_pedido("ORD-003-EXP", 300.00)


if __name__ == "__main__":
    configurar_utf8()
    demo()
