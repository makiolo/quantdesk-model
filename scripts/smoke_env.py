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
from setup_env import LAB, under_lab  # noqa: E402

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


def check_engine(require_engine: bool) -> None:
    if importlib.util.find_spec("quantdesk") is None:
        if require_engine:
            record("FALLO", "motor quantdesk", "rueda pendiente: --require-engine exige quantdesk instalado (fase 2)")
        else:
            record("SALTADO", "motor quantdesk", "rueda pendiente: comprobacion HMM de 2.1 NO ejecutada (fase 1)")
        return
    record("FALLO", "motor quantdesk", "quantdesk presente, pero la comprobacion HMM aun no esta escrita (fase 2)")


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
