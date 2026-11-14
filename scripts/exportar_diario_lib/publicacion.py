"""Confirmacion durable y reconciliacion persistente de un mismo sobre de estado.

El manifiesto y el sobre son inmutables. El registro lateral conserva la incertidumbre
antes de transmitir y permite recuperar el mismo batch_id tras perder una respuesta.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import uuid

from descarga_lago import sha256_de
from . import politica as P

STATUS = "/topics/ops.export.status/publish"


class SinConfirmacionDurable(RuntimeError):
    def __init__(self, registro):
        self.registro = registro
        super().__init__(registro["detail"])


def raices(a):
    return {"desktop": str(Path(a.raiz_desktop).resolve()), "motor": str(Path(a.raiz_datasets).resolve())}


def ruta_registro(a, digest):
    return Path(a.runs) / f"s{a.sesion.replace('-', '')}_r{a.revision or 0}_{digest}.publicacion.json"


def crear_registro(a, env, sobre):
    digest = sobre["obj"]["manifest_sha256"]
    path = ruta_registro(a, digest)
    reg = {"schema": "ti-02-diario.publicacion/v1", "session": a.sesion, "revision": a.revision,
           "env": env, "raices": raices(a), "manifest_sha256": digest, "batch_id": sobre["batch_id"],
           "estado": "preparada", "intentos": 0, "envios_http": 0, "eventos": []}
    if path.exists():
        previo = json.loads(path.read_text(encoding="utf-8"))
        if any(previo.get(k) != reg[k] for k in ("schema", "session", "revision", "env", "manifest_sha256", "batch_id")):
            raise ValueError("registro de publicacion inconsistente")
        if previo["estado"] == "incierta" and previo["raices"] != reg["raices"]:
            raise ValueError("la publicacion pendiente corresponde a otras raices")
        reg.update({k: previo[k] for k in ("estado", "intentos", "envios_http", "eventos")})
    return path, reg


def escribir_registro(path, reg, token):
    from .nucleo import canon, seguro_json
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(canon(json.loads(seguro_json(reg, token))))
    os.replace(tmp, path)


def publicar(cli, sobre, path, reg, token):
    from .nucleo import seguro

    aceptada_o_incierta = reg["estado"] in ("incierta", "confirmada")
    ultimo = "sin confirmacion durable"
    for _ in range(P.INTENTOS_PUBLICACION):
        reg["intentos"] += 1
        reg["estado"] = "incierta"
        reg["eventos"].append({"estado": "incierta", "intento": reg["intentos"]})
        # Se persiste antes de transmitir: un cierre del proceso tambien es recuperable.
        escribir_registro(path, reg, token)
        peticiones = []
        try:
            respuesta = cli.post(STATUS, {"wait": "durable"}, sobre, peticiones)
            aceptada_o_incierta = True
            reg["duplicado"] = respuesta.get("duplicate") is True
            reg["durable"] = respuesta.get("durable") is True
            if reg["durable"] and respuesta.get("batch_id", sobre["batch_id"]) == sobre["batch_id"]:
                reg["estado"] = "confirmada"
                reg["detail"] = "confirmacion durable recibida"
                reg["eventos"].append({"estado": "confirmada", "intento": reg["intentos"]})
                return reg
            ultimo = "qn acepta el sobre sin confirmacion durable"
        except Exception as e:
            aceptada_o_incierta |= cli.publicacion_incierta
            ultimo = "sin confirmacion durable: " + seguro(e, token)
        finally:
            reg["envios_http"] += sum(p.get("intentos", 1) for p in peticiones)
            escribir_registro(path, reg, token)
    reg["estado"] = "incierta" if aceptada_o_incierta else "no_enviada"
    reg["detail"] = seguro(ultimo, token)[:500]
    reg["eventos"].append({"estado": reg["estado"], "intento": reg["intentos"]})
    escribir_registro(path, reg, token)
    raise SinConfirmacionDurable(reg)


def detalle_manifiesto(path, reg):
    return {"estado": reg["estado"], "registro": path.name, "manifest_sha256_objetivo": reg["manifest_sha256"],
            "batch_id": reg["batch_id"], "intentos": reg["intentos"],
            "productos_conservados": reg["estado"] in ("incierta", "confirmada")}


def cargar_pendiente(a, env):
    """Recupera el sobre original y verifica los productos antes de repetir un ok."""
    from .nucleo import sha

    prefix = f"s{a.sesion.replace('-', '')}_r{a.revision or 0}_"
    for path in sorted(Path(a.runs).glob(prefix + "*.publicacion.json")):
        reg = json.loads(path.read_text(encoding="utf-8"))
        if reg["estado"] != "incierta":
            continue
        if reg["session"] != a.sesion or reg["revision"] != a.revision or reg["env"] != env or reg["raices"] != raices(a):
            raise ValueError("la publicacion pendiente no coincide con sesion, entorno y raices")
        digest = reg["manifest_sha256"]
        if not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest):
            raise ValueError("hash de publicacion pendiente invalido")
        mp = Path(a.runs) / f"s{a.sesion.replace('-', '')}_{digest}.integridad.json"
        raw = mp.read_bytes()
        if sha(raw) != digest:
            raise ValueError("el manifiesto pendiente no verifica su SHA-256")
        m = json.loads(raw)
        sobre = json.loads((Path(a.runs) / f"{digest}.publish.json").read_text(encoding="utf-8"))
        esperado = str(uuid.uuid5(uuid.NAMESPACE_URL, f"ti02-diario|{a.sesion}|{digest}"))
        obj = sobre["obj"]
        if (sobre["tags"] != {"job": "ti02-diario"} or sobre["batch_id"] != esperado or reg["batch_id"] != esperado
                or obj["manifest_sha256"] != digest or obj["session"] != a.sesion or obj["status"] != m["status"]
                or obj["cut_head_cycle"] != m["cut_head_cycle"]):
            raise ValueError("el sobre pendiente no corresponde a su manifiesto")
        permitidos = {"desktop": {"ohlcv_daily.parquet", "index.json"},
                      "motor": {"diario_ohlcv_1d.parquet", "manifest.json"}}
        # Solo un ok con productos necesita verificar datos antes de repetirlo.
        # Un error de escritura puede enumerar temporales que ya se retiraron.
        for entry in (m["ficheros"] if m["status"] == "ok" else []):
            producto, rel = entry["producto"], entry["ruta"]
            root = Path(reg["raices"][producto]).resolve()
            file = (root / m["destinos"][producto] / rel).resolve()
            if rel not in permitidos[producto] or not file.is_relative_to(root) or sha256_de(str(file)) != entry["sha256"]:
                raise ValueError("los productos pendientes no verifican sus hashes")
        return path, reg, sobre, m
    return None
