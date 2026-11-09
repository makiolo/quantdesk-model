# TI-12-MT5 · Cuadre: velas de 1 m agregadas a diario frente a otra fuente diaria

Fecha: 2026-11-09 · Autor: Claude Opus 5.5

Criterio de aceptación de la fila 4 del sprint: «velas de 1 m agregadas a diario cuadran con otra fuente diaria dentro de
tolerancia». Aplazado en la fase A («Lo que queda para la fase B»).

**Resultado.**
- Contra el D1 del propio MT5: **1.507 de 1.507 días completos cuadran exactos** (0 puntos en open, high, low y close) en
  los 28 cruces. Los 369 días con alguna vela de 1 m ausente se informan aparte: 341 cuadran igual. Los 28 que no cuadran
  son todos el 2026-08-06, el primer día del rango, que la descarga corta a las 03:00 del servidor.
- Contra el FX diario del lago (`lago_cierre_c20261101`, yfinance): **1.438 de 1.459 cierres (98,6 %) dentro de
  tolerancia** comparando con el precio de MT5 a las 00:00 UTC del día D, que es la hora de corte del lago estimada con
  los datos. Con el cierre de la sesión de MT5 (17:00 NY) sólo entran 201 (13,8 %), porque son ventanas distintas.
- Dos descargas de 1 m del mismo rango, la segunda con `--refrescar`, dan el mismo `hash_conjunto` y los mismos bytes.
- **Hallazgo sobre el lago** (ver abajo): el «close» del FX diario del lago es el precio de las 00:00 UTC del día D, el
  mismo instante que su open, y no el del final del día.

## Qué hay

| Ruta | Contenido |
|---|---|
| `scripts/cuadre_mt5.py` | CLI `--m1 --d1 --lago [--salida]` y `--selftest`; no toca el terminal |

La agregación usa la regla 1d del publicador sin copiarla: importa `publicador_mt5_lib.nucleo.sesion_1d`. La vela de 1 m
es de la sesión D = fecha del servidor de su apertura, así que D va de las 17:00 NY de D-1 a las 17:00 NY de D. Open es
el de la primera vela de 1 m, high y low son el máximo y el mínimo, y close es el de la última.

El selftest entra solo en la suite: `run_selftests.py` ejecuta todo `scripts/*.py` que mencione `--selftest`.

## Descargas de 1 m (dos, mismo hash)

Terminal abierto por el usuario, enganche sin credenciales (`--sin-credenciales`). Desfase en vivo: EURUSD, GBPUSD y
USDJPY a +2 h, concluyente y coincide con `ny+7`.

| | Ruta | Duración | Trozos pedidos / reutilizados | `hash_conjunto` |
|---|---|---|---|---|
| A | `E:/quantdesk-lab/data/mt5/fx28_m1_20261109` | 434 s | 112 / 0 (caché de 1 m vacía) | `sha256:8a6fa0dc253ab8a330b8dea03916e4b45904204800546e09de5023a55a51389d` |
| B (`--refrescar`) | `E:/quantdesk-lab/data/mt5/fx28_m1_20261109_rep` | 120 s | 112 / 0 | `sha256:8a6fa0dc253ab8a330b8dea03916e4b45904204800546e09de5023a55a51389d` |

- Cada una: 28 series, 2.691.949 velas y 74,3 MiB.
- `extractor_mt5.py --comparar A B`: «identicas (mismo hash_conjunto y mismos bytes)», salida 0. `--comparar` recalcula el
  SHA-256 de cada parquet en el disco.
- Rango: `--desde 2026-08-06 --hasta 2026-11-07`, es decir, de la sesión del jueves 6 de agosto (cortada) a la del
  viernes 6 de noviembre.
  - Con `maxbars` = 100.000 el terminal tiene unas 99.999 velas de 1 m por símbolo. En EURUSD empiezan el 2026-08-03 a
    las 20:54 UTC (inventario de las 11:00 UTC).
  - Esa ventana avanza con cada vela nueva. Por eso el rango empieza dos días después, para que dos descargas separadas
    por horas pidan lo mismo.
  - El 2026-11-07 excluido deja fuera la sesión en curso.
- Registros: `E:/quantdesk-lab/runs/TI-12-MT5/descarga_20261109T161926Z_30856.json` (A) y
  `descarga_20261109T162646Z_11092.json` (B). Salida de consola en `m1_descarga_a.log` y `m1_descarga_b.log`, en la misma
  carpeta.

**Horario del broker en 1 m** (moda de la ventana, el mismo en los 28 cruces): de 00:00 a 23:58 del servidor de lunes a
jueves (1.439 velas) y de 00:00 a 23:56 el viernes (1.437 velas). No hay vela a las 23:59.

**Observación sobre `cierre_semanal` en 1 m.**
- La última vela del viernes acaba a las 23:57 del servidor, que son las 16:57 NY. El método del cierre del viernes busca
  las 17:00 exactas, así que en 1 m da coherencia 0 con todas las reglas.
- El manifest lo marca «no concluyente» y «coherente»: la descarga no se para y no avisa.
- La regla `ny+7` la confirman la detección en vivo y el cuadre exacto con el D1. No toco el extractor.

## Cuadre contra el D1 de MT5

D1: `E:/quantdesk-lab/data/mt5/continuo_1d_20261109` (`hash_conjunto`
`sha256:a503bb757ce53481405a1f161feed542e1c049df0319116dafff6dcc4a208441`). Los días se emparejan por la sesión D, con la
misma regla para las dos series.

**Día completo**, decidido sin mirar precios para que el cuadre no sea circular:
- empieza y acaba en el horario del broker de ese día de la semana;
- no le falta ningún minuto dentro: n = último − primero + 1.

**Tolerancia: 0 puntos** en open, high, low y close. El punto se infiere de los precios: 1e-5, y 1e-3 en los JPY, igual
que los dígitos del inventario.
- Justificación: el D1 y las velas de 1 m del terminal se construyen con el mismo flujo de ticks Bid. Si están todos los
  minutos, el open es el primer tick, el close el último y high y low son extremos del mismo conjunto. Cualquier
  diferencia sólo puede venir de velas de 1 m ausentes, y esos días se clasifican aparte.

**Resultado.**
- **28 cruces, 1.876 días emparejados**: 67 por par, del 2026-08-06 al 2026-11-06, sin ningún día del D1 sin 1 m en el
  rango.
- **1.507 completos: los 1.507 cuadran exactos.** El máximo es 0 puntos en los cuatro campos y en todos los pares.
- **369 incompletos**; 341 de ellos cuadran igual. Velas de 1 m que faltan:
  - 1 a 9 en la gran mayoría de los días, casi siempre en los primeros minutos tras las 00:00 del servidor. Es el
    rollover de las 17:00 NY: spreads abiertos y minutos sin tick. EURJPY y EURCHF los pierden más a menudo, y por eso
    sólo tienen 15 y 33 días completos.
  - Huecos del servidor que afectan a los 28 cruces a la vez: 2026-09-09, 09-15, 09-22, 09-24, 10-28 (22 minutos, de
    las 21:32 a las 21:54 UTC del 27), 11-04, 11-05 y 11-06.
  - En esta ventana ningún minuto vacío se llevó el open, el máximo, el mínimo ni el close del día: fuera del 6 de
    agosto, los 341 incompletos cuadran exactos.
- **28 incompletos no cuadran, todos el 2026-08-06.** Les faltan los 180 minutos de las 00:00 a las 03:00 del servidor
  (de las 21:00 a las 24:00 UTC del 5), porque el rango empieza a las 00:00 UTC del 6.
  - El open difiere en todos (hasta 356 puntos en EURNZD) y el low en algunos (hasta 283 puntos en GBPAUD).
  - Es exactamente lo que se espera de una sesión cortada.

## Cuadre contra el FX diario del lago

**Lago:** `E:/quantdesk-lab/datasets/TI-02-DATA/lago_cierre_c20261101/lago_ohlcv_1d.parquet`
- SHA-256 del fichero `f783a1777719ffd1f7ceff5a00bff1fe0638b584d81234f295500647bd7ed3c8`; `dataset_hash`
  `sha256:aff96e6c…`;
- yfinance, 28 cruces, `ts_ms` = 00:00 UTC de D, hasta el 2026-10-30.

**Qué se compara:** el cierre, en error relativo |ln(lago / MT5)|. Sólo días completos de MT5; son 1.459 días con
lago.
- `cierre_sesion`: el close de la sesión de MT5, a las 17:00 NY de D.
- `cierre_corte`: el precio de MT5 (el close de la última vela de 1 m cerrada) a la hora de corte del lago.
  - La hora de corte se estima con los datos: la que minimiza la mediana del error de los 28 pares, en una rejilla de
    15 min de D-1 12:00 a D+1 06:00 UTC.
  - Sale **D 00:00 UTC**, con una mediana de 0,81 pb. A ±15 min, 1,51 y 2,48 pb. A las 21:00 UTC de D (17:00 NY en
    verano), 19,3 pb; a D+1 00:00 UTC, 19,8 pb.

**Tolerancia por par: 0,10 × rango diario mediano del par**, (high − low)/close de las sesiones completas de MT5 en la
ventana.
- Según el par, son de 2,8 pb (EURGBP) a 7,2 pb (EURJPY, NZDUSD).
- Justificación: el corte sale de una rejilla de 15 min, así que el desfase horario admisible es de hasta unos 15 min. El
  desplazamiento típico del precio en Δt es ≈ rango diario × √(Δt / 1 día), y √(15/1440) ≈ 0,10.
- También absorbe Bid frente a la cotización de yfinance: el medio spread mediano de esta cuenta es < 0,2 pb en los 28
  cruces (campo `spread` de las velas de 1 m, que es indicativo).
- Es de 4 a 11 veces el error mediano observado en el corte y de 2 a 5 veces menor que el error mediano con el cierre de
  sesión. Separa bien una misma ventana de una ventana distinta.

**Resultado por par.**

| Par | Días D1 | Completos / dentro | Incompletos / dentro | Máx. pts O/H/L/C (todos; los completos son 0/0/0/0) | Rango med. (pb) | Tol. lago (pb) | Días lago | Corte D 00:00 UTC dentro | Corte med. / máx. (pb) | Cierre sesión dentro | Sesión med. (pb) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | 67 | 56 / 56 | 11 / 10 | 13/0/0/0 | 48.18 | 4.82 | 54 | 52 (96 %) | 0.66 / 5.94 | 9 (17 %) | 17.98 |
| AUDCHF | 67 | 56 / 56 | 11 / 10 | 8/0/16/0 | 63.19 | 6.32 | 55 | 54 (98 %) | 0.87 / 9.56 | 7 (13 %) | 21.02 |
| AUDJPY | 67 | 55 / 55 | 12 / 11 | 76/0/0/0 | 69.21 | 6.92 | 53 | 53 (100 %) | 0.87 / 3.29 | 3 (6 %) | 27.39 |
| AUDNZD | 67 | 58 / 58 | 9 / 8 | 64/0/48/0 | 51.69 | 5.17 | 56 | 53 (95 %) | 0.75 / 8.62 | 10 (18 %) | 15.28 |
| AUDUSD | 67 | 58 / 58 | 9 / 8 | 6/0/0/0 | 58.87 | 5.89 | 56 | 56 (100 %) | 0.63 / 5.59 | 5 (9 %) | 24.87 |
| CADCHF | 67 | 58 / 58 | 9 / 8 | 10/0/24/0 | 54.97 | 5.5 | 56 | 43 (77 %) | 1.19 / 10.95 | 6 (11 %) | 21.91 |
| CADJPY | 67 | 56 / 56 | 11 / 10 | 32/0/46/0 | 59.98 | 6.0 | 54 | 54 (100 %) | 0.7 / 3.31 | 8 (15 %) | 20.77 |
| CHFJPY | 67 | 57 / 57 | 10 / 9 | 67/0/0/0 | 54.77 | 5.48 | 55 | 55 (100 %) | 0.86 / 4.84 | 10 (18 %) | 20.28 |
| EURAUD | 67 | 43 / 43 | 24 / 23 | 119/0/165/0 | 41.04 | 4.1 | 42 | 42 (100 %) | 0.59 / 1.99 | 3 (7 %) | 19.6 |
| EURCAD | 67 | 57 / 57 | 10 / 9 | 67/3/0/0 | 37.53 | 3.75 | 56 | 56 (100 %) | 0.6 / 3.33 | 5 (9 %) | 15.91 |
| EURCHF | 67 | 33 / 33 | 34 / 33 | 23/0/46/0 | 47.95 | 4.8 | 32 | 32 (100 %) | 0.54 / 1.93 | 4 (12 %) | 21.43 |
| EURGBP | 67 | 58 / 58 | 9 / 8 | 26/0/0/0 | 27.95 | 2.8 | 56 | 56 (100 %) | 0.36 / 2.11 | 11 (20 %) | 11.25 |
| EURJPY | 67 | 15 / 15 | 52 / 51 | 52/0/21/0 | 71.54 | 7.15 | 15 | 15 (100 %) | 0.65 / 1.86 | 4 (27 %) | 25.36 |
| EURNZD | 67 | 43 / 43 | 24 / 23 | 356/0/93/0 | 54.24 | 5.42 | 42 | 42 (100 %) | 1.43 / 4.16 | 7 (17 %) | 16.99 |
| EURUSD | 67 | 57 / 57 | 10 / 9 | 39/0/0/0 | 47.78 | 4.78 | 56 | 56 (100 %) | 0.46 / 4.35 | 8 (14 %) | 17.4 |
| GBPAUD | 67 | 55 / 55 | 12 / 11 | 97/0/283/0 | 49.16 | 4.92 | 53 | 53 (100 %) | 0.73 / 2.06 | 10 (19 %) | 15.78 |
| GBPCAD | 67 | 58 / 58 | 9 / 8 | 37/0/0/0 | 39.73 | 3.97 | 56 | 56 (100 %) | 0.91 / 2.66 | 8 (14 %) | 14.25 |
| GBPCHF | 67 | 57 / 57 | 10 / 9 | 7/0/68/0 | 49.23 | 4.92 | 55 | 55 (100 %) | 0.82 / 3.47 | 7 (13 %) | 19.29 |
| GBPJPY | 67 | 56 / 56 | 11 / 10 | 124/0/95/0 | 55.65 | 5.57 | 54 | 54 (100 %) | 0.65 / 3.23 | 14 (26 %) | 20.94 |
| GBPNZD | 67 | 58 / 58 | 9 / 8 | 118/0/193/0 | 54.87 | 5.49 | 56 | 55 (98 %) | 1.13 / 8.1 | 8 (14 %) | 18.8 |
| GBPUSD | 67 | 58 / 58 | 9 / 8 | 22/0/0/0 | 45.63 | 4.56 | 56 | 56 (100 %) | 0.4 / 2.51 | 6 (11 %) | 23.24 |
| NZDCAD | 67 | 58 / 58 | 9 / 8 | 11/0/0/0 | 57.14 | 5.71 | 56 | 55 (98 %) | 1.32 / 7.62 | 5 (9 %) | 22.27 |
| NZDCHF | 67 | 58 / 58 | 9 / 8 | 3/0/2/0 | 63.74 | 6.37 | 56 | 56 (100 %) | 1.48 / 3.87 | 12 (21 %) | 15.16 |
| NZDJPY | 67 | 58 / 58 | 9 / 8 | 54/0/0/0 | 69.59 | 6.96 | 56 | 56 (100 %) | 1.06 / 3.71 | 8 (14 %) | 28.24 |
| NZDUSD | 67 | 58 / 58 | 9 / 8 | 3/0/0/0 | 71.48 | 7.15 | 56 | 56 (100 %) | 1.59 / 4.92 | 6 (11 %) | 32.18 |
| USDCAD | 67 | 58 / 58 | 9 / 8 | 1/0/0/0 | 41.27 | 4.13 | 56 | 56 (100 %) | 0.42 / 1.44 | 6 (11 %) | 20.28 |
| USDCHF | 67 | 58 / 58 | 9 / 8 | 20/0/4/0 | 61.97 | 6.2 | 56 | 56 (100 %) | 0.67 / 3.69 | 3 (5 %) | 25.16 |
| USDJPY | 67 | 57 / 57 | 10 / 9 | 117/0/33/0 | 57.03 | 5.7 | 55 | 55 (100 %) | 0.57 / 3.5 | 8 (15 %) | 15.41 |
| **Total** | **1.876** | **1.507 / 1.507** | **369 / 341** | | | | **1.459** | **1.438 (98,6 %)** | | **201 (13,8 %)** | |

«Máx. pts (todos)» sale siempre del 2026-08-06, la sesión cortada.

**Pares por debajo del 95 %.** Sólo CADCHF: 43 de 56 (77 %), con mediana de 1,19 pb, p90 de 8,7 pb y máximo de 10,9 pb
(el 2026-10-09) frente a una tolerancia de 5,5 pb. Después están AUDNZD (95 %) y AUDCAD (96 %). El error mediano es tan
bajo como en los demás; lo que hay son colas más gruesas. Una posible explicación, sin verificar, es que yfinance
componga ese cruce o lo cotice con menos frecuencia. No es un defecto de MT5: su D1 cuadra exacto.

## Hallazgo: el «close» diario del lago es el precio de las 00:00 UTC de D

El FX diario del lago (yfinance, vía `fx_spot_scraper.run_daily`) es una vela del día UTC D con un close que no es del
final del día:

| Campo del lago | Mejor contraparte en MT5 (m1) | Error mediano (O/H/L: mediana de las medianas por par) | Dentro de la tolerancia |
|---|---|---|---|
| open | open de la primera vela de 1 m del día UTC D (00:00 UTC) | 0,8 pb | 1.447 / 1.459 |
| high | máximo de [D 00:00, D+1 00:00) UTC | 1,1 pb | 1.306 / 1.459 |
| low | mínimo de [D 00:00, D+1 00:00) UTC | 1,4 pb | 1.085 / 1.459 |
| close | precio a las **00:00 UTC de D**, el mismo instante que el open | 0,8 pb | 1.438 / 1.459 |
| close | precio a las 00:00 UTC de D+1 (el fin del día UTC) | 19,8 pb | — |

Por eso el 41,7 % de las filas del lago tiene open = close exacto.

**Consecuencia para TS-00-BENCH.**
- Lo que el banco llama cierre de D es el precio del principio de D, unas 24 h antes de lo que dice su nombre.
- No hay look-ahead: la disponibilidad proxy `ts` + 1 d es conservadora, porque el dato existe desde `ts`.
- Los rendimientos log(close_D / close_D-1) son rendimientos de 00:00 a 00:00 UTC, desplazados un día.
- Lo dejo anotado para que la raíz decida si TI-02-DATA o TS-00-BENCH lo declaran. No cambio nada fuera de TI-12-MT5.

## Comandos reproducibles

```
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --descargar --sin-credenciales --simbolos @fx28 --periodos m1 --desde 2026-08-06 --hasta 2026-11-07 --salida E:/quantdesk-lab/data/mt5/fx28_m1_20261109
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --descargar --sin-credenciales --simbolos @fx28 --periodos m1 --desde 2026-08-06 --hasta 2026-11-07 --salida E:/quantdesk-lab/data/mt5/fx28_m1_20261109_rep --refrescar
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --comparar E:/quantdesk-lab/data/mt5/fx28_m1_20261109 E:/quantdesk-lab/data/mt5/fx28_m1_20261109_rep
.venv/Scripts/python -X utf8 scripts/cuadre_mt5.py --m1 E:/quantdesk-lab/data/mt5/fx28_m1_20261109 --d1 E:/quantdesk-lab/data/mt5/continuo_1d_20261109 --lago E:/quantdesk-lab/datasets/TI-02-DATA/lago_cierre_c20261101/lago_ohlcv_1d.parquet --salida E:/quantdesk-lab/runs/TI-12-MT5/cuadre/fx28_m1_20261109
```

- El cuadre no necesita el terminal.
- Salida 0: todos los días completos cuadran con el D1.
- Escribe `cuadre.json` (por par: días, incompletos con las velas que faltan y los puntos de cada campo, horario del
  broker, errores del lago y la curva de cortes) y `cuadre.md` (la tabla de arriba) en
  `E:/quantdesk-lab/runs/TI-12-MT5/cuadre/fx28_m1_20261109/`.
- `cuadre.json` sólo cambia entre ejecuciones en `generado_utc`.
- Las descargas sólo son reproducibles mientras el rango siga dentro de las 100.000 velas de 1 m del terminal, es decir,
  hasta unos días después del 2026-11-09. Más tarde hay que mover `--desde`.

## Evidencia (selftest)

`.venv/Scripts/python -X utf8 scripts/cuadre_mt5.py --selftest` termina en `selftest ok`, sin terminal ni red. Usa tres
semanas sintéticas con el cambio de hora de EE. UU. del 1 de noviembre en medio:
- la agregación da las sesiones del servidor con la regla del publicador:
  - apertura del viernes 30 de octubre a las 21:00 UTC del 29;
  - apertura del lunes 2 de noviembre a las 22:00 UTC del domingo;
  - mismo `ts` que `sesion_1d`;
- el cuadre contra su D1 exacto da 0 puntos y 15 de 15 días completos;
- sin la primera vela de un viernes y sin la vela del máximo de un martes, los dos días salen incompletos (falta 1
  vela) y el high del martes baja lo esperado; los otros 13 siguen exactos;
- un lago sintético que cierra a las 23:00 UTC: el corte estimado es D 23:00 UTC con error 0. El precio en un instante
  anterior a la primera vela es nulo;
- de punta a punta con ficheros: salida 0 e informe escrito, y un par sin lago sale como `null`. Un D1 con un high
  distinto en un día completo da salida 1.
