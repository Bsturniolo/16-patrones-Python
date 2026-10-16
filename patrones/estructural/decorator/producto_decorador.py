"""Patrón Decorator - ``ProductoDecorador`` (Decorator base abstracto).

Roles: ``Producto`` = Component; ``Libro``/``Electronico`` = ConcreteComponent;
``ProductoDecorador`` = Decorator (ES un Producto y TIENE un Producto);
los decoradores concretos añaden comportamiento y delegan en el envuelto.

Java vs Python:
- Java: ``abstract class ... extends Producto`` con campo ``protected``. Aquí
  heredamos de la ABC ``Producto`` y guardamos el envuelto en ``_producto_decorado``.
- ``getPrecio()/getNombre()`` son ``@property`` (se sobrescriben igual que en Java).
- Como en Java, ``mostrar_info`` del decorador imprime la info del producto
  envuelto y luego añade su línea; el ``nombre`` decorado solo se ve en ``.nombre``.
- No confundir: el patrón Decorator de GoF (este módulo) y la sintaxis ``@decorador``
  de Python son conceptos DISTINTOS que comparten nombre. El de GoF es una relación
  de objetos (un objeto envuelve a otro con la misma interfaz, en tiempo de
  ejecución). ``@decorador`` es una función que envuelve a otra función/clase al
  definirla. Se parecen en la idea de "envolver", pero ``@decorador`` no es una
  implementación del patrón GoF.
- Alternativa realmente pythonica a la jerarquía de decoradores: un envoltorio
  genérico con ``__getattr__`` que delegue en el objeto envuelto todo lo que el
  decorador no redefina (evita escribir un método delegador por cada operación).
  Aquí se mantiene la jerarquía GoF para que los roles sean visibles.
- Estado: este decorador NO llama a ``Producto.__init__``. Así no guarda copias de
  ``nombre``/``precio`` que podrían quedar desactualizadas: ambos se calculan
  siempre a partir del producto envuelto (las propiedades se sobrescriben).
"""

from abc import abstractmethod
from typing import override

from ...creacional.factory import Producto


class ProductoDecorador(Producto):
    """Decorador base: envuelve otro ``Producto``.

    No delega ``mostrar_info`` por defecto: es abstracto y cada decorador concreto
    debe implementarlo (normalmente llama al del envuelto y agrega su línea).
    ``nombre`` y ``precio`` sí se delegan por defecto en el producto envuelto.
    """

    def __init__(self, producto: Producto) -> None:
        # Sin ``super().__init__``: no copiamos nombre/precio (ver docstring del módulo).
        self._producto_decorado = producto

    @override
    @abstractmethod
    def mostrar_info(self) -> None:
        """Cada decorador concreto debe completar la información."""

    @property
    @override
    def precio(self) -> float:
        return self._producto_decorado.precio

    @property
    @override
    def nombre(self) -> str:
        return self._producto_decorado.nombre
