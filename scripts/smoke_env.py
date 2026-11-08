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
import base64
import csv
import hashlib
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
WHEEL_PATH = LAB + "/wheels/" + WHEEL_NAME
WHEEL_SUMS = LAB + "/wheels/SHA256SUMS"
ENGINE_MODULES = ("quantdesk", "data_py", "market_py", "findsl_py", "strategy_py")
# Comprobacion HMM de docs/plans (backlog 2.1): serie sintetica de 400 dias, 200 caminos a 20 dias.
HMM_DAYS = 400
HMM_PATHS = 200
HMM_HORIZON = 20
HMM_SEED = 42
HMM_TEMPLATE_P = ((0.9, 0.1), (0.1, 0.9))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_sums() -> dict:
    sums = {}
    with open(WHEEL_SUMS, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                sums[parts[1]] = parts[0]
    return sums


def lock_quantdesk_block() -> str:
    """Lineas de requirements.lock que pertenecen a la entrada quantdesk (la de file:/// y sus --hash)."""
    with open(os.path.join(REPO, "requirements.lock"), encoding="utf-8") as f:
        lines = f.read().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("quantdesk @"):
            return " ".join(lines[i:i + 2])
    return ""


def check_wheel_pin() -> None:
    """El sha256 real del fichero de la rueda debe coincidir con SHA256SUMS y con requirements.lock."""
    expected = read_sums().get(WHEEL_NAME)
    if expected is None or not os.path.isfile(WHEEL_PATH):
        record("FALLO", "rueda: sha256", f"{WHEEL_NAME} ausente de SHA256SUMS o del disco")
        return
    actual = sha256_file(WHEEL_PATH)
    in_lock = f"--hash=sha256:{actual}" in lock_quantdesk_block()
    ok = actual == expected and in_lock
    record("OK" if ok else "FALLO", "rueda: sha256 fichero = SHA256SUMS = lock",
           f"{actual} (commit {WHEEL_SOURCE_COMMIT}); SHA256SUMS={'si' if actual == expected else 'NO'}; lock={'si' if in_lock else 'NO'}")


def check_installed_record() -> None:
    """Cada fichero instalado de quantdesk debe tener el sha256 que declara su RECORD."""
    dist = md.distribution("quantdesk")
    text = dist.read_text("RECORD")
    if not text:
        record("FALLO", "RECORD instalado", "quantdesk no tiene RECORD")
        return
    checked, pyd, bad = 0, 0, []
    for row in csv.reader(text.splitlines()):
        if len(row) != 3 or not row[1].startswith("sha256="):
            continue  # el propio RECORD no lleva hash
        path = str(dist.locate_file(row[0]))
        if not os.path.isfile(path):
            bad.append(f"{row[0]} ausente")
            continue
        with open(path, "rb") as f:
            digest = base64.urlsafe_b64encode(hashlib.sha256(f.read()).digest()).rstrip(b"=").decode("ascii")
        if digest != row[1][len("sha256="):]:
            bad.append(f"{row[0]} distinto")
        checked += 1
        pyd += row[0].endswith(".pyd")
    ok = not bad and pyd >= 5
    record("OK" if ok else "FALLO", "RECORD instalado",
           f"{checked} ficheros con hash igual al RECORD ({pyd} .pyd); desajustes: {bad or 'ninguno'}")


def calibration_summary(np, fit):
    """Valida la salida de una calibracion y devuelve (loglik por iteracion, pi, P). Lanza si algo no cuadra."""
    d = fit.hmm
    if d is None:
        raise RuntimeError("la calibracion no trae HmmDiagnostics")
    ll = np.asarray(d.loglik_per_iteration, dtype=np.float64)
    k = len(d.occupations)
    pi = np.asarray(d.pi_estimated, dtype=np.float64)
    p = np.asarray(d.transition_matrix_estimated, dtype=np.float64).reshape(k, k)
    if ll.size < 2 or not np.isfinite(ll).all():
        raise RuntimeError(f"log-verosimilitud por iteracion no finita o demasiado corta ({ll.size})")
    if not ll[-1] > ll[0] + 1e-6 * abs(ll[0]):
        raise RuntimeError(f"la log-verosimilitud no sube desde la inicial ({ll[0]:.6f} -> {ll[-1]:.6f})")
    if not (np.isfinite(pi).all() and abs(pi.sum() - 1.0) < 1e-6 and (pi >= 0).all()):
        raise RuntimeError(f"pi estimada invalida: {pi.tolist()}")
    if not (np.isfinite(p).all() and np.abs(p.sum(axis=1) - 1.0).max() < 1e-6 and (p >= 0).all()):
        raise RuntimeError(f"matriz de transicion estimada invalida: {p.tolist()}")
    return ll, pi, p


def synthetic_series(q, np, eng, obs: str, t, seed: int):
    truth = q.Hmm(
        states=(q.GbmP(s0=1.0, mu=0.02, sigma=0.08, observable=obs), q.GbmP(s0=1.0, mu=-0.05, sigma=0.2, observable=obs)),
        initial_probabilities=(0.6, 0.4),
        transition_matrix=((0.95, 0.05), (0.08, 0.92)),
        transition_interval=1.0 / 252.0,
    )
    sim = np.asarray(eng.simulate(truth, t, 1, seed).values, dtype=np.float64)
    if sim.shape[:2] != (1, len(t)) or not np.isfinite(sim).all():
        raise RuntimeError(f"serie sintetica con forma {sim.shape} o valores no finitos")
    return q.ObservedSeries(observable=obs, times=tuple(t), values=tuple(float(x) for x in sim[0, :, 0]))


def check_hmm() -> None:
    """Calibra un Hmm y comprueba que la calibracion hace algo: sube la verosimilitud, mueve la matriz
    de la plantilla, y otra serie da otro resultado. Luego muestrea 200 caminos de 20 dias."""
    import numpy as np
    import quantdesk as q

    eng = q.Engine(n_paths=1, n_steps=1, seed=0)
    obs = "SYN.SPOT"
    t = [i / 252.0 for i in range(HMM_DAYS)]
    series_a = synthetic_series(q, np, eng, obs, t, HMM_SEED)
    series_b = synthetic_series(q, np, eng, obs, t, HMM_SEED + 1)
    template = q.Hmm(
        states=(q.GbmP(s0=1.0, mu=0.0, sigma=0.1, observable=obs), q.GbmP(s0=1.0, mu=0.0, sigma=0.3, observable=obs)),
        initial_probabilities=(0.5, 0.5),
        transition_matrix=HMM_TEMPLATE_P,
        transition_interval=1.0 / 252.0,
    )
    opts = q.HmmCalibrationOptions(seed=7)
    fit_a = eng.calibrate(template, series_a, opts)
    ll_a, pi_a, p_a = calibration_summary(np, fit_a)
    moved = float(np.abs(p_a - np.asarray(HMM_TEMPLATE_P)).max())
    if moved <= 1e-3:
        raise RuntimeError(f"la calibracion deja la matriz igual que la plantilla (|dP|={moved:.2e}): no-op")
    fit_b = eng.calibrate(template, series_b, opts)
    ll_b, _, p_b = calibration_summary(np, fit_b)
    dp = float(np.abs(p_a - p_b).max())
    dll = abs(ll_a[-1] - ll_b[-1])
    if not (dp > 1e-6 or dll > 1e-6 * abs(ll_a[-1])):
        raise RuntimeError("dos series distintas dan la misma calibracion")

    dts = [1.0 / 252.0] * HMM_HORIZON
    paths = np.empty((HMM_PATHS, HMM_HORIZON, 1), dtype=np.float64)
    for i in range(HMM_PATHS):
        block = eng.open_stream(fit_a, HMM_SEED + i, policy="from_calibration_end").advance_many(dts)
        values = np.asarray(block.values, dtype=np.float64)
        if values.shape != (HMM_HORIZON, 1):
            raise RuntimeError(f"camino {i}: forma {values.shape}, esperada ({HMM_HORIZON}, 1)")
        paths[i] = values
    if not np.isfinite(paths).all() or not (paths > 0).all():
        raise RuntimeError("valores no finitos o no positivos en GBM_P")
    again = np.asarray(
        eng.open_stream(fit_a, HMM_SEED, policy="from_calibration_end").advance_many(dts).values, dtype=np.float64
    )
    if not np.array_equal(again, paths[0]):
        raise RuntimeError("misma semilla, distintos valores")
    other = np.asarray(
        eng.open_stream(fit_b, HMM_SEED, policy="from_calibration_end").advance_many(dts).values, dtype=np.float64
    )
    if np.array_equal(other, paths[0]):
        raise RuntimeError("la calibracion de otra serie no cambia el muestreo")
    record("OK", "HMM calibrate + open_stream",
           f"loglik {ll_a[0]:.3f} -> {ll_a[-1]:.3f} en {len(ll_a)} iteraciones "
           f"(converged={fit_a.diagnostics.converged}); |P-P0|={moved:.3f}; "
           f"serie B: |dP|={dp:.3f}, |dLL|={dll:.3f}; "
           f"{HMM_PATHS} caminos x {HMM_HORIZON} dias, forma {paths.shape}, finitos, deterministas")


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
        check_installed_record()
    except Exception as exc:  # noqa: BLE001 - se reporta tal cual
        record("FALLO", "RECORD instalado", f"{type(exc).__name__}: {exc}")
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
