"""Tests del patrón State (PedidoContext + EstadoPedido)."""

import io
import unittest
from contextlib import redirect_stdout

from patrones.comportamiento.state import (
    EstadoCancelado,
    EstadoConfirmado,
    EstadoEntregado,
    EstadoEnviado,
    EstadoNuevo,
    EstadoPedido,
    PedidoContext,
)
from patrones.comportamiento.state import pedido_context as modulo_pedido_context
from patrones.comportamiento.state.demo import demo
from tests.ayudantes import capturar


def nuevo_pedido(numero: str = "P-1", monto: float = 100.0) -> PedidoContext:
    with redirect_stdout(io.StringIO()):
        return PedidoContext(numero, monto)


class TestState(unittest.TestCase):
    def test_interfaz_abstracta(self) -> None:
        with self.assertRaises(TypeError):
            EstadoPedido()  # type: ignore[abstract]

    def test_creacion_imprime_y_arranca_en_nuevo(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            pedido = PedidoContext("ORD-1", 899.99)
        self.assertEqual(buffer.getvalue(), "📦 Pedido ORD-1 creado por $899.99\n")
        self.assertEqual(pedido.estado.nombre_estado, "NUEVO")
        self.assertEqual(pedido.numero_pedido, "ORD-1")
        self.assertEqual(pedido.monto, 899.99)

    def test_flujo_normal_completo(self) -> None:
        pedido = nuevo_pedido()
        nombres = []
        for _ in range(3):
            capturar(pedido.avanzar)
            nombres.append(pedido.estado.nombre_estado)
        self.assertEqual(nombres, ["CONFIRMADO", "ENVIADO", "ENTREGADO"])

    def test_avanzar_mensajes_por_estado(self) -> None:
        pedido = nuevo_pedido()
        self.assertEqual(capturar(pedido.avanzar), "✓ Pedido confirmado y en proceso de pago\n")
        self.assertEqual(capturar(pedido.avanzar), "✓ Pedido enviado al almacén para preparación\n")
        self.assertEqual(capturar(pedido.avanzar), "✓ Pedido entregado al cliente\n")

    def test_avanzar_desde_estado_final_no_cambia(self) -> None:
        pedido = nuevo_pedido()
        for _ in range(3):
            capturar(pedido.avanzar)
        salida = capturar(pedido.avanzar)
        self.assertEqual(salida, "⚠ El pedido ya ha sido entregado (estado final)\n")
        self.assertIsInstance(pedido.estado, EstadoEntregado)

    def test_cancelar_desde_nuevo(self) -> None:
        pedido = nuevo_pedido()
        self.assertEqual(capturar(pedido.cancelar), "✓ Pedido cancelado desde estado Nuevo\n")
        self.assertIsInstance(pedido.estado, EstadoCancelado)

    def test_cancelar_desde_confirmado(self) -> None:
        pedido = nuevo_pedido()
        capturar(pedido.avanzar)
        self.assertEqual(capturar(pedido.cancelar), "✓ Pedido cancelado. Procesando reembolso...\n")
        self.assertEqual(pedido.estado.nombre_estado, "CANCELADO")

    def test_cancelar_enviado_es_invalido(self) -> None:
        pedido = nuevo_pedido()
        capturar(pedido.avanzar)
        capturar(pedido.avanzar)
        salida = capturar(pedido.cancelar)
        self.assertIn("No se puede cancelar un pedido en tránsito", salida)
        self.assertIsInstance(pedido.estado, EstadoEnviado)

    def test_cancelar_entregado_es_invalido(self) -> None:
        pedido = nuevo_pedido()
        for _ in range(3):
            capturar(pedido.avanzar)
        salida = capturar(pedido.cancelar)
        self.assertIn("No se puede cancelar un pedido ya entregado", salida)
        self.assertIn("Para devoluciones, use el proceso de retroceso", salida)
        self.assertIsInstance(pedido.estado, EstadoEntregado)

    def test_cancelado_es_terminal(self) -> None:
        pedido = nuevo_pedido()
        capturar(pedido.cancelar)
        self.assertEqual(capturar(pedido.avanzar), "⚠ No se puede avanzar un pedido cancelado\n")
        self.assertEqual(
            capturar(pedido.retroceder), "⚠ No se puede retroceder un pedido cancelado\n"
        )
        self.assertEqual(capturar(pedido.cancelar), "⚠ El pedido ya está cancelado\n")
        self.assertIsInstance(pedido.estado, EstadoCancelado)

    def test_retroceder_desde_nuevo_no_hace_nada(self) -> None:
        pedido = nuevo_pedido()
        self.assertEqual(capturar(pedido.retroceder), "⚠ El pedido ya está en el estado inicial\n")
        self.assertIsInstance(pedido.estado, EstadoNuevo)

    def test_retroceder_recorre_hacia_atras(self) -> None:
        pedido = nuevo_pedido()
        for _ in range(3):
            capturar(pedido.avanzar)
        for tipo in (EstadoEnviado, EstadoConfirmado, EstadoNuevo):
            capturar(pedido.retroceder)
            self.assertIsInstance(pedido.estado, tipo)

    def test_mostrar_estado_incluye_numero_y_descripcion(self) -> None:
        pedido = nuevo_pedido("ORD-9")
        self.assertEqual(
            capturar(pedido.mostrar_estado),
            "Pedido ORD-9: 🆕 NUEVO - Pedido recibido, pendiente de confirmación\n",
        )
        capturar(pedido.avanzar)
        self.assertEqual(
            capturar(pedido.mostrar_estado),
            "Pedido ORD-9: ✅ CONFIRMADO - Pago procesado, preparando para envío\n",
        )
        capturar(pedido.avanzar)
        self.assertIn("🚚 ENVIADO - En tránsito hacia el destino", capturar(pedido.mostrar_estado))
        capturar(pedido.avanzar)
        salida = capturar(pedido.mostrar_estado)
        self.assertIn("📬 ENTREGADO - Pedido entregado exitosamente", salida)

    def test_pedidos_son_independientes(self) -> None:
        a, b = nuevo_pedido("A"), nuevo_pedido("B")
        capturar(a.avanzar)
        self.assertEqual(a.estado.nombre_estado, "CONFIRMADO")
        self.assertEqual(b.estado.nombre_estado, "NUEVO")

    def test_pedido_context_importa_estado_nuevo_a_nivel_de_modulo(self) -> None:
        # El ciclo de imports real está ENTRE estados (Nuevo <-> Confirmado <-> ...), no
        # entre el contexto y los estados: por eso el contexto importa a nivel de módulo.
        self.assertIs(modulo_pedido_context.EstadoNuevo, EstadoNuevo)

    def test_ida_y_vuelta_entre_estados_que_se_crean_mutuamente(self) -> None:
        # Nuevo <-> Confirmado se instancian entre sí: es el ciclo que justifica los
        # imports locales dentro de los métodos de los estados.
        pedido = nuevo_pedido()
        capturar(pedido.avanzar)
        self.assertIsInstance(pedido.estado, EstadoConfirmado)
        capturar(pedido.retroceder)
        self.assertIsInstance(pedido.estado, EstadoNuevo)

    def test_retroceder_desde_entregado_procesa_devolucion(self) -> None:
        pedido = nuevo_pedido()
        for _ in range(3):
            capturar(pedido.avanzar)
        self.assertEqual(capturar(pedido.retroceder), "↩ Procesando devolución del pedido...\n")
        self.assertIsInstance(pedido.estado, EstadoEnviado)

    def test_retroceder_desde_enviado_vuelve_a_confirmado(self) -> None:
        pedido = nuevo_pedido()
        for _ in range(2):
            capturar(pedido.avanzar)
        self.assertEqual(
            capturar(pedido.retroceder), "↩ Pedido devuelto a almacén (estado Confirmado)\n"
        )
        self.assertIsInstance(pedido.estado, EstadoConfirmado)


class TestDemo(unittest.TestCase):
    def test_demo_recorre_flujo_normal_y_cancelacion(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 12. PATRÓN STATE <<<", salida)
        self.assertIn("📦 Pedido ORD-STATE-001 creado por $899.99", salida)
        self.assertIn("Pedido ORD-STATE-001: 📬 ENTREGADO - Pedido entregado exitosamente", salida)
        self.assertIn("⚠ El pedido ya ha sido entregado (estado final)", salida)
        self.assertIn(
            "Pedido ORD-STATE-002: ❌ CANCELADO - Pedido cancelado (estado final)", salida
        )
        self.assertIn("⚠ El pedido ya está cancelado", salida)


if __name__ == "__main__":
    unittest.main()
