# LAB-00-ENV-A: entorno Python del laboratorio

Estado: fase 1 y fase 2 completas. Rueda de quantdesk (commit 69fdb39d0b67969dbdafa77f5da656511342f175, compilada por LAB-00-ENV-B) instalada y fijada en el lock. La comprobación HMM de §2.1 pasa en el `.venv`.

## Intérprete

- Base: `D:/miniconda312/python.exe`, Python 3.12.3 (conda-forge). `py -3.12` no existe en esta máquina.
- Venv del laboratorio: `S:/Projects/quantdesk-model/.venv`, creado por `scripts/setup_env.py`.
- Resolución del lock: venv de herramientas en `E:/quantdesk-lab/tmp/env-a/tools` (pip-tools 7.6.2). Sólo sirve para generar el lock; no forma parte del entorno.

## Método del lock

- `requirements.in`: dependencias directas. Versiones fijadas en el índice el 2026-11-08: torch `2.15.0+cpu`, pyarrow 26.0.1, ml_dtypes 0.6.0, arch 8.0.0, MetaTrader5 5.0.6231, chronos-forecasting 2.3.2, y la rueda local de quantdesk.
- `requirements.lock`: generado con `pip-compile --generate-hashes --allow-unsafe` desde `requirements.in`. Incluye todas las transitivas con `==` y `--hash`.
- `--allow-unsafe` hace falta para que `setuptools==84.2.1` (requerido por torch) quede fijado. Sin él, la primera instalación falló con `--require-hashes`: «setuptools>=77.0.3 ... must be pinned». Fijado en el lock tras ese fallo.
- `pip` no se fija en el lock: el pip del venv es el que trae `venv`/ensurepip (24.0). `pip freeze` tampoco lo muestra.
- torch CPU: `--extra-index-url https://download.pytorch.org/whl/cpu` declarado dentro del lock. Verificado: `torch 2.15.0+cpu`, `torch.version.cuda = None`.
- Instalación: `setup_env.py` ejecuta `pip install --require-hashes -r requirements.lock`.
- Resolución sin conflictos. chronos-forecasting 2.3.2 trae transformers 5.22.2, accelerate 1.15.0, numpy 2.5.4 y pandas 3.1.1; no hubo que cambiar versiones de torch por chronos.

### Rueda local de quantdesk (fase 2)

- Fuente de verdad: `E:/quantdesk-lab/wheels/SHA256SUMS`. Verificada con `sha256sum -c`: `quantdesk-0.0.0-cp312-cp312-win_amd64.whl: OK`.
- sha256: `28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd`. Commit del código: `69fdb39d0b67969dbdafa77f5da656511342f175` (LAB-00-ENV-B, a581355).
- Contenido (lectura del zip, sin ejecutar nada): módulos `engine`, `data_py`, `market_py`, `findsl_py`, `strategy_py` y el paquete Python `quantdesk`. Dependencias declaradas: `pydantic>=2`, `jsonschema>=4.18`.
- En `requirements.in`: `quantdesk @ file:///E:/quantdesk-lab/wheels/quantdesk-0.0.0-cp312-cp312-win_amd64.whl` con comentario de commit y sha256.
- En `requirements.lock`: pip-compile emitió la línea `quantdesk @ file:///...` con `--hash=sha256:28c1ed...`, y fijó `pydantic==2.14.3`, `jsonschema==4.26.0` y sus transitivas con hash.
- El comentario con el commit en el lock se añadió **a mano** tras pip-compile, que no lo emite. Si se regenera el lock, hay que volver a añadirlo.

## Mecanismo de cachés (escrito en el venv)

`scripts/setup_env.py` define `LAB_ENV`. Se aplica de tres formas:

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
- `df -h /c` tras la instalación de fase 1: 3.6G libres (99 %). Tras la fase 2: 3.2G libres (99 %). Sobre el mínimo de 2 GB en ambos casos.
- Caché de pip de usuario (`C:/Users/makiolo/AppData/Local/pip/cache`): 1.3G al inicio. Según la medición de la raíz, entre 00:35 y 00:53 hora local entraron unos 230 MB en esa caché por procesos ajenos a este laboratorio. Desde la reanudación no hubo cambios atribuibles a LAB-00-ENV-A; no se vuelve a medir. Mis llamadas de pip usan `PIP_CACHE_DIR` en E:, y la caché de E: (`cache/pip`) quedó en 264M.
- Tamaño del `.venv`: no medido (`du` superó los 20 s). Freeze final: 63 líneas (`E:/quantdesk-lab/tmp/env-a/freeze_venv_f2.txt`).

## Scripts

- `scripts/setup_env.py`: crea el venv, escribe la configuración de cachés e instala el lock. `--selftest` prueba la lógica pura sin crear venvs.
- `scripts/smoke_env.py`: imports del motor y de las 5 extensiones, torch CPU, rutas de cachés y temporales, `pip cache dir`, `pip.ini`, rueda en el lock (sha256 contra SHA256SUMS) y comprobación HMM de §2.1. `--require-engine` exige el motor (fase 2).
- `scripts/run_selftests.py`: ejecuta `--selftest` de cada `scripts/*.py` que lo soporte, con el Python del venv.

### Comprobación HMM de §2.1 (scripts/smoke_env.py)

- API leída con `git -C S:/projects/quantdesk show 69fdb39d:<ruta>` (nunca se ejecutó el venv de quantdesk): `clients/python/src/quantdesk/{engine.py,calibration.py,model.py}`.
- Serie sintética: `Engine.simulate` de un `Hmm` de 2 estados `GbmP` (semilla 42), 400 días, `ObservedSeries(observable="SYN.SPOT")`.
- Calibración: `Engine.calibrate(template, series, HmmCalibrationOptions(seed=7))`, plantilla `Hmm` de 2 estados.
- Caminos: 200 streams `Engine.open_stream(res, 42+i, policy="from_calibration_end").advance_many(dts)` con 20 pasos de 1/252 años.
- Verificaciones: forma `(200, 20, 1)`, valores finitos y positivos (GBM_P), determinismo (misma semilla, mismos valores).

## Salida de las comprobaciones

### Fase 1

Aceptación 1, `.venv/Scripts/python -X utf8 scripts/smoke_env.py --selftest`: exit 0 (17 OK, 1 SALTADO).

Aceptación 2, `.venv/Scripts/python -X utf8 scripts/run_selftests.py`: exit 0 (4 OK). `build_wheels.py` es de LAB-00-ENV-B; no se tocó.

Aceptación 3, `.venv/Scripts/python -c "import torch; print(torch.__version__, torch.version.cuda)"`: `2.15.0+cpu None`.

Invariante de reproducción en venv limpio: exit 0; `diff` de `pip freeze` vacío (53 líneas).

### Fase 2

Aceptación 6, `.venv/Scripts/python -X utf8 scripts/smoke_env.py --selftest --require-engine`: exit 0, 20 OK, 0 SALTADOS.

```
OK  import motor: quantdesk 0.0.0 (commit 69fdb39d0b67969dbdafa77f5da656511342f175); quantdesk, data_py, market_py, findsl_py, strategy_py
OK  rueda en requirements.lock: sha256 28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd (commit 69fdb39d0b67969dbdafa77f5da656511342f175)
OK  HMM calibrate + open_stream: serie 400 dias; 200 caminos x 20 dias; forma (200, 20, 1); finitos; determinista
smoke_env: OK (20 comprobaciones; 0 SALTADAS)
```

`run_selftests.py` tras fase 2: exit 0 (4 OK; smoke_env con el motor y la comprobación HMM).

Aceptación 7, reproducción en `E:/quantdesk-lab/tmp/env-a/lockcheck` (borrado y recreado desde cero con `setup_env.py --venv`): exit 0. `diff` de `pip freeze` del `.venv` y del lockcheck: vacío (63 líneas, incluida `quantdesk @ file:///...#sha256=28c1ed...`).

## Excluido / pendiente

- Hashes de la rueda local: cubiertos por el lock (`--require-hashes`) y verificados en la reproducción.
- Rueda de `data-py` y `market-py`: no aplica; están dentro de la rueda única de quantdesk (módulos `data_py` y `market_py`).
- Caché de pip de usuario: sin remedición; explicación en Disco.
- Comentario de commit en el lock: manual (ver Rueda local).
