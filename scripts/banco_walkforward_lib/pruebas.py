"""Selftest de banco_walkforward.py: sin red, sin datos reales y sin pesos (Chronos-2 -> modelo trivial)."""
from __future__ import annotations

import math
import socket

import numpy as np

from . import banco, datos, metricas, modelos

DIA = datos.DIA_MS
T0 = 1_700_000_000_000 - (1_700_000_000_000 % DIA)


def _sin_red():
    def _bloqueado(*a, **k):
        raise OSError("selftest sin red: conexion bloqueada")

    socket.socket.connect = _bloqueado
    socket.socket.connect_ex = _bloqueado
    socket.create_connection = _bloqueado


def _cerca(a, b, tol, que):
    if not abs(a - b) <= tol:
        raise AssertionError(f"{que}: {a!r} != {b!r} (tol {tol})")


def simular_garch(n, omega=0.05, alpha=0.08, beta=0.90, nu=6.0, mu=0.02, semilla=7):
    """Rendimientos en % de un GARCH(1,1)-t estandarizada con parametros conocidos."""
    rs = np.random.RandomState(semilla)
    z = rs.standard_t(nu, n) / math.sqrt(nu / (nu - 2))
    r = np.empty(n)
    s2 = omega / (1 - alpha - beta)
    for t in range(n):
        r[t] = mu + math.sqrt(s2) * z[t]
        s2 = omega + alpha * (r[t] - mu) ** 2 + beta * s2
    return r


def prueba_metricas():
    from scipy.stats import norm

    # pinball a mano
    _cerca(float(metricas.pinball(1.0, 0.0, 0.1)), 0.1, 1e-15, "pinball(y=1,q=0,a=0.1)")
    _cerca(float(metricas.pinball(-1.0, 0.0, 0.1)), 0.9, 1e-15, "pinball(y=-1,q=0,a=0.1)")
    _cerca(float(metricas.pinball(0.5, 1.0, 0.99)), 0.005, 1e-15, "pinball(y=.5,q=1,a=.99)")
    # CRPS por cuantiles a mano: niveles .25/.5/.75, cuantiles -1/0/1, y = .5 -> 2/3 * (.375 + .25 + .125) = .5
    _cerca(float(metricas.crps_cuantiles([0.5], [[-1.0, 0.0, 1.0]], (0.25, 0.5, 0.75))[0]), 0.5, 1e-15, "CRPS_q")
    # con una rejilla densa y uniforme de cuantiles normales, CRPS_q tiende a la formula cerrada de la normal
    lv = tuple((np.arange(1, 2000) / 2000).tolist())
    for y in (0.0, 0.7, -2.1):
        cerrada = y * (2 * norm.cdf(y) - 1) + 2 * norm.pdf(y) - 1 / math.sqrt(math.pi)
        aprox = float(metricas.crps_cuantiles([y], [norm.ppf(lv)], lv)[0])
        _cerca(aprox, cerrada, 2e-3 * max(1.0, cerrada), f"CRPS normal y={y}")
    # Kupiec a mano: n = 100, x = 3, p = 0,01
    lr, p = metricas.kupiec([1, 1, 1] + [0] * 97, 0.01)
    l0 = 97 * math.log(0.99) + 3 * math.log(0.01)
    l1 = 97 * math.log(0.97) + 3 * math.log(0.03)
    _cerca(lr, 2 * (l1 - l0), 1e-12, "Kupiec LR formula")
    _cerca(lr, 2.6323526355544757, 1e-12, "Kupiec LR literal")
    _cerca(p, 0.10470646146666306, 1e-12, "Kupiec p literal")
    _cerca(metricas.kupiec([0] * 50 + [1], 1 / 51)[0], 0.0, 1e-12, "Kupiec x/n = p")
    # Christoffersen a mano: [0,0,0,0,1,1,1,0,0,0] -> n00=5 n01=1 n10=1 n11=2
    lr, p = metricas.christoffersen([0, 0, 0, 0, 1, 1, 1, 0, 0, 0])
    l0 = 6 * math.log(2 / 3) + 3 * math.log(1 / 3)
    l1 = 5 * math.log(5 / 6) + math.log(1 / 6) + math.log(1 / 3) + 2 * math.log(2 / 3)
    _cerca(lr, 2 * (l1 - l0), 1e-12, "Christoffersen LR formula")
    _cerca(lr, 2.231435513142097, 1e-12, "Christoffersen LR literal")
    _cerca(p, 0.13522815768706561, 1e-12, "Christoffersen p literal")
    # sin dependencia: [0,0,1,1,0,0,0,1,0,0] -> pi0 = pi1 = pi -> LR = 0
    _cerca(metricas.christoffersen([0, 0, 1, 1, 0, 0, 0, 1, 0, 0])[0], 0.0, 1e-12, "Christoffersen LR=0")
    assert math.isnan(metricas.christoffersen([0] * 20)[1]), "sin excedencias el p-valor debe ser NaN"
    # vol y QLIKE
    Q = norm.ppf(metricas.NIVELES)[None, :] * 0.02
    _cerca(float(metricas.var_desde_cuantiles(Q)[0]), 0.0004, 1e-15, "varianza desde q10/q90 de N(0, 0.02)")
    _cerca(float(metricas.qlike(0.01, 0.04)), math.log(0.04) + 0.25, 1e-15, "QLIKE")
    assert metricas.submuestra_sin_solape([0, 1, 2, 5, 6, 10], 5).tolist() == [0, 3, 5], "submuestra sin solape"
    assert metricas.submuestra_sin_solape([3, 4, 5], 1).tolist() == [0, 1, 2], "submuestra h=1"
    print("metricas: pinball, CRPS_q, Kupiec, Christoffersen, varianza y QLIKE contra valores a mano: ok")


def _tabla(n, close, disp=None, inst="SINT", ts0=T0, dias=None):
    import pandas as pd

    ts = ts0 + np.arange(n, dtype=np.int64) * DIA if dias is None else ts0 + np.asarray(dias, np.int64) * DIA
    av = (ts + DIA).astype(float) if disp is None else np.asarray(disp, float)
    return pd.DataFrame({"instrument": inst, "ts_ms": ts, "interval_ms": DIA, "close": close, "available_at_ms": av})


def prueba_look_ahead():
    n, W = 400, 200
    close = 100 * np.exp(np.cumsum(simular_garch(n, semilla=3)) / 100)
    tarde = 350  # barra con ts anterior al origen pero publicada mucho despues
    origen = T0 + 361 * DIA  # cierre de la barra 360
    disp = T0 + np.arange(n) * DIA + DIA
    disp = disp.astype(float)
    disp[tarde] = T0 + 1000 * DIA
    a = datos.series_desde_tabla(_tabla(n, close, disp), None)["SINT"]
    close_b = close.copy()
    close_b[tarde] *= 1000.0  # dato del futuro extremo
    b = datos.series_desde_tabla(_tabla(n, close_b, disp), None)["SINT"]
    ca, cb = datos.cortar(a, origen, W, banco.HMAX), datos.cortar(b, origen, W, banco.HMAX)
    assert ca.k == 360 and cb.k == 360, f"ultima barra visible {ca.k}"
    assert np.array_equal(ca.precios, cb.precios), "el dato tardio entro en el contexto"
    assert close_b[tarde] not in cb.precios and close[360] == cb.precios[-1], "contexto mal cortado"
    esperado = np.delete(close[:361], tarde)[-W:]
    assert np.array_equal(cb.precios, esperado), "contexto distinto de las W barras visibles"
    # el objetivo empieza en la barra 361 (no visible en el origen)
    _cerca(float(ca.y[0]), math.log(close[361] / close[360]), 1e-15, "objetivo h=1")
    assert a.disp_ms[361] > origen, "la barra 361 no debe ser visible"
    ms = [modelos.Hmm(s_caminos=200), modelos.Garch(s_caminos=200), modelos.Trivial()]
    for m in ms:
        qa, _ = m.predecir(ca.precios, 11, banco.HMAX)
        qb, _ = m.predecir(cb.precios, 11, banco.HMAX)
        assert np.array_equal(qa, qb), f"{m.nombre}: la prediccion cambia con un dato del futuro"
    # disponibilidad por default_lag_ms (proxy): available_at nulo
    nulo = np.full(n, np.nan)
    s0 = datos.series_desde_tabla(_tabla(n, close, nulo), 0)["SINT"]
    assert datos.cortar(s0, origen, W, banco.HMAX).k == 360, "lag 0: la barra 360 cierra en el origen"
    s1 = datos.series_desde_tabla(_tabla(n, close, nulo), 1)["SINT"]
    assert datos.cortar(s1, origen, W, banco.HMAX).k == 359, "lag 1 ms: la barra 360 aun no es visible"
    try:
        datos.series_desde_tabla(_tabla(n, close, nulo), None)
        raise AssertionError("sin available_at ni default_lag_ms la carga debe fallar")
    except ValueError:
        pass
    # rejilla diaria con fines de semana: sin barra nueva -> se omite
    dias = [d for d in range(420) if d % 7 not in (5, 6)]
    sw = datos.series_desde_tabla(_tabla(len(dias), 100 * np.exp(np.arange(len(dias)) * 1e-3), dias=dias), 0)["SINT"]
    rej = list(range(T0 + 300 * DIA, T0 + 330 * DIA, DIA))
    cs, om = datos.cortes_de_serie(sw, rej, 100, 5)
    assert om["sin_barra_nueva"] > 0 and len({c.k for c in cs}) == len(cs), "deduplicacion de origenes"
    print(f"look-ahead: dato tardio x1000 fuera del contexto y sin efecto en hmm/garch/trivial; default_lag_ms 0/1 ms; "
          f"{om['sin_barra_nueva']} origenes sin barra nueva omitidos: ok")


def prueba_garch_conocido():
    r = simular_garch(4000, semilla=21)
    precios = 100 * np.exp(np.cumsum(r) / 100)
    Q, info = modelos.Garch(s_caminos=400).predecir(precios, 5, 5)
    from arch import arch_model

    fr = arch_model(r, mean="Constant", vol="GARCH", p=1, q=1, dist="t").fit(disp="off")
    p = fr.params
    _cerca(float(p["alpha[1]"]), 0.08, 0.03, "alpha estimado")
    _cerca(float(p["beta[1]"]), 0.90, 0.04, "beta estimado")
    _cerca(info["persistencia"], 0.98, 0.015, "persistencia estimada")
    _cerca(info["nu"], 6.0, 2.0, "nu estimado")
    assert np.all(np.diff(Q, axis=1) >= 0), "cuantiles no monotonos"
    print(f"GARCH(1,1)-t simulado (alpha .08, beta .90, nu 6): estimado alpha {float(p['alpha[1]']):.3f}, "
          f"beta {float(p['beta[1]']):.3f}, nu {info['nu']:.2f}: ok")


def prueba_reproducible():
    import pandas as pd

    n = 700
    close = 100 * np.exp(np.cumsum(simular_garch(n, semilla=9)) / 100)
    s = datos.series_desde_tabla(_tabla(n, close), None)["SINT"]
    rej = datos.rejilla_origenes(datos.fecha(T0 + 400 * DIA), datos.fecha(T0 + 640 * DIA), 40)
    cortes, _ = datos.cortes_de_serie(s, rej, 300, banco.HMAX)
    assert len(cortes) >= 5, f"pocos cortes {len(cortes)}"

    def una():
        ms = [modelos.Hmm(s_caminos=200), modelos.Garch(s_caminos=200), modelos.Trivial()]
        return pd.DataFrame(banco.correr_serie(s, cortes, ms, banco.SEMILLA)), ms

    p1, ms = una()
    p2, _ = una()
    assert p1["ok"].all(), p1.loc[~p1["ok"], "error"].tolist()
    assert banco.hash_predicciones(p1) == banco.hash_predicciones(p2), "dos corridas con la misma semilla difieren"
    m1 = banco.metricas_tabla(p1, [m.nombre for m in ms])
    m2 = banco.metricas_tabla(p2, [m.nombre for m in ms])
    assert m1.equals(m2), "metricas distintas entre corridas"
    assert len(m1) == len(banco.HORIZONTES) * 3 and np.all(np.isfinite(m1[["crps", "qlike"]].to_numpy()))
    # otra semilla cambia las muestras de los modelos estocasticos
    p3 = pd.DataFrame(banco.correr_serie(s, cortes[:1], [modelos.Garch(s_caminos=200)], banco.SEMILLA + 1))
    assert not np.array_equal(p3[banco.QCOLS].to_numpy(), p1[p1["modelo"] == "garch"].iloc[:3][banco.QCOLS].to_numpy())
    print(f"reproducibilidad: dos corridas de {len(cortes)} origenes x 3 modelos con semilla {banco.SEMILLA}: "
          f"predicciones y metricas identicas ({banco.hash_predicciones(p1)[:16]}): ok")


def selftest() -> int:
    _sin_red()
    prueba_metricas()
    prueba_look_ahead()
    prueba_garch_conocido()
    prueba_reproducible()
    print("selftest ok")
    return 0
