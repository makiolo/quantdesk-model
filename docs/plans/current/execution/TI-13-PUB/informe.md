# TI-13-PUB: informe de ingesta publica

- Generado: 2026-11-08T11:53:59Z (UTC). `--corte`: **2016-10-01**. Sal/semilla de la particion: `TI-13-PUB/SPRINT-01/v1` (val 10%).
- Versiones: python 3.12.3, pyarrow 26.0.1, pandas 3.1.1, numpy 2.5.4, huggingface-hub 2.4.0. Motor del entorno: quantdesk 69fdb39d (commit `69fdb39d0b67969dbdafa77f5da656511342f175`; no se usa en esta ingesta).
- Revisiones fijadas del Hub: chronos_datasets `eeecad0b82a8c237e212ce6f8d1abecb513e2cec`, lotsa_data `8191fd29eb5cf906ec55effca44d8059888b615d`.
- Formato procesado (provisional hasta TI-03-FMT): parquet zstd, columnas `series_id` (str, `dataset/id`), `ts` (timestamp ms UTC), `value` (float64; en cripto = cierre) y, en cripto, `open, high, low, close, volume, quote_volume, n_trades`. Un fichero por `<parte>.<split>.parquet` (parte = `tronco` o `adaptadores`; split = `train` o `val`) y un `manifest.json` por dataset.

## Comandos para reproducir

```
.venv/Scripts/python -X utf8 scripts/ingesta_publica.py licencias
.venv/Scripts/python -X utf8 scripts/ingesta_publica.py descargar
.venv/Scripts/python -X utf8 scripts/ingesta_publica.py procesar --corte 2016-10-01
.venv/Scripts/python -X utf8 scripts/ingesta_publica.py informe
.venv/Scripts/python -X utf8 scripts/ingesta_publica.py --verificar
```

Los datasets y manifiestos estan en `E:/quantdesk-lab/datasets/TI-13-PUB/<dataset>/`; lo crudo, en `E:/quantdesk-lab/data/public/`.

## Espacio

- Usado por TI-13-PUB (bytes de los manifiestos): **1.005 GB** de 100 GB (crudo 0.573 GB + procesado 0.432 GB); cache de huggingface_hub (scan_cache_dir): 0.000 GB.

| fuente | fase | UTC | libre C: | libre E: | usado manifiestos | cache HF |
|---|---|---|---|---|---|---|
| chronos | antes | 2026-11-08T09:43:13Z | 2.623 GB | 337.870 GB | 0.000 GB | 0.000 GB |
| chronos | despues | 2026-11-08T09:43:40Z | 2.623 GB | 337.647 GB | 0.223 GB | 0.000 GB |
| lotsa | antes | 2026-11-08T09:43:40Z | 2.623 GB | 337.647 GB | 0.223 GB | 0.000 GB |
| lotsa | despues | 2026-11-08T09:45:28Z | 2.622 GB | 337.319 GB | 0.550 GB | 0.000 GB |
| lotsa | antes | 2026-11-08T09:46:15Z | 2.622 GB | 337.274 GB | 0.550 GB | 0.000 GB |
| lotsa | despues | 2026-11-08T09:46:23Z | 2.622 GB | 337.274 GB | 0.550 GB | 0.000 GB |
| binance | antes | 2026-11-08T09:46:35Z | 2.622 GB | 337.274 GB | 0.550 GB | 0.000 GB |
| binance | despues | 2026-11-08T10:45:23Z | 2.600 GB | 336.439 GB | 0.991 GB | 0.000 GB |

- Topes de LOTSA (se comprueban antes de cada descarga con el tamano que declara el Hub): total 0.327 GB de 10.000 GB; mayor subconjunto `temperature_rain_with_missing` 90.0 MB de 2.000 GB.

## Limites conocidos de las descargas

- shortcut: huggingface_hub reintenta por dentro (hasta 5 veces, espera de 1 a 8 s, Retry-After solo dentro de su ciclo) y no deja configurarlo; `fuentes.con_reintentos` anade 3 reintentos externos con espera exponencial y el Retry-After de la excepcion HTTP, en lugar de un transporte propio. Subir a GET propios (como Binance) si hiciera falta control total del ritmo.
- Desde el intento 2 las descargas del Hub van en serie, con `user_agent=quantdesk-lab-ingesta/0.1` (la biblioteca lo antepone a su cadena `hf_hub/...; python/...`) y con el transporte Xet desactivado (`HF_HUB_DISABLE_XET=1`). Los ficheros del Hub que ya estaban descargados (intento 1) se bajaron con el agente por defecto de la biblioteca y no se repitieron; su integridad consta por el SHA-256 LFS del Hub (tabla de hashes).
- Los GET propios (APIs de licencias, Zenodo, GitHub, Binance) usan el User-Agent del proyecto, 1 peticion/s por host, 3 reintentos con espera exponencial y Retry-After.

## Datasets obtenidos

| dataset | fuente | series (tronco / adaptadores) | puntos tronco / adaptadores | rango (UTC) | frecuencia | bytes crudo | bytes procesado | descarga (UTC) | SHA-256 del dataset |
|---|---|---|---|---|---|---|---|---|---|
| binance__klines_1d | binance | 0 / 10 | 0 / 30,406 | 2017-08-17T00:00:00Z a 2026-11-07T00:00:00Z | D | 2.0 MB | 1.2 MB | 2026-11-08T10:24:52Z | `586cf9f0e2d8e0a5...` |
| binance__klines_1h | binance | 0 / 5 | 0 / 389,813 | 2017-08-17T04:00:00Z a 2026-11-07T23:00:00Z | h | 20.5 MB | 13.0 MB | 2026-11-08T10:45:23Z | `8ceda17e11e6a442...` |
| chronos__exchange_rate | chronos | 0 / 0 | 0 / 0 | 1990-01-01T00:00:00Z a 2019-01-30T00:00:00Z | D | 0.4 MB | 0.0 MB | 2026-11-08T09:43:33Z | - (todas las series excluidas) |
| chronos__monash_cif_2016 | chronos | 0 / 0 | 0 / 0 | 1970-01-31T00:00:00Z a 1979-12-31T00:00:00Z | MS | 0.1 MB | 0.0 MB | 2026-11-08T09:43:37Z | - (todas las series excluidas) |
| chronos__monash_electricity_hourly | chronos | 321 / 0 | 8,443,584 / 0 | 2012-01-01T01:00:00Z a 2015-01-01T00:00:00Z | h | 31.1 MB | 40.3 MB | 2026-11-08T09:43:17Z | `d0254c2307b33cc4...` |
| chronos__monash_fred_md | chronos | 107 / 107 | 74,151 / 3,745 | 1959-01-31T00:00:00Z a 2019-08-31T00:00:00Z | MS | 0.4 MB | 0.3 MB | 2026-11-08T09:43:35Z | `fe2041239832d8e0...` |
| chronos__monash_hospital | chronos | 767 / 0 | 64,428 / 0 | 2000-01-01T00:00:00Z a 2006-12-01T00:00:00Z | MS | 0.1 MB | 0.1 MB | 2026-11-08T09:43:25Z | `96e72c1e7c84c505...` |
| chronos__monash_nn5_weekly | chronos | 0 / 0 | 0 / 0 | 1996-03-24T00:00:00Z a 1998-05-17T00:00:00Z | W | 0.1 MB | 0.0 MB | 2026-11-08T09:43:39Z | - (todas las series excluidas) |
| chronos__monash_tourism_monthly | chronos | 0 / 0 | 0 / 0 | 1979-01-31T00:00:00Z a 2007-09-30T00:00:00Z | MS | 0.3 MB | 0.0 MB | 2026-11-08T09:43:31Z | - (todas las series excluidas) |
| chronos__monash_traffic | chronos | 862 / 0 | 15,122,928 / 0 | 2015-01-01T00:00:00Z a 2016-12-31T23:00:00Z | h | 52.7 MB | 71.2 MB | 2026-11-08T09:43:21Z | `0b7517af3fe5a974...` |
| chronos__monash_weather | chronos | 3,010 / 0 | 43,032,000 / 0 | 1970-01-01T00:00:00Z a 2150-08-25T00:00:00Z | D | 133.2 MB | 164.9 MB | 2026-11-08T09:43:29Z | `7c3fbaed469acfb5...` |
| chronos__taxi_30min | chronos | 2,428 / 0 | 3,589,798 / 0 | 2015-01-01T00:00:00Z a 2016-01-31T14:00:00Z | 30min | 4.5 MB | 4.2 MB | 2026-11-08T09:43:23Z | `1e01ed64cbfb0c99...` |
| lotsa__australian_electricity_demand | lotsa | 5 / 0 | 1,153,584 / 0 | 2002-01-01T00:00:00Z a 2015-03-25T23:30:00Z | 30min | 4.6 MB | 7.7 MB | 2026-11-08T09:43:50Z | `f1a34d4e6b7b0de2...` |
| lotsa__bitcoin_with_missing | lotsa | 18 / 18 | 50,904 / 31,014 | 2009-01-03T00:00:00Z a 2021-06-19T00:00:00Z | D | 0.3 MB | 0.3 MB | 2026-11-08T09:44:50Z | `54a7bf5be0ab9fa2...` |
| lotsa__car_parts_with_missing | lotsa | 2,674 / 0 | 104,286 / 0 | 1998-01-01T00:00:00Z a 2001-03-01T00:00:00Z | MS | 0.5 MB | 0.1 MB | 2026-11-08T09:44:36Z | `7efe17b4cd80ef81...` |
| lotsa__cif_2016_12 | lotsa | 0 / 0 | 0 / 0 | 1970-01-01T00:00:00Z a 1978-12-01T00:00:00Z | ME | 0.0 MB | 0.0 MB | 2026-11-08T09:44:58Z | - (todas las series excluidas) |
| lotsa__cif_2016_6 | lotsa | 0 / 0 | 0 / 0 | 1970-01-01T00:00:00Z a 1975-09-01T00:00:00Z | ME | 0.0 MB | 0.0 MB | 2026-11-08T09:44:54Z | - (todas las series excluidas) |
| lotsa__covid_mobility | lotsa | 362 / 0 | 148,602 / 0 | 2020-02-15T00:00:00Z a 2021-04-02T00:00:00Z | D | 0.6 MB | 0.3 MB | 2026-11-08T09:44:12Z | `275c958a14a6ff9c...` |
| lotsa__elecdemand | lotsa | 1 / 0 | 17,520 / 0 | 2014-01-01T00:00:00Z a 2014-12-31T23:30:00Z | 30min | 0.1 MB | 0.1 MB | 2026-11-08T09:43:45Z | `7dab51f02e503918...` |
| lotsa__fred_md | lotsa | 107 / 107 | 74,151 / 2,461 | 1959-01-01T00:00:00Z a 2018-08-01T00:00:00Z | ME | 0.3 MB | 0.2 MB | 2026-11-08T09:44:46Z | `f0787fb2b1805e70...` |
| lotsa__kaggle_web_traffic_weekly | lotsa | 145,063 / 0 | 16,537,182 / 0 | 2015-07-05T00:00:00Z a 2017-09-03T00:00:00Z | W | 70.7 MB | 37.9 MB | 2026-11-08T09:44:42Z | `0855dbf710497bd1...` |
| lotsa__m1_monthly | lotsa | 0 / 0 | 0 / 0 | 1900-01-01T00:00:00Z a 1989-07-01T00:00:00Z | ME | 0.2 MB | 0.0 MB | 2026-11-08T09:45:11Z | - (todas las series excluidas) |
| lotsa__m4_daily | lotsa | 0 / 0 | 0 / 0 | 1750-01-01T00:00:00Z a 1777-02-26T00:00:00Z | D | 40.0 MB | 0.0 MB | 2026-11-08T09:45:21Z | - (todas las series excluidas) |
| lotsa__m4_monthly | lotsa | 0 / 0 | 0 / 0 | 1750-01-01T00:00:00Z a 1982-10-01T00:00:00Z | ME | 42.8 MB | 0.0 MB | 2026-11-08T09:45:27Z | - (todas las series excluidas) |
| lotsa__monash_m3_monthly | lotsa | 0 / 0 | 0 / 0 | 1857-01-01T00:00:00Z a 2003-08-01T00:00:00Z | ME | 0.6 MB | 0.0 MB | 2026-11-08T09:46:22Z | - (todas las series excluidas) |
| lotsa__nn5_daily_with_missing | lotsa | 0 / 0 | 0 / 0 | 1996-03-18T00:00:00Z a 1998-03-22T00:00:00Z | D | 0.3 MB | 0.0 MB | 2026-11-08T09:45:07Z | - (todas las series excluidas) |
| lotsa__nn5_weekly | lotsa | 0 / 0 | 0 / 0 | 1996-03-24T00:00:00Z a 1998-03-22T00:00:00Z | W | 0.1 MB | 0.0 MB | 2026-11-08T09:45:03Z | - (todas las series excluidas) |
| lotsa__oikolab_weather | lotsa | 8 / 0 | 800,456 / 0 | 2010-01-01T00:00:00Z a 2021-06-01T00:00:00Z | h | 3.2 MB | 4.1 MB | 2026-11-08T09:44:16Z | `a4a7ee6bda8b9326...` |
| lotsa__pedestrian_counts | lotsa | 66 / 0 | 3,130,762 / 0 | 2009-05-01T00:00:00Z a 2020-04-29T23:00:00Z | h | 12.5 MB | 15.5 MB | 2026-11-08T09:44:04Z | `a4c3381f7f657157...` |
| lotsa__saugeenday | lotsa | 1 / 0 | 23,711 / 0 | 1915-01-01T00:00:00Z a 1979-12-01T00:00:00Z | D | 0.1 MB | 0.1 MB | 2026-11-08T09:44:31Z | `14518e4228d13cbb...` |
| lotsa__solar_power | lotsa | 1 / 0 | 7,397,222 / 0 | 2019-08-01T00:00:03Z a 2020-07-08T11:08:07Z | 4s | 29.6 MB | 14.2 MB | 2026-11-08T09:43:54Z | `cb4c7e4ead5e2f91...` |
| lotsa__sunspot_with_missing | lotsa | 1 / 0 | 73,894 / 0 | 1818-01-08T00:00:00Z a 2020-05-01T00:00:00Z | D | 0.3 MB | 0.3 MB | 2026-11-08T09:44:27Z | `5b1847566c84057f...` |
| lotsa__temperature_rain_with_missing | lotsa | 32,072 / 0 | 22,290,040 / 0 | 2015-05-02T00:00:00Z a 2017-03-26T00:00:00Z | D | 90.0 MB | 39.1 MB | 2026-11-08T09:44:23Z | `80ff44e0f0fca5cc...` |
| lotsa__tourism_monthly | lotsa | 0 / 0 | 0 / 0 | 1979-01-01T00:00:00Z a 2005-09-01T00:00:00Z | ME | 0.4 MB | 0.0 MB | 2026-11-08T09:45:15Z | - (todas las series excluidas) |
| lotsa__traffic_weekly | lotsa | 862 / 0 | 82,752 / 0 | 2015-01-04T00:00:00Z a 2016-10-30T00:00:00Z | W | 0.4 MB | 0.3 MB | 2026-11-08T09:44:08Z | `23d144664873ac3d...` |
| lotsa__wind_power | lotsa | 1 / 0 | 7,397,147 / 0 | 2019-08-01T00:00:03Z a 2020-07-08T11:03:07Z | 4s | 29.6 MB | 16.5 MB | 2026-11-08T09:43:59Z | `b9922dc63f16c664...` |

Hash de dataset = SHA-256 de las lineas `ruta<TAB>sha256` ordenadas de sus parquet (manifiesto ordenado); el valor completo y el `contenido_sha256` (hash por serie, ordenado) estan en cada `manifest.json`.

## Calidad de los datos (se cuenta, no se corrige)

| dataset | series vacias | ids duplicados | duplicados de contenido | series con marcas irregulares/huecos | series con fechas invalidas | puntos NaN | duplicados Binance | huecos Binance |
|---|---|---|---|---|---|---|---|---|
| binance__klines_1d | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| binance__klines_1h | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 136 |
| chronos__exchange_rate | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 |
| chronos__monash_cif_2016 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_electricity_hourly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_fred_md | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_hospital | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_nn5_weekly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_tourism_monthly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_traffic | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| chronos__monash_weather | 0 | 0 | 18 | 0 | 3,010 | 0 | 0 | 0 |
| chronos__taxi_30min | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__australian_electricity_demand | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__bitcoin_with_missing | 0 | 0 | 0 | 0 | 0 | 8,072 | 0 | 0 |
| lotsa__car_parts_with_missing | 0 | 0 | 61 | 0 | 0 | 4,142 | 0 | 0 |
| lotsa__cif_2016_12 | 0 | 0 | 0 | 0 | 57 | 0 | 0 | 0 |
| lotsa__cif_2016_6 | 0 | 0 | 0 | 0 | 15 | 0 | 0 | 0 |
| lotsa__covid_mobility | 0 | 0 | 0 | 0 | 0 | 4,279 | 0 | 0 |
| lotsa__elecdemand | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__fred_md | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__kaggle_web_traffic_weekly | 0 | 0 | 64 | 0 | 0 | 0 | 0 | 0 |
| lotsa__m1_monthly | 0 | 0 | 0 | 0 | 15 | 0 | 0 | 0 |
| lotsa__m4_daily | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__m4_monthly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__monash_m3_monthly | 0 | 0 | 0 | 0 | 32 | 0 | 0 | 0 |
| lotsa__nn5_daily_with_missing | 0 | 0 | 0 | 0 | 0 | 1,673 | 0 | 0 |
| lotsa__nn5_weekly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__oikolab_weather | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__pedestrian_counts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__saugeenday | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__solar_power | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__sunspot_with_missing | 0 | 0 | 0 | 0 | 0 | 3,240 | 0 | 0 |
| lotsa__temperature_rain_with_missing | 0 | 0 | 14 | 0 | 0 | 598,369 | 0 | 0 |
| lotsa__tourism_monthly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__traffic_weekly | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lotsa__wind_power | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Hashes SHA-256 por fichero

### Procesados (parquet)

| dataset | fichero | filas | bytes | SHA-256 |
|---|---|---|---|---|
| binance__klines_1d | adaptadores.train.parquet | 30,406 | 1,154,184 | `1ff49bfbde6a241f9be87d898b70fc4fe2c1e06956cb291008289e636aebd095` |
| binance__klines_1h | adaptadores.train.parquet | 389,813 | 12,992,079 | `8abb105833b48e7fad867cd56b939f743f9f069a76760b2cd81c1900dee6e0a1` |
| chronos__monash_electricity_hourly | tronco.train.parquet | 7,444,032 | 35,509,644 | `0a5011ab9fff060235264948705544f46de3650eef161d77d5cb562c30089a28` |
| chronos__monash_electricity_hourly | tronco.val.parquet | 999,552 | 4,774,433 | `28e2baafbac3352fee68351c1629a6216c689e6761c7de55df20310a765f76a2` |
| chronos__monash_fred_md | adaptadores.train.parquet | 3,150 | 13,457 | `b79a2b5c3b1d5b5258f31635e8579a5ba2fba22988416c66795e53b59ed1fc7c` |
| chronos__monash_fred_md | adaptadores.val.parquet | 595 | 4,087 | `1ba85c4046403d396b2c3d328ba0bf1f22ae9a3c9aa3982d2e44d397b3705116` |
| chronos__monash_fred_md | tronco.train.parquet | 62,370 | 198,752 | `7b0fd3ae538e7020655df73aa11c5290771e2eebe22464cd1b3602cfdec7401b` |
| chronos__monash_fred_md | tronco.val.parquet | 11,781 | 44,396 | `74b24b60cd3cab183c426d251588538678de961c0027e8b1f272046df36596ad` |
| chronos__monash_hospital | tronco.train.parquet | 58,548 | 102,434 | `d4b2a2bbb4fcfb6de1289387496aaf5d4acd7d554ceb4b8874c353e27d17e79a` |
| chronos__monash_hospital | tronco.val.parquet | 5,880 | 11,148 | `df004952db3b5bea87dadd3d646d6a79e669670f18213f79995454a5225c1162` |
| chronos__monash_traffic | tronco.train.parquet | 13,561,512 | 63,819,786 | `09d3c86a2b8bdcc7345c1f762d44a46f1667ae27c2d55feff533cf77a0159de9` |
| chronos__monash_traffic | tronco.val.parquet | 1,561,416 | 7,373,632 | `a4f7756f7faf8236e9439d690af3ebdea67ddc9352bd6ef685d7f55bab5075b7` |
| chronos__monash_weather | tronco.train.parquet | 38,330,442 | 146,556,006 | `32a1c9e39682f6c92105b047f8ea7b2547be68e2a046565e0ab38efef7599258` |
| chronos__monash_weather | tronco.val.parquet | 4,701,558 | 18,319,666 | `5b0e37d9475c29b85937485794d167131cecd0a8b3c6f6058fa03139e44bac6c` |
| chronos__taxi_30min | tronco.train.parquet | 3,230,589 | 3,763,510 | `0fa4c919894f276a338f4c74628cf36571394db951230cfefbed646a5253897c` |
| chronos__taxi_30min | tronco.val.parquet | 359,209 | 418,630 | `a5b1cffe76f05f74a978be2eb3f24e57a4dbe4cadbbd8cdd03a67d8f69d243c8` |
| lotsa__australian_electricity_demand | tronco.train.parquet | 921,648 | 6,161,558 | `f6b61b94561bdd3f344a9722e5239b68570dda58b0773fe824781e8840755123` |
| lotsa__australian_electricity_demand | tronco.val.parquet | 231,936 | 1,529,682 | `e4ceda3d23c11a1b29d85be8eed7eb0f9cfa1e9b2e2873d9df069cdffba2054e` |
| lotsa__bitcoin_with_missing | adaptadores.train.parquet | 24,122 | 89,048 | `4c723c98f09495f650f170db290c8c7c422cdf50b8c70f6c24101b1d4e94856c` |
| lotsa__bitcoin_with_missing | adaptadores.val.parquet | 6,892 | 31,634 | `2e0b8435e4653161e29360a157586f6776cc554bdd3afc2f4e2cbaf9d2b210e2` |
| lotsa__bitcoin_with_missing | tronco.train.parquet | 39,592 | 126,981 | `2b67301f417fdcf5abd85bfe8a73419c6e8688af99ea1680a74f1f5385c8c839` |
| lotsa__bitcoin_with_missing | tronco.val.parquet | 11,312 | 38,912 | `b9771cf3e28474b905d3ff0e0ddeb5f14a0ca5bed9c9c59f5102c3234525484a` |
| lotsa__car_parts_with_missing | tronco.train.parquet | 93,522 | 52,749 | `9165173d16e49f41fbe344e4775df188374eea1215359cb0e156d17e8f22331c` |
| lotsa__car_parts_with_missing | tronco.val.parquet | 10,764 | 7,754 | `99c80d35a2aed780fa666cafa3733df0befdd7fd001157ec00854bb7cb583802` |
| lotsa__covid_mobility | tronco.train.parquet | 134,247 | 290,688 | `20937e90fa5b1a32124cc72005d3de05c9e6f9515f4c6c3f9865a34853971a84` |
| lotsa__covid_mobility | tronco.val.parquet | 14,355 | 36,118 | `52532a67f360223b957ac67306e195b0f806106629a174d56af20b5e2c4ada4b` |
| lotsa__elecdemand | tronco.train.parquet | 17,520 | 117,221 | `b01324c86da15c6b82b9122a6b58c98937e3d7c1c56d7e8dca41441484e4a603` |
| lotsa__fred_md | adaptadores.train.parquet | 2,093 | 8,200 | `687ea3924240b0d52b382e46fecc02ba6b50ea833bedab83d275775e5e626dc2` |
| lotsa__fred_md | adaptadores.val.parquet | 368 | 2,523 | `d626d06b2bace5f4d585d7df9fbab3777a8ebdd99f99ba421e238c4b8b1bfb22` |
| lotsa__fred_md | tronco.train.parquet | 63,063 | 196,615 | `a13e79c320af0a3f59ed9e98835644856055f22ac816a30b100f857de016dd13` |
| lotsa__fred_md | tronco.val.parquet | 11,088 | 36,173 | `86ab34de506bdc24970b7cbc5981c7302c38a3f4048e7455a2a8e98e0f5dc927` |
| lotsa__kaggle_web_traffic_weekly | tronco.train.parquet | 14,911,200 | 34,153,716 | `7dcad99ccc26f4e9aa67eb79394ce6c8d024299fbe73b3fd9d6f467969990902` |
| lotsa__kaggle_web_traffic_weekly | tronco.val.parquet | 1,625,982 | 3,766,935 | `4924172949344783fa74119690009fd34e003db1806fb8f2985086d071fb52a5` |
| lotsa__oikolab_weather | tronco.train.parquet | 800,456 | 4,147,229 | `efffd269d4b18f342e7869d08127960e39c9aff639a0fb1cbc13bdb790f4cd14` |
| lotsa__pedestrian_counts | tronco.train.parquet | 2,900,648 | 14,357,957 | `73f9d8297a0f36f14453c2b8ad390bb214bdf33438d65bb0520f7d39963cfc91` |
| lotsa__pedestrian_counts | tronco.val.parquet | 230,114 | 1,152,769 | `d862c33357dcd3aed1e37b57a50ec0ebeccb03e9df5e0dbcbbb9ac6157cad88c` |
| lotsa__saugeenday | tronco.train.parquet | 23,711 | 116,529 | `284c7b5502e6e454ba900e92f4144e248033ca4ab6d1cdbb5936fc324d350b5a` |
| lotsa__solar_power | tronco.train.parquet | 7,397,222 | 14,241,559 | `a2e8e86eb8188b2942cab63f4056be95e3ecaefd58468beb064e937d9565909f` |
| lotsa__sunspot_with_missing | tronco.train.parquet | 73,894 | 334,530 | `f48e43bd2bdaa20af65e9f1f38100843a08b3c90b86a8b5df9c80f6f014a8379` |
| lotsa__temperature_rain_with_missing | tronco.train.parquet | 20,020,170 | 35,032,430 | `613f50007f63967485a79486e7a666551805a5a8b0b1be297717f44b49df99cf` |
| lotsa__temperature_rain_with_missing | tronco.val.parquet | 2,269,870 | 4,036,674 | `676977933f22d778b032e7f153d8e4a4d318af5229f94d0ef38ec4a46a40b272` |
| lotsa__traffic_weekly | tronco.train.parquet | 74,304 | 288,985 | `4ef500e4941166a38874a86ac0d4ec9e61eb9d4f04f659aebaa79cfbcf136b17` |
| lotsa__traffic_weekly | tronco.val.parquet | 8,448 | 33,986 | `5a1c3744945c6b256d9dfe7fbf51545f1ec6df0173c341da85c7f50158980bbe` |
| lotsa__wind_power | tronco.train.parquet | 7,397,147 | 16,493,237 | `57c43c97c761f6c55c2058785297cfece5ac4df3c529b4bbbf9589edc5379bc5` |

### Crudo del Hub

| fichero | bytes | SHA-256 | verificado contra |
|---|---|---|---|
| Salesforce/lotsa_data/australian_electricity_demand/data-00000-of-00001.arrow | 4,615,480 | `31fbcc1b224df0d6a220ba2a45404a6ec52ba63b2cb4d6ab5d8cc843eb4dd4b9` | LFS sha256 del Hub |
| Salesforce/lotsa_data/australian_electricity_demand/dataset_info.json | 903 | `3652d236e41309dbf56bd6a78f2eeb31920418eceb0832473a74f99d57b11200` | git blob id del Hub |
| Salesforce/lotsa_data/australian_electricity_demand/state.json | 250 | `1f18d6510ff8c535849ac90cecbeb3b6b8611240e9763e76a4c7bd825f1e4adf` | git blob id del Hub |
| Salesforce/lotsa_data/bitcoin_with_missing/data-00000-of-00001.arrow | 329,328 | `11d61bc2d0db36aa8ffc67876a074900594d50f88e41b8fb93e4855d0ee50304` | LFS sha256 del Hub |
| Salesforce/lotsa_data/bitcoin_with_missing/dataset_info.json | 892 | `e90fc02c433a2ee40f4b74ab3aeaa1db352f1ac490aec7cd39c239fa24c4f101` | git blob id del Hub |
| Salesforce/lotsa_data/bitcoin_with_missing/state.json | 250 | `bc1022e839570da005bd1b8424d0aef3b9c3ceddd54b983b03cdbad94f79b80e` | git blob id del Hub |
| Salesforce/lotsa_data/car_parts_with_missing/data-00000-of-00001.arrow | 487,384 | `b01c3d866bccd3f796b3ba6cff2a2b680732ac55e46786d36c210ffa5c4d7ffe` | LFS sha256 del Hub |
| Salesforce/lotsa_data/car_parts_with_missing/dataset_info.json | 896 | `3748c440254f1f8eeef785f7f06bd582c7ae6edee5ba626ed65c47d60351c8df` | git blob id del Hub |
| Salesforce/lotsa_data/car_parts_with_missing/state.json | 250 | `8ae85989032ccc3c5973510e5bc88be5c732c2279280c3c2adc5699ebb48d5d4` | git blob id del Hub |
| Salesforce/lotsa_data/cif_2016_12/data-00000-of-00001.arrow | 25,192 | `dc660346e03be3cd9ea417a6d0cd530f592ee77bbafa130b599af64b3917986b` | LFS sha256 del Hub |
| Salesforce/lotsa_data/cif_2016_12/dataset_info.json | 880 | `026d5b0cbcef8d8e50007a66769cc359736525d86b5217a03be6fed7fdf33f8d` | git blob id del Hub |
| Salesforce/lotsa_data/cif_2016_12/state.json | 250 | `4455daeb4c15c5038da391ad329a97f6089254dfc872b1ab936f91a7ed79720a` | git blob id del Hub |
| Salesforce/lotsa_data/cif_2016_6/data-00000-of-00001.arrow | 3,912 | `da02af127fa31fcab469c56b415efd4b1c6b3dad896980c5f15473e69277d4af` | LFS sha256 del Hub |
| Salesforce/lotsa_data/cif_2016_6/dataset_info.json | 876 | `06022f3cb576c6758461ebb64319f37ae1aa7c5424c3df7b1b253f86c0430ed9` | git blob id del Hub |
| Salesforce/lotsa_data/cif_2016_6/state.json | 250 | `070b13728d38ff0e23237959ca2f1fa94a0350d0797cf4875e7dcb2275580ba6` | git blob id del Hub |
| Salesforce/lotsa_data/covid_mobility/data-00000-of-00001.arrow | 604,432 | `64b2f4a99b615f5bc0508880929d2b6e207ff3c44333545124ceb6dc977e3720` | LFS sha256 del Hub |
| Salesforce/lotsa_data/covid_mobility/dataset_info.json | 887 | `415a636b3cc7840964802104d71545d7cf49fe34824ba10e2f8c7e9d8a17a68a` | git blob id del Hub |
| Salesforce/lotsa_data/covid_mobility/state.json | 250 | `41bc3431684bfd9b11328c091e091d91c9cc40edac5708e6154c7248be53754b` | git blob id del Hub |
| Salesforce/lotsa_data/elecdemand/data-00000-of-00001.arrow | 71,128 | `5b96d3d195ffb22a6799780985b22c64e5ae936bb22e1051296457a5933003c9` | LFS sha256 del Hub |
| Salesforce/lotsa_data/elecdemand/dataset_info.json | 878 | `5149d4826ba9baf7015312445b1dc159ccd4200649dc9be6953f2c3e54d67283` | git blob id del Hub |
| Salesforce/lotsa_data/elecdemand/state.json | 250 | `3d23dc383da66829c881c082d991e85b664b1838aa245159fbd4bf1d07a2924b` | git blob id del Hub |
| Salesforce/lotsa_data/fred_md/data-00000-of-00001.arrow | 310,032 | `8c305db38e89a9fffed67a1f85a96a04ab15e54954566ef43fa0ceb213303564` | LFS sha256 del Hub |
| Salesforce/lotsa_data/fred_md/dataset_info.json | 880 | `eefecebbf5e8308f422ac12d8d9ff783b5626d79a3e87eb90bdb0f7a30bced12` | git blob id del Hub |
| Salesforce/lotsa_data/fred_md/state.json | 250 | `e0dbd58bcb44915797ced2096aff4be59af1542cab2f800dc666fcedab33921b` | git blob id del Hub |
| Salesforce/lotsa_data/kaggle_web_traffic_weekly/data-00000-of-00001.arrow | 70,737,520 | `7ae24fc5412ea1d249daeab6c39e2e7976281c2d3abfa9c85b712bf822227884` | LFS sha256 del Hub |
| Salesforce/lotsa_data/kaggle_web_traffic_weekly/dataset_info.json | 907 | `e50e66264b41be64b16686de0f4019cc9e99bd6eac754647a0d1d7884743e7c0` | git blob id del Hub |
| Salesforce/lotsa_data/kaggle_web_traffic_weekly/state.json | 250 | `6bf2e817c4a7c018ed21bffeb8365d872e82e5b39fa85e0daec5b2eaa087fa47` | git blob id del Hub |
| Salesforce/lotsa_data/m1_monthly/data-00000-of-00001.arrow | 195,904 | `978dd8d17b70ae17cf477b86711f963e58dc8ede1b4d00b53c76d17a95bac63f` | LFS sha256 del Hub |
| Salesforce/lotsa_data/m1_monthly/dataset_info.json | 883 | `53085396b8de512940bea8563776ccfc6f23a65a7d6d4ec6e423bcb5499dec2e` | git blob id del Hub |
| Salesforce/lotsa_data/m1_monthly/state.json | 250 | `64b26b75b664baa5e54e54a1617121c889a9ad77f4a0c54951fa94eb3f5972af` | git blob id del Hub |
| Salesforce/lotsa_data/m4_daily/data-00000-of-00001.arrow | 39,965,800 | `25ab846d5315e2bad2636810f666fb651f1f3a1a37c4b7ac96fa6e5ce28af353` | LFS sha256 del Hub |
| Salesforce/lotsa_data/m4_daily/dataset_info.json | 888 | `907ff837aedb081123271da2cef83df5c038d5e19ef091f29aafc2e4619e5918` | git blob id del Hub |
| Salesforce/lotsa_data/m4_daily/state.json | 250 | `12b83ecf815dfc9baf5efdf48c2930de70344615ecc57d3b29af5a3dbfc45f00` | git blob id del Hub |
| Salesforce/lotsa_data/m4_monthly/data-00000-of-00001.arrow | 42,786,056 | `c8b6aeceac12e970a1f99529ff7c33cea056876e56ed5fb4e919fa6d934b3b2c` | LFS sha256 del Hub |
| Salesforce/lotsa_data/m4_monthly/dataset_info.json | 891 | `5c46f7603d4a1de5a9ae5a3f3ca91a2e9e9c5a259e93cc1799493e79fde844a8` | git blob id del Hub |
| Salesforce/lotsa_data/m4_monthly/state.json | 250 | `a24198c958852cb8382a8fdbcf7289de31afb39761b0c5b9adfea6b4ca2a6269` | git blob id del Hub |
| Salesforce/lotsa_data/monash_m3_monthly/data-00000-of-00001.arrow | 604,880 | `f477cc8b9f67b53dd0d71399761f62d8498defae4d6f6f735f8f1ba1eeec1f09` | LFS sha256 del Hub |
| Salesforce/lotsa_data/monash_m3_monthly/dataset_info.json | 891 | `9d14bf15ec949829c7d43b3383f90b1c2ee290cea1759cd122ded1c15fe916f8` | git blob id del Hub |
| Salesforce/lotsa_data/monash_m3_monthly/state.json | 250 | `3d7c8dac46059c1323142de05a6ad096eddc132f7a90365425ea0b610d2e0db5` | git blob id del Hub |
| Salesforce/lotsa_data/nn5_daily_with_missing/data-00000-of-00001.arrow | 330,024 | `06f9d0f2efeb9edc6e034e9e6b611dffd7d9b202fb155ca23a53cc8d66c9dea9` | LFS sha256 del Hub |
| Salesforce/lotsa_data/nn5_daily_with_missing/dataset_info.json | 895 | `e25f462e101e4bec4432100701607138a987803ae0d68d696be33a45051791b0` | git blob id del Hub |
| Salesforce/lotsa_data/nn5_daily_with_missing/state.json | 250 | `f7a164455bb1e066e8ca488a453e4f081805dae13d754696d0ac92b1f173f72b` | git blob id del Hub |
| Salesforce/lotsa_data/nn5_weekly/data-00000-of-00001.arrow | 50,752 | `c849f326a7095ec21f96295550b0162ca7cd3d90e83dccd9f01065a9643f5ab0` | LFS sha256 del Hub |
| Salesforce/lotsa_data/nn5_weekly/dataset_info.json | 880 | `53ea508f4b930667122c9391b43252fbf848362faa55e7a4e3f3c7a6b29c6781` | git blob id del Hub |
| Salesforce/lotsa_data/nn5_weekly/state.json | 250 | `0967991724b2c88d319674e8fefa73b8d4d0754234afcbc2b2d5116a41338431` | git blob id del Hub |
| Salesforce/lotsa_data/oikolab_weather/data-00000-of-00001.arrow | 3,203,032 | `3e27904bbaf61243a95fc30a5566b266f7bbca282233710d40ae95014efa0991` | LFS sha256 del Hub |
| Salesforce/lotsa_data/oikolab_weather/dataset_info.json | 889 | `7c1a32f653664c9ebdf75cb84979ef4ebf1b2a7c0479d4311e019ecdde78d47f` | git blob id del Hub |
| Salesforce/lotsa_data/oikolab_weather/state.json | 250 | `c4de947b6870f752890dacfa82311d81542a228b1045dd24c18ec6218a56c1d8` | git blob id del Hub |
| Salesforce/lotsa_data/pedestrian_counts/data-00000-of-00001.arrow | 12,525,656 | `de78f2fb96ba11815b92bd4f472a38dd65afc45ea1d9850f2a16f826176fb11b` | LFS sha256 del Hub |
| Salesforce/lotsa_data/pedestrian_counts/dataset_info.json | 895 | `5906507a38fedc5fac7eca5d5eb26446351e46b09cdd9d9f6009c46030e61c66` | git blob id del Hub |
| Salesforce/lotsa_data/pedestrian_counts/state.json | 250 | `ca7c00c196cb70b7e7269660de2d35914bbfbf2192f82648f90392874f646659` | git blob id del Hub |
| Salesforce/lotsa_data/saugeenday/data-00000-of-00001.arrow | 95,896 | `14e4a1060ce6844ff9f905efb1473c67393c4230dd7e9c52d614800f959f8f2c` | LFS sha256 del Hub |
| Salesforce/lotsa_data/saugeenday/dataset_info.json | 878 | `8347233aa612aec996ebcb177be94ce9a669651679742dfc8b90558b6c80a8c0` | git blob id del Hub |
| Salesforce/lotsa_data/saugeenday/state.json | 250 | `7e1f05e8b8e4ee0dbecebe8d84a930fe85bda314379ec44416b9687dd156081c` | git blob id del Hub |
| Salesforce/lotsa_data/solar_power/data-00000-of-00001.arrow | 29,589,936 | `dc6dc4179c1a652be124abbae9d62e464db2947cf06eb90e653fa2fb299ac54e` | LFS sha256 del Hub |
| Salesforce/lotsa_data/solar_power/dataset_info.json | 888 | `eb8021d134b035803dc7e0f1b3a59d66d453741c728e47e86fd01074f45c2a36` | git blob id del Hub |
| Salesforce/lotsa_data/solar_power/state.json | 250 | `921036bb8cc7020e3c5b945de15a5fed773903fe012ae3119670059404012a76` | git blob id del Hub |
| Salesforce/lotsa_data/sunspot_with_missing/data-00000-of-00001.arrow | 296,624 | `adb179d55ba298f5dbeda4a131c5bc5883540435d392a6456bf7ea12ede85f05` | LFS sha256 del Hub |
| Salesforce/lotsa_data/sunspot_with_missing/dataset_info.json | 891 | `b371fcfc0497241dc5f7ee79f85b30b441fac421f868db4943efd50613736e2f` | git blob id del Hub |
| Salesforce/lotsa_data/sunspot_with_missing/state.json | 250 | `fd8015ce64e2f4df91321b70ce8cc05d9a4e799a31caad718485f6acfacd1c55` | git blob id del Hub |
| Salesforce/lotsa_data/temperature_rain_with_missing/data-00000-of-00001.arrow | 90,028,568 | `31ba52586e53c9489df230e38f025ba5005556203d2dcc7f1804fd637858ee75` | LFS sha256 del Hub |
| Salesforce/lotsa_data/temperature_rain_with_missing/dataset_info.json | 910 | `4863596a4385955aa7d2bd9bb47bce25836a18449377f6bc90eefa9319dae9b3` | git blob id del Hub |
| Salesforce/lotsa_data/temperature_rain_with_missing/state.json | 250 | `362e0ee25c0ea52512e0fb24d2c4db635787f5761215066728b24a3b6c824be8` | git blob id del Hub |
| Salesforce/lotsa_data/tourism_monthly/data-00000-of-00001.arrow | 412,056 | `6a88626918dcf959d43256099395419c1a7b50899c2149f33763dc26b9951b65` | LFS sha256 del Hub |
| Salesforce/lotsa_data/tourism_monthly/dataset_info.json | 888 | `d4a8da9da30bb18d8fe33485184bea84349266c69babeb700da9a01a62437dd8` | git blob id del Hub |
| Salesforce/lotsa_data/tourism_monthly/state.json | 250 | `27c8dd50984b8d7806de5d256fc37603763dca82114c7ca27ba455846c53ab4e` | git blob id del Hub |
| Salesforce/lotsa_data/traffic_weekly/data-00000-of-00001.arrow | 356,928 | `52fb1df16d5b591d50438e67a658168beb8b86bc7ebdb4a488dd02505eb36f3d` | LFS sha256 del Hub |
| Salesforce/lotsa_data/traffic_weekly/dataset_info.json | 887 | `381e2ed264a4a23cd001b280c874b9cf10f2602e77463ca9ee1844514e376443` | git blob id del Hub |
| Salesforce/lotsa_data/traffic_weekly/state.json | 250 | `3c14cb3b0f9b7aa024474c9bf4f929e4b763e6fb6e3ed0669618f6a09e8a5c77` | git blob id del Hub |
| Salesforce/lotsa_data/wind_power/data-00000-of-00001.arrow | 29,589,640 | `4707acbd5d1d691ff438de231b987d4c4948eb7122166959f7e0774ed7a10ad5` | LFS sha256 del Hub |
| Salesforce/lotsa_data/wind_power/dataset_info.json | 887 | `9d49f8179218ed31da6623662d5ecf7fc28518a3a9d8f14be9bcc62e0f1b02bf` | git blob id del Hub |
| Salesforce/lotsa_data/wind_power/state.json | 250 | `1d036bf7cb4bb235ba5c7e1715f9b72b971fc32dad9702f4b768bb30de4db523` | git blob id del Hub |
| autogluon/chronos_datasets/exchange_rate/train-00000-of-00001.parquet | 401,501 | `c214a83fe8d21ef6aea8a230d9131601e5a0a0157b1b0c713470974f1e565edc` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_cif_2016/train-00000-of-00001.parquet | 70,876 | `9c570a2f42b15adeba850d2d2f76b06469996fc81aa1ee92a1a1b3229ed00f6e` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_electricity_hourly/train-00000-of-00001.parquet | 31,139,117 | `b9a0bf2b13d6b4f93afbaa97b47db064a7ac7740f6c8e40f9a97261c475c9aee` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_fred_md/train-00000-of-00001.parquet | 412,207 | `55d622cf7a51cccb1fd4bdedd58f17a8409252450a20889e36bfa7fd811cae2e` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_hospital/train-00000-of-00001.parquet | 117,078 | `ba3720171df9da41a20bc58bc270a7211561351a5ee14b49cefe2795d0509f4d` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_nn5_weekly/train-00000-of-00001.parquet | 64,620 | `b4848302e4e5645187e425fcc09e4c7da0151f13d0c2fc65fd722f9956dd32c2` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_tourism_monthly/train-00000-of-00001.parquet | 334,951 | `ac8d1c6a87cbdea71c1327828c58d9628f0be3dd322da545e17425b427c898ee` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_traffic/train-00000-of-00001.parquet | 52,748,547 | `c2ef1656931b3a33925817c461ccb724dfd19e948ca4c237ead59fc5e6be768f` | LFS sha256 del Hub |
| autogluon/chronos_datasets/monash_weather/train-00000-of-00001.parquet | 133,164,027 | `50f7ebecd006b9bff3f5b872924efd1e8820bcaf0ab9973d10138924dc762643` | LFS sha256 del Hub |
| autogluon/chronos_datasets/taxi_30min/train-00000-of-00001.parquet | 4,541,244 | `0bff6eb58578a9be944a55b88b7b04fb104b92613cd3d1c18f31570a93858a96` | LFS sha256 del Hub |

### Crudo de Binance

1,640 zip mensuales/diarios (22.5 MB), cada uno verificado contra su `.CHECKSUM` oficial. Lista completa con SHA-256 en `E:/quantdesk-lab/data/public/binance/raw_manifest.json`; hash del conjunto ordenado `7ac86656f4aa3d07cb617d0a3b400aafef4555535817af36c593706d112c5736`.

## No obtenido (con motivo)

- **fred:** robots.txt de FRED ('User-agent: *', Crawl-delay: 1) no prohibe el CSV, pero el servidor cierra la conexion (sin respuesta HTTP) o agota el tiempo en la pagina de terminos y en el CSV de muestra con el User-Agent del proyecto, tras 3 reintentos con espera exponencial; es un bloqueo y no se sortea con otro agente. Sin acceso a sus terminos la licencia no es verificable. Nota: algunas series de FRED tienen copyright de terceros (p. ej. VIX de CBOE, indices ICE BofA).
- **stooq:** robots.txt de stooq.com solo permite Googlebot y Bingbot ('User-agent: * / Disallow: /'); ademas el 2026-11-08 una unica peticion de diagnostico al CSV y a la pagina de descarga masiva devolvio un reto de verificacion JavaScript anti-bot. No se fuerza ni se sortea.
- **yahoo:** Los terminos de Yahoo prohiben acceder o recoger datos 'using any automated means ... without our express, prior permission' y robots.txt de query1.finance.yahoo.com declara 'User-agent: * / Disallow: /'. No se fuerza.
- **chronos__m4_daily:** no descargado. La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta); el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404): no verificable.
- **chronos__m4_monthly:** no descargado. La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta); el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404): no verificable.
- **chronos__training_corpus_kernel_synth_1m:** no descargado. La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta): no verificable.
