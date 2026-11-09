"""Universos con nombre (TI-12-MT5, fase C): grupos de simbolos del broker resueltos contra un inventario y guardados
como fichero de datos versionado en el repo (`universos/universos.json`), con su fecha y su regla de seleccion.

    --simbolos @fx28              los 28 cruces del lago (fijos en el codigo, como siempre)
    --simbolos @fx60 | @metales_energia | @indices | @crypto | @crypto_alts | @continuo | @us_grandes

Reglas (sobre `ruta` del inventario, la carpeta del simbolo en el terminal):
- fx60: todo `Forex\\...` (Majors, Minors y Exotics).
- metales_energia: `Commodities\\Metals\\...` y `Commodities\\Energies\\Energies Spot\\...`.
- indices: `Indices\\Indices Spot\\...`.
- crypto: los que cuelgan directamente de `Crypto\\` (las 17 grandes del broker).
- crypto_alts: `Crypto\\Crypto Alts\\...`.
- continuo: la union de los cinco anteriores.
- us_grandes: los componentes del S&P 500 de `universos/sp500.csv` cruzados con la version de sesion normal del broker
  (`.NYSE`, `.NAS`, `.US`; nunca la `-24`). Clases de accion: el punto del ticker (BRK.B) se busca como `-` y como `/`.
Fuera siempre: lo que tiene vencimiento (sufijos de mes y ano como `_Z6`, `_H7`, `SIN26`, o `_CFD`), los bonos (todos
con vencimiento) y `Stohastic` (indices sinteticos del broker).
"""
from __future__ import annotations

import csv
import io
import json
import os
import re

from . import calendarios as CAL

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "universos")
RUTA_UNIVERSOS = os.path.join(CARPETA, "universos.json")
RUTA_SP500 = os.path.join(CARPETA, "sp500.csv")
FORMATO = "quantdesk-lab.mt5-universos/v1"
GRUPOS = ("fx60", "metales_energia", "indices", "crypto", "crypto_alts", "continuo", "us_grandes")
CLASE_GRUPO = {"fx60": "forex", "metales_energia": "metales_energia", "indices": "indices", "crypto": "crypto",
               "crypto_alts": "crypto", "us_grandes": "acciones_us"}
REGLAS = {
    "fx60": "ruta Forex\\* (Majors, Minors, Exotics)",
    "metales_energia": "ruta Commodities\\Metals\\* o Commodities\\Energies\\Energies Spot\\*, sin vencimiento",
    "indices": "ruta Indices\\Indices Spot\\*, sin vencimiento",
    "crypto": "ruta Crypto\\<simbolo> (directamente bajo Crypto: las grandes del broker)",
    "crypto_alts": "ruta Crypto\\Crypto Alts\\*",
    "continuo": "union de fx60, metales_energia, indices, crypto y crypto_alts",
    "us_grandes": "componentes del S&P 500 (sp500.csv) con su simbolo de sesion normal .NYSE/.NAS/.US (no -24)",
}
# Vencimiento en el nombre: `_Z6`, `_H7`, `_Z6_CFD`, `GCG27_CFD`, `WheatZ6_CFD`. Los futuros sin marca en el nombre
# (`SIN26`) tambien quedan fuera, porque estan en carpetas de futuros (`Metal Futures`, `Energies Futures`, `Indices Futures`).
VENCIMIENTO = re.compile(r"(_[FGHJKMNQUVXZ]\d{1,2}(_CFD)?|_CFD)$")
FUERA = ("Bonds CFDs", "Stohastic")
SUFIJOS_US = {"NYSE": (".NYSE", ".NAS", ".US"), "NASDAQ": (".NAS", ".NYSE", ".US")}


def _partes(d: dict) -> list[str]:
    return [p for p in str(d.get("ruta") or "").split("\\") if p]


def con_vencimiento(simbolo: str) -> bool:
    return bool(VENCIMIENTO.search(simbolo))


def grupo_de(d: dict) -> str | None:
    """Grupo (sin us_grandes) de una fila del inventario, o None."""
    r, s = _partes(d), d["simbolo"]
    if not r or r[0] in FUERA or con_vencimiento(s):
        return None
    if r[0] == "Forex":
        return "fx60"
    if r[0] == "Commodities" and (r[1:2] == ["Metals"] or r[1:3] == ["Energies", "Energies Spot"]):
        return "metales_energia"
    if r[0] == "Indices" and r[1:2] == ["Indices Spot"]:
        return "indices"
    if r[0] == "Crypto":
        return "crypto_alts" if r[1:2] == ["Crypto Alts"] else "crypto" if len(r) == 2 else None
    return None


def clase_de(d: dict) -> str | None:
    """Clase de sesion de una fila del inventario (forex, metales_energia, indices, crypto, acciones_us) o None."""
    g = grupo_de(d)
    if g is not None:
        return CLASE_GRUPO[g]
    r = _partes(d)
    if r[:1] == ["Stock CFD's"] and r[1:2] and r[1] in ("NYSE", "Nasdaq", "Other US") and not d["simbolo"].endswith("-24"):
        return "acciones_us"
    return None


# ---------------------------------------------------------------------------------------------------------------------
# S&P 500
# ---------------------------------------------------------------------------------------------------------------------

def sp500_desde_wikitext(texto: str) -> list[dict]:
    """Filas (ticker, nombre, bolsa, sector, fecha_alta) de la tabla `constituents` del wikitext de la Wikipedia
    'List of S&P 500 companies'."""
    i = texto.index('id="constituents"')
    tabla = texto[i:texto.index("\n|}", i)]
    filas = []
    for bloque in tabla.split("\n|-")[1:]:
        celdas = [c.strip() for c in re.split(r"\n\|\|?|\|\|", bloque) if c.strip()]
        m = re.match(r"\{\{(Nyse|Nasdaq|BZX)\s*(?:Symbol|link)\|([^}|]+)", celdas[0], flags=re.I) if celdas else None
        if not m:
            continue
        nombre = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", celdas[1]).strip()
        bolsa = {"NYSE": "NYSE", "NASDAQ": "NASDAQ"}.get(m.group(1).upper(), "CBOE")
        filas.append({"ticker": m.group(2).strip(), "nombre": nombre, "bolsa": bolsa,
                      "sector": celdas[2] if len(celdas) > 2 else "", "fecha_alta": celdas[5] if len(celdas) > 5 else ""})
    return filas


def escribir_sp500(filas: list[dict], fuente: str, fecha: str, ruta: str = RUTA_SP500) -> None:
    buf = io.StringIO()
    buf.write(f"# Componentes del S&P 500. Fuente: {fuente}. Fecha de la instantanea: {fecha}. Filas: {len(filas)}.\n")
    w = csv.DictWriter(buf, fieldnames=["ticker", "nombre", "bolsa", "sector", "fecha_alta"], lineterminator="\n")
    w.writeheader()
    for f in sorted(filas, key=lambda f: f["ticker"]):
        w.writerow(f)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(buf.getvalue())


def leer_sp500(ruta: str = RUTA_SP500) -> tuple[list[dict], str]:
    with open(ruta, encoding="utf-8") as fh:
        cabecera = fh.readline().strip().lstrip("# ")
        return list(csv.DictReader(fh)), cabecera


def candidatos_us(ticker: str, bolsa: str) -> list[tuple[str, str]]:
    """(simbolo del broker, regla) en orden de preferencia. Clase de accion: BRK.B -> BRK-B o BRK/B."""
    raices = [(ticker, "ticker tal cual")]
    if "." in ticker:
        raices = [(ticker.replace(".", "-"), "clase con -"), (ticker.replace(".", "/"), "clase con /"),
                  (ticker.replace(".", ""), "clase sin separador")]
    return [(r + suf, f"{regla}, {suf}") for suf in SUFIJOS_US.get(bolsa, SUFIJOS_US["NYSE"]) for r, regla in raices]


def etiqueta_us(ticker: str) -> str:
    """Tag `symbol` propuesto para qn: el ticker con la clase separada por '-' (BRK-B), como yfinance."""
    return ticker.replace(".", "-")


def casar_sp500(sp500: list[dict], disponibles: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    casados, sin_casar = [], []
    for f in sp500:
        elegido = next(((s, r) for s, r in candidatos_us(f["ticker"], f["bolsa"]) if s in disponibles
                        and clase_de(disponibles[s]) == "acciones_us"), None)
        if elegido:
            casados.append({"ticker": f["ticker"], "nombre": f["nombre"], "simbolo": elegido[0], "regla": elegido[1],
                            "etiqueta": etiqueta_us(f["ticker"])})
            continue
        solo24 = sorted(s + "-24" for s, _ in candidatos_us(f["ticker"], f["bolsa"]) if s + "-24" in disponibles)
        sin_casar.append({"ticker": f["ticker"], "nombre": f["nombre"],
                          "motivo": "solo existe la version -24" if solo24 else "el broker no lo tiene",
                          "version_24": solo24[0] if solo24 else None})
    return casados, sin_casar


# ---------------------------------------------------------------------------------------------------------------------
# Resolucion y fichero
# ---------------------------------------------------------------------------------------------------------------------

def resolver(inventario: dict, sp500: list[dict], fuente_sp500: str, nombre_inventario: str) -> dict:
    disponibles = {d["simbolo"]: d for d in inventario["simbolos"]}
    grupos: dict[str, list[str]] = {g: [] for g in GRUPOS}
    excluidos = {"vencimiento": [], "bonos": 0, "stohastic": 0}
    for s, d in sorted(disponibles.items()):
        r = _partes(d)
        if r[:1] == ["Bonds CFDs"]:
            excluidos["bonos"] += 1
        elif r[:1] == ["Stohastic"]:
            excluidos["stohastic"] += 1
        elif r[:1] in (["Commodities"], ["Indices"], ["Crypto"], ["Forex"]) and (
                con_vencimiento(s) or any("Futures" in p for p in r)):
            excluidos["vencimiento"].append(s)
        g = grupo_de(d)
        if g:
            grupos[g].append(s)
    grupos["continuo"] = sorted(s for g in ("fx60", "metales_energia", "indices", "crypto", "crypto_alts") for s in grupos[g])
    casados, sin_casar = casar_sp500(sp500, disponibles)
    grupos["us_grandes"] = sorted({c["simbolo"] for c in casados})
    return {"formato": FORMATO, "tarea": "TI-12-MT5 fase C", "fecha": inventario["ahora_utc"][:10],
            "inventario": {"fichero": nombre_inventario, "ahora_utc": inventario["ahora_utc"],
                           "broker": (inventario.get("procedencia") or {}).get("broker"),
                           "simbolos_en_terminal": inventario.get("simbolos_en_terminal", len(disponibles))},
            "sp500": {"fichero": os.path.basename(RUTA_SP500), "fuente": fuente_sp500, "componentes": len(sp500),
                      "casados": len(casados), "sin_casar": len(sin_casar)},
            "reglas": REGLAS, "clase_por_grupo": CLASE_GRUPO, "excluidos": excluidos,
            "cuentas": {g: len(v) for g, v in grupos.items()}, "grupos": grupos,
            "etiquetas": {c["simbolo"]: c["etiqueta"] for c in casados},
            "us_grandes": {"casados": casados, "sin_casar": sin_casar}}


def guardar(doc: dict, ruta: str = RUTA_UNIVERSOS) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    os.replace(ruta + ".tmp", ruta)


def cargar(ruta: str = RUTA_UNIVERSOS) -> dict:
    try:
        with open(ruta, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as e:
        raise ValueError(f"no se pudo leer el fichero de universos {ruta}: {type(e).__name__}") from None
    if doc.get("formato") != FORMATO:
        raise ValueError(f"{ruta}: formato {doc.get('formato')!r}, se esperaba {FORMATO}")
    return doc


def grupo(nombre: str, doc: dict) -> list[str]:
    if nombre not in doc.get("grupos", {}):
        raise ValueError(f"@{nombre}: universo desconocido; hay @fx28 y {['@' + g for g in sorted(doc.get('grupos', {}))]}")
    return list(doc["grupos"][nombre])


def etiqueta(simbolo: str, base: str, doc: dict | None) -> str:
    """Tag `symbol` de qn: la base normalizada (EURUSD, XAUUSD, DE40, BTCUSD), salvo las acciones de us_grandes, que
    llevan su ticker (BRK-B). Para fx28 es la base, como siempre."""
    return ((doc or {}).get("etiquetas") or {}).get(simbolo, base)


def calendario(d: dict) -> tuple[str | None, str | None]:
    """(clase, bolsa) de una fila del inventario o de `simbolos_disponibles`."""
    c = clase_de(d)
    return c, CAL.bolsa_de(c, d.get("base", d["simbolo"]))
