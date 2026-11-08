"""Lectores de lo crudo: devuelven series (id, marcas ms UTC, valores float64) de Chronos, LOTSA y Binance."""
from __future__ import annotations

import functools
import glob
import io
import os
import re
import zipfile
from typing import NamedTuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

from . import common as C
from . import fuentes as F

OHLCV = ("open", "high", "low", "close", "volume", "quote_volume", "n_trades")
KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "n_trades",
              "taker_base", "taker_quote", "ignore"]
INTERVALO_MS = {"1d": 86_400_000, "1h": 3_600_000}


class Serie(NamedTuple):
    id: str
    ts: np.ndarray | None  # int64 ms UTC; None si no se pidio generarlas
    v: np.ndarray  # float64
    dom: str | None = None  # dominio por serie (M4: category)
    cols: dict | None = None  # columnas extra alineadas con ts (OHLCV)
    meta: dict | None = None  # duplicados / huecos detectados por el lector


_FREQ = {"T": "min", "MIN": "min", "H": "h", "S": "s", "L": "ms", "U": "us", "N": "ns", "D": "D", "B": "B", "W": "W",
         "M": "ME", "ME": "ME", "MS": "MS", "Q": "QE", "QE": "QE", "QS": "QS", "A": "YE", "Y": "YE", "YE": "YE",
         "AS": "YS", "YS": "YS"}


def norm_freq(f: str) -> str:
    """Alias de frecuencia de pandas <= 2.1 (H, T, M, Q, A) a los de pandas 3 (h, min, ME, QE, YE)."""
    m = re.fullmatch(r"(\d*)([A-Za-z]+)(-[A-Za-z]+)?", f.strip())
    if not m:
        raise ValueError(f"frecuencia ilegible: {f!r}")
    n, u, anc = m.groups()
    u2 = _FREQ.get(u) or _FREQ.get(u.upper())
    if u2 is None:
        raise ValueError(f"frecuencia desconocida: {f!r}")
    return f"{n}{u2}{anc or ''}"


@functools.lru_cache(maxsize=512)
def gen_ts_ms(inicio, n: int, freq: str) -> np.ndarray:
    """n marcas desde `inicio` (solo lectura, con cache: pandas tarda ms por serie en frecuencias ancladas como W-SUN y los
    corpus repiten inicio, longitud y frecuencia en cientos de miles de series). M/Q/A se etiquetan con el inicio del periodo
    (convencion de los corpus de Monash)."""
    f = norm_freq(freq)
    ini = pd.Timestamp(inicio)
    if ini.tzinfo is not None:
        ini = ini.tz_convert("UTC").tz_localize(None)
    if f[:2] in ("ME", "QE", "YE"):
        idx = pd.period_range(start=ini, periods=n, freq={"ME": "M", "QE": "Q", "YE": "Y"}[f[:2]] + f[2:]).start_time
    else:
        idx = pd.date_range(start=ini, periods=n, freq=f)
    out = idx.as_unit("ms").asi8.astype("int64")
    out.setflags(write=False)
    return out


def _a_f64(arr) -> np.ndarray:
    return pc.cast(arr, pa.float64()).to_numpy(zero_copy_only=False).astype("float64", copy=False)


def _a_ms(arr) -> np.ndarray:
    return arr.cast(pa.timestamp("ms", tz=None), safe=False).to_numpy(zero_copy_only=False).astype("datetime64[ms]").astype("int64")


def _trozos(col):
    """Parte una columna lista en (valores aplanados, offsets) respetando cortes de lote."""
    lens = pc.list_value_length(col).fill_null(0).to_numpy(zero_copy_only=False).astype("int64")
    offs = np.concatenate([[0], np.cumsum(lens)])
    return col.flatten(), offs


def leer_chronos(ruta: str, con_ts: bool = True, destino: str = "target", col_dom: str | None = None):
    pf = pq.ParquetFile(ruta)
    for lote in pf.iter_batches(batch_size=2000):
        ids = lote.column("id").to_pylist()
        tg, otg = _trozos(lote.column(destino))
        vals = _a_f64(tg)
        if con_ts:
            tsc, ots = _trozos(lote.column("timestamp"))
            tsms = _a_ms(tsc)
        doms = lote.column(col_dom).to_pylist() if col_dom else [None] * len(ids)
        for i, sid in enumerate(ids):
            a, b = otg[i], otg[i + 1]
            ts = None
            if con_ts:
                ts = tsms[ots[i]:ots[i + 1]]
            yield Serie(sid, ts, vals[a:b], doms[i])


def abrir_arrow(ruta: str) -> pa.Table:
    """Los .arrow del Hub son flujos IPC de la libreria datasets; se admite tambien el formato fichero."""
    with pa.memory_map(ruta) as fh:
        try:
            return pa.ipc.open_stream(fh).read_all()
        except pa.ArrowInvalid:
            pass
    with pa.memory_map(ruta) as fh:
        return pa.ipc.open_file(fh).read_all()


def leer_lotsa(ruta: str, con_ts: bool = True):
    t = abrir_arrow(ruta)
    ids = t.column("item_id").to_pylist()
    starts = t.column("start").to_pylist()
    freqs = t.column("freq").to_pylist()
    tg = t.column("target").combine_chunks()
    anidado = pa.types.is_list(tg.type.value_type) or pa.types.is_large_list(tg.type.value_type)
    for i, sid in enumerate(ids):
        fila = tg[i]
        if anidado:  # multivariante: una serie por dimension
            for k, sub in enumerate(fila.values if hasattr(fila, "values") else fila):
                v = _a_f64(sub.values)
                yield Serie(f"{sid}#{k}", gen_ts_ms(starts[i], len(v), freqs[i]) if con_ts else None, v)
        else:
            v = _a_f64(fila.values)
            yield Serie(sid, gen_ts_ms(starts[i], len(v), freqs[i]) if (con_ts and len(v)) else None, v)


def _csv_klines(datos: bytes) -> pa.Table:
    primera = datos[:40].lstrip()
    skip = 0 if primera[:1].isdigit() else 1  # versiones nuevas pueden traer cabecera
    tipos = {"open_time": pa.int64(), "close_time": pa.int64(), "n_trades": pa.int64(), "ignore": pa.string()}
    for c in ("open", "high", "low", "close", "volume", "quote_volume", "taker_base", "taker_quote"):
        tipos[c] = pa.float64()
    return pacsv.read_csv(io.BytesIO(datos), read_options=pacsv.ReadOptions(column_names=KLINE_COLS, skip_rows=skip),
                          convert_options=pacsv.ConvertOptions(column_types=tipos))


def leer_binance(entry: dict, con_ts: bool = True):
    inter = entry["intervalo"]
    paso = INTERVALO_MS[inter]
    for par in entry["pares"]:
        zips = sorted(glob.glob(f"{F.RAW_BINANCE}/data/spot/monthly/klines/{par}/{inter}/*.zip")) + \
            sorted(glob.glob(f"{F.RAW_BINANCE}/data/spot/daily/klines/{par}/{inter}/*.zip"))
        if not zips:
            continue
        tablas = []
        for z in zips:
            with zipfile.ZipFile(z) as zf:
                nombre = [n for n in zf.namelist() if n.endswith(".csv")][0]
                tablas.append(_csv_klines(zf.read(nombre)))
        t = pa.concat_tables(tablas)
        ot = t.column("open_time").to_numpy()
        ot = np.where(ot > 10**14, ot // 1000, ot).astype("int64")  # desde 2025 el spot publica microsegundos
        orden = np.argsort(ot, kind="stable")
        ot = ot[orden]
        _, primeros = np.unique(ot, return_index=True)  # primera aparicion de cada marca
        dup = int(len(ot) - len(primeros))
        sel = orden[primeros]
        ts = ot[primeros]
        huecos = int(np.count_nonzero(np.diff(ts) != paso)) if len(ts) > 1 else 0
        cols = {n: t.column(src).to_numpy()[sel] for n, src in
                zip(OHLCV, ("open", "high", "low", "close", "volume", "quote_volume", "n_trades"))}
        yield Serie(f"{par}-{inter}", ts, cols["close"].astype("float64"), None,
                    {k: (v.astype("float64") if k != "n_trades" else v.astype("int64")) for k, v in cols.items()},
                    {"duplicados": dup, "huecos": huecos, "zips": len(zips)})


def series(entry: dict, con_ts: bool = True):
    """Iterador de series de un dataset del registro, leyendo lo crudo ya descargado."""
    if entry["formato"] == "chronos":
        yield from leer_chronos(f"{F.RAW_HF}/{entry['repo']}/{entry['archivos'][0]}", con_ts,
                                col_dom=entry.get("dominio_col"))
    elif entry["formato"] == "lotsa":
        yield from leer_lotsa(f"{F.RAW_HF}/{entry['repo']}/{entry['archivos'][0]}", con_ts)
    elif entry["formato"] == "binance":
        yield from leer_binance(entry, con_ts)
    else:
        raise ValueError(entry["formato"])


def rutas_crudo(entry: dict) -> list:
    """Claves del raw_manifest que alimentan el dataset."""
    if entry["formato"] in ("chronos", "lotsa"):
        return [f"hf/{entry['repo']}/{r}" for r in entry["archivos"] + entry["extras"]]
    inter = entry["intervalo"]
    out = []
    for par in entry["pares"]:
        for tipo in ("monthly", "daily"):
            out += [os.path.relpath(p, C.PUBLIC).replace(os.sep, "/") for p in
                    glob.glob(f"{F.RAW_BINANCE}/data/spot/{tipo}/klines/{par}/{inter}/*.zip")]
    return sorted(out)
