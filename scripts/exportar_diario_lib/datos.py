"""Corte y versiones antes de la limpieza compartida; nunca se reparan precios."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import pandas as pd

from descarga_lago import ns_rfc3339
from exportar_market_history_lib.limpieza import limpiar_ohlcv, nuevo_contador
from extractor_mt5_lib.calendarios import es_festivo
from . import politica as P

DIA = 86_400_000
NUMERICAS = ("open", "high", "low", "close", "volume")


def ns(value):
    # latest usa ns enteros; objects devuelve RFC3339 (no floats ni marcas sin zona).
    return value if type(value) is int else ns_rfc3339(value)


def ms_fecha(d):
    return int(datetime.combine(d, datetime.min.time(), timezone.utc).timestamp()) * 1000


def numero(v):
    try:
        return float(v) if not isinstance(v, bool) else float("nan")
    except (ValueError, TypeError, OverflowError):
        return float("nan")


def preparar(rows, head, desde, sesion):
    corte_ns = ms_fecha(sesion + timedelta(days=1)) * 10**6
    inicio_ns = ms_fecha(desde) * 10**6
    contador = Counter()
    versiones = defaultdict(list)
    for row in rows:
        contador["leidas"] += 1
        cycle, offset = row.get("_cycle"), row.get("_offset")
        if type(cycle) is not int or type(offset) is not int or cycle < 0 or offset < 0:
            contador["provisionales"] += 1
            continue
        ts, recv = ns(row.get("_ts")), ns(row.get("_recv_ts"))
        if ts is None or recv is None or not isinstance(row.get("_batch_id"), str) or not row["_batch_id"]:
            contador["marcas_invalidas"] += 1
            continue
        if cycle > head or recv >= corte_ns:
            contador["fuera_corte"] += 1
            continue
        if not inicio_ns <= ts < corte_ns:
            contador["fuera_ventana"] += 1
            continue
        if ts % (DIA * 10**6):
            raise ValueError("vela 1d fuera de la rejilla UTC 00:00")
        key = (row["symbol"], row["source"], ts)
        versiones[key].append((recv, row["_batch_id"], row))
    elegidas = []
    conflictos = set()
    for key, group in sorted(versiones.items()):
        mayor = max((r, b) for r, b, _ in group)
        candidatas = [row for r, b, row in group if (r, b) == mayor]
        contador["versiones_anteriores"] += len(group) - len(candidatas)
        for row in candidatas:
            info = P.MAPA[row["symbol"]]
            ausente = row.get("volume") is None
            values = tuple(numero(row.get(k)) if k != "volume" or not ausente else 0.0 for k in NUMERICAS)
            elegidas.append({"instrument": info["symbol"], "ts_ms": key[2] // 10**6, "interval_ms": DIA,
                             **dict(zip(NUMERICAS, values)), "source": key[1],
                             "available_at_ms": max((mayor[0] + 999_999) // 10**6, key[2] // 10**6 + DIA),
                             "symbol_original": key[0], "volumen_ausente": ausente})
    unicas = []
    grupos = defaultdict(list)
    for row in elegidas:
        grupos[row["instrument"], row["ts_ms"]].append(row)
    for key, group in sorted(grupos.items()):
        valores = {tuple(r[k] for k in NUMERICAS) for r in group}
        if len(valores) > 1:
            contador["cuarentena"] += len(group)
            conflictos.add(key)
            continue
        contador["duplicados_iguales"] += len(group) - 1
        # El orden de alias, no el orden de entrega HTTP, resuelve duplicados iguales.
        unicas.append(sorted(group, key=lambda r: r["symbol_original"])[0])
    columnas = ["instrument", "ts_ms", "interval_ms", *NUMERICAS, "source", "available_at_ms", "orden"]
    frame = pd.DataFrame([{**r, "orden": i} for i, r in enumerate(unicas)], columns=columnas)
    frame["available_at_ms"] = pd.array(frame["available_at_ms"], dtype="Int64")
    for k in NUMERICAS:
        frame[k] = frame[k].astype("float64")
    for k in ("ts_ms", "interval_ms", "orden"):
        frame[k] = frame[k].astype("int64")
    c = nuevo_contador(len(frame))
    limpio = limpiar_ohlcv(frame, corte_ns // 10**6, "identicos", c)
    claves_finales = set(zip(limpio.instrument, limpio.ts_ms))
    procedencia = [r for r in unicas if (r["instrument"], r["ts_ms"]) in claves_finales]
    sources = {r["instrument"]: r["source"] for r in procedencia}
    desktop = limpio.rename(columns={"instrument": "symbol"})[["symbol", "ts_ms", *NUMERICAS]]
    desktop = desktop.astype({"symbol": object, "ts_ms": "int64", **{k: "float64" for k in NUMERICAS}})
    desktop = desktop.sort_values(["symbol", "ts_ms"], kind="mergesort").reset_index(drop=True)
    informe = {"corte_y_versiones": dict(sorted(contador.items())), "limpieza": c,
               "cuarentena": [{"symbol": s, "ts_ms": ts} for s, ts in sorted(conflictos)],
               "volumen_ausente": [{"symbol": r["instrument"], "ts_ms": r["ts_ms"]}
                                   for r in procedencia if r["volumen_ausente"]],
               "procedencia": [{"symbol": r["instrument"], "symbol_original": r["symbol_original"],
                                "source": r["source"], "ts_ms": r["ts_ms"]} for r in procedencia]}
    return desktop, limpio, sources, informe


def cobertura(frame, desde, sesion):
    resultado = []
    observables = {i["symbol"]: i for i in P.MAPA.values()}
    for symbol, info in sorted(observables.items()):
        g = frame[frame.symbol == symbol]
        dias = {datetime.fromtimestamp(int(t) // 1000, timezone.utc).date() for t in g.ts_ms}
        first, last = (min(dias), max(dias)) if dias else (None, None)
        ausencias, esperadas = [], []
        d = first or sesion
        while d <= sesion:
            if d.weekday() < 5 and d not in dias:
                festivo = P.festivo_fx(d) if info["calendar"] == "FX" else es_festivo(info["calendar"], d)
                (esperadas if festivo else ausencias).append(d.isoformat())
            d += timedelta(days=1)
        resultado.append({"symbol": symbol, "first": first.isoformat() if first else None,
                          "last": last.isoformat() if last else None, "rows": len(g), "calendar": info["calendar"],
                          "gaps": ausencias, "expected_absences": esperadas,
                          "available_from": first.isoformat() if first else None, "requested_from": desde.isoformat()})
    return resultado
