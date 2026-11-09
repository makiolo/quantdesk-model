"""Selftest del publicador MT5 -> qn: sin red real y sin terminal. qn falso en 127.0.0.1 (qn_falso.py) y el modulo
MetaTrader5 falso del extractor, siempre a traves de la envoltura de solo lectura. Ficheros bajo
E:/quantdesk-lab/tmp/TI-12-MT5/ y se borran al terminar."""
from __future__ import annotations

import collections
import contextlib
import glob
import io
import json
import os
import shutil
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from extractor_mt5_lib import falso as FA
from extractor_mt5_lib import hora as HR
from extractor_mt5_lib import lectura as LT
from extractor_mt5_lib.selftests import CRED, PROHIBIDAS, utc

from . import nucleo as N
from . import qn as Q
from . import qn_falso as QF

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = "E:/quantdesk-lab/tmp/TI-12-MT5"
TOKEN = "qn-token-falso-3f9a8c"
REGLA = HR.regla_desde_texto("ny+7")
SIMS = {"EURUSD.a": "EURUSD", "USDJPY": "USDJPY"}
INTERVALOS = ("1d", "1h", "5m")
DESDE = "2026-10-26"


class Banco:
    """Lanza `ejecutar` del CLI con MT5 falso, credenciales y token falsos, un reloj fijo y la flota de qn falsa."""

    def __init__(self, ejecutar, raiz: str) -> None:
        self.ejecutar, self.raiz, self.salidas, self.falsos = ejecutar, raiz, [], []

    def __call__(self, flota: QF.Flota | None, ahora: int, extra=(), token=TOKEN, modo="--ejecutar", **kw) -> tuple[int, str]:
        def fabrica():
            f = FA.MT5Falso(ahora_utc_s=ahora, trampas=PROHIBIDAS, cuenta=dict(CRED), abierto=False)
            self.falsos.append(f)
            return LT.TerminalSoloLectura(f)

        def cargar_token():
            if token is None:
                raise AssertionError("se pidio el token en una simulacion")
            return token

        argv = [modo, "--simbolos", ",".join(SIMS), "--intervalos", ",".join(INTERVALOS), "--desde", DESDE,
                "--hilos", "4", "--ventana", "16", *extra]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            c = self.ejecutar(argv, fabrica=fabrica, cargar_cred=lambda a: LT.Credenciales(**CRED),
                              cargar_token=cargar_token, urls=flota.urls if flota else [], reloj=lambda: float(ahora),
                              runs=os.path.join(self.raiz, "runs"), guarda=lambda: None, espera_max_s=0.01, **kw)
        self.salidas.append(buf.getvalue())
        return c, buf.getvalue()

    def ultimo(self) -> dict:
        with open(os.path.join(self.raiz, "runs", "ultimo.json"), encoding="utf-8") as f:
            return json.load(f)


def esperado(ahora: int) -> dict:
    """ts (ns) de las velas cerradas que MT5 tiene desde DESDE hasta `ahora`, por (simbolo, intervalo)."""
    env = LT.TerminalSoloLectura(FA.MT5Falso(ahora_utc_s=ahora, cuenta=dict(CRED)))
    env.initialize(path=CRED["path"])
    env.login(CRED["login"], password=CRED["password"], server=CRED["server"])
    out = {}
    for sim, base in SIMS.items():
        info = {"punto": 10.0 ** -FA.SIMBOLOS[sim][2], "digitos": FA.SIMBOLOS[sim][2], "precio_velas": "bid"}
        for iv in INTERVALOS:
            b = N.barras_cerradas(env, sim, info, iv, REGLA, utc(2026, 10, 26), ahora)
            out[(base, iv)] = [int(x) * 1_000_000 for x in b["ts_utc_ms"]]
    return out


def en_qn(almacen: QF.Almacen) -> dict:
    out = collections.defaultdict(list)
    for o in almacen.objetos:
        out[(o["tags"]["symbol"], o["tags"]["interval"])].append(o["ts"])
    return {k: sorted(v) for k, v in out.items()}


def sin_duplicados(almacen: QF.Almacen) -> None:
    rep = [k for k, n in almacen.publicados().items() if n > 1]
    assert not rep, f"objetos repetidos en qn: {rep[:3]}"


def prueba_codificacion() -> None:
    tags = {"symbol": "EURUSD", "interval": "1h", "source": "mt5"}
    obj = {"open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 10.0, "date": "2026-11-04T10:00:00Z", "source": "mt5"}
    c1, b1 = Q.codificar("market.ohlcv", tags, obj, 1_793_000_000_000_000_000)
    c2, b2 = Q.codificar("market.ohlcv", dict(reversed(list(tags.items()))), dict(obj), 1_793_000_000_000_000_000)
    assert b1 == b2 and json.loads(c1)["batch_id"] == b1  # independiente del orden de claves
    assert Q.codificar("market.ohlcv", tags, {**obj, "close": 1.16}, 1_793_000_000_000_000_000)[1] != b1
    for malo in ({**tags, "symbol": ""}, {**tags, "symbol": "x" * 300}):
        try:
            Q.codificar("market.ohlcv", malo, obj, 1)
        except ValueError:
            pass
        else:
            raise AssertionError(malo)
    assert Q.ts_ns_de(1_793_000_000_123_456_789) == 1_793_000_000_123_456_789
    assert Q.ts_ns_de("2026-11-04T10:00:00.000123Z") == utc(2026, 11, 4, 10) * 10 ** 9 + 123_000
    # Fechas en UTC de verdad: 1d como fecha y el resto con Z.
    cfg = N.Config(urls=[])
    b = {"ts_utc_ms": np.array([utc(2026, 11, 3, 22) * 1000]), "open": np.array([1.0]), "high": np.array([1.0]),
         "low": np.array([1.0]), "close": np.array([1.0]), "tick_volume": np.array([7])}
    assert N.objeto(cfg, "EURUSD", "1d", b, 0)[1]["date"] == "2026-11-03"
    assert N.objeto(cfg, "EURUSD", "1h", b, 0)[1]["date"] == "2026-11-03T22:00:00Z"
    assert N.objeto(cfg, "EURUSD", "1h", b, 0)[0] == {"symbol": "EURUSD", "interval": "1h", "source": "mt5"}


def prueba_cliente_reintentos_y_errores() -> None:
    alm = QF.Almacen(TOKEN)
    flota = QF.Flota(alm, vivas=2, caida=True)
    esperas = []
    try:
        cli = Q.ClienteQn(flota.urls, TOKEN, espera_max_s=0.5, dormir=esperas.append)
        alm.fallos_503["r0"] = 2
        tags = {"symbol": "EURUSD", "interval": "1h", "source": "mt5"}
        obj = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0, "date": "x", "source": "mt5"}
        for k in range(12):
            assert cli.publicar("market.ohlcv", tags, obj, k)["duplicate"] is False
        assert cli.publicar("market.ohlcv", tags, obj, 3)["duplicate"] is True
        assert alm.peticiones[("r0", "POST")] > 0 and alm.peticiones[("r1", "POST")] > 0  # rotacion
        assert cli.estadisticas["fallos_red"] > 0 and cli.estadisticas["http_503"] == 2 and esperas.count(0.5) == 2
        # 409: el mismo batch_id con otro contenido.
        cuerpo, bid = Q.codificar("market.ohlcv", tags, obj, 99)
        alm.por_id[bid] = "otro contenido"
        try:
            cli.publicar("market.ohlcv", tags, obj, 99)
        except Q.ErrorQnPermanente as e:
            assert e.estado == 409 and not isinstance(e, Q.ErrorQnAutorizacion)
        else:
            raise AssertionError("409")
        # 401: token malo; el mensaje no lleva el token.
        try:
            Q.ClienteQn(flota.urls, "token-malo-77", dormir=esperas.append).latest("market.ohlcv", tags)
        except Q.ErrorQnAutorizacion as e:
            assert e.estado == 401 and "token-malo-77" not in str(e)
        else:
            raise AssertionError("401")
        # Todas las replicas en 503: se agota.
        alm.fallar_ts.add(5_000)
        try:
            cli.publicar("market.ohlcv", tags, obj, 5_000)
        except Q.ErrorQnAgotado:
            pass
        else:
            raise AssertionError("agotado")
        assert not any(TOKEN in r for r in alm.rutas)  # el token nunca va en la URL
    finally:
        flota.parar()


def prueba_candado(raiz: str) -> None:
    ruta = os.path.join(raiz, "candado", "x.lock")
    a, b = N.Candado(ruta, 60), N.Candado(ruta, 60)
    assert a.tomar() and not b.tomar()
    a.soltar()
    assert b.tomar()
    viejo = time.time() - 120
    os.utime(ruta, (viejo, viejo))
    c = N.Candado(ruta, 60)
    assert c.tomar() and c.recuperado  # caducado: se recupera
    c.soltar()


def prueba_extremo_a_extremo(ejecutar, raiz: str) -> dict:
    b = Banco(ejecutar, raiz)
    alm = QF.Almacen(TOKEN)
    flota = QF.Flota(alm, vivas=2, caida=True)
    try:
        # 0. Esquema de hoy (sin el tag source): no se publica nada.
        alm_viejo = QF.Almacen(TOKEN, tags=("symbol", "interval"))
        flota_vieja = QF.Flota(alm_viejo, vivas=1, caida=False)
        try:
            c, out = b(flota_vieja, utc(2026, 11, 4, 12, 30))
            assert c == 2 and "source" in out and alm_viejo.peticiones[("r0", "POST")] == 0, out
        finally:
            flota_vieja.parar()
        # 1. Primera ejecucion (miercoles 12:30): todas las velas cerradas desde DESDE; ninguna abierta.
        ahora1 = utc(2026, 11, 4, 12, 30)
        alm.fallos_503["r1"] = 3
        c, out = b(flota, ahora1)
        assert c == 0, out
        q, e = en_qn(alm), esperado(ahora1)
        assert q == e, {k: (len(q.get(k, [])), len(v)) for k, v in e.items()}
        for (sim, iv), tss in q.items():
            assert tss[-1] // 10 ** 9 + N.PASO_S[iv] <= ahora1, (sim, iv)  # la vela en curso no se publica
        assert max(q[("EURUSD", "1h")]) == utc(2026, 11, 4, 11) * 10 ** 9
        reg = b.ultimo()
        assert reg["qn"].get("fallos_red", 0) > 0 and reg["qn"].get("http_503") == 3, reg["qn"]  # replica caida y 503
        ids1 = {(o["tags"]["symbol"], o["tags"]["interval"], o["ts"]): o["batch_id"] for o in alm.objetos}
        # 2. Otra vez en el mismo instante: nada nuevo, ningun POST.
        posts = sum(n for (r, m), n in alm.peticiones.items() if m == "POST")
        c, out = b(flota, ahora1)
        assert c == 0 and sum(n for (r, m), n in alm.peticiones.items() if m == "POST") == posts, out
        # 3. Apagado de varios dias con un fin de semana: el lunes 9 a las 09:10 se rellena todo.
        ahora2 = utc(2026, 11, 9, 9, 10)
        c, out = b(flota, ahora2)
        assert c == 0, out
        assert en_qn(alm) == esperado(ahora2)
        sin_duplicados(alm)
        s = next(x for x in b.ultimo()["series"] if x["simbolo"] == "EURUSD" and x["intervalo"] == "1h")
        assert s["huecos_mercado"]["fin_de_semana"] == 1 and s["huecos_mercado"]["otros"] == 0 and s["sin_publicar"] == 0, s
        # 4. Fallo a mitad de una ventana: un ts concreto da 503 siempre; la serie se para con un hueco por detras de L.
        ahora3 = utc(2026, 11, 9, 15, 0)
        nuevas_5m = [t for t in esperado(ahora3)[("USDJPY", "5m")] if t > max(en_qn(alm)[("USDJPY", "5m")])]
        hueco = nuevas_5m[20]  # segunda ventana de 16, en medio
        alm.fallar_ts.add(hueco)
        c, out = b(flota, ahora3)
        assert c == 1 and "ERROR" in out, out
        tras_fallo = en_qn(alm)[("USDJPY", "5m")]
        assert hueco not in tras_fallo and max(tras_fallo) > hueco, "el fallo debe dejar un hueco por detras de L"
        alm.fallar_ts.clear()
        c, out = b(flota, ahora3)
        assert c == 0, out
        s = next(x for x in b.ultimo()["series"] if x["simbolo"] == "USDJPY" and x["intervalo"] == "5m")
        assert s["huecos_cola_rellenados"] == 1, s
        assert en_qn(alm) == esperado(ahora3)
        sin_duplicados(alm)
        # 5. batch_id estable: un qn nuevo recibe los mismos ids para las mismas velas.
        alm2 = QF.Almacen(TOKEN)
        flota2 = QF.Flota(alm2, vivas=1, caida=False)
        try:
            assert b(flota2, ahora1)[0] == 0
        finally:
            flota2.parar()
        ids2 = {(o["tags"]["symbol"], o["tags"]["interval"], o["ts"]): o["batch_id"] for o in alm2.objetos}
        assert ids2 == ids1
        # 6. Revision: si qn tiene una vela de la cola con otro valor, se cuenta y no se republica.
        with alm.cerrojo:
            o = max((x for x in alm.objetos if x["tags"]["symbol"] == "EURUSD" and x["tags"]["interval"] == "1d"),
                    key=lambda x: x["ts"])
            o["obj"] = {**o["obj"], "close": o["obj"]["close"] + 0.001}
        posts = sum(n for (r, m), n in alm.peticiones.items() if m == "POST")
        c, out = b(flota, ahora3)
        s = next(x for x in b.ultimo()["series"] if x["simbolo"] == "EURUSD" and x["intervalo"] == "1d")
        assert c == 0 and s["revisiones_detectadas"] == 1 and s["publicadas"] == 0, s
        assert sum(n for (r, m), n in alm.peticiones.items() if m == "POST") == posts
        # 7. Candado: con otra ejecucion viva no se hace nada; uno caducado se recupera.
        lock = os.path.join(raiz, "runs", "publicador.lock")
        with open(lock, "w", encoding="utf-8") as f:
            f.write("{}")
        peticiones = sum(alm.peticiones.values())
        c, out = b(flota, ahora3)
        assert c == 0 and "otra ejecucion" in out and sum(alm.peticiones.values()) == peticiones, out
        viejo = time.time() - 4 * 3600
        os.utime(lock, (viejo, viejo))
        c, out = b(flota, ahora3)
        assert c == 0 and b.ultimo()["candado_recuperado"] is True and not os.path.exists(lock), out
        # 8. Token malo: BLOQUEADO sin publicar.
        c, out = b(flota, ahora3, token="otro-token-malo-1")
        assert c == 2 and "token" in out, out
        # 9. Simulacion: sin token y sin tocar qn.
        peticiones = sum(alm.peticiones.values())
        c, out = b(None, ahora3, token=None, modo="--simular")
        assert c == 0 and sum(alm.peticiones.values()) == peticiones, out
        s = next(x for x in b.ultimo()["series"] if x["simbolo"] == "USDJPY" and x["intervalo"] == "5m")
        assert s["simulado"] and s["sin_publicar"] == len(esperado(ahora3)[("USDJPY", "5m")]), s
        # 10. Ninguna funcion prohibida en MT5; ningun secreto en ninguna salida ni en ninguna URL.
        for f in b.falsos:
            assert f.llamadas_prohibidas == [], f.llamadas_prohibidas
        secretos = [TOKEN, str(CRED["login"]), CRED["password"], CRED["server"], CRED["path"]]
        for txt in b.salidas:
            assert not any(v in txt for v in secretos)
        ficheros = 0
        for ruta in glob.glob(os.path.join(raiz, "**", "*"), recursive=True):
            if os.path.isfile(ruta):
                with open(ruta, "rb") as fh:
                    contenido = fh.read()
                assert not any(v.encode() in contenido for v in secretos), ruta
                ficheros += 1
        assert not any(TOKEN in r for r in alm.rutas)
        return {"objetos": len(alm.objetos), "ficheros": ficheros}
    finally:
        flota.parar()


def prueba_ritmo() -> dict:
    """POST por segundo contra el qn falso local (cota superior: sin red ni WAL), con 1 y con 8 hilos."""
    out = {}
    for hilos, n in ((1, 600), (8, 3000)):
        alm = QF.Almacen(TOKEN)
        flota = QF.Flota(alm, vivas=3, caida=False)
        try:
            cli = Q.ClienteQn(flota.urls, TOKEN)
            tags = {"symbol": "EURUSD", "interval": "1m", "source": "mt5"}
            t0 = time.perf_counter()
            with ThreadPoolExecutor(hilos) as pool:
                list(pool.map(lambda k: cli.publicar("market.ohlcv", tags, {"open": 1.0, "high": 1.0, "low": 1.0,
                     "close": 1.0, "volume": 1.0, "date": "x", "source": "mt5"}, k), range(n)))
            out[hilos] = n / (time.perf_counter() - t0)
            assert len(alm.objetos) == n
        finally:
            flota.parar()
    return out


def prueba_tarea_xml() -> None:
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
    raiz = ET.parse(os.path.join(SCRIPTS, "publicador_mt5_tarea.xml")).getroot()
    v = lambda ruta: raiz.find(ruta, ns).text  # noqa: E731
    assert v("t:Triggers/t:TimeTrigger/t:Repetition/t:Interval") == "PT15M"
    assert raiz.find("t:Triggers/t:LogonTrigger", ns) is not None
    assert v("t:Settings/t:StartWhenAvailable") == "true" and v("t:Settings/t:MultipleInstancesPolicy") == "IgnoreNew"
    assert v("t:Settings/t:RunOnlyIfNetworkAvailable") == "true" and v("t:Settings/t:WakeToRun") == "false"
    assert v("t:Principals/t:Principal/t:RunLevel") == "LeastPrivilege"
    assert v("t:Principals/t:Principal/t:LogonType") == "InteractiveToken"
    assert raiz.find("t:Principals/t:Principal/t:UserId", ns) is None  # el usuario que la registra
    assert v("t:Actions/t:Exec/t:Arguments").endswith("scripts\\publicador_mt5.py --ejecutar")
    assert v("t:Actions/t:Exec/t:Command").endswith("\\.venv\\Scripts\\pythonw.exe")


def correr(ejecutar) -> int:
    raiz = os.path.join(TMP, f"selftest_pub_{os.getpid()}")
    os.makedirs(raiz, exist_ok=True)
    try:
        for p in (prueba_codificacion, prueba_cliente_reintentos_y_errores, prueba_tarea_xml):
            p()
            print(f"ok  {p.__name__}")
        prueba_candado(raiz)
        print("ok  prueba_candado")
        r = prueba_extremo_a_extremo(ejecutar, raiz)
        print(f"ok  prueba_extremo_a_extremo ({r['objetos']} objetos en qn falso; {r['ficheros']} ficheros sin secretos)")
        ritmo = prueba_ritmo()
        print("ok  prueba_ritmo (qn falso local, cota superior): "
              + ", ".join(f"{h} hilo{'s' if h > 1 else ''} {v:.0f} POST/s" for h, v in ritmo.items()))
    finally:
        shutil.rmtree(raiz, ignore_errors=True)
    print("selftest ok")
    return 0
