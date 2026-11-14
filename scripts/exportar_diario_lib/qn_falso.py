"""Servidor exclusivamente local de TI-02-DIARIO; datos sinteticos, sin credenciales reales."""
from __future__ import annotations

import copy
import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

FIXTURES = Path(__file__).with_name("fixtures")
TOKEN_PRUEBA = "credencial-ficticia-ti02"


def ns(value):
    if type(value) is int:
        return value
    from descarga_lago import ns_rfc3339
    return ns_rfc3339(value)


class Estado:
    def __init__(self):
        self.datos = json.loads((FIXTURES / "mercado.json").read_text(encoding="utf-8"))
        self.header = "7"
        self.codigo = 200
        self.peticion = []
        self.publicados = []
        self.respuestas = []
        self.transformar = lambda ruta, q, doc: doc


@contextmanager
def servidor(estado=None):
    estado = estado or Estado()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def responder(self, code, doc):
            raw = json.dumps(doc, allow_nan=True).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            if estado.header is not None:
                self.send_header("x-qn-head-cycle", estado.header)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            assert self.headers["Authorization"] == "Bearer " + TOKEN_PRUEBA
            assert TOKEN_PRUEBA not in self.path
            parsed = urlsplit(self.path)
            ruta = parsed.path
            q = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            estado.peticion.append((ruta, q))
            if estado.codigo != 200:
                return self.responder(estado.codigo, {"message": TOKEN_PRUEBA})
            rows = [copy.deepcopy(r) for r in estado.datos["rows"]
                    if all(r.get(k) == v for k, v in q.items() if k in ("symbol", "interval", "source"))]
            if ruta == "/qn/api/v1/topics/market.ohlcv.v2/latest":
                mejores = {}
                for row in rows:
                    key = tuple(row[k] for k in ("symbol", "interval", "source"))
                    if key not in mejores or (ns(row["_ts"]), ns(row["_recv_ts"]), row["_batch_id"]) > (
                            ns(mejores[key]["_ts"]), ns(mejores[key]["_recv_ts"]), mejores[key]["_batch_id"]):
                        mejores[key] = row
                doc = {"items": [{"tags": {k: r[k] for k in ("symbol", "interval", "source")},
                                  "ts": ns(r["_ts"]), "recv_ts": ns(r["_recv_ts"]),
                                  "batch_id": r["_batch_id"], "obj": {k: r[k] for k in (
                                      "open", "high", "low", "close", "volume")}}
                                 for _, r in sorted(mejores.items())]}
            elif ruta == "/qn/api/v1/objects/market.ohlcv.v2":
                rows = [r for r in rows if ns(q["from"]) <= ns(r["_ts"]) < ns(q["to"])]
                doc = {"head_cycle": estado.datos["head_cycle"], "rows": rows}
            else:
                return self.responder(404, {"message": "ruta no autorizada"})
            doc = estado.transformar(ruta, q, doc)
            estado.respuestas.append(doc)
            self.responder(200, doc)

        def do_POST(self):
            from jsonschema import Draft202012Validator, FormatChecker

            parsed = urlsplit(self.path)
            q = parse_qs(parsed.query)
            assert parsed.path == "/qn/api/v1/topics/ops.export.status/publish"
            assert q == {"env": ["main"], "wait": ["durable"]}
            doc = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.headers["Authorization"] == "Bearer " + TOKEN_PRUEBA
            assert doc["tags"] == {"job": "ti02-diario"}
            assert isinstance(doc["ts"], int)
            schema = json.loads((FIXTURES / "ops.export.status.json").read_text(encoding="utf-8"))["schema"]
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(doc["obj"])
            prev = next((p for p in estado.publicados if p["batch_id"] == doc["batch_id"]), None)
            if prev:
                assert prev == doc, "un batch repetido debe conservar tambien ts y objeto"
            estado.publicados.append(doc)
            self.responder(200, {"duplicate": prev is not None, "durable": True})

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}/qn", estado
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()
