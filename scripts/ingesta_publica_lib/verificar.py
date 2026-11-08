"""--verificar: recalcula SHA-256 de todo lo que citan los manifiestos, contrasta lo procesado con lo esperado y reaplica el filtro.

Falla (sale 1) si no hay nada que verificar, si falta un dataset esperado, si el numero de filas de un parquet no coincide con el
manifiesto, si un hash no coincide o si el filtro reaplicado con el mismo --corte da otro hash.
"""
from __future__ import annotations

import glob
import os
import shutil

import pyarrow.parquet as pq

from . import common as C
from . import filtro as FI
from . import fuentes as F
from . import licencias as L


def cargar_manifiestos(datasets_dir: str) -> dict:
    return {os.path.basename(os.path.dirname(p)): C.leer_json(p) for p in sorted(glob.glob(datasets_dir + "/*/manifest.json"))}


def verificar_datasets(datasets_dir: str, esperados: set, problemas: list) -> int:
    """Comprueba los datasets procesados de `datasets_dir` contra los `esperados` (ids). Devuelve los ficheros comprobados."""
    mans = cargar_manifiestos(datasets_dir)
    if not mans:
        problemas.append(f"no hay manifiestos en {datasets_dir}: no hay nada que verificar")
    for falta in sorted(set(esperados) - set(mans)):
        problemas.append(f"falta el dataset esperado (licencia verificada y crudo completo): {falta}")
    for sobra in sorted(set(mans) - set(esperados)):
        problemas.append(f"dataset procesado que no se esperaba: {sobra}")
    n = filas_total = filas_manifiestos = 0
    for did, man in mans.items():
        carpeta = f"{datasets_dir}/{did}"
        por_parte = {"tronco": 0, "adaptadores": 0}
        for f in man["ficheros"]:
            n += 1
            ruta = f"{carpeta}/{f['ruta']}"
            filas_manifiestos += f["filas"]
            if not os.path.isfile(ruta):
                problemas.append(f"falta {ruta}")
                continue
            if os.path.getsize(ruta) != f["bytes"] or C.sha256_fichero(ruta) != f["sha256"]:
                problemas.append(f"hash o tamano distinto: {ruta}")
            try:
                filas = pq.ParquetFile(ruta).metadata.num_rows
            except Exception as e:  # noqa: BLE001 - un parquet ilegible es un problema, no una excepcion
                problemas.append(f"parquet ilegible {ruta}: {type(e).__name__}: {e}")
                continue
            filas_total += filas
            por_parte[f["parte"]] = por_parte.get(f["parte"], 0) + filas
            if filas != f["filas"]:
                problemas.append(f"filas distintas en {ruta}: {filas} en el parquet, {f['filas']} en el manifiesto")
        for parte, clave in (("tronco", "puntos_tronco"), ("adaptadores", "puntos_adaptadores")):
            if por_parte[parte] != man["filtro"][clave]:
                problemas.append(f"{did}: {por_parte[parte]} filas de {parte} en los parquet, {man['filtro'][clave]} en el informe del filtro")
        if C.hash_conjunto((f["ruta"], f["sha256"]) for f in man["ficheros"]) != man["dataset_sha256"]:
            problemas.append(f"dataset_sha256 no coincide con sus ficheros: {did}")
        for c in man["crudo"]:
            if not os.path.isfile(f"{C.PUBLIC}/{c['ruta']}"):
                problemas.append(f"el manifiesto de {did} cita un crudo ausente: {c['ruta']}")
    if filas_total != filas_manifiestos:
        problemas.append(f"total de filas: {filas_total} en los parquet, {filas_manifiestos} en los manifiestos")
    return n


def hashes(problemas: list, esperados: set) -> int:
    n = 0
    for d in (F.RAW_HF, F.RAW_BINANCE):
        for rel, e in F.manifiesto_crudo(d)["archivos"].items():
            ruta = f"{C.PUBLIC}/{rel}"
            n += 1
            if not os.path.isfile(ruta):
                problemas.append(f"falta {ruta}")
            elif os.path.getsize(ruta) != e["bytes"] or C.sha256_fichero(ruta) != e["sha256"]:
                problemas.append(f"hash o tamano distinto: {ruta}")
    if n == 0:
        problemas.append("los raw_manifest.json no citan ningun crudo: no hay nada que verificar")
    lic = L.cargar() or {"evidencias": {}}
    for eid, e in lic["evidencias"].items():
        if e.get("sha256"):
            n += 1
            if not os.path.isfile(e["ruta"]) or C.sha256_fichero(e["ruta"]) != e["sha256"]:
                problemas.append(f"evidencia de licencia alterada: {eid}")
    n += verificar_datasets(C.DATASETS, esperados, problemas)
    csv = (C.leer_json(C.INFORMES_FUERA + "/filtro_resumen.json") or {}).get("csv")
    if csv:
        n += 1
        if not os.path.isfile(csv["ruta"]) or C.sha256_fichero(csv["ruta"]) != csv["sha256"]:
            problemas.append(f"CSV del filtro alterado: {csv['ruta']}")
    return n


def refiltrar(problemas: list, esperados: set) -> int:
    """Reaplica el filtro (mismo --corte de cada manifiesto) sobre lo crudo en una carpeta temporal y compara hashes."""
    lic = L.cargar()
    mans = cargar_manifiestos(C.DATASETS)
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
        nuevo = FI.correr(corte, lic, salida, ids=sorted(esperados or mans))["manifiestos"]
        for did, m in mans.items():
            n = nuevo.get(did)
            if n is None or n["dataset_sha256"] != m["dataset_sha256"] or n["contenido_sha256"] != m["contenido_sha256"]:
                problemas.append(f"el filtro reaplicado con corte {corte} da otro hash en {did}")
    finally:
        shutil.rmtree(salida, ignore_errors=True)
    return len(mans)


def correr(solo_hashes: bool = False) -> int:
    problemas = []
    lic = L.cargar()
    if not lic:
        problemas.append("no hay licencias.json: no se puede saber que datasets se esperan")
    esperados = {e["id"] for e in FI.datasets_esperados(lic, FI.crudo_registrado())}
    if lic and not esperados:
        problemas.append("ningun dataset esperado (ninguno con licencia verificada y crudo completo)")
    n = hashes(problemas, esperados)
    print(f"verificar: {n} ficheros comprobados (SHA-256, tamano y filas); {len(esperados)} datasets esperados")
    mans = cargar_manifiestos(C.DATASETS)
    if mans:
        esc = FI.comprobar_escrito(C.DATASETS, mans)
        print(f"verificar: parquet releidos ({esc['filas_releidas']:,} filas): series_id en train y val {esc['ids_en_ambos_lados']}, "
              f"contenidos en train y val {esc['contenidos_en_ambos_lados']}, ficheros con filas distintas del manifiesto "
              f"{len(esc['filas_distintas_del_manifiesto'])}")
        if esc["ids_en_ambos_lados"] or esc["contenidos_en_ambos_lados"]:
            problemas.append(f"particion no disjunta en los parquet: {esc}")
        problemas += [f"filas releidas distintas del manifiesto: {x}" for x in esc["filas_distintas_del_manifiesto"]]
    if not solo_hashes:
        try:
            k = refiltrar(problemas, esperados)
        except (C.ParadaDisco, C.PresupuestoExcedido) as e:  # la copia temporal tambien pasa por la guarda de 100 GB
            print(f"PARADA: {e}")
            return 3
        print(f"verificar: filtro reaplicado sobre {k} datasets")
    for p in problemas:
        print("  PROBLEMA:", p)
    print("verificar: OK" if not problemas else f"verificar: {len(problemas)} problemas")
    return 1 if problemas else 0
