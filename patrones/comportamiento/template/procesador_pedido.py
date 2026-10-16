"""Patrón Template Method - ``ProcesadorPedido`` (AbstractClass).

Rol GoF: *AbstractClass*. ``procesar_pedido`` es el *template method*: fija el esqueleto
del algoritmo (orden de los pasos) y delega los pasos variables a las subclases.

Tres tipos de pasos:
- Abstractos (obligatorios): ``calcular_costos``, ``preparar_envio``, ``notificar_cliente``.
- Con implementación por defecto (sobrescribibles): ``verificar_inventario``,
  ``procesar_pago``, ``registrar_operacion``.
- Hook: ``requiere_verificacion_adicional`` (False por defecto) + ``verificacion_adicional``.

Java vs Python:
- ``final`` no existe en Python como garantía en ejecución. Se usa ``typing.final`` sobre el
  template method: los verificadores de tipos (mypy/pyright) rechazan sobrescribirlo, pero
  el intérprete no lo impide; es una convención respaldada por herramientas.
- ``protected`` no existe en Python; aquí los pasos se dejan públicos (sin guion bajo)
  para poder sobrescribirlos y probarlos sin fricción.
- ``abstract`` -> ``abc.ABC`` + ``@abstractmethod``.
- Nota de comportamiento (igual que Java): la etapa [3] (costos) se ejecuta antes que la
  [2] (pago); la numeración de los mensajes es la del código original y se conserva
  por paridad, aunque el orden de ejecución real sea [1], [3], [2].

Diferencia con el Java original (bug corregido):
- En Java ``calcularCostos`` es ``void``: calcula e imprime el total (p. ej. $585.00 para un
  pedido nacional de $500) pero lo descarta, y el template method llama a
  ``procesarPago(monto)`` con el monto ORIGINAL: se mostraba un total de $585.00 y se cobraban
  $500.00. En esta versión ``calcular_costos`` DEVUELVE el total y ``procesar_pedido`` se lo
  pasa a ``procesar_pago`` (y a ``registrar_operacion``), de modo que se cobra lo calculado.
  Por eso la línea ``[2] Procesando pago de ...`` de la demo muestra $585.00 / $985.00 /
  $363.00 en lugar de $500.00 / $750.00 / $300.00 de la salida de Java.
"""

from abc import ABC, abstractmethod
from typing import final


class ProcesadorPedido(ABC):
    """Define el esqueleto del procesamiento de un pedido."""

    @final
    def procesar_pedido(self, numero_pedido: str, monto: float) -> None:
        """Template Method: no debe ser sobrescrito por las subclases."""
        print(f"\n=== PROCESANDO PEDIDO {numero_pedido} ===")

        self.verificar_inventario()
        total = self.calcular_costos(monto)  # el total calculado es el que se cobra
        self.procesar_pago(total)

        if self.requiere_verificacion_adicional():
            self.verificacion_adicional()

        self.preparar_envio()
        self.notificar_cliente(numero_pedido)
        self.registrar_operacion(numero_pedido, total)

        print(f"=== PEDIDO {numero_pedido} COMPLETADO ===\n")

    # Pasos obligatorios (abstractos) - deben ser implementados por subclases
    @abstractmethod
    def calcular_costos(self, monto: float) -> float:
        """Calcula e imprime el desglose y devuelve el TOTAL a cobrar (impuestos y envío)."""

    @abstractmethod
    def preparar_envio(self) -> None:
        """Prepara el envío según el tipo de pedido."""

    @abstractmethod
    def notificar_cliente(self, numero_pedido: str) -> None:
        """Avisa al cliente por los canales propios de cada tipo de pedido."""

    # Pasos con implementación por defecto - pueden ser sobrescritos
    def verificar_inventario(self) -> None:
        print("[1] Verificando inventario disponible...")
        print("    ✓ Inventario verificado")

    def procesar_pago(self, monto: float) -> None:
        """Cobra ``monto`` (el total devuelto por ``calcular_costos``)."""
        print(f"[2] Procesando pago de ${monto:.2f}...")
        print("    ✓ Pago procesado exitosamente")

    def registrar_operacion(self, numero_pedido: str, monto: float) -> None:
        print("[6] Registrando operación en base de datos...")
        print(f"    ✓ Pedido {numero_pedido} registrado")

    # Hook method - puede ser sobrescrito opcionalmente
    def requiere_verificacion_adicional(self) -> bool:
        return False

    def verificacion_adicional(self) -> None:
        print("[3b] Realizando verificación adicional...")
