"""sigma_loc por Dupire a partir del cono de cuantiles (medida 3), con el procedimiento fijo de la ficha.

S0 = 1, tipos cero, h en anios (dias/252). Para cada entrada n y horizonte h:
  S_h(alfa) = exp(q(alfa, h)); recentrado multiplicativo para que la media discreta sum_j w_j S_j sea 1.
  C(K, h) = sum_j w_j (S_j - K)+   (trapecio en alfa; la masa fuera de [0.005, 0.995] va al cuantil extremo).
  Rejilla de K (comun a todos los modelos y tipos, que es lo que permite compararlos): nK puntos equiespaciados
  en la INTERSECCION, por entrada y trio de horizontes k-1, k, k+1 (los que se usan para derivar en h y en K), de
  los intervalos [S_h(0.10), S_h(0.90)] de los M modelos f64 (uno por semilla): [max S_h(0.10), min S_h(0.90)]
  sobre modelos y horizontes. Asi todo K cae dentro del intervalo de cada modelo f64 a los tres horizontes. Si la
  interseccion es vacia o su ancho es menor que ANCHO_K_MIN (degenerada), ese trio no tiene rejilla (K = NaN) y
  sus puntos cuentan como fuera de la region valida; se publican, nunca se rellenan.
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
ANCHO_K_MIN = 1e-4  # ancho minimo declarado de la interseccion (S0 = 1): por debajo la rejilla es degenerada y no se usa
I10 = int(np.argmin(np.abs(ALFAS - 0.10)))
I90 = int(np.argmin(np.abs(ALFAS - 0.90)))
REJILLA_OK, REJILLA_VACIA, REJILLA_DEGENERADA = 0, 1, 2  # estado de cada trio (entrada, k)


def niveles_recentrados(q_modelo: np.ndarray, w: np.ndarray = W_ALFA) -> tuple[np.ndarray, np.ndarray]:
    """S_h(alfa) recentrado y el factor c (N, H) tal que sum_j w_j c S_j = 1. q en unidades del modelo."""
    S = np.exp(q_modelo * ESCALA_SALIDA)
    c = 1.0 / (S * w).sum(axis=-1)
    return S * c[..., None], c


def limites_k(S_modelos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Limites (lo, hi) de (N, H-2) de la interseccion de [S_h(0.10), S_h(0.90)] sobre los M modelos y los horizontes k-1, k, k+1.

    S_modelos (M, N, H, J): niveles recentrados de M modelos (M = 1 da el intervalo propio de un cono).
    """
    S = np.asarray(S_modelos, dtype=np.float64)
    if S.ndim != 4:
        raise ValueError(f"S_modelos debe ser (M, N, H, J), recibido {S.shape}")
    a = np.stack([S[:, :, :-2, I10], S[:, :, 1:-1, I10], S[:, :, 2:, I10]])  # (3, M, N, H-2)
    b = np.stack([S[:, :, :-2, I90], S[:, :, 1:-1, I90], S[:, :, 2:, I90]])
    return a.max(axis=(0, 1)), b.min(axis=(0, 1))


def rejilla_k(S_modelos: np.ndarray, nk: int = NK) -> tuple[np.ndarray, np.ndarray]:
    """Rejilla de K (N, H-2, nk) para los horizontes interiores k = 1..H-2 (indices de 0) y el estado de cada trio.

    Comun a los M modelos f64 de S_modelos (M, N, H, J) y a los tres horizontes k-1, k, k+1 (ver el docstring del modulo).
    estado (N, H-2): REJILLA_OK, REJILLA_VACIA (interseccion vacia o no finita) o REJILLA_DEGENERADA (ancho < ANCHO_K_MIN);
    donde no es OK, K = NaN.
    """
    lo, hi = limites_k(S_modelos)
    ancho = hi - lo
    estado = np.where(ancho >= ANCHO_K_MIN, REJILLA_OK, np.where(ancho > 0, REJILLA_DEGENERADA, REJILLA_VACIA))
    with np.errstate(invalid="ignore"):
        K = lo[..., None] + ancho[..., None] * np.linspace(0.0, 1.0, nk)
        K = np.clip(K, lo[..., None], hi[..., None])  # el redondeo de lo + (hi - lo) puede pasarse de hi por 1 ulp
    return np.where((estado == REJILLA_OK)[..., None], K, np.nan), estado


def k_fuera_intervalo(S: np.ndarray, K: np.ndarray) -> tuple[int, int]:
    """(n fuera, n total) de los K finitos de K (N, H-2, nk) que quedan fuera del intervalo PROPIO de un cono S (N, H, J).

    El intervalo propio es [max S_h(0.10), min S_h(0.90)] sobre los horizontes k-1, k, k+1 de ese cono.
    Con los f64 que definen la rejilla es 0 por construccion; para un tipo redondeado es un dato informativo.
    """
    lo, hi = limites_k(np.asarray(S)[None])
    finito = np.isfinite(K)
    with np.errstate(invalid="ignore"):
        fuera = finito & ((K < lo[..., None]) | (K > hi[..., None]))
    return int(fuera.sum()), int(finito.sum())


def sigma_loc(S: np.ndarray, K: np.ndarray, w: np.ndarray = W_ALFA, dens_min: float = DENS_MIN) -> np.ndarray:
    """sigma_loc (N, H-2, nk-2) en los K interiores de la rejilla; NaN fuera de la region valida.

    S (N, H, J): niveles recentrados; el horizonte de indice i corresponde a h = (i+1)/252 anios.
    K (N, H-2, nk): rejilla de rejilla_k (NaN o lo >= hi: rejilla vacia o degenerada y todo es NaN ahi).
    """
    N, H, _ = S.shape
    nk = K.shape[-1]
    out = np.full((N, H - 2, nk - 2), np.nan)
    dh = 2.0 / DIAS_ANIO
    for k in range(1, H - 1):
        Kk = K[:, k - 1, :]  # (N, nk)
        # C a los horizontes k-1, k, k+1 en la misma rejilla: (N, 3, nk)
        with np.errstate(invalid="ignore"):
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
