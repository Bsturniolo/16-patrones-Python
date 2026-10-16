"""Patrón Strategy - interfaz ``EstrategiaPago``.

Rol GoF: *Strategy*. Familia de algoritmos intercambiables (formas de pago).

Java vs Python:
- ``interface`` -> ``typing.Protocol``. Es la opción más didáctica aquí porque deja ver
  la diferencia entre dos formas de tipar:

  * **Tipado nominal** (Java, ``abc.ABC``): un objeto es una ``EstrategiaPago`` solo si su
    clase *declara* que hereda/implementa la interfaz (``class PagoTarjeta(EstrategiaPago)``).
  * **Tipado estructural** (``Protocol``, el "duck typing" con verificación estática): un
    objeto es una ``EstrategiaPago`` si *tiene la forma correcta* (un método
    ``pagar(monto: float) -> None``), aunque nunca haya oído hablar de esta interfaz.

  ``CarritoCompra`` anota su estrategia con el Protocol, así que acepta ambas cosas y
  mypy/pyright también las aceptan. Con una ABC la anotación sería nominal y un objeto con
  ``pagar`` pero sin herencia funcionaría en ejecución y *fallaría* el verificador de tipos.
- Las estrategias concretas de este paquete sí heredan de forma explícita del Protocol.
  Es opcional, pero tiene dos ventajas: el verificador comprueba que implementan ``pagar``
  con la firma correcta y, como el método es ``@abstractmethod``, olvidarse de implementarlo
  da ``TypeError`` al instanciar (igual que con una ABC).
- En Python una estrategia podría ser simplemente una función ``Callable[[float], None]``
  (las funciones son objetos de primera clase); se conserva la clase para mostrar la
  estructura GoF.
"""

from abc import abstractmethod
from typing import Protocol


class EstrategiaPago(Protocol):
    """Interfaz Strategy: cómo se paga un monto."""

    @abstractmethod
    def pagar(self, monto: float) -> None:
        """Ejecuta el pago del ``monto`` indicado."""
