"""Patrón Adapter - ``AdaptadorFedEx`` (Adapter: convierte kg -> libras).

Java vs Python: ``private static final`` -> constante de clase con ``typing.Final``.
"""

from typing import Final, override

from .servicio_envio import ServicioEnvio
from .sistema_fedex import SistemaFedEx


class AdaptadorFedEx(ServicioEnvio):
    KG_TO_LBS: Final = 2.20462  # 1 kg = 2.20462 lbs

    def __init__(self, sistema_fedex: SistemaFedEx) -> None:
        self._sistema_fedex = sistema_fedex

    @override
    def enviar_paquete(self, direccion: str, peso: float) -> None:
        peso_libras = peso * self.KG_TO_LBS
        self._sistema_fedex.send_shipment(direccion, peso_libras)

    @override
    def calcular_costo(self, direccion: str, peso: float) -> float:
        peso_libras = peso * self.KG_TO_LBS
        return self._sistema_fedex.get_quote(peso_libras)

    @override
    def obtener_estado(self) -> str:
        return self._sistema_fedex.check_status()
