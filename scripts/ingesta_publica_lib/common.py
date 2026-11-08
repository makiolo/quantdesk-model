"""Rutas, hashes, red con ritmo y reintentos, y guarda de disco de TI-13-PUB. Solo biblioteca estandar."""
from __future__ import annotations

import datetime as dt
import email.utils
import hashlib
import json
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request

LAB = "E:/quantdesk-lab"
PUBLIC = LAB + "/data/public"
DATASETS = LAB + "/datasets/TI-13-PUB"
INFORMES_FUERA = DATASETS + "/_informes"
RUNS = LAB + "/runs/TI-13-PUB"
TMP = LAB + "/tmp/TI-13-PUB"
HF_CACHE = LAB + "/cache/hf"
EVIDENCIAS = PUBLIC + "/_licencias"

UA = "quantdesk-lab-ingesta/0.1"  # generico: sin datos personales
MOTOR = "quantdesk 69fdb39d"  # motor del entorno (DoD 8); se registra aunque esta ingesta no lo use
MOTOR_COMMIT = "69fdb39d0b67969dbdafa77f5da656511342f175"

# Guarda de disco. Los limites se miden en bytes y son los estrictos (GB decimal para el presupuesto, GiB para los libres).
PRESUPUESTO = 100 * 10**9  # TI-13-PUB entero (GAP-02)
C_LIBRE_MIN = 2 * 1024**3  # LAUNCH 4: si C: baja de 2 GB, parar
E_LIBRE_MIN = 150 * 1024**3  # E: es compartido; la raiz fija 150 GB como suelo
PAUSA_HOST = 1.0  # segundos entre peticiones al mismo host
REINTENTOS = 3  # reintentos tras el primer intento, con espera exponencial
ESPERA_MAX = 60.0


# Topes de LOTSA (ficha): como mucho 10 GB en total y 2 GB por subconjunto, medidos con el tamano que declara el Hub.
LOTSA_TOTAL_MAX = 10 * 10**9
LOTSA_SUBCONJUNTO_MAX = 2 * 10**9
MAX_FICHEROS_CACHE = 200_000  # mas ficheros que esto en la cache de HF: no se mide a mano, se aborta
FACTOR_ESCRITURA = 2  # estimacion prudente de lo procesado que se va a escribir: 2 x el crudo del dataset
CACHE_AJENA = ("torch", "xdg")  # carpetas de HF_HOME que no son descargas de huggingface_hub (TORCH_HOME, XDG_CACHE_HOME)


class ParadaDisco(RuntimeError):
    """C: o E: por debajo del suelo: parar y avisar."""


class CacheNoMedible(ParadaDisco):
    """La cache de huggingface_hub no se puede medir completa: se aborta en lugar de guardar con un subtotal."""


class PresupuestoExcedido(RuntimeError):
    """El siguiente fichero superaria el presupuesto de TI-13-PUB."""


class TopeLotsa(PresupuestoExcedido):
    """Un subconjunto de LOTSA supera 2 GB o el total de LOTSA superaria 10 GB."""


class ErrorRed(RuntimeError):
    """Fallo de red tras los reintentos (conexion cerrada, tiempo agotado, 5xx...)."""


def ahora_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_fichero(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def git_blob_sha1(contenido: bytes) -> str:
    """Id de blob de git (lo que el Hub publica como blobId para los ficheros que no son LFS)."""
    return hashlib.sha1(b"blob %d\0" % len(contenido) + contenido).hexdigest()


def escribir_json(ruta: str, obj) -> None:
    """Escritura atomica, claves ordenadas: el mismo contenido da los mismos bytes."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, ruta)


def leer_json(ruta: str, defecto=None):
    if not os.path.isfile(ruta):
        return defecto
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def hash_conjunto(pares) -> str:
    """Hash de un conjunto de (ruta, sha256): independiente del orden de entrada (manifiesto ordenado)."""
    lineas = sorted(f"{r}\t{h}" for r, h in pares)
    return sha256_bytes(("\n".join(lineas) + "\n").encode("utf-8"))


# --- guarda de disco -------------------------------------------------------------------------------------------------

def libre(unidad: str) -> int:
    return shutil.disk_usage(unidad).free


def comprobar_discos(libre_fn=libre, reserva_e: int = 0) -> dict:
    """Mide C: y E: y para si alguno esta bajo su suelo. `reserva_e` son los bytes que se van a escribir en E: ahora mismo: el
    suelo de E: se comprueba DESPUES de escribirlos (para antes de bajar de 150 GiB, no cuando ya se ha bajado)."""
    c, e = libre_fn("C:/"), libre_fn("E:/")
    if c < C_LIBRE_MIN:
        raise ParadaDisco(f"C: tiene {c / 1e9:.2f} GB libres (< 2 GiB): parar y avisar")
    if e - reserva_e < E_LIBRE_MIN:
        raise ParadaDisco(f"E: tiene {e / 1e9:.1f} GB libres y se van a escribir {reserva_e / 1e9:.2f} GB (suelo 150 GiB): parar y avisar")
    return {"libre_C_bytes": c, "libre_E_bytes": e}


def guarda(extra: int, usado_manifiestos: int, usado_cache_hf: int, libre_fn=libre, presupuesto: int | None = None,
           reserva_e: int | None = None, etiqueta: str = "siguiente") -> dict:
    """Para ANTES de pasarse: manifiestos + cache HF + lo siguiente (`extra`) deben caber en el presupuesto (100 GB por defecto),
    y C:/E: no pueden quedar por debajo de sus suelos. `reserva_e` (por defecto `extra`) son los bytes nuevos que caeran en E:."""
    limite = PRESUPUESTO if presupuesto is None else presupuesto
    medidas = comprobar_discos(libre_fn, extra if reserva_e is None else reserva_e)
    total = usado_manifiestos + usado_cache_hf + extra
    if total > limite:
        raise PresupuestoExcedido(
            f"{total / 1e9:.2f} GB (manifiestos {usado_manifiestos / 1e9:.2f} + cache HF {usado_cache_hf / 1e9:.2f} + "
            f"{etiqueta} {extra / 1e9:.2f}) superan {limite / 1e9:.0f} GB"
        )
    medidas.update(total_previsto_bytes=total)
    return medidas


def guarda_lote(escrito: int, cota_lote: int, usado_previo: int, usado_cache_hf: int, libre_fn=libre,
                presupuesto: int | None = None) -> dict:
    """Guarda INCREMENTAL de la escritura de parquet, ANTES de cada lote: lo ya escrito en el dataset (`escrito`, bytes reales
    del disco) + la cota superior del lote + lo previo (manifiestos) + la cache de HF no pueden pasar de 100 GB, y E: no puede
    quedar por debajo de su suelo tras escribir el lote. Complementa la reserva previa (2 x crudo), que es solo una estimacion."""
    return guarda(escrito + cota_lote, usado_previo, usado_cache_hf, libre_fn, presupuesto, reserva_e=cota_lote,
                  etiqueta="ya escrito del dataset + cota del siguiente lote")


def bytes_cache_hf(raiz: str = HF_CACHE, max_ficheros: int = MAX_FICHEROS_CACHE) -> int:
    """Bytes que las descargas de huggingface_hub han dejado en HF_HOME: scan_cache_dir de hub/ (como pide la ficha) mas todo lo
    demas de HF_HOME salvo las carpetas ajenas (xet/ guarda los chunks, que ese escaneo no ve). Cuenta la cache ENTERA: si no se
    puede medir completa (mas de `max_ficheros`, un error de lectura o entradas corruptas) lanza CacheNoMedible, nunca un
    subtotal. Sin du sobre arboles grandes: el recorrido esta acotado."""
    total, visto = 0, 0
    hub = raiz + "/hub"
    if os.path.isdir(hub):
        try:
            from huggingface_hub import scan_cache_dir

            informe = scan_cache_dir(hub)
        except Exception as e:  # noqa: BLE001 - cualquier fallo de lectura impide garantizar la medida
            raise CacheNoMedible(f"no se pudo escanear {hub}: {type(e).__name__}: {e}") from e
        if informe.warnings:
            raise CacheNoMedible(f"{hub} tiene {len(informe.warnings)} entradas ilegibles o corruptas: medida incompleta")
        total += int(informe.size_on_disk)

    def sin_error(e):
        raise CacheNoMedible(f"no se pudo recorrer la cache de HF: {e}")

    if os.path.isdir(raiz):
        for nombre in sorted(os.listdir(raiz)):
            ruta = os.path.join(raiz, nombre)
            if nombre == "hub" or nombre in CACHE_AJENA:
                continue
            if os.path.isfile(ruta):
                visto += 1
                total += os.path.getsize(ruta)
                continue
            for r, _, nombres in os.walk(ruta, onerror=sin_error):
                for n in nombres:
                    visto += 1
                    if visto > max_ficheros:
                        raise CacheNoMedible(f"la cache de HF tiene mas de {max_ficheros} ficheros: no se puede medir completa")
                    try:
                        total += os.path.getsize(os.path.join(r, n))
                    except FileNotFoundError:
                        continue  # desaparecio durante el recorrido
                    except OSError as e:
                        raise CacheNoMedible(f"no se pudo medir {os.path.join(r, n)}: {e}") from e
    return total


def comprobar_tope_lotsa(bytes_subconjunto: int, bytes_lotsa_con_el_siguiente: int) -> None:
    """Antes de bajar un fichero de LOTSA: subconjunto (tamano declarado por el Hub) <= 2 GB y total de LOTSA <= 10 GB."""
    if bytes_subconjunto > LOTSA_SUBCONJUNTO_MAX:
        raise TopeLotsa(f"el subconjunto declara {bytes_subconjunto / 1e9:.2f} GB (> {LOTSA_SUBCONJUNTO_MAX / 1e9:.0f} GB)")
    if bytes_lotsa_con_el_siguiente > LOTSA_TOTAL_MAX:
        raise TopeLotsa(f"LOTSA llegaria a {bytes_lotsa_con_el_siguiente / 1e9:.2f} GB (> {LOTSA_TOTAL_MAX / 1e9:.0f} GB)")


# --- red -------------------------------------------------------------------------------------------------------------

def espera_reintento(intento: int, retry_after: float | None = None) -> float:
    """Espera exponencial 2, 4, 8... s; respeta Retry-After (acotado)."""
    base = float(2 ** (intento + 1))
    if retry_after is not None:
        base = max(base, float(retry_after))
    return min(base, ESPERA_MAX)


def parse_retry_after(valor: str | None, ahora: dt.datetime | None = None) -> float | None:
    """Retry-After en segundos: en segundos enteros o como fecha HTTP (las dos formas de la RFC 9110); None si no se entiende."""
    if not valor:
        return None
    try:
        return max(0.0, float(valor.strip()))
    except ValueError:
        pass
    try:
        t = email.utils.parsedate_to_datetime(valor.strip())
    except (TypeError, ValueError, IndexError):
        return None
    if t is None:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return max(0.0, (t - (ahora or dt.datetime.now(dt.timezone.utc))).total_seconds())


class Ritmo:
    """Como mucho una peticion por PAUSA_HOST segundos y host."""

    def __init__(self, pausa: float = PAUSA_HOST, reloj=time.monotonic, dormir=time.sleep):
        self.pausa, self.reloj, self.dormir, self.ultimo = pausa, reloj, dormir, {}

    def esperar(self, host: str) -> float:
        ahora = self.reloj()
        falta = self.ultimo.get(host, -1e18) + self.pausa - ahora
        if falta > 0:
            self.dormir(falta)
        self.ultimo[host] = self.reloj()
        return max(0.0, falta)


RITMO = Ritmo()
PETICIONES = []  # registro de peticiones (url inicial, estado) de esta ejecucion; nunca se guardan las URL firmadas de las redirecciones
MAX_SALTOS = 5  # redirecciones que se siguen dentro de un intento
REDIRECCIONES = (301, 302, 303, 307, 308)


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    """urllib sigue las redirecciones por su cuenta y sin pasar por el ritmo. Aqui no: devuelve el 3xx como HTTPError y http_get
    sigue el Location a mano, de modo que CADA salto espera el ritmo de SU host (p. ej. el Hub y su CDN)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_SinRedireccion)


def abrir_defecto(req, timeout: float = 60.0):
    return _OPENER.open(req, timeout=timeout)


class _Reintentable(Exception):
    """Fallo de un intento que merece otro (5xx, 408/429, conexion caida, respuesta truncada)."""

    def __init__(self, motivo: str, retry_after: float | None = None):
        super().__init__(motivo)
        self.motivo, self.retry_after = motivo, retry_after


def _longitud(hdr: dict) -> int | None:
    try:
        return int(hdr["content-length"])
    except (KeyError, ValueError):
        return None


def _un_intento(url: str, *, permitir: tuple, destino: str | None, timeout: float, cabeceras: dict | None, abrir,
                ritmo: "Ritmo") -> dict:
    """Un intento: la cadena de redirecciones hasta la respuesta final. Lanza _Reintentable (otro intento) o ErrorRed (no)."""
    parcial = (destino + ".part") if destino else None
    actual, saltos = url, 0
    while True:
        ritmo.esperar(urllib.parse.urlsplit(actual).netloc)
        cab = {"User-Agent": UA, "Accept": "*/*"}
        cab.update(cabeceras or {})
        previo = 0
        if parcial and os.path.isfile(parcial):
            previo = os.path.getsize(parcial)
            if previo:
                cab["Range"] = f"bytes={previo}-"
        try:
            with abrir(urllib.request.Request(actual, headers=cab), timeout=timeout) as r:
                status = getattr(r, "status", 200)
                hdr = {k.lower(): v for k, v in dict(r.headers).items()}
                leidos = 0
                if destino:
                    os.makedirs(os.path.dirname(destino), exist_ok=True)
                    modo = "ab" if (status == 206 and previo) else "wb"
                    with open(parcial, modo) as f:
                        for bloque in iter(lambda: r.read(1 << 20), b""):
                            f.write(bloque)
                            leidos += len(bloque)
                    cuerpo = b""
                else:
                    cuerpo = r.read()
                    leidos = len(cuerpo)
            esperado = _longitud(hdr)
            if esperado is not None and leidos < esperado:  # http.client no avisa de un cuerpo cortado: se reintenta (reanuda el .part)
                raise _Reintentable(f"respuesta truncada ({leidos} de {esperado} bytes)")
            if destino:
                os.replace(parcial, destino)
                n = os.path.getsize(destino)
            else:
                n = leidos
            return {"status": status, "cabeceras": hdr, "cuerpo": cuerpo, "bytes": n}
        except urllib.error.HTTPError as e:
            if e.code in REDIRECCIONES and e.headers is not None and e.headers.get("Location"):
                saltos += 1
                nuevo = urllib.parse.urljoin(actual, e.headers.get("Location"))
                e.close()
                if saltos > MAX_SALTOS:
                    PETICIONES.append((url, "REDIR"))
                    raise ErrorRed(f"{url}: mas de {MAX_SALTOS} redirecciones (no se reintenta)") from None
                if urllib.parse.urlsplit(url).scheme == "https" and urllib.parse.urlsplit(nuevo).scheme != "https":
                    PETICIONES.append((url, "REDIR"))
                    raise ErrorRed(f"{url}: redireccion a un destino que no es https (no se reintenta)") from None
                actual = nuevo
                continue
            if e.code in permitir:
                PETICIONES.append((url, e.code))
                cuerpo = e.read()
                if destino:  # la respuesta de error tambien es evidencia (p. ej. 404 de la API de licencias de GitHub)
                    os.makedirs(os.path.dirname(destino), exist_ok=True)
                    with open(destino, "wb") as f:
                        f.write(cuerpo)
                return {"status": e.code, "cabeceras": {k.lower(): v for k, v in dict(e.headers).items()},
                        "cuerpo": cuerpo, "bytes": len(cuerpo)}
            if e.code == 416 and destino and previo:  # el .part ya estaba completo
                os.replace(parcial, destino)
                return {"status": 200, "cabeceras": {}, "cuerpo": b"", "bytes": os.path.getsize(destino)}
            if e.code in (408, 429) or e.code >= 500:
                raise _Reintentable(f"HTTP {e.code}", parse_retry_after(e.headers.get("Retry-After") if e.headers else None)) from None
            PETICIONES.append((url, e.code))
            raise ErrorRed(f"{url}: HTTP {e.code} (no se reintenta)") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            raise _Reintentable(f"{type(e).__name__}: {e}") from None


def http_get(url: str, *, permitir: tuple = (), destino: str | None = None, timeout: float = 60.0,
             cabeceras: dict | None = None, abrir=abrir_defecto, ritmo: Ritmo | None = None,
             dormir=time.sleep) -> dict:
    """GET con UA del proyecto, ritmo por host, 3 reintentos con espera exponencial y Retry-After.

    Devuelve {status, cabeceras, cuerpo (bytes; vacio si destino), bytes}. Los estados de `permitir` (p. ej. 404) se
    devuelven en lugar de lanzar. Con `destino`, descarga a destino+'.part' (reanuda con Range) y renombra al terminar.
    Un 4xx distinto de 408/429 no se reintenta. Nunca sortea bloqueos: si el servidor rechaza, se lanza ErrorRed.
    Como mucho REINTENTOS + 1 = 4 intentos; un intento sigue las redirecciones (cada salto con el ritmo de su host) y un cuerpo
    mas corto que su Content-Length cuenta como fallo del intento. La misma politica sirve a Binance, a las evidencias de
    licencia y al Hub de Hugging Face."""
    ritmo = ritmo or RITMO
    ultimo_error, retry_after = "sin intentos", None
    for intento in range(REINTENTOS + 1):
        try:
            r = _un_intento(url, permitir=permitir, destino=destino, timeout=timeout, cabeceras=cabeceras, abrir=abrir, ritmo=ritmo)
            PETICIONES.append((url, r["status"]))
            return r
        except _Reintentable as e:
            ultimo_error, retry_after = e.motivo, e.retry_after
        if intento < REINTENTOS:
            dormir(espera_reintento(intento, retry_after))
    PETICIONES.append((url, "ERR"))
    raise ErrorRed(f"{url}: {ultimo_error} tras {REINTENTOS + 1} intentos")
