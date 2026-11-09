"""Modelos del banco. Interfaz comun: `predecir(precios, semilla, hmax) -> (Q, info)` donde `precios` es el contexto
causal (ultimos W cierres visibles, solo lectura), `Q[h-1]` son los 21 cuantiles (metricas.NIVELES) del
rendimiento logaritmico acumulado ln(P_{t+h}/P_t) para h = 1..hmax, e `info` un dict pequeno de diagnostico.
Ningun modelo ve otra cosa que `precios`.

- hmm: HMM del motor (quantdesk 69fdb39d, bindings Python): plantilla K = 3 estados GBM_P (el K mas pequeno de los
  candidatos {3, 4} que usa el HMM de FX del motor), calibrada con Baum-Welch (HmmCalibrationOptions por defecto
  salvo la semilla) sobre los precios con malla de observaciones (dt = 1/252 por barra); S caminos condicionados al
  final de la calibracion con Engine.open_stream(res, semilla_j, policy="from_calibration_end"), un camino por
  stream.
- garch: GARCH(1,1) de `arch` con media constante e innovaciones t de Student sobre 100 * rendimientos log;
  prevision por simulacion (S caminos, RandomState sembrado).
- chronos2: Chronos-2 (amazon/chronos-2, revision fijada) zero-shot sobre el log-precio; cuantiles nativos del
  modelo a hmax pasos menos el ultimo log-precio. Lote de una serie por llamada (el resultado depende en ~1e-6 de
  la composicion del lote; con lote 1 un subconjunto reproduce bit a bit la corrida completa).
- toto: Toto-Open-Base-1.0 zero-shot en un subproceso con el venv aparte (clase Toto, toto_trabajador.py).
- trivial: sustituto de chronos2 en el selftest (sin pesos ni red): normal de media 0 y desviacion la de los
  rendimientos del contexto por raiz de h.
"""
from __future__ import annotations

import hashlib
import os
import warnings

import numpy as np

from . import metricas

S_CAMINOS = 1000
DT = 1.0 / 252.0
K_HMM = 3
CHRONOS_ID = "amazon/chronos-2"
CHRONOS_REV = "29ec3766d36d6f73f0696f85560a422f50e8498c"


def _cuantiles_de_muestras(lr):
    """lr: (S, hmax) -> (hmax, 21)."""
    return np.quantile(lr, metricas.NIVELES, axis=0).T


class Hmm:
    nombre = "hmm"

    def __init__(self, s_caminos: int = S_CAMINOS):
        import quantdesk as q

        self.q = q
        self.eng = q.Engine(n_paths=1, n_steps=1, seed=0)
        self.s = s_caminos

    def predecir(self, precios, semilla, hmax):
        q = self.q
        p = np.asarray(precios, float)
        sd = float(np.std(np.diff(np.log(p)))) / np.sqrt(DT)
        tmpl = q.Hmm(
            states=tuple(q.GbmP(s0=float(p[-1]), mu=0.0, sigma=max(sd * f, 1e-4), observable="X")
                         for f in (0.5, 1.0, 2.0)),
            initial_probabilities=(1 / 3, 1 / 3, 1 / 3),
            transition_matrix=((0.90, 0.05, 0.05), (0.05, 0.90, 0.05), (0.05, 0.05, 0.90)),
            transition_interval=DT,
        )
        obs = q.ObservedSeries.from_arrays("X", np.arange(len(p)) * DT, p)
        res = self.eng.calibrate(tmpl, obs, q.HmmCalibrationOptions(seed=int(semilla)))
        s0 = float(res.hmm.s0_last_observed)
        if s0 != float(p[-1]):
            raise AssertionError(f"s0 de la calibracion {s0} != ultimo precio {p[-1]}")
        dts = [DT] * hmax
        out = np.empty((self.s, hmax))
        base = int(semilla) * 4096
        for j in range(self.s):
            st = self.eng.open_stream(res, base + j, policy="from_calibration_end")
            out[j] = np.asarray(st.advance_many(dts).values)[:, 0]
        lr = np.log(out / s0)
        info = {"convergido": bool(res.diagnostics.converged), "iteraciones": int(res.diagnostics.iterations)}
        return _cuantiles_de_muestras(lr), info


class Garch:
    nombre = "garch"

    def __init__(self, s_caminos: int = S_CAMINOS):
        from arch import arch_model

        self.arch_model = arch_model
        self.s = s_caminos

    def predecir(self, precios, semilla, hmax):
        r = np.diff(np.log(np.asarray(precios, float))) * 100.0
        m = self.arch_model(r, mean="Constant", vol="GARCH", p=1, q=1, dist="t")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fr = m.fit(disp="off")
            pr = fr.params
            nu = float(pr["nu"])
            gen = np.random.default_rng(int(semilla))
            esc = np.sqrt((nu - 2.0) / nu)

            def rng(size, gen=gen, nu=nu, esc=esc):  # t de Student estandarizada (varianza 1), sembrada
                return gen.standard_t(nu, size) * esc

            # arch 8 ignora random_state en la simulacion: la semilla entra por rng.
            f = fr.forecast(horizon=hmax, method="simulation", simulations=self.s, reindex=False, rng=rng)
        sims = np.asarray(f.simulations.values)[-1] / 100.0  # (S, hmax)
        lr = np.cumsum(sims, axis=1)
        info = {"convergido": int(fr.convergence_flag) == 0,
                "persistencia": float(pr["alpha[1]"] + pr["beta[1]"]), "nu": float(pr["nu"])}
        return _cuantiles_de_muestras(lr), info


class Chronos2:
    nombre = "chronos2"

    def __init__(self, hilos: int):
        import torch
        from chronos import Chronos2Pipeline

        torch.set_num_threads(hilos)
        torch.manual_seed(0)
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:  # noqa: BLE001
            pass
        self.torch = torch
        self.pipe = Chronos2Pipeline.from_pretrained(CHRONOS_ID, revision=CHRONOS_REV, device_map="cpu",
                                                     dtype=torch.float32)
        if tuple(self.pipe.quantiles) != metricas.NIVELES:
            raise AssertionError(f"cuantiles de Chronos-2 inesperados: {self.pipe.quantiles}")

    def predecir(self, precios, semilla, hmax):
        lp = np.log(np.asarray(precios, float))
        x = self.torch.tensor(lp, dtype=self.torch.float32)[None, :]
        with self.torch.no_grad():
            qs, _ = self.pipe.predict_quantiles([x], prediction_length=hmax, quantile_levels=list(metricas.NIVELES))
        Q = qs[0][0].double().numpy() - lp[-1]
        return Q, {}


class Trivial:
    """Sustituto sin pesos de chronos2 para el selftest (misma interfaz)."""

    nombre = "chronos2"

    def predecir(self, precios, semilla, hmax):
        from scipy.stats import norm

        sd = float(np.std(np.diff(np.log(np.asarray(precios, float)))))
        z = norm.ppf(metricas.NIVELES)
        Q = np.array([z * sd * np.sqrt(h) for h in range(1, hmax + 1)])
        return Q, {}


class ModeloSaltado(RuntimeError):
    """El modelo no se puede ejecutar en esta maquina (p. ej. falta el venv de Toto): se salta y se dice."""


TOTO_PY = "E:/quantdesk-lab/venvs/toto/Scripts/python.exe"
TOTO_ID = "Datadog/Toto-Open-Base-1.0"
TOTO_REV = "0411ceb27bdf7fc3e4892e99edc8ad08192dc3c5"
TOTO_MUESTRAS = 256
TRABAJADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toto_trabajador.py")


class Toto:
    """Toto zero-shot en un subproceso con el venv aparte (toto-ts 0.2.0 fija torch 2.7.0 y numpy 1.26.4, incompatibles
    con el .venv del laboratorio). Mismo contrato que chronos2: contexto en log-precio, 21 cuantiles (empiricos, de
    TOTO_MUESTRAS trayectorias) de ln(P_{t+h}/P_t). El CPU del subproceso lo mide el propio trabajador y se suma al
    del modelo (`cpu_s_externo`). `falso=True` usa una normal sembrada (selftest)."""

    nombre = "toto"

    def __init__(self, hilos: int = 2, python: str = TOTO_PY, falso: bool = False, muestras: int = TOTO_MUESTRAS,
                 log: str | None = None):
        import json
        import subprocess

        if not os.path.isfile(python):
            raise ModeloSaltado(f"toto SALTADO: no existe el venv de Toto ({python})")
        self.json = json
        env = dict(os.environ)
        env["HF_HUB_OFFLINE"] = "1"
        for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
            env[v] = str(hilos)
        cmd = [python, "-I", "-X", "utf8", TRABAJADOR, "--hilos", str(hilos), "--muestras", str(muestras),
               "--revision", TOTO_REV] + (["--falso"] if falso else [])
        self._log = open(log, "a", encoding="utf-8") if log else subprocess.DEVNULL
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._log, text=True,
                                  encoding="utf-8", env=env, cwd=os.path.dirname(TRABAJADOR))
        hola = self._leer()
        if not hola.get("listo"):
            raise ModeloSaltado(f"toto SALTADO: el trabajador no arranco: {hola}")
        self.versiones, self.pesos, self.muestras = hola["versiones"], hola["pesos"], muestras

    def _leer(self):
        linea = self.p.stdout.readline()
        if not linea:
            raise RuntimeError(f"el trabajador de Toto termino (codigo {self.p.poll()})")
        return self.json.loads(linea)

    def predecir(self, precios, semilla, hmax):
        req = {"precios": [float(x) for x in np.asarray(precios, float)], "semilla": int(semilla), "hmax": int(hmax)}
        self.p.stdin.write(self.json.dumps(req) + "\n")
        self.p.stdin.flush()
        r = self._leer()
        if "error" in r:
            raise RuntimeError(r["error"])
        return np.asarray(r["Q"], float), {"cpu_s_externo": float(r["cpu_s"])}

    def cerrar(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=30)
        except Exception:  # noqa: BLE001
            self.p.kill()


def pesos_chronos() -> dict:
    """Revision y sha256 de los ficheros del snapshot de Chronos-2 en la cache de Hugging Face (sin red)."""
    from huggingface_hub import snapshot_download

    d = snapshot_download(CHRONOS_ID, revision=CHRONOS_REV, local_files_only=True)
    out = {"repo": CHRONOS_ID, "revision": CHRONOS_REV, "ficheros": {}}
    for nombre in sorted(os.listdir(d)):
        h = hashlib.sha256()
        with open(os.path.join(d, nombre), "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        out["ficheros"][nombre] = h.hexdigest()
    return out
