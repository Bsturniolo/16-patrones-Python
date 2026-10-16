"""Tests del patrón Decorator."""

import unittest
from typing import override

from patrones.creacional.factory import Producto, ProductoFactory
from patrones.estructural.decorator import (
    EnvolturaRegaloDecorador,
    GarantiaExtendidaDecorador,
    ProductoDecorador,
    SeguroDecorador,
)
from patrones.estructural.decorator.demo import demo
from tests.ayudantes import capturar


class TestDecoradores(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.base = ProductoFactory.crear_electronico("iPad Pro", 100.0, 12)

    def test_envoltura_suma_3_50(self) -> None:
        d = EnvolturaRegaloDecorador(self.base)
        self.assertAlmostEqual(d.precio, 103.5)
        self.assertEqual(d.nombre, "iPad Pro [Con envoltura de regalo]")

    def test_seguro_suma_10_por_ciento(self) -> None:
        d = SeguroDecorador(self.base)
        self.assertAlmostEqual(d.precio, 110.0)
        self.assertEqual(d.nombre, "iPad Pro [Con seguro]")
        otro = SeguroDecorador(ProductoFactory.crear_libro("L", 20.0, "A"))
        self.assertAlmostEqual(otro.precio, 22.0)

    def test_garantia_suma_2_50_por_mes(self) -> None:
        self.assertAlmostEqual(GarantiaExtendidaDecorador(self.base, 24).precio, 160.0)
        self.assertAlmostEqual(GarantiaExtendidaDecorador(self.base, 2).precio, 105.0)
        self.assertEqual(
            GarantiaExtendidaDecorador(self.base, 24).nombre,
            "iPad Pro [Garantía extendida +24 meses]",
        )

    def test_decoradores_son_productos(self) -> None:
        d = EnvolturaRegaloDecorador(self.base)
        self.assertIsInstance(d, Producto)
        self.assertIsInstance(d, ProductoDecorador)

    def test_decorador_no_modifica_el_producto_original(self) -> None:
        SeguroDecorador(self.base)
        self.assertEqual(self.base.precio, 100.0)
        self.assertEqual(self.base.nombre, "iPad Pro")

    def test_decoradores_apilados(self) -> None:
        p = EnvolturaRegaloDecorador(GarantiaExtendidaDecorador(SeguroDecorador(self.base), 24))
        # (100 * 1.1) + 60 + 3.5
        self.assertAlmostEqual(p.precio, 173.5)
        self.assertEqual(
            p.nombre,
            "iPad Pro [Con seguro] [Garantía extendida +24 meses] [Con envoltura de regalo]",
        )

    def test_mostrar_info_envoltura(self) -> None:
        self.assertEqual(
            capturar(EnvolturaRegaloDecorador(self.base).mostrar_info),
            "Electrónico: iPad Pro | Garantía: 12 meses | Precio: $100.0\n"
            "  + Envoltura de regalo ($3.5)\n",
        )

    def test_mostrar_info_seguro_exacta(self) -> None:
        self.assertEqual(
            capturar(SeguroDecorador(self.base).mostrar_info),
            "Electrónico: iPad Pro | Garantía: 12 meses | Precio: $100.0\n"
            "  + Seguro contra daños ($10.00)\n",
        )

    def test_decorador_no_guarda_estado_copiado_que_pueda_quedar_viejo(self) -> None:
        # Nombre y precio se calculan siempre desde el envuelto: no hay copias.
        self.assertEqual(set(vars(SeguroDecorador(self.base))), {"_producto_decorado"})
        self.assertEqual(
            set(vars(GarantiaExtendidaDecorador(self.base, 3))),
            {"_producto_decorado", "_meses_extra"},
        )

    def test_mostrar_info_seguro_y_garantia(self) -> None:
        salida = capturar(SeguroDecorador(self.base).mostrar_info)
        self.assertIn("  + Seguro contra daños ($10.00)\n", salida)
        self.assertIn(
            "  + Garantía extendida +24 meses ($60.00)\n",
            capturar(GarantiaExtendidaDecorador(self.base, 24).mostrar_info),
        )

    def test_mostrar_info_apilado_en_orden(self) -> None:
        p = EnvolturaRegaloDecorador(GarantiaExtendidaDecorador(SeguroDecorador(self.base), 24))
        lineas = capturar(p.mostrar_info).splitlines()
        self.assertEqual(len(lineas), 4)
        self.assertTrue(lineas[1].startswith("  + Seguro"))
        self.assertTrue(lineas[2].startswith("  + Garantía"))
        self.assertTrue(lineas[3].startswith("  + Envoltura"))

    def test_decorador_base_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            ProductoDecorador(self.base)  # type: ignore[abstract]

    def test_nombre_y_precio_se_delegan_por_defecto(self) -> None:
        # Un decorador que solo agrega información (no cambia nombre ni precio) hereda la
        # delegación de ProductoDecorador: sigue el nombre y el precio del envuelto.
        class EtiquetaEco(ProductoDecorador):
            @override
            def mostrar_info(self) -> None:
                self._producto_decorado.mostrar_info()
                print("  + Envío con embalaje reciclado")

        eco = EtiquetaEco(SeguroDecorador(self.base))
        self.assertEqual(eco.nombre, "iPad Pro [Con seguro]")
        self.assertAlmostEqual(eco.precio, 110.0)
        self.assertTrue(capturar(eco.mostrar_info).endswith("  + Envío con embalaje reciclado\n"))


class TestDemo(unittest.TestCase):
    def test_demo(self) -> None:
        s = capturar(demo)
        self.assertTrue(s.startswith(">>> 5. PATRÓN DECORATOR <<<\n"))
        self.assertIn("Precio base: $799.99\n\n", s)
        self.assertIn("Precio total: $803.49\n\n", s)
        self.assertIn("Precio total: $1713.49\n", s)
        self.assertTrue(s.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
