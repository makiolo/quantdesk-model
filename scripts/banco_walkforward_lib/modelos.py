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
- fincast: FinCast v1, decoder MoE de 4 expertos, venv propio, timeout, 9 deciles nativos; el banco
  solo lo evalua en la ventana limpia (CRPS deciles y QLIKE).
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
FINCAST_PY = "E:/quantdesk-lab/venvs/fincast/Scripts/python.exe"
FINCAST_ID = "Vincent05R/FinCast"
FINCAST_REV = "2d7d90b159db8961d27c2cf165d51195902ef92b"
FINCAST_CODIGO_REV = "488b19d1d85fa2b3d4b93469530cefdcf1cc97a4"
FINCAST_SHA256 = "d5ca999b02c944effa60d2b94174dc4d5a0cd2c0543ae289b2e36f37431492a8"
FINCAST_CODIGO = "E:/quantdesk-lab/src/FinCast-fts@" + FINCAST_CODIGO_REV
FINCAST_PESOS = ("E:/quantdesk-lab/cache/hf/hub/models--Vincent05R--FinCast/snapshots/"
                  + FINCAST_REV + "/v1.pth")
FINCAST_TIMEOUT_S = 600.0
FINCAST_ARRANQUE_S = 300.0
FINCAST_TRABAJADOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fincast_trabajador.py")


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


class FinCast:
    """Subproceso con timeout de peticion (600 s) y de arranque (300 s).
    Un timeout mata el trabajador; el siguiente origen arranca otro y continua. Toto no se modifica.
    """

    nombre = "fincast"

    def __init__(self, hilos=2, python=FINCAST_PY, falso=False, pesos=FINCAST_PESOS,
                 codigo=FINCAST_CODIGO, timeout_s=FINCAST_TIMEOUT_S, log=None, fallo_falso=None):
        import math

        if not math.isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError("timeout de FinCast debe ser positivo y finito")
        if not os.path.isfile(python):
            raise ModeloSaltado(f"fincast SALTADO: no existe el venv de FinCast ({python})")
        if not falso:
            for p, que in ((pesos, "pesos"), (os.path.join(codigo, "src/ffm/pytorch_patched_decoder_MOE.py"), "codigo")):
                if not os.path.isfile(p):
                    raise ModeloSaltado(f"fincast SALTADO: faltan {que} ({p})")
            if os.path.normcase(os.path.realpath(python)) != os.path.normcase(os.path.realpath(FINCAST_PY)):
                raise ValueError("FinCast real solo se ejecuta con el interprete de su venv propio")
        self.hilos, self.python, self.falso, self.ruta_pesos = hilos, python, falso, pesos
        self.codigo, self.timeout_s, self.timeout_arranque_s = codigo, timeout_s, FINCAST_ARRANQUE_S
        self.log, self._fallo_pendiente = log, fallo_falso
        self.p = None
        self._log = None
        self._iniciar()

    def _iniciar(self):
        import json
        import queue
        import subprocess
        import threading

        from . import rutas

        env = dict(os.environ, HF_HOME="E:/quantdesk-lab/cache/hf", HF_HUB_OFFLINE="1",
                   TMP=rutas.TMP_FINCAST, TEMP=rutas.TMP_FINCAST)
        for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
            env[v] = str(self.hilos)
        os.makedirs(env["TMP"], exist_ok=True)
        cmd = [self.python, "-I", "-X", "utf8", FINCAST_TRABAJADOR, "--hilos", str(self.hilos)]
        if self.falso:
            cmd += ["--falso"]
            if self._fallo_pendiente:
                cmd += ["--fallo-falso", self._fallo_pendiente]
                self._fallo_pendiente = None
        else:
            cmd += ["--pesos", self.ruta_pesos, "--codigo", self.codigo, "--sha256", FINCAST_SHA256,
                    "--revision", FINCAST_REV, "--codigo-revision", FINCAST_CODIGO_REV]
        self._log = open(self.log, "a", encoding="utf-8") if self.log else subprocess.DEVNULL
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._log,
                                  text=True, encoding="utf-8", env=env, cwd=env["TMP"])
        self._cola = queue.Queue()

        def leer(p, cola):
            try:
                for linea in p.stdout:
                    cola.put(linea)
            finally:
                cola.put(None)

        self._lector = threading.Thread(target=leer, args=(self.p, self._cola), daemon=True)
        self._lector.start()
        try:
            hola = self._leer(self.timeout_arranque_s)
            if not hola.get("listo"):
                raise ModeloSaltado(f"fincast SALTADO: {hola.get('error', hola)}")
            self.versiones, self.pesos = hola["versiones"], hola["pesos"]
            self.cpu_carga_s = float(hola.get("cpu_carga_s", 0.0))
        except Exception:
            self.cerrar()
            raise

    def _leer(self, timeout):
        import json
        import queue

        try:
            linea = self._cola.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError(f"FinCast timeout tras {timeout:g} s; trabajador terminado") from None
        if linea is None:
            raise RuntimeError(f"trabajador FinCast termino (codigo {self.p.poll()})")
        return json.loads(linea)

    def predecir(self, precios, semilla, hmax):
        import json
        import threading

        if self.p is None or self.p.poll() is not None:
            self.cerrar()
            self._iniciar()
        req = json.dumps({"precios": np.asarray(precios, float).tolist(), "semilla": int(semilla), "hmax": int(hmax)})

        def enviar(p, cola):
            try:
                p.stdin.write(req + "\n")
                p.stdin.flush()
            except (OSError, ValueError):
                cola.put(None)

        # La escritura tambien queda bajo el timeout: un trabajador que deje de leer no bloquea el padre.
        threading.Thread(target=enviar, args=(self.p, self._cola), daemon=True).start()
        try:
            r = self._leer(self.timeout_s)
        except Exception:
            self.cerrar()
            raise
        try:
            if "error" in r:
                raise RuntimeError(r["error"])
            Q = np.asarray(r["Q"], float)
            if Q.shape != (hmax, len(metricas.NIVELES)) or not np.isfinite(Q).all():
                raise ValueError(f"FinCast salida invalida {Q.shape}")
            if (np.diff(Q, axis=1) < 0).any():
                raise ValueError("FinCast cuantiles no monotonos")
            return Q, {**r["info"], "cpu_s_externo": float(r["cpu_s"])}
        except Exception as exc:
            # La linea completa ya se consumio: el protocolo sigue sincronizado. No recargar ~4 GB por
            # un origen rechazado; conservar tambien la CPU que devolvio una respuesta de error.
            if isinstance(r, dict):
                exc.cpu_s_externo = float(r.get("cpu_s", 0.0))
            raise

    def cerrar(self):
        p, self.p = self.p, None
        if p is not None:
            if p.poll() is None:
                p.kill()
            p.wait(timeout=10)
            self._lector.join(timeout=5)
            p.stdin.close()
            p.stdout.close()
        if self._log is not None and hasattr(self._log, "close"):
            self._log.close()
        self._log = None


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
