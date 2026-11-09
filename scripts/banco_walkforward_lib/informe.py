"""informe.md y metricas.csv a partir de las corridas (meta.json, metricas.csv, predicciones.parquet de cada una)."""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone

from . import banco, datos, modelos, rutas

CABECERA = "lago_cierre_c20261101"  # decision del usuario 2026-11-09, transmitida por la raiz

LICENCIAS = [
    ("Chronos-2 (pesos `amazon/chronos-2`)", "Apache-2.0", "https://huggingface.co/amazon/chronos-2",
     "permite uso de investigacion interno; usado"),
    ("chronos-forecasting 2.3.2 (codigo)", "Apache-2.0", "https://github.com/amazon-science/chronos-forecasting",
     "instalado en LAB-00-ENV"),
    ("Toto (pesos `Datadog/Toto-Open-Base-1.0`)", "Apache-2.0", "https://huggingface.co/Datadog/Toto-Open-Base-1.0",
     "permite uso de investigacion interno; NO usado (paquete no instalado)"),
    ("toto-ts 0.2.0 (codigo)", "Apache-2.0", "https://pypi.org/project/toto-ts/", "no instalado"),
    ("arch 8.0.0 (GARCH)", "NCSA", "https://github.com/bashtage/arch", "sin pesos"),
    ("HMM del motor (quantdesk 69fdb39d)", "propio", "S:/Projects/quantdesk", "sin pesos"),
]

TOTO = """**Pendiente de decision (GAP-04).** No esta en el `.venv` y no se ha instalado nada.

- Paquete: `toto-ts` 0.2.0 (PyPI, 2026-02-26, Apache-2.0); pesos `Datadog/Toto-Open-Base-1.0` (Apache-2.0,
  ~151 M parametros, `model.safetensors` de 605 MB). Licencias verificadas en
  https://pypi.org/project/toto-ts/ y https://huggingface.co/Datadog/Toto-Open-Base-1.0 el 2026-11-09.
- Conflicto: `toto-ts` 0.2.0 fija versiones exactas incompatibles con el `.venv` del laboratorio (`torch==2.7.0`
  frente a 2.15.0+cpu, `numpy==1.26.4` frente a 2.5.4, `pandas==2.2.3` frente a 3.1.1, `transformers==4.52.1`
  frente a 5.22.2, `einops==0.7.0`, `gluonts[torch]==0.16.2`, mas herramientas de desarrollo como dependencias
  de ejecucion: pytest, mypy, black, jupyter, tensorboard, lightning, boto3). Instalarlo en el `.venv` lo
  degradaria y romperia Chronos-2 y la rueda del motor.
- Orden propuesta (un venv aparte bajo E:, sin tocar el del laboratorio; CPU):
  `D:/miniconda312/python.exe -m venv E:/quantdesk-lab/venvs/toto` y despues
  `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.0`
  seguido de `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install toto-ts==0.2.0 pyarrow`
  (con `PIP_CACHE_DIR`, `HF_HOME` y `TMPDIR` del laboratorio). El banco llamaria a ese interprete en un
  subproceso con el mismo contrato de cuantiles (contexto en log-precio, 256 muestras, cuantiles empiricos).
- CPU: la tarjeta solo documenta CUDA (recomienda xFormers y flash-attention, opcionales). Por tamano (~151 M,
  como Chronos-2 ~120 M) cabe en CPU y 32 GB de RAM; el coste esperado es mayor que el de Chronos-2 porque
  muestrea (256 caminos por origen frente a una pasada de cuantiles). Sin medir.
- Sin instalar: el repositorio de pesos no trae codigo de modelado (solo `config.json` y `model.safetensors`); el
  modelo esta en el paquete `toto` (`toto.model.toto.Toto`, `toto.inference.forecaster.TotoForecaster`). No hay
  forma de ejecutarlo solo con `transformers`/`torch` sin copiar ese codigo, asi que no se ha intentado."""


def _f(x, nd=4):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return str(x)
    return f"{x:.{nd}g}"


def _p(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:.3f}"


def _cargar(run):
    import pandas as pd

    with open(os.path.join(run, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    met = pd.read_csv(os.path.join(run, "metricas.csv"))
    return meta, met


def _etiqueta(meta):
    ds = meta["dataset"]["dataset_id"]
    return f"{ds} (proxy)" if meta["dataset"]["proxy"] else ds


def _resumen(met, modelos_):
    import numpy as np

    filas = []
    for h in banco.HORIZONTES:
        g = met[met["h"] == h]
        piv = g.pivot(index="instrument", columns="modelo", values="crps")
        pq = g.pivot(index="instrument", columns="modelo", values="qlike")
        gana = piv.idxmin(axis=1).value_counts()
        gana_q = pq.idxmin(axis=1).value_counts()
        for m in modelos_:
            gm = g[g["modelo"] == m]
            rel = (piv[m] / piv["garch"]).median() if "garch" in piv else float("nan")
            filas.append({
                "h": h, "modelo": m, "activos": len(gm),
                "crps": gm["crps"].median(), "crps_rel": rel,
                "p01": gm["pinball_01"].median(), "p99": gm["pinball_99"].median(),
                "exc01": gm["exc_01"].median(), "exc99": gm["exc_99"].median(),
                "ku01": int((gm["kupiec_01_p"] < 0.05).sum()), "ku99": int((gm["kupiec_99_p"] < 0.05).sum()),
                "ch01": int((gm["christ_01_p"] < 0.05).sum()), "ch99": int((gm["christ_99_p"] < 0.05).sum()),
                "qlike": gm["qlike"].median(), "gana": int(gana.get(m, 0)), "gana_q": int(gana_q.get(m, 0)),
            })
    return filas


def escribir(runs, repeticion, destino, pilotos=None) -> int:
    import pandas as pd

    cargados = [(_cargar(r), r) for r in runs]
    cargados.sort(key=lambda x: (x[0][0]["dataset"]["dataset_id"] != CABECERA, x[0][0]["dataset"]["dataset_id"]))
    L = []
    w = L.append
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    w("# TS-00-BENCH: banco walk-forward (HMM del motor, GARCH(1,1), Chronos-2 zero-shot; Toto pendiente)")
    w("")
    w(f"- Generado por `scripts/banco_walkforward.py --informe` el {ahora} a partir de las salidas de las corridas "
      "(`meta.json`, `metricas.csv`, `predicciones.parquet` en `E:/quantdesk-lab/runs/TS-00-BENCH/`). Comando: "
      "`.venv/Scripts/python -X utf8 scripts/banco_walkforward.py "
      + " ".join(sys.argv[1:]).replace(os.sep, "/").replace(rutas.REPO.replace(os.sep, "/") + "/", "") + "`.")
    w("- Selftest: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --selftest` (sin red: el selftest "
      "bloquea los sockets; sin datos reales; Chronos-2 sustituido por un modelo trivial con la misma interfaz).")
    w(f"- Motor: **{banco.MOTOR}** (commit `{banco.MOTOR_COMMIT}`). Semilla: **{banco.SEMILLA}**. Solo CPU.")
    w(f"- **Tabla de cabecera: `{CABECERA}`** (FX diario del lago; decision del usuario del 2026-11-09). Su "
      "disponibilidad es un **proxy** (`available_at_ms` nulo, `default_lag_ms` = 0: valores que qn recibio "
      "despues del corte) y cada tabla y cifra suya lleva la etiqueta «proxy». `binance_c20261101` es la segunda tabla.")
    w("- No se fijan umbrales de exito (TS-00-OBJ). Las cifras son descriptivas.")
    w("")
    w("## Resumen por modelo")
    w("")
    w("Medianas entre activos de cada metrica; «CRPS rel.» es la mediana del cociente CRPS del modelo / CRPS de "
      "GARCH en el mismo activo (< 1 mejor que GARCH). «Gana» cuenta los activos en que el modelo tiene el menor "
      "CRPS (y el menor QLIKE). «Kupiec/Chr. p<0,05» cuenta activos en que el test rechaza al 5 %. Excedencias "
      "esperadas: 1 % en cada cola.")
    for (meta, met), run in cargados:
        mods = meta["config"]["modelos"]
        w("")
        w(f"### {_etiqueta(meta)}" + (" — tabla de cabecera" if meta["dataset"]["dataset_id"] == CABECERA else ""))
        w("")
        w("| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % "
          "| Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in _resumen(met, mods):
            w(f"| {r['h']} | {r['modelo']} | {r['activos']} | {_f(r['crps'])} | {_f(r['crps_rel'], 3)} | "
              f"{_f(r['p01'])} | {_f(r['p99'])} | {_f(r['exc01'], 3)} | {_f(r['exc99'], 3)} | {r['ku01']}/{r['ku99']} | "
              f"{r['ch01']}/{r['ch99']} | {_f(r['qlike'])} | {r['gana']} | {r['gana_q']} |")
    w("")
    w("## Diseno del walk-forward")
    w("")
    w("| dataset | tabla | `dataset_hash` | ventana W (barras) | rejilla de origenes | horizontes (barras) | activos | "
      "pares activo-origen evaluados | omitidos (sin W barras / sin objetivo / sin barra nueva) |")
    w("|---|---|---|---|---|---|---|---|---|")
    for (meta, met), run in cargados:
        c, d = meta["config"], meta["dataset"]
        ev = sum(v["evaluados"] for v in meta["omitidos"].values())
        sv = sum(v["sin_ventana"] for v in meta["omitidos"].values())
        so = sum(v["sin_objetivo"] for v in meta["omitidos"].values())
        sb = sum(v["sin_barra_nueva"] for v in meta["omitidos"].values())
        w(f"| {_etiqueta(meta)} | `{d['tabla']}` | `{d['dataset_hash']}` | {c['ventana']} | 00:00 UTC de "
          f"{c['inicio']} a {c['fin']}, cada {c['paso_dias']} d ({c['n_rejilla']} instantes) | "
          f"{', '.join(map(str, c['horizontes']))} | {len(c['activos'])} | {ev} | {sv} / {so} / {sb} |")
    w("")
    w("- Unidad de tiempo: la barra diaria (observacion). h = 1, 5 y 20 barras: en cripto (24/7) son dias "
      "naturales; en FX, sesiones (h = 5 es una semana de mercado). Las barras de 1 h no se usan: en el lago solo "
      "hay desde 2026-10-18 (demasiado corto) y en Binance quedan para una fase posterior.")
    w("- Objetivo: rendimiento logaritmico acumulado y = ln(C_{k+h} / C_k), con k la ultima barra visible en el "
      "origen y C el cierre. Cada modelo da los 21 cuantiles de y (niveles de Chronos-2: 0,01, 0,05, 0,10, ..., "
      "0,95, 0,99).")
    w("- Origenes: la rejilla fija de la tabla (00:00 UTC). En cada origen y activo se omite el par si no hay W "
      "barras visibles, si no existen las 20 barras siguientes (objetivo) o si desde el origen anterior no ha "
      "llegado ninguna barra nueva (fines de semana del FX: repetiria la misma informacion). La ventana es movil: "
      "los modelos se recalibran en cada origen con las ultimas W barras visibles.")
    w("- Comparacion justa: las metricas de cada activo y horizonte se calculan solo sobre los origenes en que los "
      "tres modelos dieron prevision; los fallos se cuentan en la seccion de reproducibilidad.")
    w("- Tests de VaR: con origenes mas juntos que h las ventanas se solapan y las excedencias no son "
      "independientes; por eso Kupiec y Christoffersen se calculan sobre la submuestra sin solape (un origen se "
      "conserva si su barra k esta al menos h barras despues de la del ultimo conservado; columna `n_test`). Las "
      "tasas de excedencia y el resto de metricas usan todos los origenes. Con h = 20 la submuestra es pequena "
      "(del orden de 12 a 50 por activo) y los tests tienen poca potencia.")
    w("")
    w("### Garantia de no look-ahead")
    w("")
    w("- Disponibilidad de cada fila = `available_at_ms` si no es nulo; si lo es, `ts_ms + interval_ms + "
      "default_lag_ms` del manifest (el mecanismo del motor). Binance: cierre declarado por la fuente en cada fila. "
      "Lago (proxy): `available_at_ms` nulo y `default_lag_ms` = 0, es decir, el cierre de la barra. Una fila sin "
      "ninguna de las dos hace fallar la carga.")
    w("- En el origen t, `datos.cortar` selecciona las filas con disponibilidad <= t, las ordena por `ts_ms` y pasa "
      "al modelo una copia de solo lectura de los ultimos W cierres; el modelo no recibe el DataFrame, ni indices, "
      "ni el objetivo. El objetivo y la varianza realizada se calculan aparte con las barras de `ts_ms` posterior a "
      "la ultima visible. Un dato tardio (ts anterior pero publicado despues de t) queda fuera del contexto.")
    w("- Selftest (`--selftest`): una barra con `ts` anterior al origen pero publicada despues, multiplicada por "
      "1000, no entra en el contexto y no cambia ni un bit las predicciones de HMM, GARCH y el sustituto de "
      "Chronos-2; con `available_at_ms` nulo, `default_lag_ms` 0 hace visible la barra que cierra en el origen y "
      "1 ms la deja fuera; sin ninguno de los dos la carga falla.")
    w("- Limite del proxy: en `lago_cierre_c20261101` los valores son la version que qn recibio despues del corte "
      "(ver el informe de TI-02-DATA), asi que el dataset no es causal en sentido estricto aunque el corte por "
      "disponibilidad lo sea.")
    w("")
    w("### Modelos")
    w("")
    w(f"- **hmm**: HMM del motor por los bindings Python: plantilla de K = {modelos.K_HMM} estados `GbmP` (el menor "
      "de los K candidatos {3, 4} del HMM de FX del motor; sin seleccion por BIC en el univariante), Baum-Welch con "
      "`HmmCalibrationOptions` por defecto (200 iteraciones, 5 reinicios, `init_mode` quantile_volatility) salvo "
      "`seed`, sobre los precios con malla de observaciones (dt = 1/252 por barra). "
      f"{modelos.S_CAMINOS} caminos condicionados al final de la calibracion con "
      "`Engine.open_stream(res, semilla_j, policy=\"from_calibration_end\").advance_many([dt] * 20)`, un camino "
      "por stream; se comprueba que s0 de la calibracion es el ultimo precio del contexto.")
    w(f"- **garch**: `arch` GARCH(1,1), media constante, innovaciones t de Student, sobre 100 x rendimientos log de la "
      f"ventana; {modelos.S_CAMINOS} caminos simulados a 20 pasos con una t estandarizada sembrada "
      "(`rng=`; `arch` 8 ignora `random_state` en la simulacion, lo detecto el selftest).")
    w(f"- **chronos2**: `{modelos.CHRONOS_ID}` revision `{modelos.CHRONOS_REV}`, zero-shot, CPU, float32, "
      "`predict_quantiles` sobre el log-precio de la ventana (W barras), 20 pasos, cuantiles nativos menos el "
      "ultimo log-precio. Lote de una serie por llamada: con lotes mayores las salidas cambian en ~1e-6 segun la "
      "composicion del lote (medido), y con lote 1 un subconjunto reproduce bit a bit la corrida completa. "
      "`torch.use_deterministic_algorithms(True)`; dos llamadas iguales dan el mismo resultado (medido).")
    w("- Cuantiles de los modelos por muestras: `numpy.quantile` (lineal) de las muestras en los 21 niveles.")
    w("")
    w("### Metricas y estimador de vol realizada")
    w("")
    w("- CRPS **por cuantiles**: CRPS_q = (2/21) x suma de pinball en los 21 niveles (misma regla para los tres "
      "modelos; aproxima 2 x integral del pinball con una rejilla no uniforme que pesa algo mas las colas).")
    w("- pinball_a(y, q) = (1{y < q} - a)(q - y) en a = 0,01 y 0,99.")
    w("- VaR 1 %: excedencia si y < q_0,01; VaR 99 %: si y > q_0,99. Kupiec (POF) y Christoffersen "
      "(independencia, cadena de Markov de orden 1), p-valores con chi2(1). Sin excedencias, o sin transicion "
      "desde una excedencia, el test de Christoffersen no esta definido («—»).")
    w("- Vol realizada: RV_h = suma de los h rendimientos log diarios (cierre a cierre) al cuadrado posteriores al "
      "origen. Varianza predicha: ((q_0,90 - q_0,10) / (2 x 1,2816))^2 (equivalente normal del rango interdecil; "
      "el mismo estimador para los tres modelos, porque Chronos-2 solo da cuantiles). QLIKE = ln(s2) + RV/s2 "
      "(forma de Patton sin constante, admite RV = 0; menor es mejor; solo se comparan modelos en el mismo activo "
      "y horizonte).")
    w("")
    w("## Licencias")
    w("")
    w("| componente | licencia | URL | uso |")
    w("|---|---|---|---|")
    for a, b, c, d in LICENCIAS:
        w(f"| {a} | {b} | {c} | {d} |")
    w("")
    w("Datos: Binance Vision CC BY-NC-SA 4.0 (solo uso personal no productivo, ver TI-02-DATA); lago de qn, "
      "propio. Licencias de pesos verificadas en las tarjetas de Hugging Face el 2026-11-09.")
    w("")
    w("## Toto")
    w("")
    w(TOTO)
    w("")
    w("## Reproducibilidad")
    w("")
    meta0 = cargados[0][0][0]
    v = meta0["versiones"]
    w(f"- Versiones: python {v['python']}, numpy {v['numpy']}, scipy {v['scipy']}, pandas {v['pandas']}, "
      f"pyarrow {v['pyarrow']}, arch {v['arch']}, torch {v['torch']}, transformers {v['transformers']}, "
      f"chronos-forecasting {v['chronos-forecasting']}, huggingface_hub {v['huggingface_hub']}; motor "
      f"{v['motor']} (rueda sha256 `{v.get('rueda_quantdesk_sha256')}`). Plataforma: {v['plataforma']}.")
    pes = next((m[0].get("pesos", {}).get("chronos2") for m, _ in cargados if m[0].get("pesos")), None)
    if pes:
        fx = ", ".join(f"`{k}` sha256 `{h}`" for k, h in pes["ficheros"].items())
        w(f"- Pesos de Chronos-2: `{pes['repo']}` revision `{pes['revision']}`: {fx}. HMM y GARCH no tienen pesos "
          "(se calibran en cada origen).")
    w("- Semilla de cada prevision: los 31 bits bajos de sha256(\"semilla|activo|origen_ms|modelo\"); el camino j "
      "del HMM usa semilla x 4096 + j; GARCH usa `numpy.random.default_rng(semilla)`. Hilos: BLAS/OpenMP 1, "
      "torch 2 (`--hilos`).")
    w("")
    w("| dataset | comando exacto | pared (s) | CPU hmm (s, s/origen) | CPU garch | CPU chronos2 | carga de modelos (s CPU) | fallos hmm/garch/chronos2 | HMM sin converger | sha256 predicciones |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for (meta, met), run in cargados:
        cpu = meta["cpu"]

        def c(m, cpu=cpu):
            return f"{cpu[m]['total_s']:.0f} ({cpu[m]['por_origen_s']:.3f})" if m in cpu else "—"

        fal = "/".join(str(meta["fallos"].get(m, "—")) for m in ("hmm", "garch", "chronos2"))
        nc = meta.get("convergencia", {}).get("hmm", {})
        w(f"| {_etiqueta(meta)} | `{meta['comando']}` | {meta['pared_s']:.0f} | {c('hmm')} | {c('garch')} | "
          f"{c('chronos2')} | {meta['cpu_carga_modelos_s']:.0f} | {fal} | {nc.get('no_convergido', '—')} de "
          f"{nc.get('n', '—')} | `{meta['predicciones_sha256'][:16]}…` |")
    w("")
    w("HMM «sin converger»: Baum-Welch agota las 200 iteraciones por defecto sin bajar de `tol` = 1e-8 en la "
      "log-verosimilitud; se usa el ajuste igualmente (es el comportamiento del motor con sus opciones por defecto).")
    if any(m[0]["errores_ejemplo"] for m, _ in cargados):
        w("")
        w("Ejemplos de fallos:")
        for (meta, met), run in cargados:
            for e in meta["errores_ejemplo"]:
                w(f"- {_etiqueta(meta)} {e['instrument']} {datos.fecha(int(e['origen_ms']))} {e['modelo']}: {e['error']}")
    if repeticion:
        with open(os.path.join(repeticion, "meta.json"), encoding="utf-8") as f:
            mr = json.load(f)
        cp = mr.get("comparacion", {})
        w("")
        w("### Repeticion de un subconjunto (aceptacion 3)")
        w("")
        w(f"- Comando: `{mr['comando']}` ({mr['pared_s']:.0f} s de pared mas la carga).")
        w(f"- Resultado: {cp.get('filas')} filas (activo x origen x modelo x h) comparadas con la corrida completa "
          f"`{cp.get('referencia')}`: {cp.get('filas_sin_pareja')} sin pareja; predicciones identicas bit a bit: "
          f"**{cp.get('predicciones_identicas')}** (dif. maxima {cp.get('max_dif_predicciones')}); metricas del "
          f"subconjunto recalculadas desde la corrida completa identicas: **{cp.get('metricas_identicas')}** (dif. "
          f"maxima {cp.get('max_dif_metricas')}). El script sale con codigo 1 si no coinciden.")
        w("")
        w(f"Metricas del subconjunto ({_etiqueta(mr)}), las mismas que da la corrida completa sobre esos origenes:")
        w("")
        import pandas as pd

        ms = pd.read_csv(os.path.join(repeticion, "metricas.csv"))
        w("| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | QLIKE |")
        w("|---|---|---|---|---|---|---|---|")
        for _, r in ms.iterrows():
            w(f"| {r['instrument']} | {r['h']} | {r['modelo']} | {r['n']} | {r['crps']:.10g} | {r['pinball_01']:.10g} | "
              f"{r['pinball_99']:.10g} | {r['qlike']:.10g} |")
    if pilotos:
        w("")
        w("## Presupuesto de CPU (medido antes de las corridas completas)")
        w("")
        w("| piloto | comando | activos x origenes | CPU s/origen hmm | garch | chronos2 |")
        w("|---|---|---|---|---|---|")
        for p in pilotos:
            with open(os.path.join(p, "meta.json"), encoding="utf-8") as f:
                mp = json.load(f)
            cpu = mp["cpu"]
            n = cpu["hmm"]["n"] if "hmm" in cpu else "—"
            w(f"| {_etiqueta(mp)} | `{mp['comando']}` | {n} | {cpu['hmm']['por_origen_s']:.3f} | "
              f"{cpu['garch']['por_origen_s']:.3f} | {cpu['chronos2']['por_origen_s']:.3f} |")
        w("")
        w("Con esas medidas (en una maquina compartida, i7-4790K de 4 nucleos): FX con todos los dias habiles "
          "(paso 1) cuesta ~0,57 s por par activo-origen, unas 6 900 x 0,57 s ~ 66 min de CPU: cabe en 2 h sin "
          "recortar. Binance con origenes diarios desde 2023-11 serian ~10 750 pares x ~1,14 s ~ 3,4 h: se recorta "
          "a un origen cada 3 dias (~3 590 pares, ~68 min), con los 10 activos y la ventana de 1 000 barras. Una "
          "sola corrida pesada a la vez. El CPU y la pared reales de cada corrida estan en la tabla de "
          "reproducibilidad (el CPU de Chronos-2 suma sus 2 hilos de torch).")
    w("")
    w("## Tablas por dataset, activo, horizonte y modelo")
    todas = []
    for (meta, met), run in cargados:
        w("")
        w(f"### {_etiqueta(meta)}")
        w("")
        w("| activo | h | modelo | n | CRPS | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % | n_test | x 1 % | "
          "Kupiec 1 % p | Chr. 1 % p | x 99 % | Kupiec 99 % p | Chr. 99 % p | QLIKE |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for _, r in met.iterrows():
            w(f"| {r['instrument']} | {r['h']} | {r['modelo']} | {r['n']} | {_f(r['crps'])} | {_f(r['pinball_01'])} | "
              f"{_f(r['pinball_99'])} | {_f(r['exc_01'], 3)} | {_f(r['exc_99'], 3)} | {r['n_test']} | {r['x_01']} | "
              f"{_p(r['kupiec_01_p'])} | {_p(r['christ_01_p'])} | {r['x_99']} | {_p(r['kupiec_99_p'])} | "
              f"{_p(r['christ_99_p'])} | {_f(r['qlike'])} |")
        todas.append(met.assign(dataset=meta["dataset"]["dataset_id"], proxy=meta["dataset"]["proxy"],
                                dataset_hash=meta["dataset"]["dataset_hash"]))
    os.makedirs(destino, exist_ok=True)
    allm = pd.concat(todas, ignore_index=True)
    allm = allm[["dataset", "proxy", "dataset_hash"] + [c for c in allm.columns if c not in ("dataset", "proxy",
                                                                                              "dataset_hash")]]
    allm.to_csv(os.path.join(destino, "metricas.csv"), index=False, float_format="%.10g")
    with open(os.path.join(destino, "informe.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print(f"informe: {os.path.join(destino, 'informe.md')} ({sum(len(x) + 1 for x in L)} bytes); metricas.csv "
          f"{os.path.getsize(os.path.join(destino, 'metricas.csv'))} bytes")
    return 0
