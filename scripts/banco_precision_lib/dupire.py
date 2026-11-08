"""sigma_loc por Dupire a partir del cono de cuantiles (medida 3), con el procedimiento fijo de la ficha.

S0 = 1, tipos cero, h en anios (dias/252). Para cada entrada n y horizonte h:
  S_h(alfa) = exp(q(alfa, h)); recentrado multiplicativo para que la media discreta sum_j w_j S_j sea 1.
  C(K, h) = sum_j w_j (S_j - K)+   (trapecio en alfa; la masa fuera de [0.005, 0.995] va al cuantil extremo).
  Rejilla de K: nK puntos equiespaciados en [max_h S_h(0.10), min_h S_h(0.90)] sobre los horizontes
  k-1, k, k+1 (los que se usan para derivar en h y para derivar en K).
  dC/dh por diferencias centradas entre k-1 y k+1; d2C/dK2 por diferencias centradas en K sobre la rejilla.
  sigma_loc^2 = 2 dC/dh / (K^2 d2C/dK2) solo donde d2C/dK2 > DENS_MIN y dC/dh > 0 (region valida).
Los puntos fuera de la region valida son NaN en la salida y se cuentan, no se rellenan.
"""
from __future__ import annotations

import numpy as np

from .datos import DIAS_ANIO
from .modelo import ALFAS, ESCALA_SALIDA, W_ALFA

NK = 9  # puntos de la rejilla de K; sigma_loc se evalua en los NK-2 interiores
DENS_MIN = 0.5  # umbral declarado de d2C/dK2 (densidad de S_h respecto de K, con S0 = 1)
I10 = int(np.argmin(np.abs(ALFAS - 0.10)))
I90 = int(np.argmin(np.abs(ALFAS - 0.90)))


def niveles_recentrados(q_modelo: np.ndarray, w: np.ndarray = W_ALFA) -> tuple[np.ndarray, np.ndarray]:
    """S_h(alfa) recentrado y el factor c (N, H) tal que sum_j w_j c S_j = 1. q en unidades del modelo."""
    S = np.exp(q_modelo * ESCALA_SALIDA)
    c = 1.0 / (S * w).sum(axis=-1)
    return S * c[..., None], c


def rejilla_k(S_consenso: np.ndarray, nk: int = NK) -> np.ndarray:
    """Rejilla de K (N, H-2, nk) para los horizontes interiores k = 1..H-2 (indices de 0), comun a k-1, k, k+1."""
    lo = np.maximum(np.maximum(S_consenso[:, :-2, I10], S_consenso[:, 1:-1, I10]), S_consenso[:, 2:, I10])
    hi = np.minimum(np.minimum(S_consenso[:, :-2, I90], S_consenso[:, 1:-1, I90]), S_consenso[:, 2:, I90])
    t = np.linspace(0.0, 1.0, nk)
    return lo[..., None] + (hi - lo)[..., None] * t


def sigma_loc(S: np.ndarray, K: np.ndarray, w: np.ndarray = W_ALFA, dens_min: float = DENS_MIN) -> np.ndarray:
    """sigma_loc (N, H-2, nk-2) en los K interiores de la rejilla; NaN fuera de la region valida.

    S (N, H, J): niveles recentrados; el horizonte de indice i corresponde a h = (i+1)/252 anios.
    K (N, H-2, nk): rejilla de rejilla_k (si lo >= hi la rejilla es degenerada y todo es NaN ahi).
    """
    N, H, _ = S.shape
    nk = K.shape[-1]
    out = np.full((N, H - 2, nk - 2), np.nan)
    dh = 2.0 / DIAS_ANIO
    for k in range(1, H - 1):
        Kk = K[:, k - 1, :]  # (N, nk)
        # C a los horizontes k-1, k, k+1 en la misma rejilla: (N, 3, nk)
        C = (np.maximum(S[:, k - 1 : k + 2, :, None] - Kk[:, None, None, :], 0.0) * w[None, None, :, None]).sum(axis=2)
        dK = Kk[:, 1] - Kk[:, 0]
        dCdh = (C[:, 2, 1:-1] - C[:, 0, 1:-1]) / dh
        d2C = (C[:, 1, 2:] - 2.0 * C[:, 1, 1:-1] + C[:, 1, :-2]) / np.where(dK > 0, dK, np.nan)[:, None] ** 2
        K2 = Kk[:, 1:-1] ** 2
        with np.errstate(divide="ignore", invalid="ignore"):
            var = 2.0 * dCdh / (K2 * d2C)
        ok = (d2C > dens_min) & (dCdh > 0) & np.isfinite(var) & (var > 0) & (dK > 0)[:, None]
        out[:, k - 1, :] = np.where(ok, np.sqrt(np.where(ok, var, 0.0)), np.nan)
    return out
