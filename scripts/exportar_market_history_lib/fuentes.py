"""Lectura de las fuentes del exportador: datasets de Binance de TI-13-PUB y volcado crudo del lago (descarga_lago.py).

Cada cargador devuelve un `origen`: {"nombre", "fuente" (procedencia con hashes), "universo" (texto D-07), "tablas": [...]}. Cada
tabla trae el DataFrame sin limpiar y lo que el cargador sabe (cuentas de carga, `date` frente a `_ts`, justificacion de la
disponibilidad); la limpieza y el corte los hace `limpieza.py`.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .limpieza import nuevo_contador

INTERVALOS_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "4h": 14_400_000,
                 "1d": 86_400_000, "1w": 604_800_000}
ESQUEMA_VOLCADO = "ti-02-data.lago-crudo/v1"
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
MS_DIA = 86_400_000
BINANCE = {"1d": "binance__klines_1d", "1h": "binance__klines_1h"}
SERIE_BINANCE = re.compile(r"^(?P<ds>binance__klines_(?P<iv>[0-9a-z]+))/(?P<simbolo>[A-Z0-9]+)-(?P<iv2>[0-9a-z]+)$")
COLUMNAS_BINANCE = ["series_id", "ts", "open", "high", "low", "close", "volume"]


def sha256_fichero(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def iso_ms(ms: int) -> str:
    return (EPOCH + timedelta(milliseconds=int(ms))).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------------------------------------------------
# Binance (TI-13-PUB)
# ---------------------------------------------------------------------------------------------------------------------

def cargar_binance(raiz: str) -> dict:
    """Velas spot de Binance 1d y 1h de `datasets/TI-13-PUB`. Una tabla ohlcv/v1 por intervalo."""
    tablas, fuentes, universo = [], [], {}
    for iv, nombre in BINANCE.items():
        d = os.path.join(raiz, nombre)
        with open(os.path.join(d, "manifest.json"), encoding="utf-8") as f:
            man = json.load(f)
        partes = []
        for fich in man["ficheros"]:
            ruta = os.path.join(d, fich["ruta"])
            if sha256_fichero(ruta) != fich["sha256"]:
                raise ValueError(f"{ruta}: el SHA-256 no coincide con el de manifest.json de TI-13-PUB")
            t = pq.read_table(ruta, columns=COLUMNAS_BINANCE)
            tipo = t.schema.field("ts").type
            if not pa.types.is_timestamp(tipo) or tipo.unit != "ms":
                raise ValueError(f"{ruta}: se esperaba ts timestamp[ms], hay {tipo}")
            df = t.to_pandas()
            df["ts_ms"] = t.column("ts").cast(pa.int64()).to_numpy()
            partes.append(df)
        df = pd.concat(partes, ignore_index=True)
        ext = df["series_id"].astype(str).str.extract(SERIE_BINANCE)
        if ext["ds"].isna().any() or (ext["ds"] != nombre).any() or (ext["iv"] != iv).any() or (ext["iv2"] != iv).any():
            raise ValueError(f"{nombre}: hay series_id que no son del dataset o del intervalo {iv}")
        intervalo = INTERVALOS_MS[iv]
        marco = pd.DataFrame({
            "instrument": ext["simbolo"].astype(object), "interval_ms": intervalo, "ts_ms": df["ts_ms"].astype("int64"),
            **{k: df[k].astype("float64") for k in ("open", "high", "low", "close", "volume")},
            "available_at_ms": (df["ts_ms"] + intervalo).astype("Int64"), "orden": range(len(df))})
        marco["interval_ms"] = marco["interval_ms"].astype("int64")
        fuentes.append({
            "dataset": nombre, "dataset_sha256": man.get("dataset_sha256"), "contenido_sha256": man.get("contenido_sha256"),
            "ficheros": [{"ruta": x["ruta"], "sha256": x["sha256"], "filas": x["filas"]} for x in man["ficheros"]],
            "fecha_descarga_utc": man.get("fecha_descarga_utc"), "fecha_proceso_utc": man.get("fecha_proceso_utc"),
            "motor_ti13": man.get("motor"), "clase_d11": man.get("clase_d11"), "licencia": (man.get("licencia") or {}).get("licencia"),
            "huecos_binance_segun_ti13": (man.get("filtro") or {}).get("huecos_binance")})
        universo[iv] = {s: int(n) for s, n in marco["instrument"].value_counts().sort_index().items()}
        tablas.append({
            "table_id": f"binance_ohlcv_{iv}", "schema": "ohlcv/v1", "frame": marco, "duplicados": "identicos",
            "calendario": None, "contador": nuevo_contador(len(marco)), "carga": {"filas_leidas": int(len(marco))},
            "disponibilidad": {
                "campo": "ts_ms + interval_ms (cierre de la vela)", "declarada": "por fila",
                "justificacion": (
                    "Una vela solo es definitiva al cerrar (close_time de Binance = apertura + intervalo - 1 ms) y TI-13-PUB no "
                    "conserva ninguna marca de publicacion por fila: solo la apertura de la vela y la fecha de descarga "
                    "(2026-11-08), que como disponibilidad dejaria todo el historico fuera de cualquier corte anterior. Se "
                    "declara el instante de cierre, la cota inferior de lo que pudo saberse, sin latencia de red ni de "
                    "publicacion (limitacion: un consumidor que necesite latencia debe aplicarla en su politica).")}})
    return {
        "nombre": "binance", "fuente": {"tipo": "binance", "datasets": fuentes}, "tablas": tablas,
        "licencia": "CC BY-NC-SA 4.0 de Binance Vision, solo uso personal no productivo",
        "universo": {
            "texto": ("Pares USDT que existen hoy en Binance spot y entraron en TI-13-PUB (el universo de la fuente hoy, no el de "
                      "una fecha pasada). No hay pares deslistados ni fechas de alta como miembro de un universo: sesgo de "
                      "supervivencia declarado (D-07), sin tabla universe/v1 porque no se conocen altas ni bajas."),
            "instrumentos": {iv: u for iv, u in universo.items()}}}


# ---------------------------------------------------------------------------------------------------------------------
# Lago de qn (volcado de descarga_lago.py)
# ---------------------------------------------------------------------------------------------------------------------

def a_ms(v) -> int | None:
    """Marca numerica del lago (s, ms, us o ns, por magnitud) a milisegundos UTC; None si no es una marca plausible."""
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None
    m = abs(v)
    ms = int(v) // 10 ** 6 if m >= 1e17 else int(v) // 10 ** 3 if m >= 1e14 else int(v) if m >= 1e11 else int(v * 1000)
    return ms if 631_152_000_000 <= ms <= 4_102_444_800_000 else None  # 1990..2100


def sub_ms(v) -> bool:
    """La marca en ns tiene resolucion inferior al milisegundo (se pierde al pasar a ms)."""
    return isinstance(v, int) and not isinstance(v, bool) and abs(v) >= 1e17 and v % 10 ** 6 != 0


def num(v) -> float:
    """Valor numerico de qn: los no finitos llegan como texto; todo lo que no sea numero queda como NaN (se cuenta como nulo)."""
    if isinstance(v, bool) or v is None:
        return math.nan
    if isinstance(v, (int, float)):
        return float(v)
    return {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf}.get(v, math.nan) if isinstance(v, str) else math.nan


def fecha_ms(texto) -> int | None:
    """Dia `AAAA-MM-DD` (exacto) a ms UTC de las 00:00; None si no tiene ese formato."""
    if not isinstance(texto, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return None
    try:
        return (date.fromisoformat(texto) - date(1970, 1, 1)).days * MS_DIA
    except ValueError:
        return None


def contenido_ms(texto) -> int | None:
    """Campo `date` de un objeto de qn (`AAAA-MM-DD` o `AAAA-MM-DDTHH:MM:SSZ`) tomado como UTC, en ms."""
    if not isinstance(texto, str) or len(texto) < 10:
        return None
    try:
        d = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None
    d = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    return (d - EPOCH) // timedelta(milliseconds=1)


def leer_ndjson(ruta: str):
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                yield json.loads(linea)


def abrir_volcado(directorio: str) -> dict:
    """Manifest del volcado, comprobando que esta completo y que cada fichero conserva su SHA-256 y su numero de filas."""
    ruta = os.path.join(directorio, "manifest.json")
    with open(ruta, encoding="utf-8") as f:
        m = json.load(f)
    if m.get("esquema") != ESQUEMA_VOLCADO:
        raise ValueError(f"{ruta} no es el manifest de descarga_lago.py ({ESQUEMA_VOLCADO})")
    if not m.get("completo"):
        raise ValueError(f"{directorio}: el volcado esta incompleto (completo=false); termina la descarga antes de exportar")
    for topic, t in m["topics"].items():
        for fich in t["ficheros"]:
            r = os.path.join(directorio, *fich["ruta"].split("/"))
            if not os.path.isfile(r) or sha256_fichero(r) != fich["sha256"]:
                raise ValueError(f"{r}: falta o su SHA-256 no coincide con el manifest del volcado")
    m["_sha256_manifest"] = sha256_fichero(ruta)
    return m


def _cargar_lago_ohlcv(directorio: str, topic: dict, orden0: int) -> tuple[list, int]:
    por_iv: dict = {}
    orden = orden0
    for fich in sorted(topic["ficheros"], key=lambda x: x["ruta"]):
        et = fich["etiquetas"]
        iv = et.get("interval")
        if iv not in INTERVALOS_MS:
            raise ValueError(f"{fich['ruta']}: intervalo {iv!r} desconocido (conocidos: {', '.join(INTERVALOS_MS)}); no se adivina")
        a = por_iv.setdefault(iv, {"cols": {k: [] for k in ("instrument", "ts_ms", "open", "high", "low", "close", "volume",
                                                            "recv_ms", "orden")},
                                   "leidas": 0, "sin_ts": 0, "sub_ms": 0, "con_recv": 0, "recv_antes_de_ts": 0,
                                   "desfases": Counter(), "con_date": 0, "mismo_dia": 0, "ejemplos_dia": [],
                                   "fuentes": Counter()})
        cols = a["cols"]
        for r in leer_ndjson(os.path.join(directorio, *fich["ruta"].split("/"))):
            a["leidas"] += 1
            orden += 1
            ts = a_ms(r.get("_ts"))
            if ts is None:
                a["sin_ts"] += 1
                continue
            a["sub_ms"] += sub_ms(r.get("_ts"))
            recv = a_ms(r.get("_recv_ts"))
            a["con_recv"] += recv is not None
            a["recv_antes_de_ts"] += recv is not None and recv < ts
            cols["instrument"].append(et["symbol"])
            cols["ts_ms"].append(ts)
            for k in ("open", "high", "low", "close", "volume"):
                cols[k].append(num(r.get(k)))
            cols["recv_ms"].append(recv)
            cols["orden"].append(orden)
            a["fuentes"][str(r.get("source"))] += 1
            dc = contenido_ms(r.get("date"))
            if dc is not None:
                a["con_date"] += 1
                a["desfases"][(dc - ts) // 1000] += 1
                if dc // MS_DIA == ts // MS_DIA:
                    a["mismo_dia"] += 1
                elif len(a["ejemplos_dia"]) < 3:
                    a["ejemplos_dia"].append({"instrument": et["symbol"], "_ts": iso_ms(ts), "date": r.get("date")})
    tablas = []
    for iv, a in sorted(por_iv.items()):
        cols = a["cols"]
        n = len(cols["ts_ms"])
        marco = pd.DataFrame({
            "instrument": pd.Series(cols["instrument"], dtype=object), "interval_ms": pd.Series([INTERVALOS_MS[iv]] * n, dtype="int64"),
            "ts_ms": pd.Series(cols["ts_ms"], dtype="int64"),
            **{k: pd.Series(cols[k], dtype="float64") for k in ("open", "high", "low", "close", "volume")},
            "recv_ms": pd.array(cols["recv_ms"], dtype="Int64"),
            "available_at_ms": pd.array([None] * n, dtype="Int64"), "orden": pd.Series(cols["orden"], dtype="int64")})
        con_recv = a["con_recv"] > 0
        tablas.append({
            "table_id": f"lago_ohlcv_{iv}", "schema": "ohlcv/v1", "frame": marco, "duplicados": "recepcion", "calendario": "fx",
            "contador": nuevo_contador(a["leidas"], {"sin_ts_valido": a["sin_ts"]} if a["sin_ts"] else {}),
            "carga": {"filas_leidas": a["leidas"], "ts_con_resolucion_inferior_al_ms": a["sub_ms"],
                      "filas_con_recv_ts": a["con_recv"], "recv_ts_anterior_a_ts": a["recv_antes_de_ts"],
                      "source": dict(a["fuentes"]),
                      "date_frente_a_ts": {
                          "filas_con_date": a["con_date"], "mismo_dia_utc": a["mismo_dia"],
                          "dia_utc_distinto": a["con_date"] - a["mismo_dia"],
                          "desfase_date_menos_ts_en_segundos": {str(k): v for k, v in a["desfases"].most_common(8)},
                          "ejemplos_de_dia_distinto": a["ejemplos_dia"]}},
            "disponibilidad": {
                "campo": "_recv_ts (instante en que qn recibio la version elegida de la barra)" if con_recv else None,
                "declarada": "por fila" if con_recv else "no declarada",
                "justificacion": (
                    "El productor (market_scrapper/qn_sink.py, quantdesk-backend) pone en `_ts` el inicio de la barra de "
                    "yfinance y no guarda ningun instante de publicacion; el unico instante en que el dato existia en el "
                    "sistema es `_recv_ts` (recepcion en qn). Las barras se republican mientras estan abiertas, asi que se "
                    "conserva la primera version recibida con `_recv_ts` >= cierre de la barra (inicio + intervalo) y se "
                    "declara su `_recv_ts` como disponibilidad. Es conservador: un relleno historico queda disponible desde "
                    "la fecha del relleno, nunca antes." if con_recv else
                    "Las filas no traen `_recv_ts` y el productor no guarda ningun otro instante de publicacion de las barras: "
                    "no hay base para declarar disponibilidad ni para fijar un default_lag_ms, asi que queda sin declarar y la "
                    "tabla NO es consumible causalmente (DPOL-AVL-001 / W-NO-AVAILABILITY).")}})
    return tablas, orden


def _json_dato(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _cargar_lago_eventos(directorio: str, topic: dict, orden0: int, cfg: dict) -> tuple[dict | None, int]:
    """rates.quotes y performance como custom/v1: una fila por observacion, con su payload en `data_json`."""
    cols = {k: [] for k in ("instrument", "custom_type", "ts_ms", "available_at_ms", "data_json", "orden")}
    c = {"leidas": 0, "excluidas": Counter(), "disp_ausente": 0, "disp_distinta_de_ts": 0, "fuentes": Counter()}
    orden = orden0
    nombres = set()
    for fich in sorted(topic["ficheros"], key=lambda x: x["ruta"]):
        et = fich["etiquetas"]
        inst = cfg["instrumento"](et)
        if inst in nombres:
            raise ValueError(f"{cfg['topic']}: dos combinaciones de etiquetas dan el mismo instrumento {inst!r}")
        nombres.add(inst)
        for r in leer_ndjson(os.path.join(directorio, *fich["ruta"].split("/"))):
            c["leidas"] += 1
            orden += 1
            ts = fecha_ms(r.get(cfg["campo_fecha"]))
            valor = num(r.get(cfg["campo_valor"]))
            if ts is None:
                c["excluidas"][f"{cfg['campo_fecha']}_invalida"] += 1
                continue
            if not math.isfinite(valor):
                c["excluidas"][f"{cfg['campo_valor']}_no_valido"] += 1
                continue
            disp = a_ms(r.get(cfg["campo_disp"]))
            c["disp_ausente"] += disp is None
            if cfg["campo_disp"] != "_ts":
                propio = a_ms(r.get("_ts"))
                c["disp_distinta_de_ts"] += propio is not None and disp is not None and propio != disp
            c["fuentes"][str(r.get("source"))] += 1
            cols["instrument"].append(inst)
            cols["custom_type"].append(cfg["topic"])
            cols["ts_ms"].append(ts)
            cols["available_at_ms"].append(disp)
            cols["data_json"].append(_json_dato({**et, cfg["campo_fecha"]: r.get(cfg["campo_fecha"]), cfg["campo_valor"]: valor,
                                                 "source": r.get("source")}))
            cols["orden"].append(orden)
    if c["leidas"] == 0:
        return None, orden
    marco = pd.DataFrame({
        "instrument": pd.Series(cols["instrument"], dtype=object), "custom_type": pd.Series(cols["custom_type"], dtype=object),
        "ts_ms": pd.Series(cols["ts_ms"], dtype="int64"), "available_at_ms": pd.array(cols["available_at_ms"], dtype="Int64"),
        "data_json": pd.Series(cols["data_json"], dtype=object), "orden": pd.Series(cols["orden"], dtype="int64")})
    return {
        "table_id": cfg["table_id"], "schema": "custom/v1", "frame": marco,
        "contador": nuevo_contador(c["leidas"], dict(c["excluidas"])),
        "carga": {"filas_leidas": c["leidas"], "sin_campo_de_disponibilidad": c["disp_ausente"],
                  "disponibilidad_distinta_de__ts": c["disp_distinta_de_ts"], "source": dict(c["fuentes"])},
        "disponibilidad": {"campo": cfg["campo_disp"], "declarada": "por fila", "justificacion": cfg["justificacion"]},
    }, orden


EVENTOS_LAGO = [
    {"topic": "market.rates.quotes", "table_id": "lago_rates_quotes", "campo_fecha": "valuation_date", "campo_valor": "rate",
     "campo_disp": "scraped_at_ms",
     "instrumento": lambda et: f"{et['currency']}.{et['curve_type']}.{et['tenor']}",
     "justificacion": (
         "`scraped_at_ms` es el instante (ms) en que el scraper leyo la cotizacion (market_scrapper/qn_sink.py::rates_item; "
         "`_ts` vale lo mismo). `valuation_date` es la fecha a la que se refiere la cotizacion y fija `ts_ms` (00:00 UTC). "
         "Una fecha de valoracion puede volver a leerse otro dia: se conserva la primera lectura.")},
    {"topic": "market.performance", "table_id": "lago_performance", "campo_fecha": "date", "campo_valor": "performance",
     "campo_disp": "_ts",
     "instrumento": lambda et: f"{et['symbol']}.{et['period']}",
     "justificacion": (
         "El productor (market_scrapper/market_sink.py::publish_performance) pone en `_ts` el instante de la lectura de la "
         "matriz de rendimiento (now), que es el unico instante de captura que conserva; `date` es la fecha de la matriz y fija "
         "`ts_ms` (00:00 UTC). Una fecha puede volver a leerse otro dia: se conserva la primera lectura.")},
]


def cargar_lago(directorio: str) -> dict:
    """Volcado del lago: ohlcv (por intervalo) a ohlcv/v1 y rates.quotes / performance a custom/v1 (hay una tabla que encaja)."""
    m = abrir_volcado(directorio)
    tablas, orden = [], 0
    universo = {}
    if "market.ohlcv" in m["topics"]:
        nuevas, orden = _cargar_lago_ohlcv(directorio, m["topics"]["market.ohlcv"], orden)
        tablas += nuevas
        universo["market.ohlcv"] = sorted({f"{f['etiquetas'].get('interval')}:{f['etiquetas'].get('symbol')}"
                                           for f in m["topics"]["market.ohlcv"]["ficheros"]})
    for cfg in EVENTOS_LAGO:
        if cfg["topic"] in m["topics"]:
            t, orden = _cargar_lago_eventos(directorio, m["topics"][cfg["topic"]], orden, cfg)
            universo[cfg["topic"]] = sorted(cfg["instrumento"](f["etiquetas"]) for f in m["topics"][cfg["topic"]]["ficheros"])
            if t:
                tablas.append(t)
    return {
        "nombre": "lago", "tablas": tablas, "licencia": "datos del propio laboratorio, recogidos por los scrapers de quantdesk-backend",
        "fuente": {"tipo": "lago", "volcado": os.path.abspath(directorio), "manifest_sha256": m["_sha256_manifest"],
                   "fecha_utc": m.get("fecha_utc"), "base": m.get("base"), "env": m.get("env"), "desde": m.get("desde"),
                   "hasta": m.get("hasta"), "descarga_lago_sha256": m.get("script_sha256"), "python_descarga": m.get("python"),
                   "ficheros": sum(len(t["ficheros"]) for t in m["topics"].values()),
                   "filas_por_topic": {k: t["filas"] for k, t in m["topics"].items()}},
        "universo": {
            "texto": ("Los instrumentos que listaba /latest de qn en la fecha de la descarga: lo que hay hoy en la fuente, sin "
                      "fechas de alta ni de baja y sin deslistados ni instrumentos retirados. Sesgo de supervivencia "
                      "declarado (D-07); no se escribe tabla universe/v1 porque no se conocen altas ni bajas."),
            "instrumentos": universo}}
