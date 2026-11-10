"""Publicador MT5 -> qn (TI-12-MT5, fase B): rellena y publica en un topic de qn las velas cerradas de MetaTrader 5, con la
fuente como tag. Pensado para el Programador de tareas (cada 15 min y al iniciar sesion; ver publicador_mt5_tarea.xml).

    .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --ejecutar --topic NOMBRE [--simbolos @fx28] [--intervalos 1d,1h,5m,1m]
    .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --simular --sin-credenciales [--desde AAAA-MM-DD]
    .venv/Scripts/python -X utf8 scripts/publicador_mt5.py --selftest

- `--simbolos`: `@fx28` (por defecto), nombres, o un universo con nombre de la fase C (`@continuo`, `@us_grandes`...; ver
  scripts/extractor_mt5_lib/universos.py). El tag `symbol` es la base normalizada (EURUSD), salvo las acciones de
  `@us_grandes`, que llevan su ticker (BRK-B). La vela 1d de todas las clases: sesion = fecha del servidor, publicada al
  pasar el servidor al dia siguiente (17:00 de Nueva York); los huecos de mercado de 1d se clasifican por clase.

- Lectura de MT5 con la envoltura de solo lectura del extractor (scripts/extractor_mt5_lib/lectura.py): nunca envia
  ordenes. Por defecto `initialize(path)` + `login` con E:/quantdesk-lab/secrets/mt5.json (o QDL_MT5_SECRETS); con
  `--sin-credenciales`, se engancha a un terminal que el usuario ya abrio y autentico.
- qn: replicas en QN_URLS (separadas por comas), entorno QN_ENV (main), token en E:/quantdesk-lab/secrets/qn-mt5.token (o
  la ruta de QDL_QN_TOKEN_FILE). El token y las credenciales no salen en ninguna salida (guarda de secretos).
- Topic: `--topic`, obligatorio para publicar y sin valor por defecto. Tiene que ser un topic NUEVO con tags symbol,
  interval y source (network: market.ohlcv no admite un tag mas); el nombre lo decide el usuario.
- Seguro de esquema: antes de publicar se lee el esquema del topic; si no declara los tres tags, o si `source` es a la
  vez tag y campo del objeto, no se publica nada (BLOQUEADO). Asi el publicador queda desactivado contra qn real hasta
  que exista el topic.
- `--simular`: hace todo menos publicar y no toca qn (ni token): dice cuantas velas publicaria desde la fecha inicial.
- Ejecucion unica con candado (E:/quantdesk-lab/runs/TI-12-MT5/publicador/publicador.lock); si hay otra, sale con 0.
- Registro: E:/quantdesk-lab/runs/TI-12-MT5/publicador/ (ultimo.json y publicador_<fecha>.jsonl, una linea por ejecucion).

Salida 0 ok (o ya habia otra ejecucion); 1 alguna serie con error (la siguiente ejecucion retoma desde lo que qn
confirma); 2 BLOQUEADO (terminal, token, esquema o permisos); 3 PARADA por espacio en disco.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_env import LAB, LAB_ENV  # noqa: E402

os.environ.update(LAB_ENV)

import extractor_mt5 as X  # noqa: E402  (guarda de disco y carga de credenciales)
from extractor_mt5_lib import descarga as D  # noqa: E402
from extractor_mt5_lib import hora as HR  # noqa: E402
from extractor_mt5_lib import inventario as INV  # noqa: E402
from extractor_mt5_lib import lectura as LT  # noqa: E402
from extractor_mt5_lib import simbolos as SB  # noqa: E402
from extractor_mt5_lib import universos as UNI  # noqa: E402
from publicador_mt5_lib import nucleo as N  # noqa: E402
from publicador_mt5_lib import qn as Q  # noqa: E402

RUNS = LAB + "/runs/TI-12-MT5/publicador"
RUTA_TOKEN = "E:/quantdesk-lab/secrets/qn-mt5.token"
VAR_TOKEN = "QDL_QN_TOKEN_FILE"
MARCADOR_TOPIC = "TOPIC_POR_DECIDIR"  # el del XML de la tarea: hasta que el usuario lo cambie, no se publica


def argumentos(argv) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Publicador MT5 -> qn (TI-12-MT5)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--ejecutar", action="store_true")
    g.add_argument("--simular", action="store_true")
    g.add_argument("--selftest", action="store_true")
    p.add_argument("--topic", help="topic de qn (nuevo, con tags symbol, interval y source); sin valor por defecto")
    p.add_argument("--simbolos", default="@fx28")
    p.add_argument("--intervalos", default="1d,1h,5m,1m")
    p.add_argument("--desde", type=dt.date.fromisoformat, help="fecha inicial para todas las series vacias en qn")
    p.add_argument("--sin-credenciales", action="store_true")
    p.add_argument("--regla", default=HR.REGLA_DEFECTO)
    p.add_argument("--fuente", default="mt5", help="valor del tag de la fuente (mt5, o mt5:<broker>)")
    p.add_argument("--hilos", type=int, default=8)
    p.add_argument("--ventana", type=int, default=64)
    p.add_argument("--max-objetos-por-5min", type=int, default=None,
                   help="tope de objetos enviados en cualquier ventana de 5 min (carga historica); sin tope por defecto")
    p.add_argument("--max-objetos", type=int, default=None,
                   help="tope de objetos por ejecucion; el resto queda para la siguiente pasada; sin tope por defecto")
    p.add_argument("--pausa-serie-s", type=float, default=5.0,
                   help="pausa entre simbolos al leer MT5 (2026-11-10: el broker bloqueo la cuenta por exceso de descargas)")
    p.add_argument("--republicar-revisiones", action="store_true",
                   help="republica las velas de la cola que qn tiene con otro contenido (por defecto solo se cuentan)")
    return p.parse_args(argv)


def problema_de_esquema(cfg: N.Config, doc: dict) -> str | None:
    """None si el topic sirve: declara los tres tags y `source` no es ademas un campo del objeto."""
    tags = list(doc.get("tags") or [])
    esperados = {cfg.tag_simbolo, cfg.tag_intervalo, cfg.tag_fuente}
    if not esperados <= set(tags):
        return f"el topic {cfg.topic} declara los tags {tags}, le faltan {sorted(esperados - set(tags))}"
    props = set(((doc.get("schema") or {}).get("properties") or {}))
    if cfg.tag_fuente in props:
        return f"en el topic {cfg.topic}, {cfg.tag_fuente!r} es a la vez tag y campo del objeto"
    if cfg.fuente_en_objeto:
        return "fuente_en_objeto no es compatible con la fuente como tag"
    return None


def leer_token(ruta: str | None = None) -> str:
    ruta = ruta or os.environ.get(VAR_TOKEN) or RUTA_TOKEN
    try:
        with open(ruta, encoding="utf-8") as f:
            tok = f.read().strip()
    except OSError as e:
        raise LT.TerminalNoDisponible(f"no se pudo leer el token de qn de {ruta}: {type(e).__name__}") from None
    if not tok:
        raise LT.TerminalNoDisponible(f"el fichero del token de qn {ruta} esta vacio")
    return tok


def urls_de_entorno() -> list[str]:
    return [u.strip() for u in os.environ.get("QN_URLS", "").split(",") if u.strip()]


def ejecutar(argv, fabrica=LT.importar_paquete, cargar_cred=X.cargar_credenciales_defecto, cargar_token=leer_token,
             urls=None, reloj=time.time, en_ejecucion=LT.terminal_en_ejecucion, runs: str = RUNS,
             guarda=X.guarda_disco, espera_max_s: float = 30.0, universos: dict | None = None,
             monotono=time.monotonic, dormir=time.sleep) -> int:
    a = argumentos(argv)
    t0 = reloj()
    registro = {"tarea": "TI-12-MT5 publicador", "argv": list(argv), "inicio_utc": HR.iso(int(t0 * 1000)),
                "modo": "simular" if a.simular else "ejecutar", "series": []}
    secretos = None

    def decir(txt: str) -> None:
        print(LT.comprobar_sin_secretos(txt, secretos), flush=True)

    def guardar(codigo: int) -> int:
        t1 = reloj()
        registro.update(fin_utc=HR.iso(int(t1 * 1000)), duracion_s=round(t1 - t0, 1), codigo=codigo)
        texto = LT.comprobar_sin_secretos(json.dumps(registro, sort_keys=True, ensure_ascii=False), secretos)
        os.makedirs(runs, exist_ok=True)
        dia = dt.datetime.fromtimestamp(t0, tz=dt.timezone.utc).strftime("%Y-%m-%d")
        with open(os.path.join(runs, f"publicador_{dia}.jsonl"), "a", encoding="utf-8", newline="\n") as f:
            f.write(texto + "\n")
        with open(os.path.join(runs, "ultimo.json.tmp"), "w", encoding="utf-8", newline="\n") as f:
            f.write(texto + "\n")
        os.replace(os.path.join(runs, "ultimo.json.tmp"), os.path.join(runs, "ultimo.json"))
        return codigo

    intervalos = [x.strip() for x in a.intervalos.split(",") if x.strip()]
    if not intervalos or any(x not in N.INTERVALOS for x in intervalos):
        print(f"BLOQUEADO: --intervalos admite {list(N.INTERVALOS)}")
        return 2
    candado = N.Candado(os.path.join(runs, "publicador.lock"), N.Config(urls=[]).caducidad_candado_s)
    if not candado.tomar():
        registro["resultado"] = "otra ejecucion en curso: no se hace nada"
        decir("publicador: otra ejecucion en curso (candado activo); no se hace nada")
        return guardar(0)
    registro["candado_recuperado"] = candado.recuperado
    term = None
    try:
        try:
            regla = HR.regla_desde_texto(a.regla)
            if not a.simular and (not a.topic or MARCADOR_TOPIC in a.topic):
                raise ValueError("falta --topic: el topic nuevo (tags symbol, interval y source) lo decide el usuario")
            ritmo = N.Ritmo(a.max_objetos_por_5min, a.max_objetos, reloj=monotono, dormir=dormir)
            if a.pausa_serie_s < 0:
                raise ValueError("--pausa-serie-s no puede ser negativa")
            cred = cargar_cred(a)
            token = None if a.simular else cargar_token()
        except (ValueError, LT.TerminalNoDisponible) as e:
            registro["resultado"] = f"bloqueado: {e}"
            decir(f"BLOQUEADO: {e}")
            return guardar(2)
        secretos = LT.Secretos(cred, token)
        cfg = N.Config(urls=list(urls if urls is not None else urls_de_entorno()), env=os.environ.get("QN_ENV") or "main",
                       topic=a.topic, fuente=a.fuente, hilos=a.hilos, ventana=a.ventana, espera_max_s=espera_max_s,
                       republicar_revisiones=a.republicar_revisiones)
        registro["topic"] = cfg.topic
        cliente = None
        if not a.simular:
            try:
                cliente = Q.ClienteQn(cfg.urls, token, env=cfg.env, espera_max_s=cfg.espera_max_s)
                doc = cliente.esquema(cfg.topic)
            except Q.ErrorQnTopicDesconocido:
                registro["resultado"] = f"bloqueado: topic no registrado en qn ({cfg.topic})"
                decir(f"BLOQUEADO: el topic {cfg.topic} no esta registrado en qn (UnknownTopic); no se publica nada")
                return guardar(2)
            except (ValueError, Q.ErrorQn) as e:
                registro["resultado"] = f"bloqueado: {LT.censurar(str(e), secretos)}"
                decir(f"BLOQUEADO: qn ({cfg.topic}): {LT.censurar(str(e), secretos)}")
                return guardar(2)
            problema = problema_de_esquema(cfg, doc)
            if problema:
                registro["resultado"] = f"bloqueado: {problema}"
                decir(f"BLOQUEADO: {problema}: no se publica")
                return guardar(2)
        try:
            term = fabrica()
            ti, ai = LT.enganchar(term, cred, en_ejecucion)
        except LT.TerminalNoDisponible as e:
            term = None
            registro["resultado"] = f"bloqueado: {LT.censurar(str(e), secretos)}"
            decir(f"BLOQUEADO: {LT.censurar(str(e), secretos)}")
            return guardar(2)
        guarda()
        registro["procedencia"] = LT.procedencia(term, ti, ai)
        todos = INV.simbolos_disponibles(term, None)
        if universos is None:  # etiquetas de las acciones (BRK-B) y grupos @...; sin fichero solo vale @fx28 o nombres
            try:
                universos = UNI.cargar()
            except ValueError:
                universos = None
        try:
            pedidos = X.lista_simbolos(a.simbolos, universos)
            elegidos = SB.resolver(pedidos, todos)
        except ValueError as e:
            registro["resultado"] = f"bloqueado: {e}"
            decir(f"BLOQUEADO: {e}")
            return guardar(2)
        ahora = int(reloj())
        codigo = 0
        for n_sim, sim in enumerate(elegidos):
            if n_sim and a.pausa_serie_s:
                dormir(a.pausa_serie_s)  # dosificar las consultas al broker
            info ={"punto": todos[sim]["punto"], "digitos": todos[sim]["digitos"], "precio_velas": todos[sim]["precio_velas"]}
            for iv in intervalos:
                if ritmo.agotado and cliente is not None:  # tope por ejecucion: el resto, en la siguiente pasada
                    registro["series"].append({"simbolo": UNI.etiqueta(sim, todos[sim]["base"], universos),
                                               "simbolo_mt5": sim, "intervalo": iv, "parada_por_tope": True})
                    continue
                try:
                    r = N.serie(cfg, cliente, term, sim, UNI.etiqueta(sim, todos[sim]["base"], universos), info, iv, regla,
                                ahora, a.desde, candado, UNI.calendario(todos[sim]), ritmo)
                except (D.ErrorTerminal, D.ErrorFormato, Q.ErrorQnAgotado, Q.ErrorQnPermanente) as e:
                    if isinstance(e, (Q.ErrorQnAutorizacion, Q.ErrorQnTopicDesconocido)):
                        raise  # fatales: paran toda la ejecucion
                    r = {"simbolo": UNI.etiqueta(sim, todos[sim]["base"], universos), "simbolo_mt5": sim, "intervalo": iv,
                         "error": LT.censurar(str(e), secretos)}
                if r.get("error"):
                    codigo = 1
                registro["series"].append(r)
                hm = r.get("huecos_mercado", {})
                decir(f"{r['simbolo']:>8} {iv:>3}: nuevas {r.get('nuevas', 0)}, publicadas {r.get('publicadas', 0)}, "
                      f"duplicadas {r.get('duplicadas', 0)}, huecos de cola rellenados {r.get('huecos_cola_rellenados', 0)}, "
                      f"revisiones {r.get('revisiones_detectadas', 0)}, sin publicar {r.get('sin_publicar', 0)}; "
                      f"huecos de mercado: fin de semana {hm.get('fin_de_semana', 0)}, otros {hm.get('otros', 0)}"
                      + (f"; ERROR {r['error']}" if r.get("error") else ""))
        if cliente is not None:
            registro["qn"] = dict(cliente.estadisticas)
        registro["ritmo"] = ritmo.resumen()
        if ritmo.agotado:
            decir(f"publicador: tope de {ritmo.por_ejecucion} objetos por ejecucion alcanzado; el resto sigue en la "
                  "siguiente pasada")
        registro["resultado"] = "ok" if codigo == 0 else "series con error (se retoma en la siguiente ejecucion)"
        return guardar(codigo)
    except Q.ErrorQnAutorizacion as e:
        registro["resultado"] = f"bloqueado: qn rechazo el token ({e.estado})"
        decir(f"BLOQUEADO: qn rechazo el token o el permiso (HTTP {e.estado})")
        return guardar(2)
    except Q.ErrorQnTopicDesconocido:
        registro["resultado"] = f"bloqueado: topic no registrado en qn ({a.topic})"
        decir(f"BLOQUEADO: el topic {a.topic} no esta registrado en qn (UnknownTopic); no se publica nada")
        return guardar(2)
    except X.ParadaDisco as e:
        registro["resultado"] = f"parada: {e}"
        decir(f"PARADA: {e}")
        return guardar(3)
    finally:
        if term is not None:
            term.shutdown()
        candado.soltar()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        from publicador_mt5_lib import selftests

        return selftests.correr(ejecutar)
    return ejecutar(argv)


if __name__ == "__main__":
    raise SystemExit(main())
