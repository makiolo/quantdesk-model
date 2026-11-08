# LAB-00-ENV-B: rueda quantdesk desde el commit fijo

Commit del motor: `69fdb39d0b67969dbdafa77f5da656511342f175` (2026-11-07 22:45 +0100, "docs(plans): criterio global de niveles, IA local (A17) y arenas"). Ese commit no tiene tags.

## Resultado

| Elemento | Valor |
|---|---|
| Rueda | `E:/quantdesk-lab/wheels/quantdesk-0.0.0-cp312-cp312-win_amd64.whl` |
| Tamaño | 22 998 941 bytes |
| SHA-256 de la rueda | `28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd` |
| Sumas | `E:/quantdesk-lab/wheels/SHA256SUMS`; `sha256sum -c SHA256SUMS` da OK |
| Versión | `0.0.0`, fijada en `pyproject.toml` (línea 14) |
| Duración del build | 3071 s (inicio 01:09:32, fin hacia las 02:00) |
| git archive | sha256 `9b13af2c7f40f02f69a037a23da5355faf4aafd51dde0455b0426c7c9067a924`; 6865 ficheros; el árbol extraído coincide con el archivo antes y después del build |

## Módulos y requisitos

El zip tiene 58 entradas: el paquete `quantdesk/` (45 entradas, Python puro), cinco binarios y los `dist-info`:

- `engine.cp312-win_amd64.pyd` (nanobind, `clients/python`).
- `findsl_py`, `market_py`, `data_py` y `strategy_py`: un `.pyd` cada uno (PyO3).
- `quantdesk-0.0.0.dist-info` (METADATA, WHEEL, RECORD).

Requires-Python `>=3.10`. Requires-Dist `pydantic>=2` y `jsonschema>=4.18`.

Ruta elegida: un único backend scikit-build-core, el del `pyproject.toml` raíz, que compila los cinco módulos en una sola rueda. No se usó un maturin por crate, para no duplicar módulos.

## Comandos

Build, desde `S:/Projects/quantdesk-model` (el motor sólo se lee):

```
D:/miniconda312/python.exe -X utf8 scripts/build_wheels.py --commit 69fdb39d0b67969dbdafa77f5da656511342f175
D:/miniconda312/python.exe -X utf8 scripts/build_wheels.py --selftest
```

La pasada registrada es el mismo `--commit` redirigido a `E:/quantdesk-lab/tmp/build-b/run2.log`, con `BUILD_EXIT=0`.

Pasos internos del script:

1. `git -c core.autocrlf=false --no-optional-locks -C S:/projects/quantdesk archive --format=tar` a `E:/quantdesk-lab/tmp/build-b/<commit>.tar`. Extracción en `E:/quantdesk-lab/build/<commit>/`, que debe estar vacío (si no, se para), y verificación fichero a fichero con detección de sobrantes.
2. Entorno MSVC: `vcvars64.bat` de VS 2022 BuildTools, fusionado con el entorno de lab. `git`, `vswhere` y `vcvars64` se lanzan con ese entorno sellado (TEMP/TMP/TMPDIR en E:), no con el heredado de C:.
3. `D:/miniconda312/python.exe -m pip wheel E:/quantdesk-lab/build/<commit> --no-deps --wheel-dir E:/quantdesk-lab/tmp/build-b/wheel-out --config-settings build-dir=E:/quantdesk-lab/build/<commit>/_skbuild`.
4. Nueva verificación del árbol (sin sobrantes salvo `_skbuild` y `target`), publicación en `E:/quantdesk-lab/wheels/` (sin sobrescribir), `SHA256SUMS` y comprobación: se relee el fichero y se recalcula el SHA-256 de cada rueda; si no coincide, se para.

Entorno de lab (`lab_env`):

- `TEMP`, `TMP` y `TMPDIR` = `E:/quantdesk-lab/tmp/build-b`.
- `PIP_CACHE_DIR` = `E:/quantdesk-lab/cache/pip`; `CARGO_HOME` = `E:/quantdesk-lab/cache/cargo`.
- `CARGO_TARGET_DIR` = `E:/quantdesk-lab/build/<commit>/target`.
- `RUSTUP_HOME` = `S:/Apps/Home/.rustup`; `RUSTUP_TOOLCHAIN` = `1.97.1-x86_64-pc-windows-msvc`.
- `CMAKE_GENERATOR` = `Ninja`.

Prueba de uso, en la venv desechable `E:/quantdesk-lab/tmp/build-b/wheelcheck`:

```
E:/quantdesk-lab/tmp/build-b/wheelcheck/Scripts/python.exe -m pip install E:/quantdesk-lab/wheels/quantdesk-0.0.0-cp312-cp312-win_amd64.whl
cd E:/quantdesk-lab/tmp/build-b/empty-cwd && E:/quantdesk-lab/tmp/build-b/wheelcheck/Scripts/python.exe -c "import quantdesk, data_py, market_py"
```

Resultado: los tres módulos importan desde `E:\quantdesk-lab\tmp\build-b\wheelcheck\Lib\site-packages\`. pip instaló además pydantic 2.14.3 y jsonschema 4.26.0.

## Herramientas

| Herramienta | Versión | Origen |
|---|---|---|
| Python | 3.12.3 (conda-forge) | `D:/miniconda312/python.exe` |
| pip | 24.2 | host; lanza `pip wheel` |
| scikit-build-core | 1.1.2 | entorno aislado de pip |
| Ninja | 1.13.2 | entorno aislado de pip (`pip-build-env/…/Scripts/ninja.exe`); el Ninja 1.4.0 del sandbox no se usó |
| CMake | 3.28.0-rc5 | `D:/CMake/bin/cmake.exe` |
| rustc | 1.97.1 (8bab26f4f 2026-07-14) | `S:/Apps/Home/.rustup/toolchains/1.97.1-x86_64-pc-windows-msvc` |
| cargo | 1.97.1 (c980f4866 2026-06-30) | misma toolchain |
| rustfmt / clippy | 1.9.0-stable / 0.1.97 | misma toolchain |
| MSVC | toolset 14.44.35207 (cl 19.44.35226) | VS 2022 BuildTools 17.14.37216.2 |
| nanobind | v3.0.1 | FetchContent, `clients/python/CMakeLists.txt` |
| Corrosion | v0.6.1 | FetchContent, `CMakeLists.txt` raíz |

RUSTUP_HOME usado: `S:/Apps/Home/.rustup`, que sólo tenía `settings.toml` y la toolchain 1.97.1, ya completa. No se tocó `C:/Users/makiolo/.rustup`.

## Desviaciones y advertencias

- `core.autocrlf=false` en `git archive`: el autocrlf del sistema habría cambiado 5024 ficheros.
- `RUSTUP_TOOLCHAIN` añadido: sin él rustup usa `stable`, el default de `settings.toml`, que no está instalada en ese RUSTUP_HOME.
- `rustup toolchain install` devolvió código 1: no encontró rustup en el CARGO_HOME de E: ni en el global `D:\dev\cargo_root`. La toolchain ya estaba completa y no se descargó nada.
- TMPDIR: en la pasada registrada, los temporales de pip (`pip-build-env`, `pip-wheel`, `tmpmi*`) se crearon en `C:\Users\makiolo\AppData\Local\Temp`, porque Git Bash fija `TMPDIR=/tmp` y Python lo consulta antes que TEMP. Pip los borró al terminar: no quedó ningún resto. El script se corrigió después (`TMPDIR` en `lab_env` y una aserción en `--selftest`). La pasada usó la versión anterior y no se recompiló. El cambio sólo afecta a dónde van los temporales.
- Sin delvewheel: la rueda depende de las runtimes MSVC (MSVCP140, VCRUNTIME140) del sistema. No se ha probado en otra máquina.
- Red durante el build: pip (dependencias de build desde PyPI), FetchContent de nanobind y Corrosion desde GitHub, y en la venv pydantic y jsonschema desde PyPI, con caché en E:.
- Espacio: C: libre 9.58 GiB al empezar y 3.53 GiB al terminar. La bajada no está atribuida: las salidas del build van a E:, y los temporales de pip que estaban en C: se borraron. E: tiene 315 GiB libres.
- Tamaño del build no medido: `timeout 20 du -sh E:/quantdesk-lab/build/69fdb39d0b67969dbdafa77f5da656511342f175` cortó a los 20 s.
- Re-ejecutar el mismo commit exige vaciar `E:/quantdesk-lab/build/<commit>/` a mano: el script se para si ese directorio tiene contenido y no borra nada.

## Motor (sólo lectura)

Órdenes sobre `S:/projects/quantdesk`: `archive`, `rev-parse`, `cat-file`, `log`, `tag` y `status --short` con `--no-optional-locks`. No se escribió nada. El `git status` del motor cambió durante la sesión por trabajo de otra sesión. La diferencia respecto a la foto de las 01:06 está en `E:/quantdesk-lab/tmp/build-b/status-diff.txt`.

## Revisión independiente (correcciones sin compilación real)

Tras la revisión independiente de LAB-00-ENV (Codex terra) se corrigieron tres puntos de `scripts/build_wheels.py`, sin recompilar la rueda: (1) git y vswhere se lanzan con el entorno sellado de lab; (2) la extracción exige un directorio vacío y la verificación del árbol detecta ficheros sobrantes, salvo bajo `_skbuild` y `target`; (3) SHA256SUMS se relee y se recalcula el SHA-256 de cada rueda; el selftest cubre un hash que no coincide y una rueda sin entrada.

Ejercitado: `--selftest` con `.venv/Scripts/python` (OK); `verify_tree` sobre el árbol ya construido (6865 ficheros, sin malos ni sobrantes) y `sums_check` sobre `E:/quantdesk-lab/wheels/` (sin diferencias).

No ejercitado: una compilación real con estas correcciones. Se hará al subir de commit del motor; hasta entonces el camino completo del script (archive, build, publicación) no se ha probado con esta versión.
