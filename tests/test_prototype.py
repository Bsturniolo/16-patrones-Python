"""Tests del patrón Prototype."""

import threading
import time
import unittest
from typing import override
from unittest import mock

from patrones.creacional.prototype import ProductoPrototype, Prototype, RegistroPrototipos
from patrones.creacional.prototype.demo import demo
from tests.ayudantes import capturar


class TestProductoPrototype(unittest.TestCase):
    def _base(self) -> ProductoPrototype:
        p = ProductoPrototype("Base", 10.0, "Cat")
        p.agregar_especificacion("A", "1")
        return p

    def test_clon_tiene_mismos_valores(self) -> None:
        c = self._base().clonar()
        self.assertEqual((c.nombre, c.precio, c.categoria), ("Base", 10.0, "Cat"))
        self.assertEqual(c.especificaciones, {"A": "1"})

    def test_clon_es_otra_instancia(self) -> None:
        p = self._base()
        self.assertIsNot(p, p.clonar())

    def test_modificar_clon_no_afecta_original(self) -> None:
        p = self._base()
        c = p.clonar()
        c.nombre = "Otro"
        c.precio = 99.0
        c.categoria = "Z"
        self.assertEqual((p.nombre, p.precio, p.categoria), ("Base", 10.0, "Cat"))

    def test_copia_profunda_de_especificaciones(self) -> None:
        p = self._base()
        c = p.clonar()
        c.agregar_especificacion("A", "2")
        c.agregar_especificacion("B", "3")
        self.assertEqual(p.especificaciones, {"A": "1"})
        p.agregar_especificacion("C", "4")
        self.assertNotIn("C", c.especificaciones)

    def test_copia_superficial_comparte_valores_mutables(self) -> None:
        # clonar() copia el dict (superficial): las claves son independientes,
        # pero un valor MUTABLE (lista) queda compartido entre original y clon.
        p = ProductoPrototype("Base", 10.0, "Cat")
        p.agregar_especificacion("Colores", ["rojo"])  # type: ignore[arg-type]
        c = p.clonar()
        c._especificaciones["Colores"].append("azul")  # type: ignore[attr-defined]
        self.assertEqual(p._especificaciones["Colores"], ["rojo", "azul"])
        self.assertIs(p._especificaciones["Colores"], c._especificaciones["Colores"])

    def test_clonar_profundo_no_comparte_valores_mutables(self) -> None:
        p = ProductoPrototype("Base", 10.0, "Cat")
        p.agregar_especificacion("Colores", ["rojo"])  # type: ignore[arg-type]
        c = p.clonar_profundo()
        c._especificaciones["Colores"].append("azul")  # type: ignore[attr-defined]
        self.assertEqual(p._especificaciones["Colores"], ["rojo"])
        self.assertIsNot(p._especificaciones["Colores"], c._especificaciones["Colores"])
        self.assertEqual((c.nombre, c.precio, c.categoria), ("Base", 10.0, "Cat"))

    def test_clonar_respeta_la_subclase(self) -> None:
        class Oferta(ProductoPrototype):
            pass

        o = Oferta("O", 1.0, "C")
        o.agregar_especificacion("A", "1")
        # ``clonar() -> Self``: mypy acepta anotar el clon como ``Oferta`` (con
        # ``-> ProductoPrototype`` estas dos asignaciones serían un error de tipos).
        clon: Oferta = o.clonar()
        clon_profundo: Oferta = o.clonar_profundo()
        self.assertIsInstance(clon, Oferta)
        self.assertIsInstance(clon_profundo, Oferta)
        self.assertIs(type(o.clonar()), Oferta)
        self.assertIs(type(o.clonar_profundo()), Oferta)
        self.assertEqual(o.clonar().especificaciones, {"A": "1"})

    def test_especificaciones_property_devuelve_copia(self) -> None:
        p = self._base()
        p.especificaciones["X"] = "y"
        self.assertEqual(p.especificaciones, {"A": "1"})

    def test_es_un_prototype(self) -> None:
        self.assertIsInstance(self._base(), Prototype)

    def test_mostrar_info_sin_especificaciones(self) -> None:
        salida = capturar(ProductoPrototype("N", 5.0, "C").mostrar_info)
        self.assertEqual(salida, "=== N ===\nCategoría: C\nPrecio: $5.00\n")

    def test_mostrar_info_con_especificaciones(self) -> None:
        self.assertEqual(
            capturar(self._base().mostrar_info),
            "=== Base ===\nCategoría: Cat\nPrecio: $10.00\nEspecificaciones:\n  - A: 1\n",
        )


class TestRegistroPrototipos(unittest.TestCase):
    @override
    def setUp(self) -> None:
        previa = RegistroPrototipos._instance
        RegistroPrototipos._instance = None
        self.addCleanup(setattr, RegistroPrototipos, "_instance", previa)

    def test_es_singleton(self) -> None:
        self.assertIs(RegistroPrototipos(), RegistroPrototipos.get_instance())

    def test_subclase_creada_primero_comparte_la_instancia_unica(self) -> None:
        # Mismo criterio que DatabaseConnection: la instancia vive en la clase base, así
        # que una subclase no crea un segundo "singleton".
        class RegistroExtendido(RegistroPrototipos):
            pass

        extendido = RegistroExtendido()
        self.assertIs(extendido, RegistroPrototipos())
        self.assertIs(extendido, RegistroPrototipos.get_instance())

    def test_subclase_creada_despues_devuelve_la_instancia_base(self) -> None:
        class RegistroExtendido(RegistroPrototipos):
            pass

        base = RegistroPrototipos()
        self.assertIs(RegistroExtendido(), base)
        self.assertIs(RegistroExtendido.get_instance(), base)

    def test_thread_safety_un_solo_registro(self) -> None:
        # Se ensancha la ventana de la carrera: la carga de prototipos ocurre DENTRO de la
        # sección crítica, antes de publicar la instancia. Sin el Lock (o sin la segunda
        # verificación) varios hilos crearían su propio registro.
        n = 8
        arranque = threading.Barrier(n)
        resultados: list[RegistroPrototipos] = []
        cargar_original = RegistroPrototipos._inicializar_prototipos

        def cargar_lento(registro: RegistroPrototipos) -> None:
            time.sleep(0.05)
            cargar_original(registro)

        def tarea() -> None:
            arranque.wait(timeout=5)
            resultados.append(RegistroPrototipos.get_instance())

        with mock.patch.object(RegistroPrototipos, "_inicializar_prototipos", cargar_lento):
            hilos = [threading.Thread(target=tarea) for _ in range(n)]
            for hilo in hilos:
                hilo.start()
            for hilo in hilos:
                hilo.join()
        self.assertEqual(len(resultados), n)
        self.assertEqual(len({id(r) for r in resultados}), 1)
        self.assertEqual(resultados[0].obtener_prototipo("laptop").nombre, "Laptop Base")

    def test_prototipos_predefinidos(self) -> None:
        r = RegistroPrototipos.get_instance()
        laptop = r.obtener_prototipo("laptop")
        self.assertEqual(
            (laptop.nombre, laptop.precio, laptop.categoria),
            ("Laptop Base", 799.99, "Electrónicos"),
        )
        self.assertEqual(laptop.especificaciones["RAM"], "8GB")
        phone = r.obtener_prototipo("smartphone")
        self.assertEqual(phone.precio, 499.99)
        libro = r.obtener_prototipo("libro")
        self.assertEqual((libro.categoria, libro.especificaciones["Páginas"]), ("Libros", "300"))

    def test_obtener_devuelve_clones_independientes(self) -> None:
        r = RegistroPrototipos.get_instance()
        a = r.obtener_prototipo("laptop")
        a.nombre = "Gaming"
        a.agregar_especificacion("RAM", "16GB")
        b = r.obtener_prototipo("laptop")
        self.assertIsNot(a, b)
        self.assertEqual(b.nombre, "Laptop Base")
        self.assertEqual(b.especificaciones["RAM"], "8GB")

    def test_prototipo_inexistente(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            RegistroPrototipos.get_instance().obtener_prototipo("tablet")
        self.assertEqual(str(ctx.exception), "Prototipo no encontrado: tablet")

    def test_registrar_prototipo_nuevo(self) -> None:
        r = RegistroPrototipos.get_instance()
        r.registrar_prototipo("tablet", ProductoPrototype("Tablet Base", 300.0, "Electrónicos"))
        self.assertEqual(r.obtener_prototipo("tablet").nombre, "Tablet Base")


class TestDemo(unittest.TestCase):
    def test_demo(self) -> None:
        previa = RegistroPrototipos._instance
        RegistroPrototipos._instance = None
        self.addCleanup(setattr, RegistroPrototipos, "_instance", previa)
        s = capturar(demo)
        self.assertTrue(s.startswith(">>> 9. PATRÓN PROTOTYPE <<<\n"))
        self.assertIn("=== Laptop Gaming ===", s)
        self.assertIn("Precio: $1299.99", s)
        self.assertIn("=== Laptop Oficina ===", s)
        self.assertIn("  - RAM: 8GB", s)
        self.assertIn("¿Son el mismo objeto? false\n\n", s)


if __name__ == "__main__":
    unittest.main()
