"""Descarga reanudable e idempotente de lo crudo (Hub de Hugging Face y data.binance.vision) con guarda de presupuesto."""
from __future__ import annotations

import glob
import os
import re
import time
import xml.etree.ElementTree as ET

from . import common as C
from . import licencias as L
from . import registro as R

RAW_HF = C.PUBLIC + "/hf"
RAW_BINANCE = C.PUBLIC + "/binance"
ESPACIO = C.RUNS + "/espacio.json"
DESCARGAS = C.RUNS + "/descargas.json"


def manifiesto_crudo(fuente_dir: str) -> dict:
    return C.leer_json(fuente_dir + "/raw_manifest.json", {"archivos": {}})


def bytes_en_manifiestos() -> int:
    """Suma de bytes del crudo (raw_manifest.json de cada fuente) y de lo procesado (manifest.json de cada dataset)."""
    total = 0
    for d in (RAW_HF, RAW_BINANCE):
        total += sum(e["bytes"] for e in manifiesto_crudo(d)["archivos"].values())
    for m in glob.glob(C.DATASETS + "/*/manifest.json"):
        total += sum(f["bytes"] for f in (C.leer_json(m) or {}).get("ficheros", []))
    return total


def medir_espacio(fuente: str, fase: str) -> dict:
    """Registra el espacio libre de C: y E: y los bytes de los manifiestos antes/despues de cada fuente."""
    reg = {"fuente": fuente, "fase": fase, "fecha_utc": C.ahora_utc(), "libre_C_bytes": C.libre("C:/"),
           "libre_E_bytes": C.libre("E:/"), "usado_manifiestos_bytes": bytes_en_manifiestos(),
           "cache_hf_bytes": C.bytes_cache_hf()}
    hist = C.leer_json(ESPACIO, [])
    hist.append(reg)
    C.escribir_json(ESPACIO, hist)
    return reg


def _registrar(fuente_dir: str, rel: str, entrada: dict) -> None:
    m = manifiesto_crudo(fuente_dir)
    m["archivos"][rel] = entrada
    C.escribir_json(fuente_dir + "/raw_manifest.json", m)


def _guarda(extra: int) -> None:
    C.guarda(extra, bytes_en_manifiestos(), C.bytes_cache_hf())


# --- Hub -------------------------------------------------------------------------------------------------------------

def _siblings(estado_lic: dict, clave: str) -> dict:
    ev = estado_lic["evidencias"]["hf_%s_api" % clave]
    api = L._json(estado_lic["evidencias"], "hf_%s_api" % clave)
    if not api:
        raise RuntimeError(f"falta la evidencia {ev['ruta']}: ejecutar 'licencias'")
    return {s["rfilename"]: s for s in api["siblings"]}, api["sha"]


def descargar_hub(fuente: str, estado_lic: dict, forzar_ids: list | None = None) -> list:
    """Baja de `fuente` ('chronos'|'lotsa') solo los datasets con licencia verificada. Devuelve [(id, motivo)] no bajados."""
    from huggingface_hub import hf_hub_download

    sib, revision = _siblings(estado_lic, fuente)
    omitidos = []
    for d in R.DATASETS:
        if d["fuente"] != fuente or (forzar_ids and d["id"] not in forzar_ids):
            continue
        if not L.verificada(estado_lic, d["id"]):
            omitidos.append((d["id"], "licencia: " + estado_lic["datasets"][d["id"]]["motivo"]))
            print(f"  OMITIDO {d['id']}: licencia no verificada")
            continue
        for rel in d["archivos"] + d["extras"]:
            s = sib.get(rel)
            if s is None:
                omitidos.append((d["id"], f"{rel} no existe en el repo"))
                continue
            _bajar_hub(d, rel, s, revision, hf_hub_download)
    return omitidos


def _bajar_hub(d: dict, rel: str, s: dict, revision: str, hf_hub_download) -> None:
    local_dir = f"{RAW_HF}/{d['repo']}"
    destino = f"{local_dir}/{rel}"
    clave = f"hf/{d['repo']}/{rel}"
    esperado_lfs = (s.get("lfs") or {}).get("sha256")
    prev = manifiesto_crudo(RAW_HF)["archivos"].get(clave)
    if prev and os.path.isfile(destino) and os.path.getsize(destino) == prev["bytes"] and C.sha256_fichero(destino) == prev["sha256"]:
        return  # idempotente: ya esta con el hash registrado
    _guarda(int(s["size"]))
    t0 = time.monotonic()
    ruta = hf_hub_download(d["repo"], rel, repo_type="dataset", revision=revision, local_dir=local_dir, token=False)
    h = C.sha256_fichero(ruta)
    if esperado_lfs:
        if h != esperado_lfs:
            os.remove(ruta)
            raise RuntimeError(f"{rel}: sha256 {h} != LFS del Hub {esperado_lfs}")
    else:
        with open(ruta, "rb") as f:
            if C.git_blob_sha1(f.read()) != s["blobId"]:
                os.remove(ruta)
                raise RuntimeError(f"{rel}: blob sha1 distinto de blobId del Hub")
    _registrar(RAW_HF, clave, {
        "bytes": os.path.getsize(ruta), "sha256": h, "url": f"https://huggingface.co/datasets/{d['repo']}/resolve/{revision}/{rel}",
        "revision": revision, "verificado_contra": "LFS sha256 del Hub" if esperado_lfs else "git blob id del Hub",
        "fecha_descarga_utc": C.ahora_utc(), "fuente": "hub:" + d["repo"],
    })
    print(f"  {rel}: {os.path.getsize(ruta) / 1e6:.1f} MB en {time.monotonic() - t0:.1f}s")
    time.sleep(C.PAUSA_HOST)


# --- Binance ---------------------------------------------------------------------------------------------------------

def listar_s3(prefijo: str) -> list:
    """[(clave, bytes)] del prefijo en el bucket publico (ListObjects v1, con marcador)."""
    claves, marcador = [], ""
    while True:
        url = f"{R.BINANCE_S3}?delimiter=/&prefix={prefijo}" + (f"&marker={marcador}" if marcador else "")
        r = C.http_get(url)
        raiz = ET.fromstring(r["cuerpo"])
        ns = {"s": raiz.tag.split("}")[0].strip("{")}
        for c in raiz.findall("s:Contents", ns):
            claves.append((c.find("s:Key", ns).text, int(c.find("s:Size", ns).text)))
        trunc = raiz.find("s:IsTruncated", ns)
        if trunc is None or trunc.text != "true":
            return claves
        marcador = claves[-1][0]


def parse_checksum(texto: str) -> str:
    """El .CHECKSUM de Binance es '<sha256>  <fichero>'."""
    m = re.match(r"\s*([0-9a-fA-F]{64})\b", texto)
    if not m:
        raise ValueError("CHECKSUM ilegible: " + texto[:80])
    return m.group(1).lower()


def zips_a_bajar(par: str, intervalo: str) -> list:
    """Mensuales completos + diarios del mes aun sin zip mensual. [(clave, bytes)] solo de .zip."""
    pref = f"data/spot/monthly/klines/{par}/{intervalo}/"
    meses = [(k, n) for k, n in listar_s3(pref) if k.endswith(".zip")]
    ultimo = max((re.search(r"(\d{4}-\d{2})\.zip$", k).group(1) for k, _ in meses), default="0000-00")
    dias = [(k, n) for k, n in listar_s3(f"data/spot/daily/klines/{par}/{intervalo}/") if k.endswith(".zip")
            and re.search(r"(\d{4}-\d{2})-\d{2}\.zip$", k).group(1) > ultimo]
    return meses + dias


def _bajar_binance(clave: str, tam: int) -> None:
    destino = f"{RAW_BINANCE}/{clave}"
    rel = f"binance/{clave}"
    prev = manifiesto_crudo(RAW_BINANCE)["archivos"].get(rel)
    if prev and os.path.isfile(destino) and os.path.getsize(destino) == prev["bytes"]:
        return
    _guarda(tam)
    esp_txt = C.http_get(f"{R.BINANCE_BASE}/{clave}.CHECKSUM")["cuerpo"].decode("utf-8", "replace")
    esperado = parse_checksum(esp_txt)
    C.http_get(f"{R.BINANCE_BASE}/{clave}", destino=destino)
    h = C.sha256_fichero(destino)
    if h != esperado:
        os.remove(destino)
        raise RuntimeError(f"{clave}: sha256 {h} != .CHECKSUM {esperado}")
    with open(destino + ".CHECKSUM", "w", encoding="utf-8") as f:
        f.write(esp_txt)
    _registrar(RAW_BINANCE, rel, {
        "bytes": os.path.getsize(destino), "sha256": h, "url": f"{R.BINANCE_BASE}/{clave}",
        "verificado_contra": ".CHECKSUM de Binance (sha256)", "checksum_sha256": esperado,
        "fecha_descarga_utc": C.ahora_utc(), "fuente": "binance",
    })


def descargar_binance(estado_lic: dict, max_pares: int | None = None) -> list:
    omitidos = []
    for d in R.BINANCE:
        if not L.verificada(estado_lic, d["id"]):
            omitidos.append((d["id"], "licencia: " + estado_lic["datasets"][d["id"]]["motivo"]))
            print(f"  OMITIDO {d['id']}: licencia no verificada")
            continue
        for par in d["pares"][:max_pares]:
            try:
                zips = zips_a_bajar(par, d["intervalo"])
            except C.ErrorRed as e:
                omitidos.append((f"{d['id']}:{par}", f"listado: {e}"))
                continue
            print(f"  {par} {d['intervalo']}: {len(zips)} ficheros ({sum(n for _, n in zips) / 1e6:.1f} MB)")
            for clave, tam in zips:
                try:
                    _bajar_binance(clave, tam)
                except C.ErrorRed as e:
                    omitidos.append((clave, str(e)))
    return omitidos


def descargar(fuente: str, estado_lic: dict, max_pares: int | None = None) -> dict:
    """Orquesta una fuente: mide espacio antes y despues y devuelve {omitidos}."""
    medir_espacio(fuente, "antes")
    if fuente in ("chronos", "lotsa"):
        omit = descargar_hub(fuente, estado_lic)
    else:
        omit = descargar_binance(estado_lic, max_pares)
    medir_espacio(fuente, "despues")
    hist = C.leer_json(DESCARGAS, {})
    hist[fuente] = {"fecha_utc": C.ahora_utc(), "no_bajados": omit}
    C.escribir_json(DESCARGAS, hist)
    return {"omitidos": omit}
