"""Verifica los archivos de Correccion 1 sin repetir inferencia ni modificar predicciones."""
import hashlib
import inspect
import json
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "scripts"))
from banco_walkforward_lib import banco, datos, fincast_trabajador as ft, pruebas, rutas

DOCS = Path(__file__).resolve().parent.parent
RUNS = Path(rutas.RUNS_FINCAST)


def huella(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def guardar(p, contenido):
    p.write_text(json.dumps(contenido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    principal = DOCS / "tablas/metricas.csv"
    ref = REPO / "docs/plans/archive/SPRINT-01_2026-11-07_2026-11-09/execution/TS-00-BENCH/metricas.csv"
    assert principal.read_bytes() == ref.read_bytes()
    limpia = pd.read_csv(DOCS / "tablas/metricas_limpia.csv")
    assert limpia.groupby(["dataset", "instrument", "h"]).n.nunique().eq(1).all()
    fc = limpia[limpia.modelo == "fincast"]
    prohibidos = ["crps", "pinball_01", "pinball_99", "exc_01", "exc_99", "n_test", "x_01", "x_99",
                  "kupiec_01_p", "kupiec_99_p", "christ_01_p", "christ_99_p"]
    assert fc[prohibidos].isna().all().all() and fc.criterios_no_aplicables.str.len().gt(0).all()
    assert np.isfinite(fc[["crps_deciles", "qlike"]]).all().all()
    assert (fc.cruces_cuantiles == 0).all()
    p = pd.read_parquet(RUNS / "piloto_fx_v1/predicciones.parquet")
    f = pd.read_parquet(RUNS / "fincast_fx/predicciones.parquet")
    def bits(pred):
        g = pred[(pred.instrument == "EURUSD") & (pred.origen_ms == 1761091200000)].sort_values("h")
        assert len(g) == 3 and g.ok.all()
        return g[banco.QCOLS].to_numpy(dtype="<f8").tobytes()
    assert bits(p) == bits(f)
    originales = json.loads((DOCS / "corridas.json").read_text(encoding="utf-8"))
    sin_cambios = {}
    for n in ("fincast_fx", "fincast_binance"):
        assert huella(RUNS / n / "predicciones.parquet") == originales[n]["parquet_sha256"]
        sin_cambios[n] = originales[n]["parquet_sha256"]
    for n in ("chronos2", "fincast_fx"):
        meta = json.loads((RUNS / "correccion1" / n / "meta.json").read_text(encoding="utf-8"))
        c = meta["comparacion"]
        assert c["predicciones_identicas"] and c["metricas_identicas"] and c["metricas_limpias_identicas"]
        guardar(DOCS / "correccion1" / (n + ".json"), meta)
    # Mutacion en memoria; no se cambia el trabajador ni se toca el arbol de trabajo.
    fuente = inspect.getsource(ft.expandir_deciles)
    original = "i = min(max(int(np.searchsorted(DECILES, p)) - 1, 0), 7)"
    assert original in fuente
    ns = dict(ft.__dict__)
    exec(fuente.replace(original, "i = 0"), ns)
    with patch.object(ft, "expandir_deciles", ns["expandir_deciles"]):
        try:
            pruebas.prueba_interpolacion_asimetrica()
        except AssertionError as exc:
            mutante = str(exc)
        else:
            raise AssertionError("el mutante siempre 0.1-0.2 sobrevivio")
    # Diagnostico de volatilidad reciente observable: sd de los 20 log-retornos previos.
    pred = pd.read_parquet(RUNS / "fincast_binance/predicciones.parquet")
    series, _ = datos.cargar_dataset(rutas.dataset_dir("binance_c20261101"), "binance_ohlcv_1d")
    vol = []
    for ins, g in pred[pred.h == 1].groupby("instrument"):
        cortes, _ = datos.cortes_de_serie(series[ins], g.origen_ms.tolist(), 1000, banco.HMAX)
        ok = g.set_index("origen_ms").ok
        vol.extend({"instrument": ins, "ok": bool(ok[c.origen_ms]),
                    "sd20": float(np.std(np.diff(np.log(c.precios[-21:]))))} for c in cortes)
    vol = pd.DataFrame(vol)
    guardar(DOCS / "correccion1/volatilidad.json",
            {"metodo": "sd poblacional de los 20 log-retornos visibles anteriores; media por par activo-origen",
             "por_activo": vol.groupby(["instrument", "ok"]).sd20.agg(["size", "mean"]).reset_index().to_dict("records"),
             "total": vol.groupby("ok").sd20.agg(["size", "mean"]).reset_index().to_dict("records")})
    cobertura = json.loads((DOCS / "resumen-cobertura.json").read_text(encoding="utf-8"))
    for ds, resumen in cobertura.items():
        for r in resumen["por_activo"]:
            g = fc[(fc.dataset == ds) & (fc.instrument == r["instrument"])]
            r["comunes_por_h"] = {str(int(v.h)): int(v.n) for v in g.itertuples()}
        resumen["activos_sin_origenes_comunes"] = [r["instrument"] for r in resumen["por_activo"] if not r["comunes_por_h"]]
    guardar(DOCS / "resumen-cobertura.json", cobertura)
    guardar(DOCS / "principal-identica.json", {"referencia": str(ref.relative_to(REPO)), "generada": str(principal.relative_to(REPO)),
            "filas": len(pd.read_csv(principal)), "identica": True, "identica_byte_a_byte": True,
            "sha256_csv_canonico": huella(principal), "sha256_archivo": huella(principal)})
    guardar(DOCS / "correccion1/resultados.json", {"principal_byte_a_byte_S01": True,
            "principal_sha256": huella(principal), "limpia_sha256": huella(DOCS / "tablas/metricas_limpia.csv"),
            "limpia_filas": len(limpia), "n_comunes_por_dataset_h": fc.groupby(["dataset", "h"]).n.sum().reset_index().to_dict("records"),
            "determinismo": {"alcance": "esta maquina, CPU, 2 hilos, origenes repetidos; sin afirmacion entre plataformas",
                             "piloto_vs_FX_origen_ms": 1761091200000, "bit_a_bit": True,
                             "h_almacenados": [1, 5, 20], "sha256_63_float64": hashlib.sha256(bits(p)).hexdigest()},
            "parquets_originales_intactos": sin_cambios, "mutante_siempre_par_01_02_detectado": mutante})
    print("principal S01 byte a byte; limpia con n comunes y mascara; FinCast bit a bit; mutante detectado: OK")


if __name__ == "__main__":
    main()
