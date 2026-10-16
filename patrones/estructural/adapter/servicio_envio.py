"""Patrón Adapter - interfaz ``ServicioEnvio`` (Target).

Rol: la interfaz unificada que espera el cliente, sin importar el proveedor.

Java vs Python:
- ``interface`` de Java -> clase ``abc.ABC`` con métodos abstractos.
- Alternativa pythonica: ``typing.Protocol`` (duck typing estructural), donde ni
  siquiera hace falta heredar. Usamos ABC para reflejar el ``implements`` de Java.
"""

from abc import ABC, abstractmethod


class ServicioEnvio(ABC):
    """Interfaz unificada para todos los servicios de envío (el peso va en kg)."""

    @abstractmethod
    def enviar_paquete(self, direccion: str, peso: float) -> None:
        """Envía un paquete (el peso va en kg)."""

    @abstractmethod
    def calcular_costo(self, direccion: str, peso: float) -> float:
        """Calcula el costo de envío (el peso va en kg)."""

    @abstractmethod
    def obtener_estado(self) -> str:
        """Devuelve el estado del envío según el proveedor."""
