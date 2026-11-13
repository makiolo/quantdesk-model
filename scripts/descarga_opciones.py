"""OC-03: volcado bajo demanda, Python 3.12 y SOLO biblioteca estandar.

QN_URLS (primera base), QN_ENV (main), QN_TOKEN (solo Authorization).
--desde/--hasta son sesiones NY inclusivas, desde 2026-11-12. Se consulta
ademas hacia atras hasta tener cinco sesiones con capture_id o llegar al corte
OC-03; ese contexto se declara y no amplia el rango que se exportara.
Una ventana usa medianoches NY: incluye el reintento de las 19:00 NY incluso
cuando ya es el dia siguiente UTC. El servidor filtra _ts, el cliente date.
Sin redirecciones, sin truncar resultados; rechazo /limit divide hasta un dia.
No hay reloj de ejecucion en los datos. Directorios nuevos, manifiesto atomico,
SHA-256 por fichero. --selftest sustituye el transporte, sin abrir sockets.

En mini: python3 descarga_opciones.py --desde 2026-11-12 --hasta AAAA-MM-DD
  --salida /ruta/volcado_nuevo
Mini no monta E:. Copiar despues con scp el directorio del volcado a
E:/quantdesk-lab/tmp/TI-09-ARCH/<nombre>/ en el laboratorio.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "ti-09-arch.descarga/v1"
ESQUEMA = "ti-09-arch.volcado/v1"
TOPIC = "market.options.chain"
INICIO = date(2026, 11, 12)
TAGS = ("symbol", "asset_type", "opt_type")
TMP = Path(os.environ.get("TI09_TMP", "E:/quantdesk-lab/tmp/TI-09-ARCH" if os.name == "nt" else "./tmp-ti09"))


def json_texto(doc):
    return json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def cargar_json(texto):
    def no_finito(valor):
        raise ValueError("JSON contiene numero no finito")
    return json.loads(texto, parse_constant=no_finito)


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def guardar_json(ruta, doc):
    ruta = Path(ruta)
    temporal = ruta.with_suffix(ruta.suffix + ".part")
    temporal.write_text(json_texto(doc) + "\n", encoding="utf-8", newline="\n")
    temporal.replace(ruta)


def sanear(texto, token):
    return " ".join(str(texto).replace(token, "[redactado]").split())[:400] if token else " ".join(str(texto).split())[:400]


def sin_secreto(doc, token):
    # Un servidor puede hacer eco incluso en una respuesta 200. Nunca persistirlo.
    if isinstance(doc, str):
        if token and token in doc:
            raise ValueError("respuesta contiene la credencial; no se guarda")
    elif isinstance(doc, dict):
        for k, v in doc.items():
            sin_secreto(k, token)
            sin_secreto(v, token)
    elif isinstance(doc, (list, tuple)):
        for v in doc:
            sin_secreto(v, token)


def validar_base(base):
    u = urllib.parse.urlsplit(base)
    if u.scheme not in ("http", "https") or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise ValueError("QN_URLS debe ser una base http(s) sin credenciales, query ni fragmento")
    return base.rstrip("/")


def medianoche_ny(d):
    """RFC3339, reglas DST EEUU desde 2007; no necesita tzdata en mini.

    El cambio es a las 02:00: la medianoche del segundo domingo de marzo aun
    es EST, la del primer domingo de noviembre aun es EDT.
    """
    marzo, noviembre = date(d.year, 3, 1), date(d.year, 11, 1)
    inicio = marzo + timedelta(days=(6 - marzo.weekday()) % 7 + 7)
    fin = noviembre + timedelta(days=(6 - noviembre.weekday()) % 7)
    offset = "-04:00" if inicio < d <= fin else "-05:00"
    return d.isoformat() + "T00:00:00" + offset


def rango(desde, hasta):
    if desde < INICIO or desde > hasta:
        raise ValueError("rango invalido: desde >= 2026-11-12 y desde <= hasta")


class DemasiadasFilas(RuntimeError):
    pass


class CredencialRechazada(RuntimeError):
    pass


class SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Cliente:
    def __init__(self, base, token, env="main", abrir=None, espera=1.0):
        self.base = validar_base(base)
        self.token, self.env, self.espera = token, env, espera
        self.abrir = abrir or urllib.request.build_opener(SinRedireccion()).open

    def get(self, ruta, params, registro):
        params = {"env": self.env, **params}
        entrada = {"ruta": "/api/v1" + ruta, "params": params, "intentos": 0}
        registro.append(entrada)
        url = self.base + "/api/v1" + ruta + "?" + urllib.parse.urlencode(params)
        ultimo = ""
        for intento in range(4):
            entrada["intentos"] += 1
            if intento:
                time.sleep(self.espera * 2 ** (intento - 1))
            req = urllib.request.Request(url, headers={"Authorization": "Bearer " + self.token, "Accept": "application/json"})
            try:
                with self.abrir(req, timeout=120) as respuesta:
                    doc = cargar_json(respuesta.read().decode("utf-8"))
                if not isinstance(doc, dict):
                    raise ValueError("respuesta no es objeto")
                sin_secreto(doc, self.token)
                return doc
            except urllib.error.HTTPError as e:
                cuerpo = e.read(4096).decode("utf-8", "replace")
                if e.code in (401, 403):
                    raise CredencialRechazada(f"HTTP {e.code}: qn rechaza QN_TOKEN") from None
                if 300 <= e.code < 400:
                    raise RuntimeError(f"HTTP {e.code}: redireccion rechazada; revisar QN_URLS") from None
                # No mostrar cuerpos: hasta un eco truncado podria revelar
                # parte de una credencial. El cuerpo solo clasifica /limit.
                ultimo = f"HTTP {e.code} de qn"
                if e.code >= 500 or e.code == 429:
                    continue
                try:
                    error = cargar_json(cuerpo)
                except ValueError:
                    error = {}
                if isinstance(error, dict) and error.get("code") == "invalid" and any(
                    isinstance(x, dict) and x.get("path") == "/limit" for x in (error.get("details") or [])
                ):
                    raise DemasiadasFilas(ultimo) from None
                raise RuntimeError(ultimo) from None
            except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
                ultimo = type(e).__name__ + " de transporte qn"
        raise RuntimeError(ultimo + " (tras 4 intentos)")


def leer_ventana(cli, tags, desde, hasta, registro, avisos):
    try:
        doc = cli.get("/objects/" + TOPIC, {**tags, "from": medianoche_ny(desde),
                      "to": medianoche_ny(hasta + timedelta(days=1))}, registro)
    except DemasiadasFilas:
        if desde == hasta:
            raise RuntimeError(f"demasiadas filas incluso en un solo dia: {desde} {json_texto(tags)}") from None
        mitad = desde + (hasta - desde) // 2
        avisos.append(f"rango dividido por /limit: {desde}..{hasta}")
        return (leer_ventana(cli, tags, desde, mitad, registro, avisos)
                + leer_ventana(cli, tags, mitad + timedelta(days=1), hasta, registro, avisos))
    filas = doc.get("rows")
    if not isinstance(filas, list) or any(not isinstance(r, dict) for r in filas):
        raise ValueError("/objects exige rows lista de objetos")
    if any(any(r.get(k) != v for k, v in tags.items()) for r in filas):
        raise ValueError("fila con tags distintos del filtro")
    registro[-1]["respuesta"] = {k: doc.get(k) for k in ("columns", "head_cycle", "lake_cycle")}
    return filas


def descargar(cli, desde, hasta, salida, trozo=31):
    rango(desde, hasta)
    if trozo < 1:
        raise ValueError("trozo-dias debe ser positivo")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sin_secreto({"base": cli.base, "env": cli.env, "salida": str(salida)}, cli.token)
    m = {"schema": ESQUEMA, "version_script": VERSION, "script_sha256": hashlib.sha256(
        Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(), "base": cli.base,
        "env": cli.env, "topic": TOPIC, "desde": str(desde), "hasta": str(hasta),
        "completo": False, "ficheros": [], "avisos": [], "descartadas": {},
        "semilla": 0, "corte_oc03": str(INICIO), "peticiones_catalogo": []}
    guardar_json(salida / "manifest.json", m)
    try:
        latest = cli.get("/topics/" + TOPIC + "/latest", {}, m["peticiones_catalogo"])
        if not isinstance(latest.get("items"), list):
            raise ValueError("/latest exige items")
        combos = set()
        for item in latest["items"]:
            tags = item.get("tags") if isinstance(item, dict) else None
            if not isinstance(tags, dict) or any(not isinstance(tags.get(k), str) or not tags[k] for k in TAGS):
                raise ValueError("/latest: faltan tags symbol, asset_type u opt_type")
            combos.add(tuple(tags[k] for k in TAGS))
        m["catalogo"] = [dict(zip(TAGS, c)) for c in sorted(combos)]
        m["avisos"].append("Universo limitado a combinaciones visibles en /latest; posible sesgo de supervivencia.")
        if not combos:
            m["avisos"].append("/latest vacio: no hay combinaciones que consultar")
        # Escribir por combinacion y ventana: el volcado real puede contener
        # millones de contratos; no retener todas las cadenas en RAM de mini.
        filas_combo = {c: {"ruta": f"opciones_{i:05d}.ndjson", "filas": 0} for i, c in enumerate(sorted(combos))}
        for info in filas_combo.values():
            (salida / (info["ruta"] + ".part")).touch()
        registros = {c: [] for c in sorted(combos)}
        descartadas = Counter()
        sesiones = set()

        def tramo(a, b):
            for c in filas_combo:
                d = a
                while d <= b:
                    fin = min(b, d + timedelta(days=trozo - 1))
                    rows = leer_ventana(cli, dict(zip(TAGS, c)), d, fin, registros[c], m["avisos"])
                    info = filas_combo[c]
                    with open(salida / (info["ruta"] + ".part"), "a", encoding="utf-8", newline="\n") as f:
                        for r in sorted(rows, key=json_texto):
                            if not r.get("capture_id"):
                                descartadas["sin_capture_id"] += 1
                                continue
                            fecha = date.fromisoformat(r["date"])
                            if fecha < INICIO:
                                descartadas["anterior_oc03"] += 1
                            elif not a <= fecha <= b:
                                descartadas["fuera_de_ventana_sesion"] += 1
                            else:
                                f.write(json_texto(r) + "\n")
                                info["filas"] += 1
                                sesiones.add(fecha)
                    d = fin + timedelta(days=1)

        tramo(desde, hasta)
        consulta_desde = desde if combos else INICIO
        while len([d for d in sesiones if d < desde]) < 5 and consulta_desde > INICIO and combos:
            anterior = max(INICIO, consulta_desde - timedelta(days=14))
            tramo(anterior, consulta_desde - timedelta(days=1))
            consulta_desde = anterior
        m["consulta_desde"] = str(consulta_desde)
        m["sesiones_contexto"] = [str(d) for d in sorted(sesiones) if d < desde]
        m["contexto_completo"] = len(m["sesiones_contexto"]) >= 5 or consulta_desde == INICIO
        for combo, info in filas_combo.items():
            rel = info["ruta"]
            (salida / (rel + ".part")).replace(salida / rel)
            m["ficheros"].append({"ruta": rel, "etiquetas": dict(zip(TAGS, combo)), "filas": info["filas"],
                                   "sha256": sha256(salida / rel), "peticiones": registros[combo]})
        m["descartadas"] = dict(sorted(descartadas.items()))
        m["completo"] = True
    except Exception:
        # No persistir el texto de excepcion (puede contener secretos de transporte).
        m["avisos"].append("Volcado incompleto: no consumible; usar un directorio nuevo al repetir.")
        raise
    finally:
        sin_secreto(m, cli.token)
        guardar_json(salida / "manifest.json", m)
    return m


def fila_fixture(symbol="SPY", asset_type="ETF", opt_type="call", sesion="2026-11-12",
                 captura=None, strike=100, mid=5, **cambios):
    """Forma real /objects: enteros ns y todos los campos publicados (datos sinteticos)."""
    ns = int((datetime.fromisoformat(sesion + "T21:31:25+00:00") - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()) * 10**9
    row = {"_ts": ns, "_recv_ts": ns + 1234567, "_batch_id": "fixture-batch", "_offset": 0,
           "_cycle": 21, "_log_partition": 0, "_clock_offset_ns": 0, "_schema_version": 1,
           "symbol": symbol, "asset_type": asset_type, "opt_type": opt_type, "strike": strike,
           "maturity": "2027-01-15", "last_price": mid, "bid": mid - .005, "ask": mid + .005,
           "implied_vol": .25, "in_the_money": False, "volume": 0, "open_interest": 123,
           "date": sesion, "source": "yfinance", "captured_at": ns,
           "capture_id": captura or sesion + "-163125-5b2305", "underlying_price": 757.1199951171875}
    row.update(cambios)
    return row


class QnFalso:
    """Transporte en proceso: recibe Request real; no sockets, no DNS."""
    def __init__(self, filas, token="fixture-token-no-real", limite=None):
        self.filas, self.token, self.limite = filas, token, limite
        self.peticiones = []
        self.fallo = None

    def abrir(self, req, timeout):
        assert req.get_header("Authorization") == "Bearer " + self.token
        assert self.token not in req.full_url
        u = urllib.parse.urlsplit(req.full_url)
        q = dict(urllib.parse.parse_qsl(u.query))
        self.peticiones.append(q)
        if self.fallo:
            codigo, cuerpo = self.fallo
            raise urllib.error.HTTPError(req.full_url, codigo, "fixture", {}, io.BytesIO(cuerpo.encode()))
        if u.path.endswith("/latest"):
            combos = sorted({tuple(r[k] for k in TAGS) for r in self.filas})
            doc = {"items": [{"tags": dict(zip(TAGS, c))} for c in combos]}
        else:
            a = datetime.fromisoformat(q["from"]).timestamp() * 10**9
            b = datetime.fromisoformat(q["to"]).timestamp() * 10**9
            rows = [r for r in self.filas if all(r[k] == q[k] for k in TAGS) and a <= r["_ts"] < b]
            if self.limite is not None and len(rows) > self.limite:
                cuerpo = '{"code":"invalid","details":[{"path":"/limit"}]}'
                raise urllib.error.HTTPError(req.full_url, 400, "fixture", {}, io.BytesIO(cuerpo.encode()))
            doc = {"rows": rows, "columns": sorted(rows[0]) if rows else [], "head_cycle": 21, "lake_cycle": 21}
        return io.BytesIO(json_texto(doc).encode())


def selftest():
    from unittest.mock import patch
    # Estas pruebas usan unicamente transporte inyectado; cualquier socket es un fallo.
    TMP.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="descarga_", dir=TMP) as tmp, patch(
        "socket.socket", side_effect=AssertionError("red prohibida")):
        base = Path(tmp)
        rows = [fila_fixture(sesion=d) for d in ("2026-11-12", "2026-11-13", "2026-11-16")]
        rows += [fila_fixture(capture_id=None, opt_type="CALL", asset_type="EQUITY"),
                 fila_fixture(sesion="2026-11-11"),
                 fila_fixture(strike=101, captura="2026-11-12-190000-abcdef",
                              _ts=1794528000000000000, captured_at=1794528000000000000)]
        qn = QnFalso(rows, limite=2)
        cli = Cliente("http://fixture.invalid/qn", qn.token, abrir=qn.abrir, espera=0)
        m = descargar(cli, INICIO, date(2026, 11, 26), base / "ok")
        assert m["completo"] and m["descartadas"]["sin_capture_id"] == 1
        assert any("dividido" in a for a in m["avisos"]), m
        recibidas = [cargar_json(linea) for f in m["ficheros"] for linea in (base / "ok" / f["ruta"]).read_text(encoding="utf-8").splitlines()]
        assert len(recibidas) == 4 and any(r["capture_id"].endswith("abcdef") for r in recibidas)
        assert all(date.fromisoformat(r["date"]) >= INICIO for r in recibidas)
        assert all(qn.token not in p.read_text(encoding="utf-8") for p in (base / "ok").iterdir())
        assert all(sha256(base / "ok" / f["ruta"]) == f["sha256"] for f in m["ficheros"])
        # Un solo dia no cabe: no truncar ni completar el manifest.
        qn.limite = 0
        try:
            descargar(cli, INICIO, INICIO, base / "limite")
            raise AssertionError("falta error /limit")
        except RuntimeError as e:
            assert "un solo dia" in str(e)
        assert not cargar_json((base / "limite/manifest.json").read_text())["completo"]
        qn.limite = None
        for codigo in (401, 403, 302, 500, 429):
            qn.fallo = codigo, qn.token
            n = len(qn.peticiones)
            try:
                cli.get("/test", {}, [])
                raise AssertionError("falta error HTTP")
            except (CredencialRechazada, RuntimeError) as e:
                assert qn.token not in str(e)
            assert len(qn.peticiones) - n == (4 if codigo in (500, 429) else 1)
        qn.fallo = None
        # Eco en HTTP 200 y valores escapados: no persistir una credencial.
        qn.filas = [fila_fixture(source=qn.token)]
        try:
            cli.get("/objects/" + TOPIC, {"symbol": "SPY", "asset_type": "ETF", "opt_type": "call",
                    "from": medianoche_ny(INICIO), "to": medianoche_ny(INICIO + timedelta(days=1))}, [])
            raise AssertionError("eco de token no rechazado")
        except ValueError as e:
            assert qn.token not in str(e) and "credencial" in str(e)
        try:
            sin_secreto({"dato": 'token-con-"comillas'}, 'token-con-"comillas')
            raise AssertionError("token escapado")
        except ValueError:
            pass
        # Contexto: cinco sesiones previas CON datos, no cinco dias naturales.
        qn.filas = [fila_fixture(sesion=d) for d in ("2026-11-12", "2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-20")]
        contexto = descargar(cli, date(2026, 11, 20), date(2026, 11, 20), base / "contexto")
        assert len(contexto["sesiones_contexto"]) == 5 and contexto["contexto_completo"]
        qn.filas = []
        vacio = descargar(cli, date(2026, 11, 20), date(2026, 11, 20), base / "sin_catalogo")
        assert vacio["completo"] and vacio["contexto_completo"] and not vacio["ficheros"]
        # Piloto devuelto fuera de ventana por un servidor: se descarta antes de OC-03.
        class ServidorDesordenado(Cliente):
            def get(self, ruta, params, registro):
                if ruta.endswith("/latest"):
                    return {"items": [{"tags": {k: fila_fixture()[k] for k in TAGS}}]}
                registro.append({})
                return {"rows": [fila_fixture(sesion="2026-11-11")], "columns": []}
        piloto = descargar(ServidorDesordenado("http://fixture.invalid", qn.token), INICIO, INICIO, base / "piloto")
        assert piloto["descartadas"] == {"anterior_oc03": 1}
        for mala in ("http://user:pass@fixture.invalid", "http://fixture.invalid?token=x"):
            try:
                validar_base(mala)
                raise AssertionError("base insegura")
            except ValueError:
                pass
        assert medianoche_ny(date(2027, 3, 14)).endswith("-05:00")
        assert medianoche_ny(date(2027, 3, 15)).endswith("-04:00")
        assert medianoche_ny(date(2026, 11, 1)).endswith("-04:00")
        try:
            rango(date(2026, 11, 11), INICIO)
            raise AssertionError("rango anterior")
        except ValueError:
            pass
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    ap.add_argument("--salida")
    ap.add_argument("--trozo-dias", type=int, default=31)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    token = os.environ.get("QN_TOKEN", "").strip()
    try:
        if not all((a.desde, a.hasta, a.salida)):
            raise ValueError("faltan --desde, --hasta o --salida")
        base = os.environ.get("QN_URLS", "").split(",")[0].strip()
        if not base or not token:
            raise ValueError("faltan QN_URLS o QN_TOKEN en entorno")
        sin_secreto(vars(a), token)
        m = descargar(Cliente(base, token, os.environ.get("QN_ENV", "main") or "main"),
                      date.fromisoformat(a.desde), date.fromisoformat(a.hasta), a.salida, a.trozo_dias)
        print(f"volcado completo: {len(m['ficheros'])} ficheros; manifest SHA-256 {sha256(Path(a.salida) / 'manifest.json')}")
        return 0
    except CredencialRechazada as e:
        print("descarga_opciones: " + sanear(e, token), file=sys.stderr)
        return 3
    except Exception as e:
        print("descarga_opciones: " + sanear(e, token), file=sys.stderr)
        return 2 if isinstance(e, (ValueError, FileExistsError)) else 1


if __name__ == "__main__":
    sys.exit(main())
