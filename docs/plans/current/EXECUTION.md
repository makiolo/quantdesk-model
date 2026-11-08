# EXECUTION — SPRINT-01 de quantdesk-model

Registro de la raíz (LAUNCH §5, §8). Una fila por intento delegado y por cierre; las cifras de cuota son las de
`claude-or quota --weekly` en el momento indicado.

## Arranque de la raíz (2026-11-08)

- Raíz: Claude Opus 5.5 (`claude-opus-5-5`), suscripción. Intérprete de las skills: `S:/projects/quantdesk/venv/Scripts/python.exe`
  (el alias `python` de WindowsApps sigue dando «Permission denied»; no se instala nada en ese venv).
- `deps.py --repo . --sprint SPRINT-01`: **LISTO**, 0 dependencias de entrada.
- Cuota semanal (fuente api): Claude 40 % con el 71,1 % de la ventana (reinicio 2026-11-10 00:00 UTC); Codex 36 % con
  el 52,9 % (reinicio 2026-11-11 06:41 UTC); agy 0 %. `route --level 5` sugiere agy, pero el LAUNCH §2 fija el orden
  Claude → Codex y manda sobre la herramienta.
- Disco: C: 3,2 GB libres (umbral de parada 2 GB); E: 321 GB; S: 93 GB.
- **GAP-03 (puerta 4):** commit de `quantdesk` para las ruedas = `69fdb39d0b67969dbdafa77f5da656511342f175` (HEAD al
  empezar LAB-00-ENV; SPRINT.md citaba `57f9262c` como el de la planificación). Su árbol tenía cambios sin commitear sólo
  en `docs/`, que `git archive` no incluye.

## Ola 1

Cuota antes de la ola: la del arranque.

| Tarea / entrega | Nivel | Rol | Modelo / esfuerzo | Inicio (UTC) | Fin | Resultado | Commit | Nota |
|---|---|---|---|---|---|---|---|---|
| LAB-00-ENV (ficha) | — | revisión A2 | Claude Haiku 5.5 high (sólo lectura) | 2026-11-07 23:30 | 23:35 | 8 dudas, resueltas en las fichas | — | base corregida a `cd471fa`; TEMP/TMP asignados; sin ejecutar el venv de quantdesk; `--no-optional-locks`; temporales separados |
| LAB-00-ENV-A fase 1 | L4 | autor | Claude Haiku 5.5 high | 2026-11-07 23:38 | | en curso | | intento BDD 6 |
| LAB-00-ENV-B | L5 | autor | Claude Haiku 5.5 max | 2026-11-07 23:38 | | en curso | | intento BDD 7 |

Decisiones de la raíz (A12):

- GAP-03: la rueda única `scikit-build-core` del commit `69fdb39d` (incluye `data_py`, `market_py`, `findsl_py`,
  `strategy_py`) cumple «ruedas propias desde un commit fijo, compiladas fuera de quantdesk»; maturin por crate sólo si
  faltan módulos. Fuente de verdad de las ruedas: `E:/quantdesk-lab/wheels/SHA256SUMS`.
- `py -3.12` no existe: el `.venv` se crea con `D:/miniconda312/python.exe` (3.12.3, el mismo base que el venv de
  quantdesk), sin instalar nada en él.
- Hallazgo: el repo **sí tiene remoto** `origin` (`git@github.com:makiolo/quantdesk-model.git`), al contrario de
  SPRINT_PROJECT §2. **Resuelto (usuario, 2026-11-08):** el remoto es correcto y no se hace push; SPRINT_PROJECT §1–§2 y
  LAUNCH §4 corregidos.
- TI-01-INV (extensión del script) espera a que LAB-00-ENV-A entregue la fase 1: A ejecuta el `--selftest` de
  `scripts/inventario_options_chain.py` y no se edita a la vez.

Incidente de la raíz (2026-11-07 23:40, A9): un `cat >> … <<'EOF'` con backticks hizo que el Bash de la herramienta
ejecutara los fragmentos entre backticks (todos «command not found» salvo `D:/miniconda312/python.exe`, abierto en
interactivo y matado con TaskStop; nada escrito ni instalado). Causa: el Bash de Claude evalúa el heredoc. Control: la
raíz escribe siempre con Write y añade con script (regla ya escrita en LAUNCH §4 y en `delegation.md`).

**Bloqueo de disco (2026-11-08 00:50 UTC+1).** C: bajó de 3,0 GB a 68–333 MB libres durante la ola. A
(`pip-compile`: `OSError 28`) y B (guarda de disco antes de `git archive`) pararon como manda LAUNCH §4. No es
consumo del laboratorio: A y B escribían en E:, B no llegó a compilar y rustup no instaló nada. En ese momento
corrían `cargo test` de otra sesión sobre `S:\projects\quantdesk\rust\target` y pytest de otro proyecto;
`%LOCALAPPDATA%\Temp` ocupaba 12 GB. La raíz no borra nada ajeno: pregunta al usuario. Intentos BDD 6 y 7 cerrados
como `bloqueada`. Sin commit: `requirements.in` (A) y `scripts/build_wheels.py` (B, `--selftest` OK) quedan en el árbol.

Instrucción del usuario (2026-11-08): **no usar `du` sobre árboles grandes ni matarlo a medias** (deja
`du.exe.stackdump`); `df -h` para espacio. Segundo incidente de backticks (sed con comillas simples): el shell de la
herramienta los ejecuta igualmente; regla para la raíz y las fichas: ningún backtick en órdenes Bash.

Instrucción del usuario (2026-11-08): **en toda orden que use Rust, `RUSTUP_HOME=S:\Apps\Home\.rustup`**. Esa
carpeta sólo tiene `settings.toml`, así que B tendrá que instalar allí la toolchain 1.97.1 (rustfmt y clippy) que pide
`rust/rust-toolchain.toml`. La descarga va a S:, que tiene 93 GB libres.

| LAB-00-ENV-A fase 1 | L4 | autor | Claude Haiku 5.5 high | 23:38 | 00:46 | bloqueada (C: < 2 GB) | — | intento 6; venv de herramientas en E:, versiones resueltas: torch 2.15.0+cpu, pyarrow 26.0.1, ml_dtypes 0.6.0, arch 8.0.0, MetaTrader5 5.0.6231, chronos-forecasting 2.3.2 |
| LAB-00-ENV-B | L5 | autor | Claude Haiku 5.5 max | 23:38 | 00:51 | bloqueada (C: < 2 GB) | — | intento 7; parado por la guarda antes de compilar |

### Intentos y revisiones (2026-11-08)

| Entrega | Rol | Modelo / esfuerzo | Resultado | Commit | Nota |
|---|---|---|---|---|---|
| LAB-00-ENV-A fase 1 | autor | Claude Haiku 5.5 high | entregada | 4298979 | intento BDD 15 (reanudación) |
| LAB-00-ENV-B | autor | Claude Haiku 5.5 max | entregada | a581355 | intento 16; rueda en 3071 s |
| TI-01-INV intento 1 | autor | Claude Haiku 5.5 high | rechazada | f8f53ad | from/to no RFC3339 (ALTA, verificado en qn-server `parse_recv_ts`; el script original tenía el mismo fallo), límite de filas, mediana con fines de semana, unidades, HTTPError sin sanear |
| TI-01-INV | revisión | Codex gpt-5.6-luna high | RECHAZAR | — | intento 39 |
| LAB-00-ENV-A fase 2 | autor | Claude Haiku 5.5 high | entregada | 33e91fd | intento 38 |
| LAB-00-ENV (A+B) | revisión | Codex gpt-5.6-terra high | RECHAZAR | — | intento 45: 2 ALTA **refutados** (sandbox de sólo lectura sin temporal escribible; fuera, 4 OK), 5 MEDIA válidos |
| TI-01-INV intento 2 | autor | Claude Haiku 5.5 high | rechazada | 29b4c5c | revisión 46: marca `date` antes que `_ts` (ALTA; decisión de raíz: `_ts` principal), duplicados por respuesta, clave sin justificar |
| TI-01-INV intento 3 | autor | Claude Haiku 5.5 high | aceptada con condiciones | d3d9f55 | revisión 56 (luna): UTC en ISO con zona, `--max-symbols` ≥ 1 → cb46ce2, verificado por la raíz |
| LAB-00-ENV correcciones | autor A / B | Claude Haiku 5.5 high | aceptadas | 6b5ac1e / a9a7223 | sha256 real + RECORD + HMM no-op; entorno sellado, extracción a vacío, verificación de SHA256SUMS |
| LAB-00-ENV (correcciones) | revisión | Codex gpt-5.6-terra high | ACEPTAR CON CONDICIONES | — | intento 61: verificación de sums parcialmente tautológica (mitigada por el cruce con el lock en humo); camino de build no reejecutado con el script corregido (declarado en wheels.md) |

### Cierre de LAB-00-ENV (2026-11-08) — CERRADA

- HEAD verificado por la raíz: `cb46ce2` (entregas 4298979, 33e91fd, 6b5ac1e de A; a581355, a9a7223 de B).
- Pruebas (raíz, fuera de sandbox): `run_selftests.py` 4 OK / 0 FALLO; `smoke_env.py --selftest --require-engine` 21 OK /
  0 SALTADAS, con HMM loglik 1293,788 → 1308,932 (76 it., converged), |P−P0| = 0,094, 200 × 20 finitos y determinista;
  torch `2.15.0+cpu`, CUDA None; reproducción en venv limpio con `pip freeze` idéntico (63 líneas, del autor).
- Hashes: rueda `quantdesk-0.0.0-cp312-cp312-win_amd64.whl` sha256
  `28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd` (quantdesk `69fdb39d`); `requirements.lock`
  sha256 `af7f943dd11e442144277fb20afd83bb7bfc36b1dc315fccb6163e76f4312382`.
- Detalle: `docs/plans/current/execution/LAB-00-ENV/{env.md,wheels.md}`.
- Desviaciones: en la primera pasada entraron ~230 MB en la caché de pip de usuario de C: y pip usó TMPDIR en C: durante
  la compilación (corregido en los scripts, no reejecutado); recompilar con el script corregido al subir de motor.

### TI-01-INV — parte de código aceptada (puerta 1 resuelta el 2026-11-08: ver «Cierre de TI-01-INV» en la ola 2)

- Script `scripts/inventario_options_chain.py` en `cb46ce2`, sha256 `7a9811c72876620e1eb7441ee0d5db8e071dd82fa7bf251e8bfe9976d45f9310`;
  selftest OK, sale 2 sin credenciales, `--max-symbols -1` rechazado. Sin probar contra qn real.
- Pendiente: el usuario lo ejecuta con su `QN_URLS`/`QN_TOKEN` y genera el informe; la tarea cierra cuando el informe
  con cifras esté en `docs/plans/current/execution/TI-01-INV/`.

## Ola 2 (2026-11-08)

Cuota antes de la ola (api): Claude 48 % con el 76,8 % de la ventana (reinicio 2026-11-10 00:00 UTC); Codex 72 % con
el 58,5 % (reinicio 2026-11-11 06:41 UTC). Disco: C: 2,9 GB libres; E: 315 GB. Contexto de la raíz: 26 % (tras una
compactación). El usuario pide lanzar la ola 2 mientras la puerta 1 sigue abierta.

- En paralelo (rutas disjuntas, ninguna toca el lock): TS-00-PREC (L6) y TI-13-PUB (L5), autores Claude Sonnet 5.5
  xhigh (LAUNCH §2 para niveles L5–L6 del plan; la A2 señaló que Haiku max sólo lo admite la tabla global); revisión de
  otro proveedor (Codex). TI-12-MT5 espera a la puerta 2; TI-09-ARCH, a las cifras de TI-01-INV (puerta 1).
- Decisión de la raíz (provisional): el primer corte de backtest del filtro D-11 de TI-13-PUB es el parámetro
  `--corte`, por defecto 2016-10-01 (inicio del histórico local de 10 años, PLAN_TSFM_FINANZAS D-07); el filtro se
  reaplica sobre lo crudo sin volver a descargar. Lo fija el usuario cuando se defina el backtest.
- Decisión de la raíz: en TS-00-PREC la delta por AAD de la medida 3 queda «no medida» (no hay AAD hasta engine-nn);
  SPRINT.md sólo pide cono → σ_loc.
- Incidente de la raíz (A9, tercero): un heredoc con backticks para añadir esta sección falló en el shell sin escribir
  nada; rehecho con Edit.

| Entrega | Rol | Modelo / esfuerzo | Resultado | Commit | Nota |
|---|---|---|---|---|---|
| TS-00-PREC y TI-13-PUB (fichas) | revisión A2 | Claude Haiku 5.5 high (sólo lectura) | corregidas | — | intentos 90 y 91. TS: umbral de semillas fijado (sd ddof=1, n=5; medida 1 max de sd de los dos tipos; 2–3 RMS de sd entre modelos f64), Dupire fijado (años, recentrado, sin extrapolar colas), redondeo único con saturación, sin reentreno, tolerancia GARCH, hash canónico y `--verificar`. TI: lista cerrada de subconjuntos y criterio D-11, licencia antes de descargar, LOTSA ≤ 10 GB, caché HF en la guarda, ritmo 1 req/s. Ambas: `git commit -F f -- rutas`, tmp propio, aceptación por `git show` de sus commits |
| TS-00-PREC intento 1 | autor | Claude Sonnet 5.5 xhigh | en curso | | intento 95 |
| TI-13-PUB intento 1 | autor | Claude Sonnet 5.5 xhigh | rechazada | `cd4e4ba` | intento 96 (la BDD lo guarda como «aceptada» porque la raíz lo cerró al recibir la entrega, antes de verificar; no se puede reabrir; el rechazo vale aquí y en el 109). Verificación de la raíz sobre `git archive cd4e4ba` en `E:/quantdesk-lab/tmp/verif-cd4e4ba` (unión al `.venv`): `--selftest` ok, `run_selftests.py` 5 OK / 0 FALLO, `--verificar` OK (1805 ficheros, 130.066.541 filas, filtro reaplicado sobre 36 datasets con el mismo hash), commit sólo con rutas autorizadas. Datos: 36 datasets, 1,0 GB |
| TI-13-PUB revisión 1 | revisor | Codex gpt-5.6-terra high (sólo lectura) | RECHAZAR | — | intento 108. 6 ALTA, 3 confirmadas por la raíz en el código: idempotencia de Binance sólo por tamaño; guarda de 100 GB sin contar los parquet procesados y caché HF truncada a partir de 20.000 ficheros; sin tope LOTSA de 2/10 GB; HF sin User-Agent ni control de reintentos; `--verificar` no compara filas y pasa en vacío. Sin fuga D-11 ni credenciales |
| TI-13-PUB intento 2 | autor | Claude Sonnet 5.5 xhigh | entregada | `4a56315` | intento 109. Verificación de la raíz sobre `git archive 4a56315`: `--selftest` ok, suite 5 OK / 0 FALLO, `--verificar` OK (1805 ficheros, 130.066.541 filas releídas, 36 datasets) |
| TI-13-PUB revisión 2 | revisor | Codex gpt-5.6-terra high (sólo lectura) | RECHAZAR | — | intento 110 (terminó a las 13:10, cerrado tras la recuperación). 4 de 6 corregidos. Quedan: ALTA guarda de 100 GB por estimación 2 × crudo sin guarda incremental al escribir parquet; ALTA reintentos internos de `hf_hub_download` fuera de control (la ficha pide 3 reintentos, Retry-After, ≤ 1 req/s); MEDIA tope total de LOTSA comprobado por fichero (descarga parcial); BAJA `procesar` sin PARADA controlada. Salida: `E:/quantdesk-lab/tmp/TI-13-PUB/revision2_out.md` |
| TS-00-PREC intento 1 | autor | Claude Sonnet 5.5 xhigh | entregada | `4adda7b` | intento 95; la sesión murió tras el commit, sin informe. Logs del autor: selftest ok (8 pruebas, 28 s), suite 6 OK / 0 FALLO, dos ejecuciones completas con el mismo SHA-256 canónico `5760df75…6e1c` (3110 s y 3098 s) |

### Recuperación en frío (2026-11-08 13:32)

La raíz anterior (sesión 6c94f479) murió hacia las 13:11 sin relevar (RECOVERY-20261108-133223). Raíz nueva: sesión
dd43fa94, HANDOFF relevo 1 (`674344b`). Ningún hijo vivo; ningún WIP sin commit. Cuota (api): Claude 51 % con el
78,9 % de la ventana; Codex 77 % con el 60,6 %. Disco: C: 2,9 GB; E: 314 GB.

- Decisión de la raíz (A12): TI-13-PUB intento 3 corrige los 4 hallazgos de la revisión 2; para el Hub, GET propios con
  el cliente de Binance (UA, ritmo, reintentos y Retry-After de la ficha) en lugar de `hf_hub_download`.
- Incidente A9 (cuarto): un heredoc con backticks volvió a ejecutar fragmentos en el shell (sin escrituras ni cambios).
  Además, órdenes con `<correo>` entre comillas rompen el envoltorio del Bash de la herramienta: los mensajes de commit
  van siempre en fichero (Write) con `git commit -F`.

| Entrega | Rol | Modelo / esfuerzo | Resultado | Commit | Nota |
|---|---|---|---|---|---|
| TS-00-PREC | verificación de la raíz | — | verde | `4adda7b` | `git archive 4adda7b` en `E:/quantdesk-lab/tmp/verif-4adda7b`: selftest ok; suite 6 OK / 0 FALLO; `--verificar` del directorio del informe OK (1228 cifras); banco completo en solitario **919 s** con el mismo SHA-256 canónico `5760df75…6e1c` y `--verificar` OK. El hallazgo de tiempo de la revisión 1 queda refutado (los 51,8 min eran dos ejecuciones simultáneas) |
| TS-00-PREC revisión 1 | revisor | Codex gpt-5.6-terra high (sólo lectura) | RECHAZAR | — | intento 111 (intento 95 del autor cerrado como rechazado). Decisión de la raíz (A12): **se corrigen** la rejilla de K de la medida 3 (fijada con el cono medio f64; un K puede salirse del intervalo [S_h(0,10), S_h(0,90)] de un modelo concreto → intersección de los 5 f64) y `--informe`/`--out` sin acotar (BAJA). **Refutados** (documentados por el autor; sólo se pide justificarlos en el informe): escala por muestra en activaciones (escala por tensor de una inferencia de lote 1, independiente del agrupado) y hash canónico a 10 cifras (veredictos y cocientes van en el JSON hasheado). **Pendiente**: 51,8 min frente a ~45 min, medidos con dos ejecuciones simultáneas (una en solitario anterior: 43 min); decide la medición en solitario |
| TS-00-PREC intento 2 | autor | Claude Sonnet 5.5 xhigh | entregada | `5afc795` | intento 113. Rejilla de K por intersección de los 5 f64 (0 de 9216 tríos vacíos); `--out`/`--informe` acotados (`rutas.py`); justificaciones de escala por muestra y hash a 10 cifras en el informe. Dos ejecuciones en serie: 1445,8 s y 975,9 s, mismo SHA-256 canónico `83548e1a…3d15`. Ningún veredicto cambia (147/147). ¿Basta fp8? Entrada sí (e4m3 y e5m2); inferencia emulada y σ_loc no; bf16/f16/f32 no pierden |
| TS-00-PREC intento 2 | verificación de la raíz | — | verde | `5afc795` | `git archive 5afc795`: commit sólo con rutas autorizadas; selftest ok; suite 6 OK / 0 FALLO; `--verificar` del directorio del informe OK (1238 cifras); `--informe C:/x` rechazado con salida 2; banco completo en solitario 915 s con el mismo SHA-256 canónico `83548e1a…3d15` y `--verificar` OK |
| TS-00-PREC revisión 2 | revisor | Codex gpt-5.6-terra high (sólo lectura) | RECHAZAR, **refutado por la raíz** | — | intento 117. Confirma la rejilla de K (intersección de los 5 f64; 9216 tríos, 0 vacíos, 82.944 K, 0 fuera de un f64) y que ningún veredicto cambia. ALTA «el selftest falla de forma determinista»: **falsa**; la lista de rutas ajenas de `pruebas.py` no contiene `rutas.DOCS` (sólo `DOCS + "/../TI-13-PUB"` y `DOCS + "-otro"`), y el selftest de la raíz sobre `git archive 5afc795` da `selftest ok`, rc 0. MEDIA carrera entre validar la ruta y escribir (un proceso que cambie el directorio por una unión): fuera del modelo de amenaza de una herramienta local lanzada por el operador; BAJA, sin cambio |
| TI-13-PUB intento 3 | autor | Claude Sonnet 5.5 xhigh | entregada | `e001a97` | intento 112. Guarda incremental por lote con bytes reales y borrado del parcial; Hub con el cliente HTTP propio (sin `hf_hub_download` ni `HfApi`, revisión fijada); reserva del subconjunto LOTSA entero; PARADA con salida 3 en `procesar`. Autor: selftest ok, suite 6 OK, `--verificar` OK con hashes de dataset idénticos; 11 mutaciones rompen el selftest. Dudas declaradas: si la guarda salta a mitad se pierde el procesado anterior (regenerable desde el crudo); cota de lote muy conservadora |
| TI-13-PUB intento 3 | verificación de la raíz | — | verde | `e001a97` | `git archive e001a97` en `E:/quantdesk-lab/tmp/verif-e001a97`: commit sólo con las 9 rutas autorizadas; `--selftest` ok; suite 6 OK / 0 FALLO; `--verificar` OK (1805 ficheros, 130.066.541 filas releídas, 36 datasets, filtro reaplicado); `hf_hub_download`/`HfApi` sólo aparecen en texto y docstrings |
| TI-13-PUB revisión 3 | revisor | Codex gpt-5.6-terra high (sólo lectura) | RECHAZAR | — | intento 114 (el 112 del autor, cerrado como rechazado). Hub, tope LOTSA y PARADA: corregidos; guarda de lotes y pies: corregida, la llama «parcial» por los auxiliares. Decisión de la raíz (A12): **se corrigen** los temporales `.part` abandonados que no cuenta la guarda (ALTA → MEDIA, acotado por el tamaño de fichero) y el `Retry-After` > 60 s acortado (MEDIA; la ficha pide respetarlo: se para sin reintentar). `manifest.json`/CSV sin guarda: ALTA → **BAJA** (KB frente a una cota de lote con cientos de MB de margen); se pide una reserva fija. **Refutado**: bloqueo al reparar LOTSA corrupto cerca del tope (falla del lado seguro; se declara). Perder el procesado anterior si salta la guarda: aceptado por el revisor y por la raíz |
| TI-13-PUB intento 4 | autor | Claude Sonnet 5.5 xhigh | aceptada | `7ea6d94` | intento 115: temporales de descarga en la guarda (se conservan para reanudar con Range), `Retry-After` > 60 s para sin reintentar, reserva fija de 64 MiB para auxiliares; limitación LOTSA declarada |
| TI-13-PUB intento 4 | verificación de la raíz | — | verde | `7ea6d94` | `git archive 7ea6d94`: commit sólo con rutas autorizadas; `--selftest` ok; suite 6 OK / 0 FALLO; `--verificar` OK (1805 ficheros, 130.066.541 filas releídas, 0 series y 0 contenidos compartidos entre train y val, filtro reaplicado sobre 36 datasets) |
| TI-13-PUB revisión 4 | revisor | Codex gpt-5.6-terra high (sólo lectura) | ACEPTAR | — | intento 116: los 3 puntos corregidos con selftests significativos; sin regresiones ni defectos nuevos |

### Cierre de TI-13-PUB (2026-11-08) — CERRADA

- HEAD verificado por la raíz: `7ea6d94` (entregas `cd4e4ba`, `4a56315`, `e001a97`, `7ea6d94`; cuatro intentos de autor y
  cuatro revisiones de Codex: 108, 110 y 114 RECHAZAR, 116 ACEPTAR).
- Pruebas (raíz, copia aislada): `--selftest` ok; `run_selftests.py` 6 OK / 0 FALLO; `--verificar` OK.
- Datos: 36 datasets en `E:/quantdesk-lab/datasets/TI-13-PUB/`, crudo en `E:/quantdesk-lab/data/public/`; 1,005 GB de
  100 GB (crudo 0,573 + procesado 0,432); LOTSA 0,327 GB de 10 GB. Revisiones fijadas del Hub: chronos_datasets
  `eeecad0b…2cec`, lotsa_data `8191fd29…615d`. Corte D-11 provisional `--corte 2016-10-01` (decisión de la raíz; lo fija
  el usuario al definir el backtest; el filtro se reaplica sin volver a descargar).
- Informes (sha256): `informe.md` `62272c6c…f4bb`, `licencias.md` `8b11a8f6…faf5`, `filtro.md` `2edf6c7d…236b`, en
  `docs/plans/current/execution/TI-13-PUB/`. Script `scripts/ingesta_publica.py` sha256 `626848f3…` (paquete
  `scripts/ingesta_publica_lib/`).
- Limitaciones declaradas: si la guarda salta a mitad de procesar, el procesado anterior del dataset se pierde
  (regenerable desde el crudo); la reparación de un LOTSA corrupto cerca del tope de 10 GB se bloquea de más.

### Cierre de TS-00-PREC (2026-11-08) — CERRADA

- HEAD verificado por la raíz: `5afc795` (entregas `4adda7b`, `5afc795`; revisiones de Codex 111 RECHAZAR —2 puntos
  corregidos, 3 refutados— y 117 RECHAZAR refutado).
- Pruebas (raíz, copia aislada): selftest ok; `run_selftests.py` 6 OK / 0 FALLO; banco completo en solitario 915 s;
  SHA-256 canónico de `resultados.json` `83548e1ab61953a5602f96d0a4c21b67ef99e7b5158629f78b3956969a543d15`, igual en las
  dos ejecuciones del autor y en la de la raíz; `--verificar` OK. Semillas n = 5, ddof = 1; motor quantdesk `69fdb39d`;
  torch 2.15.0+cpu.
- Evidencia: `docs/plans/current/execution/TS-00-PREC/{informe.md, resultados.json, resultados.json.sha256}` (informe
  sha256 `b375cbc6…`); ejecuciones en `E:/quantdesk-lab/runs/TS-00-PREC/{i2-a, i2-b, verif-raiz-5afc795}`. Script
  `scripts/banco_precision.py` sha256 `872cab78…` (paquete `scripts/banco_precision_lib/`).
- **¿Basta fp8? (primera respuesta, emulada en CPU):** para la entrada (medida 1), sí, e4m3 y e5m2; para la inferencia
  con redondeo en cada frontera de capa (medida 2) y para σ_loc por Dupire (medida 3), no: pierden e4m3 y e5m2, con y
  sin escala (e4m3 pierde 4 métricas y e5m2 6). bf16, f16 y f32 no pierden en ninguna medida. Vol de la vol y delta por
  AAD: no medidas (AAD requiere engine-nn). Salvedades en el §5 del informe (emulación, modelo pequeño, n = 5).

### Cierre de TI-01-INV (2026-11-08) — CERRADA

- Puerta 1: el usuario pide a la raíz que emita un token de qn siguiendo la documentación de quantdesk-network. La raíz
  sigue la skill `qn-token` y el usuario confirma nombre, entorno y concesión exactos antes de emitir.
  - Token `ti01-inventario-20261108`, id 32, `main`, `sub:market.>`, emitido en mini a las 15:48:58Z.
  - Revocado a las 15:58:26Z: listado 0, fichero borrado con `shred`. El secreto no salió de mini.
  - Intento BDD 118, de la raíz (ejecución del script ya revisado en `cb46ce2`; no hay código nuevo que revisar).
- Primera ejecución, descartada: contra mini, en `stopping` por un redespliegue ajeno (503 en `market.rates.quotes`).
  Repetida contra macold (`/health` 200): completa, 7816 GET, sin errores.
- Comprobación de la raíz: una sonda de sólo lectura confirma que `market.options.chain` (esquema v2) y
  `market.options.fx` no tienen **ninguna fila** en `main` entre 2024-01-01 y 2027-01-01, ni siquiera sin filtro de
  etiquetas. La misma consulta sobre rates sí devuelve filas.
- GPU de la flota, medida por ssh y sólo leyendo: mini, silver y macold sólo tienen gráficos integrados de Intel, sin
  NVIDIA.
- Evidencia:
  - `docs/plans/current/execution/TI-01-INV/informe.md` (salida sin tocar, sha256 `75095098…c4fe`) y `anexo-raiz.md`
    (procedencia, sonda, GPU y lectura para el sprint);
  - JSON en `E:/quantdesk-lab/runs/TI-01-INV/inventario-macold.json` (sha256 `99dcc5cd…67fc`).
- Cifras:
  - ohlcv: 28 cruces FX diarios desde 2024-11-01, con una cobertura del 99 % y sin huecos; los horarios sólo desde
    2026-10-18. 6047 duplicados de 30 665 filas.
  - rates.quotes (103 nodos) y performance (64), desde 2025-12-04: hueco de 118–120 días hábiles entre 2026-04 y
    2026-09; cobertura del 34–44 %.
- Consecuencia: **TI-09-ARCH no tiene datos de origen.** La cadena de opciones nunca llegó a qn, y lo que no llegó no se
  recupera (12-A). Queda a decisión del usuario (pregunta abierta en el HANDOFF). TI-02-DATA puede arrancar con ohlcv,
  rates y performance.

### TI-09-ARCH — RETIRADA (2026-11-08)

- Usuario, 2026-11-08: «lo quitamos del sprint hasta que tengamos más datos». No se lanzó ningún intento.
- Estado en la BDD: `retirada`. SPRINT.md la marca en la fila 3 y en §6 Exclusiones. En el backlog pasa a «Esperando
  datos». La fila de cobertura de `next/SPRINT.md` queda condicionada a entregar antes la parte de laboratorio.
- Las dependencias de tarea de DEPENDENCIAS.md (OC-01/02/03, OCS-02) siguen siendo válidas para cuando vuelva.

## Ola 3 (2026-11-08)

- Cuota semanal antes de la ola (`claude-or quota --weekly`, 2026-11-08):
  - Claude: 54 % consumido, con el 82,9 % de la ventana transcurrido; reinicio el 2026-11-10 00:00 UTC.
  - Codex: 91 % consumido, con el 64,7 % transcurrido; reinicio el 2026-11-11 06:41 UTC.
  - Alcanza para la autoría de TI-02-DATA. A Codex le queda poco: la revisión irá a Codex sólo si le queda margen al
    llegar; si no, a Claude Opus 5.5, que es otro modelo que el autor (LAUNCH §2), y queda anotado.
- Token: el usuario autoriza otro token de sólo lectura igual al de TI-01-INV («emite otro token de solo lectura»).
- **Decisión de la raíz (A13):** TI-02-DATA se parte en dos pasos, porque la skill `qn-token` obliga a usar el token en
  el host donde se emite (mini) y el exportador necesita el `.venv` de Windows (pyarrow, `data_py`):
  1. `scripts/descarga_lago.py`: sólo biblioteca estándar. La raíz lo ejecuta en mini con el token y copia a
     `E:/quantdesk-lab/data/lago/` el volcado crudo, con su manifiesto y sus SHA-256. El volcado no contiene el
     token.
  2. `scripts/exportar_market_history.py`: en el `.venv`, sin red ni token. Pasa el volcado (y las velas de Binance
     de TI-13-PUB) a `engine.market-history/v1`.
  - El token se emite cuando la raíz haya leído entero el paso 1 y su selftest esté en verde, y se revoca en cuanto
    termine la descarga. La revisión de otro modelo cubre después los dos pasos.
