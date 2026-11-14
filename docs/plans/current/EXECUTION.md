# EXECUTION — SPRINT-03 de quantdesk-model

Registro de ejecución del sprint: arranques, lecturas de cuota, mensajes entre raíces, intentos, aceptaciones y
decisiones del usuario, con fecha y hora local (CET).

## 2026-11-14 — activación

- **00:3x.** Raíz de guardia `quantdesk-model-4d` arranca (`guardia.md`). Commit pendiente de la guardia `c4` hecho y
  empujado: `41efbbf` (revisión de planes del 2026-11-13), `8ad2a86` (arranque de guardia y kanban), `2e81fb6`.
- Presentación a las raíces vivas: `quantdesk-f1`, `quantdesk-backend-24`, `quantdesk-network-21`.
  - network: `market.*` sin cambios de retención, esquema ni borrado; la Fase 3 (borrado) irá en el sprint que siga a
    COP y rechazará `market.*` en `main`; visto bueno de 4c/5, tras el desbloqueo de MT5.
  - backend: `fred_oas_capture_schedule` aún sin activar; esperan nuestra propuesta conjunta del contrato de
    TI-02-DIARIO en SPRINT.md §3; sus restricciones de PUB-05-EXPORT no cambian.
  - quantdesk: aplicados nuestros dos avisos en su commit `3eb4c799` (sin push): PLAN_TSFM_FINANZAS sin las premisas de
    «cero cadenas» (`market.options.chain` con datos desde OC-03; `market.options.fx` vacío; cifra de la sonda C-07
    pendiente) y su DEPENDENCIAS ajustado a nuestra renumeración. Su SPRINT-02 sigue abierto; sin cambios en la rueda,
    TI-03-FMT ni DL-02-GATES.
- **Decisión del usuario (2026-11-14):** «vale» a planificar e iniciar SPRINT-03 empezando por la fila 1.
- `deps.py --repo . --sprint SPRINT-03`: **LISTO**, 0 dependencias de entrada.
- Cuota (00:39): Claude 78 % (ventana 56,9 %, reinicio 2026-11-16 23:59 UTC); Codex 61 % (ventana 37,8 %, reinicio
  2026-11-18 08:07 UTC). Orden temporal del usuario: Codex implementa y revisa hasta el 2026-11-17 00:59.
- Revisión de alertas (`alertas.md`): no existía `ultima.json`; lanzada a las 00:45 con `gpt-6.1-sol` high
  (supervisor PID 29448; informe `.git/sprint-runtime/alertas/alertas-20261114-0045-salida.md`).
- Revisión de planes: la última es del 2026-11-13 (dentro del umbral); no se repite.
- Planificación completada: §8 de capacidad, LAUNCH.md y este registro. Los planes del backlog no se reducen (sus IDs
  son más amplios que las filas). Tag de fuentes `archive/2026-11-14/sprint-03-sources`.
- Activación: dossier movido de `next/` a `current/`, `future/SPRINT-04` promovido a `next/` (En planificación, premisas
  por revalidar), fichas ISSUE-TI09-SONDA-CADENAS e ISSUE-TI12-MT5-INTRADIA-LOCAL a `current/issues/`. Enlaces
  recalculados con un script que resuelve cada enlace relativo contra su ubicación anterior, también en el archivo
  (cambio editorial de enlaces: cambian los SHA-256 de los ficheros de `archive/` tocados). Commit `4535ef6`.
- **Alertas (informe de las 00:42):** 0 urgentes, 0 por gestionar; IGNORAR la parada de MT5 (cuenta bloqueada, tarea
  desactivada por R2). Alertmanager responde por SSH desde el VPS. Límite: MT5 sin sonda ni alerta en el Prometheus del
  backend. Bloque de URL y filtro versionado en SPRINT_PROJECT §12. Próxima revisión: después de las 08:45.

- **Aviso de network (informativo):** el usuario elevó D7 a principio del ADR-001 (§5 A1, network `34eacdf`): el bucket
  `qn-lakehouse` necesita una copia verificada y, mientras no exista, `market.*` no se reconstruye ni se borra (`lake
  delete` rechaza `market.*` en `main`). La copia común (COP) sigue siendo el respaldo de TI-09-ARCH. Sin cambios aquí.

## Fila 1 — contrato de TI-02-DIARIO (L3)

- **00:5x.** Borrador encargado a Codex `gpt-6.1-sol` high en `--sandbox read-only` (intento a1; ficha en
  `.git/sprint-runtime/s03/TI-02-DIARIO-contrato/ficha.md`; supervisor PID 14660). Revisión: las raíces del backend y de
  `quantdesk` por mensaje y la aprobación del usuario (es un contrato, no código).
- **~01:10.** Borrador a1 terminado (exit 0) y aceptado como base: [borrador-contrato-a1.md](execution/TI-02-DIARIO/borrador-contrato-a1.md),
  con la revisión de la raíz encima. Hay dos opciones en el punto a: A1, Dagster invoca por SSH al PC; A2, tarea de
  Windows con un sensor de frescura en Dagster. Dos errores para la fila 2 (`volume_kind`, limpieza OHLCV). Referencia
  S03-D4 corregida a S03-D3 en SPRINT.md. Se envía a las raíces del backend, de `quantdesk` y de network.
- **Respuesta de network:** `sub:market.ohlcv.v2` basta. El corte es reproducible con `x-qn-head-cycle` (H) guardado
  en el manifiesto y el filtro `_cycle <= H`, sin `fresh=true`. Para los OAS se emite otro token. Se emite con
  `qn-token` tras la aprobación. Detalle en el borrador, «Respuestas de las raíces». Quantdesk: revisión en curso.
- **Respuesta del backend:** prefieren A2 (tarea de Windows registrada por ellos con `run_scheduler.cmd`). La señal de
  salida válida va por qn, como un objeto de estado en un topic de operaciones que hay que acordar con network; su sensor
  alimenta `DagsterJobStale`, y la credencial añade `pub` sobre ese topic. Sin señal de fin de MT5: se mira el `/latest`
  de la vela. Están de acuerdo con el horario, con `sin_mt5` y con la credencial. Los OAS están en percent y PUB-02
  sigue pendiente. Se consulta a network por el topic de estado.
- **Network, topic de estado:** sin norma en contra y prefiere esta vía a abrir Pushgateway. Propone
  `ops.export.status` (objeto, tag `job`, esquema cerrado, `max_staleness` 2d, `batch_id` determinista) y un token con
  `sub:market.ohlcv.v2` + `pub:ops.export.status`, `--envs main`. Tras la aprobación: issue en su repo con el JSON.
  Sólo falta quantdesk.
- **Respuesta de quantdesk:** confirma la ruta y el formato del desktop, el mapa de símbolos desde `daily.universe()` y la
  apertura de market-history por ruta explícita. Los JSON del mercado del día siguen con sus notebooks. Limpieza: rechazo
  o cuarentena, sin `repair_ohlcv_range`. Lleva las mismas decisiones al usuario.
- **Propuesta conjunta consolidada:** [contrato-propuesta.md](execution/TI-02-DIARIO/contrato-propuesta.md).
- **Decisión del usuario (2026-11-14, AskUserQuestion):** aprueba las cuatro recomendaciones:
  - A2, tarea de Windows;
  - sólo OHLCV + history (los JSON siguen con los notebooks de `quantdesk`);
  - topic `ops.export.status` y token `sub:market.ohlcv.v2` + `pub:ops.export.status`;
  - el resto de la propuesta tal cual.
  Escrito en GOBERNANZA, DEPENDENCIAS, PLAN_DATOS_VIA_QN §4 y SPRINT.md §2/§4.
- **Aviso de `quantdesk-f1`** (usuario, ~01:30): la cuenta MT5 sigue bloqueada y el usuario estudia pagar por datos. La
  fuente del FX queda como parámetro de la política de fuentes (nota en el contrato); afecta también a las filas 4a–4c y 5.
- **Network:** su raíz pasó a `quantdesk-network-b2` (SPRINT-02 activo), que registrará `ops.export.status` y emitirá el
  token con confirmación del usuario. El valor del token va directamente al usuario.
- **Backend:** contrato registrado en su PUB-05-EXPORT; ha pedido a network su `sub:ops.export.status` (issue `4676dfe`).
  Registrará la tarea cuando le pasemos la orden exacta. Su sensor mide la frescura con el instante de la salida válida
  (`ts` del sobre, cuando termina la validación) y asume `sin_mt5` diario mientras MT5 siga bloqueado.
- **Fila 2, preparación:** el escritor `quantdesk.daily.write_ohlcv` está en la rueda del `.venv`. Se pregunta a `quantdesk`
  por `FX_DATE_SHIFT = 1` (`daily.py:97`, se aplica en su notebook 28): no se sabe si el `ts_ms` del FX de MT5 en el
  desktop va sin desplazar. La ficha espera la respuesta (`quantdesk-f1`: su revisor lo contrasta con el notebook 28;
  piden no encargar el código hasta entonces). Se pregunta a `quantdesk-network-b2` si los tokens van atados a host
  (docstring de `descarga_lago.py`) y qué `QN_URLS` alcanza el PC por LAN.
- **Respuesta de `quantdesk-network-b2`:**
  - Los tokens **no** van atados a host: viven en el Postgres de metadatos que comparten las tres réplicas. La frase del
    docstring es una norma operativa (el fichero del token se queda en el host del cliente), no una restricción técnica:
    hay que corregirla en la fila 2.
  - El HTTP de qn en la LAN no tiene TLS, por eso el token es exclusivo y de concesión mínima.
  - Base `http://<host>:8790/qn`, comprobada desde el PC (`/health` 200, `/qn/api/v1/topics` 401 sin token). `QN_URLS`
    recomendado: `http://192.168.1.48:8790/qn,http://192.168.1.46:8790/qn,http://192.168.1.45:8790/qn` (macold, mini y
    silver la última, ISSUE-SILVER-GPF). `descarga_lago.py` sólo usa la primera URL: el exportador diario debe pasar a la
    siguiente si una réplica no responde.
  - El JSON de `ops.export.status` está escrito y en test. Registro y token esperan la confirmación del usuario.
- **Fila 1 cerrada** con el contrato decidido. Siguen: issue/JSON del topic a network, aviso al backend y encargo de la
  fila 2.
- **Norma nueva de la skill** (usuario, 2026-11-14, retransmitida por `quantdesk-f1`): al preparar un sprint entra todo
  lo pendiente (backlog, issues abiertos y arrastres) y la revisión de planes revisa también los issues. Si las
  dependencias o la capacidad no lo permiten, se ofrece partir el sprint explicando tarea por tarea. SPRINT-03 ya lo
  cumplía (R0); se aplica al planificar SPRINT-04.

## Relevo 1 (2026-11-14 01:16, sesión `quantdesk-model-00`)

- HANDOFF aceptado; `deps.py --sprint SPRINT-03`: LISTO. Cuota (01:20): Claude 80 % (reinicio 2026-11-16 23:59 UTC),
  Codex 62 % (reinicio 2026-11-18 08:07 UTC). Alertas: última revisión 00:45, toca pasadas las 08:45.
- Vigía `wsvigia.py` en el puerto 8775 (`.git/sprint-runtime/s03/wsvigia.pid`), seguido con Monitor; `relevos.json` →
  `quantdesk-model-00`.
- **Aviso de cambio en la skill** (`quantdesk-f1`, usuario 2026-11-14, SKILL.md §0): todo cambio en la skill sprint
  (norma, referencia o `tools/`) se avisa en el momento por SendMessage a cada raíz viva; quien lo recibe lo anota. Sin
  acción para nosotros salvo aplicarlo si editamos la skill.
- **Respuesta de `quantdesk-f1` sobre `FX_DATE_SHIFT`** (detalle con ruta:línea en
  `S:/Projects/quantdesk/.git/sprint-runtime/s02/TI02-REVISION/respuesta2.md`):
  1. FX de MT5 de la sesión D: `ts_ms = D 00:00 UTC`, **sin** `FX_DATE_SHIFT`. `ts_ms` es la etiqueta de sesión, no el
     instante de cierre (95_ohlcv_market_day_history:26). El shift de Yahoo es un `shift(-1)` de valores al preparar
     (notebooks 28, 94, 95); ningún lector vuelve a desplazar.
  2. Acciones y SPX: sin desplazamiento, fecha de sesión D.
  3. Rango: ventana histórica explícita hasta D con cobertura declarada en `index.json`; nunca un fichero con sólo D.
  4. Reutilizar `quantdesk.daily.write_ohlcv` con `sources` para todos los símbolos; datos ya validados, únicos y
     ordenados; versiones de quantdesk, pandas y pyarrow fijadas; sin `clean_ohlcv` (rellena volumen con 0); escritura en
     carpeta temporal y publicación tras validar Parquet e índice.
  Con esto se desbloquea la ficha de la fila 2.
- **Network (`quantdesk-network-b2`):** `ops.export.status` registrado en producción, env main (HTTP 201, versión 1,
  2026-11-14T00:21:46Z; esquema del contrato sin cambios, network `4c5c1ac`). Token del exportador emitido con el visto
  bueno del usuario: `ti02-exportador-20261114`, id 43, `sub:market.ohlcv.v2` + `pub:ops.export.status`, `--envs main`,
  sin caducidad; el valor se queda en mini y el usuario lo copia al `.env` privado del PC. Variable que lee el exportador:
  `QN_TOKEN` (del entorno o de `E:/quantdesk-lab/secrets/ti02-diario.env`).
- **Aviso de cambio en la skill** (`quantdesk-f1`, SKILL.md §0 «Compilación normal, sin exportaciones»): Rust y C++ se
  compilan en el checkout del proyecto por el gate, sin copias `git archive`. Afecta a SPRINT_PROJECT §3 «Build» de este
  repo (ruedas de `quantdesk` en `E:/quantdesk-lab/build/<commit>/`): se revisa cuando haga falta una rueda nueva.
  La fila 2 no compila nada.
- **Fila 2: ficha escrita** (`.git/sprint-runtime/s03/TI-02-DIARIO-codigo/ficha.md`, base `aab7ade`), contrastada con
  `nucleo.py:163-172` (el `_ts` del 1d de MT5 ya es D 00:00 UTC), `descarga_lago.py`, `daily.py` de la rueda, el esquema
  de network y `calendarios.py`. Decisiones de la raíz en la ficha: ausencia parcial de FX MT5 = `sin_mt5` (no se publica
  un día FX incompleto); `manifest_sha256` = hash del manifiesto lateral del intento también en `sin_mt5`/`error`;
  festivo FX conocido sin barras = `ok` sin publicación nueva. Revisión de la ficha: Codex `gpt-6-luna` high, sólo
  lectura (PID 17992).
- **Revisión de la ficha** (`gpt-6-luna` high, exit 0, `revficha-salida.md`): una observación, aceptada: la comprobación
  previa de barras FX se limita a sesiones FX (los festivos FX versionados son ausencia esperada, contrato §4). Corregida
  en la ficha.
- **Fila 2 encargada** (2026-11-14 ~01:55): autor Codex `gpt-6.1-sol` xhigh, intento 290 en la BDD, lanzado con
  `lanza.py`/`hijo.py` (PID de lanza en `TI-02-DIARIO-codigo/lz-autor-a1.pid`), seguido por el vigía. Revisor previsto:
  `gpt-6-astra` high, con ficha + diff.
- **Plan nuevo para el backend** (usuario, 2026-11-14): rsc-brain como cerebro wiki y memoria común de todos los
  proyectos para la skill global, con Postgres reciclado (hueco de mem0 en `qn-pgprod`) y nginx. Borrador en
  `.git/sprint-runtime/propuestas/PLAN_RSC_BRAIN.md`, entregado a `quantdesk-backend-24` para su
  `docs/plans/backlog/PLAN_RSC_BRAIN.md` (dueño del compose y nginx según su GOBERNANZA). Pendiente su confirmación con
  commit. Cinco GAP para el usuario en el plan.
- **PLAN_RSC_BRAIN adoptado por el backend** (`quantdesk-backend-24`, commit `c01e49d` de su repo): plan en su backlog, línea en su índice y fila de GOBERNANZA «propuesto». Entra al planificar su siguiente sprint, junto a PLAN_RETIRADA_MEM0. GAP 1-5 pendientes del usuario.
- **Aviso de cambio en la skill** (`quantdesk-network-b2`, usuario 2026-11-14): `sprint_db.py task` y `attempt start/end` ya regeneran `~/.claude/sprint-db/index.html`; `update` sólo hace falta cuando cambian ficheros del repo (`references/sprint-db.md`). Sin acción.
