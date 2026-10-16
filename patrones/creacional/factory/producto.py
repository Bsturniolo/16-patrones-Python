"""Patrón Factory - ``Producto``, ``Libro``, ``Electronico`` (Product y ConcreteProducts).

Java vs Python:
- En Java, ``Producto`` es una ``abstract class`` con un método ``abstract``.
- En Python usamos ``abc.ABC`` + ``@abstractmethod``: si una subclase no implementa
  ``mostrar_info``, no se puede instanciar (TypeError), igual que en Java.
- Los getters ``getNombre()``/``getPrecio()`` se reemplazan por ``@property``:
  en Python se accede como atributo (``p.nombre``) pero sigue siendo de solo lectura.
- ``@Override`` -> ``typing.override`` en cada método que redefine uno de la base.
"""

from abc import ABC, abstractmethod
from typing import override


class Producto(ABC):
    """Clase base abstracta (el "Product" del patrón Factory)."""

    def __init__(self, nombre: str, precio: float) -> None:
        # Un guion bajo = "protegido" por convención (Python no tiene ``protected``).
        self._nombre = nombre
        self._precio = precio

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio(self) -> float:
        return self._precio

    @abstractmethod
    def mostrar_info(self) -> None:
        """Imprime la información del producto."""


class Libro(Producto):
    """Producto concreto: Libro."""

    def __init__(self, nombre: str, precio: float, autor: str) -> None:
        super().__init__(nombre, precio)
        self._autor = autor

    @property
    def autor(self) -> str:
        return self._autor

    @override
    def mostrar_info(self) -> None:
        print(f"Libro: {self._nombre} | Autor: {self._autor} | Precio: ${self._precio}")


class Electronico(Producto):
    """Producto concreto: Electrónico."""

    def __init__(self, nombre: str, precio: float, garantia_meses: int) -> None:
        super().__init__(nombre, precio)
        self._garantia_meses = garantia_meses

    @property
    def garantia_meses(self) -> int:
        return self._garantia_meses

    @override
    def mostrar_info(self) -> None:
        print(
            f"Electrónico: {self._nombre} | Garantía: {self._garantia_meses} meses "
            f"| Precio: ${self._precio}"
        )
