"""Acceso de SOLO LECTURA al paquete `MetaTrader5`: lista blanca explicita y envoltura que rechaza todo lo demas.

Garantia (la comprueba el selftest, estatica y dinamicamente):
- Este modulo es el unico del extractor que importa el paquete, y la envoltura no guarda el modulo: guarda solo las
  funciones y constantes de la lista blanca. Desde la envoltura no hay camino a ninguna funcion que opere.
- Cualquier nombre fuera de la lista blanca lanza `FuncionNoPermitida`, exista o no en el paquete.
- `initialize()` solo acepta `path` (la ruta del terminal); servidor y credenciales nunca van por ahi.

Dos formas de engancharse (`enganchar`):
- Sin credenciales: el usuario ya abrio y autentico el terminal. Se comprueba antes que `terminal64.exe` esta en ejecucion,
  porque `initialize()` arrancaria el terminal si no lo estuviera, y se llama `initialize()` sin argumentos.
- Con credenciales (cambio de alcance del 2026-11-09, puerta 2): un JSON fuera del repo con `path`, `login`, `password` y
  `server` (por defecto E:/quantdesk-lab/secrets/mt5.json, o la ruta de QDL_MT5_SECRETS). `initialize(path=...)` y
  `login(...)`. Los valores no se imprimen, no se registran y no se guardan: `Credenciales` no los muestra en su repr, los
  mensajes de error pasan por `censurar` y toda salida JSON pasa por `comprobar_sin_secretos` antes de escribirse.
  La procedencia lleva solo el tipo de cuenta, el broker y el terminal: ni el numero de cuenta ni el servidor, tampoco en
  hash (decision de la raiz, fase B). El publicador MT5 -> qn reutiliza todo esto.
"""
from __future__ import annotations

import collections
import json
import os
import re
import subprocess
import time
from types import MappingProxyType

# Lista blanca: solo funciones que consultan, mas `login` para abrir la sesion de lectura con las credenciales del usuario.
# Nada que envie, compruebe o calcule ordenes, ni que cambie el Market Watch. `copy_rates_from_pos` mide la profundidad;
# `symbol_info_tick` detecta el desfase de la hora del servidor con el reloj UTC.
FUNCIONES_PERMITIDAS = frozenset({
    "initialize", "login", "shutdown", "version", "last_error", "terminal_info", "account_info",
    "symbols_total", "symbols_get", "symbol_info", "symbol_info_tick",
    "copy_rates_range", "copy_rates_from_pos", "copy_ticks_range",
})
CONSTANTES_PERMITIDAS = frozenset({
    "TIMEFRAME_M1", "TIMEFRAME_M5", "TIMEFRAME_H1", "TIMEFRAME_D1", "COPY_TICKS_ALL", "RES_S_OK",
    "ACCOUNT_TRADE_MODE_DEMO", "ACCOUNT_TRADE_MODE_CONTEST", "ACCOUNT_TRADE_MODE_REAL",
    "SYMBOL_CHART_MODE_BID", "SYMBOL_CHART_MODE_LAST",
})
RUTA_SECRETOS = "E:/quantdesk-lab/secrets/mt5.json"
VAR_SECRETOS = "QDL_MT5_SECRETS"


class FuncionNoPermitida(PermissionError):
    """Se pidio al paquete algo fuera de la lista blanca de solo lectura."""


class TerminalNoDisponible(RuntimeError):
    """El terminal no esta abierto, no esta conectado o no tiene una cuenta con sesion iniciada."""


class SecretoEnSalida(RuntimeError):
    """Una salida iba a contener un valor de las credenciales: no se escribe."""


def _initialize_solo_ruta(f):
    def initialize(*args, **kwargs):
        if args or set(kwargs) - {"path"}:
            raise FuncionNoPermitida("initialize() solo acepta path=: servidor y credenciales nunca van por initialize")
        return f(**kwargs)
    return initialize


class TerminalSoloLectura:
    """Envoltura del paquete (real o falso). Solo expone la lista blanca; no guarda el modulo."""

    __slots__ = ("_funciones", "_constantes", "version_paquete")

    def __init__(self, modulo) -> None:
        faltan = sorted(n for n in FUNCIONES_PERMITIDAS | CONSTANTES_PERMITIDAS if not hasattr(modulo, n))
        if faltan:
            raise RuntimeError(f"el paquete MetaTrader5 no tiene {faltan}: la version no es la esperada")
        funciones = {n: getattr(modulo, n) for n in sorted(FUNCIONES_PERMITIDAS)}
        funciones["initialize"] = _initialize_solo_ruta(funciones["initialize"])
        object.__setattr__(self, "_funciones", MappingProxyType(funciones))
        object.__setattr__(self, "_constantes", MappingProxyType({n: getattr(modulo, n) for n in sorted(CONSTANTES_PERMITIDAS)}))
        object.__setattr__(self, "version_paquete", str(getattr(modulo, "__version__", "desconocida")))

    def __getattr__(self, nombre: str):
        funciones = object.__getattribute__(self, "_funciones")
        if nombre in funciones:
            return funciones[nombre]
        constantes = object.__getattribute__(self, "_constantes")
        if nombre in constantes:
            return constantes[nombre]
        raise FuncionNoPermitida(f"MetaTrader5.{nombre} no esta en la lista blanca de solo lectura del extractor")

    def __setattr__(self, nombre, valor) -> None:
        raise FuncionNoPermitida("la envoltura de solo lectura es inmutable")

    def __delattr__(self, nombre) -> None:
        raise FuncionNoPermitida("la envoltura de solo lectura es inmutable")


def importar_paquete() -> TerminalSoloLectura:
    """Unica importacion del paquete en el extractor; devuelve solo la envoltura."""
    import MetaTrader5

    return TerminalSoloLectura(MetaTrader5)


class Credenciales:
    """Credenciales del terminal leidas de un fichero fuera del repo. Su repr no muestra ningun valor."""

    __slots__ = ("path", "login", "password", "server")

    def __init__(self, path: str, login: int, password: str, server: str) -> None:
        self.path, self.login, self.password, self.server = str(path), int(login), str(password), str(server)

    def __repr__(self) -> str:
        return "Credenciales(<ocultas>)"

    __str__ = __repr__

    def valores(self) -> list[str]:
        """Textos que nunca deben aparecer en una salida (el path no es secreto: puede revelar el usuario, tampoco sale)."""
        return [v for v in (str(self.login), self.password, self.server, self.path) if v]


def ruta_secretos() -> str:
    return os.environ.get(VAR_SECRETOS) or RUTA_SECRETOS


def leer_credenciales(ruta: str) -> Credenciales:
    try:
        with open(ruta, encoding="utf-8") as f:
            d = json.load(f)
        return Credenciales(d["path"], d["login"], d["password"], d["server"])
    except (OSError, ValueError, KeyError, TypeError) as e:  # el mensaje no incluye el contenido del fichero
        raise TerminalNoDisponible(f"no se pudieron leer las credenciales de {ruta}: {type(e).__name__}") from None


def censurar(texto: str, cred: Credenciales | None) -> str:
    if cred is not None:
        for v in sorted(cred.valores(), key=len, reverse=True):
            texto = texto.replace(v, "***")
    return texto


def comprobar_sin_secretos(texto: str, cred: Credenciales | None) -> str:
    if cred is not None:
        for v in cred.valores():
            if v and v in texto:
                raise SecretoEnSalida("una salida contenia un valor de las credenciales: no se escribe")
    return texto


class Secretos:
    """Varios secretos juntos (credenciales del terminal, token de qn) para `censurar` y `comprobar_sin_secretos`."""

    __slots__ = ("_valores",)

    def __init__(self, *fuentes) -> None:
        vals: list[str] = []
        for f in fuentes:
            if f is None:
                continue
            vals.extend(f.valores() if hasattr(f, "valores") else [str(f)])
        self._valores = [v for v in vals if v]

    def valores(self) -> list[str]:
        return list(self._valores)

    def __repr__(self) -> str:
        return "Secretos(<ocultos>)"

    __str__ = __repr__


def procedencia(term, ti, ai) -> dict:
    """Procedencia sin datos de la cuenta (decision de la raiz, fase B): tipo de cuenta, broker y terminal. Ni el numero
    de cuenta ni el servidor, tampoco como hash."""
    modos = {term.ACCOUNT_TRADE_MODE_DEMO: "demo", term.ACCOUNT_TRADE_MODE_CONTEST: "concurso",
             term.ACCOUNT_TRADE_MODE_REAL: "real"}
    v = term.version()
    return {"broker": ai.company, "cuenta_tipo": modos.get(ai.trade_mode, "desconocido"),
            "terminal": {"version": list(v) if v else None, "build": int(ti.build), "nombre": ti.name,
                         "empresa": ti.company, "maxbars": int(ti.maxbars)},
            "paquete_python": f"MetaTrader5 {term.version_paquete}"}


def slug(texto: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", texto or "desconocido").strip("._") or "desconocido"


def terminal_en_ejecucion() -> bool:
    """True si hay un `terminal64.exe` en ejecucion (lista de procesos de Windows, solo lectura)."""
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq terminal64.exe", "/NH", "/FO", "CSV"],
                           capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    return "terminal64.exe" in r.stdout.lower()


# --- Reintentos frente al terminal real (entrega 6) ------------------------------------------------------------------
# Datos: la primera consulta de un par y periodo que el terminal aun no tiene sincronizado devuelve None con
# (-1, 'Terminal: Call failed') mientras baja la historia; un terminal ocupado puede dar (-10005, 'IPC timeout').
# Arranque: volver a hacer initialize(path) + login con el terminal ya abierto y ocupado da (-6, 'Authorization failed')
# o (-10005, 'IPC timeout') de forma transitoria. En ambos casos se reintenta con esperas crecientes (por defecto 1, 2,
# 4 y 8 s: 5 intentos); agotados, el error es el mismo que sin reintentos. Esperas configurables con la variable de
# entorno QDL_MT5_ESPERAS ("1,2,4,8") o con `configurar_reintentos` (los selftests inyectan un dormir que no duerme).
TRANSITORIOS_DATOS = (-1, -10005)
TRANSITORIOS_ARRANQUE = (-6, -10005)


def _esperas_de_entorno() -> tuple:
    txt = os.environ.get("QDL_MT5_ESPERAS", "")
    try:
        vals = tuple(float(x) for x in txt.split(",") if x.strip())
    except ValueError:
        vals = ()
    return vals if vals and all(v >= 0 for v in vals) else (1.0, 2.0, 4.0, 8.0)


REINTENTO = {"esperas_s": _esperas_de_entorno(), "dormir": time.sleep, "espera_conexion_s": 60.0,
             "contador": collections.Counter()}


def configurar_reintentos(esperas_s=None, dormir=None, espera_conexion_s=None) -> dict:
    """Cambia la politica de reintentos; devuelve la anterior (para restaurarla)."""
    previa = {k: REINTENTO[k] for k in ("esperas_s", "dormir", "espera_conexion_s")}
    if esperas_s is not None:
        REINTENTO["esperas_s"] = tuple(float(x) for x in esperas_s)
    if dormir is not None:
        REINTENTO["dormir"] = dormir
    if espera_conexion_s is not None:
        REINTENTO["espera_conexion_s"] = float(espera_conexion_s)
    return previa


def es_transitorio(err, codigos) -> bool:
    return bool(err) and err[0] in codigos


def con_reintentos(term, accion, nombre: str, codigos, cred=None, al_fallar=None):
    """Ejecuta `accion()` (devuelve un valor o algo falso) reintentando los errores transitorios `codigos`. Devuelve el
    valor; agotados los intentos, o ante un error no transitorio, lanza TerminalNoDisponible con el ultimo error."""
    esperas = REINTENTO["esperas_s"]
    for k in range(len(esperas) + 1):
        r = accion()
        if r:
            return r
        err = term.last_error()
        if not es_transitorio(err, codigos) or k == len(esperas):
            if al_fallar is not None:
                al_fallar()
            raise TerminalNoDisponible(f"{nombre} fallo {censurar(str(err), cred)}")
        REINTENTO["contador"][nombre] += 1
        REINTENTO["dormir"](esperas[k])
    raise AssertionError("inalcanzable")


def misma_cuenta(ai, cred: Credenciales) -> bool:
    """La cuenta abierta en el terminal es la del fichero. Se compara sin imprimir ni registrar ningun valor."""
    try:
        return int(ai.login) == cred.login and str(ai.server) == cred.server
    except (TypeError, ValueError, AttributeError):
        return False


def esperar_conexion(term):
    """Espera acotada (REINTENTO['espera_conexion_s'], sondeo cada 1 s) a que el terminal este conectado y con cuenta."""
    esperado = 0.0
    while True:
        ti, ai = term.terminal_info(), term.account_info()
        if ti is not None and ai is not None and getattr(ti, "connected", False):
            return ti, ai
        if esperado >= REINTENTO["espera_conexion_s"]:
            return None
        REINTENTO["dormir"](1.0)
        esperado += 1.0


def enganchar(term: TerminalSoloLectura, cred: Credenciales | None = None, en_ejecucion=terminal_en_ejecucion):
    """Abre la sesion de lectura. Devuelve (terminal_info, account_info). Errores con mensajes censurados.

    Sin credenciales: el terminal tiene que estar ya abierto; `initialize()` sin argumentos.
    Con credenciales (la tarea programada):
    1. Si ya hay un terminal64.exe abierto, se prueba `initialize()` sin ruta. Si tiene abierta la MISMA cuenta que el
       fichero (comparada sin imprimirla), se usa tal cual: ni initialize(path) ni login; solo la espera acotada a que
       este conectado (un terminal recien abierto tarda en conectar).
    2. Si no, `initialize(path)` (solo si el enganche sin ruta no fue posible) y `login`, los dos con reintentos
       acotados ante -6 / -10005 transitorios, y una espera acotada a `terminal_info().connected`.
    """
    if cred is None:
        if not en_ejecucion():
            raise TerminalNoDisponible(
                "MetaTrader 5 no esta abierto (no hay terminal64.exe en ejecucion) y no hay credenciales: abrelo e inicia "
                f"sesion, o deja el fichero de credenciales en {RUTA_SECRETOS} (o en la ruta de {VAR_SECRETOS}).")
        con_reintentos(term, lambda: term.initialize(), "initialize()", TRANSITORIOS_ARRANQUE)
    else:
        enganchado = misma = False
        if en_ejecucion() and term.initialize():
            enganchado = True
            ai = term.account_info()
            misma = ai is not None and misma_cuenta(ai, cred)
        if misma:
            REINTENTO["contador"]["enganche sin login"] += 1
        else:
            if not enganchado:
                con_reintentos(term, lambda: term.initialize(path=cred.path),
                               "initialize(path=<del fichero de credenciales>)", TRANSITORIOS_ARRANQUE, cred,
                               al_fallar=term.shutdown)
            con_reintentos(term, lambda: term.login(cred.login, password=cred.password, server=cred.server),
                           "login() (revisa el fichero de credenciales, no se muestra)", TRANSITORIOS_ARRANQUE, cred,
                           al_fallar=term.shutdown)
    r = esperar_conexion(term)
    if r is None:
        term.shutdown()
        raise TerminalNoDisponible("el terminal esta abierto pero sin conexion al servidor o sin cuenta con sesion iniciada")
    return r
