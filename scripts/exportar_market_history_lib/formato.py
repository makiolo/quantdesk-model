"""Escritura de un dataset `engine.market-history/v1`: columnas desde data_py, hash logico, parquet y manifest.

El hash logico es el de `quant-data` (`TableData::logical_hash`): SHA-256 de `table:<esquema>\\n` seguido de cada fila como JSON
compacto (claves en el orden de columna, `null` para nulos) terminada en `\\n`. Aqui se calcula en Python, de forma independiente,
y despues `data_py.dataset_describe_json(verify_hashes=True)` lo recalcula en Rust y lo compara: si el formato de un float
difiriera del de `serde_json` (ryu) la validacion lo detectaria.
"""
from __future__ import annotations

import hashlib
import json
import math
import os

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

TIPOS_ARROW = {"Utf8": pa.string(), "Int64": pa.int64(), "Int32": pa.int32(), "Float64": pa.float64()}
CLAVE_TABLA = "engine.table"  # metadato del esquema Parquet que declara la tabla (rust/crates/quant-data/src/schema.rs)
FILAS_POR_GRUPO = 131072
COMPRESION = "snappy"  # quant-data solo lee UNCOMPRESSED y SNAPPY


def columnas_de(tabla: str) -> list[dict]:
    """Columnas (`name`, `type`, `nullable`) de una tabla versionada, tal como las define `data_py.table_schemas_json()`."""
    import data_py

    doc = json.loads(data_py.table_schemas_json())
    if not doc.get("ok"):
        raise RuntimeError(f"data_py.table_schemas_json fallo: {doc}")
    for t in doc["tables"]:
        if t["table"] == tabla:
            return t["columns"]
    raise KeyError(f"data_py no conoce la tabla {tabla!r}")


def esquema_arrow(tabla: str) -> pa.Schema:
    campos = [pa.field(c["name"], TIPOS_ARROW[c["type"]], nullable=c["nullable"]) for c in columnas_de(tabla)]
    return pa.schema(campos, metadata={CLAVE_TABLA: tabla})


def _ryu(r: str) -> str:
    """Reescribe el `repr` de un float con el formato de serde_json (`1e-7`, `1e+16`, `100.0`; nunca `1e-07`). Los umbrales
    (decimal entre 1e-5 y 1e16, cientifico fuera) son los de ryu; el selftest los comprueba contra el motor."""
    neg = r.startswith("-")
    if neg:
        r = r[1:]
    mant, _, exp = r.partition("e")
    ent, _, frac = mant.partition(".")
    digitos = ent + frac
    punto = len(ent) + (int(exp) if exp else 0)  # el punto decimal queda tras `punto` digitos
    sin_ceros = digitos.lstrip("0")
    punto -= len(digitos) - len(sin_ceros)
    digitos = sin_ceros.rstrip("0")
    if not digitos:
        return "-0.0" if neg else "0.0"
    n, k = len(digitos), punto - len(digitos)
    if k >= 0 and punto <= 16:
        out = digitos + "0" * k + ".0"
    elif 0 < punto <= 16:
        out = digitos[:punto] + "." + digitos[punto:]
    elif -5 < punto <= 0:
        out = "0." + "0" * (-punto) + digitos
    else:  # notacion cientifica; serde_json escribe el exponente con signo `+` si es positivo (1e+16) y sin ceros (1e-7)
        e = punto - 1
        mantisa = digitos if n == 1 else f"{digitos[0]}.{digitos[1:]}"
        out = f"{mantisa}e{'+' if e >= 0 else ''}{e}"
    return "-" + out if neg else out


def fmt_f64(x: float) -> str:
    if not math.isfinite(x):
        raise ValueError(f"un float no finito no tiene representacion en el hash logico: {x}")
    r = repr(float(x))
    return r if "e" not in r else _ryu(r)


def _fmt_utf8(v) -> str:
    return "null" if v is None else json.dumps(v, ensure_ascii=False)


def _fmt_int(v) -> str:
    return "null" if v is None else str(int(v))


def _fmt_float(v) -> str:
    return "null" if v is None else fmt_f64(v)


FORMATEADORES = {"Utf8": _fmt_utf8, "Int64": _fmt_int, "Int32": _fmt_int, "Float64": _fmt_float}


def columna_python(serie: pd.Series) -> list:
    """Valores de la columna como objetos Python, con None en vez de NA/NaN de pandas."""
    if serie.dtype == object or str(serie.dtype).startswith("string"):
        return [None if (v is None or v is pd.NA) else v for v in serie.tolist()]
    return serie.astype(object).where(serie.notna(), None).tolist()


def hash_logico(tabla: str, df: pd.DataFrame) -> str:
    """`sha256:` del contenido logico de la tabla (filas en el orden del DataFrame)."""
    cols = columnas_de(tabla)
    faltan = [c["name"] for c in cols if c["name"] not in df.columns]
    if faltan:
        raise KeyError(f"{tabla}: faltan columnas {faltan}")
    fmts = [FORMATEADORES[c["type"]] for c in cols]
    prefijos = [json.dumps(c["name"]) + ":" for c in cols]
    datos = [columna_python(df[c["name"]]) for c in cols]
    h = hashlib.sha256()
    h.update(f"table:{tabla}\n".encode())
    for fila in zip(*datos):
        h.update(("{" + ",".join(p + f(v) for p, f, v in zip(prefijos, fmts, fila)) + "}\n").encode("utf-8"))
    return "sha256:" + h.hexdigest()


def tabla_arrow(tabla: str, df: pd.DataFrame) -> pa.Table:
    esq = esquema_arrow(tabla)
    arrays = []
    for campo in esq:
        serie = df[campo.name]
        if pa.types.is_string(campo.type):
            arrays.append(pa.array(columna_python(serie), type=campo.type))
        else:
            arrays.append(pa.array(serie, type=campo.type, from_pandas=True))
    return pa.Table.from_arrays(arrays, schema=esq)


def escribir_parquet(tabla: str, df: pd.DataFrame, ruta: str) -> None:
    pq.write_table(tabla_arrow(tabla, df), ruta, compression=COMPRESION, use_dictionary=False, write_statistics=True,
                   row_group_size=FILAS_POR_GRUPO)


def sha256_fichero(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def escribir_json(ruta: str, doc: dict) -> None:
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def entrada_manifest(table_id: str, esquema: str, ruta: str, df: pd.DataFrame, hash_: str) -> dict:
    ts = df["ts_ms"]
    vacia = len(df) == 0
    return {"table_id": table_id, "schema": esquema, "path": ruta, "rows": int(len(df)),
            "ts_min_ms": None if vacia else int(ts.min()), "ts_max_ms": None if vacia else int(ts.max()),
            "logical_hash": hash_}


def manifest(dataset_id: str, descripcion: str, zona: str, tablas: list[dict], default_lag_ms: int | None = None) -> dict:
    """Manifest en el orden de campos de `MarketHistoryManifest`. `default_lag_ms` es null salvo en un dataset con un proxy de
    disponibilidad declarado (`--disponibilidad-ohlcv cierre`, valor 0): nunca se inventa otro."""
    return {"schema": "engine.market-history", "version": "v1", "dataset_id": dataset_id, "description": descripcion,
            "time": {"zone": zona}, "sessions": [], "default_lag_ms": default_lag_ms, "tables": tablas, "symbol_history": []}


def escribir_dataset(directorio: str, dataset_id: str, descripcion: str, zona: str, tablas: list[dict],
                     default_lag_ms: int | None = None) -> dict:
    """Escribe parquet y manifest de `tablas` (`table_id`, `schema`, `frame`) en `directorio`; devuelve el manifest."""
    os.makedirs(directorio, exist_ok=True)
    entradas = []
    for t in tablas:
        ruta = t["table_id"] + ".parquet"
        escribir_parquet(t["schema"], t["frame"], os.path.join(directorio, ruta))
        entradas.append(entrada_manifest(t["table_id"], t["schema"], ruta, t["frame"], hash_logico(t["schema"], t["frame"])))
    m = manifest(dataset_id, descripcion, zona, entradas, default_lag_ms)
    escribir_json(os.path.join(directorio, "manifest.json"), m)
    return m


def vacia(tabla: str) -> pd.DataFrame:
    """DataFrame vacio con las columnas de la tabla (para tablas sin ninguna fila tras la limpieza)."""
    return pd.DataFrame({c["name"]: pd.Series([], dtype=_dtype(c["type"])) for c in columnas_de(tabla)})


def _dtype(tipo: str):
    return {"Utf8": object, "Int64": "Int64", "Int32": "int32", "Float64": "float64"}[tipo]
