# HANDOFF de la raíz — relevo 3

## Relevo
- Número: 3
- Sale: sesión af8558d2-088f-40cf-acca-a2d87c0c3a37 (`quantdesk-model-c1`), claude-opus-5-5, contexto 46.3 %
- Escrito: 2026-11-14T17:23:40+01:00
- HEAD al escribir: 08178ed13bec0899c1e9931cf25796020c00c128 (más el commit de este HANDOFF)
- Motivo: **cambio de modelo, no de contexto.** Orden del usuario (2026-11-14 ~17:40, retransmitida por `quantlab-d0`;
  SKILL.md:171): toda raíz corre en **Fable 5.2 high**; relevar «ahora mismo» en el primer punto tranquilo.
- LAUNCH: docs/plans/current/LAUNCH.md · bloque del coordinador: «§8. Prompt de la raíz (relevos y recuperación)»
- Relevos anteriores: `git log --follow -- docs/plans/current/HANDOFF.md`
- Aceptado: sesión 2ec16109-67c6-4c46-b373-8ea8b7805ec7, 2026-11-14T17:24:50+01:00, contexto inicial 66.6 %

## Arranque
1. `S:/Projects/quantdesk-model/.venv/Scripts/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/tools/claude_or.py handoff accept docs/plans/current/HANDOFF.md`: valida este archivo y anota tu sesión. Después, pon tu nombre de `ListAgents` en `~/.claude/relevos.json`, clave `quantdesk-model`.
2. Lee sólo esto: este archivo, el bloque del coordinador del LAUNCH, `docs/plans/SPRINT_PROJECT.md` y la skill global
   `sprint` (`C:/Users/makiolo/.claude/skills/sprint/SKILL.md`, `references/launch.md`, `references/handoff.md`). No
   hay fichas en vuelo. El resto, cuando haga falta y delegando.
3. `git status` y `git log --oneline 08178ed13bec..HEAD`. Gate o candados: ninguno propio (SPRINT_PROJECT «Comandos»).
4. Hijos en vuelo: ninguno.
5. **Vigía, no `cache_heartbeat.py`** (`references/handoff.md`, «Latido de caché»):
   - el servidor `wsvigia.py` sigue vivo en el puerto **8775** (`.git/sprint-runtime/s03/wsvigia.pid`, PID 28040), con
     las listas `s03/fins.txt` y `s03/follow.txt`;
   - comprueba el `.pid` y suscríbete con `Monitor({ws: {url: 'ws://127.0.0.1:8775/'}, timeout_ms: 1800000})`, re-armado
     en cada caducidad;
   - si está muerto: `tools/lanza/lanza.py --dir .git/sprint-runtime/s03 --nombre wsvigia -- <python>
     tools/vigia/wsvigia.py --port 8775 -- --base .git/sprint-runtime/s03 --fins s03/fins.txt --follow s03/follow.txt`.
   - **Paso 5b (alertas): SUSPENDIDO** hasta el 2026-11-17 00:59 (SKILL.md); no lances la revisión.
6. Busca en la memoria del proyecto: `mt5-descargas-prudentes`, `codex-resume-modelo`, `bash-trampas-commit`.
7. Commit del HANDOFF con la aceptación (y push) y continúa con «Siguiente paso».

**Shell:** herramienta PowerShell; mensajes de commit con Set-Content/Write a un fichero del scratchpad y `git commit -F`.
Nada de `Start-Sleep` encadenado (lo bloquea el arnés): para esperar, `run_in_background` o el vigía.

## Estado
- **SPRINT-03 activo.** Detalle en `current/EXECUTION.md`, sección «Relevo 2».
- **Filas 1 y 2 (TI-02-DIARIO): cerradas** (`1e50e5e`, `a47ccf4`). Despliegue: token 43 instalado; la tarea de Windows
  la registra el backend en su PUB-05-EXPORT (su SPRINT-03, aún sin empezar). Avisará de la hora de la primera
  ejecución. Nada que hacer aquí hasta entonces.
- **TI-12-MT5-OPS (fila 4c, parte operativa), envoltorio del turno: ACEPTADO** (`494d97a`; ficha v2, autor
  `gpt-6.1-sol`, revisor `gpt-6-luna` ACEPTAR; gate de la raíz 16/16). **Tarea `\quantdesk\publicador_mt5`
  reactivada y Ready** con turno; primera ejecución programada **hoy 14-11 a las 23:30**.
- **Segunda pasada del publicador** (13:07–13:16, exit 0): los 28 pares están al día hasta el 12-11 (69 velas nuevas
  publicadas). La vela del viernes 13-11 queda retenida hasta que haya historia posterior: lunes 16-11 a las 23:30.
- **Filas 4a, 4b y 5:** pasan a quantlab (decisión del usuario, `8ead3db`); hay que replanificar SPRINT-03 al revisarlo
  o cerrarlo. **Filas 3, 6 y 7:** esperan su puerta (fecha ≥ 2026-12-11; PUB-02 del backend).
- **Cuota** (11:28): Claude 94 % (reinicio el 16-11 23:59), Fable 0 %. **Codex reiniciado al 0 %** (aviso de la skill;
  próximo reinicio el 21-11 a las 11:38 UTC; quedan 2 reinicios). Al 98 %, avisar al usuario.

## En vuelo
Ninguno. El cron de las 23:47 (revisar la ejecución de las 23:30) era de la sesión saliente y se cancela al relevar:
lo programa la sucesora (abajo).

## Decisiones
Todas versionadas en EXECUTION («Relevo 2»):
- Ficha del turno v2: la raíz aceptó 8 de los 10 cambios de la revisión previa y descartó los excesivos. No se
  verifica la identidad del proceso por PID reutilizado: el PID sólo informa, y un candado ajeno nunca se borra. La
  única retirada automática es la de un huérfano propio de `tarea-programada`.
- Tarea del publicador reactivada por decisión del usuario («reactivar hoy el publicador», EXECUTION del relevo 1).
- Usuario, vía `quantdesk-6c`: los tokens que necesitemos (el 43 u otros) los podemos generar nosotros, coordinando con
  backend y network; ningún valor en chats ni logs.
- Usuario, vía quantlab: las fuentes que no son de MT5 (PUB-*) se quedan en el backend.
- Skill: raíces en Fable 5.2 high (LAUNCH §2 actualizado); Codex reiniciado, se sigue priorizando.

## Preguntas abiertas al usuario
Ninguna.

## Compromisos con otras raíces
Usa los nombres actuales de `~/.claude/relevos.json`; cambian a menudo.
- **Backend (`quantdesk-backend-22`):** avisará de la hora de la primera ejecución de TI-02-DIARIO. El compromiso del
  publicador (reactivarlo antes del lunes 16-11 a las 23:30) quedó **cumplido** y avisado.
- **quantlab (`quantlab-d0` en `relevos.json`; antes `quantlab-f0` y `quantlab-7a`):**
  - comparte `turno.lock` y mantiene el descriptor abierto durante su turno; le pedimos que lo abra con compartición de
    lectura, porque nuestro `mt5_turno.py:179` lo lee y, si no puede, falla en vez de esperar (límite anotado);
  - avisará antes de su próximo turno (aplica primero QL-05b);
  - el usuario corrigió hoy un fallo de conexión en `D:\dev\deeplearning_dev\config_pro.py`, no en `mt5.json`.
- **quantdesk (`quantdesk-6c`):** nada pendiente.
- **network:** nada pendiente.

## Conocimiento promovido
- La primera ejecución real de `mt5_turno.py` (pasada 2) quedó bien registrada en `uso.jsonl`, con las series.
- Gotcha nuevo, anotado en EXECUTION y en las pruebas: el `python.exe` del `.venv` en Windows es un lanzador, y su PID
  no coincide con el del Python que escribe el candado.
- Nada nuevo para la memoria.

## Siguiente paso
1. **Programar con `CronCreate` (un solo disparo, hoy 14-11 a las 23:47)** la revisión de la primera ejecución
   programada del publicador con turno:
   - `LastTaskResult` (`Get-ScheduledTask -TaskPath '\quantdesk\' -TaskName publicador_mt5 | Get-ScheduledTaskInfo`);
   - la última línea de `~/.claude/mt5/uso.jsonl` (exit, errores, series);
   - que no quede `~/.claude/mt5/turno.lock`.
   Anotarlo en EXECUTION con commit y push. Si hubo un error de autenticación o un límite de MT5, avisar al usuario con
   `PushNotification`. El 13-11 el Programador anotó `LastTaskResult` = 2: comprobar que la de hoy da 0.
2. Lunes 16-11 a las 23:30: comprobar que se publica la vela del 13-11 (o del 16-11) en los 28 pares.
3. Esperar los avisos del backend (TI-02-DIARIO) y de quantlab (próximo turno de MT5). Mientras tanto no hay olas
   lanzables; replanificar SPRINT-03 (filas 4a, 4b y 5 a quantlab) al revisarlo o cerrarlo.
