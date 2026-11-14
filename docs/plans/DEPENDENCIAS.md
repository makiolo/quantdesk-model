# Dependencias entre sprints — quantdesk-model

Contrato leído por la skill global `sprint` (`sprint deps`, y al planificar, iniciar, lanzar y
cerrar). Condición: `cerrado` (el sprint remoto está en su `archive/`) o `activo` (está en su
`current/`; también se cumple si ya está cerrado). Estado: `decidido (usuario, AAAA-MM-DD)` bloquea
la activación si no se cumple; `propuesto` sólo avisa. Cada proyecto declara sólo sus dependencias
de entrada; las de salida se deducen leyendo los `DEPENDENCIAS.md` de los demás.

Regla del laboratorio (usuario, 2026-11-07): el sprint N del laboratorio es «lo que se puede hacer cuando termine el
sprint N de `quantdesk`», salvo SPRINT-01, que es lo que se puede hacer ya (sin dependencias de entrada).

**Enmienda (usuario, 2026-11-13, revisión de planes, R1):** desde SPRINT-03, el sprint N+1 del laboratorio corresponde
al sprint N de `quantdesk` (SPRINT-04 ← quantdesk SPRINT-03, SPRINT-05 ← quantdesk SPRINT-04). SPRINT-03 se rehízo con
sólo lo que no depende de `quantdesk` y no tiene dependencia de entrada; su contenido anterior pasó a SPRINT-04 y el
antiguo SPRINT-04 (escalera de entrenamiento) se renumeró a SPRINT-05. La regla del 2026-11-07 de arriba se conserva
como histórico (SPRINT-02 ya se había partido el 2026-11-11 sin dependencia de entrada).

## Proyectos relacionados

| Proyecto | Ruta |
|---|---|
| quantdesk | S:/projects/quantdesk |
| quantdesk-backend | S:/projects/quantdesk-backend |
| quantdesk-network | S:/projects/quantdesk-network |
| quantlab | S:/Projects/quantlab |

## Dependencias de entrada

SPRINT-02 no tiene dependencia de entrada desde el 2026-11-11: el usuario lo partió para activarlo sin esperar a
quantdesk SPRINT-02, y las filas que la necesitaban (antes «SPRINT-02 ← quantdesk SPRINT-02 cerrado», decidido el
2026-11-07) pasaron a SPRINT-03 como filas S02-1…S02-4 (hoy en SPRINT-04, ver abajo).

**SPRINT-03 no tiene dependencia de entrada desde el 2026-11-13** (usuario, 2026-11-13, revisión de planes, R1): se
rehízo con sólo lo que no depende de `quantdesk` (TI-02-DIARIO, S02-5, S02-6 con la sonda, INTRA-LOCAL, operación del
publicador MT5, universo ampliado condicionado, consumo FRED/OAS) para poder activarlo ya. Su dependencia anterior
(«SPRINT-03 ← quantdesk SPRINT-03 cerrado», decidida el 2026-11-07 y ampliada el 2026-11-11) pasó, con su contenido, a
SPRINT-04; el antiguo SPRINT-04 es SPRINT-05.

| Sprint local | Depende de | Condición | Motivo | Estado |
|---|---|---|---|---|
| SPRINT-04 (contenido del antiguo SPRINT-03) | quantdesk SPRINT-03 | cerrado | TI-03-FMT, TI-00-ADR, TS-01-SIM, TS-02-GEN (para TS-02-DISC), DL-02-GATES; y, desde el 2026-11-11, las filas S02-1…S02-4 (rueda E-RELEASE-WF, E15-filter, FG-16-hmmcop, universo59), que necesitan quantdesk SPRINT-02 cerrado (lo cubre el cierre de su SPRINT-03) | decidido (usuario, 2026-11-07 para SPRINT-03; ampliado 2026-11-11; trasladado a SPRINT-04 por R1, usuario, 2026-11-13, revisión de planes) |
| SPRINT-05 (antes SPRINT-04) | quantdesk SPRINT-04 | cerrado | DL-07-TRAIN, TI-06-CLI, TI-14-REG, TS-05-PREC (escalera de entrenamiento); intradía de MT5 en qn para TS-05-FREQ (R7) | decidido (usuario, 2026-11-07; renumerado por R1, usuario, 2026-11-13, revisión de planes) |

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
| TI-09-ARCH (backlog; fuera de SPRINT-01 desde 2026-11-08), captura al cierre con spot | quantdesk-backend SPRINT-02 OC-03-CLOSE (que espera a quantdesk-network SPRINT-01 OCS-01, ya cerrada) | Hasta entonces se archiva la última captura de cada día, **sin spot de respaldo** (se quita el «subyacente del OHLCV diario»; sólo `underlying_price` de OC-03: usuario, 2026-11-10, revisión de planes, D11) | decidido (usuario, 2026-11-07; enmendado 2026-11-10); **servida (2026-11-13)**: OC-03 desplegada en `cc1811d`, primer cierre completo `2026-11-12-163125-5b2305`; el lector usa `capture_id` y `underlying_price` (parte de laboratorio entregada en SPRINT-02; medición = SPRINT-03 fila 3) |
| TI-09-ARCH (backlog), aviso en origen | quantdesk-backend SPRINT-01 OC-01-FAIL, OC-02-ALERT | Fallos y huecos detectados en origen el mismo día | decidido (usuario, 2026-11-07); **servida** (2026-11-08/09) |
| TI-09-ARCH (backlog), lectura bajo demanda | quantdesk-network SPRINT-01 OCS-01, OCS-02 | Garantía de S3 sin retención en los topics `market.*` de los scrapers (decisión 12-A): el laboratorio lee del lago y no copia a diario | decidido (usuario, 2026-11-07); **servida** (2026-11-08). **Garantía rota** por la herramienta genérica de borrado en el lago (usuario, 2026-11-09). Sin copia propia: la copia es la común de network (`PLAN_COPIA_PERIODICA_LAGO`) y el laboratorio sólo guarda lo leído al cortar cada dataset, con hash; `lake delete` no se usa sobre `market.*` hasta que exista (usuario, 2026-11-10, revisión de planes, D7; PLAN_ARCHIVO_OPCIONES §4) |
| TI-09-ARCH (backlog), universo | quantdesk-backend (sin sprint) 5–10 ETF/índices en la captura, en OC-03 o tarea al lado | Subyacentes con `asset_type` ETF/INDEX en el lector y el informe de huecos | decidido (usuario, 2026-11-09); **servida (2026-11-13)**: siete obligatorios dentro de OC-03 (backend `04cc60f`, `5723017`) |
| TI-13-PUB ampliación (ex SPRINT-02 fila 7, devuelta al backlog el 2026-11-13) y TI-02-DATA ampliada | quantdesk-backend (backlog, sin sprint) `PLAN_PUBLICADORES_MERCADO_PUBLICO` | Las fuentes públicas (Yahoo/Stooq, FRED, cripto) entran al lago sólo por publicadores del backend (A16 bis); el laboratorio las consume vía qn. **Desde el 2026-11-13 el consumo se divide** (R6): FRED/OAS en la fila de abajo (SPRINT-03); Yahoo/Stooq y cripto quedan en el backlog hasta que alguien planifique su publicación (PUB-03/PUB-04 sin sprint) | decidido (usuario, 2026-11-09; dividido, usuario, 2026-11-13, revisión de planes, R6) |
| TI-13-PUB-FRED (SPRINT-03 fila 6, consumo de FRED/OAS) | quantdesk-backend SPRINT-03 (`next/SPRINT.md`), PUB-00…PUB-02 (topic de GAP-PUB-01) | Exportar con TI-02-DATA lo que publique de FRED y OAS; no bloquea la activación de SPRINT-03, sólo el inicio de la fila | decidido (usuario, 2026-11-13, revisión de planes, R6) |
| TI-02-DIARIO (SPRINT-03 filas 1 y 2; el laboratorio escribe el código, el backend lo programa en Dagster) | quantdesk-backend SPRINT-03 (`next/SPRINT.md`; antes citado como `future/SPRINT-03`), PUB-05-EXPORT (programación tras el cierre de Nueva York); quantdesk, formatos de D-I4 | Exportador diario de D-I4: escribe desde qn el mercado del día y los datasets que `quantdesk` abre; debe existir antes de la ola 1 de SPRINT-03 de `quantdesk`. **Contrato decidido (usuario, 2026-11-14)**, en [contrato-propuesta.md](current/execution/TI-02-DIARIO/contrato-propuesta.md):<br>- tarea de Windows registrada por el backend (A2), con sensor de frescura sobre `ops.export.status`;<br>- OHLCV en `desktop.daily-ohlcv/v1` y `engine.market-history/v1`; los JSON siguen con `quantdesk`;<br>- credencial `sub:market.ohlcv.v2` + `pub:ops.export.status`.<br>El código va **sin OAS** en la fila 2 | decidido (usuario, 2026-11-09; dueño decidido por el usuario el 2026-11-10, revisión de planes, D5 y D6; calendario, usuario, 2026-11-13, R5; **contrato, usuario, 2026-11-14**) |
| TI-02-DIARIO, despliegue (SPRINT-03 fila 2) | quantdesk-network: registrar `ops.export.status` y emitir el token del exportador; quantdesk-backend: tarea de Windows y sensor (PUB-05-EXPORT) | Sin topic ni token, el código se puede escribir y aceptar con qn falso, pero no se despliega ni se vigila; no bloquea la activación | decidido (usuario, 2026-11-14) |
| TI-02-DIARIO-OAS (SPRINT-03 fila 7) | quantdesk-backend SPRINT-03, PUB-01/PUB-02 (OAS en qn) | Añadir los OAS al exportador cuando el backend los publique; no bloquea la activación | decidido (usuario, 2026-11-13, revisión de planes, R5) |
| ~~TI-12-MT5-SYNC (fuera de sprint; carga nocturna de `@continuo`)~~ **cerrada** | quantdesk-network (excepción al horizonte de revisión de qn si venció) y aviso a quantdesk-backend | Republicar las 23 velas 1d del 2026-11-09 y aplazar la carga de `@continuo` hasta cerrar [ISSUE-TI12-MT5-SYNC](archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md). **Cerrada el 2026-11-13** (usuario, 2026-11-13, revisión de planes, R3): ficha resuelta y archivada; network respondió que el horizonte no aplica (`f660654`). La carga de `@continuo` pasa a SPRINT-03 fila 4c, con la dependencia de la fila siguiente | decidido (usuario, 2026-11-10, revisión de planes, D1); cerrada (R3) |
| TI-12-MT5-OPS y TI-12-MT5-PUB-AMP (SPRINT-03 filas 4c y 5) | quantdesk-network (visto bueno de carga: ritmo, memoria de mini) y aviso a quantdesk-backend (Bento) | Noche de `@continuo` (4c) y acciones (5, condicionada a visto bueno **nuevo** de network y aprobación del usuario, GAP-DATOS_VIA_QN-08); ≤ 40 000 objetos por 5 min, 02:00–05:00 CET. Además, ambas esperan al desbloqueo de la cuenta MT5 (usuario) | decidido (usuario, 2026-11-13, revisión de planes, R3; GAP-DATOS_VIA_QN-08 diferido como fila condicionada) |
| S02-5 / TI-12-MT5-INTRA-LOCAL / TI-12-MT5-OPS / TI-12-MT5-PUB-AMP (SPRINT-03 filas 4a, 4b, 4c y 5) | quantlab SPRINT-01 (QL-10: h1 de `@continuo`, fila 4a; descargas grandes tras el 2026-11-18) y SPRINT-02 (4b, 4c con el traspaso del publicador y el 1d en qn con carga nocturna, 5, y retirada del código de descarga MT5 de este repo); plan `S:/Projects/quantlab/docs/plans/next/PLAN_SERVICIO_DATOS.md` (`871b112`) | quantlab es el único que descarga histórico de MT5 (usuario, 2026-11-14; SKILL.md §0); entrega en `E:/quantlab` con nuestro formato (manifest `engine.market-history/v1`, procedencia y SHA-256), peticiones en `E:/quantlab/peticiones/entrada/` | propuesto (decisiones del usuario del 2026-11-14 retransmitidas por `quantlab-f0`) |
