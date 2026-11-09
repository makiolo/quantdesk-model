# TI-12-MT5 · Fase B: publicador MT5 → qn

Fecha: 2026-11-09 · Base: 7d38136 · Autor: Claude Opus 5.5 (intento BDD 126)

El publicador lleva a qn (`market.ohlcv`) las velas cerradas del terminal MetaTrader 5 de este Windows, con la fuente
como tag. El Programador de tareas lo lanza cada 15 min y al iniciar sesión. Cada ejecución rellena lo que falte desde la
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

## Contrato supuesto con qn

**Contrato futuro de `market.ohlcv`.**
- Tags `{symbol, interval, source}`. Los nombres de los tres tags y el valor de `source` son configurables; por defecto
  `source=mt5`, y `--fuente mt5:<bróker>` si hay que distinguir brókers.
- Objeto: `open`, `high`, `low`, `close`, `volume`, `date` y, mientras el esquema lo exija, también `source` dentro.

**Publicar.**
- `POST {base}/api/v1/topics/market.ohlcv/publish?env=main&wait=accepted`, un objeto por POST, con
  `Authorization: Bearer`.
- `batch_id` = uuid5 del JSON canónico `{topic, tags, obj, ts}`, con el mismo espacio de nombres que `qn_sink.py`.
- Reintentos sólo en 5xx y errores de red: se rota entre las réplicas de `QN_URLS` y se espera lo que diga
  `Retry-After`, con un tope de 30 s.
- Una réplica que no responde pasa 60 s en cuarentena. En Windows, conectar a un puerto cerrado cuesta unos 2 s.
- Un 401 o un 403 paran la ejecución. Cualquier otro 4xx, incluido el 409, para la serie.

**Leer.**
- Última vela de la serie: `GET {base}/api/v1/topics/market.ohlcv/latest?env=main&symbol=…&interval=…&source=mt5`.
- Cola: `GET {base}/api/v1/objects/market.ohlcv?env=main&<tags>&from=<ns>&to=<ns>&limit=…`. Respuesta JSON
  `{columns, rows}`, con `ts` en ns o en RFC 3339; se aceptan los dos.

**Marcas de tiempo.**
- `ts` en ns es la apertura de la vela en UTC, ya convertida desde la hora del servidor.
- `date` en UTC de verdad: `YYYY-MM-DD` en 1d y `YYYY-MM-DDTHH:MM:SSZ` en el resto. No se copia la hora de Londres con
  Z falsa del backend.
- `volume` es el `tick_volume` de MT5, porque el FX no tiene volumen real.

**Choque con el esquema en 1d** (está en las dudas).
- La vela diaria del bróker es la sesión de Nueva York: la del día D del servidor abre el D-1 a las 21:00 o 22:00 UTC.
- Con `ts` en esa apertura y `date` en UTC, la vela de la sesión D sale con `date` = D-1, y los cubos `@1d` de qn
  (00:00-00:00 UTC) la meten en el día D-1.
- Alternativas que tiene que elegir la raíz:
  - `date` = fecha de la sesión, que no es «UTC de verdad»;
  - construir velas 1d alineadas a UTC agregando las de 1h; habría una vela mínima el domingo.

**Seguro mientras no cambie el esquema.**
- Antes de publicar, el publicador lee `GET …/topics/market.ohlcv/schema`. Si el topic no declara los tres tags, sale
  BLOQUEADO (código 2) y no publica nada.
- Hoy el topic sólo tiene `symbol` e `interval`, así que el publicador queda **desactivado contra qn real** sin tocar
  nada más. Si se publicara antes de tiempo, las velas de MT5 pisarían a las de yfinance en Bento, ClickHouse y Grafana.

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
     - Las que faltan **entre** velas que qn sí tiene son huecos de una ejecución anterior cortada y se publican.
     - Las que tienen otro contenido se cuentan como revisiones.
   - **Publicación.** En orden de `ts`, por ventanas de 64 velas, cada ventana con 8 hilos. La siguiente ventana no
     empieza si la anterior no entró entera: si algo falla, la serie se para.

**Por qué no quedan huecos.**
- Una ejecución cortada sólo puede dejar huecos dentro de su última ventana, y `L` cae en esa ventana.
- La siguiente ejecución mira las `ventana`+1 velas anteriores a `L` y los rellena.
- La vela anterior a la ventana fallida siempre está en qn y sirve de ancla. No hay registro local de progreso: manda qn.

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
- La acción es `pythonw.exe` del `.venv` (sin ventana) con `scripts\publicador_mt5.py --ejecutar` y el repo como
  directorio de trabajo.

**Cómo se registra.** Lo hace el usuario:

```
Register-ScheduledTask -TaskName "quantdesk\publicador_mt5" -Xml (Get-Content -Raw S:\Projects\quantdesk-model\scripts\publicador_mt5_tarea.xml)
```

**Requisitos.**
- `QN_URLS` en las variables de entorno del usuario, y opcionalmente `QN_ENV`.
- El token en `E:\quantdesk-lab\secrets\qn-mt5.token` (o la ruta de `QDL_QN_TOKEN_FILE`).
- Las credenciales de MT5 en `E:\quantdesk-lab\secrets\mt5.json`.
- El selftest comprueba la tarea leyendo el XML (intervalo, disparadores, políticas y privilegios). No la registra.

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
4. **La raíz** emite el token (`pub:` + `sub:` sobre `market.ohlcv` en `main`) cuando quantdesk-network tenga el esquema
   con el tag `source` y el backend haya adaptado sus consumidores. Lo deja en `secrets/qn-mt5.token`.
5. **Primera ejecución real**, con el terminal abierto por el usuario y con `QN_URLS` puesto. Empieza con un símbolo y
   1d, y luego todo:
   ```
   .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --ejecutar --sin-credenciales --simbolos EURUSD --intervalos 1d
   .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --ejecutar --sin-credenciales
   ```
6. **El usuario** registra la tarea con la orden de arriba. Desde ese momento, el publicador hace `initialize(path)` y
   `login` con `secrets/mt5.json` en su propia sesión.

**Cómo comprobar la continuidad en qn después.**
- `ultimo.json` y el `jsonl` del día: `sin_publicar` = 0, `error` nulo y `huecos_cola_rellenados` tras un corte.
- En qn, por serie: `GET /api/v1/objects/market.ohlcv?env=main&symbol=EURUSD&interval=1h&source=mt5&from=…&to=…`.
  - Los `ts` tienen que ir de hora en hora sin más saltos que los fines de semana, que se ven en `huecos_mercado`.
  - Ningún `ts` puede repetirse con distinto `batch_id`.
- Tras apagar la máquina unos días, la primera ejecución al encender tiene que dar `nuevas` > 0 y, en la siguiente,
  `nuevas` = 0.

## Evidencia (selftest)

`.venv/Scripts/python -X utf8 scripts/publicador_mt5.py --selftest` termina en `selftest ok` en unos 85 s, sin red real
ni terminal. Comprueba:
- Con el esquema de hoy (sin `source`), sale BLOQUEADO y hace 0 POST.
- Primera ejecución un miércoles a las 12:30: en qn quedan exactamente las velas cerradas de MT5 (1d, 1h, 5m de 2
  símbolos) y ninguna abierta. La réplica caída y tres 503 con Retry-After se superan rotando.
- Una ejecución repetida en el mismo instante no hace ningún POST.
- Tras apagarse hasta el lunes 9 a las 09:10, con el fin de semana por medio: igualdad exacta con MT5 y sin duplicados.
  El fin de semana se informa como hueco de mercado.
- Fallo a mitad de una ventana (503 persistente en una vela): el hueco queda por detrás de `L`. La siguiente ejecución lo
  rellena (`huecos_cola_rellenados` = 1), con igualdad exacta y sin duplicados.
- Un qn nuevo recibe los mismos `batch_id` para las mismas velas.
- Una revisión se detecta y no se republica.
- Candado vivo: sale con 0 sin peticiones. Candado caducado: se recupera.
- Token malo: BLOQUEADO.
- `--simular` no pide el token ni toca qn.
- Ninguna función prohibida llamada en MT5. Ni el token ni las credenciales aparecen en la consola, en los ficheros ni en
  las URL.
- Cliente: rotación, 409, 401 sin el token en el mensaje y agotamiento con 503.
- El XML de la tarea.
