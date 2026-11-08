"""Filtro de fugas D-11, particion train/val disjunta, escritura de parquet y manifiestos (TI-13-PUB)."""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import platform
import shutil

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from . import common as C
from . import lectores as LEC
from . import registro as R

MS_ANIO_MIN = -8_520_336_000_000  # 1700-01-01 UTC: por debajo es casi seguro un error de unidad (la serie de manchas solares empieza en 1818)
# Inicios por defecto de las librerias cuando el origen no trae fecha: 1970-01-01 (epoch) y 1900-01-01 (cargador de Monash).
INICIOS_FICTICIOS = (0, -2_208_988_800_000)
PARTES = ("tronco", "adaptadores")
FILAS_POR_LOTE = 2_000_000


def iso_ms(t) -> str | None:
    """ms UTC a ISO; sin fromtimestamp, que en Windows falla con fechas anteriores a 1970."""
    if t is None:
        return None
    return (dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(milliseconds=int(t))).strftime("%Y-%m-%dT%H:%M:%SZ")


def corte_ms(corte: str) -> int:
    """AAAA-MM-DD (UTC, 00:00) en ms."""
    d = dt.datetime.strptime(corte, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp() * 1000)


# --- clasificacion y decision por serie -----------------------------------------------------------------------------

def es_financiera(entry: dict, dominio: str | None) -> bool:
    """Criterio D-11 (CRITERIO_D11). Con dominio por serie se filtra serie a serie (lo desconocido cuenta como financiero)."""
    if entry["clase"] == R.NO_FIN:
        return False
    if entry["clase"] == R.REAL:
        return True
    if entry.get("dominio_col") and dominio is not None:
        return dominio.strip().lower() not in R.DOMINIOS_NO_FIN
    return True


def hash_contenido(v: np.ndarray) -> bytes:
    """Hash por serie del contenido (valores float64, NaN canonico y longitud): detecta series identicas con otro id."""
    a = np.ascontiguousarray(np.where(np.isnan(v), np.nan, v), dtype="<f8")
    return hashlib.sha256(len(a).to_bytes(8, "little") + a.tobytes()).digest()[:16]


def decidir(entry: dict, s: LEC.Serie, corte: int, ahora: int) -> dict:
    """Decision D-11 de una serie. accion: intacta | antes | cortada | despues | excluida; idx = primer punto >= corte."""
    n = int(len(s.v))
    nan = int(np.count_nonzero(np.isnan(s.v)))
    r = {"sid": s.id, "n": n, "nan": nan, "idx": None, "motivo": "", "financiera": False, "ts_ok": True}
    if n == 0 or nan == n:
        r.update(accion="excluida", motivo="serie vacia", financiera=es_financiera(entry, s.dom))
        return r
    if s.ts is not None:
        t = s.ts
        # marcas validas: crecientes sin repetidas, entre 1700 y hoy, y sin los inicios por defecto de las librerias
        r["ts_ok"] = bool(len(t) == n and (n < 2 or np.all(np.diff(t) > 0)) and t[0] > MS_ANIO_MIN
                          and int(t[0]) not in INICIOS_FICTICIOS and t[-1] <= ahora)
        r["t0"], r["t1"] = int(t[0]), int(t[-1])
        # hueco o marca irregular: un paso mayor que 1,5 o menor que 0,5 veces el paso mediano (los meses, trimestres y anos no
        # miden lo mismo en ms, por eso no se exige un paso unico)
        paso = np.diff(t)
        med = float(np.median(paso)) if len(paso) else 1.0
        r["regular"] = bool(n < 3 or (med > 0 and paso.max() <= 1.5 * med and paso.min() >= 0.5 * med))
    fin = es_financiera(entry, s.dom)
    r["financiera"] = fin
    if entry["clase"] == R.REAL:
        r.update(accion="intacta", idx=0)  # todo a adaptadores
        if not r["ts_ok"]:
            r.update(accion="excluida", motivo="fechas imposibles (desordenadas, duplicadas o fuera de rango)")
        return r
    if not fin:
        r.update(accion="intacta", idx=n)  # todo a tronco
        return r
    if entry["fechas"] != R.FECHAS_REALES:
        r.update(accion="excluida", motivo="financiera sin fechas reales verificables")
        return r
    if not r["ts_ok"]:
        r.update(accion="excluida", motivo="financiera con fechas imposibles (desordenadas, duplicadas o fuera de rango)")
        return r
    idx = int(np.searchsorted(s.ts, corte, side="left"))
    r["idx"] = idx
    r["accion"] = "antes" if idx == n else ("despues" if idx == 0 else "cortada")
    return r


def trozos(r: dict, s: LEC.Serie):
    """[(parte, slice)] de una serie ya decidida."""
    if r["accion"] == "excluida":
        return []
    n, idx = r["n"], r["idx"]
    if r["accion"] == "intacta" and idx == n:
        return [("tronco", slice(0, n))]
    if r["accion"] == "intacta":
        return [("adaptadores", slice(0, n))]
    out = []
    if idx > 0:
        out.append(("tronco", slice(0, idx)))
    if idx < n:
        out.append(("adaptadores", slice(idx, n)))
    return out


# --- particion train/val ---------------------------------------------------------------------------------------------

def lado_por_id(clave: str, sal: str = R.SAL, frac: float = R.FRAC_VAL) -> str:
    """Hash estable (SHA-256 de sal + id), no hash() de Python: val si el valor uniforme cae bajo `frac`."""
    h = hashlib.sha256((sal + "\x1f" + clave).encode("utf-8")).digest()
    return "val" if int.from_bytes(h[:8], "big") / 2**64 < frac else "train"


def asignar_lados(contenidos: dict, sal: str = R.SAL, frac: float = R.FRAC_VAL) -> tuple:
    """contenidos: {clave_serie: [hash de cada trozo]}. Las series que comparten contenido (con cualquier id, en cualquier
    dataset) forman un componente conexo y comparten lado: el del miembro de menor clave. Devuelve ({clave: lado}, stats)."""
    padre = {k: k for k in contenidos}

    def raiz(x):
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    por_hash = {}
    for k, hs in contenidos.items():
        for h in hs:
            otro = por_hash.setdefault(h, k)
            if otro != k:
                a, b = raiz(otro), raiz(k)
                if a != b:
                    padre[max(a, b)] = min(a, b)
    lados = {k: lado_por_id(raiz(k), sal, frac) for k in contenidos}
    tam = {}
    for k in contenidos:
        tam[raiz(k)] = tam.get(raiz(k), 0) + 1
    grandes = sorted(tam.values(), reverse=True)[:3]
    return lados, {"componentes_con_duplicados": sum(1 for v in tam.values() if v > 1), "mayor_componente": grandes[0] if grandes else 0}


def comprobar_disjuntos(lados: dict, contenidos: dict) -> dict:
    """Sobre el plan: cuenta contenidos identicos asignados a ambos lados (un id solo tiene un lado por construccion)."""
    hashes = {}
    for k, hs in contenidos.items():
        for h in hs:
            hashes.setdefault(h, set()).add(lados[k])
    return {"contenidos_en_ambos_lados": sum(1 for v in hashes.values() if len(v) > 1),
            "series": len(contenidos), "contenidos_distintos": len(hashes)}


def comprobar_escrito(salida: str, mans: dict) -> dict:
    """Sobre lo ESCRITO: relee los parquet y cuenta series_id y contenidos (hash de los valores de cada serie) presentes a la vez
    en los ficheros train y val de cualquier dataset."""
    ids, hs, filas, filas_distintas = {"train": set(), "val": set()}, {"train": set(), "val": set()}, 0, []
    for did, m in mans.items():
        for f in m["ficheros"]:
            t = pq.read_table(f"{salida}/{did}/{f['ruta']}", columns=["series_id", "value"])
            filas += t.num_rows
            if t.num_rows != f["filas"]:
                filas_distintas.append(f"{did}/{f['ruta']}: {t.num_rows} filas leidas, {f['filas']} en el manifiesto")
            cod = t.column("series_id").combine_chunks().dictionary_encode()
            idx, nombres, v = cod.indices.to_numpy(), cod.dictionary.to_pylist(), t.column("value").to_numpy()
            corta = np.flatnonzero(np.diff(idx)) + 1
            for a, b in zip(np.concatenate([[0], corta]), np.concatenate([corta, [len(idx)]])):
                ids[f["split"]].add(nombres[idx[a]])
                hs[f["split"]].add(hash_contenido(v[a:b]))
    return {"filas_releidas": filas, "series_train": len(ids["train"]), "series_val": len(ids["val"]),
            "ids_en_ambos_lados": len(ids["train"] & ids["val"]), "contenidos_en_ambos_lados": len(hs["train"] & hs["val"]),
            "filas_distintas_del_manifiesto": filas_distintas}


# --- analisis (pasada 1) ---------------------------------------------------------------------------------------------

def analizar(entry: dict, corte: int, ahora: int) -> dict:
    """Lee lo crudo y decide cada serie. No guarda arrays: la escritura relee lo crudo (pasada 2)."""
    # con fechas no verificables y sin dominio por serie todo se excluye: no hace falta generar marcas
    con_ts = True  # tambien en los excluidos: el rango y la validez de las marcas son la evidencia de que no se pueden fiar
    regs, vistos, dup_ids, meta_total = [], {}, 0, {"duplicados": 0, "huecos": 0}
    for s in LEC.series(entry, con_ts=con_ts):
        sid = s.id
        if sid in vistos:  # id repetido dentro del dataset: se conserva y se renombra, y se cuenta
            vistos[sid] += 1
            dup_ids += 1
            sid = f"{sid}~dup{vistos[s.id]}"
            s = s._replace(id=sid)
        vistos.setdefault(sid, 1)
        r = decidir(entry, s, corte, ahora)
        r["clave"] = f"{entry['id']}/{sid}"
        r["hashes"] = []
        for parte, sl in trozos(r, s):
            r["hashes"].append(hash_contenido(s.v[sl]))
        if s.meta:
            meta_total["duplicados"] += s.meta.get("duplicados", 0)
            meta_total["huecos"] += s.meta.get("huecos", 0)
        regs.append(r)
    return {"registros": regs, "dup_ids": dup_ids, "meta": meta_total, "con_ts": con_ts}


def estadisticas(entry: dict, an: dict) -> dict:
    regs = an["registros"]
    st = {"series_total": len(regs), "ids_duplicados": an["dup_ids"], "series_vacias": 0,
          "series_financieras": sum(1 for r in regs if r["financiera"]),
          "series_no_financieras": sum(1 for r in regs if not r["financiera"]),
          "excluidas_sin_fechas_verificables": 0, "excluidas_fechas_imposibles": 0,
          "cortadas": 0, "financieras_solo_antes": 0, "financieras_solo_despues": 0,
          "no_financieras_intactas": 0, "puntos_total": 0, "puntos_tronco": 0, "puntos_adaptadores": 0,
          "puntos_excluidos": 0, "puntos_quitados_del_tronco_por_corte": 0, "puntos_nan": 0,
          "series_irregulares": 0, "series_fechas_invalidas": 0, "duplicados_de_contenido": 0,
          "duplicados_binance": an["meta"]["duplicados"], "huecos_binance": an["meta"]["huecos"]}
    t0 = t1 = None
    vistos = {}
    for r in regs:
        n = r["n"]
        st["puntos_total"] += n
        st["puntos_nan"] += r["nan"]
        st["series_irregulares"] += 0 if r.get("regular", True) else 1
        st["series_fechas_invalidas"] += 0 if r["ts_ok"] else 1
        if "t0" in r:
            t0 = r["t0"] if t0 is None else min(t0, r["t0"])
            t1 = r["t1"] if t1 is None else max(t1, r["t1"])
        for h in r["hashes"]:
            if h in vistos and vistos[h] != r["clave"]:
                st["duplicados_de_contenido"] += 1
            vistos.setdefault(h, r["clave"])
        a = r["accion"]
        if a == "excluida":
            st["puntos_excluidos"] += n
            if r["motivo"] == "serie vacia":
                st["series_vacias"] += 1
            elif "sin fechas" in r["motivo"]:
                st["excluidas_sin_fechas_verificables"] += 1
            else:
                st["excluidas_fechas_imposibles"] += 1
        elif a == "intacta":
            if r["idx"] == n:
                st["no_financieras_intactas"] += 1
                st["puntos_tronco"] += n
            else:
                st["puntos_adaptadores"] += n
        else:
            tr, ad = r["idx"], n - r["idx"]
            st["puntos_tronco"] += tr
            st["puntos_adaptadores"] += ad
            st["puntos_quitados_del_tronco_por_corte"] += ad
            st["cortadas"] += a == "cortada"
            st["financieras_solo_antes"] += a == "antes"
            st["financieras_solo_despues"] += a == "despues"
    st["rango_ts_utc"] = [iso_ms(t0), iso_ms(t1)]
    return st


# --- escritura (pasada 2) --------------------------------------------------------------------------------------------

def esquema(entry: dict) -> pa.Schema:
    campos = [("series_id", pa.string()), ("ts", pa.timestamp("ms", tz="UTC")), ("value", pa.float64())]
    if entry["formato"] == "binance":
        campos += [(c, pa.int64() if c == "n_trades" else pa.float64()) for c in LEC.OHLCV]
    return pa.schema(campos)


class Escritor:
    """Un ParquetWriter por (parte, split), con orden de filas determinista (orden de lectura)."""

    def __init__(self, entry, carpeta):
        self.entry, self.carpeta, self.esq = entry, carpeta, esquema(entry)
        self.w, self.buf, self.filas, self.series, self.nbuf = {}, {}, {}, {}, {}

    def _ruta(self, parte, split):
        return f"{self.carpeta}/{parte}.{split}.parquet"

    def anadir(self, parte, split, clave, ts, v, cols):
        k = (parte, split)
        self.buf.setdefault(k, []).append((clave, ts, v, cols))
        self.series[k] = self.series.get(k, 0) + 1
        self.nbuf[k] = self.nbuf.get(k, 0) + len(v)
        if self.nbuf[k] >= FILAS_POR_LOTE:
            self._vaciar(k)

    def _vaciar(self, k):
        lote = self.buf.pop(k, [])
        self.nbuf[k] = 0
        if not lote:
            return
        reps = np.repeat(np.arange(len(lote), dtype="int32"), [len(x[2]) for x in lote])
        ids = pa.array([x[0] for x in lote], pa.string()).take(pa.array(reps))
        ts = np.concatenate([t for _, t, _, _ in lote])
        cols = [ids, pa.array(ts, pa.timestamp("ms", tz="UTC")),
                pa.array(np.concatenate([v for _, _, v, _ in lote]), pa.float64())]
        if self.entry["formato"] == "binance":
            for c in LEC.OHLCV:
                cols.append(pa.array(np.concatenate([x[3][c] for x in lote]), self.esq.field(c).type))
        tabla = pa.Table.from_arrays(cols, schema=self.esq)
        if k not in self.w:
            os.makedirs(self.carpeta, exist_ok=True)
            self.w[k] = pq.ParquetWriter(self._ruta(*k), self.esq, compression="zstd", compression_level=3,
                                         use_dictionary=["series_id"], write_statistics=True)
        self.w[k].write_table(tabla, row_group_size=FILAS_POR_LOTE)
        self.filas[k] = self.filas.get(k, 0) + tabla.num_rows

    def cerrar(self) -> list:
        for k in list(self.buf):
            self._vaciar(k)
        out = []
        for k, w in sorted(self.w.items()):
            w.close()
            ruta = self._ruta(*k)
            out.append({"ruta": os.path.basename(ruta), "parte": k[0], "split": k[1], "bytes": os.path.getsize(ruta),
                        "sha256": C.sha256_fichero(ruta), "filas": self.filas[k], "series": self.series[k]})
        return out


def escribir(entry: dict, an: dict, lados: dict, carpeta: str, corte: int) -> list:
    esc = Escritor(entry, carpeta)
    por_clave = {r["clave"]: r for r in an["registros"]}
    vistos = {}
    for s in LEC.series(entry, con_ts=True):
        sid = s.id
        if sid in vistos:
            vistos[sid] += 1
            sid = f"{sid}~dup{vistos[s.id]}"
            s = s._replace(id=sid)
        vistos.setdefault(sid, 1)
        r = por_clave[f"{entry['id']}/{sid}"]
        for parte, sl in trozos(r, s):
            cols = None if s.cols is None else {c: a[sl] for c, a in s.cols.items()}
            esc.anadir(parte, lados[r["clave"]], r["clave"], s.ts[sl], s.v[sl], cols)
    return esc.cerrar()


# --- manifiestos -----------------------------------------------------------------------------------------------------

def versiones() -> dict:
    import huggingface_hub
    import pandas
    return {"python": platform.python_version(), "pyarrow": pa.__version__, "pandas": pandas.__version__,
            "numpy": np.__version__, "huggingface_hub": huggingface_hub.__version__}


def hash_contenido_dataset(an: dict, lados: dict) -> str:
    pares = []
    for r in an["registros"]:
        for i, h in enumerate(r["hashes"]):
            pares.append((f"{r['clave']}|{i}|{lados[r['clave']]}", h.hex()))
    return C.hash_conjunto(pares)


def estimacion_escritura(crudo: list) -> int:
    """Estimacion prudente de lo que ocupara lo procesado de un dataset: FACTOR_ESCRITURA x los bytes de su crudo (en los datos
    reales el parquet zstd ocupa entre 0,5 y 1,3 veces el crudo)."""
    return C.FACTOR_ESCRITURA * sum(int(c["bytes"]) for c in crudo)


def procesar_dataset(entry: dict, an: dict, lados: dict, salida: str, corte: str, licencia: dict, crudo: list,
                     usado_previo: int = 0, guarda=C.guarda) -> dict:
    """Escribe los parquet y el manifiesto de un dataset. `salida` es la carpeta raiz de datasets. ANTES de escribir aplica la
    guarda de 100 GB (y los suelos de C: y E:) con `usado_previo` (bytes de los manifiestos) mas la estimacion de lo que va a ocupar."""
    carpeta = f"{salida}/{entry['id']}"
    hay_datos = any(r["accion"] != "excluida" for r in an["registros"])
    if hay_datos:
        guarda(estimacion_escritura(crudo), usado_previo, C.bytes_cache_hf())
    if os.path.isdir(carpeta):
        shutil.rmtree(carpeta)
    ficheros = escribir(entry, an, lados, carpeta, corte_ms(corte)) if hay_datos else []
    st = estadisticas(entry, an)
    man = {
        "dataset": entry["id"], "fuente": entry["fuente"], "repo": entry.get("repo"), "subconjunto": entry["nombre"],
        "estado": "procesado" if ficheros else "sin_datos_en_el_tronco_ni_adaptadores",
        "dominio": entry["dominio"], "clase_d11": entry["clase"], "fechas": entry.get("fechas"),
        "fechas_evidencia": entry.get("fechas_evid"), "motivo_clase": entry["motivo"], "frecuencia": entry["freq"],
        "licencia": licencia, "crudo": crudo, "corte": corte, "sal": R.SAL, "fraccion_val": R.FRAC_VAL,
        "fecha_descarga_utc": max([c.get("fecha_descarga_utc", "") for c in crudo], default=""),
        "fecha_proceso_utc": C.ahora_utc(), "versiones": versiones(), "motor": C.MOTOR,
        "ficheros": ficheros, "filtro": st,
        "series": {"tronco": sum(f["series"] for f in ficheros if f["parte"] == "tronco"),
                   "adaptadores": sum(f["series"] for f in ficheros if f["parte"] == "adaptadores")},
        "dataset_sha256": C.hash_conjunto([(f["ruta"], f["sha256"]) for f in ficheros]),
        "contenido_sha256": hash_contenido_dataset(an, lados),
    }
    C.escribir_json(f"{carpeta}/manifest.json", man)
    return man


def filas_csv(entry: dict, an: dict) -> list:
    """Series afectadas por el filtro (excluidas, cortadas o movidas enteras a adaptadores)."""
    out = []
    for r in an["registros"]:
        afectada = r["accion"] == "excluida" or (r["accion"] in ("cortada", "despues") and entry["clase"] != R.REAL)
        if afectada:
            n_t = 0 if r["accion"] == "excluida" else r["idx"]
            n_a = 0 if r["accion"] == "excluida" else r["n"] - r["idx"]
            out.append((entry["id"], r["sid"], r["accion"], r["motivo"], r["n"], n_t, n_a))
    return out


def crudo_registrado() -> dict:
    """Entradas de los raw_manifest.json de todas las fuentes: ruta -> {bytes, sha256, ...}."""
    from . import fuentes as F
    return F.manifiesto_crudo(F.RAW_HF)["archivos"] | F.manifiesto_crudo(F.RAW_BINANCE)["archivos"]


def datasets_esperados(estado_lic: dict | None, crudo_all: dict, ids: list | None = None) -> list:
    """Datasets que DEBEN estar procesados: los del registro con licencia verificada y todo su crudo registrado."""
    if not estado_lic:
        return []
    out = []
    for e in R.DATASETS + R.BINANCE:
        if ids and e["id"] not in ids:
            continue
        if (estado_lic["datasets"].get(e["id"]) or {}).get("estado") != "verificada":
            continue
        claves = LEC.rutas_crudo(e)
        if claves and all(k in crudo_all for k in claves):
            out.append(e)
    return out


def correr(corte: str, estado_lic: dict, salida: str, ids: list | None = None, informes_dir: str | None = None) -> dict:
    """Procesa todos los datasets con lo crudo presente y licencia verificada. Devuelve {id: manifiesto}."""
    from . import fuentes as F
    ahora = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    c_ms = corte_ms(corte)
    crudo_all = crudo_registrado()
    esperados = datasets_esperados(estado_lic, crudo_all, ids)
    analisis, contenidos, usados = {}, {}, []
    for e in R.DATASETS + R.BINANCE:
        if (ids and e["id"] not in ids) or (estado_lic["datasets"].get(e["id"]) or {}).get("estado") != "verificada":
            continue
        if e not in esperados:
            print(f"  sin crudo completo: {e['id']} (no se procesa)")
            continue
        print(f"  analizando {e['id']}")
        an = analizar(e, c_ms, ahora)
        analisis[e["id"]] = an
        usados.append(e)
        for r in an["registros"]:
            if r["hashes"]:
                contenidos[r["clave"]] = [h for h in r["hashes"]]
    lados, st_lados = asignar_lados(contenidos)
    comp = comprobar_disjuntos(lados, contenidos)
    if comp["contenidos_en_ambos_lados"]:
        raise RuntimeError(f"particion no disjunta: {comp}")
    mans = {}
    os.makedirs(salida, exist_ok=True)
    filas = []
    en_datasets = os.path.abspath(salida) == os.path.abspath(C.DATASETS)
    escrito_fuera = 0  # bytes ya escritos en una carpeta distinta de DATASETS: los manifiestos aun no los cuentan
    for e in usados:
        an = analisis[e["id"]]
        lic = {k: v for k, v in estado_lic["datasets"][e["id"]].items() if k not in ("id",)}
        lic["consulta_utc"] = estado_lic["fecha_utc"]
        crudo = [{"ruta": k, **crudo_all[k]} for k in LEC.rutas_crudo(e) if k in crudo_all]
        print(f"  escribiendo {e['id']}")
        mans[e["id"]] = procesar_dataset(e, an, lados, salida, corte, lic, crudo,
                                         usado_previo=F.bytes_en_manifiestos() + escrito_fuera)
        if not en_datasets:
            escrito_fuera += sum(f["bytes"] for f in mans[e["id"]]["ficheros"])
        filas += filas_csv(e, an)
    comp["en_parquet"] = comprobar_escrito(salida, mans)
    if comp["en_parquet"]["ids_en_ambos_lados"] or comp["en_parquet"]["contenidos_en_ambos_lados"]:
        raise RuntimeError(f"particion no disjunta en los parquet escritos: {comp}")
    resumen = {"corte": corte, "sal": R.SAL, "fraccion_val": R.FRAC_VAL, "particion": comp, "duplicados": st_lados,
               "datasets": sorted(mans)}
    if informes_dir:
        os.makedirs(informes_dir, exist_ok=True)
        ruta = f"{informes_dir}/filtro_ids.csv"
        with open(ruta, "w", encoding="utf-8", newline="\n") as f:
            f.write("dataset,series_id,accion,motivo,puntos,puntos_tronco,puntos_adaptadores\n")
            for fila in filas:
                f.write(",".join('"%s"' % str(x).replace('"', "'") if isinstance(x, str) else str(x) for x in fila) + "\n")
        resumen["csv"] = {"ruta": ruta, "sha256": C.sha256_fichero(ruta), "filas": len(filas), "bytes": os.path.getsize(ruta)}
        C.escribir_json(f"{informes_dir}/filtro_resumen.json", resumen)
    return {"manifiestos": mans, "resumen": resumen}
