"""Reproduccion offline: fixture realista, proceso hijo y picos Windows.

Desde el repo: .venv/Scripts/python.exe -B -X utf8
  scripts/archivo_opciones_lib/medidas.py --base E:/quantdesk-lab/tmp/TI-09-ARCH/memoria_c2
No instala nada. Los volcados y datasets grandes se borran tras medir;
resultado.json y los logs pequenos permanecen como evidencia.
"""
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.dont_write_bytecode = True

import argparse
from datetime import date, timedelta
import json
import math
import shutil
import subprocess
import time
from unittest.mock import patch

from descarga_opciones import ESQUEMA, TAGS, fila_fixture, guardar_json, json_texto, sha256

DIAS = ["2026-11-12", "2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18"]
MATS = ["2026-11-20", "2026-11-27", "2026-12-04", "2026-12-11", "2026-12-18", "2027-01-15",
        "2027-02-19", "2027-03-19", "2027-06-18", "2027-09-17", "2027-12-17", "2028-01-21",
        "2028-06-16", "2028-12-15", "2029-01-19", "2029-06-15", "2029-12-21"]


def generar(base):
    symbols = [(s, "ETF") for s in ("SPY", "QQQ", "IWM", "DIA")]
    symbols += [(s, "INDEX") for s in ("^SPX", "^NDX", "^VIX")]
    symbols += [("AAPL", "EQUITY")] + [(f"EQ{i:03d}", "EQUITY") for i in range(1, 502)]
    assert len(symbols) == 509 and len(set(symbols)) == 509
    assert [sum(t == tipo for _, t in symbols) for tipo in ("EQUITY", "ETF", "INDEX")] == [502, 4, 3]
    combos = [(s, t, o) for s, t in symbols for o in ("call", "put")]
    especiales = {"SPY": 5208, "AAPL": 1432, "^VIX": 449}
    ordinarios = [c for c in combos if c[0] not in especiales]
    resto = 432000 - 2 * sum(especiales.values())
    cantidades = {c: resto // len(ordinarios) + (i < resto % len(ordinarios)) for i, c in enumerate(ordinarios)}
    cantidades.update({c: especiales[c[0]] for c in combos if c[0] in especiales})
    assert sum(cantidades.values()) == 432000
    spy_mats = set(MATS)
    semana = date(2026, 11, 20)
    while len(spy_mats) < 31:
        spy_mats.add(semana.isoformat())
        semana += timedelta(days=7)
    forma = dict(filas_por_sesion=432000, subyacentes=509, equities=502, etfs=4, indices=3,
                 spy_por_tipo=5208, spy_vencimientos=31, spy_strikes=168,
                 aapl_por_tipo=1432, vix_por_tipo=449, vix_vencimientos=12, semilla=0)
    dumps = [base / f"volcado_{n}" for n in (1, 5)]
    for p in dumps:
        p.mkdir()
    files = [[], []]
    for j, combo in enumerate(combos):
        tags = dict(zip(TAGS, combo))
        count = cantidades[combo]
        mats = sorted(spy_mats) if combo[0] == "SPY" else MATS[:16 if combo[0] == "AAPL" else 12 if combo[0] == "^VIX" else 10 + j % 8]
        nstrikes = math.ceil(count / len(mats))
        spot = {"SPY": 757.1199951171875, "^SPX": 7500.0, "^NDX": 26000.0,
                "^VIX": 18.700000762939453, "AAPL": 354.8800048828125}.get(combo[0], 50.0 + j % 450)
        paso = {"SPY": 5, "AAPL": 5, "^VIX": .5}.get(combo[0], max(.5, round(spot * .03 * 2) / 2))
        strike_min = max(paso, round((spot - (nstrikes - 1) * paso / 2) / paso) * paso)
        rutas = [p / f"opciones_{j:05d}.ndjson" for p in dumps]
        with rutas[0].open("w", encoding="utf-8", newline="\n") as uno, rutas[1].open("w", encoding="utf-8", newline="\n") as cinco:
            for sesion in DIAS:
                from archivo_opciones_lib.lector import ns_corte
                ns = ns_corte(sesion + "T21:31:25Z")
                for i in range(count):
                    mat, k = divmod(i, nstrikes)
                    strike = strike_min + k * paso
                    years = (date.fromisoformat(mats[mat]) - date.fromisoformat(sesion)).days / 365
                    vol = .8 if combo[0] == "^VIX" else .25
                    d1 = (math.log(spot / strike) + .5 * vol * vol * years) / (vol * math.sqrt(years))
                    d2 = d1 - vol * math.sqrt(years)
                    normal = lambda x: .5 * (1 + math.erf(x / math.sqrt(2)))
                    mid = spot * normal(d1) - strike * normal(d2)
                    if combo[2] == "put":
                        mid += strike - spot
                    mid = round(max(.01, mid), 4)
                    r = fila_fixture(**tags, date=sesion, captured_at=ns, _ts=ns, _recv_ts=ns + 100,
                                     capture_id=sesion + "-163125-5b2305", strike=strike, maturity=mats[mat],
                                     underlying_price=spot, bid=round(max(0, mid - .005), 4),
                                     ask=round(mid + .005, 4), last_price=mid, implied_vol=vol,
                                     _offset=i, volume=i % 150, open_interest=i % 2000,
                                     in_the_money=spot > strike if combo[2] == "call" else strike > spot)
                    if i % 251 == 0:
                        r.update(bid=0, ask=0, implied_vol=0, last_price=0)
                    linea = json_texto(r) + "\n"
                    cinco.write(linea)
                    if sesion == DIAS[0]:
                        uno.write(linea)
        for n, ruta in enumerate(rutas):
            files[n].append(dict(ruta=ruta.name, etiquetas=tags, filas=count * (1 if n == 0 else 5),
                                 sha256=sha256(ruta), peticiones=[]))
    for n, dump in enumerate(dumps):
        guardar_json(dump / "manifest.json", dict(schema=ESQUEMA, completo=True, contexto_completo=True,
            topic="market.options.chain", desde=DIAS[0], hasta=DIAS[0 if n == 0 else 4], consulta_desde=DIAS[0],
            catalogo=[dict(zip(TAGS, c)) for c in combos], ficheros=files[n], descartadas={}, avisos=[], semilla=0, fixture=forma))
        assert sum(f["filas"] for f in files[n]) == 432000 * (1 if n == 0 else 5)
    print("generado: " + json.dumps(forma), flush=True)


def hijo(base, n):
    import psutil
    import archivo_opciones as A
    inicio = time.perf_counter()
    with patch("socket.socket", side_effect=AssertionError("red prohibida")):
        destino, rep = A.archivar(base / f"volcado_{n}", "2026-11-19T06:00:00Z", f"sintetico_{n}_c2", raiz=base / "datasets")
    assert rep["filas_cruda"] == 432000 * n
    assert rep["memoria_flujo"]["max_filas_grupo"] == 10416
    assert rep["memoria_flujo"]["max_filas_sesion"] == 432000
    memoria = psutil.Process().memory_info()
    guardar_json(base / f"hijo_{n}.json", dict(tiempo_archivo_s=time.perf_counter() - inicio, dataset=str(destino),
        peak_working_set_bytes=memoria.peak_wset, peak_pagefile_bytes=memoria.peak_pagefile,
        dataset_sha256=rep["dataset_sha256"], filas_cruda=rep["filas_cruda"], filas_limpia=rep["filas_limpia"],
        memoria_flujo=rep["memoria_flujo"], validacion=rep["validacion"]["ok"], codigo_sha256=rep["codigo_sha256"],
        versiones=rep["versiones"], volcado_manifest_sha256=rep["volcado_manifest_sha256"]))


def medir(base, n):
    import psutil
    cmd = [sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--base", str(base), "--hijo", str(n)]
    inicio = time.perf_counter()
    pico_rss = pico_commit = 0
    limite_rss, limite_commit = ((3_000_000_000, 12_000_000_000) if n == 1 else (6_000_000_000, 12_000_000_000))
    detenido = False
    detalle_ruta = base / f"hijo_{n}.json"
    if detalle_ruta.exists():
        detalle_ruta.unlink()
    with (base / f"hijo_{n}.log").open("w", encoding="utf-8") as log:
        proceso = subprocess.Popen(cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
        monitor = psutil.Process(proceso.pid)
        while proceso.poll() is None:
            try:
                # Windows .venv/python.exe es un launcher: vigilar tambien
                # el interprete real, no solo los pocos MB del launcher.
                procesos = [monitor] + monitor.children(recursive=True)
                memorias = [p.memory_info() for p in procesos]
                pico_rss = max(pico_rss, sum(m.peak_wset for m in memorias))
                pico_commit = max(pico_commit, sum(m.peak_pagefile for m in memorias))
                if pico_rss > limite_rss or pico_commit > limite_commit:
                    for p in reversed(procesos):
                        p.kill()
                    detenido = True
                    break
            except psutil.NoSuchProcess:
                break
            time.sleep(.1)
        rc = proceso.wait()
    salida = dict(sesiones=n, filas_entrada=432000*n, subyacentes=509, semilla=0, orden=subprocess.list2cmdline(cmd),
                  tiempo_pared_s=time.perf_counter() - inicio, peak_working_set_bytes=pico_rss,
                  peak_pagefile_bytes=pico_commit, exit_code=rc, detenido_por_presupuesto=detenido)
    if (base / f"hijo_{n}.json").exists():
        detalle = json.loads((base / f"hijo_{n}.json").read_text(encoding="utf-8"))
        detalle["peak_working_set_bytes"] = max(pico_rss, detalle["peak_working_set_bytes"])
        detalle["peak_pagefile_bytes"] = max(pico_commit, detalle["peak_pagefile_bytes"])
        salida.update(detalle)
    print(json.dumps(salida), flush=True)
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--hijo", type=int, choices=(1, 5))
    ap.add_argument("--solo-medir", action="store_true")
    ap.add_argument("--sesiones", type=int, nargs="+", choices=(1, 5), default=[1, 5])
    ap.add_argument("--conservar", action="store_true")
    a = ap.parse_args()
    permitido = Path("E:/quantdesk-lab/tmp/TI-09-ARCH").resolve()
    base = a.base.resolve()
    if not base.is_relative_to(permitido) or base == permitido:
        raise ValueError("base fuera del temporal autorizado")
    if a.hijo:
        hijo(base, a.hijo)
        return
    if not a.solo_medir:
        base.mkdir(exist_ok=False)
        generar(base)
    resultado = [medir(base, n) for n in a.sesiones]
    if a.solo_medir and (base / "resultado.json").exists():
        anteriores = json.loads((base / "resultado.json").read_text(encoding="utf-8"))
        resultado += [r for r in anteriores if r["sesiones"] not in a.sesiones]
        resultado.sort(key=lambda r: r["sesiones"])
    guardar_json(base / "resultado.json", resultado)
    if not a.conservar:
        for nombre in ("volcado_1", "volcado_5", "datasets"):
            ruta = (base / nombre).resolve()
            assert ruta.is_relative_to(permitido) and ruta.parent == base
            if ruta.exists():
                shutil.rmtree(ruta)
    if any(r["exit_code"] or r["detenido_por_presupuesto"] for r in resultado):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
