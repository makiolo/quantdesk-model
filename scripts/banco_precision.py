"""Banco de precision emulado (TS-00-PREC): fp8 e4m3/e5m2, bf16, f16 y f32 frente a f64 en CPU.

Uso, con el venv del laboratorio:
  .venv/Scripts/python -X utf8 scripts/banco_precision.py --selftest
  .venv/Scripts/python -X utf8 scripts/banco_precision.py --out E:/quantdesk-lab/runs/TS-00-PREC/completo
  .venv/Scripts/python -X utf8 scripts/banco_precision.py --informe DIR     (regenera informe.md desde DIR/resultados.json)
  .venv/Scripts/python -X utf8 scripts/banco_precision.py --verificar DIR   (hash canonico y cifras del informe)

--out ejecuta el banco completo (medidas 1-3 de PLAN_TSFM_FINANZAS 4.5 sobre un transformer pequeno y sobre el
paso cono -> sigma_loc), escribe resultados.json (+ .sha256), informe.md y los pesos entrenados en DIR, que debe
ser un subdirectorio de E:/quantdesk-lab/runs/TS-00-PREC/. --informe escribe DIR/informe.md y solo acepta un
subdirectorio de esa misma ruta o docs/plans/current/execution/TS-00-PREC/ del repositorio; cualquier otra ruta
sale con error (codigo 2) sin escribir nada. Solo CPU, sin red; el redondeo se emula con ml_dtypes (la acumulacion
interna sigue en f64: TS-00-PREC en hardware real lo corrige). Las medidas 4-5 (entrenamiento, mezclas) y la delta
por AAD quedan fuera.
"""
from __future__ import annotations

import os
import sys

HILOS = 1
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = str(HILOS)

import argparse  # noqa: E402
import shutil  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from banco_precision_lib import rutas  # noqa: E402

RUNS = rutas.RUNS
C_MIN_GB = 2.0


def espacio_c_ok() -> bool:
    """La ficha exige parar si C: tiene menos de 2 GB libres. Si no se puede medir, no bloquea."""
    try:
        libre = shutil.disk_usage("C:/").free / 2**30
    except OSError:
        return True
    if libre < C_MIN_GB:
        print(f"banco_precision: C: tiene {libre:.2f} GB libres (< {C_MIN_GB} GB): PARO")
        return False
    return True


def cmd_out(out: str, perfil: str) -> int:
    from banco_precision_lib import banco, informe

    try:
        out = rutas.validar_out(out)
    except rutas.RutaNoAutorizada as exc:
        print(f"banco_precision: {exc}")
        return 2
    if not espacio_c_ok():
        return 3
    os.makedirs(out, exist_ok=True)
    assert banco.HILOS == HILOS, "HILOS de banco_precision.py y de banco.py deben coincidir"
    comando = ".venv/Scripts/python -X utf8 scripts/banco_precision.py --out " + out.replace(os.sep, "/")
    if perfil != "completo":
        comando += f" --perfil {perfil}"
    doc = banco.ejecutar(perfil, out, comando)
    h = banco.escribir_resultados(doc, out)
    informe.escribir_informe(out)
    print(f"resultados.json sha256 canonico: {h}")
    print(f"tiempo de pared: {doc['meta']['tiempo_pared_s']} s; informe: {os.path.join(out, 'informe.md')}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Banco de precision emulado (TS-00-PREC).")
    ap.add_argument("--selftest", action="store_true", help="prueba rapida con aserciones reales")
    ap.add_argument("--out", metavar="DIR", help="ejecuta el banco y escribe resultados.json + informe.md en DIR")
    ap.add_argument("--perfil", choices=("completo", "mini"), default="completo", help="mini es solo para pruebas")
    ap.add_argument("--informe", metavar="DIR", help="regenera DIR/informe.md desde DIR/resultados.json")
    ap.add_argument("--verificar", metavar="DIR", help="recalcula el hash canonico y compara el informe con el JSON")
    a = ap.parse_args(argv)
    n = sum(bool(x) for x in (a.selftest, a.out, a.informe, a.verificar))
    if n != 1:
        ap.error("exactamente una de --selftest, --out, --informe, --verificar")
    if a.selftest:
        from banco_precision_lib import pruebas

        return pruebas.selftest()
    if a.out:
        return cmd_out(a.out, a.perfil)
    from banco_precision_lib import informe

    if a.informe:
        try:
            destino = rutas.validar_informe(a.informe)
        except rutas.RutaNoAutorizada as exc:
            print(f"banco_precision: {exc}")
            return 2
        informe.escribir_informe(destino)
        print(f"informe regenerado en {os.path.join(destino, 'informe.md')}")
        return 0
    return informe.verificar(a.verificar)


if __name__ == "__main__":
    raise SystemExit(main())
