"""Medidas 1-3 del banco de precision y su umbral de dispersion entre semillas.

Medida 1 (entrada): se redondean solo los log-rendimientos de entrada y NO se reentrena; se mide el error de
  recuperacion de parametros conocidos y el CRPS del cono del transformer f32 sobre la verdad.
Medida 2 (inferencia): mismo modelo con pesos y activaciones redondeados en cada frontera de capa.
Medida 3 (derivados): sigma_loc por Dupire desde el cono de la medida 2 (la delta por AAD no se mide aqui).
"""
from __future__ import annotations

import json
import warnings

import numpy as np
import torch

from . import datos, dupire, modelo
from .redondeo import Contador, celdas, redondear

N_HMM_ESTADOS = 2
COBERTURA_MIN = 0.9  # M3: por debajo, el tipo "pierde" aunque el RMS sobre los puntos que quedan sea pequeno
GARCH_PERSISTENCIA = datos.GARCH_VERDAD["alfa"] + datos.GARCH_VERDAD["beta"]

# Metricas de la medida 1: (id, descripcion, unidad)
METRICAS_M1 = (
    ("garch_persistencia", "GARCH: |alfa+beta estimado - verdadero| (arch, normal, media cero)", "abs"),
    ("garch_omega", "GARCH: |omega estimado / omega verdadero - 1|", "relativo"),
    ("hmm_matriz", "HMM: max |P estimada - P verdadera| (estados ordenados por sigma)", "abs"),
    ("hmm_regimen", "HMM: Brier de la probabilidad suavizada de regimen frente al estado verdadero", "brier"),
    ("hmm_sigma", "HMM: max_k |sigma_k estimada / sigma_k verdadera - 1|", "relativo"),
    ("crps_garch", "CRPS del cono del transformer sobre rendimientos GARCH (media sobre ventanas y h)", "log-rend."),
    ("crps_regimen", "CRPS del cono del transformer sobre rendimientos con cambio de regimen", "log-rend."),
)
NO_MEDIDAS_M1 = (
    (
        "vol_de_la_vol",
        "Vol de la vol (volatilidad estocastica)",
        "la ficha pide parametros conocidos de GARCH y de regimen y deja la vol estocastica como opcional; "
        "estimar la vol de la vol exige un estimador propio (QML/Kalman sobre log r^2 o MCMC) que no esta en arch "
        "ni en el motor, y con rendimientos redondeados a cero el log r^2 no existe sin un desplazamiento arbitrario "
        "(el resultado dependeria de ese desplazamiento, no del tipo). No se inventa ningun numero.",
    ),
)

# Cantidades de las medidas 2 y 3 (en log-rendimiento fisico). id -> descripcion
CANTIDADES_M2 = (
    ("q_todos", "todos los cuantiles q(alfa, h)"),
    ("q_0005", "cuantil q(0,005, h)"),
    ("q_0995", "cuantil q(0,995, h)"),
    ("dq_todas", "diferencias de cuantiles contiguos q(alfa_j+1, h) - q(alfa_j, h)"),
    ("dq_cola_inf", "diferencia contigua de la cola inferior q(0,01, h) - q(0,005, h)"),
    ("dq_cola_sup", "diferencia contigua de la cola superior q(0,995, h) - q(0,99, h)"),
)


# ----------------------------------------------------------------------------------------------- estimadores
def ajustar_garch(r: np.ndarray) -> dict:
    """GARCH(1,1) normal de media cero con arch sobre 100*r (escala recomendada); omega se devuelve en unidades de r."""
    from arch import arch_model

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = arch_model(r * 100.0, mean="Zero", vol="GARCH", p=1, q=1, dist="normal", rescale=False).fit(
            disp="off", show_warning=False
        )
    p = res.params
    return {
        "omega": float(p["omega"]) / 1e4,
        "alfa": float(p["alpha[1]"]),
        "beta": float(p["beta[1]"]),
        "convergio": bool(res.convergence_flag == 0),
    }


def ajustar_hmm(r: np.ndarray) -> dict:
    """HMM de 2 estados GBM_P del motor quantdesk sobre S0*exp(cumsum r) con S0 = 100 (como smoke_env usa niveles).

    Estados ordenados por sigma creciente. Devuelve P (2x2), sigma (2), gamma (N, 2) suavizada.
    """
    import quantdesk as q

    lv = datos.niveles(r, 100.0)
    t = tuple(i / datos.DIAS_ANIO for i in range(len(lv)))
    obs = "SYN.SPOT"
    serie = q.ObservedSeries(observable=obs, times=t, values=tuple(float(x) for x in lv))
    plantilla = q.Hmm(
        states=(
            q.GbmP(s0=100.0, mu=0.0, sigma=0.1, observable=obs),
            q.GbmP(s0=100.0, mu=0.0, sigma=0.3, observable=obs),
        ),
        initial_probabilities=(0.5, 0.5),
        transition_matrix=((0.9, 0.1), (0.1, 0.9)),
        transition_interval=1.0 / datos.DIAS_ANIO,
    )
    eng = q.Engine(n_paths=1, n_steps=1, seed=0)
    fit = eng.calibrate(plantilla, serie, q.HmmCalibrationOptions(seed=7))
    d = fit.hmm
    spec = json.loads(fit.model.to_spec_json())
    sigma = np.array([c["params"]["sigma"] for c in spec["children"]], dtype=np.float64)
    P = np.asarray(d.transition_matrix_estimated, dtype=np.float64).reshape(N_HMM_ESTADOS, N_HMM_ESTADOS)
    G = np.asarray(d.gamma_by_step, dtype=np.float64).reshape(-1, N_HMM_ESTADOS)
    o = np.argsort(sigma)
    return {"P": P[np.ix_(o, o)], "sigma": sigma[o], "gamma": G[:, o], "convergio": bool(fit.diagnostics.converged)}


def error_hmm(est: dict, estado_verdadero: np.ndarray) -> dict:
    v = datos.REGIMEN_VERDAD
    P = np.asarray(v["P"])
    sig = np.asarray(v["sigma"])
    uno = np.eye(N_HMM_ESTADOS)[estado_verdadero]
    return {
        "hmm_matriz": float(np.abs(est["P"] - P).max()),
        "hmm_regimen": float(np.mean(np.sum((est["gamma"] - uno) ** 2, axis=1))),
        "hmm_sigma": float(np.max(np.abs(est["sigma"] / sig - 1.0))),
    }


# ----------------------------------------------------------------------------------------------- medida 1
def medida1_semilla(semilla: int, cfg: dict, mod32, contadores: dict) -> dict:
    """Metricas de la medida 1 de una semilla para todas las celdas. celda -> {metrica: valor|None, ...}.

    Los fallos de un ajuste no se tapan: la metrica queda None y el motivo se guarda en "fallos".
    """
    W, H = cfg["W"], cfg["H"]
    r_g = datos.simular_garch(cfg["n_garch"], datos.rng(semilla, datos.F_GARCH_REC), **datos.GARCH_VERDAD)
    r_r, s_r = datos.simular_regimen(cfg["n_reg"], datos.rng(semilla, datos.F_REG_REC))
    _, Yg, _ = datos.ventanas(r_g, W, H, cfg["paso_crps"])
    _, Yr, _ = datos.ventanas(r_r, W, H, cfg["paso_crps"])
    om = datos.GARCH_VERDAD["omega"]
    out = {}
    for cid, tipo, var in celdas():
        esc = var == "con"
        cont = contadores[cid]
        rg = redondear(r_g, tipo, escala=esc, contador=cont)
        rr = redondear(r_r, tipo, escala=esc, contador=cont)
        m = {k: None for k, _, _ in METRICAS_M1}
        fallos = []
        extra = {}
        try:
            e = ajustar_garch(rg)
            m["garch_persistencia"] = abs(e["alfa"] + e["beta"] - GARCH_PERSISTENCIA)
            m["garch_omega"] = abs(e["omega"] / om - 1.0)
            extra.update({"garch_alfa": e["alfa"], "garch_beta": e["beta"], "garch_omega_est": e["omega"], "garch_convergio": e["convergio"]})
        except Exception as exc:  # noqa: BLE001 - se publica el motivo
            fallos.append(f"garch: {type(exc).__name__}: {exc}")
        try:
            e = ajustar_hmm(rr)
            m.update({k: v for k, v in error_hmm(e, s_r).items()})
            extra.update({"hmm_convergio": e["convergio"]})
        except Exception as exc:  # noqa: BLE001
            fallos.append(f"hmm: {type(exc).__name__}: {exc}")
        for nombre, serie_t, serie_v, Y in (("crps_garch", rg, r_g, Yg), ("crps_regimen", rr, r_r, Yr)):
            try:
                X, _, _ = datos.ventanas(serie_t, W, H, cfg["paso_crps"])
                q = modelo.cono(mod32, X) * modelo.ESCALA_SALIDA
                if not np.isfinite(q).all():
                    raise ValueError("cono no finito")
                m[nombre] = modelo.crps_cuantiles(q, Y)
            except Exception as exc:  # noqa: BLE001
                fallos.append(f"{nombre}: {type(exc).__name__}: {exc}")
        out[cid] = {"metricas": m, "extra": extra, "fallos": fallos}
    out["_baseline"] = {
        "crps_garch": baseline_gauss(r_g, Yg),
        "crps_regimen": baseline_gauss(r_r, Yr),
    }
    return out


def baseline_gauss(serie: np.ndarray, Y: np.ndarray) -> float:
    """CRPS del cono gaussiano incondicional con la desviacion tipica de la propia serie (referencia de contexto)."""
    from scipy.stats import norm

    n, H = Y.shape
    q = norm.ppf(modelo.ALFAS)[None, None, :] * float(serie.std()) * np.sqrt(np.arange(1, H + 1))[None, :, None]
    return modelo.crps_cuantiles(np.broadcast_to(q, (n, H, modelo.J)), Y)


def _sd(x) -> float:
    return float(np.std(np.asarray(x, dtype=np.float64), ddof=1)) if len(x) > 1 else 0.0


def veredicto_m1(vals_t: list, vals_ref: list) -> dict:
    """Pierde si |media_s(m_T) - media_s(m_f64)| > max(sd_s(m_T), sd_s(m_f64)); sd con ddof = 1."""
    if any(v is None for v in vals_t) or any(v is None for v in vals_ref):
        n_t = sum(v is None for v in vals_t)
        return {"veredicto": "no medida", "motivo": f"ajuste fallido en {n_t} de {len(vals_t)} semillas del tipo", "media": None, "sd": None, "umbral": None, "cociente": None}
    mt, mr = float(np.mean(vals_t)), float(np.mean(vals_ref))
    sd_t, sd_r = _sd(vals_t), _sd(vals_ref)
    umbral = max(sd_t, sd_r)
    dif = abs(mt - mr)
    return {
        "veredicto": "pierde" if dif > umbral else "no pierde",
        "media": mt,
        "sd": sd_t,
        "dif": dif,
        "umbral": umbral,
        "cociente": (dif / umbral) if umbral > 0 else None,
    }


def agregar_m1(por_semilla: list[dict], contadores: dict) -> dict:
    ids = [c for c, _, _ in celdas()]
    res = {"entrada": {c: contadores[c].como_dict() for c in ids}, "metricas": {}, "no_medidas": {}}
    for mid, desc, unidad in METRICAS_M1:
        ref = [s["f64"]["metricas"][mid] for s in por_semilla]
        celdas_out = {}
        for c in ids:
            vals = [s[c]["metricas"][mid] for s in por_semilla]
            v = {"por_semilla": vals}
            if c == "f64":
                v.update({"veredicto": "referencia", "media": None if None in vals else float(np.mean(vals)), "sd": None if None in vals else _sd(vals)})
            else:
                v.update(veredicto_m1(vals, ref))
            celdas_out[c] = v
        res["metricas"][mid] = {"descripcion": desc, "unidad": unidad, "celdas": celdas_out}
    for mid, desc, motivo in NO_MEDIDAS_M1:
        res["no_medidas"][mid] = {"descripcion": desc, "veredicto": "no medida", "motivo": motivo}
    res["fallos"] = {c: [f for s in por_semilla for f in s[c]["fallos"]] for c in ids}
    res["no_convergen"] = {
        c: int(sum(1 for s in por_semilla for k in ("garch_convergio", "hmm_convergio") if s[c]["extra"].get(k) is False)) for c in ids
    }
    res["estimaciones_garch"] = {
        c: {k: [s[c]["extra"].get(k) for s in por_semilla] for k in ("garch_alfa", "garch_beta", "garch_omega_est")} for c in ids
    }
    return res


# ----------------------------------------------------------------------------------------------- medidas 2 y 3
def cantidades(Q: np.ndarray) -> dict:
    """Cantidades de la medida 2 (N, M) en log-rendimiento fisico desde el cono Q (N, H, J) en unidades del modelo."""
    P = Q * modelo.ESCALA_SALIDA
    N = P.shape[0]
    return {
        "q_todos": P.reshape(N, -1),
        "q_0005": P[:, :, 0],
        "q_0995": P[:, :, -1],
        "dq_todas": np.diff(P, axis=-1).reshape(N, -1),
        "dq_cola_inf": P[:, :, 1] - P[:, :, 0],
        "dq_cola_sup": P[:, :, -1] - P[:, :, -2],
    }


def _corr(a: np.ndarray, b: np.ndarray) -> float | None:
    """Correlacion de Pearson; None (no medida) si alguna serie es constante."""
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x)))) if x.size else float("nan")


def pasada_tipo(ref64, X: np.ndarray, tipo: str, esc: bool, contador: Contador, capas: list, lote: int = 128):
    """Cono con redondeo en cada frontera + error relativo (sumas de cuadrados) por capa frente al f64."""
    mT = modelo.modelo_redondeado(ref64, tipo, esc, contador)
    acc = {c: [0.0, 0.0] for c in capas}
    Qs = []
    with torch.no_grad():
        for i in range(0, len(X), lote):
            xb = torch.tensor(X[i : i + lote], dtype=torch.float64)
            ref = {}

            def h_ref(nombre, t, ref=ref):
                if nombre in acc:
                    ref[nombre] = t
                return t

            got = {}

            def h_t(nombre, t, got=got):
                r = torch.from_numpy(redondear(t.numpy(), tipo, escala=esc, por_muestra=True, contador=contador))
                if nombre in acc:
                    got[nombre] = r
                return r

            ref64(xb, h_ref)
            Qs.append(mT(xb, h_t).numpy())
            for c in capas:
                acc[c][0] += float(((got[c] - ref[c]) ** 2).sum())
                acc[c][1] += float((ref[c] ** 2).sum())
    err_rel = {c: float(np.sqrt(a / b)) if b > 0 else float("nan") for c, (a, b) in acc.items()}
    return np.concatenate(Qs, axis=0), err_rel


def nombres_capas(cfg: dict) -> list:
    out = ["emb"]
    for i in range(cfg["capas"]):
        out += [f"b{i}.attn", f"b{i}.res1", f"b{i}.mlp", f"b{i}.res2"]
    return out + ["ln_final", "cabeza", "salida"]


def veredicto_error(err: float | None, umbral: float, cobertura: float | None = None) -> dict:
    """Pierde si error > umbral o (medida 3) si la cobertura de puntos validos baja de COBERTURA_MIN.

    err None = no hay puntos validos con que calcularlo: solo es "no medida" si tampoco hay un criterio de cobertura.
    """
    cociente = err / umbral if err is not None and umbral > 0 else None
    if cobertura is not None and cobertura < COBERTURA_MIN:
        motivo = f"cobertura {100 * cobertura:.1f} % < {100 * COBERTURA_MIN:.0f} %"
        return {"error": err, "umbral": umbral, "cociente": cociente, "veredicto": "pierde", "motivo": motivo}
    if err is None:
        return {"error": None, "umbral": umbral, "cociente": None, "veredicto": "no medida"}
    return {"error": err, "umbral": umbral, "cociente": cociente, "veredicto": "pierde" if err > umbral else "no pierde"}


def medidas23(modelos32: list, X_eval: np.ndarray, cfg: dict, contadores: dict, log=print) -> tuple[dict, dict]:
    """Medidas 2 y 3 para las celdas de redondeo. Devuelve (m2, m3)."""
    ids = [c for c, t, _ in celdas() if t != "f64"]
    n_s = len(modelos32)
    refs = [modelo.a_f64(m) for m in modelos32]
    Qref = [modelo.cono(r, X_eval) for r in refs]
    capas = nombres_capas(cfg)
    # --- sensibilidad: el ancho del cono f64 a h = min(10, H) dias debe seguir a la volatilidad realizada de la ventana
    h_sens = min(10, Qref[0].shape[1]) - 1
    vol_ventana = np.sqrt((X_eval**2).mean(axis=1))
    corr_ancho = [_corr(Q[:, h_sens, -1] - Q[:, h_sens, 0], vol_ventana) for Q in Qref]
    # --- umbrales de la medida 2: ruido de semilla del propio modelo f64
    cant_ref = [cantidades(Q) for Q in Qref]
    umbral2 = {
        g: float(np.sqrt(np.mean(np.var(np.stack([c[g] for c in cant_ref]), axis=0, ddof=1)))) for g, _ in CANTIDADES_M2
    }
    # --- referencia y umbral de la medida 3: sigma_loc de los 5 modelos f64 en la rejilla comun de K, construida con la
    # interseccion (por entrada y trio de horizontes k-1, k, k+1) de los intervalos [S_h(0,10), S_h(0,90)] de los 5 modelos f64
    S_ref = [dupire.niveles_recentrados(Q)[0] for Q in Qref]
    K, estado_k = dupire.rejilla_k(np.stack(S_ref))
    k_fuera_f64 = [dupire.k_fuera_intervalo(S, K) for S in S_ref]
    if any(n for n, _ in k_fuera_f64):  # por construccion es 0; si no lo es, la rejilla no cumple la ficha: no se sigue
        raise RuntimeError(f"medida 3: hay K fuera del intervalo de un modelo f64 (por modelo: {[n for n, _ in k_fuera_f64]})")
    n_trios = int(estado_k.size)
    n_vacios = int((estado_k == dupire.REJILLA_VACIA).sum())
    n_degenerados = int((estado_k == dupire.REJILLA_DEGENERADA).sum())
    sig_ref = [dupire.sigma_loc(S, K) for S in S_ref]
    validos = np.all([np.isfinite(s) for s in sig_ref], axis=0)
    n_validos = int(validos.sum())
    if n_validos == 0:
        raise RuntimeError("medida 3: ningun punto de sigma_loc valido en los 5 modelos f64; la referencia no existe")
    umbral3 = float(np.sqrt(np.mean(np.var(np.stack([s[validos] for s in sig_ref]), axis=0, ddof=1))))
    c_ref = [dupire.niveles_recentrados(Q)[1] for Q in Qref]
    # --- por celda y semilla
    err2 = {c: {g: [] for g, _ in CANTIDADES_M2} for c in ids}
    capa_err = {c: {k: [] for k in capas} for c in ids}
    anulan = {c: [] for c in ids}
    signo = {c: [] for c in ids}
    err3 = {c: [] for c in ids}
    cob3 = {c: [] for c in ids}
    k_fuera = {c: [0, 0] for c in ids}  # K fuera del intervalo propio del cono redondeado (dato informativo), total de K
    fac = {c: [] for c in ids}
    for s in range(n_s):
        for cid, tipo, var in celdas(incluir_f64=False):
            Q, e_rel = pasada_tipo(refs[s], X_eval, tipo, var == "con", contadores[cid], capas)
            for k, v in e_rel.items():
                capa_err[cid][k].append(v)
            cant = cantidades(Q)
            for g, _ in CANTIDADES_M2:
                err2[cid][g].append(_rms(cant[g] - cant_ref[s][g]))
            d, dr = cant["dq_todas"], cant_ref[s]["dq_todas"]
            anulan[cid].append(float(100.0 * np.mean((d == 0) & (dr > 0))))
            signo[cid].append(float(100.0 * np.mean(d * dr < 0)))
            S_t, c_t = dupire.niveles_recentrados(Q)
            fac[cid].append(c_t.ravel() / c_ref[s].ravel())
            sig = dupire.sigma_loc(S_t, K)
            nf, nt = dupire.k_fuera_intervalo(S_t, K)
            k_fuera[cid][0] += nf
            k_fuera[cid][1] += nt
            ok = validos & np.isfinite(sig)
            cob3[cid].append(float(ok.sum() / n_validos))
            err3[cid].append(_rms((sig - sig_ref[s])[ok]) if ok.any() else None)
            log(f"  M2/M3 semilla {s + 1}/{n_s} {cid}: q_todos err={err2[cid]['q_todos'][-1]:.3e} cobertura sigma_loc={cob3[cid][-1]:.3f}")
    m2 = {
        "capas": capas,
        "sensibilidad_vol": {"horizonte_dias": h_sens + 1, "corr_ancho_vol_f64": corr_ancho},
        "cantidades": {},
        "entrada": {c: contadores[c].como_dict() for c in ids},
        "error_capa": {c: {k: float(np.median(v)) for k, v in capa_err[c].items()} for c in ids},
        "diferencias_contiguas": {
            c: {"se_anulan_pct": float(np.mean(anulan[c])), "cambian_signo_pct": float(np.mean(signo[c]))} for c in ids
        },
    }
    for g, desc in CANTIDADES_M2:
        m2["cantidades"][g] = {
            "descripcion": desc,
            "umbral": umbral2[g],
            "celdas": {c: veredicto_error(float(np.median(err2[c][g])), umbral2[g]) for c in ids},
        }
    sig_celdas = {}
    for c in ids:
        errs = [e for e in err3[c] if e is not None]
        e_med = float(np.median(errs)) if len(errs) == len(err3[c]) and errs else None
        sig_celdas[c] = veredicto_error(e_med, umbral3, float(np.median(cob3[c])))
        sig_celdas[c]["cobertura"] = float(np.median(cob3[c]))
        sig_celdas[c]["k_fuera_intervalo_propio_n"] = int(k_fuera[c][0])
        sig_celdas[c]["k_fuera_intervalo_propio_pct"] = float(100.0 * k_fuera[c][0] / k_fuera[c][1]) if k_fuera[c][1] else None
        f = np.concatenate(fac[c])
        sig_celdas[c]["factor_recentrado_rel_mediana"] = float(np.median(f))
        sig_celdas[c]["factor_recentrado_rel_max_dev"] = float(np.max(np.abs(f - 1.0)))
    cf = np.concatenate([x.ravel() for x in c_ref])
    m3 = {
        "descripcion": "sigma_loc(K, h) por Dupire, anualizada, en la rejilla de K comun (interseccion de los intervalos [S_h(0,10), S_h(0,90)] de los modelos f64)",
        "n_entradas": int(X_eval.shape[0]),
        "horizontes_dias": [int(i + 2) for i in range(modelos32[0].H - 2)],
        "nk": dupire.NK,
        "dens_min": dupire.DENS_MIN,
        "rejilla_k": {
            "ancho_min": dupire.ANCHO_K_MIN,
            "trios": n_trios,
            "trios_interseccion_vacia": n_vacios,
            "trios_interseccion_degenerada": n_degenerados,
            "k_fuera_intervalo_f64_n": int(sum(n for n, _ in k_fuera_f64)),
            "k_total": int(k_fuera_f64[0][1]),
        },
        "cobertura_min": COBERTURA_MIN,
        "puntos_rejilla": int(validos.size),
        "puntos_validos_f64_pct": float(100.0 * n_validos / validos.size),
        "puntos_validos_por_modelo_f64_pct": [float(100.0 * np.isfinite(s).mean()) for s in sig_ref],
        "sigma_loc_f64_mediana": float(np.median(np.stack([s[validos] for s in sig_ref]))),
        "factor_recentrado_f64": {"mediana": float(np.median(cf)), "min": float(cf.min()), "max": float(cf.max())},
        "umbral": umbral3,
        "celdas": sig_celdas,
        "delta_aad": {
            "veredicto": "no medida",
            "motivo": "no medida: requiere AAD (engine-nn); no hay diferenciacion automatica del cono hasta engine-nn",
        },
    }
    return m2, m3
