# [ISSUE-TI12-MT5-INTRADIA-LOCAL] Guardar en local el 1m y 5m de MT5 antes de que el bróker lo pierda

> **Tipo:** Mejora\
> **Estado:** Abierto\
> **Fecha de detección:** 2026-11-09\
> **Origen:** Fuera de sprint (revisión de planes 2026-11-09, GAP-BACKLOG_README-04 = GAP-TSFM-04; decisión del usuario «Guardar local ya», 2026-11-09)\
> **Componente afectado:** `scripts/extractor_mt5.py` y almacén `E:/quantdesk-lab/data/mt5/`\
> **Especificación de referencia:** [PLAN_DATOS_VIA_QN.md](../backlog/PLAN_DATOS_VIA_QN.md) §2, tarea TI-12-MT5-INTRA-LOCAL\
> **Severidad:** Media\
> **Destino:** Fuera de sprint — urgente\
> **Prioridad y motivo:** historia irrecuperable: el bróker sólo sirve ~100 000 barras por símbolo y periodo, así que el 1m (hoy desde 2025-11) pierde profundidad cada mes\
> **Responsable:** raíz del laboratorio\
> **Seguimiento:** TI-12-MT5-INTRA-LOCAL en [PLAN_DATOS_VIA_QN.md](../backlog/PLAN_DATOS_VIA_QN.md)

**Snapshot al cierre de SPRINT-01 (2026-11-09, NO RESUELTA):** [archive/SPRINT-01_2026-11-07_2026-11-09/issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md](../archive/SPRINT-01_2026-11-07_2026-11-09/issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md)

---

## 1. Contexto y comportamiento observado

El usuario eligió publicar en qn sólo 1d (2026-11-09). El único consumidor del intradía, TS-05-FREQ, está en SPRINT-04
del laboratorio, y publicar intradía en qn exige antes el visto bueno de network y aviso al backend. Mientras tanto el
bróker va descartando las barras de 1m más antiguas (`maxbars`).

## 2. Divergencia respecto a la especificación

No es una divergencia: es una mejora decidida. Se aparta de «el laboratorio consume siempre vía qn» sólo en el
almacenamiento, no en el consumo (TS-05-FREQ leerá de qn cuando se publique, al planificar SPRINT-04).

## 3. Caso mínimo reproducible

`--simular` del publicador sobre fx28 (2026-11-09): 1h 2,80 M, 5m 0,17 M, 1m 0,83 M barras; m1 sólo desde 2025-11.

## 4. Análisis de causa raíz

Límite del bróker (`maxbars`), no del código: el extractor ya soporta `--intervalos` y descarga reanudable con hash.

## 5. Criterios de aceptación y resolución

- [ ] 1. Dos descargas del mismo rango dan el mismo SHA-256.
- [ ] 2. Reanudable: la siguiente descarga sólo añade barras nuevas, sin huecos salvo fines de semana y festivos del bróker.
- [ ] 3. Manifiesto con símbolo, periodo, primera y última barra, filas y hash.
- [ ] 4. Periodicidad que no pierda barras de 1m por `maxbars` (documentada; si es una tarea programada, la registra el usuario).
- [ ] 5. Nada se publica en qn y el extractor no envía órdenes; credenciales fuera del repo y del chat.

## 6. Resolución y verificación

- **Sprint de resolución:** Fuera de sprint.
- **Fecha de resolución:** pendiente.
- **Commit(s) / diagnóstico:** pendiente.
- **Verificación:** parcial (raíz, 2026-11-09).
  - **Primera descarga completa de `@continuo`** (193 símbolos, m1 y m5, `--sin-credenciales`), terminada a las
    18:33 CET.
    - rc 0: 386 series, 37 944 660 filas y 1246,7 MiB en `E:/quantdesk-lab/data/mt5/continuo_m1m5_20261109`.
    - `hash_conjunto` `sha256:5cd9bf8691bd9d0c5dd5cb0b7328631fb69d52491acc65ddc2b1cdc324e2f9cf`; el manifiesto queda
      en la carpeta (criterio 3).
    - Profundidad de m1: 18,9 M filas. Primera vela: mediana 2026-08-04, la más antigua 2025-11-05.
    - Profundidad de m5: 19,0 M filas. Primera vela: mediana 2025-07-08, la más antigua 2021-11-10.
  - **Criterio 1, en parte:** dos descargas de m1 de fx28 en el mismo rango dieron el mismo hash (`fdfa3a7`,
    `sha256:8a6fa0dc…`, en `execution/TI-12-MT5/cuadre.md` del archivo de SPRINT-01).
- **Pendientes:**
  - Criterio 2: descargas incrementales periódicas (tarea programada o ejecución manual) que sólo añadan barras
    nuevas. Hasta entonces, las barras más viejas del bróker se van perdiendo y conviene repetir la descarga cada
    pocas semanas, a otra `--salida` o reanudando.
  - Criterio 1 sobre `@continuo` completo.
  - La publicación en qn se pide al planificar SPRINT-04 del laboratorio.
