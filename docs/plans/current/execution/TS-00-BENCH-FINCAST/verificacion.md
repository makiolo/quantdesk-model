# Evidencia del gate final

Tabla principal generada: **798 filas idénticas** a la tabla archivada SPRINT-01, incluidos los cuatro modelos
de referencia y la submuestra de Toto. [Comprobación y SHA-256 canónico](principal-identica.json):
`9b8ab8b073e012ec7e7530f56258c74c8fc6c4eb6f9e9c873878a88b1b558294`.

HEAD antes: `5b70106566f54f8b7a76dce81ea2c17de512a4a7`; despues: `5b70106566f54f8b7a76dce81ea2c17de512a4a7`.
SHA-256 del mapa ordenado de todos los scripts Python: `f54c1e750d7028e0f3a91d83429de32ff47c750734aa232260bc47eb46bedfb1`; identico antes/despues.

Comprobaciones de tablas reales: FinCast ausente de principal; solo CRPS deciles/QLIKE finitos, resto de criterios vacios y declarados; cinco modelos con el mismo n por activo/h en la tabla limpia.

[Auditoria de alcance, tests protegidos y constantes de SPRINT-01](alcance.json). El diff global incluye trabajo ajeno concurrente; los commits propios solo contienen rutas autorizadas.

## Selftest del banco

```text
metricas: pinball, CRPS_q, Kupiec, Christoffersen, varianza y QLIKE contra valores a mano: ok
look-ahead: dato tardio x1000 fuera del contexto y sin efecto en hmm/garch/trivial; default_lag_ms 0/1 ms; 9 origenes sin barra nueva omitidos: ok
GARCH(1,1)-t simulado (alpha .08, beta .90, nu 6): estimado alpha 0.076, beta 0.897, nu 5.32: ok
reproducibilidad: dos corridas de 7 origenes x 3 modelos con semilla 20261101: predicciones y metricas identicas (148ce8372ed459d4): ok
toto: venv ausente -> SALTADO sin romper la corrida; trabajador falso por subproceso con el mismo contrato de cuantiles, semilla y errores (4 origenes): ok
crps_deciles: normal exacta contra 9 pinball escalares independientes: ok
ventana limpia: corte UTC estricto, vacia declarada, origenes comunes y mascara FinCast: ok
fincast: trabajador aislado falso, deciles/z, venv/pesos ausentes, timeout y errores por origen: ok
banco: cuantiles no monotonos fallan explicitamente para cualquier modelo: ok
informe limpio: union de corridas, mascara, determinismo y vacio explicito, sin mezclar datasets: ok
  FALLO SINT 1760918400000 fincast: TimeoutError: FinCast timeout tras 0.25 s; trabajador terminado
  SINT: 2/2 origenes, 0 s
timeout persistido: un origen fallido, siguiente valido, recuento en meta y en informe: ok
ventana limpia vacia persistida: dataset antiguo, CSV con cabecera y motivo en meta: ok
selftest ok
```

## Suite completa

```text
OK     scripts/banco_precision.py: selftest ok
OK     scripts/banco_walkforward.py: selftest ok
OK     scripts/build_wheels.py: selftest OK
OK     scripts/cuadre_mt5.py: selftest ok
OK     scripts/descarga_lago.py: selftest ok
OK     scripts/exportar_market_history.py: selftest ok
OK     scripts/extractor_mt5.py: selftest ok
OK     scripts/ingesta_publica.py: selftest ok
OK     scripts/inventario_options_chain.py: selftest ok
OK     scripts/publicador_mt5.py: selftest ok
OK     scripts/setup_env.py: setup_env selftest ok
OK     scripts/smoke_env.py: smoke_env: OK (21 comprobaciones; 0 SALTADAS)
run_selftests: 12 OK, 0 FALLO
```

## Generacion de tablas

```text
S:\Projects\quantdesk-model\.venv\Scripts\python.exe -X utf8 scripts/banco_walkforward.py --informe E:\quantdesk-lab\runs\TS-00-BENCH\lago_cierre_c20261101 E:\quantdesk-lab\runs\TS-00-BENCH\binance_c20261101 --toto E:\quantdesk-lab\runs\TS-00-BENCH\toto_lago_cierre_c20261101 E:\quantdesk-lab\runs\TS-00-BENCH\toto_binance_c20261101 --fincast E:\quantdesk-lab\runs\TS-00-BENCH-FINCAST\fincast_fx E:\quantdesk-lab\runs\TS-00-BENCH-FINCAST\fincast_binance --repeticion E:\quantdesk-lab\runs\TS-00-BENCH-FINCAST\repeticion_fx E:\quantdesk-lab\runs\TS-00-BENCH-FINCAST\repeticion_binance --destino S:\Projects\quantdesk-model\docs\plans\current\execution\TS-00-BENCH-FINCAST\tablas
```

## Huellas de codigo del banco

- `scripts/banco_walkforward.py`: `df73221cdfe5e4978df4f02038e5b29bff66ee5132d324840bf001f23a391751`
- `scripts/banco_walkforward_lib/__init__.py`: `9555cfeca246a2c0936ccfd4aeab66b7fdd4230bf315ec9fe31cfa3e126b7df0`
- `scripts/banco_walkforward_lib/banco.py`: `ee8f04f0e9544308ec47082e10483f78637683f60c5ddb6f44ae87ac65628f18`
- `scripts/banco_walkforward_lib/datos.py`: `c753d8a392cc61522b1c6c4bc8e082f96cd7e42f723699cf4d89505195ac2330`
- `scripts/banco_walkforward_lib/fincast_trabajador.py`: `8ac1df7379e51c1eadc7bc6b28ae865bd98ac4acc6fcafe4dc20587269e60228`
- `scripts/banco_walkforward_lib/informe.py`: `59ec8fb5e7a9cc796b60c56fe87dce0bb5aa540a0b9729449572eb8d88a335b8`
- `scripts/banco_walkforward_lib/metricas.py`: `5846c1faedddff1f426ba74f6a568971792ac74d16c183c44baf3ccfeb42f6d1`
- `scripts/banco_walkforward_lib/modelos.py`: `04fccad98f67c10710bd45fdb369642cd99dfdd361fb48ec91c23c2aa1c568de`
- `scripts/banco_walkforward_lib/pruebas.py`: `fa3e335233ef5636a367ba0a2a3ab29045ac5e7e0c6bef4190a2dfd62fbd03e1`
- `scripts/banco_walkforward_lib/rutas.py`: `17f03ec8f48d2bd62a5b625e9b4e56bcbd6ea20024fa12a63c2412f6d1579916`
- `scripts/banco_walkforward_lib/toto_trabajador.py`: `cb4ae0bfc3f61a0a2ebbc9b7797eff6c3c9e918231967491d3ffc9572151dc69`
