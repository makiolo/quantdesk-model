# [ISSUE-TI12-MT5-INTRADIA-LOCAL] Guardar en local el 1m y 5m de MT5 antes de que el bróker lo pierda

> **Tipo:** Mejora\
> **Estado:** Abierto\
> **Fecha de detección:** 2026-11-09\
> **Origen:** Fuera de sprint (revisión de planes 2026-11-09, GAP-BACKLOG_README-04 = GAP-TSFM-04; decisión del usuario «Guardar local ya», 2026-11-09)\
> **Componente afectado:** `scripts/extractor_mt5.py` y almacén `E:/quantdesk-lab/data/mt5/`\
> **Especificación de referencia:** [PLAN_DATOS_VIA_QN.md](../backlog/PLAN_DATOS_VIA_QN.md) §2, tarea TI-12-MT5-INTRA-LOCAL\
> **Severidad:** Media\
> **Destino:** Sprint siguiente seleccionado: SPRINT-03 (next), fila 4b, fusionada operativamente con S02-5 (fila 4a; mutex del terminal MT5) ([next/SPRINT.md](../next/SPRINT.md); usuario, 2026-11-13, revisión de planes, R8). Antes: «Fuera de sprint — urgente»\
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
      **El incremental es fuera de sprint, ya, en esta ficha** (usuario, 2026-11-10, revisión de planes, D3): la fila 5 de
      [current/SPRINT.md](../archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md) se reduce a «más símbolos y periodos» y ya no lo recoge.
- [x] 3. Manifiesto con símbolo, periodo, primera y última barra, filas y hash. *(Revisión 2026-11-13: HECHO,
      `E:/quantdesk-lab/data/mt5/continuo_m1m5_20261109/manifest.json`.)*
- [ ] 4. Periodicidad que no pierda barras de 1m por `maxbars` (documentada; si es una tarea programada, la registra el usuario).
- [x] 5. Nada se publica en qn y el extractor no envía órdenes; credenciales fuera del repo y del chat. *(Revisión
      2026-11-13: HECHO; el selftest del extractor prohíbe las funciones de órdenes, `extractor_mt5_lib/selftests.py:40`,
      y no hay ningún uso en `scripts/`.)*
- [ ] 6. **Acciones (D3b, usuario, 2026-11-10, revisión de planes):** medir la profundidad y el volumen de m1 y m5 de las
      484 acciones de `@us_grandes` con el inventario del extractor (`--simular`, sólo lectura) *[corrección 2026-11-13:
      `--simular` es del publicador; el extractor usa `extractor_mt5.py --inventario --grupo @us_grandes`, que sí abre el
      terminal MT5: queda tras el desbloqueo de la cuenta]* y anotar la cifra aquí;
      incluirlas en esta descarga si la cifra es razonable frente al presupuesto de disco de 100 GB (el continuo gastó
      1,2 GiB), y si no, dejarlo escrito con el motivo. Las 13 de sólo `-24` quedan fuera de la medición salvo que la
      cifra lo aconseje.

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
  - Criterio 6: medir las acciones con `--simular` y decidir con la cifra (D3b). Hasta entonces las acciones no tienen
    intradía local y, si el bróker les aplica el mismo tope de ~100 000 barras, su profundidad se va perdiendo (SIN
    VERIFICAR: no medido).
  - La publicación en qn se pide al planificar SPRINT-04 del laboratorio.

## Revisión de planes (2026-11-13)

Veredicto: **ACTUALIZAR y A SPRINT-03 §0** (como encargo que no espera a quantdesk, igual que S02-5 y S02-6; GAP-ISSUES-03)
· Motivo: no hay nada más que hacer sin MT5 y la cuenta está bloqueada; el código del incremental ya existe y está
probado, falta ejercerlo sobre datos reales, fijar la periodicidad y decidir las acciones. No se cierra.

Qué cambió desde el 2026-11-10:

- **Cuenta bloqueada.** Todas las pasadas del publicador del 2026-11-11, 11-12 y 11-13 acaban `bloqueado: initialize(...)
  fallo (-6, 'Terminal: Authorization failed')` (`E:/quantdesk-lab/runs/TI-12-MT5/publicador/publicador_2026-11-1{1,2,3}.jsonl`,
  `ultimo.json`). Mientras siga así no hay descargas (S02-5 comparte la puerta; mutex del terminal con esta ficha).
- **Sólo existe la descarga del 2026-11-09** en `E:/quantdesk-lab/data/mt5/` (`continuo_m1m5_20261109`,
  `fx28_m1_20261109` y `_rep`, `continuo_1d`, `us_grandes*_1d`): no se ha hecho ninguna incremental ni medido ninguna
  acción desde entonces.
- **Urgencia real (estimación, SIN VERIFICAR con el bróker):** lo ya bajado queda en la caché `data/mt5/_trozos/`; lo que
  se perdería es lo que el bróker deje caer *antes* de la próxima descarga. Con `maxbars` 100 000, el m1 de cripto 24x7
  (1440 barras/día) cubre unos 69 días: la última barra local es del 2026-11-09, así que **para no abrir hueco en el m1
  de cripto hay que repetir la descarga antes de mediados de enero de 2027**; FX (5 d/semana) tiene unas 14 semanas, y
  la mediana de primera barra m1 de `@continuo` era 2026-08-04. No es urgencia de días; sí hay fecha límite.
- **Volumen de las acciones (cota, SIN VERIFICAR):** `@continuo` m1+m5 = 37.944.660 filas en 1246,7 MiB (≈ 34 B/fila).
  484 acciones × 2 periodos × 100 000 barras como máximo = 96,8 M filas ≈ 3,1 GiB, muy por debajo de los 100 GB. El
  presupuesto de disco no es la razón para dejarlas fuera; lo es el ritmo de peticiones (la cuenta ya se bloqueó una vez).

Estado por criterio:

| Criterio | Clasificación | Evidencia / qué falta |
|---|---|---|
| 1. Mismo SHA-256 en dos descargas | VIGENTE, parcial | Hecho en fx28 m1 (`fdfa3a7`, `fx28_m1_20261109` y `_rep`) y en el selftest con `--refrescar` (`extractor_mt5_lib/selftests.py:757-764`: mismos bytes y `hash_conjunto`); falta sobre `@continuo` completo (descarga real, cuenta bloqueada) |
| 2. Reanudable e incremental | VIGENTE, parcial | **Código HECHO y probado**: `extractor_mt5_lib/descarga.py:8-9` (reanudar = repetir la orden; incremental = otro `--hasta` reutiliza los trozos cerrados) y selftest `:767-781` (23 trozos reutilizados tras fallo; `trozos_reutilizados` = 4×12 con un día más). Falta ejercerlo sobre `@continuo` real y comprobar «sin huecos salvo fines de semana y festivos» en el manifiesto |
| 3. Manifiesto | HECHO | `continuo_m1m5_20261109/manifest.json` |
| 4. Periodicidad documentada | VIGENTE | Nada escrito. Propuesta: repetir la misma orden con `--hasta` nuevo cada ≤ 6 semanas (margen sobre las ~10 semanas de m1 cripto) o tarea programada que registra el usuario; decide GAP-ISSUES-03 |
| 5. Sin publicar ni órdenes | HECHO | Selftest de funciones prohibidas; sin uso en `scripts/` |
| 6. Medir las 484 acciones (D3b) | MODIFICADO (comando corregido) | No medido. Necesita MT5 (`--inventario`), tras el desbloqueo y a ritmo prudente. Con la cota de arriba, lo razonable es medir con una sola consulta por símbolo y periodo y decidir con la cifra |

Solape: S02-5 (h1 de `@continuo`) y esta ficha usan el mismo extractor y el mismo terminal. Recomendación: **una sola
sesión de descarga** tras el desbloqueo, con orden m1+m5 incremental primero (lo que caduca), después h1 nuevo y, al
final, las acciones. Lo que pida la ficha de S02-5 como «reanudación sin duplicados» se acepta aquí (criterio 2).

**Decisión (usuario, 2026-11-13, revisión de planes, R8):** alcance **fx28 y `@continuo` primero**, después las **484
acciones de `@us_grandes`** (≈ 3,1 GiB), una serie cada vez (descargas prudentes); pasadas **manuales cada ≤ 6
semanas**, la primera **antes del 2027-01-17**; **sin tarea programada** (GAP-ISSUES-04 y D3b resueltos). Espera al
desbloqueo de la cuenta. Va como fila 4b del SPRINT-03 nuevo (no depende de `quantdesk`), fusionada operativamente con
S02-5 (mutex del terminal MT5). Criterio 4 queda fijado así («manual, ≤ 6 semanas»); criterio 6: medir con
`extractor_mt5.py --inventario --grupo @us_grandes` e incluirlas tras fx28 y `@continuo` (C-09 y C-ISSUES-03 resueltas
por regla: el incremental ya existe en el extractor y `--simular` es del publicador).
