"""Patrón Builder - ``Pedido`` y ``Pedido.PedidoBuilder`` (Product y Builder).

Roles: ``Pedido`` = producto complejo; ``Pedido.PedidoBuilder`` = builder con
interfaz fluida (cada método devuelve ``self``); ``construir()`` entrega el producto.

Java vs Python:
- Java usa una ``static class`` interna y un constructor ``private`` de Pedido que
  recibe el builder. En Python anidamos la clase igual (``Pedido.PedidoBuilder``).
- Python NO puede hacer privado ``__init__``: que los clientes pasen por el builder
  es solo una convención (el guion bajo y la documentación lo indican, nada lo
  impide). Si se quisiera forzar, se podría exigir un "token" que solo el builder
  conoce (``if token is not Pedido._TOKEN: raise TypeError``); aquí no se hace
  para no ocultar la estructura GoF.
- Los getters ``getX()`` pasan a ``@property`` de solo lectura.
- Los métodos fluidos devuelven ``Self`` (``typing.Self``): Java declara ``PedidoBuilder``
  como tipo de retorno; con ``Self`` un builder derivado sigue encadenando con su propio
  tipo (sus métodos nuevos siguen visibles después de llamar a uno heredado).
- ``from __future__ import annotations`` es necesario aquí: ``Pedido.__init__`` anota
  ``Pedido.PedidoBuilder`` y ``construir`` devuelve ``Pedido`` antes de que la clase exista.
- Alternativa pythonica: argumentos con nombre y valores por defecto
  (``Pedido(productos, dir, metodo_envio="Express", ...)``) o un ``dataclass``.
  Se mantiene el Builder para mostrar la estructura GoF.
- Diferencia con Java: Java guarda la lista de productos POR REFERENCIA (el pedido
  cambia si el llamador modifica su lista). Aquí ``Pedido`` guarda una ``tuple``
  copiada al construir: es independiente de la lista del llamador y de otros
  ``Pedido`` creados con el mismo builder, y ``productos`` devuelve esa tupla
  (de solo lectura).
- Nota: los precios se imprimen como float "crudo" (``10.0``), igual que la
  concatenación de un ``double`` en Java.
"""

from __future__ import annotations

from typing import Self

from ..factory import Producto


class Pedido:
    """Producto complejo construido por ``PedidoBuilder``."""

    def __init__(self, builder: Pedido.PedidoBuilder) -> None:
        # Uso interno por convención: los clientes deben pasar por el builder.
        self._productos: tuple[Producto, ...] = tuple(builder._productos)
        self._direccion_envio = builder._direccion_envio
        self._metodo_envio = builder._metodo_envio
        self._es_regalo = builder._es_regalo
        self._mensaje_regalo = builder._mensaje_regalo
        self._envoltura_regalo = builder._envoltura_regalo
        self._notas_especiales = builder._notas_especiales

    def mostrar_resumen(self) -> None:
        print("\n=== RESUMEN DEL PEDIDO ===")
        print("Productos:")
        for p in self._productos:
            print(f"  - {p.nombre} (${p.precio})")
        print(f"Dirección de envío: {self._direccion_envio}")
        print(f"Método de envío: {self._metodo_envio}")
        if self._es_regalo:
            print("Es un regalo: Sí")
            if self._envoltura_regalo:
                print("Con envoltura de regalo")
            if self._mensaje_regalo is not None:
                print(f"Mensaje: {self._mensaje_regalo}")
        if self._notas_especiales is not None:
            print(f"Notas especiales: {self._notas_especiales}")
        print("==========================")

    def calcular_total(self) -> float:
        total = 0.0
        for p in self._productos:
            total += p.precio
        if self._metodo_envio == "Express":
            total += 15.00
        elif self._metodo_envio == "Standard":
            total += 5.00
        if self._envoltura_regalo:
            total += 3.50
        return total

    @property
    def productos(self) -> tuple[Producto, ...]:
        return self._productos

    @property
    def direccion_envio(self) -> str:
        return self._direccion_envio

    @property
    def metodo_envio(self) -> str:
        return self._metodo_envio

    @property
    def es_regalo(self) -> bool:
        return self._es_regalo

    class PedidoBuilder:
        """Builder: parámetros obligatorios en el constructor, opcionales fluidos."""

        def __init__(self, productos: list[Producto], direccion_envio: str) -> None:
            self._productos = productos
            self._direccion_envio = direccion_envio
            self._metodo_envio = "Standard"  # valor por defecto
            self._es_regalo = False
            self._mensaje_regalo: str | None = None
            self._envoltura_regalo = False
            self._notas_especiales: str | None = None

        def con_metodo_envio(self, metodo_envio: str) -> Self:
            self._metodo_envio = metodo_envio
            return self

        def es_regalo_flag(self, es_regalo: bool) -> Self:
            self._es_regalo = es_regalo
            return self

        def con_mensaje_regalo(self, mensaje: str) -> Self:
            self._mensaje_regalo = mensaje
            self._es_regalo = True
            return self

        def con_envoltura_regalo(self, envoltura: bool) -> Self:
            self._envoltura_regalo = envoltura
            if envoltura:
                self._es_regalo = True
            return self

        def con_notas_especiales(self, notas: str) -> Self:
            self._notas_especiales = notas
            return self

        def construir(self) -> Pedido:
            return Pedido(self)
