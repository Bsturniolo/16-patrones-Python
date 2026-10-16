# Java vs Python: los 16 patrones lado a lado

Este documento compara, patrón por patrón, el código del proyecto Java original con el port a Python. Los snippets de Python son los reales del repositorio (algunos abreviados); los de Java son los equivalentes del proyecto original.

Cada patrón tiene cuatro partes: **Java**, **Python**, **Qué cambió y por qué** y **La alternativa pythónica**.

Una advertencia que vale para todo el documento: los patrones de GoF nacieron para lenguajes como C++ y Smalltalk, donde hacen falta clases e interfaces para resolver cosas que otros lenguajes resuelven con funciones o con el propio lenguaje. En Python varios patrones son *una línea* o *ya vienen incluidos*. Este port **mantiene la estructura GoF a propósito** (para que el patrón se vea y se pueda comparar con Java), pero te muestra cuándo conviene no usarla.

## Índice

1. [Singleton](#1-singleton) · 2. [Factory](#2-factory) · 3. [Builder](#3-builder) · 4. [Prototype](#4-prototype)
5. [Decorator](#5-decorator) · 6. [Adapter](#6-adapter) · 7. [Composite](#7-composite) · 8. [Facade](#8-facade) · 9. [Proxy](#9-proxy)
10. [Observer](#10-observer) · 11. [Strategy](#11-strategy) · 12. [Chain of Responsibility](#12-chain-of-responsibility) · 13. [Template Method](#13-template-method) · 14. [State](#14-state) · 15. [Command](#15-command) · 16. [Iterator](#16-iterator)
17. [Mapeos generales del lenguaje](#17-mapeos-generales-del-lenguaje)
18. [Diferencias deliberadas con el Java original](#diferencias-deliberadas-con-el-java-original)

---

## 1. Singleton

**Java**

```java
public class DatabaseConnection {
    private static DatabaseConnection instance;
    private DatabaseConnection() { /* ... */ }

    public static synchronized DatabaseConnection getInstance() {
        if (instance == null) {
            instance = new DatabaseConnection();
        }
        return instance;
    }
}
```

**Python** (`creacional/singleton/database_connection.py`)

```python
class DatabaseConnection:
    _instance: ClassVar[DatabaseConnection | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> DatabaseConnection:
        if DatabaseConnection._instance is None:
            with DatabaseConnection._lock:
                if DatabaseConnection._instance is None:  # doble verificación (thread-safe)
                    instancia = super().__new__(cls)
                    instancia._connection_string = "mysql://localhost:3306/midb"
                    print(f"Conexión a BD creada: {instancia._connection_string}")
                    DatabaseConnection._instance = instancia
        return DatabaseConnection._instance

    @classmethod
    def get_instance(cls) -> DatabaseConnection:
        return cls()
```

**Qué cambió y por qué**

- Python no tiene constructores `private`. Se intercepta la creación con `__new__`, que decide si crear o devolver la instancia existente: `DatabaseConnection()` y `DatabaseConnection.get_instance()` dan el mismo objeto.
- `synchronized` se reemplaza por un `threading.Lock` con *doble verificación*, para no bloquear en cada acceso.
- La inicialización vive en `__new__`, no en `__init__`, porque Python vuelve a llamar a `__init__` cada vez que se escribe `DatabaseConnection()`.
- `getInstance()` pasa a `get_instance()` (snake_case).
- La instancia se guarda siempre en `DatabaseConnection._instance` y no en `cls._instance`: así una subclase **comparte** la instancia única en lugar de crear la suya (ver [Diferencias deliberadas](#diferencias-deliberadas-con-el-java-original)).

**La alternativa pythónica**: un **módulo ya es un singleton**. Python importa cada módulo una sola vez y lo guarda en `sys.modules`.

```python
# db.py
class _DatabaseConnection: ...


db = _DatabaseConnection()  # esta es "la" instancia

# en otro archivo
from db import db  # siempre el mismo objeto
```

Si necesitás control fino (inicialización perezosa, tests), una función con `functools.cache` también alcanza. Muchos programadores Python sostienen que el Singleton clásico es casi siempre innecesario.

---

## 2. Factory

**Java**

```java
public class ProductoFactory {
    public static Producto crearProducto(String tipo, String nombre, double precio, String extra) {
        switch (tipo.toLowerCase()) {
            case "libro":       return new Libro(nombre, precio, extra);
            case "electronico": return new Electronico(nombre, precio, Integer.parseInt(extra));
            default: throw new IllegalArgumentException("Tipo de producto no válido: " + tipo);
        }
    }
}
```

**Python** (`creacional/factory/producto_factory.py`)

```python
class ProductoFactory:
    # Registro compartido: tipo (en minúsculas) -> constructor(nombre, precio, extra).
    _CONSTRUCTORES: ClassVar[dict[str, Callable[[str, float, str], Producto]]] = {
        "libro": _crear_libro,
        "electronico": _crear_electronico,
    }

    @classmethod
    def registrar(cls, tipo: str, constructor: Callable[[str, float, str], Producto]) -> None:
        """Registra un tipo nuevo (o reemplaza uno existente). Ignora mayúsculas."""
        cls._CONSTRUCTORES[tipo.lower()] = constructor

    @classmethod
    def crear_producto(cls, tipo: str, nombre: str, precio: float, extra: str) -> Producto:
        try:
            constructor = cls._CONSTRUCTORES[tipo.lower()]
        except KeyError:
            raise ValueError(f"Tipo de producto no válido: {tipo}") from None
        return constructor(nombre, precio, extra)
```

**Qué cambió y por qué**

- El `switch` sobre un `String` pasa a un **registro a nivel de clase** (`_CONSTRUCTORES`, tipo → constructor). Agregar un producto nuevo es llamar a `ProductoFactory.registrar(...)` desde afuera, **sin editar la clase**: eso sí cumple Open/Closed. (Con un diccionario local dentro del método, como se hacía antes, había que editar el método, así que el argumento era falso. El equivalente directo del `switch` es `match`/`case`, que sí obliga a editar.)
- `crear_producto` es un `@classmethod` para poder leer el registro de la clase; la búsqueda ignora mayúsculas (`"LIBRO"` funciona) y un tipo inválido lanza `ValueError`.
- `IllegalArgumentException` → `ValueError`.
- `Producto` es una `abc.ABC` con `@abstractmethod` (ver [sección 17](#17-mapeos-generales-del-lenguaje)).
- `from None` oculta el `KeyError` interno, así el traceback muestra solo el error de negocio.

**La alternativa pythónica**: las clases son objetos de primera clase, así que el propio diccionario puede ser la fábrica (`REGISTRO = {"libro": Libro, "electronico": Electronico}`), o directamente pasar la clase como argumento. Una "factory" suele ser una función suelta, no una clase con métodos estáticos.

---

## 3. Builder

**Java**

```java
Pedido pedido = new Pedido.PedidoBuilder(productos, "Calle 123")
    .conMetodoEnvio("Express")
    .conMensajeRegalo("¡Feliz cumple!")
    .conNotasEspeciales("Tocar timbre")
    .construir();
```

**Python** (`creacional/builder/pedido.py`)

```python
pedido = (
    Pedido.PedidoBuilder(productos, "Calle 123")
    .con_metodo_envio("Express")
    .con_mensaje_regalo("¡Feliz cumple!")
    .con_notas_especiales("Tocar timbre")
    .construir()
)


class Pedido:
    def __init__(self, builder: Pedido.PedidoBuilder) -> None:  # uso interno
        self._productos: tuple[Producto, ...] = tuple(builder._productos)
        ...

    class PedidoBuilder:
        def con_metodo_envio(self, metodo_envio: str) -> Self:
            self._metodo_envio = metodo_envio
            return self  # interfaz fluida
```

**Qué cambió y por qué**

- La `static class` interna de Java se anida igual en Python (`Pedido.PedidoBuilder`).
- No existe `private`: el constructor de `Pedido` queda "interno" por convención.
- Los getters pasan a `@property` de solo lectura.
- Se mantiene la interfaz fluida (`return self`); por eso la cadena se envuelve en paréntesis para poder partirla en líneas.
- Los métodos fluidos se anotan `-> Self` (`typing.Self`, 3.11+) en lugar de `-> Pedido.PedidoBuilder`: si alguien deriva el builder y le agrega métodos, el encadenamiento conserva el tipo derivado (`BuilderConPrioridad(...).con_metodo_envio("Express").con_prioridad()` pasa mypy).
- Diferencia con Java: Java guarda la lista de productos por referencia. Aquí `Pedido` la convierte en una `tuple` al construir, así que es independiente de la lista del llamador y de otros `Pedido` creados con el mismo builder; `pedido.productos` devuelve esa tupla de solo lectura.
- Que el constructor de `Pedido` sea "interno" es solo una convención: Python no puede hacerlo privado y nada impide llamarlo directamente.

**La alternativa pythónica**: **argumentos con nombre y valores por defecto**. Python ya resuelve el problema que motivó al Builder (constructores con muchos parámetros opcionales), así que casi nunca hace falta una clase aparte:

```python
@dataclass
class Pedido:
    productos: list[Producto]
    direccion_envio: str
    metodo_envio: str = "Standard"
    es_regalo: bool = False
    mensaje_regalo: str | None = None
    envoltura_regalo: bool = False
    notas_especiales: str | None = None


Pedido(productos, "Calle 123", metodo_envio="Express", mensaje_regalo="¡Feliz cumple!")
```

El Builder sigue siendo útil cuando la construcción tiene pasos ordenados o validaciones entre campos.

---

## 4. Prototype

**Java**

```java
public ProductoPrototype clonar() {
    return new ProductoPrototype(this);   // constructor de copia
}
private ProductoPrototype(ProductoPrototype original) {
    this.especificaciones = new HashMap<>(original.especificaciones);
}
```

**Python** (`creacional/prototype/producto_prototype.py`)

```python
def clonar(self) -> Self:
    """Copia superficial: el dict se duplica, los valores se comparten."""
    copia = copy.copy(self)  # conserva el tipo real (subclases incluidas)
    copia._especificaciones = dict(self._especificaciones)
    return copia


def clonar_profundo(self) -> Self:
    """Copia profunda: nada se comparte con el original, ni valores mutables."""
    return copy.deepcopy(self)
```

**Qué cambió y por qué**

- `interface Prototype<T>` → `class Prototype[T](ABC)`: genéricos con la sintaxis de Python 3.12 (PEP 695). Antes de 3.12 se escribía `T = TypeVar("T")` a nivel de módulo y `class Prototype(ABC, Generic[T])`; la forma nueva declara `T` en la propia clase, como el `<T>` de Java, y no necesita `Generic`.
- `clonar()` y `clonar_profundo()` devuelven `Self`: como `copy.copy(self)` conserva la subclase, el verificador de tipos sabe que `oferta.clonar()` es una `Oferta` (con `-> ProductoPrototype` habría que hacer un cast).
- `clonar()` es una copia **superficial**: `copy.copy(self)` duplica el objeto (y conserva su tipo real, subclases incluidas) y `dict(...)` duplica el contenedor de especificaciones, pero **no** los valores. Alcanza porque los valores son `str` (inmutables). Con un valor mutable, por ejemplo una `list`, original y clon compartirían ese valor y modificarlo en el clon cambiaría el original.
- Para ese caso está `clonar_profundo()`, que usa `copy.deepcopy` y duplica todo el grafo de objetos. (Antes el código y este documento llamaban "copia profunda" a `dict(...)`, y eso era falso.)
- `RegistroPrototipos` es un singleton (con `__new__` + `Lock`, igual que `DatabaseConnection`) que entrega **siempre un clon**, nunca el original. Como en `DatabaseConnection`, la instancia se guarda en `RegistroPrototipos._instance` (no en `cls._instance`): una subclase comparte el registro único.
- **Decisión de diseño:** un tipo desconocido lanza `ValueError` (en Java, `IllegalArgumentException`) y no `KeyError`. Es un *argumento* inválido de `obtener_prototipo(tipo)`, igual que en `ProductoFactory.crear_producto`, que usa la misma excepción; además `str(KeyError("x"))` agrega comillas al mensaje. `KeyError` sería lo natural si el registro se usara como un mapeo (`registro["laptop"]`).
- Orden de impresión: Java usa `HashMap` (orden por hash, no definido) y Python `dict` (orden de inserción). Las especificaciones pueden imprimirse en distinto orden entre ambas versiones.

**La alternativa pythónica**: el módulo `copy`.

```python
import copy

clon = copy.deepcopy(laptop_base)  # una línea, sin escribir clonar()
```

`copy.copy` es superficial; `copy.deepcopy` copia recursivamente (es lo que usa `clonar_profundo()`). Podés personalizarlo con `__copy__`/`__deepcopy__`.

---

## 5. Decorator

**Java**

```java
public abstract class ProductoDecorador extends Producto {
    protected Producto productoDecorado;
    @Override public double getPrecio() { return productoDecorado.getPrecio(); }
}
public class SeguroDecorador extends ProductoDecorador {
    private static final double PORCENTAJE_SEGURO = 0.10; // 10% del precio base
    @Override public double getPrecio() { return productoDecorado.getPrecio() * (1 + PORCENTAJE_SEGURO); }
}
```

**Python** (`estructural/decorator/`)

```python
class ProductoDecorador(Producto):
    def __init__(self, producto: Producto) -> None:
        # Sin super().__init__: no se copian nombre/precio, se leen del envuelto.
        self._producto_decorado = producto

    @property
    def precio(self) -> float:
        return self._producto_decorado.precio


class SeguroDecorador(ProductoDecorador):
    PORCENTAJE_SEGURO = 0.10

    @property
    def precio(self) -> float:
        return self._producto_decorado.precio * (1 + self.PORCENTAJE_SEGURO)

    @property
    def nombre(self) -> str:
        return f"{self._producto_decorado.nombre} [Con seguro]"


# Se apilan:
p = GarantiaExtendidaDecorador(SeguroDecorador(EnvolturaRegaloDecorador(laptop)), 12)
```

**Qué cambió y por qué**

- `getPrecio()`/`getNombre()` son `@property` y se sobrescriben igual que en Java. A diferencia de Java, `ProductoDecorador` no llama a `Producto.__init__`, así que no guarda copias de `nombre`/`precio` que quedarían desactualizadas: ambos se leen siempre del producto envuelto.
- `private static final` → constante de clase en MAYÚSCULAS.
- El 10% del seguro se calcula sobre el precio del producto **envuelto** (que ya puede incluir otros decoradores), por eso el orden de apilado importa.
- Como en Java, `mostrar_info()` imprime primero la info del producto envuelto y luego la línea del decorador; el nombre decorado solo se ve en `.nombre`.

**Atención: Decorator de GoF no es lo mismo que un `@decorador` de Python.** Comparten el nombre y la idea de "envolver", pero son cosas distintas:

| | Decorator de GoF | `@decorador` de Python |
|---|---|---|
| Qué envuelve | un **objeto** (instancia) | una **función o clase** |
| Cuándo actúa | en tiempo de ejecución, apilando objetos | al *definir* la función (o al aplicarlo a mano) |
| Mismo tipo | el decorador **es un** `Producto` | devuelve un callable que reemplaza al original |
| Para qué | agregar responsabilidades a un objeto concreto | agregar comportamiento transversal (log, caché, reintentos) |

```python
import functools


def con_log(fn):
    @functools.wraps(fn)
    def envoltura(*args, **kwargs):
        print(f"llamando a {fn.__name__}")
        return fn(*args, **kwargs)

    return envoltura


@con_log
def calcular_total(carrito): ...
```

**La alternativa pythónica**: para el caso del GoF, delegar con `__getattr__` evita reescribir cada método del envuelto:

```python
class Decorador:
    def __init__(self, envuelto):
        self._envuelto = envuelto

    def __getattr__(self, nombre):
        return getattr(self._envuelto, nombre)
```

Para comportamiento transversal sobre funciones, usá un `@decorador`.

---

## 6. Adapter

**Java**

```java
public class AdaptadorFedEx implements ServicioEnvio {
    private static final double KG_TO_LBS = 2.20462;
    public double calcularCosto(String direccion, double peso) {
        return sistemaFedEx.getQuote(peso * KG_TO_LBS);
    }
}
```

**Python** (`estructural/adapter/adaptador_fedex.py`)

```python
class AdaptadorFedEx(ServicioEnvio):
    KG_TO_LBS = 2.20462  # 1 kg = 2.20462 lbs

    def __init__(self, sistema_fedex: SistemaFedEx) -> None:
        self._sistema_fedex = sistema_fedex  # composición

    def calcular_costo(self, direccion: str, peso: float) -> float:
        peso_libras = peso * self.KG_TO_LBS
        return self._sistema_fedex.get_quote(peso_libras)
```

**Qué cambió y por qué**

- `implements ServicioEnvio` → herencia de una `ABC` con métodos abstractos.
- El adaptee se inyecta por constructor (composición), lo que permite sustituirlo por un doble en los tests.
- Los adaptees (`SistemaDHL`, `SistemaFedEx`, `SistemaCorreos`) conservan sus nombres en inglés (`ship_package`, `get_quote`...) porque representan APIs externas que no se pueden cambiar; solo se pasaron a snake_case.
- Se mantienen los quirks de Java: `AdaptadorDHL` ignora la dirección y fija la zona "nacional" (ver `ANALISIS_PROYECTO_JAVA.md`).

**La alternativa pythónica**: **duck typing** y `typing.Protocol`. No hace falta heredar de nadie; basta con que el objeto tenga los métodos correctos.

```python
class ServicioEnvio(Protocol):
    def enviar_paquete(self, direccion: str, peso: float) -> None: ...
    def calcular_costo(self, direccion: str, peso: float) -> float: ...
    def obtener_estado(self) -> str: ...
```

Cualquier clase con esos métodos "cumple" el Protocol, y el verificador de tipos (mypy/pyright) lo comprueba sin herencia.

---

## 7. Composite

**Java**

```java
public int getCantidadProductos() {
    int cantidad = 0;
    for (ComponenteCatalogo hijo : hijos) {
        if (hijo instanceof ProductoItem) cantidad++;
        else if (hijo instanceof Categoria) cantidad += ((Categoria) hijo).getCantidadProductos();
    }
    return cantidad;
}
```

**Python** (`estructural/composite/categoria.py`)

```python
@property
def cantidad_productos(self) -> int:
    cantidad = 0
    for hijo in self._hijos:
        if isinstance(hijo, ProductoItem):
            cantidad += 1
        elif isinstance(hijo, Categoria):
            cantidad += hijo.cantidad_productos
    return cantidad
```

**Qué cambió y por qué**

- `instanceof` + cast → `isinstance` (sin cast: Python no lo necesita).
- `getPrecioTotal()` → `@property precio_total`.
- Validación agregada respecto de Java: un componente no puede agregarse a sí mismo ni crear un ciclo (`ValueError`), porque un ciclo haría infinita la recursión de `precio_total` y `mostrar_detalle`. `PaqueteProductos` además valida que el descuento esté entre 0 y 100.
- En el Component, `agregar`/`remover` lanzan por defecto `UnsupportedOperationException` en Java; en Python, `NotImplementedError`. Las hojas (`ProductoItem`) heredan ese comportamiento.
- `List.remove(obj)` de Java ignora un elemento ausente; `list.remove` de Python lanza `ValueError`. Se protege con `if componente in self._hijos` para conservar el comportamiento.
- `String.format("%.0f%%")` → `f"{x:.0f}%"` (en un f-string no hace falta escapar el `%`). Ojo: `%.0f` de Java redondea half-up y `:.0f` de Python redondea half-even (solo difiere en descuentos terminados en .5).

**La alternativa pythónica**: el polimorfismo por duck typing hace que ni `isinstance` sea imprescindible; si cada componente implementara `cantidad_productos`, el compuesto sumaría sin preguntar el tipo. Para recorridos del árbol, un generador recursivo con `yield from` es muy natural.

---

## 8. Facade

**Java**

```java
public PedidoContext realizarCompraCompleta(String tipoProducto, String nombreProducto,
                                            double precio, String direccion, String numeroTarjeta) { ... }
public void compraRapida(String nombreProducto, double precio, String direccion) { ... }
public void consultarEstadoPedido(PedidoContext pedido) { ... }
```

**Python** (`estructural/facade/tienda_facade.py`)

```python
tienda_facade = TiendaFacade("MegaStore Online")
pedido_facade = tienda_facade.realizar_compra_completa(
    "electronico",
    "Samsung Galaxy S24",
    899.99,
    "Calle Mayor 789, Valencia",
    "4532-9876-5432-1098",
)
tienda_facade.compra_rapida("AirPods Pro", 249.99, "Plaza España 10, Sevilla")
tienda_facade.consultar_estado_pedido(pedido_facade)
```

Y por dentro, el paso 4 (pago) y el 5 (seguimiento) usan el total del pedido construido:

```python
total = pedido.calcular_total()  # producto + envío Express = 914.99
PagoTarjeta(numero_tarjeta).pagar(total)
pedido_context = PedidoContext(self._nuevo_numero_pedido(), total)
```

**Qué cambió y por qué**

- Misma API en snake_case: `realizar_compra_completa`, `compra_rapida`, `consultar_estado_pedido`.
- Por dentro coordina cinco patrones: Factory (crear producto) → Builder (crear pedido) → Chain (validar) → Strategy (pagar con tarjeta) → State (contexto de seguimiento).
- En Java, el pedido de seguimiento se identifica con `"FAC-" + System.currentTimeMillis()`. El port usa `FAC-<milisegundos>-<contador>` (`_nuevo_numero_pedido`), así que dos compras en el mismo milisegundo ya no comparten id. Por eso la salida de la demo no es reproducible byte a byte (el id lleva una marca de tiempo).
- En Java, `realizarCompraCompleta` devuelve `null` si la validación falla; en Python, `None`. Los parámetros de `compraRapida` solo se imprimen: no crea nada (ver `ANALISIS_PROYECTO_JAVA.md`).
- **El port corrige dos defectos del Java** (detalle en [Diferencias deliberadas](#diferencias-deliberadas-con-el-java-original)): valida, cobra y registra el mismo monto (`pedido.calcular_total()`, 914.99 y no los 899.99 que cobraba Java), y delega la creación del producto en `ProductoFactory.crear_producto`.
- Como ya no hay `checkout()` (ver arriba), la línea con los datos del producto (`Electrónico: Samsung Galaxy S24 | ...`) se imprime en el paso 1, al crearlo, en lugar de dentro del checkout del paso 4.
- **Decisión de diseño:** sigue devolviendo un `PedidoContext` (acopla al cliente con el subsistema State, como en Java). Se conserva porque la demo y `consultar_estado_pedido` lo usan tal cual y porque cambiarlo rompería la correspondencia con `Main.java`; una fachada más estricta devolvería un id o un objeto propio.

**La alternativa pythónica**: un Facade en Python suele ser **una función de módulo** (o un módulo entero que reexporta lo importante en su `__init__.py`). La clase se justifica acá porque guarda el nombre de la tienda y agrupa tres operaciones relacionadas.

---

## 9. Proxy

**Java**

```java
private ProductoPremiumReal getProductoReal() {          // lazy loading
    if (productoReal == null) {
        productoReal = new ProductoPremiumReal(nombre, precio, contenidoDigital);
    }
    return productoReal;
}
```

**Python** (`estructural/proxy/producto_premium_proxy.py`)

```python
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


def descargar_contenido_digital(self) -> None:
    if not self._usuario_autenticado:
        print("🔒 ACCESO DENEGADO")
        return
    if self._tipo_suscripcion not in self.SUSCRIPCIONES_CON_DESCARGA:  # {"premium", "vip"}
        ...
        return
    self._get_producto_real().descargar_contenido_digital()
```

**Qué cambió y por qué**

- `Thread.sleep(500)` (en el objeto real, para simular una carga costosa) → `time.sleep(0.5)`. Se agregó un parámetro opcional `retardo_carga` (0.5 por defecto) para que los tests no esperen medio segundo por objeto.
- El constructor separa los **datos** del producto (posicionales, como en Java) de la **configuración** (keyword-only, después de `*`): `ProductoPremiumProxy("Curso", 199.99, "Videos", usuario_autenticado=False, tipo_suscripcion="basico")`. En Java la llamada es `new ProductoPremiumProxy(..., false, "basico")`, y un `false` suelto no dice qué significa (la "trampa del booleano"); en Python pasarlo por posición da `TypeError`.
- Se agregó la propiedad `producto_real_cargado`, útil para demostrar y testear que el *lazy loading* realmente retrasa la creación.
- El proxy responde `nombre` y `precio` sin crear el objeto real (información pública).
- El control de acceso se escribe explícito, método por método, igual que en Java, para que se vea qué protege cada uno.

**La alternativa pythónica**: un proxy dinámico con `__getattr__`. El port lo incluye como una clase real, `ProxyDinamico` (al final de `producto_premium_proxy.py`, con tests):

```python
class ProxyDinamico:
    def __init__(self, fabrica: Callable[[], ProductoPremium]) -> None:
        self._fabrica = fabrica
        self._real: ProductoPremium | None = None

    def __getattr__(self, nombre: str) -> Any:
        # Solo se llama si el atributo NO existe en el proxy. El guard evita la
        # recursión infinita con copy/pickle.
        if nombre.startswith("_"):
            raise AttributeError(nombre)
        if self._real is None:
            self._real = self._fabrica()
        return getattr(self._real, nombre)
```

Sus **límites** (por eso no reemplaza al proxy explícito):

- `__getattr__` solo se invoca cuando la búsqueda normal del atributo **falla**. No "intercepta cualquier atributo": lo que el proxy ya define no se delega.
- Nunca se invoca para los métodos especiales (`__len__`, `__str__`...): Python los busca en el **tipo**, no en la instancia, así que `len(proxy)` o `str(proxy)` no llegan al objeto real.
- No hereda de `ProductoPremium`: `isinstance(proxy, ProductoPremium)` es `False`, se pierde la interfaz compartida del Subject.
- `copy.copy` o `pickle` crean el objeto sin ejecutar `__init__`; sin el guard de `_`, `self._real` volvería a caer en `__getattr__` y daría `RecursionError`.

Para lazy loading de una sola propiedad, `functools.cached_property` es todavía más corto. El control de acceso explícito sigue siendo mejor con métodos concretos, como hace `ProductoPremiumProxy`.

---

## 10. Observer

**Java**

```java
public interface Observer { void actualizar(String mensaje); }

public void notificarClientes(String mensaje) {
    for (Observer c : clientes) c.actualizar(mensaje);
}
```

**Python** (`comportamiento/observer/`)

```python
class Observer(ABC):
    @abstractmethod
    def actualizar(self, mensaje: str) -> None: ...


class Tienda:
    def notificar_clientes(self, mensaje: str) -> None:
        print(f"\n--- Notificando a {len(self._clientes)} clientes ---")
        # Copia defensiva: un observador puede (des)suscribirse mientras se notifica.
        for cliente in list(self._clientes):
            cliente.actualizar(mensaje)
```

**Qué cambió y por qué**

- `ArrayList<Observer>` → `list[Observer]`; `interface` → `ABC`.
- `desuscribir`: `List.remove` de Java ignora a quien no está; `list.remove` de Python lanza `ValueError`. Se comprueba antes de quitar y, **igual que en Java**, el mensaje "desuscrito" se imprime aunque el cliente no estuviera suscripto.
- La notificación es síncrona, en el orden de suscripción.
- Se itera sobre una **copia** (`list(self._clientes)`). Si un observador se da de baja dentro de su propio `actualizar` y se recorriera la lista original, el `remove` correría los índices y el observador siguiente **se saltaría sin recibir el mensaje** (Python no avisa; Java con `ArrayList` lanzaría `ConcurrentModificationException`). Es el bug clásico del patrón.

**La alternativa pythónica**: **callbacks**. Un observador es simplemente una función `Callable[[str], None]`:

```python
class Tienda:
    def __init__(self):
        self._suscriptores: list[Callable[[str], None]] = []

    def suscribir(self, callback):
        self._suscriptores.append(callback)

    def notificar(self, mensaje):
        for cb in self._suscriptores:
            cb(mensaje)


tienda.suscribir(lambda m: print(f"Ana recibió: {m}"))
```

Para eventos más complejos existen bibliotecas de señales, pero para aprender el patrón alcanza con callbacks. (También sirve `typing.Protocol` si querés tipado estructural.)

---

## 11. Strategy

**Java**

```java
public interface EstrategiaPago { void pagar(double monto); }
carrito.setEstrategiaPago(new PagoTarjeta("1234567890123456"));
```

**Python** (`comportamiento/strategy/`)

```python
class EstrategiaPago(Protocol):
    @abstractmethod
    def pagar(self, monto: float) -> None: ...


class PagoTarjeta(EstrategiaPago):
    def __init__(self, numero_tarjeta: str) -> None:
        self._numero_tarjeta = numero_tarjeta

    @override
    def pagar(self, monto: float) -> None:
        ultimos_digitos = self._numero_tarjeta[-4:]  # substring(length - 4)
        print(f"Pagando ${monto} con tarjeta terminada en {ultimos_digitos}")


carrito.estrategia_pago = PagoTarjeta("1234567890123456")  # propiedad con setter
```

**Qué cambió y por qué**

- `substring(length - 4)` → slicing `numero[-4:]`.
- `setEstrategiaPago(x)` → propiedad con setter (`carrito.estrategia_pago = x`): en Python los getters/setters triviales se escriben como propiedades. El getter devuelve `EstrategiaPago | None` y el setter solo acepta una `EstrategiaPago`.
- `estrategia_pago` es `None` hasta que se asigna (`null` en Java); el tipo `EstrategiaPago | None` lo deja explícito. `checkout()` valida carrito vacío y falta de estrategia imprimiendo, sin lanzar excepciones, igual que Java.
- `PagoEfectivo` muestra "Pagando $X" con el monto **sin** descuento y luego el total ya descontado (comportamiento heredado).
- `EstrategiaPago` es un `typing.Protocol` (tipado **estructural**), no una `ABC`. Con una ABC la anotación sería **nominal**: un objeto sin herencia pero con `pagar` funcionaría en ejecución y, sin embargo, mypy lo rechazaría. Con el `Protocol`, `CarritoCompra` acepta cualquier objeto con un `pagar(monto)` compatible, herede o no, y el verificador también. Las estrategias concretas igual heredan de forma explícita (opcional): así el verificador comprueba su firma y olvidarse de implementar `pagar` da `TypeError` al instanciar.

**La alternativa pythónica**: **funciones como estrategias**. Las funciones son objetos de primera clase:

```python
def pago_efectivo(monto: float) -> None:
    print(f"Total a pagar: ${monto * 0.95:.2f}")


def pago_tarjeta(ultimos4: str):
    return lambda monto: print(f"Pagando ${monto} con tarjeta {ultimos4}")


carrito.estrategia = pago_efectivo  # o pago_tarjeta("3456")
carrito.estrategia(total)
```

Se necesita una clase solo cuando la estrategia tiene estado propio o varios métodos.

---

## 12. Chain of Responsibility

**Java**

```java
validadorStock.setSiguiente(validadorDireccion);
validadorDireccion.setSiguiente(validadorMonto);
validadorMonto.setSiguiente(validadorPago);
boolean ok = validadorStock.validar(pedido);
```

**Python** (`comportamiento/chain/`)

```python
class ValidadorPedido(ABC):
    def __init__(self) -> None:
        self._siguiente: ValidadorPedido | None = None

    def set_siguiente(self, siguiente: ValidadorPedido) -> ValidadorPedido:
        self._siguiente = siguiente
        return siguiente  # devuelve el enlazado: permite encadenar

    @abstractmethod
    def validar(self, pedido: Pedido) -> bool: ...

    def _validar_siguiente(self, pedido: Pedido) -> bool:
        if self._siguiente is not None:
            return self._siguiente.validar(pedido)
        return True
```

**Qué cambió y por qué**

- `protected validarSiguiente` → `_validar_siguiente` (guion bajo por convención).
- `set_siguiente` devuelve el eslabón enlazado (en Java es `void`), así que la cadena se arma en una sola expresión: `stock.set_siguiente(direccion).set_siguiente(monto).set_siguiente(pago)`.
- Por eso `set_siguiente` **sigue siendo un método** y no una propiedad: una asignación (`stock.siguiente = direccion`) no devuelve nada y no se puede encadenar. Además es el `setNext` del GoF, reconocible para quien viene de Java. (Lo mismo con `get_instance()` de los singletons: es el nombre GoF del punto de acceso global, no el getter de un atributo.)
- `Pedido` solo se usa para anotar tipos, así que se importa bajo `TYPE_CHECKING`: evita acoplar en tiempo de ejecución el paquete `chain` con `builder`.
- `ValidadorMontoPedido` es el único con lógica real: el total (productos + envío + envoltura) debe estar entre 10.00 y 5000.00, ambos inclusivos. `private static final double` → constantes de clase con `typing.Final`.
- Los otros tres validadores están "hardcodeados" para pasar, igual que en Java (simulaciones).

**La alternativa pythónica**: una **lista de funciones** con `all(...)`, que cortocircuita igual en el primer fallo:

```python
validadores = [validar_stock, validar_direccion, validar_monto, validar_pago]
es_valido = all(v(pedido) for v in validadores)
```

La cadena de objetos sigue valiendo cuando cada eslabón decide dinámicamente si seguir o no, o cuando la cadena se arma en tiempo de ejecución.

---

## 13. Template Method

**Java**

```java
public abstract class ProcesadorPedido {
    public final void procesarPedido(String numeroPedido, double monto) {
        verificarInventario();
        calcularCostos(monto);
        procesarPago(monto);
        if (requiereVerificacionAdicional()) verificacionAdicional();
        prepararEnvio();
        notificarCliente(numeroPedido);
        registrarOperacion(numeroPedido, monto);
    }
    protected abstract void calcularCostos(double monto);
    protected boolean requiereVerificacionAdicional() { return false; }
}
```

**Python** (`comportamiento/template/procesador_pedido.py`)

```python
# procesador_pedido.py
from abc import ABC, abstractmethod
from typing import final


class ProcesadorPedido(ABC):
    @final
    def procesar_pedido(self, numero_pedido: str, monto: float) -> None:
        print(f"\n=== PROCESANDO PEDIDO {numero_pedido} ===")
        self.verificar_inventario()
        total = self.calcular_costos(monto)  # el total calculado es el que se cobra
        self.procesar_pago(total)
        if self.requiere_verificacion_adicional():
            self.verificacion_adicional()
        self.preparar_envio()
        self.notificar_cliente(numero_pedido)
        self.registrar_operacion(numero_pedido, total)
        print(f"=== PEDIDO {numero_pedido} COMPLETADO ===\n")

    @abstractmethod
    def calcular_costos(self, monto: float) -> float: ...

    def requiere_verificacion_adicional(self) -> bool:  # hook
        return False


# procesador_pedido_nacional.py
from typing import override


class ProcesadorPedidoNacional(ProcesadorPedido):
    @override
    def calcular_costos(self, monto: float) -> float:
        impuesto = monto * 0.16  # IVA 16%
        envio = 5.00
        total = monto + impuesto + envio
        return total
```

**Qué cambió y por qué**

- **Corrección de un bug de Java**: en Java `calcularCostos` es `void`; calcula e imprime el total ($585.00 para un pedido nacional de $500) pero lo descarta, y `procesarPago(monto)` cobra el monto original ($500.00). En Python `calcular_costos` **devuelve** el total y el template method se lo pasa a `procesar_pago` y a `registrar_operacion` (ver [Diferencias deliberadas](#diferencias-deliberadas-con-el-java-original)).
- `final` → `typing.final`. **Ojo**: en Python no es una garantía en ejecución. Los verificadores de tipos (mypy/pyright) rechazan sobrescribir el método, pero el intérprete no lo impide. Es una convención respaldada por herramientas.
- `@Override` → `typing.override` (Python 3.12). Por eso el proyecto exige 3.12.
- `protected` no existe: los pasos quedan públicos (sin guion bajo) para poder sobrescribirlos y probarlos sin fricción.
- `%%` de `printf` (porcentaje literal) es simplemente `%` en un f-string.
- Se conserva la numeración original de los mensajes: el paso `[3]` (costos) se imprime **antes** que el `[2]` (pago).

**La alternativa pythónica**: pasar los pasos variables como **funciones/callables** (composición en lugar de herencia), o usar un *mixin*. Si solo varían un par de pasos, una función con parámetros opcionales suele ser más simple que una jerarquía.

---

## 14. State

**Java**

```java
public class EstadoNuevo implements EstadoPedido {
    @Override
    public void siguiente(PedidoContext pedido) {
        System.out.println("✓ Pedido confirmado y en proceso de pago");
        pedido.setEstado(new EstadoConfirmado());
    }
}
```

**Python** (`comportamiento/state/estado_nuevo.py`)

```python
class EstadoNuevo(EstadoPedido):
    @override
    def siguiente(self, pedido: PedidoContext) -> None:
        from .estado_confirmado import EstadoConfirmado  # import local (ver abajo)

        print("✓ Pedido confirmado y en proceso de pago")
        pedido.estado = EstadoConfirmado()  # el setter de la propiedad
```

**Qué cambió y por qué**

- `getEstado()/setEstado()` → propiedad `estado` con setter. `getNombreEstado()` → propiedad abstracta `nombre_estado`.
- El ciclo de imports **real está entre los propios estados**: `EstadoNuevo.siguiente` crea un `EstadoConfirmado` y `EstadoConfirmado.anterior` crea un `EstadoNuevo` (igual Confirmado ↔ Enviado y Enviado ↔ Entregado). Con un módulo por clase, un `import` a nivel de módulo en ambos sentidos fallaría con `ImportError`, así que esos métodos hacen el import **dentro del método**.
- Entre el contexto y los estados **no** hay ciclo: `PedidoContext` importa `EstadoNuevo` a nivel de módulo (`pedido_context` → `estado_nuevo` → `estado_pedido`) y los estados solo importan `PedidoContext` bajo `TYPE_CHECKING`, para anotar tipos. (Antes el código justificaba un import local en el contexto con un ciclo que no existía.)
- Mismo diseño de Java: las transiciones las deciden los propios estados. Operaciones inválidas se resuelven con un mensaje, sin excepción.
- `EstadoEntregado.anterior()` vuelve a `EstadoEnviado` ("devolución"): comportamiento heredado de Java.

**La alternativa pythónica**: un `enum.Enum` más una **tabla de transiciones**:

```python
class Estado(Enum):
    NUEVO = auto()
    CONFIRMADO = auto()
    ENVIADO = auto()
    ENTREGADO = auto()
    CANCELADO = auto()


SIGUIENTE = {
    Estado.NUEVO: Estado.CONFIRMADO,
    Estado.CONFIRMADO: Estado.ENVIADO,
    Estado.ENVIADO: Estado.ENTREGADO,
}
```

Es más compacto cuando los estados solo cambian de nombre. Las clases por estado se justifican cuando cada estado tiene comportamiento propio distinto, como acá.

---

## 15. Command

**Java**

```java
public interface Command { void ejecutar(); void deshacer(); String getDescripcion(); }

public void ejecutarComando(Command comando) {
    while (historial.size() > posicionActual + 1) historial.remove(historial.size() - 1);
    comando.ejecutar();
    historial.add(comando);
    posicionActual++;
}
```

**Python** (`comportamiento/command/gestor_promociones.py`)

```python
def ejecutar_comando(self, comando: Command) -> None:
    registro = copy.copy(comando)  # una copia por ejecución
    registro.ejecutar()
    # Recién ahora que tuvo éxito: eliminar los comandos que están después de la
    # posición actual (si se deshizo algo y luego se ejecuta un comando nuevo).
    del self._historial[self._posicion_actual + 1 :]
    self._historial.append(registro)
    self._posicion_actual += 1
    print(f"→ Ejecutado: {registro.descripcion}")
```

Y el receptor guarda el descuento como un snapshot inmutable (`comportamiento/command/carrito_compra_command.py`):

```python
@dataclass(frozen=True)
class DescuentoVigente:
    """Snapshot inmutable del descuento: ``valor`` es un % o un monto según ``tipo``."""

    tipo: TipoDescuento  # Literal["ninguno", "porcentaje", "fijo"]
    valor: float = 0.0


SIN_DESCUENTO: Final = DescuentoVigente("ninguno")
```

**Qué cambió y por qué**

- El `while ... remove(last)` de Java se escribe como un *slice delete* en una línea (`del historial[pos + 1:]`).
- `getTamanioHistorial()` → propiedad `tamanio_historial`. `getDescripcion()` → propiedad abstracta `descripcion` (`@property` + `@abstractmethod` en `Command`): se lee como atributo (`comando.descripcion`) y todo comando concreto debe definirla.
- El 100 de los porcentajes es una constante con nombre (`CarritoCompraCommand.PORCENTAJE_MAXIMO: Final = 100.0`), igual que en `PaqueteProductos`.
- Los porcentajes se convierten a `float` para que `10` se imprima `10.0` como un `double` de Java.
- **Correcciones de bugs de Java** (detalle en [Diferencias deliberadas](#diferencias-deliberadas-con-el-java-original)): el descuento fijo se guarda como **monto** (`DescuentoVigente("fijo", 100.0)`) y no como un porcentaje del total del momento; el total con descuento nunca baja de 0; porcentaje fuera de 0..100 o monto negativo lanzan `ValueError` sin tocar el estado; con el carrito vacío no hay división por cero (el monto queda guardado y se aplica cuando haya productos).
- Cada comando guarda el `DescuentoVigente` anterior al ejecutarse (solo si el receptor aceptó el nuevo) para restaurar el estado **exacto** en `deshacer`.
- `GestorPromociones` ejecuta **antes** de truncar el historial de rehacer (si el comando falla, lo deshecho se puede rehacer) y guarda una `copy.copy` de cada comando: ejecutar dos veces la misma instancia ya no rompe el `deshacer` de la primera ejecución.

**La alternativa pythónica**: **closures y callables**. Si no necesitás undo ni descripción, un comando es solo una función:

```python
cola = [lambda: carrito.aplicar_descuento_porcentaje(10, "Cliente frecuente")]
for accion in cola:
    accion()
```

Para undo/redo, un comando es un par de funciones `(hacer, deshacer)` que capturan su contexto en un closure, o un `dataclass` con dos callables. La clase `Command` se justifica porque acá necesitamos estado + descripción + undo.

---

## 16. Iterator

**Java**

```java
public interface Iterator<T> { boolean hasNext(); T next(); void reset(); }

Iterator<ItemCatalogo> it = catalogo.crearIteratorEnStock();
while (it.hasNext()) { ItemCatalogo item = it.next(); ... }
```

**Python** (`comportamiento/iterator/`)

```python
# Estilo Java (GoF), sigue funcionando:
it = catalogo.crear_iterator_en_stock()
while it.has_next():
    item = it.next()

# Estilo Python: el Iterator ya está en el lenguaje
it.reset()  # el iterador de arriba quedó agotado: reiniciarlo...
for item in it:  # ...(o crear uno nuevo); la ABC implementa __iter__/__next__
    ...
for item in catalogo.items_por_precio(10, 100):  # generador con yield
    ...
```

Un iterador agotado no se rebobina solo: un `for` sobre él sin llamar a `reset()` (o sin crear uno nuevo) no recorre nada.

```python
def items_por_popularidad(self):
    yield from sorted(self._items, key=lambda i: i.popularidad, reverse=True)
```

**Qué cambió y por qué**

- En Python el patrón Iterator **ya está dentro del lenguaje**: el protocolo `__iter__`/`__next__` *es* el Iterator de GoF, y `for` lo consume.
- La interfaz `Iterator` conserva `has_next`/`next`/`reset` y además implementa `__iter__` (devuelve `self`) y `__next__` (lanza `StopIteration` al agotarse). Así los mismos objetos funcionan con `while it.has_next()` y con `for x in it`.
- **Diferencia de contrato (decisión de diseño)**: el `next()` de GoF/Java devuelve `null` (`None`) al agotarse; `next(it)` de Python lanza `StopIteration`. Se conservan los dos a propósito: `next() -> T | None` es el contrato GoF/Java que se está enseñando y `__next__` es el protocolo de Python. Por eso las demos recorren con `for` y nunca llaman a `next()` a mano sin comprobar `None`.
- `interface Iterator<T>` / `interface Aggregate<T>` → `class Iterator[T](ABC)` / `class Aggregate[T](ABC)` (genéricos PEP 695, en lugar de `TypeVar` + `Generic[T]`); `__iter__` devuelve `Self`.
- Los iteradores filtrados heredan de `CatalogoIterator` y solo cambian la lista que le pasan; en Java cada uno repetía los tres métodos.
- `Catalogo` es *iterable* (`__iter__` crea un iterador nuevo, se puede repetir) y soporta `len(catalogo)`.
- `String.format("%-58s")` → `f"{x:<58}"`; `"★".repeat(n)` → `"★" * n`; `toString()` → `__str__` (con `@override`, porque redefine `object.__str__`).

**La alternativa pythónica**: **generadores**. Cada iterador de clase se reemplaza por 3 líneas. Por eso `Catalogo` ofrece también `items_por_categoria`, `items_en_stock`, `items_por_precio` e `items_por_popularidad`. **No son equivalentes** a los iteradores de clase:

- Los iteradores GoF filtrados (`crear_iterator_por_categoria`, `_en_stock`, `_por_precio`, `_por_popularidad`) arman su lista **al crearse**: son una foto fija del catálogo en ese momento (`crear_iterator`, el básico, comparte la lista y sí ve los cambios).
- Los generadores son **perezosos**: no ejecutan nada hasta el primer `next` y recorren el catálogo vivo, así que ven los items agregados antes (o durante) el recorrido.
- `items_por_popularidad` es perezoso solo hasta el primer `next`: `sorted` necesita ver todos los elementos, así que ordena la colección completa de una vez y a partir de ahí es una foto fija.

---

## 17. Mapeos generales del lenguaje

| Java | Python | Notas |
|------|--------|-------|
| `abstract class` | `class X(abc.ABC)` + `@abstractmethod` | Instanciar una subclase incompleta da `TypeError`, igual que en Java da error de compilación |
| `interface` | `abc.ABC` (herencia explícita) o `typing.Protocol` (estructural) | Este port usa `ABC` para reflejar el `implements`; `Protocol` es la opción pythónica |
| `interface Foo<T>` | `class Foo[T](ABC)` (PEP 695, 3.12) | Antes de 3.12: `T = TypeVar("T")` + `class Foo(ABC, Generic[T])` |
| método que devuelve `this` (tipo propio) | `-> typing.Self` | Las subclases heredan el tipo correcto (`clonar`, builders fluidos, `__iter__`) |
| `getX()` / `setX()` | `@property` / `@x.setter` | Se accede como atributo (`p.nombre`) pero es de solo lectura si no hay setter. Excepciones a propósito: `set_siguiente` (encadenable) y `get_instance` (nombre GoF) |
| `static` método | `@staticmethod`, `@classmethod` o función de módulo | Una clase con solo métodos estáticos suele ser una función suelta |
| `static` atributo / `final` constante | atributo de clase en MAYÚSCULAS, `typing.Final` | `Final` lo verifica el type checker, no el intérprete |
| `private` | `_nombre` (convención) o `__nombre` (name mangling) | Python no impide el acceso: es un acuerdo entre programadores |
| `protected` | `_nombre` | |
| `@Override` | `@typing.override` (3.12+) | Solo para verificadores de tipos; `mypy` exige ponerlo (`enable_error_code = ["explicit-override"]` en `pyproject.toml`) |
| `final` (método) | `@typing.final` | No se impone en ejecución |
| `new Foo()` | `Foo()` | No existe `new` |
| `null` | `None` | Se tipa como `X \| None` |
| `instanceof` + cast | `isinstance` | |
| `IllegalArgumentException` | `ValueError` | |
| `UnsupportedOperationException` | `NotImplementedError` | |
| `NullPointerException` | `AttributeError`/`TypeError` sobre `None` | |
| `ArrayList<T>` / `List<T>` | `list[T]` | |
| `HashMap<K,V>` | `dict[K, V]` | Ver nota abajo |
| `synchronized` | `threading.Lock` | `with lock:` |
| `Thread.sleep(ms)` | `time.sleep(segundos)` | Cambia la unidad: ms → segundos |
| `System.out.println` | `print` | |
| `String.format("%.2f")` / `printf` | f-string `f"{x:.2f}"` | Ver nota abajo |
| `toString()` | `__str__` (y `__repr__`) | |
| `equals()` / `hashCode()` | `__eq__` / `__hash__` | |
| `for (T x : coleccion)` | `for x in coleccion` | Requiere `__iter__` |
| `substring(n)` | slicing `s[n:]`, `s[-4:]` | |
| `"x".repeat(n)` | `"x" * n` | |
| `package a.b.c` | carpeta `a/b/c/` con `__init__.py` | |
| `import a.b.C` | `from a.b import C` | |

### Convenciones de tipado del port

- **Anotaciones**: anotaciones normales (sin comillas) en todo el proyecto. `from __future__ import annotations` se usa **solo** en los módulos que lo necesitan: los que anotan con nombres importados bajo `TYPE_CHECKING` (Chain, State) o con la propia clase mientras se define (`Pedido`, `ComponenteCatalogo`, los singletons). La única cadena entre comillas es `Prototype["ProductoPrototype"]`, que no es una anotación sino la lista de bases de la clase (la clase todavía no existe).
- **Genéricos**: sintaxis PEP 695 (`class Iterator[T](ABC)`), sin `TypeVar` a nivel de módulo.
- **`Self`** en los métodos que devuelven la propia instancia o una copia de ella.
- **`typing.Final`** en las constantes de clase y de módulo (`COSTO_ENVOLTURA`, `KG_TO_LBS`, `MONTO_MINIMO`, `PORCENTAJE_MAXIMO`, `SIN_DESCUENTO`, `LINEA`...). Los registros que sí cambian (`ProductoFactory._CONSTRUCTORES`) son `ClassVar`.
- **`@override`** en todo método que redefine otro, también en los tests; mypy lo verifica.

### Orden de `HashMap` frente a `dict`

`HashMap` en Java **no garantiza orden**: itera según el hash de las claves. Desde Python 3.7, un `dict` **conserva el orden de inserción**. Consecuencia en este proyecto: las especificaciones de un `ProductoPrototype` se imprimen en el orden en que se agregaron, mientras que Java las imprime en el orden del hash. Si querés ese orden en Java, usá `LinkedHashMap`.

### `double` y dinero

Ambas versiones usan números de punto flotante (`double` en Java, `float` en Python) para los montos, porque es una demo. **En código real no hagas esto**: `0.1 + 0.2` no es `0.3` en ninguno de los dos lenguajes. En Java se recomienda `BigDecimal`; en Python, `decimal.Decimal`:

```python
from decimal import Decimal

total = Decimal("0.10") + Decimal("0.20")  # Decimal('0.30')
```

Dos detalles de impresión que el port respeta: concatenar un `double` en Java (`"$" + 10.0`) imprime `10.0`, y `f"{10.0}"` en Python imprime lo mismo; y Python usa la representación más corta que identifica al `float` (por ejemplo `925.98`).

Ojo: esa coincidencia **no es universal**. Java (`Double.toString`) pasa a notación científica desde 10^7 (`1.0E7`) y por debajo de 10^-3, mientras que Python imprime `10000000.0` (y recién usa notación científica desde 1e16). Con los importes de esta demo no se nota, pero un total de diez millones se vería distinto. Además, con operaciones en punto flotante ambos pueden mostrar valores como `0.30000000000000004`.

### Formato numérico y *locale*

`String.format("%.2f")` y `System.out.printf` en Java usan el **locale por defecto de la JVM**: con un sistema configurado en español imprimen coma decimal (`1234,50`). Los f-strings de Python con `:.2f` **no dependen del locale**: siempre usan punto (`1234.50`). Por eso la salida de las dos versiones puede diferir en una máquina con locale `es_*`. Si necesitás formato regional en Python, usá el módulo `locale` o `babel`; si necesitás salida fija en Java, `String.format(Locale.US, ...)`.

También difiere el redondeo en casos límite: `%.0f` de Java redondea half-up y `:.0f` de Python redondea half-even.

### Excepciones y validaciones

Java obliga a declarar o capturar excepciones *checked*; Python no distingue. Este proyecto casi no lanza excepciones (los validadores y el carrito imprimen y devuelven), pero donde lo hace usa los equivalentes de la tabla (`ValueError`, `NotImplementedError`). En Python se prefiere *EAFP* ("más fácil pedir perdón que permiso": intentar y capturar la excepción) antes que comprobar todo con `if`, como se ve en la Factory con `KeyError`.

### Un módulo por clase

Java obliga a un archivo por clase pública. Python no. Este port mantiene "un módulo por clase" para que el mapeo sea 1 a 1 con el original y se pueda comparar archivo contra archivo. En Python idiomático, varias clases pequeñas relacionadas (por ejemplo los cinco estados) suelen vivir en un solo módulo; acá se separan, y eso obliga a resolver los imports circulares (`TYPE_CHECKING` e imports locales, como entre los estados de State), una buena lección sobre cómo funcionan los módulos.

---

## Diferencias deliberadas con el Java original

Este port quiere ser fiel al Java, pero en varios puntos el Java tiene **defectos** (valida un monto y cobra otro, descarta un resultado, guarda un estado que se desactualiza). Copiarlos habría enseñado mal el patrón, así que el port los corrige y lo dice. Por eso la salida de algunas demos **no coincide número por número** con la de `Main.java`. Las tres diferencias grandes (Facade, Template Method, Command) y las menores están en esta sección; el estado de cada hallazgo está en [`REVISION_PATRONES.md`](REVISION_PATRONES.md).

### Diferencias grandes

| Patrón | Java original | Python | Por qué |
|---|---|---|---|
| **Facade** | Arma un `Pedido` con envío Express y valida su total (producto + $15 = $914.99), pero lo descarta: cobra con un `CarritoCompra` que solo conoce el precio del producto y crea el `PedidoContext` con ese precio. Se valida $914.99 y se cobra y registra $899.99. | Valida, cobra y registra `pedido.calcular_total()`: $914.99. El paso 4 imprime el desglose (`producto $899.99 + envío $15.00`) y paga con `PagoTarjeta` directamente, porque `CarritoCompra` solo suma precios de productos. | Una fachada debe ser coherente: lo que valida es lo que cobra. |
| **Facade** (tipo de producto) | Cualquier tipo distinto de `"libro"` (`"LIBRO"`, `"juguete"`) se crea como electrónico de 12 meses. | Delega en `ProductoFactory.crear_producto`: ignora mayúsculas y un tipo desconocido **rechaza** la compra (devuelve `None`). | Evita crear productos equivocados sin avisar y reutiliza el Factory en lugar de duplicar su lógica. |
| **Facade** (salida del paso 1) | El producto se imprime dentro del `checkout()` del carrito, en el paso 4. | Se imprime en el paso 1, al crearlo (`producto.mostrar_info()`), porque ya no hay checkout. | Consecuencia de cobrar el total del pedido con `PagoTarjeta`: la información del producto se sigue mostrando una vez. |
| **Facade** (ids) | `"FAC-" + System.currentTimeMillis()`: dos compras en el mismo milisegundo comparten id. | `FAC-<milisegundos>-<contador>`. | Id único. Consecuencia: la salida de la demo lleva una marca de tiempo y no es reproducible. |
| **Template Method** | `calcularCostos` es `void`: imprime el total ($585.00 nacional) y lo descarta; `procesarPago(monto)` cobra el monto original ($500.00). | `calcular_costos` **devuelve** el total y `procesar_pedido` se lo pasa a `procesar_pago` y `registrar_operacion`. Salida de la demo: Nacional $585.00 (Java cobra $500.00), Internacional $985.00 (Java $750.00), Express $363.00 (Java $300.00). | Mostrar un total y cobrar otro contradice el propósito del patrón (un esqueleto con pasos que se alimentan entre sí). |
| **Command** (descuento fijo) | Convierte el monto en un **porcentaje** del total del momento (`monto / totalOriginal * 100`) y guarda solo ese porcentaje. Si se agregan productos, el "descuento de $100" deja de valer $100; al deshacer se restaura un porcentaje con ruido de coma flotante (`11.111234569272991%`). Con el carrito vacío divide por cero (`Infinity`/`NaN`). | `DescuentoVigente` (dataclass `frozen`: ninguno, porcentaje o monto fijo). El descuento fijo se guarda como **monto** y se resta del total; `deshacer` restaura el estado exacto; con el carrito vacío no falla. | El estado del descuento debe ser exactamente lo que el usuario pidió. |
| **Command** (validaciones) | No valida: se llega a totales negativos o a porcentajes absurdos. | El total nunca baja de 0; porcentaje fuera de 0..100 o monto negativo lanzan `ValueError` sin modificar el estado. | Invariantes del dominio. |
| **Command** (invoker) | `ejecutarComando` borra primero el historial de rehacer y luego ejecuta; guarda la instancia recibida. | `GestorPromociones` ejecuta primero y trunca después (si el comando falla no se pierde lo deshecho) y guarda `copy.copy(comando)`. | Con el comando fallido se perdía lo deshecho; y ejecutar dos veces la misma instancia pisaba su estado de deshacer. |

### Diferencias menores

| Patrón | Java | Python | Por qué |
|---|---|---|---|
| **Builder** | `Pedido` guarda la lista de productos por referencia: cambia si el llamador modifica su lista. | `Pedido` guarda una `tuple` copiada al construir. | Un producto terminado debe ser inmutable e independiente del builder y de otros pedidos. |
| **Composite** | Sin validaciones. | `PaqueteProductos` rechaza descuentos fuera de 0..100 y `Categoria`/`PaqueteProductos` rechazan ciclos (un componente dentro de sí mismo) con `ValueError`. | Un ciclo vuelve infinita la recursión de `precio_total` y `mostrar_detalle`. |
| **Singleton** (y `RegistroPrototipos`) | El constructor es `private`: no se puede heredar. | La instancia se guarda en `DatabaseConnection._instance` / `RegistroPrototipos._instance`, no en `cls._instance`: una subclase **comparte** la instancia única. | Python permite subclases; con `cls._instance` aparecería un segundo "singleton". |
| **Proxy** | `new ProductoPremiumProxy(nombre, precio, contenido, false, "basico")`. | `usuario_autenticado`, `tipo_suscripcion` y `retardo_carga` son keyword-only. | Un booleano posicional no dice qué significa. |
| **Observer** | Recorre la lista con `for`; si un observador se da de baja durante `actualizar`, `ArrayList` lanza `ConcurrentModificationException`. | Recorre una copia (`list(self._clientes)`). | En Python no hay excepción: simplemente se perdería la notificación del observador siguiente. |
| **Prototype** | Constructor de copia; `new HashMap<>(original)`. | `clonar()` es superficial (`copy.copy`, conserva la subclase) y se agrega `clonar_profundo()` (`copy.deepcopy`). | Aclara qué se comparte y qué no. |
| **Factory** | `switch` fijo. | Registro de clase (`registrar`), extensible sin editar la clase. | Open/Closed real. |
| **Chain** | `setSiguiente` es `void`. | Devuelve el eslabón enlazado. | Permite armar la cadena en una expresión. |

### Formato heredado que se conserva

La salida de `python main.py` se comparó línea por línea con la de `java Main` (compilado con `javac -encoding UTF-8`). Fuera de las diferencias de las tablas de arriba, del título del banner (`JAVA`/`PYTHON`), del orden de las especificaciones del Prototype (`HashMap` frente a `dict`) y de los ids del Facade (marca de tiempo), es **idéntica**. Estos detalles de formato son del Java y se conservan para no introducir diferencias:

- Las secciones 8 (Adapter) y 12 (State) no terminan con una línea en blanco, así que `>>> 9.` y `>>> 13.` quedan pegados a la línea anterior.
- En el Observer se imprimen dos líneas en blanco seguidas después de "Cliente desuscrito".
- El recuadro del catálogo del Iterator no cierra parejo: las filas de datos y de encabezado tienen una columna más que el borde, y la fila del título una menos (más el ancho doble del emoji 📚 en las terminales que lo muestran así).
- Los floats se imprimen "crudos" donde Java concatena un `double` (`$3.5`, `$115.0`), y con `%.2f` donde Java usa `printf`/`String.format`.

Los puntos que **siguen igual** que en Java a propósito (por ejemplo, `AdaptadorDHL` que ignora la dirección, `cantidad_productos` que no cuenta los productos dentro de un `PaqueteProductos`, `EstadoEntregado.anterior()` que permite la "devolución") están documentados en los docstrings y en `ANALISIS_PROYECTO_JAVA.md`.
