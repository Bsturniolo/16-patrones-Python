"""Patrón Factory."""

from .producto import Electronico, Libro, Producto
from .producto_factory import ProductoFactory

__all__ = ["Electronico", "Libro", "Producto", "ProductoFactory"]
