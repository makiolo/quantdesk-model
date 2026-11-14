"""Dos productos validados antes de publicar; manifiestos de intento direccionados por SHA-256."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from quantdesk import daily
from quantdesk.data import open_vendor_dataset

from descarga_lago import Cliente, leer_ventana, seleccionar_series, sha256_de, sanear
from exportar_market_history_lib import formato as F
from . import politica as P
from . import publicacion as PUB
from .datos import DIA, NUMERICAS, cobertura, ms_fecha, ns, preparar

REPO = Path(__file__).resolve().parents[2]


class BloqueoOcupado(ValueError):
    """Otro proceso conserva el bloqueo de la sesion."""


def canon(doc):
    return (json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seguro(texto, token):
    texto = sanear(str(texto), token, 100_000)
    return re.sub(r"qn_[A-Za-z0-9_.-]*", "[redactado]", texto)


def guardar(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Nunca se reemplaza un intento o un sobre ya identificado por su contenido.
    try:
        with path.open("xb") as f:
            f.write(raw)
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ValueError("colision de fichero de integridad") from None


@lru_cache(maxsize=1)
def versiones():
    if sys.version_info[:2] != (3, 12) or pd.__version__ != P.PANDAS or pa.__version__ != P.PYARROW:
        raise ValueError("versiones distintas de Python 3.12, pandas 3.1.1 y pyarrow 26.0.1 fijadas")
    dist = importlib.metadata.distribution("quantdesk")
    direct = json.loads(dist.read_text("direct_url.json"))
    instalado = direct["archive_info"]["hashes"]["sha256"]
    if instalado != P.WHEEL_SHA256 or sha256_de(str(P.WHEEL)) != P.WHEEL_SHA256:
        raise ValueError("la rueda quantdesk no coincide con el SHA-256 aprobado")
    if daily.universe() != P.UNIVERSO:
        raise ValueError("el universo de la rueda no coincide con el mapa versionado")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
                            capture_output=True, text=True).stdout.strip()
    return {"python": sys.version.split()[0], "quantdesk": dist.version, "quantdesk_wheel_sha256": instalado,
            "pandas": pd.__version__, "pyarrow": pa.__version__, "laboratorio_commit": commit,
            "exporter_version": commit + "+" + P.VERSION + "+" + P.POLITICA_FUENTES["version"]}


class Lectura:
    def __init__(self, cli, manifiesto, token):
        self.cli, self.m, self.token = cli, manifiesto, token
        self.head = None

    def cabecera(self, headers):
        v = headers.get("x-qn-head-cycle", "")
        if not re.fullmatch(r"[0-9]+", v):
            raise ValueError("x-qn-head-cycle ausente o no entero")
        h = int(v)
        if self.head is None:
            self.head = h
            self.m["cut_head_cycle"] = h
        return h

    def get(self, ruta, params, registro):
        try:
            doc, headers = self.cli.get_con_cabeceras(ruta, params, registro)
        except Exception:
            # Un error HTTP puede traer H. No se sustituye el error original si no la trae.
            if self.cli.cabeceras.get("x-qn-head-cycle", "").isdigit():
                self.cabecera(self.cli.cabeceras)
            raise
        h = self.cabecera(headers)
        if "head_cycle" in doc and (type(doc["head_cycle"]) is not int or doc["head_cycle"] != h):
            raise ValueError("head_cycle del cuerpo no coincide con x-qn-head-cycle")
        self.m["entradas"].append({"ruta": ruta, "params": params, "base": self.cli.base,
                                  "head_cycle": h, "sha256": sha(json.dumps(doc, sort_keys=True).encode()),
                                  "filas": len(doc.get("rows", doc.get("items", [])))})
        return doc


def leer(lectura, desde, sesion, m):
    ruta = "/topics/market.ohlcv.v2/latest"
    lat = lectura.get(ruta, {"interval": "1d"}, [])
    items = lat.get("items")
    if not isinstance(items, list):
        raise ValueError("latest no trae items")
    series = []
    for it in items:
        tags = it.get("tags", {})
        if tags.get("interval") == "1d" and tags.get("symbol") in P.MAPA:
            series.append({k: tags.get(k) for k in ("symbol", "interval", "source")})
    aceptadas, excluidas = seleccionar_series(series)
    if any(seguro(s["source"], lectura.token) != s["source"] for s in series):
        raise ValueError("una fuente contiene material de credencial: no se escribe")
    m["fuentes_excluidas"] = excluidas
    source = P.fuente_fx()
    faltan = []
    if not P.festivo_fx(sesion):
        for esperado in P.FX_ESPERADOS:
            symbol = "FX." + esperado
            originales = sorted({s for s, _, f in aceptadas if P.MAPA[s]["symbol"] == symbol and f == source}) or [esperado]
            presente = False
            for original in originales:
                doc = lectura.get(ruta, {"symbol": original, "interval": "1d", "source": source}, [])
                for it in doc.get("items", []):
                    tags = it.get("tags", {})
                    ts, recv = ns(it.get("ts", it.get("_ts"))), ns(it.get("recv_ts", it.get("_recv_ts")))
                    if (tags.get("symbol") == original and tags.get("source") == source and tags.get("interval") == "1d"
                            and ts == ms_fecha(sesion) * 10**6 and recv is not None
                            and recv < ms_fecha(sesion + timedelta(days=1)) * 10**6):
                        presente = True
            if not presente:
                faltan.append(symbol)
        # latest solo orienta la comprobacion: una version posterior a C o D+1
        # puede ocultar una barra valida. La ausencia la decide preparar() sobre
        # todas las versiones de objects resueltas dentro del corte H/C.
        m["comprobacion_previa"] = {"sin_confirmar_en_latest": faltan}
    # No depender del catalogo latest para encontrar la historia de los FX
    # esperados, incluidos sus alias del mapa versionado.
    aceptadas = set(aceptadas)
    aceptadas.update((s, "1d", source) for s, info in P.MAPA.items() if info["kind"] == "fx")
    fuentes = {}
    rows = []
    for symbol, interval, source in sorted(aceptadas):
        observable = P.MAPA[symbol]["symbol"]
        fuentes.setdefault(observable, set()).add(source)
        if len(fuentes[observable]) != 1:
            raise ValueError("dos fuentes para el mismo simbolo del mapa versionado")
        tags = {"symbol": symbol, "interval": interval, "source": source}

        def volcar(doc):
            lote = doc.get("rows")
            if not isinstance(lote, list):
                raise ValueError("objects no trae rows")
            for r in lote:
                if not isinstance(r, dict) or any(r.get(k) != v for k, v in tags.items()):
                    raise ValueError("objects trae tags distintos de los solicitados")
                rows.append(r)

        leer_ventana(lectura, "/objects/market.ohlcv.v2", tuple(tags.items()), desde, sesion, [], volcar)
    return rows, []


def hashes(folder):
    return {p.relative_to(folder).as_posix(): sha256_de(str(p)) for p in sorted(folder.rglob("*")) if p.is_file()}


def validar_desktop(folder, frame, sources, sesion):
    table = pq.read_table(folder / daily.OHLCV_FILE)
    if table.column_names != list(daily.OHLCV_COLUMNS) or table.num_rows != len(frame):
        raise ValueError("Parquet desktop con columnas o filas distintas")
    for field in table.schema:
        tipo = pa.string() if field.name == "symbol" else pa.int64() if field.name == "ts_ms" else pa.float64()
        if field.type != tipo or field.nullable or table[field.name].null_count:
            raise ValueError("Parquet desktop con tipos o nulos invalidos")
    if table.to_pandas().to_dict("records") != frame.to_dict("records"):
        raise ValueError("el desktop releido difiere del marco validado")
    index = json.loads((folder / "index.json").read_text(encoding="utf-8"))
    if index["schema"] != daily.OHLCV_INDEX_SCHEMA or index["market_date"] != sesion.isoformat():
        raise ValueError("indice desktop invalido")
    if {s["symbol"]: s["source"] for s in index["symbols"]} != sources:
        raise ValueError("sources del indice incompletas")
    pf = pq.ParquetFile(folder / daily.OHLCV_FILE)
    if any(pf.metadata.row_group(g).column(c).compression != "SNAPPY"
           for g in range(pf.num_row_groups) for c in range(pf.metadata.num_columns)):
        raise ValueError("el desktop exige Snappy")


@contextmanager
def bloqueo(path):
    # Bloqueo de proceso liberado por el SO incluso si se interrumpe Python.
    import msvcrt
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as f:
        if path.stat().st_size == 0:
            f.write(b"0")
            f.flush()
        f.seek(0)
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise BloqueoOcupado("otro exportador tiene el bloqueo de la sesion") from None
        try:
            yield
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


def exportar(a, bases, token, env, error_previo=None):
    sesion, desde = date.fromisoformat(a.sesion), date.fromisoformat(a.desde)
    runs = Path(a.runs)
    m = {"schema": "ti-02-diario.integridad/v1", "session": sesion.isoformat(),
         "cut": (sesion + timedelta(days=1)).isoformat() + "T00:00:00Z",
         "cut_ms": ms_fecha(sesion + timedelta(days=1)), "cut_head_cycle": None,
         "requested_from": desde.isoformat(), "politica_version": P.VERSION,
         "politica_fuentes": P.POLITICA_FUENTES, "festivos_fx": [list(d) for d in P.FESTIVOS_FX],
         "symbol_map": P.MAPA, "entradas": [], "ficheros": [], "avisos": [], "revision": a.revision,
         "unidades": {"prices": "cotizacion original, sin conversion", "mt5.volume": "tick_count",
                       "otras_fuentes.volume": "traded"}}
    cli = Cliente(bases, token, env)
    lectura = Lectura(cli, m, token)
    temporales, publicadas, padres_creados = [], [], []
    status, detail = "error", "exportacion no completada"

    def rollback():
        for p in reversed(publicadas):
            shutil.rmtree(p)
        publicadas.clear()
        for p in reversed(padres_creados):
            if p.exists() and not any(p.iterdir()):
                p.rmdir()

    def preparar_padres(p):
        faltan = []
        while not p.exists():
            faltan.append(p)
            p = p.parent
        for p in reversed(faltan):
            p.mkdir()
            padres_creados.append(p)

    def terminar(estado, detalle):
        m.update(status=estado, detail=seguro(detalle, token)[:500])
        # Ningun texto remoto o del sistema se escribe sin sanear.
        raw = canon(json.loads(seguro_json(m, token)))
        digest = sha(raw)
        manifiesto = runs / f"s{sesion:%Y%m%d}_{digest}.integridad.json"
        guardar(manifiesto, raw)
        return digest

    def salida(estado, detalle):
        detalle = seguro(detalle, token)[:500]
        runs.mkdir(parents=True, exist_ok=True)
        with (runs / f"s{sesion:%Y%m%d}.log").open("a", encoding="utf-8") as f:
            f.write(datetime.now(timezone.utc).isoformat() + " " + estado + " " + detalle + "\n")
        print("exportar_diario: " + estado + ": " + detalle)
        return {"ok": 0, "sin_mt5": 3, "error": 1}[estado]

    # La reconciliacion precede a cualquier nueva lectura: mantiene el mismo H,
    # manifiesto, ts y batch incluso si el mercado o latest ya han cambiado.
    if not error_previo:
        try:
            pendiente = PUB.cargar_pendiente(a, env)
        except Exception as e:
            error_previo = "no se puede reconciliar la publicacion pendiente: " + seguro(e, token)
        else:
            if pendiente:
                registro_path, registro, sobre, m = pendiente
                try:
                    PUB.publicar(cli, sobre, registro_path, registro, token)
                except Exception as e:
                    m["publicacion"] = PUB.detalle_manifiesto(registro_path, registro)
                    detail = "publicacion incierta, productos conservados: " + seguro(e, token)
                    terminar("error", detail)
                    return salida("error", detail)
                return salida(m["status"], "estado durable reconciliado: " + m["detail"])

    try:
        m["versiones"] = versiones()
        if error_previo:
            raise ValueError(error_previo)
        if sesion.weekday() >= 5:
            raise ValueError("sin sesión: sabado o domingo")
        rows, faltan = leer(lectura, desde, sesion, m)
        if faltan:
            status, detail = "sin_mt5", "faltan FX: " + ", ".join(faltan)
            m["faltan_fx"] = faltan
        else:
            desktop, motor, sources, limpieza = preparar(rows, lectura.head, desde, sesion)
            m["limpieza"] = limpieza
            m["coverage"] = coverage = cobertura(desktop, desde, sesion)
            if limpieza["cuarentena"]:
                m["avisos"].append("series y dias en cuarentena: ver limpieza.cuarentena")
            for c in coverage:
                if c["calendar"] is None:
                    m["avisos"].append("calendario desconocido: " + c["symbol"])
            dia = desktop[desktop.ts_ms == ms_fecha(sesion)]
            fx_presentes = set(dia[dia.symbol.str.startswith("FX.")].symbol)
            faltan = sorted({"FX." + s for s in P.FX_ESPERADOS} - fx_presentes)
            if P.festivo_fx(sesion) and not fx_presentes:
                status, detail = "ok", "festivo FX: sin sesión"
            elif faltan and not P.festivo_fx(sesion):
                status, detail = "sin_mt5", "faltan FX validos dentro del corte: " + ", ".join(faltan)
                m["faltan_fx"] = faltan
            elif desktop.empty:
                raise ValueError("no hay historia valida")
            elif not (desktop.ts_ms < ms_fecha(sesion)).any():
                raise ValueError("no hay historia anterior a D; no se publica solo la barra del dia")
            else:
                m["sources"] = sources
                identidad = {"session": sesion.isoformat(), "cut": m["cut"], "H": lectura.head,
                             "politica": P.VERSION, "fuentes": P.POLITICA_FUENTES["version"], "revision": a.revision,
                             "data_hash": F.hash_logico("ohlcv/v1", motor), "sources": sources}
                dataset_id = f"diario_s{sesion:%Y%m%d}_c{sesion + timedelta(days=1):%Y%m%d}_{sha(canon(identidad))[:8]}"
                if a.revision is not None:
                    dataset_id += f"_r{a.revision}"
                desktop_final = Path(a.raiz_desktop) / f"{sesion:%Y%m%d}"
                if a.revision is not None:
                    desktop_final /= f"revision_{a.revision}"
                desktop_final /= "ohlcv"
                motor_final = Path(a.raiz_datasets) / dataset_id
                preparar_padres(desktop_final.parent)
                preparar_padres(motor_final.parent)
                desktop_tmp = Path(tempfile.mkdtemp(prefix=".ohlcv.incompleto-", dir=desktop_final.parent))
                temporales.append(desktop_tmp)
                motor_stage = Path(tempfile.mkdtemp(prefix=".diario.incompleto-", dir=motor_final.parent))
                temporales.append(motor_stage)
                motor_tmp = motor_stage / dataset_id
                index = daily.write_ohlcv(desktop, desktop_tmp, sesion, sources=sources)
                index["coverage"] = coverage
                F.escribir_json(str(desktop_tmp / "index.json"), index)
                F.escribir_dataset(str(motor_tmp), dataset_id, "Historia diaria qn; corte UTC, sin reparaciones", "UTC",
                                   [{"table_id": "diario_ohlcv_1d", "schema": "ohlcv/v1", "frame": motor}])
                validar_desktop(desktop_tmp, desktop, sources, sesion)
                ds = open_vendor_dataset(motor_stage, dataset_id, verify=True)
                if not all(t.verified and t.row_count == len(motor) for t in ds.tables):
                    raise ValueError("el motor no verifica los hashes y las filas")
                planes = [("desktop", desktop_tmp, desktop_final), ("motor", motor_tmp, motor_final)]
                for producto, temporal, final in planes:
                    archivos = hashes(temporal)
                    if final.exists() and hashes(final) != archivos:
                        raise ValueError("corte publicado con contenido distinto; usa --revision N")
                    m["ficheros"] += [{"producto": producto, "ruta": ruta, "sha256": digest}
                                      for ruta, digest in archivos.items()]
                m["destinos"] = {"desktop": desktop_final.relative_to(Path(a.raiz_desktop)).as_posix(), "motor": dataset_id}
                # Ambas comprobaciones preceden a ambos renombrados. Un fallo revierte solo lo creado por este intento.
                for _, temporal, final in planes:
                    if final.exists():
                        if hashes(final) != hashes(temporal):
                            raise ValueError("el corte publicado cambio durante la validacion")
                    else:
                        temporal.rename(final)
                        publicadas.append(final)
                status, detail = "ok", "historia diaria validada"
    except Exception as e:
        rollback()
        status, detail = "error", seguro(e, token)
    finally:
        for p in temporales:
            if p.exists():
                shutil.rmtree(p)
        # Retira tambien los padres vacios tras errores ocurridos en la escritura temporal.
        if status == "error":
            rollback()
    validado_ns = time.time_ns()
    protegida = False
    registro_path, registro = None, None
    try:
        digest = terminar(status, detail)
        if lectura.head is not None:
            obj = {"session": sesion.isoformat(), "cut_head_cycle": lectura.head, "manifest_sha256": digest,
                   "status": status, "detail": m["detail"], "exporter_version": m.get("versiones", {}).get(
                       "exporter_version", "desconocido+" + P.VERSION), "host": seguro(socket.gethostname(), token)}
            bid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"ti02-diario|{sesion.isoformat()}|{digest}"))
            recibo = runs / f"{digest}.publish.json"
            sobre = {"tags": {"job": "ti02-diario"}, "obj": obj, "ts": validado_ns, "batch_id": bid}
            if recibo.exists():
                sobre = json.loads(recibo.read_text(encoding="utf-8"))
                if sobre["obj"] != obj or sobre["batch_id"] != bid:
                    raise ValueError("recibo de publicacion inconsistente")
            guardar(recibo, canon(sobre))
            registro_path, registro = PUB.crear_registro(a, env, sobre)
            protegida = registro["estado"] in ("incierta", "confirmada")
            PUB.publicar(cli, sobre, registro_path, registro, token)
            protegida = True
        else:
            detail += "; sin H: no se publica estado"
            status = "error"
    except Exception as e:
        protegida |= cli.publicacion_incierta or (registro is not None and registro["estado"] in ("incierta", "confirmada"))
        if not protegida:
            rollback()
        if registro is not None:
            m["publicacion"] = PUB.detalle_manifiesto(registro_path, registro)
        status, detail = "error", "fallo al registrar/publicar estado: " + seguro(e, token)
        if protegida:
            detail = "publicacion incierta, productos conservados; " + detail
        terminar(status, detail)
    return salida(status, detail)


def seguro_json(doc, token):
    # No colapsa los espacios internos de valores: solo retira material de credencial.
    def limpiar(value):
        if isinstance(value, str):
            if token:
                value = value.replace(token, "[redactado]")
            return re.sub(r"qn_[A-Za-z0-9_.-]*", "[redactado]", value)
        if isinstance(value, dict):
            return {limpiar(k): limpiar(v) for k, v in value.items()}
        if isinstance(value, (tuple, list)):
            return [limpiar(v) for v in value]
        return value
    return json.dumps(limpiar(doc), ensure_ascii=False, allow_nan=False)
