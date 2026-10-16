"""Demostración completa de 16 patrones de diseño en Python.

Contexto: sistema de comercio electrónico (equivalente a ``Main.java``).
Ejecutar desde esta carpeta: ``python main.py``.
"""

import sys

# Guardia de versión intencional: ``requires-python = ">=3.12"`` hace que ruff la considere
# "obsoleta" (UP036), pero quien ejecute ``python main.py`` con un Python viejo (sin instalar
# el paquete) debe ver este mensaje claro y no un SyntaxError/ImportError críptico de más
# abajo (``class Prototype[T]``, ``typing.override``...).
if sys.version_info < (3, 12):  # noqa: UP036
    print(
        "Este proyecto requiere Python 3.12 o superior "
        f"(detectado {sys.version_info.major}.{sys.version_info.minor}).",
        file=sys.stderr,
    )
    sys.exit(1)

from typing import Final

from patrones.comportamiento.chain.demo import demo as demo_chain
from patrones.comportamiento.command.demo import demo as demo_command
from patrones.comportamiento.iterator.demo import demo as demo_iterator
from patrones.comportamiento.observer.demo import demo as demo_observer
from patrones.comportamiento.state.demo import demo as demo_state
from patrones.comportamiento.strategy.demo import demo as demo_strategy
from patrones.comportamiento.template.demo import demo as demo_template
from patrones.consola import configurar_utf8
from patrones.creacional.builder.demo import demo as demo_builder
from patrones.creacional.factory.demo import demo as demo_factory
from patrones.creacional.prototype.demo import demo as demo_prototype
from patrones.creacional.singleton.demo import demo as demo_singleton
from patrones.estructural.adapter.demo import demo as demo_adapter
from patrones.estructural.composite.demo import demo as demo_composite
from patrones.estructural.decorator.demo import demo as demo_decorator
from patrones.estructural.facade.demo import demo as demo_facade
from patrones.estructural.proxy.demo import demo as demo_proxy

LINEA: Final = "=" * 53


def main() -> None:
    # Fuerza UTF-8 para los caracteres en español y símbolos (como -encoding UTF-8 en Java).
    configurar_utf8()

    print(LINEA)
    print("DEMOSTRACIÓN DE 16 PATRONES DE DISEÑO EN PYTHON")
    print(LINEA + "\n")

    demo_singleton()  # 1
    demo_factory()  # 2
    demo_observer()  # 3
    demo_strategy()  # 4
    demo_decorator()  # 5
    demo_builder()  # 6
    demo_chain()  # 7
    demo_adapter()  # 8
    demo_prototype()  # 9
    demo_composite()  # 10
    demo_template()  # 11
    demo_state()  # 12
    demo_facade()  # 13
    demo_proxy()  # 14
    demo_command()  # 15
    demo_iterator()  # 16

    print("\n" + LINEA)
    print("FIN DE LA DEMOSTRACIÓN - 16 PATRONES IMPLEMENTADOS")
    print(LINEA)
    print("\nPATRONES IMPLEMENTADOS:")
    print("Creacionales (4): Singleton, Factory, Builder, Prototype")
    print("Estructurales (5): Decorator, Adapter, Composite, Facade, Proxy")
    print("Comportamiento (7): Observer, Strategy, Chain, Template, State, Command, Iterator")


if __name__ == "__main__":
    main()
