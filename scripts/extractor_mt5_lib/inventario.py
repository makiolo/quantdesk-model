"""Inventario de simbolos del terminal: sufijo y base normalizada, digitos, punto, precio de las velas, profundidad por
periodo (1 m, 5 m, 1 h, 1 d) y si hay ticks. Solo consultas de la lista blanca.

Profundidad: UNA consulta `copy_rates_from_pos(simbolo, periodo, 0, maxbars - 1)` (la posicion 0 es la vela actual): el
terminal devuelve min(count, disponibles). La profundidad es su longitud y la primera y la ultima vela salen del array, que
se libera enseguida (en m1 son ~100k filas). Medido en el terminal real (build 6230): una posicion fuera de la historia da
-1 'Call failed', el mismo codigo que la sincronizacion pendiente, asi que no se puede biseccionar con consultas de una
vela; y count = maxbars da -2 'Invalid params', asi que nunca se pide. El terminal solo sirve las velas que caben en "Max.
bars in chart" (`terminal_info().maxbars`): si la profundidad llega a maxbars - 1 se marca `limitada_por_maxbars` y la
historia real del broker puede ser mayor. Todas las consultas pasan por `descarga.consultar` (reintentos ante -1 y
-10005). Si un periodo sigue con -1 tras los reintentos (simbolo sin historia en ese periodo), se apunta con `velas` 0 y
`error`, y el inventario sigue. Ticks: se cuentan los de una ventana de `dias_ticks` dias que acaba en la ultima vela de 1 m.
"""
from __future__ import annotations

import numpy as np

from . import descarga as D
from . import hora as HR
from . import simbolos as SB

PERIODOS_INV = ("m1", "m5", "h1", "d1")
FX28 = ("EURGBP", "EURAUD", "EURNZD", "EURUSD", "EURCAD", "EURCHF", "EURJPY", "GBPAUD", "GBPNZD", "GBPUSD", "GBPCAD",
        "GBPCHF", "GBPJPY", "AUDNZD", "AUDUSD", "AUDCAD", "AUDCHF", "AUDJPY", "NZDUSD", "NZDCAD", "NZDCHF", "NZDJPY",
        "USDCAD", "USDCHF", "USDJPY", "CADCHF", "CADJPY", "CHFJPY")  # los 28 cruces del lago (TI-01-INV)
LIQUIDOS = ("EURUSD", "USDJPY", "GBPUSD")


def cuenta_maxima(maxbars: int) -> int:
    """El count mas grande que acepta `copy_rates_from_pos`: maxbars - 1 (con maxbars da -2 'Invalid params')."""
    return max(1, min(int(maxbars), 2 ** 31 - 1) - 1)


def profundidad(term, sim: str, periodo: str, maxbars: int, regla: HR.Regla) -> dict:
    tf = getattr(term, D.PERIODOS[periodo]["tf"])
    pedir = cuenta_maxima(maxbars)
    try:
        arr = D.consultar(term, "copy_rates_from_pos", sim, tf, 0, pedir)
    except D.ErrorTerminal as e:
        if e.codigo != -1:  # -2, -10005 persistente u otro: no es "sin historia", se para como siempre
            raise
        return {"velas": 0, "error": "Call failed tras los reintentos (sin historia en este periodo o sin sincronizar)"}
    if arr is None or len(arr) == 0:
        return {"velas": 0}
    n = len(arr)
    s = np.array([int(arr["time"][0]), int(arr["time"][-1])], dtype=np.int64)
    del arr  # en m1 son ~100k filas: fuera cuanto antes
    u = regla.servidor_a_utc(s)[0]
    return {"velas": n, "primera_utc": HR.iso(int(u[0]) * 1000), "ultima_utc": HR.iso(int(u[1]) * 1000),
            "ultima_servidor_s": int(s[1]), "limitada_por_maxbars": n >= pedir}


def info_simbolo(term, s) -> dict:
    n = SB.normalizar(s.name, s.currency_base, s.currency_profit)
    n.update(ruta=s.path, descripcion=s.description, digitos=int(s.digits), punto=float(s.point),
             precio_velas="last" if s.chart_mode == term.SYMBOL_CHART_MODE_LAST else "bid",
             divisa_base=s.currency_base, divisa_beneficio=s.currency_profit, visible=bool(s.visible))
    return n


def simbolos_disponibles(term, grupo: str | None) -> dict:
    lista = D.consultar(term, "symbols_get", group=grupo) if grupo else D.consultar(term, "symbols_get")
    infos = [info_simbolo(term, s) for s in (lista or ())]
    SB.marcar_bases_compartidas(infos)
    return {d["simbolo"]: d for d in sorted(infos, key=lambda d: d["simbolo"])}


def inventario(term, regla: HR.Regla, ahora_utc_s: int, procedencia: dict, maxbars: int, grupo: str | None = None,
               pedidos: list[str] | None = None, con_profundidad: bool = True, dias_ticks: int = 3, progreso=None) -> dict:
    todos = simbolos_disponibles(term, grupo)
    elegidos = SB.resolver(pedidos, todos) if pedidos else sorted(todos)
    filas = []
    for k, sim in enumerate(elegidos):
        d = dict(todos[sim])
        if con_profundidad:
            d["profundidad"] = {p: profundidad(term, sim, p, maxbars, regla) for p in PERIODOS_INV}
            ref = d["profundidad"]["m1"].get("ultima_servidor_s") or regla.utc_a_servidor(ahora_utc_s)
            tk = D.consultar(term, "copy_ticks_range", sim, ref - dias_ticks * 86400, ref + 60, term.COPY_TICKS_ALL)
            n = 0 if tk is None else len(tk)
            d["ticks"] = {"hay": n > 0, "ventana_dias": dias_ticks, "ticks_en_ventana": n}
        filas.append(d)
        if progreso:
            progreso(k + 1, len(elegidos), sim)
    vivos = [s for s in elegidos if todos[s]["base"].upper() in LIQUIDOS] or \
            [s for s in sorted(todos) if todos[s]["base"].upper() in LIQUIDOS and not todos[s]["base_compartida"]][:3]
    return {"formato": "quantdesk-lab.mt5-inventario/v1", "tarea": "TI-12-MT5", "ahora_utc": HR.iso(ahora_utc_s * 1000),
            "grupo": grupo or "*", "procedencia": procedencia, "regla_hora": regla.describir(),
            "deteccion_desfase_en_vivo": HR.detectar_en_vivo(term, vivos[:3], ahora_utc_s, regla),
            "simbolos_en_terminal": len(todos), "simbolos": filas, "resumen": resumen(filas, len(todos))}


def resumen(filas: list[dict], total: int) -> dict:
    sufijos: dict[str, int] = {}
    for d in filas:
        sufijos[d["sufijo"] or "(ninguno)"] = sufijos.get(d["sufijo"] or "(ninguno)", 0) + 1
    out = {"simbolos_en_terminal": total, "simbolos_inventariados": len(filas),
           "sufijos": dict(sorted(sufijos.items(), key=lambda kv: (-kv[1], kv[0]))),
           "velas_de_last": sum(d["precio_velas"] == "last" for d in filas),
           "bases_compartidas": sorted({d["base"] for d in filas if d.get("base_compartida")})}
    if filas and "profundidad" in filas[0]:
        out["con_ticks"] = sum(d["ticks"]["hay"] for d in filas)
        for p in PERIODOS_INV:
            prim = sorted(d["profundidad"][p]["primera_utc"] for d in filas if d["profundidad"][p].get("velas"))
            out[f"{p}_primera_utc_mediana"] = prim[len(prim) // 2] if prim else None
            out[f"{p}_limitadas_por_maxbars"] = sum(bool(d["profundidad"][p].get("limitada_por_maxbars")) for d in filas)
    return out


def texto_resumen(inv: dict) -> str:
    r = inv["resumen"]
    v = inv["deteccion_desfase_en_vivo"]
    lineas = [f"inventario: {r['simbolos_inventariados']} de {r['simbolos_en_terminal']} simbolos; sufijos {r['sufijos']}",
              f"  velas de Last: {r['velas_de_last']}; bases compartidas: {len(r['bases_compartidas'])}"]
    if "con_ticks" in r:
        lineas.append(f"  con ticks: {r['con_ticks']}; limitadas por maxbars m1/m5/h1/d1: "
                      + "/".join(str(r[f'{p}_limitadas_por_maxbars']) for p in PERIODOS_INV))
        lineas.append("  primera vela (mediana) m1/m5/h1/d1: "
                      + " / ".join(str(r[f'{p}_primera_utc_mediana']) for p in PERIODOS_INV))
    lineas.append(f"  desfase en vivo: mercado abierto={v['mercado_fx_abierto']} observaciones={v['observaciones']} "
                  f"regla={v['desfase_regla_h']} h concluyente={v['concluyente']} coincide={v['coincide']}")
    return "\n".join(lineas)
