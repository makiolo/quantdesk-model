# TI-12-MT5 · Fase B: publicador MT5 → qn

Fecha: 2026-11-09 · Base: 7d38136 · Autor: Claude Opus 5.5 (intentos BDD 126 y 128)

El publicador lleva a qn las velas cerradas del terminal MetaTrader 5 de este Windows, con la fuente como tag. Van a un
**topic nuevo** cuyo nombre decidirá el usuario (`--topic`): network confirmó que a `market.ohlcv` no se le puede añadir
un tag. El Programador de tareas lo lanza cada 15 min y al iniciar sesión. Cada ejecución rellena lo que falte desde la
última vela que qn confirma, de modo que un apagado de días no deja huecos.

Todo está probado con un qn falso en 127.0.0.1 y el módulo MT5 falso de la fase A. No me he conectado ni a qn ni al
terminal reales, no he pedido ni emitido ningún token y no he registrado la tarea.

## Qué hay

| Ruta | Contenido |
|---|---|
| `scripts/publicador_mt5.py` | CLI: `--ejecutar`, `--simular`, `--selftest`; candado, guarda de esquema, de secretos y de disco; registro |
| `scripts/publicador_mt5_lib/nucleo.py` | configuración, candado, velas cerradas de MT5, plan por serie (cola, huecos, revisiones) y publicación por ventanas |
| `scripts/publicador_mt5_lib/qn.py` | cliente REST: `batch_id`, reintentos, rotación de réplicas, cuarentena y conexiones persistentes |
| `scripts/publicador_mt5_lib/qn_falso.py` | qn falso: publish (200, duplicate, 409, 503 con Retry-After, 401), latest, objects y schema |
| `scripts/publicador_mt5_lib/selftests.py` | selftest |
| `scripts/publicador_mt5_tarea.xml` | tarea del Programador de tareas, comentada, para que la registre el usuario |

El publicador reutiliza del extractor la envoltura de sólo lectura, la conversión de la hora del servidor a UTC (regla
`ny+7`), la guarda de secretos y la de disco.

Cambios de esta fase en el extractor:
- La procedencia ya no lleva ningún hash de la cuenta ni del servidor. Lleva el tipo de cuenta, el bróker y el terminal.
- La caché de trozos se separa por el bróker.
- El MT5 falso devuelve la vela en curso, como el terminal real.
- La lista negra estática también revisa los ficheros del publicador.

## Contrato con qn (confirmado por network leyendo su código)

**Topic: `market.ohlcv.v2`** (elegido por el usuario).
- Lo define quantdesk-network en d61b65b, en `deploy/qn-topics/market.ohlcv.v2.json`.
- **Todavía no está registrado en producción.**
- `source` no podía ser tag de `market.ohlcv`: añadir un tag a un topic existente da conflicto y no hay DELETE. Por eso
  el topic es nuevo.
- Contrato:
  - `kind: object`, tags `symbol`, `interval` y `source`;
  - propiedades `open`, `high`, `low`, `close` y `volume` (number) y `date` (string);
  - las seis obligatorias y `additionalProperties: false`;
  - **sin `source` en el objeto**: un tag no puede llamarse como un campo (`fuente_en_objeto=False`).
- El selftest lleva una copia del contrato (`CONTRATO_V2_*`, sin depender del repo de network). Comprueba que cada objeto
  publicado tiene exactamente esas seis propiedades con sus tipos y que `source` va sólo como tag.
- En el publicador, `--topic` sigue siendo obligatorio para publicar y no tiene valor por defecto. La tarea programada
  pasa `--topic market.ohlcv.v2`. La guarda del marcador `TOPIC_POR_DECIDIR` se mantiene en el código y en el selftest:
  sin `--topic`, o con el marcador, sale BLOQUEADO sin preguntar a qn.
- Los nombres de los tres tags y el valor de `source` son configurables. Por defecto `source=mt5`, y
  `--fuente mt5:<bróker>` si hay que distinguir brókers.

**Publicar.**
- `POST {base}/api/v1/topics/<topic>/publish?env=main&wait=accepted`, un objeto por POST, con
  `Authorization: Bearer`.
- `batch_id` = uuid5 del JSON canónico `{topic, tags, obj, ts}`, con el mismo espacio de nombres que `qn_sink.py`.
- Reintentos sólo en 5xx y errores de red: se rota entre las réplicas de `QN_URLS` y se espera lo que diga
  `Retry-After`, con un tope de 30 s.
- Una réplica que no responde pasa 60 s en cuarentena. En Windows, conectar a un puerto cerrado cuesta unos 2 s.
- Un 401 o un 403 paran la ejecución.
- `UnknownTopic` (404 con `code: unknown_topic`, «topic no registrado») también para la ejecución: código 2, sin
  publicar nada.
- Cualquier otro 4xx, incluido el 409, para la serie.

**Leer.**
- Última vela de la serie: `GET {base}/api/v1/topics/<topic>/latest?env=main&symbol=…&interval=…&source=mt5`.
  - Exige `sub:` y acepta `env` y el filtro por tags.
  - Comportamiento confirmado por network:
    - con datos: 200 con `{"env","topic","kind":"object","items":[{tags, ts, recv_ts, batch_id, schema_version, obj}]}`,
      con `ts` en **nanosegundos enteros**. Gana el mayor `(ts, recv_ts, batch_id)`;
    - topic registrado sin datos para el filtro: 200 con `items: []`. **Esto es «sin datos»**, y la serie empieza en
      su fecha inicial;
    - topic no registrado: `UnknownTopic` (404, `code: unknown_topic`, «topic no registrado»). Es un error **fatal**:
      la ejecución sale BLOQUEADO con código 2 y 0 POST. Nunca se toma como «sin datos».
  - Cualquier otro 404 es un error de la serie. El tratamiento antiguo de «404 = sin datos» se quitó.
- Cola: `GET {base}/api/v1/objects/<topic>?env=main&<tags>&from=<ns>&to=<ns>&limit=…`. Formato JSON confirmado:
  - `{"head_cycle","lake_cycle","columns":[{"name","type"}],"rows":[{...}]}`, cada fila un objeto por nombre de columna;
  - columnas fijas `_ts`, `_recv_ts`, `_batch_id` y `_schema_version`, y después los tags y los campos;
  - marcas en RFC 3339 con µs (`YYYY-MM-DDTHH:MM:SS.ffffffZ`);
  - no deduplica.
  El lector toma `_ts` y, si las filas llegaran como listas, las nombra con `columns`.
- Esquema: `GET {base}/api/v1/topics/<topic>/schema?env=main` (exige `sub:`), con `tags` y el JSON Schema del objeto.
- El qn falso del selftest reproduce este comportamiento: `/objects` confirmado, `latest` con `items` (ns), `items: []`
  sin datos y `UnknownTopic` para un topic no registrado.

**Marcas de tiempo.**
- 1h, 5m y 1m:
  - `ts` en ns es la apertura real de la vela en UTC, ya convertida desde la hora del servidor;
  - `date` es esa apertura en UTC, `YYYY-MM-DDTHH:MM:SSZ`. No se copia la hora de Londres con Z falsa del backend.
- 1d (opción (b), decidida por la raíz; ver «Convención de `ts` en 1d»):
  - `ts` = 00:00 UTC del día de la sesión D y `date` = D (`YYYY-MM-DD`);
  - D es la fecha en Nueva York del cierre real (17:00 NY). Por ejemplo, la sesión que abre el domingo a las 21:00 UTC
    lleva `ts` = lunes 00:00 UTC y `date` = lunes.
- `volume` es el `tick_volume` de MT5, porque el FX no tiene volumen real.

**Seguro mientras `market.ohlcv.v2` no esté registrado.**
- Sin `--topic`, o con el marcador, sale BLOQUEADO (código 2) sin preguntar a qn.
- Con un topic, antes de publicar lee `GET …/topics/<topic>/schema`. Sale BLOQUEADO y no publica nada si:
  - el topic no está registrado (`UnknownTopic`): es lo que pasará hoy con `market.ohlcv.v2`;
  - no declara los tres tags (es el caso de `market.ohlcv`);
  - `source` es a la vez tag y campo del objeto.
- Si el topic dejara de estar registrado entre `schema` y `latest`, el `UnknownTopic` de `latest` también para la
  ejecución con código 2.
- Así el publicador queda **desactivado contra qn real** hasta que network registre el topic.

## Convención de `ts` en 1d: decidida la opción (b)

**Decisión de la raíz** (intento 128): opción (b). `ts` = 00:00 UTC del día de la sesión D y `date` = D, igual que
yfinance y que la partición del lago. Está implementada en `nucleo.ts_publicado`.

**Por qué (b).**
- La sesión D cae en la partición D del lago y en una consulta `from`/`to` del día D.
- Empareja con yfinance por `(symbol, interval, ts)`.
- No hay look-ahead.

**Cuándo se publica.**
- Una vela 1d sólo se publica cuando la sesión ya cerró de verdad: apertura real + 1 d <= ahora, es decir, el cierre de
  Nueva York a las 21:00 UTC en verano y a las 22:00 UTC en invierno.
- Ese cierre llega de 2 a 3 h **antes** que `ts` + 1 d; no se espera a `ts` + 1 d.
- Las comparaciones con qn (`latest`, cola, huecos) usan el `ts` publicado; la condición de vela cerrada usa la apertura
  real.

**Disponibilidad.**
- La disponibilidad real de cada vela la da `_recv_ts`, la hora a la que qn la recibió, que siempre es posterior al
  cierre real. Ni `ts` ni `ts` + 1 d la sustituyen.
- Con `ts` + 1 d como disponibilidad, un consumidor sería conservador: vería la vela 2-3 h más tarde de lo posible,
  nunca antes.

**Apertura real.**
- La hora de apertura no está en `ts`. Se reconstruye con la regla de la sesión: la vela de D abre a las 17:00 NY del
  día de mercado anterior.
- En UTC son las 21:00 si en ese instante rige el verano de EE. UU. y las 22:00 en invierno. El domingo es la apertura
  del lunes.
- Es la inversa de `ts_publicado`.

Abajo queda el análisis con el que se decidió.

**Lo que publica hoy yfinance.** Lo leí en quantdesk-backend, sólo lectura.
- `market_scrapper/engine/fx_spot_scraper.py:run_daily` descarga `yf.download(…, interval="1d")`. El índice diario de
  yfinance son fechas sin hora.
- `market_scrapper/market_sink.py:publish_ohlcv` hace `ts = pd.Timestamp(date)`. Como la hora es 00:00, `date` =
  `YYYY-MM-DD` y `ts_ms` = 00:00 UTC del día D.
- Lo confirma el lago: `lago_cierre_c20261101/lago_ohlcv_1d.parquet` tiene `ts_ms` = 1730419200000 =
  2024-11-01T00:00:00Z para la vela del 2024-11-01.
- Así que yfinance publica 1d con `ts` = 00:00 UTC de D y `date` = D.

**Hechos de network.**
- `market.ohlcv` no declara `timeframes`: no hay cubos `@1d`.
- El lago particiona por el día UTC de `ts`.

| | (a) `ts` = apertura real (D-1 a las 21:00/22:00 UTC), lo de hoy | (b) `ts` = 00:00 UTC de D (fecha de la sesión) |
|---|---|---|
| Look-ahead | Ninguno: `ts` + 1 d es el cierre exacto (D a las 21:00/22:00 UTC). | Ninguno: `ts` + 1 d = D+1 a las 00:00 UTC, de 2 a 3 h **después** del cierre real. La disponibilidad es conservadora: no adelanta nada, sólo retrasa un poco. Si `ts` se leyera como «disponible desde ts», sí habría look-ahead (la vela no existe a las 00:00 de D); la convención del lago y del exportador es `ts` + intervalo. |
| Partición del lago | La sesión D cae en la partición D-1. | La sesión D cae en la partición D. |
| Consultas `from`/`to` | Pedir el día D (00:00-24:00 UTC) devuelve la sesión D+1, que abre esa tarde, y no la D. Hay que desplazar la ventana a mano. | Pedir el día D devuelve la sesión D, como con yfinance. |
| Choque con yfinance en el topic nuevo | No pisan nada, porque `source` es tag. Pero la misma sesión tiene `ts` distintos según la fuente (D-1 a las 21:00/22:00 frente a D a las 00:00): un cruce por `(symbol, interval, ts)` no las empareja y el cuadre necesita una regla aparte. | Mismo `ts` y misma `date` que yfinance para la misma sesión: un cruce por `(symbol, interval, ts)` empareja directamente. El contenido sigue siendo de ventanas distintas (sesión de NY frente al día de yfinance), y eso es lo que el cuadre debe medir. |
| Información perdida | Ninguna. | La hora real de apertura deja de estar en `ts`. Se reconstruye con la regla de sesión (cierre a las 17:00 NY) o se añade un campo al esquema del topic nuevo si se quiere explícita. |
| Cambio de código | Ninguno. | Pequeño y local (`nucleo.ts_publicado`), con pruebas. |

**Recomendación que se dio: (b).**
- Alinea la partición del lago, las consultas por día UTC y el cruce con yfinance, sin look-ahead.
- El coste es perder la hora de apertura en `ts`, que es derivable.
- (a) es más «verdad» en el instante, pero obliga a cada consumidor del lago a recordar que la sesión D vive en la
  partición D-1.

## Una ejecución

1. **Candado.** Fichero `runs/TI-12-MT5/publicador/publicador.lock`, creado en exclusiva.
   - Si existe y tiene latido de las últimas 3 h, la ejecución sale con 0 y lo registra.
   - El latido es el mtime: se renueva tras cada ventana.
   - Un candado sin latido durante 3 h se da por caducado (proceso muerto o máquina apagada) y se recupera.
   - El Programador además tiene `IgnoreNew`.
2. **Comprobaciones.** Credenciales y token desde ficheros fuera del repo (nunca se imprimen), esquema del topic y
   enganche a MT5 por la envoltura de sólo lectura.
3. **Para cada serie** (símbolo base del lago × intervalo):
   - **Última vela.** `L` = `latest` filtrado por los tres tags. Si qn no tiene nada, se empieza en la fecha inicial
     del intervalo.
   - **Velas de MT5.** Sólo las CERRADAS (apertura + intervalo <= ahora). La vela en curso, que el terminal sí
     devuelve, no se publica nunca.
   - **Cola.** De las `ventana`+1 velas de MT5 con ts <= `L`, se pregunta a qn cuáles tiene.
     - Las que faltan y no son anteriores a la fecha inicial configurada son huecos de una ejecución anterior cortada y
       se publican. Lo anterior a la fecha inicial nunca se pidió.
     - Con una ventana relativa (5m y 1m, «últimos 30 días»), la fecha inicial avanza con el reloj. Por eso la cota
       lleva un día de margen: a lo sumo se publica un día más de historia, nunca un duplicado.
     - Las que tienen otro contenido se cuentan como revisiones.
   - **Publicación.** En orden de `ts`, por ventanas de 64 velas, cada ventana con 8 hilos. La siguiente ventana no
     empieza si la anterior no entró entera: si algo falla, la serie se para.

**Por qué no quedan huecos.**
- Una ejecución cortada sólo puede dejar huecos dentro de su última ventana, y `L` cae en esa ventana.
- La siguiente ejecución mira las `ventana`+1 velas anteriores a `L` y los rellena.
- Esto vale también si falla la primera ventana de una carga inicial por su principio: esas velas no son anteriores a
  la fecha inicial, así que cuentan como huecos.
- No hay registro local de progreso: manda qn.

**Por qué no hay duplicados.**
- Nunca se reenvía una vela que qn ya tiene, ni las de la cola ni las de antes de `L`.
- Si una vela se reenviara igual, su `batch_id` es el mismo y qn devuelve `duplicate:true` durante 7 días.

**Revisiones.** No se republican; se cuentan en el registro (`revisiones_detectadas`). Motivos:
- qn no reemplaza una vela: cada versión es un objeto más, y en `latest` gana la de mayor `(ts, recv_ts)`.
- La republicación del backend es justo la causa de los 6.047 duplicados por clave de TI-01-INV.
- En el lago, el valor de una vela cerrada es el que se vio al cerrarse.
- Si las revisiones del bróker resultan frecuentes en la fase real, se puede abrir una ventana corta de republicación.
  Es una decisión de la raíz.

**Resumen de cada ejecución.** Una línea en `runs/TI-12-MT5/publicador/publicador_<fecha>.jsonl` y una copia en
`ultimo.json`. Por serie lleva:
- última vela de qn antes de la ejecución;
- velas nuevas, publicadas y duplicadas;
- huecos de cola rellenados y revisiones detectadas;
- velas sin publicar, que son los huecos de publicación;
- huecos de mercado del tramo (fines de semana, que se informan y no se rellenan);
- errores.

Salida: 0 ok, 1 alguna serie con error (la siguiente ejecución retoma), 2 BLOQUEADO y 3 PARADA por disco.

## Profundidad inicial y ritmo

| Intervalo | Inicio si qn está vacío | Velas para 28 cruces | A 1.000 POST/s | A 200 POST/s |
|---|---|---|---|---|
| 1d | 2000-01-01 (lo que tenga el bróker) | ~0,2 M | 3 min | 15 min |
| 1h | 2000-01-01 (lo que tenga el bróker) | ~1,9 M desde 2016; ~4,7 M desde 2000 | 0,5-1,3 h | 2,6-6,5 h |
| 5m | últimos 30 días | ~0,17 M (22,7 M desde 2016) | 3 min (6,3 h) | 15 min (31 h) |
| 1m | últimos 30 días | ~0,87 M (114 M desde 2016) | 15 min (32 h) | 73 min (6,6 días) |

**Medida en el falso.**
- Contra el qn falso local, en el mismo proceso, salen unos 1.060 POST/s con 1 hilo y unos 1.200 con 8.
- Es una cota superior y está limitada por el GIL: no hay red ni WAL.
- El ritmo real con `wait=accepted` en la red local queda por medir en la primera ejecución real (registro
  `duracion_s` y `qn`). La tabla da el rango.

**Propuesta.**
- 1d y 1h completos.
- 5m y 1m, sólo los últimos 30 días hasta que el usuario decida.
- La tarea tiene un límite de 6 h por ejecución. Si la carga inicial de 1h no cabe, la siguiente ejecución sigue desde
  lo que qn confirma.

**WebSocket.**
- Para una carga histórica de 5m o 1m (días con REST), la vía WebSocket (`/qn/ws`, operación `pub`) evitaría una
  petición HTTP por objeto en una sola conexión persistente. Previsiblemente sería varias veces más rápida.
- Lo propongo para esa carga y no lo implemento sin que se decida.

## Tarea programada (`scripts/publicador_mt5_tarea.xml`)

**Qué hace.**
- Se dispara cada 15 min (sin fin) y 2 min después de iniciar sesión.
- `StartWhenAvailable`: si se perdió un inicio, se lanza en cuanto se puede.
- `IgnoreNew`: no arranca otra si la anterior sigue corriendo.
- `RunOnlyIfNetworkAvailable`: sólo con red.
- Corre con el usuario que la registra (`InteractiveToken`, sin `UserId`) y sin privilegios elevados (`LeastPrivilege`).
  No guarda ninguna contraseña de Windows.
- No despierta el equipo y tiene un límite de 6 h por ejecución.
- La acción es `pythonw.exe` del `.venv` (sin ventana) con
  `scripts\publicador_mt5.py --ejecutar --topic market.ohlcv.v2` y el repo como directorio de trabajo.
- Mientras `market.ohlcv.v2` no esté registrado en qn, cada ejecución sale BLOQUEADO (`UnknownTopic`) sin publicar
  nada. Conviene registrar la tarea después de que network registre el topic.

**Cómo se registra.** Lo hace el usuario:

```
Register-ScheduledTask -TaskName "quantdesk\publicador_mt5" -Xml (Get-Content -Raw S:\Projects\quantdesk-model\scripts\publicador_mt5_tarea.xml)
```

**Requisitos.**
- `QN_URLS` en las variables de entorno del usuario, y opcionalmente `QN_ENV`.
- El token en `E:\quantdesk-lab\secrets\qn-mt5.token` (o la ruta de `QDL_QN_TOKEN_FILE`).
- Las credenciales de MT5 en `E:\quantdesk-lab\secrets\mt5.json`.
- El selftest comprueba la tarea leyendo el XML (intervalo, disparadores, políticas y privilegios). No la registra.

## Robustez frente al terminal real (entrega 6)

**Qué se vio en el terminal real** (build 6230, 9.421 símbolos):
- `copy_rates_from_pos` dio `(-1, 'Terminal: Call failed')` en la primera consulta, mientras el terminal sincronizaba
  la historia del símbolo. La misma consulta, poco después, funciona.
- `initialize(path)` dio `-6 'Authorization failed'` con el terminal ya abierto.
- `login` dio `-10005 'IPC timeout'`.

**Reintento acotado de las consultas de datos** (`descarga.consultar`, que usan la descarga, el inventario y el
publicador):
- Sólo se reintentan -1 «Call failed» y -10005 «IPC timeout». Cualquier otro código falla a la primera, como antes.
- Son 5 intentos con esperas de 1, 2, 4 y 8 s (15 s en total como mucho).
  - Se configuran con `QDL_MT5_ESPERAS` (por ejemplo `1,2,4,8`) o con `lectura.configurar_reintentos`.
  - El `dormir` es inyectable: los selftests no duermen y apuntan las esperas pedidas.
- Agotados los intentos, sale el mismo `ErrorTerminal` de siempre: la serie se para y la siguiente ejecución retoma.
- Un `None` sólo cuenta como «sin datos» si `last_error()` es `RES_S_OK`.

**Profundidad del inventario sin bisección (entrega 6b).** Medido por la raíz con sondas de sólo lectura (build 6230,
`maxbars` 100000, EURUSD y NZDCHF):

| Consulta | Resultado en el terminal real |
|---|---|
| `copy_rates_from_pos(sim, tf, pos, 1)`, pos fuera de la historia | `None` con (-1, 'Terminal: Call failed'). En d1 (14.398 velas) con pos 50.000, 99.999, 100.010 y 10 M; en h1 con 100.010 y 10 M |
| `copy_rates_from_pos(sim, tf, 0, count)`, count <= maxbars - 1 | min(count, disponibles). d1 con 20.000 o 99.999 da 14.398; h1 y m1 con 99.999 dan 99.999 |
| `copy_rates_from_pos(sim, tf, 0, maxbars)` | (-2, 'Terminal: Invalid params') en todos los periodos |
| `copy_rates_range` de 1971 a hoy | d1: 14.398 velas, la primera del 1971-01-04; h1 y m1: -2 Invalid params |
| `copy_rates_range` anterior a la historia | las velas que haya, con éxito |

Fuera de la historia da el mismo -1 que la sincronización pendiente, así que una bisección con consultas de una vela no
distingue «no hay» de «aún no». Por eso:
- `inventario.profundidad` hace UNA consulta `copy_rates_from_pos(sim, tf, 0, maxbars - 1)` con el reintento de -1 y
  -10005. Nunca pide count = maxbars.
- La profundidad es la longitud del array; la primera y la última vela salen de sus extremos. El array se libera en
  cuanto se leen (en m1 son unas 100.000 filas).
- `limitada_por_maxbars` se marca cuando la longitud llega a `maxbars` - 1.
- Si un periodo sigue en -1 tras los reintentos (símbolo sin historia en ese periodo, o sin sincronizar), se apunta
  `velas` 0 con `error` y el inventario sigue. Cualquier otro código (-2, -10005 persistente) para el inventario como
  antes.

**Publicador y descarga.** Revisados: ninguno consulta por posición. Los dos piden `copy_rates_range` por trozos (año en
d1 y h1, mes en m5 y m1; como mucho unas 6.300 velas de h1 o 44.700 de m1 por trozo, por debajo de `maxbars`). Un trozo
anterior a la historia vuelve vacío con éxito, según la medida de arriba. Queda por confirmar en la prueba real un trozo de
h1 que esté dentro de la historia del bróker pero más atrás de `maxbars` (h1 con 100.000 velas llega a unos 16 años). Si
diera -1, el publicador pararía esa serie tras los reintentos y lo diría en el registro, sin publicar nada mal.

**Arranque robusto** (`lectura.enganchar`):
1. Si el terminal ya está en marcha, primero se prueba `initialize()` sin ruta.
   - Si tiene abierta la misma cuenta que `secrets/mt5.json`, se engancha y no se vuelve a hacer login. Si aún no está
     conectado (recién abierto), sólo se espera a que conecte (paso 4).
   - La comparación de cuenta y servidor se hace en memoria y no se imprime.
   - Si la cuenta es otra, se hace login sobre esa sesión.
2. Si no estaba en marcha (o `initialize()` sin ruta no engancha), se hace `initialize(path)` y luego `login`.
3. -6 y -10005 en `initialize(path)` y en `login` (y en `initialize()` sin credenciales) se reintentan con las mismas
   esperas. Agotados, el error es el de siempre, sin secretos en el mensaje, y la salida es BLOQUEADO. Un error no
   transitorio (ruta mala, contraseña mala con otro código) no se reintenta.
4. Tras enganchar, se espera de forma acotada a que `terminal_info().connected` sea cierto y haya cuenta.
   - Se sondea cada segundo, hasta 60 s.
   - Si no llega, se cierra el terminal propio y se sale BLOQUEADO («sin conexion al servidor»).

**Falso de MT5.** Reproduce los dos fallos:
- `fallos_call_failed=N`: las N primeras consultas de datos de cada (función, símbolo, periodo) dan `None` con
  -1 «Terminal: Call failed».
- `fallos_arranque=(-6, -10005, ...)`: códigos que devuelven, por orden, `initialize(path)` y `login`.
- `retraso_conexion=N`: tras el login, o al engancharse a un terminal ya abierto, `connected` es falso durante N
  sondeos.
- `cuenta_abierta`: la cuenta con la que está abierto un terminal que ya estaba en marcha.
- `copy_rates_from_pos` imita las tres medidas de la entrega 6b: -1 fuera de la historia, -2 con count >= `maxbars` y
  min(count, disponibles) con count < `maxbars`.

**Selftest del extractor.**
- Arranque: misma cuenta conectada y recién abierta, otra cuenta, -6/-10005 en `initialize(path)` y en `login`, -6
  persistente, sin conexión nunca y ruta mala sin reintento.
- Reintento de datos: esperas pedidas, agotamiento, código no transitorio, `None` con `RES_S_OK` y profundidad igual con y
  sin fallos.
- `copy_rates_from_pos` como el real: -1 en las posiciones medidas, -2 con count = `maxbars` sin reintento, d1 completo
  y m1 con 99.999. La profundidad hace una consulta por periodo, marca m1 como limitada y apunta el periodo sin historia
  con `error` sin parar.
- De punta a punta:
  - una descarga con fallos de arranque y «Call failed» da el mismo hash que sin fallos;
  - un inventario con fallos es igual al limpio;
  - un inventario con `maxbars` 100000 hace 4 consultas por símbolo;
  - el enganche se hace sin login.

## Puesta en marcha (usuario y raíz)

1. **El usuario** abre el terminal MT5 y se autentica él mismo.
2. **La raíz** saca el inventario sin credenciales y comprueba que el desfase en vivo diga «concluyente=True
   coincide=True», con el FX abierto:
   ```
   .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --inventario --sin-credenciales --simbolos @fx28
   ```
3. **La raíz** simula. No usa token ni toca qn; dice cuántas velas publicaría desde la fecha inicial:
   ```
   .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --simular --sin-credenciales --intervalos 1d,1h,5m,1m
   ```
4. **Network** registra `market.ohlcv.v2` en producción. El usuario ya eligió el topic y la raíz la convención de 1d.
   **La raíz** emite el token (`pub:` + `sub:` sobre `market.ohlcv.v2` en `main`) y lo deja en `secrets/qn-mt5.token`.
5. **Primera ejecución real**, con el terminal abierto por el usuario y con `QN_URLS` puesto. Empieza con un símbolo y
   1d, y luego todo:
   ```
   .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --ejecutar --topic market.ohlcv.v2 --sin-credenciales --simbolos EURUSD --intervalos 1d
   .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --ejecutar --topic market.ohlcv.v2 --sin-credenciales
   ```
6. **El usuario** registra la tarea con la orden de arriba; el XML ya lleva `--topic market.ohlcv.v2`. Desde ese
   momento, el publicador usa `secrets/mt5.json` en su propia sesión. Si el terminal ya está abierto con esa cuenta, se
   engancha sin login. Si no, hace `initialize(path)` y `login` (ver «Robustez frente al terminal real»).

**Cómo comprobar la continuidad en qn después.**
- `ultimo.json` y el `jsonl` del día: `sin_publicar` = 0, `error` nulo y `huecos_cola_rellenados` tras un corte.
- En qn, por serie: `GET /api/v1/objects/market.ohlcv.v2?env=main&symbol=EURUSD&interval=1h&source=mt5&from=…&to=…`.
  - Los `_ts` tienen que ir de hora en hora sin más saltos que los fines de semana, que se ven en `huecos_mercado`.
  - Ningún `_ts` puede repetirse con distinto `_batch_id`. `/objects` no deduplica, así que una repetición se vería.
- Tras apagar la máquina unos días, la primera ejecución al encender tiene que dar `nuevas` > 0 y, en la siguiente,
  `nuevas` = 0.

## Evidencia (selftest)

`.venv/Scripts/python -X utf8 scripts/publicador_mt5.py --selftest` termina en `selftest ok` en unos 85 s, sin red real
ni terminal. Comprueba:
- Sale BLOQUEADO con código 2 y 0 POST:
  - sin `--topic` o con el marcador, sin preguntar a qn;
  - con `market.ohlcv.v2` sin registrar (`UnknownTopic` en `schema`);
  - con `UnknownTopic` en `latest` aunque `schema` respondiera, que nunca se toma como «sin datos»;
  - con `market.ohlcv` tal como está (sin el tag `source`);
  - con `source` a la vez como tag y como campo.
- Contrato de `market.ohlcv.v2`, copiado en el test: cada objeto, el de `objeto()`, el cuerpo del POST y todo lo
  publicado de punta a punta, tiene exactamente las seis propiedades con sus tipos, y `source` sólo como tag.
- Lectores con el comportamiento confirmado:
  - `latest` de un topic registrado sin datos da 200 con `{"env","topic","kind":"object","items":[]}`, y eso es «sin
    datos»;
  - con datos, `ts` es un entero en ns;
  - `UnknownTopic` en `publish`, `latest` y `schema` lanza el error fatal propio; cualquier otro 404 es un error
    genérico;
  - `/objects` lleva `_ts` en RFC 3339 con µs y filas por nombre de columna.
- Primera ejecución un miércoles a las 12:30: en qn quedan exactamente las velas cerradas de MT5 (1d, 1h, 5m de 2
  símbolos) y ninguna abierta. La réplica caída y tres 503 con Retry-After se superan rotando.
- Una ejecución repetida en el mismo instante no hace ningún POST.
- Tras apagarse hasta el lunes 9 a las 09:10, con el fin de semana por medio: igualdad exacta con MT5 y sin duplicados.
  El fin de semana se informa como hueco de mercado.
- Fallo a mitad de una ventana (503 persistente en una vela): el hueco queda por detrás de `L`. La siguiente ejecución lo
  rellena (`huecos_cola_rellenados` = 1), con igualdad exacta y sin duplicados.
- Primera ventana de una carga inicial que falla por el principio (las dos primeras velas de 5m): la siguiente ejecución
  las rellena (`huecos_cola_rellenados` = 2), con igualdad exacta y sin duplicados.
- 1d con la opción (b): `ts` = 00:00 UTC de la sesión y `date` = la sesión.
  - Con los dos horarios de EE. UU.: domingo 21:00 UTC → lunes 26 de octubre; domingo 22:00 UTC → lunes 2 de noviembre.
  - En el cambio de marzo: jueves 22:00 UTC → viernes 6; domingo 21:00 UTC → lunes 9.
  - Cada vela 1d publicada tiene `ts` a las 00:00 UTC de su `date` y cae de lunes a viernes.
  - Una sesión sólo se publica tras su cierre real. Antes del cierre (20:30 UTC en verano, 21:30 UTC en invierno) no
    está. Después del cierre (21:30 UTC en verano, 22:30 UTC en invierno) sí está, antes de `ts` + 1 d.
- Un qn nuevo recibe los mismos `batch_id` para las mismas velas.
- Terminal real (entrega 6), de punta a punta contra un qn nuevo:
  - con -10005 y -6 al arrancar y dos «Call failed» por serie: 3 `initialize(path)`, salida 0 e igualdad exacta con MT5;
  - con el terminal ya abierto y la misma cuenta: 0 login, 0 `initialize(path)` e igualdad exacta tras el apagado.
- Una revisión se detecta y no se republica.
- Candado vivo: sale con 0 sin peticiones. Candado caducado: se recupera.
- Token malo: BLOQUEADO.
- `--simular` no pide el token ni toca qn.
- Ninguna función prohibida llamada en MT5. Ni el token ni las credenciales aparecen en la consola, en los ficheros ni en
  las URL.
- Cliente: rotación, 409, 401 sin el token en el mensaje y agotamiento con 503.
- El XML de la tarea.
