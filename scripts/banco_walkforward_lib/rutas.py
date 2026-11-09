"""Rutas donde banco_walkforward.py puede escribir (ficha TS-00-BENCH, rutas autorizadas).

--out: solo un subdirectorio de E:/quantdesk-lab/runs/TS-00-BENCH/.
--informe (destino): docs/plans/current/execution/TS-00-BENCH/ del repositorio o un subdirectorio de RUNS.
Los datasets se leen de E:/quantdesk-lab/datasets/TI-02-DATA/ y nunca se escriben.
Las rutas se comparan resueltas (realpath), sin distinguir mayusculas en Windows.
"""
from __future__ import annotations

import os

LAB = "E:/quantdesk-lab"
RUNS = LAB + "/runs/TS-00-BENCH"
TMP = LAB + "/tmp/TS-00-BENCH"
DATASETS = LAB + "/datasets/TI-02-DATA"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(REPO, "docs", "plans", "current", "execution", "TS-00-BENCH")


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
    if not out or not dentro(out, RUNS, estricto=True):
        raise RutaNoAutorizada(f"--out debe ser un subdirectorio de {RUNS} (recibido {out!r})")
    return os.path.abspath(out)


def validar_destino_informe(d: str) -> str:
    if not d or not (dentro(d, RUNS, estricto=True) or dentro(d, DOCS)):
        raise RutaNoAutorizada(
            f"--destino debe ser {DOCS.replace(os.sep, '/')} o un subdirectorio de {RUNS} (recibido {d!r})"
        )
    return os.path.abspath(d)


def dataset_dir(nombre: str) -> str:
    if not nombre or "/" in nombre or "\\" in nombre or nombre.startswith("."):
        raise RutaNoAutorizada(f"--dataset debe ser un nombre de {DATASETS} (recibido {nombre!r})")
    return DATASETS + "/" + nombre
