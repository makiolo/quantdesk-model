"""Clases de sesion, festivos de bolsa y huecos de mercado de la vela 1d (TI-12-MT5, fase C).

La vela 1d de MT5 de este broker abre siempre a las 00:00 del servidor (medido en el terminal real: fx, indices y
cripto), y el servidor va a Nueva York + 7 h. Por eso, para TODAS las clases:
- la SESION de una vela 1d es la fecha del servidor de su apertura;
- la vela esta cerrada cuando el servidor pasa al dia siguiente (00:00 del servidor = 17:00 de Nueva York).
En FX es exactamente la regla publicada hasta ahora (fecha de Nueva York del cierre de las 17:00): ver fase-c.md.

Lo que cambia por clase es que dias se esperan (para no contar como huecos los que no son de mercado):
- forex: lunes a viernes; los huecos se clasifican con el metodo de siempre (`descarga.huecos`).
- metales_energia: lunes a viernes, festivos del CME (1 ene, Viernes Santo, 25 dic).
- indices: lunes a viernes, festivos de la bolsa de cada indice (`BOLSA_INDICE`).
- acciones_us: lunes a viernes, festivos de la NYSE (reglas y cierres extraordinarios desde 1990).
- acciones_us_24: las `-24` (24/5) que entran en us_grandes porque el broker no tiene su version de sesion normal. Mismo
  calendario que acciones_us (NYSE). La vela de D va de las 17:00 NY de D-1 a las 17:00 NY de D: lleva la nocturna, la
  preapertura, la sesion de D y la primera hora del despues del cierre. Si el broker cotiza el viernes despues de las
  17:00 NY, esa cola cae en sabado del servidor: se cuenta en `sesiones_fin_de_semana` (solo se informa).
- crypto: los siete dias; un sabado o domingo sin vela se cuenta como fin de semana (el broker no daba cripto en fin de
  semana en su historia antigua), no como hueco.
Los festivos son reglas (fechas fijas con su traslado, Pascua, n-esimo dia de la semana). No hay tablas lunares: un
hueco de 1 a 3 dias laborables que no esta en el calendario de una clase con bolsa se cuenta como `festivos_probables`,
no como `otros`. Los huecos solo se informan: nunca paran la publicacion ni la descarga.
"""
from __future__ import annotations

import datetime as dt
import functools

import numpy as np

DIA = 86400
EPOCA = dt.date(1970, 1, 1)
CLASES = ("forex", "metales_energia", "indices", "crypto", "acciones_us", "acciones_us_24")
CON_BOLSA = ("metales_energia", "indices", "acciones_us", "acciones_us_24")
MAX_PROBABLE = 3  # dias laborables seguidos fuera del calendario que aun se cuentan como festivo probable

# Bolsa (calendario) de cada indice al contado del broker.
BOLSA_INDICE = {
    "AUS200": "ASX", "CA60": "TSX", "CHINA50": "SGX", "CHINAH": "HKEX", "HK50": "HKEX", "DE40": "XETRA",
    "MidDE50": "XETRA", "TecDE30": "XETRA", "STOXX50": "XETRA", "ES35": "BME", "F40": "EURONEXT", "NETH25": "EURONEXT",
    "IT40": "MIL", "JP225": "JPX", "NOR25": "OSLO", "SA40": "JSE", "SE30": "STO", "SWI20": "SIX", "UK100": "LSE",
    "US2000": "NYSE", "US30": "NYSE", "US500": "NYSE", "USTEC": "NYSE",
}
BOLSA_CLASE = {"metales_energia": "CME", "acciones_us": "NYSE", "acciones_us_24": "NYSE"}


def pascua(anio: int) -> dt.date:
    """Domingo de Pascua (calendario gregoriano, algoritmo anonimo)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    lc = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * lc) // 451
    mes = (h + lc - 7 * m + 114) // 31
    return dt.date(anio, mes, (h + lc - 7 * m + 114) % 31 + 1)


def enesimo(anio: int, mes: int, dia_semana: int, n: int) -> dt.date:
    """n-esimo `dia_semana` (0 = lunes) del mes; n = -1, el ultimo."""
    if n > 0:
        d = dt.date(anio, mes, 1)
        return d + dt.timedelta(days=(dia_semana - d.weekday()) % 7 + 7 * (n - 1))
    d = dt.date(anio + (mes == 12), mes % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - dia_semana) % 7)


def _obs_viernes_lunes(d: dt.date) -> dt.date:
    """Sabado -> viernes antes, domingo -> lunes despues (EE. UU.)."""
    return d - dt.timedelta(days=1) if d.weekday() == 5 else d + dt.timedelta(days=1) if d.weekday() == 6 else d


def _obs_lunes(dias: list[dt.date]) -> set[dt.date]:
    """Festivos en fin de semana se trasladan al siguiente laborable libre (Reino Unido, Australia, Canada...)."""
    out: set[dt.date] = set()
    for d in sorted(dias):
        while d.weekday() >= 5 or d in out:
            d += dt.timedelta(days=1)
        out.add(d)
    return out


def _nyse(a: int) -> set[dt.date]:
    p = pascua(a)
    out = {p - dt.timedelta(days=2), enesimo(a, 2, 0, 3), enesimo(a, 5, 0, -1), _obs_viernes_lunes(dt.date(a, 7, 4)),
           enesimo(a, 9, 0, 1), enesimo(a, 11, 3, 4), _obs_viernes_lunes(dt.date(a, 12, 25))}
    if dt.date(a, 1, 1).weekday() != 5:  # 1 de enero en sabado: la NYSE no cierra el viernes 31
        out.add(_obs_viernes_lunes(dt.date(a, 1, 1)))
    if a >= 1998:
        out.add(enesimo(a, 1, 0, 3))  # Martin Luther King
    if a >= 2022:
        out.add(_obs_viernes_lunes(dt.date(a, 6, 19)))  # Juneteenth
    return out


NYSE_EXTRAORDINARIOS = {dt.date(1994, 4, 27), dt.date(2001, 9, 11), dt.date(2001, 9, 12), dt.date(2001, 9, 13),
                        dt.date(2001, 9, 14), dt.date(2004, 6, 11), dt.date(2007, 1, 2), dt.date(2012, 10, 29),
                        dt.date(2012, 10, 30), dt.date(2018, 12, 5), dt.date(2025, 1, 9)}


def _europa(a: int, extra: tuple = ()) -> set[dt.date]:
    p = pascua(a)
    return {dt.date(a, 1, 1), p - dt.timedelta(days=2), p + dt.timedelta(days=1), dt.date(a, 5, 1), dt.date(a, 12, 25),
            dt.date(a, 12, 26), *extra}


def _japon(a: int) -> set[dt.date]:
    y = a - 1980
    prim = dt.date(a, 3, int(20.8431 + 0.242194 * y - y // 4))
    oto = dt.date(a, 9, int(23.2488 + 0.242194 * y - y // 4))
    fijos = [dt.date(a, 1, 1), dt.date(a, 1, 2), dt.date(a, 1, 3), dt.date(a, 2, 11), dt.date(a, 4, 29), dt.date(a, 5, 3),
             dt.date(a, 5, 4), dt.date(a, 5, 5), dt.date(a, 11, 3), dt.date(a, 11, 23), dt.date(a, 12, 31), prim, oto,
             enesimo(a, 1, 0, 2), enesimo(a, 7, 0, 3), enesimo(a, 9, 0, 3), enesimo(a, 10, 0, 2)]
    if a >= 2020:
        fijos.append(dt.date(a, 2, 23))
    if a >= 2016:
        fijos.append(dt.date(a, 8, 11))
    return _obs_lunes(fijos)


def _reglas(bolsa: str, a: int) -> set[dt.date]:
    p = pascua(a)
    viernes_santo, lunes_pascua = p - dt.timedelta(days=2), p + dt.timedelta(days=1)
    if bolsa == "NYSE":
        return _nyse(a) | {d for d in NYSE_EXTRAORDINARIOS if d.year == a}
    if bolsa == "CME":
        return {dt.date(a, 1, 1), viernes_santo, dt.date(a, 12, 25)}
    if bolsa == "ASX":
        return _obs_lunes([dt.date(a, 1, 1), dt.date(a, 1, 26), dt.date(a, 12, 25), dt.date(a, 12, 26)]) | {
            viernes_santo, lunes_pascua, dt.date(a, 4, 25), enesimo(a, 6, 0, 2)}
    if bolsa == "TSX":
        victoria = dt.date(a, 5, 24) - dt.timedelta(days=dt.date(a, 5, 24).weekday())
        return _obs_lunes([dt.date(a, 1, 1), dt.date(a, 7, 1), dt.date(a, 12, 25), dt.date(a, 12, 26)]) | {
            enesimo(a, 2, 0, 3), viernes_santo, victoria, enesimo(a, 8, 0, 1), enesimo(a, 9, 0, 1), enesimo(a, 10, 0, 2)}
    if bolsa == "LSE":
        return _obs_lunes([dt.date(a, 1, 1), dt.date(a, 12, 25), dt.date(a, 12, 26)]) | {
            viernes_santo, lunes_pascua, enesimo(a, 5, 0, 1), enesimo(a, 5, 0, -1), enesimo(a, 8, 0, -1)}
    if bolsa == "XETRA":
        return _europa(a, (dt.date(a, 12, 24), dt.date(a, 12, 31)))
    if bolsa in ("EURONEXT", "BME"):
        return _europa(a)
    if bolsa == "MIL":
        return _europa(a, (dt.date(a, 12, 24), dt.date(a, 12, 31), dt.date(a, 8, 15)))
    if bolsa == "SIX":
        return _europa(a, (dt.date(a, 1, 2), p + dt.timedelta(days=39), p + dt.timedelta(days=50), dt.date(a, 8, 1),
                           dt.date(a, 12, 24), dt.date(a, 12, 31)))
    if bolsa == "OSLO":
        return _europa(a, (p - dt.timedelta(days=3), dt.date(a, 5, 17), p + dt.timedelta(days=39),
                           p + dt.timedelta(days=50), dt.date(a, 12, 24), dt.date(a, 12, 31)))
    if bolsa == "STO":
        midsommar = dt.date(a, 6, 19) + dt.timedelta(days=(4 - dt.date(a, 6, 19).weekday()) % 7)
        return _europa(a, (dt.date(a, 1, 6), p + dt.timedelta(days=39), dt.date(a, 6, 6), midsommar, dt.date(a, 12, 24),
                           dt.date(a, 12, 31)))
    if bolsa == "JSE":
        return _obs_lunes([dt.date(a, 1, 1), dt.date(a, 3, 21), dt.date(a, 4, 27), dt.date(a, 5, 1), dt.date(a, 6, 16),
                           dt.date(a, 8, 9), dt.date(a, 9, 24), dt.date(a, 12, 16), dt.date(a, 12, 25),
                           dt.date(a, 12, 26)]) | {viernes_santo, lunes_pascua}
    if bolsa == "JPX":
        return _japon(a)
    if bolsa == "HKEX":  # sin el Ano Nuevo lunar ni las fiestas lunares: van a festivos_probables
        return _obs_lunes([dt.date(a, 1, 1), dt.date(a, 5, 1), dt.date(a, 7, 1), dt.date(a, 10, 1), dt.date(a, 12, 25),
                           dt.date(a, 12, 26)]) | {viernes_santo, lunes_pascua}
    if bolsa == "SGX":  # sin las fiestas lunares ni las moviles de Singapur
        return _obs_lunes([dt.date(a, 1, 1), dt.date(a, 5, 1), dt.date(a, 8, 9), dt.date(a, 12, 25)]) | {viernes_santo}
    raise ValueError(f"bolsa sin calendario: {bolsa}")


BOLSAS = ("NYSE", "CME", "ASX", "TSX", "LSE", "XETRA", "EURONEXT", "BME", "MIL", "SIX", "OSLO", "STO", "JSE", "JPX",
          "HKEX", "SGX")


@functools.lru_cache(maxsize=None)
def festivos(bolsa: str, anio: int) -> frozenset:
    return frozenset(d for d in _reglas(bolsa, anio) if d.weekday() < 5)


def es_festivo(bolsa: str | None, d: dt.date) -> bool:
    return bolsa is not None and d in festivos(bolsa, d.year)


def bolsa_de(clase: str | None, base: str) -> str | None:
    if clase == "indices":
        return BOLSA_INDICE.get(base)
    return BOLSA_CLASE.get(clase)


def fecha(dia: int) -> dt.date:
    return EPOCA + dt.timedelta(days=int(dia))


def huecos_sesiones(dias, clase: str, bolsa: str | None) -> dict:
    """Huecos entre sesiones 1d consecutivas (`dias`: dias desde 1970 de la sesion, crecientes). Cada dia que falta se
    clasifica: fin de semana (sabado o domingo), festivo del calendario, festivo probable (racha de 1 a 3 laborables
    fuera del calendario en una clase con bolsa) u otros. Mismas claves que `descarga.huecos` mas las de festivos."""
    out = {"metodo": "sesiones 1d por clase", "clase": clase, "bolsa": bolsa, "fin_de_semana": 0,
           "fin_de_semana_ampliado": 0, "festivos": 0, "festivos_probables": 0, "otros": 0, "otros_pasos_faltantes": 0,
           "otros_por_tamano": {"<=5 pasos": 0, "<=60 pasos": 0, ">60 pasos": 0}, "otros_mayores": [],
           "festivos_probables_dias": []}
    dias = np.asarray(dias, dtype=np.int64)
    if clase == "acciones_us_24":  # velas con fecha de sabado o domingo del servidor (la cola del viernes): se cuentan
        out["sesiones_fin_de_semana"] = int(((dias + 3) % 7 >= 5).sum())
    if dias.size < 2:
        return out
    rachas = []  # rachas de laborables que faltan y no estan en el calendario
    for k in np.nonzero(np.diff(dias) > 1)[0]:
        racha = []
        for d in range(int(dias[k]) + 1, int(dias[k + 1])):
            f = fecha(d)
            if f.weekday() >= 5:
                out["fin_de_semana"] += 1
                if racha:
                    rachas.append(racha)
                    racha = []
            elif es_festivo(bolsa, f):
                out["festivos"] += 1
                if racha:
                    rachas.append(racha)
                    racha = []
            else:
                racha.append(d)
        if racha:
            rachas.append(racha)
    con_bolsa = clase in CON_BOLSA
    otras = []
    for r in rachas:
        if con_bolsa and len(r) <= MAX_PROBABLE:
            out["festivos_probables"] += len(r)
            out["festivos_probables_dias"].extend(fecha(d).isoformat() for d in r)
        else:
            otras.append(r)
    out["festivos_probables_dias"] = out["festivos_probables_dias"][-20:]
    out["otros"] = len(otras)
    pasos = np.array([len(r) for r in otras], dtype=np.int64)
    out["otros_pasos_faltantes"] = int(pasos.sum())
    out["otros_por_tamano"] = {"<=5 pasos": int((pasos <= 5).sum()), "<=60 pasos": int(((pasos > 5) & (pasos <= 60)).sum()),
                               ">60 pasos": int((pasos > 60).sum())}
    out["otros_mayores"] = [{"desde": fecha(r[0]).isoformat(), "hasta": fecha(r[-1]).isoformat(), "pasos": len(r)}
                            for r in sorted(otras, key=lambda r: (-len(r), r[0]))[:5]]
    return out
