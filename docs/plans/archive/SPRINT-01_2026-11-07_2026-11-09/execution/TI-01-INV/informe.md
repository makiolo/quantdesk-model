# Inventario del lago quantdesk-network (TI-01-INV)

- Fecha de ejecución (UTC): 2026-11-08 15:57:02Z
- Días pedidos: 2024-01-01 a 2026-11-08, ambos incluidos
- Base: http://192.168.1.48:8790/qn (entorno `main`). La credencial no figura en este informe.
- Topics: patrón `market.*`; instrumentos por topic: todos
- Huecos: tramos de 3 o más días hábiles sin datos; los festivos cuentan como hueco (cota superior)
- Duplicados: clave = etiquetas del instrumento + marca + campos de contrato, contados en todo el rango pedido
- Peticiones GET hechas: 7816 (lista completa en el JSON, sin cabeceras)

## Resumen por topic

| topic | lectura | etiquetas agrupadas | instrumentos | primera | última | días hábiles con datos | cobertura | paso mediano | filas por instrumento y día hábil | duplicados | nulos | no finitos | negativos | huecos | estado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| market.ohlcv | /objects/market.ohlcv | interval + symbol | 56/56 | 2024-11-01 | 2026-11-08 | 521/526 | 99% | 1 h | 1 | 6047 | 30665 | 0 | 0 | 0 | OK |
| market.options.chain | /objects/market.options.chain | – | 0/0 | – | – | 0/0 | – | – | – | 0 | 0 | 0 | 0 | 0 | sin datos |
| market.options.fx | /objects/market.options.fx | – | 0/0 | – | – | 0/0 | – | – | – | 0 | 0 | 0 | 0 | 0 | sin datos |
| market.performance | /objects/market.performance | period + symbol | 64/64 | 2025-12-04 | 2026-11-08 | 95/242 | 39% | – | 1 | 0 | 6720 | 0 | 0 | 5 | OK |
| market.rates.quotes | /objects/market.rates.quotes | currency + curve_type + tenor | 103/103 | 2025-12-04 | 2026-11-06 | 106/242 | 44% | 0.09 s | 1 | 0 | 18128 | 0 | 0 | 4 | OK |

## Detalle por topic

### market.ohlcv

- Tipo: object; lectura `/objects/market.ohlcv`
- Etiquetas declaradas: interval, symbol; agrupación por: interval + symbol (combinación completa que trae /latest)
- Esquema (campos): open:number, high:number, low:number, close:number, volume:number, date:string, source:string
- Marca temporal: columna `_ts` en ns: 30665 filas
- Campos de contenido frente a `_ts`: `date`: 140 de 30665 filas difieren de `_ts` en el día UTC; ejemplos: interval=1h,symbol=AUDCAD: _ts=2026-10-18T23:00:00+00:00 date=2026-10-19 | interval=1h,symbol=AUDCAD: _ts=2026-10-19T23:00:00+00:00 date=2026-10-20 | interval=1h,symbol=AUDCAD: _ts=2026-10-20T23:00:00+00:00 date=2026-10-21
- Primera 2024-11-01, última 2026-11-08; días con datos 525 (521 hábiles, 4 en fin de semana) frente a 526 hábiles esperables
- Frecuencia: paso mediano dentro del día 1 h; filas por instrumento y día hábil (mediana) 1
- Huecos de 3 o más días hábiles: 0
- Calidad: duplicados 6047; nulos _clock_offset_ns 30665; no finitos ninguno; negativos donde no tienen sentido ninguno

| instrumento | primera | última | días hábiles | esperables | cobertura | filas | huecos | vencimientos | strikes |
|---|---|---|---|---|---|---|---|---|---|
| interval=1d,symbol=AUDCAD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 527 | 0 | 0 | 0 |
| interval=1d,symbol=AUDCHF | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=AUDJPY | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=AUDNZD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 527 | 0 | 0 | 0 |
| interval=1d,symbol=AUDUSD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=CADCHF | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=CADJPY | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=CHFJPY | 2024-11-01 | 2026-11-06 | 521 | 526 | 99% | 527 | 0 | 0 | 0 |
| interval=1d,symbol=EURAUD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=EURCAD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=EURCHF | 2024-11-01 | 2026-11-06 | 521 | 526 | 99% | 526 | 0 | 0 | 0 |
| interval=1d,symbol=EURGBP | 2024-11-01 | 2026-11-06 | 521 | 526 | 99% | 525 | 0 | 0 | 0 |
| interval=1d,symbol=EURJPY | 2024-11-01 | 2026-11-08 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=EURNZD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=EURUSD | 2024-11-01 | 2026-11-06 | 521 | 526 | 99% | 527 | 0 | 0 | 0 |
| interval=1d,symbol=GBPAUD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=GBPCAD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=GBPCHF | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=GBPJPY | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=GBPNZD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=GBPUSD | 2024-11-01 | 2026-11-06 | 521 | 526 | 99% | 527 | 0 | 0 | 0 |
| interval=1d,symbol=NZDCAD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=NZDCHF | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=NZDJPY | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=NZDUSD | 2024-11-01 | 2026-11-07 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=USDCAD | 2024-11-01 | 2026-11-08 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1d,symbol=USDCHF | 2024-11-01 | 2026-11-06 | 521 | 526 | 99% | 526 | 0 | 0 | 0 |
| interval=1d,symbol=USDJPY | 2024-11-01 | 2026-11-08 | 521 | 526 | 99% | 528 | 0 | 0 | 0 |
| interval=1h,symbol=AUDCAD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 563 | 0 | 0 | 0 |
| interval=1h,symbol=AUDCHF | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 570 | 0 | 0 | 0 |
| interval=1h,symbol=AUDJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 566 | 0 | 0 | 0 |
| interval=1h,symbol=AUDNZD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 572 | 0 | 0 | 0 |
| interval=1h,symbol=AUDUSD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 493 | 0 | 0 | 0 |
| interval=1h,symbol=CADCHF | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 576 | 0 | 0 | 0 |
| interval=1h,symbol=CADJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 561 | 0 | 0 | 0 |
| interval=1h,symbol=CHFJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 581 | 0 | 0 | 0 |
| interval=1h,symbol=EURAUD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 585 | 0 | 0 | 0 |
| interval=1h,symbol=EURCAD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 583 | 0 | 0 | 0 |
| interval=1h,symbol=EURCHF | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 568 | 0 | 0 | 0 |
| interval=1h,symbol=EURGBP | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 573 | 0 | 0 | 0 |
| interval=1h,symbol=EURJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 586 | 0 | 0 | 0 |
| interval=1h,symbol=EURNZD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 577 | 0 | 0 | 0 |
| interval=1h,symbol=EURUSD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 571 | 0 | 0 | 0 |
| interval=1h,symbol=GBPAUD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 589 | 0 | 0 | 0 |
| interval=1h,symbol=GBPCAD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 567 | 0 | 0 | 0 |
| interval=1h,symbol=GBPCHF | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 582 | 0 | 0 | 0 |
| interval=1h,symbol=GBPJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 566 | 0 | 0 | 0 |
| interval=1h,symbol=GBPNZD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 568 | 0 | 0 | 0 |
| interval=1h,symbol=GBPUSD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 572 | 0 | 0 | 0 |
| interval=1h,symbol=NZDCAD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 572 | 0 | 0 | 0 |
| interval=1h,symbol=NZDCHF | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 579 | 0 | 0 | 0 |
| interval=1h,symbol=NZDJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 566 | 0 | 0 | 0 |
| interval=1h,symbol=NZDUSD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 492 | 0 | 0 | 0 |
| interval=1h,symbol=USDCAD | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 580 | 0 | 0 | 0 |
| interval=1h,symbol=USDCHF | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 572 | 0 | 0 | 0 |
| interval=1h,symbol=USDJPY | 2026-10-18 | 2026-11-06 | 15 | 15 | 100% | 563 | 0 | 0 | 0 |

### market.options.chain

- Tipo: object; lectura `/objects/market.options.chain`
- Etiquetas declaradas: asset_type, opt_type, symbol; agrupación por: ninguna (un único instrumento) (combinación completa que trae /latest)
- AVISO: etiquetas declaradas sin valor en /latest: asset_type, opt_type, symbol
- Esquema (campos): strike:number, maturity:string, last_price:number, bid:number, ask:number, implied_vol:number, in_the_money:boolean, volume:integer, open_interest:integer, date:string, source:string, captured_at:integer, capture_id:string, underlying_price:number
- Marca temporal: ninguna fila con marca válida
- Campos de contenido frente a `_ts`: sin comparación: no hay `_ts` en las filas, la marca es el campo de contenido indicado arriba
- Sin datos en el rango pedido

### market.options.fx

- Tipo: object; lectura `/objects/market.options.fx`
- Etiquetas declaradas: provider, symbol; agrupación por: ninguna (un único instrumento) (combinación completa que trae /latest)
- AVISO: etiquetas declaradas sin valor en /latest: provider, symbol
- Esquema (campos): strike:string, call_last:string, call_vol:string, put_last:string, put_vol:string, source:string
- Marca temporal: ninguna fila con marca válida
- Campos de contenido frente a `_ts`: sin comparación: no hay `_ts` en las filas, la marca es el campo de contenido indicado arriba
- Sin datos en el rango pedido

### market.performance

- Tipo: object; lectura `/objects/market.performance`
- Etiquetas declaradas: period, symbol; agrupación por: period + symbol (combinación completa que trae /latest)
- Esquema (campos): performance:number, date:string, source:string
- Marca temporal: columna `_ts` en ns: 6720 filas
- Campos de contenido frente a `_ts`: `date`: 0 de 6720 filas difieren de `_ts` en el día UTC
- Primera 2025-12-04, última 2026-11-08; días con datos 105 (95 hábiles, 10 en fin de semana) frente a 242 hábiles esperables
- Frecuencia: paso mediano dentro del día –; filas por instrumento y día hábil (mediana) 1
- Huecos de 3 o más días hábiles: 5; mayores: 2026-04-06→2026-09-18 (120 d), 2026-10-01→2026-10-13 (9 d), 2026-10-23→2026-10-28 (4 d), 2025-12-15→2025-12-17 (3 d), 2026-03-23→2026-03-25 (3 d)
- Calidad: duplicados 0; nulos _clock_offset_ns 6720; no finitos ninguno; negativos donde no tienen sentido ninguno

| instrumento | primera | última | días hábiles | esperables | cobertura | filas | huecos | vencimientos | strikes |
|---|---|---|---|---|---|---|---|---|---|
| period=D,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=D,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=HY,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=M,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=MTD,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Q,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=W,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=Y,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=AUD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=CAD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=CHF | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=EUR | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=GBP | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=JPY | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=NZD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |
| period=YTD,symbol=USD | 2025-12-04 | 2026-11-08 | 95 | 242 | 39% | 105 | 5 | 0 | 0 |

### market.rates.quotes

- Tipo: object; lectura `/objects/market.rates.quotes`
- Etiquetas declaradas: currency, curve_type, tenor; agrupación por: currency + curve_type + tenor (combinación completa que trae /latest)
- Esquema (campos): valuation_date:string, rate:number, scraped_at_ms:integer, source:string
- Marca temporal: columna `_ts` en ns: 18128 filas
- Campos de contenido frente a `_ts`: sin comparación: no hay `_ts` en las filas, la marca es el campo de contenido indicado arriba
- Primera 2025-12-04, última 2026-11-06; días con datos 108 (106 hábiles, 2 en fin de semana) frente a 242 hábiles esperables
- Frecuencia: paso mediano dentro del día 0.09 s; filas por instrumento y día hábil (mediana) 1
- Huecos de 3 o más días hábiles: 4; mayores: 2026-04-06→2026-09-16 (118 d), 2026-10-26→2026-11-02 (6 d), 2025-12-15→2025-12-17 (3 d), 2026-03-23→2026-03-25 (3 d)
- Calidad: duplicados 0; nulos _clock_offset_ns 18128; no finitos ninguno; negativos donde no tienen sentido ninguno

| instrumento | primera | última | días hábiles | esperables | cobertura | filas | huecos | vencimientos | strikes |
|---|---|---|---|---|---|---|---|---|---|
| currency=AUD,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 188 | 9 | 0 | 0 |
| currency=AUD,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=AUD,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 190 | 7 | 0 | 0 |
| currency=AUD,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 190 | 8 | 0 | 0 |
| currency=AUD,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=AUD,curve_type=OIS,tenor=BBSW_3M | 2026-04-03 | 2026-04-03 | 1 | 1 | 100% | 20 | 0 | 0 | 0 |
| currency=BTC,curve_type=OIS,tenor=BTC_FUT_1M | 2025-12-09 | 2026-04-03 | 61 | 84 | 73% | 118 | 3 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=20Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=30Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 179 | 7 | 0 | 0 |
| currency=CAD,curve_type=OIS,tenor=CDOR_3M | 2025-12-10 | 2026-11-06 | 81 | 238 | 34% | 156 | 6 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 8 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=12Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=15Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=20Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=25Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=30Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=4Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 80 | 242 | 33% | 189 | 8 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=6Y | 2025-12-04 | 2026-11-06 | 32 | 242 | 13% | 99 | 3 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=7Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=8Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=IBOR,tenor=9Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=CHF,curve_type=OIS,tenor=SARON_3M | 2026-04-03 | 2026-04-03 | 1 | 1 | 100% | 20 | 0 | 0 | 0 |
| currency=CHF,curve_type=OIS,tenor=SARON_FUT_3M | 2025-12-04 | 2026-04-03 | 2 | 87 | 2% | 40 | 1 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 8 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=12Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=15Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 79 | 242 | 33% | 188 | 8 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=20Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=25Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 8 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=30Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=4Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 8 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=6Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=7Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=8Y | 2025-12-04 | 2026-11-06 | 80 | 242 | 33% | 189 | 9 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=9Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=Euribor 1 month | 2025-12-04 | 2026-10-22 | 79 | 231 | 34% | 120 | 4 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=Euribor 1 week | 2025-12-04 | 2026-10-22 | 79 | 231 | 34% | 120 | 4 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=Euribor 12 months | 2025-12-04 | 2026-10-22 | 79 | 231 | 34% | 120 | 4 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=Euribor 3 months | 2025-12-04 | 2026-10-22 | 79 | 231 | 34% | 120 | 4 | 0 | 0 |
| currency=EUR,curve_type=IBOR,tenor=Euribor 6 months | 2025-12-04 | 2026-10-22 | 79 | 231 | 34% | 120 | 4 | 0 | 0 |
| currency=EUR,curve_type=OIS,tenor=EURIBOR_FUT_3M | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 186 | 7 | 0 | 0 |
| currency=EUR,curve_type=OIS,tenor=EUR_SCHATZ_FUT | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 184 | 7 | 0 | 0 |
| currency=EUR,curve_type=OIS,tenor=ON | 2025-12-04 | 2026-11-06 | 99 | 242 | 41% | 104 | 4 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=12Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=15Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 188 | 9 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=20Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=25Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 8 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=30Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=4Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 8 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=6Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=7Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 186 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=8Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=IBOR,tenor=9Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 188 | 7 | 0 | 0 |
| currency=GBP,curve_type=OIS,tenor=SONIA_3M | 2025-12-04 | 2026-11-06 | 85 | 242 | 35% | 185 | 7 | 0 | 0 |
| currency=GBP,curve_type=OIS,tenor=SONIA_FUT_3M | 2025-12-04 | 2026-11-06 | 86 | 242 | 36% | 185 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=12Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=15Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=20Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=25Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=30Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 8 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=4Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=6Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=7Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=8Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=IBOR,tenor=9Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=JPY,curve_type=OIS,tenor=TIBOR_3M | 2025-12-04 | 2026-11-06 | 78 | 242 | 32% | 189 | 10 | 0 | 0 |
| currency=NZD,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 83 | 242 | 34% | 181 | 8 | 0 | 0 |
| currency=NZD,curve_type=OIS,tenor=BKBM_3M | 2025-12-10 | 2026-11-06 | 82 | 238 | 34% | 158 | 8 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=10Y | 2025-12-04 | 2026-11-06 | 79 | 242 | 33% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=1Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=2Y | 2025-12-04 | 2026-11-06 | 80 | 242 | 33% | 189 | 8 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=30Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=3Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=4Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=5Y | 2025-12-04 | 2026-11-06 | 80 | 242 | 33% | 189 | 8 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=6Y | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=IBOR,tenor=7Y | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 189 | 7 | 0 | 0 |
| currency=USD,curve_type=OIS,tenor=FED_FUNDS_30D | 2025-12-04 | 2026-11-06 | 81 | 242 | 34% | 181 | 8 | 0 | 0 |
| currency=USD,curve_type=OIS,tenor=ON | 2025-12-04 | 2026-11-06 | 96 | 242 | 40% | 100 | 4 | 0 | 0 |
| currency=USD,curve_type=OIS,tenor=TERM_SOFR_3M | 2025-12-04 | 2026-11-06 | 82 | 242 | 34% | 191 | 7 | 0 | 0 |
| currency=USD,curve_type=OIS,tenor=US_2Y_NOTE_FUT | 2025-12-04 | 2026-11-06 | 88 | 242 | 36% | 205 | 5 | 0 | 0 |

## GPU de los nodos: pendiente

La API de qn no expone nodos ni GPU: en el código de `crates/` del repo quantdesk-network no hay ninguna ruta ni campo de GPU (rutas de qn-server: topics, schema, publish, latest, log, admin/wal/quarantine, health, metrics). No medido. Comando a ejecutar a mano en cada nodo, pegando su salida en el informe:

```
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
```

## Consultas reproducibles

Esta ejecución (QN_URLS, QN_TOKEN y, si aplica, QN_ENV en el entorno; la credencial no se escribe):

```
.venv/Scripts/python -X utf8 scripts/inventario_options_chain.py --json /home/mini/ti01-inv/inventario-macold.json --informe /home/mini/ti01-inv/informe-macold.md
```

- Listado de topics: `GET http://192.168.1.48:8790/qn/api/v1/topics?env=main`
- Por topic: `GET http://192.168.1.48:8790/qn/api/v1/topics/<topic>/schema?env=main` y `.../latest?env=main`; lectura histórica `/series/<topic>/rows` u `/objects/<topic>` con `from` y `to` en formato `AAAA-MM-DDT00:00:00Z`, por meses (troceados por días si el servidor rechaza el rango por filas) y con las etiquetas de cada instrumento.
- Detalle de cada petición: `--json`, clave `cabecera.peticiones`.
