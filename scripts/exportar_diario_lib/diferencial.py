"""Diferencial de datos contra Base; extrae solo Python a un temporal, nunca consulta qn.

Uso: .venv/Scripts/python.exe -X utf8 scripts/exportar_diario_lib/diferencial.py
Evidencia persistente: E:/quantdesk-lab/runs/TI-02-DIARIO/diferencial.json.
"""
from __future__ import annotations

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[2]
BASE = "aab7adec5aeed9d03865bd29df7572fdd4f0cdb6"
VENV = REPO / ".venv/Scripts/python.exe"


def correr(destino=Path("E:/quantdesk-lab/runs/TI-02-DIARIO/diferencial.json")):
    import os
    import pyarrow.parquet as pq
    sys.path.insert(0, str(REPO / "scripts"))
    from exportar_market_history_lib.selftests import escribir_volcado

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    # No se necesitan credenciales para este ensayo de ficheros locales.
    env.pop("QN_TOKEN", None)
    env.pop("QN_URLS", None)
    lab = Path("E:/quantdesk-lab/tmp")
    lab.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ti02-diferencial-", dir=lab) as tmp:
        root = Path(tmp)
        old = root / "base"
        paths = ["scripts/exportar_market_history.py", "scripts/exportar_market_history_lib", "scripts/descarga_lago.py",
                 "scripts/setup_env.py"]
        archive = subprocess.run(["git", "archive", "--format=zip", BASE, *paths], cwd=REPO,
                                 capture_output=True, check=True).stdout
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            z.extractall(old)

        def ns(dia, hora=0, minuto=0):
            return int(datetime(2026, 11, dia, hora, minuto, tzinfo=timezone.utc).timestamp()) * 10**9

        def barra(dia, recv, close=1.1):
            return {"_ts": ns(dia), "_recv_ts": recv, "_cycle": 7, "_offset": dia,
                    "_batch_id": f"00000000-0000-0000-0000-{dia:012d}", "date": f"2026-11-{dia:02d}",
                    "open": 1.0, "high": 2.0, "low": .5, "close": close, "volume": 123.0}

        filas = [barra(10, ns(10, 12), .8),                 # version incompleta
                 barra(10, ns(10, 23)),                   # primera completa
                 barra(10, ns(12, 23), 1.2),              # revision conocida antes de C
                 barra(10, ns(13, 1), 1.9),               # republicacion posterior al corte
                 barra(11, ns(11, 23)), barra(12, ns(12, 23))]
        dump = root / "lago"
        escribir_volcado(str(dump), {"market.ohlcv.v2": [
            ({"symbol": "EURUSD", "interval": "1d", "source": "mt5"}, filas),
            ({"symbol": "BTCUSDT", "interval": "1d", "source": "binance"}, [barra(10, ns(11, 0, 1), 1.3)])]})
        comandos = []
        for nombre, repo in (("base", old), ("nuevo", REPO)):
            args = [str(VENV), "-X", "utf8", str(repo / "scripts/exportar_market_history.py"), "--lago", str(dump),
                    "--corte", "2026-11-13", "--nombre", "diferencial", "--salida-raiz", str(root / nombre / "datasets"),
                    "--runs", str(root / nombre / "runs")]
            r = subprocess.run(args, cwd=repo, env=env, capture_output=True, text=True, encoding="utf-8", timeout=180)
            assert r.returncode == 0, (nombre, r.stdout, r.stderr)
            comandos.append({"version": nombre, "args": args, "exit": r.returncode})
        before = pq.read_table(root / "base/datasets/diferencial/lago_ohlcv_1d.parquet")
        after = pq.read_table(root / "nuevo/datasets/diferencial/lago_ohlcv_1d.parquet")
        assert before.schema == after.schema
        a, b = before.to_pylist(), after.to_pylist()
        assert len(a) == len(b) == 4
        cambios = []
        for r0, r1 in zip(a, b):
            keys = [k for k in r0 if r0[k] != r1[k]]
            if not keys:
                assert r1["instrument"] == "BTCUSDT" and r1["volume_kind"] == "traded"
                continue
            assert keys == ["volume_kind"] and r1["instrument"] == "EURUSD", (r0, r1)
            assert r0["volume_kind"] == "traded" and r1["volume_kind"] == "tick_count"
            cambios.append({"instrument": r1["instrument"], "ts_ms": r1["ts_ms"], "column": "volume_kind",
                            "before": "traded", "after": "tick_count", "reason": "source=mt5: volumen de ticks"})
        assert len(cambios) == 3
        # La correccion de volumen no puede seleccionar una revision futura o una version abierta.
        assert next(r for r in b if r["instrument"] == "EURUSD" and r["ts_ms"] == ns(10) // 10**6)["close"] == 1.2
        doc = {"base": BASE, "nuevo": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                                                     text=True, check=True).stdout.strip(),
               "rows_before": len(a), "rows_after": len(b), "added": 0, "removed": 0,
               "changes": cambios, "other_column_changes": 0, "commands": comandos,
               "derived_changes": "hashes logicos y fisicos derivados exclusivamente de volume_kind; informe actualizado"}
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"diferencial: {len(a)} filas; {len(cambios)} MT5 traded -> tick_count; Binance intacto; otras columnas=0")
        return doc


if __name__ == "__main__":
    correr()
