"""Regresiones de la revision de 237220f; red local y productos temporales."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from .qn_falso import servidor
from .selftests import check, dia, foto_productos, intentos, local, secretos, sin_productos


def registro(root):
    paths = list((root / "runs").glob("s20261112_r0_*.publicacion.json"))
    assert len(paths) == 1, "debe existir un registro persistente de publicacion"
    return json.loads(paths[0].read_text(encoding="utf-8"))


def mismo_sobre(e):
    sobres = e.peticiones_publicacion
    assert sobres and all(s == sobres[0] for s in sobres), "el reintento debe conservar objeto, ts y batch_id"


def prueba_republicacion_d(root):
    with servidor() as (base, e):
        row = next(r for r in e.datos["rows"] if r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")
        e.datos["rows"].append({**row, "_recv_ts": "2026-11-13T00:01:00Z", "close": 99.0})
        code, _ = local(root, base)
        assert code == 0, f"D tiene una version valida dentro del corte: salida={code}"
        check(root)
        assert any("/objects/" in ruta for ruta, _ in e.peticion)


def prueba_latest_dia_siguiente(root):
    with servidor() as (base, e):
        row = next(r for r in e.datos["rows"] if r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")
        e.datos["rows"].append({**row, "_ts": "2026-11-13T00:00:00Z", "_recv_ts": "2026-11-13T23:00:00Z"})
        code, _ = local(root, base)
        assert code == 0, f"latest D+1 no invalida la sesion historica D: salida={code}"
        check(root)


def prueba_estado_no_durable(root):
    with servidor() as (base, e):
        e.publicacion_defecto = "no_durable"
        code, _ = local(root, base)
        assert code == 1, f"HTTP 202 sin confirmacion durable debe fallar: salida={code}"
        assert 2 <= len(e.peticiones_publicacion) <= 12
        mismo_sobre(e)
        assert e.respuestas_publicacion[-1] == {"durable": False, "duplicate": True}
        assert registro(root)["estado"] == "incierta"
        errores = [m for m in intentos(root) if m["status"] == "error"]
        assert errores and errores[-1]["publicacion"]["estado"] == "incierta"
        assert "durable" in (root / "runs/s20261112.log").read_text(encoding="utf-8")
        check(root)  # qn ya acepto el ok, aunque siga pendiente su durabilidad.


def prueba_estado_durable_tras_pendiente(root):
    with servidor() as (base, e):
        e.acciones_publicacion = ["no_durable", "durable"]
        assert local(root, base)[0] == 0
        assert len(e.peticiones_publicacion) == 2, "durable=false exige otro intento"
        mismo_sobre(e)
        assert e.respuestas_publicacion == [{"durable": False, "duplicate": False},
                                            {"durable": True, "duplicate": True}]
        assert registro(root)["estado"] == "confirmada"
        check(root)


def prueba_respuesta_perdida_reconciliada(root):
    from descarga_lago import REINTENTOS
    with servidor() as (base, e):
        e.acciones_publicacion = ["perder"] * (REINTENTOS + 1) + ["durable"]
        code, _ = local(root, base)
        assert code == 0, f"el duplicado durable debe reconciliar el ok aceptado: salida={code}"
        mismo_sobre(e)
        assert e.respuestas_publicacion[-1] == {"durable": True, "duplicate": True}
        r = registro(root)
        assert r["estado"] == "confirmada" and any(ev["estado"] == "incierta" for ev in r["eventos"])
        check(root)


def prueba_respuesta_perdida_y_reejecucion(root):
    with servidor() as (base, e):
        e.publicacion_defecto = "perder"
        assert local(root, base)[0] == 1
        assert foto_productos(root), "un ok aceptado con respuesta perdida no permite borrar los productos"
        check(root)
        assert 2 <= len(e.peticiones_publicacion) <= 12
        mismo_sobre(e)
        assert registro(root)["estado"] == "incierta"
        assert any(m["status"] == "error" and m["publicacion"]["estado"] == "incierta" for m in intentos(root))
        foto = foto_productos(root)
        sobre = copy.deepcopy(e.publicados[0])
        n_lecturas = len(e.peticion)
        e.publicacion_defecto = "durable"
        # El nuevo head y la ausencia actual no deben cambiar el sobre pendiente.
        e.header = "8"
        e.datos["head_cycle"] = 8
        e.datos["rows"] = []
        assert local(root, base)[0] == 0
        assert len(e.peticion) == n_lecturas, "la reejecucion reconcilia antes de releer mercado"
        assert e.publicados[-1] == sobre
        assert e.respuestas_publicacion[-1] == {"durable": True, "duplicate": True}
        assert registro(root)["estado"] == "confirmada"
        assert foto_productos(root) == foto
        check(root)


def prueba_rechazo_tras_respuesta_perdida(root):
    from descarga_lago import REINTENTOS
    for aceptado in (False, True):
        with servidor() as (base, e):
            folder = root / str(aceptado)
            e.acciones_publicacion = (["perder"] * (REINTENTOS + 1)) if aceptado else []
            e.publicacion_defecto = "rechazar"
            assert local(folder, base)[0] == 1
            mismo_sobre(e)
            if aceptado:
                check(folder)
                assert registro(folder)["estado"] == "incierta"
                foto = foto_productos(folder)
                e.publicacion_defecto = "durable"
                assert local(folder, base)[0] == 0
                assert foto_productos(folder) == foto
                assert e.respuestas_publicacion[-1] == {"durable": True, "duplicate": True}
            else:
                sin_productos(folder)
                assert not e.publicados and registro(folder)["estado"] == "no_enviada"


def prueba_reconciliar_estados_sin_productos(root):
    rename = Path.rename

    def fallar_motor(path, target):
        if Path(target).parent.name == "datasets":
            raise OSError("fallo simulado al publicar motor")
        return rename(path, target)

    for status, codigo in (("sin_mt5", 3), ("error", 1)):
        with servidor() as (base, e):
            folder = root / status
            if status == "sin_mt5":
                e.datos["rows"] = [r for r in e.datos["rows"] if not (r["symbol"] == "EURUSD" and dia(r) == "2026-11-12")]
            e.publicacion_defecto = "no_durable"
            with patch.object(Path, "rename", fallar_motor):
                assert local(folder, base)[0] == 1
            sin_productos(folder)
            assert e.publicados[0]["obj"]["status"] == status
            sobre = copy.deepcopy(e.publicados[0])
            n_lecturas = len(e.peticion)
            e.publicacion_defecto = "durable"
            assert local(folder, base)[0] == codigo
            assert e.publicados[-1] == sobre and len(e.peticion) == n_lecturas
            assert registro(folder)["estado"] == "confirmada"
            assert e.respuestas_publicacion[-1] == {"durable": True, "duplicate": True}
            mismo_sobre(e)
            sin_productos(folder)


PRUEBAS = (prueba_republicacion_d, prueba_latest_dia_siguiente, prueba_estado_no_durable,
           prueba_estado_durable_tras_pendiente, prueba_respuesta_perdida_reconciliada,
           prueba_respuesta_perdida_y_reejecucion, prueba_rechazo_tras_respuesta_perdida,
           prueba_reconciliar_estados_sin_productos)


def correr():
    fallos = []
    with tempfile.TemporaryDirectory(prefix="ti02-regresiones-r2-") as tmp:
        for prueba in PRUEBAS:
            root = Path(tmp) / prueba.__name__
            try:
                prueba(root)
                secretos(root)
                print(prueba.__name__ + ": OK", flush=True)
            except Exception as e:
                fallos.append(prueba.__name__)
                print(prueba.__name__ + ": FALLO: " + str(e), flush=True)
    assert not fallos, "regresiones R2 fallidas: " + ", ".join(fallos)
    print(f"regresiones R2: {len(PRUEBAS)} OK", flush=True)


if __name__ == "__main__":
    correr()
