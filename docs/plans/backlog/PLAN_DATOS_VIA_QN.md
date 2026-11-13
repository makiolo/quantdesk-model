# Plan — Datos de mercado vía qn (MT5, publicadores públicos, exportadores)

> **Origen:** división de [backlog/README.md](README.md) (regla de publicadores de §1, filas TI-12-MT5 y TI-13-PUB de
> §2.2, filas TI-12-MT5 y TI-13-PUB de §4), en la versión del árbol revisada el 2026-11-09 sobre el commit `8a849c6`.
> División decidida por el usuario el 2026-11-09 (revisión de planes, GAP-BACKLOG_README-06 opción (a)). Texto de la
> especificación copiado íntegro; lo nuevo va marcado «(usuario, 2026-11-09)».

**Estado:** backlog. Lo que ya está en un sprint del laboratorio se especifica allí; aquí queda su estado, lo que no
tiene sprint y lo que espera a otros proyectos. **Fecha:** 2026-11-09; **puesto al día el 2026-11-10** (revisión
parcial, sección final): TI-12-MT5 está CERRADA y SPRINT-01 archivado
(`../archive/SPRINT-01_2026-11-07_2026-11-09/`); el dossier de TI-12-MT5 ya no está en `current/execution/` sino en
`../archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/`. **Decisiones del usuario del 2026-11-10 aplicadas
(revisión de planes, D1, D2, D3, D3b, D6):** ficha urgente [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md) (cerrada el 2026-11-13, R3);
TI-02-DATA-V2 en SPRINT-02 (fila 1b de [current/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md)); incremental de MT5 en INTRA-LOCAL; dueño
de TI-02-DIARIO. Sección final «Decisiones del usuario (2026-11-10)».

> **Al cierre de SPRINT-02 (2026-11-13, decisiones del usuario):** TI-02-DATA-V2 **CERRADA** (fila 1b; código
> `3e35ed5`, tabla FX sobre MT5 en `f0995d0`+`d6bc45d`). TI-12-MT5 (más símbolos y periodos, alcance h1 de `@continuo`)
> **arrastrada a SPRINT-03** como S02-5, a la espera del desbloqueo de la cuenta MT5. **TI-13-PUB (consumir lo que
> publique el backend) vuelve aquí, al backlog:** salió sin hacer porque el backend no publica nada propio en qn hasta
> su SPRINT-03 (`PLAN_PUBLICADORES_MERCADO_PUBLICO`); se mete en un sprint cuando publique. Cierre en
> [archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md#9-cierre-2026-11-13).

> **Revisión del 2026-11-13 (antes de planificar SPRINT-03; sección final «Revisión de planes (2026-11-13)»):**
> - **TI-02-DATA-V2 está HECHA y verificada en el código** (`descarga_lago.py:64-65` `TOPICS_DEFECTO = (TOPIC_OHLCV,)`,
>   `POLITICA_FUENTES` en `:67`, aserción de selftest en `:627`; `fuentes.py:191` rechaza v1; informe en
>   `../archive/SPRINT-02_2026-11-11_2026-11-13/execution/TI-02-DATA-V2/informe.md`). Sale del pendiente.
> - **El publicador MT5 no publica nada desde el 2026-11-10:** la tarea `quantdesk\publicador_mt5` está registrada y «Ready»
>   (`schtasks`, 2026-11-13; próxima 23:30) y todas sus ejecuciones desde las 22:35 UTC del 2026-11-10 salen
>   `bloqueado: initialize(...) fallo (-6, 'Terminal: Authorization failed')`, 0 series
>   (`E:/quantdesk-lab/runs/TI-12-MT5/publicador/publicador_2026-11-1{1,2,3}.jsonl`). La última publicación real fue la
>   republicación del 2026-11-10 ~09:35 UTC; el 1d de MT5 en qn termina, para fx28, en la vela del 2026-11-09 (la de los
>   días 10 a 13 la rellenará el publicador al desbloquearse la cuenta). Esto contradice «queda desactivada» de
>   [ISSUE-TI12-MT5-VELA-A-MEDIAS](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md) (C-DATOS_VIA_QN-05).
> - **TI-12-MT5-SYNC: criterios 1 a 5 cumplidos** (`2ac3f8f`, `9e2a9eb`, `b9cbbbe`, `f660654`, `d6d7a55`); queda lo
>   operativo (carga nocturna de `@continuo` aplazada, tarea, documentación).
> - **TI-02-DIARIO sigue sin una línea de código** y su plazo (antes de la ola 1 de SPRINT-03 de `quantdesk`) choca con la
>   puerta de entrada de SPRINT-03 del laboratorio (C-DATOS_VIA_QN-06). El backend ya tiene su SPRINT-03 en `next/`
>   (no en `future/`), «En planificación».

> **Decisiones del usuario del 2026-11-13 aplicadas** (usuario, 2026-11-13, revisión de planes, R1–R8; sección final
> «Decisiones del usuario (2026-11-13, revisión de planes)»): el SPRINT-03 del laboratorio se rehízo **sin dependencia de
> entrada** ([next/SPRINT.md](../current/SPRINT.md)) y recoge de este plan: TI-02-DIARIO (fila 1 contrato, primera; fila 2
> código sin OAS; fila 7 OAS; R5), la fila 4 de MT5 (4a S02-5, 4b INTRA-LOCAL, 4c reactivación del publicador y carga
> nocturna de `@continuo`; R2, R3, R8), el resto del universo ampliado en qn como fila 5 condicionada (GAP-DATOS_VIA_QN-08)
> y el consumo de FRED/OAS como fila 6 (R6). La tarea programada del publicador está **desactivada** desde el 2026-11-13
> (R2). ISSUE-TI12-MT5-SYNC está **cerrada** (R3). El intradía en qn va con SPRINT-05 (R7). Yahoo/Stooq y cripto siguen en
> el backlog (R6, §3).

## 1. Regla (A16 y A16 bis, usuario, 2026-11-09)

Los datos de mercado entran al lago de `quantdesk-network` (qn) **solo por publicadores**, uno por restricción
tecnológica. MT5, que sólo funciona en Windows, publica desde el Windows del laboratorio (`scripts/publicador_mt5.py`,
topic `market.ohlcv.v2`); las fuentes públicas de mercado (Yahoo/Stooq, FRED, cripto) van en `quantdesk-backend` como
jobs de Dagster en Linux. **El laboratorio consume siempre vía qn** y exporta a `engine.market-history/v1`. Los corpus
genéricos de preentrenamiento (Chronos, LOTSA) no son datos de mercado en vivo y siguen siendo ingesta directa del
laboratorio. El laboratorio no escribe en el backend ni en network: lo que necesite de ellos es una dependencia externa
que lleva el usuario o una sesión de ese proyecto.

Excepciones decididas el 2026-11-09:

- **Binance ya ingerido** (TI-13-PUB, `7ea6d94`): corpus congelado con hash, como Chronos y LOTSA (§5).
- **MT5 intradía 1m y 5m**: se guarda en local ya, sin publicar; se publica en qn al planificar SPRINT-04 (§2). *(Desde
  el 2026-11-13 ese sprint de entrenamiento es SPRINT-05: usuario, 2026-11-13, revisión de planes, R1 y R7.)*

## 2. MT5 (TI-12-MT5)

| ID | Qué se hace aquí | Cuándo / estado (2026-11-09) | Notas |
|---|---|---|---|
| **TI-12-MT5** (fase C) | Universo ampliado en 1d: continuo (forex 60, metales y energía 16, índices 23, cripto 94) y acciones US grandes (`@us_grandes`, S&P 500: 484 de sesión normal y 13 sólo `-24` = 497); universos con nombre, vela 1d por clase, huecos por clase y ritmo de publicación | **CÓDIGO Y DESCARGAS LOCALES CERRADOS** con SPRINT-01 (2026-11-09; commits hasta `f9dcd0c` y cuadre `fdfa3a7`). Descargas locales 1d: continuo (193 series, 547 226 filas, `E:/quantdesk-lab/data/mt5/continuo_1d_20261109`, `sha256:a503bb75…`), 484 acciones (`us_grandes_1d_20261109`, `sha256:6d9e0528…`) y 13 `-24` (`us_grandes24_1d_20261109`, `sha256:1e58cb0a…`). **Publicar en qn el universo ampliado: lo que queda de esta fila.** Plan nocturno acordado con backend y network (2026-11-09, backend `EXECUTION.md`): ≤ 40 000 objetos por 5 min, 02:00–05:00 CET; noche 1 continuo (~369 000 objetos, ~46 min), noches 2 y 3 acciones (~690 000 cada una, ~1 h 30 min); avisan al empezar y paran si el cursor del Bento se retrasa. **Noche 1 (programada a las 02:03 del 2026-11-10) APLAZADA** por el aviso de la vela incompleta (ver TI-12-MT5-SYNC) **hasta cerrar [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md)** (usuario, 2026-11-10, revisión de planes, D1); noche 2 espera a network y al usuario (cierre de SPRINT-01, §10). **Estado 2026-11-13: sigue VIGENTE y aplazada, sin sprint.** Las condiciones que la ficha SYNC ponía (criterios 1–5) ya se cumplen; lo que falta es (a) el desbloqueo de la cuenta MT5 (el publicador ni siquiera abre sesión: `Authorization failed`), (b) el visto bueno de network y el aviso al backend **de nuevo** (el del 2026-11-09 era para la noche del 2026-11-10, que no salió; no consta uno vigente) y (c) la aprobación del usuario noche a noche. La revisión del token `ti12mt5-publicacion-20261109` («al cerrar SPRINT-01») sigue vencida y sin constancia. Ver GAP-DATOS_VIA_QN-08. **Decisión (usuario, 2026-11-13, revisión de planes, R3 y GAP-DATOS_VIA_QN-08 diferido):** la noche 1 (`@continuo`) va en SPRINT-03 fila 4c (TI-12-MT5-OPS, con aviso a backend y network) y las noches 2–3 (acciones) en la fila 5 (TI-12-MT5-PUB-AMP), **condicionada** a desbloqueo + visto bueno nuevo de network + aprobación del usuario; la revisión del token id 36 entra en 4c | Detalle en `../archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/fase-c.md`. **Meta Platforms resuelto (usuario, 2026-11-09): entra con su `-24`** (`META.NAS-24`, clase `acciones_us_24`). Solapa con los publicadores públicos del backend en acciones US y cripto (GAP-BACKLOG_README-03). Sustituye la cifra anterior de «~180 000 objetos por sondeo de 5 min» (tope del Bento sin lotes) por el tope acordado de 40 000 |
| **TI-12-MT5-SYNC** (nueva, 2026-11-10; **CERRADA el 2026-11-13**, R3) | Evitar y corregir la vela 1d publicada incompleta: el 2026-11-09 la vela 1d de MT5, publicada a las 23:01 UTC, salió incompleta en 23 de 28 pares de fx28 porque la historia D1 del terminal no estaba sincronizada (EURUSD salió bien). (1) El publicador publica un símbolo y periodo sólo con la historia sincronizada; (2) republicar las 23 velas del 2026-11-09 con el valor correcto | **Ya, fuera de sprint** (aviso del laboratorio al backend ~23:45 UTC del 2026-11-09; backend `e90eb03`). **Ficha [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md)** (decisión D1, usuario, 2026-11-10, revisión de planes: «republicar y aplazar»; GAP-DATOS_VIA_QN-03 resuelto; **resuelta y archivada el 2026-11-13**, R3). Relacionada con [ISSUE-TI12-MT5-VELA-A-MEDIAS](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md) (fusionada en SYNC), que registra la guarda de historia ya escrita y la tarea programada desactivada por el bloqueo de la cuenta | **Aceptación** (detalle en la ficha): (1) selftest con un MT5 falso que devuelve el D1 parcial («Call failed» o menos barras que el 1m agregado): 0 publicadas y aviso, no velas; (2) **modo de reenvío** de velas ya publicadas; (3) **se aprueban las 23 republicaciones** de las velas 1d de FX del 2026-11-09 y, tras ellas, `scripts/cuadre_mt5.py --m1 --d1` da 0 puntos de diferencia en las 28 velas; (4) la revisión llega a qn y a ClickHouse; (5) se verifica el horizonte de revisión de qn (hipótesis H2 del backend, ~6 h) y, si ya venció, la ficha pide la excepción a network; (6) la carga nocturna de `@continuo` sigue aplazada hasta cerrar la ficha. ~~Hoy no hay camino de republicación (lo añade el criterio 2): `nucleo.py::serie` cuenta `revisiones_detectadas` pero sólo publica `huecos + ts > ultimo`~~ (texto histórico del 2026-11-10). **Estado 2026-11-13 (comprobado con git y con los registros de `E:/quantdesk-lab/runs/TI-12-MT5/publicador/`): HECHOS 1, 2, 3, 4 y 5.** (1) guarda de historia `2ac3f8f` (`prueba_guarda_historia`); (2) `--republicar-revisiones` y `--pausa-serie-s` `9e2a9eb`; (3) 23 velas republicadas el 2026-11-10 (23 publicadas, 5 sin revisión, 0 errores; verificadas 28/28 en qn, `b9cbbbe`); (4) ClickHouse y API verificados por el backend (`d6d7a55`, backend `9d63c68`); (5) network: `QN_BARS_REVISION_HORIZON_MS` no aplica a `market.ohlcv.v2` (`f660654`). **Quedan 6, 7 y 8:** la carga nocturna de `@continuo` sigue aplazada (es la fila «publicar el universo ampliado», sin sprint); la tarea programada **ya está registrada y activa, pero falla** (ver arriba), así que el criterio 7 («reactivar la tarea y primera pasada sin revisiones nuevas») sólo se puede comprobar tras el desbloqueo de la cuenta; y la documentación. El selftest del publicador no se reejecutó en esta revisión (SIN VERIFICAR: sin ejecutar scripts). **Cierre (usuario, 2026-11-13, revisión de planes, R3):** ficha cerrada fusionando VELA-A-MEDIAS; la verificación 28/28 en qn y ClickHouse sustituye al cuadre de 0 puntos (criterio 3, GAP-ISSUES-02 aceptado); el criterio 6 (carga de `@continuo`) y el 7 (reactivar la tarea y primera pasada limpia) pasan a SPRINT-03 fila 4c; el 8 (documentación) queda hecho con esta actualización (C-DATOS_VIA_QN-08 y C-ISSUES-02 resueltas por regla). Archivo: `../archive/FUERA-SPRINT_2026-11-09_2026-11-13/` |
| **TI-12-MT5** (intradía) | 1h, 5m, 1m (y ticks si hay) del publicador MT5 en `market.ohlcv.v2` | **Backlog, condicionada** (usuario, 2026-11-09: «Solo 1d»). No se lanza sin el visto bueno previo de `quantdesk-network` (ritmo, memoria de mini ~2,17 de 3 GiB, ~9 500 particiones diarias ya creadas por el 1d) y aviso al backend (cada republicación completa ~1,4 GiB y ~4 min de CPU en mini). **Decisión (usuario, 2026-11-09): guardar 1m y 5m en local ya, con hash; la publicación en qn se pide al planificar SPRINT-04 del laboratorio** (GAP-BACKLOG_README-04 resuelto). **Se mantiene (usuario, 2026-11-13, revisión de planes, R7):** se planifica con el sprint de entrenamiento, que desde la partición es **SPRINT-05**; no entra en SPRINT-03 (GAP-DATOS_VIA_QN-10 resuelto) | El código ya lo soporta (`--intervalos`); `--simular` real dio 1h 2,80 M, 5m 0,17 M, 1m 0,83 M barras en fx28 (m1 sólo desde 2025-11 por `maxbars`). Consumidor: TS-05-FREQ (SPRINT-04 del laboratorio); ver GAP-TSFM-04 de PLAN_TSFM_FINANZAS |
| **TI-12-MT5-INTRA-LOCAL** (usuario, 2026-11-09) | Descarga local periódica de 1m y 5m del universo que el bróker sirva (como mínimo fx28), con el extractor de sólo lectura (`scripts/extractor_mt5.py`), a `E:/quantdesk-lab/data/mt5/`, **sin publicar en qn** | **Ya, fuera de sprint** (historia irrecuperable: el bróker sólo da ~100 000 barras y m1 llega hoy sólo a 2025-11). Ficha viva: [ISSUE-TI12-MT5-INTRADIA-LOCAL](../current/issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md). **Primera descarga hecha (2026-11-09 18:33 CET):** `@continuo` completo (193 símbolos), m1 y m5, 386 series, 37 944 660 filas, 1246,7 MiB en `E:/quantdesk-lab/data/mt5/continuo_m1m5_20261109`, `hash_conjunto sha256:5cd9bf8691bd9d0c5dd5cb0b7328631fb69d52491acc65ddc2b1cdc324e2f9cf`; m1 llega a 2026-08-04 (mediana) y 2025-11-05 (la más antigua); m5 a 2025-07-08 y 2021-11-10. Según la ficha, el manifiesto (criterio 3) está en la carpeta y nada se publicó (criterio 5); criterio 1 sólo en fx28 (`fdfa3a7`); **2 y 4 pendientes**: no hay descarga incremental ni tarea que la repita. **El incremental reanudable se hace ya, fuera de sprint, en esta ficha** y la fila 5 de `next/SPRINT.md` se reduce a «más símbolos y periodos» (D3, usuario, 2026-11-10, revisión de planes; C-DATOS_VIA_QN-03 resuelta). Las acciones (`@us_grandes`) no están en el alcance descargado: **se mide su profundidad y volumen m1/m5 con `--simular` y se incluyen si la cifra es razonable** (presupuesto 100 GB), anotado en la ficha (D3b; GAP-DATOS_VIA_QN-04 resuelto) | **Aceptación:** (1) dos descargas del mismo rango dan el mismo SHA-256; (2) la descarga es reanudable y la siguiente sólo añade barras nuevas (sin huecos entre la última barra guardada y la primera nueva, salvo fines de semana y festivos del bróker); (3) manifiesto con símbolo, periodo, primera y última barra, filas y hash; (4) periodicidad que no pierda barras por `maxbars` (para m1, menos de ~100 000 barras entre descargas: unas 13 semanas en FX y metales de lunes a viernes, 1440 barras al día, y unas 9,9 semanas en cripto 24/7; **recomendada: mensual**, con margen para un fallo); (5) nada se publica en qn ni se envía ninguna orden. Contradice «consume vía qn» sólo en el almacenamiento, no en el consumo: TS-05-FREQ leerá de qn cuando se publique. **Estado 2026-11-13 (revisión):** el **incremental ya está en el código** (`scripts/extractor_mt5_lib/descarga.py`, docstring y `obtener_trozo`: caché de trozos cerrados en `<data>/_trozos/…`, una descarga posterior con otro `hasta` reutiliza los trozos y sólo pide los nuevos; `--refrescar` los repite; trozo = mes en m1/m5, año en h1/d1) y la caché de la primera descarga existe en `E:/quantdesk-lab/data/mt5/_trozos`: lo que falta no es código sino **ejecutarlo y repetirlo** (criterio 2 sin prueba real; criterio 1 sobre `@continuo` completo; criterio 4 sin tarea; criterio 6, la medición de acciones, sin hacer). No hay segunda descarga desde el 2026-11-09 y **ninguna puede hacerse hasta que el bróker desbloquee la cuenta** (el extractor usa el mismo terminal). **Plazo real, cálculo propio de la revisión (SIN VERIFICAR contra el bróker):** con ~100 000 barras de m1, la barra más reciente guardada el 2026-11-09 sale del alcance del bróker a las ~9,9 semanas en cripto 24/7 (~2027-01-17) y a las ~13 semanas en FX y metales de lunes a viernes (~2027-02-08); dentro de ese plazo no debería perderse ninguna barra entre la última guardada y la primera nueva (la profundidad antigua ya está en la caché). La etiqueta «urgente» de la ficha se mantiene por la cuenta bloqueada, no por una fecha inminente. Se fusiona operativamente con la fila S02-5 de SPRINT-03 (mismo extractor, mismo terminal, mismo mutex). **Decisión (usuario, 2026-11-13, revisión de planes, R8):** alcance **fx28 y `@continuo` primero**, después las **484 acciones de `@us_grandes`** (≈ 3,1 GiB; medir con `extractor_mt5.py --inventario --grupo @us_grandes`, no con `--simular`, que es del publicador: C-ISSUES-03 por regla), una serie cada vez; pasadas **manuales cada ≤ 6 semanas**, la primera **antes del 2027-01-17**; **sin tarea programada** (sustituye la «recomendada: mensual» del criterio 4; GAP-ISSUES-04 y D3b resueltos). SPRINT-03 fila 4b, fusionada con S02-5 (4a); espera al desbloqueo. C-DATOS_VIA_QN-09 resuelta por regla (el incremental ya existe en el extractor) |
| **TI-12-MT5** (tarea programada) | Registrar `scripts/publicador_mt5_tarea.xml` en el Programador de tareas (~~cada 15 min~~ una vez al día a las 23:30 hora local desde `1fff755`, y al iniciar sesión; `--intervalos 1d`, relleno de huecos desde lo que qn confirma) | **DESACTIVADA desde el 2026-11-13** por la raíz de guardia (~23:55 local, `schtasks /Change /DISABLE`, estado verificado «Disabled») hasta el desbloqueo de la cuenta MT5; se reactiva en SPRINT-03 fila 4c (usuario, 2026-11-13, revisión de planes, R2; GAP-DATOS_VIA_QN-05 resuelto; C-DATOS_VIA_QN-05 resuelta por regla). Backend avisado del FX 1d de MT5 parado desde el 2026-11-10. *Texto de la revisión, antes de R2:* **HECHO, pero hoy ACTIVA Y FALLANDO (2026-11-13):** `schtasks /query` la da «Ready», con disparo diario a las 23:30 hora local (`1fff755`) y al iniciar sesión; ver arriba el resultado de cada ejecución (`Authorization failed`, 0 series, desde el 2026-11-10 22:35 UTC). Original: **HECHO** (puerta de usuario cumplida): el usuario registró la tarea `quantdesk\publicador_mt5` para el 1d de fx28 (cierre de SPRINT-01, §10; `run_scheduler.cmd` `4cd1237` la registra de forma idempotente; la primera publicación real fue `9b74bed`). Verificado el 2026-11-13 que la tarea sigue registrada y activa (`schtasks`). La publicación de las 23:01 UTC del 2026-11-09 con velas incompletas (TI-12-MT5-SYNC) fue de esta tarea: el registro `publicador_2026-11-09.jsonl` tiene ejecuciones a las 23:00, 23:15, 23:30 y 23:45 UTC (cada 15 min, el disparo de entonces) | Token de larga vida `ti12mt5-publicacion-20261109` (id 36, `pub:`/`sub:` sobre `market.ohlcv.v2`, `env=main`) en `E:/quantdesk-lab/secrets/qn-mt5.token`; **la revisión «al cerrar SPRINT-01» está vencida y sin constancia** (el cierre no la menciona): pendiente de la raíz o del usuario; entra en SPRINT-03 fila 4c |

Opciones descartadas para el intradía (usuario, 2026-11-09): pedirlo sólo al planificar SPRINT-04 sin guardar nada
(se pierde profundidad m1 cada mes); publicar ya a ritmo bajo (más carga en mini).

## 3. Datos públicos de mercado (TI-13-PUB) — movidos al backend

| ID | Qué se hace aquí | Cuándo / estado (2026-11-09) | Notas |
|---|---|---|---|
| **TI-13-PUB** (datos públicos de mercado) | Yahoo/Stooq (miles de tickers diarios), FRED y cripto con histórico completo, leídos de qn | **MOVIDO a `quantdesk-backend`** (publicadores Dagster, A16 bis). **Decisión (usuario, 2026-11-09): plan nuevo en el backend, `PLAN_PUBLICADORES_MERCADO_PUBLICO`**, con FRED común con la fuente USD de F1 de `PLAN_FUENTES_OFICIALES_CURVAS` (GAP-FOC-06) y una tarea OAS para XVA; lo escribe el aplicador del backend (GAP-BACKLOG_README-02 resuelto) | Aquí queda sólo el consumo: exportar con TI-02-DATA lo que llegue al lago. La ampliación «más tickers y cripto» de [current/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md) fila 7 pasa a «consumir y exportar lo que publique el backend» (C-BACKLOG_README-03 / C-10 resuelta). El filtro de fugas D-11 se aplica también a estas series. **Estado 2026-11-13 (comprobado en el backend):** sigue sin haber nada que consumir. `PLAN_PUBLICADORES_MERCADO_PUBLICO` está en el backlog del backend; su SPRINT-03 está en `next/` («En planificación», sin fecha, tras el SPRINT-02 del backend, aún activo) y sólo lleva PUB-00, PUB-01 (publicación de FRED), PUB-02 (OAS) y la programación del exportador; **PUB-03 (Yahoo/Stooq) y PUB-04 (cripto) están explícitamente fuera de ese sprint y sin sprint** (GAP-PUB-04 y GAP-PUB-08 abiertos). La captura de FRED/OAS del backend (FOC-F1-5, primera captura real el 2026-11-11) va a su `app_db`, no a qn. Por tanto TI-13-PUB (consumo) se **divide**: la parte FRED/OAS será consumible cuando el backend cierre su SPRINT-03; la parte Yahoo/Stooq y cripto no tiene fecha y sigue en el backlog. Cuando haya publicadores en qn, el backend avisa a la raíz del laboratorio (aviso de salida de su SPRINT-03) |

**División del consumo (usuario, 2026-11-13, revisión de planes, R6; dentro de este plan, sin plan nuevo).** La fila de
arriba conserva la especificación común (consumo vía qn, exportación con TI-02-DATA, filtro de fugas D-11); su ejecución
se reparte en dos IDs:

| ID | Qué se hace aquí | Aceptación | Sprint / estado |
|---|---|---|---|
| **TI-13-PUB-FRED** (consumo de FRED/OAS) | Exportar con TI-02-DATA lo que el backend publique en qn de FRED (H.15) y de OAS (uso interno); filtro de fugas D-11 sobre esas series; licencias en la tabla (FRED: atribución; ICE: uso interno) | Informe del filtro actualizado; datasets con hash exportados desde qn y reproducibles; licencias anotadas; el dataset con OAS no sale del equipo del usuario | **SPRINT-03, fila 6** ([next/SPRINT.md](../current/SPRINT.md)), con **dependencia de tarea** del SPRINT-03 del backend (PUB-00…PUB-02; topic de GAP-PUB-01): no bloquea la activación, sólo el inicio de la fila. Nivel L4 |
| **TI-13-PUB** (consumo de Yahoo/Stooq y cripto) | Exportar con TI-02-DATA lo que el backend publique de Yahoo/Stooq (miles de tickers diarios) y de cripto | Mismas garantías de hash, look-ahead y filtro D-11; regla de fuentes versionada antes de mezclar con MT5 (GAP-DATOS_VIA_QN-09) | **Backlog** hasta que alguien planifique su publicación (backend PUB-03/PUB-04 sin sprint; GAP-PUB-04 y GAP-PUB-08 abiertos). Se avisa al backend de la discrepancia entre nuestro EXECUTION de SPRINT-02 (mensaje del 2026-11-11: «Yahoo/Stooq, FRED, cripto y OAS en su SPRINT-03») y su `next/SPRINT.md` (sólo FRED y OAS) (C-BACKLOG_README-09; lo hace la raíz) |

Opciones descartadas (usuario, 2026-11-09): raíl nuevo en SPRINT-02 del backend; ingesta directa provisional del
laboratorio.

## 4. Exportadores

| ID | Qué se hace | Aceptación | Estado |
|---|---|---|---|
| **TI-02-DATA-V2** (usuario, 2026-11-09) — **HECHA (2026-11-13)** | `scripts/descarga_lago.py` lee **sólo** `market.ohlcv.v2` (~~hoy `TOPICS_DEFECTO` en la línea 57 lee `market.ohlcv`, v1~~; ahora `descarga_lago.py:65` `TOPICS_DEFECTO = (TOPIC_OHLCV,)` con `TOPIC_OHLCV = "market.ohlcv.v2"`, y el CLI rechaza v1 en `:991`); quita v1 de los topics por defecto y del código | (1) Un dataset nuevo con corte posterior al 2026-11-09 contiene las barras de v2 de esas fechas (no se congela en silencio); (2) selftest en verde con un caso que falla si el topic por defecto vuelve a v1; (3) mismas garantías de hash y look-ahead de TI-02-DATA; (4) el informe dice que los cuatro datasets de TI-02-DATA (`binance_c20261101`, `lago_c20261101`, `lago_cierre_c20261101`, `lago_c20261107`) **se regeneran desde la versión anterior del script en git** (`git show 0e67465:scripts/descarga_lago.py`, último commit que lee v1), no desde el nuevo; **(5, nuevo 2026-11-10) selección por `source`**: v2 trae el tag `source` (`mt5`, `market_scraper`, y `yahoo`/`stooq`/exchange cuando el backend publique), cada combinación de etiquetas es un fichero distinto y `exportar_market_history_lib/fuentes.py:230` toma `instrument = symbol` sin mirar `source`, así que dos fuentes del mismo símbolo e intervalo se mezclarían o chocarían; el exportador (y el volcado) elige la fuente por clase y falla si una (símbolo, intervalo, ts) llega de dos fuentes sin regla; **(6) FX diario sólo con `source=mt5`** (criterio 3 de [ISSUE-LAGO-FX-1D-CLOSE](../archive/SPRINT-02_2026-11-11_2026-11-13/issues/ISSUE-LAGO-FX-1D-CLOSE.md)): un corte nuevo del lago con ese filtro cuadra con `scripts/cuadre_mt5.py`; el 1d de yfinance (`market_scraper`) tiene el close del inicio del día y no se corrige en el lago; **(7)** `lago_cierre_c20261101` se regenera sólo para reproducir el hash y el informe lo marca como afectado por esa incidencia | **En SPRINT-02, fila 1b de [current/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md)** (con la repetición de la tabla FX sobre el 1d de MT5, en dos tablas; usuario, 2026-11-10, revisión de planes, D2 y D15; GAP-DATOS_VIA_QN-02 y C-DATOS_VIA_QN-01 resueltos). **Es la condición previa de los criterios 1–3 de ISSUE-LAGO-FX-1D-CLOSE** y de las filas 2, 4 y 7 de `next/SPRINT.md`, que ahora la declaran. Resuelve **C-12** y la urgencia **U5** de la revisión (exportaciones congeladas en silencio). Opciones descartadas: v2 por defecto con v1 para reproducir hashes; selección a mano. **CERRADA 2026-11-13** (SPRINT-02 fila 1b; A4 ACEPTAR en A y C; cierre `778d0e3`). Evidencia por criterio: (1) `prueba_corte_v2_posterior_migracion` (barras del 9 y 10 de noviembre con corte 12); (2) `descarga_lago.py:627` `assert TOPICS_DEFECTO == ('market.ohlcv.v2',)` y mutación ejecutada (`default_mutacion.log`); (3) mismos hashes y 0 violaciones; (4) los cuatro datasets regenerados desde `0e67465` con hash idéntico (`regeneracion.json`, informe); (5) `POLITICA_FUENTES` (`descarga_lago.py:67`, versión `ti-02-data.fuentes/v1`, el exportador la importa) y una única fuente por `(symbol, interval)` sin regla; (6) FX + `interval=1d` sólo `source=mt5` y cuadre 1459/1459 con `cuadre_mt5.py` (volcado en mini, `fb11457`); (7) `lago_cierre_c20261101` marcado afectado en el informe. Datasets MT5: `sha256:a5015bc9…893da` (cabecera) y `sha256:47d79b39…67d32` (ampliación). Rutas en `../archive/SPRINT-02_2026-11-11_2026-11-13/execution/TI-02-DATA-V2/` y `TS-00-BENCH-MT5/`. **Consecuencia que queda abierta:** la política «una sola fuente por (símbolo, intervalo) sin regla» hace fallar el exportador en cuanto el backend publique Yahoo/Stooq o cripto de un exchange para símbolos que MT5 ya publica (acciones US, cripto): hará falta una regla versionada por clase (GAP-DATOS_VIA_QN-09, heredado de GAP-BACKLOG_README-03) |
| **TI-02-DIARIO** (D-I4, usuario, 2026-11-09) | **Exportador diario** que escribe desde qn el mercado del día y los datasets que `quantdesk` ya abre (incluidos los OAS para XVA), para que el motor no dependa de qn ni use tokens | (1) Cada día hábil deja en la ruta que abre `quantdesk` el mercado del día y los datasets con hash; (2) un día sin datos en qn produce un aviso, no un fichero vacío; (3) `quantdesk` no importa ningún cliente de qn ni lee tokens; **(4, nuevo 2026-11-10)** el FX diario sale con `source=mt5` (como TI-02-DATA-V2 (6)), y el job corre después de la publicación nocturna de MT5 (la vela 1d de MT5 sólo se publica tras el cierre de Nueva York, 17:00 NY, y el día en curso no aparece hasta entonces: backend `ISSUE-FX-1D-CLOSE-YFINANCE`); un día sin vela de MT5 es aviso, no se rellena con yfinance; **(5–9, añadidos en la revisión del 2026-11-13 para hacerlos ejecutables; (6) y (7) son condiciones del backend `PLAN_PUBLICADORES_MERCADO_PUBLICO` §4 ya aceptadas por el laboratorio)** (5) `--selftest` con qn falso: un día sin barras produce un aviso registrado y ningún fichero vacío; (6) no exporta la vela 1d del día en curso ni una marcada incompleta (guarda análoga a `2ac3f8f`); (7) el dataset con OAS no sale del equipo del usuario (uso interno de ICE); (8) mismo corte y mismas entradas → mismo SHA-256 (regla de TI-02-DATA) y 0 violaciones de look-ahead por `data_py`; (9) un `grep` de `quantdesk` no encuentra cliente de qn ni lectura de tokens (cierra el criterio 3 con una prueba). **Sin fijar y bloqueante para el código:** la ruta que abre `quantdesk`, los formatos que debe escribir (quantdesk pide `engine.market-history/v1` **y** `desktop.daily-ohlcv/v1`, `PLAN_TSFM_INTEGRACION` §6 D-I4; el laboratorio no tiene ningún escritor de `desktop.daily-ohlcv/v1`: `rg` sin resultados en `scripts/`) y dónde corre el job (GAP-DATOS_VIA_QN-06) | Backlog; **sin una línea de código a 2026-11-13**. **Dueño (usuario, 2026-11-10, revisión de planes, D6; GAP-DATOS_VIA_QN-01 resuelto): el laboratorio escribe el código** (reutiliza `exportar_market_history_lib`, hashes y reglas sin look-ahead) **y el backend lo programa en Dagster después del cierre de Nueva York** (cuando MT5 publica el 1d), en su SPRINT-03 (D5: `quantdesk-backend/docs/plans/future/SPRINT-03/SPRINT.md`, junto con PUB-00, PUB-01 y PUB-02). Debe existir antes de la ola 1 de SPRINT-03 de `quantdesk` (decisión «Publicador OAS ya», usuario, 2026-11-09). Resuelve D-I4 (GAP-TSFM_INTEGRACION-04): descartado que `quantdesk` lea qn directamente. **Estado 2026-11-13 (revisión):** (a) el SPRINT-03 del backend está en `quantdesk-backend/docs/plans/next/SPRINT.md` (no en `future/`), «En planificación», tras el SPRINT-02 del backend (activo); su fila PUB-05-EXPORT depende del código de esta tarea («sprint del laboratorio por asignar», propuesto); (b) las piezas del laboratorio ya existen y son reutilizables (`descarga_lago.py` con selección por fuente, `exportar_market_history_lib`, hashes), pero el exportador **depende de `data_py` de la rueda `quantdesk` cp312 de Windows** (`exportar_market_history_lib/validacion.py:80`) y escribe en `E:/quantdesk-lab/` (`exportar_market_history.py:33`), mientras que Dagster corre en Linux; el volcado de qn ya se hizo en mini con la biblioteca estándar (1b-B) pero la exportación no (C-DATOS_VIA_QN-07); (c) los OAS no existen en qn hasta PUB-02 (backend SPRINT-03), así que el exportador se puede entregar y aceptar **sin OAS** y añadir los OAS después; (d) el FX con `source=mt5` está parado en la vela del 2026-11-09 mientras la cuenta esté bloqueada, es decir, cada día sale como aviso; (e) **plazo duro: antes de la ola 1 de SPRINT-03 de `quantdesk`**, y el SPRINT-03 del laboratorio sólo se activa cuando `quantdesk` cierre ese SPRINT-03 (C-DATOS_VIA_QN-06). **Decisión (usuario, 2026-11-13, revisión de planes, R5; con R1):** TI-02-DIARIO es la **primera fila del SPRINT-03 nuevo**, que no tiene dependencia de entrada: fila 1, acordar el **contrato** con el backend por mensaje (dónde corre, ruta, formatos incluido `desktop.daily-ohlcv/v1`, series OAS, credencial) y registrarlo en GOBERNANZA y DEPENDENCIAS; fila 2, el **código sin OAS** en el mismo sprint (criterios (1)–(6), (8), (9)); fila 7 (TI-02-DIARIO-OAS), los OAS y el criterio (7) cuando el backend los publique (dependencia de tarea de su SPRINT-03). Debe llegar antes de la ola 1 de quantdesk SPRINT-03. El bloque «Sin fijar y bloqueante» de la aceptación lo cierra el contrato (GAP-DATOS_VIA_QN-06 y -07 resueltos así; C-DATOS_VIA_QN-06 y -07 resueltas por R1 y R5); el **contenido del contrato sigue pendiente de acordar** |

## 5. Binance ingerido directamente (C-09 / C-BACKLOG_README-02)

**Decisión (usuario, 2026-11-09): corpus congelado con hash**, excepción a A16 bis como Chronos y LOTSA. El dataset
`binance_c20261101` (TI-13-PUB `7ea6d94`, segunda tabla de TS-00-BENCH `baa4ee6`) no se rehace; lo nuevo de cripto
llegará por qn cuando exista el publicador del backend. Opciones descartadas: rehacerlo desde qn (cambian hashes y la
tabla del banco); retirar Binance del banco.

## 6. Dependencias externas (2026-11-09)

| Tarea local | Depende de | Estado | Mientras tanto |
|---|---|---|---|
| TI-12-MT5 fase C (publicar en qn) e intradía (publicar) | visto bueno de `quantdesk-network` (ritmo, compactación) y aviso a `quantdesk-backend` (carga del Bento) | fase C: **plan nocturno acordado con backend** (≤ 40 000 objetos/5 min, 02:00–05:00 CET; noche 1 continuo aplazada; noche 2 espera a network y al usuario); intradía: se pide al planificar SPRINT-04 del laboratorio (usuario, 2026-11-09). **2026-11-13:** noche 1 = SPRINT-03 fila 4c (R3); noches 2–3 = fila 5, condicionada a visto bueno nuevo de network y aprobación del usuario (GAP-DATOS_VIA_QN-08); intradía con SPRINT-05 (R7) | descarga local en `E:/quantdesk-lab/data/mt5/` (TI-12-MT5-INTRA-LOCAL para 1m y 5m) |
| TI-13-PUB (mercado público) y TI-02-DATA ampliada (ex fila 7 de SPRINT-02, devuelta al backlog el 2026-11-13; S02-4 de SPRINT-03 para «nuevas fuentes») | `quantdesk-backend` `PLAN_PUBLICADORES_MERCADO_PUBLICO` (backlog; su SPRINT-03 en `next/` lleva sólo PUB-00…PUB-02 y la programación del exportador; PUB-03/PUB-04 sin sprint) | decidido (usuario, 2026-11-09) | Binance congelado de TI-13-PUB; FX diario de qn **sólo `source=mt5`** (el 1d de yfinance tiene el close desfasado: ISSUE-LAGO-FX-1D-CLOSE) |
| TI-02-DATA-V2 (lectura de `market.ohlcv.v2` con selección por `source`) | ninguna externa; es **condición previa** de ISSUE-LAGO-FX-1D-CLOSE y de las filas 2, 4 y 7 de `next/SPRINT.md` | **HECHA** (SPRINT-02, fila 1b, cerrada 2026-11-13; usuario, 2026-11-10, D2) | ~~`descarga_lago.py` lee v1~~ (ya lee sólo v2) |
| TI-02-DIARIO | backend: programación en Dagster tras el cierre de NY (SPRINT-03 del backend, D5); OAS del publicador del backend | mecanismo (usuario, 2026-11-09) y dueño (usuario, 2026-11-10, D6): el laboratorio escribe, el backend programa. **2026-11-13:** el SPRINT-03 del backend está en `next/SPRINT.md` (en planificación; backend SPRINT-02 activo); `quantdesk` SPRINT-03 ola 1 lo espera. **SPRINT-03 del laboratorio, filas 1, 2 y 7** (usuario, 2026-11-13, revisión de planes, R5): contrato por mensaje (fila 1) y código sin OAS (fila 2) sin dependencia de sprint; OAS (fila 7) con dependencia de tarea de PUB-01/PUB-02 | Desarrollar el código sin OAS y sin la programación (parte del laboratorio, sin dependencia externa salvo el contrato); el FX con `source=mt5` sale como aviso mientras la cuenta esté bloqueada |
| ~~TI-12-MT5-SYNC (republicación y carga de `@continuo`)~~ **cerrada el 2026-11-13 (R3)**; la carga de `@continuo` es SPRINT-03 fila 4c | ~~visto bueno de network para el horizonte de revisión de qn (si venció)~~ (network, 2026-11-10: no aplica a `market.ohlcv.v2`, `f660654`); aviso al backend y visto bueno de network para la carga | [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md), D1 (usuario, 2026-11-10); criterios 1–5 cumplidos; cerrada (R3) | la carga de `@continuo` sigue aplazada: cuenta MT5 bloqueada, aviso vigente a network y backend, aprobación del usuario |
| TI-12-MT5 (h1 de `@continuo`, S02-5) y TI-12-MT5-INTRA-LOCAL (incremental m1/m5, medición de acciones) | **Desbloqueo de la cuenta MT5 por el bróker (usuario)**; mutex del terminal (una tarea a la vez, una serie cada vez) | cuenta bloqueada desde el 2026-11-10 por descargas agresivas; el publicador del 2026-11-13 20:52 UTC (al iniciar sesión) aún recibe `Authorization failed`; tarea del publicador desactivada desde el 2026-11-13 (R2). **SPRINT-03 fila 4** (4a S02-5, 4b INTRA-LOCAL, 4c publicador; R8, R2, R3) | nada que hacer salvo preparar la orden y el calendario; plazo sin pérdida de m1: ~2027-01-17 en cripto y ~2027-02-08 en FX (cálculo propio) |
| TI-13-PUB-FRED (consumo de FRED/OAS) | backend SPRINT-03 (PUB-00…PUB-02, GAP-PUB-01 topic): dependencia de tarea | `next/SPRINT.md` del backend, en planificación. **SPRINT-03 del laboratorio, fila 6** (usuario, 2026-11-13, revisión de planes, R6) | nada; no hay datos en qn |
| TI-13-PUB consumo de Yahoo/Stooq y cripto | backend PUB-03/PUB-04 (sin sprint; GAP-PUB-04 y GAP-PUB-08 abiertos) | backlog del backend; **backlog del laboratorio** hasta que alguien planifique su publicación (R6) | Binance congelado (§5); FX diario `source=mt5` |

Filas en [DEPENDENCIAS.md](../DEPENDENCIAS.md) «Dependencias de tarea».

## 7. GAPs abiertos

- **GAP-BACKLOG_README-03 — Acciones US y cripto por dos publicadores** (abierto, sin prisa: la publicación del universo
  ampliado sigue bloqueada por el visto bueno de network). ¿Referencia del laboratorio por clase de activo, o las dos
  fuentes con su `source`? Opciones: (a) MT5 en FX, metales e índices; Yahoo/Stooq en acciones; cripto de un solo
  origen; (b) las dos fuentes con `source`; (c) sólo MT5. Recomendación: (a), con un subconjunto pequeño duplicado para
  el cuadre. (2026-11-10: el cuadre del FX ya demostró su valor: cruzar yfinance y MT5 destapó el close desfasado de
  yfinance; apoya la opción (a) con duplicado de control.)
- ~~**GAP-DATOS_VIA_QN-01 — Dueño del exportador diario (TI-02-DIARIO)**~~ **RESUELTO (usuario, 2026-11-10, revisión de
  planes, D6):** el laboratorio escribe el código (TI-02-DIARIO) y el backend lo programa en Dagster tras el cierre de
  Nueva York, en su SPRINT-03 (D5). Texto histórico (abierto, nuevo el 2026-11-09): Laboratorio
  (Windows, ya tiene `descarga_lago.py` y el exportador) o backend (Dagster en Linux, junto al publicador OAS). Debe
  decidirse antes de planificar la ola 1 de SPRINT-03 de `quantdesk`. (2026-11-10: sigue abierto en los tres repos:
  GAP-PUB-02 del backend y `quantdesk/docs/plans/DEPENDENCIAS.md`, que exige tarea OAS y exportador cerrados en un
  backend o laboratorio antes de la ola 1; el criterio nuevo (4) de TI-02-DIARIO, FX con `source=mt5`, no cambia la
  disyuntiva.)
- ~~**GAP-DATOS_VIA_QN-02 — TI-02-DATA-V2 como condición previa de SPRINT-02**~~ **RESUELTO (usuario, 2026-11-10,
  revisión de planes, D2):** fila nueva 1b en `next/SPRINT.md` con TI-02-DATA-V2 y la repetición de la tabla FX sobre
  MT5, antes de las filas 2, 4 y 7. Texto histórico (abierto, nuevo el 2026-11-10): La incidencia
  ISSUE-LAGO-FX-1D-CLOSE (destino SPRINT-02) pide repetir la tabla FX del banco sobre el 1d de MT5 «desde qn», y
  `descarga_lago.py` sólo lee v1, que ya no recibe barras. Detalle y opciones en el informe de la revisión.
- ~~**GAP-DATOS_VIA_QN-03 — Republicar las 23 velas 1d del 2026-11-09 y mantener el aplazamiento de la carga nocturna**~~
  **RESUELTO (usuario, 2026-11-10, revisión de planes, D1):** «republicar y aplazar». Ficha urgente
  [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md); se aprueban las 23 republicaciones; la carga nocturna de
  `@continuo` sigue aplazada hasta cerrarla; se verifica el horizonte de revisión de qn y, si venció, se pide la
  excepción a network. Texto histórico (abierto, nuevo el 2026-11-10): decisión de usuario (backend e90eb03: «si el
  usuario lo aprueba»).
- ~~**GAP-DATOS_VIA_QN-04 — Alcance del intradía local**~~ **RESUELTO (usuario, 2026-11-10, revisión de planes, D3b):**
  medir profundidad y volumen m1/m5 de las 484 acciones de `@us_grandes` con `--simular` e incluirlas en INTRA-LOCAL si
  la cifra es razonable (presupuesto 100 GB); se anota en la ficha. Texto histórico (abierto, nuevo el 2026-11-10). La primera descarga m1/m5 cubre
  `@continuo` (193); las 497 acciones de `@us_grandes` no tienen intradía local; si el bróker les aplica el mismo tope de ~100 000 barras, su profundidad también se pierde
  (SIN VERIFICAR: no se ha medido el intradía de acciones).
- ~~**GAP-DATOS_VIA_QN-05 — Tarea programada activa con la cuenta bloqueada (nuevo, 2026-11-13).**~~ **RESUELTO (usuario,
  2026-11-13, revisión de planes, R2):** desactivada por la raíz de guardia el 2026-11-13 hasta el desbloqueo; se reactiva
  en SPRINT-03 fila 4c. Texto histórico: ¿La desactiva el usuario
  hasta el desbloqueo? Hoy dispara a las 23:30 y al iniciar sesión, y cada intento es un login fallido contra el bróker
  que ya bloqueó la cuenta por exceso de peticiones.
- ~~**GAP-DATOS_VIA_QN-06 — TI-02-DIARIO: dónde corre y qué escribe (nuevo, 2026-11-13).**~~ **RESUELTO (usuario, 2026-11-13,
  revisión de planes, R5):** lo resuelve el contrato con el backend, primera fila de SPRINT-03 (las opciones del informe
  quedan como base de la negociación; el contenido sigue **pendiente de acordar**). Texto histórico: ¿Corre en Windows (el laboratorio,
  con su rueda cp312) o en Linux dentro de Dagster (hace falta rueda Linux o prescindir de `data_py`)? ¿Qué formatos y qué
  ruta abre `quantdesk` (`engine.market-history/v1` y/o `desktop.daily-ohlcv/v1`)?
- ~~**GAP-DATOS_VIA_QN-07 — Calendario de TI-02-DIARIO (nuevo, 2026-11-13).**~~ **RESUELTO (usuario, 2026-11-13, revisión de
  planes, R1 y R5):** partir SPRINT-03; TI-02-DIARIO es su primera fila y debe llegar antes de la ola 1 de quantdesk
  SPRINT-03. Texto histórico: El plazo es «antes de la ola 1 de SPRINT-03 de
  `quantdesk`» y el SPRINT-03 del laboratorio sólo se activa al cerrar el de `quantdesk` (C-DATOS_VIA_QN-06): ¿fuera de
  sprint como INTRA-LOCAL, fila de SPRINT-03 sin la puerta, o partir SPRINT-03?
- **GAP-DATOS_VIA_QN-08 — Reanudar la publicación del universo ampliado (nuevo, 2026-11-13).** **Diferido** (sin pregunta
  en la revisión; se pregunta al planificar la fila): fila condicionada en SPRINT-03 (fila 5, acciones) a desbloqueo +
  visto bueno nuevo de network + aprobación del usuario; la noche 1 (`@continuo`) y la revisión del token van en la fila 4c
  por R3. Texto: Con SYNC 1–5 cumplidos y la
  cuenta bloqueada: ¿quién pide a network y backend el visto bueno nuevo, cuándo se reanudan las noches 1–3 y se revisa el
  token `ti12mt5-publicacion-20261109`?
- **GAP-DATOS_VIA_QN-09 — Política de fuentes cuando haya dos (heredado de GAP-BACKLOG_README-03, 2026-11-13).** **Abierto,
  diferido** (= GAP-BACKLOG_README-03; dos publicadores, sin sprint). El
  exportador falla con dos fuentes sin regla (`POLITICA_FUENTES` v1): hay que decidir la regla por clase (acciones US,
  cripto) antes de consumir PUB-03/PUB-04 o publicar las acciones de MT5.
- ~~**GAP-DATOS_VIA_QN-10 — Intradía MT5 en qn en SPRINT-03 (nuevo, 2026-11-13).**~~ **RESUELTO (usuario, 2026-11-13,
  revisión de planes, R7):** se mantiene la decisión del 2026-11-09; se planifica con el sprint de entrenamiento (SPRINT-05),
  consumidor TS-05-FREQ; no entra en SPRINT-03. Texto histórico: El usuario pidió meter todo el backlog en
  SPRINT-03; la decisión vigente (2026-11-09) lo pide al planificar SPRINT-04 y exige visto bueno de network: ¿se adelanta?

### Decisiones del usuario (2026-11-10, revisión de planes)

Fuente de todas: usuario, 2026-11-10, revisión de planes.

| Decisión | Resuelve | Efecto en este plan |
|---|---|---|
| D1 «Republicar y aplazar» | GAP-DATOS_VIA_QN-03, C-DATOS_VIA_QN-02 | Ficha urgente [ISSUE-TI12-MT5-SYNC](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/ISSUE-TI12-MT5-SYNC.md); modo de reenvío; se aprueban las 23 republicaciones; carga de `@continuo` aplazada hasta cerrarla; verificar el horizonte de revisión de qn (H2, ~6 h) y pedir excepción a network si venció |
| D2 | GAP-DATOS_VIA_QN-02, C-DATOS_VIA_QN-01 | TI-02-DATA-V2 y la repetición de la tabla FX en la fila 1b de `next/SPRINT.md` (SPRINT-02) |
| D3 | C-DATOS_VIA_QN-03 | Incremental de MT5 fuera de sprint en INTRA-LOCAL; la fila 5 de `next/SPRINT.md` queda en «más símbolos y periodos» |
| D3b | GAP-DATOS_VIA_QN-04 | Medir con `--simular` las 484 acciones de `@us_grandes` y decidir con la cifra (presupuesto 100 GB), anotado en la ficha INTRA-LOCAL |
| D6 | GAP-DATOS_VIA_QN-01 | TI-02-DIARIO: el laboratorio escribe el código; el backend lo programa en Dagster tras el cierre de NY, en su SPRINT-03 (D5) |
| Por regla | C-DATOS_VIA_QN-04 | Los derivados del laboratorio (`backlog/README.md`, `index.md`, `issues/index.md`) se ponen al día tras el cierre de SPRINT-01 |

Contradicciones C-DATOS_VIA_QN-01 a -04: todas resueltas. GAPs abiertos que quedan relacionados con este plan:
GAP-BACKLOG_README-03 (dos publicadores en acciones US y cripto; aquí GAP-DATOS_VIA_QN-09).

## Revisión de planes (2026-11-13)

Veredicto: **ACTUALIZAR + DIVIDIR en «MT5 y exportadores» (este plan, sin TI-02-DATA-V2, que sale a hecha) y «TI-13-PUB
consumo» (FRED/OAS, que espera al SPRINT-03 del backend, y Yahoo/Stooq/cripto, sin sprint)**; TI-02-DATA-V2 → **BORRAR del
pendiente** (HECHA; la especificación se conserva en §4 como constancia) · Motivo: lo único realmente nuevo desde el
2026-11-10 es que TI-02-DATA-V2 se cerró, que la cuenta MT5 está bloqueada y que el publicador y la tarea programada fallan
a diario, que TI-12-MT5-SYNC está cumplida salvo lo operativo y que TI-02-DIARIO no tiene código ni dueño de calendario.
Sin cambios de dirección: A16, A16 bis y las decisiones D1–D6 siguen. (Sustituye la tabla de clasificación de la revisión
parcial del 2026-11-10, que queda en git; se conservan sus decisiones del usuario, más abajo.)

| Tarea | Clasificación | Evidencia / motivo | ¿Lista para SPRINT-03? (nivel, dependencias, puerta) |
|---|---|---|---|
| TI-12-MT5 fase C: código y descargas locales 1d | HECHO | SPRINT-01 §10; `f9dcd0c`, `fdfa3a7`, `beaf81c`; `E:/quantdesk-lab/data/mt5/{continuo_1d,us_grandes_1d,us_grandes24_1d}_20261109` existen | No entra (hecha) |
| TI-12-MT5 fase C: publicar el universo ampliado en qn (noches 1–3) | VIGENTE (aplazada, **sin fila en ningún sprint**) | SYNC 1–5 cumplidos; el publicador no abre sesión (`Authorization failed` desde el 2026-11-10); no consta visto bueno vigente de network ni aviso al backend; token de larga vida con revisión vencida | **Sí, como fila condicionada**, L5. Puertas de usuario: desbloqueo de la cuenta, aprobación de cada noche, token. Depende de visto bueno de network y aviso al backend (otros proyectos) |
| TI-12-MT5-SYNC | MODIFICADO (criterios 1–5 HECHOS; 6–8 operativos) | `2ac3f8f`, `9e2a9eb`, `b9cbbbe`, `f660654`, `d6d7a55`; ficha SYNC sin marcar y a fusionar con VELA-A-MEDIAS | **Cierre administrativo L3**, no hay código; FUSIONAR las dos fichas al cerrar. Criterio 7 depende del desbloqueo |
| TI-12-MT5 intradía publicado en qn | VIGENTE (sin cambios) | Decisión del 2026-11-09: al planificar SPRINT-04; condición de network | **No sin decisión del usuario** (GAP-DATOS_VIA_QN-10) |
| TI-12-MT5-INTRA-LOCAL | MODIFICADO | Incremental ya en `extractor_mt5_lib/descarga.py` (caché de trozos); falta ejecutarlo, medir acciones (criterio 6) y fijar periodicidad; sin segunda descarga desde el 2026-11-09 | **Sí**, L5, fusionada operativamente con S02-5. Depende del desbloqueo (puerta de usuario) y del mutex del terminal; la tarea mensual la registra el usuario |
| TI-12-MT5 más símbolos y periodos (S02-5) | VIGENTE | Alcance fijado 2026-11-11: h1 de `@continuo`, sin símbolos nuevos; sin código nuevo previsto (el extractor ya admite h1); sin empezar | **Sí**, L6 (el nivel de SPRINT-01 no baja), con la misma puerta de desbloqueo |
| TI-12-MT5 tarea programada | HECHO (registrada) pero ACTIVA Y FALLANDO | `schtasks`: Ready, próxima 23:30; `publicador_2026-11-1{1,2,3}.jsonl` con `Authorization failed` | No es fila: es una decisión del usuario (GAP-DATOS_VIA_QN-05); verificar el criterio 7 de SYNC tras el desbloqueo |
| TI-13-PUB corpus genéricos (Chronos, LOTSA, Binance) | HECHO | `7ea6d94`; `E:/quantdesk-lab/datasets/TI-13-PUB/` existe; Binance congelado (§5) | No entra (hecha). La tabla de licencias al ADR es la fila 2 de `next/SPRINT.md` |
| TI-13-PUB consumo de FRED/OAS | VIGENTE, no lista | Backend: PUB-00…PUB-02 en su SPRINT-03 (`next/`, en planificación); captura FOC-F1-5 va a su `app_db`, no a qn | Sí como fila **diferida** a «backend SPRINT-03 cerrado» (que, por orden formal, precede a quantdesk SPRINT-03 y por tanto al del laboratorio), L4; OAS: uso interno |
| TI-13-PUB consumo de Yahoo/Stooq y cripto | VIGENTE, sin fecha | Backend PUB-03/PUB-04 sin sprint; GAP-PUB-04 y GAP-PUB-08 abiertos | **No** puede entrar: nada se publica. Necesita GAP-DATOS_VIA_QN-09 |
| TI-02-DATA-V2 | HECHO | `27cfb2b`…`3e35ed5`, `f0995d0`+`d6bc45d`, cierre `778d0e3`; `descarga_lago.py:65,67,627,991`; `fuentes.py:191`; informe y `regeneracion.json`; cuadre 1459/1459 | No entra (hecha). Quitar de las filas pendientes |
| TI-02-DIARIO | VIGENTE (sin código; criterios 5–9 añadidos) | Ver §4; `rg desktop.daily-ohlcv` sin resultados en el laboratorio; exportador depende de `data_py` Windows y de rutas `E:/` | **Sí, L6**, sin dependencia de `quantdesk` pero con C-DATOS_VIA_QN-06 (puerta de entrada) y GAP-DATOS_VIA_QN-06/-07; parte OAS (L4) después de PUB-02 |
| Binance congelado (§5) | VIGENTE | Decisión del usuario del 2026-11-09 | No es tarea |

GAPs al redactar la revisión: GAP-DATOS_VIA_QN-05 (tarea programada con la cuenta bloqueada) · GAP-DATOS_VIA_QN-06 (dónde corre
TI-02-DIARIO y qué formatos escribe) · GAP-DATOS_VIA_QN-07 (calendario de TI-02-DIARIO frente a la puerta de SPRINT-03) ·
GAP-DATOS_VIA_QN-08 (reanudar la publicación del universo ampliado, visto bueno y token) · GAP-DATOS_VIA_QN-09 (política de
fuentes con dos publicadores; heredado de GAP-BACKLOG_README-03) · GAP-DATOS_VIA_QN-10 (intradía MT5 en qn en SPRINT-03).
**Tras las decisiones del 2026-11-13:** -05 (R2), -06 (R5), -07 (R1, R5) y -10 (R7) resueltos; -08 y -09 abiertos,
diferidos (§7).

Contradicciones registradas (detalle en el informe de la revisión; **todas resueltas el 2026-11-13**: -05, -08 y -09 por
regla; -06 por R1 y R5; -07 por R5, el contrato):
- **C-DATOS_VIA_QN-05** — la ficha VELA-A-MEDIAS (2026-11-10) dice que la tarea «queda desactivada» hasta el fin del
  bloqueo; `schtasks` (2026-11-13) la da registrada y «Ready», y falla cada día.
- **C-DATOS_VIA_QN-06** — TI-02-DIARIO debe estar «antes de la ola 1 de SPRINT-03 de `quantdesk`»
  (`quantdesk/docs/plans/DEPENDENCIAS.md`) y el SPRINT-03 del laboratorio entra «cuando `quantdesk` SPRINT-03 cierre»
  (`DEPENDENCIAS.md` del laboratorio): la tarea no puede estar en ese sprint y cumplir su plazo.
- **C-DATOS_VIA_QN-07** — «el backend sólo lo programa» (D6) frente a un exportador atado a la rueda Windows y a `E:/`, y
  quantdesk espera también `desktop.daily-ohlcv/v1`, que el laboratorio no escribe.
- **C-DATOS_VIA_QN-08** — la ficha ISSUE-TI12-MT5-SYNC tiene los 8 criterios sin marcar mientras su cabecera y VELA-A-MEDIAS
  acreditan los criterios 1 a 5 con commits.
- **C-DATOS_VIA_QN-09** — INTRA-LOCAL dice «no hay descarga incremental» (criterio 2) y el extractor ya la tiene (caché de
  trozos); y la etiqueta «urgente» no casa con el plazo calculado (≥ ~2027-01-17).

Sinergias: backend `PLAN_PUBLICADORES_MERCADO_PUBLICO` (PUB-05-EXPORT programa lo que escribe TI-02-DIARIO; aviso de salida
a la raíz del laboratorio cuando haya publicadores) y su `ISSUE-FX-1D-CLOSE-YFINANCE`; quantdesk `PLAN_XVA_BANCARIO`
(XVA-03-DATA, OAS por TI-02-DIARIO) y `PLAN_TSFM_INTEGRACION` D-I4; network `PLAN_COPIA_PERIODICA_LAGO` (respaldo del lago, D7)
y `RETENCION.md` (visto bueno de carga); TS-05-FREQ (SPRINT-04) como consumidor del intradía; la fila 1 de `next/SPRINT.md`
(re-exportación con procedencia TI-03-FMT) deberá incluir los dos datasets MT5 de TI-02-DATA-V2 (desde la partición del
2026-11-13 es la fila 1 de §3 de [SPRINT-04](../next/SPRINT.md)).

### Decisiones del usuario (2026-11-13, revisión de planes)

Fuente de todas: usuario, 2026-11-13, revisión de planes (registro en [REVISIONES.md](REVISIONES.md)). La división se
aplica **dentro de este plan** (§3, IDs TI-13-PUB-FRED y TI-13-PUB Yahoo/Stooq/cripto), sin plan nuevo.

| Decisión | Resuelve | Efecto en este plan |
|---|---|---|
| R1 Partir SPRINT-03 | GAP-DATOS_VIA_QN-07 (con R5), C-DATOS_VIA_QN-06 (con R5) | SPRINT-03 del laboratorio sin dependencia de entrada: TI-02-DIARIO, fila de MT5, universo ampliado condicionado y FRED/OAS entran en él |
| R2 Publicador desactivado | GAP-DATOS_VIA_QN-05, C-DATOS_VIA_QN-05 (por regla) | Tarea `quantdesk\publicador_mt5` desactivada desde el 2026-11-13; se reactiva en SPRINT-03 fila 4c |
| R3 Cerrar SYNC | C-DATOS_VIA_QN-08 (por regla) | TI-12-MT5-SYNC cerrada fusionando VELA-A-MEDIAS (archivo `FUERA-SPRINT_2026-11-09_2026-11-13`); reactivación y carga nocturna de `@continuo` en la fila 4c |
| R5 TI-02-DIARIO | GAP-DATOS_VIA_QN-06, -07; C-DATOS_VIA_QN-06, -07 | Contrato (fila 1, primera), código sin OAS (fila 2), OAS (fila 7, dependencia de tarea del backend) |
| R6 TI-13-PUB | (C-BACKLOG_README-09) | Consumo dividido en §3: FRED/OAS en SPRINT-03 fila 6; Yahoo/Stooq y cripto en el backlog |
| R7 Intradía en qn | GAP-DATOS_VIA_QN-10 | Con el sprint de entrenamiento (SPRINT-05); no entra en SPRINT-03 |
| R8 INTRA-LOCAL | (D3b, periodicidad), C-DATOS_VIA_QN-09 (por regla) | fx28 y `@continuo`, después 484 acciones; manual cada ≤ 6 semanas, primera antes del 2027-01-17; sin tarea programada; fila 4b |
| Diferidos | GAP-DATOS_VIA_QN-08, GAP-DATOS_VIA_QN-09 (= GAP-BACKLOG_README-03) | -08: fila 5 condicionada a desbloqueo + visto bueno nuevo de network + aprobación del usuario; -09: sin sprint |

GAPs abiertos que quedan: GAP-DATOS_VIA_QN-08 y GAP-DATOS_VIA_QN-09 (diferidos). Contradicciones abiertas: ninguna.
