"""Patrón Singleton - ``DatabaseConnection`` (una única conexión a la base de datos).

Rol: ``DatabaseConnection`` garantiza que exista UNA sola instancia y ofrece un
punto de acceso global (``get_instance()``).

Java vs Python:
- Java: constructor ``private`` + ``static synchronized getInstance()``.
- Python no tiene constructores privados. Aquí interceptamos la creación con
  ``__new__``: ``DatabaseConnection()`` y ``DatabaseConnection.get_instance()``
  devuelven siempre el mismo objeto. El ``Lock`` cumple el papel de ``synchronized``
  (doble verificación para no bloquear en cada acceso).
- La inicialización (y el mensaje) viven en ``__new__`` y no en ``__init__``,
  porque Python vuelve a ejecutar ``__init__`` cada vez que se "construye".
- Alternativa pythonica: un módulo ya es un singleton (se importa una sola vez),
  así que una variable a nivel de módulo suele bastar. Aquí mostramos la
  estructura GoF para que el patrón sea visible.
- ``get_instance()`` conserva el nombre GoF/Java del punto de acceso global (no es un
  getter de un atributo, por eso no se convierte en propiedad).
- Subclases: la instancia única se guarda SIEMPRE en ``DatabaseConnection`` (no en
  ``cls``). Si se escribiera ``cls._instance``, una subclase crearía su propia
  instancia y habría dos "singletons" (uno por clase). Con esta decisión, el
  primero que se construya (base o subclase) es la única instancia del árbol.
"""

from __future__ import annotations

import threading
from typing import ClassVar


class DatabaseConnection:
    """Conexión simulada a la base de datos (instancia única)."""

    _instance: ClassVar[DatabaseConnection | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    _connection_string: str

    def __new__(cls) -> DatabaseConnection:
        if DatabaseConnection._instance is None:
            with DatabaseConnection._lock:
                if DatabaseConnection._instance is None:  # doble verificación (thread-safe)
                    instancia = super().__new__(cls)
                    instancia._connection_string = "mysql://localhost:3306/midb"
                    print(f"Conexión a BD creada: {instancia._connection_string}")
                    DatabaseConnection._instance = instancia
        return DatabaseConnection._instance

    @classmethod
    def get_instance(cls) -> DatabaseConnection:
        """Equivalente a ``getInstance()`` de Java."""
        return cls()

    def query(self, sql: str) -> None:
        print(f"Ejecutando query: {sql}")

    @property
    def connection_string(self) -> str:
        return self._connection_string
