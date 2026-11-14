# SPRINT-03 — Exportador diario, operación de MT5 y cobertura de cadenas (sin esperar a quantdesk)

**Estado:** Activo
**Inicio de planificación:** 2026-11-13
**Inicio:** 2026-11-14
**Fin:** pendiente

> **Activado el 2026-11-14** (usuario, 2026-11-14, «vale» a planificar e iniciar SPRINT-03 empezando por la fila 1).
> Lo activa la raíz de guardia `quantdesk-model-4d`, que pasa a ser la raíz inicial (skill `sprint`, `guardia.md`
> «Paso a sprint»). `deps.py --sprint SPRINT-03`: LISTO, 0 dependencias de entrada. Dossier movido de `next/` a
> `current/`; `future/SPRINT-04` promovido a `next/`. Registro de ejecución: [EXECUTION.md](EXECUTION.md); lanzamiento y
> relevos: [LAUNCH.md](LAUNCH.md).

> **Rehecho por partición** (usuario, 2026-11-13, revisión de planes, R1; precedente: partición de SPRINT-02 del
> 2026-11-11). Este SPRINT-03 sólo tiene lo que **no depende de `quantdesk`** y por eso **no tiene dependencia de
> entrada de sprint**: se puede activar ya. El contenido anterior de `next/SPRINT.md` («Ciclo sintético-real y
> procedencia en el manifiesto»: filas S02-1…S02-4 con su tabla de entregas, objetivo, entregas de quantdesk SPRINT-03,
> tareas de §3, dependencia, exclusiones, orden, DoD y capacidad) pasó **íntegro** a
> [SPRINT-04](../next/SPRINT.md), que espera a quantdesk SPRINT-03 cerrado; el sprint de
> entrenamiento que era `future/SPRINT-04` es ahora [future/SPRINT-05](../future/SPRINT-05/SPRINT.md). Las filas S02-5 y
> S02-6, arrastradas de SPRINT-02 el 2026-11-13, se quedan aquí con su etiqueta.
>
> Petición del usuario (usuario, 2026-11-13, revisión de planes, R0): meter en el sprint siguiente S02-5, S02-6, todos
> los planes del backlog y todas las issues pendientes. Se cumple así: lo que no depende de `quantdesk` entra aquí; lo
> que sí, en SPRINT-04; el intradía de MT5 en qn, con el sprint de entrenamiento (SPRINT-05, R7); el consumo de
> Yahoo/Stooq y cripto queda en el backlog hasta que alguien planifique su publicación (R6).
>
> El `next/SPRINT.md` de `quantdesk-backend` (línea 59) espera TI-02-DIARIO en «sprint del laboratorio por asignar»:
> ahora es **SPRINT-03** (filas 1 y 2). Se le avisa por mensaje (lo hace la raíz); su repo no se edita desde aquí.

## 1. Objetivo

Lo que el laboratorio puede hacer **sin esperar a ningún sprint de `quantdesk`**:

1. **TI-02-DIARIO** antes de la ola 1 de quantdesk SPRINT-03: primero el contrato con el backend (dónde corre, ruta,
   formatos, series OAS, credencial), después el código **sin OAS** (R5).
2. **Cadenas de opciones:** medir la cobertura de los 20 días hábiles NYSE desde la sesión 2026-11-12 (S02-6) y cerrar
   con esa cifra la sonda de cadenas (R4).
3. **MT5,** en cuanto el bróker desbloquee la cuenta: una sola ventana de descargas prudentes (incremental m1/m5, h1 de
   `@continuo`, acciones de `@us_grandes`; R8), reactivar el publicador 1d y hacer la carga nocturna de `@continuo`
   (R2, R3); el resto del universo ampliado en qn, sólo si se cumplen sus condiciones (GAP-DATOS_VIA_QN-08).
4. **Lo que publique el backend en su SPRINT-03:** consumir FRED/OAS (R6) y añadir los OAS al exportador diario (R5),
   como dependencias de tarea que no bloquean la activación.

## 2. Responsabilidades y gobernanza

Filas de [GOBERNANZA.md](../GOBERNANZA.md) que afectan a este sprint (revisadas el 2026-11-13).

| Cosa | Dueño | Escribe | Decide | Nota para este sprint |
|---|---|---|---|---|
| Exportador diario TI-02-DIARIO: código | quantdesk-model | sesiones del laboratorio | usuario | **Contrato decidido (usuario, 2026-11-14)**: [contrato-propuesta.md](execution/TI-02-DIARIO/contrato-propuesta.md) |
| Topic `ops.export.status` y credencial del exportador | quantdesk-network | network registra y emite; el usuario instala el token | usuario | Decidido el 2026-11-14; registro y emisión pendientes |
| Programación del exportador en Dagster | quantdesk-backend | sesiones del backend | usuario | Su PUB-05-EXPORT; depende del contrato y del código de las filas 1 y 2 |
| Publicador MT5 → qn `market.ohlcv.v2` y copia local del intradía | quantdesk-model | sesiones del laboratorio | usuario (visto bueno de network y aviso al backend antes de publicar el universo ampliado) | Filas 4 y 5 |
| Publicadores públicos en qn (FRED, OAS; Yahoo/Stooq y cripto sin sprint) | quantdesk-backend | sesiones del backend | usuario | Filas 6 y 7 consumen lo que publique |
| Scraper de cadenas (OC-03) / esquema y retención del lago | backend / network | sus sesiones | usuario | Fila 3 lee del lago; sin copia propia (D7) |
| Credenciales (MT5, `QN_TOKEN`) | usuario | usuario | usuario | Nunca en repos, informes, prompts ni chat |

## 3. Tareas

Todas las filas tienen nivel L1–L10 y aceptación ejecutable. «Puerta» = acción que sólo puede hacer o aprobar el
usuario. La **fila 4** es «la fila de MT5» a la que se refieren R2, R3 y R8: comparte puerta (desbloqueo de la cuenta)
y terminal (mutex), y se ejecuta en una sola ventana.

> **Entrada de la fila 1. Respuesta del backend del 2026-11-14 (~00:10), raíz `quantdesk-backend-d4`; contrato aún no acordado.**
> Restricciones que el backend ya tiene fijadas en su `next/SPRINT.md` (líneas 28 y 51-52):
> - el código es del laboratorio y el backend no lo escribe ni lo modifica (S03-D2); el backend crea el job, el schedule y la alerta `DagsterJobStale`;
> - corre cada día hábil tras el cierre de Nueva York, cuando MT5 publica el 1d;
> - no exporta la vela 1d del día en curso ni una vela incompleta;
> - un día sin datos en qn da un aviso, nunca un fichero vacío;
> - el FX diario va con `source=mt5`;
> - `quantdesk` no importa un cliente de qn ni lee tokens: la credencial de lectura la pone el lado Dagster;
> - los OAS son de uso interno (S03-D3 del backend, de la decisión D4 del usuario; corregido el 2026-11-14): no salen del equipo del usuario y no hay fixtures con valores de ICE.
>
> Su SPRINT-03 publica FRED (PUB-01) y OAS (PUB-02) y programa el exportador (PUB-05-EXPORT). Confirman que Yahoo/Stooq
> (PUB-03) y cripto (PUB-04) no están en él.
>
> Queda por acordar en una propuesta conjunta para el usuario:
> 1. Dónde corre. Dagster vive en mini (Linux, contenedores) y no ve el `E:/` del PC; si el destino es `E:/`, hace falta copiar a una ruta compartida o un job en el PC.
> 2. Ruta y formato `desktop.daily-ohlcv/v1`: los propone el laboratorio y los revisa el backend.
> 3. La credencial de qn del job: la emite network y la pone el usuario en el `.env`.
> 4. Qué hace el exportador sin 1d de `source=mt5` mientras el publicador esté desactivado: avisar y parar, o esperar.

| Fila | ID | Qué se hace | Aceptación (ejecutable) | Depende de | Nivel | Puerta de usuario |
|---|---|---|---|---|---|---|
| 1 | **TI-02-DIARIO** (contrato) — primera fila | Acordar por mensaje con `quantdesk-backend` (y con `quantdesk` para formatos y ruta) el contrato del exportador diario: **dónde corre** (Windows del laboratorio, Linux/Dagster o en dos fases: opciones de GAP-DATOS_VIA_QN-06), **ruta** de salida que abre `quantdesk`, **formatos** (`engine.market-history/v1` y `desktop.daily-ohlcv/v1`, y quién escribe el segundo), **series OAS** (PUB-00), **credencial** (`sub:` de lectura de qn, fuera del repo) y **hora** (después del cierre de Nueva York y de la pasada del publicador MT5). Registrarlo en GOBERNANZA (filas del exportador), DEPENDENCIAS (dependencia de tarea) y PLAN_DATOS_VIA_QN §4 | (1) Mensajes enviados y respuestas registradas con fecha en el EXECUTION del sprint; (2) GOBERNANZA y DEPENDENCIAS con el contrato marcado «decidido (usuario, fecha)» tras el visto bueno del usuario; (3) PLAN_DATOS_VIA_QN §4 sin el bloque «Sin fijar y bloqueante»: ruta, formatos, lugar de ejecución, series y credencial escritos; (4) patrón `qn_` = 0 en repo e informes | Respuesta del backend y de `quantdesk` (sin dependencia de sprint) | L3 | Aprobar el contrato y la credencial del job |
| 2 | **TI-02-DIARIO** (código, sin OAS) | Exportador diario desde qn sobre `scripts/descarga_lago.py` y `exportar_market_history_lib` (TI-02-DATA-V2), en el lugar y con la ruta y los formatos del contrato; FX diario sólo `source=mt5`; día sin datos = aviso. **Plazo: antes de la ola 1 de quantdesk SPRINT-03** (R5) | Criterios (1)–(6), (8) y (9) de [PLAN_DATOS_VIA_QN](../backlog/PLAN_DATOS_VIA_QN.md) §4 con `--selftest` sobre qn falso: día sin barras → aviso registrado y ningún fichero vacío; ni la vela 1d del día en curso ni una incompleta; mismo corte y entradas → mismo SHA-256 y 0 violaciones de look-ahead; FX diario sólo `source=mt5` y día sin vela de MT5 = aviso (no se rellena con yfinance); `grep` en `quantdesk` sin cliente de qn ni lectura de tokens. El criterio (7) (OAS) va en la fila 7. Mientras la cuenta MT5 siga bloqueada el FX sale como aviso (esperado, no fallo) | Fila 1 | L6 | Credencial `sub:` para el job, si el contrato la pide |
| 3 | **S02-6 TI-09-ARCH** (medición de cobertura) + cierre de [ISSUE-TI09-SONDA-CADENAS](issues/ISSUE-TI09-SONDA-CADENAS.md) | Resto de la fila 6 de SPRINT-02 (ya hecho: lector y archivador aceptados `c6c7b5b`, A4 ACEPTAR, y primer dataset real `oc03_s20261112_c20261113`, `sha256:eb98ac6a…eea1`, cruda 431.681 filas, limpia 320.125). Volcado en mini de las **20 sesiones NYSE 2026-11-12…2026-12-10** (Thanksgiving 2026-11-26 fuera) con `scripts/descarga_opciones.py`, copia a `E:/quantdesk-lab/tmp/TI-09-ARCH/` y archivado con `scripts/archivo_opciones.py` con corte posterior al 2026-12-10. Con el mismo volcado, la **cifra por sesión desde el 2026-11-12** cierra la sonda; los días 2026-11-09…11 (régimen sin `capture_id`) se documentan como **no medibles** (R4). **Métrica por defecto** (GAP-ARCHIVO_OPCIONES-03, diferido: se confirma al hacer la ficha): días con captura completa (≥ 95 % del universo esperado del backend y los 7 obligatorios) sobre 20, y por separado pares subyacente-día frente a los 510 esperados por el backend. Ventana: la de esta fila, desde la sesión 2026-11-12 hasta el 2026-12-10 (C-ARCHIVO_OPCIONES-06, decidida en el arrastre del 2026-11-13) | (1) Cobertura ≥ 98 % según la métrica (con 20 días, 20/20) o causa documentada por cada día o subyacente que falte; (2) dos lecturas del mismo rango y corte sobre el lago real dan el mismo SHA-256; (3) informe de exclusiones por motivo y de huecos por subyacente y `asset_type` de las 20 sesiones; (4) pico de memoria ≤ 3 GB por sesión, medido; (5) cifra por sesión (filas, subyacentes, vencimientos, `capture_id`) guardada con su consulta, nota «2026-11-09…11 no medibles» en la ficha de la sonda, que se cierra y se archiva; (6) token revocado y patrón `qn_` = 0 en volcado, repo, informes y chat | Fecha ≥ 2026-12-11; OC-03 del backend en producción (OC-04 para la duración de los runs) | L5 | Emitir y revocar un `QN_TOKEN` de lectura (`sub:market.options.chain` y `sub:market.options.fx`) |
| 4a | **S02-5 TI-12-MT5** (h1 de `@continuo`) | Texto íntegro de la fila 5 de SPRINT-02: más símbolos y periodos; la descarga incremental reanudable no es de esta fila (va en 4b, [ISSUE-TI12-MT5-INTRADIA-LOCAL](issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md), D3). Alcance fijado por el usuario el 2026-11-11: **h1 de `@continuo`, sin símbolos nuevos**. Estado al arrastre: sin empezar; el parquet h1 de `D:/dev/deeplearning_dev` sólo trae FX28 y no cubre el alcance (comprobado el 2026-11-13). Con `scripts/extractor_mt5.py` (sólo lectura), una serie cada vez y pausa fija entre series, a `E:/quantdesk-lab/data/mt5/continuo_h1_<fecha>` | Mismo hash para el mismo rango en los símbolos y periodos nuevos, con manifiesto (la reanudación sin duplicados se acepta en 4b); la repetición con `--refrescar` se hace **sobre un subconjunto declarado** (p. ej. fx28) para no doblar la carga al bróker; manifiesto con símbolo, periodo, primera y última barra, filas y hash; ritmo y número de series por sesión escritos en la ficha antes de empezar; 0 órdenes; nada se publica en qn | **Desbloqueo de la cuenta MT5**; mutex del terminal con 4b y 4c; descargas prudentes | L6 | Desbloqueo de la cuenta; aprobar el ritmo |
| 4b | **TI-12-MT5-INTRA-LOCAL** ([ficha](issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md)) | Alcance (R8): **fx28 y `@continuo` primero** (incremental m1/m5 con `--hasta` nuevo sobre la caché `E:/quantdesk-lab/data/mt5/_trozos`), **después las 484 acciones de `@us_grandes`** (cota ≈ 3,1 GiB; medir con `extractor_mt5.py --inventario --grupo @us_grandes` y descargar), una serie cada vez. Pasadas **manuales cada ≤ 6 semanas**, la primera **antes del 2027-01-17**; **sin tarea programada**. Fusionada operativamente con 4a (mutex del terminal MT5) | Criterios 1, 2, 4 y 6 de la ficha: mismo `hash_conjunto` en dos descargas del mismo rango (subconjunto declarado); `trozos_reutilizados` > 0 en el registro y manifiesto sin huecos salvo fines de semana y festivos del bróker; periodicidad manual ≤ 6 semanas escrita en la ficha con la fecha de la siguiente pasada; cifra de las acciones anotada y, si se descargan, manifiesto con hash cuya suma de filas cuadra con el inventario; primera pasada antes del 2027-01-17; nada en qn y 0 órdenes | Desbloqueo de la cuenta MT5; mutex con 4a y 4c | L5 | Desbloqueo de la cuenta |
| 4c | **TI-12-MT5-OPS** (publicador 1d y carga nocturna de `@continuo`; residuo de ISSUE-TI12-MT5-SYNC, R2 y R3) | Tras el desbloqueo: reactivar la tarea `quantdesk\publicador_mt5` (**desactivada** por la raíz de guardia el 2026-11-13, R2); primera pasada con relleno de huecos del 1d de fx28 (parado desde el 2026-11-10) y aviso al backend; después, **carga nocturna del 1d de `@continuo`** (≈ 369 000 objetos) con aviso a backend y network, ≤ 40 000 objetos por 5 min, 02:00–05:00 CET, parada si el cursor del Bento se retrasa; revisar el token `ti12mt5-publicacion-20261109` (id 36) | `ultimo.json` de la primera pasada con `codigo` 0, 28 series y 0 `revisiones_detectadas`; 28/28 series sin hueco en qn (lectura de sólo lectura); registro de la noche de `@continuo` (series, objetos, errores) con objetos publicados = filas locales por serie y sin `revisiones_detectadas` sin explicar; `publicador_mt5.py --selftest` ok; revisión del token anotada | Desbloqueo de la cuenta MT5; terminal libre de 4a y 4b; visto bueno de network y aviso al backend vigentes para la noche | L3 | Desbloqueo; reactivar la tarea programada; aprobar la noche; revisión del token id 36 |
| 5 | **TI-12-MT5-PUB-AMP** (resto del universo ampliado en qn: acciones de `@us_grandes`, noches 2–3) — **condicionada** | Publicar el 1d de las 484 acciones de sesión normal y las 13 `-24` en `market.ohlcv.v2` (≈ 690 000 objetos por noche) con el mismo ritmo y avisos que 4c | Registro de cada noche sin `revisiones_detectadas` sin explicar; cuadre `cuadre_mt5.py` de un subconjunto 1d contra qn; Bento y ClickHouse sin retraso (aviso del backend) | **Condición de entrada (GAP-DATOS_VIA_QN-08):** desbloqueo de la cuenta + visto bueno **nuevo** de network + aprobación del usuario; 4c cerrada. GAP-DATOS_VIA_QN-09 (dos publicadores) sigue abierto: se pregunta al planificar la fila si para entonces el backend publica acciones | L5 | Aprobación del usuario (fila y cada noche) |
| 6 | **TI-13-PUB-FRED** (consumo de FRED/OAS; R6) | Exportar con TI-02-DATA lo que el backend publique en qn de FRED (H.15) y de OAS; filtro de fugas D-11 sobre esas series; licencias en la tabla (FRED: atribución; ICE: uso interno) | Informe del filtro actualizado; datasets con hash exportados desde qn y reproducibles; licencias anotadas; el dataset con OAS no sale del equipo del usuario | **Dependencia de tarea:** quantdesk-backend SPRINT-03 (PUB-00…PUB-02, topic de GAP-PUB-01); no bloquea la activación | L4 | Token de lectura de qn, si el volcado lo pide |
| 7 | **TI-02-DIARIO-OAS** | Añadir al exportador de la fila 2 los OAS que publique PUB-02 | Dataset con OAS con la fecha de publicación de la fuente (sin look-ahead); huecos como aviso; criterio (7) de PLAN_DATOS_VIA_QN §4: el dataset con OAS no sale del equipo del usuario ni va a repos | Fila 2; **dependencia de tarea:** quantdesk-backend SPRINT-03 PUB-01/PUB-02 | L4 | Ninguna |

**Fichas de issue seleccionadas para este sprint** (destino «Sprint actual»; pasaron de `issues/` a
[current/issues/](issues/index.md) al activar el 2026-11-14, mismo ID):
[ISSUE-TI09-SONDA-CADENAS](issues/ISSUE-TI09-SONDA-CADENAS.md) (fila 3) e
[ISSUE-TI12-MT5-INTRADIA-LOCAL](issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md) (fila 4b). ISSUE-TI12-MT5-SYNC y
ISSUE-TI12-MT5-VELA-A-MEDIAS están **resueltas** (R3) y archivadas en
[archive/FUERA-SPRINT_2026-11-09_2026-11-13/](../archive/FUERA-SPRINT_2026-11-09_2026-11-13/ARCHIVE_MANIFEST.md); su
residuo es la fila 4c.

**Planes del backlog que alimentan el sprint:** [PLAN_DATOS_VIA_QN](../backlog/PLAN_DATOS_VIA_QN.md) (filas 1, 2,
4a–4c, 5, 6 y 7) y [PLAN_ARCHIVO_OPCIONES](../backlog/PLAN_ARCHIVO_OPCIONES.md) (fila 3; se archiva al cerrar S02-6, no
antes del 2026-12-11). Los planes no se reducen: sus IDs son más amplios que las filas y anotan el sprint que las ejecuta.

## 4. Dependencias externas

**Sin dependencia de entrada de sprint** (usuario, 2026-11-13, revisión de planes, R1): ninguna fila necesita que
cierre un sprint de otro proyecto para empezar. Las dependencias que hay son **de tarea**: no bloquean la activación,
sólo el inicio de la fila indicada.

| Fila (tarea local) | Depende de (proyecto, sprint, tarea) | Condición | Estado |
|---|---|---|---|
| 1 TI-02-DIARIO (contrato) | quantdesk-backend, `next/SPRINT.md` (SPRINT-03), PUB-05-EXPORT; quantdesk, formatos de D-I4 (`PLAN_TSFM_INTEGRACION` §6) | respuesta por mensaje | decidido (usuario, 2026-11-13, revisión de planes, R5); **contrato decidido (usuario, 2026-11-14)** |
| 2 TI-02-DIARIO (despliegue) | quantdesk-network: registro de `ops.export.status` y token; quantdesk-backend: tarea de Windows y sensor | topic y token emitidos | decidido (usuario, 2026-11-14); pendiente |
| 2 TI-02-DIARIO (código) | (salida) quantdesk SPRINT-03, ola 1, XVA-03-DATA lo espera; backend PUB-05-EXPORT lo programa | entregar antes de la ola 1 | decidido (usuario, 2026-11-09/10; calendario R5) |
| 3 S02-6 + sonda | quantdesk-backend OC-03 en producción (servida, `cc1811d`) | fecha ≥ 2026-12-11 | servida |
| 4a, 4b, 4c, 5 | bróker MT5: desbloqueo de la cuenta (lo gestiona el usuario) | cuenta desbloqueada | bloqueada desde el 2026-11-10 |
| 4c (noche de `@continuo`) y 5 | quantdesk-network: visto bueno de carga (ritmo, memoria de mini); quantdesk-backend: aviso (Bento) | visto bueno vigente / nuevo | el del 2026-11-09 era para la noche del 2026-11-10, que no salió |
| 6 TI-13-PUB-FRED | quantdesk-backend SPRINT-03, PUB-00…PUB-02 | tarea entregada | decidido (usuario, 2026-11-13, revisión de planes, R6) |
| 7 TI-02-DIARIO-OAS | quantdesk-backend SPRINT-03, PUB-01/PUB-02 | tarea entregada | decidido (usuario, 2026-11-13, revisión de planes, R5) |

Contrato para `sprint deps` en [DEPENDENCIAS.md](../DEPENDENCIAS.md).

## 5. Exclusiones

| Qué | Motivo | Destino |
|---|---|---|
| TI-12-MT5 intradía publicado en qn | Se planifica con el sprint de entrenamiento; consumidor TS-05-FREQ; visto bueno de network (usuario, 2026-11-13, revisión de planes, R7; mantiene la decisión del 2026-11-09; GAP-DATOS_VIA_QN-10 resuelto) | [future/SPRINT-05](../future/SPRINT-05/SPRINT.md) |
| TI-13-PUB consumo de Yahoo/Stooq y cripto | El backend no los publica (PUB-03/PUB-04 sin sprint); falta la política de dos publicadores (GAP-DATOS_VIA_QN-09 = GAP-BACKLOG_README-03) (usuario, 2026-11-13, revisión de planes, R6) | Backlog: [PLAN_DATOS_VIA_QN](../backlog/PLAN_DATOS_VIA_QN.md) §3 |
| Filas S02-1…S02-4; re-exportación con TI-03-FMT; licencias al ADR; TS-00-PREC con sintéticos del motor; TS-02-DISC; TS-00-BENCH en GPU | Dependen de entregas de quantdesk SPRINT-02 y SPRINT-03 (R1) | [SPRINT-04](../next/SPRINT.md) |
| Ejecuciones de entrenamiento, ajuste fino, adaptadores | Necesitan TI-06-CLI, DL-07-TRAIN y TS-05-PREC (SPRINT-04 de `quantdesk`) | [future/SPRINT-05](../future/SPRINT-05/SPRINT.md) |
| Cortes periódicos de cadenas después de S02-6 | GAP-ARCHIVO_OPCIONES-05 diferido (bajo demanda por defecto) | Se decide al cerrar S02-6 |
| Copia del lago | Es la común de network (D7); el laboratorio sólo guarda lo leído al cortar | — |
| XVA (XVA-03-DATA/CDS/CURVE…) | Se ejecuta en `quantdesk` | — |

## 6. Orden

1. **Fila 1 al activar** (contrato por mensaje) y **fila 2** en cuanto haya contrato: es la única con plazo duro
   (antes de la ola 1 de quantdesk SPRINT-03).
2. **Fila 4 en cuanto se desbloquee la cuenta**, en una sola ventana y nunca dos tareas a la vez en el terminal:
   4b incremental m1/m5 de fx28 y `@continuo` (lo que caduca) → 4a h1 de `@continuo` → 4b acciones de `@us_grandes` →
   4c reactivación del publicador y primera pasada → noche de `@continuo` → fila 5 sólo si se cumplen sus condiciones.
   Una serie cada vez, con pausas; el publicador, una pasada al día. Si la cuenta sigue bloqueada al acercarse el
   2027-01-17, avisar al usuario (fecha límite de 4b).
3. **Fila 3 desde el 2026-12-11**, en una sola sesión de token.
4. **Filas 6 y 7** cuando el backend avise de que publica FRED/OAS (aviso de salida de su SPRINT-03).

## 7. Definition of Done

La de [SPRINT-01](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md#8-definition-of-done).

## 8. Capacidad y presupuesto

Suscripciones compartidas con `quantdesk` (su SPRINT-02 sigue abierto), `quantdesk-backend`, `quantdesk-network` y
`reinforcement_learning`, sin tope ni reserva (SPRINT_PROJECT §7).

- **Lectura al activar** (2026-11-14 00:39 CET, `claude-or quota --weekly`): Claude 78 % con el 56,9 % de la ventana
  (reinicio 2026-11-16 23:59 UTC); Codex 61 % con el 37,8 % (reinicio 2026-11-18 08:07 UTC). Codex va a 1,6 veces el
  ritmo de su ventana.
- **Orden temporal del usuario** (2026-11-14 00:20, skill `niveles-y-modelos.md` §0, hasta el 2026-11-17 00:59): Codex
  implementa y revisa todo; Claude, sólo la raíz, L9–L10 y sus arenas. Ninguna fila de este sprint pasa de L6.
- **Carga a corto plazo:** sólo las filas 1 y 2 pueden avanzar ahora. Fila 1 (L3): coordinación por mensaje de la raíz;
  el borrador lo prepara un Codex de sólo lectura y lo revisan el backend, `quantdesk` y el usuario, que lo aprueba.
  Fila 2 (L6): autor `gpt-6.1-sol` xhigh y revisor `gpt-6-astra` high. Las filas 3 (desde el 2026-12-11), 4a–4c y 5
  (desbloqueo de MT5) y 6–7 (publicación del backend) no consumen cuota hasta que se abra su puerta.
- **Escenario hipotético, sin calibración propia:** no hay consumo medido por tarea en SPRINT-01 ni en SPRINT-02 (no
  se archivó USAGE.md), así que no se da una cifra de pp por fila. Se toma como supuesto que una sola tarea L6 con su
  revisión cabe en el margen de Codex antes de su reinicio, y se comprueba leyendo la cuota antes y después de la
  fila 2. Antes de cada ola se lee la cuota y se anota en EXECUTION. Si Codex se acerca a su
  reserva, se avisa al usuario antes de pasar trabajo a Claude (§0). No se recorta alcance para ahorrar.
- Medición según [USAGE_PROTOCOL](../USAGE_PROTOCOL.md); coordinador de costes: la raíz. Se recalibra al cerrar.
