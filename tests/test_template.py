"""Tests del patrón Template Method (ProcesadorPedido)."""

import io
import re
import unittest
from contextlib import redirect_stdout
from typing import override

from patrones.comportamiento.template import (
    ProcesadorPedido,
    ProcesadorPedidoExpress,
    ProcesadorPedidoInternacional,
    ProcesadorPedidoNacional,
)
from patrones.comportamiento.template.demo import demo
from tests.ayudantes import capturar


def procesar(procesador: ProcesadorPedido, numero: str, monto: float) -> str:
    """Salida impresa del template method completo."""
    return capturar(procesador.procesar_pedido, numero, monto)


def etiquetas(salida: str) -> list[str]:
    """Etiquetas de paso ([1], [2], [3], [3b]...) en orden de aparición."""
    return re.findall(r"^\[(\w+)\]", salida, flags=re.MULTILINE)


class TestTemplate(unittest.TestCase):
    def test_clase_base_abstracta(self) -> None:
        with self.assertRaises(TypeError):
            ProcesadorPedido()  # type: ignore[abstract]

    def test_nacional_orden_de_pasos(self) -> None:
        salida = procesar(ProcesadorPedidoNacional(), "N-1", 500.0)
        # El esqueleto: inventario, costos, pago, envío, notificación, registro.
        self.assertEqual(etiquetas(salida), ["1", "3", "2", "4", "5", "6"])

    def test_nacional_calculos(self) -> None:
        salida = procesar(ProcesadorPedidoNacional(), "N-1", 500.0)
        self.assertIn("Subtotal: $500.00", salida)
        self.assertIn("IVA (16%): $80.00", salida)
        self.assertIn("Envío: $5.00", salida)
        self.assertIn("✓ Total: $585.00", salida)
        # El pago cobra el total calculado (subtotal + IVA + envío), no el subtotal.
        self.assertIn("[2] Procesando pago de $585.00...", salida)
        self.assertNotIn("Procesando pago de $500.00", salida)

    def test_nacional_no_tiene_verificacion_adicional(self) -> None:
        self.assertNotIn("[3b]", procesar(ProcesadorPedidoNacional(), "N-1", 100.0))

    def test_internacional_ejecuta_el_hook(self) -> None:
        salida = procesar(ProcesadorPedidoInternacional(), "I-1", 750.0)
        self.assertEqual(etiquetas(salida), ["1", "3", "2", "3b", "4", "5", "6"])
        self.assertIn("Verificaciones internacionales completadas", salida)

    def test_internacional_calculos(self) -> None:
        salida = procesar(ProcesadorPedidoInternacional(), "I-1", 750.0)
        self.assertIn("IVA (16%): $120.00", salida)
        self.assertIn("Aranceles (10%): $75.00", salida)
        self.assertIn("Envío internacional: $25.00", salida)
        self.assertIn("Seguro (2%): $15.00", salida)
        self.assertIn("✓ Total: $985.00", salida)
        self.assertIn("[2] Procesando pago de $985.00...", salida)

    def test_express_sobrescribe_inventario(self) -> None:
        salida = procesar(ProcesadorPedidoExpress(), "E-1", 300.0)
        self.assertIn("[1] Verificación RÁPIDA de inventario...", salida)
        self.assertNotIn("Verificando inventario disponible", salida)
        self.assertIn("Envío Express: $15.00", salida)
        self.assertIn("✓ Total: $363.00", salida)
        self.assertIn("[2] Procesando pago de $363.00...", salida)
        self.assertNotIn("[3b]", salida)

    def test_calcular_costos_devuelve_el_total(self) -> None:
        casos = [
            (ProcesadorPedidoNacional(), 500.0, 585.0),
            (ProcesadorPedidoInternacional(), 750.0, 985.0),
            (ProcesadorPedidoExpress(), 300.0, 363.0),
            (ProcesadorPedidoNacional(), 100.0, 121.0),
        ]
        for procesador, monto, esperado in casos:
            with self.subTest(tipo=type(procesador).__name__, monto=monto):
                with redirect_stdout(io.StringIO()):
                    total = procesador.calcular_costos(monto)
                self.assertAlmostEqual(total, esperado)

    def test_el_template_method_cobra_lo_que_devuelve_calcular_costos(self) -> None:
        cobros: list[float] = []

        class ConTotalFijo(ProcesadorPedidoNacional):
            @override
            def calcular_costos(self, monto: float) -> float:
                return 1234.5

            @override
            def procesar_pago(self, monto: float) -> None:
                cobros.append(monto)

        procesar(ConTotalFijo(), "F-1", 10.0)
        self.assertEqual(cobros, [1234.5])

    def test_encabezado_y_cierre_incluyen_numero_de_pedido(self) -> None:
        salida = procesar(ProcesadorPedidoNacional(), "ORD-X", 50.0)
        self.assertTrue(salida.startswith("\n=== PROCESANDO PEDIDO ORD-X ===\n"))
        self.assertTrue(salida.endswith("=== PEDIDO ORD-X COMPLETADO ===\n\n"))
        self.assertIn("✓ Pedido ORD-X registrado", salida)

    def test_subclase_incompleta_no_se_puede_instanciar(self) -> None:
        class Incompleto(ProcesadorPedido):
            @override
            def calcular_costos(self, monto: float) -> float:
                return monto

        with self.assertRaises(TypeError):
            Incompleto()  # type: ignore[abstract]

    def test_hook_en_subclase_propia(self) -> None:
        class ConVerificacion(ProcesadorPedidoNacional):
            @override
            def requiere_verificacion_adicional(self) -> bool:
                return True

        salida = procesar(ConVerificacion(), "C-1", 10.0)
        self.assertEqual(etiquetas(salida), ["1", "3", "2", "3b", "4", "5", "6"])
        self.assertIn("[3b] Realizando verificación adicional...", salida)


class TestDemo(unittest.TestCase):
    def test_demo_procesa_los_tres_tipos_cobrando_el_total(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 11. PATRÓN TEMPLATE METHOD <<<", salida)
        for numero in ("ORD-001-NAC", "ORD-002-INT", "ORD-003-EXP"):
            self.assertIn(f"=== PEDIDO {numero} COMPLETADO ===", salida)
        self.assertIn("[2] Procesando pago de $585.00...", salida)
        self.assertIn("[2] Procesando pago de $985.00...", salida)
        self.assertIn("[2] Procesando pago de $363.00...", salida)
        self.assertEqual(salida.count("[3b]"), 1)  # solo el internacional


if __name__ == "__main__":
    unittest.main()
