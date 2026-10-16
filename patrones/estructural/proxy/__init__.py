"""Patrón Proxy: control de acceso y lazy loading de productos premium."""

from .producto_premium import ProductoPremium
from .producto_premium_proxy import ProductoPremiumProxy
from .producto_premium_real import ProductoPremiumReal

__all__ = ["ProductoPremium", "ProductoPremiumProxy", "ProductoPremiumReal"]
