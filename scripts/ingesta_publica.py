"""Ingesta de fuentes publicas con filtro de fugas D-11 (tarea TI-13-PUB, SPRINT-01).

Orden obligatorio: licencias -> descargar -> procesar -> informe. Sin licencia verificada no se descarga.

    .venv/Scripts/python -X utf8 scripts/ingesta_publica.py licencias           # evidencia + veredictos + licencias.md
    .venv/Scripts/python -X utf8 scripts/ingesta_publica.py descargar           # Hub (Chronos, LOTSA) y Binance; reanudable
    .venv/Scripts/python -X utf8 scripts/ingesta_publica.py procesar --corte 2016-10-01   # filtro D-11 + particion train/val
    .venv/Scripts/python -X utf8 scripts/ingesta_publica.py informe             # filtro.md, informe.md (cifras de los manifiestos)
    .venv/Scripts/python -X utf8 scripts/ingesta_publica.py --verificar         # recalcula SHA-256 y reaplica el filtro
    .venv/Scripts/python -X utf8 scripts/ingesta_publica.py --selftest          # sin red

Almacen (fuera de Git, todo bajo E:/quantdesk-lab): data/public/<fuente>/ (crudo), datasets/TI-13-PUB/<dataset>/ (parquet +
manifest.json), runs/TI-13-PUB/ (estado). El filtro se reaplica sobre lo crudo con otro --corte sin volver a descargar.
Solo biblioteca estandar mas lo instalado en el .venv (pyarrow, pandas, numpy, huggingface-hub).
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from setup_env import LAB_ENV  # noqa: E402  (cachés y temporales del laboratorio: HF_HOME, TMPDIR, TEMP...)

os.environ.update(LAB_ENV)  # el sitecustomize del venv ya lo hace; esto cubre un lanzamiento con otro interprete

from ingesta_publica_lib import common as C  # noqa: E402
from ingesta_publica_lib import registro as R  # noqa: E402

DOC_DIR = os.path.join(REPO, "docs", "plans", "current", "execution", "TI-13-PUB")


def cmd_licencias(a) -> int:
    from ingesta_publica_lib import licencias

    estado = licencias.correr(refrescar=a.refrescar, md=os.path.join(DOC_DIR, "licencias.md"))
    n_ok = sum(1 for v in estado["datasets"].values() if v["estado"] == "verificada")
    print(f"licencias: {n_ok} datasets verificados, {len(estado['datasets']) - n_ok} excluidos; "
          f"fuentes no obtenidas: {', '.join(estado['fuentes_no_obtenidas'])}")
    return 0


def _estado_licencias():
    from ingesta_publica_lib import licencias

    estado = licencias.cargar()
    if not estado:
        print("BLOQUEADO: no hay licencias.json; ejecutar primero 'licencias' (sin licencia verificada no se descarga)")
        raise SystemExit(2)
    return estado


def cmd_descargar(a) -> int:
    from ingesta_publica_lib import fuentes

    estado = _estado_licencias()
    for fuente in (["chronos", "lotsa", "binance"] if a.fuente == "todas" else [a.fuente]):
        print(f"descargar: {fuente}")
        try:
            r = fuentes.descargar(fuente, estado)
        except (C.ParadaDisco, C.PresupuestoExcedido) as e:
            print(f"PARADA: {e}")
            return 3
        for clave, motivo in r["omitidos"]:
            print(f"  no bajado {clave}: {motivo}")
    return 0


def cmd_procesar(a) -> int:
    from ingesta_publica_lib import filtro

    estado = _estado_licencias()
    r = filtro.correr(a.corte, estado, C.DATASETS, informes_dir=C.INFORMES_FUERA)
    p = r["resumen"]["particion"]["en_parquet"]
    print(f"procesar: {len(r['manifiestos'])} datasets, corte {a.corte}; en los parquet escritos: series_id en train y val "
          f"{p['ids_en_ambos_lados']}, contenidos en train y val {p['contenidos_en_ambos_lados']}")
    return 0


def cmd_informe(a) -> int:
    from ingesta_publica_lib import informes

    informes.generar(DOC_DIR)
    print("informe: licencias.md, filtro.md e informe.md escritos en", DOC_DIR)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orden", nargs="?", choices=["licencias", "descargar", "procesar", "informe", "todo"])
    ap.add_argument("--corte", default=R.CORTE_DEFECTO, help="primer corte de backtest AAAA-MM-DD (filtro D-11)")
    ap.add_argument("--fuente", choices=["chronos", "lotsa", "binance", "todas"], default="todas")
    ap.add_argument("--refrescar", action="store_true", help="licencias: volver a consultar la evidencia")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--solo-hashes", action="store_true", help="--verificar sin reaplicar el filtro")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        from ingesta_publica_lib import selftests

        selftests.correr()
        print("selftest ok")
        return 0
    if a.verificar:
        from ingesta_publica_lib import verificar

        return verificar.correr(solo_hashes=a.solo_hashes)
    if a.orden == "todo":
        for f in (cmd_licencias, cmd_descargar, cmd_procesar, cmd_informe):
            rc = f(a)
            if rc:
                return rc
        return 0
    if a.orden:
        return {"licencias": cmd_licencias, "descargar": cmd_descargar, "procesar": cmd_procesar, "informe": cmd_informe}[a.orden](a)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
