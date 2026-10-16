"""Patrón Facade - ``TiendaFacade`` (Facade).

Rol GoF: *Facade*. Ofrece una interfaz simple (``realizar_compra_completa``) sobre varios
subsistemas que el cliente no necesita conocer: Factory (producto), Builder (pedido),
Chain of Responsibility (validación), Strategy (pago) y State (seguimiento).

Java vs Python:
- ``realizarCompraCompleta`` -> ``realizar_compra_completa`` (snake_case); ``getNombreTienda()``
  -> propiedad de solo lectura ``nombre_tienda``.
- ``System.currentTimeMillis()`` -> ``int(time.time() * 1000)``.
- ``null`` -> ``None``: una compra rechazada devuelve ``None``.
- En Python, un *módulo* de funciones ya puede actuar como fachada (``import tienda;
  tienda.comprar(...)``) sin necesidad de una clase; aquí se conserva la clase para que se
  vea la estructura GoF y para poder guardar el estado (``nombre_tienda``).
- Los precios se imprimen como float crudo (``249.99``), igual que la concatenación de un
  ``double`` en Java (los importes derivados del envío se muestran con ``:.2f``).

Diferencia con el Java original (corrección deliberada de un defecto de Java):
- Java arma un ``Pedido`` con envío Express, valida su total (producto + $15 de envío),
  pero luego DESCARTA ese ``Pedido``: cobra con un ``CarritoCompra`` que solo conoce el
  precio del producto y crea el seguimiento (``PedidoContext``) con ese precio pelado.
  Resultado en Java: se valida $914.99 pero se cobra y se registra $899.99.
- Aquí se usa el ``Pedido`` construido: se valida, se cobra y se registra
  ``pedido.calcular_total()`` (producto + envío), y el texto impreso lo explica.
  Como ``CarritoCompra`` solo suma precios de productos, el cobro usa la estrategia
  ``PagoTarjeta`` directamente con el total del pedido.
- Java crea cualquier tipo distinto de ``"libro"`` como electrónico (``"LIBRO"`` o
  ``"juguete"`` incluidos). Aquí se delega en ``ProductoFactory.crear_producto``:
  ignora mayúsculas y un tipo desconocido RECHAZA la compra (devuelve ``None``).
- "Pago procesado" se imprime solo después de ejecutar el cobro (Java lo imprimía
  tras ``checkout()`` sin comprobar nada).
- Los ids de seguimiento son únicos (contador + marca de tiempo); en Java dos compras
  dentro del mismo milisegundo compartían id.
- Acoplamiento: devuelve un ``PedidoContext`` (subsistema State) al cliente, como Java.
  Una fachada más estricta devolvería un id o un DTO propio.
"""

import itertools
import time
from collections.abc import Iterator, Mapping
from typing import ClassVar, Final

from ...comportamiento.chain import (
    ValidadorDireccion,
    ValidadorMetodoPago,
    ValidadorMontoPedido,
    ValidadorPedido,
    ValidadorStock,
)
from ...comportamiento.state import PedidoContext
from ...comportamiento.strategy import PagoTarjeta
from ...creacional.builder.pedido import Pedido
from ...creacional.factory import ProductoFactory


class TiendaFacade:
    """Fachada que simplifica las operaciones de compra de la tienda."""

    # Dato extra que pide ProductoFactory según el tipo (autor / meses de garantía).
    _EXTRA_POR_DEFECTO: Final[Mapping[str, str]] = {
        "libro": "Autor Desconocido",
        "electronico": "12",
    }

    # Contador compartido: next() es atómico en CPython, así que cada id es único.
    _contador_pedidos: ClassVar[Iterator[int]] = itertools.count(1)

    def __init__(self, nombre_tienda: str) -> None:
        self._nombre_tienda = nombre_tienda

    @classmethod
    def _nuevo_numero_pedido(cls) -> str:
        """Id único: marca de tiempo + contador (los milisegundos solos se repiten)."""
        return f"FAC-{int(time.time() * 1000)}-{next(cls._contador_pedidos)}"

    @property
    def nombre_tienda(self) -> str:
        return self._nombre_tienda

    def realizar_compra_completa(
        self,
        tipo_producto: str,
        nombre_producto: str,
        precio: float,
        direccion: str,
        numero_tarjeta: str,
    ) -> PedidoContext | None:
        """Crea producto, pedido, valida, cobra y genera el seguimiento.

        Devuelve el ``PedidoContext`` de seguimiento, o ``None`` si el tipo de producto no
        es válido o la validación falla.
        """
        print(f"\n=== PROCESANDO COMPRA EN {self._nombre_tienda} ===")

        # 1. Crear producto usando Factory (ignora mayúsculas; tipo desconocido -> rechazo)
        print("[1/5] Creando producto...")
        extra = self._EXTRA_POR_DEFECTO.get(tipo_producto.lower(), "")
        try:
            producto = ProductoFactory.crear_producto(tipo_producto, nombre_producto, precio, extra)
        except ValueError as error:
            print(f"✗ Pedido rechazado - {error}")
            return None
        producto.mostrar_info()
        print(f"✓ Producto creado: {nombre_producto}")

        # 2. Crear pedido usando Builder
        print("[2/5] Creando pedido...")
        pedido = (
            Pedido.PedidoBuilder([producto], direccion)
            .con_metodo_envio("Express")
            .es_regalo_flag(False)
            .con_notas_especiales("Pedido desde facade")
            .construir()
        )
        print(f"✓ Pedido creado con dirección: {direccion}")

        # 3. Validar pedido usando Chain of Responsibility
        print("[3/5] Validando pedido...")
        validador_stock: ValidadorPedido = ValidadorStock()
        validador_direccion: ValidadorPedido = ValidadorDireccion()
        validador_monto: ValidadorPedido = ValidadorMontoPedido()
        validador_pago: ValidadorPedido = ValidadorMetodoPago()

        validador_stock.set_siguiente(validador_direccion)
        validador_direccion.set_siguiente(validador_monto)
        validador_monto.set_siguiente(validador_pago)

        if not validador_stock.validar(pedido):
            print("✗ Pedido rechazado - validación fallida")
            return None
        print("✓ Pedido validado exitosamente")

        # 4. Procesar pago usando Strategy: se cobra el total del pedido (producto + envío)
        print("[4/5] Procesando pago...")
        total = pedido.calcular_total()
        print(
            f"Total a cobrar: ${total:.2f} (producto ${precio:.2f} + envío ${total - precio:.2f})"
        )
        PagoTarjeta(numero_tarjeta).pagar(total)
        print("✓ Pago procesado")

        # 5. Crear contexto de seguimiento usando State (con el mismo total cobrado)
        print("[5/5] Generando orden de seguimiento...")
        pedido_context = PedidoContext(self._nuevo_numero_pedido(), total)
        pedido_context.mostrar_estado()
        print("✓ Orden generada")

        print(f"\n¡COMPRA COMPLETADA EXITOSAMENTE EN {self._nombre_tienda}!\n")

        return pedido_context

    def compra_rapida(self, nombre_producto: str, precio: float, direccion: str) -> None:
        """Compra simplificada con configuración por defecto."""
        print(f"\n=== COMPRA RÁPIDA EN {self._nombre_tienda} ===")
        print(f"Producto: {nombre_producto}")
        print(f"Precio: ${precio}")
        print(f"Envío a: {direccion}")
        print("✓ Compra procesada con configuración por defecto")
        print("✓ Se enviará confirmación por email\n")

    def consultar_estado_pedido(self, pedido: PedidoContext | None) -> None:
        """Muestra el estado de un pedido (o avisa si no existe)."""
        print(f"\n=== CONSULTA DE ESTADO - {self._nombre_tienda} ===")
        if pedido is not None:
            pedido.mostrar_estado()
        else:
            print("✗ Pedido no encontrado")
        print()
