"""Dos tablas MT5, auditoria de fuentes y revision calculada de TS-00-OBJ.

No modifica umbrales ni predicciones. Las comparaciones usan las funciones de metricas
existentes, con GARCH sobre los mismos origenes que cada modelo.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from . import banco, datos, rutas

ANTIGUO = "lago_cierre_c20261101"
CABECERA = "mt5_fx28_cierre_c20261101"
AMPLIACION = "mt5_fx28_hist_cierre_c20261101"
MODELOS = ("chronos2", "toto", "hmm", "fincast")
REFERENCIAS = {
    "base": rutas.RUNS + "/lago_cierre_c20261101",
    "toto": rutas.RUNS + "/toto_lago_cierre_c20261101",
    "fincast": rutas.RUNS_FINCAST + "/fincast_fx",
}


def _numero(x):
    return x is not None and math.isfinite(float(x))


def _estado(condicion):
    return "no evaluable" if condicion is None else "pasa" if condicion else "no pasa"


def evaluar_criterios(filas, fincast=False):
    """Contrato puro, sin redondear antes de comparar; un horizonte ausente no aprueba.

    FinCast solo evalua C1; C2/C3 son no aplica y el resultado tiene alcance solo CRPS.
    """
    por_h = {r["h"]: dict(r) for r in filas}
    salida = []
    for h in banco.HORIZONTES:
        r = por_h.get(h, {"h": h})
        crps = r.get("crps_rel")
        r["crps_097"] = _estado(float(crps) <= .97 if _numero(crps) else None)
        r["tope_102"] = _estado(float(crps) <= 1.02 if _numero(crps) else None)
        n = r.get("n_activos", 0)
        colas = [r.get("rechazos_01"), r.get("rechazos_99")]
        r["c2"] = "no aplica" if fincast else _estado(
            all(x / n <= .10 for x in colas) if n and all(_numero(x) for x in colas) else None)
        r["c3"] = "no aplica" if fincast else _estado(
            float(r["banda_rel"]) <= 2.0 if _numero(r.get("banda_rel")) else None)
        salida.append(r)
    valores = [r.get("crps_rel") for r in salida]
    c1 = _estado(sum(float(x) <= .97 for x in valores) >= 2 and all(float(x) <= 1.02 for x in valores)
                 if all(_numero(x) for x in valores) else None)

    def conjunto(k):
        estados = [r[k] for r in salida]
        return "no evaluable" if "no evaluable" in estados else _estado(all(x == "pasa" for x in estados))

    c2, c3 = ("no aplica", "no aplica") if fincast else (conjunto("c2"), conjunto("c3"))
    aplicables = [c1] if fincast else [c1, c2, c3]
    total = "no evaluable" if "no evaluable" in aplicables else _estado(all(x == "pasa" for x in aplicables))
    return {"horizontes": salida, "c1": c1, "c2": c2, "c3": c3, "resultado": total,
            "alcance": "solo CRPS deciles limpio" if fincast else "forecast M1: tres condiciones"}


def situacion(antes, despues, rankings_antes=None, rankings_despues=None):
    """Rango por modelo, cruces de 1/.97 y cambios de orden por horizonte."""
    rangos, cruces, ordenes = {}, [], []
    for m in MODELOS:
        aa = {r["h"]: r.get("crps_rel") for r in antes[m]["horizontes"]}
        bb = {r["h"]: r.get("crps_rel") for r in despues[m]["horizontes"]}
        def rango(d):
            v = list(d.values())
            return [min(v), max(v)] if all(_numero(x) for x in v) else None
        rangos[m] = {"antiguo": rango(aa), "mt5": rango(bb)}
        for h in banco.HORIZONTES:
            if _numero(aa[h]) and _numero(bb[h]):
                for umbral in (.97, 1.0):
                    if (aa[h] <= umbral) != (bb[h] <= umbral):
                        cruces.append({"modelo": m, "h": h, "umbral": umbral, "antes": aa[h], "despues": bb[h]})
    if rankings_antes is None:
        # Interfaz pura para fixtures que comparten muestra/definicion de CRPS.
        rankings_antes = {"fixture_comparable": {h: {m: antes[m]["horizontes"][i].get("crps_rel") for m in MODELOS}
                                                for i, h in enumerate(banco.HORIZONTES)}}
        rankings_despues = {"fixture_comparable": {h: {m: despues[m]["horizontes"][i].get("crps_rel") for m in MODELOS}
                                                  for i, h in enumerate(banco.HORIZONTES)}}
    for grupo, rr in rankings_antes.items():
        for h in banco.HORIZONTES:
            a, b = rr[h], rankings_despues[grupo][h]
            comunes = [m for m in a if _numero(a[m]) and _numero(b.get(m))]
            cambios = [[m, n] for i, m in enumerate(comunes) for n in comunes[i + 1:]
                       if np.sign(a[m] - a[n]) != np.sign(b[m] - b[n])]
            ordenes.append({"grupo": grupo, "h": h, "antiguo": sorted(comunes, key=lambda m: (a[m], m)),
                            "mt5": sorted(comunes, key=lambda m: (b[m], m)), "cambios": cambios,
                            "estado": "calculado" if len(comunes) >= 2 else "no evaluable"})
    return {"rangos": rangos, "cruces": cruces, "ordenes": ordenes,
            "cambia": bool(cruces or any(o["cambios"] for o in ordenes))}


def _cargar(run):
    p = Path(run)
    meta = json.loads((p / "meta.json").read_text(encoding="utf-8"))
    pred = pd.read_parquet(p / "predicciones.parquet")
    if banco.hash_predicciones(pred) != meta["predicciones_sha256"]:
        raise ValueError(f"SHA-256 canonico de predicciones distinto en {run}")
    ds = meta["dataset"]["dataset_id"]
    if ds in rutas.HASHES_MT5 and meta["dataset"]["dataset_hash"] != rutas.HASHES_MT5[ds]:
        raise ValueError(f"dataset_hash MT5 distinto en {run}")
    return {"run": str(run).replace(os.sep, "/"), "meta": meta, "pred": pred}


def _unir(partes):
    """Reutiliza la validacion de contexto/objetivo del informe existente, sin escribir."""
    from . import informe

    if not partes:
        return pd.DataFrame(), [], pd.DataFrame()
    met, estado, _ = informe.cargar_limpia([p["run"] for p in partes])
    return pd.concat([p["pred"] for p in partes], ignore_index=True), estado, met


def _comunes(pred, modelos, limpia=False):
    if pred.empty:
        return pred
    pred = pred[pred.modelo.isin(modelos)]
    if limpia:
        pred = pred[banco.es_origen_limpio(pred.origen_ms)]
        pred, _ = banco.validar_predicciones_limpias(pred)
    claves = ["instrument", "origen_ms", "h"]
    ok = pred.groupby(claves).ok.agg(lambda s: bool(s.all()) and len(s) == len(modelos))
    return pred.merge(ok[ok].reset_index()[claves], on=claves, how="inner")


def revisar(partes, activos):
    """Main HMM/Chronos; Toto en su submuestra; FinCast en limpia comun de todos.

    Exige todos los activos esperados en cada horizonte para emitir pasa/no pasa.
    Evita convertir fallos o modelos ausentes en aprobaciones de colas.
    """
    vacio = pd.DataFrame()
    base = next((p for p in partes if {"hmm", "garch", "chronos2"}.issubset(p["meta"]["config"]["modelos"])), None)
    toto = next((p for p in partes if "toto" in p["meta"]["config"]["modelos"]), None)
    fc = next((p for p in partes if "fincast" in p["meta"]["config"]["modelos"]), None)
    salida = {}
    for m in MODELOS:
        mods = ["hmm", "garch", "chronos2"]
        pred = base["pred"] if base else vacio
        if m == "toto":
            mods += ["toto"]
            pred = pd.concat([pred, toto["pred"]], ignore_index=True) if toto and base else vacio
        if m == "fincast":
            if fc and base:
                pp = [base] + ([toto] if toto else []) + [fc]
                pred, _, _ = _unir(pp)
                mods = sorted(pred.modelo.unique())
            else:
                pred = vacio
        comun = _comunes(pred, mods, limpia=m == "fincast")
        met = banco.metricas_tabla(comun, mods, limpia=m == "fincast") if not comun.empty else vacio
        filas = []
        for h in banco.HORIZONTES:
            r = {"h": h, "n_activos": 0, "motivo": "modelo ausente o sin origenes comunes validos"}
            if not met.empty:
                gm = met[(met.modelo == m) & (met.h == h)].set_index("instrument")
                ga = met[(met.modelo == "garch") & (met.h == h)].set_index("instrument")
                r["n_activos"] = len(gm)
                r["origenes_por_activo"] = gm["n"].astype(int).to_dict()
                if set(gm.index) == set(ga.index) == set(activos):
                    col = "crps_deciles" if m == "fincast" else "crps"
                    rel = gm[col] / ga[col]
                    if np.isfinite(rel).all() and (ga[col] > 0).all():
                        r.update(crps_rel=float(rel.median()), qlike=float(gm.qlike.median()), motivo="")
                    if m != "fincast":
                        for cola in ("01", "99"):
                            pv = gm[f"kupiec_{cola}_p"]
                            r[f"rechazos_{cola}"] = int((pv < .05).sum()) if np.isfinite(pv).all() else None
                        ph = comun[comun.h == h]
                        ancho = ph.assign(w=ph.q20 - ph.q00).groupby("modelo").w.quantile(.99)
                        if "garch" in ancho and ancho["garch"] > 0:
                            r["banda_p99"] = float(ancho[m])
                            r["garch_banda_p99"] = float(ancho["garch"])
                            r["banda_rel"] = float(ancho[m] / ancho["garch"])
                else:
                    r["motivo"] = "cobertura incompleta de activos; no se reduce el denominador"
            filas.append(r)
        salida[m] = evaluar_criterios(filas, m == "fincast")
    return salida


def clasificaciones(partes, activos):
    """Ordenes solo con misma muestra y mismo CRPS: principal, Toto y limpia.

    FinCast participa exclusivamente en el orden de CRPS deciles limpio comun.
    """
    base = next((p for p in partes if {"hmm", "garch", "chronos2"}.issubset(p["meta"]["config"]["modelos"])), None)
    toto = next((p for p in partes if "toto" in p["meta"]["config"]["modelos"]), None)
    fc = next((p for p in partes if "fincast" in p["meta"]["config"]["modelos"]), None)
    salida = {}
    for grupo, limpia, mods in [("principal_crps21", False, ["hmm", "garch", "chronos2"]),
                                ("submuestra_toto_crps21", False, ["hmm", "garch", "chronos2", "toto"]),
                                ("limpia_comun_crps_deciles", True, ["hmm", "garch", "chronos2", "toto", "fincast"])]:
        pp = [base] if base else []
        if grupo != "principal_crps21":
            pp = pp + [toto] if pp and toto else []
        if limpia:
            pp = pp + [fc] if pp and fc else []
        met = pd.DataFrame()
        if pp:
            pred = pd.concat([p["pred"] for p in pp], ignore_index=True)
            comun = _comunes(pred, mods, limpia)
            met = banco.metricas_tabla(comun, mods, limpia)
        salida[grupo] = {}
        for h in banco.HORIZONTES:
            rr = {m: None for m in mods if m != "garch"}
            if not met.empty:
                g = met[met.h == h]
                piv = g.pivot(index="instrument", columns="modelo", values="crps_deciles" if limpia else "crps")
                if set(piv.index) == set(activos) and set(piv.columns) == set(mods) and np.isfinite(piv).all().all() and (piv.garch > 0).all():
                    rr = {m: float((piv[m] / piv.garch).median()) for m in rr}
            salida[grupo][h] = rr
    return salida


def inventario(series, cfg):
    rej = datos.rejilla_origenes(cfg["inicio"], cfg["fin"], cfg["paso_dias"])
    filas = []
    inicio = rej[0]
    for ins, s in sorted(series.items()):
        cc, omit = datos.cortes_de_serie(s, rej, cfg["ventana"], banco.HMAX)
        dias = (s.ts_ms // datos.DIA_MS + 3) % 7
        filas.append({"instrument": ins, "barras": len(s.close), "primera_barra": datos.fecha(int(s.ts_ms[0])),
                      "sabados": int((dias == 5).sum()), "domingos": int((dias == 6).sum()),
                      "barras_antes_inicio": int((s.ts_ms < inicio).sum()), "origenes_validos": len(cc),
                      "primer_origen": datos.fecha(cc[0].origen_ms) if cc else None,
                      "ultimo_origen": datos.fecha(cc[-1].origen_ms) if cc else None, **omit})
    return filas


def validar_objetivos(run, series, cfg):
    """Los y del diferencial deben ser los guardados en el run, no solo otra tabla calculada."""
    pred = run["pred"]
    claves = ["instrument", "origen_ms", "h"]
    if (pred.groupby(claves)[["y", "rv"]].nunique(dropna=False) > 1).any().any():
        raise ValueError(f"objetivos diferentes entre modelos: {run['run']}")
    for (ins, t), g in pred.drop_duplicates(claves).groupby(["instrument", "origen_ms"]):
        c = datos.cortar(series[ins], int(t), cfg["ventana"], banco.HMAX)
        if c is None:
            raise ValueError(f"origen no valido en dataset: {run['run']} {ins} {t}")
        for r in g.itertuples():
            if r.y != float(c.y[r.h - 1]) or r.rv != float(c.rv[r.h - 1]):
                raise ValueError(f"y/rv del parquet difieren del dataset: {run['run']} {ins} {t} h={r.h}")
    return {"run": run["run"], "filas_objetivo": len(pred.drop_duplicates(claves)), "identicos": True}


def causa_exclusivo(s_valida, s_otra, origen, cfg):
    """Solo las causas autorizadas; ninguna explicacion generica acepta un cambio."""
    W = cfg["ventana"]
    vis = np.flatnonzero(s_otra.disp_ms <= origen)
    inicio = datos.rejilla_origenes(cfg["inicio"], cfg["inicio"], 1)[0]
    nv = int((s_valida.ts_ms < inicio).sum())
    no = int((s_otra.ts_ms < inicio).sum())
    if len(vis) < W and nv == 249 and no == 248:
        return "barra extra antes de inicio (249 frente a 248)"
    if len(vis) >= W and int(vis[-1]) + banco.HMAX >= len(s_otra.close):
        return "falta de 20 pasos futuros"
    # Solo fechas de barras visibles que no existen en la otra fuente.
    av = s_valida.ts_ms[s_valida.disp_ms <= origen]
    ao = s_otra.ts_ms[s_otra.disp_ms <= origen]
    ultimas = np.union1d(av[-1:], ao[-1:])
    distintas = [int(t) for t in ultimas if (t in av) != (t in ao)]
    if distintas:
        fechas = ", ".join(datos.fecha(t) + (" (fin de semana)" if (t // datos.DIA_MS + 3) % 7 >= 5 else " (dia sin barra/festivo)")
                           for t in distintas)
        return "dia con barra en una fuente y no en la otra: " + fechas
    return "BLOQUEADO: causa fuera del contrato"


def diferencial(antiguas, nuevas, cfg, claves_piloto):
    """Validez de fuentes en toda la rejilla; delta y en el ambito de los pilotos.

    El limite N del piloto no es un hueco de datos: se consulta la validez completa
    de la otra fuente aunque el piloto no haya inferido ese origen.
    """
    rej = datos.rejilla_origenes(cfg["inicio"], cfg["fin"], cfg["paso_dias"])
    exclusivos, deltas = [], []
    for ins in sorted(nuevas):
        sa, sn = antiguas[ins], nuevas[ins]
        ca = {c.origen_ms: c for c in datos.cortes_de_serie(sa, rej, cfg["ventana"], banco.HMAX)[0]}
        cn = {c.origen_ms: c for c in datos.cortes_de_serie(sn, rej, cfg["ventana"], banco.HMAX)[0]}
        ka, kn = set(ca), set(cn)
        for t in sorted(ka ^ kn):
            nueva = t in kn
            exclusivos.append({"instrument": ins, "fecha": datos.fecha(t), "origen_ms": t,
                                "solo_en": "MT5" if nueva else "antigua", "en_piloto": (ins, t) in claves_piloto,
                                "causa": causa_exclusivo(sn if nueva else sa, sa if nueva else sn, t, cfg)})
        for t in sorted(ka & kn):
            if (ins, t) not in claves_piloto:
                continue
            for h in banco.HORIZONTES:
                dy = float((cn[t].y[h - 1] - ca[t].y[h - 1]) * 10000)
                deltas.append({"instrument": ins, "fecha": datos.fecha(t), "h": h, "delta_y_pb": dy,
                               "abs_delta_y_pb": abs(dy)})
    dd = pd.DataFrame(deltas)
    resumen, extremos = [], []
    if not dd.empty:
        for h, g in dd.groupby("h"):
            resumen.append({"h": int(h), "n": len(g), "mediana_delta_pb": float(g.delta_y_pb.median()),
                            "mediana_abs_pb": float(g.abs_delta_y_pb.median()), "max_abs_pb": float(g.abs_delta_y_pb.max())})
        for (ins, h), g in dd.groupby(["instrument", "h"]):
            med = float(g.abs_delta_y_pb.median())
            extremos += g[g.abs_delta_y_pb > 5 * med].assign(mediana_abs_par_h_pb=med).to_dict("records")
    return {"estado": "BLOQUEADO" if any(x["causa"].startswith("BLOQUEADO") for x in exclusivos) else "explicado",
            "exclusivos": exclusivos, "resumen_delta_y": resumen, "extremos": extremos,
            "deltas": deltas, "explicacion": "close 00:00 UTC de yfinance → cierre de sesion 17:00 NY de MT5"}


def oraculo(run, directorio):
    """Lee dos close directamente del parquet: no llama a cortar ni a cargar_dataset."""
    import pyarrow.parquet as pq

    pred = run["pred"]
    fila = pred[(pred.instrument == "EURUSD") & (pred.h == 1)].sort_values("origen_ms").iloc[0]
    man = json.loads(Path(directorio, "manifest.json").read_text(encoding="utf-8"))
    tabla = next(t for t in man["tables"] if t["table_id"] == "lago_ohlcv_1d")
    df = pq.read_table(Path(directorio, tabla["path"]), columns=["instrument", "ts_ms", "close"]).to_pandas()
    df = df[df.instrument == "EURUSD"].sort_values("ts_ms").reset_index(drop=True)
    # Proxy declarado: disponible en ts + 1 dia, sin usar indices del banco.
    visibles = df[df.ts_ms + 86_400_000 <= int(fila.origen_ms)]
    k = int(visibles.index[-1])
    c0, c1 = float(df.iloc[k].close), float(df.iloc[k + 1].close)
    manual = math.log(c1 / c0)
    diferencia = abs(manual - float(fila.y))
    return {"instrument": "EURUSD", "origen": datos.fecha(int(fila.origen_ms)),
            "fecha_c0": datos.fecha(int(df.iloc[k].ts_ms)), "fecha_c1": datos.fecha(int(df.iloc[k + 1].ts_ms)),
            "close_0": c0, "close_1": c1, "log_c1_c0": manual, "y_banco": float(fila.y),
            "diferencia": diferencia, "coincide": diferencia <= 1e-15,
            "nota": "tolerancia 1e-15: log(c1/c0) escalar frente a log(c1)-log(c0) vectorial"}


def presupuesto(piloto, filas_inventario):
    meta = piloto["meta"]
    n = sum(r["origenes_validos"] for r in filas_inventario)
    pared = meta.get("pared_modelos", {})
    medidos = {m: pared[m]["por_origen_s"] for m in ("hmm", "garch", "chronos2") if m in pared}
    npil = sum(v["evaluados"] for v in meta["omitidos"].values())
    sobrecoste = max(0.0, meta["pared_s"] - sum(t["total_s"] for t in pared.values())) / max(npil, 1)
    carga = meta.get("pared_carga_modelos_s", 0.0)
    preparacion = max(0.0, meta.get("pared_total_s", meta["pared_s"] + carga) - meta["pared_s"] - carga)
    estimada = n * (sum(medidos.values()) + sobrecoste) + carga + preparacion if len(medidos) == 3 else None
    return {"paso_dias": meta["config"]["paso_dias"], "n_completo": n, "n_piloto": npil,
            "pared_s_por_origen": medidos, "sobrecoste_s_por_origen": sobrecoste,
            "carga_s": carga, "preparacion_s": preparacion, "estimada_s": estimada,
            "estimada_h": estimada / 3600 if estimada is not None else None,
            "cabe_2h": estimada is not None and estimada <= 7200, "hilos_torch": meta["config"]["hilos_torch"]}


def comandos():
    p = ".venv/Scripts/python -X utf8 scripts/banco_walkforward.py"
    b, f = rutas.RUNS, rutas.RUNS_FINCAST
    cab, hist, toto, fc = b + "/mt5_fx28_cierre_c20261101", b + "/mt5_fx28_hist_cierre_c20261101", b + "/toto_mt5_fx28_cierre_c20261101", f + "/mt5_fx28_cierre_c20261101"
    return [
        "$env:HF_HOME='E:/quantdesk-lab/cache/hf'; $env:HF_HUB_OFFLINE='1'; $env:TRANSFORMERS_OFFLINE='1'",
        "$env:QUANTDESK_BENCH_TMP='E:/quantdesk-lab/tmp/TS-00-BENCH-MT5'; $env:TMP=$env:QUANTDESK_BENCH_TMP; $env:TEMP=$env:TMP; $env:TMPDIR=$env:TMP; $env:PYTHONDONTWRITEBYTECODE='1'",
        f"{p} --dataset {CABECERA} --hilos 2 --out {cab}",
        f"{p} --dataset {AMPLIACION} --hilos 2 --out {hist}",
        f"{p} --dataset {CABECERA} --modelos toto --hilos 2 --cada 5 --out {toto}",
        f"{p} --dataset {CABECERA} --modelos fincast --hilos 2 --solo-limpia --cada 5 --out {fc}",
        f"{p} --informe {cab} {hist} --toto {toto} --fincast {fc} --pilotos {b}/piloto_mt5_cabecera {b}/piloto_mt5_ampliacion {b}/piloto_toto_mt5_cabecera {f}/piloto_mt5_cabecera --destino docs/plans/current/execution/TS-00-BENCH-MT5/completo",
    ]


def _f(x):
    return f"{x:.9g}" if _numero(x) else "—"


def _tabla(L, columnas, filas):
    L += ["", "| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    L += ["| " + " | ".join(str(v) for v in fila) + " |" for fila in filas]
    L.append("")


def escribir(runs, repeticiones, destino, pilotos=None, totos=None, fincasts=None):
    todos = [_cargar(r) for r in list(runs) + list(totos or []) + list(fincasts or [])]
    pp = [_cargar(r) for r in (pilotos or [])]
    grupos = {}
    for r in todos:
        grupos.setdefault(r["meta"]["dataset"]["dataset_id"], []).append(r)
    nuevos = grupos.get(CABECERA, [])
    anteriores, ausentes = [], []
    for rol, run in REFERENCIAS.items():
        if Path(run, "meta.json").is_file():
            r = _cargar(run)
            if r["meta"]["dataset"]["dataset_id"] != ANTIGUO:
                raise ValueError(f"dataset incorrecto en referencia {run}")
            anteriores.append(r)
        else:
            ausentes.append(f"{rol}: {run}")
    series, descripciones, inventarios = {}, {}, {}
    for ds in (ANTIGUO, CABECERA, AMPLIACION):
        series[ds], descripciones[ds] = datos.cargar_dataset(rutas.dataset_dir(ds), banco.PRESETS[ds]["tabla"])
        inventarios[ds] = inventario(series[ds], banco.PRESETS[ds])
    for r in todos + anteriores:
        meta = r["meta"]
        ds = meta["dataset"]["dataset_id"]
        if ds in descripciones:
            if meta["dataset"]["dataset_hash"] != descripciones[ds]["dataset_hash"]:
                raise ValueError(f"dataset_hash del run distinto del dataset verificado: {r['run']}")
            for k, v in banco.PRESETS[ds].items():
                if meta["config"].get(k) != v:
                    raise ValueError(f"preset {k} distinto en {r['run']}")
            if meta["config"]["horizontes"] != list(banco.HORIZONTES) or meta["config"]["semilla"] != banco.SEMILLA:
                raise ValueError(f"horizontes/semilla distintos en {r['run']}")
    objetivos = [validar_objetivos(r, series[r["meta"]["dataset"]["dataset_id"]],
                                  banco.PRESETS[r["meta"]["dataset"]["dataset_id"]])
                 for r in todos + anteriores if r["meta"]["dataset"]["dataset_id"] in series]
    activos = sorted(series[CABECERA])
    antes, despues = revisar(anteriores, activos), revisar(nuevos, activos)
    cambios = {m: ("no evaluable" if "no evaluable" in (antes[m]["resultado"], despues[m]["resultado"])
                   else "cambia" if antes[m]["resultado"] != despues[m]["resultado"] else "no cambia") for m in MODELOS}
    rankings_antes, rankings_despues = clasificaciones(anteriores, activos), clasificaciones(nuevos, activos)
    sit = situacion(antes, despues, rankings_antes, rankings_despues)
    base = next((r for r in nuevos if "garch" in r["meta"]["config"]["modelos"]), None)
    claves = set()
    if base:
        claves = set(base["pred"][["instrument", "origen_ms"]].drop_duplicates().itertuples(index=False, name=None))
    dif = diferencial(series[ANTIGUO], series[CABECERA], banco.PRESETS[CABECERA], claves)
    ora = oraculo(base, rutas.dataset_dir(CABECERA)) if base and "EURUSD" in base["meta"]["config"]["activos"] else None
    ph = next((r for r in pp if r["meta"]["dataset"]["dataset_id"] == AMPLIACION), None)
    coste = presupuesto(ph, inventarios[AMPLIACION]) if ph else None
    piloto = any(r["meta"]["config"].get("max_origenes", 0) for r in todos)
    L = ["# TS-00-BENCH-MT5: cabecera y ampliación", "",
         f"Generado {datetime.now(timezone.utc).isoformat()}. Motor `{banco.MOTOR_COMMIT}`; semilla {banco.SEMILLA}; "
         "fecha de corte de datos **2026-11-01T00:00:00Z**; CPU, 2 hilos torch; sin red, HF_HUB_OFFLINE=1.", "",
         "**INFORME DE PRUEBA DESDE PILOTOS: no confirma umbrales ni sustituye las corridas completas.**" if piloto else
         "Informe de corridas completas. Los umbrales se evalúan sin modificarlos.", "",
         "D14/D15 · ISSUE-LAGO-FX-1D-CLOSE: la tabla anterior usaba close 00:00 UTC de yfinance; "
         "MT5 usa el cierre de sesión 17:00 NY. Los umbrales fijados el 2026-11-09 son provisionales hasta la tabla "
         "MT5 completa. Cabecera: misma ventana, inicio, fin, rejilla de fechas y horizontes; "
         "ampliación desde 2000: descriptiva, **no mueve umbrales**, solo HMM/GARCH/Chronos-2; Toto y FinCast excluidos.", "",
         "Los tres datasets son proxy de disponibilidad: ts es fecha de sesión a 00:00 UTC; available_at nulo "
         "y default_lag_ms=0 (disponible en ts+1 día). No prueba disponibilidad histórica real. "
         "Horizontes por barra, incluidas las barras antiguas de sábado/domingo; no se filtran.", "",
         "Comando de generación: `" + ".venv/Scripts/python -X utf8 scripts/banco_walkforward.py " + " ".join(sys.argv[1:]) + "`."]
    _tabla(L, ["dataset (proxy)", "dataset_hash SHA-256", "filas", "preset"],
           [(ds, d["dataset_hash"], d["filas"], str(banco.PRESETS[ds])) for ds, d in descripciones.items()])
    metricas_salida, limpias = [], []
    for ds in (CABECERA, AMPLIACION):
        L += [f"## {'Cabecera' if ds == CABECERA else 'Ampliación'} MT5 (proxy)"]
        partes = grupos.get(ds, [])
        if not partes:
            L += ["", "SALTADO: no se suministró corrida de esta tabla.", ""]
        esperados = {"hmm", "garch", "chronos2"} | ({"toto", "fincast"} if ds == CABECERA else set())
        presentes = {m for p in partes for m in p["meta"]["config"]["modelos"]}
        if esperados - presentes:
            L += ["", "SALTADO/no suministrado: " + ", ".join(sorted(esperados - presentes)) +
                  "; criterios correspondientes no evaluables. Consultar saltados y log del piloto si falta su venv.", ""]
        for r in partes:
            meta, pred = r["meta"], r["pred"]
            mods = meta["config"]["modelos"]
            L += ["", f"Corrida `{r['run']}`; modelos {mods}; cada={meta['config'].get('cada', 1)}; "
                  f"máximo por activo={meta['config'].get('max_origenes', 0)}; fallos={meta['fallos']}; "
                  f"SALTADOS={meta.get('saltados', {})}. SHA-256 predicciones `{meta['predicciones_sha256']}`."]
            L += ["", "Convergencia declarada: `" + json.dumps(meta.get("convergencia", {}), ensure_ascii=False) +
                  "`. Cruces de cuantiles conservados de SPRINT-01 (solo FinCast rechaza): `" +
                  json.dumps(meta.get("cruces_cuantiles", {}), ensure_ascii=False) + "`."]
            if "fincast" in mods:
                continue
            if mods == ["toto"]:
                rb = next((p for p in partes if "garch" in p["meta"]["config"]["modelos"]), None)
                pred = pd.concat([rb["pred"], pred], ignore_index=True) if rb else pred
                mods = ["hmm", "garch", "chronos2", "toto"]
            comun = _comunes(pred, mods)
            met = banco.metricas_tabla(comun, mods)
            metricas_salida.append(met.assign(dataset=ds, conjunto="toto_comunes" if "toto" in mods else "principal"))
            resumen = []
            for h in banco.HORIZONTES:
                g = met[met.h == h]
                piv = g.pivot(index="instrument", columns="modelo", values="crps")
                for m in mods:
                    gm = g[g.modelo == m]
                    rel = float((piv[m] / piv.garch).median()) if m in piv and "garch" in piv else None
                    resumen.append([h, m, len(gm), _f(gm.crps.median()), _f(rel), _f(gm.qlike.median()),
                                    f"{int((gm.kupiec_01_p < .05).sum())}/{int((gm.kupiec_99_p < .05).sum())}"])
            _tabla(L, ["h", "modelo", "activos", "CRPS mediana", "CRPS rel. GARCH", "QLIKE mediana", "Kupiec rechazos 1%/99%"], resumen)
        if any("fincast" in p["meta"]["config"]["modelos"] for p in partes):
            _, est, met = _unir(partes)
            limpias.append(met.assign(dataset=ds))
            L += ["### FinCast y bases: ventana limpia común", "",
                  "CRPS deciles nativos para todos; origen > 2025-08-27, comunes válidos. "
                  "FinCast: colas y banda **no aplica**; sólo C1 CRPS y QLIKE. "
                  "La selección condicionada a sus fallos está registrada en revision.json."]
            _tabla(L, ["h", "modelo", "activos", "CRPS deciles mediana", "QLIKE mediana"],
                   [(h, m, len(g), _f(g.crps_deciles.median()), _f(g.qlike.median()))
                    for (h, m), g in met.groupby(["h", "modelo"])])
        L += ["### Barras, fines de semana y orígenes válidos por par", "",
              "Validez antes de --cada/--max-origenes; omisiones referidas a toda la rejilla. "
              "El fin del preset limita los orígenes; los futuros se buscan en el dataset hasta el corte congelado."]
        cols = ["instrument", "barras", "primera_barra", "sabados", "domingos", "barras_antes_inicio", "origenes_validos",
                "primer_origen", "ultimo_origen", "sin_ventana", "sin_objetivo", "sin_barra_nueva"]
        _tabla(L, cols, [[r[c] for c in cols] for r in inventarios[ds]])
    L += ["## Revisión de umbrales de TS-00-OBJ", "",
          "Evaluación por código, sin mover umbrales. C1: ≤0,97 en ≥2 horizontes, ninguno >1,02. "
          "C2: rechazos Kupiec al 5% ≤10% en cada cola y horizonte. C3: P99 banda 1–99% ≤2×GARCH "
          "en cada horizonte, sobre los mismos orígenes comunes. CRPS rel. = mediana entre activos de los cocientes. "
          "Toto usa su submuestra con las bases; FinCast sólo CRPS deciles/QLIKE en limpia común. "
          "--cada 5 selecciona sobre orígenes válidos: la barra extra inicial puede adelantar la fase de "
          "la submuestra MT5 frente a la antigua; las bases se alinean a cada muestra sin reindexarla. "
          "Un activo/modelo/horizonte ausente o p-valor no finito deja el criterio no evaluable. "
          "Las cifras del piloto son provisionales y los tests tienen poca potencia."]
    if ausentes:
        L += ["", "Referencias ausentes (no evaluables): " + "; ".join(ausentes)]
    for etiqueta, resultados in (("Antigua (yfinance, proxy)", antes), ("MT5 cabecera (proxy)", despues)):
        L += [f"### {etiqueta}"]
        _tabla(L, ["modelo", "h", "n activos", "CRPS rel.", "≤0,97", "≤1,02", "Kupiec rechazos 1%/99%", "C2", "P99 banda/GARCH", "C3", "QLIKE"],
               [[m, r["h"], r["n_activos"], _f(r.get("crps_rel")), r["crps_097"], r["tope_102"],
                 "no aplica" if m == "fincast" else f"{r.get('rechazos_01', '—')}/{r.get('rechazos_99', '—')}",
                 r["c2"], _f(r.get("banda_rel")), r["c3"], _f(r.get("qlike"))]
                for m in MODELOS for r in resultados[m]["horizontes"]])
    _tabla(L, ["modelo", "C1 antigua → MT5", "C2 antigua → MT5", "C3 antigua → MT5", "conclusión antigua → MT5", "¿cambia conclusión?", "alcance"],
           [[m, *[antes[m][c] + " → " + despues[m][c] for c in ("c1", "c2", "c3", "resultado")], cambios[m], despues[m]["alcance"]] for m in MODELOS])
    L += ["Cambia la conclusión (pasa ↔ no pasa) de algún modelo: **" +
          ("sí" if "cambia" in cambios.values() else "no evaluable" if "no evaluable" in cambios.values() else "no") + "**.", ""]
    L += ["### Situación de partida", "",
          "Rango [mín,máx] entre horizontes; cambia si cruza 1,00/0,97 o cambia el orden en algún horizonte. "
          "Rangos de HMM/Chronos: principal FX; Toto: submuestra FX; FinCast: deciles limpios comunes. "
          "Órdenes calculados dentro de tres grupos comparables: principal CRPS21, submuestra Toto CRPS21 "
          "y limpia común CRPS deciles (FinCast sólo en esta última). "
          "Los rangos publicados en TS-00-OBJ (0,967–1,05; etc.) abarcaban también Binance y submuestras "
          "del informe SPRINT-01; aquí se recalcula exclusivamente la cabecera FX especificada. "
          "Estado calculado: **" + ("cambia" if sit["cambia"] else "no cambia"
          if all(v for r in sit["rangos"].values() for v in r.values()) else "no evaluable") + "**."]
    _tabla(L, ["modelo", "rango antiguo", "rango MT5"],
           [[m, str(sit["rangos"][m]["antiguo"]), str(sit["rangos"][m]["mt5"])] for m in MODELOS])
    L += ["Cruces: `" + json.dumps(sit["cruces"], ensure_ascii=False) + "`.", "",
          "Órdenes por horizonte: `" + json.dumps(sit["ordenes"], ensure_ascii=False) + "`.", "",
          "## Test diferencial de la fuente de datos", "",
          "Base de código fb11457: no cambian fórmulas, disponibilidad ni selección de orígenes. "
          "La única variación de datos es " + dif["explicacion"] + ". Estado de causas de orígenes: **" + dif["estado"] + "**. "
          "Se lista toda diferencia de validez en la rejilla y se marca si pertenece al piloto. "
          "--max-origenes limita inferencias, no la validez de la fuente contraria. "
          "Antes de inicio: 249 barras MT5 frente a 248 antiguas en cada par; el primer origen válido se adelanta un día."]
    ia, im = inventarios[ANTIGUO], inventarios[CABECERA]
    L += ["", f"Orígenes válidos totales: antigua {sum(r['origenes_validos'] for r in ia)}, "
          f"MT5 {sum(r['origenes_validos'] for r in im)}; "
          f"primeros válidos antiguos {sorted({r['primer_origen'] for r in ia if r['primer_origen']})}, "
          f"MT5 {sorted({r['primer_origen'] for r in im if r['primer_origen']})}."]
    _tabla(L, ["par", "fecha", "sólo en", "en piloto", "causa"],
           [[r["instrument"], r["fecha"], r["solo_en"], r["en_piloto"], r["causa"]] for r in dif["exclusivos"]])
    _tabla(L, ["h", "orígenes comunes del piloto", "mediana Δy pb", "mediana |Δy| pb", "máximo |Δy| pb"],
           [[r["h"], r["n"], _f(r["mediana_delta_pb"]), _f(r["mediana_abs_pb"]), _f(r["max_abs_pb"])] for r in dif["resumen_delta_y"]])
    L += ["Casos |Δy| > 5×mediana de |Δy| de ese par/h: revisión humana por la raíz, sin umbral de aceptación de Δy."]
    _tabla(L, ["par", "fecha", "h", "Δy pb", "mediana |Δy| par/h pb"],
           [[r["instrument"], r["fecha"], r["h"], _f(r["delta_y_pb"]), _f(r["mediana_abs_par_h_pb"])] for r in dif["extremos"]])
    L += ["Todos los Δy por par/fecha/h: diferencial.csv. No se atribuye causalidad individual a los valores extremos.", "",
          "## Oráculo independiente EURUSD h=1", "", "`" + json.dumps(ora, ensure_ascii=False) + "`", "",
          "## Medida de pilotos y presupuesto de ampliación"]
    _tabla(L, ["run", "modelo", "n", "CPU s/origen", "pared s/origen", "pared carga s", "pared total s"],
           [[r["run"], m, c["n"], _f(c["por_origen_s"]), _f(r["meta"].get("pared_modelos", {}).get(m, {}).get("por_origen_s")),
             _f(r["meta"].get("pared_carga_modelos_s")), _f(r["meta"].get("pared_total_s"))]
            for r in pp for m, c in r["meta"]["cpu"].items()])
    if coste:
        L += ["", f"Paso fijo elegido: **{coste['paso_dias']} días**. {coste['n_completo']} orígenes válidos × "
              f"(suma pared/modelo {sum(coste['pared_s_por_origen'].values()):.6f} + sobrecoste/origen {coste['sobrecoste_s_por_origen']:.6f}) "
              f"+ carga {coste['carga_s']:.3f} + lectura/verificación/preparación {coste['preparacion_s']:.3f} "
              f"= {_f(coste['estimada_s'])} s = {_f(coste['estimada_h'])} h. "
              f"≤2 h: **{coste['cabe_2h']}** por extrapolación de {coste['n_piloto']} orígenes; "
              "2 hilos torch, una corrida pesada cada vez. La raíz contrasta con la corrida real (si >2,5 h decide ella)."]
    L += ["## Invariantes y reproducibilidad"]
    for run in (repeticiones or []):
        r = _cargar(run)
        L += ["", "`" + r["run"] + "`. Comando: `" + r["meta"]["comando"] + "`.", "",
              "```text", "comparacion: " + json.dumps(r["meta"].get("comparacion", {}), ensure_ascii=False), "```",
              "SHA-256 canónico `" + r["meta"]["predicciones_sha256"] + "`."]
    L += ["", "## Órdenes exactas para la raíz (NO ejecutadas aquí)", "", "```powershell", *comandos(), "```", ""]
    revision = {"motor": banco.MOTOR_COMMIT, "semilla": banco.SEMILLA, "corte_datos": "2026-11-01T00:00:00Z",
                "piloto": piloto, "datasets": descripciones, "inventarios": inventarios,
                "antigua": antes, "mt5": despues,
                "cambios_conclusion": cambios, "situacion_partida": sit, "diferencial": dif, "oraculo": ora,
                "rankings_comparables": {"antiguos": rankings_antes, "mt5": rankings_despues},
                "presupuesto": coste, "referencias_ausentes": ausentes,
                "objetivos_verificados_con_parquet": objetivos,
                "referencias": [{"run": r["run"], "dataset_hash": r["meta"]["dataset"]["dataset_hash"],
                                  "predicciones_sha256": r["meta"]["predicciones_sha256"]} for r in anteriores]}
    for ds, partes in grupos.items():
        if any("fincast" in p["meta"]["config"]["modelos"] for p in partes):
            _, estado, _ = _unir(partes)
            revision.setdefault("cobertura_limpia", {})[ds] = estado
    p = Path(destino)
    p.mkdir(parents=True, exist_ok=True)
    (p / "informe.md").write_text("\n".join(L).rstrip() + "\n", encoding="utf-8")
    (p / "revision.json").write_text(json.dumps(revision, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    (p / "comandos_completos.ps1").write_text("\n".join(comandos()) + "\n", encoding="utf-8")
    pd.concat(metricas_salida, ignore_index=True).to_csv(p / "metricas.csv", index=False, float_format="%.17g")
    (pd.concat(limpias, ignore_index=True) if limpias else pd.DataFrame()).to_csv(p / "metricas_limpia.csv", index=False, float_format="%.17g")
    pd.DataFrame(dif["deltas"]).to_csv(p / "diferencial.csv", index=False, float_format="%.17g")
    hashes = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.iterdir()) if f.is_file() and f.name != "SHA256SUMS"}
    (p / "SHA256SUMS").write_text("\n".join(f"{v}  {k}" for k, v in hashes.items()) + "\n", encoding="utf-8")
    print(f"informe MT5: {p / 'informe.md'}; sha256 {hashes['informe.md']}; diferencial {dif['estado']}")
    return 2 if dif["estado"] == "BLOQUEADO" or (ora and not ora["coincide"]) or (coste and not coste["cabe_2h"]) else 0
