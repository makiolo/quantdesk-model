"""Solo tests nuevos; oraculos escritos a mano, fixture de forma real, sin red."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import date
from decimal import Decimal
from pathlib import Path
import tempfile
import random
from unittest.mock import patch
import uuid

from descarga_opciones import (Cliente, ESQUEMA, INICIO, QnFalso, TAGS, descargar, fila_fixture,
                               guardar_json, json_texto, sha256)
from . import lector as L


def preparado(**kwargs):
    r = fila_fixture(**kwargs)
    L.validar_fila(r)
    return r


def espera_error(fn, texto):
    try:
        fn()
    except (ValueError, FileExistsError) as e:
        assert texto in str(e), str(e)
    else:
        raise AssertionError("falta error " + texto)


def test_oraculo_call_put():
    """Oraculo independiente, CINCO strikes, resultado calculado aqui a mano.

    Call K=90,100,110,120,130; mids=12,11,6,7,2; hw=.005.
    120: 7-6=1>.01, monotonia. Sin 120, la cuerda 90..110
    vale (12+6)/2=9 en 100; 11-9=2>.01: convexidad.
    Quedan (90,12),(110,6),(130,2), pendientes -.3,-.2: convexa.

    Put mismos K; mids=2,9,8,10,14; hw=.005.
    110: 9-8=1>.01, monotonia. Sin 110, cuerda 90..120
    vale 2+(10-2)/3=14/3 en 100; 9-14/3=13/3>.01.
    Quedan (90,2),(120,10),(130,14), pendientes 8/30,.4: convexa.
    Las claves y motivos esperados son literales, no usan el filtro.
    """
    for tipo, mids, claves, bad in (
        ("call", [12, 11, 6, 7, 2], [90, 110, 130], {100: "convexidad", 120: "monotonia"}),
        ("put", [2, 9, 8, 10, 14], [90, 120, 130], {100: "convexidad", 110: "monotonia"}),
    ):
        rows = [preparado(strike=k, mid=m, opt_type=tipo) for k, m in zip([90, 100, 110, 120, 130], mids)]
        clean, ledger = L.limpiar(rows)
        assert sorted(r["strike"] for r, p in clean) == claves
        assert {int(e["instrument"].split("|")[-1]): e["motivo"] for e in ledger} == bad
        assert L.limpiar(list(reversed(rows))) == (clean, ledger)


def test_calendario_tolerancias_prioridad():
    a = preparado(strike=100, mid=8, maturity="2026-12-18")
    b = preparado(strike=100, mid=7, maturity="2027-01-15")
    clean, ledger = L.limpiar([a, b])
    assert len(clean) == 1 and ledger[0]["motivo"] == "calendario"
    # Comparacion exacta al tick admitida, y por encima excluida.
    for segundo, n in (("5.01", 2), ("5.0100001", 1)):
        rows = [preparado(strike=90, bid="5", ask="5"), preparado(strike=100, bid=segundo, ask=segundo)]
        assert len(L.limpiar(rows)[0]) == n
    # Semianchura en ambos extremos; 0.9 < 1.0 no es violacion.
    rows = [preparado(strike=90, bid=4, ask=6), preparado(strike=100, bid=5.9, ask=5.9)]
    assert len(L.limpiar(rows)[0]) == 2
    # Strikes desiguales: cuerda a K=100 entre K90(10) y K130(2) = 8.
    rows = [preparado(strike=k, bid=m, ask=m) for k, m in ((90, 10), (100, 9), (130, 2))]
    assert L.limpiar(rows)[1][0]["motivo"] == "convexidad"
    # Sin cotizacion prevalece sobre cualquier infraccion de precios.
    rows = [a, preparado(strike=110, bid=99, ask=0), b]
    assert Counter(e["motivo"] for e in L.limpiar(rows)[1]) == {"sin_cotizacion": 1, "calendario": 1}
    # Una retirada de calendario revela monotonia que antes admitia la
    # horquilla ancha intermedia: el punto fijo garantiza todas las reglas.
    rows = [preparado(strike=90, bid=5, ask=5), preparado(strike=100, bid=4, ask=6),
            preparado(strike=110, bid=5.5, ask=5.5),
            preparado(strike=100, mid=8, maturity="2026-12-18")]
    clean, ledger = L.limpiar(rows)
    assert any(e["motivo"] == "calendario" for e in ledger)
    assert any(e["motivo"] == "monotonia" and e["instrument"].endswith("|110") for e in ledger)
    assert L.limpiar([r for r, p in clean])[1] == []
    # Monotonia gana frente a convexidad cuando la misma fila viola ambas.
    rows = [preparado(strike=k, mid=m) for k, m in ((90, 10), (100, 11), (110, 1))]
    assert L.limpiar(rows)[1][0]["motivo"] == "monotonia"


def test_punto_fijo_oraculo_independiente():
    rng = random.Random(0)
    rows = [preparado(strike=k, opt_type=tipo, maturity=mat, bid=bid, ask=bid + ancho)
            for tipo in ("call", "put") for mat in ("2026-12-18", "2027-01-15", "2027-02-19")
            for k in range(70, 151, 5) for bid, ancho in [(rng.randrange(0, 200) / 10, rng.randrange(0, 30) / 10)]]
    clean, ledger = L.limpiar(rows)
    rng.shuffle(rows)
    assert L.limpiar(rows) == (clean, ledger)
    # Verificacion numerica independiente sobre TODAS las parejas y ternas
    # consecutivas de la salida, sin llamar a comparadores del lector.
    precios = [{"strike": Decimal(str(p["strike"])), "mid": (Decimal(str(p["bid"])) + Decimal(str(p["ask"]))) / 2,
                "hw": (Decimal(str(p["ask"])) - Decimal(str(p["bid"]))) / 2, "mat": p["maturity"], "tipo": p["opt_type"]}
               for r, p in clean]
    for tipo in ("call", "put"):
        for mat in ("2026-12-18", "2027-01-15", "2027-02-19"):
            chain = sorted((p for p in precios if p["tipo"] == tipo and p["mat"] == mat), key=lambda p: p["strike"])
            for a, b in zip(chain, chain[1:]):
                tol = max(Decimal(".01"), a["hw"], b["hw"])
                assert (b["mid"] - a["mid"] if tipo == "call" else a["mid"] - b["mid"]) <= tol
            for a, b, c in zip(chain, chain[1:], chain[2:]):
                chord = ((c["strike"] - b["strike"]) * a["mid"] + (b["strike"] - a["strike"]) * c["mid"]) / (c["strike"] - a["strike"])
                assert b["mid"] - chord <= max(Decimal(".01"), a["hw"], b["hw"], c["hw"])
        for k in range(70, 151, 5):
            chain = sorted((p for p in precios if p["tipo"] == tipo and p["strike"] == k), key=lambda p: p["mat"])
            for a, b in zip(chain, chain[1:]):
                assert a["mid"] - b["mid"] <= max(Decimal(".01"), a["hw"], b["hw"])


def universo100():
    return sorted(L.OBLIGATORIOS) + sorted({("AAPL", "EQUITY"), ("NVR", "EQUITY")} |
                                          {(f"EQ{i:03d}", "EQUITY") for i in range(91)})


def captura(sesion, combo, sufijo="163125-5b2305", ns=None):
    rows = [fila_fixture(symbol=s, asset_type=t, sesion=sesion, captura=sesion + "-" + sufijo,
                         underlying_price=18.700000762939453 if s == "^VIX" else 757.1199951171875) for s, t in combo]
    if ns is not None:
        for r in rows:
            r.update(captured_at=ns, _ts=ns, _recv_ts=ns + 1234567)
    return rows


def fixture_realista():
    u = universo100()
    assert len(u) == 100
    base = captura("2026-11-12", u)
    parcial = captura("2026-11-13", u[:80], "163125-aaaaaa")
    # 19 NY = 00 UTC del dia siguiente, con fraccion ns para probar ceil.
    ns = L.ns_corte("2026-11-14T00:00:00.000000001Z")
    reintento = captura("2026-11-13", [x for x in u if x[0] != "NVR"], "190000-bbbbbb", ns)
    noventa = captura("2026-11-16", u[:90], "163125-cccccc")
    extras = [fila_fixture(strike=110, ask=0), fila_fixture(strike=120, bid=6, ask=5),
              fila_fixture(strike=130, bid=0, ask=.02, implied_vol=0, last_price=0),
              fila_fixture(strike=140, maturity="2026-11-10"),
              fila_fixture(strike=150, bid=0, ask=.02, implied_vol=0, last_price=0)]
    duplicado = deepcopy(next(r for r in base if r["symbol"] == "SPY"))
    viejas = [fila_fixture(symbol=s, asset_type="EQUITY", opt_type="CALL", capture_id=None) for s in ("SPY", "QQQ")]
    pilotos = [fila_fixture(sesion="2026-11-11", captura="2026-11-11-140051-62d271"),
               fila_fixture(sesion="2026-11-11", captura="2026-11-11-220233-1a3bd8")]
    return base + parcial + reintento + noventa + extras + [duplicado] + viejas + pilotos


def test_capturas_universo_huecos():
    rows = fixture_realista()
    cal, sessions = L.calendario_validado(L.CALENDARIO, INICIO, date(2026, 11, 27))
    raw, rep = L.seleccionar(rows, INICIO, date(2026, 11, 27), L.ns_corte("2026-11-28"), INICIO, sessions)
    assert len(raw) == 204, len(raw)  # 100+5 extras+99, exacto repetido eliminado
    dec = {d["sesion"]: d for d in rep["capturas"]}
    assert dec["2026-11-13"]["capture_id"] == "2026-11-13-190000-bbbbbb"
    assert [(c["subyacentes"], c["valida"]) for c in dec["2026-11-13"]["candidatas"]] == [(80, False), (99, True)]
    assert dec["2026-11-16"]["capture_id"] is None
    assert "2026-11-17" in rep["sesiones_sin_captura_valida"]
    assert "2026-11-26" not in dec
    for h in rep["huecos_por_subyacente"]:
        assert "2026-11-17" in h["sesiones_sin_datos"]
        assert "2026-11-26" not in h["sesiones_sin_datos"]
        assert "2026-11-27" in h["sesiones_sin_datos"]  # media sesion habil
    assert len(rep["huecos_por_subyacente"]) == 100
    counts = rep["descartes_lector"]
    assert counts["sin_capture_id"] == 2 and counts["anterior_oc03"] == 2
    assert counts["duplicado_exacto"] == 1 and counts["sin_captura_valida"] == 90
    assert counts["captura_no_elegida"] == 80
    assert all(r["date"] >= "2026-11-12" and r["capture_id"] for r in raw)
    return raw, rep


def test_empates_95_y_cinco_previas():
    u = universo100()
    cal, ses = L.calendario_validado(L.CALENDARIO, INICIO, date(2026, 11, 27))
    cut = L.ns_corte("2026-11-28")
    baseline = captura("2026-11-12", u)
    # Dos completas: mas subyacentes gana aunque sea la anterior.
    rows = baseline + captura("2026-11-13", u, "163125-aaaaaa") + captura(
        "2026-11-13", u[:99], "190000-bbbbbb", L.ns_corte("2026-11-14T00:00:00Z"))
    assert L.seleccionar(rows, INICIO, date(2026, 11, 13), cut, INICIO, ses)[1]["capturas"][-1]["capture_id"].endswith("aaaaaa")
    rows += captura("2026-11-13", u, "190000-cccccc", L.ns_corte("2026-11-14T00:00:00Z"))
    assert L.seleccionar(rows, INICIO, date(2026, 11, 13), cut, INICIO, ses)[1]["capturas"][-1]["capture_id"].endswith("cccccc")
    rows += captura("2026-11-13", u, "190000-dddddd", L.ns_corte("2026-11-14T00:00:00Z"))
    assert L.seleccionar(rows, INICIO, date(2026, 11, 13), cut, INICIO, ses)[1]["capturas"][-1]["capture_id"].endswith("dddddd")
    for n, valida in ((95, True), (94, False), (90, False)):
        rep = L.seleccionar(baseline + captura("2026-11-13", u[:n]), INICIO, date(2026, 11, 13), cut, INICIO, ses)[1]
        assert (rep["capturas"][-1]["capture_id"] is not None) == valida
    # Sesiones con datos no necesariamente validas; sin usar sesiones futuras.
    rows = baseline[:]
    for d in ("2026-11-13", "2026-11-16", "2026-11-18", "2026-11-20", "2026-11-23", "2026-11-24"):
        rows += captura(d, u[:90])
    rep = L.seleccionar(rows, INICIO, date(2026, 11, 24), cut, INICIO, ses)[1]
    ultimo = rep["capturas"][-1]
    assert ultimo["sesiones_contexto"] == ["2026-11-13", "2026-11-16", "2026-11-18", "2026-11-20", "2026-11-23"]
    assert ultimo["capture_id"] is not None  # d12 ya salio de la ventana
    # Subyacentes que solo aparecen manana no cambian el denominador de hoy.
    hoy = L.seleccionar(captura("2026-11-12", u[:90]) + captura("2026-11-13", u), INICIO, date(2026, 11, 13), cut, INICIO, ses)[1]
    assert hoy["capturas"][0]["candidatas"][0]["valida"]


def test_ceros_vix_expirado_duplicados():
    raw, rep = test_capturas_universo_huecos()
    clean, ledger = L.limpiar(raw)
    assert len(clean) == 201, (len(clean), ledger)
    assert Counter(e["motivo"] for e in ledger) == {"sin_cotizacion": 2, "vencimiento_pasado": 1}
    ceros = [p for r, p in clean if r["symbol"] == "SPY" and r["strike"] in (130, 150)]
    assert len(ceros) == 2 and all(p["bid"] == 0 and p["mid"] == .01 and p["implied_vol"] is None and p["last_price"] is None for p in ceros)
    assert all(r["volume"] == 0 for r in raw)
    assert all(r["underlying_price"] == 18.700000762939453 for r in raw if r["symbol"] == "^VIX")
    assert {L.identidad(r) for r, p in clean} < {L.identidad(r) for r in raw}
    assert {L.identidad(r) for r, p in clean}.isdisjoint({(e["sesion"], e["instrument"]) for e in ledger})
    assert len(ledger) == len({(e["sesion"], e["instrument"]) for e in ledger})
    cal, ses = L.calendario_validado(L.CALENDARIO, INICIO, INICIO)
    rows = captura("2026-11-12", universo100())
    d = deepcopy(rows[0]); d["bid"] = 99
    espera_error(lambda: L.seleccionar(rows + [d], INICIO, INICIO, L.ns_corte("2026-11-14"), INICIO, ses), "duplicado con distinto contenido")
    espera_error(lambda: L.validar_fila({**rows[0], "underlying_price": None}), "numero ausente")


def test_corte_ns_calendario():
    assert L.ns_corte("2026-11-14T00:00:00.000000001Z") == L.ns_corte("2026-11-14") + 1
    ns = L.ns_corte("2026-11-14T00:00:00.000000001Z")
    row = captura("2026-11-13", sorted(L.OBLIGATORIOS), "190000-bbbbbb", ns)
    cal, ses = L.calendario_validado(L.CALENDARIO, INICIO, date(2026, 11, 13))
    # El ceil exige el primer ms disponible entero, no redondear hacia abajo.
    assert not L.seleccionar(row, date(2026, 11, 13), date(2026, 11, 13), ns, INICIO, ses)[0]
    assert len(L.seleccionar(row, date(2026, 11, 13), date(2026, 11, 13), ns + 999999, INICIO, ses)[0]) == 7
    espera_error(lambda: L.calendario_validado(L.CALENDARIO, INICIO, date(2027, 3, 1)), "no cubre")
    for festivo in L.CALENDARIO["holidays"]:
        assert date.fromisoformat(festivo) not in ses
    assert date(2026, 12, 24) in ses and date(2026, 11, 27) in ses


def test_dataset_doble_offline(base):
    import archivo_opciones as A
    import pyarrow.parquet as pq
    qn = QnFalso(fixture_realista())
    cli = Cliente("http://fixture.invalid/qn", qn.token, abrir=qn.abrir, espera=0)
    dump = base / "volcado"
    m = descargar(cli, INICIO, date(2026, 11, 27), dump)
    assert m["descartadas"]["sin_capture_id"] == 2
    qn2 = QnFalso(list(reversed(fixture_realista())))
    dump2 = base / "volcado_reordenado"
    m2 = descargar(Cliente("http://fixture.invalid/qn", qn2.token, abrir=qn2.abrir, espera=0),
                   INICIO, date(2026, 11, 27), dump2)
    assert m == m2 and sha256(dump / "manifest.json") == sha256(dump2 / "manifest.json")
    nombre = "fixture_ti09_" + uuid.uuid4().hex[:12]
    # Dos llamadas identicas salvo la raiz fisica: tambien bytes identicos.
    d1, r1 = A.archivar(dump, "2026-11-28T06:00:00Z", nombre, raiz=base / "a")
    d2, r2 = A.archivar(dump, "2026-11-28T06:00:00Z", nombre, raiz=base / "b")
    assert r1 == r2 and r1["dataset_sha256"] == r2["dataset_sha256"]
    assert {p.name: sha256(p) for p in d1.iterdir()} == {p.name: sha256(p) for p in d2.iterdir()}
    assert r1["filas_cruda"] == 204 and r1["filas_limpia"] == 201
    _, vacio = A.archivar(dump, "2026-11-28T06:00:00Z", nombre + "_vacio", desde="2026-11-16", hasta="2026-11-16", raiz=base / "vacios")
    assert vacio["filas_cruda"] == vacio["filas_limpia"] == 0
    assert vacio["sesiones_sin_captura_valida"] == ["2026-11-16"]
    assert all(h["sesiones_sin_datos"] == ["2026-11-16"] for h in vacio["huecos_por_subyacente"])
    for t in ("opciones_cruda", "opciones_limpia"):
        df = pq.read_table(d1 / (t + ".parquet")).to_pandas()
        assert df["available_at_ms"].notna().all() and df["revision"].eq(0).all()
        caps = {}
        for payload in df["data_json"]:
            p = L.cargar_json(payload)
            caps.setdefault(p["date"], set()).add(p["capture_id"])
            assert p["capture_id"] and p["date"] >= "2026-11-12"
        assert all(len(c) == 1 for c in caps.values())
        assert df.loc[df["ts_ms"] == (date(2026, 11, 13) - date(1970, 1, 1)).days * L.MS_DIA, "available_at_ms"].eq(
            L.ns_corte("2026-11-14") // 1000000 + 1).all()
    espera_error(lambda: A.archivar(dump, "2026-11-28", nombre, raiz=base / "a"), "ya existe")
    # Nuevo dataset fixture autorizado; conservar evidencia legible para la raiz.
    final, r = A.archivar(dump, "2026-11-28T06:00:00Z", nombre)
    assert r["dataset_sha256"] == r1["dataset_sha256"]
    md = (final / "informe.md").read_text(encoding="utf-8")
    assert "^VIX" in md and "semilla" in md and "convexidad" in md and "2026-11-26" in md
    assert r["validacion"]["ok"] and r["validacion"]["politica"]["ok"]
    # Integridad y completitud: fallar antes de generar dataset.
    archivo = dump / m["ficheros"][0]["ruta"]
    original = archivo.read_bytes()
    archivo.write_bytes(original + b"\n")
    espera_error(lambda: L.cargar_volcado(dump), "SHA-256")
    archivo.write_bytes(original)
    m["completo"] = False
    guardar_json(dump / "manifest.json", m)
    espera_error(lambda: L.cargar_volcado(dump), "incompleto")
    m["completo"] = True
    m["contexto_completo"] = False
    guardar_json(dump / "manifest.json", m)
    espera_error(lambda: L.cargar_volcado(dump), "sin contexto")
    m["contexto_completo"] = True
    guardar_json(dump / "manifest.json", m)
    evidencia = {"dataset": str(final), "dataset_sha256": r["dataset_sha256"],
                 "informe_md_sha256": sha256(final / "informe.md"), "doble_ejecucion": "hash y bytes identicos",
                 "fixtures": {"cruda": 204, "limpia": 201, "sin_cotizacion": 2, "vencimiento_pasado": 1},
                 "volcado": str(dump), "tests": [f.__name__ for f in TESTS] + ["test_dataset_doble_offline"]}
    guardar_json(base / "evidencia.json", evidencia)
    print("evidencia " + str(base / "evidencia.json"))
    print("dataset SHA-256 " + r["dataset_sha256"])


TESTS = (test_oraculo_call_put, test_calendario_tolerancias_prioridad, test_punto_fijo_oraculo_independiente, test_capturas_universo_huecos,
         test_empates_95_y_cinco_previas, test_ceros_vix_expirado_duplicados, test_corte_ns_calendario)


def selftest():
    from archivo_opciones import TMP
    TMP.mkdir(parents=True, exist_ok=True)
    # Se conserva el fixture, hashes e informe: todos bajo E:/quantdesk-lab.
    base = Path(tempfile.mkdtemp(prefix="selftest_", dir=TMP))
    with patch("socket.socket", side_effect=AssertionError("red prohibida")):
        for test in TESTS:
            test()
        test_dataset_doble_offline(base)
    print("selftest ok")
