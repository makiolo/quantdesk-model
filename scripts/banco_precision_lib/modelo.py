"""Transformer pequeno que predice el cono de cuantiles q(alfa, h) desde una ventana de log-rendimientos.

Arquitectura (pre-LN, solo codificador, atencion completa sobre la ventana):
  x (B, W) -> x/0.01 -> Linear(2, d) sobre (x, |x|) + posicion aprendida
  -> L bloques [LN, MHA(nh), +, LN, MLP(ff, GELU), +]
  -> lectura = ultimo token + media de tokens -> LN final -> Linear(d, H*J) -> (B, H, J) crudos
  cono monotono en alfa por construccion: mediana m_h = crudo del nodo alfa=0.5; los J-1 huecos entre nodos
  contiguos son softplus(crudo) > 0 y se acumulan hacia arriba (suma) y hacia abajo (resta) desde la mediana.
La salida esta en UNIDADES DEL MODELO (multiplos del 1 % de log-rendimiento acumulado); el log-rendimiento
fisico es ESCALA_SALIDA * salida. Los rendimientos de entrada se dividen por la misma constante.

forward(x, hook): cada tensor que se escribe entre operaciones pasa por hook(nombre, tensor); con
hook=None es el modelo ordinario (entrenamiento en f32). El banco de precision inyecta ahi el redondeo.
"""
from __future__ import annotations

import copy
import math

import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import norm
from torch import nn

from .redondeo import Contador, redondear

ESCALA_SALIDA = 0.01  # 1 % de log-rendimiento = 1 unidad del modelo

# Rejilla de alfa (J = 41): colas finas, centro cada 0.025. Incluye 0.005, 0.10, 0.50, 0.90 y 0.995.
ALFAS = np.array(
    [0.005, 0.01, 0.025, 0.05] + [float(a) for a in np.round(np.linspace(0.10, 0.90, 33), 6)] + [0.95, 0.975, 0.99, 0.995]
)
J = len(ALFAS)
J_MED = int(np.argmin(np.abs(ALFAS - 0.5)))


def pesos_alfa(alfas: np.ndarray = ALFAS) -> np.ndarray:
    """Pesos de la regla trapezoidal en alfa sobre [0, 1] con la masa de las colas asignada al cuantil extremo.

    E[f(Q)] ~ sum_j w_j f(q_j); los pesos suman 1 y, para una rejilla simetrica, sum_j w_j alfa_j = 1/2.
    """
    a = np.asarray(alfas, dtype=np.float64)
    w = np.empty_like(a)
    w[1:-1] = (a[2:] - a[:-2]) / 2.0
    w[0] = (a[1] - a[0]) / 2.0 + a[0]
    w[-1] = (a[-1] - a[-2]) / 2.0 + (1.0 - a[-1])
    return w


W_ALFA = pesos_alfa()


def _inv_softplus(x: np.ndarray) -> np.ndarray:
    return np.log(np.expm1(x))


class Bloque(nn.Module):
    def __init__(self, d: int, nh: int, ff: int) -> None:
        super().__init__()
        self.nh = nh
        self.ln1 = nn.LayerNorm(d)
        self.qkv = nn.Linear(d, 3 * d)
        self.out = nn.Linear(d, d)
        self.ln2 = nn.LayerNorm(d)
        self.fc1 = nn.Linear(d, ff)
        self.fc2 = nn.Linear(ff, d)


class Cono(nn.Module):
    def __init__(self, W: int, d: int, nh: int, ff: int, capas: int, H: int) -> None:
        super().__init__()
        self.W, self.d, self.nh, self.H = W, d, nh, H
        self.emb = nn.Linear(2, d)
        self.pos = nn.Parameter(torch.randn(W, d) * 0.02)
        self.bloques = nn.ModuleList([Bloque(d, nh, ff) for _ in range(capas)])
        self.ln_f = nn.LayerNorm(d)
        self.cabeza = nn.Linear(d, H * J)
        self._init_cabeza()

    def _init_cabeza(self) -> None:
        """Arranca con el cono gaussiano de sigma diaria 1 (1 unidad del modelo): huecos = dz*sqrt(h)."""
        hueco = np.diff(norm.ppf(ALFAS))[None, :] * np.sqrt(np.arange(1, self.H + 1))[:, None]  # (H, J-1)
        crudo = np.zeros((self.H, J))  # posiciones 0..J-2: huecos; posicion J-1: mediana (0); ver _montar
        crudo[:, : J - 1] = _inv_softplus(hueco)
        with torch.no_grad():
            self.cabeza.weight.mul_(0.1)
            self.cabeza.bias.copy_(torch.tensor(crudo.reshape(-1), dtype=self.cabeza.bias.dtype))

    def forward(self, x: torch.Tensor, hook=None) -> torch.Tensor:
        h = hook if hook is not None else (lambda nombre, t: t)
        B = x.shape[0]
        d, nh = self.d, self.nh
        dh = d // nh
        x = h("entrada", x / ESCALA_SALIDA)
        e = h("emb_lin", F.linear(torch.stack([x, x.abs()], dim=-1), self.emb.weight, self.emb.bias))
        z = h("emb", e + self.pos)
        for i, b in enumerate(self.bloques):
            p = f"b{i}."
            a = h(p + "ln1", F.layer_norm(z, (d,), b.ln1.weight, b.ln1.bias))
            qkv = F.linear(a, b.qkv.weight, b.qkv.bias)
            q, k, v = qkv.chunk(3, dim=-1)
            q = h(p + "q", q).reshape(B, self.W, nh, dh).transpose(1, 2)
            k = h(p + "k", k).reshape(B, self.W, nh, dh).transpose(1, 2)
            v = h(p + "v", v).reshape(B, self.W, nh, dh).transpose(1, 2)
            sc = h(p + "scores", (q @ k.transpose(-1, -2)) / math.sqrt(dh))
            pr = h(p + "probs", torch.softmax(sc, dim=-1))
            ctx = h(p + "ctx", (pr @ v).transpose(1, 2).reshape(B, self.W, d))
            at = h(p + "attn", F.linear(ctx, b.out.weight, b.out.bias))
            z = h(p + "res1", z + at)
            m = h(p + "ln2", F.layer_norm(z, (d,), b.ln2.weight, b.ln2.bias))
            m1 = h(p + "fc1", F.linear(m, b.fc1.weight, b.fc1.bias))
            ac = h(p + "act", F.gelu(m1))
            m2 = h(p + "mlp", F.linear(ac, b.fc2.weight, b.fc2.bias))
            z = h(p + "res2", z + m2)
        lect = h("lectura", z[:, -1] + z.mean(dim=1))
        u = h("ln_final", F.layer_norm(lect, (d,), self.ln_f.weight, self.ln_f.bias))
        crudo = h("cabeza", F.linear(u, self.cabeza.weight, self.cabeza.bias)).reshape(B, self.H, J)
        return self._montar(crudo, h)

    def _montar(self, crudo: torch.Tensor, h) -> torch.Tensor:
        """crudo[..., :J-1] -> huecos entre nodos contiguos; crudo[..., J-1] -> mediana. Cono monotono en alfa."""
        hueco = h("huecos", F.softplus(crudo[..., : J - 1]))
        med = crudo[..., J - 1 : J]
        arriba = torch.cumsum(hueco[..., J_MED:], dim=-1)  # nodos J_MED+1 .. J-1
        abajo = torch.flip(torch.cumsum(torch.flip(hueco[..., :J_MED], dims=[-1]), dim=-1), dims=[-1])  # nodos 0 .. J_MED-1
        q = torch.cat([med - abajo, med, med + arriba], dim=-1)
        return h("salida", q)


def crear_modelo(cfg: dict) -> Cono:
    return Cono(cfg["W"], cfg["d"], cfg["nh"], cfg["ff"], cfg["capas"], cfg["H"])


def n_parametros(m: nn.Module) -> int:
    return int(sum(p.numel() for p in m.parameters()))


def describir(cfg: dict) -> str:
    return (
        f"Transformer pre-LN solo codificador: ventana W={cfg['W']} log-rendimientos, d_model={cfg['d']}, "
        f"{cfg['nh']} cabezas, MLP {cfg['ff']} con GELU, {cfg['capas']} bloques, atencion completa y lectura = ultimo "
        f"token + media de tokens; entrada (x, |x|)/0.01; cabeza lineal a H x J = {cfg['H']} x {J} salidas (J cuantiles por horizonte h = 1..{cfg['H']}); "
        "mediana + huecos softplus acumulados en ambos sentidos (monotono en alfa por construccion)."
    )


def perdida_pinball(q: torch.Tensor, y: torch.Tensor, alfas: torch.Tensor) -> torch.Tensor:
    """Pinball medio. q (B, H, J) y y (B, H) en las mismas unidades."""
    u = y[..., None] - q
    return torch.maximum(alfas * u, (alfas - 1.0) * u).mean()


def entrenar(cfg: dict, semilla: int, R: np.ndarray, validos: np.ndarray, gen: np.random.Generator) -> tuple[Cono, dict]:
    """Entrena el modelo en f32 con pinball. Semilla de torch por semilla del banco."""
    torch.manual_seed(int(semilla))
    modelo = crear_modelo(cfg)
    W, H, B = cfg["W"], cfg["H"], cfg["lote"]
    pasos = cfg["pasos"]
    opt = torch.optim.AdamW(modelo.parameters(), lr=cfg["lr"], weight_decay=0.01)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: 0.05 + 0.95 * 0.5 * (1.0 + math.cos(math.pi * min(s, pasos) / pasos))
    )
    alfas = torch.tensor(ALFAS, dtype=torch.float32)
    off_x, off_y = np.arange(-W + 1, 1), np.arange(1, H + 1)
    historial = []
    modelo.train()
    for paso in range(pasos):
        t = validos[gen.integers(0, len(validos), size=B)]
        X = torch.tensor(R[t[:, None] + off_x[None, :]], dtype=torch.float32)
        Y = torch.tensor(np.cumsum(R[t[:, None] + off_y[None, :]], axis=1) / ESCALA_SALIDA, dtype=torch.float32)
        perdida = perdida_pinball(modelo(X), Y, alfas)
        opt.zero_grad(set_to_none=True)
        perdida.backward()
        nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
        opt.step()
        sched.step()
        historial.append(float(perdida.detach()))
    modelo.eval()
    k = max(1, min(50, pasos // 4))
    return modelo, {
        "pasos": pasos,
        "lote": B,
        "perdida_inicial": float(np.mean(historial[:k])),
        "perdida_final": float(np.mean(historial[-k:])),
    }


@torch.no_grad()
def cono(modelo: Cono, X: np.ndarray, hook=None, lote: int = 128) -> np.ndarray:
    """Cono en unidades del modelo (N, H, J) en el dtype del modelo, por lotes."""
    dt = next(modelo.parameters()).dtype
    out = []
    for i in range(0, len(X), lote):
        xb = torch.tensor(X[i : i + lote], dtype=dt)
        out.append(modelo(xb, hook).double().numpy())
    return np.concatenate(out, axis=0)


def a_f64(modelo: Cono) -> Cono:
    """Copia del modelo entrenado en f32 llevada a f64 (los pesos f32 son exactos en f64): la referencia."""
    return copy.deepcopy(modelo).double().eval()


def modelo_redondeado(ref64: Cono, tipo: str, escala: bool, contador: Contador | None) -> Cono:
    """Copia f64 con TODOS los parametros (pesos, sesgos, LN, posicion) redondeados al tipo, por tensor."""
    m = copy.deepcopy(ref64)
    with torch.no_grad():
        for p in m.parameters():
            r = redondear(p.detach().numpy(), tipo, escala=escala, por_muestra=False, contador=contador)
            p.copy_(torch.from_numpy(r))
    return m.eval()


def crps_cuantiles(q: np.ndarray, y: np.ndarray, alfas: np.ndarray = ALFAS) -> float:
    """CRPS aproximado por cuantiles: 2 * sum_j w_j pinball_alfa_j(y - q_j), media sobre todo salvo alfa.

    q (..., J), y (...). Con una prediccion degenerada (todos los cuantiles iguales) da exactamente |y - q|
    cuando la rejilla es simetrica (sum_j w_j alfa_j = 1/2).
    """
    w = pesos_alfa(alfas)
    u = y[..., None] - q
    pin = np.maximum(alfas * u, (alfas - 1.0) * u)
    return float(np.mean(2.0 * (pin * w).sum(axis=-1)))
