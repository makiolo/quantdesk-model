# Borrador del contrato de TI-02-DIARIO (SPRINT-03, fila 1, intento a1)

> **Revisión de la raíz (2026-11-14, `quantdesk-model-4d`).** Autor: Codex `gpt-6.1-sol` high, sólo lectura. Es la base
> de la negociación con el backend y `quantdesk`; **nada está aprobado** hasta el visto bueno del usuario.
>
> 1. **Punto a (dónde corre): se negocia con dos opciones, no con una.**
>    - **A1, la del borrador:** Dagster invoca al exportador en el PC Windows por SSH. El puente no existe: haría falta
>      un servidor SSH en el PC, y eso es un cambio de configuración del sistema que decide y hace el usuario.
>    - **A2, añadida por la raíz:** tarea programada de Windows en el PC, con el mismo precedente que
>      `quantdesk\publicador_mt5`. El exportador deja una señal de salida válida y Dagster vigila su frescura con un
>      sensor (`DagsterJobStale` sobre la última salida válida, no sobre el último run).
>    - A2 no necesita puente, pero se aparta de «el backend crea el job y el schedule» (S03-D2). Lo decide el backend
>      con el usuario.
> 2. **Alcance de «mercado del día» (punto c, límite funcional):** el desktop abre más que OHLCV
>    (`market_fx28_spx30.json`, curvas…). `quantdesk` tiene que decir qué ficheros exige D-I4 de TI-02-DIARIO y cuáles
>    quedan fuera.
> 3. **Errores encontrados que entran en la fila 2:**
>    - el escritor del motor etiqueta `volume_kind="traded"`, pero MT5 da `tick_volume`;
>    - hay que acordar con `quantdesk` qué se hace con una barra OHLCV inválida (rechazo o cuarentena, sin reparar
>      precios).
> 4. **Referencia corregida:** el uso interno de los OAS es S03-D3 en el `next/SPRINT.md` del backend (viene de la
>    decisión D4 del usuario). En nuestro SPRINT.md se citaba como S03-D4.
> 5. El resto (formatos existentes, credencial exclusiva `sub:market.ohlcv.v2`, corte D+1 00:00 UTC con schedule
>    `15 0 * * 2-6` UTC, parada con aviso sin MT5, OAS `BAMLC0A0CM` y `BAMLC0A4CBBB` en la fila 7) se propone tal cual.

**Propuesta recomendada:** ejecutar TI-02-DIARIO en el PC Windows mediante un job gobernado por Dagster, conservar los dos formatos existentes, publicar únicamente cortes completos y añadir OAS después de PUB-02.

Borrador L3 para negociación y aprobación; **ninguna decisión nueva queda aprobada**. Referencias abreviadas: M = quantdesk-model, B = quantdesk-backend, Q = quantdesk. Las rutas y mecanismos nuevos se marcan como **propuesta**.

**a. Dónde corre y cómo llega a E:/**

| Opción | Ventajas | Costes o límites |
|---|---|---|
| PC Windows, invocado desde Dagster | Reutiliza rueda y validación; escribe directamente en E:/ y en la carpeta del desktop | Necesita PC encendido y un mecanismo de ejecución remota aún inexistente en lo revisado |
| Todo en Linux/Dagster, con copia al PC | Centraliza ejecución y credencial | Requiere rueda Linux o adaptar la validación; además necesita transporte y publicación final en Windows |
| Dos fases: volcado en mini y exportación en PC | El lector de qn usa biblioteca estándar; aprovecha la validación Windows | Dos ejecuciones, transporte, estados intermedios y tratamiento explícito del perímetro OAS |

**Recomendación: PC Windows bajo control de Dagster.** El laboratorio entrega también el ejecutable invocable; el backend escribe exclusivamente su integración, schedule y alertas. **Propuesta:** invocación por SSH con comando fijo y resultado estructurado; host, usuario y disponibilidad de SSH en el PC pendientes. Sin un puente aprobado, esta opción todavía no es desplegable.

**Existente:** `requirements.in` fija una rueda cp312/win_amd64; `formato.columnas_de()` y `validacion.validar()` importan `data_py`. No basta con portar la descarga. Véanse [requirements.in](/S:/Projects/quantdesk-model/requirements.in:21), [formato.py](/S:/Projects/quantdesk-model/scripts/exportar_market_history_lib/formato.py:25) y [validacion.py](/S:/Projects/quantdesk-model/scripts/exportar_market_history_lib/validacion.py:80).

Dagster monta código, almacenamiento y SSH de mini en sus contenedores; el inventario de ejecutores contiene mini y macold, sin Windows. No aparece E:/ ni un recurso compartido PC–mini en los archivos revisados: [compose](/S:/Projects/quantdesk-backend/backend/docker-compose-observability.yml:778), [machines.py](/S:/Projects/quantdesk-backend/backend/dagster/code/machines.py:27).

**b. Ruta, carpetas y corte**

| Opción | Ventajas | Costes o límites |
|---|---|---|
| Raíz diaria predeterminada del desktop | Usa el comportamiento existente | Datos repartidos entre perfil del usuario y almacén E:/ |
| Raíz diaria en E:/ mediante `ENGINE_QUANT_DAILY_DATA` | Centraliza almacenamiento | El usuario debe configurar también el proceso del desktop |
| Salida en mini y copia a cualquiera de las anteriores | Evita escritura remota directa en Windows | Requiere compartir/copiar; no hay ruta acreditada |

**Recomendación:** empezar con `%USERPROFILE%/EngineQuantDesktop/data/YYYYMMDD/ohlcv/{ohlcv_daily.parquet,index.json}`; `YYYYMMDD` representa la sesión completada D. Es **existente**, con raíz alternativa admitida: [daily.py](/S:/Projects/quantdesk/clients/python/src/quantdesk/daily.py:26).

**Propuesta de archivo del motor:** `E:/quantdesk-lab/datasets/TI-02-DIARIO/diario_sYYYYMMDD_cYYYYMMDD_<hash8>/`, con `manifest.json`, tablas Parquet y procedencia; `c` identifica el corte UTC C = D+1 a las 00:00. La ruta concreta TI-02-DIARIO no existe acreditada y requiere configuración del consumidor del motor.

Construir fuera de carpetas visibles y publicar tras validar; mismo corte y entradas, mismos hashes. Una salida distinta para un corte ya publicado exige revisión identificada, sin sobrescritura silenciosa. La convivencia con notebooks que escriban la misma fecha queda por acordar.

**c. Formatos y escritor**

Opciones: **reutilizar ambos contratos existentes** (+compatibilidad; −requiere adaptar símbolos y procedencia), crear un formato nuevo (+más metadatos; −requiere cambios en Q), o entregar sólo `engine.market-history/v1` (+menos trabajo; −incumple D-I4). **Recomiendo la primera.**

**Existente:** `desktop.daily-ohlcv/v1` tiene escritor Python y lector Rust, además de pruebas; no es sólo un plan. La ausencia de escritor afecta al laboratorio. Referencias: [daily.write_ohlcv](/S:/Projects/quantdesk/clients/python/src/quantdesk/daily.py:221), [lector Rust](/S:/Projects/quantdesk/rust/crates/quant-desktop-backend/src/daily_market.rs:698).

| Elemento | Contrato recomendado |
|---|---|
| Columnas y tipos existentes | `symbol: utf8`, `ts_ms: int64`, `open/high/low/close/volume: float64`; todas no nulas; Parquet Snappy |
| Clave y orden | `(symbol, ts_ms)` único; orden ascendente por esa clave |
| Tiempo | `ts_ms`: milisegundos Unix UTC de las 00:00 de la fecha de la barra; cierre real separado, 17:00 `America/New_York` para MT5 1d |
| Símbolos | Observables de Q, p. ej. `FX.EURUSD`; **propuesta:** mapa versionado desde el símbolo qn, conservando ambos nombres en procedencia |
| Precios y volumen | Precio en unidades de cotización del instrumento; FX, moneda cotizada por unidad base. MT5 aporta **tick_volume**, no volumen negociado; declararlo por serie |
| Índice existente | `schema`, `market_date`, `file`, `symbols:[{symbol,first,last,rows,source}]`; suministrar `sources` explícitamente: el escritor asume Yahoo si se omite |
| Integridad, propuesta | Manifiesto lateral `ti-02-diario.integridad/v1`: sesión, corte UTC, versiones, mapa de símbolos, unidades, fuentes, entradas y SHA-256 de cada fichero; hashes lógicos separados |
| Responsabilidad | El laboratorio escribe ambos formatos y el manifiesto lateral; el backend sólo los ejecuta y supervisa |

Esquema y escritura acreditados en [daily.py:231](/S:/Projects/quantdesk/clients/python/src/quantdesk/daily.py:231); volumen MT5 en [nucleo.py:182](/S:/Projects/quantdesk-model/scripts/publicador_mt5_lib/nucleo.py:182).

Para el motor se conserva `schema:"engine.market-history", version:"v1"`, tablas y hashes lógicos existentes, sin añadir campos arbitrarios al manifiesto. Reutilizar disponibilidad por recepción, sin activar el proxy `cierre`: [formato.py:162](/S:/Projects/quantdesk-model/scripts/exportar_market_history_lib/formato.py:162), [fuentes.py:316](/S:/Projects/quantdesk-model/scripts/exportar_market_history_lib/fuentes.py:316).

**Límite funcional:** el desktop también busca `market_fx28_spx30.json`, curvas y otros ficheros. OHLCV y market-history no acreditan por sí solos el suministro completo del «mercado del día». Q debe concretar qué salidas adicionales exige D-I4 y quién las transforma: [daily_market.rs:429](/S:/Projects/quantdesk/rust/crates/quant-desktop-backend/src/daily_market.rs:429).

**d. Credencial de lectura**

Opciones: credencial exclusiva del exportador (+mínimo alcance y revocación independiente; −provisionamiento), reutilizar la del scraper (+menos configuración; −permisos excesivos), o leer qn sólo en mini (+centraliza credencial; −obliga a dos fases). **Recomiendo credencial exclusiva.**

**Propuesta:** `sub:market.ohlcv.v2` para el alcance inicial; ampliar exclusivamente a los topics adicionales aprobados. Network emite; el usuario instala el valor en el `.env` privado del ejecutor gobernado por Dagster, fuera de repos; el job lo recibe por entorno. Q no recibe fichero ni variable de credencial.

Network debe confirmar que ese alcance permite catálogo, esquema, latest y lectura de objetos empleados por `descarga_lago.py`; no propongo permisos administrativos para resolverlo. En la opción Windows, el backend debe aceptar que «lado Dagster» incluye su ejecutor remoto.

**e. Hora, calendario y festivos**

Opciones: inmediatamente después de 17:00 NY (+menor demora; −publicador o validación nominal aún pendientes), después del publicador y de medianoche UTC (+reutiliza el corte actual; −entrega más tarde), o depender sólo de una señal de publicación (+orden exacto; −necesita señal y vigilancia de ausencia). **Recomiendo la segunda, con comprobación de publicación.**

**Propuesta:** schedule `15 0 * * 2-6`, zona UTC: martes–sábado 00:15, para sesiones lunes–viernes; corte C a las 00:00 UTC. Exigir cierre NY y versión completa recibida antes de C. Retrasos posteriores a C no se incorporan fingiendo disponibilidad anterior.

Motivo: el exportador actual acepta cortes de fecha a medianoche y exige cierre nominal `ts_ms + intervalo`, además del cierre real MT5. Ejecutarlo sólo después de 17:00 NY todavía excluiría la barra por su fin nominal: [exportar_market_history.py:336](/S:/Projects/quantdesk-model/scripts/exportar_market_history.py:336), [limpieza.py:191](/S:/Projects/quantdesk-model/scripts/exportar_market_history_lib/limpieza.py:191).

Calendario **por fuente/instrumento**: festivo NYSE no implica cierre FX. Festivo confirmado = ausencia esperada registrada, sin inventar barras; calendario desconocido = aviso. El lector diario actual aplica una regla semanal, sin acreditar aquí calendario completo de festivos; coordinarlo con Q.

**f. Sin 1d MT5**

Opciones: avisar y parar (+evita publicar mercado incompleto; −no actualiza la salida diaria), continuar con el resto (+aprovecha datos; −puede aparentar cobertura completa), o reintentar (+absorbe retrasos; −inútil mientras el publicador esté desactivado).

**Recomendación:** mientras esté desactivado, avisar y detener la publicación diaria dependiente de FX; conservar la anterior y registrar `sin_mt5`, fecha esperada y símbolos ausentes. Es ausencia esperada, no fallo del exportador. Sin relleno con yfinance ni ficheros vacíos. Una vez reactivado: reintentos acotados por retraso, manteniendo el corte y sus reglas.

**Propuesta de supervisión:** aviso visible inmediato y frescura calculada desde la última salida validada/publicada. Añadir TI-02-DIARIO a `DagsterJobStale`, contemplando calendario y mantenimiento declarado. Atención: el sensor existente actualiza la métrica por cualquier run exitoso; un aviso tratado como éxito podría ocultar la falta de datos: [run_failure_alerts.py:148](/S:/Projects/quantdesk-backend/backend/dagster/code/run_failure_alerts.py:148).

**g. OAS, sin bloquear fila 2**

Opciones: añadir las dos series aprobadas tras PUB-02 (+alcance conocido; −cobertura inicial limitada), esperar a todos los ratings/sectores (+más cobertura; −demora), o bloquear el exportador entero (+entrega única; −contradice la partición aprobada). **Recomiendo la primera, en fila 7.**

**Existente:** `BAMLC0A0CM` —Corporate IG— y `BAMLC0A4CBBB` —BBB— están aprobadas para captura; el cliente las enumera. La captura usa `unit="percent"`; conversión propuesta explícita: puntos básicos = percent × 100. [fred_client.py:24](/S:/Projects/quantdesk-backend/market_scrapper/engine/fred_client.py:24), [capture_fred_oas.py:35](/S:/Projects/quantdesk-backend/market_scrapper/scripts/capture_fred_oas.py:35).

**Pendiente:** topic, claves y esquema qn, GAP-PUB-01; no inventarlos ni asumir `market.rates.quotes`. Otros ratings/sectores requieren identificación y aprobación. La captura en app_db no acredita publicación en qn.

Fila 7 añadirá un adaptador al contrato de PUB-02: identificador, unidad, fecha de observación, publicación de la fuente, recepción y revisión; disponibilidad conservadora sin look-ahead. Falta de publicación acreditada = aviso, sin sustituirla por la fecha de observación. OAS sólo en el perímetro interno aprobado, sin valores en repos, fixtures ni informes.

**Restricciones del backend → cumplimiento propuesto** — comprobación documental, todavía sin prueba operativa:

| Restricción | Cómo se cumple |
|---|---|
| S03-D2: laboratorio escribe; backend no modifica | Ambos escritores y adaptación pertenecen a M; B integra job, schedule y alertas |
| Cada día hábil, tras NY y MT5 | 00:15 UTC de la madrugada siguiente, con calendario y comprobación de publicación |
| Sin vela del día en curso | Sesión D anterior a la fecha UTC de ejecución; fin nominal y disponibilidad ≤ C |
| Sin vela incompleta | Reutilizar selección de versiones completas; rechazar marcas explícitas de incompletitud si el futuro contrato las incorpora |
| Día sin datos: aviso, nunca fichero vacío | No publicar carpeta/producto nuevo; conservar salida previa y registrar ausencia |
| FX diario `source=mt5` | Política existente `ti-02-data.fuentes/v3`; sin sustitución ni mezcla de fuentes |
| Q sin cliente qn ni tokens | Sólo abre ficheros; credencial exclusiva del ejecutor Dagster |
| Alerta `DagsterJobStale` | Incorporar job y medir salida fresca, sin confundir run exitoso con exportación completa |
| OAS internos, sin fixtures ICE | Incorporación en fila 7 y almacenamiento local dentro del perímetro aprobado |
| PUB-03/PUB-04 fuera del sprint | Sin añadir sus fuentes ni resolver implícitamente la política futura de fuentes |

Base: [entrada de fila 1](/S:/Projects/quantdesk-model/docs/plans/current/SPRINT.md:64), [PUB-05-EXPORT](/S:/Projects/quantdesk-backend/docs/plans/next/SPRINT.md:28), [política de fuentes](/S:/Projects/quantdesk-model/scripts/descarga_lago.py:67).

**Preguntas abiertas, para que las tramite la raíz**

- **Usuario:** ¿aprueba ejecutor Windows gobernado por Dagster, raíz diaria predeterminada, horario propuesto y parada con aviso mientras no haya MT5? ¿Qué máquinas comprende exactamente «equipo del usuario» para OAS?
- **Raíz backend:** confirmar puente de ejecución Windows, instalación del código sin modificarlo, residencia de credencial, señal de finalización MT5, presupuesto de reintentos y alerta por salida fresca. Entregar contrato PUB-02 y actualizar «sprint del laboratorio por asignar» a SPRINT-03.
- **Raíz quantdesk:** confirmar rutas y mapa de observables, historia/universo exigidos, carga de market-history, salidas adicionales del mercado del día, convivencia con notebooks y presentación de fecha antigua/cobertura incompleta.
- **Raíz network:** confirmar alcance mínimo y acceso a metadatos, emitir credencial tras aprobación y acordar topic/esquema OAS con backend; precisar evidencia disponible de versiones/publicación para cortes reproducibles.

**Riesgos y límites**

No se verificaron servicios, montajes reales, SSH Windows, schedules activos, credenciales, contenido del lago ni apertura de artefactos. No se ejecutaron scripts ni selftests: pueden escribir. La inspección fue local; no se acreditan despliegues.

El escritor del motor etiqueta actualmente `volume_kind="traded"` aunque MT5 publica ticks; corregir esa semántica dentro de la fila 2. También difieren las reglas de limpieza OHLCV del laboratorio y de Q: acordar rechazo/cuarentena, sin reparar precios silenciosamente.

La reproducibilidad exige conservar entradas y revisiones con hash; un corte sobre un lago mutable no basta. La ruta engine propuesta no tiene autodescubrimiento acreditado en Q. PUB-02 debe aportar disponibilidad histórica verificable.

Hay una discrepancia de referencia: la entrada de M llama **S03-D4** al uso interno OAS; el `next/SPRINT.md` de B lo registra como **S03-D3**, procedente de la decisión D4 del usuario. También quedan referencias antiguas a `future/SPRINT-03`; la ubicación revisada es `next/SPRINT.md`.

**Texto para registrar tras aprobación** — sustituir marcadores sólo cuando las raíces resuelvan los puntos pendientes; no se ha escrito:

| GOBERNANZA: Cosa | Dueño | Escribe | Decide / aprueba | Cambios desde otro proyecto | Estado |
|---|---|---|---|---|---|
| TI-02-DIARIO: código y dos salidas desde qn; ejecutor Windows invocado por Dagster mediante `<puente acordado>`; desktop en `%USERPROFILE%/EngineQuantDesktop/data/YYYYMMDD/ohlcv/`; engine en `E:/quantdesk-lab/datasets/TI-02-DIARIO/`; formatos existentes y manifiesto lateral de integridad; corte D+1 00:00 UTC; FX sólo MT5; ausencia detiene publicación con aviso | quantdesk-model | laboratorio | usuario | Contrato aprobado de fila 1; revisión de rutas/formatos por quantdesk y backend | decidido (usuario, `<fecha>`) |
| PUB-05-EXPORT: invocación Windows, schedule 00:15 UTC martes–sábado, calendario por fuente y alerta por última salida válida; credencial exclusiva emitida por network e instalada por usuario fuera de repos | quantdesk-backend | backend, sin modificar exportador | usuario | Mensaje a raíz backend | decidido (usuario, `<fecha>`) |
| TI-02-DIARIO-OAS: añadir BAMLC0A0CM y BAMLC0A4CBBB tras PUB-02; topic/esquema `<contrato network/backend>`; unidad percent y publicación de fuente; uso exclusivamente interno | quantdesk-model | laboratorio; backend publica origen | usuario | Adaptador de fila 7; nuevos identificadores requieren aprobación | decidido (usuario, `<fecha>`) |

| DEPENDENCIAS: Tarea local | Depende de | Motivo | Estado |
|---|---|---|---|
| TI-02-DIARIO, SPRINT-03 filas 1–2 | Backend SPRINT-03 PUB-05-EXPORT; quantdesk D-I4; network, credencial mínima | Contrato acordado; laboratorio entrega código sin OAS antes de ola 1 de quantdesk SPRINT-03; backend programa ejecución Windows y frescura. Dependencia de tarea, sin bloquear activación del sprint | decidido (usuario, `<fecha>`); contrato aprobado, ejecución pendiente de entrega |
| TI-02-DIARIO-OAS, SPRINT-03 fila 7 | Fila 2; backend SPRINT-03 PUB-01/PUB-02 y contrato qn acordado con network | Incorporar las dos series aprobadas con unidad y disponibilidad verificadas, exclusivamente dentro del perímetro interno; no bloquea fila 2 | decidido (usuario, `<fecha>`); pendiente de PUB-02 |

Informe entregado aquí: no se indicó ruta `-o`. Sin escrituras, commits ni mensajes a otras raíces.
## Respuestas de las raíces

### network (`quantdesk-network-21`, 2026-11-14), fuente `crates/qn-server/README.md` (tablas REST l. 1353 y 2479; fuentes de consulta l. 1202-1253)

1. **Alcance:** `sub:market.ohlcv.v2` basta para todo lo que usa `descarga_lago.py`: `GET /topics` (lista sólo lo que el
   token puede leer), y `GET /topics/{t}/schema`, `GET /topics/{t}/latest` y `GET /objects/{t}`, que piden `sub` sobre el topic.
   No hace falta ningún permiso de administración. El docstring del script dice «lectura sobre `market.>`»; con el token
   exclusivo, cualquier otro topic dará `unknown_topic` o 403 (corregirlo en la fila 2). Para los OAS de PUB-02 se emite otro
   token y se sustituye, porque el CLI no amplía tokens. Hay que decirles con qué `--envs` se emite (previsiblemente `main`).
2. **Cortes reproducibles:** `/objects` no tiene un parámetro `as_of`, pero cada respuesta trae `x-qn-head-cycle` (H) y
   `x-qn-lake-cycle` (P), y cada fila trae `_cycle`, `_offset`, `_batch_id`, `_recv_ts` y `_schema_version`.
   - Receta: guardar H en el manifiesto del volcado; para reproducir, releer y quedarse con las filas de `_cycle <= H`.
   - Las filas tardías llegan con un `_cycle` mayor y quedan fuera, que es lo correcto.
   - No usar `fresh=true`: las filas provisionales traen `_cycle` y `_offset` nulos.
3. **Garantías:**
   - La retención no borra filas vigentes (OCS-02a).
   - `lake delete` está vetado sobre `market.*` hasta que exista la copia verificada (D7, ADR-001 A1); avisarán antes.
   - La única versión por objeto es `_schema_version`.
   - Las lecturas profundas de v2 son lentas, con un fichero por día (PLAN_LAGO_PARTICIONADO); avisarán si cambia.
4. Emiten el token con la skill `qn-token` cuando el usuario apruebe el contrato.

### backend (`quantdesk-backend-24`, 2026-11-14)

1. **Dónde corre: prefieren A2** (tarea programada de Windows).
   - Contra A1: exige un servidor SSH en el PC y guardar en mini una credencial para entrar al PC, y `machine_docker_op`
     sólo conoce ejecutores Linux con Docker.
   - A2 no rompe S03-D2 en lo esencial: el backend registra la tarea desde su repo con `run_scheduler.cmd` (skill
     `programador-tareas`, idempotente y con política de huecos), y el exportador sigue siendo nuestro.
   - **Condición:** Pushgateway sólo escucha en 10.10.0.3 (WireGuard) y el PC no llega allí, así que la señal de salida
     válida va a mini por qn (LAN, 192.168.1.46:8790).
   - Propuesta: tras validar, el exportador publica un objeto pequeño de estado (sesión D, corte C, hash del manifiesto,
     estado `ok|sin_mt5|error`) en un topic de operaciones que se acuerda con network. Un sensor de Dagster del backend lee
     su `/latest` y alimenta `DagsterJobStale` con la última salida válida, nunca con el último run.
   - Eso amplía la credencial exclusiva con `pub` sobre ese topic. Alternativa peor: abrir Pushgateway en la LAN.
2. **Sin señal de fin del publicador MT5.** Basta con mirar en qn la última vela: `/api/v1/topics/market.ohlcv.v2/latest`
   con `interval=1d` y `source=mt5`, `_ts = D 00:00 UTC` y `_recv_ts < C`. Ojo: `to` es exclusivo (lo vieron en CH-02).
   El horario `15 0 * * 2-6` UTC les vale.
3. **`sin_mt5`:** de acuerdo con avisar, no publicar y conservar la salida anterior. Con el objeto de estado, `sin_mt5`
   queda visible y no cuenta como frescura. El sensor nuevo no se apoya en `run_failure_alerts.py:148`.
4. **Credencial:** de acuerdo con `sub:market.ohlcv.v2`, más el `pub` del topic de estado si sale A2.
5. **OAS:**
   - Unidad verificada en FRED: «Percent, NSA, Daily Close»; el dato de D sale hacia las 9:02-9:05 CST de D+1.
   - La captura guarda `unit='percent'` desde `36aba3d`, y `fred_oas_capture_schedule` está activo desde hoy (22:00 UTC,
     lunes a viernes). Es captura interna en `app_db`, no publicación en qn.
   - El contrato de PUB-02 llega en su SPRINT-03; GAP-PUB-01 sigue abierto. Avisarán al publicar.
6. Corregido en su `e4a22fb`: su `next/SPRINT.md` ya cita nuestro SPRINT-03, filas 1 y 2. S03-D3 está bien en su lado.

### network, topic de estado (`quantdesk-network-21`, 2026-11-14)

Opinión técnica de la guardia. El registro del topic lo aprueba el usuario. Los esquemas de topics son de network y se
piden por issue en su repo (GOBERNANZA).

1. **Norma:** no hay ninguna contra publicar estado operativo en qn. Precedentes: `prometheus.metrics` y
   `qn.canary.object`. Lo prefieren a abrir Pushgateway en la LAN.
2. **Propuesta `deploy/qn-topics/ops.export.status.json`:**
   - `kind` "object", `tags` ["job"], `max_tag_sets` 16, sin timeframes. El sensor lee `/latest?job=…`.
   - Los tags son inmutables: sólo `job`; el host va dentro del objeto.
   - Esquema con `additionalProperties` false, con estos campos:
     - `session`: date (sesión D);
     - `cut_head_cycle`: integer (`x-qn-head-cycle` del corte C);
     - `manifest_sha256`: `^[0-9a-f]{64}$`;
     - `status`: `ok|sin_mt5|error`;
     - `detail`: opcional, como mucho 500 caracteres y sin secretos;
     - `exporter_version`: string;
     - `host`: opcional.
   - Obligatorios: `session`, `cut_head_cycle`, `manifest_sha256`, `status` y `exporter_version`.
   - `max_staleness` 2d. El `ts` del sobre es el instante en que termina la validación.
   - Retención: 7 días en el log y para siempre en el lago (OCS-02); queda un historial auditable.
   - Publicar con `POST /topics/ops.export.status/publish?wait=durable` y un `batch_id` determinista (job + session +
     hash), para que un reintento salga como duplicado.
3. **Credencial:** un token exclusivo con `--grant sub:market.ohlcv.v2 --grant pub:ops.export.status --envs main`
   (`token create` admite varios `--grant`, `crates/qn-server/src/main.rs:283`). El `pub` va sólo a ese topic, sin comodín.
4. **Tras la aprobación:**
   - abrimos un issue en network con el JSON;
   - network lo registra con `register.sh` y emite el token con `qn-token`;
   - el backend pide su propio `sub:ops.export.status`.
