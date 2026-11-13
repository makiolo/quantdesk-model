# Issues vivas fuera de sprint

Una ficha viva por ID ([plantilla](TEMPLATE_ISSUE.md)). Las del sprint activo están en
`current/issues/`. Al cerrar un sprint, sus pendientes vuelven aquí con snapshot **NO RESUELTA** en
el archivo; archivado no significa resuelto. Las seleccionadas para el sprint siguiente siguen aquí hasta que se active
y entonces pasan a `current/issues/`.

| ID | Estado | Severidad | Destino | Ficha |
|---|---|---|---|---|
| ISSUE-TI09-SONDA-CADENAS | Abierto; se cierra con la cifra por sesión de S02-6 desde el 2026-11-12, y los días 2026-11-09…11 quedan como no medibles (R4). STATUS ya corregido (2026-11-13) | Media | Sprint siguiente seleccionado: SPRINT-03 (next), fila 3 (con S02-6; puerta: token de lectura tras el 2026-12-10) | [ficha](ISSUE-TI09-SONDA-CADENAS.md) |
| ISSUE-TI12-MT5-INTRADIA-LOCAL | Abierto (primera descarga m1/m5 de `@continuo` el 2026-11-09; alcance y periodicidad decididos el 2026-11-13: fx28 y `@continuo`, después 484 acciones; manual cada ≤ 6 semanas, primera antes del 2027-01-17; R8). Espera al desbloqueo de la cuenta MT5 | Media | Sprint siguiente seleccionado: SPRINT-03 (next), fila 4b (con S02-5; mutex del terminal) | [ficha](ISSUE-TI12-MT5-INTRADIA-LOCAL.md) |

Resueltas y archivadas fuera de sprint:

| ID | Resolución | Archivo |
|---|---|---|
| ISSUE-TI12-MT5-SYNC | **Resuelta** el 2026-11-13 (usuario, 2026-11-13, revisión de planes, R3): fusiona VELA-A-MEDIAS; la verificación 28/28 en qn y ClickHouse sustituye al cuadre; lo operativo (reactivar la tarea, carga nocturna de `@continuo`) pasa a SPRINT-03 fila 4c | [ficha](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md) · [manifiesto](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/ARCHIVE_MANIFEST.md) |
| ISSUE-TI12-MT5-VELA-A-MEDIAS | **Resuelta por fusión** en ISSUE-TI12-MT5-SYNC el 2026-11-13 (R3) | [ficha](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md) |

ISSUE-LAGO-FX-1D-CLOSE pasó al sprint activo al iniciar SPRINT-02 (2026-11-11) y se **resolvió** en su fila 1b:
[archive/SPRINT-02_2026-11-11_2026-11-13/issues/](../archive/SPRINT-02_2026-11-11_2026-11-13/issues/index.md).
