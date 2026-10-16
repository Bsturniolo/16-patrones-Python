"""Demo del patrón Observer (sección 3 de Main.java)."""

from ...consola import configurar_utf8
from .cliente import Cliente
from .tienda import Tienda


def demo() -> None:
    print(">>> 3. PATRÓN OBSERVER <<<")
    tienda = Tienda("TechStore")

    cliente1 = Cliente("Juan Pérez")
    cliente2 = Cliente("María López")
    cliente3 = Cliente("Carlos Gómez")

    tienda.suscribir(cliente1)
    tienda.suscribir(cliente2)
    tienda.suscribir(cliente3)

    tienda.nueva_oferta("50% descuento en laptops")

    print()
    tienda.desuscribir(cliente2)
    print()

    tienda.nueva_oferta("Black Friday: Todo al 70% de descuento")
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
