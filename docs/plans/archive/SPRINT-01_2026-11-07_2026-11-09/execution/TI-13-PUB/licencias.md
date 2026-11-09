# TI-13-PUB: licencias de las fuentes publicas

Consulta de licencias: 2026-11-08T09:46:14Z (UTC). Generado por `scripts/ingesta_publica.py licencias`; cada fila sale de `E:/quantdesk-lab/runs/TI-13-PUB/licencias.json`, que cita la evidencia descargada (ruta y SHA-256 en la ultima seccion).
Regla: licencia no verificable contra la evidencia => **excluida** (no se descarga). Orden: licencia primero, datos despues.

## Tabla de licencias

| Fuente | Dataset / subconjunto | Licencia declarada | Licencia de origen | Investigacion / comercial / redistribucion | Atribucion | Clase D-11 | Veredicto | Destino D-11 (registro) |
|---|---|---|---|---|---|---|---|---|
| binance | klines 1d (spot) | CC BY-NC-SA 4.0 ([ficha](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md)) | - | si (no comercial) / NO / solo bajo CC BY-NC-SA 4.0 y con atribucion | Atribuir a Binance Vision; derivados bajo la misma licencia | real con fecha | solo adaptadores | adaptadores |
| binance | klines 1h (spot) | CC BY-NC-SA 4.0 ([ficha](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md)) | - | si (no comercial) / NO / solo bajo CC BY-NC-SA 4.0 y con atribucion | Atribuir a Binance Vision; derivados bajo la misma licencia | real con fecha | solo adaptadores | adaptadores |
| chronos | exchange_rate | MIT ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | - | si / si / si, con aviso de licencia | Conservar el aviso de copyright y la licencia | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| chronos | m4_daily | sin licencia declarada ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | - | - / - / - | - | financiera | excluida | - |
| chronos | m4_monthly | sin licencia declarada ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | - | - / - / - | - | financiera | excluida | - |
| chronos | monash_cif_2016 | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656042)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| chronos | monash_electricity_hourly | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656140)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | no financiera | usable en tronco | tronco (intacta) |
| chronos | monash_fred_md | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4654833)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | financiera | usable (tronco antes del corte, resto adaptadores) | tronco < corte; adaptadores >= corte |
| chronos | monash_hospital | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656014)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | no financiera | usable en tronco | tronco (intacta) |
| chronos | monash_nn5_weekly | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656125)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| chronos | monash_tourism_monthly | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656096)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| chronos | monash_traffic | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656132)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | no financiera | usable en tronco | tronco (intacta) |
| chronos | monash_weather | CC BY 4.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4654822)) | si / si / si, con atribucion | Citar a los autores, enlazar la licencia e indicar los cambios | no financiera | usable en tronco | tronco (intacta) |
| chronos | taxi_30min | Apache 2.0 ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | - | si / si / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| chronos | training_corpus_kernel_synth_1m | sin licencia declarada ([ficha](https://huggingface.co/datasets/autogluon/chronos_datasets)) | - | - / - / - | - | no financiera | excluida | - |
| lotsa | australian_electricity_demand | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4659727)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | bitcoin_with_missing | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/5121965)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable (tronco antes del corte, resto adaptadores) | tronco < corte; adaptadores >= corte |
| lotsa | car_parts_with_missing | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656022)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | cif_2016_12 | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656042)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | cif_2016_6 | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656042)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | covid_mobility | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4663809)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | elecdemand | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656069)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | fred_md | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4654833)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable (tronco antes del corte, resto adaptadores) | tronco < corte; adaptadores >= corte |
| lotsa | kaggle_web_traffic_weekly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656664)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | m1_monthly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656159)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | m4_daily | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656548)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | m4_monthly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656480)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | monash_m3_monthly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656298)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | nn5_daily_with_missing | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656110)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | nn5_weekly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656125)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | oikolab_weather | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/5184708)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | pedestrian_counts | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656626)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | saugeenday | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656058)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | solar_power | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656027)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | sunspot_with_missing | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4654773)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | temperature_rain_with_missing | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/5129073)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | tourism_monthly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656096)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | financiera | usable; excluida del tronco por D-11 | excluida del tronco (fechas no verificables) |
| lotsa | traffic_weekly | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656135)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |
| lotsa | wind_power | Apache 2.0 ([ficha](https://huggingface.co/datasets/Salesforce/lotsa_data)) | CC BY 4.0 ([Zenodo](https://zenodo.org/records/4656032)) | si / tratar como NO hasta aclarar (README de LOTSA: 'research purposes only') / si, con aviso de licencia | Conservar el aviso de licencia y de copyright | no financiera | usable en tronco | tronco (intacta) |

### Motivo de cada veredicto

- `binance__klines_1d`: verificada. Terminos del dataset (Binance Vision Dataset Terms v1.0, 2026-08-26): CC BY-NC-SA 4.0; backtesting personal no productivo permitido; uso comercial excluido (3.4, 4.1-4.4).
- `binance__klines_1h`: verificada. Terminos del dataset (Binance Vision Dataset Terms v1.0, 2026-08-26): CC BY-NC-SA 4.0; backtesting personal no productivo permitido; uso comercial excluido (3.4, 4.1-4.4).
- `chronos__exchange_rate`: verificada. Licencia declarada en la tarjeta.
- `chronos__m4_daily`: excluida. La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta); el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404): no verificable.
- `chronos__m4_monthly`: excluida. La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta); el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404): no verificable.
- `chronos__monash_cif_2016`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_electricity_hourly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_fred_md`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_hospital`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_nn5_weekly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_tourism_monthly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_traffic`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__monash_weather`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `chronos__taxi_30min`: verificada. Licencia declarada en la tarjeta.
- `chronos__training_corpus_kernel_synth_1m`: excluida. La tarjeta no declara licencia para el subconjunto (licencia del repo: 'other'; el README remite a la licencia de cada config, que falta): no verificable.
- `lotsa__australian_electricity_demand`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__bitcoin_with_missing`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__car_parts_with_missing`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__cif_2016_12`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__cif_2016_6`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__covid_mobility`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__elecdemand`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__fred_md`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__kaggle_web_traffic_weekly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__m1_monthly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__m4_daily`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__m4_monthly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__monash_m3_monthly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__nn5_daily_with_missing`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__nn5_weekly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__oikolab_weather`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__pedestrian_counts`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__saugeenday`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__solar_power`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__sunspot_with_missing`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__temperature_rain_with_missing`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__tourism_monthly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__traffic_weekly`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).
- `lotsa__wind_power`: verificada. Licencia declarada en la tarjeta y confirmada en el registro de origen (Zenodo).

## Fuentes pedidas que no se obtienen

| Fuente | Estado | Motivo | Enlace de consulta |
|---|---|---|---|
| fred | excluida | robots.txt de FRED ('User-agent: *', Crawl-delay: 1) no prohibe el CSV, pero el servidor cierra la conexion (sin respuesta HTTP) o agota el tiempo en la pagina de terminos y en el CSV de muestra con el User-Agent del proyecto, tras 3 reintentos con espera exponencial; es un bloqueo y no se sortea con otro agente. Sin acceso a sus terminos la licencia no es verificable. Nota: algunas series de FRED tienen copyright de terceros (p. ej. VIX de CBOE, indices ICE BofA). | https://fred.stlouisfed.org/legal/ |
| stooq | excluida | robots.txt de stooq.com solo permite Googlebot y Bingbot ('User-agent: * / Disallow: /'); ademas el 2026-11-08 una unica peticion de diagnostico al CSV y a la pagina de descarga masiva devolvio un reto de verificacion JavaScript anti-bot. No se fuerza ni se sortea. | https://stooq.com/robots.txt |
| yahoo | excluida | Los terminos de Yahoo prohiben acceder o recoger datos 'using any automated means ... without our express, prior permission' y robots.txt de query1.finance.yahoo.com declara 'User-agent: * / Disallow: /'. No se fuerza. | https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html |

## Notas

- **LOTSA:** la tarjeta del repo declara `apache-2.0`, pero el README limita la publicacion a 'research purposes only'. La correspondencia de cada subconjunto con su registro de Zenodo (Monash Time Series Forecasting Archive, CC BY 4.0) es por nombre y la respalda la Tabla 14 del paper de LOTSA (arXiv 2402.02592), que atribuye estos subconjuntos al repositorio Monash. Se aplica la condicion mas restrictiva.
- **Chronos:** la licencia del repo es `other`; el README remite a la de cada config. Solo se usan configs con licencia declarada en la tarjeta; las que no la declaran (m4_daily, m4_monthly, training_corpus_kernel_synth_1m) quedan excluidas sin descargar.
- **Binance Vision:** CC BY-NC-SA 4.0, no comercial; los terminos tratan como derivados los modelos entrenados con los datos (2.4). Decision de producto pendiente del usuario si quantdesk se usa comercialmente.
- **FRED:** algunas series tienen copyright de terceros (CBOE, ICE BofA...); no se ingiere (ver tabla de fuentes no obtenidas).

## Evidencia consultada

| Id | URL | Estado | SHA-256 | Consulta (UTC) |
|---|---|---|---|---|
| binance_readme | https://raw.githubusercontent.com/binance/binance-public-data/master/README.md | 200 | 2e133d9945a9263a02781369078e72805eff074680f305cd5460016471c6caad | 2026-11-08T09:34:48Z |
| binance_terms | https://raw.githubusercontent.com/binance/binance-public-data/master/TERMS_AND_CONDITIONS.md | 200 | 99c4921dbe023cd68c1a447775707d621453cc78aec6ac0bfe2e6c06a5114ee0 | 2026-11-08T09:34:48Z |
| fred_csv_muestra | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10 | ERROR: https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10: TimeoutError: The read | - | 2026-11-08T09:34:49Z |
| fred_robots | https://fred.stlouisfed.org/robots.txt | 200 | ae2677d993247f34d0c1f1e974d3940c24cc4c14ec1544a28d334158c41d99ed | 2026-11-08T09:38:22Z |
| fred_terms | https://fred.stlouisfed.org/legal/ | ERROR: https://fred.stlouisfed.org/legal/: TimeoutError: The read operation timed out t | - | 2026-11-08T09:38:22Z |
| github_m4_licencia | https://api.github.com/repos/Mcompetitions/M4-methods/license | 404 | 6c0109c2ac75f1f264b61da6aff1737f7bc7eac254e6396710ff81a4139f32b1 | 2026-11-08T09:41:56Z |
| hf_chronos_api | https://huggingface.co/api/datasets/autogluon/chronos_datasets?blobs=true | 200 | b0b756a7a22ae2a00976995ca81e9cb896be37b53a079767882b90e4f67fb857 | 2026-11-08T09:41:57Z |
| hf_chronos_readme | https://huggingface.co/datasets/autogluon/chronos_datasets/raw/main/README.md | 200 | 1726bc69085b71b2189ff116b61951ae318e77a82b2103308297cf626ce14862 | 2026-11-08T09:41:57Z |
| hf_lotsa_api | https://huggingface.co/api/datasets/Salesforce/lotsa_data?blobs=true | 200 | 139bc046b63e4f8ccae780bfb34cdd0c4086ae44bd7b4951554124abf103d4af | 2026-11-08T09:41:58Z |
| hf_lotsa_readme | https://huggingface.co/datasets/Salesforce/lotsa_data/raw/main/README.md | 200 | d30ca30dec5dc30c87b865452e8dedae9c812d206b44efb950b0f5de01593ff3 | 2026-11-08T09:41:59Z |
| stooq_robots | https://stooq.com/robots.txt | 200 | b2f1e90e59d2e03ef256ecf56f0cdd50b00d53f46d7ac8cde7c505525ef15c45 | 2026-11-08T09:42:00Z |
| yahoo_robots | https://query1.finance.yahoo.com/robots.txt | 200 | 331ea9090db0c9f6f597bd9840fd5b171830f6e0b3ba1cb24dfa91f0c95aedc1 | 2026-11-08T09:42:00Z |
| yahoo_terms | https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html | 200 | 268da8486fc5ac8919487c759188e60055386f7dd6aae0d0c667d06bb45439fe | 2026-11-08T09:42:00Z |
| zenodo_4654773 | https://zenodo.org/api/records/4654773 | 200 | d4a20adca248d09d2b234112d40e4c0b44c73278a5a40e12690b0f8b3e709394 | 2026-11-08T09:42:00Z |
| zenodo_4654822 | https://zenodo.org/api/records/4654822 | 200 | 432d0ef494a1b776a77e7e4b440a23e553b7c5060d960049db3828312b19f361 | 2026-11-08T09:42:00Z |
| zenodo_4654833 | https://zenodo.org/api/records/4654833 | 200 | 4f4898b869768a73f555fcc225d8589568098b6fedba696336e46c780c1e3c9e | 2026-11-08T09:42:01Z |
| zenodo_4656014 | https://zenodo.org/api/records/4656014 | 200 | a73a8463cb8fc3a8caa3f6c9a88282ba564421d8785af13829c38d0739a4f366 | 2026-11-08T09:42:02Z |
| zenodo_4656022 | https://zenodo.org/api/records/4656022 | 200 | 578cbe21abd0a3a105233b6837e9951082b9e00563b1d6fe2f64083ef5eda91a | 2026-11-08T09:42:03Z |
| zenodo_4656027 | https://zenodo.org/api/records/4656027 | 200 | 21540699b9bbd42aa667dcb3503ec19760ffd8dcf2b6fc533c9842d94be642cb | 2026-11-08T09:42:04Z |
| zenodo_4656032 | https://zenodo.org/api/records/4656032 | 200 | 83e4e56fbb92d790d09108fb3f37213fba888a1632333fc19863bda2efbf07e0 | 2026-11-08T09:42:05Z |
| zenodo_4656042 | https://zenodo.org/api/records/4656042 | 200 | 19b22bb26c16f590a036f506edc109e87abc5de68744b5f98f9b8b52bedaac93 | 2026-11-08T09:42:06Z |
| zenodo_4656058 | https://zenodo.org/api/records/4656058 | 200 | 9f3cb252bc9fad61883ad59bf92d4f0fcf57d09af226dd0dcdbd83edb6beed1a | 2026-11-08T09:42:07Z |
| zenodo_4656069 | https://zenodo.org/api/records/4656069 | 200 | a5d1cf1d738ba5b8fce3c65b4b961eb4997c787e29d2645011a19ee56c3cda5f | 2026-11-08T09:42:08Z |
| zenodo_4656096 | https://zenodo.org/api/records/4656096 | 200 | 84b679028ac1a0544bb9d8d087d4905445726e3f66664c2072713b643dd421f0 | 2026-11-08T09:42:09Z |
| zenodo_4656110 | https://zenodo.org/api/records/4656110 | 200 | 870f7484135030e314f4aff9ad1f448fb668656484d73b4aaa062faea8cb15f0 | 2026-11-08T09:42:10Z |
| zenodo_4656125 | https://zenodo.org/api/records/4656125 | 200 | b3626d45ca83c85f109308d089852a28666242b9fbe7f8646ac3eb38f4da85ec | 2026-11-08T09:42:12Z |
| zenodo_4656132 | https://zenodo.org/api/records/4656132 | 200 | 66796cf7265993b9cff247456bb0d52ddbc7cbfb6fe8324279ef910961b51dcb | 2026-11-08T09:42:13Z |
| zenodo_4656135 | https://zenodo.org/api/records/4656135 | 200 | 27894201c9df7f0175ec6746dbce2c26b7ad493016068f3fb029ca2acaa9ff7e | 2026-11-08T09:42:14Z |
| zenodo_4656140 | https://zenodo.org/api/records/4656140 | 200 | 65a63d9640ccfff98c24133cbe4a32769d57c4c4aa5b78ed8d42e26d51acbf31 | 2026-11-08T09:42:15Z |
| zenodo_4656159 | https://zenodo.org/api/records/4656159 | 200 | 6c1c5d037cfe0117d7b12d6067e6da5337676210fd852c2935a639fa7a0cbf09 | 2026-11-08T09:42:16Z |
| zenodo_4656298 | https://zenodo.org/api/records/4656298 | 200 | 011c05e26ddb341b0114a2c97f3d8e7b3ad0e5f9df72023fdb329ac7e90bb5ec | 2026-11-08T09:42:17Z |
| zenodo_4656480 | https://zenodo.org/api/records/4656480 | 200 | 1be3264cf7e02d02bc7e4111fad7fc500e7cedc9b8f7cee1e9f7547d5d5c4c65 | 2026-11-08T09:42:18Z |
| zenodo_4656548 | https://zenodo.org/api/records/4656548 | 200 | c4c3f08a6bf1c722bb472e15f1d62e84463e5c06eb4fe8bbb518619bb8b736f0 | 2026-11-08T09:42:19Z |
| zenodo_4656626 | https://zenodo.org/api/records/4656626 | 200 | c85d41db19e0a435ec591225a9b867e3e723198256566aadc7ebc4f4c7993f82 | 2026-11-08T09:42:20Z |
| zenodo_4656664 | https://zenodo.org/api/records/4656664 | 200 | 6a58a59ca739c6aff59c9bb1e538e155af66b0f0604397285c42f738d8dc2b8e | 2026-11-08T09:42:21Z |
| zenodo_4659727 | https://zenodo.org/api/records/4659727 | 200 | e3008ffe6b95d42a927aed8ed770067b96775a8c2ab4fffb48260aa220bf06d4 | 2026-11-08T09:42:22Z |
| zenodo_4663809 | https://zenodo.org/api/records/4663809 | 200 | 434b8763b1103bea1cec3d779811f07e78fa725a6bb2a3466928800d892a0d95 | 2026-11-08T09:42:23Z |
| zenodo_5121965 | https://zenodo.org/api/records/5121965 | 200 | b0859177d6a0ae381e609e15c359ef89a91a89196a56bbff0489d40dccb26891 | 2026-11-08T09:42:24Z |
| zenodo_5129073 | https://zenodo.org/api/records/5129073 | 200 | a5e27d83a18bc32427d2e50355171ea564e70fd293c3adda640a0fe7439a49d8 | 2026-11-08T09:42:25Z |
| zenodo_5184708 | https://zenodo.org/api/records/5184708 | 200 | a8e9141fa409440b3aabcfc65fc24a14ff82ea22acdd6bd16aafff3de2caabbb | 2026-11-08T09:42:26Z |
