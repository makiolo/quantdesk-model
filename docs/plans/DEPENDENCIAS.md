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

SPRINT-02 no tiene dependencia de entrada desde el 2026-11-11: el usuario lo partió para activarlo sin esperar a
quantdesk SPRINT-02, y las filas que la necesitaban (antes «SPRINT-02 ← quantdesk SPRINT-02 cerrado», decidido el
2026-11-07) pasaron a SPRINT-03 como filas S02-1…S02-4.

| Sprint local | Depende de | Condición | Motivo | Estado |
|---|---|---|---|---|
| SPRINT-03 | quantdesk SPRINT-03 | cerrado | TI-03-FMT, TI-00-ADR, TS-01-SIM, TS-02-GEN (para TS-02-DISC), DL-02-GATES; y, desde el 2026-11-11, las filas S02-1…S02-4 (rueda E-RELEASE-WF, E15-filter, FG-16-hmmcop, universo59), que necesitan quantdesk SPRINT-02 cerrado (lo cubre el cierre de su SPRINT-03) | decidido (usuario, 2026-11-07; ampliado 2026-11-11) |
| SPRINT-04 | quantdesk SPRINT-04 | cerrado | DL-07-TRAIN, TI-06-CLI, TI-14-REG, TS-05-PREC (escalera de entrenamiento) | decidido (usuario, 2026-11-07) |

## Dependencias de tarea

Entre tareas de sprints que corren a la vez: **no bloquean la activación** del sprint local, sólo el inicio o la
parte de la tarea indicada (skill `sprint`, `references/deps.md`). SPRINT-01 no espera al backend ni a network: hasta
que lleguen sus tareas, el laboratorio lee del lago en el modo «mientras tanto». El backend hace OC-01 y OC-02 en su SPRINT-01 y
OC-03…OC-05 en su SPRINT-02 (usuario, 2026-11-07).

TI-09-ARCH salió de SPRINT-01 el 2026-11-08 (usuario) y vive en
[backlog/PLAN_ARCHIVO_OPCIONES.md](backlog/PLAN_ARCHIVO_OPCIONES.md); sus filas se conservan con el estado del
2026-11-09 (revisión de planes).

| Tarea local (sprint) | Depende de (proyecto, sprint, tarea) | Motivo | Estado |
|---|---|---|---|
| TI-09-ARCH (backlog; fuera de SPRINT-01 desde 2026-11-08), captura al cierre con spot | quantdesk-backend SPRINT-02 OC-03-CLOSE (que espera a quantdesk-network SPRINT-01 OCS-01, ya cerrada) | Hasta entonces se archiva la última captura de cada día, **sin spot de respaldo** (se quita el «subyacente del OHLCV diario»; sólo `underlying_price` de OC-03: usuario, 2026-11-10, revisión de planes, D11) | decidido (usuario, 2026-11-07; enmendado 2026-11-10); pendiente |
| TI-09-ARCH (backlog), aviso en origen | quantdesk-backend SPRINT-01 OC-01-FAIL, OC-02-ALERT | Fallos y huecos detectados en origen el mismo día | decidido (usuario, 2026-11-07); **servida** (2026-11-08/09) |
| TI-09-ARCH (backlog), lectura bajo demanda | quantdesk-network SPRINT-01 OCS-01, OCS-02 | Garantía de S3 sin retención en los topics `market.*` de los scrapers (decisión 12-A): el laboratorio lee del lago y no copia a diario | decidido (usuario, 2026-11-07); **servida** (2026-11-08). **Garantía rota** por la herramienta genérica de borrado en el lago (usuario, 2026-11-09). Sin copia propia: la copia es la común de network (`PLAN_COPIA_PERIODICA_LAGO`) y el laboratorio sólo guarda lo leído al cortar cada dataset, con hash; `lake delete` no se usa sobre `market.*` hasta que exista (usuario, 2026-11-10, revisión de planes, D7; PLAN_ARCHIVO_OPCIONES §4) |
| TI-09-ARCH (backlog), universo | quantdesk-backend (sin sprint) 5–10 ETF/índices en la captura, en OC-03 o tarea al lado | Subyacentes con `asset_type` ETF/INDEX en el lector y el informe de huecos | decidido (usuario, 2026-11-09) |
| TI-13-PUB ampliación (SPRINT-02 fila 7) y TI-02-DATA ampliada | quantdesk-backend (backlog, sin sprint) `PLAN_PUBLICADORES_MERCADO_PUBLICO` | Las fuentes públicas (Yahoo/Stooq, FRED, cripto) entran al lago sólo por publicadores del backend (A16 bis); el laboratorio las consume vía qn | decidido (usuario, 2026-11-09) |
| TI-02-DIARIO (backlog; el laboratorio escribe el código, el backend lo programa en Dagster) | quantdesk-backend SPRINT-03 (futuro, en planificación) `PLAN_PUBLICADORES_MERCADO_PUBLICO`, tarea OAS y programación del exportador tras el cierre de Nueva York | Exportador diario de D-I4: escribe desde qn el mercado del día y los datasets que `quantdesk` abre, incluidos los OAS para XVA; debe existir antes de la ola 1 de SPRINT-03 de `quantdesk` | decidido (usuario, 2026-11-09; dueño decidido por el usuario el 2026-11-10, revisión de planes, D5 y D6) |
| TI-12-MT5-SYNC (fuera de sprint; carga nocturna de `@continuo`) | quantdesk-network (excepción al horizonte de revisión de qn si venció) y aviso a quantdesk-backend | Republicar las 23 velas 1d del 2026-11-09 y aplazar la carga de `@continuo` hasta cerrar [ISSUE-TI12-MT5-SYNC](issues/ISSUE-TI12-MT5-SYNC.md) | decidido (usuario, 2026-11-10, revisión de planes, D1) |
