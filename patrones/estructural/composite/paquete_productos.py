"""Patrón Composite - ``PaqueteProductos`` (Composite con descuento automático).

Java vs Python: ``String.format("%.0f%%")`` -> ``f"{x:.0f}%"`` (en un f-string el
``%`` no necesita escape). El precio final es la suma de los hijos con el
porcentaje de descuento aplicado.
Validaciones agregadas respecto de Java: el descuento debe estar entre 0 y 100
(``ValueError``) y no se admiten ciclos al agregar componentes.
"""

from typing import Final, override

from .componente_catalogo import ComponenteCatalogo


class PaqueteProductos(ComponenteCatalogo):
    PORCENTAJE_MAXIMO: Final = 100.0  # el descuento del paquete va de 0 a 100

    def __init__(self, nombre: str, porcentaje_descuento: float) -> None:
        super().__init__(nombre, 0.0)
        if not 0.0 <= porcentaje_descuento <= self.PORCENTAJE_MAXIMO:
            raise ValueError(
                f"El descuento debe estar entre 0 y {self.PORCENTAJE_MAXIMO:g}, "
                f"recibido: {porcentaje_descuento}"
            )
        self._productos: list[ComponenteCatalogo] = []
        self._porcentaje_descuento = porcentaje_descuento

    @override
    def agregar(self, componente: ComponenteCatalogo) -> None:
        self._validar_nuevo_hijo(componente)
        self._productos.append(componente)

    @override
    def _contiene(self, otro: ComponenteCatalogo) -> bool:
        return any(p is otro or p._contiene(otro) for p in self._productos)

    @override
    def remover(self, componente: ComponenteCatalogo) -> None:
        if componente in self._productos:
            self._productos.remove(componente)

    @override
    def mostrar_detalle(self, nivel: int) -> None:
        indent = self._obtener_indentacion(nivel)
        precio_original = self._precio_sin_descuento()
        precio_con_descuento = self.precio_total
        ahorro = precio_original - precio_con_descuento

        print(f"{indent}[Paquete] {self._nombre}")
        print(
            f"{indent}  Descuento: {self._porcentaje_descuento:.0f}% "
            f"| Precio original: ${precio_original:.2f} "
            f"| Precio final: ${precio_con_descuento:.2f} "
            f"| Ahorro: ${ahorro:.2f}"
        )
        print(f"{indent}  Incluye:")

        for producto in self._productos:
            producto.mostrar_detalle(nivel + 2)

    @property
    @override
    def precio_total(self) -> float:
        total = self._precio_sin_descuento()
        return total * (1 - self._porcentaje_descuento / self.PORCENTAJE_MAXIMO)

    def _precio_sin_descuento(self) -> float:
        total = 0.0
        for producto in self._productos:
            total += producto.precio_total
        return total

    @property
    def porcentaje_descuento(self) -> float:
        return self._porcentaje_descuento
