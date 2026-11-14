"""Oraculo independiente y casos de contrato; solamente qn falso y directorios temporales."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .qn_falso import TOKEN_PRUEBA, servidor

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/exportar_diario.py"


def ejecutar(tmp, base, *extra):
    env = {**os.environ, "QN_URLS": base, "QN_TOKEN": TOKEN_PRUEBA, "QN_ENV": "main",
           "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), "--ejecutar", "--sesion", "2026-11-12",
                           "--raiz-desktop", str(tmp / "desktop"), "--raiz-datasets", str(tmp / "datasets"),
                           "--runs", str(tmp / "runs"), *extra], cwd=REPO, env=env, capture_output=True,
                          text=True, encoding="utf-8", timeout=180)


def check(tmp):
    """El timestamp esperado sale de la convencion del publicador, no del JSON del qn falso."""
    from datetime import datetime, timezone
    import numpy as np
    import pyarrow.parquet as pq
    from quantdesk.data import open_vendor_dataset
    from publicador_mt5_lib.nucleo import sesion_1d
    from extractor_mt5_lib.hora import Regla, verano_us

    time_servidor = int(datetime(2026, 11, 12, tzinfo=timezone.utc).timestamp())
    expected, _ = sesion_1d(np.array([time_servidor]), Regla("NY+7", 7200, verano_us))
    assert int(expected[0]) == 1794441600000
    folder = tmp / "desktop/20261112/ohlcv"
    frame = pq.read_table(folder / "ohlcv_daily.parquet").to_pandas()
    assert len(frame) == 90 and not frame.duplicated(["symbol", "ts_ms"]).any()
    assert frame.equals(frame.sort_values(["symbol", "ts_ms"]).reset_index(drop=True))
    index = json.loads((folder / "index.json").read_text(encoding="utf-8"))
    sources = {s["symbol"]: s["source"] for s in index["symbols"]}
    for symbol, price, volume, source in (("FX.EURUSD", 1.0, 100.0, "mt5"),
                                         ("EQ.SPOT.AAPL", 128.0, 128.0, "market_scraper"),
                                         ("EQ.SPOT.SPX", 158.0, 158.0, "market_scraper")):
        row = frame[(frame.symbol == symbol) & (frame.ts_ms == expected[0])].iloc[0]
        assert row[["open", "high", "low", "close", "volume"]].tolist() == [price, price+1, price-.5, price+.25, volume]
        assert sources[symbol] == source
    roots = [p for p in (tmp / "datasets").iterdir() if not p.name.startswith(".")]
    assert len(roots) == 1
    ds = open_vendor_dataset(tmp / "datasets", roots[0].name, verify=True)
    table = ds.table("diario_ohlcv_1d")
    assert table.verified and table.row_count == len(frame)
    rows = {(r["instrument"], r["ts_ms"]): r for r in table.rows}
    for row in frame.to_dict("records"):
        r = rows[row["symbol"], row["ts_ms"]]
        assert all(r[k] == row[k] for k in ("open", "high", "low", "close", "volume"))
        assert r["volume_kind"] == ("tick_count" if sources[row["symbol"]] == "mt5" else "traded")


def prueba_oraculo(tmp):
    with servidor() as (base, estado):
        r = ejecutar(tmp, base)
        assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
        check(tmp)
        assert estado.publicados[-1]["obj"]["status"] == "ok"


def correr():
    with tempfile.TemporaryDirectory(prefix="ti02-diario-") as tmp:
        prueba_oraculo(Path(tmp))
    print("exportar_diario --selftest: oraculo OK")


if __name__ == "__main__":
    correr()
