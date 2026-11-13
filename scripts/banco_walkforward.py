"""Banco walk-forward: HMM, GARCH, Chronos-2, Toto y FinCast (solo criterios en ventana limpia).

Uso, con el venv del laboratorio:
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --selftest
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 \
      --out E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 \
      --out E:/quantdesk-lab/runs/TS-00-BENCH/binance_c20261101
  (repeticion de un subconjunto, <= 10 min, comparada con la corrida completa)
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 \
      --activos EURUSD,USDJPY --max-origenes 12 --out E:/quantdesk-lab/runs/TS-00-BENCH/repeticion \
      --comparar E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101
  (Toto, fase 2: venv aparte E:/quantdesk-lab/venvs/toto; submuestra declarada de origenes)
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos toto \
      --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH/toto_lago_cierre_c20261101
  (FinCast: venv propio, 9 deciles nativos, timeout por peticion de 600 s)
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos fincast \
      --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/fx
  (informe a partir de las corridas)
  .venv/Scripts/python -X utf8 scripts/banco_walkforward.py --informe RUN1 RUN2 [--toto RUN ...] \
      [--repeticion RUN ...] [--pilotos RUN ...] --destino docs/plans/current/execution/TS-00-BENCH

Cada origen es independiente (semilla derivada de semilla|activo|origen|modelo, Chronos-2 con lote 1), asi que un
subconjunto reproduce exactamente las filas de la corrida completa. Toto corre en un subproceso con su venv aparte
(modelos.Toto); si el venv no existe queda SALTADO y la corrida sigue con los demas modelos.
Solo CPU. Los datasets antiguos se leen de TI-02-DATA y los dos MT5 fijados de TI-02-DATA-V2, ambos bajo
E:/quantdesk-lab/datasets (solo lectura); las salidas pesadas van a
E:/quantdesk-lab/runs/TS-00-BENCH/; los pesos de Chronos-2 se leen de la cache de HF del laboratorio sin red.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from banco_walkforward_lib import rutas  # noqa: E402

C_MIN_GB = 2.0
# Toto (fase 2) se pide con --modelos ...,toto: el valor por defecto sigue siendo el de la fase 1 para que sus
# comandos documentados (y la repeticion con --comparar) se reproduzcan igual. Sin su venv, Toto queda SALTADO.
MODELOS = ("hmm", "garch", "chronos2")


def espacio_c_ok() -> bool:
    try:
        libre = shutil.disk_usage("C:/").free / 2**30
    except OSError:
        return True
    if libre < C_MIN_GB:
        print(f"banco_walkforward: C: tiene {libre:.2f} GB libres (< {C_MIN_GB} GB): PARO")
        return False
    return True


def fabrica_modelos(nombres, hilos, toto_python=None, fincast_timeout=None, fincast_python=None):
    """(modelos, saltados). Toto sin su venv aparte no rompe la corrida: queda SALTADO con el motivo."""
    from banco_walkforward_lib import modelos

    out, saltados = [], {}
    for n in nombres:
        if n == "hmm":
            out.append(modelos.Hmm())
        elif n == "garch":
            out.append(modelos.Garch())
        elif n == "chronos2":
            out.append(modelos.Chronos2(hilos))
        elif n == "toto":
            try:
                os.makedirs(rutas.TMP, exist_ok=True)
                out.append(modelos.Toto(hilos, python=toto_python or modelos.TOTO_PY,
                                        log=rutas.TMP + "/toto_trabajador.log"))
            except modelos.ModeloSaltado as exc:
                saltados[n] = str(exc)
        elif n == "fincast":
            try:
                os.makedirs(rutas.TMP_FINCAST, exist_ok=True)
                out.append(modelos.FinCast(hilos, python=fincast_python or modelos.FINCAST_PY,
                                           timeout_s=modelos.FINCAST_TIMEOUT_S if fincast_timeout is None else fincast_timeout,
                                           log=rutas.TMP_FINCAST + "/fincast_trabajador.log"))
            except modelos.ModeloSaltado as exc:
                saltados[n] = str(exc)
        else:
            raise ValueError(f"modelo desconocido {n!r}")
    return out, saltados


def cmd_correr(a) -> int:
    from banco_walkforward_lib import banco

    try:
        out = rutas.validar_out(a.out)
        rutas.dataset_dir(a.dataset)
    except rutas.RutaNoAutorizada as exc:
        print(f"banco_walkforward: {exc}")
        return 2
    if a.dataset not in banco.PRESETS:
        print(f"banco_walkforward: dataset sin configuracion: {a.dataset} (hay {sorted(banco.PRESETS)})")
        return 2
    hf = os.environ.get("HF_HOME", "")
    if not rutas.dentro(hf or "C:/", rutas.LAB):
        print(f"banco_walkforward: HF_HOME={hf!r} no esta bajo {rutas.LAB}: PARO")
        return 2
    os.environ["HF_HUB_OFFLINE"] = "1"  # los pesos ya estan en la cache del laboratorio; ninguna corrida usa red
    if a.dataset in rutas.HASHES_MT5:
        rutas.TMP = rutas.TMP_FINCAST = rutas.LAB + "/tmp/TS-00-BENCH-MT5"
    if not espacio_c_ok():
        return 3
    nombres = [m for m in a.modelos.split(",") if m]
    activos = [x for x in a.activos.split(",") if x] if a.activos else None
    comando = ".venv/Scripts/python -X utf8 scripts/banco_walkforward.py " + " ".join(sys.argv[1:]).replace(os.sep, "/")
    def fabrica(nombres, hilos):
        return fabrica_modelos(nombres, hilos, fincast_timeout=a.fincast_timeout)

    try:
        pred, met, meta = banco.ejecutar(a.dataset, out, nombres, activos, a.max_origenes, a.semilla, a.hilos, comando,
                                      a.reanudar, fabrica, cada=a.cada, solo_limpia=a.solo_limpia)
    except ValueError as exc:
        print(f"banco_walkforward: {exc}")
        return 2
    if "fincast" in nombres:
        meta["config"]["fincast_timeout_s"] = a.fincast_timeout
        meta["config"]["fincast_driver"] = "errores_sin_recargar_v2"
    if "chronos2" in nombres:
        from banco_walkforward_lib import modelos

        meta.setdefault("pesos", {})["chronos2"] = modelos.pesos_chronos()
    if a.comparar:
        meta["comparacion"] = banco.comparar(out, os.path.abspath(a.comparar))
        print("comparacion:", json.dumps(meta["comparacion"], ensure_ascii=False))
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1, default=str)
    for m, c in meta["cpu"].items():
        print(f"cpu {m}: {c['total_s']:.1f} s en {c['n']} origenes ({c['por_origen_s']:.3f} s/origen); "
              f"fallos {meta['fallos'][m]}")
    print(f"carga de modelos {meta['cpu_carga_modelos_s']:.1f} s cpu; pared {meta['pared_s']:.0f} s; "
          f"predicciones sha256 {meta['predicciones_sha256']}")
    if a.comparar and not (meta["comparacion"]["predicciones_identicas"] and meta["comparacion"]["metricas_identicas"]
                          and meta["comparacion"]["metricas_limpias_identicas"]):
        print("banco_walkforward: la repeticion NO coincide con la referencia")
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Banco walk-forward TS-00-BENCH.")
    ap.add_argument("--selftest", action="store_true", help="prueba sin red ni datos reales")
    ap.add_argument("--dataset", help="preset congelado: TI-02-DATA (antiguos) o TI-02-DATA-V2 (MT5)")
    ap.add_argument("--out", metavar="DIR", help="subdirectorio de E:/quantdesk-lab/runs/TS-00-BENCH")
    ap.add_argument("--modelos", default=",".join(MODELOS))
    ap.add_argument("--activos", default="", help="lista separada por comas (por defecto, todos)")
    ap.add_argument("--max-origenes", type=int, default=0, help="primeros N origenes por activo (0 = todos)")
    ap.add_argument("--cada", type=int, default=1, help="uno de cada N origenes validos por activo (submuestra)")
    ap.add_argument("--solo-limpia", action="store_true", help="origen > 2025-08-27T00:00Z tras --cada, antes de --max-origenes")
    ap.add_argument("--fincast-timeout", type=float, default=600.0, metavar="SEG", help="timeout por peticion FinCast (600 s)")
    ap.add_argument("--semilla", type=int, default=None)
    ap.add_argument("--hilos", type=int, default=2, help="hilos de torch para Chronos-2")
    ap.add_argument("--reanudar", action="store_true", help="reutiliza out/pred/<activo>.parquet ya escritos")
    ap.add_argument("--comparar", metavar="RUN", help="compara las predicciones con las de otra corrida")
    ap.add_argument("--informe", nargs="+", metavar="RUN", help="genera informe.md y metricas.csv desde corridas")
    ap.add_argument("--repeticion", nargs="*", metavar="RUN", help="corridas de repeticion (con --comparar)")
    ap.add_argument("--toto", nargs="*", metavar="RUN", help="corridas de Toto (--modelos toto) para el informe")
    ap.add_argument("--fincast", nargs="*", metavar="RUN", help="corridas FinCast para tabla limpia comun con las bases")
    ap.add_argument("--pilotos", nargs="*", metavar="RUN", help="corridas piloto de medida de CPU para el informe")
    ap.add_argument("--destino", metavar="DIR", help="directorio del informe")
    a = ap.parse_args(argv)
    if a.selftest:
        from banco_walkforward_lib import pruebas

        return pruebas.selftest()
    if a.informe:
        from banco_walkforward_lib import informe

        try:
            destino = rutas.validar_destino_informe(a.destino or "")
        except rutas.RutaNoAutorizada as exc:
            print(f"banco_walkforward: {exc}")
            return 2
        return informe.escribir(a.informe, a.repeticion, destino, a.pilotos, a.toto, a.fincast)
    if not (a.dataset and a.out):
        ap.error("--selftest, --informe o bien --dataset y --out")
    from banco_walkforward_lib import banco

    if a.semilla is None:
        a.semilla = banco.SEMILLA
    if a.cada < 1 or a.max_origenes < 0 or not 0 < a.fincast_timeout < float("inf"):
        ap.error("--cada >= 1, --max-origenes >= 0 y --fincast-timeout positivo y finito")
    return cmd_correr(a)


if __name__ == "__main__":
    raise SystemExit(main())
