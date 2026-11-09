# Plan — Archivo de cadenas de opciones del laboratorio (TI-09-ARCH)

> **Origen:** división de [backlog/README.md](README.md) (fila TI-09-ARCH de §2.2, filas TI-09-ARCH de §4 y riesgo
> transversal de §4), en la versión del árbol revisada el 2026-11-09 sobre el commit `8a849c6`. División decidida por el
> usuario el 2026-11-09 (revisión de planes, GAP-BACKLOG_README-06 opción (a)). Texto de la especificación copiado
> íntegro; lo nuevo va marcado «(usuario, 2026-11-09)».

**Estado:** backlog, sin sprint. Retirada de SPRINT-01 por el usuario el 2026-11-08; vuelve cuando se decida
GAP-BACKLOG_README-01 (§5). **Fecha:** 2026-11-09.

**Especificación de referencia:** [PLAN_TSFM_INTEGRACION] TI-09-ARCH y fila 3 de SPRINT-01 (conservada en
[archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md)). Scraper: `quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md`.
Esquema y retención del topic: `quantdesk-network/docs/lake/RETENCION.md` (el plan de network
`PLAN_OPTIONS_CHAIN_ESQUEMA_CAPTURA`, con OCS-01/OCS-02 cerradas, se archiva en la revisión del 2026-11-09).

## 1. Contexto

TI-09-ARCH es el lector del lago que congela con hash la instantánea limpia de las cadenas de opciones (mid y filtro de
arbitraje). Dependen de ella TS-16-QCONO y TS-08-DYN (GAP-TSFM-02 de PLAN_TSFM_FINANZAS).

- 2026-11-08: TI-01-INV halló `market.options.chain` y `market.options.fx` vacíos en `main`; el usuario la retiró de
  SPRINT-01 «hasta tener más datos».
- 2026-11-09: el backend publica de nuevo: primer run de `options_downloader_job` 03:00–04:17 UTC, `SUCCESS`,
  `options_chain_coverage_ratio` 0,998 (backend `current/EXECUTION.md`, run `157c2754`, ISSUE-OPTIONS-JOBS-PARADOS, «día
  hábil 1 de 3»). SIN VERIFICAR desde el laboratorio: lo comprueba TI-09-SONDA (§3).
- Decisión 12-A (usuario, 2026-11-07): todo lo que pasa por qn acaba en S3 sin retención, así que el laboratorio no
  copia a diario. **Esta garantía se rompe el 2026-11-09** (§4).

## 2. TI-09-ARCH (parte laboratorio)

| ID | Qué se hace aquí | Cuándo / estado (2026-11-09) | Notas |
|---|---|---|---|
| **TI-09-ARCH** (parte laboratorio) | Lector bajo demanda de `market.options.chain` desde el lago (decisión 12-A: S3 sin retención, sin copia diaria ni tarea programada propia) que produce, para un rango de fechas, la instantánea por día hábil cruda y limpia (mid, filtro de arbitraje de mariposa y calendario) y la congela con hash en `E:/quantdesk-lab/datasets/` al cortar cada dataset; informe de días hábiles sin datos en el lago | **Backlog; ya desbloqueable** (GAP-BACKLOG_README-01). Retirada de SPRINT-01 por el usuario el 2026-11-08 (TI-01-INV halló la cadena vacía en qn). Desde el **2026-11-09** el backend publica de nuevo: primer run de `options_downloader_job` 03:00–04:17 UTC, `SUCCESS`, `options_chain_coverage_ratio` 0,998 (backend `current/EXECUTION.md`, ISSUE-OPTIONS-JOBS-PARADOS, «día hábil 1 de 3»). SIN VERIFICAR desde el laboratorio: falta una sonda de sólo lectura con `scripts/inventario_options_chain.py` (TI-09-SONDA, §3) | Especificación: [PLAN_TSFM_INTEGRACION] TI-09-ARCH y fila 3 de SPRINT-01 (conservada en [archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md)). Scraper: `quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md`: OC-01-FAIL y OC-02-ALERT **hechas** (su SPRINT-01), OC-05-RET cumplida en revisión, **OC-03-CLOSE** (captura tras el cierre de EE. UU. con `captured_at`, `capture_id` y `underlying_price`) y OC-04-TIME pendientes en su SPRINT-02. Esquema y garantía de S3: network OCS-01/OCS-02 **cerradas** (2026-11-08). Mientras no exista OC-03: última captura de cada día (hoy la de las 20:00 París) con su hora; sin spot en la fila, subyacente del OHLCV diario. **Aceptación ejecutable:** (1) dos lecturas del mismo rango y corte dan el mismo SHA-256; (2) el filtro de arbitraje está documentado y su informe cuenta las filas excluidas por motivo; (3) informe de días hábiles sin captura en el lago por subyacente; (4) cobertura ≥ 98 % de días hábiles medida sobre los 20 días hábiles siguientes a la entrega (o causa documentada). La alerta de «falta un día hábil» ya la da el backend (`OptionsChainSnapshotMissing`): el laboratorio la reutiliza y no crea otra |

Cambios decididos el 2026-11-09 que la especificación anterior aún no recoge (se aplican al planificarla):

- **Copia propia** (usuario, 2026-11-09): con la herramienta genérica de borrado en el lago, «sin copia diaria ni tarea
  programada propia» deja de ser seguro. TI-09-ARCH debe planificar una copia propia del archivo de opciones (§4,
  GAP-ARCHIVO_OPCIONES-01).
- **Universo** (usuario, 2026-11-09): el backend añade 5–10 ETF e índices a la captura (`asset_type` ETF/INDEX, en OC-03
  o en una tarea al lado). El lector y el informe de huecos agrupan por subyacente y `asset_type`; el subyacente de
  respaldo «OHLCV diario» debe existir también para esos ETF e índices.
- **Cobertura en SPRINT-02 del laboratorio:** la fila 6 de [next/SPRINT.md](../next/SPRINT.md) («TI-09-ARCH
  (cobertura)») sigue condicionada a que antes se entregue esta parte.

## 3. TI-09-SONDA — sonda de sólo lectura de las cadenas en qn (usuario, 2026-11-09)

Resuelve **C-07** de la revisión (= C-BACKLOG_README-01): cadenas «vacías» (STATUS y SPRINT-01 §6 del laboratorio,
2026-11-08; quantdesk `PLAN_TSFM_FINANZAS` §3) frente a «publicando» (backend `current/EXECUTION.md`, 2026-11-09).
Decisión: **sonda de sólo lectura** del laboratorio. Descartada: dar por buena la palabra del backend (riesgo de
repetir el «Published N sin enviar nada» del diagnóstico del 2026-11-07).

| ID | Qué se hace | Aceptación | Depende de |
|---|---|---|---|
| **TI-09-SONDA** | Ejecutar `scripts/inventario_options_chain.py` (sólo lectura) sobre `market.options.chain` y `market.options.fx` en `main` desde el 2026-11-09 | (1) Cifra por día hábil: filas, subyacentes distintos, vencimientos y hora de captura (`captured_at` si existe), con la consulta reproducible; (2) con esa cifra se corrigen la fila «Datos» de [STATUS.md](../STATUS.md), la fila 3 y §6 de SPRINT-01 (o su dossier si ya cerró) y, por su aplicador, `quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md` §3; (3) ningún token en el repo, informes ni chat | Token `sub:` de lectura de qn del usuario (**puerta de usuario**, como TI-01-INV). Ficha viva: [ISSUE-TI09-SONDA-CADENAS](../issues/ISSUE-TI09-SONDA-CADENAS.md) |

Repetición: la recomendación de GAP-BACKLOG_README-01 (c) es repetir la sonda cada semana mientras TI-09-ARCH espera a
OC-03; se decide con ese GAP.

## 4. Retención del lago y copia propia (usuario, 2026-11-09)

Decisión T7 de la revisión (C-13, «Borrado en el lago»): **herramienta genérica de borrado** en qn (network
`PLAN_QUITAR_TOPICS_PENDIENTE`, Fase 3 `lake delete`). Consecuencias para este plan:

- **Rompe 12-A y la garantía OCS-02**: `quantdesk-network/docs/lake/RETENCION.md` declara la excepción (lo aplica
  network). El lago deja de ser un archivo garantizado de las cadenas.
- **El laboratorio debe planificar una copia propia** del archivo de opciones (igual que el backend en OC-05-RET).
  Hasta que exista, los datasets que el laboratorio congela en `E:/quantdesk-lab/` son la única copia fuera del lago de
  lo que han leído.
- Mitigación recomendada, **no decidida**: que la herramienta rechace por defecto `market.*` en `main` salvo
  confirmación explícita. Es de network; aquí sólo se registra.
- Opciones descartadas por el usuario: descartar la Fase 3 de borrado; borrado restringido a `mqtt.events`.

Riesgo transversal (conservado de README §4): la copia periódica de qn (network `PLAN_COPIA_PERIODICA_LAGO`) aún no
copia S3 de verdad (sólo simulada, 2026-11-08).

## 5. Dependencias externas (2026-11-09)

| Tarea local | Depende de | Estado | Mientras tanto |
|---|---|---|---|
| TI-09-ARCH | backend OC-03-CLOSE (su SPRINT-02) | pendiente; dependencia de network servida | última captura de cada día y subyacente del OHLCV diario |
| TI-09-ARCH | backend OC-01/OC-02 (alerta en origen); network OCS-02 (S3 sin retención) | **hechas** (2026-11-08/09); la garantía de OCS-02 queda con la excepción del borrado genérico (§4) | — |
| TI-09-ARCH (universo) | backend: 5–10 ETF/índices en la captura (OC-03 o tarea al lado) | decidido (usuario, 2026-11-09), sin fecha | sólo acciones del S&P 500 |
| TI-09-SONDA | token de lectura de qn (usuario) | puerta de usuario | — |

Filas en [DEPENDENCIAS.md](../DEPENDENCIAS.md) «Dependencias de tarea».

## 6. GAPs abiertos

- **GAP-BACKLOG_README-01 — ¿Cuándo vuelve TI-09-ARCH?** (abierto; se pregunta al planificar el próximo sprint del
  laboratorio). Opciones: (a) reabrir en SPRINT-01 ya en modo «mientras tanto»; (b) fila de SPRINT-02 del laboratorio;
  (c) esperar a OC-03 y a unos 20 días hábiles de capturas. Recomendación: (c), con la sonda semanal de §3. Si no se
  decide: sigue en el backlog; el riesgo de no ver una racha sin captura lo cubre la alerta del backend.
- **GAP-ARCHIVO_OPCIONES-01 — Forma de la copia propia** (abierto, nuevo el 2026-11-09). ¿Copia incremental diaria
  (tarea programada del laboratorio a `E:/quantdesk-lab/`, con hash por día) o copia de todo lo leído al cortar cada
  dataset? La diaria cubre un borrado entre cortes; la del corte no añade tareas programadas pero deja ventanas sin
  copia. Se decide al planificar TI-09-ARCH, junto con GAP-BACKLOG_README-01.

[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
