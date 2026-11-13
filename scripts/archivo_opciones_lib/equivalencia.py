"""Diferencial offline del fixture contra el commit fba4279, en procesos separados."""
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.dont_write_bytecode = True

import argparse
from datetime import date
import json
import subprocess
import tempfile
from descarga_opciones import Cliente, INICIO, QnFalso, descargar, guardar_json
from archivo_opciones_lib.selftests import fixture_realista


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="fba4279")
    a = ap.parse_args()
    raiz = Path(tempfile.mkdtemp(prefix="equivalencia_c2_", dir="E:/quantdesk-lab/tmp/TI-09-ARCH"))
    baseline = raiz / "baseline"
    baseline.mkdir()
    for nombre in ("archivo_opciones.py", "descarga_opciones.py", "archivo_opciones_lib/__init__.py", "archivo_opciones_lib/lector.py",
                   "exportar_market_history_lib/__init__.py", "exportar_market_history_lib/formato.py", "exportar_market_history_lib/validacion.py"):
        contenido = subprocess.check_output(["git", "show", f"{a.base}:scripts/{nombre}"], cwd=REPO)
        ruta = baseline / nombre
        ruta.parent.mkdir(exist_ok=True)
        ruta.write_bytes(contenido)
    dump = raiz / "volcado"
    qn = QnFalso(fixture_realista())
    descargar(Cliente("http://fixture.invalid/qn", qn.token, abrir=qn.abrir, espera=0), INICIO, date(2026, 11, 27), dump)
    for etiqueta, scripts in (("base", baseline), ("nuevo", REPO / "scripts")):
        codigo = ("import sys; from pathlib import Path; from unittest.mock import patch; "
                  f"sys.path[:0] = [{str(scripts)!r}, {str(REPO / 'scripts')!r}]; "
                  "import archivo_opciones as A; "
                  "prohibida=patch('socket.socket',side_effect=AssertionError('red prohibida')); prohibida.start(); "
                  f"A.archivar({str(dump)!r}, '2026-11-28T06:00:00Z', 'fixture_equivalencia', raiz=Path({str(raiz / etiqueta)!r}))")
        subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", codigo], check=True, cwd=REPO)
    import pyarrow.parquet as pq
    dirs = [raiz / etiqueta / "fixture_equivalencia" for etiqueta in ("base", "nuevo")]
    informes = [json.loads((d / "informe.json").read_text(encoding="utf-8")) for d in dirs]
    salida = {"base": a.base, "fixture": str(dump), "dataset_sha256_base": informes[0]["dataset_sha256"],
              "dataset_sha256_nuevo": informes[1]["dataset_sha256"], "tablas": {}}
    for tabla in ("opciones_cruda", "opciones_limpia"):
        contenido = [pq.read_table(d / (tabla + ".parquet")).to_pylist() for d in dirs]
        assert contenido[0] == contenido[1], tabla
        salida["tablas"][tabla] = {"filas": len(contenido[0]), "identicas_fila_a_fila": True}
    assert informes[0]["dataset_sha256"] == informes[1]["dataset_sha256"]
    for campo in ("exclusiones_contratos", "descartes_lector", "capturas", "huecos_por_subyacente"):
        assert informes[0][campo] == informes[1][campo], campo
    salida.update(sha256_identico=True, motivos_identicos=True, capturas_y_huecos_identicos=True)
    guardar_json(raiz / "resultado.json", salida)
    print(json.dumps(salida, ensure_ascii=False))
    print("equivalencia ok; evidencia " + str(raiz / "resultado.json"))


if __name__ == "__main__":
    main()
