"""Patrón Adapter - ``AdaptadorDHL`` (Adapter: DHL ya trabaja en kg).

Rol: traduce la interfaz ``ServicioEnvio`` a la API de ``SistemaDHL`` por composición.

Java vs Python: ``implements`` -> herencia de la ABC. Se inyecta el adaptee por
constructor (composición), lo que permite sustituirlo por un doble en tests.
Nota (quirk de Java mantenido): la dirección se ignora al calcular el costo y la
zona se fija en "nacional".
"""

from typing import override

from .servicio_envio import ServicioEnvio
from .sistema_dhl import SistemaDHL


class AdaptadorDHL(ServicioEnvio):
    def __init__(self, sistema_dhl: SistemaDHL) -> None:
        self._sistema_dhl = sistema_dhl

    @override
    def enviar_paquete(self, direccion: str, peso: float) -> None:
        # peso ya está en kg, no necesita conversión
        self._sistema_dhl.ship_package(direccion, peso)

    @override
    def calcular_costo(self, direccion: str, peso: float) -> float:
        return self._sistema_dhl.calculate_shipping_price(peso, "nacional")

    @override
    def obtener_estado(self) -> str:
        return self._sistema_dhl.tracking_status()
