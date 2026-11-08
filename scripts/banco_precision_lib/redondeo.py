"""Redondeo emulado a fp8 (e4m3/e5m2), bf16, f16 y f32 en CPU: UNA sola funcion para todo el banco.

redondear(x, tipo) = recorte a +-(maximo finito del tipo) y despues ida y vuelta f64 -> tipo -> f64
con ml_dtypes (o numpy para f32). El recorte emula fp8 con saturacion y evita los NaN de desbordamiento
de e4m3fn (maximo 448, sin infinitos).

Limitacion conocida de ml_dtypes 0.6.0: el cast f64 -> fp8/bf16 pasa por f32, de modo que un valor a menos
de 2^-24 (relativo) de un empate se redondea como si estuviera en el empate (doble redondeo). Afecta a
~1e-6 de los valores y no mueve el error relativo maximo por encima de u*(1+2^-23).
"""
from __future__ import annotations


import ml_dtypes
import numpy as np

# f64 es la referencia (identidad); el resto son los tipos que se emulan.
TIPOS = ("f32", "bf16", "f16", "e4m3", "e5m2")
VARIANTES = ("sin", "con")  # sin escala / con escala por tensor

DTYPE = {
    "f32": np.float32,
    "bf16": ml_dtypes.bfloat16,
    "f16": np.float16,
    "e4m3": ml_dtypes.float8_e4m3fn,
    "e5m2": ml_dtypes.float8_e5m2,
}
MAXIMO = {t: float(ml_dtypes.finfo(d).max) for t, d in DTYPE.items()}
MANTISA = {t: int(ml_dtypes.finfo(d).nmant) for t, d in DTYPE.items()}
# Error relativo maximo teorico del redondeo al mas cercano en valores normales: u = 2^-(mantisa+1).
U = {t: 2.0 ** -(MANTISA[t] + 1) for t in TIPOS}
# Menor valor normal y menor subnormal positivo de cada tipo.
MIN_NORMAL = {t: float(ml_dtypes.finfo(d).tiny) for t, d in DTYPE.items()}
MIN_SUBNORMAL = {t: float(ml_dtypes.finfo(d).smallest_subnormal) for t, d in DTYPE.items()}


class Contador:
    """Acumula cuantos valores se recortaron y cuantos no nulos acabaron en cero."""

    def __init__(self) -> None:
        self.n = 0
        self.n_recortados = 0
        self.n_no_nulos = 0
        self.n_a_cero = 0
        self.n_nan = 0

    def como_dict(self) -> dict:
        return {
            "n": int(self.n),
            "recortados_pct": 100.0 * self.n_recortados / self.n if self.n else 0.0,
            "no_nulos_a_cero_pct": 100.0 * self.n_a_cero / self.n_no_nulos if self.n_no_nulos else 0.0,
            "nan": int(self.n_nan),
        }


def _escala_pot2(amax: np.ndarray, maximo: float) -> np.ndarray:
    """Potencia de 2 s tal que amax*s <= maximo (la mayor). Devuelve 1 si amax no es finito o es 0."""
    amax = np.asarray(amax, dtype=np.float64)
    ok = np.isfinite(amax) & (amax > 0)
    seguro = np.where(ok, amax, 1.0)
    e = np.floor(np.log2(maximo / seguro))
    e = np.clip(e, -1000.0, 1000.0)
    e = np.where(seguro * 2.0**e > maximo, e - 1.0, e)  # guarda contra el redondeo de log2
    return np.where(ok, 2.0**e, 1.0)


def redondear(x, tipo: str, escala: bool = False, por_muestra: bool = False, contador: Contador | None = None):
    """Redondea x (se lleva a f64) al tipo y devuelve f64.

    tipo: "f64" (identidad), "f32", "bf16", "f16", "e4m3", "e5m2".
    escala: variante con escala. Se escala por una potencia de 2 (sin error de escalado) para que el
      maximo absoluto del tensor quepa en el maximo finito del tipo, se redondea y se desescala.
    por_muestra: con escala, el maximo se toma por muestra (eje 0) en vez de por todo el tensor.
    contador: acumula el porcentaje de valores recortados y de no nulos que acaban en cero.
    """
    x = np.asarray(x, dtype=np.float64)
    if tipo == "f64":
        if contador is not None:
            contador.n += x.size
            contador.n_nan += int(np.isnan(x).sum())
        return x
    if tipo not in DTYPE:
        raise ValueError(f"tipo desconocido: {tipo!r}")
    m = MAXIMO[tipo]
    if escala and x.size:
        if por_muestra and x.ndim > 1:
            amax = np.max(np.abs(x), axis=tuple(range(1, x.ndim)), keepdims=True)
        else:
            amax = np.max(np.abs(x))
        s = _escala_pot2(amax, m)
    else:
        s = 1.0
    y = x * s
    recortado = np.abs(y) > m
    z = np.clip(y, -m, m).astype(DTYPE[tipo]).astype(np.float64)
    if contador is not None:
        no_nulo = x != 0
        contador.n += x.size
        contador.n_recortados += int(recortado.sum())
        contador.n_no_nulos += int(no_nulo.sum())
        contador.n_a_cero += int((no_nulo & (z == 0)).sum())
        contador.n_nan += int(np.isnan(x).sum())
    return z / s


def celda_id(tipo: str, variante: str) -> str:
    """Identificador de columna: "f64" o "<tipo>:<sin|con>"."""
    return "f64" if tipo == "f64" else f"{tipo}:{variante}"


def celdas(incluir_f64: bool = True) -> list[tuple[str, str, str]]:
    """Lista (id, tipo, variante) de todas las columnas del banco, con f64 primero."""
    out = [("f64", "f64", "sin")] if incluir_f64 else []
    for t in TIPOS:
        for v in VARIANTES:
            out.append((celda_id(t, v), t, v))
    return out
