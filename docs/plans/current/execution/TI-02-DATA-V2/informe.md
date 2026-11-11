# TI-02-DATA-V2 · subentrega A

Fecha: 2026-11-11. Base: `934d9af000c6c9f0452f3757a8c9bf856bf821d5`. Autor: `autor-1b-A`, padre: raíz inicial (Opus 5.5), intento 1, dificultad L6 (`difficulty-v3-10`). Ejecución en la suscripción Codex del proyecto. Semilla: no aplica, transformación determinista sin muestreo ni RNG. Motor verificado: `quantdesk 69fdb39d`; Python 3.12.3, pyarrow 26.0.1, pandas 3.1.1, numpy 2.5.4.

La subentrega A implementa v2, selección de fuentes y reproducción histórica. La lectura real de qn y el cuadre con MT5 quedan para B: no se han solicitado, buscado ni leído credenciales, `.env` ni el directorio de secretos; las únicas peticiones de esta ejecución son a servidores falsos en 127.0.0.1. No hay publicación ni push. Los originales de TI-02-DATA se han leído, sin regenerarlos sobre su directorio.

## Cambios y reglas de fuente

- `scripts/descarga_lago.py`: sin `--topics` solicita exclusivamente `market.ohlcv.v2`. Rechaza el topic OHLCV v1 con explicación de su congelación. Se mantienen los topics de eventos por opción explícita. Añade `--source`, `--symbols` (alias `--simbolos`) y `--interval`, con listas de valores exactos separadas por comas. Los tags completos se reenvían en cada petición de filas y quedan en cada entrada de fichero del manifiesto. Una respuesta cuyos tags no coincidan con el filtro falla.
- La política única es `POLITICA_FUENTES`, versión `ti-02-data.fuentes/v1`, en `scripts/descarga_lago.py:64`; el exportador la importa. Reside ahí para que el volcado en mini siga siendo un único fichero con biblioteca estándar, sin instalar nada. Su SHA-256 se incorpora también a `codigo_sha256` del exportador (`scripts/exportar_market_history.py:82`).
- Clasificación explícita: seis letras mayúsculas, dos divisas distintas de `AUD,CAD,CHF,EUR,GBP,JPY,NZD,USD`. Cubre los 28 pares de `scripts/extractor_mt5_lib/inventario.py:23` y sus orientaciones inversas. No clasifica metales, criptomonedas, índices, sufijos de bróker ni otras divisas: siguen la regla sin clase. El publicador normaliza los símbolos antes de publicarlos.
- Regla de clase: **FX + `interval=1d` → exclusivamente `source=mt5`**, por ISSUE-LAGO-FX-1D-CLOSE. Ningún filtro CLI anula esta regla. Si sólo hay `market_scraper`, no se usa de sustituto; se excluye y se avisa. Para otra fuente de FX diario, incluso `mt5:<bróker>`, hará falta una regla versionada nueva.
- Sin regla: **una única fuente por `(symbol, interval)`**. Dos fuentes fallan antes de la limpieza, también si sus historias no se solapan. Es una decisión conservadora explícita: además de rechazar la misma `(instrumento, intervalo, ts)` de dos fuentes, impide empalmar historias sin una regla de procedencia. Republicaciones dentro de una misma fuente siguen entrando en la política existente de versiones.
- El volcado registra selección, versión de política, combinaciones excluidas por filtro/regla y avisos. No solicita las filas excluidas; cuenta combinaciones y declara que el número de barras no solicitadas no se conoce. Reanudar con otra selección, topic o versión de política falla antes de modificar el manifiesto previo. Se conserva la reanudación con la misma selección, los hashes y la partición automática por exceso de filas.
- El exportador consume `market.ohlcv.v2`, valida `source` no vacío en las etiquetas de cada fichero, contrasta los tags presentes en cada fila y rechaza explícitamente cualquier volcado con OHLCV v1, incluso mezclado con v2. Nunca infiere la fuente del objeto. En `procedencia.json`, `tablas[].carga.source` deja de contener `None`; `seleccion_fuentes` detalla las series, reglas, fuentes leídas y excluidas. `limpieza.excluidas.fuente_excluida_por_regla` cuenta cada barra descartada; la identidad origen = finales + excluidas sigue comprobándose.
- El manifiesto `engine.market-history/v1` describe las fuentes y sus filas finales. La procedencia y el informe generado detallan todos los descartes y la ausencia de MT5. La descripción del manifiesto sólo incorpora las fuentes presentes en las filas finales: añadir datos posteriores al corte no cambia el manifiesto ni los parquet, como exige el test anterior.
- V2 `/objects` usa RFC 3339 con microsegundos: se añade lectura exacta con zona explícita, hasta nanosegundos, además del formato numérico anterior. Se trunca `_ts` a ms y se redondea `_recv_ts` hacia arriba, sin floats. Referencia verificada: `docs/plans/archive/SPRINT-01_2026-11-07_2026-11-09/execution/TI-12-MT5/fase-b.md:75` y `scripts/publicador_mt5_lib/qn_falso.py`.
- Añade `--desde` al exportador: límite inferior inclusivo por `ts_ms`, contado como `anterior_al_inicio_de_ventana`. Se necesita para la cabecera y la ampliación histórica del mismo volcado. `--corte`, `recepcion` y `cierre` conservan sus significados. **`limpieza.py` no se modifica.** Se conserva la primera versión recibida con `_recv_ts >= ts + intervalo`; en ausencia de recepciones se mantiene el comportamiento anterior. El modo `cierre` sigue siendo un proxy, con `available_at_ms` nulo y `default_lag_ms=0`, no disponibilidad causal demostrada.

## Casos borde → test que los cubre

`E` = `scripts/exportar_market_history_lib/selftests.py` (`prueba_fuentes_v2`:612, `prueba_corte_v2_posterior_migracion`:716); `D` = `scripts/descarga_lago.py` (`selftest`:590, `prueba_seleccion_v2`:805). Todos se invocan desde los respectivos `--selftest`.

| Caso borde | Test y caso concreto |
|---|---|
| FX 1d en MT5 y market_scraper: sólo MT5, descarte contado | E `prueba_fuentes_v2`, `fx_doble`; D `prueba_seleccion_v2`, `regla_v2` |
| Índice 1d con misma clave en dos fuentes: error explícito | E `prueba_fuentes_v2`, `indice_doble`; D `prueba_seleccion_v2`, `conflicto_v2` |
| Una fuente sin regla: se acepta y se anota | E `prueba_fuentes_v2`, `indice_unica` (`yahoo`) |
| FX diario sólo market_scraper: cero filas y aviso | E `prueba_fuentes_v2`, `fx_sin_mt5`, tanto `recepcion` como `cierre` |
| Fichero v2 sin tag source: error explícito | E `prueba_fuentes_v2`, `sin_tag`; D `prueba_seleccion_v2`, `sin_source_v2` |
| Topic por defecto vuelve a v1: falla el selftest | D `selftest`, aserción literal `TOPICS_DEFECTO == ('market.ohlcv.v2',)` y CLI sin `--topics`; mutación ejecutada en copia temporal, `default_mutacion.log` |
| Volcado v1 al exportador nuevo: error explícito | E `prueba_fuentes_v2`, `volcado_v1`; también rechazo v1 en D |
| Republicaciones de la misma fuente: primera versión cerrada | E `prueba_fuentes_v2`, `versiones_mt5`, más `prueba_versiones_del_lago` anterior intacto |
| Corte posterior al 2026-11-09: aparecen barras v2 posteriores | E `prueba_corte_v2_posterior_migracion`: qn falso → volcado sin `--topics` → exportador, barras del 9 y 10 de noviembre, corte 12, cero violaciones |
| Dos historias sin solape de distintas fuentes sin regla | E `prueba_fuentes_v2`, `indice_empalme` |
| Filtros exactos y cambio de filtro al reanudar | D `prueba_seleccion_v2`, `filtros_v2`: dos símbolos, source/interval enviados y manifiesto intacto tras rechazo |
| Mismo v2 dos veces: mismo hash y mismos bytes | E `prueba_fuentes_v2`, `fx_doble` + `v2_repetida`; comparación de todos los SHA-256 y del hash del motor |
| Ventana histórica y redondeo sin look-ahead | E `prueba_fuentes_v2`, `ventana_mt5` y RFC3339 con µs/ns, zona +01:00 y rechazo sin zona |

## Tests existentes: cambios declarados

No se elimina, relaja ni omite ninguna aserción del exportador. Se migra exclusivamente la forma de sus entradas sintéticas: `datos_lago` cambia el nombre del topic a v2 y añade `source=market_scraper` a las etiquetas; `prueba_exportar_lago` altera la ruta del fichero manipulado para que siga comprobando el rechazo por SHA-256. `prueba_integracion_con_descarga` pide explícitamente el catálogo de tres topics que antes era el valor por defecto y su aserción de filas por topic usa la clave v2; conserva todas las cifras y condiciones anteriores. Las barras AAA/BBB/CCC siguen sin ser FX, con la misma única fuente. `LAB_TMP` cambia al temporal autorizado de esta tarea.

El selftest de `descarga_lago.py` se migra a v2 como se autorizó: catálogo con source como tag, filas de `/objects` con tags y marcas RFC3339, rutas con source y aserciones equivalentes; se conservan los casos de integridad, reanudación, límites, reintentos, rechazos, redirecciones y protección de la credencial ficticia. Se añaden los casos descritos arriba. No se toca ningún otro selftest.

La primera ejecución del exportador detectó una regresión propia: recuentos brutos de fuentes en la descripción del manifiesto hacían que filas futuras cambiasen sus bytes. Se corrigió la descripción para usar únicamente filas finales; **la aserción anterior que lo detectó se mantuvo sin cambios**. Las salidas de aceptación siguientes corresponden al código corregido.

## Reproducción histórica, sin qn

El código de `descarga_lago.py` y del exportador de la base `934d9af` coincide con el de `0e67465` (`git diff 0e67465 934d9af -- scripts/descarga_lago.py scripts/exportar_market_history.py scripts/exportar_market_history_lib`: salida vacía). La reproducción se ejecutó con **el exportador y los scripts de `0e67465`**, nunca con el lector nuevo. El script antiguo de volcado se conserva junto a él: `git show 0e67465:scripts/descarga_lago.py`.

Extracción ejecutada por `E:/quantdesk-lab/tmp/TI-02-DATA-V2/regenerar.py`, sin red: `git archive 0e67465 scripts` con stdout binario capturado en memoria y extracción con `tarfile` a `E:/quantdesk-lab/tmp/TI-02-DATA-V2/v1code/`. Se ejecutó mediante `.venv/Scripts/python -X utf8 E:/quantdesk-lab/tmp/TI-02-DATA-V2/regenerar.py`. La evidencia pequeña `regeneracion.json` adjunta comandos, versiones, validaciones y SHA-256 de todos los ficheros originales antes/después.

| Dataset | Hash original | Hash regenerado | Coincide |
|---|---|---|---|
| `binance_c20261101` | `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744` | `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744` | sí |
| `lago_c20261101` | `sha256:cce80ad2bb82374e71a92ba27c4f9a89ad6ad0d7901697b853c15e24b39f70ea` | `sha256:cce80ad2bb82374e71a92ba27c4f9a89ad6ad0d7901697b853c15e24b39f70ea` | sí |
| `lago_cierre_c20261101` | `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356` | `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356` | sí |
| `lago_c20261107` | `sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495` | `sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495` | sí |

Órdenes exactas ejecutadas (Python del laboratorio, código histórico y salida temporal):

```powershell
S:\Projects\quantdesk-model\.venv\Scripts\python.exe -X utf8 E:\quantdesk-lab\tmp\TI-02-DATA-V2\v1code\scripts\exportar_market_history.py --binance --corte 2026-11-01 --nombre binance_c20261101 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen --runs E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen_runs
S:\Projects\quantdesk-model\.venv\Scripts\python.exe -X utf8 E:\quantdesk-lab\tmp\TI-02-DATA-V2\v1code\scripts\exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-01 --nombre lago_c20261101 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen --runs E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen_runs
S:\Projects\quantdesk-model\.venv\Scripts\python.exe -X utf8 E:\quantdesk-lab\tmp\TI-02-DATA-V2\v1code\scripts\exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-01 --nombre lago_cierre_c20261101 --disponibilidad-ohlcv cierre --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen --runs E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen_runs
S:\Projects\quantdesk-model\.venv\Scripts\python.exe -X utf8 E:\quantdesk-lab\tmp\TI-02-DATA-V2\v1code\scripts\exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-07 --nombre lago_c20261107 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen --runs E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen_runs
```

Salida de la reproducción:

```text
binance_c20261101 sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744 coincide=True
lago_c20261101 sha256:cce80ad2bb82374e71a92ba27c4f9a89ad6ad0d7901697b853c15e24b39f70ea coincide=True
lago_cierre_c20261101 sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356 coincide=True
lago_c20261107 sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495 coincide=True
4/4
originales_sin_cambios=true
```

Los cuatro resultados tienen `validacion.ok=true` y cero violaciones de look-ahead por fila. El modo proxy conserva su advertencia y su política estricta no satisfecha: eso no se convierte en causalidad por reproducir su hash. Se verificaron los bytes de los ficheros originales antes y después: no cambiaron. Las salidas están exclusivamente en `E:/quantdesk-lab/tmp/TI-02-DATA-V2/regen/`, con registros en `regen_runs/`.

**`lago_cierre_c20261101` está afectado por ISSUE-LAGO-FX-1D-CLOSE.** Se ha regenerado sólo para reproducir su hash histórico; conserva el FX diario de yfinance/market_scraper cuyo close corresponde al inicio del día. La coincidencia de hash no valida esos cierres ni corrige los datos. No debe tratarse como el nuevo dataset de FX diario MT5.

El volcado v1 tiene `script_sha256=1989f121885c0ca3338278c9f35d690e5889d223dd5317646c96280b9e09dace`, que corresponde al blob LF de `a3d6a0e`; el de `0e67465` es `5faf3e1b93a41fb77f2778a94314766fba2553bde998558424c14bb313ae59d0`. Se comprobó cambiando sólo ese metadato en una **copia** del volcado (`volcado_metadato/`, manifiesto copiado, ndjson enlazados y sólo leídos). El exportador histórico siguió dando `sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495`; véase `probe_metadato.json`. El hash lógico incorpora tablas/esquemas/contenido, no el hash del script del volcado ni las rutas de procedencia. Ejecución: `.venv/Scripts/python -X utf8 E:/quantdesk-lab/tmp/TI-02-DATA-V2/comprobar_procedencia.py`.

## Paso 1 para el usuario en mini · no ejecutado

Usar el **nuevo** `descarga_lago.py` de esta entrega. `QN_URLS` y `QN_TOKEN` deben existir en su entorno local; `QN_ENV=main`. No introducir sus valores en la orden, en el repositorio ni en este informe. La lista de 28 símbolos procede literalmente de `scripts/extractor_mt5_lib/inventario.py:23` (`FX28`); un test comprueba que todos satisfacen la regla FX diario MT5.

```sh
python3 descarga_lago.py --topics market.ohlcv.v2 --source mt5 --interval 1d --symbols EURGBP,EURAUD,EURNZD,EURUSD,EURCAD,EURCHF,EURJPY,GBPAUD,GBPNZD,GBPUSD,GBPCAD,GBPCHF,GBPJPY,AUDNZD,AUDUSD,AUDCAD,AUDCHF,AUDJPY,NZDUSD,NZDCAD,NZDCHF,NZDJPY,USDCAD,USDCHF,USDJPY,CADCHF,CADJPY,CHFJPY --desde 2000-01-01 --hasta 2026-11-10 --trozo-dias 10000 --salida <dir>
```

`hasta` es inclusivo: la última consulta lleva `to=2026-11-11T00:00:00Z` exclusivo. Son 9 811 días naturales, unas 27 anualidades × 28 pares; 10 000 días permite una petición inicial por serie (28 en total, además del catálogo), en vez de unas 8 876 con trozos de 31 días. Si hay demasiadas filas o republicaciones, el mecanismo existente parte por la mitad sin truncar y vuelve a partir hasta un día. No se asume que los 28 pares tengan historia desde 2000: revisar los avisos de símbolos ausentes, los ficheros, sus filas y sus rangos.

Copiar el volcado completo, incluido `manifest.json`, al Windows del laboratorio en `E:/quantdesk-lab/tmp/TI-02-DATA-V2/mt5_fx28_20000101_20261110/`. El informe del volcado debe mostrar sólo `market.ohlcv.v2`, `interval=1d` y `source=mt5`; nunca reutilizar una salida con otros filtros.

## Paso 2 para el usuario · no ejecutado con datos reales

Cabecera con corte 2026-11-01 y ventana diaria de `lago_cierre_c20261101`: se usa `--desde 2024-11-01`, su primera barra diaria real, y el mismo límite nominal de cierre. El volcado antiguo se pidió desde 2024-10-01 pero no contiene barras diarias anteriores al 2024-11-01; su última barra diaria admisible era 2026-10-30. No se reproducen sus huecos ni se fuerza al nuevo MT5 a carecer de la barra del 31 de octubre si cumple el mismo corte.

```powershell
.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/tmp/TI-02-DATA-V2/mt5_fx28_20000101_20261110 --desde 2024-11-01 --corte 2026-11-01 --disponibilidad-ohlcv cierre --nombre mt5_fx28_cierre_c20261101 --salida-raiz E:/quantdesk-lab/datasets/TI-02-DATA-V2 --runs E:/quantdesk-lab/tmp/TI-02-DATA-V2/runs
```

Ampliación: mismo volcado, fuente, corte y disponibilidad; toda la historia disponible (sin límite inferior añadido).

```powershell
.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/tmp/TI-02-DATA-V2/mt5_fx28_20000101_20261110 --corte 2026-11-01 --disponibilidad-ohlcv cierre --nombre mt5_fx28_hist_cierre_c20261101 --salida-raiz E:/quantdesk-lab/datasets/TI-02-DATA-V2 --runs E:/quantdesk-lab/tmp/TI-02-DATA-V2/runs
```

No se añade `--sobrescribir`: son datasets nuevos. `cierre` sigue declarando disponibilidad proxy. El cotejo real con `scripts/cuadre_mt5.py` queda pendiente de B y de las entradas MT5 del usuario; esta entrega no afirma haber cumplido el criterio (6). Se ha leído su convención de sesión diaria compartida con el publicador, sin modificar el publicador, el extractor ni el cuadre.

## Aceptación y alcance

Comando: `.venv/Scripts/python -X utf8 scripts/descarga_lago.py --selftest`.

```text
selftest ok
```

Comando: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --selftest`.

```text
selftest ok
```

Comando: `.venv/Scripts/python -X utf8 scripts/run_selftests.py`.

```text
OK     scripts/banco_precision.py: selftest ok
OK     scripts/banco_walkforward.py: selftest ok
OK     scripts/build_wheels.py: selftest OK
OK     scripts/cuadre_mt5.py: selftest ok
OK     scripts/descarga_lago.py: selftest ok
OK     scripts/exportar_market_history.py: selftest ok
OK     scripts/extractor_mt5.py: selftest ok
OK     scripts/ingesta_publica.py: selftest ok
OK     scripts/inventario_options_chain.py: selftest ok
OK     scripts/publicador_mt5.py: selftest ok
OK     scripts/setup_env.py: setup_env selftest ok
OK     scripts/smoke_env.py: smoke_env: OK (21 comprobaciones; 0 SALTADAS)
run_selftests: 12 OK, 0 FALLO
```

Base 934d9af: 120 aserciones; entrega: 163. Todas las anteriores intactas, normalizando solo la clave del topic OHLCV a v2.


El diff de esta subentrega se limita a las rutas autorizadas; `limpieza.py` permanece sin cambios. La orden global `git diff --name-status 934d9af` también muestra los cambios del otro autor en el banco y `docs/plans/current/EXECUTION.md`; el árbol tenía además `bash.exe.stackdump` antes de empezar. No se han tocado, revertido ni añadido al commit. La salida global y la acotada constan completas en `alcance_git.log`; se verifica por separado el contenido selectivo del commit. El siguiente fragmento identifica los cinco ficheros de código; se añaden además los diez ficheros nuevos de este dossier, todos dentro de su ruta autorizada.

```text
M	scripts/descarga_lago.py
M	scripts/exportar_market_history.py
M	scripts/exportar_market_history_lib/fuentes.py
M	scripts/exportar_market_history_lib/informe.py
M	scripts/exportar_market_history_lib/selftests.py
```

Los SHA-256 del informe, evidencias, logs y código se registran en `evidencia_sha256.json` (el propio índice no se incluye en su contenido). Las evidencias de regeneración incluyen la versión del motor y la fecha de corte de cada dataset. La suite completa usa los selftests del proyecto, con sus temporales habituales bajo el laboratorio; los datos y experimentos creados por esta subentrega quedan bajo `E:/quantdesk-lab/tmp/TI-02-DATA-V2/`.

## Corrección 1

2026-11-11 · intento 2 · base `a98cea8` de main (incluye `27cfb2b`) · motor `quantdesk 69fdb39d` · semilla: no aplica · corte del fixture: 2026-11-01. Estado: **BLOQUEADO en recepción MT5 por contradicción de A12**; las secciones anteriores documentan la entrega inicial.
Política `ti-02-data.fuentes/v2`: 164 códigos monetarios vigentes de [SIX, lista publicada 2026-09-17](https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml); metales, otros X no monetarios y cripto fuera de la clase FX. Minúsculas, `/`, sufijo `=X` y espacios exteriores se normalizan sólo para clasificar; `instrument` y filtros siguen exactos.
MT5 1d: versión completa desde las 17:00 America/New_York de D, con `zoneinfo`; source interno procede del tag. Primera versión completa y diagnóstico usan ese umbral; corte, proxy `cierre=ts+1d` y `_recv_ts` de recepción se conservan. Contraste ejecutado con `publicador_mt5_lib.nucleo.sesion_1d` y su regla `ny+7`, incluidas ambas transiciones DST.
A12 es incompatible: invierno cierra 22:00Z y verano 21:00Z; sus ejemplos 21:30Z/20:30Z aún están en curso. Recepciones válidas 22:30Z/21:30Z anteriores a `ts+1d` chocan con la invariante Python y DPOL-AVL-002 del motor; `correccion1/A12.json` reproduce ambos. No se ha cambiado la disponibilidad ni debilitado la validación; hace falta resolver A12 para aceptar recepción.
Temporal del volcado: sistema por defecto, alternativa E:/quantdesk-lab/tmp si existe en Windows y variable `QN_SELFTEST_TMP` para redirigirlo; copia suelta sin imports del repo verificada. Esta ejecución usa el directorio temporal autorizado.
Aceptación: los dos `--selftest` → `selftest ok`; `run_selftests.py` → **run_selftests: 12 OK, 0 FALLO**; comandos exactos y salidas en `correccion1/aceptacion.log`. No se tocaron ni añadieron los cambios concurrentes de `banco_walkforward*`; no hubo fallos que exigieran archive de la suite.
Únicos cambios de aserciones previas: dos literales de versión v1→v2 para versionar ISO; 163 aserciones previas conservadas, 186 actuales (`correccion1/aserciones.log`). Desviación deliberada mantenida: dos fuentes sin regla fallan por (instrumento, intervalo), también con historias disjuntas (`indice_empalme`), para exigir regla de empalme explícita.

| Caso borde | Test que lo cubre |
|---|---|
| USDMXN/USDTRY dobles y sólo scraper; variantes sin renombrar; metales/cripto/X no monetarios fuera | D `prueba_clasificacion_fx`, `prueba_exoticos_v2`; E `prueba_fx_iso_y_tags_v2` |
| MT5 invierno/verano/DST, un minuto antes, justo al cierre, primera 23:01 y republicación; scraper sin cambio | E `prueba_cierre_real_mt5` (CLI en cierre, contraste con publicador y selección de versiones) |
| Recepción MT5 anterior a ts+1d: aceptación pendiente | `reproducir_A12.py` → `correccion1/A12.json`: error explícito Python y DPOL-AVL-002 del motor, 2/2 |
| Tags symbol/interval/source distintos del fichero/filtro | D `prueba_tags_v2`: «fila con tags distintos del filtro»; E `prueba_fx_iso_y_tags_v2`: «tags de la fila distintos de las etiquetas del fichero» |
| Temporal portable, redirección y copia suelta | D `prueba_temporal_selftest`; `standalone/descarga_lago.py --selftest` |
| Fixture sin MT5 conserva hash; cuatro históricos intactos | `comprobar_invariantes.py` → `correccion1/invariantes.json`: 2/2 hashes idénticos contra archive de a98cea8; 4/4 históricos de 0e67465 sin rehacer, originales byte a byte intactos. `lago_cierre_c20261101` sigue afectado por ISSUE-LAGO-FX-1D-CLOSE. SHA-256 de pruebas, informe, código y evidencia en `correccion1/sha256.json`. |

Dudas para revisión: resolver A12 (horas de los ejemplos y disponibilidad `_recv_ts < ts+1d` incompatible con DPOL-AVL-002).
