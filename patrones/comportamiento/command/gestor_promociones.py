"""Patrón Command - ``GestorPromociones`` (Invoker: ejecuta y guarda el historial undo/redo).

Rol en el patrón: no sabe qué hace cada comando; solo los ejecuta, los guarda
y mueve un puntero (``_posicion_actual``) para deshacer / rehacer. Ejecutar un
comando nuevo tras un ``deshacer`` descarta los comandos "rehacibles".

Dos garantías (ambas distintas del Java original, que no las daba):
- *Ejecutar primero, descartar después*: el historial "rehacible" solo se trunca cuando el
  comando nuevo se ejecutó SIN error. Si ``ejecutar`` lanza una excepción (p. ej. un
  descuento inválido), el historial queda intacto y lo deshecho aún puede rehacerse.
- *Se guarda una copia*: el invoker ejecuta y guarda ``copy.copy(comando)``, no el objeto
  recibido. Un comando con estado de deshacer (el descuento anterior) que se ejecutara dos
  veces sobreescribiría ese estado y rompería el ``deshacer`` de la primera ejecución. GoF lo
  prevé: "si los comandos deben copiarse (porque su estado cambia al ejecutarse), se usa el
  patrón Prototype". Consecuencia: el objeto que se le pasa al invoker actúa como
  plantilla y NO refleja el estado de la ejecución (``copy.copy`` es superficial: el
  receptor se comparte, que es lo correcto).

Java vs Python:
- ``ArrayList`` -> ``list``; el ``while ... remove(last)`` del Java se escribe
  como un slice ``del historial[posicion + 1:]``.
- ``getTamanioHistorial()`` -> propiedad ``tamanio_historial``; ``getDescripcion()`` de cada
  comando -> propiedad ``descripcion``.
"""

import copy

from .command import Command


class GestorPromociones:
    """Invoker: historial de comandos con undo/redo."""

    def __init__(self) -> None:
        self._historial: list[Command] = []
        self._posicion_actual = -1

    def ejecutar_comando(self, comando: Command) -> None:
        """Ejecuta un comando y lo agrega al historial.

        Si el comando falla (lanza una excepción) el historial no se modifica.
        """
        registro = copy.copy(comando)  # una copia por ejecución (ver docstring del módulo)
        registro.ejecutar()

        # Recién ahora que tuvo éxito: eliminar los comandos que están después de la posición
        # actual (si se deshizo algo y luego se ejecuta un comando nuevo).
        del self._historial[self._posicion_actual + 1 :]
        self._historial.append(registro)
        self._posicion_actual += 1

        print(f"→ Ejecutado: {registro.descripcion}")

    def deshacer(self) -> None:
        """Deshace el último comando ejecutado."""
        if self._posicion_actual < 0:
            print("⚠ No hay comandos para deshacer")
            return

        comando = self._historial[self._posicion_actual]
        comando.deshacer()
        self._posicion_actual -= 1

    def rehacer(self) -> None:
        """Rehace el comando que fue deshecho."""
        if self._posicion_actual >= len(self._historial) - 1:
            print("⚠ No hay comandos para rehacer")
            return

        self._posicion_actual += 1
        comando = self._historial[self._posicion_actual]
        comando.ejecutar()
        print(f"↻ Rehecho: {comando.descripcion}")

    def mostrar_historial(self) -> None:
        """Muestra el historial de comandos ejecutados."""
        print("\n--- HISTORIAL DE PROMOCIONES ---")
        if not self._historial:
            print("(vacío)")
        else:
            for i, comando in enumerate(self._historial):
                marcador = "→" if i == self._posicion_actual else " "
                estado = "✓" if i <= self._posicion_actual else "✗"
                print(f"{marcador} [{estado}] {i + 1}. {comando.descripcion}")
        print("--------------------------------\n")

    def limpiar_historial(self) -> None:
        """Limpia el historial."""
        self._historial.clear()
        self._posicion_actual = -1
        print("✓ Historial limpiado")

    def hay_comandos_para_deshacer(self) -> bool:
        return self._posicion_actual >= 0

    def hay_comandos_para_rehacer(self) -> bool:
        return self._posicion_actual < len(self._historial) - 1

    @property
    def tamanio_historial(self) -> int:
        return len(self._historial)
