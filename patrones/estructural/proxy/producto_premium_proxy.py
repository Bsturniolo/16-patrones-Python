"""Patrón Proxy - ``ProductoPremiumProxy`` (Proxy: lazy loading y control de acceso).

Rol en el patrón: implementa la misma interfaz que ``ProductoPremiumReal`` y
añade (1) *lazy loading* (virtual proxy): el objeto real se crea solo cuando
es necesario, y (2) control de acceso (protection proxy) por autenticación y
suscripción.

Java vs Python:
- Aquí el proxy es explícito (GoF clásico): un método por operación.
- Alternativa: un proxy dinámico basado en ``__getattr__`` (ver ``ProxyDinamico``
  al final de este módulo), que reenvía al objeto real sin escribir cada método a
  mano. Sirve para proxies transparentes (logging, caché, acceso remoto), pero
  tiene LÍMITES que lo hacen distinto del proxy GoF:

  * ``__getattr__`` solo se invoca cuando la búsqueda normal del atributo FALLA
    (no "intercepta cualquier atributo"): lo que el proxy ya define, no se delega.
  * Nunca se invoca para los métodos especiales (``__len__``, ``__str__``, ...):
    Python los busca en el TIPO, no en la instancia, así que ``len(proxy)`` o
    ``str(proxy)`` no llegan al objeto real.
  * No hereda de ``ProductoPremium``: ``isinstance(proxy, ProductoPremium)`` es
    ``False`` y no comparte la interfaz del Subject (pierde el tipado nominal).
  * Riesgo de recursión: ``copy.copy`` o ``pickle`` crean el objeto SIN ejecutar
    ``__init__`` y consultan atributos como ``__setstate__``; si ``_real`` aún no
    existe, ``self._real`` vuelve a caer en ``__getattr__`` y se recurre sin fin
    (``RecursionError``). La defensa es rechazar los nombres que empiezan con
    ``_``::

        if nombre.startswith("_"):
            raise AttributeError(nombre)

- Los getters ``isUsuarioAutenticado()``/``getTipoSuscripcion()`` son
  propiedades; ``producto_real_cargado`` es una adición para poder verificar
  el lazy loading en los tests.
- Constructor: los datos del producto van por posición (como en Java) y la configuración
  de acceso es *keyword-only* (después de ``*``): ``usuario_autenticado=False`` se
  entiende, un ``False`` suelto en la llamada no (la "trampa del booleano").
  ``retardo_carga`` (segundos que simula la carga del objeto real) también va por nombre.
"""

from collections.abc import Callable
from typing import Any, Final, override

from .producto_premium import ProductoPremium
from .producto_premium_real import ProductoPremiumReal


class ProductoPremiumProxy(ProductoPremium):
    """Proxy: lazy loading + control de acceso."""

    SUSCRIPCIONES_CON_DESCARGA: Final = frozenset({"premium", "vip"})

    def __init__(  # noqa: PLR0913 - 3 datos del producto + 3 opciones keyword-only
        self,
        nombre: str,
        precio: float,
        contenido_digital: str,
        *,
        usuario_autenticado: bool,
        tipo_suscripcion: str,
        retardo_carga: float = 0.5,
    ) -> None:
        self._nombre = nombre
        self._precio = precio
        self._contenido_digital = contenido_digital
        self._usuario_autenticado = usuario_autenticado
        self._tipo_suscripcion = tipo_suscripcion
        self._retardo_carga = retardo_carga
        # NO creamos el objeto real aquí - lazy loading
        self._producto_real: ProductoPremiumReal | None = None

    @property
    def producto_real_cargado(self) -> bool:
        """True si el objeto real ya fue creado (útil para demostrar lazy loading)."""
        return self._producto_real is not None

    def _get_producto_real(self) -> ProductoPremiumReal:
        """Lazy loading - solo crea el objeto real cuando es necesario."""
        if self._producto_real is None:
            self._producto_real = ProductoPremiumReal(
                self._nombre,
                self._precio,
                self._contenido_digital,
                retardo_carga=self._retardo_carga,
            )
        return self._producto_real

    @override
    def mostrar_detalles(self) -> None:
        """Control de acceso - verifica permisos antes de mostrar detalles."""
        if not self._usuario_autenticado:
            print("🔒 ACCESO DENEGADO")
            print("Debe iniciar sesión para ver productos premium")
            print(f"Nombre: {self._nombre} (vista limitada)")
            print(f"Precio: ${self._precio}")
            return

        # Usuario autenticado - delegar al objeto real
        self._get_producto_real().mostrar_detalles()

    @property
    @override
    def precio(self) -> float:
        return self._precio  # Información pública - no requiere objeto real

    @property
    @override
    def nombre(self) -> str:
        return self._nombre  # Información pública - no requiere objeto real

    @override
    def descargar_contenido_digital(self) -> None:
        """Control de acceso estricto - requiere suscripción premium."""
        if not self._usuario_autenticado:
            print("🔒 ACCESO DENEGADO")
            print("Debe iniciar sesión para descargar contenido")
            return

        if self._tipo_suscripcion not in self.SUSCRIPCIONES_CON_DESCARGA:
            print("🔒 ACCESO DENEGADO")
            print("Requiere suscripción Premium o VIP")
            print(f"Su suscripción actual: {self._tipo_suscripcion}")
            print("💡 Actualice su suscripción para acceder a contenido digital")
            return

        # Usuario con permisos adecuados - delegar al objeto real
        self._get_producto_real().descargar_contenido_digital()

    # Métodos adicionales del proxy
    def actualizar_autenticacion(self, autenticado: bool) -> None:
        self._usuario_autenticado = autenticado
        print(
            "🔐 Estado de autenticación actualizado: "
            + ("Autenticado" if autenticado else "No autenticado")
        )

    def actualizar_suscripcion(self, tipo_suscripcion: str) -> None:
        self._tipo_suscripcion = tipo_suscripcion
        print(f"⭐ Suscripción actualizada a: {tipo_suscripcion}")

    @property
    def usuario_autenticado(self) -> bool:
        return self._usuario_autenticado

    @property
    def tipo_suscripcion(self) -> str:
        return self._tipo_suscripcion


class ProxyDinamico:
    """Proxy virtual con ``__getattr__``: crea el objeto real en el primer acceso.

    Ejemplo mínimo de la alternativa pythonica (probado en ``tests/test_proxy.py``).
    No es un ``ProductoPremium`` y no controla accesos: solo ilustra el mecanismo
    y sus límites descritos en el docstring del módulo.
    """

    def __init__(self, fabrica: Callable[[], ProductoPremium]) -> None:
        self._fabrica = fabrica
        self._real: ProductoPremium | None = None

    def __getattr__(self, nombre: str) -> Any:
        # Solo se llama si el atributo NO existe en el proxy. El guard evita la
        # recursión infinita con copy/pickle (ver docstring del módulo).
        if nombre.startswith("_"):
            raise AttributeError(nombre)
        if self._real is None:
            self._real = self._fabrica()
        return getattr(self._real, nombre)
