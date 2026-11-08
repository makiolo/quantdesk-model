# TI-02-DATA: informe del exportador a `engine.market-history/v1`

- Motor: quantdesk 69fdb39d; python 3.12.3, pyarrow 26.0.1, pandas 3.1.1, numpy 2.5.4.
- Generado por `exportar_market_history.py --informe` a partir de `procedencia.json` y del registro de cada ejecucion.
- Reglas: el corte es el instante `AAAA-MM-DDT00:00:00Z`; una fila entra solo si su cierre y su `available_at_ms` son menores o iguales; `default_lag_ms` queda nulo; los huecos no se rellenan; nada se descarta sin contarlo.

## Dataset `binance_c20261101`

- Corte (`--corte`): **2026-11-01** (2026-11-01T00:00:00Z); `dataset_hash` `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744`.
- Fecha de la ejecucion (UTC): 2026-11-08T19:59:01Z; duracion 24.5 s; zona del mercado `UTC`.
- Comando exacto: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --binance --corte 2026-11-01 --nombre binance_c20261101 --sobrescribir`

- Fuente `binance__klines_1d` (TI-13-PUB, clase D-11 `real`, licencia CC BY-NC-SA 4.0): sha256 del dataset `586cf9f0e2d8e0a51fa9aeedbb85e1dfc1b8605e8adb468de17f0a9f8b8e5561`, descarga 2026-11-08T10:24:52Z, parquet `adaptadores.train.parquet` `1ff49bfbde6a241f...` (30406 filas).
- Fuente `binance__klines_1h` (TI-13-PUB, clase D-11 `real`, licencia CC BY-NC-SA 4.0): sha256 del dataset `8ceda17e11e6a442211d33697673820dcb7e394b0ed3d5f2e919a333373776b4`, descarga 2026-11-08T10:45:23Z, parquet `adaptadores.train.parquet` `8abb105833b48e7f...` (389813 filas).

| tabla | esquema | instrumentos | frecuencias | primera | ultima | filas | logical_hash |
|---|---|---|---|---|---|---|---|
| `binance_ohlcv_1d` | ohlcv/v1 | 10 | 1 d | 2017-08-17T00:00:00Z | 2026-10-31T00:00:00Z | 30336 | `sha256:cc4e7be3736b289a111c04cf02e0cc2eb6a31e4dbf706dd6238abc4f66cfbea5` |
| `binance_ohlcv_1h` | ohlcv/v1 | 5 | 1 h | 2017-08-17T04:00:00Z | 2026-10-31T23:00:00Z | 388973 | `sha256:89a7ca387058c5db80068a836bc4b4b52cbd8743f30fbd959f9529fc5f1e1251` |

### Reproducibilidad

- Segunda exportacion con el mismo origen y corte (2026-11-08T19:59:25Z): `dataset_hash` `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744` -> **igual**; manifest, parquet y procedencia **byte a byte identicos**.
- Comando de la repeticion: `.venv/Scripts/python -X utf8 scripts/exportar_market_history.py --binance --corte 2026-11-01 --nombre binance_c20261101 --salida-raiz E:/quantdesk-lab/tmp/TI-02-DATA/repeticion --sobrescribir --repeticion`

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

- `binance_ohlcv_1d`: por fila; campo: ts_ms + interval_ms (cierre de la vela). Una vela solo es definitiva al cerrar (close_time de Binance = apertura + intervalo - 1 ms) y TI-13-PUB no conserva ninguna marca de publicacion por fila: solo la apertura de la vela y la fecha de descarga (2026-11-08), que como disponibilidad dejaria todo el historico fuera de cualquier corte anterior. Se declara el instante de cierre, la cota inferior de lo que pudo saberse, sin latencia de red ni de publicacion (limitacion: un consumidor que necesite latencia debe aplicarla en su politica).
- `binance_ohlcv_1h`: por fila; campo: ts_ms + interval_ms (cierre de la vela). Una vela solo es definitiva al cerrar (close_time de Binance = apertura + intervalo - 1 ms) y TI-13-PUB no conserva ninguna marca de publicacion por fila: solo la apertura de la vela y la fecha de descarga (2026-11-08), que como disponibilidad dejaria todo el historico fuera de cualquier corte anterior. Se declara el instante de cierre, la cota inferior de lo que pudo saberse, sin latencia de red ni de publicacion (limitacion: un consumidor que necesite latencia debe aplicarla en su politica).

### Validacion con `data_py` y look-ahead

- `data_py.vendor_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA")`: `dataset_hash` del motor `sha256:d765d56037f700bd2550a9a2ae9d53fbd2406afd7cddb82bbfeaf2a56670b744`, igual calculado aqui.
- `data_py.dataset_describe_json("E:/quantdesk-lab/datasets/TI-02-DATA/binance_c20261101", True)`: tablas binance_ohlcv_1d (30336 filas, hash_verified=True), binance_ohlcv_1h (388973 filas, hash_verified=True).
- `data_py.availability_report_json(dir, table_id, "{}", "reject")` por tabla: binance_ohlcv_1d: declared 30336/30336, undeclared 0, violaciones DPOL-AVL-002 0; binance_ohlcv_1h: declared 388973/388973, undeclared 0, violaciones DPOL-AVL-002 0.
- `data_py.verify_policy_json(mode=feed, policy={"availability": {"require_available_at": true}, "schema": "engine.data-policy", "timezone": {"require_declared": true}, "version": "v1"}, vendor_root="E:/quantdesk-lab/datasets/TI-02-DATA", dataset_id="binance_c20261101", revision_policy="reject")`: ok=True, violaciones: ninguna; report_hash `sha256:b939648033e79fb8cf9e59d006c5e743e98b2a8923a4ba8eb9b2ee7bb77b2b59`.
- Comprobacion propia sobre el parquet releido (esquema exacto de `data_py.table_schemas_json()`, orden, cierre y disponibilidad <= corte, disponibilidad >= cierre, revision 0): sin incidencias.
- Violaciones de look-ahead por fila: **0**; tablas no consumibles causalmente: ninguna.

### Universo y sesgo de supervivencia (D-07)

- binance: Pares USDT que existen hoy en Binance spot y entraron en TI-13-PUB (el universo de la fuente hoy, no el de una fecha pasada). No hay pares deslistados ni fechas de alta como miembro de un universo: sesgo de supervivencia declarado (D-07), sin tabla universe/v1 porque no se conocen altas ni bajas.

## Lo que no se exporta

- Cadenas de opciones (`market.options.*`): vacias en el lago (TI-01-INV); TI-09-ARCH retirada.
- MT5 (TI-12-MT5, a la espera de la puerta 2) y los corpus genericos de TI-13-PUB (sin OHLCV real con fecha).
- De Binance: `quote_volume` y `n_trades`; `ohlcv/v1` no tiene donde ponerlos (`volume` es el volumen en activo base, `volume_kind` = `traded`). Tampoco `value`, que es igual a `close`.
- Del lago: el campo `date` (se usa `_ts`, ver el desfase arriba), `_clock_offset_ns` (nulo en todas las filas), `_batch_id`, `_cycle` y demas columnas de sistema.
- Ninguna tabla `universe/v1` ni `corporate_actions/v1`: no se conocen altas, bajas ni acciones corporativas, y `adjusted_by_vendor` queda en su valor por defecto (precios crudos).
