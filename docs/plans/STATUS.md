# Estado global actual

Qué tenemos y qué falta, por área, en una o dos líneas por fila con el ID que cubre cada hueco. Se
actualiza en el mismo commit que cierra cada tarea; el detalle vive en los planes.

| Área | Tenemos | Falta (ID) |
|---|---|---|
| Entorno | `.venv` propio (Python 3.12.3 de `D:/miniconda312`) con `requirements.lock` (hashes, torch 2.15.0+cpu, chronos-forecasting 2.3.2, arch, ml_dtypes, MetaTrader5, pyarrow) y la rueda `quantdesk-0.0.0-cp312` de quantdesk `69fdb39d` (sha256 `28c1ed66…c3fd`, `E:/quantdesk-lab/wheels/`); cachés y temporales en `E:/quantdesk-lab/`; humo con HMM y suite `scripts/run_selftests.py` en verde (LAB-00-ENV, 2026-11-08) | Recompilar con `build_wheels.py` corregido al subir de commit del motor (decisión del usuario) |
| Datos | `scripts/inventario_options_chain.py` extendido a todos los topics `market.*` (TI-01-INV, `cb46ce2`, revisado; sin ejecutar: falta el token) | TI-01-INV, TI-09-ARCH, TI-12-MT5, TI-13-PUB, TI-02-DATA |
| Banco | HMM desde Python comprobado (backlog §2.1) | TS-00-PREC, TS-00-BENCH, TS-00-OBJ |
