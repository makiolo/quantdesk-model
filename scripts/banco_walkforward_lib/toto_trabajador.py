"""Trabajador de Toto para banco_walkforward.py. Se ejecuta con el Python del venv aparte de Toto
(E:/quantdesk-lab/venvs/toto, torch 2.7.0+cpu y toto-ts 0.2.0), nunca con el .venv del laboratorio, y no importa nada
del repositorio (solo numpy, torch, toto y huggingface_hub del venv de Toto).

Protocolo por lineas JSON (stdin -> stdout; todo lo demas que se imprima va a stderr):
- al arrancar escribe {"listo": true, "versiones": {...}, "pesos": {...}};
- por cada peticion {"precios": [...], "semilla": int, "hmax": int} responde {"Q": [[21 cuantiles] x hmax],
  "cpu_s": float} o {"error": str, "cpu_s": float}.
Contrato de cuantiles (el mismo que Chronos-2): contexto = log de los W precios visibles; Toto da `--muestras`
trayectorias de log-precio a hmax pasos; Q[h-1] son los 21 cuantiles empiricos (numpy.quantile lineal) de
log P_{t+h} - log P_t. `--falso` sustituye Toto por una normal sembrada (selftest: sin torch, sin pesos, sin red).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

NIVELES = (0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
           0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99)
TOTO_ID = "Datadog/Toto-Open-Base-1.0"


def _sha_snapshot(repo, revision):
    from huggingface_hub import snapshot_download

    d = snapshot_download(repo, revision=revision, local_files_only=True)
    out = {"repo": repo, "revision": os.path.basename(os.path.normpath(d)), "ficheros": {}}
    for raiz, _, nombres in os.walk(d):
        for n in sorted(nombres):
            p = os.path.join(raiz, n)
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
            out["ficheros"][os.path.relpath(p, d).replace(os.sep, "/")] = h.hexdigest()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hilos", type=int, default=2)
    ap.add_argument("--muestras", type=int, default=256)
    ap.add_argument("--revision", default=None)
    ap.add_argument("--falso", action="store_true")
    ap.add_argument("--descargar", action="store_true", help="solo descarga los pesos a HF_HOME y sale")
    a = ap.parse_args()
    proto = sys.stdout
    sys.stdout = sys.stderr
    import numpy as np

    versiones = {"python": sys.version.split()[0], "numpy": np.__version__, "ejecutable": sys.executable}
    pesos = None
    if a.falso:
        def predecir(lp, semilla, hmax):
            sd = float(np.std(np.diff(lp)))
            rs = np.random.RandomState(semilla)
            tray = np.cumsum(rs.standard_normal((a.muestras, hmax)) * sd, axis=1)
            return tray
    else:
        import importlib.metadata as md

        import torch

        if a.descargar:
            from huggingface_hub import snapshot_download

            print(snapshot_download(TOTO_ID, revision=a.revision))
            return 0
        torch.set_num_threads(a.hilos)
        torch.use_deterministic_algorithms(True)
        from toto.data.util.dataset import MaskedTimeseries
        from toto.inference.forecaster import TotoForecaster
        from toto.model.toto import Toto

        modelo = Toto.from_pretrained(TOTO_ID, revision=a.revision)
        modelo.eval()
        fc = TotoForecaster(modelo.model)
        for p in ("torch", "toto-ts", "transformers", "huggingface-hub", "gluonts"):
            try:
                versiones[p] = md.version(p)
            except md.PackageNotFoundError:
                versiones[p] = None
        pesos = _sha_snapshot(TOTO_ID, a.revision)

        def predecir(lp, semilla, hmax):
            x = torch.tensor(lp, dtype=torch.float32)[None, :]
            n = x.shape[-1]
            ent = MaskedTimeseries(
                series=x,
                padding_mask=torch.ones_like(x, dtype=torch.bool),
                id_mask=torch.zeros_like(x, dtype=torch.int),
                timestamp_seconds=(torch.arange(n, dtype=torch.int64) * 86400)[None, :],
                time_interval_seconds=torch.full((1,), 86400, dtype=torch.int),
            )
            torch.manual_seed(semilla)
            with torch.inference_mode():
                f = fc.forecast(ent, prediction_length=hmax, num_samples=a.muestras, samples_per_batch=a.muestras)
            s = f.samples[0, 0].double().numpy()  # (hmax, muestras)
            return s.T - lp[-1]

    proto.write(json.dumps({"listo": True, "versiones": versiones, "pesos": pesos, "falso": a.falso}) + "\n")
    proto.flush()
    for linea in sys.stdin:
        if not linea.strip():
            continue
        t0 = time.process_time()
        try:
            req = json.loads(linea)
            lp = np.log(np.asarray(req["precios"], dtype=np.float64))
            tray = predecir(lp, int(req["semilla"]), int(req["hmax"]))  # (muestras, hmax)
            Q = np.quantile(tray, NIVELES, axis=0).T
            if not np.all(np.isfinite(Q)):
                raise ValueError("cuantiles no finitos")
            resp = {"Q": Q.tolist(), "cpu_s": time.process_time() - t0}
        except Exception as exc:  # noqa: BLE001 -- el banco lo cuenta como fallo
            resp = {"error": f"{type(exc).__name__}: {exc}"[:300], "cpu_s": time.process_time() - t0}
        proto.write(json.dumps(resp) + "\n")
        proto.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
