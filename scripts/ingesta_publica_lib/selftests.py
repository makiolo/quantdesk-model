"""Autoprueba de la ingesta publica (sin red, con datos sinteticos). La lanza `ingesta_publica.py --selftest`."""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import shutil
import urllib.error
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
            man = FI.procesar_dataset(e, an, lados, f"{tmp}/ds{k}", "2016-10-01", {"licencia": "x"}, [])
            h.append((man["dataset_sha256"], man["contenido_sha256"]))
        assert h[0] == h[1], "reaplicar el filtro debe dar el mismo hash de dataset"
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
        mal = FI.comprobar_escrito(f"{tmp}/mal", {"x": {"ficheros": [{"ruta": f"tronco.{sp}.parquet", "split": sp} for sp in ("train", "val")]}})
        assert mal["ids_en_ambos_lados"] == 1 and mal["contenidos_en_ambos_lados"] == 1, mal
        # otro corte: mismo crudo, otro reparto, sin descargar nada
        an2 = FI.analizar(e, FI.corte_ms("2016-09-01"), AHORA)
        assert FI.estadisticas(e, an2)["puntos_tronco"] != st["puntos_tronco"]
    finally:
        LEC.series = orig


def correr():
    tmp = f"{C.TMP}/selftest-{os.getpid()}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    try:
        for nombre, f in (("decidir", t_decidir), ("particion", t_particion), ("guarda", t_guarda), ("red", t_red)):
            f()
            print(f"  ok {nombre}")
        for nombre, f in (("lectores", t_lectores), ("licencias", t_licencias), ("extremo_a_extremo", t_extremo_a_extremo)):
            f(tmp)
            print(f"  ok {nombre}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
