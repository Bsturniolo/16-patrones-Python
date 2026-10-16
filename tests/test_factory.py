"""Tests del patrón Factory (ProductoFactory)."""

import os
import subprocess
import sys
import tempfile
import unittest
from typing import ClassVar, override
from unittest import mock

from patrones.creacional.factory import Electronico, Libro, Producto, ProductoFactory
from patrones.creacional.factory.demo import demo
from tests.ayudantes import capturar, exigir_tipo


class TestProductoFactory(unittest.TestCase):
    def test_crear_libro(self) -> None:
        libro = ProductoFactory.crear_libro("Don Quijote", 19.99, "Cervantes")
        self.assertIsInstance(libro, Libro)
        self.assertEqual(
            (libro.nombre, libro.precio, libro.autor), ("Don Quijote", 19.99, "Cervantes")
        )

    def test_crear_electronico(self) -> None:
        e = ProductoFactory.crear_electronico("Laptop HP", 899.99, 24)
        self.assertIsInstance(e, Electronico)
        self.assertEqual((e.nombre, e.precio, e.garantia_meses), ("Laptop HP", 899.99, 24))

    def test_crear_producto_libro_ignora_mayusculas(self) -> None:
        for tipo in ("libro", "LIBRO"):
            # crear_producto devuelve un ``Producto``: exigir_tipo comprueba y estrecha a Libro.
            libro = exigir_tipo(ProductoFactory.crear_producto(tipo, "L", 10.0, "Autor"), Libro)
            self.assertEqual(libro.autor, "Autor")

    def test_crear_producto_electronico_convierte_garantia(self) -> None:
        for tipo in ("electronico", "ELECTRONICO"):
            producto = ProductoFactory.crear_producto(tipo, "E", 20.0, "12")
            self.assertEqual(exigir_tipo(producto, Electronico).garantia_meses, 12)

    def test_tipo_invalido_lanza_value_error(self) -> None:
        for tipo in ("juguete", ""):
            with self.assertRaises(ValueError) as ctx:
                ProductoFactory.crear_producto(tipo, "X", 1.0, "z")
            self.assertIn("Tipo de producto no válido", str(ctx.exception))

    def test_registrar_tipo_nuevo_sin_tocar_la_fabrica(self) -> None:
        class Juguete(Producto):
            def __init__(self, nombre: str, precio: float, edad: str) -> None:
                super().__init__(nombre, precio)
                self.edad = edad

            @override
            def mostrar_info(self) -> None:
                pass

        # patch.dict restaura el registro compartido al terminar el test.
        self.enterContext(mock.patch.dict(ProductoFactory._CONSTRUCTORES))
        with self.assertRaises(ValueError):
            ProductoFactory.crear_producto("juguete", "Robot", 30.0, "8+")
        ProductoFactory.registrar("juguete", Juguete)
        producto = ProductoFactory.crear_producto("JUGUETE", "Robot", 30.0, "8+")
        juguete = exigir_tipo(producto, Juguete)
        self.assertEqual((juguete.nombre, juguete.precio, juguete.edad), ("Robot", 30.0, "8+"))

    def test_registrar_no_afecta_tipos_existentes(self) -> None:
        self.enterContext(mock.patch.dict(ProductoFactory._CONSTRUCTORES))
        ProductoFactory.registrar("Comic", Libro)  # una clase ya es un constructor válido
        self.assertIsInstance(ProductoFactory.crear_producto("comic", "C", 1.0, "A"), Libro)
        self.assertIsInstance(ProductoFactory.crear_producto("libro", "L", 1.0, "A"), Libro)
        self.assertIsInstance(
            ProductoFactory.crear_producto("electronico", "E", 1.0, "3"), Electronico
        )

    def test_registro_queda_intacto_tras_un_test_que_registra(self) -> None:
        self.assertEqual(set(ProductoFactory._CONSTRUCTORES), {"libro", "electronico"})

    def test_producto_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            Producto("a", 1.0)  # type: ignore[abstract]

    def test_mostrar_info(self) -> None:
        self.assertEqual(
            capturar(ProductoFactory.crear_libro("Don Quijote", 19.99, "Cervantes").mostrar_info)
            + capturar(ProductoFactory.crear_electronico("Laptop HP", 899.99, 24).mostrar_info),
            "Libro: Don Quijote | Autor: Cervantes | Precio: $19.99\n"
            "Electrónico: Laptop HP | Garantía: 24 meses | Precio: $899.99\n",
        )


class TestFactoryDemo(unittest.TestCase):
    def test_demo_reproduce_seccion_2(self) -> None:
        salida = capturar(demo)
        lineas = salida.split("\n")
        self.assertEqual(lineas[0], ">>> 2. PATRÓN FACTORY <<<")
        self.assertEqual(
            lineas[1],
            "Libro: Cien Años de Soledad | Autor: Gabriel García Márquez | Precio: $25.99",
        )
        self.assertEqual(lineas[4], "Electrónico: iPhone 15 | Garantía: 12 meses | Precio: $999.99")
        self.assertEqual(salida[-2:], "\n\n")


class TestDemosComoModulo(unittest.TestCase):
    """``python -m <paquete>.demo`` debe imprimir, incluso con la salida redirigida.

    Sin ``PYTHONIOENCODING`` y redirigiendo a un archivo, Windows usa cp1252 y los
    emojis fallan: ``configurar_utf8()`` en el ``__main__`` de cada demo lo evita.
    Se prueban las 16 demos (módulo -> comienzo esperado de su salida).
    """

    MODULOS: ClassVar[dict[str, str]] = {
        "patrones.creacional.singleton.demo": ">>> 1. ",
        "patrones.creacional.factory.demo": ">>> 2. ",
        "patrones.comportamiento.observer.demo": ">>> 3. ",
        "patrones.comportamiento.strategy.demo": ">>> 4. ",
        "patrones.estructural.decorator.demo": ">>> 5. ",
        "patrones.creacional.builder.demo": ">>> 6. ",
        "patrones.comportamiento.chain.demo": ">>> 7. ",
        "patrones.estructural.adapter.demo": ">>> 8. ",
        "patrones.creacional.prototype.demo": ">>> 9. ",
        "patrones.estructural.composite.demo": ">>> 10. ",
        "patrones.comportamiento.template.demo": ">>> 11. ",
        "patrones.comportamiento.state.demo": ">>> 12. ",
        "patrones.estructural.facade.demo": ">>> 13. ",
        "patrones.estructural.proxy.demo": ">>> 14. ",
        "patrones.comportamiento.command.demo": ">>> 15. ",
        "patrones.comportamiento.iterator.demo": ">>> 16. ",
    }

    def test_cada_demo_se_ejecuta_como_modulo_con_salida_redirigida(self) -> None:
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        entorno = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
        for modulo, inicio in self.MODULOS.items():
            with self.subTest(modulo=modulo), tempfile.TemporaryFile() as salida:
                proceso = subprocess.run(
                    [sys.executable, "-m", modulo],
                    cwd=raiz,
                    env=entorno,
                    stdout=salida,
                    stderr=subprocess.PIPE,
                    timeout=60,
                    check=False,  # el código de salida se comprueba abajo, con el stderr
                )
                self.assertEqual(proceso.returncode, 0, proceso.stderr.decode("utf-8", "replace"))
                salida.seek(0)
                self.assertTrue(salida.read().decode("utf-8").startswith(inicio))


if __name__ == "__main__":
    unittest.main()
