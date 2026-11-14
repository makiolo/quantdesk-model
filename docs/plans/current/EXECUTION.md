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
- **Fila 2, entrega a1** (`4c34af1` oráculo rojo, `237220f` verde; gate 15/15; diferencial: sólo `volume_kind`
  `traded`→`tick_count` en 3 filas MT5). Rutas autorizadas comprobadas por la raíz. **Revisión r1** (`gpt-6-astra` high,
  intento 309): **RECHAZAR**, A5 legítimo, gate 15/15 reproducido, oráculo con contraste independiente válido. Tres
  bloqueantes reproducidos con qn local (`E:/quantdesk-lab/runs/TI-02-DIARIO/revision-r1/informe.txt`):
  1. `nucleo.py:147`: `sin_mt5` falso si `latest` muestra una republicación de D posterior a C o una barra de D+1;
  2. `nucleo.py:361`: un 202 con `durable=false` se toma como éxito;
  3. `nucleo.py:369`: si qn acepta el `ok` y se pierde la respuesta, se borran los productos y queda un `ok` sin datos.
  Intento 290 → rechazada.
- **Segunda vuelta** con la misma sesión de Codex (`codex exec resume`). El primer relanzamiento (intento 313) arrancó con
  `gpt-5.6-terra`, porque `resume` sin `-m` no conserva el modelo de la sesión: parado con `arbol.py --kill` a los ~30 s,
  sin cambios en el árbol (fallida). Relanzado con `-m gpt-6.1-sol` xhigh (intento 314).
- **Fila 2 CERRADA (TI-02-DIARIO, código sin OAS)**, 2026-11-14 ~04:00. Entrega a2: `cd87b05` (regresiones rojas) y
  **`a47ccf4`** (arreglo), sobre `4c34af1`/`237220f` de a1.
  - **Revisión r2** (`gpt-6-astra` high, reanudando la sesión de r1, intento 322): **ACEPTAR**, sin hallazgos. Los
    tres bloqueantes de r1 quedan resueltos y sus reproducciones dan el resultado correcto. Las 8 regresiones fallan por
    aserción sobre `237220f` y pasan sobre `a47ccf4`. **A5: legítimo**: contra Base sólo se añade cobertura; frente a a1,
    `prueba_previa` cambia por contrato. Evidencia en `E:/quantdesk-lab/runs/TI-02-DIARIO/revision-r2/informe.txt`
    (sha256 `d647e90e…179c`).
  - **Gate de la raíz** sobre HEAD fijo `a47ccf4`, sin cambios en `scripts/` antes ni después:
    `scripts/run_selftests.py` 15 OK, 0 FALLO; incluye `exportar_diario.py` (19 grupos) y `smoke_env` (21
    comprobaciones).
  - **Diferencial contra `aab7ade`:** sólo cambia `volume_kind`, de `traded` a `tick_count`, en 3 filas MT5; Binance y
    las demás columnas, intactas (`E:/quantdesk-lab/runs/TI-02-DIARIO/autor-r2/diferencial.json`).
  - **BDD:** intentos 290 rechazada, 309 aceptada (revisión), 313 fallida (modelo equivocado), 314 aceptada y 322
    aceptada; tarea `cerrada`.
  - **Orden para la tarea de Windows** (para el backend, PUB-05-EXPORT):
    `S:/Projects/quantdesk-model/.venv/Scripts/python.exe -X utf8 scripts/exportar_diario.py --ejecutar`.
    - Se ejecuta con cwd `S:/Projects/quantdesk-model`, de martes a sábado a las 00:15 UTC.
    - Variables: `QN_URLS=http://192.168.1.48:8790/qn,http://192.168.1.46:8790/qn,http://192.168.1.45:8790/qn` y
      `QN_ENV=main`. `QN_TOKEN` se lee del entorno o de `E:/quantdesk-lab/secrets/ti02-diario.env`.
    - Salida: 0 `ok`, 3 `sin_mt5`, 1 `error`, 2 uso.
  - **Pendiente fuera de la fila:**
    - el usuario copia el token id 43 a ese `.env`;
    - el backend registra la tarea y el sensor;
    - primera ejecución real. Con la cuenta MT5 bloqueada saldrá `sin_mt5`, que es lo esperado.
- **Raíz de `quantdesk` cambiada:** `quantdesk-f1` (relevo 56) pasó la raíz a `quantdesk-cb` («quantdesk raiz relevo 57»), que ya tiene el aviso de la fila 2. Los mensajes a `quantdesk` van ahora allí.
- **Raíz del backend cambiada:** `quantdesk-backend-24` pasó la raíz a `quantdesk-backend-1a` y le reenvió la orden de la tarea de Windows de TI-02-DIARIO (`a47ccf4`). La nueva raíz dirá la hora de la primera ejecución; los mensajes al backend van ahora allí.
- **Decisión del usuario** (2026-11-14, AskUserQuestion en esta sesión) sobre PLAN_RSC_BRAIN: integrarlo en el
  **sprint activo del backend (SPRINT-02)**, ejecutado por el backend como dueño. Nuestro SPRINT-03 no cambia.
  - GAP-1: BD `rsc_brain` en `qn-pgprod`.
  - GAP-2: **pública con OAuth** (subdominio de `stoch.cloud`), no la opción «sólo LAN» que recomendaba la raíz.
  - GAP-3: sin embeddings al principio.
  - GAP-4 (curador) y GAP-5 (memorias actuales) siguen abiertas; las pregunta el backend antes de su fase 4.
  - Comunicado a `quantdesk-backend-1a`; pendiente su commit.
- **rsc-brain en el SPRINT-02 del backend** (`quantdesk-backend-1a`, commit `c372ae8` de su repo, empujado):
  - entra como raíl R, con las fases RSC-F0 a RSC-F6;
  - plan §6 y GOBERNANZA con las GAP 1-3 «decidido (usuario, 2026-11-14)»; la 4 y la 5 se preguntan antes de RSC-F4;
  - RSC-F3 (exposición pública) no se abre hasta que se acepte la auditoría de autenticación de RSC-F0.
- **TI-02-DIARIO:** el backend registrará la tarea de Windows en su PUB-05-EXPORT (SPRINT-03), con permiso del usuario.
  Avisará de la hora de la primera ejecución.
- **Token del exportador instalado** (aviso de `quantdesk-cb`, a petición del usuario, 08:26): `E:/quantdesk-lab/secrets/ti02-diario.env` con una sola línea `QN_TOKEN=…`, comprobada por la raíz sin leer el valor (46 caracteres). La copia de mini se borró tras comprobar el hash. Faltan la tarea de Windows del backend y la primera ejecución (`sin_mt5` mientras MT5 siga bloqueado).
- **Revisión de alertas SUSPENDIDA** (cambio de la skill, usuario 2026-11-14, para ahorrar cuota; aviso de `quantdesk-cb`;
  SKILL.md:187 y `references/alertas.md`:3) hasta el reinicio semanal de Claude del **2026-11-17 a las 00:59**. La
  revisión lanzada a las 08:50 (encargo `alertas/encargo-20261114-0850.md`) se paró con `arbol.py --kill` a los ~2 min,
  sin informe. `ultima.json` sigue con la de las 00:45. Se reanuda después del 17-11 00:59, incluido el paso 5b del
  Arranque de los relevos.
- **MT5 desbloqueado.** Anuncio del usuario para todas las raíces (2026-11-14, retransmitido por `quantdesk-cb`): «acabo de
  desbloquear la cuenta de Metatrader 5, todos los desarrollos pueden seguir».
  - Comprobación de la raíz a las 09:1x, sólo lectura y sin pedir historia: el terminal está abierto por el usuario desde
    las 09:02 (`D:\ICMarkets - MetaTrader 5`) y `terminal_info.connected=True` (ping 80 ms). La cuenta real responde, con
    `trade_allowed` del terminal en False.
  - La tarea `\quantdesk\publicador_mt5` sigue Disabled.
  - Puertas de usuario pendientes (LAUNCH §3): reactivar la tarea (4c), aprobar el ritmo (4a), cada noche (4c y 5) y la
    revisión del token id 36.
  - Cuota a las 09:1x: Claude 92 % (reinicio el 2026-11-17 00:00 UTC), Codex 84 % (reinicio el 2026-11-18 08:07 UTC).
- **Decisiones del usuario** (2026-11-14, AskUserQuestion en esta sesión):
  1. **reactivar hoy el publicador** `quantdesk\publicador_mt5` (fila 4c, primera parte), con una primera pasada
     vigilada a ritmo prudente;
  2. **descargas grandes (4b incremental m1/m5 y 4a h1) tras el reinicio de Codex del 2026-11-18**: antes, Codex
     añade la pausa entre series al extractor, con revisión;
  3. **token id 36: se mantiene**; revisado por el usuario el 2026-11-14, la próxima revisión será al cerrar SPRINT-03.
- **Contraseña de MT5 cambiada** (anuncio del usuario vía `quantdesk-cb`). El usuario la actualizó: «lo he
  actualizado». Ficheros de credenciales MT5 del proyecto: `E:/quantdesk-lab/secrets/mt5.json` (claves path, login,
  password y server; los usan el extractor y el publicador, `scripts/extractor_mt5_lib/lectura.py:126`).
- **Regla nueva de la skill** (SKILL.md §0, «MetaTrader 5: un solo usuario a la vez», aviso de `quantdesk-cb`):
  - turno exclusivo con `~/.claude/mt5/turno.lock`;
  - peticiones en serie con pausas, y parada al primer error de autenticación o de límite;
  - una línea por turno en `~/.claude/mt5/uso.jsonl`.
  Se aplica ya a toda conexión y a los encargos.
- **Prueba de login con turno** (09:3x): `initialize(path)` + `login` con `mt5.json`, OK; sin pedir historia; anotada en
  `uso.jsonl`, junto con la consulta de estado de las 09:1x, que fue anterior a la regla.
- **Primera pasada del publicador** lanzada con turno (ejecutor de la raíz que toma el candado, ejecuta y anota el
  turno; `s03/TI-12-MT5-OPS/pub-pasada1`):
  `publicador_mt5.py --ejecutar --topic market.ohlcv.v2 --intervalos 1d --republicar-revisiones --pausa-serie-s 15`.
  Rellena desde la última vela en qn (parado desde el 2026-11-10) y republica las velas revisadas del 2026-11-09.
- **Pendiente antes de reactivar la tarea programada:** el publicador no toma el turno de MT5, así que la tarea diaria
  necesita un envoltorio versionado que lo tome. Hay que tenerlo antes del lunes 16-11 a las 23:30, la primera vela
  nueva tras el fin de semana.
- **Proyecto nuevo `quantlab`** (anuncio del usuario vía `quantdesk-cb`, 2026-11-14): `S:/Projects/quantlab` será el centro de datos central. Atenderá las peticiones de datos de todos los proyectos, descargará el histórico (primero MT5) y lo dejará disponible para todos; acabará siendo el único que hable con MT5. Su raíz inicial nos escribirá para coordinar `E:/quantdesk-lab`, el exportador, el lago qn, DEPENDENCIAS y GOBERNANZA. Mientras tanto sigue la norma de turnos de MT5. Afecta a las filas 4a–4c y 5 (extractor y publicador MT5): se revisan con quantlab antes de encargar código nuevo de MT5.
- **Primera pasada del publicador** (09:26–09:34; exit 0; turno liberado y anotado en `uso.jsonl`):
  - 5 de 28 pares publicaron 3 velas nuevas, las del 10, 11 y 12-11: AUDJPY, EURUSD, GBPUSD, USDCAD y USDCHF.
  - Los otros 23 dieron 0 nuevas porque el terminal sólo tenía historia hasta el 09-11 (`mt5_hasta_utc`).
  - En todos los pares queda 1 vela retenida por la guarda de historia (`retenidas_sin_historia`).
  - Diagnóstico: el terminal recién autenticado aún no ha sincronizado la historia de los pares fuera de su lista de
    seguimiento. No se fuerza con consultas en ráfaga (causa del bloqueo).
  - Segunda pasada programada en esta sesión a las 13:07 (cron de un solo disparo), con el mismo turno y la misma
    pausa. Detalle de la pasada 1: `E:/quantdesk-lab/runs/TI-12-MT5/publicador/ultimo.json`.
- **`quantlab-f0` (raíz de quantlab)** propone centralizar MT5: heredar el extractor y después el publicador, con almacén propio en nuestro formato y entradas en DEPENDENCIAS y GOBERNANZA. Respuesta técnica de la raíz: de acuerdo con la herencia y con que use su propio almacén (nosotros sólo leemos). Le corregimos que el publicador ya es diario y está desactivado. Peticiones reales: filas 4a–4c y 5. Las filas de DEPENDENCIAS y GOBERNANZA llegarán cuando el usuario decida la entrega. **Pendiente del usuario:** el traspaso de propiedad del extractor y del publicador, y dónde se entregan los datos.
- **Decisiones del usuario sobre quantlab** (2026-11-14, retransmitidas por `quantlab-f0`; plan
  `S:/Projects/quantlab/docs/plans/next/PLAN_SERVICIO_DATOS.md`, `871b112`):
  - quantlab es el **único** que descarga histórico de MT5; el trading en vivo queda fuera.
  - Entrega en su almacén `E:/quantlab`, con nuestro formato y parquet zstd; peticiones JSON en
    `E:/quantlab/peticiones/entrada/`.
  - Se recicla todo lo ya descargado: quantlab sólo lee nuestro `E:/quantdesk-lab`.
  - Reparto de nuestras filas: la 4a (h1 de `@continuo`) pasa a su SPRINT-01 (QL-10), tras el 18-11. La 4b, la 4c
    (traspaso del publicador) y la 5 pasan a su SPRINT-02, con la retirada de nuestro código de descarga MT5.
  - Hasta el traspaso, nuestro publicador sigue tal cual, con `turno.lock`.
  - Skill: viñeta «quantlab, único para histórico» en SKILL.md:198, que se aplica en la próxima planificación.
  - Filas versionadas en DEPENDENCIAS (proyecto relacionado y dependencia de las filas 4a–4c y 5) y en GOBERNANZA (tres
    filas).
  - **Consecuencia para SPRINT-03:** las filas 4a, 4b y 5 ya no las ejecuta este laboratorio. Se replanifican al cerrar o
    revisar el sprint. La 4c sigue aquí sólo en su parte operativa: publicador diario con turno hasta el traspaso.
- **Aviso de cambio en la skill** (`quantlab-f0` por encargo del usuario, 2026-11-14; `niveles-y-modelos.md` §0 y SKILL.md): Claude 93 % (reinicio el 17-11 01:00), Codex 91 % (reinicio el 18-11 09:07). (1) Codex tiene dos cuentas: se sigue encargando a Codex y, cuando la cuenta activa llegue al 98 %, se avisa al usuario, que cambia a la segunda; no se pasa trabajo a Claude por eso. (2) Lo que deba ir a Claude (L9–L10, arenas o escalada con motivo) usa antes Fable 5.2 (`claude-fable-5-2`), con barra semanal propia; las raíces siguen en Opus. Se aplica desde el próximo encargo.

### Relevo 2 (2026-11-14, `quantdesk-model-c1`)

- **Aceptación** 11:26 (`3aa50a0`): sesión af8558d2, contexto inicial 17,3 %; `relevos.json` → `quantdesk-model-c1`.
  `deps.py --sprint SPRINT-03`: LISTO. Vigía `wsvigia.py` vivo (PID 28040, puerto 8775) y Monitor re-armado. Alertas:
  suspendidas hasta el 17-11 00:59 (SKILL.md). Cuota 11:28: Claude 94 % (reinicio 16-11 23:59), Fable 0 %, Codex 92 %
  (reinicio 18-11 08:07; aviso al usuario al 98 %).
- **TI-12-MT5-OPS, envoltorio del turno:** revisión previa de `ficha-turno.md` con `gpt-6-luna` high, sólo lectura
  (intento BDD 333; `s03/TI-12-MT5-OPS/revficha-turno`).
- **Decisión del usuario retransmitida por `quantdesk-6c`** (2026-11-14 ~11:30, literal): «El tema del secret y el .env
  ya lo he arreglado se supone, y los tokens tienes libertad para generar los que necesites. Network puede usar mini o lo
  que necesite». Para este laboratorio: los tokens que necesite (el 43 de TI-02-DIARIO u otros) los podemos generar
  nosotros, coordinando con backend y network; ningún valor en chats ni logs. `quantdesk-6c` avisa además de que el
  HANDOFF de la 01:14 daba MT5 por bloqueado: ya está corregido desde el relevo 2 (MT5 desbloqueado hoy, histórico vía
  quantlab, uso por turnos según SKILL.md §0).
- **TI-12-MT5-OPS, envoltorio del turno: ACEPTADO** (`494d97a`, base `8d790e3`).
  - Ficha v2 tras la revisión previa de `gpt-6-luna` (CAMBIAR, 8 cambios incorporados: formato real de
    `ultimo.json`, `token` en el candado y liberación por token, huérfano propio de `tarea-programada` retirable,
    candado corrupto = ocupado, UTC con `Z`, saneado de secretos en `orden`/`errores`, registro a stderr si falla
    `uso.jsonl`, hija con `CREATE_NO_WINDOW`; hija también con `pythonw.exe`).
  - Autor `gpt-6.1-sol` high (intento 335): `scripts/mt5_turno.py` (767 líneas, 24 tests con tabla «caso borde → test»
    completa) y `scripts/publicador_mt5_tarea.xml` (sólo cambia `Arguments`).
  - Revisor `gpt-6-luna` high (intento 338): ACEPTAR, sin hallazgos; reprodujo la cadena `pythonw → envoltorio →
    pythonw` (código 37 propagado, candado liberado; PID del lanzador del `.venv` ≠ PID de Python del candado). A5:
    sólo el XML, sólo `<Arguments>`.
  - Gate de la raíz sobre HEAD fijo `494d97a`, `scripts` limpio antes y después: `mt5_turno.py --selftest` 24 OK;
    `run_selftests.py` 16 OK, 0 fallos (`E:/quantdesk-lab/runs/TI-12-MT5/gate-raiz-turno/`).
  - **Tarea reactivada** (decisión del usuario «reactivar hoy el publicador», arriba): `run_scheduler.cmd` →
    `ACTUALIZADA quantdesk\publicador_mt5`; estado **Ready**, próxima ejecución 2026-11-14 23:30, ya con turno.
    Compromiso con el backend (antes del lunes 16-11 23:30) cumplido. Ojo: `LastTaskResult` = 2 de la ejecución que
    el Programador anota el 13-11 23:30; se mira tras la de hoy.
- **quantlab** (`quantlab-f0`, 2026-11-14): anota nuestra pasada de las 13:07 y la tarea de las 23:30. Su primera
  conexión real (QL-09a, ~144 peticiones y ≥ 15 min de pausas) aún no tiene hora, porque faltan credenciales del usuario.
  No coincidirá con esas franjas, usa el mismo `turno.lock` con O_EXCL y mantiene el descriptor abierto todo el turno.
  Avisará antes de lanzarla. Límite conocido de `mt5_turno.py`: si un candado ajeno se abre negando la lectura,
  `leer_candado` (`scripts/mt5_turno.py:179`) lanza `PermissionError` y el envoltorio sale con error en vez de esperar.
  Se ha pedido a quantlab que lo abra con compartición de lectura (lo normal en Python). Si no, issue para el envoltorio.
- **Backend** (`quantdesk-backend-22`, relevo 8, 2026-11-14): confirma que el publicador está reactivado. La tarea de
  Windows de TI-02-DIARIO va en su PUB-05-EXPORT (su SPRINT-03, aún sin empezar; su SPRINT-02 sigue activo, con la
  ventana de Mongo hasta el 18-11). Avisará de la hora de la primera ejecución cuando la registre, con permiso del
  usuario. Decisión del usuario retransmitida (vía quantlab): las fuentes que no son de MT5 (PUB-*) se quedan en el
  backend. Para nosotros, el despliegue de TI-02-DIARIO sigue esperando ese aviso; nada que hacer.
- **Aviso de cambio en la skill** (`quantlab-f0` por encargo del usuario, 2026-11-14; `niveles-y-modelos.md` §0,
  «Actualización … quedan 2 más»): el usuario gastó uno de sus reinicios de Codex y le quedan 2. Codex está al 0 %, con
  el próximo reinicio el 21-11 a las 11:38 UTC. Se sigue priorizando Codex para autores y revisores. La regla del 98 % no
  cambia: avisar al usuario, que decide cuándo reinicia o cambia de cuenta. Se aplica desde el próximo encargo; no hay
  que relanzar nada.
- **Segunda pasada del publicador** (13:07–13:16 CET, exit 0, sin errores; primera ejecución real de
  `scripts/mt5_turno.py`, sesión `quantdesk-model-c1`; turno tomado, liberado y con una línea en `uso.jsonl` con las
  28 series; `s03/TI-12-MT5-OPS/pub-pasada2`). La orden es la de la pasada 1, con `--republicar-revisiones` y
  `--pausa-serie-s 15`.
  - Los 23 pares que en la pasada 1 sólo tenían historia hasta el 09-11 la tienen ya hasta el 12-11: publicaron 3 velas
    cada uno (10, 11 y 12-11), **69 nuevas y 69 publicadas**. Los 5 de la pasada 1 (AUDJPY, EURUSD, GBPUSD, USDCAD,
    USDCHF) dieron 0 nuevas, como se esperaba.
  - Los 28 retienen 1 vela (`retenidas_sin_historia`), la del viernes 13-11. La guarda la retiene hasta que el terminal
    tenga historia posterior; con el mercado cerrado el fin de semana, se publicará en la ejecución diaria del lunes
    16-11 a las 23:30. `revisiones_a_republicar` = 0 en todas.
  - Copia de la pasada 1: `s03/TI-12-MT5-OPS/ultimo-pasada1.json`; la pasada 2 está en
    `E:/quantdesk-lab/runs/TI-12-MT5/publicador/ultimo.json`.
- **quantlab** (nueva raíz `quantlab-7a`, 2026-11-14 tarde): toma el turno de MT5 para la descarga real de QL-09a (144 peticiones, 15–25 min). Le contestamos que siga: no necesitamos MT5 hasta las 23:30.
- **quantlab** (raíz `quantlab-d0`, 2026-11-14 ~17:10): MT5 vuelve a estar disponible. Según el usuario, el fallo de conexión venía de `D:\dev\deeplearning_dev\config_pro.py` (ya corregido), no de `mt5.json`. quantlab tiene ahora el turno para QL-09a, en serie y con pausas. Las normas no cambian. Para nosotros: la tarea de las 23:30 espera el turno si sigue ocupado (hasta 30 min, y si no, sale con 4).
  Corrección de `quantlab-d0` poco después: ya soltó el turno y no tiene ninguna descarga en marcha. Antes de bajar nada aplicará las medidas de conexión que pidió el usuario (QL-05b) y avisará antes del próximo turno.
- **Aviso de cambio en la skill** (`quantlab-d0` por orden del usuario, 2026-11-14 ~17:40; SKILL.md:171, `handoff.md`, `launch.md` y el valor por defecto de `claude_handoff.py`, comprobados): **toda raíz corre en Fable 5.2 high** (`claude-fable-5-2`), no en Opus 5.5 high. Lo que la norma reservaba a «decide la raíz en Opus» pasa a decidirlo la raíz en Fable. El usuario pide relevar «ahora mismo», en el primer punto tranquilo: LAUNCH §2 actualizado y relevo 3 lanzado en Fable.
- **Relevo 3 aceptado** (2026-11-14 17:24 CET; raíz `quantdesk-model-22`, Fable 5.2 high; `relevos.json` actualizado; commit `787b592`). `deps.py --sprint SPRINT-03`: LISTO, 0 dependencias de entrada. Vigía `wsvigia.py` vivo (PID 28040, puerto 8775) y Monitor re-armado. Revisión de alertas: suspendida hasta el 17-11 00:59 (skill). Sin hijos en vuelo. Programada con `CronCreate` la revisión de la ejecución de las 23:30 del publicador (un disparo, 23:47).
  - **Problema del arnés, pendiente de decisión del usuario:** `handoff accept` midió un contexto inicial del 66.6 % y `handoff status` da 98.5 % de 200 000 tokens tras leer sólo lo que manda el Arranque (HANDOFF, LAUNCH, SPRINT_PROJECT, SKILL.md, `handoff.md`, `launch.md` y tres memorias). Con ese arranque, relevar otra vez no arregla nada: la sucesora nacería igual. No se lanza el relevo 4; se avisa al usuario.
- **Aviso de cambio en la skill** (`quantlab-e6`, 2026-11-14 ~18:15; SKILL.md:207-221, comprobado): «Conexión prudente: cuatro medidas (usuario, 2026-11-14)» para todo código que conecte a MT5: `login` sólo si la cuenta no coincide; `initialize` nunca arranca el terminal (se comprueba antes el `terminal64.exe` de la ruta configurada); nunca se mata ni reinicia el terminal; espera acotada (5 s / 180 s) a conexión y símbolo. Además, quantlab toma el turno para un intento de QL-09a.
  - **Nuestro código no cumple del todo** (`scripts/extractor_mt5_lib/lectura.py::enganchar`, que usan el extractor y el publicador): con el terminal cerrado llama a `initialize(path)` y lo arranca; comprueba cualquier `terminal64.exe` con `tasklist`; reintenta `initialize` y `login` hasta 5 veces ante -6/-10005; espera 60 s / 1 s y no espera al símbolo. Con el terminal abierto en la cuenta del fichero (caso de hoy) el camino sí es prudente.
  - **Arreglo lanzado** dentro de TI-12-MT5-OPS: ficha `s03/TI-12-MT5-OPS/ficha-conexion.md` (L4), autor `gpt-6.1-sol` high (`autor-c1`, lanza PID 15372, intento 384 de la BDD), base `d86e178`; revisor previsto `gpt-6-astra` high. Punto de control a las 23:12 (cron de la sesión): si no está aceptado y el terminal no está abierto, se desactiva la tarea sólo esta noche (no hay vela nueva hasta el lunes) y se avisa al usuario.
- **Contexto de las raíces en Fable** (`quantlab-e6`, comprobado): `modelSettings` de `~/.claude/settings.json` no tiene `autoCompactWindow` para `claude-fable-5-2` y `tools/claude_context.py:17` cae en 200 000; el aviso de «zona urgente» es un artefacto. No se releva por él; pendiente de que el usuario fije el valor.
