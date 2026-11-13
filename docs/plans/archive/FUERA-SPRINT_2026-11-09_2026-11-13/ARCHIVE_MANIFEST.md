# Manifiesto — FUERA-SPRINT_2026-11-09_2026-11-13

Issues fuera de sprint resueltas y verificadas en la revisión de planes del 2026-11-13 (skill `sprint`,
`references/lifecycle.md`: «Fuera de sprint, usar `archive/FUERA-SPRINT_<detección>_<resolución>/` al resolver y
verificar»). Clave: detección más antigua de las dos fichas (ISSUE-TI12-MT5-SYNC, 2026-11-09) y resolución 2026-11-13.

- **Motivo:** decisión del usuario «(usuario, 2026-11-13, revisión de planes, R3)»: cerrar ISSUE-TI12-MT5-SYNC fusionando
  ISSUE-TI12-MT5-VELA-A-MEDIAS. La verificación 28/28 en qn y ClickHouse sustituye al cuadre de 0 puntos del 2026-11-09
  (GAP-ISSUES-02 aceptado). Lo que queda (reactivar la tarea programada, primera pasada limpia, carga nocturna de
  `@continuo`) pasa a la fila 4c (TI-12-MT5-OPS) de [SPRINT-03](../../current/SPRINT.md).
- **Movido con `git mv`** en la aplicación de la revisión (2026-11-13); commit: pendiente (lo pone la raíz de guardia).
- **Hashes:** SHA-256 del contenido. «Previo» = el fichero en `issues/` en `7f5a5d0` (HEAD antes de la revisión);
  «posterior» = el archivado al terminar la aplicación (incluye la sección «Revisión de planes (2026-11-13)» de los
  revisores, la resolución y los enlaces relativos corregidos por el cambio de profundidad).

| Origen | Destino (en esta carpeta) | Estado | SHA-256 previo | SHA-256 posterior |
|---|---|---|---|---|
| `docs/plans/issues/ISSUE-TI12-MT5-SYNC.md` | [issues/ISSUE-TI12-MT5-SYNC.md](issues/ISSUE-TI12-MT5-SYNC.md) | **Resuelta** (R3); criterio 3 aceptado por R3, criterio 7 trasladado a SPRINT-03 fila 4c, criterio 8 hecho | `fe2c3d7cbea62be9b1511a6160ccac612343986d846a4fa586780c34df03451c` | ver nota |
| `docs/plans/issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md` | [issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md](issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md) | **Resuelta por fusión** en SYNC (R3); su criterio 3 = SYNC 7, trasladado a SPRINT-03 fila 4c | `0b89418f0757ca5869e2d83df7ba3cffcdd5f26e1db1e84bb2421672efc08737` | ver nota |

Nota: el SHA-256 posterior se calcula sobre el contenido que entre en el commit de la raíz (`sha256sum` de cada fichero
de esta carpeta); al escribir este manifiesto, antes del commit, eran `327fd139…1de16` (SYNC) y `92231b10…b0d42`
(VELA-A-MEDIAS), y cambian si la raíz retoca las fichas al revisar el diff.

## Commits que acreditan los criterios (informe de la revisión de issues, 2026-11-13)

| Criterio (SYNC) | Evidencia |
|---|---|
| 1. Guarda de historia | `2ac3f8f`; `prueba_guarda_historia` en `publicador_mt5_lib/selftests.py:548`; suite del DoD de SPRINT-02 (`fb5d21f`, 14 OK) |
| 2. Modo de reenvío | `9e2a9eb` (`--republicar-revisiones`, `--pausa-serie-s`); `selftests.py:430-443` |
| 3. 23 velas republicadas | `b9cbbbe`; `publicador_2026-11-10.jsonl` línea 9; verificación 28/28 en qn (`verif_republicacion.py`); aceptado en lugar del cuadre por R3 |
| 4. Llega a lago y ClickHouse | `d6d7a55` (laboratorio); backend `9d63c68` |
| 5. Horizonte de revisión | `f660654` (respuesta de network: no aplica a `market.ohlcv.v2`) |
| 6. Carga de `@continuo` aplazada | registros de `E:/quantdesk-lab/runs/TI-12-MT5/publicador/` sin `--simbolos @continuo` (fuera de Git) |
| 7. Tarea y primera pasada limpia | **no cumplido**: trasladado a SPRINT-03 fila 4c por R3; tarea desactivada el 2026-11-13 (R2) |
| 8. Documentación | aplicación de la revisión del 2026-11-13 (este cambio; commit pendiente) |

VELA-A-MEDIAS: `1fff755` (horario), `2ac3f8f` (guarda), `9e2a9eb` (reenvío); criterios 1 y 2 hechos, 3 = SYNC 7.

## Enlaces reapuntados

- `docs/plans/DEPENDENCIAS.md`, `backlog/README.md`, `backlog/PLAN_DATOS_VIA_QN.md`, `backlog/REVISIONES.md`,
  `issues/index.md` e `index.md` (tablas de estado): a esta carpeta o al texto nuevo.
- Edición editorial sólo del destino del enlace en dos dossieres archivados (su SHA-256 posterior en sus manifiestos deja
  de coincidir por esta línea): `archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md` (dos enlaces a VELA-A-MEDIAS) y
  `archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md` (enlace a `future/SPRINT-04`, renumerado a SPRINT-05 por R1).
- El bloque kanban generado de `index.md` no se edita a mano: lo regenera `sprint_db.py kanban --write`.

Evidencia fuera de Git (registros del publicador, logs de la suite) en `E:/quantdesk-lab/`, citada por ruta. Ninguna
credencial copiada.
