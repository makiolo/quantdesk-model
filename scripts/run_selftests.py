"""Suite completa del proyecto: ejecuta --selftest de cada scripts/*.py que lo soporte.

Uso:
  .venv/Scripts/python -X utf8 scripts/run_selftests.py

Usa el Python del .venv del repo. Un script "soporta" --selftest si su fuente lo menciona.
Sale != 0 si algun selftest falla o si no se ejecuto ninguno. Los scripts sin --selftest se
listan como SIN SELFTEST, nunca se omiten en silencio.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_env import REPO, lab_env  # noqa: E402

VENV_PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
TIMEOUT_S = 900


def supports_selftest(path: str) -> bool:
    with open(path, encoding="utf-8", errors="replace") as f:
        return "--selftest" in f.read()


def main() -> int:
    if not os.path.isfile(VENV_PY):
        print(f"run_selftests: BLOQUEADO, falta el venv {VENV_PY} (ejecutar setup_env.py)")
        return 2
    scripts = sorted(
        p for p in glob.glob(os.path.join(HERE, "*.py"))
        if os.path.basename(p) != os.path.basename(__file__)
    )
    ok_n, fail_n = 0, 0
    for path in scripts:
        name = os.path.relpath(path, REPO).replace(os.sep, "/")
        if not supports_selftest(path):
            print(f"SIN SELFTEST  {name}")
            continue
        try:
            r = subprocess.run(
                [VENV_PY, "-X", "utf8", path, "--selftest"], cwd=REPO, env=lab_env(),
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S,
                check=False,
            )
            out = (r.stdout + r.stderr).strip().splitlines()
            code = r.returncode
        except subprocess.TimeoutExpired:
            out, code = ["timeout tras %d s" % TIMEOUT_S], 1
        last = out[-1] if out else "(sin salida)"
        if code == 0:
            ok_n += 1
            print(f"OK     {name}: {last}")
        else:
            fail_n += 1
            print(f"FALLO  {name} (salida {code}): {last}")
            for line in out[-15:]:
                print("    " + line)
    print(f"run_selftests: {ok_n} OK, {fail_n} FALLO")
    return 1 if fail_n or ok_n == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
