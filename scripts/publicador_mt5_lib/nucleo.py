"""Nucleo del publicador MT5 -> qn: configuracion, candado, barras cerradas de MT5, plan por serie y publicacion.

Una serie es (simbolo, intervalo) con la fuente fija (`source=mt5` por defecto). En cada ejecucion:
1. `L` = `ts` de la ultima barra de la serie que qn confirma (`latest` filtrado por los tres tags). Sin nada en qn, se
   empieza en la fecha inicial del intervalo.
2. Se leen de MT5 las velas CERRADAS (apertura + intervalo <= ahora) desde un poco antes de `L` hasta ahora; la hora del
   servidor se pasa a UTC con la regla del extractor.
3. Comprobacion de la cola: de las `ventana` velas de MT5 con ts <= L se pregunta a qn cuales tiene (`/objects`). Las que
   faltan son huecos de una ejecucion anterior cortada a mitad de una ventana y se publican; las que estan pero con otro
   contenido se cuentan como revisiones y NO se republican (decision documentada en fase-b.md).
4. Se publica en orden de ts por ventanas de `ventana` barras, cada ventana en paralelo (`hilos`). La siguiente ventana
   solo empieza si la anterior entro entera; si algo falla, la serie se para. Asi los huecos solo pueden quedar dentro
   de la ultima ventana, y la siguiente ejecucion los rellena en el paso 3. No hay registro local de progreso: manda qn.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from extractor_mt5_lib import descarga as D
from extractor_mt5_lib import hora as HR

from . import qn as Q

INTERVALOS = {"1d": "d1", "1h": "h1", "5m": "m5", "1m": "m1"}  # intervalo de qn -> periodo del extractor
PASO_S = {"1d": 86400, "1h": 3600, "5m": 300, "1m": 60}
MARGEN_COLA_S = 4 * 86400  # la cola de `ventana` velas puede cruzar un fin de semana largo


@dataclasses.dataclass
class Config:
    urls: list
    env: str = "main"
    topic: str = "market.ohlcv"
    tag_simbolo: str = "symbol"
    tag_intervalo: str = "interval"
    tag_fuente: str = "source"
    fuente: str = "mt5"
    fuente_en_objeto: bool = True  # el esquema actual exige `source` dentro del objeto
    # Profundidad inicial (solo cuando qn no tiene nada de la serie): fecha fija o ventana reciente en dias.
    inicio: dict = dataclasses.field(default_factory=lambda: {"1d": "2000-01-01", "1h": "2000-01-01", "5m": 30, "1m": 30})
    hilos: int = 8
    ventana: int = 64
    espera_max_s: float = 30.0
    caducidad_candado_s: int = 3 * 3600


class Candado:
    """Ejecucion unica: fichero creado en exclusiva. El que lo tiene lo "late" (mtime) en cada ventana; uno sin latido
    durante `caducidad_s` se da por caducado (proceso muerto o maquina apagada) y se recupera."""

    def __init__(self, ruta: str, caducidad_s: float) -> None:
        self.ruta, self.caducidad_s, self.recuperado = ruta, caducidad_s, False

    def tomar(self) -> bool:
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    edad = time.time() - os.path.getmtime(self.ruta)
                except OSError:
                    continue  # lo acaban de soltar
                if edad <= self.caducidad_s:
                    return False
                try:
                    os.remove(self.ruta)
                    self.recuperado = True
                except OSError:
                    return False
                continue
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps({"pid": os.getpid(), "desde_utc": HR.iso(int(time.time() * 1000))}) + "\n")
            return True
        return False

    def latir(self) -> None:
        try:
            os.utime(self.ruta)
        except OSError:
            pass

    def soltar(self) -> None:
        try:
            os.remove(self.ruta)
        except OSError:
            pass


def inicio_s(cfg: Config, intervalo: str, ahora_s: int, desde: dt.date | None) -> int:
    if desde is not None:
        return D.a_s(desde)
    v = cfg.inicio[intervalo]
    if isinstance(v, int):
        return D.a_s(dt.datetime.fromtimestamp(ahora_s, tz=dt.timezone.utc).date() - dt.timedelta(days=v))
    return D.a_s(dt.date.fromisoformat(v))


def cota_inicial_s(cfg: Config, intervalo: str, ahora_s: int, desde: dt.date | None) -> int:
    """Limite inferior de la comprobacion de la cola: la fecha inicial configurada. Con una ventana relativa (dias) la
    fecha inicial avanza con el reloj; se le resta un dia de margen para no perder el principio de una carga inicial
    hecha el dia anterior (a lo sumo se publica un dia mas de historia, nunca un duplicado)."""
    cota = inicio_s(cfg, intervalo, ahora_s, desde)
    if desde is None and isinstance(cfg.inicio[intervalo], int):
        cota -= 86400
    return cota


def barras_cerradas(term, simbolo: str, info: dict, intervalo: str, regla: HR.Regla, desde_s: int, ahora_s: int) -> dict:
    """Velas cerradas de MT5 con apertura UTC en [desde_s, ...) y cierre <= ahora_s, en orden. Arrays numpy."""
    periodo, paso = INTERVALOS[intervalo], PASO_S[intervalo]
    ini = dt.datetime.fromtimestamp(desde_s, tz=dt.timezone.utc).date()
    fin = dt.datetime.fromtimestamp(ahora_s, tz=dt.timezone.utc).date() + dt.timedelta(days=1)
    partes = [D.bajar_trozo(term, simbolo, periodo, a, b, regla, info)[0]
              for a, b in D.trozos(ini, fin, D.PERIODOS[periodo]["trozo"])]
    cols = ("ts_utc_ms", "open", "high", "low", "close", "tick_volume")
    out = {c: np.concatenate([p.column(c).to_numpy() for p in partes]) if partes else np.zeros(0) for c in cols}
    ts = out["ts_utc_ms"].astype(np.int64)
    ok = (ts >= desde_s * 1000) & (ts + paso * 1000 <= ahora_s * 1000)  # nunca una vela abierta
    out = {c: v[ok] for c, v in out.items()}
    out["ts_utc_ms"] = out["ts_utc_ms"].astype(np.int64)
    if out["ts_utc_ms"].size > 1 and not np.all(np.diff(out["ts_utc_ms"]) > 0):
        raise D.ErrorFormato(f"{simbolo} {intervalo}: velas fuera de orden o repetidas")
    return out


def objeto(cfg: Config, simbolo_tag: str, intervalo: str, b: dict, i: int) -> tuple[dict, dict, int]:
    ts_ms = int(b["ts_utc_ms"][i])
    if intervalo == "1d":
        # Fecha de la SESION (decision de la raiz): la del cierre de Nueva York de la vela. La sesion que abre el domingo a
        # las 21:00/22:00 UTC cierra el lunes a las 17:00 NY y lleva la fecha del lunes. `ts` sigue siendo la apertura
        # real en UTC; la disponibilidad (ts + 1 d) es el cierre real.
        cierre = ts_ms // 1000 + PASO_S["1d"]
        ny = cierre + int(HR.NUEVA_YORK.desfase(np.array([cierre]))[0])
        fecha = dt.datetime.fromtimestamp(ny, tz=dt.timezone.utc).strftime("%Y-%m-%d")
    else:
        fecha = dt.datetime.fromtimestamp(ts_ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    obj = {"open": float(b["open"][i]), "high": float(b["high"][i]), "low": float(b["low"][i]),
           "close": float(b["close"][i]), "volume": float(b["tick_volume"][i]), "date": fecha}
    if cfg.fuente_en_objeto:
        obj["source"] = cfg.fuente
    tags = {cfg.tag_simbolo: simbolo_tag, cfg.tag_intervalo: intervalo, cfg.tag_fuente: cfg.fuente}
    return tags, obj, ts_ms * 1_000_000


def _igual(obj_qn: dict, obj: dict) -> bool:
    return all(k in obj_qn and obj_qn[k] == obj[k] for k in ("open", "high", "low", "close", "volume"))


def serie(cfg: Config, cliente: Q.ClienteQn | None, term, simbolo: str, simbolo_tag: str, info: dict, intervalo: str,
          regla: HR.Regla, ahora_s: int, desde: dt.date | None, candado: Candado | None) -> dict:
    """Publica una serie. Con `cliente` None (simulacion) no toca qn: calcula lo que publicaria desde la fecha inicial."""
    paso = PASO_S[intervalo]
    tags_serie = {cfg.tag_simbolo: simbolo_tag, cfg.tag_intervalo: intervalo, cfg.tag_fuente: cfg.fuente}
    r = {"simbolo": simbolo_tag, "simbolo_mt5": simbolo, "intervalo": intervalo, "ultimo_qn_antes": None,
         "huecos_cola_rellenados": 0, "revisiones_detectadas": 0, "nuevas": 0, "publicadas": 0, "duplicadas": 0,
         "sin_publicar": 0, "error": None}
    ultimo = None
    if cliente is not None:
        items = cliente.latest(cfg.topic, tags_serie)
        tss = [Q.ts_ns_de(it["ts"]) for it in items if all(it.get("tags", {}).get(k) == v for k, v in tags_serie.items())]
        ultimo = max(tss) // 1_000_000 if tss else None
    r["ultimo_qn_antes"] = HR.iso(ultimo)
    if ultimo is None:
        b = barras_cerradas(term, simbolo, info, intervalo, regla, inicio_s(cfg, intervalo, ahora_s, desde), ahora_s)
        pendientes = list(range(b["ts_utc_ms"].size))
    else:
        desde_cola = ultimo // 1000 - cfg.ventana * paso - MARGEN_COLA_S
        b = barras_cerradas(term, simbolo, info, intervalo, regla, desde_cola, ahora_s)
        ts = b["ts_utc_ms"]
        cola = [i for i in np.nonzero(ts <= ultimo)[0][-(cfg.ventana + 1):]]
        if cola:
            filas = cliente.objetos(cfg.topic, tags_serie, int(ts[cola[0]]) * 1_000_000, ultimo * 1_000_000 + 1)
            en_qn = {}
            for f in filas:
                en_qn.setdefault(Q.ts_ns_de(f["ts"]) // 1_000_000, f)
            # Hueco = vela de MT5 de la cola que falta en qn y no es anterior a la fecha inicial configurada (lo anterior
            # nunca se pidio). Cubre tambien una primera ventana de carga inicial que fallo por el principio.
            cota_ms = cota_inicial_s(cfg, intervalo, ahora_s, desde) * 1000
            huecos = [i for i in cola if int(ts[i]) >= cota_ms and int(ts[i]) not in en_qn]
            r["huecos_cola_rellenados"] = len(huecos)
            r["revisiones_detectadas"] = sum(
                1 for i in cola if int(ts[i]) in en_qn and not _igual(en_qn[int(ts[i])], objeto(cfg, simbolo_tag, intervalo, b, i)[1]))
        else:
            huecos = []
        pendientes = huecos + [int(i) for i in np.nonzero(ts > ultimo)[0]]
    r["nuevas"] = len(pendientes) - r["huecos_cola_rellenados"]
    # Huecos de mercado del tramo de esta ejecucion (desde la ultima vela que qn tenia): se informan, no se rellenan.
    tramo = b["ts_utc_ms"] if ultimo is None else b["ts_utc_ms"][b["ts_utc_ms"] >= ultimo]
    r["huecos_mercado"] = D.huecos(tramo, paso)
    if b["ts_utc_ms"].size:
        r["mt5_desde_utc"], r["mt5_hasta_utc"] = HR.iso(int(b["ts_utc_ms"][0])), HR.iso(int(b["ts_utc_ms"][-1]))
    if cliente is None:
        r["sin_publicar"] = len(pendientes)
        r["simulado"] = True
        return r

    def uno(i: int) -> str:
        tags, obj, ts_ns = objeto(cfg, simbolo_tag, intervalo, b, i)
        try:
            return "duplicada" if cliente.publicar(cfg.topic, tags, obj, ts_ns).get("duplicate") else "publicada"
        except Q.ErrorQnAutorizacion:
            raise
        except (Q.ErrorQn, ValueError) as e:
            return f"error en {HR.iso(int(b['ts_utc_ms'][i]))}: {e}"

    with ThreadPoolExecutor(max_workers=max(1, cfg.hilos)) as pool:
        for k in range(0, len(pendientes), cfg.ventana):
            lote = pendientes[k:k + cfg.ventana]
            res = list(pool.map(uno, lote))
            r["publicadas"] += res.count("publicada")
            r["duplicadas"] += res.count("duplicada")
            errores = [x for x in res if x not in ("publicada", "duplicada")]
            if candado is not None:
                candado.latir()
            if errores:
                r["error"] = errores[0] + (f" (y {len(errores) - 1} mas en la ventana)" if len(errores) > 1 else "")
                r["sin_publicar"] = len(errores) + len(pendientes) - k - len(lote)
                break
    return r
