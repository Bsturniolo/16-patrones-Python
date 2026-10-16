"""Patrón Template Method - ``ProcesadorPedidoNacional`` (ConcreteClass).

Envíos dentro del país: IVA 16% + $5.00 de envío fijo. No usa el hook.

Java vs Python:
- ``@Override`` no existe; ``typing.override`` (3.12) cumple el mismo rol para los
  verificadores de tipos y se aplica a cada paso redefinido.
- ``%%`` de ``printf`` (porcentaje literal) es simplemente ``%`` en una f-string.
- ``calcular_costos`` devuelve el total (Java: ``void``), ver "Diferencia con el Java
  original" en ``ProcesadorPedido``.
"""

from typing import override

from .procesador_pedido import ProcesadorPedido


class ProcesadorPedidoNacional(ProcesadorPedido):
    @override
    def calcular_costos(self, monto: float) -> float:
        print("[3] Calculando costos para pedido NACIONAL...")
        impuesto = monto * 0.16  # IVA 16%
        envio = 5.00  # Envío nacional fijo
        total = monto + impuesto + envio

        print(f"    Subtotal: ${monto:.2f}")
        print(f"    IVA (16%): ${impuesto:.2f}")
        print(f"    Envío: ${envio:.2f}")
        print(f"    ✓ Total: ${total:.2f}")
        return total

    @override
    def preparar_envio(self) -> None:
        print("[4] Preparando envío NACIONAL...")
        print("    - Empaquetando productos")
        print("    - Generando guía de envío nacional")
        print("    - Courier asignado: Estafeta/DHL Nacional")
        print("    - Tiempo estimado: 3-5 días hábiles")
        print("    ✓ Envío preparado")

    @override
    def notificar_cliente(self, numero_pedido: str) -> None:
        print("[5] Notificando al cliente (Nacional)...")
        print("    ✓ Email enviado")
        print("    ✓ SMS con número de rastreo enviado")
