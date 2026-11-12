# LAUNCH — SPRINT-02 de quantdesk-model

Preparado el 2026-11-11 al activar el sprint. Escribirlo no lanza nada: el usuario abre **una** sesión de Claude Code
(la raíz) y pega el prompt de §8. Fuentes: [SPRINT.md](SPRINT.md), [SPRINT_PROJECT](../SPRINT_PROJECT.md),
[GOBERNANZA](../GOBERNANZA.md), [DEPENDENCIAS](../DEPENDENCIAS.md) y la skill global `sprint` (`execute-plan`,
`references/delegation.md`, `niveles-y-modelos.md`, `ficha.md`, `handoff.md`).

## 1. Guardia de activación

- `deps.py --repo . --sprint SPRINT-02` (2026-11-11): **LISTO**, 0 dependencias de entrada (el usuario partió el
  sprint ese día; las filas que esperaban a quantdesk SPRINT-02 están en SPRINT-03). La raíz lo recomprueba al
  arrancar y en cada relevo; si cambia, para.
- Dependencias de tarea (SPRINT.md §4, no bloquean): fila 6 ← cadenas en qn y OC-03 del backend; fila 7 ← publicadores
  públicos del backend; fila 2b ← GPU de DL-02-GATES (opcional); fila 1b ← rango 1d de MT5 verificado en qn
  (ISSUE-TI12-MT5-VELA-A-MEDIAS).

## 2. Raíz, ejecutores y cupo

Criterio global de niveles y modelos (`~/.claude/skills/sprint/references/niveles-y-modelos.md` §1), con la decisión
del usuario del 2026-11-10 (SPRINT_PROJECT §6), **anotada en EXECUTION.md como decisión del usuario retransmitida**.

| Rol | Proveedor / modelo | Esfuerzo | Notas |
|---|---|---|---|
| Raíz (coordina, revisa, decide nivel) | Claude Opus 5.5 (`claude-opus-5-5`), suscripción | high | Se releva a sí misma por contexto (§6) |
| Autores L6 (filas 1b, 2b, 5) | `gpt-6.1-sol` xhigh o Sonnet 5.5 high | según tabla | Va el proveedor con más margen (`claude-or route --level 6`) |
| Revisores L6 | Sonnet 5.5 xhigh; si el autor es Claude, `gpt-6-astra` high | high/xhigh | Reciben ficha + diff, nunca el informe del autor |
| Autores L5 (filas 6, 7) | `gpt-6.1-sol` high o Sonnet 5.5 high | high | Haiku 5.5 ni autor ni revisor |
| Revisores L5 | `gpt-5.6-terra` high | high | |

- Orden de suscripciones: la que tenga más margen (Claude 28 %, Codex 0 % el 2026-11-11). **IA local** según la
  escalera A17 global (desde L5, grado `opus`, sólo si la escalera llega), con ficha completa y revisión en la nube;
  `claude-local` reserva ranura de GPU. **Sin API de pago**: sin ruta → `BLOQUEADO_PRESUPUESTO` y parar.
- Cupo: raíz + **3** descendientes activos, contando revisores, nietos y autores locales.
- Esquema de dificultad: `difficulty-v3-10`; niveles en SPRINT.md §3.
- **BDD de sprints** (`references/sprint-db.md`): cada intento con `sprint_db.py attempt start/end` y cada cambio de
  estado con `sprint_db.py task`; tras cerrar una tarea, `sprint_db.py update`.

## 3. Cola y olas (orden de SPRINT.md §6, sin solver)

| Ola | Tareas | Condición |
|---|---|---|
| 1 | **Fila 1b** (TI-02-DATA-V2, después la tabla FX en dos tablas); en paralelo **fila 2b** (FinCast: licencia, venv, pesos) y **fila 5** (TI-12-MT5, más símbolos y periodos) | Mutex del terminal MT5 entre 1b, 5 e INTRA-LOCAL |
| 2 | **Fila 7** (TI-13-PUB, consumir lo publicado) | TI-02-DATA-V2 aceptada |
| 3 | **Fila 6** (TI-09-ARCH, cobertura) | Sólo si hay cadenas en qn; si no, sale con causa |

**Puertas de usuario** (la raíz pregunta dentro de la tarea y no las salta):
1. **Filas 1b y 5:** el terminal MT5 lo abre y autentica el usuario; el extractor sólo lee. Descargas prudentes: una
   serie cada vez, despacio (el bróker bloqueó la cuenta una vez).
2. **Fila 1b:** si la tabla de cabecera cambia la conclusión de TS-00-OBJ, se avisa al usuario antes de tocar umbrales.
3. **Fila 2b:** descarga de los pesos de FinCast (3,97 GB): confirmar con el usuario nombre, origen y tamaño.
4. **Fila 6 y lecturas de qn:** con el `QN_TOKEN` del usuario; nunca por el chat.

## 4. Reglas que la raíz copia en cada ficha

- **Gobernanza:** no se escribe en nada de `quantdesk`, backend ni network. Sólo las decisiones del usuario en
  `PLAN_TSFM_*` (GAP-01). La rueda es la `69fdb39d` de SPRINT-01; subir de motor es de SPRINT-03 (S02-1).
- **Disco:** todo dato, caché, venv auxiliar, descarga y artefacto va a `E:/quantdesk-lab/` (C: y S: casi llenos). No
  usar `du` sobre árboles grandes; `df -h`.
- **Credenciales:** ninguna en repo, informes, prompts ni chat (secretos MT5 en `E:/quantdesk-lab/secrets`).
- **Fichas:** plantilla `ficha.md`, en `.git/sprint-runtime/s02/<ID>/ficha.md`, escritas con Write o script, nunca
  heredoc. Commit por tarea sólo de las rutas autorizadas; el hijo no empuja. La raíz commitea y empuja en cada
  checkpoint importante (skill `delegation.md` §7, usuario 2026-11-12).
- **Evidencia:** cada dataset e informe con SHA-256, semilla, fecha de corte y versión del motor (DoD de SPRINT-01 §8).

## 5. Cuota y costes

- Antes de cada ola: `python -X utf8 "$HOME/.claude/skills/sprint/tools/claude_or.py" quota --weekly`, anotado en
  `EXECUTION.md`. Si no alcanza para la ola, esperar al reinicio; no recortar alcance.
- Lectura inicial (2026-11-11 07:27 UTC): Claude 28 % con el 18,7 % de la ventana (reinicio 2026-11-16 23:59 UTC);
  Codex 0 %, ventana sin empezar.
- Medición según [USAGE_PROTOCOL](../USAGE_PROTOCOL.md); coordinador de costes: la raíz. Tabla con `sprint_costs.py`.

## 6. Relevo

`run_claude_handoff_launch.cmd` / `run_claude_handoff_recover.cmd` (motor de la skill global). HANDOFF en
`docs/plans/current/HANDOFF.md`; arranque en `docs/plans/arnes/ARRANQUE.md`. La sucesora usa el mismo modelo, esfuerzo
y modo de permisos de la raíz. El hook de zonas avisa al 70 % y al 80 %.

## 7. Cómo arrancar (usuario)

1. Abrir una terminal en `S:/Projects/quantdesk-model` y ejecutar `claude --model claude-opus-5-5`.
2. Pegar el prompt de §8. Sólo esa sesión; los demás agentes los lanza la raíz.

## 8. Prompt de la raíz

```text
Eres la raíz del SPRINT-02 de quantdesk-model (docs/plans/current/SPRINT.md). Lee, por este orden,
docs/plans/SPRINT_PROJECT.md, docs/plans/GOBERNANZA.md, docs/plans/current/SPRINT.md,
docs/plans/current/LAUNCH.md y docs/plans/current/EXECUTION.md, y usa la skill global execute-plan con
la skill sprint (delegation.md, niveles-y-modelos.md, ficha.md, handoff.md).

Al arrancar: ejecuta `python -X utf8 "$HOME/.claude/skills/sprint/scripts/deps.py" --repo . --sprint SPRINT-02`
(debe salir LISTO) y lee la cuota semanal (LAUNCH §5); anota ambas en EXECUTION.md.

Ejecuta las olas de LAUNCH §3 en orden, con cupo raíz + 3 descendientes, autor y revisor distintos según
LAUNCH §2, fichas según LAUNCH §4 y aceptación verificada por ti sobre un HEAD fijo (no te fíes del informe
del autor). Para en cada puerta de usuario de LAUNCH §3 y pregúntame. No escribas en quantdesk, backend ni
network. Registra cada cierre en EXECUTION.md, STATUS.md y la BDD de sprints con commit, pruebas y hashes.
Relévate con handoff según LAUNCH §6. Empieza por la fila 1b (TI-02-DATA-V2).
```
