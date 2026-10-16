"""Patrón Composite - ``ComponenteCatalogo`` (Component).

Rol: interfaz común para hojas (``ProductoItem``) y compuestos (``Categoria``,
``PaqueteProductos``); el cliente los trata de forma uniforme.

Java vs Python:
- ``abstract class`` -> ``abc.ABC``. ``getPrecioTotal()`` -> property ``precio_total``.
- Las operaciones de gestión de hijos (``agregar``/``remover``) lanzan por defecto
  ``UnsupportedOperationException`` en Java; el equivalente de Python es
  ``NotImplementedError``. Las hojas heredan ese comportamiento.
  Matiz: en Python ``NotImplementedError`` significa "falta implementar" (pensado
  para métodos abstractos o pendientes); para "esta operación no existe en este
  tipo de objeto" suele ser más exacto ``TypeError`` (o un error propio). Se mantiene
  ``NotImplementedError`` por su paralelismo con ``UnsupportedOperationException``.
- Validaciones agregadas respecto de Java: un componente no puede agregarse a sí
  mismo ni crear un ciclo (``ValueError``); un ciclo haría infinita la recursión de
  ``precio_total`` y ``mostrar_detalle``.
- ``from __future__ import annotations``: los métodos de la clase reciben otro
  ``ComponenteCatalogo`` (referencia a la propia clase mientras se define), así que las
  anotaciones se evalúan de forma diferida en lugar de escribirse entre comillas.
- Nota: ``%.0f`` de Java redondea half-up y ``:.0f`` de Python redondea half-even
  (solo difiere en descuentos terminados en .5).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ComponenteCatalogo(ABC):
    def __init__(self, nombre: str, precio: float) -> None:
        self._nombre = nombre
        self._precio = precio

    @abstractmethod
    def mostrar_detalle(self, nivel: int) -> None:
        """Imprime el componente con indentación según su nivel en el árbol."""

    @property
    @abstractmethod
    def precio_total(self) -> float:
        """Precio del componente (recursivo para los compuestos)."""

    def _contiene(self, otro: ComponenteCatalogo) -> bool:
        """True si ``otro`` está en el subárbol de este componente (las hojas: nunca)."""
        return False

    def _validar_nuevo_hijo(self, componente: ComponenteCatalogo) -> None:
        """Rechaza agregarse a sí mismo o crear un ciclo en el árbol."""
        if componente is self or componente._contiene(self):
            raise ValueError(
                f"No se puede agregar '{componente.nombre}' a '{self._nombre}': crearía un ciclo"
            )

    def agregar(self, componente: ComponenteCatalogo) -> None:
        raise NotImplementedError("Operación no soportada")

    def remover(self, componente: ComponenteCatalogo) -> None:
        raise NotImplementedError("Operación no soportada")

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio(self) -> float:
        return self._precio

    def _obtener_indentacion(self, nivel: int) -> str:
        return "  " * nivel
