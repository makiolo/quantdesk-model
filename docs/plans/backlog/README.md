# Backlog del laboratorio (`quantdesk-model`)

Planes individuales futuros, uno por tema (`PLAN_<TEMA>.md`), sin sprint asignado. Cada plan lleva
estado, estado verificado, opciones, fases o tareas con aceptación verificable, dependencias, riesgos
y preguntas abiertas. `sprint planificar` los refresca contra el código y agrupa sus tareas en
`next/` o en un `future/SPRINT-NN/`; los documentos de visión permanentes (p. ej. `ROADMAP.md`) se
refrescan pero no se fusionan. Listado y estado de cada plan: tablero [index.md](../index.md).

> **Origen:** contenido íntegro de `docs/plans/BACKLOG.md` (2026-11-07), trasladado aquí al instalar los sprints; esa ruta queda como puntero. **Asignación a sprints** (usuario, 2026-11-07): el sprint N del laboratorio es «lo que se puede hacer cuando termine el sprint N de `quantdesk`», salvo SPRINT-01, que es lo que se puede hacer ya; **enmendada** (usuario, 2026-11-13, revisión de planes, R1): desde SPRINT-03, el sprint N+1 del laboratorio corresponde al sprint N de `quantdesk`. Hoy (2026-11-13): SPRINT-01 **cerrado** (2026-11-07 a 2026-11-09) y archivado en [archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md); SPRINT-02 **cerrado con arrastres** (2026-11-11 a 2026-11-13; partido el 2026-11-11 sin esperar a `quantdesk`) y archivado en [archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md); **SPRINT-03 rehecho** en [next/SPRINT.md](../next/SPRINT.md) con sólo lo que no depende de `quantdesk` (TI-02-DIARIO, S02-5, S02-6 con la sonda, INTRA-LOCAL, operación del publicador MT5, universo ampliado condicionado, consumo FRED/OAS; sin dependencia de entrada); SPRINT-04 (filas S02-1…S02-4 y ciclo sintético-real, tras quantdesk SPRINT-03) y SPRINT-05 (escalera de entrenamiento, antes SPRINT-04, tras quantdesk SPRINT-04) en [future/](../future/README.md); dependencias en [DEPENDENCIAS.md](../DEPENDENCIAS.md).

**Fecha:** 2026-11-07; **revisado y dividido el 2026-11-09** (usuario, 2026-11-09; primera sección final); **puesto al
día el 2026-11-10** tras el cierre de SPRINT-01 (segunda sección final), con las decisiones del usuario del mismo día
aplicadas (tercera sección final); **puesto al día el 2026-11-13** tras el cierre de SPRINT-02 (cuarta sección final,
«Revisión de planes (2026-11-13)»), con las **decisiones del usuario R0–R8 del mismo día aplicadas** (sección final
«Decisiones del usuario (2026-11-13, revisión de planes)»). Este fichero es el
**índice** del backlog del laboratorio, la regla de separación y el calendario **del laboratorio**. Lo que ya está en un
sprint del laboratorio se especifica allí; aquí queda su estado. Lo que no tiene sprint vive en sus planes:

| Plan | Contenido | IDs |
|---|---|---|
| [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) | Archivo de cadenas de opciones desde el lago, sonda de sólo lectura y retención (sin copia propia: la copia es la común de network; usuario, 2026-11-10) | TI-09-ARCH (parte laboratorio **entregada** en SPRINT-02; queda la medición de cobertura, fila S02-6 = fila 3 de [next/SPRINT.md](../next/SPRINT.md)), TI-09-SONDA (se cierra con S02-6, R4). Backlog residual: se archiva al cerrar S02-6 |
| [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) | MT5 (universo ampliado, intradía en local y en qn, tarea programada), datos públicos movidos al backend, exportadores (sólo v2 y diario de D-I4), Binance como corpus congelado | TI-12-MT5 (publicar el universo ampliado, intradía en qn, INTRA-LOCAL, tarea programada; «más símbolos y periodos» = S02-5; SYNC **cerrada**, R3), TI-13-PUB (consumo: FRED/OAS en SPRINT-03, Yahoo/Stooq y cripto en el backlog, R6), TI-02-DIARIO (SPRINT-03, R5); TI-02-DATA-V2 **hecha** (SPRINT-02 fila 1b) |

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

Estado verificado el 2026-11-13 (revisión de planes, tras el cierre de SPRINT-02) contra el archivo de SPRINT-01
([archive/SPRINT-01_2026-11-07_2026-11-09/](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md): `SPRINT.md` §10 y
`EXECUTION.md`), el de SPRINT-02 ([archive/SPRINT-02_2026-11-11_2026-11-13/](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md):
`SPRINT.md` §9 y `EXECUTION.md`), [next/SPRINT.md](../next/SPRINT.md), `STATUS.md` (atrasado en varias filas: lo regenera el
cierre), las fichas de [issues/](../issues/index.md) y `git log` del laboratorio (HEAD `7f5a5d0`), y contra los registros de
`quantdesk`, `quantdesk-backend` y `quantdesk-network`. No hay sprint activo: `current/` está vacío desde el cierre de
SPRINT-02 (2026-11-13). Lo ya cerrado está en §2.3.

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

| ID | Qué se hace aquí | Cuándo / estado (2026-11-13) | Notas |
|---|---|---|---|
| **TI-09-ARCH** (medición de cobertura), **TI-09-SONDA** | Medir la cobertura de 20 días hábiles NYSE del archivo de cadenas; sonda de sólo lectura | La **parte de laboratorio de TI-09-ARCH está HECHA** (SPRINT-02 fila 6: lector y archivador aceptados `c6c7b5b`, primer dataset real `oc03_s20261112_c20261113` `sha256:eb98ac6a…eea1`, `a80ad40`). Queda la medición: fila **S02-6** de [next/SPRINT.md](../next/SPRINT.md) (fila 3 del SPRINT-03 nuevo; corte posterior al 2026-12-10, `QN_TOKEN` nuevo: puerta de usuario). La sonda sigue abierta como ficha ([ISSUE-TI09-SONDA-CADENAS](../issues/ISSUE-TI09-SONDA-CADENAS.md)): la sonda de contraste del 2026-11-13 midió agregados, no la cifra por día hábil desde el 2026-11-09. **Decisión (usuario, 2026-11-13, revisión de planes, R4):** la sonda se cierra con la cifra por sesión de S02-6 desde el 2026-11-12 y su fila se une a S02-6; los días 2026-11-09…11 quedan como no medibles; STATUS ya corregido (cadenas presentes; `market.options.fx` vacío) | [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md). La sonda y S02-6 comparten puerta (token de lectura de qn), y su cifra por día sale del mismo volcado |
| **TI-12-MT5** (más símbolos y periodos; publicar el universo ampliado; intradía en qn; INTRA-LOCAL; SYNC), **TI-13-PUB** (consumo del mercado público), **TI-02-DIARIO** | Datos de mercado vía qn y exportadores | **TI-02-DATA-V2 CERRADA** (SPRINT-02 fila 1b, §2.3). La fase C (1d local) y el cuadre están cerrados (§2.3). «Más símbolos y periodos» (h1 de `@continuo`, sin símbolos nuevos; usuario, 2026-11-11) = fila **S02-5** de `next/SPRINT.md`, a la espera del desbloqueo de la cuenta MT5. Publicar `@continuo` y acciones en qn: **aplazado y sin fila de sprint** (necesita cerrar [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md), cuenta MT5 y visto bueno de network; usuario, 2026-11-10, D1). INTRA-LOCAL: fuera de sprint, primera descarga hecha el 2026-11-09, **criterios 2, 4 y 6 sin hacer** (sin commits del extractor desde el 2026-11-10). TI-13-PUB (consumo): **vuelve al backlog** (fila 7 salió de SPRINT-02, `96ed9c0`); el SPRINT-03 del backend sólo publica FRED y OAS, no Yahoo/Stooq ni cripto (C-BACKLOG_README-01). TI-02-DIARIO: el laboratorio escribe y el backend programa (D6), **sin fila en ningún sprint del laboratorio** (C-BACKLOG_README-02). **Decisiones del 2026-11-13 (usuario, revisión de planes):** S02-5 + INTRA-LOCAL forman la fila 4 de MT5 del SPRINT-03 nuevo (4a, 4b; mutex del terminal, descargas prudentes; R8) con la reactivación del publicador y la carga nocturna de `@continuo` (4c; R2, R3); [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md) **cerrada** fusionando VELA-A-MEDIAS (R3); el resto del universo ampliado en qn es la fila 5, condicionada (GAP-DATOS_VIA_QN-08); el intradía en qn va con SPRINT-05 (R7); TI-13-PUB consumo se divide: FRED/OAS = fila 6 (dependencia de tarea del backend SPRINT-03), Yahoo/Stooq y cripto al backlog (R6); TI-02-DIARIO = filas 1 (contrato, primera), 2 (código sin OAS) y 7 (OAS) (R5) | [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md). Publicador 1d de fx28: tarea `quantdesk\publicador_mt5` registrada por el usuario (`6c02490`); estuvo **activa y fallando** (`Authorization failed`) desde el 2026-11-10 hasta que la raíz de guardia la **desactivó el 2026-11-13** (~23:55 local, `schtasks /Change /DISABLE`, verificado «Disabled»; usuario, 2026-11-13, revisión de planes, R2) hasta el desbloqueo de la cuenta: el 1d de MT5 en qn está parado desde el 2026-11-10 y se reactiva en la fila 4c (C-BACKLOG_README-11 resuelta por regla) |
| **TS-00-BENCH** (ampliaciones) | HMM filtrado causal y corpus FG-16-hmmcop (fila S02-2), GPU (SPRINT-04 fila 5; era SPRINT-03 fila 5 antes de la partición del 2026-11-13). **FinCast HECHO** (SPRINT-02 fila 2b, §2.3) | HMM causal y FG-16-hmmcop esperan a `quantdesk` SPRINT-02 (E15-filter, FG-16-hmmcop; cubiertos por el cierre de su SPRINT-03); GPU espera a DL-02-GATES (SPRINT-03 de `quantdesk`, ola 2) | Licencias de pesos Chronos-2/Toto y `toto-ts`: Apache-2.0 (informe). Hallazgo: `arch` 8 ignora `random_state`; la semilla entra por `rng`. **La nota «FinCast en CPU cuesta unas 7 veces Toto» es OBSOLETA:** se midió 1,72 s CPU por origen en FX (2,73 s en Binance) frente a 6,70 s de Toto (SPRINT-02 EXECUTION 2026-11-11 y 2026-11-13); la GPU ya no es necesaria para FinCast y GAP-BACKLOG_README-05 queda reducido a Chronos-2/Toto a gran escala |
| **TS-02-DISC** (parte laboratorio) | Clasificador real frente a sintético e informe de rasgos que faltan | Tras SPRINT-03 de `quantdesk` (necesita TS-02-GEN, ola 3, condicionada a capacidad) | Planificado en [future/SPRINT-04](../future/SPRINT-04/SPRINT.md) §3 fila 4 (antes en `next/SPRINT.md` como SPRINT-03; partición del 2026-11-13, R1) |
| Ejecuciones de entrenamiento | Configuraciones `engine.train-request/v1`, escalera 4 M → 20 M → 80 M, ablaciones TS-05-PRE (interferencia y punto de control D-08) y TS-05-FREQ, recibos e informes | Tras SPRINT-04 de `quantdesk` (necesita TI-06-CLI y DL-07-TRAIN) | Planificado en [future/SPRINT-05](../future/SPRINT-05/SPRINT.md) (antes `future/SPRINT-04`, renumerado el 2026-11-13, R1). El código de entrenamiento es de `quantdesk`. **TS-05-PREC no es del laboratorio**: es el banco de precisión real en las R9700 dentro de `quantdesk` (PLAN_TSFM_FINANZAS) y es dependencia de TS-05-PRE |
| Adaptadores walk-forward | Ejecuciones trimestrales y mensuales de TS-18-WF; TS-06-FT y TS-15-FINAL | Tras SPRINT-04 de `quantdesk` | Planificado en [future/SPRINT-05](../future/SPRINT-05/SPRINT.md) filas 3–5 (antes `future/SPRINT-04`) |

Ampliaciones ya planificadas en sprints (sólo referencia; la especificación está allí):
[SPRINT-02 archivado](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md) (2026-11-11 a 2026-11-13, cerrado con arrastres:
FinCast en el banco (fila 2b) y fila 1b (TI-02-DATA-V2 y banco FX sobre MT5) **cerradas**; TI-09-ARCH parte laboratorio
entregada; fila 5 (TI-12-MT5, más símbolos y periodos) y la medición de cobertura de la fila 6 **arrastradas** a SPRINT-03;
fila 7 (TI-13-PUB) devuelta al backlog),
[next/SPRINT.md](../next/SPRINT.md) (**SPRINT-03 nuevo**, sin dependencia de entrada, usuario, 2026-11-13, revisión de
planes, R1: TI-02-DIARIO contrato y código sin OAS, S02-6 con la sonda, fila de MT5 con S02-5, INTRA-LOCAL y operación del
publicador, universo ampliado condicionado, consumo FRED/OAS y OAS del exportador),
[future/SPRINT-04](../future/SPRINT-04/SPRINT.md) (filas S02-1…S02-4 recibidas de SPRINT-02 el 2026-11-11, LAB-00-ENV
re-fijado, TS-00-BENCH y TS-00-PREC con HMM causal y FG-16-hmmcop, TI-02-DATA con el universo59; re-exportación con
procedencia TI-03-FMT, licencias al ADR, TS-00-PREC con TS-01-SIM, TS-02-DISC, TS-00-BENCH en GPU) y
[future/SPRINT-05](../future/SPRINT-05/SPRINT.md) (entrenamiento; intradía de MT5 en qn, R7). *Texto anterior (2026-11-13,
antes de las decisiones):* «Sin fila en ningún sprint: TI-02-DIARIO, publicar el universo ampliado y el intradía de MT5
en qn, TI-13-PUB (consumo) y la cola de fichas de issues/». **Hoy sólo quedan sin sprint** el consumo de Yahoo/Stooq y
cripto (R6) y la política de dos publicadores (GAP-BACKLOG_README-03).

### 2.3 Hechas (constancia)

| ID | Qué se hizo | Evidencia |
|---|---|---|
| **LAB-00-ENV** | `.venv` propio (Python 3.12.3 de `D:/miniconda312`), `requirements.lock` con hashes (torch 2.15.0+cpu, chronos-forecasting 2.3.2, `arch`, `ml_dtypes`, `MetaTrader5`, `pyarrow`), rueda `quantdesk-0.0.0-cp312` construida desde quantdesk `69fdb39d` (`scripts/build_wheels.py`, `E:/quantdesk-lab/wheels/SHA256SUMS`), cachés en `E:/quantdesk-lab/` | CERRADA el 2026-11-08 (`a581355`, `33e91fd`, `6b5ac1e`, `a9a7223`; cierre `ee7454e`); STATUS «Entorno» |
| **TI-01-INV** | Inventario de todos los topics `market.*` del lago (`scripts/inventario_options_chain.py`) | CERRADA el 2026-11-08 (`f8f53ad`…`cb46ce2`; cierre `e8df2f8`); `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-01-INV/` (antes `current/execution/`). Hallazgos: 28 cruces FX diarios desde 2024-11; tipos y rendimientos desde 2025-12 con hueco 2026-04…09; cadenas vacías (a esa fecha); la flota de qn no tiene GPU |
| **TI-13-PUB** (corpus genéricos) | Corpus con licencia (Chronos, LOTSA) y Binance; filtro de fugas D-11 (corte provisional 2016-10-01), train/val disjuntos | CERRADA el 2026-11-08 (`7ea6d94`); 36 datasets, 1,0 GB en `E:/quantdesk-lab/datasets/TI-13-PUB/`; `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-13-PUB/` (licencias, filtro; antes `current/execution/`). Binance se ingirió directamente, antes de A16; queda como corpus congelado con hash (usuario, 2026-11-09; [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §5) |
| **TI-02-DATA** | Exportador a `engine.market-history/v1` (`scripts/exportar_market_history.py`) | CERRADA el 2026-11-09 (`906f73e`, revisión 2 ACEPTAR); cuatro datasets en `E:/quantdesk-lab/datasets/TI-02-DATA/` (`binance_c20261101`, `lago_c20261101`, `lago_cierre_c20261101` proxy con `default_lag_ms`, `lago_c20261107`), hash reproducible y 0 violaciones de look-ahead. La procedencia va en `procedencia.json` adjunto hasta TI-03-FMT. `descarga_lago.py` leía v1 (corregido por TI-02-DATA-V2, fila siguiente) |
| **TI-02-DATA-DEUDA** | Tres arreglos BAJA de la revisión 2: prueba de la guardia de `default_lag_ms`; CRLF→LF antes de hashear el código; «mayor cambio de close» sólo entre versiones cerradas | CERRADA el 2026-11-09 (`0e67465`); los cuatro `dataset_hash` no cambian |
| **TS-00-PREC** | Banco de precisión emulado (fp8 e4m3/e5m2, bf16, f16, f32 en CPU) | CERRADA el 2026-11-08 (`5afc795`); hash `83548e1a…` reproducido por la raíz. fp8 basta para la entrada, no para la inferencia emulada ni para σ_loc; bf16/f16/f32 no pierden. Ya consumido por PLAN_DEEP_LEARNING_GPU (DL-08-QUANT) |
| **TI-12-MT5** (fases A y B) | Extractor de sólo lectura (lista blanca, hora del servidor a UTC `ny+7`, descarga reanudable con hash estable) y **publicador MT5 → qn `market.ohlcv.v2`** con relleno de huecos, candado, `--simular` y tarea XML; 1d con `ts` a las 00:00 UTC del día de sesión (como yfinance) | Fase A `7d38136`; fase B `a495e5f`, `90fa001`, `45a93ce`, `9ed66d4`, `1ed4dfd`, `558baee`, `773965e`; **primera publicación real** `9b74bed` (28 series fx28, 178 522 barras 1d, idempotente). Backend ya lee v2 (`source=mt5` en ClickHouse `fx_spot_1d` y `/api/fxspot?source=mt5`, **fuente por defecto del 1d** desde backend `6425e29`); network `PLAN_OHLCV_V2_CORTE`. Tarea programada del publicador registrada por el usuario (`4cd1237`, `6c02490`); con la cuenta MT5 bloqueada siguió activa y fallando hasta que la raíz de guardia la **desactivó el 2026-11-13** (R2); se reactiva en SPRINT-03 fila 4c |
| **TI-12-MT5** (fase C y cuadre) | Universos con nombre, 1d local por clase de activo (continuo de 193 series; acciones US: 484 de sesión normal y 13 `-24`), huecos por clase y ritmo de publicación; cuadre del 1m agregado a diario contra el D1 de MT5 y contra el FX diario del lago | CERRADA el 2026-11-09 (`9e9dfe5`, `f9dcd0c`, `fdfa3a7`; cierre `beaf81c`). 1d local: `continuo_1d_20261109` `sha256:a503bb75…`, `us_grandes_1d_20261109` `sha256:6d9e0528…`, `us_grandes24_1d_20261109` `sha256:1e58cb0a…`; m1 de fx28 `fx28_m1_20261109` `sha256:8a6fa0dc…`, cuadrado exacto con el D1 de MT5 | `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/` (`fase-c.md`, `cuadre.md`). El cuadre reveló [ISSUE-LAGO-FX-1D-CLOSE](../archive/SPRINT-02_2026-11-11_2026-11-13/issues/ISSUE-LAGO-FX-1D-CLOSE.md) |
| **TS-00-BENCH** (base) | Banco walk-forward: HMM del motor, GARCH(1,1), Chronos-2 y Toto en zero-shot | CERRADA el 2026-11-09. Fase 1 `baa4ee6` (tabla de cabecera `lago_cierre_c20261101`, proxy declarado, y `binance_c20261101`); fase 2 Toto `8a849c6` en venv aparte `E:/quantdesk-lab/venvs/toto` (`torch==2.7.0` CPU, `toto-ts==0.2.0`; decisión A18), submuestra declarada. Motor `69fdb39d`, semilla 20261101 | Informe `archive/SPRINT-01_2026-11-07_2026-11-09/execution/TS-00-BENCH/informe.md`. La tabla de cabecera FX queda bajo la incidencia ISSUE-LAGO-FX-1D-CLOSE |
| **TS-00-OBJ** | Umbrales de éxito por uso, con el usuario a la vista del banco | CERRADA el 2026-11-09 (puerta 3 del usuario; `83887de`). Escritos en `PLAN_TSFM_FINANZAS` «Fase 0» (quantdesk `905b1670`): forecast con CRPS relativo a GARCH ≤ 0,97 en 2 de 3 horizontes y nunca > 1,02, Kupiec ≤ 10 % de activos por cola, banda 99 % ≤ 2× GARCH; **«pierde claramente» (D-08): X = 3 % en 2 de 3 horizontes**, doble de rechazos de Kupiec, o sin ganar en colas ni en QLIKE; H1 y TS-08-STAB provisionales. FinCast como comparación y profesor candidato (quantdesk `c5f2be51`) | Resuelve GAP-TSFM-03 (forma combinada, decidida el 2026-11-09). **Confirmados por el usuario el 2026-11-13** tras la tabla FX sobre MT5 (ningún modelo cambia de conclusión; `PLAN_TSFM_FINANZAS` «Fase 0», quantdesk `3077fddd`): dejan de ser provisionales |
| **TS-00-BENCH** (FinCast, SPRINT-02 fila 2b) | FinCast (`Vincent05R/FinCast`, 1B parámetros) como cuarto modelo público, en venv propio `E:/quantdesk-lab/venvs/fincast`, subproceso con 21 cuantiles; ventana limpia posterior al 2025-08-27 para todos los modelos; FinCast sólo en CRPS de deciles y QLIKE (D13) | CERRADA el 2026-11-11 (A4 ronda 2 ACEPTAR): `f3f8a4d`, `a98cea8`, `84fe1a9`, `d422e48`, `c0c7633`, `ce1150d`, `05c27cf`; cierre `09befb8`. Pesos `v1.pth` sha256 `d5ca999b…`, `weights_only=True`, Apache-2.0 verificada; 1,72 s CPU por origen en FX; tabla principal idéntica a SPRINT-01. `archive/SPRINT-02_2026-11-11_2026-11-13/execution/TS-00-BENCH-FINCAST/` |
| **TI-02-DATA-V2** y **tabla FX del banco sobre el 1d de MT5** (SPRINT-02 fila 1b; D2, D15) | `descarga_lago.py` lee sólo `market.ohlcv.v2` con selección por `source` (FX diario sólo `source=mt5`); los cuatro datasets de TI-02-DATA se regeneran desde `0e67465` con el mismo hash; el banco se repite en dos tablas (cabecera desde 2024-11 y ampliación desde 2000) | CERRADA el 2026-11-13: código `27cfb2b`…`3e35ed5` (4 correcciones, A4 ACEPTAR), volcado en mini `fb11457`, banco `f0995d0`+`d6bc45d`, cierre `778d0e3`. `descarga_lago.py:65` `TOPICS_DEFECTO = (TOPIC_OHLCV,)` con `market.ohlcv.v2` y selftest de la línea 627; datasets `mt5_fx28_cierre_c20261101` `sha256:a5015bc9…893da` y `mt5_fx28_hist_cierre_c20261101` `sha256:47d79b39…67d32`; ningún modelo cambia de conclusión en TS-00-OBJ. `archive/SPRINT-02_2026-11-11_2026-11-13/execution/{TI-02-DATA-V2,TS-00-BENCH-MT5}/`. Resuelve [ISSUE-LAGO-FX-1D-CLOSE](../archive/SPRINT-02_2026-11-11_2026-11-13/issues/ISSUE-LAGO-FX-1D-CLOSE.md) (criterios 1–3) |
| **TI-09-ARCH** (parte laboratorio, SPRINT-02 fila 6) | Lector bajo demanda de `market.options.chain` y archivador sesión a sesión (cruda y limpia, filtro de monotonía, mariposa y calendario); primer dataset real de la sesión NY 2026-11-12 | PARCIAL, parte de laboratorio ACEPTADA el 2026-11-13 (A4 ACEPTAR tras 2 correcciones): `1b92162`, `fba4279`, `722effa`, `c6c7b5b`, aceptación `a62d78f`, dataset `a80ad40`. `E:/quantdesk-lab/datasets/TI-09-ARCH/oc03_s20261112_c20261113` `sha256:eb98ac6ae50e4e5d7e8dc024fef9347348bc077abc0486136dc462a2a70ceea1` (comprobado en su `informe.md`); cruda 431 681 filas, limpia 320 125; pico de memoria 1,15 GB con 1 sesión. La medición de cobertura queda en S02-6. `archive/SPRINT-02_2026-11-11_2026-11-13/execution/TI-09-ARCH/` |

## 3. Calendario del laboratorio

«L» = este laboratorio. Las asignaciones a SPRINT-04 y posteriores son estimaciones por dependencias; se recalibran al
planificar cada sprint. **Las tareas de `quantdesk` («Q») no se copian aquí** (usuario, 2026-11-09; C-26): su fuente de
verdad es el alcance de SPRINT-03 en
[`quantdesk/docs/plans/next/README.md`](S:/projects/quantdesk/docs/plans/next/README.md) y sus planes de diseño. La
copia que había hasta el 2026-11-09 queda en la historia de git (`git show 8a849c6:docs/plans/backlog/README.md`, §3).

### 3.1 Ahora (sin sprint activo; `quantdesk` sigue en su SPRINT-02; sin tocar `quantdesk`)

- **L (SPRINT-01, cerrado el 2026-11-09 sin arrastres; SPRINT-02, cerrado con arrastres el 2026-11-13):** hechas LAB-00-ENV,
  TI-01-INV, TI-13-PUB (corpus), TI-02-DATA, TI-02-DATA-DEUDA, TS-00-PREC, TI-12-MT5 (A, B y C), TS-00-BENCH, TS-00-OBJ
  (confirmada el 2026-11-13), y de SPRINT-02 TS-00-BENCH FinCast, TI-02-DATA-V2 con la tabla FX sobre MT5 y la parte de
  laboratorio de TI-09-ARCH (§2.3). El laboratorio **no tiene sprint activo** (planificación desde el 2026-11-13).
- **L (fuera de sprint, ya; texto previo a las decisiones del 2026-11-13: la sonda e INTRA-LOCAL pasan a SPRINT-03, filas 3
  y 4b; SYNC y VELA-A-MEDIAS quedan cerradas por R3 y su residuo es la fila 4c):** TI-09-SONDA (puerta de usuario: token de lectura), TI-12-MT5-INTRA-LOCAL (1m y 5m en local
  con hash; primera descarga de `@continuo` hecha el 2026-11-09, **falta la incremental periódica** (D3) y medir las
  acciones (D3b); con crypto 24/7 el margen de ~100 000 barras de m1 se agota hacia el 2027-01-17 si no hay otra
  descarga, cuenta propia de esta revisión sobre las cifras de la ficha) y [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md)
  junto con [ISSUE-TI12-MT5-VELA-A-MEDIAS](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md) (guarda de historia `2ac3f8f`, reenvío
  `9e2a9eb` y 23 velas republicadas y verificadas `b9cbbbe`; **queda reactivar la tarea programada**, que espera al
  desbloqueo de la cuenta MT5, y la carga de `@continuo`, aplazada). ISSUE-LAGO-FX-1D-CLOSE está **resuelta** (fila 1b).
  Fichas en [issues/](../issues/index.md).
- **Backend (`quantdesk-backend`, su propio sprint):** OC-01 y OC-02 hechas (su SPRINT-01); **OC-03 servida**
  (`cc1811d`, 2026-11-12, primer cierre completo `2026-11-12-163125-5b2305`), OC-05-RET cerrada (backend `current/SPRINT.md`), OC-04 en su SPRINT-02 (estado SIN VERIFICAR). Corte a `market.ohlcv.v2` hecho (2026-11-09). MT5 es la fuente por defecto del FX diario (`6425e29`, desplegado
  2026-11-09); su ficha ISSUE-FX-1D-CLOSE-YFINANCE sigue abierta por si se corrige o retira el 1d de yfinance, y registra
  el aviso de la vela 1d incompleta (`e90eb03`). Publicadores de fuentes públicas (`PLAN_PUBLICADORES_MERCADO_PUBLICO`):
  su SPRINT-03 (en `next/`) publica sólo FRED y OAS (PUB-00…PUB-02) y programa el exportador diario; **PUB-03 (Yahoo/Stooq) y
  PUB-04 (cripto) siguen sin sprint** (backend `next/SPRINT.md` §2 y §5).
- **Network:** OCS-01/OCS-02 cerradas; `market.ohlcv.v2` registrado. Pendiente su visto bueno para el universo ampliado
  de MT5 (la noche 1 de `@continuo` sigue aplazada; noche 2, acciones, espera a network y al usuario); el intradía se le
  pide al planificar SPRINT-04. Herramienta genérica de borrado en el lago (rompe 12-A): network concilió su Fase 3 con D7
  en `85c4708` (2026-11-13): sin copia propia del laboratorio, `lake delete` no se usa sobre `market.*` hasta que exista
  la copia común (COP-02/03/08).
- **Usuario:** reiniciar la máquina antes de la ola 2 de SPRINT-03 de `quantdesk`. Hechas por el usuario: registro de la
  tarea programada del publicador MT5, los umbrales de TS-00-OBJ (X = 3 %, confirmados el 2026-11-13), la aprobación de las
  23 republicaciones de velas 1d (D1, 2026-11-10), «Cerrar y arrastrar» SPRINT-02 y fila 7 al backlog (2026-11-13). Siguen en
  su mano: desbloqueo de la cuenta MT5 (S02-5, INTRA-LOCAL, reactivar la tarea, SYNC 7), `QN_TOKEN` de lectura nuevo (S02-6,
  sonda) y cómo ejecutar lo que no depende de `quantdesk` (GAP-BACKLOG_README-09, **resuelto el 2026-11-13 con R1**: se
  parte SPRINT-03). Tras las decisiones del 2026-11-13 siguen en su mano: desbloqueo de la cuenta MT5 (filas 4 y 5 de
  SPRINT-03; la tarea del publicador queda desactivada hasta entonces, R2), el token de lectura de S02-6 (fila 3), aprobar
  el contrato de TI-02-DIARIO (fila 1) y la fila 5 (universo ampliado).

### 3.2 SPRINT-02 del laboratorio (cerrado el 2026-11-13; partido el 2026-11-11 sin esperar a `quantdesk`)

- **L ([archivo de SPRINT-02](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md)):** FinCast en el banco (2b) y TI-02-DATA-V2
  con la tabla FX sobre MT5 (1b) cerradas; TI-09-ARCH parte laboratorio entregada (6); arrastradas S02-5 y S02-6; fila 7
  (TI-13-PUB) al backlog. Rueda re-fijada, HMM causal, FG-16-hmmcop y universo59 pasaron a SPRINT-03 (S02-1…S02-4).
- **TI-02-DIARIO sin sprint (C-BACKLOG_README-02):** «antes de la ola 1 de SPRINT-03 de `quantdesk`»: exportador diario con
  los OAS para XVA; el laboratorio escribe el código y el backend lo programa en Dagster en su SPRINT-03 (D5, D6). SPRINT-02
  se partió y no lo recogió, y SPRINT-03 del laboratorio no empieza hasta que cierre el de `quantdesk`, es decir, después
  de esa ola 1: **por construcción llega tarde** si espera a SPRINT-03. **Resuelto (usuario, 2026-11-13, revisión de
  planes, R1 y R5):** el SPRINT-03 nuevo no tiene dependencia de entrada y TI-02-DIARIO es su primera fila (contrato con el
  backend por mensaje) y la segunda (código sin OAS); los OAS, en la fila 7, cuando el backend los publique.
- Nota (2026-11-09, **SIN VERIFICAR hoy**): desde el 2026-11-06 las GPU están en pruebas de rendimiento y la IA local en
  pausa; el deep learning nativo va por Rust/Burn con GPU obligatoria en `engine-nn`. El uso de GPU del laboratorio (zero-shot
  con PyTorch-ROCm) depende de que esa pausa termine y de DL-02-GATES (ola 2 de SPRINT-03 de `quantdesk`); FinCast ya no la
  necesita (§2.2) (GAP-BACKLOG_README-05).

### 3.3 SPRINT-03 del laboratorio (sin dependencia de entrada; usuario, 2026-11-13, revisión de planes, R1)

- **L ([next/SPRINT.md](../next/SPRINT.md)):** TI-02-DIARIO (contrato con el backend, primera fila; código sin OAS; OAS
  cuando el backend los publique, R5); S02-6 con el cierre de la sonda (tras el 2026-12-10, R4); fila de MT5: S02-5 (h1 de
  `@continuo`), INTRA-LOCAL (fx28 y `@continuo`, después las 484 acciones; manual cada ≤ 6 semanas, la primera antes del
  2027-01-17, R8) y reactivación del publicador con la carga nocturna de `@continuo` (R2, R3), todo tras el desbloqueo de
  la cuenta; universo ampliado en qn, condicionado (GAP-DATOS_VIA_QN-08); consumo de FRED/OAS cuando el backend cierre esas
  tareas de su SPRINT-03 (R6).

### 3.4 Cuando termine SPRINT-03 de `quantdesk` (= SPRINT-04 del laboratorio; antes «= SPRINT-03»)

- **L:** las filas S02-1…S02-4 (rueda re-fijada, HMM causal, TS-00-PREC con FG-16-hmmcop, universo59), TS-02-DISC, la
  re-exportación con procedencia TI-03-FMT, las licencias al ADR, TS-00-PREC con TS-01-SIM y TS-00-BENCH en GPU
  ([future/SPRINT-04](../future/SPRINT-04/SPRINT.md)). *Texto anterior:* incluía las arrastradas S02-5 y S02-6, que «no
  dependen de `quantdesk`» (GAP-BACKLOG_README-09); desde R1 están en SPRINT-03.

### 3.5 Cuando termine SPRINT-04 de `quantdesk` (= SPRINT-05 del laboratorio en adelante; antes «= SPRINT-04»)

- **L:** ejecuciones de la escalera (TS-05-PRE con la prueba de interferencia y el punto de control frente a modelos
  públicos en 20 M), TS-05-FREQ (necesita el intradía de MT5 en qn: se planifica con este sprint, R7), TS-06-FT,
  adaptadores de TS-18-WF, TS-15-FINAL ([future/SPRINT-05](../future/SPRINT-05/SPRINT.md)).
- **Usuario:** D-13 (pagar datos de mercado y CDS) cuando el dato real sea el cuello de botella.

## 4. Dependencias externas

Por plan: [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) §5 y [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) §6;
contrato para `sprint deps` en [DEPENDENCIAS.md](../DEPENDENCIAS.md). Ampliaciones de SPRINT-02/03/04: cierre de los
sprints de `quantdesk` (decidido, usuario, 2026-11-07). Desde el 2026-11-13 (R1): SPRINT-03 sin dependencia de entrada;
SPRINT-04 ← quantdesk SPRINT-03 cerrado; SPRINT-05 ← quantdesk SPRINT-04 cerrado.

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
| Publicador MT5: velas 1d sólo con historia sincronizada (nuevo) | VIGENTE (a la 01:00 sin ficha; desde el 2026-11-10 con ficha [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md), D1) | Aviso del backend `e90eb03`: «Model lo corrige»; no había commit, ficha ni fila en el laboratorio a las 01:00 (`git log` y `issues/` sin rastro) |
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
  [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md) (opción (a)), con modo de reenvío, aprobación de las 23
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
| D1 «Republicar y aplazar» | GAP-BACKLOG_README-08 | Ficha urgente fuera de sprint [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md); se aprueban las 23 republicaciones; carga de `@continuo` aplazada hasta cerrarla |
| D2 «En SPRINT-02» | GAP-BACKLOG_README-07, C-BACKLOG_README-08 | Fila 1b de `next/SPRINT.md`: TI-02-DATA-V2 y repetición de la tabla FX sobre MT5; `ISSUE-LAGO-FX-1D-CLOSE` remite a ella |
| D3 y D3b | (PLAN_DATOS_VIA_QN: C-DATOS_VIA_QN-03, GAP-DATOS_VIA_QN-04) | Incremental de MT5 ya, en INTRA-LOCAL; medir las 484 acciones con `--simular` |
| D6 | (GAP-DATOS_VIA_QN-01) | TI-02-DIARIO: el laboratorio escribe el código, el backend lo programa |
| D7 y D11 | GAP-BACKLOG_README-01 (opción (c)); (PLAN_ARCHIVO_OPCIONES: GAP-ARCHIVO_OPCIONES-01 y -02, C-ARCHIVO_OPCIONES-01) | Sin copia propia (copia común de network); sin spot de respaldo; `lake delete` no sobre `market.*` hasta que exista la copia común |
| D13 y D15 | (PLAN_TSFM_FINANZAS: GAP-TSFM-08 y -09) | FinCast sólo en CRPS y QLIKE sobre la ventana limpia (fila 2b); la tabla FX en dos tablas (fila 1b) |
| Por regla | C-BACKLOG_README-06, C-BACKLOG_README-07 | Enlaces de `quantdesk` al archivo de SPRINT-01 (los repunta su aplicador); derivados del laboratorio al día |

GAPs que siguen abiertos en este índice: GAP-BACKLOG_README-03 (dos publicadores en acciones US y cripto) y
GAP-BACKLOG_README-05 (GPU, diferido). Contradicciones abiertas: ninguna.

## Revisión de planes (2026-11-13)

Veredicto: **ACTUALIZAR** (aplicado a §2, §3 y la cabecera; la sección de ayer y las anteriores se conservan como historia) ·
Motivo: el índice describía SPRINT-02 como activo y a TI-02-DATA-V2, la tabla FX sobre MT5, FinCast y la parte de laboratorio
de TI-09-ARCH como pendientes; todo eso está cerrado y archivado (`778d0e3`, `05c27cf`, `c6c7b5b`, `a80ad40`). Sigue siendo un
índice: nada se fusiona ni se divide. Aparecen tres huecos que el índice no recogía: **TI-02-DIARIO no tiene fila en ningún
sprint** y llega tarde por construcción, **el SPRINT-03 del backend no publica Yahoo/Stooq ni cripto** (sólo FRED y OAS), y
**la tarea programada del publicador MT5 está desactivada** por el bloqueo de la cuenta. · Cambios desde la revisión del
2026-11-10: SPRINT-02 cerrado con arrastres (`8c50bf7`), S02-5 y S02-6 en `next/SPRINT.md`, fila 7 al backlog (`96ed9c0`),
umbrales de TS-00-OBJ confirmados (quantdesk `3077fddd`), OC-03 servida (backend `cc1811d`), network concilia con D7 (`85c4708`).

Notas de lectura: «lista» = aceptación ejecutable, dependencias y dueño fijados; el nivel L1–L10 de las filas nuevas es
propuesto y lo fija la raíz al planificar. El código de las fichas de [issues/](../issues/index.md) lo revisa otro revisor:
aquí sólo se clasifican por lo que dice este índice.

| Tarea | Clasificación | Evidencia / motivo | ¿Lista para SPRINT-03? (nivel, dependencias, puerta) |
|---|---|---|---|
| LAB-00-ENV | HECHO (SPRINT-01) y re-fijado = S02-1 (DUPLICADO en `next/SPRINT.md`) | `a581355`…`ee7454e`; S02-1 en §0 de `next/SPRINT.md` | S02-1 sin nivel en `next/SPRINT.md` (proponer L4); depende de quantdesk SPRINT-02 cerrado (E-RELEASE-WF-probes sin entregar el 2026-11-11) |
| TI-01-INV, TI-13-PUB (corpus), TI-02-DATA, TI-02-DATA-DEUDA, TS-00-PREC (base), TS-00-BENCH (base), TS-00-OBJ, TI-12-MT5 fases A, B y C | HECHO | §2.3; TS-00-OBJ confirmada el 2026-11-13 (quantdesk `3077fddd`) | No entran (constancia) |
| TI-02-DATA-V2 | HECHO (antes «SPRINT-02 fila 1b») | `27cfb2b`…`3e35ed5`, cierre `778d0e3`; `descarga_lago.py:65` `TOPICS_DEFECTO = (TOPIC_OHLCV,)` (v2) y selftest `:627`; `:991` rechaza v1 | No entra |
| Repetir el banco FX sobre el 1d de MT5 / ISSUE-LAGO-FX-1D-CLOSE | HECHO | `f0995d0`, `d6bc45d`, `778d0e3`; datasets `sha256:a5015bc9…893da` y `sha256:47d79b39…67d32`; ningún modelo cambia de conclusión | No entra |
| TS-00-BENCH (FinCast) | HECHO (antes DUPLICADO en SPRINT-02 fila 2b) | `f3f8a4d`…`05c27cf`, cierre `09befb8`; 1,72 s CPU/origen en FX frente a 6,70 s de Toto: la nota «7 veces Toto» es OBSOLETA | No entra |
| TS-00-BENCH (HMM causal, FG-16-hmmcop) / TS-00-PREC (FG-16-hmmcop) / TI-02-DATA (universo59) | DUPLICADO (S02-2, S02-3, S02-4) | `next/SPRINT.md` §0 | Dependen de quantdesk SPRINT-02 (E15-filter, FG-16-hmmcop, G-MKT05-RAW-a); S02-2 y S02-4 dependen además de la fila 1b, ya cerrada. Niveles por fijar |
| TS-00-BENCH (GPU) | DUPLICADO (`next/SPRINT.md` fila 5) y MODIFICADO | Sólo Chronos-2/Toto a gran escala: FinCast no la necesita (GAP-BACKLOG_README-05) | Depende de DL-02-GATES (quantdesk SPRINT-03, ola 2); «si procede» |
| TI-09-ARCH (parte laboratorio) | HECHO (antes VIGENTE) | `c6c7b5b`, `a62d78f`, `a80ad40`; `oc03_s20261112_c20261113` `sha256:eb98ac6a…eea1` (comprobado en su `informe.md`) | No entra |
| TI-09-ARCH (medición de cobertura) = S02-6 | VIGENTE (DUPLICADO en `next/SPRINT.md`) | Aceptación «≥ 98 % de días hábiles o causa documentada» y «dos lecturas, mismo SHA-256». Con 20 días, 98 % equivale a 20 de 20: un solo día sin captura completa obliga a causa documentada. Falta fijar «día completo» (regla del backend: `capture_id` con ≥ 95 % del universo) | **Lista** (L5): fecha posterior al 2026-12-10 y `QN_TOKEN` nuevo (puerta de usuario); no depende de `quantdesk` |
| TI-09-SONDA | VIGENTE (ficha abierta) | La sonda de contraste del 2026-11-13 (token 39, revocado) midió agregados, no la cifra por día desde el 2026-11-09; STATUS aún dice «vacíos» (C-BACKLOG_README-12) | **Lista** (L2, sin código): misma puerta de token que S02-6; proponer unirla a S02-6 (mismo volcado) |
| TI-12-MT5 (más símbolos y periodos) = S02-5 | VIGENTE (DUPLICADO en `next/SPRINT.md`) | h1 de `@continuo`, sin símbolos nuevos (usuario, 2026-11-11); el parquet de `D:/dev/deeplearning_dev` cubre 28 de 194 y no sirve (2026-11-13) | **Casi lista** (L6): falta fijar rango, ritmo máximo de peticiones y número de series por sesión; puerta: desbloqueo de la cuenta MT5; mutex del terminal con INTRA-LOCAL; no depende de `quantdesk` |
| TI-12-MT5-INTRA-LOCAL (ficha) | VIGENTE, parcial | Primera descarga `continuo_m1m5_20261109` (`sha256:5cd9bf86…`); sin commits del extractor desde el 2026-11-10; criterios 2, 4 y 6 sin hacer; el margen de m1 en cripto (9,9 semanas) se agota hacia el 2027-01-17 | **Lista** (L4) si se confirma que el extractor añade a un dataset existente (SIN VERIFICAR: la reanudación se prueba dentro de una descarga, no entre dos); puerta: cuenta MT5; urgente por fecha |
| TI-12-MT5-SYNC y VELA-A-MEDIAS (fichas) | MODIFICADO: mayormente HECHO | `2ac3f8f`, `9e2a9eb`, `b9cbbbe`, `d6d7a55` (criterios 1–5); queda reactivar la tarea (criterio 7) y la carga de `@continuo` (6); las casillas de SYNC siguen sin marcar | **No es fila de sprint:** fusionar y cerrar salvo el 7 (L1, puerta de usuario: cuenta MT5) |
| TI-12-MT5 (tarea programada del publicador) | MODIFICADO (HECHO → «registrada pero desactivada») | `6c02490` la registra; `1fff755` y VELA-A-MEDIAS §3 la dejan desactivada hasta que acabe el bloqueo (SIN VERIFICAR hoy) | Puerta de usuario; condiciona TI-02-DIARIO (sin 1d nuevo de MT5 no hay FX diario nuevo) |
| TI-12-MT5 (publicar el universo ampliado en qn) | VIGENTE, aplazado, **sin fila de sprint ni ficha** | Noche 1 aplazada (D1); noche 2 espera a network y al usuario; plan nocturno del 2026-11-09 (≤ 40 000 objetos/5 min, 02:00–05:00 CET) | **No lista:** necesita cerrar SYNC, cuenta MT5, visto bueno de network y aviso al backend; sin aceptación propia. Se escribe la ficha al desbloquear (L4) |
| TI-12-MT5 (intradía en qn) | VIGENTE, condicionado | «Se pide al planificar SPRINT-04»; consumidor TS-05-FREQ | **No entra:** visto bueno de network y consumidor en SPRINT-04; sólo cabe una petición escrita a network |
| TI-13-PUB (consumo del mercado público) | VIGENTE, bloqueado | Backend `next/SPRINT.md` §2 y §5: PUB-03 (Yahoo/Stooq) y PUB-04 (cripto) sin sprint; sólo FRED y OAS (topic sin decidir, GAP-PUB-01) | **No entra** (C-BACKLOG_README-09); sólo se activaría para FRED/OAS cuando existan en qn |
| TI-13-PUB (mercado público: publicación) | MOVER a quantdesk-backend (confirmado) | `PLAN_PUBLICADORES_MERCADO_PUBLICO`; GAP-PUB-04 del backend = GAP-BACKLOG_README-03 | — |
| TI-02-DIARIO | VIGENTE, **sin fila de sprint** | Dueño D6; la fila de `quantdesk/docs/plans/DEPENDENCIAS.md` lo exige «antes de la ola 1 de SPRINT-03 de `quantdesk`» y SPRINT-03 del laboratorio llega después (C-BACKLOG_README-10) | **No lista:** falta ficha (GAP-BACKLOG_README-10); L5–L6 propuesto; depende de PUB-02 del backend (OAS) y de la tarea del publicador MT5 activa |
| Binance congelado (§5 de PLAN_DATOS_VIA_QN) | VIGENTE, sin tarea | Decisión del 2026-11-09; no se rehace | No entra |
| TS-02-DISC, ejecuciones de entrenamiento, adaptadores walk-forward | DUPLICADO (`next/SPRINT.md` fila 4; `future/SPRINT-04`) | Sin cambios | Según su sprint; fuera de la petición «backlog en SPRINT-03» salvo TS-02-DISC (depende de TS-02-GEN, ola 3 condicionada) |

GAPs al redactar la revisión: GAP-BACKLOG_README-03, GAP-BACKLOG_README-05, GAP-BACKLOG_README-09, GAP-BACKLOG_README-10.
**Tras las decisiones del usuario del 2026-11-13** (sección siguiente): -09 y -10 resueltos; -03 y -05 siguen abiertos,
diferidos.
- **GAP-BACKLOG_README-03 — Acciones US y cripto por dos publicadores** (sigue abierto, **diferido**: = GAP-DATOS_VIA_QN-09,
  dos publicadores, sin sprint; se pregunta al planificar la fila que lo necesite; es GAP-PUB-04 del backend). ¿MT5 como
  única referencia en acciones y cripto, MT5 en FX/metales/índices y Yahoo/Stooq en acciones, o ambas con su `source`?
  Ahora pesa más «sólo MT5»: el backend dejó PUB-03/PUB-04 sin sprint y la cuenta MT5 es el cuello de botella; contra: las
  acciones de MT5 son CFD con `-24` y sin ajuste por dividendos. Sin decidir, TI-13-PUB (consumo) no tiene alcance.
- **GAP-BACKLOG_README-05 — GPU para el banco** (sigue diferido y **más pequeño**): FinCast cuesta 1,72 s por origen en CPU,
  menos que Toto (6,70 s), así que la nota antigua «FinCast 7 veces Toto» queda corregida; sólo queda Chronos-2/Toto a gran
  escala (fila 5 de §3 de [future/SPRINT-04](../future/SPRINT-04/SPRINT.md), antes `next/SPRINT.md`). Se reevalúa al cerrar
  DL-02-GATES.
- ~~**GAP-BACKLOG_README-09 — Cómo se ejecuta lo que no depende de `quantdesk`**~~ **RESUELTO (usuario, 2026-11-13, revisión
  de planes, R1):** opción (a), partir: SPRINT-03 sin dependencia de entrada con lo que no depende de `quantdesk`, SPRINT-04
  con lo que sí (tras quantdesk SPRINT-03) y la escalera renumerada a SPRINT-05. Texto histórico (nuevo; es la pregunta 1 de `GUARDIA.md`).
  SPRINT-03 no puede activarse hasta que cierre quantdesk SPRINT-03, pero S02-5, S02-6, TI-02-DIARIO, INTRA-LOCAL, SYNC y la
  sonda no dependen de él (INTRA-LOCAL tiene fecha dura hacia el 2027-01-17). Opciones: (a) repetir el precedente del
  2026-11-11: partir SPRINT-03 en uno sin dependencia de entrada y otro con ella; (b) encargos fuera de sprint, registrados como
  en un sprint; (c) esperar a SPRINT-03 entero.
- ~~**GAP-BACKLOG_README-10 — Contrato de TI-02-DIARIO**~~ **RESUELTO (usuario, 2026-11-13, revisión de planes, R5):** el
  contrato se acuerda por mensaje con el backend como primera fila del SPRINT-03 nuevo (dónde corre, ruta, formatos incluido
  `desktop.daily-ohlcv/v1`, series OAS, credencial) y se registra en GOBERNANZA y DEPENDENCIAS; el contenido del contrato
  sigue **pendiente de acordar**. Texto histórico (nuevo). ¿Dónde corre el exportador (el Dagster del backend es Linux; los
  scripts del laboratorio asumen Windows y `E:/`), qué ruta y qué datasets abre `quantdesk`, y con qué credencial lee qn? Sin esto el
  backend no puede programarlo (su PUB-05-EXPORT) ni quantdesk planificar XVA-03-DATA.

Contradicciones: C-BACKLOG_README-09 a -12 (detalle en el informe de la revisión). **Todas resueltas el 2026-11-13**
(sección siguiente): -09 por R6, -10 por R1 y R5, -11 y -12 por regla.
- **C-BACKLOG_README-09 — ¿Qué publica el SPRINT-03 del backend?** SPRINT-02 EXECUTION (2026-11-11, mensaje de
  `quantdesk-backend-fe`) y PLAN_DATOS_VIA_QN (cabecera de cierre) dicen que Yahoo/Stooq, FRED, cripto y OAS están en él; el
  backend `next/SPRINT.md` §2 y §5 deja PUB-03 y PUB-04 fuera. Afecta a TI-13-PUB (consumo). **Resuelta (usuario,
  2026-11-13, revisión de planes, R6):** vale el `next/SPRINT.md` del backend; TI-13-PUB consume FRED/OAS en SPRINT-03 y
  Yahoo/Stooq y cripto quedan en el backlog; se avisa al backend de la discrepancia con nuestro EXECUTION de SPRINT-02 (lo
  hace la raíz por mensaje).
- **C-BACKLOG_README-10 — Plazo de TI-02-DIARIO.** **Resuelta (usuario, 2026-11-13, revisión de planes, R1 y R5):** SPRINT-03
  sin dependencia de entrada y TI-02-DIARIO como su primera fila. Debe existir antes de la ola 1 de SPRINT-03 de `quantdesk`
  (`quantdesk/DEPENDENCIAS.md`, este §3.2) y no tiene fila en ningún sprint del laboratorio; SPRINT-03 del laboratorio empieza
  después de esa ola.
- **C-BACKLOG_README-11 — Estado de la tarea programada.** «Registrada por el usuario» (§2.3, PLAN_DATOS_VIA_QN, DEPENDENCIAS)
  frente a «desactivada hasta que acabe el bloqueo» (VELA-A-MEDIAS §3). **Resuelta por regla:** estaba activa y fallando;
  la raíz de guardia la desactivó el 2026-11-13 (R2).
- **C-BACKLOG_README-12 — Derivados atrasados** (los rehace el orquestador; **resuelta por regla**: STATUS, `index.md` y
  DEPENDENCIAS rehechos en la aplicación de la revisión del 2026-11-13): `STATUS.md` (cadenas «vacías» frente a la sonda del
  2026-11-13; «descarga en curso» de m1/m5; ISSUE-LAGO-FX-1D-CLOSE «abierta»), `index.md` (fila del backlog «lo pendiente en
  SPRINT-02…04»; fila de PLAN_DATOS_VIA_QN con TI-02-DATA-V2 «en SPRINT-02»), `DEPENDENCIAS.md` (filas de TI-13-PUB «SPRINT-02 fila 7»
  y de TI-09-ARCH «pendiente»).

Sinergias: S02-5, INTRA-LOCAL y la republicación comparten el terminal MT5 y la misma puerta (cuenta), y conviene una sola
ventana de descargas prudentes; S02-6 y TI-09-SONDA, el mismo token y volcado; TI-02-DIARIO reutiliza `exportar_market_history_lib`
y `descarga_lago.py` de TI-02-DATA-V2 y comparte el calendario del backend (PUB-02, PUB-05-EXPORT); la cobertura de S02-6
alimenta TS-16-QCONO y TS-08-DYN de `PLAN_TSFM_FINANZAS`; network `PLAN_COPIA_PERIODICA_LAGO` (COP-02/03/08) condiciona
cualquier uso de `lake delete` sobre `market.*`.

## Decisiones del usuario (2026-11-13, revisión de planes)

Fuente de todas: usuario, 2026-11-13, revisión de planes (registro en [REVISIONES.md](REVISIONES.md)). Citar como
«(usuario, 2026-11-13, revisión de planes, Rn)».

| Decisión | Resuelve | Efecto en el laboratorio |
|---|---|---|
| R0 Petición | — | Meter en el sprint siguiente S02-5, S02-6, todos los planes del backlog y todas las issues pendientes; se cumple con R1 (lo que depende de `quantdesk` va a SPRINT-04, el intradía en qn a SPRINT-05, Yahoo/Stooq/cripto al backlog) |
| R1 Partir en dos sprints | GAP-BACKLOG_README-09; C-BACKLOG_README-10 (con R5); (C-ARCHIVO_OPCIONES-04, C-ISSUES-05, GAP-ARCHIVO_OPCIONES-06, GAP-DATOS_VIA_QN-07, GAP-ISSUES-04) | [next/SPRINT.md](../next/SPRINT.md) = SPRINT-03 nuevo, sin dependencia de entrada; [future/SPRINT-04](../future/SPRINT-04/SPRINT.md) = filas S02-1…S02-4 y ciclo sintético-real (← quantdesk SPRINT-03); [future/SPRINT-05](../future/SPRINT-05/SPRINT.md) = escalera (← quantdesk SPRINT-04). Regla «sprint N = sprint N de `quantdesk`» enmendada: desde SPRINT-03, N+1 del laboratorio = N de `quantdesk` |
| R2 Publicador | C-BACKLOG_README-11 (por regla); (GAP-DATOS_VIA_QN-05, GAP-ISSUES-03, C-DATOS_VIA_QN-05, C-ISSUES-01) | Tarea `quantdesk\publicador_mt5` desactivada por la raíz de guardia el 2026-11-13 hasta el desbloqueo; se reactiva en SPRINT-03 fila 4c; backend avisado del FX 1d de MT5 parado desde el 2026-11-10 |
| R3 SYNC | (GAP-ISSUES-02, C-DATOS_VIA_QN-08, C-ISSUES-02) | ISSUE-TI12-MT5-SYNC cerrada fusionando VELA-A-MEDIAS; archivadas en [archive/FUERA-SPRINT_2026-11-09_2026-11-13/](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/ARCHIVE_MANIFEST.md); lo que queda pasa a la fila 4c |
| R4 Sonda | (GAP-ISSUES-01, GAP-ARCHIVO_OPCIONES-04, C-ARCHIVO_OPCIONES-05, C-ISSUES-04) | La sonda se cierra con la cifra por sesión de S02-6 desde el 2026-11-12 (fila 3); 2026-11-09…11 no medibles; STATUS corregido ya; aviso a `quantdesk` |
| R5 TI-02-DIARIO | GAP-BACKLOG_README-10; C-BACKLOG_README-10 (con R1); (GAP-DATOS_VIA_QN-06, -07; C-DATOS_VIA_QN-06, -07) | Primera fila de SPRINT-03: contrato por mensaje con el backend; después el código sin OAS (fila 2); los OAS cuando el backend los publique (fila 7). Antes de la ola 1 de quantdesk SPRINT-03 |
| R6 TI-13-PUB | C-BACKLOG_README-09 | Consumo dividido: FRED/OAS en SPRINT-03 (fila 6, dependencia de tarea del backend SPRINT-03); Yahoo/Stooq y cripto en el backlog |
| R7 Intradía MT5 en qn | (GAP-DATOS_VIA_QN-10) | Se planifica con el sprint de entrenamiento (SPRINT-05), consumidor TS-05-FREQ |
| R8 INTRA-LOCAL | (GAP-ISSUES-04 y D3b, periodicidad y acciones) | fx28 y `@continuo` primero, después las 484 acciones (≈ 3,1 GiB), una serie cada vez; manual cada ≤ 6 semanas, la primera antes del 2027-01-17; sin tarea programada; fila 4b, fusionada con S02-5 |
| Por regla | C-BACKLOG_README-11, C-BACKLOG_README-12 | Estado real de la tarea programada; derivados (STATUS, `index.md`, DEPENDENCIAS) rehechos |

GAPs que siguen abiertos en este índice (diferidos): GAP-BACKLOG_README-03 (= GAP-DATOS_VIA_QN-09, dos publicadores, sin
sprint) y GAP-BACKLOG_README-05 (GPU, diferido; nota de FinCast corregida: 1,72 s frente a 6,70 s de Toto). Contradicciones
abiertas: ninguna.

[PLAN_TSFM_FINANZAS]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md
[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
[PLAN_XVA_BANCARIO]: S:/projects/quantdesk/docs/plans/backlog/PLAN_XVA_BANCARIO.md
[PLAN_DEEP_LEARNING_GPU]: S:/projects/quantdesk/docs/plans/backlog/PLAN_DEEP_LEARNING_GPU.md
