"""Tests del patrón Adapter (ServicioEnvio)."""

import unittest
from typing import override

from patrones.estructural.adapter import (
    AdaptadorCorreos,
    AdaptadorDHL,
    AdaptadorFedEx,
    ServicioEnvio,
    SistemaCorreos,
    SistemaDHL,
    SistemaFedEx,
)
from patrones.estructural.adapter.demo import demo
from tests.ayudantes import capturar


class TestAdaptadores(unittest.TestCase):
    def test_todos_implementan_la_interfaz(self) -> None:
        for a in (
            AdaptadorDHL(SistemaDHL()),
            AdaptadorFedEx(SistemaFedEx()),
            AdaptadorCorreos(SistemaCorreos()),
        ):
            self.assertIsInstance(a, ServicioEnvio)

    def test_interfaz_no_instanciable(self) -> None:
        with self.assertRaises(TypeError):
            ServicioEnvio()  # type: ignore[abstract]

    def test_dhl_no_convierte_kg(self) -> None:
        s = AdaptadorDHL(SistemaDHL())
        self.assertEqual(
            capturar(s.enviar_paquete, "Madrid", 2.5),
            "DHL: Enviando paquete a Madrid\nDHL: Peso del paquete: 2.5 kg\n",
        )
        self.assertAlmostEqual(s.calcular_costo("Madrid", 2.5), 13.0)
        self.assertAlmostEqual(s.calcular_costo("Madrid", 10), 28.0)

    def test_fedex_convierte_kg_a_libras(self) -> None:
        s = AdaptadorFedEx(SistemaFedEx())
        self.assertIn("FedEx: Peso del envío: 5.51155 lbs\n", capturar(s.enviar_paquete, "X", 2.5))
        self.assertAlmostEqual(s.calcular_costo("X", 2.5), 10.0 + 2.5 * 2.20462 * 1.5)
        self.assertAlmostEqual(s.calcular_costo("X", 0), 10.0)
        self.assertAlmostEqual(s.calcular_costo("X", 1), 13.30693)

    def test_correos_convierte_kg_a_gramos(self) -> None:
        s = AdaptadorCorreos(SistemaCorreos())
        self.assertIn("Correos: Peso: 2500.0 gramos\n", capturar(s.enviar_paquete, "X", 2.5))
        self.assertAlmostEqual(s.calcular_costo("X", 2.5), 30.0)
        self.assertAlmostEqual(s.calcular_costo("X", 1), 15.0)

    def test_estados(self) -> None:
        self.assertEqual(AdaptadorDHL(SistemaDHL()).obtener_estado(), "DHL: Paquete en tránsito")
        self.assertEqual(
            AdaptadorFedEx(SistemaFedEx()).obtener_estado(), "FedEx: En camino al destino"
        )
        self.assertEqual(
            AdaptadorCorreos(SistemaCorreos()).obtener_estado(),
            "Correos: Paquete en oficina de distribución",
        )

    def test_adaptador_delega_en_el_adaptee_inyectado(self) -> None:
        class FedExFalso(SistemaFedEx):
            @override
            def get_quote(self, pounds: float) -> float:
                return pounds

        self.assertAlmostEqual(AdaptadorFedEx(FedExFalso()).calcular_costo("X", 10), 22.0462)


class TestDemo(unittest.TestCase):
    def test_demo(self) -> None:
        s = capturar(demo)
        self.assertTrue(s.startswith(">>> 8. PATRÓN ADAPTER <<<\n\n--- Envío con DHL ---\n"))
        self.assertIn("Costo: $13.00\n", s)
        self.assertIn("Costo: $18.27\n", s)
        self.assertIn("Costo: $30.00\n", s)
        self.assertTrue(s.endswith("Estado: Correos: Paquete en oficina de distribución\n"))


if __name__ == "__main__":
    unittest.main()
