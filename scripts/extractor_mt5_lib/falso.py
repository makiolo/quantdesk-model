"""Modulo `MetaTrader5` falso para el selftest: mismas firmas, constantes, tuplas con nombre y dtypes que el paquete 5.0.6231
(el selftest lo compara con el paquete instalado leyendo su API, sin llamarla). Datos sinteticos deterministas generados al
vuelo: un broker con hora de servidor `ny+7` (o la regla que se le pase), FX de domingo 17:00 a viernes 17:00 hora de NY,
un simbolo 24x7, uno de bolsa con velas de Last y sin ticks, sufijos y una base compartida. Puede fallar a proposito tras N
consultas de datos (reanudacion a medias) y lleva trampas: funciones con los nombres prohibidos que, si se llamaran,
quedan registradas y lanzan error.
"""
from __future__ import annotations

import collections
import datetime as dt
import fnmatch

import numpy as np

from . import calendarios as CAL
from . import hora as HR

VERSION = "5.0.6231"
TIMEFRAME_M1, TIMEFRAME_M5, TIMEFRAME_H1, TIMEFRAME_D1 = 1, 5, 16385, 16408
PASOS = {TIMEFRAME_M1: 60, TIMEFRAME_M5: 300, TIMEFRAME_H1: 3600, TIMEFRAME_D1: 86400}
COPY_TICKS_ALL = -1
RES_S_OK, RES_E_FAIL, RES_E_INVALID_PARAMS, RES_E_AUTH_FAILED = 1, -1, -2, -6
ACCOUNT_TRADE_MODE_DEMO, ACCOUNT_TRADE_MODE_CONTEST, ACCOUNT_TRADE_MODE_REAL = 0, 1, 2
SYMBOL_CHART_MODE_BID, SYMBOL_CHART_MODE_LAST = 0, 1

DTYPE_VELAS = np.dtype([("time", "<i8"), ("open", "<f8"), ("high", "<f8"), ("low", "<f8"), ("close", "<f8"),
                        ("tick_volume", "<u8"), ("spread", "<i4"), ("real_volume", "<u8")])
DTYPE_TICKS = np.dtype([("time", "<i8"), ("bid", "<f8"), ("ask", "<f8"), ("last", "<f8"), ("volume", "<u8"),
                        ("time_msc", "<i8"), ("flags", "<u4"), ("volume_real", "<f8")])

CAMPOS = {
    "TerminalInfo": ("community_account", "community_connection", "connected", "dlls_allowed", "trade_allowed",
                     "tradeapi_disabled", "email_enabled", "ftp_enabled", "notifications_enabled", "mqid", "build", "maxbars",
                     "codepage", "ping_last", "community_balance", "retransmission", "company", "name", "language", "path",
                     "data_path", "commondata_path"),
    "AccountInfo": ("login", "trade_mode", "leverage", "limit_orders", "margin_so_mode", "trade_allowed", "trade_expert",
                    "margin_mode", "currency_digits", "fifo_close", "balance", "credit", "profit", "equity", "margin",
                    "margin_free", "margin_level", "margin_so_call", "margin_so_so", "margin_initial", "margin_maintenance",
                    "assets", "liabilities", "commission_blocked", "name", "server", "currency", "company"),
    "Tick": ("time", "bid", "ask", "last", "volume", "time_msc", "flags", "volume_real"),
    "SymbolInfo": (
        "custom", "chart_mode", "select", "visible", "session_deals", "session_buy_orders", "session_sell_orders", "volume",
        "volumehigh", "volumelow", "time", "digits", "spread", "spread_float", "ticks_bookdepth", "trade_calc_mode",
        "trade_mode", "start_time", "expiration_time", "trade_stops_level", "trade_freeze_level", "trade_exemode",
        "swap_mode", "swap_rollover3days", "margin_hedged_use_leg", "expiration_mode", "filling_mode", "order_mode",
        "order_gtc_mode", "option_mode", "option_right", "bid", "bidhigh", "bidlow", "ask", "askhigh", "asklow", "last",
        "lasthigh", "lastlow", "volume_real", "volumehigh_real", "volumelow_real", "option_strike", "point",
        "trade_tick_value", "trade_tick_value_profit", "trade_tick_value_loss", "trade_tick_size", "trade_contract_size",
        "trade_accrued_interest", "trade_face_value", "trade_liquidity_rate", "volume_min", "volume_max", "volume_step",
        "volume_limit", "swap_long", "swap_short", "margin_initial", "margin_maintenance", "session_volume",
        "session_turnover", "session_interest", "session_buy_orders_volume", "session_sell_orders_volume", "session_open",
        "session_close", "session_aw", "session_price_settlement", "session_price_limit_min", "session_price_limit_max",
        "margin_hedged", "price_change", "price_volatility", "price_theoretical", "price_greeks_delta",
        "price_greeks_theta", "price_greeks_gamma", "price_greeks_vega", "price_greeks_rho", "price_greeks_omega",
        "price_sensitivity", "basis", "category", "currency_base", "currency_profit", "currency_margin", "bank",
        "description", "exchange", "formula", "isin", "name", "page", "path"),
}
TerminalInfo = collections.namedtuple("TerminalInfo", CAMPOS["TerminalInfo"])
AccountInfo = collections.namedtuple("AccountInfo", CAMPOS["AccountInfo"])
Tick = collections.namedtuple("Tick", CAMPOS["Tick"])
SymbolInfo = collections.namedtuple("SymbolInfo", CAMPOS["SymbolInfo"])


def _d(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp())


# nombre: (base, beneficio, digitos, horario, precio, chart_mode, ticks[, ruta en el terminal])
# horario: "fx" (domingo 17:00 a viernes 17:00 NY), "24x7", "bolsa" (9:30-16:00 NY sin los festivos de la NYSE) o
# "fx:<BOLSA>" (horario de fx sin velas en los festivos de esa bolsa, por fecha del servidor; fase C).
SIMBOLOS = {
    "EURUSD.a": ("EUR", "USD", 5, "fx", 1.08, SYMBOL_CHART_MODE_BID, True),
    "EURUSD.pro": ("EUR", "USD", 5, "fx", 1.0801, SYMBOL_CHART_MODE_BID, True),
    "GBPUSDm": ("GBP", "USD", 5, "fx", 1.27, SYMBOL_CHART_MODE_BID, True),
    "USDJPY": ("USD", "JPY", 3, "fx", 150.0, SYMBOL_CHART_MODE_BID, True),
    "BTCUSD.x": ("BTC", "USD", 2, "24x7", 65000.0, SYMBOL_CHART_MODE_BID, True),
    "AAPL.US": ("USD", "USD", 2, "bolsa", 190.0, SYMBOL_CHART_MODE_LAST, False),
}
HISTORIA = {TIMEFRAME_M1: _d(2026, 1, 1), TIMEFRAME_M5: _d(2025, 6, 1), TIMEFRAME_H1: _d(2024, 1, 1), TIMEFRAME_D1: _d(2015, 1, 1)}


class ErrorTrampa(AssertionError):
    pass


class MT5Falso:
    """Se usa como modulo: `TerminalSoloLectura(MT5Falso(...))`."""

    def __init__(self, ahora_utc_s: int, regla: str = "ny+7", fallar_tras: int | None = None, abierto: bool = True,
                 cuenta: dict | None = None, trampas: tuple = (), maxbars: int = 5_000_000, simbolos=None,
                 fallos_call_failed: int = 0, fallos_arranque: tuple = (), retraso_conexion: int = 0,
                 cuenta_abierta: dict | None = None, dias_sin_datos: dict | None = None) -> None:
        """Fallos del terminal real que reproduce (entrega 6):
        - `fallos_call_failed` = N: las N primeras consultas de datos de cada (funcion, simbolo, periodo) devuelven None con
          (-1, 'Terminal: Call failed'), como un terminal que aun sincroniza esa historia.
        - `fallos_arranque`: codigos (-6 'Authorization failed', -10005 'IPC timeout') que devuelven, por orden, las
          llamadas a initialize(path=...) y login() de un terminal ocupado.
        - `retraso_conexion` = N: tras el login (o al engancharse a un terminal ya abierto), las N primeras
          terminal_info() dicen connected=False.
        - `cuenta_abierta`: la cuenta con la que esta abierto un terminal que ya estaba en marcha (por defecto, la del
          fichero de credenciales).
        - `dias_sin_datos`: simbolo -> fechas (dt.date, del servidor) sin ninguna vela ni tick: un hueco de mercado que no
          es fin de semana ni festivo (fase C)."""
        self.__version__ = VERSION
        for n, v in globals().items():
            if n.isupper() and isinstance(v, int):
                setattr(self, n, v)
        self.TerminalInfo, self.AccountInfo, self.Tick, self.SymbolInfo = TerminalInfo, AccountInfo, Tick, SymbolInfo
        self.ahora_utc_s, self.regla = int(ahora_utc_s), HR.regla_desde_texto(regla)
        self.fallar_tras, self.abierto, self.maxbars = fallar_tras, abierto, maxbars
        self.cuenta = cuenta or {"login": 11223344, "password": "pw-falsa", "server": "Falso-Demo", "path": "C:/Falso/terminal64.exe"}
        self.cuenta_abierta = dict(cuenta_abierta) if cuenta_abierta else {k: self.cuenta[k] for k in ("login", "server")}
        self._cuenta_activa = dict(self.cuenta_abierta)
        self.fallos_call_failed, self._call_failed = int(fallos_call_failed), collections.Counter()
        self.fallos_arranque = list(fallos_arranque)
        self.retraso_conexion, self._pendiente_conexion = int(retraso_conexion), 0
        self.simbolos = dict(SIMBOLOS if simbolos is None else simbolos)
        self.dias_sin_datos = {k: np.array(sorted((d - dt.date(1970, 1, 1)).days for d in v), dtype=np.int64)
                               for k, v in (dias_sin_datos or {}).items()}
        self.iniciado = self.sesion = False
        self.consultas_datos = 0
        self.llamadas = collections.Counter()
        self.llamadas_prohibidas: list[str] = []
        self._error = (RES_S_OK, "Success")
        self._cache_pos: dict = {}
        for nombre in trampas:
            setattr(self, nombre, self._trampa(nombre))

    def _trampa(self, nombre):
        def f(*a, **k):
            self.llamadas_prohibidas.append(nombre)
            raise ErrorTrampa(f"se llamo a la funcion prohibida {nombre}")
        return f

    # ---- sesion ----
    def initialize(self, path=None, *, login=None, password=None, server=None, timeout=None, portable=False):
        self.llamadas["initialize"] += 1
        if login is not None or password is not None or server is not None:
            self.llamadas_prohibidas.append("initialize con credenciales")
        if path is not None:
            self.llamadas["initialize con ruta"] += 1
        if path is not None and path != self.cuenta["path"]:
            self._error = (RES_E_FAIL, "Terminal: path not found")
            return False
        if path is not None and self._fallo_arranque():
            return False
        if not self.abierto and path is None:
            self._error = (-10003, "IPC initialize failed, MetaTrader 5 x64 not found")
            return False
        self.iniciado = True
        self.sesion = self.abierto  # un terminal ya abierto por el usuario tiene sesion
        if self.abierto:  # recien abierto: puede tardar en conectar con el servidor
            self._pendiente_conexion = self.retraso_conexion
        self._cuenta_activa = dict(self.cuenta_abierta)
        self._error = (RES_S_OK, "Success")
        return True

    def _fallo_arranque(self) -> bool:
        if not self.fallos_arranque:
            return False
        codigo = self.fallos_arranque.pop(0)
        self._error = (codigo, {-6: "Terminal: Authorization failed", -10005: "IPC timeout"}.get(codigo, "Terminal: error"))
        return True

    def login(self, login, password=None, server=None, timeout=60000):
        self.llamadas["login"] += 1
        if self._fallo_arranque():
            return False
        ok = self.iniciado and login == self.cuenta["login"] and password == self.cuenta["password"] and server == self.cuenta["server"]
        self.sesion = ok
        if ok:
            self._cuenta_activa = {k: self.cuenta[k] for k in ("login", "server")}
            self._pendiente_conexion = self.retraso_conexion
        self._error = (RES_S_OK, "Success") if ok else (RES_E_AUTH_FAILED, "Authorization failed")
        return ok

    def shutdown(self):
        self.iniciado = self.sesion = False
        return True

    def last_error(self):
        return self._error

    def version(self):
        return (500, 5000, "01 Jan 2026") if self.iniciado else None

    def terminal_info(self):
        if not self.iniciado:
            return None
        conectado = self.sesion and self._pendiente_conexion == 0
        if self._pendiente_conexion > 0:
            self._pendiente_conexion -= 1
        v = dict.fromkeys(CAMPOS["TerminalInfo"], 0)
        v.update(connected=conectado, build=5000, maxbars=self.maxbars, company="Broker Falso Ltd.", name="Broker Falso MT5",
                 language="Spanish", path="C:/Falso", data_path="C:/Users/falso/AppData", commondata_path="C:/Users/falso/Common",
                 mqid=False, trade_allowed=True)
        return TerminalInfo(**v)

    def account_info(self):
        if not self.sesion:
            return None
        v = dict.fromkeys(CAMPOS["AccountInfo"], 0)
        v.update(login=self._cuenta_activa["login"], trade_mode=ACCOUNT_TRADE_MODE_DEMO, server=self._cuenta_activa["server"],
                 company="Broker Falso Ltd.", name="Titular Falso", currency="EUR", balance=10000.0)
        return AccountInfo(**v)

    # ---- simbolos ----
    def _info(self, nombre):
        b, p, dig, _, precio, cm, *resto = self.simbolos[nombre]
        ruta = resto[1] if len(resto) > 1 else "Falso\\" + nombre
        v = dict.fromkeys(CAMPOS["SymbolInfo"], 0)
        v.update(name=nombre, currency_base=b, currency_profit=p, currency_margin=b, digits=dig, point=10.0 ** -dig,
                 chart_mode=cm, visible=True, select=True, description=f"{b}/{p} sintetico", path=ruta,
                 bid=precio, ask=precio, spread_float=True, bank="", exchange="", formula="", isin="", page="", basis="",
                 category="")
        return SymbolInfo(**v)

    def symbols_total(self):
        return len(self.simbolos) if self.sesion else None

    def symbols_get(self, group=None):
        if not self.sesion:
            return None
        return tuple(self._info(n) for n in sorted(self.simbolos) if group is None or fnmatch.fnmatchcase(n, group))

    def symbol_info(self, symbol):
        return self._info(symbol) if self.sesion and symbol in self.simbolos else None

    def symbol_info_tick(self, symbol):
        if not self.sesion or symbol not in self.simbolos:
            return None
        s = self.regla.utc_a_servidor(self.ahora_utc_s - 2)  # tick de hace 2 s
        b, a = self._precios(symbol, np.array([self.ahora_utc_s - 2]))
        return Tick(s, float(b[0]), float(a[0]), 0.0, 0, s * 1000, 6, 0.0)

    # ---- datos ----
    def _contar(self):
        self.consultas_datos += 1
        if self.fallar_tras is not None and self.consultas_datos > self.fallar_tras:
            self._error = (-10005, "IPC timeout")
            return False
        self._error = (RES_S_OK, "Success")
        return True

    def _sincronizando(self, *clave) -> bool:
        """Las N primeras consultas de cada clave fallan con -1 'Call failed', como un terminal que baja esa historia."""
        if self._call_failed[clave] < self.fallos_call_failed:
            self._call_failed[clave] += 1
            self.llamadas["call failed"] += 1
            self._error = (RES_E_FAIL, "Terminal: Call failed")
            return True
        return False

    def _reales(self, s):
        """Horas de servidor que existen en el reloj del broker (fuera la hora que se salta al pasar al verano)."""
        u = self.regla.servidor_a_utc(s)[0]
        ok = (u + self.regla.desfase(u)) == s
        return s[ok], u[ok]

    def _abierto(self, nombre, u, paso):
        ok = self._abierto_horario(nombre, u, paso)
        if nombre in self.dias_sin_datos:
            ok &= ~np.isin((u + self.regla.desfase(u)) // 86400, self.dias_sin_datos[nombre])
        return ok

    def _abierto_horario(self, nombre, u, paso):
        horario = self.simbolos[nombre][3]
        if horario == "24x7":
            return np.ones(u.shape, dtype=bool)
        ny = u + HR.NUEVA_YORK.desfase(u)
        dia, minuto = (ny // 86400 + 3) % 7, (ny % 86400) // 60
        bolsa = "NYSE" if horario == "bolsa" else horario[3:] if horario.startswith("fx:") else None
        if paso == 86400:  # vela diaria: dia de la semana del servidor (y sin los festivos de su bolsa)
            dia_s = (u + self.regla.desfase(u)) // 86400
            return (((dia_s + 3) % 7) < 5) & ~self._festivo(bolsa, dia_s)
        if horario == "bolsa":
            return (dia < 5) & (minuto >= 570) & (minuto < 960) & ~self._festivo(bolsa, ny // 86400)
        if bolsa is not None:
            cerrado_hoy = self._festivo(bolsa, (u + self.regla.desfase(u)) // 86400)
            return ~((dia == 5) | ((dia == 4) & (minuto >= 1020)) | ((dia == 6) & (minuto < 1020)) | cerrado_hoy)
        cerrado = (dia == 5) | ((dia == 4) & (minuto >= 1020)) | ((dia == 6) & (minuto < 1020))
        return ~cerrado

    @staticmethod
    def _festivo(bolsa, dias):
        dias = np.asarray(dias, dtype=np.int64)
        if bolsa is None or dias.size == 0:
            return np.zeros(dias.shape, dtype=bool)
        anios = range(CAL.fecha(int(dias.min())).year, CAL.fecha(int(dias.max())).year + 1)
        fest = sorted((d - CAL.EPOCA).days for a in anios for d in CAL.festivos(bolsa, a))
        return np.isin(dias, np.array(fest, dtype=np.int64))

    def _precios(self, nombre, u):
        dig, precio = self.simbolos[nombre][2], self.simbolos[nombre][4]
        x = u.astype(np.float64)
        bid = np.round(precio * (1 + 0.01 * np.sin(x / 259200.0) + 0.002 * np.sin(x / 3700.0)), dig)
        sp = 8 + (u // 60) % 7
        return bid, np.round(bid + sp * 10.0 ** -dig, dig)

    def _velas(self, nombre, tf, s_ini, s_fin):
        paso = PASOS[tf]
        s0 = -(-int(s_ini) // paso) * paso
        s = np.arange(s0, int(s_fin) + 1, paso, dtype=np.int64)
        # Como el terminal real, incluye la vela en curso (abierta antes de "ahora" y aun sin cerrar).
        s = s[(s >= self.regla.utc_a_servidor(HISTORIA[tf])) & (s <= self.regla.utc_a_servidor(self.ahora_utc_s))]
        s, u = self._reales(s)
        s = s[self._abierto(nombre, u, paso)]
        u = self.regla.servidor_a_utc(s)[0]
        dig = self.simbolos[nombre][2]
        o, _ = self._precios(nombre, u)
        c, _ = self._precios(nombre, u + paso)
        k = 10.0 ** -dig * 3
        out = np.zeros(s.size, dtype=DTYPE_VELAS)
        out["time"], out["open"], out["close"] = s, o, c
        out["high"], out["low"] = np.round(np.maximum(o, c) + k, dig), np.round(np.minimum(o, c) - k, dig)
        out["tick_volume"] = 50 + (u // 60) % 100
        out["spread"] = 8 + (u // 60) % 7
        out["real_volume"] = 0 if self.simbolos[nombre][5] == SYMBOL_CHART_MODE_BID else 1000 + (u // 60) % 10
        return out

    @staticmethod
    def _seg(x):
        return int(x.timestamp()) if isinstance(x, dt.datetime) else int(x)

    def copy_rates_range(self, symbol, timeframe, date_from, date_to):
        self.llamadas["copy_rates_range"] += 1
        if not self.sesion or symbol not in self.simbolos or not self._contar():
            return None
        if self._sincronizando("copy_rates_range", symbol, timeframe):
            return None
        return self._velas(symbol, timeframe, self._seg(date_from), self._seg(date_to))

    def copy_rates_from_pos(self, symbol, timeframe, start_pos, count):
        self.llamadas["copy_rates_from_pos"] += 1
        if not self.sesion or symbol not in self.simbolos:
            return None
        if self._sincronizando("copy_rates_from_pos", symbol, timeframe):
            return None
        # Medido en el terminal real (build 6230, maxbars 100000; entrega 6b):
        # - count >= maxbars: None con (-2, 'Terminal: Invalid params'), en todos los periodos;
        # - start_pos fuera de la historia: None con (-1, 'Terminal: Call failed'), el mismo codigo que la sincronizacion;
        # - si no, min(count, disponibles desde start_pos).
        if count >= self.maxbars:
            self._error = (RES_E_INVALID_PARAMS, "Terminal: Invalid params")
            return None
        clave = (symbol, timeframe)
        if clave not in self._cache_pos:
            self._cache_pos[clave] = self._velas(symbol, timeframe, self.regla.utc_a_servidor(HISTORIA[timeframe]),
                                                 self.regla.utc_a_servidor(self.ahora_utc_s))
        todas = self._cache_pos[clave][::-1][: self.maxbars]
        if start_pos >= len(todas):
            self._error = (RES_E_FAIL, "Terminal: Call failed")
            return None
        self._error = (RES_S_OK, "Success")
        return todas[start_pos:start_pos + count][::-1].copy()

    def copy_ticks_range(self, symbol, date_from, date_to, flags):
        self.llamadas["copy_ticks_range"] += 1
        if not self.sesion or symbol not in self.simbolos or not self._contar():
            return None
        if self._sincronizando("copy_ticks_range", symbol):
            return None
        if not self.simbolos[symbol][6]:
            return np.zeros(0, dtype=DTYPE_TICKS)
        a, b = self._seg(date_from), min(self._seg(date_to), self.regla.utc_a_servidor(self.ahora_utc_s))
        s = np.arange(-(-a // 20) * 20, b, 20, dtype=np.int64)
        s, u = self._reales(s)
        s = s[self._abierto(symbol, u, 60)]
        u = self.regla.servidor_a_utc(s)[0]
        bid, ask = self._precios(symbol, u)
        out = np.zeros(s.size, dtype=DTYPE_TICKS)
        out["time"], out["bid"], out["ask"] = s, bid, ask
        out["time_msc"] = s * 1000 + (s * 7919) % 1000
        out["flags"] = 6
        return out
