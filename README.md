# 16 Patrones de Diseño en Python

Port didáctico a **Python 3.12** del proyecto Java "16 Patrones en Java": los 16 patrones de diseño del *Gang of Four* aplicados a un mismo dominio, un **e-commerce** (productos, pedidos, pagos, envíos, catálogo).

La idea no es solo traducir la sintaxis. Cada módulo de patrón (todos los de `patrones/` salvo `consola.py`, que es una utilidad compartida y no un patrón) lleva en su docstring una sección **"Java vs Python"** que explica qué cambió y por qué, y qué haría un programador Python "de verdad" en lugar de copiar el patrón tal cual. Si querés la comparación completa, andá directo a [`JAVA_VS_PYTHON.md`](JAVA_VS_PYTHON.md).

- Sin dependencias externas: solo la biblioteca estándar (`abc`, `typing`, `threading`, `unittest`, `time`).
- Un módulo por clase Java, un paquete por patrón, un `demo.py` por patrón.
- 286 tests con `unittest` (incluye una prueba de humo de `main()`, una de cada `demo` y la ejecución de las 16 demos como módulo). Cobertura de ramas: 99 % (ver [Calidad del código](#calidad-del-código)).

## Requisitos

- **Python 3.12 o superior.** Se usa `typing.override` (agregado en 3.12) en todos los paquetes y la sintaxis de genéricos de PEP 695 (`class Prototype[T](ABC)`, también 3.12). Con 3.11 o menor el código no se puede importar.
- Sin `pip install` de nada. El proyecto incluye un `pyproject.toml` (`requires-python = ">=3.12"`, sin dependencias), así que también se puede instalar con `pip install -e .`. `main.py` avisa con un mensaje claro y sale con código 1 si se ejecuta con una versión menor.
- Opcional, para revisar tipos, estilo y cobertura: `mypy`, `ruff` y `coverage` (ver [Calidad del código](#calidad-del-código)). Ninguno es necesario para ejecutar el proyecto.
- Sintaxis moderna usada en el código: uniones `X | None`, `list[str]`/`dict[str, str]` nativos, genéricos PEP 695, `typing.Self`, `typing.Final` y `typing.override`.

## Cómo ejecutar

Desde la carpeta `16PatronesenPython/`:

```bash
python main.py
```

`main.py` es el punto de entrada: recorre los 16 patrones invocando la función `demo()` del `demo.py` de cada paquete. El orden es el de `Main.java` (Singleton, Factory, Observer, Strategy, Decorator, Builder, Chain, Adapter, Prototype, Composite, Template Method, State, Facade, Proxy, Command, Iterator), que no coincide con el de la tabla de abajo (agrupada por categoría). `main.py` y los `demo.py` ya reconfiguran `stdout` a UTF-8 (`patrones/consola.py`), así que la variable de entorno de abajo solo hace falta si la consola sigue deformando los caracteres o al correr los tests.

También podés ejecutar la demo de un solo patrón como módulo (formato `python -m patrones.<categoria>.<patron>.demo`):

```bash
python -m patrones.creacional.singleton.demo
python -m patrones.comportamiento.state.demo
```

No funciona `python patrones/comportamiento/state/demo.py`: los `demo.py` usan imports relativos (`from .xxx import ...`), que solo existen cuando Python los carga como parte del paquete. Cada `demo.py` configura UTF-8 al ejecutarse como `__main__`, y define una función `demo()` que `main.py` llama en orden.

### Acentos y símbolos raros en la consola (Windows)

La salida usa tildes, `ñ` y símbolos Unicode (`✓`, `★`, `📦`). Si la consola de Windows los muestra deformados, forzá UTF-8:

```powershell
# PowerShell
$env:PYTHONIOENCODING = "utf-8"
python main.py
```

```cmd
:: cmd.exe
set PYTHONIOENCODING=utf-8
python main.py
```

```bash
# Git Bash / Linux / macOS
PYTHONIOENCODING=utf-8 python main.py
```

## Cómo ejecutar los tests

```bash
python -m unittest discover -s tests -v
```

Un solo archivo o un solo caso:

```bash
python -m unittest tests.test_state -v
python -m unittest tests.test_command.TestUndoRedo -v
```

Los tests no necesitan `PYTHONIOENCODING`: capturan la salida en memoria y las demos que se ejecutan como subproceso reconfiguran `stdout` a UTF-8. (Si tu consola igual deforma los caracteres de `-v`, usá la variable de arriba.)

Los tests verifican comportamiento observable (valores devueltos, estado, y salida por consola), no solo que "no explote". Todos capturan la salida con los mismos ayudantes de `tests/ayudantes.py`: `capturar(funcion, *args)` devuelve el texto impreso, `capturar_con_resultado(funcion)` devuelve `(resultado, texto)` y `exigir_tipo(objeto, Tipo)` comprueba el tipo y lo estrecha para mypy.

## Calidad del código

Las herramientas son opcionales (el proyecto no tiene dependencias) y su configuración está en `pyproject.toml`. Instalalas en un entorno virtual:

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows (en Linux/macOS: source .venv/bin/activate)
pip install mypy ruff coverage
```

```bash
# Tipos: la configuración del proyecto (incluye @override obligatorio) y el modo estricto
mypy patrones main.py tests
mypy --strict patrones main.py

# Estilo y errores comunes (E, F, W, B, UP, SIM, RUF, PL; líneas de hasta 100 caracteres)
ruff check .

# Cobertura de ramas: los tests más una ejecución completa de main.py
coverage run -m unittest discover -s tests
coverage run --append main.py
coverage report
```

Estado actual: mypy sin errores (normal y `--strict`), ruff sin hallazgos y 99 % de cobertura de ramas. Lo que queda sin cubrir es inalcanzable a propósito: la guardia de versión de `main.py` (solo corre con Python < 3.12) y las ramas de rechazo de los validadores simulados de Chain (`ValidadorStock`, `ValidadorDireccion`, `ValidadorMetodoPago` siempre aprueban, igual que en Java) y de su demo.

Excepciones documentadas en `pyproject.toml` y en el código:

- `PLC0415` (import dentro de una función) en los estados de State: los estados se crean entre sí y un import a nivel de módulo en ambos sentidos sería circular.
- `# noqa: UP036` en la guardia de versión de `main.py`: ruff la considera obsoleta por `requires-python`, pero da un mensaje claro a quien ejecute el script con un Python viejo.
- `# noqa: PLR0913` en `ProductoPremiumProxy.__init__`: tres datos del producto más tres opciones *keyword-only*.

### Convención de anotaciones

- Anotaciones normales, **sin comillas**. `from __future__ import annotations` solo en los módulos que lo necesitan: los que anotan con nombres importados bajo `TYPE_CHECKING` (Chain y State, para evitar imports circulares) o con la propia clase mientras se define (`Pedido`, `ComponenteCatalogo`, `DatabaseConnection`, `RegistroPrototipos`).
- Genéricos con la sintaxis de PEP 695 (`class Iterator[T](ABC)`), `typing.Self` para los métodos que devuelven la propia instancia (`clonar`, el builder fluido, `__iter__`), `typing.Final` en las constantes y `@override` en todo método que redefine otro (mypy lo exige con `enable_error_code = ["explicit-override"]`).
- Getters y setters de Java → propiedades (`carrito.estrategia_pago = PagoTarjeta(...)`, `comando.descripcion`). Se conservan dos métodos con prefijo a propósito: `set_siguiente` (devuelve el eslabón enlazado para encadenar la cadena de validadores; una asignación no se puede encadenar) y `get_instance` (el nombre GoF del punto de acceso de los singletons).

## Los 16 patrones

| # | Categoría | Patrón | Paquete Python (`patrones/...`) | Clases principales | Caso de uso en el e-commerce |
|---|-----------|--------|----------------------------------|--------------------|------------------------------|
| 1 | Creacional | Singleton | `creacional/singleton` | `DatabaseConnection` | Una única conexión (simulada) a la base de datos |
| 2 | Creacional | Factory | `creacional/factory` | `Producto`, `Libro`, `Electronico`, `ProductoFactory` | Crear libros y electrónicos sin exponer el `new` |
| 3 | Creacional | Builder | `creacional/builder` | `Pedido`, `Pedido.PedidoBuilder` | Armar pedidos con opciones (envío, regalo, notas) |
| 4 | Creacional | Prototype | `creacional/prototype` | `Prototype`, `ProductoPrototype`, `RegistroPrototipos` | Clonar productos base (laptop, smartphone, libro) para crear variantes |
| 5 | Estructural | Decorator | `estructural/decorator` | `ProductoDecorador`, `EnvolturaRegaloDecorador`, `SeguroDecorador`, `GarantiaExtendidaDecorador` | Agregar envoltura, seguro o garantía a un producto, apilables |
| 6 | Estructural | Adapter | `estructural/adapter` | `ServicioEnvio`, `AdaptadorDHL`, `AdaptadorFedEx`, `AdaptadorCorreos` + `SistemaDHL/FedEx/Correos` | Una interfaz única para tres couriers con unidades distintas (kg, lb, g) |
| 7 | Estructural | Composite | `estructural/composite` | `ComponenteCatalogo`, `ProductoItem`, `Categoria`, `PaqueteProductos` | Árbol de categorías y paquetes con descuento |
| 8 | Estructural | Facade | `estructural/facade` | `TiendaFacade` | Una sola llamada (`realizar_compra_completa`) que orquesta Factory, Builder, Chain, Strategy y State |
| 9 | Estructural | Proxy | `estructural/proxy` | `ProductoPremium`, `ProductoPremiumReal`, `ProductoPremiumProxy` | Control de acceso y *lazy loading* de contenido premium |
| 10 | Comportamiento | Observer | `comportamiento/observer` | `Observer`, `Cliente`, `Tienda` | Avisar ofertas a los clientes suscriptos |
| 11 | Comportamiento | Strategy | `comportamiento/strategy` | `EstrategiaPago`, `PagoTarjeta`, `PagoEfectivo`, `PagoPayPal`, `CarritoCompra` | Cambiar el medio de pago en tiempo de ejecución |
| 12 | Comportamiento | Chain of Responsibility | `comportamiento/chain` | `ValidadorPedido`, `ValidadorStock`, `ValidadorDireccion`, `ValidadorMontoPedido`, `ValidadorMetodoPago` | Validar un pedido en cadena, cortando en el primer fallo |
| 13 | Comportamiento | Template Method | `comportamiento/template` | `ProcesadorPedido`, `ProcesadorPedidoNacional`, `...Internacional`, `...Express` | Mismo flujo de procesamiento, costos y envío distintos según el tipo |
| 14 | Comportamiento | State | `comportamiento/state` | `PedidoContext`, `EstadoPedido`, `EstadoNuevo`, `EstadoConfirmado`, `EstadoEnviado`, `EstadoEntregado`, `EstadoCancelado` | Ciclo de vida del pedido con transiciones válidas |
| 15 | Comportamiento | Command | `comportamiento/command` | `Command`, `CarritoCompraCommand`, `AplicarDescuento*Command`, `RemoverDescuentoCommand`, `GestorPromociones` | Descuentos con deshacer/rehacer e historial |
| 16 | Comportamiento | Iterator | `comportamiento/iterator` | `Iterator`, `Aggregate`, `Catalogo`, `ItemCatalogo`, `CatalogoIterator*` | Recorrer el catálogo con distintos filtros y órdenes |

## Estructura del proyecto

```
16PatronesenPython/
├── main.py                          # Punto de entrada: demo de los 16 patrones
├── pyproject.toml                   # Metadatos, Python >= 3.12, configuración de mypy, ruff y coverage
├── README.md                        # Este archivo
├── JAVA_VS_PYTHON.md                # Comparación patrón por patrón
├── ANALISIS_PROYECTO_JAVA.md        # Análisis del proyecto Java original y sus rarezas
├── REVISION_PATRONES.md             # Revisión del port y estado de cada hallazgo
├── patrones/
│   ├── consola.py                   # configurar_utf8(), compartido por main.py y los demo.py
│   ├── creacional/
│   │   ├── singleton/   (database_connection.py, demo.py)
│   │   ├── factory/     (producto.py, producto_factory.py, demo.py)
│   │   ├── builder/     (pedido.py, demo.py)
│   │   └── prototype/   (prototype.py, producto_prototype.py, registro_prototipos.py, demo.py)
│   ├── estructural/
│   │   ├── decorator/   (producto_decorador.py, envoltura_regalo_decorador.py,
│   │   │                 seguro_decorador.py, garantia_extendida_decorador.py, demo.py)
│   │   ├── adapter/     (servicio_envio.py, sistema_{dhl,fedex,correos}.py,
│   │   │                 adaptador_{dhl,fedex,correos}.py, demo.py)
│   │   ├── composite/   (componente_catalogo.py, producto_item.py, categoria.py,
│   │   │                 paquete_productos.py, demo.py)
│   │   ├── facade/      (tienda_facade.py, demo.py)
│   │   └── proxy/       (producto_premium.py, producto_premium_real.py,
│   │                     producto_premium_proxy.py, demo.py)
│   └── comportamiento/
│       ├── observer/    (observer.py, cliente.py, tienda.py, demo.py)
│       ├── strategy/    (estrategia_pago.py, pago_*.py, carrito_compra.py, demo.py)
│       ├── chain/       (validador_pedido.py, validador_*.py, demo.py)
│       ├── template/    (procesador_pedido.py, procesador_pedido_*.py, demo.py)
│       ├── state/       (estado_pedido.py, pedido_context.py, estado_*.py, demo.py)
│       ├── command/     (command.py, carrito_compra_command.py, *_command.py,
│       │                 gestor_promociones.py, demo.py)
│       └── iterator/    (iterator.py, aggregate.py, item_catalogo.py, catalogo.py,
│                         catalogo_iterator*.py, demo.py)
└── tests/                           # unittest, un archivo por patrón (test_<patron>.py)
    └── ayudantes.py                 # capturar(), capturar_con_resultado(), exigir_tipo()
```

Convenciones: módulos en `snake_case`, clases en `PascalCase` (los mismos nombres que en Java), métodos y atributos en `snake_case` (`calcularTotal()` pasa a `calcular_total()`), y cada paquete expone sus clases en su `__init__.py`.

## Ruta de aprendizaje sugerida

Si es tu primera vez con los patrones, este orden va de lo simple a lo que combina varias ideas:

1. **Empezá por la base**: Factory (`Producto`), Singleton y Builder. Introducen la jerarquía de productos que reaparece en casi todo.
2. **Comportamiento intercambiable**: Strategy, Observer y Template Method. Son los más fáciles de reconocer y los que más cambian en Python (funciones, callbacks).
3. **Estructura y composición**: Decorator, Adapter, Composite. Fijate bien en la diferencia entre el *Decorator de GoF* y los `@decoradores` de Python (ver `JAVA_VS_PYTHON.md`).
4. **Estado y control**: State, Proxy, Chain of Responsibility.
5. **Los que Python ya trae adentro**: Iterator (generadores) y Prototype (`copy.copy` para la copia superficial y `copy.deepcopy` para la profunda; ver `clonar_profundo()`). Acá se ve mejor que un patrón es una solución a un problema, no una receta fija.
6. **Cerrá con Command y Facade**: Command con undo/redo, y Facade, que junta Factory + Builder + Chain + Strategy + State en una sola llamada.

Para cada patrón: leé el docstring del módulo, corré su `demo.py`, abrí su `tests/test_<patron>.py` y después probá romper algo (por ejemplo, instanciar una clase abstracta) para ver qué error aparece.

## Otras documentación

- [`JAVA_VS_PYTHON.md`](JAVA_VS_PYTHON.md): código Java y Python lado a lado, qué cambió y la alternativa "pythónica" de cada patrón.
- [`JAVA_VS_PYTHON.md`](JAVA_VS_PYTHON.md#diferencias-deliberadas-con-el-java-original): sección **"Diferencias deliberadas con el Java original"**. En Facade, Template Method y Command el port corrige bugs del Java en lugar de copiarlos, y los números de la salida difieren a propósito (por ejemplo, Template Nacional cobra 585.00 y no 500.00).
- [`REVISION_PATRONES.md`](REVISION_PATRONES.md): la revisión del port, con el estado de cada hallazgo (corregido o decisión de diseño documentada).
- [`ANALISIS_PROYECTO_JAVA.md`](ANALISIS_PROYECTO_JAVA.md): arquitectura del proyecto original, dependencias entre patrones y las rarezas/errores encontrados al portar.
- Proyecto Java original (carpeta superior): `README.md`, `README_JAVA.md`, `CLAUDE.md` y `HISTORIAS_USUARIOS.md` (historias de usuario HU-001 a HU-016), más los diagramas `diagrama_clases.puml` y `diagrama_secuencia.puml`.
