"""Informe Markdown generado desde resultados.json (nunca escrito a mano) y verificacion hash + cifras."""
from __future__ import annotations

import os
import re

from . import banco
from .medidas import CANTIDADES_M2, METRICAS_M1
from .redondeo import TIPOS, celdas

DIRECCION_INFORME = "docs/plans/current/execution/TS-00-PREC/informe.md"
OBJETIVO_PARED_MIN = 45  # la ficha pide reducir tamaños si el banco completo pasa de ~45 min en CPU


def etiqueta(cid: str) -> str:
    if cid == "f64":
        return "f64 (referencia)"
    t, v = cid.split(":")
    return f"{t} {'con' if v == 'con' else 'sin'} escala"


def fe(x, nd: int = 3) -> str:
    return "n/m" if x is None else f"{x:.{nd}e}"


def fc(x) -> str:
    return "n/m" if x is None else f"{x:.2f}"


def fp(x) -> str:
    return "n/m" if x is None else f"{x:.2f}"


def tabla(cabecera: list, filas: list) -> list:
    out = ["| " + " | ".join(cabecera) + " |", "|" + "|".join("---" for _ in cabecera) + "|"]
    out += ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]
    return out + [""]


def ids_tipo(doc) -> list:
    """Celdas en orden canonico (f32, bf16, f16, e4m3, e5m2; sin escala antes que con escala), no el del JSON ordenado."""
    return [c for c, _, _ in celdas(incluir_f64=False)]


def resumen(filas: list) -> tuple:
    """Veredicto global de una medida desde la lista de dicts con 'veredicto': (texto, n_pierde, n_medidas, n_no_medidas)."""
    med = [f for f in filas if f["veredicto"] in ("pierde", "no pierde")]
    perd = [f for f in med if f["veredicto"] == "pierde"]
    if not med:
        return "no medida", 0, 0, len(filas)
    return ("pierde" if perd else "no pierde"), len(perd), len(med), len(filas) - len(med)


def _cociente_orden(f: dict) -> float:
    c = f.get("cociente")
    return float("inf") if c is None else c


def filas_celda(d: dict, cid: str) -> dict:
    """Para una celda: {medida: [(nombre, dict con veredicto/valor/umbral/cociente)]} de las tres medidas."""
    m1 = []
    for mid, _, _ in METRICAS_M1:
        c = d["m1"]["metricas"][mid]["celdas"][cid]
        m1.append((mid, {"veredicto": c["veredicto"], "valor": c.get("dif"), "umbral": c.get("umbral"), "cociente": c.get("cociente")}))
    m2 = []
    for gid, _ in CANTIDADES_M2:
        c = d["m2"]["cantidades"][gid]["celdas"][cid]
        m2.append((gid, {"veredicto": c["veredicto"], "valor": c.get("error"), "umbral": c.get("umbral"), "cociente": c.get("cociente")}))
    c3 = d["m3"]["celdas"][cid]
    m3 = [("sigma_loc", {"veredicto": c3["veredicto"], "valor": c3.get("error"), "umbral": c3.get("umbral"), "cociente": c3.get("cociente")})]
    return {"M1": m1, "M2": m2, "M3": m3}


def generar_informe(doc: dict) -> str:
    d, meta = doc["datos"], doc["meta"]
    cfg = d["config"]
    ids = ids_tipo(doc)
    L: list = []
    a = L.append

    a("# TS-00-PREC — Banco de precisión emulado (fp8 e4m3/e5m2, bf16, f16, f32 frente a f64)")
    a("")
    a("Informe generado por `scripts/banco_precision.py` desde `resultados.json`; no se edita a mano. "
      "`--verificar DIR` regenera este texto desde el JSON y exige que coincida cifra por cifra.")
    a("")

    # ------------------------------------------------------------------ 1. evidencia
    a("## 1. Evidencia")
    a("")
    v = d["versiones"]
    a(f"- Perfil: `{d['perfil']}`. Semillas: {', '.join(str(s) for s in cfg['semillas'])} (n = {len(cfg['semillas'])}); "
      f"semilla de las entradas de evaluación (fijas, comunes a todas): {banco.SEMILLA_EVAL}.")
    t_pared = meta["tiempo_pared_s"]
    a(f"- Fecha UTC: {meta['fecha_utc']}. Tiempo de pared: {t_pared} s ({t_pared / 60:.1f} min; objetivo de la ficha ~{OBJETIVO_PARED_MIN} min con el banco completo: "
      + ("dentro del objetivo, tamaños del perfil sin reducir" if t_pared <= 60 * OBJETIVO_PARED_MIN else "por encima del objetivo, ver el compromiso de tamaños en la entrega")
      + "). La máquina es compartida: el tiempo de pared depende de la carga de otros procesos.")
    a(f"- Versiones: python {v['python']}, torch {v['torch']}, ml_dtypes {v['ml_dtypes']}, arch {v['arch']}, numpy {v['numpy']}, "
      f"scipy {v['scipy']}; motor quantdesk commit `{v['quantdesk_motor_commit']}` (paquete {v['quantdesk_paquete']}).")
    a(f"- Determinismo: `torch.manual_seed` por semilla, `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads({d['hilos']})` "
      f"(también `OMP/MKL/OPENBLAS_NUM_THREADS={d['hilos']}`); aleatoriedad de datos con `numpy.random.default_rng([semilla, flujo])`.")
    a(f"- SHA-256 canónico de `resultados.json` (JSON con claves ordenadas, floats a 10 cifras significativas, sin el bloque `meta`): "
      f"`{meta['sha256_canonico']}`. Los floats se canonizan a 10 cifras (una diferencia menor que eso no mueve el hash), pero los veredictos y los "
      "cocientes error/umbral forman parte del JSON hasheado, así que un cambio de veredicto siempre cambia el hash.")
    a(f"- Comando exacto para reproducir (dos ejecuciones con las mismas semillas deben dar el mismo hash): `{meta['comando']}`.")
    a("- Verificación: `.venv/Scripts/python -X utf8 scripts/banco_precision.py --verificar <DIR>`.")
    a("")

    # ------------------------------------------------------------------ 2. diseño
    a("## 2. Diseño (decisiones de diseño declaradas)")
    a("")
    a("### 2.1 Datos sintéticos con verdad conocida")
    a("")
    g, r = d["verdad"]["garch"], d["verdad"]["regimen"]
    a(f"- (a) GARCH(1,1) normal, r_t = sqrt(h_t) z_t, h_t = ω + α r²_(t-1) + β h_(t-1): ω = {g['omega']:g}, α = {g['alfa']:g}, "
      f"β = {g['beta']:g} (persistencia {g['alfa'] + g['beta']:g}, vol diaria incondicional 1 %). {cfg['n_garch']} puntos por semilla.")
    a(f"- (b) Cambio de régimen de 2 estados (cadena de Markov diaria; log-rendimiento = (μ_s − σ_s²/2)/252 + σ_s/√252 · z): "
      f"P = {r['P']}, μ anual = {r['mu']}, σ anual = {r['sigma']}. {cfg['n_reg']} puntos por semilla. Estado inicial de la distribución estacionaria.")
    a("- (c) Volatilidad estocástica («vol de la vol»): **no medida**, motivo en 3.1.")
    a("- Entrenamiento del transformer: por semilla, "
      f"{cfg['n_series_ent']} series de cada familia de {cfg['n_ent']} puntos (generadas con flujos de aleatoriedad distintos de los de recuperación y evaluación).")
    a(f"- Entradas de evaluación de las medidas 2 y 3: {cfg['n_eval']} ventanas fijas (mitad GARCH, mitad régimen), idénticas para las {len(cfg['semillas'])} semillas.")
    a("")
    a("### 2.2 Transformer y cono")
    a("")
    a(d["modelo"]["descripcion"])
    a("")
    a(f"Parámetros: {d['modelo']['n_parametros']}. Rejilla de α (J = {len(d['modelo']['alfas'])}): 0,005; 0,01; 0,025; 0,05; de 0,10 a 0,90 cada 0,025; "
      "0,95; 0,975; 0,99; 0,995. Salida en unidades del modelo (1 unidad = 1 % de log-rendimiento acumulado); "
      "el log-rendimiento físico es 0,01 × salida. Pérdida pinball media sobre α y h, AdamW "
      f"(lr {cfg['lr']:g}, coseno hasta el 5 %), lote {cfg['lote']}, {cfg['pasos']} pasos, f32 en CPU.")
    a("")
    filas = []
    ent = d["modelo"]["entrenamiento"]
    ctx = d["modelo"]["contexto_crps"]
    sens = d["m2"]["sensibilidad_vol"]
    for i, s in enumerate(cfg["semillas"]):
        filas.append([s, f"{ent[i]['perdida_inicial']:.4f}", f"{ent[i]['perdida_final']:.4f}",
                      fe(ctx["crps_f64"]["crps_garch"][i]), fe(ctx["crps_gauss_incondicional"]["crps_garch"][i]),
                      fe(ctx["crps_f64"]["crps_regimen"][i]), fe(ctx["crps_gauss_incondicional"]["crps_regimen"][i]),
                      fc(sens["corr_ancho_vol_f64"][i])])
    L += tabla(["Semilla", "Pinball medio, primeros pasos", "Pinball medio, últimos pasos", "CRPS GARCH modelo", "CRPS GARCH gauss. incond.",
                "CRPS régimen modelo", "CRPS régimen gauss. incond.", f"Corr. ancho del cono (h = {sens['horizonte_dias']}) con vol. de la ventana"], filas)
    a("Pinball medio: de los primeros y de los últimos pasos de entrenamiento (lotes ruidosos; el cono inicial ya es gaussiano de σ diaria 1 %). "
      "El cono gaussiano incondicional (σ = desviación típica de la propia serie) sólo da contexto: en estos procesos la predictibilidad del "
      "CRPS acumulado es pequeña, así que el listón es que el modelo no sea peor que él y que su cono responda a la volatilidad reciente "
      "(última columna: correlación, sobre las entradas de evaluación, del ancho q(0,995) − q(0,005) del cono f64 con la volatilidad realizada de la ventana).")
    a("")
    a("### 2.3 Redondeo")
    a("")
    a("Una sola función para todo el banco: `redondear(x, tipo)` = recorte a ±(máximo finito del tipo) y después ida y vuelta f64 → tipo → f64 con "
      "`ml_dtypes` (`float8_e4m3fn`, `float8_e5m2`, `bfloat16`, `float16`) o numpy (`float32`). El recorte emula fp8 con saturación y evita los NaN de "
      "desbordamiento de e4m3fn (máx. 448, sin infinitos). Variante «con escala»: se escala por una potencia de 2 (sin error de escalado) para que "
      "el máximo absoluto del tensor quepa en el máximo del tipo, se redondea y se desescala; se publica junto a «sin escala», nunca en su lugar. "
      "Las activaciones se escalan por muestra (eje 0 = una ventana), los pesos y la serie de entrada por tensor. "
      "Justificación: cada ventana es una inferencia, y la escala por tensor de una inferencia con lote 1 hace que el resultado no dependa de cómo se agrupe "
      "la evaluación (con una escala por lote, la precisión de una ventana cambiaría según con qué otras comparta lote); el selftest lo comprueba.")
    a("")
    a("| Tipo | Máx. finito | Bits de mantisa | Error relativo máx. teórico |")
    a("|---|---|---|---|")
    for t in TIPOS:
        p = d["tipos"][t]
        a(f"| {t} | {p['maximo_finito']:g} | {p['bits_mantisa']} | 2^-{p['bits_mantisa'] + 1} |")
    a("")
    a("Porcentaje de valores recortados y de valores no nulos que acaban en cero (suma sobre semillas):")
    a("")
    filas = []
    for c in ids:
        e1, e2 = d["m1"]["entrada"][c], d["m2"]["entrada"][c]
        filas.append([etiqueta(c), fp(e1["recortados_pct"]), fp(e1["no_nulos_a_cero_pct"]), fp(e2["recortados_pct"]), fp(e2["no_nulos_a_cero_pct"])])
    L += tabla(["Celda", "Medida 1 recortados %", "Medida 1 a cero %", "Medida 2 recortados %", "Medida 2 a cero %"], filas)
    a("")
    a("### 2.4 Definición de la dispersión entre semillas (umbral)")
    a("")
    a(f"n = {len(cfg['semillas'])} semillas; cada semilla cambia los datos sintéticos, la inicialización y el orden del entrenamiento. "
      "Dispersión = desviación típica muestral (ddof = 1) entre semillas.")
    a("")
    a("- Medida 1: métrica m (error de recuperación, CRPS) por tipo T y semilla s. Umbral = max(sd_s(m_T), sd_s(m_f64)). Pierde si |media_s(m_T) − media_s(m_f64)| > umbral.")
    a("- Medidas 2 y 3: magnitud x (cada grupo de cuantiles, diferencias contiguas, σ_loc) sobre el conjunto fijo de entradas de evaluación. "
      "Umbral = RMS sobre entradas (y horizontes, α, K) de la desviación típica entre los modelos f64 de las semillas. Error del tipo T = mediana sobre semillas "
      "del RMS de (x_T − x_f64) en el mismo modelo. Pierde si error > umbral.")
    a("- Se publica también el cociente error / umbral.")
    a("")
    a("### 2.5 Procedimiento de la medida 3 (Dupire, fijo)")
    a("")
    m3 = d["m3"]
    a(f"S0 = 1, tipos cero, h = días/252; S_h(α) = exp(q(α, h)) con recentrado multiplicativo para que la media discreta Σ w_j S_j sea 1 "
      f"(forward = S0; los factores se publican en 3.3). C(K, h) = Σ_j w_j (S_j − K)⁺ con pesos trapezoidales en α y la masa de las colas asignada al cuantil extremo "
      f"(error declarado: no se extrapola fuera de [0,005; 0,995]). Rejilla de K: {m3['nk']} puntos equiespaciados en [máx S_h(0,10), mín S_h(0,90)], donde el máximo y el mínimo se "
      f"toman, por entrada de evaluación y trío de horizontes k−1, k, k+1, sobre los {len(cfg['semillas'])} modelos f64 (intersección de sus intervalos [S_h(0,10), S_h(0,90)]): "
      f"todo K cae dentro del intervalo de cada modelo f64 a los tres horizontes, y la rejilla es común a todos los modelos y tipos, que es lo que permite compararlos. "
      f"Si la intersección es vacía o su ancho es menor que {m3['rejilla_k']['ancho_min']:g} (S0 = 1), ese trío no tiene rejilla y sus puntos cuentan como fuera de región (se publican en 3.3, nunca se rellenan). "
      f"∂C/∂h por diferencias centradas entre k−1 y k+1; ∂²C/∂K² por diferencias centradas en K; "
      f"σ_loc² = 2 ∂C/∂h / (K² ∂²C/∂K²) sólo donde ∂²C/∂K² > {m3['dens_min']:g} y ∂C/∂h > 0 (región válida; los puntos fuera se cuentan, no se rellenan). "
      f"σ_loc se evalúa en los {m3['nk'] - 2} K interiores y en los horizontes de {m3['horizontes_dias'][0]} a {m3['horizontes_dias'][-1]} días. "
      f"El error se calcula sobre los puntos válidos en los {len(cfg['semillas'])} modelos f64 y en el tipo; la cobertura (fracción de esos puntos que el tipo conserva) "
      f"se publica y, si baja de {100 * m3['cobertura_min']:.0f} %, el tipo pierde aunque el RMS de los puntos que quedan sea pequeño.")
    a("")

    # ------------------------------------------------------------------ 3. resultados
    a("## 3. Resultados por medida (valor, umbral, veredicto)")
    a("")
    a("### 3.1 Medida 1 — entrada")
    a("")
    a("Se redondean sólo los log-rendimientos de entrada (unidades físicas, ~1e-2; la serie entera es el tensor de la variante «con escala»); "
      "el transformer f32 entrenado **no se reentrena**: se evalúa sobre las series sin redondear con las entradas redondeadas. "
      "«Media» es la media entre semillas de la métrica con ese tipo; «Dif.» es |media_T − media_f64|.")
    a("")
    a("- GARCH: `arch` (normal, media cero) sobre 100·r; persistencia α+β y ω (reescalado a unidades de r).")
    a("- Régimen: HMM de 2 estados `GBM_P` del motor quantdesk (`Engine.calibrate`, `HmmCalibrationOptions(seed=7)`) sobre niveles S0·exp(cumsum(r redondeado)) "
      "con S0 = 100 y tiempos i/252; estados ordenados por σ estimada creciente; probabilidad de régimen = posterior suavizada (`gamma_by_step`), "
      "medida con el Brier frente al estado verdadero de cada día.")
    a(f"- CRPS aproximado por cuantiles: 2 Σ_j w_j pinball_α_j(y − q_j) con los pesos trapezoidales de la rejilla de α (colas al cuantil extremo), "
      f"media sobre ventanas (una cada {cfg['paso_crps']} días: GARCH {cfg['n_garch']} puntos, régimen {cfg['n_reg']}) y horizontes h = 1..{cfg['H']}; "
      "el objetivo es el log-rendimiento acumulado realizado sin redondear.")
    a("")
    for mid, desc, unidad in METRICAS_M1:
        mm = d["m1"]["metricas"][mid]
        a(f"**{mid}** — {desc} (unidad: {unidad}). Referencia f64: media {fe(mm['celdas']['f64']['media'])}, sd {fe(mm['celdas']['f64']['sd'])}.")
        a("")
        filas = []
        for c in ids:
            x = mm["celdas"][c]
            filas.append([etiqueta(c), fe(x.get("media")), fe(x.get("dif")), fe(x.get("umbral")), fc(x.get("cociente")), x["veredicto"]])
        L += tabla(["Celda", "Media", "Dif.", "Umbral", "Cociente", "Veredicto"], filas)
    for mid, nm in d["m1"]["no_medidas"].items():
        a(f"**{mid}** — {nm['descripcion']}: veredicto **{nm['veredicto']}**. {nm['motivo']}")
        a("")
    nc = {c: n for c, n in d["m1"]["no_convergen"].items() if n}
    fl = {c: f for c, f in d["m1"]["fallos"].items() if f}
    a("Ajustes que no convergieron (optimizador de arch o del motor), por celda: "
      + (", ".join(f"{etiqueta(c)}: {n}" for c, n in nc.items()) if nc else "ninguno") + ".")
    a("")
    a("Ajustes fallidos (la métrica correspondiente queda «no medida»): "
      + ("; ".join(f"{etiqueta(c)}: {len(f)} ({f[0]})" for c, f in fl.items()) if fl else "ninguno") + ".")
    a("")

    a("### 3.2 Medida 2 — inferencia")
    a("")
    a("El mismo modelo (pesos entrenados) con pesos (todos los parámetros) y activaciones redondeados al tipo en cada frontera de capa, frente a la referencia del "
      "mismo modelo en f64. La entrada del modelo es el rendimiento ya dividido por 0,01 (la medida 1 ya cubre el redondeo del rendimiento físico); la salida se mide "
      "en log-rendimiento físico (0,01 × salida del modelo, sin redondeo posterior). Error = mediana entre semillas del RMS sobre las entradas de evaluación.")
    a("")
    for gid, desc in CANTIDADES_M2:
        q = d["m2"]["cantidades"][gid]
        a(f"**{gid}** — {desc}. Umbral (ruido de semilla del modelo f64): {fe(q['umbral'])}.")
        a("")
        filas = [[etiqueta(c), fe(q["celdas"][c]["error"]), fe(q["umbral"]), fc(q["celdas"][c]["cociente"]), q["celdas"][c]["veredicto"]] for c in ids]
        L += tabla(["Celda", "Error", "Umbral", "Cociente", "Veredicto"], filas)
    a("**Diferencias contiguas que se anulan o cambian de signo** (porcentaje sobre todas las diferencias q(α_j+1, h) − q(α_j, h); media entre semillas):")
    a("")
    filas = [[etiqueta(c), fp(d["m2"]["diferencias_contiguas"][c]["se_anulan_pct"]), fp(d["m2"]["diferencias_contiguas"][c]["cambian_signo_pct"])] for c in ids]
    L += tabla(["Celda", "Se anulan %", "Cambian de signo %"], filas)
    a("**Error relativo por capa** (norma, ‖x_T − x_f64‖ / ‖x_f64‖ sobre las entradas de evaluación; mediana entre semillas; "
      "sin umbral entre semillas porque las activaciones internas de modelos distintos no comparten base, así que sólo se publican):")
    a("")
    filas = []
    for capa in d["m2"]["capas"]:
        filas.append([capa] + [fe(d["m2"]["error_capa"][c][capa], 1) for c in ids])
    L += tabla(["Capa"] + [etiqueta(c) for c in ids], filas)

    a("### 3.3 Medida 3 — derivados de la salida")
    a("")
    a(f"σ_loc (H1) por Dupire desde el cono de cada tipo (el de la medida 2). Puntos de la rejilla: {m3['puntos_rejilla']}; válidos en los modelos f64: "
      f"{fp(m3['puntos_validos_f64_pct'])} % (por modelo: {', '.join(fp(x) for x in m3['puntos_validos_por_modelo_f64_pct'])} %); "
      f"σ_loc f64 mediana {fe(m3['sigma_loc_f64_mediana'])}; factor de recentrado f64: mediana {m3['factor_recentrado_f64']['mediana']:.6f}, "
      f"mín {m3['factor_recentrado_f64']['min']:.6f}, máx {m3['factor_recentrado_f64']['max']:.6f}. Umbral (ruido de semilla de σ_loc f64): {fe(m3['umbral'])}.")
    a("")
    rk = m3["rejilla_k"]
    a(f"Rejilla de K común (intersección de los intervalos de los {len(cfg['semillas'])} modelos f64): {rk['trios']} tríos (entrada, k), de los que "
      f"{rk['trios_interseccion_vacia']} tienen intersección vacía y {rk['trios_interseccion_degenerada']} degenerada (ancho < {rk['ancho_min']:g}); sus puntos cuentan como fuera de región, "
      f"no se rellenan. Comprobación: K fuera del intervalo de algún modelo f64: {rk['k_fuera_intervalo_f64_n']} de {rk['k_total']} K por modelo "
      "(por construcción 0; el banco aborta si no lo es). Dato informativo: la columna «K fuera del intervalo propio» da el porcentaje de K (suma sobre semillas) "
      "que queda fuera de [máx S_h(0,10), mín S_h(0,90)] del propio cono redondeado del tipo (mismos tres horizontes), es decir, cuánto de la rejilla común cae fuera de la región "
      "interior que ese cono declara; no cambia el veredicto. El valor de f32 (≈ 2 %) es el suelo de esta cuenta: los dos K extremos de la rejilla coinciden con el borde "
      "del f64 que define la intersección y el redondeo de un tipo casi exacto los deja fuera, por una diferencia ínfima, en una parte de esos casos; lo informativo es el exceso sobre f32.")
    a("")
    filas = []
    for c in ids:
        x = m3["celdas"][c]
        filas.append([etiqueta(c), fe(x["error"]), fe(x["umbral"]), fc(x["cociente"]), fp(100 * x["cobertura"]),
                      fp(x["k_fuera_intervalo_propio_pct"]),
                      f"{x['factor_recentrado_rel_mediana']:.6f}", fe(x["factor_recentrado_rel_max_dev"]),
                      x["veredicto"] + (f" ({x['motivo']})" if x.get("motivo") else "")])
    L += tabla(["Celda", "Error σ_loc", "Umbral", "Cociente", "Cobertura %", "K fuera del intervalo propio %", "Factor recentrado T/f64 (mediana)", "Factor T/f64 máx. desviación absoluta", "Veredicto"], filas)
    a(f"**Delta por AAD** según el tipo del cono: {m3['delta_aad']['motivo']}.")
    a("")

    # ------------------------------------------------------------------ 4. tabla final
    a("## 4. Tabla final tipo × medida")
    a("")
    a("Por celda y medida: número de métricas que pierden entre las medidas, la de peor cociente (valor, umbral) y el veredicto global "
      "(pierde si alguna métrica medida pierde; «no medida» si ninguna se pudo medir).")
    a("")
    por_celda = {c: filas_celda(d, c) for c in ids}
    resumen_celda: dict = {}
    for medida, nombre in (("M1", "Medida 1 (entrada)"), ("M2", "Medida 2 (inferencia)"), ("M3", "Medida 3 (σ_loc)")):
        a(f"**{nombre}**")
        a("")
        filas = []
        for c in ids:
            f = por_celda[c][medida]
            veredicto, n_p, n_m, n_nm = resumen([x for _, x in f])
            resumen_celda[(c, medida)] = (veredicto, n_p, n_m, n_nm, [n for n, x in f if x["veredicto"] == "pierde"])
            med = [(n, x) for n, x in f if x["veredicto"] in ("pierde", "no pierde")]
            if med:
                n_w, x_w = max(med, key=lambda t: _cociente_orden(t[1]))
                peor = f"{n_w}: valor {fe(x_w['valor'])}, umbral {fe(x_w['umbral'])}, cociente {fc(x_w['cociente'])}"
            else:
                peor = "n/m"
            filas.append([etiqueta(c), f"{n_p}/{n_m}" + (f" (+{n_nm} no medidas)" if n_nm else ""), peor, veredicto])
        L += tabla(["Celda", "Pierden / medidas", "Peor métrica", "Veredicto"], filas)
    a("**Delta por AAD**: no medida: requiere AAD (engine-nn).")
    a("")

    # ------------------------------------------------------------------ 5. ¿basta fp8?
    a("## 5. ¿Basta fp8?")
    a("")
    a("Primera respuesta, mecánica (reglas de 2.4 aplicadas a las cifras de arriba), por medida y por variante. «Basta» = ninguna métrica medida pierde; "
      "no es una afirmación sobre el entrenamiento ni sobre hardware real (ver 6).")
    a("")
    fp8 = [c for c in ids if c.startswith("e4m3") or c.startswith("e5m2")]
    filas = []
    for c in fp8:
        fila = [etiqueta(c)]
        for medida in ("M1", "M2", "M3"):
            veredicto, n_p, n_m, _, perdidas = resumen_celda[(c, medida)]
            fila.append("basta" if veredicto == "no pierde" else ("no basta" if veredicto == "pierde" else "no medida"))
        fila.append("no medida (requiere AAD)")
        filas.append(fila)
    L += tabla(["Celda fp8", "Medida 1 (entrada)", "Medida 2 (inferencia)", "Medida 3 (σ_loc)", "Delta por AAD"], filas)
    for medida, nombre in (("M1", "Medida 1 (entrada)"), ("M2", "Medida 2 (inferencia)"), ("M3", "Medida 3 (σ_loc)")):
        a(f"- **{nombre}**")
        for var, vtxt in (("sin", "sin escala"), ("con", "con escala")):
            partes = []
            for t in ("e4m3", "e5m2"):
                veredicto, n_p, n_m, _, perdidas = resumen_celda[(f"{t}:{var}", medida)]
                txt = "no pierde en ninguna métrica medida" if veredicto == "no pierde" else (
                    f"pierde en {n_p} de {n_m} ({', '.join(perdidas)})" if veredicto == "pierde" else "no medida")
                partes.append(f"{t}: {txt}")
            e4, e5 = resumen_celda[(f"e4m3:{var}", medida)], resumen_celda[(f"e5m2:{var}", medida)]
            cmp_ = "e4m3 y e5m2 pierden igual número de métricas" if e4[1] == e5[1] else (
                "e5m2 pierde menos métricas que e4m3" if e5[1] < e4[1] else "e4m3 pierde menos métricas que e5m2")
            a(f"  - {vtxt}: " + "; ".join(partes) + f". Comparación: {cmp_}.")
    a("")
    a("**Respuesta corta** (por celda fp8; la delta por AAD queda sin medir hasta `engine-nn`):")
    a("")
    total = {}
    for c in fp8:
        bastan = [m for m in ("M1", "M2", "M3") if resumen_celda[(c, m)][0] == "no pierde"]
        no_bastan = [(m, resumen_celda[(c, m)][4]) for m in ("M1", "M2", "M3") if resumen_celda[(c, m)][0] == "pierde"]
        total[c] = sum(len(p) for _, p in no_bastan)
        txt = f"- {etiqueta(c)}: basta en {', '.join(bastan) if bastan else 'ninguna medida'}"
        if no_bastan:
            txt += "; no basta en " + "; ".join(f"{m} ({', '.join(p)})" for m, p in no_bastan)
        a(txt + ".")
    a("")
    for var, vtxt in (("sin", "sin escala"), ("con", "con escala")):
        n4, n5 = total[f"e4m3:{var}"], total[f"e5m2:{var}"]
        quien = "empatan" if n4 == n5 else ("e5m2 pierde menos métricas que e4m3" if n5 < n4 else "e4m3 pierde menos métricas que e5m2")
        a(f"- e4m3 frente a e5m2 {vtxt}: e4m3 pierde en {n4} métricas y e5m2 en {n5} (suma de las tres medidas): {quien}.")
    a("")
    a("Salvedades: (1) emulación en CPU, no hardware fp8: la acumulación interna del producto matricial sigue en f64 y el hardware real acumula en f32/bf16 con sus "
      "propios redondeos; (2) los modelos son pequeños y las series sintéticas, sin colas gruesas ni microestructura; (3) con n = 5 semillas la desviación típica "
      "muestral es ella misma ruidosa, así que un cociente cercano a 1 es indeciso; (4) la medida 1 no reentrena, por lo que mide sólo desajuste de entrada, "
      "no lo que ganaría un modelo entrenado con esa entrada (medidas 4–5, TS-05-PREC); (5) la medida 2 redondea todos los tensores entre operaciones "
      "(más severo que una receta mixta con softmax, LayerNorm y acumuladores en mayor precisión); (6) σ_loc depende de la discretización de α (J = 41) y de K "
      f"(nK = {m3['nk']}) y no extrapola colas; (7) la variante con escala usa potencias de 2 y máximos por tensor (por muestra en activaciones), "
      "no la calibración por canal ni la escala diferida de las recetas de hardware.")
    a("")

    # ------------------------------------------------------------------ 6. limitaciones
    a("## 6. Limitaciones de la emulación y alcance")
    a("")
    a("- La emulación redondea con `ml_dtypes` (f64 → tipo → f64) en cada frontera de capa; la acumulación interna sigue en f64. TS-05-PREC lo corrige en hardware real.")
    a("- `ml_dtypes` 0.6.0 convierte f64 → fp8/bf16 pasando por f32: un valor a menos de 2^-24 (relativo) de un empate se redondea como si estuviera en él "
      "(doble redondeo). Afecta a ~1e-6 de los valores y no mueve el error relativo máximo por encima de u·(1 + 2^-23).")
    a("- Fuera de alcance: medidas 4–5 (entrenamiento por tipo, mezclas), GPU, hardware fp8 real, AAD. La vol de la vol no se mide (3.1).")
    a("- Sin red, sin dependencias nuevas; salidas bajo `E:/quantdesk-lab/runs/TS-00-PREC/`.")
    a("")
    return "\n".join(L)


def escribir_informe(directorio: str) -> str:
    doc = banco.leer_resultados(directorio)
    texto = generar_informe(doc)
    ruta = os.path.join(directorio, "informe.md")
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    return ruta


def _cifras_tabla(texto: str) -> list:
    out = []
    for linea in texto.splitlines():
        if linea.startswith("|"):
            out += re.findall(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", linea)
    return out


def verificar(directorio: str) -> int:
    problemas = []
    try:
        doc = banco.leer_resultados(directorio)
    except Exception as exc:  # noqa: BLE001
        print(f"verificar: no se pudo leer resultados.json en {directorio}: {exc}")
        return 1
    h = banco.hash_canonico(doc["datos"])
    side = os.path.join(directorio, "resultados.json.sha256")
    if not os.path.isfile(side):
        problemas.append("falta resultados.json.sha256")
    else:
        with open(side, encoding="utf-8") as f:
            h_side = f.read().split()[0]
        if h_side != h:
            problemas.append(f"hash canonico recalculado {h} != resultados.json.sha256 {h_side}")
    if doc["meta"].get("sha256_canonico") != h:
        problemas.append("meta.sha256_canonico no coincide con el hash canonico recalculado")
    esperado = generar_informe(doc)
    ruta = os.path.join(directorio, "informe.md")
    n_cifras = 0
    if not os.path.isfile(ruta):
        problemas.append("falta informe.md")
    else:
        with open(ruta, encoding="utf-8") as f:
            actual = f.read()
        if actual != esperado:
            la, le = actual.splitlines(), esperado.splitlines()
            for i in range(max(len(la), len(le))):
                x = la[i] if i < len(la) else "(fin)"
                y = le[i] if i < len(le) else "(fin)"
                if x != y:
                    problemas.append(f"informe.md difiere del regenerado desde el JSON en la linea {i + 1}:\n  informe : {x[:200]}\n  esperado: {y[:200]}")
                    break
        n_cifras = len(_cifras_tabla(actual))
        if "## 5. ¿Basta fp8?" not in actual or "## 4. Tabla final tipo × medida" not in actual:
            problemas.append("el informe no contiene la tabla final o la seccion '¿Basta fp8?'")
    if problemas:
        print("verificar: FALLO")
        for p in problemas:
            print("  - " + p)
        return 1
    print(f"verificar: OK; sha256 canonico {h}; informe.md coincide con el regenerado desde el JSON ({n_cifras} cifras en tablas comprobadas)")
    return 0
