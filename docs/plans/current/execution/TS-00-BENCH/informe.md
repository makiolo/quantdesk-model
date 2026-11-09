# TS-00-BENCH: banco walk-forward (HMM del motor, GARCH(1,1), Chronos-2 zero-shot; Toto pendiente)

- Generado por `scripts/banco_walkforward.py --informe` el 2026-11-09T05:21:39Z a partir de las salidas de las corridas (`meta.json`, `metricas.csv`, `predicciones.parquet` en `E:/quantdesk-lab/runs/TS-00-BENCH/`). Comando: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --informe E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101 E:/quantdesk-lab/runs/TS-00-BENCH/binance_c20261101 --repeticion E:/quantdesk-lab/runs/TS-00-BENCH/repeticion --pilotos E:/quantdesk-lab/runs/TS-00-BENCH/piloto_lago E:/quantdesk-lab/runs/TS-00-BENCH/piloto_binance --destino docs/plans/current/execution/TS-00-BENCH`.
- Selftest: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --selftest` (sin red: el selftest bloquea los sockets; sin datos reales; Chronos-2 sustituido por un modelo trivial con la misma interfaz).
- Motor: **quantdesk 69fdb39d** (commit `69fdb39d0b67969dbdafa77f5da656511342f175`). Semilla: **20261101**. Solo CPU.
- **Tabla de cabecera: `lago_cierre_c20261101`** (FX diario del lago; decision del usuario del 2026-11-09). Su disponibilidad es un **proxy** (`available_at_ms` nulo, `default_lag_ms` = 0: valores que qn recibio despues del corte) y cada tabla y cifra suya lleva la etiqueta «proxy». `binance_c20261101` es la segunda tabla.
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
| Toto (pesos `Datadog/Toto-Open-Base-1.0`) | Apache-2.0 | https://huggingface.co/Datadog/Toto-Open-Base-1.0 | permite uso de investigacion interno; NO usado (paquete no instalado) |
| toto-ts 0.2.0 (codigo) | Apache-2.0 | https://pypi.org/project/toto-ts/ | no instalado |
| arch 8.0.0 (GARCH) | NCSA | https://github.com/bashtage/arch | sin pesos |
| HMM del motor (quantdesk 69fdb39d) | propio | S:/Projects/quantdesk | sin pesos |

Datos: Binance Vision CC BY-NC-SA 4.0 (solo uso personal no productivo, ver TI-02-DATA); lago de qn, propio. Licencias de pesos verificadas en las tarjetas de Hugging Face el 2026-11-09.

## Toto

**Pendiente de decision (GAP-04).** No esta en el `.venv` y no se ha instalado nada.

- Paquete: `toto-ts` 0.2.0 (PyPI, 2026-02-26, Apache-2.0); pesos `Datadog/Toto-Open-Base-1.0` (Apache-2.0,
  ~151 M parametros, `model.safetensors` de 605 MB). Licencias verificadas en
  https://pypi.org/project/toto-ts/ y https://huggingface.co/Datadog/Toto-Open-Base-1.0 el 2026-11-09.
- Conflicto: `toto-ts` 0.2.0 fija versiones exactas incompatibles con el `.venv` del laboratorio (`torch==2.7.0`
  frente a 2.15.0+cpu, `numpy==1.26.4` frente a 2.5.4, `pandas==2.2.3` frente a 3.1.1, `transformers==4.52.1`
  frente a 5.22.2, `einops==0.7.0`, `gluonts[torch]==0.16.2`, mas herramientas de desarrollo como dependencias
  de ejecucion: pytest, mypy, black, jupyter, tensorboard, lightning, boto3). Instalarlo en el `.venv` lo
  degradaria y romperia Chronos-2 y la rueda del motor.
- Orden propuesta (un venv aparte bajo E:, sin tocar el del laboratorio; CPU):
  `D:/miniconda312/python.exe -m venv E:/quantdesk-lab/venvs/toto` y despues
  `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.0`
  seguido de `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install toto-ts==0.2.0 pyarrow`
  (con `PIP_CACHE_DIR`, `HF_HOME` y `TMPDIR` del laboratorio). El banco llamaria a ese interprete en un
  subproceso con el mismo contrato de cuantiles (contexto en log-precio, 256 muestras, cuantiles empiricos).
- CPU: la tarjeta solo documenta CUDA (recomienda xFormers y flash-attention, opcionales). Por tamano (~151 M,
  como Chronos-2 ~120 M) cabe en CPU y 32 GB de RAM; el coste esperado es mayor que el de Chronos-2 porque
  muestrea (256 caminos por origen frente a una pasada de cuantiles). Sin medir.
- Sin instalar: el repositorio de pesos no trae codigo de modelado (solo `config.json` y `model.safetensors`); el
  modelo esta en el paquete `toto` (`toto.model.toto.Toto`, `toto.inference.forecaster.TotoForecaster`). No hay
  forma de ejecutarlo solo con `transformers`/`torch` sin copiar ese codigo, asi que no se ha intentado.

## Reproducibilidad

- Versiones: python 3.12.3, numpy 2.5.4, scipy 1.18.1, pandas 3.1.1, pyarrow 26.0.1, arch 8.0.0, torch 2.15.0+cpu, transformers 5.22.2, chronos-forecasting 2.3.2, huggingface_hub 2.4.0; motor quantdesk 69fdb39d (rueda sha256 `sha256=28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd`). Plataforma: Windows-10-10.0.19045-SP0.
- Pesos de Chronos-2: `amazon/chronos-2` revision `29ec3766d36d6f73f0696f85560a422f50e8498c`: `config.json` sha256 `ef1143bfdc9c0376d9a056eefca46cb4b1ec3d0ffacd541ff56feb40fb708031`, `model.safetensors` sha256 `ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42`. HMM y GARCH no tienen pesos (se calibran en cada origen).
- Semilla de cada prevision: los 31 bits bajos de sha256("semilla|activo|origen_ms|modelo"); el camino j del HMM usa semilla x 4096 + j; GARCH usa `numpy.random.default_rng(semilla)`. Hilos: BLAS/OpenMP 1, torch 2 (`--hilos`).

| dataset | comando exacto | pared (s) | CPU hmm (s, s/origen) | CPU garch | CPU chronos2 | carga de modelos (s CPU) | fallos hmm/garch/chronos2 | HMM sin converger | sha256 predicciones |
|---|---|---|---|---|---|---|---|---|---|
| lago_cierre_c20261101 (proxy) | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --out E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101` | 2457 | 1351 (0.195) | 573 (0.083) | 1637 (0.237) | 10 | 0/0/0 | 1892 de 6916 | `f130e892181f932f…` |
| binance_c20261101 | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --out E:/quantdesk-lab/runs/TS-00-BENCH/binance_c20261101` | 4769 | 2158 (0.601) | 241 (0.067) | 1784 (0.497) | 15 | 0/0/0 | 987 de 3590 | `22e2e2531d30d357…` |

HMM «sin converger»: Baum-Welch agota las 200 iteraciones por defecto sin bajar de `tol` = 1e-8 en la log-verosimilitud; se usa el ajuste igualmente (es el comportamiento del motor con sus opciones por defecto).

### Repeticion de un subconjunto (aceptacion 3)

- Comando: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --activos EURUSD,USDJPY --max-origenes 12 --out E:/quantdesk-lab/runs/TS-00-BENCH/repeticion --comparar E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101` (10 s de pared mas la carga).
- Resultado: 216 filas (activo x origen x modelo x h) comparadas con la corrida completa `E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101`: 0 sin pareja; predicciones identicas bit a bit: **True** (dif. maxima 0.0); metricas del subconjunto recalculadas desde la corrida completa identicas: **True** (dif. maxima 0.0). El script sale con codigo 1 si no coinciden.

Metricas del subconjunto (lago_cierre_c20261101 (proxy)), las mismas que da la corrida completa sobre esos origenes:

| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | QLIKE |
|---|---|---|---|---|---|---|---|
| EURUSD | 1 | hmm | 12 | 0.00149651604 | 0.0001160303225 | 0.0001566170356 | -10.5243696 |
| EURUSD | 1 | garch | 12 | 0.001480094306 | 0.0001085829101 | 0.0001298938689 | -10.60146655 |
| EURUSD | 1 | chronos2 | 12 | 0.001777402322 | 0.000159022946 | 0.0001630543159 | -10.5875084 |
| EURUSD | 5 | hmm | 12 | 0.00450749457 | 0.0002527015385 | 0.0003486292365 | -8.738470275 |
| EURUSD | 5 | garch | 12 | 0.004244217916 | 0.0002428672434 | 0.0003015389661 | -8.826808762 |
| EURUSD | 5 | chronos2 | 12 | 0.004043802317 | 0.0002640876602 | 0.0003030387753 | -8.992219512 |
| EURUSD | 20 | hmm | 12 | 0.006982640145 | 0.0004858987172 | 0.0006658221839 | -7.298241984 |
| EURUSD | 20 | garch | 12 | 0.00612730559 | 0.0005104013865 | 0.0005846816683 | -7.375758854 |
| EURUSD | 20 | chronos2 | 12 | 0.005581446424 | 0.0006855379528 | 0.0006699049052 | -7.493406084 |
| USDJPY | 1 | hmm | 12 | 0.002633696579 | 0.0001560051636 | 0.0001259338121 | -9.6751223 |
| USDJPY | 1 | garch | 12 | 0.002645422724 | 0.0001563482268 | 0.0001240622661 | -9.664827884 |
| USDJPY | 1 | chronos2 | 12 | 0.002680101114 | 0.0002135026064 | 0.0001372297996 | -9.628607085 |
| USDJPY | 5 | hmm | 12 | 0.004468782106 | 0.0003865936216 | 0.000282734383 | -8.024170114 |
| USDJPY | 5 | garch | 12 | 0.004463988475 | 0.000380270763 | 0.0002801771924 | -8.008724538 |
| USDJPY | 5 | chronos2 | 12 | 0.004432048312 | 0.0003776014683 | 0.0002564556561 | -8.037455099 |
| USDJPY | 20 | hmm | 12 | 0.01309266059 | 0.0009043720461 | 0.0004457244023 | -6.687242791 |
| USDJPY | 20 | garch | 12 | 0.0129884097 | 0.0008789162486 | 0.0004646229996 | -6.71091502 |
| USDJPY | 20 | chronos2 | 12 | 0.01288955544 | 0.00088073684 | 0.0003970635611 | -6.862335326 |

## Presupuesto de CPU (medido antes de las corridas completas)

| piloto | comando | activos x origenes | CPU s/origen hmm | garch | chronos2 |
|---|---|---|---|---|---|
| lago_cierre_c20261101 (proxy) | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --activos EURUSD,USDJPY --max-origenes 10 --out E:/quantdesk-lab/runs/TS-00-BENCH/piloto_lago` | 20 | 0.271 | 0.059 | 0.236 |
| binance_c20261101 | `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --activos BTCUSDT,SOLUSDT --max-origenes 10 --out E:/quantdesk-lab/runs/TS-00-BENCH/piloto_binance` | 20 | 0.666 | 0.059 | 0.411 |

Con esas medidas (en una maquina compartida, i7-4790K de 4 nucleos): FX con todos los dias habiles (paso 1) cuesta ~0,57 s por par activo-origen, unas 6 900 x 0,57 s ~ 66 min de CPU: cabe en 2 h sin recortar. Binance con origenes diarios desde 2023-11 serian ~10 750 pares x ~1,14 s ~ 3,4 h: se recorta a un origen cada 3 dias (~3 590 pares, ~68 min), con los 10 activos y la ventana de 1 000 barras. Una sola corrida pesada a la vez. El CPU y la pared reales de cada corrida estan en la tabla de reproducibilidad (el CPU de Chronos-2 suma sus 2 hilos de torch).

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
