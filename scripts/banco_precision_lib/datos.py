"""Datos sinteticos con verdad conocida (TS-00-PREC): GARCH(1,1) y cambio de regimen de 2 estados.

Todo se genera desde una semilla con numpy.random.default_rng([semilla, flujo]); el flujo separa los
usos (recuperacion, entrenamiento, evaluacion) para que cambiar un tamano no mueva los demas.
"""
from __future__ import annotations

import numpy as np

DIAS_ANIO = 252.0

# Verdad del GARCH(1,1): vol diaria incondicional sqrt(omega/(1-alfa-beta)) = 1 %.
GARCH_VERDAD = {"omega": 2.0e-6, "alfa": 0.08, "beta": 0.90}
# Verdad del cambio de regimen: estado 0 = calma, estado 1 = estres (vol anualizada creciente).
REGIMEN_VERDAD = {
    "P": ((0.98, 0.02), (0.04, 0.96)),
    "mu": (0.08, -0.10),  # anualizado
    "sigma": (0.08, 0.30),  # anualizado
}

# Flujos de aleatoriedad (el segundo elemento de default_rng).
F_GARCH_REC, F_REG_REC, F_GARCH_ENT, F_REG_ENT, F_LOTES, F_GARCH_EVAL, F_REG_EVAL = 1, 2, 3, 4, 5, 6, 7


def rng(semilla: int, flujo: int) -> np.random.Generator:
    return np.random.default_rng([int(semilla), int(flujo)])


def simular_garch(n: int, gen: np.random.Generator, omega: float, alfa: float, beta: float, quemado: int = 500) -> np.ndarray:
    """r_t = sqrt(h_t) z_t, h_t = omega + alfa r_{t-1}^2 + beta h_{t-1}, z normal. Devuelve n log-rendimientos."""
    z = gen.standard_normal(n + quemado)
    r = np.empty(n + quemado)
    h = omega / (1.0 - alfa - beta)
    for t in range(n + quemado):
        r[t] = np.sqrt(h) * z[t]
        h = omega + alfa * r[t] * r[t] + beta * h
    return r[quemado:]


def simular_regimen(n: int, gen: np.random.Generator, P=None, mu=None, sigma=None) -> tuple[np.ndarray, np.ndarray]:
    """Log-rendimientos diarios de un GBM con cambio de regimen (2 estados, cadena de Markov por dia).

    Devuelve (r, s) con s el estado verdadero de cada dia. El estado inicial sale de la distribucion
    estacionaria de P. r = (mu - sigma^2/2)/252 + sigma/sqrt(252) z.
    """
    P = np.asarray(REGIMEN_VERDAD["P"] if P is None else P, dtype=np.float64)
    mu = np.asarray(REGIMEN_VERDAD["mu"] if mu is None else mu, dtype=np.float64)
    sigma = np.asarray(REGIMEN_VERDAD["sigma"] if sigma is None else sigma, dtype=np.float64)
    pi0 = P[1, 0] / (P[0, 1] + P[1, 0])  # estacionaria de la cadena de 2 estados: P(estado 0)
    u = gen.random(n)
    z = gen.standard_normal(n)
    s = np.empty(n, dtype=np.int64)
    s[0] = 0 if u[0] < pi0 else 1
    for t in range(1, n):
        s[t] = 0 if u[t] < P[s[t - 1], 0] else 1
    r = (mu[s] - 0.5 * sigma[s] ** 2) / DIAS_ANIO + sigma[s] / np.sqrt(DIAS_ANIO) * z
    return r, s


def niveles(r: np.ndarray, s0: float = 100.0) -> np.ndarray:
    """Niveles S0*exp(cumsum(r)) con S0 como primer valor (len(r)+1 puntos), como los consume el HMM."""
    return s0 * np.exp(np.concatenate([[0.0], np.cumsum(r)]))


def ventanas(r: np.ndarray, W: int, H: int, paso: int, inicio: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ventanas de W rendimientos y objetivos acumulados a h = 1..H dias.

    Devuelve (X (n, W), Y (n, H), fin (n,)): X[i] = r[t-W+1..t], Y[i, h-1] = sum r[t+1..t+h], fin[i] = t.
    """
    fin = np.arange(inicio + W - 1, len(r) - H, paso)
    X = r[fin[:, None] + np.arange(-W + 1, 1)[None, :]]
    Y = np.cumsum(r[fin[:, None] + np.arange(1, H + 1)[None, :]], axis=1)
    return X, Y, fin


def corpus_entrenamiento(semilla: int, cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    """Serie concatenada de entrenamiento (mitad GARCH, mitad regimen) y posiciones de fin validas.

    Devuelve (R, validos): R concatena n_series_ent series de cada familia de n_ent puntos; validos son
    los indices t con ventana y horizonte completos dentro de una misma serie.
    """
    gg, gr = rng(semilla, F_GARCH_ENT), rng(semilla, F_REG_ENT)
    series = []
    for _ in range(cfg["n_series_ent"]):
        series.append(simular_garch(cfg["n_ent"], gg, **GARCH_VERDAD))
        series.append(simular_regimen(cfg["n_ent"], gr)[0])
    W, H = cfg["W"], cfg["H"]
    R = np.concatenate(series)
    validos = []
    for i, s in enumerate(series):
        base = i * cfg["n_ent"]
        validos.append(base + np.arange(W - 1, len(s) - H))
    return R, np.concatenate(validos)
