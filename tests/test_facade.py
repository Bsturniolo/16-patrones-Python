"""Tests del patrón Facade (TiendaFacade)."""

import io
import unittest
from contextlib import redirect_stdout
from typing import override

from patrones.comportamiento.state import PedidoContext
from patrones.estructural.facade import TiendaFacade
from patrones.estructural.facade.demo import demo
from tests.ayudantes import capturar, capturar_con_resultado, exigir_tipo


class TestRealizarCompraCompleta(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.tienda = TiendaFacade("MegaStore Online")

    def comprar(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        tarjeta: str = "1234",
        direccion: str = "Calle 1",
    ) -> tuple[PedidoContext | None, str]:
        """``(pedido devuelto o None, salida impresa)`` de una compra completa."""
        return capturar_con_resultado(
            lambda: self.tienda.realizar_compra_completa(tipo, nombre, precio, direccion, tarjeta)
        )

    def comprar_ok(self, tipo: str, nombre: str, precio: float) -> PedidoContext:
        """Compra que debe salir bien: devuelve el ``PedidoContext`` ya tipado."""
        pedido, _ = self.comprar(tipo, nombre, precio)
        return exigir_tipo(pedido, PedidoContext)

    def test_compra_valida_devuelve_pedido_nuevo_con_monto(self) -> None:
        resultado, _ = self.comprar(
            "electronico", "Samsung Galaxy S24", 899.99, "4532-9876-5432-1098", "Calle Mayor 789"
        )
        pedido = exigir_tipo(resultado, PedidoContext)
        self.assertEqual(pedido.estado.nombre_estado, "NUEVO")
        # Diferencia con Java: el monto incluye el envio Express ($15), no solo el precio.
        self.assertAlmostEqual(pedido.monto, 899.99 + 15.0)
        self.assertTrue(pedido.numero_pedido.startswith("FAC-"))

    def test_el_pedido_devuelto_puede_avanzar_de_estado(self) -> None:
        pedido = self.comprar_ok("libro", "Don Quijote", 19.99)
        capturar(pedido.avanzar)
        self.assertEqual(pedido.estado.nombre_estado, "CONFIRMADO")
        capturar(pedido.avanzar)
        self.assertEqual(pedido.estado.nombre_estado, "ENVIADO")

    def test_usa_la_tarjeta_indicada_para_pagar(self) -> None:
        _, salida = self.comprar("electronico", "TV", 100.0, "4532-9876-5432-1098")
        self.assertIn("Pagando $115.0 con tarjeta terminada en 1098", salida)
        _, salida2 = self.comprar("electronico", "TV", 100.0, "0000-0000-0000-7777")
        self.assertIn("tarjeta terminada en 7777", salida2)
        self.assertNotIn("1098", salida2)

    def test_tipo_libro_crea_libro_y_electronico_crea_electronico(self) -> None:
        _, salida_libro = self.comprar("libro", "Don Quijote", 19.99)
        _, salida_elec = self.comprar("electronico", "Laptop", 500.0)
        self.assertIn("Libro: Don Quijote | Autor: Autor Desconocido", salida_libro)
        self.assertIn("Electrónico: Laptop | Garantía: 12 meses", salida_elec)

    def test_tipo_ignora_mayusculas(self) -> None:
        # Antes (como en Java) "LIBRO" se creaba como electronico por caer en el else.
        pedido, salida = self.comprar("LIBRO", "Don Quijote", 19.99)
        self.assertIsNotNone(pedido)
        self.assertIn("Libro: Don Quijote | Autor: Autor Desconocido", salida)
        self.assertNotIn("Electrónico", salida)

    def test_tipo_invalido_rechaza_la_compra_sin_cobrar(self) -> None:
        pedido, salida = self.comprar("juguete", "Robot", 30.0)
        self.assertIsNone(pedido)
        self.assertIn("✗ Pedido rechazado - Tipo de producto no válido: juguete", salida)
        self.assertNotIn("Pagando", salida)
        self.assertNotIn("Pago procesado", salida)
        self.assertNotIn("COMPRA COMPLETADA", salida)

    def test_cobra_producto_mas_envio_y_lo_explica(self) -> None:
        resultado, salida = self.comprar("electronico", "TV", 100.0)
        self.assertIn("Monto válido: $115.00", salida)  # lo que valida la cadena...
        self.assertIn("Pagando $115.0 con tarjeta", salida)  # ...es lo que se cobra
        self.assertNotIn("Pagando $100.0", salida)
        self.assertIn("Total a cobrar: $115.00 (producto $100.00 + envío $15.00)", salida)
        self.assertEqual(exigir_tipo(resultado, PedidoContext).monto, 115.0)

    def test_pago_procesado_aparece_solo_despues_de_pagar(self) -> None:
        _, salida = self.comprar("libro", "Don Quijote", 19.99)
        self.assertLess(salida.index("Pagando"), salida.index("Pago procesado"))

    def test_ids_de_pedido_unicos_en_compras_seguidas(self) -> None:
        ids = {self.comprar_ok("libro", "L", 19.99).numero_pedido for _ in range(50)}
        self.assertEqual(len(ids), 50)

    def test_monto_sobre_el_maximo_es_rechazado_sin_cobrar(self) -> None:
        pedido, salida = self.comprar("electronico", "Joya", 5000.0)
        self.assertIsNone(pedido)
        self.assertIn("✗ Pedido rechazado - validación fallida", salida)
        self.assertNotIn("Pagando", salida)
        self.assertNotIn("[4/5]", salida)

    def test_monto_bajo_el_minimo_es_rechazado(self) -> None:
        pedido, salida = self.comprar("libro", "Promo", -10.0)
        self.assertIsNone(pedido)
        self.assertIn("El monto mínimo es $10.0", salida)
        self.assertNotIn("COMPRA COMPLETADA", salida)

    def test_compra_valida_ejecuta_los_cinco_pasos(self) -> None:
        _, salida = self.comprar("libro", "Don Quijote", 19.99)
        for paso in ("[1/5]", "[2/5]", "[3/5]", "[4/5]", "[5/5]"):
            self.assertIn(paso, salida)
        self.assertIn("¡COMPRA COMPLETADA EXITOSAMENTE EN MegaStore Online!", salida)


class TestCompraRapida(unittest.TestCase):
    def test_imprime_producto_precio_y_direccion(self) -> None:
        tienda = TiendaFacade("MegaStore Online")
        salida = capturar(tienda.compra_rapida, "AirPods Pro", 249.99, "Plaza España 10, Sevilla")
        self.assertIn("=== COMPRA RÁPIDA EN MegaStore Online ===", salida)
        self.assertIn("Producto: AirPods Pro", salida)
        self.assertIn("Precio: $249.99", salida)
        self.assertIn("Envío a: Plaza España 10, Sevilla", salida)

    def test_no_pasa_por_validacion_ni_pago(self) -> None:
        tienda = TiendaFacade("Otra")
        salida = capturar(tienda.compra_rapida, "X", 1.0, "Y")
        self.assertIn("COMPRA RÁPIDA EN Otra", salida)
        self.assertNotIn("Pagando", salida)
        self.assertNotIn("Validando", salida)


class TestConsultarEstadoPedido(unittest.TestCase):
    def test_pedido_existente_muestra_su_estado(self) -> None:
        tienda = TiendaFacade("MegaStore Online")
        with redirect_stdout(io.StringIO()):
            pedido = PedidoContext("ORD-9", 50.0)
            pedido.avanzar()
        salida = capturar(tienda.consultar_estado_pedido, pedido)
        self.assertIn("=== CONSULTA DE ESTADO - MegaStore Online ===", salida)
        self.assertIn("Pedido ORD-9: ", salida)
        self.assertNotIn("no encontrado", salida)

    def test_pedido_inexistente_informa_no_encontrado(self) -> None:
        tienda = TiendaFacade("MegaStore Online")
        salida = capturar(tienda.consultar_estado_pedido, None)
        self.assertIn("✗ Pedido no encontrado", salida)
        self.assertTrue(salida.endswith("\n\n"))

    def test_estado_refleja_avance_posterior(self) -> None:
        tienda = TiendaFacade("T")
        with redirect_stdout(io.StringIO()):
            pedido = PedidoContext("ORD-1", 10.0)
        antes = capturar(tienda.consultar_estado_pedido, pedido)
        capturar(pedido.avanzar)
        despues = capturar(tienda.consultar_estado_pedido, pedido)
        self.assertNotEqual(antes, despues)


class TestNombreTienda(unittest.TestCase):
    def test_nombre_tienda(self) -> None:
        self.assertEqual(TiendaFacade("A").nombre_tienda, "A")
        self.assertEqual(TiendaFacade("B").nombre_tienda, "B")


class TestDemo(unittest.TestCase):
    def test_demo(self) -> None:
        salida = capturar(demo)
        self.assertTrue(salida.startswith(">>> 13. PATRÓN FACADE <<<\n"))
        self.assertIn("=== PROCESANDO COMPRA EN MegaStore Online ===", salida)
        self.assertIn("Pagando $914.99 con tarjeta terminada en 1098", salida)
        self.assertIn("=== COMPRA RÁPIDA EN MegaStore Online ===", salida)
        self.assertIn("=== CONSULTA DE ESTADO - MegaStore Online ===", salida)


if __name__ == "__main__":
    unittest.main()
