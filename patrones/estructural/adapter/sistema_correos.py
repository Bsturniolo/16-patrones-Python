"""Patrón Adapter - ``SistemaCorreos`` (Adaptee: API externa en gramos).

Java vs Python:
- Es el sistema "externo" que no se modifica: conserva sus nombres en español
  (``enviar``/``precio``/``estado``) y trabaja en gramos. No implementa
  ``ServicioEnvio``; de eso se encarga ``AdaptadorCorreos``.
- ``System.out.println("..." + double)`` -> ``print(f"...{gramos}")``: ambos
  imprimen el ``float`` crudo (``2500.0``).
- Los valores de la tarifa ($5 + $0.01 por gramo) son literales ``double`` en Java
  y ``float`` en Python.
"""


class SistemaCorreos:
    def enviar(self, destino: str, gramos: float) -> None:
        print(f"Correos: Preparando envío para {destino}")
        print(f"Correos: Peso: {gramos} gramos")

    def precio(self, gramos: float) -> float:
        # Tarifa de Correos: $5 base + $0.01 por gramo
        return 5.0 + (gramos * 0.01)

    def estado(self) -> str:
        return "Correos: Paquete en oficina de distribución"
