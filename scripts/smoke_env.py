"""Prueba de humo del entorno del laboratorio (LAB-00-ENV-A).

Uso, con el venv del laboratorio:
  .venv/Scripts/python -X utf8 scripts/smoke_env.py [--selftest] [--require-engine]

--selftest es la prueba entera (tambien es el modo por defecto). Sale != 0 si algo falla y
dice que. Solo imports y comprobaciones de rutas y versiones: no descarga pesos, no hace red
salvo lo que hace pip, y MetaTrader5 solo se importa (nunca initialize, login ni ordenes).

Fase 1: si quantdesk no esta instalado, la parte del motor se SALTA con un mensaje explicito.
--require-engine la hace obligatoria (fase 2, con la rueda instalada).
"""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata as md
import importlib.util
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setup_env import LAB, REPO, under_lab  # noqa: E402

DIRECT = {
    "pyarrow": "pyarrow",
    "ml_dtypes": "ml_dtypes",
    "arch": "arch",
    "MetaTrader5": "MetaTrader5",
    "torch": "torch",
    "chronos": "chronos-forecasting",
}

results: list[tuple[str, str, str]] = []  # (estado, nombre, detalle)


def record(state: str, name: str, detail: str) -> None:
    results.append((state, name, detail))
    print(f"{state:<8} {name}: {detail}")


def check_imports() -> None:
    for mod, dist in DIRECT.items():
        try:
            importlib.import_module(mod)
            record("OK", f"import {mod}", f"{dist} {md.version(dist)}")
        except Exception as exc:  # noqa: BLE001 - se reporta tal cual
            record("FALLO", f"import {mod}", f"{type(exc).__name__}: {exc}")


def check_torch_cpu() -> None:
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        record("FALLO", "torch CPU", f"no importa: {exc}")
        return
    ok = "+cpu" in torch.__version__ and torch.version.cuda is None
    record("OK" if ok else "FALLO", "torch CPU", f"torch.__version__={torch.__version__} torch.version.cuda={torch.version.cuda}")


def check_lab_paths() -> None:
    for var in ("HF_HOME", "PIP_CACHE_DIR", "TORCH_HOME", "XDG_CACHE_HOME", "TMPDIR", "TEMP", "TMP"):
        val = os.environ.get(var, "")
        ok = bool(val) and under_lab(val)
        record("OK" if ok else "FALLO", f"env {var}", val or "(vacia)")
    tmp = tempfile.gettempdir()
    record("OK" if under_lab(tmp) else "FALLO", "tempfile.gettempdir", tmp)
    pip_dir = subprocess.run(
        [sys.executable, "-m", "pip", "cache", "dir"], capture_output=True, text=True, check=False,
    ).stdout.strip()
    record("OK" if pip_dir and under_lab(pip_dir) else "FALLO", "pip cache dir", pip_dir or "(sin salida)")
    pip_ini = os.path.join(sys.prefix, "pip.ini")
    record("OK" if os.path.isfile(pip_ini) else "FALLO", "pip.ini del venv", pip_ini)


WHEEL_NAME = "quantdesk-0.0.0-cp312-cp312-win_amd64.whl"
# Commit de quantdesk del que se compila la rueda (LAB-00-ENV-B, a581355).
WHEEL_SOURCE_COMMIT = "69fdb39d0b67969dbdafa77f5da656511342f175"
WHEEL_SUMS = LAB + "/wheels/SHA256SUMS"
ENGINE_MODULES = ("quantdesk", "data_py", "market_py", "findsl_py", "strategy_py")
# Comprobacion HMM de docs/plans (backlog 2.1): serie sintetica de 400 dias, 200 caminos a 20 dias.
HMM_DAYS = 400
HMM_PATHS = 200
HMM_HORIZON = 20
HMM_SEED = 42


def check_wheel_pin() -> None:
    """La rueda instalada debe ser la de SHA256SUMS y su hash debe estar en requirements.lock."""
    sums = {}
    with open(WHEEL_SUMS, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                sums[parts[1]] = parts[0]
    digest = sums.get(WHEEL_NAME)
    if digest is None:
        record("FALLO", "rueda en SHA256SUMS", f"{WHEEL_NAME} no aparece en {WHEEL_SUMS}")
        return
    with open(os.path.join(REPO, "requirements.lock"), encoding="utf-8") as f:
        lock = f.read()
    ok = f"--hash=sha256:{digest}" in lock
    record("OK" if ok else "FALLO", "rueda en requirements.lock", f"sha256 {digest} (commit {WHEEL_SOURCE_COMMIT})")


def check_hmm() -> None:
    """Calibra un Hmm con Engine.calibrate y muestrea 200 caminos de 20 dias con open_stream."""
    import numpy as np
    import quantdesk as q

    eng = q.Engine(n_paths=1, n_steps=1, seed=0)
    obs = "SYN.SPOT"
    t = [i / 252.0 for i in range(HMM_DAYS)]
    truth = q.Hmm(
        states=(q.GbmP(s0=1.0, mu=0.02, sigma=0.08, observable=obs), q.GbmP(s0=1.0, mu=-0.05, sigma=0.2, observable=obs)),
        initial_probabilities=(0.6, 0.4),
        transition_matrix=((0.95, 0.05), (0.08, 0.92)),
        transition_interval=1.0 / 252.0,
    )
    sim = np.asarray(eng.simulate(truth, t, 1, HMM_SEED).values, dtype=np.float64)
    if sim.shape[:2] != (1, HMM_DAYS) or not np.isfinite(sim).all():
        record("FALLO", "serie sintetica", f"forma {sim.shape} o valores no finitos")
        return
    series = q.ObservedSeries(observable=obs, times=tuple(t), values=tuple(float(x) for x in sim[0, :, 0]))
    template = q.Hmm(
        states=(q.GbmP(s0=1.0, mu=0.0, sigma=0.1, observable=obs), q.GbmP(s0=1.0, mu=0.0, sigma=0.3, observable=obs)),
        initial_probabilities=(0.5, 0.5),
        transition_matrix=((0.9, 0.1), (0.1, 0.9)),
        transition_interval=1.0 / 252.0,
    )
    res = eng.calibrate(template, series, q.HmmCalibrationOptions(seed=7))
    dts = [1.0 / 252.0] * HMM_HORIZON
    paths = np.empty((HMM_PATHS, HMM_HORIZON, 1), dtype=np.float64)
    for i in range(HMM_PATHS):
        block = eng.open_stream(res, HMM_SEED + i, policy="from_calibration_end").advance_many(dts)
        values = np.asarray(block.values, dtype=np.float64)
        if values.shape != (HMM_HORIZON, 1):
            record("FALLO", "HMM open_stream", f"camino {i}: forma {values.shape}, esperada ({HMM_HORIZON}, 1)")
            return
        paths[i] = values
    if not np.isfinite(paths).all() or not (paths > 0).all():
        record("FALLO", "HMM caminos", "valores no finitos o no positivos en GBM_P")
        return
    again = np.asarray(
        eng.open_stream(res, HMM_SEED, policy="from_calibration_end").advance_many(dts).values, dtype=np.float64
    )
    if not np.array_equal(again, paths[0]):
        record("FALLO", "HMM determinismo", "misma semilla, distintos valores")
        return
    record("OK", "HMM calibrate + open_stream",
           f"serie {HMM_DAYS} dias; {HMM_PATHS} caminos x {HMM_HORIZON} dias; forma {paths.shape}; finitos; determinista")


def check_engine(require_engine: bool) -> None:
    if importlib.util.find_spec("quantdesk") is None:
        if require_engine:
            record("FALLO", "motor quantdesk", "rueda pendiente: --require-engine exige quantdesk instalado (fase 2)")
        else:
            record("SALTADO", "motor quantdesk", "rueda pendiente: comprobacion HMM de 2.1 NO ejecutada (fase 1)")
        return
    try:
        for m in ENGINE_MODULES:
            importlib.import_module(m)
        record("OK", "import motor", f"quantdesk {md.version('quantdesk')} (commit {WHEEL_SOURCE_COMMIT}); "
               + ", ".join(ENGINE_MODULES))
    except Exception as exc:  # noqa: BLE001 - se reporta tal cual
        record("FALLO", "import motor", f"{type(exc).__name__}: {exc}")
        return
    check_wheel_pin()
    try:
        check_hmm()
    except Exception as exc:  # noqa: BLE001 - se reporta tal cual
        record("FALLO", "HMM calibrate + open_stream", f"{type(exc).__name__}: {exc}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Prueba de humo del entorno del laboratorio.")
    ap.add_argument("--selftest", action="store_true", help="la prueba entera (por defecto)")
    ap.add_argument("--require-engine", action="store_true", help="exige la parte del motor (fase 2)")
    a = ap.parse_args(argv)
    print(f"python {sys.version.split()[0]} en {sys.executable}; lab={LAB}")
    check_imports()
    check_torch_cpu()
    check_lab_paths()
    check_engine(a.require_engine)
    fallos = [r for r in results if r[0] == "FALLO"]
    saltados = [r for r in results if r[0] == "SALTADO"]
    if fallos:
        print(f"smoke_env: FALLO ({len(fallos)} comprobaciones)")
        return 1
    print(f"smoke_env: OK ({len(results) - len(saltados)} comprobaciones; {len(saltados)} SALTADAS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
