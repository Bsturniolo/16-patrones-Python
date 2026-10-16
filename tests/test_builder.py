"""Tests del patrón Builder (Pedido / PedidoBuilder)."""

import unittest
from typing import Self

from patrones.creacional.builder import Pedido
from patrones.creacional.builder.demo import demo
from patrones.creacional.factory import Producto, ProductoFactory
from tests.ayudantes import capturar


def _productos() -> list[Producto]:
    return [
        ProductoFactory.crear_libro("Libro A", 10.0, "Autor"),
        ProductoFactory.crear_electronico("Tablet", 100.0, 12),
    ]


class TestPedidoBuilder(unittest.TestCase):
    def test_valores_por_defecto(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "Calle 1").construir()
        self.assertEqual(p.metodo_envio, "Standard")
        self.assertFalse(p.es_regalo)
        self.assertEqual(p.direccion_envio, "Calle 1")
        self.assertEqual(len(p.productos), 2)

    def test_metodos_fluidos_devuelven_el_mismo_builder(self) -> None:
        b = Pedido.PedidoBuilder(_productos(), "X")
        self.assertIs(b.con_metodo_envio("Express"), b)
        self.assertIs(b.con_notas_especiales("n"), b)
        self.assertIs(b.es_regalo_flag(True), b)

    def test_metodos_fluidos_conservan_el_tipo_de_un_builder_derivado(self) -> None:
        # Con ``-> Self`` el encadenamiento sigue siendo del builder derivado, así que mypy
        # acepta llamar a ``con_prioridad`` después de un método heredado.
        class BuilderConPrioridad(Pedido.PedidoBuilder):
            def con_prioridad(self) -> Self:
                return self.con_notas_especiales("PRIORITARIO")

        pedido = (
            BuilderConPrioridad(_productos(), "X")
            .con_metodo_envio("Express")
            .con_prioridad()
            .construir()
        )
        self.assertEqual(pedido.metodo_envio, "Express")
        self.assertIn("Notas especiales: PRIORITARIO", capturar(pedido.mostrar_resumen))

    def test_mensaje_regalo_activa_es_regalo(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "X").con_mensaje_regalo("Hola").construir()
        self.assertTrue(p.es_regalo)

    def test_envoltura_true_activa_regalo_pero_false_no(self) -> None:
        con = Pedido.PedidoBuilder(_productos(), "X").con_envoltura_regalo(True).construir()
        sin = Pedido.PedidoBuilder(_productos(), "X").con_envoltura_regalo(False).construir()
        self.assertTrue(con.es_regalo)
        self.assertFalse(sin.es_regalo)

    def test_total_standard(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "X").construir()
        self.assertAlmostEqual(p.calcular_total(), 115.0)

    def test_total_express_con_envoltura(self) -> None:
        p = (
            Pedido.PedidoBuilder(_productos(), "X")
            .con_metodo_envio("Express")
            .con_envoltura_regalo(True)
            .construir()
        )
        self.assertAlmostEqual(p.calcular_total(), 110.0 + 15.0 + 3.5)

    def test_total_con_metodo_desconocido_no_suma_envio(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "X").con_metodo_envio("Drone").construir()
        self.assertAlmostEqual(p.calcular_total(), 110.0)

    def test_resumen_simple(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "Calle 1").construir()
        self.assertEqual(
            capturar(p.mostrar_resumen),
            "\n=== RESUMEN DEL PEDIDO ===\n"
            "Productos:\n"
            "  - Libro A ($10.0)\n"
            "  - Tablet ($100.0)\n"
            "Dirección de envío: Calle 1\n"
            "Método de envío: Standard\n"
            "==========================\n",
        )

    def test_resumen_regalo_completo(self) -> None:
        p = (
            Pedido.PedidoBuilder(_productos(), "Calle 2")
            .con_metodo_envio("Express")
            .con_envoltura_regalo(True)
            .con_mensaje_regalo("Feliz")
            .con_notas_especiales("Mañana")
            .construir()
        )
        salida = capturar(p.mostrar_resumen)
        self.assertIn("Es un regalo: Sí\nCon envoltura de regalo\nMensaje: Feliz\n", salida)
        self.assertIn("Notas especiales: Mañana\n", salida)

    def test_resumen_regalo_sin_envoltura_ni_mensaje(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "X").es_regalo_flag(True).construir()
        salida = capturar(p.mostrar_resumen)
        self.assertIn("Es un regalo: Sí\n", salida)
        self.assertNotIn("envoltura", salida)
        self.assertNotIn("Mensaje", salida)


class TestPedidoInmutable(unittest.TestCase):
    def test_productos_es_tupla(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "X").construir()
        self.assertIsInstance(p.productos, tuple)

    def test_pedido_independiente_de_la_lista_del_llamador(self) -> None:
        lista = _productos()
        p = Pedido.PedidoBuilder(lista, "X").construir()
        lista.append(ProductoFactory.crear_libro("Extra", 1000.0, "Z"))
        self.assertEqual(len(p.productos), 2)
        self.assertAlmostEqual(p.calcular_total(), 115.0)

    def test_builder_reutilizado_no_comparte_productos_entre_pedidos(self) -> None:
        lista = _productos()
        builder = Pedido.PedidoBuilder(lista, "X")
        p1 = builder.construir()
        lista.pop()  # cambia lo que el builder ve; p1 no debe enterarse
        p2 = builder.construir()
        self.assertEqual(len(p1.productos), 2)
        self.assertIsNot(p1.productos, p2.productos)

    def test_productos_no_se_puede_modificar(self) -> None:
        p = Pedido.PedidoBuilder(_productos(), "X").construir()
        with self.assertRaises(AttributeError):
            extra = ProductoFactory.crear_libro("E", 1.0, "Z")
            p.productos.append(extra)  # type: ignore[attr-defined]


class TestDemo(unittest.TestCase):
    def test_demo_totales(self) -> None:
        salida = capturar(demo)
        self.assertTrue(salida.startswith(">>> 6. PATRÓN BUILDER <<<\n"))
        self.assertIn("Total del pedido: $830.98\n", salida)
        self.assertIn("Total del pedido: $1918.48\n", salida)
        self.assertTrue(salida.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
