"""Oraculo independiente y casos de contrato; solamente qn falso y directorios temporales."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import copy
from contextlib import redirect_stdout, redirect_stderr
from datetime import date, datetime, timedelta, timezone
import io
import re
import socket
import uuid
from unittest.mock import patch

from .qn_falso import TOKEN_PRUEBA, Estado, servidor

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/exportar_diario.py"


def ejecutar(tmp, base, *extra):
    env = {**os.environ, "QN_URLS": base, "QN_TOKEN": TOKEN_PRUEBA, "QN_ENV": "main",
           "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([str(REPO / ".venv/Scripts/python.exe"), "-X", "utf8", str(SCRIPT), "--ejecutar", "--sesion", "2026-11-12",
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
    from extractor_mt5_lib.hora import Regla, verano_ee_uu

    time_servidor = int(datetime(2026, 11, 12, tzinfo=timezone.utc).timestamp())
    expected, _ = sesion_1d(np.array([time_servidor]), Regla("NY+7", 7200, verano_ee_uu))
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


def local(tmp, base, *extra, entorno=None, verificar_secretos=True):
    from exportar_diario import main
    args = ["--ejecutar", "--sesion", "2026-11-12", "--raiz-desktop", str(tmp / "desktop"),
            "--raiz-datasets", str(tmp / "datasets"), "--runs", str(tmp / "runs"),
            "--env-file", str(tmp / "privado.env"), *extra]
    out = io.StringIO()
    env = {"QN_URLS": base, "QN_TOKEN": TOKEN_PRUEBA, "QN_ENV": "main"} if entorno is None else entorno
    with redirect_stdout(out), redirect_stderr(out), patch("descarga_lago.time.sleep"):
        code = main(args, env)
    assert TOKEN_PRUEBA not in out.getvalue() and not re.search(r"qn_", out.getvalue())
    if verificar_secretos:
        secretos(tmp)
    return code, out.getvalue()


def secretos(tmp):
    for p in tmp.rglob("*"):
        if p.is_file() and p.name != "privado.env":
            raw = p.read_bytes()
            assert TOKEN_PRUEBA.encode() not in raw and b"qn_" not in raw, p


def intentos(tmp):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((tmp / "runs").glob("*.integridad.json"))]


def comprobar_estado(tmp, estado, status):
    from .nucleo import sha
    publicado = estado.publicados[-1]
    obj = publicado["obj"]
    assert obj["status"] == status, obj
    path = next((tmp / "runs").glob("*" + obj["manifest_sha256"] + ".integridad.json"))
    assert sha(path.read_bytes()) == obj["manifest_sha256"]
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == status
    assert publicado["batch_id"] == str(uuid.uuid5(uuid.NAMESPACE_URL,
        "ti02-diario|" + obj["session"] + "|" + obj["manifest_sha256"]))
    assert len(obj["detail"]) <= 500


def sin_productos(tmp):
    assert not any((tmp / "desktop").rglob("*")), list((tmp / "desktop").rglob("*"))
    assert not any((tmp / "datasets").rglob("*")), list((tmp / "datasets").rglob("*"))


def foto_productos(tmp):
    from .nucleo import sha
    return {p.relative_to(tmp).as_posix(): (sha(p.read_bytes()), p.stat().st_mtime_ns)
            for raiz in (tmp / "desktop", tmp / "datasets") for p in raiz.rglob("*") if p.is_file()}


def dia(row):
    return row["_ts"][:10]


def nueva_sesion(e, session):
    delta = date.fromisoformat(session) - date(2026, 11, 12)
    for r in e.datos["rows"]:
        for key in ("_ts", "_recv_ts"):
            r[key] = (datetime.fromisoformat(r[key].replace("Z", "+00:00")) + delta).isoformat().replace("+00:00", "Z")
        r["date"] = dia(r)


def prueba_sin_sesion(tmp):
    for session in ("2026-11-14", "2026-11-15"):
        with servidor() as (base, e):
            root = tmp / session
            assert local(root, base, "--sesion", session)[0] == 1
            sin_productos(root)
            assert not e.peticion and not e.publicados
            assert "sin sesión" in intentos(root)[0]["detail"]
    # Las ejecuciones del domingo/lunes eligen sabado/domingo UTC sin saltar al viernes.
    from exportar_diario import main
    for ejecucion, esperado in (("2026-11-15", "2026-11-14"), ("2026-11-16", "2026-11-15")):
        class Reloj(datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime.fromisoformat(ejecucion + "T00:15:00+00:00")
        recibidos = []
        with patch("exportar_diario.datetime", Reloj), patch("exportar_diario_lib.nucleo.exportar",
                side_effect=lambda a, *_: recibidos.append(a.sesion) or 1):
            main(["--ejecutar", "--runs", str(tmp / "defaults")], {"QN_URLS": "http://127.0.0.1:1/qn", "QN_TOKEN": TOKEN_PRUEBA})
        assert recibidos == [esperado]


def prueba_previa(tmp):
    for caso in ("parcial", "parado", "recepcion_corte", "ultimo_antiguo", "solo_yfinance"):
        with servidor() as (base, e):
            root = tmp / caso
            if caso == "parcial":
                e.datos["rows"] = [r for r in e.datos["rows"] if not (r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")]
            elif caso == "parado":
                e.datos["rows"] = [r for r in e.datos["rows"] if not (r["source"] == "mt5" and dia(r) == "2026-11-12")]
            elif caso == "recepcion_corte":
                next(r for r in e.datos["rows"] if r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")["_recv_ts"] = "2026-11-13T00:00:00Z"
            elif caso == "ultimo_antiguo":
                e.datos["rows"] = [r for r in e.datos["rows"] if not (r["symbol"] == "GBPUSD" and dia(r) == "2026-11-12")]
            else:
                for r in e.datos["rows"]:
                    if r["symbol"] == "EURUSD":
                        r["source"] = "yfinance"
            assert local(root, base)[0] == 3, caso
            sin_productos(root)
            comprobar_estado(root, e, "sin_mt5")
            assert not any("/objects/" in p for p, _ in e.peticion)
            filtros = [q for p, q in e.peticion if q.get("source") == "mt5"]
            assert len(filtros) == 28 and all(q["interval"] == "1d" for q in filtros)


def prueba_festivos(tmp):
    for session in ("2026-12-25", "2027-01-01"):
        for con_barras in (False, True):
            with servidor() as (base, e):
                nueva_sesion(e, session)
                if not con_barras:
                    e.datos["rows"] = [r for r in e.datos["rows"] if r["source"] != "mt5" or dia(r) != session]
                root = tmp / (session + str(con_barras))
                assert local(root, base, "--sesion", session)[0] == 0
                comprobar_estado(root, e, "ok")
                if not con_barras:
                    sin_productos(root)
                    assert "festivo FX: sin sesión" in e.publicados[-1]["obj"]["detail"]
                else:
                    assert list((root / "desktop").rglob("*.parquet"))
                assert not any("symbol" in q and p.endswith("latest") for p, q in e.peticion)
    with servidor() as (base, e):
        nueva_sesion(e, "2026-11-26")
        e.datos["rows"] = [r for r in e.datos["rows"] if r["source"] == "mt5" or dia(r) != "2026-11-26"]
        root = tmp / "nyse"
        assert local(root, base, "--sesion", "2026-11-26")[0] == 0
        coverage = intentos(root)[0]["coverage"]
        aapl = next(c for c in coverage if c["symbol"] == "EQ.SPOT.AAPL")
        assert "2026-11-26" in aapl["expected_absences"] and "2026-11-26" not in aapl["gaps"]
    from . import politica as P
    mapa = copy.deepcopy(P.MAPA)
    mapa["^GSPC"]["calendar"] = None
    # El calendario del alias SPX debe concordar con el del instrumento.
    mapa["SPX"]["calendar"] = None
    with servidor() as (base, e), patch.object(P, "MAPA", mapa):
        root = tmp / "calendario_desconocido"
        assert local(root, base)[0] == 0
        assert any("calendario desconocido" in a for a in intentos(root)[0]["avisos"])


def prueba_corte_versiones(tmp):
    import pyarrow.parquet as pq
    with servidor() as (base, e):
        row = next(r for r in e.datos["rows"] if r["symbol"] == "EURUSD" and dia(r) == "2026-11-11")
        # Ultima version dentro del corte; misma recepcion se ordena por batch_id.
        e.datos["rows"] += [{**row, "_recv_ts": "2026-11-12T23:59:59.999999999Z", "_batch_id": "z", "close": 1.5},
                           {**row, "_recv_ts": "2026-11-12T23:59:59.999999999Z", "_batch_id": "y", "close": 1.4},
                           {**row, "_recv_ts": "2026-11-13T00:00:00Z", "close": 99.0},
                           {**row, "_cycle": 8, "close": 88.0},
                           {**row, "_cycle": None, "close": 77.0},
                           {**row, "_offset": None, "close": 66.0}]
        def avanzar(ruta, q, doc):
            if "/objects/" in ruta:
                e.header = "8"
                doc["head_cycle"] = 8
            return doc
        e.transformar = avanzar
        root = tmp / "versiones"
        assert local(root, base)[0] == 0
        df = pq.read_table(root / "desktop/20261112/ohlcv/ohlcv_daily.parquet").to_pandas()
        row = df[(df.symbol == "FX.EURUSD") & (df.ts_ms == 1794355200000)].iloc[0]
        assert row.close == 1.5
        m = intentos(root)[0]
        assert m["cut_head_cycle"] == 7 and m["limpieza"]["corte_y_versiones"]["fuera_corte"] == 2
        assert m["limpieza"]["corte_y_versiones"]["provisionales"] == 2
        assert not any("fresh" in q for _, q in e.peticion)
        assert all(q["to"] == "2026-11-13T00:00:00Z" for p, q in e.peticion if "/objects/" in p)
    # La barra actual solo fuera de H no convierte el dia en publicable.
    with servidor() as (base, e):
        next(r for r in e.datos["rows"] if r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")["_cycle"] = 8
        root = tmp / "sin_barra_en_h"
        assert local(root, base)[0] == 3
        sin_productos(root)
    with servidor() as (base, e):
        # Se pide la ventana completa, pero una fuente que solo conserva D no es historia.
        e.datos["rows"] = [r for r in e.datos["rows"] if dia(r) == "2026-11-12"]
        root = tmp / "solo_d"
        assert local(root, base)[0] == 1
        sin_productos(root)


def prueba_cabeceras(tmp):
    for head in (None, "no-entero", "-1", "7.0"):
        with servidor() as (base, e):
            e.header = head
            root = tmp / str(head)
            assert local(root, base)[0] == 1
            sin_productos(root)
            assert not e.publicados
            assert "x-qn-head-cycle" in intentos(root)[0]["detail"]
    with servidor() as (base, e):
        e.transformar = lambda p, q, doc: {**doc, "head_cycle": 999} if "/objects/" in p else doc
        root = tmp / "discrepancia"
        assert local(root, base)[0] == 1
        sin_productos(root)
        comprobar_estado(root, e, "error")


def prueba_replicas(tmp):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        muerta = f"http://127.0.0.1:{s.getsockname()[1]}/qn"
    for caso in ("conexion", "503"):
        with servidor() as (base, e), servidor() as (caida, mala):
            mala.codigo = 503
            root = tmp / caso
            urls = (muerta if caso == "conexion" else caida) + "," + base
            assert local(root, urls)[0] == 0
            assert intentos(root)[0]["entradas"][0]["base"] == base
    for codigo in (401, 403, 404):
        with servidor() as (mala_url, mala), servidor() as (base, e):
            mala.codigo = codigo
            root = tmp / str(codigo)
            assert local(root, mala_url + "," + base)[0] == 1
            assert len(mala.peticion) == 1 and not e.peticion
            sin_productos(root)
    with servidor() as (base, e):
        e.codigo = 503
        # Sin H en ninguna respuesta, no hay estado.
        e.header = None
        root = tmp / "todas_caidas"
        assert local(root, base + "," + muerta)[0] == 1
        assert not e.publicados
        sin_productos(root)


def prueba_duplicados_volumen_invalidos(tmp):
    import pyarrow.parquet as pq
    for caso in ("igual", "empate", "alias", "volumen", "nan", "inf", "cero", "negativo", "rango", "volumen_negativo", "revision_invalida"):
        with servidor() as (base, e):
            root = tmp / caso
            row = next(r for r in e.datos["rows"] if r["symbol"] == "AAPL" and dia(r) == "2026-11-11")
            if caso == "igual":
                e.datos["rows"].append(dict(row))
            elif caso == "empate":
                e.datos["rows"].append({**row, "close": row["close"] + .1})
            elif caso == "alias":
                row = next(r for r in e.datos["rows"] if r["symbol"] == "^GSPC" and dia(r) == "2026-11-11")
                e.datos["rows"].append({**row, "symbol": "SPX", "close": row["close"] + .1})
            elif caso == "volumen":
                row["volume"] = None
            elif caso == "revision_invalida":
                e.datos["rows"].append({**row, "_recv_ts": "2026-11-12T23:30:00Z", "open": 0})
            else:
                key, value = {"nan": ("open", float("nan")), "inf": ("close", float("inf")),
                              "cero": ("open", 0), "negativo": ("low", -1), "rango": ("high", .1),
                              "volumen_negativo": ("volume", -1)}[caso]
                row[key] = value
            assert local(root, base)[0] == 0, caso
            df = pq.read_table(root / "desktop/20261112/ohlcv/ohlcv_daily.parquet").to_pandas()
            m = intentos(root)[0]["limpieza"]
            if caso == "igual":
                assert len(df) == 90 and m["corte_y_versiones"]["duplicados_iguales"] == 1
            elif caso in ("empate", "alias"):
                assert len(df) == 89 and len(m["cuarentena"]) == 1 and m["corte_y_versiones"]["cuarentena"] == 2
            elif caso == "volumen":
                assert len(df) == 90 and len(m["volumen_ausente"]) == 1
                assert df[(df.symbol == "EQ.SPOT.AAPL") & (df.ts_ms == 1794355200000)].iloc[0].volume == 0
            else:
                assert len(df) == 89 and sum(m["limpieza"]["excluidas"].values()) == 1


def prueba_determinismo_revision(tmp):
    from .nucleo import hashes
    with servidor() as (base, e):
        r1, r2 = tmp / "uno", tmp / "dos"
        assert local(r1, base)[0] == 0
        manifiestos = {p.name: p.read_bytes() for p in (r1 / "runs").glob("*.integridad.json")}
        assert local(r2, base, "--runs", str(r1 / "runs"))[0] == 0
        for carpeta in ("desktop", "datasets"):
            assert hashes(r1 / carpeta) == hashes(r2 / carpeta)
        assert manifiestos == {p.name: p.read_bytes() for p in (r1 / "runs").glob("*.integridad.json")}
        foto = foto_productos(r1)
        assert local(r1, base)[0] == 0 and foto_productos(r1) == foto
        assert e.publicados[0] == e.publicados[-1]
        row = next(r for r in e.datos["rows"] if r["symbol"] == "AAPL" and dia(r) == "2026-11-12")
        row["close"] += .1
        assert local(r1, base)[0] == 1 and foto_productos(r1) == foto
        comprobar_estado(r1, e, "error")
        assert local(r1, base, "--revision", "1")[0] == 0
        assert (r1 / "desktop/20261112/revision_1/ohlcv/index.json").is_file()
        assert all(foto_productos(r1)[k] == v for k, v in foto.items())
        posterior = foto_productos(r1)
        assert local(r1, base, "--revision", "1")[0] == 0 and foto_productos(r1) == posterior
        # Un fallo de previa tampoco toca una publicacion anterior.
        e.datos["rows"] = [r for r in e.datos["rows"] if not (r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")]
        assert local(r1, base)[0] == 3 and foto_productos(r1) == posterior


def prueba_fallos_atomicos(tmp):
    from quantdesk import daily
    from .nucleo import Cliente, bloqueo
    with servidor() as (base, e):
        root = tmp / "previo"
        assert local(root, base)[0] == 0
        foto = foto_productos(root)
        contexto = "previo"
        def solo_parquet(frame, folder, *_a, **_kw):
            frame.to_parquet(Path(folder) / "ohlcv_daily.parquet", compression="snappy", index=False)
            raise RuntimeError("fallo simulado entre Parquet e indice: " + contexto)
        with patch.object(daily, "write_ohlcv", solo_parquet):
            assert local(root, base)[0] == 1 and foto_productos(root) == foto
            nuevo = tmp / "nuevo"
            contexto = "nuevo"
            assert local(nuevo, base)[0] == 1
            sin_productos(nuevo)
        comprobar_estado(nuevo, e, "error")
        rename = Path.rename
        def fallar_motor(path, target):
            if Path(target).parent.name == "datasets":
                raise OSError("fallo simulado en segundo renombrado")
            return rename(path, target)
        with patch.object(Path, "rename", fallar_motor):
            nuevo = tmp / "rename"
            assert local(nuevo, base)[0] == 1
            sin_productos(nuevo)
        with patch.object(Cliente, "post", side_effect=RuntimeError("fallo de estado")):
            nuevo = tmp / "status"
            assert local(nuevo, base)[0] == 1
            sin_productos(nuevo)
        nuevo = tmp / "bloqueado"
        n_peticiones, n_estados = len(e.peticion), len(e.publicados)
        with bloqueo(nuevo / "runs/s20261112.lock"):
            # Windows impide leer el byte bloqueado incluso desde otro handle del mismo proceso.
            assert local(nuevo, base, verificar_secretos=False)[0] == 1
        secretos(nuevo)
        assert len(e.peticion) == n_peticiones and len(e.publicados) == n_estados
        assert intentos(nuevo)[0]["cut_head_cycle"] is None
        assert "bloqueo" in intentos(nuevo)[0]["detail"]
        sin_productos(nuevo)
        assert not any(p.name.startswith(".") for p in tmp.rglob("*") if p.is_dir())


def prueba_credencial_detail(tmp):
    from .nucleo import Lectura
    with servidor() as (base, e):
        root = tmp / "sin_token"
        root.mkdir(parents=True)
        (root / "privado.env").write_text("# sin credencial\nOTRA=valor\n", encoding="utf-8")
        assert local(root, base, entorno={"QN_URLS": base})[0] == 2
        assert not e.peticion and not e.publicados
        for argumentos in (("--sesion", "2026-99-01"), ("--desde", "2027-01-01"), ("--revision", "0")):
            assert local(root, base, *argumentos)[0] == 2
        root = tmp / "env_file"
        root.mkdir(parents=True)
        (root / "privado.env").write_text("QN_TOKEN='" + TOKEN_PRUEBA + "'\n", encoding="utf-8")
        assert local(root, base, entorno={"QN_URLS": base})[0] == 0
        # Entorno prioritario: un fichero privado incorrecto no se consulta.
        (root / "privado.env").write_text("QN_TOKEN=incorrecto\n", encoding="utf-8")
        assert local(root, base)[0] == 0
    get = Lectura.get
    def detalle_largo(self, ruta, params, registro):
        doc = get(self, ruta, params, registro)
        if "/objects/" in ruta:
            raise ValueError(TOKEN_PRUEBA + " qn_" + "ficticio " + "x" * 1000)
        return doc
    with servidor() as (base, e), patch.object(Lectura, "get", detalle_largo):
        root = tmp / "largo"
        assert local(root, base)[0] == 1
        comprobar_estado(root, e, "error")
        assert len(e.publicados[-1]["obj"]["detail"]) == 500
        sin_productos(root)
    for source in (TOKEN_PRUEBA, "qn_" + "ficticio"):
        with servidor() as (base, e):
            for row in e.datos["rows"]:
                if row["symbol"] == "AAPL":
                    row["source"] = source
            root = tmp / ("fuente_token" if source == TOKEN_PRUEBA else "fuente_patron")
            assert local(root, base)[0] == 1
            comprobar_estado(root, e, "error")
            sin_productos(root)


def correr():
    with tempfile.TemporaryDirectory(prefix="ti02-diario-") as tmp:
        root = Path(tmp)
        pruebas = (prueba_oraculo, prueba_sin_sesion, prueba_previa, prueba_festivos, prueba_corte_versiones,
                   prueba_cabeceras, prueba_replicas, prueba_duplicados_volumen_invalidos,
                   prueba_determinismo_revision, prueba_fallos_atomicos, prueba_credencial_detail)
        for prueba in pruebas:
            prueba(root / prueba.__name__)
            secretos(root / prueba.__name__)
            print(prueba.__name__ + ": OK", flush=True)
    print(f"exportar_diario --selftest: {len(pruebas)} grupos OK")


if __name__ == "__main__":
    correr()
