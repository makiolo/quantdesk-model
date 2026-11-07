
## Arranque

Eres la raíz nueva tras una interrupción. Nadie escribe en el repo por la raíz anterior: ella murió.
1. Lee este informe, el último HANDOFF y el bloque del coordinador del LAUNCH que nombra.
2. `git status` y el estado del gate o candados de SPRINT_PROJECT. Si un candado es de un proceso muerto,
   sigue la política de gates del proyecto.
3. Hijos interrumpidos: mira su salida y el WIP de su ID en el árbol. Lo acabado se revisa y acepta con el
   protocolo normal; lo que quedó a medias se conserva y se relanza el ID desde su ficha con la salida parcial
   como contexto. Nunca descartes WIP sin mirarlo. El WIP de otras sesiones vivas no es tuyo.
4. Reconstruye en un HANDOFF nuevo:
   `python -X utf8 {tool} handoff new {file} --from-session {session}`,
   rellénalo con el estado reconstruido, commit, y después `handoff accept {file}`.
5. Sigue con su «Siguiente paso».
