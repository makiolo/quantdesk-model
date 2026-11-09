"""Lectura del dataset congelado (engine.market-history/v1), disponibilidad y cortes causales del walk-forward.

Garantia de no look-ahead (una sola puerta, `cortar`):
- disponibilidad de cada fila = `available_at_ms` si no es nulo; si es nulo, `ts_ms + interval_ms + default_lag_ms`
  del manifest (el mecanismo del motor; en `lago_cierre_c20261101` es el proxy `default_lag_ms = 0`). Una fila sin
  ninguna de las dos no es consumible y la carga falla (nunca se inventa una disponibilidad).
- en el origen `t` (ms UTC) el contexto que recibe un modelo son SOLO las filas con disponibilidad <= t, ordenadas por
  `ts_ms`, y de ellas las ultimas W. La funcion devuelve una copia de esos precios; el modelo no recibe el
  DataFrame ni ningun indice al resto de la serie.
- el objetivo (rendimientos y varianza realizada a h barras) se calcula aparte con las barras de `ts_ms` posterior a
  la ultima barra visible, y nunca se pasa al modelo.
Una fila con `ts_ms` anterior a la ultima visible pero publicada despues de `t` (dato tardio) queda fuera del
contexto; el selftest lo comprueba con un valor extremo que no debe alterar ninguna prediccion.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np

DIA_MS = 86_400_000


@dataclass(frozen=True)
class Serie:
    instrument: str
    ts_ms: np.ndarray  # int64, creciente
    disp_ms: np.ndarray  # int64, disponibilidad de cada fila
    close: np.ndarray  # float64 > 0


@dataclass(frozen=True)
class Corte:
    origen_ms: int
    k: int  # indice (en la serie ordenada por ts) de la ultima barra visible
    ts_ultima_ms: int
    precios: np.ndarray  # contexto: ultimos W cierres visibles (copia)
    y: np.ndarray  # y[h-1] = ln(C_{k+h} / C_k), h = 1..Hmax
    rv: np.ndarray  # rv[h-1] = suma de r_{k+i}^2, i = 1..h


def disponibilidad(ts_ms, interval_ms, available_at_ms, default_lag_ms):
    """Vector de disponibilidad (ms). available_at_ms puede traer NaN/None (nulo)."""
    ts = np.asarray(ts_ms, dtype=np.int64)
    itv = np.asarray(interval_ms, dtype=np.int64)
    av = np.asarray(available_at_ms, dtype=float)
    nulo = ~np.isfinite(av)
    out = np.where(nulo, 0, np.nan_to_num(av, nan=0.0)).astype(np.int64)
    if nulo.any():
        if default_lag_ms is None:
            raise ValueError(f"{int(nulo.sum())} filas sin available_at_ms y el manifest no declara default_lag_ms")
        out[nulo] = ts[nulo] + itv[nulo] + int(default_lag_ms)
    return out


def series_desde_tabla(df, default_lag_ms) -> dict[str, Serie]:
    """df con columnas instrument, ts_ms, interval_ms, close, available_at_ms. Devuelve una Serie por instrumento."""
    disp = disponibilidad(df["ts_ms"], df["interval_ms"], df["available_at_ms"], default_lag_ms)
    df = df.assign(_disp=disp)
    out = {}
    for ins in sorted(df["instrument"].unique()):
        d = df[df["instrument"] == ins].sort_values("ts_ms", kind="mergesort")
        ts = d["ts_ms"].to_numpy(np.int64)
        if np.any(np.diff(ts) <= 0):
            raise ValueError(f"{ins}: ts_ms repetido o desordenado")
        c = d["close"].to_numpy(np.float64)
        if not np.all(np.isfinite(c)) or np.any(c <= 0):
            raise ValueError(f"{ins}: close no positivo o no finito")
        out[ins] = Serie(ins, ts, d["_disp"].to_numpy(np.int64), c)
    return out


def cortar(s: Serie, origen_ms: int, ventana: int, hmax: int):
    """Corte causal en el origen. None si no hay W barras visibles o faltan Hmax barras posteriores."""
    vis = np.flatnonzero(s.disp_ms <= origen_ms)
    if len(vis) < ventana:
        return None
    k = int(vis[-1])
    if k + hmax >= len(s.close):
        return None
    precios = s.close[vis[-ventana:]].copy()
    precios.flags.writeable = False
    lc = np.log(s.close[k:k + hmax + 1])
    y = lc[1:] - lc[0]
    rv = np.cumsum(np.diff(lc) ** 2)
    return Corte(int(origen_ms), k, int(s.ts_ms[k]), precios, y, rv)


def rejilla_origenes(inicio: str, fin: str, paso_dias: int) -> list[int]:
    """00:00 UTC de cada paso_dias dias desde inicio hasta fin (ambos incluidos), en ms."""
    a = datetime.strptime(inicio, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    b = datetime.strptime(fin, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    t0, t1 = int(a.timestamp() * 1000), int(b.timestamp() * 1000)
    if t1 < t0 or paso_dias < 1:
        raise ValueError("rejilla de origenes vacia")
    return list(range(t0, t1 + 1, paso_dias * DIA_MS))


def cortes_de_serie(s: Serie, origenes, ventana: int, hmax: int):
    """Cortes validos de una serie en la rejilla. Un origen en el que no ha llegado ninguna barra nueva desde el
    origen anterior (fin de semana del FX) se omite: repetiria la misma informacion. Devuelve (cortes, omitidos)."""
    cortes, omit = [], {"sin_ventana": 0, "sin_objetivo": 0, "sin_barra_nueva": 0}
    k_prev = None
    for t in origenes:
        c = cortar(s, t, ventana, hmax)
        if c is None:
            vis = int(np.count_nonzero(s.disp_ms <= t))
            omit["sin_ventana" if vis < ventana else "sin_objetivo"] += 1
            continue
        if c.k == k_prev:
            omit["sin_barra_nueva"] += 1
            continue
        k_prev = c.k
        cortes.append(c)
    return cortes, omit


def cargar_dataset(directorio: str, tabla: str):
    """Lee la tabla OHLCV del dataset con pyarrow y describe el dataset con data_py (hash verificado)."""
    import data_py
    import pyarrow.parquet as pq

    desc = json.loads(data_py.dataset_describe_json(directorio, True))
    if not desc.get("ok"):
        raise ValueError(f"data_py.dataset_describe_json fallo: {desc}")
    d = desc["description"]
    t = [x for x in d["tables"] if x["table_id"] == tabla]
    if not t or not t[0].get("hash_verified"):
        raise ValueError(f"tabla {tabla} ausente o hash no verificado en {directorio}")
    with open(os.path.join(directorio, "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    lag = man.get("default_lag_ms")
    df = pq.read_table(os.path.join(directorio, t[0]["path"]),
                       columns=["instrument", "ts_ms", "interval_ms", "close", "available_at_ms"]).to_pandas()
    n_nulos = int(df["available_at_ms"].isna().sum())
    meta = {
        "dataset_id": d["dataset_id"],
        "dataset_hash": d["dataset_hash"],
        "tabla": tabla,
        "logical_hash": t[0]["logical_hash"],
        "filas": int(t[0]["rows"]),
        "default_lag_ms": lag,
        "filas_available_at_nulo": n_nulos,
        "proxy": bool(n_nulos > 0),
        "intervalos_ms": sorted(int(x) for x in df["interval_ms"].unique()),
    }
    return series_desde_tabla(df, lag), meta


def fecha(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def finito(x) -> bool:
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)
