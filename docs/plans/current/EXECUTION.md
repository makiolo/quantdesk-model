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

### TI-01-INV — parte de código aceptada; falta la puerta de usuario 1

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
| TI-13-PUB intento 2 | autor | Claude Sonnet 5.5 xhigh | en curso | | intento 109, mismo autor reanudado con el diagnóstico |
