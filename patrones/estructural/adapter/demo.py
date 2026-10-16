"""Demostración del patrón Adapter (sección 8 de Main.java).

Nota: igual que Main.java, esta sección NO imprime línea en blanco final.
"""

from ...consola import configurar_utf8
from .adaptador_correos import AdaptadorCorreos
from .adaptador_dhl import AdaptadorDHL
from .adaptador_fedex import AdaptadorFedEx
from .servicio_envio import ServicioEnvio
from .sistema_correos import SistemaCorreos
from .sistema_dhl import SistemaDHL
from .sistema_fedex import SistemaFedEx


def demo() -> None:
    print(">>> 8. PATRÓN ADAPTER <<<")

    peso = 2.5  # kg
    destino = "Madrid, España"

    # Usar DHL a través del adaptador
    print("\n--- Envío con DHL ---")
    servicio_dhl: ServicioEnvio = AdaptadorDHL(SistemaDHL())
    servicio_dhl.enviar_paquete(destino, peso)
    print(f"Costo: ${servicio_dhl.calcular_costo(destino, peso):.2f}")
    print(f"Estado: {servicio_dhl.obtener_estado()}")

    # Usar FedEx a través del adaptador
    print("\n--- Envío con FedEx ---")
    servicio_fedex: ServicioEnvio = AdaptadorFedEx(SistemaFedEx())
    servicio_fedex.enviar_paquete(destino, peso)
    print(f"Costo: ${servicio_fedex.calcular_costo(destino, peso):.2f}")
    print(f"Estado: {servicio_fedex.obtener_estado()}")

    # Usar Correos a través del adaptador
    print("\n--- Envío con Correos ---")
    servicio_correos: ServicioEnvio = AdaptadorCorreos(SistemaCorreos())
    servicio_correos.enviar_paquete(destino, peso)
    print(f"Costo: ${servicio_correos.calcular_costo(destino, peso):.2f}")
    print(f"Estado: {servicio_correos.obtener_estado()}")


if __name__ == "__main__":
    configurar_utf8()
    demo()
