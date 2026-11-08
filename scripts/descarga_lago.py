"""Volcado crudo del lago de quantdesk-network (tarea TI-02-DATA, paso 1 de 2).

Descarga `market.ohlcv`, `market.rates.quotes` y `market.performance` del entorno `QN_ENV`, todos los instrumentos que lista
`/latest`, entre `--desde` y `--hasta` (ambos incluidos, en UTC), y los deja tal como los devuelve qn en un directorio:

    <salida>/<topic>/<etiqueta=valor,...>.ndjson   una fila JSON por linea, sin transformar (mismo orden que qn)
    <salida>/manifest.json                         fecha UTC, base, entorno, rango, filas y SHA-256 de cada fichero,
                                                   esquema de cada topic y lista de peticiones (ruta y parametros)

Este script NO convierte nada: el paso 2 (`exportar_market_history.py`, con el .venv de Windows) lee este volcado. Existe
aparte porque la credencial de qn solo puede usarse en el host donde se emite y no sale de el: aqui solo hay biblioteca
estandar (Python >= 3.10, sin pandas ni pyarrow) y un unico fichero.

Variables: `QN_URLS` (bases separadas por comas, p. ej. http://192.168.1.48:8790/qn; se usa la primera), `QN_TOKEN`
(permiso de lectura sobre market.>) y `QN_ENV` (entorno, por defecto main). La credencial se lee solo de `QN_TOKEN`, viaja
solo en la cabecera Authorization y no se imprime ni se escribe en ningun fichero, error o log (todo texto se sanea antes).

Uso:

    python3 descarga_lago.py --desde 2024-10-01 --hasta 2026-11-07 --salida /ruta/lago/AAAA-MM-DD
    python3 descarga_lago.py --selftest          # sin red real: levanta un qn falso en 127.0.0.1

Comportamiento:
- Peticiones en serie, con timeout de 120 s y 3 reintentos (espera 1, 2 y 4 s) ante HTTP 5xx, 429 o fallo de red.
  HTTP 401/403 paran la ejecucion al instante con un mensaje claro (sin reintentar).
- Cada instrumento se pide por trozos de `--trozo-dias` dias (`from` inclusivo, `to` exclusivo, RFC 3339 con zona). Si qn
  rechaza un trozo por exceso de filas (`QN_QUERY_MAX_ROWS`, detalle `/limit`) se parte por la mitad hasta un dia; un dia que
  no cabe es un error: nunca se trunca.
- Reanudable e idempotente: un fichero que ya esta en `manifest.json` con el mismo SHA-256 no se vuelve a pedir; uno al que
  le falta o le cambia el hash se descarga de nuevo entero (se escribe a `.part` y se renombra al terminar). Una salida con
  otro entorno o rango se rechaza en lugar de mezclarse.
- `manifest.json` se reescribe de forma atomica tras cada fichero; `completo` solo es true si terminaron todos.

Codigos de salida: 0 ok; 1 fallo de lectura (servidor, exceso de filas, datos inconsistentes); 2 uso o entorno incorrecto;
3 credencial rechazada (401/403).
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

ESQUEMA = "ti-02-data.lago-crudo/v1"
TOPICS_DEFECTO = ("market.ohlcv", "market.rates.quotes", "market.performance")
TIMEOUT_S = 120
REINTENTOS = 3  # tras el primer intento: espera = espera_base * 2**n -> 1, 2, 4 s
ESPERA_BASE_S = 1.0
RESERVADOS = ("env", "from", "to", "limit", "tf", "time", "correct_clock", "fill", "max_staleness", "fresh")
EXIT_LECTURA, EXIT_USO, EXIT_CREDENCIAL = 1, 2, 3


class DemasiadasFilas(RuntimeError):
    """qn rechaza la consulta porque el resultado supera `QN_QUERY_MAX_ROWS` (detalle `/limit`)."""


class Parada(RuntimeError):
    """Fallo que no se reintenta y detiene toda la ejecucion (credencial rechazada)."""


def sanear(texto: str, acceso: str, maximo: int = 300) -> str:
    """Quita la credencial, colapsa espacios y acota el texto. Se aplica a todo error antes de mostrarlo o guardarlo."""
    if acceso:
        texto = texto.replace(acceso, "[redactado]")
    texto = " ".join(texto.split())
    return texto if len(texto) <= maximo else texto[:maximo] + "..."


def ts_qn(d: date) -> str:
    """Inicio del dia UTC en RFC 3339 con zona: qn rechaza from/to como YYYY-MM-DD."""
    return f"{d.isoformat()}T00:00:00Z"


def ventanas(desde: date, hasta: date, dias: int):
    """Trozos contiguos [a, b] de `dias` dias (el ultimo mas corto) que cubren desde..hasta sin solaparse."""
    d = desde
    while d <= hasta:
        e = min(d + timedelta(days=dias - 1), hasta)
        yield d, e
        d = e + timedelta(days=1)


def slug(combo: tuple) -> str:
    """Nombre de fichero de un instrumento: `k=v,k=v` con los caracteres raros sustituidos por `_`."""
    txt = ",".join(f"{k}={v}" for k, v in combo) or "_sin_etiquetas"
    return re.sub(r"[^A-Za-z0-9._=,+-]", "_", txt)


def sha256_de(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def utc_ahora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Cliente:
    """GET a `{base}/api/v1{ruta}` con reintentos. La credencial va solo en la cabecera Authorization."""

    def __init__(self, base: str, acceso: str, env: str, espera_base: float = ESPERA_BASE_S):
        self.base, self.acceso, self.env, self.espera_base = base, acceso, env, espera_base

    def get(self, ruta: str, params: dict, registro: list) -> dict:
        q = {"env": self.env, **params}
        entrada = {"ruta": f"/api/v1{ruta}", "params": {k: str(v) for k, v in q.items()}}
        registro.append(entrada)
        url = f"{self.base}/api/v1{ruta}?{urllib.parse.urlencode(q)}"
        ultimo = ""
        for intento in range(REINTENTOS + 1):
            if intento:
                entrada["intentos"] = intento + 1
                time.sleep(self.espera_base * 2 ** (intento - 1))
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.acceso}",
                                                       "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                    doc = json.load(r)
                if not isinstance(doc, dict):
                    raise ValueError("la respuesta no es un objeto JSON")
                return doc
            except urllib.error.HTTPError as e:
                crudo = e.read(4096).decode("utf-8", "replace")
                if e.code in (401, 403):
                    raise Parada(f"qn rechaza la credencial (HTTP {e.code}) en {ruta}: comprueba QN_TOKEN, que no este "
                                 f"revocado y que tenga permiso de lectura sobre market.> en el entorno {self.env}") from None
                if e.code >= 500 or e.code == 429:
                    ultimo = f"HTTP {e.code} en {ruta}: {sanear(crudo, self.acceso)}"
                    continue
                try:
                    cuerpo = json.loads(crudo)
                except ValueError:
                    cuerpo = {}
                detalles = cuerpo.get("details") or [] if isinstance(cuerpo, dict) else []
                msg = f"HTTP {e.code} en {ruta}: {sanear(crudo, self.acceso)}"
                if isinstance(cuerpo, dict) and cuerpo.get("code") == "invalid" and any(
                        isinstance(x, dict) and x.get("path") == "/limit" for x in detalles):
                    raise DemasiadasFilas(msg) from None
                raise RuntimeError(msg) from None
            except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError) as e:
                ultimo = f"{type(e).__name__} en {ruta}: {sanear(str(e), self.acceso)}"
        raise RuntimeError(f"{ultimo} (tras {REINTENTOS + 1} intentos)")


def leer_ventana(cli: Cliente, lectura: str, combo: tuple, d0: date, d1: date, registro: list, volcar) -> None:
    """Pide los dias [d0, d1]; si qn rechaza por filas parte el rango por la mitad. `volcar(doc)` recibe cada respuesta."""
    params = {**dict(combo), "from": ts_qn(d0), "to": ts_qn(d1 + timedelta(days=1))}
    try:
        doc = cli.get(lectura, params, registro)
    except DemasiadasFilas:
        if d0 == d1:
            raise RuntimeError(f"el dia {d0} supera el maximo de filas de qn; no se puede partir mas") from None
        mitad = d0 + timedelta(days=(d1 - d0).days // 2)
        leer_ventana(cli, lectura, combo, d0, mitad, registro, volcar)
        leer_ventana(cli, lectura, combo, mitad + timedelta(days=1), d1, registro, volcar)
        return
    volcar(doc)


def descargar_instrumento(cli: Cliente, lectura: str, combo: tuple, desde: date, hasta: date, dias: int,
                          destino: str) -> dict:
    """Escribe en `destino` (.part) todas las filas del instrumento y devuelve su entrada de manifest sin la ruta."""
    registro: list = []
    ciclos: dict = {"head_cycle": [], "lake_cycle": []}
    filas = 0

    def volcar(doc: dict) -> None:
        nonlocal filas
        for k in ciclos:
            if isinstance(doc.get(k), int):
                ciclos[k].append(doc[k])
        rows = doc.get("rows")
        if not isinstance(rows, list):
            raise RuntimeError("la respuesta de qn no trae la lista `rows`")
        for r in rows:
            linea = json.dumps(r, ensure_ascii=False, separators=(",", ":"))
            if cli.acceso and cli.acceso in linea:
                raise RuntimeError("una fila contiene la credencial: no se escribe")
            f.write(linea + "\n")
            filas += 1

    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        for a, b in ventanas(desde, hasta, dias):
            leer_ventana(cli, lectura, combo, a, b, registro, volcar)
    return {"etiquetas": dict(combo), "filas": filas, "peticiones": registro,
            "ciclos": {k: [min(v), max(v)] for k, v in ciclos.items() if v}}


def escribir_manifest(salida: str, m: dict, acceso: str) -> None:
    texto = json.dumps(m, ensure_ascii=False, indent=2) + "\n"
    if acceso and acceso in texto:
        raise SystemExit("no se escribe manifest.json: contiene la credencial")
    tmp = os.path.join(salida, "manifest.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    os.replace(tmp, os.path.join(salida, "manifest.json"))


def cargar_manifest(salida: str, env: str, desde: date, hasta: date) -> dict | None:
    """Manifest previo de la salida (None si no hay). Una salida de otro entorno o rango se rechaza, no se mezcla."""
    ruta = os.path.join(salida, "manifest.json")
    if not os.path.isfile(ruta):
        if os.listdir(salida):
            raise ValueError(f"{salida} no esta vacia y no tiene manifest.json de un volcado anterior")
        return None
    with open(ruta, encoding="utf-8") as f:
        m = json.load(f)
    if m.get("esquema") != ESQUEMA:
        raise ValueError(f"{ruta} no es un manifest de este script ({ESQUEMA})")
    if (m.get("env"), m.get("desde"), m.get("hasta")) != (env, desde.isoformat(), hasta.isoformat()):
        raise ValueError(f"la salida ya contiene un volcado de otro entorno o rango (env={m.get('env')}, "
                         f"{m.get('desde')}..{m.get('hasta')}); usa otra --salida")
    return m


def entrada_vigente(salida: str, previo: dict | None, topic: str, combo: tuple) -> dict | None:
    """Entrada del manifest anterior si su fichero existe y conserva el SHA-256 registrado; si no, None (se rehace)."""
    if not previo:
        return None
    for e in previo.get("topics", {}).get(topic, {}).get("ficheros", []):
        if e.get("etiquetas") == dict(combo):
            ruta = os.path.join(salida, *e["ruta"].split("/"))
            if os.path.isfile(ruta) and sha256_de(ruta) == e.get("sha256"):
                return e
    return None


def correr(a: argparse.Namespace, base: str, acceso: str, env: str) -> int:
    desde, hasta = date.fromisoformat(a.desde), date.fromisoformat(a.hasta)
    salida = os.path.abspath(a.salida)
    os.makedirs(salida, exist_ok=True)
    try:
        previo = cargar_manifest(salida, env, desde, hasta)
    except ValueError as e:
        print(f"descarga_lago: {e}", file=sys.stderr)
        return EXIT_USO
    for raiz, _, nombres in os.walk(salida):  # restos de una ejecucion cortada a medias
        for n in nombres:
            if n.endswith(".part"):
                os.remove(os.path.join(raiz, n))
    cli = Cliente(base, acceso, env, a.espera_base)
    topics_pedidos = [t.strip() for t in a.topics.split(",") if t.strip()]
    catalogo: list = []
    m = {"esquema": ESQUEMA, "fecha_utc": (previo or {}).get("fecha_utc") or utc_ahora(), "ultima_ejecucion_utc": utc_ahora(),
         "base": base, "bases": sorted({base, *(previo or {}).get("bases", [])}), "env": env,
         "desde": desde.isoformat(), "hasta": hasta.isoformat(), "trozo_dias": a.trozo_dias,
         "script_sha256": sha256_de(os.path.abspath(__file__)), "python": sys.version.split()[0],
         "completo": False, "avisos": [], "topics": {}, "peticiones_catalogo": catalogo}
    previos_t = (previo or {}).get("topics", {})
    m["topics"] = dict(previos_t)  # lo ya descargado se conserva aunque esta ejecucion se corte antes de llegar a ello
    try:
        listado = cli.get("/topics", {}, catalogo).get("topics", [])
        info = {x["topic"]: x for x in listado}
        faltan = [t for t in topics_pedidos if t not in info]
        if faltan:
            print(f"descarga_lago: topics que qn no lista: {', '.join(faltan)}", file=sys.stderr)
            return EXIT_LECTURA
        pendientes = 0
        for topic in topics_pedidos:
            kind = info[topic].get("kind")
            if kind not in ("object", "series"):
                raise RuntimeError(f"tipo de topic desconocido: {kind!r} en {topic}")
            lectura = f"/objects/{topic}" if kind == "object" else f"/series/{topic}/rows"
            esquema = cli.get(f"/topics/{topic}/schema", {}, catalogo)
            lat = cli.get(f"/topics/{topic}/latest", {}, catalogo)
            combos = sorted({tuple(sorted((it.get("tags") or {}).items())) for it in lat.get("items", [])})
            nombres = [slug(c) for c in combos]
            if len(set(nombres)) != len(nombres):
                raise RuntimeError(f"{topic}: dos instrumentos darian el mismo nombre de fichero")
            if any(k in RESERVADOS for c in combos for k, _ in c):
                raise RuntimeError(f"{topic}: una etiqueta se llama como un parametro reservado de qn")
            t_m = {"kind": kind, "lectura": lectura, "etiquetas_declaradas": esquema.get("tags") or info[topic].get("tags"),
                   "esquema": esquema, "instrumentos_listados": len(combos),
                   "ficheros": list(previos_t.get(topic, {}).get("ficheros", [])), "filas": 0}
            m["topics"][topic] = t_m
            if not combos:
                m["avisos"].append(f"{topic}: /latest no lista ningun instrumento; no se descarga nada")
            os.makedirs(os.path.join(salida, topic), exist_ok=True)
            vigentes = {json.dumps(dict(c), sort_keys=True) for c in combos}
            for e in t_m["ficheros"]:  # instrumentos que /latest ya no lista: el fichero anterior se conserva y se avisa
                if json.dumps(e["etiquetas"], sort_keys=True) not in vigentes:
                    m["avisos"].append(f"{topic}: {e['ruta']} ya no sale en /latest; se conserva del volcado anterior")
            for combo, nombre in zip(combos, nombres):
                rel = f"{topic}/{nombre}.ndjson"
                bueno = entrada_vigente(salida, previo, topic, combo)
                if bueno is not None:
                    print(f"  ya esta  {rel} ({bueno['filas']} filas)")
                    continue
                destino = os.path.join(salida, topic, nombre + ".ndjson")
                parte = destino + ".part"
                res = descargar_instrumento(cli, lectura, combo, desde, hasta, a.trozo_dias, parte)
                os.replace(parte, destino)
                res.update(ruta=rel, bytes=os.path.getsize(destino), sha256=sha256_de(destino))
                t_m["ficheros"] = [x for x in t_m["ficheros"] if x["etiquetas"] != dict(combo)] + [res]
                pendientes += 1
                print(f"  bajado   {rel} ({res['filas']} filas, {len(res['peticiones'])} peticiones)")
                t_m["filas"] = sum(x["filas"] for x in t_m["ficheros"])
                escribir_manifest(salida, m, acceso)
            t_m["ficheros"].sort(key=lambda x: x["ruta"])
            t_m["filas"] = sum(x["filas"] for x in t_m["ficheros"])
            print(f"{topic}: {len(combos)} instrumentos, {t_m['filas']} filas")
        m["completo"] = True
        escribir_manifest(salida, m, acceso)
        print(f"volcado completo en {salida} ({pendientes} ficheros descargados en esta ejecucion)")
        return 0
    except Parada as e:
        escribir_manifest(salida, m, acceso)
        print(f"descarga_lago: PARADA: {sanear(str(e), acceso, 600)}", file=sys.stderr)
        return EXIT_CREDENCIAL
    except (RuntimeError, OSError, KeyError, ValueError) as e:
        escribir_manifest(salida, m, acceso)
        print(f"descarga_lago: ERROR: {sanear(f'{type(e).__name__}: {e}', acceso, 600)}; volcado incompleto, vuelve a "
              "lanzar el mismo comando para reanudar", file=sys.stderr)
        return EXIT_LECTURA


# ---------------------------------------------------------------------------------------------------------------------
# Selftest: un qn falso en 127.0.0.1 (http.server) y el script real lanzado como subproceso.
# ---------------------------------------------------------------------------------------------------------------------

TOKEN_PRUEBA = "SECRETO-TI02-0123456789abcdef"
CATALOGO_PRUEBA = {
    "market.ohlcv": [{"interval": "1d", "symbol": "AAA"}, {"interval": "1d", "symbol": "BBB"},
                     {"interval": "1h", "symbol": "AAA"}],
    "market.rates.quotes": [{"currency": "AUD", "curve_type": "IBOR", "tenor": "10Y"}],
    "market.performance": [{"period": "D", "symbol": "EUR"}],
}


class QnFalso:
    """Estado compartido del servidor de prueba: datos sinteticos, limite de filas, fallos inyectados y registro."""

    def __init__(self, max_filas: int | None = None):
        self.max_filas = max_filas
        self.fallos: dict = {}      # (topic, simbolo) -> HTTP a devolver; "inf" en `restantes` = siempre
        self.restantes: dict = {}   # (topic, simbolo) -> cuantos fallos quedan
        self.respuesta_global: int | None = None  # HTTP fijo para todo (p. ej. 401)
        self.peticiones: list = []  # (ruta, params, tiene_autorizacion_correcta)
        self.token = TOKEN_PRUEBA

    def filas(self, topic: str, tags: dict, a: date, b: date) -> list:
        """Una fila por dia del rango [a, b) con la forma real de qn (`_ts`, `_recv_ts` en ns, campos de usuario)."""
        out, d = [], a
        semilla = sum(map(ord, "".join(sorted(tags.values()))))
        while d < b:
            ns = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()) * 10 ** 9
            base = 1.0 + (semilla % 7) * 0.1 + d.toordinal() % 11 * 0.01
            if topic == "market.ohlcv":
                cuerpo = {"open": base, "high": base + 0.02, "low": base - 0.02, "close": base + 0.005, "volume": 0.0,
                          "date": d.isoformat(), "source": "market_scraper"}
            elif topic == "market.rates.quotes":
                cuerpo = {"valuation_date": d.isoformat(), "rate": base / 10, "scraped_at_ms": ns // 10 ** 6,
                          "source": "market_scraper"}
            else:
                cuerpo = {"performance": base - 1, "date": d.isoformat(), "source": "finviz"}
            out.append({"_ts": ns, "_recv_ts": ns + 25 * 3600 * 10 ** 9, "_clock_offset_ns": None, **cuerpo})
            d += timedelta(days=1)
        return out


def servidor_falso(estado: QnFalso):
    class Manejador(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):  # silencio
            pass

        def _json(self, codigo: int, doc: dict) -> None:
            cuerpo = json.dumps(doc).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

        def do_GET(self):
            url = urllib.parse.urlparse(self.path)
            params = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
            ok = self.headers.get("Authorization") == f"Bearer {estado.token}"
            estado.peticiones.append((url.path, params, ok))
            if estado.respuesta_global is not None:
                return self._json(estado.respuesta_global, {"code": "unauthorized", "message": "token " + estado.token})
            if not ok:
                return self._json(401, {"code": "unauthorized", "message": "sin permiso"})
            partes = url.path.split("/")  # '', 'qn', 'api', 'v1', ...
            if url.path == "/qn/api/v1/topics":
                return self._json(200, {"topics": [{"topic": t, "kind": "object", "tags": sorted(c[0])}
                                                   for t, c in CATALOGO_PRUEBA.items()] +
                                  [{"topic": "market.options.chain", "kind": "object", "tags": ["symbol"]}]})
            if len(partes) == 7 and partes[4] == "topics" and partes[6] in ("schema", "latest"):
                topic = partes[5]
                combos = CATALOGO_PRUEBA.get(topic, [])
                if partes[6] == "schema":
                    return self._json(200, {"topic": topic, "tags": sorted(combos[0]) if combos else ["symbol"],
                                            "schema": {"type": "object", "properties": {"close": {"type": "number"}}}})
                return self._json(200, {"items": [{"tags": c} for c in combos]})
            if len(partes) == 6 and partes[4] == "objects":
                topic = partes[5]
                tags = {k: v for k, v in params.items() if k not in ("env", "from", "to")}
                clave = (topic, tags.get("symbol") or tags.get("currency") or "")
                if estado.restantes.get(clave, 0) > 0:
                    estado.restantes[clave] -= 1
                    return self._json(estado.fallos[clave], {"code": "unavailable", "message": "reintenta"})
                if estado.restantes.get(clave, 0) == -1:
                    return self._json(estado.fallos[clave], {"code": "internal", "message": "roto " + estado.token})
                a = date.fromisoformat(params["from"][:10])
                b = date.fromisoformat(params["to"][:10])
                assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T00:00:00Z", params["from"]), params
                assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T00:00:00Z", params["to"]), params
                filas = estado.filas(topic, tags, a, b)
                if estado.max_filas is not None and len(filas) > estado.max_filas:
                    return self._json(400, {"code": "invalid", "message": "demasiadas filas",
                                            "details": [{"path": "/limit", "message": "supera el maximo"}]})
                return self._json(200, {"head_cycle": 7, "lake_cycle": 5, "columns": [{"name": "_ts"}], "rows": filas})
            return self._json(404, {"code": "not_found", "message": "ruta"})

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def lanzar(estado_url: str, salida: str, *extra: str, token: str = TOKEN_PRUEBA):
    """Ejecuta este mismo script como subproceso contra el qn falso; devuelve (codigo, stdout, stderr)."""
    env = {k: v for k, v in os.environ.items() if not k.upper().endswith("_PROXY")}
    env.update(QN_URLS=estado_url, QN_TOKEN=token, QN_ENV="main", NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--salida", salida, "--espera-base", "0",
                        *extra], capture_output=True, text=True, encoding="utf-8", env=env, timeout=300)
    return r.returncode, r.stdout, r.stderr


def ficheros_de(salida: str) -> dict:
    out = {}
    for raiz, _, nombres in os.walk(salida):
        for n in nombres:
            ruta = os.path.join(raiz, n)
            out[os.path.relpath(ruta, salida).replace(os.sep, "/")] = ruta
    return out


def sin_credencial(salida: str, *textos: str) -> None:
    for t in textos:
        assert TOKEN_PRUEBA not in t, "la credencial aparece en la salida estandar o de error"
    for rel, ruta in ficheros_de(salida).items():
        with open(ruta, "rb") as f:
            assert TOKEN_PRUEBA.encode() not in f.read(), f"la credencial aparece en {rel}"


def n_objetos(estado: QnFalso, desde: int = 0, symbol: str | None = None) -> int:
    return sum(1 for r, p, _ in estado.peticiones[desde:]
               if "/objects/" in r and (symbol is None or p.get("symbol") == symbol))


def selftest() -> None:
    # --- piezas puras
    assert sanear("Bearer SECRETO y " + "x " * 400, "SECRETO").startswith("Bearer [redactado] y")
    assert len(sanear("a " * 500, "")) <= 303 and "SECRETO" not in sanear("SECRETO", "SECRETO")
    assert ts_qn(date(2026, 1, 5)) == "2026-01-05T00:00:00Z"
    v = list(ventanas(date(2026, 1, 1), date(2026, 3, 1), 31))
    assert v == [(date(2026, 1, 1), date(2026, 1, 31)), (date(2026, 2, 1), date(2026, 3, 1))], v
    assert list(ventanas(date(2026, 1, 1), date(2026, 1, 1), 31)) == [(date(2026, 1, 1), date(2026, 1, 1))]
    assert slug((("interval", "1d"), ("symbol", "EUR/USD"))) == "interval=1d,symbol=EUR_USD"
    assert slug(()) == "_sin_etiquetas"

    dias = date(2026, 3, 31) - date(2026, 1, 1) + timedelta(days=1)  # 90 filas por instrumento
    n_instr = sum(len(c) for c in CATALOGO_PRUEBA.values())
    comun = ("--desde", "2026-01-01", "--hasta", "2026-03-31", "--topics", ",".join(CATALOGO_PRUEBA))
    with tempfile.TemporaryDirectory() as tmp:
        # --- 1. descarga completa: ficheros, hashes, filas, formato de from/to y credencial solo en la cabecera
        estado = QnFalso()
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            s1 = os.path.join(tmp, "uno")
            cod, out, err = lanzar(url, s1, *comun, "--trozo-dias", "31")
            assert cod == 0, (cod, out, err)
            m = json.load(open(os.path.join(s1, "manifest.json"), encoding="utf-8"))
            assert m["completo"] is True and m["env"] == "main" and m["base"] == url and m["python"], m
            assert (m["desde"], m["hasta"]) == ("2026-01-01", "2026-03-31") and m["fecha_utc"].endswith("Z")
            todos = [f for t in m["topics"].values() for f in t["ficheros"]]
            assert len(todos) == n_instr and all(f["filas"] == dias.days for f in todos), todos
            for f in todos:
                ruta = os.path.join(s1, *f["ruta"].split("/"))
                assert sha256_de(ruta) == f["sha256"] and os.path.getsize(ruta) == f["bytes"]
                lineas = open(ruta, encoding="utf-8").read().splitlines()
                assert len(lineas) == f["filas"] and json.loads(lineas[0])["_ts"] > 0
                assert len(f["peticiones"]) == 3 and f["ciclos"] == {"head_cycle": [7, 7], "lake_cycle": [5, 5]}
            assert m["topics"]["market.ohlcv"]["esquema"]["schema"]["type"] == "object"
            assert any(p["ruta"] == "/api/v1/topics" for p in m["peticiones_catalogo"])
            assert all(set(p) <= {"ruta", "params", "intentos"} for f in todos for p in f["peticiones"])
            assert all(ok for _, _, ok in estado.peticiones), "toda peticion debe llevar la cabecera Authorization"
            sin_credencial(s1, out, err)
            assert "market.options.chain" not in m["topics"]  # solo los topics pedidos
            # --- 2. reanudar sobre un volcado completo: ninguna peticion de datos y manifest identico en lo esencial
            n0 = len(estado.peticiones)
            cod, out, err = lanzar(url, s1, *comun, "--trozo-dias", "31")
            assert cod == 0 and n_objetos(estado, n0) == 0, (cod, out, err)
            m2 = json.load(open(os.path.join(s1, "manifest.json"), encoding="utf-8"))
            assert [f["sha256"] for t in m2["topics"].values() for f in t["ficheros"]] == [f["sha256"] for f in todos]
            # --- 3. un fichero alterado se vuelve a bajar y recupera su hash; los demas no se piden
            victima = os.path.join(s1, "market.ohlcv", "interval=1d,symbol=BBB.ndjson")
            with open(victima, "a", encoding="utf-8") as f:
                f.write("basura\n")
            n0 = len(estado.peticiones)
            cod, out, err = lanzar(url, s1, *comun, "--trozo-dias", "31")
            assert cod == 0 and n_objetos(estado, n0, "BBB") == 3 and n_objetos(estado, n0) == 3, (cod, out)
            assert sha256_de(victima) in {f["sha256"] for f in todos}
            # --- 4. otro rango sobre la misma salida se rechaza sin tocarla
            antes = sha256_de(os.path.join(s1, "manifest.json"))
            cod, out, err = lanzar(url, s1, "--desde", "2026-02-01", "--hasta", "2026-03-31", "--trozo-dias", "31")
            assert cod == 2 and "otro entorno o rango" in err and sha256_de(os.path.join(s1, "manifest.json")) == antes
            # --- 5. una salida con otro contenido tampoco se mezcla
            ajena = os.path.join(tmp, "ajena")
            os.makedirs(ajena)
            open(os.path.join(ajena, "x.txt"), "w").write("x")
            cod, out, err = lanzar(url, ajena, *comun)
            assert cod == 2 and "no esta vacia" in err
        finally:
            srv.shutdown()
            srv.server_close()

        # --- 6. exceso de filas: se parte hasta caber y no se pierde ni duplica ninguna fila
        estado = QnFalso(max_filas=10)
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            s2 = os.path.join(tmp, "partido")
            cod, out, err = lanzar(url, s2, *comun, "--trozo-dias", "31")
            assert cod == 0, (cod, out, err)
            m = json.load(open(os.path.join(s2, "manifest.json"), encoding="utf-8"))
            todos2 = [f for t in m["topics"].values() for f in t["ficheros"]]
            assert all(f["filas"] == dias.days and len(f["peticiones"]) > 3 for f in todos2), todos2[0]["peticiones"]
            assert [f["sha256"] for f in todos2] == [f["sha256"] for f in todos], "partir no cambia el contenido"
            sin_credencial(s2, out, err)
        finally:
            srv.shutdown()
            srv.server_close()
        # --- 7. un dia que no cabe es un error, no un truncado
        estado = QnFalso(max_filas=0)
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            cod, out, err = lanzar(url, os.path.join(tmp, "dia"), *comun)
            assert cod == 1 and "no se puede partir" in err, (cod, err)
            assert json.load(open(os.path.join(tmp, "dia", "manifest.json")))["completo"] is False
        finally:
            srv.shutdown()
            srv.server_close()

        # --- 8. reintentos: 2 fallos 503 y despues responde; uno persistente agota 4 intentos y pide reanudar
        estado = QnFalso()
        estado.fallos[("market.ohlcv", "AAA")] = 503
        estado.restantes[("market.ohlcv", "AAA")] = 2
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            s3 = os.path.join(tmp, "reintento")
            cod, out, err = lanzar(url, s3, *comun, "--trozo-dias", "31")
            assert cod == 0, (cod, out, err)
            m = json.load(open(os.path.join(s3, "manifest.json"), encoding="utf-8"))
            ints = [p.get("intentos") for f in m["topics"]["market.ohlcv"]["ficheros"] for p in f["peticiones"]]
            assert 3 in ints, ints
        finally:
            srv.shutdown()
            srv.server_close()

        # --- 9. fallo persistente en un instrumento, luego reanudacion: lo ya bajado no se repite
        estado = QnFalso()
        estado.fallos[("market.ohlcv", "BBB")] = 500
        estado.restantes[("market.ohlcv", "BBB")] = -1  # siempre
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            s4 = os.path.join(tmp, "reanuda")
            cod, out, err = lanzar(url, s4, *comun, "--trozo-dias", "31")
            assert cod == 1 and "tras 4 intentos" in err and "reanudar" in err, (cod, err)
            assert "[redactado]" in err, "el eco de la credencial en el cuerpo del error debe quedar saneado"
            assert sum(1 for r, p, _ in estado.peticiones if p.get("symbol") == "BBB") == 4
            m = json.load(open(os.path.join(s4, "manifest.json"), encoding="utf-8"))
            assert m["completo"] is False
            hechos = [f["etiquetas"] for f in m["topics"]["market.ohlcv"]["ficheros"]]
            assert hechos == [{"interval": "1d", "symbol": "AAA"}], hechos
            sin_credencial(s4, out, err)
            estado.restantes[("market.ohlcv", "BBB")] = 0  # el servidor se recupera
            n0 = len(estado.peticiones)
            cod, out, err = lanzar(url, s4, *comun, "--trozo-dias", "31")
            assert cod == 0, (cod, out, err)
            assert n_objetos(estado, n0) == 3 * (n_instr - 1), "no debe repetir el instrumento ya descargado"
            m = json.load(open(os.path.join(s4, "manifest.json"), encoding="utf-8"))
            assert m["completo"] is True and sorted(
                (f["ruta"], f["sha256"]) for t in m["topics"].values() for f in t["ficheros"]) == sorted(
                (f["ruta"], f["sha256"]) for f in todos)
            assert not [r for r in ficheros_de(s4) if r.endswith(".part")]
        finally:
            srv.shutdown()
            srv.server_close()

        # --- 10. credencial rechazada: parada inmediata, un solo intento, sin credencial en ninguna salida
        estado = QnFalso()
        estado.respuesta_global = 401
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            s5 = os.path.join(tmp, "rechazo")
            cod, out, err = lanzar(url, s5, *comun)
            assert cod == 3 and "401" in err and "QN_TOKEN" in err, (cod, err)
            assert len(estado.peticiones) == 1, estado.peticiones
            sin_credencial(s5, out, err)
            # un token equivocado (el servidor devuelve 401 sin eco) tambien para
            estado.respuesta_global = None
            cod, out, err = lanzar(url, os.path.join(tmp, "mal"), *comun, token="OTRO-TOKEN-XYZ")
            assert cod == 3 and "OTRO-TOKEN-XYZ" not in out + err
        finally:
            srv.shutdown()
            srv.server_close()

        # --- 11. entorno incompleto o topic inexistente
        env = {k: v for k, v in os.environ.items() if not k.startswith("QN_")}
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--desde", "2026-01-01", "--hasta", "2026-01-02",
                            "--salida", os.path.join(tmp, "sinenv")], capture_output=True, text=True, env=env)
        assert r.returncode == 2 and "QN_URLS" in r.stderr, (r.returncode, r.stderr)
        estado = QnFalso()
        srv = servidor_falso(estado)
        url = f"http://127.0.0.1:{srv.server_address[1]}/qn"
        try:
            cod, out, err = lanzar(url, os.path.join(tmp, "nt"), "--desde", "2026-01-01", "--hasta", "2026-01-02",
                                   "--topics", "market.no.existe")
            assert cod == 1 and "market.no.existe" in err, (cod, err)
        finally:
            srv.shutdown()
            srv.server_close()
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser(description="Volcado crudo del lago de qn (TI-02-DATA, paso 1).")
    ap.add_argument("--desde", help="primer dia UTC (AAAA-MM-DD), incluido")
    ap.add_argument("--hasta", help="ultimo dia UTC (AAAA-MM-DD), incluido")
    ap.add_argument("--salida", help="directorio del volcado (se crea; debe estar vacio o ser un volcado anterior igual)")
    ap.add_argument("--topics", default=",".join(TOPICS_DEFECTO), help="topics separados por comas")
    ap.add_argument("--trozo-dias", type=int, default=31, help="dias por peticion (se parte si qn rechaza por filas)")
    ap.add_argument("--espera-base", type=float, default=ESPERA_BASE_S, help="espera base de los reintentos, en segundos")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if not (a.desde and a.hasta and a.salida):
        print("descarga_lago: faltan --desde, --hasta o --salida", file=sys.stderr)
        return EXIT_USO
    if a.trozo_dias < 1 or a.espera_base < 0:
        print("descarga_lago: --trozo-dias debe ser >= 1 y --espera-base >= 0", file=sys.stderr)
        return EXIT_USO
    try:
        desde, hasta = date.fromisoformat(a.desde), date.fromisoformat(a.hasta)
    except ValueError:
        print("descarga_lago: --desde y --hasta deben ser AAAA-MM-DD", file=sys.stderr)
        return EXIT_USO
    if desde > hasta:
        print("descarga_lago: --desde es posterior a --hasta", file=sys.stderr)
        return EXIT_USO
    base = os.environ.get("QN_URLS", "").split(",")[0].strip().rstrip("/")
    acceso = os.environ.get("QN_TOKEN", "").strip()
    env = os.environ.get("QN_ENV", "").strip() or "main"
    if not base or not acceso:
        print("descarga_lago: faltan QN_URLS o QN_TOKEN en el entorno", file=sys.stderr)
        return EXIT_USO
    return correr(a, base, acceso, env)


if __name__ == "__main__":
    sys.exit(main())
