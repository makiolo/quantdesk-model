# Backlog del laboratorio (`quantdesk-model`)

Planes individuales futuros, uno por tema (`PLAN_<TEMA>.md`), sin sprint asignado. Cada plan lleva
estado, estado verificado, opciones, fases o tareas con aceptación verificable, dependencias, riesgos
y preguntas abiertas. `sprint planificar` los refresca contra el código y agrupa sus tareas en
`next/` o en un `future/SPRINT-NN/`; los documentos de visión permanentes (p. ej. `ROADMAP.md`) se
refrescan pero no se fusionan. Listado y estado de cada plan: tablero [index.md](../index.md).

> **Origen:** contenido íntegro de `docs/plans/BACKLOG.md` (2026-11-07), trasladado aquí al instalar los sprints; esa ruta queda como puntero. **Asignación a sprints** (usuario, 2026-11-07): el sprint N del laboratorio es «lo que se puede hacer cuando termine el sprint N de `quantdesk`», salvo SPRINT-01, que es lo que se puede hacer ya: [next/SPRINT.md](../next/SPRINT.md) (SPRINT-01), [future/](../future/README.md) (SPRINT-02…04) y [DEPENDENCIAS.md](../DEPENDENCIAS.md).

**Fecha:** 2026-11-07. Los planes de diseño viven en el backlog de `quantdesk`
(`S:/projects/quantdesk/docs/plans/backlog/`): [PLAN_TSFM_FINANZAS], [PLAN_TSFM_INTEGRACION], [PLAN_XVA_BANCARIO] y
[PLAN_DEEP_LEARNING_GPU]. Este fichero recoge **lo que se ejecuta aquí** y el calendario de todo.

## 1. Regla de separación

| Va al backlog de `quantdesk` | Va al backlog del laboratorio (este) |
|---|---|
| Código que se ejecuta en producción: Rust/C++ (`engine-core`, `engine-nn`, `quant-data`, `quant-domain`), FinDSL, contratos, desktop, gates | Adquisición y exportación de datos, datasets congelados con hash, bancos y referencias externas en Python, configuraciones de ejecuciones, informes, fichas de modelo, almacén de artefactos |
| Se planifica y ejecuta en los sprints de `quantdesk`, con sus gates y revisión | No depende de los sprints de `quantdesk` ni de `rust-target`; usa `quantdesk` solo como consumidor (rueda Python, CLI) |
| Los IDs y su especificación siguen en los planes de `quantdesk` | Mismos IDs; aquí se registra su ejecución |

Límites: el laboratorio no escribe código Rust ni modifica `quantdesk`; si una tarea necesita algo del motor que no está
expuesto, se pide como tarea de `quantdesk`. La GPU se usa respetando los carriles de DL-02-GATES cuando existan.

## 2. Tareas del laboratorio

| ID | Qué se hace aquí | Cuándo | Notas |
|---|---|---|---|
| **LAB-00-ENV** | Entorno propio del laboratorio (`quantdesk-model/.venv`, Python 3.12): rueda de `quantdesk` fijada por versión, `pyarrow`, `ml_dtypes`, `arch`, `MetaTrader5`, `torch` (CPU para el zero-shot) y `chronos-forecasting`; versiones congeladas en un `requirements.lock` | **Ya**, primero | Ver §2.1. No instalar en el venv de `quantdesk`: lo cambian sus sprints y el banco debe registrar qué versión del motor usó |
| **TI-01-INV** | Inventario del lago: `scripts/inventario_options_chain.py` (hecho) y el resto de topics `market.*` | **Ya** | Falta ejecutarlo con el token del usuario |
| **TI-09-ARCH** (parte laboratorio) | Instantánea diaria de `market.options.chain` desde el lago al almacén del laboratorio, cruda y limpia (mid, filtro de arbitraje), con alerta si falta un día hábil | **Ya** | El scraper se arregla en `quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md` (OC-01…OC-05). Mientras no exista la captura al cierre (OC-03), quedarse con la última captura de cada día y guardar su hora; sin spot en la fila, el subyacente sale del OHLCV diario |
| **TI-12-MT5** | Extractor MetaTrader 5: inventario, descarga incremental 1 m/5 m (ticks si hay), hora a UTC, solo lectura | **Ya** (tras LAB-00-ENV) | Credenciales fuera del repo; el paquete `MetaTrader5` no está instalado |
| **TI-13-PUB** | Ingesta pública: corpus genéricos con licencia, Yahoo/Stooq, FRED, cripto; filtro de fugas | **Ya** | Licencias en una tabla |
| **TI-02-DATA** | Exportador a `engine.market-history/v1` (pyarrow según `data_py.table_schemas_json()`, validado con `data_py.dataset_describe_json`) | **Ya** | El campo de procedencia sintética (TI-03-FMT) llega en SPRINT-03; los datos reales no lo necesitan |
| **TS-00-PREC** | Banco de precisión emulado (fp8/bf16/f16/f32 en CPU) | **Ya** (tras LAB-00-ENV) | `ml_dtypes` no está instalado (hay 0.6.0 en PyPI) |
| **TS-00-BENCH** | Banco walk-forward: HMM actual, GARCH, Chronos-2 y Toto en zero-shot | **Ya** (tras TI-02-DATA y LAB-00-ENV) | HMM expuesto y probado (§2.1), sin tarea en `quantdesk`. GARCH con `arch`; Chronos-2/Toto con `torch` en CPU (PyTorch con ROCm en Windows no se da por supuesto) |
| **TS-00-OBJ** | Umbrales de éxito con el usuario | Tras TS-00-BENCH | Decisión del usuario |
| **TS-02-DISC** (parte laboratorio) | Clasificador real frente a sintético e informe de rasgos que faltan | Tras SPRINT-03 (necesita TS-02-GEN) | — |
| Ejecuciones de entrenamiento | Configuraciones `engine.train-request/v1`, escalera 4 M → 20 M → 80 M, ablaciones (TS-05-PREC/PRE/FREQ), recibos e informes | Tras SPRINT-04 (necesita TI-06-CLI y DL-07-TRAIN) | El código de entrenamiento es de `quantdesk` |
| Adaptadores walk-forward | Ejecuciones trimestrales y mensuales de TS-18-WF | Tras SPRINT-04 | — |

### 2.1 Comprobaciones (2026-11-07)

- **HMM desde Python: sí.** `quantdesk.Engine.calibrate(Hmm, ObservedSeries, HmmCalibrationOptions)` calibra con
  Baum-Welch y `Engine.open_stream(res, seed, policy="from_calibration_end").advance_many(dts)` muestrea caminos
  condicionados al final de la calibración. Probado con una serie sintética de 400 días y 200 caminos a 20 días. Un
  camino por stream: para miles de caminos, medir el tiempo antes de pedir una versión vectorizada.
- **Entorno de `quantdesk` (`venv`, Python 3.12.3):** tiene `pyarrow`, `numpy`, `pandas`, `data_py` y `quantdesk`
  (editable desde `S:/Projects/engine_quant`, que es una unión a `S:/Projects/quantdesk`). Le faltan `ml_dtypes`,
  `arch`, `torch` y `MetaTrader5`. De ahí LAB-00-ENV.
- **Scraper de cadenas (`quantdesk-backend`):** yfinance sobre el S&P 500, capturas a las 04, 12 y 20 h de París con
  timeout de 8 h, errores tragados, ninguna captura tras el cierre de EE. UU. y sin precio del subyacente. Plan en el
  backlog del backend (`PLAN_OPTIONS_CHAIN_ARCHIVO`). Retención del topic sin verificar (OC-05-RET).

## 3. Calendario de todo

«Q» = sprint de `quantdesk`; «L» = este laboratorio. Las asignaciones a SPRINT-04 y posteriores son estimaciones por
dependencias; se recalibran al planificar cada sprint.

### 3.1 Ahora (en paralelo a SPRINT-02, sin tocar `quantdesk`)

- **L:** LAB-00-ENV primero; luego TI-01-INV, TI-09-ARCH (parte laboratorio), TI-12-MT5, TI-13-PUB, TI-02-DATA,
  TS-00-PREC, TS-00-BENCH, TS-00-OBJ.
- **Backend (`quantdesk-backend`, su propio sprint):** OC-01…OC-05 de `PLAN_OPTIONS_CHAIN_ARCHIVO`, urgente porque cada
  día sin captura se pierde. OC-03 necesita campos nuevos en el esquema de `market.options.chain` (`quantdesk-network`).
- **Usuario:** ejecutar el inventario con su token; reiniciar la máquina antes de la ola 2 de SPRINT-03.

### 3.2 Cuando termine SPRINT-02 (= SPRINT-03, tres olas en `quantdesk/docs/plans/next/README.md`)

- **Q, ola 1:** TI-00-ADR, TI-03-FMT, TS-01-SIM, TS-11a-RIESGO, XVA-00-ADR, XVA-00-FIX, XVA-01-DOM (tras G-AG64-char de
  SPRINT-02), XVA-03-DATA, XVA-03-CDS, XVA-03-CURVE.
- **Q, ola 2:** DL-00-LT, DL-00-COLA, DL-00-F64, DL-01-ADR, DL-02-GATES, TI-04-EXACT, TI-11-COEX, DL-04-NN.
- **Q, ola 3 (si hay capacidad):** TS-02-GEN, TS-03-ARCH, TS-04-CONO, XVA-02-FINDSL, XVA-03-PROXY, XVA-03-SIM, XVA-04-SIM.

### 3.3 Cuando termine SPRINT-03 (= SPRINT-04)

- **Q, base de entrenamiento e inferencia:** DL-03-CORE (solo MLP), DL-05-FINDSL, DL-06-PREC, DL-07-TRAIN, TI-04-REF,
  TI-05-REQ, TI-06-CLI, TI-14-REG, TI-10-WORKER, y lo que quede de la ola 3.
- **Q, modelo:** TS-05-PREC; arranque de TS-05-PRE si DL-07-TRAIN llega pronto (si no, SPRINT-05).
- **Q, XVA:** XVA-05-REVAL, XVA-06-COLL (sobre G-AG64-impl), XVA-07-CUBE, XVA-10-IM.
- **L:** TS-02-DISC.

### 3.4 Cuando termine SPRINT-04 (= SPRINT-05 en adelante)

- **L:** ejecuciones de la escalera (TS-05-PRE con la prueba de interferencia y el punto de control frente a modelos
  públicos en 20 M), TS-05-FREQ, TS-06-FT, adaptadores de TS-18-WF, TS-15-FINAL.
- **Q, modelo y uso:** TS-06-CAL, TS-07-LV, TS-08-HEDGE, TS-08-DYN, TS-08-STAB, TS-09-CAMINO, TS-10-SLV, TS-10-H2P,
  TS-11b-RIESGO, TS-12-DESK, TS-13-MERCADO, TS-14-CTX, TS-16-QCONO, TS-17-XVA, TS-18-WF (parte motor), TI-07-FINDSL,
  TI-08-SERV.
- **Q, XVA:** XVA-08-CVA, XVA-09-FVA, XVA-10-MVA, XVA-11-KVA, XVA-12-WWR, XVA-13-SENS, XVA-14-INCR, XVA-15-EXPLAIN,
  XVA-16-DESK, XVA-17-ORE.
- **Q, deep learning:** DL-08-QUANT, DL-09-HEDGE, DL-10-ONNX.
- **Usuario:** D-13 (pagar datos de mercado y CDS) cuando el dato real sea el cuello de botella.

[PLAN_TSFM_FINANZAS]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md
[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
[PLAN_XVA_BANCARIO]: S:/projects/quantdesk/docs/plans/backlog/PLAN_XVA_BANCARIO.md
[PLAN_DEEP_LEARNING_GPU]: S:/projects/quantdesk/docs/plans/backlog/PLAN_DEEP_LEARNING_GPU.md
