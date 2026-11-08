"""Genera filtro.md e informe.md a partir de los manifiestos (las cifras no se escriben a mano)."""
from __future__ import annotations

import glob
import os

from . import common as C
from . import fuentes as F
from . import licencias as L
from . import registro as R

COMANDO = [
    ".venv/Scripts/python -X utf8 scripts/ingesta_publica.py licencias",
    ".venv/Scripts/python -X utf8 scripts/ingesta_publica.py descargar",
    ".venv/Scripts/python -X utf8 scripts/ingesta_publica.py procesar --corte {corte}",
    ".venv/Scripts/python -X utf8 scripts/ingesta_publica.py informe",
    ".venv/Scripts/python -X utf8 scripts/ingesta_publica.py --verificar",
]


def _gb(b: int) -> str:
    return f"{b / 1e9:.3f} GB"


def _mb(b: int) -> str:
    return f"{b / 1e6:.1f} MB"


def cargar_manifiestos() -> dict:
    return {os.path.basename(os.path.dirname(p)): C.leer_json(p) for p in sorted(glob.glob(C.DATASETS + "/*/manifest.json"))}


def escribir(ruta: str, lineas: list) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lineas) + "\n")


def filtro_md(mans: dict, resumen: dict, lic: dict) -> list:
    corte = resumen["corte"]
    L_ = ["# TI-13-PUB: informe del filtro de fugas D-11", "",
          f"- `--corte`: **{corte}** (UTC, 00:00). Lo anterior va a `tronco`, lo posterior a `adaptadores`. Provisional (decision de la raiz): "
          "se reaplica sobre lo crudo con `procesar --corte AAAA-MM-DD` sin volver a descargar.",
          f"- Sal de la particion: `{resumen['sal']}`; fraccion de validacion: {resumen['fraccion_val']:.0%} de las series (por hash SHA-256 del id).",
          "- Regla D-11 (PLAN_TSFM_FINANZAS, 2026-11-07): tronco sin datos reales con fecha; lo real solo en adaptadores.", "",
          "## Criterio de financiera y de fechas fiables", "", R.CRITERIO_D11, ""]
    cols = ["dataset", "clase", "series", "financieras", "excl. sin fechas verificables", "excl. fechas imposibles", "vacias",
            "cortadas", "solo antes", "solo despues", "no financieras intactas", "puntos tronco", "puntos adaptadores",
            "puntos excluidos", "quitados del tronco por el corte", "NaN"]
    L_ += ["## Cifras por dataset", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    tot = {k: 0 for k in cols[2:]}
    for did, m in mans.items():
        f = m["filtro"]
        fila = [f["series_total"], f["series_financieras"], f["excluidas_sin_fechas_verificables"], f["excluidas_fechas_imposibles"],
                f["series_vacias"], f["cortadas"], f["financieras_solo_antes"], f["financieras_solo_despues"],
                f["no_financieras_intactas"], f["puntos_tronco"], f["puntos_adaptadores"], f["puntos_excluidos"],
                f["puntos_quitados_del_tronco_por_corte"], f["puntos_nan"]]
        for k, v in zip(cols[2:], fila):
            tot[k] += v
        L_.append(f"| {did} | {m['clase_d11']} | " + " | ".join(f"{v:,}" for v in fila) + " |")
    L_.append("| **total** | | " + " | ".join(f"**{tot[k]:,}**" for k in cols[2:]) + " |")
    L_ += ["", "Filtro por dominio de cada serie: la unica config con dominio por serie (`autogluon/chronos_datasets` `m4_daily`/`m4_monthly`, "
           "columna `category`) esta excluida por licencia y no se descargo; el filtro serie a serie (`es_financiera` con `dominio_col`) solo "
           "se ejercita en el selftest. Los M4/M3/M1 de LOTSA no traen dominio por serie y cuentan como financieros enteros.", "",
           "Notas: `solo antes` = financiera con fechas reales entera anterior al corte (pasa al tronco intacta); `solo despues` = entera "
           "posterior (va a adaptadores); `cortadas` = cruza el corte (prefijo al tronco, resto a adaptadores). En datasets `real` "
           "(cripto) todo va a adaptadores.", "", "## Detalle de la deteccion por dataset", "",
           "| dataset | dominio | clase | criterio de deteccion | fechas | evidencia de fechas | rango observado (UTC) |", "|---|---|---|---|---|---|---|"]
    for did, m in mans.items():
        rng = m["filtro"]["rango_ts_utc"]
        L_.append(f"| {did} | {m['dominio']} | {m['clase_d11']} | {m['motivo_clase']} | {m['fechas'] or '-'} | "
                  f"{m['fechas_evidencia'] or '-'} | {rng[0] or '-'} a {rng[1] or '-'} |")
    sin = [d for d, v in lic["datasets"].items() if v["estado"] != "verificada"]
    L_ += ["", "## Datasets no procesados por licencia (no se descargaron)", ""]
    L_ += [f"- `{d}`: {lic['datasets'][d]['motivo']}." for d in sin] or ["- (ninguno)"]
    p, q = resumen["particion"], resumen["particion"]["en_parquet"]
    L_ += ["", "## Validacion disjunta de entrenamiento", "",
           f"Particion determinista por `series_id` (`{{dataset}}/{{id}}`): SHA-256(sal + id) -> uniforme en [0,1); `val` si < {resumen['fraccion_val']}. "
           "Las series que comparten contenido (hash SHA-256 de sus valores) forman un componente y van al mismo lado, de modo que ningun "
           "`series_id` ni contenido identico aparece a ambos lados, tampoco entre datasets. La comprobacion se hace sobre el plan y, de "
           "nuevo, releyendo los parquet escritos.", "",
           f"- Plan: {p['series']:,} series con contenido, {p['contenidos_distintos']:,} contenidos distintos; contenidos en ambos lados: **{p['contenidos_en_ambos_lados']}**.",
           f"- Parquet releidos ({q['filas_releidas']:,} filas): {q['series_train']:,} series en train y {q['series_val']:,} en val; "
           f"`series_id` en ambos lados: **{q['ids_en_ambos_lados']}**; contenidos identicos en ambos lados: **{q['contenidos_en_ambos_lados']}**.",
           f"- Componentes con duplicados de contenido: {resumen['duplicados']['componentes_con_duplicados']:,}; mayor componente: {resumen['duplicados']['mayor_componente']:,} series.", "",
           "| dataset | series tronco | series adaptadores | filas train | filas val | series val (tronco+adapt.) |", "|---|---|---|---|---|---|"]
    for did, m in mans.items():
        tr = sum(x["filas"] for x in m["ficheros"] if x["split"] == "train")
        va = sum(x["filas"] for x in m["ficheros"] if x["split"] == "val")
        sv = sum(x["series"] for x in m["ficheros"] if x["split"] == "val")
        L_.append(f"| {did} | {m['series']['tronco']:,} | {m['series']['adaptadores']:,} | {tr:,} | {va:,} | {sv:,} |")
    sin_val = [d for d, m in mans.items() if m["ficheros"] and not any(x["split"] == "val" for x in m["ficheros"])]
    L_ += ["", "Datasets con series pero sin ninguna en val (la particion es por serie, como pide la ficha, y los datasets de pocas "
           "series pueden quedarse sin lado val): " + (", ".join(f"`{d}`" for d in sin_val) or "ninguno") + "."]
    c = resumen.get("csv")
    L_ += ["", "## Lista completa de series afectadas", ""]
    if c:
        L_.append(f"CSV fuera de Git (series excluidas, cortadas o movidas enteras a adaptadores): `{c['ruta']}`; {c['filas']:,} filas, "
                  f"{_mb(c['bytes'])}, SHA-256 `{c['sha256']}`. Columnas: dataset, series_id, accion, motivo, puntos, puntos_tronco, puntos_adaptadores.")
    return L_


def informe_md(mans: dict, resumen: dict, lic: dict, corte: str) -> list:
    esp = C.leer_json(F.ESPACIO, [])
    desc = C.leer_json(F.DESCARGAS, {})
    usado = F.bytes_en_manifiestos()
    cache = C.bytes_cache_hf()
    raw = {**F.manifiesto_crudo(F.RAW_HF)["archivos"], **F.manifiesto_crudo(F.RAW_BINANCE)["archivos"]}
    bytes_crudo = sum(e["bytes"] for e in raw.values())
    bytes_proc = sum(f["bytes"] for m in mans.values() for f in m["ficheros"])
    primer = next(iter(mans.values()), None)
    ver = primer["versiones"] if primer else {}
    L_ = ["# TI-13-PUB: informe de ingesta publica", "",
          f"- Generado: {C.ahora_utc()} (UTC). `--corte`: **{corte}**. Sal/semilla de la particion: `{R.SAL}` (val {R.FRAC_VAL:.0%}).",
          f"- Versiones: python {ver.get('python')}, pyarrow {ver.get('pyarrow')}, pandas {ver.get('pandas')}, numpy {ver.get('numpy')}, "
          f"huggingface-hub {ver.get('huggingface_hub')}. Motor del entorno: {C.MOTOR} (commit `{C.MOTOR_COMMIT}`; no se usa en esta ingesta).",
          f"- Revisiones fijadas del Hub: chronos_datasets `{lic['revisiones']['chronos']}`, lotsa_data `{lic['revisiones']['lotsa']}`.",
          "- Formato procesado (provisional hasta TI-03-FMT): parquet zstd, columnas `series_id` (str, `dataset/id`), `ts` (timestamp ms UTC), "
          "`value` (float64; en cripto = cierre) y, en cripto, `open, high, low, close, volume, quote_volume, n_trades`. Un fichero por "
          "`<parte>.<split>.parquet` (parte = `tronco` o `adaptadores`; split = `train` o `val`) y un `manifest.json` por dataset.", "",
          "## Comandos para reproducir", "", "```"] + [c.format(corte=corte) for c in COMANDO] + ["```", "",
          "Los datasets y manifiestos estan en `E:/quantdesk-lab/datasets/TI-13-PUB/<dataset>/`; lo crudo, en `E:/quantdesk-lab/data/public/`.", "",
          "## Espacio", "",
          f"- Usado por TI-13-PUB (bytes de los manifiestos): **{_gb(usado)}** de 100 GB (crudo {_gb(bytes_crudo)} + procesado {_gb(bytes_proc)}); "
          f"cache de huggingface_hub (scan_cache_dir): {_gb(cache)}.", "",
          "| fuente | fase | UTC | libre C: | libre E: | usado manifiestos | cache HF |", "|---|---|---|---|---|---|---|"]
    for e in esp:
        L_.append(f"| {e['fuente']} | {e['fase']} | {e['fecha_utc']} | {_gb(e['libre_C_bytes'])} | {_gb(e['libre_E_bytes'])} | "
                  f"{_gb(e['usado_manifiestos_bytes'])} | {_gb(e.get('cache_hf_bytes', 0))} |")
    L_ += ["", "## Datasets obtenidos", "",
           "| dataset | fuente | series (tronco / adaptadores) | puntos tronco / adaptadores | rango (UTC) | frecuencia | bytes crudo | bytes procesado | descarga (UTC) | SHA-256 del dataset |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for did, m in mans.items():
        f, rng = m["filtro"], m["filtro"]["rango_ts_utc"]
        bc = sum(c["bytes"] for c in m["crudo"])
        bp = sum(x["bytes"] for x in m["ficheros"])
        L_.append(f"| {did} | {m['fuente']} | {m['series']['tronco']:,} / {m['series']['adaptadores']:,} | {f['puntos_tronco']:,} / "
                  f"{f['puntos_adaptadores']:,} | {rng[0] or '-'} a {rng[1] or '-'} | {m['frecuencia']} | {_mb(bc)} | {_mb(bp)} | "
                  f"{m['fecha_descarga_utc']} | {'`' + m['dataset_sha256'][:16] + '...`' if m['ficheros'] else '- (todas las series excluidas)'} |")
    L_ += ["", "Hash de dataset = SHA-256 de las lineas `ruta<TAB>sha256` ordenadas de sus parquet (manifiesto ordenado); el valor completo y el "
           "`contenido_sha256` (hash por serie, ordenado) estan en cada `manifest.json`.", "",
           "## Calidad de los datos (se cuenta, no se corrige)", "",
           "| dataset | series vacias | ids duplicados | duplicados de contenido | series con marcas irregulares/huecos | series con fechas invalidas | puntos NaN | duplicados Binance | huecos Binance |",
           "|---|---|---|---|---|---|---|---|---|"]
    for did, m in mans.items():
        f = m["filtro"]
        L_.append(f"| {did} | {f['series_vacias']:,} | {f['ids_duplicados']:,} | {f['duplicados_de_contenido']:,} | {f['series_irregulares']:,} | "
                  f"{f['series_fechas_invalidas']:,} | {f['puntos_nan']:,} | {f['duplicados_binance']:,} | {f['huecos_binance']:,} |")
    L_ += ["", "## Hashes SHA-256 por fichero", "", "### Procesados (parquet)", "", "| dataset | fichero | filas | bytes | SHA-256 |", "|---|---|---|---|---|"]
    for did, m in mans.items():
        for x in m["ficheros"]:
            L_.append(f"| {did} | {x['ruta']} | {x['filas']:,} | {x['bytes']:,} | `{x['sha256']}` |")
    L_ += ["", "### Crudo del Hub", "", "| fichero | bytes | SHA-256 | verificado contra |", "|---|---|---|---|"]
    for k, e in sorted(raw.items()):
        if k.startswith("hf/"):
            L_.append(f"| {k[3:]} | {e['bytes']:,} | `{e['sha256']}` | {e['verificado_contra']} |")
    bz = {k: e for k, e in raw.items() if k.startswith("binance/")}
    if bz:
        L_ += ["", "### Crudo de Binance", "",
               f"{len(bz):,} zip mensuales/diarios ({_mb(sum(e['bytes'] for e in bz.values()))}), cada uno verificado contra su `.CHECKSUM` oficial. "
               f"Lista completa con SHA-256 en `{F.RAW_BINANCE}/raw_manifest.json`; hash del conjunto ordenado "
               f"`{C.hash_conjunto((k, e['sha256']) for k, e in bz.items())}`."]
    L_ += ["", "## No obtenido (con motivo)", ""]
    for fuente, v in lic["fuentes_no_obtenidas"].items():
        L_.append(f"- **{fuente}:** {v['motivo']}")
    for d, v in lic["datasets"].items():
        if v["estado"] != "verificada":
            L_.append(f"- **{d}:** no descargado. {v['motivo']}.")
    for fuente, v in desc.items():
        for clave, motivo in v.get("no_bajados", []):
            if not clave.startswith(tuple(d for d, x in lic["datasets"].items() if x["estado"] != "verificada")):
                L_.append(f"- **{clave}** ({fuente}): {motivo}")
    return L_


def generar(doc_dir: str) -> None:
    lic = L.cargar()
    mans = cargar_manifiestos()
    resumen = C.leer_json(C.INFORMES_FUERA + "/filtro_resumen.json")
    if not (lic and mans and resumen):
        raise RuntimeError("faltan licencias.json, manifiestos o filtro_resumen.json: ejecutar licencias, descargar y procesar")
    L.escribir_md(lic, f"{doc_dir}/licencias.md")
    escribir(f"{doc_dir}/filtro.md", filtro_md(mans, resumen, lic))
    escribir(f"{doc_dir}/informe.md", informe_md(mans, resumen, lic, resumen["corte"]))
