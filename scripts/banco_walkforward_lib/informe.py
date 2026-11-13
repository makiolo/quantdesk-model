"""informe.md y metricas.csv a partir de las corridas (meta.json, metricas.csv, predicciones.parquet de cada una)."""
from __future__ import annotations

import json
import hashlib
import math
import os
import sys

import numpy as np
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

LICENCIAS_TOTO = [x if not x[0].startswith(("Toto", "toto-ts")) else
                  (x[0], x[1], x[2], "permite uso de investigacion interno; usado (venv aparte, fase 2)")
                  for x in LICENCIAS]

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


MODELOS4 = ("hmm", "garch", "chronos2", "toto")


def _cpu_celda(meta):
    return "; ".join(f"{m} {c['total_s']:.0f} ({c['por_origen_s']:.3f})" for m, c in meta["cpu"].items())


def _cargar_toto(run, base_runs):
    """Une las predicciones de una corrida de Toto con las de la corrida de 3 modelos del mismo dataset y calcula las
    metricas de los 4 modelos sobre los origenes comunes (los de la submuestra de Toto)."""
    import pandas as pd

    meta_t, _ = _cargar(run)
    ds = meta_t["dataset"]["dataset_id"]
    base = [r for r in base_runs if _cargar(r)[0]["dataset"]["dataset_id"] == ds]
    if len(base) != 1:
        raise ValueError(f"corrida de Toto {run} sin una unica corrida base del dataset {ds}")
    meta_b = _cargar(base[0])[0]
    if meta_b["dataset"]["dataset_hash"] != meta_t["dataset"]["dataset_hash"]:
        raise ValueError(f"dataset_hash distinto entre {run} y {base[0]}")
    pt = pd.read_parquet(os.path.join(run, "predicciones.parquet"))
    pb = pd.read_parquet(os.path.join(base[0], "predicciones.parquet"))
    pt = pt[pt["modelo"] == "toto"]
    claves = pt[["instrument", "origen_ms"]].drop_duplicates()
    pb = pb.merge(claves, on=["instrument", "origen_ms"], how="inner")
    # el objetivo de cada origen es el mismo en las dos corridas (mismo dataset y mismo corte)
    chk = pt[["instrument", "origen_ms", "h", "y", "rv"]].drop_duplicates().merge(
        pb[["instrument", "origen_ms", "h", "y", "rv"]].drop_duplicates(), on=["instrument", "origen_ms", "h"])
    if not (np.array_equal(chk["y_x"], chk["y_y"]) and np.array_equal(chk["rv_x"], chk["rv_y"])):
        raise ValueError("el objetivo difiere entre la corrida de Toto y la base")
    pred = pd.concat([pb, pt], ignore_index=True)
    met = banco.metricas_tabla(pred, list(MODELOS4))
    pred["w80"] = pred["q18"] - pred["q02"]
    pred["w98"] = pred["q20"] - pred["q00"]
    pred["cola"] = pred["w98"] / pred["w80"]
    g = pred.groupby(["h", "modelo"])
    anchos = g[["w80", "w98", "cola"]].median().join(g["w98"].quantile(0.99).rename("w98_p99")).reset_index()
    meta_t["_anchos"] = anchos.to_dict("records")
    return meta_t, met, base[0]


def escribir(runs, repeticiones, destino, pilotos=None, totos=None, fincasts=None) -> int:
    import pandas as pd

    if any(_cargar(r)[0]["dataset"]["dataset_id"] in rutas.HASHES_MT5 for r in runs):
        from . import informe_mt5

        return informe_mt5.escribir(runs, repeticiones, destino, pilotos, totos, fincasts)

    cargados = [(_cargar(r), r) for r in runs]
    cargados.sort(key=lambda x: (x[0][0]["dataset"]["dataset_id"] != CABECERA, x[0][0]["dataset"]["dataset_id"]))
    tt = [_cargar_toto(r, runs) + (r,) for r in (totos or [])]
    tt.sort(key=lambda x: (x[0]["dataset"]["dataset_id"] != CABECERA, x[0]["dataset"]["dataset_id"]))
    L = []
    w = L.append
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    w("# TS-00-BENCH: banco walk-forward (HMM del motor, GARCH(1,1), Chronos-2 y Toto en zero-shot)" if tt else
      "# TS-00-BENCH: banco walk-forward (HMM del motor, GARCH(1,1), Chronos-2 zero-shot; Toto pendiente)")
    w("")
    w(f"- Generado por `scripts/banco_walkforward.py --informe` el {ahora} a partir de las salidas de las corridas "
      "(`meta.json`, `metricas.csv`, `predicciones.parquet` en `E:/quantdesk-lab/runs/TS-00-BENCH/`). Comando: "
      "`.venv/Scripts/python -X utf8 scripts/banco_walkforward.py "
      + " ".join(sys.argv[1:]).replace(os.sep, "/").replace(rutas.REPO.replace(os.sep, "/") + "/", "") + "`.")
    w("- Selftest: `.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --selftest` (sin red: el selftest "
      "bloquea los sockets; sin datos reales; Chronos-2 sustituido por un modelo trivial con la misma interfaz; "
      "Toto, por su trabajador real en modo `--falso` lanzado como subproceso, y un venv de Toto inexistente deja "
      "Toto SALTADO sin romper la corrida).")
    w(f"- Motor: **{banco.MOTOR}** (commit `{banco.MOTOR_COMMIT}`). Semilla: **{banco.SEMILLA}**. Solo CPU.")
    w(f"- **Tabla de cabecera: `{CABECERA}`** (FX diario del lago; decision del usuario del 2026-11-09). Su "
      "disponibilidad es un **proxy** (`available_at_ms` nulo, `default_lag_ms` = 0: valores que qn recibio "
      "despues del corte) y cada tabla y cifra suya lleva la etiqueta «proxy». `binance_c20261101` es la segunda tabla.")
    w("- Datasets: los dos que fija la ficha. De los otros dos de TI-02-DATA, `lago_c20261101` (estricto) tiene las "
      "tablas OHLCV vacias tras el corte (0 filas; no hay serie que evaluar) y `lago_c20261107` no esta en la ficha.")
    w("- No se fijan umbrales de exito (TS-00-OBJ). Las cifras son descriptivas.")
    w("")
    w("## Resumen por modelo")
    w("")
    w("Medianas entre activos de cada metrica; «CRPS rel.» es la mediana del cociente CRPS del modelo / CRPS de "
      "GARCH en el mismo activo (< 1 mejor que GARCH). «Gana» cuenta los activos en que el modelo tiene el menor "
      "CRPS (y el menor QLIKE). «Kupiec/Chr. p<0,05» cuenta activos en que el test rechaza al 5 %. Excedencias "
      "esperadas: 1 % en cada cola.")
    for (meta, met), run in cargados:
        mods = [m for m in meta["config"]["modelos"] if m != "fincast"]
        w("")
        w(f"### {_etiqueta(meta)}" + (" — tabla de cabecera" if meta["dataset"]["dataset_id"] == CABECERA else ""))
        w("")
        w("| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % "
          "| Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in _resumen(met, mods) if not met.empty else []:
            w(f"| {r['h']} | {r['modelo']} | {r['activos']} | {_f(r['crps'])} | {_f(r['crps_rel'], 3)} | "
              f"{_f(r['p01'])} | {_f(r['p99'])} | {_f(r['exc01'], 3)} | {_f(r['exc99'], 3)} | {r['ku01']}/{r['ku99']} | "
              f"{r['ch01']}/{r['ch99']} | {_f(r['qlike'])} | {r['gana']} | {r['gana_q']} |")
    if tt:
        w("")
        w("## Toto frente a HMM, GARCH y Chronos-2 (submuestra de origenes)")
        w("")
        w("Toto cuesta mucho mas CPU por origen que los otros tres (ver presupuesto de CPU), asi que no cabe en 2 h "
          "con la rejilla completa: se corre sobre una submuestra declarada de origenes (`--cada N`: uno de cada N "
          "origenes validos de cada activo, todos los activos) y aqui los CUATRO modelos se comparan sobre exactamente "
          "esos origenes (las predicciones de HMM, GARCH y Chronos-2 son las de la corrida completa: cada origen es "
          "independiente y reproducible). Las tablas de arriba (3 modelos, rejilla completa) no cambian.")
        for meta_t, met4, base, run in tt:
            c = meta_t["config"]
            n = sum(v["evaluados"] for v in meta_t["omitidos"].values())
            w("")
            w(f"### {_etiqueta(meta_t)}" + (" — tabla de cabecera" if meta_t["dataset"]["dataset_id"] == CABECERA
                                            else "") + f": uno de cada {c.get('cada', 1)} origenes ({n} pares)")
            w("")
            w("| h | modelo | activos | CRPS (med.) | CRPS rel. GARCH | pinball 0,01 | pinball 0,99 | exc. 1 % | exc. 99 % "
              "| Kupiec p<0,05 (1 %/99 %) | Chr. p<0,05 (1 %/99 %) | QLIKE (med.) | gana CRPS | gana QLIKE |")
            w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for r in _resumen(met4, list(MODELOS4)):
                w(f"| {r['h']} | {r['modelo']} | {r['activos']} | {_f(r['crps'])} | {_f(r['crps_rel'], 3)} | "
                  f"{_f(r['p01'])} | {_f(r['p99'])} | {_f(r['exc01'], 3)} | {_f(r['exc99'], 3)} | "
                  f"{r['ku01']}/{r['ku99']} | {r['ch01']}/{r['ch99']} | {_f(r['qlike'])} | {r['gana']} | {r['gana_q']} |")
        w("")
        w("Anchura de las bandas predichas sobre esos mismos origenes (en log-rendimiento): mediana de la banda "
          "10-90 % (`q90 - q10`) y de la banda 1-99 % (`q99 - q01`), mediana del cociente entre ambas (cola; una "
          "normal da 1,82) y percentil 99 de la banda 1-99 % entre origenes (colas explosivas).")
        for meta_t, met4, base, run in tt:
            w("")
            w(f"| {_etiqueta(meta_t)} h | modelo | banda 10-90 % | banda 1-99 % | cola (1-99 / 10-90) | banda 1-99 % p99 |")
            w("|---|---|---|---|---|---|")
            for r in meta_t["_anchos"]:
                w(f"| {r['h']} | {r['modelo']} | {_f(r['w80'])} | {_f(r['w98'])} | {_f(r['cola'], 3)} | "
                  f"{_f(r['w98_p99'])} |")
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
    if tt:
        w(f"- **toto**: `{modelos.TOTO_ID}` revision `{modelos.TOTO_REV}`, zero-shot, CPU, en un subproceso con el "
          "venv aparte `E:/quantdesk-lab/venvs/toto` (`scripts/banco_walkforward_lib/toto_trabajador.py`, protocolo "
          "de lineas JSON; los precios viajan como float64 sin perdida). Mismo contrato que Chronos-2: contexto = "
          f"log-precio de la ventana (W barras), {modelos.TOTO_MUESTRAS} trayectorias a 20 pasos "
          "(`TotoForecaster.forecast`, `samples_per_batch` = numero de muestras, `torch.manual_seed(semilla)` antes "
          "de cada prevision, `use_deterministic_algorithms(True)`, 2 hilos), cuantiles empiricos de "
          "log P_{t+h} - log P_t. Marcas de tiempo sinteticas a 1 dia por barra. El CPU del subproceso lo mide el "
          "trabajador y se suma al de Toto. Sin el venv, `--modelos ...,toto` deja Toto SALTADO y la corrida sigue.")
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
    for a, b, c, d in (LICENCIAS_TOTO if tt else LICENCIAS):
        w(f"| {a} | {b} | {c} | {d} |")
    w("")
    w("Datos: Binance Vision CC BY-NC-SA 4.0 (solo uso personal no productivo, ver TI-02-DATA); lago de qn, "
      "propio. Licencias de pesos verificadas en las tarjetas de Hugging Face el 2026-11-09.")
    w("")
    w("## Toto")
    w("")
    if tt:
        mt = tt[0][0]
        vt = mt.get("versiones_externas", {}).get("toto", {})
        pt = mt.get("pesos", {}).get("toto") or {}
        w("Instalado en la fase 2 por decision del usuario (venv aparte; el `.venv` del laboratorio no se toca).")
        w("")
        w("- Ordenes ejecutadas (con `PIP_CACHE_DIR`, `HF_HOME` y `TMPDIR` bajo E:/quantdesk-lab): "
          "`D:/miniconda312/python.exe -m venv E:/quantdesk-lab/venvs/toto`; "
          "`E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install --index-url https://download.pytorch.org/whl/cpu "
          "torch==2.7.0`; `E:/quantdesk-lab/venvs/toto/Scripts/python -m pip install toto-ts==0.2.0 pyarrow` (con "
          "las dependencias que fija toto-ts 0.2.0, entre ellas numpy 1.26.4, pandas 2.2.3, transformers 4.52.1 y "
          "gluonts 0.16.2, y herramientas de desarrollo que el paquete declara como dependencias de ejecucion). Pesos "
          "descargados una vez con `toto_trabajador.py --descargar`; las corridas usan `HF_HUB_OFFLINE=1`.")
        w("- Versiones del venv de Toto: " + ", ".join(f"{k} {v}" for k, v in vt.items() if k != "ejecutable") + ".")
        if pt:
            w(f"- Pesos: `{pt.get('repo')}` revision `{pt.get('revision')}`: "
              + ", ".join(f"`{k}` sha256 `{h}`" for k, h in pt.get("ficheros", {}).items()
                          if not k.startswith("figures/")) + ".")
    else:
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
    w("| dataset | comando exacto | pared (s) | CPU por modelo: total s (s/origen) | carga de modelos (s CPU) | "
      "fallos por modelo | HMM sin converger | sha256 predicciones |")
    w("|---|---|---|---|---|---|---|---|")
    metas_corridas = [m for (m, _), _r in cargados] + [x[0] for x in tt]
    for meta in metas_corridas:
        fal = ", ".join(f"{m} {n}" for m, n in meta["fallos"].items())
        nc = meta.get("convergencia", {}).get("hmm", {})
        w(f"| {_etiqueta(meta)} | `{meta['comando']}` | {meta['pared_s']:.0f} | {_cpu_celda(meta)} | "
          f"{meta['cpu_carga_modelos_s']:.0f} | {fal} | {nc.get('no_convergido', '—')} de "
          f"{nc.get('n', '—')} | `{meta['predicciones_sha256'][:16]}…` |")
    w("")
    w("HMM «sin converger»: Baum-Welch agota las 200 iteraciones por defecto sin bajar de `tol` = 1e-8 en la "
      "log-verosimilitud; se usa el ajuste igualmente (es el comportamiento del motor con sus opciones por defecto). "
      "El CPU de Chronos-2 y de Toto suma sus 2 hilos de torch; el de Toto lo mide su subproceso.")
    if any(m["errores_ejemplo"] for m in metas_corridas):
        w("")
        w("Ejemplos de fallos:")
        for meta in metas_corridas:
            for e in meta["errores_ejemplo"]:
                w(f"- {_etiqueta(meta)} {e['instrument']} {datos.fecha(int(e['origen_ms']))} {e['modelo']}: {e['error']}")
    for repeticion in repeticiones or []:
        with open(os.path.join(repeticion, "meta.json"), encoding="utf-8") as f:
            mr = json.load(f)
        cp = mr.get("comparacion", {})
        w("")
        w(f"### Repeticion de un subconjunto (aceptacion 3): {', '.join(mr['config']['modelos'])}")
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
        w("| piloto | comando | activos x origenes | pared (s) | CPU s/origen por modelo |")
        w("|---|---|---|---|---|")
        for p in pilotos:
            with open(os.path.join(p, "meta.json"), encoding="utf-8") as f:
                mp = json.load(f)
            cpu = mp["cpu"]
            n = next(iter(cpu.values()))["n"]
            w(f"| {_etiqueta(mp)} | `{mp['comando']}` | {n} | {mp['pared_s']:.0f} | "
              + "; ".join(f"{m} {c['por_origen_s']:.3f}" for m, c in cpu.items()) + " |")
        w("")
        w("Con esas medidas (en una maquina compartida, i7-4790K de 4 nucleos): FX con todos los dias habiles "
          "(paso 1) cuesta ~0,57 s por par activo-origen, unas 6 900 x 0,57 s ~ 66 min de CPU: cabe en 2 h sin "
          "recortar. Binance con origenes diarios desde 2023-11 serian ~10 750 pares x ~1,14 s ~ 3,4 h: se recorta "
          "a un origen cada 3 dias (~3 590 pares, ~68 min), con los 10 activos y la ventana de 1 000 barras. Una "
          "sola corrida pesada a la vez. El CPU y la pared reales de cada corrida estan en la tabla de "
          "reproducibilidad (el CPU de Chronos-2 suma sus 2 hilos de torch).")
        pil_toto = []
        for p in pilotos:
            with open(os.path.join(p, "meta.json"), encoding="utf-8") as f:
                mp = json.load(f)
            if list(mp["cpu"]) == ["toto"]:
                pil_toto.append(mp)
        for mp in pil_toto:
            ds = mp["dataset"]["dataset_id"]
            seg = mp["pared_s"] / mp["cpu"]["toto"]["n"]
            base = next((m for (m, _), _r in cargados if m["dataset"]["dataset_id"] == ds), None)
            total = sum(v["evaluados"] for v in base["omitidos"].values()) if base else 0
            corr = next((x[0] for x in tt if x[0]["dataset"]["dataset_id"] == ds), None)
            elegido = corr["config"].get("cada", 1) if corr else None
            real = ""
            if corr:
                n_r = corr["cpu"]["toto"]["n"]
                real = (f" Real: {n_r} pares, {corr['pared_s'] / 3600:.2f} h de pared ({corr['pared_s'] / n_r:.1f} s por "
                        f"origen) y {corr['cpu']['toto']['por_origen_s']:.1f} s de CPU por origen"
                        + (": **supera las 2 h de pared**; el CPU por origen apenas cambia frente al piloto, la pared "
                           "crece porque la maquina compartida estuvo al 100 % de CPU (antivirus, terminal y descargas "
                           "MT5 de otro proyecto) durante la corrida." if corr["pared_s"] > 7200 else ".")
                        )
            w("")
            w(f"Toto en {_etiqueta(mp)}: {seg:.1f} s de pared y {mp['cpu']['toto']['por_origen_s']:.1f} s de CPU por "
              f"origen en el piloto; la rejilla completa ({total} pares) costaria ~{total * seg / 3600:.1f} h de "
              f"pared, mas de 2 h. Se corre uno de cada {elegido} origenes (~{total / max(elegido or 1, 1) * seg / 3600:.1f} h"
              f" estimadas con la carga del piloto) con todos los activos.{real} Propuesta para otro momento (maquina "
              f"libre): la rejilla completa con `--modelos toto --cada 1`, en tandas por activo con `--activos` (cada "
              f"tanda < 2 h) y `--reanudar`.")
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
                                dataset_hash=meta["dataset"]["dataset_hash"][:23],  # prefijo; completo en el informe
                                conjunto="rejilla_completa_3_modelos"))
    for meta, met, base, run in tt:
        cada = meta["config"].get("cada", 1)
        w("")
        w(f"### {_etiqueta(meta)}: 4 modelos sobre la submuestra de Toto (uno de cada {cada} origenes)")
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
                                dataset_hash=meta["dataset"]["dataset_hash"][:23],
                                conjunto=f"submuestra_toto_cada_{cada}_4_modelos"))
    seccion, limpia, estados = seccion_limpia(list(runs) + list(totos or []) + list(fincasts or []))
    L.extend(seccion)
    os.makedirs(destino, exist_ok=True)
    allm = pd.concat(todas, ignore_index=True)
    primeras = ["dataset", "proxy", "dataset_hash", "conjunto"]
    allm = allm[primeras + [c for c in allm.columns if c not in primeras]]
    allm.to_csv(os.path.join(destino, "metricas.csv"), index=False, float_format="%.10g")
    limpia.to_csv(os.path.join(destino, "metricas_limpia.csv"), index=False, float_format="%.10g")
    with open(os.path.join(destino, "ventana_limpia.json"), "w", encoding="utf-8") as f:
        json.dump(estados, f, ensure_ascii=False, indent=1)
    with open(os.path.join(destino, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"motor": banco.MOTOR_COMMIT, "semilla": banco.SEMILLA, "corte_utc": banco.CORTE_LIMPIO,
                   "datasets": estados}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(destino, "informe.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L).rstrip() + "\n")
    print(f"informe: {os.path.join(destino, 'informe.md')} ({sum(len(x) + 1 for x in L)} bytes); metricas.csv "
          f"{os.path.getsize(os.path.join(destino, 'metricas.csv'))} bytes")
    return 0


def cargar_limpia(runs):
    """Une predicciones del mismo dataset sin limitar la tabla principal a la submuestra FinCast.
    Rechaza diferencias de dataset, contexto, semilla u objetivo antes de calcular criterios comunes.
    """
    import pandas as pd

    metas, partes = [], []
    for run in runs:
        with open(os.path.join(run, "meta.json"), encoding="utf-8") as f:
            metas.append(json.load(f))
        partes.append(pd.read_parquet(os.path.join(run, "predicciones.parquet")))
    base = metas[0]
    for m in metas[1:]:
        if m["dataset"]["dataset_hash"] != base["dataset"]["dataset_hash"]:
            raise ValueError("dataset_hash distinto en la comparacion limpia")
        for k in ("ventana", "horizontes", "semilla"):
            if m["config"][k] != base["config"][k]:
                raise ValueError(f"{k} distinto en la comparacion limpia")
    pred = pd.concat(partes, ignore_index=True)
    clave = ["instrument", "origen_ms", "h"]
    if pred.duplicated(clave + ["modelo"]).any():
        raise ValueError("predicciones duplicadas entre corridas de la tabla limpia")
    for k in ("y", "rv", "k", "ts_ultima_ms"):
        if (pred.groupby(clave)[k].nunique(dropna=False) > 1).any():
            raise ValueError(f"{k}: objetivo/contexto distinto entre corridas de la tabla limpia")
    ms = sorted({m for meta in metas for m in meta["config"]["modelos"]})
    met = banco.metricas_tabla(pred, ms, limpia=True)
    estado = banco.estado_limpia(pred, met, ms)
    estado["dataset_hash"] = base["dataset"]["dataset_hash"]
    estado["cruces_todos_origenes"] = banco.contar_cruces(pred)
    return met, estado, metas


def seccion_limpia(runs):
    import pandas as pd
    from . import fincast_trabajador as ft

    grupos = {}
    hay_fincast = False
    for run in runs:
        with open(os.path.join(run, "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
            ds = meta["dataset"]["dataset_id"]
            hay_fincast |= "fincast" in meta["config"]["modelos"]
        grupos.setdefault(ds, []).append(run)
    L = ["", "## Ventana limpia: segundo calculo de los mismos criterios", "",
         f"Origen estrictamente posterior a **{banco.CORTE_LIMPIO}**; el contexto puede ser anterior. "
         "Todos los modelos de cada tabla usan los mismos origenes validos comunes. La tabla principal "
         "conserva los origenes de sus modelos sin recortar por FinCast.", "",
         "**Comparacion condicionada:** cuando entra FinCast, solo se puntuan los origenes donde no falla. "
         "La cobertura por activo/h y el efecto de esa seleccion sobre los modelos base se declaran abajo; "
         "no es una muestra aleatoria de la ventana posterior al corte. Los cruces de hmm/garch/chronos2/toto "
         "se conservan y puntuan como en SPRINT-01, sin reordenar ni descartar. Solo FinCast los rechaza. "
         "La columna cruces_cuantiles cuenta origenes cruzados realmente puntuados por celda; el anexo "
         "cuenta tambien los suministrados antes de la interseccion.", "",
         "`crps_deciles` = 2 × media de los pinball en 0.1, 0.2, …, 0.9, para todos los modelos. "
         "No es el CRPS continuo ni el de 21 niveles. FinCast solo aporta `crps_deciles` y QLIKE "
         "(varianza = ((q90-q10)/(2 Phi^-1(0.9)))²). CRPS de 21 niveles, pinball 1 %/99 %, excedencias, "
         "Kupiec y Christoffersen de FinCast: **no aplicables**, quedan vacios en CSV y — en la tabla.", "",
         "Para los demas modelos, un p-valor de Christoffersen vacio significa que el test no esta definido: "
         "menos de dos observaciones, ninguna excedencia o una fila de transiciones vacia. No equivale a "
         "aceptar independencia. Una celda sin origenes comunes validos no se puntua. Los tests de colas "
         "con pocas observaciones tienen poca potencia; las cifras siguen siendo descriptivas.", "",
         "Cuantiles de FinCast: " + ft.METODO + ". Nativos: 0.1..0.9; extrapolados: 0.01/0.05/0.95/0.99; "
         "interpolados: 0.15/0.25/0.35/0.45/0.55/0.65/0.75/0.85. Ninguno de los niveles no nativos "
         "entra en sus criterios.", ""]
    if hay_fincast:
        L += ["FinCast v1: decoder oficial sin modificar, 50 capas, dimension 1280, 16 cabezas, 4 expertos/top-2, "
              "patch 32, horizonte de salida 128, frecuencia diaria 0. Contexto log-precio completo, "
              "padding frontal al siguiente multiplo de 32, lote 1, CPU float32. Se importa directamente el "
              "decoder para evitar la API de covariables JAX; `torch.load(weights_only=True)`, "
              "`load_state_dict(strict=True)`, `eval()` y `torch.use_deterministic_algorithms(True)`. "
              "Semilla reiniciada por origen, tambien para el sorteo del gate MoE.", "",
              f"Timeout FinCast por peticion: {modelos.FINCAST_TIMEOUT_S:g} s por defecto "
              "(`--fincast-timeout`); arranque 300 s. Un timeout mata el trabajador y marca el origen fallido; "
              "el siguiente origen arranca otro. CPU de peticiones fallidas sin respuesta no recuperable; "
              "el tiempo de espera si esta en la pared. Las respuestas JSON completas de error conservan "
              "el trabajador sincronizado y su CPU externa con el driver v2. Toto conserva su comportamiento previo.", "",
              "Licencias verificadas el 2026-11-11: [codigo Apache-2.0](https://github.com/vincent05r/FinCast-fts/blob/"
              + modelos.FINCAST_CODIGO_REV + "/LICENSE), SHA-256 de LICENSE "
              "`1eb85fc97224598dad1852b5d6483bbcf0aa8608790dcc657a5a2a761ae9c8c6`; "
              "[tarjeta de pesos Apache-2.0](https://huggingface.co/Vincent05R/FinCast/blob/"
              + modelos.FINCAST_REV + "/README.md), SHA-256 "
              "`cbc5c2eb63cd9cc2ff8baa1ed888cd062e81ec170413ffe9827b920bc726794d`. "
              f"v1.pth SHA-256 `{modelos.FINCAST_SHA256}`. La tarjeta no fija fecha de corte del "
              "preentrenamiento: la ventana posterior a publicacion es el control disponible, no una prueba "
              "de ausencia de contaminacion de los pesos.", ""]
    tablas, estados = [], {}
    for ds, rr in grupos.items():
        met, estado, metas = cargar_limpia(rr)
        estados[ds] = estado
        estado["metricas_sha256"] = hashlib.sha256(met.to_csv(index=False, float_format="%.10g").encode()).hexdigest()
        L += [f"### {_etiqueta(metas[0])}: ventana limpia", "",
              f"Dataset SHA-256: `{metas[0]['dataset']['dataset_hash']}`. Estado: **{estado['estado']}**. "
              + (estado["motivo"] + "." if met.empty else "Orígenes comunes por activo y horizonte: columna n."), ""]
        validacion = estado["validacion_predicciones"]
        if validacion["origenes_modelo_excluidos"]:
            L += [f"**Predicciones archivadas invalidas:** {validacion['origenes_modelo_excluidos']} pares "
                  f"origen-modelo ({validacion['por_modelo']}) con cuantiles no finitos o FinCast no monotono, "
                  "excluidos de TODOS los horizontes de la comparacion limpia. No se reparan cuantiles ni se "
                  "reescriben predicciones o criterios de las tablas principales historicas. La validacion "
                  "cuenta todos los origenes limpios suministrados antes de tomar la interseccion; n es "
                  "el numero comun realmente puntuado por celda. La validacion "
                  "del archivo solo puede comprobar los horizontes almacenados (1/5/20); FinCast nuevo "
                  "comprueba los 20 horizontes. Ejemplos: " + str(validacion["ejemplos"]) + ".", ""]
        L += ["Anexo de cruces conservados (por dataset/modelo/h; filas ok antes de la interseccion). "
              "Solo se conocen los horizontes almacenados 1/5/20 en los archivos de SPRINT-01; "
              "FinCast valida los 20 al inferir.", "",
              "| modelo | h | n todos | cruces todos | n posteriores al corte | cruces posteriores al corte |",
              "|---|---:|---:|---:|---:|---:|"]
        limpios = {(r["modelo"], r["h"]): r for r in estado["cruces_cuantiles"]["por_modelo_h"]}
        for r in estado["cruces_todos_origenes"]["por_modelo_h"]:
            c = limpios.get((r["modelo"], r["h"]), {})
            L.append(f"| {r['modelo']} | {r['h']} | {r['n_validos']} | {r['origenes_con_cruce']} | "
                     f"{c.get('n_validos', 0)} | {c.get('origenes_con_cruce', 0)} |")
        L.append("")
        seleccion = estado["seleccion_fincast"]
        if seleccion["condicionada"]:
            L += ["Cobertura de la comparacion condicionada a FinCast. n_base: origenes intentados por FinCast "
                  "con todos los modelos base validos; n_comun: subconjunto donde FinCast es valido. "
                  "Los fallos FinCast se declaran aunque un origen ya carezca de algun modelo base.", "",
                  "| activo | h | intentos FinCast | fallos FinCast | n_base | n_comun |",
                  "|---|---:|---:|---:|---:|---:|"]
            for r in seleccion["cobertura"]:
                L.append(f"| {r['instrument']} | {r['h']} | {r['intentos_fincast']} | {r['fallos_fincast']} | "
                         f"{r['n_base']} | {r['n_comun']} |")
            L += ["", "Efecto medido de la seleccion sobre CRPS deciles de modelos base: " + seleccion["metodo"] + ". "
                  "Es un diagnostico descriptivo de seleccion, sin interpretacion causal.", "",
                  "| modelo | h | n_base | n_comun | CRPS deciles base | CRPS deciles comun | variacion % |",
                  "|---|---:|---:|---:|---:|---:|---:|"]
            for r in seleccion["efecto_crps_deciles"]:
                L.append(f"| {r['modelo']} | {r['h']} | {r['n_base']} | {r['n_comun']} | "
                         f"{_f(r['base'], 8)} | {_f(r['comun'], 8)} | {_f(r['variacion_pct'], 6)} |")
            L.append("")
        if not met.empty:
            cols = ["instrument", "h", "modelo", *banco.metricas.COLUMNAS_RESUMEN, "crps_deciles", "cruces_cuantiles"]
            L += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
            for _, r in met.iterrows():
                L.append("| " + " | ".join(str(r[c]) if c in banco.CLAVES_METRICAS else _f(r[c], 8)
                                          for c in cols) + " |")
            L.append("")
        L += ["| corrida | modelos | cada | solo limpia | CPU s/origen | pared inferencia / total s | fallos | SHA-256 predicciones |",
              "|---|---|---|---|---|---|---|---|"]
        for m, run in zip(metas, rr):
            L.append(f"| `{run}` | {','.join(m['config']['modelos'])} | {m['config'].get('cada', 1)} | "
                     f"{m['config'].get('solo_limpia', False)} | "
                     + "; ".join(f"{n}: {c['por_origen_s']:.4g}" for n, c in m["cpu"].items())
                     + f" | {m['pared_s']:.2f} / {m.get('pared_total_s', 'no medida')} | {m['fallos']} | "
                     f"`{m['predicciones_sha256']}` |")
            if m.get("saltados"):
                L.append(f"Modelos saltados declarados: {m['saltados']}.")
            if ("fincast" in m["config"]["modelos"] and m["fallos"].get("fincast")
                    and (not m["config"].get("fincast_driver") or m.get("reanudados"))):
                L.append("Limitacion del driver inicial de esta corrida: CPU externa de respuestas fallidas no "
                         "conservada y recargas posteriores no sumadas a CPU de carga inicial; si incluidas en "
                         "pared. La CPU por origen es la registrada, no el coste completo de los fallos. "
                         "El informe principal adjunta tambien CPU por origen valido.")
            for e in m.get("errores_ejemplo", []):
                L.append(f"Fallo declarado: {e['instrument']} {e['origen_ms']} {e['modelo']}: {e['error']}.")
        L.append("")
        tablas.append(met.assign(dataset=ds, dataset_hash=metas[0]["dataset"]["dataset_hash"]))
    return L, pd.concat(tablas, ignore_index=True), estados
