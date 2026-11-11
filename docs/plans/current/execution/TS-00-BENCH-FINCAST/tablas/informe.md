# TS-00-BENCH: banco walk-forward (HMM del motor, GARCH(1,1), Chronos-2 y Toto en zero-shot)

- Generado por `scripts/banco_walkforward.py --informe` el 2026-11-11T10:09:36Z a partir de las salidas de las corridas (`meta.json`, `metricas.csv`, `predicciones.parquet` en `E:/quantdesk-lab/runs/TS-00-BENCH/`). Comando: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --informe E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101 E:/quantdesk-lab/runs/TS-00-BENCH/binance_c20261101 --toto E:/quantdesk-lab/runs/TS-00-BENCH/toto_lago_cierre_c20261101 E:/quantdesk-lab/runs/TS-00-BENCH/toto_binance_c20261101 --fincast E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/fincast_fx E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/fincast_binance --repeticion E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/repeticion_fx E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/repeticion_binance --destino docs/plans/current/execution/TS-00-BENCH-FINCAST/tablas`.
- Selftest: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --selftest` (sin red: el selftest bloquea los sockets; sin datos reales; Chronos-2 sustituido por un modelo trivial con la misma interfaz; Toto, por su trabajador real en modo `--falso` lanzado como subproceso, y un venv de Toto inexistente deja Toto SALTADO sin romper la corrida).
- Motor: **quantdesk 69fdb39d** (commit `69fdb39d0b67969dbdafa77f5da656511342f175`). Semilla: **20261101**. Solo CPU.
- **Tabla de cabecera: `lago_cierre_c20261101`** (FX diario del lago; decision del usuario del 2026-11-09). Su disponibilidad es un **proxy** (`available_at_ms` nulo, `default_lag_ms` = 0: valores que qn recibio despues del corte) y cada tabla y cifra suya lleva la etiqueta «proxy». `binance_c20261101` es la segunda tabla.
- Datasets: los dos que fija la ficha. De los otros dos de TI-02-DATA, `lago_c20261101` (estricto) tiene las tablas OHLCV vacias tras el corte (0 filas; no hay serie que evaluar) y `lago_c20261107` no esta en la ficha.
- No se fijan umbrales de exito (TS-00-OBJ). Las cifras son descriptivas.

## Resumen por modelo

Medianas entre activos de cada metrica; «CRPS rel.» es la mediana del cociente CRPS del modelo / CRPS de GARCH en el mismo activo (< 1 mejor que GARCH). «Gana» cuenta los activos en que el modelo tiene el menor CRPS (y el menor QLIKE). «Kupiec/Chr. p<0,05» cuenta activos en que el test rechaza al 5 %. Excedencias esperadas: 1 % en cada cola.

### lago_cierre_c20261101 (proxy) — tabla de cabecera

| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | hmm | 28 | 0.002081 | 1 | 0.0001319 | 0.0001122 | 0.0162 | 0.0121 | 2/2 | 1/0 | -10.01 | 9 | 12 |
| 1 | garch | 28 | 0.002078 | 1 | 0.000132 | 0.0001172 | 0.0162 | 0.00607 | 3/2 | 0/0 | -10.01 | 18 | 8 |
| 1 | chronos2 | 28 | 0.002139 | 1.03 | 0.0001371 | 0.0001358 | 0.00202 | 0.00405 | 14/13 | 0/0 | -10.01 | 1 | 8 |
| 5 | hmm | 28 | 0.004368 | 1.02 | 0.0002753 | 0.0002422 | 0.0081 | 0.00405 | 1/0 | 0/0 | -8.41 | 3 | 13 |
| 5 | garch | 28 | 0.004289 | 1 | 0.0002426 | 0.0002504 | 0.0081 | 0 | 2/0 | 0/0 | -8.402 | 16 | 11 |
| 5 | chronos2 | 28 | 0.004348 | 1.01 | 0.0002793 | 0.0002379 | 0.00405 | 0.00202 | 1/0 | 0/0 | -8.357 | 9 | 4 |
| 20 | hmm | 28 | 0.009154 | 1.04 | 0.0005084 | 0.0004654 | 0.00202 | 0 | 0/0 | 0/0 | -7.035 | 1 | 13 |
| 20 | garch | 28 | 0.008954 | 1 | 0.0004498 | 0.0004649 | 0.00405 | 0 | 0/0 | 0/0 | -7.009 | 8 | 12 |
| 20 | chronos2 | 28 | 0.008552 | 0.972 | 0.0005635 | 0.0005342 | 0 | 0 | 0/0 | 0/0 | -7.012 | 19 | 3 |

### binance_c20261101

| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | hmm | 10 | 0.01814 | 1 | 0.001139 | 0.001252 | 0.00836 | 0.00836 | 1/0 | 0/0 | -5.706 | 4 | 5 |
| 1 | garch | 10 | 0.01824 | 1 | 0.001177 | 0.001308 | 0.00696 | 0.00836 | 0/0 | 0/0 | -5.659 | 6 | 3 |
| 1 | chronos2 | 10 | 0.01984 | 1.05 | 0.001334 | 0.001314 | 0.00557 | 0.00696 | 1/1 | 0/0 | -5.685 | 0 | 2 |
| 5 | hmm | 10 | 0.04201 | 1 | 0.002598 | 0.003082 | 0.0111 | 0.0139 | 0/1 | 0/0 | -3.992 | 4 | 5 |
| 5 | garch | 10 | 0.04204 | 1 | 0.002657 | 0.003005 | 0.00836 | 0.0139 | 0/2 | 0/0 | -3.958 | 5 | 4 |
| 5 | chronos2 | 10 | 0.04311 | 1.01 | 0.002806 | 0.003302 | 0.0139 | 0.0237 | 1/6 | 0/0 | -3.831 | 1 | 1 |
| 20 | hmm | 10 | 0.09119 | 1.01 | 0.00498 | 0.005222 | 0.00418 | 0.0153 | 0/0 | 0/1 | -2.546 | 2 | 6 |
| 20 | garch | 10 | 0.09004 | 1 | 0.005077 | 0.005261 | 0 | 0.00975 | 0/1 | 0/0 | -2.548 | 5 | 2 |
| 20 | chronos2 | 10 | 0.09151 | 1.01 | 0.005208 | 0.0055 | 0.00696 | 0.0251 | 0/0 | 0/2 | -2.452 | 3 | 2 |

## Toto frente a HMM, GARCH y Chronos-2 (submuestra de origenes)

Toto cuesta mucho mas CPU por origen que los otros tres (ver presupuesto de CPU), asi que no cabe en 2 h con la rejilla completa: se corre sobre una submuestra declarada de origenes (`--cada N`: uno de cada N origenes validos de cada activo, todos los activos) y aqui los CUATRO modelos se comparan sobre exactamente esos origenes (las predicciones de HMM, GARCH y Chronos-2 son las de la corrida completa: cada origen es independiente y reproducible). Las tablas de arriba (3 modelos, rejilla completa) no cambian.

### lago_cierre_c20261101 (proxy) — tabla de cabecera: uno de cada 5 origenes (1400 pares)

| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | hmm | 28 | 0.002124 | 1 | 0.0001225 | 0.0001099 | 0.02 | 0 | 3/0 | 0/0 | -10.01 | 9 | 10 |
| 1 | garch | 28 | 0.00214 | 1 | 0.0001226 | 0.0001128 | 0.02 | 0 | 5/1 | 0/0 | -10.01 | 10 | 11 |
| 1 | chronos2 | 28 | 0.00224 | 1.03 | 0.0001486 | 0.0001328 | 0 | 0 | 0/0 | 0/0 | -9.957 | 8 | 5 |
| 1 | toto | 28 | 0.002255 | 1.04 | 0.0001611 | 0.0001521 | 0.04 | 0.04 | 9/5 | 0/0 | -9.748 | 1 | 2 |
| 5 | hmm | 28 | 0.004456 | 1.01 | 0.0002679 | 0.0002293 | 0 | 0 | 1/0 | 0/0 | -8.407 | 1 | 15 |
| 5 | garch | 28 | 0.004305 | 1 | 0.0002357 | 0.000237 | 0.02 | 0 | 2/0 | 0/0 | -8.403 | 13 | 9 |
| 5 | chronos2 | 28 | 0.004456 | 1.01 | 0.0002958 | 0.000235 | 0 | 0 | 1/0 | 0/0 | -8.364 | 9 | 4 |
| 5 | toto | 28 | 0.004588 | 1.03 | 0.0005355 | 0.0003643 | 0 | 0 | 1/0 | 0/0 | -8.281 | 5 | 0 |
| 20 | hmm | 28 | 0.009257 | 1.03 | 0.0005198 | 0.0004752 | 0 | 0 | 0/0 | 0/0 | -7.035 | 0 | 14 |
| 20 | garch | 28 | 0.008808 | 1 | 0.0004428 | 0.0004707 | 0 | 0 | 0/0 | 0/0 | -7.009 | 10 | 12 |
| 20 | chronos2 | 28 | 0.008296 | 0.967 | 0.0005673 | 0.0005371 | 0 | 0 | 0/0 | 0/0 | -7.013 | 14 | 2 |
| 20 | toto | 28 | 0.008744 | 1.06 | 0.002223 | 0.001384 | 0 | 0 | 0/0 | 0/0 | -6.908 | 4 | 0 |

### binance_c20261101: uno de cada 10 origenes (360 pares)

| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | hmm | 10 | 0.01689 | 1 | 0.001005 | 0.001163 | 0 | 0 | 0/0 | 0/0 | -5.754 | 5 | 5 |
| 1 | garch | 10 | 0.01692 | 1 | 0.000992 | 0.001118 | 0 | 0 | 0/0 | 0/0 | -5.798 | 4 | 1 |
| 1 | chronos2 | 10 | 0.01855 | 1.04 | 0.001205 | 0.001418 | 0 | 0 | 0/0 | 0/0 | -5.778 | 0 | 2 |
| 1 | toto | 10 | 0.01787 | 1.05 | 0.001071 | 0.001151 | 0 | 0.0139 | 0/1 | 0/0 | -5.705 | 1 | 2 |
| 5 | hmm | 10 | 0.0455 | 0.996 | 0.002288 | 0.003672 | 0 | 0.0278 | 0/0 | 0/0 | -4.104 | 2 | 5 |
| 5 | garch | 10 | 0.04561 | 1 | 0.00239 | 0.004944 | 0 | 0.0278 | 0/0 | 0/0 | -4.058 | 2 | 3 |
| 5 | chronos2 | 10 | 0.04456 | 1 | 0.002228 | 0.005236 | 0 | 0.0556 | 0/1 | 0/1 | -3.909 | 2 | 1 |
| 5 | toto | 10 | 0.04478 | 1.01 | 0.00247 | 0.005679 | 0 | 0.0278 | 0/0 | 0/0 | -3.869 | 4 | 1 |
| 20 | hmm | 10 | 0.09885 | 0.998 | 0.005052 | 0.00488 | 0.0139 | 0 | 0/0 | 0/0 | -2.394 | 4 | 7 |
| 20 | garch | 10 | 0.09683 | 1 | 0.005364 | 0.004959 | 0 | 0 | 0/0 | 0/0 | -2.341 | 2 | 2 |
| 20 | chronos2 | 10 | 0.09698 | 1.02 | 0.005915 | 0.005114 | 0.0139 | 0.0278 | 0/0 | 0/0 | -2.208 | 2 | 1 |
| 20 | toto | 10 | 0.09754 | 1.04 | 0.00572 | 0.006936 | 0.0278 | 0.0278 | 0/0 | 0/0 | -2.142 | 2 | 0 |

Anchura de las bandas predichas sobre esos mismos origenes (en log-rendimiento): mediana de la banda 10-90 % (`q90 - q10`) y de la banda 1-99 % (`q99 - q01`), mediana del cociente entre ambas (cola; una normal da 1,82) y percentil 99 de la banda 1-99 % entre origenes (colas explosivas).

| lago_cierre_c20261101 (proxy) h | modelo | banda 10-90 % | banda 1-99 % | cola (1-99 / 10-90) | banda 1-99 % p99 |
|---|---|---|---|---|---|
| 1 | chronos2 | 0.00942 | 0.02667 | 2.76 | 0.06376 |
| 1 | garch | 0.009254 | 0.01937 | 2.08 | 0.03831 |
| 1 | hmm | 0.009323 | 0.01942 | 2.01 | 0.0376 |
| 1 | toto | 0.007259 | 0.01634 | 2.14 | 0.05948 |
| 5 | chronos2 | 0.02025 | 0.0466 | 2.28 | 0.08996 |
| 5 | garch | 0.02174 | 0.04358 | 2 | 0.08289 |
| 5 | hmm | 0.02209 | 0.04448 | 1.97 | 0.09137 |
| 5 | toto | 0.01862 | 0.05487 | 2.91 | 0.6639 |
| 20 | chronos2 | 0.04167 | 0.1025 | 2.45 | 0.2194 |
| 20 | garch | 0.04545 | 0.08822 | 1.93 | 0.1604 |
| 20 | hmm | 0.04649 | 0.09008 | 1.91 | 0.1992 |
| 20 | toto | 0.03813 | 0.2213 | 5.27 | 4.425 |

| binance_c20261101 h | modelo | banda 10-90 % | banda 1-99 % | cola (1-99 / 10-90) | banda 1-99 % p99 |
|---|---|---|---|---|---|
| 1 | chronos2 | 0.08471 | 0.1995 | 2.31 | 0.7449 |
| 1 | garch | 0.07366 | 0.1854 | 2.51 | 0.397 |
| 1 | hmm | 0.07448 | 0.1792 | 2.36 | 0.3619 |
| 1 | toto | 0.069 | 0.1711 | 2.46 | 0.4872 |
| 5 | chronos2 | 0.1686 | 0.37 | 2.12 | 1.037 |
| 5 | garch | 0.1794 | 0.4273 | 2.3 | 0.79 |
| 5 | hmm | 0.1789 | 0.4323 | 2.28 | 0.784 |
| 5 | toto | 0.1648 | 0.3959 | 2.4 | 1.435 |
| 20 | chronos2 | 0.3581 | 0.8143 | 2.26 | 2.064 |
| 20 | garch | 0.4044 | 0.9197 | 2.26 | 1.619 |
| 20 | hmm | 0.4206 | 0.9239 | 2.13 | 1.552 |
| 20 | toto | 0.3608 | 0.8903 | 2.47 | 3.733 |

## Diseno del walk-forward

| dataset | tabla | `dataset_hash` | ventana W (barras) | rejilla de origenes | horizontes (barras) | activos | pares activo-origen evaluados | omitidos (sin W barras / sin objetivo / sin barra nueva) |
|---|---|---|---|---|---|---|---|---|
| lago_cierre_c20261101 (proxy) | `lago_ohlcv_1d` | `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356` | 250 | 00:00 UTC de 2025-10-20 a 2026-10-03, cada 1 d (349 instantes) | 1, 5, 20 | 28 | 6916 | 56 / 0 / 2800 |
| binance_c20261101 | `binance_ohlcv_1d` | `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744` | 1000 | 00:00 UTC de 2023-11-01 a 2026-10-12, cada 3 d (359 instantes) | 1, 5, 20 | 10 | 3590 | 0 / 0 / 0 |

- Unidad de tiempo: la barra diaria (observacion). h = 1, 5 y 20 barras: en cripto (24/7) son dias naturales; en FX, sesiones (h = 5 es una semana de mercado). Las barras de 1 h no se usan: en el lago solo hay desde 2026-10-18 (demasiado corto) y en Binance quedan para una fase posterior.
- Objetivo: rendimiento logaritmico acumulado y = ln(C_{k+h} / C_k), con k la ultima barra visible en el origen y C el cierre. Cada modelo da los 21 cuantiles de y (niveles de Chronos-2: 0,01, 0,05, 0,10, ..., 0,95, 0,99).
- Origenes: la rejilla fija de la tabla (00:00 UTC). En cada origen y activo se omite el par si no hay W barras visibles, si no existen las 20 barras siguientes (objetivo) o si desde el origen anterior no ha llegado ninguna barra nueva (fines de semana del FX: repetiria la misma informacion). La ventana es movil: los modelos se recalibran en cada origen con las ultimas W barras visibles.
- Comparacion justa: las metricas de cada activo y horizonte se calculan solo sobre los origenes en que los tres modelos dieron prevision; los fallos se cuentan en la seccion de reproducibilidad.
- Tests de VaR: con origenes mas juntos que h las ventanas se solapan y las excedencias no son independientes; por eso Kupiec y Christoffersen se calculan sobre la submuestra sin solape (un origen se conserva si su barra k esta al menos h barras despues de la del ultimo conservado; columna `n_test`). Las tasas de excedencia y el resto de metricas usan todos los origenes. Con h = 20 la submuestra es pequena (del orden de 12 a 50 por activo) y los tests tienen poca potencia.

### Garantia de no look-ahead

- Disponibilidad de cada fila = `available_at_ms` si no es nulo; si lo es, `ts_ms + interval_ms + default_lag_ms` del manifest (el mecanismo del motor). Binance: cierre declarado por la fuente en cada fila. Lago (proxy): `available_at_ms` nulo y `default_lag_ms` = 0, es decir, el cierre de la barra. Una fila sin ninguna de las dos hace fallar la carga.
- En el origen t, `datos.cortar` selecciona las filas con disponibilidad <= t, las ordena por `ts_ms` y pasa al modelo una copia de solo lectura de los ultimos W cierres; el modelo no recibe el DataFrame, ni indices, ni el objetivo. El objetivo y la varianza realizada se calculan aparte con las barras de `ts_ms` posterior a la ultima visible. Un dato tardio (ts anterior pero publicado despues de t) queda fuera del contexto.
- Selftest (`--selftest`): una barra con `ts` anterior al origen pero publicada despues, multiplicada por 1000, no entra en el contexto y no cambia ni un bit las predicciones de HMM, GARCH y el sustituto de Chronos-2; con `available_at_ms` nulo, `default_lag_ms` 0 hace visible la barra que cierra en el origen y 1 ms la deja fuera; sin ninguno de los dos la carga falla.
- Limite del proxy: en `lago_cierre_c20261101` los valores son la version que qn recibio despues del corte (ver el informe de TI-02-DATA), asi que el dataset no es causal en sentido estricto aunque el corte por disponibilidad lo sea.

### Modelos

- **hmm**: HMM del motor por los bindings Python: plantilla de K = 3 estados `GbmP` (el menor de los K candidatos {3, 4} del HMM de FX del motor; sin seleccion por BIC en el univariante), Baum-Welch con `HmmCalibrationOptions` por defecto (200 iteraciones, 5 reinicios, `init_mode` quantile_volatility) salvo `seed`, sobre los precios con malla de observaciones (dt = 1/252 por barra). 1000 caminos condicionados al final de la calibracion con `Engine.open_stream(res, semilla_j, policy="from_calibration_end").advance_many([dt] * 20)`, un camino por stream; se comprueba que s0 de la calibracion es el ultimo precio del contexto.
- **garch**: `arch` GARCH(1,1), media constante, innovaciones t de Student, sobre 100 x rendimientos log de la ventana; 1000 caminos simulados a 20 pasos con una t estandarizada sembrada (`rng=`; `arch` 8 ignora `random_state` en la simulacion, lo detecto el selftest).
- **chronos2**: `amazon/chronos-2` revision `29ec3766d36d6f73f0696f85560a422f50e8498c`, zero-shot, CPU, float32, `predict_quantiles` sobre el log-precio de la ventana (W barras), 20 pasos, cuantiles nativos menos el ultimo log-precio. Lote de una serie por llamada: con lotes mayores las salidas cambian en ~1e-6 segun la composicion del lote (medido), y con lote 1 un subconjunto reproduce bit a bit la corrida completa. `torch.use_deterministic_algorithms(True)`; dos llamadas iguales dan el mismo resultado (medido).
- **toto**: `Datadog/Toto-Open-Base-1.0` revision `0411ceb27bdf7fc3e4892e99edc8ad08192dc3c5`, zero-shot, CPU, en un subproceso con el venv aparte `E:/quantdesk-lab/venvs/toto` (`scripts/banco_walkforward_lib/toto_trabajador.py`, protocolo de lineas JSON; los precios viajan como float64 sin perdida). Mismo contrato que Chronos-2: contexto = log-precio de la ventana (W barras), 256 trayectorias a 20 pasos (`TotoForecaster.forecast`, `samples_per_batch` = numero de muestras, `torch.manual_seed(semilla)` antes de cada prevision, `use_deterministic_algorithms(True)`, 2 hilos), cuantiles empiricos de log P_{t+h} - log P_t. Marcas de tiempo sinteticas a 1 dia por barra. El CPU del subproceso lo mide el trabajador y se suma al de Toto. Sin el venv, `--modelos ...,toto` deja Toto SALTADO y la corrida sigue.
- Cuantiles de los modelos por muestras: `numpy.quantile` (lineal) de las muestras en los 21 niveles.

### Metricas y estimador de vol realizada

- CRPS **por cuantiles**: CRPS_q = (2/21) x suma de pinball en los 21 niveles (misma regla para los tres modelos; aproxima 2 x integral del pinball con una rejilla no uniforme que pesa algo mas las colas).
- pinball_a(y, q) = (1{y < q} - a)(q - y) en a = 0,01 y 0,99.
- VaR 1 %: excedencia si y < q_0,01; VaR 99 %: si y > q_0,99. Kupiec (POF) y Christoffersen (independencia, cadena de Markov de orden 1), p-valores con chi2(1). Sin excedencias, o sin transicion desde una excedencia, el test de Christoffersen no esta definido («—»).
- Vol realizada: RV_h = suma de los h rendimientos log diarios (cierre a cierre) al cuadrado posteriores al origen. Varianza predicha: ((q_0,90 - q_0,10) / (2 x 1,2816))^2 (equivalente normal del rango interdecil; el mismo estimador para los tres modelos, porque Chronos-2 solo da cuantiles). QLIKE = ln(s2) + RV/s2 (forma de Patton sin constante, admite RV = 0; menor es mejor; solo se comparan modelos en el mismo activo y horizonte).

## Licencias

| componente | licencia | URL | uso |
|---|---|---|---|
| Chronos-2 (pesos `amazon/chronos-2`) | Apache-2.0 | https://huggingface.co/amazon/chronos-2 | permite uso de investigacion interno; usado |
| chronos-forecasting 2.3.2 (codigo) | Apache-2.0 | https://github.com/amazon-science/chronos-forecasting | instalado en LAB-00-ENV |
| Toto (pesos `Datadog/Toto-Open-Base-1.0`) | Apache-2.0 | https://huggingface.co/Datadog/Toto-Open-Base-1.0 | permite uso de investigacion interno; usado (venv aparte, fase 2) |
| toto-ts 0.2.0 (codigo) | Apache-2.0 | https://pypi.org/project/toto-ts/ | permite uso de investigacion interno; usado (venv aparte, fase 2) |
| arch 8.0.0 (GARCH) | NCSA | https://github.com/bashtage/arch | sin pesos |
| HMM del motor (quantdesk 69fdb39d) | propio | S:/Projects/quantdesk | sin pesos |

Datos: Binance Vision CC BY-NC-SA 4.0 (solo uso personal no productivo, ver TI-02-DATA); lago de qn, propio. Licencias de pesos verificadas en las tarjetas de Hugging Face el 2026-11-09.

## Toto

Instalado en la fase 2 por decision del usuario (venv aparte; el `.venv` del laboratorio no se toca).

- Ordenes ejecutadas (con `PIP_CACHE_DIR`, `HF_HOME` y `TMPDIR` bajo E:/quantdesk-lab): `D:/miniconda312/python.exe -m venv E:/quantdesk-lab/venvs/toto`; `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.0`; `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install toto-ts==0.2.0 pyarrow` (con las dependencias que fija toto-ts 0.2.0, entre ellas numpy 1.26.4, pandas 2.2.3, transformers 4.52.1 y gluonts 0.16.2, y herramientas de desarrollo que el paquete declara como dependencias de ejecucion). Pesos descargados una vez con `toto_trabajador.py --descargar`; las corridas usan `HF_HUB_OFFLINE=1`.
- Versiones del venv de Toto: python 3.12.3, numpy 1.26.4, torch 2.7.0+cpu, toto-ts 0.2.0, transformers 4.52.1, huggingface-hub 0.36.2, gluonts 0.16.2.
- Pesos: `Datadog/Toto-Open-Base-1.0` revision `0411ceb27bdf7fc3e4892e99edc8ad08192dc3c5`: `.gitattributes` sha256 `79115223a5a3bf830db5a40a4cddf7049c1e9f7540ea4fd6c56de69fb459421f`, `README.md` sha256 `6c3ceab349ffce68af94844bd421642807cf402ea371ddb33fe05939e1e36c80`, `config.json` sha256 `e381ed28a05898bf2ea3386adb839f9f2742d66d97825db492b6658d4af1f778`, `model.safetensors` sha256 `69b67e60decc90baf741729abcf1fe8fe0881e3e3337176042053c28a122fa4c`.

## Reproducibilidad

- Versiones: python 3.12.3, numpy 2.5.4, scipy 1.18.1, pandas 3.1.1, pyarrow 26.0.1, arch 8.0.0, torch 2.15.0+cpu, transformers 5.22.2, chronos-forecasting 2.3.2, huggingface_hub 2.4.0; motor quantdesk 69fdb39d (rueda sha256 `sha256=28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd`). Plataforma: Windows-10-10.0.19045-SP0.
- Pesos de Chronos-2: `amazon/chronos-2` revision `29ec3766d36d6f73f0696f85560a422f50e8498c`: `config.json` sha256 `ef1143bfdc9c0376d9a056eefca46cb4b1ec3d0ffacd541ff56feb40fb708031`, `model.safetensors` sha256 `ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42`. HMM y GARCH no tienen pesos (se calibran en cada origen).
- Semilla de cada prevision: los 31 bits bajos de sha256("semilla|activo|origen_ms|modelo"); el camino j del HMM usa semilla x 4096 + j; GARCH usa `numpy.random.default_rng(semilla)`. Hilos: BLAS/OpenMP 1, torch 2 (`--hilos`).

| dataset | comando exacto | pared (s) | CPU por modelo: total s (s/origen) | carga de modelos (s CPU) | fallos por modelo | HMM sin converger | sha256 predicciones |
|---|---|---|---|---|---|---|---|
| lago_cierre_c20261101 (proxy) | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --out E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101` | 2457 | chronos2 1637 (0.237); garch 573 (0.083); hmm 1351 (0.195) | 10 | chronos2 0, garch 0, hmm 0 | 1892 de 6916 | `f130e892181f932f…` |
| binance_c20261101 | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --out E:/quantdesk-lab/runs/TS-00-BENCH/binance_c20261101` | 4769 | chronos2 1784 (0.497); garch 241 (0.067); hmm 2158 (0.601) | 15 | chronos2 0, garch 0, hmm 0 | 987 de 3590 | `22e2e2531d30d357…` |
| lago_cierre_c20261101 (proxy) | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos toto --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH/toto_lago_cierre_c20261101` | 15178 | toto 9993 (7.138) | 0 | toto 0 | — de — | `cab8e95d13845c6f…` |
| binance_c20261101 | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --modelos toto --cada 10 --out E:/quantdesk-lab/runs/TS-00-BENCH/toto_binance_c20261101` | 13409 | toto 9638 (26.773) | 0 | toto 0 | — de — | `4c35cc697b24bb13…` |

HMM «sin converger»: Baum-Welch agota las 200 iteraciones por defecto sin bajar de `tol` = 1e-8 en la log-verosimilitud; se usa el ajuste igualmente (es el comportamiento del motor con sus opciones por defecto). El CPU de Chronos-2 y de Toto suma sus 2 hilos de torch; el de Toto lo mide su subproceso.

### Repeticion de un subconjunto (aceptacion 3): fincast

- Comando: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos fincast --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/repeticion_fx --activos EURUSD --max-origenes 2 --comparar E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_fx_v1` (2 s de pared mas la carga).
- Resultado: 6 filas (activo x origen x modelo x h) comparadas con la corrida completa `E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_fx_v1`: 0 sin pareja; predicciones identicas bit a bit: **True** (dif. maxima 0.0); metricas del subconjunto recalculadas desde la corrida completa identicas: **True** (dif. maxima 0.0). El script sale con codigo 1 si no coinciden.

Metricas del subconjunto (lago_cierre_c20261101 (proxy)), las mismas que da la corrida completa sobre esos origenes:

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | QLIKE |
|---|---|---|---|---|---|---|---|

### Repeticion de un subconjunto (aceptacion 3): fincast

- Comando: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --modelos fincast --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/repeticion_binance --activos BTCUSDT --max-origenes 2 --comparar E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_binance` (3 s de pared mas la carga).
- Resultado: 6 filas (activo x origen x modelo x h) comparadas con la corrida completa `E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_binance`: 0 sin pareja; predicciones identicas bit a bit: **True** (dif. maxima 0.0); metricas del subconjunto recalculadas desde la corrida completa identicas: **True** (dif. maxima 0.0). El script sale con codigo 1 si no coinciden.

Metricas del subconjunto (binance_c20261101), las mismas que da la corrida completa sobre esos origenes:

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | QLIKE |
|---|---|---|---|---|---|---|---|

## Tablas por dataset, activo, horizonte y modelo

### lago_cierre_c20261101 (proxy)

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | n_test | x 1 % | Kupiec 1 % p | Chr. 1 % p | x 99 % | Kupiec 99 % p | Chr. 99 % p | QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | 1 | hmm | 247 | 0.002183 | 0.0001268 | 0.0001422 | 0.0202 | 0.0162 | 247 | 5 | 0.155 | 0.649 | 4 | 0.369 | 0.716 | -10.01 |
| AUDCAD | 1 | garch | 247 | 0.002179 | 0.0001251 | 0.0001369 | 0.0243 | 0.0121 | 247 | 6 | 0.056 | 0.584 | 3 | 0.743 | 0.785 | -9.969 |
| AUDCAD | 1 | chronos2 | 247 | 0.002264 | 0.0002114 | 0.0001502 | 0 | 0.00405 | 247 | 0 | 0.026 | — | 1 | 0.286 | 0.928 | -10.03 |
| AUDCAD | 5 | hmm | 247 | 0.004204 | 0.0002829 | 0.0002641 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.383 |
| AUDCAD | 5 | garch | 247 | 0.004078 | 0.0002249 | 0.0002362 | 0 | 0.00405 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.361 |
| AUDCAD | 5 | chronos2 | 247 | 0.004175 | 0.0003077 | 0.0002341 | 0 | 0.0202 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.314 |
| AUDCAD | 20 | hmm | 247 | 0.007731 | 0.0006043 | 0.0004689 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.973 |
| AUDCAD | 20 | garch | 247 | 0.007104 | 0.0004402 | 0.0004571 | 0 | 0.0081 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.945 |
| AUDCAD | 20 | chronos2 | 247 | 0.007577 | 0.0006561 | 0.000545 | 0 | 0.0081 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.93 |
| AUDCHF | 1 | hmm | 247 | 0.002319 | 0.0001313 | 0.0001229 | 0.00405 | 0.0162 | 247 | 1 | 0.286 | 0.928 | 4 | 0.369 | 0.716 | -9.889 |
| AUDCHF | 1 | garch | 247 | 0.002319 | 0.000143 | 0.0001304 | 0.0202 | 0.0081 | 247 | 5 | 0.155 | 0.649 | 2 | 0.756 | 0.856 | -9.893 |
| AUDCHF | 1 | chronos2 | 247 | 0.002375 | 0.0002026 | 0.0001628 | 0.00405 | 0.00405 | 247 | 1 | 0.286 | 0.928 | 1 | 0.286 | 0.928 | -9.818 |
| AUDCHF | 5 | hmm | 247 | 0.00437 | 0.0003264 | 0.0002309 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.271 |
| AUDCHF | 5 | garch | 247 | 0.004284 | 0.0002825 | 0.0002635 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.268 |
| AUDCHF | 5 | chronos2 | 247 | 0.004314 | 0.0003111 | 0.0002292 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.179 |
| AUDCHF | 20 | hmm | 247 | 0.007757 | 0.000891 | 0.0004619 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.859 |
| AUDCHF | 20 | garch | 247 | 0.007174 | 0.0005878 | 0.0005269 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.861 |
| AUDCHF | 20 | chronos2 | 247 | 0.007478 | 0.0006984 | 0.0005188 | 0 | 0.00405 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.755 |
| AUDJPY | 1 | hmm | 247 | 0.002851 | 0.0001638 | 0.0001588 | 0.0162 | 0.0081 | 247 | 4 | 0.369 | 0.043 | 2 | 0.756 | 0.856 | -9.433 |
| AUDJPY | 1 | garch | 247 | 0.002849 | 0.0001687 | 0.0001706 | 0.0162 | 0.00405 | 247 | 4 | 0.369 | 0.716 | 1 | 0.286 | 0.928 | -9.457 |
| AUDJPY | 1 | chronos2 | 247 | 0.003038 | 0.0002886 | 0.0001963 | 0 | 0.00405 | 247 | 0 | 0.026 | — | 1 | 0.286 | 0.928 | -9.419 |
| AUDJPY | 5 | hmm | 247 | 0.006463 | 0.0005327 | 0.0003269 | 0.0243 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.813 |
| AUDJPY | 5 | garch | 247 | 0.006453 | 0.0005315 | 0.0003446 | 0.0243 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.817 |
| AUDJPY | 5 | chronos2 | 247 | 0.006645 | 0.000518 | 0.0003061 | 0.0121 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.744 |
| AUDJPY | 20 | hmm | 247 | 0.01199 | 0.0007542 | 0.0006829 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.463 |
| AUDJPY | 20 | garch | 247 | 0.01204 | 0.0006178 | 0.0007316 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.476 |
| AUDJPY | 20 | chronos2 | 247 | 0.01074 | 0.001019 | 0.000712 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.408 |
| AUDNZD | 1 | hmm | 247 | 0.001583 | 0.0001098 | 9.546e-05 | 0.0202 | 0.0243 | 247 | 5 | 0.155 | 0.649 | 6 | 0.056 | 0.584 | -10.5 |
| AUDNZD | 1 | garch | 247 | 0.001562 | 0.000106 | 0.0001 | 0.0081 | 0.0162 | 247 | 2 | 0.756 | 0.856 | 4 | 0.369 | 0.716 | -10.56 |
| AUDNZD | 1 | chronos2 | 247 | 0.001637 | 0.0001273 | 0.0001015 | 0.00405 | 0.0081 | 247 | 1 | 0.286 | 0.928 | 2 | 0.756 | 0.856 | -10.57 |
| AUDNZD | 5 | hmm | 247 | 0.003815 | 0.0002295 | 0.0001447 | 0.0283 | 0.00405 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.951 |
| AUDNZD | 5 | garch | 247 | 0.003736 | 0.0001785 | 0.0001568 | 0.0202 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.989 |
| AUDNZD | 5 | chronos2 | 247 | 0.003848 | 0.0002037 | 0.0001621 | 0 | 0.00405 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.006 |
| AUDNZD | 20 | hmm | 247 | 0.007699 | 0.0003302 | 0.0003224 | 0.0121 | 0.0202 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.546 |
| AUDNZD | 20 | garch | 247 | 0.007262 | 0.0002888 | 0.00033 | 0.00405 | 0.00405 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.562 |
| AUDNZD | 20 | chronos2 | 247 | 0.007553 | 0.0004922 | 0.000387 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.579 |
| AUDUSD | 1 | hmm | 247 | 0.002763 | 0.0001651 | 0.000176 | 0.0243 | 0.0202 | 247 | 6 | 0.056 | 0.584 | 5 | 0.155 | 0.077 | -9.564 |
| AUDUSD | 1 | garch | 247 | 0.002772 | 0.0001574 | 0.000183 | 0.0202 | 0.0121 | 247 | 5 | 0.155 | 0.649 | 3 | 0.743 | 0.785 | -9.501 |
| AUDUSD | 1 | chronos2 | 247 | 0.002886 | 0.0002404 | 0.0002042 | 0 | 0.0081 | 247 | 0 | 0.026 | — | 2 | 0.756 | 0.856 | -9.526 |
| AUDUSD | 5 | hmm | 247 | 0.006133 | 0.0003057 | 0.000561 | 0.0081 | 0.0202 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -7.953 |
| AUDUSD | 5 | garch | 247 | 0.005959 | 0.0002823 | 0.0005591 | 0.00405 | 0.0243 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -7.886 |
| AUDUSD | 5 | chronos2 | 247 | 0.006108 | 0.0003695 | 0.0006453 | 0 | 0.0202 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.836 |
| AUDUSD | 20 | hmm | 247 | 0.01423 | 0.0006775 | 0.001033 | 0.0202 | 0.0405 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.519 |
| AUDUSD | 20 | garch | 247 | 0.01278 | 0.0005763 | 0.0008871 | 0.0081 | 0.0324 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.444 |
| AUDUSD | 20 | chronos2 | 247 | 0.01344 | 0.0007745 | 0.001273 | 0 | 0.0445 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.316 |
| CADCHF | 1 | hmm | 247 | 0.001803 | 0.0001179 | 0.000112 | 0.00405 | 0.0121 | 247 | 1 | 0.286 | 0.928 | 3 | 0.743 | 0.785 | -10.36 |
| CADCHF | 1 | garch | 247 | 0.001806 | 0.0001223 | 0.0001039 | 0.0162 | 0.00405 | 247 | 4 | 0.369 | 0.716 | 1 | 0.286 | 0.928 | -10.34 |
| CADCHF | 1 | chronos2 | 247 | 0.001847 | 0.0001257 | 0.0001137 | 0 | 0.00405 | 247 | 0 | 0.026 | — | 1 | 0.286 | 0.928 | -10.31 |
| CADCHF | 5 | hmm | 247 | 0.003816 | 0.0002494 | 0.0001988 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.741 |
| CADCHF | 5 | garch | 247 | 0.003802 | 0.0002336 | 0.0002112 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.733 |
| CADCHF | 5 | chronos2 | 247 | 0.003821 | 0.0002224 | 0.0002008 | 0 | 0.00405 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.684 |
| CADCHF | 20 | hmm | 247 | 0.006772 | 0.0005302 | 0.0003684 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.354 |
| CADCHF | 20 | garch | 247 | 0.006427 | 0.0004875 | 0.0004 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.341 |
| CADCHF | 20 | chronos2 | 247 | 0.006248 | 0.0005062 | 0.0004093 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.332 |
| CADJPY | 1 | hmm | 247 | 0.002324 | 0.0002675 | 0.0001224 | 0.0364 | 0.0081 | 247 | 9 | 0.001 | 0.320 | 2 | 0.756 | 0.856 | -9.389 |
| CADJPY | 1 | garch | 247 | 0.00234 | 0.0002667 | 0.0001287 | 0.0324 | 0.00405 | 247 | 8 | 0.005 | 0.243 | 1 | 0.286 | 0.928 | -9.617 |
| CADJPY | 1 | chronos2 | 247 | 0.002433 | 0.0002009 | 0.0001379 | 0.00405 | 0.00405 | 247 | 1 | 0.286 | 0.928 | 1 | 0.286 | 0.928 | -9.733 |
| CADJPY | 5 | hmm | 247 | 0.005559 | 0.0006552 | 0.000282 | 0.0364 | 0.0121 | 50 | 3 | 0.015 | 0.531 | 1 | 0.532 | 0.838 | -7.999 |
| CADJPY | 5 | garch | 247 | 0.005572 | 0.0006809 | 0.0002912 | 0.0324 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.083 |
| CADJPY | 5 | chronos2 | 247 | 0.005525 | 0.0005039 | 0.0002376 | 0.0202 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.995 |
| CADJPY | 20 | hmm | 247 | 0.009932 | 0.0005201 | 0.0005277 | 0.0081 | 0.0202 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.691 |
| CADJPY | 20 | garch | 247 | 0.0103 | 0.0005214 | 0.0006037 | 0.00405 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.754 |
| CADJPY | 20 | chronos2 | 247 | 0.008844 | 0.0005903 | 0.000512 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.665 |
| CHFJPY | 1 | hmm | 247 | 0.002315 | 0.0001594 | 0.0001233 | 0.0202 | 0.0081 | 247 | 5 | 0.155 | 0.077 | 2 | 0.756 | 0.856 | -9.829 |
| CHFJPY | 1 | garch | 247 | 0.00232 | 0.0001649 | 0.0001121 | 0.0324 | 0.00405 | 247 | 8 | 0.005 | 0.243 | 1 | 0.286 | 0.928 | -9.817 |
| CHFJPY | 1 | chronos2 | 247 | 0.002435 | 0.0001949 | 0.0001401 | 0.00405 | 0 | 247 | 1 | 0.286 | 0.928 | 0 | 0.026 | — | -9.861 |
| CHFJPY | 5 | hmm | 247 | 0.005528 | 0.0005857 | 0.0002649 | 0.0364 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.188 |
| CHFJPY | 5 | garch | 247 | 0.005476 | 0.0005516 | 0.0002869 | 0.0405 | 0.00405 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.199 |
| CHFJPY | 5 | chronos2 | 247 | 0.005313 | 0.0003432 | 0.0002658 | 0.0283 | 0.00405 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.107 |
| CHFJPY | 20 | hmm | 247 | 0.009927 | 0.0005176 | 0.000566 | 0.0283 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.843 |
| CHFJPY | 20 | garch | 247 | 0.009903 | 0.0005053 | 0.0005544 | 0.0324 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.852 |
| CHFJPY | 20 | chronos2 | 247 | 0.0078 | 0.0006993 | 0.0005573 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.583 |
| EURAUD | 1 | hmm | 247 | 0.001964 | 0.0001236 | 0.0001124 | 0.0162 | 0.0121 | 247 | 4 | 0.369 | 0.716 | 3 | 0.743 | 0.785 | -10.24 |
| EURAUD | 1 | garch | 247 | 0.001936 | 0.0001087 | 0.0001073 | 0.0081 | 0.00405 | 247 | 2 | 0.756 | 0.856 | 1 | 0.286 | 0.928 | -10.25 |
| EURAUD | 1 | chronos2 | 247 | 0.002018 | 0.0001332 | 0.0001473 | 0 | 0 | 247 | 0 | 0.026 | — | 0 | 0.026 | — | -10.2 |
| EURAUD | 5 | hmm | 247 | 0.004231 | 0.0002051 | 0.0002745 | 0.00405 | 0.0121 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.612 |
| EURAUD | 5 | garch | 247 | 0.004087 | 0.0002136 | 0.0002595 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.638 |
| EURAUD | 5 | chronos2 | 247 | 0.004255 | 0.000216 | 0.0002876 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.614 |
| EURAUD | 20 | hmm | 247 | 0.009104 | 0.0004005 | 0.0006403 | 0.00405 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.19 |
| EURAUD | 20 | garch | 247 | 0.008354 | 0.0004113 | 0.000478 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.223 |
| EURAUD | 20 | chronos2 | 247 | 0.008758 | 0.0005626 | 0.0006219 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.219 |
| EURCAD | 1 | hmm | 247 | 0.001453 | 0.0001075 | 9.488e-05 | 0.0121 | 0.0121 | 247 | 3 | 0.743 | 0.785 | 3 | 0.743 | 0.785 | -10.69 |
| EURCAD | 1 | garch | 247 | 0.001436 | 0.0001159 | 8.95e-05 | 0.0121 | 0.0121 | 247 | 3 | 0.743 | 0.785 | 3 | 0.743 | 0.785 | -10.81 |
| EURCAD | 1 | chronos2 | 247 | 0.001444 | 0.0001054 | 8.904e-05 | 0.00405 | 0 | 247 | 1 | 0.286 | 0.928 | 0 | 0.026 | — | -10.81 |
| EURCAD | 5 | hmm | 247 | 0.003208 | 0.0002019 | 0.0001964 | 0.0162 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.12 |
| EURCAD | 5 | garch | 247 | 0.003197 | 0.0002062 | 0.0001939 | 0.0121 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.181 |
| EURCAD | 5 | chronos2 | 247 | 0.003119 | 0.0003017 | 0.0001746 | 0.0162 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.155 |
| EURCAD | 20 | hmm | 247 | 0.006507 | 0.0003481 | 0.0004206 | 0.00405 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.744 |
| EURCAD | 20 | garch | 247 | 0.006701 | 0.0006503 | 0.0004163 | 0.0526 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.681 |
| EURCAD | 20 | chronos2 | 247 | 0.005899 | 0.0004054 | 0.0003803 | 0.0121 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.676 |
| EURCHF | 1 | hmm | 247 | 0.00132 | 0.0001413 | 6.051e-05 | 0.0283 | 0.0081 | 247 | 7 | 0.018 | 0.522 | 2 | 0.756 | 0.856 | -10.85 |
| EURCHF | 1 | garch | 247 | 0.001309 | 0.0001302 | 6.809e-05 | 0.0162 | 0.00405 | 247 | 4 | 0.369 | 0.716 | 1 | 0.286 | 0.928 | -10.9 |
| EURCHF | 1 | chronos2 | 247 | 0.001318 | 0.0001222 | 7.634e-05 | 0.0243 | 0 | 247 | 6 | 0.056 | 0.584 | 0 | 0.026 | — | -10.83 |
| EURCHF | 5 | hmm | 247 | 0.002684 | 0.0001804 | 0.0001271 | 0.0121 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.244 |
| EURCHF | 5 | garch | 247 | 0.002696 | 0.0001638 | 0.0001327 | 0.0081 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -9.277 |
| EURCHF | 5 | chronos2 | 247 | 0.002733 | 0.0001817 | 0.000125 | 0.0243 | 0 | 50 | 2 | 0.107 | 0.772 | 0 | 0.316 | — | -9.008 |
| EURCHF | 20 | hmm | 247 | 0.006084 | 0.0003123 | 0.00026 | 0.00405 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.897 |
| EURCHF | 20 | garch | 247 | 0.006109 | 0.0003269 | 0.0002638 | 0.0162 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.86 |
| EURCHF | 20 | chronos2 | 247 | 0.006083 | 0.0002738 | 0.0002656 | 0.0121 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.669 |
| EURGBP | 1 | hmm | 247 | 0.001128 | 6.783e-05 | 7.243e-05 | 0.0202 | 0.0081 | 247 | 5 | 0.155 | 0.649 | 2 | 0.756 | 0.856 | -11.28 |
| EURGBP | 1 | garch | 247 | 0.001121 | 8.228e-05 | 6.639e-05 | 0.0243 | 0.0121 | 247 | 6 | 0.056 | 0.584 | 3 | 0.743 | 0.785 | -11.21 |
| EURGBP | 1 | chronos2 | 247 | 0.001155 | 0.0001042 | 8.512e-05 | 0.0121 | 0 | 247 | 3 | 0.743 | 0.785 | 0 | 0.026 | — | -11.1 |
| EURGBP | 5 | hmm | 247 | 0.002459 | 0.0001222 | 0.0001564 | 0.00405 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.666 |
| EURGBP | 5 | garch | 247 | 0.002431 | 0.0001546 | 0.0001376 | 0.0162 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.647 |
| EURGBP | 5 | chronos2 | 247 | 0.002501 | 0.0002225 | 0.0001501 | 0.0324 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.596 |
| EURGBP | 20 | hmm | 247 | 0.005196 | 0.0002753 | 0.000364 | 0.0243 | 0 | 13 | 1 | 0.121 | — | 0 | 0.609 | — | -8.28 |
| EURGBP | 20 | garch | 247 | 0.004944 | 0.0003811 | 0.000296 | 0.0324 | 0 | 13 | 1 | 0.121 | — | 0 | 0.609 | — | -8.292 |
| EURGBP | 20 | chronos2 | 247 | 0.005038 | 0.0004819 | 0.0003483 | 0.0486 | 0 | 13 | 1 | 0.121 | — | 0 | 0.609 | — | -8.206 |
| EURJPY | 1 | hmm | 247 | 0.002003 | 0.0001874 | 0.0001097 | 0.0162 | 0.00405 | 247 | 4 | 0.369 | 0.716 | 1 | 0.286 | 0.928 | -9.926 |
| EURJPY | 1 | garch | 247 | 0.002007 | 0.000198 | 0.000115 | 0.0243 | 0.00405 | 247 | 6 | 0.056 | 0.121 | 1 | 0.286 | 0.928 | -10 |
| EURJPY | 1 | chronos2 | 247 | 0.002117 | 0.0001642 | 0.0001241 | 0 | 0.00405 | 247 | 0 | 0.026 | — | 1 | 0.286 | 0.928 | -9.962 |
| EURJPY | 5 | hmm | 247 | 0.004805 | 0.0003881 | 0.0002292 | 0.0364 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.374 |
| EURJPY | 5 | garch | 247 | 0.004821 | 0.0005723 | 0.0002393 | 0.0486 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.317 |
| EURJPY | 5 | chronos2 | 247 | 0.00478 | 0.0003793 | 0.0002204 | 0.0283 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.056 |
| EURJPY | 20 | hmm | 247 | 0.009104 | 0.0003839 | 0.0005042 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.021 |
| EURJPY | 20 | garch | 247 | 0.009739 | 0.0004306 | 0.0005244 | 0.0324 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.972 |
| EURJPY | 20 | chronos2 | 247 | 0.008213 | 0.0005644 | 0.0005053 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.846 |
| EURNZD | 1 | hmm | 247 | 0.001919 | 0.0001252 | 9.698e-05 | 0.0162 | 0 | 247 | 4 | 0.369 | 0.716 | 0 | 0.026 | — | -10.29 |
| EURNZD | 1 | garch | 247 | 0.001901 | 9.921e-05 | 9.908e-05 | 0.0081 | 0 | 247 | 2 | 0.756 | 0.856 | 0 | 0.026 | — | -10.3 |
| EURNZD | 1 | chronos2 | 247 | 0.001929 | 0.0001206 | 0.0001286 | 0 | 0 | 247 | 0 | 0.026 | — | 0 | 0.026 | — | -10.29 |
| EURNZD | 5 | hmm | 247 | 0.004365 | 0.0002128 | 0.000241 | 0.0081 | 0.00405 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.674 |
| EURNZD | 5 | garch | 247 | 0.004234 | 0.0002101 | 0.0002286 | 0.00405 | 0.00405 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.692 |
| EURNZD | 5 | chronos2 | 247 | 0.004249 | 0.0002332 | 0.0002463 | 0.00405 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.683 |
| EURNZD | 20 | hmm | 247 | 0.009753 | 0.0003875 | 0.0005321 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.272 |
| EURNZD | 20 | garch | 247 | 0.009355 | 0.0003698 | 0.0004727 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.304 |
| EURNZD | 20 | chronos2 | 247 | 0.008804 | 0.0004803 | 0.000562 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.312 |
| EURUSD | 1 | hmm | 247 | 0.001795 | 9.813e-05 | 0.0001212 | 0.0121 | 0.0162 | 247 | 3 | 0.743 | 0.785 | 4 | 0.369 | 0.716 | -10.42 |
| EURUSD | 1 | garch | 247 | 0.001796 | 9.67e-05 | 0.0001206 | 0.0081 | 0.0202 | 247 | 2 | 0.756 | 0.856 | 5 | 0.155 | 0.649 | -10.35 |
| EURUSD | 1 | chronos2 | 247 | 0.001868 | 0.0001237 | 0.0001296 | 0 | 0 | 247 | 0 | 0.026 | — | 0 | 0.026 | — | -10.32 |
| EURUSD | 5 | hmm | 247 | 0.004401 | 0.0002054 | 0.0003297 | 0.0081 | 0.0243 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.751 |
| EURUSD | 5 | garch | 247 | 0.004295 | 0.0001963 | 0.0003454 | 0.00405 | 0.0162 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.714 |
| EURUSD | 5 | chronos2 | 247 | 0.004382 | 0.0002344 | 0.0003066 | 0 | 0.0162 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.686 |
| EURUSD | 20 | hmm | 247 | 0.009751 | 0.0004226 | 0.0004969 | 0.0202 | 0.00405 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.269 |
| EURUSD | 20 | garch | 247 | 0.009001 | 0.0003948 | 0.0004403 | 0.0162 | 0.00405 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.217 |
| EURUSD | 20 | chronos2 | 247 | 0.009364 | 0.0005203 | 0.0005639 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.279 |
| GBPAUD | 1 | hmm | 247 | 0.001965 | 9.422e-05 | 0.0001009 | 0.0081 | 0.0121 | 247 | 2 | 0.756 | 0.856 | 3 | 0.743 | 0.785 | -10.21 |
| GBPAUD | 1 | garch | 247 | 0.001968 | 0.0001038 | 0.0001109 | 0.0081 | 0.0081 | 247 | 2 | 0.756 | 0.856 | 2 | 0.756 | 0.856 | -10.2 |
| GBPAUD | 1 | chronos2 | 247 | 0.002 | 0.0001144 | 0.0001371 | 0.00405 | 0 | 247 | 1 | 0.286 | 0.928 | 0 | 0.026 | — | -10.15 |
| GBPAUD | 5 | hmm | 247 | 0.004302 | 0.000209 | 0.0002372 | 0.00405 | 0.0121 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.626 |
| GBPAUD | 5 | garch | 247 | 0.004342 | 0.0002157 | 0.0002444 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.615 |
| GBPAUD | 5 | chronos2 | 247 | 0.004446 | 0.0002106 | 0.0002352 | 0.00405 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.576 |
| GBPAUD | 20 | hmm | 247 | 0.009269 | 0.0004728 | 0.0004959 | 0.0081 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.234 |
| GBPAUD | 20 | garch | 247 | 0.009273 | 0.000446 | 0.0004357 | 0.00405 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.238 |
| GBPAUD | 20 | chronos2 | 247 | 0.009505 | 0.0006723 | 0.0005715 | 0.0364 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.217 |
| GBPCAD | 1 | hmm | 247 | 0.00176 | 9.864e-05 | 0.0001069 | 0.0162 | 0.0162 | 247 | 4 | 0.369 | 0.716 | 4 | 0.369 | 0.716 | -10.43 |
| GBPCAD | 1 | garch | 247 | 0.001767 | 0.0001009 | 0.0001136 | 0.0202 | 0.0162 | 247 | 5 | 0.155 | 0.649 | 4 | 0.369 | 0.716 | -10.39 |
| GBPCAD | 1 | chronos2 | 247 | 0.001783 | 0.000116 | 9.673e-05 | 0.00405 | 0 | 247 | 1 | 0.286 | 0.928 | 0 | 0.026 | — | -10.36 |
| GBPCAD | 5 | hmm | 247 | 0.003357 | 0.0001874 | 0.0001864 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.795 |
| GBPCAD | 5 | garch | 247 | 0.003361 | 0.0001881 | 0.0001931 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.783 |
| GBPCAD | 5 | chronos2 | 247 | 0.003323 | 0.0002311 | 0.0001937 | 0.0081 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.813 |
| GBPCAD | 20 | hmm | 247 | 0.005863 | 0.0003733 | 0.000362 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.446 |
| GBPCAD | 20 | garch | 247 | 0.006022 | 0.0003699 | 0.0003828 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.404 |
| GBPCAD | 20 | chronos2 | 247 | 0.005298 | 0.0004359 | 0.0003541 | 0.00405 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.275 |
| GBPCHF | 1 | hmm | 247 | 0.001677 | 0.0001553 | 7.901e-05 | 0.0202 | 0 | 247 | 5 | 0.155 | 0.649 | 0 | 0.026 | — | -10.43 |
| GBPCHF | 1 | garch | 247 | 0.001651 | 0.0001433 | 8.387e-05 | 0.0162 | 0 | 247 | 4 | 0.369 | 0.716 | 0 | 0.026 | — | -10.47 |
| GBPCHF | 1 | chronos2 | 247 | 0.001669 | 0.0001289 | 0.0001091 | 0.0121 | 0.00405 | 247 | 3 | 0.743 | 0.785 | 1 | 0.286 | 0.928 | -10.49 |
| GBPCHF | 5 | hmm | 247 | 0.003337 | 0.0002414 | 0.0001704 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.807 |
| GBPCHF | 5 | garch | 247 | 0.003269 | 0.000201 | 0.0001842 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.828 |
| GBPCHF | 5 | chronos2 | 247 | 0.003252 | 0.0002022 | 0.0001819 | 0 | 0.0081 | 50 | 0 | 0.316 | — | 2 | 0.107 | 0.680 | -8.703 |
| GBPCHF | 20 | hmm | 247 | 0.006664 | 0.0005901 | 0.0003146 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.477 |
| GBPCHF | 20 | garch | 247 | 0.006348 | 0.0004246 | 0.000345 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.487 |
| GBPCHF | 20 | chronos2 | 247 | 0.006153 | 0.000497 | 0.0003957 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.354 |
| GBPJPY | 1 | hmm | 247 | 0.00223 | 0.0001402 | 0.0001286 | 0.0202 | 0.0121 | 247 | 5 | 0.155 | 0.649 | 3 | 0.743 | 0.785 | -9.802 |
| GBPJPY | 1 | garch | 247 | 0.002226 | 0.0001873 | 0.0001269 | 0.0324 | 0.00405 | 247 | 8 | 0.005 | 0.243 | 1 | 0.286 | 0.928 | -9.792 |
| GBPJPY | 1 | chronos2 | 247 | 0.002339 | 0.0001995 | 0.0001434 | 0 | 0.00405 | 247 | 0 | 0.026 | — | 1 | 0.286 | 0.928 | -9.836 |
| GBPJPY | 5 | hmm | 247 | 0.005051 | 0.0005233 | 0.0002537 | 0.0364 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.225 |
| GBPJPY | 5 | garch | 247 | 0.005093 | 0.0006135 | 0.0002713 | 0.0405 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -8.211 |
| GBPJPY | 5 | chronos2 | 247 | 0.00515 | 0.0003305 | 0.0002383 | 0.0081 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.077 |
| GBPJPY | 20 | hmm | 247 | 0.009598 | 0.0004962 | 0.0005142 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.868 |
| GBPJPY | 20 | garch | 247 | 0.01009 | 0.0005073 | 0.0005731 | 0.0283 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.858 |
| GBPJPY | 20 | chronos2 | 247 | 0.009232 | 0.0006473 | 0.0005233 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.792 |
| GBPNZD | 1 | hmm | 247 | 0.001853 | 0.0001063 | 0.0001033 | 0.0162 | 0.0081 | 247 | 4 | 0.369 | 0.716 | 2 | 0.756 | 0.856 | -10.33 |
| GBPNZD | 1 | garch | 247 | 0.001846 | 0.0001019 | 9.425e-05 | 0.0081 | 0.0081 | 247 | 2 | 0.756 | 0.856 | 2 | 0.756 | 0.856 | -10.33 |
| GBPNZD | 1 | chronos2 | 247 | 0.001875 | 0.0001283 | 0.0001129 | 0.00405 | 0 | 247 | 1 | 0.286 | 0.928 | 0 | 0.026 | — | -10.31 |
| GBPNZD | 5 | hmm | 247 | 0.004218 | 0.0002443 | 0.0002055 | 0.0243 | 0.0081 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.744 |
| GBPNZD | 5 | garch | 247 | 0.004177 | 0.0002378 | 0.0002159 | 0.0162 | 0.00405 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.735 |
| GBPNZD | 5 | chronos2 | 247 | 0.0042 | 0.0002281 | 0.0002313 | 0.00405 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.739 |
| GBPNZD | 20 | hmm | 247 | 0.008722 | 0.0004508 | 0.0003908 | 0.0162 | 0.00405 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.361 |
| GBPNZD | 20 | garch | 247 | 0.008673 | 0.0004079 | 0.000413 | 0.0162 | 0.00405 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.372 |
| GBPNZD | 20 | chronos2 | 247 | 0.00834 | 0.0004628 | 0.0004681 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.367 |
| GBPUSD | 1 | hmm | 247 | 0.002159 | 0.0001048 | 0.0001409 | 0.00405 | 0.0202 | 247 | 1 | 0.286 | 0.928 | 5 | 0.155 | 0.649 | -10.02 |
| GBPUSD | 1 | garch | 247 | 0.002149 | 0.0001055 | 0.0001482 | 0.0121 | 0.0243 | 247 | 3 | 0.743 | 0.785 | 6 | 0.056 | 0.584 | -10.01 |
| GBPUSD | 1 | chronos2 | 247 | 0.002162 | 0.0001277 | 0.0001321 | 0 | 0.0081 | 247 | 0 | 0.026 | — | 2 | 0.756 | 0.856 | -9.984 |
| GBPUSD | 5 | hmm | 247 | 0.00468 | 0.0002157 | 0.0003165 | 0 | 0.0202 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.425 |
| GBPUSD | 5 | garch | 247 | 0.004598 | 0.0002151 | 0.0003321 | 0.00405 | 0.0243 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.406 |
| GBPUSD | 5 | chronos2 | 247 | 0.004561 | 0.0002507 | 0.0003412 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.4 |
| GBPUSD | 20 | hmm | 247 | 0.009126 | 0.0004315 | 0.000448 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.048 |
| GBPUSD | 20 | garch | 247 | 0.008385 | 0.0004218 | 0.0004332 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.01 |
| GBPUSD | 20 | chronos2 | 247 | 0.008346 | 0.0005459 | 0.0004982 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.037 |
| NZDCAD | 1 | hmm | 247 | 0.002296 | 0.0001326 | 0.0001312 | 0.0162 | 0.0202 | 247 | 4 | 0.369 | 0.716 | 5 | 0.155 | 0.649 | -9.864 |
| NZDCAD | 1 | garch | 247 | 0.002273 | 0.0001355 | 0.0001349 | 0.0162 | 0.0243 | 247 | 4 | 0.369 | 0.716 | 6 | 0.056 | 0.584 | -9.873 |
| NZDCAD | 1 | chronos2 | 247 | 0.002272 | 0.0001411 | 0.0001344 | 0 | 0.00405 | 247 | 0 | 0.026 | — | 1 | 0.286 | 0.928 | -9.892 |
| NZDCAD | 5 | hmm | 247 | 0.004971 | 0.0002678 | 0.0002435 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.294 |
| NZDCAD | 5 | garch | 247 | 0.004871 | 0.0002475 | 0.0002481 | 0.0081 | 0.0162 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.263 |
| NZDCAD | 5 | chronos2 | 247 | 0.004977 | 0.0002737 | 0.0003242 | 0.00405 | 0.0162 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.304 |
| NZDCAD | 20 | hmm | 247 | 0.009182 | 0.0004992 | 0.0004514 | 0 | 0.0121 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.896 |
| NZDCAD | 20 | garch | 247 | 0.008907 | 0.0004537 | 0.0004414 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.885 |
| NZDCAD | 20 | chronos2 | 247 | 0.008864 | 0.0005137 | 0.0007348 | 0 | 0.0648 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.773 |
| NZDCHF | 1 | hmm | 247 | 0.002198 | 0.0001332 | 0.0001103 | 0.00405 | 0.00405 | 247 | 1 | 0.286 | 0.928 | 1 | 0.286 | 0.928 | -9.996 |
| NZDCHF | 1 | garch | 247 | 0.002195 | 0.0001338 | 0.0001195 | 0.00405 | 0.00405 | 247 | 1 | 0.286 | 0.928 | 1 | 0.286 | 0.928 | -10.01 |
| NZDCHF | 1 | chronos2 | 247 | 0.002259 | 0.0001698 | 0.0001429 | 0 | 0 | 247 | 0 | 0.026 | — | 0 | 0.026 | — | -9.925 |
| NZDCHF | 5 | hmm | 247 | 0.004323 | 0.0002836 | 0.0002534 | 0 | 0.0081 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.395 |
| NZDCHF | 5 | garch | 247 | 0.004252 | 0.000271 | 0.0002672 | 0 | 0.0081 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.398 |
| NZDCHF | 5 | chronos2 | 247 | 0.004234 | 0.000285 | 0.0002519 | 0 | 0.0081 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.306 |
| NZDCHF | 20 | hmm | 247 | 0.00884 | 0.0007434 | 0.000441 | 0 | 0.00405 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.011 |
| NZDCHF | 20 | garch | 247 | 0.008598 | 0.0005778 | 0.000476 | 0 | 0.00405 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.007 |
| NZDCHF | 20 | chronos2 | 247 | 0.007866 | 0.0006758 | 0.000559 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.988 |
| NZDJPY | 1 | hmm | 247 | 0.002791 | 0.0001724 | 0.0001561 | 0.0081 | 0.0081 | 247 | 2 | 0.756 | 0.856 | 2 | 0.756 | 0.856 | -9.475 |
| NZDJPY | 1 | garch | 247 | 0.002788 | 0.0001699 | 0.000146 | 0.0121 | 0.00405 | 247 | 3 | 0.743 | 0.785 | 1 | 0.286 | 0.928 | -9.52 |
| NZDJPY | 1 | chronos2 | 247 | 0.002897 | 0.0002043 | 0.0001878 | 0 | 0.0081 | 247 | 0 | 0.026 | — | 2 | 0.756 | 0.856 | -9.437 |
| NZDJPY | 5 | hmm | 247 | 0.006911 | 0.0005739 | 0.000324 | 0.0283 | 0.00405 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.867 |
| NZDJPY | 5 | garch | 247 | 0.006785 | 0.000581 | 0.0003257 | 0.0283 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.876 |
| NZDJPY | 5 | chronos2 | 247 | 0.006841 | 0.0004639 | 0.0003514 | 0.0121 | 0.0081 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.759 |
| NZDJPY | 20 | hmm | 247 | 0.01278 | 0.001025 | 0.0006253 | 0.0567 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.496 |
| NZDJPY | 20 | garch | 247 | 0.01264 | 0.0009942 | 0.0006656 | 0.0486 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.501 |
| NZDJPY | 20 | chronos2 | 247 | 0.01189 | 0.0006595 | 0.0006866 | 0.0081 | 0.0121 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.354 |
| NZDUSD | 1 | hmm | 247 | 0.002977 | 0.0001362 | 0.0001752 | 0.0121 | 0.0121 | 247 | 3 | 0.743 | 0.785 | 3 | 0.743 | 0.785 | -9.431 |
| NZDUSD | 1 | garch | 247 | 0.002931 | 0.000137 | 0.0001799 | 0.00405 | 0.0202 | 247 | 1 | 0.286 | 0.928 | 5 | 0.155 | 0.649 | -9.411 |
| NZDUSD | 1 | chronos2 | 247 | 0.002985 | 0.0001761 | 0.00017 | 0 | 0 | 247 | 0 | 0.026 | — | 0 | 0.026 | — | -9.403 |
| NZDUSD | 5 | hmm | 247 | 0.007172 | 0.0003009 | 0.0005659 | 0 | 0.0364 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.813 |
| NZDUSD | 5 | garch | 247 | 0.006867 | 0.0002943 | 0.0004813 | 0 | 0.0202 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.811 |
| NZDUSD | 5 | chronos2 | 247 | 0.007019 | 0.000361 | 0.0003989 | 0 | 0.0121 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.83 |
| NZDUSD | 20 | hmm | 247 | 0.01643 | 0.0006214 | 0.0009595 | 0.00405 | 0.0445 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.407 |
| NZDUSD | 20 | garch | 247 | 0.01476 | 0.0006111 | 0.0006255 | 0.00405 | 0.0283 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.421 |
| NZDUSD | 20 | chronos2 | 247 | 0.01454 | 0.0007535 | 0.0007118 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.413 |
| USDCAD | 1 | hmm | 247 | 0.001445 | 0.0001063 | 7.767e-05 | 0.0162 | 0.0081 | 247 | 4 | 0.369 | 0.716 | 2 | 0.756 | 0.856 | -10.82 |
| USDCAD | 1 | garch | 247 | 0.001442 | 9.689e-05 | 9.239e-05 | 0.0202 | 0.0081 | 247 | 5 | 0.155 | 0.649 | 2 | 0.756 | 0.856 | -10.77 |
| USDCAD | 1 | chronos2 | 247 | 0.001479 | 9.755e-05 | 8.923e-05 | 0.00405 | 0.00405 | 247 | 1 | 0.286 | 0.928 | 1 | 0.286 | 0.928 | -10.76 |
| USDCAD | 5 | hmm | 247 | 0.003963 | 0.0002925 | 0.0001668 | 0.0202 | 0.0162 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -9.181 |
| USDCAD | 5 | garch | 247 | 0.003854 | 0.0002673 | 0.0001638 | 0.0162 | 0.00405 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.168 |
| USDCAD | 5 | chronos2 | 247 | 0.003904 | 0.0002726 | 0.0001677 | 0.0202 | 0.00405 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.142 |
| USDCAD | 20 | hmm | 247 | 0.009692 | 0.0005213 | 0.0003464 | 0.0364 | 0.0364 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.745 |
| USDCAD | 20 | garch | 247 | 0.009154 | 0.000314 | 0.0003447 | 0.0081 | 0.0081 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.741 |
| USDCAD | 20 | chronos2 | 247 | 0.008904 | 0.0003808 | 0.0003811 | 0 | 0.0081 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.742 |
| USDCHF | 1 | hmm | 247 | 0.002344 | 0.0001713 | 0.0001101 | 0.0162 | 0.00405 | 247 | 4 | 0.369 | 0.716 | 1 | 0.286 | 0.928 | -9.856 |
| USDCHF | 1 | garch | 247 | 0.002342 | 0.000168 | 0.0001195 | 0.0162 | 0.00405 | 247 | 4 | 0.369 | 0.716 | 1 | 0.286 | 0.928 | -9.83 |
| USDCHF | 1 | chronos2 | 247 | 0.002381 | 0.0001718 | 0.0001582 | 0.0081 | 0 | 247 | 2 | 0.756 | 0.856 | 0 | 0.026 | — | -9.796 |
| USDCHF | 5 | hmm | 247 | 0.005502 | 0.0003117 | 0.0002241 | 0 | 0.00405 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.217 |
| USDCHF | 5 | garch | 247 | 0.005288 | 0.0002983 | 0.0002526 | 0.0121 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.227 |
| USDCHF | 5 | chronos2 | 247 | 0.00537 | 0.0003585 | 0.0002706 | 0.0162 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.173 |
| USDCHF | 20 | hmm | 247 | 0.01018 | 0.0008352 | 0.0004124 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.788 |
| USDCHF | 20 | garch | 247 | 0.009249 | 0.0005506 | 0.0004934 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.818 |
| USDCHF | 20 | chronos2 | 247 | 0.009623 | 0.0006727 | 0.0006201 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.771 |
| USDJPY | 1 | hmm | 247 | 0.002393 | 0.0002366 | 0.0001182 | 0.0162 | 0.0121 | 247 | 4 | 0.369 | 0.716 | 3 | 0.743 | 0.785 | -9.524 |
| USDJPY | 1 | garch | 247 | 0.00242 | 0.0003085 | 0.0001403 | 0.0243 | 0.00405 | 247 | 6 | 0.056 | 0.584 | 1 | 0.286 | 0.928 | -9.398 |
| USDJPY | 1 | chronos2 | 247 | 0.002493 | 0.0002298 | 0.0001515 | 0.0121 | 0.00405 | 247 | 3 | 0.743 | 0.785 | 1 | 0.286 | 0.928 | -9.429 |
| USDJPY | 5 | hmm | 247 | 0.00584 | 0.0005012 | 0.000253 | 0.0324 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -7.955 |
| USDJPY | 5 | garch | 247 | 0.005835 | 0.001012 | 0.0003016 | 0.0567 | 0 | 50 | 4 | 0.002 | 0.399 | 0 | 0.316 | — | -7.723 |
| USDJPY | 5 | chronos2 | 247 | 0.005781 | 0.0008445 | 0.0002589 | 0.0486 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -7.344 |
| USDJPY | 20 | hmm | 247 | 0.01084 | 0.0006646 | 0.0005461 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.623 |
| USDJPY | 20 | garch | 247 | 0.01096 | 0.000851 | 0.0006568 | 0.0648 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.387 |
| USDJPY | 20 | chronos2 | 247 | 0.01017 | 0.0006348 | 0.0005594 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.163 |

### binance_c20261101

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | n_test | x 1 % | Kupiec 1 % p | Chr. 1 % p | x 99 % | Kupiec 99 % p | Chr. 99 % p | QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | 1 | hmm | 359 | 0.02281 | 0.001268 | 0.00142 | 0.00836 | 0.00557 | 359 | 3 | 0.747 | 0.822 | 2 | 0.357 | 0.881 | -5.265 |
| ADAUSDT | 1 | garch | 359 | 0.02285 | 0.001397 | 0.00136 | 0.0139 | 0.0139 | 359 | 5 | 0.480 | 0.707 | 5 | 0.480 | 0.707 | -5.26 |
| ADAUSDT | 1 | chronos2 | 359 | 0.02386 | 0.001386 | 0.00152 | 0.00279 | 0.00279 | 359 | 1 | 0.104 | 0.940 | 1 | 0.104 | 0.940 | -5.32 |
| ADAUSDT | 5 | hmm | 359 | 0.05481 | 0.002995 | 0.005311 | 0.0139 | 0.0223 | 180 | 3 | 0.412 | 0.749 | 5 | 0.049 | 0.592 | -3.429 |
| ADAUSDT | 5 | garch | 359 | 0.05483 | 0.003285 | 0.005293 | 0.0139 | 0.0306 | 180 | 2 | 0.883 | 0.832 | 6 | 0.013 | 0.519 | -3.429 |
| ADAUSDT | 5 | chronos2 | 359 | 0.05559 | 0.003588 | 0.006497 | 0.0167 | 0.0334 | 180 | 2 | 0.883 | 0.832 | 8 | 0.001 | 0.387 | -3.372 |
| ADAUSDT | 20 | hmm | 359 | 0.113 | 0.005036 | 0.01316 | 0.00557 | 0.0223 | 52 | 0 | 0.307 | — | 2 | 0.116 | 0.037 | -2.089 |
| ADAUSDT | 20 | garch | 359 | 0.1114 | 0.00552 | 0.01107 | 0 | 0.0251 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.024 |
| ADAUSDT | 20 | chronos2 | 359 | 0.1198 | 0.008581 | 0.0138 | 0.0195 | 0.0251 | 52 | 1 | 0.553 | 0.841 | 2 | 0.116 | 0.037 | -1.921 |
| BNBUSDT | 1 | hmm | 359 | 0.01321 | 0.0009237 | 0.0009019 | 0.00836 | 0.00836 | 359 | 3 | 0.747 | 0.822 | 3 | 0.747 | 0.822 | -6.393 |
| BNBUSDT | 1 | garch | 359 | 0.01317 | 0.0009142 | 0.0008712 | 0.00836 | 0.00557 | 359 | 3 | 0.747 | 0.822 | 2 | 0.357 | 0.881 | -6.374 |
| BNBUSDT | 1 | chronos2 | 359 | 0.01378 | 0.0009982 | 0.0008704 | 0.00836 | 0.0167 | 359 | 3 | 0.747 | 0.822 | 6 | 0.244 | 0.651 | -6.356 |
| BNBUSDT | 5 | hmm | 359 | 0.03133 | 0.002251 | 0.002142 | 0.0111 | 0.0139 | 180 | 2 | 0.883 | 0.832 | 2 | 0.883 | 0.832 | -4.654 |
| BNBUSDT | 5 | garch | 359 | 0.03148 | 0.002113 | 0.002368 | 0.00836 | 0.0111 | 180 | 1 | 0.513 | 0.916 | 2 | 0.883 | 0.832 | -4.664 |
| BNBUSDT | 5 | chronos2 | 359 | 0.03178 | 0.00232 | 0.002327 | 0.0139 | 0.0279 | 180 | 2 | 0.883 | 0.832 | 5 | 0.049 | 0.111 | -4.616 |
| BNBUSDT | 20 | hmm | 359 | 0.06268 | 0.00493 | 0.003725 | 0.0195 | 0.0111 | 52 | 1 | 0.553 | 0.841 | 1 | 0.553 | 0.841 | -3.205 |
| BNBUSDT | 20 | garch | 359 | 0.06258 | 0.005122 | 0.005176 | 0.0139 | 0.0139 | 52 | 1 | 0.553 | 0.841 | 1 | 0.553 | 0.841 | -3.184 |
| BNBUSDT | 20 | chronos2 | 359 | 0.06458 | 0.005453 | 0.004816 | 0.0195 | 0.0279 | 52 | 1 | 0.553 | 0.841 | 2 | 0.116 | 0.037 | -3.129 |
| BTCUSDT | 1 | hmm | 359 | 0.01233 | 0.0008093 | 0.0007827 | 0.0111 | 0.00557 | 359 | 4 | 0.831 | 0.764 | 2 | 0.357 | 0.881 | -6.497 |
| BTCUSDT | 1 | garch | 359 | 0.0123 | 0.0007783 | 0.0007257 | 0.00557 | 0.00279 | 359 | 2 | 0.357 | 0.881 | 1 | 0.104 | 0.940 | -6.479 |
| BTCUSDT | 1 | chronos2 | 359 | 0.0132 | 0.0008324 | 0.0009121 | 0.00557 | 0.0195 | 359 | 2 | 0.357 | 0.881 | 7 | 0.109 | 0.597 | -6.393 |
| BTCUSDT | 5 | hmm | 359 | 0.02808 | 0.001724 | 0.001909 | 0.0111 | 0.00836 | 180 | 2 | 0.883 | 0.832 | 2 | 0.883 | 0.832 | -4.862 |
| BTCUSDT | 5 | garch | 359 | 0.02814 | 0.001867 | 0.002126 | 0.00836 | 0.00836 | 180 | 2 | 0.883 | 0.832 | 2 | 0.883 | 0.832 | -4.836 |
| BTCUSDT | 5 | chronos2 | 359 | 0.02862 | 0.00169 | 0.002321 | 0.0139 | 0.0334 | 180 | 3 | 0.412 | 0.749 | 6 | 0.013 | 0.519 | -4.766 |
| BTCUSDT | 20 | hmm | 359 | 0.05901 | 0.00381 | 0.00323 | 0.0167 | 0.00836 | 52 | 1 | 0.553 | 0.841 | 1 | 0.553 | 0.841 | -3.441 |
| BTCUSDT | 20 | garch | 359 | 0.05925 | 0.003759 | 0.003726 | 0.0111 | 0.0111 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -3.388 |
| BTCUSDT | 20 | chronos2 | 359 | 0.05912 | 0.003669 | 0.003304 | 0.0139 | 0.0223 | 52 | 1 | 0.553 | 0.841 | 1 | 0.553 | 0.841 | -3.331 |
| DOGEUSDT | 1 | hmm | 359 | 0.02275 | 0.001432 | 0.001454 | 0.0251 | 0.0167 | 359 | 9 | 0.016 | 0.496 | 6 | 0.244 | 0.651 | -5.227 |
| DOGEUSDT | 1 | garch | 359 | 0.02271 | 0.001352 | 0.001366 | 0.00557 | 0.0111 | 359 | 2 | 0.357 | 0.881 | 4 | 0.831 | 0.764 | -5.266 |
| DOGEUSDT | 1 | chronos2 | 359 | 0.02374 | 0.001721 | 0.001567 | 0.00279 | 0 | 359 | 1 | 0.104 | 0.940 | 0 | 0.007 | — | -5.336 |
| DOGEUSDT | 5 | hmm | 359 | 0.05462 | 0.003035 | 0.004359 | 0.0111 | 0.0167 | 180 | 0 | 0.057 | — | 3 | 0.412 | 0.749 | -3.565 |
| DOGEUSDT | 5 | garch | 359 | 0.05435 | 0.003032 | 0.005246 | 0.00836 | 0.0223 | 180 | 0 | 0.057 | — | 5 | 0.049 | 0.592 | -3.534 |
| DOGEUSDT | 5 | chronos2 | 359 | 0.05503 | 0.002928 | 0.005506 | 0.00557 | 0.0251 | 180 | 1 | 0.513 | 0.916 | 7 | 0.003 | 0.450 | -3.457 |
| DOGEUSDT | 20 | hmm | 359 | 0.1166 | 0.005031 | 0.01297 | 0.00279 | 0.0251 | 52 | 0 | 0.307 | — | 2 | 0.116 | 0.686 | -2.138 |
| DOGEUSDT | 20 | garch | 359 | 0.1151 | 0.006421 | 0.01018 | 0 | 0.0306 | 52 | 0 | 0.307 | — | 3 | 0.017 | 0.540 | -2.148 |
| DOGEUSDT | 20 | chronos2 | 359 | 0.1157 | 0.005786 | 0.01574 | 0 | 0.0362 | 52 | 0 | 0.307 | — | 2 | 0.116 | 0.686 | -2.016 |
| ETHUSDT | 1 | hmm | 359 | 0.01737 | 0.001142 | 0.001308 | 0.00557 | 0.00836 | 359 | 2 | 0.357 | 0.881 | 3 | 0.747 | 0.822 | -5.685 |
| ETHUSDT | 1 | garch | 359 | 0.01737 | 0.001139 | 0.001347 | 0.0111 | 0.00836 | 359 | 4 | 0.831 | 0.764 | 3 | 0.747 | 0.822 | -5.659 |
| ETHUSDT | 1 | chronos2 | 359 | 0.01799 | 0.001251 | 0.00134 | 0.0139 | 0.0111 | 359 | 5 | 0.480 | 0.707 | 4 | 0.831 | 0.764 | -5.684 |
| ETHUSDT | 5 | hmm | 359 | 0.03994 | 0.002702 | 0.003203 | 0.0111 | 0.0139 | 180 | 1 | 0.513 | 0.916 | 3 | 0.412 | 0.749 | -4.071 |
| ETHUSDT | 5 | garch | 359 | 0.03984 | 0.002676 | 0.003288 | 0.0195 | 0.0139 | 180 | 4 | 0.156 | 0.669 | 3 | 0.412 | 0.749 | -4.057 |
| ETHUSDT | 5 | chronos2 | 359 | 0.04019 | 0.002976 | 0.003754 | 0.0251 | 0.0306 | 180 | 5 | 0.049 | 0.592 | 7 | 0.003 | 0.450 | -3.902 |
| ETHUSDT | 20 | hmm | 359 | 0.08629 | 0.005453 | 0.004693 | 0.0195 | 0.0195 | 52 | 1 | 0.553 | 0.841 | 1 | 0.553 | 0.841 | -2.678 |
| ETHUSDT | 20 | garch | 359 | 0.08586 | 0.004359 | 0.004457 | 0.00836 | 0.00836 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.671 |
| ETHUSDT | 20 | chronos2 | 359 | 0.08662 | 0.004695 | 0.005076 | 0.0195 | 0.0362 | 52 | 1 | 0.553 | 0.841 | 2 | 0.116 | 0.686 | -2.598 |
| LINKUSDT | 1 | hmm | 359 | 0.0212 | 0.001243 | 0.001272 | 0.00557 | 0.0139 | 359 | 2 | 0.357 | 0.881 | 5 | 0.480 | 0.707 | -5.451 |
| LINKUSDT | 1 | garch | 359 | 0.02115 | 0.001167 | 0.001225 | 0.00279 | 0.00836 | 359 | 1 | 0.104 | 0.940 | 3 | 0.747 | 0.822 | -5.469 |
| LINKUSDT | 1 | chronos2 | 359 | 0.02169 | 0.001282 | 0.001287 | 0.00279 | 0.00279 | 359 | 1 | 0.104 | 0.940 | 1 | 0.104 | 0.940 | -5.426 |
| LINKUSDT | 5 | hmm | 359 | 0.05043 | 0.002762 | 0.003361 | 0.00557 | 0.0139 | 180 | 1 | 0.513 | 0.916 | 1 | 0.513 | 0.916 | -3.626 |
| LINKUSDT | 5 | garch | 359 | 0.05006 | 0.002813 | 0.002969 | 0.0111 | 0.0195 | 180 | 1 | 0.513 | 0.916 | 3 | 0.412 | 0.749 | -3.643 |
| LINKUSDT | 5 | chronos2 | 359 | 0.05015 | 0.002685 | 0.003124 | 0.0139 | 0.0167 | 180 | 2 | 0.883 | 0.832 | 2 | 0.883 | 0.832 | -3.676 |
| LINKUSDT | 20 | hmm | 359 | 0.1002 | 0.00514 | 0.006896 | 0 | 0.0279 | 52 | 0 | 0.307 | — | 2 | 0.116 | 0.686 | -2.225 |
| LINKUSDT | 20 | garch | 359 | 0.09864 | 0.005032 | 0.005531 | 0 | 0.00557 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.248 |
| LINKUSDT | 20 | chronos2 | 359 | 0.09838 | 0.004963 | 0.006789 | 0 | 0.0251 | 52 | 0 | 0.307 | — | 2 | 0.116 | 0.686 | -2.27 |
| LTCUSDT | 1 | hmm | 359 | 0.0173 | 0.001368 | 0.001194 | 0.0111 | 0.0167 | 359 | 4 | 0.831 | 0.764 | 6 | 0.244 | 0.651 | -5.768 |
| LTCUSDT | 1 | garch | 359 | 0.01722 | 0.001346 | 0.00127 | 0.0111 | 0.0167 | 359 | 4 | 0.831 | 0.764 | 6 | 0.244 | 0.651 | -5.794 |
| LTCUSDT | 1 | chronos2 | 359 | 0.01761 | 0.001427 | 0.001256 | 0.00836 | 0.0111 | 359 | 3 | 0.747 | 0.822 | 4 | 0.831 | 0.764 | -5.722 |
| LTCUSDT | 5 | hmm | 359 | 0.03972 | 0.002357 | 0.002732 | 0 | 0.0167 | 180 | 0 | 0.057 | — | 4 | 0.156 | 0.669 | -4.066 |
| LTCUSDT | 5 | garch | 359 | 0.03953 | 0.002248 | 0.002666 | 0.00279 | 0.0139 | 180 | 0 | 0.057 | — | 3 | 0.412 | 0.749 | -4.07 |
| LTCUSDT | 5 | chronos2 | 359 | 0.03945 | 0.002223 | 0.003175 | 0.0167 | 0.0223 | 180 | 2 | 0.883 | 0.832 | 5 | 0.049 | 0.592 | -4.028 |
| LTCUSDT | 20 | hmm | 359 | 0.07574 | 0.004743 | 0.004706 | 0 | 0.00836 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.645 |
| LTCUSDT | 20 | garch | 359 | 0.07591 | 0.004558 | 0.005045 | 0 | 0.00836 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.653 |
| LTCUSDT | 20 | chronos2 | 359 | 0.07307 | 0.003717 | 0.005207 | 0.00557 | 0.0139 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.56 |
| SOLUSDT | 1 | hmm | 359 | 0.02201 | 0.001127 | 0.001571 | 0.00279 | 0.00557 | 359 | 1 | 0.104 | 0.940 | 2 | 0.357 | 0.881 | -5.417 |
| SOLUSDT | 1 | garch | 359 | 0.02204 | 0.001186 | 0.001555 | 0.00557 | 0.00836 | 359 | 2 | 0.357 | 0.881 | 3 | 0.747 | 0.822 | -5.41 |
| SOLUSDT | 1 | chronos2 | 359 | 0.02328 | 0.001392 | 0.00165 | 0.00557 | 0.0111 | 359 | 2 | 0.357 | 0.881 | 4 | 0.831 | 0.764 | -5.273 |
| SOLUSDT | 5 | hmm | 359 | 0.04866 | 0.003041 | 0.002961 | 0.0139 | 0.00836 | 180 | 4 | 0.156 | 0.669 | 2 | 0.883 | 0.832 | -3.747 |
| SOLUSDT | 5 | garch | 359 | 0.04865 | 0.002801 | 0.00304 | 0.00836 | 0.0111 | 180 | 2 | 0.883 | 0.832 | 2 | 0.883 | 0.832 | -3.757 |
| SOLUSDT | 5 | chronos2 | 359 | 0.04969 | 0.003043 | 0.003429 | 0.0111 | 0.0223 | 180 | 2 | 0.883 | 0.832 | 4 | 0.156 | 0.669 | -3.745 |
| SOLUSDT | 20 | hmm | 359 | 0.1034 | 0.006243 | 0.005739 | 0.0111 | 0.00279 | 52 | 0 | 0.307 | — | 0 | 0.307 | — | -2.331 |
| SOLUSDT | 20 | garch | 359 | 0.1035 | 0.00563 | 0.005345 | 0.00557 | 0.00557 | 52 | 0 | 0.307 | — | 0 | 0.307 | — | -2.343 |
| SOLUSDT | 20 | chronos2 | 359 | 0.1041 | 0.006345 | 0.005794 | 0.00557 | 0.0111 | 52 | 0 | 0.307 | — | 0 | 0.307 | — | -2.344 |
| TRXUSDT | 1 | hmm | 359 | 0.009968 | 0.0006116 | 0.000704 | 0.00557 | 0.00836 | 359 | 2 | 0.357 | 0.881 | 3 | 0.747 | 0.822 | -7.041 |
| TRXUSDT | 1 | garch | 359 | 0.009804 | 0.0006456 | 0.0007168 | 0.00557 | 0.00836 | 359 | 2 | 0.357 | 0.881 | 3 | 0.747 | 0.822 | -7.067 |
| TRXUSDT | 1 | chronos2 | 359 | 0.01067 | 0.0008879 | 0.0008284 | 0.00557 | 0.00279 | 359 | 2 | 0.357 | 0.881 | 1 | 0.104 | 0.940 | -7.003 |
| TRXUSDT | 5 | hmm | 359 | 0.02175 | 0.001598 | 0.00257 | 0 | 0.00557 | 180 | 0 | 0.057 | — | 1 | 0.513 | 0.916 | -4.39 |
| TRXUSDT | 5 | garch | 359 | 0.02146 | 0.001428 | 0.002359 | 0.00279 | 0.00557 | 180 | 0 | 0.057 | — | 1 | 0.513 | 0.916 | -4.603 |
| TRXUSDT | 5 | chronos2 | 359 | 0.0216 | 0.001508 | 0.002335 | 0.00836 | 0.0167 | 180 | 1 | 0.513 | 0.916 | 3 | 0.412 | 0.749 | -4.439 |
| TRXUSDT | 20 | hmm | 359 | 0.04698 | 0.004009 | 0.004595 | 0.00279 | 0.00557 | 52 | 1 | 0.553 | 0.841 | 0 | 0.307 | — | -3.16 |
| TRXUSDT | 20 | garch | 359 | 0.04572 | 0.002923 | 0.003551 | 0 | 0.00836 | 52 | 0 | 0.307 | — | 0 | 0.307 | — | -3.127 |
| TRXUSDT | 20 | chronos2 | 359 | 0.04565 | 0.003831 | 0.004788 | 0.00836 | 0.0362 | 52 | 0 | 0.307 | — | 0 | 0.307 | — | -2.717 |
| XRPUSDT | 1 | hmm | 359 | 0.01891 | 0.001135 | 0.001232 | 0.0139 | 0.00279 | 359 | 5 | 0.480 | 0.707 | 1 | 0.104 | 0.940 | -5.726 |
| XRPUSDT | 1 | garch | 359 | 0.0191 | 0.001263 | 0.001377 | 0.0111 | 0.0139 | 359 | 4 | 0.831 | 0.764 | 5 | 0.480 | 0.707 | -5.66 |
| XRPUSDT | 1 | chronos2 | 359 | 0.02188 | 0.001745 | 0.001433 | 0 | 0.00279 | 359 | 0 | 0.007 | — | 1 | 0.104 | 0.940 | -5.687 |
| XRPUSDT | 5 | hmm | 359 | 0.04408 | 0.002493 | 0.004579 | 0.00557 | 0.0111 | 180 | 0 | 0.057 | — | 2 | 0.883 | 0.832 | -3.919 |
| XRPUSDT | 5 | garch | 359 | 0.04423 | 0.002638 | 0.004731 | 0.00557 | 0.0195 | 180 | 1 | 0.513 | 0.916 | 2 | 0.883 | 0.832 | -3.858 |
| XRPUSDT | 5 | chronos2 | 359 | 0.04602 | 0.003105 | 0.004484 | 0.00836 | 0.0223 | 180 | 2 | 0.883 | 0.832 | 4 | 0.156 | 0.669 | -3.759 |
| XRPUSDT | 20 | hmm | 359 | 0.09609 | 0.004515 | 0.01502 | 0 | 0.0223 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.447 |
| XRPUSDT | 20 | garch | 359 | 0.09421 | 0.005712 | 0.01416 | 0 | 0.0223 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.444 |
| XRPUSDT | 20 | chronos2 | 359 | 0.0964 | 0.006413 | 0.01715 | 0 | 0.0251 | 52 | 0 | 0.307 | — | 1 | 0.553 | 0.841 | -2.322 |

### lago_cierre_c20261101 (proxy): 4 modelos sobre la submuestra de Toto (uno de cada 5 origenes)

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | n_test | x 1 % | Kupiec 1 % p | Chr. 1 % p | x 99 % | Kupiec 99 % p | Chr. 99 % p | QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | 1 | hmm | 50 | 0.002127 | 0.000117 | 0.000132 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -10.13 |
| AUDCAD | 1 | garch | 50 | 0.002154 | 9.792e-05 | 0.0001178 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -10.03 |
| AUDCAD | 1 | chronos2 | 50 | 0.002247 | 0.0002028 | 0.0001489 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.08 |
| AUDCAD | 1 | toto | 50 | 0.002201 | 0.0001076 | 0.0001075 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.27 |
| AUDCAD | 5 | hmm | 50 | 0.004361 | 0.0002696 | 0.0002833 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.385 |
| AUDCAD | 5 | garch | 50 | 0.004202 | 0.0002276 | 0.0002262 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.362 |
| AUDCAD | 5 | chronos2 | 50 | 0.004227 | 0.0003065 | 0.0002322 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.339 |
| AUDCAD | 5 | toto | 50 | 0.00449 | 0.0004516 | 0.0002768 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.8 |
| AUDCAD | 20 | hmm | 50 | 0.00782 | 0.0005751 | 0.000479 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.984 |
| AUDCAD | 20 | garch | 50 | 0.007221 | 0.0004375 | 0.0005117 | 0 | 0.04 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.955 |
| AUDCAD | 20 | chronos2 | 50 | 0.007583 | 0.0006532 | 0.0005892 | 0 | 0.02 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.96 |
| AUDCAD | 20 | toto | 50 | 0.008374 | 0.001047 | 0.000642 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.518 |
| AUDCHF | 1 | hmm | 50 | 0.00212 | 0.0001169 | 0.0001118 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.09 |
| AUDCHF | 1 | garch | 50 | 0.002126 | 0.0001178 | 0.0001259 | 0.02 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -10.06 |
| AUDCHF | 1 | chronos2 | 50 | 0.002234 | 0.0001948 | 0.0001596 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.989 |
| AUDCHF | 1 | toto | 50 | 0.00207 | 0.0001638 | 0.000169 | 0.06 | 0.04 | 50 | 3 | 0.015 | 0.611 | 2 | 0.107 | 0.680 | -9.7 |
| AUDCHF | 5 | hmm | 50 | 0.004544 | 0.0003177 | 0.0002276 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.268 |
| AUDCHF | 5 | garch | 50 | 0.00449 | 0.0002842 | 0.0002625 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.261 |
| AUDCHF | 5 | chronos2 | 50 | 0.004603 | 0.0003164 | 0.0002301 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.171 |
| AUDCHF | 5 | toto | 50 | 0.004431 | 0.0004588 | 0.0004596 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.845 |
| AUDCHF | 20 | hmm | 50 | 0.007785 | 0.0008607 | 0.0004577 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.865 |
| AUDCHF | 20 | garch | 50 | 0.007282 | 0.0005855 | 0.0005257 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.857 |
| AUDCHF | 20 | chronos2 | 50 | 0.007558 | 0.000709 | 0.0005198 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.786 |
| AUDCHF | 20 | toto | 50 | 0.008013 | 0.001995 | 0.001706 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.715 |
| AUDJPY | 1 | hmm | 50 | 0.002983 | 0.0001751 | 0.0001507 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -9.294 |
| AUDJPY | 1 | garch | 50 | 0.003041 | 0.0001952 | 0.0001549 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -9.309 |
| AUDJPY | 1 | chronos2 | 50 | 0.003278 | 0.0002738 | 0.000206 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.333 |
| AUDJPY | 1 | toto | 50 | 0.003128 | 0.0001685 | 0.0002611 | 0.04 | 0.04 | 50 | 2 | 0.107 | 0.680 | 2 | 0.107 | 0.680 | -7.886 |
| AUDJPY | 5 | hmm | 50 | 0.005957 | 0.0003743 | 0.0003226 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.818 |
| AUDJPY | 5 | garch | 50 | 0.005979 | 0.0003357 | 0.0003395 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.831 |
| AUDJPY | 5 | chronos2 | 50 | 0.006312 | 0.0004184 | 0.0003066 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.762 |
| AUDJPY | 5 | toto | 50 | 0.005857 | 0.0007334 | 0.0003047 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.192 |
| AUDJPY | 20 | hmm | 50 | 0.01205 | 0.0007474 | 0.0006739 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.465 |
| AUDJPY | 20 | garch | 50 | 0.01214 | 0.0006015 | 0.0007223 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.48 |
| AUDJPY | 20 | chronos2 | 50 | 0.01116 | 0.001013 | 0.0007112 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.419 |
| AUDJPY | 20 | toto | 50 | 0.01235 | 0.01236 | 0.004238 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -5.946 |
| AUDNZD | 1 | hmm | 50 | 0.0014 | 7.217e-05 | 6.708e-05 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -10.86 |
| AUDNZD | 1 | garch | 50 | 0.001383 | 6.84e-05 | 7.851e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.97 |
| AUDNZD | 1 | chronos2 | 50 | 0.001457 | 0.0001134 | 9.947e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.74 |
| AUDNZD | 1 | toto | 50 | 0.001664 | 8.385e-05 | 8.92e-05 | 0.02 | 0.04 | 50 | 1 | 0.532 | 0.838 | 2 | 0.107 | 0.680 | -10.75 |
| AUDNZD | 5 | hmm | 50 | 0.003541 | 0.0001873 | 0.0001402 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.9 |
| AUDNZD | 5 | garch | 50 | 0.003474 | 0.0001906 | 0.0001578 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9 |
| AUDNZD | 5 | chronos2 | 50 | 0.003632 | 0.0002051 | 0.000163 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.012 |
| AUDNZD | 5 | toto | 50 | 0.004132 | 0.000302 | 0.0003315 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -8.809 |
| AUDNZD | 20 | hmm | 50 | 0.007143 | 0.0003096 | 0.0002924 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.551 |
| AUDNZD | 20 | garch | 50 | 0.0068 | 0.0002906 | 0.0003151 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.561 |
| AUDNZD | 20 | chronos2 | 50 | 0.007183 | 0.0004931 | 0.0003859 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.587 |
| AUDNZD | 20 | toto | 50 | 0.008151 | 0.001936 | 0.001263 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.4 |
| AUDUSD | 1 | hmm | 50 | 0.002816 | 0.0001354 | 0.0001992 | 0.02 | 0.04 | 50 | 1 | 0.532 | 0.838 | 2 | 0.107 | 0.680 | -9.473 |
| AUDUSD | 1 | garch | 50 | 0.002864 | 0.0001274 | 0.0002186 | 0.02 | 0.04 | 50 | 1 | 0.532 | 0.838 | 2 | 0.107 | 0.680 | -9.317 |
| AUDUSD | 1 | chronos2 | 50 | 0.002956 | 0.0002338 | 0.0002511 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -9.298 |
| AUDUSD | 1 | toto | 50 | 0.002994 | 0.0002986 | 0.0003554 | 0.06 | 0.04 | 50 | 3 | 0.015 | 0.531 | 2 | 0.107 | 0.680 | -7.871 |
| AUDUSD | 5 | hmm | 50 | 0.0062 | 0.0003205 | 0.0007165 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -7.956 |
| AUDUSD | 5 | garch | 50 | 0.005992 | 0.0003016 | 0.0006972 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -7.896 |
| AUDUSD | 5 | chronos2 | 50 | 0.006257 | 0.0003674 | 0.0008013 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.807 |
| AUDUSD | 5 | toto | 50 | 0.006596 | 0.0005644 | 0.0005092 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.806 |
| AUDUSD | 20 | hmm | 50 | 0.01476 | 0.0007647 | 0.001153 | 0.02 | 0.04 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.535 |
| AUDUSD | 20 | garch | 50 | 0.01299 | 0.0005903 | 0.0009892 | 0.02 | 0.02 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.408 |
| AUDUSD | 20 | chronos2 | 50 | 0.01378 | 0.0007722 | 0.001381 | 0 | 0.04 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.298 |
| AUDUSD | 20 | toto | 50 | 0.01441 | 0.002483 | 0.002526 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.396 |
| CADCHF | 1 | hmm | 50 | 0.002055 | 0.0001032 | 0.0001046 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -10.11 |
| CADCHF | 1 | garch | 50 | 0.002035 | 0.0001163 | 9.161e-05 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -10.08 |
| CADCHF | 1 | chronos2 | 50 | 0.001971 | 0.0001252 | 0.0001076 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.09 |
| CADCHF | 1 | toto | 50 | 0.002005 | 0.0001216 | 0.0001684 | 0.04 | 0.02 | 50 | 2 | 0.107 | 0.772 | 1 | 0.532 | 0.838 | -9.88 |
| CADCHF | 5 | hmm | 50 | 0.004204 | 0.0002556 | 0.0002015 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.732 |
| CADCHF | 5 | garch | 50 | 0.004173 | 0.0002325 | 0.0002126 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.732 |
| CADCHF | 5 | chronos2 | 50 | 0.004133 | 0.0002232 | 0.0001844 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.666 |
| CADCHF | 5 | toto | 50 | 0.004104 | 0.0002355 | 0.0005097 | 0 | 0.04 | 50 | 0 | 0.316 | — | 2 | 0.107 | 0.680 | -8.612 |
| CADCHF | 20 | hmm | 50 | 0.007035 | 0.000539 | 0.0003785 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.343 |
| CADCHF | 20 | garch | 50 | 0.006706 | 0.000484 | 0.0003987 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.337 |
| CADCHF | 20 | chronos2 | 50 | 0.006439 | 0.0005112 | 0.0004043 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.331 |
| CADCHF | 20 | toto | 50 | 0.007088 | 0.0006989 | 0.002053 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.177 |
| CADJPY | 1 | hmm | 50 | 0.002815 | 0.0004259 | 0.0001094 | 0.08 | 0 | 50 | 4 | 0.002 | 0.399 | 0 | 0.316 | — | -8.207 |
| CADJPY | 1 | garch | 50 | 0.002827 | 0.0005809 | 0.0001222 | 0.08 | 0 | 50 | 4 | 0.002 | 0.399 | 0 | 0.316 | — | -8.691 |
| CADJPY | 1 | chronos2 | 50 | 0.002902 | 0.0002804 | 0.0001346 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.798 |
| CADJPY | 1 | toto | 50 | 0.003028 | 0.0007626 | 0.0002174 | 0.12 | 0.1 | 50 | 6 | 0.000 | 0.195 | 5 | 0.000 | 0.343 | -4.143 |
| CADJPY | 5 | hmm | 50 | 0.005586 | 0.0007437 | 0.0002672 | 0.06 | 0.02 | 50 | 3 | 0.015 | 0.531 | 1 | 0.532 | 0.838 | -7.982 |
| CADJPY | 5 | garch | 50 | 0.005587 | 0.0007256 | 0.0002814 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.046 |
| CADJPY | 5 | chronos2 | 50 | 0.005581 | 0.0005701 | 0.0002318 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.973 |
| CADJPY | 5 | toto | 50 | 0.005675 | 0.0009894 | 0.0002734 | 0.06 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -7.469 |
| CADJPY | 20 | hmm | 50 | 0.01048 | 0.0005128 | 0.0005422 | 0 | 0.02 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.703 |
| CADJPY | 20 | garch | 50 | 0.01074 | 0.0005143 | 0.0005932 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.756 |
| CADJPY | 20 | chronos2 | 50 | 0.009436 | 0.0005893 | 0.0005035 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.663 |
| CADJPY | 20 | toto | 50 | 0.01098 | 0.002341 | 0.002072 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.504 |
| CHFJPY | 1 | hmm | 50 | 0.002268 | 0.0001353 | 0.0001174 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -9.912 |
| CHFJPY | 1 | garch | 50 | 0.002263 | 0.0001398 | 0.0001102 | 0.06 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -9.93 |
| CHFJPY | 1 | chronos2 | 50 | 0.002342 | 0.0001834 | 0.0001401 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.925 |
| CHFJPY | 1 | toto | 50 | 0.002566 | 0.0003783 | 0.0002074 | 0.12 | 0.06 | 50 | 6 | 0.000 | 0.734 | 3 | 0.015 | 0.071 | -8.143 |
| CHFJPY | 5 | hmm | 50 | 0.005376 | 0.0005288 | 0.0002669 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.23 |
| CHFJPY | 5 | garch | 50 | 0.005341 | 0.0004069 | 0.0002533 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.216 |
| CHFJPY | 5 | chronos2 | 50 | 0.005194 | 0.0003254 | 0.0002474 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.123 |
| CHFJPY | 5 | toto | 50 | 0.005386 | 0.000606 | 0.0008933 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -7.249 |
| CHFJPY | 20 | hmm | 50 | 0.009859 | 0.0005267 | 0.000566 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.859 |
| CHFJPY | 20 | garch | 50 | 0.009857 | 0.0005348 | 0.0005574 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.865 |
| CHFJPY | 20 | chronos2 | 50 | 0.007814 | 0.0006991 | 0.000553 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.561 |
| CHFJPY | 20 | toto | 50 | 0.009246 | 0.007647 | 0.004426 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.394 |
| EURAUD | 1 | hmm | 50 | 0.00201 | 9.677e-05 | 9.671e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.26 |
| EURAUD | 1 | garch | 50 | 0.00197 | 0.0001023 | 9.724e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.29 |
| EURAUD | 1 | chronos2 | 50 | 0.002091 | 0.0001399 | 0.0001436 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.18 |
| EURAUD | 1 | toto | 50 | 0.00226 | 0.0001148 | 0.0001373 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -10.18 |
| EURAUD | 5 | hmm | 50 | 0.004521 | 0.0002024 | 0.0002795 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.634 |
| EURAUD | 5 | garch | 50 | 0.004351 | 0.000208 | 0.0002522 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.65 |
| EURAUD | 5 | chronos2 | 50 | 0.004583 | 0.000218 | 0.0002973 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.638 |
| EURAUD | 5 | toto | 50 | 0.00492 | 0.0006903 | 0.000581 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -8.598 |
| EURAUD | 20 | hmm | 50 | 0.009574 | 0.0004188 | 0.0006711 | 0.02 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.192 |
| EURAUD | 20 | garch | 50 | 0.008848 | 0.0004074 | 0.0004893 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.235 |
| EURAUD | 20 | chronos2 | 50 | 0.009325 | 0.000573 | 0.0006215 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.23 |
| EURAUD | 20 | toto | 50 | 0.01143 | 0.002659 | 0.001466 | 0.04 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.047 |
| EURCAD | 1 | hmm | 50 | 0.001572 | 0.0001513 | 0.0001189 | 0.02 | 0.02 | 50 | 1 | 0.532 | — | 1 | 0.532 | 0.838 | -10.48 |
| EURCAD | 1 | garch | 50 | 0.001556 | 0.0001314 | 0.0001087 | 0.02 | 0.02 | 50 | 1 | 0.532 | — | 1 | 0.532 | 0.838 | -10.6 |
| EURCAD | 1 | chronos2 | 50 | 0.001515 | 9.874e-05 | 9.194e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.56 |
| EURCAD | 1 | toto | 50 | 0.001536 | 0.0001583 | 0.0001153 | 0.04 | 0.04 | 50 | 2 | 0.107 | 0.772 | 2 | 0.107 | 0.680 | -10.31 |
| EURCAD | 5 | hmm | 50 | 0.003223 | 0.0002014 | 0.0001991 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.119 |
| EURCAD | 5 | garch | 50 | 0.003204 | 0.000189 | 0.0001987 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.175 |
| EURCAD | 5 | chronos2 | 50 | 0.003062 | 0.000297 | 0.0001749 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.148 |
| EURCAD | 5 | toto | 50 | 0.003082 | 0.0007917 | 0.0002305 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -8.91 |
| EURCAD | 20 | hmm | 50 | 0.00668 | 0.0004382 | 0.0004175 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.755 |
| EURCAD | 20 | garch | 50 | 0.006799 | 0.0007099 | 0.0004258 | 0.04 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.738 |
| EURCAD | 20 | chronos2 | 50 | 0.00606 | 0.0004241 | 0.000384 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.669 |
| EURCAD | 20 | toto | 50 | 0.006245 | 0.003877 | 0.0006076 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.513 |
| EURCHF | 1 | hmm | 50 | 0.001601 | 0.0002293 | 5.859e-05 | 0.04 | 0 | 50 | 2 | 0.107 | 0.772 | 0 | 0.316 | — | -10.16 |
| EURCHF | 1 | garch | 50 | 0.001567 | 0.0002486 | 6.258e-05 | 0.04 | 0 | 50 | 2 | 0.107 | 0.772 | 0 | 0.316 | — | -10.26 |
| EURCHF | 1 | chronos2 | 50 | 0.001548 | 0.0002008 | 7.797e-05 | 0.04 | 0 | 50 | 2 | 0.107 | 0.772 | 0 | 0.316 | — | -10.23 |
| EURCHF | 1 | toto | 50 | 0.001753 | 0.0002451 | 8.856e-05 | 0.04 | 0.04 | 50 | 2 | 0.107 | 0.772 | 2 | 0.107 | 0.680 | -9.942 |
| EURCHF | 5 | hmm | 50 | 0.003019 | 0.0002161 | 0.0001245 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.244 |
| EURCHF | 5 | garch | 50 | 0.00297 | 0.0002085 | 0.0001305 | 0.02 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -9.292 |
| EURCHF | 5 | chronos2 | 50 | 0.002985 | 0.0002221 | 0.0001225 | 0.04 | 0 | 50 | 2 | 0.107 | 0.772 | 0 | 0.316 | — | -8.936 |
| EURCHF | 5 | toto | 50 | 0.003191 | 0.0001736 | 0.0001758 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.948 |
| EURCHF | 20 | hmm | 50 | 0.00615 | 0.0003006 | 0.0002555 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.909 |
| EURCHF | 20 | garch | 50 | 0.006077 | 0.0003507 | 0.000265 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.86 |
| EURCHF | 20 | chronos2 | 50 | 0.006011 | 0.0002758 | 0.000262 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.628 |
| EURCHF | 20 | toto | 50 | 0.006391 | 0.0005827 | 0.000494 | 0.04 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.882 |
| EURGBP | 1 | hmm | 50 | 0.001214 | 6.361e-05 | 8.722e-05 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -11.1 |
| EURGBP | 1 | garch | 50 | 0.001216 | 6.535e-05 | 7.46e-05 | 0 | 0.04 | 50 | 0 | 0.316 | — | 2 | 0.107 | 0.680 | -11.04 |
| EURGBP | 1 | chronos2 | 50 | 0.00125 | 8.333e-05 | 7.78e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -11.1 |
| EURGBP | 1 | toto | 50 | 0.001368 | 9.797e-05 | 0.0001095 | 0.04 | 0.1 | 50 | 2 | 0.107 | 0.680 | 5 | 0.000 | 0.487 | -10.99 |
| EURGBP | 5 | hmm | 50 | 0.002383 | 0.0001191 | 0.0001531 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.657 |
| EURGBP | 5 | garch | 50 | 0.002322 | 0.0001268 | 0.000135 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.638 |
| EURGBP | 5 | chronos2 | 50 | 0.002432 | 0.0002049 | 0.000149 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.6 |
| EURGBP | 5 | toto | 50 | 0.002479 | 0.0002246 | 0.0001936 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 1.000 | -9.365 |
| EURGBP | 20 | hmm | 50 | 0.005104 | 0.0002377 | 0.0003517 | 0.02 | 0 | 13 | 1 | 0.121 | — | 0 | 0.609 | — | -8.281 |
| EURGBP | 20 | garch | 50 | 0.004967 | 0.0003495 | 0.0002916 | 0.04 | 0 | 13 | 1 | 0.121 | — | 0 | 0.609 | — | -8.289 |
| EURGBP | 20 | chronos2 | 50 | 0.005038 | 0.0004956 | 0.0003451 | 0.06 | 0 | 13 | 1 | 0.121 | — | 0 | 0.609 | — | -8.225 |
| EURGBP | 20 | toto | 50 | 0.005837 | 0.001026 | 0.0007454 | 0.06 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -8.21 |
| EURJPY | 1 | hmm | 50 | 0.002273 | 0.0004072 | 0.0001065 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -9.37 |
| EURJPY | 1 | garch | 50 | 0.002286 | 0.0005134 | 0.0001048 | 0.06 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -9.262 |
| EURJPY | 1 | chronos2 | 50 | 0.002254 | 0.0001574 | 0.0001269 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.048 |
| EURJPY | 1 | toto | 50 | 0.002579 | 0.000648 | 0.000114 | 0.06 | 0.02 | 50 | 3 | 0.015 | 0.531 | 1 | 0.532 | 0.838 | -5.568 |
| EURJPY | 5 | hmm | 50 | 0.004787 | 0.0004636 | 0.0002302 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.365 |
| EURJPY | 5 | garch | 50 | 0.004763 | 0.0004752 | 0.0002285 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.341 |
| EURJPY | 5 | chronos2 | 50 | 0.004708 | 0.0002945 | 0.0002147 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.989 |
| EURJPY | 5 | toto | 50 | 0.005266 | 0.0008013 | 0.0008149 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -6.622 |
| EURJPY | 20 | hmm | 50 | 0.009228 | 0.0003886 | 0.0005023 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.016 |
| EURJPY | 20 | garch | 50 | 0.009684 | 0.0003226 | 0.0005188 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.975 |
| EURJPY | 20 | chronos2 | 50 | 0.008178 | 0.0005617 | 0.0005 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.828 |
| EURJPY | 20 | toto | 50 | 0.01097 | 0.007485 | 0.006638 | 0.06 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.189 |
| EURNZD | 1 | hmm | 50 | 0.002055 | 9.011e-05 | 9.591e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.13 |
| EURNZD | 1 | garch | 50 | 0.002046 | 9.536e-05 | 9.875e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.14 |
| EURNZD | 1 | chronos2 | 50 | 0.002067 | 0.000119 | 0.0001278 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.09 |
| EURNZD | 1 | toto | 50 | 0.00215 | 7.617e-05 | 0.0001502 | 0 | 0.06 | 50 | 0 | 0.316 | — | 3 | 0.015 | 0.531 | -9.972 |
| EURNZD | 5 | hmm | 50 | 0.004155 | 0.000197 | 0.0002317 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.705 |
| EURNZD | 5 | garch | 50 | 0.003979 | 0.0001999 | 0.0002209 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.705 |
| EURNZD | 5 | chronos2 | 50 | 0.004011 | 0.0002206 | 0.0002478 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.695 |
| EURNZD | 5 | toto | 50 | 0.003845 | 0.0008468 | 0.0002762 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.632 |
| EURNZD | 20 | hmm | 50 | 0.009285 | 0.0003924 | 0.000543 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.27 |
| EURNZD | 20 | garch | 50 | 0.008767 | 0.0003702 | 0.000467 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.3 |
| EURNZD | 20 | chronos2 | 50 | 0.008312 | 0.0004788 | 0.0005577 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.31 |
| EURNZD | 20 | toto | 50 | 0.008698 | 0.004806 | 0.001047 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.928 |
| EURUSD | 1 | hmm | 50 | 0.001689 | 9.84e-05 | 9.591e-05 | 0.02 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -10.55 |
| EURUSD | 1 | garch | 50 | 0.001665 | 8.862e-05 | 9.16e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.51 |
| EURUSD | 1 | chronos2 | 50 | 0.001738 | 0.0001236 | 0.0001282 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.51 |
| EURUSD | 1 | toto | 50 | 0.001677 | 8.102e-05 | 9.424e-05 | 0.02 | 0.02 | 50 | 1 | 0.532 | — | 1 | 0.532 | 0.838 | -10.47 |
| EURUSD | 5 | hmm | 50 | 0.00439 | 0.000183 | 0.0002308 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.765 |
| EURUSD | 5 | garch | 50 | 0.004238 | 0.0001934 | 0.000409 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.725 |
| EURUSD | 5 | chronos2 | 50 | 0.004381 | 0.0002336 | 0.0003753 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.65 |
| EURUSD | 5 | toto | 50 | 0.004342 | 0.0002625 | 0.0005257 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.597 |
| EURUSD | 20 | hmm | 50 | 0.009751 | 0.0004332 | 0.0005034 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.294 |
| EURUSD | 20 | garch | 50 | 0.009014 | 0.0004175 | 0.0004401 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.237 |
| EURUSD | 20 | chronos2 | 50 | 0.009395 | 0.0005223 | 0.0005624 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.269 |
| EURUSD | 20 | toto | 50 | 0.009166 | 0.001023 | 0.0006007 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.238 |
| GBPAUD | 1 | hmm | 50 | 0.002091 | 8.467e-05 | 9.441e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.07 |
| GBPAUD | 1 | garch | 50 | 0.002079 | 9.29e-05 | 9.796e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.08 |
| GBPAUD | 1 | chronos2 | 50 | 0.002206 | 0.0001176 | 0.0001389 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -10.01 |
| GBPAUD | 1 | toto | 50 | 0.002453 | 0.0001266 | 0.0001703 | 0.02 | 0.04 | 50 | 1 | 0.532 | 0.838 | 2 | 0.107 | 0.680 | -9.748 |
| GBPAUD | 5 | hmm | 50 | 0.004315 | 0.0001994 | 0.0002168 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.634 |
| GBPAUD | 5 | garch | 50 | 0.004259 | 0.0002101 | 0.000218 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.627 |
| GBPAUD | 5 | chronos2 | 50 | 0.0044 | 0.0002016 | 0.0002345 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.59 |
| GBPAUD | 5 | toto | 50 | 0.004869 | 0.001064 | 0.0003542 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.552 |
| GBPAUD | 20 | hmm | 50 | 0.009543 | 0.0005917 | 0.0005057 | 0.02 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.232 |
| GBPAUD | 20 | garch | 50 | 0.009458 | 0.0005093 | 0.0004431 | 0.02 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.237 |
| GBPAUD | 20 | chronos2 | 50 | 0.009758 | 0.0008815 | 0.0005716 | 0.02 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.22 |
| GBPAUD | 20 | toto | 50 | 0.011 | 0.003501 | 0.001606 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.086 |
| GBPCAD | 1 | hmm | 50 | 0.002091 | 9.555e-05 | 0.0001558 | 0.04 | 0.02 | 50 | 2 | 0.107 | 0.680 | 1 | 0.532 | 0.838 | -10.07 |
| GBPCAD | 1 | garch | 50 | 0.00211 | 8.479e-05 | 0.0001736 | 0.04 | 0.02 | 50 | 2 | 0.107 | 0.680 | 1 | 0.532 | 0.838 | -9.991 |
| GBPCAD | 1 | chronos2 | 50 | 0.002069 | 0.0001165 | 0.0001061 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.816 |
| GBPCAD | 1 | toto | 50 | 0.002081 | 0.0001353 | 8.848e-05 | 0.04 | 0.02 | 50 | 2 | 0.107 | 0.680 | 1 | 0.532 | 0.838 | -9.917 |
| GBPCAD | 5 | hmm | 50 | 0.003307 | 0.0001841 | 0.0001871 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.819 |
| GBPCAD | 5 | garch | 50 | 0.00334 | 0.0001876 | 0.0001925 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.794 |
| GBPCAD | 5 | chronos2 | 50 | 0.00324 | 0.0003008 | 0.0001921 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.812 |
| GBPCAD | 5 | toto | 50 | 0.003556 | 0.0009866 | 0.000291 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.74 |
| GBPCAD | 20 | hmm | 50 | 0.006114 | 0.0003676 | 0.0003596 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.446 |
| GBPCAD | 20 | garch | 50 | 0.006365 | 0.0003686 | 0.0003897 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.406 |
| GBPCAD | 20 | chronos2 | 50 | 0.005556 | 0.0004169 | 0.0003576 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.252 |
| GBPCAD | 20 | toto | 50 | 0.00675 | 0.005434 | 0.001301 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.114 |
| GBPCHF | 1 | hmm | 50 | 0.001948 | 0.000172 | 8.933e-05 | 0.04 | 0 | 50 | 2 | 0.107 | 0.772 | 0 | 0.316 | — | -9.958 |
| GBPCHF | 1 | garch | 50 | 0.001926 | 0.0001452 | 9.352e-05 | 0.02 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -10.17 |
| GBPCHF | 1 | chronos2 | 50 | 0.001862 | 0.0001035 | 0.0001277 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -10.2 |
| GBPCHF | 1 | toto | 50 | 0.001994 | 0.0001833 | 0.0001645 | 0.08 | 0.04 | 50 | 4 | 0.002 | 0.467 | 2 | 0.107 | 0.680 | -10.07 |
| GBPCHF | 5 | hmm | 50 | 0.003615 | 0.0002494 | 0.0001661 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.81 |
| GBPCHF | 5 | garch | 50 | 0.003592 | 0.0001973 | 0.0001856 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.813 |
| GBPCHF | 5 | chronos2 | 50 | 0.003519 | 0.000196 | 0.000234 | 0 | 0.04 | 50 | 0 | 0.316 | — | 2 | 0.107 | 0.680 | -8.679 |
| GBPCHF | 5 | toto | 50 | 0.003799 | 0.0002439 | 0.0003164 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.617 |
| GBPCHF | 20 | hmm | 50 | 0.006625 | 0.0005963 | 0.000318 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.477 |
| GBPCHF | 20 | garch | 50 | 0.00636 | 0.0004185 | 0.0003503 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.486 |
| GBPCHF | 20 | chronos2 | 50 | 0.006106 | 0.0004809 | 0.0004012 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.329 |
| GBPCHF | 20 | toto | 50 | 0.006753 | 0.0006291 | 0.0007635 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.457 |
| GBPJPY | 1 | hmm | 50 | 0.002635 | 0.0001711 | 0.000125 | 0.08 | 0 | 50 | 4 | 0.002 | 0.399 | 0 | 0.316 | — | -9.252 |
| GBPJPY | 1 | garch | 50 | 0.002649 | 0.0003187 | 0.0001292 | 0.1 | 0 | 50 | 5 | 0.000 | 0.487 | 0 | 0.316 | — | -9.227 |
| GBPJPY | 1 | chronos2 | 50 | 0.002641 | 0.0001862 | 0.0001453 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.387 |
| GBPJPY | 1 | toto | 50 | 0.003109 | 0.001019 | 0.0001979 | 0.16 | 0.04 | 50 | 8 | 0.000 | 0.742 | 2 | 0.107 | 0.680 | -4.016 |
| GBPJPY | 5 | hmm | 50 | 0.005184 | 0.0004689 | 0.0002536 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.198 |
| GBPJPY | 5 | garch | 50 | 0.005236 | 0.0005571 | 0.000263 | 0.06 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -8.217 |
| GBPJPY | 5 | chronos2 | 50 | 0.005132 | 0.0003014 | 0.0002359 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.093 |
| GBPJPY | 5 | toto | 50 | 0.005867 | 0.001366 | 0.0006063 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -6.719 |
| GBPJPY | 20 | hmm | 50 | 0.009702 | 0.0004907 | 0.0005181 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.861 |
| GBPJPY | 20 | garch | 50 | 0.01007 | 0.0004295 | 0.000565 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.871 |
| GBPJPY | 20 | chronos2 | 50 | 0.009286 | 0.0006401 | 0.0005235 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.774 |
| GBPJPY | 20 | toto | 50 | 0.01132 | 0.005814 | 0.005018 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.401 |
| GBPNZD | 1 | hmm | 50 | 0.002 | 7.687e-05 | 8.921e-05 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -10.22 |
| GBPNZD | 1 | garch | 50 | 0.002021 | 7.907e-05 | 9.28e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.2 |
| GBPNZD | 1 | chronos2 | 50 | 0.001982 | 0.0001111 | 0.00012 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.18 |
| GBPNZD | 1 | toto | 50 | 0.002077 | 7.182e-05 | 0.000154 | 0.04 | 0.04 | 50 | 2 | 0.107 | 0.680 | 2 | 0.107 | 0.680 | -9.683 |
| GBPNZD | 5 | hmm | 50 | 0.003942 | 0.0002043 | 0.0001898 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.745 |
| GBPNZD | 5 | garch | 50 | 0.003908 | 0.0002309 | 0.0001962 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.749 |
| GBPNZD | 5 | chronos2 | 50 | 0.003932 | 0.0002182 | 0.0002316 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.752 |
| GBPNZD | 5 | toto | 50 | 0.004062 | 0.0005302 | 0.0003743 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.604 |
| GBPNZD | 20 | hmm | 50 | 0.008368 | 0.0004373 | 0.0003858 | 0.02 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.349 |
| GBPNZD | 20 | garch | 50 | 0.008421 | 0.0003784 | 0.0003941 | 0.02 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -7.373 |
| GBPNZD | 20 | chronos2 | 50 | 0.008019 | 0.0004579 | 0.0004702 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.368 |
| GBPNZD | 20 | toto | 50 | 0.007956 | 0.004448 | 0.001087 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.182 |
| GBPUSD | 1 | hmm | 50 | 0.002459 | 0.0001177 | 0.0001728 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -9.768 |
| GBPUSD | 1 | garch | 50 | 0.00239 | 0.0001049 | 0.000165 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -9.851 |
| GBPUSD | 1 | chronos2 | 50 | 0.00248 | 0.0001204 | 0.0001263 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.815 |
| GBPUSD | 1 | toto | 50 | 0.002467 | 0.0001339 | 0.0001711 | 0.02 | 0.08 | 50 | 1 | 0.532 | 0.838 | 4 | 0.002 | 0.399 | -9.521 |
| GBPUSD | 5 | hmm | 50 | 0.004667 | 0.0002125 | 0.0004498 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.419 |
| GBPUSD | 5 | garch | 50 | 0.004479 | 0.0002087 | 0.0004286 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.412 |
| GBPUSD | 5 | chronos2 | 50 | 0.004512 | 0.000248 | 0.0004781 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.389 |
| GBPUSD | 5 | toto | 50 | 0.004685 | 0.000505 | 0.0005051 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.279 |
| GBPUSD | 20 | hmm | 50 | 0.008818 | 0.0004217 | 0.0004628 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.054 |
| GBPUSD | 20 | garch | 50 | 0.008294 | 0.0004188 | 0.000439 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.011 |
| GBPUSD | 20 | chronos2 | 50 | 0.00828 | 0.00054 | 0.0004984 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.03 |
| GBPUSD | 20 | toto | 50 | 0.007877 | 0.002106 | 0.000808 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.905 |
| NZDCAD | 1 | hmm | 50 | 0.002496 | 9.855e-05 | 0.0001474 | 0 | 0.04 | 50 | 0 | 0.316 | — | 2 | 0.107 | 0.680 | -9.766 |
| NZDCAD | 1 | garch | 50 | 0.002502 | 0.0001011 | 0.0001622 | 0 | 0.06 | 50 | 0 | 0.316 | — | 3 | 0.015 | 0.531 | -9.663 |
| NZDCAD | 1 | chronos2 | 50 | 0.002583 | 0.0001324 | 0.000131 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.62 |
| NZDCAD | 1 | toto | 50 | 0.002609 | 0.0001812 | 0.0002229 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -9.334 |
| NZDCAD | 5 | hmm | 50 | 0.00483 | 0.0002662 | 0.0002163 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.301 |
| NZDCAD | 5 | garch | 50 | 0.004719 | 0.000239 | 0.0002245 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.273 |
| NZDCAD | 5 | chronos2 | 50 | 0.004808 | 0.0002647 | 0.000251 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.326 |
| NZDCAD | 5 | toto | 50 | 0.00476 | 0.0002334 | 0.000387 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.255 |
| NZDCAD | 20 | hmm | 50 | 0.008821 | 0.0004903 | 0.0004714 | 0 | 0.02 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.889 |
| NZDCAD | 20 | garch | 50 | 0.008648 | 0.0004481 | 0.000444 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.893 |
| NZDCAD | 20 | chronos2 | 50 | 0.008688 | 0.0005026 | 0.0006963 | 0 | 0.06 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.791 |
| NZDCAD | 20 | toto | 50 | 0.008789 | 0.0004347 | 0.001106 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.754 |
| NZDCHF | 1 | hmm | 50 | 0.002252 | 0.0002053 | 0.0001105 | 0.02 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -9.846 |
| NZDCHF | 1 | garch | 50 | 0.002246 | 0.0001919 | 0.0001155 | 0.02 | 0 | 50 | 1 | 0.532 | — | 0 | 0.316 | — | -9.885 |
| NZDCHF | 1 | chronos2 | 50 | 0.002386 | 0.0001649 | 0.0001426 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.88 |
| NZDCHF | 1 | toto | 50 | 0.00225 | 0.0002661 | 0.0001484 | 0.04 | 0.02 | 50 | 2 | 0.107 | 0.772 | 1 | 0.532 | 0.838 | -9.747 |
| NZDCHF | 5 | hmm | 50 | 0.004189 | 0.0002828 | 0.0002284 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.395 |
| NZDCHF | 5 | garch | 50 | 0.004134 | 0.0002675 | 0.0002455 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.394 |
| NZDCHF | 5 | chronos2 | 50 | 0.004191 | 0.0002842 | 0.0002356 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.32 |
| NZDCHF | 5 | toto | 50 | 0.004227 | 0.0002902 | 0.0005416 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -8.284 |
| NZDCHF | 20 | hmm | 50 | 0.008371 | 0.0007415 | 0.0004493 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.008 |
| NZDCHF | 20 | garch | 50 | 0.008126 | 0.0005727 | 0.0004743 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.006 |
| NZDCHF | 20 | chronos2 | 50 | 0.007472 | 0.000677 | 0.0005537 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.996 |
| NZDCHF | 20 | toto | 50 | 0.008697 | 0.0008544 | 0.00273 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.91 |
| NZDJPY | 1 | hmm | 50 | 0.002995 | 0.0001931 | 0.0001496 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.298 |
| NZDJPY | 1 | garch | 50 | 0.002993 | 0.0001693 | 0.0001484 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.408 |
| NZDJPY | 1 | chronos2 | 50 | 0.003108 | 0.0001973 | 0.0001671 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.391 |
| NZDJPY | 1 | toto | 50 | 0.003299 | 0.0002058 | 0.0003083 | 0.06 | 0.04 | 50 | 3 | 0.015 | 0.531 | 2 | 0.107 | 0.772 | -7.781 |
| NZDJPY | 5 | hmm | 50 | 0.006076 | 0.0003912 | 0.00031 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.866 |
| NZDJPY | 5 | garch | 50 | 0.006126 | 0.0004763 | 0.0003218 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -7.895 |
| NZDJPY | 5 | chronos2 | 50 | 0.006207 | 0.0003351 | 0.0002966 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -7.793 |
| NZDJPY | 5 | toto | 50 | 0.006129 | 0.0005409 | 0.0003505 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 1.000 | -7.566 |
| NZDJPY | 20 | hmm | 50 | 0.01217 | 0.0008101 | 0.0006416 | 0.04 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.495 |
| NZDJPY | 20 | garch | 50 | 0.01228 | 0.0007887 | 0.0006625 | 0.04 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.501 |
| NZDJPY | 20 | chronos2 | 50 | 0.01146 | 0.0006504 | 0.0006112 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.345 |
| NZDJPY | 20 | toto | 50 | 0.0144 | 0.002775 | 0.003801 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.278 |
| NZDUSD | 1 | hmm | 50 | 0.003229 | 0.0001334 | 0.0002052 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -9.238 |
| NZDUSD | 1 | garch | 50 | 0.003228 | 0.0001328 | 0.0002279 | 0 | 0.04 | 50 | 0 | 0.316 | — | 2 | 0.107 | 0.680 | -9.125 |
| NZDUSD | 1 | chronos2 | 50 | 0.003228 | 0.0001762 | 0.0001686 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.065 |
| NZDUSD | 1 | toto | 50 | 0.003422 | 0.0001715 | 0.0003037 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -8.639 |
| NZDUSD | 5 | hmm | 50 | 0.006743 | 0.0002952 | 0.0006506 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.838 |
| NZDUSD | 5 | garch | 50 | 0.00646 | 0.0002967 | 0.0005556 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.814 |
| NZDUSD | 5 | chronos2 | 50 | 0.006596 | 0.0003599 | 0.0004775 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.843 |
| NZDUSD | 5 | toto | 50 | 0.006649 | 0.0003548 | 0.0006967 | 0 | 0.02 | 50 | 0 | 0.316 | — | 1 | 0.532 | 0.838 | -7.789 |
| NZDUSD | 20 | hmm | 50 | 0.01615 | 0.0006076 | 0.0009423 | 0 | 0.04 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.423 |
| NZDUSD | 20 | garch | 50 | 0.01427 | 0.0006015 | 0.0005923 | 0 | 0.02 | 13 | 0 | 0.609 | — | 1 | 0.121 | 0.670 | -6.412 |
| NZDUSD | 20 | chronos2 | 50 | 0.01419 | 0.0007493 | 0.000706 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.423 |
| NZDUSD | 20 | toto | 50 | 0.01413 | 0.0009202 | 0.001944 | 0.02 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.418 |
| USDCAD | 1 | hmm | 50 | 0.001334 | 7.035e-05 | 6.417e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -11.03 |
| USDCAD | 1 | garch | 50 | 0.001343 | 7.649e-05 | 7.495e-05 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -11.03 |
| USDCAD | 1 | chronos2 | 50 | 0.001414 | 8.676e-05 | 9.314e-05 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -10.92 |
| USDCAD | 1 | toto | 50 | 0.001353 | 0.0001192 | 7.533e-05 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -10.89 |
| USDCAD | 5 | hmm | 50 | 0.00381 | 0.0003791 | 0.0001427 | 0.02 | 0.02 | 50 | 1 | 0.532 | 0.838 | 1 | 0.532 | 0.838 | -9.216 |
| USDCAD | 5 | garch | 50 | 0.003679 | 0.0003789 | 0.0001634 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.172 |
| USDCAD | 5 | chronos2 | 50 | 0.003808 | 0.0003669 | 0.0001671 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.156 |
| USDCAD | 5 | toto | 50 | 0.003597 | 0.0004009 | 0.0002984 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.136 |
| USDCAD | 20 | hmm | 50 | 0.009506 | 0.0005803 | 0.0003036 | 0.02 | 0.02 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.768 |
| USDCAD | 20 | garch | 50 | 0.009106 | 0.0003029 | 0.0003277 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.73 |
| USDCAD | 20 | chronos2 | 50 | 0.008869 | 0.0003774 | 0.00042 | 0 | 0.02 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.745 |
| USDCAD | 20 | toto | 50 | 0.008405 | 0.001546 | 0.0009119 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -7.709 |
| USDCHF | 1 | hmm | 50 | 0.002493 | 0.0001273 | 0.0001054 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.753 |
| USDCHF | 1 | garch | 50 | 0.002465 | 0.000141 | 0.0001186 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -9.788 |
| USDCHF | 1 | chronos2 | 50 | 0.002427 | 0.0001611 | 0.0001633 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.758 |
| USDCHF | 1 | toto | 50 | 0.002484 | 0.0001214 | 0.0001414 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -9.802 |
| USDCHF | 5 | hmm | 50 | 0.005688 | 0.0003088 | 0.0002179 | 0 | 0 | 50 | 0 | 0.316 | — | 0 | 0.316 | — | -8.221 |
| USDCHF | 5 | garch | 50 | 0.005345 | 0.0003233 | 0.0002548 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.239 |
| USDCHF | 5 | chronos2 | 50 | 0.005314 | 0.0004668 | 0.0002701 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.171 |
| USDCHF | 5 | toto | 50 | 0.005342 | 0.0006946 | 0.0004352 | 0.02 | 0 | 50 | 1 | 0.532 | 0.838 | 0 | 0.316 | — | -8.026 |
| USDCHF | 20 | hmm | 50 | 0.01026 | 0.0008422 | 0.0004067 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.791 |
| USDCHF | 20 | garch | 50 | 0.009305 | 0.0005512 | 0.0004992 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.827 |
| USDCHF | 20 | chronos2 | 50 | 0.00953 | 0.0006693 | 0.0006244 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.779 |
| USDCHF | 20 | toto | 50 | 0.01004 | 0.001008 | 0.0009842 | 0.04 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.428 |
| USDJPY | 1 | hmm | 50 | 0.002893 | 0.0003268 | 0.0001187 | 0.06 | 0.02 | 50 | 3 | 0.015 | 0.531 | 1 | 0.532 | 0.838 | -8.081 |
| USDJPY | 1 | garch | 50 | 0.002968 | 0.0007883 | 0.000137 | 0.1 | 0 | 50 | 5 | 0.000 | 0.286 | 0 | 0.316 | — | -7.438 |
| USDJPY | 1 | chronos2 | 50 | 0.002933 | 0.0002086 | 0.0001436 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -7.482 |
| USDJPY | 1 | toto | 50 | 0.002985 | 0.0006126 | 0.0001061 | 0.06 | 0.02 | 50 | 3 | 0.015 | 0.531 | 1 | 0.532 | 0.838 | -4.911 |
| USDJPY | 5 | hmm | 50 | 0.006141 | 0.0005352 | 0.0002451 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -8.006 |
| USDJPY | 5 | garch | 50 | 0.006111 | 0.001089 | 0.0002948 | 0.08 | 0 | 50 | 4 | 0.002 | 0.399 | 0 | 0.316 | — | -7.734 |
| USDJPY | 5 | chronos2 | 50 | 0.006018 | 0.0007426 | 0.0002508 | 0.06 | 0 | 50 | 3 | 0.015 | 0.531 | 0 | 0.316 | — | -7.437 |
| USDJPY | 5 | toto | 50 | 0.006026 | 0.00107 | 0.0002832 | 0.04 | 0 | 50 | 2 | 0.107 | 0.680 | 0 | 0.316 | — | -6.198 |
| USDJPY | 20 | hmm | 50 | 0.01091 | 0.0006666 | 0.0005351 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.629 |
| USDJPY | 20 | garch | 50 | 0.01086 | 0.0009394 | 0.0006465 | 0.06 | 0 | 13 | 1 | 0.121 | 0.670 | 0 | 0.609 | — | -6.379 |
| USDJPY | 20 | chronos2 | 50 | 0.00999 | 0.000625 | 0.0005508 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -6.156 |
| USDJPY | 20 | toto | 50 | 0.0112 | 0.006734 | 0.0024 | 0 | 0 | 13 | 0 | 0.609 | — | 0 | 0.609 | — | -5.705 |

### binance_c20261101: 4 modelos sobre la submuestra de Toto (uno de cada 10 origenes)

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | n_test | x 1 % | Kupiec 1 % p | Chr. 1 % p | x 99 % | Kupiec 99 % p | Chr. 99 % p | QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | 1 | hmm | 36 | 0.02006 | 0.001114 | 0.001184 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -5.588 |
| ADAUSDT | 1 | garch | 36 | 0.02014 | 0.001022 | 0.001132 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -5.532 |
| ADAUSDT | 1 | chronos2 | 36 | 0.02068 | 0.001216 | 0.00141 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.587 |
| ADAUSDT | 1 | toto | 36 | 0.02124 | 0.002184 | 0.001124 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -5.478 |
| ADAUSDT | 5 | hmm | 36 | 0.05273 | 0.002452 | 0.00279 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -4.028 |
| ADAUSDT | 5 | garch | 36 | 0.05277 | 0.002404 | 0.005193 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -4.002 |
| ADAUSDT | 5 | chronos2 | 36 | 0.05293 | 0.002187 | 0.004339 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -3.988 |
| ADAUSDT | 5 | toto | 36 | 0.05182 | 0.002516 | 0.002625 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -4.002 |
| ADAUSDT | 20 | hmm | 36 | 0.1223 | 0.006055 | 0.01012 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -1.905 |
| ADAUSDT | 20 | garch | 36 | 0.1234 | 0.005319 | 0.0108 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -1.738 |
| ADAUSDT | 20 | chronos2 | 36 | 0.1371 | 0.01226 | 0.01227 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -1.727 |
| ADAUSDT | 20 | toto | 36 | 0.129 | 0.01142 | 0.01428 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -1.759 |
| BNBUSDT | 1 | hmm | 36 | 0.01217 | 0.0006659 | 0.0007697 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -6.686 |
| BNBUSDT | 1 | garch | 36 | 0.01227 | 0.0006728 | 0.0008107 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -6.637 |
| BNBUSDT | 1 | chronos2 | 36 | 0.01245 | 0.0008001 | 0.0008818 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -6.356 |
| BNBUSDT | 1 | toto | 36 | 0.01287 | 0.000803 | 0.0007157 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -6.599 |
| BNBUSDT | 5 | hmm | 36 | 0.02596 | 0.001651 | 0.001637 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -4.974 |
| BNBUSDT | 5 | garch | 36 | 0.02627 | 0.001629 | 0.002065 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.952 |
| BNBUSDT | 5 | chronos2 | 36 | 0.02564 | 0.001524 | 0.00224 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.904 |
| BNBUSDT | 5 | toto | 36 | 0.02521 | 0.001896 | 0.003304 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.983 |
| BNBUSDT | 20 | hmm | 36 | 0.05576 | 0.00562 | 0.0033 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -3.095 |
| BNBUSDT | 20 | garch | 36 | 0.0557 | 0.006128 | 0.003706 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -2.994 |
| BNBUSDT | 20 | chronos2 | 36 | 0.058 | 0.007672 | 0.003481 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -2.999 |
| BNBUSDT | 20 | toto | 36 | 0.05637 | 0.00448 | 0.004596 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -2.703 |
| BTCUSDT | 1 | hmm | 36 | 0.01228 | 0.0006825 | 0.0007187 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -6.456 |
| BTCUSDT | 1 | garch | 36 | 0.01224 | 0.0006794 | 0.0007307 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -6.5 |
| BTCUSDT | 1 | chronos2 | 36 | 0.01271 | 0.0007191 | 0.0006898 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -6.236 |
| BTCUSDT | 1 | toto | 36 | 0.01299 | 0.0006627 | 0.000694 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -6.263 |
| BTCUSDT | 5 | hmm | 36 | 0.03159 | 0.001461 | 0.0043 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -4.833 |
| BTCUSDT | 5 | garch | 36 | 0.03181 | 0.001917 | 0.005267 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -4.714 |
| BTCUSDT | 5 | chronos2 | 36 | 0.03197 | 0.001547 | 0.007318 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -4.462 |
| BTCUSDT | 5 | toto | 36 | 0.02997 | 0.001555 | 0.005864 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.717 |
| BTCUSDT | 20 | hmm | 36 | 0.06017 | 0.005287 | 0.00295 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -3.302 |
| BTCUSDT | 20 | garch | 36 | 0.06053 | 0.005892 | 0.003106 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -3.163 |
| BTCUSDT | 20 | chronos2 | 36 | 0.06298 | 0.005418 | 0.004608 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -2.985 |
| BTCUSDT | 20 | toto | 36 | 0.06427 | 0.004184 | 0.007025 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -3.257 |
| DOGEUSDT | 1 | hmm | 36 | 0.02268 | 0.00118 | 0.001467 | 0.0556 | 0.0278 | 36 | 2 | 0.056 | 0.622 | 1 | 0.379 | 0.808 | -5.248 |
| DOGEUSDT | 1 | garch | 36 | 0.02231 | 0.001179 | 0.001298 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.164 |
| DOGEUSDT | 1 | chronos2 | 36 | 0.0235 | 0.001619 | 0.001627 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.385 |
| DOGEUSDT | 1 | toto | 36 | 0.02403 | 0.001129 | 0.002137 | 0 | 0.0833 | 36 | 0 | 0.395 | — | 3 | 0.006 | 0.453 | -4.628 |
| DOGEUSDT | 5 | hmm | 36 | 0.05832 | 0.002453 | 0.003591 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.622 |
| DOGEUSDT | 5 | garch | 36 | 0.05838 | 0.002867 | 0.006851 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.514 |
| DOGEUSDT | 5 | chronos2 | 36 | 0.05888 | 0.002811 | 0.008862 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -2.373 |
| DOGEUSDT | 5 | toto | 36 | 0.06085 | 0.002617 | 0.008366 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -0.1275 |
| DOGEUSDT | 20 | hmm | 36 | 0.1271 | 0.004733 | 0.01938 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -2.028 |
| DOGEUSDT | 20 | garch | 36 | 0.1255 | 0.006114 | 0.01223 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -2.025 |
| DOGEUSDT | 20 | chronos2 | 36 | 0.1242 | 0.005555 | 0.02151 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -1.658 |
| DOGEUSDT | 20 | toto | 36 | 0.1351 | 0.00531 | 0.013 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -1.268 |
| ETHUSDT | 1 | hmm | 36 | 0.01715 | 0.0008476 | 0.00202 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.65 |
| ETHUSDT | 1 | garch | 36 | 0.01694 | 0.0009383 | 0.001613 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.672 |
| ETHUSDT | 1 | chronos2 | 36 | 0.01756 | 0.001339 | 0.002199 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -5.644 |
| ETHUSDT | 1 | toto | 36 | 0.01799 | 0.001198 | 0.002882 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -5.685 |
| ETHUSDT | 5 | hmm | 36 | 0.04316 | 0.001954 | 0.005084 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.186 |
| ETHUSDT | 5 | garch | 36 | 0.04303 | 0.002416 | 0.005664 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -4.199 |
| ETHUSDT | 5 | chronos2 | 36 | 0.04363 | 0.002934 | 0.007742 | 0.0278 | 0.0556 | 36 | 1 | 0.379 | 0.808 | 2 | 0.056 | 0.622 | -3.446 |
| ETHUSDT | 5 | toto | 36 | 0.04401 | 0.001949 | 0.008481 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -1.675 |
| ETHUSDT | 20 | hmm | 36 | 0.09861 | 0.008482 | 0.004465 | 0.0556 | 0.0278 | 36 | 2 | 0.056 | 0.622 | 1 | 0.379 | 0.808 | -2.535 |
| ETHUSDT | 20 | garch | 36 | 0.09637 | 0.004319 | 0.00444 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -2.533 |
| ETHUSDT | 20 | chronos2 | 36 | 0.101 | 0.007572 | 0.004928 | 0.0556 | 0.0556 | 36 | 2 | 0.056 | 0.622 | 2 | 0.056 | 0.622 | -2.219 |
| ETHUSDT | 20 | toto | 36 | 0.1051 | 0.007254 | 0.005946 | 0.0556 | 0.0278 | 36 | 2 | 0.056 | 0.622 | 1 | 0.379 | 0.808 | -2.319 |
| LINKUSDT | 1 | hmm | 36 | 0.0187 | 0.001016 | 0.001158 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.719 |
| LINKUSDT | 1 | garch | 36 | 0.01859 | 0.001064 | 0.001103 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.71 |
| LINKUSDT | 1 | chronos2 | 36 | 0.01955 | 0.001194 | 0.001218 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.585 |
| LINKUSDT | 1 | toto | 36 | 0.01958 | 0.001241 | 0.001157 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.815 |
| LINKUSDT | 5 | hmm | 36 | 0.04909 | 0.002353 | 0.005625 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.895 |
| LINKUSDT | 5 | garch | 36 | 0.04836 | 0.002377 | 0.004129 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.927 |
| LINKUSDT | 5 | chronos2 | 36 | 0.04858 | 0.002269 | 0.00514 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.914 |
| LINKUSDT | 5 | toto | 36 | 0.04809 | 0.00256 | 0.004747 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -3.919 |
| LINKUSDT | 20 | hmm | 36 | 0.1167 | 0.004817 | 0.005296 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.081 |
| LINKUSDT | 20 | garch | 36 | 0.1158 | 0.004668 | 0.005231 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.083 |
| LINKUSDT | 20 | chronos2 | 36 | 0.1158 | 0.004758 | 0.005301 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.12 |
| LINKUSDT | 20 | toto | 36 | 0.1153 | 0.006253 | 0.006846 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -2.108 |
| LTCUSDT | 1 | hmm | 36 | 0.01664 | 0.0009944 | 0.001168 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.965 |
| LTCUSDT | 1 | garch | 36 | 0.0169 | 0.0009623 | 0.001148 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.898 |
| LTCUSDT | 1 | chronos2 | 36 | 0.0169 | 0.001158 | 0.001503 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.912 |
| LTCUSDT | 1 | toto | 36 | 0.01776 | 0.001013 | 0.001372 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.729 |
| LTCUSDT | 5 | hmm | 36 | 0.0371 | 0.0023 | 0.003753 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -4.18 |
| LTCUSDT | 5 | garch | 36 | 0.03738 | 0.002084 | 0.003603 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.114 |
| LTCUSDT | 5 | chronos2 | 36 | 0.03697 | 0.001939 | 0.006381 | 0 | 0.0833 | 36 | 0 | 0.395 | — | 3 | 0.006 | 0.106 | -3.903 |
| LTCUSDT | 5 | toto | 36 | 0.03924 | 0.001882 | 0.005495 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.622 | -3.819 |
| LTCUSDT | 20 | hmm | 36 | 0.07768 | 0.004582 | 0.00413 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.493 |
| LTCUSDT | 20 | garch | 36 | 0.07885 | 0.004341 | 0.004841 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.491 |
| LTCUSDT | 20 | chronos2 | 36 | 0.07495 | 0.003517 | 0.003966 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.263 |
| LTCUSDT | 20 | toto | 36 | 0.08114 | 0.005599 | 0.006793 | 0.0556 | 0.0278 | 36 | 2 | 0.056 | 0.622 | 1 | 0.379 | 0.808 | -2 |
| SOLUSDT | 1 | hmm | 36 | 0.02166 | 0.001085 | 0.001167 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.43 |
| SOLUSDT | 1 | garch | 36 | 0.02198 | 0.001128 | 0.001196 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.376 |
| SOLUSDT | 1 | chronos2 | 36 | 0.02519 | 0.001364 | 0.001426 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -5.125 |
| SOLUSDT | 1 | toto | 36 | 0.02284 | 0.001518 | 0.001354 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -5.341 |
| SOLUSDT | 5 | hmm | 36 | 0.04902 | 0.003219 | 0.003495 | 0.0556 | 0.0278 | 36 | 2 | 0.056 | 0.622 | 1 | 0.379 | 0.808 | -3.721 |
| SOLUSDT | 5 | garch | 36 | 0.04835 | 0.00245 | 0.004694 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.809 |
| SOLUSDT | 5 | chronos2 | 36 | 0.05238 | 0.002459 | 0.005332 | 0 | 0.0556 | 36 | 0 | 0.395 | — | 2 | 0.056 | 0.012 | -3.753 |
| SOLUSDT | 5 | toto | 36 | 0.04971 | 0.003047 | 0.006163 | 0.0556 | 0.0278 | 36 | 2 | 0.056 | 0.622 | 1 | 0.379 | 0.808 | -3.686 |
| SOLUSDT | 20 | hmm | 36 | 0.1179 | 0.007195 | 0.005949 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -2.228 |
| SOLUSDT | 20 | garch | 36 | 0.12 | 0.006793 | 0.005434 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -2.233 |
| SOLUSDT | 20 | chronos2 | 36 | 0.1253 | 0.006424 | 0.005895 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -2.197 |
| SOLUSDT | 20 | toto | 36 | 0.1233 | 0.009699 | 0.01017 | 0.0278 | 0.0278 | 36 | 1 | 0.379 | 0.808 | 1 | 0.379 | 0.808 | -2.192 |
| TRXUSDT | 1 | hmm | 36 | 0.009803 | 0.0005448 | 0.0005211 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -7.047 |
| TRXUSDT | 1 | garch | 36 | 0.009872 | 0.0005352 | 0.0005412 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -7.011 |
| TRXUSDT | 1 | chronos2 | 36 | 0.01154 | 0.0008028 | 0.0007503 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -6.984 |
| TRXUSDT | 1 | toto | 36 | 0.01133 | 0.000543 | 0.0005099 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.352 |
| TRXUSDT | 5 | hmm | 36 | 0.01883 | 0.001477 | 0.001484 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.641 |
| TRXUSDT | 5 | garch | 36 | 0.0194 | 0.001196 | 0.001371 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.633 |
| TRXUSDT | 5 | chronos2 | 36 | 0.02006 | 0.001214 | 0.001133 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.673 |
| TRXUSDT | 5 | toto | 36 | 0.02059 | 0.002424 | 0.001315 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -5.221 |
| TRXUSDT | 20 | hmm | 36 | 0.05162 | 0.003667 | 0.004092 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.763 |
| TRXUSDT | 20 | garch | 36 | 0.05257 | 0.002707 | 0.003117 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.381 |
| TRXUSDT | 20 | chronos2 | 36 | 0.05293 | 0.003192 | 0.002544 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -2.004 |
| TRXUSDT | 20 | toto | 36 | 0.05649 | 0.00474 | 0.00404 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -1.334 |
| XRPUSDT | 1 | hmm | 36 | 0.01587 | 0.00155 | 0.001135 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -5.79 |
| XRPUSDT | 1 | garch | 36 | 0.01582 | 0.001423 | 0.001023 | 0.0278 | 0 | 36 | 1 | 0.379 | 0.808 | 0 | 0.395 | — | -5.886 |
| XRPUSDT | 1 | chronos2 | 36 | 0.02063 | 0.001704 | 0.001528 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.983 |
| XRPUSDT | 1 | toto | 36 | 0.01551 | 0.001006 | 0.001144 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -5.726 |
| XRPUSDT | 5 | hmm | 36 | 0.04784 | 0.002275 | 0.007435 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -4.006 |
| XRPUSDT | 5 | garch | 36 | 0.0482 | 0.002568 | 0.00817 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.88 |
| XRPUSDT | 5 | chronos2 | 36 | 0.0455 | 0.002752 | 0.004974 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.211 |
| XRPUSDT | 5 | toto | 36 | 0.04556 | 0.002795 | 0.009928 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -3.759 |
| XRPUSDT | 20 | hmm | 36 | 0.09909 | 0.004409 | 0.00614 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.295 |
| XRPUSDT | 20 | garch | 36 | 0.09729 | 0.005408 | 0.005077 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.301 |
| XRPUSDT | 20 | chronos2 | 36 | 0.093 | 0.006275 | 0.006735 | 0 | 0.0278 | 36 | 0 | 0.395 | — | 1 | 0.379 | 0.808 | -2.238 |
| XRPUSDT | 20 | toto | 36 | 0.08999 | 0.00584 | 0.007973 | 0 | 0 | 36 | 0 | 0.395 | — | 0 | 0.395 | — | -2.175 |

## Ventana limpia: segundo calculo de los mismos criterios

Origen estrictamente posterior a **2025-08-27T00:00:00Z**; el contexto puede ser anterior. Todos los modelos de cada tabla usan los mismos origenes validos comunes. La tabla principal conserva los origenes de sus modelos sin recortar por FinCast.

`crps_deciles` = 2 × media de los pinball en 0.1, 0.2, …, 0.9, para todos los modelos. No es el CRPS continuo ni el de 21 niveles. FinCast solo aporta `crps_deciles` y QLIKE (varianza = ((q90-q10)/(2 Phi^-1(0.9)))²). CRPS de 21 niveles, pinball 1 %/99 %, excedencias, Kupiec y Christoffersen de FinCast: **no aplicables**, quedan vacios en CSV y — en la tabla.

Para los demas modelos, un p-valor de Christoffersen vacio significa que el test no esta definido: menos de dos observaciones, ninguna excedencia o una fila de transiciones vacia. No equivale a aceptar independencia. Una celda sin origenes comunes validos no se puntua. Los tests de colas con pocas observaciones tienen poca potencia; las cifras siguen siendo descriptivas.

Cuantiles de FinCast: lineal en z=Phi^-1(p) entre deciles adyacentes; extrapolacion con pendiente de 0.1-0.2 para p<0.1 y de 0.8-0.9 para p>0.9; deciles nativos intactos. Nativos: 0.1..0.9; extrapolados: 0.01/0.05/0.95/0.99; interpolados: 0.15/0.25/0.35/0.45/0.55/0.65/0.75/0.85. Ninguno de los niveles no nativos entra en sus criterios.

FinCast v1: decoder oficial sin modificar, 50 capas, dimension 1280, 16 cabezas, 4 expertos/top-2, patch 32, horizonte de salida 128, frecuencia diaria 0. Contexto log-precio completo, padding frontal al siguiente multiplo de 32, lote 1, CPU float32. Se importa directamente el decoder para evitar la API de covariables JAX; `torch.load(weights_only=True)`, `load_state_dict(strict=True)`, `eval()` y `torch.use_deterministic_algorithms(True)`. Semilla reiniciada por origen, tambien para el sorteo del gate MoE.

Timeout FinCast por peticion: 600 s por defecto (`--fincast-timeout`); arranque 300 s. Un timeout mata el trabajador y marca el origen fallido; el siguiente origen arranca otro. CPU de peticiones fallidas sin respuesta no recuperable; el tiempo de espera si esta en la pared. Las respuestas JSON completas de error conservan el trabajador sincronizado y su CPU externa con el driver v2. Toto conserva su comportamiento previo.

Licencias verificadas el 2026-11-11: [codigo Apache-2.0](https://github.com/vincent05r/FinCast-fts/blob/488b19d1d85fa2b3d4b93469530cefdcf1cc97a4/LICENSE), SHA-256 de LICENSE `1eb85fc97224598dad1852b5d6483bbcf0aa8608790dcc657a5a2a761ae9c8c6`; [tarjeta de pesos Apache-2.0](https://huggingface.co/Vincent05R/FinCast/blob/2d7d90b159db8961d27c2cf165d51195902ef92b/README.md), SHA-256 `cbc5c2eb63cd9cc2ff8baa1ed888cd062e81ec170413ffe9827b920bc726794d`. v1.pth SHA-256 `d5ca999b02c944effa60d2b94174dc4d5a0cd2c0543ae289b2e36f37431492a8`. La tarjeta no fija fecha de corte del preentrenamiento: la ventana posterior a publicacion es el control disponible, no una prueba de ausencia de contaminacion de los pesos.

### lago_cierre_c20261101 (proxy): ventana limpia

Dataset SHA-256: `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356`. Estado: **calculada**. Orígenes comunes por activo y horizonte: columna n.

**Predicciones archivadas invalidas:** 187 pares origen-modelo ({'chronos2': 187}) con cuantiles no finitos/no monotonos, excluidos de TODOS los horizontes de la comparacion limpia. No se reparan cuantiles ni se reescriben predicciones o criterios de las tablas principales historicas. La validacion cuenta todos los origenes limpios suministrados antes de tomar la interseccion; n es el numero comun realmente puntuado por celda. La validacion del archivo solo puede comprobar los horizontes almacenados (1/5/20); una corrida nueva comprueba los 20 horizontes. Ejemplos: [{'instrument': 'AUDCHF', 'origen_ms': 1789603200000, 'modelo': 'chronos2'}, {'instrument': 'AUDCHF', 'origen_ms': 1789689600000, 'modelo': 'chronos2'}, {'instrument': 'AUDCHF', 'origen_ms': 1789776000000, 'modelo': 'chronos2'}, {'instrument': 'AUDCHF', 'origen_ms': 1790035200000, 'modelo': 'chronos2'}, {'instrument': 'AUDCHF', 'origen_ms': 1790121600000, 'modelo': 'chronos2'}, {'instrument': 'AUDCHF', 'origen_ms': 1790208000000, 'modelo': 'chronos2'}, {'instrument': 'AUDJPY', 'origen_ms': 1772150400000, 'modelo': 'chronos2'}, {'instrument': 'AUDJPY', 'origen_ms': 1772668800000, 'modelo': 'chronos2'}, {'instrument': 'AUDJPY', 'origen_ms': 1772755200000, 'modelo': 'chronos2'}, {'instrument': 'AUDJPY', 'origen_ms': 1772841600000, 'modelo': 'chronos2'}].

| instrument | h | modelo | n | crps | pinball_01 | pinball_99 | exc_01 | exc_99 | n_test | x_01 | x_99 | kupiec_01_p | kupiec_99_p | christ_01_p | christ_99_p | qlike | crps_deciles |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | 1 | chronos2 | 50 | 0.0022466479 | 0.00020280046 | 0.00014885285 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.082613 | 0.0025518569 |
| AUDCAD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -10.214364 | 0.0023092562 |
| AUDCAD | 1 | garch | 50 | 0.0021543818 | 9.7923056e-05 | 0.0001177679 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -10.032277 | 0.0024599954 |
| AUDCAD | 1 | hmm | 50 | 0.0021274825 | 0.00011697558 | 0.00013196636 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -10.128365 | 0.0024265566 |
| AUDCAD | 1 | toto | 50 | 0.0022007634 | 0.00010755928 | 0.0001074703 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.268504 | 0.0025206966 |
| AUDCAD | 5 | chronos2 | 50 | 0.004226696 | 0.00030649711 | 0.00023217097 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.339035 | 0.0048033867 |
| AUDCAD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.4082048 | 0.0046958707 |
| AUDCAD | 5 | garch | 50 | 0.0042017014 | 0.0002275569 | 0.00022615347 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.3624553 | 0.0047860516 |
| AUDCAD | 5 | hmm | 50 | 0.0043609792 | 0.00026956483 | 0.00028334002 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.3845832 | 0.0049605094 |
| AUDCAD | 5 | toto | 50 | 0.0044904668 | 0.00045163179 | 0.00027682552 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -7.7996236 | 0.0050785839 |
| AUDCAD | 20 | chronos2 | 50 | 0.0075832293 | 0.00065319471 | 0.00058915159 | 0 | 0.02 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.9604539 | 0.0085521802 |
| AUDCAD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.0122388 | 0.008247071 |
| AUDCAD | 20 | garch | 50 | 0.0072211112 | 0.00043753045 | 0.00051174157 | 0 | 0.04 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.9553202 | 0.0081942462 |
| AUDCAD | 20 | hmm | 50 | 0.0078201947 | 0.0005751404 | 0.00047901788 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.9840681 | 0.0088646578 |
| AUDCAD | 20 | toto | 50 | 0.0083742013 | 0.0010466014 | 0.00064201489 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.5176293 | 0.0094377748 |
| AUDCHF | 1 | chronos2 | 49 | 0.0022449376 | 0.00019582764 | 0.00016158969 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -9.980698 | 0.0025451104 |
| AUDCHF | 1 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -10.060919 | 0.0025915913 |
| AUDCHF | 1 | garch | 49 | 0.0021373935 | 0.00011773155 | 0.00012701488 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | — | — | -10.050779 | 0.0024309241 |
| AUDCHF | 1 | hmm | 49 | 0.0021287756 | 0.000116454 | 0.00011319172 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -10.088388 | 0.002429503 |
| AUDCHF | 1 | toto | 49 | 0.0020667234 | 0.0001657032 | 0.00017239925 | 0.06122449 | 0.040816327 | 49 | 3 | 2 | 0.014436675 | 0.10332307 | 0.60747077 | 0.67660924 | -9.7120226 | 0.0023328302 |
| AUDCHF | 5 | chronos2 | 49 | 0.0045705939 | 0.00032107113 | 0.00022994975 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.1629554 | 0.0052225625 |
| AUDCHF | 5 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -8.182056 | 0.005267102 |
| AUDCHF | 5 | garch | 49 | 0.0044404233 | 0.00028794122 | 0.00026136758 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.2502122 | 0.0050578814 |
| AUDCHF | 5 | hmm | 49 | 0.0045257005 | 0.00032195648 | 0.00022658498 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.2576114 | 0.0051528809 |
| AUDCHF | 5 | toto | 49 | 0.0043755218 | 0.00041686904 | 0.00046534029 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -7.8555596 | 0.0049585262 |
| AUDCHF | 20 | chronos2 | 49 | 0.0075346517 | 0.00071678421 | 0.00052032252 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7775076 | 0.0085330713 |
| AUDCHF | 20 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -6.7929927 | 0.0091232483 |
| AUDCHF | 20 | garch | 49 | 0.0072091888 | 0.0005915317 | 0.00052249606 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.8475896 | 0.0081572223 |
| AUDCHF | 20 | hmm | 49 | 0.0077725345 | 0.00087300642 | 0.00045588689 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.8553208 | 0.0087784189 |
| AUDCHF | 20 | toto | 49 | 0.007890813 | 0.0020139446 | 0.0017298834 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7169902 | 0.00863574 |
| AUDJPY | 1 | chronos2 | 42 | 0.0030829711 | 0.00027657852 | 0.00019597267 | 0 | 0 | 42 | 0 | 0 | 0.35819029 | 0.35819029 | — | — | -9.3072458 | 0.0035054009 |
| AUDJPY | 1 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -9.2391374 | 0.0038537946 |
| AUDJPY | 1 | garch | 42 | 0.0029862249 | 0.0002131852 | 0.00014852543 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -9.2992853 | 0.0033881582 |
| AUDJPY | 1 | hmm | 42 | 0.0029527229 | 0.00018866907 | 0.00014303365 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -9.2865197 | 0.0033556793 |
| AUDJPY | 1 | toto | 42 | 0.002992103 | 0.00012658567 | 0.00028370983 | 0.023809524 | 0.047619048 | 42 | 1 | 2 | 0.44508829 | 0.076234514 | 0.82305421 | 0.65054142 | -7.8190603 | 0.0033854606 |
| AUDJPY | 5 | chronos2 | 42 | 0.0060046102 | 0.00042655932 | 0.00029351963 | 0 | 0 | 42 | 0 | 0 | 0.35819029 | 0.35819029 | — | — | -7.7346174 | 0.0068624071 |
| AUDJPY | 5 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -7.7829121 | 0.0071722294 |
| AUDJPY | 5 | garch | 42 | 0.0056798709 | 0.00034893452 | 0.00032889676 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -7.7986023 | 0.0064517354 |
| AUDJPY | 5 | hmm | 42 | 0.0056652084 | 0.00039138629 | 0.00030712785 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -7.7859684 | 0.0064310257 |
| AUDJPY | 5 | toto | 42 | 0.0054383019 | 0.00076229049 | 0.0002680803 | 0 | 0 | 42 | 0 | 0 | 0.35819029 | 0.35819029 | — | — | -7.1216805 | 0.0061779814 |
| AUDJPY | 20 | chronos2 | 42 | 0.011174498 | 0.0010022844 | 0.00068279214 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.4079867 | 0.012689073 |
| AUDJPY | 20 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -6.4002717 | 0.013739408 |
| AUDJPY | 20 | garch | 42 | 0.011853698 | 0.00062555348 | 0.00070258908 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.4647332 | 0.013510597 |
| AUDJPY | 20 | hmm | 42 | 0.011818105 | 0.00078531545 | 0.0006417331 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.4503485 | 0.013457274 |
| AUDJPY | 20 | toto | 42 | 0.011732032 | 0.011412124 | 0.0043500036 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -5.9059382 | 0.011672256 |
| AUDNZD | 1 | chronos2 | 46 | 0.0014372542 | 0.00011517304 | 0.0001005855 | 0 | 0 | 46 | 0 | 0 | 0.33626198 | 0.33626198 | — | — | -10.746547 | 0.0016296502 |
| AUDNZD | 1 | fincast | 46 | — | — | — | — | — | — | — | — | — | — | — | — | -10.745685 | 0.0017733539 |
| AUDNZD | 1 | garch | 46 | 0.0013785071 | 6.8133564e-05 | 7.8811631e-05 | 0 | 0 | 46 | 0 | 0 | 0.33626198 | 0.33626198 | — | — | -10.973664 | 0.0015694152 |
| AUDNZD | 1 | hmm | 46 | 0.0014021371 | 7.2948835e-05 | 6.702517e-05 | 0.02173913 | 0 | 46 | 1 | 0 | 0.48865514 | 0.33626198 | 0.83116325 | — | -10.835767 | 0.0015979991 |
| AUDNZD | 1 | toto | 46 | 0.0016877718 | 8.7714132e-05 | 9.0841003e-05 | 0.02173913 | 0.02173913 | 46 | 1 | 1 | 0.48865514 | 0.48865514 | 0.83116325 | 0.83116325 | -10.834401 | 0.0019262707 |
| AUDNZD | 5 | chronos2 | 46 | 0.0036413245 | 0.00020485535 | 0.00016549786 | 0 | 0 | 46 | 0 | 0 | 0.33626198 | 0.33626198 | — | — | -8.9818415 | 0.0041608484 |
| AUDNZD | 5 | fincast | 46 | — | — | — | — | — | — | — | — | — | — | — | — | -8.9612887 | 0.0043257076 |
| AUDNZD | 5 | garch | 46 | 0.0035193851 | 0.00019174802 | 0.0001599239 | 0.02173913 | 0 | 46 | 1 | 0 | 0.48865514 | 0.33626198 | 0.83116325 | — | -8.9677602 | 0.0040184089 |
| AUDNZD | 5 | hmm | 46 | 0.0036010491 | 0.00018866403 | 0.00014203333 | 0.02173913 | 0 | 46 | 1 | 0 | 0.48865514 | 0.33626198 | 0.83116325 | — | -8.855942 | 0.0041242691 |
| AUDNZD | 5 | toto | 46 | 0.0041267852 | 0.00031420912 | 0.00033641852 | 0.02173913 | 0.02173913 | 46 | 1 | 1 | 0.48865514 | 0.48865514 | 0.83116325 | 0.83116325 | -8.7767766 | 0.0046853866 |
| AUDNZD | 20 | chronos2 | 46 | 0.0073646508 | 0.00049765422 | 0.00038011525 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.60258 | 0.0084076427 |
| AUDNZD | 20 | fincast | 46 | — | — | — | — | — | — | — | — | — | — | — | — | -7.5843882 | 0.0087005455 |
| AUDNZD | 20 | garch | 46 | 0.0069116493 | 0.00029535686 | 0.00030891672 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.5776761 | 0.0079339458 |
| AUDNZD | 20 | hmm | 46 | 0.0072110133 | 0.00031694179 | 0.00028637613 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.5787708 | 0.0082767262 |
| AUDNZD | 20 | toto | 46 | 0.008288513 | 0.0019002277 | 0.0012737529 | 0.02173913 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.4315757 | 0.0091361678 |
| AUDUSD | 1 | chronos2 | 50 | 0.0029564885 | 0.00023378472 | 0.00025107037 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -9.2981704 | 0.0033513407 |
| AUDUSD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.5065125 | 0.0035440371 |
| AUDUSD | 1 | garch | 50 | 0.0028636986 | 0.00012742497 | 0.00021857579 | 0.02 | 0.04 | 50 | 1 | 2 | 0.53158437 | 0.1074658 | 0.83825072 | 0.67987714 | -9.3165615 | 0.0032615182 |
| AUDUSD | 1 | hmm | 50 | 0.0028156466 | 0.00013542544 | 0.00019924468 | 0.02 | 0.04 | 50 | 1 | 2 | 0.53158437 | 0.1074658 | 0.83825072 | 0.67987714 | -9.4729807 | 0.0032069531 |
| AUDUSD | 1 | toto | 50 | 0.0029941679 | 0.00029856812 | 0.00035539522 | 0.06 | 0.04 | 50 | 3 | 2 | 0.015322518 | 0.1074658 | 0.5314689 | 0.67987714 | -7.8706058 | 0.0033697577 |
| AUDUSD | 5 | chronos2 | 50 | 0.0062565275 | 0.00036744483 | 0.0008013403 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -7.8065736 | 0.007059059 |
| AUDUSD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.9339944 | 0.0070348654 |
| AUDUSD | 5 | garch | 50 | 0.005992217 | 0.00030164722 | 0.00069721312 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -7.8958164 | 0.0067774597 |
| AUDUSD | 5 | hmm | 50 | 0.0061999238 | 0.00032053199 | 0.00071649551 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -7.955568 | 0.0070102814 |
| AUDUSD | 5 | toto | 50 | 0.0065956604 | 0.00056437196 | 0.00050920608 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -7.8059353 | 0.0074865076 |
| AUDUSD | 20 | chronos2 | 50 | 0.013782113 | 0.00077221781 | 0.0013810084 | 0 | 0.04 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.2984303 | 0.015592715 |
| AUDUSD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -6.5325895 | 0.015093769 |
| AUDUSD | 20 | garch | 50 | 0.012987947 | 0.00059029037 | 0.00098916384 | 0.02 | 0.02 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.4077789 | 0.014786689 |
| AUDUSD | 20 | hmm | 50 | 0.014762841 | 0.0007646816 | 0.0011525831 | 0.02 | 0.04 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.5348364 | 0.016767908 |
| AUDUSD | 20 | toto | 50 | 0.014413613 | 0.0024833385 | 0.0025258614 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.3956042 | 0.015984772 |
| CADCHF | 1 | chronos2 | 49 | 0.0019605607 | 0.00012447151 | 0.00010851953 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -10.102678 | 0.0022332415 |
| CADCHF | 1 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -9.8902309 | 0.0025502205 |
| CADCHF | 1 | garch | 49 | 0.0020193834 | 0.00011583961 | 9.2150812e-05 | 0.040816327 | 0 | 49 | 2 | 0 | 0.10332307 | 0.32098398 | 0.67660924 | — | -10.091099 | 0.0023013434 |
| CADCHF | 1 | hmm | 49 | 0.0020329396 | 9.9940977e-05 | 0.00010419251 | 0 | 0.020408163 | 49 | 0 | 1 | 0.32098398 | 0.52091544 | — | 0.8365628 | -10.124194 | 0.0023210561 |
| CADCHF | 1 | toto | 49 | 0.0019798878 | 0.00012201514 | 0.00017180345 | 0.040816327 | 0.020408163 | 49 | 2 | 1 | 0.10332307 | 0.52091544 | 0.76927566 | 0.8365628 | -9.9298859 | 0.0022415765 |
| CADCHF | 5 | chronos2 | 49 | 0.0041870522 | 0.00022399612 | 0.00018411773 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.7313406 | 0.0047990545 |
| CADCHF | 5 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -8.6366356 | 0.00496586 |
| CADCHF | 5 | garch | 49 | 0.004219544 | 0.00023272428 | 0.00021254996 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.7660052 | 0.0048227457 |
| CADCHF | 5 | hmm | 49 | 0.0042475966 | 0.00025028157 | 0.0001976381 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.7589116 | 0.0048550749 |
| CADCHF | 5 | toto | 49 | 0.0041639336 | 0.00023598804 | 0.00051506608 | 0 | 0.040816327 | 49 | 0 | 2 | 0.32098398 | 0.10332307 | — | 0.67660924 | -8.7047383 | 0.0047106209 |
| CADCHF | 20 | chronos2 | 49 | 0.0064122089 | 0.00051388038 | 0.00040061371 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.3534235 | 0.0072821548 |
| CADCHF | 20 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -7.3362366 | 0.0070923442 |
| CADCHF | 20 | garch | 49 | 0.0067149351 | 0.00048467086 | 0.00039398999 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.3518632 | 0.0076256493 |
| CADCHF | 20 | hmm | 49 | 0.0070535054 | 0.00053550775 | 0.00036844387 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.3587087 | 0.0080280764 |
| CADCHF | 20 | toto | 49 | 0.0070537647 | 0.00070675426 | 0.0020729718 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.1975233 | 0.0077998567 |
| CADJPY | 1 | chronos2 | 50 | 0.0029020352 | 0.00028039698 | 0.00013460524 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.7982762 | 0.0032895322 |
| CADJPY | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.8803253 | 0.0035095535 |
| CADJPY | 1 | garch | 50 | 0.00282664 | 0.00058085101 | 0.00012221866 | 0.08 | 0 | 50 | 4 | 0 | 0.0016626471 | 0.31609559 | 0.39876393 | — | -8.6911506 | 0.00315338 |
| CADJPY | 1 | hmm | 50 | 0.0028151382 | 0.00042591636 | 0.00010936572 | 0.08 | 0 | 50 | 4 | 0 | 0.0016626471 | 0.31609559 | 0.39876393 | — | -8.2074511 | 0.003161376 |
| CADJPY | 1 | toto | 50 | 0.0030281768 | 0.00076257914 | 0.00021740141 | 0.12 | 0.1 | 50 | 6 | 5 | 1.0305327e-05 | 0.00014408777 | 0.19493842 | 0.34266545 | -4.1428057 | 0.003333354 |
| CADJPY | 5 | chronos2 | 50 | 0.0055812163 | 0.00057008499 | 0.00023179789 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -7.973452 | 0.0063329311 |
| CADJPY | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.0477242 | 0.0065444574 |
| CADJPY | 5 | garch | 50 | 0.005586842 | 0.00072562001 | 0.00028140352 | 0.04 | 0 | 50 | 2 | 0 | 0.1074658 | 0.31609559 | 0.67987714 | — | -8.04618 | 0.0063019771 |
| CADJPY | 5 | hmm | 50 | 0.0055863144 | 0.00074367233 | 0.00026717267 | 0.06 | 0.02 | 50 | 3 | 1 | 0.015322518 | 0.53158437 | 0.5314689 | 0.83825072 | -7.9817116 | 0.0062944656 |
| CADJPY | 5 | toto | 50 | 0.005674622 | 0.00098939568 | 0.00027342716 | 0.06 | 0 | 50 | 3 | 0 | 0.015322518 | 0.31609559 | 0.5314689 | — | -7.4688934 | 0.0063515648 |
| CADJPY | 20 | chronos2 | 50 | 0.0094364589 | 0.00058925908 | 0.00050346581 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.6632478 | 0.010778064 |
| CADJPY | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -6.7932434 | 0.011054661 |
| CADJPY | 20 | garch | 50 | 0.010735854 | 0.000514288 | 0.00059321468 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7564972 | 0.012269738 |
| CADJPY | 20 | hmm | 50 | 0.010482435 | 0.00051281888 | 0.00054215274 | 0 | 0.02 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7032865 | 0.011984819 |
| CADJPY | 20 | toto | 50 | 0.010984712 | 0.0023409099 | 0.0020719557 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.5040355 | 0.012186868 |
| CHFJPY | 1 | chronos2 | 42 | 0.0025217914 | 0.00018072901 | 0.00014133816 | 0 | 0 | 42 | 0 | 0 | 0.35819029 | 0.35819029 | — | — | -9.7717739 | 0.0028802419 |
| CHFJPY | 1 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -9.6035311 | 0.0028595772 |
| CHFJPY | 1 | garch | 42 | 0.0024308583 | 0.0001450053 | 0.00010812877 | 0.071428571 | 0 | 42 | 3 | 0 | 0.0091148606 | 0.35819029 | 0.49107158 | — | -9.794437 | 0.0027720923 |
| CHFJPY | 1 | hmm | 42 | 0.0024450269 | 0.00014248771 | 0.0001182023 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -9.7668665 | 0.0027885974 |
| CHFJPY | 1 | toto | 42 | 0.0027910714 | 0.0003988753 | 0.00023025345 | 0.14285714 | 0.071428571 | 42 | 6 | 3 | 3.4726728e-06 | 0.0091148606 | 0.72727381 | 0.087770036 | -7.5539893 | 0.0031228136 |
| CHFJPY | 5 | chronos2 | 42 | 0.0052656652 | 0.00032501102 | 0.00025229633 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -8.1489562 | 0.0059947621 |
| CHFJPY | 5 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -8.201781 | 0.0060920321 |
| CHFJPY | 5 | garch | 42 | 0.0054341121 | 0.00043466233 | 0.0002553941 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -8.2500369 | 0.0061722562 |
| CHFJPY | 5 | hmm | 42 | 0.0054723856 | 0.00058367177 | 0.00027161472 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -8.2447829 | 0.0062045335 |
| CHFJPY | 5 | toto | 42 | 0.0051725755 | 0.00053843385 | 0.0010182977 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.75028361 | — | -7.2226397 | 0.005767937 |
| CHFJPY | 20 | chronos2 | 42 | 0.0077936705 | 0.00066058546 | 0.00055494466 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.6107138 | 0.0088450746 |
| CHFJPY | 20 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -6.869376 | 0.010149897 |
| CHFJPY | 20 | garch | 42 | 0.010245694 | 0.00054499416 | 0.0005668699 | 0.023809524 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.9452694 | 0.011695695 |
| CHFJPY | 20 | hmm | 42 | 0.01034899 | 0.00053597827 | 0.00057976675 | 0.023809524 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.9346338 | 0.011793412 |
| CHFJPY | 20 | toto | 42 | 0.0091928576 | 0.0069981728 | 0.0043707525 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.479639 | 0.0092945286 |
| EURAUD | 1 | chronos2 | 48 | 0.0020818798 | 0.0001412139 | 0.00014636404 | 0 | 0 | 48 | 0 | 0 | 0.32597239 | 0.32597239 | — | — | -10.153022 | 0.0023702838 |
| EURAUD | 1 | fincast | 48 | — | — | — | — | — | — | — | — | — | — | — | — | -10.261981 | 0.0023572374 |
| EURAUD | 1 | garch | 48 | 0.001978028 | 0.00010290129 | 9.8241457e-05 | 0 | 0 | 48 | 0 | 0 | 0.32597239 | 0.32597239 | — | — | -10.275533 | 0.0022586084 |
| EURAUD | 1 | hmm | 48 | 0.0020303221 | 9.67046e-05 | 9.7737496e-05 | 0 | 0 | 48 | 0 | 0 | 0.32597239 | 0.32597239 | — | — | -10.241863 | 0.0023191126 |
| EURAUD | 1 | toto | 48 | 0.0023026694 | 0.0001159141 | 0.00014023205 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -10.154323 | 0.0026236191 |
| EURAUD | 5 | chronos2 | 48 | 0.0045765552 | 0.00021931534 | 0.00030465332 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -8.5998056 | 0.0052196849 |
| EURAUD | 5 | fincast | 48 | — | — | — | — | — | — | — | — | — | — | — | — | -8.5680063 | 0.0051305084 |
| EURAUD | 5 | garch | 48 | 0.0043653641 | 0.0002068573 | 0.00025589649 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -8.6213401 | 0.0049835754 |
| EURAUD | 5 | hmm | 48 | 0.0045551955 | 0.00020130206 | 0.00028459908 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -8.6058782 | 0.0051973308 |
| EURAUD | 5 | toto | 48 | 0.0049838198 | 0.00070271782 | 0.00058091696 | 0.020833333 | 0.020833333 | 48 | 1 | 1 | 0.51020363 | 0.51020363 | 0.83482092 | 0.83482092 | -8.5607932 | 0.0055709556 |
| EURAUD | 20 | chronos2 | 48 | 0.0094916664 | 0.00057699554 | 0.00063067607 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.2266639 | 0.01081527 |
| EURAUD | 20 | fincast | 48 | — | — | — | — | — | — | — | — | — | — | — | — | -7.2389479 | 0.010874969 |
| EURAUD | 20 | garch | 48 | 0.0089328135 | 0.00040710747 | 0.00049502214 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.2308344 | 0.010200271 |
| EURAUD | 20 | hmm | 48 | 0.0096777331 | 0.00041737531 | 0.00068499753 | 0.020833333 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.1831444 | 0.011048111 |
| EURAUD | 20 | toto | 48 | 0.011655742 | 0.0027091793 | 0.0014891734 | 0.041666667 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.0288713 | 0.012975163 |
| EURCAD | 1 | chronos2 | 50 | 0.0015145355 | 9.8744245e-05 | 9.1941176e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.5561 | 0.0017215761 |
| EURCAD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -10.176925 | 0.0020533682 |
| EURCAD | 1 | garch | 50 | 0.0015564954 | 0.00013136397 | 0.00010874852 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | — | 0.83825072 | -10.597731 | 0.0017637824 |
| EURCAD | 1 | hmm | 50 | 0.001572438 | 0.0001513134 | 0.00011894736 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | — | 0.83825072 | -10.47545 | 0.0017761926 |
| EURCAD | 1 | toto | 50 | 0.0015362945 | 0.00015833242 | 0.00011532391 | 0.04 | 0.04 | 50 | 2 | 2 | 0.1074658 | 0.1074658 | 0.77165 | 0.67987714 | -10.305753 | 0.0017319356 |
| EURCAD | 5 | chronos2 | 50 | 0.0030622643 | 0.00029704713 | 0.00017494683 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.1484937 | 0.0034724753 |
| EURCAD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.1277506 | 0.0035963669 |
| EURCAD | 5 | garch | 50 | 0.0032043095 | 0.0001889938 | 0.00019869197 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.1746905 | 0.0036470934 |
| EURCAD | 5 | hmm | 50 | 0.003222556 | 0.00020138437 | 0.00019913548 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.1192123 | 0.0036594969 |
| EURCAD | 5 | toto | 50 | 0.0030821313 | 0.00079167445 | 0.00023046186 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -8.9095519 | 0.0034090122 |
| EURCAD | 20 | chronos2 | 50 | 0.0060599808 | 0.00042410363 | 0.0003839759 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.6693192 | 0.0068744782 |
| EURCAD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.7975659 | 0.0070200269 |
| EURCAD | 20 | garch | 50 | 0.0067992954 | 0.00070989601 | 0.00042579674 | 0.04 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.7383003 | 0.0076899435 |
| EURCAD | 20 | hmm | 50 | 0.0066802955 | 0.00043815305 | 0.00041751649 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.7545724 | 0.0075986775 |
| EURCAD | 20 | toto | 50 | 0.0062449636 | 0.0038765542 | 0.00060757552 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.5126593 | 0.0066107465 |
| EURCHF | 1 | chronos2 | 50 | 0.0015481612 | 0.00020075012 | 7.7972468e-05 | 0.04 | 0 | 50 | 2 | 0 | 0.1074658 | 0.31609559 | 0.77165 | — | -10.233428 | 0.0017467282 |
| EURCHF | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.9272171 | 0.0019217532 |
| EURCHF | 1 | garch | 50 | 0.0015674446 | 0.00024861832 | 6.258135e-05 | 0.04 | 0 | 50 | 2 | 0 | 0.1074658 | 0.31609559 | 0.77165 | — | -10.261876 | 0.0017672066 |
| EURCHF | 1 | hmm | 50 | 0.0016007287 | 0.00022927246 | 5.8594354e-05 | 0.04 | 0 | 50 | 2 | 0 | 0.1074658 | 0.31609559 | 0.77165 | — | -10.155048 | 0.0018056323 |
| EURCHF | 1 | toto | 50 | 0.0017530634 | 0.00024513304 | 8.8556978e-05 | 0.04 | 0.04 | 50 | 2 | 2 | 0.1074658 | 0.1074658 | 0.77165 | 0.67987714 | -9.9424945 | 0.0019735403 |
| EURCHF | 5 | chronos2 | 50 | 0.002984712 | 0.00022209814 | 0.00012251898 | 0.04 | 0 | 50 | 2 | 0 | 0.1074658 | 0.31609559 | 0.77165 | — | -8.9355061 | 0.0034026187 |
| EURCHF | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.972003 | 0.0035036441 |
| EURCHF | 5 | garch | 50 | 0.0029699959 | 0.00020853798 | 0.00013047768 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | — | — | -9.2922862 | 0.0033871307 |
| EURCHF | 5 | hmm | 50 | 0.0030187066 | 0.00021608627 | 0.00012454878 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.2437899 | 0.0034450973 |
| EURCHF | 5 | toto | 50 | 0.003191005 | 0.00017357426 | 0.00017576038 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.9478761 | 0.0036402521 |
| EURCHF | 20 | chronos2 | 50 | 0.0060105753 | 0.00027584443 | 0.00026195913 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.6280272 | 0.0068688808 |
| EURCHF | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.61863 | 0.0068260264 |
| EURCHF | 20 | garch | 50 | 0.0060765478 | 0.00035070558 | 0.00026503966 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.8604395 | 0.0069456582 |
| EURCHF | 20 | hmm | 50 | 0.0061498635 | 0.00030057127 | 0.00025554801 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.9085757 | 0.0070350764 |
| EURCHF | 20 | toto | 50 | 0.0063907847 | 0.00058269887 | 0.00049404244 | 0.04 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.8818605 | 0.0072214056 |
| EURGBP | 1 | chronos2 | 50 | 0.0012499012 | 8.3331034e-05 | 7.7797655e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -11.102457 | 0.0014186264 |
| EURGBP | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -10.975056 | 0.0014513322 |
| EURGBP | 1 | garch | 50 | 0.0012164097 | 6.535042e-05 | 7.4596137e-05 | 0 | 0.04 | 50 | 0 | 2 | 0.31609559 | 0.1074658 | — | 0.67987714 | -11.041008 | 0.0013852327 |
| EURGBP | 1 | hmm | 50 | 0.0012135267 | 6.3612473e-05 | 8.7222499e-05 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -11.099573 | 0.0013825913 |
| EURGBP | 1 | toto | 50 | 0.0013680938 | 9.7968451e-05 | 0.00010951154 | 0.04 | 0.1 | 50 | 2 | 5 | 0.1074658 | 0.00014408777 | 0.67987714 | 0.48692165 | -10.99093 | 0.0015493235 |
| EURGBP | 5 | chronos2 | 50 | 0.0024315778 | 0.00020493526 | 0.00014897826 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.6003068 | 0.0027624928 |
| EURGBP | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.6804887 | 0.0027217441 |
| EURGBP | 5 | garch | 50 | 0.0023217559 | 0.0001267678 | 0.00013504743 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.637614 | 0.0026485286 |
| EURGBP | 5 | hmm | 50 | 0.0023825809 | 0.00011912388 | 0.00015305216 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.6573837 | 0.0027143476 |
| EURGBP | 5 | toto | 50 | 0.0024791078 | 0.00022458977 | 0.00019364141 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 1 | -9.3648312 | 0.0028094722 |
| EURGBP | 20 | chronos2 | 50 | 0.0050379281 | 0.00049561365 | 0.00034511678 | 0.06 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | — | — | -8.2245995 | 0.0056890378 |
| EURGBP | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.2909839 | 0.0052595774 |
| EURGBP | 20 | garch | 50 | 0.0049673379 | 0.00034953621 | 0.00029155717 | 0.04 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | — | — | -8.289437 | 0.0056336703 |
| EURGBP | 20 | hmm | 50 | 0.0051038101 | 0.00023773039 | 0.00035171473 | 0.02 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | — | — | -8.2810724 | 0.0058020602 |
| EURGBP | 20 | toto | 50 | 0.0058373951 | 0.001026234 | 0.00074541708 | 0.06 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -8.2095448 | 0.0064685905 |
| EURJPY | 1 | chronos2 | 42 | 0.0020183838 | 0.00016231527 | 0.00012737931 | 0 | 0 | 42 | 0 | 0 | 0.35819029 | 0.35819029 | — | — | -9.9107085 | 0.002281219 |
| EURJPY | 1 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -9.5564207 | 0.0026365862 |
| EURJPY | 1 | garch | 42 | 0.002045882 | 0.00036249803 | 0.0001080475 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -9.7639226 | 0.0022873276 |
| EURJPY | 1 | hmm | 42 | 0.0020558847 | 0.00027053608 | 0.0001069252 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -9.8050122 | 0.0023150297 |
| EURJPY | 1 | toto | 42 | 0.0023187366 | 0.00043486069 | 0.00012141786 | 0.047619048 | 0.023809524 | 42 | 2 | 1 | 0.076234514 | 0.44508829 | 0.65054142 | 0.82305421 | -9.0641581 | 0.0025825977 |
| EURJPY | 5 | chronos2 | 42 | 0.0045766911 | 0.00031232664 | 0.00021761526 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -8.4530697 | 0.0051917265 |
| EURJPY | 5 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -8.4530618 | 0.0055159495 |
| EURJPY | 5 | garch | 42 | 0.0046370991 | 0.0005373259 | 0.00023437146 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -8.5181957 | 0.0052333825 |
| EURJPY | 5 | hmm | 42 | 0.0046291939 | 0.00052025651 | 0.00022671662 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -8.4879133 | 0.0052286744 |
| EURJPY | 5 | toto | 42 | 0.0050722421 | 0.00091030066 | 0.00092884922 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -7.7982874 | 0.0056402683 |
| EURJPY | 20 | chronos2 | 42 | 0.0080666396 | 0.00057758823 | 0.00049730945 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -6.9895123 | 0.0092076217 |
| EURJPY | 20 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -7.0228992 | 0.0092759012 |
| EURJPY | 20 | garch | 42 | 0.0096627796 | 0.0003409326 | 0.00052547707 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -7.0912936 | 0.011043317 |
| EURJPY | 20 | hmm | 42 | 0.0088291774 | 0.00040337265 | 0.00048935685 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -7.080657 | 0.010096796 |
| EURJPY | 20 | toto | 42 | 0.01086431 | 0.0083738654 | 0.0077871103 | 0.047619048 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -6.3886076 | 0.010701034 |
| EURNZD | 1 | chronos2 | 47 | 0.0021350779 | 0.0001152502 | 0.00012435474 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -10.038324 | 0.0024379526 |
| EURNZD | 1 | fincast | 47 | — | — | — | — | — | — | — | — | — | — | — | — | -10.145458 | 0.0025673018 |
| EURNZD | 1 | garch | 47 | 0.0021079455 | 9.444909e-05 | 9.708013e-05 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -10.093144 | 0.002412506 |
| EURNZD | 1 | hmm | 47 | 0.0021154431 | 8.9742816e-05 | 9.5101675e-05 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -10.084186 | 0.0024246564 |
| EURNZD | 1 | toto | 47 | 0.002229807 | 7.6657214e-05 | 0.00015446181 | 0 | 0.063829787 | 47 | 0 | 3 | 0.33106397 | 0.012761054 | — | 0.51746399 | -9.8771036 | 0.0025472631 |
| EURNZD | 5 | chronos2 | 47 | 0.0039632085 | 0.00021944439 | 0.00024213725 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -8.7323721 | 0.004521024 |
| EURNZD | 5 | fincast | 47 | — | — | — | — | — | — | — | — | — | — | — | — | -8.7254477 | 0.0046436519 |
| EURNZD | 5 | garch | 47 | 0.0039394973 | 0.00020000398 | 0.00021514613 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -8.7370986 | 0.0044875345 |
| EURNZD | 5 | hmm | 47 | 0.0041238988 | 0.00019825718 | 0.00022413741 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -8.7334498 | 0.0047081208 |
| EURNZD | 5 | toto | 47 | 0.003820774 | 0.00084321677 | 0.00027646275 | 0 | 0 | 47 | 0 | 0 | 0.33106397 | 0.33106397 | — | — | -8.6961073 | 0.0042771087 |
| EURNZD | 20 | chronos2 | 47 | 0.0080933153 | 0.00047465599 | 0.00053930605 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -7.3158354 | 0.0092334835 |
| EURNZD | 20 | fincast | 47 | — | — | — | — | — | — | — | — | — | — | — | — | -7.2962954 | 0.009105868 |
| EURNZD | 20 | garch | 47 | 0.0085616388 | 0.00037638907 | 0.0004516028 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -7.3091949 | 0.0098072787 |
| EURNZD | 20 | hmm | 47 | 0.0090484501 | 0.00039740983 | 0.00052174301 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -7.2804668 | 0.010354145 |
| EURNZD | 20 | toto | 47 | 0.0081865646 | 0.0045509485 | 0.0010275916 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -6.9795962 | 0.0086875037 |
| EURUSD | 1 | chronos2 | 48 | 0.0017603649 | 0.0001251938 | 0.00012818599 | 0 | 0 | 48 | 0 | 0 | 0.32597239 | 0.32597239 | — | — | -10.47156 | 0.0020013966 |
| EURUSD | 1 | fincast | 48 | — | — | — | — | — | — | — | — | — | — | — | — | -10.396424 | 0.0022082347 |
| EURUSD | 1 | garch | 48 | 0.0017000175 | 9.0104927e-05 | 9.2396947e-05 | 0 | 0 | 48 | 0 | 0 | 0.32597239 | 0.32597239 | — | — | -10.455336 | 0.0019364886 |
| EURUSD | 1 | hmm | 48 | 0.0017272501 | 0.00010055424 | 9.7069225e-05 | 0.020833333 | 0 | 48 | 1 | 0 | 0.51020363 | 0.32597239 | — | — | -10.497726 | 0.0019689087 |
| EURUSD | 1 | toto | 48 | 0.0017122766 | 8.278772e-05 | 9.469822e-05 | 0.020833333 | 0.020833333 | 48 | 1 | 1 | 0.51020363 | 0.51020363 | — | 0.83482092 | -10.408807 | 0.0019530795 |
| EURUSD | 5 | chronos2 | 48 | 0.0044894456 | 0.00023634717 | 0.00038239152 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -8.6186349 | 0.0050990737 |
| EURUSD | 5 | fincast | 48 | — | — | — | — | — | — | — | — | — | — | — | — | -8.7189192 | 0.0054078446 |
| EURUSD | 5 | garch | 48 | 0.0043496956 | 0.00019671843 | 0.00041970544 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -8.6951541 | 0.0049408783 |
| EURUSD | 5 | hmm | 48 | 0.0045102858 | 0.0001855638 | 0.00023438546 | 0 | 0 | 48 | 0 | 0 | 0.32597239 | 0.32597239 | — | — | -8.7370779 | 0.0051574079 |
| EURUSD | 5 | toto | 48 | 0.0044457442 | 0.00026657914 | 0.00053318784 | 0 | 0.020833333 | 48 | 0 | 1 | 0.32597239 | 0.51020363 | — | 0.83482092 | -8.5700684 | 0.0050264561 |
| EURUSD | 20 | chronos2 | 48 | 0.0095235089 | 0.00052165275 | 0.00056233455 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.288847 | 0.010892507 |
| EURUSD | 20 | fincast | 48 | — | — | — | — | — | — | — | — | — | — | — | — | -7.3557727 | 0.010827376 |
| EURUSD | 20 | garch | 48 | 0.0091206656 | 0.0004257478 | 0.00044620021 | 0.020833333 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.2780853 | 0.01044203 |
| EURUSD | 20 | hmm | 48 | 0.0098973824 | 0.00044053724 | 0.0005134913 | 0.020833333 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.327993 | 0.011328707 |
| EURUSD | 20 | toto | 48 | 0.0093120702 | 0.0010439388 | 0.00060981905 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.260711 | 0.010571325 |
| GBPAUD | 1 | chronos2 | 50 | 0.0022060299 | 0.00011761597 | 0.00013893496 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -10.007767 | 0.0025121605 |
| GBPAUD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.988176 | 0.002570501 |
| GBPAUD | 1 | garch | 50 | 0.0020787595 | 9.2900285e-05 | 9.7963045e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.079944 | 0.002374495 |
| GBPAUD | 1 | hmm | 50 | 0.0020909162 | 8.4673447e-05 | 9.4405327e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.071902 | 0.0023928 |
| GBPAUD | 1 | toto | 50 | 0.0024533301 | 0.00012659025 | 0.00017032152 | 0.02 | 0.04 | 50 | 1 | 2 | 0.53158437 | 0.1074658 | 0.83825072 | 0.67987714 | -9.7483555 | 0.0027950645 |
| GBPAUD | 5 | chronos2 | 50 | 0.0044003512 | 0.00020158771 | 0.00023445021 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.5899405 | 0.0050235506 |
| GBPAUD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.6048947 | 0.0050159887 |
| GBPAUD | 5 | garch | 50 | 0.0042590386 | 0.00021009441 | 0.00021802801 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.6266722 | 0.0048556721 |
| GBPAUD | 5 | hmm | 50 | 0.0043152794 | 0.00019938866 | 0.00021678373 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.6342252 | 0.0049287744 |
| GBPAUD | 5 | toto | 50 | 0.0048691406 | 0.0010643649 | 0.0003542372 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.5524586 | 0.0054519754 |
| GBPAUD | 20 | chronos2 | 50 | 0.0097575362 | 0.00088151565 | 0.00057157716 | 0.02 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.2197283 | 0.011063852 |
| GBPAUD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.2019466 | 0.010572549 |
| GBPAUD | 20 | garch | 50 | 0.0094576221 | 0.0005092949 | 0.00044313201 | 0.02 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.2365967 | 0.010788338 |
| GBPAUD | 20 | hmm | 50 | 0.0095428856 | 0.00059167442 | 0.00050571679 | 0.02 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.2321256 | 0.010879354 |
| GBPAUD | 20 | toto | 50 | 0.010998315 | 0.003501265 | 0.0016060715 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0857953 | 0.01202606 |
| GBPCAD | 1 | chronos2 | 50 | 0.0020692031 | 0.00011650928 | 0.00010605711 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.816309 | 0.002358159 |
| GBPCAD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -10.015752 | 0.002792441 |
| GBPCAD | 1 | garch | 50 | 0.0021098736 | 8.4790181e-05 | 0.00017362367 | 0.04 | 0.02 | 50 | 2 | 1 | 0.1074658 | 0.53158437 | 0.67987714 | 0.83825072 | -9.9907865 | 0.002401048 |
| GBPCAD | 1 | hmm | 50 | 0.0020911288 | 9.5547125e-05 | 0.00015580281 | 0.04 | 0.02 | 50 | 2 | 1 | 0.1074658 | 0.53158437 | 0.67987714 | 0.83825072 | -10.068268 | 0.0023832113 |
| GBPCAD | 1 | toto | 50 | 0.002081131 | 0.0001353116 | 8.8480681e-05 | 0.04 | 0.02 | 50 | 2 | 1 | 0.1074658 | 0.53158437 | 0.67987714 | 0.83825072 | -9.9166696 | 0.0023647091 |
| GBPCAD | 5 | chronos2 | 50 | 0.00324038 | 0.00030076006 | 0.00019206697 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.8115325 | 0.0036725137 |
| GBPCAD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.7578194 | 0.0040436522 |
| GBPCAD | 5 | garch | 50 | 0.0033400186 | 0.00018757616 | 0.00019251853 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.7936114 | 0.003800345 |
| GBPCAD | 5 | hmm | 50 | 0.0033073421 | 0.00018412622 | 0.00018713747 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.8191451 | 0.0037693714 |
| GBPCAD | 5 | toto | 50 | 0.0035557633 | 0.00098662093 | 0.00029101891 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.7403827 | 0.0039521077 |
| GBPCAD | 20 | chronos2 | 50 | 0.0055559405 | 0.00041687029 | 0.00035763757 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.2521887 | 0.0063032881 |
| GBPCAD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.347559 | 0.0069545496 |
| GBPCAD | 20 | garch | 50 | 0.0063650708 | 0.00036861915 | 0.00038965789 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.4058131 | 0.0072365078 |
| GBPCAD | 20 | hmm | 50 | 0.0061136233 | 0.00036764383 | 0.00035956676 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.4463905 | 0.0069625244 |
| GBPCAD | 20 | toto | 50 | 0.0067501136 | 0.0054339345 | 0.0013008222 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.1139198 | 0.0069259 |
| GBPCHF | 1 | chronos2 | 49 | 0.0017863868 | 0.00010445616 | 0.00012550274 | 0 | 0.020408163 | 49 | 0 | 1 | 0.32098398 | 0.52091544 | — | 0.8365628 | -10.300679 | 0.0020293496 |
| GBPCHF | 1 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -10.216374 | 0.0021311209 |
| GBPCHF | 1 | garch | 49 | 0.0018571929 | 0.00014771403 | 9.2152833e-05 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | — | — | -10.25193 | 0.0021091787 |
| GBPCHF | 1 | hmm | 49 | 0.0018781919 | 0.00017259252 | 8.8227287e-05 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | — | — | -10.066651 | 0.0021246324 |
| GBPCHF | 1 | toto | 49 | 0.0019259574 | 0.00015693286 | 0.0001654407 | 0.06122449 | 0.040816327 | 49 | 3 | 2 | 0.014436675 | 0.10332307 | 0.60747077 | 0.67660924 | -10.273625 | 0.0021784048 |
| GBPCHF | 5 | chronos2 | 49 | 0.0034152256 | 0.00019833572 | 0.0002316926 | 0 | 0.040816327 | 49 | 0 | 2 | 0.32098398 | 0.10332307 | — | 0.67660924 | -8.7118913 | 0.0038895233 |
| GBPCHF | 5 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -8.8180181 | 0.0039143425 |
| GBPCHF | 5 | garch | 49 | 0.0035066709 | 0.00019976969 | 0.00018274176 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.8301338 | 0.004003966 |
| GBPCHF | 5 | hmm | 49 | 0.0035398691 | 0.00025002422 | 0.00016349817 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.8354541 | 0.0040400677 |
| GBPCHF | 5 | toto | 49 | 0.0036990969 | 0.00024758943 | 0.00031528539 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.6781068 | 0.0042031308 |
| GBPCHF | 20 | chronos2 | 49 | 0.0060384388 | 0.00047537895 | 0.00040063907 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.3276586 | 0.0068534764 |
| GBPCHF | 20 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -7.4096369 | 0.0070123767 |
| GBPCHF | 20 | garch | 49 | 0.0063133367 | 0.00041500715 | 0.0003509417 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.4874563 | 0.0071888557 |
| GBPCHF | 20 | hmm | 49 | 0.0064737055 | 0.00058576605 | 0.00031965126 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.4780529 | 0.0073344589 |
| GBPCHF | 20 | toto | 49 | 0.0066968906 | 0.00062672907 | 0.00077277448 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.457566 | 0.0075361133 |
| GBPJPY | 1 | chronos2 | 50 | 0.0026407853 | 0.0001861741 | 0.00014525423 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.3871904 | 0.002998416 |
| GBPJPY | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.2735831 | 0.0031893432 |
| GBPJPY | 1 | garch | 50 | 0.0026486125 | 0.00031869026 | 0.0001291615 | 0.1 | 0 | 50 | 5 | 0 | 0.00014408777 | 0.31609559 | 0.48692165 | — | -9.2271726 | 0.0029747943 |
| GBPJPY | 1 | hmm | 50 | 0.0026345462 | 0.00017113864 | 0.00012503399 | 0.08 | 0 | 50 | 4 | 0 | 0.0016626471 | 0.31609559 | 0.39876393 | — | -9.2521049 | 0.0029848642 |
| GBPJPY | 1 | toto | 50 | 0.0031092193 | 0.0010187169 | 0.00019787063 | 0.16 | 0.04 | 50 | 8 | 2 | 3.2370524e-08 | 0.1074658 | 0.74192631 | 0.67987714 | -4.0159357 | 0.0034018353 |
| GBPJPY | 5 | chronos2 | 50 | 0.0051318763 | 0.00030141251 | 0.00023593958 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.0925838 | 0.0058332813 |
| GBPJPY | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.214023 | 0.0060212012 |
| GBPJPY | 5 | garch | 50 | 0.0052362183 | 0.00055714459 | 0.00026303958 | 0.06 | 0 | 50 | 3 | 0 | 0.015322518 | 0.31609559 | 0.5314689 | — | -8.2172266 | 0.0059112136 |
| GBPJPY | 5 | hmm | 50 | 0.0051842963 | 0.00046889226 | 0.00025360118 | 0.04 | 0 | 50 | 2 | 0 | 0.1074658 | 0.31609559 | 0.67987714 | — | -8.1979057 | 0.005874266 |
| GBPJPY | 5 | toto | 50 | 0.0058671156 | 0.0013660674 | 0.0006063198 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -6.7193328 | 0.0065118753 |
| GBPJPY | 20 | chronos2 | 50 | 0.0092857297 | 0.00064011071 | 0.00052345197 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7742293 | 0.010609851 |
| GBPJPY | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -6.8835943 | 0.010652827 |
| GBPJPY | 20 | garch | 50 | 0.010068392 | 0.00042953238 | 0.00056500394 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.8714677 | 0.01148155 |
| GBPJPY | 20 | hmm | 50 | 0.0097016856 | 0.00049072202 | 0.0005181424 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.8606929 | 0.011077596 |
| GBPJPY | 20 | toto | 50 | 0.011323997 | 0.0058137256 | 0.0050176383 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.4014019 | 0.011871107 |
| GBPNZD | 1 | chronos2 | 50 | 0.0019821337 | 0.00011107648 | 0.00011995086 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.176903 | 0.0022664228 |
| GBPNZD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -10.159919 | 0.0025781492 |
| GBPNZD | 1 | garch | 50 | 0.0020210019 | 7.907348e-05 | 9.2803219e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.196628 | 0.002318602 |
| GBPNZD | 1 | hmm | 50 | 0.002000242 | 7.6868688e-05 | 8.9211543e-05 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -10.223955 | 0.0022914128 |
| GBPNZD | 1 | toto | 50 | 0.0020773399 | 7.1824437e-05 | 0.00015401865 | 0.04 | 0.04 | 50 | 2 | 2 | 0.1074658 | 0.1074658 | 0.67987714 | 0.67987714 | -9.6833216 | 0.0023690393 |
| GBPNZD | 5 | chronos2 | 50 | 0.0039322826 | 0.00021820118 | 0.00023163692 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.7517853 | 0.0044821218 |
| GBPNZD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.7186491 | 0.0049020521 |
| GBPNZD | 5 | garch | 50 | 0.0039077552 | 0.00023093116 | 0.00019620283 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.7488159 | 0.0044575518 |
| GBPNZD | 5 | hmm | 50 | 0.0039421375 | 0.00020430681 | 0.00018982098 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.7445556 | 0.0045046918 |
| GBPNZD | 5 | toto | 50 | 0.0040624441 | 0.0005302249 | 0.00037427429 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.6036841 | 0.0045645795 |
| GBPNZD | 20 | chronos2 | 50 | 0.0080188865 | 0.00045788788 | 0.00047022868 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.3677739 | 0.0091240132 |
| GBPNZD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.3028809 | 0.0091926846 |
| GBPNZD | 20 | garch | 50 | 0.0084213585 | 0.00037840236 | 0.00039413029 | 0.02 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.3732805 | 0.0096254958 |
| GBPNZD | 20 | hmm | 50 | 0.0083678053 | 0.00043727961 | 0.00038580185 | 0.02 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -7.3489396 | 0.0095587847 |
| GBPNZD | 20 | toto | 50 | 0.007955681 | 0.0044479524 | 0.0010871248 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.1816686 | 0.0084939706 |
| GBPUSD | 1 | chronos2 | 50 | 0.0024800155 | 0.00012042676 | 0.00012633354 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.8145287 | 0.002831616 |
| GBPUSD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.8613633 | 0.0029969563 |
| GBPUSD | 1 | garch | 50 | 0.0023897291 | 0.00010488532 | 0.00016502847 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -9.8513682 | 0.0027252763 |
| GBPUSD | 1 | hmm | 50 | 0.0024593448 | 0.00011771182 | 0.00017275414 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -9.7679814 | 0.002801919 |
| GBPUSD | 1 | toto | 50 | 0.0024671581 | 0.00013385503 | 0.00017113143 | 0.02 | 0.08 | 50 | 1 | 4 | 0.53158437 | 0.0016626471 | 0.83825072 | 0.39876393 | -9.5209999 | 0.0028055881 |
| GBPUSD | 5 | chronos2 | 50 | 0.0045123462 | 0.00024800124 | 0.00047810969 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.3885287 | 0.0051155682 |
| GBPUSD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.4281145 | 0.0052072193 |
| GBPUSD | 5 | garch | 50 | 0.0044792833 | 0.0002086585 | 0.0004285859 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.4121362 | 0.0050844687 |
| GBPUSD | 5 | hmm | 50 | 0.004666954 | 0.0002124725 | 0.00044975152 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.4187812 | 0.0053071877 |
| GBPUSD | 5 | toto | 50 | 0.0046853511 | 0.00050501285 | 0.00050506983 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -8.2788922 | 0.0052740929 |
| GBPUSD | 20 | chronos2 | 50 | 0.0082799402 | 0.00053995415 | 0.00049840914 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0300007 | 0.0094379121 |
| GBPUSD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.0319481 | 0.0096920495 |
| GBPUSD | 20 | garch | 50 | 0.0082938455 | 0.0004187512 | 0.00043900285 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0114002 | 0.0094843806 |
| GBPUSD | 20 | hmm | 50 | 0.0088183838 | 0.00042171297 | 0.00046284295 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0539521 | 0.010084857 |
| GBPUSD | 20 | toto | 50 | 0.0078770315 | 0.0021058213 | 0.0008080041 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.9052583 | 0.0087304155 |
| NZDCAD | 1 | chronos2 | 50 | 0.0025834415 | 0.00013240272 | 0.0001310197 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.6204468 | 0.0029475551 |
| NZDCAD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.5795691 | 0.0031582616 |
| NZDCAD | 1 | garch | 50 | 0.0025018388 | 0.00010105233 | 0.00016223196 | 0 | 0.06 | 50 | 0 | 3 | 0.31609559 | 0.015322518 | — | 0.5314689 | -9.66279 | 0.0028526565 |
| NZDCAD | 1 | hmm | 50 | 0.0024964145 | 9.8553512e-05 | 0.00014743156 | 0 | 0.04 | 50 | 0 | 2 | 0.31609559 | 0.1074658 | — | 0.67987714 | -9.7655323 | 0.0028549845 |
| NZDCAD | 1 | toto | 50 | 0.0026085723 | 0.00018122311 | 0.00022291171 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -9.3337835 | 0.0029534282 |
| NZDCAD | 5 | chronos2 | 50 | 0.0048084778 | 0.00026468135 | 0.00025103561 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.3259768 | 0.0054779849 |
| NZDCAD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -8.0605095 | 0.0054628763 |
| NZDCAD | 5 | garch | 50 | 0.0047190445 | 0.00023898983 | 0.00022452091 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -8.2734963 | 0.0053993881 |
| NZDCAD | 5 | hmm | 50 | 0.0048299902 | 0.00026615303 | 0.00021632848 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.3010267 | 0.0055212005 |
| NZDCAD | 5 | toto | 50 | 0.004760105 | 0.0002334458 | 0.00038698707 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -8.2552732 | 0.0054231305 |
| NZDCAD | 20 | chronos2 | 50 | 0.0086882768 | 0.00050256651 | 0.00069629597 | 0 | 0.06 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.7912864 | 0.0098563394 |
| NZDCAD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -6.6709273 | 0.0092003747 |
| NZDCAD | 20 | garch | 50 | 0.0086475058 | 0.00044810549 | 0.0004439606 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.893131 | 0.0098789874 |
| NZDCAD | 20 | hmm | 50 | 0.0088212875 | 0.00049027717 | 0.00047144466 | 0 | 0.02 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.888866 | 0.01005786 |
| NZDCAD | 20 | toto | 50 | 0.0087893565 | 0.00043471217 | 0.0011056815 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7540931 | 0.0099434615 |
| NZDCHF | 1 | chronos2 | 49 | 0.0023679157 | 0.00016410159 | 0.00014442052 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -9.883024 | 0.002690948 |
| NZDCHF | 1 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -9.761571 | 0.0025784622 |
| NZDCHF | 1 | garch | 49 | 0.0022312615 | 0.0001929521 | 0.00011671851 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | — | — | -9.8918846 | 0.0025359482 |
| NZDCHF | 1 | hmm | 49 | 0.0022398056 | 0.00020663601 | 0.00011181894 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | — | — | -9.8504205 | 0.0025419297 |
| NZDCHF | 1 | toto | 49 | 0.0022291706 | 0.00026884764 | 0.00015015312 | 0.040816327 | 0.020408163 | 49 | 2 | 1 | 0.10332307 | 0.52091544 | 0.76927566 | 0.8365628 | -9.7724615 | 0.0025133743 |
| NZDCHF | 5 | chronos2 | 49 | 0.0040865151 | 0.00028224682 | 0.00023912261 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.3534207 | 0.0046521777 |
| NZDCHF | 5 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -8.2075103 | 0.0042644089 |
| NZDCHF | 5 | garch | 49 | 0.0040401755 | 0.00026499059 | 0.00024780967 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.4192499 | 0.004591522 |
| NZDCHF | 5 | hmm | 49 | 0.004100174 | 0.00028005109 | 0.00023019397 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.4194357 | 0.0046672145 |
| NZDCHF | 5 | toto | 49 | 0.0041398338 | 0.00028682054 | 0.00054688848 | 0 | 0.020408163 | 49 | 0 | 1 | 0.32098398 | 0.52091544 | — | 0.8365628 | -8.3096292 | 0.0046697509 |
| NZDCHF | 20 | chronos2 | 49 | 0.0073866323 | 0.00067367295 | 0.00055767604 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0273489 | 0.0083776718 |
| NZDCHF | 20 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -6.839683 | 0.0075260164 |
| NZDCHF | 20 | garch | 49 | 0.0080037003 | 0.00056830052 | 0.00047521666 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0285052 | 0.0090926718 |
| NZDCHF | 20 | hmm | 49 | 0.0082792965 | 0.00073826664 | 0.00045123353 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.0308094 | 0.009390006 |
| NZDCHF | 20 | toto | 49 | 0.0086362024 | 0.00084610289 | 0.0027806684 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.9377402 | 0.0095458537 |
| NZDJPY | 1 | chronos2 | 50 | 0.0031075531 | 0.0001972785 | 0.0001671464 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.3910456 | 0.0035366198 |
| NZDJPY | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.3930284 | 0.003549603 |
| NZDJPY | 1 | garch | 50 | 0.0029927346 | 0.00016934577 | 0.00014838343 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.4078593 | 0.0034087332 |
| NZDJPY | 1 | hmm | 50 | 0.0029947479 | 0.00019311227 | 0.00014956542 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.2984175 | 0.0034083071 |
| NZDJPY | 1 | toto | 50 | 0.0032990589 | 0.00020582923 | 0.00030825091 | 0.06 | 0.04 | 50 | 3 | 2 | 0.015322518 | 0.1074658 | 0.5314689 | 0.77165 | -7.7807993 | 0.0037362336 |
| NZDJPY | 5 | chronos2 | 50 | 0.0062069172 | 0.0003350724 | 0.00029657929 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -7.7933859 | 0.0070916348 |
| NZDJPY | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.8300124 | 0.0072891985 |
| NZDJPY | 5 | garch | 50 | 0.0061256421 | 0.00047634415 | 0.00032176556 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -7.895283 | 0.0069590861 |
| NZDJPY | 5 | hmm | 50 | 0.0060763696 | 0.0003912289 | 0.00031002245 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -7.8657683 | 0.0069334936 |
| NZDJPY | 5 | toto | 50 | 0.0061294466 | 0.00054087178 | 0.00035050383 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 1 | -7.5658577 | 0.0069974541 |
| NZDJPY | 20 | chronos2 | 50 | 0.011456755 | 0.00065043132 | 0.0006111769 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.3445023 | 0.013048106 |
| NZDJPY | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -6.4863636 | 0.013054715 |
| NZDJPY | 20 | garch | 50 | 0.012279434 | 0.00078868126 | 0.00066252914 | 0.04 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -6.5011731 | 0.013968284 |
| NZDJPY | 20 | hmm | 50 | 0.012170137 | 0.00081008329 | 0.00064157329 | 0.04 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -6.4946673 | 0.013817003 |
| NZDJPY | 20 | toto | 50 | 0.014403365 | 0.0027745659 | 0.0038014618 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.2779472 | 0.015861964 |
| NZDUSD | 1 | chronos2 | 50 | 0.003228413 | 0.00017618355 | 0.00016858946 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.0646184 | 0.0036955542 |
| NZDUSD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.0999876 | 0.0036460205 |
| NZDUSD | 1 | garch | 50 | 0.003228367 | 0.00013280329 | 0.00022793691 | 0 | 0.04 | 50 | 0 | 2 | 0.31609559 | 0.1074658 | — | 0.67987714 | -9.124866 | 0.0036727822 |
| NZDUSD | 1 | hmm | 50 | 0.0032285307 | 0.00013343451 | 0.00020518928 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -9.237673 | 0.0036842954 |
| NZDUSD | 1 | toto | 50 | 0.0034223666 | 0.00017152618 | 0.00030372598 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -8.6391375 | 0.0038892575 |
| NZDUSD | 5 | chronos2 | 50 | 0.0065955025 | 0.00035988836 | 0.00047752271 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -7.8427766 | 0.0075056335 |
| NZDUSD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.7244937 | 0.0072391058 |
| NZDUSD | 5 | garch | 50 | 0.0064599717 | 0.0002966802 | 0.00055558027 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -7.8139382 | 0.0073465344 |
| NZDUSD | 5 | hmm | 50 | 0.0067434203 | 0.00029517016 | 0.00065064668 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -7.8376403 | 0.0076475765 |
| NZDUSD | 5 | toto | 50 | 0.0066488425 | 0.00035478629 | 0.00069673599 | 0 | 0.02 | 50 | 0 | 1 | 0.31609559 | 0.53158437 | — | 0.83825072 | -7.7886555 | 0.0075356101 |
| NZDUSD | 20 | chronos2 | 50 | 0.01418676 | 0.00074925736 | 0.00070599967 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.4228041 | 0.016218733 |
| NZDUSD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -6.3696562 | 0.015288271 |
| NZDUSD | 20 | garch | 50 | 0.014274041 | 0.00060154359 | 0.00059231431 | 0 | 0.02 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.4116211 | 0.016319906 |
| NZDUSD | 20 | hmm | 50 | 0.01614697 | 0.00060757657 | 0.00094229691 | 0 | 0.04 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -6.4230436 | 0.01844092 |
| NZDUSD | 20 | toto | 50 | 0.014132145 | 0.00092022742 | 0.0019440733 | 0.02 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.4182388 | 0.015941138 |
| USDCAD | 1 | chronos2 | 50 | 0.0014142306 | 8.6757481e-05 | 9.3138849e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -10.922353 | 0.0016114672 |
| USDCAD | 1 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -10.918731 | 0.0016881045 |
| USDCAD | 1 | garch | 50 | 0.0013432379 | 7.6485751e-05 | 7.4949911e-05 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -11.034393 | 0.0015303352 |
| USDCAD | 1 | hmm | 50 | 0.0013337323 | 7.0353905e-05 | 6.4170292e-05 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -11.026384 | 0.0015252951 |
| USDCAD | 1 | toto | 50 | 0.0013533397 | 0.00011918077 | 7.5330704e-05 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -10.888349 | 0.0015369718 |
| USDCAD | 5 | chronos2 | 50 | 0.0038081665 | 0.00036687857 | 0.00016708542 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.156457 | 0.0043326351 |
| USDCAD | 5 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -9.2172453 | 0.0044459874 |
| USDCAD | 5 | garch | 50 | 0.0036794034 | 0.00037886294 | 0.00016340093 | 0.02 | 0 | 50 | 1 | 0 | 0.53158437 | 0.31609559 | 0.83825072 | — | -9.1719862 | 0.0041788355 |
| USDCAD | 5 | hmm | 50 | 0.0038096491 | 0.00037913425 | 0.00014274071 | 0.02 | 0.02 | 50 | 1 | 1 | 0.53158437 | 0.53158437 | 0.83825072 | 0.83825072 | -9.215552 | 0.004339684 |
| USDCAD | 5 | toto | 50 | 0.0035970817 | 0.00040091862 | 0.00029837211 | 0 | 0 | 50 | 0 | 0 | 0.31609559 | 0.31609559 | — | — | -9.1359133 | 0.0040623438 |
| USDCAD | 20 | chronos2 | 50 | 0.0088688008 | 0.00037738085 | 0.00041998234 | 0 | 0.02 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.7445346 | 0.010152354 |
| USDCAD | 20 | fincast | 50 | — | — | — | — | — | — | — | — | — | — | — | — | -7.8213144 | 0.01017078 |
| USDCAD | 20 | garch | 50 | 0.0091060353 | 0.0003029496 | 0.00032774591 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.72992 | 0.010468237 |
| USDCAD | 20 | hmm | 50 | 0.0095064715 | 0.00058034932 | 0.00030359888 | 0.02 | 0.02 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.7675285 | 0.010881104 |
| USDCAD | 20 | toto | 50 | 0.0084049219 | 0.0015461235 | 0.00091189723 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -7.7085181 | 0.0094139197 |
| USDCHF | 1 | chronos2 | 49 | 0.0024500132 | 0.00016182489 | 0.00016270091 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -9.7372157 | 0.0027942269 |
| USDCHF | 1 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -9.7647038 | 0.0028388098 |
| USDCHF | 1 | garch | 49 | 0.0024906506 | 0.00014196354 | 0.00011840286 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | 0.8365628 | — | -9.7699402 | 0.0028474886 |
| USDCHF | 1 | hmm | 49 | 0.0025178607 | 0.00012834289 | 0.00010516243 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | 0.8365628 | — | -9.73418 | 0.0028853992 |
| USDCHF | 1 | toto | 49 | 0.0025133499 | 0.00012185057 | 0.00014110777 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -9.7779076 | 0.0028731819 |
| USDCHF | 5 | chronos2 | 49 | 0.0053773604 | 0.00047081824 | 0.00027039662 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | 0.8365628 | — | -8.1572715 | 0.0061161468 |
| USDCHF | 5 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -8.2237509 | 0.0065635791 |
| USDCHF | 5 | garch | 49 | 0.005402366 | 0.00032409061 | 0.00025523972 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | 0.8365628 | — | -8.2298882 | 0.0061703781 |
| USDCHF | 5 | hmm | 49 | 0.005747979 | 0.00030764012 | 0.00021823107 | 0 | 0 | 49 | 0 | 0 | 0.32098398 | 0.32098398 | — | — | -8.2111194 | 0.0065740436 |
| USDCHF | 5 | toto | 49 | 0.0054097312 | 0.00070294089 | 0.00043957374 | 0.020408163 | 0 | 49 | 1 | 0 | 0.52091544 | 0.32098398 | 0.8365628 | — | -8.0083632 | 0.0060893202 |
| USDCHF | 20 | chronos2 | 49 | 0.0095068332 | 0.00067406064 | 0.0006183124 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7683075 | 0.010823239 |
| USDCHF | 20 | fincast | 49 | — | — | — | — | — | — | — | — | — | — | — | — | -6.7502363 | 0.011430518 |
| USDCHF | 20 | garch | 49 | 0.0093140623 | 0.0005550325 | 0.00049487841 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.8199957 | 0.010610977 |
| USDCHF | 20 | hmm | 49 | 0.010325748 | 0.00083682703 | 0.0004039212 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.7833312 | 0.011770087 |
| USDCHF | 20 | toto | 49 | 0.010057273 | 0.0010189943 | 0.00098874902 | 0.040816327 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -6.4095512 | 0.011344021 |
| USDJPY | 1 | chronos2 | 42 | 0.002673241 | 0.00021249341 | 0.00014816816 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -8.9392495 | 0.0030206778 |
| USDJPY | 1 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -8.9768544 | 0.0033551662 |
| USDJPY | 1 | garch | 42 | 0.0027318991 | 0.00057133429 | 0.00014478049 | 0.071428571 | 0 | 42 | 3 | 0 | 0.0091148606 | 0.35819029 | 0.49107158 | — | -8.8511415 | 0.003032475 |
| USDJPY | 1 | hmm | 42 | 0.0026694442 | 0.00034578518 | 0.00012614047 | 0.047619048 | 0.023809524 | 42 | 2 | 1 | 0.076234514 | 0.44508829 | 0.65054142 | 0.82305421 | -9.2957402 | 0.0030022361 |
| USDJPY | 1 | toto | 42 | 0.0026904767 | 0.00028897052 | 0.00011249322 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -6.1151029 | 0.0030284175 |
| USDJPY | 5 | chronos2 | 42 | 0.0060122192 | 0.00064513234 | 0.00026317694 | 0.047619048 | 0 | 42 | 2 | 0 | 0.076234514 | 0.35819029 | 0.65054142 | — | -7.7994424 | 0.0067868999 |
| USDJPY | 5 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -7.9797609 | 0.0069652265 |
| USDJPY | 5 | garch | 42 | 0.0061226257 | 0.00076867755 | 0.00031336974 | 0.071428571 | 0 | 42 | 3 | 0 | 0.0091148606 | 0.35819029 | 0.49107158 | — | -7.9086334 | 0.0068895461 |
| USDJPY | 5 | hmm | 42 | 0.006197122 | 0.00049055409 | 0.00026025544 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -8.0092405 | 0.0070446166 |
| USDJPY | 5 | toto | 42 | 0.0060077556 | 0.0010291631 | 0.0002988098 | 0.023809524 | 0 | 42 | 1 | 0 | 0.44508829 | 0.35819029 | 0.82305421 | — | -6.485309 | 0.0067657966 |
| USDJPY | 20 | chronos2 | 42 | 0.0092257582 | 0.00067982311 | 0.00054813339 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -6.4268963 | 0.010497059 |
| USDJPY | 20 | fincast | 42 | — | — | — | — | — | — | — | — | — | — | — | — | -6.6522466 | 0.011232836 |
| USDJPY | 20 | garch | 42 | 0.0098850944 | 0.00060848314 | 0.00066978239 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -6.5935508 | 0.011253519 |
| USDJPY | 20 | hmm | 42 | 0.010676443 | 0.00071139221 | 0.00055122962 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -6.6222137 | 0.012180619 |
| USDJPY | 20 | toto | 42 | 0.01065881 | 0.0061308283 | 0.0026800195 | 0 | 0 | 12 | 0 | 0 | 0.62333495 | 0.62333495 | — | — | -5.828645 | 0.011259661 |

| corrida | modelos | cada | solo limpia | CPU s/origen | pared inferencia / total s | fallos | SHA-256 predicciones |
|---|---|---|---|---|---|---|---|
| `E:\quantdesk-lab\runs\TS-00-BENCH\lago_cierre_c20261101` | hmm,garch,chronos2 | 1 | False | chronos2: 0.2367; garch: 0.08285; hmm: 0.1954 | 2457.06 / no medida | {'chronos2': 0, 'garch': 0, 'hmm': 0} | `f130e892181f932f6a870911aaad96ef6ec73d0a3d440eaf10aa20b01f2092aa` |
| `E:\quantdesk-lab\runs\TS-00-BENCH\toto_lago_cierre_c20261101` | toto | 5 | False | toto: 7.138 | 15177.85 / no medida | {'toto': 0} | `cab8e95d13845c6f8d169937083d9e777eb74e12a033fc0b86aeb6885dcca09c` |
| `E:\quantdesk-lab\runs\TS-00-BENCH-FINCAST\fincast_fx` | fincast | 5 | True | fincast: 1.645 | 1732.09 / 1856.4765409000101 | {'fincast': 9} | `1ea978134e8c6949f3bd32de7a6e70fa6db62f5d97db8e0daf60bf139832356e` |
Limitacion del driver inicial de esta corrida: CPU externa de respuestas fallidas no conservada y recargas posteriores no sumadas a CPU de carga inicial; si incluidas en pared. La CPU por origen es la registrada, no el coste completo de los fallos. El informe principal adjunta tambien CPU por origen valido.
Fallo declarado: AUDNZD 1766534400000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: CADCHF 1768521600000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: EURAUD 1788480000000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: EURAUD 1790294400000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: EURJPY 1776384000000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: EURUSD 1765929600000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: EURUSD 1767916800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: NZDCHF 1768521600000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: USDCHF 1764720000000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.

### binance_c20261101: ventana limpia

Dataset SHA-256: `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744`. Estado: **calculada**. Orígenes comunes por activo y horizonte: columna n.

**Predicciones archivadas invalidas:** 283 pares origen-modelo ({'chronos2': 283}) con cuantiles no finitos/no monotonos, excluidos de TODOS los horizontes de la comparacion limpia. No se reparan cuantiles ni se reescriben predicciones o criterios de las tablas principales historicas. La validacion cuenta todos los origenes limpios suministrados antes de tomar la interseccion; n es el numero comun realmente puntuado por celda. La validacion del archivo solo puede comprobar los horizontes almacenados (1/5/20); una corrida nueva comprueba los 20 horizontes. Ejemplos: [{'instrument': 'ADAUSDT', 'origen_ms': 1772928000000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1773187200000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1773446400000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1773964800000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1774224000000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1774483200000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1774742400000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1775001600000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1775260800000, 'modelo': 'chronos2'}, {'instrument': 'ADAUSDT', 'origen_ms': 1775520000000, 'modelo': 'chronos2'}].

| instrument | h | modelo | n | crps | pinball_01 | pinball_99 | exc_01 | exc_99 | n_test | x_01 | x_99 | kupiec_01_p | kupiec_99_p | christ_01_p | christ_99_p | qlike | crps_deciles |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | 1 | chronos2 | 5 | 0.020295042 | 0.001064136 | 0.0023687294 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -5.3160881 | 0.022928475 |
| ADAUSDT | 1 | fincast | 5 | — | — | — | — | — | — | — | — | — | — | — | — | -5.557284 | 0.023005979 |
| ADAUSDT | 1 | garch | 5 | 0.020240055 | 0.00077657467 | 0.0014403521 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -5.5268668 | 0.023008541 |
| ADAUSDT | 1 | hmm | 5 | 0.020376959 | 0.00074932196 | 0.0015103297 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -5.4845004 | 0.023156167 |
| ADAUSDT | 1 | toto | 5 | 0.019380132 | 0.00082457165 | 0.0014825912 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -5.4457027 | 0.022356553 |
| ADAUSDT | 5 | chronos2 | 5 | 0.048282139 | 0.0018221465 | 0.0043050412 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -4.0045554 | 0.055206397 |
| ADAUSDT | 5 | fincast | 5 | — | — | — | — | — | — | — | — | — | — | — | — | -4.177996 | 0.047725719 |
| ADAUSDT | 5 | garch | 5 | 0.045873098 | 0.0017178459 | 0.0030260885 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -4.0654584 | 0.052527692 |
| ADAUSDT | 5 | hmm | 5 | 0.047623303 | 0.0017644485 | 0.003703462 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -4.0062238 | 0.053877527 |
| ADAUSDT | 5 | toto | 5 | 0.039335025 | 0.0028191428 | 0.0029286176 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -4.1543116 | 0.04438966 |
| ADAUSDT | 20 | chronos2 | 5 | 0.1315241 | 0.0042446751 | 0.010285306 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -2.0589689 | 0.15084906 |
| ADAUSDT | 20 | fincast | 5 | — | — | — | — | — | — | — | — | — | — | — | — | -1.9534048 | 0.11412375 |
| ADAUSDT | 20 | garch | 5 | 0.089144297 | 0.0039924834 | 0.0057370796 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -1.8990729 | 0.10204657 |
| ADAUSDT | 20 | hmm | 5 | 0.093948605 | 0.0035721637 | 0.0069040198 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -1.9327083 | 0.10636103 |
| ADAUSDT | 20 | toto | 5 | 0.093552565 | 0.0048173978 | 0.008070781 | 0 | 0 | 5 | 0 | 0 | 0.75122642 | 0.75122642 | — | — | -2.0653309 | 0.10622646 |
| BNBUSDT | 1 | chronos2 | 11 | 0.010350229 | 0.0004895206 | 0.00068199937 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.7710365 | 0.011812454 |
| BNBUSDT | 1 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -6.0255606 | 0.011984663 |
| BNBUSDT | 1 | garch | 11 | 0.010793143 | 0.00055877607 | 0.00070374009 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.8919863 | 0.012316454 |
| BNBUSDT | 1 | hmm | 11 | 0.011054489 | 0.00053704245 | 0.00071039317 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.8705013 | 0.012680861 |
| BNBUSDT | 1 | toto | 11 | 0.01163656 | 0.00088493992 | 0.00069515435 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -6.7962938 | 0.013199379 |
| BNBUSDT | 5 | chronos2 | 11 | 0.025989066 | 0.0012741411 | 0.00346155 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -5.0760804 | 0.029240426 |
| BNBUSDT | 5 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -4.555734 | 0.035784703 |
| BNBUSDT | 5 | garch | 11 | 0.025715886 | 0.0015188567 | 0.0025578579 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -5.2048009 | 0.028952953 |
| BNBUSDT | 5 | hmm | 11 | 0.026118698 | 0.0015297232 | 0.0014006723 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -5.2366951 | 0.029696979 |
| BNBUSDT | 5 | toto | 11 | 0.025039337 | 0.0013793341 | 0.006151019 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -5.0990938 | 0.027826607 |
| BNBUSDT | 20 | chronos2 | 11 | 0.071930913 | 0.016669928 | 0.0028667017 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -3.0277485 | 0.079775836 |
| BNBUSDT | 20 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -3.0114125 | 0.090996606 |
| BNBUSDT | 20 | garch | 11 | 0.071346466 | 0.010858435 | 0.0034296332 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -3.2161209 | 0.079668434 |
| BNBUSDT | 20 | hmm | 11 | 0.070398883 | 0.009566241 | 0.0031980746 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -3.3076052 | 0.078984011 |
| BNBUSDT | 20 | toto | 11 | 0.075247073 | 0.0039411871 | 0.0059398964 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -2.6366051 | 0.084765831 |
| BTCUSDT | 1 | chronos2 | 8 | 0.0085708157 | 0.00056832737 | 0.0005505293 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -7.2176359 | 0.0097078003 |
| BTCUSDT | 1 | fincast | 8 | — | — | — | — | — | — | — | — | — | — | — | — | -6.3984091 | 0.012920442 |
| BTCUSDT | 1 | garch | 8 | 0.0089778864 | 0.00062882926 | 0.00081658652 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -7.1749221 | 0.010157662 |
| BTCUSDT | 1 | hmm | 8 | 0.0089562499 | 0.00054041548 | 0.00070449325 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -7.1741576 | 0.010136512 |
| BTCUSDT | 1 | toto | 8 | 0.0090750087 | 0.00073968208 | 0.00060726893 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -7.2027778 | 0.010325005 |
| BTCUSDT | 5 | chronos2 | 8 | 0.019487657 | 0.0013240374 | 0.00092520107 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -5.2501687 | 0.022202887 |
| BTCUSDT | 5 | fincast | 8 | — | — | — | — | — | — | — | — | — | — | — | — | -4.6784276 | 0.024938451 |
| BTCUSDT | 5 | garch | 8 | 0.020481739 | 0.001621052 | 0.0014169057 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -5.2260312 | 0.023164644 |
| BTCUSDT | 5 | hmm | 8 | 0.019756282 | 0.0013437354 | 0.0013554157 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -5.3005526 | 0.02244233 |
| BTCUSDT | 5 | toto | 8 | 0.018673212 | 0.0015002509 | 0.00098843641 | 0 | 0 | 8 | 0 | 0 | 0.68841611 | 0.68841611 | — | — | -5.3916057 | 0.021236885 |
| BTCUSDT | 20 | chronos2 | 8 | 0.060098302 | 0.013687318 | 0.0024487276 | 0.125 | 0 | 8 | 1 | 0 | 0.06832859 | 0.68841611 | 0.56279146 | — | -2.9197971 | 0.066544005 |
| BTCUSDT | 20 | fincast | 8 | — | — | — | — | — | — | — | — | — | — | — | — | -3.0556611 | 0.072393191 |
| BTCUSDT | 20 | garch | 8 | 0.062402354 | 0.014803069 | 0.003203261 | 0.125 | 0 | 8 | 1 | 0 | 0.06832859 | 0.68841611 | 0.56279146 | — | -3.1353146 | 0.068874189 |
| BTCUSDT | 20 | hmm | 8 | 0.062061364 | 0.013668587 | 0.0028713554 | 0.125 | 0 | 8 | 1 | 0 | 0.06832859 | 0.68841611 | 0.56279146 | — | -3.3368209 | 0.068867846 |
| BTCUSDT | 20 | toto | 8 | 0.061338486 | 0.0062387651 | 0.0034085999 | 0.125 | 0 | 8 | 1 | 0 | 0.06832859 | 0.68841611 | 0.56279146 | — | -3.3952059 | 0.0689538 |
| DOGEUSDT | 1 | chronos2 | 10 | 0.014348284 | 0.0010108725 | 0.0015816102 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.1519881 | 0.016225729 |
| DOGEUSDT | 1 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -6.3188271 | 0.014514337 |
| DOGEUSDT | 1 | garch | 10 | 0.012388724 | 0.00098549078 | 0.0012235261 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.3243096 | 0.013991318 |
| DOGEUSDT | 1 | hmm | 10 | 0.013269157 | 0.00090329206 | 0.0013020622 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.1723227 | 0.014934204 |
| DOGEUSDT | 1 | toto | 10 | 0.012319163 | 0.00082686357 | 0.0014941901 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.5832511 | 0.01384071 |
| DOGEUSDT | 5 | chronos2 | 10 | 0.035224176 | 0.0019446967 | 0.0027129056 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.4081111 | 0.040185702 |
| DOGEUSDT | 5 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -4.1639739 | 0.039965209 |
| DOGEUSDT | 5 | garch | 10 | 0.038108683 | 0.0023618393 | 0.0026569966 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.3262971 | 0.043351025 |
| DOGEUSDT | 5 | hmm | 10 | 0.037203816 | 0.0020820831 | 0.0029806575 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.2907545 | 0.042167555 |
| DOGEUSDT | 5 | toto | 10 | 0.035097336 | 0.0016646781 | 0.0034097279 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.5084966 | 0.040113087 |
| DOGEUSDT | 20 | chronos2 | 10 | 0.093861569 | 0.0041282814 | 0.0064884027 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.3508492 | 0.10691727 |
| DOGEUSDT | 20 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -1.6411707 | 0.10106661 |
| DOGEUSDT | 20 | garch | 10 | 0.10085617 | 0.004671738 | 0.0055556172 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.2954515 | 0.11565452 |
| DOGEUSDT | 20 | hmm | 10 | 0.10144094 | 0.0038758623 | 0.0065579179 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.3106762 | 0.11601045 |
| DOGEUSDT | 20 | toto | 10 | 0.10974898 | 0.0030518025 | 0.0080110994 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.0723467 | 0.12586947 |
| ETHUSDT | 1 | chronos2 | 11 | 0.014184833 | 0.00082059513 | 0.0011209141 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.1249909 | 0.016156044 |
| ETHUSDT | 1 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -6.240059 | 0.017368937 |
| ETHUSDT | 1 | garch | 11 | 0.014999794 | 0.00085679411 | 0.0012178731 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.0460033 | 0.017119246 |
| ETHUSDT | 1 | hmm | 11 | 0.015254554 | 0.00068669261 | 0.0010580768 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.199345 | 0.017311619 |
| ETHUSDT | 1 | toto | 11 | 0.014439202 | 0.00073041885 | 0.0010238871 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.0226548 | 0.016436493 |
| ETHUSDT | 5 | chronos2 | 11 | 0.026049132 | 0.0017513873 | 0.0018647121 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -4.6443002 | 0.029544334 |
| ETHUSDT | 5 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -4.7958381 | 0.02861771 |
| ETHUSDT | 5 | garch | 11 | 0.0274603 | 0.00229836 | 0.0025115802 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -4.6125142 | 0.030951139 |
| ETHUSDT | 5 | hmm | 11 | 0.026354078 | 0.0019277965 | 0.0019275829 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -4.7317627 | 0.029883389 |
| ETHUSDT | 5 | toto | 11 | 0.027373842 | 0.0020512238 | 0.0020048149 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -4.6558726 | 0.03122609 |
| ETHUSDT | 20 | chronos2 | 11 | 0.084345088 | 0.0070614594 | 0.0046229049 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -2.7953833 | 0.095589087 |
| ETHUSDT | 20 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -2.6189412 | 0.098949851 |
| ETHUSDT | 20 | garch | 11 | 0.083909064 | 0.0042198205 | 0.0052287526 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -2.7808261 | 0.095304869 |
| ETHUSDT | 20 | hmm | 11 | 0.084190843 | 0.018021578 | 0.0041618997 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -2.7761885 | 0.093807597 |
| ETHUSDT | 20 | toto | 11 | 0.09447947 | 0.014953175 | 0.0049597285 | 0.090909091 | 0 | 11 | 1 | 0 | 0.099761448 | 0.63819744 | 0.63700412 | — | -2.6393553 | 0.10608592 |
| LINKUSDT | 1 | chronos2 | 13 | 0.01485665 | 0.0010369099 | 0.0013167674 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.0292844 | 0.016783026 |
| LINKUSDT | 1 | fincast | 13 | — | — | — | — | — | — | — | — | — | — | — | — | -6.0842321 | 0.021292896 |
| LINKUSDT | 1 | garch | 13 | 0.014187096 | 0.00094930728 | 0.0011101385 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.2171791 | 0.016082639 |
| LINKUSDT | 1 | hmm | 13 | 0.014501033 | 0.00081867435 | 0.0012363905 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.2075463 | 0.016475584 |
| LINKUSDT | 1 | toto | 13 | 0.013816148 | 0.00091020218 | 0.0012203302 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -6.2681871 | 0.015580344 |
| LINKUSDT | 5 | chronos2 | 13 | 0.049980589 | 0.0022095035 | 0.010011162 | 0 | 0.076923077 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -3.9750075 | 0.056009819 |
| LINKUSDT | 5 | fincast | 13 | — | — | — | — | — | — | — | — | — | — | — | — | -4.0509779 | 0.050663091 |
| LINKUSDT | 5 | garch | 13 | 0.050528031 | 0.0023942564 | 0.0068542134 | 0 | 0.076923077 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -4.0443749 | 0.057001645 |
| LINKUSDT | 5 | hmm | 13 | 0.050309334 | 0.0021990333 | 0.010905617 | 0 | 0.076923077 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -3.995799 | 0.056192069 |
| LINKUSDT | 5 | toto | 13 | 0.046620633 | 0.0021852352 | 0.0080414244 | 0 | 0.076923077 | 13 | 0 | 1 | 0.60922246 | 0.12128681 | — | 0.66960079 | -4.1442653 | 0.052342393 |
| LINKUSDT | 20 | chronos2 | 13 | 0.1013679 | 0.0045070436 | 0.0051928168 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -2.5020575 | 0.11602227 |
| LINKUSDT | 20 | fincast | 13 | — | — | — | — | — | — | — | — | — | — | — | — | -2.3885423 | 0.11927023 |
| LINKUSDT | 20 | garch | 13 | 0.10571026 | 0.0044570012 | 0.0050020103 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -2.4116105 | 0.1212381 |
| LINKUSDT | 20 | hmm | 13 | 0.10490821 | 0.0039322289 | 0.0052227124 | 0 | 0 | 13 | 0 | 0 | 0.60922246 | 0.60922246 | — | — | -2.4419455 | 0.12016268 |
| LINKUSDT | 20 | toto | 13 | 0.099531949 | 0.008285089 | 0.0061833195 | 0.076923077 | 0 | 13 | 1 | 0 | 0.12128681 | 0.60922246 | 0.66960079 | — | -2.5111093 | 0.11271694 |
| LTCUSDT | 1 | chronos2 | 10 | 0.0124978 | 0.00090474809 | 0.001206889 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.4949665 | 0.014142942 |
| LTCUSDT | 1 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -6.2494502 | 0.013394443 |
| LTCUSDT | 1 | garch | 10 | 0.012439908 | 0.00078568779 | 0.0011007355 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.6220475 | 0.014115722 |
| LTCUSDT | 1 | hmm | 10 | 0.011995144 | 0.00086594298 | 0.00097141574 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.7421677 | 0.013546918 |
| LTCUSDT | 1 | toto | 10 | 0.012193181 | 0.00066244917 | 0.00091040895 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.6546843 | 0.013917969 |
| LTCUSDT | 5 | chronos2 | 10 | 0.033905533 | 0.0015806965 | 0.0030753728 | 0 | 0.1 | 10 | 0 | 1 | 0.65390948 | 0.08915378 | — | — | -4.5134097 | 0.038539164 |
| LTCUSDT | 5 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -4.5433248 | 0.037513263 |
| LTCUSDT | 5 | garch | 10 | 0.036555117 | 0.0019129074 | 0.002178956 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.5372929 | 0.041824968 |
| LTCUSDT | 5 | hmm | 10 | 0.034935079 | 0.0020362387 | 0.0020309647 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.5951278 | 0.039935096 |
| LTCUSDT | 5 | toto | 10 | 0.036016642 | 0.0013805501 | 0.0019267947 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.5840157 | 0.041109569 |
| LTCUSDT | 20 | chronos2 | 10 | 0.098223162 | 0.0030205533 | 0.0039467562 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.2690299 | 0.1117653 |
| LTCUSDT | 20 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -1.4630131 | 0.10285667 |
| LTCUSDT | 20 | garch | 10 | 0.097130692 | 0.0041702487 | 0.0046405149 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.3772954 | 0.11141071 |
| LTCUSDT | 20 | hmm | 10 | 0.095574107 | 0.0040481626 | 0.0041748053 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -2.3474926 | 0.10956204 |
| LTCUSDT | 20 | toto | 10 | 0.11102944 | 0.0093753995 | 0.0039553762 | 0.2 | 0 | 10 | 2 | 0 | 0.0034110252 | 0.65390948 | 0.28168604 | — | -1.7753545 | 0.12537197 |
| SOLUSDT | 1 | chronos2 | 10 | 0.016082871 | 0.000950528 | 0.0012292091 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -5.9514457 | 0.018313133 |
| SOLUSDT | 1 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -5.133575 | 0.026033043 |
| SOLUSDT | 1 | garch | 10 | 0.014888539 | 0.00082329682 | 0.0011824873 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.1545426 | 0.01692731 |
| SOLUSDT | 1 | hmm | 10 | 0.014584407 | 0.00074800772 | 0.0011489791 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.1482396 | 0.016572274 |
| SOLUSDT | 1 | toto | 10 | 0.014914868 | 0.00093074517 | 0.00117239 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -6.094923 | 0.016971145 |
| SOLUSDT | 5 | chronos2 | 10 | 0.049658373 | 0.0020402539 | 0.0030935007 | 0 | 0.1 | 10 | 0 | 1 | 0.65390948 | 0.08915378 | — | — | -4.1411783 | 0.056310046 |
| SOLUSDT | 5 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -3.587134 | 0.052453211 |
| SOLUSDT | 5 | garch | 10 | 0.045990989 | 0.002096663 | 0.0024648418 | 0 | 0 | 10 | 0 | 0 | 0.65390948 | 0.65390948 | — | — | -4.1601815 | 0.052479115 |
| SOLUSDT | 5 | hmm | 10 | 0.045055758 | 0.0037982209 | 0.0025877885 | 0.1 | 0 | 10 | 1 | 0 | 0.08915378 | 0.65390948 | 1 | — | -4.2294779 | 0.051194882 |
| SOLUSDT | 5 | toto | 10 | 0.045955937 | 0.0032294023 | 0.0020021034 | 0.1 | 0 | 10 | 1 | 0 | 0.08915378 | 0.65390948 | 1 | — | -4.289635 | 0.05261206 |
| SOLUSDT | 20 | chronos2 | 10 | 0.10944318 | 0.005329567 | 0.0046619066 | 0.1 | 0 | 10 | 1 | 0 | 0.08915378 | 0.65390948 | 0.61661415 | — | -2.5669581 | 0.12483178 |
| SOLUSDT | 20 | fincast | 10 | — | — | — | — | — | — | — | — | — | — | — | — | -2.2066482 | 0.11993755 |
| SOLUSDT | 20 | garch | 10 | 0.1053765 | 0.0099540358 | 0.0051451181 | 0.1 | 0 | 10 | 1 | 0 | 0.08915378 | 0.65390948 | 0.61661415 | — | -2.5224379 | 0.11932901 |
| SOLUSDT | 20 | hmm | 10 | 0.10533299 | 0.010102752 | 0.0055932408 | 0.1 | 0 | 10 | 1 | 0 | 0.08915378 | 0.65390948 | 0.61661415 | — | -2.5273479 | 0.11925545 |
| SOLUSDT | 20 | toto | 10 | 0.1127732 | 0.017523555 | 0.0042835682 | 0.1 | 0 | 10 | 1 | 0 | 0.08915378 | 0.65390948 | 0.61661415 | — | -2.5863357 | 0.12673972 |
| TRXUSDT | 1 | chronos2 | 1 | 0.0093660269 | 0.00072385089 | 0.00047666176 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.8223246 | 0.010522304 |
| TRXUSDT | 1 | fincast | 1 | — | — | — | — | — | — | — | — | — | — | — | — | -5.5306074 | 0.033773607 |
| TRXUSDT | 1 | garch | 1 | 0.011203263 | 0.00072554748 | 0.00037991613 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.7466862 | 0.012850429 |
| TRXUSDT | 1 | hmm | 1 | 0.010172082 | 0.00078224062 | 0.00034350532 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.7340604 | 0.011658459 |
| TRXUSDT | 1 | toto | 1 | 0.012889855 | 0.00048476742 | 0.00024548795 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | 9.5543166 | 0.014504184 |
| TRXUSDT | 5 | chronos2 | 1 | 0.0072000486 | 0.000944708 | 0.00094355404 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.2654082 | 0.0079412289 |
| TRXUSDT | 5 | fincast | 1 | — | — | — | — | — | — | — | — | — | — | — | — | -4.535198 | 0.039260408 |
| TRXUSDT | 5 | garch | 1 | 0.0081969107 | 0.001109587 | 0.0011172721 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.1648299 | 0.0089974916 |
| TRXUSDT | 5 | hmm | 1 | 0.0082754278 | 0.0014224125 | 0.0012315522 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.0868999 | 0.0090621391 |
| TRXUSDT | 5 | toto | 1 | 0.0024985761 | 0.00052535004 | 0.00079578452 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -6.3028525 | 0.0027033105 |
| TRXUSDT | 20 | chronos2 | 1 | 0.017757436 | 0.0021580686 | 0.0018837766 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -4.822359 | 0.019691947 |
| TRXUSDT | 20 | fincast | 1 | — | — | — | — | — | — | — | — | — | — | — | — | -3.0675216 | 0.06578491 |
| TRXUSDT | 20 | garch | 1 | 0.020245729 | 0.0023425502 | 0.0021592155 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -4.5676064 | 0.02215506 |
| TRXUSDT | 20 | hmm | 1 | 0.020619025 | 0.0030108534 | 0.0046426323 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -4.4444866 | 0.022313135 |
| TRXUSDT | 20 | toto | 1 | 0.014985271 | 0.001495294 | 0.0029990614 | 0 | 0 | 1 | 0 | 0 | 0.88725628 | 0.88725628 | — | — | -4.8965929 | 0.016333781 |
| XRPUSDT | 1 | chronos2 | 11 | 0.015765437 | 0.00081937783 | 0.0013801348 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.4065586 | 0.01796113 |
| XRPUSDT | 1 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -5.8349189 | 0.01913222 |
| XRPUSDT | 1 | garch | 11 | 0.013775205 | 0.00091051707 | 0.0011308077 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.3459715 | 0.015596248 |
| XRPUSDT | 1 | hmm | 11 | 0.013810284 | 0.00088350361 | 0.0012566848 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.3111835 | 0.015591348 |
| XRPUSDT | 1 | toto | 11 | 0.013159279 | 0.00087464928 | 0.00097181636 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -6.4003658 | 0.014991318 |
| XRPUSDT | 5 | chronos2 | 11 | 0.056216032 | 0.002098324 | 0.01087581 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -0.86923609 | 0.062350336 |
| XRPUSDT | 5 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -3.5873375 | 0.065043454 |
| XRPUSDT | 5 | garch | 11 | 0.056251642 | 0.0027346943 | 0.021549532 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -3.1024769 | 0.061059367 |
| XRPUSDT | 5 | hmm | 11 | 0.055089417 | 0.002437279 | 0.017521619 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -3.5258931 | 0.060081792 |
| XRPUSDT | 5 | toto | 11 | 0.056413437 | 0.0029528855 | 0.02545594 | 0 | 0.090909091 | 11 | 0 | 1 | 0.63819744 | 0.099761448 | — | 0.63700412 | -2.5444147 | 0.060814496 |
| XRPUSDT | 20 | chronos2 | 11 | 0.093235984 | 0.0046944868 | 0.0057635841 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -2.5852519 | 0.10659091 |
| XRPUSDT | 20 | fincast | 11 | — | — | — | — | — | — | — | — | — | — | — | — | -2.483211 | 0.10507757 |
| XRPUSDT | 20 | garch | 11 | 0.092278038 | 0.0053754616 | 0.0051090931 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -2.604913 | 0.10513121 |
| XRPUSDT | 20 | hmm | 11 | 0.093108952 | 0.0037879568 | 0.0061252058 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -2.5763345 | 0.10636905 |
| XRPUSDT | 20 | toto | 11 | 0.099112274 | 0.0048618745 | 0.0060847599 | 0 | 0 | 11 | 0 | 0 | 0.63819744 | 0.63819744 | — | — | -2.2437708 | 0.11248163 |

| corrida | modelos | cada | solo limpia | CPU s/origen | pared inferencia / total s | fallos | SHA-256 predicciones |
|---|---|---|---|---|---|---|---|
| `E:\quantdesk-lab\runs\TS-00-BENCH\binance_c20261101` | hmm,garch,chronos2 | 1 | False | chronos2: 0.497; garch: 0.06702; hmm: 0.6012 | 4769.12 / no medida | {'chronos2': 0, 'garch': 0, 'hmm': 0} | `22e2e2531d30d35733e22372db65bfef1c3b1d1b096ff1934d5678a7f9f8cfb1` |
| `E:\quantdesk-lab\runs\TS-00-BENCH\toto_binance_c20261101` | toto | 10 | False | toto: 26.77 | 13408.88 / no medida | {'toto': 0} | `4c35cc697b24bb132dff347ba682db8d5775fd0f6c027c6beb1af164ce0d4560` |
| `E:\quantdesk-lab\runs\TS-00-BENCH-FINCAST\fincast_binance` | fincast | 10 | True | fincast: 1.911 | 142.48 / 194.2701355999743 | {'fincast': 20} | `1a7e2f8a4591c05109de841bab09b38cf6294e481958d0afc9792839145e93ce` |
Fallo declarado: ADAUSDT 1768780800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: ADAUSDT 1773964800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: ADAUSDT 1776556800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: ADAUSDT 1779148800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: ADAUSDT 1781740800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: BTCUSDT 1763596800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: BTCUSDT 1779148800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: BTCUSDT 1786924800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: DOGEUSDT 1781740800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
Fallo declarado: DOGEUSDT 1786924800000 fincast: RuntimeError: ValueError: deciles nativos no monotonos.
