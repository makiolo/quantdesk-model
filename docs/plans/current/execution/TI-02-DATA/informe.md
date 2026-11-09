# TI-02-DATA: informe del exportador a `engine.market-history/v1`

- Motor: quantdesk 69fdb39d; python 3.12.3, pyarrow 26.0.1, pandas 3.1.1, numpy 2.5.4.
- Generado por `exportar_market_history.py --informe` a partir de `procedencia.json` y del registro de cada ejecucion.
- Reglas: el corte es el instante `AAAA-MM-DDT00:00:00Z`; una fila entra solo si su cierre y su `available_at_ms` son menores o iguales (si lo tiene); `default_lag_ms` queda nulo salvo en un dataset con disponibilidad proxy declarada (valor 0, y esas filas llevan `available_at_ms` nulo); los huecos no se rellenan; nada se descarta sin contarlo.

| dataset | corte | filas por tabla | tablas vacias tras el corte | tipo de disponibilidad por tabla | dataset_hash |
|---|---|---|---|---|---|
| `binance_c20261101` | 2026-11-01 | binance_ohlcv_1d 30336, binance_ohlcv_1h 388973 | ninguna | binance_ohlcv_1d: cierre declarado por la fuente; binance_ohlcv_1h: cierre declarado por la fuente | `sha256:d765d56037f700bd...` |
| `lago_c20261101` | 2026-11-01 | lago_ohlcv_1d 0, lago_ohlcv_1h 0, lago_rates_quotes 15363, lago_performance 0 | lago_ohlcv_1d, lago_ohlcv_1h, lago_performance | lago_rates_quotes: campo del lago | `sha256:cce80ad2bb82374e...` |
| `lago_cierre_c20261101` | 2026-11-01 | lago_ohlcv_1d 14448, lago_ohlcv_1h 6651, lago_rates_quotes 15363, lago_performance 0 | lago_performance | lago_ohlcv_1d: proxy por default_lag_ms; lago_ohlcv_1h: proxy por default_lag_ms; lago_rates_quotes: campo del lago | `sha256:aff96e6cb64296f1...` |
| `lago_c20261107` | 2026-11-07 | lago_ohlcv_1d 14560, lago_ohlcv_1h 9978, lago_rates_quotes 16289, lago_performance 6592 | ninguna | lago_ohlcv_1d: campo del lago; lago_ohlcv_1h: campo del lago; lago_rates_quotes: campo del lago; lago_performance: campo del lago | `sha256:853d8e8a111005d8...` |

## Dataset `binance_c20261101`

- Corte (`--corte`): **2026-11-01** (2026-11-01T00:00:00Z); `dataset_hash` `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744`.
- Fecha de la ejecucion (UTC): 2026-11-09T01:03:36Z; duracion 31.0 s; zona del mercado `UTC`.
- Comando exacto: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --binance --corte 2026-11-01 --nombre binance_c20261101 --sobrescribir`

- Fuente `binance__klines_1d` (TI-13-PUB, clase D-11 `real`, licencia CC BY-NC-SA 4.0): sha256 del dataset `586cf9f0e2d8e0a51fa9aeedbb85e1dfc1b8605e8adb468de17f0a9f8b8e5561`, descarga 2026-11-08T10:24:52Z, parquet `adaptadores.train.parquet` `1ff49bfbde6a241f...` (30406 filas).
- Fuente `binance__klines_1h` (TI-13-PUB, clase D-11 `real`, licencia CC BY-NC-SA 4.0): sha256 del dataset `8ceda17e11e6a442211d33697673820dcb7e394b0ed3d5f2e919a333373776b4`, descarga 2026-11-08T10:45:23Z, parquet `adaptadores.train.parquet` `8abb105833b48e7f...` (389813 filas).

| tabla | esquema | instrumentos | frecuencias | primera | ultima | filas | logical_hash |
|---|---|---|---|---|---|---|---|
| `binance_ohlcv_1d` | ohlcv/v1 | 10 | 1 d | 2017-08-17T00:00:00Z | 2026-10-31T00:00:00Z | 30336 | `sha256:cc4e7be3736b289a111c04cf02e0cc2eb6a31e4dbf706dd6238abc4f66cfbea5` |
| `binance_ohlcv_1h` | ohlcv/v1 | 5 | 1 h | 2017-08-17T04:00:00Z | 2026-10-31T23:00:00Z | 388973 | `sha256:89a7ca387058c5db80068a836bc4b4b52cbd8743f30fbd959f9529fc5f1e1251` |

### Reproducibilidad

- Segunda exportacion con el mismo origen y corte (2026-11-09T01:04:34Z): `dataset_hash` `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744` -> **igual**; manifest, parquet y procedencia **byte a byte identicos**.
- Comando de la repeticion: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --binance --corte 2026-11-01 --nombre binance_c20261101 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA/deuda/repeticion --repeticion`

### Limpieza

- `binance_ohlcv_1d`: 30406 filas de origen = 30336 finales + 70 excluidas (posterior_al_corte_por_fecha 70).
  - Ejemplos de filas excluidas: posterior_al_corte_por_fecha: [{'instrument': 'BTCUSDT', 'ts_ms': 1793491200000}, {'instrument': 'BTCUSDT', 'ts_ms': 1793577600000}].
  - Barras con volumen 0 (se conservan): 0.
  - Huecos (no se rellenan): 0 huecos, 0 barras ausentes, mayor 0 barras seguidas; 0 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
- `binance_ohlcv_1h`: 389813 filas de origen = 388973 finales + 840 excluidas (posterior_al_corte_por_fecha 840).
  - Ejemplos de filas excluidas: posterior_al_corte_por_fecha: [{'instrument': 'BTCUSDT', 'ts_ms': 1793491200000}, {'instrument': 'BTCUSDT', 'ts_ms': 1793494800000}].
  - Barras con volumen 0 (se conservan): 23.
  - Huecos (no se rellenan): 133 huecos, 548 barras ausentes, mayor 32 barras seguidas; 0 caen en el cierre semanal del FX.
  - Barras que no empiezan en la rejilla UTC de su intervalo (se conservan tal como las publica la fuente): 129 (BNBUSDT 43, BTCUSDT 43, ETHUSDT 43), entre 2018-02-09T09:28:14Z y 2018-02-11T03:28:15Z.

### Disponibilidad (`available_at_ms`)

- `binance_ohlcv_1d` [cierre declarado por la fuente]: por fila; campo: ts_ms + interval_ms (cierre de la vela). No es un proxy: es el cierre que declara la propia fuente. Cada kline de Binance trae su `close_time`, que vale apertura + intervalo - 1 ms; TI-13-PUB lo descarto y conserva solo la apertura. Se comprobo en el crudo (1640 zips de data.binance.vision, 420 219 klines): lo cumplen todos salvo 61 de 1 h, que cierran antes (el cierre declarado aqui es conservador en esas). Es el instante en que la vela deja de cambiar, no un instante de publicacion: no modela latencia de red ni de publicacion (un consumidor que la necesite debe aplicarla en su politica), y la fecha de descarga (2026-11-08) no sirve porque dejaria todo el historico fuera de cualquier corte anterior.
- `binance_ohlcv_1h` [cierre declarado por la fuente]: por fila; campo: ts_ms + interval_ms (cierre de la vela). No es un proxy: es el cierre que declara la propia fuente. Cada kline de Binance trae su `close_time`, que vale apertura + intervalo - 1 ms; TI-13-PUB lo descarto y conserva solo la apertura. Se comprobo en el crudo (1640 zips de data.binance.vision, 420 219 klines): lo cumplen todos salvo 61 de 1 h, que cierran antes (el cierre declarado aqui es conservador en esas). Es el instante en que la vela deja de cambiar, no un instante de publicacion: no modela latencia de red ni de publicacion (un consumidor que la necesite debe aplicarla en su politica), y la fecha de descarga (2026-11-08) no sirve porque dejaria todo el historico fuera de cualquier corte anterior.

### Validacion con `data_py` y look-ahead

- `data_py.vendor_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA")`: `dataset_hash` del motor `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744`, igual calculado aqui.
- `data_py.dataset_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA/binance_c20261101", True)`: tablas binance_ohlcv_1d (30336 filas, hash_verified=True), binance_ohlcv_1h (388973 filas, hash_verified=True).
- `data_py.availability_report_json(dir, table_id, "{}", "reject")` por tabla: binance_ohlcv_1d: declared 30336/30336, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; binance_ohlcv_1h: declared 388973/388973, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0.
- `data_py.verify_policy_json(mode=feed, policy={"availability": {"require_available_at": true}, "schema": "engine.data-policy", "timezone": {"require_declared": true}, "version": "v1"}, vendor_root="E:/quantdesk-lab/datasets/TI-02-DATA", dataset_id="binance_c20261101", revision_policy="reject")`: ok=True, violaciones: ninguna; report_hash `sha256:b939648033e79fb8cf9e59d006c5e743e98b2a8923a4ba8eb9b2ee7bb77b2b59`.
- Comprobacion propia sobre el parquet releido (esquema exacto de `data_py.table_schemas_json()`, orden, cierre y disponibilidad <= corte, disponibilidad >= cierre, revision 0): sin incidencias.
- Violaciones de look-ahead por fila: **0**; tablas no consumibles causalmente en sentido estricto: ninguna (de ellas, proxy por `default_lag_ms`: ninguna); tablas vacias tras el corte (ninguna fila cumple cierre y disponibilidad <= corte): ninguna.

### Universo y sesgo de supervivencia (D-07)

- binance: Pares USDT que existen hoy en Binance spot y entraron en TI-13-PUB (el universo de la fuente hoy, no el de una fecha pasada). No hay pares deslistados ni fechas de alta como miembro de un universo: sesgo de supervivencia declarado (D-07), sin tabla universe/v1 porque no se conocen altas ni bajas.

## Dataset `lago_c20261101`

- Corte (`--corte`): **2026-11-01** (2026-11-01T00:00:00Z); `dataset_hash` `sha256:cce80ad2bb82374e71a92ba27c4f9a89ad6ad0d7901697b853c15e24b39f70ea`.
- Fecha de la ejecucion (UTC): 2026-11-09T01:03:41Z; duracion 3.8 s; zona del mercado `UTC`.
- Comando exacto: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-01 --nombre lago_c20261101 --sobrescribir`

- Fuente lago de qn: base `http://192.168.1.48:8790/qn`, entorno `main`, rango pedido 2024-10-01 a 2026-11-07, volcado del 2026-11-08T20:02:46Z (223 ficheros), manifest sha256 `74ca1e9181d88dfb9e25180c0b31cf1fcf2a078bc0b1de67ef178b2cb4af4bf6`; `descarga_lago.py` sha256 `1989f121885c0ca3...` (python 3.12.3).
  - Paso 1, en mini con `QN_URLS`, `QN_TOKEN` y `QN_ENV=main` en el entorno: `python3 descarga_lago.py --desde 2024-10-01 --hasta 2026-11-07 --salida <directorio>`; despues se copia a `E:\quantdesk-lab\data\lago\2026-11-08` y el paso 2 es el comando exacto de arriba.

| tabla | esquema | instrumentos | frecuencias | primera | ultima | filas | logical_hash |
|---|---|---|---|---|---|---|---|
| `lago_ohlcv_1d` | ohlcv/v1 | 0 | eventos | - | - | 0 | `sha256:f0989bd1f6994e8c1562854f7e87da94d25865ec060a8e78c06c1f4805f44426` |
| `lago_ohlcv_1h` | ohlcv/v1 | 0 | eventos | - | - | 0 | `sha256:f0989bd1f6994e8c1562854f7e87da94d25865ec060a8e78c06c1f4805f44426` |
| `lago_rates_quotes` | custom/v1 | 103 | eventos | 2014-01-28T00:00:00Z | 2026-10-23T00:00:00Z | 15363 | `sha256:68d305523929e1aa4ad0c75f7a730ad2591910d1ba7a0f5f7f727a10169df17c` |
| `lago_performance` | custom/v1 | 0 | eventos | - | - | 0 | `sha256:588e7628f965154833d6400ec8305ec9740ad24dd66071d0f471c5bc73921ca9` |

### Reproducibilidad

- Segunda exportacion con el mismo origen y corte (2026-11-09T01:04:39Z): `dataset_hash` `sha256:cce80ad2bb82374e71a92ba27c4f9a89ad6ad0d7901697b853c15e24b39f70ea` -> **igual**; manifest, parquet y procedencia **byte a byte identicos**.
- Comando de la repeticion: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-01 --nombre lago_c20261101 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA/deuda/repeticion --repeticion`

### Limpieza

- `lago_ohlcv_1d`: 14769 filas de origen = 0 finales + 14769 excluidas (posterior_al_corte_por_disponibilidad 14448, posterior_al_corte_por_fecha 140, version_en_curso 181).
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'EURUSD', 'ts_ms': 1730419200000}, {'instrument': 'EURUSD', 'ts_ms': 1730678400000}]; posterior_al_corte_por_fecha: [{'instrument': 'EURUSD', 'ts_ms': 1793577600000}, {'instrument': 'USDJPY', 'ts_ms': 1793577600000}]; version_en_curso: [{'instrument': 'AUDCAD', 'ts_ms': 1793577600000}, {'instrument': 'AUDCAD', 'ts_ms': 1793664000000}].
  - Barras con volumen 0 (se conservan): 0.
  - Huecos (no se rellenan): 0 huecos, 0 barras ausentes, mayor 0 barras seguidas; 0 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
  - Campo `date` frente a `_ts` (se usa `_ts`): 14769 filas con `date`, 0 cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) {'0': 14769}; ejemplos [].
  - `_recv_ts` presente en 14769 de 14769 filas, entre 2026-11-01T23:02:23Z y 2026-11-07T23:01:15Z, anterior a `_ts` en 2; `_ts` con resolucion inferior al ms en 0.
- `lago_ohlcv_1h`: 15893 filas de origen = 0 finales + 15893 excluidas (posterior_al_corte_por_disponibilidad 6651, posterior_al_corte_por_fecha 3327, version_en_curso 2340, version_posterior_descartada 3575).
  - Versiones repetidas de una misma barra o dato (version_posterior_descartada): 3575 descartadas, 255 con valores distintos de la conservada, diferencia relativa maxima de `close` 0.00112.
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'EURUSD', 'ts_ms': 1792364400000}, {'instrument': 'EURUSD', 'ts_ms': 1792368000000}]; posterior_al_corte_por_fecha: [{'instrument': 'EURUSD', 'ts_ms': 1793577600000}, {'instrument': 'USDJPY', 'ts_ms': 1793577600000}]; version_en_curso: [{'instrument': 'AUDCAD', 'ts_ms': 1793577600000}, {'instrument': 'AUDCAD', 'ts_ms': 1793581200000}]; version_posterior_descartada: [{'instrument': 'USDJPY', 'ts_ms': 1792414800000}, {'instrument': 'USDJPY', 'ts_ms': 1792656000000}].
  - Barras con volumen 0 (se conservan): 0.
  - Huecos (no se rellenan): 0 huecos, 0 barras ausentes, mayor 0 barras seguidas; 0 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
  - Campo `date` frente a `_ts` (se usa `_ts`): 15893 filas con `date`, 140 cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) {'0': 12511, '3600': 3382}; ejemplos [{'instrument': 'AUDCAD', '_ts': '2026-10-18T23:00:00Z', 'date': '2026-10-19'}, {'instrument': 'AUDCAD', '_ts': '2026-10-19T23:00:00Z', 'date': '2026-10-20'}, {'instrument': 'AUDCAD', '_ts': '2026-10-20T23:00:00Z', 'date': '2026-10-21'}].
  - `_recv_ts` presente en 15893 de 15893 filas, entre 2026-11-01T03:01:49Z y 2026-11-08T04:00:56Z, anterior a `_ts` en 0; `_ts` con resolucion inferior al ms en 0.
  - Mayor cambio de `close` entre la primera y la ultima version recibida con la barra ya cerrada, en una barra del dataset: CADCHF 1 h 2026-10-23T16:00:00Z pasa de 0.58912 (recibida 2026-11-01T03:02:08Z) a 0.58906 (recibida 2026-11-04T05:01:04Z), 0.01%. Es una revision de un valor ya cerrado: el valor que llega despues no es el visible al cierre.
  - Causa del desfase de 3600 s: aparece solo en `_ts` de 2026-10-18T23:00:00Z a 2026-10-23T21:00:00Z y vale 0 de 2026-10-26T00:00:00Z en adelante; el horario de verano britanico (BST) acabo el 2026-10-25. `date` es la hora local de Londres escrita como si fuera UTC (los cambios de dia son las barras de las 00:00 de Londres, que en BST son las 23:00 UTC del dia anterior) y `_ts` es el instante UTC correcto: se usa `_ts`.
- `lago_rates_quotes`: 18128 filas de origen = 15363 finales + 2765 excluidas (posterior_al_corte_por_disponibilidad 462, posterior_al_corte_por_fecha 464, version_posterior_descartada 1839).
  - Versiones repetidas de una misma barra o dato (version_posterior_descartada): 1839 descartadas, 507 con valores distintos de la conservada.
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'EUR.IBOR.1Y', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793318400000}, {'instrument': 'EUR.IBOR.1Y', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793232000000}]; posterior_al_corte_por_fecha: [{'instrument': 'EUR.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793577600000}, {'instrument': 'EUR.IBOR.1Y', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793664000000}]; version_posterior_descartada: [{'instrument': 'EUR.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1764806400000}, {'instrument': 'USD.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1764806400000}].
  - Huecos de dias naturales entre eventos (no se rellenan): 3086 huecos, 19980 dias sin evento.
  - Filas sin campo de disponibilidad: 0; con `_ts` distinto del campo de disponibilidad: 0; con `_ts` igual a la medianoche de la fecha del dato: 0; disponibilidad entre 2025-12-04T08:33:44Z y 2026-11-06T21:07:16Z.
  - Cotizaciones fechadas (`valuation_date`) mas de un ano antes de leerse: AUD.OIS.BBSW_3M (20 filas de 2014, 1 valor(es) entre 0.0245 y 0.0245); CHF.IBOR.6Y (20 filas de 2025, 12 valor(es) entre 0.00368 y 0.00797); CHF.OIS.SARON_3M (20 filas de 2021, 1 valor(es) entre 1.0072 y 1.0072); CHF.OIS.SARON_FUT_3M (40 filas de 2021, 1 valor(es) entre 1.0072 y 1.0072). Las de un unico valor repetido son cotizaciones congeladas de la fuente; el scraper lee todas a partir de 2025-12 y se fechan por `valuation_date` (por eso el rango llega a 2014, aunque el inventario TI-01-INV las fechaba por `_ts`, la lectura) y su disponibilidad es la lectura, asi que no hay look-ahead. Se conservan tal cual.
  - Un 1,0072 en SARON no parece un tipo (1 %) sino un precio de futuro dividido entre 100; se conserva sin corregir y quien use estas series debe tratarlo como sospechoso.
- `lago_performance`: 6656 filas de origen = 0 finales + 6656 excluidas (posterior_al_corte_por_disponibilidad 6400, posterior_al_corte_por_fecha 256).
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'NZD.D', 'custom_type': 'market.performance', 'ts_ms': 1764806400000}, {'instrument': 'EUR.D', 'custom_type': 'market.performance', 'ts_ms': 1764806400000}]; posterior_al_corte_por_fecha: [{'instrument': 'AUD.D', 'custom_type': 'market.performance', 'ts_ms': 1793664000000}, {'instrument': 'CAD.D', 'custom_type': 'market.performance', 'ts_ms': 1793664000000}].
  - Huecos de dias naturales entre eventos (no se rellenan): 0 huecos, 0 dias sin evento.
  - Filas sin campo de disponibilidad: 0; con `_ts` distinto del campo de disponibilidad: 6656; con `_ts` igual a la medianoche de la fecha del dato: 6400; disponibilidad entre 2026-11-03T15:50:11Z y 2026-11-07T00:00:46Z.

### Disponibilidad (`available_at_ms`)

- `lago_ohlcv_1d` [campo del lago]: por fila; campo: _recv_ts (instante en que qn recibio la version elegida de la barra). El productor (market_scrapper/qn_sink.py, quantdesk-backend) pone en `_ts` el inicio de la barra de yfinance y no guarda ningun instante de publicacion; el unico instante en que el dato existia en el sistema es `_recv_ts` (recepcion en qn). Las barras se republican mientras estan abiertas, asi que se conserva la primera version recibida con `_recv_ts` >= cierre de la barra (inicio + intervalo) y se declara su `_recv_ts` como disponibilidad. Es conservador: un relleno historico queda disponible desde la fecha del relleno, nunca antes.
- `lago_ohlcv_1h` [campo del lago]: por fila; campo: _recv_ts (instante en que qn recibio la version elegida de la barra). El productor (market_scrapper/qn_sink.py, quantdesk-backend) pone en `_ts` el inicio de la barra de yfinance y no guarda ningun instante de publicacion; el unico instante en que el dato existia en el sistema es `_recv_ts` (recepcion en qn). Las barras se republican mientras estan abiertas, asi que se conserva la primera version recibida con `_recv_ts` >= cierre de la barra (inicio + intervalo) y se declara su `_recv_ts` como disponibilidad. Es conservador: un relleno historico queda disponible desde la fecha del relleno, nunca antes.
- `lago_rates_quotes` [campo del lago]: por fila; campo: scraped_at_ms. `scraped_at_ms` es el instante (ms) en que el scraper leyo la cotizacion (market_scrapper/qn_sink.py::rates_item; `_ts` vale lo mismo). `valuation_date` es la fecha a la que se refiere la cotizacion y fija `ts_ms` (00:00 UTC). Una fecha de valoracion puede volver a leerse otro dia: se conserva la primera lectura.
- `lago_performance` [campo del lago]: por fila; campo: _recv_ts. El productor (market_scrapper/market_sink.py::publish_performance) pretende poner en `_ts` el instante de la lectura, pero en el volcado real `_ts` es la medianoche de `date` en casi todas las filas (el historico se cargo con esa marca; ver `filas_con__ts_igual_a_la_fecha`): no es un instante de captura y declararla como disponibilidad adelantaria cada rendimiento diario a las 00:00 del propio dia. Solo `_recv_ts` (recepcion en qn) esta respaldado, asi que es la disponibilidad; `date` fija `ts_ms` (00:00 UTC). Una fecha puede volver a leerse otro dia: se conserva la primera lectura.

### Validacion con `data_py` y look-ahead

- `data_py.vendor_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA")`: `dataset_hash` del motor `sha256:cce80ad2bb82374e71a92ba27c4f9a89ad6ad0d7901697b853c15e24b39f70ea`, igual calculado aqui.
- `data_py.dataset_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA/lago_c20261101", True)`: tablas lago_ohlcv_1d (0 filas, hash_verified=True), lago_ohlcv_1h (0 filas, hash_verified=True), lago_rates_quotes (15363 filas, hash_verified=True), lago_performance (0 filas, hash_verified=True).
- `data_py.availability_report_json(dir, table_id, "{}", "reject")` por tabla: lago_ohlcv_1d: declared 0/0, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_ohlcv_1h: declared 0/0, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_rates_quotes: declared 15363/15363, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_performance: declared 0/0, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0.
- `data_py.verify_policy_json(mode=feed, policy={"availability": {"require_available_at": true}, "schema": "engine.data-policy", "timezone": {"require_declared": true}, "version": "v1"}, vendor_root="E:/quantdesk-lab/datasets/TI-02-DATA", dataset_id="lago_c20261101", revision_policy="reject")`: ok=True, violaciones: ninguna; report_hash `sha256:cccf7424d0cefbcbcb6e0d6f219c5b96d33eec22db34147518bea5c8563f0074`.
- Comprobacion propia sobre el parquet releido (esquema exacto de `data_py.table_schemas_json()`, orden, cierre y disponibilidad <= corte, disponibilidad >= cierre, revision 0): sin incidencias.
- Violaciones de look-ahead por fila: **0**; tablas no consumibles causalmente en sentido estricto: ninguna (de ellas, proxy por `default_lag_ms`: ninguna); tablas vacias tras el corte (ninguna fila cumple cierre y disponibilidad <= corte): ['lago_ohlcv_1d', 'lago_ohlcv_1h', 'lago_performance'].

### Universo y sesgo de supervivencia (D-07)

- lago: Los instrumentos que listaba /latest de qn en la fecha de la descarga: lo que hay hoy en la fuente, sin fechas de alta ni de baja y sin deslistados ni instrumentos retirados. Sesgo de supervivencia declarado (D-07); no se escribe tabla universe/v1 porque no se conocen altas ni bajas.

## Dataset `lago_cierre_c20261101`

- Corte (`--corte`): **2026-11-01** (2026-11-01T00:00:00Z); `dataset_hash` `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356`.
- Fecha de la ejecucion (UTC): 2026-11-09T01:03:50Z; duracion 7.8 s; zona del mercado `UTC`.
- Comando exacto: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-01 --disponibilidad-ohlcv cierre --nombre lago_cierre_c20261101 --sobrescribir`

- Fuente lago de qn: base `http://192.168.1.48:8790/qn`, entorno `main`, rango pedido 2024-10-01 a 2026-11-07, volcado del 2026-11-08T20:02:46Z (223 ficheros), manifest sha256 `74ca1e9181d88dfb9e25180c0b31cf1fcf2a078bc0b1de67ef178b2cb4af4bf6`; `descarga_lago.py` sha256 `1989f121885c0ca3...` (python 3.12.3).
  - Paso 1, en mini con `QN_URLS`, `QN_TOKEN` y `QN_ENV=main` en el entorno: `python3 descarga_lago.py --desde 2024-10-01 --hasta 2026-11-07 --salida <directorio>`; despues se copia a `E:\quantdesk-lab\data\lago\2026-11-08` y el paso 2 es el comando exacto de arriba.

| tabla | esquema | instrumentos | frecuencias | primera | ultima | filas | logical_hash |
|---|---|---|---|---|---|---|---|
| `lago_ohlcv_1d` | ohlcv/v1 | 28 | 1 d | 2024-11-01T00:00:00Z | 2026-10-30T00:00:00Z | 14448 | `sha256:640959ade547195c4913a0db2b3f4852fc3ce94e0d97ac75e3ad0db31108f575` |
| `lago_ohlcv_1h` | ohlcv/v1 | 28 | 1 h | 2026-10-18T23:00:00Z | 2026-10-30T23:00:00Z | 6651 | `sha256:da1944984256babd7ae5fc9eab88d999f61d8fbb16d60570585825c6e0a0648a` |
| `lago_rates_quotes` | custom/v1 | 103 | eventos | 2014-01-28T00:00:00Z | 2026-10-23T00:00:00Z | 15363 | `sha256:68d305523929e1aa4ad0c75f7a730ad2591910d1ba7a0f5f7f727a10169df17c` |
| `lago_performance` | custom/v1 | 0 | eventos | - | - | 0 | `sha256:588e7628f965154833d6400ec8305ec9740ad24dd66071d0f471c5bc73921ca9` |

### Reproducibilidad

- Segunda exportacion con el mismo origen y corte (2026-11-09T01:04:46Z): `dataset_hash` `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356` -> **igual**; manifest, parquet y procedencia **byte a byte identicos**.
- Comando de la repeticion: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-01 --disponibilidad-ohlcv cierre --nombre lago_cierre_c20261101 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA/deuda/repeticion --repeticion`

### Limpieza

- `lago_ohlcv_1d`: 14769 filas de origen = 14448 finales + 321 excluidas (posterior_al_corte_por_fecha 140, version_en_curso 181).
  - Ejemplos de filas excluidas: posterior_al_corte_por_fecha: [{'instrument': 'EURUSD', 'ts_ms': 1793577600000}, {'instrument': 'USDJPY', 'ts_ms': 1793577600000}]; version_en_curso: [{'instrument': 'AUDCAD', 'ts_ms': 1793577600000}, {'instrument': 'AUDCAD', 'ts_ms': 1793664000000}].
  - Barras con volumen 0 (se conservan): 14448.
  - Huecos (no se rellenan): 2996 huecos, 5964 barras ausentes, mayor 4 barras seguidas; 2884 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
  - Campo `date` frente a `_ts` (se usa `_ts`): 14769 filas con `date`, 0 cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) {'0': 14769}; ejemplos [].
  - `_recv_ts` presente en 14769 de 14769 filas, entre 2026-11-01T23:02:23Z y 2026-11-07T23:01:15Z, anterior a `_ts` en 2; `_ts` con resolucion inferior al ms en 0.
  - Barras con open o close fuera de [low, high] (se conservan, no se corrigen): 604; desvio relativo al cierre, mediana 9.78e-05 y maximo 0.00469.
- `lago_ohlcv_1h`: 15893 filas de origen = 6651 finales + 9242 excluidas (posterior_al_corte_por_fecha 3327, version_en_curso 2340, version_posterior_descartada 3575).
  - Versiones repetidas de una misma barra o dato (version_posterior_descartada): 3575 descartadas, 255 con valores distintos de la conservada, diferencia relativa maxima de `close` 0.00112.
  - Ejemplos de filas excluidas: posterior_al_corte_por_fecha: [{'instrument': 'EURUSD', 'ts_ms': 1793577600000}, {'instrument': 'USDJPY', 'ts_ms': 1793577600000}]; version_en_curso: [{'instrument': 'AUDCAD', 'ts_ms': 1793577600000}, {'instrument': 'AUDCAD', 'ts_ms': 1793581200000}]; version_posterior_descartada: [{'instrument': 'USDJPY', 'ts_ms': 1792414800000}, {'instrument': 'USDJPY', 'ts_ms': 1792656000000}].
  - Barras con volumen 0 (se conservan): 6651.
  - Huecos (no se rellenan): 43 huecos, 1416 barras ausentes, mayor 51 barras seguidas; 15 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
  - Campo `date` frente a `_ts` (se usa `_ts`): 15893 filas con `date`, 140 cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) {'0': 12511, '3600': 3382}; ejemplos [{'instrument': 'AUDCAD', '_ts': '2026-10-18T23:00:00Z', 'date': '2026-10-19'}, {'instrument': 'AUDCAD', '_ts': '2026-10-19T23:00:00Z', 'date': '2026-10-20'}, {'instrument': 'AUDCAD', '_ts': '2026-10-20T23:00:00Z', 'date': '2026-10-21'}].
  - `_recv_ts` presente en 15893 de 15893 filas, entre 2026-11-01T03:01:49Z y 2026-11-08T04:00:56Z, anterior a `_ts` en 0; `_ts` con resolucion inferior al ms en 0.
  - Mayor cambio de `close` entre la primera y la ultima version recibida con la barra ya cerrada, en una barra del dataset: CADCHF 1 h 2026-10-23T16:00:00Z pasa de 0.58912 (recibida 2026-11-01T03:02:08Z) a 0.58906 (recibida 2026-11-04T05:01:04Z), 0.01%. Es una revision de un valor ya cerrado: el valor que llega despues no es el visible al cierre.
  - Causa del desfase de 3600 s: aparece solo en `_ts` de 2026-10-18T23:00:00Z a 2026-10-23T21:00:00Z y vale 0 de 2026-10-26T00:00:00Z en adelante; el horario de verano britanico (BST) acabo el 2026-10-25. `date` es la hora local de Londres escrita como si fuera UTC (los cambios de dia son las barras de las 00:00 de Londres, que en BST son las 23:00 UTC del dia anterior) y `_ts` es el instante UTC correcto: se usa `_ts`.
- `lago_rates_quotes`: 18128 filas de origen = 15363 finales + 2765 excluidas (posterior_al_corte_por_disponibilidad 462, posterior_al_corte_por_fecha 464, version_posterior_descartada 1839).
  - Versiones repetidas de una misma barra o dato (version_posterior_descartada): 1839 descartadas, 507 con valores distintos de la conservada.
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'EUR.IBOR.1Y', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793318400000}, {'instrument': 'EUR.IBOR.1Y', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793232000000}]; posterior_al_corte_por_fecha: [{'instrument': 'EUR.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793577600000}, {'instrument': 'EUR.IBOR.1Y', 'custom_type': 'market.rates.quotes', 'ts_ms': 1793664000000}]; version_posterior_descartada: [{'instrument': 'EUR.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1764806400000}, {'instrument': 'USD.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1764806400000}].
  - Huecos de dias naturales entre eventos (no se rellenan): 3086 huecos, 19980 dias sin evento.
  - Filas sin campo de disponibilidad: 0; con `_ts` distinto del campo de disponibilidad: 0; con `_ts` igual a la medianoche de la fecha del dato: 0; disponibilidad entre 2025-12-04T08:33:44Z y 2026-11-06T21:07:16Z.
  - Cotizaciones fechadas (`valuation_date`) mas de un ano antes de leerse: AUD.OIS.BBSW_3M (20 filas de 2014, 1 valor(es) entre 0.0245 y 0.0245); CHF.IBOR.6Y (20 filas de 2025, 12 valor(es) entre 0.00368 y 0.00797); CHF.OIS.SARON_3M (20 filas de 2021, 1 valor(es) entre 1.0072 y 1.0072); CHF.OIS.SARON_FUT_3M (40 filas de 2021, 1 valor(es) entre 1.0072 y 1.0072). Las de un unico valor repetido son cotizaciones congeladas de la fuente; el scraper lee todas a partir de 2025-12 y se fechan por `valuation_date` (por eso el rango llega a 2014, aunque el inventario TI-01-INV las fechaba por `_ts`, la lectura) y su disponibilidad es la lectura, asi que no hay look-ahead. Se conservan tal cual.
  - Un 1,0072 en SARON no parece un tipo (1 %) sino un precio de futuro dividido entre 100; se conserva sin corregir y quien use estas series debe tratarlo como sospechoso.
- `lago_performance`: 6656 filas de origen = 0 finales + 6656 excluidas (posterior_al_corte_por_disponibilidad 6400, posterior_al_corte_por_fecha 256).
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'NZD.D', 'custom_type': 'market.performance', 'ts_ms': 1764806400000}, {'instrument': 'EUR.D', 'custom_type': 'market.performance', 'ts_ms': 1764806400000}]; posterior_al_corte_por_fecha: [{'instrument': 'AUD.D', 'custom_type': 'market.performance', 'ts_ms': 1793664000000}, {'instrument': 'CAD.D', 'custom_type': 'market.performance', 'ts_ms': 1793664000000}].
  - Huecos de dias naturales entre eventos (no se rellenan): 0 huecos, 0 dias sin evento.
  - Filas sin campo de disponibilidad: 0; con `_ts` distinto del campo de disponibilidad: 6656; con `_ts` igual a la medianoche de la fecha del dato: 6400; disponibilidad entre 2026-11-03T15:50:11Z y 2026-11-07T00:00:46Z.

### Disponibilidad (`available_at_ms`)

- `lago_ohlcv_1d` [proxy por default_lag_ms]: por default_lag_ms = 0 (proxy, sin campo que la respalde); campo: ninguno: available_at_ms nulo y default_lag_ms = 0 en el manifest (cierre + 0). PROXY elegido con --disponibilidad-ohlcv cierre. Ningun campo del lago dice cuando se supo cada barra antes de que qn la recibiera: `_recv_ts` es la recepcion en qn, y qn se relleno con el historico de golpe (primer `_recv_ts` en la seccion de limpieza), asi que con ese campo no hay ninguna barra anterior a esa fecha. Por eso `available_at_ms` queda nulo y el manifest declara `default_lag_ms` = 0, el mecanismo del motor para 'disponible al cierre, sin evidencia' (el motor cuenta estas filas como `defaulted`, no `declared`). Los VALORES son la version que qn recibio DESPUES del corte, no la visible al cierre (ver el ejemplo de mayor diferencia entre versiones en la limpieza): el dataset NO es causal en sentido estricto. Para eso esta el dataset estricto, que usa `_recv_ts`.
- `lago_ohlcv_1h` [proxy por default_lag_ms]: por default_lag_ms = 0 (proxy, sin campo que la respalde); campo: ninguno: available_at_ms nulo y default_lag_ms = 0 en el manifest (cierre + 0). PROXY elegido con --disponibilidad-ohlcv cierre. Ningun campo del lago dice cuando se supo cada barra antes de que qn la recibiera: `_recv_ts` es la recepcion en qn, y qn se relleno con el historico de golpe (primer `_recv_ts` en la seccion de limpieza), asi que con ese campo no hay ninguna barra anterior a esa fecha. Por eso `available_at_ms` queda nulo y el manifest declara `default_lag_ms` = 0, el mecanismo del motor para 'disponible al cierre, sin evidencia' (el motor cuenta estas filas como `defaulted`, no `declared`). Los VALORES son la version que qn recibio DESPUES del corte, no la visible al cierre (ver el ejemplo de mayor diferencia entre versiones en la limpieza): el dataset NO es causal en sentido estricto. Para eso esta el dataset estricto, que usa `_recv_ts`.
- `lago_rates_quotes` [campo del lago]: por fila; campo: scraped_at_ms. `scraped_at_ms` es el instante (ms) en que el scraper leyo la cotizacion (market_scrapper/qn_sink.py::rates_item; `_ts` vale lo mismo). `valuation_date` es la fecha a la que se refiere la cotizacion y fija `ts_ms` (00:00 UTC). Una fecha de valoracion puede volver a leerse otro dia: se conserva la primera lectura.
- `lago_performance` [campo del lago]: por fila; campo: _recv_ts. El productor (market_scrapper/market_sink.py::publish_performance) pretende poner en `_ts` el instante de la lectura, pero en el volcado real `_ts` es la medianoche de `date` en casi todas las filas (el historico se cargo con esa marca; ver `filas_con__ts_igual_a_la_fecha`): no es un instante de captura y declararla como disponibilidad adelantaria cada rendimiento diario a las 00:00 del propio dia. Solo `_recv_ts` (recepcion en qn) esta respaldado, asi que es la disponibilidad; `date` fija `ts_ms` (00:00 UTC). Una fecha puede volver a leerse otro dia: se conserva la primera lectura.

### Validacion con `data_py` y look-ahead

- `data_py.vendor_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA")`: `dataset_hash` del motor `sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356`, igual calculado aqui.
- `data_py.dataset_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA/lago_cierre_c20261101", True)`: tablas lago_ohlcv_1d (14448 filas, hash_verified=True), lago_ohlcv_1h (6651 filas, hash_verified=True), lago_rates_quotes (15363 filas, hash_verified=True), lago_performance (0 filas, hash_verified=True).
- `data_py.availability_report_json(dir, table_id, "{}", "reject")` por tabla: lago_ohlcv_1d: declared 0/14448, defaulted 14448, undeclared 0, violaciones DPOL-AVL-002 0; lago_ohlcv_1h: declared 0/6651, defaulted 6651, undeclared 0, violaciones DPOL-AVL-002 0; lago_rates_quotes: declared 15363/15363, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_performance: declared 0/0, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0.
- `data_py.verify_policy_json(mode=feed, policy={"availability": {"require_available_at": true}, "schema": "engine.data-policy", "timezone": {"require_declared": true}, "version": "v1"}, vendor_root="E:/quantdesk-lab/datasets/TI-02-DATA", dataset_id="lago_cierre_c20261101", revision_policy="reject")`: ok=False, violaciones: [('DPOL-AVL-001', 'error', None), ('DPOL-AVL-001', 'error', None)]; report_hash `sha256:e817a7ddbe30dca446c46cb3c1f5a9689ee6063a05e0590e43dbff01eb142b24`.
- Misma politica con `max_default_lag_ms` = 0 (admite el lag declarado): ok=True, violaciones ninguna. El DPOL-AVL-001 de arriba es el aviso de que esas filas son proxy y no estrictas.
- Comprobacion propia sobre el parquet releido (esquema exacto de `data_py.table_schemas_json()`, orden, cierre y disponibilidad <= corte, disponibilidad >= cierre, revision 0): sin incidencias.
- Violaciones de look-ahead por fila: **0**; tablas no consumibles causalmente en sentido estricto: ['lago_ohlcv_1d', 'lago_ohlcv_1h'] (de ellas, proxy por `default_lag_ms`: ['lago_ohlcv_1d', 'lago_ohlcv_1h']); tablas vacias tras el corte (ninguna fila cumple cierre y disponibilidad <= corte): ['lago_performance'].

### Universo y sesgo de supervivencia (D-07)

- lago: Los instrumentos que listaba /latest de qn en la fecha de la descarga: lo que hay hoy en la fuente, sin fechas de alta ni de baja y sin deslistados ni instrumentos retirados. Sesgo de supervivencia declarado (D-07); no se escribe tabla universe/v1 porque no se conocen altas ni bajas.

## Dataset `lago_c20261107`

- Corte (`--corte`): **2026-11-07** (2026-11-07T00:00:00Z); `dataset_hash` `sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495`.
- Fecha de la ejecucion (UTC): 2026-11-09T01:03:56Z; duracion 5.0 s; zona del mercado `UTC`.
- Comando exacto: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-07 --nombre lago_c20261107 --sobrescribir`

- Fuente lago de qn: base `http://192.168.1.48:8790/qn`, entorno `main`, rango pedido 2024-10-01 a 2026-11-07, volcado del 2026-11-08T20:02:46Z (223 ficheros), manifest sha256 `74ca1e9181d88dfb9e25180c0b31cf1fcf2a078bc0b1de67ef178b2cb4af4bf6`; `descarga_lago.py` sha256 `1989f121885c0ca3...` (python 3.12.3).
  - Paso 1, en mini con `QN_URLS`, `QN_TOKEN` y `QN_ENV=main` en el entorno: `python3 descarga_lago.py --desde 2024-10-01 --hasta 2026-11-07 --salida <directorio>`; despues se copia a `E:\quantdesk-lab\data\lago\2026-11-08` y el paso 2 es el comando exacto de arriba.

| tabla | esquema | instrumentos | frecuencias | primera | ultima | filas | logical_hash |
|---|---|---|---|---|---|---|---|
| `lago_ohlcv_1d` | ohlcv/v1 | 28 | 1 d | 2024-11-01T00:00:00Z | 2026-11-05T00:00:00Z | 14560 | `sha256:2447a3a888d3caf2beff2255eadbd9895939528bdd11f4b6bc67bd56a4bf3703` |
| `lago_ohlcv_1h` | ohlcv/v1 | 28 | 1 h | 2026-10-18T23:00:00Z | 2026-11-06T22:00:00Z | 9978 | `sha256:feb490460b8c2057c36700c25b6bb3c1756038c0edf3d2e4e8ad7a31a928973d` |
| `lago_rates_quotes` | custom/v1 | 103 | eventos | 2014-01-28T00:00:00Z | 2026-11-06T00:00:00Z | 16289 | `sha256:ca58cd06b1fcce51dfbca270863438915ca6685caf582ee862dd65a0a83ba5c4` |
| `lago_performance` | custom/v1 | 64 | eventos | 2025-12-04T00:00:00Z | 2026-11-05T00:00:00Z | 6592 | `sha256:5d75ae0b261dd406ac329edd3a3556d4c2a68a9f23e02c3f363c1459fcf32cde` |

### Reproducibilidad

- Segunda exportacion con el mismo origen y corte (2026-11-09T01:04:52Z): `dataset_hash` `sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495` -> **igual**; manifest, parquet y procedencia **byte a byte identicos**.
- Comando de la repeticion: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/2026-11-08 --corte 2026-11-07 --nombre lago_c20261107 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA/deuda/repeticion --repeticion`

### Limpieza

- `lago_ohlcv_1d`: 14769 filas de origen = 14560 finales + 209 excluidas (posterior_al_corte_por_disponibilidad 28, version_en_curso 181).
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'EURUSD', 'ts_ms': 1793923200000}, {'instrument': 'USDJPY', 'ts_ms': 1793923200000}]; version_en_curso: [{'instrument': 'AUDCAD', 'ts_ms': 1793577600000}, {'instrument': 'AUDCAD', 'ts_ms': 1793664000000}].
  - Barras con volumen 0 (se conservan): 14560.
  - Huecos (no se rellenan): 3024 huecos, 6020 barras ausentes, mayor 4 barras seguidas; 2912 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
  - Campo `date` frente a `_ts` (se usa `_ts`): 14769 filas con `date`, 0 cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) {'0': 14769}; ejemplos [].
  - `_recv_ts` presente en 14769 de 14769 filas, entre 2026-11-01T23:02:23Z y 2026-11-07T23:01:15Z, anterior a `_ts` en 2; `_ts` con resolucion inferior al ms en 0.
  - Barras con open o close fuera de [low, high] (se conservan, no se corrigen): 607; desvio relativo al cierre, mediana 9.7e-05 y maximo 0.00469.
  - Ninguna barra del dataset cambia de `close` entre versiones recibidas con la barra ya cerrada. La cifra siguiente incluye versiones recibidas con la barra todavia abierta, asi que mide la evolucion dentro de la barra y no una revision posterior al cierre: AUDCHF 1 d 2026-11-02T00:00:00Z pasa de 0.57289 (recibida 2026-11-02T23:04:41Z) a 0.579681 (recibida 2026-11-03T23:01:26Z), 1.19%.
- `lago_ohlcv_1h`: 15893 filas de origen = 9978 finales + 5915 excluidas (version_en_curso 2340, version_posterior_descartada 3575).
  - Versiones repetidas de una misma barra o dato (version_posterior_descartada): 3575 descartadas, 255 con valores distintos de la conservada, diferencia relativa maxima de `close` 0.00112.
  - Ejemplos de filas excluidas: version_en_curso: [{'instrument': 'AUDCAD', 'ts_ms': 1793577600000}, {'instrument': 'AUDCAD', 'ts_ms': 1793581200000}]; version_posterior_descartada: [{'instrument': 'USDJPY', 'ts_ms': 1792414800000}, {'instrument': 'USDJPY', 'ts_ms': 1792656000000}].
  - Barras con volumen 0 (se conservan): 9978.
  - Huecos (no se rellenan): 71 huecos, 2785 barras ausentes, mayor 51 barras seguidas; 15 caen en el cierre semanal del FX.
  - Todas las barras empiezan en la rejilla UTC de su intervalo.
  - Campo `date` frente a `_ts` (se usa `_ts`): 15893 filas con `date`, 140 cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) {'0': 12511, '3600': 3382}; ejemplos [{'instrument': 'AUDCAD', '_ts': '2026-10-18T23:00:00Z', 'date': '2026-10-19'}, {'instrument': 'AUDCAD', '_ts': '2026-10-19T23:00:00Z', 'date': '2026-10-20'}, {'instrument': 'AUDCAD', '_ts': '2026-10-20T23:00:00Z', 'date': '2026-10-21'}].
  - `_recv_ts` presente en 15893 de 15893 filas, entre 2026-11-01T03:01:49Z y 2026-11-08T04:00:56Z, anterior a `_ts` en 0; `_ts` con resolucion inferior al ms en 0.
  - Mayor cambio de `close` entre la primera y la ultima version recibida con la barra ya cerrada, en una barra del dataset: AUDJPY 1 h 2026-11-05T23:00:00Z pasa de 109.022 (recibida 2026-11-06T00:01:41Z) a 109.144 (recibida 2026-11-06T05:01:28Z), 0.11%. Es una revision de un valor ya cerrado: el valor que llega despues no es el visible al cierre.
  - Causa del desfase de 3600 s: aparece solo en `_ts` de 2026-10-18T23:00:00Z a 2026-10-23T21:00:00Z y vale 0 de 2026-10-26T00:00:00Z en adelante; el horario de verano britanico (BST) acabo el 2026-10-25. `date` es la hora local de Londres escrita como si fuera UTC (los cambios de dia son las barras de las 00:00 de Londres, que en BST son las 23:00 UTC del dia anterior) y `_ts` es el instante UTC correcto: se usa `_ts`.
- `lago_rates_quotes`: 18128 filas de origen = 16289 finales + 1839 excluidas (version_posterior_descartada 1839).
  - Versiones repetidas de una misma barra o dato (version_posterior_descartada): 1839 descartadas, 507 con valores distintos de la conservada.
  - Ejemplos de filas excluidas: version_posterior_descartada: [{'instrument': 'EUR.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1764806400000}, {'instrument': 'USD.OIS.ON', 'custom_type': 'market.rates.quotes', 'ts_ms': 1764806400000}].
  - Huecos de dias naturales entre eventos (no se rellenan): 3274 huecos, 20372 dias sin evento.
  - Filas sin campo de disponibilidad: 0; con `_ts` distinto del campo de disponibilidad: 0; con `_ts` igual a la medianoche de la fecha del dato: 0; disponibilidad entre 2025-12-04T08:33:44Z y 2026-11-06T21:07:16Z.
  - Cotizaciones fechadas (`valuation_date`) mas de un ano antes de leerse: AUD.OIS.BBSW_3M (20 filas de 2014, 1 valor(es) entre 0.0245 y 0.0245); CHF.IBOR.6Y (20 filas de 2025, 12 valor(es) entre 0.00368 y 0.00797); CHF.OIS.SARON_3M (20 filas de 2021, 1 valor(es) entre 1.0072 y 1.0072); CHF.OIS.SARON_FUT_3M (40 filas de 2021, 1 valor(es) entre 1.0072 y 1.0072). Las de un unico valor repetido son cotizaciones congeladas de la fuente; el scraper lee todas a partir de 2025-12 y se fechan por `valuation_date` (por eso el rango llega a 2014, aunque el inventario TI-01-INV las fechaba por `_ts`, la lectura) y su disponibilidad es la lectura, asi que no hay look-ahead. Se conservan tal cual.
  - Un 1,0072 en SARON no parece un tipo (1 %) sino un precio de futuro dividido entre 100; se conserva sin corregir y quien use estas series debe tratarlo como sospechoso.
- `lago_performance`: 6656 filas de origen = 6592 finales + 64 excluidas (posterior_al_corte_por_disponibilidad 64).
  - Ejemplos de filas excluidas: posterior_al_corte_por_disponibilidad: [{'instrument': 'AUD.D', 'custom_type': 'market.performance', 'ts_ms': 1794009600000}, {'instrument': 'CAD.D', 'custom_type': 'market.performance', 'ts_ms': 1794009600000}].
  - Huecos de dias naturales entre eventos (no se rellenan): 1664 huecos, 14976 dias sin evento.
  - Filas sin campo de disponibilidad: 0; con `_ts` distinto del campo de disponibilidad: 6656; con `_ts` igual a la medianoche de la fecha del dato: 6400; disponibilidad entre 2026-11-03T15:50:11Z y 2026-11-07T00:00:46Z.

### Disponibilidad (`available_at_ms`)

- `lago_ohlcv_1d` [campo del lago]: por fila; campo: _recv_ts (instante en que qn recibio la version elegida de la barra). El productor (market_scrapper/qn_sink.py, quantdesk-backend) pone en `_ts` el inicio de la barra de yfinance y no guarda ningun instante de publicacion; el unico instante en que el dato existia en el sistema es `_recv_ts` (recepcion en qn). Las barras se republican mientras estan abiertas, asi que se conserva la primera version recibida con `_recv_ts` >= cierre de la barra (inicio + intervalo) y se declara su `_recv_ts` como disponibilidad. Es conservador: un relleno historico queda disponible desde la fecha del relleno, nunca antes.
- `lago_ohlcv_1h` [campo del lago]: por fila; campo: _recv_ts (instante en que qn recibio la version elegida de la barra). El productor (market_scrapper/qn_sink.py, quantdesk-backend) pone en `_ts` el inicio de la barra de yfinance y no guarda ningun instante de publicacion; el unico instante en que el dato existia en el sistema es `_recv_ts` (recepcion en qn). Las barras se republican mientras estan abiertas, asi que se conserva la primera version recibida con `_recv_ts` >= cierre de la barra (inicio + intervalo) y se declara su `_recv_ts` como disponibilidad. Es conservador: un relleno historico queda disponible desde la fecha del relleno, nunca antes.
- `lago_rates_quotes` [campo del lago]: por fila; campo: scraped_at_ms. `scraped_at_ms` es el instante (ms) en que el scraper leyo la cotizacion (market_scrapper/qn_sink.py::rates_item; `_ts` vale lo mismo). `valuation_date` es la fecha a la que se refiere la cotizacion y fija `ts_ms` (00:00 UTC). Una fecha de valoracion puede volver a leerse otro dia: se conserva la primera lectura.
- `lago_performance` [campo del lago]: por fila; campo: _recv_ts. El productor (market_scrapper/market_sink.py::publish_performance) pretende poner en `_ts` el instante de la lectura, pero en el volcado real `_ts` es la medianoche de `date` en casi todas las filas (el historico se cargo con esa marca; ver `filas_con__ts_igual_a_la_fecha`): no es un instante de captura y declararla como disponibilidad adelantaria cada rendimiento diario a las 00:00 del propio dia. Solo `_recv_ts` (recepcion en qn) esta respaldado, asi que es la disponibilidad; `date` fija `ts_ms` (00:00 UTC). Una fecha puede volver a leerse otro dia: se conserva la primera lectura.

### Validacion con `data_py` y look-ahead

- `data_py.vendor_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA")`: `dataset_hash` del motor `sha256:853d8e8a111005d87836732266d800bb52a44f200eaba3599440d91b555c1495`, igual calculado aqui.
- `data_py.dataset_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA/lago_c20261107", True)`: tablas lago_ohlcv_1d (14560 filas, hash_verified=True), lago_ohlcv_1h (9978 filas, hash_verified=True), lago_rates_quotes (16289 filas, hash_verified=True), lago_performance (6592 filas, hash_verified=True).
- `data_py.availability_report_json(dir, table_id, "{}", "reject")` por tabla: lago_ohlcv_1d: declared 14560/14560, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_ohlcv_1h: declared 9978/9978, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_rates_quotes: declared 16289/16289, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0; lago_performance: declared 6592/6592, defaulted 0, undeclared 0, violaciones DPOL-AVL-002 0.
- `data_py.verify_policy_json(mode=feed, policy={"availability": {"require_available_at": true}, "schema": "engine.data-policy", "timezone": {"require_declared": true}, "version": "v1"}, vendor_root="E:/quantdesk-lab/datasets/TI-02-DATA", dataset_id="lago_c20261107", revision_policy="reject")`: ok=True, violaciones: ninguna; report_hash `sha256:3a1923340945453e7ee8049fbca9f0e8bbd9c06d90f7336f940d1fb4e0458769`.
- Comprobacion propia sobre el parquet releido (esquema exacto de `data_py.table_schemas_json()`, orden, cierre y disponibilidad <= corte, disponibilidad >= cierre, revision 0): sin incidencias.
- Violaciones de look-ahead por fila: **0**; tablas no consumibles causalmente en sentido estricto: ninguna (de ellas, proxy por `default_lag_ms`: ninguna); tablas vacias tras el corte (ninguna fila cumple cierre y disponibilidad <= corte): ninguna.

### Universo y sesgo de supervivencia (D-07)

- lago: Los instrumentos que listaba /latest de qn en la fecha de la descarga: lo que hay hoy en la fuente, sin fechas de alta ni de baja y sin deslistados ni instrumentos retirados. Sesgo de supervivencia declarado (D-07); no se escribe tabla universe/v1 porque no se conocen altas ni bajas.

## Lo que no se exporta

- Cadenas de opciones (`market.options.*`): vacias en el lago (TI-01-INV); TI-09-ARCH retirada.
- MT5 (TI-12-MT5, a la espera de la puerta 2) y los corpus genericos de TI-13-PUB (sin OHLCV real con fecha).
- De Binance: `quote_volume` y `n_trades`; `ohlcv/v1` no tiene donde ponerlos (`volume` es el volumen en activo base, `volume_kind` = `traded`). Tampoco `value`, que es igual a `close`.
- Del lago: el campo `date` (se usa `_ts`, ver el desfase arriba), `_clock_offset_ns` (nulo en todas las filas), `_batch_id`, `_cycle` y demas columnas de sistema.
- Ninguna tabla `universe/v1` ni `corporate_actions/v1`: no se conocen altas, bajas ni acciones corporativas, y `adjusted_by_vendor` queda en su valor por defecto (precios crudos).
