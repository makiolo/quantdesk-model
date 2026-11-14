# HANDOFF de la raíz — relevo 2

## Relevo
- Número: 2
- Sale: sesión 2ab53d59-60b1-4f92-84cf-bf4a7115386f (`quantdesk-model-00`), claude-opus-5-5, contexto 70.5 %
- Escrito: 2026-11-14T11:25:46+01:00
- HEAD al escribir: ad43ba057610b5ea1b9296b4ea836be54f3d0f0c
- LAUNCH: docs/plans/current/LAUNCH.md · bloque del coordinador: «§8. Prompt de la raíz (relevos y recuperación)»
- Relevos anteriores: `git log --follow -- docs/plans/current/HANDOFF.md`

## Arranque
1. `S:/Projects/quantdesk-model/.venv/Scripts/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/tools/claude_or.py handoff accept docs/plans/current/HANDOFF.md`: valida este archivo y anota tu sesión. Después, pon tu nombre de `ListAgents` en `~/.claude/relevos.json`, clave `quantdesk-model`.
2. Lee sólo esto: este archivo, el bloque del coordinador del LAUNCH, `docs/plans/SPRINT_PROJECT.md` (y las
   políticas que liste), la skill global `sprint` (`C:/Users/makiolo/.claude/skills/sprint/SKILL.md`, `references/launch.md`,
   `references/handoff.md`) y la ficha en espera (`.git/sprint-runtime/s03/TI-12-MT5-OPS/ficha-turno.md`). El resto,
   cuando haga falta y delegando.
3. `git status`, el estado del gate o candados de SPRINT_PROJECT «Comandos» y `git log --oneline ad43ba057610..HEAD`.
4. Hijos en vuelo: ninguno (abajo).
5. **Vigía, no `cache_heartbeat.py`** (la skill lo sustituyó el 13-11; `references/handoff.md`, «Latido de caché»):
   - el servidor `wsvigia.py` sigue vivo en el puerto **8775** (`.git/sprint-runtime/s03/wsvigia.pid`), con las listas
     `s03/fins.txt` y `s03/follow.txt`;
   - comprueba su `.pid` y suscríbete con `Monitor({ws: {url: 'ws://127.0.0.1:8775/'}, timeout_ms: 1800000})`, re-armado
     en cada caducidad;
   - si está muerto, arráncalo con `tools/lanza/lanza.py --dir .git/sprint-runtime/s03 --nombre wsvigia -- <python>
     tools/vigia/wsvigia.py --port 8775 -- --base .git/sprint-runtime/s03 --fins s03/fins.txt --follow s03/follow.txt`.
   - **Paso 5b (alertas): SUSPENDIDO** hasta el 2026-11-17 00:59 (decisión del usuario, SKILL.md); no lances la revisión.
6. Busca en la memoria del proyecto: `mt5-descargas-prudentes`, `codex-resume-modelo`, `bash-trampas-commit`.
7. Commit del HANDOFF con la aceptación y continúa con «Siguiente paso».

**Shell:** herramienta PowerShell; mensajes de commit con Write/Set-Content a un fichero del scratchpad y `git commit -F`.

## Estado
- **SPRINT-03 activo.** Detalle completo en `current/EXECUTION.md` (secciones del relevo 1).
- **Fila 1 (contrato TI-02-DIARIO): cerrada** (`1e50e5e`, relevo 0).
- **Fila 2 (código TI-02-DIARIO): CERRADA** el 2026-11-14 en `a47ccf4`:
  - r1 rechazó la primera entrega; r2 ACEPTAR, con A5 legítimo;
  - gate de la raíz 15/15 sobre HEAD fijo;
  - registrada en SPRINT.md, STATUS.md y la BDD (tarea `cerrada`).
- **Despliegue de TI-02-DIARIO** (fuera de la fila):
  - token id 43 instalado en `E:/quantdesk-lab/secrets/ti02-diario.env` (comprobado sin leer el valor);
  - **falta que el backend registre la tarea de Windows** (su PUB-05-EXPORT, con permiso del usuario); su raíz activa
    es `quantdesk-backend-22` (ver `relevos.json`). Dirá la hora de la primera ejecución: revisar su log en
    `E:/quantdesk-lab/runs/TI-02-DIARIO/`.
- **MT5 desbloqueado** (usuario, 2026-11-14), con contraseña nueva ya puesta en `E:/quantdesk-lab/secrets/mt5.json`.
  - Prueba de login con turno: OK.
  - **Primera pasada del publicador** (09:26–09:34, exit 0): sólo 5 de 28 pares publicaron (10–12-11). Los otros 23
    tenían historia del terminal sólo hasta el 09-11 (sin sincronizar) y todos retienen 1 vela.
  - La tarea `\quantdesk\publicador_mt5` sigue **Disabled**.
- **quantlab** (proyecto nuevo, raíz `quantlab-f0`) es el único que descarga histórico de MT5 (usuario):
  - las filas 4a, 4b y 5 pasan a sus sprints 1 y 2;
  - la 4c sigue aquí sólo como publicador diario con turno hasta el traspaso;
  - filas en DEPENDENCIAS y GOBERNANZA (`8ead3db`);
  - hay que replanificar SPRINT-03 al revisarlo o cerrarlo.
- **Filas 3, 6 y 7:** esperan su puerta (fecha ≥ 2026-12-11; PUB-02 del backend).
- **Cuota** (11:2x): Claude 93 % (reinicio el 17-11 01:00), Codex 91 % (reinicio el 18-11 09:07). Codex tiene dos
  cuentas: al 98 % se avisa al usuario. Lo que deba ir a Claude usa antes Fable 5.2.

## En vuelo
Ninguno. El cron de la segunda pasada (13:07) se canceló al relevar: lo hace la sucesora (abajo).

## Decisiones
Todas versionadas en EXECUTION (relevo 1), salvo que se diga otra cosa:
- **Fila 2:** cierre con `a47ccf4`. Decisiones de la raíz en la ficha:
  - ausencia parcial de FX = `sin_mt5`;
  - `manifest_sha256` del intento también en `sin_mt5` y `error`;
  - festivo FX sin barras = `ok` sin publicación.
- **rsc-brain:** plan en el backlog del backend (`c01e49d`). El usuario lo integró en el SPRINT-02 del backend (raíl R,
  `c372ae8`) con estas GAP:
  - GAP-1: `qn-pgprod`;
  - GAP-2: pública con OAuth;
  - GAP-3: sin embeddings.
  La GAP-4 y la GAP-5 las pregunta el backend.
- **MT5** (usuario, AskUserQuestion):
  - reactivar hoy el publicador;
  - descargas grandes tras el 18-11 (ahora de quantlab);
  - token id 36 mantenido: revisado el 14-11, la próxima revisión al cerrar SPRINT-03.
- **quantlab:** decisiones del usuario retransmitidas por `quantlab-f0`, versionadas en DEPENDENCIAS y GOBERNANZA
  (`8ead3db`).
- **Cambios de la skill anotados:**
  - avisar de todo cambio en la skill;
  - compilación sin exportaciones;
  - `sprint_db` regenera la web;
  - alertas suspendidas hasta el 17-11;
  - turno de MT5 (`~/.claude/mt5/turno.lock` y `uso.jsonl`);
  - quantlab, único para histórico;
  - dos cuentas de Codex y Fable para Claude.

## Preguntas abiertas al usuario
Ninguna.

## Compromisos con otras raíces
- **Backend (`quantdesk-backend-22`):** registra la tarea de Windows de TI-02-DIARIO y avisa de la primera ejecución.
  Le prometimos reactivar la tarea diaria del publicador antes del lunes 16-11 a las 23:30.
- **quantdesk (`quantdesk-cb` o la que figure en `relevos.json`):** informada del cierre de la fila 2. No queda nada
  pendiente.
- **quantlab (`quantlab-f0`):** espera que respetemos `turno.lock` hasta el traspaso y que no añadamos código de
  descarga de MT5. Avisará cuando QL-10 entregue el h1 en `E:/quantlab`.
- **network (`quantdesk-network-b2`):** nada pendiente.

## Conocimiento promovido
- Memoria nueva `codex-resume-modelo`: `codex exec resume` sin `-m` arranca con el modelo por defecto. Propuesto al
  usuario anotarlo en `tools/lanza/README.md` de la skill; no hubo respuesta.
- Lo demás está en EXECUTION.

## Siguiente paso
1. **Segunda pasada del publicador** con turno, a partir de las 13:00:
   - comprobar que no existe `~/.claude/mt5/turno.lock`;
   - lanzar con `lanza.py` en `.git/sprint-runtime/s03/TI-12-MT5-OPS` (nombre `pub-pasada2`) el ejecutor
     `S:/Apps/tmp/claude/claude/37f65974f743234e/2ab53d59-60b1-4f92-84cf-bf4a7115386f/scratchpad/mt5_turno_runner.py`,
     con `--plan "…" -- <python> -X utf8 scripts/publicador_mt5.py --ejecutar --topic market.ohlcv.v2 --intervalos 1d
     --republicar-revisiones --pausa-serie-s 15` (orden completa en `s03/TI-12-MT5-OPS/pub-pasada1.log` y
     `lz-pub-pasada1-eventos.jsonl`);
   - añadir su `.fin` a `s03/fins.txt`;
   - comparar con la pasada 1 (`E:/quantdesk-lab/runs/TI-12-MT5/publicador/ultimo.json`) y anotarlo en EXECUTION;
   - al primer error de autenticación o de límite, parar y avisar al usuario.
2. **Envoltorio del turno de MT5 para la tarea diaria.** Ficha escrita: `.git/sprint-runtime/s03/TI-12-MT5-OPS/ficha-turno.md`
   (L3, base `ad43ba0`).
   - Revisión previa de la ficha con `gpt-6-luna` high, sólo lectura.
   - Autor Codex `gpt-6.1-sol` high; revisor `gpt-6-luna` high (revisión obligatoria en L3 hasta el 24-11).
   - Al aceptarlo: `run_scheduler.cmd` registra la tarea con turno; después, comprobar que está habilitada (`Ready`).
   - **Antes del lunes 16-11 a las 23:30.**
3. Seguir los avisos del backend sobre la primera ejecución de TI-02-DIARIO.
