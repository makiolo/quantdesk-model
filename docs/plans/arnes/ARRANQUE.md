1. `python -X utf8 {tool} handoff accept {file}`: valida este archivo y anota tu sesión.
2. Lee sólo esto: este archivo, el bloque del coordinador del LAUNCH, `docs/plans/SPRINT_PROJECT.md` (y las
   políticas que liste), la skill global `sprint` (`{skill}/SKILL.md`, `references/launch.md`,
   `references/handoff.md`) y las fichas de los hijos en vuelo. El resto, cuando haga falta y delegando.
3. `git status`, el estado del gate o candados de SPRINT_PROJECT «Comandos» y `git log --oneline {head}..HEAD`.
4. Adopta los hijos en vuelo: comprueba su proceso y su salida y vigílala; no relances un ID vivo.
5. Lanza el vigía de caché con `run_in_background` desde la raíz del repo:
   `python -X utf8 {skill}/scripts/cache_heartbeat.py` (`references/handoff.md`, «Latido de caché»).
6. Busca en la memoria del proyecto (SPRINT_PROJECT «Identidad») las palabras clave del siguiente paso.
7. Commit del HANDOFF con la aceptación y continúa con «Siguiente paso».
