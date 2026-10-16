"""Patrón Iterator - interfaz ``Aggregate`` (la colección que sabe crear su iterador).

Rol en el patrón: declara ``crear_iterator`` (el "factory method" del iterador).

Java vs Python:
- En Python el equivalente nativo es ``__iter__`` (lo que usa ``for``). ``Catalogo``
  implementa ambos: ``crear_iterator`` (GoF) y ``__iter__`` (Python), que simplemente
  delega en el primero.
- ``interface Aggregate<T>`` -> ``class Aggregate[T](ABC)`` (genéricos PEP 695, Python
  3.12; antes: ``T = TypeVar("T")`` + ``class Aggregate(ABC, Generic[T])``). El ``T`` de
  ``Aggregate`` y el de ``Iterator`` son parámetros distintos, cada uno con alcance en su
  clase; ``Catalogo(Aggregate[ItemCatalogo])`` los fija a ambos en ``ItemCatalogo``.
"""

from abc import ABC, abstractmethod

from .iterator import Iterator


class Aggregate[T](ABC):
    """Aggregate: contrato de las colecciones iterables."""

    @abstractmethod
    def crear_iterator(self) -> Iterator[T]:
        """Crea un iterador para recorrer la colección."""
