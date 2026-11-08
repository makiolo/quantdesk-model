"""--selftest de banco_precision.py: aserciones reales, sin red, rapido (< 2 min)."""
from __future__ import annotations

import contextlib
import io
import os
import shutil
import time

import numpy as np
import torch
from scipy.stats import norm

from . import banco, datos, dupire, informe, medidas, modelo, rutas
from .redondeo import DTYPE, MAXIMO, MIN_NORMAL, TIPOS, U, Contador, redondear

TMP = "E:/quantdesk-lab/tmp/TS-00-PREC"
# Tolerancias declaradas (no se relajan para que pasen: salen del analisis de cada prueba)
TOL_DUPIRE_MAX = 0.05  # error relativo maximo de sigma_loc frente a la sigma constante del cono lognormal (medido ~0.025)
TOL_DUPIRE_MEDIA = 0.01  # sesgo medio relativo (medido ~0.004)
TOL_CRPS_NORMAL = 5e-3  # CRPS por cuantiles (J = 41, colas al cuantil extremo) frente al cerrado de N(0,1): medido <= 2.3e-3


def _ok(nombre: str, detalle: str = "") -> None:
    print(f"OK       {nombre}" + (f": {detalle}" if detalle else ""), flush=True)


def prueba_redondeo() -> None:
    holgura = 1.0 + 2.0**-22  # doble redondeo f64 -> f32 -> tipo de ml_dtypes (ver redondeo.py)
    codigos = {"e4m3": (np.uint8, 256), "e5m2": (np.uint8, 256), "bf16": (np.uint16, 65536), "f16": (np.uint16, 65536)}
    for t, (ut, n) in codigos.items():
        with np.errstate(invalid="ignore"):  # los codigos NaN/inf se descartan justo debajo
            v = np.arange(n, dtype=ut).view(DTYPE[t]).astype(np.float64)
        v = np.unique(v[np.isfinite(v) & (v >= MIN_NORMAL[t]) & (v <= MAXIMO[t])])
        # los puntos medios entre valores representables contiguos son el peor caso del error relativo
        mid = (v[1:] + v[:-1]) / 2.0
        rel = np.abs(redondear(mid, t) - mid) / mid
        assert rel.max() <= U[t] * holgura, (t, rel.max(), U[t])
        # el peor caso exacto es el primer empate de cada binada: u / (1 + u); si no se alcanza, el tipo no es el que dice ser
        assert abs(rel.max() / (U[t] / (1 + U[t])) - 1) < 1e-6, f"{t}: peor caso {rel.max():.6e}, esperado {U[t] / (1 + U[t]):.6e}"
        assert np.array_equal(redondear(v, t), v), f"{t}: los valores representables deben quedar intactos"
    gen = np.random.default_rng(0)
    for t in TIPOS:
        x = np.exp(gen.uniform(np.log(MIN_NORMAL[t]) + 1e-6, np.log(MAXIMO[t] / 2.0), 200_000))
        if t in ("bf16", "f32"):  # rango enorme: se acota a un intervalo representativo en f64
            x = np.exp(gen.uniform(-30.0, 30.0, 200_000))
        rel = np.abs(redondear(x, t) - x) / x
        assert rel.max() <= U[t] * holgura, (t, rel.max(), U[t])
        assert rel.max() >= 0.5 * U[t], (t, rel.max(), U[t])
    # recorte: saturacion, nunca NaN ni inf por desbordamiento
    for t in TIPOS:
        c = Contador()
        y = redondear(np.array([1e300, -1e300, 2 * MAXIMO[t]]), t, contador=c)
        assert np.all(np.isfinite(y)) and np.all(np.abs(y) == MAXIMO[t]), (t, y)
        assert c.n_recortados == 3 and c.como_dict()["recortados_pct"] == 100.0
    assert redondear(np.array([1000.0]), "e4m3")[0] == 448.0
    assert np.isnan(redondear(np.array([np.nan]), "e4m3")[0])
    # subnormales: 1e-4 desaparece en e4m3 (menor subnormal 2^-9) y se conserva en e5m2 (2^-16)
    c = Contador()
    r = np.array([1e-4, 0.0, 3e-4, 1e-2])
    assert redondear(r, "e4m3", contador=c)[0] == 0.0 and c.n_a_cero == 2 and c.n_no_nulos == 3
    assert redondear(np.array([1e-4]), "e5m2")[0] != 0.0
    # variante con escala: nada se recorta, el maximo se conserva y es invariante a multiplicar por 2^k
    x = gen.standard_normal(5000) * 1e-2
    for t in ("e4m3", "e5m2", "f16", "bf16"):
        c = Contador()
        con = redondear(x, t, escala=True, contador=c)
        assert c.n_recortados == 0
        assert np.array_equal(redondear(x * 2.0**-9, t, escala=True), con * 2.0**-9)
        i = np.argmax(np.abs(x))
        assert abs(con[i] - x[i]) / abs(x[i]) <= U[t] * holgura
    assert np.abs(redondear(x, "e4m3", escala=True) - x).mean() < np.abs(redondear(x, "e4m3") - x).mean()
    # por muestra: el resultado de una fila no depende de las otras
    m = np.stack([x[:100], x[100:200] * 1000.0])
    sola = redondear(m[:1], "e4m3", escala=True, por_muestra=True)
    assert np.array_equal(sola[0], redondear(m, "e4m3", escala=True, por_muestra=True)[0])
    _ok("redondeo", "error relativo teorico de e4m3/e5m2/bf16/f16/f32, saturacion, subnormales y variante con escala")


def prueba_crps() -> None:
    # caso calculado a mano: alfa = (0.25, 0.5, 0.75), q = (-1, 0, 1), y = 0.5
    # pesos 0.375, 0.25, 0.375; pinball 0.375, 0.25, 0.125 -> 2 * (0.140625 + 0.0625 + 0.046875) = 0.5
    a = np.array([0.25, 0.5, 0.75])
    c = modelo.crps_cuantiles(np.array([[-1.0, 0.0, 1.0]]), np.array([0.5]), a)
    assert abs(c - 0.5) < 1e-12, c
    # prediccion degenerada: el CRPS es |y - q| con la rejilla simetrica del banco
    for y, q in ((0.3, 2.0), (-1.0, -1.0), (5.0, 0.0)):
        got = modelo.crps_cuantiles(np.full((1, modelo.J), q), np.array([y]))
        assert abs(got - abs(y - q)) < 1e-12, (y, q, got)
    # frente al CRPS cerrado de una N(0,1)
    z = norm.ppf(modelo.ALFAS)[None, :]
    for y in (-1.5, 0.0, 0.3, 2.0):
        cerrado = y * (2 * norm.cdf(y) - 1) + 2 * norm.pdf(y) - 1 / np.sqrt(np.pi)
        got = modelo.crps_cuantiles(z, np.array([y]))
        assert abs(got - cerrado) < TOL_CRPS_NORMAL, (y, got, cerrado)
    w = modelo.W_ALFA
    assert abs(w.sum() - 1) < 1e-12 and abs((w * modelo.ALFAS).sum() - 0.5) < 1e-12
    _ok("CRPS por cuantiles", "caso a mano (0.5), degenerado = |y-q|, frente al CRPS cerrado de N(0,1)")


def prueba_cono() -> None:
    cfg = banco.PERFILES["mini"]
    torch.manual_seed(0)
    m = modelo.crear_modelo(cfg)
    gen = np.random.default_rng(1)
    X = gen.standard_normal((16, cfg["W"])) * 0.05
    q = modelo.cono(m, X)
    assert q.shape == (16, cfg["H"], modelo.J) and np.all(np.diff(q, axis=-1) > 0), "cono no monotono en alfa (init)"
    with torch.no_grad():  # pesos grandes: la monotonia es por construccion, no por buen condicionamiento
        for p in m.parameters():
            p.mul_(8.0)
    q = modelo.cono(m, X)
    # con pesos x8 softplus puede subdesbordar en f32 (huecos exactamente 0): monotonia debil, nunca decreciente
    assert np.all(np.isfinite(q)) and np.all(np.diff(q, axis=-1) >= 0), "cono no monotono en alfa (pesos grandes)"
    ref = modelo.a_f64(m)
    for t in TIPOS:
        for esc in (False, True):
            mt = modelo.modelo_redondeado(ref, t, esc, None)
            qt = modelo.cono(mt, X, hook=lambda n, x, t=t, esc=esc: torch.from_numpy(redondear(x.numpy(), t, escala=esc, por_muestra=True)))
            assert np.all(np.isfinite(qt)) and np.all(np.diff(qt, axis=-1) >= 0), f"{t} escala={esc}: el redondeo rompe la monotonia debil"
    # el entrenamiento mejora la perdida y el cono sigue monotono
    R, validos = datos.corpus_entrenamiento(3, cfg)
    cfg2 = dict(cfg, pasos=150)
    mod, info = modelo.entrenar(cfg2, 3, R, validos, datos.rng(3, datos.F_LOTES))
    assert np.all(np.diff(modelo.cono(mod, X), axis=-1) > 0)

    # el entrenamiento mejora la pinball en un lote fijo (mismo modelo inicial: misma semilla de torch)
    t = validos[np.arange(0, len(validos), len(validos) // 400)][:400]
    Xf = R[t[:, None] + np.arange(-cfg["W"] + 1, 1)[None, :]]
    Yf = torch.tensor(np.cumsum(R[t[:, None] + np.arange(1, cfg["H"] + 1)[None, :]], axis=1) / modelo.ESCALA_SALIDA, dtype=torch.float32)
    alfas = torch.tensor(modelo.ALFAS, dtype=torch.float32)
    torch.manual_seed(3)
    ini = modelo.crear_modelo(cfg).eval()
    antes = float(modelo.perdida_pinball(torch.tensor(modelo.cono(ini, Xf), dtype=torch.float32), Yf, alfas))
    despues = float(modelo.perdida_pinball(torch.tensor(modelo.cono(mod, Xf), dtype=torch.float32), Yf, alfas))
    assert despues < antes, (antes, despues)
    _ok("cono monotono en alfa", f"por construccion, con pesos x8 y tras redondear; pinball en lote fijo {antes:.4f} -> {despues:.4f}")


def prueba_dupire() -> None:
    H = 12
    h = np.arange(1, H + 1) / datos.DIAS_ANIO
    z = norm.ppf(modelo.ALFAS)
    peor = 0.0
    for sig in (0.1, 0.2, 0.4):
        q = -0.5 * sig**2 * h[:, None] + sig * np.sqrt(h)[:, None] * z[None, :]
        S, _ = dupire.niveles_recentrados((q / modelo.ESCALA_SALIDA)[None])
        K, estado = dupire.rejilla_k(S[None])
        assert (estado == dupire.REJILLA_OK).all()
        s = dupire.sigma_loc(S, K)
        assert np.isfinite(s).all(), f"sigma={sig}: puntos fuera de la region valida en un cono lognormal"
        rel = s / sig - 1.0
        assert np.abs(rel).max() < TOL_DUPIRE_MAX, (sig, np.abs(rel).max())
        assert abs(rel.mean()) < TOL_DUPIRE_MEDIA, (sig, rel.mean())
        peor = max(peor, float(np.abs(rel).max()))
    # un cono degenerado (cuantiles empatados, sin variacion en h) deja todos los puntos invalidos: se cuentan, no se rellenan
    q = np.zeros((1, H, modelo.J))
    S, _ = dupire.niveles_recentrados(q)
    assert np.isnan(dupire.sigma_loc(S, np.full((1, H - 2, dupire.NK), 1.0) + np.linspace(-0.01, 0.01, dupire.NK))).all()
    _ok("Dupire", f"recupera sigma constante 0.1/0.2/0.4 desde un cono lognormal (error relativo max {peor:.4f} < {TOL_DUPIRE_MAX})")


def _cono_sesgado(sig: float, sesgo: float, H: int) -> np.ndarray:
    """Cono sintetico (H, J) en unidades del modelo: cuantiles de un log-rendimiento acumulado de vol anual sig con asimetria
    tipo Cornish-Fisher (monotono en alfa mientras |sesgo| < 1.16)."""
    h = np.arange(1, H + 1) / datos.DIAS_ANIO
    z = norm.ppf(modelo.ALFAS)
    return sig * np.sqrt(h)[:, None] * (z + sesgo * (z**2 - 1.0) / 6.0)[None, :] / modelo.ESCALA_SALIDA


def prueba_rejilla_k() -> None:
    H, N = 8, 3
    sigs, sesgos, esc = (0.10, 0.20, 0.30, 0.40, 0.50), (-0.8, -0.4, 0.0, 0.4, 0.8), (0.7, 1.0, 1.4)
    # 5 conos f64 sinteticos con intervalos [S_h(0,10), S_h(0,90)] distintos (vol y asimetria distintas) y 3 entradas por modelo
    Qs = np.stack([np.stack([_cono_sesgado(s * e, g, H) for e in esc]) for s, g in zip(sigs, sesgos)])  # (5, N, H, J)
    S_ref = np.stack([dupire.niveles_recentrados(Q)[0] for Q in Qs])
    K, estado = dupire.rejilla_k(S_ref)
    assert K.shape == (N, H - 2, dupire.NK) and (estado == dupire.REJILLA_OK).all() and np.isfinite(K).all()
    # comprobacion independiente de la funcion: todo K dentro del intervalo de CADA uno de los 5 modelos f64, a los tres horizontes
    ancho_min = np.inf
    for m in range(len(sigs)):
        for n in range(N):
            for k in range(1, H - 1):
                for hz in (k - 1, k, k + 1):
                    assert K[n, k - 1].min() >= S_ref[m, n, hz, dupire.I10], (m, n, k, hz)
                    assert K[n, k - 1].max() <= S_ref[m, n, hz, dupire.I90], (m, n, k, hz)
                ancho_min = min(ancho_min, K[n, k - 1].max() - K[n, k - 1].min())
        assert dupire.k_fuera_intervalo(S_ref[m], K) == (0, K.size), "K fuera del intervalo propio de un f64"
    # contraste: la rejilla del cono medio (consenso, el metodo del intento 1) SI se sale del intervalo de algun f64: la prueba discrimina
    S_cons = dupire.niveles_recentrados(Qs.mean(axis=0))[0]
    K_cons, _ = dupire.rejilla_k(S_cons[None])
    assert sum(dupire.k_fuera_intervalo(S_ref[m], K_cons)[0] for m in range(len(sigs))) > 0, "la prueba no distingue el consenso de la interseccion"
    # un cono redondeado mucho mas estrecho que la rejilla comun: sus K quedan fuera de su intervalo propio y se cuentan
    S_est = dupire.niveles_recentrados(np.stack([_cono_sesgado(0.04, 0.0, H)] * N))[0]
    fuera, total = dupire.k_fuera_intervalo(S_est, K)
    assert total == K.size and 0 < fuera <= total, (fuera, total)
    # interseccion vacia / degenerada / correcta (S dado a mano: S_h(0,10) y S_h(0,90) de dos modelos, 3 entradas, 3 horizontes)
    S = np.ones((2, 3, 3, modelo.J))
    S[0, :, :, dupire.I10], S[0, :, :, dupire.I90] = 1.0, 1.5
    S[1, :, :, dupire.I10], S[1, :, :, dupire.I90] = [[1.3], [1.5 - 1e-6], [1.6]], 2.0  # anchos de la interseccion: 0.2, 1e-6, -0.1
    K, estado = dupire.rejilla_k(S)
    assert estado.shape == (3, 1) and estado[:, 0].tolist() == [dupire.REJILLA_OK, dupire.REJILLA_DEGENERADA, dupire.REJILLA_VACIA], estado
    assert K[0, 0, 0] == 1.3 and K[0, 0, -1] == 1.5 and np.all(np.diff(K[0, 0]) > 0), K[0, 0]
    assert np.isnan(K[1:]).all(), "una rejilla vacia o degenerada no se rellena"
    sig = dupire.sigma_loc(S[0], K)
    assert np.isnan(sig[1:]).all(), "sigma_loc debe ser NaN donde no hay rejilla"
    assert dupire.k_fuera_intervalo(S[0], K) == (0, dupire.NK), "los K NaN no cuentan como fuera"
    # conos con intervalos disjuntos (desplazados +-5 % con vol 10 %): interseccion vacia en todas las entradas
    h = (np.arange(1, H + 1) / datos.DIAS_ANIO)[:, None]
    z = norm.ppf(modelo.ALFAS)[None, :]
    disj = np.stack([np.exp(d + 0.1 * np.sqrt(h) * z)[None] for d in (0.05, -0.05)])
    K, estado = dupire.rejilla_k(disj)
    assert (estado == dupire.REJILLA_VACIA).all() and np.isnan(K).all()
    _ok("rejilla de K comun", f"todo K dentro del intervalo de cada uno de 5 f64 a k-1, k, k+1 (ancho min {ancho_min:.4f}); el consenso no lo cumple; vacia/degenerada = NaN")


def prueba_rutas() -> None:
    R = rutas.RUNS
    for p in (f"{R}/completo", f"{R}/a/b", f"{R}/x/../y"):
        assert rutas.validar_out(p) == os.path.abspath(p)
    for p in (f"{R}/completo", rutas.DOCS, rutas.DOCS + "/sub"):
        assert rutas.validar_informe(p) == os.path.abspath(p), p
    # rutas ajenas (otro disco, otro proyecto, ".." que se escapa, prefijo parecido, tmp, el propio RUNS para --out, vacio)
    ajenas = [
        "C:/quantdesk_prueba_no_escribir", "C:/quantdesk_prueba_no_escribir/x", "S:/projects/quantdesk/x", "S:/Projects/quantdesk-model/docs",
        R + "/..", R + "/../otro", R + "-otro/x", "E:/quantdesk-lab/runs/TS-00-PREC2/x", "E:/quantdesk-lab/tmp/TS-00-PREC/x",
        "E:/quantdesk-lab/runs", "E:/quantdesk-lab", "", R, rutas.REPO, rutas.REPO + "/docs/plans/current", rutas.DOCS + "/../TI-13-PUB",
        rutas.DOCS + "-otro", rutas.REPO + "/scripts",
    ]
    for p in ajenas:  # el propio RUNS tampoco vale: es un subdirectorio estricto
        for f in (rutas.validar_out, rutas.validar_informe):
            try:
                f(p)
            except rutas.RutaNoAutorizada:
                continue
            raise AssertionError(f"{f.__name__} acepto una ruta no autorizada: {p!r}")
    try:
        rutas.validar_out(rutas.DOCS)  # --out no escribe en el directorio documental
    except rutas.RutaNoAutorizada:
        pass
    else:
        raise AssertionError("--out acepto el directorio documental")
    # extremo a extremo por la linea de ordenes: error y codigo != 0 sin escribir nada
    import importlib

    cli = importlib.import_module("banco_precision")
    inexistente = "C:/quantdesk_prueba_no_escribir"
    assert not os.path.exists(inexistente)
    base = f"{TMP}/rutas-{os.getpid()}"
    os.makedirs(base, exist_ok=True)
    try:
        with open(f"{base}/resultados.json", "w", encoding="utf-8") as f:  # un directorio por lo demas valido, pero no autorizado
            f.write('{"datos": {}, "meta": {}}\n')
        casos = (["--out", inexistente + "/x"], ["--out", inexistente + "/x", "--perfil", "mini"], ["--informe", inexistente],
                 ["--out", base + "/run"], ["--informe", base])
        for argv in casos:
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                rc = cli.main(argv)
            assert rc != 0 and "debe ser un subdirectorio" in salida.getvalue(), (argv, rc, salida.getvalue())
            assert not os.path.exists(inexistente), "la linea de ordenes creo un directorio fuera de las rutas autorizadas"
        assert sorted(os.listdir(base)) == ["resultados.json"], "la linea de ordenes escribio en un directorio no autorizado"
    finally:
        shutil.rmtree(base, ignore_errors=True)
    _ok("rutas de escritura", f"--out solo bajo {R}; --informe solo ahi o en docs/.../TS-00-PREC; {len(ajenas)} rutas ajenas rechazadas (codigo 2)")


def prueba_garch() -> None:
    r = datos.simular_garch(20000, datos.rng(20240, datos.F_GARCH_REC), **datos.GARCH_VERDAD)
    e = medidas.ajustar_garch(r)
    assert abs(e["alfa"] + e["beta"] - 0.98) < 0.01, e
    assert abs(e["alfa"] - 0.08) < 0.03 and abs(e["beta"] - 0.90) < 0.03, e
    assert abs(e["omega"] / datos.GARCH_VERDAD["omega"] - 1.0) < 1.0, e  # omega es poco identificable: solo orden de magnitud
    _ok("recuperacion GARCH en f64", f"20000 puntos: alfa+beta = {e['alfa'] + e['beta']:.4f}, alfa = {e['alfa']:.4f}, beta = {e['beta']:.4f}")


def prueba_hmm() -> None:
    r, s = datos.simular_regimen(1500, datos.rng(7, datos.F_REG_REC))
    e = medidas.ajustar_hmm(r)
    err = medidas.error_hmm(e, s)
    assert e["sigma"][0] < e["sigma"][1], "estados sin ordenar por sigma"
    assert err["hmm_matriz"] < 0.05 and err["hmm_sigma"] < 0.15 and err["hmm_regimen"] < 0.15, err
    assert np.allclose(e["gamma"].sum(axis=1), 1.0, atol=1e-6) and e["gamma"].shape == (1500, 2)
    # con los estados invertidos el error tendria que ser grande: la alineacion se esta comprobando de verdad
    inv = medidas.error_hmm(dict(e, P=e["P"][::-1, ::-1], gamma=e["gamma"][:, ::-1], sigma=e["sigma"][::-1]), s)
    assert inv["hmm_regimen"] > 3 * err["hmm_regimen"], (inv, err)
    _ok("HMM del motor quantdesk", f"|P-P0| = {err['hmm_matriz']:.3f}, Brier = {err['hmm_regimen']:.3f}, sigma rel = {err['hmm_sigma']:.3f}")


def prueba_veredictos() -> None:
    assert medidas._sd([1.0, 2.0, 3.0]) == 1.0  # ddof = 1
    # medida 1: umbral = max(sd_T, sd_f64) = 1; dif = |2 - 1| = 1 no supera el umbral, 2.5 si
    v = medidas.veredicto_m1([1.0, 2.0, 3.0], [0.0, 1.0, 2.0])
    assert (v["veredicto"], v["umbral"], v["dif"], v["cociente"]) == ("no pierde", 1.0, 1.0, 1.0), v
    v = medidas.veredicto_m1([2.5, 3.5, 4.5], [0.0, 1.0, 2.0])
    assert (v["veredicto"], v["dif"], v["cociente"]) == ("pierde", 2.5, 2.5), v
    v = medidas.veredicto_m1([0.0, 3.0, 6.0], [0.0, 1.0, 2.0])  # el umbral es el mayor de los dos sd
    assert v["umbral"] == 3.0 and v["veredicto"] == "no pierde", v
    assert medidas.veredicto_m1([None, 1.0, 2.0], [0.0, 1.0, 2.0])["veredicto"] == "no medida"
    # medidas 2 y 3
    assert medidas.veredicto_error(2.0, 1.0)["veredicto"] == "pierde"
    assert medidas.veredicto_error(0.5, 1.0)["veredicto"] == "no pierde"
    assert medidas.veredicto_error(0.5, 1.0, cobertura=0.5)["veredicto"] == "pierde"  # cobertura baja
    assert medidas.veredicto_error(None, 1.0, cobertura=0.0)["veredicto"] == "pierde"  # sin puntos validos
    assert medidas.veredicto_error(None, 1.0)["veredicto"] == "no medida"
    # umbral de la medida 2: RMS sobre entradas de la sd entre modelos (ddof = 1); dos modelos que difieren en 2 -> sd = sqrt(2)
    a, b = np.zeros((3, 4)), np.full((3, 4), 2.0)
    assert abs(np.sqrt(np.mean(np.var(np.stack([a, b]), axis=0, ddof=1))) - np.sqrt(2.0)) < 1e-12
    _ok("veredictos y umbrales", "sd con ddof = 1, umbral max(sd_T, sd_f64), cobertura y no medida")


def _banco_mini(base: str) -> str:
    """Dos ejecuciones del perfil mini en base: mismo hash, verificar OK y verificar detecta manipulaciones."""
    hashes = []
    for i in (1, 2):
        d = f"{base}/run{i}"
        os.makedirs(d, exist_ok=True)
        doc = banco.ejecutar("mini", d, "selftest", log=lambda *_: None, hilos=1)
        hashes.append(banco.escribir_resultados(doc, d))  # rechaza NaN/inf: lo no definido es null con motivo
        informe.escribir_informe(d)
        assert informe.verificar(d) == 0
        assert set(doc["datos"]["m1"]["no_medidas"]) == {"vol_de_la_vol"}
    assert hashes[0] == hashes[1], f"dos ejecuciones con las mismas semillas dan hashes distintos: {hashes}"
    d = f"{base}/run1"
    # el hash canonico ignora meta: cambiar la fecha y el tiempo no lo mueve
    doc = banco.leer_resultados(d)
    doc["meta"]["fecha_utc"], doc["meta"]["tiempo_pared_s"] = "2000-01-01T00:00:00Z", 1.0
    assert banco.hash_canonico(doc["datos"]) == hashes[0]
    # una cifra cambiada en el informe, o un JSON manipulado, deben hacer fallar --verificar
    with open(f"{d}/informe.md", encoding="utf-8") as f:
        texto = f.read()
    assert "## 5. ¿Basta fp8?" in texto and "## 4. Tabla final tipo × medida" in texto
    malo = f"{base}/malo_informe"
    shutil.copytree(d, malo)
    marca = "\n| e4m3 sin escala | "
    i = texto.index(marca) + len(marca)  # primera cifra de una fila de tabla
    with open(f"{malo}/informe.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(texto[:i] + ("9" if texto[i] != "9" else "8") + texto[i + 1 :])
    assert informe.verificar(malo) == 1, "verificar acepto un informe con una cifra cambiada"
    malo2 = f"{base}/malo_json"
    shutil.copytree(d, malo2)
    with open(f"{malo2}/resultados.json", encoding="utf-8") as f:
        js = f.read()
    k = js.index('"umbral": ') + len('"umbral": ')
    with open(f"{malo2}/resultados.json", "w", encoding="utf-8", newline="\n") as f:
        f.write(js[:k] + "12345.0, \"x_manipulado\": " + js[k:])
    assert informe.verificar(malo2) == 1, "verificar acepto un JSON manipulado"
    return hashes[0]


def prueba_banco_mini() -> None:
    base = f"{TMP}/selftest-{os.getpid()}"
    os.makedirs(base, exist_ok=True)
    try:
        with contextlib.redirect_stdout(io.StringIO()):  # los verificar internos no ensucian la salida
            h = _banco_mini(base)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    _ok("banco mini de extremo a extremo", f"2 ejecuciones con el mismo hash canonico {h[:16]}...; --verificar detecta informe y JSON manipulados")


def selftest() -> int:
    # Un solo hilo: con la maquina compartida y saturada, dos hilos de torch se esperan entre si y el selftest se multiplica por 8.
    banco.configurar_torch(1)
    t0 = time.time()
    pruebas = (prueba_redondeo, prueba_crps, prueba_veredictos, prueba_cono, prueba_dupire, prueba_rejilla_k, prueba_rutas,
               prueba_garch, prueba_hmm, prueba_banco_mini)
    for p in pruebas:
        t = time.time()
        try:
            p()
        except Exception as exc:  # noqa: BLE001
            import traceback

            traceback.print_exc()
            print(f"FALLO    {p.__name__}: {type(exc).__name__}: {exc}")
            print("selftest FALLO")
            return 1
        print(f"         ({p.__name__}: {time.time() - t:.1f} s)", flush=True)
    print(f"tiempo total del selftest: {time.time() - t0:.0f} s")
    print("selftest ok")
    return 0
