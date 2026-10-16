"""Tests del patrón Singleton (DatabaseConnection)."""

import io
import threading
import time
import unittest
from contextlib import redirect_stdout
from typing import override
from unittest import mock

from patrones.creacional.singleton import DatabaseConnection
from patrones.creacional.singleton import database_connection as modulo_db
from patrones.creacional.singleton.demo import demo
from tests.ayudantes import capturar


class TestDatabaseConnection(unittest.TestCase):
    @override
    def setUp(self) -> None:
        # Aislamos cada test: reiniciamos el singleton (solo posible en tests)
        # y restauramos el estado previo al terminar para no dejar fugas.
        previa = DatabaseConnection._instance
        DatabaseConnection._instance = None
        self.addCleanup(setattr, DatabaseConnection, "_instance", previa)

    def test_dos_llamadas_devuelven_la_misma_instancia(self) -> None:
        with redirect_stdout(io.StringIO()):
            db1 = DatabaseConnection()
            db2 = DatabaseConnection()
            db3 = DatabaseConnection.get_instance()
        self.assertIs(db1, db2)
        self.assertIs(db1, db3)

    def test_mensaje_de_creacion_se_imprime_una_sola_vez(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            DatabaseConnection.get_instance()
            DatabaseConnection.get_instance()
            DatabaseConnection()
        self.assertEqual(buf.getvalue(), "Conexión a BD creada: mysql://localhost:3306/midb\n")

    def test_connection_string(self) -> None:
        with redirect_stdout(io.StringIO()):
            db = DatabaseConnection.get_instance()
        self.assertEqual(db.connection_string, "mysql://localhost:3306/midb")

    def test_query_imprime_sql(self) -> None:
        with redirect_stdout(io.StringIO()):
            db = DatabaseConnection.get_instance()
        buf = io.StringIO()
        with redirect_stdout(buf):
            db.query("SELECT * FROM usuarios")
            db.query("DELETE FROM x")
        self.assertEqual(
            buf.getvalue(),
            "Ejecutando query: SELECT * FROM usuarios\nEjecutando query: DELETE FROM x\n",
        )

    def test_thread_safety_una_sola_instancia(self) -> None:
        # Ensanchamos la ventana de la carrera: el "print" de creacion ocurre DENTRO
        # de la seccion critica, antes de asignar ``_instance``. Si lo dormimos, una
        # version sin Lock dejaria pasar a los demas hilos y crearia varias
        # instancias. Con el Lock, solo un hilo entra y el resultado es una sola.
        n = 8
        arranque = threading.Barrier(n)
        resultados: list[DatabaseConnection] = []

        def print_lento(*_args: object, **_kwargs: object) -> None:
            time.sleep(0.05)

        def tarea() -> None:
            arranque.wait(timeout=5)
            resultados.append(DatabaseConnection.get_instance())

        with mock.patch.object(modulo_db, "print", print_lento, create=True):
            hilos = [threading.Thread(target=tarea) for _ in range(n)]
            for h in hilos:
                h.start()
            for h in hilos:
                h.join()
        self.assertEqual(len(resultados), n)
        self.assertEqual(len({id(r) for r in resultados}), 1)

    def test_subclase_creada_primero_comparte_la_instancia_unica(self) -> None:
        class Replica(DatabaseConnection):
            pass

        with redirect_stdout(io.StringIO()):
            replica = Replica()
            base = DatabaseConnection()
        self.assertIs(replica, base)

    def test_subclase_creada_despues_devuelve_la_instancia_base(self) -> None:
        class Replica(DatabaseConnection):
            pass

        with redirect_stdout(io.StringIO()):
            base = DatabaseConnection()
            replica = Replica()
        self.assertIs(base, replica)


class TestDemo(unittest.TestCase):
    def test_demo_reproduce_main_java(self) -> None:
        previa = DatabaseConnection._instance
        DatabaseConnection._instance = None
        self.addCleanup(setattr, DatabaseConnection, "_instance", previa)
        self.assertEqual(
            capturar(demo),
            ">>> 1. PATRÓN SINGLETON <<<\n"
            "Conexión a BD creada: mysql://localhost:3306/midb\n"
            "¿Son la misma instancia? true\n"
            "Ejecutando query: SELECT * FROM usuarios\n\n",
        )


if __name__ == "__main__":
    unittest.main()
