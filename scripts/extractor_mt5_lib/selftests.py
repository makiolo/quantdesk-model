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

from . import calendarios as CAL
from . import descarga as D
from . import falso as FA
from . import hora as HR
from . import inventario as INV
from . import lectura as LT
from . import simbolos as SB
from . import universos as UNI

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
    # Profundidad con el terminal sincronizando: el mismo resultado que sin fallos, con una sola consulta por periodo.
    limpio, _ = envoltura(ahora_utc_s=utc(2026, 11, 6, 15))
    limpio.initialize()
    sucio, falso = envoltura(ahora_utc_s=utc(2026, 11, 6, 15), fallos_call_failed=3)
    sucio.initialize()
    regla = HR.regla_desde_texto("ny+7")
    for per in ("m1", "d1"):
        a = INV.profundidad(limpio, "USDJPY", per, 5_000_000, regla)
        b = INV.profundidad(sucio, "USDJPY", per, 5_000_000, regla)
        assert a == b and a["velas"] > 1 and not a["limitada_por_maxbars"], (per, a, b)
    assert falso.llamadas["call failed"] == 6 and falso.llamadas["copy_rates_from_pos"] == 8  # (3 + 1) por periodo


def prueba_copy_rates_from_pos_como_el_real(esperas: list) -> None:
    """Entrega 6b, medido en el terminal real (build 6230, maxbars 100000): fuera de la historia con count 1 da -1 'Call
    failed' (no se distingue de la sincronizacion); count >= maxbars da -2 'Invalid params'; count < maxbars da
    min(count, disponibles). La profundidad usa una sola consulta con count = maxbars - 1."""
    regla = HR.regla_desde_texto("ny+7")
    env, falso = envoltura(ahora_utc_s=utc(2026, 11, 6, 15), maxbars=100_000)
    env.initialize()
    d1 = env.copy_rates_from_pos("USDJPY", env.TIMEFRAME_D1, 0, 99_999)
    n_d1 = len(d1)
    assert 1000 < n_d1 < 99_999 and env.last_error()[0] == env.RES_S_OK  # d1: todas las disponibles
    assert len(env.copy_rates_from_pos("USDJPY", env.TIMEFRAME_M1, 0, 99_999)) == 99_999  # m1: tope del count
    for tf in (env.TIMEFRAME_D1, env.TIMEFRAME_H1, env.TIMEFRAME_M1):
        assert env.copy_rates_from_pos("USDJPY", tf, 0, 100_000) is None and env.last_error()[0] == -2
    for pos in (n_d1, 50_000, 99_999, 100_010, 10_000_000):
        assert env.copy_rates_from_pos("USDJPY", env.TIMEFRAME_D1, pos, 1) is None
        assert env.last_error() == (-1, "Terminal: Call failed")
    # Por consultar: -1 fuera de la historia se reintenta (es el mismo codigo) y acaba en ErrorTerminal con codigo -1;
    # -2 no se reintenta.
    del esperas[:]
    try:
        D.consultar(env, "copy_rates_from_pos", "USDJPY", env.TIMEFRAME_D1, 10_000_000, 1)
    except D.ErrorTerminal as e:
        assert e.codigo == -1 and esperas == [1.0, 2.0, 4.0, 8.0]
    else:
        raise AssertionError("fuera de la historia")
    del esperas[:]
    try:
        D.consultar(env, "copy_rates_from_pos", "USDJPY", env.TIMEFRAME_D1, 0, 100_000)
    except D.ErrorTerminal as e:
        assert e.codigo == -2 and esperas == []
    else:
        raise AssertionError("count = maxbars")
    # Profundidad: una consulta con count = maxbars - 1, nunca maxbars; sin reintentos si no hay fallos.
    antes = falso.llamadas["copy_rates_from_pos"]
    del esperas[:]
    p = INV.profundidad(env, "USDJPY", "d1", 100_000, regla)
    assert p["velas"] == n_d1 and not p["limitada_por_maxbars"] and esperas == [], p
    assert p["primera_utc"] == "2015-01-01T22:00:00.000Z" and p["ultima_servidor_s"] == int(d1["time"][-1]), p
    p = INV.profundidad(env, "USDJPY", "m1", 100_000, regla)
    assert p["velas"] == 99_999 and p["limitada_por_maxbars"], p
    assert falso.llamadas["copy_rates_from_pos"] - antes == 2
    # Simbolo sin historia en un periodo (m1 antes del 1-ene-2026 en el falso): -1 tras los reintentos; se apunta y sigue.
    env, falso = envoltura(ahora_utc_s=utc(2025, 12, 10, 15), maxbars=100_000)
    env.initialize()
    del esperas[:]
    p = INV.profundidad(env, "USDJPY", "m1", 100_000, regla)
    assert p["velas"] == 0 and "Call failed" in p["error"] and len(esperas) == 4, p
    assert INV.profundidad(env, "USDJPY", "d1", 100_000, regla)["velas"] > 1


# ---------------------------------------------------------------------------------------------------------------------
# Fase C: universos con nombre, calendarios por clase y huecos de 1d
# ---------------------------------------------------------------------------------------------------------------------

_BID = FA.SYMBOL_CHART_MODE_BID
# Un broker falso con las carpetas del real (rutas del inventario de 2026-11-09) y una muestra de cada clase.
SIMBOLOS_C = {
    "EURUSD": ("EUR", "USD", 5, "fx", 1.08, _BID, True, "Forex\\Majors\\EURUSD"),
    "USDJPY": ("USD", "JPY", 3, "fx", 150.0, _BID, True, "Forex\\Majors\\USDJPY"),
    "XAUUSD": ("XAU", "USD", 2, "fx:CME", 2000.0, _BID, True, "Commodities\\Metals\\XAUUSD"),
    "BRENT_F7": ("USD", "USD", 2, "fx", 80.0, _BID, True, "Commodities\\Energies\\Energies Futures\\BRENT_F7"),
    "SIN26": ("USD", "USD", 3, "fx", 30.0, _BID, True, "Commodities\\Metal Futures\\SIN26"),
    "DE40": ("USD", "EUR", 1, "fx:XETRA", 18000.0, _BID, True, "Indices\\Indices Spot\\Major Spot Indices\\DE40"),
    "HK50": ("USD", "HKD", 1, "fx:HKEX", 17000.0, _BID, True, "Indices\\Indices Spot\\Minor Spot Indices\\HK50"),
    "DXY_Z6": ("USD", "USD", 3, "fx", 100.0, _BID, True, "Indices\\Indices Futures\\DXY_Z6"),
    "BTCUSD": ("USD", "USD", 2, "24x7", 65000.0, _BID, True, "Crypto\\BTCUSD"),
    "ETCUSD": ("USD", "USD", 3, "24x7", 20.0, _BID, True, "Crypto\\Crypto Alts\\ETCUSD"),
    "AAPL.NAS": ("USD", "USD", 2, "bolsa", 190.0, _BID, False, "Stock CFD's\\Nasdaq\\AAPL.NAS"),
    "AAPL.NAS-24": ("USD", "USD", 2, "fx", 190.0, _BID, False, "Stock CFD's\\Nasdaq\\24HR NAS\\AAPL.NAS-24"),
    "BRK-B.NYSE": ("USD", "USD", 2, "bolsa", 450.0, _BID, False, "Stock CFD's\\NYSE\\BRK-B.NYSE"),
    "BF/B.NYSE": ("USD", "USD", 2, "bolsa", 40.0, _BID, False, "Stock CFD's\\NYSE\\BF/B.NYSE"),
    "HON.NYSE": ("USD", "USD", 2, "bolsa", 200.0, _BID, False, "Stock CFD's\\NYSE\\HON.NYSE"),
    "META.NAS-24": ("USD", "USD", 2, "fx", 500.0, _BID, False, "Stock CFD's\\Nasdaq\\24HR NAS\\META.NAS-24"),
    "0001.HK": ("HKD", "HKD", 3, "fx", 40.0, _BID, False, "Stock CFD's\\HK\\0001.HK"),
    "UST10Y_H7": ("USD", "USD", 3, "fx", 110.0, _BID, True, "Bonds CFDs\\UST10Y_H7"),
    "Boom1000": ("USD", "USD", 3, "24x7", 9000.0, _BID, True, "Stohastic\\Boom1000"),
}
SP500_C = [{"ticker": "AAPL", "nombre": "Apple Inc.", "bolsa": "NASDAQ"},
           {"ticker": "BRK.B", "nombre": "Berkshire Hathaway", "bolsa": "NYSE"},
           {"ticker": "BF.B", "nombre": "Brown-Forman", "bolsa": "NYSE"},
           {"ticker": "HON", "nombre": "Honeywell", "bolsa": "NASDAQ"},
           {"ticker": "META", "nombre": "Meta Platforms", "bolsa": "NASDAQ"},
           {"ticker": "GOOGL", "nombre": "Alphabet Inc. (Class A)", "bolsa": "NASDAQ"}]


def universos_falsos(ahora=utc(2026, 11, 6, 15)) -> dict:
    """Universos resueltos contra el inventario del broker falso de la fase C (como `--universos` sobre el real)."""
    env, _ = envoltura(ahora_utc_s=ahora, simbolos=SIMBOLOS_C)
    env.initialize()
    filas = list(INV.simbolos_disponibles(env, None).values())
    return UNI.resolver({"ahora_utc": HR.iso(ahora * 1000), "simbolos": filas}, SP500_C, "selftest", "falso.json")


def prueba_calendarios() -> None:
    d = dt.date
    assert [CAL.pascua(a) for a in (2024, 2025, 2026, 2027)] == [d(2024, 3, 31), d(2025, 4, 20), d(2026, 4, 5), d(2027, 3, 28)]
    assert sorted(CAL.festivos("NYSE", 2026)) == [d(2026, 1, 1), d(2026, 1, 19), d(2026, 2, 16), d(2026, 4, 3), d(2026, 5, 25),
                                                 d(2026, 6, 19), d(2026, 7, 3), d(2026, 9, 7), d(2026, 11, 26), d(2026, 12, 25)]
    assert d(2021, 12, 31) not in CAL.festivos("NYSE", 2021)  # 1-ene-2022 en sabado: la NYSE abrio el viernes
    assert {d(2022, 6, 20), d(2022, 12, 26)} <= CAL.festivos("NYSE", 2022) and d(2025, 1, 9) in CAL.festivos("NYSE", 2025)
    # Dias laborables sin vela 1d medidos en el terminal real (2023-2026): todos estan en el calendario de su bolsa.
    medidos = {"ASX": ["2023-12-25", "2023-12-26", "2024-01-01", "2024-03-29", "2024-04-01", "2024-12-25", "2024-12-26",
                       "2025-01-01", "2025-04-18", "2025-04-21", "2025-12-25", "2025-12-26", "2026-01-01", "2026-04-03",
                       "2026-04-06", "2026-06-08"],
               "TSX": ["2024-02-19", "2024-03-29", "2024-05-20", "2024-07-01", "2024-08-05", "2024-09-02", "2024-10-14",
                       "2025-02-17", "2025-04-18", "2025-05-19", "2025-07-01", "2025-08-04", "2025-09-01", "2025-10-13",
                       "2026-02-16", "2026-04-03", "2026-05-18", "2026-07-01", "2026-08-03", "2026-09-07", "2026-10-12"]}
    for bolsa, dias in medidos.items():
        assert all(CAL.es_festivo(bolsa, d.fromisoformat(x)) for x in dias), bolsa
    assert all(CAL.festivos(b, 2026) for b in CAL.BOLSAS) and set(CAL.BOLSA_INDICE.values()) <= set(CAL.BOLSAS)
    dia = lambda txt: (d.fromisoformat(txt) - CAL.EPOCA).days  # noqa: E731
    laborables = lambda a, b, fuera=(): [x for x in range(dia(a), dia(b) + 1) if (x + 3) % 7 < 5 and x not in fuera]  # noqa: E731
    # Indice europeo: Viernes Santo y Lunes de Pascua son festivos; un martes sin vela es otro hueco.
    h = CAL.huecos_sesiones(laborables("2026-03-30", "2026-04-17", {dia("2026-04-03"), dia("2026-04-06"), dia("2026-04-14")}),
                            "indices", "XETRA")
    assert (h["festivos"], h["festivos_probables"], h["otros"], h["fin_de_semana"]) == (2, 1, 0, 4), h
    h = CAL.huecos_sesiones(laborables("2026-03-30", "2026-04-30", set(range(dia("2026-04-13"), dia("2026-04-18")))),
                            "indices", "XETRA")
    assert h["otros"] == 1 and h["otros_mayores"][0]["pasos"] == 5, h  # una semana entera no es un festivo
    # Cripto: sin vela un sabado es fin de semana (historia antigua del broker); un martes, otro hueco. Sin festivos probables.
    todos = [x for x in range(dia("2026-10-01"), dia("2026-10-31")) if x not in (dia("2026-10-10"), dia("2026-10-13"))]
    h = CAL.huecos_sesiones(todos, "crypto", None)
    assert (h["fin_de_semana"], h["festivos"], h["festivos_probables"], h["otros"]) == (1, 0, 0, 1), h
    # Acciones US: la semana de Accion de Gracias de 2026 (jueves 26 festivo de la NYSE).
    h = CAL.huecos_sesiones(laborables("2026-11-23", "2026-11-30", {dia("2026-11-26")}), "acciones_us", "NYSE")
    assert (h["festivos"], h["otros"], h["festivos_probables"]) == (1, 0, 0) and "sesiones_fin_de_semana" not in h, h
    # Acciones US solo -24 (24/5): mismo calendario NYSE; una vela de sabado (la cola del viernes) se cuenta y no es hueco.
    assert CAL.bolsa_de("acciones_us_24", "META") == "NYSE"
    h = CAL.huecos_sesiones(sorted(laborables("2026-11-23", "2026-11-30", {dia("2026-11-26")}) + [dia("2026-11-28")]),
                            "acciones_us_24", "NYSE")
    assert (h["festivos"], h["otros"], h["fin_de_semana"], h["sesiones_fin_de_semana"]) == (1, 0, 1, 1), h


def prueba_universos() -> None:
    """Reglas de seleccion sobre un broker con las carpetas del real, cruce del S&P 500 y el fichero del repo."""
    u = universos_falsos()
    g = u["grupos"]
    assert g["fx60"] == ["EURUSD", "USDJPY"] and g["metales_energia"] == ["XAUUSD"] and g["indices"] == ["DE40", "HK50"]
    assert g["crypto"] == ["BTCUSD"] and g["crypto_alts"] == ["ETCUSD"]
    assert g["continuo"] == sorted(["EURUSD", "USDJPY", "XAUUSD", "DE40", "HK50", "BTCUSD", "ETCUSD"])
    assert sorted(u["excluidos"]["vencimiento"]) == ["BRENT_F7", "DXY_Z6", "SIN26"]
    assert (u["excluidos"]["bonos"], u["excluidos"]["stohastic"]) == (1, 1)
    # La sesion normal manda (AAPL tiene AAPL.NAS y AAPL.NAS-24); META solo existe en -24 y entra con su -24 (decision
    # del usuario del 2026-11-09), con clase propia y la etiqueta de su ticker. HON cotiza como .NYSE.
    assert g["us_grandes"] == ["AAPL.NAS", "BF/B.NYSE", "BRK-B.NYSE", "HON.NYSE", "META.NAS-24"]
    assert u["etiquetas"] == {"AAPL.NAS": "AAPL", "BF/B.NYSE": "BF-B", "BRK-B.NYSE": "BRK-B", "HON.NYSE": "HON",
                              "META.NAS-24": "META"}
    cas = {x["ticker"]: x for x in u["us_grandes"]["casados"]}
    assert (cas["AAPL"]["simbolo"], cas["AAPL"]["clase"]) == ("AAPL.NAS", "acciones_us")
    assert (cas["META"]["simbolo"], cas["META"]["clase"]) == ("META.NAS-24", "acciones_us_24")
    assert cas["META"]["regla"] == UNI.REGLA_24 + ", ticker tal cual, .NAS-24" and "-24" not in cas["AAPL"]["regla"]
    fila =lambda s, ruta: {"simbolo": s, "ruta": ruta}  # noqa: E731
    assert UNI.clase_de(fila("AAPL.NAS-24", "Stock CFD's\\Nasdaq\\24HR NAS\\AAPL.NAS-24")) == "acciones_us_24"
    assert UNI.calendario(fila("META.NAS-24", "Stock CFD's\\Nasdaq\\24HR NAS\\META.NAS-24")) == ("acciones_us_24", "NYSE")
    sin = {x["ticker"]: x for x in u["us_grandes"]["sin_casar"]}
    assert sin == {"GOOGL": {"ticker": "GOOGL", "nombre": "Alphabet Inc. (Class A)", "motivo": "el broker no lo tiene"}}
    assert UNI.con_vencimiento("WheatZ6_CFD") and UNI.con_vencimiento("GCG27_CFD") and not UNI.con_vencimiento("NETH25")
    assert not UNI.con_vencimiento("STOXX50") and not UNI.con_vencimiento("US2000")
    # --simbolos: @fx28 sigue igual; un universo se expande; uno desconocido es uso incorrecto.
    import extractor_mt5 as X  # el CLI (scripts/ esta en sys.path)
    assert X.lista_simbolos("@fx28,@crypto", u) == list(INV.FX28) + ["BTCUSD"]
    try:
        X.lista_simbolos("@nada", u)
    except ValueError as e:
        assert "@nada" in str(e)
    else:
        raise AssertionError("universo desconocido")
    # Wikitext de la Wikipedia: los tres formatos de la primera celda que trae la tabla.
    wiki = ('x {| class="wikitable" id="constituents"\n|-\n! Symbol\n|-\n|| {{NyseSymbol|BRK.B}} <!-- nota -->\n|| '
            '[[Berkshire Hathaway]]\n|| Financials\n|| Multi\n|| [[Omaha]]\n|| 2010-02-16\n|-\n| {{NyseSymbol|RDDT}}\n|| '
            '[[Reddit]]\n|| Communication Services\n|| I\n|| SF\n|| 2026-08-18\n|-\n|| {{BZX link|CBOE}}\n|| [[Cboe Global '
            'Markets]]\n|| Financials\n|| F\n|| C\n|| 2017-03-01\n|}\n')
    assert [(f["ticker"], f["bolsa"], f["nombre"]) for f in UNI.sp500_desde_wikitext(wiki)] == [
        ("BRK.B", "NYSE", "Berkshire Hathaway"), ("RDDT", "NYSE", "Reddit"), ("CBOE", "CBOE", "Cboe Global Markets")]
    # El fichero versionado del repo: resuelto contra el inventario real del 2026-11-09.
    real = UNI.cargar()
    assert real["fecha"] == "2026-11-09" and real["inventario"]["simbolos_en_terminal"] == 9421
    assert {k: real["cuentas"][k] for k in ("fx60", "metales_energia", "indices", "crypto", "crypto_alts", "continuo")} == {
        "fx60": 60, "metales_energia": 16, "indices": 23, "crypto": 17, "crypto_alts": 77, "continuo": 193}
    assert set(INV.FX28) <= set(real["grupos"]["fx60"])
    solo24 = {c["ticker"]: c["simbolo"] for c in real["us_grandes"]["casados"] if c["clase"] == "acciones_us_24"}
    assert sorted(solo24) == ["ARES", "BDX", "CPAY", "CRH", "ECHO", "FERG", "FIX", "META", "Q", "SHW", "SKYD", "SNDK", "WDC"]
    assert solo24["META"] == "META.NAS-24" and all(s.endswith("-24") for s in solo24.values())
    assert sum(s.endswith("-24") for s in real["grupos"]["us_grandes"]) == 13 and real["etiquetas"]["META.NAS-24"] == "META"
    assert sorted(x["ticker"] for x in real["us_grandes"]["sin_casar"]) == ["FDXF", "GOOGL", "HONA", "MDT", "OKE", "VYLR"]
    assert real["cuentas"]["us_grandes"] == 497 and real["sp500"]["sin_casar"] == 6 and real["sp500"]["componentes"] == 503
    filas, cabecera = UNI.leer_sp500()
    assert len(filas) == 503 and "wikipedia.org" in cabecera and "2026-11-09" in cabecera


def prueba_clases_extremo_a_extremo(ejecutar, raiz: str) -> None:
    """`--descargar --simbolos @us_grandes,@continuo --periodos d1`: huecos de 1d por clase, sin tocar fx."""
    u = universos_falsos()
    ahora = utc(2026, 11, 6, 15)
    hueco = {"BTCUSD": {dt.date(2026, 10, 13)}}  # un martes sin cripto: hueco de verdad (y no para nada)
    falsos = []

    def fabrica():
        falsos.append(FA.MT5Falso(ahora_utc_s=ahora, trampas=PROHIBIDAS, cuenta=dict(CRED), abierto=False,
                                  simbolos=SIMBOLOS_C, dias_sin_datos=hueco))
        return LT.TerminalSoloLectura(falsos[-1])
    salida = os.path.join(raiz, "dataC", "U")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        c = ejecutar(["--descargar", "--simbolos", "@us_grandes,@continuo", "--periodos", "d1", "--desde", "2024-01-01",
                      "--hasta", "2026-11-06", "--salida", salida], fabrica=fabrica,
                     cargar_cred=lambda a: LT.Credenciales(**CRED), reloj=lambda: float(ahora),
                     data=os.path.join(raiz, "dataC"), runs=os.path.join(raiz, "runs"), guarda=lambda: None,
                     en_ejecucion=lambda: False, universos=u)
    assert c == 0, buf.getvalue()
    man = _manifest(salida)
    ent = {e["simbolo"]: e for e in man["ficheros"]}
    assert sorted(ent) == sorted(u["grupos"]["us_grandes"] + u["grupos"]["continuo"])
    for s in ("AAPL.NAS", "BRK-B.NYSE", "BF/B.NYSE"):
        h = ent[s]["huecos"]
        assert ent[s]["clase"] == "acciones_us" and h["festivos"] > 20 and h["otros"] == 0, (s, h)
    h = ent["META.NAS-24"]["huecos"]  # solo -24: su clase, calendario NYSE, sin huecos y sin velas de fin de semana
    assert (ent["META.NAS-24"]["clase"], ent["META.NAS-24"]["bolsa"]) == ("acciones_us_24", "NYSE"), ent["META.NAS-24"]
    assert h["otros"] == 0 and h["sesiones_fin_de_semana"] == 0, h
    assert ent["DE40"]["huecos"]["festivos"] > 10 and ent["DE40"]["huecos"]["otros"] == 0 and ent["DE40"]["bolsa"] == "XETRA"
    assert ent["XAUUSD"]["huecos"]["festivos"] > 0 and ent["XAUUSD"]["huecos"]["otros"] == 0
    hb = ent["BTCUSD"]["huecos"]
    assert (hb["fin_de_semana"], hb["otros"], hb["otros_mayores"][0]["desde"]) == (0, 1, "2026-10-13"), hb
    assert ent["ETCUSD"]["huecos"]["otros"] == 0 and ent["ETCUSD"]["clase"] == "crypto"
    assert "metodo" not in ent["EURUSD"]["huecos"] and ent["EURUSD"]["clase"] == "forex"  # fx: el metodo de siempre
    # Nombres de fichero: la '/' de BF/B no llega al disco.
    assert ent["BF/B.NYSE"]["fichero"].startswith("BF_B.NYSE~") and os.path.isfile(os.path.join(salida, ent["BF/B.NYSE"]["fichero"]))
    btc = pq.read_table(os.path.join(salida, ent["BTCUSD"]["fichero"])).to_pandas()
    assert ((btc.time_servidor // 86400 + 3) % 7 >= 5).sum() > 100  # cripto con velas de fin de semana
    assert all(f.llamadas_prohibidas == [] for f in falsos)


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
    # maxbars real (100000): profundidad con count 99999 en una consulta por periodo; m1 queda limitada por maxbars.
    c, out = b(["--inventario", "--simbolos", "USDJPY"], datos="data6", maxbars=100_000)
    f = b.falsos[-1]
    assert c == 0 and f.llamadas["copy_rates_from_pos"] == 4, (out, dict(f.llamadas))
    with open(glob.glob(os.path.join(raiz, "data6", "inventario", "inventario_*.json"))[0], encoding="utf-8") as fi:
        pr = json.load(fi)["simbolos"][0]["profundidad"]
    assert pr["m1"]["velas"] == 99_999 and pr["m1"]["limitada_por_maxbars"] and not pr["d1"]["limitada_por_maxbars"], pr
    assert pr["d1"] == sims["USDJPY"]["profundidad"]["d1"]
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
               lambda: prueba_reintentos_de_datos(esperas), lambda: prueba_copy_rates_from_pos_como_el_real(esperas),
               prueba_calendarios, prueba_universos]
    nombres = [getattr(p, "__name__", "") for p in pruebas[:-5]] + [
        "prueba_arranque_robusto", "prueba_reintentos_de_datos", "prueba_copy_rates_from_pos_como_el_real",
        "prueba_calendarios", "prueba_universos"]
    raiz = os.path.join(TMP, f"selftest_{os.getpid()}")
    os.makedirs(raiz, exist_ok=True)
    try:
        for p, nombre in zip(pruebas, nombres):
            r = p()
            print(f"ok  {nombre}" + (f" ({r} nombres rechazados)" if isinstance(r, int) else ""))
        prueba_clases_extremo_a_extremo(ejecutar, raiz)
        print("ok  prueba_clases_extremo_a_extremo")
        r = prueba_extremo_a_extremo(ejecutar, raiz)
        print(f"ok  prueba_extremo_a_extremo ({r['trozos']} trozos; {r['ficheros_revisados']} ficheros sin secretos; "
              f"hash {r['hash'][:23]}...)")
    finally:
        LT.configurar_reintentos(**previa)
        shutil.rmtree(raiz, ignore_errors=True)
        shutil.rmtree(os.path.join(TMP, "selftest_cred"), ignore_errors=True)
    print("selftest ok")
    return 0
