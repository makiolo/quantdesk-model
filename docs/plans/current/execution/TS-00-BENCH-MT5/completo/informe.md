# TS-00-BENCH-MT5: cabecera y ampliación

Generado 2026-11-13T08:59:14.084182+00:00. Motor `69fdb39d0b67969dbdafa77f5da656511342f175`; semilla 20261101; fecha de corte de datos **2026-11-01T00:00:00Z**; CPU, 2 hilos torch; sin red, HF_HUB_OFFLINE=1.

Informe de corridas completas. Los umbrales se evalúan sin modificarlos.

D14/D15 · ISSUE-LAGO-FX-1D-CLOSE: la tabla anterior usaba close 00:00 UTC de yfinance; MT5 usa el cierre de sesión 17:00 NY. Los umbrales fijados el 2026-11-09 son provisionales hasta la tabla MT5 completa. Cabecera: misma ventana, inicio, fin, rejilla de fechas y horizontes; ampliación desde 2000: descriptiva, **no mueve umbrales**, solo HMM/GARCH/Chronos-2; Toto y FinCast excluidos.

Los tres datasets son proxy de disponibilidad: ts es fecha de sesión a 00:00 UTC; available_at nulo y default_lag_ms=0 (disponible en ts+1 día). No prueba disponibilidad histórica real. Horizontes por barra, incluidas las barras antiguas de sábado/domingo; no se filtran.

Comando de generación: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --informe E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_cierre_c20261101 E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_hist_cierre_c20261101 --toto E:/quantdesk-lab/runs/TS-00-BENCH/toto_mt5_fx28_cierre_c20261101 --fincast E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/mt5_fx28_cierre_c20261101 --pilotos E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_cabecera E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_ampliacion E:/quantdesk-lab/runs/TS-00-BENCH/piloto_toto_mt5_cabecera E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_mt5_cabecera --destino docs/plans/current/execution/TS-00-BENCH-MT5/completo`.

| dataset (proxy) | dataset_hash SHA-256 | filas | preset |
|---|---|---|---|
| lago_cierre_c20261101 | sha256:aff96e6cb64296f1a55032354a3b6b3642a7527c0f40c55d3f83630a344fd356 | 14448 | {'tabla': 'lago_ohlcv_1d', 'ventana': 250, 'inicio': '2025-10-20', 'fin': '2026-10-03', 'paso_dias': 1} |
| mt5_fx28_cierre_c20261101 | sha256:a5015bc95b7b410b090785e8e9a118e5cb9276086e9c6a05f69932f0df9893da | 14476 | {'tabla': 'lago_ohlcv_1d', 'ventana': 250, 'inicio': '2025-10-20', 'fin': '2026-10-03', 'paso_dias': 1} |
| mt5_fx28_hist_cierre_c20261101 | sha256:47d79b39fd682ebd6adc92aeb429edcb535884c9e2fb4d58d9c1b4cc16067d32 | 178382 | {'tabla': 'lago_ohlcv_1d', 'ventana': 250, 'inicio': '2001-01-02', 'fin': '2026-10-03', 'paso_dias': 20} |

## Cabecera MT5 (proxy)

Corrida `E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_cierre_c20261101`; modelos ['hmm', 'garch', 'chronos2']; cada=1; máximo por activo=0; fallos={'chronos2': 0, 'garch': 0, 'hmm': 0}; SALTADOS={}. SHA-256 predicciones `c1e9b4382345c5e13e72bb6434735b7b72894034f562f5d9272bc30ca0201951`.

Convergencia declarada: `{"garch": {"no_convergido": 0, "n": 6944}, "hmm": {"no_convergido": 1561, "n": 6944}}`. Cruces de cuantiles conservados de SPRINT-01 (solo FinCast rechaza): `{"politica": "A12: solo FinCast rechaza cruces; los modelos SPRINT-01 se puntuan sin reparacion", "alcance": "filas ok, horizontes almacenados; antes de la interseccion de modelos", "por_modelo_h": [{"modelo": "chronos2", "h": 1, "n_validos": 6944, "origenes_con_cruce": 155}, {"modelo": "chronos2", "h": 5, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "chronos2", "h": 20, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "garch", "h": 1, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "garch", "h": 5, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "garch", "h": 20, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "hmm", "h": 1, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "hmm", "h": 5, "n_validos": 6944, "origenes_con_cruce": 0}, {"modelo": "hmm", "h": 20, "n_validos": 6944, "origenes_con_cruce": 0}]}`.

| h | modelo | activos | CRPS mediana | CRPS rel. GARCH | QLIKE mediana | Kupiec rechazos 1%/99% |
|---|---|---|---|---|---|---|
| 1 | hmm | 28 | 0.00207114669 | 1.00157278 | -10.0946906 | 4/3 |
| 1 | garch | 28 | 0.00207669242 | 1 | -10.082431 | 6/3 |
| 1 | chronos2 | 28 | 0.00211867857 | 1.02744796 | -10.0923781 | 14/15 |
| 5 | hmm | 28 | 0.0043454928 | 1.00725467 | -8.47375123 | 1/1 |
| 5 | garch | 28 | 0.00431198694 | 1 | -8.4747556 | 2/0 |
| 5 | chronos2 | 28 | 0.00437196159 | 1.00923716 | -8.47612537 | 1/0 |
| 20 | hmm | 28 | 0.00915561947 | 1.02357595 | -7.07895297 | 0/0 |
| 20 | garch | 28 | 0.00886441117 | 1 | -7.07592786 | 0/0 |
| 20 | chronos2 | 28 | 0.0084914273 | 0.974912203 | -7.08760747 | 0/0 |


Corrida `E:/quantdesk-lab/runs/TS-00-BENCH/toto_mt5_fx28_cierre_c20261101`; modelos ['toto']; cada=5; máximo por activo=0; fallos={'toto': 0}; SALTADOS={}. SHA-256 predicciones `c334b6d82738b228f6d16468792e5fb1717abd54fb4eead646500775490f6c1b`.

Convergencia declarada: `{}`. Cruces de cuantiles conservados de SPRINT-01 (solo FinCast rechaza): `{"politica": "A12: solo FinCast rechaza cruces; los modelos SPRINT-01 se puntuan sin reparacion", "alcance": "filas ok, horizontes almacenados; antes de la interseccion de modelos", "por_modelo_h": [{"modelo": "toto", "h": 1, "n_validos": 1400, "origenes_con_cruce": 0}, {"modelo": "toto", "h": 5, "n_validos": 1400, "origenes_con_cruce": 0}, {"modelo": "toto", "h": 20, "n_validos": 1400, "origenes_con_cruce": 0}]}`.

| h | modelo | activos | CRPS mediana | CRPS rel. GARCH | QLIKE mediana | Kupiec rechazos 1%/99% |
|---|---|---|---|---|---|---|
| 1 | hmm | 28 | 0.00217023554 | 1.00071718 | -9.97312134 | 4/1 |
| 1 | garch | 28 | 0.00217533525 | 1 | -10.0060226 | 4/2 |
| 1 | chronos2 | 28 | 0.00228540341 | 1.02775759 | -9.93256218 | 0/0 |
| 1 | toto | 28 | 0.00230401228 | 1.0607944 | -9.74629856 | 11/5 |
| 5 | hmm | 28 | 0.00443421763 | 1.00492398 | -8.47388509 | 1/1 |
| 5 | garch | 28 | 0.00441401067 | 1 | -8.47133813 | 2/0 |
| 5 | chronos2 | 28 | 0.00449607375 | 1.00396029 | -8.48228485 | 1/0 |
| 5 | toto | 28 | 0.0045963708 | 1.02203178 | -8.32200002 | 1/0 |
| 20 | hmm | 28 | 0.00910257573 | 1.01659447 | -7.08135368 | 0/0 |
| 20 | garch | 28 | 0.00888892434 | 1 | -7.08013755 | 0/0 |
| 20 | chronos2 | 28 | 0.00832601998 | 0.973244006 | -7.09371521 | 0/0 |
| 20 | toto | 28 | 0.00878287052 | 1.05398121 | -6.81852791 | 0/0 |


Corrida `E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/mt5_fx28_cierre_c20261101`; modelos ['fincast']; cada=5; máximo por activo=0; fallos={'fincast': 6}; SALTADOS={}. SHA-256 predicciones `5ccce1e070d96c7839afef09b6890687e91e11ee62aac62f9c6f2eaf78f8040c`.

Convergencia declarada: `{}`. Cruces de cuantiles conservados de SPRINT-01 (solo FinCast rechaza): `{"politica": "A12: solo FinCast rechaza cruces; los modelos SPRINT-01 se puntuan sin reparacion", "alcance": "filas ok, horizontes almacenados; antes de la interseccion de modelos", "por_modelo_h": [{"modelo": "fincast", "h": 1, "n_validos": 1394, "origenes_con_cruce": 0}, {"modelo": "fincast", "h": 5, "n_validos": 1394, "origenes_con_cruce": 0}, {"modelo": "fincast", "h": 20, "n_validos": 1394, "origenes_con_cruce": 0}]}`.
### FinCast y bases: ventana limpia común

CRPS deciles nativos para todos; origen > 2025-08-27, comunes válidos. FinCast: colas y banda **no aplica**; sólo C1 CRPS y QLIKE. La selección condicionada a sus fallos está registrada en revision.json.

| h | modelo | activos | CRPS deciles mediana | QLIKE mediana |
|---|---|---|---|---|
| 1 | chronos2 | 28 | 0.00259954456 | -9.93256218 |
| 1 | fincast | 28 | 0.00275443391 | -9.76064864 |
| 1 | garch | 28 | 0.00248329904 | -10.0060226 |
| 1 | hmm | 28 | 0.00247704725 | -9.97312134 |
| 1 | toto | 28 | 0.00262678344 | -9.73514735 |
| 5 | chronos2 | 28 | 0.00511488532 | -8.48228485 |
| 5 | fincast | 28 | 0.00518295319 | -8.50486234 |
| 5 | garch | 28 | 0.00502323522 | -8.47133813 |
| 5 | hmm | 28 | 0.00503569956 | -8.47388509 |
| 5 | toto | 28 | 0.00516885304 | -8.32200002 |
| 20 | chronos2 | 28 | 0.00949362068 | -7.09371521 |
| 20 | fincast | 28 | 0.0094820942 | -7.1219255 |
| 20 | garch | 28 | 0.0101711467 | -7.08013755 |
| 20 | hmm | 28 | 0.0104331048 | -7.08135368 |
| 20 | toto | 28 | 0.00952197808 | -6.81852791 |

### Barras, fines de semana y orígenes válidos por par

Validez antes de --cada/--max-origenes; omisiones referidas a toda la rejilla. El fin del preset limita los orígenes; los futuros se buscan en el dataset hasta el corte congelado.

| instrument | barras | primera_barra | sabados | domingos | barras_antes_inicio | origenes_validos | primer_origen | ultimo_origen | sin_ventana | sin_objetivo | sin_barra_nueva |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| AUDCHF | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| AUDJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| AUDNZD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| AUDUSD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| CADCHF | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| CADJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| CHFJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURAUD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURCAD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURCHF | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURGBP | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURNZD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| EURUSD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| GBPAUD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| GBPCAD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| GBPCHF | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| GBPJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| GBPNZD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| GBPUSD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| NZDCAD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| NZDCHF | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| NZDJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| NZDUSD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| USDCAD | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| USDCHF | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |
| USDJPY | 517 | 2024-11-01 | 0 | 0 | 249 | 248 | 2025-10-21 | 2026-10-03 | 1 | 0 | 100 |

## Ampliación MT5 (proxy)

Corrida `E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_hist_cierre_c20261101`; modelos ['hmm', 'garch', 'chronos2']; cada=1; máximo por activo=0; fallos={'chronos2': 0, 'garch': 0, 'hmm': 0}; SALTADOS={}. SHA-256 predicciones `5786fff614453783d07beb7ef4352595d10443a281e69c4651cc611b75bd0edc`.

Convergencia declarada: `{"garch": {"no_convergido": 3, "n": 12037}, "hmm": {"no_convergido": 3335, "n": 12037}}`. Cruces de cuantiles conservados de SPRINT-01 (solo FinCast rechaza): `{"politica": "A12: solo FinCast rechaza cruces; los modelos SPRINT-01 se puntuan sin reparacion", "alcance": "filas ok, horizontes almacenados; antes de la interseccion de modelos", "por_modelo_h": [{"modelo": "chronos2", "h": 1, "n_validos": 12037, "origenes_con_cruce": 125}, {"modelo": "chronos2", "h": 5, "n_validos": 12037, "origenes_con_cruce": 2}, {"modelo": "chronos2", "h": 20, "n_validos": 12037, "origenes_con_cruce": 3}, {"modelo": "garch", "h": 1, "n_validos": 12037, "origenes_con_cruce": 0}, {"modelo": "garch", "h": 5, "n_validos": 12037, "origenes_con_cruce": 0}, {"modelo": "garch", "h": 20, "n_validos": 12037, "origenes_con_cruce": 0}, {"modelo": "hmm", "h": 1, "n_validos": 12037, "origenes_con_cruce": 0}, {"modelo": "hmm", "h": 5, "n_validos": 12037, "origenes_con_cruce": 0}, {"modelo": "hmm", "h": 20, "n_validos": 12037, "origenes_con_cruce": 0}]}`.

| h | modelo | activos | CRPS mediana | CRPS rel. GARCH | QLIKE mediana | Kupiec rechazos 1%/99% |
|---|---|---|---|---|---|---|
| 1 | hmm | 28 | 0.00326474444 | 1.01138191 | -9.15975114 | 7/7 |
| 1 | garch | 28 | 0.00319288754 | 1 | -9.22918396 | 5/4 |
| 1 | chronos2 | 28 | 0.00325226304 | 1.02686499 | -9.19860366 | 8/12 |
| 5 | hmm | 28 | 0.00733849803 | 1.02977124 | -7.5998746 | 7/1 |
| 5 | garch | 28 | 0.00704394807 | 1 | -7.60577066 | 9/5 |
| 5 | chronos2 | 28 | 0.00711353481 | 1.00824772 | -7.53464037 | 3/5 |
| 20 | hmm | 28 | 0.0150131936 | 1.06235803 | -6.17526447 | 9/3 |
| 20 | garch | 28 | 0.0141975395 | 1 | -6.16300726 | 10/4 |
| 20 | chronos2 | 28 | 0.0142114132 | 0.985865015 | -6.1465008 | 3/5 |

### Barras, fines de semana y orígenes válidos por par

Validez antes de --cada/--max-origenes; omisiones referidas a toda la rejilla. El fin del preset limita los orígenes; los futuros se buscan en el dataset hasta el corte congelado.

| instrument | barras | primera_barra | sabados | domingos | barras_antes_inicio | origenes_validos | primer_origen | ultimo_origen | sin_ventana | sin_objetivo | sin_barra_nueva |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | 6890 | 2000-01-03 | 1 | 9 | 259 | 466 | 2001-01-02 | 2026-09-28 | 0 | 0 | 5 |
| AUDCHF | 6880 | 2000-01-03 | 1 | 9 | 261 | 466 | 2001-01-02 | 2026-09-28 | 0 | 0 | 5 |
| AUDJPY | 6912 | 2000-01-03 | 0 | 0 | 261 | 470 | 2001-01-02 | 2026-09-28 | 0 | 0 | 1 |
| AUDNZD | 6859 | 2000-01-03 | 0 | 9 | 246 | 465 | 2001-01-22 | 2026-09-28 | 1 | 0 | 5 |
| AUDUSD | 6970 | 2000-01-03 | 0 | 0 | 260 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| CADCHF | 6801 | 2000-01-03 | 1 | 9 | 261 | 460 | 2001-01-02 | 2026-09-28 | 0 | 0 | 11 |
| CADJPY | 5104 | 2007-02-12 | 0 | 0 | 0 | 341 | 2008-02-15 | 2026-09-28 | 130 | 0 | 0 |
| CHFJPY | 6914 | 2000-01-03 | 1 | 0 | 261 | 469 | 2001-01-02 | 2026-09-28 | 0 | 0 | 2 |
| EURAUD | 5799 | 2004-06-17 | 1 | 0 | 0 | 390 | 2005-06-10 | 2026-09-28 | 81 | 0 | 0 |
| EURCAD | 6811 | 2000-01-03 | 1 | 2 | 237 | 464 | 2001-02-11 | 2026-09-28 | 2 | 0 | 5 |
| EURCHF | 6960 | 2000-01-03 | 1 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| EURGBP | 6966 | 2000-01-03 | 0 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| EURJPY | 6843 | 2000-01-03 | 1 | 0 | 134 | 462 | 2001-07-01 | 2026-09-28 | 9 | 0 | 0 |
| EURNZD | 6798 | 2000-01-03 | 1 | 9 | 261 | 459 | 2001-01-02 | 2026-09-28 | 0 | 0 | 12 |
| EURUSD | 6971 | 2000-01-03 | 0 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| GBPAUD | 4969 | 2007-08-21 | 0 | 0 | 0 | 332 | 2008-08-13 | 2026-09-28 | 139 | 0 | 0 |
| GBPCAD | 4969 | 2007-08-21 | 0 | 0 | 0 | 332 | 2008-08-13 | 2026-09-28 | 139 | 0 | 0 |
| GBPCHF | 6924 | 2000-01-03 | 1 | 0 | 261 | 468 | 2001-01-02 | 2026-09-28 | 0 | 0 | 3 |
| GBPJPY | 6971 | 2000-01-03 | 1 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| GBPNZD | 4174 | 2010-05-10 | 0 | 0 | 0 | 278 | 2011-06-19 | 2026-09-28 | 191 | 0 | 2 |
| GBPUSD | 6970 | 2000-01-03 | 0 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| NZDCAD | 4957 | 2007-08-20 | 0 | 3 | 0 | 332 | 2008-08-13 | 2026-09-28 | 139 | 0 | 0 |
| NZDCHF | 4973 | 2007-08-21 | 0 | 0 | 0 | 332 | 2008-08-13 | 2026-09-28 | 139 | 0 | 0 |
| NZDJPY | 5117 | 2007-02-12 | 0 | 0 | 0 | 341 | 2008-02-15 | 2026-09-28 | 130 | 0 | 0 |
| NZDUSD | 6970 | 2000-01-03 | 0 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| USDCAD | 6970 | 2000-01-03 | 1 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| USDCHF | 6970 | 2000-01-03 | 1 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |
| USDJPY | 6970 | 2000-01-03 | 0 | 0 | 261 | 471 | 2001-01-02 | 2026-09-28 | 0 | 0 | 0 |

## Revisión de umbrales de TS-00-OBJ

Evaluación por código, sin mover umbrales. C1: ≤0,97 en ≥2 horizontes, ninguno >1,02. C2: rechazos Kupiec al 5% ≤10% en cada cola y horizonte. C3: P99 banda 1–99% ≤2×GARCH en cada horizonte, sobre los mismos orígenes comunes. CRPS rel. = mediana entre activos de los cocientes. Toto usa su submuestra con las bases; FinCast sólo CRPS deciles/QLIKE en limpia común. --cada 5 selecciona sobre orígenes válidos: la barra extra inicial puede adelantar la fase de la submuestra MT5 frente a la antigua; las bases se alinean a cada muestra sin reindexarla. Un activo/modelo/horizonte ausente o p-valor no finito deja el criterio no evaluable. Las cifras del piloto son provisionales y los tests tienen poca potencia.

Sensibilidad a la lectura alternativa agregada (no sustituye el veredicto por cada horizonte): C2 suma rechazos de h1/h5/h20 por cola y divide por la suma de activos-horizonte (84 si hay 28 pares en los tres); no son 84 activos distintos ni un nuevo test Kupiec. C3 calcula P99 sobre todas las anchuras de h1/h5/h20 juntas, y lo divide por el P99 conjunto de GARCH en los mismos orígenes; no promedia los cocientes por horizonte. C1 conserva su definición. FinCast mantiene C2/C3 no aplica en ambas lecturas.
### Antigua (yfinance, proxy)

| modelo | h | n activos | CRPS rel. | ≤0,97 | ≤1,02 | Kupiec rechazos 1%/99% | C2 | P99 banda/GARCH | C3 | QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|
| chronos2 | 1 | 28 | 1.0278396 | no pasa | no pasa | 1%: 14/28; 99%: 13/28 | no pasa | 1.59755187 | pasa | -10.0078043 |
| chronos2 | 5 | 28 | 1.00976289 | no pasa | pasa | 1%: 1/28; 99%: 0/28 | pasa | 1.07531157 | pasa | -8.3568443 |
| chronos2 | 20 | 28 | 0.972396116 | no pasa | pasa | 1%: 0/28; 99%: 0/28 | pasa | 1.2836521 | pasa | -7.01235228 |
| toto | 1 | 28 | 1.03878934 | no pasa | no pasa | 1%: 9/28; 99%: 5/28 | no pasa | 1.5523754 | pasa | -9.74791187 |
| toto | 5 | 28 | 1.02694875 | no pasa | no pasa | 1%: 1/28; 99%: 0/28 | pasa | 8.00922765 | no pasa | -8.28144986 |
| toto | 20 | 28 | 1.05869803 | no pasa | no pasa | 1%: 0/28; 99%: 0/28 | pasa | 27.5880304 | no pasa | -6.90755678 |
| hmm | 1 | 28 | 1.0016088 | no pasa | pasa | 1%: 2/28; 99%: 2/28 | pasa | 0.981528027 | pasa | -10.0124767 |
| hmm | 5 | 28 | 1.01729586 | no pasa | pasa | 1%: 1/28; 99%: 0/28 | pasa | 1.14480518 | pasa | -8.41003467 |
| hmm | 20 | 28 | 1.03672279 | no pasa | no pasa | 1%: 0/28; 99%: 0/28 | pasa | 1.29327266 | pasa | -7.03463483 |
| fincast | 1 | 28 | 1.08518922 | no pasa | no pasa | no aplica | no aplica | — | no aplica | -9.90872399 |
| fincast | 5 | 28 | 1.0289735 | no pasa | no pasa | no aplica | no aplica | — | no aplica | -8.41815967 |
| fincast | 20 | 28 | 0.952479172 | pasa | pasa | no aplica | no aplica | — | no aplica | -7.02209345 |


| modelo | condición | h1 | h5 | h20 | cada horizonte | cifra agregada | veredicto agregado | ¿cambia condición? |
|---|---|---|---|---|---|---|---|---|
| chronos2 | (2) Kupiec | 1%: 14/28; 99%: 13/28; no pasa | 1%: 1/28; 99%: 0/28; pasa | 1%: 0/28; 99%: 0/28; pasa | no pasa | 1%: 15/84; 99%: 13/84 | no pasa | no cambia |
| chronos2 | (3) banda P99/GARCH | 1.59755187; pasa | 1.07531157; pasa | 1.2836521; pasa | pasa | 1.23908118 | pasa | no cambia |
| toto | (2) Kupiec | 1%: 9/28; 99%: 5/28; no pasa | 1%: 1/28; 99%: 0/28; pasa | 1%: 0/28; 99%: 0/28; pasa | no pasa | 1%: 10/84; 99%: 5/84 | no pasa | no cambia |
| toto | (3) banda P99/GARCH | 1.5523754; pasa | 8.00922765; no pasa | 27.5880304; no pasa | no pasa | 17.7605747 | no pasa | no cambia |
| hmm | (2) Kupiec | 1%: 2/28; 99%: 2/28; pasa | 1%: 1/28; 99%: 0/28; pasa | 1%: 0/28; 99%: 0/28; pasa | pasa | 1%: 3/84; 99%: 2/84 | pasa | no cambia |
| hmm | (3) banda P99/GARCH | 0.981528027; pasa | 1.14480518; pasa | 1.29327266; pasa | pasa | 1.21332709 | pasa | no cambia |
| fincast | (2) Kupiec | no aplica | no aplica | no aplica | no aplica | no aplica | no aplica | no cambia |
| fincast | (3) banda P99/GARCH | no aplica | no aplica | no aplica | no aplica | no aplica | no aplica | no cambia |


| modelo | conclusión cada horizonte | conclusión agregada | ¿cambiaría veredicto del modelo? |
|---|---|---|---|
| chronos2 | no pasa | no pasa | no cambia |
| toto | no pasa | no pasa | no cambia |
| hmm | no pasa | no pasa | no cambia |
| fincast | no pasa | no pasa | no cambia |

### MT5 cabecera (proxy)

| modelo | h | n activos | CRPS rel. | ≤0,97 | ≤1,02 | Kupiec rechazos 1%/99% | C2 | P99 banda/GARCH | C3 | QLIKE |
|---|---|---|---|---|---|---|---|---|---|---|
| chronos2 | 1 | 28 | 1.02744796 | no pasa | no pasa | 1%: 14/28; 99%: 15/28 | no pasa | 1.6973144 | pasa | -10.0923781 |
| chronos2 | 5 | 28 | 1.00923716 | no pasa | pasa | 1%: 1/28; 99%: 0/28 | pasa | 1.15314436 | pasa | -8.47612537 |
| chronos2 | 20 | 28 | 0.974912203 | no pasa | pasa | 1%: 0/28; 99%: 0/28 | pasa | 1.33349745 | pasa | -7.08760747 |
| toto | 1 | 28 | 1.0607944 | no pasa | no pasa | 1%: 11/28; 99%: 5/28 | no pasa | 1.5646364 | pasa | -9.74629856 |
| toto | 5 | 28 | 1.02203178 | no pasa | no pasa | 1%: 1/28; 99%: 0/28 | pasa | 6.61038377 | no pasa | -8.32200002 |
| toto | 20 | 28 | 1.05398121 | no pasa | no pasa | 1%: 0/28; 99%: 0/28 | pasa | 30.0417992 | no pasa | -6.81852791 |
| hmm | 1 | 28 | 1.00157278 | no pasa | pasa | 1%: 4/28; 99%: 3/28 | no pasa | 1.04392331 | pasa | -10.0946906 |
| hmm | 5 | 28 | 1.00725467 | no pasa | pasa | 1%: 1/28; 99%: 1/28 | pasa | 1.13470573 | pasa | -8.47375123 |
| hmm | 20 | 28 | 1.02357595 | no pasa | no pasa | 1%: 0/28; 99%: 0/28 | pasa | 1.2072966 | pasa | -7.07895297 |
| fincast | 1 | 28 | 1.08470472 | no pasa | no pasa | no aplica | no aplica | — | no aplica | -9.76064864 |
| fincast | 5 | 28 | 1.03494852 | no pasa | no pasa | no aplica | no aplica | — | no aplica | -8.50486234 |
| fincast | 20 | 28 | 0.962210422 | pasa | pasa | no aplica | no aplica | — | no aplica | -7.1219255 |


| modelo | condición | h1 | h5 | h20 | cada horizonte | cifra agregada | veredicto agregado | ¿cambia condición? |
|---|---|---|---|---|---|---|---|---|
| chronos2 | (2) Kupiec | 1%: 14/28; 99%: 15/28; no pasa | 1%: 1/28; 99%: 0/28; pasa | 1%: 0/28; 99%: 0/28; pasa | no pasa | 1%: 15/84; 99%: 15/84 | no pasa | no cambia |
| chronos2 | (3) banda P99/GARCH | 1.6973144; pasa | 1.15314436; pasa | 1.33349745; pasa | pasa | 1.26887308 | pasa | no cambia |
| toto | (2) Kupiec | 1%: 11/28; 99%: 5/28; no pasa | 1%: 1/28; 99%: 0/28; pasa | 1%: 0/28; 99%: 0/28; pasa | no pasa | 1%: 12/84; 99%: 5/84 | no pasa | no cambia |
| toto | (3) banda P99/GARCH | 1.5646364; pasa | 6.61038377; no pasa | 30.0417992; no pasa | no pasa | 20.3815998 | no pasa | no cambia |
| hmm | (2) Kupiec | 1%: 4/28; 99%: 3/28; no pasa | 1%: 1/28; 99%: 1/28; pasa | 1%: 0/28; 99%: 0/28; pasa | no pasa | 1%: 5/84; 99%: 4/84 | pasa | cambia |
| hmm | (3) banda P99/GARCH | 1.04392331; pasa | 1.13470573; pasa | 1.2072966; pasa | pasa | 1.15261976 | pasa | no cambia |
| fincast | (2) Kupiec | no aplica | no aplica | no aplica | no aplica | no aplica | no aplica | no cambia |
| fincast | (3) banda P99/GARCH | no aplica | no aplica | no aplica | no aplica | no aplica | no aplica | no cambia |


| modelo | conclusión cada horizonte | conclusión agregada | ¿cambiaría veredicto del modelo? |
|---|---|---|---|
| chronos2 | no pasa | no pasa | no cambia |
| toto | no pasa | no pasa | no cambia |
| hmm | no pasa | no pasa | no cambia |
| fincast | no pasa | no pasa | no cambia |


| modelo | C1 antigua → MT5 | C2 antigua → MT5 | C3 antigua → MT5 | conclusión antigua → MT5 | ¿cambia conclusión? | alcance |
|---|---|---|---|---|---|---|
| chronos2 | no pasa → no pasa | no pasa → no pasa | pasa → pasa | no pasa → no pasa | no cambia | forecast M1: tres condiciones |
| toto | no pasa → no pasa | no pasa → no pasa | no pasa → no pasa | no pasa → no pasa | no cambia | forecast M1: tres condiciones |
| hmm | no pasa → no pasa | pasa → no pasa | pasa → pasa | no pasa → no pasa | no cambia | forecast M1: tres condiciones |
| fincast | no pasa → no pasa | no aplica → no aplica | no aplica → no aplica | no pasa → no pasa | no cambia | solo CRPS deciles limpio |

Cambia la conclusión (pasa ↔ no pasa) de algún modelo: **no**.

### Situación de partida

Rango [mín,máx] entre horizontes; cambia si cruza 1,00/0,97 o cambia el orden en algún horizonte. Rangos de HMM/Chronos: principal FX; Toto: submuestra FX; FinCast: deciles limpios comunes. Órdenes calculados dentro de tres grupos comparables: principal CRPS21, submuestra Toto CRPS21 y limpia común CRPS deciles (FinCast sólo en esta última). Los rangos publicados en TS-00-OBJ (0,967–1,05; etc.) abarcaban también Binance y submuestras del informe SPRINT-01; aquí se recalcula exclusivamente la cabecera FX especificada. Estado calculado: **cambia**.

| modelo | rango antiguo | rango MT5 |
|---|---|---|
| chronos2 | [0.9723961163390822, 1.0278395961325186] | [0.9749122034927806, 1.027447961523896] |
| toto | [1.0269487513480473, 1.0586980315194394] | [1.022031784758134, 1.060794402193161] |
| hmm | [1.0016087961662132, 1.0367227864079451] | [1.0015727780458992, 1.0235759498993666] |
| fincast | [0.9524791719003061, 1.085189218129262] | [0.9622104220974855, 1.0847047176680151] |

Cruces: `[]`.

Órdenes por horizonte: `[{"grupo": "principal_crps21", "h": 1, "antiguo": ["hmm", "chronos2"], "mt5": ["hmm", "chronos2"], "cambios": [], "estado": "calculado"}, {"grupo": "principal_crps21", "h": 5, "antiguo": ["chronos2", "hmm"], "mt5": ["hmm", "chronos2"], "cambios": [["hmm", "chronos2"]], "estado": "calculado"}, {"grupo": "principal_crps21", "h": 20, "antiguo": ["chronos2", "hmm"], "mt5": ["chronos2", "hmm"], "cambios": [], "estado": "calculado"}, {"grupo": "submuestra_toto_crps21", "h": 1, "antiguo": ["hmm", "chronos2", "toto"], "mt5": ["hmm", "chronos2", "toto"], "cambios": [], "estado": "calculado"}, {"grupo": "submuestra_toto_crps21", "h": 5, "antiguo": ["chronos2", "hmm", "toto"], "mt5": ["chronos2", "hmm", "toto"], "cambios": [], "estado": "calculado"}, {"grupo": "submuestra_toto_crps21", "h": 20, "antiguo": ["chronos2", "hmm", "toto"], "mt5": ["chronos2", "hmm", "toto"], "cambios": [], "estado": "calculado"}, {"grupo": "limpia_comun_crps_deciles", "h": 1, "antiguo": ["hmm", "chronos2", "toto", "fincast"], "mt5": ["hmm", "chronos2", "toto", "fincast"], "cambios": [], "estado": "calculado"}, {"grupo": "limpia_comun_crps_deciles", "h": 5, "antiguo": ["chronos2", "hmm", "toto", "fincast"], "mt5": ["chronos2", "hmm", "toto", "fincast"], "cambios": [], "estado": "calculado"}, {"grupo": "limpia_comun_crps_deciles", "h": 20, "antiguo": ["fincast", "chronos2", "toto", "hmm"], "mt5": ["chronos2", "fincast", "hmm", "toto"], "cambios": [["hmm", "toto"], ["chronos2", "fincast"]], "estado": "calculado"}]`.

## Test diferencial de la fuente de datos

Base de código fb11457: no cambian fórmulas, disponibilidad ni selección de orígenes. La única variación de datos es close 00:00 UTC de yfinance → cierre de sesion 17:00 NY de MT5. Estado de causas de orígenes: **explicado**. Se lista toda diferencia de validez en la rejilla y se marca si pertenece al piloto. --max-origenes limita inferencias, no la validez de la fuente contraria. Antes de inicio: 249 barras MT5 frente a 248 antiguas en cada par; el primer origen válido se adelanta un día.

ISSUE-LAGO-FX-1D-CLOSE: hay un desfase de una barra entre etiquetas. El close de yfinance fechado D es el precio de las 00:00 UTC de D y corresponde aproximadamente al cierre de la sesión MT5 anterior con datos (17:00 NY, aproximadamente 21:00/22:00 UTC de esa sesión). Se conservan Δy de la misma etiqueta de origen y Δy alineado: barra antigua D frente a la barra MT5 anterior a D con datos, usando h barras futuras de cada fuente. Se busca la sesión anterior por par, también al cruzar fines de semana o festivos; no se resta un día de calendario. Δy = y MT5 − y antigua. Esta alineación es sólo diagnóstica: no cambia la rejilla de orígenes ni las tablas de métricas o de umbrales; D15 compara cada tabla con su propia fuente.

Orígenes válidos totales: antigua 6916, MT5 6944; primeros válidos antiguos ['2025-10-22'], MT5 ['2025-10-21'].

| par | fecha | sólo en | en piloto | causa |
|---|---|---|---|---|
| AUDCAD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| AUDCHF | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| AUDJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| AUDNZD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| AUDUSD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| CADCHF | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| CADJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| CHFJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURAUD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURCAD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURCHF | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURGBP | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURNZD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| EURUSD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| GBPAUD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| GBPCAD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| GBPCHF | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| GBPJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| GBPNZD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| GBPUSD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| NZDCAD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| NZDCHF | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| NZDJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| NZDUSD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| USDCAD | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| USDCHF | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |
| USDJPY | 2025-10-21 | MT5 | True | barra extra antes de inicio (249 frente a 248) |


| alineación | h | orígenes comunes del piloto | mediana Δy pb | media abs(Δy) pb | mediana abs(Δy) pb | máximo abs(Δy) pb |
|---|---|---|---|---|---|---|
| misma etiqueta | 1 | 6916 | -0.561880478 | 42.6174427 | 32.5624863 | 280.640679 |
| misma etiqueta | 5 | 6916 | -0.919180178 | 41.8929782 | 31.8186011 | 286.918894 |
| misma etiqueta | 20 | 6916 | -0.330601825 | 41.8196388 | 31.5920957 | 281.567563 |
| alineado | 1 | 6916 | -0.0204880374 | 9.17008629 | 5.81797561 | 148.449381 |
| alineado | 5 | 6916 | -0.00238775494 | 8.49419324 | 5.14150838 | 138.95706 |
| alineado | 20 | 6916 | -0.0158513324 | 8.74551415 | 5.52424784 | 139.984945 |

### Diferencial por par y horizonte (pb)

| par | h | n misma etiqueta/alineado | media abs(Δy) misma etiqueta | media abs(Δy) alineado | mediana abs(Δy) misma etiqueta | mediana abs(Δy) alineado | máximo abs(Δy) misma etiqueta | máximo abs(Δy) alineado |
|---|---|---|---|---|---|---|---|---|
| AUDCAD | 1 | 247/247 | 43.9125167 | 10.5868715 | 33.120519 | 6.12394344 | 200.381139 | 113.102311 |
| AUDCAD | 5 | 247/247 | 41.8402771 | 9.45266849 | 32.3485385 | 5.59313043 | 164.621918 | 109.010105 |
| AUDCAD | 20 | 247/247 | 40.8159935 | 9.69524729 | 30.6242595 | 6.02118069 | 168.604779 | 107.761437 |
| AUDCHF | 1 | 247/247 | 49.1465841 | 10.2151881 | 40.7027109 | 7.37595242 | 239.008953 | 82.9597892 |
| AUDCHF | 5 | 247/247 | 42.9177685 | 9.40232568 | 33.5588681 | 6.04261486 | 218.488829 | 65.0239235 |
| AUDCHF | 20 | 247/247 | 44.4709749 | 9.65841308 | 33.1268465 | 6.60123332 | 179.010228 | 64.2189495 |
| AUDJPY | 1 | 247/247 | 58.3945555 | 12.7557938 | 48.5310004 | 8.68271934 | 261.046753 | 89.4542494 |
| AUDJPY | 5 | 247/247 | 59.1982763 | 11.8133309 | 48.29746 | 7.76838001 | 242.270564 | 83.930822 |
| AUDJPY | 20 | 247/247 | 57.4753319 | 11.6127681 | 44.248063 | 7.8688223 | 209.015797 | 83.1099259 |
| AUDNZD | 1 | 247/247 | 30.1297536 | 8.07313349 | 24.6003732 | 6.26204709 | 185.764988 | 30.8245694 |
| AUDNZD | 5 | 247/247 | 32.2738382 | 7.60552106 | 25.366536 | 6.41754945 | 185.381395 | 32.9634433 |
| AUDNZD | 20 | 247/247 | 34.4132406 | 8.14905685 | 29.0531045 | 6.57355174 | 182.981405 | 37.4192015 |
| AUDUSD | 1 | 247/247 | 58.2456595 | 13.1873876 | 54.0643016 | 7.10503992 | 240.088666 | 148.449381 |
| AUDUSD | 5 | 247/247 | 55.0900628 | 11.9979152 | 42.749476 | 6.55597063 | 270.06793 | 138.95706 |
| AUDUSD | 20 | 247/247 | 55.2066552 | 12.2152394 | 45.2502461 | 6.59040493 | 196.853015 | 139.373219 |
| CADCHF | 1 | 247/247 | 36.4345795 | 8.97313195 | 28.7177862 | 6.40803746 | 202.360422 | 59.8989652 |
| CADCHF | 5 | 247/247 | 35.7189742 | 7.51372301 | 27.5546028 | 4.73443973 | 159.507934 | 57.6260671 |
| CADCHF | 20 | 247/247 | 34.832456 | 8.30981826 | 26.5841061 | 5.62874583 | 157.340798 | 56.5845986 |
| CADJPY | 1 | 247/247 | 48.0634027 | 9.60450515 | 39.8885049 | 6.59229529 | 230.681452 | 42.8543384 |
| CADJPY | 5 | 247/247 | 49.2967006 | 9.0246469 | 35.0728987 | 5.6788631 | 264.88785 | 54.7860616 |
| CADJPY | 20 | 247/247 | 47.438274 | 8.70395096 | 35.5289831 | 5.93498493 | 237.837805 | 58.9482063 |
| CHFJPY | 1 | 247/247 | 47.7792213 | 8.64866589 | 38.4025334 | 6.85548963 | 175.719344 | 43.3734075 |
| CHFJPY | 5 | 247/247 | 49.7030333 | 8.07363922 | 40.1172035 | 5.46378065 | 205.135851 | 62.0528444 |
| CHFJPY | 20 | 247/247 | 48.2031476 | 8.3238487 | 35.6891487 | 5.7384045 | 219.951195 | 47.8468978 |
| EURAUD | 1 | 247/247 | 41.0515807 | 7.746656 | 34.7133175 | 5.30621736 | 189.691042 | 68.630765 |
| EURAUD | 5 | 247/247 | 39.469319 | 7.30389245 | 32.5510886 | 4.79899926 | 147.708609 | 65.4903869 |
| EURAUD | 20 | 247/247 | 36.7163827 | 7.22679321 | 28.1470579 | 4.78450706 | 131.286684 | 67.2683092 |
| EURCAD | 1 | 247/247 | 29.3449014 | 6.39618595 | 23.8543338 | 4.04878883 | 160.923289 | 51.4422186 |
| EURCAD | 5 | 247/247 | 27.3113003 | 5.70641742 | 20.3427778 | 3.54381296 | 138.040002 | 60.4059602 |
| EURCAD | 20 | 247/247 | 28.2013579 | 6.17941385 | 20.2756415 | 3.78310256 | 155.584434 | 61.7059212 |
| EURCHF | 1 | 247/247 | 28.2499606 | 4.85473876 | 20.8973971 | 3.69614705 | 139.465786 | 42.4710313 |
| EURCHF | 5 | 247/247 | 25.5338071 | 4.1464925 | 20.5567283 | 2.80506461 | 161.844698 | 40.1748156 |
| EURCHF | 20 | 247/247 | 26.8831216 | 4.71524503 | 21.1570741 | 2.88446295 | 129.794128 | 50.2316086 |
| EURGBP | 1 | 247/247 | 23.5760538 | 3.71154919 | 18.1469785 | 2.54653838 | 101.700066 | 24.0086085 |
| EURGBP | 5 | 247/247 | 21.5794477 | 3.43914832 | 16.9254604 | 2.42714413 | 83.0524973 | 31.6027212 |
| EURGBP | 20 | 247/247 | 21.7846959 | 3.61265574 | 17.6606336 | 2.8920622 | 78.3426335 | 30.9389933 |
| EURJPY | 1 | 247/247 | 40.3914284 | 8.46240577 | 28.5662959 | 6.37502869 | 225.178004 | 44.7538269 |
| EURJPY | 5 | 247/247 | 44.1370946 | 7.80003904 | 34.0005276 | 4.7864551 | 205.195427 | 47.4765263 |
| EURJPY | 20 | 247/247 | 42.1676315 | 8.16805296 | 28.8407318 | 5.48989467 | 207.043007 | 52.2850881 |
| EURNZD | 1 | 247/247 | 40.7909044 | 8.69830804 | 32.2488144 | 6.54459882 | 164.018429 | 52.8107114 |
| EURNZD | 5 | 247/247 | 39.7796176 | 8.34942823 | 34.8989428 | 6.58398378 | 195.93081 | 55.7232017 |
| EURNZD | 20 | 247/247 | 38.5477425 | 8.81281229 | 33.8433423 | 6.68596496 | 172.530729 | 66.4521885 |
| EURUSD | 1 | 247/247 | 35.3926411 | 9.19110282 | 26.4222486 | 4.60298386 | 189.843426 | 80.2149254 |
| EURUSD | 5 | 247/247 | 35.5422728 | 8.23809962 | 27.8399888 | 4.33348133 | 156.508489 | 97.6675524 |
| EURUSD | 20 | 247/247 | 36.1795136 | 8.69053272 | 27.7281408 | 4.61056268 | 153.988672 | 90.3820481 |
| GBPAUD | 1 | 247/247 | 41.5262601 | 7.76634394 | 35.7953524 | 5.41729771 | 125.788981 | 66.4904987 |
| GBPAUD | 5 | 247/247 | 39.6406817 | 7.32299824 | 34.6251463 | 4.57209649 | 136.61864 | 64.9625755 |
| GBPAUD | 20 | 247/247 | 40.6023028 | 7.24391384 | 33.4257981 | 4.74456207 | 165.112836 | 62.66583 |
| GBPCAD | 1 | 247/247 | 36.7749142 | 6.90611697 | 30.1411498 | 4.13914962 | 201.95287 | 53.214892 |
| GBPCAD | 5 | 247/247 | 33.5139727 | 6.2811228 | 28.4666766 | 3.68900846 | 133.742472 | 64.2211802 |
| GBPCAD | 20 | 247/247 | 35.1980864 | 6.25318264 | 26.9086097 | 3.65935422 | 183.547958 | 56.5998326 |
| GBPCHF | 1 | 247/247 | 35.1059837 | 5.95054715 | 26.5944265 | 4.51063705 | 190.591028 | 49.2354356 |
| GBPCHF | 5 | 247/247 | 31.2357075 | 5.01192254 | 25.050472 | 3.48954166 | 156.683712 | 42.6354213 |
| GBPCHF | 20 | 247/247 | 32.5459774 | 5.51844973 | 26.3339917 | 4.06821117 | 172.388697 | 55.9860107 |
| GBPJPY | 1 | 247/247 | 45.4501044 | 9.57932737 | 36.0146182 | 7.24169938 | 196.298338 | 47.0290699 |
| GBPJPY | 5 | 247/247 | 47.5708715 | 8.87027007 | 36.9718054 | 5.85535232 | 202.691327 | 49.9612117 |
| GBPJPY | 20 | 247/247 | 48.3395695 | 8.58973785 | 39.3355255 | 5.42938088 | 209.901452 | 49.5199109 |
| GBPNZD | 1 | 247/247 | 39.7235823 | 8.92413828 | 32.5129953 | 6.57585946 | 159.017883 | 45.1096904 |
| GBPNZD | 5 | 247/247 | 39.9435652 | 8.39885476 | 34.288569 | 6.54464318 | 202.442428 | 54.1218143 |
| GBPNZD | 20 | 247/247 | 39.1046458 | 8.41621926 | 34.8319212 | 5.96069154 | 187.067362 | 58.8276883 |
| GBPUSD | 1 | 247/247 | 43.7791224 | 9.44191134 | 38.5052653 | 4.7972161 | 201.434675 | 83.8609376 |
| GBPUSD | 5 | 247/247 | 41.5889278 | 8.74633756 | 32.8594264 | 5.02370745 | 192.609018 | 100.985385 |
| GBPUSD | 20 | 247/247 | 44.1409136 | 8.8124242 | 37.5890069 | 4.89478227 | 204.484793 | 79.9797247 |
| NZDCAD | 1 | 247/247 | 48.0283419 | 11.570823 | 38.9216951 | 7.87531465 | 223.979274 | 93.9829415 |
| NZDCAD | 5 | 247/247 | 47.8251754 | 10.9434543 | 39.8127605 | 7.7119874 | 205.263297 | 96.8124438 |
| NZDCAD | 20 | 247/247 | 47.4801472 | 11.7051258 | 37.9896829 | 7.82113135 | 224.125155 | 104.006851 |
| NZDCHF | 1 | 247/247 | 48.4769258 | 9.8436827 | 37.9657105 | 6.19075608 | 204.804522 | 63.4992972 |
| NZDCHF | 5 | 247/247 | 43.9508883 | 10.1587686 | 35.3819488 | 7.08722374 | 183.913725 | 58.3172079 |
| NZDCHF | 20 | 247/247 | 45.243331 | 10.7337326 | 38.6337821 | 8.01142928 | 205.6899 | 59.400971 |
| NZDJPY | 1 | 247/247 | 57.2116195 | 12.2714848 | 47.9430139 | 9.3369643 | 274.301333 | 73.1623108 |
| NZDJPY | 5 | 247/247 | 61.2559728 | 12.8773697 | 52.7924513 | 9.89735742 | 218.158981 | 73.4695235 |
| NZDJPY | 20 | 247/247 | 57.5693356 | 12.4708162 | 43.7712999 | 8.53292606 | 206.581766 | 80.7276185 |
| NZDUSD | 1 | 247/247 | 61.3076124 | 14.3406192 | 52.4471404 | 8.09271155 | 244.47879 | 129.017968 |
| NZDUSD | 5 | 247/247 | 60.4396799 | 13.5900612 | 45.2813689 | 8.34892749 | 229.82445 | 129.022221 |
| NZDUSD | 20 | 247/247 | 61.5038511 | 14.4473077 | 50.1543972 | 9.32091999 | 203.43848 | 139.984945 |
| USDCAD | 1 | 247/247 | 28.4654554 | 5.60788969 | 22.9397459 | 3.64458067 | 132.814888 | 35.4936278 |
| USDCAD | 5 | 247/247 | 28.4327996 | 5.09905246 | 20.4316563 | 3.31016519 | 159.576017 | 38.137449 |
| USDCAD | 20 | 247/247 | 28.6783057 | 5.34443677 | 22.7779936 | 3.75232033 | 126.397363 | 36.7713478 |
| USDCHF | 1 | 247/247 | 47.1956381 | 11.3135581 | 34.1035225 | 6.59349463 | 277.099058 | 91.9324724 |
| USDCHF | 5 | 247/247 | 48.1765094 | 9.62884978 | 38.5723363 | 5.19697641 | 230.339446 | 88.7970837 |
| USDCHF | 20 | 247/247 | 47.4444775 | 10.3263713 | 38.8058813 | 5.83543985 | 269.993289 | 91.0827444 |
| USDJPY | 1 | 247/247 | 49.3390911 | 12.1403497 | 36.6108945 | 8.13606893 | 280.640679 | 60.8429838 |
| USDJPY | 5 | 247/247 | 50.0368464 | 11.0410607 | 31.4855586 | 7.05198881 | 286.918894 | 81.3332502 |
| USDJPY | 20 | 247/247 | 49.7624243 | 10.93883 | 31.8667643 | 7.35085398 | 281.567563 | 58.3952473 |

### Correlación de retornos h=1 (Pearson, por par)

Misma muestra de orígenes del diferencial en las dos alineaciones; no se infieren predicciones adicionales. Si la varianza es cero o hay menos de dos retornos, no evaluable.

| par | n misma etiqueta/alineado | correlación misma etiqueta | correlación alineada |
|---|---|---|---|
| AUDCAD | 247/247 | -0.0666713951 | 0.906733144 |
| AUDCHF | 247/247 | -0.107262652 | 0.938528993 |
| AUDJPY | 247/247 | 0.0329774186 | 0.940609678 |
| AUDNZD | 247/247 | 0.131718402 | 0.939058832 |
| AUDUSD | 247/247 | -0.0116598336 | 0.899794359 |
| CADCHF | 247/247 | -0.0230524144 | 0.929151641 |
| CADJPY | 247/247 | 0.0413133483 | 0.959106342 |
| CHFJPY | 247/247 | 0.0363634325 | 0.966207479 |
| EURAUD | 247/247 | -0.0488511643 | 0.944242936 |
| EURCAD | 247/247 | -0.0561230148 | 0.93303076 |
| EURCHF | 247/247 | -0.120929373 | 0.958546133 |
| EURGBP | 247/247 | -0.0350343517 | 0.97047915 |
| EURJPY | 247/247 | 0.0628508891 | 0.961712004 |
| EURNZD | 247/247 | -0.047420147 | 0.945459694 |
| EURUSD | 247/247 | 0.0604712307 | 0.892674437 |
| GBPAUD | 247/247 | -0.0223234307 | 0.947143138 |
| GBPCAD | 247/247 | -0.108722685 | 0.946682022 |
| GBPCHF | 247/247 | -0.159921529 | 0.961864552 |
| GBPJPY | 247/247 | 0.0625800432 | 0.957860279 |
| GBPNZD | 247/247 | -0.013481224 | 0.943684615 |
| GBPUSD | 247/247 | 0.0103787048 | 0.914838415 |
| NZDCAD | 247/247 | -0.0828840398 | 0.923401411 |
| NZDCHF | 247/247 | -0.156390035 | 0.943683299 |
| NZDJPY | 247/247 | 0.0592127203 | 0.950572844 |
| NZDUSD | 247/247 | 0.00520566943 | 0.914194883 |
| USDCAD | 247/247 | 0.0964069716 | 0.952791844 |
| USDCHF | 247/247 | 0.00379894265 | 0.921588745 |
| USDJPY | 247/247 | 0.0538168635 | 0.941629168 |

### Control de escala h=1 en toda la rejilla de cabecera

Diagnóstico adicional desde los datasets, sin nuevas inferencias: EURUSD y USDJPY en todos los orígenes válidos comunes de la misma rejilla (ventana 250 y 20 futuros exigidos). El número de retornos de cada muestra figura en las tablas. Se muestran ambas muestras por separado para contrastar el orden de magnitud de unos 7–10 pb medido en la revisión; no se sustituyen los registros ni los extremos de las corridas suministradas.

| par | n | media abs(Δy) misma etiqueta pb | media abs(Δy) alineado pb | correlación misma etiqueta | correlación alineada |
|---|---|---|---|---|---|
| EURUSD | 247 | 35.3926411 | 9.19110282 | 0.0604712307 | 0.892674437 |
| USDJPY | 247 | 49.3390911 | 12.1403497 | 0.0538168635 | 0.941629168 |

### Extremos del Δy alineado

Casos |Δy alineado| > 5×mediana de |Δy alineado| de ese par/h: revisión humana por la raíz, sin umbral de aceptación de Δy. La regla se aplica exclusivamente al diferencial alineado; el diferencial de la misma etiqueta queda como dato.

| par | fecha origen | barra antigua | sesión MT5 alineada | h | Δy alineado pb | Δy misma etiqueta pb | mediana abs(Δy alineado) par/h pb |
|---|---|---|---|---|---|---|---|
| AUDCAD | 2025-10-25 | 2025-10-24 | 2025-10-23 | 1 | -34.4048488 | 32.4440064 | 6.12394344 |
| AUDCAD | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -39.8077187 | -102.778318 | 6.12394344 |
| AUDCAD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 51.7428877 | 62.2408923 | 6.12394344 |
| AUDCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -73.2657347 | -152.785127 | 6.12394344 |
| AUDCAD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 62.071519 | 200.381139 | 6.12394344 |
| AUDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -48.5338885 | -80.2583486 | 6.12394344 |
| AUDCAD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 1 | 30.9802859 | 27.8495205 | 6.12394344 |
| AUDCAD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -111.648246 | -112.711164 | 6.12394344 |
| AUDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 113.102311 | 81.2372731 | 6.12394344 |
| AUDCAD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | 38.7500426 | 50.5059293 | 6.12394344 |
| AUDCAD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | -42.7379099 | -26.7249684 | 6.12394344 |
| AUDCAD | 2026-05-23 | 2026-05-22 | 2026-05-21 | 1 | -33.8717169 | 16.6453743 | 6.12394344 |
| AUDCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 34.7477321 | -23.1554753 | 6.12394344 |
| AUDCAD | 2026-09-12 | 2026-09-11 | 2026-09-10 | 1 | 31.6226251 | -39.6033034 | 6.12394344 |
| AUDCAD | 2025-10-28 | 2025-10-27 | 2025-10-24 | 5 | 32.44781 | -14.1335398 | 5.59313043 |
| AUDCAD | 2026-01-20 | 2026-01-19 | 2026-01-16 | 5 | -34.6696324 | -10.0301399 | 5.59313043 |
| AUDCAD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | 38.5900526 | 27.7339877 | 5.59313043 |
| AUDCAD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | -31.304328 | -26.3818637 | 5.59313043 |
| AUDCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 77.620459 | 100.26657 | 5.59313043 |
| AUDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -85.1056017 | -72.1119275 | 5.59313043 |
| AUDCAD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 5 | -29.1121325 | 140.29162 | 5.59313043 |
| AUDCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 52.8812326 | -58.4584745 | 5.59313043 |
| AUDCAD | 2026-03-26 | 2026-03-25 | 2026-03-24 | 5 | -28.5730317 | 20.3334602 | 5.59313043 |
| AUDCAD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -89.619277 | -34.4895124 | 5.59313043 |
| AUDCAD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 29.7032878 | 28.7465655 | 5.59313043 |
| AUDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 109.010105 | 86.8918432 | 5.59313043 |
| AUDCAD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 5 | -31.6490763 | 4.10034736 | 5.59313043 |
| AUDCAD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -38.88214 | -13.3829689 | 5.59313043 |
| AUDCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 31.6130918 | -19.7260518 | 5.59313043 |
| AUDCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 29.7796931 | -26.576104 | 5.59313043 |
| AUDCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 5 | 27.9867946 | -30.0165094 | 5.59313043 |
| AUDCAD | 2026-09-08 | 2026-09-07 | 2026-09-04 | 5 | 29.2023435 | 4.14942915 | 5.59313043 |
| AUDCAD | 2026-09-15 | 2026-09-14 | 2026-09-11 | 5 | -32.815198 | 18.3977544 | 5.59313043 |
| AUDCAD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 50.7586254 | 21.0398503 | 6.02118069 |
| AUDCAD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 81.1389665 | 136.809901 | 6.02118069 |
| AUDCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | 44.4721031 | 59.0843548 | 6.02118069 |
| AUDCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -32.5878817 | -35.1750255 | 6.02118069 |
| AUDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -45.409684 | -123.178978 | 6.02118069 |
| AUDCAD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -107.761437 | -98.0325266 | 6.02118069 |
| AUDCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 69.3992056 | -22.3204848 | 6.02118069 |
| AUDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 94.601149 | 113.437396 | 6.02118069 |
| AUDCAD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 20 | -35.0782058 | -35.2728738 | 6.02118069 |
| AUDCAD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -31.0527413 | 2.67975856 | 6.02118069 |
| AUDCAD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | -40.2901371 | -26.9153941 | 6.02118069 |
| AUDCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | 38.0502472 | -53.8196926 | 6.02118069 |
| AUDCAD | 2026-08-18 | 2026-08-17 | 2026-08-14 | 20 | 31.7378144 | -20.6864785 | 6.02118069 |
| AUDCHF | 2025-10-25 | 2025-10-24 | 2025-10-23 | 1 | -40.5397592 | 29.9033387 | 7.37595242 |
| AUDCHF | 2025-10-28 | 2025-10-27 | 2025-10-24 | 1 | 48.4644246 | -2.61969865 | 7.37595242 |
| AUDCHF | 2025-11-11 | 2025-11-10 | 2025-11-07 | 1 | 39.3460383 | -94.1761722 | 7.37595242 |
| AUDCHF | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | 51.7135848 | 54.8113237 | 7.37595242 |
| AUDCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | -48.0092356 | -82.786038 | 7.37595242 |
| AUDCHF | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | 39.3092646 | -136.389431 | 7.37595242 |
| AUDCHF | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -47.0265813 | -158.694043 | 7.37595242 |
| AUDCHF | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 60.2632519 | 211.483831 | 7.37595242 |
| AUDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -82.9597892 | -239.008953 | 7.37595242 |
| AUDCHF | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -53.2840809 | -114.00629 | 7.37595242 |
| AUDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 58.1231781 | 84.9238277 | 7.37595242 |
| AUDCHF | 2025-10-28 | 2025-10-27 | 2025-10-24 | 5 | 37.3088312 | -0.126307258 | 6.04261486 |
| AUDCHF | 2025-11-04 | 2025-11-03 | 2025-10-31 | 5 | -34.4311453 | -1.24518763 | 6.04261486 |
| AUDCHF | 2025-11-11 | 2025-11-10 | 2025-11-07 | 5 | 37.204518 | -63.9467434 | 6.04261486 |
| AUDCHF | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 53.7953823 | 37.7579509 | 6.04261486 |
| AUDCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 5 | -44.2806754 | -28.9463908 | 6.04261486 |
| AUDCHF | 2026-01-23 | 2026-01-22 | 2026-01-21 | 5 | 36.1165889 | -37.8638157 | 6.04261486 |
| AUDCHF | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | -38.4980631 | -122.882079 | 6.04261486 |
| AUDCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 65.0239235 | 218.488829 | 6.04261486 |
| AUDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | -56.0939882 | -69.6970536 | 6.04261486 |
| AUDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -39.1705679 | -44.080914 | 6.04261486 |
| AUDCHF | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 40.0567664 | -79.6507978 | 6.04261486 |
| AUDCHF | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -34.7530747 | 9.25471714 | 6.04261486 |
| AUDCHF | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -45.942294 | -4.74253019 | 6.04261486 |
| AUDCHF | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 41.2819716 | -10.4886898 | 6.04261486 |
| AUDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 52.1259429 | 108.108361 | 6.04261486 |
| AUDCHF | 2026-04-21 | 2026-04-20 | 2026-04-17 | 5 | -33.9012936 | 53.3315865 | 6.04261486 |
| AUDCHF | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | 39.744024 | -18.3758688 | 6.60123332 |
| AUDCHF | 2025-12-19 | 2025-12-18 | 2025-12-17 | 20 | 36.5517091 | 19.3520865 | 6.60123332 |
| AUDCHF | 2026-01-01 | 2025-12-31 | 2025-12-30 | 20 | 35.6590178 | 24.3599627 | 6.60123332 |
| AUDCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -61.7772498 | -3.82174627 | 6.60123332 |
| AUDCHF | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 64.2189495 | 96.1716401 | 6.60123332 |
| AUDCHF | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 46.6230244 | 149.356666 | 6.60123332 |
| AUDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -56.0385862 | -179.010228 | 6.60123332 |
| AUDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -34.6976727 | -100.058457 | 6.60123332 |
| AUDCHF | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -50.8348622 | -105.88282 | 6.60123332 |
| AUDCHF | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 45.7548668 | -66.4662333 | 6.60123332 |
| AUDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 47.1749011 | 48.4010802 | 6.60123332 |
| AUDCHF | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | -38.1889268 | 66.605938 | 6.60123332 |
| AUDJPY | 2025-10-28 | 2025-10-27 | 2025-10-24 | 1 | 53.4903637 | -19.9787002 | 8.68271934 |
| AUDJPY | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -58.1221552 | -173.712886 | 8.68271934 |
| AUDJPY | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -52.9025859 | -170.526058 | 8.68271934 |
| AUDJPY | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 49.5525098 | 71.8158221 | 8.68271934 |
| AUDJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -45.3832094 | -24.7874548 | 8.68271934 |
| AUDJPY | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -89.4542494 | -137.408522 | 8.68271934 |
| AUDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 86.9263335 | 140.977208 | 8.68271934 |
| AUDJPY | 2025-11-25 | 2025-11-24 | 2025-11-21 | 5 | 39.0431257 | -57.7816303 | 7.76838001 |
| AUDJPY | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 45.7579952 | 38.5487222 | 7.76838001 |
| AUDJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -71.1810815 | -48.2174141 | 7.76838001 |
| AUDJPY | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 43.3488561 | -109.074259 | 7.76838001 |
| AUDJPY | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -69.6710081 | -82.3595191 | 7.76838001 |
| AUDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 83.930822 | 126.177048 | 7.76838001 |
| AUDJPY | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -42.2005311 | -31.1526721 | 7.76838001 |
| AUDJPY | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | 41.4331162 | -52.4575329 | 7.8688223 |
| AUDJPY | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -39.406023 | -25.6009896 | 7.8688223 |
| AUDJPY | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 49.66773 | 68.3465902 | 7.8688223 |
| AUDJPY | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 70.9188475 | 110.407049 | 7.8688223 |
| AUDJPY | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -83.1099259 | -157.137986 | 7.8688223 |
| AUDJPY | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 70.0460034 | 32.6863765 | 7.8688223 |
| AUDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 71.3400859 | 19.4016295 | 7.8688223 |
| AUDJPY | 2026-04-14 | 2026-04-13 | 2026-04-10 | 20 | -39.6602512 | -49.893 | 7.8688223 |
| AUDJPY | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | -48.1837107 | -36.7637994 | 7.8688223 |
| AUDNZD | 2026-04-22 | 2026-04-21 | 2026-04-20 | 5 | -32.9634433 | 40.0049657 | 6.41754945 |
| AUDNZD | 2026-04-22 | 2026-04-21 | 2026-04-20 | 20 | -37.2165765 | -17.6827768 | 6.57355174 |
| AUDNZD | 2026-07-09 | 2026-07-08 | 2026-07-07 | 20 | -37.4192015 | 26.0314185 | 6.57355174 |
| AUDNZD | 2026-08-06 | 2026-08-05 | 2026-08-04 | 20 | 35.3847944 | 112.089037 | 6.57355174 |
| AUDUSD | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -40.2329644 | -59.4559792 | 7.10503992 |
| AUDUSD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 1 | 38.0272977 | -97.7962614 | 7.10503992 |
| AUDUSD | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | -41.7138533 | -118.518579 | 7.10503992 |
| AUDUSD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 71.1338247 | 35.241007 | 7.10503992 |
| AUDUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -93.8105647 | -152.002373 | 7.10503992 |
| AUDUSD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 91.1848273 | 136.436632 | 7.10503992 |
| AUDUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -74.0038301 | -87.2932977 | 7.10503992 |
| AUDUSD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 1 | 35.8513119 | -118.920319 | 7.10503992 |
| AUDUSD | 2026-03-14 | 2026-03-13 | 2026-03-12 | 1 | -36.7508977 | 228.380801 | 7.10503992 |
| AUDUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 1 | 40.3037021 | -42.5221913 | 7.10503992 |
| AUDUSD | 2026-04-01 | 2026-03-31 | 2026-03-30 | 1 | -39.3148496 | -66.8863442 | 7.10503992 |
| AUDUSD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 1 | 36.4702262 | -31.7759304 | 7.10503992 |
| AUDUSD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -145.035812 | -133.082267 | 7.10503992 |
| AUDUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 148.449381 | 109.357813 | 7.10503992 |
| AUDUSD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | 58.3978242 | 118.147381 | 7.10503992 |
| AUDUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | -73.4989028 | -69.5798288 | 7.10503992 |
| AUDUSD | 2026-04-18 | 2026-04-17 | 2026-04-16 | 1 | 41.8186182 | 48.0830514 | 7.10503992 |
| AUDUSD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 1 | -40.2909107 | -88.142538 | 7.10503992 |
| AUDUSD | 2026-05-23 | 2026-05-22 | 2026-05-21 | 1 | -42.8459623 | 53.8374203 | 7.10503992 |
| AUDUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 48.0023553 | -29.4377537 | 7.10503992 |
| AUDUSD | 2026-06-13 | 2026-06-12 | 2026-06-11 | 1 | -52.7042073 | 1.73883725 | 7.10503992 |
| AUDUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 1 | 43.4981066 | -1.42236401 | 7.10503992 |
| AUDUSD | 2025-10-28 | 2025-10-27 | 2025-10-24 | 5 | 33.079835 | -45.2610237 | 6.55597063 |
| AUDUSD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | 43.0611515 | -1.71155781 | 6.55597063 |
| AUDUSD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | -42.4948703 | 82.9074028 | 6.55597063 |
| AUDUSD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | -36.7616217 | -81.6035027 | 6.55597063 |
| AUDUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 115.793827 | 129.782999 | 6.55597063 |
| AUDUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -121.659096 | -64.036299 | 6.55597063 |
| AUDUSD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 5 | -41.4575317 | 157.085504 | 6.55597063 |
| AUDUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 53.5721012 | -91.208398 | 6.55597063 |
| AUDUSD | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -39.325944 | 45.0455633 | 6.55597063 |
| AUDUSD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -113.47572 | -59.5415536 | 6.55597063 |
| AUDUSD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 75.700388 | 60.1743725 | 6.55597063 |
| AUDUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 138.95706 | 105.626624 | 6.55597063 |
| AUDUSD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 5 | -33.8372804 | -1.60471402 | 6.55597063 |
| AUDUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -62.4606749 | -28.7340844 | 6.55597063 |
| AUDUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 47.1589665 | -52.865737 | 6.55597063 |
| AUDUSD | 2026-06-09 | 2026-06-08 | 2026-06-05 | 5 | -42.4898346 | -9.48057117 | 6.55597063 |
| AUDUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 55.164272 | 3.77757341 | 6.55597063 |
| AUDUSD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 58.3301031 | 48.5452352 | 6.59040493 |
| AUDUSD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 109.533016 | 72.7174276 | 6.59040493 |
| AUDUSD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 20 | -33.918847 | 91.2227928 | 6.59040493 |
| AUDUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | 56.4148759 | 81.6178975 | 6.59040493 |
| AUDUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -44.5712461 | -47.9754684 | 6.59040493 |
| AUDUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -92.6052329 | -110.0095 | 6.59040493 |
| AUDUSD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -139.373219 | -91.3021118 | 6.59040493 |
| AUDUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 104.754251 | 14.2011714 | 6.59040493 |
| AUDUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 113.836337 | 93.846245 | 6.59040493 |
| AUDUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 20 | -56.4117411 | -90.8314815 | 6.59040493 |
| AUDUSD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -53.3381999 | -33.7864388 | 6.59040493 |
| AUDUSD | 2026-05-07 | 2026-05-06 | 2026-05-05 | 20 | 36.8350967 | -111.171854 | 6.59040493 |
| AUDUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | -68.6177794 | -60.7817253 | 6.59040493 |
| AUDUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | 49.0071675 | -28.2700675 | 6.59040493 |
| AUDUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | 62.5690276 | -29.0165007 | 6.59040493 |
| AUDUSD | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | -46.1819677 | 13.5448848 | 6.59040493 |
| CADCHF | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | 43.4099159 | 32.3979598 | 6.40803746 |
| CADCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | -43.4341446 | -79.937284 | 6.40803746 |
| CADCHF | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | 36.0021844 | -73.4631838 | 6.40803746 |
| CADCHF | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | -40.1300513 | -54.8316093 | 6.40803746 |
| CADCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | 33.6660692 | 52.8747103 | 6.40803746 |
| CADCHF | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 59.8989652 | -1.34651043 | 6.40803746 |
| CADCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -54.8300006 | 2.61626151 | 6.40803746 |
| CADCHF | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | -35.2648807 | 15.9906675 | 6.40803746 |
| CADCHF | 2025-11-04 | 2025-11-03 | 2025-10-31 | 5 | -25.9745585 | -22.28545 | 4.73443973 |
| CADCHF | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 49.6810153 | 33.0363261 | 4.73443973 |
| CADCHF | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -25.1528973 | 63.1837402 | 4.73443973 |
| CADCHF | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | 35.7270053 | -0.540978723 | 4.73443973 |
| CADCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | -55.3829607 | -159.507934 | 4.73443973 |
| CADCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 45.5202287 | 29.5329914 | 4.73443973 |
| CADCHF | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 46.6588024 | 32.8369274 | 4.73443973 |
| CADCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -57.6260671 | 20.6524958 | 4.73443973 |
| CADCHF | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | 28.4025475 | 31.4223569 | 4.73443973 |
| CADCHF | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | -45.8703416 | 18.6613414 | 4.73443973 |
| CADCHF | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | -32.8486747 | 27.5546028 | 4.73443973 |
| CADCHF | 2026-07-21 | 2026-07-20 | 2026-07-17 | 5 | 33.0287708 | 23.880458 | 4.73443973 |
| CADCHF | 2026-08-25 | 2026-08-24 | 2026-08-21 | 5 | -25.4653559 | 40.9136286 | 4.73443973 |
| CADCHF | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | 32.0508705 | 19.2218025 | 5.62874583 |
| CADCHF | 2025-12-19 | 2025-12-18 | 2025-12-17 | 20 | 36.3127572 | 12.8490785 | 5.62874583 |
| CADCHF | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 41.4923398 | -29.4105454 | 5.62874583 |
| CADCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -49.0158898 | 0.258661849 | 5.62874583 |
| CADCHF | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -31.3158489 | 11.7585774 | 5.62874583 |
| CADCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | -35.0248605 | -34.3969067 | 5.62874583 |
| CADCHF | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 56.5845986 | -8.674683 | 5.62874583 |
| CADCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -47.3654684 | -65.678078 | 5.62874583 |
| CADCHF | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | 41.8177172 | -20.1497027 | 5.62874583 |
| CADCHF | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | -43.8444123 | 6.93165383 | 5.62874583 |
| CADCHF | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | -29.3106467 | 79.0821157 | 5.62874583 |
| CADJPY | 2026-01-24 | 2026-01-23 | 2026-01-22 | 1 | 42.8543384 | 48.9311716 | 6.59229529 |
| CADJPY | 2026-01-27 | 2026-01-26 | 2026-01-23 | 1 | -40.9288393 | 25.2246852 | 6.59229529 |
| CADJPY | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | -34.037705 | 2.14849918 | 6.59229529 |
| CADJPY | 2026-05-02 | 2026-05-01 | 2026-04-30 | 1 | 35.9377785 | 1.29625271 | 6.59229529 |
| CADJPY | 2026-07-31 | 2026-07-30 | 2026-07-29 | 1 | -39.5039186 | 49.7573451 | 6.59229529 |
| CADJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 1 | 39.2849218 | 115.557949 | 6.59229529 |
| CADJPY | 2025-11-25 | 2025-11-24 | 2025-11-21 | 5 | 35.4461456 | -54.3460974 | 5.6788631 |
| CADJPY | 2025-12-19 | 2025-12-18 | 2025-12-17 | 5 | -31.4094685 | 20.0933278 | 5.6788631 |
| CADJPY | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 40.7922485 | 33.6369753 | 5.6788631 |
| CADJPY | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -54.7860616 | 58.8910411 | 5.6788631 |
| CADJPY | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | 29.033093 | -49.1302165 | 5.6788631 |
| CADJPY | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -41.7467144 | 53.0152839 | 5.6788631 |
| CADJPY | 2026-07-25 | 2026-07-24 | 2026-07-23 | 5 | -41.2236512 | -158.388247 | 5.6788631 |
| CADJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 5 | 40.6939371 | 175.554907 | 5.6788631 |
| CADJPY | 2026-09-03 | 2026-09-02 | 2026-09-01 | 5 | 30.9667357 | 40.904742 | 5.6788631 |
| CADJPY | 2026-09-09 | 2026-09-08 | 2026-09-07 | 5 | -28.9659469 | 6.28125655 | 5.6788631 |
| CADJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 5 | -37.9229083 | 35.0728987 | 5.6788631 |
| CADJPY | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | 33.3796327 | -15.5612255 | 5.93498493 |
| CADJPY | 2025-11-28 | 2025-11-27 | 2025-11-26 | 20 | -34.2032136 | 16.3229901 | 5.93498493 |
| CADJPY | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 58.9482063 | -95.3175857 | 5.93498493 |
| CADJPY | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -29.861782 | -24.8566489 | 5.93498493 |
| CADJPY | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | -33.9060404 | -47.9391262 | 5.93498493 |
| CADJPY | 2026-04-07 | 2026-04-06 | 2026-04-03 | 20 | 30.0257762 | -20.9224783 | 5.93498493 |
| CADJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 20 | 41.4321456 | 171.537619 | 5.93498493 |
| CADJPY | 2026-08-13 | 2026-08-12 | 2026-08-11 | 20 | 31.5897585 | -11.6975859 | 5.93498493 |
| CADJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 20 | -37.843523 | -28.1944868 | 5.93498493 |
| CHFJPY | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | -43.3734075 | -143.842553 | 6.85548963 |
| CHFJPY | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | 35.3893652 | 66.4402701 | 6.85548963 |
| CHFJPY | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -34.8463987 | -18.5098621 | 6.85548963 |
| CHFJPY | 2026-07-31 | 2026-07-30 | 2026-07-29 | 1 | -37.0060994 | -59.679055 | 6.85548963 |
| CHFJPY | 2025-11-25 | 2025-11-24 | 2025-11-21 | 5 | 30.5589922 | -64.4224362 | 5.46378065 |
| CHFJPY | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -31.297285 | -63.2642651 | 5.46378065 |
| CHFJPY | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | 62.0528444 | 85.1615574 | 5.46378065 |
| CHFJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -32.8215592 | -8.37350271 | 5.46378065 |
| CHFJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 36.2827736 | 16.2654669 | 5.46378065 |
| CHFJPY | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 28.0636389 | -10.4649854 | 5.46378065 |
| CHFJPY | 2026-07-25 | 2026-07-24 | 2026-07-23 | 5 | -31.2808254 | -173.471744 | 5.46378065 |
| CHFJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 5 | 33.8756813 | 205.135851 | 5.46378065 |
| CHFJPY | 2026-08-05 | 2026-08-04 | 2026-08-03 | 5 | 28.8835207 | -35.4034881 | 5.46378065 |
| CHFJPY | 2026-09-09 | 2026-09-08 | 2026-09-07 | 5 | -30.7936771 | 25.515531 | 5.46378065 |
| CHFJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 5 | -33.9231483 | -8.24547446 | 5.46378065 |
| CHFJPY | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | 47.8468978 | 53.107307 | 5.7384045 |
| CHFJPY | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -31.3547109 | -47.7425846 | 5.7384045 |
| CHFJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 30.1376173 | -29.5902245 | 5.7384045 |
| CHFJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 20 | 30.2342586 | 165.553288 | 5.7384045 |
| CHFJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 20 | -30.2522915 | -16.7644734 | 5.7384045 |
| EURAUD | 2025-10-28 | 2025-10-27 | 2025-10-24 | 1 | -30.0226351 | -17.3285162 | 5.30621736 |
| EURAUD | 2025-11-11 | 2025-11-10 | 2025-11-07 | 1 | -30.2793589 | 72.9915886 | 5.30621736 |
| EURAUD | 2026-01-31 | 2026-01-30 | 2026-01-29 | 1 | -27.8264655 | -70.9071722 | 5.30621736 |
| EURAUD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 1 | 31.8344585 | -26.8240767 | 5.30621736 |
| EURAUD | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | 30.1304126 | 104.410376 | 5.30621736 |
| EURAUD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | -27.7122079 | -97.6310322 | 5.30621736 |
| EURAUD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | 48.8143061 | 139.454361 | 5.30621736 |
| EURAUD | 2026-03-14 | 2026-03-13 | 2026-03-12 | 1 | 28.6903036 | -73.6494912 | 5.30621736 |
| EURAUD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 67.0493029 | 64.3776828 | 5.30621736 |
| EURAUD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -68.630765 | -54.7278504 | 5.30621736 |
| EURAUD | 2026-04-18 | 2026-04-17 | 2026-04-16 | 1 | -32.8814881 | 14.3217055 | 5.30621736 |
| EURAUD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 1 | 32.7530786 | 14.9582527 | 5.30621736 |
| EURAUD | 2025-11-11 | 2025-11-10 | 2025-11-07 | 5 | -29.7605489 | 80.608317 | 4.79899926 |
| EURAUD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -24.5622143 | -66.7641121 | 4.79899926 |
| EURAUD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | 41.7939213 | 42.6700322 | 4.79899926 |
| EURAUD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -32.418036 | -147.708609 | 4.79899926 |
| EURAUD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | 24.1508101 | 50.6582998 | 4.79899926 |
| EURAUD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 32.032179 | 28.1835098 | 4.79899926 |
| EURAUD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | -32.9207705 | 72.4518309 | 4.79899926 |
| EURAUD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 55.8093473 | 25.1707809 | 4.79899926 |
| EURAUD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -65.4903869 | -83.939984 | 4.79899926 |
| EURAUD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 5 | 38.2365971 | -24.651194 | 4.79899926 |
| EURAUD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | 24.6443282 | -6.86329605 | 4.79899926 |
| EURAUD | 2026-09-08 | 2026-09-07 | 2026-09-04 | 5 | -24.8370987 | -10.5688575 | 4.79899926 |
| EURAUD | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | -38.7428421 | 54.3776678 | 4.78450706 |
| EURAUD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -28.0091187 | -50.58047 | 4.78450706 |
| EURAUD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 20 | 25.1451004 | -15.7589835 | 4.78450706 |
| EURAUD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 67.2683092 | 110.735085 | 4.78450706 |
| EURAUD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | -43.642656 | -4.77023627 | 4.78450706 |
| EURAUD | 2026-03-31 | 2026-03-30 | 2026-03-27 | 20 | 26.481819 | -17.0053909 | 4.78450706 |
| EURAUD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -56.393414 | -45.2678395 | 4.78450706 |
| EURAUD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | 26.9193272 | 12.7001163 | 4.78450706 |
| EURAUD | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | 49.7553356 | -13.3861557 | 4.78450706 |
| EURCAD | 2026-01-24 | 2026-01-23 | 2026-01-22 | 1 | -30.701157 | 25.5851699 | 4.04878883 |
| EURCAD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 1 | 29.7734818 | 13.5389365 | 4.04878883 |
| EURCAD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 31.5569364 | -41.4962778 | 4.04878883 |
| EURCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -31.0055768 | -13.8705784 | 4.04878883 |
| EURCAD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 51.4422186 | 154.641294 | 4.04878883 |
| EURCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -39.5911023 | -98.6426288 | 4.04878883 |
| EURCAD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 1 | -21.1387466 | -22.5033103 | 4.04878883 |
| EURCAD | 2026-03-20 | 2026-03-19 | 2026-03-18 | 1 | 21.4149611 | -131.596453 | 4.04878883 |
| EURCAD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -44.1778544 | -48.5447724 | 4.04878883 |
| EURCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 44.9233869 | 27.2945007 | 4.04878883 |
| EURCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 24.6054872 | -1.05821208 | 4.04878883 |
| EURCAD | 2026-08-22 | 2026-08-21 | 2026-08-20 | 1 | -23.365984 | 41.0921096 | 4.04878883 |
| EURCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 1 | 22.933341 | -17.0587807 | 4.04878883 |
| EURCAD | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | -20.2948002 | -16.692256 | 3.54381296 |
| EURCAD | 2026-01-20 | 2026-01-19 | 2026-01-16 | 5 | -18.1960147 | 27.3866647 | 3.54381296 |
| EURCAD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | 22.9036086 | -40.4607651 | 3.54381296 |
| EURCAD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | -22.4368837 | -7.24572791 | 3.54381296 |
| EURCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 52.4452942 | -46.276738 | 3.54381296 |
| EURCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | 23.6461218 | 138.040002 | 3.54381296 |
| EURCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -60.4059602 | -43.0027691 | 3.54381296 |
| EURCAD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 5 | -23.6041648 | 115.941857 | 3.54381296 |
| EURCAD | 2026-03-14 | 2026-03-13 | 2026-03-12 | 5 | 18.9495429 | 6.8487144 | 3.54381296 |
| EURCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 22.0789105 | 12.5477831 | 3.54381296 |
| EURCAD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -36.0319019 | -11.353255 | 3.54381296 |
| EURCAD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 17.7621105 | 11.6348169 | 3.54381296 |
| EURCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 41.3488184 | 0.813791906 | 3.54381296 |
| EURCAD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -19.1193293 | -18.884104 | 3.54381296 |
| EURCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 26.8433581 | 16.6607785 | 3.54381296 |
| EURCAD | 2026-07-21 | 2026-07-20 | 2026-07-17 | 5 | -23.077356 | -20.2654202 | 3.54381296 |
| EURCAD | 2026-08-18 | 2026-08-17 | 2026-08-14 | 5 | -20.000558 | 15.7809568 | 3.54381296 |
| EURCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 5 | 23.6142009 | -30.2083628 | 3.54381296 |
| EURCAD | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | -21.7305224 | 17.9703935 | 3.78310256 |
| EURCAD | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | -22.0772129 | 35.7232603 | 3.78310256 |
| EURCAD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 36.8810456 | -35.9295239 | 3.78310256 |
| EURCAD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 61.7059212 | 86.0648979 | 3.78310256 |
| EURCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | 37.7643663 | 61.3082781 | 3.78310256 |
| EURCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -20.0552063 | 43.0065547 | 3.78310256 |
| EURCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -53.4648803 | -82.2084371 | 3.78310256 |
| EURCAD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -39.7328189 | 13.6891179 | 3.78310256 |
| EURCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 24.7031904 | -27.5708511 | 3.78310256 |
| EURCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 36.1412243 | 66.6425112 | 3.78310256 |
| EURCAD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -26.9294854 | 25.0119698 | 3.78310256 |
| EURCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | 22.2853158 | -42.263453 | 3.78310256 |
| EURCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 20 | 22.4305104 | -5.89709533 | 3.78310256 |
| EURCAD | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | 25.6973933 | -34.1031517 | 3.78310256 |
| EURCAD | 2026-09-29 | 2026-09-28 | 2026-09-25 | 20 | -20.1137332 | -48.088275 | 3.78310256 |
| EURCHF | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | 30.6473337 | 16.4179156 | 3.69614705 |
| EURCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | -31.1934244 | -27.7138782 | 3.69614705 |
| EURCHF | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | 22.0184539 | -38.9467291 | 3.69614705 |
| EURCHF | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 42.4710313 | 107.372235 | 3.69614705 |
| EURCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -42.2453184 | -99.6278738 | 3.69614705 |
| EURCHF | 2025-12-19 | 2025-12-18 | 2025-12-17 | 5 | -20.1282628 | 30.2498271 | 2.80506461 |
| EURCHF | 2025-12-27 | 2025-12-26 | 2025-12-24 | 5 | 14.2267048 | -10.5587669 | 2.80506461 |
| EURCHF | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 27.2144567 | 15.2532646 | 2.80506461 |
| EURCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 5 | -29.039892 | 6.61010992 | 2.80506461 |
| EURCHF | 2026-01-23 | 2026-01-22 | 2026-01-21 | 5 | 14.0581376 | -2.27033505 | 2.80506461 |
| EURCHF | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | 15.0217884 | -6.46638681 | 2.80506461 |
| EURCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 40.1748156 | 71.1322285 | 2.80506461 |
| EURCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | -31.21649 | -20.8494975 | 2.80506461 |
| EURCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -15.0963099 | -14.4978137 | 2.80506461 |
| EURCHF | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -20.7387383 | 20.6516007 | 2.80506461 |
| EURCHF | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 17.6969968 | -27.802156 | 2.80506461 |
| EURCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -15.4824654 | 22.9813316 | 2.80506461 |
| EURCHF | 2026-06-09 | 2026-06-08 | 2026-06-05 | 5 | 14.0362411 | -28.1811632 | 2.80506461 |
| EURCHF | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | -15.1507584 | -20.5284459 | 2.80506461 |
| EURCHF | 2025-11-28 | 2025-11-27 | 2025-11-26 | 20 | -19.7049842 | -10.6131269 | 2.88446295 |
| EURCHF | 2025-12-19 | 2025-12-18 | 2025-12-17 | 20 | 25.0763481 | 29.8193856 | 2.88446295 |
| EURCHF | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 16.1647188 | 6.1796684 | 2.88446295 |
| EURCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -38.4799472 | 3.61682624 | 2.88446295 |
| EURCHF | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 50.2316086 | 39.6303426 | 2.88446295 |
| EURCHF | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 25.9929785 | 99.565746 | 2.88446295 |
| EURCHF | 2026-02-11 | 2026-02-10 | 2026-02-09 | 20 | 14.5410131 | -1.63452164 | 2.88446295 |
| EURCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -43.2551633 | -101.306817 | 2.88446295 |
| EURCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -32.7774117 | -59.8057186 | 2.88446295 |
| EURCHF | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 15.6508466 | 3.86446045 | 2.88446295 |
| EURCHF | 2026-03-24 | 2026-03-23 | 2026-03-20 | 20 | -18.2495996 | -54.1771723 | 2.88446295 |
| EURCHF | 2026-04-07 | 2026-04-06 | 2026-04-03 | 20 | 19.5460744 | 15.5360866 | 2.88446295 |
| EURCHF | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | 16.9463524 | 54.4080899 | 2.88446295 |
| EURGBP | 2025-11-14 | 2025-11-13 | 2025-11-12 | 1 | -24.0086085 | -13.3525896 | 2.54653838 |
| EURGBP | 2025-11-15 | 2025-11-14 | 2025-11-13 | 1 | 19.4720194 | 11.3048285 | 2.54653838 |
| EURGBP | 2026-01-27 | 2026-01-26 | 2026-01-23 | 1 | 16.3705153 | 6.78700992 | 2.54653838 |
| EURGBP | 2026-02-10 | 2026-02-09 | 2026-02-06 | 1 | 15.4349122 | 10.0871974 | 2.54653838 |
| EURGBP | 2026-04-04 | 2026-04-03 | 2026-04-02 | 1 | -14.561424 | -1.94468045 | 2.54653838 |
| EURGBP | 2025-11-08 | 2025-11-07 | 2025-11-06 | 5 | -28.2009112 | -21.4897809 | 2.42714413 |
| EURGBP | 2025-11-15 | 2025-11-14 | 2025-11-13 | 5 | 31.6027212 | -6.22861168 | 2.42714413 |
| EURGBP | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | -12.4311009 | 53.7325717 | 2.42714413 |
| EURGBP | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 14.2024172 | 17.9769734 | 2.42714413 |
| EURGBP | 2025-11-15 | 2025-11-14 | 2025-11-13 | 20 | 30.9389933 | 41.0891236 | 2.8920622 |
| EURGBP | 2026-01-13 | 2026-01-12 | 2026-01-09 | 20 | -16.5858131 | 29.728174 | 2.8920622 |
| EURGBP | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | -16.2705604 | -44.4502731 | 2.8920622 |
| EURJPY | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 38.9807067 | 26.2399071 | 6.37502869 |
| EURJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -34.893883 | -41.9848986 | 6.37502869 |
| EURJPY | 2026-07-31 | 2026-07-30 | 2026-07-29 | 1 | -44.7538269 | 24.4702236 | 6.37502869 |
| EURJPY | 2025-11-25 | 2025-11-24 | 2025-11-21 | 5 | 25.5476741 | -48.8346024 | 4.7864551 |
| EURJPY | 2025-12-19 | 2025-12-18 | 2025-12-17 | 5 | -32.8312215 | 27.5383474 | 4.7864551 |
| EURJPY | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -34.493705 | 19.5637228 | 4.7864551 |
| EURJPY | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | 28.4604503 | 62.2194136 | 4.7864551 |
| EURJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -47.4765263 | -19.8483716 | 4.7864551 |
| EURJPY | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -26.012785 | 79.5672628 | 4.7864551 |
| EURJPY | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 26.2770887 | 34.0005276 | 4.7864551 |
| EURJPY | 2026-04-14 | 2026-04-13 | 2026-04-10 | 5 | -33.5938004 | -37.6637796 | 4.7864551 |
| EURJPY | 2026-07-25 | 2026-07-24 | 2026-07-23 | 5 | -38.7842599 | -151.97335 | 4.7864551 |
| EURJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 5 | 39.484118 | 147.884214 | 4.7864551 |
| EURJPY | 2026-08-05 | 2026-08-04 | 2026-08-03 | 5 | 29.0119541 | -29.2470555 | 4.7864551 |
| EURJPY | 2026-09-02 | 2026-09-01 | 2026-08-31 | 5 | 28.4859761 | -1.28317667 | 4.7864551 |
| EURJPY | 2026-09-03 | 2026-09-02 | 2026-09-01 | 5 | 28.7897147 | 104.266269 | 4.7864551 |
| EURJPY | 2026-09-09 | 2026-09-08 | 2026-09-07 | 5 | -29.4271974 | 35.6085292 | 4.7864551 |
| EURJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 5 | -36.9708618 | -7.95848729 | 4.7864551 |
| EURJPY | 2025-11-28 | 2025-11-27 | 2025-11-26 | 20 | -29.8285123 | 17.1904808 | 5.48989467 |
| EURJPY | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 31.8184075 | -59.2199548 | 5.48989467 |
| EURJPY | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 35.1871861 | 10.536057 | 5.48989467 |
| EURJPY | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 52.2850881 | 59.9378662 | 5.48989467 |
| EURJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -48.1242001 | -26.4215577 | 5.48989467 |
| EURJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 20 | 40.7314535 | 142.684483 | 5.48989467 |
| EURJPY | 2026-08-13 | 2026-08-12 | 2026-08-11 | 20 | 29.3268318 | 15.938023 | 5.48989467 |
| EURJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 20 | -36.3388882 | -74.5155858 | 5.48989467 |
| EURNZD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 52.8107114 | -54.9962597 | 6.54459882 |
| EURNZD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -48.625028 | 13.140274 | 6.54459882 |
| EURNZD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 1 | 49.5457936 | -10.9363735 | 6.54459882 |
| EURNZD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 33.7373723 | -2.58415693 | 6.58398378 |
| EURNZD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 55.7232017 | -59.8341457 | 6.58398378 |
| EURNZD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -52.51048 | 28.6882218 | 6.58398378 |
| EURNZD | 2026-07-10 | 2026-07-09 | 2026-07-08 | 5 | -33.3251616 | 45.8884074 | 6.58398378 |
| EURNZD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 66.4521885 | -20.448818 | 6.68596496 |
| EURNZD | 2026-03-25 | 2026-03-24 | 2026-03-23 | 20 | 38.1405003 | -39.1893357 | 6.68596496 |
| EURNZD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -48.2490461 | -18.2577713 | 6.68596496 |
| EURNZD | 2026-07-09 | 2026-07-08 | 2026-07-07 | 20 | -36.4540337 | 29.7266974 | 6.68596496 |
| EURNZD | 2026-08-06 | 2026-08-05 | 2026-08-04 | 20 | 38.0976651 | 72.2549608 | 6.68596496 |
| EURUSD | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | -23.2743318 | 26.8186256 | 4.60298386 |
| EURUSD | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | 28.3141948 | 56.9310513 | 4.60298386 |
| EURUSD | 2026-01-24 | 2026-01-23 | 2026-01-22 | 1 | -27.4007164 | -42.9056543 | 4.60298386 |
| EURUSD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 1 | 29.8618403 | 118.262254 | 4.60298386 |
| EURUSD | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | -38.4550904 | 47.4458976 | 4.60298386 |
| EURUSD | 2026-01-30 | 2026-01-29 | 2026-01-28 | 1 | 24.2680404 | -88.7571611 | 4.60298386 |
| EURUSD | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | -46.0766894 | -53.7199611 | 4.60298386 |
| EURUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 1 | 36.4827187 | 25.4469028 | 4.60298386 |
| EURUSD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 51.0535249 | -68.6079594 | 4.60298386 |
| EURUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -52.5880079 | -13.9353982 | 4.60298386 |
| EURUSD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 80.2149254 | 90.2704156 | 4.60298386 |
| EURUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -64.2769023 | -104.883688 | 4.60298386 |
| EURUSD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 1 | -30.1974989 | -64.1951223 | 4.60298386 |
| EURUSD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -78.0914751 | -69.4763872 | 4.60298386 |
| EURUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 79.0661473 | 54.253757 | 4.60298386 |
| EURUSD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | 37.5220661 | 41.6338549 | 4.60298386 |
| EURUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | -52.0954947 | -49.5441409 | 4.60298386 |
| EURUSD | 2026-05-23 | 2026-05-22 | 2026-05-21 | 1 | -31.4965532 | 17.4759703 | 4.60298386 |
| EURUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 39.8120394 | -5.6912354 | 4.60298386 |
| EURUSD | 2026-06-13 | 2026-06-12 | 2026-06-11 | 1 | -34.3853863 | -3.28569279 | 4.60298386 |
| EURUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 1 | 27.7801179 | 23.9499586 | 4.60298386 |
| EURUSD | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | -30.1468724 | -18.8922493 | 4.33348133 |
| EURUSD | 2026-01-23 | 2026-01-22 | 2026-01-21 | 5 | -32.6327717 | -76.1803524 | 4.33348133 |
| EURUSD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | 30.0379247 | -67.9694195 | 4.33348133 |
| EURUSD | 2026-01-30 | 2026-01-29 | 2026-01-28 | 5 | 23.4669467 | -13.0481348 | 4.33348133 |
| EURUSD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | -44.9434656 | -28.9951888 | 4.33348133 |
| EURUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 90.6898243 | -16.7776866 | 4.33348133 |
| EURUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | 33.9631555 | 156.508489 | 4.33348133 |
| EURUSD | 2026-03-04 | 2026-03-03 | 2026-03-02 | 5 | 22.274261 | 65.5601993 | 4.33348133 |
| EURUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -97.6675524 | -35.6447671 | 4.33348133 |
| EURUSD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 5 | -32.4353038 | 136.243353 | 4.33348133 |
| EURUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 24.6357223 | -18.2644388 | 4.33348133 |
| EURUSD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -58.2898494 | -34.8045548 | 4.33348133 |
| EURUSD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 39.4604986 | 42.8477286 | 4.33348133 |
| EURUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 72.5547481 | 20.8193104 | 4.33348133 |
| EURUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 5 | -24.9291263 | -32.6494106 | 4.33348133 |
| EURUSD | 2026-05-07 | 2026-05-06 | 2026-05-05 | 5 | 23.858458 | -46.2640357 | 4.33348133 |
| EURUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -43.8462381 | -35.2000583 | 4.33348133 |
| EURUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 43.9912273 | -15.1579952 | 4.33348133 |
| EURUSD | 2026-06-09 | 2026-06-08 | 2026-06-05 | 5 | -28.7140691 | -19.6951018 | 4.33348133 |
| EURUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 39.540065 | -18.4903975 | 4.33348133 |
| EURUSD | 2026-07-21 | 2026-07-20 | 2026-07-17 | 5 | -29.9331221 | -11.6541461 | 4.33348133 |
| EURUSD | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | 23.4721844 | -31.1362252 | 4.61056268 |
| EURUSD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 43.3981465 | -9.24694859 | 4.61056268 |
| EURUSD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 90.3820481 | 22.1970523 | 4.61056268 |
| EURUSD | 2026-02-13 | 2026-02-12 | 2026-02-11 | 20 | 24.3357329 | -24.1234288 | 4.61056268 |
| EURUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | 51.6211497 | 85.8215965 | 4.61056268 |
| EURUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -29.5941706 | 32.7374901 | 4.61056268 |
| EURUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -76.2461263 | -68.7302762 | 4.61056268 |
| EURUSD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -74.1327158 | 17.5740856 | 4.61056268 |
| EURUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 60.8819247 | 9.76221954 | 4.61056268 |
| EURUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 56.8305811 | 48.4650561 | 4.61056268 |
| EURUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 20 | -29.5843464 | -60.2327967 | 4.61056268 |
| EURUSD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -48.6850518 | -10.9309593 | 4.61056268 |
| EURUSD | 2026-05-07 | 2026-05-06 | 2026-05-05 | 20 | 27.5438178 | -48.136767 | 4.61056268 |
| EURUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | -40.9589386 | -47.8088102 | 4.61056268 |
| EURUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | 42.4273645 | -31.0991495 | 4.61056268 |
| EURUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | 40.7206636 | -9.49976503 | 4.61056268 |
| EURUSD | 2026-09-18 | 2026-09-17 | 2026-09-16 | 20 | -29.1490304 | 18.480863 | 4.61056268 |
| EURUSD | 2026-09-29 | 2026-09-28 | 2026-09-25 | 20 | -25.4951553 | -33.2043489 | 4.61056268 |
| GBPAUD | 2025-11-14 | 2025-11-13 | 2025-11-12 | 1 | 30.8088246 | -55.4118764 | 5.41729771 |
| GBPAUD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 1 | 36.6671599 | -66.85847 | 5.41729771 |
| GBPAUD | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | 35.4217119 | 58.3354463 | 5.41729771 |
| GBPAUD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 1 | -29.2894938 | 4.01003223 | 5.41729771 |
| GBPAUD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | 43.3460909 | 113.021972 | 5.41729771 |
| GBPAUD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 61.6506017 | 84.3780323 | 5.41729771 |
| GBPAUD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -66.4904987 | -72.904544 | 5.41729771 |
| GBPAUD | 2026-04-18 | 2026-04-17 | 2026-04-16 | 1 | -28.0907562 | 1.65590724 | 5.41729771 |
| GBPAUD | 2026-09-12 | 2026-09-11 | 2026-09-10 | 1 | -27.1631681 | 6.57462416 | 5.41729771 |
| GBPAUD | 2025-11-08 | 2025-11-07 | 2025-11-06 | 5 | 23.5135648 | 3.90560758 | 4.57209649 |
| GBPAUD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -35.4055151 | -16.8381616 | 4.57209649 |
| GBPAUD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | 51.8772738 | -11.928248 | 4.57209649 |
| GBPAUD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 5 | -27.4270036 | 5.3991931 | 4.57209649 |
| GBPAUD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -29.0624933 | -100.604531 | 4.57209649 |
| GBPAUD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 29.6337466 | 13.2986424 | 4.57209649 |
| GBPAUD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | -27.950667 | 106.393593 | 4.57209649 |
| GBPAUD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 46.8723063 | 8.09515403 | 4.57209649 |
| GBPAUD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -64.9625755 | -110.883893 | 4.57209649 |
| GBPAUD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 5 | 32.2717548 | -19.868483 | 4.57209649 |
| GBPAUD | 2026-05-12 | 2026-05-11 | 2026-05-08 | 5 | -26.4891927 | 46.9105816 | 4.57209649 |
| GBPAUD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | 22.863895 | -44.6043207 | 4.57209649 |
| GBPAUD | 2026-09-08 | 2026-09-07 | 2026-09-04 | 5 | -25.520104 | -0.255929477 | 4.57209649 |
| GBPAUD | 2025-11-11 | 2025-11-10 | 2025-11-07 | 20 | -33.229165 | 41.8874309 | 4.74456207 |
| GBPAUD | 2025-11-15 | 2025-11-14 | 2025-11-13 | 20 | -32.9453527 | -7.86102807 | 4.74456207 |
| GBPAUD | 2026-01-06 | 2026-01-05 | 2026-01-02 | 20 | -24.7818793 | -40.9964985 | 4.74456207 |
| GBPAUD | 2026-01-13 | 2026-01-12 | 2026-01-09 | 20 | 27.455514 | -38.0465026 | 4.74456207 |
| GBPAUD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -38.7872863 | -31.0474496 | 4.74456207 |
| GBPAUD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 62.66583 | 93.3334055 | 4.74456207 |
| GBPAUD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | -35.3652917 | 13.6622574 | 4.74456207 |
| GBPAUD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -54.8108681 | -70.5540575 | 4.74456207 |
| GBPAUD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 20 | 27.4313848 | 16.8734373 | 4.74456207 |
| GBPAUD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | 24.6728211 | -59.5568676 | 4.74456207 |
| GBPAUD | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | 33.4828252 | -21.3754343 | 4.74456207 |
| GBPCAD | 2025-11-14 | 2025-11-13 | 2025-11-12 | 1 | 26.0153329 | -58.1626322 | 4.13914962 |
| GBPCAD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 41.8192953 | 36.5092125 | 4.13914962 |
| GBPCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -37.3685085 | -41.1426765 | 4.13914962 |
| GBPCAD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 53.214892 | 132.505457 | 4.13914962 |
| GBPCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -43.5694578 | -105.778364 | 4.13914962 |
| GBPCAD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -51.2381787 | -30.1411498 | 4.13914962 |
| GBPCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 49.3995064 | 11.3749685 | 4.13914962 |
| GBPCAD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | 23.5458216 | -9.53709178 | 4.13914962 |
| GBPCAD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | -22.9537355 | -0.70352082 | 4.13914962 |
| GBPCAD | 2026-05-09 | 2026-05-08 | 2026-05-07 | 1 | 23.1610844 | -57.2907346 | 4.13914962 |
| GBPCAD | 2026-05-23 | 2026-05-22 | 2026-05-21 | 1 | -21.5411783 | -13.0705159 | 4.13914962 |
| GBPCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 27.6993099 | -52.9317581 | 4.13914962 |
| GBPCAD | 2026-08-22 | 2026-08-21 | 2026-08-20 | 1 | -22.0671387 | 31.5450076 | 4.13914962 |
| GBPCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 1 | 23.1954764 | -13.2764889 | 4.13914962 |
| GBPCAD | 2025-10-28 | 2025-10-27 | 2025-10-24 | 5 | 19.4710926 | 26.8657546 | 3.68900846 |
| GBPCAD | 2025-11-08 | 2025-11-07 | 2025-11-06 | 5 | 26.352019 | 37.6691661 | 3.68900846 |
| GBPCAD | 2025-11-15 | 2025-11-14 | 2025-11-13 | 5 | -34.5914109 | 11.3832703 | 3.68900846 |
| GBPCAD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | -23.105787 | 3.36042472 | 3.68900846 |
| GBPCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 56.5586065 | 1.50605019 | 3.68900846 |
| GBPCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -64.2211802 | -59.3008683 | 3.68900846 |
| GBPCAD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 5 | -19.4919849 | 133.742472 | 3.68900846 |
| GBPCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 26.8571437 | 46.4073866 | 3.68900846 |
| GBPCAD | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -19.71642 | 34.2704878 | 3.68900846 |
| GBPCAD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -47.1629907 | -30.6311993 | 3.68900846 |
| GBPCAD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 24.6386275 | 13.5826254 | 3.68900846 |
| GBPCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 43.6254222 | -24.469629 | 3.68900846 |
| GBPCAD | 2026-05-05 | 2026-05-04 | 2026-05-01 | 5 | 24.0899265 | 17.7114011 | 3.68900846 |
| GBPCAD | 2026-05-12 | 2026-05-11 | 2026-05-08 | 5 | -21.5444026 | 69.0780732 | 3.68900846 |
| GBPCAD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -22.4889943 | -57.6478866 | 3.68900846 |
| GBPCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 21.1461039 | 14.3981895 | 3.68900846 |
| GBPCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 23.0890994 | 31.7891595 | 3.68900846 |
| GBPCAD | 2026-07-21 | 2026-07-20 | 2026-07-17 | 5 | -24.4620569 | -47.6794642 | 3.68900846 |
| GBPCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 5 | 26.2699806 | -46.6548838 | 3.68900846 |
| GBPCAD | 2025-11-15 | 2025-11-14 | 2025-11-13 | 20 | -35.2945786 | -26.9086097 | 3.65935422 |
| GBPCAD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 42.746346 | -20.5671626 | 3.65935422 |
| GBPCAD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 52.7089403 | 107.281272 | 3.65935422 |
| GBPCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | 35.9758527 | 77.0306541 | 3.65935422 |
| GBPCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -20.1021299 | -28.6399722 | 3.65935422 |
| GBPCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -56.5998326 | -82.78757 | 3.65935422 |
| GBPCAD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -47.6778988 | -7.01116605 | 3.65935422 |
| GBPCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 32.2599752 | -9.9040763 | 3.65935422 |
| GBPCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 39.419058 | 42.9773229 | 3.65935422 |
| GBPCAD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -27.9013558 | 42.8384902 | 3.65935422 |
| GBPCAD | 2026-05-12 | 2026-05-11 | 2026-05-08 | 20 | -26.6496451 | -0.590154519 | 3.65935422 |
| GBPCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | 29.385741 | 2.17211517 | 3.65935422 |
| GBPCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | 19.8955681 | -25.1271642 | 3.65935422 |
| GBPCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 20 | 22.32025 | -7.08475163 | 3.65935422 |
| GBPCHF | 2025-10-28 | 2025-10-27 | 2025-10-24 | 1 | 25.3884566 | -70.8113129 | 4.51063705 |
| GBPCHF | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | 31.9911879 | 7.99746819 | 4.51063705 |
| GBPCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | -33.2066755 | -81.9076326 | 4.51063705 |
| GBPCHF | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | 31.4750136 | -85.2926865 | 4.51063705 |
| GBPCHF | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 49.2354356 | 184.454246 | 4.51063705 |
| GBPCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -46.5579463 | -126.664973 | 4.51063705 |
| GBPCHF | 2025-10-28 | 2025-10-27 | 2025-10-24 | 5 | 24.7417973 | 41.2562386 | 3.48954166 |
| GBPCHF | 2025-11-04 | 2025-11-03 | 2025-10-31 | 5 | -19.3561594 | -44.4617878 | 3.48954166 |
| GBPCHF | 2025-11-08 | 2025-11-07 | 2025-11-06 | 5 | 24.6724776 | 23.5148983 | 3.48954166 |
| GBPCHF | 2025-11-15 | 2025-11-14 | 2025-11-13 | 5 | -29.6202201 | 26.4601437 | 3.48954166 |
| GBPCHF | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 35.6244167 | -1.12434024 | 3.48954166 |
| GBPCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 5 | -19.674651 | 1.30465056 | 3.48954166 |
| GBPCHF | 2026-01-23 | 2026-01-22 | 2026-01-21 | 5 | 24.3255194 | 1.22293808 | 3.48954166 |
| GBPCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 42.6354213 | 118.336774 | 3.48954166 |
| GBPCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | -39.0303358 | -71.0906541 | 3.48954166 |
| GBPCHF | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -22.1347766 | 44.6883604 | 3.48954166 |
| GBPCHF | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 18.5324887 | -26.1249304 | 3.48954166 |
| GBPCHF | 2025-11-15 | 2025-11-14 | 2025-11-13 | 20 | -21.0919364 | -24.7234503 | 4.06821117 |
| GBPCHF | 2025-12-19 | 2025-12-18 | 2025-12-17 | 20 | 26.7288877 | 7.44435109 | 4.06821117 |
| GBPCHF | 2026-01-01 | 2025-12-31 | 2025-12-30 | 20 | 20.9547612 | -40.0211149 | 4.06821117 |
| GBPCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -38.1054082 | 5.68377721 | 4.06821117 |
| GBPCHF | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 55.9860107 | 54.4188073 | 4.06821117 |
| GBPCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -42.3857413 | -172.388697 | 4.06821117 |
| GBPCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -25.4901821 | -56.6096823 | 4.06821117 |
| GBPJPY | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 39.1192073 | 2.14022765 | 7.24169938 |
| GBPJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -37.9905704 | -47.5863499 | 7.24169938 |
| GBPJPY | 2026-07-31 | 2026-07-30 | 2026-07-29 | 1 | -47.0290699 | 14.711652 | 7.24169938 |
| GBPJPY | 2025-11-25 | 2025-11-24 | 2025-11-21 | 5 | 31.8023734 | -69.2032802 | 5.85535232 |
| GBPJPY | 2025-12-19 | 2025-12-18 | 2025-12-17 | 5 | -31.4444828 | 9.10423236 | 5.85535232 |
| GBPJPY | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -45.5361 | 68.4866584 | 5.85535232 |
| GBPJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -49.9612117 | -34.8585227 | 5.85535232 |
| GBPJPY | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -33.7057256 | 104.38477 | 5.85535232 |
| GBPJPY | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 34.1148282 | 35.6227974 | 5.85535232 |
| GBPJPY | 2026-04-14 | 2026-04-13 | 2026-04-10 | 5 | -33.9010964 | -52.5401018 | 5.85535232 |
| GBPJPY | 2026-07-25 | 2026-07-24 | 2026-07-23 | 5 | -40.1186985 | -152.882189 | 5.85535232 |
| GBPJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 5 | 39.091571 | 134.028571 | 5.85535232 |
| GBPJPY | 2026-09-09 | 2026-09-08 | 2026-09-07 | 5 | -30.6238973 | 24.7647126 | 5.85535232 |
| GBPJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 5 | -38.157033 | -9.94069724 | 5.85535232 |
| GBPJPY | 2025-11-28 | 2025-11-27 | 2025-11-26 | 20 | -29.8200316 | 19.3940105 | 5.42938088 |
| GBPJPY | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 41.4587363 | -69.0368075 | 5.42938088 |
| GBPJPY | 2026-01-06 | 2026-01-05 | 2026-01-02 | 20 | -28.1826468 | -21.430837 | 5.42938088 |
| GBPJPY | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 41.5279487 | 26.783601 | 5.42938088 |
| GBPJPY | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 41.3256692 | 79.6139882 | 5.42938088 |
| GBPJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -49.5199109 | -23.9012794 | 5.42938088 |
| GBPJPY | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 34.556129 | 46.5800407 | 5.42938088 |
| GBPJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 20 | 39.9487561 | 146.650488 | 5.42938088 |
| GBPJPY | 2026-08-13 | 2026-08-12 | 2026-08-11 | 20 | 30.7947978 | 8.33760077 | 5.42938088 |
| GBPJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 20 | -37.9845811 | -62.3141912 | 5.42938088 |
| GBPNZD | 2025-11-14 | 2025-11-13 | 2025-11-12 | 1 | 34.2387418 | -94.909357 | 6.57585946 |
| GBPNZD | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | 36.6868402 | 92.0028482 | 6.57585946 |
| GBPNZD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 45.1096904 | -38.3583235 | 6.57585946 |
| GBPNZD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -44.1629157 | -0.923247385 | 6.57585946 |
| GBPNZD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 1 | 43.3966062 | 9.97306821 | 6.57585946 |
| GBPNZD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 5 | 35.0308079 | 5.31268832 | 6.54464318 |
| GBPNZD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 48.467849 | -78.1174189 | 6.54464318 |
| GBPNZD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -54.1218143 | -0.480727944 | 6.54464318 |
| GBPNZD | 2025-11-15 | 2025-11-14 | 2025-11-13 | 20 | -33.2254373 | 16.0538698 | 5.96069154 |
| GBPNZD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -38.5139921 | -59.9947978 | 5.96069154 |
| GBPNZD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 58.8276883 | -40.8408022 | 5.96069154 |
| GBPNZD | 2026-03-25 | 2026-03-24 | 2026-03-23 | 20 | 35.0986723 | -15.4183953 | 5.96069154 |
| GBPNZD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -43.5088907 | -40.500851 | 5.96069154 |
| GBPNZD | 2026-07-09 | 2026-07-08 | 2026-07-07 | 20 | -36.262904 | 4.18745825 | 5.96069154 |
| GBPNZD | 2026-08-06 | 2026-08-05 | 2026-08-04 | 20 | 38.5244763 | 59.2492827 | 5.96069154 |
| GBPUSD | 2025-11-14 | 2025-11-13 | 2025-11-12 | 1 | 25.0096396 | -34.9928577 | 4.7972161 |
| GBPUSD | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | 26.4046426 | 2.12029207 | 4.7972161 |
| GBPUSD | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | -30.1992708 | 1.11902681 | 4.7972161 |
| GBPUSD | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | -41.4223229 | -44.5496096 | 4.7972161 |
| GBPUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 1 | 35.7945292 | 25.0420148 | 4.7972161 |
| GBPUSD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 60.033457 | 8.24554572 | 4.7972161 |
| GBPUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -57.7791786 | -40.0947673 | 4.7972161 |
| GBPUSD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 81.0364878 | 67.0583774 | 4.7972161 |
| GBPUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -67.9331613 | -111.503749 | 4.7972161 |
| GBPUSD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 1 | 24.8319079 | -24.1386183 | 4.7972161 |
| GBPUSD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 1 | -29.9153815 | -70.4975941 | 4.7972161 |
| GBPUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 1 | 24.2552409 | -23.4334067 | 4.7972161 |
| GBPUSD | 2026-03-28 | 2026-03-27 | 2026-03-26 | 1 | 27.6406196 | 9.01614214 | 4.7972161 |
| GBPUSD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -83.8609376 | -49.7837696 | 4.7972161 |
| GBPUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 81.8294182 | 36.6226585 | 4.7972161 |
| GBPUSD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | 45.1460406 | 60.0053465 | 4.7972161 |
| GBPUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | -56.4280937 | -46.2133711 | 4.7972161 |
| GBPUSD | 2026-05-09 | 2026-05-08 | 2026-05-07 | 1 | 30.7514235 | -44.1248291 | 4.7972161 |
| GBPUSD | 2026-05-23 | 2026-05-22 | 2026-05-21 | 1 | -34.7560096 | 19.2166191 | 4.7972161 |
| GBPUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 44.7585103 | -55.3013083 | 4.7972161 |
| GBPUSD | 2026-06-13 | 2026-06-12 | 2026-06-11 | 1 | -35.3055527 | -20.7625729 | 4.7972161 |
| GBPUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 1 | 31.0717712 | 36.2086629 | 4.7972161 |
| GBPUSD | 2025-11-08 | 2025-11-07 | 2025-11-06 | 5 | 31.7948239 | -3.1512749 | 5.02370745 |
| GBPUSD | 2025-11-15 | 2025-11-14 | 2025-11-13 | 5 | -38.4188942 | -0.251269807 | 5.02370745 |
| GBPUSD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | -44.8886435 | -17.6624977 | 5.02370745 |
| GBPUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 94.1672728 | 30.4387921 | 5.02370745 |
| GBPUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | 26.6125508 | 106.246802 | 5.02370745 |
| GBPUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -100.985385 | -51.3335248 | 5.02370745 |
| GBPUSD | 2026-03-13 | 2026-03-12 | 2026-03-11 | 5 | -29.4764311 | 152.882237 | 5.02370745 |
| GBPUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 5 | 29.4103599 | 15.4015316 | 5.02370745 |
| GBPUSD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -68.3609274 | -52.9754776 | 5.02370745 |
| GBPUSD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 40.6898874 | 44.4054312 | 5.02370745 |
| GBPUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 73.9566379 | -5.35582258 | 5.02370745 |
| GBPUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 5 | -25.4112438 | -47.1041932 | 5.02370745 |
| GBPUSD | 2026-05-05 | 2026-05-04 | 2026-05-01 | 5 | 31.7547801 | 48.1387285 | 5.02370745 |
| GBPUSD | 2026-05-07 | 2026-05-06 | 2026-05-05 | 5 | 25.3868736 | -28.237111 | 5.02370745 |
| GBPUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -47.6978744 | -74.9138327 | 5.02370745 |
| GBPUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 39.3156866 | -15.9235749 | 5.02370745 |
| GBPUSD | 2026-06-09 | 2026-06-08 | 2026-06-05 | 5 | -32.9637931 | -29.8464989 | 5.02370745 |
| GBPUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 46.9481958 | 60.0187942 | 5.02370745 |
| GBPUSD | 2026-07-21 | 2026-07-20 | 2026-07-17 | 5 | -29.1398856 | -35.6413088 | 5.02370745 |
| GBPUSD | 2025-11-15 | 2025-11-14 | 2025-11-13 | 20 | -31.8224413 | -29.5607154 | 4.89478227 |
| GBPUSD | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | 25.6893314 | -29.5025295 | 4.89478227 |
| GBPUSD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 20 | -25.5281494 | -42.7641695 | 4.89478227 |
| GBPUSD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 49.9197495 | 6.78968494 | 4.89478227 |
| GBPUSD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 79.9797247 | 42.0100073 | 4.89478227 |
| GBPUSD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 20 | -25.0942051 | 67.6895721 | 4.89478227 |
| GBPUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | 49.2047984 | 100.753601 | 4.89478227 |
| GBPUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -31.2623768 | -40.6277026 | 4.89478227 |
| GBPUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -71.6272253 | -66.6982768 | 4.89478227 |
| GBPUSD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -79.6800311 | -0.704454263 | 4.89478227 |
| GBPUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 70.0480472 | 29.0406791 | 4.89478227 |
| GBPUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 58.9914242 | 23.6885865 | 4.89478227 |
| GBPUSD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -50.5638763 | 5.34303021 | 4.89478227 |
| GBPUSD | 2026-05-07 | 2026-05-06 | 2026-05-05 | 20 | 29.607534 | -46.0538476 | 4.89478227 |
| GBPUSD | 2026-05-12 | 2026-05-11 | 2026-05-08 | 20 | -27.4538733 | -9.25887954 | 4.89478227 |
| GBPUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | -44.5684244 | -121.502792 | 4.89478227 |
| GBPUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | 50.0776458 | 13.4298352 | 4.89478227 |
| GBPUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | 42.2768905 | -2.12935731 | 4.89478227 |
| GBPUSD | 2026-09-18 | 2026-09-17 | 2026-09-16 | 20 | -24.8569556 | 53.1085303 | 4.89478227 |
| NZDCAD | 2026-01-24 | 2026-01-23 | 2026-01-22 | 1 | -45.2352355 | 39.4277967 | 7.87531465 |
| NZDCAD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 42.8689128 | -20.9337554 | 7.87531465 |
| NZDCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -54.0818666 | -76.9675219 | 7.87531465 |
| NZDCAD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 56.5784537 | 201.887843 | 7.87531465 |
| NZDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -47.019996 | -134.014192 | 7.87531465 |
| NZDCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 1 | 39.9075571 | -79.2476411 | 7.87531465 |
| NZDCAD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -93.9829415 | 12.2655082 | 7.87531465 |
| NZDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 91.5825359 | 8.56707541 | 7.87531465 |
| NZDCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 44.4753052 | -40.2383635 | 7.87531465 |
| NZDCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 72.2155003 | 25.5653547 | 7.7119874 |
| NZDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -85.5343641 | -40.3429461 | 7.7119874 |
| NZDCAD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -92.5173791 | 49.7520851 | 7.7119874 |
| NZDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 96.8124438 | -26.5805488 | 7.7119874 |
| NZDCAD | 2026-05-05 | 2026-05-04 | 2026-05-01 | 5 | 44.8860651 | 50.7507282 | 7.7119874 |
| NZDCAD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 45.5974137 | -28.8173691 | 7.82113135 |
| NZDCAD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 79.3393735 | 165.082721 | 7.82113135 |
| NZDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -54.9117255 | -107.592027 | 7.82113135 |
| NZDCAD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -104.006851 | 37.6460259 | 7.82113135 |
| NZDCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 62.4395511 | -38.3986767 | 7.82113135 |
| NZDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 82.4673006 | 82.0859028 | 7.82113135 |
| NZDCHF | 2025-10-28 | 2025-10-27 | 2025-10-24 | 1 | 32.7814919 | -14.6102741 | 6.19075608 |
| NZDCHF | 2025-11-11 | 2025-11-10 | 2025-11-07 | 1 | 33.0940066 | -41.4597003 | 6.19075608 |
| NZDCHF | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | 32.9772996 | 37.0827616 | 6.19075608 |
| NZDCHF | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -50.108758 | -190.345024 | 6.19075608 |
| NZDCHF | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 51.1782123 | 126.294332 | 6.19075608 |
| NZDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -63.4992972 | -161.817309 | 6.19075608 |
| NZDCHF | 2026-03-14 | 2026-03-13 | 2026-03-12 | 1 | -32.9618859 | 139.641393 | 6.19075608 |
| NZDCHF | 2026-04-04 | 2026-04-03 | 2026-04-02 | 1 | -31.4134445 | 46.7834302 | 6.19075608 |
| NZDCHF | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -38.1776022 | 6.78042296 | 6.19075608 |
| NZDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 35.1978213 | 13.9213352 | 6.19075608 |
| NZDCHF | 2026-05-29 | 2026-05-28 | 2026-05-27 | 1 | -31.4089464 | -2.92185406 | 6.19075608 |
| NZDCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 58.3172079 | 142.273607 | 7.08722374 |
| NZDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | -42.7626663 | -7.92573473 | 7.08722374 |
| NZDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -40.2353668 | -12.969495 | 7.08722374 |
| NZDCHF | 2026-03-31 | 2026-03-30 | 2026-03-27 | 5 | -42.2896694 | 20.7846 | 7.08722374 |
| NZDCHF | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -44.7518738 | 79.5833267 | 7.08722374 |
| NZDCHF | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 42.4337275 | -6.35783011 | 7.08722374 |
| NZDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 40.6243871 | -4.23552649 | 7.08722374 |
| NZDCHF | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 59.400971 | 46.9142157 | 8.01142928 |
| NZDCHF | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 45.1074022 | 178.235488 | 8.01142928 |
| NZDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 20 | -42.368643 | -116.031158 | 8.01142928 |
| NZDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -41.8956461 | -87.3208234 | 8.01142928 |
| NZDCHF | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -50.6007073 | 25.8991583 | 8.01142928 |
| NZDCHF | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 40.7734482 | -80.7091586 | 8.01142928 |
| NZDJPY | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -61.5709857 | -204.65737 | 9.3369643 |
| NZDJPY | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -73.1623108 | -14.5606489 | 9.3369643 |
| NZDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 64.2169623 | 68.814207 | 9.3369643 |
| NZDJPY | 2026-08-05 | 2026-08-04 | 2026-08-03 | 1 | 51.1593849 | -38.2098484 | 9.3369643 |
| NZDJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -72.9475817 | -17.8313986 | 9.89735742 |
| NZDJPY | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -70.3106314 | 1.74103843 | 9.89735742 |
| NZDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 73.4695235 | 14.3981297 | 9.89735742 |
| NZDJPY | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 43.7067371 | 17.989968 | 8.53292606 |
| NZDJPY | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 70.5481761 | 139.857059 | 8.53292606 |
| NZDJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -54.6073843 | -53.4273768 | 8.53292606 |
| NZDJPY | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -80.7276185 | -22.9341616 | 8.53292606 |
| NZDJPY | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 63.5987412 | 17.1964732 | 8.53292606 |
| NZDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 61.1853847 | -11.0653213 | 8.53292606 |
| NZDJPY | 2026-07-09 | 2026-07-08 | 2026-07-07 | 20 | 45.7758661 | -36.672527 | 8.53292606 |
| NZDUSD | 2026-01-24 | 2026-01-23 | 2026-01-22 | 1 | -42.2451547 | -28.2688957 | 8.09271155 |
| NZDUSD | 2026-02-07 | 2026-02-06 | 2026-02-05 | 1 | -45.0155293 | -90.3910567 | 8.09271155 |
| NZDUSD | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | -51.9034258 | -87.1068875 | 8.09271155 |
| NZDUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 1 | 40.8401493 | 91.1499248 | 8.09271155 |
| NZDUSD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | 59.7742728 | -49.7588864 | 8.09271155 |
| NZDUSD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | -72.5410877 | -74.3321474 | 8.09271155 |
| NZDUSD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | 86.7595603 | 139.981359 | 8.09271155 |
| NZDUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | -71.389995 | -140.494413 | 8.09271155 |
| NZDUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 1 | 52.0485485 | -101.938107 | 8.09271155 |
| NZDUSD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | -129.017968 | -9.04828935 | 8.09271155 |
| NZDUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | 127.757249 | 35.8328329 | 8.09271155 |
| NZDUSD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | 43.0024781 | 128.805017 | 8.09271155 |
| NZDUSD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | -66.3903463 | -58.3271394 | 8.09271155 |
| NZDUSD | 2026-04-21 | 2026-04-20 | 2026-04-17 | 1 | -49.7587658 | -64.5507216 | 8.09271155 |
| NZDUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | 61.9045387 | -43.1044099 | 8.09271155 |
| NZDUSD | 2026-06-13 | 2026-06-12 | 2026-06-11 | 1 | -51.4889722 | -50.1312673 | 8.09271155 |
| NZDUSD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | -56.3613456 | -80.927958 | 8.34892749 |
| NZDUSD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | 108.978411 | 53.5178014 | 8.34892749 |
| NZDUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | -123.155151 | -33.4454167 | 8.34892749 |
| NZDUSD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | -116.743737 | 27.0505104 | 8.34892749 |
| NZDUSD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | 63.3463647 | 63.053981 | 8.34892749 |
| NZDUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | 129.022221 | -5.60162233 | 8.34892749 |
| NZDUSD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 5 | -42.1208946 | -121.600231 | 8.34892749 |
| NZDUSD | 2026-05-05 | 2026-05-04 | 2026-05-01 | 5 | 51.8319095 | 80.0823399 | 8.34892749 |
| NZDUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | -51.5611957 | -73.277199 | 8.34892749 |
| NZDUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | 48.4034479 | -80.8695622 | 8.34892749 |
| NZDUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | 49.1505434 | 20.4764618 | 8.34892749 |
| NZDUSD | 2026-02-03 | 2026-02-02 | 2026-01-30 | 20 | 52.0870122 | -2.11105745 | 9.32091999 |
| NZDUSD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | 109.246353 | 102.635753 | 9.32091999 |
| NZDUSD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | -88.8505705 | -98.1616868 | 9.32091999 |
| NZDUSD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | -139.984945 | 39.9519269 | 9.32091999 |
| NZDUSD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | 97.6509451 | -1.66228913 | 9.32091999 |
| NZDUSD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | 103.413813 | 64.1881313 | 9.32091999 |
| NZDUSD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | -56.9864834 | -63.3599136 | 9.32091999 |
| NZDUSD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | -53.5528701 | -130.117179 | 9.32091999 |
| NZDUSD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | 47.1588689 | -36.3635183 | 9.32091999 |
| NZDUSD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | 50.8606351 | 42.2083923 | 9.32091999 |
| USDCAD | 2026-01-03 | 2026-01-02 | 2025-12-31 | 1 | -19.0793607 | 9.27662086 | 3.64458067 |
| USDCAD | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | 26.4680189 | -11.8041367 | 3.64458067 |
| USDCAD | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | 26.1945783 | 41.5376098 | 3.64458067 |
| USDCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 1 | -19.619618 | -32.2591044 | 3.64458067 |
| USDCAD | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | -19.47097 | 27.3723875 | 3.64458067 |
| USDCAD | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | 20.0575464 | -1.17082917 | 3.64458067 |
| USDCAD | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | -30.2338547 | 63.7913626 | 3.64458067 |
| USDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | 24.8825013 | 6.46874381 | 3.64458067 |
| USDCAD | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 33.7494681 | 20.8018153 | 3.64458067 |
| USDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -35.4936278 | -27.3974234 | 3.64458067 |
| USDCAD | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | -20.70138 | -67.812239 | 3.64458067 |
| USDCAD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | 31.7131236 | 43.7511611 | 3.64458067 |
| USDCAD | 2026-06-13 | 2026-06-12 | 2026-06-11 | 1 | 23.3271399 | 6.72901364 | 3.64458067 |
| USDCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 1 | -18.4596348 | -16.0297974 | 3.64458067 |
| USDCAD | 2026-08-22 | 2026-08-21 | 2026-08-20 | 1 | -24.3082481 | 47.6496795 | 3.64458067 |
| USDCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 1 | 21.1773288 | -37.4138375 | 3.64458067 |
| USDCAD | 2026-01-23 | 2026-01-22 | 2026-01-21 | 5 | 23.2205514 | 4.70658659 | 3.31016519 |
| USDCAD | 2026-01-30 | 2026-01-29 | 2026-01-28 | 5 | -19.446354 | 66.3585341 | 3.31016519 |
| USDCAD | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | 23.1298894 | 21.968143 | 3.31016519 |
| USDCAD | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -38.137449 | -29.6934584 | 3.31016519 |
| USDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 37.583577 | -6.98465383 | 3.31016519 |
| USDCAD | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 23.8276113 | 23.2640867 | 3.31016519 |
| USDCAD | 2026-04-07 | 2026-04-06 | 2026-04-03 | 5 | -19.3128908 | -30.8346641 | 3.31016519 |
| USDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -31.5952089 | -20.4184763 | 3.31016519 |
| USDCAD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | 25.1006933 | 16.6529729 | 3.31016519 |
| USDCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | -16.5840273 | 31.9138351 | 3.31016519 |
| USDCAD | 2026-06-09 | 2026-06-08 | 2026-06-05 | 5 | 22.3321686 | 12.4358742 | 3.31016519 |
| USDCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | -25.2373526 | -30.18543 | 3.31016519 |
| USDCAD | 2026-08-18 | 2026-08-17 | 2026-08-14 | 5 | -18.5770095 | 35.611304 | 3.31016519 |
| USDCAD | 2026-08-25 | 2026-08-24 | 2026-08-21 | 5 | 24.6185679 | -69.6255157 | 3.31016519 |
| USDCAD | 2026-01-27 | 2026-01-26 | 2026-01-23 | 20 | 25.4601456 | 31.2399264 | 3.75232033 |
| USDCAD | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -28.8455611 | 63.6323077 | 3.75232033 |
| USDCAD | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | 20.12512 | -14.1279859 | 3.75232033 |
| USDCAD | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 34.3219812 | -3.93912803 | 3.75232033 |
| USDCAD | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | -36.7713478 | -37.9779962 | 3.75232033 |
| USDCAD | 2026-03-24 | 2026-03-23 | 2026-03-20 | 20 | -21.8913379 | -55.9059034 | 3.75232033 |
| USDCAD | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -19.6223109 | 19.1991129 | 3.75232033 |
| USDCAD | 2026-04-14 | 2026-04-13 | 2026-04-10 | 20 | 19.6237949 | 53.8150564 | 3.75232033 |
| USDCAD | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | 22.1725632 | 36.9166345 | 3.75232033 |
| USDCAD | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | 30.379939 | 35.466072 | 3.75232033 |
| USDCAD | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | -19.958107 | -11.372331 | 3.75232033 |
| USDCAD | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | -24.4649246 | -24.7525125 | 3.75232033 |
| USDCAD | 2026-07-28 | 2026-07-27 | 2026-07-24 | 20 | -22.4791677 | 11.111096 | 3.75232033 |
| USDCAD | 2026-09-22 | 2026-09-21 | 2026-09-18 | 20 | 19.6125465 | -34.3536135 | 3.75232033 |
| USDCHF | 2025-11-08 | 2025-11-07 | 2025-11-06 | 1 | -33.2559964 | -12.8912555 | 6.59349463 |
| USDCHF | 2026-01-17 | 2026-01-16 | 2026-01-15 | 1 | 53.6906859 | -11.8267716 | 6.59349463 |
| USDCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 1 | -60.1015666 | -84.5075537 | 6.59349463 |
| USDCHF | 2026-01-29 | 2026-01-28 | 2026-01-27 | 1 | 61.5829473 | -86.4692404 | 6.59349463 |
| USDCHF | 2026-01-30 | 2026-01-29 | 2026-01-28 | 1 | -35.8602981 | 129.283576 | 6.59349463 |
| USDCHF | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | 53.6363766 | 36.4779506 | 6.59349463 |
| USDCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 1 | -43.3105511 | -41.7711681 | 6.59349463 |
| USDCHF | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | -69.7426962 | 9.95572565 | 6.59349463 |
| USDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 1 | 59.972522 | 58.2733066 | 6.59349463 |
| USDCHF | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 91.9324724 | 19.1492481 | 6.59349463 |
| USDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -90.4415543 | -24.2771577 | 6.59349463 |
| USDCHF | 2026-04-11 | 2026-04-10 | 2026-04-09 | 1 | -38.0582034 | -89.11404 | 6.59349463 |
| USDCHF | 2026-04-14 | 2026-04-13 | 2026-04-10 | 1 | 52.2942172 | 82.4922824 | 6.59349463 |
| USDCHF | 2026-05-23 | 2026-05-22 | 2026-05-21 | 1 | 37.381836 | 21.6507524 | 6.59349463 |
| USDCHF | 2026-05-26 | 2026-05-25 | 2026-05-22 | 1 | -41.3489639 | 29.6964828 | 6.59349463 |
| USDCHF | 2026-06-13 | 2026-06-12 | 2026-06-11 | 1 | 41.3663161 | -13.1710756 | 6.59349463 |
| USDCHF | 2026-06-16 | 2026-06-15 | 2026-06-12 | 1 | -34.3199297 | -27.0803608 | 6.59349463 |
| USDCHF | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 58.5140725 | 34.4425665 | 5.19697641 |
| USDCHF | 2026-01-22 | 2026-01-21 | 2026-01-20 | 5 | -29.9692874 | -7.08356068 | 5.19697641 |
| USDCHF | 2026-01-23 | 2026-01-22 | 2026-01-21 | 5 | 46.5826805 | 74.2569317 | 5.19697641 |
| USDCHF | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -36.2710378 | 89.868172 | 5.19697641 |
| USDCHF | 2026-01-30 | 2026-01-29 | 2026-01-28 | 5 | -34.1528449 | 26.5499668 | 5.19697641 |
| USDCHF | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | 60.8458599 | 21.7648128 | 5.19697641 |
| USDCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -51.0722339 | 88.3915291 | 5.19697641 |
| USDCHF | 2026-03-03 | 2026-03-02 | 2026-02-27 | 5 | -66.3801915 | -178.137113 | 5.19697641 |
| USDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 84.0225907 | 21.4146149 | 5.19697641 |
| USDCHF | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 68.5104079 | 55.607462 | 5.19697641 |
| USDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -88.7970837 | 0.774850792 | 5.19697641 |
| USDCHF | 2026-04-28 | 2026-04-27 | 2026-04-24 | 5 | 29.6985358 | 43.6654189 | 5.19697641 |
| USDCHF | 2026-05-19 | 2026-05-18 | 2026-05-15 | 5 | 42.7173574 | 41.1200875 | 5.19697641 |
| USDCHF | 2026-05-26 | 2026-05-25 | 2026-05-22 | 5 | -50.7026934 | 56.9880465 | 5.19697641 |
| USDCHF | 2026-06-09 | 2026-06-08 | 2026-06-05 | 5 | 41.2331894 | -8.37076953 | 5.19697641 |
| USDCHF | 2026-06-16 | 2026-06-15 | 2026-06-12 | 5 | -56.5424367 | -2.3943482 | 5.19697641 |
| USDCHF | 2026-07-21 | 2026-07-20 | 2026-07-17 | 5 | 37.1106235 | 13.9485991 | 5.19697641 |
| USDCHF | 2025-12-19 | 2025-12-18 | 2025-12-17 | 20 | 47.5521697 | -3.44299719 | 5.83543985 |
| USDCHF | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 36.9913386 | -23.50179 | 5.83543985 |
| USDCHF | 2025-12-31 | 2025-12-30 | 2025-12-29 | 20 | -31.3659451 | 28.7743471 | 5.83543985 |
| USDCHF | 2026-01-01 | 2025-12-31 | 2025-12-30 | 20 | 33.514166 | -25.6641907 | 5.83543985 |
| USDCHF | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -63.4329113 | 35.5669747 | 5.83543985 |
| USDCHF | 2026-01-29 | 2026-01-28 | 2026-01-27 | 20 | 30.7886635 | -82.642791 | 5.83543985 |
| USDCHF | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -64.7223557 | 74.8748978 | 5.83543985 |
| USDCHF | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | -46.3243086 | -56.1964712 | 5.83543985 |
| USDCHF | 2026-03-10 | 2026-03-09 | 2026-03-06 | 20 | 45.220525 | 10.3115847 | 5.83543985 |
| USDCHF | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 91.0827444 | -12.1193186 | 5.83543985 |
| USDCHF | 2026-03-17 | 2026-03-16 | 2026-03-13 | 20 | -59.9420519 | -81.5986143 | 5.83543985 |
| USDCHF | 2026-03-24 | 2026-03-23 | 2026-03-20 | 20 | -31.2912211 | -50.8471151 | 5.83543985 |
| USDCHF | 2026-04-07 | 2026-04-06 | 2026-04-03 | 20 | 29.5118828 | 75.1459965 | 5.83543985 |
| USDCHF | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -67.575279 | -45.9979599 | 5.83543985 |
| USDCHF | 2026-04-28 | 2026-04-27 | 2026-04-24 | 20 | 59.5391098 | 13.6324131 | 5.83543985 |
| USDCHF | 2026-05-07 | 2026-05-06 | 2026-05-05 | 20 | -34.8065953 | 83.5940185 | 5.83543985 |
| USDCHF | 2026-05-19 | 2026-05-18 | 2026-05-15 | 20 | 44.0742172 | 46.8520062 | 5.83543985 |
| USDCHF | 2026-05-26 | 2026-05-25 | 2026-05-22 | 20 | -55.1855769 | 3.33757053 | 5.83543985 |
| USDCHF | 2026-06-16 | 2026-06-15 | 2026-06-12 | 20 | -51.1883027 | 54.7166446 | 5.83543985 |
| USDCHF | 2026-06-30 | 2026-06-29 | 2026-06-26 | 20 | 29.2979217 | 68.7058008 | 5.83543985 |
| USDCHF | 2026-09-18 | 2026-09-17 | 2026-09-16 | 20 | 31.2612339 | -50.4886307 | 5.83543985 |
| USDCHF | 2026-09-29 | 2026-09-28 | 2026-09-25 | 20 | 30.6009694 | 19.0594253 | 5.83543985 |
| USDJPY | 2026-01-24 | 2026-01-23 | 2026-01-22 | 1 | 43.767851 | 112.128276 | 8.13606893 |
| USDJPY | 2026-01-27 | 2026-01-26 | 2026-01-23 | 1 | -46.8912598 | -80.1292149 | 8.13606893 |
| USDJPY | 2026-02-21 | 2026-02-20 | 2026-02-19 | 1 | 57.310874 | 27.4823834 | 8.13606893 |
| USDJPY | 2026-02-24 | 2026-02-23 | 2026-02-20 | 1 | -44.7307138 | 60.2455612 | 8.13606893 |
| USDJPY | 2026-02-28 | 2026-02-27 | 2026-02-26 | 1 | -51.8435998 | 30.9881958 | 8.13606893 |
| USDJPY | 2026-03-03 | 2026-03-02 | 2026-02-27 | 1 | 40.7659749 | -18.6827608 | 8.13606893 |
| USDJPY | 2026-03-07 | 2026-03-06 | 2026-03-05 | 1 | -41.7485171 | -64.8323924 | 8.13606893 |
| USDJPY | 2026-04-08 | 2026-04-07 | 2026-04-06 | 1 | 55.1660131 | -4.76552594 | 8.13606893 |
| USDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 1 | -60.8429838 | 32.3145132 | 8.13606893 |
| USDJPY | 2026-07-31 | 2026-07-30 | 2026-07-29 | 1 | -48.9841393 | 71.1329751 | 8.13606893 |
| USDJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 1 | 42.1212303 | 135.243619 | 8.13606893 |
| USDJPY | 2025-11-25 | 2025-11-24 | 2025-11-21 | 5 | 36.1425511 | -43.3172798 | 7.05198881 |
| USDJPY | 2026-01-13 | 2026-01-12 | 2026-01-09 | 5 | 51.3663455 | 36.2437492 | 7.05198881 |
| USDJPY | 2026-01-27 | 2026-01-26 | 2026-01-23 | 5 | -65.36897 | 87.2866829 | 7.05198881 |
| USDJPY | 2026-02-17 | 2026-02-16 | 2026-02-13 | 5 | 53.5472669 | -26.8275063 | 7.05198881 |
| USDJPY | 2026-02-24 | 2026-02-23 | 2026-02-20 | 5 | -81.3332502 | 24.7636172 | 7.05198881 |
| USDJPY | 2026-03-10 | 2026-03-09 | 2026-03-06 | 5 | 50.3160584 | 15.7685077 | 7.05198881 |
| USDJPY | 2026-04-02 | 2026-04-01 | 2026-03-31 | 5 | 46.2801493 | -23.7620654 | 7.05198881 |
| USDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 5 | -54.5385685 | 21.038926 | 7.05198881 |
| USDJPY | 2026-07-25 | 2026-07-24 | 2026-07-23 | 5 | -42.1851971 | -162.979975 | 7.05198881 |
| USDJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 5 | 42.9971578 | 123.034162 | 7.05198881 |
| USDJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 5 | -43.7454865 | 61.4884997 | 7.05198881 |
| USDJPY | 2025-12-27 | 2025-12-26 | 2025-12-24 | 20 | 49.6828709 | -90.5293322 | 7.35085398 |
| USDJPY | 2026-01-20 | 2026-01-19 | 2026-01-16 | 20 | -43.9433402 | 10.7970221 | 7.35085398 |
| USDJPY | 2026-02-10 | 2026-02-09 | 2026-02-06 | 20 | -38.5065382 | 37.7627271 | 7.35085398 |
| USDJPY | 2026-02-24 | 2026-02-23 | 2026-02-20 | 20 | -47.1082888 | -72.0961792 | 7.35085398 |
| USDJPY | 2026-03-12 | 2026-03-11 | 2026-03-10 | 20 | 58.3952473 | -63.702453 | 7.35085398 |
| USDJPY | 2026-04-09 | 2026-04-08 | 2026-04-07 | 20 | -41.7969398 | -73.9257739 | 7.35085398 |
| USDJPY | 2026-08-01 | 2026-07-31 | 2026-07-30 | 20 | 45.3675361 | 210.025501 | 7.35085398 |
| USDJPY | 2026-09-10 | 2026-09-09 | 2026-09-08 | 20 | -46.0157057 | -18.4141621 | 7.35085398 |

Todos los Δy por par/fecha/h, retornos y fechas de barras: diferencial.csv. No se atribuye causalidad individual a los valores extremos.

## Oráculo independiente EURUSD h=1

`{"instrument": "EURUSD", "origen": "2025-10-21", "fecha_c0": "2025-10-20", "fecha_c1": "2025-10-21", "close_0": 1.16409, "close_1": 1.15993, "log_c1_c0": -0.003580007438005133, "y_banco": -0.0035800074380051283, "diferencia": 4.7704895589362195e-18, "coincide": true, "nota": "tolerancia 1e-15: log(c1/c0) escalar frente a log(c1)-log(c0) vectorial"}`

## Medida de pilotos y presupuesto de ampliación

| run | modelo | n | CPU s/origen | pared s/origen | pared carga s | pared total s |
|---|---|---|---|---|---|---|
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_cabecera | chronos2 | 280 | 0.235267857 | 0.301548174 | 22.4300385 | 188.211869 |
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_cabecera | garch | 280 | 0.0728794643 | 0.070108295 | 22.4300385 | 188.211869 |
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_cabecera | hmm | 280 | 0.140122768 | 0.125816549 | 22.4300385 | 188.211869 |
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_ampliacion | chronos2 | 140 | 0.257589286 | 0.155436936 | 14.8194069 | 85.4067843 |
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_ampliacion | garch | 140 | 0.101339286 | 0.0648484757 | 14.8194069 | 85.4067843 |
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_ampliacion | hmm | 140 | 0.219977679 | 0.123541073 | 14.8194069 | 85.4067843 |
| E:/quantdesk-lab/runs/TS-00-BENCH/piloto_toto_mt5_cabecera | toto | 56 | 5.92243304 | 3.13111297 | 111.187724 | 312.988145 |
| E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_mt5_cabecera | fincast | 56 | 1.37555804 | 0.744447736 | 118.911197 | 188.281093 |


Paso fijo elegido: **20 días**. 12037 orígenes válidos × (suma pared/modelo 0.343826 + sobrecoste/origen 0.016473) + carga 14.819 + lectura/verificación/preparación 20.145 = 4371.89003 s = 1.2144139 h. ≤2 h: **True** por extrapolación de 140 orígenes; 2 hilos torch, una corrida pesada cada vez. La raíz contrasta con la corrida real (si >2,5 h decide ella).
## Invariantes y reproducibilidad

## Órdenes exactas para la raíz (NO ejecutadas aquí)

```powershell
$env:HF_HOME='E:/quantdesk-lab/cache/hf'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'
$env:QUANTDESK_BENCH_TMP='E:/quantdesk-lab/tmp/TS-00-BENCH-MT5'; $env:TMP=$env:QUANTDESK_BENCH_TMP; $env:TEMP=$env:TMP; $env:TMPDIR=$env:TMP; $env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset mt5_fx28_cierre_c20261101 --hilos 2 --out E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_cierre_c20261101
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset mt5_fx28_hist_cierre_c20261101 --hilos 2 --out E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_hist_cierre_c20261101
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset mt5_fx28_cierre_c20261101 --modelos toto --hilos 2 --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH/toto_mt5_fx28_cierre_c20261101
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset mt5_fx28_cierre_c20261101 --modelos fincast --hilos 2 --solo-limpia --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/mt5_fx28_cierre_c20261101
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --informe E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_cierre_c20261101 E:/quantdesk-lab/runs/TS-00-BENCH/mt5_fx28_hist_cierre_c20261101 --toto E:/quantdesk-lab/runs/TS-00-BENCH/toto_mt5_fx28_cierre_c20261101 --fincast E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/mt5_fx28_cierre_c20261101 --pilotos E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_cabecera E:/quantdesk-lab/runs/TS-00-BENCH/piloto_mt5_ampliacion E:/quantdesk-lab/runs/TS-00-BENCH/piloto_toto_mt5_cabecera E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_mt5_cabecera --destino docs/plans/current/execution/TS-00-BENCH-MT5/completo
```
