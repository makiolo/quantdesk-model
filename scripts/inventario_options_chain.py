"""Inventario de SOLO LECTURA del lago de quantdesk-network (tarea TI-01-INV).

Por cada topic que la credencial puede leer y cuyo nombre case con --topics (por defecto `market.*`), y por cada instrumento
(combinación de etiquetas que lista /latest): tipo de lectura, esquema, clave de instrumento, primera y última fecha,
frecuencia observada (paso mediano dentro del día y filas por día), días hábiles con datos frente a esperables, huecos de
al menos --gap días hábiles y calidad básica (duplicados por clave+marca, nulos, no finitos y negativos donde no tienen
sentido). Solo hace GET; nunca publica. Solo biblioteca estándar.

Variables: QN_URLS (bases separadas por comas, p. ej. http://192.168.1.48:8790/qn; se usa la primera), QN_TOKEN (permiso de
lectura sobre market.>) y QN_ENV (entorno, por defecto main). La credencial sólo se lee de QN_TOKEN; nunca se imprime ni se
escribe en --json o --informe. Uso:

    .venv/Scripts/python -X utf8 scripts/inventario_options_chain.py --desde 2025-01-01 --json RUTA.json --informe RUTA.md
    .venv/Scripts/python -X utf8 scripts/inventario_options_chain.py --topics "market.options.*" --max-symbols 2
    .venv/Scripts/python -X utf8 scripts/inventario_options_chain.py --selftest
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import math
import os
import re
import shlex
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone

EXCLUIR_CLAVE = ("venue", "exchange", "source", "feed", "env")  # etiquetas que no identifican el instrumento
TIEMPO = ("ts", "ts_corrected", "date", "time", "timestamp")  # columnas de marca, por prioridad
CLAVE_CONTRATO = ("maturity", "strike", "right", "option_type", "id")  # campos que distinguen filas de una misma marca
NO_NEGATIVO = re.compile(r"price|precio|volume|volumen|bid|ask|open|high|low|close|\blast\b", re.I)
NO_FINITO = ("NaN", "Infinity", "-Infinity")  # cómo el servidor escribe los no finitos en JSON
SIN_FILTRO = "(todo el topic)"
CMD_GPU = "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv"


def get(base: str, acceso: str, env: str, path: str, params: dict, peticiones: list) -> dict:
    """GET a `{base}/api/v1{path}`. La credencial va sólo en la cabecera Authorization."""
    q = {"env": env, **params}
    peticiones.append({"ruta": f"/api/v1{path}", "params": {k: str(v) for k, v in q.items()}})
    url = f"{base}/api/v1{path}?{urllib.parse.urlencode(q)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {acceso}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        cuerpo = e.read(300).decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} en {path}: {cuerpo}") from None


def parse_ts(v) -> datetime | None:
    """Marca temporal: entero en ns o texto ISO 8601 (las fracciones se recortan a microsegundos)."""
    if v is None or isinstance(v, bool):
        return None
    try:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v / 1e9, tz=timezone.utc)
        if isinstance(v, str) and len(v) >= 10:
            d = datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", v.strip().replace("Z", "+00:00")))
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None
    return None


def row_time(row: dict) -> datetime | None:
    """Marca de la fila: la primera columna de tiempo por prioridad (ts, date...) con valor válido."""
    orden = [k for k in TIEMPO if k in row] + [k for k in row if "ts" in k.lower() and k not in TIEMPO]
    for k in orden:
        t = parse_ts(row[k])
        if t is not None:
            return t
    return None


def row_day(row: dict) -> date | None:
    """Fecha de la fila: el campo `date` del objeto o, si falta, la marca de evento."""
    t = row_time(row)
    return t.date() if t else None


def business_days(a: date, b: date) -> list[date]:
    out, d = [], a
    while d <= b:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def gaps(days: set[date], a: date, b: date, min_len: int) -> list[tuple[date, date, int]]:
    """Tramos de días hábiles sin datos de longitud >= min_len (festivos incluidos: es una cota superior)."""
    out, run = [], []
    for d in business_days(a, b):
        if d in days:
            if len(run) >= min_len:
                out.append((run[0], run[-1], len(run)))
            run = []
        else:
            run.append(d)
    if len(run) >= min_len:
        out.append((run[0], run[-1], len(run)))
    return out


def months(a: date, b: date):
    d = a.replace(day=1)
    while d <= b:
        nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        yield max(d, a), min(nxt - timedelta(days=1), b)
        d = nxt


def detectar_clave(tags: list[str]) -> str | None:
    """Clave de instrumento: `symbol` si el topic lo tiene; si no, la primera etiqueta que no sea de venue o fuente."""
    if "symbol" in tags:
        return "symbol"
    return next((t for t in tags if t not in EXCLUIR_CLAVE), None)


def aplanar(node: dict, prefijo: str = "") -> list[tuple[str, str]]:
    """Hojas de un JSON Schema de objeto como (`a.b`, tipo); tipo `json` si no es escalar."""
    if not isinstance(node, dict):
        return []
    tipo = node.get("type")
    tipos = tipo if isinstance(tipo, list) else [tipo]
    props = node.get("properties")
    if props and "object" in tipos:
        out = []
        for k, sub in props.items():
            out += aplanar(sub, f"{prefijo}.{k}" if prefijo else k)
        return out
    if not prefijo:
        return []
    for t in ("number", "integer", "string", "boolean"):
        if t in tipos and "array" not in tipos and "object" not in tipos:
            return [(prefijo, t)]
    return [(prefijo, "json")]


def pasos_en_dia(marcas: list[datetime]) -> list[float]:
    """Segundos entre marcas consecutivas que caen en el mismo día UTC (los cruces de día no cuentan)."""
    m = sorted(marcas)
    return [(b - a).total_seconds() for a, b in zip(m, m[1:]) if a.date() == b.date() and b > a]


def fmt_paso(s: float | None) -> str:
    if s is None:
        return "–"
    if s < 60:
        return f"{s:g} s"
    return f"{s / 60:g} min" if s < 3600 else f"{s / 3600:g} h"


class Acumulador:
    """Estadísticas de un topic, acumuladas mes a mes y por instrumento."""

    def __init__(self):
        self.dias, self.filas, self.filas_dia, self.pasos = set(), 0, Counter(), []
        self.duplicados, self.nulos, self.no_finitos, self.negativos = 0, Counter(), Counter(), Counter()
        self.instr = {}


def procesar(acc: Acumulador, etiqueta: str, res: dict) -> None:
    """Acumula una respuesta mensual de un instrumento: días, filas, paso, duplicados, nulos y valores imposibles."""
    ins = acc.instr.setdefault(etiqueta, {"dias": set(), "filas": 0, "mat": set(), "strk": set()})
    columnas = [c["name"] for c in res.get("columns", [])]
    marcas, vistos = [], Counter()
    for r in res.get("rows", []):
        ins["filas"] += 1
        acc.filas += 1
        t = row_time(r)
        if t is not None:
            ins["dias"].add(t.date())
            acc.dias.add(t.date())
            acc.filas_dia[(etiqueta, t.date())] += 1
            marcas.append(t)
        clave = (repr(t), tuple(repr(r.get(c)) for c in CLAVE_CONTRATO if c in r))
        if vistos[clave]:
            acc.duplicados += 1
        vistos[clave] += 1
        for c in columnas:
            v = r.get(c)
            if v is None:
                acc.nulos[c] += 1
            elif (isinstance(v, str) and v in NO_FINITO) or (isinstance(v, float) and not math.isfinite(v)):
                acc.no_finitos[c] += 1
            elif isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0 and NO_NEGATIVO.search(c):
                acc.negativos[c] += 1
        for campo, conj in (("maturity", ins["mat"]), ("strike", ins["strk"])):
            if r.get(campo) is not None:
                conj.add(str(r[campo]))
    acc.pasos += pasos_en_dia(marcas)


def resumen_instrumento(ins: dict, gap: int) -> dict:
    base = {"filas": ins["filas"], "vencimientos": len(ins["mat"]), "strikes": len(ins["strk"])}
    dias = sorted(ins["dias"])
    if not dias:
        return dict(base, primera=None, ultima=None, dias_habiles=0, esperables=0, cobertura=None, huecos=0)
    habiles = [d for d in dias if d.weekday() < 5]
    esperables = max(len(business_days(dias[0], dias[-1])), 1)
    return dict(base, primera=dias[0].isoformat(), ultima=dias[-1].isoformat(), dias_habiles=len(habiles),
                esperables=esperables, cobertura=round(len(habiles) / esperables, 3),
                huecos=len(gaps(ins["dias"], dias[0], dias[-1], gap)))


def resumen(acc: Acumulador, gap: int, meta: dict) -> dict:
    """Cifras de un topic a partir de lo acumulado; `meta` aporta lectura, etiquetas, esquema y estado."""
    out = dict(meta, primera=None, ultima=None, dias=0, dias_habiles=0, dias_fin_de_semana=0, esperables=0,
               cobertura=None, huecos=[], paso_mediano_s=None, filas=acc.filas, filas_por_dia_mediana=None,
               duplicados=acc.duplicados, nulos=dict(acc.nulos), no_finitos=dict(acc.no_finitos),
               negativos=dict(acc.negativos),
               por_instrumento={et: resumen_instrumento(ins, gap) for et, ins in sorted(acc.instr.items())})
    if not acc.dias:
        return out
    dias = sorted(acc.dias)
    habiles = [d for d in dias if d.weekday() < 5]
    esperables = max(len(business_days(dias[0], dias[-1])), 1)
    out.update(primera=dias[0].isoformat(), ultima=dias[-1].isoformat(), dias=len(dias), dias_habiles=len(habiles),
               dias_fin_de_semana=len(dias) - len(habiles), esperables=esperables,
               cobertura=round(len(habiles) / esperables, 3),
               huecos=[[x.isoformat(), y.isoformat(), n] for x, y, n in gaps(acc.dias, dias[0], dias[-1], gap)],
               paso_mediano_s=statistics.median(acc.pasos) if acc.pasos else None,
               filas_por_dia_mediana=statistics.median(acc.filas_dia.values()) if acc.filas_dia else None)
    return out


def inventariar(base: str, acceso: str, env: str, info: dict, a, desde: date, hasta: date, peticiones: list) -> dict:
    nombre, kind = info["topic"], info.get("kind")
    sch = get(base, acceso, env, f"/topics/{nombre}/schema", {}, peticiones)
    spec = sch.get("schema") or {}
    tags = info.get("tags") or sch.get("tags") or []
    if kind == "series":
        lectura = f"/series/{nombre}/rows"
        esquema = [f"{c['name']} ({c.get('agg')})" for c in spec.get("columns", [])]
    elif kind == "object":
        lectura = f"/objects/{nombre}"
        esquema = [f"{n}:{t}" for n, t in aplanar(spec)]
    else:
        raise RuntimeError(f"tipo de topic desconocido: {kind!r}")
    lat = get(base, acceso, env, f"/topics/{nombre}/latest", {}, peticiones)
    combos = sorted({tuple(sorted((it.get("tags") or {}).items())) for it in lat.get("items", [])})
    listados = len(combos)
    if a.max_symbols:
        combos = combos[: a.max_symbols]
    acc = Acumulador()
    for combo in combos:
        etiqueta = ",".join(f"{k}={v}" for k, v in combo) or SIN_FILTRO
        for m0, m1 in months(desde, hasta):
            params = {**dict(combo), "from": m0.isoformat(), "to": (m1 + timedelta(days=1)).isoformat()}
            procesar(acc, etiqueta, get(base, acceso, env, lectura, params, peticiones))
    meta = {"kind": kind, "lectura": lectura, "tags": tags, "clave": detectar_clave(tags), "esquema": esquema,
            "instrumentos_listados": listados, "instrumentos_leidos": len(combos), "error": None}
    return resumen(acc, a.gap, meta)


def linea(nombre: str, r: dict, gap: int) -> str:
    if r.get("error"):
        return f"{nombre:40s} ERROR {r['error']}"
    if not r.get("primera"):
        return f"{nombre:40s} sin datos ({r.get('instrumentos_listados', 0)} instrumentos listados)"
    mayor = max((h[2] for h in r["huecos"]), default=0)
    return (f"{nombre:40s} {r['kind']:7s} {r['primera']}→{r['ultima']}  días hábiles {r['dias_habiles']}/{r['esperables']} "
            f"({r['cobertura']:.0%})  filas {r['filas']}  paso {fmt_paso(r['paso_mediano_s'])}  "
            f"instrumentos {r['instrumentos_leidos']}/{r['instrumentos_listados']}  dup {r['duplicados']}  "
            f"huecos≥{gap}: {len(r['huecos'])} (mayor {mayor} días)")


def celda(v) -> str:
    if v is None or v == "":
        return "–"
    return str(v).replace("|", "/").replace("\n", " ")


def fila(cells: list) -> str:
    return "| " + " | ".join(celda(c) for c in cells) + " |"


def pct(x) -> str:
    return "–" if x is None else f"{x:.0%}"


def fmt_num(x) -> str:
    return "–" if x is None else f"{x:g}"


def fmt_dict(d: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in d.items()) or "ninguno"


def render_md(report: dict) -> str:
    c, tops = report["cabecera"], report["topics"]
    cab = ["# Inventario del lago quantdesk-network (TI-01-INV)", "",
           f"- Fecha de ejecución (UTC): {c['fecha_utc']}",
           f"- Días pedidos: {c['desde']} a {c['hasta']}, ambos incluidos",
           f"- Base: {c['base']} (entorno `{c['env']}`). La credencial no figura en este informe.",
           f"- Topics: patrón `{c['patron']}`; instrumentos por topic: {c['max_symbols'] or 'todos'}",
           f"- Huecos: tramos de {c['gap']} o más días hábiles sin datos; los festivos cuentan como hueco (cota superior)",
           f"- Peticiones GET hechas: {len(c['peticiones'])} (lista completa en el JSON, sin cabeceras)", ""]
    cabeceras = ["topic", "lectura", "clave", "instrumentos", "primera", "última", "días hábiles con datos", "cobertura",
                 "paso mediano", "filas por instrumento y día", "duplicados", "nulos", "no finitos", "negativos",
                 "huecos", "estado"]
    L = cab + ["## Resumen por topic", "", fila(cabeceras), "|" + "---|" * len(cabeceras)]
    for n, t in tops.items():
        if t.get("error"):
            L.append(fila([n, t.get("lectura")] + [None] * 13 + [f"ERROR: {t['error']}"]))
            continue
        L.append(fila([n, t["lectura"], t["clave"], f"{t['instrumentos_leidos']}/{t['instrumentos_listados']}",
                       t["primera"], t["ultima"], f"{t['dias_habiles']}/{t['esperables']}", pct(t["cobertura"]),
                       fmt_paso(t["paso_mediano_s"]), fmt_num(t["filas_por_dia_mediana"]), t["duplicados"],
                       sum(t["nulos"].values()), sum(t["no_finitos"].values()), sum(t["negativos"].values()),
                       len(t["huecos"]), "OK" if t["primera"] else "sin datos"]))
    L += ["", "## Detalle por topic"]
    for n, t in tops.items():
        L += ["", f"### {n}", ""]
        if t.get("error"):
            L += [f"- ERROR: {t['error']}"]
            continue
        etiq = ", ".join(t["tags"]) or "ninguna"
        L += [f"- Tipo: {t['kind']}; lectura `{t['lectura']}`; etiquetas: {etiq}; "
              f"clave de instrumento: {t['clave'] or 'ninguna (un único instrumento)'}",
              f"- Esquema ({'columnas' if t['kind'] == 'series' else 'campos'}): {', '.join(t['esquema']) or 'sin datos'}"]
        if not t["primera"]:
            L += ["- Sin datos en el rango pedido"]
            continue
        mayores = sorted(t["huecos"], key=lambda h: -h[2])[:5]
        txt_huecos = "; mayores: " + ", ".join(f"{x}→{y} ({k} d)" for x, y, k in mayores) if mayores else ""
        L += [f"- Primera {t['primera']}, última {t['ultima']}; días con datos {t['dias']} ({t['dias_habiles']} hábiles, "
              f"{t['dias_fin_de_semana']} en fin de semana) frente a {t['esperables']} hábiles esperables",
              f"- Frecuencia: paso mediano dentro del día {fmt_paso(t['paso_mediano_s'])}; filas por instrumento y día "
              f"(mediana) {fmt_num(t['filas_por_dia_mediana'])}",
              f"- Huecos de {c['gap']} o más días hábiles: {len(t['huecos'])}{txt_huecos}",
              f"- Calidad: duplicados (etiquetas + marca + campos de contrato) {t['duplicados']}; nulos "
              f"{fmt_dict(t['nulos'])}; no finitos {fmt_dict(t['no_finitos'])}; negativos donde no tienen sentido "
              f"{fmt_dict(t['negativos'])}", "",
              fila(["instrumento", "primera", "última", "días hábiles", "esperables", "cobertura", "filas", "huecos",
                    "vencimientos", "strikes"]),
              "|" + "---|" * 10]
        for et, i in t["por_instrumento"].items():
            L.append(fila([et, i["primera"], i["ultima"], i["dias_habiles"], i["esperables"], pct(i["cobertura"]),
                           i["filas"], i["huecos"], i["vencimientos"], i["strikes"]]))
    L += ["", "## GPU de los nodos: pendiente", "",
          "La API de qn no expone nodos ni GPU: en el código de `crates/` del repo quantdesk-network no hay ninguna ruta ni "
          "campo de GPU (rutas de qn-server: topics, schema, publish, latest, log, admin/wal/quarantine, health, metrics). "
          "No medido. Comando a ejecutar a mano en cada nodo, pegando su salida en el informe:", "",
          "```", c["cmd_gpu"], "```", "",
          "## Consultas reproducibles", "",
          "Esta ejecución (QN_URLS, QN_TOKEN y, si aplica, QN_ENV en el entorno; la credencial no se escribe):", "",
          "```", c["comando"], "```", "",
          f"- Listado de topics: `GET {c['base']}/api/v1/topics?env={c['env']}`",
          f"- Por topic: `GET {c['base']}/api/v1/topics/<topic>/schema?env={c['env']}` y `.../latest?env={c['env']}`; "
          f"lectura histórica `/series/<topic>/rows` u `/objects/<topic>` con `from` y `to` por meses y las etiquetas de "
          f"cada instrumento.",
          "- Detalle de cada petición: `--json`, clave `cabecera.peticiones`."]
    return "\n".join(L) + "\n"


def escribir(ruta: str, texto: str, acceso: str) -> None:
    if acceso and acceso in texto:
        raise SystemExit(f"no se escribe {ruta}: contiene la credencial")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


def selftest() -> None:
    mon = date(2026, 1, 5)
    have = {mon, mon + timedelta(days=1), mon + timedelta(days=7)}
    g = gaps(have, mon, mon + timedelta(days=7), 2)
    assert g == [(date(2026, 1, 7), date(2026, 1, 9), 3)], g
    assert len(business_days(mon, mon + timedelta(days=6))) == 5
    assert row_day({"date": "2026-03-02"}) == date(2026, 3, 2)
    # clave de instrumento desde las etiquetas del topic
    assert detectar_clave(["venue", "symbol"]) == "symbol"
    assert detectar_clave(["exchange", "contract_id"]) == "contract_id"
    assert detectar_clave([]) is None
    # JSON Schema de objeto aplanado a hojas escalares
    esq = {"type": "object", "properties": {"price": {"type": "number"}, "book": {"type": "object", "properties": {
        "n": {"type": "integer"}}}, "tags": {"type": "array"}}}
    assert aplanar(esq) == [("price", "number"), ("book.n", "integer"), ("tags", "json")], aplanar(esq)
    # frecuencia: pasos de 60 s dentro del día; el cruce de medianoche no cuenta
    t0 = datetime(2026, 1, 5, 23, 58, tzinfo=timezone.utc)
    assert pasos_en_dia([t0 + timedelta(seconds=60 * i) for i in range(5)]) == [60.0, 60.0, 60.0]
    # duplicados, nulos, no finitos y negativos sobre una respuesta de ejemplo (ns con más de 6 decimales)
    acc = Acumulador()
    res = {"columns": [{"name": "ts", "type": "timestamp"}, {"name": "price", "type": "float64"},
                       {"name": "volume", "type": "int64"}],
           "rows": [{"ts": "2026-01-05T10:00:00.123456789Z", "price": 1.0, "volume": 2},
                    {"ts": "2026-01-05T10:00:00.123456789Z", "price": None, "volume": -3},
                    {"ts": "2026-01-05T10:01:00Z", "price": "NaN", "volume": 1}]}
    procesar(acc, "symbol=X", res)
    assert acc.duplicados == 1, acc.duplicados
    assert acc.nulos == Counter({"price": 1}), acc.nulos
    assert acc.no_finitos == Counter({"price": 1}), acc.no_finitos
    assert acc.negativos == Counter({"volume": 1}), acc.negativos
    assert acc.filas == 3 and len(acc.pasos) == 1 and abs(acc.pasos[0] - 59.876544) < 1e-6, acc.pasos
    # informe Markdown: cabecera, tabla y secciones obligatorias; un topic con error no rompe el formato
    tema = resumen(acc, 3, {"kind": "series", "lectura": "/series/market.x/rows", "tags": ["symbol"],
                            "clave": "symbol", "esquema": ["price (last)"], "instrumentos_listados": 1,
                            "instrumentos_leidos": 1, "error": None})
    rep = {"cabecera": {"fecha_utc": "2026-01-06 00:00:00Z", "desde": "2026-01-01", "hasta": "2026-01-31",
                        "base": "http://127.0.0.1:1/qn", "env": "main", "patron": "market.*", "max_symbols": 0,
                        "gap": 3, "peticiones": [], "comando": "x", "cmd_gpu": CMD_GPU},
           "topics": {"market.x": tema, "market.y": {"kind": "object", "lectura": "/objects/market.y",
                                                     "error": "HTTP 400: prueba | con barra"}}}
    md = render_md(rep)
    assert "| topic |" in md and "## Consultas reproducibles" in md and "## GPU de los nodos: pendiente" in md, md
    assert "ERROR: HTTP 400: prueba / con barra" in md and "| market.x |" in md
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2024-01-01")
    ap.add_argument("--hasta", default=date.today().isoformat())
    ap.add_argument("--gap", type=int, default=3, help="huecos de al menos N días hábiles")
    ap.add_argument("--topics", default="market.*", help="patrón de nombres de topic (fnmatch)")
    ap.add_argument("--max-symbols", type=int, default=0, help="instrumentos por topic como máximo (0 = todos)")
    ap.add_argument("--json", help="guardar el inventario completo en este fichero")
    ap.add_argument("--informe", help="escribir el informe Markdown en este fichero")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0

    base = os.environ.get("QN_URLS", "").split(",")[0].strip().rstrip("/")
    acceso = os.environ.get("QN_TOKEN", "").strip()
    env = os.environ.get("QN_ENV", "").strip() or "main"
    if not base or not acceso:
        print("Faltan QN_URLS o QN_TOKEN", file=sys.stderr)
        return 2
    desde, hasta = date.fromisoformat(a.desde), date.fromisoformat(a.hasta)
    if desde > hasta:
        print("--desde es posterior a --hasta", file=sys.stderr)
        return 2

    peticiones: list = []
    report = {"cabecera": {
        "fecha_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"), "desde": desde.isoformat(),
        "hasta": hasta.isoformat(), "base": base, "env": env, "patron": a.topics, "max_symbols": a.max_symbols,
        "gap": a.gap, "peticiones": peticiones, "cmd_gpu": CMD_GPU,
        "comando": ".venv/Scripts/python -X utf8 scripts/inventario_options_chain.py " + shlex.join(sys.argv[1:])},
        "gpu": {"estado": "pendiente", "comando_por_nodo": CMD_GPU}, "topics": {}}

    topics = get(base, acceso, env, "/topics", {}, peticiones).get("topics", [])
    elegidos = sorted((t for t in topics if fnmatch.fnmatchcase(t["topic"], a.topics)), key=lambda t: t["topic"])
    if not elegidos:
        print(f"ningún topic de {len(topics)} coincide con {a.topics!r}", file=sys.stderr)
        return 1
    print(f"topics listados: {len(topics)}; con el patrón {a.topics!r}: {len(elegidos)}")
    for info in elegidos:
        nombre = info["topic"]
        try:
            r = inventariar(base, acceso, env, info, a, desde, hasta, peticiones)
        except Exception as e:  # un topic con fallo no aborta los demás: queda registrado en el informe
            r = {"kind": info.get("kind"), "lectura": None, "error": f"{type(e).__name__}: {e}"}
        report["topics"][nombre] = r
        print(linea(nombre, r, a.gap))

    con_datos = [t for t in report["topics"].values() if t.get("primera")]
    if con_datos:
        print(f"\ntopics con datos: {len(con_datos)}; primera fecha global: {min(t['primera'] for t in con_datos)}")
    errores = [n for n, t in report["topics"].items() if t.get("error")]
    if errores:
        print(f"topics con error ({len(errores)}): {', '.join(errores)}")
    if a.json:
        escribir(a.json, json.dumps(report, ensure_ascii=False, indent=2), acceso)
        print(f"inventario guardado en {a.json}")
    if a.informe:
        escribir(a.informe, render_md(report), acceso)
        print(f"informe guardado en {a.informe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
