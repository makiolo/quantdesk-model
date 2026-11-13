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
    prueba_interpolacion_asimetrica()
    prueba_puertas_fincast()
    prueba_cruces_sprint01()
    prueba_seleccion_fincast()
    prueba_mt5_presets_rutas_hash()
    prueba_mt5_umbrales()
    prueba_mt5_diferencial_bordes()
    prueba_mt5_ausentes_y_comunes()
    prueba_mt5_situacion_y_coste()
    prueba_mt5_oraculo_parquet()
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
        nombre = "fincast"

        def predecir(self, precios, semilla, hmax):
            Q = np.tile(np.arange(21, dtype=float), (hmax, 1))
            Q[1, 1] = -1  # h=2 no se almacena: FinCast debe validar los 20 al inferir
            return Q, {}

    close = np.exp(np.arange(80) * 0.001)
    ts0 = banco.CORTE_LIMPIO_MS + DIA
    s = datos.series_desde_tabla(_tabla(80, close, ts0=ts0), None)["SINT"]
    cortes, _ = datos.cortes_de_serie(s, [ts0 + 40 * DIA], 30, banco.HMAX)
    p = pd.DataFrame(banco.correr_serie(s, cortes, [Roto()], banco.SEMILLA))
    assert not p.ok.any() and p.error.str.contains("monoton").all()

    class ErrorCPU(Roto):
        def predecir(self, precios, semilla, hmax):
            exc = RuntimeError("fallo externo con CPU conocida")
            exc.cpu_s_externo = 7.25
            raise exc

    p = pd.DataFrame(banco.correr_serie(s, cortes, [ErrorCPU()], banco.SEMILLA))
    assert not p.ok.any() and (p.cpu_s >= 7.25).all(), "CPU externa de una respuesta fallida perdida"
    print("banco: cuantiles FinCast no monotonos fallan explicitamente; CPU externa fallida conservada: ok")


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
        # A12: los cruces de SPRINT-01 se puntuan intactos y se cuentan; solo FinCast los rechaza.
        p = Path(archivos[0], "predicciones.parquet")
        original = pd.read_parquet(p)
        roto = original.copy()
        roto.loc[0, "q01"] = roto.loc[0, "q00"] - 1
        roto.to_parquet(p, index=False)
        tabla_rota, estado_roto, _ = informe.cargar_limpia(archivos)
        assert len(tabla_rota) == 9 and not estado_roto["validacion_predicciones"]["por_modelo"]
        assert tabla_rota.loc[(tabla_rota.modelo == "hmm") & (tabla_rota.h == 1), "cruces_cuantiles"].item() == 1
        assert len(banco.metricas_tabla(roto, ["hmm"])) == 3
        original.to_parquet(p, index=False)
        pfc = Path(archivos[-1], "predicciones.parquet")
        fc_original = pd.read_parquet(pfc)
        fc_roto = fc_original.copy()
        fc_roto.loc[0, "q04"] = fc_roto.loc[0, "q02"] - 1
        fc_roto.to_parquet(pfc, index=False)
        tabla_rota, estado_roto, _ = informe.cargar_limpia(archivos)
        assert tabla_rota.empty and estado_roto["validacion_predicciones"]["por_modelo"] == {"fincast": 1}
        fc_original.to_parquet(pfc, index=False)
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


def prueba_interpolacion_asimetrica():
    from statistics import NormalDist
    from . import fincast_trabajador as ft

    # Pendientes diferentes en cada intervalo: una normal afin en z no detectaria el par equivocado.
    nativos = np.array([[-0.17, -0.09, -0.065, -0.01, 0.002, 0.04, 0.11, 0.13, 0.31]])
    q, _ = ft.expandir_deciles(nativos)
    pares = {0.01: (0, 1), 0.05: (0, 1), 0.15: (0, 1), 0.25: (1, 2), 0.35: (2, 3),
             0.45: (3, 4), 0.55: (4, 5), 0.65: (5, 6), 0.75: (6, 7), 0.85: (7, 8),
             0.95: (7, 8), 0.99: (7, 8)}
    z = NormalDist().inv_cdf
    for p, (i, j) in pares.items():
        w = (z(p) - z(ft.DECILES[i])) / (z(ft.DECILES[j]) - z(ft.DECILES[i]))
        esperado = (1 - w) * nativos[0, i] + w * nativos[0, j]
        _cerca(q[0, ft.NIVELES.index(p)], esperado, 1e-15, f"par asimetrico {p}")
    assert np.array_equal(q[:, metricas.IDECILES], nativos)
    cruzado = nativos.copy()
    cruzado[0, 5] = cruzado[0, 4] - 0.01
    try:
        ft.expandir_deciles(cruzado)
        raise AssertionError("un decil nativo cruzado debe fallar")
    except ValueError as exc:
        assert "nativos no monotonos" in str(exc)
    print("interpolacion asimetrica: pares adyacentes y extremos en z, decil cruzado rechazado: ok")


def prueba_puertas_fincast():
    """Protocolo real de arranque con pesos/codigo pequenos y torch falso: nunca abre pesos reales."""
    import contextlib
    import hashlib
    import io
    import json
    import sys
    import tempfile
    from pathlib import Path
    from types import ModuleType
    from unittest.mock import Mock, patch
    from . import fincast_trabajador as ft, rutas

    os.makedirs(rutas.TMP_FINCAST, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="puertas-", dir=rutas.TMP_FINCAST) as tmp:
        raiz = Path(tmp)
        pesos = raiz / "v1.pth"
        pesos.write_bytes(b"pesos falsos pequenos, no pickle")
        fuentes = {
            "st_moe_pytorch/__init__.py": "from st_moe_pytorch.st_moe_pytorch import MoE\n",
            "st_moe_pytorch/st_moe_pytorch.py": "from st_moe_pytorch.distributed import MoE\n",
            "st_moe_pytorch/distributed.py": "MoE = 'solo desde src'\n",
            "ffm/pytorch_patched_decoder_MOE.py":
                "from st_moe_pytorch import MoE\nclass FFMConfig:\n"
                "    def __init__(self, **kw):\n"
                f"        self.quantiles = {ft.DECILES!r}\n",
        }
        for relativo, contenido in fuentes.items():
            p = raiz / "src" / relativo
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(contenido, encoding="utf-8")
        # Si src se anadiera a sys.path, una importacion tardia quedaria sombreada.
        (raiz / "src" / "sombra_fincast_prueba.py").write_text("raise RuntimeError('sombreado')\n", encoding="utf-8")
        huellas = {n: hashlib.sha256((raiz / "src" / n).read_bytes()).hexdigest() for n in fuentes}
        falso = ModuleType("torch")
        for n in ("set_num_threads", "use_deterministic_algorithms", "manual_seed"):
            setattr(falso, n, Mock())
        falso.load = Mock(side_effect=RuntimeError("weights_only rechazo el archivo falso"))
        argv = [ft.__file__, "--codigo", tmp, "--pesos", str(pesos), "--sha256", ft.sha256(pesos)]
        # Un paquete preexistente fuera de src tampoco puede prevalecer en sys.modules.
        ajeno = ModuleType("st_moe_pytorch")
        ajeno.MoE = "fuera de src"
        with patch.dict(sys.modules, {"torch": falso, "st_moe_pytorch": ajeno}), \
                patch.object(ft, "CODIGO_HUELLAS", huellas), patch.object(sys, "argv", argv):
            def bloqueado(mensaje):
                salida = io.StringIO()
                with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
                    assert ft.main() == 1
                hola = json.loads(salida.getvalue())
                assert not hola["listo"] and "BLOQUEADO" in hola["error"] and mensaje in hola["error"], hola

            originales = pesos.read_bytes()
            pesos.write_bytes(b"sha256 diferente")
            bloqueado("sha256 de v1.pth distinto")
            falso.load.assert_not_called()
            pesos.write_bytes(originales)
            p = raiz / "src" / "st_moe_pytorch/distributed.py"
            original = p.read_bytes()
            p.write_bytes(original + b"# alterado\n")
            bloqueado("codigo distinto de la revision auditada")
            falso.load.assert_not_called()
            p.write_bytes(original)
            camino = list(sys.path)
            bloqueado("weights_only rechazo")
            falso.load.assert_called_once_with(str(pesos), map_location="cpu", weights_only=True)
            assert sys.path == camino, "src no debe entrar en sys.path"
            assert sys.modules["st_moe_pytorch"].MoE == "solo desde src"
            assert sys.modules["fincast_decoder_auditado"].MoE == "solo desde src"
            assert ft.importlib.util.find_spec("sombra_fincast_prueba") is None
            for nombre in ("st_moe_pytorch", "st_moe_pytorch.st_moe_pytorch", "st_moe_pytorch.distributed"):
                assert Path(sys.modules[nombre].__file__).is_relative_to(raiz / "src")
    print("puertas FinCast: sha256/codigo/weights_only -> BLOQUEADO; paquete solo desde src sin sombreado: ok")


def prueba_cruces_sprint01():
    import json
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    import pandas as pd
    from . import rutas

    # Fila archivada SPRINT-01: AUDCHF / 1789603200000 / chronos2 / h=1, cruce q35 > q40.
    q = np.array([-0.01109920730781333, -0.005101668741223975, -0.0034524678249336915,
                  -0.002505707647321387, -0.0018402217884041505, -0.0012804745693184572,
                  -0.0005676030178047853, -5.851974677817395e-05, -8.224239539877942e-05,
                  0.0006951809864066405, 0.001005780790331201, 0.001210403535845117,
                  0.0014448286037467284, 0.0018338085155509276, 0.002376031969072656,
                  0.002587807271959619, 0.0031515480022452635, 0.0037435413341544432,
                  0.004656148050310449, 0.005801630113603906, 0.009366047475817041])
    r = {"instrument": "AUDCHF", "origen_ms": 1789603200000, "h": 1, "k": 483, "modelo": "chronos2",
         "ok": True, "y": 0.0023463510363763707, "rv": 5.505363185904469e-06, **dict(zip(banco.QCOLS, q))}
    p = pd.DataFrame([r])
    original = p.copy(deep=True)
    for limpia in (False, True):
        m = banco.metricas_tabla(p, ["chronos2"], limpia=limpia).iloc[0]
        assert m.n == 1
        _cerca(m.crps, 0.000959225938625, 5e-16, "CRPS archivado S01")
        _cerca(m.qlike, -10.962015044244035, 1e-14, "QLIKE archivado S01")
        if limpia:
            assert m.cruces_cuantiles == 1
    assert p.equals(original), "ni ordenar ni mutar la prediccion archivada"
    for nombre in ("hmm", "garch", "chronos2", "toto"):
        class Cruzado:
            def predecir(self, precios, semilla, hmax):
                return np.tile(q, (hmax, 1)), {}
        modelo = Cruzado()
        modelo.nombre = nombre
        s = datos.series_desde_tabla(_tabla(80, np.exp(np.arange(80) * .001)), None)["SINT"]
        cortes, _ = datos.cortes_de_serie(s, [T0 + 40 * DIA], 30, banco.HMAX)
        nuevo = pd.DataFrame(banco.correr_serie(s, cortes, [modelo], banco.SEMILLA))
        assert nuevo.ok.all() and np.array_equal(nuevo[banco.QCOLS], np.tile(q, (3, 1)))
        assert [r["origenes_con_cruce"] for r in banco.contar_cruces(nuevo)["por_modelo_h"]] == [1, 1, 1]
    # Recuento persistido en meta.json y tabla limpia, manteniendo todas las filas principales.
    modelo.nombre = "chronos2"
    ts0 = datos.rejilla_origenes("2025-01-01", "2025-01-01", 1)[0]
    series = datos.series_desde_tabla(_tabla(500, np.exp(np.arange(500) * .001), ts0=ts0), None)
    meta_ds = {"dataset_id": "sintetico_cruces", "dataset_hash": "sha256:cruces",
               "intervalos_ms": [DIA], "proxy": False}
    with tempfile.TemporaryDirectory(prefix="cruces-", dir=rutas.TMP_FINCAST) as tmp:
        with patch.object(datos, "cargar_dataset", return_value=(series, meta_ds)):
            pred, principal, meta = banco.ejecutar("lago_cierre_c20261101", tmp, ["chronos2"], None, 2,
                                                 banco.SEMILLA, 1, "selftest cruces sin pesos", False,
                                                 lambda nombres, hilos: ([modelo], {}))
        assert pred.ok.all() and (principal.n == 2).all() and meta["fallos"] == {"chronos2": 0}
        persistido = json.loads(Path(tmp, "meta.json").read_text(encoding="utf-8"))
        assert [r["origenes_con_cruce"] for r in persistido["cruces_cuantiles"]["por_modelo_h"]] == [2, 2, 2]
        assert (pd.read_csv(Path(tmp, "metricas_limpia.csv")).cruces_cuantiles == 2).all()
    print("cruces SPRINT-01: fila Chronos-2 archivada puntuada intacta; cuatro modelos conservan y cuentan: ok")


def prueba_seleccion_fincast():
    import pandas as pd

    filas = []
    q = np.linspace(-.1, .1, 21)
    for j in range(3):
        for m in ("hmm", "fincast"):
            for h in banco.HORIZONTES:
                filas.append({"instrument": "SINT", "origen_ms": banco.CORTE_LIMPIO_MS + (j + 1) * DIA,
                              "k": j, "h": h, "modelo": m, "ok": m != "fincast" or j != 0,
                              "y": float(j), "rv": .01, **dict(zip(banco.QCOLS, q))})
    p = pd.DataFrame(filas)
    met = banco.metricas_tabla(p, ["hmm", "fincast"], limpia=True)
    estado = banco.estado_limpia(p, met, ["hmm", "fincast"])
    seleccion = estado["seleccion_fincast"]
    assert seleccion["condicionada"] and (met.n == 2).all()
    assert all(r["n_base"] == 3 and r["n_comun"] == 2 and r["fallos_fincast"] == 1
               for r in seleccion["cobertura"])
    scores = [2 / 9 * sum(max(p * (y - v), (p - 1) * (y - v))
                         for p, v in zip(metricas.DECILES, q[metricas.IDECILES])) for y in (0., 1., 2.)]
    a, b = sum(scores) / 3, sum(scores[1:]) / 2
    for r in seleccion["efecto_crps_deciles"]:
        _cerca(r["base"], a, 1e-15, "base sin condicionar")
        _cerca(r["comun"], b, 1e-15, "comun condicionado")
        _cerca(r["variacion_pct"], 100 * (b / a - 1), 1e-12, "efecto de seleccion")
    print("seleccion FinCast: n por activo/h y efecto CRPS deciles antes/despues contra calculo a mano: ok")


def prueba_mt5_presets_rutas_hash():
    import json
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    import data_py
    from . import rutas, informe_mt5 as mt

    assert banco.PRESETS[mt.CABECERA] == banco.PRESETS[mt.ANTIGUO], "cabecera MT5 cambia la rejilla antigua"
    assert banco.PRESETS[mt.ANTIGUO] == dict(tabla="lago_ohlcv_1d", ventana=250, inicio="2025-10-20", fin="2026-10-03", paso_dias=1)
    assert banco.PRESETS["binance_c20261101"] == dict(tabla="binance_ohlcv_1d", ventana=1000, inicio="2023-11-01", fin="2026-10-12", paso_dias=3)
    for ds in rutas.HASHES_MT5:
        assert rutas.dataset_dir(ds).replace("\\", "/") == rutas.DATASETS_V2 + "/" + ds
    for ds in (mt.ANTIGUO, "binance_c20261101"):
        assert rutas.dataset_dir(ds).replace("\\", "/") == rutas.DATASETS + "/" + ds
    assert rutas.dentro(rutas.validar_destino_informe(rutas.DOCS_MT5), rutas.DOCS_MT5)
    for nombre in ("../mt5", "mt5/fuga", "mt5\\fuga"):
        try:
            rutas.dataset_dir(nombre)
            raise AssertionError("ruta de dataset no autorizada aceptada")
        except rutas.RutaNoAutorizada:
            pass
    with tempfile.TemporaryDirectory(prefix="mt5-hash-", dir=rutas.TMP_FINCAST) as tmp:
        for ds in rutas.HASHES_MT5:
            dd = Path(tmp, ds)
            out = Path(tmp, "sin_run_" + ds)
            with patch.object(rutas, "dataset_dir", return_value=str(dd)):
                for existe in (False, True):
                    if existe:
                        dd.mkdir()
                        (dd / "manifest.json").write_text("{}", encoding="utf-8")
                    desc = {"ok": True, "description": {"dataset_id": ds, "dataset_hash": "sha256:incorrecto"}}
                    with patch.object(data_py, "dataset_describe_json", return_value=json.dumps(desc)), \
                            patch.object(__import__("pyarrow.parquet", fromlist=["read_table"]), "read_table") as lectura:
                        try:
                            banco.ejecutar(ds, str(out), ["hmm"], None, 1, banco.SEMILLA, 2, "selftest hash",
                                          False, lambda n, h: (_ for _ in ()).throw(AssertionError("carga modelo prematura")))
                            raise AssertionError("dataset ausente/hash distinto aceptado")
                        except ValueError as exc:
                            assert ("hash/id distinto" if existe else "dataset ausente") in str(exc)
                        lectura.assert_not_called()
                        assert not out.exists(), "se escribe run antes de verificar dataset"
        try:
            banco.ejecutar(mt.AMPLIACION, str(Path(tmp, "prohibido")), ["toto"], None, 1,
                          banco.SEMILLA, 2, "selftest ampliacion", False, None)
            raise AssertionError("Toto permitido en ampliacion")
        except ValueError as exc:
            assert "Toto y FinCast excluidos" in str(exc)
    print("MT5 presets/rutas: cabecera identica, V2 exclusivo, hashes fijados/ausente sin runs, ampliacion restringida: ok")


def prueba_mt5_umbrales():
    from . import informe_mt5 as mt

    def evaluar(valores, rechazos=0, banda=1., fincast=False):
        return mt.evaluar_criterios([dict(h=h, crps_rel=v, n_activos=28, rechazos_01=rechazos,
                                         rechazos_99=0, banda_rel=banda)
                                    for h, v in zip(banco.HORIZONTES, valores)], fincast)
    assert evaluar([.97, .98, .96])["resultado"] == "pasa"
    assert evaluar([.96, .98, .99])["c1"] == "no pasa"
    assert evaluar([.96, .98, .99])["c2"] == evaluar([.96, .98, .99])["c3"] == "pasa"
    assert evaluar([.96, .97, 1.03])["resultado"] == "no pasa"
    assert evaluar([.96, .97, 1.02])["resultado"] == "pasa"
    assert evaluar([.96, .97, .99], rechazos=3)["c2"] == "no pasa"
    assert evaluar([.96, .97, .99], rechazos=3)["c1"] == evaluar([.96, .97, .99], rechazos=3)["c3"] == "pasa"
    assert evaluar([.96, .97, .99], rechazos=2)["resultado"] == "pasa"
    assert evaluar([.96, .97, .99], banda=2.)["resultado"] == "pasa"
    assert evaluar([.96, .97, .99], banda=2.01)["c3"] == "no pasa"
    assert evaluar([.96, .97, .99], banda=2.01)["c1"] == evaluar([.96, .97, .99], banda=2.01)["c2"] == "pasa"
    fc = evaluar([.96, .97, .99], rechazos=28, banda=100, fincast=True)
    assert fc["c1"] == fc["resultado"] == "pasa" and fc["c2"] == fc["c3"] == "no aplica"
    assert mt.evaluar_criterios([])["resultado"] == "no evaluable"
    assert evaluar([.96, .97, float("nan")])["resultado"] == "no evaluable"
    # Solo la cola 99%: 3/28 falla aunque la cola 1% no rechace ningun activo.
    filas_99 = [dict(h=h, crps_rel=v, n_activos=28, rechazos_01=0, rechazos_99=3, banda_rel=1.)
                for h, v in zip(banco.HORIZONTES, [.96, .97, .99])]
    solo_99 = mt.evaluar_criterios(filas_99)
    assert solo_99["c2"] == solo_99["resultado"] == "no pasa"
    assert solo_99["c1"] == solo_99["c3"] == "pasa"
    # Un solo horizonte no puede diluir sus 3/28 rechazos en los otros dos.
    filas_h5 = [{**r, "rechazos_99": 3 if r["h"] == 5 else 0} for r in filas_99]
    solo_h5 = mt.evaluar_criterios(filas_h5)
    assert [r["c2"] for r in solo_h5["horizontes"]] == ["pasa", "no pasa", "pasa"]
    assert solo_h5["c2"] == solo_h5["resultado"] == "no pasa"
    assert solo_h5["c1"] == solo_h5["c3"] == "pasa"
    ag = mt.lectura_agregada(solo_h5, 1., 1.)
    assert ag["rechazos_99"] == 3 and ag["n_activos_horizonte"] == 84
    assert ag["resultado"] == "pasa" and ag["cambios"]["resultado"] == "cambia"
    # Banda: h5 puede fallar con un P99 conjunto que pasa; la lectura no se mezcla.
    banda_h5 = mt.evaluar_criterios([{**r, "rechazos_99": 0, "banda_rel": 2.01 if r["h"] == 5 else 1.}
                                    for r in filas_h5])
    assert banda_h5["c3"] == banda_h5["resultado"] == "no pasa"
    assert mt.lectura_agregada(banda_h5, 2., 1.)["resultado"] == "pasa"
    assert mt.lectura_agregada(banda_h5, 2.01, 1.)["resultado"] == "no pasa"
    assert mt.lectura_agregada(mt.evaluar_criterios([]), 1., 1.)["resultado"] == "no evaluable"
    assert mt.lectura_agregada(fc, fincast=True)["c2"] == "no aplica"
    print("MT5 C1 revision: solo cola 99%, solo h5, sensibilidad agregada Kupiec/banda sin cambiar cada horizonte: ok")
    print("MT5 umbrales aislados: CRPS 2/3 y tope 1.02, Kupiec 2/28 frente 3/28, banda 2/2.01, FinCast no aplica: ok")


def prueba_mt5_diferencial_bordes():
    from . import informe_mt5 as mt

    # 249 frente a 248 barras antes del inicio, sin modelos ni datos reales.
    inicio = T0 + 249 * DIA
    cfg = dict(inicio=datos.fecha(inicio), fin=datos.fecha(inicio + 45 * DIA), paso_dias=1, ventana=250)
    nueva = datos.series_desde_tabla(_tabla(300, np.exp(np.arange(300) * .001)), 0)["SINT"]
    ix = np.arange(1, 300)  # la antigua carece de la primera barra
    antigua = datos.Serie("SINT", nueva.ts_ms[ix], nueva.disp_ms[ix], nueva.close[ix])
    assert mt.causa_exclusivo(nueva, antigua, inicio + DIA, cfg) == "barra extra antes de inicio (249 frente a 248)"
    claves = {("SINT", t) for t in datos.rejilla_origenes(cfg["inicio"], cfg["fin"], 1)}
    d = mt.diferencial({"SINT": antigua}, {"SINT": nueva}, cfg, claves)
    assert d["estado"] == "explicado" and len(d["exclusivos"]) == 1
    assert all(r["max_abs_pb"] == 0 for r in d["resumen_delta_y"])
    assert datos.cortar(nueva, inicio, 250, banco.HMAX) is None, "249 barras no bastan"
    assert datos.cortar(nueva, T0 + 281 * DIA, 250, banco.HMAX) is None, "faltan 20 futuros"
    assert datos.cortar(nueva, T0 + 280 * DIA, 250, banco.HMAX) is not None
    corta = datos.Serie("SINT", nueva.ts_ms[:270], nueva.disp_ms[:270], nueva.close[:270])
    assert mt.causa_exclusivo(nueva, corta, T0 + 260 * DIA, cfg) == "falta de 20 pasos futuros"
    ix = np.delete(np.arange(300), 260)
    hueco = datos.Serie("SINT", nueva.ts_ms[ix], nueva.disp_ms[ix], nueva.close[ix])
    assert datos.fecha(int(nueva.ts_ms[260])) in mt.causa_exclusivo(nueva, hueco, T0 + 261 * DIA, cfg)
    assert "BLOQUEADO" in mt.causa_exclusivo(nueva, nueva, T0 + 270 * DIA, cfg)
    # Se usan sabados y domingos como barras; inicio tardio representa GBPNZD.
    inv = mt.inventario({"SINT": nueva}, cfg)[0]
    assert inv["sabados"] > 0 and inv["domingos"] > 0
    c = datos.cortar(nueva, inicio + DIA, 250, banco.HMAX)
    _cerca(float(c.y[0]), math.log(nueva.close[c.k + 1] / nueva.close[c.k]), 1e-15, "MT5 fin de semana no filtrado")
    tardia = datos.Serie("GBPNZD", nueva.ts_ms + 10 * 365 * DIA, nueva.disp_ms + 10 * 365 * DIA, nueva.close)
    antes = mt.inventario({"GBPNZD": tardia}, cfg)[0]
    assert antes["origenes_validos"] == 0 and antes["sin_ventana"] > 0
    cfg_tardia = {**cfg, "fin": datos.fecha(T0 + (10 * 365 + 280) * DIA), "paso_dias": 20}
    tarde = mt.inventario({"GBPNZD": tardia}, cfg_tardia)[0]
    assert tarde["origenes_validos"] > 0
    primera = datos.rejilla_origenes(tarde["primer_origen"], tarde["primer_origen"], 1)[0]
    assert int((tardia.disp_ms <= primera).sum()) >= 250
    # Antigua D contiene el close de la sesion MT5 anterior con datos: desfase de
    # una barra, incluidos fines de semana y un hueco adicional entre sesiones.
    dias = np.arange(450)
    habiles = dias[(dias + T0 // DIA + 3) % 7 < 5]
    habiles = np.delete(habiles, 253)[:300]
    ts = T0 + habiles * DIA
    precios = np.exp(.001 * np.sin(np.arange(300) * 1.7) + .0001 * np.arange(300) ** 1.1)
    mt5 = datos.Serie("SINT", ts, ts + DIA, precios)
    desplazada = datos.Serie("SINT", ts[1:], ts[1:] + DIA, precios[:-1])
    cfg_al = dict(inicio=datos.fecha(int(ts[251] + DIA)), fin=datos.fecha(int(ts[260] + DIA)),
                  paso_dias=1, ventana=250)
    claves_al = {("SINT", t) for t in datos.rejilla_origenes(cfg_al["inicio"], cfg_al["fin"], 1)}
    al = mt.diferencial({"SINT": desplazada}, {"SINT": mt5}, cfg_al, claves_al)
    assert al["estado"] == "explicado" and not al["sin_alinear"]
    assert len(al["resumen_delta_y_alineado"]) == 3
    assert all(r["delta_y_alineado_pb"] == 0 for r in al["deltas"])
    assert all(r["max_abs_pb"] == 0 for r in al["resumen_delta_y_alineado"])
    assert all(r["max_abs_pb"] > 0 for r in al["resumen_delta_y"])
    assert not al["extremos"], "los extremos deben usar el delta alineado, que es cero"
    _cerca(al["correlaciones_h1"][0]["alineado"], 1., 1e-15, "correlacion h1 desplazada alineada")
    assert al["correlaciones_h1"][0]["misma_etiqueta"] < .99
    assert any(len(datos.rejilla_origenes(r["fecha_barra_mt5_alineada"], r["fecha_barra_antigua"], 1)) > 2
               for r in al["deltas"]), "el fixture debe cruzar sesiones no consecutivas en calendario"
    print("MT5 diferencial alineado: desplazamiento de una barra con huecos, delta 0 frente a misma etiqueta distinto de 0: ok")
    print("MT5 bordes/diferencial: 249/248, hueco fechado, futuros 20, causa desconocida bloqueada, fines de semana y GBPNZD tardio: ok")


def prueba_mt5_ausentes_y_comunes():
    from . import informe_mt5 as mt
    import pandas as pd

    # GARCH de referencia tiene un segundo origen extremo; el cociente debe usar solo el comun.
    filas = []
    q = np.linspace(-.1, .1, 21)
    for h in banco.HORIZONTES:
        for m, i in (("hmm", 1), ("garch", 1), ("chronos2", 1), ("toto", 1), ("fincast", 1), ("garch", 2)):
            filas.append(dict(instrument="SINT", h=h, modelo=m, origen_ms=banco.CORTE_LIMPIO_MS + i * DIA,
                              k=i, ts_ultima_ms=banco.CORTE_LIMPIO_MS + (i - 1) * DIA,
                              y=0. if i == 1 else 100., rv=.01, ok=True, **dict(zip(banco.QCOLS, q))))
    pred = pd.DataFrame(filas)
    vacio = mt.revisar([], ["SINT"])
    assert all(v["resultado"] == "no evaluable" for v in vacio.values())
    base = {"pred": pred[pred.modelo.isin(["hmm", "garch", "chronos2"])],
            "meta": {"config": {"modelos": ["hmm", "garch", "chronos2"]}}}
    toto = {"pred": pred[pred.modelo == "toto"], "meta": {"config": {"modelos": ["toto"]}}}
    r = mt.revisar([base, toto], ["SINT"])
    assert r["fincast"]["resultado"] == "no evaluable"
    assert r["fincast"]["c2"] == r["fincast"]["c3"] == "no aplica"
    assert all(v["crps_rel"] == 1. for v in r["toto"]["horizontes"])
    parcial = mt.revisar([base, toto], ["SINT", "AUSENTE"])
    assert parcial["toto"]["resultado"] == "no evaluable", "no aprobar con activos ausentes"
    co = mt._comunes(pred, ["garch", "fincast"], limpia=True)
    assert len(co) == 6 and not (co.k == 2).any()
    met = banco.metricas_tabla(co, ["garch", "fincast"], limpia=True)
    assert (met.n == 1).all() and (met.crps_deciles == met.crps_deciles.iloc[0]).all()
    fc = {"pred": pred[pred.modelo == "fincast"], "meta": {"config": {"modelos": ["fincast"]}}}
    rankings = mt.clasificaciones([base, toto, fc], ["SINT"])
    assert all("fincast" not in rr for rr in rankings["principal_crps21"].values())
    assert all("fincast" not in rr for rr in rankings["submuestra_toto_crps21"].values())
    assert all(set(rr) == {"hmm", "chronos2", "toto", "fincast"} and set(rr.values()) == {1.}
               for rr in rankings["limpia_comun_crps_deciles"].values())
    ausentes = mt.clasificaciones([base, toto], ["SINT"])
    assert all(v is None for rr in ausentes["limpia_comun_crps_deciles"].values() for v in rr.values())
    print("MT5 ausentes/comunes: modelo o activo incompleto no evaluable; GARCH alineado a Toto/FinCast; no aplica en colas: ok")


def prueba_mt5_situacion_y_coste():
    from . import informe_mt5 as mt

    def revision(v):
        return {m: mt.evaluar_criterios([dict(h=h, crps_rel=x, n_activos=28, rechazos_01=0, rechazos_99=0, banda_rel=1.)
                                        for h, x in zip(banco.HORIZONTES, v)], m == "fincast") for m in mt.MODELOS}
    a, b = revision([.96, .99, 1.01]), revision([.98, 1.01, .99])
    s = mt.situacion(a, b)
    assert s["cambia"] and len(s["cruces"]) == 12
    assert not mt.situacion(a, a)["cambia"]
    a, b = revision([1.1] * 3), revision([1.1] * 3)
    a["hmm"] = revision([1.2] * 3)["hmm"]
    b["hmm"] = revision([1.05] * 3)["hmm"]
    assert mt.situacion(a, b)["cambia"] and not mt.situacion(a, b)["cruces"], "cambio de orden sin cruzar umbral"
    meta = dict(pared_modelos={m: dict(total_s=2., por_origen_s=.2) for m in ["hmm", "garch", "chronos2"]},
                pared_s=7., pared_carga_modelos_s=5., omitidos={"SINT": dict(evaluados=10)},
                config=dict(paso_dias=20, hilos_torch=2))
    c = mt.presupuesto({"meta": meta}, [dict(origenes_validos=100)])
    _cerca(c["estimada_s"], 75., 1e-12, "cuenta pared extrapolada")
    assert c["cabe_2h"] and not mt.presupuesto({"meta": meta}, [dict(origenes_validos=20000)])["cabe_2h"]
    meta["pared_total_s"] = 15.
    _cerca(mt.presupuesto({"meta": meta}, [dict(origenes_validos=100)])["estimada_s"], 78., 1e-12,
           "lectura/hash/preparacion fija incluida")
    print("MT5 situacion/coste: cruces 1/.97, orden sin cruce, cuenta por modelo y limite 2h: ok")


def prueba_mt5_oraculo_parquet():
    import json
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    import pandas as pd
    from . import rutas, informe_mt5 as mt

    close = np.exp(np.arange(275) * .001) * 1.1
    tabla = _tabla(275, close, inst="EURUSD")
    serie = datos.series_desde_tabla(tabla, 0)["EURUSD"]
    origen = T0 + 250 * DIA
    corte = datos.cortar(serie, origen, 250, banco.HMAX)
    pred = pd.DataFrame(banco._filas_corte("EURUSD", corte, "garch", np.zeros((20, 21)), {}, 0., None))
    with tempfile.TemporaryDirectory(prefix="mt5-oraculo-", dir=rutas.TMP_FINCAST) as tmp:
        tabla.to_parquet(Path(tmp, "precios.parquet"), index=False)
        Path(tmp, "manifest.json").write_text(json.dumps(dict(tables=[dict(table_id="lago_ohlcv_1d", path="precios.parquet")])), encoding="utf-8")
        with patch.object(datos, "cortar", side_effect=AssertionError("el oraculo no puede usar el banco")), \
                patch.object(datos, "cargar_dataset", side_effect=AssertionError("el oraculo lee parquet directo")):
            ora = mt.oraculo(dict(pred=pred), tmp)
        assert ora["coincide"] and ora["close_0"] == close[249] and ora["close_1"] == close[250]
        _cerca(ora["log_c1_c0"], .001, 1e-15, "oraculo parquet h1 independiente")
        run = dict(pred=pred, run="fixture-parquet")
        assert mt.validar_objetivos(run, {"EURUSD": serie}, dict(ventana=250))["identicos"]
        pred.loc[pred.h == 1, "y"] += .01
        try:
            mt.validar_objetivos(run, {"EURUSD": serie}, dict(ventana=250))
            raise AssertionError("objetivo alterado aceptado en el diferencial")
        except ValueError as exc:
            assert "difieren del dataset" in str(exc)
    print("MT5 oraculo: dos close de parquet sin funciones del banco; objetivo alterado bloquea informe: ok")
