"""Patrón Template Method - ``ProcesadorPedidoInternacional`` (ConcreteClass).

Envíos fuera del país: IVA 16% + aranceles 10% + $25.00 de envío + seguro 2%.
Sobrescribe el *hook* ``requiere_verificacion_adicional`` para activar el paso [3b].

Java vs Python:
- El hook es un método ``protected boolean`` en Java; aquí es un método público que devuelve
  ``bool`` y se marca con ``typing.override``. La verificación adicional se sobrescribe en
  conjunto con el hook (el hook solo decide SI se ejecuta; el paso define QUÉ hace).
- ``calcular_costos`` devuelve el total (Java: ``void``), ver "Diferencia con el Java
  original" en ``ProcesadorPedido``.
"""

from typing import override

from .procesador_pedido import ProcesadorPedido


class ProcesadorPedidoInternacional(ProcesadorPedido):
    @override
    def calcular_costos(self, monto: float) -> float:
        print("[3] Calculando costos para pedido INTERNACIONAL...")
        impuesto = monto * 0.16  # IVA 16%
        aranceles = monto * 0.10  # Aranceles 10%
        envio = 25.00  # Envío internacional
        seguro = monto * 0.02  # Seguro 2%
        total = monto + impuesto + aranceles + envio + seguro

        print(f"    Subtotal: ${monto:.2f}")
        print(f"    IVA (16%): ${impuesto:.2f}")
        print(f"    Aranceles (10%): ${aranceles:.2f}")
        print(f"    Envío internacional: ${envio:.2f}")
        print(f"    Seguro (2%): ${seguro:.2f}")
        print(f"    ✓ Total: ${total:.2f}")
        return total

    @override
    def preparar_envio(self) -> None:
        print("[4] Preparando envío INTERNACIONAL...")
        print("    - Empaquetando productos con protección adicional")
        print("    - Generando documentación aduanera")
        print("    - Declaración de valor y contenido")
        print("    - Courier asignado: FedEx/DHL International")
        print("    - Tiempo estimado: 7-15 días hábiles")
        print("    ✓ Envío preparado con documentación aduanera")

    @override
    def notificar_cliente(self, numero_pedido: str) -> None:
        print("[5] Notificando al cliente (Internacional)...")
        print("    ✓ Email enviado con información de rastreo")
        print("    ✓ Instrucciones aduaneras incluidas")
        print("    ✓ Información de contacto de courier internacional")

    # Sobrescribir el hook: los pedidos internacionales requieren verificación adicional
    @override
    def requiere_verificacion_adicional(self) -> bool:
        return True

    @override
    def verificacion_adicional(self) -> None:
        print("[3b] Verificación adicional para envío internacional...")
        print("    - Validando dirección internacional")
        print("    - Verificando restricciones de productos")
        print("    - Confirmando cobertura de courier")
        print("    ✓ Verificaciones internacionales completadas")
