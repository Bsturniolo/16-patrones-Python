"""Patrón Observer - ``Cliente`` (ConcreteObserver).

Rol GoF: *ConcreteObserver*. Implementa ``actualizar`` imprimiendo el mensaje.

Java vs Python:
- ``getNombre()`` se convierte en una ``@property`` de solo lectura.
"""

from typing import override

from .observer import Observer


class Cliente(Observer):
    """Cliente suscrito a la tienda."""

    def __init__(self, nombre: str) -> None:
        self._nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @override
    def actualizar(self, mensaje: str) -> None:
        print(f"Cliente {self._nombre} recibió notificación: {mensaje}")
