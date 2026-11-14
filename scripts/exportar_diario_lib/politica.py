"""Parametros versionados; el universo se congela desde la rueda aprobada de quantdesk."""
from __future__ import annotations

import json
from pathlib import Path

from descarga_lago import POLITICA_FUENTES, regla_fuente

VERSION = "ti-02-diario.politica/v2"
INTENTOS_PUBLICACION = 3
DESDE = "2016-01-01"
FESTIVOS_FX = ((1, 1), (12, 25))
WHEEL = Path("E:/quantdesk-lab/wheels/quantdesk-0.0.0-cp312-cp312-win_amd64.whl")
WHEEL_SHA256 = "28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd"
PANDAS = "3.1.1"
PYARROW = "26.0.1"
UNIVERSO = json.loads((Path(__file__).with_name("fixtures") / "universo.json").read_text(encoding="utf-8"))


def mapa_simbolos():
    mapa = {}
    for item in UNIVERSO:
        original = item["yahoo"]
        simbolos = [original]
        if item["kind"] == "fx":
            par = original.removesuffix("=X")
            simbolos += [par, par[:3] + "/" + par[3:]]
        else:
            simbolos += [original.replace("-", "."), original.replace("-", "_")]
            if original == "^GSPC":
                simbolos += ["SPX"]
        for symbol in simbolos:
            mapa[symbol] = {"symbol": item["observable"], "kind": item["kind"],
                            "calendar": "FX" if item["kind"] == "fx" else "NYSE"}
    return mapa


MAPA = mapa_simbolos()
FX_ESPERADOS = tuple(item["yahoo"].removesuffix("=X") for item in UNIVERSO if item["kind"] == "fx")


def fuente_fx():
    fuentes = {regla_fuente(s, "1d")["source"] for s in FX_ESPERADOS}
    if len(fuentes) != 1:
        raise ValueError("la politica FX debe declarar una fuente unica")
    return fuentes.pop()


def festivo_fx(d):
    return (d.month, d.day) in FESTIVOS_FX
