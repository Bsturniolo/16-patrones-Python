"""Patrón Adapter - ``AdaptadorCorreos`` (Adapter: convierte kg -> gramos).

Java vs Python:
- Java: ``class AdaptadorCorreos implements ServicioEnvio`` con el adaptee en un
  campo ``private final``. Python: herencia de la ABC ``ServicioEnvio`` y el adaptee
  inyectado por constructor (composición, no herencia múltiple).
- ``private static final double`` -> constante de clase en MAYÚSCULAS con ``typing.Final``.
- Los métodos conservan la firma de ``ServicioEnvio`` (peso en kg) y convierten a
  gramos antes de delegar; el cliente nunca ve las unidades de Correos.
"""

from typing import Final, override

from .servicio_envio import ServicioEnvio
from .sistema_correos import SistemaCorreos


class AdaptadorCorreos(ServicioEnvio):
    KG_TO_GRAMS: Final = 1000.0  # 1 kg = 1000 gramos

    def __init__(self, sistema_correos: SistemaCorreos) -> None:
        self._sistema_correos = sistema_correos

    @override
    def enviar_paquete(self, direccion: str, peso: float) -> None:
        peso_gramos = peso * self.KG_TO_GRAMS
        self._sistema_correos.enviar(direccion, peso_gramos)

    @override
    def calcular_costo(self, direccion: str, peso: float) -> float:
        peso_gramos = peso * self.KG_TO_GRAMS
        return self._sistema_correos.precio(peso_gramos)

    @override
    def obtener_estado(self) -> str:
        return self._sistema_correos.estado()
