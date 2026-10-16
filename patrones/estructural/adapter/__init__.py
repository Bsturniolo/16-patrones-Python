"""Patrón Adapter."""

from .adaptador_correos import AdaptadorCorreos
from .adaptador_dhl import AdaptadorDHL
from .adaptador_fedex import AdaptadorFedEx
from .servicio_envio import ServicioEnvio
from .sistema_correos import SistemaCorreos
from .sistema_dhl import SistemaDHL
from .sistema_fedex import SistemaFedEx

__all__ = [
    "AdaptadorCorreos",
    "AdaptadorDHL",
    "AdaptadorFedEx",
    "ServicioEnvio",
    "SistemaCorreos",
    "SistemaDHL",
    "SistemaFedEx",
]
