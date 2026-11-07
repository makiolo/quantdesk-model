# Dependencias entre sprints — quantdesk-model

Contrato leído por la skill global `sprint` (`sprint deps`, y al planificar, iniciar, lanzar y
cerrar). Condición: `cerrado` (el sprint remoto está en su `archive/`) o `activo` (está en su
`current/`; también se cumple si ya está cerrado). Estado: `decidido (usuario, AAAA-MM-DD)` bloquea
la activación si no se cumple; `propuesto` sólo avisa. Cada proyecto declara sólo sus dependencias
de entrada; las de salida se deducen leyendo los `DEPENDENCIAS.md` de los demás.

Regla del laboratorio (usuario, 2026-11-07): el sprint N del laboratorio es «lo que se puede hacer cuando termine el
sprint N de `quantdesk`», salvo SPRINT-01, que es lo que se puede hacer ya (sin dependencias de entrada).

## Proyectos relacionados

| Proyecto | Ruta |
|---|---|
| quantdesk | S:/projects/quantdesk |
| quantdesk-backend | S:/projects/quantdesk-backend |
| quantdesk-network | S:/projects/quantdesk-network |

## Dependencias de entrada

| Sprint local | Depende de | Condición | Motivo | Estado |
|---|---|---|---|---|
| SPRINT-02 | quantdesk SPRINT-02 | cerrado | Rueda versionada (E-RELEASE-WF), filtro HMM causal (E15-filter), corpus FG-16-hmmcop, universo59 | decidido (usuario, 2026-11-07) |
| SPRINT-03 | quantdesk SPRINT-03 | cerrado | TI-03-FMT, TI-00-ADR, TS-01-SIM, TS-02-GEN (para TS-02-DISC), DL-02-GATES | decidido (usuario, 2026-11-07) |
| SPRINT-04 | quantdesk SPRINT-04 | cerrado | DL-07-TRAIN, TI-06-CLI, TI-14-REG, TS-05-PREC (escalera de entrenamiento) | decidido (usuario, 2026-11-07) |

## Dependencias de tarea

Entre tareas de sprints que corren a la vez: **no bloquean la activación** del sprint local, sólo el inicio o la
parte de la tarea indicada (skill `sprint`, `references/deps.md`). SPRINT-01 no espera al backend porque cada día
sin archivar en el laboratorio también se pierde. El backend hace OC-01 y OC-02 en su SPRINT-01 y
OC-03…OC-05 en su SPRINT-02 (usuario, 2026-11-07).

| Tarea local (sprint) | Depende de (proyecto, sprint, tarea) | Motivo | Estado |
|---|---|---|---|
| TI-09-ARCH (SPRINT-01), captura al cierre con spot | quantdesk-backend SPRINT-02 OC-03-CLOSE (que espera a quantdesk-network SPRINT-01 OCS-01) | Hasta entonces se archiva la última captura de cada día y el subyacente del OHLCV diario | decidido (usuario, 2026-11-07) |
| TI-09-ARCH (SPRINT-01), aviso en origen | quantdesk-backend SPRINT-01 OC-01-FAIL, OC-02-ALERT | Fallos y huecos detectados en origen el mismo día | decidido (usuario, 2026-11-07) |
| TI-09-ARCH (SPRINT-01), duración y retención | quantdesk-backend SPRINT-02 OC-04-TIME, OC-05-RET | Captura acotada sin solapes; retención sin caducidad | decidido (usuario, 2026-11-07) |
