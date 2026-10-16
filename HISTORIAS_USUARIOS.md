1# Historias de Usuario - Sistema de Comercio Electrónico

## Información del Proyecto

**Proyecto:** Sistema de Comercio Electrónico con Patrones de Diseño
**Versión:** 3.0
**Fecha:** Diciembre 2025
**Equipo:** Desarrollo Los Cortez
**Arquitectura:** Estructura organizada por paquetes con 16 patrones de diseño

---

## Estructura del Proyecto

El proyecto está organizado en paquetes que reflejan las categorías de patrones de diseño:

```
src/
├── Main.java (Clase principal de demostración)
└── patrones/
    ├── creacional/
    │   ├── singleton/    → DatabaseConnection
    │   ├── factory/      → Producto, Libro, Electronico, ProductoFactory
    │   └── builder/      → Pedido (con PedidoBuilder interno)
    ├── estructural/
    │   ├── decorator/    → ProductoDecorador + 3 decoradores concretos
    │   └── adapter/      → ServicioEnvio + 3 sistemas + 3 adaptadores
    └── comportamiento/
        ├── observer/     → Observer, Cliente, Tienda
        ├── strategy/     → EstrategiaPago + 3 estrategias + CarritoCompra
        └── chain/        → ValidadorPedido + 4 validadores concretos
```

**Compilación:**
```bash
# Windows
javac -d out -encoding UTF-8 src\Main.java src\patrones\**\*.java
java -cp out Main

# Linux/Mac
javac -d out -encoding UTF-8 src/Main.java src/patrones/**/*.java
java -cp out Main
```

---

## Épica 1: Gestión de Conexión a Base de Datos

### HU-001: Conexión Única a Base de Datos (Patrón Singleton)

**Como** administrador del sistema
**Quiero** que exista una única instancia de conexión a la base de datos
**Para** optimizar recursos y evitar múltiples conexiones innecesarias

**Criterios de Aceptación:**
- ✓ Solo puede existir una instancia de DatabaseConnection en todo el sistema
- ✓ Todas las solicitudes de conexión retornan la misma instancia
- ✓ La conexión se crea de forma lazy (solo cuando se solicita por primera vez)
- ✓ El constructor es privado para evitar instanciación externa
- ✓ El método getInstance() es thread-safe

**Prioridad:** Alta
**Estimación:** 3 puntos
**Dependencias:** Ninguna

**Notas Técnicas:**
- Implementar patrón Singleton clásico
- Clase: `patrones.creacional.singleton.DatabaseConnection`
- Connection string: jdbc:mysql://localhost:3306/midb
- Import requerido en Main: `import patrones.creacional.singleton.DatabaseConnection;`

**Casos de Prueba:**
1. Verificar que db1.getInstance() == db2.getInstance() retorna true
2. Intentar crear instancia con new debe fallar (constructor privado)
3. Ejecutar queries básicas a través de la instancia única

---

## Épica 2: Catálogo de Productos

### HU-002: Creación de Productos mediante Factory (Patrón Factory)

**Como** administrador de tienda
**Quiero** crear diferentes tipos de productos de forma estandarizada
**Para** mantener consistencia en la creación de objetos del catálogo

**Criterios de Aceptación:**
- ✓ ProductoFactory puede crear Libros con nombre, precio y autor
- ✓ ProductoFactory puede crear Electrónicos con nombre, precio y garantía
- ✓ Método genérico crearProducto() acepta tipo como string
- ✓ Métodos específicos crearLibro() y crearElectronico() con parámetros personalizados
- ✓ Se lanza IllegalArgumentException para tipos no válidos
- ✓ Todos los productos heredan de clase abstracta Producto

**Prioridad:** Alta
**Estimación:** 5 puntos
**Dependencias:** Ninguna

**Notas Técnicas:**
- Paquete: `patrones.creacional.factory`
- Clase abstracta `Producto` con método abstracto mostrarInfo()
- Subclases: `Libro`, `Electronico`
- Factory: `ProductoFactory` utiliza métodos estáticos
- Imports requeridos en Main:
  ```java
  import patrones.creacional.factory.Producto;
  import patrones.creacional.factory.ProductoFactory;
  ```

**Casos de Prueba:**
1. Crear libro con autor "Gabriel García Márquez" y verificar atributos
2. Crear electrónico con garantía de 24 meses
3. Intentar crear producto tipo "ropa" debe lanzar excepción
4. Verificar que libro instanceof Producto == true

---

### HU-003: Visualización de Información de Productos

**Como** usuario de la tienda
**Quiero** ver la información detallada de cada producto
**Para** tomar decisiones de compra informadas

**Criterios de Aceptación:**
- ✓ Los Libros muestran: nombre, autor y precio
- ✓ Los Electrónicos muestran: nombre, garantía en meses y precio
- ✓ El formato de salida es legible y consistente
- ✓ Los precios se muestran con símbolo $ y 2 decimales

**Prioridad:** Media
**Estimación:** 2 puntos
**Dependencias:** HU-002

**Casos de Prueba:**
1. Mostrar info de libro debe incluir "Autor:"
2. Mostrar info de electrónico debe incluir "Garantía: X meses"
3. Precio debe mostrarse como $XX.XX

---

## Épica 3: Sistema de Notificaciones

### HU-004: Suscripción de Clientes a Notificaciones (Patrón Observer)

**Como** cliente de la tienda
**Quiero** suscribirme a notificaciones de ofertas
**Para** estar informado de promociones y descuentos

**Criterios de Aceptación:**
- ✓ Los clientes pueden suscribirse a una tienda
- ✓ Los clientes pueden desuscribirse en cualquier momento
- ✓ Una tienda puede tener múltiples clientes suscritos
- ✓ Al suscribirse se confirma la acción con mensaje
- ✓ Al desuscribirse se confirma la acción con mensaje

**Prioridad:** Alta
**Estimación:** 5 puntos
**Dependencias:** Ninguna

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.observer`
- Implementar patrón Observer con interfaz `Observer`
- `Tienda` actúa como Subject
- `Cliente` actúa como ConcreteObserver
- Usar ArrayList para mantener lista de observadores
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.observer.Cliente;
  import patrones.comportamiento.observer.Tienda;
  ```

**Casos de Prueba:**
1. Suscribir 3 clientes y verificar que la lista contiene 3 elementos
2. Desuscribir un cliente y verificar que la lista contiene 2 elementos
3. Verificar mensajes de confirmación en consola

---

### HU-005: Notificación de Ofertas a Clientes Suscritos

**Como** administrador de tienda
**Quiero** notificar ofertas a todos los clientes suscritos
**Para** aumentar las ventas mediante promociones dirigidas

**Criterios de Aceptación:**
- ✓ Al publicar una oferta, todos los clientes suscritos reciben notificación
- ✓ Los clientes no suscritos no reciben notificaciones
- ✓ El mensaje de oferta se personaliza con el nombre del cliente
- ✓ Se muestra el número total de clientes notificados
- ✓ Las notificaciones se envían de forma síncrona e inmediata

**Prioridad:** Alta
**Estimación:** 3 puntos
**Dependencias:** HU-004

**Casos de Prueba:**
1. Crear oferta "50% descuento" con 3 clientes suscritos
2. Verificar que cada cliente recibe el mensaje exacto
3. Desuscribir 1 cliente y verificar que solo 2 reciben siguiente oferta
4. Verificar output: "Notificando a X clientes"

---

## Épica 4: Proceso de Compra

### HU-006: Gestión del Carrito de Compras

**Como** cliente
**Quiero** agregar productos a mi carrito de compras
**Para** realizar una compra de múltiples artículos

**Criterios de Aceptación:**
- ✓ Puedo agregar cualquier tipo de producto al carrito
- ✓ El carrito confirma cada producto agregado con mensaje
- ✓ El carrito calcula el total sumando precios de todos los productos
- ✓ Puedo ver todos los productos en el carrito durante checkout
- ✓ El carrito valida que no esté vacío antes de checkout

**Prioridad:** Alta
**Estimación:** 5 puntos
**Dependencias:** HU-002

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.strategy`
- Clase: `CarritoCompra`
- Usar ArrayList<Producto> para almacenar productos
- Método calcularTotal() itera y suma precios
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.strategy.CarritoCompra;
  import patrones.creacional.factory.Producto;
  ```

**Casos de Prueba:**
1. Agregar 2 productos y verificar total = suma de precios
2. Intentar checkout con carrito vacío debe mostrar error
3. Verificar que productos se listan correctamente

---

### HU-007: Selección de Método de Pago (Patrón Strategy)

**Como** cliente
**Quiero** seleccionar mi método de pago preferido
**Para** completar la compra de manera conveniente

**Criterios de Aceptación:**
- ✓ Puedo pagar con tarjeta de crédito/débito
- ✓ Puedo pagar en efectivo con 5% descuento
- ✓ Puedo pagar con PayPal usando mi email
- ✓ El método de pago se puede cambiar antes del checkout
- ✓ El sistema valida que haya un método de pago seleccionado

**Prioridad:** Alta
**Estimación:** 5 puntos
**Dependencias:** HU-006

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.strategy`
- Implementar patrón Strategy con interfaz `EstrategiaPago`
- Tres estrategias concretas: `PagoTarjeta`, `PagoEfectivo`, `PagoPayPal`
- `CarritoCompra` es el Context que usa la estrategia
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.strategy.PagoTarjeta;
  import patrones.comportamiento.strategy.PagoEfectivo;
  import patrones.comportamiento.strategy.PagoPayPal;
  ```

**Casos de Prueba:**
1. Intentar checkout sin método de pago debe mostrar error
2. Cambiar de PagoTarjeta a PagoEfectivo debe funcionar
3. Verificar que cada estrategia procesa el pago correctamente

---

### HU-008: Procesamiento de Pago con Tarjeta

**Como** cliente
**Quiero** pagar con tarjeta de crédito/débito
**Para** realizar compras de forma segura y rápida

**Criterios de Aceptación:**
- ✓ Se solicita número de tarjeta
- ✓ Solo se muestran los últimos 4 dígitos por seguridad
- ✓ Se procesa el pago por el monto total exacto
- ✓ Se confirma el pago exitoso

**Prioridad:** Alta
**Estimación:** 3 puntos
**Dependencias:** HU-007

**Casos de Prueba:**
1. Pagar $100 con tarjeta "4532-1234-5678-9012"
2. Verificar output: "terminada en 9012"
3. Verificar monto exacto: $100.00

---

### HU-009: Procesamiento de Pago en Efectivo con Descuento

**Como** cliente
**Quiero** pagar en efectivo y recibir descuento
**Para** ahorrar dinero en mis compras

**Criterios de Aceptación:**
- ✓ Se aplica 5% de descuento automático al pagar en efectivo
- ✓ Se muestra el monto original
- ✓ Se muestra el monto final con descuento aplicado
- ✓ El cálculo del descuento es correcto (monto * 0.95)

**Prioridad:** Media
**Estimación:** 2 puntos
**Dependencias:** HU-007

**Casos de Prueba:**
1. Pagar $100 en efectivo debe resultar en $95
2. Verificar mensaje "Se aplicó 5% descuento"
3. Verificar "Total a pagar: $95.00"

---

### HU-010: Procesamiento de Pago con PayPal

**Como** cliente
**Quiero** pagar con mi cuenta PayPal
**Para** utilizar mi método de pago en línea preferido

**Criterios de Aceptación:**
- ✓ Se solicita email de cuenta PayPal
- ✓ Se procesa el pago por el monto total exacto
- ✓ Se muestra el email de la cuenta utilizada
- ✓ Se confirma el pago exitoso

**Prioridad:** Media
**Estimación:** 2 puntos
**Dependencias:** HU-007

**Casos de Prueba:**
1. Pagar con email "usuario@email.com"
2. Verificar output incluye el email
3. Verificar monto correcto

---

### HU-011: Proceso Completo de Checkout

**Como** cliente
**Quiero** completar el proceso de compra
**Para** finalizar mi orden y recibir mis productos

**Criterios de Aceptación:**
- ✓ Se muestra resumen de productos en el carrito
- ✓ Se muestra el total a pagar
- ✓ Se procesa el pago con el método seleccionado
- ✓ Se confirma que la compra fue completada exitosamente
- ✓ El formato de salida es profesional y claro

**Prioridad:** Alta
**Estimación:** 3 puntos
**Dependencias:** HU-006, HU-007

**Casos de Prueba:**
1. Checkout con 2 productos y pago con tarjeta
2. Verificar output incluye: "=== CHECKOUT ==="
3. Verificar listado de productos con mostrarInfo()
4. Verificar total calculado correctamente
5. Verificar "¡Compra completada!"

---

## Épica 5: Demostración del Sistema

### HU-012: Demostración Completa de Patrones de Diseño

**Como** usuario técnico/estudiante
**Quiero** ejecutar una demostración completa del sistema
**Para** ver todos los patrones de diseño en acción

**Criterios de Aceptación:**
- ✓ Main.java ejecuta ejemplos de los 4 patrones
- ✓ Cada patrón está claramente identificado en el output
- ✓ Los ejemplos son representativos y realistas
- ✓ El flujo es lógico y fácil de seguir
- ✓ Se incluyen múltiples casos de uso por patrón

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** Todas las HU anteriores

**Notas Técnicas:**
- Archivo principal: `src/Main.java`
- Requiere imports específicos de todos los paquetes (30+ imports)
- El Main debe compilarse con acceso a todos los paquetes en src/

**Demostración Incluye:**

1. **Singleton** - Conexión única a BD
2. **Factory** - Creación de productos (Libro, Electrónico)
3. **Observer** - Notificaciones a clientes suscritos
4. **Strategy** - Diferentes métodos de pago
5. **Decorator** - Agregar funcionalidades a productos
6. **Builder** - Construcción de pedidos complejos
7. **Chain of Responsibility** - Validación en cadena de pedidos
8. **Adapter** - Integración de sistemas de envío
9. **Prototype** - Clonación de productos desde registro
10. **Composite** - Jerarquías de categorías y paquetes
11. **Template Method** - Procesamiento de pedidos nacionales/internacionales/express
12. **State** - Gestión de estados del pedido
13. **Facade** - Simplificación de procesos de compra
14. **Proxy** - Control de acceso a productos premium
15. **Command** - Gestión de promociones con undo/redo
16. **Iterator** - Recorrido de catálogo con diferentes estrategias

**Casos de Prueba:**
1. Compilar todos los archivos desde src/ con javac
2. Ejecutar Main y verificar que los 16 patrones funcionan sin errores
3. Verificar output formateado correctamente con títulos por patrón
4. Verificar cálculos correctos en todos los escenarios
5. Confirmar que no hay errores de imports o package declarations

---

## Resumen de Prioridades

### Alta (10 historias)
- HU-001: Conexión única BD (Singleton)
- HU-002: Factory de productos
- HU-004: Suscripción clientes (Observer)
- HU-005: Notificación ofertas
- HU-006: Carrito de compras
- HU-007: Selección método pago (Strategy)
- HU-008: Pago con tarjeta
- HU-011: Checkout completo
- HU-012: Demostración completa

### Media (3 historias)
- HU-003: Visualización productos
- HU-009: Pago efectivo con descuento
- HU-010: Pago PayPal

---

## Estimación Total

**Total Puntos:** 46 puntos
**Sprint sugerido:** 2 sprints de 2 semanas

### Sprint 1 (23 puntos)
- Épica 1: Gestión de BD (3 pts)
- Épica 2: Catálogo de Productos (7 pts)
- Épica 3: Sistema de Notificaciones (8 pts)

### Sprint 2 (23 puntos)
- Épica 4: Proceso de Compra (15 pts)
- Épica 5: Demostración del Sistema (8 pts)

---

## Definición de Terminado (DoD)

- [ ] Código implementado según criterios de aceptación
- [ ] Código compilado sin errores ni warnings
- [ ] Patrón de diseño correctamente implementado
- [ ] Casos de prueba ejecutados manualmente con éxito
- [ ] Código comentado apropiadamente
- [ ] Output en consola es claro y profesional
- [ ] Integración con Main.java funcional
- [ ] Revisión de código completada

---

## Glosario

### Patrones de Diseño:

**Patrones Creacionales:**
- **Singleton:** Garantiza una única instancia de una clase
- **Factory:** Encapsula la creación de objetos relacionados
- **Builder:** Construye objetos complejos paso a paso con fluent interface
- **Prototype:** Clona objetos existentes para crear copias independientes

**Patrones Estructurales:**
- **Decorator:** Agrega funcionalidades dinámicamente a objetos
- **Adapter:** Adapta interfaces incompatibles entre sistemas
- **Composite:** Representa jerarquías parte-todo como estructuras de árbol
- **Facade:** Proporciona interfaz simplificada a subsistemas complejos
- **Proxy:** Controla acceso a objetos con lazy loading y verificación

**Patrones de Comportamiento:**
- **Observer:** Define dependencia uno-a-muchos para notificaciones
- **Strategy:** Define familia de algoritmos intercambiables
- **Chain of Responsibility:** Pasa solicitudes a través de cadena de manejadores
- **Template Method:** Define esqueleto de algoritmo con pasos personalizables
- **State:** Permite que un objeto altere su comportamiento al cambiar de estado
- **Command:** Encapsula operaciones como objetos con undo/redo
- **Iterator:** Proporciona múltiples formas de recorrer colecciones

### Términos Técnicos:
**Package:** Organización de clases en directorios con namespace (paquete)
**Import:** Declaración para usar clases de otros paquetes
**Subject:** Objeto observado en patrón Observer
**ConcreteObserver:** Implementación específica de observador
**Context:** Clase que utiliza una estrategia en patrón Strategy
**Target:** Interfaz esperada por el cliente en patrón Adapter
**Adaptee:** Sistema externo a adaptar en patrón Adapter
**Handler:** Manejador en cadena de responsabilidad
**Checkout:** Proceso final de compra

---

## Contacto

**Product Owner:** Los Cortez Development Team
**Scrum Master:** [A definir]
**Equipo de Desarrollo:** [A definir]

---

# ARQUITECTURA Y ORGANIZACIÓN DEL CÓDIGO

## Refactorización a Estructura de Paquetes

El proyecto ha sido completamente refactorizado para seguir una arquitectura organizada por patrones de diseño. Esta estructura facilita:

1. **Mantenibilidad**: Cada patrón está aislado en su propio paquete
2. **Escalabilidad**: Agregar nuevos patrones es straightforward
3. **Comprensión**: La estructura del código refleja los conceptos de diseño
4. **Educación**: Ideal para aprender patrones de diseño organizados

### Mapeo de Clases a Paquetes:

| Clase | Paquete | Categoría |
|-------|---------|-----------|
| DatabaseConnection | patrones.creacional.singleton | Creacional |
| Producto, Libro, Electronico, ProductoFactory | patrones.creacional.factory | Creacional |
| Pedido (con PedidoBuilder) | patrones.creacional.builder | Creacional |
| ProductoDecorador, EnvolturaRegaloDecorador, SeguroDecorador, GarantiaExtendidaDecorador | patrones.estructural.decorator | Estructural |
| ServicioEnvio, SistemaDHL, SistemaFedEx, SistemaCorreos, AdaptadorDHL, AdaptadorFedEx, AdaptadorCorreos | patrones.estructural.adapter | Estructural |
| Observer, Cliente, Tienda | patrones.comportamiento.observer | Comportamiento |
| EstrategiaPago, PagoTarjeta, PagoEfectivo, PagoPayPal, CarritoCompra | patrones.comportamiento.strategy | Comportamiento |
| ValidadorPedido, ValidadorStock, ValidadorDireccion, ValidadorMontoPedido, ValidadorMetodoPago | patrones.comportamiento.chain | Comportamiento |

### Dependencias entre Paquetes:

```
patrones.creacional.factory (Producto)
    ↓
    ├─→ patrones.creacional.builder (Pedido usa List<Producto>)
    ├─→ patrones.estructural.decorator (ProductoDecorador envuelve Producto)
    └─→ patrones.comportamiento.strategy (CarritoCompra usa List<Producto>)

patrones.creacional.builder (Pedido)
    ↓
    └─→ patrones.comportamiento.chain (ValidadorPedido valida Pedido)
```

### Consideraciones Importantes:

1. **Imports Específicos**: Usar imports específicos en lugar de wildcards (*)
   ```java
   // Correcto
   import patrones.creacional.factory.Producto;

   // Incorrecto (puede causar ambigüedad)
   import patrones.creacional.factory.*;
   ```

2. **Compilación**: Compilar desde el directorio raíz con classpath src/
   ```bash
   javac -cp src src/Main.java src/patrones/**/*.java
   ```

3. **Package Declarations**: Todas las clases excepto Main.java tienen declaración de paquete
   ```java
   package patrones.creacional.singleton;
   ```

---

*Documento actualizado: Octubre 2025*

---

# HISTORIAS DE USUARIO DETALLADAS

## Épica 6: Personalización de Productos

### HU-013: Agregar Funcionalidades Adicionales a Productos (Patrón Decorator)

**Como** cliente
**Quiero** agregar funcionalidades opcionales a los productos
**Para** personalizar mi compra según mis necesidades

**Criterios de Aceptación:**
- ✓ Puedo agregar envoltura de regalo a cualquier producto (+$3.50)
- ✓ Puedo agregar seguro contra daños (10% del precio del producto)
- ✓ Puedo agregar garantía extendida para electrónicos ($2.50 por mes adicional)
- ✓ Los decoradores son combinables (puedo agregar múltiples)
- ✓ El precio se calcula correctamente con todos los decoradores aplicados
- ✓ La información del producto muestra todos los extras agregados

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-002

**Notas Técnicas:**
- Paquete: `patrones.estructural.decorator`
- Implementar patrón Decorator con `ProductoDecorador` como clase base abstracta
- Decoradores concretos: `EnvolturaRegaloDecorador`, `SeguroDecorador`, `GarantiaExtendidaDecorador`
- Cada decorador extiende ProductoDecorador y envuelve un Producto
- Los decoradores sobrescriben getPrecio() y mostrarInfo() para agregar funcionalidad
- Dependencia: requiere importar `patrones.creacional.factory.Producto`
- Imports requeridos en Main:
  ```java
  import patrones.estructural.decorator.EnvolturaRegaloDecorador;
  import patrones.estructural.decorator.SeguroDecorador;
  import patrones.estructural.decorator.GarantiaExtendidaDecorador;
  ```

**Casos de Prueba:**
1. Producto base: iPad Pro $799.99
2. iPad + Envoltura: $803.49
3. MacBook + Seguro + Garantía extendida + Envoltura: verificar cálculo correcto
4. Verificar que mostrarInfo() muestra todos los extras

---

## Épica 7: Gestión Avanzada de Pedidos

### HU-014: Construir Pedidos Complejos (Patrón Builder)

**Como** cliente
**Quiero** crear pedidos con múltiples opciones personalizables
**Para** especificar exactamente cómo quiero recibir mi compra

**Criterios de Aceptación:**
- ✓ Puedo especificar dirección de envío (obligatorio)
- ✓ Puedo elegir método de envío: Standard ($5) o Express ($15)
- ✓ Puedo marcar el pedido como regalo
- ✓ Si es regalo, puedo agregar mensaje personalizado
- ✓ Si es regalo, puedo solicitar envoltura de regalo (+$3.50)
- ✓ Puedo agregar notas especiales para el envío
- ✓ El pedido calcula automáticamente el total incluyendo costos de envío
- ✓ El resumen del pedido muestra toda la información configurada

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-002

**Notas Técnicas:**
- Paquete: `patrones.creacional.builder`
- Implementar patrón Builder con clase interna `PedidoBuilder`
- Constructor privado en Pedido - solo el Builder puede crear instancias
- Métodos fluent interface: conMetodoEnvio(), esRegalo(), conMensajeRegalo(), etc.
- Método construir() retorna el Pedido completo
- Dependencia: requiere importar `patrones.creacional.factory.Producto`
- Imports requeridos en Main:
  ```java
  import patrones.creacional.builder.Pedido;
  import java.util.ArrayList;
  import java.util.List;
  ```

**Casos de Prueba:**
1. Pedido simple: productos + dirección + envío Standard
2. Pedido completo: productos + Express + regalo + envoltura + mensaje + notas
3. Verificar cálculo de total con diferentes métodos de envío
4. Verificar resumen muestra toda la información

---

### HU-015: Validación en Cadena de Pedidos (Patrón Chain of Responsibility)

**Como** sistema de e-commerce
**Quiero** validar pedidos a través de múltiples verificaciones secuenciales
**Para** asegurar que solo se procesen pedidos válidos

**Criterios de Aceptación:**
- ✓ Validación de stock: verificar disponibilidad de productos
- ✓ Validación de dirección: verificar dirección de envío válida
- ✓ Validación de monto: verificar monto entre $10 y $5000
- ✓ Validación de método de pago: verificar método de pago autorizado
- ✓ Las validaciones se ejecutan en secuencia (cadena)
- ✓ Si una validación falla, se detiene la cadena y se reporta el error
- ✓ Si todas las validaciones pasan, el pedido se marca como válido
- ✓ Cada validador muestra mensaje de su verificación

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-014

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.chain`
- Implementar patrón Chain of Responsibility con `ValidadorPedido` abstracto
- Validadores concretos: `ValidadorStock`, `ValidadorDireccion`, `ValidadorMontoPedido`, `ValidadorMetodoPago`
- Cada validador tiene referencia al siguiente en la cadena
- Método setSiguiente() para configurar la cadena
- Método validar() retorna boolean y llama validarSiguiente()
- Dependencia: requiere importar `patrones.creacional.builder.Pedido`
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.chain.ValidadorPedido;
  import patrones.comportamiento.chain.ValidadorStock;
  import patrones.comportamiento.chain.ValidadorDireccion;
  import patrones.comportamiento.chain.ValidadorMontoPedido;
  import patrones.comportamiento.chain.ValidadorMetodoPago;
  ```

**Casos de Prueba:**
1. Pedido válido: pasar todas las validaciones
2. Pedido con monto < $10: fallar en ValidadorMontoPedido
3. Pedido con monto > $5000: fallar en ValidadorMontoPedido
4. Verificar que validaciones se ejecutan en orden correcto

---

## Épica 8: Integración con Proveedores de Envío

### HU-016: Integrar Múltiples Sistemas de Envío (Patrón Adapter)

**Como** administrador del sistema
**Quiero** integrar diferentes proveedores de envío con APIs diferentes
**Para** ofrecer opciones de envío a los clientes sin cambiar mi código

**Criterios de Aceptación:**
- ✓ Integrar sistema DHL (unidades en kg, métodos específicos DHL)
- ✓ Integrar sistema FedEx (unidades en libras, métodos específicos FedEx)
- ✓ Integrar sistema Correos (unidades en gramos, métodos específicos Correos)
- ✓ Todos los sistemas usan interfaz común ServicioEnvio
- ✓ Los adaptadores convierten automáticamente las unidades de peso
- ✓ Calcular costo de envío según proveedor y peso
- ✓ Obtener estado del envío de manera uniforme
- ✓ El código cliente usa la misma interfaz para todos los proveedores

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-014

**Notas Técnicas:**
- Paquete: `patrones.estructural.adapter`
- Implementar patrón Adapter con interfaz `ServicioEnvio` (Target)
- Sistemas externos (Adaptees): `SistemaDHL`, `SistemaFedEx`, `SistemaCorreos`
- Adaptadores: `AdaptadorDHL`, `AdaptadorFedEx`, `AdaptadorCorreos`
- Conversiones: 1 kg = 2.20462 lbs, 1 kg = 1000 g
- Cada sistema tiene tarifas diferentes
- Imports requeridos en Main:
  ```java
  import patrones.estructural.adapter.ServicioEnvio;
  import patrones.estructural.adapter.SistemaDHL;
  import patrones.estructural.adapter.SistemaFedEx;
  import patrones.estructural.adapter.SistemaCorreos;
  import patrones.estructural.adapter.AdaptadorDHL;
  import patrones.estructural.adapter.AdaptadorFedEx;
  import patrones.estructural.adapter.AdaptadorCorreos;
  ```

**Casos de Prueba:**
1. Enviar paquete de 2.5 kg con los 3 proveedores
2. Verificar conversiones de unidades correctas
3. Verificar cálculo de costos según cada proveedor:
   - DHL: $8 base + $2/kg = $13.00
   - FedEx: $10 base + $1.50/lb ≈ $18.27
   - Correos: $5 base + $0.01/g = $30.00
4. Obtener estado de envío de cada proveedor

---

## Épica 9: Clonación y Gestión de Prototipos

### HU-017: Clonación de Productos desde Registro (Patrón Prototype)

**Como** administrador de catálogo
**Quiero** clonar productos existentes para crear variantes
**Para** acelerar la creación de productos similares sin crear desde cero

**Criterios de Aceptación:**
- ✓ Existe un registro centralizado de prototipos (RegistroPrototipos)
- ✓ Los prototipos base incluyen: laptop, smartphone, libro
- ✓ Puedo clonar cualquier prototipo del registro
- ✓ Los clones son copias profundas (deep copy) independientes
- ✓ Puedo personalizar el clon sin afectar el prototipo original
- ✓ Las especificaciones técnicas se clonan correctamente

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-002

**Notas Técnicas:**
- Paquete: `patrones.creacional.prototype`
- Interfaz genérica `Prototype<T>` con método `clonar()`
- `ProductoPrototype` implementa Prototype usando constructor de copia
- `RegistroPrototipos` es Singleton que mantiene Map de prototipos
- Deep copy mediante nuevo HashMap en constructor de copia
- Imports requeridos en Main:
  ```java
  import patrones.creacional.prototype.RegistroPrototipos;
  import patrones.creacional.prototype.ProductoPrototype;
  ```

**Casos de Prueba:**
1. Clonar laptop, modificar precio, verificar que original no cambió
2. Clonar smartphone, agregar especificación nueva, verificar independencia
3. Verificar que RegistroPrototipos es Singleton
4. Verificar Map de especificaciones es copia profunda

---

## Épica 10: Jerarquías de Catálogo

### HU-018: Gestión de Categorías y Paquetes de Productos (Patrón Composite)

**Como** administrador de catálogo
**Quiero** organizar productos en categorías jerárquicas y crear paquetes
**Para** estructurar el catálogo y ofrecer bundles con descuento

**Criterios de Aceptación:**
- ✓ Puedo crear categorías que contienen productos y subcategorías
- ✓ Puedo crear paquetes de productos con descuento automático
- ✓ El precio total se calcula recursivamente en toda la jerarquía
- ✓ Puedo agregar y eliminar componentes dinámicamente
- ✓ Los productos, categorías y paquetes se tratan uniformemente
- ✓ El sistema muestra la jerarquía con indentación apropiada

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-002

**Notas Técnicas:**
- Paquete: `patrones.estructural.composite`
- Componente base abstracto: `ComponenteCatalogo`
- Leaf: `ProductoItem` - productos individuales
- Composite: `Categoria` - contiene hijos (productos/subcategorías)
- Composite: `PaqueteProductos` - aplica porcentaje de descuento
- Usa Java 8 Streams para calcular precios totales
- Imports requeridos en Main:
  ```java
  import patrones.estructural.composite.*;
  import patrones.creacional.factory.Producto;
  ```

**Casos de Prueba:**
1. Crear categoría "Electrónica" con 2 subcategorías y verificar total
2. Crear paquete con 3 productos y 15% descuento, verificar cálculo
3. Agregar/eliminar componente y verificar actualización de precio
4. Verificar indentación correcta en mostrarDetalle()

---

## Épica 11: Procesamiento de Pedidos

### HU-019: Procesamiento con Flujo Consistente (Patrón Template Method)

**Como** sistema de procesamiento de pedidos
**Quiero** ejecutar un flujo consistente para todos los tipos de pedidos
**Para** garantizar que no se omitan pasos críticos del proceso

**Criterios de Aceptación:**
- ✓ Todos los pedidos siguen el mismo flujo de procesamiento (template)
- ✓ Los pasos invariantes son: verificar inventario, procesar pago, registrar operación
- ✓ Los pasos personalizables son: calcular costos, preparar envío, notificar cliente
- ✓ Pedidos nacionales: 16% impuestos + $5 envío
- ✓ Pedidos internacionales: 16% impuestos + 10% aranceles + $25 envío + 2% seguro + verificación aduanera
- ✓ Pedidos express: 16% impuestos + $15 envío express + verificación rápida de inventario
- ✓ Hook method `requiereVerificacionAdicional()` opcional

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-014

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.template`
- Clase abstracta `ProcesadorPedido` con método `final procesarPedido()`
- Implementaciones: `ProcesadorPedidoNacional`, `ProcesadorPedidoInternacional`, `ProcesadorPedidoExpress`
- Pasos abstractos (must override): `calcularCostos()`, `prepararEnvio()`, `notificarCliente()`
- Hook method: `requiereVerificacionAdicional()` retorna false por defecto
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.template.*;
  ```

**Casos de Prueba:**
1. Procesar pedido nacional de $100 y verificar total = $121
2. Procesar pedido internacional de $100 y verificar verificación aduanera
3. Procesar pedido express y verificar envío rápido
4. Verificar que template method ejecuta todos los pasos en orden

---

### HU-020: Gestión de Estados del Pedido (Patrón State)

**Como** sistema de seguimiento de pedidos
**Quiero** gestionar las transiciones de estado del pedido
**Para** mantener el ciclo de vida correcto y evitar transiciones inválidas

**Criterios de Aceptación:**
- ✓ Estados válidos: Nuevo → Confirmado → Enviado → Entregado
- ✓ Estado alternativo: Cancelado (desde Nuevo o Confirmado)
- ✓ No se puede cancelar un pedido ya enviado
- ✓ No se puede avanzar un pedido entregado o cancelado
- ✓ Cada estado tiene comportamiento específico
- ✓ Las transiciones son manejadas por los propios estados
- ✓ Se puede retroceder al estado anterior cuando es válido

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-014

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.state`
- Interfaz `EstadoPedido` con métodos: `siguiente()`, `anterior()`, `cancelar()`, `mostrarEstado()`
- Context: `PedidoContext` mantiene estado actual y delega operaciones
- Estados concretos: `EstadoNuevo`, `EstadoConfirmado`, `EstadoEnviado`, `EstadoEntregado`, `EstadoCancelado`
- Los estados cambian el estado del contexto mediante `pedido.setEstado()`
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.state.*;
  ```

**Casos de Prueba:**
1. Crear pedido nuevo y avanzar hasta entregado, verificar cada transición
2. Cancelar pedido desde estado Nuevo
3. Intentar cancelar pedido Enviado, verificar que no se permite
4. Verificar mensajes apropiados para operaciones inválidas

---

## Épica 12: Simplificación de Operaciones

### HU-021: Proceso de Compra Simplificado (Patrón Facade)

**Como** cliente
**Quiero** realizar una compra completa con una sola operación
**Para** no tener que interactuar con múltiples subsistemas

**Criterios de Aceptación:**
- ✓ Un único método realiza todo el proceso de compra
- ✓ El proceso incluye: crear producto → crear pedido → validar → procesar pago → generar orden
- ✓ La fachada coordina Factory, Builder, Chain, Strategy y State
- ✓ Método `compraRapida()` para compras con configuración por defecto
- ✓ El cliente no necesita conocer los subsistemas internos
- ✓ Se muestra progreso del proceso (1/5, 2/5, etc.)

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** HU-002, HU-014, HU-015, HU-007, HU-020

**Notas Técnicas:**
- Paquete: `patrones.estructural.facade`
- Clase: `TiendaFacade` con método `realizarCompraCompleta()`
- Coordina 5 subsistemas en secuencia
- Retorna `PedidoContext` para seguimiento o null si falla validación
- Imports requeridos en Main:
  ```java
  import patrones.estructural.facade.TiendaFacade;
  import patrones.comportamiento.state.PedidoContext;
  ```

**Casos de Prueba:**
1. Realizar compra completa de laptop y verificar que se ejecutan los 5 pasos
2. Realizar compra que falla validación y verificar retorno null
3. Usar compraRapida() y verificar configuración por defecto
4. Verificar que PedidoContext retornado tiene ID correcto

---

## Épica 13: Control de Acceso a Contenido Premium

### HU-022: Acceso Controlado a Productos Premium (Patrón Proxy)

**Como** sistema de contenido digital
**Quiero** controlar el acceso a productos premium
**Para** proteger contenido digital y aplicar lazy loading

**Criterios de Aceptación:**
- ✓ El proxy verifica autenticación antes de mostrar detalles
- ✓ El proxy verifica nivel de suscripción antes de permitir descarga
- ✓ Lazy loading: el objeto real se crea solo cuando es necesario
- ✓ Niveles de suscripción: FREE (sin acceso), PREMIUM (acceso completo)
- ✓ La inicialización del objeto real es costosa (simular con Thread.sleep)
- ✓ El cliente trabaja con el proxy de forma transparente

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** Ninguna

**Notas Técnicas:**
- Paquete: `patrones.estructural.proxy`
- Interfaz `ProductoPremium` con métodos: `mostrarDetalles()`, `descargarContenidoDigital()`
- RealSubject: `ProductoPremiumReal` con inicialización costosa
- Proxy: `ProductoPremiumProxy` con control de acceso y lazy loading
- Métodos del proxy: `autenticar()`, `actualizarSuscripcion()`
- Imports requeridos en Main:
  ```java
  import patrones.estructural.proxy.*;
  ```

**Casos de Prueba:**
1. Intentar acceder sin autenticación, verificar mensaje de error
2. Autenticar con nivel FREE e intentar descargar, verificar error de suscripción
3. Actualizar a PREMIUM y descargar, verificar éxito
4. Verificar que objeto real se crea solo cuando es necesario (lazy loading)

---

## Épica 14: Gestión de Promociones

### HU-023: Sistema de Descuentos con Undo/Redo (Patrón Command)

**Como** gerente de promociones
**Quiero** aplicar y deshacer descuentos con historial auditable
**Para** gestionar promociones de forma flexible y reversible

**Criterios de Aceptación:**
- ✓ Puedo aplicar descuento porcentual
- ✓ Puedo aplicar descuento fijo en monto
- ✓ Puedo remover descuentos
- ✓ Puedo deshacer la última operación (undo)
- ✓ Puedo rehacer operaciones deshechas (redo)
- ✓ El historial muestra todas las operaciones ejecutadas
- ✓ La posición actual en el historial se marca claramente

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** Ninguna

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.command`
- Interfaz `Command` con métodos: `ejecutar()`, `deshacer()`, `getDescripcion()`
- Receiver: `CarritoCompraCommand` que conoce cómo aplicar descuentos
- Comandos: `AplicarDescuentoPorcentajeCommand`, `AplicarDescuentoFijoCommand`, `RemoverDescuentoCommand`
- Invoker: `GestorPromociones` gestiona historial y posición actual
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.command.*;
  ```

**Casos de Prueba:**
1. Aplicar 3 descuentos, verificar historial
2. Deshacer 2 operaciones y verificar posición actual
3. Rehacer 1 operación y verificar estado
4. Aplicar nuevo comando en medio del historial y verificar que se eliminan comandos posteriores

---

## Épica 15: Navegación de Catálogo

### HU-024: Recorrido Flexible del Catálogo (Patrón Iterator)

**Como** usuario del catálogo
**Quiero** recorrer productos de diferentes maneras
**Para** encontrar productos según diferentes criterios

**Criterios de Aceptación:**
- ✓ Puedo iterar productos en orden de inserción
- ✓ Puedo iterar solo productos de una categoría específica
- ✓ Puedo iterar solo productos en stock
- ✓ Puedo iterar productos ordenados por precio (menor a mayor)
- ✓ Puedo iterar productos ordenados por popularidad (mayor a menor)
- ✓ Cada iterador puede reiniciarse con reset()
- ✓ Los iteradores no modifican la colección original

**Prioridad:** Alta
**Estimación:** 8 puntos
**Dependencias:** Ninguna

**Notas Técnicas:**
- Paquete: `patrones.comportamiento.iterator`
- Interfaz genérica `Iterator<T>` con métodos: `hasNext()`, `next()`, `reset()`
- Interfaz `Aggregate<T>` con método factory `crearIterador()`
- ConcreteAggregate: `Catalogo` con 5 métodos factory para diferentes iteradores
- Clase de datos: `ItemCatalogo` con atributos: nombre, precio, categoría, enStock, popularidad
- 5 iteradores concretos con diferentes estrategias
- Usa `Collections.sort()` con `Comparator` anónimo para ordenamiento
- Imports requeridos en Main:
  ```java
  import patrones.comportamiento.iterator.*;
  ```

**Casos de Prueba:**
1. Crear catálogo con 10 items, iterar con cada uno de los 5 iteradores
2. Filtrar por categoría "Electrónica" y verificar solo items de esa categoría
3. Filtrar solo items en stock y verificar flag enStock
4. Verificar ordenamiento por precio ascendente
5. Verificar ordenamiento por popularidad descendente
6. Usar reset() y verificar que vuelve al inicio

---

## Resumen Actualizado de Prioridades

### Alta (24 historias)
- HU-001 a HU-016: Historias originales y primeras expansiones
- HU-017: Prototype - Clonación de productos
- HU-018: Composite - Jerarquías de catálogo
- HU-019: Template Method - Procesamiento consistente
- HU-020: State - Gestión de estados
- HU-021: Facade - Simplificación de compras
- HU-022: Proxy - Control de acceso premium
- HU-023: Command - Gestión de promociones
- HU-024: Iterator - Navegación de catálogo

---

## Estimación Total Actualizada

**Total Puntos:** 142 puntos (78 anteriores + 64 nuevos)

### Sprint 4 (64 puntos) - 8 NUEVOS PATRONES
- Épica 9: Clonación y Prototipos (8 pts)
- Épica 10: Jerarquías de Catálogo (8 pts)
- Épica 11: Procesamiento de Pedidos (16 pts)
- Épica 12: Simplificación de Operaciones (8 pts)
- Épica 13: Control de Acceso Premium (8 pts)
- Épica 14: Gestión de Promociones (8 pts)
- Épica 15: Navegación de Catálogo (8 pts)

---

## Patrones de Diseño Implementados (16 Total)

### Patrones Creacionales (4):
1. **Singleton** (HU-001): DatabaseConnection - instancia única de BD
2. **Factory** (HU-002): ProductoFactory - creación de Libro y Electronico
3. **Builder** (HU-014): PedidoBuilder - construcción de pedidos complejos
4. **Prototype** (HU-017): RegistroPrototipos - clonación de productos

### Patrones Estructurales (5):
5. **Decorator** (HU-013): ProductoDecorador - agregar funcionalidades a productos
6. **Adapter** (HU-016): Adaptadores de envío - integrar sistemas externos
7. **Composite** (HU-018): ComponenteCatalogo - jerarquías de categorías
8. **Facade** (HU-021): TiendaFacade - simplificación de procesos de compra
9. **Proxy** (HU-022): ProductoPremiumProxy - control de acceso y lazy loading

### Patrones de Comportamiento (7):
10. **Observer** (HU-004, HU-005): Tienda/Cliente - notificaciones de ofertas
11. **Strategy** (HU-007-HU-010): EstrategiaPago - diferentes métodos de pago
12. **Chain of Responsibility** (HU-015): ValidadorPedido - validación en cadena
13. **Template Method** (HU-019): ProcesadorPedido - flujo consistente de procesamiento
14. **State** (HU-020): PedidoContext - gestión de transiciones de estado
15. **Command** (HU-023): GestorPromociones - descuentos con undo/redo
16. **Iterator** (HU-024): Catalogo - múltiples formas de recorrer productos

---

## Resumen Ejecutivo del Proyecto

### Métricas del Proyecto:
- **Total de Historias de Usuario:** 24
- **Total de Puntos de Historia:** 142 puntos
- **Patrones Implementados:** 16 (4 Creacionales + 5 Estructurales + 7 Comportamiento)
- **Clases Totales:** 68 clases organizadas en 16 paquetes
- **Líneas de Código Main.java:** ~520 líneas de demostración

### Estado del Proyecto:
- ✅ **Refactorización completada**: Estructura organizada por paquetes
- ✅ **Compilación exitosa**: Sin errores ni warnings
- ✅ **Demostración funcional**: Los 16 patrones funcionan correctamente
- ✅ **Documentación actualizada**: CLAUDE.md, README.md, README_JAVA.md, diagramas UML y este documento

### Próximos Pasos Recomendados:
1. **Testing**: Implementar pruebas unitarias con JUnit para cada patrón
2. **CI/CD**: Configurar pipeline de integración continua
3. **JavaDoc**: Agregar documentación JavaDoc a todas las clases públicas
4. **Persistencia**: Implementar persistencia real con JPA/Hibernate
5. **API REST**: Exponer funcionalidad a través de Spring Boot REST API
6. **Frontend**: Crear interfaz web con React o Angular

### Tecnologías Utilizadas:
- **Lenguaje:** Java (versión compatible con Java 8+)
- **Organización:** Package-based architecture
- **Patrones:** GoF (Gang of Four) Design Patterns
- **Documentación:** PlantUML para diagramas, Markdown para docs
- **IDE Recomendado:** IntelliJ IDEA, Eclipse, VS Code con Java Extension Pack

### Guía de Compilación y Ejecución:

**Opción 1: Compilación Manual (Desde raíz del proyecto)**
```bash
# Windows
javac -d out -encoding UTF-8 src\Main.java src\patrones\creacional\**\*.java src\patrones\estructural\**\*.java src\patrones\comportamiento\**\*.java
java -cp out Main

# Linux/Mac
javac -d out -encoding UTF-8 src/Main.java src/patrones/creacional/**/*.java src/patrones/estructural/**/*.java src/patrones/comportamiento/**/*.java
java -cp out Main
```

**Opción 2: Usar find para compilar todos los archivos**
```bash
# Linux/Mac
find src -name "*.java" -print | xargs javac -d out -encoding UTF-8 -cp src
java -cp out Main

# Windows (PowerShell)
Get-ChildItem -Path src -Recurse -Filter *.java | ForEach-Object { javac -d out -encoding UTF-8 -cp src $_.FullName }
java -cp out Main
```

**Opción 3: Desde IntelliJ IDEA**
1. Abrir el proyecto en IntelliJ IDEA
2. Marcar `src/` como "Sources Root" (clic derecho → Mark Directory as → Sources Root)
3. Ejecutar Main.java (clic derecho → Run 'Main.main()')

**Verificación de Compilación Exitosa:**
```bash
# Debe crear la siguiente estructura en out/:
out/
├── Main.class
└── patrones/
    ├── creacional/
    │   ├── singleton/DatabaseConnection.class
    │   ├── factory/Producto.class, Libro.class, etc.
    │   └── builder/Pedido.class, Pedido$PedidoBuilder.class
    ├── estructural/
    │   ├── decorator/ProductoDecorador.class, etc.
    │   └── adapter/ServicioEnvio.class, etc.
    └── comportamiento/
        ├── observer/Observer.class, Cliente.class, Tienda.class
        ├── strategy/EstrategiaPago.class, etc.
        └── chain/ValidadorPedido.class, etc.
```

**Salida Esperada al Ejecutar:**
```
=====================================================
DEMOSTRACIÓN DE 16 PATRONES DE DISEÑO EN JAVA
=====================================================

>>> 1. PATRÓN SINGLETON <<<
...
>>> 2. PATRÓN FACTORY <<<
...
>>> 3. PATRÓN OBSERVER <<<
...
>>> 4. PATRÓN STRATEGY <<<
...
>>> 5. PATRÓN DECORATOR <<<
...
>>> 6. PATRÓN BUILDER <<<
...
>>> 7. PATRÓN CHAIN OF RESPONSIBILITY <<<
...
>>> 8. PATRÓN ADAPTER <<<
...
>>> 9. PATRÓN PROTOTYPE <<<
...
>>> 10. PATRÓN COMPOSITE <<<
...
>>> 11. PATRÓN TEMPLATE METHOD <<<
...
>>> 12. PATRÓN STATE <<<
...
>>> 13. PATRÓN FACADE <<<
...
>>> 14. PATRÓN PROXY <<<
...
>>> 15. PATRÓN COMMAND <<<
...
>>> 16. PATRÓN ITERATOR <<<
...
=====================================================
FIN DE LA DEMOSTRACIÓN - 16 PATRONES IMPLEMENTADOS
CREACIONALES: 4 | ESTRUCTURALES: 5 | COMPORTAMIENTO: 7
=====================================================
```

---

*Documento actualizado: Diciembre 2025 - Versión 3.0 con 16 Patrones Gang of Four*
