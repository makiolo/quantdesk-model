"""Validacion de rango sin materializar tablas enteras en data_py.

Cada bloque se valida con el validador original (hash Rust, disponibilidad,
politica feed y parquet). Ademas se relee el parquet final, comprobando su
hash logico incremental, esquema, conteos, corte y orden GLOBAL, incluidas
las fronteras entre bloques/sesiones. No se rebaja ninguna regla del motor.
"""
from pathlib import Path
import hashlib
import json
import tempfile

import pyarrow.parquet as pq

from descarga_opciones import cargar_json
from exportar_market_history_lib import formato as F
from exportar_market_history_lib import validacion as V
from . import lector as L

FILAS_BLOQUE = 8192


def validar(dir_dataset, vendor_root, dataset_id, tablas, corte_ms, dataset_hash):
    manifiesto = cargar_json((Path(dir_dataset) / "manifest.json").read_text(encoding="utf-8"))
    # Las politicas por bloque no deben ocultar defectos del manifest final.
    if (not isinstance(manifiesto.get("description"), str)
            or manifiesto != F.manifest(dataset_id, manifiesto["description"], "America/New_York", tablas)
            or len({t["table_id"] for t in tablas}) != len(tablas)):
        raise ValueError("manifest final incompatible con OC-03/data_py")
    problemas, resumen = [], {}
    entradas = []
    cols = F.columnas_de("custom/v1")
    prefijos = [json.dumps(c["name"]) + ":" for c in cols]
    fmts = [F.FORMATEADORES[c["type"]] for c in cols]
    for t in tablas:
        ruta = Path(dir_dataset) / t["path"]
        pf = pq.ParquetFile(ruta)
        if not pf.schema_arrow.equals(F.esquema_arrow(t["schema"]), check_metadata=True):
            problemas.append(t["table_id"] + ": esquema distinto de data_py")
        h = hashlib.sha256(b"table:custom/v1\n")
        filas = bloques = 0
        anterior = None
        min_ts = max_ts = None
        # Respetar los limites de sesion que escribe cada row group.
        batches = (b for rg in range(pf.num_row_groups)
                   for b in pf.iter_batches(batch_size=FILAS_BLOQUE, row_groups=[rg]))
        for batch in batches:
            if len(set(batch.column("ts_ms").to_pylist())) > 1:
                raise ValueError("bloque de validacion mezcla sesiones")
            valores = [batch.column(c["name"]).to_pylist() for c in cols]
            for row in zip(*valores):
                if any(v is None for c, v in zip(cols, row) if not c["nullable"]):
                    raise ValueError("nulo en columna obligatoria")
                data = dict(zip((c["name"] for c in cols), row))
                key = data["ts_ms"], data["instrument"]
                if anterior is not None and key < anterior:
                    raise ValueError("orden global incorrecto entre bloques")
                anterior = key
                ts, disp = data["ts_ms"], data["available_at_ms"]
                if ts > corte_ms or disp is None or disp > corte_ms or disp < ts or data["revision"] != 0:
                    raise ValueError("disponibilidad, corte o revision invalidos")
                min_ts = ts if min_ts is None else min(min_ts, ts)
                max_ts = ts if max_ts is None else max(max_ts, ts)
                h.update(("{" + ",".join(p + f(v) for p, f, v in zip(prefijos, fmts, row)) + "}\n").encode("utf-8"))
            # La tabla del motor es SOLO este bloque; el rango no se concatena
            # en RAM. TemporaryDirectory garantiza que vendor no ve el rango.
            with tempfile.TemporaryDirectory(prefix="validacion_bloque_", dir=vendor_root) as tmp:
                destino = Path(tmp) / "bloque"
                frame = batch.to_pandas()
                m = F.escribir_dataset(str(destino), "bloque", "OC-03 validacion incremental", "America/New_York",
                                       [{"table_id": t["table_id"], "schema": t["schema"], "frame": frame}])
                del frame
                val = V.validar(str(destino), tmp, "bloque", m["tables"], corte_ms, L.hash_dataset(m["tables"]))
                if not val["ok"] or not val["politica"]["ok"]:
                    raise ValueError("data_py rechaza bloque: " + json.dumps(val["problemas"]))
            filas += len(batch)
            bloques += 1
            del valores, batch, val
        hash_ = "sha256:" + h.hexdigest()
        if filas != t["rows"] or hash_ != t["logical_hash"] or min_ts != t["ts_min_ms"] or max_ts != t["ts_max_ms"]:
            problemas.append(t["table_id"] + ": hash, filas o extremos no coinciden con manifest")
        entradas.append({**t, "logical_hash": hash_})
        resumen[t["table_id"]] = {"filas": filas, "bloques_motor": bloques, "hash_verified": hash_ == t["logical_hash"],
                                  "orden_global": True, "disponibilidad_y_corte": True}
    if L.hash_dataset(entradas) != dataset_hash:
        problemas.append("dataset SHA-256 distinto tras releer los parquet")
    return {"ok": not problemas, "problemas": problemas, "politica": {"ok": not problemas, "violaciones": []},
            "metodo": "parquet final y SHA-256 incrementales; data_py hash/disponibilidad/politica feed por bloque",
            "filas_maximas_bloque_motor": FILAS_BLOQUE, "max_sesiones_bloque_motor": 1,
            "tablas": resumen, "dataset_sha256_releido": L.hash_dataset(entradas)}
