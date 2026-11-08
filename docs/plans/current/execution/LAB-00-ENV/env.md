# LAB-00-ENV-A: entorno Python del laboratorio (fase 1)

Estado: fase 1 completa. Falta la rueda de `quantdesk` (fase 2): la comprobación HMM de §2.1 está **saltada explícitamente**, no ejecutada.

## Intérprete

- Base: `D:/miniconda312/python.exe`, Python 3.12.3 (conda-forge). `py -3.12` no existe en esta máquina.
- Venv del laboratorio: `S:/Projects/quantdesk-model/.venv`, creado por `scripts/setup_env.py`.
- Resolución del lock: venv de herramientas en `E:/quantdesk-lab/tmp/env-a/tools` (pip-tools 7.6.2). Sólo sirve para generar el lock; no forma parte del entorno.

## Método del lock

- `requirements.in`: dependencias directas. Versiones fijadas en el índice el 2026-11-08: torch `2.15.0+cpu`, pyarrow 26.0.1, ml_dtypes 0.6.0, arch 8.0.0, MetaTrader5 5.0.6231, chronos-forecasting 2.3.2 (resuelto a estas versiones).
- `requirements.lock`: generado con `pip-compile --generate-hashes --allow-unsafe` desde `requirements.in`. Incluye todas las transitivas con `==` y `--hash` (989 hashes).
- `--allow-unsafe` hace falta para que `setuptools==84.2.1` (requerido por torch) quede fijado. Sin él, la primera instalación falló con `--require-hashes`: «setuptools>=77.0.3 ... must be pinned». Fijado en el lock tras ese fallo.
- `pip` no se fija en el lock: el pip del venv es el que trae `venv`/ensurepip (24.0). `pip freeze` tampoco lo muestra.
- torch CPU: `--extra-index-url https://download.pytorch.org/whl/cpu` declarado dentro del lock. Verificado: `torch 2.15.0+cpu`, `torch.version.cuda = None`.
- Instalación: `setup_env.py` ejecuta `pip install --require-hashes -r requirements.lock`.
- Resolución sin conflictos. chronos-forecasting 2.3.2 trae transformers 5.22.2, accelerate 1.15.0, numpy 2.5.4 y pandas 3.1.1; no hubo que cambiar versiones de torch por chronos.
- Rueda local de quantdesk: pendiente. Se añadirá en fase 2 como `file:///E:/quantdesk-lab/wheels/<fichero>.whl` con comentario de commit y SHA-256.

## Mecanismo de cachés (escrito en el venv)

`scripts/setup_env.py` define `LAB_ENV`. Se aplica de dos formas:

1. `<venv>/pip.ini`: `[global] cache-dir = E:/quantdesk-lab/cache/pip`, `disable-pip-version-check = true`. Lo lee pip aunque el venv no esté activado.
2. `<venv>/Lib/site-packages/sitecustomize.py`: asigna (no `setdefault`) las variables y crea los directorios si faltan. Cualquier proceso del venv las hereda, activado o no.
3. `setup_env.py` pasa las mismas variables con `env=` a cada subproceso, incluido el primer `python -m venv` y el primer pip.

Variables:

| Variable | Valor |
|---|---|
| `HF_HOME` | `E:/quantdesk-lab/cache/hf` |
| `PIP_CACHE_DIR` | `E:/quantdesk-lab/cache/pip` |
| `TORCH_HOME` | `E:/quantdesk-lab/cache/hf/torch` |
| `XDG_CACHE_HOME` | `E:/quantdesk-lab/cache/hf/xdg` |
| `TMPDIR`, `TEMP`, `TMP` | `E:/quantdesk-lab/tmp/env-a` |

Decisiones:

- `TORCH_HOME` y `XDG_CACHE_HOME` van bajo `cache/hf`: la ficha no autoriza `cache/torch` ni `cache/xdg`. Autorizado por el coordinador (2026-11-08).
- `TMPDIR` se añadió tras detectar en la prueba de humo que `tempfile.gettempdir()` devolvía `C:\...\Temp`: `tempfile` lee `TMPDIR` antes que `TEMP`, y en esta máquina `TMPDIR` apunta a C:. Con `TMPDIR` asignado, `gettempdir()` devuelve `E:\quantdesk-lab\tmp\env-a`.
- Las variables de usuario/sistema de Windows no se tocan.

## Disco

- `df -h /c` al inicio: 3.0G libres (99 %).
- Durante la compilación del lock bajó a 68M y luego a 89M por consumo ajeno (C: Temp con 12G y `cargo.exe` de otras sesiones). Detenido por la guarda de 2 GB; el usuario liberó C: y el coordinador desbloqueó la tarea.
- `df -h /c` tras la instalación: 3.6G libres (99 %). Sobre el mínimo de 2 GB.
- Caché de pip de usuario (`C:/Users/makiolo/AppData/Local/pip/cache`): 1.3G al inicio; 1.5G en la última lectura antes de la compilación. No se volvió a medir: `du` superó los 20 s y no devolvió salida. El aumento aparece tras lecturas de otras sesiones. Mis llamadas de pip usaron `PIP_CACHE_DIR` en E:, y la caché de E: pasó a 264M (`cache/pip`). **Pendiente de revisar.**
- Tamaño del `.venv`: no medido (`du` superó los 20 s). Ver `E:/quantdesk-lab/tmp/env-a/freeze_venv.txt` (53 paquetes).

## Scripts

- `scripts/setup_env.py`: crea el venv, escribe la configuración de cachés e instala el lock. `--selftest` prueba la lógica pura sin crear venvs.
- `scripts/smoke_env.py`: imports, torch CPU, rutas de cachés y temporales, `pip cache dir`, `pip.ini`. Motor quantdesk: saltado en fase 1 con mensaje explícito. `--require-engine` lo hace obligatorio (fase 2).
- `scripts/run_selftests.py`: ejecuta `--selftest` de cada `scripts/*.py` que lo soporte, con el Python del venv.

## Salida de las comprobaciones (fase 1)

Aceptación 1, `.venv/Scripts/python -X utf8 scripts/smoke_env.py --selftest`: exit 0.

```
OK  import pyarrow 26.0.1 / ml_dtypes 0.6.0 / arch 8.0.0 / MetaTrader5 5.0.6231 / torch 2.15.0+cpu / chronos-forecasting 2.3.2
OK  torch CPU: torch.__version__=2.15.0+cpu torch.version.cuda=None
OK  env HF_HOME, PIP_CACHE_DIR, TORCH_HOME, XDG_CACHE_HOME, TMPDIR, TEMP, TMP bajo E:/quantdesk-lab
OK  tempfile.gettempdir: E:\quantdesk-lab\tmp\env-a
OK  pip cache dir: e:\quantdesk-lab\cache\pip
OK  pip.ini del venv: S:\Projects\quantdesk-model\.venv\pip.ini
SALTADO  motor quantdesk: rueda pendiente: comprobacion HMM de 2.1 NO ejecutada (fase 1)
smoke_env: OK (17 comprobaciones; 1 SALTADAS)
```

Aceptación 2, `.venv/Scripts/python -X utf8 scripts/run_selftests.py`: exit 0.

```
OK     scripts/build_wheels.py: selftest OK          (de LAB-00-ENV-B; no tocado)
OK     scripts/inventario_options_chain.py: selftest ok
OK     scripts/setup_env.py: setup_env selftest ok
OK     scripts/smoke_env.py: smoke_env: OK (17 comprobaciones; 1 SALTADAS)
run_selftests: 4 OK, 0 FALLO
```

Aceptación 3, `.venv/Scripts/python -c "import torch; print(torch.__version__, torch.version.cuda)"`: `2.15.0+cpu None`.

Aceptación 4: `df -h /c` ≥ 2 GB (ver Disco). Caché de pip de usuario: ver Disco (pendiente).

Invariante, reproducción en venv limpio (`setup_env.py --venv E:/quantdesk-lab/tmp/env-a/lockcheck`): exit 0. `pip freeze` del `.venv` y del lockcheck: idénticos (53 líneas, `diff` vacío).

## Excluido / pendiente

- Motor quantdesk y comprobación HMM de §2.1: fase 2.
- Rueda de quantdesk, `data-py` y `market-py`: pendiente de LAB-00-ENV-B (`E:/quantdesk-lab/wheels/`).
- Caché de pip de usuario: medición final pendiente (ver Disco).
- Hashes de la rueda local: se generan en fase 2.
