"""Patrón Proxy - interfaz ``ProductoPremium`` (Subject común de RealSubject y Proxy).

Rol en el patrón: el cliente solo conoce ``ProductoPremium``; no sabe si habla
con el objeto real o con su sustituto (proxy).

Java vs Python:
- ``interface`` de Java -> ``abc.ABC`` con métodos abstractos.
- ``getNombre()``/``getPrecio()`` -> propiedades de solo lectura ``nombre``/``precio``.
"""

from abc import ABC, abstractmethod


class ProductoPremium(ABC):
    """Subject: contrato compartido por el objeto real y el proxy."""

    @abstractmethod
    def mostrar_detalles(self) -> None:
        """Muestra los detalles del producto."""

    @property
    @abstractmethod
    def precio(self) -> float:
        """Precio del producto."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre del producto."""

    @abstractmethod
    def descargar_contenido_digital(self) -> None:
        """Descarga el contenido digital asociado."""
