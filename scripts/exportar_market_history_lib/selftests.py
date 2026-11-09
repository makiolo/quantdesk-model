"""Selftest del exportador: sin red y sin datos reales. Volcado sintetico del lago con la forma real (esquemas del inventario
TI-01-INV: `_ts`/`_recv_ts` en ns, tags en el nombre del fichero) y datasets sinteticos de TI-13-PUB; el script real se lanza
como subproceso. Todo bajo E:/quantdesk-lab/tmp/TI-02-DATA/ y se borra al terminar."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from . import formato as F
from . import limpieza as L
from . import validacion as V
from .fuentes import ESQUEMA_VOLCADO, sha256_fichero
from .fuentes import a_ms as A_MS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(HERE, "exportar_market_history.py")
LAB_TMP = "E:/quantdesk-lab/tmp/TI-02-DATA"
CORTE = "2026-11-01"
H, DIA, MIN = 3_600_000, 86_400_000, 60_000


def ms(m: int, d: int, h: int = 0, mi: int = 0) -> int:
    return int(datetime(2026, m, d, h, mi, tzinfo=timezone.utc).timestamp()) * 1000


def ns(m: int, d: int, h: int = 0, mi: int = 0) -> int:
    return ms(m, d, h, mi) * 10 ** 6


# ---------------------------------------------------------------------------------------------------------------------
# Piezas puras
# ---------------------------------------------------------------------------------------------------------------------

def prueba_redondeo_de_marcas() -> None:
    """La disponibilidad se redondea hacia arriba (nunca por delante de la recepcion); el instante de un evento, hacia abajo."""
    ns_ = 1793574185437103040
    assert A_MS(ns_) == 1793574185437 and A_MS(ns_, arriba=True) == 1793574185438
    assert A_MS(1793574185437000000, arriba=True) == 1793574185437  # un ms exacto no se mueve
    assert A_MS(1793574185437, arriba=True) == 1793574185437 and A_MS(1793574185.4371, arriba=True) == 1793574185438
    assert A_MS(None) is None and A_MS(True) is None and A_MS(5) is None


def prueba_formato_de_floats() -> None:
    """El formato de ryu/serde_json: sin cero en el exponente, `.0` en los enteros y notacion cientifica fuera de 1e-5..1e16."""
    casos = [(100.0, "100.0"), (0.1, "0.1"), (4285.08, "4285.08"), (1e-7, "1e-7"), (1.5e-7, "1.5e-7"), (1e-5, "0.00001"),
             (0.000012345, "0.000012345"), (0.0001, "0.0001"), (1e15, "1000000000000000.0"), (1e16, "1e+16"),
             (1.2345678901234568e17, "1.2345678901234568e+17"), (-2.5e-9, "-2.5e-9"), (5e-324, "5e-324"),
             (1.7976931348623157e308, "1.7976931348623157e+308"), (9e-6, "9e-6"), (-0.0, "-0.0"), (0.0, "0.0"), (123456.789, "123456.789")]
    for x, esperado in casos:
        assert F.fmt_f64(x) == esperado, (x, F.fmt_f64(x), esperado)
    try:
        F.fmt_f64(float("nan"))
    except ValueError:
        pass
    else:
        raise AssertionError("un NaN no tiene representacion en el hash logico")


def prueba_hash_contra_el_motor(tmp: str) -> None:
    """El hash logico calculado en Python coincide con el de quant-data (Rust) incluso con floats de formato delicado."""
    import data_py

    extremos = [1e-7, 1.5e-7, 1e-5, 0.000012345, 0.0001, 1e15, 1e16, 1.2345678901234568e17, 5e-324, 1.7976931348623157e308,
                100.0, 123456.789, -0.0, 0.1 + 0.2, 4285.08, 2.5e-9]
    n = len(extremos)
    df = pd.DataFrame({
        "instrument": pd.Series([f"I{i % 3}" for i in range(n)], dtype=object), "ts_ms": np.arange(n, dtype="int64") * 1000,
        "interval_ms": np.full(n, 1000, dtype="int64"), "open": extremos, "high": extremos, "low": extremos,
        "close": extremos[::-1], "volume": extremos, "volume_kind": pd.Series(["traded"] * n, dtype=object),
        "available_at_ms": pd.array([None if i % 2 else 2000 + i * 1000 for i in range(n)], dtype="Int64"),
        "revision": np.zeros(n, dtype="int32")})
    ruta = os.path.join(tmp, "extremos.parquet")
    F.escribir_parquet("ohlcv/v1", df, ruta)
    doc = json.loads(data_py.read_parquet_json(ruta, "ohlcv/v1", "{}"))
    assert doc["ok"] and doc["row_count"] == n, doc
    assert doc["logical_hash"] == F.hash_logico("ohlcv/v1", df), (doc["logical_hash"], F.hash_logico("ohlcv/v1", df))
    cu = pd.DataFrame({
        "instrument": pd.Series(["AUD.IBOR.10Y", None], dtype=object), "custom_type": pd.Series(["t\"x", "market.rates.quotes"], dtype=object),
        "schema_version": np.ones(2, dtype="int32"), "ts_ms": np.array([1, 2], dtype="int64"),
        "data_json": pd.Series(['{"rate":4.1,"s":"a\\"b\\\\c"}', '{"x":[1,2]}'], dtype=object),
        "available_at_ms": pd.array([None, 5], dtype="Int64"), "revision": np.zeros(2, dtype="int32")})
    ruta2 = os.path.join(tmp, "custom.parquet")
    F.escribir_parquet("custom/v1", cu, ruta2)
    doc = json.loads(data_py.read_parquet_json(ruta2, "custom/v1", "{}"))
    assert doc["ok"] and doc["logical_hash"] == F.hash_logico("custom/v1", cu), doc


def marco(filas: list, intervalo: int = DIA) -> pd.DataFrame:
    """DataFrame crudo para `limpiar_ohlcv`; cada fila: (instrument, ts, o, h, l, c, v, recv|None, disp|None)."""
    n = len(filas)
    return pd.DataFrame({
        "instrument": pd.Series([f[0] for f in filas], dtype=object), "interval_ms": np.full(n, intervalo, dtype="int64"),
        "ts_ms": pd.Series([f[1] for f in filas], dtype="int64"),
        **{k: pd.Series([f[2 + i] for f in filas], dtype="float64") for i, k in enumerate(("open", "high", "low", "close", "volume"))},
        "recv_ms": pd.array([f[7] for f in filas], dtype="Int64"), "available_at_ms": pd.array([f[8] for f in filas], dtype="Int64"),
        "orden": np.arange(n, dtype="int64")})


def prueba_limpieza() -> None:
    corte = ms(11, 1)
    ok = (1.0, 1.2, 0.9, 1.1, 5.0)
    # Binance: duplicado identico se quita, no finito, cero, negativo, incoherente y corte; el hueco se cuenta
    filas = [("A", ms(10, 26), *ok, None, ms(10, 27)), ("A", ms(10, 26), *ok, None, ms(10, 27)),
             ("A", ms(10, 28), *ok, None, ms(10, 29)),                                     # hueco de 1 barra (27)
             ("A", ms(10, 29), float("inf"), 1.2, 0.9, 1.1, 5.0, None, ms(10, 30)),
             ("A", ms(10, 30), 1.0, 1.2, 0.9, 1.1, -1.0, None, ms(10, 31)),
             ("B", ms(10, 26), 0.0, 1.2, 0.9, 1.1, 5.0, None, ms(10, 27)),
             ("B", ms(10, 27), 1.0, 0.8, 0.9, 1.1, 5.0, None, ms(10, 28)),                 # high < low
             ("B", ms(10, 28), 1.0, 1.2, 0.9, float("nan"), 5.0, None, ms(10, 29)),
             ("B", ms(10, 30), 1.0, 1.2, 0.9, 1.1, 0.0, None, ms(10, 31)),                 # volumen 0 se conserva
             ("B", ms(10, 31), *ok, None, ms(11, 1)),                                      # cierra justo en el corte: entra
             ("B", ms(11, 1), *ok, None, ms(11, 2))]                                       # cierra despues: fuera
    c = L.nuevo_contador(len(filas))
    out = L.limpiar_ohlcv(marco(filas), corte, "identicos", c)
    assert c["excluidas"] == {"duplicado": 1, "infinito": 1, "volumen_negativo": 1, "precio_no_positivo": 1,
                              "high_menor_que_low": 1, "nulo_o_nan": 1, "posterior_al_corte_por_fecha": 1}, c["excluidas"]
    assert len(out) == 4 and c["filas_finales"] == 4 and c["volumen_cero"] == 1
    assert out["ts_ms"].tolist() == [ms(10, 26), ms(10, 28), ms(10, 30), ms(10, 31)], out["ts_ms"].tolist()
    assert c["huecos"]["total"]["huecos"] == 1 and c["huecos"]["total"]["barras_ausentes"] == 1, c["huecos"]["total"]
    try:
        L.limpiar_ohlcv(marco([("A", ms(10, 26), *ok, None, ms(10, 27)), ("A", ms(10, 26), 1.0, 1.2, 0.9, 1.15, 5.0, None, ms(10, 27))]),
                        corte, "identicos", L.nuevo_contador(2))
    except ValueError as e:
        assert "valores distintos" in str(e)
    else:
        raise AssertionError("dos filas repetidas con valores distintos y sin criterio deben fallar")
    # cuentas que no cuadran se detectan
    try:
        L.verificar_identidad({"filas_origen": 5, "excluidas": {"x": 1}}, 3)
    except AssertionError:
        pass
    else:
        raise AssertionError("verificar_identidad debe fallar si las cuentas no cuadran")
    # open/close fuera de [low, high] se conserva y se cuenta aparte (no se corrige ni se quita)
    c = L.nuevo_contador(2)
    out = L.limpiar_ohlcv(marco([("A", ms(10, 26), 1.0, 1.2, 0.9, 1.1, 5.0, None, ms(10, 27)),
                                 ("A", ms(10, 27), 1.3, 1.2, 0.9, 1.1, 5.0, None, ms(10, 28))]), corte, "identicos", c)
    assert len(out) == 2 and c["excluidas"] == {}, c["excluidas"]
    x = c["detalle"]["ohlc_incoherente_conservada"]
    assert x["filas"] == 1 and abs(x["max_desvio_relativo"] - 0.1 / 1.1) < 1e-12, x
    # huecos con calendario FX: viernes -> lunes es cierre semanal; faltar un jueves no
    ts = [ms(10, 22), ms(10, 23), ms(10, 26), ms(10, 28)]  # jue, vie, lun, mie
    h = L.huecos(pd.DataFrame({"instrument": ["A"] * 4, "interval_ms": [DIA] * 4, "ts_ms": ts}), "fx")["total"]
    assert (h["huecos"], h["barras_ausentes"], h["huecos_de_fin_de_semana"]) == (2, 3, 1), h
    assert L.huecos(pd.DataFrame({"instrument": ["A"] * 4, "interval_ms": [DIA] * 4, "ts_ms": ts}))["total"]["huecos_de_fin_de_semana"] == 0
    # barras que no empiezan en la rejilla UTC del intervalo (p. ej. las de Binance de febrero de 2018): se conservan y se cuentan
    fuera = L.huecos(pd.DataFrame({"instrument": ["A"] * 3, "interval_ms": [H] * 3, "ts_ms": [0, 5 * H + 1000, 6 * H + 1000]}))
    assert fuera["total"]["fuera_de_rejilla"] == 2 and fuera["por_instrumento"]["A|3600000"]["primera_fuera_de_rejilla_ms"] == 5 * H + 1000


def prueba_versiones_del_lago() -> None:
    """Primera version ya cerrada segun la recepcion; sin recepcion, la ultima y la disponibilidad queda sin declarar."""
    corte = ms(11, 1)
    t = ms(10, 27)
    filas = [("A", t, 1, 1.2, 0.9, 1.00, 5, t + 12 * H, None), ("A", t, 1, 1.2, 0.9, 1.10, 5, t + DIA + 10 * MIN, None),
             ("A", t, 1, 1.2, 0.9, 1.15, 5, t + 3 * DIA, None),
             ("B", t, 1, 1.2, 0.9, 1.10, 5, t + 12 * H, None),     # solo version en curso
             ("C", t, 1, 1.2, 0.9, 1.10, 5, None, None)]          # sin marca de recepcion en una tabla que las trae
    c = L.nuevo_contador(len(filas))
    out = L.limpiar_ohlcv(marco(filas), corte, "recepcion", c)
    assert c["excluidas"] == {"sin_marca_de_recepcion": 1, "version_en_curso": 2, "version_posterior_descartada": 1}, c["excluidas"]
    assert out["close"].tolist() == [1.10] and out["available_at_ms"].tolist() == [t + DIA + 10 * MIN]
    d = c["detalle"]["version_posterior_descartada"]
    assert d["descartadas"] == 1 and d["con_valores_distintos"] == 1 and abs(d["max_dif_relativa_close"] - 0.05 / 1.10) < 1e-12
    sin = [("A", t, 1, 1.2, 0.9, 1.00, 5, None, None), ("A", t, 1, 1.2, 0.9, 1.15, 5, None, None)]
    c = L.nuevo_contador(2)
    out = L.limpiar_ohlcv(marco(sin), corte, "recepcion", c)
    assert out["close"].tolist() == [1.15] and out["available_at_ms"].isna().all() and "version_anterior_descartada" in c["excluidas"]


# ---------------------------------------------------------------------------------------------------------------------
# Volcado sintetico del lago
# ---------------------------------------------------------------------------------------------------------------------

def barra(ts: int, recv, o=1.0, h=1.2, l=0.9, c=1.1, v=0.0, date=None) -> dict:
    r = {"_ts": ts, "_clock_offset_ns": None, "open": o, "high": h, "low": l, "close": c, "volume": v, "date": date, "source": "market_scraper"}
    if recv is not None:
        r["_recv_ts"] = recv
    return r


def normal(m: int, d: int, **kw) -> dict:
    """Barra diaria completa, recibida 10 min despues del cierre."""
    return barra(ns(m, d), ns(m, d + 1, 0, 10), date=f"2026-{m:02d}-{d:02d}", **kw)


def cotizacion(valuation: str, rate, scraped_ns: int) -> dict:
    return {"_ts": scraped_ns, "_recv_ts": scraped_ns + 5 * 10 ** 9, "_clock_offset_ns": None, "valuation_date": valuation,
            "rate": rate, "scraped_at_ms": scraped_ns // 10 ** 6, "source": "market_scraper"}


def rendimiento(fecha: str, valor, ts_ns: int) -> dict:
    return {"_ts": ts_ns, "_recv_ts": ts_ns + 5 * 10 ** 9, "_clock_offset_ns": None, "performance": valor, "date": fecha, "source": "finviz"}


def datos_lago(futuro: bool = False, sin_recv: bool = False) -> dict:
    """{topic: [(etiquetas, filas)]} con duplicados, `date` desfasado de `_ts`, huecos, invalidos y filas posteriores al corte."""
    aaa = [barra(ns(10, 26), ns(10, 26, 12), date="2026-10-26"),                                  # solo version en curso
           barra(ns(10, 27), ns(10, 27, 12), c=1.00, date="2026-10-27"),                          # en curso
           barra(ns(10, 27), ns(10, 28, 0, 10), c=1.10, date="2026-10-27"),                       # primera version cerrada
           barra(ns(10, 27), ns(10, 30), c=1.15, date="2026-10-27"),                              # revision posterior
           normal(10, 28),
           barra(ns(10, 29), ns(10, 30, 0, 10), o="NaN", date="2026-10-29"),
           barra(ns(10, 30), ns(11, 2, 12), date="2026-10-30"),                                   # recibida despues del corte
           normal(11, 2)]
    bbb = [normal(10, 26), normal(10, 27), normal(10, 29), normal(10, 30), normal(11, 2), normal(11, 3)]  # falta el 28
    ccc = [barra(ns(10, 26), ns(10, 27, 0, 10), o=0.0), barra(ns(10, 27), ns(10, 28, 0, 10), h=0.8), normal(10, 28),
           normal(10, 29), normal(10, 30)]
    if futuro:  # nada de esto puede cambiar el dataset con corte 2026-11-01
        aaa += [normal(11, 4), barra(ns(10, 28), ns(11, 5), c=9.9, date="2026-10-28")]
        bbb += [normal(11, 5)]
    ohlcv = [({"interval": "1d", "symbol": "AAA"}, aaa), ({"interval": "1d", "symbol": "BBB"}, bbb),
             ({"interval": "1d", "symbol": "CCC"}, ccc),
             ({"interval": "1h", "symbol": "AAA"}, [
                 barra(ns(10, 25, 23), ns(10, 26, 0, 5), date="2026-10-26"), barra(ns(10, 26, 0), ns(10, 26, 1, 5), date="2026-10-26"),
                 barra(ns(10, 26, 1), ns(10, 26, 2, 5), date="2026-10-26T02:00:00Z")])]
    if futuro:
        ohlcv.append(({"interval": "1d", "symbol": "DDD"}, [normal(11, 2)]))
    if sin_recv:
        for _, filas in ohlcv:
            for r in filas:
                r.pop("_recv_ts", None)
    aud = [cotizacion("2026-10-26", 4.0, ns(10, 26, 9)), cotizacion("2026-10-27", 4.10, ns(10, 27, 9)),
           cotizacion("2026-10-27", 4.12, ns(10, 28, 9)), cotizacion("2026-10-28", 4.2, ns(10, 27, 23)),
           cotizacion("2026-11-02", 4.3, ns(11, 2, 9))]
    usd = [cotizacion(f"2026-10-{d}", 5.0 + d / 100, ns(10, d, 18)) for d in range(26, 31)]
    if futuro:
        aud.append(cotizacion("2026-11-04", 4.4, ns(11, 4, 9)))
    perf = [rendimiento(f"2026-10-{d}", 0.1 * d, ns(10, d, 17)) for d in range(26, 30)] + [
        rendimiento("2026-10-30", None, ns(10, 30, 17)), rendimiento("2026-11-01", 0.7, ns(11, 1, 17))]
    if futuro:
        perf.append(rendimiento("2026-11-04", 0.9, ns(11, 4, 17)))
    return {"market.ohlcv": ohlcv,
            "market.rates.quotes": [({"currency": "AUD", "curve_type": "IBOR", "tenor": "10Y"}, aud),
                                    ({"currency": "USD", "curve_type": "OIS", "tenor": "1D"}, usd)],
            "market.performance": [({"period": "D", "symbol": "EUR"}, perf)]}


def escribir_volcado(directorio: str, datos: dict, completo: bool = True) -> None:
    """Escribe lo mismo que descarga_lago.py: ndjson por instrumento y manifest con sha256 y filas."""
    topics = {}
    for topic, instrumentos in datos.items():
        ficheros = []
        for et, filas in instrumentos:
            rel = f"{topic}/" + ",".join(f"{k}={v}" for k, v in sorted(et.items())) + ".ndjson"
            ruta = os.path.join(directorio, *rel.split("/"))
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with open(ruta, "w", encoding="utf-8", newline="\n") as f:
                for r in filas:
                    f.write(json.dumps(r, separators=(",", ":")) + "\n")
            ficheros.append({"ruta": rel, "etiquetas": et, "filas": len(filas), "sha256": sha256_fichero(ruta)})
        topics[topic] = {"kind": "object", "ficheros": ficheros, "filas": sum(f["filas"] for f in ficheros)}
    F.escribir_json(os.path.join(directorio, "manifest.json"), {
        "esquema": ESQUEMA_VOLCADO, "fecha_utc": "2026-11-08T12:00:00Z", "base": "http://127.0.0.1:1/qn", "env": "main",
        "desde": "2026-10-01", "hasta": "2026-11-07", "script_sha256": "0" * 64, "python": "3.12.3", "completo": completo,
        "topics": topics})


def cli(*args: str, runs: str):
    env = dict(os.environ)
    r = subprocess.run([sys.executable, "-X", "utf8", SCRIPT, *args, "--runs", runs], capture_output=True, text=True,
                       encoding="utf-8", cwd=REPO, env=env, timeout=900)
    return r.returncode, r.stdout, r.stderr


def leer(raiz: str, nombre: str) -> dict:
    with open(os.path.join(raiz, nombre, "procedencia.json"), encoding="utf-8") as f:
        return json.load(f)


def prueba_exportar_lago(tmp: str) -> None:
    dump = os.path.join(tmp, "lago")
    escribir_volcado(dump, datos_lago())
    raiz1, raiz2, runs = (os.path.join(tmp, x) for x in ("r1", "r2", "runs"))
    base = ["--lago", dump, "--corte", CORTE, "--nombre", "lago_t"]
    cod, out, err = cli(*base, "--salida-raiz", raiz1, runs=runs)
    assert cod == 0, (out, err)
    p = leer(raiz1, "lago_t")
    t = {x["table_id"]: x for x in p["tablas"]}
    assert list(t) == ["lago_ohlcv_1d", "lago_ohlcv_1h", "lago_rates_quotes", "lago_performance"], list(t)
    assert [x["filas"] for x in t.values()] == [9, 3, 7, 4], [x["filas"] for x in t.values()]
    assert [x["schema"] for x in t.values()] == ["ohlcv/v1", "ohlcv/v1", "custom/v1", "custom/v1"]
    d1 = t["lago_ohlcv_1d"]["limpieza"]
    assert d1["filas_origen"] == 19 and d1["excluidas"] == {
        "version_en_curso": 2, "version_posterior_descartada": 1, "nulo_o_nan": 1, "precio_no_positivo": 1, "high_menor_que_low": 1,
        "posterior_al_corte_por_disponibilidad": 1, "posterior_al_corte_por_fecha": 3}, d1["excluidas"]
    assert d1["huecos"]["total"]["huecos"] == 1 and d1["huecos"]["total"]["barras_ausentes"] == 1
    assert d1["huecos"]["por_instrumento"]["BBB|86400000"]["mayor_hueco_barras"] == 1
    x = t["lago_ohlcv_1h"]["carga"]["date_frente_a_ts"]
    assert (x["filas_con_date"], x["dia_utc_distinto"], x["mismo_dia_utc"]) == (3, 1, 2), x
    assert x["desfase_date_menos_ts_en_segundos"] == {"3600": 2, "0": 1}, x
    assert t["lago_rates_quotes"]["limpieza"]["excluidas"] == {
        "disponibilidad_anterior_al_evento": 1, "version_posterior_descartada": 1, "posterior_al_corte_por_fecha": 1}
    assert t["lago_performance"]["limpieza"]["excluidas"] == {"performance_no_valido": 1, "posterior_al_corte_por_disponibilidad": 1}
    ds = os.path.join(raiz1, "lago_t")
    ohlcv = pq.read_table(os.path.join(ds, "lago_ohlcv_1d.parquet")).to_pandas()
    a27 = ohlcv[(ohlcv["instrument"] == "AAA") & (ohlcv["ts_ms"] == ms(10, 27))].iloc[0]
    assert a27["close"] == 1.10 and a27["available_at_ms"] == ms(10, 28, 0, 10), a27.to_dict()
    assert ohlcv["ts_ms"].is_monotonic_increasing and ((ohlcv["ts_ms"] + ohlcv["interval_ms"]) <= ms(11, 1)).all()
    assert (ohlcv["available_at_ms"] >= ohlcv["ts_ms"] + ohlcv["interval_ms"]).all() and (ohlcv["available_at_ms"] <= ms(11, 1)).all()
    ev = pq.read_table(os.path.join(ds, "lago_rates_quotes.parquet")).to_pandas()
    aud = ev[(ev["instrument"] == "AUD.IBOR.10Y") & (ev["ts_ms"] == ms(10, 27))].iloc[0]
    assert json.loads(aud["data_json"])["rate"] == 4.10 and aud["available_at_ms"] == ms(10, 27, 9)
    m = json.load(open(os.path.join(ds, "manifest.json"), encoding="utf-8"))
    assert m["default_lag_ms"] is None and m["time"]["zone"] == "UTC" and "sesgo de supervivencia" in m["description"].lower()
    reg = json.load(open(os.path.join(runs, "lago_t.json"), encoding="utf-8"))
    assert reg["validacion"]["ok"] and reg["validacion"]["tablas_no_consumibles_causalmente"] == []
    assert reg["validacion"]["lookahead"]["violaciones_por_fila"] == 0 and reg["validacion"]["politica"]["ok"]
    assert all(tb["hash_verified"] for tb in reg["validacion"]["describe"]["tablas"])
    # disponibilidad proxy: available_at_ms nulo y default_lag_ms = 0; la barra de `_recv_ts` posterior al corte (AAA 10-30) entra
    cod, out, err = cli(*base[:-1], "lago_p_cierre", "--salida-raiz", raiz1, "--disponibilidad-ohlcv", "cierre", runs=runs)
    assert cod == 0, (out, err)
    pp = {x["table_id"]: x for x in leer(raiz1, "lago_p_cierre")["tablas"]}
    assert pp["lago_ohlcv_1d"]["filas"] == 10 and "posterior_al_corte_por_disponibilidad" not in pp["lago_ohlcv_1d"]["limpieza"]["excluidas"]
    assert pp["lago_ohlcv_1d"]["disponibilidad"]["tipo"] == "proxy por default_lag_ms" and pp["lago_rates_quotes"]["filas"] == 7
    pr = pq.read_table(os.path.join(raiz1, "lago_p_cierre", "lago_ohlcv_1d.parquet")).to_pandas()
    assert pr["available_at_ms"].isna().all(), "el proxy no se escribe como disponibilidad por fila"
    mp = json.load(open(os.path.join(raiz1, "lago_p_cierre", "manifest.json"), encoding="utf-8"))
    assert mp["default_lag_ms"] == 0 and "DISPONIBILIDAD PROXY" in mp["description"] and "DESPUES del corte" in mp["description"]
    vp = json.load(open(os.path.join(runs, "lago_p_cierre.json"), encoding="utf-8"))["validacion"]
    assert vp["ok"] and vp["tablas_proxy"] == ["lago_ohlcv_1d", "lago_ohlcv_1h"], vp["tablas_proxy"]
    d1p = vp["disponibilidad"]["lago_ohlcv_1d"]
    assert (d1p["declared"], d1p["defaulted"], d1p["undeclared"], d1p["violaciones_dpol_avl_002"]) == (0, 10, 0, 0), d1p
    assert vp["disponibilidad"]["lago_rates_quotes"]["declared"] == 7 and vp["politica_con_lag_admitido"]["ok"]
    assert any(v["code"] == "DPOL-AVL-001" for v in vp["politica"]["violaciones"]), "la politica estricta debe avisar del proxy"
    # el nombre: el proxy lleva `_cierre` por defecto y nunca comparte nombre con el estricto; --sobrescribir no cambia de modo
    cod, out, err = cli("--lago", dump, "--corte", CORTE, "--salida-raiz", raiz1, "--disponibilidad-ohlcv", "cierre", runs=runs)
    assert cod == 0 and os.path.isdir(os.path.join(raiz1, "lago_cierre_c20261101")), (out, err)
    assert cli(*base, "--salida-raiz", os.path.join(tmp, "r6"), "--disponibilidad-ohlcv", "cierre", runs=runs)[0] == 2
    assert cli(*base[:-1], "lago_t_cierre", "--salida-raiz", os.path.join(tmp, "r6"), runs=runs)[0] == 2
    assert cli("--binance", "--corte", CORTE, "--disponibilidad-ohlcv", "cierre", "--salida-raiz", os.path.join(tmp, "r6"), runs=runs)[0] == 2
    shutil.copytree(os.path.join(raiz1, "lago_t"), os.path.join(raiz1, "lago_x_cierre"))
    antes = sha256_fichero(os.path.join(raiz1, "lago_x_cierre", "manifest.json"))
    cod, out, err = cli(*base[:-1], "lago_x_cierre", "--salida-raiz", raiz1, "--disponibilidad-ohlcv", "cierre", "--sobrescribir", runs=runs)
    assert cod == 2 and "otro modo" in err, (cod, err)
    assert sha256_fichero(os.path.join(raiz1, "lago_x_cierre", "manifest.json")) == antes
    # misma exportacion otra vez: mismo hash y mismos bytes
    cod, out, err = cli(*base, "--salida-raiz", raiz2, "--repeticion", runs=runs)
    assert cod == 0, (out, err)
    rep = json.load(open(os.path.join(runs, "lago_t.repeticion.json"), encoding="utf-8"))
    assert rep["validacion"]["dataset_hash"] == reg["validacion"]["dataset_hash"] and rep["ficheros_sha256"] == reg["ficheros_sha256"]
    assert set(reg["ficheros_sha256"]) == {"manifest.json", "procedencia.json", *(f"{k}.parquet" for k in t)}
    # un dato posterior al corte no entra: con filas futuras el dataset es identico
    dump_f = os.path.join(tmp, "lago_futuro")
    escribir_volcado(dump_f, datos_lago(futuro=True))
    cod, out, err = cli("--lago", dump_f, "--corte", CORTE, "--nombre", "lago_t", "--salida-raiz", os.path.join(tmp, "r3"),
                        "--repeticion", runs=os.path.join(tmp, "runs3"))
    assert cod == 0, (out, err)
    f3 = json.load(open(os.path.join(tmp, "runs3", "lago_t.repeticion.json"), encoding="utf-8"))["ficheros_sha256"]
    assert {k: v for k, v in f3.items() if k != "procedencia.json"} == {k: v for k, v in reg["ficheros_sha256"].items() if k != "procedencia.json"}
    # con otro corte el contenido cambia, y nunca asoma nada posterior a el
    cod, out, err = cli("--lago", dump_f, "--corte", "2026-10-30", "--nombre", "lago_t30", "--salida-raiz", raiz1, runs=runs)
    assert cod == 0, (out, err)
    p30 = leer(raiz1, "lago_t30")
    assert p30["dataset_hash"] != p["dataset_hash"]
    o30 = pq.read_table(os.path.join(raiz1, "lago_t30", "lago_ohlcv_1d.parquet")).to_pandas()
    assert ((o30["ts_ms"] + o30["interval_ms"]) <= ms(10, 30)).all() and (o30["available_at_ms"] <= ms(10, 30)).all() and len(o30) < 9
    # informe: cifras de los registros
    from . import informe

    md = informe.generar(raiz1, runs, ["lago_t"])
    assert "byte a byte identicos" in md and p["dataset_hash"] in md and "hash_verified=True" in md and "D-07" in md, md[:500]
    # sin `_recv_ts` la disponibilidad no se inventa: tablas no consumibles y error DPOL-AVL-001 de la politica
    dump_s = os.path.join(tmp, "lago_sin_recv")
    escribir_volcado(dump_s, datos_lago(sin_recv=True))
    cod, out, err = cli("--lago", dump_s, "--corte", CORTE, "--nombre", "lago_sr", "--salida-raiz", raiz1, runs=runs)
    assert cod == 0, (out, err)
    sr = json.load(open(os.path.join(runs, "lago_sr.json"), encoding="utf-8"))["validacion"]
    assert sr["tablas_no_consumibles_causalmente"] == ["lago_ohlcv_1d", "lago_ohlcv_1h"], sr["tablas_no_consumibles_causalmente"]
    assert any(v["code"] == "DPOL-AVL-001" for v in sr["politica"]["violaciones"]) and sr["ok"]
    ps = leer(raiz1, "lago_sr")
    assert ps["tablas"][0]["disponibilidad"]["declarada"] == "no declarada" and ps["tablas"][0]["disponibilidad"]["campo"] is None
    assert pq.read_table(os.path.join(raiz1, "lago_sr", "lago_ohlcv_1d.parquet")).to_pandas()["available_at_ms"].isna().all()
    assert json.load(open(os.path.join(raiz1, "lago_sr", "manifest.json"), encoding="utf-8"))["default_lag_ms"] is None
    # volcado incompleto o alterado: BLOQUEADO (2), nunca una exportacion parcial
    inc = os.path.join(tmp, "lago_inc")
    escribir_volcado(inc, datos_lago(), completo=False)
    cod, out, err = cli("--lago", inc, "--corte", CORTE, "--nombre", "x", "--salida-raiz", os.path.join(tmp, "r4"), runs=runs)
    assert cod == 2 and "incompleto" in err, (cod, err)
    with open(os.path.join(dump, "market.ohlcv", "interval=1d,symbol=AAA.ndjson"), "a", encoding="utf-8") as f:
        f.write("{}\n")
    cod, out, err = cli(*base, "--salida-raiz", os.path.join(tmp, "r5"), runs=runs)
    assert cod == 2 and "SHA-256" in err, (cod, err)
    assert not os.path.exists(os.path.join(tmp, "r5", "lago_t"))
    # revalidar un dataset ya escrito
    cod, out, err = cli("--validar", "lago_t", "--salida-raiz", raiz1, runs=runs)
    assert cod == 0 and '"ok": true' in out, (out, err)


# ---------------------------------------------------------------------------------------------------------------------
# Binance (TI-13-PUB) sintetico
# ---------------------------------------------------------------------------------------------------------------------

def escribir_ti13(raiz: str, iv: str, filas: list) -> None:
    """Un dataset con la forma de TI-13-PUB: parquet (series_id, ts ms UTC, value, open..volume, quote_volume, n_trades) + manifest."""
    nombre = f"binance__klines_{iv}"
    d = os.path.join(raiz, nombre)
    os.makedirs(d, exist_ok=True)
    cols = {k: [f[2 + i] for f in filas] for i, k in enumerate(("open", "high", "low", "close", "volume"))}
    t = pa.table({
        "series_id": pa.array([f"{nombre}/{f[0]}-{iv}" for f in filas], type=pa.string()),
        "ts": pa.array([f[1] for f in filas], type=pa.timestamp("ms", tz="UTC")), "value": pa.array(cols["close"]),
        **{k: pa.array(v, type=pa.float64()) for k, v in cols.items()},
        "quote_volume": pa.array([1.0] * len(filas)), "n_trades": pa.array([1] * len(filas), type=pa.int64())})
    ruta = os.path.join(d, "adaptadores.train.parquet")
    pq.write_table(t, ruta)
    F.escribir_json(os.path.join(d, "manifest.json"), {
        "dataset": nombre, "clase_d11": "real", "dataset_sha256": "a" * 64, "contenido_sha256": "b" * 64,
        "fecha_descarga_utc": "2026-11-08T10:00:00Z", "fecha_proceso_utc": "2026-11-08T10:30:00Z", "motor": "quantdesk 69fdb39d",
        "licencia": {"licencia": "CC BY-NC-SA 4.0"}, "filtro": {"huecos_binance": 1},
        "ficheros": [{"ruta": "adaptadores.train.parquet", "sha256": sha256_fichero(ruta), "filas": len(filas), "bytes": 1}]})


def prueba_exportar_binance(tmp: str) -> None:
    def vela(sim, t_ms, c=1.1, v=5.0):
        return (sim, t_ms, 1.0, 1.2, 0.9, c, v)

    d1 = [vela("AAAUSDT", ms(10, d)) for d in (27, 28, 30)] + [vela("AAAUSDT", ms(10, 27))] + [
        vela("AAAUSDT", ms(11, d)) for d in (1, 2, 3)]                     # un duplicado identico, un hueco (29), tres despues del corte
    d1h = [vela("BBBUSDT", ms(10, 31, h), v=0.0 if h == 21 else 5.0) for h in range(20, 24)] + [
        vela("BBBUSDT", ms(11, 1, h)) for h in range(0, 4)]
    raiz_ti = os.path.join(tmp, "ti13")
    escribir_ti13(raiz_ti, "1d", d1)
    escribir_ti13(raiz_ti, "1h", d1h)
    runs, r1, r2 = (os.path.join(tmp, x) for x in ("runs", "b1", "b2"))
    base = ["--binance", "--ti13", raiz_ti, "--corte", CORTE, "--nombre", "bin_t"]
    cod, out, err = cli(*base, "--salida-raiz", r1, runs=runs)
    assert cod == 0, (out, err)
    p = leer(r1, "bin_t")
    t = {x["table_id"]: x for x in p["tablas"]}
    assert [x["filas"] for x in t.values()] == [3, 4], [x["filas"] for x in t.values()]
    assert t["binance_ohlcv_1d"]["limpieza"]["excluidas"] == {"duplicado": 1, "posterior_al_corte_por_fecha": 3}
    assert t["binance_ohlcv_1d"]["limpieza"]["huecos"]["total"]["barras_ausentes"] == 1
    assert t["binance_ohlcv_1d"]["limpieza"]["huecos"]["total"]["huecos_de_fin_de_semana"] == 0   # 24x7: todo hueco es anomalo
    assert t["binance_ohlcv_1h"]["limpieza"]["excluidas"] == {"posterior_al_corte_por_fecha": 4}
    assert t["binance_ohlcv_1h"]["limpieza"]["volumen_cero"] == 1
    df = pq.read_table(os.path.join(r1, "bin_t", "binance_ohlcv_1h.parquet")).to_pandas()
    assert (df["available_at_ms"] == df["ts_ms"] + 3_600_000).all() and df["ts_ms"].max() == ms(10, 31, 23)
    assert (df["volume_kind"] == "traded").all() and df["instrument"].unique().tolist() == ["BBBUSDT"]
    reg = json.load(open(os.path.join(runs, "bin_t.json"), encoding="utf-8"))
    assert reg["validacion"]["ok"] and reg["validacion"]["lookahead"]["violaciones_por_fila"] == 0
    assert reg["validacion"]["tablas_no_consumibles_causalmente"] == []
    cod, out, err = cli(*base, "--salida-raiz", r2, "--repeticion", runs=runs)
    assert cod == 0, (out, err)
    rep = json.load(open(os.path.join(runs, "bin_t.repeticion.json"), encoding="utf-8"))
    assert rep["ficheros_sha256"] == reg["ficheros_sha256"] and rep["validacion"]["dataset_hash"] == reg["validacion"]["dataset_hash"]
    # uso incorrecto y reglas de sobrescritura
    cod, out, err = cli(*base, "--salida-raiz", r1, runs=runs)
    assert cod == 2 and "ya existe" in err, (cod, err)
    cod, out, err = cli(*base, "--salida-raiz", r1, "--sobrescribir", runs=runs)
    assert cod == 0, (out, err)
    assert cli("--binance", "--ti13", raiz_ti, "--corte", "2026-13-01", "--salida-raiz", r2, runs=runs)[0] == 2
    assert cli("--corte", CORTE, "--salida-raiz", r2, runs=runs)[0] == 2
    assert cli("--binance", "--ti13", raiz_ti, "--corte", CORTE, "--nombre", "../x", "--salida-raiz", r2, runs=runs)[0] == 2
    # dos filas repetidas con distinto valor: no hay criterio, datos inconsistentes
    malo = os.path.join(tmp, "ti13_malo")
    escribir_ti13(malo, "1d", d1 + [vela("AAAUSDT", ms(10, 27), c=1.15)])
    escribir_ti13(malo, "1h", d1h)
    cod, out, err = cli("--binance", "--ti13", malo, "--corte", CORTE, "--nombre", "bin_malo", "--salida-raiz", os.path.join(tmp, "b3"), runs=runs)
    assert cod == 1 and "INCONSISTENTES" in err, (cod, err)
    # un parquet alterado frente al SHA-256 de su manifest bloquea
    with open(os.path.join(raiz_ti, "binance__klines_1d", "adaptadores.train.parquet"), "ab") as f:
        f.write(b"x")
    cod, out, err = cli(*base, "--salida-raiz", os.path.join(tmp, "b4"), runs=runs)
    assert cod == 2 and "SHA-256" in err, (cod, err)


def prueba_validacion_detecta_lookahead(tmp: str) -> None:
    """La validacion no es vacua: una barra disponible antes de su cierre o un cierre posterior al corte se detectan."""
    raiz = os.path.join(tmp, "val")
    ds = os.path.join(raiz, "ds1")
    t = ms(10, 27)
    buenas = [("A", t, 1.0, 1.2, 0.9, 1.1, 5.0, None, t + DIA), ("A", t + DIA, 1.0, 1.2, 0.9, 1.1, 5.0, None, t + 2 * DIA)]
    tabla = {"table_id": "ohlcv", "schema": "ohlcv/v1"}
    limpias = L.limpiar_ohlcv(marco(buenas), ms(11, 1), "identicos", L.nuevo_contador(2))
    F.escribir_dataset(ds, "ds1", "prueba", "UTC", [{**tabla, "frame": limpias}])
    ok = V.validar(ds, raiz, "ds1", [tabla], ms(11, 1))
    assert ok["ok"] and ok["lookahead"]["violaciones_por_fila"] == 0 and ok["politica"]["ok"], ok["problemas"]
    # available_at_ms 1 s antes del cierre de la segunda barra
    mala = limpias.copy()
    mala.loc[1, "available_at_ms"] = t + 2 * DIA - 1000
    shutil.rmtree(ds)
    F.escribir_dataset(ds, "ds1", "prueba", "UTC", [{**tabla, "frame": mala}])
    r = V.validar(ds, raiz, "ds1", [tabla], ms(11, 1))
    assert not r["ok"] and r["lookahead"]["violaciones_por_fila"] == 1, r["problemas"]
    assert any(v["code"] == "DPOL-AVL-002" for v in r["politica"]["violaciones"]), r["politica"]
    # un cierre posterior al corte tambien lo detecta la comprobacion propia
    r = V.validar(ds, raiz, "ds1", [tabla], t + DIA)
    assert any("posterior al corte" in p for p in r["problemas"]), r["problemas"]


def prueba_integracion_con_descarga(tmp: str) -> None:
    """Los dos pasos encajan: el volcado que escribe descarga_lago.py (contra su qn falso) lo lee el exportador."""
    import descarga_lago as D

    estado = D.QnFalso()
    srv = D.servidor_falso(estado)
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        volcado = os.path.join(tmp, "integracion_volcado")
        cod, out, err = D.lanzar(url, volcado, "--desde", "2026-10-01", "--hasta", "2026-11-07")
        assert cod == 0, (out, err)
    finally:
        srv.shutdown()
        srv.server_close()
    raiz, runs = os.path.join(tmp, "integracion"), os.path.join(tmp, "integracion_runs")
    cod, out, err = cli("--lago", volcado, "--corte", CORTE, "--nombre", "lago_i", "--salida-raiz", raiz, runs=runs)
    assert cod == 0, (out, err)
    p = leer(raiz, "lago_i")
    filas = {t["table_id"]: t["filas"] for t in p["tablas"]}
    # 1d: 30 dias (1-30 oct) por simbolo; el 31 se recibe pasado el corte; 1 al 7 de nov cierran despues. Eventos: hasta el 1 nov incluido
    # performance usa `_recv_ts` (ts + 25 h): el 31 de octubre y el 1 de noviembre se reciben pasado el corte
    assert filas == {"lago_ohlcv_1d": 60, "lago_ohlcv_1h": 30, "lago_rates_quotes": 32, "lago_performance": 30}, filas
    d1 = p["tablas"][0]["limpieza"]["excluidas"]
    assert d1 == {"posterior_al_corte_por_disponibilidad": 2, "posterior_al_corte_por_fecha": 14}, d1
    assert p["origenes"][0]["fuente"]["filas_por_topic"]["market.ohlcv"] == 3 * 38 and p["origenes"][0]["fuente"]["ficheros"] == 5
    reg = json.load(open(os.path.join(runs, "lago_i.json"), encoding="utf-8"))["validacion"]
    assert reg["ok"] and reg["tablas_no_consumibles_causalmente"] == [] and reg["lookahead"]["violaciones_por_fila"] == 0


def correr() -> None:
    os.makedirs(LAB_TMP, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="selftest-", dir=LAB_TMP)
    try:
        prueba_formato_de_floats()
        prueba_redondeo_de_marcas()
        prueba_hash_contra_el_motor(tmp)
        prueba_limpieza()
        prueba_versiones_del_lago()
        prueba_validacion_detecta_lookahead(tmp)
        prueba_exportar_binance(tmp)
        prueba_exportar_lago(tmp)
        prueba_integracion_con_descarga(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest ok")
