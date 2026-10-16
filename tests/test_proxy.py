"""Tests del patrón Proxy (ProductoPremiumProxy)."""

import copy
import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from patrones.estructural.proxy import (
    ProductoPremium,
    ProductoPremiumProxy,
    ProductoPremiumReal,
)
from patrones.estructural.proxy.demo import demo
from patrones.estructural.proxy.producto_premium_proxy import ProxyDinamico
from tests.ayudantes import capturar


def crear(autenticado: bool, suscripcion: str = "basico") -> ProductoPremiumProxy:
    # retardo_carga=0 evita dormir 500 ms en cada test.
    return ProductoPremiumProxy(
        "Curso X",
        199.99,
        "Videos HD",
        usuario_autenticado=autenticado,
        tipo_suscripcion=suscripcion,
        retardo_carga=0,
    )


class TestLazyLoading(unittest.TestCase):
    def test_constructor_no_crea_objeto_real(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            p = crear(True)
        self.assertFalse(p.producto_real_cargado)
        self.assertEqual(buf.getvalue(), "")

    def test_nombre_y_precio_no_cargan_objeto_real(self) -> None:
        p = crear(True)
        self.assertEqual(p.nombre, "Curso X")
        self.assertEqual(p.precio, 199.99)
        self.assertFalse(p.producto_real_cargado)

    def test_acceso_denegado_no_carga_objeto_real(self) -> None:
        p = crear(False)
        capturar(p.mostrar_detalles)
        capturar(p.descargar_contenido_digital)
        self.assertFalse(p.producto_real_cargado)

    def test_primer_uso_carga_y_segundo_reutiliza(self) -> None:
        p = crear(True)
        s1 = capturar(p.mostrar_detalles)
        self.assertTrue(p.producto_real_cargado)
        self.assertIn("⏳ Cargando producto premium: Curso X...", s1)
        self.assertIn("✓ Producto premium cargado", s1)
        s2 = capturar(p.mostrar_detalles)
        self.assertNotIn("Cargando", s2)
        self.assertIn("🌟 PRODUCTO PREMIUM 🌟", s2)


class TestControlAcceso(unittest.TestCase):
    def test_mostrar_detalles_sin_autenticar_da_vista_limitada(self) -> None:
        s = capturar(crear(False).mostrar_detalles)
        self.assertEqual(
            s.splitlines(),
            [
                "🔒 ACCESO DENEGADO",
                "Debe iniciar sesión para ver productos premium",
                "Nombre: Curso X (vista limitada)",
                "Precio: $199.99",
            ],
        )

    def test_mostrar_detalles_autenticado_delega(self) -> None:
        s = capturar(crear(True).mostrar_detalles)
        self.assertIn("Nombre: Curso X", s)
        self.assertIn("Contenido digital incluido: Videos HD", s)
        self.assertNotIn("DENEGADO", s)

    def test_descarga_sin_autenticar(self) -> None:
        s = capturar(crear(False, "premium").descargar_contenido_digital)
        self.assertIn("Debe iniciar sesión para descargar contenido", s)
        self.assertNotIn("Descargando", s)

    def test_descarga_basico_denegada_con_suscripcion_actual(self) -> None:
        s = capturar(crear(True, "basico").descargar_contenido_digital)
        self.assertIn("Requiere suscripción Premium o VIP", s)
        self.assertIn("Su suscripción actual: basico", s)
        self.assertIn("💡 Actualice su suscripción para acceder a contenido digital", s)
        self.assertNotIn("Descargando", s)

    def test_descarga_premium_y_vip_permitida(self) -> None:
        for tipo in ("premium", "vip"):
            with self.subTest(tipo=tipo):
                s = capturar(crear(True, tipo).descargar_contenido_digital)
                self.assertIn("📥 Descargando: Videos HD", s)
                self.assertIn("✓ Descarga completada", s)

    def test_actualizar_suscripcion_habilita_descarga(self) -> None:
        p = crear(True, "basico")
        capturar(p.descargar_contenido_digital)
        s = capturar(p.actualizar_suscripcion, "premium")
        self.assertEqual(s, "⭐ Suscripción actualizada a: premium\n")
        self.assertEqual(p.tipo_suscripcion, "premium")
        self.assertIn("Descargando", capturar(p.descargar_contenido_digital))

    def test_actualizar_autenticacion_cambia_acceso(self) -> None:
        p = crear(False)
        s = capturar(p.actualizar_autenticacion, True)
        self.assertEqual(s, "🔐 Estado de autenticación actualizado: Autenticado\n")
        self.assertTrue(p.usuario_autenticado)
        self.assertNotIn("DENEGADO", capturar(p.mostrar_detalles))
        s = capturar(p.actualizar_autenticacion, False)
        self.assertIn("No autenticado", s)
        self.assertIn("DENEGADO", capturar(p.mostrar_detalles))


class TestSujetoComun(unittest.TestCase):
    def test_proxy_y_real_son_producto_premium(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            real = ProductoPremiumReal("A", 1.5, "c", retardo_carga=0)
        self.assertIsInstance(real, ProductoPremium)
        self.assertIsInstance(crear(True), ProductoPremium)
        self.assertEqual(real.precio, 1.5)
        self.assertEqual(real.nombre, "A")

    def test_configuracion_del_proxy_solo_por_nombre(self) -> None:
        # Evita la "trampa del booleano": ProductoPremiumProxy("C", 1.0, "x", False, ...)
        # no dice qué significa False. Esos parámetros son keyword-only.
        with self.assertRaises(TypeError):
            ProductoPremiumProxy("C", 1.0, "x", True, "premium")  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            ProductoPremiumReal("C", 1.0, "x", 0)  # type: ignore[call-arg]

    def test_interfaz_abstracta_no_instanciable(self) -> None:
        with self.assertRaises(TypeError):
            ProductoPremium()  # type: ignore[abstract]


class TestProxyDinamico(unittest.TestCase):
    """La alternativa con ``__getattr__`` y sus límites (ver docstring del módulo)."""

    def _proxy(self) -> tuple[ProxyDinamico, list[int]]:
        llamadas: list[int] = []

        def fabrica() -> ProductoPremiumReal:
            llamadas.append(1)
            return ProductoPremiumReal("Curso Y", 10.0, "Videos", retardo_carga=0)

        return ProxyDinamico(fabrica), llamadas

    def test_crea_el_real_en_el_primer_acceso_y_lo_reutiliza(self) -> None:
        proxy, llamadas = self._proxy()
        self.assertEqual(llamadas, [])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(proxy.nombre, "Curso Y")
            self.assertEqual(proxy.precio, 10.0)
        self.assertEqual(len(llamadas), 1)

    def test_delega_metodos_en_el_real(self) -> None:
        proxy, _ = self._proxy()

        # El acceso al atributo crea el real (y este imprime la carga): se
        # resuelve DENTRO de capturar para no ensuciar stdout. Por eso no se pasa
        # ``proxy.descargar_contenido_digital`` directamente (se evaluaría afuera).
        def descargar() -> None:
            proxy.descargar_contenido_digital()

        s = capturar(descargar)
        self.assertIn("📥 Descargando: Videos", s)

    def test_no_comparte_la_interfaz_producto_premium(self) -> None:
        proxy, _ = self._proxy()
        self.assertNotIsInstance(proxy, ProductoPremium)

    def test_no_intercepta_metodos_especiales(self) -> None:
        # __getattr__ solo se llama cuando la busqueda normal falla, y las
        # operaciones como str()/len() buscan en el TIPO, no en la instancia.
        proxy, _ = self._proxy()
        with redirect_stdout(io.StringIO()):
            _ = proxy.nombre  # fuerza la carga del real
        with self.assertRaises(TypeError):
            len(proxy)
        self.assertTrue(str(proxy).startswith("<"))  # el repr por defecto, no el del real

    def test_atributo_inexistente_del_real_lanza_attribute_error(self) -> None:
        proxy, _ = self._proxy()
        with redirect_stdout(io.StringIO()), self.assertRaises(AttributeError):
            _ = proxy.no_existe

    def test_nombres_con_guion_bajo_no_se_delegan_y_copy_no_recursa(self) -> None:
        proxy, llamadas = self._proxy()
        with self.assertRaises(AttributeError):
            _ = proxy._algo_privado
        self.assertEqual(llamadas, [])  # el guard evita incluso crear el real
        clon = copy.copy(proxy)  # sin el guard: RecursionError
        self.assertIsNot(clon, proxy)


class TestDemo(unittest.TestCase):
    def test_demo_sin_dormir_de_verdad(self) -> None:
        with mock.patch("patrones.estructural.proxy.producto_premium_real.time.sleep") as dormir:
            s = capturar(demo)
        # Solo el usuario autenticado carga el objeto real (una vez): lazy loading.
        dormir.assert_called_once_with(0.5)
        self.assertTrue(s.startswith(">>> 14. PATRÓN PROXY <<<\n"))
        self.assertEqual(s.count("⏳ Cargando producto premium:"), 1)
        self.assertIn("⏳ Cargando producto premium: Masterclass de Arquitectura de Software...", s)
        self.assertIn("Debe iniciar sesión para ver productos premium", s)
        self.assertIn("Su suscripción actual: basico", s)
        self.assertIn("⭐ Suscripción actualizada a: premium", s)
        self.assertIn("📥 Descargando: Videos 4K + Certificado + Mentoría", s)


if __name__ == "__main__":
    unittest.main()
