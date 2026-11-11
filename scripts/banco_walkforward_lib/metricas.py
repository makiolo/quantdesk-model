"""Metricas del banco (por activo, horizonte y modelo).

- Niveles de cuantil: los 21 de Chronos-2 (0,01, 0,05, 0,10, ..., 0,95, 0,99). Todos los modelos se evaluan sobre
  esos 21 cuantiles; los modelos por muestras (HMM, GARCH) los sacan de sus muestras con numpy.quantile (lineal).
- pinball_a(y, q) = (1{y < q} - a) (q - y).
- CRPS por cuantiles: CRPS_q = (2 / |L|) * suma_a pinball_a, con L los 21 niveles (aproximacion de
  CRPS = 2 * integral_0^1 pinball_u du con una regla de cuantiles NO uniforme: pesa algo mas las colas que la
  integral exacta). Misma definicion para todos los modelos.
- VaR 1 %: excedencia si y < q_0,01; VaR 99 %: excedencia si y > q_0,99.
- Kupiec (POF): LR_uc = -2 ln[(1-p)^(n-x) p^x] + 2 ln[(1-x/n)^(n-x) (x/n)^x] ~ chi2(1).
- Christoffersen (independencia): LR_ind = -2 ln[(1-pi)^(n00+n10) pi^(n01+n11)]
  + 2 ln[(1-pi0)^n00 pi0^n01 (1-pi1)^n10 pi1^n11] ~ chi2(1); sin excedencias o sin transiciones desde un 1 el
  p-valor no esta definido y se devuelve NaN.
- Vol: varianza predicha a h = ((q_0,90 - q_0,10) / (2 z_0,90))^2 (equivalente normal del rango interdecil, el
  mismo estimador para todos los modelos); varianza realizada RV_h = suma de los h rendimientos logaritmicos
  diarios al cuadrado posteriores al origen (proxy condicionalmente insesgado, Patton 2011).
  QLIKE = ln(s2) + RV / s2 (forma de Patton sin la constante; admite RV = 0; menor es mejor).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.stats import chi2

NIVELES = (0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
           0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99)
I01, I10, I50, I90, I99 = 0, 2, 10, 18, 20
Z90 = 1.2815515655446004
DECILES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
IDECILES = [NIVELES.index(p) for p in DECILES]
COLUMNAS_RESUMEN = ("n", "crps", "pinball_01", "pinball_99", "exc_01", "exc_99", "n_test", "x_01", "x_99",
                    "kupiec_01_p", "kupiec_99_p", "christ_01_p", "christ_99_p", "qlike")
MOTIVO_FINCAST = ("FinCast: solo crps_deciles y QLIKE en ventana limpia; crps de 21 niveles y criterios de "
                  "colas no aplicables porque incluyen cuantiles interpolados/extrapolados")


def pinball(y, q, a):
    y = np.asarray(y, float)
    q = np.asarray(q, float)
    return ((y < q).astype(float) - a) * (q - y)


def crps_cuantiles(y, Q, niveles=NIVELES):
    """y: (n,), Q: (n, L). CRPS_q por fila."""
    Q = np.asarray(Q, float)
    y = np.asarray(y, float)[:, None]
    a = np.asarray(niveles, float)[None, :]
    pb = ((y < Q).astype(float) - a) * (Q - y)
    return 2.0 * pb.mean(axis=1)


def crps_deciles(y, Q):
    """2 * media de los 9 pinball nativos (0.1..0.9), con el mismo peso para cada decil."""
    return crps_cuantiles(y, np.asarray(Q, float)[:, IDECILES], DECILES)


def resumen_fincast(y, Q, rv):
    """No llama a ningun criterio de colas ni al CRPS de 21 niveles; exclusiones declaradas por celda."""
    s2 = var_desde_cuantiles(Q)
    if not np.isfinite(s2).all() or (s2 <= 0).any():
        raise ValueError("FinCast QLIKE no definido: varianza q10/q90 no positiva o no finita")
    r = dict.fromkeys(COLUMNAS_RESUMEN, float("nan"))
    r.update(n=len(y), crps_deciles=float(np.mean(crps_deciles(y, Q))),
             qlike=float(np.mean(qlike(rv, s2))), criterios_no_aplicables=MOTIVO_FINCAST)
    return r


def _xlogy(x, y):
    return 0.0 if x == 0 else x * math.log(y)


def kupiec(hits, p):
    """(LR, p-valor) del test POF de Kupiec. hits: secuencia 0/1."""
    h = np.asarray(hits, int)
    n, x = len(h), int(h.sum())
    if n == 0:
        return float("nan"), float("nan")
    l0 = _xlogy(n - x, 1 - p) + _xlogy(x, p)
    ph = x / n
    l1 = _xlogy(n - x, 1 - ph) + _xlogy(x, ph)
    lr = max(2.0 * (l1 - l0), 0.0)
    return lr, float(chi2.sf(lr, 1))


def christoffersen(hits):
    """(LR_ind, p-valor) del test de independencia de Christoffersen; NaN si no esta definido."""
    h = np.asarray(hits, int)
    if len(h) < 2 or h.sum() == 0:
        return float("nan"), float("nan")
    a, b = h[:-1], h[1:]
    n00 = int(np.sum((a == 0) & (b == 0)))
    n01 = int(np.sum((a == 0) & (b == 1)))
    n10 = int(np.sum((a == 1) & (b == 0)))
    n11 = int(np.sum((a == 1) & (b == 1)))
    if n10 + n11 == 0 or n00 + n01 == 0:
        return float("nan"), float("nan")
    pi0 = n01 / (n00 + n01)
    pi1 = n11 / (n10 + n11)
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    l0 = _xlogy(n00 + n10, 1 - pi) + _xlogy(n01 + n11, pi)
    l1 = _xlogy(n00, 1 - pi0) + _xlogy(n01, pi0) + _xlogy(n10, 1 - pi1) + _xlogy(n11, pi1)
    lr = max(2.0 * (l1 - l0), 0.0)
    return lr, float(chi2.sf(lr, 1))


def var_desde_cuantiles(Q):
    Q = np.asarray(Q, float)
    return ((Q[:, I90] - Q[:, I10]) / (2.0 * Z90)) ** 2


def qlike(rv, s2):
    s2 = np.asarray(s2, float)
    return np.log(s2) + np.asarray(rv, float) / s2


def submuestra_sin_solape(k, h):
    """Indices (en el orden dado, creciente en k) de una submuestra de origenes cuyas ventanas de h barras no se
    solapan: se conserva un origen si su barra k esta al menos h barras despues de la del ultimo conservado."""
    keep, last = [], None
    for i, ki in enumerate(k):
        if last is None or ki >= last + h:
            keep.append(i)
            last = ki
    return np.asarray(keep, int)


def resumen_celda(y, Q, rv, k, h):
    """Todas las metricas de una celda (activo, horizonte, modelo) sobre n origenes."""
    y = np.asarray(y, float)
    Q = np.asarray(Q, float)
    s2 = var_desde_cuantiles(Q)
    lo = (y < Q[:, I01]).astype(int)
    hi = (y > Q[:, I99]).astype(int)
    sub = submuestra_sin_solape(np.asarray(k), h)
    ku01 = kupiec(lo[sub], 0.01)[1]
    ku99 = kupiec(hi[sub], 0.01)[1]
    ch01 = christoffersen(lo[sub])[1]
    ch99 = christoffersen(hi[sub])[1]
    return {
        "n": int(len(y)),
        "crps": float(np.mean(crps_cuantiles(y, Q))),
        "pinball_01": float(np.mean(pinball(y, Q[:, I01], 0.01))),
        "pinball_99": float(np.mean(pinball(y, Q[:, I99], 0.99))),
        "exc_01": float(lo.mean()),
        "exc_99": float(hi.mean()),
        "n_test": int(len(sub)),
        "x_01": int(lo[sub].sum()),
        "x_99": int(hi[sub].sum()),
        "kupiec_01_p": ku01,
        "kupiec_99_p": ku99,
        "christ_01_p": ch01,
        "christ_99_p": ch99,
        "qlike": float(np.mean(qlike(rv, s2))),
    }
