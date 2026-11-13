"""Seleccion OC-03 y filtro determinista sobre mid; no red ni spot de respaldo.

Filtro por sesion, con Decimal para comparar precios y strikes sin epsilon
oculto. Semianchura=(ask-bid)/2; en CADA comparacion
tol=max(0.01, semianchuras de los 2 o 3 participantes). Solo se excluye si
la diferencia EXCEDE tol (igualdad admitida). Motivos de limpieza:
vencimiento_pasado, sin_cotizacion, monotonia, convexidad, calendario.
Una cotizacion exige bid finito >=0, ask finito >0 y ask>=bid. El volumen
no interviene. IV y last=0 son ausentes, bid=0 es valido.

Monotonia por (symbol, maturity, C/P): TODOS los pares de strikes, call no
creciente / put no decreciente. Convexidad: tres strikes consecutivos a<b<c;
hay violacion si mid_b supera la cuerda ((c-b)*mid_a+(b-a)*mid_c)/(c-a)+tol.
Esta definicion mide la mariposa en unidades de precio, incluso con strikes
no equiespaciados. En cada grupo se cuentan las violaciones de monotonia
y convexidad en que participa CADA contrato (los tres en una mariposa).
Se retira el de mayor cuenta; empate: mayor (ask-bid)/mid; empate: mayor
strike. Motivo: la regla con mas participaciones; empate: monotonia.
Se recalcula tras cada retirada hasta no tener violaciones. Despues se
aplica calendario por (symbol,C/P,strike), contando TODOS los pares de
vencimientos cuyo mid disminuye mas de tol. Misma regla de retirada;
empate final (strikes iguales): vencimiento mayor.

Tras strike y calendario se repite desde strike hasta punto fijo:
quitar un vecino de horquilla ancha puede revelar otra infraccion.
La primera regla que retira una fila fija su UNICO motivo; nunca se
reclasifica. Orden de grupos/strikes/vencimientos estable. No se alteran
precios ni se ajusta una superficie. Es una politica de descarte
conservadora, no una prueba de arbitraje economico con dividendos/tipos.
Maturity <= date se excluye como vencimiento_pasado: la captura OC-03 es
posterior al cierre de esa sesion, incluido el dia de vencimiento.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
from pathlib import Path
import re

from descarga_opciones import (ESQUEMA, INICIO, TAGS, cargar_json, json_texto, medianoche_ny, sha256)

VERSION = "ti-09-arch.lector/v1"
MOTOR = "quantdesk 69fdb39d"
OBLIGATORIOS = {(s, "ETF") for s in ("SPY", "QQQ", "IWM", "DIA")} | {(s, "INDEX") for s in ("^SPX", "^NDX", "^VIX")}
MOTIVOS = ("vencimiento_pasado", "sin_cotizacion", "monotonia", "convexidad", "calendario")
DESCARTES = ("sin_capture_id", "anterior_oc03", "fuera_rango_leido", "posterior_corte", "sesion_no_habil",
             "sin_captura_valida", "captura_no_elegida", "duplicado_exacto", "solo_contexto",
             "underlying_price_invalido", "strike_invalido", "capture_id_invalido", "fila_invalida")
CONTENIDO = TAGS + ("strike", "maturity", "last_price", "bid", "ask", "implied_vol", "in_the_money",
                    "volume", "open_interest", "date", "source", "captured_at", "capture_id", "underlying_price")
FILTRO = __doc__
CALENDARIO = {"version": "NYSE-ficha-2026-11-13/v1", "desde": "2026-11-12", "hasta": "2027-02-28",
              "holidays": ["2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15"],
              "medias_sesiones": ["2026-11-27", "2026-12-24"],
              "regla": "lunes-viernes salvo holidays; medias sesiones son habiles"}
MS_DIA = 86400000


def fecha(v):
    if not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        raise ValueError("fecha debe ser AAAA-MM-DD")
    return date.fromisoformat(v)


def ns_corte(v):
    """RFC3339 hasta ns sin conversion float. Fecha sola = 00:00 UTC."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        v += "T00:00:00Z"
    m = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})", v)
    if not m:
        raise ValueError("corte debe ser RFC3339 con zona (o fecha = 00:00 UTC)")
    d = datetime.fromisoformat(m[1] + m[3].replace("Z", "+00:00")) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (d.days * 86400 + d.seconds) * 10**9 + int((m[2] or "").ljust(9, "0"))


def dias(a, b):
    while a <= b:
        yield a
        a += timedelta(days=1)


def calendario_validado(cal, desde, hasta):
    cal = dict(cal)
    if fecha(cal["desde"]) > desde or fecha(cal["hasta"]) < hasta:
        raise ValueError("calendario NYSE no cubre el rango: proporcionar --calendario explicito")
    if not isinstance(cal.get("holidays"), list):
        raise ValueError("calendario exige holidays explicitos")
    holidays = {fecha(d) for d in cal["holidays"]}
    if "sessions" in cal:
        if not isinstance(cal["sessions"], list):
            raise ValueError("sessions debe ser lista explicita")
        sessions = {fecha(d) for d in cal["sessions"]}
        if sessions & holidays:
            raise ValueError("sesion tambien declarada festivo")
    else:
        sessions = {d for d in dias(fecha(cal["desde"]), fecha(cal["hasta"])) if d.weekday() < 5 and d not in holidays}
    cal["sessions"] = sorted(str(d) for d in sessions)
    return cal, sessions


def decimal(v):
    if isinstance(v, bool) or not isinstance(v, (int, float, str, Decimal)):
        raise ValueError("numero ausente o invalido")
    try:
        d = Decimal(str(v))
    except InvalidOperation:
        raise ValueError("numero invalido") from None
    if not d.is_finite():
        raise ValueError("numero no finito")
    return d


def numero_opcional(v):
    try:
        n = decimal(v)
        return float(n) if n > 0 else None
    except ValueError:
        return None


def strike_texto(v):
    d = decimal(v)
    if d <= 0:
        raise ValueError("strike debe ser positivo")
    s = format(d, "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def instrumento(r):
    return f"{r['symbol']}|{r['maturity']}|{r['_tipo']}|{strike_texto(r['strike'])}"


def identidad(r):
    return r["date"], instrumento(r)


def validar_fila(r):
    """Valida una fila; seleccionar convierte defectos de fila en descartes."""
    if not isinstance(r.get("symbol"), str) or not r["symbol"] or "|" in r["symbol"]:
        raise ValueError("symbol invalido")
    if r.get("asset_type") not in ("EQUITY", "ETF", "INDEX"):
        raise ValueError("asset_type invalido")
    if not isinstance(r.get("opt_type"), str) or r["opt_type"].lower() not in ("call", "put"):
        raise ValueError("opt_type invalido")
    if not isinstance(r.get("capture_id"), str) or not re.fullmatch(re.escape(r["date"]) + r"-\d{6}-[0-9a-f]{6}", r["capture_id"]):
        raise ValueError("capture_id no corresponde a date o formato OC-03")
    fecha(r["maturity"])
    strike_texto(r["strike"])
    cap = r.get("captured_at")
    if type(cap) is not int or cap <= 0:
        raise ValueError("captured_at debe ser entero epoch ns positivo")
    inicio = ns_corte(medianoche_ny(fecha(r["date"])))
    fin = ns_corte(medianoche_ny(fecha(r["date"]) + timedelta(days=1)))
    if not inicio <= cap < fin:
        raise ValueError("captured_at fuera de la sesion NY declarada")
    if decimal(r.get("underlying_price")) <= 0:
        raise ValueError("underlying_price ausente/invalido; no hay spot de respaldo")
    r["_tipo"] = "C" if r["opt_type"].lower() == "call" else "P"


def motivo_fila(r):
    """Lista cerrada, prioridad spot, strike, captura, resto de contenido."""
    for campo, motivo in (("underlying_price", "underlying_price_invalido"), ("strike", "strike_invalido")):
        try:
            if decimal(r.get(campo)) <= 0:
                return motivo
        except ValueError:
            return motivo
    if not isinstance(r.get("date"), str) or not isinstance(r.get("capture_id"), str) or not re.fullmatch(
            re.escape(r["date"]) + r"-\d{6}-[0-9a-f]{6}", r["capture_id"]):
        return "capture_id_invalido"
    try:
        validar_fila(r)
    except (ValueError, KeyError, TypeError):
        return "fila_invalida"
    return None


def cargar_volcado(raiz):
    raiz = Path(raiz).resolve()
    m = cargar_json((raiz / "manifest.json").read_text(encoding="utf-8"))
    if m.get("schema") != ESQUEMA or m.get("completo") is not True or m.get("topic") != "market.options.chain":
        raise ValueError("volcado incompleto o esquema/topic incompatible")
    if m.get("contexto_completo") is not True:
        raise ValueError("volcado sin contexto de cinco sesiones ni llegada al corte OC-03")
    lista = m.get("ficheros")
    if not isinstance(lista, list):
        raise ValueError("manifest sin ficheros")
    rows, vistos, combos = [], set(), set()
    # JSON-lines crea las mismas claves y cadenas de etiquetas por cada fila.
    # Compartirlas reduce memoria sin cambiar contenido ni tipos del volcado.
    campos, textos = {}, {}
    repetidos = set(TAGS) | {"maturity", "date", "source", "capture_id", "_batch_id"}
    for f in lista:
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
                if not isinstance(r, dict) or any(r.get(k) != f["etiquetas"][k] for k in TAGS):
                    raise ValueError("fila con tags distintos del manifiesto")
                if r.get("capture_id") and ("date" not in r or isinstance(r["date"], str) and r["date"] >= str(INICIO)) and any(
                        c not in r for c in CONTENIDO + ("_offset",)):
                    raise ValueError("esquema ausente: faltan campos OC-03")
                r = {campos.setdefault(k, k): textos.setdefault(v, v) if k in repetidos and isinstance(v, str) else v
                     for k, v in r.items()}
                rows.append(r)
                n += 1
        if n != f["filas"]:
            raise ValueError("numero de filas no coincide: " + f["ruta"])
    catalogo = {tuple(c[k] for k in TAGS) for c in m.get("catalogo", [])}
    if combos != catalogo:
        raise ValueError("catalogo y ficheros no coinciden")
    return m, rows, sha256(raiz / "manifest.json")


def seleccionar(rows, desde, hasta, corte, consulta_desde, sessions, *, copiar=True):
    """95% con enteros; cinco sesiones CON datos anteriores, sin mirar al futuro.

    Universo: union actual + cinco previas + los siete obligatorios. Distintos
    (symbol,asset_type); mas subyacentes, luego max captured_at, luego capture_id
    lexicografico mayor para que incluso un empate total sea determinista.
    """
    cuentas = Counter({m: 0 for m in DESCARTES})
    grupos = defaultdict(lambda: defaultdict(list))
    tipos = {}
    for original in rows:
        r = dict(original) if copiar else original
        if not r.get("capture_id"):
            cuentas["sin_capture_id"] += 1
            continue
        try:
            d = fecha(r["date"])
        except (ValueError, KeyError, TypeError):
            cuentas["fila_invalida"] += 1
            continue
        if d < INICIO:
            cuentas["anterior_oc03"] += 1
            continue
        if not consulta_desde <= d <= hasta:
            cuentas["fuera_rango_leido"] += 1
            continue
        motivo = motivo_fila(r)
        if motivo:
            cuentas[motivo] += 1
            continue
        if r["captured_at"] > corte or (r["captured_at"] + 999999) // 1000000 > corte // 1000000:
            cuentas["posterior_corte"] += 1
            continue
        if d not in sessions:
            cuentas["sesion_no_habil"] += 1
            continue
        previo = tipos.setdefault(r["symbol"], r["asset_type"])
        if previo != r["asset_type"]:
            raise ValueError("symbol publicado con asset_type contradictorio: " + r["symbol"])
        grupos[d][r["capture_id"]].append(r)
    observados = {d: {(r["symbol"], r["asset_type"]) for rs in caps.values() for r in rs} for d, caps in grupos.items()}
    if consulta_desde > INICIO and len([d for d in observados if d < desde]) < 5:
        raise ValueError("contexto insuficiente al corte: hacen falta cinco sesiones previas o llegar a OC-03")
    universo = set(OBLIGATORIOS).union(*observados.values())
    anteriores = []
    raw, decisiones, sin_valida = [], [], []
    for d in sorted(sessions & set(dias(consulta_desde, hasta))):
        contexto = anteriores[-5:]
        esperado = set(OBLIGATORIOS) | observados.get(d, set())
        for p in contexto:
            esperado |= observados[p]
        candidatos = []
        for cap, rs in sorted(grupos.get(d, {}).items()):
            n = len({(r["symbol"], r["asset_type"]) for r in rs})
            candidatos.append({"capture_id": cap, "subyacentes": n, "esperados": len(esperado),
                               "cobertura": n / len(esperado), "valida": n * 100 >= len(esperado) * 95,
                               "captured_at_max_ns": max(r["captured_at"] for r in rs), "filas": len(rs)})
        validos = [c for c in candidatos if c["valida"]]
        elegido = max(validos, key=lambda c: (c["subyacentes"], c["captured_at_max_ns"], c["capture_id"])) if validos else None
        if d >= desde:
            decisiones.append({"sesion": str(d), "capture_id": elegido["capture_id"] if elegido else None,
                               "motivo": "mas subyacentes; empate: captured_at max, luego capture_id" if elegido else "sin captura valida (ninguna >=95% o sin datos)",
                               "universo_esperado": [dict(symbol=s, asset_type=t) for s, t in sorted(esperado)],
                               "sesiones_contexto": [str(p) for p in contexto], "candidatas": candidatos})
            if not elegido:
                sin_valida.append(str(d))
            for cap, rs in grupos.get(d, {}).items():
                if elegido and cap == elegido["capture_id"]:
                    raw.extend(rs)
                else:
                    cuentas["captura_no_elegida" if elegido else "sin_captura_valida"] += len(rs)
        else:
            cuentas["solo_contexto"] += sum(len(rs) for rs in grupos.get(d, {}).values())
        if d in observados:
            anteriores.append(d)
    unicas = {}
    for r in raw:
        clave = identidad(r)
        if clave in unicas:
            if any(r.get(c) != unicas[clave].get(c) for c in CONTENIDO):
                raise ValueError("duplicado con distinto contenido: " + " | ".join(clave))
            cuentas["duplicado_exacto"] += 1
            if r["_offset"] < unicas[clave]["_offset"]:
                unicas[clave] = r
        else:
            unicas[clave] = r
    raw = [unicas[k] for k in sorted(unicas)]
    presentes = defaultdict(set)
    for r in raw:
        presentes[r["date"]].add((r["symbol"], r["asset_type"]))
    huecos = [{"symbol": s, "asset_type": t, "sesiones_sin_datos": [str(d) for d in sorted(sessions)
               if desde <= d <= hasta and (s, t) not in presentes[str(d)]]} for s, t in sorted(universo)]
    assert len(rows) == len(raw) + sum(cuentas.values())
    return raw, {"capturas": decisiones, "sesiones_sin_captura_valida": sin_valida,
                 "descartes_lector": dict(cuentas), "motivos_cerrados_lector": list(DESCARTES), "huecos_por_subyacente": huecos,
                 "universo_huecos": "union de subyacentes OC-03 leidos hasta corte + siete obligatorios; datos de captura elegida",
                 "regla_universo_captura": "union de sesion y 5 sesiones anteriores CON datos + siete obligatorios; umbral inclusivo 95%"}


def limpiar(raw):
    activos, motivos = {}, {}
    for r in raw:
        k = identidad(r)
        if r["maturity"] <= r["date"]:
            motivos[k] = "vencimiento_pasado"
            continue
        try:
            bid, ask = decimal(r.get("bid")), decimal(r.get("ask"))
            if bid < 0 or ask <= 0 or ask < bid:
                raise ValueError("sin cotizacion")
        except ValueError:
            motivos[k] = "sin_cotizacion"
            continue
        mid = (bid + ask) / 2
        activos[k] = {"row": r, "k": decimal(r["strike"]), "mid": mid, "hw": (ask - bid) / 2,
                      "rel": (ask - bid) / mid}

    def grupos(regla):
        gs = defaultdict(list)
        for key, v in activos.items():
            r = v["row"]
            g = (r["date"], r["symbol"], r["_tipo"], r["maturity"] if regla != "calendario" else v["k"])
            gs[g].append(key)
        for g in sorted(gs):
            yield sorted(gs[g], key=lambda k: activos[k]["k"] if regla != "calendario" else activos[k]["row"]["maturity"])

    def fase(regla):
        for keys in grupos(regla):
            while True:
                counts = defaultdict(Counter)
                pareja = "calendario" if regla == "calendario" else "monotonia"
                for i, a in enumerate(keys):
                    for b in keys[i + 1:]:
                        if viola((a, b), pareja):
                            counts[a][pareja] += 1
                            counts[b][pareja] += 1
                if regla != "calendario":
                    for ks in zip(keys, keys[1:], keys[2:]):
                        if viola(ks, "convexidad"):
                            for k in ks:
                                counts[k]["convexidad"] += 1
                if not counts:
                    break
                k = max(counts, key=lambda k: (sum(counts[k].values()), activos[k]["rel"], activos[k]["k"],
                                               activos[k]["row"]["maturity"]))
                motivos[k] = max(counts[k], key=lambda m: (counts[k][m], m == "monotonia"))
                del activos[k]
                keys.remove(k)

    def viola(ks, regla):
        vs = [activos[k] for k in ks]
        tol = max(Decimal("0.01"), *(v["hw"] for v in vs))
        a, b = vs[:2]
        if regla == "convexidad":
            c = vs[2]
            diferencia = b["mid"] - ((c["k"] - b["k"]) * a["mid"] + (b["k"] - a["k"]) * c["mid"]) / (c["k"] - a["k"])
        elif regla == "monotonia":
            diferencia = b["mid"] - a["mid"] if a["row"]["_tipo"] == "C" else a["mid"] - b["mid"]
        else:
            diferencia = a["mid"] - b["mid"]
        return diferencia > tol

    with localcontext() as ctx:
        ctx.prec = 50
        while True:
            n = len(activos)
            for regla in ("strike", "calendario"):
                fase(regla)
            if len(activos) == n:
                break
    clean = []
    for k in sorted(activos):
        v = activos.pop(k)
        r = {a: b for a, b in v["row"].items() if a != "_tipo"}
        r.update(mid=float(v["mid"]), implied_vol=numero_opcional(r.get("implied_vol")),
                 last_price=numero_opcional(r.get("last_price")))
        clean.append((v["row"], r))
    ledger = [{"sesion": k[0], "instrument": k[1], "motivo": motivos[k]} for k in sorted(motivos)]
    assert len(clean) + len(ledger) == len(raw)
    assert set(motivos.values()) <= set(MOTIVOS)
    return clean, ledger


def hash_dataset(tablas):
    lineas = sorted(f"{t['table_id']}:{t['schema']}:{t['logical_hash']}\n" for t in tablas)
    return "sha256:" + hashlib.sha256("".join(lineas).encode()).hexdigest()
