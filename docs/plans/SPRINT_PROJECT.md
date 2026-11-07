# Proyecto de sprints — quantdesk-model

Datos propios de este repositorio para las skills globales `sprint`, `execute-plan` y `como-vas`
(`~/.claude/skills/`). Las skills leen este fichero primero; todo lo que no esté aquí sigue la regla
genérica de la skill. Mantenerlo corto: la parte principal se lee en cada invocación; lo largo va a
«Anexos», que sólo se leen cuando una referencia los pide. Instalado el 2026-11-07.

## 1. Identidad

- Proyecto: `quantdesk-model` (mismo nombre que usan los `DEPENDENCIAS.md` de otros proyectos).
- Qué es: **laboratorio Python** de datos y modelos del TSFM de `quantdesk` (adquisición y exportación de
  datos, datasets congelados con hash, bancos y referencias externas, configuraciones de ejecuciones,
  informes, fichas de modelo, almacén de artefactos). Git local sin remoto (§2); datos fuera de Git (§11).
- Repositorio: `S:/Projects/quantdesk-model`
- Raíz de planes: `docs/plans/`
- Backlog del laboratorio (tareas, comprobaciones y calendario): [backlog/README.md](backlog/README.md).
  `docs/plans/BACKLOG.md` queda como puntero (lo citan planes de `quantdesk` y una memoria).
- Planes de diseño (especificación y aceptación de cada ID): en `quantdesk`, sólo lectura:
  `S:/projects/quantdesk/docs/plans/backlog/` (PLAN_TSFM_FINANZAS, PLAN_TSFM_INTEGRACION,
  PLAN_XVA_BANCARIO, PLAN_DEEP_LEARNING_GPU). Los IDs de tarea son los de esos planes.
- Cola viva de issues fuera de sprint: `docs/plans/issues/`
- Estado global: `docs/plans/STATUS.md`
- Tablero: `docs/plans/index.md` · Navegación del portal: ninguna
- Memoria / herramienta de conocimiento: ninguna

## 2. Git

- Repositorio Git local, rama `main`, **sin remoto** (decisión del usuario, 2026-11-07). Commits por
  fase y tag de cierre `sprint-NN` como en la skill; sin push.
- `.gitignore`: `.sprint-runtime/`, entornos, `data/`, `runs/`, `artifacts/` y pesos/datasets
  (`*.parquet`, `*.safetensors`, `*.ckpt`, `*.pt`). Los datasets y artefactos no van a Git: se
  registran por ruta y SHA-256 en los informes.

## 3. Comandos

| Uso | Comando |
|---|---|
| Entorno | `.venv` propio, Python 3.12 (LAB-00-ENV): `py -3.12 -m venv .venv` y `.venv/Scripts/python -m pip install -r requirements.lock` «el lock lo crea LAB-00-ENV» |
| Python mientras no exista `.venv` | `S:/projects/quantdesk/venv/Scripts/python.exe` sólo para leer/probar; **no instalar nada en él** (lo cambian los sprints de `quantdesk`) |
| Build | sólo las ruedas de `quantdesk` (GAP-03): `git -C S:/projects/quantdesk archive <commit>` a `E:/quantdesk-lab/build/<commit>/` y `maturin build --release` allí; ruedas a `E:/quantdesk-lab/wheels/` con SHA-256. Nunca compilar dentro de `S:/projects/quantdesk` |
| Tests rápidos | `--selftest` de cada script, p. ej. `.venv/Scripts/python -X utf8 scripts/inventario_options_chain.py --selftest` |
| Suite completa (DoD y cierre) | «rellenar al crear LAB-00-ENV: selftests de todos los `scripts/*.py`, p. ej. con `pytest`» |
| Gate / candados | ninguno propio; la GPU según los carriles de DL-02-GATES de `quantdesk` cuando existan |
| Build de release / Publicar | ninguno |

## 4. Capas y verificación

Capas: datos (adquisición y exportación) → datasets congelados (`engine.market-history/v1`, hash) →
bancos e informes. Se verifica de dentro hacia fuera: el dataset carga en `quant-data` sin violaciones
de look-ahead y su hash es reproducible antes de usarlo en un banco; cada informe cita semilla, hash del
dataset y versión de la rueda de `quantdesk` usada.

## 5. Políticas del proyecto

Reglas de separación (backlog §1, decididas por el usuario el 2026-11-07):

- El laboratorio **no escribe código Rust ni toca el código ni los sprints de `quantdesk`**; usa
  `quantdesk` sólo como consumidor (rueda Python fijada por versión, CLI). Si una tarea necesita algo del
  motor que no está expuesto, se pide como tarea de `quantdesk` (en su backlog). Excepción (usuario,
  2026-11-07): el laboratorio **sí registra** las decisiones del usuario y los umbrales de TS-00-OBJ en
  los planes TSFM del backlog de `quantdesk`, con enlace a su informe. La tabla completa de dueños y
  permisos está en [GOBERNANZA.md](GOBERNANZA.md).
- Los IDs y su especificación siguen en los planes de `quantdesk`; aquí se registra su ejecución.
- **GPU**: respetar los carriles de DL-02-GATES (`gpu:0`, `gpu:1`) cuando existan; hasta entonces, el
  banco zero-shot va en CPU.
- **Credenciales** (MT5, `QN_TOKEN`, tokens de APIs públicas): fuera del repo y del chat; variables de
  entorno o almacén del sistema. Nunca en ficheros del proyecto, informes ni prompts.
- El extractor MT5 sólo lee: nunca envía órdenes.

| Fichero | Para qué | Cuándo leerlo |
|---|---|---|
| `docs/plans/backlog/README.md` | Tareas, comprobaciones y calendario del laboratorio | planificar |
| `docs/plans/USAGE_PROTOCOL.md` | Medición de cuota y costes | presupuestar, lanzar, cerrar |
| `docs/plans/arnes/README.md` | Arnés de ejecución (reglas para trabajo delegado) | lanzar, ejecutar |

## 6. Delegación

- Esquema de dificultad: L1–L4 por defecto (execute-plan §2.1); los niveles de los planes de
  `quantdesk` (L3…L8) se respetan como referencia de riesgo.
- Tabla de modelos y revisores: la de execute-plan §2.1.
- Herramientas de cuota/ruta: ninguna propia.
- Cupo por defecto: raíz + 3 descendientes activos.

## 7. Costes

- Mensualidades: Claude 200 USD/mes y Codex 100 USD/mes, **las mismas suscripciones que `quantdesk`,
  `quantdesk-backend` y `quantdesk-network`** (usuario, 2026-11-07); mes contable de 30 días,
  `USD = mensualidad × 7/30 × pp/100`. Sin tope ni reserva de cuota entre proyectos: la cuota semanal
  es común y la usa quien llega primero (decisión del usuario).
- Tabla de costes: `docs/plans/usage/COST_TABLE.md`, generada con `python -X utf8 "$HOME/.claude/skills/sprint/scripts/sprint_costs.py"` (skill global, desde la raíz del repo).

## 8. Orden de la cola

Ninguno: el orden es el del SPRINT.md de cada sprint.

## 9. Relevo de la raíz

- Herramienta: `python -X utf8 "$HOME/.claude/skills/sprint/tools/claude_or.py" handoff` (lanzadores
  `run_claude_handoff_launch.cmd` y `run_claude_handoff_recover.cmd` en la raíz del repo). Requiere Git
  (hecho el 2026-11-07).
- HANDOFF: `docs/plans/current/HANDOFF.md`. Arranque: `docs/plans/arnes/ARRANQUE.md` y `ARRANQUE_FRIO.md`.
- Hook de zonas: PostToolUse `node "<home>/.claude/skills/sprint/scripts/context-hook.mjs"` en
  `.claude/settings.json`: registrado (2026-11-07).
- Modelo/esfuerzo de la raíz y modo de permisos de la sucesora: los del LAUNCH.

## 10. Release

Ninguna release: al cerrar un sprint se pasa de cerrado a planificación registrando esa decisión.
Los entregables son datasets e informes con hash, no paquetes publicados.

## 11. Particularidades

- **Estado de ejecución y relevos**: los de la skill, dentro de `.git/` y sin versionar:
  `.git/sprint-runtime/` (fichas, salidas de hijos, relevos, candado del latido) y `.git/sprint-usage/`
  (evidencia privada de cuota). El latido se lanza sin `--lock-dir`. (Hasta el 2026-11-07, sin Git, se
  usaba `.sprint-runtime/`; sigue en `.gitignore` por si quedara algún resto.)
- **Almacén de datos y artefactos** (GAP-02, usuario, 2026-11-07; provisional hasta D-I2 / TI-00-ADR):
  `E:/quantdesk-lab/` con `data/`, `datasets/`, `runs/`, `artifacts/`, `cache/hf`, `cache/pip`. Nada
  grande en S: (98 %) ni en C: (99 %): `HF_HOME` y `PIP_CACHE_DIR` apuntan a `cache/`. Los informes citan
  ruta y SHA-256. Presupuesto de corpus públicos: 100 GB, ajustable por el usuario.
- **Python del sistema**: el alias `python` de WindowsApps no funciona («Permission denied»). Usar el
  `.venv` del laboratorio o, para las skills, `S:/projects/quantdesk/venv/Scripts/python.exe`.
- **Datos sin campo de procedencia sintética** hasta TI-03-FMT (SPRINT-03 de `quantdesk`): los datos
  reales no lo necesitan; la procedencia (fuente, bróker, versión) va en un fichero adjunto al dataset y
  se incorpora al manifiesto cuando TI-03-FMT exista.

## Anexos

Ninguno.
