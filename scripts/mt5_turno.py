"""Turno exclusivo de MT5, sin importar MT5 ni leer credenciales.

Uso: python mt5_turno.py --plan "texto" -- <orden...>
Pruebas: python mt5_turno.py --selftest (sólo directorios temporales).

La liberación relee el identificador antes de borrar. Se acepta la ventana mínima
entre esa lectura y unlink: los participantes deben respetar el protocolo. La
recuperación de huérfanos se serializa además mediante recuperacion.lock, un
mutex del SO que se libera incluso al morir el proceso. Ese fichero auxiliar
permanece, pero nunca representa la propiedad del turno.
finally libera el turno en salidas normales, excepciones y KeyboardInterrupt;
no puede hacerlo tras taskkill /F o el límite de 6 h del Programador. Sólo se
recuperan huérfanos de quantdesk-model/tarea-programada, muertos y de más de 2 h.
Cada intento válido escribe una línea; si falla el almacenamiento, I3 depende
de que stderr esté disponible (pythonw puede no tenerlo). No se captura ni se
retransmite la salida de la hija. Una interrupción termina y espera a la hija
antes de soltar el turno, para evitar dejarla trabajando sin exclusividad.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

PROYECTO = "quantdesk-model"
SESION_DEFECTO = "tarea-programada"
ULTIMO = "E:/quantdesk-lab/runs/TI-12-MT5/publicador/ultimo.json"
OMITIR = re.compile(r"secret|password|token|key", re.IGNORECASE)
CAMPOS_SERIE = ("simbolo", "nuevas", "publicadas", "retenidas_sin_historia", "error")
CAMPOS_DUENO = {"proyecto", "sesion", "pid", "inicio", "plan"}


def ahora() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sanear(texto: object) -> str:
    texto = str(texto)
    return "<omitido>" if OMITIR.search(texto) else texto


def error(exc: BaseException) -> str:
    return (type(exc).__name__ + ": " + sanear(exc))[:300]


def instante(texto: object) -> float:
    fecha = dt.datetime.fromisoformat(str(texto))
    if fecha.tzinfo is None:
        raise ValueError("instante sin zona horaria")
    return fecha.timestamp()


def pid_vivo(pid: object) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    if os.name == "nt":
        # os.kill(pid, 0) no es una consulta segura en Windows.
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.GetExitCodeProcess.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.CloseHandle.restype = wintypes.BOOL
        if pid > 0xFFFFFFFF:
            return False
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() == 5  # acceso denegado: no afirmar que murió
        try:
            codigo = wintypes.DWORD()
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(codigo)) or codigo.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except (PermissionError, OverflowError):
        return True


def leer_candado(ruta: Path) -> tuple[dict, str, float]:
    # Leer y obtener mtime del mismo fichero, aunque otro proceso lo sustituya.
    with ruta.open("r", encoding="utf-8", errors="replace") as fichero:
        contenido = fichero.read()
        modificado = os.fstat(fichero.fileno()).st_mtime
    try:
        datos = json.loads(contenido)
        if not isinstance(datos, dict):
            datos = {}
    except ValueError:
        datos = {}
    try:
        if not CAMPOS_DUENO <= datos.keys():
            raise ValueError("candado parcial: dueño desconocido")
        desde = instante(datos.get("inicio"))
    except (ValueError, TypeError, OverflowError):
        desde = modificado
    return datos, contenido, desde


@contextlib.contextmanager
def mutex_recuperacion(ruta: Path):
    """Evita que dos recuperadores borren sucesivamente un turno nuevo."""
    with ruta.open("a+b") as fichero:
        if os.fstat(fichero.fileno()).st_size == 0:
            fichero.write(b"\0")
            fichero.flush()
        fichero.seek(0)
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(fichero.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                yield False
                return
            try:
                yield True
            finally:
                fichero.seek(0)
                msvcrt.locking(fichero.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            try:
                fcntl.flock(fichero.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                yield False
                return
            try:
                yield True
            finally:
                fcntl.flock(fichero.fileno(), fcntl.LOCK_UN)


def huerfano_propio(datos: dict, desde: float) -> bool:
    return (CAMPOS_DUENO <= datos.keys()
            and datos.get("proyecto") == PROYECTO
            and datos.get("sesion") == SESION_DEFECTO
            and isinstance(datos.get("pid"), int) and not isinstance(datos["pid"], bool)
            and datos["pid"] > 0 and time.time() - desde > 7200
            and not pid_vivo(datos["pid"]))


def ocupado(datos: dict, desde: float) -> str:
    if not CAMPOS_DUENO <= datos.keys():
        datos = {}
    mensaje = (f"turno ocupado: {sanear(datos.get('proyecto', 'desconocido'))}/"
               f"{sanear(datos.get('sesion', 'desconocido'))}, pid {sanear(datos.get('pid', '?'))} "
               f"({'vivo' if pid_vivo(datos.get('pid')) else 'muerto'}), "
               f"desde {sanear(datos.get('inicio', 'desconocido'))}")
    if time.time() - desde > 7200:
        mensaje += "; más de 2 h: consultar a su dueña"
    return mensaje[:300]


def tomar_turno(a: argparse.Namespace, registro: dict, identificador: str) -> bool:
    limite = time.monotonic() + a.esperar_s
    ruta = a.dir_mt5 / "turno.lock"
    a.dir_mt5.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            fd = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            try:
                datos, _, desde = leer_candado(ruta)
            except FileNotFoundError:
                continue
            if huerfano_propio(datos, desde):
                with mutex_recuperacion(a.dir_mt5 / "recuperacion.lock") as exclusivo:
                    if exclusivo:
                        try:
                            # Revalidar dentro del mutex; nunca borrar lo observado antes de él.
                            datos, contenido, desde = leer_candado(ruta)
                            if huerfano_propio(datos, desde):
                                ruta.unlink()
                                registro["errores"].append(
                                    ("candado huérfano propio retirado: " + sanear(contenido))[:300])
                                continue
                        except FileNotFoundError:
                            continue
            if time.time() - desde > 7200 or time.monotonic() >= limite:
                registro["errores"].append(ocupado(datos, desde))
                return False
            time.sleep(min(a.sondeo_s, max(0, limite - time.monotonic())))
            continue
        registro["inicio"] = ahora()
        datos = {"proyecto": PROYECTO, "sesion": os.environ.get("MT5_TURNO_SESION", SESION_DEFECTO),
                 "pid": os.getpid(), "inicio": registro["inicio"], "plan": a.plan,
                 "token": identificador}
        # Una escritura del JSON completo, seguida de flush y fsync.
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fichero:
            fichero.write(json.dumps(datos, ensure_ascii=False))
            fichero.flush()
            os.fsync(fichero.fileno())
        return True


def liberar(ruta: Path, identificador: str, registro: dict) -> None:
    try:
        datos, _, _ = leer_candado(ruta)
        if datos.get("token") != identificador:
            registro["errores"].append("conflicto al liberar: identificador distinto, ausente o candado corrupto")
            return
        ruta.unlink()
    except FileNotFoundError:
        registro["errores"].append("conflicto al liberar: candado desaparecido")
    except Exception as exc:
        registro["errores"].append(("conflicto al liberar: " + error(exc))[:300])


def leer_series(ruta: Path, registro: dict) -> None:
    try:
        with ruta.open(encoding="utf-8") as fichero:
            if os.fstat(fichero.fileno()).st_mtime <= instante(registro["inicio"]):
                registro["detalle"] = "ultimo.json anterior o igual al inicio del turno; no se atribuye"
                return
            datos = json.load(fichero)
        if not isinstance(datos, dict) or not isinstance(datos.get("series"), list):
            raise ValueError("ultimo.json sin lista series")
        series = []
        for serie in datos["series"]:
            if not isinstance(serie, dict):
                raise ValueError("series debe contener objetos")
            fila = {}
            for clave in CAMPOS_SERIE:
                if clave in serie:
                    valor = serie[clave]
                    if not isinstance(valor, (str, int, float, bool, type(None))):
                        raise ValueError("campo de serie no escalar")
                    fila[clave] = sanear(valor) if isinstance(valor, str) else valor
            series.append(fila)
        registro["series"] = series
    except Exception as exc:
        registro["detalle"] = error(exc)


def registrar(directorio: Path, registro: dict) -> None:
    registro["fin"] = ahora()
    linea = json.dumps(registro, ensure_ascii=False) + "\n"
    try:
        with (directorio / "uso.jsonl").open("a", encoding="utf-8", newline="\n") as fichero:
            fichero.write(linea)
    except (OSError, UnicodeError):
        if sys.stderr is not None:
            try:
                sys.stderr.write(linea)
                sys.stderr.flush()
            except (OSError, UnicodeError):
                pass  # Tampoco hay almacenamiento para el fallback.


def ejecutar(a: argparse.Namespace, orden: list[str]) -> int:
    registro = {"proyecto": PROYECTO, "sesion": sanear(os.environ.get("MT5_TURNO_SESION", SESION_DEFECTO)),
                "inicio": ahora(), "fin": None, "plan": sanear(a.plan),
                "orden": [sanear(arg) for arg in orden], "exit": 3, "errores": []}
    identificador = str(uuid.uuid4())
    # Comprobar también si la escritura/fsync del candado falla tras crearlo.
    creado = False
    proceso = None
    ejecutada = False
    try:
        try:
            if not tomar_turno(a, registro, identificador):
                registro["exit"] = 4
                return 4
            creado = True
        except Exception as exc:
            registro["errores"].append(error(exc))
            return 3
        try:
            ejecutada = True
            proceso = subprocess.Popen(
                orden, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            registro["exit"] = proceso.wait()
            if registro["exit"]:
                registro["errores"].append(f"orden terminó con código {registro['exit']}")
        except KeyboardInterrupt as exc:
            registro["exit"] = 130
            registro["errores"].append(error(exc))
        except Exception as exc:
            registro["exit"] = 1
            registro["errores"].append(error(exc))
        return registro["exit"]
    except KeyboardInterrupt as exc:
        registro["exit"] = 130
        registro["errores"].append(error(exc))
        return 130
    finally:
        try:
            if proceso is not None and proceso.poll() is None:
                try:
                    proceso.kill()
                    proceso.wait()
                except Exception as exc:
                    registro["errores"].append(error(exc))
            if ejecutada and any(Path(arg.replace("\\", "/")).name.lower() == "publicador_mt5.py"
                                 for arg in orden):
                leer_series(a.ultimo_json, registro)
        finally:
            if not creado:
                # También cubre una interrupción tras la escritura del JSON, antes
                # de retornar de tomar_turno. Nunca liberar un turno observado ajeno.
                try:
                    creado = leer_candado(a.dir_mt5 / "turno.lock")[0].get("token") == identificador
                except OSError:
                    pass
            if creado:
                liberar(a.dir_mt5 / "turno.lock", identificador, registro)
            registrar(a.dir_mt5, registro)


class Argumentos(argparse.ArgumentParser):
    def error(self, message):
        # argparse normal reproduciría argumentos inválidos, que pueden ser sensibles.
        super().error(sanear(message))


def duracion(texto: str) -> float:
    valor = float(texto)
    if not math.isfinite(valor) or valor < 0:
        raise argparse.ArgumentTypeError("se requiere un número finito no negativo")
    return valor


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--selftest"]:
        return selftest()
    parser = Argumentos(description="Ejecuta una orden con el turno exclusivo de MT5")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--dir-mt5", type=Path, default=Path.home() / ".claude" / "mt5")
    parser.add_argument("--ultimo-json", type=Path, default=Path(ULTIMO))
    parser.add_argument("--sondeo-s", type=duracion, default=60.0)
    parser.add_argument("--esperar-s", type=duracion, default=1800.0)
    if "--" not in argv:
        parser.error("se requiere -- antes de la orden")
    corte = argv.index("--")
    a = parser.parse_args(argv[:corte])
    orden = argv[corte + 1:]
    if not orden or a.sondeo_s <= 0:
        parser.error("se requieren una orden y --sondeo-s mayor que cero")
    return ejecutar(a, orden)


def selftest() -> int:
    """Pruebas de contrato; ninguna usa el directorio MT5 ni el publicador reales."""
    # Las pruebas se incluyen aquí porque sólo están autorizadas dos rutas.
    import tempfile
    import unittest
    from unittest import mock
    import xml.etree.ElementTree as ET

    class TurnoTests(unittest.TestCase):
        def setUp(self):
            self.temporal = tempfile.TemporaryDirectory(prefix="mt5-turno-")
            self.addCleanup(self.temporal.cleanup)
            self.raiz = Path(self.temporal.name)
            self.directorio = self.raiz / "mt5"
            self.ultimo = self.raiz / "ultimo.json"
            self.lock = self.directorio / "turno.lock"
            self.log = self.directorio / "uso.jsonl"
            self.script = str(Path(__file__).resolve())
            self.env = dict(os.environ, MT5_TURNO_SESION=SESION_DEFECTO)
            parche = mock.patch.dict(os.environ, {"MT5_TURNO_SESION": SESION_DEFECTO})
            parche.start()
            self.addCleanup(parche.stop)

        def args(self, espera="0.15"):
            return ["--dir-mt5", str(self.directorio), "--ultimo-json", str(self.ultimo),
                    "--plan", "prueba diaria", "--sondeo-s", "0.02", "--esperar-s", espera]

        def comando(self, codigo="pass", extra=()):
            return [sys.executable, "-X", "utf8", "-c", codigo, *extra]

        def cli(self, codigo="pass", extra=(), espera="0.15", orden=None):
            return [sys.executable, "-X", "utf8", self.script, *self.args(espera), "--",
                    *(orden if orden is not None else self.comando(codigo, extra))]

        def correr(self, codigo="pass", extra=(), espera="0.15", orden=None):
            return subprocess.run(self.cli(codigo, extra, espera, orden), env=self.env,
                                  capture_output=True, text=True, encoding="utf-8", timeout=15)

        def registros(self, cantidad=1):
            contenido = self.log.read_bytes()
            self.assertNotIn(b"\r", contenido)
            lineas = contenido.decode("utf-8").splitlines()
            self.assertEqual(len(lineas), cantidad)
            registros = [json.loads(linea) for linea in lineas]
            permitidos = {"proyecto", "sesion", "inicio", "fin", "plan", "orden", "exit", "errores",
                          "series", "detalle"}
            for registro in registros:
                self.assertLessEqual(set(registro), permitidos)
                for clave in ("inicio", "fin"):
                    self.assertTrue(registro[clave].endswith("Z"))
                    instante(registro[clave])
            return registros

        def poner_lock(self, edad=0, pid=None, propio=False, inicio=None):
            self.directorio.mkdir(parents=True, exist_ok=True)
            datos = {"proyecto": PROYECTO if propio else "otro", "sesion": SESION_DEFECTO if propio else "raiz",
                     "pid": os.getpid() if pid is None else pid,
                     "inicio": inicio or dt.datetime.fromtimestamp(time.time() - edad, dt.timezone.utc).isoformat(),
                     "plan": "ocupado", "token": "ajeno"}
            self.lock.write_text(json.dumps(datos), encoding="utf-8")
            os.utime(self.lock, (time.time() - edad, time.time() - edad))
            return self.lock.read_bytes()

        def esperar_fichero(self, ruta, proceso):
            limite = time.monotonic() + 10
            while not ruta.exists() and time.monotonic() < limite:
                self.assertIsNone(proceso.poll(), "el proceso terminó antes de la señal")
                time.sleep(0.01)
            self.assertTrue(ruta.exists(), "la orden falsa no señaló su arranque")

        def lanzar(self, comando):
            proceso = subprocess.Popen(comando, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            def cerrar():
                if proceso.poll() is None:
                    proceso.kill()
                proceso.communicate(timeout=10)
            self.addCleanup(cerrar)
            return proceso

        def test_salidas_y_creacion(self):
            for codigo in (0, 1, 3):
                with self.subTest(codigo=codigo):
                    resultado = self.correr(f"raise SystemExit({codigo})")
                    self.assertEqual(resultado.returncode, codigo, resultado.stderr)
                    self.assertFalse(self.lock.exists())
                    registro = self.registros()[0]
                    self.assertEqual(registro["exit"], codigo)
                    self.assertEqual(bool(registro["errores"]), bool(codigo))
                    self.log.unlink()

        def test_ejecutable_ausente(self):
            resultado = self.correr(orden=[str(self.raiz / "inexistente.exe")])
            self.assertEqual(resultado.returncode, 1)
            self.assertFalse(self.lock.exists())
            self.assertIn("FileNotFoundError", self.registros()[0]["errores"][0])

        def test_ajeno_vivo_se_libera(self):
            original = self.poner_lock()
            señal = self.raiz / "arranco"
            proceso = self.lanzar(self.cli(f"from pathlib import Path; Path({str(señal)!r}).touch()", espera="5"))
            time.sleep(0.2)
            self.assertFalse(señal.exists())
            self.assertEqual(self.lock.read_bytes(), original)
            self.lock.unlink()
            salida, errores = proceso.communicate(timeout=10)
            self.assertEqual(proceso.returncode, 0, errores)
            self.assertTrue(señal.exists())
            self.assertFalse(self.lock.exists())
            self.registros()

        def test_ajenos_antiguos(self):
            for pid in (os.getpid(), 2147483647):
                with self.subTest(pid=pid):
                    original = self.poner_lock(edad=7300, pid=pid)
                    inicio = time.monotonic()
                    resultado = self.correr("raise SystemExit(99)", espera="8")
                    self.assertEqual(resultado.returncode, 4)
                    self.assertLess(time.monotonic() - inicio, 4)
                    self.assertEqual(self.lock.read_bytes(), original)
                    texto = self.registros()[0]["errores"][0]
                    self.assertIn("más de 2 h", texto)
                    self.assertIn("vivo" if pid == os.getpid() else "muerto", texto)
                    self.log.unlink()

        def test_huerfano_propio(self):
            for con_identificador in (True, False):
                self.poner_lock(edad=7300, pid=2147483647, propio=True)
                if not con_identificador:
                    # Las otras raíces pueden escribir el formato anterior sin UUID.
                    datos = json.loads(self.lock.read_text(encoding="utf-8"))
                    del datos["token"]
                    self.lock.write_text(json.dumps(datos), encoding="utf-8")
                resultado = self.correr()
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                self.assertFalse(self.lock.exists())
                self.assertIn("candado huérfano propio retirado:", self.registros()[0]["errores"][0])
                self.log.unlink()

        def test_sesion_ajena_y_propio_vivo_no_se_retiran(self):
            for sesion, pid in (("otra", 2147483647), (SESION_DEFECTO, os.getpid())):
                self.poner_lock(edad=7300, pid=pid, propio=True)
                datos = json.loads(self.lock.read_text(encoding="utf-8"))
                datos["sesion"] = sesion
                self.lock.write_text(json.dumps(datos), encoding="utf-8")
                original = self.lock.read_bytes()
                self.assertEqual(self.correr().returncode, 4)
                self.assertEqual(self.lock.read_bytes(), original)
                self.registros()
                self.log.unlink()

        def test_desconocidos_ocupados(self):
            self.directorio.mkdir()
            for texto in ("", "{", "[]", '{"proyecto":"quantdesk-model"}',
                          json.dumps(dict(proyecto=PROYECTO, sesion=SESION_DEFECTO,
                                          pid=2147483647, inicio="2000-01-01T00:00:00Z"))):
                with self.subTest(texto=texto):
                    self.lock.write_text(texto, encoding="utf-8")
                    inicio = time.monotonic()
                    self.assertEqual(self.correr("raise SystemExit(99)").returncode, 4)
                    self.assertGreaterEqual(time.monotonic() - inicio, 0.15)
                    self.assertEqual(self.lock.read_text(encoding="utf-8"), texto)
                    self.assertIn("turno ocupado:", self.registros()[0]["errores"][0])
                    self.log.unlink()

        def test_fecha_desfase_y_fallback_mtime(self):
            antiguo = dt.datetime.fromtimestamp(time.time() - 7300, dt.timezone(dt.timedelta(hours=3))).isoformat()
            for fecha in (antiguo, "incorrecta", "2020-01-01T00:00:00"):
                with self.subTest(fecha=fecha):
                    original = self.poner_lock(edad=7300, inicio=fecha)
                    self.assertEqual(self.correr(espera="8").returncode, 4)
                    self.assertEqual(self.lock.read_bytes(), original)
                    self.assertIn("más de 2 h", self.registros()[0]["errores"][0])
                    self.log.unlink()

        def test_i2_conflictos_liberacion(self):
            for operacion in ("p.unlink()", "p.write_text(json.dumps({'token':'nuevo'}))",
                              "p.write_text('{')", "p.write_text('{}')"):
                with self.subTest(operacion=operacion):
                    codigo = f"import json; from pathlib import Path; p=Path({str(self.lock)!r}); {operacion}"
                    self.assertEqual(self.correr(codigo).returncode, 0)
                    self.assertIn("conflicto al liberar:", self.registros()[0]["errores"][0])
                    if "unlink" not in operacion:
                        self.assertTrue(self.lock.exists())
                        if "nuevo" in operacion:
                            self.assertEqual(json.loads(self.lock.read_text())["token"], "nuevo")
                        self.lock.unlink()
                    self.log.unlink()

        def test_i1_concurrencia_real(self):
            señal = self.raiz / "arranco"
            puerta = self.raiz / "terminar"
            codigo = (f"import time; from pathlib import Path; Path({str(señal)!r}).touch(); "
                      f"limite=time.monotonic()+10; "
                      f"\nwhile not Path({str(puerta)!r}).exists() and time.monotonic()<limite: time.sleep(.01)")
            primero = self.lanzar(self.cli(codigo, espera="5"))
            self.addCleanup(puerta.touch)
            self.esperar_fichero(señal, primero)
            datos = json.loads(self.lock.read_text(encoding="utf-8"))
            self.assertEqual(set(datos), {"proyecto", "sesion", "pid", "inicio", "plan", "token"})
            # El lanzador del venv de Windows puede añadir un proceso intermedio.
            self.assertTrue(pid_vivo(datos["pid"]))
            self.assertEqual(uuid.UUID(datos["token"]).version, 4)
            self.assertTrue(datos["inicio"].endswith("Z"))
            segundo = self.correr("raise SystemExit(99)")
            self.assertEqual(segundo.returncode, 4)
            self.assertEqual(json.loads(self.lock.read_text())["token"], datos["token"])
            puerta.touch()
            primero.communicate(timeout=10)
            self.assertEqual(primero.returncode, 0)
            self.assertEqual(sorted(r["exit"] for r in self.registros(2)), [0, 4])
            self.assertFalse(self.lock.exists())

        def test_recuperacion_concurrente(self):
            self.poner_lock(edad=7300, pid=2147483647, propio=True)
            critico = self.raiz / "orden-exclusiva"
            codigo = (f"import os,time; p={str(critico)!r}; "
                      "fd=os.open(p, os.O_CREAT|os.O_EXCL|os.O_WRONLY); "
                      "os.close(fd); time.sleep(.3); os.unlink(p)")
            procesos = [self.lanzar(self.cli(codigo, espera="5")) for _ in range(2)]
            for proceso in procesos:
                _, errores = proceso.communicate(timeout=12)
                self.assertEqual(proceso.returncode, 0, errores)
            registros = self.registros(2)
            retiradas = [e for r in registros for e in r["errores"] if "huérfano propio retirado" in e]
            self.assertEqual(len(retiradas), 1)
            self.assertFalse(self.lock.exists())
            self.assertFalse(critico.exists())

        def test_registro_no_escribible(self):
            self.directorio.mkdir()
            self.log.mkdir()  # EISDIR/PermissionError determinista incluso como administrador.
            resultado = self.correr("raise SystemExit(3)")
            self.assertEqual(resultado.returncode, 3)
            registro = json.loads(resultado.stderr)
            self.assertEqual(registro["exit"], 3)
            self.assertEqual(len(resultado.stderr.splitlines()), 1)
            self.assertFalse(self.lock.exists())

        def test_i3_una_linea_por_turno(self):
            for cantidad, codigo in enumerate((0, 1, 3), start=1):
                self.assertEqual(self.correr(f"raise SystemExit({codigo})").returncode, codigo)
                self.assertEqual(self.registros(cantidad)[-1]["exit"], codigo)
            original = self.poner_lock()
            self.assertEqual(self.correr("raise SystemExit(99)").returncode, 4)
            self.assertEqual(self.registros(4)[-1]["exit"], 4)
            self.assertEqual(self.lock.read_bytes(), original)

        def test_error_crear_candado(self):
            self.directorio.write_text("no es un directorio", encoding="utf-8")
            resultado = self.correr("raise SystemExit(99)")
            self.assertEqual(resultado.returncode, 3)
            registro = json.loads(resultado.stderr)
            self.assertEqual(registro["exit"], 3)
            self.assertTrue(registro["errores"])

        def test_fsync_y_error_escritura(self):
            with mock.patch(__name__ + ".os.fsync", side_effect=OSError("disco lleno")) as fsync:
                codigo = main([*self.args(), "--", *self.comando()])
            self.assertEqual(codigo, 3)
            fsync.assert_called_once()
            self.assertFalse(self.lock.exists())
            self.assertIn("OSError", self.registros()[0]["errores"][0])

        def test_series_frescas_filtradas(self):
            documento = {"procedencia": "privado", "series": [dict(simbolo="EURUSD", nuevas=3, publicadas=2,
                retenidas_sin_historia=1, error=None, procedencia="privado", qn={"interno": 1})]}
            codigo = (f"import json,time; from pathlib import Path; time.sleep(.02); "
                      f"Path({str(self.ultimo)!r}).write_text({json.dumps(documento)!r}, encoding='utf-8')")
            resultado = self.correr(codigo, extra=("publicador_mt5.py",))
            self.assertEqual(resultado.returncode, 0)
            registro = self.registros()[0]
            self.assertEqual(set(registro["series"][0]), set(CAMPOS_SERIE))
            self.assertIsNone(registro["series"][0]["error"])
            self.assertNotIn("privado", json.dumps(registro["series"]))

        def test_ultimo_invalido_o_viejo(self):
            for texto in (None, "{", "{}", '{"series":{}}', '{"series":[1]}',
                          '{"series":[{"error":{"qn":"privado"}}]}', '{"series":[]}'):
                with self.subTest(texto=texto):
                    if self.ultimo.exists():
                        self.ultimo.unlink()
                    if texto == '{"series":[]}':
                        self.ultimo.write_text(texto)
                        os.utime(self.ultimo, (1, 1))
                        codigo = "pass"
                    elif texto is None:
                        codigo = "pass"
                    else:
                        codigo = f"from pathlib import Path; Path({str(self.ultimo)!r}).write_text({texto!r})"
                    self.assertEqual(self.correr(codigo, extra=("publicador_mt5.py",)).returncode, 0)
                    registro = self.registros()[0]
                    self.assertIn("detalle", registro)
                    self.assertNotIn("series", registro)
                    if texto == '{"series":[]}':
                        self.assertIn("anterior", registro["detalle"])
                    self.log.unlink()

        def test_i4_saneado_y_sin_salida(self):
            palabras = ("secrets/valor", "PASSWORD=valor", "Token=valor", "apiKEY=valor")
            codigo = "import sys; print('salida ' + 'privada'); print('fallo ' + 'privado', file=sys.stderr)"
            resultado = self.correr(codigo, extra=palabras)
            self.assertEqual(resultado.stdout + resultado.stderr, "")
            registro = self.registros()[0]
            self.assertEqual(registro["orden"][-4:], ["<omitido>"] * 4)
            self.assertNotIn("salida privada", self.log.read_text())
            self.assertNotIn("fallo privado", self.log.read_text())
            self.log.unlink()
            with mock.patch(__name__ + ".subprocess.Popen", side_effect=OSError("PASSWORD=valor")):
                self.assertEqual(main([*self.args(), "--", *self.comando()]), 1)
            registro = self.registros()[0]
            self.assertEqual(registro["errores"], ["OSError: <omitido>"])
            self.assertLessEqual(len(error(OSError("x" * 500))), 300)
            self.assertFalse(self.lock.exists())

        def test_series_error_saneado(self):
            documento = {"series": [{"simbolo": "EURUSD", "error": "PASSWORD=privado"}]}
            codigo = (f"from pathlib import Path; "
                      f"Path({str(self.ultimo)!r}).write_text({json.dumps(documento)!r})")
            self.assertEqual(self.correr(codigo, extra=("publicador_mt5.py",)).returncode, 0)
            self.assertEqual(self.registros()[0]["series"][0]["error"], "<omitido>")
            self.assertNotIn("privado", self.log.read_text())

        def test_sesion_entorno_y_defecto(self):
            observado = self.raiz / "observado.json"
            codigo = (f"from pathlib import Path; "
                      f"Path({str(observado)!r}).write_bytes(Path({str(self.lock)!r}).read_bytes())")
            for sesion in (None, "sesion-prueba"):
                if sesion is None:
                    self.env.pop("MT5_TURNO_SESION", None)
                else:
                    self.env["MT5_TURNO_SESION"] = sesion
                self.assertEqual(self.correr(codigo).returncode, 0)
                esperado = sesion or SESION_DEFECTO
                self.assertEqual(json.loads(observado.read_text())["sesion"], esperado)
                self.assertEqual(self.registros()[0]["sesion"], esperado)
                self.log.unlink()

        def test_keyboard_interrupt(self):
            proceso_real = subprocess.Popen
            procesos = []
            def fabrica(*args, **kwargs):
                proceso = proceso_real(*args, **kwargs)
                procesos.append(proceso)
                esperar = proceso.wait
                def interrumpir(*args, **kwargs):
                    proceso.wait = esperar
                    raise KeyboardInterrupt()
                proceso.wait = interrumpir
                return proceso
            with mock.patch(__name__ + ".subprocess.Popen", side_effect=fabrica):
                codigo = main([*self.args(), "--", *self.comando("import time; time.sleep(30)")])
            self.assertEqual(codigo, 130)
            self.assertIsNotNone(procesos[0].poll())
            self.assertFalse(self.lock.exists())
            registro = self.registros()[0]
            self.assertEqual(registro["exit"], 130)
            self.assertIn("KeyboardInterrupt", registro["errores"][0])

        def test_sin_consola(self):
            proceso_real = subprocess.Popen
            with mock.patch(__name__ + ".subprocess.Popen", wraps=proceso_real) as popen:
                self.assertEqual(main([*self.args(), "--", *self.comando()]), 0)
            opciones = popen.call_args.kwargs
            self.assertEqual(opciones["creationflags"], subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            self.assertEqual(opciones["stdout"], subprocess.DEVNULL)
            self.assertEqual(opciones["stderr"], subprocess.DEVNULL)
            self.registros()

        def test_uso_incorrecto(self):
            for opciones in (["--plan", "x"], ["--", sys.executable],
                             ["--plan", "x", "--"], ["--plan", "x", "--sondeo-s", "0", "--", "x"],
                             ["--plan", "x", "--esperar-s", "nan", "--", "x"],
                             ["--plan", "x", "--password=privado", "--", "x"]):
                resultado = subprocess.run([sys.executable, self.script, *opciones], env=self.env,
                                          capture_output=True, text=True, timeout=10)
                self.assertEqual(resultado.returncode, 2)
                self.assertNotIn("privado", resultado.stderr)
            self.assertFalse(self.directorio.exists())

        def test_xml_solo_accion_y_recolector(self):
            repo = Path(__file__).resolve().parent.parent
            base = subprocess.run(["git", "show", "8d790e3:scripts/publicador_mt5_tarea.xml"],
                                  cwd=repo, capture_output=True, check=True).stdout
            anterior = ET.fromstring(base)
            actual = ET.parse(repo / "scripts" / "publicador_mt5_tarea.xml").getroot()
            ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
            command = actual.find("t:Actions/t:Exec/t:Command", ns)
            arguments = actual.find("t:Actions/t:Exec/t:Arguments", ns)
            pythonw = r"S:\Projects\quantdesk-model\.venv\Scripts\pythonw.exe"
            self.assertEqual(command.text, pythonw)
            self.assertEqual(arguments.text, '-X utf8 scripts\\mt5_turno.py --plan "publicador 1d fx28 diario" -- '
                             + pythonw + r" -X utf8 scripts\publicador_mt5.py --ejecutar --topic market.ohlcv.v2 --intervalos 1d")
            for nombre in ("Command", "Arguments"):
                ruta = f"t:Actions/t:Exec/t:{nombre}"
                actual.find(ruta, ns).text = anterior.find(ruta, ns).text
            self.assertEqual(ET.tostring(actual), ET.tostring(anterior))
            import run_selftests
            self.assertTrue(run_selftests.supports_selftest(str(repo / "scripts" / "mt5_turno.py")))

    resultado = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TurnoTests))
    if resultado.wasSuccessful():
        print(f"mt5_turno selftest ok: {resultado.testsRun} tests")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
