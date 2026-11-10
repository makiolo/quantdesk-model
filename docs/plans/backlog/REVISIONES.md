# Registro de revisiones del backlog — quantdesk-model

Una entrada por revisión, la más reciente arriba (skill `sprint`, `references/review.md` §7).

## 2026-11-10 — revisión parcial (quantdesk, quantdesk-backend, quantdesk-model)

- Documentos: 7 en total (7 revisores Sonnet 5.5, uno por documento); 3 de este repo: `backlog/README.md`,
  `backlog/PLAN_DATOS_VIA_QN.md` y `backlog/PLAN_ARCHIVO_OPCIONES.md`.
- Veredictos: este repo, 3 ACTUALIZAR (0 mantener, 0 borrar, 0 fusionar, 0 dividir, 0 mover); global, 7 ACTUALIZAR.
- Decisiones del usuario que tocan este repo (usuario, 2026-11-10, revisión de planes):
  - **D1** republicar y aplazar: ficha urgente fuera de sprint [ISSUE-TI12-MT5-SYNC](../issues/ISSUE-TI12-MT5-SYNC.md)
    (publicar el 1d sólo con la historia D1 sincronizada, modo de reenvío, se aprueban las 23 republicaciones de las velas
    1d de FX del 2026-11-09, carga nocturna de `@continuo` aplazada hasta cerrarla, verificar el horizonte de revisión de
    qn (H2, ~6 h) y pedir excepción a network si venció). Relacionada con ISSUE-TI12-MT5-VELA-A-MEDIAS (guarda ya escrita),
    que se fusionará con ella al cerrar.
  - **D2** SPRINT-02 del laboratorio: fila 1b nueva en `next/SPRINT.md` (TI-02-DATA-V2 y repetición de la tabla FX sobre
    MT5 1d), de la que dependen las filas 2, 4 y 7; `ISSUE-LAGO-FX-1D-CLOSE` remite a ella.
  - **D3** el incremental reanudable de MT5 se hace ya, fuera de sprint, en `ISSUE-TI12-MT5-INTRADIA-LOCAL`; la fila 5 de
    `next/SPRINT.md` queda en «más símbolos y periodos». **D3b** medir con `--simular` las 484 acciones de `@us_grandes` y
    decidir con la cifra (presupuesto 100 GB).
  - **D6** TI-02-DIARIO: el laboratorio escribe el código, el backend lo programa en Dagster tras el cierre de Nueva York
    (SPRINT-03 del backend, D5); fila de dueños en `GOBERNANZA.md`.
  - **D7** copia común de network: sin copia propia del laboratorio ni del backend; el laboratorio sólo guarda lo leído al
    cortar cada dataset, con hash; `lake delete` no sobre `market.*` hasta que exista la copia común. **D11** se quita el
    «subyacente del OHLCV diario» como spot de respaldo: sólo `underlying_price` de OC-03.
  - **D13** FinCast sólo en CRPS y QLIKE sobre la ventana limpia, nunca en colas (fila 2b). **D15** la repetición de la
    tabla FX en dos tablas: cabecera (misma ventana y rejilla, desde 2024-11) y ampliación (MT5 1d desde 2000, sin mover
    umbrales).
- GAPs resueltos (todos «usuario, 2026-11-10, revisión de planes»): GAP-BACKLOG_README-01 (opción (c), D11), -07 (D2),
  -08 (D1); GAP-DATOS_VIA_QN-01 (D6), -02 (D2), -03 (D1), -04 (D3b); GAP-ARCHIVO_OPCIONES-01 y -02 (D7).
- GAPs abiertos: GAP-BACKLOG_README-03 (dos publicadores en acciones US y cripto) y GAP-BACKLOG_README-05 (GPU,
  diferido). De otros repos y diferidos (no de este): GAP-PUB-08 (ajuste Yahoo/Stooq), C-FOC-01 (claves FRED) y la parte
  «comprar historia u otra fuente» de D4.
- Contradicciones y su resolución:
  - C-BACKLOG_README-08 y C-DATOS_VIA_QN-01 (la ficha del FX remitía a una fila que no contenía su trabajo) → D2, fila 1b.
  - C-DATOS_VIA_QN-02 (noche 1 programada frente a aplazada) → D1.
  - C-DATOS_VIA_QN-03 (incremental en tres sitios) → D3.
  - C-ARCHIVO_OPCIONES-01 (spot de respaldo que no está en el lago) → D11.
  - Por regla, sin pregunta: C-BACKLOG_README-06 (enlaces de `quantdesk` al archivo de SPRINT-01; los repunta el
    aplicador de `quantdesk`), C-BACKLOG_README-07 y C-DATOS_VIA_QN-04 (derivados del laboratorio al día),
    C-ARCHIVO_OPCIONES-02 (las filas anteriores a OC-03 no tienen `captured_at`; el lector deriva la sesión desde `_ts`;
    la frase de OC-03(b) se corrige en el plan del backend) y C-ARCHIVO_OPCIONES-03 (el archivo de SPRINT-01 no se
    reescribe; la cifra de la sonda va a la ficha y a STATUS).
- Derivados: `index.md` (tablas de estado y backlog; el bloque kanban es generado y se regenera aparte), `issues/index.md`,
  `DEPENDENCIAS.md` (filas de TI-09-ARCH, TI-02-DIARIO y TI-12-MT5-SYNC), `GOBERNANZA.md` (copia común y exportador
  diario), `next/SPRINT.md` (filas 1b, 2, 2b, 4, 5, 7), fichas `ISSUE-LAGO-FX-1D-CLOSE` e `ISSUE-TI12-MT5-INTRADIA-LOCAL`.
- Commits: `docs(plans): revisión de planes 2026-11-10 (parcial)` en quantdesk, quantdesk-backend, quantdesk-model y quantdesk-network (mismo título en los cuatro repos).

## 2026-11-09 — revisión general (quantdesk, quantdesk-backend, quantdesk-model, quantdesk-network)

- Documentos: 1 en este repo (`backlog/README.md`) de 29 en total (un subagente por documento).
- Veredictos (este repo): 0 mantener · 1 actualizar · 0 borrar · 0 fusionar · 1 dividir · 0 mover (TI-13-PUB
  mercado público se mueve al backend como tarea, no como plan).
- División aplicada (usuario, 2026-11-09): `backlog/README.md` queda como índice, regla y calendario del laboratorio
  (listas «Q» sustituidas por enlace a `quantdesk/docs/plans/next/README.md`; ruta y ancla `#21-comprobaciones-2026-11-07`
  conservadas); nuevos [PLAN_ARCHIVO_OPCIONES.md](PLAN_ARCHIVO_OPCIONES.md) (TI-09-ARCH, TI-09-SONDA) y
  [PLAN_DATOS_VIA_QN.md](PLAN_DATOS_VIA_QN.md) (TI-12-MT5, TI-13-PUB mercado público, TI-02-DATA-V2, TI-02-DIARIO).
- Decisiones del usuario aplicadas aquí:
  - C-07 cadenas en qn: sonda de sólo lectura (TI-09-SONDA, ficha `issues/ISSUE-TI09-SONDA-CADENAS.md`); con la cifra se
    corrigen STATUS y SPRINT-01.
  - C-12 exportador: `descarga_lago.py` sólo v2 (TI-02-DATA-V2 al backlog); los datasets antiguos se regeneran desde
    `0e67465`.
  - GAP-TSFM-03 umbral D-08: combinado (CRPS no peor de X % y ganar en colas o QLIKE; X en TS-00-OBJ con Toto).
  - GAP-BACKLOG_README-04 MT5 intradía: 1m y 5m en local ya con hash (TI-12-MT5-INTRA-LOCAL, ficha
    `issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md`); publicar en qn al planificar SPRINT-04.
  - GAP-BACKLOG_README-02 / C-10 publicadores: plan nuevo en el backend `PLAN_PUBLICADORES_MERCADO_PUBLICO`; fila 7 de
    `next/SPRINT.md` pasa a «consumir y exportar lo que publique el backend».
  - C-09 Binance: corpus congelado con hash (excepción a A16 bis).
  - D-I4: exportador diario (TI-02-DIARIO), dueño por decidir (GAP-DATOS_VIA_QN-01).
  - C-13 borrado en el lago: herramienta genérica; rompe 12-A/OCS-02 y el laboratorio planifica copia propia
    (GAP-ARCHIVO_OPCIONES-01).
  - Universo de opciones: 5–10 ETF/índices en el backend; anotado como dependencia de TI-09-ARCH.
- GAPs abiertos: GAP-BACKLOG_README-01 (vuelta de TI-09-ARCH), -03 (dos publicadores en acciones US y cripto), -05
  (GPU para Chronos-2/Toto, diferido), GAP-ARCHIVO_OPCIONES-01 (forma de la copia propia), GAP-DATOS_VIA_QN-01 (dueño
  del exportador diario).
- Contradicciones: C-07 cadenas «vacías» frente a «publicando» → sonda · C-09 Binance directo → corpus congelado ·
  C-10 fila 7 → consumir vía qn · C-12 exportador v1 → sólo v2 · C-13 borrado → herramienta genérica y copia propia ·
  C-26 calendario «Q» copiado → enlace · C-27 dependencias servidas como abiertas → `DEPENDENCIAS.md` actualizado (la
  fila 1 de `next/SPRINT.md`, «en lugar del editable», se corrige al planificar SPRINT-02).
- Derivados: `index.md`, `DEPENDENCIAS.md`, `GOBERNANZA.md`, `issues/index.md`, `next/SPRINT.md` fila 7. Sin portal
  (`mkdocs.yml`) ni `RESUMEN_BACKLOG.md`/`ROADMAP.md` en este repo.
- Commits: pendiente.
