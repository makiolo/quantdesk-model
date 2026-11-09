"""Selftest del extractor MT5: sin terminal y sin red. Usa el modulo falso (falso.py) a traves de la misma envoltura de solo
lectura; del paquete real solo se LEE la API (nombres, docstrings, campos y constantes), nunca se llama. Ficheros bajo
E:/quantdesk-lab/tmp/TI-12-MT5/ y se borran al terminar."""
from __future__ import annotations

import contextlib
import datetime as dt
import glob
import importlib
import inspect
import io
import json
import os
import re
import shutil
import types
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow.parquet as pq

from . import descarga as D
from . import falso as FA
from . import hora as HR
from . import inventario as INV
from . import lectura as LT
from . import simbolos as SB

LIB = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(LIB)
REPO = os.path.dirname(SCRIPTS)
DOCS = os.path.join(REPO, "docs", "plans", "current", "execution", "TI-12-MT5")
TMP = "E:/quantdesk-lab/tmp/TI-12-MT5"

# --- LISTA NEGRA (inicio) ---
# Nombres del paquete que operan o tocan ordenes/posiciones/Market Watch. Este bloque es el UNICO sitio de las rutas de
# TI-12-MT5 donde pueden aparecer: el selftest lo comprueba sobre el resto de la fuente y de la documentacion.
PROHIBIDAS = ("order_send", "order_check", "order_calc_margin", "order_calc_profit", "orders_get", "orders_total",
              "positions_get", "positions_total", "history_orders_get", "history_orders_total", "history_deals_get",
              "history_deals_total", "symbol_select", "market_book_add", "market_book_get", "market_book_release",
              "Buy", "Sell", "Close", "_RawOrder", "TradeRequest", "OrderSendResult", "OrderCheckResult")
# `order_mode` y `order_gtc_mode` son campos de datos de SymbolInfo (los usa el modulo falso), no funciones.
PATRONES = (r"order_(?!mode\b|gtc_mode\b)\w*", r"orders_\w*", r"positions_\w*", r"history_(?:orders|deals)\w*",
            r"market_book\w*", r"symbol_select")
# --- LISTA NEGRA (fin) ---

CRED = {"login": 98765432, "password": "Pw-Falsa-7c1e", "server": "Broker-Falso-Demo", "path": "C:/Falso/terminal64.exe"}


def utc(y, m, d, h=0, mi=0) -> int:
    return int(dt.datetime(y, m, d, h, mi, tzinfo=dt.timezone.utc).timestamp())


def envoltura(**kw) -> tuple[LT.TerminalSoloLectura, FA.MT5Falso]:
    falso = FA.MT5Falso(trampas=PROHIBIDAS, cuenta=dict(CRED), **kw)
    return LT.TerminalSoloLectura(falso), falso


# ---------------------------------------------------------------------------------------------------------------------
# Solo lectura
# ---------------------------------------------------------------------------------------------------------------------

def _fuentes() -> list[str]:
    rutas = [os.path.join(SCRIPTS, "extractor_mt5.py")] + sorted(glob.glob(os.path.join(LIB, "*.py")))
    rutas += sorted(glob.glob(os.path.join(SCRIPTS, "publicador_mt5*.*")))  # publicador de la fase B y su tarea
    rutas += sorted(glob.glob(os.path.join(SCRIPTS, "publicador_mt5_lib", "*.py")))
    return rutas + sorted(glob.glob(os.path.join(DOCS, "*.md")))


def prueba_lista_negra_estatica() -> None:
    """Ningun nombre que opere aparece en la fuente ni en la documentacion, salvo en el bloque de la lista negra."""
    regex = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join([re.escape(n) for n in PROHIBIDAS] + list(PATRONES))
                       + r")(?![A-Za-z0-9_])")
    vistos = 0
    for ruta in _fuentes():
        with open(ruta, encoding="utf-8") as f:
            texto = f.read()
        if os.path.abspath(ruta) == os.path.abspath(__file__):
            ini, fin = "# --- LISTA NEGRA " + "(inicio) ---\n", "# --- LISTA NEGRA " + "(fin) ---\n"
            assert texto.count(ini) == 1 and texto.count(fin) == 1, "marcas de la lista negra"
            a = texto.index(ini)
            texto = texto[:a] + texto[texto.index(fin, a):]
        hallados = sorted(set(regex.findall(texto)))
        assert not hallados, f"{os.path.relpath(ruta, REPO)} menciona {hallados} fuera de la lista negra"
        importa = re.findall(r"^\s*(?:import|from)\s+MetaTrader5\b", texto, flags=re.M)
        assert not importa or os.path.basename(ruta) == "lectura.py", f"{ruta} importa el paquete"
        vistos += 1
    assert vistos >= 9
    assert not set(PROHIBIDAS) & (LT.FUNCIONES_PERMITIDAS | LT.CONSTANTES_PERMITIDAS)


def prueba_lista_blanca_dinamica() -> int:
    """Sobre el paquete REAL (solo se leen atributos): todo nombre fuera de la lista blanca lanza FuncionNoPermitida."""
    real = importlib.import_module("MetaTrader5")
    assert all(hasattr(real, n) for n in PROHIBIDAS), "la lista negra debe nombrar funciones que existen"
    env = LT.TerminalSoloLectura(real)
    permitidos = LT.FUNCIONES_PERMITIDAS | LT.CONSTANTES_PERMITIDAS
    rechazados = 0
    for n in sorted(set(dir(real)) | set(PROHIBIDAS)):
        if n in permitidos or (n.startswith("__") and n.endswith("__")):
            continue
        try:
            getattr(env, n)
        except LT.FuncionNoPermitida:
            rechazados += 1
        else:
            raise AssertionError(f"la envoltura deja pasar {n}")
    assert rechazados >= 60, rechazados
    for n in LT.FUNCIONES_PERMITIDAS - {"initialize"}:
        assert getattr(env, n) is getattr(real, n)
    assert env.TIMEFRAME_H1 == real.TIMEFRAME_H1
    for llamada in (lambda: env.initialize(login=1), lambda: env.initialize("x", "y"), lambda: env.initialize(password="p"),
                    lambda: setattr(env, "order", 1), lambda: delattr(env, "version_paquete")):
        try:
            llamada()
        except LT.FuncionNoPermitida:
            pass
        else:
            raise AssertionError("la envoltura acepto una llamada prohibida")
    # La envoltura no guarda el modulo: ni en sus atributos ni dentro de sus mapas.
    for slot in LT.TerminalSoloLectura.__slots__:
        v = object.__getattribute__(env, slot)
        assert not isinstance(v, types.ModuleType)
        if hasattr(v, "values"):
            assert not any(isinstance(x, types.ModuleType) for x in v.values())
            assert set(v) <= permitidos
    return rechazados


def _params_doc(doc: str) -> tuple[list[str], list[str]]:
    """Parametros de la primera linea del docstring del paquete: (obligatorios en orden, opcionales)."""
    firma = doc.strip().splitlines()[0]
    interior = firma[firma.index("(") + 1: firma.rindex(")")]
    interior = re.sub(r'"[^"]*"', "", interior)
    interior = re.sub(r"=\s*[A-Za-z_0-9]+", "", interior)
    opcionales = re.findall(r"\[\s*([A-Za-z_]\w*)", interior)
    todos = re.findall(r"[A-Za-z_]\w*", interior)
    return [x for x in todos if x not in opcionales], opcionales


def prueba_api_falso_igual_al_real() -> None:
    """El falso tiene las firmas, campos, constantes y dtypes del paquete instalado (leidos, no llamados)."""
    real = importlib.import_module("MetaTrader5")
    assert real.__version__ == FA.VERSION, real.__version__
    for n in sorted(LT.FUNCIONES_PERMITIDAS):
        obligatorios, opcionales = _params_doc(getattr(real, n).__doc__)
        firma = [p for p in inspect.signature(getattr(FA.MT5Falso, n)).parameters if p != "self"]
        assert firma[:len(obligatorios)] == obligatorios, (n, obligatorios, firma)
        assert set(opcionales) <= set(firma), (n, opcionales, firma)
    for t, campos in FA.CAMPOS.items():
        assert tuple(getattr(real, t).__match_args__) == campos, t
    for n in LT.CONSTANTES_PERMITIDAS:
        assert getattr(FA, n) == getattr(real, n), n
    assert FA.DTYPE_VELAS.names == D.CAMPOS_VELAS and FA.DTYPE_TICKS.names == D.CAMPOS_TICKS
    assert D.CAMPOS_TICKS == FA.CAMPOS["Tick"]
    # Los campos de MqlRates estan en el binario del paquete en este orden (lectura del fichero, no ejecucion).
    core = glob.glob(os.path.join(os.path.dirname(real.__file__), "_core*.pyd"))[0]
    with open(core, "rb") as f:
        binario = f.read()
    pos = [binario.find(c.encode() + b"\x00") for c in ("open", "high", "low", "close", "tick_volume", "real_volume")]
    assert all(p > 0 for p in pos) and pos == sorted(pos), pos


# ---------------------------------------------------------------------------------------------------------------------
# Hora del servidor
# ---------------------------------------------------------------------------------------------------------------------

def prueba_hora_cambios_de_marzo_y_noviembre() -> None:
    r = HR.regla_desde_texto("ny+7")
    a_utc = lambda *x: int(r.servidor_a_utc(np.array([utc(*x)]))[0][0])  # noqa: E731
    # Marzo de 2026: EE. UU. pasa al verano el domingo 8 a las 07:00 UTC.
    assert a_utc(2026, 3, 6, 23, 59) == utc(2026, 3, 6, 21, 59)  # ultimo minuto del viernes (UTC+2)
    assert a_utc(2026, 3, 9, 0, 0) == utc(2026, 3, 8, 21, 0)  # apertura del lunes (UTC+3)
    assert a_utc(2026, 3, 8, 8, 59) == utc(2026, 3, 8, 6, 59) and a_utc(2026, 3, 8, 10, 0) == utc(2026, 3, 8, 7, 0)
    u, d, amb, inex = r.servidor_a_utc(np.array([utc(2026, 3, 8, 9, 30)]))
    assert (amb, inex, int(d[0])) == (0, 1, 7200)  # 09:30 del servidor no existe: desfase de invierno
    # Noviembre de 2026: vuelve al invierno el domingo 1 a las 06:00 UTC.
    assert a_utc(2026, 10, 30, 23, 59) == utc(2026, 10, 30, 20, 59)
    assert a_utc(2026, 11, 2, 0, 0) == utc(2026, 11, 1, 22, 0)
    u, d, amb, inex = r.servidor_a_utc(np.array([utc(2026, 11, 1, 8, 30)]))
    assert (amb, inex, int(u[0])) == (1, 0, utc(2026, 11, 1, 5, 30))  # ambigua: primera aparicion (verano)
    # Reglas antiguas: 2006 (primer domingo de abril, ultimo de octubre) y 1985 (ultimo de abril).
    assert HR.verano_ee_uu(2006) == (utc(2006, 4, 2, 7), utc(2006, 10, 29, 6))
    assert HR.verano_ee_uu(1985) == (utc(1985, 4, 28, 7), utc(1985, 10, 27, 6))
    assert HR.verano_ue(2026) == (utc(2026, 3, 29, 1), utc(2026, 10, 25, 1))
    assert HR.regla_desde_texto("fija:+3").servidor_a_utc(np.array([utc(2026, 7, 1)]))[0][0] == utc(2026, 6, 30, 21)
    for malo in ("ny+8", "fija:+20", "fija:2", ""):
        try:
            HR.regla_desde_texto(malo)
        except ValueError:
            pass
        else:
            raise AssertionError(malo)


def _contra_zoneinfo(nombre_regla: str, zona: str, extra_h: int, anios: tuple[int, int], paso_h: int) -> None:
    """Cada `paso_h` horas de los anios dados: desfase de la regla == el de la zona IANA (+extra_h) y vuelta exacta."""
    r, z = HR.regla_desde_texto(nombre_regla), ZoneInfo(zona)
    u = np.arange(utc(anios[0], 1, 1), utc(anios[1], 1, 1), paso_h * 3600, dtype=np.int64)
    esperado = np.array([int(dt.datetime.fromtimestamp(int(x), tz=z).utcoffset().total_seconds()) for x in u]) + extra_h * 3600
    assert np.array_equal(r.desfase(u), esperado), nombre_regla
    s = u + esperado
    vuelta, _, amb, _ = r.servidor_a_utc(s)
    malas = np.nonzero(vuelta != u)[0]
    # Solo fallan las horas UTC de la segunda aparicion de la hora repetida, que se resuelven a la primera (una al ano).
    assert all(vuelta[i] == u[i] - 3600 for i in malas), nombre_regla
    assert len(malas) <= (anios[1] - anios[0]) * (3600 // (paso_h * 3600) or 1) and amb >= len(malas)


def prueba_hora_contra_zoneinfo() -> None:
    _contra_zoneinfo("ny+7", "America/New_York", 7, (1987, 2036), 1)
    _contra_zoneinfo("ue+2", "Europe/Athens", 0, (1997, 2036), 1)
    _contra_zoneinfo("ny+7", "America/New_York", 7, (1976, 1987), 3)


def prueba_deteccion_del_desfase() -> None:
    assert HR.desfase_observado(utc(2026, 7, 1, 13) - 90, utc(2026, 7, 1, 10)) == 3 * 3600  # tick de hace 90 s
    assert HR.desfase_observado(utc(2026, 7, 1, 12) + 1200, utc(2026, 7, 1, 10)) is None  # residuo de 20 min
    assert HR.fx_abierto(utc(2026, 11, 4, 15)) and not HR.fx_abierto(utc(2026, 11, 7, 12))
    assert not HR.fx_abierto(utc(2026, 11, 6, 22, 30)) and HR.fx_abierto(utc(2026, 11, 8, 22, 30))
    ny7 = HR.regla_desde_texto("ny+7")
    env, _ = envoltura(ahora_utc_s=utc(2026, 11, 4, 15))
    env.initialize()
    v = HR.detectar_en_vivo(env, ["USDJPY", "GBPUSDm"], utc(2026, 11, 4, 15), ny7)
    assert v["concluyente"] and v["coincide"] and v["desfase_regla_h"] == 2.0, v
    env, _ = envoltura(ahora_utc_s=utc(2026, 7, 15, 15), regla="fija:+2")  # broker en UTC+2 fija, en julio
    env.initialize()
    v = HR.detectar_en_vivo(env, ["USDJPY"], utc(2026, 7, 15, 15), ny7)
    assert v["concluyente"] and v["coincide"] is False, v
    v = HR.detectar_en_vivo(env, ["USDJPY"], utc(2026, 7, 18, 15), ny7)  # sabado: no concluyente
    assert not v["concluyente"] and v["coincide"] is None
    # Metodo historico: velas de 1 h de casi dos anos con cambios de hora.
    for verdad, esperada_coherente in (("ny+7", True), ("fija:+2", False), ("ue+2", False)):
        env, _ = envoltura(ahora_utc_s=utc(2026, 11, 6, 15), regla=verdad)
        env.initialize()
        velas = env.copy_rates_range("USDJPY", env.TIMEFRAME_H1, utc(2025, 1, 1), utc(2026, 11, 1))
        c = HR.cierre_semanal(velas["time"], 3600, "ny+7")
        assert c["coherente"] is esperada_coherente and c["mejor"] == [verdad] and c["concluyente"], (verdad, c)
        assert c["por_regla"][verdad]["cierre_ny_moda"] == "17:00" and c["por_regla"][verdad]["coherencia"] == 1.0


# ---------------------------------------------------------------------------------------------------------------------
# Simbolos
# ---------------------------------------------------------------------------------------------------------------------

def prueba_sufijos_y_nombres() -> None:
    casos = [("EURUSD.a", "EUR", "USD", "EURUSD", ".a"), ("GBPUSDm", "GBP", "USD", "GBPUSD", "m"),
             ("XAUUSD#", "XAU", "USD", "XAUUSD", "#"), ("EURUSD", "EUR", "USD", "EURUSD", ""),
             ("US30.cash", "USD", "USD", "US30", ".cash"), ("DE40_i", "EUR", "EUR", "DE40", "_i"),
             ("US500m", "USD", "USD", "US500", "m"), ("#AAPL", "USD", "USD", "AAPL", ""),
             ("BTCUSD.x", "BTC", "USD", "BTCUSD", ".x")]
    for nombre, b, p, base, suf in casos:
        n = SB.normalizar(nombre, b, p)
        assert (n["base"], n["sufijo"]) == (base, suf), (nombre, n)
    assert SB.normalizar("#AAPL", "USD", "USD")["prefijo"] == "#"
    f = SB.nombres_fichero(["EURUSDm", "EURUSDM", "EURUSD.a", "CON", "A/B"])
    assert f["EURUSD.a"] == "EURUSD.a"
    assert f["EURUSDm"].lower() != f["EURUSDM"].lower() and f["EURUSDm"].startswith("EURUSDm~")
    assert f["CON"].startswith("_CON") and "/" not in f["A/B"] and f["A/B"] != "A_B"
    disp = {s: SB.normalizar(s, *FA.SIMBOLOS[s][:2]) for s in FA.SIMBOLOS}
    assert SB.resolver(["GBPUSD", "EURUSD.pro", "USDJPY"], disp) == ["EURUSD.pro", "GBPUSDm", "USDJPY"]
    for malo in ("EURUSD", "AUDUSD"):
        try:
            SB.resolver([malo], disp)
        except ValueError:
            pass
        else:
            raise AssertionError(malo)


# ---------------------------------------------------------------------------------------------------------------------
# Enganche y credenciales
# ---------------------------------------------------------------------------------------------------------------------

def prueba_enganche() -> None:
    cred = LT.Credenciales(**CRED)
    assert all(v not in repr(cred) and v not in str(cred) for v in cred.valores())
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=False)
    try:
        LT.enganchar(env, None, en_ejecucion=lambda: False)
    except LT.TerminalNoDisponible:
        assert falso.llamadas["initialize"] == 0  # no se intenta arrancar el terminal
    else:
        raise AssertionError("se engancho sin terminal")
    ti, ai = LT.enganchar(env, cred, en_ejecucion=lambda: False)  # con credenciales: initialize(path) y login
    assert ti.connected and ai is not None and falso.llamadas["login"] == 1
    malo = LT.Credenciales(CRED["path"], CRED["login"], "otra-clave-9", CRED["server"])
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=False)
    try:
        LT.enganchar(env, malo, en_ejecucion=lambda: False)
    except LT.TerminalNoDisponible as e:  # -6 de una clave mala: se reintenta acotado y se rinde con el mismo error
        assert all(v not in str(e) for v in malo.valores()) and not falso.iniciado and "-6" in str(e)
        assert falso.llamadas["login"] == len(LT.REINTENTO["esperas_s"]) + 1
    else:
        raise AssertionError("login con clave mala")
    env, _ = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=True)
    assert LT.enganchar(env, None, en_ejecucion=lambda: True)[0].connected
    assert LT.censurar(f"x {CRED['server']} y {CRED['login']}", cred) == "x *** y ***"
    try:
        LT.comprobar_sin_secretos(f"... {CRED['password']} ...", cred)
    except LT.SecretoEnSalida:
        pass
    else:
        raise AssertionError("la guarda de secretos no salto")
    d = os.path.join(TMP, "selftest_cred")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "mt5.json"), "w", encoding="utf-8") as f:
        json.dump(CRED, f)
    c2 = LT.leer_credenciales(os.path.join(d, "mt5.json"))
    assert (c2.login, c2.server) == (CRED["login"], CRED["server"])
    try:
        LT.leer_credenciales(os.path.join(d, "no-existe.json"))
    except LT.TerminalNoDisponible:
        pass


def prueba_arranque_robusto(esperas: list) -> None:
    """Entrega 6: terminal ya abierto con la misma cuenta (sin login), con otra cuenta (login sin initialize(path)),
    fallos -6 / -10005 transitorios al arrancar, espera a `connected` y rendicion acotada."""
    cred = LT.Credenciales(**CRED)
    # a) Abierto y conectado con la misma cuenta: initialize() sin ruta y nada mas.
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=True)
    ti, ai = LT.enganchar(env, cred, en_ejecucion=lambda: True)
    assert ti.connected and falso.llamadas["login"] == 0 and falso.llamadas["initialize con ruta"] == 0
    # a2) Recien abierto con la misma cuenta y aun sin conexion: sin login, solo la espera acotada a `connected`.
    del esperas[:]
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=True, retraso_conexion=2)
    ti, ai = LT.enganchar(env, cred, en_ejecucion=lambda: True)
    assert ti.connected and falso.llamadas["login"] == 0 and esperas == [1.0, 1.0], (dict(falso.llamadas), esperas)
    # b) Abierto con otra cuenta: login sobre esa sesion, sin initialize(path).
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=True,
                           cuenta_abierta={"login": 55500011, "server": "Otro-Servidor"})
    ti, ai = LT.enganchar(env, cred, en_ejecucion=lambda: True)
    assert falso.llamadas["login"] == 1 and falso.llamadas["initialize con ruta"] == 0 and LT.misma_cuenta(ai, cred)
    # c) Cerrado y ocupado: initialize(path) da -6 y luego -10005, y la conexion tarda dos sondeos.
    del esperas[:]
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=False, fallos_arranque=(-6, -10005),
                           retraso_conexion=2)
    ti, ai = LT.enganchar(env, cred, en_ejecucion=lambda: False)
    assert ti.connected and falso.llamadas["initialize con ruta"] == 3 and falso.llamadas["login"] == 1
    assert esperas == [1.0, 2.0, 1.0, 1.0], esperas  # 2 del initialize y 2 de esperar la conexion
    # c2) Abierto con otra cuenta y el login da -10005 una vez: se reintenta el login.
    del esperas[:]
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=True, fallos_arranque=(-10005,),
                           cuenta_abierta={"login": 55500011, "server": "Otro-Servidor"})
    ti, ai = LT.enganchar(env, cred, en_ejecucion=lambda: True)
    assert falso.llamadas["login"] == 2 and esperas == [1.0] and LT.misma_cuenta(ai, cred), (dict(falso.llamadas), esperas)
    # d) -6 persistente: 5 intentos y el mismo error de siempre, sin secretos en el mensaje.
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=False, fallos_arranque=(-6,) * 20)
    try:
        LT.enganchar(env, cred, en_ejecucion=lambda: False)
    except LT.TerminalNoDisponible as e:
        assert "Authorization failed" in str(e) and falso.llamadas["initialize con ruta"] == 5 and not falso.iniciado
        assert all(v not in str(e) for v in cred.valores())
    else:
        raise AssertionError("-6 persistente")
    # e) Nunca conecta: espera acotada y BLOQUEADO.
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=False, retraso_conexion=10_000)
    try:
        LT.enganchar(env, cred, en_ejecucion=lambda: False)
    except LT.TerminalNoDisponible as e:
        assert "sin conexion" in str(e)
    else:
        raise AssertionError("sin conexion")
    # f) Un error no transitorio (ruta mala) no se reintenta.
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 4, 15), abierto=False)
    try:
        LT.enganchar(env, LT.Credenciales("C:/otra/ruta.exe", CRED["login"], CRED["password"], CRED["server"]),
                     en_ejecucion=lambda: False)
    except LT.TerminalNoDisponible:
        assert falso.llamadas["initialize con ruta"] == 1
    else:
        raise AssertionError("ruta mala")


def prueba_reintentos_de_datos(esperas: list) -> None:
    """Entrega 6: -1 'Call failed' mientras el terminal sincroniza se reintenta (5 intentos, esperas 1-8 s); agotados,
    el mismo ErrorTerminal de siempre; un None con RES_S_OK es "sin datos"; la biseccion no se confunde."""
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 6, 15), fallos_call_failed=2)
    env.initialize()
    del esperas[:]
    v = D.consultar(env, "copy_rates_range", "USDJPY", env.TIMEFRAME_H1, utc(2026, 11, 2), utc(2026, 11, 3))
    assert len(v) == 25 and esperas == [1.0, 2.0] and falso.llamadas["call failed"] == 2, (len(v), esperas)
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 6, 15), fallos_call_failed=50)
    env.initialize()
    del esperas[:]
    try:
        D.consultar(env, "copy_rates_range", "USDJPY", env.TIMEFRAME_H1, utc(2026, 11, 2), utc(2026, 11, 3))
    except D.ErrorTerminal as e:
        assert "Call failed" in str(e) and esperas == [1.0, 2.0, 4.0, 8.0] and falso.llamadas["copy_rates_range"] == 5
    else:
        raise AssertionError("agotado")

    class Stub:  # error no transitorio y None con RES_S_OK
        RES_S_OK = 1

        def __init__(self, err):
            self.err, self.n = err, 0

        def copy_rates_range(self, *a):
            self.n += 1
            return None

        def last_error(self):
            return self.err

    s = Stub((-2, "Terminal: Invalid params"))
    del esperas[:]
    try:
        D.consultar(s, "copy_rates_range", "X")
    except D.ErrorTerminal:
        assert s.n == 1 and esperas == []
    else:
        raise AssertionError("no transitorio")
    s = Stub((1, "Success"))
    assert D.consultar(s, "copy_rates_range", "X") is None and s.n == 1
    # Biseccion de la profundidad con el terminal sincronizando: el mismo resultado que sin fallos.
    limpio, _ = envoltura(ahora_utc_s=utc(2026, 11, 6, 15))
    limpio.initialize()
    sucio, falso = envoltura(ahora_utc_s=utc(2026, 11, 6, 15), fallos_call_failed=3)
    sucio.initialize()
    regla = HR.regla_desde_texto("ny+7")
    for per in ("m1", "d1"):
        a = INV.profundidad(limpio, "USDJPY", per, 5_000_000, regla)
        b = INV.profundidad(sucio, "USDJPY", per, 5_000_000, regla)
        assert a == b and a["velas"] > 1, (per, a, b)
    assert falso.llamadas["call failed"] == 6  # 3 por periodo
    assert INV._una(limpio, "USDJPY", limpio.TIMEFRAME_D1, 10 ** 6) is None  # fuera de la historia: vacio = no hay


# ---------------------------------------------------------------------------------------------------------------------
# Extremo a extremo con el CLI
# ---------------------------------------------------------------------------------------------------------------------

class Banco:
    """Lanza `ejecutar` del CLI con el terminal falso, credenciales falsas y un reloj fijo; guarda toda la salida."""

    def __init__(self, ejecutar, raiz: str) -> None:
        self.ejecutar, self.raiz, self.salidas, self.falsos = ejecutar, raiz, [], []

    def __call__(self, argv: list[str], datos: str = "data", ahora=utc(2026, 11, 6, 15), **kw_falso) -> tuple[int, str]:
        abierto = kw_falso.pop("abierto", False)  # terminal ya abierto por el usuario (y lo que ve la lista de procesos)

        def fabrica():
            falso = FA.MT5Falso(ahora_utc_s=ahora, trampas=PROHIBIDAS, cuenta=dict(CRED), abierto=abierto, **kw_falso)
            self.falsos.append(falso)
            return LT.TerminalSoloLectura(falso)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = self.ejecutar(argv, fabrica=fabrica, cargar_cred=lambda a: LT.Credenciales(**CRED),
                                   reloj=lambda: float(ahora), data=os.path.join(self.raiz, datos),
                                   runs=os.path.join(self.raiz, "runs"), guarda=lambda: None,
                                   en_ejecucion=lambda: abierto)
        self.salidas.append(buf.getvalue())
        return codigo, buf.getvalue()

    def ultimo_registro(self) -> dict:
        rutas = sorted(glob.glob(os.path.join(self.raiz, "runs", "*.json")), key=os.path.getmtime)
        with open(rutas[-1], encoding="utf-8") as f:
            return json.load(f)


def _manifest(d: str) -> dict:
    with open(os.path.join(d, "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


def _serie(man: dict, sim: str, per: str) -> dict:
    return next(e for e in man["ficheros"] if e["simbolo"] == sim and e["periodo"] == per)


def prueba_extremo_a_extremo(ejecutar, raiz: str) -> dict:
    b = Banco(ejecutar, raiz)
    data = os.path.join(raiz, "data")
    # Inventario
    c, out = b(["--inventario"])
    assert c == 0, out
    inv_ruta = glob.glob(os.path.join(data, "inventario", "inventario_*.json"))[0]
    with open(inv_ruta, encoding="utf-8") as f:
        inv = json.load(f)
    sims = {d["simbolo"]: d for d in inv["simbolos"]}
    assert len(sims) == 6 and inv["resumen"]["bases_compartidas"] == ["EURUSD"]
    assert (sims["GBPUSDm"]["base"], sims["GBPUSDm"]["sufijo"]) == ("GBPUSD", "m")
    assert not sims["AAPL.US"]["ticks"]["hay"] and sims["BTCUSD.x"]["ticks"]["hay"]
    assert sims["AAPL.US"]["precio_velas"] == "last" and sims["USDJPY"]["punto"] == 0.001
    assert sims["USDJPY"]["profundidad"]["m1"]["primera_utc"] == "2026-01-01T00:00:00.000Z", sims["USDJPY"]["profundidad"]
    assert sims["USDJPY"]["profundidad"]["d1"]["primera_utc"] == "2015-01-01T22:00:00.000Z"  # 2 ene del servidor
    viva = inv["deteccion_desfase_en_vivo"]
    assert viva["concluyente"] and viva["coincide"] and viva["desfase_regla_h"] == 2.0, viva
    assert inv["procedencia"]["cuenta_tipo"] == "demo" and inv["procedencia"]["broker"] == "Broker Falso Ltd."
    assert not {k for k in inv["procedencia"] if "hash" in k}, inv["procedencia"]  # decision de la raiz: sin hashes

    args = ["--descargar", "--simbolos", "EURUSD.a,GBPUSD,BTCUSD.x,AAPL.US", "--periodos", "d1,h1,m5,m1,ticks",
            "--desde", "2026-10-26", "--hasta", "2026-11-05"]
    dir_a, dir_b = os.path.join(data, "A"), os.path.join(data, "B")
    c, out = b(args + ["--salida", dir_a])
    assert c == 0, out
    total = b.ultimo_registro()["trozos_pedidos"]
    assert total == 4 * (1 + 1 + 2 + 2 + 10), total
    ma = _manifest(dir_a)
    # Hora: el viernes 30 de octubre aun es verano en EE. UU. (UTC+3); el lunes 2 de noviembre, invierno (UTC+2).
    t = pq.read_table(os.path.join(dir_a, "EURUSD.a__m1.parquet")).to_pandas()
    viernes = t[t.ts_utc_ms < utc(2026, 10, 31) * 1000].ts_utc_ms.max()
    lunes = t[t.ts_utc_ms > utc(2026, 10, 31) * 1000].ts_utc_ms.min()
    assert (viernes, lunes) == (utc(2026, 10, 30, 20, 59) * 1000, utc(2026, 11, 1, 22) * 1000)
    assert (t.ts_utc_ms + t.desfase_s.astype("int64") * 1000 == t.time_servidor * 1000).all()
    s = _serie(ma, "EURUSD.a", "m1")
    assert s["hora"]["desfases_h"] == [2.0, 3.0] and s["huecos"]["fin_de_semana"] == 1 and s["huecos"]["otros"] == 0, s
    assert np.allclose(t.ask_close_est, (t.close + t.spread).round(5)) and (t.spread > 0).all()
    d1 = pq.read_table(os.path.join(dir_a, "EURUSD.a__d1.parquet")).to_pandas()
    assert len(d1) == 8 and d1.ts_utc_ms.max() == utc(2026, 11, 3, 22) * 1000  # vela del 4-nov del servidor, cerrada
    # Cripto 24x7: la hora repetida del 1 de noviembre se cuenta como ambigua; no hay hueco de fin de semana.
    btc = _serie(ma, "BTCUSD.x", "m1")
    assert btc["hora"]["ambiguas"] == 60 and btc["huecos"]["fin_de_semana"] == 0, btc
    assert _serie(ma, "BTCUSD.x", "h1")["hora"]["ambiguas"] == 1
    # Bolsa: velas de Last sin ask/mid estimados, y sin ticks.
    aapl = _serie(ma, "AAPL.US", "ticks")
    assert aapl["filas"] == 0 and aapl["fichero"] is None
    ta = pq.read_table(os.path.join(dir_a, "AAPL.US__m1.parquet")).to_pandas()
    assert ta.ask_close_est.isna().all() and _serie(ma, "AAPL.US", "m1")["precio_velas"] == "last"
    tk = pq.read_table(os.path.join(dir_a, "EURUSD.a__ticks.parquet")).to_pandas()
    assert np.allclose(tk.mid, (tk.bid + tk.ask) / 2) and (tk.spread > 0).all() and tk.ts_utc_ms.is_monotonic_increasing
    # Dos descargas del mismo rango (la segunda vuelve a pedirlo todo) dan los mismos bytes y el mismo hash.
    c, out = b(args + ["--salida", dir_b, "--refrescar"])
    assert c == 0 and b.ultimo_registro()["trozos_reutilizados"] == 0, out
    mb = _manifest(dir_b)
    assert ma["hash_conjunto"] == mb["hash_conjunto"]
    for e in ma["ficheros"]:
        if e["fichero"]:
            with open(os.path.join(dir_a, e["fichero"]), "rb") as fa, open(os.path.join(dir_b, e["fichero"]), "rb") as fb:
                assert fa.read() == fb.read(), e["fichero"]
    c, out = b(["--comparar", dir_a, dir_b])
    assert c == 0 and "identicas" in out, out
    # Reanudacion a medias: otra cache; el terminal falla tras 23 consultas de datos.
    c, out = b(args + ["--salida", os.path.join(raiz, "data2", "R")], datos="data2", fallar_tras=23)
    assert c == 1 and "reanudable" in out, out
    assert not os.path.exists(os.path.join(raiz, "data2", "R", "manifest.json"))
    hechos = glob.glob(os.path.join(raiz, "data2", "_trozos", "*", "*", "*", "*", "*.parquet.json"))
    assert len(hechos) == 23, len(hechos)
    c, out = b(args + ["--salida", os.path.join(raiz, "data2", "R")], datos="data2")
    reg = b.ultimo_registro()
    assert c == 0 and (reg["trozos_reutilizados"], reg["trozos_pedidos"]) == (23, total - 23), (out, reg)
    assert _manifest(os.path.join(raiz, "data2", "R"))["hash_conjunto"] == ma["hash_conjunto"]
    # Incremental: un dia mas reutiliza los trozos cerrados de la cache.
    args2 = [x if x != "2026-11-05" else "2026-11-06" for x in args]
    c, out = b(args2 + ["--salida", os.path.join(data, "C")])
    reg = b.ultimo_registro()
    assert c == 0 and reg["trozos_pedidos"] == 4 * 5 and reg["trozos_reutilizados"] == 4 * 12, reg
    # Misma salida con otros parametros: se rechaza.
    c, out = b(["--descargar", "--simbolos", "USDJPY", "--periodos", "d1", "--desde", "2026-10-26", "--hasta", "2026-11-05",
                "--salida", dir_a])
    assert c == 2 and "otros parametros" in out, out
    # Rango en el futuro y periodo desconocido: uso incorrecto.
    assert b(args[:-1] + ["2026-11-07"])[0] == 2
    assert b(["--descargar", "--simbolos", "USDJPY", "--periodos", "w1", "--desde", "2026-10-01", "--hasta", "2026-10-02"])[0] == 2
    # Marzo: cambio de hora de primavera.
    c, out = b(["--descargar", "--simbolos", "USDJPY,BTCUSD.x", "--periodos", "m1", "--desde", "2026-03-05",
                "--hasta", "2026-03-11", "--salida", os.path.join(data, "M")])
    assert c == 0, out
    tm = pq.read_table(os.path.join(data, "M", "USDJPY__m1.parquet")).to_pandas()
    assert tm[tm.ts_utc_ms < utc(2026, 3, 7) * 1000].ts_utc_ms.max() == utc(2026, 3, 6, 21, 59) * 1000
    assert tm[tm.ts_utc_ms > utc(2026, 3, 7) * 1000].ts_utc_ms.min() == utc(2026, 3, 8, 21) * 1000
    mm = _manifest(os.path.join(data, "M"))
    bm = _serie(mm, "BTCUSD.x", "m1")
    assert bm["huecos"]["otros"] == 0 and bm["hora"]["inexistentes"] == 0 and bm["hora"]["desfases_h"] == [2.0, 3.0], bm
    # Broker con otra hora: la deteccion en vivo para la descarga.
    c, out = b(["--descargar", "--simbolos", "USDJPY", "--periodos", "d1", "--desde", "2026-07-01", "--hasta", "2026-07-03",
                "--salida", os.path.join(data, "X")], ahora=utc(2026, 7, 15, 15), regla="fija:+2")
    assert c == 2 and "--regla" in out, out
    # Entrega 6, terminal real: arranque con -6 y -10005 y datos con 'Call failed' mientras sincroniza. Misma descarga
    # (mismo hash que A) y mismo inventario que sin fallos.
    c, out = b(args + ["--salida", os.path.join(raiz, "data3", "F")], datos="data3", fallos_call_failed=2,
               fallos_arranque=(-6, -10005))
    f = b.falsos[-1]
    assert c == 0 and f.llamadas["call failed"] > 0 and f.llamadas["initialize con ruta"] == 3, (out, dict(f.llamadas))
    assert _manifest(os.path.join(raiz, "data3", "F"))["hash_conjunto"] == ma["hash_conjunto"]
    c, out = b(["--inventario"], datos="data4", fallos_call_failed=2, fallos_arranque=(-10005,))
    assert c == 0 and b.falsos[-1].llamadas["call failed"] > 0, out
    with open(glob.glob(os.path.join(raiz, "data4", "inventario", "inventario_*.json"))[0], encoding="utf-8") as fi:
        assert json.load(fi)["simbolos"] == inv["simbolos"]
    # Terminal ya abierto y conectado con la cuenta del fichero: se engancha sin login.
    c, out = b(["--inventario"], datos="data5", abierto=True)
    f = b.falsos[-1]
    assert c == 0 and f.llamadas["login"] == 0 and f.llamadas["initialize con ruta"] == 0, (out, dict(f.llamadas))
    # Terminal cerrado y sin credenciales: BLOQUEADO sin arrancarlo.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        falso = FA.MT5Falso(ahora_utc_s=utc(2026, 11, 6, 15), trampas=PROHIBIDAS, abierto=False)
        c = ejecutar(["--inventario", "--sin-credenciales"], fabrica=lambda: LT.TerminalSoloLectura(falso),
                     cargar_cred=lambda a: None, en_ejecucion=lambda: False, data=data, runs=os.path.join(raiz, "runs"))
    assert c == 2 and "no esta abierto" in buf.getvalue() and falso.llamadas["initialize"] == 0
    # Ninguna funcion prohibida llamada, initialize nunca con credenciales.
    for f in b.falsos + [falso]:
        assert f.llamadas_prohibidas == [], f.llamadas_prohibidas
    # Ningun valor de las credenciales en ninguna salida: consola, JSON, parquet, registros.
    secretos = [str(CRED["login"]), CRED["password"], CRED["server"], CRED["path"]]
    for txt in b.salidas:
        assert not any(v in txt for v in secretos)
    ficheros = 0
    for ruta in glob.glob(os.path.join(raiz, "**", "*"), recursive=True):
        if os.path.isfile(ruta) and "selftest_cred" not in ruta:
            with open(ruta, "rb") as f:
                contenido = f.read()
            assert not any(v.encode() in contenido for v in secretos), ruta
            ficheros += 1
    return {"ficheros_revisados": ficheros, "trozos": total, "hash": ma["hash_conjunto"]}


def correr(ejecutar) -> int:
    esperas: list = []  # los reintentos no duermen en el selftest: se apuntan las esperas pedidas
    previa = LT.configurar_reintentos(esperas_s=(1.0, 2.0, 4.0, 8.0), dormir=esperas.append, espera_conexion_s=5)
    pruebas = [prueba_lista_negra_estatica, prueba_lista_blanca_dinamica, prueba_api_falso_igual_al_real,
               prueba_hora_cambios_de_marzo_y_noviembre, prueba_hora_contra_zoneinfo, prueba_deteccion_del_desfase,
               prueba_sufijos_y_nombres, prueba_enganche, lambda: prueba_arranque_robusto(esperas),
               lambda: prueba_reintentos_de_datos(esperas)]
    nombres = [getattr(p, "__name__", "") for p in pruebas[:-2]] + ["prueba_arranque_robusto", "prueba_reintentos_de_datos"]
    raiz = os.path.join(TMP, f"selftest_{os.getpid()}")
    os.makedirs(raiz, exist_ok=True)
    try:
        for p, nombre in zip(pruebas, nombres):
            r = p()
            print(f"ok  {nombre}" + (f" ({r} nombres rechazados)" if isinstance(r, int) else ""))
        r = prueba_extremo_a_extremo(ejecutar, raiz)
        print(f"ok  prueba_extremo_a_extremo ({r['trozos']} trozos; {r['ficheros_revisados']} ficheros sin secretos; "
              f"hash {r['hash'][:23]}...)")
    finally:
        LT.configurar_reintentos(**previa)
        shutil.rmtree(raiz, ignore_errors=True)
        shutil.rmtree(os.path.join(TMP, "selftest_cred"), ignore_errors=True)
    print("selftest ok")
    return 0
