"""Autoprueba de la ingesta publica (sin red, con datos sinteticos). La lanza `ingesta_publica.py --selftest`."""
from __future__ import annotations

import datetime as dt
import email.utils
import functools
import glob
import io
import json
import os
import shutil
import urllib.error
import urllib.parse
import zipfile

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from . import common as C
from . import filtro as FI
from . import fuentes as F
from . import lectores as LEC
from . import licencias as L
from . import registro as R

DIA = 86_400_000
AHORA = int(dt.datetime(2026, 11, 8, tzinfo=dt.timezone.utc).timestamp() * 1000)
CORTE = FI.corte_ms("2016-10-01")


def ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


def entrada(clase, fechas=None, dominio_col=None, formato="chronos", id_="chronos__sint"):
    return {"id": id_, "fuente": "chronos", "nombre": "sint", "clase": clase, "fechas": fechas, "dominio_col": dominio_col,
            "formato": formato, "dominio": "x", "motivo": "x", "freq": "D", "fechas_evid": "", "archivos": ["x"], "extras": []}


def diarias(inicio_ms, n, base=1.0):
    return inicio_ms + np.arange(n, dtype="int64") * DIA, base + np.arange(n, dtype="float64")


def t_decidir():
    ts, v = diarias(ms(2016, 9, 1), 60)  # cruza el corte (30 dias antes, 30 despues)
    s = LEC.Serie("S1", ts, v)
    r = FI.decidir(entrada(R.FIN, R.FECHAS_REALES), s, CORTE, AHORA)
    assert r["accion"] == "cortada" and r["idx"] == 30, r
    assert [p for p, _ in FI.trozos(r, s)] == ["tronco", "adaptadores"]
    assert FI.trozos(r, s)[0][1] == slice(0, 30) and FI.trozos(r, s)[1][1] == slice(30, 60)
    # un corte distinto cambia el reparto sin tocar los datos (el filtro se reaplica sobre lo crudo)
    r2 = FI.decidir(entrada(R.FIN, R.FECHAS_REALES), s, FI.corte_ms("2016-09-11"), AHORA)
    assert r2["idx"] == 10, r2
    ts_a, v_a = diarias(ms(2010, 1, 1), 100)
    assert FI.decidir(entrada(R.FIN, R.FECHAS_REALES), LEC.Serie("A", ts_a, v_a), CORTE, AHORA)["accion"] == "antes"
    ts_d, v_d = diarias(ms(2020, 1, 1), 100)
    assert FI.decidir(entrada(R.FIN, R.FECHAS_REALES), LEC.Serie("D", ts_d, v_d), CORTE, AHORA)["accion"] == "despues"
    # el corte exacto va a adaptadores (se corta con ts < corte)
    ts_e, v_e = diarias(CORTE - 2 * DIA, 4)
    assert FI.decidir(entrada(R.FIN, R.FECHAS_REALES), LEC.Serie("E", ts_e, v_e), CORTE, AHORA)["idx"] == 2
    # no financiera: intacta al tronco, con o sin fechas
    r = FI.decidir(entrada(R.NO_FIN), LEC.Serie("N", ts, v), CORTE, AHORA)
    assert r["accion"] == "intacta" and r["idx"] == 60 and [p for p, _ in FI.trozos(r, LEC.Serie("N", ts, v))] == ["tronco"]
    # financiera sin fechas verificables: excluida entera; con fechas imposibles: excluida aunque se declaren reales
    assert FI.decidir(entrada(R.FIN, R.FECHAS_NO_VERIFICABLES), LEC.Serie("X", None, v), CORTE, AHORA)["accion"] == "excluida"
    malas = [ts[::-1].copy(), np.full(60, ts[0]), ts - ts[0], np.full(60, 0, dtype="int64") + np.arange(60) * DIA,
             ts + (AHORA - ts[0] + 400 * DIA)]
    for m in malas:
        assert FI.decidir(entrada(R.FIN, R.FECHAS_REALES), LEC.Serie("M", m, v), CORTE, AHORA)["accion"] == "excluida", m[:2]
    mensual = LEC.gen_ts_ms("2000-01-01", 36, "M")  # meses de 28 a 31 dias: regulares aunque el paso en ms varie
    assert FI.decidir(entrada(R.NO_FIN), LEC.Serie("Mes", mensual, np.arange(36.0)), CORTE, AHORA)["regular"]
    con_hueco = np.delete(ts, 20)  # falta un dia
    assert not FI.decidir(entrada(R.NO_FIN), LEC.Serie("H", con_hueco, np.arange(59.0)), CORTE, AHORA)["regular"]
    t_monash, v_monash = diarias(ms(1900, 1, 1), 10)  # inicio por defecto del cargador de Monash: ficticio
    assert FI.decidir(entrada(R.FIN, R.FECHAS_REALES), LEC.Serie("Y", t_monash, v_monash), CORTE, AHORA)["accion"] == "excluida"
    t_sol, v_sol = diarias(ms(1818, 1, 8), 10)  # una fecha antigua pero plausible (manchas solares) no es un error
    assert FI.decidir(entrada(R.FIN, R.FECHAS_REALES), LEC.Serie("S", t_sol, v_sol), CORTE, AHORA)["accion"] == "antes"
    # series vacias: se excluyen y se cuentan, sean o no financieras
    for vac in (np.array([]), np.full(5, np.nan)):
        assert FI.decidir(entrada(R.NO_FIN), LEC.Serie("V", None, vac), CORTE, AHORA)["motivo"] == "serie vacia"
    # datos reales con fecha (cripto): todo a adaptadores
    r = FI.decidir(entrada(R.REAL, R.FECHAS_REALES), LEC.Serie("B", ts, v), CORTE, AHORA)
    assert FI.trozos(r, LEC.Serie("B", ts, v))[0][0] == "adaptadores"
    # mixto con dominio por serie (M4): se filtra serie a serie; lo desconocido cuenta como financiero
    m4 = entrada(R.FIN, R.FECHAS_REALES, dominio_col="category")
    assert not FI.es_financiera(m4, "Demographic") and FI.es_financiera(m4, "Finance") and FI.es_financiera(m4, "Macro")
    assert FI.es_financiera(m4, "Other") and FI.es_financiera(m4, None)
    assert FI.decidir(m4, LEC.Serie("d", ts, v, "Demographic"), CORTE, AHORA)["accion"] == "intacta"
    assert FI.decidir(m4, LEC.Serie("f", ts, v, "Finance"), CORTE, AHORA)["accion"] == "cortada"
    assert FI.es_financiera(entrada(R.FIN, R.FECHAS_NO_VERIFICABLES), None)  # sin dominio por serie: entero financiero


def t_particion():
    ids = [f"chronos__x/T{i:03d}" for i in range(40)]
    patron = "".join("V" if FI.lado_por_id(i) == "val" else "t" for i in ids)
    assert patron == "ttVttttttttttVttttttttttttttVttttttttttt", patron  # fijado: cambiar la sal o el hash lo rompe
    assert FI.lado_por_id("a/b") == FI.lado_por_id("a/b")
    frac = sum(FI.lado_por_id(f"k{i}") == "val" for i in range(20000)) / 20000
    assert abs(frac - R.FRAC_VAL) < 0.01, frac
    otro = "".join("V" if FI.lado_por_id(i, sal="otra-sal") == "val" else "t" for i in ids)
    assert otro != patron  # la sal cambia la particion
    h = {k: FI.hash_contenido(np.arange(k % 5 + 3, dtype="float64")) for k in range(50)}
    cont = {f"d/{k}": [h[k]] for k in range(50)}  # series con contenido repetido bajo ids distintos
    lados, st = FI.asignar_lados(cont)
    assert st["componentes_con_duplicados"] > 0
    comp = FI.comprobar_disjuntos(lados, cont)
    assert comp["contenidos_en_ambos_lados"] == 0, comp
    grupos = {}
    for k in range(50):
        grupos.setdefault(h[k], set()).add(lados[f"d/{k}"])
    assert all(len(g) == 1 for g in grupos.values())
    # el comprobador detecta una fuga: mismo contenido a ambos lados
    malos = dict(lados)
    a, b = next((x, y) for x in cont for y in cont if x != y and cont[x] == cont[y])
    malos[a], malos[b] = "train", "val"
    assert FI.comprobar_disjuntos(malos, cont)["contenidos_en_ambos_lados"] >= 1
    assert FI.hash_contenido(np.array([1.0, np.nan])) == FI.hash_contenido(np.array([1.0, -np.nan]))
    assert FI.hash_contenido(np.array([1.0, 2.0])) != FI.hash_contenido(np.array([1.0, 2.0, 2.0]))
    # el componente toma el lado de su miembro minimo: no depende del orden de entrada
    inv = dict(reversed(list(cont.items())))
    assert FI.asignar_lados(inv)[0] == lados


def t_guarda():
    GB = 10**9
    ok = lambda u: {"C:/": 5 * GB, "E:/": 300 * GB}[u]  # noqa: E731
    assert C.guarda(1 * GB, 10 * GB, 1 * GB, ok)["total_previsto_bytes"] == 12 * GB
    assert C.guarda(100 * GB - 11 * GB, 10 * GB, 1 * GB, ok)["total_previsto_bytes"] == 100 * GB  # justo en el limite
    try:
        C.guarda(100 * GB - 11 * GB + 1, 10 * GB, 1 * GB, ok)
        raise AssertionError("debia parar por presupuesto")
    except C.PresupuestoExcedido:
        pass
    for c, e in ((C.C_LIBRE_MIN - 1, 300 * GB), (5 * GB, C.E_LIBRE_MIN - 1)):
        try:
            C.guarda(1, 0, 0, lambda u, c=c, e=e: {"C:/": c, "E:/": e}[u])
            raise AssertionError("debia parar por disco")
        except C.ParadaDisco:
            pass
    assert C.hash_conjunto([("a", "1"), ("b", "2")]) == C.hash_conjunto([("b", "2"), ("a", "1")])
    assert C.hash_conjunto([("a", "1"), ("b", "2")]) != C.hash_conjunto([("a", "1"), ("b", "3")])
    assert C.git_blob_sha1(b"hola") == "b8b4a4e2a5db3ebed5f5e02beb3e2d27bca9fc9a"  # git hash-object


def t_red():
    assert [C.espera_reintento(i) for i in range(3)] == [2.0, 4.0, 8.0]
    assert C.espera_reintento(0, 30) == 30.0 and C.espera_reintento(0, 500) == C.ESPERA_MAX
    assert C.parse_retry_after("7") == 7.0 and C.parse_retry_after("x") is None and C.parse_retry_after(None) is None
    reloj = [0.0]
    dormidos = []

    def dormir(s):
        dormidos.append(s)
        reloj[0] += s

    ritmo = C.Ritmo(1.0, reloj=lambda: reloj[0], dormir=dormir)
    ritmo.esperar("h")
    ritmo.esperar("h")
    ritmo.esperar("otro")
    assert dormidos == [1.0], dormidos  # el segundo GET al mismo host espera 1 s; otro host, no
    # reintentos: dos caidas y luego exito; Retry-After en 429; 404 no se reintenta
    class Resp(io.BytesIO):
        status, headers = 200, {"Content-Length": "2"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    intentos = []

    def abrir_ok(req, timeout=0):
        intentos.append(1)
        if len(intentos) <= 2:
            raise urllib.error.URLError("conexion cerrada")
        return Resp(b"ok")

    esp = []
    r = C.http_get("http://x.test/a", abrir=abrir_ok, ritmo=C.Ritmo(0, dormir=lambda s: None), dormir=esp.append)
    assert r["cuerpo"] == b"ok" and esp == [2.0, 4.0], esp

    def abrir_429(req, timeout=0):
        raise urllib.error.HTTPError(req.full_url, 429, "x", {"Retry-After": "9"}, io.BytesIO(b""))

    esp = []
    try:
        C.http_get("http://x.test/b", abrir=abrir_429, ritmo=C.Ritmo(0, dormir=lambda s: None), dormir=esp.append)
        raise AssertionError("debia agotar reintentos")
    except C.ErrorRed:
        pass
    assert esp == [9.0, 9.0, 9.0], esp  # respeta Retry-After (mayor que 2, 4, 8 en el primero) en los 3 reintentos

    # revision 3 (MEDIA): un Retry-After mayor que ESPERA_MAX (60 s) no se acorta a 60 s: no se reintenta (cero peticiones mas) y
    # se lanza ErrorRed con el motivo. 7, 30 y 60 s siguen como antes (se espera exactamente lo que pide el servidor).
    def abrir_con_ra(ra, antes=()):
        n = []

        def abrir(req, timeout=0):
            n.append(1)
            if len(n) <= len(antes):
                raise urllib.error.HTTPError(req.full_url, antes[len(n) - 1], "x", {}, io.BytesIO(b""))
            raise urllib.error.HTTPError(req.full_url, 429, "x", {"Retry-After": ra}, io.BytesIO(b""))
        return abrir, n

    assert C.ESPERA_MAX == 60.0
    for ra, antes, peticiones, esperas in (("7", (), 4, [7.0, 7.0, 8.0]),  # la exponencial (2, 4, 8) manda cuando es mayor que Retry-After
                                           ("30", (), 4, [30.0] * 3), ("60", (), 4, [60.0] * 3),
                                           ("61", (), 1, []), ("120", (), 1, []), ("120", (503,), 2, [2.0])):
        abrir, n = abrir_con_ra(ra, antes)
        esp = []
        try:
            C.http_get("http://x.test/ra", abrir=abrir, ritmo=C.Ritmo(0, dormir=lambda s: None), dormir=esp.append)
            raise AssertionError(ra)
        except C.ErrorRed as err:
            assert len(n) == peticiones and esp == esperas, (ra, len(n), esp)  # tras Retry-After > 60 s: ni una peticion mas, ni una espera
            if int(ra) > 60:
                assert f"el servidor pide esperar {ra} s; se reintentara en otra ejecucion" in str(err), err
            else:
                assert "4 intentos" in str(err), err
    # Retry-After como fecha HTTP lejana (> 60 s desde ahora): tampoco se reintenta
    lejos = email.utils.format_datetime(dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=10), usegmt=True)
    abrir, n = abrir_con_ra(lejos)
    try:
        C.http_get("http://x.test/ra", abrir=abrir, ritmo=C.Ritmo(0, dormir=lambda s: None), dormir=lambda s: None)
        raise AssertionError("fecha lejana")
    except C.ErrorRed as err:
        assert len(n) == 1 and "el servidor pide esperar" in str(err) and "otra ejecucion" in str(err), (len(n), err)

    llamadas = []

    def abrir_404(req, timeout=0):
        llamadas.append(1)
        raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, io.BytesIO(b"{}"))

    r = C.http_get("http://x.test/c", permitir=(404,), abrir=abrir_404, ritmo=C.Ritmo(0, dormir=lambda s: None))
    assert r["status"] == 404 and len(llamadas) == 1
    try:
        C.http_get("http://x.test/c", abrir=abrir_404, ritmo=C.Ritmo(0, dormir=lambda s: None), dormir=lambda s: None)
        raise AssertionError("404 no permitido debia fallar")
    except C.ErrorRed:
        assert len(llamadas) == 2  # sin reintentos en un 4xx


def t_lectores(tmp):
    assert LEC.norm_freq("H") == "h" and LEC.norm_freq("30T") == "30min" and LEC.norm_freq("4S") == "4s"
    assert LEC.norm_freq("M") == "ME" and LEC.norm_freq("Q-DEC") == "QE-DEC" and LEC.norm_freq("W-SUN") == "W-SUN"
    t = LEC.gen_ts_ms("1959-03-01", 3, "M")
    assert [int(x) for x in t] == [ms(1959, 3, 1), ms(1959, 4, 1), ms(1959, 5, 1)]
    assert list(np.diff(LEC.gen_ts_ms("2020-01-01", 3, "30T"))) == [1_800_000] * 2
    # Chronos: parquet con listas
    p = f"{tmp}/chronos.parquet"
    ts0 = np.array([ms(2016, 9, 29), ms(2016, 9, 30), ms(2016, 10, 1)], dtype="datetime64[ms]")
    tabla = pa.table({"id": ["a", "b"], "timestamp": pa.array([list(ts0), list(ts0[:2])], pa.list_(pa.timestamp("ms"))),
                      "target": pa.array([[1.0, 2.0, 3.0], [4.0, None]], pa.list_(pa.float32()))})
    pq.write_table(tabla, p)
    s = list(LEC.leer_chronos(p))
    assert [x.id for x in s] == ["a", "b"] and list(s[0].v) == [1.0, 2.0, 3.0] and np.isnan(s[1].v[1]) and len(s[1].ts) == 2
    assert s[0].ts[2] == ms(2016, 10, 1)
    # LOTSA: flujo IPC con una serie univariante y otra multivariante
    p = f"{tmp}/lotsa.arrow"
    uni = pa.table({"item_id": ["u"], "start": pa.array([dt.datetime(2020, 1, 1)], pa.timestamp("s")), "freq": ["D"],
                    "target": pa.array([[1.0, 2.0, 3.0]], pa.list_(pa.float32()))})
    with pa.OSFile(p, "wb") as fh, pa.ipc.new_stream(fh, uni.schema) as w:
        w.write_table(uni)
    s = list(LEC.leer_lotsa(p))
    assert s[0].id == "u" and list(s[0].v) == [1.0, 2.0, 3.0] and s[0].ts[1] - s[0].ts[0] == DIA
    mul = pa.table({"item_id": ["m"], "start": pa.array([dt.datetime(2020, 1, 1)], pa.timestamp("s")), "freq": ["h"],
                    "target": pa.array([[[1.0, 2.0], [3.0, 4.0]]], pa.list_(pa.list_(pa.float32())))})
    p2 = f"{tmp}/lotsa_m.arrow"
    with pa.OSFile(p2, "wb") as fh, pa.ipc.new_stream(fh, mul.schema) as w:
        w.write_table(mul)
    s = list(LEC.leer_lotsa(p2))
    assert [x.id for x in s] == ["m#0", "m#1"] and list(s[1].v) == [3.0, 4.0] and s[0].ts[1] - s[0].ts[0] == 3_600_000
    # Binance: ms y microsegundos, cabecera opcional, un duplicado y un hueco
    assert F.parse_checksum("ab" * 32 + "  BTCUSDT-1d-2020-01.zip\n") == "ab" * 32
    try:
        F.parse_checksum("no es un hash")
        raise AssertionError("debia fallar")
    except ValueError:
        pass
    filas = [f"{ms(2020, 1, 1)},1,2,0.5,1.5,10,0,100,5,0,0,0", f"{ms(2020, 1, 2)},1.5,2,1,1.8,11,0,110,6,0,0,0",
             f"{ms(2020, 1, 4)},1.8,3,1,2.0,12,0,120,7,0,0,0", f"{ms(2020, 1, 4)},1.8,3,1,2.0,12,0,120,7,0,0,0"]
    base = f"{tmp}/binance/data/spot/monthly/klines/TESTUSDT/1d"
    os.makedirs(base)
    with zipfile.ZipFile(f"{base}/TESTUSDT-1d-2020-01.zip", "w") as z:
        z.writestr("TESTUSDT-1d-2020-01.csv", "\n".join(filas) + "\n")
    micro = f"{ms(2025, 1, 1) * 1000},1,1,1,1,1,0,1,1,0,0,0\n"
    with zipfile.ZipFile(f"{base}/TESTUSDT-1d-2025-01.zip", "w") as z:
        z.writestr("TESTUSDT-1d-2025-01.csv", "open_time,open,high,low,close,volume,close_time,quote_volume,n_trades,tb,tq,ig\n" + micro)
    F_RAW = F.RAW_BINANCE
    F.RAW_BINANCE = f"{tmp}/binance"
    try:
        s = list(LEC.leer_binance({"intervalo": "1d", "pares": ["TESTUSDT", "NOEXISTE"]}))
    finally:
        F.RAW_BINANCE = F_RAW
    assert len(s) == 1 and s[0].id == "TESTUSDT-1d" and len(s[0].ts) == 4, s
    assert s[0].meta["duplicados"] == 1 and s[0].meta["huecos"] == 2, s[0].meta  # hueco 01-02->01-04 y 01-04->2025-01-01
    assert s[0].ts[-1] == ms(2025, 1, 1) and list(s[0].cols["close"][:3]) == [1.5, 1.8, 2.0]


def t_licencias(tmp):
    def evid(nombre, contenido):
        ruta = f"{tmp}/{nombre}"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido if isinstance(contenido, str) else json.dumps(contenido))
        return {"ruta": ruta, "sha256": "x", "status": 200, "error": None, "url": "u", "fecha_utc": "t", "bytes": 1}

    api = {"sha": "rev", "cardData": {"license": "other", "dataset_info": [
        {"config_name": "con_lic", "license": "CC BY 4.0"}, {"config_name": "otra", "license": "MIT"}, {"config_name": "sin_lic"}]}}
    zen = {"metadata": {"license": {"id": "cc-by-4.0"}, "title": "T"}}
    ev = {"hf_chronos_api": evid("api.json", api), "zenodo_1": evid("z1.json", zen),
          "zenodo_2": evid("z2.json", {"metadata": {"license": {"id": "other-closed"}}}), "github_m4_licencia": {"status": 404}}
    base = {"fuente": "chronos", "repo": "autogluon/chronos_datasets", "id": "chronos__x"}
    v = L.veredicto_hf({**base, "nombre": "con_lic", "lic_tarjeta": "CC BY 4.0", "zenodo": 1}, ev)
    assert v["estado"] == "verificada" and v["licencia"] == "CC BY 4.0" and v["origen"] == "CC BY 4.0"
    assert L.veredicto_hf({**base, "nombre": "sin_lic", "lic_tarjeta": None, "zenodo": None}, ev)["estado"] == "excluida"
    assert "no verificable" in L.veredicto_hf({**base, "nombre": "m4_daily", "lic_tarjeta": None, "zenodo": None}, ev)["motivo"]
    assert L.veredicto_hf({**base, "nombre": "inexistente", "lic_tarjeta": "MIT", "zenodo": None}, ev)["estado"] == "excluida"
    assert L.veredicto_hf({**base, "nombre": "otra", "lic_tarjeta": "CC BY 4.0", "zenodo": None}, ev)["estado"] == "excluida"  # no coincide
    assert L.veredicto_hf({**base, "nombre": "con_lic", "lic_tarjeta": "CC BY 4.0", "zenodo": 2}, ev)["estado"] == "excluida"  # origen no CC BY
    assert L.veredicto_hf({**base, "nombre": "con_lic", "lic_tarjeta": "CC BY 4.0", "zenodo": 3}, ev)["estado"] == "excluida"  # sin evidencia
    ev2 = {"binance_terms": evid("bt.txt", "## 3. NON-COMMERCIAL LICENSE GRANT\n ... (CC BY-NC-SA 4.0) ...")}
    assert L.veredicto_binance({"id": "b"}, ev2)["licencia"] == "CC BY-NC-SA 4.0"
    assert L.veredicto_binance({"id": "b"}, {})["estado"] == "excluida"
    ev3 = {"yahoo_robots": evid("yr.txt", "User-agent: *\nDisallow: /\n"), "yahoo_terms": evid("yt.txt", "any automated means ... express, prior permission"),
           "stooq_robots": evid("sr.txt", "User-agent: Googlebot\nAllow: /\nUser-agent: *\nDisallow: /\n"),
           "fred_robots": evid("fr.txt", "User-agent: *"), "fred_terms": {"error": "cerrada", "sha256": None},
           "fred_csv_muestra": {"error": "cerrada", "sha256": None}}
    n = L.no_obtenidas(ev3)
    assert n["yahoo"]["robots_prohibe"] and n["stooq"]["robots_prohibe"] and n["fred"]["bloqueado"]
    assert all(x["estado"] == "excluida" for x in n.values())
    # la descarga exige veredicto 'verificada'
    assert L.verificada({"datasets": {"a": {"estado": "verificada"}, "b": {"estado": "excluida"}}}, "a")
    assert not L.verificada({"datasets": {"b": {"estado": "excluida"}}}, "b") and not L.verificada(None, "a")
    for d in R.DATASETS:  # el registro es coherente
        assert d["clase"] in (R.NO_FIN, R.FIN, R.REAL) and d["archivos"]
        assert d["clase"] != R.FIN or d["fechas"] in (R.FECHAS_REALES, R.FECHAS_NO_VERIFICABLES)
    assert len({d["id"] for d in R.DATASETS + R.BINANCE}) == len(R.DATASETS + R.BINANCE)


def t_extremo_a_extremo(tmp):
    """Filtro + particion + parquet + manifiesto con series sinteticas; reaplicar da el mismo hash, otro corte no."""
    e = entrada(R.FIN, R.FECHAS_REALES, dominio_col="category")
    e["id"], e["formato"] = "chronos__sint", "chronos"
    sint = []
    for i in range(30):
        ts, v = diarias(ms(2016, 8, 1) + (i % 3) * 20 * DIA, 120, base=float(i))
        sint.append(LEC.Serie(f"F{i:02d}", ts, v, "Finance" if i % 2 else "Demographic"))
    sint.append(LEC.Serie("COPIA", sint[1].ts, sint[1].v.copy(), "Finance"))  # contenido identico a F01 con otro id
    sint.append(LEC.Serie("F01", *diarias(ms(2017, 1, 1), 5), "Finance"))  # id repetido
    sint.append(LEC.Serie("VACIA", None, np.array([]), "Finance"))
    orig = LEC.series
    LEC.series = lambda entry, con_ts=True: iter(sint)
    try:
        an = FI.analizar(e, CORTE, AHORA)
        st = FI.estadisticas(e, an)
        assert st["series_total"] == 33 and st["ids_duplicados"] == 1 and st["series_vacias"] == 1, st
        assert st["cortadas"] > 0 and st["puntos_tronco"] + st["puntos_adaptadores"] + st["puntos_excluidos"] == st["puntos_total"], st
        assert st["duplicados_de_contenido"] >= 1, st
        cont = {r["clave"]: r["hashes"] for r in an["registros"] if r["hashes"]}
        lados, _ = FI.asignar_lados(cont)
        assert FI.comprobar_disjuntos(lados, cont)["contenidos_en_ambos_lados"] == 0
        assert lados["chronos__sint/COPIA"] == lados["chronos__sint/F01"]  # el duplicado va al mismo lado
        h = []
        for k in (1, 2):
            man = FI.procesar_dataset(e, an, lados, f"{tmp}/ds{k}", "2016-10-01", {"licencia": "x"}, [], guarda=_sin_guarda,
                                      guarda_lote=_sin_guarda_lote)
            h.append((man["dataset_sha256"], man["contenido_sha256"]))
        assert h[0] == h[1], "reaplicar el filtro debe dar el mismo hash de dataset"
        # punto 2a: la guarda se aplica ANTES de escribir, con usado_previo y 2 x el crudo del dataset como estimacion
        vistas = []
        FI.procesar_dataset(e, an, lados, f"{tmp}/g1", "2016-10-01", {}, [{"bytes": 1000}], usado_previo=7,
                            guarda=lambda extra, usado, cache: vistas.append((extra, usado)) or {}, guarda_lote=_sin_guarda_lote)
        assert vistas == [(2 * 1000, 7)], vistas
        cache0, C.bytes_cache_hf = C.bytes_cache_hf, lambda *a, **k: 0
        try:
            try:
                FI.procesar_dataset(e, an, lados, f"{tmp}/g2", "2016-10-01", {}, [{"bytes": 60 * 10**9}], usado_previo=0,
                                    guarda=lambda extra, usado, cache: C.guarda(extra, usado, cache, libre_fn=lambda u: 10**13),
                                    guarda_lote=_sin_guarda_lote)
                raise AssertionError("2 x 60 GB de estimacion debia superar el presupuesto")
            except C.PresupuestoExcedido:
                pass
        finally:
            C.bytes_cache_hf = cache0
        assert not os.path.exists(f"{tmp}/g2/chronos__sint"), "no debe escribirse nada si la guarda para"
        for k in ("corte", "sal", "versiones", "motor", "fecha_proceso_utc", "dataset_sha256", "ficheros"):
            assert k in man, k
        assert man["motor"] == "quantdesk 69fdb39d" and man["sal"] == R.SAL and man["corte"] == "2016-10-01"
        # lo escrito: ninguna serie en tronco y adaptadores con lado distinto, y el corte se respeta
        ids_lado, fin_ids = {}, {f"chronos__sint/{s.id}" for s in sint if s.dom == "Finance" and s.id != "VACIA"}
        fin_ids |= {"chronos__sint/F01~dup1"}
        n_ad = 0
        for f in man["ficheros"]:
            t = pq.read_table(f"{tmp}/ds1/chronos__sint/{f['ruta']}")
            assert t.schema.names == ["series_id", "ts", "value"] and str(t.schema.field("ts").type) == "timestamp[ms, tz=UTC]"
            assert t.num_rows == f["filas"]
            ts = t.column("ts").cast(pa.int64()).to_numpy()
            ids = np.array(t.column("series_id").to_pylist())
            es_fin = np.isin(ids, list(fin_ids))
            if f["parte"] == "tronco":
                assert (ts[es_fin] < CORTE).all()  # lo financiero del tronco es anterior al corte
            else:
                assert (ts >= CORTE).all() and len(ts) > 0
                n_ad += len(ts)
            for sid in set(ids.tolist()):
                assert ids_lado.setdefault(sid, f["split"]) == f["split"], sid  # un id, un lado
        assert n_ad == st["puntos_adaptadores"]
        esc = FI.comprobar_escrito(f"{tmp}/ds1", {"chronos__sint": man})  # lo escrito, releido: sin fugas entre train y val
        assert esc["ids_en_ambos_lados"] == 0 and esc["contenidos_en_ambos_lados"] == 0 and esc["filas_releidas"] > 0, esc
        assert esc["series_train"] + esc["series_val"] == len(ids_lado), esc
        # el comprobador detecta una fuga: la misma serie (mismo id y mismos valores) en un fichero train y otro val
        os.makedirs(f"{tmp}/mal/x")
        tt = pa.table({"series_id": ["x/a"] * 3, "ts": pa.array([1, 2, 3], pa.timestamp("ms", tz="UTC")), "value": [1.0, 2.0, 3.0]})
        for sp in ("train", "val"):
            pq.write_table(tt, f"{tmp}/mal/x/tronco.{sp}.parquet")
        mal = FI.comprobar_escrito(f"{tmp}/mal", {"x": {"ficheros": [{"ruta": f"tronco.{sp}.parquet", "split": sp, "filas": 3} for sp in ("train", "val")]}})
        assert mal["ids_en_ambos_lados"] == 1 and mal["contenidos_en_ambos_lados"] == 1, mal
        # otro corte: mismo crudo, otro reparto, sin descargar nada
        an2 = FI.analizar(e, FI.corte_ms("2016-09-01"), AHORA)
        assert FI.estadisticas(e, an2)["puntos_tronco"] != st["puntos_tronco"]
    finally:
        LEC.series = orig


def _sin_guarda(extra, usado, cache):
    return {}


def _sin_guarda_lote(escrito, cota, usado, cache):
    return {}


def _zip(contenido: bytes) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("TESTUSDT-1d-2020-01.csv", contenido)
    return b.getvalue()


def t_binance_idempotencia(tmp):
    """Punto 1: la idempotencia exige tamano y SHA-256; un ZIP corrupto del mismo tamano se redescarga y se verifica."""
    ok = _zip(b"1,2,3\n" * 50)
    mal = bytearray(ok)
    mal[len(mal) // 2] ^= 0xFF  # mismo tamano, otro contenido
    mal = bytes(mal)
    assert len(mal) == len(ok) and mal != ok
    clave = "data/spot/monthly/klines/TESTUSDT/1d/TESTUSDT-1d-2020-01.zip"
    base = f"{tmp}/binance_idem"
    llamadas, servidor = [], {"zip": ok}

    def http_falso(url, destino=None, **kw):
        llamadas.append(url)
        if url.endswith(".CHECKSUM"):
            return {"status": 200, "cabeceras": {}, "cuerpo": (C.sha256_bytes(ok) + "  TESTUSDT-1d-2020-01.zip\n").encode(), "bytes": 0}
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "wb") as f:
            f.write(servidor["zip"])
        return {"status": 200, "cabeceras": {}, "cuerpo": b"", "bytes": len(servidor["zip"])}

    raw0, guarda0, http0 = F.RAW_BINANCE, F._guarda, C.http_get
    F.RAW_BINANCE, F._guarda, C.http_get = base, lambda extra: None, http_falso
    destino = f"{base}/{clave}"
    try:
        F._bajar_binance(clave, len(ok))
        assert len(llamadas) == 2 and open(destino, "rb").read() == ok  # .CHECKSUM + zip
        llamadas.clear()
        F._bajar_binance(clave, len(ok))
        assert llamadas == [], "con tamano y hash correctos no debe haber red"
        with open(destino, "wb") as f:
            f.write(mal)  # corrupto, del mismo tamano que lo registrado
        assert os.path.getsize(destino) == F.manifiesto_crudo(base)["archivos"][f"binance/{clave}"]["bytes"]
        F._bajar_binance(clave, len(ok))
        assert len(llamadas) == 2 and open(destino, "rb").read() == ok, llamadas  # se redescargo y quedo bien
        assert F.manifiesto_crudo(base)["archivos"][f"binance/{clave}"]["sha256"] == C.sha256_bytes(ok)
        # si el servidor tambien da un contenido que no casa con el .CHECKSUM, se rechaza y se borra
        servidor["zip"] = mal
        with open(destino, "wb") as f:
            f.write(mal)
        try:
            F._bajar_binance(clave, len(ok))
            raise AssertionError("debia rechazar un zip que no casa con su .CHECKSUM")
        except RuntimeError:
            assert not os.path.exists(destino)
    finally:
        F.RAW_BINANCE, F._guarda, C.http_get = raw0, guarda0, http0
    # camino del Hub: el mismo criterio (tamano y hash del manifiesto)
    ruta = f"{tmp}/hub_f.bin"
    with open(ruta, "wb") as f:
        f.write(b"abc")
    assert F.ya_descargado({"bytes": 3, "sha256": C.sha256_bytes(b"abc")}, ruta)
    assert not F.ya_descargado({"bytes": 3, "sha256": C.sha256_bytes(b"abd")}, ruta)  # mismo tamano, otro hash
    assert not F.ya_descargado(None, ruta) and not F.ya_descargado({"bytes": 3, "sha256": "x"}, ruta + ".no")


def t_cache_hf(tmp):
    """Punto 2b: la cache de HF se cuenta entera o se aborta; nunca devuelve un subtotal."""
    raiz = f"{tmp}/cachehf"
    for rel, n in (("xet/a/1", 10), ("xet/a/2", 5), ("datasets/x", 7), ("torch/grande", 1000), ("xdg/y", 1000)):
        os.makedirs(os.path.dirname(f"{raiz}/{rel}"), exist_ok=True)
        with open(f"{raiz}/{rel}", "wb") as f:
            f.write(b"x" * n)
    assert C.bytes_cache_hf(raiz) == 22  # xet + datasets; torch y xdg no son descargas de huggingface_hub
    assert C.bytes_cache_hf(f"{tmp}/no_existe") == 0
    try:
        C.bytes_cache_hf(raiz, max_ficheros=2)  # 3 ficheros contables > 2: la cache esta truncada
        raise AssertionError("una cache que no se puede medir completa debe abortar")
    except C.CacheNoMedible as e:
        assert "no se puede medir completa" in str(e)
    assert issubclass(C.CacheNoMedible, C.ParadaDisco)  # la orden descargar la trata como parada
    os.makedirs(f"{raiz}/hub/basura")  # entrada que scan_cache_dir no reconoce: medida incompleta
    try:
        C.bytes_cache_hf(raiz)
        raise AssertionError("una entrada ilegible en hub/ debe abortar")
    except C.CacheNoMedible:
        pass


class _Resp(io.BytesIO):
    """Respuesta falsa de urllib: cuerpo, estado y cabeceras propios."""

    def __init__(self, cuerpo: bytes, status: int = 200, headers: dict | None = None):
        super().__init__(cuerpo)
        self.status = status
        self.headers = {"Content-Length": str(len(cuerpo))} if headers is None else headers

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http_error(url, code, cab=None):
    return urllib.error.HTTPError(url, code, "x", cab or {}, io.BytesIO(b""))


class _Mundo:
    """Reloj y transporte falsos (sin red): el ritmo (1 peticion/s por host) y la espera entre reintentos avanzan el mismo reloj."""

    def __init__(self, servidor):
        self.t, self.esperas, self.peticiones, self.servidor = 0.0, [], [], servidor
        self.ritmo = C.Ritmo(1.0, reloj=lambda: self.t, dormir=self._avanzar)

    def _avanzar(self, s):
        self.t += s

    def dormir(self, s):
        self.esperas.append(s)
        self.t += s

    def abrir(self, req, timeout=0):
        self.peticiones.append((self.t, req.full_url, {k.lower(): v for k, v in req.header_items()}))
        return self.servidor(self, req)

    def http(self):
        return functools.partial(C.http_get, abrir=self.abrir, ritmo=self.ritmo, dormir=self.dormir)

    def a(self, prefijo):
        return [p for p in self.peticiones if p[1].startswith(prefijo)]


CDN = "https://cdn.hf.test/blob/abc?sig=SECRETA"  # el CDN firma la URL: no debe aparecer en el registro de peticiones


def _hub_ok(contenidos: dict):
    """Hub falso: resolve -> 302 al CDN -> 200 con el contenido del fichero."""
    def servidor(mundo, req):
        url = req.full_url
        if url.startswith(R.HUB_BASE):
            rel = url.split("/resolve/", 1)[1].split("/", 1)[1]
            raise _http_error(url, 302, {"Location": f"https://cdn.hf.test/blob/{rel}?sig=SECRETA"})
        return _Resp(contenidos[url.split("/blob/", 1)[1].split("?", 1)[0]])
    return servidor


def _ritmo_ok(mundo):
    """Nunca dos peticiones al mismo host con menos de 1 s de diferencia."""
    for host in {urllib.parse.urlsplit(p[1]).netloc for p in mundo.peticiones}:
        t = [p[0] for p in mundo.peticiones if urllib.parse.urlsplit(p[1]).netloc == host]
        assert all(b - a >= 1.0 - 1e-9 for a, b in zip(t, t[1:])), (host, t)


def t_topes_lotsa(tmp):
    """Punto 3: un subconjunto de LOTSA de mas de 2 GB, o cuyo total (el SUBCONJUNTO ENTERO, no cada fichero) llevaria LOTSA a mas de
    10 GB, se bloquea antes de bajar su primer fichero."""
    GB = 10**9
    C.comprobar_tope_lotsa(2 * GB, 8 * GB)  # justo en el limite: pasa
    C.comprobar_tope_lotsa(GB, 10 * GB)
    for sub, tot in ((2 * GB + 1, 0), (2_100_000_000, 3 * GB), (GB, 10 * GB + 1)):
        try:
            C.comprobar_tope_lotsa(sub, tot)
            raise AssertionError((sub, tot))
        except C.TopeLotsa:
            pass
    assert issubclass(C.TopeLotsa, C.PresupuestoExcedido)
    base = f"{tmp}/hf_topes"

    def ds(nombre, extras=(), archivos=None):
        return {"id": f"lotsa__{nombre}", "fuente": "lotsa", "repo": R.LOTSA_REPO, "nombre": nombre,
                "archivos": archivos or [f"{nombre}/data.arrow"], "extras": list(extras)}

    contenido = b"x" * 1000
    sib = {"grande/data.arrow": {"size": 2_100_000_000}, "grande/state.json": {"size": 250},
           "pequeno/data.arrow": {"size": 1000, "lfs": {"sha256": C.sha256_bytes(contenido)}}}
    estado = {"datasets": {"lotsa__grande": {"estado": "verificada"}, "lotsa__pequeno": {"estado": "verificada"}}}
    mundo = _Mundo(_hub_ok({"pequeno/data.arrow": contenido, "grande/data.arrow": contenido}))
    raw0, guarda0, sib0 = F.RAW_HF, F._guarda, F._siblings
    F.RAW_HF, F._guarda, F._siblings = base, lambda extra: None, lambda estado_lic, fuente: (sib, "rev")
    try:
        omit = F.descargar_hub("lotsa", estado, datasets=[ds("grande", ["grande/state.json"]), ds("pequeno")], http=mundo.http())
        assert [i for i, _ in omit] == ["lotsa__grande"] and "tope de LOTSA" in omit[0][1], omit
        assert [p[1] for p in mundo.a(R.HUB_BASE)] == [F.url_hub(R.LOTSA_REPO, "rev", "pequeno/data.arrow")], mundo.peticiones
        # el de 2,1 GB no se pidio ni un byte
        # total: con 9,5 GB de LOTSA ya registrados, un subconjunto de 1 GB lo llevaria por encima de 10 GB
        for i in range(19):
            F._registrar(base, f"hf/{R.LOTSA_REPO}/viejo{i}/d.arrow", {"bytes": GB // 2, "sha256": "x"})
        sib["otro/data.arrow"] = {"size": GB, "lfs": {"sha256": C.sha256_bytes(contenido)}}
        estado["datasets"]["lotsa__otro"] = {"estado": "verificada"}
        mundo.peticiones.clear()
        try:
            F.descargar_hub("lotsa", estado, datasets=[ds("otro")], http=mundo.http())
            raise AssertionError("debia parar por el tope de 10 GB de LOTSA")
        except C.TopeLotsa as e:
            assert "10 GB" in str(e) and mundo.peticiones == []
        # revision 2 (MEDIA): un subconjunto de DOS ficheros cuyo total no cabe en el cupo, aunque el primero si cabria solo.
        # Se reducen los topes (10 GB -> 3000 B, 2 GB -> 2000 B) para poder bajar de verdad los ficheros.
        tot0, sub0 = C.LOTSA_TOTAL_MAX, C.LOTSA_SUBCONJUNTO_MAX
        C.LOTSA_TOTAL_MAX, C.LOTSA_SUBCONJUNTO_MAX = 3000, 2000
        try:
            ctn = {"dos/a.arrow": b"a" * 800, "dos/b.arrow": b"b" * 800}
            for k, v in ctn.items():
                sib[k] = {"size": 800, "lfs": {"sha256": C.sha256_bytes(v)}}
            dos = ds("dos", archivos=list(ctn))
            estado["datasets"]["lotsa__dos"] = {"estado": "verificada"}

            def con_registrado(nombre, registrado, bajado=()):
                b = f"{tmp}/hf_{nombre}"
                F.RAW_HF = b
                F._registrar(b, f"hf/{R.LOTSA_REPO}/otros/x.arrow", {"bytes": registrado, "sha256": "x"})
                for rel in bajado:  # un fichero del subconjunto ya bajado y registrado
                    os.makedirs(os.path.dirname(f"{b}/{R.LOTSA_REPO}/{rel}"), exist_ok=True)
                    with open(f"{b}/{R.LOTSA_REPO}/{rel}", "wb") as f:
                        f.write(ctn[rel])
                    F._registrar(b, f"hf/{R.LOTSA_REPO}/{rel}", {"bytes": 800, "sha256": C.sha256_bytes(ctn[rel])})
                return b

            b = con_registrado("tope_a", 1500)  # 1500 + 800 = 2300 <= 3000 (el 1.er fichero cabe), 1500 + 1600 = 3100 > 3000
            m = _Mundo(_hub_ok(ctn))
            try:
                F.descargar_hub("lotsa", estado, datasets=[dos], http=m.http())
                raise AssertionError("el subconjunto entero (3100 B) no cabe en 3000 B: debia parar antes del primer fichero")
            except C.TopeLotsa:
                assert m.peticiones == [] and not os.path.exists(f"{b}/{R.LOTSA_REPO}/dos"), "ni un byte del subconjunto"
            b = con_registrado("tope_b", 1000)  # 1000 + 1600 = 2600 <= 3000: cabe y se bajan los dos
            m = _Mundo(_hub_ok(ctn))
            assert F.descargar_hub("lotsa", estado, datasets=[dos], http=m.http()) == []
            assert len(m.a(R.HUB_BASE)) == 2 and F.bytes_lotsa_en_manifiesto() == 1000 + 1600
            # solo cuenta lo PENDIENTE: con a.arrow ya bajado (1000 + 800 registrados) y b pendiente (800) son 2600; contarlo dos
            # veces (3400) bloquearia sin motivo
            b = con_registrado("tope_c", 1000, bajado=["dos/a.arrow"])
            m = _Mundo(_hub_ok(ctn))
            assert F.descargar_hub("lotsa", estado, datasets=[dos], http=m.http()) == []
            assert [p[1] for p in m.a(R.HUB_BASE)] == [F.url_hub(R.LOTSA_REPO, "rev", "dos/b.arrow")], m.peticiones
        finally:
            C.LOTSA_TOTAL_MAX, C.LOTSA_SUBCONJUNTO_MAX = tot0, sub0
    finally:
        F.RAW_HF, F._guarda, F._siblings = raw0, guarda0, sib0


def t_hub_red(tmp):
    """Punto 4 (revision 2): el Hub se descarga con GET propios y la MISMA politica que Binance: User-Agent del proyecto, ritmo de 1
    peticion/s por host (tambien en las redirecciones al CDN), 3 reintentos con espera exponencial, Retry-After, URL fijada a una
    revision, tamano y SHA-256 frente a lo que declara el Hub y rename atomico. Todo con un transporte falso, sin red."""
    contenido = bytes(range(256)) * 20  # 5120 bytes
    h = C.sha256_bytes(contenido)
    rel = "fino/data.arrow"
    d = {"id": "lotsa__fino", "fuente": "lotsa", "repo": R.LOTSA_REPO, "nombre": "fino", "archivos": [rel], "extras": ["fino/dos.arrow"]}
    s = {"size": len(contenido), "lfs": {"sha256": h}}
    clave = f"hf/{R.LOTSA_REPO}/{rel}"
    url = F.url_hub(R.LOTSA_REPO, "rev1", rel)
    assert url == "https://huggingface.co/datasets/Salesforce/lotsa_data/resolve/rev1/fino/data.arrow", url
    base = f"{tmp}/hub_red"
    destino = f"{base}/{R.LOTSA_REPO}/{rel}"
    raw0, guarda0, sib0 = F.RAW_HF, F._guarda, F._siblings
    F.RAW_HF, F._guarda = base, lambda extra: None

    def limpio():
        shutil.rmtree(base, ignore_errors=True)

    try:
        # a) 429 con Retry-After dos veces y luego el exito (con redireccion al CDN): espera 7 s, 7 s; 3 GET al Hub
        limpio()
        n = [0]

        def srv_429(m, req):
            if req.full_url.startswith(R.HUB_BASE):
                n[0] += 1
                if n[0] <= 2:
                    raise _http_error(req.full_url, 429, {"Retry-After": "7"})
                raise _http_error(req.full_url, 302, {"Location": CDN})
            return _Resp(contenido)

        m = _Mundo(srv_429)
        F._bajar_hub(d, rel, s, "rev1", m.http())
        assert m.esperas == [7.0, 7.0], m.esperas  # Retry-After (7) manda sobre la espera exponencial (2, 4)
        assert len(m.a(R.HUB_BASE)) == 3 and len(m.a("https://cdn.hf.test/")) == 1, m.peticiones
        assert all(p[2]["user-agent"] == C.UA == "quantdesk-lab-ingesta/0.1" for p in m.peticiones)  # tambien en el CDN
        _ritmo_ok(m)
        assert open(destino, "rb").read() == contenido and not os.path.exists(destino + ".dl")
        e = F.manifiesto_crudo(base)["archivos"][clave]
        assert e["url"] == url and e["revision"] == "rev1" and e["sha256"] == h and e["bytes"] == len(contenido), e
        assert all("SECRETA" not in u for u, _ in C.PETICIONES), "la URL firmada del CDN no se registra"
        # g) idempotencia: con tamano y hash registrados no hay ni una peticion
        m = _Mundo(srv_429)
        F._bajar_hub(d, rel, s, "rev1", m.http())
        assert m.peticiones == []

        # b) 503 sin parar en el Hub: exactamente 3 reintentos (4 intentos), esperas 2, 4, 8; nada queda en disco ni en el manifiesto
        limpio()
        m = _Mundo(lambda m, req: (_ for _ in ()).throw(_http_error(req.full_url, 503)))
        try:
            F._bajar_hub(d, rel, s, "rev1", m.http())
            raise AssertionError("debia agotar los reintentos")
        except C.ErrorRed as e:
            assert "4 intentos" in str(e), e
        assert len(m.a(R.HUB_BASE)) == C.REINTENTOS + 1 == 4 and m.esperas == [2.0, 4.0, 8.0], (len(m.peticiones), m.esperas)
        _ritmo_ok(m)
        assert not os.path.exists(destino) and not os.path.exists(destino + ".dl") and F.manifiesto_crudo(base)["archivos"] == {}
        # ... y descargar_hub lo trata como no bajado (se documenta) y no sigue con el resto del subconjunto
        F._siblings = lambda estado_lic, fuente: ({rel: s, "fino/dos.arrow": s}, "rev1")
        m = _Mundo(lambda m, req: (_ for _ in ()).throw(_http_error(req.full_url, 503)))
        omit = F.descargar_hub("lotsa", {"datasets": {"lotsa__fino": {"estado": "verificada"}}}, datasets=[d], http=m.http())
        assert [i for i, _ in omit] == [f"lotsa__fino:{rel}"] and len(m.a(R.HUB_BASE)) == 4, (omit, len(m.peticiones))
        F._siblings = sib0

        # c) el 503 llega del CDN tras la redireccion: cada intento son 2 GET (Hub + CDN) y nunca hay mas de 4 intentos
        limpio()

        def srv_cdn_503(m, req):
            if req.full_url.startswith(R.HUB_BASE):
                raise _http_error(req.full_url, 302, {"Location": CDN})
            raise _http_error(req.full_url, 503)

        m = _Mundo(srv_cdn_503)
        try:
            F._bajar_hub(d, rel, s, "rev1", m.http())
            raise AssertionError("debia agotar los reintentos")
        except C.ErrorRed:
            pass
        assert len(m.a(R.HUB_BASE)) == 4 and len(m.a("https://cdn.hf.test/")) == 4 and m.esperas == [2.0, 4.0, 8.0], m.peticiones
        _ritmo_ok(m)

        # d) cuerpo truncado (http.client no avisa): cuenta como fallo del intento y el siguiente reanuda con Range
        limpio()
        n = [0]

        def srv_trunc(m, req):
            if req.full_url.startswith(R.HUB_BASE):
                raise _http_error(req.full_url, 302, {"Location": CDN})
            n[0] += 1
            if n[0] == 1:
                return _Resp(contenido[:3000], headers={"Content-Length": str(len(contenido))})
            assert req.headers.get("Range") == "bytes=3000-", req.headers
            return _Resp(contenido[3000:], 206, {"Content-Length": str(len(contenido) - 3000)})

        m = _Mundo(srv_trunc)
        F._bajar_hub(d, rel, s, "rev1", m.http())
        assert open(destino, "rb").read() == contenido and m.esperas == [2.0], m.esperas

        # i) una redireccion (relativa) dentro del MISMO host, Hub -> Hub -> CDN: cada salto espera su turno de 1 s
        limpio()

        def srv_doble(m, req):
            u = req.full_url
            if u == url:
                raise _http_error(u, 302, {"Location": "/api/resolve-cache/x"})
            if u.startswith(R.HUB_BASE):
                raise _http_error(u, 302, {"Location": CDN})
            return _Resp(contenido)

        m = _Mundo(srv_doble)
        F._bajar_hub(d, rel, s, "rev1", m.http())
        hub = m.a(R.HUB_BASE)
        assert len(hub) == 2 and hub[1][1] == R.HUB_BASE + "/api/resolve-cache/x" and hub[1][0] - hub[0][0] >= 1.0, m.peticiones
        _ritmo_ok(m)

        # e) contenido que no casa con lo que declara el Hub: se rechaza y no queda nada (ni destino ni temporal ni manifiesto)
        for malo, motivo in ((bytes([contenido[0] ^ 1]) + contenido[1:], "sha256"), (contenido + b"!", "bytes descargados")):
            limpio()
            m = _Mundo(_hub_ok({rel: malo}))
            try:
                F._bajar_hub(d, rel, s, "rev1", m.http())
                raise AssertionError("debia rechazar un contenido que no casa con el Hub")
            except RuntimeError as err:
                assert motivo in str(err), err
            assert not os.path.exists(destino) and not os.path.exists(destino + ".dl") and F.manifiesto_crudo(base)["archivos"] == {}
        limpio()
        pequeno = b'{"a": 1}'  # fichero sin LFS: se verifica con el git blob id
        s2 = {"size": len(pequeno), "blobId": C.git_blob_sha1(pequeno)}
        F._bajar_hub(d, "fino/dos.arrow", s2, "rev1", _Mundo(_hub_ok({"fino/dos.arrow": pequeno})).http())
        assert F.manifiesto_crudo(base)["archivos"][f"hf/{R.LOTSA_REPO}/fino/dos.arrow"]["verificado_contra"] == "git blob id del Hub"
        try:
            F._bajar_hub(d, "fino/tres.arrow", {"size": 3}, "rev1", _Mundo(_hub_ok({})).http())
            raise AssertionError("sin hash declarado por el Hub no se puede verificar")
        except RuntimeError:
            pass

        # f) un 404 no se reintenta; h) una redireccion que no es https tampoco
        limpio()
        m = _Mundo(lambda m, req: (_ for _ in ()).throw(_http_error(req.full_url, 404)))
        try:
            F._bajar_hub(d, rel, s, "rev1", m.http())
            raise AssertionError("404")
        except C.ErrorRed:
            assert len(m.peticiones) == 1 and m.esperas == []
        m = _Mundo(lambda m, req: (_ for _ in ()).throw(_http_error(req.full_url, 302, {"Location": "http://cdn.hf.test/x"})))
        try:
            F._bajar_hub(d, rel, s, "rev1", m.http())
            raise AssertionError("redireccion a http")
        except C.ErrorRed as err:
            assert "https" in str(err) and len(m.peticiones) == 1
        # Retry-After en fecha HTTP, ademas de en segundos
        t0 = dt.datetime(2026, 11, 8, 10, 0, 0, tzinfo=dt.timezone.utc)
        assert C.parse_retry_after("Sun, 08 Nov 2026 10:00:30 GMT", t0) == 30.0
        assert C.parse_retry_after("Sun, 08 Nov 2026 09:59:00 GMT", t0) == 0.0 and C.parse_retry_after("-3") == 0.0
        assert C.parse_retry_after("ni idea", t0) is None

        # j) revision 3 (MEDIA): Retry-After 120 s (> ESPERA_MAX) en el Hub: una sola peticion, ninguna espera, y descargar_hub lo deja en
        # "no bajado" con el motivo (no sigue con el resto del subconjunto); con 30 s se espera 30 s y se baja
        limpio()
        F._siblings = lambda estado_lic, fuente: ({rel: s, "fino/dos.arrow": s}, "rev1")
        m = _Mundo(lambda m, req: (_ for _ in ()).throw(_http_error(req.full_url, 429, {"Retry-After": "120"})))
        omit = F.descargar_hub("lotsa", {"datasets": {"lotsa__fino": {"estado": "verificada"}}}, datasets=[d], http=m.http())
        assert [i for i, _ in omit] == [f"lotsa__fino:{rel}"] and len(m.peticiones) == 1 and m.esperas == [], (omit, m.peticiones, m.esperas)
        assert "el servidor pide esperar 120 s; se reintentara en otra ejecucion" in omit[0][1], omit
        assert not os.path.exists(destino) and F.manifiesto_crudo(base)["archivos"] == {}
        n = [0]

        def srv_30(m, req):
            if req.full_url.startswith(R.HUB_BASE):
                n[0] += 1
                if n[0] == 1:
                    raise _http_error(req.full_url, 429, {"Retry-After": "30"})
                raise _http_error(req.full_url, 302, {"Location": CDN})
            return _Resp(contenido)

        m = _Mundo(srv_30)
        F._bajar_hub(d, rel, s, "rev1", m.http())
        assert m.esperas == [30.0] and open(destino, "rb").read() == contenido, m.esperas
    finally:
        F.RAW_HF, F._guarda, F._siblings = raw0, guarda0, sib0
        limpio()


def t_sin_hf_hub():
    """Punto 4: ningun modulo de la ingesta usa huggingface_hub para la red (hf_hub_download, snapshot_download, HfApi...): solo
    scan_cache_dir (local) y la version."""
    import ast

    aqui = os.path.dirname(os.path.abspath(__file__))
    n = 0
    for ruta in glob.glob(aqui + "/*.py") + [os.path.join(os.path.dirname(aqui), "ingesta_publica.py")]:
        if os.path.basename(ruta) == "selftests.py":
            continue
        n += 1
        arbol = ast.parse(open(ruta, encoding="utf-8").read())
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom) and (nodo.module or "").split(".")[0] == "huggingface_hub":
                assert {a.name for a in nodo.names} <= {"scan_cache_dir"}, (ruta, [a.name for a in nodo.names])
            if isinstance(nodo, ast.Attribute) and isinstance(nodo.value, ast.Name) and nodo.value.id == "huggingface_hub":
                assert nodo.attr == "__version__", (ruta, nodo.attr)
    assert n >= 8, n


def t_guarda_incremental(tmp):
    """Punto 2 (revision 2): la guarda de 100 GB se aplica ANTES de CADA lote con los bytes REALES ya escritos. Una escritura que
    supera el presupuesto a mitad (la reserva previa pasa, el parquet real no) para y no deja ningun parquet parcial."""
    GB = 10**9
    libre = lambda u: {"C:/": 5 * GB, "E:/": 300 * GB}[u]  # noqa: E731
    C.guarda_lote(40 * GB, 5 * GB, 10 * GB, 5 * GB, libre)
    assert C.guarda_lote(80 * GB, 5 * GB, 10 * GB, 5 * GB, libre)["total_previsto_bytes"] == 100 * GB  # justo en el limite
    for args, exc in (((80 * GB + 1, 5 * GB, 10 * GB, 5 * GB), C.PresupuestoExcedido),  # un byte mas
                      ((0, 140 * GB, 0, 0), C.ParadaDisco)):  # E: quedaria bajo 150 GiB DESPUES de escribir el lote
        try:
            C.guarda_lote(*args, libre)
            raise AssertionError(args)
        except exc:
            pass
    try:
        C.guarda_lote(0, 1, 0, 0, lambda u: {"C:/": C.C_LIBRE_MIN - 1, "E:/": 300 * GB}[u])
        raise AssertionError("C: bajo su suelo")
    except C.ParadaDisco:
        pass

    # escritura real con series sinteticas (valores aleatorios: incompresibles) en lotes de 1200 filas
    e = entrada(R.NO_FIN, id_="chronos__inc")
    rng = np.random.default_rng(7)
    sint = [LEC.Serie(f"S{i:02d}", diarias(ms(2010, 1, 1), 400)[0], rng.random(400)) for i in range(12)]
    orig_series, orig_lote, cache0 = LEC.series, FI.FILAS_POR_LOTE, C.bytes_cache_hf
    LEC.series, FI.FILAS_POR_LOTE = (lambda entry, con_ts=True: iter(sint)), 1000
    C.bytes_cache_hf = lambda *a, **k: 0  # el presupuesto del test es de bytes: la cache real de HF no entra en la cuenta
    try:
        an = FI.analizar(e, CORTE, AHORA)
        lados = {r["clave"]: "train" for r in an["registros"]}
        salida = f"{tmp}/inc"
        reg = []
        man = FI.procesar_dataset(e, an, lados, salida, "2016-10-01", {}, [{"bytes": 1000}], guarda=_sin_guarda,
                                  guarda_lote=lambda escrito, cota, usado, cache: reg.append((escrito, cota)) or {})
        assert len(reg) == 5, reg  # 4 lotes de 1200 filas + el control de los pies al cerrar
        assert reg[0][0] == 0 and all(reg[i][0] < reg[i + 1][0] for i in range(4)), reg  # bytes REALES, crecientes
        assert all(reg[i + 1][0] - reg[i][0] <= reg[i][1] for i in range(4)), reg  # la cota es una cota: cada lote cabe en ella
        total = man["ficheros"][0]["bytes"]
        assert reg[4][0] <= total <= reg[4][0] + reg[4][1], (reg[4], total)  # lo escrito + los pies cabe en lo ultimo comprobado
        # revision 3 (BAJA): el control final suma una reserva FIJA de 64 MiB para manifest.json y su .tmp (se escriben despues)
        n_pq = len(man["ficheros"])
        assert C.RESERVA_AUXILIAR == 64 * 1024**2 and reg[4][1] == FI.MARGEN_PARQUET * n_pq + C.RESERVA_AUXILIAR, reg[4]

        def con_final(delta):  # solo el control final (5.a llamada) aplica el presupuesto: lo escrito + los pies + la reserva + delta
            nn = [0]

            def gl(escrito, cota, usado, cache):
                nn[0] += 1
                if nn[0] == 5:
                    return C.guarda_lote(escrito, cota, usado, cache, libre_fn=libre,
                                         presupuesto=escrito + FI.MARGEN_PARQUET * n_pq + C.RESERVA_AUXILIAR + delta)
                return {}
            return gl

        FI.procesar_dataset(e, an, lados, f"{tmp}/inc_fin_ok", "2016-10-01", {}, [], guarda=_sin_guarda, guarda_lote=con_final(0))  # justo: pasa
        try:  # parquet + pies caben, pero NO la reserva del manifiesto (un byte menos): para y no deja nada
            FI.procesar_dataset(e, an, lados, f"{tmp}/inc_fin", "2016-10-01", {}, [], guarda=_sin_guarda, guarda_lote=con_final(-1))
            raise AssertionError("sin sitio para la reserva del manifiesto debia parar")
        except C.PresupuestoExcedido:
            assert os.listdir(f"{tmp}/inc_fin") == [], os.listdir(f"{tmp}/inc_fin")
        # un dataset sin ninguna serie escribible (todas excluidas) solo escribe el manifiesto: misma reserva fija
        LEC.series = lambda entry, con_ts=True: iter([LEC.Serie("V1", None, np.array([])), LEC.Serie("V2", None, np.full(5, np.nan))])
        an0 = FI.analizar(e, CORTE, AHORA)
        vistas0 = []
        man0 = FI.procesar_dataset(e, an0, {}, f"{tmp}/inc_vacio", "2016-10-01", {}, [], guarda=_sin_guarda,
                                   guarda_lote=lambda escrito, cota, usado, cache: vistas0.append((escrito, cota)) or {})
        assert man0["ficheros"] == [] and vistas0 == [(0, C.RESERVA_AUXILIAR)], (man0["ficheros"], vistas0)
        LEC.series = lambda entry, con_ts=True: iter(sint)

        # la reserva previa (2 x crudo = 2000 B) pasa; en el 3.er lote, lo ya escrito mas su cota supera el presupuesto: PARA
        pres = reg[2][0] + reg[2][1] - 1
        llamadas = []

        def guarda_lote(escrito, cota, usado, cache):
            llamadas.append(escrito)
            return C.guarda_lote(escrito, cota, usado, cache, libre_fn=libre, presupuesto=pres)

        try:
            FI.procesar_dataset(e, an, lados, salida, "2016-10-01", {}, [{"bytes": 1000}], usado_previo=0,
                                guarda=lambda extra, usado, cache: C.guarda(extra, usado, cache, libre_fn=libre, presupuesto=pres),
                                guarda_lote=guarda_lote)
            raise AssertionError("la escritura real supera el presupuesto a mitad: debia parar")
        except C.PresupuestoExcedido as err:
            assert "cota del siguiente lote" in str(err), err
        assert len(llamadas) == 3 and llamadas[0] == 0 and llamadas[2] > 0, llamadas  # paro en el 3.er lote, con bytes ya escritos
        # ya habia 2 lotes escritos y no queda NADA: ni un parquet parcial ni manifiesto (el dataset anterior se habia reemplazado)
        assert os.listdir(salida) == [] and glob.glob(f"{salida}/**/*.parquet", recursive=True) == [], os.listdir(salida)

        # sin dataset anterior: tras una parada a mitad (presupuesto o suelo de disco) o un fallo de lectura no queda ni un parquet
        def lectura_rota(entry, con_ts=True):
            yield from sint[:7]
            raise OSError("lectura rota a mitad")

        for nombre, falla in (("presupuesto", C.PresupuestoExcedido("sin presupuesto")), ("disco", C.ParadaDisco("sin disco")),
                              ("lectura", None)):
            salida2 = f"{tmp}/inc_{nombre}"
            n = [0]

            def gl(escrito, cota, usado, cache, falla=falla):
                n[0] += 1
                if falla is not None and n[0] == 2:
                    raise falla
                return {}

            if falla is None:
                LEC.series = lectura_rota
            try:
                FI.procesar_dataset(e, an, lados, salida2, "2016-10-01", {}, [], guarda=_sin_guarda, guarda_lote=gl)
                raise AssertionError(nombre)
            except (C.PresupuestoExcedido, C.ParadaDisco, OSError):
                pass
            assert glob.glob(f"{salida2}/**/*.parquet", recursive=True) == [] and os.listdir(salida2) == [], (nombre, os.listdir(salida2))
            LEC.series = lambda entry, con_ts=True: iter(sint)
        # el borrado reintenta si un fichero esta un instante en uso (Windows: antivirus, indexador) y avisa si no lo consigue
        rmtree0, dormidos, fallos = shutil.rmtree, [], [0]

        def rmtree_ocupado(ruta, ignore_errors=False):
            fallos[0] += 1
            if fallos[0] > 2:  # las dos primeras veces "no puede" borrar
                rmtree0(ruta, ignore_errors=ignore_errors)

        os.makedirs(f"{tmp}/ocupada/x")
        shutil.rmtree = rmtree_ocupado
        try:
            assert FI.borrar_carpeta(f"{tmp}/ocupada", dormir=dormidos.append) and dormidos == [0.5, 1.0] and not os.path.exists(f"{tmp}/ocupada")
            os.makedirs(f"{tmp}/ocupada/x")
            fallos[0] = -100  # nunca puede
            assert not FI.borrar_carpeta(f"{tmp}/ocupada", intentos=3, dormir=lambda s: None) and os.path.isdir(f"{tmp}/ocupada")
        finally:
            shutil.rmtree = rmtree0
    finally:
        LEC.series, FI.FILAS_POR_LOTE, C.bytes_cache_hf = orig_series, orig_lote, cache0


def t_procesar_parada():
    """Punto 5 (revision 2, BAJA): 'procesar' ante PresupuestoExcedido o ParadaDisco da 'PARADA: ...' y sale 3, sin traceback."""
    import argparse
    import contextlib
    import importlib

    ip = importlib.import_module("ingesta_publica")
    correr0, estado0 = FI.correr, ip._estado_licencias
    ip._estado_licencias = lambda: {"datasets": {}}
    try:
        for exc in (C.PresupuestoExcedido("101.00 GB superan 100 GB"), C.ParadaDisco("E: sin espacio"), C.CacheNoMedible("cache")):
            def correr_falso(*a, exc=exc, **k):
                raise exc

            FI.correr = correr_falso
            for llamada in (lambda: ip.cmd_procesar(argparse.Namespace(corte="2016-10-01")), lambda: ip.main(["procesar"])):
                salida = io.StringIO()
                with contextlib.redirect_stdout(salida):
                    rc = llamada()
                assert rc == 3 and salida.getvalue().startswith("PARADA: ") and str(exc) in salida.getvalue(), (rc, salida.getvalue())
    finally:
        FI.correr, ip._estado_licencias = correr0, estado0


def _escribir_bytes(ruta: str, n: int) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "wb") as f:
        f.write(b"x" * n)


def t_temporales(tmp):
    """Revision 3 (MEDIA): los temporales de descarga abandonados (.dl.part, .dl, .part, .tmp bajo data/public) entran en la guarda de
    100 GB aunque ningun manifiesto los registre, y se CONSERVAN para que la reanudacion con Range siga funcionando entre ejecuciones."""
    GB = 10**9
    libre = lambda u: {"C:/": 5 * GB, "E:/": 300 * GB}[u]  # noqa: E731
    # a) bytes_temporales: solo los temporales, a cualquier profundidad; un directorio ausente son 0 bytes; no se mide a medias
    pub = f"{tmp}/pub_t"
    for rel, n in (("hf/r/a.arrow.dl.part", 2000), ("hf/r/b.arrow.dl", 300), ("binance/x/y.zip.part", 40),
                   ("hf/raw_manifest.json.tmp", 5), ("hf/r/.cache/z.incomplete", 7), ("hf/r/real.arrow", 99_999),
                   ("binance/x/y.zip.CHECKSUM", 70)):
        _escribir_bytes(f"{pub}/{rel}", n)
    assert C.bytes_temporales(pub) == 2000 + 300 + 40 + 5 + 7 and C.bytes_temporales(f"{tmp}/no_existe") == 0
    try:
        C.bytes_temporales(pub, max_ficheros=3)
        raise AssertionError("un recorrido que no cabe en el limite debe abortar, no devolver un subtotal")
    except C.TemporalesNoMedibles as e:
        assert "no se pueden medir" in str(e) and isinstance(e, C.ParadaDisco)
    # b) C.guarda suma los temporales
    assert C.guarda(1000, 4000, 0, libre, presupuesto=10_000, usado_temporales=5000)["total_previsto_bytes"] == 10_000  # justo
    try:
        C.guarda(1001, 4000, 0, libre, presupuesto=10_000, usado_temporales=5000)
        raise AssertionError("un byte mas sobre el limite")
    except C.PresupuestoExcedido as e:
        assert "temporales de descarga 0.00" in str(e) and "superan" in str(e), e
    # c) la guarda de descarga REAL (fuentes._guarda: Hub y Binance): un .part abandonado de tamano conocido la hace saltar cuando, sin
    # el, el fichero cabria; y el .part sigue en disco
    base = f"{tmp}/pub_g"
    salvado = (F.RAW_HF, F.RAW_BINANCE, C.PUBLIC, C.DATASETS, C.PRESUPUESTO, C.bytes_cache_hf, F._guarda, F._siblings)
    F.RAW_HF, F.RAW_BINANCE, C.PUBLIC, C.DATASETS, C.PRESUPUESTO = f"{base}/hf", f"{base}/binance", base, f"{base}/datasets", 10_000
    C.bytes_cache_hf = lambda *a, **k: 0
    real = F._guarda
    F._guarda = lambda extra: real(extra, libre)  # el suelo de C:/E: del selftest no depende del disco real
    try:
        F._registrar(F.RAW_HF, "hf/r/registrado.arrow", {"bytes": 4000, "sha256": "x"})
        real(5000, libre)  # 4000 + 5000 <= 10000: cabe
        parcial = f"{base}/hf/r/x.arrow.dl.part"
        _escribir_bytes(parcial, 2000)
        for extra, ok in ((4000, True), (4001, False)):  # 4000 + 2000 + 4000 = 10000 justo; un byte mas, no
            try:
                real(extra, libre)
                assert ok, extra
            except C.PresupuestoExcedido as e:
                assert not ok and "temporales de descarga" in str(e), (extra, e)
        assert os.path.getsize(parcial) == 2000, "el temporal se conserva (reanudacion con Range), no se borra"
        os.remove(parcial)  # y lo mismo con un .part de Binance (la guarda de _bajar_binance es la misma)
        _escribir_bytes(f"{base}/binance/data/spot/monthly/klines/P/1d/P-1d-2020-01.zip.part", 2000)
        try:
            real(5000, libre)
            raise AssertionError("el .part de Binance no entro en la guarda")
        except C.PresupuestoExcedido:
            pass
        os.remove(f"{base}/binance/data/spot/monthly/klines/P/1d/P-1d-2020-01.zip.part")

        # d) de punta a punta: una descarga del Hub agota los reintentos (503) tras dejar 3000 bytes; el bucle sigue con el SIGUIENTE
        # subconjunto, y su guarda cuenta ese .dl.part: no se baja nada mas. Con presupuesto otra vez, la reanudacion usa Range.
        contenido = bytes(range(256)) * 20  # 5120 bytes
        s = {"size": len(contenido), "lfs": {"sha256": C.sha256_bytes(contenido)}}
        ds = lambda n: {"id": f"chronos__{n}", "fuente": "chronos", "repo": "autogluon/chronos_datasets", "nombre": n,  # noqa: E731
                        "archivos": [f"{n}/data.arrow"], "extras": []}
        estado = {"datasets": {"chronos__a": {"estado": "verificada"}, "chronos__b": {"estado": "verificada"}}}
        F._siblings = lambda estado_lic, fuente: ({"a/data.arrow": s, "b/data.arrow": s}, "rev1")
        shutil.rmtree(base, ignore_errors=True)
        C.PRESUPUESTO = 8000  # un fichero (5120) cabe; el parcial abandonado (3000) mas otro fichero (5120) no
        n = [0]

        def srv_cae(m, req):
            if req.full_url.startswith(R.HUB_BASE):
                raise _http_error(req.full_url, 302, {"Location": CDN})
            n[0] += 1
            if n[0] == 1:
                return _Resp(contenido[:3000], headers={"Content-Length": str(len(contenido))})  # cuerpo truncado
            raise _http_error(req.full_url, 503)

        m = _Mundo(srv_cae)
        try:
            F.descargar_hub("chronos", estado, datasets=[ds("a"), ds("b")], http=m.http())
            raise AssertionError("el .dl.part abandonado de a (3000 B) + b (5120 B) supera 8000 B: la guarda de b debia saltar")
        except C.PresupuestoExcedido as e:
            assert "temporales de descarga 0.00" in str(e) and "superan" in str(e), e
        abandonado = f"{base}/hf/autogluon/chronos_datasets/a/data.arrow.dl.part"
        assert os.path.getsize(abandonado) == 3000 and len(m.a(R.HUB_BASE)) == 4, (os.path.exists(abandonado), len(m.peticiones))
        assert not [p for p in m.peticiones if "/b/data.arrow" in p[1]], "de b no se pidio ni un byte"
        assert F.manifiesto_crudo(F.RAW_HF)["archivos"] == {}  # y no esta en ningun manifiesto: solo la guarda de temporales lo ve
        assert C.bytes_temporales(base) == 3000
        # otra ejecucion con presupuesto: reanuda con Range desde el parcial conservado y lo deja verificado y sin temporales
        C.PRESUPUESTO = 10**9

        def srv_reanuda(m, req):
            if req.full_url.startswith(R.HUB_BASE):
                raise _http_error(req.full_url, 302, {"Location": CDN})
            assert req.headers.get("Range") == "bytes=3000-", req.headers
            return _Resp(contenido[3000:], 206, {"Content-Length": str(len(contenido) - 3000)})

        assert F.descargar_hub("chronos", estado, datasets=[ds("a")], http=_Mundo(srv_reanuda).http()) == []
        assert open(f"{base}/hf/autogluon/chronos_datasets/a/data.arrow", "rb").read() == contenido and C.bytes_temporales(base) == 0
    finally:
        F.RAW_HF, F.RAW_BINANCE, C.PUBLIC, C.DATASETS, C.PRESUPUESTO, C.bytes_cache_hf, F._guarda, F._siblings = salvado


def t_csv_resumen(tmp):
    """Revision 3 (BAJA): filtro_ids.csv y filtro_resumen.json (y su .tmp) se escriben tras la ultima guarda de los parquet: su guarda suma
    el tamano exacto del CSV (en memoria) mas la reserva fija de 64 MiB, y si salta no se escribe nada."""
    GB = 10**9
    libre = lambda u: {"C:/": 5 * GB, "E:/": 300 * GB}[u]  # noqa: E731
    filas = [("chronos__x", "a", "excluida", "m", 10, 0, 0), ("chronos__x", 'b"c', "cortada", "x", 5, 2, 3)]
    cache0, C.bytes_cache_hf = C.bytes_cache_hf, lambda *a, **k: 0
    try:
        reg = []
        res = {"corte": "2016-10-01"}
        FI.escribir_csv_y_resumen(f"{tmp}/inf", filas, res, 7, guarda=lambda extra, usado, cache: reg.append((extra, usado)) or {})
        ruta = f"{tmp}/inf/filtro_ids.csv"
        tam = os.path.getsize(ruta)
        assert reg == [(tam + C.RESERVA_AUXILIAR, 7)], reg
        with open(ruta, "rb") as f:
            assert f.read() == ('dataset,series_id,accion,motivo,puntos,puntos_tronco,puntos_adaptadores\n'
                                '"chronos__x","a","excluida","m",10,0,0\n"chronos__x","b\'c","cortada","x",5,2,3\n').encode()
        assert res["csv"] == {"ruta": ruta, "sha256": C.sha256_fichero(ruta), "filas": 2, "bytes": tam}
        assert C.leer_json(f"{tmp}/inf/filtro_resumen.json")["csv"]["bytes"] == tam and not os.path.exists(f"{tmp}/inf/filtro_resumen.json.tmp")
        # limite exacto con la guarda real: usado + CSV + reserva cabe justo; un byte menos de presupuesto (el CSV solo cabria) para
        justo = 7 + tam + C.RESERVA_AUXILIAR
        guarda_con = lambda pres: (lambda extra, usado, cache: C.guarda(extra, usado, cache, libre_fn=libre, presupuesto=pres))  # noqa: E731
        FI.escribir_csv_y_resumen(f"{tmp}/inf_ok", filas, {}, 7, guarda=guarda_con(justo))
        try:
            FI.escribir_csv_y_resumen(f"{tmp}/inf_no", filas, {}, 7, guarda=guarda_con(justo - 1))
            raise AssertionError("sin sitio para la reserva debia parar")
        except C.PresupuestoExcedido:
            assert not os.path.exists(f"{tmp}/inf_no"), "si la guarda salta no se escribe ni el CSV ni el resumen"
    finally:
        C.bytes_cache_hf = cache0


def t_verificar(tmp):
    """Puntos 5 y 6: filas alteradas, directorio vacio, dataset esperado ausente o inesperado => problemas."""
    from . import verificar as V

    bueno = f"{tmp}/ds1"  # lo escribio t_extremo_a_extremo
    problemas = []
    n = V.verificar_datasets(bueno, {"chronos__sint"}, problemas)
    assert n > 0 and problemas == [], problemas
    # punto 5: un manifiesto con filas alteradas falla (el parquet no cambia)
    malo = f"{tmp}/dsmal"
    shutil.copytree(bueno, malo)
    ruta = f"{malo}/chronos__sint/manifest.json"
    man = C.leer_json(ruta)
    man["ficheros"][0]["filas"] += 1
    C.escribir_json(ruta, man)
    problemas = []
    V.verificar_datasets(malo, {"chronos__sint"}, problemas)
    assert any("filas distintas" in p for p in problemas), problemas
    assert any("total de filas" in p for p in problemas), problemas
    esc = FI.comprobar_escrito(malo, V.cargar_manifiestos(malo))
    assert len(esc["filas_distintas_del_manifiesto"]) == 1, esc
    # punto 6: la verificacion no pasa en vacio
    os.makedirs(f"{tmp}/vacio")
    problemas = []
    assert V.verificar_datasets(f"{tmp}/vacio", {"chronos__sint"}, problemas) == 0
    assert any("no hay manifiestos" in p for p in problemas), problemas
    problemas = []
    V.verificar_datasets(f"{tmp}/vacio", set(), problemas)  # ni siquiera sin esperados: un directorio vacio no es una verificacion
    assert any("no hay manifiestos" in p for p in problemas), problemas
    # y se contrasta con lo esperado: uno ausente y uno inesperado son problemas
    problemas = []
    V.verificar_datasets(bueno, {"chronos__sint", "lotsa__ausente"}, problemas)
    assert problemas == ["falta el dataset esperado (licencia verificada y crudo completo): lotsa__ausente"], problemas
    problemas = []
    V.verificar_datasets(bueno, set(), problemas)
    assert any("no se esperaba" in p for p in problemas), problemas
    # los esperados salen del registro: licencia verificada y todo el crudo registrado
    e0 = R.DATASETS[0]
    crudo = {k: {} for k in LEC.rutas_crudo(e0)}
    ver = {"datasets": {e0["id"]: {"estado": "verificada"}}}
    assert [e["id"] for e in FI.datasets_esperados(ver, crudo)] == [e0["id"]]
    assert FI.datasets_esperados(ver, {}) == []  # falta el crudo
    assert FI.datasets_esperados({"datasets": {e0["id"]: {"estado": "excluida"}}}, crudo) == []  # sin licencia
    assert FI.datasets_esperados(None, crudo) == []


def correr():
    tmp = f"{C.TMP}/selftest-{os.getpid()}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    try:
        for nombre, f in (("decidir", t_decidir), ("particion", t_particion), ("guarda", t_guarda), ("red", t_red),
                          ("sin_hf_hub", t_sin_hf_hub), ("procesar_parada", t_procesar_parada)):
            f()
            print(f"  ok {nombre}")
        for nombre, f in (("lectores", t_lectores), ("licencias", t_licencias), ("extremo_a_extremo", t_extremo_a_extremo),
                          ("guarda_incremental", t_guarda_incremental), ("binance_idempotencia", t_binance_idempotencia),
                          ("cache_hf", t_cache_hf), ("topes_lotsa", t_topes_lotsa), ("hub_red", t_hub_red),
                          ("temporales", t_temporales), ("csv_resumen", t_csv_resumen), ("verificar", t_verificar)):
            f(tmp)
            print(f"  ok {nombre}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
