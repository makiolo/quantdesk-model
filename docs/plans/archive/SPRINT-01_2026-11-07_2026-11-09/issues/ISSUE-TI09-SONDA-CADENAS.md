**NO RESUELTA** (pendiente al cierre de SPRINT-01, 2026-11-09). Snapshot congelado; la ficha viva es [issues/ISSUE-TI09-SONDA-CADENAS.md](../../../issues/ISSUE-TI09-SONDA-CADENAS.md).

# [ISSUE-TI09-SONDA-CADENAS] ¿Hay cadenas de opciones en qn? Sonda de sólo lectura

> **Tipo:** Incidencia\
> **Estado:** Abierto\
> **Fecha de detección:** 2026-11-09\
> **Origen:** Fuera de sprint (revisión de planes 2026-11-09, contradicción C-07; decisión del usuario «Sonda de sólo lectura», 2026-11-09)\
> **Componente afectado:** documentación de estado del laboratorio (STATUS, SPRINT-01) y lectura de `market.options.chain` en qn\
> **Especificación de referencia:** [PLAN_ARCHIVO_OPCIONES.md](../../../backlog/PLAN_ARCHIVO_OPCIONES.md) §3, tarea TI-09-SONDA\
> **Severidad:** Media\
> **Destino:** Fuera de sprint — urgente\
> **Prioridad y motivo:** decide la vuelta de TI-09-ARCH y corrige un dato que hoy planifican TSFM (TS-16-QCONO, TS-08-DYN); minutos de trabajo\
> **Responsable:** raíz del laboratorio; puerta de usuario (token `sub:` de lectura de qn)\
> **Seguimiento:** TI-09-SONDA en [PLAN_ARCHIVO_OPCIONES.md](../../../backlog/PLAN_ARCHIVO_OPCIONES.md)

---

## 1. Contexto y comportamiento observado

- Dicen «vacías»: [STATUS.md](../../../STATUS.md) fila «Datos» y SPRINT-01 §6 del laboratorio (2026-11-08, TI-01-INV), y
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
