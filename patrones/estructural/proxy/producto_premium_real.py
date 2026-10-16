"""Patrón Proxy - ``ProductoPremiumReal`` (RealSubject: el objeto costoso con la lógica).

Rol en el patrón: su construcción simula una carga lenta (``time.sleep``).
Por eso el proxy retrasa su creación hasta que realmente hace falta.

Java vs Python:
- ``Thread.sleep(500)`` -> ``time.sleep(0.5)``. Se agrega el parámetro opcional
  ``retardo_carga`` (segundos, 0.5 por defecto como en Java) para que los tests
  no esperen medio segundo por cada objeto. Es *keyword-only* (``retardo_carga=0``).
"""

import time
from typing import override

from .producto_premium import ProductoPremium


class ProductoPremiumReal(ProductoPremium):
    """RealSubject: contiene la lógica de negocio real."""

    def __init__(
        self,
        nombre: str,
        precio: float,
        contenido_digital: str,
        *,
        retardo_carga: float = 0.5,
    ) -> None:
        self._nombre = nombre
        self._precio = precio
        self._contenido_digital = contenido_digital
        self._retardo_carga = retardo_carga
        # Simular carga costosa del producto
        self._cargar_producto()

    def _cargar_producto(self) -> None:
        print(f"⏳ Cargando producto premium: {self._nombre}...")
        time.sleep(self._retardo_carga)  # Simular tiempo de carga
        print("✓ Producto premium cargado")

    @override
    def mostrar_detalles(self) -> None:
        print("🌟 PRODUCTO PREMIUM 🌟")
        print(f"Nombre: {self._nombre}")
        print(f"Precio: ${self._precio}")
        print(f"Contenido digital incluido: {self._contenido_digital}")

    @property
    @override
    def precio(self) -> float:
        return self._precio

    @property
    @override
    def nombre(self) -> str:
        return self._nombre

    @override
    def descargar_contenido_digital(self) -> None:
        print(f"📥 Descargando: {self._contenido_digital}")
        print("✓ Descarga completada")
