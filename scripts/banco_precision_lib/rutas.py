"""Rutas donde banco_precision.py puede escribir desde la linea de ordenes (ficha TS-00-PREC, rutas autorizadas).

--out: solo un subdirectorio de E:/quantdesk-lab/runs/TS-00-PREC/.
--informe: un subdirectorio de E:/quantdesk-lab/runs/TS-00-PREC/ o el directorio documental
docs/plans/current/execution/TS-00-PREC/ del repositorio (o uno dentro de el).
Cualquier otra ruta (otro disco, otro proyecto, un ".." que se escape, un enlace o union que apunte fuera) se rechaza
con RutaNoAutorizada. Las rutas se comparan resueltas (realpath), sin distinguir mayusculas en Windows.
"""
from __future__ import annotations

import os

RUNS = "E:/quantdesk-lab/runs/TS-00-PREC"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(REPO, "docs", "plans", "current", "execution", "TS-00-PREC")


class RutaNoAutorizada(ValueError):
    pass


def _real(p: str) -> str:
    return os.path.normcase(os.path.realpath(os.path.abspath(p)))


def dentro(ruta: str, base: str, estricto: bool = False) -> bool:
    """True si ruta esta dentro de base (estricto: dentro y distinta de base). Compara rutas resueltas."""
    r, b = _real(ruta), _real(base).rstrip(os.sep)
    if r == b:
        return not estricto
    return r.startswith(b + os.sep)


def validar_out(out: str) -> str:
    """Ruta absoluta de --out si es un subdirectorio de RUNS; si no, RutaNoAutorizada."""
    if not out or not dentro(out, RUNS, estricto=True):
        raise RutaNoAutorizada(f"--out debe ser un subdirectorio de {RUNS} (recibido {out!r})")
    return os.path.abspath(out)


def validar_informe(directorio: str) -> str:
    """Ruta absoluta de --informe si esta bajo RUNS (subdirectorio) o en DOCS; si no, RutaNoAutorizada."""
    if not directorio or not (dentro(directorio, RUNS, estricto=True) or dentro(directorio, DOCS)):
        raise RutaNoAutorizada(
            f"--informe debe ser un subdirectorio de {RUNS} o {DOCS.replace(os.sep, '/')} (recibido {directorio!r})"
        )
    return os.path.abspath(directorio)
