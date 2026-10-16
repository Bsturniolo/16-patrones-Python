"""Tests del patrón Chain of Responsibility (ValidadorPedido)."""

import unittest
from typing import override

from patrones.comportamiento.chain import (
    ValidadorDireccion,
    ValidadorMetodoPago,
    ValidadorMontoPedido,
    ValidadorPedido,
    ValidadorStock,
)
from patrones.comportamiento.chain.demo import demo
from patrones.creacional.builder.pedido import Pedido
from patrones.creacional.factory import ProductoFactory
from tests.ayudantes import capturar, capturar_con_resultado


def pedido_con_precio(precio: float, metodo: str = "Standard") -> Pedido:
    """Pedido de un solo producto. Standard suma 5.00 de envío, Express 15.00."""
    producto = ProductoFactory.crear_libro("Libro", precio, "Autor")
    return Pedido.PedidoBuilder([producto], "Calle 1").con_metodo_envio(metodo).construir()


def armar_cadena() -> ValidadorStock:
    stock, direccion = ValidadorStock(), ValidadorDireccion()
    monto, pago = ValidadorMontoPedido(), ValidadorMetodoPago()
    stock.set_siguiente(direccion)
    direccion.set_siguiente(monto)
    monto.set_siguiente(pago)
    return stock


def validar(validador: ValidadorPedido, pedido: Pedido) -> tuple[bool, str]:
    """``(resultado de la cadena, salida impresa)``."""
    return capturar_con_resultado(lambda: validador.validar(pedido))


class TestChain(unittest.TestCase):
    def test_handler_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            ValidadorPedido()  # type: ignore[abstract]

    def test_cadena_completa_valida_pedido_normal(self) -> None:
        ok, salida = validar(armar_cadena(), pedido_con_precio(100.0))
        self.assertTrue(ok)
        orden = [
            "Validando disponibilidad de stock",
            "Validando dirección de envío",
            "Validando monto del pedido",
            "Validando método de pago",
        ]
        posiciones = [salida.index(texto) for texto in orden]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("Monto válido: $105.00", salida)

    def test_se_detiene_en_el_primer_fallo(self) -> None:
        ok, salida = validar(armar_cadena(), pedido_con_precio(1.0))  # 1 + 5 = 6 < 10
        self.assertFalse(ok)
        self.assertIn("[X] ERROR: El monto mínimo es $10.0", salida)
        self.assertNotIn("Validando método de pago", salida)  # eslabón posterior no se ejecuta

    def test_monto_minimo_inclusive(self) -> None:
        ok, _ = validar(ValidadorMontoPedido(), pedido_con_precio(5.0))  # total 10.00
        self.assertTrue(ok)
        ok, _ = validar(ValidadorMontoPedido(), pedido_con_precio(4.99))  # total 9.99
        self.assertFalse(ok)

    def test_monto_maximo_inclusive(self) -> None:
        ok, _ = validar(ValidadorMontoPedido(), pedido_con_precio(4995.0))  # total 5000.00
        self.assertTrue(ok)
        ok, salida = validar(ValidadorMontoPedido(), pedido_con_precio(4995.01))
        self.assertFalse(ok)
        self.assertIn("[X] ERROR: El monto máximo es $5000.0", salida)

    def test_monto_considera_el_envio_express(self) -> None:
        # 4990 + 15 (Express) = 5005 > 5000 pero 4990 + 5 (Standard) = 4995 es válido
        self.assertTrue(validar(ValidadorMontoPedido(), pedido_con_precio(4990.0))[0])
        self.assertFalse(validar(ValidadorMontoPedido(), pedido_con_precio(4990.0, "Express"))[0])

    def test_validador_sin_siguiente_devuelve_true(self) -> None:
        for validador in (ValidadorStock(), ValidadorDireccion(), ValidadorMetodoPago()):
            ok, salida = validar(validador, pedido_con_precio(50.0))
            self.assertTrue(ok)
            self.assertIn("[OK]", salida)

    def test_cada_validador_delega_al_siguiente(self) -> None:
        stock, pago = ValidadorStock(), ValidadorMetodoPago()
        stock.set_siguiente(pago)
        ok, salida = validar(stock, pedido_con_precio(50.0))
        self.assertTrue(ok)
        self.assertIn("Método de pago verificado y autorizado", salida)

    def test_eslabon_personalizado_puede_cortar_la_cadena(self) -> None:
        class Rechazador(ValidadorPedido):
            @override
            def validar(self, pedido: Pedido) -> bool:
                print("rechazado")
                return False

        stock = ValidadorStock()
        stock.set_siguiente(Rechazador())
        ok, salida = validar(stock, pedido_con_precio(50.0))
        self.assertFalse(ok)
        self.assertIn("rechazado", salida)

    def test_set_siguiente_devuelve_el_siguiente_para_encadenar(self) -> None:
        stock, direccion, monto = ValidadorStock(), ValidadorDireccion(), ValidadorMontoPedido()
        self.assertIs(stock.set_siguiente(direccion), direccion)
        self.assertIs(direccion.set_siguiente(monto), monto)

    def test_cadena_fluida_valida_pedido_normal(self) -> None:
        stock = ValidadorStock()
        stock.set_siguiente(ValidadorDireccion()).set_siguiente(
            ValidadorMontoPedido()
        ).set_siguiente(ValidadorMetodoPago())
        ok, salida = validar(stock, pedido_con_precio(100.0))
        self.assertTrue(ok)
        self.assertIn("Método de pago verificado y autorizado", salida)

    def test_cadena_fluida_corta_en_el_validador_de_monto(self) -> None:
        stock = ValidadorStock()
        stock.set_siguiente(ValidadorDireccion()).set_siguiente(
            ValidadorMontoPedido()
        ).set_siguiente(ValidadorMetodoPago())
        ok, salida = validar(stock, pedido_con_precio(1.0))
        self.assertFalse(ok)
        self.assertNotIn("Validando método de pago", salida)


class TestDemo(unittest.TestCase):
    def test_demo_valida_los_dos_pedidos(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 7. PATRÓN CHAIN OF RESPONSIBILITY <<<", salida)
        self.assertIn("=== VALIDANDO PEDIDO 1 ===", salida)
        self.assertIn("=== VALIDANDO PEDIDO 2 ===", salida)
        self.assertEqual(salida.count("PEDIDO VALIDADO EXITOSAMENTE"), 2)
        self.assertNotIn("PEDIDO RECHAZADO", salida)


if __name__ == "__main__":
    unittest.main()
