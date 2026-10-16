"""Patrón Template Method - ``ProcesadorPedidoExpress`` (ConcreteClass).

Entregas rápidas: IVA 16% + $15.00 de envío express. Además de los pasos abstractos,
sobrescribe un paso con implementación por defecto (``verificar_inventario``) para
priorizar la rapidez.

Java vs Python:
- ``verificarInventario`` es un método ``protected`` con cuerpo en la clase base; la subclase
  lo redefine con ``@Override``. En Python se usa ``typing.override`` y el método queda
  público (no existe ``protected``).
- ``calcular_costos`` devuelve el total (Java: ``void``), ver "Diferencia con el Java
  original" en ``ProcesadorPedido``.
"""

from typing import override

from .procesador_pedido import ProcesadorPedido


class ProcesadorPedidoExpress(ProcesadorPedido):
    @override
    def calcular_costos(self, monto: float) -> float:
        print("[3] Calculando costos para pedido EXPRESS...")
        impuesto = monto * 0.16  # IVA 16%
        envio_express = 15.00  # Envío express premium
        total = monto + impuesto + envio_express

        print(f"    Subtotal: ${monto:.2f}")
        print(f"    IVA (16%): ${impuesto:.2f}")
        print(f"    Envío Express: ${envio_express:.2f}")
        print(f"    ✓ Total: ${total:.2f}")
        return total

    @override
    def preparar_envio(self) -> None:
        print("[4] Preparando envío EXPRESS...")
        print("    - Prioridad ALTA en empaquetado")
        print("    - Etiqueta EXPRESS aplicada")
        print("    - Courier asignado: Servicio Express 24h")
        print("    - Tiempo estimado: 24-48 horas")
        print("    ✓ Envío express listo para despacho inmediato")

    @override
    def notificar_cliente(self, numero_pedido: str) -> None:
        print("[5] Notificando al cliente (Express)...")
        print("    ✓ Email prioritario enviado")
        print("    ✓ SMS con hora estimada de entrega")
        print("    ✓ Notificación push activada para seguimiento en tiempo real")

    # Pedidos express priorizan rapidez sobre verificaciones extensivas
    @override
    def verificar_inventario(self) -> None:
        print("[1] Verificación RÁPIDA de inventario...")
        print("    ✓ Inventario confirmado (verificación express)")
