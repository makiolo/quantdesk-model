"""--verificar: recalcula SHA-256 de todo lo que citan los manifiestos y reaplica el filtro con el mismo --corte."""
from __future__ import annotations

import glob
import os
import shutil

from . import common as C
from . import filtro as FI
from . import fuentes as F
from . import licencias as L


def hashes(problemas: list) -> int:
    n = 0
    for d in (F.RAW_HF, F.RAW_BINANCE):
        for rel, e in F.manifiesto_crudo(d)["archivos"].items():
            ruta = f"{C.PUBLIC}/{rel}"
            n += 1
            if not os.path.isfile(ruta):
                problemas.append(f"falta {ruta}")
            elif os.path.getsize(ruta) != e["bytes"] or C.sha256_fichero(ruta) != e["sha256"]:
                problemas.append(f"hash o tamano distinto: {ruta}")
    lic = L.cargar() or {"evidencias": {}}
    for eid, e in lic["evidencias"].items():
        if e.get("sha256"):
            n += 1
            if not os.path.isfile(e["ruta"]) or C.sha256_fichero(e["ruta"]) != e["sha256"]:
                problemas.append(f"evidencia de licencia alterada: {eid}")
    for m in sorted(glob.glob(C.DATASETS + "/*/manifest.json")):
        man, carpeta = C.leer_json(m), os.path.dirname(m)
        for f in man["ficheros"]:
            n += 1
            ruta = f"{carpeta}/{f['ruta']}"
            if not os.path.isfile(ruta) or C.sha256_fichero(ruta) != f["sha256"] or os.path.getsize(ruta) != f["bytes"]:
                problemas.append(f"hash o tamano distinto: {ruta}")
        if C.hash_conjunto((f["ruta"], f["sha256"]) for f in man["ficheros"]) != man["dataset_sha256"]:
            problemas.append(f"dataset_sha256 no coincide con sus ficheros: {man['dataset']}")
        for c in man["crudo"]:
            if not os.path.isfile(f"{C.PUBLIC}/{c['ruta']}"):
                problemas.append(f"el manifiesto de {man['dataset']} cita un crudo ausente: {c['ruta']}")
    csv = (C.leer_json(C.INFORMES_FUERA + "/filtro_resumen.json") or {}).get("csv")
    if csv:
        n += 1
        if not os.path.isfile(csv["ruta"]) or C.sha256_fichero(csv["ruta"]) != csv["sha256"]:
            problemas.append(f"CSV del filtro alterado: {csv['ruta']}")
    return n


def refiltrar(problemas: list) -> int:
    """Reaplica el filtro (mismo --corte de cada manifiesto) sobre lo crudo en una carpeta temporal y compara hashes."""
    lic = L.cargar()
    mans = {os.path.basename(os.path.dirname(p)): C.leer_json(p) for p in glob.glob(C.DATASETS + "/*/manifest.json")}
    if not mans:
        return 0
    cortes = {m["corte"] for m in mans.values()}
    if len(cortes) != 1:
        problemas.append(f"los manifiestos usan cortes distintos: {sorted(cortes)}")
        return 0
    corte = cortes.pop()
    salida = C.TMP + "/verif"
    shutil.rmtree(salida, ignore_errors=True)
    try:
        nuevo = FI.correr(corte, lic, salida, ids=sorted(mans))["manifiestos"]
        for did, m in mans.items():
            n = nuevo.get(did)
            if n is None or n["dataset_sha256"] != m["dataset_sha256"] or n["contenido_sha256"] != m["contenido_sha256"]:
                problemas.append(f"el filtro reaplicado con corte {corte} da otro hash en {did}")
    finally:
        shutil.rmtree(salida, ignore_errors=True)
    return len(mans)


def correr(solo_hashes: bool = False) -> int:
    problemas = []
    n = hashes(problemas)
    print(f"verificar: {n} ficheros comprobados (SHA-256 y tamano)")
    mans = {os.path.basename(os.path.dirname(p)): C.leer_json(p) for p in glob.glob(C.DATASETS + "/*/manifest.json")}
    esc = FI.comprobar_escrito(C.DATASETS, mans)
    print(f"verificar: parquet releidos ({esc['filas_releidas']:,} filas): series_id en train y val {esc['ids_en_ambos_lados']}, "
          f"contenidos en train y val {esc['contenidos_en_ambos_lados']}")
    if esc["ids_en_ambos_lados"] or esc["contenidos_en_ambos_lados"]:
        problemas.append(f"particion no disjunta en los parquet: {esc}")
    if not solo_hashes:
        k = refiltrar(problemas)
        print(f"verificar: filtro reaplicado sobre {k} datasets")
    for p in problemas:
        print("  PROBLEMA:", p)
    print("verificar: OK" if not problemas else f"verificar: {len(problemas)} problemas")
    return 1 if problemas else 0
