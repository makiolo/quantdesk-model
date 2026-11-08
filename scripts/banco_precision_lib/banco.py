"""Orquestacion del banco: perfiles, ejecucion de las medidas, JSON canonico y hash."""
from __future__ import annotations

import hashlib
import importlib.metadata as md
import json
import math
import os
import platform
import sys
import time
from datetime import datetime, timezone

import numpy as np
import torch

from . import datos, dupire, medidas, modelo
from .redondeo import MAXIMO, MANTISA, TIPOS, Contador, celdas

HILOS = 1  # fijo y publicado; con la maquina compartida y saturada, 2 hilos de torch se esperan entre si (spin-wait) y el tiempo se multiplica por 8-20
SEMILLA_EVAL = 9999  # entradas de evaluacion fijas, comunes a todas las semillas
MOTOR_COMMIT = "69fdb39d"
FORMATO = 1

PERFILES = {
    "completo": {
        "semillas": [11, 22, 33, 44, 55],
        "W": 64, "d": 32, "nh": 4, "ff": 64, "capas": 2, "H": 20,
        "n_series_ent": 8, "n_ent": 5000, "lote": 128, "pasos": 800, "lr": 3e-3,
        "n_garch": 10000, "n_reg": 2500, "paso_crps": 10, "n_eval": 512,
    },
    # Perfil de prueba: mismo codigo, tamanos minimos. No produce cifras utiles; solo comprueba el cableado.
    "mini": {
        "semillas": [1, 2],
        "W": 16, "d": 16, "nh": 2, "ff": 32, "capas": 1, "H": 6,
        "n_series_ent": 2, "n_ent": 600, "lote": 32, "pasos": 20, "lr": 3e-3,
        "n_garch": 1500, "n_reg": 800, "paso_crps": 20, "n_eval": 32,
    },
}


def configurar_torch(hilos: int = HILOS) -> None:
    torch.set_num_threads(hilos)
    torch.use_deterministic_algorithms(True)


def versiones() -> dict:
    def v(dist: str) -> str:
        try:
            return md.version(dist)
        except md.PackageNotFoundError:
            return "no instalado"

    return {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "ml_dtypes": v("ml_dtypes"),
        "arch": v("arch"),
        "numpy": np.__version__,
        "scipy": v("scipy"),
        "quantdesk_paquete": v("quantdesk"),
        "quantdesk_motor_commit": MOTOR_COMMIT,
    }


def entradas_evaluacion(cfg: dict) -> np.ndarray:
    """Conjunto fijo de ventanas de evaluacion (mitad GARCH, mitad regimen), igual para todas las semillas."""
    W, H, n = cfg["W"], cfg["H"], cfg["n_eval"] // 2
    paso = W + H  # sin solape entre ventanas ni entre ventana y horizonte
    N = n * paso + W + H
    rg = datos.simular_garch(N, datos.rng(SEMILLA_EVAL, datos.F_GARCH_EVAL), **datos.GARCH_VERDAD)
    rr, _ = datos.simular_regimen(N, datos.rng(SEMILLA_EVAL, datos.F_REG_EVAL))
    return np.concatenate([datos.ventanas(rg, W, H, paso)[0][:n], datos.ventanas(rr, W, H, paso)[0][:n]], axis=0)


# ------------------------------------------------------------------------------------------- JSON canonico
def normalizar(o):
    """Tipos python puros; floats a 10 cifras significativas; NaN/inf prohibidos (lo no definido es null con motivo)."""
    if isinstance(o, dict):
        return {str(k): normalizar(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [normalizar(v) for v in o]
    if isinstance(o, (np.floating, float)):
        f = float(o)
        if not math.isfinite(f):
            raise ValueError(f"valor no finito en los resultados: {f}")
        return float(f"{f:.10g}")
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return normalizar(o.tolist())
    return o


def canonico(d: dict) -> str:
    return json.dumps(normalizar(d), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def hash_canonico(d: dict) -> str:
    return hashlib.sha256(canonico(d).encode("utf-8")).hexdigest()


def escribir_resultados(doc: dict, out_dir: str) -> str:
    """Escribe resultados.json y resultados.json.sha256; devuelve el hash canonico (sin meta)."""
    h = hash_canonico(doc["datos"])
    doc["meta"]["sha256_canonico"] = h
    texto = json.dumps(normalizar(doc), sort_keys=True, indent=1, ensure_ascii=False, allow_nan=False)
    with open(os.path.join(out_dir, "resultados.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(texto + "\n")
    with open(os.path.join(out_dir, "resultados.json.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{h}  resultados.json (JSON canonico con claves ordenadas, sin el bloque meta)\n")
    return h


def leer_resultados(directorio: str) -> dict:
    with open(os.path.join(directorio, "resultados.json"), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------ ejecucion
def ejecutar(perfil: str, out_dir: str, comando: str, log=print, hilos: int = HILOS) -> dict:
    """Ejecuta el banco completo y devuelve el documento {datos, meta}. Escribe pesos en out_dir."""
    cfg = dict(PERFILES[perfil])
    configurar_torch(hilos)
    t0 = time.time()
    ids = [c for c, _, _ in celdas()]
    cont1 = {c: Contador() for c in ids}
    cont2 = {c: Contador() for c in ids}
    modelos, entren, m1_sem, base = [], [], [], []
    for semilla in cfg["semillas"]:
        ts = time.time()
        R, validos = datos.corpus_entrenamiento(semilla, cfg)
        mod, info = modelo.entrenar(cfg, semilla, R, validos, datos.rng(semilla, datos.F_LOTES))
        torch.save(mod.state_dict(), os.path.join(out_dir, f"pesos_semilla{semilla}.pt"))
        info["n_parametros"] = modelo.n_parametros(mod)
        entren.append(info)
        modelos.append(mod)
        log(f"semilla {semilla}: entrenado en {time.time() - ts:.0f} s, perdida {info['perdida_inicial']:.4f} -> {info['perdida_final']:.4f}")
        s1 = medidas.medida1_semilla(semilla, cfg, mod, cont1)
        m1_sem.append(s1)
        base.append(s1.pop("_baseline"))
        log(f"semilla {semilla}: medida 1 hecha ({time.time() - ts:.0f} s en total)")
    m1 = medidas.agregar_m1(m1_sem, cont1)
    X_eval = entradas_evaluacion(cfg)
    log("medidas 2 y 3 ...")
    m2, m3 = medidas.medidas23(modelos, X_eval, cfg, cont2, log=log)
    contexto = {
        "crps_f64": {
            k: [s["f64"]["metricas"][k] for s in m1_sem] for k in ("crps_garch", "crps_regimen")
        },
        "crps_gauss_incondicional": {k: [b[k] for b in base] for k in ("crps_garch", "crps_regimen")},
    }
    datos_doc = {
        "formato": FORMATO,
        "perfil": perfil,
        "config": cfg,
        "hilos": hilos,
        "versiones": versiones(),
        "tipos": {t: {"maximo_finito": MAXIMO[t], "bits_mantisa": MANTISA[t]} for t in TIPOS},
        "verdad": {"garch": datos.GARCH_VERDAD, "regimen": datos.REGIMEN_VERDAD},
        "modelo": {
            "descripcion": modelo.describir(cfg),
            "n_parametros": entren[0]["n_parametros"],
            "alfas": modelo.ALFAS.tolist(),
            "entrenamiento": entren,
            "contexto_crps": contexto,
        },
        "dupire": {"nk": dupire.NK, "dens_min": dupire.DENS_MIN, "cobertura_min": medidas.COBERTURA_MIN},
        "m1": m1,
        "m2": m2,
        "m3": m3,
    }
    meta = {
        "fecha_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tiempo_pared_s": round(time.time() - t0, 1),
        "comando": comando,
        "plataforma": platform.platform(),
    }
    return {"datos": datos_doc, "meta": meta}
