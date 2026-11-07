# LAUNCH — SPRINT-01 de quantdesk-model

Preparado el 2026-11-07 al activar el sprint. Escribirlo no lanza nada: el usuario abre **una** sesión de Claude Code
(la raíz) y pega el prompt de §8. Fuentes: [SPRINT.md](SPRINT.md), [SPRINT_PROJECT](../SPRINT_PROJECT.md),
[GOBERNANZA](../GOBERNANZA.md), [DEPENDENCIAS](../DEPENDENCIAS.md) y la skill global `sprint` (`execute-plan`,
`references/delegation.md`, `ficha.md`, `handoff.md`).

## 1. Guardia de activación

- `deps.py --repo . --sprint SPRINT-01` (2026-11-07): **LISTO**, 0 dependencias de entrada. La raíz lo recomprueba
  al arrancar y en cada relevo; si cambia, para.
- Dependencias de tarea (no bloquean; SPRINT.md §4): TI-09-ARCH ← backend SPRINT-01 OC-01/OC-02 (aviso en origen),
  backend SPRINT-02 OC-03 (captura al cierre), network SPRINT-01 OCS-02 (S3 sin retención). Mientras tanto, el modo
  «mientras tanto» de SPRINT.md §4. Vigilar además la ficha urgente del backend
  `ISSUE-OPTIONS-JOBS-PARADOS` (si el topic está vacío, TI-09-ARCH no tiene datos que leer).

## 2. Raíz, ejecutores y cupo

| Rol | Proveedor / modelo | Esfuerzo | Notas |
|---|---|---|---|
| Raíz (coordina, revisa, decide nivel) | Claude Opus 5.5 (`claude-opus-5-5`), suscripción | high | Se releva a sí misma por contexto (§6) |
| Autores L1–L2 | Claude Haiku 5.5 / Sonnet 5.5 (tabla execute-plan §2.1) o Codex | high | Revisión siempre por otro modelo |
| Autores L3–L4 (niveles del plan L5–L6) | Sonnet 5.5 extra high u Opus 5.5 high; Codex como alternativa de otro proveedor | según tabla | Revisor de otro proveedor si el autor es Claude, y viceversa |
| Revisores | modelo distinto del autor (preferible otro proveedor) | high | Reciben ficha + diff, nunca el informe del autor |

- Orden de suscripciones: Claude (cuota semanal compartida con quantdesk SPRINT-02), después Codex. Sin modelos
  gratuitos ni locales (la política del proyecto no los admite todavía). **Sin API de pago**: sin ruta →
  `BLOQUEADO_PRESUPUESTO` y parar.
- Cupo: raíz + **3** descendientes activos, contando revisores y nietos.
- Esquema de dificultad: L1–L4 por defecto; los niveles L3–L6 del plan se usan como referencia de riesgo.

## 3. Cola y olas (orden de SPRINT.md §7, sin solver)

| Ola | Tareas | Condición |
|---|---|---|
| 1 | **LAB-00-ENV** (barrera) y, en paralelo, la extensión de `scripts/inventario_options_chain.py` a los topics `market.*` (TI-01-INV, sin ejecutarlo) | — |
| 2 | TS-00-PREC; TI-12-MT5; TI-13-PUB; TI-09-ARCH (cuando TI-01-INV tenga cifras) | LAB-00-ENV aceptada |
| 3 | TI-02-DATA (lago primero; añade MT5 y públicas al llegar) → TS-00-BENCH → TS-00-OBJ | primer dataset congelado |

**Puertas de usuario** (la raíz pregunta dentro de la tarea y no las salta):
1. **TI-01-INV:** el usuario ejecuta el inventario con su `QN_URLS`/`QN_TOKEN`; el token nunca pasa por el chat.
2. **TI-12-MT5:** el terminal MT5 lo abre y autentica el usuario; el extractor sólo lee y nunca envía órdenes.
3. **TS-00-OBJ:** los umbrales los acepta el usuario a la vista del banco.
4. **GAP-03:** al empezar LAB-00-ENV, la raíz anota el commit de `quantdesk` (`git -C S:/projects/quantdesk rev-parse
   HEAD`) como fuente de las ruedas; subir de motor después es una decisión del usuario.

## 4. Reglas que la raíz copia en cada ficha

- **Gobernanza:** no se escribe en nada de `quantdesk`, backend ni network (ni `current/`, ni código, ni el venv de
  quantdesk). Sólo las decisiones del usuario en `PLAN_TSFM_*` (GAP-01). Ruedas: `git archive` a
  `E:/quantdesk-lab/build/<commit>/` y `maturin` allí, nunca en `S:/projects/quantdesk`.
- **Disco:** todo dato, caché (`HF_HOME`, `PIP_CACHE_DIR`), descarga y artefacto va a `E:/quantdesk-lab/`. C: tiene
  ~3 GB libres: si baja de 2 GB, parar y avisar. TI-13-PUB dentro de 100 GB.
- **Credenciales:** ninguna en repo, informes, prompts ni chat.
- **Fichas:** plantilla `ficha.md`, en `.git/sprint-runtime/s01/<ID>/ficha.md`, escritas con Write o script, nunca
  heredoc. Commit por tarea sólo de las rutas autorizadas; sin push (repo sin remoto).
- **Evidencia:** cada dataset e informe con SHA-256, semilla, fecha de corte y versión del motor (DoD §8).

## 5. Cuota y costes

- Antes de cada ola: `python -X utf8 "$HOME/.claude/skills/sprint/tools/claude_or.py" quota --weekly`, anotado en
  `EXECUTION.md` (crear al arrancar). Si no alcanza para la ola, esperar al reinicio; no recortar alcance.
- Lectura inicial (2026-11-07): Claude 38 % con el 69,6 % de la ventana (reinicio 2026-11-10 00:00 UTC); Codex 36 %
  con el 51,4 % (reinicio 2026-11-11 06:41 UTC).
- Medición según [USAGE_PROTOCOL](../USAGE_PROTOCOL.md); coordinador de costes: la raíz. `USAGE.md` del sprint en
  `current/`; tabla con `sprint_costs.py` de la skill global.

## 6. Relevo

`run_claude_handoff_launch.cmd` / `run_claude_handoff_recover.cmd` (motor de la skill global). HANDOFF en
`docs/plans/current/HANDOFF.md`; arranque en `docs/plans/arnes/ARRANQUE.md`. La sucesora usa el mismo modelo y
esfuerzo de la raíz y el mismo modo de permisos con que el usuario abrió la raíz. El hook de zonas avisa al 70 % y al
80 %.

## 7. Cómo arrancar (usuario)

1. Opcional, pero quita el único test rojo: desactivar los alias `python.exe`/`python3.exe` de la Microsoft Store.
2. Abrir una terminal en `S:/Projects/quantdesk-model` y ejecutar `claude --model claude-opus-5-5`.
3. Pegar el prompt de §8. Sólo esa sesión; los demás agentes los lanza la raíz.

## 8. Prompt de la raíz

```text
Eres la raíz del SPRINT-01 de quantdesk-model (docs/plans/current/SPRINT.md). Lee, por este orden,
docs/plans/SPRINT_PROJECT.md, docs/plans/GOBERNANZA.md, docs/plans/current/SPRINT.md y
docs/plans/current/LAUNCH.md, y usa la skill global execute-plan con la skill sprint (delegation.md,
ficha.md, handoff.md).

Al arrancar: ejecuta `python -X utf8 "$HOME/.claude/skills/sprint/scripts/deps.py" --repo . --sprint SPRINT-01`
(debe salir LISTO), lee la cuota semanal (LAUNCH §5) y crea docs/plans/current/EXECUTION.md con ambas lecturas.

Ejecuta las olas de LAUNCH §3 en orden, con cupo raíz + 3 descendientes, autor y revisor distintos, fichas
según LAUNCH §4 y aceptación verificada por ti sobre un HEAD fijo (no te fíes del informe del autor). Para en
cada puerta de usuario de LAUNCH §3 y pregúntame. No escribas en quantdesk, backend ni network. Registra cada
cierre en EXECUTION.md y STATUS.md con commit, pruebas y hashes. Relévate con handoff según LAUNCH §6.
Empieza por LAB-00-ENV.
```
