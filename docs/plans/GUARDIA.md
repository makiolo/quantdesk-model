# GUARDIA — quantdesk-model

Notas de la raíz de guardia (skill global `sprint`, `references/guardia.md`). Como mucho 80 líneas.

> **2026-11-14: SPRINT-03 activo.** La guardia `quantdesk-model-4d` pasó a ser la raíz inicial del sprint (`guardia.md`
> «Paso a sprint»). Mientras dure el sprint mandan `current/SPRINT.md`, `current/LAUNCH.md`, `current/EXECUTION.md` y,
> en los relevos, `current/HANDOFF.md`; este fichero queda como notas de la última guardia y se actualiza al cerrar.

## Estado (2026-11-14). Guardia `quantdesk-model-4d`
- **Sin sprint activo hasta el 2026-11-14.** SPRINT-02 cerrado con arrastres el 2026-11-13 (`archive/SPRINT-02_2026-11-11_2026-11-13/`).
- Revisión de planes del 2026-11-13 commiteada y empujada en `41efbbf` (la guardia `c4` murió antes del commit); hash
  anotado en `backlog/REVISIONES.md` y kanban de `index.md` regenerado (`scripts/sprint_db.py kanban --write`).
- Raíces vivas a la entrada: `quantdesk-f1`, `quantdesk-backend-24`, `quantdesk-network-21` (presentación enviada a las tres).
- `bash.exe.stackdump` sin seguimiento en la raíz del repo: nunca añadirlo.
- Decisiones del usuario R0–R8 (detalle en `backlog/REVISIONES.md`, entrada 2026-11-13):
  - **R1 partición:** SPRINT-03 nuevo en `next/`, activable ya y sin depender de quantdesk. SPRINT-04 nuevo en `future/`
    (S02-1…S02-4 y §3; espera a quantdesk SPRINT-03). El antiguo SPRINT-04 de entrenamiento pasa a SPRINT-05 (espera a quantdesk SPRINT-04).
  - **R2:** tarea `quantdesk\publicador_mt5` **DESACTIVADA** el 2026-11-13 ~23:55 (verificado «Disabled»). Se reactiva en
    la fila 4c cuando el bróker desbloquee la cuenta.
  - **R3:** ISSUE-TI12-MT5-SYNC cerrada y VELA-A-MEDIAS fusionada en ella, en `archive/FUERA-SPRINT_2026-11-09_2026-11-13/`.
  - **R4:** la SONDA se cierra con la cifra de S02-6.
  - **R5:** TI-02-DIARIO es la fila 1 (contrato) y la fila 2 (código sin OAS) de SPRINT-03.
  - **R6:** se consumen FRED/OAS; Yahoo/Stooq y cripto quedan en el backlog.
  - **R7:** el intradía en qn va en SPRINT-05.
  - **R8:** INTRA-LOCAL incluye las acciones, con pasadas manuales cada ≤ 6 semanas; la primera, antes del 2027-01-17.
- Filas de SPRINT-03: 1 contrato TI-02-DIARIO (L3) · 2 código TI-02-DIARIO (L6) · 3 S02-6 + sonda (L5, desde el 2026-12-11,
  token nuevo) · 4a S02-5 h1 (L6) · 4b INTRA-LOCAL (L5) · 4c MT5-OPS (L3) · 5 PUB-AMP condicionada (L5) · 6 FRED (L4) · 7 OAS (L4).
- Avisos del revisor sin verificar: con este diff cambian los SHA-256 de `archive/SPRINT-01…/SPRINT.md` y
  `archive/SPRINT-02…/SPRINT.md`, porque se reapuntaron enlaces; está anotado en el manifiesto nuevo. Sus hashes «posteriores» se
  calcularon antes de la última edición de `next/SPRINT.md`, que no está archivado.

## Dependencias
- SPRINT-03 sin dependencia de entrada. SPRINT-04 ← quantdesk SPRINT-03 cerrado. SPRINT-05 ← quantdesk SPRINT-04 cerrado.
- Backend: OC-03 servida (una captura por sesión NY a las 16:30, corte ≥ 2026-11-12). Su SPRINT-03 publica FRED y OAS y
  programa nuestro exportador (PUB-05-EXPORT).

## Compromisos con otras raíces (las tres guardias o raíces se cerraron a petición del usuario a la vez que esta)
- **quantdesk** (era `quantdesk-c3`, relevo 55): avisará al cerrar su SPRINT-02 y si cambian la rueda, TI-03-FMT o
  DL-02-GATES. Las dos tareas que apuntó (su DEPENDENCIAS por nuestra renumeración y PLAN_TSFM_FINANZAS §3, TS-16-QCONO
  y TS-08-DYN, «cadenas vacías») están hechas en su `3eb4c799` (sin push a 2026-11-14), confirmado por `quantdesk-f1`.
- **backend** (era `quantdesk-backend-d4`; sucesora «quantdesk-backend raiz relevo 6», ver `~/.claude/relevos.json`):
  avisará cuando publique el mercado público y antes de cambiar OC-03. Contrato de TI-02-DIARIO abierto: sus
  restricciones y los 4 puntos por acordar están en `current/SPRINT.md` §3 («Entrada de la fila 1»). **Nosotros** les
  avisamos cuando MT5 vuelva a publicar. Confirmado por `quantdesk-backend-24` el 2026-11-14: `fred_oas_capture_schedule`
  aún sin activar (antes verifican unidad y hora); esperan nuestra propuesta conjunta del contrato en la §3; sus
  restricciones de PUB-05-EXPORT no cambian.
- **network** (era `quantdesk-network-f0`; la guardia nueva entra por su GUARDIA.md): avisará de cambios en retención o
  esquema de `market.*`, en el borrado o en el horizonte de revisión. D7 conciliado en su `85c4708`. Confirmado por
  `quantdesk-network-21` el 2026-11-14: `market.*` sin cambios; la Fase 3 (borrado) irá en el sprint que siga a COP y
  rechazará `market.*` en `main` por defecto; avisarán cuando la 3.2 se despliegue (único resto de la 3.4,
  C-RETIRADA-02); nuestra sustitución de PLAN_ARCHIVO_OPCIONES §4 les vale. Visto bueno de 4c/5: escribirles tras el desbloqueo.
- Norma nueva (usuario, 2026-11-13 23:40, ya en la skill): no se usa bash.exe para nada que dure. Los hijos se lanzan con
  `tools/lanza/hijo.py`, el vigía con `wsvigia.py` por WebSocket en un puerto propio (quantdesk usa el 8765).

## Preguntas abiertas al usuario
- Diferidas a la ficha de cada fila: GAP-ARCHIVO_OPCIONES-03 (métrica del 98 %) y -05 (cortes bajo demanda); GAP-BACKLOG_README-03
  (dos publicadores); -05 (GPU); GAP-DATOS_VIA_QN-08 (universo ampliado en qn).
- ¿Activar SPRINT-03 ya (`sprint iniciar`)? Hoy casi todas sus filas esperan algo: el contrato, el 2026-12-11, el
  desbloqueo de MT5 o el backend. La fila 1 (contrato de TI-02-DIARIO) sí puede empezar ya.

## Siguiente paso
1. Hacer el commit pendiente (arriba).
2. Presentarse a las raíces nuevas.
3. Proponer al usuario `sprint planificar`/`iniciar` de SPRINT-03, empezando por el contrato de TI-02-DIARIO.
