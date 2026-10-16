"""Tests del patrón Observer (Tienda / Cliente)."""

import unittest
from typing import override

from patrones.comportamiento.observer import Cliente, Observer, Tienda
from patrones.comportamiento.observer.demo import demo
from tests.ayudantes import capturar


class ObservadorEspia(Observer):
    """Observer de prueba: guarda los mensajes recibidos (ejemplo de otro Observer concreto)."""

    def __init__(self) -> None:
        self.mensajes: list[str] = []

    @override
    def actualizar(self, mensaje: str) -> None:
        self.mensajes.append(mensaje)


class ObservadorQueSeDesuscribe(Observer):
    """Se da de baja de la tienda en cuanto recibe un mensaje (caso límite clásico)."""

    def __init__(self, tienda: Tienda) -> None:
        self._tienda = tienda
        self.mensajes: list[str] = []

    @override
    def actualizar(self, mensaje: str) -> None:
        self.mensajes.append(mensaje)
        self._tienda.desuscribir(self)


class TestObserver(unittest.TestCase):
    def test_observer_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            Observer()  # type: ignore[abstract]

    def test_cliente_imprime_la_notificacion(self) -> None:
        salida = capturar(Cliente("Juan").actualizar, "hola")
        self.assertEqual(salida, "Cliente Juan recibió notificación: hola\n")

    def test_cliente_expone_nombre(self) -> None:
        self.assertEqual(Cliente("María").nombre, "María")

    def test_suscribir_imprime_y_registra(self) -> None:
        tienda = Tienda("TechStore")
        salida = capturar(tienda.suscribir, ObservadorEspia())
        self.assertEqual(salida, "Cliente suscrito a la tienda TechStore\n")

    def test_todos_los_suscritos_reciben_la_oferta(self) -> None:
        tienda = Tienda("TechStore")
        a, b = ObservadorEspia(), ObservadorEspia()
        capturar(tienda.suscribir, a)
        capturar(tienda.suscribir, b)
        capturar(tienda.nueva_oferta, "50% descuento en laptops")
        self.assertEqual(a.mensajes, ["Nueva oferta: 50% descuento en laptops"])
        self.assertEqual(b.mensajes, ["Nueva oferta: 50% descuento en laptops"])

    def test_desuscrito_ya_no_recibe(self) -> None:
        tienda = Tienda("TechStore")
        a, b = ObservadorEspia(), ObservadorEspia()
        capturar(tienda.suscribir, a)
        capturar(tienda.suscribir, b)
        salida = capturar(tienda.desuscribir, a)
        self.assertEqual(salida, "Cliente desuscrito de la tienda TechStore\n")
        capturar(tienda.nueva_oferta, "Black Friday")
        self.assertEqual(a.mensajes, [])
        self.assertEqual(b.mensajes, ["Nueva oferta: Black Friday"])

    def test_notificar_informa_cantidad_de_clientes(self) -> None:
        tienda = Tienda("T")
        capturar(tienda.suscribir, ObservadorEspia())
        self.assertIn("--- Notificando a 1 clientes ---", capturar(tienda.notificar_clientes, "x"))
        capturar(tienda.suscribir, ObservadorEspia())
        self.assertIn("--- Notificando a 2 clientes ---", capturar(tienda.notificar_clientes, "x"))

    def test_nueva_oferta_formato_completo(self) -> None:
        tienda = Tienda("TechStore")
        capturar(tienda.suscribir, Cliente("Ana"))
        salida = capturar(tienda.nueva_oferta, "2x1")
        self.assertEqual(
            salida,
            "\n¡Nueva oferta en TechStore!\n"
            "\n--- Notificando a 1 clientes ---\n"
            "Cliente Ana recibió notificación: Nueva oferta: 2x1\n",
        )

    def test_desuscribir_alguien_no_suscrito_no_falla(self) -> None:
        # Java: List.remove ignora silenciosamente lo que no está.
        tienda = Tienda("T")
        capturar(tienda.desuscribir, ObservadorEspia())  # no debe lanzar
        self.assertIn("0 clientes", capturar(tienda.notificar_clientes, "x"))

    def test_desuscripcion_durante_la_notificacion_no_saltea_a_nadie(self) -> None:
        # Pitfall clásico: si se recorre la lista original mientras un observador la
        # modifica, el elemento siguiente se "salta". Se notifica sobre una copia.
        tienda = Tienda("T")
        primero = ObservadorQueSeDesuscribe(tienda)
        segundo, tercero = ObservadorEspia(), ObservadorEspia()
        for observador in (primero, segundo, tercero):
            capturar(tienda.suscribir, observador)

        capturar(tienda.nueva_oferta, "2x1")

        self.assertEqual(primero.mensajes, ["Nueva oferta: 2x1"])
        self.assertEqual(segundo.mensajes, ["Nueva oferta: 2x1"])
        self.assertEqual(tercero.mensajes, ["Nueva oferta: 2x1"])
        # La baja sí surtió efecto para las notificaciones siguientes.
        salida = capturar(tienda.notificar_clientes, "otra")
        self.assertIn("Notificando a 2 clientes", salida)
        self.assertEqual(primero.mensajes, ["Nueva oferta: 2x1"])
        self.assertEqual(segundo.mensajes[-1], "otra")


class TestDemo(unittest.TestCase):
    def test_demo_notifica_y_respeta_la_baja(self) -> None:
        salida = capturar(demo)
        self.assertIn(">>> 3. PATRÓN OBSERVER <<<", salida)
        self.assertIn(
            "Cliente María López recibió notificación: Nueva oferta: 50% descuento en laptops",
            salida,
        )
        self.assertIn("--- Notificando a 3 clientes ---", salida)
        self.assertIn("--- Notificando a 2 clientes ---", salida)
        # María se dio de baja antes de la segunda oferta.
        self.assertEqual(salida.count("Cliente María López recibió"), 1)
        self.assertEqual(salida.count("Cliente Juan Pérez recibió"), 2)


if __name__ == "__main__":
    unittest.main()
