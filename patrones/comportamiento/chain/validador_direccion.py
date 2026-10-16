"""Patrón Chain of Responsibility - ``ValidadorDireccion`` (ConcreteHandler).

Simulación: la dirección siempre es válida (en un sistema real se consultaría una API
de geocodificación). Igual que en Java, no se valida realmente nada, ni siquiera que
la dirección no esté vacía.

Java vs Python:
- ``if (direccionValida) {...} else {...}`` sobre una constante ``true`` se conserva tal cual
  para mostrar la estructura de un validador real; la rama de error es inalcanzable.
- ``@Override`` -> ``typing.override``; ``protected validarSiguiente`` -> ``_validar_siguiente``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from .validador_pedido import ValidadorPedido

if TYPE_CHECKING:
    from ...creacional.builder.pedido import Pedido


class ValidadorDireccion(ValidadorPedido):
    @override
    def validar(self, pedido: Pedido) -> bool:
        print("[OK] Validando dirección de envío...")

        # Simulación: se da por válida siempre (no se comprueba ni siquiera que no esté vacía)
        direccion_valida = True

        if direccion_valida:
            print("  Dirección válida y verificada")
            return self._validar_siguiente(pedido)
        print("  [X] ERROR: Dirección inválida")
        return False
