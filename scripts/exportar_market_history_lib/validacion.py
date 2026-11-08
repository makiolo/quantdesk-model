"""Validacion de un dataset escrito: `data_py` (quant-data, el motor) y comprobaciones propias sobre el parquet releido.

Llamadas exactas a data_py (rueda `quantdesk 69fdb39d`):
- `dataset_describe_json(dir, True)`: abre el manifest, relee cada tabla, recalcula filas y hash logico (`hash_verified`).
- `availability_report_json(dir, table_id, "{}", "reject")`: modo de disponibilidad por fila (declared/defaulted/undeclared)
  y violaciones DPOL-AVL-002 (`available_at` anterior al cierre); con "reject" cualquier `revision != 0` es un error.
- `verify_policy_json({...})` con `mode = "feed"`: construye el feed de eventos del dataset y comprueba la politica
  (`require_available_at`, zona declarada) y el look-ahead de los eventos materializados (DPOL-AVL-001/002/003, DPOL-TZ-001).
"""
from __future__ import annotations

import json
import os

import pyarrow.parquet as pq

from .formato import CLAVE_TABLA, TIPOS_ARROW, columnas_de

POLITICA = {"schema": "engine.data-policy", "version": "v1", "availability": {"require_available_at": True},
            "timezone": {"require_declared": True}}


def _llamar(fn, *args) -> dict:
    doc = json.loads(fn(*args))
    if not doc.get("ok", False) and "error" in doc:
        raise RuntimeError(f"{fn.__name__} fallo: {doc['error']}")
    return doc


def comprobar_parquet(dir_dataset: str, tabla: dict, corte_ms: int) -> dict:
    """Relee el parquet escrito: esquema exacto de data_py, sin nulos en columnas obligatorias, orden y reglas del corte."""
    ruta = os.path.join(dir_dataset, tabla["table_id"] + ".parquet")
    pf = pq.ParquetFile(ruta)
    esq = pf.schema_arrow
    esperadas = columnas_de(tabla["schema"])
    problemas = []
    if [f.name for f in esq] != [c["name"] for c in esperadas]:
        problemas.append(f"columnas {[f.name for f in esq]} != {[c['name'] for c in esperadas]}")
    for f, c in zip(esq, esperadas):
        if f.type != TIPOS_ARROW[c["type"]]:
            problemas.append(f"{f.name}: tipo {f.type} != {c['type']}")
    meta = (esq.metadata or {}).get(CLAVE_TABLA.encode())
    if meta != tabla["schema"].encode():
        problemas.append(f"metadato {CLAVE_TABLA} = {meta!r}")
    df = pf.read().to_pandas()
    for c in esperadas:
        if not c["nullable"] and df[c["name"]].isna().any():
            problemas.append(f"nulos en la columna obligatoria {c['name']}")
    res = {"filas": int(len(df)), "grupos": pf.num_row_groups, "codec": pf.metadata.row_group(0).column(0).compression
           if pf.num_row_groups else None}
    if len(df) > 1:
        ts, inst = df["ts_ms"].to_numpy(), df["instrument"].to_numpy(dtype=object)
        if not ((ts[1:] > ts[:-1]) | ((ts[1:] == ts[:-1]) & (inst[1:] >= inst[:-1]))).all():
            problemas.append("las filas no estan ordenadas por (ts_ms, instrument)")
    if len(df):
        disp = df["available_at_ms"]
        cierre = df["ts_ms"] + (df["interval_ms"] if "interval_ms" in df.columns else 0)
        res["max_cierre_ms"] = int(cierre.max())
        if (cierre > corte_ms).any():
            problemas.append(f"{int((cierre > corte_ms).sum())} filas con cierre posterior al corte")
        res["con_disponibilidad"] = int(disp.notna().sum())
        if disp.notna().any():
            res["max_available_at_ms"] = int(disp.max())
            if (disp > corte_ms).any():
                problemas.append(f"{int((disp > corte_ms).sum())} filas con available_at_ms posterior al corte")
            if (disp < cierre).any():
                problemas.append(f"{int((disp < cierre).sum())} filas con available_at_ms anterior al cierre")
        if (df["revision"] != 0).any():
            problemas.append("hay filas con revision != 0")
    res["problemas"] = problemas
    return res


def validar(dir_dataset: str, vendor_root: str, dataset_id: str, tablas: list, corte_ms: int, dataset_hash: str | None = None) -> dict:
    """Ejecuta las llamadas de data_py y las comprobaciones propias; devuelve un resumen serializable.
    `ok` exige: describe ok con hashes verificados, cero violaciones de disponibilidad en las tablas que la declaran,
    `dataset_hash` propio igual al que calcula `vendor_describe_json` y ninguna incidencia propia. Una tabla sin disponibilidad
    declarada no falla la exportacion pero se marca `consumible_causal` = false (y la politica `require_available_at` da
    DPOL-AVL-001 por ella)."""
    import data_py

    out: dict = {"llamadas": {
        "describe": f'data_py.dataset_describe_json("{dir_dataset}", True)',
        "disponibilidad": 'data_py.availability_report_json(dir, table_id, "{}", "reject")',
        "politica": f"data_py.verify_policy_json(mode=feed, policy={json.dumps(POLITICA, sort_keys=True)}, "
                    f'vendor_root="{vendor_root}", dataset_id="{dataset_id}", revision_policy="reject")'}}
    d = _llamar(data_py.dataset_describe_json, dir_dataset, True)["description"]
    out["describe"] = {"dataset_id": d.get("dataset_id"), "tablas": [
        {k: t.get(k) for k in ("table_id", "schema", "rows", "rows_declared", "row_groups", "ts_min_ms", "ts_max_ms",
                               "file_size_bytes", "codecs", "logical_hash", "hash_verified")} for t in d["tables"]]}
    problemas = []
    for t in out["describe"]["tablas"]:
        if not t["hash_verified"] or t["rows"] != t["rows_declared"]:
            problemas.append(f"{t['table_id']}: hash o filas no verificados por data_py")
    vendor = _llamar(data_py.vendor_describe_json, vendor_root)
    del_motor = next((x["dataset_hash"] for x in vendor["datasets"] if x["dataset_id"] == dataset_id), None)
    out["llamadas"]["vendor"] = f'data_py.vendor_describe_json("{vendor_root}")'
    out["vendor"] = {"dataset_hash_del_motor": del_motor, "issues": vendor.get("issues", [])}
    if del_motor is None or (dataset_hash is not None and del_motor != dataset_hash):
        problemas.append(f"dataset_hash propio {dataset_hash} != el del motor {del_motor}")
    out["disponibilidad"], out["parquet"] = {}, {}
    for t in tablas:
        ar = _llamar(data_py.availability_report_json, dir_dataset, t["table_id"], "{}", "reject")
        rep = ar["report"]
        resumen = {k: rep[k] for k in ("rows", "declared", "defaulted", "undeclared")}
        resumen["violaciones_dpol_avl_002"] = len(rep["violations"])
        resumen["ejemplos_de_violacion"] = rep["violations"][:3]
        resumen["revisiones_conservadas"] = len(ar["revisions"]["kept"])
        resumen["revisiones_descartadas"] = len(ar["revisions"]["dropped"])
        resumen["consumible_causal"] = bool(rep["rows"] and rep["declared"] == rep["rows"] and not rep["violations"])
        out["disponibilidad"][t["table_id"]] = resumen
        if rep["violations"]:
            problemas.append(f"{t['table_id']}: {len(rep['violations'])} violaciones DPOL-AVL-002")
        pq_res = comprobar_parquet(dir_dataset, t, corte_ms)
        out["parquet"][t["table_id"]] = pq_res
        problemas += [f"{t['table_id']}: {p}" for p in pq_res["problemas"]]
    req = {"policy": POLITICA, "vendor_root": vendor_root, "dataset_id": dataset_id, "mode": "feed",
           "revision_policy": "reject"}
    pol = _llamar(data_py.verify_policy_json, json.dumps(req))["report"]
    out["politica"] = {"ok": pol["ok"], "descriptor_hash": pol["descriptor_hash"], "report_hash": pol["report_hash"],
                       "violaciones": [{"code": v["code"], "severity": v["severity"], "instrument": v.get("instrument"),
                                        "detail": v["detail"][:200]} for v in pol["violations"]]}
    sin_disp = [k for k, v in out["disponibilidad"].items() if not v["consumible_causal"]]
    out["tablas_no_consumibles_causalmente"] = sin_disp
    codigos = {v["code"] for v in out["politica"]["violaciones"] if v["severity"] == "error"}
    inesperados = codigos - ({"DPOL-AVL-001"} if sin_disp else set())
    if inesperados:
        problemas.append(f"la politica de datos da errores {sorted(inesperados)}")
    out["lookahead"] = {
        "violaciones": [v for v in out["politica"]["violaciones"] if v["code"] in ("DPOL-AVL-002", "DPOL-AVL-003")],
        "violaciones_por_fila": sum(v["violaciones_dpol_avl_002"] for v in out["disponibilidad"].values())}
    out["problemas"] = problemas
    out["ok"] = not problemas
    return out
