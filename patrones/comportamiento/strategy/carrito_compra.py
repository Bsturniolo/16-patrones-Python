"""Patrón Strategy - ``CarritoCompra`` (Context).

Rol GoF: *Context*. Guarda una referencia a la estrategia de pago y le delega el cobro;
la estrategia se puede cambiar en tiempo de ejecución asignando ``carrito.estrategia_pago``.

Java vs Python:
- ``setEstrategiaPago(x)`` -> propiedad con setter: ``carrito.estrategia_pago = x``. En Python
  los getters/setters triviales se escriben como propiedades (se leen y asignan como un
  atributo y, si mañana hace falta validar, se agrega lógica al setter sin cambiar a los
  clientes). El getter devuelve ``EstrategiaPago | None`` y el setter solo acepta una
  ``EstrategiaPago``: no se puede "des-asignar" la estrategia con ``None``.
- La anotación ``EstrategiaPago`` es un ``typing.Protocol`` (tipado estructural): cualquier
  objeto con ``pagar(monto)`` es válido, herede o no de la interfaz.
- ``estrategia_pago`` es ``None`` hasta que se asigna (``null`` en Java); el
  tipo ``EstrategiaPago | None`` lo deja explícito.
- ``checkout`` valida carrito vacío y falta de estrategia imprimiendo (no lanza excepciones),
  igual que Java.
"""

from ...creacional.factory import Producto

from .estrategia_pago import EstrategiaPago


class CarritoCompra:
    """Carrito que cobra usando la estrategia de pago configurada."""

    def __init__(self) -> None:
        self._productos: list[Producto] = []
        self._estrategia_pago: EstrategiaPago | None = None

    def agregar_producto(self, producto: Producto) -> None:
        self._productos.append(producto)
        print(f"Producto agregado al carrito: {producto.nombre}")

    @property
    def estrategia_pago(self) -> EstrategiaPago | None:
        """Estrategia de pago actual (``None`` hasta que se asigna una)."""
        return self._estrategia_pago

    @estrategia_pago.setter
    def estrategia_pago(self, estrategia_pago: EstrategiaPago) -> None:
        self._estrategia_pago = estrategia_pago

    def calcular_total(self) -> float:
        total = 0.0
        for producto in self._productos:
            total += producto.precio
        return total

    def checkout(self) -> None:
        if not self._productos:
            print("El carrito está vacío")
            return

        if self._estrategia_pago is None:
            print("Debe seleccionar un método de pago")
            return

        total = self.calcular_total()
        print("\n=== CHECKOUT ===")
        print("Productos en el carrito:")
        for producto in self._productos:
            producto.mostrar_info()
        print(f"Total: ${total}")
        self._estrategia_pago.pagar(total)
        print("¡Compra completada!\n")
