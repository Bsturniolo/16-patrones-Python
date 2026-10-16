"""Patrón Observer: notificación uno-a-muchos."""

from .cliente import Cliente
from .observer import Observer
from .tienda import Tienda

__all__ = ["Cliente", "Observer", "Tienda"]
