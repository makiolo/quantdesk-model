"""OC-03 offline: dos custom/v1 (opciones_cruda, opciones_limpia) con hash.

Uso: .venv/Scripts/python -X utf8 scripts/archivo_opciones.py --volcado DIR
  --corte 2026-11-14T06:00:00Z --nombre opciones_c20261114
Rango por defecto: --desde/--hasta del manifest de descarga. --corte limita
captured_at y su disponibilidad redondeada hacia arriba a ms; no simula
la recepcion historica en qn. Esta ultima se conserva en el payload crudo.
--calendario JSON permite ampliar la vigencia del calendario explicito.
Sin sobrescritura: cada nombre identifica una congelacion nueva.
--selftest usa fixtures y qn falso en proceso, sin sockets ni credenciales.
El filtro completo, sus tolerancias y la politica de retiro estan en
archivo_opciones_lib/lector.py y en cada informe generado.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import platform
import re
import sys
import tempfile

sys.dont_write_bytecode = True

from descarga_opciones import cargar_json, guardar_json, json_texto, sha256
from archivo_opciones_lib import lector as L

DATASETS = Path("E:/quantdesk-lab/datasets/TI-09-ARCH")
TMP = Path("E:/quantdesk-lab/tmp/TI-09-ARCH")


def frame_custom(filas, tipo):
    import pandas as pd
    from exportar_market_history_lib import formato as F
    registros = []
    for original, payload in filas:
        registros.append({"instrument": L.instrumento(original), "custom_type": tipo,
                          "schema_version": 1, "ts_ms": (L.fecha(original["date"]) - L.fecha("1970-01-01")).days * L.MS_DIA,
                          "data_json": json_texto(payload),
                          "available_at_ms": (original["captured_at"] + 999999) // 1000000, "revision": 0})
    if not registros:
        return F.vacia("custom/v1")
    df = pd.DataFrame(registros).sort_values(["ts_ms", "instrument"], kind="mergesort").reset_index(drop=True)
    for c in F.columnas_de("custom/v1"):
        df[c["name"]] = df[c["name"]].astype({"Utf8": object, "Int64": "Int64", "Int32": "int32"}[c["type"]])
    return df


def codigo_sha256():
    scripts = Path(__file__).resolve().parent
    rutas = [scripts / "archivo_opciones.py", scripts / "descarga_opciones.py",
             scripts / "archivo_opciones_lib/lector.py", scripts / "exportar_market_history_lib/formato.py",
             scripts / "exportar_market_history_lib/validacion.py"]
    return {p.relative_to(scripts).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in rutas}


def informe_markdown(rep):
    lineas = ["# TI-09-ARCH — instantanea OC-03", "", f"Dataset SHA-256: `{rep['dataset_sha256']}`.",
              f"Corte: `{rep['corte']}`; semilla: 0 (sin aleatoriedad); motor: {L.MOTOR}; lector: {L.VERSION}.",
              "ts_ms = 00:00 UTC de date (sesion NY); available_at_ms = ceil(captured_at_ns/1e6).",
              "Corte sobre captured_at, sin reconstruir el estado de recepcion del lago; _recv_ts se conserva.",
              "", "## Seleccion", rep["regla_universo_captura"],
              "Desempate: mas subyacentes; despues max captured_at; despues capture_id lexicografico mayor.",
              "El universo de /latest puede sufrir sesgo de supervivencia; no conocemos la lista del run.",
              "", "| Sesion | Captura | Motivo |", "|---|---|---|"]
    for c in rep["capturas"]:
        lineas.append(f"| {c['sesion']} | {c['capture_id'] or 'sin captura valida'} | {c['motivo']} |")
    lineas += ["", "## Calendario NYSE declarado", "```json", json_texto(rep["calendario"]), "```",
               "", "## Filtro", L.FILTRO, "", "## Exclusiones", "```json", json_texto(rep["exclusiones_limpieza"]), "```",
               "Descartes de lectura: " + json_texto(rep["descartes_lector"]),
               "Descartes del descargador: " + json_texto(rep["descartes_descarga"]),
               "Lista cerrada de motivos de limpieza: " + ", ".join(L.MOTIVOS) + ".",
               "Cada contrato crudo excluido tiene exactamente una entrada en exclusiones_contratos de informe.json.",
               "", "## Huecos por subyacente y asset_type", rep["universo_huecos"],
               "| Symbol | Asset type | Dias habiles sin datos |", "|---|---|---|"]
    for h in rep["huecos_por_subyacente"]:
        lineas.append(f"| {h['symbol']} | {h['asset_type']} | {', '.join(h['sesiones_sin_datos']) or 'ninguno'} |")
    lineas += ["", "^VIX: underlying_price es spot del indice, sin tratamiento especial ni respaldo.",
               "No se compara spot float32 por igualdad con otros precios. volume=0 no se usa en filtros.",
               "implied_vol=0 y last_price=0 pasan a null en limpia; cruda conserva el valor publicado.",
               "Validacion data_py: hashes, esquema, disponibilidad por fila y politica feed: ok.",
               "Calendario, candidatas, coberturas, universo explicito y trazabilidad: informe.json."]
    return "\n".join(lineas) + "\n"


def archivar(volcado, corte, nombre, desde=None, hasta=None, calendario=None, raiz=DATASETS):
    from exportar_market_history_lib import formato as F
    from exportar_market_history_lib import validacion as V
    import pyarrow
    import pandas

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", nombre) or nombre in (".", ".."):
        raise ValueError("nombre de dataset invalido")
    destino = Path(raiz) / nombre
    # Tambien en llamadas internas: nunca sobrescribir un dataset existente.
    if destino.exists():
        raise FileExistsError("dataset ya existe; elegir nombre nuevo")
    m, rows, manifest_sha = L.cargar_volcado(volcado)
    desde = L.fecha(desde or m["desde"])
    hasta = L.fecha(hasta or m["hasta"])
    if desde < L.INICIO or desde > hasta or desde < L.fecha(m["desde"]) or hasta > L.fecha(m["hasta"]):
        raise ValueError("rango solicitado fuera del volcado o anterior a OC-03")
    consulta_desde = L.fecha(m["consulta_desde"])
    if consulta_desde > L.fecha(m["desde"]) or consulta_desde < L.INICIO:
        raise ValueError("consulta_desde incompatible")
    corte_ns = L.ns_corte(corte)
    cal, sessions = L.calendario_validado(calendario or L.CALENDARIO, consulta_desde, hasta)
    raw, rep = L.seleccionar(rows, desde, hasta, corte_ns, consulta_desde, sessions)
    limpia, ledger = L.limpiar(raw)
    cruda = [(r, {k: v for k, v in r.items() if k != "_tipo"}) for r in raw]
    tablas = [{"table_id": tipo, "schema": "custom/v1", "frame": frame_custom(filas, "market.options.chain." + tipo)}
              for tipo, filas in (("opciones_cruda", cruda), ("opciones_limpia", limpia))]
    TMP.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="construccion_", dir=TMP) as temporal:
        staging = Path(temporal) / nombre
        manifest = F.escribir_dataset(str(staging), nombre, f"OC-03; corte {corte}; {L.VERSION}; {L.MOTOR}; semilla 0",
                                      "America/New_York", tablas)
        dataset_sha = L.hash_dataset(manifest["tables"])
        val = V.validar(str(staging), temporal, nombre, manifest["tables"], corte_ns // 1000000, dataset_sha)
        if not val["ok"] or not val["politica"]["ok"]:
            raise ValueError("data_py no valida el dataset: " + json_texto(val["problemas"]))
        # No conservar rutas temporales aleatorias en el informe congelado.
        val.pop("llamadas", None)
        rep.update({"schema": "ti-09-arch.informe/v1", "dataset_sha256": dataset_sha, "corte": corte,
                    "corte_ns": corte_ns, "desde": str(desde), "hasta": str(hasta), "semilla": 0,
                    "version_lector": L.VERSION, "motor": L.MOTOR,
                    "versiones": {"python": platform.python_version(), "pyarrow": pyarrow.__version__, "pandas": pandas.__version__},
                    "volcado_manifest_sha256": manifest_sha, "codigo_sha256": codigo_sha256(),
                    "calendario": cal, "filtro": L.FILTRO, "motivos_cerrados": list(L.MOTIVOS),
                    "descartes_descarga": m.get("descartadas", {}), "avisos_descarga": m.get("avisos", []),
                    "filas_cruda": len(raw), "filas_limpia": len(limpia), "tablas": manifest["tables"],
                    "exclusiones_limpieza": {m: Counter(e["motivo"] for e in ledger)[m] for m in L.MOTIVOS},
                    "exclusiones_contratos": ledger, "validacion": val,
                    "semantica_corte": "captured_at y ceil ms <= corte; no se filtra por recepcion en qn"})
        guardar_json(staging / "informe.json", rep)
        (staging / "informe.md").write_text(informe_markdown(rep), encoding="utf-8", newline="\n")
        guardar_json(staging / "checksums.json", {"dataset_sha256": dataset_sha,
                     "ficheros_sha256": {p.name: sha256(p) for p in sorted(staging.iterdir())}})
        Path(raiz).mkdir(parents=True, exist_ok=True)
        staging.rename(destino)
    return destino, rep


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--volcado")
    ap.add_argument("--corte")
    ap.add_argument("--nombre")
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    ap.add_argument("--calendario", help="JSON: desde, hasta, holidays explicitos; sessions opcional")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        from archivo_opciones_lib.selftests import selftest
        selftest()
        return 0
    try:
        if not all((a.volcado, a.corte, a.nombre)):
            raise ValueError("faltan --volcado, --corte o --nombre")
        cal = cargar_json(Path(a.calendario).read_text(encoding="utf-8")) if a.calendario else None
        destino, rep = archivar(a.volcado, a.corte, a.nombre, a.desde, a.hasta, cal)
        print(f"dataset {destino}; SHA-256 {rep['dataset_sha256']}; cruda={rep['filas_cruda']}, limpia={rep['filas_limpia']}")
        print("informe.md SHA-256 " + sha256(destino / "informe.md"))
        return 0
    except (ValueError, KeyError, OSError, RuntimeError) as e:
        print("archivo_opciones: " + str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
