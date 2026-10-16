"""Tests del patrón Iterator (Catalogo y sus iteradores)."""

import unittest

from patrones.comportamiento.iterator import Catalogo, ItemCatalogo, Iterator
from patrones.comportamiento.iterator.demo import demo
from tests.ayudantes import capturar


def catalogo() -> Catalogo:
    c = Catalogo("Tecnología 2025")
    for args in [
        ("MacBook Pro M3", 1999.99, "Laptops", True, 5),
        ("Dell XPS 15", 1599.99, "Laptops", True, 4),
        ("HP Pavilion", 899.99, "Laptops", False, 3),
        ("iPhone 15 Pro", 1199.99, "Smartphones", True, 5),
        ("Samsung S24 Ultra", 1099.99, "Smartphones", True, 5),
        ("Google Pixel 8", 699.99, "Smartphones", True, 4),
        ("iPad Pro", 899.99, "Tablets", True, 5),
        ("Surface Pro", 799.99, "Tablets", False, 4),
        ("Mouse MX Master", 99.99, "Accesorios", True, 5),
        ("Teclado Mecánico", 149.99, "Accesorios", True, 4),
    ]:
        c.agregar_item(ItemCatalogo(*args))
    return c


def nombres(it: Iterator[ItemCatalogo]) -> list[str]:
    return [item.nombre for item in it]


class TestItemCatalogo(unittest.TestCase):
    def test_popularidad_se_acota_entre_1_y_5(self) -> None:
        self.assertEqual(ItemCatalogo("a", 1, "c", True, 9).popularidad, 5)
        self.assertEqual(ItemCatalogo("a", 1, "c", True, 0).popularidad, 1)
        self.assertEqual(ItemCatalogo("a", 1, "c", True, 3).popularidad, 3)

    def test_mostrar_info_formato(self) -> None:
        s = capturar(ItemCatalogo("Mouse", 99.99, "Accesorios", True, 4).mostrar_info)
        self.assertEqual(s, f"{'Mouse':<30} ${'99.99':<8} [Accesorios] ★★★★☆ ✓ En stock\n")
        s = capturar(ItemCatalogo("X", 5, "C", False, 1).mostrar_info)
        self.assertIn("★☆☆☆☆ ✗ Agotado", s)

    def test_str(self) -> None:
        self.assertEqual(str(ItemCatalogo("Mouse", 99.99, "Acc", True, 4)), "Mouse ($99.99) - Acc")


class TestIteradorBasico(unittest.TestCase):
    def test_recorre_todo_en_orden(self) -> None:
        n = nombres(catalogo().crear_iterator())
        self.assertEqual(len(n), 10)
        self.assertEqual(n[0], "MacBook Pro M3")
        self.assertEqual(n[-1], "Teclado Mecánico")

    def test_agotado_next_devuelve_none(self) -> None:
        c = Catalogo("x")
        it = c.crear_iterator()
        self.assertFalse(it.has_next())
        self.assertIsNone(it.next())
        c.agregar_item(ItemCatalogo("a", 1, "c", True, 1))
        it = c.crear_iterator()
        it.next()
        self.assertIsNone(it.next())

    def test_reset_reinicia(self) -> None:
        it = catalogo().crear_iterator()
        primero = nombres(it)
        self.assertFalse(it.has_next())
        it.reset()
        self.assertEqual(nombres(it), primero)

    def test_iteradores_independientes(self) -> None:
        c = catalogo()
        a, b = c.crear_iterator(), c.crear_iterator()
        a.next()
        a.next()
        self.assertEqual(next(b).nombre, "MacBook Pro M3")
        self.assertEqual(next(a).nombre, "HP Pavilion")

    def test_remover_item(self) -> None:
        c = catalogo()
        item = ItemCatalogo("Z", 1, "c", True, 1)
        c.agregar_item(item)
        self.assertEqual(c.tamanio, 11)
        c.remover_item(item)
        self.assertEqual(c.tamanio, 10)

    def test_remover_item_ausente_se_ignora(self) -> None:
        # Java: List.remove ignora un elemento ausente; list.remove de Python lanzaría.
        c = catalogo()
        c.remover_item(ItemCatalogo("No está", 1, "c", True, 1))
        self.assertEqual(c.tamanio, 10)

    def test_nombre_catalogo(self) -> None:
        self.assertEqual(catalogo().nombre_catalogo, "Tecnología 2025")
        self.assertEqual(Catalogo("Ofertas").nombre_catalogo, "Ofertas")


class TestFiltros(unittest.TestCase):
    def test_por_categoria(self) -> None:
        self.assertEqual(
            nombres(catalogo().crear_iterator_por_categoria("Laptops")),
            ["MacBook Pro M3", "Dell XPS 15", "HP Pavilion"],
        )
        # equalsIgnoreCase en Java
        self.assertEqual(len(nombres(catalogo().crear_iterator_por_categoria("tablets"))), 2)
        self.assertEqual(nombres(catalogo().crear_iterator_por_categoria("Nada")), [])

    def test_en_stock(self) -> None:
        n = nombres(catalogo().crear_iterator_en_stock())
        self.assertEqual(len(n), 8)
        self.assertNotIn("HP Pavilion", n)
        self.assertNotIn("Surface Pro", n)

    def test_por_precio_rango_inclusivo(self) -> None:
        n = nombres(catalogo().crear_iterator_por_precio(500, 1000))
        self.assertEqual(n, ["HP Pavilion", "Google Pixel 8", "iPad Pro", "Surface Pro"])
        n = nombres(catalogo().crear_iterator_por_precio(99.99, 149.99))
        self.assertEqual(n, ["Mouse MX Master", "Teclado Mecánico"])

    def test_filtro_reset(self) -> None:
        it = catalogo().crear_iterator_en_stock()
        nombres(it)
        it.reset()
        self.assertEqual(len(nombres(it)), 8)

    def test_popularidad_descendente_y_estable(self) -> None:
        n = nombres(catalogo().crear_iterator_por_popularidad())
        self.assertEqual(
            n[:5],
            ["MacBook Pro M3", "iPhone 15 Pro", "Samsung S24 Ultra", "iPad Pro", "Mouse MX Master"],
        )
        pops = [i.popularidad for i in catalogo().crear_iterator_por_popularidad()]
        self.assertEqual(pops, sorted(pops, reverse=True))

    def test_popularidad_no_altera_catalogo(self) -> None:
        c = catalogo()
        nombres(c.crear_iterator_por_popularidad())
        self.assertEqual(nombres(c.crear_iterator())[0], "MacBook Pro M3")


class TestProtocoloPython(unittest.TestCase):
    def test_for_sobre_iterador(self) -> None:
        self.assertEqual(
            [i.nombre for i in catalogo().crear_iterator_por_categoria("Tablets")],
            ["iPad Pro", "Surface Pro"],
        )

    def test_for_sobre_catalogo(self) -> None:
        c = catalogo()
        self.assertEqual(len(list(c)), 10)
        # Cada for crea un iterador nuevo: se puede recorrer varias veces.
        self.assertEqual(len(list(c)), 10)

    def test_next_builtin_lanza_stop_iteration(self) -> None:
        it = catalogo().crear_iterator_por_categoria("Tablets")
        next(it)
        next(it)
        with self.assertRaises(StopIteration):
            next(it)
        with self.assertRaises(StopIteration):
            next(it)

    def test_iter_devuelve_si_mismo(self) -> None:
        it = catalogo().crear_iterator()
        self.assertIs(iter(it), it)

    def test_generador_equivalente(self) -> None:
        c = catalogo()
        self.assertEqual(
            [i.nombre for i in c.items_por_categoria("Laptops")],
            nombres(c.crear_iterator_por_categoria("Laptops")),
        )
        self.assertEqual(
            [i.nombre for i in c.items_en_stock()], nombres(c.crear_iterator_en_stock())
        )

    def test_len(self) -> None:
        self.assertEqual(len(catalogo()), 10)

    def test_generador_por_precio_equivale_al_iterador(self) -> None:
        c = catalogo()
        esperado = ["HP Pavilion", "Google Pixel 8", "iPad Pro", "Surface Pro"]
        self.assertEqual([i.nombre for i in c.items_por_precio(500, 1000)], esperado)
        self.assertEqual(nombres(c.crear_iterator_por_precio(500, 1000)), esperado)
        # Extremos inclusivos y rango vacío
        self.assertEqual(
            [i.nombre for i in c.items_por_precio(99.99, 149.99)],
            ["Mouse MX Master", "Teclado Mecánico"],
        )
        self.assertEqual(list(c.items_por_precio(5000, 6000)), [])

    def test_generador_por_popularidad_equivale_al_iterador(self) -> None:
        c = catalogo()
        por_generador = [i.nombre for i in c.items_por_popularidad()]
        self.assertEqual(por_generador, nombres(c.crear_iterator_por_popularidad()))
        self.assertEqual(
            por_generador[:5],
            ["MacBook Pro M3", "iPhone 15 Pro", "Samsung S24 Ultra", "iPad Pro", "Mouse MX Master"],
        )
        self.assertEqual(por_generador[-1], "HP Pavilion")  # la única de 3 estrellas
        self.assertEqual(len(por_generador), 10)


class TestPerezosoVsSnapshot(unittest.TestCase):
    """Los iteradores GoF filtrados son una foto fija; los generadores son perezosos."""

    def nuevo_en_stock(self) -> ItemCatalogo:
        return ItemCatalogo("Nuevo", 10.0, "Accesorios", True, 1)

    def test_iterador_filtrado_es_snapshot_al_crearse(self) -> None:
        c = catalogo()
        iterador = c.crear_iterator_en_stock()
        c.agregar_item(self.nuevo_en_stock())
        self.assertEqual(len(nombres(iterador)), 8)  # no ve el item agregado después

    def test_generador_no_hace_nada_hasta_el_primer_next(self) -> None:
        c = catalogo()
        generador = c.items_en_stock()
        c.agregar_item(self.nuevo_en_stock())  # antes de empezar a recorrer
        self.assertEqual(len(list(generador)), 9)  # sí lo ve

    def test_generador_ve_los_cambios_durante_el_recorrido(self) -> None:
        c = catalogo()
        generador = c.items_en_stock()
        next(generador)
        c.agregar_item(self.nuevo_en_stock())  # a mitad del recorrido
        self.assertIn("Nuevo", [i.nombre for i in generador])

    def test_iterador_basico_comparte_la_lista_del_catalogo(self) -> None:
        c = catalogo()
        iterador = c.crear_iterator()
        c.agregar_item(self.nuevo_en_stock())
        self.assertEqual(len(nombres(iterador)), 11)  # no copia: ve el item nuevo

    def test_popularidad_precalcula_todo_al_primer_next(self) -> None:
        # ``sorted`` necesita ver todos los elementos: la "pereza" solo alcanza hasta el
        # primer ``next``. Los cambios posteriores ya no se reflejan.
        c = catalogo()
        generador = c.items_por_popularidad()
        next(generador)
        c.agregar_item(ItemCatalogo("Nuevo", 10.0, "Accesorios", True, 5))
        self.assertNotIn("Nuevo", [i.nombre for i in generador])

    def test_popularidad_antes_del_primer_next_si_ve_los_cambios(self) -> None:
        c = catalogo()
        generador = c.items_por_popularidad()
        c.agregar_item(ItemCatalogo("Nuevo", 10.0, "Accesorios", True, 5))
        self.assertIn("Nuevo", [i.nombre for i in generador])


class TestMostrarCatalogo(unittest.TestCase):
    def test_salida(self) -> None:
        s = capturar(catalogo().mostrar_catalogo)
        self.assertIn("📚 CATÁLOGO: Tecnología 2025", s)
        self.assertIn("Total de productos: 10", s)
        self.assertIn(
            f"║  {'MacBook Pro M3':<30} ${'1999.99':<9} {'Laptops':<12} ★★★★★      ✓      ║", s
        )
        self.assertTrue(s.startswith("\n╔"))


class TestDemo(unittest.TestCase):
    def test_demo_recorre_con_todos_los_iteradores(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 16. PATRÓN ITERATOR <<<", salida)
        self.assertIn("--- Filtrar por categoría: Laptops ---", salida)
        self.assertIn("Total en stock: 8", salida)
        self.assertIn("--- Ordenar por popularidad (Top 5) ---", salida)
        self.assertIn("1. MacBook Pro M3", salida)
        self.assertIn("5. Mouse MX Master", salida)
        numeradas = {"1.", "2.", "3.", "4.", "5.", "6."}
        posiciones = [linea[:2] for linea in salida.splitlines() if linea[:2] in numeradas]
        self.assertEqual(posiciones, ["1.", "2.", "3.", "4.", "5."])  # solo el Top 5


if __name__ == "__main__":
    unittest.main()
