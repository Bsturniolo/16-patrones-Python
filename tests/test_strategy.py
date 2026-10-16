"""Tests del patrón Strategy (CarritoCompra + EstrategiaPago)."""

import unittest
from typing import override

from patrones.comportamiento.strategy import (
    CarritoCompra,
    EstrategiaPago,
    PagoEfectivo,
    PagoPayPal,
    PagoTarjeta,
)
from patrones.comportamiento.strategy.demo import demo
from patrones.creacional.factory import ProductoFactory
from tests.ayudantes import capturar


class TestEstrategias(unittest.TestCase):
    def test_interfaz_abstracta(self) -> None:
        with self.assertRaises(TypeError):
            EstrategiaPago()  # type: ignore[misc]  # un Protocol no se instancia

    def test_subclase_explicita_incompleta_no_se_instancia(self) -> None:
        # Subclasificar el Protocol de forma explícita es opcional, pero si se hace,
        # ``@abstractmethod`` obliga a implementar ``pagar``.
        class SinPagar(EstrategiaPago):
            pass

        with self.assertRaises(TypeError):
            SinPagar()  # type: ignore[abstract]

    def test_tarjeta_muestra_ultimos_cuatro_digitos(self) -> None:
        self.assertEqual(
            capturar(PagoTarjeta("4532-1234-5678-9012").pagar, 100.0),
            "Pagando $100.0 con tarjeta terminada en 9012\n",
        )
        self.assertEqual(
            capturar(PagoTarjeta("0000111122223333").pagar, 5.5),
            "Pagando $5.5 con tarjeta terminada en 3333\n",
        )

    def test_efectivo_aplica_5_por_ciento(self) -> None:
        self.assertEqual(
            capturar(PagoEfectivo().pagar, 100.0),
            "Pagando $100.0 en efectivo. Se aplicó 5% descuento.\nTotal a pagar: $95.00\n",
        )
        self.assertIn("Total a pagar: $190.00", capturar(PagoEfectivo().pagar, 200.0))

    def test_paypal_muestra_cuenta(self) -> None:
        self.assertEqual(
            capturar(PagoPayPal("a@b.com").pagar, 10.5),
            "Pagando $10.5 con PayPal desde la cuenta: a@b.com\n",
        )


class TestCarritoCompra(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.libro = ProductoFactory.crear_libro("Don Quijote", 19.99, "Cervantes")
        self.laptop = ProductoFactory.crear_electronico("Laptop HP", 899.99, 24)

    def test_agregar_producto_imprime(self) -> None:
        carrito = CarritoCompra()
        self.assertEqual(
            capturar(carrito.agregar_producto, self.libro),
            "Producto agregado al carrito: Don Quijote\n",
        )

    def test_calcular_total(self) -> None:
        carrito = CarritoCompra()
        self.assertEqual(carrito.calcular_total(), 0.0)
        capturar(carrito.agregar_producto, self.libro)
        capturar(carrito.agregar_producto, self.laptop)
        self.assertAlmostEqual(carrito.calcular_total(), 919.98)

    def test_estrategia_pago_es_none_hasta_asignarla(self) -> None:
        carrito = CarritoCompra()
        self.assertIsNone(carrito.estrategia_pago)
        efectivo = PagoEfectivo()
        carrito.estrategia_pago = efectivo
        self.assertIs(carrito.estrategia_pago, efectivo)

    def test_estrategia_pago_es_una_propiedad_con_setter(self) -> None:
        # Java: setEstrategiaPago(...). Python: propiedad (``carrito.estrategia_pago = x``).
        atributo = vars(CarritoCompra)["estrategia_pago"]
        self.assertIsInstance(atributo, property)
        self.assertIsNotNone(atributo.fset)
        self.assertFalse(hasattr(CarritoCompra, "set_estrategia_pago"))

    def test_checkout_carrito_vacio(self) -> None:
        carrito = CarritoCompra()
        carrito.estrategia_pago = PagoEfectivo()
        self.assertEqual(capturar(carrito.checkout), "El carrito está vacío\n")

    def test_checkout_sin_estrategia(self) -> None:
        carrito = CarritoCompra()
        capturar(carrito.agregar_producto, self.libro)
        self.assertEqual(capturar(carrito.checkout), "Debe seleccionar un método de pago\n")

    def test_checkout_completo_con_efectivo(self) -> None:
        carrito = CarritoCompra()
        capturar(carrito.agregar_producto, self.libro)
        carrito.estrategia_pago = PagoEfectivo()
        salida = capturar(carrito.checkout)
        self.assertIn("\n=== CHECKOUT ===\n", salida)
        self.assertIn("Libro: Don Quijote | Autor: Cervantes | Precio: $19.99", salida)
        self.assertIn("Total: $19.99\n", salida)
        self.assertIn("Total a pagar: $18.99", salida)  # 19.99 * 0.95 = 18.9905
        self.assertTrue(salida.endswith("¡Compra completada!\n\n"))

    def test_cambiar_estrategia_en_tiempo_de_ejecucion(self) -> None:
        carrito = CarritoCompra()
        capturar(carrito.agregar_producto, self.laptop)
        carrito.estrategia_pago = PagoTarjeta("1111222233334444")
        self.assertIn("tarjeta terminada en 4444", capturar(carrito.checkout))
        carrito.estrategia_pago = PagoPayPal("x@y.com")
        salida = capturar(carrito.checkout)
        self.assertIn("PayPal", salida)
        self.assertNotIn("tarjeta", salida)

    def test_estrategia_duck_typing(self) -> None:
        # Tipado estructural (``typing.Protocol``): Espia NO hereda de EstrategiaPago,
        # pero tiene ``pagar(monto)`` y por eso el type checker también lo acepta.
        pagos: list[float] = []

        class Espia:
            def pagar(self, monto: float) -> None:
                pagos.append(monto)

        espia: EstrategiaPago = Espia()  # type-correct: compatibilidad estructural
        carrito = CarritoCompra()
        capturar(carrito.agregar_producto, self.libro)
        carrito.estrategia_pago = espia
        capturar(carrito.checkout)
        self.assertEqual(pagos, [19.99])


class TestDemo(unittest.TestCase):
    def test_demo_cobra_con_las_tres_estrategias(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 4. PATRÓN STRATEGY <<<", salida)
        self.assertIn("Pagando $925.98 con tarjeta terminada en 9012", salida)
        self.assertIn("en efectivo. Se aplicó 5% descuento.", salida)
        self.assertIn("Pagando $1899.98 con PayPal desde la cuenta: usuario@email.com", salida)
        self.assertEqual(salida.count("¡Compra completada!"), 3)


if __name__ == "__main__":
    unittest.main()
