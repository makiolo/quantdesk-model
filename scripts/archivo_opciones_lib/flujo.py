"""Archivado columnar acotado por sesion; filtro original acotado por symbol.

El JSON de entrada solo vive como un dict transitorio. Se conserva canonico
en Arrow para no convertir enteros en floats ni perder campos del lago.
Las cinco sesiones previas se conservan exclusivamente como sets de simbolos.
"""
from collections import Counter, defaultdict, deque
from itertools import groupby
from pathlib import Path
import hashlib

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from descarga_opciones import TAGS, cargar_json, json_texto, sha256
from . import lector as L

BLOQUE = 4096
ESQUEMA = pa.schema([("symbol", pa.string()), ("asset_type", pa.string()),
                     ("capture_id", pa.string()), ("captured_at", pa.int64()),
                     ("instrument", pa.string()), ("payload", pa.string()), ("orden", pa.int64())])


class ExclusionesDisco:
    """Ledger potencialmente del tamano del rango, sin acumular sus filas."""
    def __init__(self, staging):
        self.ruta = Path(staging) / "exclusiones.jsonl"
        self.salida = self.ruta.open("w", encoding="utf-8", newline="\n")
        self.n = 0
        self.pequeno = []

    def agregar(self, filas):
        for r in filas:
            self.salida.write(json_texto(r) + "\n")
            self.n += 1
            if self.pequeno is not None:
                if self.n <= BLOQUE:
                    self.pequeno.append(r)
                else:
                    self.pequeno = None

    def __iter__(self):
        with self.ruta.open(encoding="utf-8") as entrada:
            for linea in entrada:
                yield cargar_json(linea)

    def __len__(self):
        return self.n

    def cerrar(self):
        self.salida.close()

    def resultado(self):
        if self.pequeno is not None:
            self.ruta.unlink()
            return self.pequeno
        return self


def guardar_informe(ruta, rep):
    """JSON canonico tambien cuando el ledger no cabe como una lista Python."""
    ruta = Path(ruta)
    temporal = ruta.with_suffix(ruta.suffix + ".part")
    with temporal.open("w", encoding="utf-8", newline="\n") as salida:
        salida.write("{")
        for i, k in enumerate(sorted(rep)):
            salida.write(("," if i else "") + json_texto(k) + ":")
            if isinstance(rep[k], ExclusionesDisco):
                salida.write("[")
                for j, fila in enumerate(rep[k]):
                    salida.write(("," if j else "") + json_texto(fila))
                salida.write("]")
            else:
                salida.write(json_texto(rep[k]))
        salida.write("}\n")
    temporal.replace(ruta)


def preparar(volcado, temporal, desde, hasta, corte, consulta_desde, sessions):
    """Valida todo el volcado y lo reparte en disco sin retener filas del rango."""
    from descarga_opciones import ESQUEMA as ESQUEMA_VOLCADO
    raiz = Path(volcado).resolve()
    m = cargar_json((raiz / "manifest.json").read_text(encoding="utf-8"))
    if m.get("schema") != ESQUEMA_VOLCADO or m.get("completo") is not True or m.get("topic") != "market.options.chain":
        raise ValueError("volcado incompleto o esquema/topic incompatible")
    if m.get("contexto_completo") is not True:
        raise ValueError("volcado sin contexto de cinco sesiones ni llegada al corte OC-03")
    if not isinstance(m.get("ficheros"), list):
        raise ValueError("manifest sin ficheros")
    vistos, combos, tipos = set(), set(), {}
    cuentas = Counter({motivo: 0 for motivo in L.DESCARTES})
    # Solo un bloque de JSONs, incluso cuando los ficheros mezclan sesiones.
    buffer = defaultdict(list)
    writers, rutas = {}, {}
    total = 0

    def vaciar():
        for d, filas in buffer.items():
            if d not in writers:
                rutas[d] = Path(temporal) / (d + ".parquet")
                writers[d] = pq.ParquetWriter(rutas[d], ESQUEMA, compression="snappy", use_dictionary=False)
            arrays = [pa.array(col, type=f.type) for col, f in zip(zip(*filas), ESQUEMA)]
            writers[d].write_table(pa.Table.from_arrays(arrays, schema=ESQUEMA))
        buffer.clear()

    try:
        for f in m["ficheros"]:
            ruta = (raiz / f["ruta"]).resolve()
            if not ruta.is_relative_to(raiz) or ruta in vistos:
                raise ValueError("ruta de volcado escapada o repetida")
            vistos.add(ruta)
            if sha256(ruta) != f["sha256"]:
                raise ValueError("SHA-256 de fichero no coincide: " + f["ruta"])
            combo = tuple(f["etiquetas"][k] for k in TAGS)
            if combo in combos:
                raise ValueError("combinacion repetida en manifest")
            combos.add(combo)
            n = 0
            with ruta.open(encoding="utf-8") as entrada:
                for linea in entrada:
                    r = cargar_json(linea)
                    n += 1
                    total += 1
                    if not isinstance(r, dict) or any(r.get(k) != f["etiquetas"][k] for k in TAGS):
                        raise ValueError("fila con tags distintos del manifiesto")
                    if r.get("capture_id") and ("date" not in r or isinstance(r["date"], str) and r["date"] >= str(L.INICIO)) and any(
                            c not in r for c in L.CONTENIDO + ("_offset",)):
                        raise ValueError("esquema ausente: faltan campos OC-03")
                    motivo = None
                    if not r.get("capture_id"):
                        motivo = "sin_capture_id"
                    else:
                        try:
                            d = L.fecha(r["date"])
                        except (ValueError, KeyError, TypeError):
                            motivo = "fila_invalida"
                        if motivo is None:
                            if d < L.INICIO:
                                motivo = "anterior_oc03"
                            elif not consulta_desde <= d <= hasta:
                                motivo = "fuera_rango_leido"
                            else:
                                motivo = L.motivo_fila(r)
                                if motivo is None:
                                    if r["captured_at"] > corte or (r["captured_at"] + 999999) // 1000000 > corte // 1000000:
                                        motivo = "posterior_corte"
                                    elif d not in sessions:
                                        motivo = "sesion_no_habil"
                    if motivo:
                        cuentas[motivo] += 1
                        continue
                    previo = tipos.setdefault(r["symbol"], r["asset_type"])
                    if previo != r["asset_type"]:
                        raise ValueError("symbol publicado con asset_type contradictorio: " + r["symbol"])
                    buffer[str(d)].append((r["symbol"], r["asset_type"], r["capture_id"], r["captured_at"],
                                           L.instrumento(r), json_texto({k: v for k, v in r.items() if k != "_tipo"}), total))
                    if sum(map(len, buffer.values())) >= BLOQUE:
                        vaciar()
            if n != f["filas"]:
                raise ValueError("numero de filas no coincide: " + f["ruta"])
        vaciar()
    finally:
        for w in writers.values():
            w.close()
    if combos != {tuple(c[k] for k in TAGS) for c in m.get("catalogo", [])}:
        raise ValueError("catalogo y ficheros no coinciden")
    return rutas, cuentas, total


class Escritor:
    """Parquet y hash logico de data_py incrementales, sin DataFrames completos."""
    def __init__(self, staging, tipo):
        from exportar_market_history_lib import formato as F
        self.tipo = tipo
        self.schema = F.esquema_arrow("custom/v1")
        self.writer = pq.ParquetWriter(Path(staging) / (tipo + ".parquet"), self.schema,
                                      compression=F.COMPRESION, use_dictionary=False, write_statistics=True)
        self.hash = hashlib.sha256(b"table:custom/v1\n")
        self.buffer = []
        self.rows = 0
        self.min_ts = self.max_ts = None

    def agregar(self, r, payload):
        ts = (L.fecha(r["date"]) - L.fecha("1970-01-01")).days * L.MS_DIA
        valores = (L.instrumento(r), "market.options.chain." + self.tipo, 1, ts,
                   json_texto(payload), (r["captured_at"] + 999999) // 1000000, 0)
        # Orden de columnas exacto del esquema custom/v1, no sort_keys.
        import json
        self.hash.update((json.dumps(dict(zip(self.schema.names, valores)), ensure_ascii=False,
                                    separators=(",", ":")) + "\n").encode("utf-8"))
        self.buffer.append(valores)
        self.rows += 1
        self.min_ts = ts if self.min_ts is None else min(ts, self.min_ts)
        self.max_ts = ts if self.max_ts is None else max(ts, self.max_ts)
        if len(self.buffer) >= BLOQUE:
            self.vaciar()

    def vaciar(self):
        if self.buffer:
            arrays = [pa.array(col, type=f.type) for col, f in zip(zip(*self.buffer), self.schema)]
            self.writer.write_table(pa.Table.from_arrays(arrays, schema=self.schema))
            self.buffer.clear()

    def cerrar(self):
        self.vaciar()
        self.writer.close()
        return {"table_id": self.tipo, "schema": "custom/v1", "path": self.tipo + ".parquet", "rows": self.rows,
                "ts_min_ms": self.min_ts, "ts_max_ms": self.max_ts, "logical_hash": "sha256:" + self.hash.hexdigest()}


def filas(tabla):
    for batch in tabla.select(["symbol", "payload"]).to_batches(max_chunksize=BLOQUE):
        yield from zip(batch.column(0).to_pylist(), batch.column(1).to_pylist())


def procesar(rutas, cuentas, total, desde, hasta, consulta_desde, sessions, staging, observador=None):
    anteriores = deque(maxlen=5)
    universo = set(L.OBLIGATORIOS)
    presentes, decisiones, sin_valida = {}, [], []
    ledger = ExclusionesDisco(staging)
    escritores = [Escritor(staging, t) for t in ("opciones_cruda", "opciones_limpia")]
    max_filas = max_grupo = 0
    previas = 0
    try:
        for d in sorted(sessions & set(L.dias(consulta_desde, hasta))):
            tabla = pq.read_table(rutas[str(d)]) if str(d) in rutas else pa.Table.from_batches([], schema=ESQUEMA)
            max_filas = max(max_filas, len(tabla))
            if observador:
                observador(str(d), len(tabla), tuple((str(p), frozenset(s)) for p, s in anteriores))
            caps = defaultdict(lambda: {"symbols": set(), "max": 0, "rows": 0})
            for batch in tabla.select(["symbol", "asset_type", "capture_id", "captured_at"]).to_batches(max_chunksize=BLOQUE):
                for s, t, c, ns in zip(*(col.to_pylist() for col in batch.columns)):
                    caps[c]["symbols"].add((s, t))
                    caps[c]["max"] = max(caps[c]["max"], ns)
                    caps[c]["rows"] += 1
            if len(tabla):
                del batch
            observados = set().union(*(c["symbols"] for c in caps.values()))
            universo |= observados
            esperado = set(L.OBLIGATORIOS) | observados
            for _, symbols in anteriores:
                esperado |= symbols
            candidatos = [{"capture_id": cap, "subyacentes": len(c["symbols"]), "esperados": len(esperado),
                           "cobertura": len(c["symbols"]) / len(esperado),
                           "valida": len(c["symbols"]) * 100 >= len(esperado) * 95,
                           "captured_at_max_ns": c["max"], "filas": c["rows"]} for cap, c in sorted(caps.items())]
            validos = [c for c in candidatos if c["valida"]]
            elegido = max(validos, key=lambda c: (c["subyacentes"], c["captured_at_max_ns"], c["capture_id"])) if validos else None
            if d >= desde:
                if consulta_desde > L.INICIO and previas < 5:
                    raise ValueError("contexto insuficiente al corte: hacen falta cinco sesiones previas o llegar a OC-03")
                decisiones.append({"sesion": str(d), "capture_id": elegido["capture_id"] if elegido else None,
                                   "motivo": "mas subyacentes; empate: captured_at max, luego capture_id" if elegido else "sin captura valida (ninguna >=95% o sin datos)",
                                   "universo_esperado": [dict(symbol=s, asset_type=t) for s, t in sorted(esperado)],
                                   "sesiones_contexto": [str(p) for p, _ in anteriores], "candidatas": candidatos})
                presentes[str(d)] = set()
                if not elegido:
                    sin_valida.append(str(d))
                    cuentas["sin_captura_valida"] += len(tabla)
                else:
                    seleccion = tabla.filter(pc.equal(tabla["capture_id"], elegido["capture_id"]))
                    cuentas["captura_no_elegida"] += len(tabla) - len(seleccion)
                    del tabla
                    tabla = seleccion.sort_by([("instrument", "ascending"), ("orden", "ascending")])
                    del seleccion
                    # Toda la logica de limpieza es independiente entre symbols.
                    for symbol, grupo in groupby(filas(tabla), key=lambda p: p[0]):
                        unicas = {}
                        for _, payload in grupo:
                            r = cargar_json(payload)
                            r["_tipo"] = "C" if r["opt_type"].lower() == "call" else "P"
                            clave = L.identidad(r)
                            if clave in unicas:
                                if any(r.get(c) != unicas[clave].get(c) for c in L.CONTENIDO):
                                    raise ValueError("duplicado con distinto contenido: " + " | ".join(clave))
                                cuentas["duplicado_exacto"] += 1
                                if r["_offset"] < unicas[clave]["_offset"]:
                                    unicas[clave] = r
                            else:
                                unicas[clave] = r
                        raw = [unicas[k] for k in sorted(unicas)]
                        max_grupo = max(max_grupo, len(raw))
                        for r in raw:
                            presentes[str(d)].add((r["symbol"], r["asset_type"]))
                            escritores[0].agregar(r, {k: v for k, v in r.items() if k != "_tipo"})
                        limpia, excluidas = L.limpiar(raw)
                        for r, payload in limpia:
                            escritores[1].agregar(r, payload)
                        ledger.agregar(excluidas)
                        del raw, limpia, excluidas, unicas
                # Un row group nunca mezcla sesiones, tampoco en fixtures.
                for w in escritores:
                    w.vaciar()
            else:
                cuentas["solo_contexto"] += len(tabla)
                if observados:
                    previas += 1
            del tabla
            if observados:
                anteriores.append((d, observados))
        if consulta_desde > L.INICIO and previas < 5:
            raise ValueError("contexto insuficiente al corte: hacen falta cinco sesiones previas o llegar a OC-03")
    finally:
        entradas = [w.cerrar() for w in escritores]
        ledger.cerrar()
    assert total == escritores[0].rows + sum(cuentas.values())
    rep = {"capturas": decisiones, "sesiones_sin_captura_valida": sin_valida,
           "descartes_lector": dict(cuentas), "motivos_cerrados_lector": list(L.DESCARTES),
           "huecos_por_subyacente": [{"symbol": s, "asset_type": t, "sesiones_sin_datos": [str(d) for d in sorted(sessions)
                                    if desde <= d <= hasta and (s, t) not in presentes.get(str(d), set())]} for s, t in sorted(universo)],
           "universo_huecos": "union de subyacentes OC-03 leidos hasta corte + siete obligatorios; datos de captura elegida",
           "regla_universo_captura": "union de sesion y 5 sesiones anteriores CON datos + siete obligatorios; umbral inclusivo 95%"}
    return entradas, rep, ledger.resultado(), {"max_filas_sesion": max_filas, "max_filas_grupo": max_grupo,
                                                                                  "max_sesiones_filas_simultaneas": 1, "contexto_max_sesiones": 5}
