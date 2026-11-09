"""Bucle walk-forward, persistencia de predicciones, metricas agregadas y comparacion entre corridas."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time

import numpy as np

from . import datos, metricas

MOTOR = "quantdesk 69fdb39d"
MOTOR_COMMIT = "69fdb39d0b67969dbdafa77f5da656511342f175"
HORIZONTES = (1, 5, 20)
HMAX = max(HORIZONTES)
SEMILLA = 20261101
QCOLS = [f"q{i:02d}" for i in range(len(metricas.NIVELES))]

# Configuracion fija por dataset (documentada en el informe). Los recortes frente a "todos los origenes diarios"
# salen de la medida de CPU por origen (ver informe, presupuesto de CPU).
PRESETS = {
    "lago_cierre_c20261101": {
        "tabla": "lago_ohlcv_1d", "ventana": 250, "inicio": "2025-10-20", "fin": "2026-10-03", "paso_dias": 1,
    },
    "binance_c20261101": {
        "tabla": "binance_ohlcv_1d", "ventana": 1000, "inicio": "2023-11-01", "fin": "2026-10-12", "paso_dias": 3,
    },
}


def caminos_por_modelo(modelos):
    return {m.nombre: getattr(m, "s", getattr(m, "muestras", None)) for m in modelos}


def semilla_par(semilla: int, instrument: str, origen_ms: int, modelo: str) -> int:
    h = hashlib.sha256(f"{semilla}|{instrument}|{origen_ms}|{modelo}".encode()).digest()
    return int.from_bytes(h[:4], "little") & 0x7FFFFFFF


def versiones() -> dict:
    import importlib.metadata as md

    v = {"python": platform.python_version(), "plataforma": platform.platform()}
    for p in ("numpy", "scipy", "pandas", "pyarrow", "arch", "torch", "transformers", "chronos-forecasting",
              "huggingface_hub"):
        try:
            v[p] = md.version(p)
        except md.PackageNotFoundError:
            v[p] = None
    v["motor"] = MOTOR
    v["motor_commit"] = MOTOR_COMMIT
    try:
        dist = md.distribution("quantdesk")
        du = json.loads(dist.read_text("direct_url.json") or "{}")
        v["rueda_quantdesk_sha256"] = du.get("archive_info", {}).get("hash")
    except Exception:  # noqa: BLE001
        v["rueda_quantdesk_sha256"] = None
    return v


def _filas_corte(ins, c, modelo, Q, info, cpu_s, error):
    filas = []
    for h in HORIZONTES:
        f = {"instrument": ins, "origen_ms": c.origen_ms, "k": c.k, "ts_ultima_ms": c.ts_ultima_ms, "modelo": modelo,
             "h": h, "y": float(c.y[h - 1]), "rv": float(c.rv[h - 1]), "ok": error is None,
             "error": error or "", "cpu_s": cpu_s, "info": json.dumps(info, sort_keys=True)}
        q = Q[h - 1] if Q is not None else [float("nan")] * len(QCOLS)
        f.update({col: float(x) for col, x in zip(QCOLS, q)})
        filas.append(f)
    return filas


def correr_serie(serie, cortes, modelos, semilla, progreso=None):
    """Predicciones de todos los modelos en todos los cortes de una serie. Devuelve lista de filas."""
    filas = []
    for i, c in enumerate(cortes):
        for m in modelos:
            t0 = time.process_time()
            try:
                Q, info = m.predecir(c.precios, semilla_par(semilla, serie.instrument, c.origen_ms, m.nombre), HMAX)
                Q = np.asarray(Q, float)
                if Q.shape != (HMAX, len(QCOLS)) or not np.all(np.isfinite(Q)):
                    raise ValueError(f"salida invalida {Q.shape}")
                err = None
            except Exception as exc:  # noqa: BLE001 -- se cuenta y se informa, nunca se oculta
                Q, info, err = None, {}, f"{type(exc).__name__}: {exc}"[:300]
            # el CPU de un subproceso (Toto) no lo ve process_time: lo mide el trabajador y se suma aqui
            externo = float(info.pop("cpu_s_externo", 0.0)) if isinstance(info, dict) else 0.0
            filas += _filas_corte(serie.instrument, c, m.nombre, Q, info, time.process_time() - t0 + externo, err)
        if progreso:
            progreso(i + 1, len(cortes))
    return filas


def metricas_tabla(pred, modelos):
    """Metricas por (instrument, h, modelo) sobre los origenes en que TODOS los modelos dieron prevision."""
    import pandas as pd

    filas = []
    for (ins, h), g in pred.groupby(["instrument", "h"], sort=True):
        ok = g.groupby("origen_ms")["ok"].agg(lambda s: bool(s.all()) and len(s) == len(modelos))
        comunes = set(ok[ok].index)
        for m in modelos:
            gm = g[(g["modelo"] == m) & g["origen_ms"].isin(comunes)].sort_values("k", kind="mergesort")
            if gm.empty:
                continue
            r = metricas.resumen_celda(gm["y"].to_numpy(), gm[QCOLS].to_numpy(), gm["rv"].to_numpy(),
                                       gm["k"].to_numpy(), int(h))
            filas.append({"instrument": ins, "h": int(h), "modelo": m, **r})
    return pd.DataFrame(filas)


def ejecutar(dataset, out, nombres_modelos, activos, max_origenes, semilla, hilos, comando, reanudar,
             fabrica_modelos, cada=1):
    """Corrida sobre un dataset real. Escribe out/pred/<activo>.parquet, out/predicciones.parquet,
    out/metricas.csv y out/meta.json. `fabrica_modelos(nombres, hilos)` devuelve (modelos, saltados); un modelo
    saltado (p. ej. Toto sin su venv) se anota en meta["saltados"] y la corrida sigue con los demas.
    `cada` > 1 evalua uno de cada `cada` origenes validos de cada activo (submuestra declarada)."""
    import pandas as pd

    from . import rutas

    cfg = PRESETS[dataset]
    series, meta_ds = datos.cargar_dataset(rutas.dataset_dir(dataset), cfg["tabla"])
    if set(meta_ds["intervalos_ms"]) != {datos.DIA_MS}:
        raise ValueError(f"se esperaban barras diarias: {meta_ds['intervalos_ms']}")
    rej = datos.rejilla_origenes(cfg["inicio"], cfg["fin"], cfg["paso_dias"])
    nombres = sorted(series) if not activos else [a for a in activos if a in series]
    if activos and len(nombres) != len(activos):
        raise ValueError(f"activos inexistentes: {sorted(set(activos) - set(series))}")
    os.makedirs(os.path.join(out, "pred"), exist_ok=True)
    t_carga = time.process_time()
    modelos, saltados = fabrica_modelos(nombres_modelos, hilos)
    t_carga = time.process_time() - t_carga
    for n, motivo in saltados.items():
        print(f"modelo {n}: {motivo}", flush=True)
    if not modelos:
        raise RuntimeError(f"ningun modelo ejecutable: {saltados}")
    meta = {"dataset": meta_ds, "config": {**cfg, "horizontes": list(HORIZONTES), "semilla": semilla,
                                           "s_caminos": caminos_por_modelo(modelos), "hilos_torch": hilos,
                                           "activos": nombres, "max_origenes": max_origenes, "cada": cada,
                                           "modelos": [m.nombre for m in modelos], "n_rejilla": len(rej)},
            "comando": comando, "versiones": versiones(), "omitidos": {}, "cpu_carga_modelos_s": t_carga,
            "saltados": saltados}
    for m in modelos:
        if getattr(m, "versiones", None) is not None:
            meta.setdefault("versiones_externas", {})[m.nombre] = m.versiones
        if getattr(m, "pesos", None):
            meta.setdefault("pesos", {})[m.nombre] = m.pesos
    partes = []
    w0 = time.perf_counter()
    for ins in nombres:
        cortes, omit = datos.cortes_de_serie(series[ins], rej, cfg["ventana"], HMAX)
        if cada > 1:
            cortes = cortes[::cada]
        if max_origenes:
            cortes = cortes[:max_origenes]
        meta["omitidos"][ins] = {**omit, "evaluados": len(cortes)}
        fp = os.path.join(out, "pred", f"{ins}.parquet")
        if reanudar and os.path.exists(fp):
            partes.append(pd.read_parquet(fp))
            print(f"{ins}: reanudado ({len(cortes)} origenes)", flush=True)
            continue
        t0 = time.perf_counter()

        def prog(i, n, ins=ins, t0=t0):
            if i % 25 == 0 or i == n:
                print(f"  {ins}: {i}/{n} origenes, {time.perf_counter() - t0:.0f} s", flush=True)

        df = pd.DataFrame(correr_serie(series[ins], cortes, modelos, semilla, prog))
        df.to_parquet(fp + ".tmp", index=False)
        os.replace(fp + ".tmp", fp)
        partes.append(df)
    for m in modelos:
        if hasattr(m, "cerrar"):
            m.cerrar()
    pred = pd.concat(partes, ignore_index=True)
    pred = pred.sort_values(["instrument", "origen_ms", "modelo", "h"], kind="mergesort").reset_index(drop=True)
    pred.to_parquet(os.path.join(out, "predicciones.parquet"), index=False)
    met = metricas_tabla(pred, [m.nombre for m in modelos])
    met.to_csv(os.path.join(out, "metricas.csv"), index=False, float_format="%.10g")
    p1 = pred[pred["h"] == HORIZONTES[0]]
    meta["cpu"] = {m: {"total_s": float(p1.loc[p1["modelo"] == m, "cpu_s"].sum()),
                       "por_origen_s": float(p1.loc[p1["modelo"] == m, "cpu_s"].mean()),
                       "n": int((p1["modelo"] == m).sum())} for m in sorted(p1["modelo"].unique())}
    meta["fallos"] = {m: int((~p1.loc[p1["modelo"] == m, "ok"]).sum()) for m in sorted(p1["modelo"].unique())}
    meta["errores_ejemplo"] = p1.loc[~p1["ok"], ["instrument", "origen_ms", "modelo", "error"]].head(10).to_dict("records")
    conv = {}
    for m in sorted(p1["modelo"].unique()):
        inf = [json.loads(x) for x in p1.loc[(p1["modelo"] == m) & p1["ok"], "info"]]
        if inf and "convergido" in inf[0]:
            conv[m] = {"no_convergido": int(sum(not d["convergido"] for d in inf)), "n": len(inf)}
    meta["convergencia"] = conv
    meta["pared_s"] = time.perf_counter() - w0
    meta["predicciones_sha256"] = hash_predicciones(pred)
    meta["metricas_sha256"] = hashlib.sha256(met.to_csv(index=False, float_format="%.10g").encode()).hexdigest()
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1, default=str)
    return pred, met, meta


def hash_predicciones(pred) -> str:
    cols = ["instrument", "origen_ms", "modelo", "h", "y", "rv", *QCOLS]
    return hashlib.sha256(pred[cols].to_csv(index=False, float_format="%.17g").encode()).hexdigest()


def comparar(out, ref):
    """Compara las predicciones y las metricas de `out` con las de la corrida `ref` restringida a las mismas claves."""
    import pandas as pd

    a = pd.read_parquet(os.path.join(out, "predicciones.parquet"))
    b = pd.read_parquet(os.path.join(ref, "predicciones.parquet"))
    with open(os.path.join(ref, "meta.json"), encoding="utf-8") as f:
        mref = json.load(f)
    clave = ["instrument", "origen_ms", "modelo", "h"]
    j = a.merge(b, on=clave, how="left", suffixes=("", "_ref"), indicator=True)
    faltan = int((j["_merge"] != "both").sum())
    cols = ["y", "rv", *QCOLS]
    dif = float(np.nanmax(np.abs(j[cols].to_numpy() - j[[c + "_ref" for c in cols]].to_numpy()))) if len(j) else 0.0
    iguales = bool(faltan == 0 and np.array_equal(j[cols].to_numpy(), j[[c + "_ref" for c in cols]].to_numpy(),
                                                  equal_nan=True))
    b_sub = b.merge(a[clave], on=clave, how="inner")
    modelos = sorted(a["modelo"].unique())
    ma = metricas_tabla(a, modelos).sort_values(["instrument", "h", "modelo"]).reset_index(drop=True)
    mb = metricas_tabla(b_sub, modelos).sort_values(["instrument", "h", "modelo"]).reset_index(drop=True)
    num = [c for c in ma.columns if c not in ("instrument", "h", "modelo")]
    dm = float(np.nanmax(np.abs(ma[num].to_numpy(float) - mb[num].to_numpy(float)))) if len(ma) else 0.0
    met_iguales = bool(ma[["instrument", "h", "modelo"]].equals(mb[["instrument", "h", "modelo"]])
                       and np.array_equal(ma[num].to_numpy(float), mb[num].to_numpy(float), equal_nan=True))
    return {"referencia": ref.replace(os.sep, "/"), "filas": int(len(a)), "filas_sin_pareja": faltan,
            "max_dif_predicciones": dif, "predicciones_identicas": iguales, "max_dif_metricas": dm,
            "metricas_identicas": met_iguales, "ref_dataset_hash": mref["dataset"]["dataset_hash"]}
