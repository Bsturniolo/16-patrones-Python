"""Patrón Prototype - ``RegistroPrototipos`` (registro de prototipos, a su vez Singleton).

Rol: almacena prototipos pre-configurados y entrega SIEMPRE un clon, nunca el original.

Java vs Python:
- Java: ``private`` constructor + ``synchronized getInstance()``. Aquí se usa
  ``__new__`` con ``Lock`` (ver ``DatabaseConnection`` para la explicación).
- ``get_instance()`` se conserva con ese nombre (y no como propiedad) porque es el nombre
  GoF/Java del punto de acceso global; ``RegistroPrototipos()`` devuelve lo mismo.
- Subclases: igual que en ``DatabaseConnection``, la instancia única se guarda SIEMPRE en
  ``RegistroPrototipos._instance`` (no en ``cls._instance``). Con ``cls`` una subclase
  crearía su propio registro y habría dos "singletons"; así el primero que se construya
  (base o subclase) es la única instancia del árbol.
- Un tipo desconocido lanza ``ValueError`` (el ``IllegalArgumentException`` de Java), no
  ``KeyError``: es un *argumento* inválido de ``obtener_prototipo`` y es la misma excepción
  que usa ``ProductoFactory.crear_producto``. Además ``str(KeyError(...))`` agrega comillas
  al mensaje. ``KeyError`` sería lo natural si el registro se expusiera como un mapeo
  (``registro["laptop"]``).
- Nota: ``registrar_prototipo`` guarda la referencia recibida (como Java); si el
  llamador sigue mutando ese objeto, cambia el prototipo registrado.
"""

from __future__ import annotations

import threading
from typing import ClassVar

from .producto_prototype import ProductoPrototype


class RegistroPrototipos:
    """Registro centralizado (singleton) de prototipos."""

    _instance: ClassVar[RegistroPrototipos | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    _prototipos: dict[str, ProductoPrototype]

    def __new__(cls) -> RegistroPrototipos:
        # Siempre ``RegistroPrototipos._instance`` (no ``cls``): una sola instancia para
        # toda la jerarquía, aunque se construya primero una subclase.
        if RegistroPrototipos._instance is None:
            with RegistroPrototipos._lock:
                if RegistroPrototipos._instance is None:  # doble verificación (thread-safe)
                    instancia = super().__new__(cls)
                    instancia._prototipos = {}
                    instancia._inicializar_prototipos()
                    RegistroPrototipos._instance = instancia
        return RegistroPrototipos._instance

    @classmethod
    def get_instance(cls) -> RegistroPrototipos:
        return cls()

    def _inicializar_prototipos(self) -> None:
        # Prototipo de Laptop
        laptop_base = ProductoPrototype("Laptop Base", 799.99, "Electrónicos")
        laptop_base.agregar_especificacion("RAM", "8GB")
        laptop_base.agregar_especificacion("Almacenamiento", "256GB SSD")
        laptop_base.agregar_especificacion("Procesador", "Intel i5")
        self._prototipos["laptop"] = laptop_base

        # Prototipo de Smartphone
        phone_base = ProductoPrototype("Smartphone Base", 499.99, "Electrónicos")
        phone_base.agregar_especificacion("Pantalla", "6.1 pulgadas")
        phone_base.agregar_especificacion("Cámara", "12MP")
        phone_base.agregar_especificacion("Batería", "3000mAh")
        self._prototipos["smartphone"] = phone_base

        # Prototipo de Libro
        libro_base = ProductoPrototype("Libro Base", 19.99, "Libros")
        libro_base.agregar_especificacion("Páginas", "300")
        libro_base.agregar_especificacion("Editorial", "Editorial Genérica")
        libro_base.agregar_especificacion("Idioma", "Español")
        self._prototipos["libro"] = libro_base

    def obtener_prototipo(self, tipo: str) -> ProductoPrototype:
        prototipo = self._prototipos.get(tipo)
        if prototipo is not None:
            return prototipo.clonar()
        raise ValueError(f"Prototipo no encontrado: {tipo}")

    def registrar_prototipo(self, clave: str, prototipo: ProductoPrototype) -> None:
        self._prototipos[clave] = prototipo
