# Backlog del laboratorio (`quantdesk-model`)

Planes individuales futuros, uno por tema (`PLAN_<TEMA>.md`), sin sprint asignado. Cada plan lleva
estado, estado verificado, opciones, fases o tareas con aceptación verificable, dependencias, riesgos
y preguntas abiertas. `sprint planificar` los refresca contra el código y agrupa sus tareas en
`next/` o en un `future/SPRINT-NN/`; los documentos de visión permanentes (p. ej. `ROADMAP.md`) se
refrescan pero no se fusionan. Listado y estado de cada plan: tablero [index.md](../index.md).

> **Origen:** contenido íntegro de `docs/plans/BACKLOG.md` (2026-11-07), trasladado aquí al instalar los sprints; esa ruta queda como puntero. **Asignación a sprints** (usuario, 2026-11-07): el sprint N del laboratorio es «lo que se puede hacer cuando termine el sprint N de `quantdesk`», salvo SPRINT-01, que es lo que se puede hacer ya. Hoy (2026-11-09): SPRINT-01 **cerrado** (2026-11-07 a 2026-11-09) y archivado en [archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md), SPRINT-02 en [next/SPRINT.md](../next/SPRINT.md), SPRINT-03 y SPRINT-04 en [future/](../future/README.md); dependencias en [DEPENDENCIAS.md](../DEPENDENCIAS.md).

**Fecha:** 2026-11-07; **revisado y dividido el 2026-11-09** (usuario, 2026-11-09; primera sección final); **puesto al
día el 2026-11-10** tras el cierre de SPRINT-01 (segunda sección final), con las decisiones del usuario del mismo día
aplicadas (tercera sección final). Este fichero es el
**índice** del backlog del laboratorio, la regla de separación y el calendario **del laboratorio**. Lo que ya está en un
sprint del laboratorio se especifica allí; aquí queda su estado. Lo que no tiene sprint vive en sus planes:

| Plan | Contenido | IDs |
|---|---|---|
| [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) | Archivo de cadenas de opciones desde el lago, sonda de sólo lectura y retención (sin copia propia: la copia es la común de network; usuario, 2026-11-10) | TI-09-ARCH (parte laboratorio), TI-09-SONDA |
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

Estado verificado el 2026-11-10 (01:00) contra el archivo de SPRINT-01
([archive/SPRINT-01_2026-11-07_2026-11-09/](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md): `SPRINT.md` §10 y
`EXECUTION.md`), `STATUS.md`, las fichas de [issues/](../issues/index.md) y `git log` del laboratorio, y contra los
registros de `quantdesk-backend` y `quantdesk-network`. No hay sprint activo: `current/` está vacío desde el cierre.

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

| ID | Qué se hace aquí | Cuándo / estado (2026-11-10) | Notas |
|---|---|---|---|
| **TI-09-ARCH**, **TI-09-SONDA** | Archivo de cadenas de opciones y sonda de sólo lectura | Backlog; sonda ya, fuera de sprint | [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) |
| **TI-12-MT5** (publicar el universo ampliado, intradía, INTRA-LOCAL), **TI-13-PUB** (mercado público), **TI-02-DATA-V2**, **TI-02-DIARIO** | Datos de mercado vía qn y exportadores | La fase C (1d local) y el cuadre están **cerrados** (§2.3). Publicar `@continuo` en qn: **aplazado** (la noche 1 de las 02:03 del 2026-11-10 no sale mientras no se cierre [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md); usuario, 2026-11-10, D1). INTRA-LOCAL ya, fuera de sprint, con la primera descarga hecha y el incremental incluido (D3); TI-02-DATA-V2 en SPRINT-02 (fila 1b, D2); TI-02-DIARIO: el laboratorio escribe y el backend programa (D6); el resto en backlog o movido al backend | [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md). Publicador 1d de fx28: tarea programada **registrada por el usuario** (`quantdesk\publicador_mt5`, `6c02490`) |
| **Repetir el banco FX sobre el 1d de MT5** | La tabla de cabecera de TS-00-BENCH usa un close de yfinance que es el precio de las 00:00 UTC; hay que repetirla sobre `source=mt5` y revisar los umbrales de TS-00-OBJ si cambia la conclusión | **Abierta, en SPRINT-02 fila 1b de [next/SPRINT.md](../next/SPRINT.md)** (usuario, 2026-11-10, revisión de planes, D2; GAP-BACKLOG_README-07 resuelto) ([ISSUE-LAGO-FX-1D-CLOSE](../current/issues/ISSUE-LAGO-FX-1D-CLOSE.md)). El backend dejó MT5 como fuente por defecto del 1d (`6425e29`, desplegado) y **no corrige el 1d de yfinance en el lago**. Necesita que el exportador filtre `source=mt5`, y `descarga_lago.py` sólo lee v1 (`TOPICS_DEFECTO`, línea 57), donde MT5 no está: **TI-02-DATA-V2 va en la misma fila 1b**, de la que dependen las filas 2, 4 y 7. La tabla se repite en dos tablas (D15): cabecera con la ventana de hoy y ampliación desde 2000 | La ficha ya remite a la fila 1b (C-BACKLOG_README-08 resuelta). La vela 1d de MT5 del 2026-11-09 está incompleta en 23 de 28 pares (aviso del backend `e90eb03`, 00:48): excluirla hasta la republicación ([ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md); GAP-BACKLOG_README-08 resuelto, D1) |
| **TS-00-BENCH** (ampliaciones) | HMM filtrado causal y corpus FG-16-hmmcop (SPRINT-03, fila S02-2), **FinCast** como cuarto modelo público (SPRINT-02 fila 2b, pedido del usuario el 2026-11-09, `84dafed`; sólo CRPS y QLIKE en la ventana limpia, nunca en colas: D13, usuario, 2026-11-10), GPU (SPRINT-03) | El banco base está **CERRADO** (§2.3). FinCast en SPRINT-02 (activo); HMM causal y FG-16-hmmcop esperan al cierre de `quantdesk` SPRINT-02 (SPRINT-03) | Licencias de pesos Chronos-2/Toto y `toto-ts`: Apache-2.0 (informe). Hallazgo: `arch` 8 ignora `random_state`; la semilla entra por `rng`. FinCast en CPU cuesta unas 7 veces Toto: GPU si DL-02-GATES la habilita (GAP-BACKLOG_README-05) |
| **TS-02-DISC** (parte laboratorio) | Clasificador real frente a sintético e informe de rasgos que faltan | Tras SPRINT-03 de `quantdesk` (necesita TS-02-GEN, ola 3, condicionada a capacidad) | Planificado en [future/SPRINT-03](../next/SPRINT.md) fila 4 |
| Ejecuciones de entrenamiento | Configuraciones `engine.train-request/v1`, escalera 4 M → 20 M → 80 M, ablaciones TS-05-PRE (interferencia y punto de control D-08) y TS-05-FREQ, recibos e informes | Tras SPRINT-04 de `quantdesk` (necesita TI-06-CLI y DL-07-TRAIN) | Planificado en [future/SPRINT-04](../future/SPRINT-04/SPRINT.md). El código de entrenamiento es de `quantdesk`. **TS-05-PREC no es del laboratorio**: es el banco de precisión real en las R9700 dentro de `quantdesk` (PLAN_TSFM_FINANZAS) y es dependencia de TS-05-PRE |
| Adaptadores walk-forward | Ejecuciones trimestrales y mensuales de TS-18-WF; TS-06-FT y TS-15-FINAL | Tras SPRINT-04 de `quantdesk` | Planificado en [future/SPRINT-04](../future/SPRINT-04/SPRINT.md) filas 3–5 |

Ampliaciones ya planificadas en sprints (sólo referencia; la especificación está allí):
[current/SPRINT.md](../current/SPRINT.md) (SPRINT-02, activo desde el 2026-11-11: FinCast en el banco
(fila 2b), TI-12-MT5 (más símbolos y periodos; el incremental ya es de INTRA-LOCAL, D3), TI-09-ARCH
cobertura, TI-13-PUB: consumir lo que publique el backend; **fila 1b nueva** para TI-02-DATA-V2 y la repetición del banco
FX sobre MT5, D2) y
[next/SPRINT.md](../next/SPRINT.md) (SPRINT-03: filas S02-1…S02-4 recibidas de SPRINT-02 el 2026-11-11, LAB-00-ENV re-fijado, TS-00-BENCH y TS-00-PREC con HMM causal y FG-16-hmmcop, TI-02-DATA con el universo59; re-exportación con procedencia TI-03-FMT, licencias al ADR,
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
| **TI-12-MT5** (fases A y B) | Extractor de sólo lectura (lista blanca, hora del servidor a UTC `ny+7`, descarga reanudable con hash estable) y **publicador MT5 → qn `market.ohlcv.v2`** con relleno de huecos, candado, `--simular` y tarea XML; 1d con `ts` a las 00:00 UTC del día de sesión (como yfinance) | Fase A `7d38136`; fase B `a495e5f`, `90fa001`, `45a93ce`, `9ed66d4`, `1ed4dfd`, `558baee`, `773965e`; **primera publicación real** `9b74bed` (28 series fx28, 178 522 barras 1d, idempotente). Backend ya lee v2 (`source=mt5` en ClickHouse `fx_spot_1d` y `/api/fxspot?source=mt5`, **fuente por defecto del 1d** desde backend `6425e29`); network `PLAN_OHLCV_V2_CORTE`. Tarea programada del publicador registrada por el usuario (`4cd1237`, `6c02490`) |
| **TI-12-MT5** (fase C y cuadre) | Universos con nombre, 1d local por clase de activo (continuo de 193 series; acciones US: 484 de sesión normal y 13 `-24`), huecos por clase y ritmo de publicación; cuadre del 1m agregado a diario contra el D1 de MT5 y contra el FX diario del lago | CERRADA el 2026-11-09 (`9e9dfe5`, `f9dcd0c`, `fdfa3a7`; cierre `beaf81c`). 1d local: `continuo_1d_20261109` `sha256:a503bb75…`, `us_grandes_1d_20261109` `sha256:6d9e0528…`, `us_grandes24_1d_20261109` `sha256:1e58cb0a…`; m1 de fx28 `fx28_m1_20261109` `sha256:8a6fa0dc…`, cuadrado exacto con el D1 de MT5 | `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/` (`fase-c.md`, `cuadre.md`). El cuadre reveló [ISSUE-LAGO-FX-1D-CLOSE](../current/issues/ISSUE-LAGO-FX-1D-CLOSE.md) |
| **TS-00-BENCH** (base) | Banco walk-forward: HMM del motor, GARCH(1,1), Chronos-2 y Toto en zero-shot | CERRADA el 2026-11-09. Fase 1 `baa4ee6` (tabla de cabecera `lago_cierre_c20261101`, proxy declarado, y `binance_c20261101`); fase 2 Toto `8a849c6` en venv aparte `E:/quantdesk-lab/venvs/toto` (`torch==2.7.0` CPU, `toto-ts==0.2.0`; decisión A18), submuestra declarada. Motor `69fdb39d`, semilla 20261101 | Informe `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TS-00-BENCH/informe.md`. La tabla de cabecera FX queda bajo la incidencia ISSUE-LAGO-FX-1D-CLOSE |
| **TS-00-OBJ** | Umbrales de éxito por uso, con el usuario a la vista del banco | CERRADA el 2026-11-09 (puerta 3 del usuario; `83887de`). Escritos en `PLAN_TSFM_FINANZAS` «Fase 0» (quantdesk `905b1670`): forecast con CRPS relativo a GARCH ≤ 0,97 en 2 de 3 horizontes y nunca > 1,02, Kupiec ≤ 10 % de activos por cola, banda 99 % ≤ 2× GARCH; **«pierde claramente» (D-08): X = 3 % en 2 de 3 horizontes**, doble de rechazos de Kupiec, o sin ganar en colas ni en QLIKE; H1 y TS-08-STAB provisionales. FinCast como comparación y profesor candidato (quantdesk `c5f2be51`) | Resuelve GAP-TSFM-03 (forma combinada, decidida el 2026-11-09). Se revisan si la tabla FX sobre MT5 cambia la conclusión (ISSUE-LAGO-FX-1D-CLOSE, criterio 2) |

## 3. Calendario del laboratorio

«L» = este laboratorio. Las asignaciones a SPRINT-04 y posteriores son estimaciones por dependencias; se recalibran al
planificar cada sprint. **Las tareas de `quantdesk` («Q») no se copian aquí** (usuario, 2026-11-09; C-26): su fuente de
verdad es el alcance de SPRINT-03 en
[`quantdesk/docs/plans/next/README.md`](S:/projects/quantdesk/docs/plans/next/README.md) y sus planes de diseño. La
copia que había hasta el 2026-11-09 queda en la historia de git (`git show 8a849c6:docs/plans/backlog/README.md`, §3).

### 3.1 Ahora (en paralelo a SPRINT-02 de `quantdesk`, activo desde el 2026-10-23; sin tocar `quantdesk`)

- **L (SPRINT-01, cerrado el 2026-11-09 sin arrastres):** hechas LAB-00-ENV, TI-01-INV, TI-13-PUB (corpus), TI-02-DATA,
  TI-02-DATA-DEUDA, TS-00-PREC, TI-12-MT5, TS-00-BENCH y TS-00-OBJ. TI-09-ARCH fue retirada del sprint por falta de datos
  (GAP-BACKLOG_README-01). El laboratorio **no tiene sprint activo** hasta que SPRINT-02 se active (cierre de SPRINT-02
  de `quantdesk`).
- **L (fuera de sprint, ya):** TI-09-SONDA (puerta de usuario: token de lectura), TI-12-MT5-INTRA-LOCAL (1m y 5m en local
  con hash; primera descarga de `@continuo` hecha, falta la incremental periódica, que se hace en la ficha: D3; y medir
  las acciones: D3b) y [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md) (publicador que no emite velas 1d
  incompletas, modo de reenvío y republicación de las 23 velas; D1; GAP-BACKLOG_README-08 resuelto). La incidencia del
  close del FX diario ([ISSUE-LAGO-FX-1D-CLOSE](../current/issues/ISSUE-LAGO-FX-1D-CLOSE.md)) **no es fuera de sprint**: va en
  SPRINT-02, fila 1b (D2; GAP-BACKLOG_README-07 resuelto). Fichas en [issues/](../issues/index.md).
- **Backend (`quantdesk-backend`, su propio sprint):** OC-01 y OC-02 hechas (su SPRINT-01); OC-03 y OC-04 en su SPRINT-02.
  Corte a `market.ohlcv.v2` hecho (2026-11-09). MT5 es la fuente por defecto del FX diario (`6425e29`, desplegado
  2026-11-09); su ficha ISSUE-FX-1D-CLOSE-YFINANCE sigue abierta por si se corrige o retira el 1d de yfinance, y registra
  el aviso de la vela 1d incompleta (`e90eb03`). Publicadores de fuentes públicas: plan nuevo
  `PLAN_PUBLICADORES_MERCADO_PUBLICO` (usuario, 2026-11-09).
- **Network:** OCS-01/OCS-02 cerradas; `market.ohlcv.v2` registrado. Pendiente su visto bueno para el universo ampliado
  de MT5 (la noche 1 de `@continuo`, prevista para las 02:03 del 2026-11-10, queda aplazada según el aviso del backend);
  el intradía se le pide al planificar SPRINT-04. Herramienta genérica de borrado en el lago (rompe 12-A).
- **Usuario:** reiniciar la máquina antes de la ola 2 de SPRINT-03 de `quantdesk`. Hechas por el usuario: registro de la
  tarea programada del publicador MT5, los umbrales de TS-00-OBJ (X = 3 %) y, el 2026-11-10 (revisión de planes), la
  aprobación de las 23 republicaciones de velas 1d (D1) y la decisión de GAP-BACKLOG_README-07 y -08.

### 3.2 Cuando termine SPRINT-02 de `quantdesk` (= SPRINT-02 del laboratorio)

- **L ([current/SPRINT.md](../current/SPRINT.md), activo desde el 2026-11-11, partido por el usuario sin esperar a
  `quantdesk`):** FinCast en el banco, ampliaciones de MT5; rueda re-fijada y HMM causal pasaron a SPRINT-03 (S02-*); TI-13-PUB consume lo que publique el backend. TI-02-DATA-V2 y la repetición del banco FX sobre MT5 entran
  aquí como fila 1b (GAP-BACKLOG_README-07 resuelto, D2).
- **Antes de la ola 1 de SPRINT-03 de `quantdesk`:** exportador diario TI-02-DIARIO con los OAS para XVA: el laboratorio
  escribe el código y el backend lo programa en Dagster en su SPRINT-03 (D5, D6).
- Nota (2026-11-09): desde el 2026-11-06 las GPU están en pruebas de rendimiento y la IA local en pausa; el deep learning
  nativo va por Rust/Burn con GPU obligatoria en `engine-nn`. El uso de GPU del laboratorio (zero-shot con PyTorch-ROCm)
  depende de que esa pausa termine (GAP-BACKLOG_README-05).

### 3.3 Cuando termine SPRINT-03 de `quantdesk` (= SPRINT-03 del laboratorio)

- **L:** TS-02-DISC; re-exportación con procedencia TI-03-FMT ([next/SPRINT.md](../next/SPRINT.md)); y las filas S02-1…S02-4.

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
- ~~GAP-BACKLOG_README-01~~ **resuelto con su opción (c) (usuario, 2026-11-10, revisión de planes, D11)** (vuelta de TI-09-ARCH: esperar a OC-03 y unos 20 días hábiles, sin spot de respaldo): ver [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) §6.
- ~~GAP-BACKLOG_README-02~~ **resuelto (usuario, 2026-11-09):** plan nuevo en el backend `PLAN_PUBLICADORES_MERCADO_PUBLICO`, FRED común con F1 de FUENTES.
- GAP-BACKLOG_README-03 **abierto** (dos publicadores en acciones US y cripto): ver [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §7.
- ~~GAP-BACKLOG_README-04~~ **resuelto (usuario, 2026-11-09):** 1m y 5m de MT5 en local ya, con hash; publicar en qn al planificar SPRINT-04.
- GAP-BACKLOG_README-05 **abierto, diferido** (GPU para Chronos-2/Toto): CPU mientras dure la pausa de las GPU; se reevalúa al planificar SPRINT-03 del laboratorio.
- ~~GAP-BACKLOG_README-06~~ **resuelto (usuario, 2026-11-09):** dividir en tres y enlazar el calendario «Q».
- Nuevos: ~~GAP-ARCHIVO_OPCIONES-01~~ (forma de la copia propia; **resuelto**, usuario, 2026-11-10, D7: sin copia propia, copia común de network) y ~~GAP-DATOS_VIA_QN-01~~ (dueño del exportador diario; **resuelto**, usuario, 2026-11-10, D6: el laboratorio escribe, el backend programa).

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

## Revisión de planes (2026-11-10, parcial)

Veredicto: **ACTUALIZAR** (aplicado) · Motivo: el índice describía SPRINT-01 como activo y a TS-00-BENCH, TS-00-OBJ y
TI-12-MT5 fase C como «en curso»; las tres están cerradas y archivadas, y han aparecido dos frentes sin sprint (repetir el
banco FX sobre el 1d de MT5 y la vela 1d incompleta). La división de ayer (índice + dos planes) se mantiene. Sigue siendo
un índice: nada se fusiona ni se divide. · Cambios desde la revisión de 2026-11-09: cierre y archivo de SPRINT-01
(`d4a83b5`, `083cf72`); TS-00-OBJ cerrada con X = 3 % (`83887de`; quantdesk `905b1670`, `c5f2be51`); FinCast en el banco de
SPRINT-02 (fila 2b, `84dafed`); TI-12-MT5 fase C y cuadre cerrados (`fdfa3a7`, `beaf81c`); ISSUE-LAGO-FX-1D-CLOSE abierta
(`beaf81c`) y actualizada con la decisión del backend (`6425e29`, MT5 por defecto); primera descarga m1/m5 de `@continuo`
(`b7b074c`); aviso de vela 1d incompleta (backend `e90eb03`). Aplicado a este fichero: §2 (verificado contra el archivo,
no contra `current/`), §2.2 (filas TI-12-MT5, banco FX sobre MT5, TS-00-BENCH ampliaciones; quitadas TS-00-BENCH y
TS-00-OBJ como en curso), §2.3 (TI-12-MT5 fase C, TS-00-BENCH y TS-00-OBJ pasan a hechas), §3.1 y §3.2. Se conservan la
ruta, el ancla `#21-comprobaciones-2026-11-07` y la sección de ayer.

| Tarea | Clasificación | Evidencia / motivo |
|---|---|---|
| Asignación a sprints (cabecera «Origen») | HECHO | Ya decía «SPRINT-01 cerrado y archivado» (`083cf72`); §2.2 y §3.1 no lo decían |
| TS-00-BENCH (base) | HECHO (antes VIGENTE) | `baa4ee6`, `8a849c6`, cierre `2e8dfff`; `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TS-00-BENCH/informe.md`; SPRINT.md §10 |
| TS-00-OBJ | HECHO (antes DUPLICADO en una fila de `current/SPRINT.md`, que ya no existe) | `83887de`; quantdesk `905b1670` (umbrales, X = 3 %) y `c5f2be51` (FinCast, D-08). Resuelve el «X se fija en TS-00-OBJ» de la fila |
| TI-12-MT5 (fase C) | HECHO (antes VIGENTE) | `9e9dfe5`, `f9dcd0c`, `fdfa3a7`, cierre `beaf81c`; STATUS «MT5 (local)» |
| TI-12-MT5 (publicador 1d de fx28, tarea programada) | HECHO (antes «salvo puerta de usuario») | El usuario registró `quantdesk\publicador_mt5` (`6c02490`; SPRINT.md §10 «Operación») |
| TI-12-MT5 (publicar `@continuo` y acciones en qn) | VIGENTE, aplazado | Backend `e90eb03`: noche de activos continuos aplazada por la vela 1d incompleta; noche 2 espera a network y al usuario (SPRINT.md §10). **SIN VERIFICAR** si la noche 1 de las 02:03 se canceló: la revisión se hizo a la 01:00 |
| TI-12-MT5-INTRA-LOCAL | VIGENTE, parcial | `b7b074c`: 386 series, 37 944 660 filas, `sha256:5cd9bf86…`; faltan los criterios 2 (incremental periódico) y 1 sobre `@continuo` completo |
| Repetir el banco FX sobre el 1d de MT5 (nuevo) | VIGENTE (MODIFICADO frente a la ficha) | Ficha `issues/ISSUE-LAGO-FX-1D-CLOSE.md`, criterio 3 sustituido: el exportador filtra `source=mt5`. `scripts/descarga_lago.py:57` lee sólo `market.ohlcv` (v1): no ve MT5 |
| TI-02-DATA-V2 | MODIFICADO | Pasa de «backlog, sin urgencia» a prerrequisito del punto anterior (MT5 sólo existe en `market.ohlcv.v2`) |
| FinCast en el banco | DUPLICADO (next/SPRINT.md fila 2b) | `84dafed`; requiere venv propio y GPU si DL-02-GATES la habilita |
| Publicador MT5: velas 1d sólo con historia sincronizada (nuevo) | VIGENTE (a la 01:00 sin ficha; desde el 2026-11-10 con ficha [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md), D1) | Aviso del backend `e90eb03`: «Model lo corrige»; no había commit, ficha ni fila en el laboratorio a las 01:00 (`git log` y `issues/` sin rastro) |
| Ejecuciones de entrenamiento, adaptadores, TS-02-DISC | DUPLICADO (future/SPRINT-03 y -04) | Sin cambios; `future/SPRINT-03` y `-04` sólo repuntan su DoD al archivo (`d4a83b5`) |

GAPs nuevos de la revisión (siguen abiertos -03 y -05 de ayer; **-01, -07 y -08 resueltos por el usuario el 2026-11-10**, ver la sección siguiente):
- ~~**GAP-BACKLOG_README-07 — Cuándo y dónde se repite el banco FX sobre el 1d de MT5, y quién hace TI-02-DATA-V2.**~~
  **RESUELTO (usuario, 2026-11-10, revisión de planes, D2 y D15):** en SPRINT-02 del laboratorio, fila 1b de
  `next/SPRINT.md` (TI-02-DATA-V2 más repetición de la tabla FX, en dos tablas), antes de las filas 2, 4 y 7; se descarta
  hacerlo fuera de sprint (la recomendación (a) de abajo). Texto histórico. Contexto:
  la tabla de cabecera del banco usa un close de yfinance corrido un día; el backend ya sirve MT5 por defecto y no corrige
  el lago. Arreglarlo exige TI-02-DATA-V2 (hoy en backlog, sin sprint) y una tabla nueva; SPRINT-02 del laboratorio no
  empieza hasta que cierre SPRINT-02 de `quantdesk`, que sigue en curso, y su fila 2 no lo incluye. Opciones: (a) hacerlo ya
  fuera de sprint, como INTRA-LOCAL y la sonda (sin motor nuevo: vale la rueda `69fdb39d`; coste: unas horas de CPU del
  banco y un script cambiado; los demás consumidores de la tabla vieja, TS-00-OBJ y `PLAN_TSFM_FINANZAS`, se corrigen
  antes); (b) esperar a SPRINT-02 y añadir las filas (la tabla de cabecera de TS-00-OBJ queda en entredicho semanas); (c) no
  repetir y declarar la tabla como proxy (se pierde la comprobación de los umbrales). Recomendación: (a), porque los
  umbrales de TS-00-OBJ se apoyan en esa tabla y el cambio no depende de nada de `quantdesk`. Si no se decide, la
  incidencia sigue «Abierto» y los umbrales quedan sin contrastar hasta SPRINT-02.
- ~~**GAP-BACKLOG_README-08 — Dónde se sigue el arreglo de la vela 1d incompleta del publicador MT5 (y su republicación).**~~
  **RESUELTO (usuario, 2026-11-10, revisión de planes, D1):** ficha urgente fuera de sprint
  [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md) (opción (a)), con modo de reenvío, aprobación de las 23
  republicaciones y carga nocturna de `@continuo` aplazada hasta cerrarla. Texto histórico. Contexto: la vela del 2026-11-09, publicada a las 23:01 UTC, salió incompleta en 23 de 28 pares por historia D1 sin
  sincronizar; el laboratorio dijo al backend que lo corrige y que republicará con aprobación del usuario. Hoy no consta en
  ningún plan ni ficha del laboratorio. Opciones: (a) ficha nueva fuera de sprint, urgente (`issues/`), con aceptación
  ejecutable (selftest con el MT5 falso que devuelve D1 parcial) y la republicación como puerta de usuario; (b) reabrir
  TI-12-MT5 (cerrada, con su cierre ya archivado: reescribe la historia del sprint); (c) añadirlo a
  ISSUE-LAGO-FX-1D-CLOSE (mezcla dos causas: la del origen yfinance y la del publicador propio). Recomendación: (a), porque
  es un defecto propio del laboratorio, afecta a datos ya en qn y bloquea la carga de `@continuo`. Si no se decide, el
  1d de MT5 del 2026-11-09 sigue sin ser fiable para cualquier consumidor y la carga de continuos sigue aplazada.

Contradicciones:
- ~~**C-BACKLOG_README-06 — Enlaces de `quantdesk` al laboratorio rotos por el archivo.**~~ **Resuelta por regla (usuario, 2026-11-10, revisión de planes):** los enlaces `quantdesk-model/docs/plans/current/...` se repuntan a `archive/SPRINT-01_2026-11-07_2026-11-09/...`; la edición es del aplicador de `quantdesk`. Texto histórico: `quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md` (líneas 89, 256 y 290, 2026-11-09 17:16–17:28) y `PLAN_TSFM_INTEGRACION.md` (líneas 56, 153 y 169) citan `quantdesk-model/docs/plans/current/SPRINT.md` y `current/execution/{TS-00-BENCH,TI-01-INV,TI-13-PUB}/`; desde `d4a83b5` (17:52) viven en `archive/SPRINT-01_2026-11-07_2026-11-09/` y `current/` sólo tiene un README. PLAN_TSFM_FINANZAS además dice «se ejecuta en SPRINT-01» (cerrado). Dependen: el lector de los umbrales de TS-00-OBJ y la tabla de licencias de TI-00-ADR. Consecuencia: si `quantdesk` repunta, la ruta queda atada al nombre del dossier archivado; si no, los enlaces fallan (no se pierde evidencia, está en git y en el archivo). Es edición de otro proyecto: no se hace aquí.
- ~~**C-BACKLOG_README-07 — Derivados del laboratorio con el estado de antes del cierre.**~~ **Resuelta por regla (usuario, 2026-11-10, revisión de planes):** `index.md`, `issues/index.md` y `PLAN_DATOS_VIA_QN` puestos al día tras el cierre de SPRINT-01. Texto histórico: `index.md` (fila «Backlog del laboratorio»: «Repartido en SPRINT-01…04») y `backlog/PLAN_DATOS_VIA_QN.md` §2 («SPRINT-01, en curso», «`current/execution/TI-12-MT5/fase-c.md`», visto bueno «de fase C» pendiente, tarea programada «puerta de usuario», «se revisa al cerrar SPRINT-01») contradicen el cierre del 2026-11-09 (SPRINT.md §10). `PLAN_DATOS_VIA_QN` lo actualiza su propio revisor; `index.md` y `STATUS.md` los regenera el cierre. Consecuencia: leer el plan de datos sin este índice da por activa la fase C.
- ~~**C-BACKLOG_README-08 — Seguimiento de la incidencia del FX sin fila en el sprint.**~~ **Resuelta (usuario, 2026-11-10, revisión de planes, D2):** el seguimiento es la fila 1b de `next/SPRINT.md`, que se añade; la ficha ya remite a ella. Texto histórico: `issues/ISSUE-LAGO-FX-1D-CLOSE.md` (2026-11-09 18:38; «Seguimiento: SPRINT-02, fila 2») y `archive/SPRINT-01_.../SPRINT.md` §10 («destino SPRINT-02») frente a `next/SPRINT.md` (fila 2: sólo HMM causal, FG-16-hmmcop «más activos y horizontes»; sin filtro `source=mt5` ni repetición de la tabla FX) y a `PLAN_DATOS_VIA_QN.md` §4 (TI-02-DATA-V2 «Backlog»). Dependen: GAP-07, los umbrales de TS-00-OBJ. Consecuencia: resolver a favor de SPRINT-02 exige añadir filas a `next/SPRINT.md` y traer TI-02-DATA-V2; resolver a favor de «ya» exige cambiar el destino de la ficha a «Fuera de sprint».

Sinergias: backend `ISSUE-FX-1D-CLOSE-YFINANCE` (`6425e29`, `e90eb03`: MT5 por defecto y velas incompletas; quien lea FX diario
del lago debe filtrar `source=mt5`, también los publicadores de curvas y el XVA/TSFM de `quantdesk`); network (visto bueno
de la carga de `@continuo`); `PLAN_TSFM_FINANZAS` (umbrales de «Fase 0» y FinCast en D-08, a revisar si la tabla FX sobre MT5
cambia la conclusión); `PLAN_DEEP_LEARNING_GPU` (FinCast pide GPU en el banco: GAP-BACKLOG_README-05 sigue diferido).

## Decisiones del usuario (2026-11-10, revisión de planes)

Fuente de todas: usuario, 2026-11-10, revisión de planes (registro en [REVISIONES.md](REVISIONES.md)).

| Decisión | Resuelve | Efecto en el laboratorio |
|---|---|---|
| D1 «Republicar y aplazar» | GAP-BACKLOG_README-08 | Ficha urgente fuera de sprint [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md); se aprueban las 23 republicaciones; carga de `@continuo` aplazada hasta cerrarla |
| D2 «En SPRINT-02» | GAP-BACKLOG_README-07, C-BACKLOG_README-08 | Fila 1b de `next/SPRINT.md`: TI-02-DATA-V2 y repetición de la tabla FX sobre MT5; `ISSUE-LAGO-FX-1D-CLOSE` remite a ella |
| D3 y D3b | (PLAN_DATOS_VIA_QN: C-DATOS_VIA_QN-03, GAP-DATOS_VIA_QN-04) | Incremental de MT5 ya, en INTRA-LOCAL; medir las 484 acciones con `--simular` |
| D6 | (GAP-DATOS_VIA_QN-01) | TI-02-DIARIO: el laboratorio escribe el código, el backend lo programa |
| D7 y D11 | GAP-BACKLOG_README-01 (opción (c)); (PLAN_ARCHIVO_OPCIONES: GAP-ARCHIVO_OPCIONES-01 y -02, C-ARCHIVO_OPCIONES-01) | Sin copia propia (copia común de network); sin spot de respaldo; `lake delete` no sobre `market.*` hasta que exista la copia común |
| D13 y D15 | (PLAN_TSFM_FINANZAS: GAP-TSFM-08 y -09) | FinCast sólo en CRPS y QLIKE sobre la ventana limpia (fila 2b); la tabla FX en dos tablas (fila 1b) |
| Por regla | C-BACKLOG_README-06, C-BACKLOG_README-07 | Enlaces de `quantdesk` al archivo de SPRINT-01 (los repunta su aplicador); derivados del laboratorio al día |

GAPs que siguen abiertos en este índice: GAP-BACKLOG_README-03 (dos publicadores en acciones US y cripto) y
GAP-BACKLOG_README-05 (GPU, diferido). Contradicciones abiertas: ninguna.

[PLAN_TSFM_FINANZAS]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md
[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
[PLAN_XVA_BANCARIO]: S:/projects/quantdesk/docs/plans/backlog/PLAN_XVA_BANCARIO.md
[PLAN_DEEP_LEARNING_GPU]: S:/projects/quantdesk/docs/plans/backlog/PLAN_DEEP_LEARNING_GPU.md
