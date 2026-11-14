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
- **Propuesta conjunta consolidada:** [contrato-propuesta.md](execution/TI-02-DIARIO/contrato-propuesta.md). Pendiente de
  la aprobación del usuario.
- **Norma nueva de la skill** (usuario, 2026-11-14, retransmitida por `quantdesk-f1`): al preparar un sprint entra todo
  lo pendiente (backlog, issues abiertos y arrastres) y la revisión de planes revisa también los issues. Si las
  dependencias o la capacidad no lo permiten, se ofrece partir el sprint explicando tarea por tarea. SPRINT-03 ya lo
  cumplía (R0); se aplica al planificar SPRINT-04.
