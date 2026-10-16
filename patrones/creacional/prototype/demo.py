"""Demostración del patrón Prototype (sección 9 de Main.java)."""

from ...consola import configurar_utf8
from .registro_prototipos import RegistroPrototipos


def demo() -> None:
    print(">>> 9. PATRÓN PROTOTYPE <<<")

    registro = RegistroPrototipos.get_instance()

    # Clonar y personalizar una laptop
    laptop1 = registro.obtener_prototipo("laptop")
    laptop1.nombre = "Laptop Gaming"
    laptop1.precio = 1299.99
    laptop1.agregar_especificacion("RAM", "16GB")
    laptop1.agregar_especificacion("GPU", "NVIDIA RTX 3060")

    print("\n--- Producto clonado y personalizado ---")
    laptop1.mostrar_info()

    # Clonar otro producto del mismo prototipo
    laptop2 = registro.obtener_prototipo("laptop")
    laptop2.nombre = "Laptop Oficina"
    laptop2.precio = 899.99

    print("\n--- Otro producto del mismo prototipo ---")
    laptop2.mostrar_info()

    # Demostrar que son instancias diferentes
    print(f"\n¿Son el mismo objeto? {str(laptop1 is laptop2).lower()}")
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
