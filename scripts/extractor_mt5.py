"""Extractor MetaTrader 5 de SOLO LECTURA (TI-12-MT5): inventario y descarga cruda reanudable de velas y ticks.

    .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --inventario [--grupo PATRON] [--simbolos A,B] [--sin-profundidad]
    .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --descargar --simbolos @fx28 --periodos d1,h1,m5,m1 \
        --desde AAAA-MM-DD --hasta AAAA-MM-DD [--salida DIR] [--refrescar]
    .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --comparar DIR_A DIR_B
    .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --universos INVENTARIO.json   (sin terminal)
    .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --sp500 WIKITEXT.json          (sin terminal)
    .venv/Scripts/python -X utf8 scripts/extractor_mt5.py --selftest

Garantias:
- Solo lectura: el paquete `MetaTrader5` se usa solo a traves de `extractor_mt5_lib.lectura.TerminalSoloLectura`, que expone
  una lista blanca de consultas (y `login`) y lanza `FuncionNoPermitida` con cualquier otro nombre. Nunca envia ordenes.
- Credenciales: si existe el fichero de credenciales (E:/quantdesk-lab/secrets/mt5.json o la ruta de QDL_MT5_SECRETS) se usa
  `initialize(path)` + `login(...)`; con `--sin-credenciales`, o sin fichero, se engancha a un terminal ya abierto y
  autenticado por el usuario. Ningun valor de las credenciales se imprime, se registra ni se guarda: toda salida pasa por
  una guarda que la rechaza si contiene alguno. La procedencia lleva el tipo de cuenta y hashes con sal (cuenta, servidor).
- Hora: las marcas del servidor se convierten a UTC con `--regla` (por defecto `ny+7`); ver extractor_mt5_lib/hora.py.

Simbolos: nombres exactos del terminal o bases normalizadas (`EURUSD` encuentra `EURUSD.a` si es el unico); `@fx28` son
los 28 cruces FX del lago; `@fx60`, `@metales_energia`, `@indices`, `@crypto`, `@crypto_alts`, `@continuo` y `@us_grandes`
son los universos con nombre de extractor_mt5_lib/universos/universos.json (fase C). Periodos: d1, h1, m5, m1, ticks. Rango: `--desde` incluido, `--hasta` excluido (UTC, <= hoy).
Almacen (fuera de Git): E:/quantdesk-lab/data/mt5/<hasta>/ (parquet + manifest.json), cache de trozos en
E:/quantdesk-lab/data/mt5/_trozos/, inventarios en E:/quantdesk-lab/data/mt5/inventario/ y registro de cada ejecucion en
E:/quantdesk-lab/runs/TI-12-MT5/. Salida 0 ok; 1 datos inconsistentes, descarga interrumpida (reanudable) o hashes
distintos; 2 uso incorrecto o terminal no disponible; 3 PARADA por espacio en disco.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_env import LAB, LAB_ENV  # noqa: E402

os.environ.update(LAB_ENV)

from extractor_mt5_lib import descarga as D  # noqa: E402
from extractor_mt5_lib import hora as HR  # noqa: E402
from extractor_mt5_lib import inventario as INV  # noqa: E402
from extractor_mt5_lib import lectura as LT  # noqa: E402
from extractor_mt5_lib import simbolos as SB  # noqa: E402
from extractor_mt5_lib import universos as UNI  # noqa: E402

DATA = LAB + "/data/mt5"
RUNS = LAB + "/runs/TI-12-MT5"
SUELO_C = 2 * 1024 ** 3
SUELO_E = 150 * 1024 ** 3  # E: es compartido: el laboratorio no baja de 150 GiB libres


class ParadaDisco(RuntimeError):
    pass


def guarda_disco() -> None:
    for unidad, suelo in (("C:/", SUELO_C), ("E:/", SUELO_E)):
        if os.path.exists(unidad):
            libre = shutil.disk_usage(unidad).free
            if libre < suelo:
                raise ParadaDisco(f"{unidad} tiene {libre / 1024 ** 3:.1f} GiB libres (< {suelo / 1024 ** 3:.0f} GiB)")


procedencia = LT.procedencia


def _fecha(txt: str) -> dt.date:
    return dt.date.fromisoformat(txt)


def argumentos(argv) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extractor MetaTrader 5 de solo lectura (TI-12-MT5)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--inventario", action="store_true")
    g.add_argument("--descargar", action="store_true")
    g.add_argument("--comparar", nargs=2, metavar="DIR")
    g.add_argument("--universos", metavar="INVENTARIO_JSON",
                   help="resuelve los universos con nombre contra un inventario y escribe el fichero de universos")
    g.add_argument("--sp500", metavar="WIKITEXT_JSON",
                   help="rehace universos/sp500.csv desde la respuesta JSON de la API de la Wikipedia (action=parse)")
    p.add_argument("--grupo")
    p.add_argument("--simbolos")
    p.add_argument("--sin-profundidad", action="store_true")
    p.add_argument("--dias-ticks", type=int, default=3)
    p.add_argument("--periodos", default="d1,h1,m5,m1")
    p.add_argument("--desde", type=_fecha)
    p.add_argument("--hasta", type=_fecha)
    p.add_argument("--salida")
    p.add_argument("--refrescar", action="store_true")
    p.add_argument("--regla", default=HR.REGLA_DEFECTO)
    p.add_argument("--sin-credenciales", action="store_true")
    return p.parse_args(argv)


def lista_simbolos(txt: str | None, universos: dict | None = None) -> list[str] | None:
    """Nombres pedidos. `@fx28`: los 28 cruces del lago (fijos). `@<universo>`: un grupo del fichero de universos
    (scripts/extractor_mt5_lib/universos/universos.json, ver fase-c.md). Un universo desconocido es ValueError."""
    if not txt:
        return None
    out = []
    for x in (s.strip() for s in txt.split(",")):
        if x == "@fx28":
            out.extend(INV.FX28)
        elif x.startswith("@"):
            out.extend(UNI.grupo(x[1:], universos if universos is not None else UNI.cargar()))
        elif x:
            out.append(x)
    return out


def cargar_credenciales_defecto(a):
    if a.sin_credenciales:
        return None
    ruta = LT.ruta_secretos()
    return LT.leer_credenciales(ruta) if os.path.isfile(ruta) else None


def generar_universos(a, sp500_csv: str = UNI.RUTA_SP500) -> int:
    """`--universos INVENTARIO`: no toca el terminal; lee un inventario y la instantanea del S&P 500."""
    with open(a.universos, encoding="utf-8") as f:
        inv = json.load(f)
    sp500, cabecera = UNI.leer_sp500(sp500_csv)
    doc = UNI.resolver(inv, sp500, cabecera, os.path.basename(a.universos))
    destino = a.salida or UNI.RUTA_UNIVERSOS
    UNI.guardar(doc, destino)
    print("universos: " + ", ".join(f"@{g} {n}" for g, n in doc["cuentas"].items()) + f" -> {destino}")
    print(f"  S&P 500: {doc['sp500']['casados']} casados, {doc['sp500']['sin_casar']} sin casar: "
          + ", ".join(f"{x['ticker']} ({x['motivo']})" for x in doc["us_grandes"]["sin_casar"]))
    print(f"  fuera: {len(doc['excluidos']['vencimiento'])} con vencimiento, {doc['excluidos']['bonos']} bonos, "
          f"{doc['excluidos']['stohastic']} Stohastic")
    return 0


def ejecutar(argv, fabrica=LT.importar_paquete, cargar_cred=cargar_credenciales_defecto, reloj=time.time,
             en_ejecucion=LT.terminal_en_ejecucion, data: str = DATA, runs: str = RUNS, guarda=guarda_disco,
             universos: dict | None = None) -> int:
    a = argumentos(argv)
    if a.universos:
        return generar_universos(a)
    if a.sp500:
        with open(a.sp500, encoding="utf-8") as f:
            w = json.load(f)["parse"]
        filas = UNI.sp500_desde_wikitext(w["wikitext"])
        fuente = f"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies (revid {w.get('revid')})"
        hoy = dt.datetime.fromtimestamp(reloj(), tz=dt.timezone.utc).date().isoformat()
        UNI.escribir_sp500(filas, fuente, hoy, a.salida or UNI.RUTA_SP500)
        print(f"sp500: {len(filas)} componentes -> {a.salida or UNI.RUTA_SP500}")
        return 0
    if a.comparar:
        difs = D.comparar(*a.comparar)
        for d in difs:
            print("DIFERENCIA " + d)
        print("comparar: " + ("identicas (mismo hash_conjunto y mismos bytes)" if not difs else f"{len(difs)} diferencias"))
        return 0 if not difs else 1
    try:
        regla = HR.regla_desde_texto(a.regla)
        periodos = [x.strip() for x in a.periodos.split(",") if x.strip()]
        if a.descargar:
            if not a.simbolos or not a.desde or not a.hasta:
                raise ValueError("--descargar necesita --simbolos, --desde y --hasta")
            hoy = dt.datetime.fromtimestamp(reloj(), tz=dt.timezone.utc).date()
            if not a.desde < a.hasta <= hoy:
                raise ValueError(f"rango invalido: hace falta desde < hasta <= hoy UTC ({hoy})")
            if not periodos or any(x not in D.PERIODOS for x in periodos) or len(set(periodos)) != len(periodos):
                raise ValueError(f"--periodos: usa sin repetir {list(D.PERIODOS)}")
        cred = cargar_cred(a)
    except (ValueError, LT.TerminalNoDisponible) as e:
        print(f"BLOQUEADO: {e}")
        return 2

    def decir(txt: str) -> None:
        print(LT.comprobar_sin_secretos(txt, cred), flush=True)

    def escribir_json(ruta: str, doc: dict) -> None:
        texto = LT.comprobar_sin_secretos(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=1) + "\n", cred)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        os.replace(ruta + ".tmp", ruta)

    t0 = reloj()
    sello = dt.datetime.fromtimestamp(t0, tz=dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    registro = {"tarea": "TI-12-MT5", "argv": list(argv), "inicio_utc": HR.iso(int(t0 * 1000)),
                "modo_enganche": "credenciales" if cred is not None else "terminal abierto por el usuario"}
    try:
        term = fabrica()
        ti, ai = LT.enganchar(term, cred, en_ejecucion)
    except LT.TerminalNoDisponible as e:
        decir(f"BLOQUEADO: {LT.censurar(str(e), cred)}")
        return 2
    codigo = 0
    try:
        guarda()
        proc = procedencia(term, ti, ai)
        registro["procedencia"] = proc
        ahora = int(reloj())
        if a.inventario:
            inv = INV.inventario(term, regla, ahora, proc, int(ti.maxbars), a.grupo, lista_simbolos(a.simbolos, universos),
                                 not a.sin_profundidad, a.dias_ticks,
                                 progreso=lambda k, n, s: decir(f"  {k}/{n} {s}") if k % 25 == 0 or k == n else None)
            ruta = f"{data}/inventario/inventario_{sello}.json"
            escribir_json(ruta, inv)
            decir(INV.texto_resumen(inv))
            decir(f"inventario: {ruta}")
            registro.update(resultado="ok", inventario=ruta, deteccion_desfase_en_vivo=inv["deteccion_desfase_en_vivo"])
        else:
            todos = INV.simbolos_disponibles(term, None)
            elegidos = SB.resolver(lista_simbolos(a.simbolos, universos), todos)
            fich = SB.nombres_fichero(elegidos)
            simbolos = {s: {"base": todos[s]["base"], "sufijo": todos[s]["sufijo"], "fichero": fich[s],
                            "punto": todos[s]["punto"], "digitos": todos[s]["digitos"],
                            "precio_velas": todos[s]["precio_velas"],
                            "es_fx": todos[s]["regla_sufijo"] == "par de divisas"} for s in elegidos}
            for s in elegidos:  # clase de sesion y bolsa: huecos de 1d por clase (fase C); sin clase, como siempre
                clase, bolsa = UNI.calendario(todos[s])
                if clase is not None:
                    simbolos[s].update(clase=clase, bolsa=bolsa)
            vivos = [s for s in sorted(todos) if todos[s]["base"].upper() in INV.LIQUIDOS and not todos[s]["base_compartida"]]
            viva = HR.detectar_en_vivo(term, vivos[:3], ahora, regla)
            registro["deteccion_desfase_en_vivo"] = viva
            decir(f"desfase en vivo: observaciones={viva['observaciones']} regla={viva['desfase_regla_h']} h "
                  f"concluyente={viva['concluyente']} coincide={viva['coincide']}")
            if viva["concluyente"] and not viva["coincide"]:
                raise ValueError(f"el desfase observado no es el de la regla {regla.nombre}: elige otra con --regla")
            salida = os.path.abspath(a.salida or f"{data}/{a.hasta.isoformat()}")
            if os.path.commonpath([salida, os.path.abspath(data)]) != os.path.abspath(data):
                raise ValueError(f"--salida tiene que estar bajo {data}")
            cache = os.path.join(data, "_trozos", LT.slug(proc["broker"]), regla.nombre.replace(":", "_"))
            man, est = D.descargar(term, simbolos, periodos, a.desde, a.hasta, regla, salida, cache, proc, a.refrescar,
                                   guarda, decir, lambda t: LT.comprobar_sin_secretos(t, cred))
            filas = sum(e["filas"] for e in man["ficheros"])
            octetos = sum(e.get("bytes", 0) for e in man["ficheros"])
            decir(f"descarga: {len(man['ficheros'])} series, {filas} filas, {octetos / 1024 ** 2:.1f} MiB en {salida}")
            decir(f"  trozos pedidos {est['trozos_pedidos']}, reutilizados {est['trozos_reutilizados']}; "
                  f"hash_conjunto {man['hash_conjunto']}")
            registro.update(resultado="ok" if est["coherencia_hora"] else "regla de hora incoherente", salida=salida,
                            hash_conjunto=man["hash_conjunto"], filas=filas, bytes=octetos, **est)
            if not est["coherencia_hora"]:
                decir("AVISO: el cierre semanal no cuadra con la regla de hora en alguna serie (ver manifest)")
                codigo = 1
    except ParadaDisco as e:
        decir(f"PARADA: {e}")
        registro["resultado"], codigo = f"parada: {e}", 3
    except (D.ErrorTerminal, D.ErrorFormato) as e:
        msg = LT.censurar(str(e), cred)
        decir(f"FALLO: {msg}. La descarga es reanudable: vuelve a lanzar la misma orden.")
        registro["resultado"], codigo = f"fallo: {msg}", 1
    except ValueError as e:
        decir(f"BLOQUEADO: {LT.censurar(str(e), cred)}")
        registro["resultado"], codigo = f"bloqueado: {LT.censurar(str(e), cred)}", 2
    finally:
        term.shutdown()
        t1 = reloj()
        registro.update(fin_utc=HR.iso(int(t1 * 1000)), duracion_s=round(t1 - t0, 1), codigo=codigo)
        accion = "inventario" if a.inventario else "descarga"
        escribir_json(f"{runs}/{accion}_{sello}_{os.getpid()}.json", registro)
    return codigo


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        from extractor_mt5_lib import selftests

        return selftests.correr(ejecutar)
    return ejecutar(argv)


if __name__ == "__main__":
    raise SystemExit(main())
