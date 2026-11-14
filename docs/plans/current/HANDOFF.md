# HANDOFF de la raíz — relevo 1

## Relevo
- Número: 1
- Sale: sesión 2ed6ea1b-5994-4369-a983-cbc5d4646f9d (`quantdesk-model-4d`, antes raíz de guardia), claude-opus-5-5,
  contexto 70.7 %
- Escrito: 2026-11-14T01:14:40+01:00
- HEAD al escribir: 1aa21801c946323a578267c11a05c34185b2fbf7
- LAUNCH: docs/plans/current/LAUNCH.md · bloque del coordinador: «§8. Prompt de la raíz (relevos y recuperación)»
- Relevos anteriores: `git log --follow -- docs/plans/current/HANDOFF.md`
- Aceptado: sesión 2ab53d59-60b1-4f92-84cf-bf4a7115386f, 2026-11-14T01:16:15+01:00, contexto inicial 21.9 %

## Arranque
1. `S:/Projects/quantdesk-model/.venv/Scripts/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/tools/claude_or.py handoff accept docs/plans/current/HANDOFF.md`: valida este archivo y anota tu sesión.
2. Lee sólo esto: este archivo, el bloque del coordinador del LAUNCH, `docs/plans/SPRINT_PROJECT.md` (y las
   políticas que liste), la skill global `sprint` (`C:/Users/makiolo/.claude/skills/sprint/SKILL.md`, `references/launch.md`,
   `references/handoff.md`) y las fichas de los hijos en vuelo. El resto, cuando haga falta y delegando.
3. `git status`, el estado del gate o candados de SPRINT_PROJECT «Comandos» y `git log --oneline 1aa21801c946..HEAD`.
4. Adopta los hijos en vuelo: comprueba su proceso y su salida y vigílala; no relances un ID vivo.
5. Lanza el vigía de caché con `run_in_background` desde la raíz del repo:
   `S:/Projects/quantdesk-model/.venv/Scripts/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/scripts/cache_heartbeat.py` (`references/handoff.md`, «Latido de caché»).
6. Busca en la memoria del proyecto (SPRINT_PROJECT «Identidad») las palabras clave del siguiente paso.
7. Commit del HANDOFF con la aceptación y continúa con «Siguiente paso».

**Shell:** usa la herramienta PowerShell. Bash, sólo para órdenes triviales: el envoltorio ejecutó con `eval` backticks
y `!` dos veces en este tramo (memoria `bash-trampas-commit`). Mensajes de commit: Write a un fichero y `git commit -F`.

## Estado
- **SPRINT-03 activo desde el 2026-11-14** (`4535ef6`); SPRINT-04 promovido a `next/`. La guardia `quantdesk-model-4d`
  pasó a raíz inicial. Detalle de todo el tramo en `current/EXECUTION.md`.
- **Fila 1 (TI-02-DIARIO, contrato, L3): CERRADA** (`1e50e5e`).
  - Contrato decidido por el usuario: `current/execution/TI-02-DIARIO/contrato-propuesta.md`.
  - El borrador y las respuestas de las tres raíces están en `borrador-contrato-a1.md`.
  - Escrito en GOBERNANZA, DEPENDENCIAS, PLAN_DATOS_VIA_QN §4 y SPRINT.md §2/§4.
- **Fila 2 (TI-02-DIARIO, código sin OAS, L6): sin encargar.** Espera la respuesta de `quantdesk-f1` sobre
  `FX_DATE_SHIFT` (ver «Siguiente paso»). En la BDD, `TI-02-DIARIO` está `en_curso`; el intento 283 (borrador) cerró
  `aceptada`.
- **Filas 3, 4a–4c, 5, 6 y 7:** esperan su puerta:
  - fila 3: fecha ≥ 2026-12-11;
  - filas 4a–4c y 5: desbloqueo de la cuenta MT5; el usuario estudia pagar por datos;
  - filas 6 y 7: PUB-02 del backend.
- **Alertas:** primera revisión a las 00:42 (`.git/sprint-runtime/alertas/ultima.json`): sin incidencias. Toca otra
  pasadas las 08:45. URL y filtro en SPRINT_PROJECT §12.
- **Cuota** (01:1x): Claude 80 % (reinicio 2026-11-16 23:59 UTC); Codex 62 % (reinicio 2026-11-18 08:07 UTC). Orden
  temporal: Codex implementa y revisa hasta el 2026-11-17 00:59.

## En vuelo
Ninguno. Los dos Codex del tramo (alertas y borrador del contrato) terminaron con exit 0.

## Decisiones
- Usuario, 2026-11-14: «vale» a planificar e iniciar SPRINT-03 empezando por la fila 1 (EXECUTION, SPRINT.md cabecera).
- Usuario, 2026-11-14 (AskUserQuestion): contrato de TI-02-DIARIO (EXECUTION; GOBERNANZA; DEPENDENCIAS;
  PLAN_DATOS_VIA_QN §4):
  - A2, tarea de Windows registrada por el backend;
  - sólo OHLCV en `desktop.daily-ohlcv/v1` y `engine.market-history/v1`; los JSON siguen con los notebooks de `quantdesk`;
  - topic `ops.export.status` y token `sub:market.ohlcv.v2` + `pub:ops.export.status`;
  - el resto tal cual.
- Raíz: fuente del FX como parámetro de la política de fuentes (hoy `mt5`), porque el usuario estudia pagar por datos
  (nota en el contrato).
- Raíz: SPRINT_PROJECT §12 «Alertas» versionado con la URL y el filtro de la primera revisión.
- Norma nueva de la skill (usuario vía `quantdesk-f1`): al planificar entra todo lo pendiente; se aplica a SPRINT-04
  (EXECUTION).

## Preguntas abiertas al usuario
Ninguna. Network registrará el topic y emitirá el token pidiendo confirmación al usuario desde su propia sesión.

## Compromisos con otras raíces
- **`quantdesk-f1`:** responderá con ruta:línea la pregunta de `FX_DATE_SHIFT` (`daily.py:97`, se aplica en su notebook
  28): dirección del desplazamiento, si algún lector vuelve a desplazar, acciones y SPX, rango de fechas y si usamos su
  `write_ohlcv`. **Pidió no encargar la fila 2 hasta entonces.** Hay que avisarle al aceptar la fila 2.
- **`quantdesk-backend-24`:** espera la orden exacta de la tarea de Windows (script, argumentos, cwd y venv) cuando la
  fila 2 esté aceptada. Su sensor usa el `ts` del sobre de `ops.export.status` (cuando termina la validación) y sólo
  cuenta `status=ok`.
- **`quantdesk-network-b2`** (la raíz de network desde hoy; `-21` ya no escribe): registrará `ops.export.status` y
  emitirá el token, con la confirmación del usuario, y avisará. Respuestas de despliegue en EXECUTION: el token no va
  atado a host; `QN_URLS=http://192.168.1.48:8790/qn,http://192.168.1.46:8790/qn,http://192.168.1.45:8790/qn`; sin TLS
  en la LAN.
- Nosotros avisamos al backend cuando MT5 vuelva a publicar.

## Conocimiento promovido
Memoria `bash-trampas-commit` ampliada: PowerShell para órdenes no triviales y nada que cambie el árbol en las órdenes
de verificación. Lo demás está versionado (contrato y EXECUTION); no hay grafo de conocimiento en este proyecto.

## Siguiente paso
Cuando llegue la respuesta de `quantdesk-f1` sobre `FX_DATE_SHIFT`, escribir la ficha de la fila 2 en
`.git/sprint-runtime/s03/TI-02-DIARIO-codigo/ficha.md` (plantilla `references/ficha.md`, L6, riesgo numérico-silencioso).
Contrastar con la fuente cada hora, zona y regla que ponga. La ficha recoge:
- el contrato aprobado;
- el `ts_ms` del FX de MT5 según la respuesta de `quantdesk`;
- el uso de `quantdesk.daily.write_ohlcv` de la rueda, si lo aceptan, con `sources` explícitas;
- `volume_kind=tick_count`;
- el docstring de `descarga_lago.py` corregido (ni «`market.>`» ni «el host donde se emite»);
- paso a la siguiente URL de `QN_URLS`;
- H (`x-qn-head-cycle`) en el manifiesto y el filtro `_cycle <= H`, sin `fresh=true`;
- publicación del objeto de estado con `batch_id` determinista, job `ti02-diario`;
- `sin_mt5` sin publicar nada;
- un oráculo contra `quantdesk.daily` y un test diferencial frente a `Base`.

Después: revisión de la ficha por un modelo barato de sólo lectura, autor Codex `gpt-6.1-sol` xhigh y revisor
`gpt-6-astra` high (LAUNCH §2), lanzados con `lanza.py`/`hijo.py`. Mientras no llegue la respuesta, no se encarga nada.
