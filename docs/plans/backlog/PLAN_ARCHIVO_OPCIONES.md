# Plan — Archivo de cadenas de opciones del laboratorio (TI-09-ARCH)

> **Origen:** división de [backlog/README.md](README.md) (fila TI-09-ARCH de §2.2, filas TI-09-ARCH de §4 y riesgo
> transversal de §4), en la versión del árbol revisada el 2026-11-09 sobre el commit `8a849c6`. División decidida por el
> usuario el 2026-11-09 (revisión de planes, GAP-BACKLOG_README-06 opción (a)). Texto de la especificación copiado
> íntegro; lo nuevo va marcado «(usuario, 2026-11-09)».

**Estado (revisado el 2026-11-13): backlog RESIDUAL.** La parte de laboratorio está entregada; lo único pendiente es la
medición de cobertura (fila S02-6 de [next/SPRINT.md](../next/SPRINT.md), ya planificada: no se duplica aquí) y cerrar
TI-09-SONDA. Cuando S02-6 cierre (no antes del 2026-12-11) este plan se archiva (veredicto de la revisión, al final).
**Decisiones del usuario del 2026-11-13 aplicadas** (usuario, 2026-11-13, revisión de planes, R1 y R4; sección final):
S02-6 es la **fila 3 del SPRINT-03 nuevo**, que no tiene dependencia de entrada (R1), y la sonda se une a ella y se
cierra con su cifra por sesión desde el 2026-11-12; los días 2026-11-09…11 quedan como no medibles (R4). STATUS ya dice
que hay cadenas en qn desde la sesión 2026-11-12 y que `market.options.fx` está vacío.
*Texto anterior:* backlog, sin sprint. Retirada de SPRINT-01 por el usuario el 2026-11-08; vuelve según GAP-BACKLOG_README-01,
resuelto el 2026-11-10 con su opción (c): esperar a OC-03 y a unos 20 días hábiles de capturas (§6). **Fecha:**
2026-11-09; revisado el 2026-11-10 (final del plan), con las decisiones D7 y D11 del usuario aplicadas (usuario,
2026-11-10, revisión de planes): **sin copia propia** (la copia es la común de network) y **sin spot de respaldo**.

> **Al cierre de SPRINT-02 (2026-11-13):** la parte de laboratorio de TI-09-ARCH está **entregada** en SPRINT-02 (fila
> 6): lector y archivador aceptados (`c6c7b5b`) y primer dataset real `oc03_s20261112_c20261113` (`sha256:eb98ac6a…eea1`).
> La **medición de cobertura** (20 días hábiles NYSE hasta el 2026-12-10, con token nuevo) pasa a SPRINT-03 como S02-6
> (decisión del usuario «Cerrar y arrastrar»). Código: `scripts/archivo_opciones.py`, `scripts/archivo_opciones_lib/`
> (`lector.py`, `flujo.py`, `validacion.py`, `selftests.py`) y `scripts/descarga_opciones.py` (volcado sólo stdlib para mini);
> dataset en `E:/quantdesk-lab/datasets/TI-09-ARCH/oc03_s20261112_c20261113/` (`informe.md` con motivos de exclusión y
> huecos por subyacente y `asset_type`). **Qué quedó fuera de lo previsto en este plan** (decidido por la raíz con la
> respuesta del backend, 2026-11-13): no hay «modo mientras tanto» —el lector **ignora toda fila sin `capture_id`** y su
> corte son las sesiones con `date` ≥ 2026-11-12 (las capturas de 04:00/12:00/20:00 París, sin spot, no se archivan,
> coherente con D11)—, y el universo de los huecos es la unión de lo observado más los siete obligatorios
> (`lector.py:47`). Cierre en
> [archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md#9-cierre-2026-11-13).

**Especificación de referencia:** [PLAN_TSFM_INTEGRACION] TI-09-ARCH y fila 3 de SPRINT-01 (conservada en
[archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md)). Scraper: `quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md`.
Esquema y retención del topic: `quantdesk-network/docs/lake/RETENCION.md` (el plan de network
`PLAN_OPTIONS_CHAIN_ESQUEMA_CAPTURA`, con OCS-01/OCS-02 cerradas, está archivado desde el 2026-11-09 en
`quantdesk-network/docs/plans/archive/SPRINT-01_2026-11-08_2026-11-08/PLAN_OPTIONS_CHAIN_ESQUEMA_CAPTURA.md`; en el
backlog de network queda un stub).

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
| **TI-09-ARCH** (parte laboratorio) | Lector bajo demanda de `market.options.chain` desde el lago (decisión 12-A: S3 sin retención, sin copia diaria ni tarea programada propia) que produce, para un rango de fechas, la instantánea por día hábil cruda y limpia (mid, filtro de arbitraje de mariposa y calendario) y la congela con hash en `E:/quantdesk-lab/datasets/` al cortar cada dataset; informe de días hábiles sin datos en el lago | **Backlog; ya desbloqueable** (GAP-BACKLOG_README-01). Retirada de SPRINT-01 por el usuario el 2026-11-08 (TI-01-INV halló la cadena vacía en qn). Desde el **2026-11-09** el backend publica de nuevo: primer run de `options_downloader_job` 03:00–04:17 UTC, `SUCCESS`, `options_chain_coverage_ratio` 0,998 (backend `current/EXECUTION.md`, ISSUE-OPTIONS-JOBS-PARADOS, «día hábil 1 de 3»). SIN VERIFICAR desde el laboratorio: falta una sonda de sólo lectura con `scripts/inventario_options_chain.py` (TI-09-SONDA, §3) | Especificación: [PLAN_TSFM_INTEGRACION] TI-09-ARCH y fila 3 de SPRINT-01 (conservada en [archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md)). Scraper: `quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md`: OC-01-FAIL y OC-02-ALERT **hechas** (su SPRINT-01), OC-05-RET cumplida en revisión, **OC-03-CLOSE** (captura tras el cierre de EE. UU. con `captured_at`, `capture_id` y `underlying_price`) y OC-04-TIME pendientes en su SPRINT-02. Esquema y garantía de S3: network OCS-01/OCS-02 **cerradas** (2026-11-08). Mientras no exista OC-03: última captura de cada día (hoy la de las 20:00 París) con su hora; **sin spot en la fila y sin spot de respaldo** (se quita el «subyacente del OHLCV diario»; sólo vale `underlying_price` de OC-03, captura de cierre del backend: usuario, 2026-11-10, revisión de planes, D11). **Aceptación ejecutable:** (1) dos lecturas del mismo rango y corte dan el mismo SHA-256; (2) el filtro de arbitraje está documentado y su informe cuenta las filas excluidas por motivo; (3) informe de días hábiles sin captura en el lago por subyacente; (4) cobertura ≥ 98 % de días hábiles medida sobre los 20 días hábiles siguientes a la entrega (o causa documentada) *(ventana fijada en la fila S02-6: sesiones 2026-11-12…2026-12-10, decidida en el arrastre del 2026-11-13; C-ARCHIVO_OPCIONES-06)*. La alerta de «falta un día hábil» ya la da el backend (`OptionsChainSnapshotMissing`): el laboratorio la reutiliza y no crea otra |

Cambios decididos el 2026-11-09 que la especificación anterior aún no recoge (se aplican al planificarla):

- **Copia** (usuario, 2026-11-09; **sustituida el 2026-11-10, D7**): con la herramienta genérica de borrado en el lago,
  «sin copia diaria ni tarea programada propia» deja de ser seguro, pero **no hay copia propia del laboratorio ni del
  backend**: la copia de `market.options.chain` es la común de network (`PLAN_COPIA_PERIODICA_LAGO`, todo el lago, una
  vía). El laboratorio sólo guarda lo que lee al cortar cada dataset, con hash. Condición: `lake delete` no se usa sobre
  `market.*` hasta que exista la copia común (§4; usuario, 2026-11-10, revisión de planes).
- **Universo** (usuario, 2026-11-09): el backend añade 5–10 ETF e índices a la captura (`asset_type` ETF/INDEX, en OC-03
  o en una tarea al lado). El lector y el informe de huecos agrupan por subyacente y `asset_type`. *(Decisión
  2026-11-10, D11:)* **no hay subyacente de respaldo** del OHLCV diario ni para esos ETF e índices: sólo cuentan las
  filas con `underlying_price` de OC-03.
- **Cobertura en SPRINT-02 del laboratorio:** la fila 6 de [current/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md) («TI-09-ARCH
  (cobertura)») sigue condicionada a que antes se entregue esta parte.

Correcciones de la revisión del 2026-11-10 (verificadas contra el código del backend en `e90eb03`, el inventario
TI-01-INV y los datos locales; se aplican al planificar):

- **Modo «mientras tanto» y marca de captura. OBSOLETO desde el 2026-11-13 (no se implementó: el lector ignora toda
  fila sin `capture_id`; corte = sesiones con `date` ≥ 2026-11-12; ver C-ARCHIVO_OPCIONES-07). Se conserva el análisis
  como razón de que las capturas anteriores a OC-03 no se archiven.** Antes de OC-03 las filas no llevan `captured_at` ni `capture_id`: `date`
  es la fecha UTC de la llamada (`market_scrapper/options_downloader.py:339`, `now.date()`) y la marca `ts` de cada fila
  es el instante de publicación de su lote ticker-vencimiento (`market_scrapper/market_sink.py:174`,
  `datetime.now(timezone.utc)`), o sea el `_ts` del lago. Los tres runs diarios (cron `0 4,12,20 * * 1-5`,
  `Europe/Paris`, `backend/dagster/code/airflow_migrated.py:137`, ~77 min cada uno) sólo se distinguen agrupando por
  `_ts`; el lector debe fijar y documentar esa regla de agrupación y asignar cada captura a una **sesión de Nueva York**
  (la de las 04:00 París refleja la sesión anterior). Con OC-03 `date` ya es la sesión de NY y existe `captured_at`: el
  lector atiende los dos regímenes y prueba el empalme. La nota del backend «las filas del 2026-11-09 se reinterpretan
  con `captured_at`» no es posible para ellas (no lo tienen): **C-ARCHIVO_OPCIONES-02 resuelta por regla (usuario,
  2026-11-10, revisión de planes):** hecho del código, el lector deriva la sesión desde `_ts`; la frase de OC-03(b) se
  corrige en `PLAN_OPTIONS_CHAIN_ARCHIVO` del backend.
- **Subyacente de respaldo: quitado (D11).** «Subyacente del OHLCV diario» no está en el lago para las acciones del
  S&P 500: el inventario TI-01-INV (2026-11-08) sólo ve 56 series de `market.ohlcv` (v1, FX 1h y 1d). **Decisión del
  usuario, 2026-11-10, revisión de planes: se elimina ese respaldo; el spot es sólo `underlying_price` de OC-03** (captura
  de cierre del backend). Así se evita además que un cierre de las 16:00 ET se mezcle con una captura de las 14:00 ET.
  C-ARCHIVO_OPCIONES-01 resuelta. Queda como dato (no como entrada del lector) que localmente existe
  `E:/quantdesk-lab/data/mt5/us_grandes_1d_20261109`.
- **Nada congelado todavía.** `E:/quantdesk-lab/` no contiene ningún dato de opciones (sólo `data/{lago,mt5,public}` y
  `datasets/{TI-02-DATA,TI-13-PUB}`, 2026-11-10): hoy el laboratorio no tiene copia de lo que ya está en qn.
- **FX diario (ISSUE-LAGO-FX-1D-CLOSE / ISSUE-FX-1D-CLOSE-YFINANCE).** No afecta a este plan: el defecto es del cierre
  diario de FX de yfinance y el archivo de opciones no usa FX diario. `market.options.fx` es otro topic (la sonda lo
  lee igual).

## 3. TI-09-SONDA — sonda de sólo lectura de las cadenas en qn (usuario, 2026-11-09)

Resuelve **C-07** de la revisión (= C-BACKLOG_README-01): cadenas «vacías» (STATUS y SPRINT-01 §6 del laboratorio,
2026-11-08; quantdesk `PLAN_TSFM_FINANZAS` §3) frente a «publicando» (backend `current/EXECUTION.md`, 2026-11-09).
Decisión: **sonda de sólo lectura** del laboratorio. Descartada: dar por buena la palabra del backend (riesgo de
repetir el «Published N sin enviar nada» del diagnóstico del 2026-11-07).

| ID | Qué se hace | Aceptación | Depende de |
|---|---|---|---|
| **TI-09-SONDA** | Ejecutar `scripts/inventario_options_chain.py` (sólo lectura) sobre `market.options.chain` y `market.options.fx` en `main` desde el 2026-11-09 | (1) Cifra por día hábil: filas, subyacentes distintos, vencimientos y hora de captura (`captured_at` si existe; si no, número de capturas distintas del día agrupando `_ts`, §2), con la consulta reproducible y su salida guardada; (2) con esa cifra se corrigen la fila «Lago de qn» de [STATUS.md](../STATUS.md) (antes «Datos») y, por su aplicador, `quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md` §3. **SPRINT-01 ya cerró (2026-11-09, archivado con SHA-256 en su `ARCHIVE_MANIFEST.md`):** la fila 3 y §6 de [archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md) dicen «vacío» y eso era cierto el 2026-11-08; no se reescriben (C-ARCHIVO_OPCIONES-03 resuelta por regla, usuario, 2026-11-10, revisión de planes: el archivo es inmutable con su manifiesto): la corrección va como nota fechada en la ficha de la incidencia y en STATUS; (3) ningún token en el repo, informes ni chat | Token `sub:` de lectura de qn del usuario (**puerta de usuario**, como TI-01-INV). Ficha viva: [ISSUE-TI09-SONDA-CADENAS](../issues/ISSUE-TI09-SONDA-CADENAS.md) |

Repetición: la recomendación de GAP-BACKLOG_README-01 (c) es repetir la sonda cada semana mientras TI-09-ARCH espera a
OC-03; se decide con ese GAP. **Obsoleta el 2026-11-13:** OC-03 ya está servida y el lector se prueba con el lago real
(dataset `oc03_s20261112_c20261113`); la sonda semanal no se hace.

**Estado de TI-09-SONDA (2026-11-13).** La pregunta de fondo (¿hay cadenas en qn?) quedó contestada por la «sonda de
contraste» de la raíz (token id 39, `main`, `sub:market.options.chain` y `sub:market.options.fx`, revocado el mismo día;
[EXECUTION de SPRINT-02](../archive/SPRINT-02_2026-11-11_2026-11-13/EXECUTION.md), fila 2026-11-13 «Sonda de contraste»):
`market.options.chain` tiene filas con los campos nuevos, `/latest` trae 509 símbolos (502 `EQUITY`, 4 `ETF`, 3 `INDEX`),
y `market.options.fx` **no tiene filas**. Con ella y el primer dataset real (sesión 2026-11-12, 431.681 filas crudas, 509
subyacentes) la aceptación 1 sólo está cubierta para esa sesión; el detalle por día del 2026-11-09 al 2026-11-11 (régimen
antiguo, sin spot ni `capture_id`) no se ha medido y ningún consumidor lo usa. La aceptación 2 (corregir la fila «Lago de
qn» de STATUS y avisar a quantdesk de su `PLAN_TSFM_FINANZAS` §3) sigue sin hacerse y no necesita token. La aceptación 3
se cumple (tokens revocados; búsqueda de patrón `qn_` en el repo: 0).

**Decisión (usuario, 2026-11-13, revisión de planes, R4):** TI-09-SONDA se cierra con la **cifra por sesión de S02-6
desde el 2026-11-12**; los días 2026-11-09…11 (régimen sin `capture_id`) quedan documentados como **no medibles**
(GAP-ARCHIVO_OPCIONES-04 y GAP-ISSUES-01 resueltos así). La aceptación 1 se lee así; la 2 queda hecha en STATUS el
2026-11-13 (la corrección de `PLAN_TSFM_FINANZAS` §3 es de `quantdesk`, avisado por la raíz). La ficha sigue viva hasta
que S02-6 dé la cifra; su fila se une a S02-6 (SPRINT-03 fila 3).

## 4. Retención del lago y copia propia (usuario, 2026-11-09)

Decisión T7 de la revisión (C-13, «Borrado en el lago»): **herramienta genérica de borrado** en qn (network
`PLAN_RETIRADA_TOPICS_EVENTOS`, Fase 3 `lake delete`; antes `PLAN_QUITAR_TOPICS_PENDIENTE`, hoy un stub que remite
allí). Estado a 2026-11-10: la herramienta **no existe** (tareas 3.1/3.2 sin empezar, sin sprint asignado; `RETENCION.md`
aún no declara la excepción, tarea 3.3) y la tarea 3.4 de network (issue de aviso a este repo) **no se ha abierto**
(`issues/` sólo tiene las tres fichas conocidas): el riesgo es prospectivo, pero la copia debe estar antes de que se
use la herramienta sobre `market.*`. Consecuencias para este plan:

- **Rompe 12-A y la garantía OCS-02**: `quantdesk-network/docs/lake/RETENCION.md` declara la excepción (lo aplica
  network). El lago deja de ser un archivo garantizado de las cadenas.
- **Copia común de network, sin copia propia (D7, usuario, 2026-11-10, revisión de planes).** La copia de
  `market.options.chain` es la de `PLAN_COPIA_PERIODICA_LAGO` (todo el lago, una vía); ni el backend (OC-05-RET /
  GAP-OCARCH-05) ni el laboratorio hacen copia propia. El laboratorio sólo guarda lo que lee al cortar cada dataset, con
  hash: esos datasets en `E:/quantdesk-lab/` son la única copia fuera del lago de lo que han leído.
- **Condición:** `lake delete` no se usa sobre `market.*` hasta que la copia común exista.
- **Actualización 2026-11-13.** Network concilió su Fase 3 y su DEPENDENCIAS con D7 en `85c4708` (sin copia propia de
  backend ni laboratorio; anota las lecturas y escrituras de este repo sobre qn y pide avisarnos de cambios en retención,
  esquema o borrado de `market.*`). La tarea 3.4 (issue de aviso a este repo) queda **sustituida** por esa conciliación y
  por el aviso de la raíz: no hace falta abrir ficha. COP-01 (destino de la copia) sigue sin decidir: la copia común
  **no existe**, y por eso los datasets congelados de `E:/quantdesk-lab/datasets/TI-09-ARCH/` son hoy la única copia
  fuera del lago de lo que el laboratorio leyó. Para el laboratorio no queda tarea de copia: es una dependencia de
  network, y sólo se vigila.
- Mitigación recomendada, **no decidida**: que la herramienta rechace por defecto `market.*` en `main` salvo
  confirmación explícita. Es de network; aquí sólo se registra.
- Opciones descartadas por el usuario: descartar la Fase 3 de borrado; borrado restringido a `mqtt.events`.

Riesgo transversal (conservado de README §4): la copia periódica de qn (network `PLAN_COPIA_PERIODICA_LAGO`) aún no
copia S3 de verdad (sólo simulada, 2026-11-08; sigue igual el 2026-11-10: COP-01 espera decisión del usuario sobre
destino y host). Solape con el backend (`PLAN_OPTIONS_CHAIN_ARCHIVO` OC-05-RET reabierta, GAP-OCARCH-05) resuelto en
favor de la copia común de network: ver GAP-ARCHIVO_OPCIONES-02. Mientras COP-01 no tenga destino, no hay copia del lago
y por eso rige la condición de arriba sobre `lake delete`.

## 5. Dependencias externas (2026-11-09)

| Tarea local | Depende de | Estado | Mientras tanto |
|---|---|---|---|
| TI-09-ARCH | backend OC-03-CLOSE (su SPRINT-02, aún en `next/`: S02-D6) | **servida (2026-11-13)**: desplegada en `cc1811d`; corte 2026-11-12, primer cierre completo `capture_id` `2026-11-12-163125-5b2305`; contrato del lector en [current/EXECUTION.md](../archive/SPRINT-02_2026-11-11_2026-11-13/EXECUTION.md) (fila 2026-11-13) | última captura de cada día (agrupando `_ts`, §2), **sin spot de respaldo** (D11: sólo `underlying_price` de OC-03; C-ARCHIVO_OPCIONES-01 resuelta) |
| TI-09-ARCH | backend OC-01/OC-02 (alerta en origen); network OCS-02 (S3 sin retención) | **hechas** (2026-11-08/09); la garantía de OCS-02 queda con la excepción del borrado genérico (§4) | — |
| TI-09-ARCH (universo) | backend: 5–10 ETF/índices en la captura (OC-03 o tarea al lado) | **servida (2026-11-13)**: siete obligatorios (SPY, QQQ, IWM, DIA como `ETF`; ^SPX, ^NDX, ^VIX como `INDEX`) dentro de OC-03; aceptada en producción (backend `04cc60f`, `5723017`); `OBLIGATORIOS` en `scripts/archivo_opciones_lib/lector.py:47` | — |
| TI-09-SONDA | token de lectura de qn (usuario) | **sonda de contraste hecha el 2026-11-13** (EXECUTION de SPRINT-02, fila «Sonda de contraste»; token id 39, revocado): hay cadenas; `market.options.fx` sin filas. Falta sólo corregir STATUS y avisar a quantdesk. **2026-11-13:** STATUS corregido; cierre con la cifra por sesión de S02-6 (R4, SPRINT-03 fila 3, mismo token) | — |
| TI-09-ARCH (copia) | network `PLAN_COPIA_PERIODICA_LAGO` (copia común del lago, COP-01 sin destino) y 3.3/3.4 de `PLAN_RETIRADA_TOPICS_EVENTOS`; backend OC-05-RET / GAP-OCARCH-05 se alinea con la copia común | decidido (usuario, 2026-11-10, D7); la copia común aún no existe (COP-01 sin destino a 2026-11-13); network concilió su texto con D7 en `85c4708` | los datasets que el laboratorio congela al cortar (hoy uno: `oc03_s20261112_c20261113`); `lake delete` no se usa sobre `market.*` hasta que exista la copia |

Filas en [DEPENDENCIAS.md](../DEPENDENCIAS.md) «Dependencias de tarea».

## 6. GAPs abiertos

- ~~**GAP-BACKLOG_README-01 — ¿Cuándo vuelve TI-09-ARCH?**~~ **RESUELTO con su opción (c) (usuario, 2026-11-10, revisión
  de planes, D11):** TI-09-ARCH espera a OC-03 y a unos 20 días hábiles de capturas, con la sonda semanal de §3, y sin
  spot de respaldo. Texto histórico (abierto; se preguntaba al planificar el próximo sprint del laboratorio). Opciones: (a) reabrir en SPRINT-01 ya en modo «mientras tanto»; (b) fila de SPRINT-02 del laboratorio;
  (c) esperar a OC-03 y a unos 20 días hábiles de capturas. Recomendación: (c), con la sonda semanal de §3. Si no se
  decide: sigue en el backlog; el riesgo de no ver una racha sin captura lo cubre la alerta del backend.
  *Novedad 2026-11-10:* (a) y (b) necesitan además un spot de acciones que hoy no está en el lago y cuyo cierre de
  16:00 ET no casa con la captura de las 14:00 ET (C-ARCHIVO_OPCIONES-01); (c) no lo necesita, porque OC-03 trae
  `underlying_price`. Refuerza la recomendación (c). Pendiente aún: ni OC-03 ni la sonda se han ejecutado.
- ~~**GAP-ARCHIVO_OPCIONES-01 — Forma de la copia propia**~~ **RESUELTO (usuario, 2026-11-10, revisión de planes, D7):**
  no hay copia propia; el laboratorio sólo guarda lo leído al cortar cada dataset, con hash, y la copia del lago es la
  común de network. Texto histórico (abierto, nuevo el 2026-11-09). ¿Copia incremental diaria
  (tarea programada del laboratorio a `E:/quantdesk-lab/`, con hash por día) o copia de todo lo leído al cortar cada
  dataset? La diaria cubre un borrado entre cortes; la del corte no añade tareas programadas pero deja ventanas sin
  copia. Se decide al planificar TI-09-ARCH, junto con GAP-BACKLOG_README-01.
- ~~**GAP-ARCHIVO_OPCIONES-02 — ¿Una copia propia por proyecto o una sola compartida?**~~ **RESUELTO con la opción (c)
  (usuario, 2026-11-10, revisión de planes, D7):** una sola copia, la común de network (`PLAN_COPIA_PERIODICA_LAGO`);
  `lake delete` no se usa sobre `market.*` hasta que exista. Texto histórico (abierto, nuevo el 2026-11-10). Backend (GAP-OCARCH-05) y laboratorio planifican a la vez una copia de `market.options.chain`, con el mismo dato de
  origen y plazos distintos; network tiene además `PLAN_COPIA_PERIODICA_LAGO` sin destino decidido (COP-01). Opciones:
  (a) copias independientes (laboratorio a `E:/quantdesk-lab/` con hash; backend la suya): máxima independencia, el
  doble de tráfico contra qn y dos mecanismos que mantener; (b) una sola copia del backend, de la que el laboratorio
  lee y congela sus cortes: un único mecanismo, pero la fuente de verdad del laboratorio pasa a depender de un destino
  del backend aún sin decidir; (c) sumarse a la copia común de network cuando decida destino: cubre todo el lago, sin
  fecha. Recomendación: decidirlo junto con GAP-OCARCH-05 y GAP-ARCHIVO_OPCIONES-01, y mientras tanto (a) en su forma
  mínima (copia de lo leído al cortar, que no añade tareas). Si no se decide: no hay copia hasta que se use `lake delete`
  o se planifique TI-09-ARCH.

## Revisión de planes (2026-11-10, parcial)

(La revisión del 2026-11-09 no dejó sección propia en este plan, que nació de ella por división: sus decisiones están en
la cabecera, §2–§4 «(usuario, 2026-11-09)» y en [REVISIONES.md](REVISIONES.md).)

Veredicto: **ACTUALIZAR** (aplicado) · Motivo: la especificación sigue vigente y nada de lo pendiente se ha hecho, pero
tres premisas no se sostienen contra el código y los datos de hoy: el spot de respaldo de las acciones no está en el
lago, las filas anteriores a OC-03 no se pueden «reinterpretar con `captured_at`» y la corrección de SPRINT-01 choca con
su archivo. Además, la copia propia se solapa con la del backend. No se funde ni se divide: el scraper es del backend y
la copia común, de network (GOBERNANZA).

Cambios desde la revisión de 2026-11-09: SPRINT-01 cerrado y archivado (`d4a83b5`, `083cf72`); TI-12-MT5 cerrada
(`fdfa3a7`, `beaf81c`) y primera descarga m1/m5 local (`b7b074c`); issues de FX diario (`6425818`, backend `e90eb03`);
el backend no ha avanzado OC-03/OC-04/OC-05 (siguen en su `next/SPRINT.md`) ni ha publicado nuevas cifras de cadenas
(último dato: run `157c2754` del 2026-11-09, día hábil 1 de 3); network no ha abierto la tarea 3.4 ni empezado la
herramienta de borrado. Ni la sonda ni el archivo de opciones se han ejecutado.

| Tarea | Clasificación | Evidencia / motivo |
|---|---|---|
| TI-09-ARCH (lector, modo «mientras tanto») | MODIFICADO | Agrupación por `_ts` y sesión de NY (`options_downloader.py:339`, `market_sink.py:174`); empalme con OC-03; spot de acciones no está en el lago (inventario TI-01-INV; `E:/quantdesk-lab/data/mt5/us_grandes_1d_20261109` local) |
| TI-09-ARCH (universo ETF/INDEX) | MODIFICADO | El respaldo «OHLCV diario» sólo aplica si la tarea de ETF llega antes de OC-03 (backend `PLAN_OPTIONS_CHAIN_ARCHIVO` OC-03 (c)) |
| TI-09-ARCH (copia propia) | MODIFICADO (D7: sin copia propia; copia común de network) | Backend OC-05-RET/GAP-OCARCH-05 planificaba lo mismo; `E:/quantdesk-lab/` sin datos de opciones; network 3.4 sin abrir |
| TI-09-SONDA | MODIFICADO (aceptación 2) | SPRINT-01 archivado con SHA-256: no se reescribe (C-ARCHIVO_OPCIONES-03); se añade el recuento de capturas por día; sigue sin ejecutarse (puerta de usuario). Datos: SIN VERIFICAR |

GAPs al redactar la revisión: GAP-ARCHIVO_OPCIONES-02 (copia propia compartida o por proyecto), GAP-BACKLOG_README-01 y
GAP-ARCHIVO_OPCIONES-01 (novedad anotada en §6). **Los tres quedaron resueltos por el usuario el 2026-11-10** (revisión de
planes, D7 y D11): ver «Decisiones del usuario» más abajo. No queda ningún GAP abierto en este plan.

Contradicciones: C-ARCHIVO_OPCIONES-01 (spot de acciones), C-ARCHIVO_OPCIONES-02 (reinterpretar con `captured_at`),
C-ARCHIVO_OPCIONES-03 (corregir SPRINT-01 archivado). Detalle en el informe de la revisión; **las tres resueltas**
(-01 por D11; -02 y -03 por regla, sin pregunta).

Sinergias: backend `PLAN_OPTIONS_CHAIN_ARCHIVO` (OC-03, GAP-OCARCH-05) y `PLAN_PUBLICADORES_MERCADO_PUBLICO` (PUB-03:
acciones diarias); network `PLAN_RETIRADA_TOPICS_EVENTOS` (3.3, 3.4) y `PLAN_COPIA_PERIODICA_LAGO` (COP-01);
[PLAN_DATOS_VIA_QN](PLAN_DATOS_VIA_QN.md) (MT5 acciones en qn y TI-02-DATA-V2 para el exportador); quantdesk
`PLAN_TSFM_FINANZAS` §3 (se corrige con la cifra de la sonda).

### Decisiones del usuario (2026-11-10, revisión de planes)

Fuente de todas: usuario, 2026-11-10, revisión de planes.

| Decisión | Resuelve | Efecto en este plan |
|---|---|---|
| D7 «Copia común de network» | GAP-ARCHIVO_OPCIONES-01, GAP-ARCHIVO_OPCIONES-02 (y GAP-OCARCH-05 del backend) | Sin copia propia del laboratorio ni del backend; la copia de `market.options.chain` es la de `PLAN_COPIA_PERIODICA_LAGO`; el laboratorio sólo guarda lo leído al cortar cada dataset, con hash; `lake delete` no se usa sobre `market.*` hasta que exista la copia común |
| D11 «Quitar el respaldo» | C-ARCHIVO_OPCIONES-01, GAP-BACKLOG_README-01 (opción (c)) | Se elimina el «subyacente del OHLCV diario» como spot de respaldo; sólo `underlying_price` de OC-03; TI-09-ARCH espera a OC-03 y a unos 20 días hábiles de capturas |
| Por regla | C-ARCHIVO_OPCIONES-02, C-ARCHIVO_OPCIONES-03 | El lector deriva la sesión desde `_ts` (las filas anteriores a OC-03 no tienen `captured_at`; se corrige la frase de OC-03(b) en el plan del backend); el archivo de SPRINT-01 no se reescribe |

## Revisión de planes (2026-11-13)

Veredicto: **ACTUALIZAR** (aplicado) y **BORRAR/ARCHIVAR tras S02-6** (recomendado; no se hace hasta que cierre la
medición, no antes del 2026-12-11) · Motivo: la parte de laboratorio de TI-09-ARCH está entregada y aceptada (SPRINT-02
fila 6, `c6c7b5b`/`a62d78f`/`a80ad40`), OC-03 del backend y los siete ETF/índices están servidos, y la única tarea que
queda con fecha y aceptación (la medición de cobertura) ya vive como S02-6 en [next/SPRINT.md](../next/SPRINT.md): este
plan no aporta tareas propias. TI-09-SONDA está casi cubierta por la sonda del 2026-11-13. No se absorbe en SPRINT-03
como plan, porque se duplicaría S02-6; sólo entra la fila S02-6 (refinada) y una fila corta para cerrar la sonda. La
retención (§4) es de network: aquí sólo queda como dependencia vigilada.

| Tarea | Clasificación | Evidencia / motivo | ¿Lista para SPRINT-03? (nivel, dependencias, puerta) |
|---|---|---|---|
| TI-09-ARCH lector y archivador (parte laboratorio) | HECHO | `scripts/archivo_opciones.py`, `scripts/archivo_opciones_lib/{lector,flujo,validacion}.py`, `scripts/descarga_opciones.py`; `1b92162`, `fba4279`, `722effa`, `c6c7b5b`, `a62d78f`, `a80ad40`; dataset `oc03_s20261112_c20261113` `sha256:eb98ac6a…eea1` en `E:/quantdesk-lab/datasets/TI-09-ARCH/` | No hace falta |
| Aceptación 1 (dos lecturas, mismo SHA-256) | HECHO sobre fixture; sobre el lago real, DUPLICADO en S02-6 | Fixture 204 → 201 filas, hash `4341ec59…8412` idéntico en la doble ejecución y en `equivalencia_c2.json`; sobre el lago real el dato queda para el corte posterior al 2026-12-10 | Entra con S02-6 |
| Aceptación 2 (filtro documentado, exclusiones por motivo) | HECHO | `informe.md` del dataset: motivos `vencimiento_pasado`, `sin_cotizacion`, `monotonia`, `convexidad`, `calendario` (63.267 por convexidad, 14,7 % de la cadena: vigilar) | No hace falta |
| Aceptación 3 (informe de días hábiles sin captura por subyacente) | HECHO para 1 sesión | Sección «Huecos por subyacente y `asset_type`» del informe, 509 + 7 obligatorios; se vuelve a generar en S02-6 | Entra con S02-6 |
| Aceptación 4 (cobertura ≥ 98 % en 20 días hábiles) | DUPLICADO (S02-6) | Calendario NYSE declarado en el informe: 20 sesiones desde el 2026-11-12, la 20.ª es el 2026-12-10 (Thanksgiving 2026-11-26 fuera) | Sí, desde el 2026-12-11 (L5; token nuevo, puerta de usuario). Falta definir la métrica (GAP-ARCHIVO_OPCIONES-03) |
| Modo «mientras tanto» (agrupar `_ts`, sesión de NY) | OBSOLETO | No implementado: el lector ignora filas sin `capture_id` (EXECUTION SPRINT-02, 2026-11-13, respuesta de `quantdesk-backend-89`); C-ARCHIVO_OPCIONES-07 | No |
| Captura al cierre con spot (OC-03-CLOSE) | HECHO (backend; dependencia servida) | Backend `cc1811d` (despliegue 2026-11-12), aceptación en producción `5723017`; primer cierre completo `capture_id` `2026-11-12-163125-5b2305`; el lector usa `capture_id` y `underlying_price` | No hace falta |
| Universo ETF/INDEX | HECHO | Siete obligatorios en OC-03 y en `lector.py:47`; el dataset trae SPY, QQQ, IWM, DIA (`ETF`) y ^SPX, ^NDX, ^VIX (`INDEX`) | No hace falta |
| §4 copia común (D7) | MOVER a network (COP-01/02/03/08) | Network concilió D7 en `85c4708` (2026-11-13); COP-01 sin destino; condición sobre `lake delete` vigente | No es tarea del laboratorio; se vigila |
| TI-09-SONDA | MODIFICADO (casi HECHO) | Sonda de contraste 2026-11-13 (token id 39, revocado) + dataset; falta aceptación 2 (STATUS y aviso a quantdesk) y decidir si se mide el 2026-11-09..11 | Sí, fila corta (L2, sin puerta si GAP-ARCHIVO_OPCIONES-04 = a) |
| Sonda semanal repetida | OBSOLETO | Sustituida por S02-6 (OC-03 ya servida) | No |
| Tarea 3.4 de network (issue de aviso a este repo) | OBSOLETO | Sustituida por la conciliación `85c4708` y el aviso de la raíz | No |

GAPs al redactar la revisión (estado tras las decisiones del usuario del 2026-11-13):
- GAP-ARCHIVO_OPCIONES-03: ¿cómo se mide la «cobertura ≥ 98 %» de S02-6 (días con captura completa o pares subyacente-día) y contra qué universo? **Abierto, diferido:** recomendación por defecto en la fila S02-6 (SPRINT-03 fila 3): días con captura completa (≥ 95 % del universo esperado y los 7 obligatorios) sobre 20, y por separado pares subyacente-día frente a los 510 del backend; se confirma al hacer la ficha de S02-6.
- ~~GAP-ARCHIVO_OPCIONES-04: ¿TI-09-SONDA se cierra con la sonda del 2026-11-13 y el dataset (sin medir el 2026-11-09..11)?~~ **RESUELTO (usuario, 2026-11-13, revisión de planes, R4):** se cierra con la cifra por sesión de S02-6 desde el 2026-11-12; 2026-11-09…11 no medibles (§3).
- GAP-ARCHIVO_OPCIONES-05: ¿hay cortes del laboratorio después de S02-6 (cadencia) mientras no exista la copia común? **Abierto, diferido** (cortes bajo demanda; se pregunta al cerrar S02-6, antes de archivar este plan).
- ~~GAP-ARCHIVO_OPCIONES-06: ¿S02-6 sigue esperando a quantdesk SPRINT-03 o se ejecuta en cuanto llegue su fecha?~~ **RESUELTO (usuario, 2026-11-13, revisión de planes, R1):** S02-6 está en el SPRINT-03 nuevo, sin dependencia de entrada; se ejecuta desde el 2026-12-11.

Contradicciones: C-ARCHIVO_OPCIONES-04 (S02-6 «no depende de quantdesk» frente a la dependencia de entrada de
SPRINT-03), C-ARCHIVO_OPCIONES-05 (STATUS y `PLAN_TSFM_FINANZAS` dicen «vacío»), C-ARCHIVO_OPCIONES-06 (aceptación de
S02-6 y calendario con fecha frente a «20 días hábiles siguientes a la entrega»), C-ARCHIVO_OPCIONES-07 (modo «mientras
tanto» frente a lo implementado). Detalle en el informe de la revisión. **Resolución (2026-11-13):** -04 por R1 (SPRINT-03
sin dependencia de entrada); -05 por regla (STATUS corregido; `PLAN_TSFM_FINANZAS` lo corrige `quantdesk` con aviso de la
raíz); -06: vale la ventana de la fila S02-6, desde la sesión 2026-11-12 hasta el 2026-12-10, decidida en el arrastre del
2026-11-13 (diferido sin pregunta); -07 por regla (el modo «mientras tanto» queda obsoleto por OC-03).

Sinergias: S02-6 ↔ aceptación 6 y OC-04-TIME del backend (la duración de los runs con ETF puede dejar días sin captura
completa); network COP-01/02/03/08 y 3.3 (copia común); quantdesk `PLAN_TSFM_FINANZAS` §3 (corregir «ninguna fila»),
TS-16-QCONO y TS-08-DYN (consumidores del dataset; GAP-TSFM-02); [PLAN_DATOS_VIA_QN](PLAN_DATOS_VIA_QN.md) (mismo patrón
de volcado en mini con token de lectura de corta vida).

### Decisiones del usuario (2026-11-13, revisión de planes)

Fuente de todas: usuario, 2026-11-13, revisión de planes (registro en [REVISIONES.md](REVISIONES.md)).

| Decisión | Resuelve | Efecto en este plan |
|---|---|---|
| R1 Partir SPRINT-03 | GAP-ARCHIVO_OPCIONES-06, C-ARCHIVO_OPCIONES-04 | S02-6 es la fila 3 del SPRINT-03 nuevo, sin dependencia de entrada; se ejecuta desde el 2026-12-11 |
| R4 Sonda | GAP-ARCHIVO_OPCIONES-04 (y GAP-ISSUES-01), C-ARCHIVO_OPCIONES-05 (con la corrección de STATUS) | TI-09-SONDA se cierra con la cifra por sesión de S02-6 desde el 2026-11-12; 2026-11-09…11 no medibles; su fila se une a S02-6 |
| Diferidos | GAP-ARCHIVO_OPCIONES-03, -05; C-ARCHIVO_OPCIONES-06 | -03: métrica por defecto en la fila S02-6, se confirma al hacer su ficha; -05: cortes bajo demanda, se pregunta al cerrar S02-6; -06: ventana 2026-11-12…2026-12-10 de la fila |
| Por regla | C-ARCHIVO_OPCIONES-07 | Modo «mientras tanto» obsoleto por OC-03 |

Destino del plan: **backlog residual**; se archiva cuando cierre S02-6 (no antes del 2026-12-11). GAPs abiertos que
quedan: GAP-ARCHIVO_OPCIONES-03 y -05 (diferidos). Contradicciones abiertas: ninguna.

[PLAN_TSFM_INTEGRACION]: S:/projects/quantdesk/docs/plans/backlog/PLAN_TSFM_INTEGRACION.md
