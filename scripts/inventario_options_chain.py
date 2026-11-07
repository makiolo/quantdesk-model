"""Inventario de SOLO LECTURA del histórico de `market.options.chain` en quantdesk-network (tarea TI-01-INV).

Por cada símbolo: primera y última fecha, días hábiles con datos frente a los esperables, cobertura, huecos de más de
`--gap` días hábiles, filas, vencimientos y strikes distintos. Solo hace GET; nunca publica.

Variables: QN_URLS (bases separadas por comas, p. ej. http://192.168.1.48:8790/qn; se usa la primera) y QN_TOKEN (permiso
`sub` sobre `market.>`). Uso:

    python scripts/inventario_options_chain.py --desde 2025-01-01
    python scripts/inventario_options_chain.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

TOPIC = "market.options.chain"


def get(base: str, token: str, path: str, params: dict) -> dict:
    url = f"{base}/api/v1{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def row_day(row: dict) -> date | None:
    """Fecha de la fila: el campo `date` del objeto o, si falta, la marca de evento."""
    d = row.get("date")
    if isinstance(d, str) and len(d) >= 10:
        return date.fromisoformat(d[:10])
    for k, v in row.items():
        if "ts" in k.lower() and isinstance(v, int):
            return datetime.fromtimestamp(v / 1e9, tz=timezone.utc).date()
        if "ts" in k.lower() and isinstance(v, str) and len(v) >= 10:
            return date.fromisoformat(v[:10])
    return None


def business_days(a: date, b: date) -> list[date]:
    out, d = [], a
    while d <= b:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def gaps(days: set[date], a: date, b: date, min_len: int) -> list[tuple[date, date, int]]:
    """Tramos de días hábiles sin datos de longitud >= min_len (festivos incluidos: es una cota superior)."""
    out, run = [], []
    for d in business_days(a, b):
        if d in days:
            if len(run) >= min_len:
                out.append((run[0], run[-1], len(run)))
            run = []
        else:
            run.append(d)
    if len(run) >= min_len:
        out.append((run[0], run[-1], len(run)))
    return out


def months(a: date, b: date):
    d = a.replace(day=1)
    while d <= b:
        nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        yield max(d, a), min(nxt - timedelta(days=1), b)
        d = nxt


def selftest() -> None:
    mon = date(2026, 1, 5)
    have = {mon, mon + timedelta(days=1), mon + timedelta(days=7)}
    g = gaps(have, mon, mon + timedelta(days=7), 2)
    assert g == [(date(2026, 1, 7), date(2026, 1, 9), 3)], g
    assert len(business_days(mon, mon + timedelta(days=6))) == 5
    assert row_day({"date": "2026-03-02"}) == date(2026, 3, 2)
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2024-01-01")
    ap.add_argument("--hasta", default=date.today().isoformat())
    ap.add_argument("--gap", type=int, default=3, help="huecos de al menos N días hábiles")
    ap.add_argument("--json", help="guardar el inventario completo en este fichero")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0

    base = os.environ.get("QN_URLS", "").split(",")[0].rstrip("/")
    token = os.environ.get("QN_TOKEN", "")
    if not base or not token:
        print("Faltan QN_URLS o QN_TOKEN", file=sys.stderr)
        return 2
    desde, hasta = date.fromisoformat(a.desde), date.fromisoformat(a.hasta)

    # Símbolos: los vistos en las dos últimas semanas y en todo el rango, mes a mes sin filtro sería caro.
    recent = get(base, token, f"/objects/{TOPIC}", {"from": (hasta - timedelta(days=14)).isoformat(), "to": hasta.isoformat()})
    symbols = sorted({r.get("symbol") for r in recent.get("rows", []) if r.get("symbol")})
    print(f"columnas: {[c['name'] for c in recent.get('columns', [])]}")
    print(f"símbolos vistos en las dos últimas semanas: {len(symbols)}")

    report = {}
    for sym in symbols:
        days, rows, mats, strikes = set(), 0, set(), set()
        for m0, m1 in months(desde, hasta):
            res = get(base, token, f"/objects/{TOPIC}",
                      {"symbol": sym, "from": m0.isoformat(), "to": (m1 + timedelta(days=1)).isoformat()})
            for r in res.get("rows", []):
                rows += 1
                d = row_day(r)
                if d:
                    days.add(d)
                mats.add(r.get("maturity"))
                strikes.add(r.get("strike"))
        if not days:
            print(f"{sym:10s} sin datos en el rango")
            continue
        first, last = min(days), max(days)
        expected = len(business_days(first, last))
        g = gaps(days, first, last, a.gap)
        report[sym] = {"first": first.isoformat(), "last": last.isoformat(), "days": len(days), "expected": expected,
                       "coverage": round(len(days) / expected, 3), "rows": rows, "maturities": len(mats),
                       "strikes": len(strikes), "gaps": [(x.isoformat(), y.isoformat(), n) for x, y, n in g]}
        print(f"{sym:10s} {first}→{last}  días {len(days)}/{expected} ({len(days) / expected:.0%})  filas {rows}  "
              f"venc. {len(mats)}  huecos≥{a.gap}: {len(g)} (mayor {max((n for *_, n in g), default=0)} días)")

    if report:
        print(f"\nsímbolos con datos: {len(report)}; primera fecha global: {min(v['first'] for v in report.values())}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"inventario guardado en {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
