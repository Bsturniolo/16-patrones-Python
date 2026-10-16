"""Patrón Factory - ``ProductoFactory`` (Factory: centraliza la creación de productos).

Java vs Python:
- Java usa métodos ``static`` y un ``switch`` sobre un String.
- En Python las funciones de módulo ya cumplen el rol de "métodos estáticos", pero
  mantenemos la clase con ``@staticmethod`` para que la comparación sea directa.
- En lugar del ``switch`` usamos un registro a nivel de clase (``_CONSTRUCTORES``,
  un diccionario tipo -> constructor). Agregar un producto nuevo es llamar a
  ``ProductoFactory.registrar(...)`` desde afuera, SIN editar esta clase: eso sí
  cumple Open/Closed (abierta a extensión, cerrada a modificación).
- El equivalente directo del ``switch`` de Java en Python 3.10+ es la sentencia
  ``match``/``case``. Es más legible para pocos casos, pero agregar un tipo obliga
  a editar el ``match`` (no es extensible desde afuera).
"""

from collections.abc import Callable
from typing import ClassVar

from .producto import Electronico, Libro, Producto


def _crear_libro(nombre: str, precio: float, extra: str) -> Producto:
    """``extra`` es el autor."""
    return Libro(nombre, precio, extra)


def _crear_electronico(nombre: str, precio: float, extra: str) -> Producto:
    """``extra`` son los meses de garantía (llegan como texto)."""
    return Electronico(nombre, precio, int(extra))


class ProductoFactory:
    """Fábrica de productos."""

    # Registro compartido: tipo (en minúsculas) -> constructor(nombre, precio, extra).
    _CONSTRUCTORES: ClassVar[dict[str, Callable[[str, float, str], Producto]]] = {
        "libro": _crear_libro,
        "electronico": _crear_electronico,
    }

    @classmethod
    def registrar(cls, tipo: str, constructor: Callable[[str, float, str], Producto]) -> None:
        """Registra un tipo nuevo (o reemplaza uno existente). Ignora mayúsculas."""
        cls._CONSTRUCTORES[tipo.lower()] = constructor

    @staticmethod
    def crear_libro(nombre: str, precio: float, autor: str) -> Libro:
        return Libro(nombre, precio, autor)

    @staticmethod
    def crear_electronico(nombre: str, precio: float, garantia_meses: int) -> Electronico:
        return Electronico(nombre, precio, garantia_meses)

    @classmethod
    def crear_producto(cls, tipo: str, nombre: str, precio: float, extra: str) -> Producto:
        """Crea un producto a partir de su tipo registrado ("libro", "electronico", ...)."""
        try:
            constructor = cls._CONSTRUCTORES[tipo.lower()]
        except KeyError:
            raise ValueError(f"Tipo de producto no válido: {tipo}") from None
        return constructor(nombre, precio, extra)
