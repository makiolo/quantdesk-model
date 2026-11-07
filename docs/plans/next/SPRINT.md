# SPRINT-01 — Entorno, datos reales y banco de referencia

**Estado:** En planificación
**Inicio de planificación:** 2026-11-07
**Inicio:** pendiente
**Fin:** pendiente

## 1. Objetivo

Lo que el laboratorio puede hacer **ya**, en paralelo a SPRINT-02 de `quantdesk` y sin tocarlo (decisión del
usuario, 2026-11-07). Al terminar, el usuario tiene un entorno propio y reproducible, el inventario del lago, el
archivo diario de cadenas de opciones en marcha, datos reales (lago, MT5, fuentes públicas) exportados a
`engine.market-history/v1` con hash, y la primera tabla del banco (HMM, GARCH, Chronos-2, Toto) con la que fijar
los umbrales de éxito del modelo.

## 2. Responsabilidades y gobernanza

Filas de [GOBERNANZA.md](../GOBERNANZA.md) que afectan a este sprint.

| Cosa | Dueño | Escribe | Decide | Cambios desde otro proyecto |
|---|---|---|---|---|
| Backlog, sprints, `.venv`, `requirements.lock`, datasets, informes del banco | quantdesk-model | sesiones del laboratorio | usuario | issue en este repo |
| `PLAN_TSFM_FINANZAS` / `PLAN_TSFM_INTEGRACION` (umbrales de TS-00-OBJ, decisiones) | quantdesk (backlog) | el laboratorio registra allí las decisiones del usuario, con enlace al informe | usuario | edición directa del plan; nunca `current/` ni código de quantdesk |
| Rueda de `quantdesk`, `data_py`, bindings HMM | quantdesk | quantdesk | usuario | tarea en el backlog de quantdesk |
| Scraper de cadenas (OC-*) / esquema y retención del topic (OCS-*) | backend / network | sus sesiones | usuario | sus planes de backlog |
| Credenciales (MT5, `QN_TOKEN`) | usuario | usuario | usuario | nunca en repo, informes ni chat |

## 3. Tareas

Especificación y aceptación: [PLAN_TSFM_INTEGRACION] §5 (TI-*) y [PLAN_TSFM_FINANZAS] §5 fase 0 (TS-00-*);
comprobaciones previas en [backlog §2.1](../backlog/README.md#21-comprobaciones-2026-11-07).

| Orden | ID | Nivel (plan) | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|---|
| 1 | **LAB-00-ENV** | — | `.venv` propio (Python 3.12) con las ruedas de `quantdesk` construidas desde un commit fijo (GAP-03: `quantdesk`, `data-py`, `market-py` y las que el banco importe), `pyarrow`, `ml_dtypes`, `arch`, `MetaTrader5`, `torch` (CPU) y `chronos-forecasting`; `requirements.lock`; almacén `E:/quantdesk-lab/` creado y `HF_HOME`/`PIP_CACHE_DIR` apuntando a él (GAP-02) | `pip install -r requirements.lock` en un venv limpio reproduce el entorno; ninguna caché ni descarga escribe en C:; prueba de humo importa todo y repite la comprobación HMM de §2.1 (calibrar + `open_stream`) en el `.venv`; la versión del motor queda registrada. Nada se instala en el venv de `quantdesk` | — |
| 2 | **TI-01-INV** | L3 | Ejecutar `scripts/inventario_options_chain.py` (hecho) y extenderlo al resto de topics `market.*` | Informe con cifras y consultas reproducibles por topic (instrumentos, profundidad, frecuencia, huecos, calidad); GPU en los nodos de la flota | — (**puerta de usuario:** ejecutarlo con su token `QN_TOKEN`) |
| 3 | **TI-09-ARCH** (parte laboratorio) | L5, urgente | Instantánea diaria de `market.options.chain` desde el lago al almacén del laboratorio, cruda y limpia (mid, filtro de arbitraje de mariposa y calendario), con hash; aviso si falta un día hábil | Instantánea diaria con hash y filtro documentado; aviso de día hábil ausente probado. Mientras no exista OC-03 (captura al cierre, backend): última captura de cada día con su hora; sin spot en la fila, subyacente del OHLCV diario. La cobertura ≥ 98 % del plan se mide en el mes siguiente (SPRINT-02) | TI-01-INV |
| 4 | **TI-12-MT5** | L6 | Extractor MetaTrader 5 de solo lectura: inventario de símbolos y profundidad por periodo, descarga incremental y reanudable 1 m/5 m (ticks si hay), hora del servidor a UTC, sufijos, huecos de fin de semana, mid frente a bid/ask y spread como serie | Inventario publicado; dos descargas del mismo rango dan el mismo hash; velas de 1 m agregadas a diario cuadran con otra fuente diaria dentro de tolerancia; el extractor nunca envía órdenes. Credenciales fuera del repo y del chat | LAB-00-ENV (el plan cita TI-03-FMT: aquí la procedencia va en fichero adjunto hasta SPRINT-03) |
| 5 | **TI-13-PUB** | L5 | Ingesta pública: corpus genéricos con licencia (Chronos, LOTSA…), Yahoo/Stooq, FRED, cripto; filtro de fugas D-11; sólo subconjuntos dentro del presupuesto de disco (100 GB, GAP-02) | Tabla de licencias (en el laboratorio hasta TI-00-ADR, SPRINT-03); datasets con hash; validación disjunta de entrenamiento; informe del filtro (series excluidas o cortadas) | LAB-00-ENV |
| 6 | **TI-02-DATA** | L6 | Exportador a `engine.market-history/v1` (pyarrow según `data_py.table_schemas_json()`, validado con `data_py.dataset_describe_json`) desde el lago y las fuentes de TI-12/TI-13; universos con sesgo de supervivencia declarado (D-07) | El dataset congelado carga en `quant-data` sin violaciones de look-ahead; dos exportaciones con el mismo corte dan el mismo hash | TI-01-INV, LAB-00-ENV; TI-12/TI-13 a medida que lleguen |
| 7 | **TS-00-PREC** | L6 | Banco de precisión emulado (fp8 e4m3/e5m2, bf16, f16, f32 en CPU con `ml_dtypes`): medidas 1–3 de §4.5 (entrada, inferencia, derivados cono → σ_loc) sobre un transformer pequeño | Tabla por tipo y medida con la dispersión entre semillas como umbral; primera respuesta a «¿basta fp8?» | LAB-00-ENV |
| 8 | **TS-00-BENCH** | L6 | Banco walk-forward sobre el dataset real congelado: HMM actual (bindings), GARCH(1,1) con `arch`, Chronos-2 y Toto zero-shot en CPU; licencias de los pesos verificadas | Tabla por activo y horizonte: CRPS, pinball 0,01/0,99, Kupiec y Christoffersen, QLIKE de vol realizada; semilla, hash del dataset y versión del motor en el informe | TI-02-DATA, LAB-00-ENV |
| 9 | **TS-00-OBJ** | L3, U | Umbrales de éxito por uso (forecast, H1, hedging) con el usuario a la vista del banco | Umbrales aceptados por el usuario y escritos en `PLAN_TSFM_FINANZAS` (GAP-01) con enlace al informe del banco | TS-00-BENCH; **puerta de usuario** |

## 4. Dependencias externas

Ninguna dependencia de sprint en [DEPENDENCIAS.md](../DEPENDENCIAS.md): SPRINT-01 es «lo que se puede hacer ya» y
su activación no espera a nadie. Consume `quantdesk` desde un commit fijo (GAP-03).

Dependencias de tarea (DEPENDENCIAS.md «Dependencias de tarea», decididas por el usuario el 2026-11-07):

| Tarea local | Espera a | Mientras tanto |
|---|---|---|
| TI-09-ARCH, captura al cierre con spot | quantdesk-backend SPRINT-02 OC-03-CLOSE (tras quantdesk-network SPRINT-01 OCS-01) | Última captura de cada día con su hora; subyacente del OHLCV diario |
| TI-09-ARCH, aviso en origen | quantdesk-backend SPRINT-01 OC-01-FAIL, OC-02-ALERT (urgentes, primeras de su sprint) | El aviso de día hábil ausente del laboratorio es la única alarma |
| TI-09-ARCH, duración y retención | quantdesk-backend SPRINT-02 OC-04, OC-05 | Retención sin verificar: el archivo del laboratorio es la copia que no caduca |

El backend adelanta OC-01 y OC-02 a su SPRINT-01 y deja OC-03, OC-04 y OC-05 para su SPRINT-02 (usuario,
2026-11-07). Lo de SPRINT-02 llegará casi seguro después de cerrar este sprint: esa parte de TI-09-ARCH se
planifica en el modo «mientras tanto».

Al cerrar cada OC en el backend, TI-09-ARCH cambia de modo (dentro de este sprint si llega a tiempo; si no, en
SPRINT-02). El cierre de SPRINT-01 no espera a los OC: lo que falte queda como arrastre.

## 5. Decisiones (GAPs)

| GAP | Pregunta | Decisión (quién, fecha) |
|---|---|---|
| GAP-01 | TS-00-OBJ pide «umbrales escritos en este plan» (PLAN_TSFM_FINANZAS, en `quantdesk`). ¿Dónde se escriben? | En `PLAN_TSFM_FINANZAS`: el laboratorio registra allí las decisiones del usuario y los umbrales, con enlace al informe del banco; no toca `current/` ni código de `quantdesk` (GOBERNANZA.md). Usuario, 2026-11-07 |
| GAP-02 | Ruta provisional del almacén de artefactos del laboratorio hasta D-I2 / TI-00-ADR (SPRINT-03) | `E:/quantdesk-lab/` (`data/`, `datasets/`, `runs/`, `artifacts/`, `cache/hf`, `cache/pip`), fuera de Git; LAB-00-ENV fija `HF_HOME` y `PIP_CACHE_DIR` ahí (C: al 99 %). Presupuesto inicial de TI-13-PUB: 100 GB, ajustable; el usuario libera espacio en E:. Usuario, 2026-11-07 |
| GAP-03 | Rueda de `quantdesk` para LAB-00-ENV: la instalación editable actual (`S:/Projects/engine_quant`) o una rueda construida; en ambos casos versión y commit en el lock | Ruedas propias desde un commit fijo: `git archive <commit>` de `S:/projects/quantdesk` a `E:/quantdesk-lab/build/`, compiladas allí con maturin (nunca en la carpeta ni el `target/` de quantdesk), guardadas en `E:/quantdesk-lab/wheels/` con SHA-256 y citadas en el lock con el commit. Commit: el HEAD de quantdesk al empezar LAB-00-ENV (hoy `57f9262c`), sin esperar al cierre de SPRINT-02. Subir de motor es una decisión registrada. Usuario, 2026-11-07 |
| GAP-04 | Paquete de Toto y licencia de sus pesos (no se da por supuesto que esté en PyPI) | se resuelve dentro de TS-00-BENCH |

## 6. Exclusiones

| Qué | Motivo | Destino |
|---|---|---|
| TS-02-DISC (parte laboratorio) | Necesita TS-02-GEN (SPRINT-03 de `quantdesk`, ola 3) | [future/SPRINT-03](../future/SPRINT-03/SPRINT.md) |
| Ejecuciones de entrenamiento, TS-05-*, TS-06-FT, TS-18-WF, TS-15-FINAL | Necesitan TI-06-CLI y DL-07-TRAIN (SPRINT-04 de `quantdesk`) | [future/SPRINT-04](../future/SPRINT-04/SPRINT.md) |
| Cualquier cambio en código o sprints de `quantdesk` o en el scraper del backend | Gobernanza (GOBERNANZA.md, SPRINT_PROJECT §5) | backlog de cada repo |
| GPU para Chronos-2/Toto | PyTorch con ROCm en Windows no se da por supuesto; carriles DL-02-GATES aún no existen | CPU ahora; GPU en SPRINT-03 si procede |

## 7. Orden, carriles y mutex

- **LAB-00-ENV primero**: barrera para todo lo que importe paquetes nuevos.
- Carril datos: TI-01-INV → TI-09-ARCH (diaria desde que exista, cada día perdido es irrecuperable);
  TI-12-MT5 y TI-13-PUB en paralelo → TI-02-DATA (exporta primero el lago y añade fuentes al llegar).
- Carril banco: TS-00-PREC en paralelo desde LAB-00-ENV; TS-00-BENCH tras el primer dataset congelado de TI-02-DATA;
  TS-00-OBJ al final.
- Mutex: `requirements.lock` (sólo LAB-00-ENV y quien añada dependencias, en serie); el esquema del dataset exportado
  (sólo TI-02-DATA).

## 8. Definition of Done

- Selftest de cada script en verde (SPRINT_PROJECT «Comandos»); suite completa en verde.
- Cada dataset e informe con hash SHA-256, semilla, fecha de corte y versión del motor; commit de cierre por tarea
  (los datasets y artefactos no van a Git: el informe cita su ruta y hash).
- Ninguna credencial ni token en el repo, informes o prompts.
- STATUS.md, backlog e issues actualizados.

## 9. Capacidad y presupuesto

Suscripciones compartidas con `quantdesk` (SPRINT-02 activo), sin tope ni reserva de cuota para ninguno de los dos
(usuario, 2026-11-07, SPRINT_PROJECT §7). Antes de cada lanzamiento se lee la cuota semanal restante
(`claude-or quota --weekly`) y se registra en el LAUNCH; si no alcanza para la ola, se espera al reinicio en lugar de
recortar el alcance. Tareas L3–L6, sin GPU; el tiempo de pared lo dominan las descargas (MT5, públicas) y el
zero-shot en CPU, no los tokens.

[PLAN_TSFM_FINANZAS]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md
[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
