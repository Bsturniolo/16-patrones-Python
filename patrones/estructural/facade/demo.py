"""Demo del patrón Facade (sección 13 de Main.java)."""

from ...consola import configurar_utf8
from .tienda_facade import TiendaFacade


def demo() -> None:
    print(">>> 13. PATRÓN FACADE <<<")

    # Usar fachada para realizar compra completa
    tienda_facade = TiendaFacade("MegaStore Online")

    print("\n--- Compra completa con Facade ---")
    pedido_facade = tienda_facade.realizar_compra_completa(
        "electronico",
        "Samsung Galaxy S24",
        899.99,
        "Calle Mayor 789, Valencia",
        "4532-9876-5432-1098",
    )

    # Compra rápida
    tienda_facade.compra_rapida("AirPods Pro", 249.99, "Plaza España 10, Sevilla")

    # Consultar estado
    tienda_facade.consultar_estado_pedido(pedido_facade)


if __name__ == "__main__":
    configurar_utf8()
    demo()
