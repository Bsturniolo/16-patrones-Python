"""Demo del patrón State (sección 12 de Main.java)."""

from ...consola import configurar_utf8
from .pedido_context import PedidoContext


def demo() -> None:
    print(">>> 12. PATRÓN STATE <<<")

    # Crear pedido y avanzar por los estados
    pedido_state = PedidoContext("ORD-STATE-001", 899.99)

    print("\n--- Flujo normal del pedido ---")
    pedido_state.mostrar_estado()

    pedido_state.avanzar()  # Nuevo -> Confirmado
    pedido_state.mostrar_estado()

    pedido_state.avanzar()  # Confirmado -> Enviado
    pedido_state.mostrar_estado()

    pedido_state.avanzar()  # Enviado -> Entregado
    pedido_state.mostrar_estado()

    print("\n--- Intentar avanzar desde estado final ---")
    pedido_state.avanzar()  # Ya está entregado

    # Crear otro pedido y cancelarlo
    print("\n--- Flujo de cancelación ---")
    pedido_cancelado = PedidoContext("ORD-STATE-002", 450.00)
    pedido_cancelado.mostrar_estado()

    pedido_cancelado.avanzar()  # Nuevo -> Confirmado
    pedido_cancelado.mostrar_estado()

    pedido_cancelado.cancelar()  # Cancelar desde Confirmado
    pedido_cancelado.mostrar_estado()

    print("\n--- Intentar operaciones en pedido cancelado ---")
    pedido_cancelado.avanzar()
    pedido_cancelado.cancelar()


if __name__ == "__main__":
    configurar_utf8()
    demo()
