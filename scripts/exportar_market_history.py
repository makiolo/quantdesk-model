"""Exportador a `engine.market-history/v1` (tarea TI-02-DATA, paso 2 de 2). En el .venv, sin red.

Lee el volcado crudo del lago (`descarga_lago.py`, paso 1) y/o los datasets de Binance de TI-13-PUB y escribe un dataset
`engine.market-history/v1` en un punto en el tiempo: tablas parquet con el esquema exacto de `data_py.table_schemas_json()` y su
`manifest.json` con el `logical_hash` de cada una. Despues lo valida con `data_py` (describe con hashes, informe de
disponibilidad y politica de look-ahead sobre el feed).

    .venv/Scripts/python -X utf8 scripts/exportar_market_history.py --binance --corte 2026-11-01 --nombre binance_c20261101
    .venv/Scripts/python -X utf8 scripts/exportar_market_history.py --lago E:/quantdesk-lab/data/lago/AAAA-MM-DD --corte 2026-11-01
    .venv/Scripts/python -X utf8 scripts/exportar_market_history.py --validar binance_c20261101
    .venv/Scripts/python -X utf8 scripts/exportar_market_history.py --informe RUTA.md --datasets binance_c20261101,lago_c20261101
    .venv/Scripts/python -X utf8 scripts/exportar_market_history.py --selftest

Reglas (el detalle y las cifras de cada exportacion quedan en `procedencia.json` del dataset y en el informe):
- Corte: `--corte AAAA-MM-DD` es el instante AAAA-MM-DDT00:00:00Z. Una fila entra solo si su cierre (inicio + intervalo; el
  propio instante en tablas de eventos) y su `available_at_ms` son <= corte; el resto se cuenta y no entra.
- Disponibilidad: por fila. Binance: el cierre de la vela. Lago: max(_recv_ts, _ts + intervalo) en ohlcv (A12),
  `_recv_ts` en performance o `scraped_at_ms` en rates; sin marca queda sin declarar y no es consumible causalmente.
  Con `--disponibilidad-ohlcv cierre` las barras del lago llevan `available_at_ms` nulo y el manifest `default_lag_ms` = 0
  (disponibles al cierre): es un proxy sin campo que lo respalde, el motor las cuenta como `defaulted` y sus valores son la
  version que qn recibio despues del corte. Ese dataset debe llevar `_cierre` en el nombre. En cualquier otro caso
  `default_lag_ms` queda en null.
- Limpieza contada, sin rellenar huecos ni aproximar: nulos, no finitos, precios <= 0, volumen < 0, high < low (se excluyen),
  open/close fuera de [low, high] (se conservan y se cuentan), versiones repetidas de una barra (se queda la primera ya
  cerrada segun la recepcion en qn, salvo MT5 1d: ultima completa recibida hasta el corte), filas posteriores al corte.
- Universo: lo que hay hoy en la fuente, con el sesgo de supervivencia declarado (D-07) en el manifest y en `procedencia.json`.
- Fuentes v2: politica versionada en descarga_lago.py; FX 1d solo mt5, sin regla una sola fuente por simbolo/intervalo.
- Ventana opcional: --desde AAAA-MM-DD excluye y cuenta filas anteriores (por ts_ms); --corte conserva su significado.
- Determinismo: orden estable de filas y tablas, ninguna marca de ejecucion dentro del dataset; dos exportaciones del mismo
  origen y corte dan el mismo `logical_hash` y los mismos bytes.

Almacen (fuera de Git, todo bajo E:/quantdesk-lab): datasets/TI-02-DATA/<nombre>/ (manifest.json, <tabla>.parquet, procedencia.json)
y runs/TI-02-DATA/<nombre>.json (comando, fecha UTC y resultado de la validacion). Salida 0 ok; 1 validacion fallida o datos
inconsistentes; 2 uso incorrecto o BLOQUEADO; 3 PARADA por el suelo de espacio en C:.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import sys
import time
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_env import LAB, LAB_ENV  # noqa: E402  (cachés y temporales del laboratorio)

os.environ.update(LAB_ENV)  # el sitecustomize del venv ya lo hace; esto cubre un lanzamiento con otro interprete

from exportar_market_history_lib import formato as F  # noqa: E402
from exportar_market_history_lib import fuentes as S  # noqa: E402
from exportar_market_history_lib import limpieza as L  # noqa: E402

SALIDA_RAIZ = LAB + "/datasets/TI-02-DATA"
RUNS = LAB + "/runs/TI-02-DATA"
TI13 = LAB + "/datasets/TI-13-PUB"
MOTOR = "quantdesk 69fdb39d"  # rueda de LAB-00-ENV-B (commit 69fdb39d0b67969dbdafa77f5da656511342f175)
SUELO_C_BYTES = 2 * 1024 ** 3
NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def comprobar_disco() -> None:
    """Para (salida 3) si C: tiene menos de 2 GiB libres: el laboratorio no debe llenar el disco del sistema."""
    if os.path.exists("C:/"):
        libre = shutil.disk_usage("C:/").free
        if libre < SUELO_C_BYTES:
            print(f"PARADA: C: tiene {libre / 1024 ** 3:.1f} GiB libres (< 2 GiB)", file=sys.stderr)
            raise SystemExit(3)


def corte_a_ms(corte: str) -> int:
    d = date.fromisoformat(corte)
    return (d - date(1970, 1, 1)).days * 86_400_000


def hash_codigo(raiz: str = HERE) -> dict:
    """SHA-256 del exportador y de los modulos que deciden el contenido del dataset (no los selftests, el informe ni la
    validacion): la procedencia del codigo que lo produjo. Con CRLF normalizado a LF, para que no dependa del checkout."""
    lib = os.path.join(raiz, "exportar_market_history_lib")
    ficheros = [os.path.join(raiz, n) for n in ("exportar_market_history.py", "descarga_lago.py")] + [
        os.path.join(lib, n) for n in ("formato.py", "fuentes.py", "limpieza.py")]
    return {os.path.relpath(f, raiz).replace(os.sep, "/"): F.sha256_codigo(f) for f in ficheros}


def versiones() -> dict:
    import numpy
    import pandas
    import pyarrow

    return {"python": platform.python_version(), "pyarrow": pyarrow.__version__, "pandas": pandas.__version__,
            "numpy": numpy.__version__, "motor": MOTOR}


def hash_dataset(tablas: list[dict]) -> str:
    """Igual que `MarketHistoryManifest::dataset_hash`: sha256 de las lineas `table_id:schema:logical_hash` ordenadas."""
    lineas = sorted(f"{t['table_id']}:{t['schema']}:{t['logical_hash']}\n" for t in tablas)
    return "sha256:" + hashlib.sha256("".join(lineas).encode()).hexdigest()


def describir(origenes: list, corte: str, tablas: list, vistas: list, default_lag_ms: int | None) -> str:
    """Descripcion del manifest: solo depende de lo que entra en el dataset (no de filas posteriores al corte)."""
    proxies = [t for t in tablas if t["disponibilidad"]["tipo"] == "proxy por default_lag_ms"]
    if proxies:
        recibidas = [t["carga"][k] for t in proxies for k in ("recv_ts_primero", "recv_ts_ultimo") if t["carga"][k] is not None]
        rango = f"entre {min(recibidas)} y {max(recibidas)}" if recibidas else "sin recepciones admisibles"
        partes = [f"Exportacion TI-02-DATA ({MOTOR}) con corte {corte}T00:00:00Z. ATENCION, DISPONIBILIDAD PROXY: ninguna fila tiene "
                  "su cierre posterior al corte, pero las tablas ohlcv del lago llevan available_at_ms nulo y default_lag_ms = 0 "
                  "(disponibles al cierre, sin ningun campo que lo respalde) y sus valores son la version de cada barra que qn "
                  f"recibio DESPUES del corte ({rango}), no la visible al cierre. No es causal "
                  "en sentido estricto; el dataset estricto es el que usa _recv_ts."]
        if any(t["table_id"] == "lago_ohlcv_1d" and "mt5" in t["carga"]["source"] for t in proxies):
            partes = [f"Exportacion TI-02-DATA ({MOTOR}) con corte {corte}T00:00:00Z. ATENCION, DISPONIBILIDAD PROXY: "
                      "available_at_ms nulo y default_lag_ms = 0 declaran el cierre nominal sin evidencia de disponibilidad "
                      "al cierre. MT5 1d usa la ultima version completa recibida hasta el corte; otras fuentes e intervalos "
                      "conservan la primera completa, que puede recibirse despues del corte. No es causal en sentido estricto; "
                      "el dataset estricto es el que usa _recv_ts."]
    else:
        partes = [f"Exportacion TI-02-DATA ({MOTOR}) con corte {corte}T00:00:00Z: ninguna fila tiene su cierre ni su "
                  "available_at_ms declarado posteriores al corte."]
    for o in origenes:
        partes.append(f"Fuente {o['nombre']}, licencia: {o['licencia']}. Universo: {o['universo']['texto']}")
    for t, v in zip(tablas, vistas):
        d = t["disponibilidad"]
        revisadas = t["contador"]["detalle"].get("version_mt5_revisada")
        if revisadas:
            finales = set(zip(v["instrument"], v["ts_ms"]))
            afectadas = [r for r in revisadas["pares_y_fechas"] if (r["instrument"], r["ts_ms"]) in finales]
            if afectadas:
                pares = ", ".join(f"{r['instrument']} {S.iso_ms(r['ts_ms'])}" for r in afectadas)
                sustituidas = sum(r["versiones_completas"] - 1 for r in afectadas)
                partes.append(f"version_mt5_revisada: {len(afectadas)} barras, {sustituidas} versiones "
                              f"anteriores sustituidas; pares y fechas: {pares}.")
        partes.append(f"{t['table_id']}: {v['instrument'].nunique()} instrumentos con datos hasta el corte; disponibilidad "
                      f"{d['declarada']}; campo: {d['campo'] or 'ninguno'}"
                      + (", no consumible causalmente." if d["tipo"] == "no declarada" else "."))
        if "seleccion_fuentes" in t["carga"]:
            fuentes_finales = {}
            for s in t["carga"]["seleccion_fuentes"]["series"]:
                n = int((v["instrument"] == s["symbol"]).sum()) if s["admitida"] else 0
                if n:
                    fuentes_finales[s["source"]] = fuentes_finales.get(s["source"], 0) + n
            partes.append(f"{t['table_id']}: fuentes por tag source {dict(sorted(fuentes_finales.items()))}; "
                          f"politica {S.POLITICA_FUENTES['version']}; descartes contados en procedencia.json.")
    partes.append("default_lag_ms nulo: ninguna disponibilidad se inventa." if default_lag_ms is None else
                  f"default_lag_ms = {default_lag_ms} solo por el proxy declarado arriba.")
    partes.append("Huecos y datos descartados contados en procedencia.json.")
    return " ".join(partes)


def resumen_tabla(t: dict, final, entrada: dict) -> dict:
    inst = sorted(final["instrument"].unique().tolist()) if len(final) else []
    ivs = sorted(final["interval_ms"].unique().tolist()) if "interval_ms" in final.columns and len(final) else []
    return {"table_id": t["table_id"], "schema": t["schema"], "filas": int(len(final)), "instrumentos": len(inst),
            "lista_de_instrumentos": inst, "intervalos_ms": [int(x) for x in ivs],
            "primera": S.iso_ms(entrada["ts_min_ms"]) if entrada["ts_min_ms"] is not None else None,
            "ultima": S.iso_ms(entrada["ts_max_ms"]) if entrada["ts_max_ms"] is not None else None,
            "logical_hash": entrada["logical_hash"], "limpieza": t["contador"], "carga": t["carga"],
            "disponibilidad": t["disponibilidad"]}


def exportar(a: argparse.Namespace) -> int:
    from exportar_market_history_lib import validacion as V

    t0 = time.time()
    comprobar_disco()
    try:
        corte_ms = corte_a_ms(a.corte)
        desde_ms = corte_a_ms(a.desde) if a.desde else None
        if desde_ms is not None and desde_ms >= corte_ms:
            raise ValueError("ventana vacia")
    except ValueError:
        print("exportar: --corte y --desde deben ser AAAA-MM-DD y --desde anterior al corte", file=sys.stderr)
        return 2
    if not (a.binance or a.lago):
        print("exportar: indica al menos una fuente (--binance y/o --lago DIR)", file=sys.stderr)
        return 2
    if a.disponibilidad_ohlcv == "cierre" and not a.lago:
        print("exportar: --disponibilidad-ohlcv cierre solo aplica a --lago", file=sys.stderr)
        return 2
    modo = ("cierre" if a.disponibilidad_ohlcv == "cierre" else "recepcion") if a.lago else "no aplica"
    nombre = (a.nombre or "_".join(n for n, on in (("binance", a.binance), ("lago", a.lago)) if on)
              + ("_cierre" if modo == "cierre" else "") + "_c" + a.corte.replace("-", ""))
    if not NOMBRE_VALIDO.match(nombre):
        print(f"exportar: nombre de dataset no valido: {nombre!r}", file=sys.stderr)
        return 2
    if ("_cierre" in nombre) != (modo == "cierre"):  # el proxy y el estricto nunca comparten nombre
        print(f"exportar: el nombre {nombre!r} y --disponibilidad-ohlcv {a.disponibilidad_ohlcv} no casan: un dataset con la "
              "disponibilidad proxy lleva `_cierre` en el nombre y uno estricto no", file=sys.stderr)
        return 2
    destino = os.path.join(a.salida_raiz, nombre)
    if os.path.exists(destino) and not a.sobrescribir:
        print(f"exportar: {destino} ya existe (usa --sobrescribir para rehacerlo)", file=sys.stderr)
        return 2
    if os.path.exists(destino):  # --sobrescribir solo rehace un dataset del mismo modo de disponibilidad
        try:
            with open(os.path.join(destino, "procedencia.json"), encoding="utf-8") as f:
                previo = json.load(f).get("modo_disponibilidad_ohlcv")
        except (OSError, ValueError):
            previo = None
        if previo != modo:
            print(f"exportar: {destino} es de otro modo de disponibilidad ({previo!r}, ahora {modo!r}) o no tiene procedencia.json; "
                  "no se sobrescribe", file=sys.stderr)
            return 2
    try:
        origenes = ([S.cargar_binance(a.ti13)] if a.binance else []) + ([S.cargar_lago(a.lago, a.disponibilidad_ohlcv == "cierre")] if a.lago else [])
    except (ValueError, OSError, KeyError) as e:
        print(f"exportar: BLOQUEADO: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    tablas, vistas = [], []
    for o in origenes:
        for t in o["tablas"]:
            c = t["contador"]
            seleccion = t["carga"].get("seleccion_fuentes")
            if seleccion:
                for s in seleccion["series"]:
                    if not s["admitida"]:
                        print(f"AVISO: {s['symbol']} {s['interval']} source={s['source']}: "
                              f"{s['filas_excluidas_por_fuente']} barras excluidas; solo se admite "
                              f"{s['regla']['source']} ({s['regla']['motivo']})")
                for symbol in sorted({s["symbol"] for s in seleccion["series"]}):
                    ss = [s for s in seleccion["series"] if s["symbol"] == symbol]
                    if any(s["regla"] for s in ss) and not any(s["admitida"] and s["filas_leidas"] for s in ss):
                        print(f"AVISO: {symbol}: sin barras de la fuente exigida; no se usa una fuente alternativa")
            try:
                if desde_ms is not None:
                    t["frame"] = L.quitar(t["frame"], t["frame"]["ts_ms"] < desde_ms, "anterior_al_inicio_de_ventana", c)
                if t["schema"] == "ohlcv/v1":
                    final = L.limpiar_ohlcv(t["frame"], corte_ms, t["duplicados"], c, t["calendario"], t.get("disp_cierre", False))
                else:
                    final = L.limpiar_custom(t["frame"], corte_ms, c)
            except (ValueError, AssertionError) as e:
                print(f"exportar: DATOS INCONSISTENTES en {t['table_id']}: {e}", file=sys.stderr)
                return 1
            t["frame"] = None  # libera el crudo
            tablas.append(t)
            vistas.append(final)
            print(f"  {t['table_id']}: {c['filas_origen']} filas de origen -> {len(final)} "
                  f"({sum(c['excluidas'].values())} excluidas: {c['excluidas'] or 'ninguna'})")
    # default_lag_ms solo se escribe para un proxy declarado; vale para TODAS las filas sin available_at_ms del dataset, asi que
    # ninguna otra tabla puede tenerlas
    default_lag = 0 if any(t.get("disp_cierre") for t in tablas) else None
    if default_lag is not None:
        for t, f in zip(tablas, vistas):
            if not t.get("disp_cierre") and f["available_at_ms"].isna().any():
                print(f"exportar: DATOS INCONSISTENTES en {t['table_id']}: filas sin available_at_ms en un dataset con "
                      "default_lag_ms: se les aplicaria un lag que nadie ha declarado para ellas", file=sys.stderr)
                return 1
    construccion = os.path.join(a.salida_raiz, ".construyendo")
    dir_ds = os.path.join(construccion, nombre)
    shutil.rmtree(dir_ds, ignore_errors=True)
    descripcion = describir(origenes, a.corte, tablas, vistas, default_lag)
    if a.desde:
        descripcion += f" Ventana desde {a.desde}T00:00:00Z (ts_ms inclusivo)."
    entradas = F.escribir_dataset(
        dir_ds, nombre, descripcion, a.zona,
        [{"table_id": t["table_id"], "schema": t["schema"], "frame": f} for t, f in zip(tablas, vistas)], default_lag)["tables"]
    ds_hash = hash_dataset(entradas)
    proc = {
        "esquema": "ti-02-data.procedencia/v1", "dataset_id": nombre, "dataset_hash": ds_hash, "corte": a.corte,
        "corte_utc": a.corte + "T00:00:00Z", "corte_ms": corte_ms, "modo_disponibilidad_ohlcv": modo,
        "default_lag_ms": default_lag,
        "desde": a.desde, "desde_ms": desde_ms,
        "semantica_del_corte": "entra una fila si su cierre (ts_ms + interval_ms; ts_ms en eventos) y su available_at_ms, si lo tiene, son <= corte",
        "zona_horaria_del_mercado": a.zona, "versiones": versiones(), "codigo_sha256": hash_codigo(),
        "origenes": [{"nombre": o["nombre"], "licencia": o["licencia"], "fuente": o["fuente"], "universo": o["universo"]}
                     for o in origenes],
        "tablas": [resumen_tabla(t, f, e) for t, f, e in zip(tablas, vistas, entradas)]}
    F.escribir_json(os.path.join(dir_ds, "procedencia.json"), proc)
    val = V.validar(dir_ds, construccion, nombre, [{"table_id": t["table_id"], "schema": t["schema"]} for t in tablas], corte_ms,
                    ds_hash)
    val["dataset_hash"] = ds_hash
    val["llamadas"] = {k: v.replace("\\", "/").replace("/.construyendo", "") for k, v in val["llamadas"].items()}  # ruta final
    runs = a.runs or RUNS
    os.makedirs(runs, exist_ok=True)
    registro = {"dataset_id": nombre, "fecha_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "comando": ".venv/Scripts/python -X utf8 scripts/exportar_market_history.py " + shlex.join(sys.argv[1:]),
                "duracion_s": round(time.time() - t0, 1), "validacion": val,
                "ficheros_sha256": {n: F.sha256_fichero(os.path.join(dir_ds, n)) for n in sorted(os.listdir(dir_ds))}}
    F.escribir_json(os.path.join(runs, nombre + (".repeticion" if a.repeticion else "") + ".json"), registro)
    if not val["ok"]:
        fallido = os.path.join(a.salida_raiz, ".fallido-" + nombre)
        shutil.rmtree(fallido, ignore_errors=True)
        os.replace(dir_ds, fallido)
        print(f"exportar: VALIDACION FALLIDA ({len(val['problemas'])} problemas), dataset dejado en {fallido}", file=sys.stderr)
        for p in val["problemas"][:20]:
            print(f"  - {p}", file=sys.stderr)
        return 1
    if os.path.exists(destino):
        shutil.rmtree(destino)
    os.replace(dir_ds, destino)
    try:
        os.rmdir(construccion)
    except OSError:
        pass
    imprimir_resumen(destino, proc, val, registro)
    return 0


def imprimir_resumen(destino: str, proc: dict, val: dict, registro: dict) -> None:
    print(f"dataset {proc['dataset_id']} escrito en {destino} ({registro['duracion_s']} s)")
    print(f"  corte {proc['corte_utc']}; dataset_hash {proc['dataset_hash']}")
    for t in proc["tablas"]:
        print(f"  {t['table_id']:22s} {t['schema']:9s} {t['filas']:>9d} filas  {t['instrumentos']:>3d} instrumentos  "
              f"{t['primera']} -> {t['ultima']}  {t['logical_hash']}")
    print(f"  data_py describe: ok con hashes verificados; politica de look-ahead ok={val['politica']['ok']}; "
          f"violaciones por fila={val['lookahead']['violaciones_por_fila']}; "
          f"no consumibles causalmente en sentido estricto: {val['tablas_no_consumibles_causalmente'] or 'ninguna'} "
          f"(de ellas, proxy por default_lag_ms: {val['tablas_proxy'] or 'ninguna'}); "
          f"tablas vacias tras el corte: {val['tablas_vacias'] or 'ninguna'}")


def revalidar(a: argparse.Namespace) -> int:
    from exportar_market_history_lib import validacion as V

    ruta = os.path.join(a.salida_raiz, a.validar)
    with open(os.path.join(ruta, "procedencia.json"), encoding="utf-8") as f:
        proc = json.load(f)
    val = V.validar(ruta, a.salida_raiz, a.validar, [{"table_id": t["table_id"], "schema": t["schema"]} for t in proc["tablas"]],
                    proc["corte_ms"], proc["dataset_hash"])
    val["dataset_hash"] = proc["dataset_hash"]
    print(json.dumps({k: val[k] for k in ("ok", "problemas", "tablas_no_consumibles_causalmente", "lookahead")}, indent=2))
    return 0 if val["ok"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Exportador a engine.market-history/v1 (TI-02-DATA, paso 2).")
    ap.add_argument("--corte", help="fecha de corte AAAA-MM-DD (el instante 00:00:00Z de ese dia)")
    ap.add_argument("--desde", help="inicio inclusivo de ventana por ts_ms, AAAA-MM-DD; por defecto toda la historia")
    ap.add_argument("--binance", action="store_true", help="velas 1d y 1h de Binance de TI-13-PUB")
    ap.add_argument("--ti13", default=TI13, help="raiz de datasets/TI-13-PUB")
    ap.add_argument("--lago", help="directorio del volcado de descarga_lago.py")
    ap.add_argument("--disponibilidad-ohlcv", choices=("recepcion", "cierre"), default="recepcion",
                    help="disponibilidad de las barras del lago: `recepcion` (max(_recv_ts, _ts + intervalo), por defecto) o `cierre` (proxy: "
                         "el cierre de la barra; no lo respalda ningun campo del lago)")
    ap.add_argument("--nombre", help="dataset_id y nombre del directorio (por defecto <fuentes>_c<corte>)")
    ap.add_argument("--salida-raiz", default=SALIDA_RAIZ, help="directorio que contiene los datasets (raiz del FileVendor)")
    ap.add_argument("--runs", help="donde dejar el registro de la ejecucion (por defecto runs/TI-02-DATA)")
    ap.add_argument("--zona", default="UTC", help="zona IANA del mercado para time.zone (por defecto UTC)")
    ap.add_argument("--sobrescribir", action="store_true", help="rehacer un dataset que ya existe")
    ap.add_argument("--repeticion", action="store_true",
                    help="es la segunda exportacion de comprobacion: el registro se guarda como <nombre>.repeticion.json")
    ap.add_argument("--validar", metavar="NOMBRE", help="solo revalidar un dataset ya escrito")
    ap.add_argument("--informe", metavar="RUTA.md", help="escribir el informe Markdown de --datasets")
    ap.add_argument("--datasets", help="nombres separados por comas para --informe")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        from exportar_market_history_lib import selftests

        selftests.correr()
        return 0
    if a.validar:
        return revalidar(a)
    if a.informe:
        from exportar_market_history_lib import informe

        if not a.datasets:
            print("exportar: --informe necesita --datasets", file=sys.stderr)
            return 2
        texto = informe.generar(a.salida_raiz, a.runs or RUNS, [n.strip() for n in a.datasets.split(",") if n.strip()])
        with open(a.informe, "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        print(f"informe escrito en {a.informe}")
        return 0
    if not a.corte:
        print("exportar: falta --corte", file=sys.stderr)
        return 2
    return exportar(a)


if __name__ == "__main__":
    sys.exit(main())
