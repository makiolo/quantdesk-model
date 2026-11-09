# Registro de revisiones del backlog — quantdesk-model

Una entrada por revisión, la más reciente arriba (skill `sprint`, `references/review.md` §7).

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
