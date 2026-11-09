# TI-13-PUB: informe del filtro de fugas D-11

- `--corte`: **2016-10-01** (UTC, 00:00). Lo anterior va a `tronco`, lo posterior a `adaptadores`. Provisional (decision de la raiz): se reaplica sobre lo crudo con `procesar --corte AAAA-MM-DD` sin volver a descargar.
- Sal de la particion: `TI-13-PUB/SPRINT-01/v1`; fraccion de validacion: 10% de las series (por hash SHA-256 del id).
- Regla D-11 (PLAN_TSFM_FINANZAS, 2026-11-07): tronco sin datos reales con fecha; lo real solo en adaptadores.

## Criterio de financiera y de fechas fiables

Financiera: serie de precios, rendimientos, tipos de interes o de cambio, indices, credito o macroeconomia financiera, y todo subconjunto marcado Finance, Econ, Macro o banca en sus metadatos o documentacion (en LOTSA, el dominio 'Econ/Fin' de la Tabla 14 del paper). Los mixtos (M4, M3, M1) cuentan como financieros enteros salvo que traigan el dominio por serie. Una serie financiera con fechas reales fiables se corta en --corte (antes: tronco; desde el corte: adaptadores); sin fechas reales verificables se excluye entera del tronco. Fechas reales solo si la documentacion del origen describe una base de datos o fuente fechada Y las marcas de los datos pasan las comprobaciones de plausibilidad; ninguna documentacion consultada lo afirma para las competiciones M1, M3, M4, NN5, CIF 2016 y Tourism, ni para exchange_rate (el origen no publica fechas).

## Cifras por dataset

| dataset | clase | series | financieras | excl. sin fechas verificables | excl. fechas imposibles | vacias | cortadas | solo antes | solo despues | no financieras intactas | puntos tronco | puntos adaptadores | puntos excluidos | quitados del tronco por el corte | NaN |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| binance__klines_1d | real | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30,406 | 0 | 0 | 0 |
| binance__klines_1h | real | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 389,813 | 0 | 0 | 0 |
| chronos__exchange_rate | fin | 8 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 60,704 | 0 | 0 |
| chronos__monash_cif_2016 | fin | 72 | 72 | 72 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7,108 | 0 | 0 |
| chronos__monash_electricity_hourly | no_fin | 321 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 321 | 8,443,584 | 0 | 0 | 0 | 0 |
| chronos__monash_fred_md | fin | 107 | 107 | 0 | 0 | 0 | 107 | 0 | 0 | 0 | 74,151 | 3,745 | 0 | 3,745 | 0 |
| chronos__monash_hospital | no_fin | 767 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 767 | 64,428 | 0 | 0 | 0 | 0 |
| chronos__monash_nn5_weekly | fin | 111 | 111 | 111 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12,543 | 0 | 0 |
| chronos__monash_tourism_monthly | fin | 366 | 366 | 366 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 109,280 | 0 | 0 |
| chronos__monash_traffic | no_fin | 862 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 862 | 15,122,928 | 0 | 0 | 0 | 0 |
| chronos__monash_weather | no_fin | 3,010 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3,010 | 43,032,000 | 0 | 0 | 0 | 0 |
| chronos__taxi_30min | no_fin | 2,428 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2,428 | 3,589,798 | 0 | 0 | 0 | 0 |
| lotsa__australian_electricity_demand | no_fin | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 1,153,584 | 0 | 0 | 0 | 0 |
| lotsa__bitcoin_with_missing | fin | 18 | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0 | 50,904 | 31,014 | 0 | 31,014 | 8,072 |
| lotsa__car_parts_with_missing | no_fin | 2,674 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2,674 | 104,286 | 0 | 0 | 0 | 4,142 |
| lotsa__cif_2016_12 | fin | 57 | 57 | 57 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5,701 | 0 | 0 |
| lotsa__cif_2016_6 | fin | 15 | 15 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 633 | 0 | 0 |
| lotsa__covid_mobility | no_fin | 362 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 362 | 148,602 | 0 | 0 | 0 | 4,279 |
| lotsa__elecdemand | no_fin | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 17,520 | 0 | 0 | 0 | 0 |
| lotsa__fred_md | fin | 107 | 107 | 0 | 0 | 0 | 107 | 0 | 0 | 0 | 74,151 | 2,461 | 0 | 2,461 | 0 |
| lotsa__kaggle_web_traffic_weekly | no_fin | 145,063 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 145,063 | 16,537,182 | 0 | 0 | 0 | 0 |
| lotsa__m1_monthly | fin | 617 | 617 | 617 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 44,892 | 0 | 0 |
| lotsa__m4_daily | fin | 4,227 | 4,227 | 4,227 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9,964,658 | 0 | 0 |
| lotsa__m4_monthly | fin | 48,000 | 48,000 | 48,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10,382,411 | 0 | 0 |
| lotsa__monash_m3_monthly | fin | 1,428 | 1,428 | 1,428 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 141,858 | 0 | 0 |
| lotsa__nn5_daily_with_missing | fin | 111 | 111 | 111 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 81,585 | 0 | 1,673 |
| lotsa__nn5_weekly | fin | 111 | 111 | 111 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 11,655 | 0 | 0 |
| lotsa__oikolab_weather | no_fin | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 800,456 | 0 | 0 | 0 | 0 |
| lotsa__pedestrian_counts | no_fin | 66 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 66 | 3,130,762 | 0 | 0 | 0 | 0 |
| lotsa__saugeenday | no_fin | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 23,711 | 0 | 0 | 0 | 0 |
| lotsa__solar_power | no_fin | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 7,397,222 | 0 | 0 | 0 | 0 |
| lotsa__sunspot_with_missing | no_fin | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 73,894 | 0 | 0 | 0 | 3,240 |
| lotsa__temperature_rain_with_missing | no_fin | 32,072 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 32,072 | 22,290,040 | 0 | 0 | 0 | 598,369 |
| lotsa__tourism_monthly | fin | 366 | 366 | 366 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 100,496 | 0 | 0 |
| lotsa__traffic_weekly | no_fin | 862 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 862 | 82,752 | 0 | 0 | 0 | 0 |
| lotsa__wind_power | no_fin | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 7,397,147 | 0 | 0 | 0 | 0 |
| **total** | | **244,241** | **55,736** | **55,489** | **0** | **0** | **232** | **0** | **0** | **188,505** | **129,609,102** | **457,439** | **20,923,524** | **37,220** | **619,775** |

Filtro por dominio de cada serie: la unica config con dominio por serie (`autogluon/chronos_datasets` `m4_daily`/`m4_monthly`, columna `category`) esta excluida por licencia y no se descargo; el filtro serie a serie (`es_financiera` con `dominio_col`) solo se ejercita en el selftest. Los M4/M3/M1 de LOTSA no traen dominio por serie y cuentan como financieros enteros.

Notas: `solo antes` = financiera con fechas reales entera anterior al corte (pasa al tronco intacta); `solo despues` = entera posterior (va a adaptadores); `cortadas` = cruza el corte (prefijo al tronco, resto a adaptadores). En datasets `real` (cripto) todo va a adaptadores.

## Detalle de la deteccion por dataset

| dataset | dominio | clase | criterio de deteccion | fechas | evidencia de fechas | rango observado (UTC) |
|---|---|---|---|---|---|---|
| binance__klines_1d | Cripto (precios) | real | Datos reales con fecha: solo adaptadores. | reales | Marcas de apertura de vela publicadas por Binance. | 2017-08-17T00:00:00Z a 2026-11-07T00:00:00Z |
| binance__klines_1h | Cripto (precios) | real | Datos reales con fecha: solo adaptadores. | reales | Marcas de apertura de vela publicadas por Binance. | 2017-08-17T04:00:00Z a 2026-11-07T23:00:00Z |
| chronos__exchange_rate | Finance (tipos de cambio) | fin | Tipos de cambio diarios de 8 divisas: serie financiera. | no_verificables | El origen (laiguokun/multivariate-time-series-data) publica 7588 dias de 1990 a 2016 sin marcas de fecha; el corpus asigna un inicio. | 1990-01-01T00:00:00Z a 2019-01-30T00:00:00Z |
| chronos__monash_cif_2016 | Banking | fin | Banca (CIF 2016); 48 de las 72 series son artificiales segun Zenodo. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). 48 de 72 series son artificiales. | 1970-01-31T00:00:00Z a 1979-12-31T00:00:00Z |
| chronos__monash_electricity_hourly | Energy | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2012-01-01T01:00:00Z a 2015-01-01T00:00:00Z |
| chronos__monash_fred_md | Macro (FRED-MD) | fin | Indicadores macroeconomicos del Federal Reserve Bank: macroeconomia financiera. | reales | FRED-MD: base de datos fechada del Federal Reserve Bank de St. Louis; la ficha de Zenodo la cita como origen. | 1959-01-31T00:00:00Z a 2019-08-31T00:00:00Z |
| chronos__monash_hospital | Healthcare | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2000-01-01T00:00:00Z a 2006-12-01T00:00:00Z |
| chronos__monash_nn5_weekly | Banking (ATM) | fin | Dominio banca (retiradas de cajeros). | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1996-03-24T00:00:00Z a 1998-05-17T00:00:00Z |
| chronos__monash_tourism_monthly | Econ/Fin (LOTSA) | fin | Reclasificada a financiera (adicion conservadora): LOTSA la marca Econ/Fin en su Tabla 14. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1979-01-31T00:00:00Z a 2007-09-30T00:00:00Z |
| chronos__monash_traffic | Transport | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2015-01-01T00:00:00Z a 2016-12-31T23:00:00Z |
| chronos__monash_weather | Climate | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 1970-01-01T00:00:00Z a 2150-08-25T00:00:00Z |
| chronos__taxi_30min | Transport | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2015-01-01T00:00:00Z a 2016-01-31T14:00:00Z |
| lotsa__australian_electricity_demand | Energy | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2002-01-01T00:00:00Z a 2015-03-25T23:30:00Z |
| lotsa__bitcoin_with_missing | Econ/Fin | fin | Series asociadas al precio del bitcoin: Econ/Fin en LOTSA. | reales | bitinfocharts.com: graficos web fechados, segun la ficha de Zenodo. | 2009-01-03T00:00:00Z a 2021-06-19T00:00:00Z |
| lotsa__car_parts_with_missing | Sales | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 1998-01-01T00:00:00Z a 2001-03-01T00:00:00Z |
| lotsa__cif_2016_12 | Econ/Fin | fin | Banca (CIF 2016), horizonte 12. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). 48 de 72 series son artificiales. | 1970-01-01T00:00:00Z a 1978-12-01T00:00:00Z |
| lotsa__cif_2016_6 | Econ/Fin | fin | Banca (CIF 2016), horizonte 6. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). 48 de 72 series son artificiales. | 1970-01-01T00:00:00Z a 1975-09-01T00:00:00Z |
| lotsa__covid_mobility | Transport | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2020-02-15T00:00:00Z a 2021-04-02T00:00:00Z |
| lotsa__elecdemand | Energy | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2014-01-01T00:00:00Z a 2014-12-31T23:30:00Z |
| lotsa__fred_md | Econ/Fin | fin | Macro (FRED-MD): Econ/Fin en LOTSA. | reales | FRED-MD: base de datos fechada del Federal Reserve Bank de St. Louis; la ficha de Zenodo la cita como origen. | 1959-01-01T00:00:00Z a 2018-08-01T00:00:00Z |
| lotsa__kaggle_web_traffic_weekly | Web | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2015-07-05T00:00:00Z a 2017-09-03T00:00:00Z |
| lotsa__m1_monthly | Econ/Fin | fin | M1 mixto (macro/micro/industria/demografia) sin dominio por serie. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1900-01-01T00:00:00Z a 1989-07-01T00:00:00Z |
| lotsa__m4_daily | Econ/Fin | fin | M4 mixto sin dominio por serie en LOTSA. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1750-01-01T00:00:00Z a 1777-02-26T00:00:00Z |
| lotsa__m4_monthly | Econ/Fin | fin | M4 mixto sin dominio por serie en LOTSA. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1750-01-01T00:00:00Z a 1982-10-01T00:00:00Z |
| lotsa__monash_m3_monthly | Econ/Fin | fin | M3 mixto sin dominio por serie en LOTSA. | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1857-01-01T00:00:00Z a 2003-08-01T00:00:00Z |
| lotsa__nn5_daily_with_missing | Econ/Fin | fin | Dominio banca (retiradas de cajeros). | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1996-03-18T00:00:00Z a 1998-03-22T00:00:00Z |
| lotsa__nn5_weekly | Econ/Fin | fin | Dominio banca (retiradas de cajeros). | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1996-03-24T00:00:00Z a 1998-03-22T00:00:00Z |
| lotsa__oikolab_weather | Climate | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2010-01-01T00:00:00Z a 2021-06-01T00:00:00Z |
| lotsa__pedestrian_counts | Transport | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2009-05-01T00:00:00Z a 2020-04-29T23:00:00Z |
| lotsa__saugeenday | Nature | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 1915-01-01T00:00:00Z a 1979-12-01T00:00:00Z |
| lotsa__solar_power | Energy | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2019-08-01T00:00:03Z a 2020-07-08T11:08:07Z |
| lotsa__sunspot_with_missing | Nature | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 1818-01-08T00:00:00Z a 2020-05-01T00:00:00Z |
| lotsa__temperature_rain_with_missing | Climate | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2015-05-02T00:00:00Z a 2017-03-26T00:00:00Z |
| lotsa__tourism_monthly | Econ/Fin | fin | Econ/Fin en LOTSA (Tabla 14). | no_verificables | Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11). | 1979-01-01T00:00:00Z a 2005-09-01T00:00:00Z |
| lotsa__traffic_weekly | Transport | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2015-01-04T00:00:00Z a 2016-10-30T00:00:00Z |
| lotsa__wind_power | Energy | no_fin | No financiera (energia, transporte, clima, naturaleza, ventas, web o salud). | - | - | 2019-08-01T00:00:03Z a 2020-07-08T11:03:07Z |

## Datasets no procesados por licencia (no se descargaron)

- `chronos__m4_daily`: La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta); el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404): no verificable.
- `chronos__m4_monthly`: La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta); el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404): no verificable.
- `chronos__training_corpus_kernel_synth_1m`: La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta): no verificable.

## Validacion disjunta de entrenamiento

Particion determinista por `series_id` (`{dataset}/{id}`): SHA-256(sal + id) -> uniforme en [0,1); `val` si < 0.1. Las series que comparten contenido (hash SHA-256 de sus valores) forman un componente y van al mismo lado, de modo que ningun `series_id` ni contenido identico aparece a ambos lados, tampoco entre datasets. La comprobacion se hace sobre el plan y, de nuevo, releyendo los parquet escritos.

- Plan: 188,752 series con contenido, 188,803 contenidos distintos; contenidos en ambos lados: **0**.
- Parquet releidos (130,066,541 filas): 170,029 series en train y 18,723 en val; `series_id` en ambos lados: **0**; contenidos identicos en ambos lados: **0**.
- Componentes con duplicados de contenido: 93; mayor componente: 28 series.

| dataset | series tronco | series adaptadores | filas train | filas val | series val (tronco+adapt.) |
|---|---|---|---|---|---|
| binance__klines_1d | 0 | 10 | 30,406 | 0 | 0 |
| binance__klines_1h | 0 | 5 | 389,813 | 0 | 0 |
| chronos__exchange_rate | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_cif_2016 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_electricity_hourly | 321 | 0 | 7,444,032 | 999,552 | 38 |
| chronos__monash_fred_md | 107 | 107 | 65,520 | 12,376 | 34 |
| chronos__monash_hospital | 767 | 0 | 58,548 | 5,880 | 70 |
| chronos__monash_nn5_weekly | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_tourism_monthly | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_traffic | 862 | 0 | 13,561,512 | 1,561,416 | 89 |
| chronos__monash_weather | 3,010 | 0 | 38,330,442 | 4,701,558 | 312 |
| chronos__taxi_30min | 2,428 | 0 | 3,230,589 | 359,209 | 243 |
| lotsa__australian_electricity_demand | 5 | 0 | 921,648 | 231,936 | 1 |
| lotsa__bitcoin_with_missing | 18 | 18 | 63,714 | 18,204 | 8 |
| lotsa__car_parts_with_missing | 2,674 | 0 | 93,522 | 10,764 | 276 |
| lotsa__cif_2016_12 | 0 | 0 | 0 | 0 | 0 |
| lotsa__cif_2016_6 | 0 | 0 | 0 | 0 | 0 |
| lotsa__covid_mobility | 362 | 0 | 134,247 | 14,355 | 35 |
| lotsa__elecdemand | 1 | 0 | 17,520 | 0 | 0 |
| lotsa__fred_md | 107 | 107 | 65,156 | 11,456 | 32 |
| lotsa__kaggle_web_traffic_weekly | 145,063 | 0 | 14,911,200 | 1,625,982 | 14,263 |
| lotsa__m1_monthly | 0 | 0 | 0 | 0 | 0 |
| lotsa__m4_daily | 0 | 0 | 0 | 0 | 0 |
| lotsa__m4_monthly | 0 | 0 | 0 | 0 | 0 |
| lotsa__monash_m3_monthly | 0 | 0 | 0 | 0 | 0 |
| lotsa__nn5_daily_with_missing | 0 | 0 | 0 | 0 | 0 |
| lotsa__nn5_weekly | 0 | 0 | 0 | 0 | 0 |
| lotsa__oikolab_weather | 8 | 0 | 800,456 | 0 | 0 |
| lotsa__pedestrian_counts | 66 | 0 | 2,900,648 | 230,114 | 5 |
| lotsa__saugeenday | 1 | 0 | 23,711 | 0 | 0 |
| lotsa__solar_power | 1 | 0 | 7,397,222 | 0 | 0 |
| lotsa__sunspot_with_missing | 1 | 0 | 73,894 | 0 | 0 |
| lotsa__temperature_rain_with_missing | 32,072 | 0 | 20,020,170 | 2,269,870 | 3,266 |
| lotsa__tourism_monthly | 0 | 0 | 0 | 0 | 0 |
| lotsa__traffic_weekly | 862 | 0 | 74,304 | 8,448 | 88 |
| lotsa__wind_power | 1 | 0 | 7,397,147 | 0 | 0 |

Datasets con series pero sin ninguna en val (la particion es por serie, como pide la ficha, y los datasets de pocas series pueden quedarse sin lado val): `binance__klines_1d`, `binance__klines_1h`, `lotsa__elecdemand`, `lotsa__oikolab_weather`, `lotsa__saugeenday`, `lotsa__solar_power`, `lotsa__sunspot_with_missing`, `lotsa__wind_power`.

## Lista completa de series afectadas

CSV fuera de Git (series excluidas, cortadas o movidas enteras a adaptadores): `E:/quantdesk-lab/datasets/TI-13-PUB/_informes/filtro_ids.csv`; 55,721 filas, 5.0 MB, SHA-256 `57480ae12c3591f45d5cd8dd3b1e9b2f0b552b22476f9fc5365f01fc84d16072`. Columnas: dataset, series_id, accion, motivo, puntos, puntos_tronco, puntos_adaptadores.
