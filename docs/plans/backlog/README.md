# Backlog del laboratorio (`quantdesk-model`)

Planes individuales futuros, uno por tema (`PLAN_<TEMA>.md`), sin sprint asignado. Cada plan lleva
estado, estado verificado, opciones, fases o tareas con aceptación verificable, dependencias, riesgos
y preguntas abiertas. `sprint planificar` los refresca contra el código y agrupa sus tareas en
`next/` o en un `future/SPRINT-NN/`; los documentos de visión permanentes (p. ej. `ROADMAP.md`) se
refrescan pero no se fusionan. Listado y estado de cada plan: tablero [index.md](../index.md).

> **Origen:** contenido íntegro de `docs/plans/BACKLOG.md` (2026-11-07), trasladado aquí al instalar los sprints; esa ruta queda como puntero. **Asignación a sprints** (usuario, 2026-11-07): el sprint N del laboratorio es «lo que se puede hacer cuando termine el sprint N de `quantdesk`», salvo SPRINT-01, que es lo que se puede hacer ya. Hoy (2026-11-09): SPRINT-01 **activo** en [current/SPRINT.md](../current/SPRINT.md) (desde el 2026-11-07), SPRINT-02 en [next/SPRINT.md](../next/SPRINT.md), SPRINT-03 y SPRINT-04 en [future/](../future/README.md); dependencias en [DEPENDENCIAS.md](../DEPENDENCIAS.md).

**Fecha:** 2026-11-07; **revisado y dividido el 2026-11-09** (usuario, 2026-11-09; sección final). Este fichero es el
**índice** del backlog del laboratorio, la regla de separación y el calendario **del laboratorio**. Lo que ya está en un
sprint del laboratorio se especifica allí; aquí queda su estado. Lo que no tiene sprint vive en sus planes:

| Plan | Contenido | IDs |
|---|---|---|
| [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) | Archivo de cadenas de opciones desde el lago, sonda de sólo lectura y copia propia tras la herramienta genérica de borrado | TI-09-ARCH (parte laboratorio), TI-09-SONDA |
| [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) | MT5 (universo ampliado, intradía en local y en qn, tarea programada), datos públicos movidos al backend, exportadores (sólo v2 y diario de D-I4), Binance como corpus congelado | TI-12-MT5 (fase C, intradía, INTRA-LOCAL, tarea programada), TI-13-PUB (mercado público), TI-02-DATA-V2, TI-02-DIARIO |

Los planes de diseño (especificación y aceptación de cada ID) viven en el backlog de `quantdesk`
(`S:/projects/quantdesk/docs/plans/backlog/`): [PLAN_TSFM_FINANZAS], [PLAN_TSFM_INTEGRACION], [PLAN_XVA_BANCARIO] y
[PLAN_DEEP_LEARNING_GPU].

## 1. Regla de separación

| Va al backlog de `quantdesk` | Va al backlog del laboratorio (este) |
|---|---|
| Código que se ejecuta en producción: Rust/C++ (`engine-core`, `engine-nn`, `quant-data`, `quant-domain`), FinDSL, contratos, desktop, gates | Adquisición y exportación de datos, datasets congelados con hash, bancos y referencias externas en Python, configuraciones de ejecuciones, informes, fichas de modelo, almacén de artefactos |
| Se planifica y ejecuta en los sprints de `quantdesk`, con sus gates y revisión | No depende de los sprints de `quantdesk` ni de `rust-target`; usa `quantdesk` solo como consumidor (rueda Python, CLI) |
| Los IDs y su especificación siguen en los planes de `quantdesk` | Mismos IDs; aquí se registra su ejecución |

Límites: el laboratorio no escribe código Rust ni modifica `quantdesk`; si una tarea necesita algo del motor que no está
expuesto, se pide como tarea de `quantdesk`. La GPU se usa respetando los carriles de DL-02-GATES cuando existan.

**Publicadores (usuario, 2026-11-09, EXECUTION de SPRINT-01 A16 y A16 bis):** los datos de mercado entran al lago de
`quantdesk-network` (qn) **solo por publicadores**: MT5 desde el Windows del laboratorio; las fuentes públicas en
`quantdesk-backend` (`PLAN_PUBLICADORES_MERCADO_PUBLICO`). **El laboratorio consume siempre vía qn** y exporta a
`engine.market-history/v1`. Excepciones decididas (corpus Chronos, LOTSA y Binance congelado; MT5 1m/5m guardado en
local): texto completo en [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §1.

## 2. Tareas del laboratorio

Estado verificado el 2026-11-09 contra `current/EXECUTION.md`, `STATUS.md` y `git log` del laboratorio, y contra los
registros de `quantdesk-backend` y `quantdesk-network`.

### 2.1 Comprobaciones (2026-11-07)

Histórico; anotado el 2026-11-09 entre paréntesis.

- **HMM desde Python: sí.** `quantdesk.Engine.calibrate(Hmm, ObservedSeries, HmmCalibrationOptions)` calibra con
  Baum-Welch y `Engine.open_stream(res, seed, policy="from_calibration_end").advance_many(dts)` muestrea caminos
  condicionados al final de la calibración. Probado con una serie sintética de 400 días y 200 caminos a 20 días. Un
  camino por stream: para miles de caminos, medir el tiempo antes de pedir una versión vectorizada. (2026-11-09: el banco
  de TS-00-BENCH lo usa con la rueda de `69fdb39d`; no se ha pedido versión vectorizada.)
- **Entorno de `quantdesk` (`venv`, Python 3.12.3):** tiene `pyarrow`, `numpy`, `pandas`, `data_py` y `quantdesk`
  (editable desde `S:/Projects/engine_quant`, que es una unión a `S:/Projects/quantdesk`). Le faltaban `ml_dtypes`,
  `arch`, `torch` y `MetaTrader5`. De ahí LAB-00-ENV. (2026-11-09: **superado**; el laboratorio usa su `.venv` y una rueda
  propia, no el editable; nada se instala en el venv de `quantdesk`.)
- **Scraper de cadenas (`quantdesk-backend`):** yfinance sobre el S&P 500, capturas a las 04, 12 y 20 h de París con
  timeout de 8 h, errores tragados, ninguna captura tras el cierre de EE. UU. y sin precio del subyacente. Plan en el
  backlog del backend (`PLAN_OPTIONS_CHAIN_ARCHIVO`). (2026-11-09: errores y alerta **arreglados** (OC-01, OC-02); el
  primer run real tardó 77 min; la captura al cierre con spot (OC-03) sigue pendiente; la retención la garantizaba network
  (OCS-02), pero la herramienta genérica de borrado decidida el 2026-11-09 la rompe: ver
  [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) §4; OC-05 está cumplida en revisión.)

### 2.2 Pendientes o en curso

| ID | Qué se hace aquí | Cuándo / estado (2026-11-09) | Notas |
|---|---|---|---|
| **TI-09-ARCH**, **TI-09-SONDA** | Archivo de cadenas de opciones y sonda de sólo lectura | Backlog; sonda ya, fuera de sprint | [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) |
| **TI-12-MT5** (fase C, intradía, INTRA-LOCAL, tarea programada), **TI-13-PUB** (mercado público), **TI-02-DATA-V2**, **TI-02-DIARIO** | Datos de mercado vía qn y exportadores | Fase C en SPRINT-01; INTRA-LOCAL ya, fuera de sprint; el resto en backlog o movido al backend | [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) |
| **TS-00-BENCH** | Banco walk-forward: HMM del motor, GARCH(1,1), Chronos-2 y Toto en zero-shot | **SPRINT-01, en curso.** Fase 1 aceptada (`baa4ee6`, 2026-11-09): tabla de cabecera `lago_cierre_c20261101` (proxy declarado), segunda tabla `binance_c20261101`. Fase 2 (Toto, decisión A18): venv aparte `E:/quantdesk-lab/venvs/toto` (`torch==2.7.0` CPU, `toto-ts==0.2.0`), llamado en subproceso; Toto FX terminado (28 pares, 1 400 orígenes, 0 fallos), Toto Binance en curso | Licencias de pesos Chronos-2/Toto y `toto-ts`: Apache-2.0 (informe). Hallazgo: `arch` 8 ignora `random_state`; la semilla entra por `rng`. Ampliaciones en SPRINT-02 (HMM filtrado causal, FG-16-hmmcop) y SPRINT-03 (GPU) |
| **TS-00-OBJ** | Umbrales de éxito con el usuario a la vista del banco | **SPRINT-01, fila 9**, tras TS-00-BENCH; **puerta de usuario** | Se escriben en `PLAN_TSFM_FINANZAS` (GAP-01 de SPRINT-01). **Forma del umbral D-08 decidida (usuario, 2026-11-09; resuelve GAP-TSFM-03): combinada.** El modelo «no pierde claramente» si su CRPS no es peor que el de la referencia en más de un X % **y** gana en colas (pinball 0,01/0,99, Kupiec/Christoffersen) **o** en QLIKE. X se fija en TS-00-OBJ a la vista del banco con Toto. Opciones descartadas: mandan las colas (el CRPS sólo informa); sólo CRPS relativo |
| **TS-02-DISC** (parte laboratorio) | Clasificador real frente a sintético e informe de rasgos que faltan | Tras SPRINT-03 de `quantdesk` (necesita TS-02-GEN, ola 3, condicionada a capacidad) | Planificado en [future/SPRINT-03](../future/SPRINT-03/SPRINT.md) fila 4 |
| Ejecuciones de entrenamiento | Configuraciones `engine.train-request/v1`, escalera 4 M → 20 M → 80 M, ablaciones TS-05-PRE (interferencia y punto de control D-08) y TS-05-FREQ, recibos e informes | Tras SPRINT-04 de `quantdesk` (necesita TI-06-CLI y DL-07-TRAIN) | Planificado en [future/SPRINT-04](../future/SPRINT-04/SPRINT.md). El código de entrenamiento es de `quantdesk`. **TS-05-PREC no es del laboratorio**: es el banco de precisión real en las R9700 dentro de `quantdesk` (PLAN_TSFM_FINANZAS) y es dependencia de TS-05-PRE |
| Adaptadores walk-forward | Ejecuciones trimestrales y mensuales de TS-18-WF; TS-06-FT y TS-15-FINAL | Tras SPRINT-04 de `quantdesk` | Planificado en [future/SPRINT-04](../future/SPRINT-04/SPRINT.md) filas 3–5 |

Ampliaciones ya planificadas en sprints (sólo referencia; la especificación está allí):
[next/SPRINT.md](../next/SPRINT.md) (LAB-00-ENV re-fijado, TS-00-BENCH y TS-00-PREC ampliados, TI-02-DATA con el
universo59, TI-12-MT5 incremental, TI-09-ARCH cobertura, TI-13-PUB: consumir lo que publique el backend) y
[future/SPRINT-03](../future/SPRINT-03/SPRINT.md) (re-exportación con procedencia TI-03-FMT, licencias al ADR,
TS-00-PREC con TS-01-SIM, TS-00-BENCH en GPU).

### 2.3 Hechas (constancia)

| ID | Qué se hizo | Evidencia |
|---|---|---|
| **LAB-00-ENV** | `.venv` propio (Python 3.12.3 de `D:/miniconda312`), `requirements.lock` con hashes (torch 2.15.0+cpu, chronos-forecasting 2.3.2, `arch`, `ml_dtypes`, `MetaTrader5`, `pyarrow`), rueda `quantdesk-0.0.0-cp312` construida desde quantdesk `69fdb39d` (`scripts/build_wheels.py`, `E:/quantdesk-lab/wheels/SHA256SUMS`), cachés en `E:/quantdesk-lab/` | CERRADA el 2026-11-08 (`a581355`, `33e91fd`, `6b5ac1e`, `a9a7223`; cierre `ee7454e`); STATUS «Entorno» |
| **TI-01-INV** | Inventario de todos los topics `market.*` del lago (`scripts/inventario_options_chain.py`) | CERRADA el 2026-11-08 (`f8f53ad`…`cb46ce2`; cierre `e8df2f8`); `current/execution/TI-01-INV/`. Hallazgos: 28 cruces FX diarios desde 2024-11; tipos y rendimientos desde 2025-12 con hueco 2026-04…09; cadenas vacías (a esa fecha); la flota de qn no tiene GPU |
| **TI-13-PUB** (corpus genéricos) | Corpus con licencia (Chronos, LOTSA) y Binance; filtro de fugas D-11 (corte provisional 2016-10-01), train/val disjuntos | CERRADA el 2026-11-08 (`7ea6d94`); 36 datasets, 1,0 GB en `E:/quantdesk-lab/datasets/TI-13-PUB/`; `current/execution/TI-13-PUB/` (licencias, filtro). Binance se ingirió directamente, antes de A16; queda como corpus congelado con hash (usuario, 2026-11-09; [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §5) |
| **TI-02-DATA** | Exportador a `engine.market-history/v1` (`scripts/exportar_market_history.py`) | CERRADA el 2026-11-09 (`906f73e`, revisión 2 ACEPTAR); cuatro datasets en `E:/quantdesk-lab/datasets/TI-02-DATA/` (`binance_c20261101`, `lago_c20261101`, `lago_cierre_c20261101` proxy con `default_lag_ms`, `lago_c20261107`), hash reproducible y 0 violaciones de look-ahead. La procedencia va en `procedencia.json` adjunto hasta TI-03-FMT. `descarga_lago.py` aún lee v1: TI-02-DATA-V2 |
| **TI-02-DATA-DEUDA** | Tres arreglos BAJA de la revisión 2: prueba de la guardia de `default_lag_ms`; CRLF→LF antes de hashear el código; «mayor cambio de close» sólo entre versiones cerradas | CERRADA el 2026-11-09 (`0e67465`); los cuatro `dataset_hash` no cambian |
| **TS-00-PREC** | Banco de precisión emulado (fp8 e4m3/e5m2, bf16, f16, f32 en CPU) | CERRADA el 2026-11-08 (`5afc795`); hash `83548e1a…` reproducido por la raíz. fp8 basta para la entrada, no para la inferencia emulada ni para σ_loc; bf16/f16/f32 no pierden. Ya consumido por PLAN_DEEP_LEARNING_GPU (DL-08-QUANT) |
| **TI-12-MT5** (fases A y B) | Extractor de sólo lectura (lista blanca, hora del servidor a UTC `ny+7`, descarga reanudable con hash estable) y **publicador MT5 → qn `market.ohlcv.v2`** con relleno de huecos, candado, `--simular` y tarea XML; 1d con `ts` a las 00:00 UTC del día de sesión (como yfinance) | Fase A `7d38136`; fase B `a495e5f`, `90fa001`, `45a93ce`, `9ed66d4`, `1ed4dfd`, `558baee`, `773965e`; **primera publicación real** `9b74bed` (28 series fx28, 178 522 barras 1d, idempotente). Backend ya lee v2 (`source=mt5` en ClickHouse `fx_spot_1d` y `/api/fxspot?source=mt5`); network `PLAN_OHLCV_V2_CORTE` |

## 3. Calendario del laboratorio

«L» = este laboratorio. Las asignaciones a SPRINT-04 y posteriores son estimaciones por dependencias; se recalibran al
planificar cada sprint. **Las tareas de `quantdesk` («Q») no se copian aquí** (usuario, 2026-11-09; C-26): su fuente de
verdad es el alcance de SPRINT-03 en
[`quantdesk/docs/plans/next/README.md`](S:/projects/quantdesk/docs/plans/next/README.md) y sus planes de diseño. La
copia que había hasta el 2026-11-09 queda en la historia de git (`git show 8a849c6:docs/plans/backlog/README.md`, §3).

### 3.1 Ahora (en paralelo a SPRINT-02 de `quantdesk`, activo desde el 2026-10-23; sin tocar `quantdesk`)

- **L (SPRINT-01):** hechas LAB-00-ENV, TI-01-INV, TI-13-PUB (corpus), TI-02-DATA, TI-02-DATA-DEUDA y TS-00-PREC; en curso
  TI-12-MT5 (fase C) y TS-00-BENCH (Toto); queda TS-00-OBJ. TI-09-ARCH fuera del sprint (GAP-BACKLOG_README-01).
- **L (fuera de sprint, ya):** TI-09-SONDA (puerta de usuario: token de lectura) y TI-12-MT5-INTRA-LOCAL (1m y 5m en
  local con hash); fichas en [issues/](../issues/index.md).
- **Backend (`quantdesk-backend`, su propio sprint):** OC-01 y OC-02 hechas (su SPRINT-01); OC-03 y OC-04 en su SPRINT-02.
  Corte a `market.ohlcv.v2` hecho (2026-11-09). Publicadores de fuentes públicas: plan nuevo
  `PLAN_PUBLICADORES_MERCADO_PUBLICO` (usuario, 2026-11-09).
- **Network:** OCS-01/OCS-02 cerradas; `market.ohlcv.v2` registrado. Pendiente su visto bueno para el universo ampliado
  de MT5; el intradía se le pide al planificar SPRINT-04. Herramienta genérica de borrado en el lago (rompe 12-A).
- **Usuario:** registrar la tarea programada del publicador MT5; TS-00-OBJ (fijar X del umbral D-08); reiniciar la
  máquina antes de la ola 2 de SPRINT-03 de `quantdesk`.

### 3.2 Cuando termine SPRINT-02 de `quantdesk` (= SPRINT-02 del laboratorio)

- **L ([next/SPRINT.md](../next/SPRINT.md)):** rueda re-fijada, HMM causal, ampliaciones; TI-13-PUB consume lo que
  publique el backend.
- **Antes de la ola 1 de SPRINT-03 de `quantdesk`:** exportador diario TI-02-DIARIO (dueño por decidir) con los OAS
  para XVA.
- Nota (2026-11-09): desde el 2026-11-06 las GPU están en pruebas de rendimiento y la IA local en pausa; el deep learning
  nativo va por Rust/Burn con GPU obligatoria en `engine-nn`. El uso de GPU del laboratorio (zero-shot con PyTorch-ROCm)
  depende de que esa pausa termine (GAP-BACKLOG_README-05).

### 3.3 Cuando termine SPRINT-03 de `quantdesk` (= SPRINT-03 del laboratorio)

- **L:** TS-02-DISC; re-exportación con procedencia TI-03-FMT ([future/SPRINT-03](../future/SPRINT-03/SPRINT.md)).

### 3.4 Cuando termine SPRINT-04 de `quantdesk` (= SPRINT-04 del laboratorio en adelante)

- **L:** ejecuciones de la escalera (TS-05-PRE con la prueba de interferencia y el punto de control frente a modelos
  públicos en 20 M), TS-05-FREQ (necesita el intradía de MT5 en qn: se pide al planificar SPRINT-04), TS-06-FT,
  adaptadores de TS-18-WF, TS-15-FINAL.
- **Usuario:** D-13 (pagar datos de mercado y CDS) cuando el dato real sea el cuello de botella.

## 4. Dependencias externas

Por plan: [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) §5 y [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §6;
contrato para `sprint deps` en [DEPENDENCIAS.md](../DEPENDENCIAS.md). Ampliaciones de SPRINT-02/03/04: cierre de los
sprints de `quantdesk` (decidido, usuario, 2026-11-07).

## Revisión de planes (2026-11-09)

Veredicto: **ACTUALIZAR + DIVIDIR**, **aplicado** el 2026-11-09 por decisión del usuario (GAP-BACKLOG_README-06 opción
(a); opción descartada: mantener un solo fichero). Motivo: de las 14 filas (17 al separar TI-12-MT5 y TI-13-PUB por
partes), 8 están hechas, 6 ya viven en un sprint del laboratorio y sólo 3 frentes no tienen sprint (TI-09-ARCH, MT5 en
qn más allá del 1d y los datos públicos de mercado). La tabla mezclaba horizontes y copiaba el calendario de
`quantdesk`. Resultado: este README queda como índice, regla y calendario del laboratorio (las listas «Q» se sustituyen
por un enlace); [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) recoge TI-09-ARCH; [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md)
recoge MT5, publicadores, exportadores y Binance. La ruta de este fichero y el ancla `#21-comprobaciones-2026-11-07`
se conservan (las enlazan `BACKLOG.md`, `current/SPRINT.md`, `quantdesk/next/README.md` y `PLAN_TSFM_INTEGRACION`).

| Tarea | Clasificación | Evidencia / motivo |
|---|---|---|
| LAB-00-ENV | HECHO | `a581355`, `33e91fd`, `6b5ac1e`, `a9a7223`; cierre `ee7454e` (2026-11-08); rueda de quantdesk `69fdb39d`. Re-fijado en next/SPRINT fila 1 (DUPLICADO allí) |
| TI-01-INV | HECHO | `f8f53ad`…`cb46ce2`, cierre `e8df2f8`; `current/execution/TI-01-INV/informe.md` |
| TI-09-ARCH (parte laboratorio) | MODIFICADO | Texto alineado con la decisión 12-A (lector bajo demanda, sin copia diaria; la fila decía «instantánea diaria con alerta»); condición de vuelta cumplida: cadenas en qn desde el 2026-11-09 (backend EXECUTION, run 03:00–04:17 UTC, cobertura 0,998), OC-01/02 hechas, OC-05 cumplida; alerta reutilizable del backend; aceptación hecha ejecutable. Movida a PLAN_ARCHIVO_OPCIONES |
| TI-12-MT5 (extractor, fases A/B) | HECHO | `7d38136`; publicador `a495e5f`…`773965e`; primera publicación `9b74bed` |
| TI-12-MT5 (publicador, fila A16) | HECHO salvo puerta de usuario | `9b74bed`, idempotente; falta que el usuario registre la tarea programada |
| TI-12-MT5 (fase C) | VIGENTE (en curso en SPRINT-01) | `9e9dfe5`; descarga local 1d del continuo; publicar en qn espera a network y backend |
| TI-12-MT5 (intradía 1h/5m/1m) | MODIFICADO | Usuario «Solo 1d» (2026-11-09) y condición de network; sale de «Ya» a backlog condicionado; consumidor TS-05-FREQ. Movida a PLAN_DATOS_VIA_QN |
| TI-13-PUB (corpus genéricos) | HECHO | `7ea6d94`; 36 datasets, licencias y filtro D-11 |
| TI-13-PUB (Yahoo/Stooq, FRED, cripto) | MOVER a quantdesk-backend | Decisión A16 bis (2026-11-09); plan dueño `PLAN_PUBLICADORES_MERCADO_PUBLICO` (usuario, 2026-11-09) |
| TI-02-DATA | HECHO | `906f73e`; ampliaciones en next/SPRINT fila 4 y future/SPRINT-03 fila 1 (DUPLICADO allí) |
| TI-02-DATA-DEUDA | HECHO | `0e67465` |
| TS-00-PREC | HECHO | `5afc795`; la nota «`ml_dtypes` no está instalado» era OBSOLETA (está en el lock); ampliaciones en next y future/SPRINT-03 |
| TS-00-BENCH | VIGENTE (en curso en SPRINT-01) | Fase 1 `baa4ee6`; Toto en venv aparte (A18), en curso; la nota «Toto con `torch` en CPU en el `.venv`» queda MODIFICADA |
| TS-00-OBJ | DUPLICADO (current/SPRINT.md fila 9) | Puerta de usuario tras TS-00-BENCH |
| TS-02-DISC (parte laboratorio) | DUPLICADO (future/SPRINT-03 fila 4) | Depende de TS-02-GEN (ola 3 de quantdesk, condicionada) |
| Ejecuciones de entrenamiento | DUPLICADO (future/SPRINT-04) y MODIFICADO | Quitado TS-05-PREC de las ablaciones del laboratorio: es tarea de `quantdesk` (PLAN_TSFM_FINANZAS; future/SPRINT-04 §4 ya lo excluye) |
| Adaptadores walk-forward | DUPLICADO (future/SPRINT-04 filas 3–5) | — |

GAPs:
- GAP-BACKLOG_README-01 **abierto** (vuelta de TI-09-ARCH): ver [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) §6.
- ~~GAP-BACKLOG_README-02~~ **resuelto (usuario, 2026-11-09):** plan nuevo en el backend `PLAN_PUBLICADORES_MERCADO_PUBLICO`, FRED común con F1 de FUENTES.
- GAP-BACKLOG_README-03 **abierto** (dos publicadores en acciones US y cripto): ver [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §7.
- ~~GAP-BACKLOG_README-04~~ **resuelto (usuario, 2026-11-09):** 1m y 5m de MT5 en local ya, con hash; publicar en qn al planificar SPRINT-04.
- GAP-BACKLOG_README-05 **abierto, diferido** (GPU para Chronos-2/Toto): CPU mientras dure la pausa de las GPU; se reevalúa al planificar SPRINT-03 del laboratorio.
- ~~GAP-BACKLOG_README-06~~ **resuelto (usuario, 2026-11-09):** dividir en tres y enlazar el calendario «Q».
- Nuevos: GAP-ARCHIVO_OPCIONES-01 (forma de la copia propia) y GAP-DATOS_VIA_QN-01 (dueño del exportador diario).

Contradicciones:
- ~~C-BACKLOG_README-01~~ (= C-07, cadenas «vacías» frente a «publicando») → sonda de sólo lectura TI-09-SONDA (usuario, 2026-11-09).
- ~~C-BACKLOG_README-02~~ (= C-09, Binance directo frente a A16) → corpus congelado con hash (usuario, 2026-11-09).
- ~~C-BACKLOG_README-03~~ (= C-10, next/SPRINT fila 7) → «consumir y exportar lo que publique el backend» (usuario, 2026-11-09; aplicado en `next/SPRINT.md`).
- ~~C-BACKLOG_README-04~~ (= C-27, dependencias servidas como abiertas) → `DEPENDENCIAS.md` actualizado el 2026-11-09; la fila 1 de `next/SPRINT.md` («en lugar del editable») se corrige al planificar SPRINT-02.
- ~~C-BACKLOG_README-05~~ (= C-26, calendario «Q» copiado) → enlace (usuario, 2026-11-09).
- C-12 (exportador lee v1) → sólo v2, TI-02-DATA-V2 (usuario, 2026-11-09). C-13 (borrado en el lago) → herramienta genérica; el laboratorio planifica copia propia (usuario, 2026-11-09).

Sinergias: backend `PLAN_OPTIONS_CHAIN_ARCHIVO` (OC-03 es el cambio de modo de TI-09-ARCH; `OptionsChainSnapshotMissing`
sustituye la alerta del laboratorio); backend `PLAN_PUBLICADORES_MERCADO_PUBLICO` (TI-13-PUB, OAS) y
`PLAN_FUENTES_OFICIALES_CURVAS` (FRED común; el publicador MT5 es candidato intradía de su F3); network
`PLAN_COPIA_PERIODICA_LAGO` y `docs/lake/RETENCION.md` (copia y retención del lago); network `PLAN_QN_CACHE` (caché de
lecturas que usarían `descarga_lago.py` y el exportador); `PLAN_TSFM_FINANZAS` (GAP-TSFM-02/-04 van con
GAP-BACKLOG_README-01/-04; TS-00-OBJ escribe allí); `PLAN_DEEP_LEARNING_GPU` (DL-08-QUANT ya consume TS-00-PREC);
`PLAN_XVA_BANCARIO` (OAS por el exportador diario; D-13). Sin dependencia de `PLAN_RETIRADA_EXCEL`.

[PLAN_TSFM_FINANZAS]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md
[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
[PLAN_XVA_BANCARIO]: S:/projects/quantdesk/docs/plans/backlog/PLAN_XVA_BANCARIO.md
[PLAN_DEEP_LEARNING_GPU]: S:/projects/quantdesk/docs/plans/backlog/PLAN_DEEP_LEARNING_GPU.md
