"""Patrón Adapter - ``SistemaFedEx`` (Adaptee: API externa en libras).

Conserva los nombres de su API original (inglés, snake_case).

Java vs Python:
- En Java los métodos se llaman en camelCase (``sendShipment``, ``getQuote``,
  ``checkStatus``); aquí se pasan a snake_case, que es la convención de Python.
- Trabaja en libras: la conversión desde kg la hace ``AdaptadorFedEx``.
- ``System.out.println("..." + double)`` -> ``print(f"...{pounds}")``: ambos
  imprimen el ``float`` crudo.
"""


class SistemaFedEx:
    def send_shipment(self, address: str, pounds: float) -> None:
        print(f"FedEx: Procesando envío a {address}")
        print(f"FedEx: Peso del envío: {pounds} lbs")

    def get_quote(self, pounds: float) -> float:
        # Tarifa de FedEx: $10 + $1.50 por libra
        return 10.0 + (pounds * 1.5)

    def check_status(self) -> str:
        return "FedEx: En camino al destino"
