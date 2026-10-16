# Análisis del proyecto Java original

Análisis del proyecto "16 Patrones en Java" (carpeta `src/` del repositorio), hecho durante el port a Python. Combina una descripción de la arquitectura con una lista de las rarezas y errores que aparecieron al traducir cada clase.

## 1. Qué es el proyecto

Un proyecto **educativo** en Java puro (JDK 8+, sin frameworks ni dependencias) que demuestra los 16 patrones de diseño del *Gang of Four* sobre un único dominio: un **e-commerce**. Son 68 archivos `.java` en total, contando `Main.java`, que ejecuta una demostración de todos los patrones en secuencia (67 clases de patrones más `Main`).

Se compila con `javac -encoding UTF-8 @sources.txt` desde `src/` y se ejecuta con `java Main`. No incluye pruebas automatizadas, ni `pom.xml`, ni `build.gradle` (el `CLAUDE.md` original los sugiere como opcionales).

Material de apoyo en la raíz: `README.md`, `README_JAVA.md`, `CLAUDE.md`, `HISTORIAS_USUARIOS.md` (historias HU-001 a HU-016 con criterios de aceptación), `diagrama_clases.puml`, `diagrama_secuencia.puml` y las imágenes `Patrones.png` y `secuencia.png`.

## 2. Organización de paquetes

Los paquetes se organizan **por categoría GoF**, no por funcionalidad de negocio:

```
patrones/
├── creacional/       singleton, factory, builder, prototype
├── estructural/      decorator, adapter, composite, facade, proxy
└── comportamiento/   observer, strategy, chain, template, state, command, iterator
```

Un paquete por patrón, con las clases del patrón adentro. Racional (documentado en el `CLAUDE.md` original):

- Es fácil encontrar todas las implementaciones de una categoría.
- Separa responsabilidades por tipo de patrón.
- Facilita el aprendizaje agrupando patrones relacionados.
- Replica la clasificación del libro de GoF.

La contracara: en un sistema real, el código de dominio (producto, pedido, pago) quedaría repartido en varios paquetes según qué patrón lo use. En una arquitectura "por feature" `Producto`, `Pedido` y `CarritoCompra` vivirían juntos. Acá se sacrifica eso a favor de la claridad pedagógica. Una consecuencia: `Producto` está en `creacional.factory` pero lo usan `decorator`, `composite`, `strategy`, `builder` y `command`.

## 3. Dependencias entre patrones

El dominio gira en torno a `Producto` (jerarquía de `factory`) y `Pedido` (de `builder`). No es un grafo de capas limpio: es una red de reutilización.

```
creacional.factory (Producto, Libro, Electronico, ProductoFactory)
    ├──> creacional.builder        Pedido guarda List<Producto>
    ├──> estructural.decorator     ProductoDecorador EXTIENDE Producto y envuelve un Producto
    ├──> comportamiento.strategy   CarritoCompra guarda List<Producto>
    ├──> comportamiento.command    CarritoCompraCommand guarda List<Producto>
    └──> estructural.facade        TiendaFacade crea productos

creacional.builder (Pedido)
    └──> comportamiento.chain      ValidadorPedido valida un Pedido (ValidadorMontoPedido llama a calcularTotal())

comportamiento.state (PedidoContext, EstadoPedido y 5 estados)
    └──> estructural.facade        el facade crea un PedidoContext para el seguimiento
         (PedidoContext es independiente de la clase Pedido del Builder)

comportamiento.chain + strategy + state + builder + factory
    └──> estructural.facade        TiendaFacade las coordina en realizarCompraCompleta()
```

Patrones **autocontenidos** (no dependen de otros del proyecto): Singleton, Prototype (`ProductoPrototype` NO extiende `Producto`; es una jerarquía aparte), Observer, Adapter, Composite (`ProductoItem` es hoja propia, no usa `Producto`), Template Method, Proxy (su propio `ProductoPremium`) e Iterator (su propio `ItemCatalogo`).

Observaciones:

- **Hay tres modelos de "producto" paralelos**: `Producto` (factory), `ProductoPrototype` (prototype) e `ItemCatalogo` (iterator), más `ProductoItem` (composite) y `ProductoPremium` (proxy). En el dominio real serían la misma entidad; acá se duplican para que cada patrón pueda estudiarse aislado. Es una decisión pedagógica razonable, pero conviene saberla.
- **Facade es el único punto de integración real**: es el patrón que demuestra cómo se combinan cinco más.
- No hay ciclos de dependencia entre paquetes. En Java no importaría igual (el compilador los resuelve), pero en Python sí hay que cuidarlos entre los estados y su contexto (ver `JAVA_VS_PYTHON.md`).

## 4. Flujo de `Main.java`

`Main.main()` es una demostración lineal de 520 líneas (423 sin contar las vacías), con un bloque por patrón, cada uno con un encabezado `>>> N. PATRÓN X <<<`. Todos los datos están escritos a mano (sin lectura de archivos ni entrada del usuario). El orden real:

| # | Patrón | Qué muestra |
|---|--------|-------------|
| 1 | Singleton | Dos `getInstance()` y comparación con `==` |
| 2 | Factory | Dos libros y dos electrónicos con `ProductoFactory` (`crearLibro` / `crearElectronico`) |
| 3 | Observer | Tienda "TechStore", 3 clientes suscriptos, ofertas, una baja |
| 4 | Strategy | 3 carritos con tarjeta, efectivo (5%) y PayPal |
| 5 | Decorator | Envoltura, seguro, garantía y varios apilados |
| 6 | Builder | Pedido simple y pedido complejo |
| 7 | Chain | Cadena Stock → Dirección → Monto → Pago con dos pedidos |
| 8 | Adapter | Envíos con DHL, FedEx y Correos por la misma interfaz |
| 9 | Prototype | Clona dos veces el prototipo `"laptop"` ("Laptop Gaming" y "Laptop Oficina"), los personaliza y comprueba que son objetos distintos (el registro también tiene `smartphone` y `libro`, pero `Main` no los usa) |
| 10 | Composite | Árbol Electrónica → Computadoras/Accesorios y un paquete con descuento ("Paquete Gamer", 15%) |
| 11 | Template Method | Pedido nacional, internacional y express |
| 12 | State | Flujo normal y flujo de cancelación |
| 13 | Facade | `realizarCompraCompleta`, `compraRapida`, `consultarEstadoPedido` |
| 14 | Proxy | Acceso sin login, con login sin suscripción y con suscripción; lazy loading |
| 15 | Command | Descuentos con deshacer/rehacer e historial |
| 16 | Iterator | Recorridos por categoría, stock, rango de precio y popularidad |

El orden no es el de las categorías (por ejemplo, Facade y Proxy, que son estructurales, aparecen tras State). Parece reflejar el orden en que se fueron agregando patrones (los primeros 8 serían los originales y del 9 al 16 se sumaron después; el repo conserva `NUEVOS_PATRONES.md`, `HISTORIAS_NUEVAS.md` y `CAMBIOS_REALIZADOS.md` sobre esa ampliación; es una inferencia, no un dato verificado). Los números de línea que cita el `CLAUDE.md` original para cada sección están desactualizados respecto de `Main.java` actual.

## 5. Fortalezas

- **Alcance completo y coherente**: los 16 patrones en un mismo dominio, con nombres en español consistentes.
- **Cero dependencias**: se compila con `javac` y nada más; ideal para clases.
- **Estructura GoF fiel**: roles reconocibles (Component/Leaf/Composite, Context/State, Invoker/Receiver/Command...).
- **Buena documentación**: historias de usuario con criterios de aceptación, diagramas de clases y de secuencia, y un `CLAUDE.md` muy detallado.
- **Ejemplos con valor didáctico**: `final` en el Template Method, constructor privado en el Singleton, constructor de copia en el Prototype, clase interna estática en el Builder, undo/redo con puntero en el Command.
- **Simulaciones honestas**: los sistemas externos (base de datos, DHL, FedEx, Correos) están claramente marcados como simulados.

## 6. Rarezas y errores encontrados al portar

Cada punto se verificó contra el código Java. Para cada uno se indica cómo lo trata el port a Python.

> **Actualización:** una revisión posterior del port (ver [`REVISION_PATRONES.md`](REVISION_PATRONES.md)) decidió **corregir** varios de estos defectos en lugar de copiarlos. Quedan corregidos en Python los puntos **1** (descuento fijo), **10** (el total calculado ahora se cobra; el orden `[3]` antes de `[2]` se conserva), **14** (el `Pedido` guarda una `tuple`; `registrarPrototipo` sigue por referencia), **16** (tipo de producto validado y total coherente en Facade) y, en parte, **21** (Observer itera una copia, aunque sigue sin aislar excepciones). Cada uno lleva una marca "Port:" abajo. La lista completa está en [`JAVA_VS_PYTHON.md`](JAVA_VS_PYTHON.md#diferencias-deliberadas-con-el-java-original).

### Errores de comportamiento

1. **División por cero en `aplicarDescuentoFijo` con carrito vacío.** `CarritoCompraCommand.aplicarDescuentoFijo` calcula `(monto / totalOriginal) * 100`. Con `totalOriginal == 0`, en Java la división de `double` no lanza excepción: da `Infinity` o `NaN` y el descuento queda corrupto en silencio. **En Python** un `/` por cero lanzaría `ZeroDivisionError`. **Port: corregido de raíz.** El descuento fijo ya no se convierte en porcentaje: se guarda como monto (`DescuentoVigente`), así que no hay división, con el carrito vacío el total es $0.00 y el monto se aplica en cuanto haya productos. Además el total nunca baja de 0 y se validan porcentaje (0..100) y monto (>= 0).
2. **`Tienda.desuscribir` informa éxito aunque el cliente no estuviera suscripto.** `clientes.remove(cliente)` devuelve `false` si no estaba, pero igual se imprime "Cliente desuscrito...". **El port lo mantiene** (y comprueba la pertenencia para que `list.remove` no lance `ValueError`).
3. **`Categoria.getCantidadProductos()` no cuenta los productos dentro de un `PaqueteProductos`.** Solo suma `ProductoItem` y recurre en `Categoria`; un paquete anidado en una categoría aporta 0. Es inconsistente con `getPrecioTotal()`, que sí incluye a los paquetes. **El port lo mantiene** y lo documenta.
4. **`EstadoEntregado.anterior()` vuelve a `EstadoEnviado`.** Un estado descrito como "terminal" permite retroceder ("procesar devolución"), pero `siguiente()` y `cancelar()` sí están bloqueados. Es una decisión de diseño, no un bug, pero contradice la descripción "EstadoEntregado (terminal state)". **El port lo mantiene.**
5. **La variable `descuento5` de `Main` aplica 15%.** `Command descuento5 = new AplicarDescuentoPorcentajeCommand(carritoCmd, 15, "Black Friday");` El nombre quedó de una versión anterior con 5%. Variable engañosa, sin consecuencias funcionales.

### Simulaciones "siempre verdaderas" y datos fijos

6. **`ValidadorStock`, `ValidadorDireccion` y `ValidadorMetodoPago` están hardcodeados para pasar.** Cada uno declara una variable (`stockDisponible = true`, `direccionValida = true`, `metodoValido = true`) y luego hace `if` sobre ella: la rama de error es código muerto. En la práctica la cadena solo puede fallar en `ValidadorMontoPedido` (total entre $10 y $5000, que sí tiene lógica). Ni siquiera se valida que la dirección no esté vacía. **El port lo mantiene** para conservar la estructura de un validador real.
7. **`AdaptadorDHL` ignora la dirección al calcular el costo y fija la zona "nacional".** `calcularCosto(direccion, peso)` llama a `calculateShippingPrice(peso, "nacional")`. Además `SistemaDHL.calculateShippingPrice` ignora el parámetro `zone`: la tarifa siempre es `$8 + $2/kg`. Es decir, el parámetro zona no sirve para nada en ningún nivel. **El port lo mantiene.**

### Formato y plataforma

8. **`printf`/`String.format` dependen del *locale*.** `ValidadorMontoPedido` usa `System.out.printf("... $%.2f\n", total)` y varias clases usan `String.format("%.2f", ...)`. En una JVM con locale `es_*` el separador decimal sale como coma (`1234,50`), en `en_*` con punto. Los f-strings de Python no dependen del locale. Si se comparan las salidas de ambas versiones en una máquina en español, difieren en esos números. Además `printf` usa `\n` literal en lugar de `%n`.
9. **El orden de impresión del `HashMap` en el Prototype no está definido.** `ProductoPrototype` guarda las especificaciones en un `HashMap`; al mostrarlas, el orden depende del hash de las claves y no del orden de inserción. Una salida distinta entre JVM/versiones es posible (aunque en la práctica sea estable para las mismas claves). Python usa `dict`, que conserva el orden de inserción, así que el orden impreso difiere del de Java. Con `LinkedHashMap` en Java sería determinista.
10. **El Template Method imprime el paso `[3]` antes que el `[2]`.** El método plantilla ejecuta `verificarInventario()` `[1]`, `calcularCostos()` `[3]`, `procesarPago()` `[2]`: la numeración de los mensajes no coincide con el orden de ejecución. **El port mantiene el orden** y lo advierte en el docstring. **Port: corregido, además, un defecto relacionado que aquí no estaba listado**: en Java `calcularCostos` es `void` y `procesarPago(monto)` cobra el monto original, no el total calculado (se muestra $585.00 y se cobran $500.00). En Python `calcular_costos` devuelve el total y es el que se cobra.
11. **`%.0f` de Java y `:.0f` de Python redondean distinto** (half-up frente a half-even) en valores terminados en .5; afecta solo a descuentos de ese tipo en `PaqueteProductos`.

### Modelo de datos y diseño

12. **Se usa `double` para dinero.** Todos los precios, impuestos y descuentos son `double`. Es aceptable para una demo (el propio `CLAUDE.md` lo aclara), pero en producción debe usarse `BigDecimal` (en Python, `decimal.Decimal`): la aritmética binaria acumula errores de redondeo (`0.1 + 0.2 != 0.3`) y las comparaciones de límites como `total < 10.00` pueden fallar por milésimas.
13. **Tres jerarquías de producto paralelas** (`Producto`, `ProductoPrototype`, `ItemCatalogo`) más `ProductoItem` y `ProductoPremium`. Ver sección 3.
14. **`Pedido` guarda la lista de productos por referencia.** `Pedido(builder)` hace `this.productos = builder.productos`, sin copia defensiva: si el cliente modifica la lista después de `construir()`, el pedido cambia. Lo mismo ocurre con `registrarPrototipo`, que guarda la referencia recibida. **Port: corregido para `Pedido`** (guarda una `tuple` copiada al construir). `registrar_prototipo` sigue guardando la referencia recibida, como Java.
15. **`TiendaFacade.compraRapida` no hace ninguna compra.** Solo imprime el producto, el precio y la dirección, y "Compra procesada con configuración por defecto": no crea pedido, no valida, no cobra. Es un método de demostración sin lógica. **El port lo mantiene.**
16. **`TiendaFacade.realizarCompraCompleta` trata cualquier tipo que no sea `"libro"` como electrónico** (con 12 meses de garantía fijos y autor "Autor Desconocido" para libros). No valida el tipo, a diferencia de `ProductoFactory.crearProducto`, que lanza excepción ante un tipo inválido. Además `PedidoContext` se crea con el `precio` del producto, no con el total del pedido (que incluye los $15 de envío Express), y se cobra ese mismo precio: se valida $914.99 pero se cobran $899.99. **Port: corregido.** Delega en `ProductoFactory.crear_producto` (ignora mayúsculas; un tipo desconocido rechaza la compra y devuelve `None`) y valida, cobra y registra `pedido.calcular_total()` ($914.99). Los ids de seguimiento llevan un contador, así que no se repiten.
17. **`Thread.sleep` captura `InterruptedException` y solo hace `printStackTrace()`.** En `ProductoPremiumReal` la interrupción se traga en lugar de restaurar el estado de interrupción del hilo (`Thread.currentThread().interrupt()`). Es la forma típica pero poco recomendable de manejarla.
18. **`ValidadorMontoPedido` valida el total que incluye envío y envoltura** (`Pedido.calcularTotal()` suma $15 si es Express, $5 si es Standard, y $3.50 por envoltura), no solo la suma de productos. Puede sorprender: con envío Standard ($5), productos por $5.00 pasan (total $10.00) y por $4.99 no (total $9.99). Los límites son inclusivos.
19. **`PagoEfectivo` imprime el monto sin descuento y después el total con descuento.** "Pagando $100.0 en efectivo. Se aplicó 5% descuento." seguido de "Total a pagar: $95.00": el primer mensaje contradice al segundo. **El port lo mantiene.**
20. **El `Singleton` combina `synchronized` en `getInstance()` con inicialización diferida.** Es correcto pero toma el lock en cada llamada (el *double-checked locking* o el *holder idiom* lo evitarían). Un detalle de eficiencia, irrelevante para la demo.
21. **Las ofertas de `Tienda` se notifican de forma síncrona** y sin aislamiento de errores: si un observador lanza una excepción, los siguientes no se enteran. **Port: en parte.** Itera sobre una copia de la lista, así que un observador que se da de baja durante la notificación no hace que se salte al siguiente; el aislamiento de excepciones no se agregó.
22. **El `CLAUDE.md` original queda desactualizado en algunos puntos**: cita números de línea de `Main.java` que ya no coinciden, y la estructura que describe lista `patronesJava8-main/` como raíz.

### Ausencia de pruebas

23. **No hay tests en el proyecto Java.** El `CLAUDE.md` solo incluye "sugerencias" con JUnit 5. Todo se valida leyendo la salida de `Main`. Esto tiene dos consecuencias: (a) los comportamientos descritos arriba (bugs y rarezas) nunca fueron detectados por una prueba; (b) la salida por consola mezcla lógica y presentación, lo que dificulta probar: casi todos los métodos hacen `System.out.println` en lugar de devolver valores. El port a Python incluye 286 tests con `unittest` (99 % de cobertura de ramas) que capturan la salida con `contextlib.redirect_stdout` cuando hace falta.

## 7. Resumen de cómo trata el port cada hallazgo

| Hallazgo | Decisión en el port |
|----------|---------------------|
| Descuento fijo (carrito vacío, porcentaje que cambia, totales negativos) | **Corregido**: se guarda como monto, total >= 0, validaciones |
| Template: se calcula un total y se cobra otro | **Corregido**: se cobra el total calculado |
| Facade: se valida un total y se cobra otro; tipo no validado | **Corregido** |
| `Pedido` guarda la lista por referencia | **Corregido** (`tuple`); `registrar_prototipo` se mantiene |
| Observer: baja durante la notificación | **Corregido** (copia); sin aislamiento de excepciones |
| `desuscribir` imprime éxito sin estar suscripto | Mantenido |
| `Categoria.cantidad_productos` sin paquetes | Mantenido, documentado |
| `EstadoEntregado.anterior` | Mantenido |
| Validadores siempre verdaderos | Mantenido |
| `AdaptadorDHL` ignora dirección/zona | Mantenido |
| Orden `[3]` antes de `[2]` | Mantenido |
| `HashMap` vs orden de inserción | Difiere (Python respeta inserción) |
| `printf` y locale | Difiere (f-strings no dependen del locale) |
| Redondeo `%.0f` | Difiere en casos .5 |
| `double` para dinero | Mantenido (`float`); se recomienda `Decimal` |
| `compra_rapida` sin lógica | Mantenido |
| Sin tests | **Agregados** (`unittest`, stdlib) |

La regla original del port fue: *mantener el comportamiento observable de Java salvo cuando el equivalente literal sea un error de ejecución en Python* (como la división por cero). Tras la revisión se amplió: *también se corrigen los defectos que hacen que el patrón enseñe algo falso* (validar un monto y cobrar otro, descartar un resultado calculado). En ambos casos cada diferencia queda documentada en el docstring del módulo correspondiente y en la sección "Diferencias deliberadas con el Java original" de `JAVA_VS_PYTHON.md`.
