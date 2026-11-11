"""Selftest de banco_walkforward.py: sin red, sin datos reales y sin pesos (Chronos-2 -> modelo trivial)."""
from __future__ import annotations

import math
import os
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


def prueba_toto():
    """Toto por subproceso: ausencia del venv -> SALTADO sin romper nada; protocolo y contrato con un Toto falso
    (el trabajador real en modo --falso, con el Python de este venv: sin torch, sin pesos, sin red)."""
    import sys

    import pandas as pd

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import banco_walkforward as bw

    falta = "E:/quantdesk-lab/venvs/no-existe/Scripts/python.exe"
    try:
        modelos.Toto(python=falta)
        raise AssertionError("Toto sin venv deberia quedar SALTADO")
    except modelos.ModeloSaltado as exc:
        assert "SALTADO" in str(exc)
    ms, salt = bw.fabrica_modelos(["garch", "toto"], 1, toto_python=falta)
    assert [m.nombre for m in ms] == ["garch"] and "toto" in salt and "SALTADO" in salt["toto"], salt
    n = 500
    close = 100 * np.exp(np.cumsum(simular_garch(n, semilla=13)) / 100)
    s = datos.series_desde_tabla(_tabla(n, close), None)["SINT"]
    cortes, _ = datos.cortes_de_serie(s, datos.rejilla_origenes(datos.fecha(T0 + 400 * DIA),
                                                                 datos.fecha(T0 + 470 * DIA), 20), 300, banco.HMAX)
    t = modelos.Toto(hilos=1, python=sys.executable, falso=True, muestras=500)
    try:
        assert t.versiones and t.pesos is None
        q1, i1 = t.predecir(cortes[0].precios, 7, banco.HMAX)
        q2, _ = t.predecir(cortes[0].precios, 7, banco.HMAX)
        q3, _ = t.predecir(cortes[0].precios, 8, banco.HMAX)
        assert q1.shape == (banco.HMAX, len(metricas.NIVELES)) and np.all(np.diff(q1, axis=1) >= 0)
        assert np.array_equal(q1, q2) and not np.array_equal(q1, q3), "semilla del trabajador"
        assert "cpu_s_externo" in i1, "el CPU del subproceso debe volver al banco"
        # los precios viajan en JSON sin perder bits: el contexto del trabajador es el del banco
        sd = float(np.std(np.diff(np.log(cortes[0].precios))))
        _cerca(float(q1[0, metricas.I90] - q1[0, metricas.I10]), 2 * metricas.Z90 * sd, 0.25 * sd, "escala falsa")
        try:
            t.predecir(np.array([1.0, -1.0, 2.0]), 1, banco.HMAX)
            raise AssertionError("un error del trabajador debe propagarse")
        except RuntimeError:
            pass
        filas = pd.DataFrame(banco.correr_serie(s, cortes, [modelos.Garch(s_caminos=200), t], banco.SEMILLA))
        assert filas["ok"].all() and set(filas["modelo"]) == {"garch", "toto"}, filas["error"].unique()
        met = banco.metricas_tabla(filas, ["garch", "toto"])
        assert set(met["modelo"]) == {"garch", "toto"} and np.all(np.isfinite(met["crps"]))
    finally:
        t.cerrar()
    print(f"toto: venv ausente -> SALTADO sin romper la corrida; trabajador falso por subproceso con el mismo "
          f"contrato de cuantiles, semilla y errores ({len(cortes)} origenes): ok")


def selftest() -> int:
    _sin_red()
    prueba_metricas()
    prueba_look_ahead()
    prueba_garch_conocido()
    prueba_reproducible()
    prueba_toto()
    prueba_deciles_independientes()
    prueba_ventana_limpia()
    prueba_fincast()
    prueba_monotonia_banco()
    prueba_informe_limpia()
    prueba_timeout_persistido()
    prueba_ventana_vacia_persistida()
    print("selftest ok")
    return 0


def prueba_deciles_independientes():
    """Oraculo escalar: NormalDist (stdlib), formula de pinball de scikit-learn,
    https://scikit-learn.org/stable/modules/model_evaluation.html#pinball-loss.
    No usa pinball/crps del banco para calcular el esperado; no es la integral continua del CRPS normal.
    """
    from statistics import NormalDist

    niveles = tuple(i / 10 for i in range(1, 10))
    normales = [NormalDist().inv_cdf(p) for p in niveles]
    ys = [-2.1, 0.0, 0.7]
    esperado = [2 * sum(max(p * (y - q), (p - 1) * (y - q))
                        for p, q in zip(niveles, normales)) / 9 for y in ys]
    Q = np.tile([NormalDist().inv_cdf(p) for p in metricas.NIVELES], (len(ys), 1))
    obtenido = metricas.crps_deciles(ys, Q)
    assert np.allclose(obtenido, esperado, rtol=0, atol=1e-15), (obtenido, esperado)
    # Todos los cuantiles no decilicos se pueden alterar sin cambiar la metrica.
    Q[:, [i for i, p in enumerate(metricas.NIVELES) if p not in niveles]] += 100
    assert np.array_equal(metricas.crps_deciles(ys, Q), obtenido)
    print("crps_deciles: normal exacta contra 9 pinball escalares independientes: ok")


def prueba_ventana_limpia():
    import pandas as pd
    from scipy.stats import norm

    corte = datos.rejilla_origenes("2025-08-27", "2025-08-27", 1)[0]
    filas = []
    for j, t in enumerate((corte - DIA, corte, corte + DIA, corte + 2 * DIA)):
        for m in ("hmm", "garch", "chronos2", "toto", "fincast"):
            for h in banco.HORIZONTES:
                f = {"instrument": "SINT", "origen_ms": t, "k": j, "modelo": m, "h": h,
                     "y": 0.01, "rv": 0.001, "ok": m != "fincast" or j == 2}
                f.update(dict(zip(banco.QCOLS, norm.ppf(metricas.NIVELES) * 0.02)))
                filas.append(f)
    p = pd.DataFrame(filas)
    ms = ["hmm", "garch", "chronos2", "toto"]
    base = banco.metricas_tabla(p[p.modelo != "fincast"], ms)
    principal = banco.metricas_tabla(p, ms + ["fincast"])
    assert base.equals(principal) and set(principal.modelo) == set(ms)
    assert (principal.n == 4).all(), "FinCast reduce los origenes principales"
    limpia = banco.metricas_tabla(p, ms + ["fincast"], limpia=True)
    assert (limpia.n == 1).all() and set(limpia.modelo) == set(ms + ["fincast"])
    fc = limpia[limpia.modelo == "fincast"]
    prohibidos = ["crps", "pinball_01", "pinball_99", "exc_01", "exc_99", "n_test", "x_01", "x_99",
                  "kupiec_01_p", "kupiec_99_p", "christ_01_p", "christ_99_p"]
    assert fc[prohibidos].isna().all().all() and fc.criterios_no_aplicables.str.len().gt(0).all()
    assert np.isfinite(fc[["crps_deciles", "qlike"]]).all().all()
    # La frontera exacta se excluye; +1 ms tambien debe entrar, no solo +1 dia.
    assert not banco.es_origen_limpio(corte) and banco.es_origen_limpio(corte + 1)
    assert banco.es_origen_limpio(corte + DIA)
    antiguo = p[p.origen_ms <= corte]
    vacia = banco.metricas_tabla(antiguo, ms, limpia=True)
    assert vacia.empty and "crps_deciles" in vacia.columns
    estado = banco.estado_limpia(antiguo, vacia, ms)
    assert estado["estado"] == "vacia" and "posteriores" in estado["motivo"]
    # Con origenes posteriores pero sin interseccion tambien hay motivo explicito.
    sin_comunes = p[p.origen_ms == corte + 2 * DIA]
    vacia = banco.metricas_tabla(sin_comunes, ms + ["fincast"], limpia=True)
    assert banco.estado_limpia(sin_comunes, vacia, ms + ["fincast"])["estado"] == "vacia"
    assert "comunes" in banco.estado_limpia(sin_comunes, vacia, ms + ["fincast"])["motivo"]
    print("ventana limpia: corte UTC estricto, vacia declarada, origenes comunes y mascara FinCast: ok")


def prueba_fincast():
    import sys
    import pandas as pd
    from statistics import NormalDist
    from . import fincast_trabajador as ft, toto_trabajador as tt

    assert ft.NIVELES == tt.NIVELES == metricas.NIVELES, "copias del contrato de niveles distintas"
    nativos = np.array([[0.3 + 0.02 * NormalDist().inv_cdf(p) for p in ft.DECILES]])
    Q, info = ft.expandir_deciles(nativos)
    esperado = np.array([[0.3 + 0.02 * NormalDist().inv_cdf(p) for p in metricas.NIVELES]])
    assert np.allclose(Q, esperado, rtol=0, atol=1e-15)
    assert np.array_equal(Q[:, metricas.IDECILES], nativos)
    assert len(info["niveles_nativos"]) == 9 and len(info["niveles_interpolados"]) == 8
    assert info["niveles_extrapolados"] == [0.01, 0.05, 0.95, 0.99]
    falta = "E:/quantdesk-lab/venvs/no-existe/Scripts/python.exe"
    for opciones in ({"python": falta}, {"python": sys.executable, "pesos": falta}):
        try:
            modelos.FinCast(**opciones)
            raise AssertionError("FinCast sin venv/pesos debe quedar SALTADO")
        except modelos.ModeloSaltado as exc:
            assert "SALTADO" in str(exc)
    close = 100 * np.exp(np.cumsum(simular_garch(500, semilla=13)) / 100)
    ts0 = datos.rejilla_origenes("2025-01-01", "2025-01-01", 1)[0]
    s = datos.series_desde_tabla(_tabla(500, close, ts0=ts0), None)["SINT"]
    cortes, _ = datos.cortes_de_serie(s, [ts0 + j * DIA for j in (400, 420)], 250, banco.HMAX)
    t = modelos.FinCast(python=sys.executable, falso=True, timeout_s=5)
    try:
        q1, i1 = t.predecir(cortes[0].precios, 7, banco.HMAX)
        q2, _ = t.predecir(cortes[0].precios, 7, banco.HMAX)
        assert np.array_equal(q1, q2) and q1.shape == (banco.HMAX, 21)
        assert np.all(np.diff(q1, axis=1) >= 0) and "cpu_s_externo" in i1
        assert i1["niveles_nativos"] == list(ft.DECILES)
        try:
            t.predecir([1, -1, 2], 7, banco.HMAX)
            raise AssertionError("error JSON del trabajador no propagado")
        except RuntimeError as exc:
            assert "precios" in str(exc)
        filas = pd.DataFrame(banco.correr_serie(s, cortes, [t], banco.SEMILLA))
        assert filas.ok.all() and banco.metricas_tabla(filas, ["fincast"]).empty
        assert len(banco.metricas_tabla(filas, ["fincast"], limpia=True)) == 3
    finally:
        t.cerrar()
    # El trabajador real falso puede simular un cuelgue o una salida corrupta. Tras el timeout se reinicia
    # para el siguiente origen; el primero queda fallido y el banco no se bloquea.
    for fallo, mensaje in (("silencio", "timeout"), ("error", "error falso"), ("no_monotono", "monoton")):
        t = modelos.FinCast(python=sys.executable, falso=True, timeout_s=0.25, fallo_falso=fallo)
        try:
            pid_antes = t.p.pid
            t.timeout_arranque_s = 10
            filas = pd.DataFrame(banco.correr_serie(s, cortes, [t], banco.SEMILLA))
            assert not filas.iloc[:3].ok.any() and filas.iloc[:3].error.str.contains(mensaje).all(), filas.error
            assert filas.iloc[3:].ok.all(), "la corrida no sigue tras un origen fallido"
            assert filas.loc[~filas.ok, "origen_ms"].nunique() == 1
            assert (t.p.pid != pid_antes) == (fallo == "silencio"), "solo el fallo de transporte exige reinicio"
        finally:
            t.cerrar()
    print("fincast: trabajador aislado falso, deciles/z, venv/pesos ausentes, timeout y errores por origen: ok")


def prueba_monotonia_banco():
    import pandas as pd

    class Roto:
        nombre = "hmm"

        def predecir(self, precios, semilla, hmax):
            Q = np.tile(np.arange(21, dtype=float), (hmax, 1))
            Q[0, 1] = -1
            return Q, {}

    close = np.exp(np.arange(80) * 0.001)
    s = datos.series_desde_tabla(_tabla(80, close), None)["SINT"]
    cortes, _ = datos.cortes_de_serie(s, [T0 + 40 * DIA], 30, banco.HMAX)
    p = pd.DataFrame(banco.correr_serie(s, cortes, [Roto()], banco.SEMILLA))
    assert not p.ok.any() and p.error.str.contains("monoton").all()

    class ErrorCPU(Roto):
        def predecir(self, precios, semilla, hmax):
            exc = RuntimeError("fallo externo con CPU conocida")
            exc.cpu_s_externo = 7.25
            raise exc

    p = pd.DataFrame(banco.correr_serie(s, cortes, [ErrorCPU()], banco.SEMILLA))
    assert not p.ok.any() and (p.cpu_s >= 7.25).all(), "CPU externa de una respuesta fallida perdida"
    print("banco: cuantiles no monotonos fallan explicitamente para cualquier modelo: ok")


def prueba_informe_limpia():
    import json
    import tempfile
    from pathlib import Path
    import pandas as pd
    from scipy.stats import norm
    from . import informe, rutas

    os.makedirs(rutas.TMP_FINCAST, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="selftest-", dir=rutas.TMP_FINCAST) as tmp:
        origen = banco.CORTE_LIMPIO_MS + DIA
        archivos = []
        for m in ("hmm", "toto", "fincast"):
            run = Path(tmp, m)
            run.mkdir()
            c = datos.Corte(origen, 30, origen - DIA, np.ones(30), np.full(20, 0.01), np.full(20, 0.001))
            q = np.tile(norm.ppf(metricas.NIVELES) * 0.02, (banco.HMAX, 1))
            pred = pd.DataFrame(banco._filas_corte("SINT", c, m, q, {}, 0.1, None))
            pred.to_parquet(run / "predicciones.parquet", index=False)
            meta = {"dataset": {"dataset_id": "sintetico", "dataset_hash": "sha256:prueba", "proxy": False},
                    "config": {"modelos": [m], "ventana": 30, "horizontes": [1, 5, 20], "semilla": banco.SEMILLA},
                    "cpu": {m: {"por_origen_s": 0.1}}, "pared_s": 0.1, "fallos": {m: 0},
                    "predicciones_sha256": banco.hash_predicciones(pred)}
            (run / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
            archivos.append(str(run))
        met, estado, _ = informe.cargar_limpia(archivos)
        assert len(met) == 9 and (met.n == 1).all() and estado["estado"] == "calculada"
        texto, tabla, _ = informe.seccion_limpia(archivos)
        assert "no aplicables" in "\n".join(texto) and "extrapolacion" in "\n".join(texto)
        assert tabla[tabla.modelo == "fincast"].pinball_01.isna().all()
        # Los archivos SPRINT-01 pueden contener cruces antes aceptados. La nueva tabla limpia los
        # excluye por origen-modelo entero, los declara y conserva intactos los criterios principales.
        p = Path(archivos[0], "predicciones.parquet")
        original = pd.read_parquet(p)
        roto = original.copy()
        roto.loc[0, "q01"] = roto.loc[0, "q00"] - 1
        roto.to_parquet(p, index=False)
        tabla_rota, estado_roto, _ = informe.cargar_limpia(archivos)
        assert tabla_rota.empty and estado_roto["validacion_predicciones"]["por_modelo"] == {"hmm": 1}
        assert len(banco.metricas_tabla(roto, ["hmm"])) == 3
        original.to_parquet(p, index=False)
        # La comparacion FinCast comprueba tambien la tabla limpia (la principal esta vacia).
        comp = banco.comparar(archivos[-1], archivos[-1])
        assert comp["predicciones_identicas"] and comp["metricas_limpias_identicas"]
        # CSV vacio con cabecera, estado explicito y render sin NaN mudo si no hay origen limpio.
        for run in archivos:
            p = Path(run, "predicciones.parquet")
            antiguo = pd.read_parquet(p).assign(origen_ms=banco.CORTE_LIMPIO_MS)
            antiguo.to_parquet(p, index=False)
        texto, tabla, estados = informe.seccion_limpia(archivos)
        assert tabla.empty and estados["sintetico"]["estado"] == "vacia"
        assert "sin origenes posteriores" in "\n".join(texto)
        # Un dataset distinto o un objetivo distinto se rechazan antes de comparar criterios.
        path = Path(archivos[-1], "meta.json")
        meta = json.loads(path.read_text(encoding="utf-8"))
        meta["dataset"]["dataset_hash"] = "sha256:otro"
        path.write_text(json.dumps(meta), encoding="utf-8")
        try:
            informe.cargar_limpia(archivos)
            raise AssertionError("mezcla de datasets aceptada")
        except ValueError as exc:
            assert "dataset_hash" in str(exc)
    print("informe limpio: union de corridas, mascara, determinismo y vacio explicito, sin mezclar datasets: ok")


def prueba_timeout_persistido():
    """Cruza trabajador -> banco -> parquet/meta -> informe; el fallo no desaparece al persistir."""
    import json
    import sys
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    import pandas as pd
    from . import informe, rutas

    ts0 = datos.rejilla_origenes("2025-01-01", "2025-01-01", 1)[0]
    close = 100 * np.exp(np.cumsum(simular_garch(500, semilla=17)) / 100)
    s = datos.series_desde_tabla(_tabla(500, close, ts0=ts0), None)
    meta_ds = {"dataset_id": "sintetico_timeout", "dataset_hash": "sha256:sintetico_timeout",
               "intervalos_ms": [DIA], "proxy": False}
    t = modelos.FinCast(python=sys.executable, falso=True, timeout_s=0.25, fallo_falso="silencio")
    with tempfile.TemporaryDirectory(prefix="timeout-", dir=rutas.TMP_FINCAST) as tmp:
        try:
            with patch.object(datos, "cargar_dataset", return_value=(s, meta_ds)):
                pred, principal, meta = banco.ejecutar("lago_cierre_c20261101", tmp, ["fincast"], None, 2,
                                                     banco.SEMILLA, 1, "selftest sintetico sin red", False,
                                                     lambda nombres, hilos: ([t], {}))
            assert meta["fallos"] == {"fincast": 1} and principal.empty
            assert pred.loc[~pred.ok, "origen_ms"].nunique() == 1 and pred.loc[pred.ok, "origen_ms"].nunique() == 1
            persistido = json.loads(Path(tmp, "meta.json").read_text(encoding="utf-8"))
            assert persistido["fallos"]["fincast"] == 1 and "timeout" in persistido["errores_ejemplo"][0]["error"]
            assert pd.read_csv(Path(tmp, "metricas.csv")).empty
            limpia = pd.read_csv(Path(tmp, "metricas_limpia.csv"))
            assert (limpia.n == 1).all() and limpia.pinball_01.isna().all()
            texto, _, _ = informe.seccion_limpia([tmp])
            assert "timeout" in "\n".join(texto) and "'fincast': 1" in "\n".join(texto)
        finally:
            t.cerrar()
    print("timeout persistido: un origen fallido, siguiente valido, recuento en meta y en informe: ok")


def prueba_ventana_vacia_persistida():
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    import pandas as pd
    from . import rutas

    ts0 = datos.rejilla_origenes("2020-01-01", "2020-01-01", 1)[0]
    close = 100 * np.exp(np.cumsum(simular_garch(1600, semilla=18)) / 100)
    s = datos.series_desde_tabla(_tabla(1600, close, ts0=ts0), None)
    meta_ds = {"dataset_id": "sintetico_antiguo", "dataset_hash": "sha256:sintetico_antiguo",
               "intervalos_ms": [DIA], "proxy": False}
    os.makedirs(rutas.TMP_FINCAST, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vacia-", dir=rutas.TMP_FINCAST) as tmp:
        with patch.object(datos, "cargar_dataset", return_value=(s, meta_ds)):
            pred, principal, meta = banco.ejecutar("binance_c20261101", tmp, ["chronos2"], None, 0,
                                                 banco.SEMILLA, 1, "selftest sintetico antiguo", False,
                                                 lambda nombres, hilos: ([modelos.Trivial()], {}), solo_limpia=True)
        assert pred.empty and principal.empty and meta["ventana_limpia"]["estado"] == "vacia"
        assert meta["omitidos"]["SINT"]["fuera_ventana_limpia"] > 0
        assert "posteriores" in meta["ventana_limpia"]["motivo"]
        assert pd.read_csv(Path(tmp, "metricas_limpia.csv")).empty
    print("ventana limpia vacia persistida: dataset antiguo, CSV con cabecera y motivo en meta: ok")
