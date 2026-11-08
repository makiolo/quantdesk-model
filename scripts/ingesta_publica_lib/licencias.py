"""Verificacion de licencias ANTES de descargar (TI-13-PUB): reune evidencia, emite veredictos y escribe licencias.md.

Regla: licencia no verificable contra la evidencia => excluida, nunca supuesta. `descargar` solo baja datasets cuyo
veredicto en licencias.json sea 'verificada'.
"""
from __future__ import annotations

import json
import os
import re

from . import common as C
from . import registro as R

ARCHIVO_ESTADO = C.RUNS + "/licencias.json"

# Uso permitido por licencia (resumen del texto legal; el enlace de cada fila remite al original).
USOS = {
    "CC BY 4.0": ("si", "si", "si, con atribucion", "Citar a los autores, enlazar la licencia e indicar los cambios"),
    "Apache 2.0": ("si", "si", "si, con aviso de licencia", "Conservar el aviso de licencia y de copyright"),
    "MIT": ("si", "si", "si, con aviso de licencia", "Conservar el aviso de copyright y la licencia"),
    "CC BY-NC-SA 4.0": ("si (no comercial)", "NO", "solo bajo CC BY-NC-SA 4.0 y con atribucion",
                        "Atribuir a Binance Vision; derivados bajo la misma licencia"),
}
ALIAS_LIC = {"apache-2.0": "Apache 2.0", "cc-by-4.0": "CC BY 4.0"}


def _ext(evid_id: str) -> str:
    return ".json" if evid_id.startswith(("hf_", "zenodo_", "github_")) and not evid_id.endswith("readme") else ".txt"


def reunir_evidencias(previo: dict | None = None, refrescar: bool = False) -> dict:
    """Descarga (GET) cada pagina de ficha o terminos a E:/.../_licencias y registra url, sha256 y fecha de consulta."""
    previas = (previo or {}).get("evidencias", {})
    urls = dict(R.URL_EVIDENCIAS)
    urls.update({f"zenodo_{z}": f"https://zenodo.org/api/records/{z}" for z in R.zenodo_ids()})
    ev = {}
    for eid, url in sorted(urls.items()):
        ruta = f"{C.EVIDENCIAS}/{eid}{_ext(eid)}"
        p = previas.get(eid)
        # se reutiliza la evidencia ya consultada (con su fecha), incluida una que fallo: --refrescar la vuelve a pedir
        if p and not refrescar and (p.get("error") or (os.path.isfile(ruta) and C.sha256_fichero(ruta) == p.get("sha256"))):
            ev[eid] = p
            continue
        reg = {"url": url, "ruta": ruta, "fecha_utc": C.ahora_utc(), "status": None, "error": None, "sha256": None, "bytes": 0}
        try:
            r = C.http_get(url, permitir=(404,), destino=ruta, cabeceras={"Accept": "application/json, text/plain, */*"})
            reg.update(status=r["status"], bytes=r["bytes"], sha256=C.sha256_fichero(ruta))
        except C.ErrorRed as e:
            reg["error"] = str(e)
        ev[eid] = reg
        print(f"  evidencia {eid}: {reg['status'] or 'ERROR'} {reg['bytes']} B {reg['error'] or ''}".rstrip())
    return ev


def _texto(ev: dict, eid: str) -> str:
    r = ev.get(eid) or {}
    if not r.get("sha256") or not os.path.isfile(r["ruta"]):
        return ""
    with open(r["ruta"], encoding="utf-8", errors="replace") as f:
        return f.read()


def _json(ev: dict, eid: str):
    t = _texto(ev, eid)
    if not t:
        return None
    try:
        return json.loads(t)
    except ValueError:
        return None


def _norm(lic: str | None) -> str | None:
    return None if not lic else ALIAS_LIC.get(lic.strip().lower(), lic.strip())


def declarada_en_tarjeta(api: dict | None, d: dict) -> tuple:
    """(licencia declarada, enlace/homepage) para un dataset del Hub; None si la tarjeta no la declara."""
    if not api:
        return None, None
    card = api.get("cardData") or {}
    if d["fuente"] == "lotsa":
        return _norm(card.get("license")), None
    for it in card.get("dataset_info") or []:
        if it.get("config_name") == d["nombre"]:
            return _norm(it.get("license")), it.get("homepage")
    return None, None


def veredicto_hf(d: dict, ev: dict) -> dict:
    api = _json(ev, "hf_chronos_api" if d["fuente"] == "chronos" else "hf_lotsa_api")
    repo = d["repo"]
    out = {"id": d["id"], "enlace": f"https://huggingface.co/datasets/{repo}", "origen": None, "origen_enlace": None,
           "estado": "excluida", "motivo": ""}
    decl, home = declarada_en_tarjeta(api, d)
    out["licencia"] = decl
    out["homepage"] = home
    if api is None:
        out["motivo"] = "No se pudo leer la ficha del dataset en el Hub: licencia no verificable"
        return out
    out["revision"] = api.get("sha")
    if decl is None:
        card_lic = _norm((api.get("cardData") or {}).get("license"))
        origen = ""
        if d["nombre"].startswith("m4_") and (ev.get("github_m4_licencia") or {}).get("status") == 404:
            origen = "; el origen M4-methods (GitHub) no tiene LICENSE (API de licencias: 404)"
        out["motivo"] = (f"La tarjeta no declara licencia para el subconjunto (licencia del repo: '{card_lic}'; el README "
                         f"remite a la licencia de cada config, que falta){origen}: no verificable")
        return out
    if d["lic_tarjeta"] is None or _norm(d["lic_tarjeta"]) != decl:
        out["motivo"] = f"La licencia declarada ({decl}) no coincide con la esperada en el registro ({d['lic_tarjeta']}): revisar"
        return out
    if d.get("zenodo"):
        z = _json(ev, f"zenodo_{d['zenodo']}")
        out["origen_enlace"] = f"https://zenodo.org/records/{d['zenodo']}"
        zl = ((z or {}).get("metadata") or {}).get("license", {}).get("id") if z else None
        out["origen"] = _norm(zl)
        out["origen_titulo"] = ((z or {}).get("metadata") or {}).get("title") if z else None
        if _norm(zl) != "CC BY 4.0":
            out["motivo"] = f"Licencia de origen en Zenodo no verificada como CC BY 4.0 (leida: {zl})"
            return out
    out["estado"] = "verificada"
    out["motivo"] = "Licencia declarada en la tarjeta" + (" y confirmada en el registro de origen (Zenodo)" if d.get("zenodo") else "")
    return out


def veredicto_binance(d: dict, ev: dict) -> dict:
    t = _texto(ev, "binance_terms")
    out = {"id": d["id"], "licencia": None, "enlace": "https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md",
           "origen": None, "origen_enlace": None, "estado": "excluida", "motivo": ""}
    if "CC BY-NC-SA 4.0" in t and "NON-COMMERCIAL LICENSE GRANT" in t:
        out.update(licencia="CC BY-NC-SA 4.0", estado="verificada",
                   motivo="Terminos del dataset (Binance Vision Dataset Terms v1.0, 2026-08-26): CC BY-NC-SA 4.0; "
                          "backtesting personal no productivo permitido; uso comercial excluido (3.4, 4.1-4.4)")
    else:
        out["motivo"] = "No se pudieron leer los terminos del dataset de Binance Vision: licencia no verificable"
    return out


def no_obtenidas(ev: dict) -> dict:
    """Stooq, Yahoo y FRED: estado y motivo con su evidencia."""
    out = {}
    yr, yt = _texto(ev, "yahoo_robots"), _texto(ev, "yahoo_terms")
    robots_yahoo = bool(re.search(r"(?im)^user-agent:\s*\*\s*\r?\n\s*disallow:\s*/\s*$", yr))
    terminos_yahoo = "automated means" in yt and "express, prior permission" in yt
    out["yahoo"] = {
        "estado": "excluida",
        "motivo": ("Los terminos de Yahoo prohiben acceder o recoger datos 'using any automated means ... without our express, "
                   "prior permission' y robots.txt de query1.finance.yahoo.com declara 'User-agent: * / Disallow: /'. "
                   "No se fuerza." if (robots_yahoo or terminos_yahoo) else "No se pudo leer robots.txt ni los terminos: licencia no verificable"),
        "robots_prohibe": robots_yahoo, "terminos_prohiben_automatizado": terminos_yahoo,
        "evidencias": ["yahoo_robots", "yahoo_terms"],
        "enlace": "https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html",
    }
    sr = _texto(ev, "stooq_robots")
    robots_stooq = bool(re.search(r"(?im)^user-agent:\s*\*\s*\r?\n\s*disallow:\s*/\s*$", sr))
    out["stooq"] = {
        "estado": "excluida",
        "motivo": ("robots.txt de stooq.com solo permite Googlebot y Bingbot ('User-agent: * / Disallow: /'); ademas el 2026-11-08 "
                   "una unica peticion de diagnostico al CSV y a la pagina de descarga masiva devolvio un reto de verificacion "
                   "JavaScript anti-bot. No se fuerza ni se sortea." if robots_stooq else
                   "No se pudo leer robots.txt: licencia y acceso no verificables"),
        "robots_prohibe": robots_stooq, "evidencias": ["stooq_robots"], "enlace": "https://stooq.com/robots.txt",
    }
    fe = {k: ev.get(k) or {} for k in ("fred_robots", "fred_terms", "fred_csv_muestra")}
    errores = {k: v.get("error") for k, v in fe.items() if v.get("error")}
    bloqueado = bool(errores.get("fred_terms") or errores.get("fred_csv_muestra"))
    out["fred"] = {
        "estado": "excluida",
        "motivo": ("robots.txt de FRED ('User-agent: *', Crawl-delay: 1) no prohibe el CSV, pero el servidor cierra la conexion "
                   "(sin respuesta HTTP) o agota el tiempo en la pagina de terminos y en el CSV de muestra con el User-Agent del "
                   "proyecto, tras 3 reintentos con espera exponencial; es un bloqueo y no se sortea con otro agente. Sin "
                   "acceso a sus terminos la licencia no es verificable. Nota: algunas series de FRED tienen copyright de "
                   "terceros (p. ej. VIX de CBOE, indices ICE BofA)." if bloqueado else
                   "Accesible, pero esta ingesta no implementa FRED: terminos y copyright de terceros por serie sin verificar. "
                   "Nota: algunas series de FRED tienen copyright de terceros."),
        "bloqueado": bloqueado, "errores": errores, "evidencias": list(fe),
        "enlace": "https://fred.stlouisfed.org/legal/",
    }
    return out


def calcular(ev: dict) -> dict:
    ds = {}
    for d in R.DATASETS:
        ds[d["id"]] = veredicto_hf(d, ev)
    for d in R.BINANCE:
        ds[d["id"]] = veredicto_binance(d, ev)
    api_c, api_l = _json(ev, "hf_chronos_api") or {}, _json(ev, "hf_lotsa_api") or {}
    return {
        "fecha_utc": C.ahora_utc(), "evidencias": ev, "datasets": ds, "fuentes_no_obtenidas": no_obtenidas(ev),
        "revisiones": {"chronos": api_c.get("sha"), "lotsa": api_l.get("sha")},
    }


def cargar() -> dict | None:
    return C.leer_json(ARCHIVO_ESTADO)


def verificada(estado: dict | None, dataset_id: str) -> bool:
    return bool(estado) and (estado.get("datasets", {}).get(dataset_id) or {}).get("estado") == "verificada"


def destino_d11(d: dict) -> str:
    if d["clase"] == R.NO_FIN:
        return "tronco (intacta)"
    if d["clase"] == R.REAL:
        return "adaptadores"
    if d["fechas"] == R.FECHAS_REALES:
        return "tronco < corte; adaptadores >= corte"
    return "excluida del tronco (fechas no verificables)"


def veredicto_texto(d: dict, v: dict) -> str:
    if v["estado"] != "verificada":
        return "excluida"
    if d["clase"] == R.REAL:
        return "solo adaptadores"
    if d["clase"] == R.FIN and d["fechas"] != R.FECHAS_REALES:
        return "usable; excluida del tronco por D-11"
    return "usable en tronco" if d["clase"] == R.NO_FIN else "usable (tronco antes del corte, resto adaptadores)"


def escribir_md(estado: dict, ruta: str) -> None:
    ds = {d["id"]: d for d in R.DATASETS + R.BINANCE}
    L = ["# TI-13-PUB: licencias de las fuentes publicas", "",
         f"Consulta de licencias: {estado['fecha_utc']} (UTC). Generado por `scripts/ingesta_publica.py licencias`; cada fila sale de "
         "`E:/quantdesk-lab/runs/TI-13-PUB/licencias.json`, que cita la evidencia descargada (ruta y SHA-256 en la ultima seccion).",
         "Regla: licencia no verificable contra la evidencia => **excluida** (no se descarga). Orden: licencia primero, datos despues.", "",
         "## Tabla de licencias", "",
         "| Fuente | Dataset / subconjunto | Licencia declarada | Licencia de origen | Investigacion / comercial / redistribucion | Atribucion | Clase D-11 | Veredicto | Destino D-11 (registro) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for did, v in estado["datasets"].items():
        d = ds[did]
        uso = USOS.get(v.get("licencia") or "", ("-", "-", "-", "-"))
        origen = f"{v['origen']} ([Zenodo]({v['origen_enlace']}))" if v.get("origen") else "-"
        lic = f"{v['licencia']} ([ficha]({v['enlace']}))" if v.get("licencia") else f"sin licencia declarada ([ficha]({v['enlace']}))"
        if v["estado"] != "verificada":
            uso = ("-", "-", "-", "-")
        if d["fuente"] == "lotsa" and v["estado"] == "verificada":
            uso = ("si", "tratar como NO hasta aclarar (README de LOTSA: 'research purposes only')", uso[2], uso[3])
        tipo = {"no_fin": "no financiera", "fin": "financiera", "real": "real con fecha"}[d["clase"]]
        L.append(f"| {d['fuente']} | {d['nombre']} | {lic} | {origen} | {uso[0]} / {uso[1]} / {uso[2]} | {uso[3]} | {tipo} "
                 f"| {veredicto_texto(d, v)} | {destino_d11(d) if v['estado'] == 'verificada' else '-'} |")
    L += ["", "### Motivo de cada veredicto", ""]
    for did, v in estado["datasets"].items():
        L.append(f"- `{did}`: {v['estado']}. {v['motivo']}.")
    L += ["", "## Fuentes pedidas que no se obtienen", "", "| Fuente | Estado | Motivo | Enlace de consulta |", "|---|---|---|---|"]
    for k, v in estado["fuentes_no_obtenidas"].items():
        L.append(f"| {k} | {v['estado']} | {v['motivo']} | {v['enlace']} |")
    L += ["", "## Notas", "",
          "- **LOTSA:** la tarjeta del repo declara `apache-2.0`, pero el README limita la publicacion a 'research purposes only'. "
          "La correspondencia de cada subconjunto con su registro de Zenodo (Monash Time Series Forecasting Archive, CC BY 4.0) es "
          "por nombre y la respalda la Tabla 14 del paper de LOTSA (arXiv 2402.02592), que atribuye estos subconjuntos al repositorio Monash. "
          "Se aplica la condicion mas restrictiva.",
          "- **Chronos:** la licencia del repo es `other`; el README remite a la de cada config. Solo se usan configs con licencia declarada "
          "en la tarjeta; las que no la declaran (m4_daily, m4_monthly, training_corpus_kernel_synth_1m) quedan excluidas sin descargar.",
          "- **Binance Vision:** CC BY-NC-SA 4.0, no comercial; los terminos tratan como derivados los modelos entrenados con los datos "
          "(2.4). Decision de producto pendiente del usuario si quantdesk se usa comercialmente.",
          "- **FRED:** algunas series tienen copyright de terceros (CBOE, ICE BofA...); no se ingiere (ver tabla de fuentes no obtenidas).",
          "", "## Evidencia consultada", "", "| Id | URL | Estado | SHA-256 | Consulta (UTC) |", "|---|---|---|---|---|"]
    for eid, e in sorted(estado["evidencias"].items()):
        L.append(f"| {eid} | {e['url']} | {e['status'] if e['status'] else 'ERROR: ' + str(e['error'])[:80]} | "
                 f"{(e['sha256'] or '-')} | {e['fecha_utc']} |")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


def correr(refrescar: bool = False, md: str | None = None) -> dict:
    C.comprobar_discos()
    os.makedirs(C.EVIDENCIAS, exist_ok=True)
    previo = cargar()
    print("licencias: reuniendo evidencia (GET, 1 peticion/s por host)")
    ev = reunir_evidencias(previo, refrescar)
    estado = calcular(ev)
    C.escribir_json(ARCHIVO_ESTADO, estado)
    if md:
        escribir_md(estado, md)
    return estado
