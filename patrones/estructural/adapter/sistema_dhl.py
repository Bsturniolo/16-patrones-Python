"""Patrón Adapter - ``SistemaDHL`` (Adaptee: API externa en kilogramos).

Es el sistema "heredado/externo" cuya interfaz NO se puede (ni se debe) cambiar;
por eso conserva sus propios nombres en inglés, convertidos a snake_case.

Java vs Python: ``System.out.println("..." + double)`` imprime el float crudo
(``2.5``); ``print(f"...{peso}")`` hace lo mismo.
"""


class SistemaDHL:
    def ship_package(self, destination: str, weight_kg: float) -> None:
        print(f"DHL: Enviando paquete a {destination}")
        print(f"DHL: Peso del paquete: {weight_kg} kg")

    def calculate_shipping_price(self, weight_kg: float, zone: str) -> float:
        # Tarifa base de DHL: $8 + $2 por kg (la zona se ignora, como en Java)
        return 8.0 + (weight_kg * 2.0)

    def tracking_status(self) -> str:
        return "DHL: Paquete en tránsito"
