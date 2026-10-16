"""Prueba de humo de ``main.main()``: las 16 secciones salen en orden."""

import contextlib
import io
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import main  # noqa: E402


class TestMain(unittest.TestCase):
    def test_main_imprime_las_16_secciones_en_orden(self) -> None:
        salida = io.StringIO()
        with (
            mock.patch("patrones.estructural.proxy.producto_premium_real.time.sleep"),
            contextlib.redirect_stdout(salida),
        ):
            main.main()
        texto = salida.getvalue()

        numeros = [int(n) for n in re.findall(r">>> (\d+)\. PATRÓN", texto)]
        self.assertEqual(numeros, list(range(1, 17)))
        self.assertIn("FIN DE LA DEMOSTRACIÓN - 16 PATRONES IMPLEMENTADOS", texto)
        self.assertIn("Comportamiento (7)", texto)


if __name__ == "__main__":
    unittest.main()
