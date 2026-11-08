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

Instrucción del usuario (2026-11-08): **en toda orden que use Rust, `RUSTUP_HOME=S:\Apps\Home\.rustup`**. Esa
carpeta sólo tiene `settings.toml`, así que B tendrá que instalar allí la toolchain 1.97.1 (rustfmt y clippy) que pide
`rust/rust-toolchain.toml`. La descarga va a S:, que tiene 93 GB libres.

| LAB-00-ENV-A fase 1 | L4 | autor | Claude Haiku 5.5 high | 23:38 | 00:46 | bloqueada (C: < 2 GB) | — | intento 6; venv de herramientas en E:, versiones resueltas: torch 2.15.0+cpu, pyarrow 26.0.1, ml_dtypes 0.6.0, arch 8.0.0, MetaTrader5 5.0.6231, chronos-forecasting 2.3.2 |
| LAB-00-ENV-B | L5 | autor | Claude Haiku 5.5 max | 23:38 | 00:51 | bloqueada (C: < 2 GB) | — | intento 7; parado por la guarda antes de compilar |
