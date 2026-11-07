# Responsabilidades y gobernanza — quantdesk-model

Quién es dueño de cada cosa que este proyecto produce o consume, quién la escribe, quién decide y cómo se
piden cambios desde otro proyecto. Es la referencia para coordinar el trabajo entre proyectos; cada sprint
la revisa al planificar e iniciar (skill `sprint`, `references/start.md` paso 2b) y copia en su SPRINT.md
§2 las filas que le afectan. Las dependencias temporales entre sprints van en [DEPENDENCIAS.md](DEPENDENCIAS.md).

Estado: `decidido (usuario, fecha)` o `propuesto` (pendiente de preguntar al usuario).

| Cosa (documento, código, dato, artefacto, decisión) | Dueño (proyecto) | Escribe | Decide / aprueba | Cambios desde otro proyecto | Estado |
|---|---|---|---|---|---|
| Backlog, sprints y `docs/plans/` del laboratorio | quantdesk-model | sesiones del laboratorio | usuario | nota o issue en este repo | decidido |
| Especificación TSFM: `PLAN_TSFM_FINANZAS`, `PLAN_TSFM_INTEGRACION` (decisiones D-*, D-I*, umbrales de TS-00-OBJ) | quantdesk (backlog) | quantdesk y el laboratorio: el laboratorio registra allí las decisiones del usuario y los umbrales, con enlace a su informe | usuario | edición directa del plan en `quantdesk/docs/plans/backlog/`; nunca `current/` ni código de quantdesk | decidido (usuario, 2026-11-07) |
| Código del motor, rueda Python, bindings (`data_py`, HMM), CLI | quantdesk | sesiones de quantdesk | usuario | tarea en el backlog de quantdesk | decidido (usuario, 2026-11-07) |
| Datasets congelados (`engine.market-history/v1`), informes de banco, artefactos del laboratorio; almacén `E:/quantdesk-lab/` (GAP-02) | quantdesk-model | sesiones del laboratorio | usuario (umbrales, publicación, presupuesto de disco) | issue en este repo | decidido (usuario, 2026-11-07) |
| Entorno del laboratorio (`.venv`, `requirements.lock`) | quantdesk-model | LAB-00-ENV y quien añada dependencias, en serie | usuario | — | decidido (usuario, 2026-11-07) |
| Scraper de cadenas de opciones (OC-01…OC-05) | quantdesk-backend | sesiones del backend | usuario | `quantdesk-backend/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ARCHIVO.md` | decidido (usuario, 2026-11-07) |
| Esquema de `market.options.chain` y retención del lago (OCS-01, OCS-02) | quantdesk-network | sesiones de network | usuario | `quantdesk-network/docs/plans/backlog/PLAN_OPTIONS_CHAIN_ESQUEMA_CAPTURA.md` | decidido (usuario, 2026-11-07) |
| Herramientas de sprint y relevos (`~/.claude/skills/sprint`, incluido `tools/`) | global (skill) | cualquier sesión, registrándolo en la skill | usuario | editar la skill; nunca `S:/Apps/bin` (congelada) | decidido (usuario, 2026-11-07) |
| Credenciales (MT5, `QN_TOKEN`, APIs) | usuario | usuario | usuario | nunca en repos, informes, prompts ni chat | decidido |
