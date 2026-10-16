"""Patrón Iterator - interfaz ``Iterator`` (``has_next`` / ``next`` / ``reset`` de GoF).

Rol en el patrón: separa el *recorrido* de una colección de la colección misma.

Java vs Python (lo más didáctico del proyecto):
- En Python el patrón Iterator YA está dentro del lenguaje: el protocolo
  ``__iter__`` / ``__next__`` es el Iterator de GoF, y el ``for`` lo consume.
  Un *generador* (``yield``) construye un iterador sin escribir ninguna clase.
- Para no perder la estructura GoF, esta interfaz mantiene los tres métodos de
  Java (``has_next``, ``next``, ``reset``) y, además, implementa el protocolo
  de Python: ``__iter__`` devuelve ``self`` y ``__next__`` lanza
  ``StopIteration`` al agotarse. Así los mismos objetos funcionan con
  ``while it.has_next()`` (estilo Java) y con ``for item in it`` (estilo Python).
- Diferencia de contrato: el ``next()`` de Java/GoF devuelve ``null`` (aquí
  ``None``) al agotarse; ``__next__`` / ``next(it)`` de Python lanza
  ``StopIteration``.
- ``interface Iterator<T>`` de Java -> ``class Iterator[T](ABC)``: sintaxis de genéricos
  de Python 3.12 (PEP 695). Equivale a la forma anterior ``T = TypeVar("T")`` +
  ``class Iterator(ABC, Generic[T])``, pero sin declarar el ``TypeVar`` a nivel de módulo:
  ``T`` existe solo dentro de la clase, como el ``<T>`` de Java.
- ``__iter__`` devuelve ``Self``: un iterador concreto (``CatalogoIterator``) se devuelve a
  sí mismo con su propio tipo.
"""

from abc import ABC, abstractmethod
from typing import Self


class Iterator[T](ABC):
    """Iterator: recorre una colección sin exponer su estructura interna."""

    @abstractmethod
    def has_next(self) -> bool:
        """True si quedan elementos por recorrer."""

    @abstractmethod
    def next(self) -> T | None:
        """Devuelve el siguiente elemento (``None`` si está agotado, como Java)."""

    @abstractmethod
    def reset(self) -> None:
        """Reinicia el recorrido al principio."""

    # --- Protocolo de iteración de Python (el Iterator "nativo") -----------
    def __iter__(self) -> Self:
        return self

    def __next__(self) -> T:
        if not self.has_next():
            raise StopIteration
        item = self.next()
        assert item is not None
        return item
