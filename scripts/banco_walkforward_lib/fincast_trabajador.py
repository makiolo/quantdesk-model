"""FinCast aislado (-I, venv propio); JSON por lineas, sin importar el repositorio del banco.

Contexto: log-precio; salida: cuantiles de log P[t+h] - log P[t]. Decoder oficial sin modificar,
cargado directamente para no importar ffm.__init__ (API de covariables que exige JAX).
--falso usa solo numpy/stdlib y permite probar el protocolo sin pesos ni red.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from statistics import NormalDist

# Copia del mismo contrato que toto_trabajador.py; prueba_fincast comprueba las tres copias.
NIVELES = (0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
           0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99)
DECILES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
METODO = ("lineal en z=Phi^-1(p) entre deciles adyacentes; extrapolacion con pendiente "
          "de 0.1-0.2 para p<0.1 y de 0.8-0.9 para p>0.9; deciles nativos intactos")
CODIGO_HUELLAS = {
    "ffm/pytorch_patched_decoder_MOE.py": "b7df152bfe7666c10a2c5a643459468e53f2ef2a7c489de8c9a9bd6c924d5147",
    "st_moe_pytorch/__init__.py": "549246007614aab738d7a5543efb29d82d3acba4ab0fec4fe02fcf907cc9b132",
    "st_moe_pytorch/st_moe_pytorch.py": "33e9afc0597933c35ffecc8149be9d166f84f919401750bed52dbf88052c3bf7",
    "st_moe_pytorch/distributed.py": "ab8dc35f4919418650b33d1c50c10f3bd79bc8eb6bf2ac2d4696c0af25e8499d",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def expandir_deciles(nativos):
    import numpy as np

    q = np.asarray(nativos, float)
    if q.ndim != 2 or q.shape[1] != 9 or not np.isfinite(q).all():
        raise ValueError("deciles nativos invalidos")
    if (np.diff(q, axis=1) < 0).any():
        raise ValueError("deciles nativos no monotonos")
    z = [NormalDist().inv_cdf(p) for p in DECILES]
    out = np.empty((len(q), len(NIVELES)))
    for j, p in enumerate(NIVELES):
        if p in DECILES:
            out[:, j] = q[:, DECILES.index(p)]
            continue
        i = min(max(int(np.searchsorted(DECILES, p)) - 1, 0), 7)
        peso = (NormalDist().inv_cdf(p) - z[i]) / (z[i + 1] - z[i])
        out[:, j] = q[:, i] + peso * (q[:, i + 1] - q[:, i])
    return out, {"niveles_nativos": list(DECILES), "niveles_extrapolados": [0.01, 0.05, 0.95, 0.99],
                 "niveles_interpolados": [p for p in NIVELES if 0.1 < p < 0.9 and p not in DECILES],
                 "metodo_cuantiles": METODO}


def cargar_decoder(a):
    """Solo ejecuta los ficheros auditados de la revision fijada. No carga pickle arbitrario."""
    import torch

    if sha256(a.pesos) != a.sha256:
        raise ValueError("sha256 de v1.pth distinto del fijado")
    for relativo, huella in CODIGO_HUELLAS.items():
        if sha256(os.path.join(a.codigo, "src", relativo)) != huella:
            raise ValueError(f"codigo distinto de la revision auditada: {relativo}")
    # El modulo decoder no usa imports relativos. Evita ejecutar ffm/__init__.py y xreg_lib (JAX).
    # Registrar solo este paquete y su __path__: src nunca entra en sys.path y no puede
    # sombrear torch/numpy/stdlib. Descarta modulos precargados para no resolver desde otra raiz.
    paquete = "st_moe_pytorch"
    for n in list(sys.modules):
        if n == paquete or n.startswith(paquete + "."):
            del sys.modules[n]
    directorio = os.path.join(a.codigo, "src", paquete)
    spec_paquete = importlib.util.spec_from_file_location(
        paquete, os.path.join(directorio, "__init__.py"), submodule_search_locations=[directorio])
    modulo_paquete = importlib.util.module_from_spec(spec_paquete)
    sys.modules[paquete] = modulo_paquete
    spec_paquete.loader.exec_module(modulo_paquete)
    nombre = "fincast_decoder_auditado"
    spec = importlib.util.spec_from_file_location(
        nombre, os.path.join(a.codigo, "src", "ffm", "pytorch_patched_decoder_MOE.py"))
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    torch.set_num_threads(a.hilos)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)
    # v1: 50 capas, dim 1280, 16 cabezas, 4 expertos (inference_utils.py), top-2, patch 32, output 128.
    cfg = modulo.FFMConfig(num_experts=4)
    if tuple(cfg.quantiles) != DECILES:
        raise ValueError(f"deciles del modelo inesperados: {cfg.quantiles}")
    estado = torch.load(a.pesos, map_location="cpu", weights_only=True)
    if not isinstance(estado, dict) or not estado or not all(
            isinstance(k, str) and isinstance(v, torch.Tensor) for k, v in estado.items()):
        raise ValueError("BLOQUEADO: v1.pth no es un state_dict puro; weights_only=False no permitido")
    limpio = {}
    for k, v in estado.items():
        for prefijo in ("_orig_mod.module.", "_orig_mod.", "module."):
            if k.startswith(prefijo):
                k = k[len(prefijo):]
                break
        if k in limpio:
            raise ValueError("claves duplicadas al quitar prefijo DDP/compile")
        limpio[k] = v
    modelo = modulo.PatchedTimeSeriesDecoder_MOE(cfg)
    modelo.load_state_dict(limpio, strict=True)
    modelo.eval()

    def predecir(lp, semilla, hmax):
        import numpy as np

        # Igual que FFmBase._preprocess: padding frontal con ceros y mascara 1.
        # Se conserva todo W (250/1000), ampliando solo al multiplo siguiente de patch_len=32.
        pad = (-len(lp)) % cfg.patch_len
        x = torch.tensor(np.pad(lp, (pad, 0)), dtype=torch.float32)[None, :]
        mascara = torch.zeros((1, len(lp) + pad + hmax), dtype=torch.float32)
        mascara[:, :pad] = 1
        torch.manual_seed(semilla)  # el gate MoE sortea tambien en eval; semilla por origen, lote 1
        with torch.inference_mode():
            _, full = modelo.decode(x, mascara, torch.zeros((1, 1), dtype=torch.long),
                                    horizon_len=hmax, return_forecast_on_context=False)
        return full[0, :, 1:].double().numpy() - lp[-1]

    return predecir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hilos", type=int, default=2)
    ap.add_argument("--codigo")
    ap.add_argument("--pesos")
    ap.add_argument("--sha256")
    ap.add_argument("--revision")
    ap.add_argument("--codigo-revision")
    ap.add_argument("--falso", action="store_true")
    ap.add_argument("--fallo-falso", choices=("silencio", "error", "no_monotono"))
    a = ap.parse_args()
    proto = sys.stdout
    sys.stdout = sys.stderr
    import numpy as np

    versiones = {"python": sys.version.split()[0], "numpy": np.__version__, "ejecutable": sys.executable}
    pesos = None
    carga_inicio = time.process_time()
    try:
        if a.falso:
            def predecir(lp, semilla, hmax):
                sd = float(np.std(np.diff(lp)))
                return np.array([[NormalDist().inv_cdf(p) * sd * h ** 0.5 for p in DECILES]
                                 for h in range(1, hmax + 1)])
        else:
            import importlib.metadata as md

            predecir = cargar_decoder(a)
            versiones.update({p: md.version(p) for p in ("torch", "einops", "einx", "beartype", "CoLT5-attention")})
            pesos = {"repo": "Vincent05R/FinCast", "revision": a.revision, "ficheros": {"v1.pth": a.sha256},
                     "codigo_revision": a.codigo_revision, "carga": "torch.load(weights_only=True), strict=True",
                     "licencia_codigo_sha256": sha256(os.path.join(a.codigo, "LICENSE")),
                     "codigo_ficheros_sha256": CODIGO_HUELLAS}
    except Exception as exc:  # no reintenta con deserializacion insegura
        proto.write(json.dumps({"listo": False, "error": f"BLOQUEADO: {type(exc).__name__}: {exc}"}) + "\n")
        proto.flush()
        return 1
    proto.write(json.dumps({"listo": True, "versiones": versiones, "pesos": pesos, "falso": a.falso,
                           "cpu_carga_s": time.process_time() - carga_inicio}) + "\n")
    proto.flush()
    for i, linea in enumerate(sys.stdin):
        t0 = time.process_time()
        try:
            req = json.loads(linea)
            p = np.asarray(req["precios"], dtype=float)
            if p.ndim != 1 or len(p) < 3 or not np.isfinite(p).all() or (p <= 0).any():
                raise ValueError("precios no positivos/no finitos o contexto insuficiente")
            hmax = int(req["hmax"])
            if not 1 <= hmax <= 128:
                raise ValueError("hmax fuera de 1..128")
            if a.falso and i == 0 and a.fallo_falso == "silencio":
                time.sleep(3600)
            if a.falso and i == 0 and a.fallo_falso == "error":
                raise ValueError("error falso del trabajador")
            nativos = predecir(np.log(p), int(req["semilla"]), hmax)
            Q, info = expandir_deciles(nativos)
            if a.falso and i == 0 and a.fallo_falso == "no_monotono":
                Q[0, 1] = Q[0, 0] - 1
            resp = {"Q": Q.tolist(), "info": info, "cpu_s": time.process_time() - t0}
        except Exception as exc:  # el banco conserva el fallo por origen
            resp = {"error": f"{type(exc).__name__}: {exc}"[:500], "cpu_s": time.process_time() - t0}
        proto.write(json.dumps(resp, allow_nan=False) + "\n")
        proto.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
