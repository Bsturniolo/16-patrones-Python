"""Demostración del patrón Singleton (sección 1 de Main.java)."""

from ...consola import configurar_utf8
from .database_connection import DatabaseConnection


def demo() -> None:
    print(">>> 1. PATRÓN SINGLETON <<<")
    db1 = DatabaseConnection.get_instance()
    db2 = DatabaseConnection.get_instance()

    # Java imprime el booleano como "true"/"false"
    print(f"¿Son la misma instancia? {str(db1 is db2).lower()}")
    db1.query("SELECT * FROM usuarios")
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
