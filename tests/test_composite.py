"""Tests del patrón Composite."""

import unittest

from patrones.estructural.composite import (
    Categoria,
    ComponenteCatalogo,
    PaqueteProductos,
    ProductoItem,
)
from patrones.estructural.composite.demo import demo
from tests.ayudantes import capturar


class TestProductoItem(unittest.TestCase):
    def test_precio_total_es_su_precio(self) -> None:
        self.assertEqual(ProductoItem("A", 10.5, "d").precio_total, 10.5)
        self.assertEqual(ProductoItem("B", 0.0, "d").precio_total, 0.0)

    def test_nombre_precio_y_descripcion(self) -> None:
        item = ProductoItem("Mouse", 29.99, "Inalámbrico")
        self.assertEqual(
            (item.nombre, item.precio, item.descripcion), ("Mouse", 29.99, "Inalámbrico")
        )
        self.assertIsNone(ProductoItem("Sin desc", 1.0, None).descripcion)

    def test_compuestos_no_tienen_precio_propio(self) -> None:
        # ``precio`` es el precio PROPIO del componente; el de los compuestos es 0 y su valor
        # real está en ``precio_total`` (la suma recursiva de los hijos).
        categoria = Categoria("C")
        categoria.agregar(ProductoItem("A", 10.0, ""))
        paquete = PaqueteProductos("P", 10.0)
        paquete.agregar(ProductoItem("B", 20.0, ""))
        self.assertEqual((categoria.precio, categoria.precio_total), (0.0, 10.0))
        self.assertEqual(paquete.precio, 0.0)
        self.assertAlmostEqual(paquete.precio_total, 18.0)

    def test_mostrar_detalle_con_descripcion(self) -> None:
        self.assertEqual(
            capturar(ProductoItem("A", 10.5, "desc").mostrar_detalle, 1),
            "  [Producto] A - $10.50\n    Descripción: desc\n",
        )

    def test_mostrar_detalle_sin_descripcion(self) -> None:
        self.assertEqual(
            capturar(ProductoItem("A", 1.0, "").mostrar_detalle, 0), "[Producto] A - $1.00\n"
        )
        self.assertEqual(
            capturar(ProductoItem("A", 1.0, None).mostrar_detalle, 0), "[Producto] A - $1.00\n"
        )

    def test_hoja_no_soporta_agregar_ni_remover(self) -> None:
        hoja = ProductoItem("A", 1.0, "")
        with self.assertRaises(NotImplementedError):
            hoja.agregar(ProductoItem("B", 1.0, ""))
        with self.assertRaises(NotImplementedError):
            hoja.remover(ProductoItem("B", 1.0, ""))

    def test_componente_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            ComponenteCatalogo("x", 1.0)  # type: ignore[abstract]


class TestCategoria(unittest.TestCase):
    def _arbol(self) -> Categoria:
        e, c, a = Categoria("Electrónica"), Categoria("Computadoras"), Categoria("Accesorios")
        c.agregar(ProductoItem("Mac", 1000.0, "x"))
        c.agregar(ProductoItem("Dell", 500.0, "y"))
        a.agregar(ProductoItem("Mouse", 30.0, "z"))
        e.agregar(c)
        e.agregar(a)
        return e

    def test_categoria_vacia(self) -> None:
        c = Categoria("Vacía")
        self.assertEqual(c.precio_total, 0.0)
        self.assertEqual(c.cantidad_productos, 0)

    def test_total_recursivo(self) -> None:
        self.assertAlmostEqual(self._arbol().precio_total, 1530.0)

    def test_cantidad_recursiva(self) -> None:
        self.assertEqual(self._arbol().cantidad_productos, 3)

    def test_remover_actualiza_total(self) -> None:
        c = Categoria("C")
        p = ProductoItem("P", 10.0, "")
        c.agregar(p)
        c.agregar(ProductoItem("Q", 5.0, ""))
        c.remover(p)
        self.assertEqual(c.precio_total, 5.0)
        c.remover(p)  # remover un ausente se ignora, como en Java
        self.assertEqual(c.precio_total, 5.0)

    def test_hijos_devuelve_copia(self) -> None:
        c = Categoria("C")
        c.agregar(ProductoItem("P", 10.0, ""))
        c.hijos.clear()
        self.assertEqual(len(c.hijos), 1)

    def test_mostrar_detalle_indentado(self) -> None:
        s = capturar(self._arbol().mostrar_detalle, 0)
        self.assertEqual(
            s.splitlines()[:5],
            [
                "[Categoría] Electrónica (Total: $1530.00)",
                "  [Categoría] Computadoras (Total: $1500.00)",
                "    [Producto] Mac - $1000.00",
                "      Descripción: x",
                "    [Producto] Dell - $500.00",
            ],
        )


class TestPaquete(unittest.TestCase):
    def _paquete(self, desc: float = 15.0) -> PaqueteProductos:
        p = PaqueteProductos("Pack", desc)
        p.agregar(ProductoItem("A", 100.0, "a"))
        p.agregar(ProductoItem("B", 100.0, "b"))
        return p

    def test_aplica_descuento(self) -> None:
        self.assertAlmostEqual(self._paquete(15.0).precio_total, 170.0)
        self.assertAlmostEqual(self._paquete(50.0).precio_total, 100.0)
        self.assertAlmostEqual(self._paquete(0.0).precio_total, 200.0)

    def test_porcentaje_descuento(self) -> None:
        self.assertEqual(self._paquete(15.0).porcentaje_descuento, 15.0)

    def test_mostrar_detalle(self) -> None:
        s = capturar(self._paquete().mostrar_detalle, 0)
        self.assertEqual(
            s.splitlines()[:4],
            [
                "[Paquete] Pack",
                "  Descuento: 15% | Precio original: $200.00 | Precio final: $170.00"
                " | Ahorro: $30.00",
                "  Incluye:",
                "    [Producto] A - $100.00",
            ],
        )

    def test_paquete_dentro_de_categoria_suma_precio_con_descuento(self) -> None:
        c = Categoria("C")
        c.agregar(self._paquete(10.0))
        c.agregar(ProductoItem("Z", 20.0, ""))
        self.assertAlmostEqual(c.precio_total, 200.0)

    def test_paquete_anidado_descuento_compuesto(self) -> None:
        externo = PaqueteProductos("Ext", 10.0)
        externo.agregar(self._paquete(50.0))  # vale 100
        self.assertAlmostEqual(externo.precio_total, 90.0)


class TestPaqueteRemoverYValidaciones(unittest.TestCase):
    def test_remover_actualiza_total(self) -> None:
        paquete = PaqueteProductos("Pack", 10.0)
        a, b = ProductoItem("A", 100.0, ""), ProductoItem("B", 50.0, "")
        paquete.agregar(a)
        paquete.agregar(b)
        self.assertAlmostEqual(paquete.precio_total, 135.0)
        paquete.remover(a)
        self.assertAlmostEqual(paquete.precio_total, 45.0)

    def test_remover_ausente_se_ignora(self) -> None:
        paquete = PaqueteProductos("Pack", 10.0)
        paquete.agregar(ProductoItem("A", 100.0, ""))
        paquete.remover(ProductoItem("Otro", 1.0, ""))
        self.assertAlmostEqual(paquete.precio_total, 90.0)

    def test_descuento_fuera_de_rango_lanza_value_error(self) -> None:
        for invalido in (-0.1, 100.1, 150.0):
            with self.subTest(descuento=invalido), self.assertRaises(ValueError):
                PaqueteProductos("Pack", invalido)

    def test_descuento_en_los_limites_es_valido(self) -> None:
        self.assertAlmostEqual(PaqueteProductos("Gratis", 100.0).precio_total, 0.0)
        self.assertEqual(PaqueteProductos("Sin", 0.0).porcentaje_descuento, 0.0)


class TestCiclos(unittest.TestCase):
    def test_categoria_no_puede_agregarse_a_si_misma(self) -> None:
        c = Categoria("C")
        with self.assertRaises(ValueError):
            c.agregar(c)
        self.assertEqual(c.hijos, [])

    def test_paquete_no_puede_agregarse_a_si_mismo(self) -> None:
        p = PaqueteProductos("P", 5.0)
        with self.assertRaises(ValueError):
            p.agregar(p)

    def test_ciclo_indirecto_lanza_value_error(self) -> None:
        a, b, c = Categoria("A"), Categoria("B"), PaqueteProductos("C", 0.0)
        a.agregar(b)
        b.agregar(c)
        with self.assertRaises(ValueError):
            c.agregar(a)  # A -> B -> C -> A
        # sin ciclo el total sigue calculable (no hay recursion infinita)
        self.assertEqual(a.precio_total, 0.0)

    def test_mismo_componente_en_dos_ramas_no_es_ciclo(self) -> None:
        compartido = ProductoItem("X", 10.0, "")
        a, b = Categoria("A"), Categoria("B")
        a.agregar(compartido)
        b.agregar(compartido)
        raiz = Categoria("Raiz")
        raiz.agregar(a)
        raiz.agregar(b)
        self.assertEqual(raiz.precio_total, 20.0)


class TestCantidadProductosQuirk(unittest.TestCase):
    def test_no_cuenta_los_productos_dentro_de_un_paquete(self) -> None:
        # Quirk heredado de Java y documentado: solo cuenta ProductoItem y
        # Categoria anidadas; el Paquete (y sus productos) no suma.
        c = Categoria("C")
        c.agregar(ProductoItem("Suelto", 1.0, ""))
        paquete = PaqueteProductos("Pack", 0.0)
        paquete.agregar(ProductoItem("A", 1.0, ""))
        paquete.agregar(ProductoItem("B", 1.0, ""))
        c.agregar(paquete)
        self.assertEqual(c.cantidad_productos, 1)
        self.assertAlmostEqual(c.precio_total, 3.0)  # pero el precio SI los incluye


class TestDemo(unittest.TestCase):
    def test_demo(self) -> None:
        s = capturar(demo)
        self.assertTrue(
            s.startswith(">>> 10. PATRÓN COMPOSITE <<<\n\n--- Estructura del catálogo ---\n")
        )
        self.assertIn("[Categoría] Electrónica (Total: $2919.96)\n", s)
        self.assertIn(
            "Descuento: 15% | Precio original: $1439.97 | Precio final: $1223.97"
            " | Ahorro: $216.00\n",
            s,
        )
        self.assertTrue(s.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
