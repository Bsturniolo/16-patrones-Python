"""Patrón Command - ``CarritoCompraCommand`` (Receiver: sabe aplicar y quitar descuentos).

Rol en el patrón: los comandos concretos delegan en este objeto el trabajo
real (aplicar / quitar descuentos y calcular totales).

Modelo del descuento: el carrito guarda UN descuento vigente (``DescuentoVigente``), que
puede ser *ninguno*, un *porcentaje* o un *monto fijo*. Los totales se calculan a partir de
ese estado cada vez que se piden, así nunca quedan desactualizados. Un snapshot inmutable
del descuento vigente es lo que usan los comandos para deshacer.

Java vs Python:
- ``getTotalOriginal()`` etc. -> propiedades de solo lectura.
- ``getProductos()`` devolvía una copia (``new ArrayList<>``); aquí ``list(...)``.
- Los porcentajes se convierten a ``float`` para imprimir ``10.0%`` como Java
  imprime un ``double`` (``10`` -> ``10.0``).

Diferencia con el Java original (bugs corregidos):
- Java convertía el descuento fijo en un PORCENTAJE del total del momento
  (``monto / totalOriginal * 100``) y guardaba solo ese porcentaje. Si después se agregaban
  productos, el "descuento de $100" dejaba de valer $100; y al deshacer otro comando se
  restauraba un porcentaje con ruido de punto flotante (p. ej. ``11.111234569272991%``).
  Aquí el descuento fijo se guarda como MONTO y se resta del total: sigue valiendo lo mismo
  aunque cambie el carrito, y deshacer restaura el estado exacto.
- Con el carrito vacío ese cálculo dividía por cero (en Java daba ``Infinity``/``NaN`` sin
  error; en Python ``/`` lanzaría ``ZeroDivisionError``). Ahora el monto queda guardado, el
  total es $0.00 y se aplicará en cuanto haya productos.
- Java no validaba nada y permitía totales negativos (descuento mayor al total) o porcentajes
  absurdos. Aquí el total con descuento nunca baja de 0, el porcentaje debe estar entre 0 y 100
  y el monto fijo no puede ser negativo (``ValueError``, sin modificar el estado).
"""

from dataclasses import dataclass
from typing import Final, Literal

from ...creacional.factory import Producto

TipoDescuento = Literal["ninguno", "porcentaje", "fijo"]


@dataclass(frozen=True)
class DescuentoVigente:
    """Snapshot inmutable del descuento: ``valor`` es un % o un monto según ``tipo``."""

    tipo: TipoDescuento
    valor: float = 0.0


SIN_DESCUENTO: Final = DescuentoVigente("ninguno")


class CarritoCompraCommand:
    """Receiver: carrito con descuento aplicable."""

    PORCENTAJE_MAXIMO: Final = 100.0  # un descuento porcentual va de 0 a 100

    def __init__(self) -> None:
        self._productos: list[Producto] = []
        self._descuento = SIN_DESCUENTO

    def agregar_producto(self, producto: Producto) -> None:
        self._productos.append(producto)

    def aplicar_descuento_porcentaje(self, porcentaje: float, razon: str) -> None:
        """Aplica un descuento porcentual (0 a 100); reemplaza al descuento vigente."""
        if not 0 <= porcentaje <= self.PORCENTAJE_MAXIMO:  # también rechaza NaN
            raise ValueError(
                f"El porcentaje debe estar entre 0 y {self.PORCENTAJE_MAXIMO:g}, no {porcentaje}"
            )
        self._descuento = DescuentoVigente("porcentaje", float(porcentaje))
        print(f"✓ Descuento del {float(porcentaje)}% aplicado ({razon})")

    def aplicar_descuento_fijo(self, monto: float, razon: str) -> None:
        """Aplica un descuento de monto fijo (>= 0); reemplaza al descuento vigente."""
        if not monto >= 0:  # también rechaza NaN
            raise ValueError(f"El monto del descuento no puede ser negativo: {monto}")
        self._descuento = DescuentoVigente("fijo", float(monto))
        print(f"✓ Descuento de ${float(monto)} aplicado ({razon})")

    def remover_descuento(self) -> None:
        self._descuento = SIN_DESCUENTO
        print("✓ Descuento removido")

    def restaurar_descuento(self, anterior: DescuentoVigente) -> None:
        """Vuelve a un descuento guardado antes (lo usan los ``deshacer`` de los comandos)."""
        if anterior.tipo == "porcentaje":
            self.aplicar_descuento_porcentaje(anterior.valor, "Restauración de descuento")
        elif anterior.tipo == "fijo":
            self.aplicar_descuento_fijo(anterior.valor, "Restauración de descuento")
        else:
            self.remover_descuento()

    def mostrar_resumen(self) -> None:
        print("\n--- RESUMEN DEL CARRITO ---")
        print(f"Productos en carrito: {len(self._productos)}")
        print(f"Total original: ${self.total_original:.2f}")
        if self.descuento_aplicado > 0:
            print(f"Descuento aplicado: {self.descuento_aplicado:.1f}%")
            print(f"Ahorro: ${self.total_original - self.total_con_descuento:.2f}")
        print(f"TOTAL A PAGAR: ${self.total_con_descuento:.2f}")
        print("---------------------------\n")

    @property
    def total_original(self) -> float:
        total = 0.0
        for producto in self._productos:
            total += producto.precio
        return total

    @property
    def total_con_descuento(self) -> float:
        """Total a pagar; nunca es negativo."""
        original = self.total_original
        if self._descuento.tipo == "porcentaje":
            return original * (1 - self._descuento.valor / self.PORCENTAJE_MAXIMO)
        if self._descuento.tipo == "fijo":
            return max(0.0, original - self._descuento.valor)
        return original

    @property
    def descuento_aplicado(self) -> float:
        """Descuento efectivo expresado en % del total original (0.0 si no hay ninguno)."""
        if self._descuento.tipo == "porcentaje":
            return self._descuento.valor
        original = self.total_original
        if self._descuento.tipo == "fijo" and original > 0:
            return min(self._descuento.valor, original) / original * self.PORCENTAJE_MAXIMO
        return 0.0

    @property
    def descuento_vigente(self) -> DescuentoVigente:
        """Snapshot del descuento actual (para que un comando pueda deshacerse)."""
        return self._descuento

    @property
    def productos(self) -> list[Producto]:
        return list(self._productos)
