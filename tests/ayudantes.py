"""Ayudantes compartidos por los tests (un único estilo para capturar la salida).

Casi todas las clases del proyecto *imprimen* (igual que el Java original), así que los tests
comparan lo que sale por consola. En lugar de que cada archivo defina su propia función
(``_capturar``, ``ejecutar``, ``_salida``...), todos usan estas:

- ``capturar(funcion, *args)``: ejecuta ``funcion(*args)`` y devuelve el texto impreso.
- ``capturar_con_resultado(funcion)``: igual, pero devuelve también lo que retornó la función.
- ``exigir_tipo(objeto, Tipo)``: comprueba el tipo en ejecución Y lo estrecha para mypy (un
  ``assertIsInstance`` no le dice nada al verificador de tipos).

Se importan como ``from tests.ayudantes import capturar`` (``python -m unittest discover -s
tests`` se ejecuta desde la raíz del proyecto, que queda en ``sys.path``).
"""

import io
from collections.abc import Callable
from contextlib import redirect_stdout


def capturar(funcion: Callable[..., object], *args: object) -> str:
    """Ejecuta ``funcion(*args)`` y devuelve todo lo que imprimió por stdout."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        funcion(*args)
    return buffer.getvalue()


def capturar_con_resultado[T](funcion: Callable[[], T]) -> tuple[T, str]:
    """Ejecuta ``funcion()`` y devuelve ``(lo que retornó, lo que imprimió)``."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        resultado = funcion()
    return resultado, buffer.getvalue()


def exigir_tipo[T](objeto: object, tipo: type[T]) -> T:
    """Falla el test si ``objeto`` no es un ``tipo``; si lo es, lo devuelve ya tipado."""
    if not isinstance(objeto, tipo):
        raise AssertionError(f"se esperaba {tipo.__name__}, se obtuvo {type(objeto).__name__}")
    return objeto
