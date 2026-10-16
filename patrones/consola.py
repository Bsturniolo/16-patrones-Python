"""Utilidades de consola compartidas por ``main.py`` y los ``demo.py``.

En Windows la consola suele usar cp1252, que no puede codificar emojis ni
caracteres como ✓. Si la salida no es UTF-8, ``print("✓")`` lanza
``UnicodeEncodeError`` (sobre todo al redirigir a un archivo o a un pipe).
"""

import sys


def configurar_utf8() -> None:
    """Fuerza UTF-8 en stdout cuando es posible.

    ``reconfigure`` solo existe en ``io.TextIOWrapper``. En IDLE, o cuando
    stdout fue reemplazado por un ``StringIO`` (por ejemplo en los tests),
    no está disponible, así que lo dejamos como está.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")
