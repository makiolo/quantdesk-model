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

**Nota (propuesto, sin fila):** TI-09-ARCH mejora cuando `quantdesk-backend` entregue la captura al cierre con spot
(OC-03-CLOSE de `S:/projects/quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md`, que a su vez
necesita campos nuevos en `market.options.chain` de `quantdesk-network`). A 2026-11-07, OC-03 no está en ningún
sprint del backend (su next es SPRINT-01, Tier 3/streaming; el plan sigue en backlog). Cuando se asigne, añadir aquí
una fila `propuesto` del sprint local que lo consuma frente a `quantdesk-backend SPRINT-NN` / `activo` o `cerrado`.
