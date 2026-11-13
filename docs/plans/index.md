# Tablero de planes — quantdesk-model

Toda evolución sustancial se rige por un documento de plan antes de tocar código de producción. El
trabajo se organiza en sprints, gestionados por las skills globales `sprint`, `execute-plan` y
`como-vas`; los datos propios del proyecto están en [SPRINT_PROJECT.md](SPRINT_PROJECT.md).

## Convención

- **[current/](current/)**: sprint activo (`SPRINT.md`, planes de grupo, LAUNCH, USAGE, issues).
- **[next/](next/)**: el próximo sprint en preparación. Prepararlo no lo activa.
- **[future/](future/README.md)**: sprints posteriores, uno por carpeta (`future/SPRINT-NN/SPRINT.md`).
  Al activar next, `future/SPRINT-(n+1)` se promueve a next.
- **[backlog/](backlog/README.md)**: planes futuros sin sprint asignado.
- **[issues/](issues/index.md)**: incidencias vivas fuera de sprint ([plantilla](issues/TEMPLATE_ISSUE.md)).
- **[usage/](usage/README.md)**: registro global de cuota y costes ([protocolo](USAGE_PROTOCOL.md)); nunca se mueve.
- **[archive/](archive/index.md)**: dossier completo de cada sprint cerrado (`SPRINT-NN_<inicio>_<fin>/`).
- **[DEPENDENCIAS.md](DEPENDENCIAS.md)**: dependencias de nuestros sprints con sprints de otros
  proyectos; `/sprint deps` muestra el grafo y qué está listo para empezar.
- **[arnes/](arnes/README.md)**: arnés de ejecución y arranque de los relevos de la raíz.
- **[STATUS.md](STATUS.md)**: estado global vivo.

Ciclo: planificación → inicio → ejecución → cierre y archivo → freeze → release → planificación.

## Estado

| Fase | Sprint | Enlace |
|---|---|---|
| Activo | **SPRINT-03** desde el 2026-11-14 — Exportador diario, operación de MT5 y cobertura de cadenas, **sin dependencia de entrada** (rehecho por partición, usuario, 2026-11-13, R1): TI-02-DIARIO (contrato primero, código sin OAS, OAS después), S02-6 con el cierre de la sonda, fila de MT5 (S02-5, INTRA-LOCAL, reactivación del publicador y carga de `@continuo`), universo ampliado condicionado, consumo FRED/OAS | [current/SPRINT.md](current/SPRINT.md) |
| Próximo | SPRINT-04 — Ciclo sintético-real y procedencia en el manifiesto (en planificación; espera a quantdesk SPRINT-03 cerrado) | [next/SPRINT.md](next/SPRINT.md) |
| Issues del sprint activo | ISSUE-TI09-SONDA-CADENAS (fila 3), ISSUE-TI12-MT5-INTRADIA-LOCAL (fila 4b). Resueltas el 2026-11-13: ISSUE-TI12-MT5-SYNC y VELA-A-MEDIAS (R3) | [current/issues/](current/issues/index.md) · [FUERA-SPRINT_2026-11-09_2026-11-13](archive/FUERA-SPRINT_2026-11-09_2026-11-13/ARCHIVE_MANIFEST.md) |
| Futuros | SPRINT-04 — Ciclo sintético-real y procedencia en el manifiesto, con las filas S02-1…S02-4 (tras quantdesk SPRINT-03); SPRINT-05 — Escalera de entrenamiento (antes SPRINT-04; tras quantdesk SPRINT-04) | [future/](future/README.md) · [DEPENDENCIAS](DEPENDENCIAS.md) |
| Último cerrado | SPRINT-02 — Datos MT5 vía qn, FinCast y ampliación de datos (2026-11-11 a 2026-11-13), cerrado con arrastres y archivado | [archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md](archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md) · [archive/](archive/index.md) |

## Backlog

| Plan | Ámbito | Estado | Descripción |
|---|---|---|---|
| [Backlog del laboratorio](backlog/README.md) | Índice, regla de separación, estado de las tareas ya en sprint (TS-00-*, TS-02-DISC, ejecuciones de entrenamiento) y calendario del laboratorio | SPRINT-01 y SPRINT-02 cerrados; lo pendiente en SPRINT-03 (sin dependencia de entrada), SPRINT-04 y SPRINT-05; sin sprint sólo el consumo de Yahoo/Stooq y cripto y la política de dos publicadores | Antes en `docs/plans/BACKLOG.md` (ahora puntero). Especificación en los planes de `quantdesk` (sólo lectura). Dividido el 2026-11-09 (usuario); puesto al día el 2026-11-10 y el 2026-11-13 con las decisiones de la revisión de planes (usuario, 2026-11-13, R0–R8) |
| [PLAN_ARCHIVO_OPCIONES](backlog/PLAN_ARCHIVO_OPCIONES.md) | TI-09-ARCH (parte laboratorio), TI-09-SONDA, retención (sin copia propia: copia común de network) | Backlog residual: parte de laboratorio entregada en SPRINT-02; medición de cobertura (S02-6) y cierre de la sonda en SPRINT-03 fila 3 (R4); se archiva al cerrar S02-6 (no antes del 2026-12-11) | Lector del lago de `market.options.chain` con hash; OC-03 servida; GAP-ARCHIVO_OPCIONES-03 y -05 diferidos |
| [PLAN_DATOS_VIA_QN](backlog/PLAN_DATOS_VIA_QN.md) | TI-12-MT5 (fase C, intradía, INTRA-LOCAL, tarea programada, SYNC), TI-13-PUB (consumo: FRED/OAS y Yahoo/Stooq/cripto), TI-02-DATA-V2, TI-02-DIARIO | Fase C (1d local) cerrada en SPRINT-01; TI-02-DATA-V2 cerrada en SPRINT-02; SYNC cerrada (R3); en SPRINT-03: TI-02-DIARIO (filas 1, 2, 7), fila de MT5 (4a–4c), universo ampliado condicionado (5), FRED/OAS (6); intradía en qn con SPRINT-05 (R7); Yahoo/Stooq y cripto en backlog (R6) | Datos de mercado sólo por publicadores y consumo vía qn (A16 bis); Binance como corpus congelado; publicador MT5 desactivado hasta el desbloqueo (R2) |

## 🧭 Tablero Kanban de Planes

Generado desde `docs/plans`: backlog, próximos sprints, sprint activo con el progreso de cada plan, sprints cerrados e issues abiertas.

<!-- kanban:inicio -->
<!-- Generado por `sprint_db.py kanban --write` (skill global sprint); no editar a mano: se regenera. -->

```mermaid
graph LR
    classDef backlog fill:#eceff1,stroke:#607d8b,stroke-width:2px;
    classDef next fill:#fff8e1,stroke:#ffa000,stroke-width:2px;
    classDef current fill:#e3f2fd,stroke:#1976d2,stroke-width:2px;
    classDef completed fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef issues fill:#fff3e0,stroke:#f57c00,stroke-width:2px;

    subgraph B["📌 1. Backlog (futuros)"]
        B1["PLAN_ARCHIVO_OPCIONES<br/>Archivo de cadenas de opciones del laboratorio (TI-09-ARCH)"]:::backlog
        B2["PLAN_DATOS_VIA_QN<br/>Datos de mercado vía qn (MT5, publicadores públicos, export…"]:::backlog
    end

    subgraph N["⏳ 2. Próximos (next y future)"]
        N1["SPRINT-04<br/>Ciclo sintético-real y procedencia en el manifiesto · En planificación"]:::next
        N2["SPRINT-05<br/>Escalera de entrenamiento, ajuste fino y adaptadores · En planificación"]:::next
    end

    subgraph C["📦 3. SPRINT-03 activo"]
        C1["SPRINT-03<br/>Exportador diario, operación de MT5 y cobertura de cadenas… · 0/8 cerradas"]:::current
        C2["PLAN_DATOS_VIA_QN<br/>Datos de mercado vía qn (MT5, publicadores públicos, export…"]:::current
        C3["PLAN_ARCHIVO_OPCIONES<br/>Archivo de cadenas de opciones del laboratorio (TI-09-ARCH)"]:::current
        C1 --> C2
        C1 --> C3
    end

    subgraph D["✅ 4. Sprints cerrados"]
        D1["SPRINT-01<br/>Entorno, datos reales y banco de referencia · Cerrado"]:::completed
        D2["SPRINT-02<br/>Datos MT5 vía qn, FinCast y ampliación de datos · Cerrado con arrastres"]:::completed
    end

    subgraph P["⚠️ 5. Issues abiertas"]
        P1["ISSUE-TI09-SONDA-CADENAS<br/>¿Hay cadenas de opciones en qn? Sonda de sólo lectura · Abierto"]:::issues
        P2["ISSUE-TI12-MT5-INTRADIA-LOCAL<br/>Guardar en local el 1m y 5m de MT5 antes de que el bróker l… · Abierto"]:::issues
    end

    B --> N
    N --> C
    C --> D
    D --> P

    click B1 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/backlog/PLAN_ARCHIVO_OPCIONES.md" _blank
    click B2 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/backlog/PLAN_DATOS_VIA_QN.md" _blank
    click N1 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/next/SPRINT.md" _blank
    click N2 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/future/SPRINT-05/SPRINT.md" _blank
    click C1 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/current/SPRINT.md" _blank
    click C2 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/backlog/PLAN_DATOS_VIA_QN.md" _blank
    click C3 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/backlog/PLAN_ARCHIVO_OPCIONES.md" _blank
    click D1 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md" _blank
    click D2 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md" _blank
    click P1 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/current/issues/ISSUE-TI09-SONDA-CADENAS.md" _blank
    click P2 href "https://github.com/makiolo/quantdesk-model/blob/main/docs/plans/current/issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md" _blank
```

<details><summary>Enlaces de los planes e issues</summary>

**📌 Backlog (futuros)**

- [PLAN_ARCHIVO_OPCIONES](backlog/PLAN_ARCHIVO_OPCIONES.md) — Archivo de cadenas de opciones del laboratorio (TI-09-ARCH)
- [PLAN_DATOS_VIA_QN](backlog/PLAN_DATOS_VIA_QN.md) — Datos de mercado vía qn (MT5, publicadores públicos, export…

**⏳ Próximos (next y future)**

- [SPRINT-04](next/SPRINT.md) — Ciclo sintético-real y procedencia en el manifiesto
- [SPRINT-05](future/SPRINT-05/SPRINT.md) — Escalera de entrenamiento, ajuste fino y adaptadores

**📦 SPRINT-03 activo**

- [SPRINT-03](current/SPRINT.md) — Exportador diario, operación de MT5 y cobertura de cadenas…
  - [PLAN_DATOS_VIA_QN](backlog/PLAN_DATOS_VIA_QN.md) — Datos de mercado vía qn (MT5, publicadores públicos, export…
  - [PLAN_ARCHIVO_OPCIONES](backlog/PLAN_ARCHIVO_OPCIONES.md) — Archivo de cadenas de opciones del laboratorio (TI-09-ARCH)

**✅ Sprints cerrados**

- [SPRINT-01](archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md) — Entorno, datos reales y banco de referencia
- [SPRINT-02](archive/SPRINT-02_2026-11-11_2026-11-13/SPRINT.md) — Datos MT5 vía qn, FinCast y ampliación de datos

**⚠️ Issues abiertas**

- [ISSUE-TI09-SONDA-CADENAS](current/issues/ISSUE-TI09-SONDA-CADENAS.md) — ¿Hay cadenas de opciones en qn? Sonda de sólo lectura
- [ISSUE-TI12-MT5-INTRADIA-LOCAL](current/issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md) — Guardar en local el 1m y 5m de MT5 antes de que el bróker l…

</details>
<!-- kanban:fin -->
