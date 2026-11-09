"""qn falso para el selftest: varias replicas HTTP en 127.0.0.1 que comparten un almacen y siguen el contrato supuesto
(publish con 200/duplicate/409/503 con Retry-After/401, latest, objects y schema). Fallos programables por replica y por
ts. Registra cada peticion (ruta y cabeceras) para comprobar que el token no viaja en la URL."""
from __future__ import annotations

import collections
import datetime as dt
import json
import socket
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROPIEDADES = ("open", "high", "low", "close", "volume", "date")  # el topic nuevo: `source` solo como tag
TOPIC = "prueba.ohlcv.fuentes"


def rfc3339_us(ns: int) -> str:
    s, resto = divmod(int(ns), 1_000_000_000)
    return dt.datetime.fromtimestamp(s, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + f".{resto // 1000:06d}Z"


class Almacen:
    """`latest`: "items" responde `{"items":[...]}` con ts en ns; "suelto" responde el objeto suelto (un solo conjunto de
    tags) con ts en RFC 3339 y 404 si no hay nada (las dos formas que network no ha podido descartar)."""

    def __init__(self, token: str, tags: tuple = ("symbol", "interval", "source"), propiedades: tuple = PROPIEDADES,
                 topic: str = TOPIC, latest: str = "items") -> None:
        self.token, self.tags, self.propiedades, self.topic, self.modo_latest = token, list(tags), set(propiedades), topic, latest
        self.cerrojo = threading.Lock()
        self.objetos: list[dict] = []
        self.por_id: dict[str, str] = {}
        self.recv = 0
        self.fallar_ts: set[int] = set()  # ts (ns) que reciben siempre 503
        self.fallos_503: collections.Counter = collections.Counter()  # replica -> 503 que quedan por dar
        self.peticiones: collections.Counter = collections.Counter()  # (replica, metodo)
        self.rutas: list[str] = []

    def publicados(self) -> collections.Counter:
        with self.cerrojo:
            return collections.Counter((tuple(sorted(o["tags"].items())), o["ts"]) for o in self.objetos)


def _handler(almacen: Almacen, nombre: str):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):  # silencio
            pass

        def _json(self, estado: int, doc: dict, cab: dict | None = None) -> None:
            datos = json.dumps(doc).encode()
            self.send_response(estado)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(datos)))
            for k, v in (cab or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(datos)

        def _entrada(self, metodo: str):
            u = urllib.parse.urlsplit(self.path)
            q = dict(urllib.parse.parse_qsl(u.query))
            with almacen.cerrojo:
                almacen.peticiones[(nombre, metodo)] += 1
                almacen.rutas.append(self.path)
            if self.headers.get("Authorization") != f"Bearer {almacen.token}":
                self._json(401, {"code": "unauthorized", "message": "token"})
                return None
            with almacen.cerrojo:
                if almacen.fallos_503[nombre] > 0:
                    almacen.fallos_503[nombre] -= 1
                    self._json(503, {"code": "backpressure", "retry_after_ms": 1000}, {"Retry-After": "1"})
                    return None
            return u.path, q

        def _tags(self, q: dict) -> dict:
            return {k: v for k, v in q.items() if k in almacen.tags}

        def do_GET(self):
            e = self._entrada("GET")
            if e is None:
                return
            ruta, q = e
            if not self._topic_ok(ruta):
                return
            tags = self._tags(q)
            casa = lambda o: all(o["tags"].get(k) == v for k, v in tags.items())  # noqa: E731
            if ruta.endswith("/schema"):
                self._json(200, {"env": q.get("env"), "topic": almacen.topic, "kind": "object", "version": 1,
                                 "tags": almacen.tags,
                                 "schema": {"type": "object", "properties": {p: {} for p in sorted(almacen.propiedades)},
                                            "additionalProperties": False}})
            elif ruta.endswith("/latest"):
                with almacen.cerrojo:
                    mejor: dict = {}
                    for o in almacen.objetos:
                        if casa(o):
                            k = tuple(sorted(o["tags"].items()))
                            if k not in mejor or (o["ts"], o["recv_ts"], o["batch_id"]) > (mejor[k]["ts"], mejor[k]["recv_ts"], mejor[k]["batch_id"]):
                                mejor[k] = o
                if almacen.modo_latest == "suelto":
                    if not mejor:
                        self._json(404, {"code": "not_found", "message": "sin datos"})
                        return
                    o = max(mejor.values(), key=lambda x: (x["ts"], x["recv_ts"], x["batch_id"]))
                    self._json(200, {"tags": o["tags"], "ts": rfc3339_us(o["ts"]), "recv_ts": rfc3339_us(o["recv_ts"]),
                                     "batch_id": o["batch_id"], "schema_version": 1, "obj": o["obj"]})
                    return
                items = [{"tags": o["tags"], "ts": o["ts"], "recv_ts": o["recv_ts"], "batch_id": o["batch_id"],
                          "schema_version": 1, "obj": o["obj"]} for _, o in sorted(mejor.items())]
                self._json(200, {"env": q.get("env"), "topic": almacen.topic, "kind": "object", "items": items})
            elif "/objects/" in ruta:
                desde, hasta, limite = int(q["from"]), int(q["to"]), int(q.get("limit", 1_000_000))
                with almacen.cerrojo:  # formato confirmado por network: filas por nombre de columna, marcas RFC 3339 us
                    filas = [{"_ts": rfc3339_us(o["ts"]), "_recv_ts": rfc3339_us(o["recv_ts"]), "_batch_id": o["batch_id"],
                              "_schema_version": 1, **o["tags"], **o["obj"]}
                             for o in sorted(almacen.objetos, key=lambda x: x["ts"]) if casa(o) and desde <= o["ts"] < hasta]
                if len(filas) > limite:
                    self._json(400, {"code": "invalid", "message": "limit"})
                    return
                columnas = ([{"name": "_ts", "type": "timestamp_us"}, {"name": "_recv_ts", "type": "timestamp_us"},
                             {"name": "_batch_id", "type": "string"}, {"name": "_schema_version", "type": "int64"}]
                            + [{"name": t, "type": "string"} for t in almacen.tags]
                            + [{"name": p, "type": "string" if p == "date" else "float64"} for p in sorted(almacen.propiedades)])
                self._json(200, {"head_cycle": 1, "lake_cycle": 1, "columns": columnas, "rows": filas})
            else:
                self._json(404, {"code": "not_found"})

        def _topic_ok(self, ruta: str) -> bool:
            if f"/topics/{almacen.topic}/" in ruta or ruta.endswith(f"/objects/{almacen.topic}"):
                return True
            self._json(404, {"code": "unknown_topic", "message": ruta.rsplit("/", 2)[-2]})
            return False

        def do_POST(self):
            n = int(self.headers.get("Content-Length", "0"))
            datos = self.rfile.read(n)
            e = self._entrada("POST")
            if e is None:
                return
            ruta, q = e
            if not self._topic_ok(ruta):
                return
            if not ruta.endswith("/publish") or q.get("wait") != "accepted":
                self._json(400, {"code": "bad_request"})
                return
            doc = json.loads(datos)
            tags, obj, ts, bid = doc.get("tags", {}), doc.get("obj", {}), doc.get("ts"), doc.get("batch_id")
            if set(tags) != set(almacen.tags) or not set(obj) <= almacen.propiedades or not isinstance(ts, int):
                self._json(400, {"code": "invalid", "message": "tags u objeto"})
                return
            if ts in almacen.fallar_ts:
                self._json(503, {"code": "unavailable", "retry_after_ms": 0}, {"Retry-After": "0"})
                return
            canon = json.dumps({"tags": tags, "obj": obj, "ts": ts}, sort_keys=True)
            with almacen.cerrojo:
                if bid in almacen.por_id:
                    if almacen.por_id[bid] != canon:
                        self._json(409, {"code": "conflict", "message": "batch_id con otro contenido"})
                        return
                    self._json(200, {"batch_id": bid, "copies": 1, "recv_ts": 0, "duplicate": True, "seq": None, "durable": False})
                    return
                almacen.recv += 1
                almacen.por_id[bid] = canon
                almacen.objetos.append({"tags": tags, "obj": obj, "ts": ts, "batch_id": bid, "recv_ts": almacen.recv})
                recv = almacen.recv
            self._json(200, {"batch_id": bid, "copies": 1, "recv_ts": recv, "duplicate": False, "seq": recv, "durable": False})

    return H


class Flota:
    """Replicas vivas (y opcionalmente una URL de una replica caida) sobre un mismo almacen."""

    def __init__(self, almacen: Almacen, vivas: int = 2, caida: bool = True) -> None:
        self.almacen, self.servidores = almacen, []
        self.urls = []
        if caida:
            s = socket.socket()
            s.bind(("127.0.0.1", 0))
            puerto = s.getsockname()[1]
            s.close()  # nadie escucha: conexion rechazada
            self.urls.append(f"http://127.0.0.1:{puerto}/qn")
        for k in range(vivas):
            srv = ThreadingHTTPServer(("127.0.0.1", 0), _handler(almacen, f"r{k}"))
            srv.daemon_threads = True
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            self.servidores.append(srv)
            self.urls.append(f"http://127.0.0.1:{srv.server_address[1]}/qn")

    def parar(self) -> None:
        for s in self.servidores:
            s.shutdown()
            s.server_close()
