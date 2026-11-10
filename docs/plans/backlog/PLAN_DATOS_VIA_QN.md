# Plan — Datos de mercado vía qn (MT5, publicadores públicos, exportadores)

> **Origen:** división de [backlog/README.md](README.md) (regla de publicadores de §1, filas TI-12-MT5 y TI-13-PUB de
> §2.2, filas TI-12-MT5 y TI-13-PUB de §4), en la versión del árbol revisada el 2026-11-09 sobre el commit `8a849c6`.
> División decidida por el usuario el 2026-11-09 (revisión de planes, GAP-BACKLOG_README-06 opción (a)). Texto de la
> especificación copiado íntegro; lo nuevo va marcado «(usuario, 2026-11-09)».

**Estado:** backlog. Lo que ya está en un sprint del laboratorio se especifica allí; aquí queda su estado, lo que no
tiene sprint y lo que espera a otros proyectos. **Fecha:** 2026-11-09; **puesto al día el 2026-11-10** (revisión
parcial, sección final): TI-12-MT5 está CERRADA y SPRINT-01 archivado
(`../archive/SPRINT-01_2026-11-07_2026-11-09/`); el dossier de TI-12-MT5 ya no está en `current/execution/` sino en
`../archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/`. **Decisiones del usuario del 2026-11-10 aplicadas
(revisión de planes, D1, D2, D3, D3b, D6):** ficha urgente [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md);
TI-02-DATA-V2 en SPRINT-02 (fila 1b de [next/SPRINT.md](../next/SPRINT.md)); incremental de MT5 en INTRA-LOCAL; dueño
de TI-02-DIARIO. Sección final «Decisiones del usuario (2026-11-10)».

## 1. Regla (A16 y A16 bis, usuario, 2026-11-09)

Los datos de mercado entran al lago de `quantdesk-network` (qn) **solo por publicadores**, uno por restricción
tecnológica. MT5, que sólo funciona en Windows, publica desde el Windows del laboratorio (`scripts/publicador_mt5.py`,
topic `market.ohlcv.v2`); las fuentes públicas de mercado (Yahoo/Stooq, FRED, cripto) van en `quantdesk-backend` como
jobs de Dagster en Linux. **El laboratorio consume siempre vía qn** y exporta a `engine.market-history/v1`. Los corpus
genéricos de preentrenamiento (Chronos, LOTSA) no son datos de mercado en vivo y siguen siendo ingesta directa del
laboratorio. El laboratorio no escribe en el backend ni en network: lo que necesite de ellos es una dependencia externa
que lleva el usuario o una sesión de ese proyecto.

Excepciones decididas el 2026-11-09:

- **Binance ya ingerido** (TI-13-PUB, `7ea6d94`): corpus congelado con hash, como Chronos y LOTSA (§5).
- **MT5 intradía 1m y 5m**: se guarda en local ya, sin publicar; se publica en qn al planificar SPRINT-04 (§2).

## 2. MT5 (TI-12-MT5)

| ID | Qué se hace aquí | Cuándo / estado (2026-11-09) | Notas |
|---|---|---|---|
| **TI-12-MT5** (fase C) | Universo ampliado en 1d: continuo (forex 60, metales y energía 16, índices 23, cripto 94) y acciones US grandes (`@us_grandes`, S&P 500: 484 de sesión normal y 13 sólo `-24` = 497); universos con nombre, vela 1d por clase, huecos por clase y ritmo de publicación | **CÓDIGO Y DESCARGAS LOCALES CERRADOS** con SPRINT-01 (2026-11-09; commits hasta `f9dcd0c` y cuadre `fdfa3a7`). Descargas locales 1d: continuo (193 series, 547 226 filas, `E:/quantdesk-lab/data/mt5/continuo_1d_20261109`, `sha256:a503bb75…`), 484 acciones (`us_grandes_1d_20261109`, `sha256:6d9e0528…`) y 13 `-24` (`us_grandes24_1d_20261109`, `sha256:1e58cb0a…`). **Publicar en qn el universo ampliado: lo que queda de esta fila.** Plan nocturno acordado con backend y network (2026-11-09, backend `EXECUTION.md`): ≤ 40 000 objetos por 5 min, 02:00–05:00 CET; noche 1 continuo (~369 000 objetos, ~46 min), noches 2 y 3 acciones (~690 000 cada una, ~1 h 30 min); avisan al empezar y paran si el cursor del Bento se retrasa. **Noche 1 (programada a las 02:03 del 2026-11-10) APLAZADA** por el aviso de la vela incompleta (ver TI-12-MT5-SYNC) **hasta cerrar [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md)** (usuario, 2026-11-10, revisión de planes, D1); noche 2 espera a network y al usuario (cierre de SPRINT-01, §10) | Detalle en `../archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/fase-c.md`. **Meta Platforms resuelto (usuario, 2026-11-09): entra con su `-24`** (`META.NAS-24`, clase `acciones_us_24`). Solapa con los publicadores públicos del backend en acciones US y cripto (GAP-BACKLOG_README-03). Sustituye la cifra anterior de «~180 000 objetos por sondeo de 5 min» (tope del Bento sin lotes) por el tope acordado de 40 000 |
| **TI-12-MT5-SYNC** (nueva, 2026-11-10) | Evitar y corregir la vela 1d publicada incompleta: el 2026-11-09 la vela 1d de MT5, publicada a las 23:01 UTC, salió incompleta en 23 de 28 pares de fx28 porque la historia D1 del terminal no estaba sincronizada (EURUSD salió bien). (1) El publicador publica un símbolo y periodo sólo con la historia sincronizada; (2) republicar las 23 velas del 2026-11-09 con el valor correcto | **Ya, fuera de sprint** (aviso del laboratorio al backend ~23:45 UTC del 2026-11-09; backend `e90eb03`). **Ficha abierta: [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md)** (decisión D1, usuario, 2026-11-10, revisión de planes: «republicar y aplazar»; GAP-DATOS_VIA_QN-03 resuelto). Relacionada con [ISSUE-TI12-MT5-VELA-A-MEDIAS](../issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md), que registra la guarda de historia ya escrita y la tarea programada desactivada por el bloqueo de la cuenta | **Aceptación** (detalle en la ficha): (1) selftest con un MT5 falso que devuelve el D1 parcial («Call failed» o menos barras que el 1m agregado): 0 publicadas y aviso, no velas; (2) **modo de reenvío** de velas ya publicadas; (3) **se aprueban las 23 republicaciones** de las velas 1d de FX del 2026-11-09 y, tras ellas, `scripts/cuadre_mt5.py --m1 --d1` da 0 puntos de diferencia en las 28 velas; (4) la revisión llega a qn y a ClickHouse; (5) se verifica el horizonte de revisión de qn (hipótesis H2 del backend, ~6 h) y, si ya venció, la ficha pide la excepción a network; (6) la carga nocturna de `@continuo` sigue aplazada hasta cerrar la ficha. **Hoy no hay camino de republicación (lo añade el criterio 2):** `nucleo.py::serie` cuenta `revisiones_detectadas` pero sólo publica `huecos + ts > ultimo`, así que una vela ya publicada con valores distintos no se reenvía |
| **TI-12-MT5** (intradía) | 1h, 5m, 1m (y ticks si hay) del publicador MT5 en `market.ohlcv.v2` | **Backlog, condicionada** (usuario, 2026-11-09: «Solo 1d»). No se lanza sin el visto bueno previo de `quantdesk-network` (ritmo, memoria de mini ~2,17 de 3 GiB, ~9 500 particiones diarias ya creadas por el 1d) y aviso al backend (cada republicación completa ~1,4 GiB y ~4 min de CPU en mini). **Decisión (usuario, 2026-11-09): guardar 1m y 5m en local ya, con hash; la publicación en qn se pide al planificar SPRINT-04 del laboratorio** (GAP-BACKLOG_README-04 resuelto) | El código ya lo soporta (`--intervalos`); `--simular` real dio 1h 2,80 M, 5m 0,17 M, 1m 0,83 M barras en fx28 (m1 sólo desde 2025-11 por `maxbars`). Consumidor: TS-05-FREQ (SPRINT-04 del laboratorio); ver GAP-TSFM-04 de PLAN_TSFM_FINANZAS |
| **TI-12-MT5-INTRA-LOCAL** (usuario, 2026-11-09) | Descarga local periódica de 1m y 5m del universo que el bróker sirva (como mínimo fx28), con el extractor de sólo lectura (`scripts/extractor_mt5.py`), a `E:/quantdesk-lab/data/mt5/`, **sin publicar en qn** | **Ya, fuera de sprint** (historia irrecuperable: el bróker sólo da ~100 000 barras y m1 llega hoy sólo a 2025-11). Ficha viva: [ISSUE-TI12-MT5-INTRADIA-LOCAL](../issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md). **Primera descarga hecha (2026-11-09 18:33 CET):** `@continuo` completo (193 símbolos), m1 y m5, 386 series, 37 944 660 filas, 1246,7 MiB en `E:/quantdesk-lab/data/mt5/continuo_m1m5_20261109`, `hash_conjunto sha256:5cd9bf8691bd9d0c5dd5cb0b7328631fb69d52491acc65ddc2b1cdc324e2f9cf`; m1 llega a 2026-08-04 (mediana) y 2025-11-05 (la más antigua); m5 a 2025-07-08 y 2021-11-10. Según la ficha, el manifiesto (criterio 3) está en la carpeta y nada se publicó (criterio 5); criterio 1 sólo en fx28 (`fdfa3a7`); **2 y 4 pendientes**: no hay descarga incremental ni tarea que la repita. **El incremental reanudable se hace ya, fuera de sprint, en esta ficha** y la fila 5 de `next/SPRINT.md` se reduce a «más símbolos y periodos» (D3, usuario, 2026-11-10, revisión de planes; C-DATOS_VIA_QN-03 resuelta). Las acciones (`@us_grandes`) no están en el alcance descargado: **se mide su profundidad y volumen m1/m5 con `--simular` y se incluyen si la cifra es razonable** (presupuesto 100 GB), anotado en la ficha (D3b; GAP-DATOS_VIA_QN-04 resuelto) | **Aceptación:** (1) dos descargas del mismo rango dan el mismo SHA-256; (2) la descarga es reanudable y la siguiente sólo añade barras nuevas (sin huecos entre la última barra guardada y la primera nueva, salvo fines de semana y festivos del bróker); (3) manifiesto con símbolo, periodo, primera y última barra, filas y hash; (4) periodicidad que no pierda barras por `maxbars` (para m1, menos de ~100 000 barras entre descargas: unas 13 semanas en FX y metales de lunes a viernes, 1440 barras al día, y unas 9,9 semanas en cripto 24/7; **recomendada: mensual**, con margen para un fallo); (5) nada se publica en qn ni se envía ninguna orden. Contradice «consume vía qn» sólo en el almacenamiento, no en el consumo: TS-05-FREQ leerá de qn cuando se publique |
| **TI-12-MT5** (tarea programada) | Registrar `scripts/publicador_mt5_tarea.xml` en el Programador de tareas (cada 15 min y al iniciar sesión, `--intervalos 1d`, relleno de huecos desde lo que qn confirma) | **HECHO** (puerta de usuario cumplida): el usuario registró la tarea `quantdesk\publicador_mt5` para el 1d de fx28 (cierre de SPRINT-01, §10; `run_scheduler.cmd` `4cd1237` la registra de forma idempotente; la primera publicación real fue `9b74bed`). SIN VERIFICAR desde esta revisión que la tarea siga activa: `schtasks` no la lista desde la shell de la revisión. La publicación de las 23:01 UTC del 2026-11-09 con velas incompletas (TI-12-MT5-SYNC) fue probablemente de esta tarea (SIN VERIFICAR: no hay registro en este repo) | Token de larga vida `ti12mt5-publicacion-20261109` (id 36, `pub:`/`sub:` sobre `market.ohlcv.v2`, `env=main`) en `E:/quantdesk-lab/secrets/qn-mt5.token`; **la revisión «al cerrar SPRINT-01» está vencida y sin constancia** (el cierre no la menciona): pendiente de la raíz o del usuario |

Opciones descartadas para el intradía (usuario, 2026-11-09): pedirlo sólo al planificar SPRINT-04 sin guardar nada
(se pierde profundidad m1 cada mes); publicar ya a ritmo bajo (más carga en mini).

## 3. Datos públicos de mercado (TI-13-PUB) — movidos al backend

| ID | Qué se hace aquí | Cuándo / estado (2026-11-09) | Notas |
|---|---|---|---|
| **TI-13-PUB** (datos públicos de mercado) | Yahoo/Stooq (miles de tickers diarios), FRED y cripto con histórico completo, leídos de qn | **MOVIDO a `quantdesk-backend`** (publicadores Dagster, A16 bis). **Decisión (usuario, 2026-11-09): plan nuevo en el backend, `PLAN_PUBLICADORES_MERCADO_PUBLICO`**, con FRED común con la fuente USD de F1 de `PLAN_FUENTES_OFICIALES_CURVAS` (GAP-FOC-06) y una tarea OAS para XVA; lo escribe el aplicador del backend (GAP-BACKLOG_README-02 resuelto) | Aquí queda sólo el consumo: exportar con TI-02-DATA lo que llegue al lago. La ampliación «más tickers y cripto» de [next/SPRINT.md](../next/SPRINT.md) fila 7 pasa a «consumir y exportar lo que publique el backend» (C-BACKLOG_README-03 / C-10 resuelta). El filtro de fugas D-11 se aplica también a estas series |

Opciones descartadas (usuario, 2026-11-09): raíl nuevo en SPRINT-02 del backend; ingesta directa provisional del
laboratorio.

## 4. Exportadores

| ID | Qué se hace | Aceptación | Estado |
|---|---|---|---|
| **TI-02-DATA-V2** (usuario, 2026-11-09) | `scripts/descarga_lago.py` lee **sólo** `market.ohlcv.v2` (hoy `TOPICS_DEFECTO` en la línea 57 lee `market.ohlcv`, v1, congelado desde el corte a v2 del 2026-11-09); quita v1 de los topics por defecto y del código | (1) Un dataset nuevo con corte posterior al 2026-11-09 contiene las barras de v2 de esas fechas (no se congela en silencio); (2) selftest en verde con un caso que falla si el topic por defecto vuelve a v1; (3) mismas garantías de hash y look-ahead de TI-02-DATA; (4) el informe dice que los cuatro datasets de TI-02-DATA (`binance_c20261101`, `lago_c20261101`, `lago_cierre_c20261101`, `lago_c20261107`) **se regeneran desde la versión anterior del script en git** (`git show 0e67465:scripts/descarga_lago.py`, último commit que lee v1), no desde el nuevo; **(5, nuevo 2026-11-10) selección por `source`**: v2 trae el tag `source` (`mt5`, `market_scraper`, y `yahoo`/`stooq`/exchange cuando el backend publique), cada combinación de etiquetas es un fichero distinto y `exportar_market_history_lib/fuentes.py:230` toma `instrument = symbol` sin mirar `source`, así que dos fuentes del mismo símbolo e intervalo se mezclarían o chocarían; el exportador (y el volcado) elige la fuente por clase y falla si una (símbolo, intervalo, ts) llega de dos fuentes sin regla; **(6) FX diario sólo con `source=mt5`** (criterio 3 de [ISSUE-LAGO-FX-1D-CLOSE](../issues/ISSUE-LAGO-FX-1D-CLOSE.md)): un corte nuevo del lago con ese filtro cuadra con `scripts/cuadre_mt5.py`; el 1d de yfinance (`market_scraper`) tiene el close del inicio del día y no se corrige en el lago; **(7)** `lago_cierre_c20261101` se regenera sólo para reproducir el hash y el informe lo marca como afectado por esa incidencia | **En SPRINT-02, fila 1b de [next/SPRINT.md](../next/SPRINT.md)** (con la repetición de la tabla FX sobre el 1d de MT5, en dos tablas; usuario, 2026-11-10, revisión de planes, D2 y D15; GAP-DATOS_VIA_QN-02 y C-DATOS_VIA_QN-01 resueltos). **Es la condición previa de los criterios 1–3 de ISSUE-LAGO-FX-1D-CLOSE** y de las filas 2, 4 y 7 de `next/SPRINT.md`, que ahora la declaran. Resuelve **C-12** y la urgencia **U5** de la revisión (exportaciones congeladas en silencio). Opciones descartadas: v2 por defecto con v1 para reproducir hashes; selección a mano |
| **TI-02-DIARIO** (D-I4, usuario, 2026-11-09) | **Exportador diario** que escribe desde qn el mercado del día y los datasets que `quantdesk` ya abre (incluidos los OAS para XVA), para que el motor no dependa de qn ni use tokens | (1) Cada día hábil deja en la ruta que abre `quantdesk` el mercado del día y los datasets con hash; (2) un día sin datos en qn produce un aviso, no un fichero vacío; (3) `quantdesk` no importa ningún cliente de qn ni lee tokens; **(4, nuevo 2026-11-10)** el FX diario sale con `source=mt5` (como TI-02-DATA-V2 (6)), y el job corre después de la publicación nocturna de MT5 (la vela 1d de MT5 sólo se publica tras el cierre de Nueva York, 17:00 NY, y el día en curso no aparece hasta entonces: backend `ISSUE-FX-1D-CLOSE-YFINANCE`); un día sin vela de MT5 es aviso, no se rellena con yfinance | Backlog. **Dueño (usuario, 2026-11-10, revisión de planes, D6; GAP-DATOS_VIA_QN-01 resuelto): el laboratorio escribe el código** (reutiliza `exportar_market_history_lib`, hashes y reglas sin look-ahead) **y el backend lo programa en Dagster después del cierre de Nueva York** (cuando MT5 publica el 1d), en su SPRINT-03 (D5: `quantdesk-backend/docs/plans/future/SPRINT-03/SPRINT.md`, junto con PUB-00, PUB-01 y PUB-02). Debe existir antes de la ola 1 de SPRINT-03 de `quantdesk` (decisión «Publicador OAS ya», usuario, 2026-11-09). Resuelve D-I4 (GAP-TSFM_INTEGRACION-04): descartado que `quantdesk` lea qn directamente |

## 5. Binance ingerido directamente (C-09 / C-BACKLOG_README-02)

**Decisión (usuario, 2026-11-09): corpus congelado con hash**, excepción a A16 bis como Chronos y LOTSA. El dataset
`binance_c20261101` (TI-13-PUB `7ea6d94`, segunda tabla de TS-00-BENCH `baa4ee6`) no se rehace; lo nuevo de cripto
llegará por qn cuando exista el publicador del backend. Opciones descartadas: rehacerlo desde qn (cambian hashes y la
tabla del banco); retirar Binance del banco.

## 6. Dependencias externas (2026-11-09)

| Tarea local | Depende de | Estado | Mientras tanto |
|---|---|---|---|
| TI-12-MT5 fase C (publicar en qn) e intradía (publicar) | visto bueno de `quantdesk-network` (ritmo, compactación) y aviso a `quantdesk-backend` (carga del Bento) | fase C: **plan nocturno acordado con backend** (≤ 40 000 objetos/5 min, 02:00–05:00 CET; noche 1 continuo aplazada; noche 2 espera a network y al usuario); intradía: se pide al planificar SPRINT-04 del laboratorio (usuario, 2026-11-09) | descarga local en `E:/quantdesk-lab/data/mt5/` (TI-12-MT5-INTRA-LOCAL para 1m y 5m) |
| TI-13-PUB (mercado público) y TI-02-DATA ampliada (next/SPRINT fila 7) | `quantdesk-backend` `PLAN_PUBLICADORES_MERCADO_PUBLICO` (backlog, sin sprint) | decidido (usuario, 2026-11-09) | Binance congelado de TI-13-PUB; FX diario de qn **sólo `source=mt5`** (el 1d de yfinance tiene el close desfasado: ISSUE-LAGO-FX-1D-CLOSE) |
| TI-02-DATA-V2 (lectura de `market.ohlcv.v2` con selección por `source`) | ninguna externa; es **condición previa** de ISSUE-LAGO-FX-1D-CLOSE y de las filas 2, 4 y 7 de `next/SPRINT.md` | SPRINT-02, fila 1b (usuario, 2026-11-10, D2) | `descarga_lago.py` lee `market.ohlcv` (v1) congelado desde el 2026-11-09: no ve el 1d de MT5 |
| TI-02-DIARIO | backend: programación en Dagster tras el cierre de NY (SPRINT-03 del backend, D5); OAS del publicador del backend | mecanismo (usuario, 2026-11-09) y dueño (usuario, 2026-11-10, D6): el laboratorio escribe, el backend programa | — |
| TI-12-MT5-SYNC (republicación y carga de `@continuo`) | visto bueno de network para el horizonte de revisión de qn (si venció) y aviso al backend | [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md), D1 (usuario, 2026-11-10) | la carga de `@continuo` sigue aplazada |

Filas en [DEPENDENCIAS.md](../DEPENDENCIAS.md) «Dependencias de tarea».

## 7. GAPs abiertos

- **GAP-BACKLOG_README-03 — Acciones US y cripto por dos publicadores** (abierto, sin prisa: la publicación del universo
  ampliado sigue bloqueada por el visto bueno de network). ¿Referencia del laboratorio por clase de activo, o las dos
  fuentes con su `source`? Opciones: (a) MT5 en FX, metales e índices; Yahoo/Stooq en acciones; cripto de un solo
  origen; (b) las dos fuentes con `source`; (c) sólo MT5. Recomendación: (a), con un subconjunto pequeño duplicado para
  el cuadre. (2026-11-10: el cuadre del FX ya demostró su valor: cruzar yfinance y MT5 destapó el close desfasado de
  yfinance; apoya la opción (a) con duplicado de control.)
- ~~**GAP-DATOS_VIA_QN-01 — Dueño del exportador diario (TI-02-DIARIO)**~~ **RESUELTO (usuario, 2026-11-10, revisión de
  planes, D6):** el laboratorio escribe el código (TI-02-DIARIO) y el backend lo programa en Dagster tras el cierre de
  Nueva York, en su SPRINT-03 (D5). Texto histórico (abierto, nuevo el 2026-11-09): Laboratorio
  (Windows, ya tiene `descarga_lago.py` y el exportador) o backend (Dagster en Linux, junto al publicador OAS). Debe
  decidirse antes de planificar la ola 1 de SPRINT-03 de `quantdesk`. (2026-11-10: sigue abierto en los tres repos:
  GAP-PUB-02 del backend y `quantdesk/docs/plans/DEPENDENCIAS.md`, que exige tarea OAS y exportador cerrados en un
  backend o laboratorio antes de la ola 1; el criterio nuevo (4) de TI-02-DIARIO, FX con `source=mt5`, no cambia la
  disyuntiva.)
- ~~**GAP-DATOS_VIA_QN-02 — TI-02-DATA-V2 como condición previa de SPRINT-02**~~ **RESUELTO (usuario, 2026-11-10,
  revisión de planes, D2):** fila nueva 1b en `next/SPRINT.md` con TI-02-DATA-V2 y la repetición de la tabla FX sobre
  MT5, antes de las filas 2, 4 y 7. Texto histórico (abierto, nuevo el 2026-11-10): La incidencia
  ISSUE-LAGO-FX-1D-CLOSE (destino SPRINT-02) pide repetir la tabla FX del banco sobre el 1d de MT5 «desde qn», y
  `descarga_lago.py` sólo lee v1, que ya no recibe barras. Detalle y opciones en el informe de la revisión.
- ~~**GAP-DATOS_VIA_QN-03 — Republicar las 23 velas 1d del 2026-11-09 y mantener el aplazamiento de la carga nocturna**~~
  **RESUELTO (usuario, 2026-11-10, revisión de planes, D1):** «republicar y aplazar». Ficha urgente
  [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md); se aprueban las 23 republicaciones; la carga nocturna de
  `@continuo` sigue aplazada hasta cerrarla; se verifica el horizonte de revisión de qn y, si venció, se pide la
  excepción a network. Texto histórico (abierto, nuevo el 2026-11-10): decisión de usuario (backend e90eb03: «si el
  usuario lo aprueba»).
- ~~**GAP-DATOS_VIA_QN-04 — Alcance del intradía local**~~ **RESUELTO (usuario, 2026-11-10, revisión de planes, D3b):**
  medir profundidad y volumen m1/m5 de las 484 acciones de `@us_grandes` con `--simular` e incluirlas en INTRA-LOCAL si
  la cifra es razonable (presupuesto 100 GB); se anota en la ficha. Texto histórico (abierto, nuevo el 2026-11-10). La primera descarga m1/m5 cubre
  `@continuo` (193); las 497 acciones de `@us_grandes` no tienen intradía local; si el bróker les aplica el mismo tope de ~100 000 barras, su profundidad también se pierde
  (SIN VERIFICAR: no se ha medido el intradía de acciones).

## Revisión de planes (2026-11-10, parcial)

Veredicto: **ACTUALIZAR** (aplicado) · Motivo: TI-12-MT5 se cerró y SPRINT-01 se archivó después de la revisión de ayer, el
FX diario del lago resultó tener el close desfasado, la tarea programada ya existe y apareció una tarea sin dueño (velas 1d
incompletas). La revisión de ayer de este plan es la división decidida por el usuario en
[README.md](README.md) («Revisión de planes (2026-11-09)»); aquí no hay sección propia de ayer. Sin cambios de
dirección: A16 y A16 bis siguen. · Cambios desde la revisión de 2026-11-09: rutas del dossier de TI-12-MT5 al archivo;
fase C cerrada (cifras de 497 acciones y de 3 descargas); Meta con `-24`; plan nocturno de carga con tope de 40 000
objetos/5 min; tarea programada registrada; INTRA-LOCAL con su primera descarga; tarea nueva TI-12-MT5-SYNC;
TI-02-DATA-V2 y TI-02-DIARIO con selección por `source` y FX con `source=mt5`; GAP-DATOS_VIA_QN-02, -03 y -04.

| Tarea | Clasificación | Evidencia / motivo |
|---|---|---|
| TI-12-MT5 (fase C: código y descargas locales 1d) | HECHO | SPRINT-01 §10 (CERRADA 2026-11-09); `f9dcd0c`, cuadre `fdfa3a7`, cierre `beaf81c`; `../archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/` |
| TI-12-MT5 (fase C: publicar el universo ampliado en qn) | MODIFICADO | Plan nocturno acordado con backend (≤ 40 000 objetos/5 min, 02:00–05:00 CET); noche 1 aplazada por backend `e90eb03`; noche 2 espera a network y al usuario |
| Decisión de Meta Platforms | HECHO | `f9dcd0c` (decisión del usuario 2026-11-09): `META.NAS-24`; `@us_grandes` = 497 |
| TI-12-MT5 (tarea programada) | HECHO (la revisión del token, VIGENTE) | SPRINT-01 §10: la registró el usuario (`quantdesk\publicador_mt5`); activa: SIN VERIFICAR |
| TI-12-MT5-INTRA-LOCAL | VIGENTE (primera descarga hecha; criterios 2 y 4 pendientes) | `ISSUE-TI12-MT5-INTRADIA-LOCAL` §6; `continuo_m1m5_20261109`, 37 944 660 filas |
| TI-12-MT5 (intradía publicado en qn) | VIGENTE (sin cambios) | Se pide al planificar SPRINT-04 |
| TI-12-MT5-SYNC | NUEVA | Backend `e90eb03`; sin commit en este repo (último del publicador: `f9dcd0c`); `nucleo.py::serie` no reenvía revisiones |
| TI-13-PUB (mercado público) | MOVER a quantdesk-backend (confirmado) | Backend `PLAN_PUBLICADORES_MERCADO_PUBLICO` PUB-03/PUB-04 (backlog, sin sprint); `source` por fijar con network |
| TI-02-DATA-V2 | MODIFICADO | Criterios (5) a (7) nuevos; `descarga_lago.py:57` sigue con `market.ohlcv`; `fuentes.py:230` toma `instrument = symbol` |
| TI-02-DIARIO | MODIFICADO | Criterio (4) nuevo; dueño sigue por decidir (backend GAP-PUB-02; `quantdesk/docs/plans/DEPENDENCIAS.md`, línea de SPRINT-03 ola 1) |
| Binance congelado (§5) | VIGENTE (sin cambios) | Decisión del usuario 2026-11-09; el backend PUB-04 no lo toca |

GAPs abiertos al redactar la revisión (todos resueltos después por el usuario: ver «Decisiones del usuario» más abajo):
GAP-DATOS_VIA_QN-02 (TI-02-DATA-V2 como condición previa de SPRINT-02) · GAP-DATOS_VIA_QN-03 (republicar las 23 velas y
mantener aplazada la carga nocturna) · GAP-DATOS_VIA_QN-04 (intradía local de las acciones) · GAP-DATOS_VIA_QN-01 (dueño
del exportador diario). Sigue abierto GAP-BACKLOG_README-03.

Contradicciones registradas (detalle en el informe de la revisión): C-DATOS_VIA_QN-01 (la incidencia dice que su
seguimiento es la fila 2 de `next/SPRINT.md`, y esa fila no incluye repetir la tabla FX sobre MT5) · C-DATOS_VIA_QN-02
(SPRINT-01 §10 programa la noche 1 a las 02:03 del 2026-11-10; el backend la aplazó a las 00:48) · C-DATOS_VIA_QN-03
(descarga incremental en tres sitios: fila 5 de `next/SPRINT.md`, INTRA-LOCAL y TI-12-MT5 cerrada) · C-DATOS_VIA_QN-04
(`backlog/README.md` §2.2 y §3.1 siguen con TI-12-MT5 fase C «en curso en SPRINT-01»).

Sinergias: backend `ISSUE-FX-1D-CLOSE-YFINANCE` (MT5 fuente por defecto del 1d; vela incompleta del 2026-11-09) y
`PLAN_PUBLICADORES_MERCADO_PUBLICO` (PUB-03/PUB-04 usarán `market.ohlcv.v2` con `source` propio: TI-02-DATA-V2 (5) los
absorbe sin cambios); network `PLAN_COPIA_PERIODICA_LAGO` y `PLAN_QN_CACHE` (lecturas grandes de `descarga_lago.py`: avisar
antes, regla del backend del 2026-11-09); `PLAN_TSFM_FINANZAS` (TS-05-FREQ, consumidor del intradía en SPRINT-04) y
quantdesk `PLAN_XVA_BANCARIO` (OAS vía TI-02-DIARIO).

### Decisiones del usuario (2026-11-10, revisión de planes)

Fuente de todas: usuario, 2026-11-10, revisión de planes.

| Decisión | Resuelve | Efecto en este plan |
|---|---|---|
| D1 «Republicar y aplazar» | GAP-DATOS_VIA_QN-03, C-DATOS_VIA_QN-02 | Ficha urgente [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md); modo de reenvío; se aprueban las 23 republicaciones; carga de `@continuo` aplazada hasta cerrarla; verificar el horizonte de revisión de qn (H2, ~6 h) y pedir excepción a network si venció |
| D2 | GAP-DATOS_VIA_QN-02, C-DATOS_VIA_QN-01 | TI-02-DATA-V2 y la repetición de la tabla FX en la fila 1b de `next/SPRINT.md` (SPRINT-02) |
| D3 | C-DATOS_VIA_QN-03 | Incremental de MT5 fuera de sprint en INTRA-LOCAL; la fila 5 de `next/SPRINT.md` queda en «más símbolos y periodos» |
| D3b | GAP-DATOS_VIA_QN-04 | Medir con `--simular` las 484 acciones de `@us_grandes` y decidir con la cifra (presupuesto 100 GB), anotado en la ficha INTRA-LOCAL |
| D6 | GAP-DATOS_VIA_QN-01 | TI-02-DIARIO: el laboratorio escribe el código; el backend lo programa en Dagster tras el cierre de NY, en su SPRINT-03 (D5) |
| Por regla | C-DATOS_VIA_QN-04 | Los derivados del laboratorio (`backlog/README.md`, `index.md`, `issues/index.md`) se ponen al día tras el cierre de SPRINT-01 |

Contradicciones C-DATOS_VIA_QN-01 a -04: todas resueltas. GAPs abiertos que quedan relacionados con este plan:
GAP-BACKLOG_README-03 (dos publicadores en acciones US y cripto).
