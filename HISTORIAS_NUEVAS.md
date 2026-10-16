# Nuevas Historias de Usuario - Patrones Adicionales

Este documento contiene las 8 nuevas historias de usuario para los 4 patrones adicionales.

## HU-017: Clonar Productos Base (Prototype)

**Como** administrador del catálogo
**Quiero** clonar productos base para crear variantes
**Para** ahorrar tiempo evitando configurar productos similares desde cero

**Criterios de Aceptación:**
- Puedo clonar un producto desde un registro de prototipos
- El producto clonado es independiente del original
- Puedo modificar el clon sin afectar al prototipo
- Las especificaciones se copian profundamente (deep copy)

**Implementación:**
- Interfaz `Prototype<T>` con método `clonar()`
- `ProductoPrototype` con copy constructor
- `RegistroPrototipos` singleton con prototipos predefinidos

---

## HU-018: Gestionar Categorías de Productos (Composite)

**Como** administrador del catálogo
**Quiero** organizar productos en categorías jerárquicas
**Para** facilitar la navegación y búsqueda de productos

**Criterios de Aceptación:**
- Puedo crear categorías principales y subcategorías
- Puedo agregar productos a cualquier nivel de la jerarquía
- El sistema calcula automáticamente el precio total de una categoría
- Puedo mostrar la estructura completa del catálogo

**Implementación:**
- Componente base: `ComponenteCatalogo`
- Hoja: `ProductoItem`
- Composite: `Categoria` (con hijos recursivos)

---

## HU-019: Crear Paquetes Promocionales (Composite)

**Como** gerente de ventas
**Quiero** crear paquetes de productos con descuento automático
**Para** aumentar las ventas mediante ofertas atractivas

**Criterios de Aceptación:**
- Puedo crear un paquete y agregar múltiples productos
- Puedo definir un porcentaje de descuento para el paquete
- El sistema calcula el precio con descuento automáticamente
- El paquete muestra el ahorro obtenido

**Implementación:**
- `PaqueteProductos` extiende `ComponenteCatalogo`
- Calcula `precioTotal = precioOriginal * (1 - descuento/100)`
- Muestra precio original, precio final y ahorro

---

## HU-020: Procesar Pedidos Nacionales (Template Method)

**Como** sistema de e-commerce
**Quiero** procesar pedidos nacionales con flujo consistente
**Para** asegurar que todos los pedidos pasen por los mismos pasos

**Criterios de Aceptación:**
- Verifica inventario disponible
- Calcula IVA 16% y envío nacional $5
- Procesa el pago
- Prepara envío nacional (3-5 días)
- Notifica al cliente por email y SMS
- Registra la operación en la base de datos

**Implementación:**
- `ProcesadorPedidoNacional` extiende `ProcesadorPedido`
- Template method `procesarPedido()` define el flujo
- Implementa métodos abstractos específicos para pedidos nacionales

---

## HU-021: Procesar Pedidos Internacionales (Template Method)

**Como** sistema de e-commerce
**Quiero** procesar pedidos internacionales con verificaciones adicionales
**Para** cumplir con regulaciones aduaneras

**Criterios de Aceptación:**
- Verifica inventario disponible
- Calcula IVA 16%, aranceles 10%, envío internacional $25, seguro 2%
- Procesa el pago
- Realiza verificación adicional (dirección, restricciones, cobertura)
- Prepara envío con documentación aduanera (7-15 días)
- Notifica al cliente con instrucciones aduaneras
- Registra la operación

**Implementación:**
- `ProcesadorPedidoInternacional` extiende `ProcesadorPedido`
- Override hook method `requiereVerificacionAdicional()` → true
- Implementa `verificacionAdicional()` con validaciones extra

---

## HU-022: Procesar Pedidos Express (Template Method)

**Como** cliente premium
**Quiero** procesar pedidos express con entrega rápida
**Para** recibir mis productos en 24-48 horas

**Criterios de Aceptación:**
- Verifica inventario de forma rápida
- Calcula IVA 16% y envío express $15
- Procesa el pago
- Prepara envío express con prioridad ALTA (24-48h)
- Notifica al cliente con hora estimada de entrega
- Activa seguimiento en tiempo real

**Implementación:**
- `ProcesadorPedidoExpress` extiende `ProcesadorPedido`
- Override `verificarInventario()` para verificación rápida
- Implementa métodos para procesamiento prioritario

---

## HU-023: Gestionar Estados del Pedido (State)

**Como** cliente
**Quiero** que mi pedido transite por estados bien definidos
**Para** saber en qué etapa se encuentra mi compra

**Criterios de Aceptación:**
- El pedido inicia en estado NUEVO
- Puedo avanzar: NUEVO → CONFIRMADO → ENVIADO → ENTREGADO
- En cada estado, el sistema valida las operaciones permitidas
- No puedo realizar operaciones inválidas (ej: cancelar pedido enviado)
- Puedo ver el estado actual del pedido en cualquier momento

**Implementación:**
- Interfaz `EstadoPedido` con operaciones: `siguiente()`, `anterior()`, `cancelar()`
- `PedidoContext` delega comportamiento al estado actual
- Estados concretos: Nuevo, Confirmado, Enviado, Entregado

---

## HU-024: Cancelar Pedidos Según Estado (State)

**Como** cliente
**Quiero** cancelar mi pedido si aún es posible
**Para** evitar recibir productos que ya no necesito

**Criterios de Aceptación:**
- Puedo cancelar un pedido en estado NUEVO (cancelación inmediata)
- Puedo cancelar un pedido CONFIRMADO (procesando reembolso)
- NO puedo cancelar un pedido ENVIADO (debo contactar soporte)
- NO puedo cancelar un pedido ya ENTREGADO
- El pedido cancelado transita a estado CANCELADO (terminal)
- Recibo mensaje claro cuando intento operación inválida

**Implementación:**
- Cada estado implementa `cancelar()` con lógica específica
- `EstadoNuevo` y `EstadoConfirmado` permiten cancelación
- `EstadoEnviado` y `EstadoEntregado` rechazan cancelación
- `EstadoCancelado` es estado terminal (no permite más operaciones)

---

## Matriz de Trazabilidad

| Historia | Patrón | Componente Principal | Prioridad |
|----------|--------|---------------------|-----------|
| HU-017 | Prototype | RegistroPrototipos | Media |
| HU-018 | Composite | Categoria | Alta |
| HU-019 | Composite | PaqueteProductos | Media |
| HU-020 | Template Method | ProcesadorPedidoNacional | Alta |
| HU-021 | Template Method | ProcesadorPedidoInternacional | Alta |
| HU-022 | Template Method | ProcesadorPedidoExpress | Media |
| HU-023 | State | PedidoContext + Estados | Alta |
| HU-024 | State | EstadoCancelado | Media |

## Dependencias entre Historias

```
HU-017 (Prototype) → Independiente
HU-018 (Categorías) → Base para HU-019
HU-019 (Paquetes) → Depende de HU-018
HU-020 (Nacional) → Base para HU-021, HU-022
HU-021 (Internacional) → Extiende HU-020
HU-022 (Express) → Extiende HU-020
HU-023 (Estados) → Base para HU-024
HU-024 (Cancelación) → Depende de HU-023
```

## Escenarios de Prueba Sugeridos

### Prototype
```java
@Test
void testClonesIndependientes() {
    RegistroPrototipos reg = RegistroPrototipos.getInstance();
    ProductoPrototype p1 = reg.obtenerPrototipo("laptop");
    ProductoPrototype p2 = reg.obtenerPrototipo("laptop");

    p1.setNombre("Gaming");
    assertNotEquals(p1.getNombre(), p2.getNombre());
    assertNotSame(p1, p2);
}
```

### Composite
```java
@Test
void testCalculoPrecioJerarquico() {
    Categoria root = new Categoria("Electrónica");
    root.agregar(new ProductoItem("Laptop", 1000.0, ""));
    root.agregar(new ProductoItem("Mouse", 20.0, ""));

    assertEquals(1020.0, root.getPrecioTotal(), 0.01);
}

@Test
void testPaqueteConDescuento() {
    PaqueteProductos pack = new PaqueteProductos("Paquete", 10.0);
    pack.agregar(new ProductoItem("Item1", 100.0, ""));
    pack.agregar(new ProductoItem("Item2", 50.0, ""));

    assertEquals(135.0, pack.getPrecioTotal(), 0.01); // 150 * 0.9
}
```

### Template Method
```java
@Test
void testFlujoConsistente() {
    ProcesadorPedido proc = new ProcesadorPedidoNacional();
    // Verifica que todos los pasos se ejecutan en orden
    proc.procesarPedido("ORD-001", 100.0);
}
```

### State
```java
@Test
void testTransicionesValidas() {
    PedidoContext pedido = new PedidoContext("ORD-001", 100.0);
    assertEquals("NUEVO", pedido.getEstado().getNombreEstado());

    pedido.avanzar();
    assertEquals("CONFIRMADO", pedido.getEstado().getNombreEstado());

    pedido.avanzar();
    assertEquals("ENVIADO", pedido.getEstado().getNombreEstado());
}

@Test
void testCancelacionSegunEstado() {
    PedidoContext pedido = new PedidoContext("ORD-002", 100.0);
    pedido.cancelar(); // OK desde NUEVO
    assertEquals("CANCELADO", pedido.getEstado().getNombreEstado());
}
```

---

**Documento creado**: Octubre 2025
**Total de historias**: 8 nuevas (HU-017 a HU-024)
**Patrones cubiertos**: Prototype, Composite, Template Method, State
