"""Nucleo del publicador MT5 -> qn: configuracion, candado, barras cerradas de MT5, plan por serie y publicacion.

Una serie es (simbolo, intervalo) con la fuente fija (`source=mt5` por defecto). En cada ejecucion:
0. El topic es uno NUEVO con tags symbol, interval y source y sin `source` en el objeto (`--topic`, sin valor por
   defecto: lo decide el usuario).
1. `L` = `ts` de la ultima barra de la serie que qn confirma (`latest` filtrado por los tres tags). Sin nada en qn, se
   empieza en la fecha inicial del intervalo.
2. Se leen de MT5 las velas CERRADAS (apertura + intervalo <= ahora) desde un poco antes de `L` hasta ahora; la hora del
   servidor se pasa a UTC con la regla del extractor. Guarda de historia al dia: solo cuentan las cerradas que MT5
   confirma con la vela siguiente (ver `barras_cerradas`).
3. Comprobacion de la cola: de las `ventana` velas de MT5 con ts <= L se pregunta a qn cuales tiene (`/objects`). Las que
   faltan son huecos de una ejecucion anterior cortada a mitad de una ventana y se publican; las que estan pero con otro
   contenido se cuentan como revisiones y NO se republican (decision documentada en fase-b.md).
4. Se publica en orden de ts por ventanas de `ventana` barras, cada ventana en paralelo (`hilos`). La siguiente ventana
   solo empieza si la anterior entro entera; si algo falla, la serie se para. Asi los huecos solo pueden quedar dentro
   de la ultima ventana, y la siguiente ejecucion los rellena en el paso 3. No hay registro local de progreso: manda qn.
"""
from __future__ import annotations

import collections
import dataclasses
import datetime as dt
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from extractor_mt5_lib import calendarios as CAL
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
    # Topic NUEVO con tags symbol, interval y source (network: un tag no se puede anadir a market.ohlcv). El nombre lo
    # decide el usuario: no hay valor por defecto y sin el no se publica.
    topic: str | None = None
    tag_simbolo: str = "symbol"
    tag_intervalo: str = "interval"
    tag_fuente: str = "source"
    fuente: str = "mt5"
    fuente_en_objeto: bool = False  # un tag no puede llamarse como un campo: `source` solo va como tag
    # Profundidad inicial (solo cuando qn no tiene nada de la serie): fecha fija o ventana reciente en dias.
    inicio: dict = dataclasses.field(default_factory=lambda: {"1d": "2000-01-01", "1h": "2000-01-01", "5m": 30, "1m": 30})
    hilos: int = 8
    ventana: int = 64
    espera_max_s: float = 30.0
    caducidad_candado_s: int = 3 * 3600
    # Republicar las velas de la cola que qn tiene con otro contenido (por defecto solo se cuentan; fase-b.md). Se usa a
    # mano para corregir velas publicadas a medias (ISSUE-TI12-MT5-VELA-A-MEDIAS).
    republicar_revisiones: bool = False


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
    """Velas cerradas de MT5 con `ts` publicado en [desde_s, ...) y cierre <= ahora_s, en orden. Arrays numpy, mas
    `retenidas` (int): velas cerradas por la hora que la guarda de historia al dia deja para otra pasada.

    Guarda de historia al dia (2026-11-10): una vela solo se publica si MT5 devuelve tambien alguna vela que abre en su
    cierre o despues (la siguiente, aunque este en curso). Un simbolo fuera del Market Watch devuelve la historia que el
    terminal tenia guardada, sin sincronizar: el 2026-11-09 la vela diaria de ese dia salio a medias en 23 de 28 pares,
    y en todos ellos faltaba la vela siguiente. Coste: la ultima vela antes de un cierre de mercado (viernes, festivo)
    espera a que abra la siguiente sesion."""
    periodo, paso = INTERVALOS[intervalo], PASO_S[intervalo]
    ini = dt.datetime.fromtimestamp(desde_s, tz=dt.timezone.utc).date()
    # +2 dias: el trozo tiene que incluir la vela en curso (en 1d, la de la sesion siguiente abre a las 17:00 de Nueva
    # York y cierra al dia siguiente), que es la que confirma la guarda.
    fin = dt.datetime.fromtimestamp(ahora_s, tz=dt.timezone.utc).date() + dt.timedelta(days=2)
    partes = [D.bajar_trozo(term, simbolo, periodo, a, b, regla, info)[0]
              for a, b in D.trozos(ini, fin, D.PERIODOS[periodo]["trozo"])]
    cols = ("ts_utc_ms", "time_servidor", "open", "high", "low", "close", "tick_volume")
    out = {c: np.concatenate([p.column(c).to_numpy() for p in partes]) if partes else np.zeros(0) for c in cols}
    apertura = out.pop("ts_utc_ms").astype(np.int64)
    servidor = out.pop("time_servidor").astype(np.int64)
    if intervalo == "1d":
        ts, cierre = sesion_1d(servidor, regla)
    else:
        ts, cierre = apertura, apertura + paso * 1000
    # Se publica solo la vela CERRADA de verdad (en 1d, cuando el servidor pasa al dia siguiente: 17:00 de Nueva York,
    # no `ts` + 1 d). El rango inicial se aplica sobre el `ts` publicado (en 1d, la fecha de la sesion).
    cerrada = (ts >= desde_s * 1000) & (cierre <= ahora_s * 1000)
    confirmada = cierre <= (int(apertura.max()) if apertura.size else -1)  # guarda de historia al dia
    ok = cerrada & confirmada
    out = {c: v[ok] for c, v in out.items()}
    out["ts_utc_ms"], out["apertura_utc_ms"] = ts[ok], apertura[ok]
    out["retenidas"] = int(np.count_nonzero(cerrada & ~confirmada))
    if out["ts_utc_ms"].size > 1 and not np.all(np.diff(out["ts_utc_ms"]) > 0):
        raise D.ErrorFormato(f"{simbolo} {intervalo}: velas fuera de orden o repetidas")
    return out


def sesion_1d(time_servidor_s, regla: HR.Regla) -> tuple[np.ndarray, np.ndarray]:
    """1d, todas las clases (fase C): (`ts` publicado, cierre real), en ms UTC.
    - Sesion D = fecha del SERVIDOR de la apertura de la vela (este broker abre la 1d a las 00:00 del servidor, que va a
      Nueva York + 7 h); `ts` = 00:00 UTC de D (opcion b de la raiz; `date` = D).
    - Cierre = cuando el servidor pasa al dia siguiente (00:00 del servidor = 17:00 de Nueva York), en UTC con la regla.
    En FX es la regla publicada hasta ahora: D era la fecha de Nueva York del cierre de las 17:00, que es la del servidor
    (servidor = Nueva York + 7 h todo el ano), y el cierre era apertura + 1 d, que es el mismo instante salvo en una vela
    que contiene un cambio de hora (solo hay velas de domingo en la historia antigua de algunos cruces). Ver fase-c.md."""
    dia = np.asarray(time_servidor_s, dtype=np.int64) // 86400
    return dia * 86400 * 1000, regla.servidor_a_utc((dia + 1) * 86400)[0] * 1000


def objeto(cfg: Config, simbolo_tag: str, intervalo: str, b: dict, i: int) -> tuple[dict, dict, int]:
    ts_ms = int(b["ts_utc_ms"][i])  # ya es el `ts` publicado (ver sesion_1d)
    if intervalo == "1d":
        fecha = dt.datetime.fromtimestamp(ts_ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d")  # la sesion D
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
          regla: HR.Regla, ahora_s: int, desde: dt.date | None, candado: Candado | None,
          calendario: tuple = (None, None), ritmo: "Ritmo | None" = None) -> dict:
    """Publica una serie. Con `cliente` None (simulacion) no toca qn: calcula lo que publicaria desde la fecha inicial.
    `calendario` = (clase, bolsa) de la fase C: solo cambia como se clasifican los huecos de mercado de 1d. `ritmo`: topes
    de objetos por 5 min y por ejecucion (ver Ritmo); sin el, sin topes."""
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
            # Por ts, la version vigente de qn: la de mayor (recv_ts, batch_id), como `latest`.
            mejor = {}
            for f in filas:
                k = Q.ts_fila_ns(f) // 1_000_000
                clave = (Q.ts_ns_de(f.get("_recv_ts", 0)), str(f.get("_batch_id", "")))
                if k not in mejor or clave > mejor[k][0]:
                    mejor[k] = (clave, f)
            en_qn = {k: f for k, (_, f) in mejor.items()}
            # Hueco = vela de MT5 de la cola que falta en qn y no es anterior a la fecha inicial configurada (lo anterior
            # nunca se pidio). Cubre tambien una primera ventana de carga inicial que fallo por el principio.
            cota_ms = cota_inicial_s(cfg, intervalo, ahora_s, desde) * 1000
            huecos = [i for i in cola if int(ts[i]) >= cota_ms and int(ts[i]) not in en_qn]
            r["huecos_cola_rellenados"] = len(huecos)
            revisadas = [i for i in cola if int(ts[i]) in en_qn
                         and not _igual(en_qn[int(ts[i])], objeto(cfg, simbolo_tag, intervalo, b, i)[1])]
            r["revisiones_detectadas"] = len(revisadas)
            if cfg.republicar_revisiones:
                r["revisiones_a_republicar"] = len(revisadas)
                huecos = sorted(huecos + revisadas)  # en orden de ts, antes de las nuevas
        else:
            huecos = []
        pendientes = huecos + [int(i) for i in np.nonzero(ts > ultimo)[0]]
    r["nuevas"] = len(pendientes) - r["huecos_cola_rellenados"] - r.get("revisiones_a_republicar", 0)
    r["retenidas_sin_historia"] = b["retenidas"]
    # Huecos de mercado del tramo de esta ejecucion (desde la ultima vela que qn tenia): se informan, no se rellenan.
    tramo = b["ts_utc_ms"] if ultimo is None else b["ts_utc_ms"][b["ts_utc_ms"] >= ultimo]
    clase, bolsa = calendario
    if intervalo == "1d" and clase not in (None, "forex"):  # dias sin mercado por clase: no son huecos
        r["huecos_mercado"] = CAL.huecos_sesiones(tramo // 86_400_000, clase, bolsa)
    else:
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
        except (Q.ErrorQnAutorizacion, Q.ErrorQnTopicDesconocido):
            raise  # fatales: paran toda la ejecucion
        except (Q.ErrorQn, ValueError) as e:
            return f"error en {HR.iso(int(b['ts_utc_ms'][i]))}: {e}"

    ritmo = ritmo or Ritmo()
    with ThreadPoolExecutor(max_workers=max(1, cfg.hilos)) as pool:
        k = 0
        while k < len(pendientes):
            # Tope por ejecucion: se publica un prefijo en orden de `ts` y el resto queda para la siguiente pasada, que lo
            # retoma desde lo que qn confirma (no deja huecos por detras de L).
            n = ritmo.cupo(min(cfg.ventana, len(pendientes) - k))
            if n == 0:
                r["sin_publicar"] = len(pendientes) - k
                r["parada_por_tope"] = True
                break
            lote = pendientes[k:k + n]
            ritmo.esperar(len(lote))
            res = list(pool.map(uno, lote))
            ritmo.apuntar(len(lote))
            r["publicadas"] += res.count("publicada")
            r["duplicadas"] += res.count("duplicada")
            errores = [x for x in res if x not in ("publicada", "duplicada")]
            if candado is not None:
                candado.latir()
            if errores:
                r["error"] = errores[0] + (f" (y {len(errores) - 1} mas en la ventana)" if len(errores) > 1 else "")
                r["sin_publicar"] = len(errores) + len(pendientes) - k - len(lote)
                break
            k += len(lote)
    return r


class Ritmo:
    """Ritmo de publicacion, compartido por todas las series de una ejecucion (fase C; el Bento del backend aguanta unos
    180.000 objetos por sondeo de 5 min):
    - `por_5min`: como mucho N objetos enviados en cualquier ventana deslizante de 300 s; si no caben, se espera a que
      caduquen los mas antiguos (con `dormir`, inyectable).
    - `por_ejecucion`: como mucho N objetos en la ejecucion; las series siguen en la proxima pasada.
    Sin topes (por defecto) no cambia nada: la tarea diaria publica igual que antes. Cuenta todo lo que se envia, tambien
    lo que qn da por duplicado."""

    VENTANA_S = 300.0

    def __init__(self, por_5min: int | None = None, por_ejecucion: int | None = None, reloj=time.monotonic,
                 dormir=time.sleep) -> None:
        if (por_5min is not None and por_5min < 1) or (por_ejecucion is not None and por_ejecucion < 0):
            raise ValueError("los topes de ritmo tienen que ser enteros positivos")
        self.por_5min, self.por_ejecucion, self.reloj, self.dormir = por_5min, por_ejecucion, reloj, dormir
        self.enviados, self.esperado_s = 0, 0.0
        self._marcas: collections.deque = collections.deque()  # (instante, n)

    @property
    def agotado(self) -> bool:
        return self.por_ejecucion is not None and self.enviados >= self.por_ejecucion

    def cupo(self, n: int) -> int:
        if self.por_5min is not None:
            n = min(n, self.por_5min)
        if self.por_ejecucion is not None:
            n = min(n, self.por_ejecucion - self.enviados)
        return max(0, n)

    def esperar(self, n: int) -> None:
        if self.por_5min is None:
            return
        while True:
            ahora = self.reloj()
            while self._marcas and self._marcas[0][0] <= ahora - self.VENTANA_S:
                self._marcas.popleft()
            if sum(m for _, m in self._marcas) + n <= self.por_5min:
                return
            pausa = max(0.01, self._marcas[0][0] + self.VENTANA_S - ahora)
            self.esperado_s += pausa
            self.dormir(pausa)

    def apuntar(self, n: int) -> None:
        self.enviados += n
        if self.por_5min is not None:
            self._marcas.append((self.reloj(), n))

    def resumen(self) -> dict:
        return {"max_objetos_por_5min": self.por_5min, "max_objetos_por_ejecucion": self.por_ejecucion,
                "enviados": self.enviados, "esperado_s": round(self.esperado_s, 1), "tope_alcanzado": self.agotado}
