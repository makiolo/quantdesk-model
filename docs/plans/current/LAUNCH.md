# LAUNCH — SPRINT-03 de quantdesk-model

Preparado el 2026-11-14 al activar el sprint. No hace falta abrir ninguna sesión: la raíz de guardia
`quantdesk-model-4d` pasa a ser la raíz inicial (skill `sprint`, `guardia.md` «Paso a sprint»). El prompt de §8 sirve
para relevos y recuperaciones. Fuentes: [SPRINT.md](SPRINT.md), [SPRINT_PROJECT](../SPRINT_PROJECT.md),
[GOBERNANZA](../GOBERNANZA.md), [DEPENDENCIAS](../DEPENDENCIAS.md) y la skill global `sprint` (`execute-plan`,
`references/delegation.md`, `niveles-y-modelos.md`, `ficha.md`, `handoff.md`, `entre-raices.md`, `alertas.md`).

## 1. Guardia de activación

- `deps.py --repo . --sprint SPRINT-03` (2026-11-14 00:39 CET): **LISTO**, 0 dependencias de entrada. La raíz lo
  recomprueba en cada relevo; si cambia, para.
- Dependencias de tarea (SPRINT.md §4, no bloquean la activación): fila 1 ← respuesta del backend y de `quantdesk`;
  fila 2 ← fila 1; fila 3 ← fecha ≥ 2026-12-11; filas 4a–4c y 5 ← desbloqueo de la cuenta MT5 (y visto bueno de
  network para 4c/5); filas 6 y 7 ← PUB-00…PUB-02 del backend.

## 2. Raíz, ejecutores y cupo

**Orden temporal del usuario** (2026-11-14 00:20, `niveles-y-modelos.md` §0, hasta el 2026-11-17 00:59 CET): Codex
implementa y revisa todo; Claude sólo para la raíz, L9–L10 y sus arenas. Al caducar, vuelve la tabla de §1 de esa
referencia con la decisión del usuario del 2026-11-10 (SPRINT_PROJECT §6: Haiku 5.5 fuera; revisión obligatoria en
L3–L4 hasta el 2026-11-24, con tabla «caso borde → test»).

| Rol | Proveedor / modelo | Esfuerzo | Notas |
|---|---|---|---|
| Raíz (coordina, negocia por mensaje, revisa, decide nivel) | Claude Fable 5.2 (`claude-fable-5-2`), suscripción (usuario, 2026-11-14 ~17:40; antes Opus 5.5) | high | Se releva a sí misma por contexto (§6) |
| Borrador del contrato, fila 1 (L3) | `gpt-6.1-sol` high, sólo lectura | high | Revisan el backend y `quantdesk` por mensaje; aprueba el usuario |
| Autor L6 (fila 2; 4a cuando se abra) | `gpt-6.1-sol` xhigh | xhigh | |
| Revisor L6 | `gpt-6-astra` high | high | Recibe ficha + diff, nunca el informe del autor |
| Autores L4–L5 (filas 3, 4b, 5, 6, 7) | `gpt-6.1-sol` high | high | Tras el 2026-11-17, según la tabla y la cuota |
| Revisores L4–L5 | `gpt-6-astra` high (hasta el 2026-11-17); después, la tabla | high | |
| Autor y revisor L3 (fila 4c) | `gpt-6.1-sol` high / `gpt-6-astra` high | high | Revisión obligatoria hasta el 2026-11-24 |
| Revisión de alertas cada 8 h | `gpt-6.1-sol` high (`alertas.md`) | high | Cuenta en el cupo |

- **IA local** según la escalera A17 global, con ficha completa y revisión en la nube; `claude-local` reserva ranura
  de GPU. **Sin API de pago**: sin ruta → `BLOQUEADO_PRESUPUESTO` y parar.
- Cupo: raíz + **3** descendientes activos, contando revisores, nietos, autores locales y la revisión de alertas.
- Esquema de dificultad: `difficulty-v3-10`; niveles en SPRINT.md §3.
- **BDD de sprints** (`references/sprint-db.md`): cada intento con `sprint_db.py attempt start/end` y cada cambio de
  estado con `sprint_db.py task`; tras cerrar una tarea, `sprint_db.py update`.
- **Lanzamiento sin bash** (norma del 2026-11-13): hijos con `tools/lanza/lanza.py` + `tools/lanza/hijo.py`, órdenes
  largas con `lanza.py`; vigía `tools/vigia/wsvigia.py` en un puerto propio (no el 8765 de `quantdesk`), seguido con
  Monitor por WebSocket. Se anota el PID de cada lanzamiento para `arbol.py --kill`.

## 3. Cola y olas (orden de SPRINT.md §6, sin solver)

| Ola | Tareas | Condición |
|---|---|---|
| 1 | **Fila 1** (contrato de TI-02-DIARIO, por mensaje) | Al activar |
| 2 | **Fila 2** (código de TI-02-DIARIO, sin OAS) | Contrato aprobado por el usuario; antes de la ola 1 de quantdesk SPRINT-03 |
| MT5 | 4b incremental m1/m5 → 4a h1 de `@continuo` → 4b acciones → 4c publicador y noche de `@continuo` → 5 (condicionada) | Desbloqueo de la cuenta; mutex del terminal; una serie cada vez |
| 3 | **Fila 3** (S02-6 y cierre de la sonda) | Desde el 2026-12-11, en una sola sesión de token |
| 4 | **Filas 6 y 7** (FRED/OAS) | Aviso del backend de que publica |

**Puertas de usuario** (la raíz pregunta, con aviso al móvil antes, y no las salta):
1. **Fila 1:** aprobar el contrato y la credencial del job.
2. **Fila 2:** credencial `sub:` del job, si el contrato la pide.
3. **Filas 4a–4c y 5:** el desbloqueo de la cuenta lo gestiona el usuario; el terminal lo abre y autentica él; aprobar
   el ritmo (4a), reactivar la tarea programada (4c), aprobar cada noche (4c y 5) y revisar el token id 36.
4. **Fila 3 y lecturas de qn:** el `QN_TOKEN` lo emite y revoca el usuario; nunca por el chat.
5. Si la cuenta MT5 sigue bloqueada al acercarse el 2027-01-17 (fecha límite de 4b), avisar al usuario.

## 4. Reglas que la raíz copia en cada ficha

- **Gobernanza:** no se escribe en nada de `quantdesk`, backend ni network; se coordina por mensaje. Sólo las
  decisiones del usuario en `PLAN_TSFM_*` (GAP-01).
- **Disco:** todo dato, caché, descarga y artefacto va a `E:/quantdesk-lab/`. Nada de `du` sobre árboles grandes;
  `df -h`. Búsquedas con ripgrep.
- **Credenciales:** ninguna en repo, informes, prompts ni chat (secretos MT5 en `E:/quantdesk-lab/secrets`); patrón
  `qn_` = 0.
- **MT5:** el extractor sólo lee; descargas prudentes (una serie cada vez, pausas; el bróker ya bloqueó la cuenta).
- **Fichas:** plantilla `ficha.md`, en `.git/sprint-runtime/s03/<ID>/ficha.md`, escritas con Write o script, nunca
  heredoc. L3–L4: casos borde concretos y tabla «caso borde → test» en el informe del autor. Commit por tarea sólo de
  las rutas autorizadas; el hijo no empuja. La raíz commitea y empuja en cada checkpoint.
- **Evidencia:** cada dataset e informe con SHA-256, semilla, fecha de corte y versión del motor (DoD de SPRINT-01 §8).

## 5. Cuota y costes

- Antes de cada ola: `python -X utf8 "$HOME/.claude/skills/sprint/tools/claude_or.py" quota --weekly`, anotado en
  EXECUTION.md. Si Codex se acerca a su reserva antes de su reinicio, avisar al usuario antes de pasar trabajo a Claude.
- Lectura inicial: SPRINT.md §8. Medición según [USAGE_PROTOCOL](../USAGE_PROTOCOL.md); coordinador de costes: la
  raíz. Tabla con `sprint_costs.py`.

## 6. Relevo

`run_claude_handoff_launch.cmd` / `run_claude_handoff_recover.cmd` (motor de la skill global). HANDOFF en
`docs/plans/current/HANDOFF.md`; arranque en `docs/plans/arnes/ARRANQUE.md`. La sucesora usa el mismo modelo, esfuerzo
y modo de permisos de la raíz. El hook de zonas avisa al 70 % y al 80 %. Al aceptar el relevo, la sucesora comprueba
la revisión de alertas (`.git/sprint-runtime/alertas/ultima.json`, más de 8 h → se lanza).

## 7. Cómo arrancar (usuario)

No hace falta: la raíz ya está viva. Para una recuperación, `run_claude_handoff_recover.cmd` desde el repo.

## 8. Prompt de la raíz (relevos y recuperación)

```text
Eres la raíz del SPRINT-03 de quantdesk-model (docs/plans/current/SPRINT.md). Lee, por este orden,
docs/plans/SPRINT_PROJECT.md, docs/plans/GOBERNANZA.md, docs/plans/current/SPRINT.md,
docs/plans/current/LAUNCH.md, docs/plans/current/EXECUTION.md y, si existe, docs/plans/current/HANDOFF.md,
y usa la skill global execute-plan con la skill sprint (delegation.md, niveles-y-modelos.md, ficha.md,
handoff.md, entre-raices.md, alertas.md).

Al arrancar: ejecuta `python -X utf8 "$HOME/.claude/skills/sprint/scripts/deps.py" --repo . --sprint SPRINT-03`
(debe salir LISTO), lee la cuota semanal (LAUNCH §5) y comprueba la revisión de alertas; anótalo en EXECUTION.md.
Preséntate a las raíces vivas de los otros proyectos (ListAgents) si hay compromisos abiertos.

Ejecuta las olas de LAUNCH §3 en orden, con cupo raíz + 3 descendientes, autor y revisor distintos según
LAUNCH §2 (orden temporal de Codex hasta el 2026-11-17 00:59), fichas según LAUNCH §4 y aceptación verificada
por ti sobre un HEAD fijo. Para en cada puerta de usuario de LAUNCH §3 y pregúntame, con aviso al móvil antes.
No escribas en quantdesk, backend ni network. Registra cada cierre en EXECUTION.md, STATUS.md y la BDD de
sprints con commit, pruebas y hashes. Relévate con handoff según LAUNCH §6.
```
