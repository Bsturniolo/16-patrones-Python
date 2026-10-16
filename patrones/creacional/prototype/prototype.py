"""Patrón Prototype - interfaz ``Prototype`` (declara ``clonar``).

Rol: contrato para que un objeto sepa clonarse a sí mismo (``clonar()``).

Java vs Python:
- Java: ``interface Prototype<T>``. Python 3.12: ``class Prototype[T](ABC)`` (PEP 695). La
  lista ``[T]`` después del nombre declara el parámetro de tipo en la propia clase, igual
  que ``<T>`` en Java. Antes de 3.12 había que escribir::

      T = TypeVar("T")

      class Prototype(ABC, Generic[T]): ...

  La sintaxis nueva no necesita el ``TypeVar`` a nivel de módulo ni heredar de ``Generic``
  y deja el ``T`` con alcance solo dentro de la clase.
- Alternativa pythonica: el módulo ``copy`` (``copy.copy`` / ``copy.deepcopy``)
  clona cualquier objeto sin escribir código. Aquí mantenemos ``clonar()``
  explícito para mostrar el patrón GoF.
"""

from abc import ABC, abstractmethod


class Prototype[T](ABC):
    """Define el contrato para clonar objetos."""

    @abstractmethod
    def clonar(self) -> T:
        """Crea una nueva instancia con los mismos valores."""
