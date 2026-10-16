# Revisión exhaustiva de los patrones en Python

Revisión de solo lectura hecha el 2026-10-15 sobre los 16 paquetes, sus `demo.py`, los tests, `main.py` y la documentación.
Cada hallazgo se confirmó ejecutando código. La lectura directa del código re-confirmó #1 (Prototype), #2 (Proxy), #3 (State), #12 (Observer) y #16 (Command).

## Resolución (2026-10-15)

Después de la revisión se aplicaron los arreglos en el código, los tests y la documentación. Cada hallazgo lleva ahora una marca de **Estado**: ✅ Corregido o 📐 **Decisión de diseño** (se conserva a propósito, con el motivo). Ya no quedan hallazgos "no aplicados". Las marcas se verificaron leyendo el código actual, no los resúmenes.

- **Tests:** 286 pasan (`python -m unittest discover -s tests -v`, sin `PYTHONIOENCODING`; eran 194 antes de la revisión y 271 después de la primera ronda de arreglos). Cobertura de ramas: 99 % (tests + `main.py`). `python main.py`, `python -W error main.py` y `python -X dev -W error main.py` terminan con código 0, y también las 16 demos ejecutadas como módulo con la salida redirigida.
- **Herramientas:** `mypy patrones main.py tests` (configuración de `pyproject.toml`, con `@override` obligatorio) y `mypy --strict patrones main.py` sin errores; `ruff check .` (E, F, W, B, UP, SIM, RUF, PL; línea de 100) sin hallazgos. Las pocas excepciones están justificadas en `pyproject.toml` y en el código (ver README, "Calidad del código").
- **Salida frente a Java:** `python main.py` se comparó línea por línea con `java Main`. Solo difiere en el título del banner, el orden de las especificaciones del Prototype (`HashMap` frente a `dict`), los ids del Facade y las correcciones deliberadas (Facade, Template); ver [`JAVA_VS_PYTHON.md`](JAVA_VS_PYTHON.md#formato-heredado-que-se-conserva).
- **Decisión pendiente (al final del documento): se eligió (a)**. Los hallazgos #10 (Facade), #14 (Template) y #15 (Command) se **corrigieron en Python** y la diferencia con el Java quedó documentada en [`JAVA_VS_PYTHON.md`](JAVA_VS_PYTHON.md#diferencias-deliberadas-con-el-java-original). Por eso algunos números de las demos ya no coinciden con `Main.java`.
- **Segunda ronda (lo que estaba "no aplicado"):** `RegistroPrototipos` guarda la instancia en la clase base (#28); PEP 695 y `typing.Self` (#29); `Final`, `@override`, anotaciones y propiedades unificados, con `estrategia_pago` y `descripcion` como propiedades (#36); ayudantes de test únicos en `tests/ayudantes.py` (#36); búsqueda de código muerto con `coverage` y tests nuevos para lo que no se ejecutaba (#37); `retardo_carga` y la configuración del proxy pasan a keyword-only (#33).
- **Decisiones de diseño (se conservan a propósito, documentadas):**
  - **#19** `next() -> T | None`: es el contrato GoF/Java que se enseña; `__next__` (protocolo de Python) lanza `StopIteration`. Las demos recorren con `for`.
  - **#29** `ValueError` (y no `KeyError`) para un prototipo desconocido: es un argumento inválido, como en `ProductoFactory.crear_producto`.
  - **#31** `NotImplementedError` (paralelo a `UnsupportedOperationException`) y el `isinstance` de `cantidad_productos` (paridad con Java).
  - **#32** `TiendaFacade.realizar_compra_completa` devuelve el `PedidoContext`, igual que Java.
  - **#33** `retardo_carga` sigue en la API (ahora keyword-only): es una dependencia inyectable y además los tests de la demo y de `main()` parchean `time.sleep`.
  - **#35** floats crudos donde Java concatena un `double`, por paridad de la salida.

## Estado base (antes de los arreglos)

- **Tests:** los 194 tests pasan. Pasan también uno por uno, en orden inverso y en 20 órdenes aleatorios. No dejan ruido en stdout.
- **Ejecución:** `python main.py`, `python -W error main.py` y `python -X dev main.py` terminan bien y sin warnings.
- **Imports:** los ~100 submódulos se importan bien de forma aislada; no hay imports circulares.
- **Fidelidad al Java:** las afirmaciones sobre el comportamiento del Java original se verificaron contra `../src` y son correctas, salvo detalles menores (ver #27).

**Conclusión:** en lo funcional el proyecto está sano. Los problemas son de **precisión didáctica**, de **huecos en los tests** y de **consistencia**. En material para enseñar, una afirmación falsa sobre el lenguaje es más grave que un bug.

---

## ALTA: afirmaciones técnicas falsas y fallos de ejecución

| # | Dónde | Problema | Arreglo | Estado |
|---|---|---|---|---|
| 1 | `creacional/prototype/producto_prototype.py:5-6,31`, `JAVA_VS_PYTHON.md:201,209`, `README.md:142` | Llama "copia profunda" a `dict(...)`, que es una copia **superficial**. Funciona solo porque los valores son `str`. Con una lista como valor, el original queda modificado al cambiar el clon (verificado). | Explicar copia superficial frente a `copy.deepcopy` y agregar un test con un valor mutable. | ✅ Corregido: `clonar()` documentado como copia superficial, nuevo `clonar_profundo()` (`copy.deepcopy`) y tests con un valor mutable |
| 2 | `estructural/proxy/producto_premium_proxy.py:10-24` | Dice que `__getattr__` "intercepta cualquier atributo". Es falso: solo se llama cuando la búsqueda normal falla, y nunca para dunders (`len()` y `str()` fallan). Además, el ejemplo no comparte la interfaz `ProductoPremium` y entra en `RecursionError` con `copy.copy`. | Corregir el texto, mencionar sus límites y proteger los nombres que empiezan con `_`. | ✅ Corregido: docstring corregido, clase real `ProxyDinamico` con guard `_` y tests de sus límites |
| 3 | `comportamiento/state/pedido_context.py:10-11,21` | Justifica un import local por un ciclo de imports que **no existe**: subido al nivel de módulo, funciona. El ciclo real está entre los estados. | Subir el import y explicar dónde está el ciclo de verdad. | ✅ Corregido: import subido a nivel de módulo; el ciclo real (entre estados) está explicado |
| 4 | `main.py:32` | `sys.stdout.reconfigure(...)` falla en IDLE y con un stdout redirigido a un objeto que no es de archivo. | Usar `if hasattr(sys.stdout, "reconfigure")` y agregar un test de humo de `main()`. | ✅ Corregido: `main.py` usa `patrones.consola.configurar_utf8` (con `getattr`) y `tests/test_main.py` ejecuta `main()` |
| 5 | `JAVA_VS_PYTHON.md:786-793` | El snippet de Iterator recorre con `for` un iterador ya agotado, así que no imprime nada: enseña un bug. | Llamar a `it.reset()` o crear un iterador nuevo. | ✅ Corregido (`JAVA_VS_PYTHON.md`: el snippet usa `reset()`) |

## MEDIA: corrección, fidelidad al patrón y tests

### Creacionales y estructurales

| # | Dónde | Problema | Estado |
|---|---|---|---|
| 6 | `creacional/factory/producto_factory.py:7-8,30-33` | Dice que cumple Open/Closed, pero el diccionario es local y se reconstruye en cada llamada: agregar un tipo obliga a editar el método. Conviene un registro a nivel de clase con `registrar()`, o mencionar `match`. | ✅ Corregido: registro `_CONSTRUCTORES` a nivel de clase + `registrar()` |
| 7 | `creacional/builder/pedido.py:29,66-68,86` | El producto no es inmutable: guarda la lista del llamador por referencia y la expone sin copiar. Debería convertirla en `tuple`. | ✅ Corregido: `Pedido` guarda una `tuple` |
| 8 | `creacional/builder/pedido.py:9,27-28` | Dice que el constructor es "interno", pero nada lo impide. Hay que aclarar que en Python solo queda la convención. | ✅ Corregido: el docstring dice que es solo una convención |
| 9 | `estructural/decorator/producto_decorador.py:13-14` | Ofrece `@decorador` como alternativa al Decorator de GoF. Son conceptos distintos, aunque compartan nombre. | ✅ Corregido: aclarado en el docstring y en `JAVA_VS_PYTHON.md` |
| 10 | `estructural/facade/tienda_facade.py:69-74,96-104` | Valida un total de $115 (con envío Express) pero cobra $100, y descarta el `Pedido` que construyó. | ✅ Corregido: valida, cobra y registra `pedido.calcular_total()` (914.99). **Difiere del Java**, decisión (a) |
| 11 | `estructural/facade/tienda_facade.py:61-64` | Cualquier tipo distinto de `"libro"` (incluido `"LIBRO"` o `"juguete"`) se crea como electrónico. Debería delegar en `ProductoFactory.crear_producto`. | ✅ Corregido: delega en `ProductoFactory.crear_producto` (ignora mayúsculas, tipo inválido rechaza la compra) |

### Comportamiento

| # | Dónde | Problema | Estado |
|---|---|---|---|
| 12 | `comportamiento/observer/tienda.py:34` | Recorre la lista mientras puede cambiar: si un observador se desuscribe durante la notificación, el siguiente no recibe el mensaje. Es el bug clásico del patrón. Arreglo: `for cliente in list(self._clientes)`. | ✅ Corregido: itera una copia (`list(self._clientes)`) y hay test |
| 13 | `comportamiento/strategy/estrategia_pago.py:8-9`, `carrito_compra.py:31` | Promete duck typing, pero la anotación es la ABC (tipado nominal), así que mypy rechaza el test `Espia`. Usar `typing.Protocol` y explicar nominal frente a estructural. | ✅ Corregido: `EstrategiaPago` es un `typing.Protocol` |
| 14 | `comportamiento/template/procesador_pedido.py:36-37` | Calcula un total de $585 pero cobra $500, y el test lo da por correcto. El bug viene del Java. | ✅ Corregido: `calcular_costos` devuelve el total y se cobra (585.00 / 985.00 / 363.00). **Difiere del Java**, decisión (a) |
| 15 | `comportamiento/command/carrito_compra_command.py:37-43` | El descuento fijo se guarda como porcentaje, así que cambia si cambia el carrito. Tampoco hay validaciones: se llega a totales negativos. | ✅ Corregido: `DescuentoVigente` (monto fijo guardado como monto, total >= 0, `ValueError`). **Difiere del Java**, decisión (a) |
| 16 | `comportamiento/command/gestor_promociones.py:27-29` | Borra el historial de rehacer **antes** de ejecutar el comando nuevo: si el comando falla, se pierde lo deshecho. | ✅ Corregido: ejecuta primero y trunca el historial de rehacer después |
| 17 | `comportamiento/command/aplicar_descuento_*_command.py` | Si se ejecuta dos veces la misma instancia de un comando, deshacer queda roto. Documentarlo o copiar el comando al guardarlo en el historial. | ✅ Corregido: el gestor guarda `copy.copy` de cada comando |
| 18 | `comportamiento/iterator/catalogo.py:10-12,84,89-105` | Los generadores no son "equivalentes": son perezosos y no toman una foto fija como los iteradores. Además, `items_por_popularidad` sí precalcula (usa `sorted`). | ✅ Corregido: docstrings de `catalogo.py` y `JAVA_VS_PYTHON.md` explican foto fija frente a perezoso |
| 19 | `comportamiento/iterator/demo.py`, `tests/test_iterator.py` | `next()` devuelve `T \| None` y se usa sin comprobar `None` (mypy da error `union-attr`). | 📐 Decisión de diseño: `next()` sigue devolviendo `T \| None` (contrato GoF/Java) y `__next__` lanza `StopIteration`; el demo recorre con `for` y los tests pasan mypy |

### Transversales

| # | Dónde | Problema | Estado |
|---|---|---|---|
| 20 | 10 demos de Facade, Proxy, Template, State, Command e Iterator | En Windows fallan con `UnicodeEncodeError` al redirigir la salida, porque solo `main.py` configura UTF-8. | ✅ Corregido: los `demo.py` configuran UTF-8 al ejecutarse como `__main__` |
| 21 | `README.md:5` | Promete una sección "Java vs Python" en cada módulo, pero falta en 13 módulos. | ✅ Corregido: todos los módulos de patrón tienen "Java vs Python" (solo `consola.py`, una utilidad, no lo lleva y el README lo aclara) |
| 22 | `tests/test_singleton.py:49-62` | El test de thread-safety pasa aunque se quite el `Lock`. Habría que forzar la carrera con un `Barrier` y un `sleep` parcheado. | ✅ Corregido: test con `Barrier` y `sleep` parcheado |
| 23 | tests | Huecos que se detectan con mutaciones (cambiando el código, el test sigue en verde):<br>• la **única corrección de un bug de Java** (descuento fijo con el carrito vacío) no tiene test;<br>• tampoco la tienen el `deshacer` del descuento fijo, `items_por_precio`, `items_por_popularidad`, `PaqueteProductos.remover` y `SeguroDecorador.mostrar_info`. | ✅ Corregido: hay tests para el descuento fijo con carrito vacío, su `deshacer`, `items_por_precio`, `items_por_popularidad`, `PaqueteProductos.remover` y `SeguroDecorador.mostrar_info` |
| 24 | tests | 9 de las 16 demos y `main()` nunca se ejecutan en los tests. | ✅ Corregido: cada paquete tiene un test de su demo y `main()` tiene su prueba de humo |
| 25 | raíz | No hay `pyproject.toml` (`requires-python >=3.12`). En 3.11 falla con un `ImportError` críptico. | ✅ Corregido: `pyproject.toml` y guard de versión en `main.py` |
| 26 | 6 demos | 6 demos no tienen `if __name__ == "__main__"`, así que `python -m ...demo` no imprime nada. El README no documenta `python -m`. | ✅ Corregido: todos los demos tienen `__main__`; el README documenta `python -m patrones.<cat>.<patron>.demo` |

## BAJA: detalles, estilo y consistencia

### 27. Documentación con datos inexactos

**Estado:** ✅ Corregido. `ANALISIS_PROYECTO_JAVA.md` (68 archivos contando `Main`, `Main.java` de 520 líneas, filas de Factory, Prototype y Composite) y `JAVA_VS_PYTHON.md` (Seguro, Template, Facade) se verificaron contra `../src` y el código.

- `ANALISIS_PROYECTO_JAVA.md`:
  - el conteo de archivos está mal (son 68 contando `Main`);
  - `Main.java` tiene 520 líneas;
  - las filas de Factory, Prototype y Composite no coinciden con `Main.java`.
- `JAVA_VS_PYTHON.md`:
  - el snippet del Seguro está parafraseado;
  - el snippet de Template incluye un import que el archivo real no tiene;
  - el de Facade usa datos inventados.

### 28. Singleton

**Estado:** ✅ Corregido en `DatabaseConnection` y en `RegistroPrototipos`: la instancia vive en la clase base y una subclase la comparte (tests de subclase creada antes y después, y test de concurrencia del registro).

`cls._instance` se escribe en la subclase, así que una subclase genera una segunda instancia.

### 29. Prototype

**Estado:** ✅ `clonar()` conserva la subclase (`copy.copy`) y devuelve `Self`; `Prototype`, `Iterator` y `Aggregate` usan genéricos PEP 695 (`class Prototype[T](ABC)`) y sus docstrings comparan con `TypeVar` + `Generic`. 📐 Decisión de diseño: se mantiene `ValueError` (argumento inválido, igual que `ProductoFactory`; `KeyError` sería lo natural si el registro fuera un mapeo).

- `clonar()` crea siempre un `ProductoPrototype`, así que el clon de una subclase pierde su tipo.
- Se podría enseñar la sintaxis PEP 695 o `typing.Self`.
- Para una clave inexistente, lo idiomático es `KeyError`.

### 30. Decorator

**Estado:** ✅ Corregido: `ProductoDecorador` ya no copia `_nombre`/`_precio` y el docstring explica que `mostrar_info` es abstracto.

- Guarda `_precio` y `_nombre` que nadie usa y quedan desactualizados.
- El docstring dice que "delega por defecto", pero el método es abstracto.

### 31. Composite

**Estado:** ✅ Validación de ciclos y de descuentos fuera de 0..100 (`ValueError`, con la constante `PORCENTAJE_MAXIMO`). 📐 Decisión de diseño: `NotImplementedError` y el `isinstance` de `cantidad_productos` se mantienen por paridad con Java y están documentados.

- `NotImplementedError` no es la excepción adecuada para "operación no soportada".
- `cantidad_productos` usa `isinstance`, lo que rompe el tratamiento uniforme.
- No hay control de ciclos ni de descuentos mayores a 100%.

### 32. Facade

**Estado:** ✅ Los ids ya no se repiten (`FAC-<ms>-<contador>`). 📐 Decisión de diseño: sigue devolviendo un `PedidoContext`, como Java (la demo y `consultar_estado_pedido` lo usan); el acoplamiento con State está documentado.

- Los IDs con milisegundos se repiten en compras seguidas.
- Devuelve un `PedidoContext`, lo que acopla al cliente con el subsistema State.

### 33. Proxy

**Estado:** ✅ La configuración del proxy (`usuario_autenticado`, `tipo_suscripcion`, `retardo_carga`) es keyword-only, en el proxy y en `ProductoPremiumReal`, con test. 📐 Decisión de diseño: `retardo_carga` sigue en la API como dependencia inyectable (los tests de la demo y de `main()` además parchean `time.sleep`).

`retardo_carga` es un hook para tests que queda en la API pública; sería mejor parchear `time.sleep`.

### 34. Chain

**Estado:** ✅ Corregido: `set_siguiente` devuelve el siguiente eslabón y el comentario contradictorio se eliminó.

- Un comentario contradice al docstring.
- `set_siguiente` no devuelve nada; si devolviera el siguiente, se podría encadenar.

### 35. Floats crudos

**Estado:** ✅ Corregido en la documentación (`JAVA_VS_PYTHON.md` explica que la coincidencia con `Double.toString` no es universal: `1.0E7` frente a `10000000.0`). 📐 Decisión de diseño: los demos siguen imprimiendo floats crudos donde Java concatena un `double`, por paridad de la salida.

Se imprimen valores como `0.30000000000000004` o `11.111234569272991%`. La afirmación "`f"{x}"` imprime igual que Java" no es universal: Java imprime `1.0E7` donde Python imprime `10000000.0`.

### 36. Matriz de inconsistencias

**Estado:** ✅ Corregido (ver la última columna).

| Eje | Variantes (antes) | Estado |
|---|---|---|
| Imports | Relativos y absolutos mezclados. | ✅ Regla única: relativos dentro del paquete `patrones`, absolutos en `main.py` y en los tests. |
| `@override` | Solo en State y Template. | ✅ En todo método que redefine otro (también en los tests); mypy lo exige con `enable_error_code = ["explicit-override"]`. |
| `Final` en constantes | Solo en Chain. | ✅ En todas las constantes de clase y de módulo (`COSTO_*`, `KG_TO_*`, `PORCENTAJE_*`, `SIN_DESCUENTO`, `LINEA`...). |
| Getters y setters | Quedan `get_`/`set_` en `set_siguiente`, `set_estrategia_pago`, `get_descripcion` y `get_instance`; el resto usa property. | ✅ `set_estrategia_pago(x)` → propiedad `estrategia_pago` con setter; `get_descripcion()` → propiedad abstracta `descripcion`. 📐 Se conservan `set_siguiente` (devuelve el eslabón para encadenar; una asignación no se encadena) y `get_instance` (nombre GoF del punto de acceso global). |
| Cuerpo de métodos abstractos | `...` en unos paquetes, docstring en otros. | ✅ Todos llevan docstring. |
| Anotaciones | `from __future__ import annotations` en unos, comillas en otros. | ✅ Sin comillas; `from __future__ import annotations` solo donde hace falta (nombres bajo `TYPE_CHECKING` o la propia clase). Documentado en el README. |
| Encabezados de docstring | Tres formatos distintos. | ✅ Un solo formato en todos los módulos de patrón: «Patrón X - `Clase` (rol GoF: detalle).» |
| Helpers de test | Nombres y type hints distintos en cada archivo. | ✅ `tests/ayudantes.py`: `capturar`, `capturar_con_resultado` y `exigir_tipo`, tipados. |

### 37. Varios

**Estado:** ✅ Los tests de Singleton y Prototype restauran `_instance` con `addCleanup`; el README explica cómo correr mypy, ruff y coverage. ✅ Código muerto: se midió con `coverage` (tests + `main.py`) y se agregaron tests en lugar de borrar API didáctica: `Catalogo.nombre_catalogo` y `remover_item` de un ausente, `ProductoItem.descripcion`, `ComponenteCatalogo.precio` de los compuestos y la delegación por defecto de `ProductoDecorador.nombre`/`precio` (con un decorador que solo agrega información). Cobertura de ramas: 99 %; lo que falta es inalcanzable a propósito (guardia de versión de `main.py` y ramas de rechazo de los validadores simulados de Chain, siempre aprobados como en Java).

- La fuga de `_instance = None` en los tests no se restaura con `addCleanup`.
- Hay código que nunca se ejecuta.
- No hay instrucciones para correr mypy.

---

## Veredicto por patrón (al momento de la revisión, antes de los arreglos)

| Patrón | Veredicto |
|---|---|
| Singleton | Correcto y bien explicado. El test de concurrencia no prueba nada. |
| Factory | Funciona. El argumento de Open/Closed es falso. |
| Builder | La estructura es clara, pero el producto es mutable y comparte la lista. |
| Prototype | Buenos roles y tests. Tiene el error didáctico más grave: llamar profunda a una copia superficial. |
| Decorator | Es un Decorator GoF real. Lo confunde con `@decorador`. |
| Adapter | Sin problemas relevantes. |
| Composite | Tratamiento uniforme salvo `cantidad_productos`. Le faltan validaciones. |
| Facade | Oculta bien los subsistemas, pero cobra un monto distinto del que valida. |
| Proxy | Cumple los tres roles, pero la nota sobre `__getattr__` es falsa. |
| Observer | Roles claros, con el bug clásico de recorrer una lista que cambia. |
| Strategy | Intercambio en tiempo de ejecución bien mostrado. El duck typing contradice el tipado. |
| Chain | Fiel y desacoplado. Solo detalles menores. |
| Template | Esqueleto, hook y `@final` bien explicados. Cobra el subtotal. |
| State | Transiciones bien diseñadas y tests completos. La justificación del import es falsa. |
| Command | Undo y redo correctos en el caso normal. Frágil con el descuento fijo, con fallos y con reutilización. |
| Iterator | Muy buena didáctica GoF frente al protocolo de Python. El snippet del iterador agotado y la "equivalencia" con generadores están mal. |

## Decisión (ya tomada): fidelidad al Java o corrección

Se eligió **(a)**; ver "Resolución" al principio.

Los hallazgos #10, #14 y #15 son bugs **heredados del Java**. Hay dos caminos:

- **(a) Corregirlos en Python** y documentar la diferencia.
- **(b) Mantenerlos por paridad con el Java** y marcarlos explícitamente como defectos conocidos en docstrings y tests.
