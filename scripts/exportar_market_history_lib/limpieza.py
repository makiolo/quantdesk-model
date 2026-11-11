"""Limpieza explicita y contada de las tablas antes de escribirlas (nada se aproxima, se rellena ni se omite en silencio).

Cada fila de origen acaba en la tabla final o en exactamente un motivo de `contador["excluidas"]`; `verificar_identidad`
lo comprueba. Los huecos se informan, no se rellenan. Orden de los pasos (importa para a que motivo se atribuye una fila):
validez de los valores -> version de cada barra -> corte -> orden final.
"""
from __future__ import annotations

from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

PRECIOS = ("open", "high", "low", "close")
NUMERICAS = PRECIOS + ("volume",)
CLAVE_OHLCV = ["instrument", "interval_ms", "ts_ms"]
CLAVE_CUSTOM = ["instrument", "custom_type", "ts_ms"]
EJEMPLOS = 5
MS_HORA = 3_600_000
MS_DIA = 86_400_000


def nuevo_contador(filas_origen: int, excluidas_en_carga: dict | None = None) -> dict:
    return {"filas_origen": int(filas_origen), "excluidas": dict(excluidas_en_carga or {}), "ejemplos": {}, "detalle": {}}


def como_mascara(cond) -> np.ndarray:
    """Booleano numpy de una condicion que puede contener NA (NA cuenta como falso)."""
    return np.asarray(pd.Series(cond).fillna(False), dtype=bool)


def quitar(df: pd.DataFrame, mascara, motivo: str, c: dict) -> pd.DataFrame:
    """Elimina las filas de `mascara`, las cuenta bajo `motivo` y guarda los primeros ejemplos (clave de la fila)."""
    m = como_mascara(mascara)
    n = int(m.sum())
    if n:
        c["excluidas"][motivo] = c["excluidas"].get(motivo, 0) + n
        cols = [k for k in ("instrument", "custom_type", "ts_ms") if k in df.columns]
        c["ejemplos"].setdefault(motivo, [])
        for _, f in df.loc[m, cols].head(max(0, EJEMPLOS - len(c["ejemplos"][motivo]))).iterrows():
            c["ejemplos"][motivo].append({k: (f[k].item() if hasattr(f[k], "item") else f[k]) for k in cols})
    return df.loc[~m]


def verificar_identidad(c: dict, filas_finales: int) -> None:
    c["filas_finales"] = int(filas_finales)
    total = filas_finales + sum(c["excluidas"].values())
    if total != c["filas_origen"]:
        raise AssertionError(f"las cuentas no cuadran: {c['filas_origen']} de origen != {filas_finales} finales + "
                             f"{sum(c['excluidas'].values())} excluidas {c['excluidas']}")


def _distintas(a: pd.DataFrame, b: pd.DataFrame, cols) -> np.ndarray:
    """Filas alineadas de a y b cuyos valores en `cols` difieren."""
    return np.any([a[k].to_numpy() != b[k].to_numpy() for k in cols], axis=0)


def elegir_version(df: pd.DataFrame, clave: list, orden_por: list, conservar: str, cols_valor: list, c: dict,
                   motivo: str) -> pd.DataFrame:
    """Una fila por clave: ordena por `orden_por` y conserva la primera o la ultima. Cuenta las descartadas y cuantas
    traian valores distintos de la conservada (`detalle[motivo]`)."""
    df = df.sort_values(orden_por, kind="mergesort")
    descarta = df.duplicated(clave, keep="first" if conservar == "primera" else "last").to_numpy()
    if not descarta.any():
        return df
    quitadas, quedan = df.loc[descarta], df.loc[~descarta]
    pares = quitadas[clave + cols_valor].merge(quedan[clave + cols_valor], on=clave, suffixes=("", "_conservada"))
    distintas = np.any([pares[k].to_numpy() != pares[k + "_conservada"].to_numpy() for k in cols_valor], axis=0)
    detalle = {"descartadas": int(descarta.sum()), "con_valores_distintos": int(distintas.sum())}
    if "close" in cols_valor and distintas.any():
        rel = (pares["close"] - pares["close_conservada"]).abs() / pares["close_conservada"].abs()
        detalle["max_dif_relativa_close"] = float(rel.max())
    c["detalle"][motivo] = detalle
    return quitar(df, descarta, motivo, c)


def es_mt5_diaria(df: pd.DataFrame) -> pd.Series:
    return (df["source"] == "mt5") & (df["interval_ms"] == MS_DIA) if "source" in df else pd.Series(False, index=df.index)


def cierre_version(df: pd.DataFrame) -> pd.Series:
    """Umbral de version completa; solo MT5 1d usa 17:00 America/New_York de la fecha UTC de ts.

    Es distinto del fin nominal ts + intervalo usado por el corte y el proxy de disponibilidad. La columna source es
    interna a la carga: no se infiere MT5 del simbolo ni se cambia el esquema de salida.
    """
    cierre = df["ts_ms"] + df["interval_ms"]
    if "source" in df:
        mt5_diaria = es_mt5_diaria(df)
        if mt5_diaria.any():
            if (df.loc[mt5_diaria, "ts_ms"] % MS_DIA != 0).any():
                raise ValueError("source=mt5 1d exige ts exactamente a las 00:00Z")
            ny = ZoneInfo("America/New_York")
            por_ts = {ts: int(datetime.combine(datetime.fromtimestamp(int(ts) // 1000, timezone.utc).date(),
                                               time(17), ny).timestamp()) * 1000
                      for ts in df.loc[mt5_diaria, "ts_ms"].unique()}
            cierre.loc[mt5_diaria] = df.loc[mt5_diaria, "ts_ms"].map(por_ts)
    return cierre


def mayor_diferencia(df: pd.DataFrame, solo_cerradas: bool = True) -> dict | None:
    """La barra cuyo `close` mas cambia entre su primera y su ultima version recibida. Con `solo_cerradas` (por defecto) solo
    cuentan las versiones recibidas con la barra ya cerrada (el mismo criterio que `version_en_curso`): es la revision de un
    valor cerrado, lo que el proxy de disponibilidad al cierre no ve. Sin el, tambien las abiertas (incluye la evolucion de la
    barra antes de cerrar). None si ninguna barra cambia."""
    s = df.dropna(subset=["recv_ms"])
    if solo_cerradas:
        s = s[como_mascara(s["recv_ms"] >= cierre_version(s))]
    s = s.sort_values(["recv_ms", "orden"], kind="mergesort")
    g = s.groupby(CLAVE_OHLCV, sort=True)
    a, b = g[["close", "recv_ms"]].first(), g[["close", "recv_ms"]].last()
    rel = (b["close"] - a["close"]).abs() / a["close"]
    if not len(rel) or rel.max() <= 0:
        return None
    k = rel.idxmax()
    return {"instrument": k[0], "interval_ms": int(k[1]), "ts_ms": int(k[2]), "close_primera": float(a.loc[k, "close"]),
            "recv_primera_ms": int(a.loc[k, "recv_ms"]), "close_ultima": float(b.loc[k, "close"]),
            "recv_ultima_ms": int(b.loc[k, "recv_ms"]), "dif_relativa": float(rel.max()), "solo_cerradas": solo_cerradas}


def limpiar_ohlcv(df: pd.DataFrame, corte_ms: int, duplicados: str, c: dict, calendario: str | None = None,
                  disp_cierre: bool = False) -> pd.DataFrame:
    """Aplica los pasos a una tabla ohlcv/v1 en construccion y devuelve el DataFrame final, con las columnas de la tabla.

    `df`: instrument, interval_ms, ts_ms, open..volume, available_at_ms (Int64), orden y, en el lago, recv_ms (Int64) y source.
    `duplicados`: 'identicos' (solo se admiten filas repetidas iguales) o 'recepcion' (el lago: primera version ya cerrada,
    salvo MT5 1d: ultima completa recibida hasta el corte; sin marca, ultima del orden de qn y disponibilidad sin declarar).
    `calendario`: 'fx' separa los huecos del cierre semanal en el informe; None trata todo hueco como anomalo (24x7).
    En recepcion, disponibilidad = max(recv_ms, ts_ms + interval_ms), nunca antes del fin nominal (A12).
    `disp_cierre`: sustituye la disponibilidad por el cierre de la barra (proxy declarado como tal; solo para el lago).
    """
    df = df.sort_values(CLAVE_OHLCV + ["orden"], kind="mergesort")
    cierre = cierre_version(df)  # valida la rejilla MT5 incluso si los valores de la barra son invalidos
    # 1. validez de los valores
    for k in NUMERICAS:
        n = int(df[k].isna().sum())
        if n:
            c["detalle"].setdefault("nulo_o_nan_por_columna", {})[k] = n
    df = quitar(df, df[list(NUMERICAS)].isna().any(axis=1), "nulo_o_nan", c)
    df = quitar(df, np.isinf(df[list(NUMERICAS)].to_numpy(dtype=float)).any(axis=1), "infinito", c)
    df = quitar(df, (df[list(PRECIOS)] <= 0).any(axis=1), "precio_no_positivo", c)
    df = quitar(df, df["volume"] < 0, "volumen_negativo", c)
    # high < low es una barra imposible y se excluye; open/close fuera de [low, high] se conserva tal como la publica la fuente
    # (corregirla seria aproximar y quitarla abriria huecos): se cuenta aparte sobre las filas finales
    df = quitar(df, df["high"] < df["low"], "high_menor_que_low", c)
    # 2. una fila por (instrumento, intervalo, inicio de barra)
    valores = list(NUMERICAS)
    if duplicados == "recepcion" and df["recv_ms"].notna().any():
        del_dataset = df[(df["ts_ms"] + df["interval_ms"]) <= corte_ms]  # barras que pueden entrar en el dataset
        # entre versiones ya cerradas; si ninguna cambia, con las abiertas y marcado (`solo_cerradas` false) para el informe
        conocidas = del_dataset[~es_mt5_diaria(del_dataset) | (del_dataset["recv_ms"] <= corte_ms)]
        c["detalle"]["version_mayor_diferencia"] = mayor_diferencia(conocidas) or mayor_diferencia(conocidas, False)
        df = quitar(df, df["recv_ms"].isna(), "sin_marca_de_recepcion", c)
        df = quitar(df, df["recv_ms"] < cierre.loc[df.index], "version_en_curso", c)
        # A12 (correccion 3): las republicaciones MT5 1d son correcciones. El corte de recepcion precede a la
        # eleccion, tambien en modo cierre: una revision futura no puede desplazar a la ultima conocida.
        mt5 = es_mt5_diaria(df)
        df = quitar(df, mt5 & (df["recv_ms"] > corte_ms) & (df["ts_ms"] + df["interval_ms"] > corte_ms),
                    "posterior_al_corte_por_fecha", c)
        df = quitar(df, es_mt5_diaria(df) & (df["recv_ms"] > corte_ms), "posterior_al_corte_por_disponibilidad", c)
        mt5 = es_mt5_diaria(df)
        revisables = df.loc[mt5].sort_values(["recv_ms", "orden"], kind="mergesort")
        afectadas = []
        for clave, g in revisables[revisables.duplicated(CLAVE_OHLCV, keep=False)].groupby(CLAVE_OHLCV, sort=True):
            ultima = g.iloc[-1]
            afectadas.append({"instrument": clave[0], "ts_ms": int(clave[2]), "versiones_completas": len(g),
                              "recv_elegida_ms": int(ultima["recv_ms"]),
                              "available_at_recepcion_ms": max(int(ultima["recv_ms"]), int(clave[2]) + MS_DIA)})
        revisadas = elegir_version(revisables, CLAVE_OHLCV, ["recv_ms", "orden"], "ultima", valores, c, "version_mt5_revisada")
        if afectadas:
            c["detalle"]["version_mt5_revisada"].update(barras=len(afectadas), pares_y_fechas=afectadas)
        otras = elegir_version(df.loc[~mt5], CLAVE_OHLCV, ["recv_ms", "orden"], "primera", valores, c,
                               "version_posterior_descartada")
        df = pd.concat([revisadas, otras])
        # A12: una MT5 1d puede estar completa antes del fin nominal. La disponibilidad sigue siendo conservadora
        # y respeta DPOL-AVL-002 para toda barra; las recepciones posteriores al fin nominal no cambian.
        df["available_at_ms"] = df["recv_ms"].clip(lower=df["ts_ms"] + df["interval_ms"])
    elif duplicados == "recepcion":
        df = elegir_version(df, CLAVE_OHLCV, ["orden"], "ultima", valores, c, "version_anterior_descartada")
    else:
        df = elegir_version(df, CLAVE_OHLCV, ["orden"], "primera", valores, c, "duplicado")
        if c["detalle"].get("duplicado", {}).get("con_valores_distintos"):
            raise ValueError(f"filas repetidas con valores distintos y sin criterio para elegir: {c['detalle']['duplicado']}")
    # 3. corte: ni el cierre de la barra ni su disponibilidad pueden ser posteriores
    cierre = df["ts_ms"] + df["interval_ms"]
    if disp_cierre:  # ningun campo respalda la disponibilidad: queda nula y el manifest declara default_lag_ms = 0 (cierre + 0)
        df["available_at_ms"] = pd.array([None] * len(df), dtype="Int64")
    df = quitar(df, cierre > corte_ms, "posterior_al_corte_por_fecha", c)
    df = quitar(df, df["available_at_ms"] > corte_ms, "posterior_al_corte_por_disponibilidad", c)
    # 4. invariante: nunca disponible antes del cierre
    antes = como_mascara(df["available_at_ms"] < df["ts_ms"] + df["interval_ms"])
    if antes.any():
        raise AssertionError(f"{int(antes.sum())} barras con available_at_ms anterior a su cierre")
    df = df.sort_values(["ts_ms", "instrument"], kind="mergesort").reset_index(drop=True)
    c["volumen_cero"] = int((df["volume"] == 0).sum())
    fuera = como_mascara((df["high"] < df[["open", "close"]].max(axis=1)) | (df["low"] > df[["open", "close"]].min(axis=1)))
    if fuera.any():
        sobra = np.maximum.reduce([(df[k] - df["high"]).clip(lower=0).to_numpy() for k in ("open", "close")]
                                  + [(df["low"] - df[k]).clip(lower=0).to_numpy() for k in ("open", "close")])
        rel = (sobra / df["close"].to_numpy())[fuera]  # cuanto se sale del rango [low, high], relativo al cierre
        c["detalle"]["ohlc_incoherente_conservada"] = {"filas": int(fuera.sum()), "max_desvio_relativo": float(rel.max()),
                                                       "mediana_desvio_relativo": float(np.median(rel))}
    out = pd.DataFrame({
        "instrument": df["instrument"].astype(object), "ts_ms": df["ts_ms"].astype("int64"),
        "interval_ms": df["interval_ms"].astype("int64"), "open": df["open"].astype("float64"),
        "high": df["high"].astype("float64"), "low": df["low"].astype("float64"), "close": df["close"].astype("float64"),
        "volume": df["volume"].astype("float64"), "volume_kind": pd.Series(["traded"] * len(df), dtype=object),
        "available_at_ms": df["available_at_ms"].astype("Int64"), "revision": np.zeros(len(df), dtype="int32")})
    verificar_identidad(c, len(out))
    c["huecos"] = huecos(out, calendario)
    return out


def limpiar_custom(df: pd.DataFrame, corte_ms: int, c: dict) -> pd.DataFrame:
    """Igual para custom/v1. `df`: instrument, custom_type, ts_ms, data_json, available_at_ms (Int64), orden.
    Una fila por (instrumento, tipo, ts_ms): la primera disponible (empate: la primera en el orden del lago)."""
    df = df.sort_values(CLAVE_CUSTOM + ["orden"], kind="mergesort")
    df = quitar(df, df["available_at_ms"] < df["ts_ms"], "disponibilidad_anterior_al_evento", c)
    df["_sin_disp"] = df["available_at_ms"].isna()
    df = elegir_version(df, CLAVE_CUSTOM, ["_sin_disp", "available_at_ms", "orden"], "primera", ["data_json"], c,
                        "version_posterior_descartada")
    df = quitar(df, df["ts_ms"] > corte_ms, "posterior_al_corte_por_fecha", c)
    df = quitar(df, df["available_at_ms"] > corte_ms, "posterior_al_corte_por_disponibilidad", c)
    df = df.sort_values(["ts_ms", "instrument", "custom_type"], kind="mergesort").reset_index(drop=True)
    out = pd.DataFrame({
        "instrument": df["instrument"].astype(object), "custom_type": df["custom_type"].astype(object),
        "schema_version": np.ones(len(df), dtype="int32"), "ts_ms": df["ts_ms"].astype("int64"),
        "data_json": df["data_json"].astype(object), "available_at_ms": df["available_at_ms"].astype("Int64"),
        "revision": np.zeros(len(df), dtype="int32")})
    verificar_identidad(c, len(out))
    c["huecos_por_dia"] = huecos_diarios(out)
    return out


def en_fin_de_semana_fx(ts_ms: np.ndarray) -> np.ndarray:
    """Barras cuyo inicio cae en el cierre semanal del FX (vie 21:00 UTC a dom 22:00 UTC). Solo clasifica el informe."""
    semana = ((ts_ms // MS_DIA) + 3) % 7  # 0 = lunes (1970-01-01 fue jueves)
    hora = (ts_ms % MS_DIA) / MS_HORA
    return (semana == 5) | ((semana == 4) & (hora >= 21)) | ((semana == 6) & (hora < 22))


def huecos(df: pd.DataFrame, calendario: str | None = None) -> dict:
    """Huecos por instrumento (diferencias entre inicios consecutivos mayores que el intervalo). No se rellenan.
    `calendario='fx'` separa los huecos que caen en el cierre semanal del FX; sin calendario todo hueco es anomalo."""
    por_inst, tot = {}, {"huecos": 0, "barras_ausentes": 0, "huecos_de_fin_de_semana": 0, "fuera_de_rejilla": 0}
    for (inst, iv), g in df.groupby(["instrument", "interval_ms"], sort=True):
        ts = g["ts_ms"].to_numpy(dtype="int64")
        d = np.diff(ts)
        hay = d > iv
        ausentes = (d[hay] // iv) - 1
        fuera = ts[ts % iv != 0]  # barras que no empiezan en la rejilla UTC de su intervalo (se conservan y se cuentan)
        fin = 0
        if calendario == "fx":
            for i in np.flatnonzero(hay):
                faltan = ts[i] + iv * np.arange(1, d[i] // iv)
                fin += int(en_fin_de_semana_fx(faltan).all())
        r = {"intervalo_ms": int(iv), "barras": int(len(ts)), "huecos": int(hay.sum()),
             "barras_ausentes": int(ausentes.sum()), "mayor_hueco_barras": int(ausentes.max()) if len(ausentes) else 0,
             "huecos_de_fin_de_semana": fin, "fuera_de_rejilla": int(len(fuera)),
             "primera_fuera_de_rejilla_ms": int(fuera.min()) if len(fuera) else None,
             "ultima_fuera_de_rejilla_ms": int(fuera.max()) if len(fuera) else None}
        por_inst[f"{inst}|{int(iv)}"] = r
        for k in tot:
            tot[k] += r[k]
    return {"total": tot, "por_instrumento": por_inst}


def huecos_diarios(df: pd.DataFrame) -> dict:
    """Para las tablas de eventos (custom/v1): dias naturales sin ningun evento de un instrumento entre su primero y su ultimo."""
    por_inst, ausentes_total, huecos_total = {}, 0, 0
    for inst, g in df.groupby("instrument", sort=True):
        dias = np.unique(g["ts_ms"].to_numpy(dtype="int64") // MS_DIA)
        d = np.diff(dias)
        hay = d > 1
        ausentes = int((d[hay] - 1).sum())
        por_inst[inst] = {"eventos": int(len(g)), "dias_con_evento": int(len(dias)), "huecos_de_dias": int(hay.sum()),
                          "dias_ausentes": ausentes, "mayor_hueco_dias": int((d[hay] - 1).max()) if hay.any() else 0}
        ausentes_total += ausentes
        huecos_total += int(hay.sum())
    return {"total": {"huecos_de_dias": huecos_total, "dias_ausentes": ausentes_total}, "por_instrumento": por_inst}
