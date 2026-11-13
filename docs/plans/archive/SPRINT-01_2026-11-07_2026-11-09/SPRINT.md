# SPRINT-01 — Entorno, datos reales y banco de referencia

**Estado:** Cerrado (sin arrastres; TI-09-ARCH retirada por el usuario el 2026-11-08). Cierre en §10.
**Inicio de planificación:** 2026-11-07
**Inicio:** 2026-11-07
**Fin:** 2026-11-09
**Orígenes:** etiqueta `archive/2026-11-07/sprint-01-sources` (commit `b9b576d`); planes de `quantdesk` en `af941862`
(`PLAN_TSFM_FINANZAS`, `PLAN_TSFM_INTEGRACION`, sólo lectura). Los planes de backlog del laboratorio no se consumen:
la especificación vive en `quantdesk` (GOBERNANZA).
**Medición:** coordinador de costes, la raíz del LAUNCH. Lectura inicial (`claude-or quota --weekly`, 2026-11-07,
fuente api): Claude semanal 38 % consumido con el 69,6 % de la ventana (reinicio 2026-11-10 00:00 UTC); Codex
semanal 36 % con el 51,4 % (reinicio 2026-11-11 06:41 UTC). Cuota compartida con `quantdesk` SPRINT-02 (activo).

## 1. Objetivo

Lo que el laboratorio puede hacer **ya**, en paralelo a SPRINT-02 de `quantdesk` y sin tocarlo (decisión del
usuario, 2026-11-07). Al terminar, el usuario tiene un entorno propio y reproducible, el inventario del lago, el
archivo diario de cadenas de opciones en marcha, datos reales (lago, MT5, fuentes públicas) exportados a
`engine.market-history/v1` con hash, y la primera tabla del banco (HMM, GARCH, Chronos-2, Toto) con la que fijar
los umbrales de éxito del modelo.

## 2. Responsabilidades y gobernanza

Filas de [GOBERNANZA.md](../../GOBERNANZA.md) que afectan a este sprint.

| Cosa | Dueño | Escribe | Decide | Cambios desde otro proyecto |
|---|---|---|---|---|
| Backlog, sprints, `.venv`, `requirements.lock`, datasets, informes del banco | quantdesk-model | sesiones del laboratorio | usuario | issue en este repo |
| `PLAN_TSFM_FINANZAS` / `PLAN_TSFM_INTEGRACION` (umbrales de TS-00-OBJ, decisiones) | quantdesk (backlog) | el laboratorio registra allí las decisiones del usuario, con enlace al informe | usuario | edición directa del plan; nunca `current/` ni código de quantdesk |
| Rueda de `quantdesk`, `data_py`, bindings HMM | quantdesk | quantdesk | usuario | tarea en el backlog de quantdesk |
| Scraper de cadenas (OC-*) / esquema y retención del topic (OCS-*) | backend / network | sus sesiones | usuario | sus planes de backlog |
| Credenciales (MT5, `QN_TOKEN`) | usuario | usuario | usuario | nunca en repo, informes ni chat |

## 3. Tareas

Especificación y aceptación: [PLAN_TSFM_INTEGRACION] §5 (TI-*) y [PLAN_TSFM_FINANZAS] §5 fase 0 (TS-00-*);
comprobaciones previas en [backlog §2.1](../../backlog/README.md#21-comprobaciones-2026-11-07).

| Orden | ID | Nivel (plan) | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|---|
| 1 | **LAB-00-ENV** | — | `.venv` propio (Python 3.12) con las ruedas de `quantdesk` construidas desde un commit fijo (GAP-03: `quantdesk`, `data-py`, `market-py` y las que el banco importe), `pyarrow`, `ml_dtypes`, `arch`, `MetaTrader5`, `torch` (CPU) y `chronos-forecasting`; `requirements.lock`; almacén `E:/quantdesk-lab/` creado y `HF_HOME`/`PIP_CACHE_DIR` apuntando a él (GAP-02) | `pip install -r requirements.lock` en un venv limpio reproduce el entorno; ninguna caché ni descarga escribe en C:; prueba de humo importa todo y repite la comprobación HMM de §2.1 (calibrar + `open_stream`) en el `.venv`; la versión del motor queda registrada. Nada se instala en el venv de `quantdesk` | — |
| 2 | **TI-01-INV** | L3 | Ejecutar `scripts/inventario_options_chain.py` (hecho) y extenderlo al resto de topics `market.*` | Informe con cifras y consultas reproducibles por topic (instrumentos, profundidad, frecuencia, huecos, calidad); GPU en los nodos de la flota | — (**puerta de usuario:** ejecutarlo con su token `QN_TOKEN`) |
| 3 | **TI-09-ARCH** (parte laboratorio) · **RETIRADA** (usuario, 2026-11-08: `market.options.chain` vacío en qn según TI-01-INV; vuelve cuando haya datos, ver §6) | L5 | Lector bajo demanda de `market.options.chain` desde el lago (Iceberg en S3, sin retención: decisión 12-A), que produce la instantánea por día hábil cruda y limpia (mid, filtro de arbitraje de mariposa y calendario) para un rango de fechas, y la congela con hash en el almacén del laboratorio al cortar cada dataset. Sin tarea programada ni copia diaria propia | Dos lecturas del mismo rango y corte dan el mismo hash; filtro documentado; informe de días hábiles sin datos en el lago (huecos de origen). Mientras no exista OC-03 (captura al cierre, backend): última captura de cada día con su hora; sin spot en la fila, subyacente del OHLCV diario. La cobertura ≥ 98 % del plan se mide en el mes siguiente (SPRINT-02) | TI-01-INV |
| 4 | **TI-12-MT5** | L6 | Extractor MetaTrader 5 de solo lectura: inventario de símbolos y profundidad por periodo, descarga incremental y reanudable 1 m/5 m (ticks si hay), hora del servidor a UTC, sufijos, huecos de fin de semana, mid frente a bid/ask y spread como serie | Inventario publicado; dos descargas del mismo rango dan el mismo hash; velas de 1 m agregadas a diario cuadran con otra fuente diaria dentro de tolerancia; el extractor nunca envía órdenes. Credenciales fuera del repo y del chat | LAB-00-ENV (el plan cita TI-03-FMT: aquí la procedencia va en fichero adjunto hasta SPRINT-03) |
| 5 | **TI-13-PUB** | L5 | Ingesta pública: corpus genéricos con licencia (Chronos, LOTSA…), Yahoo/Stooq, FRED, cripto; filtro de fugas D-11; sólo subconjuntos dentro del presupuesto de disco (100 GB, GAP-02) | Tabla de licencias (en el laboratorio hasta TI-00-ADR, SPRINT-03); datasets con hash; validación disjunta de entrenamiento; informe del filtro (series excluidas o cortadas) | LAB-00-ENV |
| 6 | **TI-02-DATA** | L6 | Exportador a `engine.market-history/v1` (pyarrow según `data_py.table_schemas_json()`, validado con `data_py.dataset_describe_json`) desde el lago y las fuentes de TI-12/TI-13; universos con sesgo de supervivencia declarado (D-07) | El dataset congelado carga en `quant-data` sin violaciones de look-ahead; dos exportaciones con el mismo corte dan el mismo hash | TI-01-INV, LAB-00-ENV; TI-12/TI-13 a medida que lleguen |
| 7 | **TS-00-PREC** | L6 | Banco de precisión emulado (fp8 e4m3/e5m2, bf16, f16, f32 en CPU con `ml_dtypes`): medidas 1–3 de §4.5 (entrada, inferencia, derivados cono → σ_loc) sobre un transformer pequeño | Tabla por tipo y medida con la dispersión entre semillas como umbral; primera respuesta a «¿basta fp8?» | LAB-00-ENV |
| 8 | **TS-00-BENCH** | L6 | Banco walk-forward sobre el dataset real congelado: HMM actual (bindings), GARCH(1,1) con `arch`, Chronos-2 y Toto zero-shot en CPU; licencias de los pesos verificadas | Tabla por activo y horizonte: CRPS, pinball 0,01/0,99, Kupiec y Christoffersen, QLIKE de vol realizada; semilla, hash del dataset y versión del motor en el informe | TI-02-DATA, LAB-00-ENV |
| 9 | **TS-00-OBJ** | L3, U | Umbrales de éxito por uso (forecast, H1, hedging) con el usuario a la vista del banco | Umbrales aceptados por el usuario y escritos en `PLAN_TSFM_FINANZAS` (GAP-01) con enlace al informe del banco | TS-00-BENCH; **puerta de usuario** |

## 4. Dependencias externas

Ninguna dependencia de sprint en [DEPENDENCIAS.md](../../DEPENDENCIAS.md): SPRINT-01 es «lo que se puede hacer ya» y
su activación no espera a nadie. Consume `quantdesk` desde un commit fijo (GAP-03).

Dependencias de tarea (DEPENDENCIAS.md «Dependencias de tarea», decididas por el usuario el 2026-11-07):

| Tarea local | Espera a | Mientras tanto |
|---|---|---|
| TI-09-ARCH, captura al cierre con spot | quantdesk-backend SPRINT-02 OC-03-CLOSE (tras quantdesk-network SPRINT-01 OCS-01) | Última captura de cada día con su hora; subyacente del OHLCV diario |
| TI-09-ARCH, aviso en origen | quantdesk-backend SPRINT-01 OC-01-FAIL, OC-02-ALERT (urgentes, primeras de su sprint) | El informe de huecos del laboratorio es la única señal, y llega tarde |
| TI-09-ARCH, lectura bajo demanda | quantdesk-network SPRINT-01 OCS-02 (garantía de S3 sin retención) | Se lee del lago igualmente; hasta OCS-02 la no-caducidad es una revisión de código, no una garantía |

Decisión 12-A (usuario, 2026-11-07): todo lo que pasa por qn acaba en S3 sin retención, así que el laboratorio no
copia a diario; lo irrecuperable es lo que el scraper no captura (OC-01/OC-02). El backend adelanta OC-01 y OC-02 a
su SPRINT-01 y deja OC-03 para su SPRINT-02, que llegará casi seguro después de cerrar este sprint.

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
| TI-09-ARCH (parte laboratorio) | Sin datos de origen: `market.options.chain` y `market.options.fx` vacíos en `main` de 2024 a hoy (TI-01-INV). Retirada por el usuario el 2026-11-08 «hasta que tengamos más datos» | [backlog](../../backlog/README.md), cuando el backend publique la cadena en qn |
| TS-02-DISC (parte laboratorio) | Necesita TS-02-GEN (SPRINT-03 de `quantdesk`, ola 3) | [future/SPRINT-03](../../future/SPRINT-03/SPRINT.md) |
| Ejecuciones de entrenamiento, TS-05-*, TS-06-FT, TS-18-WF, TS-15-FINAL | Necesitan TI-06-CLI y DL-07-TRAIN (SPRINT-04 de `quantdesk`) | [future/SPRINT-04](../../future/SPRINT-05/SPRINT.md) (renumerado a SPRINT-05 el 2026-11-13) |
| Cualquier cambio en código o sprints de `quantdesk` o en el scraper del backend | Gobernanza (GOBERNANZA.md, SPRINT_PROJECT §5) | backlog de cada repo |
| GPU para Chronos-2/Toto | PyTorch con ROCm en Windows no se da por supuesto; carriles DL-02-GATES aún no existen | CPU ahora; GPU en SPRINT-03 si procede |

## 7. Orden, carriles y mutex

- **LAB-00-ENV primero**: barrera para todo lo que importe paquetes nuevos.
- Carril datos: TI-01-INV → TI-09-ARCH (lectura bajo demanda del lago; sin urgencia diaria tras la decisión 12-A;
  retirada el 2026-11-08, §6); TI-12-MT5 y TI-13-PUB en paralelo → TI-02-DATA (exporta primero el lago y añade fuentes al llegar).
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

## 10. Cierre (2026-11-09)

**Estado:** Cerrado. Fin real: 2026-11-09. No hay release (SPRINT_PROJECT §10): se pasa de cerrado a planificación.

**Freeze:** no aplica (sin release); el proyecto pasa a planificación el 2026-11-09.

| ID | Commits (rama `main`, sin push) | Veredicto | Evidencia |
|---|---|---|---|
| LAB-00-ENV | `cb46ce2` (motor `69fdb39d`) | CERRADA 2026-11-08 | EXECUTION «Cierre de LAB-00-ENV» |
| TI-01-INV | `cb46ce2`; informe del usuario | CERRADA 2026-11-08 | `execution/TI-01-INV/` |
| TI-09-ARCH | — | RETIRADA por el usuario el 2026-11-08: sin datos de origen | §6; [backlog](../../backlog/README.md) |
| TI-12-MT5 | fases `7d38136`, `1ed4dfd`, `558baee`, `773965e`, `9e9dfe5`, `f9dcd0c` y `fdfa3a7` (cuadre); raíz `4cd1237` (`run_scheduler.cmd`) | CERRADA 2026-11-09 | `execution/TI-12-MT5/` (fase-a/b/c, `cuadre.md`); intentos BDD 126, 129–133 |
| TI-13-PUB | `7ea6d94`, `cd4e4ba`, `4a56315`, `e001a97` | CERRADA 2026-11-08 | EXECUTION «Cierre de TI-13-PUB» |
| TI-02-DATA | `906f73e`, deuda `0e67465` | CERRADA 2026-11-09 | EXECUTION «Cierre de TI-02-DATA» |
| TS-00-PREC | `5afc795` | CERRADA 2026-11-08 | `execution/TS-00-PREC/` |
| TS-00-BENCH | `baa4ee6` (fase 1) y `8a849c6` (Toto) | CERRADA 2026-11-09 | `execution/TS-00-BENCH/informe.md`; intento BDD 127 |
| TS-00-OBJ | `quantdesk` `905b1670` (umbrales) y `c5f2be51` (FinCast en D-08) | CERRADA 2026-11-09, puerta 3 | PLAN_TSFM_FINANZAS «Fase 0» |

- **Suite del DoD.** `run_selftests.py` sobre `git archive` del HEAD de cierre (beaf81c) da 12 OK y 0 FALLO. Los selftests del
  extractor, el publicador, el banco y el cuadre están en verde. El resultado está en
  `E:/quantdesk-lab/tmp/verif_cierre_beaf81c.log`.
- **Datasets e informes:** cada uno con hash, semilla, corte y versión del motor, en sus informes. Ninguna credencial en
  el repo.
- **Incidencias:**
  - [ISSUE-LAGO-FX-1D-CLOSE](../../issues/ISSUE-LAGO-FX-1D-CLOSE.md): abierta, destino SPRINT-02. La tabla de cabecera
    del banco usa un close de yfinance que en realidad es el precio de las 00:00 UTC; hay que repetirla sobre el 1d de
    MT5.
  - [ISSUE-TI12-MT5-INTRADIA-LOCAL](../../issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md): en investigación; descarga local de
    m1 y m5 de `@continuo` en curso.
  - [ISSUE-TI09-SONDA-CADENAS](../../issues/ISSUE-TI09-SONDA-CADENAS.md): abierta, fuera de sprint.
  - Ninguna se resolvió dentro del sprint. Las tres siguen vivas en `issues/`.
- **Operación que sigue fuera del sprint:**
  - publicador 1d de fx28 con la tarea programada `quantdesk\publicador_mt5`, que registró el usuario;
  - noche 1 de la carga 1d de `@continuo` en qn, programada a las 02:03 del 2026-11-10 con el OK de network y backend;
  - noche 2, la de las acciones, a la espera de network y del usuario.
- **Costes:** no hay `USAGE.md` del sprint ni lectura final de cuota. Los intentos están en la BDD de sprints (`sprint_db`,
  intentos 119–133), todos con Opus 5.5 o Sonnet 5.5 por suscripción. Faltan pp aislados por tarea, así que no entran
  en la media de calibración: es un hueco, no un cero.

### Retrospectiva y trinquete

| Fallo repetido o grave | Causa | Control añadido | Prueba de que lo detecta | ¿Bloquea o avisa? |
|---|---|---|---|---|
| El extractor y el publicador fallaban con el terminal real («Call failed», -6, -10005) | Comportamiento real de MT5: historia sincronizándose, relogin sobre un terminal abierto, `count = maxbars` | Reintento acotado, enganche al terminal abierto y profundidad con una sola consulta (entregas 6 y 6b) | El MT5 falso de los selftests reproduce los códigos -1, -2, -6 y -10005 | Bloquea (suite) |
| `schtasks` rechazaba el XML («unable to switch the encoding») | `schtasks` exige UTF-16 y el XML del repo es UTF-8 | `run_scheduler.cmd` y `registrar_tareas.ps1` convierten a UTF-16 y registran de forma idempotente | Registro real por el usuario: tarea CREADA y Ready. Sin test automático | Avisa |
| La raíz afirmó a backend datos sin comprobar (`EURUSD=X`; «ningún símbolo de 6 letras no FX») | Respuesta de memoria | Regla: comprobar contra el universo o el inventario antes de afirmar a otro proyecto; corregido en ambos casos | Sin control automático | Avisa (regla escrita) |
| El close del FX diario del lago no es el del final del día | Captura de yfinance en el backend | `cuadre_mt5.py` cruza el 1d con el 1m de MT5; ISSUE-LAGO-FX-1D-CLOSE | El cuadre lo detectó (41,7 % de filas con `open == close`). Falta una comprobación en el exportador TI-02-DATA (SPRINT-02) | Avisa |
| Las corridas de Toto pasaron de las 2 h de pared | Máquina cargada (antivirus, MT5) | Coste de CPU por origen medido en piloto antes de cada corrida | Informe del banco | Avisa |

Reglas que se retiran: ninguna.

[PLAN_TSFM_FINANZAS]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md
[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
