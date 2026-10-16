"""Demostración del patrón Proxy (sección 14 de Main.java)."""

from ...consola import configurar_utf8
from .producto_premium_proxy import ProductoPremiumProxy


def demo() -> None:
    print(">>> 14. PATRÓN PROXY <<<")

    print("\n--- Usuario no autenticado ---")
    curso_online1 = ProductoPremiumProxy(
        "Curso Avanzado de Java",
        199.99,
        "Videos HD + Material descargable",
        usuario_autenticado=False,
        tipo_suscripcion="basico",
    )

    curso_online1.mostrar_detalles()
    print()
    curso_online1.descargar_contenido_digital()

    print("\n--- Usuario autenticado con suscripción básica ---")
    curso_online2 = ProductoPremiumProxy(
        "Masterclass de Arquitectura de Software",
        299.99,
        "Videos 4K + Certificado + Mentoría",
        usuario_autenticado=True,
        tipo_suscripcion="basico",
    )

    curso_online2.mostrar_detalles()
    print()
    curso_online2.descargar_contenido_digital()

    print("\n--- Actualizar a suscripción premium ---")
    curso_online2.actualizar_suscripcion("premium")
    print()
    curso_online2.descargar_contenido_digital()
    print()


if __name__ == "__main__":
    configurar_utf8()
    demo()
