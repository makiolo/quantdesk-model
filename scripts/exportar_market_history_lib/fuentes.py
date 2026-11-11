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
from descarga_lago import POLITICA_FUENTES, TOPIC_OHLCV, ns_rfc3339, regla_fuente, seleccionar_series, validar_etiquetas

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
                "tipo": "cierre declarado por la fuente", "campo": "ts_ms + interval_ms (cierre de la vela)",
                "declarada": "por fila",
                "justificacion": (
                    "No es un proxy: es el cierre que declara la propia fuente. Cada kline de Binance trae su `close_time`, que "
                    "vale apertura + intervalo - 1 ms; TI-13-PUB lo descarto y conserva solo la apertura. Se comprobo en el crudo "
                    "(1640 zips de data.binance.vision, 420 219 klines): lo cumplen todos salvo 61 de 1 h, que cierran antes "
                    "(el cierre declarado aqui es conservador en esas). Es el instante en que la vela deja de cambiar, no un "
                    "instante de publicacion: no modela latencia de red ni de publicacion (un consumidor que la necesite debe "
                    "aplicarla en su politica), y la fecha de descarga (2026-11-08) no sirve porque dejaria todo el historico "
                    "fuera de cualquier corte anterior.")}})
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

def a_ms(v, arriba: bool = False) -> int | None:
    """Marca del lago (RFC3339 con zona, o numerica s/ms/us/ns por magnitud) a ms UTC; None si no es plausible.
    Redondea hacia abajo (instante de un evento) o, con `arriba`, hacia arriba: una disponibilidad nunca debe quedar por
    delante de la recepcion real."""
    if isinstance(v, str):
        ns = ns_rfc3339(v)
        if ns is None:
            return None
        ms = -(-ns // 10 ** 6) if arriba else ns // 10 ** 6
        return ms if 631_152_000_000 <= ms <= 4_102_444_800_000 else None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None
    m = abs(v)
    div = 10 ** 6 if m >= 1e17 else 10 ** 3 if m >= 1e14 else 1 if m >= 1e11 else None
    if div is None:
        ms = math.ceil(v * 1000) if arriba else int(v * 1000)
    else:
        ms = -(-int(v) // div) if arriba else int(v) // div
    return ms if 631_152_000_000 <= ms <= 4_102_444_800_000 else None  # 1990..2100


def sub_ms(v) -> bool:
    """La marca en ns tiene resolucion inferior al milisegundo (se pierde al pasar a ms)."""
    if isinstance(v, str):
        n = ns_rfc3339(v)
        return n is not None and n % 10 ** 6 != 0
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
    if TOPIC_OHLCV.removesuffix('.v2') in m["topics"]:
        raise ValueError("market.ohlcv v1 esta congelado y no se admite; usa un volcado de market.ohlcv.v2. "
                         "Para reproducir datasets antiguos ejecuta el exportador historico de git (0e67465).")
    for topic, t in m["topics"].items():
        for fich in t["ficheros"]:
            r = os.path.join(directorio, *fich["ruta"].split("/"))
            if not os.path.isfile(r) or sha256_fichero(r) != fich["sha256"]:
                raise ValueError(f"{r}: falta o su SHA-256 no coincide con el manifest del volcado")
    m["_sha256_manifest"] = sha256_fichero(ruta)
    return m


DISP_OHLCV_PROXY = {
    "tipo": "proxy por default_lag_ms", "campo": "ninguno: available_at_ms nulo y default_lag_ms = 0 en el manifest (cierre + 0)",
    "declarada": "por default_lag_ms = 0 (proxy, sin campo que la respalde)",
    "justificacion": (
        "PROXY elegido con --disponibilidad-ohlcv cierre. Ningun campo del lago dice cuando se supo cada barra antes de que qn la "
        "recibiera: `_recv_ts` es la recepcion en qn, y qn se relleno con el historico de golpe (primer `_recv_ts` en la seccion "
        "de limpieza), asi que con ese campo no hay ninguna barra anterior a esa fecha. Por eso `available_at_ms` queda nulo y "
        "el manifest declara `default_lag_ms` = 0, el mecanismo del motor para 'disponible al cierre, sin evidencia' (el motor "
        "cuenta estas filas como `defaulted`, no `declared`). Los VALORES son la version que qn recibio DESPUES del corte, no la "
        "visible al cierre (ver el ejemplo de mayor diferencia entre versiones en la limpieza): el dataset NO es causal en "
        "sentido estricto. Para eso esta el dataset estricto, que usa `_recv_ts`.")}


def _cargar_lago_ohlcv(directorio: str, topic: dict, orden0: int, disp_cierre: bool = False) -> tuple[list, int]:
    por_iv: dict = {}
    orden = orden0
    aceptadas, _ = seleccionar_series([f["etiquetas"] for f in topic["ficheros"]])
    for fich in sorted(topic["ficheros"], key=lambda x: x["ruta"]):
        et = fich["etiquetas"]
        validar_etiquetas(et, fich["ruta"])
        iv = et.get("interval")
        source = et["source"]
        admitida = (et["symbol"], iv, source) in aceptadas
        if iv not in INTERVALOS_MS:
            raise ValueError(f"{fich['ruta']}: intervalo {iv!r} desconocido (conocidos: {', '.join(INTERVALOS_MS)}); no se adivina")
        a = por_iv.setdefault(iv, {"cols": {k: [] for k in ("instrument", "ts_ms", "open", "high", "low", "close", "volume",
                                                            "recv_ms", "source", "orden")},
                                   "leidas": 0, "sin_ts": 0, "sub_ms": 0, "con_recv": 0, "recv_antes_de_ts": 0,
                                   "desfases": Counter(), "con_date": 0, "mismo_dia": 0, "ejemplos_dia": [],
                                   "fuentes": Counter(), "fuentes_leidas": Counter(), "fuentes_excluidas": Counter(),
                                   "series": {}, "excluidas_fuente": 0,
                                   "recv_min": None, "recv_max": None, "rango_desfase": {}})
        serie = a["series"].setdefault((et["symbol"], source), {
            "symbol": et["symbol"], "interval": iv, "source": source, "regla": regla_fuente(et["symbol"], iv),
            "admitida": admitida, "filas_leidas": 0, "filas_excluidas_por_fuente": 0})
        cols = a["cols"]
        for r in leer_ndjson(os.path.join(directorio, *fich["ruta"].split("/"))):
            a["leidas"] += 1
            a["fuentes_leidas"][source] += 1
            serie["filas_leidas"] += 1
            orden += 1
            if not isinstance(r, dict) or any(k in r and r[k] != et[k] for k in ("symbol", "interval", "source")):
                raise ValueError(f"{fich['ruta']}: tags de la fila distintos de las etiquetas del fichero")
            if not admitida:
                a["excluidas_fuente"] += 1
                a["fuentes_excluidas"][source] += 1
                serie["filas_excluidas_por_fuente"] += 1
                continue
            ts_original = r.get("_ts")
            ts = a_ms(ts_original)
            if ts is None:
                a["sin_ts"] += 1
                continue
            if source == "mt5" and iv == "1d" and (ts % MS_DIA != 0 or a_ms(ts_original, arriba=True) != ts
                                                   or isinstance(ts_original, float) and not ts_original.is_integer()):
                raise ValueError(f"{fich['ruta']}: source=mt5 1d exige ts exactamente a las 00:00Z")
            a["sub_ms"] += sub_ms(r.get("_ts"))
            recv = a_ms(r.get("_recv_ts"), arriba=True)
            a["con_recv"] += recv is not None
            a["recv_antes_de_ts"] += recv is not None and recv < ts
            if recv is not None:
                a["recv_min"] = recv if a["recv_min"] is None else min(a["recv_min"], recv)
                a["recv_max"] = recv if a["recv_max"] is None else max(a["recv_max"], recv)
            cols["instrument"].append(et["symbol"])
            cols["ts_ms"].append(ts)
            for k in ("open", "high", "low", "close", "volume"):
                cols[k].append(num(r.get(k)))
            cols["recv_ms"].append(recv)
            cols["source"].append(source)
            cols["orden"].append(orden)
            a["fuentes"][source] += 1
            dc = contenido_ms(r.get("date"))
            if dc is not None:
                a["con_date"] += 1
                a["desfases"][(dc - ts) // 1000] += 1
                lo, hi = a["rango_desfase"].get((dc - ts) // 1000, (ts, ts))
                a["rango_desfase"][(dc - ts) // 1000] = (min(lo, ts), max(hi, ts))
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
            "source": pd.Series(cols["source"], dtype=object),
            "available_at_ms": pd.array([None] * n, dtype="Int64"), "orden": pd.Series(cols["orden"], dtype="int64")})
        con_recv = a["con_recv"] > 0
        tablas.append({
            "table_id": f"lago_ohlcv_{iv}", "schema": "ohlcv/v1", "frame": marco, "duplicados": "recepcion", "calendario": "fx",
            "disp_cierre": disp_cierre,
            "contador": nuevo_contador(a["leidas"], {k: v for k, v in {
                "sin_ts_valido": a["sin_ts"], "fuente_excluida_por_regla": a["excluidas_fuente"]}.items() if v}),
            "carga": {"filas_leidas": a["leidas"], "ts_con_resolucion_inferior_al_ms": a["sub_ms"],
                      "filas_con_recv_ts": a["con_recv"], "recv_ts_anterior_a_ts": a["recv_antes_de_ts"],
                      "recv_ts_primero": iso_ms(a["recv_min"]) if a["recv_min"] is not None else None,
                      "recv_ts_ultimo": iso_ms(a["recv_max"]) if a["recv_max"] is not None else None,
                      "source": dict(a["fuentes"]),
                      "seleccion_fuentes": {"politica_version": POLITICA_FUENTES["version"],
                                            "leidas_por_source": dict(a["fuentes_leidas"]),
                                            "excluidas_por_source": dict(a["fuentes_excluidas"]),
                                            "series": [s for _, s in sorted(a["series"].items())]},
                      "date_frente_a_ts": {
                          "filas_con_date": a["con_date"], "mismo_dia_utc": a["mismo_dia"],
                          "dia_utc_distinto": a["con_date"] - a["mismo_dia"],
                          "desfase_date_menos_ts_en_segundos": {str(k): v for k, v in a["desfases"].most_common(8)},
                          "rango_de__ts_por_desfase": {str(k): [iso_ms(a["rango_desfase"][k][0]), iso_ms(a["rango_desfase"][k][1])]
                                                       for k, _ in a["desfases"].most_common(8)},
                          "ejemplos_de_dia_distinto": a["ejemplos_dia"]}},
            "disponibilidad": DISP_OHLCV_PROXY if disp_cierre else {
                "tipo": "campo del lago" if con_recv else "no declarada",
                "campo": "max(_recv_ts, _ts + intervalo) de la version elegida de la barra" if con_recv else None,
                "declarada": "por fila" if con_recv else "no declarada",
                "justificacion": (
                    "El topic market.ohlcv.v2 identifica la fuente por el tag source; `_ts` es la marca de la barra. "
                    "El unico instante respaldado en que el dato existia en el "
                    "sistema es `_recv_ts` (recepcion en qn). Las barras se republican mientras estan abiertas, asi que se "
                    "conserva la primera version recibida con `_recv_ts` >= cierre real (MT5 1d: 17:00 America/New_York "
                    "de la fecha UTC de `_ts`; resto: inicio + intervalo) y se "
                    "declara max(_recv_ts, _ts + intervalo) como disponibilidad (A12, DPOL-AVL-002). Para MT5 1d en vivo "
                    "es el fin nominal a las 00:00 UTC del dia siguiente, 2-3 h despues del cierre real. Es conservador: "
                    "un relleno historico queda disponible desde la fecha del relleno, nunca antes." if con_recv else
                    "Las filas no traen `_recv_ts` y el productor no guarda ningun otro instante de publicacion de las barras: "
                    "no hay base para declarar disponibilidad ni para fijar un default_lag_ms, asi que queda sin declarar y la "
                    "tabla NO es consumible causalmente (DPOL-AVL-001 / W-NO-AVAILABILITY).")}})
    return tablas, orden


def anotar_revisiones_mt5(t: dict) -> None:
    """Amplia la procedencia solo si la seleccion final realmente sustituyo una primera completa (A12)."""
    if t["contador"]["detalle"].get("version_mt5_revisada"):
        t["disponibilidad"] = {**t["disponibilidad"], "justificacion": (
            "MT5 1d usa la ultima version completa recibida hasta el corte si existe alguna; sin ninguna, conserva la "
            "primera completa como proxy en cierre y queda fuera en recepcion. Completa significa recepcion desde las "
            "17:00 America/New_York de la fecha UTC de ts. Otras fuentes e intervalos conservan la primera completa. "
            + ("PROXY elegido con --disponibilidad-ohlcv cierre: available_at_ms nulo y default_lag_ms = 0; el cierre "
               "nominal no demuestra disponibilidad y los valores pueden haberse recibido DESPUES del corte."
               if t.get("disp_cierre") else
               "Disponibilidad = max(_recv_ts de la version elegida, ts + intervalo), nunca anterior al fin nominal "
               "(A12, DPOL-AVL-002); para MT5 1d en vivo, 00:00 UTC del dia siguiente, 2-3 h despues del cierre real."))}


def _json_dato(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _cargar_lago_eventos(directorio: str, topic: dict, orden0: int, cfg: dict) -> tuple[dict | None, int]:
    """rates.quotes y performance como custom/v1: una fila por observacion, con su payload en `data_json`."""
    cols = {k: [] for k in ("instrument", "custom_type", "ts_ms", "available_at_ms", "data_json", "orden")}
    c = {"leidas": 0, "excluidas": Counter(), "disp_ausente": 0, "disp_distinta_de_ts": 0, "fuentes": Counter(),
         "ts_igual_a_fecha": 0, "disp_min": None, "disp_max": None, "congeladas": {}}
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
            disp = a_ms(r.get(cfg["campo_disp"]), arriba=True)
            c["disp_ausente"] += disp is None
            if disp is not None:
                c["disp_min"] = disp if c["disp_min"] is None else min(c["disp_min"], disp)
                c["disp_max"] = disp if c["disp_max"] is None else max(c["disp_max"], disp)
            c["ts_igual_a_fecha"] += a_ms(r.get("_ts")) == ts
            if cfg["campo_disp"] != "_ts":
                propio = a_ms(r.get("_ts"))
                c["disp_distinta_de_ts"] += propio is not None and disp is not None and propio != disp
            c["fuentes"][str(r.get("source"))] += 1
            if disp is not None and disp - ts > 365 * MS_DIA:  # dato fechado mas de un ano antes de que se leyera
                g = c["congeladas"].setdefault(inst, {"filas": 0, "anios": set(), "valores": set()})
                g["filas"] += 1
                g["anios"].add(r.get(cfg["campo_fecha"])[:4])
                g["valores"].add(valor)
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
                  "disponibilidad_distinta_de__ts": c["disp_distinta_de_ts"],
                  "filas_con__ts_igual_a_la_fecha": c["ts_igual_a_fecha"],
                  "disponibilidad_primera": iso_ms(c["disp_min"]) if c["disp_min"] is not None else None,
                  "disponibilidad_ultima": iso_ms(c["disp_max"]) if c["disp_max"] is not None else None,
                  "fechados_mas_de_un_ano_antes_de_leerse": [
                      {"instrument": k, "filas": g["filas"], "anios": sorted(g["anios"]), "valores_distintos": len(g["valores"]),
                       "valor_minimo": min(g["valores"]), "valor_maximo": max(g["valores"])}
                      for k, g in sorted(c["congeladas"].items())],
                  "source": dict(c["fuentes"])},
        "disponibilidad": {"tipo": "campo del lago", "campo": cfg["campo_disp"], "declarada": "por fila",
                           "justificacion": cfg["justificacion"]},
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
     "campo_disp": "_recv_ts",
     "instrumento": lambda et: f"{et['symbol']}.{et['period']}",
     "justificacion": (
         "El productor (market_scrapper/market_sink.py::publish_performance) pretende poner en `_ts` el instante de la lectura, "
         "pero en el volcado real `_ts` es la medianoche de `date` en casi todas las filas (el historico se cargo con esa marca; "
         "ver `filas_con__ts_igual_a_la_fecha`): no es un instante de captura y declararla como disponibilidad adelantaria cada "
         "rendimiento diario a las 00:00 del propio dia. Solo `_recv_ts` (recepcion en qn) esta respaldado, asi que es la "
         "disponibilidad; `date` fija `ts_ms` (00:00 UTC). Una fecha puede volver a leerse otro dia: se conserva la primera lectura.")},
]


def cargar_lago(directorio: str, disp_cierre: bool = False) -> dict:
    """Volcado del lago: ohlcv (por intervalo) a ohlcv/v1 y rates.quotes / performance a custom/v1 (hay una tabla que encaja).
    `disp_cierre`: la disponibilidad de ohlcv es el cierre de la barra (proxy) en vez de `_recv_ts`."""
    m = abrir_volcado(directorio)
    tablas, orden = [], 0
    universo = {}
    if TOPIC_OHLCV in m["topics"]:
        nuevas, orden = _cargar_lago_ohlcv(directorio, m["topics"][TOPIC_OHLCV], orden, disp_cierre)
        tablas += nuevas
        universo[TOPIC_OHLCV] = sorted({f"{f['etiquetas'].get('interval')}:{f['etiquetas'].get('symbol')}:{f['etiquetas'].get('source')}"
                                      for f in m["topics"][TOPIC_OHLCV]["ficheros"]})
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
                   "politica_fuentes": POLITICA_FUENTES,
                   "seleccion_volcado": m.get("seleccion"),
                   "avisos_volcado": m.get("avisos", []),
                   "filas_por_topic": {k: t["filas"] for k, t in m["topics"].items()}},
        "universo": {
            "texto": ("Los instrumentos que listaba /latest de qn en la fecha de la descarga: lo que hay hoy en la fuente, sin "
                      "fechas de alta ni de baja y sin deslistados ni instrumentos retirados. Sesgo de supervivencia "
                      "declarado (D-07); no se escribe tabla universe/v1 porque no se conocen altas ni bajas."),
            "instrumentos": universo}}
