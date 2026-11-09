"""Cuadre de TI-12-MT5: velas de 1 m de MT5 agregadas a diario frente a dos fuentes diarias. No toca el terminal.

    .venv/Scripts/python -X utf8 scripts/cuadre_mt5.py --m1 DIR_M1 --d1 DIR_D1 --lago LAGO_OHLCV_1D.parquet [--salida DIR]
    .venv/Scripts/python -X utf8 scripts/cuadre_mt5.py --selftest

Entradas (solo lectura):
- `--m1`: una descarga del extractor (`extractor_mt5.py --descargar --periodos m1`) con su `manifest.json`.
- `--d1`: una descarga 1d del extractor (p. ej. E:/quantdesk-lab/data/mt5/continuo_1d_20261109) con su `manifest.json`.
- `--lago`: la tabla `lago_ohlcv_1d.parquet` (engine.market-history/v1, columnas instrument, ts_ms, open..close) de un
  dataset congelado (p. ej. E:/quantdesk-lab/datasets/TI-02-DATA/lago_cierre_c20261101).

Agregacion diaria: la MISMA regla que publica el publicador (`publicador_mt5_lib.nucleo.sesion_1d`, reutilizada, no
copiada): la vela de 1 m pertenece a la sesion D = fecha del servidor de su apertura (servidor = Nueva York + 7 h, asi que
D va de las 17:00 NY de D-1 a las 17:00 NY de D). open = open de la primera vela de 1 m, high/low = max/min, close = close
de la ultima. Un dia es COMPLETO en 1 m si empieza y acaba en el horario del broker para ese dia de la semana y no le
falta ningun minuto dentro (se decide sin mirar precios; ver `completitud`).

Comparaciones:
1. Contra el D1 de MT5 (misma fuente, mismos ticks Bid): diferencia en PUNTOS del simbolo en open, high, low y close.
   Tolerancia `TOL_D1_PUNTOS` (ver cuadre.md). Los dias incompletos se informan aparte y no cuentan como fallo.
2. Contra el FX diario del lago (yfinance; otra ventana diaria, otro proveedor): solo el cierre, en error relativo.
   - `cierre_sesion`: el cierre de la sesion de MT5 (17:00 NY) frente al cierre del lago del mismo dia D.
   - `cierre_corte`: el precio de MT5 (close de la ultima vela de 1 m cerrada) en la hora de corte UTC del lago, que se
     estima con los datos: la que minimiza el error mediano de todos los pares entre las candidatas `CORTES_H` (horas
     relativas a las 00:00 UTC de D, cada 15 min).
   Tolerancia relativa por par y dia: `K_RANGO` x rango diario mediano del par (high-low)/close de las sesiones
   completas de MT5 en la ventana. K_RANGO = 0,10 ~ raiz(15 min / 1 dia): el desplazamiento tipico del precio en el
   paso de la rejilla de cortes (ver cuadre.md).

Salida: <salida>/cuadre.json (todo, ordenado y sin marcas de la ejecucion salvo `generado_utc`) y <salida>/cuadre.md
(tablas por par). Codigo 0 si todos los dias completos cuadran con el D1 de MT5 dentro de tolerancia; 1 si no; 2 uso.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys

import numpy as np
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_env import LAB, LAB_ENV  # noqa: E402

os.environ.update(LAB_ENV)

from extractor_mt5_lib import hora as HR  # noqa: E402
from publicador_mt5_lib.nucleo import sesion_1d  # noqa: E402  (regla 1d del publicador: no se duplica)

RUNS = LAB + "/runs/TI-12-MT5/cuadre"
TMP = LAB + "/tmp/TI-12-MT5"
DIA_MS = 86_400_000
CAMPOS = ("open", "high", "low", "close")
TOL_D1_PUNTOS = 0  # mismo flujo de precios Bid: el D1 se construye con los mismos ticks que las velas de 1 m
K_RANGO = 0.10  # tolerancia del lago: fraccion del rango diario mediano del par (~ raiz(15/1440), paso de la rejilla)
CORTES_H = tuple(x / 4 for x in range(-12 * 4, 30 * 4 + 1))  # de D-1 12:00 a D+1 06:00 UTC, cada 15 min
CORTE_MAX_RANCIO_MS = 4 * DIA_MS  # un precio "en el corte" no puede venir de una vela mas vieja (fin de semana largo)


# ---------------------------------------------------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------------------------------------------------

def leer_descarga(directorio: str, periodo: str) -> dict:
    """base -> {simbolo, columnas numpy} de una descarga del extractor (solo velas del periodo pedido)."""
    with open(os.path.join(directorio, "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    out = {}
    for e in man["ficheros"]:
        if e["periodo"] != periodo or not e.get("fichero"):
            continue
        t = pq.read_table(os.path.join(directorio, e["fichero"]),
                          columns=["time_servidor", "ts_utc_ms", "open", "high", "low", "close"])
        out[e["base"]] = {"simbolo": e["simbolo"], **{c: t.column(c).to_numpy() for c in t.column_names}}
    return {"manifest": man, "series": out}


def leer_lago(ruta: str) -> dict:
    """instrument -> {ts_ms, close, ...} del lago (engine.market-history/v1, ohlcv/v1), ordenado por ts_ms."""
    t = pq.read_table(ruta, columns=["instrument", "ts_ms", "open", "high", "low", "close"])
    ins = np.asarray(t.column("instrument").to_pylist(), dtype=object)
    cols = {c: t.column(c).to_numpy() for c in ("ts_ms", "open", "high", "low", "close")}
    out = {}
    for nombre in sorted(set(ins)):
        m = ins == nombre
        orden = np.argsort(cols["ts_ms"][m], kind="stable")
        out[nombre] = {c: v[m][orden] for c, v in cols.items()}
    return out


def punto_de_precios(*arrays, max_digitos: int = 8) -> float:
    """Punto del simbolo inferido de los precios: el menor 10^-k con el que todos son enteros (MT5 da precios redondeados
    a `digits`). Evita depender del inventario; cuadre.md lo contrasta con el `punto` del inventario."""
    v = np.concatenate([np.asarray(a, dtype=np.float64) for a in arrays])
    for k in range(max_digitos + 1):
        x = v * 10 ** k
        if np.all(np.abs(x - np.round(x)) < 1e-6):
            return 10.0 ** -k
    return 10.0 ** -max_digitos


# ---------------------------------------------------------------------------------------------------------------------
# Agregacion diaria (regla del publicador)
# ---------------------------------------------------------------------------------------------------------------------

def diario(s: dict, regla: HR.Regla) -> dict:
    """Velas (de 1 m o 1d) -> una fila por sesion D con la regla del publicador. `dia_ms` = 00:00 UTC de D (el `ts`
    publicado); `apertura_ms`/`cierre_ms` = inicio y fin reales de la sesion (17:00 NY de D-1 y de D); `primera_ms` y
    `ultima_ms` = apertura UTC de la primera y de la ultima vela del dia; `n` = velas."""
    ts_dia, cierre = sesion_1d(s["time_servidor"], regla)
    if ts_dia.size == 0:
        return {k: np.zeros(0) for k in ("dia_ms", "open", "high", "low", "close", "n", "primera_ms", "ultima_ms",
                                         "apertura_ms", "cierre_ms")}
    if np.any(np.diff(s["ts_utc_ms"]) <= 0):
        raise ValueError("velas fuera de orden o repetidas")
    corte = np.nonzero(np.diff(ts_dia) != 0)[0] + 1
    ini = np.concatenate([[0], corte])
    fin = np.concatenate([corte, [ts_dia.size]]) - 1
    dia = ts_dia[ini]
    apertura = regla.servidor_a_utc((dia // DIA_MS) * 86400)[0] * 1000  # 00:00 del servidor = 17:00 NY de D-1
    return {"dia_ms": dia, "open": s["open"][ini], "high": np.maximum.reduceat(s["high"], ini),
            "low": np.minimum.reduceat(s["low"], ini), "close": s["close"][fin], "n": fin - ini + 1,
            "primera_ms": s["ts_utc_ms"][ini], "ultima_ms": s["ts_utc_ms"][fin], "apertura_ms": apertura,
            "cierre_ms": cierre[ini]}


def emparejar(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Indices de los dias comunes (a y b crecientes, sin repetidos)."""
    _, ia, ib = np.intersect1d(a, b, assume_unique=True, return_indices=True)
    return ia, ib


def _moda(x: np.ndarray) -> int:
    v, n = np.unique(x, return_counts=True)
    return int(v[np.argmax(n)])


def completitud(m: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    """Dias completos en 1 m, sin mirar precios (para no hacer circular el cuadre).
    Horario del broker por dia de la semana = la moda, en la ventana, del primer y del ultimo minuto del servidor con vela
    (en el terminal real: 00:00-23:58 de lunes a jueves y 00:00-23:56 el viernes). Un dia es COMPLETO si empieza y acaba
    en ese horario y no le falta ningun minuto dentro: n = ultimo - primero + 1. Devuelve (completo, velas que faltan
    respecto del horario, horario)."""
    if m["dia_ms"].size == 0:
        return np.zeros(0, dtype=bool), np.zeros(0, dtype=np.int64), {}
    primero = (m["primera_ms"] - m["apertura_ms"]) // 60_000
    ultimo = (m["ultima_ms"] - m["apertura_ms"]) // 60_000
    dsem = (m["dia_ms"] // DIA_MS + 3) % 7  # 0 = lunes
    horario = {int(w): (_moda(primero[dsem == w]), _moda(ultimo[dsem == w])) for w in np.unique(dsem)}
    a = np.array([horario[int(w)][0] for w in dsem])
    b = np.array([horario[int(w)][1] for w in dsem])
    completo = (primero == a) & (ultimo == b) & (m["n"] == b - a + 1)
    faltan = np.maximum(0, (b - a + 1) - m["n"])
    return completo, faltan, horario


# ---------------------------------------------------------------------------------------------------------------------
# Cuadres
# ---------------------------------------------------------------------------------------------------------------------

def _fecha(ms) -> str:
    return dt.datetime.fromtimestamp(int(ms) / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")


def cuadre_d1(m: dict, d1: dict, punto: float, tol_puntos: int = TOL_D1_PUNTOS) -> dict:
    i_m, i_d = emparejar(m["dia_ms"], d1["dia_ms"])
    comp_todos, faltan_todos, horario = completitud(m)
    completo, faltan = comp_todos[i_m], faltan_todos[i_m]
    dif = {c: np.rint(np.abs(m[c][i_m] - d1[c][i_d]) / punto).astype(np.int64) for c in CAMPOS}
    peor = np.max(np.stack([dif[c] for c in CAMPOS]), axis=0) if i_m.size else np.zeros(0, dtype=np.int64)
    dentro = peor <= tol_puntos
    r = {"punto": punto, "tol_puntos": tol_puntos, "dias_m1": int(m["dia_ms"].size), "dias_d1_en_rango": None,
         "dias_comparados": int(i_m.size), "dias_completos": int(completo.sum()),
         "dias_incompletos": int((~completo).sum()),
         "completos_dentro": int((dentro & completo).sum()), "incompletos_dentro": int((dentro & ~completo).sum()),
         "max_puntos": {c: int(dif[c].max()) if dif[c].size else None for c in CAMPOS},
         "max_puntos_completos": {c: int(dif[c][completo].max()) if completo.any() else None for c in CAMPOS},
         "mediana_puntos": {c: float(np.median(dif[c])) if dif[c].size else None for c in CAMPOS},
         "fallos_completos": [_fecha(m["dia_ms"][i_m[k]]) for k in np.nonzero(completo & ~dentro)[0]],
         "horario_servidor": {["lun", "mar", "mie", "jue", "vie", "sab", "dom"][w]: f"{a // 60:02d}:{a % 60:02d}-{b // 60:02d}:{b % 60:02d}"
                              for w, (a, b) in sorted(horario.items())},
         "incompletos": [{"dia": _fecha(m["dia_ms"][i_m[k]]), "velas_1m": int(m["n"][i_m[k]]),
                          "velas_que_faltan": int(faltan[k]), "max_puntos": int(peor[k]),
                          "puntos_ohlc": [int(dif[c][k]) for c in CAMPOS]} for k in np.nonzero(~completo)[0]]}
    lo, hi = m["dia_ms"].min() if m["dia_ms"].size else 0, m["dia_ms"].max() if m["dia_ms"].size else -1
    en_rango = (d1["dia_ms"] >= lo) & (d1["dia_ms"] <= hi)
    r["dias_d1_en_rango"] = int(en_rango.sum())
    r["dias_d1_sin_m1"] = [_fecha(x) for x in np.setdiff1d(d1["dia_ms"][en_rango], m["dia_ms"])]
    r["completo_mascara"] = completo
    r["i_m"] = i_m
    return r


def precio_en(s: dict, instantes_ms: np.ndarray) -> np.ndarray:
    """Precio de MT5 en cada instante: close de la ultima vela de 1 m CERRADA (apertura + 60 s <= instante). NaN si no
    hay ninguna o si es mas vieja que `CORTE_MAX_RANCIO_MS`."""
    fin = s["ts_utc_ms"] + 60_000
    k = np.searchsorted(fin, instantes_ms, side="right") - 1
    ok = k >= 0
    out = np.full(instantes_ms.shape, np.nan)
    out[ok] = s["close"][k[ok]]
    rancio = ok & (instantes_ms - fin[np.maximum(k, 0)] > CORTE_MAX_RANCIO_MS)
    out[rancio] = np.nan
    return out


def errores_lago(s: dict, m: dict, completos_dia_ms: np.ndarray, lago: dict, corte_h: float | None) -> dict:
    """Error relativo |ln(lago / mt5)| del cierre en los dias completos de MT5 que tambien estan en el lago. Con
    `corte_h` None se usa el cierre de la sesion de MT5 (17:00 NY); si no, el precio de MT5 en 00:00 UTC de D + corte_h."""
    _, i_l, _ = np.intersect1d(lago["ts_ms"], completos_dia_ms, assume_unique=True, return_indices=True)
    dias = lago["ts_ms"][i_l]
    if corte_h is None:
        i_m = np.searchsorted(m["dia_ms"], dias)
        mt5 = m["close"][i_m]
    else:
        mt5 = precio_en(s, dias + int(round(corte_h * 3_600_000)))
    err = np.abs(np.log(lago["close"][i_l] / mt5))
    ok = np.isfinite(err)
    return {"dias_ms": dias[ok], "err": err[ok]}


def mejor_corte(series: dict, diarios: dict, completos: dict, lago: dict) -> tuple[float, list]:
    """Hora de corte UTC (relativa a las 00:00 de D) que minimiza la mediana del error del cierre, todos los pares a la
    vez. Devuelve (corte, curva [(corte_h, mediana)])."""
    curva = []
    for c in CORTES_H:
        e = [errores_lago(series[b], diarios[b], completos[b], lago[b], c)["err"] for b in sorted(series) if b in lago]
        e = np.concatenate(e) if e else np.zeros(0)
        curva.append((c, float(np.median(e)) if e.size else float("inf")))
    return min(curva, key=lambda x: (x[1], abs(x[0])))[0], curva


def ohl_dia_utc(s: dict, completos_dia_ms: np.ndarray, lago: dict) -> dict:
    """Evidencia de la ventana del lago: open, high y low del lago frente a MT5 agregado sobre el dia UTC [D 00:00,
    D+1 00:00) (open = open de la primera vela de 1 m del dia UTC). Solo dias completos de MT5. Errores relativos."""
    _, i_l, _ = np.intersect1d(lago["ts_ms"], completos_dia_ms, assume_unique=True, return_indices=True)
    out = {c: [] for c in ("open", "high", "low")}
    for i in i_l:
        k0, k1 = np.searchsorted(s["ts_utc_ms"], [lago["ts_ms"][i], lago["ts_ms"][i] + DIA_MS])
        if k1 <= k0:
            continue
        out["open"].append(abs(np.log(lago["open"][i] / s["open"][k0])))
        out["high"].append(abs(np.log(lago["high"][i] / s["high"][k0:k1].max())))
        out["low"].append(abs(np.log(lago["low"][i] / s["low"][k0:k1].min())))
    return {c: np.asarray(v, dtype=np.float64) for c, v in out.items()}


def resumen_err(err: np.ndarray, tol: float) -> dict:
    return {"dias": int(err.size), "dentro": int((err <= tol).sum()),
            "proporcion": round(float((err <= tol).mean()), 4) if err.size else None,
            "mediana_pb": round(float(np.median(err)) * 1e4, 2) if err.size else None,
            "p90_pb": round(float(np.quantile(err, 0.9)) * 1e4, 2) if err.size else None,
            "max_pb": round(float(err.max()) * 1e4, 2) if err.size else None}


# ---------------------------------------------------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------------------------------------------------

def cuadrar(m1_dir: str, d1_dir: str, lago_ruta: str, regla: HR.Regla, k_rango: float = K_RANGO) -> dict:
    m1, d1 = leer_descarga(m1_dir, "m1"), leer_descarga(d1_dir, "d1")
    lago = leer_lago(lago_ruta)
    bases = sorted(m1["series"])
    diarios, completos, res = {}, {}, {}
    for b in bases:
        s = m1["series"][b]
        if b not in d1["series"]:
            raise ValueError(f"{b}: no esta en la descarga D1 {d1_dir}")
        m = diario(s, regla)
        d = diario(d1["series"][b], regla)
        punto = punto_de_precios(s["open"], s["high"], s["low"], s["close"], d["open"], d["close"])
        r = cuadre_d1(m, d, punto)
        comp = r.pop("completo_mascara")
        i_m = r.pop("i_m")
        diarios[b], completos[b] = m, m["dia_ms"][i_m[comp]]
        idx = i_m[comp]
        rango = (m["high"][idx] - m["low"][idx]) / m["close"][idx]
        r["rango_diario_mediano_pb"] = round(float(np.median(rango)) * 1e4, 2) if idx.size else None
        res[b] = {"simbolo": m1["series"][b]["simbolo"], "d1": r}
    corte, curva = mejor_corte(m1["series"], diarios, completos, lago)
    for b in bases:
        tol = k_rango * res[b]["d1"]["rango_diario_mediano_pb"] / 1e4 if res[b]["d1"]["rango_diario_mediano_pb"] else 0.0
        if b not in lago:
            res[b]["lago"] = None
            continue
        res[b]["lago"] = {"tol_pb": round(tol * 1e4, 2)}
        for nombre, c in (("cierre_sesion", None), ("cierre_corte", corte)):
            e = errores_lago(m1["series"][b], diarios[b], completos[b], lago[b], c)
            res[b]["lago"][nombre] = resumen_err(e["err"], tol)
            if nombre == "cierre_corte":
                peores = np.argsort(-e["err"], kind="stable")[:3]
                res[b]["lago"]["peores_corte"] = [{"dia": _fecha(e["dias_ms"][k]), "err_pb": round(float(e["err"][k]) * 1e4, 2)}
                                                  for k in peores]
        ohl = ohl_dia_utc(m1["series"][b], completos[b], lago[b])
        res[b]["lago"]["ohl_dia_utc"] = {c: resumen_err(v, tol) for c, v in ohl.items()}
        en_rango = (lago[b]["ts_ms"] >= diarios[b]["dia_ms"].min()) & (lago[b]["ts_ms"] <= diarios[b]["dia_ms"].max())
        res[b]["lago"]["dias_lago_en_rango"] = int(en_rango.sum())
    tot = agregado(res)
    return {"tarea": "TI-12-MT5", "entradas": {"m1": {"dir": m1_dir, "hash_conjunto": m1["manifest"]["hash_conjunto"],
                                                      "parametros": m1["manifest"]["parametros"]},
                                               "d1": {"dir": d1_dir, "hash_conjunto": d1["manifest"]["hash_conjunto"]},
                                               "lago": {"ruta": lago_ruta}},
            "regla": regla.nombre, "tol_d1_puntos": TOL_D1_PUNTOS, "k_rango": k_rango, "corte_lago_h": corte,
            "curva_corte": [[c, round(v * 1e4, 3)] for c, v in curva], "pares": res, "agregado": tot}


def agregado(res: dict) -> dict:
    t = {"pares": len(res), "dias_comparados_d1": 0, "dias_completos": 0, "completos_dentro_d1": 0,
         "dias_incompletos": 0, "incompletos_dentro_d1": 0, "lago_dias": 0, "lago_dentro_sesion": 0,
         "lago_dentro_corte": 0}
    for r in res.values():
        t["dias_comparados_d1"] += r["d1"]["dias_comparados"]
        t["dias_completos"] += r["d1"]["dias_completos"]
        t["completos_dentro_d1"] += r["d1"]["completos_dentro"]
        t["dias_incompletos"] += r["d1"]["dias_incompletos"]
        t["incompletos_dentro_d1"] += r["d1"]["incompletos_dentro"]
        if r.get("lago"):
            t["lago_dias"] += r["lago"]["cierre_corte"]["dias"]
            t["lago_dentro_sesion"] += r["lago"]["cierre_sesion"]["dentro"]
            t["lago_dentro_corte"] += r["lago"]["cierre_corte"]["dentro"]
    for c in ("open", "high", "low"):
        t[f"lago_dentro_{c}_dia_utc"] = sum(r["lago"]["ohl_dia_utc"][c]["dentro"] for r in res.values() if r.get("lago"))
    t["d1_ok"] = t["completos_dentro_d1"] == t["dias_completos"] and t["dias_completos"] > 0
    return t


def hhmm(corte_h: float) -> str:
    dia = "D-1 " if corte_h < 0 else ("D+1 " if corte_h >= 24 else "D ")
    x = corte_h % 24
    return f"{dia}{int(x):02d}:{int(round((x % 1) * 60)):02d} UTC"


def texto_md(doc: dict) -> str:
    L = [f"Corte del lago estimado: {hhmm(doc['corte_lago_h'])}. Tolerancia D1: {doc['tol_d1_puntos']} puntos. "
         f"Tolerancia del lago: {doc['k_rango']} x rango diario mediano.", "",
         "| Par | Dias D1 | Completos | Dentro D1 | Incompletos (dentro) | Max pts O/H/L/C (completos) | Max pts (todos) | "
         "Rango med. (pb) | Tol. lago (pb) | Lago dias | Sesion dentro | Sesion med/max (pb) | Corte dentro | "
         "Corte med/max (pb) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b, r in doc["pares"].items():
        d, lg = r["d1"], r["lago"]
        mc = "/".join(str(d["max_puntos_completos"][c]) for c in CAMPOS)
        mt = "/".join(str(d["max_puntos"][c]) for c in CAMPOS)
        if lg:
            s, c = lg["cierre_sesion"], lg["cierre_corte"]
            lago_txt = (f"{lg['tol_pb']} | {c['dias']} | {s['dentro']} ({s['proporcion']:.0%}) | {s['mediana_pb']}/{s['max_pb']} | "
                        f"{c['dentro']} ({c['proporcion']:.0%}) | {c['mediana_pb']}/{c['max_pb']}")
        else:
            lago_txt = "- | - | - | - | - | -"
        L.append(f"| {b} | {d['dias_comparados']} | {d['dias_completos']} | {d['completos_dentro']} | {d['dias_incompletos']} ({d['incompletos_dentro']}) | "
                 f"{mc} | {mt} | {d['rango_diario_mediano_pb']} | {lago_txt} |")
    t = doc["agregado"]
    L += ["", f"Total: {t['pares']} pares; D1: {t['completos_dentro_d1']}/{t['dias_completos']} dias completos dentro "
              f"({t['dias_incompletos']} incompletos aparte, {t['incompletos_dentro_d1']} de ellos dentro; de {t['dias_comparados_d1']} comparados); lago: "
              f"{t['lago_dentro_sesion']}/{t['lago_dias']} con el cierre de sesion y {t['lago_dentro_corte']}/{t['lago_dias']} "
              f"con el corte estimado. Open/high/low del lago frente al dia UTC [D 00:00, D+1 00:00) de MT5 dentro de la "
              f"misma tolerancia: {t['lago_dentro_open_dia_utc']}/{t['lago_dentro_high_dia_utc']}/"
              f"{t['lago_dentro_low_dia_utc']} de {t['lago_dias']}."]
    return "\n".join(L) + "\n"


def escribir(doc: dict, salida: str) -> None:
    os.makedirs(salida, exist_ok=True)
    for nombre, texto in (("cuadre.json", json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=1) + "\n"),
                          ("cuadre.md", texto_md(doc))):
        ruta = os.path.join(salida, nombre)
        with open(ruta + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        os.replace(ruta + ".tmp", ruta)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(description="Cuadre 1 m -> diario de MT5 frente al D1 de MT5 y al lago (TI-12-MT5)")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--m1")
    p.add_argument("--d1")
    p.add_argument("--lago")
    p.add_argument("--salida")
    p.add_argument("--regla", default=HR.REGLA_DEFECTO)
    a = p.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.m1 and a.d1 and a.lago):
        print("BLOQUEADO: hacen falta --m1, --d1 y --lago")
        return 2
    doc = cuadrar(a.m1, a.d1, a.lago, HR.regla_desde_texto(a.regla))
    doc["generado_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    salida = a.salida or os.path.join(RUNS, dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    escribir(doc, salida)
    print(texto_md(doc), end="")
    print(f"cuadre: {salida}")
    return 0 if doc["agregado"]["d1_ok"] else 1


# ---------------------------------------------------------------------------------------------------------------------
# Selftest (sin terminal: datos sinteticos con la forma de las descargas del extractor)
# ---------------------------------------------------------------------------------------------------------------------

def _sintetico(regla: HR.Regla, dias: list[dt.date], semilla: int = 7, punto: float = 1e-5):
    """m1 de una serie FX sintetica (sesiones completas, de 17:00 NY de D-1 a 17:00 NY de D) y su D1 exacto."""
    rng = np.random.default_rng(semilla)
    filas_s, o, h, lo, c = [], [], [], [], []
    precio = 1.1
    for d in dias:
        s0 = (d - dt.date(1970, 1, 1)).days * 86400
        for k in range(1440):
            ap = precio
            pasos = np.round(rng.normal(0, 3, 4)).astype(int) * punto
            camino = ap + np.cumsum(pasos)
            cie = round(float(camino[-1]), 5)
            filas_s.append(s0 + 60 * k)
            o.append(ap)
            h.append(round(max(ap, float(camino.max())), 5))
            lo.append(round(min(ap, float(camino.min())), 5))
            c.append(cie)
            precio = cie
    s = np.array(filas_s, dtype=np.int64)
    m1 = {"time_servidor": s, "ts_utc_ms": regla.servidor_a_utc(s)[0] * 1000, "open": np.array(o), "high": np.array(h),
          "low": np.array(lo), "close": np.array(c)}
    agg = diario(m1, regla)
    sd = np.array([(d - dt.date(1970, 1, 1)).days * 86400 for d in dias], dtype=np.int64)
    d1 = {"time_servidor": sd, "ts_utc_ms": regla.servidor_a_utc(sd)[0] * 1000, "open": agg["open"].copy(),
          "high": agg["high"].copy(), "low": agg["low"].copy(), "close": agg["close"].copy()}
    return m1, d1


def _escribir_descarga(directorio: str, periodo: str, series: dict) -> None:
    import pyarrow as pa

    os.makedirs(directorio, exist_ok=True)
    ficheros = []
    for base, s in series.items():
        nombre = f"{base}__{periodo}.parquet"
        pq.write_table(pa.table({k: s[k] for k in ("time_servidor", "ts_utc_ms", "open", "high", "low", "close")}),
                       os.path.join(directorio, nombre))
        ficheros.append({"simbolo": base, "base": base, "periodo": periodo, "fichero": nombre})
    with open(os.path.join(directorio, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"hash_conjunto": f"sha256:{periodo}-sintetico", "parametros": {"periodos": [periodo]},
                   "ficheros": ficheros}, f)


def selftest() -> int:
    regla = HR.regla_desde_texto("ny+7")
    # Tres semanas con el cambio de hora de EE. UU. (domingo 1-nov-2026) en medio: sesiones del 19-oct al 6-nov.
    dias = [dt.date(2026, 10, 19) + dt.timedelta(days=k) for k in range(19)]
    dias = [d for d in dias if d.weekday() < 5]

    # 1. La regla de agregacion es la del publicador: dia = fecha del servidor; sesion = 17:00 NY de D-1 a 17:00 NY de D.
    m1, d1 = _sintetico(regla, dias)
    agg = diario(m1, regla)
    assert [_fecha(x) for x in agg["dia_ms"]] == [x.isoformat() for x in dias], agg["dia_ms"]
    ap = {_fecha(d): HR.iso(int(x)) for d, x in zip(agg["dia_ms"], agg["apertura_ms"])}
    assert ap["2026-10-30"] == "2026-10-29T21:00:00.000Z" and ap["2026-11-02"] == "2026-11-01T22:00:00.000Z", ap
    cie = {_fecha(d): HR.iso(int(x)) for d, x in zip(agg["dia_ms"], agg["cierre_ms"])}
    assert cie["2026-10-30"] == "2026-10-30T21:00:00.000Z" and cie["2026-11-02"] == "2026-11-02T22:00:00.000Z", cie
    assert np.all(agg["n"] == 1440) and np.all(agg["primera_ms"] == agg["apertura_ms"])
    ts_pub, _ = sesion_1d(m1["time_servidor"], regla)  # la funcion del publicador, la misma que usa `diario`
    assert set(ts_pub.tolist()) == set(agg["dia_ms"].tolist())
    print("ok  agregacion con la regla 1d del publicador (cambio de hora incluido)")

    # 2. Cuadre exacto contra su D1; un dia sin su primera vela y otro sin la vela de su maximo: incompletos, con las
    #    velas que faltan y la diferencia que explican.
    p = punto_de_precios(m1["open"], m1["close"])
    assert abs(p - 1e-5) < 1e-12, p
    dd1 = diario(d1, regla)
    r = cuadre_d1(agg, dd1, p)
    assert r["dias_completos"] == 15 and r["completos_dentro"] == 15 and r["max_puntos"]["high"] == 0, r
    assert r["horario_servidor"]["lun"] == "00:00-23:59", r["horario_servidor"]
    quita = np.ones(m1["time_servidor"].size, dtype=bool)
    k_vie = [_fecha(x) for x in agg["dia_ms"]].index("2026-10-30")
    k_mar = [_fecha(x) for x in agg["dia_ms"]].index("2026-11-03")
    i0 = int(np.searchsorted(m1["ts_utc_ms"], agg["primera_ms"][k_vie]))
    quita[i0] = False  # viernes 30 sin su primera vela
    i3 = int(np.searchsorted(m1["ts_utc_ms"], agg["primera_ms"][k_mar]))
    i_max = i3 + 1 + int(np.argmax(m1["high"][i3 + 1:i3 + 1439]))
    quita[i_max] = False  # martes 3 sin la vela de su maximo (interior)
    m1b = {k: v[quita] for k, v in m1.items()}
    rb = cuadre_d1(diario(m1b, regla), dd1, p)
    inc = {x["dia"]: x for x in rb["incompletos"]}
    assert set(inc) == {"2026-10-30", "2026-11-03"} and rb["dias_completos"] == 13 and not rb["fallos_completos"], rb
    assert inc["2026-10-30"]["velas_que_faltan"] == 1 and inc["2026-11-03"]["velas_que_faltan"] == 1, inc
    resto = np.delete(m1["high"][i3:i3 + 1440], i_max - i3)
    esperado = int(round((m1["high"][i_max] - max(resto.max(), 0)) / p))
    assert inc["2026-11-03"]["puntos_ohlc"][1] == esperado, (inc, esperado)
    print(f"ok  cuadre D1: exacto en sesiones completas; 2 dias con una vela menos = incompletos (high -{esperado} pts)")

    # 3. Precio en el corte y estimacion del corte del lago: un lago que cierra a las 23:00 UTC de D (sintetico).
    corte_real = 23.0
    dias_ms = agg["dia_ms"]
    lago = {"ts_ms": dias_ms.copy(), "close": precio_en(m1, dias_ms + int(corte_real * 3_600_000)),
            "open": agg["open"], "high": agg["high"], "low": agg["low"]}
    assert np.all(np.isfinite(lago["close"]))
    completos = dias_ms
    c, curva = mejor_corte({"X": m1}, {"X": agg}, {"X": completos}, {"X": lago})
    assert c == corte_real, (c, curva[:3])
    e = errores_lago(m1, agg, completos, lago, c)
    assert e["err"].size == len(dias) and float(e["err"].max()) == 0.0
    t = precio_en(m1, np.array([int(m1["ts_utc_ms"][0]) - 1, int(m1["ts_utc_ms"][5]) + 60_000], dtype=np.int64))
    assert np.isnan(t[0]) and t[1] == m1["close"][5], t
    print(f"ok  precio en el corte y corte del lago estimado ({hhmm(c)})")

    # 4. De punta a punta con ficheros: dos pares, uno sin lago; salida 0 y el informe se escribe.
    raiz = os.path.join(TMP, f"selftest_cuadre_{os.getpid()}")
    try:
        m1y, d1y = _sintetico(regla, dias, semilla=11)
        _escribir_descarga(os.path.join(raiz, "m1"), "m1", {"EURUSD": m1, "USDJPY": m1y})
        _escribir_descarga(os.path.join(raiz, "d1"), "d1", {"EURUSD": d1, "USDJPY": d1y})
        import pyarrow as pa

        pq.write_table(pa.table({"instrument": ["EURUSD"] * len(dias), "ts_ms": lago["ts_ms"], "open": lago["open"],
                                 "high": lago["high"], "low": lago["low"], "close": lago["close"]}),
                       os.path.join(raiz, "lago.parquet"))
        cod = main(["--m1", os.path.join(raiz, "m1"), "--d1", os.path.join(raiz, "d1"), "--lago",
                    os.path.join(raiz, "lago.parquet"), "--salida", os.path.join(raiz, "out")])
        assert cod == 0, cod
        with open(os.path.join(raiz, "out", "cuadre.json"), encoding="utf-8") as f:
            doc = json.load(f)
        assert doc["pares"]["USDJPY"]["lago"] is None and doc["pares"]["EURUSD"]["lago"]["cierre_corte"]["dentro"] == len(dias)
        assert doc["agregado"]["d1_ok"] and doc["corte_lago_h"] == corte_real
        # un D1 con un close distinto en un dia completo -> salida 1
        d1z = {k: v.copy() for k, v in d1.items()}
        d1z["high"][2] += 5 * 1e-5
        _escribir_descarga(os.path.join(raiz, "d1z"), "d1", {"EURUSD": d1z, "USDJPY": d1y})
        cod = main(["--m1", os.path.join(raiz, "m1"), "--d1", os.path.join(raiz, "d1z"), "--lago",
                    os.path.join(raiz, "lago.parquet"), "--salida", os.path.join(raiz, "out2")])
        assert cod == 1, cod
    finally:
        shutil.rmtree(raiz, ignore_errors=True)
    print("ok  de punta a punta (salida 0; un high distinto en un dia completo da salida 1)")
    print("selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
