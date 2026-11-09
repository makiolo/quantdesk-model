"""Cliente REST de qn para el publicador MT5 (solo biblioteca estandar).

Contrato (investigacion de la raiz, quantdesk-backend/market_scrapper/qn_sink.py y qn-server/README.md):
- `POST {base}/api/v1/topics/{topic}/publish?env=<env>&wait=accepted`, `Authorization: Bearer <token>`, un objeto por
  POST: `{"tags":{...},"obj":{...},"ts":<ns>,"batch_id":<uuid>}`. Respuesta `{batch_id, copies, recv_ts, duplicate, seq,
  durable}`.
- `batch_id` = uuid5(espacio fijo de qn_sink.py, JSON canonico de {topic, tags, obj, ts}): el mismo contenido da el mismo
  id en cualquier ejecucion, y qn lo trata como duplicado (7 dias de memoria); el mismo id con otro contenido es 409.
- `GET {base}/api/v1/topics/{topic}/latest?env&<tag>=<valor>...` -> `{"items":[{"tags","ts","recv_ts","batch_id","obj"}]}`.
- `GET {base}/api/v1/objects/{topic}?env&<tags>&from=<ns>&to=<ns>&limit` -> `{"columns":[...],"rows":[{...}]}`
  (`from` incluido, `to` excluido).
- `GET {base}/api/v1/topics/{topic}/schema?env` -> `{"tags":[...], "schema":{...}}`.

Reintentos: solo en 5xx y errores de red, rotando entre replicas (turno rotatorio por peticion) y esperando lo que diga
`Retry-After` (con un tope). Una replica que falla en la red pasa 60 s en cuarentena (al final del turno). 401/403 paran la ejecucion; cualquier otro 4xx para la serie. Conexiones persistentes por hilo
y replica (HTTP/1.1). El token solo viaja en la cabecera `Authorization`: nunca en la URL ni en un mensaje.
"""
from __future__ import annotations

import collections
import datetime as dt
import http.client
import itertools
import json
import threading
import time
import urllib.parse
import uuid

BATCH_NS = uuid.UUID("5d0f2a52-6b1e-4f55-9a63-1c6c2c8e1a01")  # el de qn_sink.py del backend


class ErrorQn(RuntimeError):
    pass


class ErrorQnPermanente(ErrorQn):
    """4xx: reintentar no lo arregla (contenido, conflicto de batch_id, topic)."""

    def __init__(self, estado: int, detalle: str) -> None:
        super().__init__(f"HTTP {estado} {detalle}")
        self.estado = estado


class ErrorQnAutorizacion(ErrorQnPermanente):
    """401/403: el token no vale o no tiene permiso; se para toda la ejecucion."""


class ErrorQnAgotado(ErrorQn):
    """Ninguna replica respondio bien tras los reintentos."""


def codificar(topic: str, tags: dict, obj: dict, ts_ns: int) -> tuple[bytes, str]:
    """Cuerpo del POST y su batch_id determinista (mismo algoritmo que qn_sink.encode_item)."""
    for nombre, valor in tags.items():
        if not isinstance(valor, str) or not valor or len(valor.encode("utf-8")) > 256:
            raise ValueError(f"tag {nombre} invalido: {valor!r}")
    cuerpo = {"tags": tags, "obj": obj, "ts": int(ts_ns)}
    canonico = json.dumps({"topic": topic, **cuerpo}, sort_keys=True, separators=(",", ":"), allow_nan=False)
    cuerpo["batch_id"] = str(uuid.uuid5(BATCH_NS, canonico))
    return json.dumps(cuerpo, allow_nan=False).encode("utf-8"), cuerpo["batch_id"]


class ClienteQn:
    def __init__(self, urls: list[str], token: str, env: str = "main", timeout: float = 15.0, espera_max_s: float = 30.0,
                 dormir=time.sleep, cuarentena_s: float = 60.0) -> None:
        if not urls:
            raise ValueError("faltan las URL de qn (QN_URLS)")
        self.urls = [u.rstrip("/") for u in urls]
        self.cuarentena_s, self._cuarentena = cuarentena_s, {}
        self._token, self.env, self.timeout, self.espera_max_s, self._dormir = token, env, timeout, espera_max_s, dormir
        self._local = threading.local()
        self._turno = itertools.count()
        self._cerrojo = threading.Lock()
        self.estadisticas = collections.Counter()

    def __repr__(self) -> str:
        return f"ClienteQn({len(self.urls)} replicas, env={self.env})"

    def _contar(self, clave: str) -> None:
        with self._cerrojo:
            self.estadisticas[clave] += 1

    def _conexion(self, base: str):
        conns = getattr(self._local, "conns", None)
        if conns is None:
            conns = self._local.conns = {}
        c = conns.get(base)
        if c is None:
            p = urllib.parse.urlsplit(base)
            clase = http.client.HTTPSConnection if p.scheme == "https" else http.client.HTTPConnection
            c = conns[base] = clase(p.netloc, timeout=self.timeout)
        return c

    def _cerrar(self, base: str) -> None:
        c = getattr(self._local, "conns", {}).pop(base, None)
        if c is not None:
            c.close()

    def _una(self, base: str, metodo: str, ruta: str, cuerpo: bytes | None):
        prefijo = urllib.parse.urlsplit(base).path
        c = self._conexion(base)
        cab = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
        if cuerpo is not None:
            cab["Content-Type"] = "application/json"
        c.request(metodo, prefijo + ruta, body=cuerpo, headers=cab)
        r = c.getresponse()
        datos = r.read()
        if r.will_close:
            self._cerrar(base)
        return r.status, r.getheader("Retry-After"), datos

    def _orden(self) -> list[str]:
        """Replicas en turno rotatorio; las que estan en cuarentena por un fallo de red van al final."""
        with self._cerrojo:
            inicio = next(self._turno)
            ahora = time.monotonic()
            rot = [self.urls[(inicio + k) % len(self.urls)] for k in range(len(self.urls))]
            sanas = [u for u in rot if self._cuarentena.get(u, 0.0) <= ahora]
        return sanas + [u for u in rot if u not in sanas]

    def peticion(self, metodo: str, ruta: str, cuerpo: bytes | None = None) -> dict:
        orden = self._orden()
        ultimo = None
        for intento in range(2 * len(orden)):
            base = orden[intento % len(orden)]
            try:
                estado, retry_after, datos = self._una(base, metodo, ruta, cuerpo)
            except (OSError, http.client.HTTPException) as e:
                self._cerrar(base)
                self._contar("fallos_red")
                with self._cerrojo:  # una replica que no responde se deja de lado un rato (conectar cuesta segundos)
                    self._cuarentena[base] = time.monotonic() + self.cuarentena_s
                ultimo = f"{type(e).__name__} en una replica"
                continue
            self._contar(f"http_{estado}")
            if estado >= 500:
                ultimo = f"HTTP {estado}"
                try:
                    espera = float(retry_after) if retry_after else 1.0
                except ValueError:
                    espera = 1.0
                self._dormir(min(max(espera, 0.0), self.espera_max_s))
                continue
            detalle = datos[:200].decode("utf-8", "replace")
            if estado in (401, 403):
                raise ErrorQnAutorizacion(estado, detalle)
            if estado >= 400:
                raise ErrorQnPermanente(estado, detalle)
            return json.loads(datos or b"{}")
        raise ErrorQnAgotado(f"ninguna replica de qn respondio bien: {ultimo}")

    def _q(self, params: dict) -> str:
        return urllib.parse.urlencode({"env": self.env, **params})

    def publicar(self, topic: str, tags: dict, obj: dict, ts_ns: int) -> dict:
        cuerpo, _ = codificar(topic, tags, obj, ts_ns)
        return self.peticion("POST", f"/api/v1/topics/{topic}/publish?{self._q({'wait': 'accepted'})}", cuerpo)

    def latest(self, topic: str, tags: dict) -> list[dict]:
        return self.peticion("GET", f"/api/v1/topics/{topic}/latest?{self._q(tags)}").get("items", [])

    def objetos(self, topic: str, tags: dict, desde_ns: int, hasta_ns: int, limite: int = 100_000) -> list[dict]:
        q = self._q({**tags, "from": int(desde_ns), "to": int(hasta_ns), "limit": int(limite)})
        return self.peticion("GET", f"/api/v1/objects/{topic}?{q}").get("rows", [])

    def esquema(self, topic: str) -> dict:
        return self.peticion("GET", f"/api/v1/topics/{topic}/schema?{self._q({})}")


def ts_ns_de(valor) -> int:
    """`ts` de una fila de qn: ns enteros o RFC 3339 con zona (la REST puede dar cualquiera de los dos)."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return int(valor)
    txt = str(valor).replace("Z", "+00:00")
    frac = 0
    if "." in txt:
        base, resto = txt.split(".", 1)
        digitos = "".join(itertools.takewhile(str.isdigit, resto))
        zona = resto[len(digitos):]
        frac = int((digitos + "000000000")[:9])
        txt = base + zona
    return int(dt.datetime.fromisoformat(txt).timestamp()) * 1_000_000_000 + frac
