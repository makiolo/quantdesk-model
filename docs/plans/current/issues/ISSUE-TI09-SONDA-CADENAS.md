# [ISSUE-TI09-SONDA-CADENAS] ¿Hay cadenas de opciones en qn? Sonda de sólo lectura

> **Tipo:** Incidencia\
> **Estado:** Abierto; se cierra con la cifra por sesión de S02-6 desde el 2026-11-12 (usuario, 2026-11-13, revisión de planes, R4)\
> **Fecha de detección:** 2026-11-09\
> **Origen:** Fuera de sprint (revisión de planes 2026-11-09, contradicción C-07; decisión del usuario «Sonda de sólo lectura», 2026-11-09)\
> **Componente afectado:** documentación de estado del laboratorio (STATUS, SPRINT-01) y lectura de `market.options.chain` en qn\
> **Especificación de referencia:** [PLAN_ARCHIVO_OPCIONES.md](../../backlog/PLAN_ARCHIVO_OPCIONES.md) §3, tarea TI-09-SONDA\
> **Severidad:** Media\
> **Destino:** Sprint actual: SPRINT-03 (activo desde el 2026-11-14), fila 3, unida a S02-6 ([SPRINT.md](../SPRINT.md); usuario, 2026-11-13, revisión de planes, R4). Antes: «Fuera de sprint — urgente»\
> **Prioridad y motivo:** la pregunta de fondo ya está contestada (hay cadenas en qn desde la sesión 2026-11-12; `market.options.fx` sin filas) y STATUS se corrigió el 2026-11-13; queda la cifra por sesión, que sale del volcado de S02-6 (tras el 2026-12-10). *Texto anterior:* decide la vuelta de TI-09-ARCH y corrige un dato que hoy planifican TSFM (TS-16-QCONO, TS-08-DYN); minutos de trabajo\
> **Responsable:** raíz del laboratorio; puerta de usuario (token `sub:` de lectura de qn, el mismo de S02-6)\
> **Seguimiento:** TI-09-SONDA en [PLAN_ARCHIVO_OPCIONES.md](../../backlog/PLAN_ARCHIVO_OPCIONES.md); SPRINT-03 fila 3

**Snapshot al cierre de SPRINT-01 (2026-11-09, NO RESUELTA):** [archive/SPRINT-01_2026-11-07_2026-11-09/issues/ISSUE-TI09-SONDA-CADENAS.md](../../archive/SPRINT-01_2026-11-07_2026-11-09/issues/ISSUE-TI09-SONDA-CADENAS.md)

---

## 1. Contexto y comportamiento observado

- Dicen «vacías»: [STATUS.md](../../STATUS.md) fila «Datos» y SPRINT-01 §6 del laboratorio (2026-11-08, TI-01-INV), y
  `quantdesk/docs/plans/backlog/PLAN_TSFM_FINANZAS.md` §3 (2026-11-09).
- Dice «se publica»: `quantdesk-backend/docs/plans/current/EXECUTION.md` (2026-11-09, run `157c2754`, `SUCCESS`,
  `options_chain_coverage_ratio` 0,998 en `market.options.chain`).
- Nadie lo ha comprobado leyendo el lago; el 2026-11-07 ya hubo un «Published N» que no enviaba nada.

## 2. Divergencia respecto a la especificación

Los documentos de estado deben reflejar lo que hay en el lago (SPRINT_PROJECT, STATUS). Hoy se contradicen.

## 3. Caso mínimo reproducible

`.venv/Scripts/python -X utf8 scripts/inventario_options_chain.py` con el token de lectura del usuario en el entorno
(nunca en el repo ni en el chat), sobre `market.options.chain` y `market.options.fx` en `main` desde el 2026-11-09.

## 4. Análisis de causa raíz

No hay defecto de código conocido: el inventario de TI-01-INV es del 2026-11-08 y el backend reanudó la publicación el
2026-11-09 (ISSUE-OPTIONS-JOBS-PARADOS del backend).

## 5. Criterios de aceptación y resolución

- [ ] 1. Cifra por día hábil desde el 2026-11-09: filas, subyacentes distintos, vencimientos y hora de captura, con la
  consulta reproducible y su salida guardada.
- [ ] 2. Corregidos con esa cifra: fila «Datos» de STATUS.md; fila 3 y §6 de SPRINT-01 (o su dossier si ya cerró).
  `PLAN_TSFM_FINANZAS` §3 lo corrige su dueño (`quantdesk`), con aviso.
- [ ] 3. Ningún token en el repo, informes ni chat.
- No aplican test de regresión, rendimiento ni paridad: es una medición sin cambio de código.

## 6. Resolución y verificación

- **Sprint de resolución:** Fuera de sprint.
- **Fecha de resolución:** pendiente.
- **Commit(s) / diagnóstico:** pendiente.
- **Verificación:** pendiente.
- **Pendientes:** todos.

## Revisión de planes (2026-11-13)

Veredicto: **ACTUALIZAR y CERRAR condicionado** (GAP-ISSUES-01) · Motivo: la pregunta de fondo («¿hay cadenas en qn?») ya
está contestada con datos desde el 2026-11-13, pero los criterios 1 y 2 siguen sin cumplirse a la letra y la cifra por
día hábil desde el 2026-11-09 tiene hoy poco valor (el lector sólo usa sesiones con `capture_id`, corte 2026-11-12).

Evidencia nueva (no estaba en la ficha):

- **Sonda de contraste del 2026-11-13** ([EXECUTION de SPRINT-02](../../archive/SPRINT-02_2026-11-11_2026-11-13/EXECUTION.md),
  fila `2026-11-13 TI-09-ARCH (6)` «Sonda de contraste»): token `ti09arch-lectura-20261113` (id 39, `main`, lectura de
  `market.options.chain` y `market.options.fx`), emitido 04:36Z y revocado 04:38Z. `market.options.chain` **tiene
  datos** (/latest 509 símbolos: 502 EQUITY, 4 ETF, 3 INDEX; 1018 de 1022 combinaciones con `capture_id`);
  `market.options.fx` **sin filas**. Es una sonda de agregados fuera del repo, **no** la salida de
  `inventario_options_chain.py`.
- **Primer dataset real** `oc03_s20261112_c20261113` (`sha256:eb98ac6a…eea1`, `E:/quantdesk-lab/datasets/TI-09-ARCH/`):
  sesión NY 2026-11-12, 431.681 filas crudas (= cifra del aviso del backend), 509 subyacentes; descartes del volcado:
  37.278 sin `capture_id` (camino viejo) y 12.797 anteriores a OC-03 (es decir, **hay capturas anteriores en el lago**,
  sin cifra por día).
- `scripts/inventario_options_chain.py` existe y su selftest pasa (suite del DoD de SPRINT-02 sobre `fb5d21f`, 14 OK,
  `E:/quantdesk-lab/tmp/verif_cierre_s02_fb5d21f.log`). El comando del §3 sin argumentos recorre **todo** `market.*`: para
  esta sonda hay que acotarlo (`--topics "market.options.*" --desde 2026-11-09 --json … --informe …`). SIN VERIFICAR: el
  coste de leer todas las capturas (≈ 430 000 filas por sesión) con ese script; la sonda del 13-nov usó agregados.

Estado por criterio:

| Criterio | Clasificación | Evidencia / qué falta |
|---|---|---|
| 1. Cifra por día hábil desde 2026-11-09 | VIGENTE (no hecho) | Sólo hay cifra de la sesión 2026-11-12 (dataset) y agregados de /latest; falta la serie por día con consulta reproducible y salida guardada. Puerta: token de lectura nuevo (el del 13-nov está revocado) |
| 2. Corregir STATUS, SPRINT-01 y `PLAN_TSFM_FINANZAS` §3 | MODIFICADO | SPRINT-01 es archivo inmutable: no se reescribe (ya decidido); STATUS.md fila «Lago de qn» sigue diciendo «vacíos» (la rehace el orquestador); `quantdesk/…/PLAN_TSFM_FINANZAS.md` §3 sigue diciendo «ni una fila» (l. 115): lo corrige su dueño con aviso |
| 3. Ningún token en repo, informes ni chat | VIGENTE (cumplido hasta hoy) | Tokens 38–40 revocados el mismo día; búsqueda de patrón `qn_` = 0 en los volcados (EXECUTION, 2026-11-13). Se vuelve a comprobar al ejecutar |

Opciones (GAP-ISSUES-01): (a) cerrar ya con el alcance reducido «hay cadenas; la cifra por sesión NY la da S02-6 desde
2026-11-12», tras corregir STATUS y avisar a quantdesk; (b) cifra literal desde 2026-11-09 en la misma sesión de token
que S02-6 (tras 2026-12-10): `inventario_options_chain.py --topics "market.options.*" --desde 2026-11-09`; (c) dejar el
criterio 1 como está y esperar. Recomendación: (a) y, si se quiere la cifra literal, (b) sin token adicional.

**Decisión (usuario, 2026-11-13, revisión de planes, R4):** la ficha se cierra con la **cifra por sesión de S02-6 desde
el 2026-11-12**; los días 2026-11-09…11 (régimen sin `capture_id`) quedan documentados como **no medibles**
(GAP-ISSUES-01 y GAP-ARCHIVO_OPCIONES-04 resueltos así). Sigue viva hasta que S02-6 dé la cifra; su fila se une a S02-6
(SPRINT-03 fila 3). Criterio 1 reformulado en consecuencia: «cifra por sesión NY desde el 2026-11-12 (filas,
subyacentes, vencimientos, `capture_id`) con la consulta y su salida guardadas; 2026-11-09…11 declarados no medibles».
Criterio 2: STATUS.md (fila «Lago de qn») corregido el 2026-11-13 en la aplicación de la revisión (hay cadenas en qn
desde la sesión 2026-11-12; `market.options.fx` vacío); el aviso a `quantdesk` para su `PLAN_TSFM_FINANZAS` §3 lo da la
raíz por mensaje (no se edita desde aquí); SPRINT-01 no se reescribe.
