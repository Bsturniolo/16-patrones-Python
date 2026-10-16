"""Patrón Prototype - ``ProductoPrototype`` (ConcretePrototype).

Java vs Python:
- Java clona con un "constructor de copia" privado y ``new HashMap<>(original)``.
- Aquí ``clonar()`` hace una copia SUPERFICIAL del objeto (``copy.copy``) y copia
  aparte el dict de especificaciones (``dict(...)``). Copia superficial significa
  que se duplica el contenedor pero NO los valores que contiene: ambos dicts
  apuntan a los mismos objetos-valor.
- Eso es suficiente aquí porque los valores son ``str`` (inmutables): nadie puede
  modificarlos "por dentro", solo reemplazarlos, y reemplazar en el clon no toca
  al original. Con un valor MUTABLE (por ejemplo una ``list``) la copia
  superficial comparte ese valor y modificarlo en el clon cambia el original.
- Para ese caso existe la copia PROFUNDA: ``clonar_profundo()`` usa
  ``copy.deepcopy``, que duplica recursivamente todo el grafo de objetos.
- ``clonar()`` usa ``copy.copy(self)``, así que el clon conserva el tipo real:
  si se hereda de ``ProductoPrototype``, el clon es de la subclase. Por eso se anota
  ``-> Self`` (``typing.Self``, 3.11+): para el verificador de tipos, ``oferta.clonar()``
  es una ``Oferta`` y no un ``ProductoPrototype`` genérico.
- ``getX/setX`` pasan a ``@property`` con setter.
- Nota Java vs Python: el orden de ``HashMap`` en Java no está definido (se imprime
  por hash); ``dict`` en Python conserva el orden de inserción, por eso el orden
  de las especificaciones impresas puede diferir de Java.
- Nota: ``especificaciones`` devuelve una copia, para no exponer el estado interno.
"""

import copy
from typing import Self, override

from .prototype import Prototype


# ``Prototype["ProductoPrototype"]``: la clase no puede nombrarse a sí misma en su propia
# lista de bases (todavía no existe), así que el argumento de tipo va entre comillas. Es la
# única "anotación" entre comillas del proyecto y no es una anotación sino una expresión.
class ProductoPrototype(Prototype["ProductoPrototype"]):
    """Producto que puede clonarse para crear variantes."""

    def __init__(self, nombre: str, precio: float, categoria: str) -> None:
        self._nombre = nombre
        self._precio = precio
        self._categoria = categoria
        self._especificaciones: dict[str, str] = {}

    @override
    def clonar(self) -> Self:
        """Copia superficial: el dict se duplica, los valores se comparten.

        Es correcto mientras los valores sean inmutables (``str``). Si hubiera
        valores mutables, usar ``clonar_profundo()``.
        """
        copia = copy.copy(self)  # conserva el tipo real (subclases incluidas)
        copia._especificaciones = dict(self._especificaciones)
        return copia

    def clonar_profundo(self) -> Self:
        """Copia profunda: nada se comparte con el original, ni valores mutables."""
        return copy.deepcopy(self)

    def agregar_especificacion(self, clave: str, valor: str) -> None:
        self._especificaciones[clave] = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nombre: str) -> None:
        self._nombre = nombre

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, precio: float) -> None:
        self._precio = precio

    @property
    def categoria(self) -> str:
        return self._categoria

    @categoria.setter
    def categoria(self, categoria: str) -> None:
        self._categoria = categoria

    @property
    def especificaciones(self) -> dict[str, str]:
        return dict(self._especificaciones)

    def mostrar_info(self) -> None:
        print(f"=== {self._nombre} ===")
        print(f"Categoría: {self._categoria}")
        print(f"Precio: ${self._precio:.2f}")
        if self._especificaciones:
            print("Especificaciones:")
            for clave, valor in self._especificaciones.items():
                print(f"  - {clave}: {valor}")
