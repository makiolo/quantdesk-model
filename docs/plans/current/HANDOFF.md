# HANDOFF de la raíz — relevo 1

## Relevo
- Número: 1
- Sale: sesión 6c94f479-4b88-440a-8616-ef71c1a57e56, claude-opus-5-5, contexto 30.5 %
- Escrito: 2026-11-08T13:34:19+01:00
- HEAD al escribir: 4adda7bef93eef6efacfe730ea1a1eb6eb177a40
- LAUNCH: docs/plans/current/LAUNCH.md · bloque del coordinador: LAUNCH §2–§4 (raíz, cupo, olas y reglas de ficha) y §8
- Relevos anteriores: `git log --follow -- docs/plans/current/HANDOFF.md`
- Aceptado: sesión dd43fa94-0e5a-414a-818f-86561b20af08, 2026-11-08T13:35:24+01:00, contexto inicial 32.8 %

## Arranque
1. `D:/miniconda312/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/tools/claude_or.py handoff accept docs/plans/current/HANDOFF.md`: valida este archivo y anota tu sesión.
2. Lee sólo esto: este archivo, el bloque del coordinador del LAUNCH, `docs/plans/SPRINT_PROJECT.md` (y las
   políticas que liste), la skill global `sprint` (`C:/Users/makiolo/.claude/skills/sprint/SKILL.md`, `references/launch.md`,
   `references/handoff.md`) y las fichas de los hijos en vuelo. El resto, cuando haga falta y delegando.
3. `git status`, el estado del gate o candados de SPRINT_PROJECT «Comandos» y `git log --oneline 4adda7bef93e..HEAD`.
4. Adopta los hijos en vuelo: comprueba su proceso y su salida y vigílala; no relances un ID vivo.
5. Lanza el vigía de caché con `run_in_background` desde la raíz del repo:
   `D:/miniconda312/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/scripts/cache_heartbeat.py` (`references/handoff.md`, «Latido de caché»).
6. Busca en la memoria del proyecto (SPRINT_PROJECT «Identidad») las palabras clave del siguiente paso.
7. Commit del HANDOFF con la aceptación y continúa con «Siguiente paso».

## Estado
Recuperación en frío (RECOVERY-20261108-133223): la raíz anterior murió hacia las 13:11 sin relevar. Ola 2 en curso.
- Cerradas antes: LAB-00-ENV (`cb46ce2`). TI-01-INV: código aceptado (`cb46ce2`), falta la puerta de usuario 1.
- TI-13-PUB intento 2 (`4a56315`): verificación de la raíz en verde (selftest, suite 5 OK, `--verificar` OK con 1805
  ficheros y 130.066.541 filas). Revisión 2 de Codex (intento BDD 110, terminada a las 13:10 y cerrada ahora como
  rechazada): **RECHAZAR**; 4 de 6 corregidos; quedan ALTA guarda de 100 GB por estimación (2 × crudo, sin guarda
  incremental al escribir parquet), ALTA reintentos internos de `hf_hub_download` fuera de control (la ficha pide 3
  reintentos, Retry-After y ≤ 1 req/s), MEDIA tope total de LOTSA por fichero (descarga parcial), BAJA `procesar` sin
  PARADA controlada. Salida en `E:/quantdesk-lab/tmp/TI-13-PUB/revision2_out.md`.
- TS-00-PREC intento 1 (BDD 95): el autor commiteó `4adda7b` a las 13:10 y su sesión murió antes de informar. Logs del
  autor: selftest ok (8 pruebas), `run_selftests.py` 6 OK / 0 FALLO. Sin verificar por la raíz ni revisar.
- TI-12-MT5 espera la puerta 2; TI-09-ARCH, las cifras de TI-01-INV (puerta 1).

## En vuelo
- TI-02-DATA está CERRADA (`906f73e`, revisión 2 ACEPTAR, EXECUTION «Cierre de TI-02-DATA»).
- Directiva del usuario «todo con Claude», vigente hasta el 2026-11-10 01:00 CET (EXECUTION, A14). Tres autores
  Opus 5.5 high, agentes en segundo plano de la sesión dd43fa94, base `82d7f4f`, fichas en
  `.git/sprint-runtime/s01/<ID>/ficha.md`:
  - TS-00-BENCH, intento BDD 123;
  - TI-12-MT5, fase A (sin terminal real), BDD 124;
  - TI-02-DATA-DEUDA, BDD 125.
  Si esta sesión muere, relanzarlos desde su ficha y su último commit.
- Pregunta al usuario pendiente: qué precios del lago usa TS-00-BENCH, el proxy `cierre` (recomendado) o sólo el
  estricto. TS-00-BENCH no se lanza hasta que conteste.

## Decisiones
- Raíz (A12): los 4 hallazgos de la revisión 2 de TI-13-PUB se corrigen en un intento 3 (los dos ALTA son requisitos
  literales de la ficha: guarda de 100 GB y ritmo/reintentos). Para el Hub, GET propios con el mismo cliente de
  Binance, como propone el propio comentario `shortcut:` del autor. Versionado en EXECUTION.md (ola 2).
- Raíz: TS-00-PREC sigue el protocolo normal: verificación de la raíz sobre `git archive 4adda7b` + revisión de Codex.
- Incidente A9 (cuarto): un heredoc con backticks en Bash ejecutó los fragmentos (sin escrituras ni cambios; sólo
  «command not found» y un tar por stdout). La raíz escribe ficheros sólo con Write/Edit.

## Preguntas abiertas al usuario
- Respondidas el 2026-11-08: TI-09-ARCH RETIRADA del sprint (`eccc8d2`); el usuario autoriza otro token de sólo
  lectura igual al de TI-01-INV para TI-02-DATA («emite otro token de solo lectura»). La raíz lo emite en mini sólo
  cuando `descarga_lago.py` esté leído y con selftest en verde, y lo revoca al terminar la descarga (EXECUTION, ola 3, A13).
- Puerta 2 (TI-12-MT5): el usuario abre y autentica el terminal MT5 («luego lo resuelvo»).

## Conocimiento promovido
nada nuevo: el proyecto no tiene herramienta de conocimiento (SPRINT_PROJECT §1).

## Siguiente paso
Hecho en este tramo:
- TI-13-PUB CERRADA en `7ea6d94` y TS-00-PREC en `5afc795`.
- TI-01-INV CERRADA: la raíz ejecutó el inventario con el token 32, ya revocado. Las cadenas de opciones están vacías
  en qn y la flota no tiene GPU (EXECUTION, «Cierre de TI-01-INV»).

En vuelo: autor de TI-02-DATA, fase 1 (Sonnet 5.5 xhigh, intento BDD 119, ficha en
`.git/sprint-runtime/s01/TI-02-DATA/ficha.md`, base `eccc8d2`).

Siguiente paso:
1. Al entregar la fase 1: verificar sobre su commit, leer entero `descarga_lago.py`, correr su selftest en mini.
2. Emitir el token (`ti02-lago-20261108`, `main`, `sub:market.>`, skill `qn-token`), ejecutar la descarga en mini,
   copiar el volcado a `E:/quantdesk-lab/data/lago/`, revocar y borrar.
3. Pedir al autor la fase 2 por mensaje; luego revisión de otro modelo (Codex si le queda margen; si no, Opus).
4. TS-00-BENCH tras el primer dataset congelado. TI-12-MT5, tras la puerta 2.
