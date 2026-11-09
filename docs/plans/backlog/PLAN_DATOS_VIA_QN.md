# Plan — Datos de mercado vía qn (MT5, publicadores públicos, exportadores)

> **Origen:** división de [backlog/README.md](README.md) (regla de publicadores de §1, filas TI-12-MT5 y TI-13-PUB de
> §2.2, filas TI-12-MT5 y TI-13-PUB de §4), en la versión del árbol revisada el 2026-11-09 sobre el commit `8a849c6`.
> División decidida por el usuario el 2026-11-09 (revisión de planes, GAP-BACKLOG_README-06 opción (a)). Texto de la
> especificación copiado íntegro; lo nuevo va marcado «(usuario, 2026-11-09)».

**Estado:** backlog. Lo que ya está en un sprint del laboratorio se especifica allí; aquí queda su estado, lo que no
tiene sprint y lo que espera a otros proyectos. **Fecha:** 2026-11-09.

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
| **TI-12-MT5** (fase C) | Universo ampliado en 1d: continuo (forex 60, metales y energía 16, índices 23, cripto 94) y acciones US grandes (`@us_grandes`, S&P 500 de sesión normal, 484); universos con nombre, vela 1d por clase, huecos por clase y ritmo de publicación | **SPRINT-01, en curso** (intento BDD 131; último commit `9e9dfe5`). Descarga local 1d del continuo hecha (193 series, 547 226 filas, `E:/quantdesk-lab/data/mt5/continuo_1d_20261109`, `sha256:a503bb75…`). **Publicar en qn el universo ampliado** espera el visto bueno de network **y** del backend (carga histórica grande; el Bento del backend aguanta ~180 000 objetos por sondeo de 5 min) | Detalle en `current/execution/TI-12-MT5/fase-c.md`. Decisión pendiente del autor: Meta Platforms sólo existe como `-24` en el bróker. Solapa con los publicadores públicos del backend en acciones US y cripto (GAP-BACKLOG_README-03) |
| **TI-12-MT5** (intradía) | 1h, 5m, 1m (y ticks si hay) del publicador MT5 en `market.ohlcv.v2` | **Backlog, condicionada** (usuario, 2026-11-09: «Solo 1d»). No se lanza sin el visto bueno previo de `quantdesk-network` (ritmo, memoria de mini ~2,17 de 3 GiB, ~9 500 particiones diarias ya creadas por el 1d) y aviso al backend (cada republicación completa ~1,4 GiB y ~4 min de CPU en mini). **Decisión (usuario, 2026-11-09): guardar 1m y 5m en local ya, con hash; la publicación en qn se pide al planificar SPRINT-04 del laboratorio** (GAP-BACKLOG_README-04 resuelto) | El código ya lo soporta (`--intervalos`); `--simular` real dio 1h 2,80 M, 5m 0,17 M, 1m 0,83 M barras en fx28 (m1 sólo desde 2025-11 por `maxbars`). Consumidor: TS-05-FREQ (SPRINT-04 del laboratorio); ver GAP-TSFM-04 de PLAN_TSFM_FINANZAS |
| **TI-12-MT5-INTRA-LOCAL** (usuario, 2026-11-09) | Descarga local periódica de 1m y 5m del universo que el bróker sirva (como mínimo fx28), con el extractor de sólo lectura (`scripts/extractor_mt5.py`), a `E:/quantdesk-lab/data/mt5/`, **sin publicar en qn** | **Ya, fuera de sprint** (historia irrecuperable: el bróker sólo da ~100 000 barras y m1 llega hoy sólo a 2025-11). Ficha viva: [ISSUE-TI12-MT5-INTRADIA-LOCAL](../issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md) | **Aceptación:** (1) dos descargas del mismo rango dan el mismo SHA-256; (2) la descarga es reanudable y la siguiente sólo añade barras nuevas (sin huecos entre la última barra guardada y la primera nueva, salvo fines de semana y festivos del bróker); (3) manifiesto con símbolo, periodo, primera y última barra, filas y hash; (4) periodicidad que no pierda barras por `maxbars` (para m1, menos de ~100 000 barras entre descargas); (5) nada se publica en qn ni se envía ninguna orden. Contradice «consume vía qn» sólo en el almacenamiento, no en el consumo: TS-05-FREQ leerá de qn cuando se publique |
| **TI-12-MT5** (tarea programada) | Registrar `scripts/publicador_mt5_tarea.xml` en el Programador de tareas (cada 15 min y al iniciar sesión, `--intervalos 1d`, relleno de huecos desde lo que qn confirma) | **Puerta de usuario**: la registra él (`schtasks /Create /XML scripts\publicador_mt5_tarea.xml /TN …`) | Token de larga vida `ti12mt5-publicacion-20261109` (id 36, `pub:`/`sub:` sobre `market.ohlcv.v2`, `env=main`) en `E:/quantdesk-lab/secrets/qn-mt5.token`; se revisa al cerrar SPRINT-01 |

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
| **TI-02-DATA-V2** (usuario, 2026-11-09) | `scripts/descarga_lago.py` lee **sólo** `market.ohlcv.v2` (hoy `TOPICS_DEFECTO` en la línea 57 lee `market.ohlcv`, v1, congelado desde el corte a v2 del 2026-11-09); quita v1 de los topics por defecto y del código | (1) Un dataset nuevo con corte posterior al 2026-11-09 contiene las barras de v2 de esas fechas (no se congela en silencio); (2) selftest en verde con un caso que falla si el topic por defecto vuelve a v1; (3) mismas garantías de hash y look-ahead de TI-02-DATA; (4) el informe dice que los cuatro datasets de TI-02-DATA (`binance_c20261101`, `lago_c20261101`, `lago_cierre_c20261101`, `lago_c20261107`) **se regeneran desde la versión anterior del script en git** (`git show 0e67465:scripts/descarga_lago.py`, último commit que lee v1), no desde el nuevo | Backlog. Resuelve **C-12** y la urgencia **U5** de la revisión (exportaciones congeladas en silencio). Opciones descartadas: v2 por defecto con v1 para reproducir hashes; selección a mano |
| **TI-02-DIARIO** (D-I4, usuario, 2026-11-09) | **Exportador diario** que escribe desde qn el mercado del día y los datasets que `quantdesk` ya abre (incluidos los OAS para XVA), para que el motor no dependa de qn ni use tokens | (1) Cada día hábil deja en la ruta que abre `quantdesk` el mercado del día y los datasets con hash; (2) un día sin datos en qn produce un aviso, no un fichero vacío; (3) `quantdesk` no importa ningún cliente de qn ni lee tokens | Backlog. **Dueño por decidir** (laboratorio o backend; GAP-DATOS_VIA_QN-01). Debe existir antes de la ola 1 de SPRINT-03 de `quantdesk` (decisión «Publicador OAS ya», usuario, 2026-11-09). Resuelve D-I4 (GAP-TSFM_INTEGRACION-04): descartado que `quantdesk` lea qn directamente |

## 5. Binance ingerido directamente (C-09 / C-BACKLOG_README-02)

**Decisión (usuario, 2026-11-09): corpus congelado con hash**, excepción a A16 bis como Chronos y LOTSA. El dataset
`binance_c20261101` (TI-13-PUB `7ea6d94`, segunda tabla de TS-00-BENCH `baa4ee6`) no se rehace; lo nuevo de cripto
llegará por qn cuando exista el publicador del backend. Opciones descartadas: rehacerlo desde qn (cambian hashes y la
tabla del banco); retirar Binance del banco.

## 6. Dependencias externas (2026-11-09)

| Tarea local | Depende de | Estado | Mientras tanto |
|---|---|---|---|
| TI-12-MT5 fase C (publicar en qn) e intradía (publicar) | visto bueno de `quantdesk-network` (ritmo, compactación) y aviso a `quantdesk-backend` (carga del Bento) | fase C: por pedir cuando se quiera publicar; intradía: se pide al planificar SPRINT-04 del laboratorio (usuario, 2026-11-09) | descarga local en `E:/quantdesk-lab/data/mt5/` (TI-12-MT5-INTRA-LOCAL para 1m y 5m) |
| TI-13-PUB (mercado público) y TI-02-DATA ampliada (next/SPRINT fila 7) | `quantdesk-backend` `PLAN_PUBLICADORES_MERCADO_PUBLICO` (backlog, sin sprint) | decidido (usuario, 2026-11-09) | Binance congelado de TI-13-PUB; FX diario de qn |
| TI-02-DIARIO | dueño por decidir; OAS del publicador del backend | decidido el mecanismo (usuario, 2026-11-09) | — |

Filas en [DEPENDENCIAS.md](../DEPENDENCIAS.md) «Dependencias de tarea».

## 7. GAPs abiertos

- **GAP-BACKLOG_README-03 — Acciones US y cripto por dos publicadores** (abierto, sin prisa: la publicación del universo
  ampliado sigue bloqueada por el visto bueno de network). ¿Referencia del laboratorio por clase de activo, o las dos
  fuentes con su `source`? Opciones: (a) MT5 en FX, metales e índices; Yahoo/Stooq en acciones; cripto de un solo
  origen; (b) las dos fuentes con `source`; (c) sólo MT5. Recomendación: (a), con un subconjunto pequeño duplicado para
  el cuadre.
- **GAP-DATOS_VIA_QN-01 — Dueño del exportador diario (TI-02-DIARIO)** (abierto, nuevo el 2026-11-09). Laboratorio
  (Windows, ya tiene `descarga_lago.py` y el exportador) o backend (Dagster en Linux, junto al publicador OAS). Debe
  decidirse antes de planificar la ola 1 de SPRINT-03 de `quantdesk`.
