"""Patrón Observer - ``Tienda`` (Subject / sujeto observable).

Rol GoF: *Subject*. Mantiene la lista de observadores y los notifica a todos,
de forma síncrona, cuando publica una oferta.

Java vs Python:
- ``ArrayList<Observer>`` -> ``list[Observer]``.
- ``List.remove(obj)`` de Java ignora silenciosamente un objeto ausente, mientras que
  ``list.remove`` de Python lanza ``ValueError``; por eso se comprueba antes de quitar.
  El mensaje "desuscrito" se imprime igual que en Java (aunque no estuviera suscrito).

Trampa clásica del patrón (modificar la colección mientras se recorre):
- Un observador puede darse de baja *dentro* de su propio ``actualizar`` (por ejemplo, una
  oferta de "un solo uso"). Si ``notificar_clientes`` recorriera ``self._clientes`` directamente,
  ese ``remove`` desplazaría los índices de la lista y el observador siguiente se saltaría
  sin recibir el mensaje (Python no avisa: no hay ``ConcurrentModificationException`` como
  en Java con ``ArrayList``; simplemente se pierde una notificación).
- Por eso se itera sobre una *copia* (``list(self._clientes)``): las altas y bajas que ocurran
  durante la notificación afectan a la próxima ronda, no a la que está en curso.
"""

from .observer import Observer


class Tienda:
    """Sujeto observable: publica ofertas a sus clientes suscritos."""

    def __init__(self, nombre: str) -> None:
        self._nombre = nombre
        self._clientes: list[Observer] = []

    def suscribir(self, cliente: Observer) -> None:
        self._clientes.append(cliente)
        print(f"Cliente suscrito a la tienda {self._nombre}")

    def desuscribir(self, cliente: Observer) -> None:
        if cliente in self._clientes:
            self._clientes.remove(cliente)
        print(f"Cliente desuscrito de la tienda {self._nombre}")

    def notificar_clientes(self, mensaje: str) -> None:
        print(f"\n--- Notificando a {len(self._clientes)} clientes ---")
        # Copia defensiva: un observador puede (des)suscribirse mientras se notifica.
        for cliente in list(self._clientes):
            cliente.actualizar(mensaje)

    def nueva_oferta(self, descripcion: str) -> None:
        print(f"\n¡Nueva oferta en {self._nombre}!")
        self.notificar_clientes(f"Nueva oferta: {descripcion}")
