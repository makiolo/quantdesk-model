"""Crea el venv del laboratorio y lo deja configurado (LAB-00-ENV-A).

Uso:
  D:/miniconda312/python.exe -X utf8 scripts/setup_env.py [--venv RUTA] [--lock FICHERO] [--base PYTHON]
  D:/miniconda312/python.exe scripts/setup_env.py --selftest

Pasos:
  1. Comprueba que el Python base es 3.12.x (D:/miniconda312/python.exe = 3.12.3 en esta maquina).
  2. Crea el venv si no existe (por defecto <repo>/.venv).
  3. Escribe <venv>/pip.ini (cache-dir de pip) y <venv>/Lib/site-packages/sitecustomize.py. Ese
     sitecustomize ASIGNA HF_HOME, PIP_CACHE_DIR, TORCH_HOME, XDG_CACHE_HOME, TEMP y TMP bajo
     E:/quantdesk-lab, asi que cualquier proceso del venv (activado o no) las usa.
  4. Instala requirements.lock con --require-hashes.
Todo subproceso recibe las variables con env=, incluido el primer pip.
Solo biblioteca estandar.
"""
from __future__ import annotations

import argparse
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = "E:/quantdesk-lab"
TMP_DIR = LAB + "/tmp/env-a"
BASE_PYTHON = "D:/miniconda312/python.exe"
BASE_VERSION_PREFIX = "3.12."

# Cachés y temporales del laboratorio. TORCH_HOME y XDG_CACHE_HOME van bajo cache/hf porque
# la ficha solo autoriza E:/quantdesk-lab/{cache/hf,cache/pip,tmp,...}.
LAB_ENV = {
    "HF_HOME": LAB + "/cache/hf",
    "PIP_CACHE_DIR": LAB + "/cache/pip",
    "TORCH_HOME": LAB + "/cache/hf/torch",
    "XDG_CACHE_HOME": LAB + "/cache/hf/xdg",
    # tempfile lee TMPDIR antes que TEMP y TMP; en esta maquina TMPDIR apunta a C:.
    "TMPDIR": TMP_DIR,
    "TEMP": TMP_DIR,
    "TMP": TMP_DIR,
}
LAB_DIRS = [
    LAB + "/" + d
    for d in ("data", "datasets", "runs", "artifacts", "cache/hf", "cache/pip", "tmp/env-a")
] + [LAB_ENV["TORCH_HOME"], LAB_ENV["XDG_CACHE_HOME"]]


def under_lab(path: str) -> bool:
    """True si path cae dentro de E:/quantdesk-lab (normalizado, sin distinguir mayusculas)."""
    p = os.path.normcase(os.path.abspath(path))
    lab = os.path.normcase(os.path.abspath(LAB))
    return p == lab or p.startswith(lab + os.sep)


def lab_env() -> dict:
    """Entorno para subprocesos: el actual mas las variables del laboratorio."""
    env = dict(os.environ)
    env.update(LAB_ENV)
    return env


def make_dirs() -> None:
    for d in LAB_DIRS:
        os.makedirs(d, exist_ok=True)


def is_base_version(text: str) -> bool:
    return text.strip().startswith(BASE_VERSION_PREFIX)


def sitecustomize_text() -> str:
    # Asignacion directa: TEMP/TMP de esta maquina apuntan a C:, un setdefault no lo corregiria.
    return (
        "# Generado por scripts/setup_env.py (LAB-00-ENV-A). No editar a mano.\n"
        "import os as _os\n"
        "_LAB_ENV = " + repr(LAB_ENV) + "\n"
        "for _k, _v in _LAB_ENV.items():\n"
        "    _os.environ[_k] = _v\n"
        "    _os.makedirs(_v, exist_ok=True)\n"
    )


def pip_ini_text() -> str:
    return (
        "[global]\n"
        "cache-dir = " + LAB_ENV["PIP_CACHE_DIR"] + "\n"
        "disable-pip-version-check = true\n"
    )


def ensure_venv(venv: str, base: str) -> None:
    out = subprocess.run(
        [base, "-c", "import sys; print('%d.%d.%d' % sys.version_info[:3])"],
        env=lab_env(), capture_output=True, text=True, check=True,
    ).stdout
    if not is_base_version(out):
        raise SystemExit(f"BLOQUEADO: el Python base {base} es {out.strip()}; se exige 3.12.x")
    if not os.path.isfile(os.path.join(venv, "Scripts", "python.exe")):
        subprocess.run([base, "-m", "venv", venv], env=lab_env(), check=True)


def write_config(venv: str) -> None:
    with open(os.path.join(venv, "pip.ini"), "w", encoding="utf-8", newline="\n") as f:
        f.write(pip_ini_text())
    site = os.path.join(venv, "Lib", "site-packages")
    if not os.path.isdir(site):
        raise SystemExit(f"BLOQUEADO: no existe {site}; el venv no esta bien creado")
    with open(os.path.join(site, "sitecustomize.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sitecustomize_text())


def install(venv: str, lock: str) -> None:
    py = os.path.join(venv, "Scripts", "python.exe")
    subprocess.run(
        [py, "-X", "utf8", "-m", "pip", "install", "--no-input", "--require-hashes", "-r", lock],
        env=lab_env(), check=True,
    )


def selftest() -> None:
    assert all(under_lab(v) for v in LAB_ENV.values()), "variables fuera de E:/quantdesk-lab"
    assert all(under_lab(d) for d in LAB_DIRS), "directorios fuera de E:/quantdesk-lab"
    assert not under_lab("C:/Users/makiolo/AppData/Local/Temp"), "C: aceptado como laboratorio"
    assert not under_lab("E:/quantdesk-lab-otro/x"), "prefijo parecido aceptado como laboratorio"
    assert is_base_version("3.12.3\n") and not is_base_version("3.11.9") and not is_base_version("3.13.0")
    env = lab_env()
    assert all(env[k] == v for k, v in LAB_ENV.items()), "lab_env no asigna las variables"
    s = sitecustomize_text()
    assert "setdefault" not in s and "_os.environ[_k] = _v" in s, "sitecustomize no asigna"
    assert all(repr(v) in s for v in LAB_ENV.values()), "sitecustomize sin todas las rutas"
    assert "cache-dir = " + LAB_ENV["PIP_CACHE_DIR"] in pip_ini_text(), "pip.ini sin cache-dir"
    print("setup_env selftest ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Crea y configura el venv del laboratorio.")
    ap.add_argument("--venv", default=os.path.join(REPO, ".venv"))
    ap.add_argument("--lock", default=os.path.join(REPO, "requirements.lock"))
    ap.add_argument("--base", default=BASE_PYTHON)
    ap.add_argument("--selftest", action="store_true", help="prueba la logica pura, sin crear venvs")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    make_dirs()
    ensure_venv(a.venv, a.base)
    write_config(a.venv)
    install(a.venv, a.lock)
    print("setup_env: venv listo en", a.venv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
