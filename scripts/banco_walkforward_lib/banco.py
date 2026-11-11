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
CORTE_LIMPIO = "2025-08-27T00:00:00Z"
CORTE_LIMPIO_MS = 1756252800000
CLAVES_METRICAS = ["instrument", "h", "modelo"]


def es_origen_limpio(origen_ms):
    return origen_ms > CORTE_LIMPIO_MS

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
            if m.nombre == "fincast" and not es_origen_limpio(c.origen_ms):
                continue
            t0 = time.process_time()
            try:
                Q, info = m.predecir(c.precios, semilla_par(semilla, serie.instrument, c.origen_ms, m.nombre), HMAX)
                Q = np.asarray(Q, float)
                if Q.shape != (HMAX, len(QCOLS)) or not np.all(np.isfinite(Q)):
                    raise ValueError(f"salida invalida {Q.shape}")
                if np.any(np.diff(Q, axis=1) < 0):
                    raise ValueError("cuantiles no monotonos (se exige orden no decreciente)")
                err = None
            except Exception as exc:  # noqa: BLE001 -- se cuenta y se informa, nunca se oculta
                Q, info, err = None, {}, f"{type(exc).__name__}: {exc}"[:300]
            # el CPU de un subproceso (Toto) no lo ve process_time: lo mide el trabajador y se suma aqui
            externo = float(info.pop("cpu_s_externo", 0.0)) if isinstance(info, dict) else 0.0
            filas += _filas_corte(serie.instrument, c, m.nombre, Q, info, time.process_time() - t0 + externo, err)
        if progreso:
            progreso(i + 1, len(cortes))
    return filas


def metricas_tabla(pred, modelos, limpia=False):
    """Principal: todos los modelos pedidos salvo FinCast, sin recortar por su cobertura.
    Limpia: origen > corte UTC, comunes de TODOS los modelos pedidos, y CRPS de deciles comparable.
    """
    import pandas as pd

    modelos = list(dict.fromkeys(m for m in modelos if limpia or m != "fincast"))
    columnas = CLAVES_METRICAS + list(metricas.COLUMNAS_RESUMEN)
    if limpia:
        columnas += ["crps_deciles", "criterios_no_aplicables"]
    if pred.empty or not modelos:
        return pd.DataFrame(columns=columnas)
    pred = pred[pred["modelo"].isin(modelos)]
    if limpia:
        pred = pred[es_origen_limpio(pred["origen_ms"])]
        pred, _ = validar_predicciones_limpias(pred)
    if pred.duplicated(["instrument", "h", "modelo", "origen_ms"]).any():
        raise ValueError("predicciones duplicadas por activo/h/modelo/origen")
    filas = []
    for (ins, h), g in pred.groupby(["instrument", "h"], sort=True):
        ok = g.groupby("origen_ms")["ok"].agg(lambda s: bool(s.all()) and len(s) == len(modelos))
        comunes = set(ok[ok].index)
        for m in modelos:
            gm = g[(g["modelo"] == m) & g["origen_ms"].isin(comunes)].sort_values("k", kind="mergesort")
            if gm.empty:
                continue
            if m == "fincast":
                r = metricas.resumen_fincast(gm["y"].to_numpy(), gm[QCOLS].to_numpy(), gm["rv"].to_numpy())
            else:
                r = metricas.resumen_celda(gm["y"].to_numpy(), gm[QCOLS].to_numpy(), gm["rv"].to_numpy(),
                                           gm["k"].to_numpy(), int(h))
                if limpia:
                    r["crps_deciles"] = float(np.mean(metricas.crps_deciles(gm["y"].to_numpy(), gm[QCOLS].to_numpy())))
                    r["criterios_no_aplicables"] = ""
            filas.append({"instrument": ins, "h": int(h), "modelo": m, **r})
    return pd.DataFrame(filas, columns=columnas)


def estado_limpia(pred, met, modelos):
    hay = not pred.empty and bool(es_origen_limpio(pred["origen_ms"]).any())
    seleccion = pred[pred["modelo"].isin(modelos) & es_origen_limpio(pred["origen_ms"])] if not pred.empty else pred
    _, validacion = validar_predicciones_limpias(seleccion)
    return {"corte_utc": CORTE_LIMPIO, "regla": "origen_ms > corte (estricto); contexto puede ser anterior",
            "modelos": list(modelos), "estado": "vacia" if met.empty else "calculada", "celdas": len(met),
            "motivo": ("sin origenes posteriores al corte" if not hay else "sin origenes comunes validos")
                      if met.empty else "", "exclusiones_fincast": metricas.MOTIVO_FINCAST,
            "validacion_predicciones": validacion}


def validar_predicciones_limpias(pred):
    """Valida tambien previsiones archivadas antes de formar la nueva comparacion limpia.
    Un cruce en cualquier h almacenado invalida el origen-modelo entero, como correr_serie.
    No repara cuantiles ni modifica el archivo de predicciones ni sus criterios principales historicos.
    """
    estado = {"origenes_modelo_excluidos": 0, "por_modelo": {}, "ejemplos": [],
              "alcance": "origenes limpios suministrados, antes de tomar los comunes"}
    if pred.empty:
        return pred, estado
    buenas = pred.loc[pred["ok"]]
    Q = buenas[QCOLS].to_numpy(float)
    malas = buenas.loc[~np.isfinite(Q).all(axis=1) | (np.diff(Q, axis=1) < 0).any(axis=1)]
    claves = ["instrument", "origen_ms", "modelo"]
    invalidos = malas[claves].drop_duplicates()
    if invalidos.empty:
        return pred, estado
    import pandas as pd

    out = pred.copy()
    marca = pd.MultiIndex.from_frame(out[claves]).isin(pd.MultiIndex.from_frame(invalidos))
    out.loc[marca, "ok"] = False
    out.loc[marca, "error"] = "salida archivada invalida: cuantiles no finitos o no monotonos; excluida de ventana limpia"
    estado.update(origenes_modelo_excluidos=len(invalidos), por_modelo=invalidos.groupby("modelo").size().to_dict(),
                  ejemplos=invalidos.head(10).to_dict("records"))
    return out, estado


def ejecutar(dataset, out, nombres_modelos, activos, max_origenes, semilla, hilos, comando, reanudar,
             fabrica_modelos, cada=1, solo_limpia=False):
    """Corrida sobre un dataset real. Escribe out/pred/<activo>.parquet, out/predicciones.parquet,
    out/metricas.csv y out/meta.json. `fabrica_modelos(nombres, hilos)` devuelve (modelos, saltados); un modelo
    saltado (p. ej. Toto sin su venv) se anota en meta["saltados"] y la corrida sigue con los demas.
    `cada` > 1 evalua uno de cada `cada` origenes validos de cada activo (submuestra declarada)."""
    import pandas as pd

    from . import rutas

    inicio_pared = time.perf_counter()
    cfg = PRESETS[dataset]
    solo_limpia = solo_limpia or nombres_modelos == ["fincast"]
    series, meta_ds = datos.cargar_dataset(rutas.dataset_dir(dataset), cfg["tabla"])
    if set(meta_ds["intervalos_ms"]) != {datos.DIA_MS}:
        raise ValueError(f"se esperaban barras diarias: {meta_ds['intervalos_ms']}")
    rej = datos.rejilla_origenes(cfg["inicio"], cfg["fin"], cfg["paso_dias"])
    nombres = sorted(series) if not activos else [a for a in activos if a in series]
    if activos and len(nombres) != len(activos):
        raise ValueError(f"activos inexistentes: {sorted(set(activos) - set(series))}")
    os.makedirs(os.path.join(out, "pred"), exist_ok=True)
    t_carga = time.process_time()
    w_carga = time.perf_counter()
    modelos, saltados = fabrica_modelos(nombres_modelos, hilos)
    w_carga = time.perf_counter() - w_carga
    t_carga = time.process_time() - t_carga + sum(getattr(m, "cpu_carga_s", 0.0) for m in modelos)
    for n, motivo in saltados.items():
        print(f"modelo {n}: {motivo}", flush=True)
    if not modelos:
        raise RuntimeError(f"ningun modelo ejecutable: {saltados}")
    meta = {"dataset": meta_ds, "config": {**cfg, "horizontes": list(HORIZONTES), "semilla": semilla,
                                           "s_caminos": caminos_por_modelo(modelos), "hilos_torch": hilos,
                                           "activos": nombres, "max_origenes": max_origenes, "cada": cada,
                                           "modelos": [m.nombre for m in modelos], "n_rejilla": len(rej),
                                           "solo_limpia": solo_limpia},
            "comando": comando, "versiones": versiones(), "omitidos": {}, "cpu_carga_modelos_s": t_carga,
            "saltados": saltados, "pared_carga_modelos_s": w_carga}
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
        if solo_limpia:
            limpios = [c for c in cortes if es_origen_limpio(c.origen_ms)]
            omit["fuera_ventana_limpia"] = len(cortes) - len(limpios)
            cortes = limpios
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

        df = pd.DataFrame(correr_serie(series[ins], cortes, modelos, semilla, prog),
                          columns=["instrument", "origen_ms", "k", "ts_ultima_ms", "modelo", "h", "y", "rv",
                                   "ok", "error", "cpu_s", "info", *QCOLS])
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
    limpia = metricas_tabla(pred, [m.nombre for m in modelos], limpia=True)
    limpia.to_csv(os.path.join(out, "metricas_limpia.csv"), index=False, float_format="%.10g")
    meta["ventana_limpia"] = estado_limpia(pred, limpia, [m.nombre for m in modelos])
    meta["ventana_limpia"]["metricas_sha256"] = hashlib.sha256(
        limpia.to_csv(index=False, float_format="%.10g").encode()).hexdigest()
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
    meta["pared_total_s"] = time.perf_counter() - inicio_pared
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
    limpia_a = metricas_tabla(a, modelos, limpia=True)
    limpia_b = metricas_tabla(b_sub, modelos, limpia=True)
    limpias_iguales = limpia_a.equals(limpia_b)
    return {"referencia": ref.replace(os.sep, "/"), "filas": int(len(a)), "filas_sin_pareja": faltan,
            "max_dif_predicciones": dif, "predicciones_identicas": iguales, "max_dif_metricas": dm,
            "metricas_identicas": met_iguales, "metricas_limpias_identicas": limpias_iguales,
            "ref_dataset_hash": mref["dataset"]["dataset_hash"]}
