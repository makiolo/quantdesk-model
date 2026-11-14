"""TI-02-DIARIO: --ejecutar sin argumentos obligatorios; --selftest solo con qn falso local.

Python 3.12 del .venv. QN_URLS: bases separadas por comas; failover ante conexion/5xx.
QN_TOKEN: entorno o --env-file privado. Concesiones: sub:market.ohlcv.v2 + pub:ops.export.status.
Nunca usa fresh=true ni topics adicionales. No registra la tarea de Windows.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

from exportar_diario_lib.politica import DESDE


def main(argv=None, entorno=None):
    ap = argparse.ArgumentParser(description=__doc__)
    accion = ap.add_mutually_exclusive_group(required=True)
    accion.add_argument("--ejecutar", action="store_true")
    accion.add_argument("--selftest", action="store_true")
    ap.add_argument("--sesion", default=(datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat())
    ap.add_argument("--desde", default=DESDE, help="primer dia incluido; politica versionada")
    ap.add_argument("--revision", type=int, help="revision identificada; no sustituye la publicacion original")
    ap.add_argument("--raiz-desktop", default=str(Path(os.environ.get("USERPROFILE", str(Path.home()))) / "EngineQuantDesktop/data"))
    ap.add_argument("--raiz-datasets", default="E:/quantdesk-lab/datasets/TI-02-DIARIO")
    ap.add_argument("--runs", default="E:/quantdesk-lab/runs/TI-02-DIARIO")
    ap.add_argument("--env-file", default="E:/quantdesk-lab/secrets/ti02-diario.env")
    a = ap.parse_args(argv)
    if a.selftest:
        from exportar_diario_lib.selftests import correr
        correr()
        return 0
    env = os.environ if entorno is None else entorno
    try:
        sesion, desde = date.fromisoformat(a.sesion), date.fromisoformat(a.desde)
        if a.sesion != sesion.isoformat() or a.desde != desde.isoformat() or desde > sesion:
            raise ValueError("--sesion/--desde deben ser AAAA-MM-DD y desde <= sesion")
        if a.revision is not None and a.revision < 1:
            raise ValueError("--revision debe ser >= 1")
        token = env.get("QN_TOKEN", "").strip()
        if not token:
            p = Path(a.env_file)
            if p.is_file():
                for linea in p.read_text(encoding="utf-8-sig").splitlines():
                    key, sep, value = linea.strip().partition("=")
                    if sep and key.strip() == "QN_TOKEN":
                        token = value.strip().strip("\"'")
        if not token:
            raise ValueError("falta QN_TOKEN en entorno y --env-file privado")
        bases = env.get("QN_URLS", "").strip()
        if not bases:
            raise ValueError("falta QN_URLS en el entorno")
        if token in bases:
            raise ValueError("QN_URLS no puede contener la credencial")
        for base in bases.split(","):
            u = urlsplit(base.strip())
            if u.scheme not in ("http", "https") or not u.hostname or u.username or u.password or u.query or u.fragment:
                raise ValueError("QN_URLS debe contener bases HTTP sin credenciales ni parametros")
    except (ValueError, OSError):
        # Mensaje fijo por categoria, nunca contenido del fichero ni errores con valores remotos.
        print("exportar_diario: uso incorrecto: comprueba fechas/revision y QN_URLS; falta QN_TOKEN si no esta en entorno "
              "ni en --env-file privado", file=sys.stderr)
        return 2
    from exportar_diario_lib.nucleo import BloqueoOcupado, bloqueo, exportar
    try:
        with bloqueo(Path(a.runs) / f"s{sesion:%Y%m%d}.lock"):
            return exportar(a, bases, token, env.get("QN_ENV", "main"))
    except BloqueoOcupado:
        return exportar(a, bases, token, env.get("QN_ENV", "main"),
                        error_previo="otro exportador tiene el bloqueo de la sesion")
    except (OSError, ValueError):
        print("exportar_diario: error al bloquear o registrar la sesion", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
