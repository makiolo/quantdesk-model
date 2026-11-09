"""Descarga incremental y reanudable de velas y ticks de MT5 a parquet, con manifest determinista.

Unidad de trabajo: el TROZO, un intervalo UTC de un simbolo y periodo (mes para 1 m y 5 m, ano para 1 h y 1 d, dia para
ticks; el ultimo se corta en `hasta`). Un tick entra si su marca UTC esta en [inicio, fin); una vela, si su CIERRE UTC
(apertura + periodo) esta en (inicio, fin]: asi solo entran velas cerradas en `hasta` y ninguna queda partida entre dos
trozos (la vela diaria del dia D del servidor abre el D-1 a las 21:00/22:00 UTC). Cada trozo se guarda, ya convertido a UTC, en la cache
`<data>/_trozos/<broker>/<regla>/<simbolo>/<periodo>/<inicio>_<fin>.parquet` con un `.json` al lado (filas y SHA-256),
escritos de forma atomica. Reanudar = volver a lanzar la misma orden: los trozos con `.json` valido no se piden otra vez.
Incremental = una descarga posterior con otro `hasta` reutiliza los trozos cerrados que ya estan en la cache. `--refrescar`
los vuelve a pedir todos (para comprobar que dos descargas del mismo rango dan los mismos bytes).

Consolidacion: `<salida>/<simbolo>__<periodo>.parquet` (trozos en orden, un grupo de filas por trozo) y `manifest.json` con
SHA-256 por fichero, filas, rangos, huecos, conversion de hora y procedencia. Ni el manifest ni los parquet llevan marcas de
la ejecucion: dos descargas del mismo rango dan los mismos bytes y el mismo `hash_conjunto`. Lo que depende de la ejecucion
(duracion, trozos reutilizados, deteccion en vivo) va al registro de `runs/`.

Peticion al terminal: los argumentos de `copy_rates_range`/`copy_ticks_range` son segundos en la hora del servidor; se pide
[inicio, fin) convertido con la regla y ampliado 6 h por cada lado (mas que cualquier desfase), y despues se filtra en UTC.
Asi el resultado no depende de si el terminal interpreta las fechas como UTC o como hora del servidor.

Precios: las velas de MT5 se construyen con el Bid (simbolos con `chart_mode` = BID: FX, CFD) o con el Last (`chart_mode` =
LAST: bolsa). Se guardan tal cual en open/high/low/close y se declara `precio_velas`. `spread_puntos` es el campo
`spread` de MqlRates (MetaQuotes no documenta si es el minimo, el de apertura o otro de la barra: se trata como indicativo);
`spread` = spread_puntos * point; `ask_close_est` = close + spread y `mid_close_est` = close + spread / 2 son estimaciones
(nulas si las velas son de Last). En ticks hay bid, ask y last reales, y `mid` = (bid + ask) / 2 y `spread` = ask - bid
(nulos si falta un lado).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from . import calendarios as CAL
from . import hora as HR
from . import lectura as LT

FORMATO = "quantdesk-lab.mt5-crudo/v1"
PERIODOS = {
    "d1": {"tf": "TIMEFRAME_D1", "paso": 86400, "trozo": "anio"},
    "h1": {"tf": "TIMEFRAME_H1", "paso": 3600, "trozo": "anio"},
    "m5": {"tf": "TIMEFRAME_M5", "paso": 300, "trozo": "mes"},
    "m1": {"tf": "TIMEFRAME_M1", "paso": 60, "trozo": "mes"},
    "ticks": {"tf": None, "paso": None, "trozo": "dia"},
}
CAMPOS_VELAS = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")  # MqlRates
CAMPOS_TICKS = ("time", "bid", "ask", "last", "volume", "time_msc", "flags", "volume_real")  # MqlTick
MARGEN_S = 6 * 3600
FILAS_POR_GRUPO = 1_000_000

ESQUEMA_VELAS = pa.schema([
    ("time_servidor", pa.int64()), ("ts_utc_ms", pa.int64()), ("desfase_s", pa.int32()),
    ("open", pa.float64()), ("high", pa.float64()), ("low", pa.float64()), ("close", pa.float64()),
    ("tick_volume", pa.int64()), ("real_volume", pa.int64()), ("spread_puntos", pa.int32()), ("spread", pa.float64()),
    ("ask_close_est", pa.float64()), ("mid_close_est", pa.float64()),
])
ESQUEMA_TICKS = pa.schema([
    ("time_msc_servidor", pa.int64()), ("ts_utc_ms", pa.int64()), ("desfase_s", pa.int32()),
    ("bid", pa.float64()), ("ask", pa.float64()), ("last", pa.float64()), ("mid", pa.float64()), ("spread", pa.float64()),
    ("volume", pa.int64()), ("volume_real", pa.float64()), ("flags", pa.int64()),
])


class ErrorTerminal(RuntimeError):
    """El terminal devolvio un error en una consulta. `codigo`: el de `last_error()` (None si no se conoce)."""

    def __init__(self, mensaje: str, codigo: int | None = None) -> None:
        super().__init__(mensaje)
        self.codigo = codigo


class ErrorFormato(RuntimeError):
    """Los datos del terminal no tienen la forma esperada (campos, orden)."""


def sha256_fichero(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return "sha256:" + h.hexdigest()


def a_s(d: dt.date) -> int:
    return (d - dt.date(1970, 1, 1)).days * 86400


def trozos(desde: dt.date, hasta: dt.date, tipo: str) -> list[tuple[dt.date, dt.date]]:
    out, d = [], desde
    while d < hasta:
        if tipo == "dia":
            sig = d + dt.timedelta(days=1)
        elif tipo == "mes":
            sig = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        else:
            sig = dt.date(d.year + 1, 1, 1)
        sig = min(sig, hasta)
        out.append((d, sig))
        d = sig
    return out


def consultar(term, funcion: str, *args, **kwargs):
    """Llama a una consulta de la envoltura. None con last_error OK = sin datos (devuelve None). None con un error
    transitorio (-1 'Call failed' mientras el terminal sincroniza la historia, -10005 'IPC timeout') se reintenta con la
    politica de `lectura.REINTENTO` (por defecto 5 intentos, esperas de 1 a 8 s). Agotados, o con otro error:
    ErrorTerminal, igual que sin reintentos."""
    esperas = LT.REINTENTO["esperas_s"]
    for k in range(len(esperas) + 1):
        r = getattr(term, funcion)(*args, **kwargs)
        if r is not None:
            return r
        err = term.last_error()
        if err and err[0] == term.RES_S_OK:
            return None
        if not LT.es_transitorio(err, LT.TRANSITORIOS_DATOS) or k == len(esperas):
            primero = repr(args[0]) if args else ""
            raise ErrorTerminal(f"{funcion}({primero}, ...) fallo: {err}", err[0] if err else None)
        LT.REINTENTO["contador"][funcion] += 1
        LT.REINTENTO["dormir"](esperas[k])
    raise AssertionError("inalcanzable")


def _comprobar_campos(arr, esperados: tuple) -> None:
    nombres = tuple(arr.dtype.names or ())
    if nombres != esperados:
        raise ErrorFormato(f"campos inesperados {nombres}; se esperaba {esperados}")


def _nulos_si(valores: np.ndarray, mascara: np.ndarray) -> pa.Array:
    return pa.array(valores, type=pa.float64(), mask=mascara)


def tabla_velas(arr, regla: HR.Regla, point: float, digitos: int, precio_last: bool) -> tuple[pa.Table, dict]:
    if arr is None or len(arr) == 0:
        return ESQUEMA_VELAS.empty_table(), {"ambiguas": 0, "inexistentes": 0}
    _comprobar_campos(arr, CAMPOS_VELAS)
    arr = arr[np.argsort(arr["time"], kind="stable")]
    s = arr["time"].astype(np.int64)
    if s.size > 1 and not np.all(np.diff(s) > 0):
        raise ErrorFormato("velas con marcas de servidor repetidas")
    u, d, amb, inex = regla.servidor_a_utc(s)
    sp_p = arr["spread"].astype(np.int32)
    sp = np.round(sp_p.astype(np.float64) * float(point), digitos)
    close = arr["close"].astype(np.float64)
    nulo = np.full(s.shape, bool(precio_last))
    cols = [s, u * 1000, d.astype(np.int32), arr["open"].astype(np.float64), arr["high"].astype(np.float64),
            arr["low"].astype(np.float64), close, arr["tick_volume"].astype(np.int64), arr["real_volume"].astype(np.int64),
            sp_p, sp, _nulos_si(np.round(close + sp, digitos), nulo), _nulos_si(np.round(close + sp / 2, digitos + 1), nulo)]
    return pa.Table.from_arrays([pa.array(c) if not isinstance(c, pa.Array) else c for c in cols], schema=ESQUEMA_VELAS), \
        {"ambiguas": amb, "inexistentes": inex}


def tabla_ticks(arr, regla: HR.Regla) -> tuple[pa.Table, dict]:
    if arr is None or len(arr) == 0:
        return ESQUEMA_TICKS.empty_table(), {"ambiguas": 0, "inexistentes": 0}
    _comprobar_campos(arr, CAMPOS_TICKS)
    arr = arr[np.argsort(arr["time_msc"], kind="stable")]
    s_ms = arr["time_msc"].astype(np.int64)
    u_ms, d, amb, inex = regla.servidor_ms_a_utc_ms(s_ms)
    bid, ask = arr["bid"].astype(np.float64), arr["ask"].astype(np.float64)
    falta = (bid <= 0) | (ask <= 0)
    cols = [s_ms, u_ms, d.astype(np.int32), bid, ask, arr["last"].astype(np.float64),
            _nulos_si((bid + ask) / 2, falta), _nulos_si(ask - bid, falta),
            arr["volume"].astype(np.int64), arr["volume_real"].astype(np.float64), arr["flags"].astype(np.int64)]
    return pa.Table.from_arrays([pa.array(c) if not isinstance(c, pa.Array) else c for c in cols], schema=ESQUEMA_TICKS), \
        {"ambiguas": amb, "inexistentes": inex}


def bajar_trozo(term, simbolo: str, periodo: str, ini: dt.date, fin: dt.date, regla: HR.Regla, info: dict):
    u_ini, u_fin = a_s(ini), a_s(fin)
    paso = PERIODOS[periodo]["paso"] or 0
    s_ini, s_fin = regla.utc_a_servidor(u_ini) - MARGEN_S - paso, regla.utc_a_servidor(u_fin) + MARGEN_S
    if periodo == "ticks":
        arr = consultar(term, "copy_ticks_range", simbolo, s_ini, s_fin, term.COPY_TICKS_ALL)
        t, est = tabla_ticks(arr, regla)
    else:
        tf = getattr(term, PERIODOS[periodo]["tf"])
        arr = consultar(term, "copy_rates_range", simbolo, tf, s_ini, s_fin)
        t, est = tabla_velas(arr, regla, info["punto"], info["digitos"], info["precio_velas"] == "last")
    ts = t.column("ts_utc_ms").to_numpy()
    if periodo == "ticks":
        dentro = (ts >= u_ini * 1000) & (ts < u_fin * 1000)
    else:  # una vela es del trozo cuyo intervalo (inicio, fin] contiene su CIERRE: solo velas cerradas, ninguna partida
        cierre = ts + PERIODOS[periodo]["paso"] * 1000
        dentro = (cierre > u_ini * 1000) & (cierre <= u_fin * 1000)
    if not dentro.all():  # las ambiguas/inexistentes del margen no cuentan
        t = t.filter(pa.array(dentro))
        sub = t.column("time_msc_servidor" if periodo == "ticks" else "time_servidor").to_numpy()
        sub = sub // 1000 if periodo == "ticks" else sub
        _, _, amb, inex = regla.servidor_a_utc(sub)
        est = {"ambiguas": amb, "inexistentes": inex}
    return t, est


def _escribir_atomico_json(ruta: str, doc: dict) -> None:
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=1) + "\n")
    os.replace(tmp, ruta)


def _trozo_valido(ruta_pq: str) -> dict | None:
    try:
        with open(ruta_pq + ".json", encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return None
    if doc.get("formato") != FORMATO or not os.path.isfile(ruta_pq) or sha256_fichero(ruta_pq) != doc.get("sha256"):
        return None
    return doc


def obtener_trozo(term, cache: str, simbolo: str, fsim: str, periodo: str, ini, fin, regla, info, refrescar: bool):
    """Devuelve (ruta, doc, reutilizado). Escribe parquet y .json de forma atomica: un corte deja el trozo sin .json."""
    carpeta = os.path.join(cache, fsim, periodo)
    ruta = os.path.join(carpeta, f"{ini.isoformat()}_{fin.isoformat()}.parquet")
    if not refrescar:
        doc = _trozo_valido(ruta)
        if doc is not None:
            return ruta, doc, True
    os.makedirs(carpeta, exist_ok=True)
    if os.path.exists(ruta + ".json"):
        os.remove(ruta + ".json")
    t, est = bajar_trozo(term, simbolo, periodo, ini, fin, regla, info)
    tmp = ruta + ".tmp"
    pq.write_table(t, tmp, compression="snappy", row_group_size=FILAS_POR_GRUPO)
    os.replace(tmp, ruta)
    doc = {"formato": FORMATO, "simbolo": simbolo, "periodo": periodo, "inicio": ini.isoformat(), "fin": fin.isoformat(),
           "filas": t.num_rows, "sha256": sha256_fichero(ruta), **est}
    _escribir_atomico_json(ruta + ".json", doc)
    return ruta, doc, False


def huecos(ts_ms: np.ndarray, paso_s: int) -> dict:
    """Huecos entre velas consecutivas (se informan, no se rellenan). Fin de semana: el hueco contiene el sabado 12:00 UTC
    y dura <= 2,5 dias; ampliado (festivo junto al fin de semana) si dura mas; el resto, otros."""
    out = {"fin_de_semana": 0, "fin_de_semana_ampliado": 0, "otros": 0, "otros_pasos_faltantes": 0,
           "otros_por_tamano": {"<=5 pasos": 0, "<=60 pasos": 0, ">60 pasos": 0}, "otros_mayores": []}
    if ts_ms.size < 2:
        return out
    ini = ts_ms[:-1] + paso_s * 1000
    fin = ts_ms[1:]
    i = np.nonzero(fin > ini)[0]
    if i.size == 0:
        return out
    a, b = ini[i] // 1000, fin[i] // 1000
    dia_a = a // 86400
    sab = (dia_a + (5 - (dia_a + 3) % 7) % 7) * 86400 + 12 * 3600  # sabado 12:00 UTC de esa semana (o el siguiente)
    cubre_sabado = (a <= sab) & (b > sab)
    dur = b - a
    finde = cubre_sabado & (dur <= 2.5 * 86400)
    ampliado = cubre_sabado & ~finde & (dur <= 6 * 86400)
    otros = ~(finde | ampliado)
    out["fin_de_semana"], out["fin_de_semana_ampliado"] = int(finde.sum()), int(ampliado.sum())
    out["otros"] = int(otros.sum())
    pasos = dur[otros] // paso_s
    out["otros_pasos_faltantes"] = int(pasos.sum())
    out["otros_por_tamano"] = {"<=5 pasos": int((pasos <= 5).sum()), "<=60 pasos": int(((pasos > 5) & (pasos <= 60)).sum()),
                               ">60 pasos": int((pasos > 60).sum())}
    orden = np.argsort(-dur[otros], kind="stable")[:5]
    out["otros_mayores"] = [{"desde_utc": HR.iso(int(x) * 1000), "hasta_utc": HR.iso(int(y) * 1000), "pasos": int((y - x) // paso_s)}
                            for x, y in zip(a[otros][orden], b[otros][orden])]
    return out


def consolidar(rutas: list[str], destino: str, esquema: pa.Schema, es_ticks: bool) -> int:
    """Une los trozos en orden en un parquet (un grupo de filas por trozo). Comprueba el orden temporal entre trozos."""
    tmp, filas, ultimo = destino + ".tmp", 0, None
    with pq.ParquetWriter(tmp, esquema, compression="snappy") as w:
        for r in rutas:
            t = pq.read_table(r)
            if t.num_rows == 0:
                continue
            ts = t.column("ts_utc_ms").to_numpy()
            if np.any(np.diff(ts) < 0) or (not es_ticks and np.any(np.diff(ts) == 0)):
                raise ErrorFormato(f"{r}: marcas UTC fuera de orden o repetidas")
            if ultimo is not None and (ts[0] < ultimo or (not es_ticks and ts[0] == ultimo)):
                raise ErrorFormato(f"{r}: solapa con el trozo anterior")
            ultimo = int(ts[-1])
            w.write_table(t, row_group_size=FILAS_POR_GRUPO)
            filas += t.num_rows
    os.replace(tmp, destino)
    return filas


def hash_conjunto(manifest: dict) -> str:
    cuerpo = {k: v for k, v in manifest.items() if k != "hash_conjunto"}
    return "sha256:" + hashlib.sha256(json.dumps(cuerpo, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def descargar(term, simbolos: dict, periodos: list[str], desde: dt.date, hasta: dt.date, regla: HR.Regla, salida: str,
              cache: str, procedencia: dict, refrescar: bool = False, guarda_disco=lambda: None, aviso=print,
              escribir_texto=None) -> tuple[dict, dict]:
    """`simbolos`: simbolo -> {base, sufijo, fichero, punto, digitos, precio_velas}. Devuelve (manifest, estadisticas)."""
    parametros = {"desde": desde.isoformat(), "hasta": hasta.isoformat(), "periodos": list(periodos),
                  "simbolos": sorted(simbolos), "regla": regla.nombre}
    ruta_manifest = os.path.join(salida, "manifest.json")
    if os.path.isfile(ruta_manifest):
        with open(ruta_manifest, encoding="utf-8") as f:
            previo = json.load(f).get("parametros")
        if previo != parametros:
            raise ValueError(f"{salida} ya tiene una descarga con otros parametros ({previo}); usa otra --salida")
    os.makedirs(salida, exist_ok=True)
    est = {"trozos_pedidos": 0, "trozos_reutilizados": 0}
    ficheros = []
    for sim in sorted(simbolos):
        info = simbolos[sim]
        for per in periodos:
            p = PERIODOS[per]
            rutas, amb, inex = [], 0, 0
            for ini, fin in trozos(desde, hasta, p["trozo"]):
                guarda_disco()
                ruta, doc, reus = obtener_trozo(term, cache, sim, info["fichero"], per, ini, fin, regla, info, refrescar)
                est["trozos_reutilizados" if reus else "trozos_pedidos"] += 1
                rutas.append(ruta)
                amb += doc["ambiguas"]
                inex += doc["inexistentes"]
            nombre = f"{info['fichero']}__{per}.parquet"
            destino = os.path.join(salida, nombre)
            filas = consolidar(rutas, destino, ESQUEMA_TICKS if per == "ticks" else ESQUEMA_VELAS, per == "ticks")
            entrada = {"simbolo": sim, "base": info["base"], "sufijo": info["sufijo"], "periodo": per,
                       "precio_velas": info["precio_velas"], "trozos": len(rutas), "filas": filas,
                       "hora": {"ambiguas": amb, "inexistentes": inex}}
            if info.get("clase"):
                entrada.update(clase=info["clase"], bolsa=info.get("bolsa"))
            if filas == 0:
                os.remove(destino)
                entrada.update(fichero=None, nota="el terminal no da datos de este simbolo y periodo en el rango")
            else:
                t = pq.read_table(destino, columns=["ts_utc_ms", "desfase_s"] + ([] if per == "ticks" else ["time_servidor"]))
                ts = t.column("ts_utc_ms").to_numpy()
                entrada.update(fichero=nombre, bytes=os.path.getsize(destino), sha256=sha256_fichero(destino),
                               primera_utc=HR.iso(int(ts[0])), ultima_utc=HR.iso(int(ts[-1])))
                entrada["hora"]["desfases_h"] = sorted({int(x) / 3600 for x in np.unique(t.column("desfase_s").to_numpy())})
                if per != "ticks":
                    clase = info.get("clase")
                    if per == "d1" and clase not in (None, "forex"):  # fase C: dias sin mercado por clase, no huecos
                        dias = np.unique(t.column("time_servidor").to_numpy() // 86400)
                        entrada["huecos"] = CAL.huecos_sesiones(dias, clase, info.get("bolsa"))
                    else:
                        entrada["huecos"] = huecos(ts, p["paso"])
                    if per in ("m1", "m5", "h1") and info.get("es_fx"):  # el cierre de las 17:00 NY es del FX
                        entrada["cierre_semanal"] = HR.cierre_semanal(t.column("time_servidor").to_numpy(), p["paso"], regla.nombre)
                        if not entrada["cierre_semanal"]["coherente"]:
                            aviso(f"AVISO {sim} {per}: el cierre semanal no cuadra con la regla {regla.nombre} "
                                  f"(mejor: {entrada['cierre_semanal']['mejor']})")
            ficheros.append(entrada)
    manifest = {"formato": FORMATO, "tarea": "TI-12-MT5", "parametros": parametros, "regla_hora": regla.describir(),
                "procedencia": procedencia, "esquemas": {"velas": ESQUEMA_VELAS.names, "ticks": ESQUEMA_TICKS.names},
                "ficheros": ficheros}
    manifest["hash_conjunto"] = hash_conjunto(manifest)
    texto = json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=1) + "\n"
    if escribir_texto is not None:
        texto = escribir_texto(texto)  # guarda de secretos del CLI
    tmp = ruta_manifest + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    os.replace(tmp, ruta_manifest)
    est["coherencia_hora"] = all(e.get("cierre_semanal", {}).get("coherente", True) for e in ficheros)
    return manifest, est


def comparar(dir_a: str, dir_b: str) -> list[str]:
    """Diferencias entre dos descargas: hash_conjunto, y SHA-256 de cada fichero recalculado sobre el disco."""
    difs = []
    m = []
    for d in (dir_a, dir_b):
        with open(os.path.join(d, "manifest.json"), encoding="utf-8") as f:
            m.append(json.load(f))
        for e in m[-1]["ficheros"]:
            if e.get("fichero") and sha256_fichero(os.path.join(d, e["fichero"])) != e["sha256"]:
                difs.append(f"{d}/{e['fichero']}: el SHA-256 en disco no es el del manifest")
    if m[0]["hash_conjunto"] != m[1]["hash_conjunto"]:
        difs.append(f"hash_conjunto distinto: {m[0]['hash_conjunto']} != {m[1]['hash_conjunto']}")
    fa = {(e["simbolo"], e["periodo"]): e.get("sha256") for e in m[0]["ficheros"]}
    fb = {(e["simbolo"], e["periodo"]): e.get("sha256") for e in m[1]["ficheros"]}
    for k in sorted(set(fa) | set(fb)):
        if fa.get(k) != fb.get(k):
            difs.append(f"{k[0]} {k[1]}: {fa.get(k)} != {fb.get(k)}")
    return difs
