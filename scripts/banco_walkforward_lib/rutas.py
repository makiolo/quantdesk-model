"""Rutas donde banco_walkforward.py puede escribir (ficha TS-00-BENCH, rutas autorizadas).

--out: subdirectorio de E:/quantdesk-lab/runs/TS-00-BENCH/ o TS-00-BENCH-FINCAST/.
--informe (destino): docs/plans/current/execution/TS-00-BENCH-FINCAST/ o TS-00-BENCH-MT5/ o subdirectorio de RUNS.
Los datasets antiguos se leen de TI-02-DATA; los dos MT5 fijados, de TI-02-DATA-V2. Nunca se escriben.
Las rutas se comparan resueltas (realpath), sin distinguir mayusculas en Windows.
"""
from __future__ import annotations

import os

LAB = "E:/quantdesk-lab"
RUNS = LAB + "/runs/TS-00-BENCH"
TMP = os.environ.get("QUANTDESK_BENCH_TMP", LAB + "/tmp/TS-00-BENCH")
RUNS_FINCAST = LAB + "/runs/TS-00-BENCH-FINCAST"
TMP_FINCAST = os.environ.get("QUANTDESK_BENCH_TMP", LAB + "/tmp/TS-00-BENCH-FINCAST")
DATASETS = LAB + "/datasets/TI-02-DATA"
DATASETS_V2 = LAB + "/datasets/TI-02-DATA-V2"
HASHES_MT5 = {
    "mt5_fx28_cierre_c20261101": "sha256:a5015bc95b7b410b090785e8e9a118e5cb9276086e9c6a05f69932f0df9893da",
    "mt5_fx28_hist_cierre_c20261101": "sha256:47d79b39fd682ebd6adc92aeb429edcb535884c9e2fb4d58d9c1b4cc16067d32",
}
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(REPO, "docs", "plans", "current", "execution", "TS-00-BENCH-FINCAST")
DOCS_MT5 = os.path.join(REPO, "docs", "plans", "current", "execution", "TS-00-BENCH-MT5")


class RutaNoAutorizada(ValueError):
    pass


def _real(p: str) -> str:
    return os.path.normcase(os.path.realpath(os.path.abspath(p)))


def dentro(ruta: str, base: str, estricto: bool = False) -> bool:
    r, b = _real(ruta), _real(base).rstrip(os.sep)
    if r == b:
        return not estricto
    return r.startswith(b + os.sep)


def validar_out(out: str) -> str:
    if not out or not any(dentro(out, b, estricto=True) for b in (RUNS, RUNS_FINCAST)):
        raise RutaNoAutorizada(f"--out debe ser subdirectorio de {RUNS} o {RUNS_FINCAST} (recibido {out!r})")
    return os.path.abspath(out)


def validar_destino_informe(d: str) -> str:
    if not d or not (any(dentro(d, b, estricto=True) for b in (RUNS, RUNS_FINCAST))
                     or any(dentro(d, b) for b in (DOCS, DOCS_MT5))):
        raise RutaNoAutorizada(
            f"--destino debe ser {DOCS.replace(os.sep, '/')} o un subdirectorio de {RUNS} (recibido {d!r})"
        )
    return os.path.abspath(d)


def dataset_dir(nombre: str) -> str:
    if not nombre or "/" in nombre or "\\" in nombre or nombre.startswith("."):
        raise RutaNoAutorizada(f"--dataset debe ser un nombre de {DATASETS} (recibido {nombre!r})")
    return (DATASETS_V2 if nombre in HASHES_MT5 else DATASETS) + "/" + nombre
