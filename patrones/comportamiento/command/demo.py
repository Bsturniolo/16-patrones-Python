"""Demostración del patrón Command (sección 15 de Main.java).

En Main.java los productos ``laptop``, ``telefono`` y ``tablet`` se crean en
secciones anteriores (Factory / Decorator); aquí se recrean con los mismos datos.
"""

from ...consola import configurar_utf8
from ...creacional.factory import Electronico
from .aplicar_descuento_fijo_command import AplicarDescuentoFijoCommand
from .aplicar_descuento_porcentaje_command import AplicarDescuentoPorcentajeCommand
from .carrito_compra_command import CarritoCompraCommand
from .command import Command
from .gestor_promociones import GestorPromociones


def demo() -> None:
    print(">>> 15. PATRÓN COMMAND <<<")

    laptop = Electronico("Laptop HP", 899.99, 24)
    telefono = Electronico("iPhone 15", 999.99, 12)
    tablet = Electronico("iPad Pro", 799.99, 12)

    # Crear carrito para comandos
    carrito_cmd = CarritoCompraCommand()
    carrito_cmd.agregar_producto(laptop)
    carrito_cmd.agregar_producto(telefono)
    carrito_cmd.agregar_producto(tablet)

    print("\n--- Carrito inicial ---")
    carrito_cmd.mostrar_resumen()

    # Crear gestor de promociones
    gestor = GestorPromociones()

    # Aplicar descuento del 10%
    descuento10: Command = AplicarDescuentoPorcentajeCommand(carrito_cmd, 10, "Cliente frecuente")
    gestor.ejecutar_comando(descuento10)
    carrito_cmd.mostrar_resumen()

    # Segundo descuento (15 %): REEMPLAZA al de 10 %, no se acumula (en Java la variable
    # se llama descuento5 pero aplica 15 %)
    descuento5: Command = AplicarDescuentoPorcentajeCommand(carrito_cmd, 15, "Black Friday")
    gestor.ejecutar_comando(descuento5)
    carrito_cmd.mostrar_resumen()

    # Deshacer último descuento
    print("--- Deshaciendo último descuento ---")
    gestor.deshacer()
    carrito_cmd.mostrar_resumen()

    # Aplicar descuento fijo
    descuento_fijo: Command = AplicarDescuentoFijoCommand(carrito_cmd, 100, "Cupón especial")
    gestor.ejecutar_comando(descuento_fijo)
    carrito_cmd.mostrar_resumen()

    # Mostrar historial
    gestor.mostrar_historial()

    # Rehacer
    print("--- Rehaciendo descuento ---")
    gestor.rehacer()
    carrito_cmd.mostrar_resumen()


if __name__ == "__main__":
    configurar_utf8()
    demo()
