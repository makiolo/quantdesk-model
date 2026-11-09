# Estado global actual

Qué tenemos y qué falta, por área, en una o dos líneas por fila con el ID que cubre cada hueco. Se
actualiza en el mismo commit que cierra cada tarea; el detalle vive en los planes.

| Área | Tenemos | Falta (ID) |
|---|---|---|
| Entorno | `.venv` propio (Python 3.12.3 de `D:/miniconda312`) con `requirements.lock` (hashes, torch 2.15.0+cpu, chronos-forecasting 2.3.2, arch, ml_dtypes, MetaTrader5, pyarrow) y la rueda `quantdesk-0.0.0-cp312` de quantdesk `69fdb39d` (sha256 `28c1ed66…c3fd`, `E:/quantdesk-lab/wheels/`); cachés y temporales en `E:/quantdesk-lab/`; humo con HMM y suite `scripts/run_selftests.py` en verde (LAB-00-ENV, 2026-11-08) | Recompilar con `build_wheels.py` corregido al subir de commit del motor (decisión del usuario) |
| Datos | Inventario del lago de qn (TI-01-INV, 2026-11-08, `execution/TI-01-INV/`):
- OHLCV de 28 cruces FX diarios desde 2024-11 (99 %); los horarios, desde 2026-10-18.
- Tipos (103 nodos) y rendimientos (64) desde 2025-12, con un hueco de 2026-04 a 2026-09.
- **`market.options.chain` y `market.options.fx`, vacíos en `main`.**
- La flota de qn no tiene GPU. Ingesta pública con licencias verificadas y filtro de fugas D-11 (TI-13-PUB, `7ea6d94`, 2026-11-08): 36 datasets (Chronos, LOTSA, Binance; 1,0 GB de 100 GB) en `E:/quantdesk-lab/datasets/TI-13-PUB/`, partición train/val disjunta, `--verificar` en verde; corte D-11 provisional 2016-10-01.
- Exportador a `engine.market-history/v1` (TI-02-DATA, `906f73e`, 2026-11-09). Cuatro datasets congelados en `E:/quantdesk-lab/datasets/TI-02-DATA/`, con hash reproducible y 0 violaciones de look-ahead:
  - `binance_c20261101`;
  - `lago_c20261101`, estricto: sin ohlcv, porque qn recibió la historia el 2026-11-01;
  - `lago_cierre_c20261101`, proxy declarado con `default_lag_ms`: valores recibidos después del corte;
  - `lago_c20261107`.
  El volcado del lago está en `E:/quantdesk-lab/data/lago/2026-11-08/` | TI-12-MT5; TI-09-ARCH retirada del sprint (sin datos de origen; vuelve desde el backlog cuando el backend publique la cadena) |
| Banco | HMM desde Python comprobado (backlog §2.1). Banco de precisión emulado (TS-00-PREC, `5afc795`, 2026-11-08): fp8 basta para la entrada, no para la inferencia emulada ni para σ_loc; bf16/f16/f32 no pierden; hash `83548e1a…` reproducido por la raíz | TS-00-BENCH, TS-00-OBJ |
