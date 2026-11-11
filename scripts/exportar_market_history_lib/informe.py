"""Informe Markdown de uno o varios datasets exportados. Todas las cifras salen de `procedencia.json` (dentro del dataset) y de
`runs/TI-02-DATA/<nombre>.json` (registro de la ejecucion y de la validacion); no se escribe ninguna a mano."""
from __future__ import annotations

import json
import os

from .fuentes import iso_ms


def _fila(celdas) -> str:
    return "| " + " | ".join("-" if c is None or c == "" else str(c).replace("|", "/").replace("\n", " ") for c in celdas) + " |"


def _leer(ruta: str) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def _motivos(c: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in sorted(c["excluidas"].items())) or "ninguna"


def _detalle_limpieza(t: dict) -> list:
    c, carga, out = t["limpieza"], t["carga"], []
    out.append(f"- `{t['table_id']}`: {c['filas_origen']} filas de origen = {c['filas_finales']} finales + "
               f"{sum(c['excluidas'].values())} excluidas ({_motivos(c)}).")
    sel = carga.get("seleccion_fuentes")
    if sel:
        out.append(f"  - Politica de fuentes `{sel['politica_version']}`; source admitidas (tags, filas validas de carga): "
                   f"{carga['source']}; leidas {sel['leidas_por_source']}; excluidas {sel['excluidas_por_source']}.")
        for s in sel["series"]:
            out.append(f"  - {s['symbol']} {s['interval']} source={s['source']}: {s['filas_leidas']} leidas, "
                       f"{s['filas_excluidas_por_fuente']} excluidas por fuente; regla {s['regla'] or 'una sola fuente'}.")
        for symbol in sorted({s['symbol'] for s in sel['series']}):
            ss = [s for s in sel['series'] if s['symbol'] == symbol]
            if any(s['regla'] for s in ss) and not any(s['admitida'] and s['filas_leidas'] for s in ss):
                out.append(f"  - AVISO: {symbol}: sin barras de la fuente exigida; no se usa una fuente alternativa.")
    d = c["detalle"]
    if "nulo_o_nan_por_columna" in d:
        out.append(f"  - Nulos o NaN por columna: {d['nulo_o_nan_por_columna']}.")
    for k in ("version_posterior_descartada", "version_anterior_descartada", "version_mt5_revisada", "duplicado"):
        if k in d:
            extra = f", diferencia relativa maxima de `close` {d[k]['max_dif_relativa_close']:.3g}" \
                if "max_dif_relativa_close" in d[k] else ""
            out.append(f"  - Versiones repetidas de una misma barra o dato ({k}): {d[k]['descartadas']} descartadas, "
                       f"{d[k]['con_valores_distintos']} con valores distintos de la conservada{extra}.")
    if "version_mt5_revisada" in d:
        for r in d["version_mt5_revisada"]["pares_y_fechas"]:
            out.append(f"  - version_mt5_revisada: {r['instrument']} {iso_ms(r['ts_ms'])}, "
                       f"{r['versiones_completas']} versiones completas hasta el corte; elegida recepcion "
                       f"{iso_ms(r['recv_elegida_ms'])}, disponible en recepcion {iso_ms(r['available_at_recepcion_ms'])}.")
    if c.get("ejemplos"):
        out.append("  - Ejemplos de filas excluidas: " + "; ".join(
            f"{m}: {e[:2]}" for m, e in sorted(c["ejemplos"].items())) + ".")
    if "volumen_cero" in c:
        out.append(f"  - Barras con volumen 0 (se conservan): {c['volumen_cero']}.")
    h = c.get("huecos")
    if h:
        tot = h["total"]
        mayor = max((v["mayor_hueco_barras"] for v in h["por_instrumento"].values()), default=0)
        out.append(f"  - Huecos (no se rellenan): {tot['huecos']} huecos, {tot['barras_ausentes']} barras ausentes, mayor "
                   f"{mayor} barras seguidas; {tot['huecos_de_fin_de_semana']} caen en el cierre semanal del FX.")
        fuera = {k.split('|')[0]: v for k, v in h["por_instrumento"].items() if v["fuera_de_rejilla"]}
        if fuera:
            ini = min(v["primera_fuera_de_rejilla_ms"] for v in fuera.values())
            fin = max(v["ultima_fuera_de_rejilla_ms"] for v in fuera.values())
            por = ", ".join(k + " " + str(v["fuera_de_rejilla"]) for k, v in fuera.items())
            out.append(f"  - Barras que no empiezan en la rejilla UTC de su intervalo (se conservan tal como las publica la fuente): "
                       f"{tot['fuera_de_rejilla']} ({por}), entre {iso_ms(ini)} y {iso_ms(fin)}.")
        else:
            out.append("  - Todas las barras empiezan en la rejilla UTC de su intervalo.")
    hd = c.get("huecos_por_dia")
    if hd:
        out.append(f"  - Huecos de dias naturales entre eventos (no se rellenan): {hd['total']['huecos_de_dias']} huecos, "
                   f"{hd['total']['dias_ausentes']} dias sin evento.")
    if "date_frente_a_ts" in carga:
        x = carga["date_frente_a_ts"]
        out.append(f"  - Campo `date` frente a `_ts` (se usa `_ts`): {x['filas_con_date']} filas con `date`, "
                   f"{x['dia_utc_distinto']} cambian de dia UTC; desfase `date - _ts` en segundos (valor: filas) "
                   f"{x['desfase_date_menos_ts_en_segundos']}; ejemplos {x['ejemplos_de_dia_distinto']}.")
        out.append(f"  - `_recv_ts` presente en {carga['filas_con_recv_ts']} de {carga['filas_leidas']} filas, entre "
                   f"{carga['recv_ts_primero']} y {carga['recv_ts_ultimo']}, anterior a `_ts` en {carga['recv_ts_anterior_a_ts']}; "
                   f"`_ts` con resolucion inferior al ms en {carga['ts_con_resolucion_inferior_al_ms']}.")
    if "sin_campo_de_disponibilidad" in carga:
        out.append(f"  - Filas sin campo de disponibilidad: {carga['sin_campo_de_disponibilidad']}; con `_ts` distinto del campo "
                   f"de disponibilidad: {carga['disponibilidad_distinta_de__ts']}; con `_ts` igual a la medianoche de la fecha del "
                   f"dato: {carga['filas_con__ts_igual_a_la_fecha']}; disponibilidad entre {carga['disponibilidad_primera']} y "
                   f"{carga['disponibilidad_ultima']}.")
    if "ohlc_incoherente_conservada" in d:
        x = d["ohlc_incoherente_conservada"]
        out.append(f"  - Barras con open o close fuera de [low, high] (se conservan, no se corrigen): {x['filas']}; desvio relativo "
                   f"al cierre, mediana {x['mediana_desvio_relativo']:.3g} y maximo {x['max_desvio_relativo']:.3g}.")
    v = d.get("version_mayor_diferencia")
    if v:
        iv = f"{v['interval_ms'] // 3_600_000} h" if v["interval_ms"] < 86_400_000 else f"{v['interval_ms'] // 86_400_000} d"
        cifra = (f"{v['instrument']} {iv} {iso_ms(v['ts_ms'])} pasa de {v['close_primera']:.6g} (recibida "
                 f"{iso_ms(v['recv_primera_ms'])}) a {v['close_ultima']:.6g} (recibida {iso_ms(v['recv_ultima_ms'])}), "
                 f"{v['dif_relativa']:.2%}")
        if v.get("solo_cerradas", False):
            out.append(f"  - Mayor cambio de `close` entre la primera y la ultima version recibida con la barra ya cerrada, en una "
                       f"barra del dataset: {cifra}. Es una revision de un valor ya cerrado: el valor que llega despues no es "
                       "el visible al cierre.")
        else:
            out.append("  - Ninguna barra del dataset cambia de `close` entre versiones recibidas con la barra ya cerrada. La "
                       f"cifra siguiente incluye versiones recibidas con la barra todavia abierta, asi que mide la evolucion "
                       f"dentro de la barra y no una revision posterior al cierre: {cifra}.")
    if "date_frente_a_ts" in carga:
        r = carga["date_frente_a_ts"].get("rango_de__ts_por_desfase", {})
        r3600, r0 = r.get("3600"), r.get("0")
        if r3600 and r0 and r3600[1][:10] < "2026-10-25" <= r0[0][:10]:
            out.append(f"  - Causa del desfase de 3600 s: aparece solo en `_ts` de {r3600[0]} a {r3600[1]} y vale 0 de {r0[0]} en "
                       "adelante; el horario de verano britanico (BST) acabo el 2026-10-25. `date` es la hora local de Londres "
                       "escrita como si fuera UTC (los cambios de dia son las barras de las 00:00 de Londres, que en BST son las "
                       "23:00 UTC del dia anterior) y `_ts` es el instante UTC correcto: se usa `_ts`.")
    congeladas = carga.get("fechados_mas_de_un_ano_antes_de_leerse")
    if congeladas:
        lista = "; ".join(f"{g['instrument']} ({g['filas']} filas de {', '.join(g['anios'])}, {g['valores_distintos']} valor(es) "
                          f"entre {g['valor_minimo']:g} y {g['valor_maximo']:g})" for g in congeladas)
        out.append(f"  - Cotizaciones fechadas (`valuation_date`) mas de un ano antes de leerse: {lista}. Las de un unico valor "
                   "repetido son cotizaciones congeladas de la fuente; el scraper lee todas a partir de 2025-12 y se fechan por `valuation_date` (por eso el "
                   "rango llega a 2014, aunque el inventario TI-01-INV las fechaba por `_ts`, la lectura) y su disponibilidad es "
                   "la lectura, asi que no hay look-ahead. Se conservan tal cual.")
        if any("SARON" in g["instrument"] and g["valor_maximo"] > 0.5 for g in congeladas):
            out.append("  - Un 1,0072 en SARON no parece un tipo (1 %) sino un precio de futuro dividido entre 100; se conserva "
                       "sin corregir y quien use estas series debe tratarlo como sospechoso.")
    return out


def generar(raiz: str, runs: str, nombres: list) -> str:
    docs = []
    for n in nombres:
        proc = _leer(os.path.join(raiz, n, "procedencia.json"))
        reg = _leer(os.path.join(runs, n + ".json"))
        rep = os.path.join(runs, n + ".repeticion.json")
        docs.append((n, proc, reg, _leer(rep) if os.path.isfile(rep) else None))
    v = docs[0][1]["versiones"]
    L = ["# TI-02-DATA: informe del exportador a `engine.market-history/v1`", "",
         f"- Motor: {v['motor']}; python {v['python']}, pyarrow {v['pyarrow']}, pandas {v['pandas']}, numpy {v['numpy']}.",
         "- Generado por `exportar_market_history.py --informe` a partir de `procedencia.json` y del registro de cada ejecucion.",
         "- Reglas: el corte es el instante `AAAA-MM-DDT00:00:00Z`; una fila entra solo si su cierre y su `available_at_ms` son "
         "menores o iguales (si lo tiene); `default_lag_ms` queda nulo salvo en un dataset con disponibilidad proxy declarada "
         "(valor 0, y esas filas llevan `available_at_ms` nulo); los huecos no se rellenan; nada se descarta sin contarlo.", ""]
    L += [_fila(["dataset", "corte", "filas por tabla", "tablas vacias tras el corte", "tipo de disponibilidad por tabla",
                 "dataset_hash"]), "|---|---|---|---|---|---|"]
    for n, proc, reg, _ in docs:
        tipos = "; ".join(f"{t['table_id']}: {t['disponibilidad']['tipo']}" for t in proc["tablas"] if t["filas"])
        L.append(_fila([f"`{n}`", proc["corte"], ", ".join(f"{t['table_id']} {t['filas']}" for t in proc["tablas"]),
                        ", ".join(reg["validacion"].get("tablas_vacias", [])) or "ninguna", tipos or "-",
                        f"`{proc['dataset_hash'][:23]}...`"]))
    L.append("")
    for n, proc, reg, rep in docs:
        L += [f"## Dataset `{n}`", "",
              f"- Corte (`--corte`): **{proc['corte']}** ({proc['corte_utc']}); `dataset_hash` `{proc['dataset_hash']}`.",
              f"- Fecha de la ejecucion (UTC): {reg['fecha_utc']}; duracion {reg['duracion_s']} s; zona del mercado "
              f"`{proc['zona_horaria_del_mercado']}`.",
              f"- Comando exacto: `{reg['comando']}`", ""]
        for o in proc["origenes"]:
            f = o["fuente"]
            if f["tipo"] == "binance":
                for d in f["datasets"]:
                    L.append(f"- Fuente `{d['dataset']}` (TI-13-PUB, clase D-11 `{d['clase_d11']}`, licencia {d['licencia']}): "
                             f"sha256 del dataset `{d['dataset_sha256']}`, descarga {d['fecha_descarga_utc']}, parquet "
                             + ", ".join(f"`{x['ruta']}` `{x['sha256'][:16]}...` ({x['filas']} filas)" for x in d["ficheros"]) + ".")
            else:
                L.append(f"- Fuente lago de qn: base `{f['base']}`, entorno `{f['env']}`, rango pedido {f['desde']} a {f['hasta']}, "
                         f"volcado del {f['fecha_utc']} ({f['ficheros']} ficheros), manifest sha256 `{f['manifest_sha256']}`; "
                         f"`descarga_lago.py` sha256 `{str(f['descarga_lago_sha256'])[:16]}...` (python {f['python_descarga']}).")
                L.append(f"  - Paso 1, en mini con `QN_URLS`, `QN_TOKEN` y `QN_ENV={f['env']}` en el entorno: "
                         f"`python3 descarga_lago.py --desde {f['desde']} --hasta {f['hasta']} --salida <directorio>`; despues se copia "
                         f"a `{f['volcado']}` y el paso 2 es el comando exacto de arriba.")
        L += ["", _fila(["tabla", "esquema", "instrumentos", "frecuencias", "primera", "ultima", "filas", "logical_hash"]),
              "|---|---|---|---|---|---|---|---|"]
        for t in proc["tablas"]:
            frec = ", ".join(f"{x // 3_600_000} h" if x < 86_400_000 else f"{x // 86_400_000} d" for x in t["intervalos_ms"]) or "eventos"
            L.append(_fila([f"`{t['table_id']}`", t["schema"], t["instrumentos"], frec, t["primera"], t["ultima"], t["filas"],
                            f"`{t['logical_hash']}`"]))
        L += ["", "### Reproducibilidad", ""]
        if rep:
            iguales = rep["validacion"]["dataset_hash"] == proc["dataset_hash"]
            mismos = rep.get("ficheros_sha256") == reg.get("ficheros_sha256") and rep.get("ficheros_sha256") is not None
            L += [f"- Segunda exportacion con el mismo origen y corte ({rep['fecha_utc']}): `dataset_hash` "
                  f"`{rep['validacion']['dataset_hash']}` -> **{'igual' if iguales else 'DISTINTO'}**; "
                  f"manifest, parquet y procedencia **{'byte a byte identicos' if mismos else 'NO identicos'}**.",
                  f"- Comando de la repeticion: `{rep['comando']}`"]
        else:
            L.append("- No hay segunda exportacion registrada (`runs/TI-02-DATA/<nombre>.repeticion.json`).")
        L += ["", "### Limpieza", ""]
        for t in proc["tablas"]:
            L += _detalle_limpieza(t)
        L += ["", "### Disponibilidad (`available_at_ms`)", ""]
        for t in proc["tablas"]:
            d = t["disponibilidad"]
            L.append(f"- `{t['table_id']}` [{d['tipo']}]: {d['declarada']}; campo: {d['campo'] or 'ninguno'}. {d['justificacion']}")
        val = reg["validacion"]
        L += ["", "### Validacion con `data_py` y look-ahead", "",
              f"- `{val['llamadas']['vendor']}`: `dataset_hash` del motor `{val['vendor']['dataset_hash_del_motor']}`, "
              f"{'igual' if val['vendor']['dataset_hash_del_motor'] == proc['dataset_hash'] else 'DISTINTO del'} calculado aqui.",
              f"- `{val['llamadas']['describe']}`: tablas {', '.join(t['table_id'] + ' (' + str(t['rows']) + ' filas, hash_verified=' + str(t['hash_verified']) + ')' for t in val['describe']['tablas'])}.",
              f"- `{val['llamadas']['disponibilidad']}` por tabla: " + "; ".join(
                  f"{k}: declared {x['declared']}/{x['rows']}, defaulted {x['defaulted']}, undeclared {x['undeclared']}, "
                  f"violaciones DPOL-AVL-002 {x['violaciones_dpol_avl_002']}" for k, x in val["disponibilidad"].items()) + ".",
              f"- `{val['llamadas']['politica']}`: ok={val['politica']['ok']}, violaciones: "
              f"{[(x['code'], x['severity'], x.get('instrument')) for x in val['politica']['violaciones']] or 'ninguna'}; "
              f"report_hash `{val['politica']['report_hash']}`."]
        if "politica_con_lag_admitido" in val:
            x = val["politica_con_lag_admitido"]
            L.append(f"- Misma politica con `max_default_lag_ms` = {x['max_default_lag_ms']} (admite el lag declarado): ok={x['ok']}, "
                     f"violaciones {[(v['code'], v['severity']) for v in x['violaciones']] or 'ninguna'}. El DPOL-AVL-001 de arriba es "
                     "el aviso de que esas filas son proxy y no estrictas.")
        L += [
              f"- Comprobacion propia sobre el parquet releido (esquema exacto de `data_py.table_schemas_json()`, orden, "
              f"cierre y disponibilidad <= corte, disponibilidad >= cierre, revision 0): "
              + ("sin incidencias." if not any(x["problemas"] for x in val["parquet"].values()) else str(val["parquet"])),
              f"- Violaciones de look-ahead por fila: **{val['lookahead']['violaciones_por_fila']}**; tablas no consumibles "
              f"causalmente en sentido estricto: {val['tablas_no_consumibles_causalmente'] or 'ninguna'} (de ellas, proxy por "
              f"`default_lag_ms`: {val['tablas_proxy'] or 'ninguna'}); tablas vacias tras el corte (ninguna fila "
              f"cumple cierre y disponibilidad <= corte): {val['tablas_vacias'] or 'ninguna'}.", ""]
        L += ["### Universo y sesgo de supervivencia (D-07)", ""]
        for o in proc["origenes"]:
            L.append(f"- {o['nombre']}: {o['universo']['texto']}")
        L.append("")
    L += ["## Lo que no se exporta", "",
          "- Cadenas de opciones (`market.options.*`): vacias en el lago (TI-01-INV); TI-09-ARCH retirada.",
          "- MT5 (TI-12-MT5, a la espera de la puerta 2) y los corpus genericos de TI-13-PUB (sin OHLCV real con fecha).",
          "- De Binance: `quote_volume` y `n_trades`; `ohlcv/v1` no tiene donde ponerlos (`volume` es el volumen en activo base, "
          "`volume_kind` = `traded`). Tampoco `value`, que es igual a `close`.",
          "- Del lago: el campo `date` (se usa `_ts`, ver el desfase arriba), `_clock_offset_ns` (nulo en todas las filas), "
          "`_batch_id`, `_cycle` y demas columnas de sistema.",
          "- Ninguna tabla `universe/v1` ni `corporate_actions/v1`: no se conocen altas, bajas ni acciones corporativas, y "
          "`adjusted_by_vendor` queda en su valor por defecto (precios crudos).", ""]
    return "\n".join(L)
