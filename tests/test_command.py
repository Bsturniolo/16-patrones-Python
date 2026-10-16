"""Tests del patrón Command (GestorPromociones y descuentos con undo/redo)."""

import unittest
from typing import override

from patrones.comportamiento.command import (
    AplicarDescuentoFijoCommand,
    AplicarDescuentoPorcentajeCommand,
    CarritoCompraCommand,
    Command,
    GestorPromociones,
    RemoverDescuentoCommand,
)
from patrones.comportamiento.command.demo import demo
from patrones.creacional.factory import Electronico
from tests.ayudantes import capturar


def carrito() -> CarritoCompraCommand:
    c = CarritoCompraCommand()
    c.agregar_producto(Electronico("Laptop HP", 899.99, 24))
    c.agregar_producto(Electronico("iPhone 15", 999.99, 12))
    c.agregar_producto(Electronico("iPad Pro", 799.99, 12))
    return c


TOTAL = 899.99 + 999.99 + 799.99


class TestCarrito(unittest.TestCase):
    def test_totales_sin_descuento(self) -> None:
        c = carrito()
        self.assertAlmostEqual(c.total_original, TOTAL)
        self.assertAlmostEqual(c.total_con_descuento, TOTAL)
        self.assertEqual(len(c.productos), 3)

    def test_descuento_porcentaje(self) -> None:
        c = carrito()
        capturar(lambda: c.aplicar_descuento_porcentaje(10, "x"))
        self.assertAlmostEqual(c.total_con_descuento, TOTAL * 0.9)
        self.assertEqual(c.descuento_aplicado, 10)

    def test_descuento_fijo_resta_el_monto(self) -> None:
        c = carrito()
        capturar(lambda: c.aplicar_descuento_fijo(100, "x"))
        self.assertAlmostEqual(c.total_con_descuento, TOTAL - 100)
        self.assertAlmostEqual(c.descuento_aplicado, 100 / TOTAL * 100)  # equivalente en %

    def test_descuento_fijo_se_guarda_como_monto_no_como_porcentaje(self) -> None:
        # Bug heredado de Java: se convertía a % del total de ese momento, así que agregar
        # productos después cambiaba lo descontado. Ahora el monto es fijo.
        c = carrito()
        capturar(lambda: c.aplicar_descuento_fijo(100, "x"))
        capturar(lambda: c.agregar_producto(Electronico("Mouse", 500.0, 12)))
        self.assertAlmostEqual(c.total_original, TOTAL + 500.0)
        self.assertAlmostEqual(c.total_con_descuento, TOTAL + 500.0 - 100)

    def test_descuento_fijo_no_deja_total_negativo(self) -> None:
        c = carrito()
        capturar(lambda: c.aplicar_descuento_fijo(TOTAL + 1000, "enorme"))
        self.assertEqual(c.total_con_descuento, 0.0)
        self.assertAlmostEqual(c.descuento_aplicado, 100.0)  # nunca más del 100 %

    def test_descuento_fijo_con_carrito_vacio_no_divide_por_cero(self) -> None:
        # Única corrección de un bug de Java que documenta el port (ahí daba Infinity/NaN).
        c = CarritoCompraCommand()
        capturar(lambda: c.aplicar_descuento_fijo(50, "cupón"))
        self.assertEqual(c.total_original, 0.0)
        self.assertEqual(c.total_con_descuento, 0.0)
        self.assertEqual(c.descuento_aplicado, 0.0)
        s = capturar(c.mostrar_resumen)
        self.assertIn("TOTAL A PAGAR: $0.00", s)
        self.assertNotIn("Descuento aplicado", s)
        # El monto quedó guardado: se aplica en cuanto hay con qué.
        capturar(lambda: c.agregar_producto(Electronico("Mouse", 80.0, 12)))
        self.assertAlmostEqual(c.total_con_descuento, 30.0)

    def test_porcentaje_fuera_de_rango_lanza_value_error(self) -> None:
        for invalido in (-0.01, 100.01, 150, float("nan")):
            with self.subTest(porcentaje=invalido), self.assertRaises(ValueError):
                carrito().aplicar_descuento_porcentaje(invalido, "x")

    def test_porcentaje_en_los_limites_es_valido(self) -> None:
        c = carrito()
        capturar(lambda: c.aplicar_descuento_porcentaje(100, "gratis"))
        self.assertEqual(c.total_con_descuento, 0.0)
        capturar(lambda: c.aplicar_descuento_porcentaje(0, "nada"))
        self.assertAlmostEqual(c.total_con_descuento, TOTAL)

    def test_monto_fijo_negativo_lanza_value_error(self) -> None:
        for invalido in (-1, -0.01, float("nan")):
            with self.subTest(monto=invalido), self.assertRaises(ValueError):
                carrito().aplicar_descuento_fijo(invalido, "x")

    def test_monto_fijo_cero_es_valido(self) -> None:
        c = carrito()
        capturar(lambda: c.aplicar_descuento_fijo(0, "x"))
        self.assertAlmostEqual(c.total_con_descuento, TOTAL)

    def test_descuento_invalido_no_altera_el_estado(self) -> None:
        c = carrito()
        capturar(lambda: c.aplicar_descuento_porcentaje(10, "ok"))
        antes = c.total_con_descuento
        with self.assertRaises(ValueError):
            c.aplicar_descuento_porcentaje(150, "mal")
        with self.assertRaises(ValueError):
            c.aplicar_descuento_fijo(-5, "mal")
        self.assertEqual(c.total_con_descuento, antes)
        self.assertEqual(c.descuento_aplicado, 10.0)

    def test_productos_devuelve_copia(self) -> None:
        c = carrito()
        c.productos.clear()
        self.assertEqual(len(c.productos), 3)

    def test_mostrar_resumen_formato(self) -> None:
        c = carrito()
        s = capturar(c.mostrar_resumen)
        self.assertIn("Productos en carrito: 3", s)
        self.assertIn("Total original: $2699.97", s)
        self.assertNotIn("Descuento aplicado", s)
        capturar(lambda: c.aplicar_descuento_porcentaje(10, "x"))
        s = capturar(c.mostrar_resumen)
        self.assertIn("Descuento aplicado: 10.0%", s)
        self.assertIn("Ahorro: $270.00", s)
        self.assertIn("TOTAL A PAGAR: $2429.97", s)


class TestUndoRedo(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.c = carrito()
        self.g = GestorPromociones()

    def ejecutar(self, cmd: Command) -> str:
        return capturar(lambda: self.g.ejecutar_comando(cmd))

    def test_ejecutar_imprime_y_registra(self) -> None:
        s = self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "Cliente frecuente"))
        self.assertIn("✓ Descuento del 10.0% aplicado (Cliente frecuente)", s)
        self.assertIn("→ Ejecutado: Aplicar descuento del 10.0% - Cliente frecuente", s)
        self.assertEqual(self.g.tamanio_historial, 1)

    def test_undo_restaura_total_exacto_sin_descuento_previo(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        s = capturar(self.g.deshacer)
        self.assertEqual(self.c.total_con_descuento, self.c.total_original)
        self.assertEqual(self.c.descuento_aplicado, 0.0)
        self.assertIn("✓ Descuento removido", s)
        self.assertIn("⟲ Comando deshecho: Aplicar descuento del 10.0% - a", s)

    def test_undo_restaura_descuento_previo(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        antes = self.c.total_con_descuento
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 15, "b"))
        self.assertAlmostEqual(self.c.total_con_descuento, TOTAL * 0.85)
        s = capturar(self.g.deshacer)
        self.assertEqual(self.c.total_con_descuento, antes)
        self.assertIn("Restauración de descuento", s)

    def test_undo_descuento_fijo(self) -> None:
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 100, "Cupón"))
        capturar(self.g.deshacer)
        self.assertEqual(self.c.total_con_descuento, self.c.total_original)
        self.assertEqual(self.c.descuento_aplicado, 0.0)

    def test_undo_descuento_fijo_restaura_el_porcentaje_previo_exacto(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        antes = self.c.total_con_descuento
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 100, "Cupón"))
        capturar(self.g.deshacer)
        self.assertEqual(self.c.total_con_descuento, antes)  # igualdad exacta, sin ruido float
        self.assertEqual(self.c.descuento_aplicado, 10.0)

    def test_undo_restaura_un_descuento_fijo_previo_como_monto(self) -> None:
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 100, "a"))
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 300, "b"))
        capturar(self.g.deshacer)
        self.assertAlmostEqual(self.c.total_con_descuento, TOTAL - 100)
        # Sigue siendo un MONTO: agregar productos no cambia lo descontado.
        capturar(lambda: self.c.agregar_producto(Electronico("Mouse", 500.0, 12)))
        self.assertAlmostEqual(self.c.total_con_descuento, TOTAL + 500.0 - 100)

    def test_undo_de_remover_restaura_un_descuento_fijo(self) -> None:
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 100, "a"))
        self.ejecutar(RemoverDescuentoCommand(self.c))
        self.assertEqual(self.c.total_con_descuento, self.c.total_original)
        capturar(self.g.deshacer)
        self.assertAlmostEqual(self.c.total_con_descuento, TOTAL - 100)

    def test_undo_remover_restaura_descuento(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 20, "a"))
        con = self.c.total_con_descuento
        self.ejecutar(RemoverDescuentoCommand(self.c))
        self.assertEqual(self.c.total_con_descuento, self.c.total_original)
        s = capturar(self.g.deshacer)
        self.assertEqual(self.c.total_con_descuento, con)
        self.assertIn("⟲ Comando deshecho: Remover descuento aplicado", s)

    def test_undo_remover_sin_descuento_previo_no_hace_nada(self) -> None:
        self.ejecutar(RemoverDescuentoCommand(self.c))
        s = capturar(self.g.deshacer)
        self.assertEqual(s, "")
        self.assertEqual(self.c.descuento_aplicado, 0.0)

    def test_undo_sin_historial_avisa(self) -> None:
        self.assertEqual(capturar(self.g.deshacer), "⚠ No hay comandos para deshacer\n")
        self.assertFalse(self.g.hay_comandos_para_deshacer())

    def test_redo_reaplica(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        aplicado = self.c.total_con_descuento
        capturar(self.g.deshacer)
        self.assertTrue(self.g.hay_comandos_para_rehacer())
        s = capturar(self.g.rehacer)
        self.assertEqual(self.c.total_con_descuento, aplicado)
        self.assertIn("↻ Rehecho: Aplicar descuento del 10.0% - a", s)
        self.assertFalse(self.g.hay_comandos_para_rehacer())

    def test_redo_sin_nada_avisa(self) -> None:
        self.assertEqual(capturar(self.g.rehacer), "⚠ No hay comandos para rehacer\n")
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        self.assertEqual(capturar(self.g.rehacer), "⚠ No hay comandos para rehacer\n")

    def test_nuevo_comando_tras_undo_descarta_redo(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 15, "b"))
        capturar(self.g.deshacer)
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 100, "c"))
        self.assertEqual(self.g.tamanio_historial, 2)
        self.assertFalse(self.g.hay_comandos_para_rehacer())
        self.assertEqual(capturar(self.g.rehacer), "⚠ No hay comandos para rehacer\n")

    def test_comando_que_falla_no_descarta_lo_deshecho(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 15, "b"))
        capturar(self.g.deshacer)
        self.assertTrue(self.g.hay_comandos_para_rehacer())

        with self.assertRaises(ValueError):
            self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 150, "inválido"))

        # El fallo no tocó el historial: el comando deshecho sigue pudiendo rehacerse.
        self.assertEqual(self.g.tamanio_historial, 2)
        self.assertTrue(self.g.hay_comandos_para_rehacer())
        capturar(self.g.rehacer)
        self.assertAlmostEqual(self.c.total_con_descuento, TOTAL * 0.85)

    def test_comando_que_falla_no_se_agrega_al_historial(self) -> None:
        with self.assertRaises(ValueError):
            self.ejecutar(AplicarDescuentoFijoCommand(self.c, -5, "inválido"))
        self.assertEqual(self.g.tamanio_historial, 0)
        self.assertFalse(self.g.hay_comandos_para_deshacer())

    def test_reutilizar_la_misma_instancia_no_rompe_el_deshacer(self) -> None:
        # GoF: si un comando puede ejecutarse varias veces, el historial guarda una COPIA
        # por ejecución; si no, la segunda ejecución pisa el estado de "deshacer" de la primera.
        diez = AplicarDescuentoPorcentajeCommand(self.c, 10, "a")
        self.ejecutar(diez)  # previo: sin descuento
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 20, "b"))  # previo: 10
        self.ejecutar(diez)  # MISMA instancia, previo: 20
        self.assertEqual(self.g.tamanio_historial, 3)

        capturar(self.g.deshacer)
        self.assertEqual(self.c.descuento_aplicado, 20.0)
        capturar(self.g.deshacer)
        self.assertEqual(self.c.descuento_aplicado, 10.0)
        capturar(self.g.deshacer)
        self.assertEqual(self.c.descuento_aplicado, 0.0)
        self.assertEqual(self.c.total_con_descuento, self.c.total_original)

    def test_historial_marcadores(self) -> None:
        s = capturar(self.g.mostrar_historial)
        self.assertIn("(vacío)", s)
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        self.ejecutar(AplicarDescuentoFijoCommand(self.c, 100, "b"))
        capturar(self.g.deshacer)
        s = capturar(self.g.mostrar_historial)
        self.assertIn("--- HISTORIAL DE PROMOCIONES ---", s)
        self.assertIn("→ [✓] 1. Aplicar descuento del 10.0% - a", s)
        self.assertIn("  [✗] 2. Aplicar descuento fijo de $100.0 - b", s)

    def test_limpiar_historial(self) -> None:
        self.ejecutar(AplicarDescuentoPorcentajeCommand(self.c, 10, "a"))
        s = capturar(self.g.limpiar_historial)
        self.assertEqual(s, "✓ Historial limpiado\n")
        self.assertEqual(self.g.tamanio_historial, 0)
        self.assertFalse(self.g.hay_comandos_para_deshacer())


class TestComandosPropios(unittest.TestCase):
    def test_comando_propio_cumple_la_interfaz(self) -> None:
        # El invoker ejecuta una COPIA del comando; el estado compartido va en el receptor.
        eventos: list[str] = []

        class Contar(Command):
            def __init__(self, registro: list[str]) -> None:
                self._registro = registro

            @override
            def ejecutar(self) -> None:
                self._registro.append("ejecutar")

            @override
            def deshacer(self) -> None:
                self._registro.append("deshacer")

            @property
            @override
            def descripcion(self) -> str:
                return "contar"

        g = GestorPromociones()
        capturar(lambda: g.ejecutar_comando(Contar(eventos)))
        self.assertEqual(eventos, ["ejecutar"])
        capturar(g.deshacer)
        self.assertEqual(eventos, ["ejecutar", "deshacer"])
        capturar(g.rehacer)
        self.assertEqual(eventos, ["ejecutar", "deshacer", "ejecutar"])

    def test_interfaz_abstracta(self) -> None:
        with self.assertRaises(TypeError):
            Command()  # type: ignore[abstract]

    def test_descripcion_es_una_propiedad_de_cada_comando(self) -> None:
        c = carrito()
        self.assertEqual(
            AplicarDescuentoPorcentajeCommand(c, 10, "a").descripcion,
            "Aplicar descuento del 10.0% - a",
        )
        self.assertEqual(
            AplicarDescuentoFijoCommand(c, 100, "b").descripcion,
            "Aplicar descuento fijo de $100.0 - b",
        )
        self.assertEqual(RemoverDescuentoCommand(c).descripcion, "Remover descuento aplicado")
        self.assertFalse(hasattr(Command, "get_descripcion"))

    def test_descripcion_abstracta_obliga_a_implementarla(self) -> None:
        class SinDescripcion(Command):
            @override
            def ejecutar(self) -> None:
                pass

            @override
            def deshacer(self) -> None:
                pass

        with self.assertRaises(TypeError):
            SinDescripcion()  # type: ignore[abstract]


class TestDemo(unittest.TestCase):
    def test_demo_aplica_deshace_y_rehace(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 15. PATRÓN COMMAND <<<", salida)
        self.assertIn("TOTAL A PAGAR: $2429.97", salida)  # 10 %
        self.assertIn("TOTAL A PAGAR: $2294.97", salida)  # 15 % reemplaza al 10 %
        self.assertIn("✓ Descuento del 10.0% aplicado (Restauración de descuento)", salida)
        self.assertIn("TOTAL A PAGAR: $2599.97", salida)  # cupón fijo de $100
        self.assertIn("--- HISTORIAL DE PROMOCIONES ---", salida)
        self.assertIn("⚠ No hay comandos para rehacer", salida)


if __name__ == "__main__":
    unittest.main()
