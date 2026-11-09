"""Sufijos de simbolo del broker, nombre base normalizado, nombres de fichero sin colision y resolucion de nombres pedidos.

Regla de normalizacion (en este orden; se declara en el inventario):
1. Un prefijo `#` o `!` (acciones/CFD en algunos brokers) se separa como `prefijo`.
2. Si el simbolo empieza por `currency_base + currency_profit` (6 letras, FX y metales), eso es la base y el resto el
   sufijo: `EURUSD.a`, `EURUSDm`, `XAUUSD#`, `GBPUSD.pro`.
3. Si no, el primer separador (`.`, `_`, `#`, `+`, `!`, `-`) parte base y sufijo: `US30.cash`, `DE40_i`.
4. Si no, una cola de 1-4 minusculas tras un nucleo en mayusculas es sufijo: `US500m`.
5. Si no, no hay sufijo.
Dos simbolos con la misma base (`EURUSD` y `EURUSD.pro`) se marcan `base_compartida`: pedir por base es ambiguo.
"""
from __future__ import annotations

import hashlib
import re

_RESERVADOS = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


def normalizar(nombre: str, currency_base: str = "", currency_profit: str = "") -> dict:
    prefijo, n = "", nombre
    if n[:1] in ("#", "!") and len(n) > 1:
        prefijo, n = n[0], n[1:]
    par = f"{currency_base or ''}{currency_profit or ''}"
    if len(par) == 6 and n[:6].upper() == par.upper() and n[:6].isupper():
        base, sufijo, regla = n[:6], n[6:], "par de divisas"
    elif m := re.fullmatch(r"([A-Za-z0-9]+?)([._#+!-].*)", n):
        base, sufijo, regla = m.group(1), m.group(2), "separador"
    elif m := re.fullmatch(r"([A-Z0-9]{3,})([a-z]{1,4})", n):
        base, sufijo, regla = m.group(1), m.group(2), "cola en minusculas"
    else:
        base, sufijo, regla = n, "", "sin sufijo"
    return {"simbolo": nombre, "prefijo": prefijo, "base": base, "sufijo": sufijo, "regla_sufijo": regla}


def marcar_bases_compartidas(normalizados: list[dict]) -> None:
    cuenta: dict[str, int] = {}
    for d in normalizados:
        cuenta[d["base"].upper()] = cuenta.get(d["base"].upper(), 0) + 1
    for d in normalizados:
        d["base_compartida"] = cuenta[d["base"].upper()] > 1


def nombres_fichero(simbolos: list[str]) -> dict[str, str]:
    """Nombre de fichero por simbolo: caracteres seguros y sin colision en un disco que no distingue mayusculas."""
    limpio = {}
    for s in simbolos:
        f = re.sub(r"[^A-Za-z0-9._-]", "_", s).strip(".") or "_"
        if f.split(".")[0].upper() in _RESERVADOS:
            f = "_" + f
        limpio[s] = f
    grupos: dict[str, list[str]] = {}
    for s, f in limpio.items():
        grupos.setdefault(f.lower(), []).append(s)
    for miembros in grupos.values():
        if len(miembros) > 1 or limpio[miembros[0]] != miembros[0]:
            for s in miembros:  # el hash del nombre exacto desambigua y queda estable entre ejecuciones
                limpio[s] = f"{limpio[s]}~{hashlib.sha256(s.encode('utf-8')).hexdigest()[:8]}"
    return limpio


def resolver(pedidos: list[str], disponibles: dict[str, dict]) -> list[str]:
    """Nombres pedidos (exactos o por base) -> simbolos exactos del terminal. Ambiguo o inexistente: ValueError."""
    out: list[str] = []
    for p in pedidos:
        if p in disponibles:
            out.append(p)
            continue
        cands = sorted(s for s, d in disponibles.items() if d["base"].upper() == p.upper())
        if not cands:
            raise ValueError(f"{p}: no existe en el terminal ni como nombre exacto ni como base")
        if len(cands) > 1:
            raise ValueError(f"{p}: ambiguo, el terminal tiene {cands}; pide el nombre exacto")
        out.append(cands[0])
    return sorted(set(out))
