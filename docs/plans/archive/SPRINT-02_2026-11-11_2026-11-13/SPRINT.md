# SPRINT-02 — Datos MT5 vía qn, FinCast y ampliación de datos

**Estado:** Cerrado con arrastres (filas 5 y medición de la 6 a SPRINT-03; fila 7 al backlog). Cierre en §9.
**Inicio de planificación:** 2026-11-07
**Inicio:** 2026-11-11
**Fin:** 2026-11-13
**Orígenes:** etiqueta `archive/2026-11-11/sprint-02-sources` (commit `bb809e4`); planes de backlog del laboratorio
(`PLAN_DATOS_VIA_QN`, `PLAN_ARCHIVO_OPCIONES`) y planes TSFM de `quantdesk` (sólo lectura). Los planes de backlog no
se reducen: sus IDs son más amplios que las filas del sprint y anotan el sprint que los ejecuta.
**Medición:** coordinador de costes, la raíz del LAUNCH. Lectura inicial (`claude-or quota --weekly`,
2026-11-11 07:27 UTC, fuente api): Claude semanal 28 % consumido con el 18,7 % de la ventana (reinicio 2026-11-16
23:59 UTC); Codex semanal 0 %, ventana sin empezar. Cuota compartida con `quantdesk` SPRINT-02 (activo).

> **Partido por decisión del usuario (2026-11-11).** quantdesk SPRINT-02 sigue activo (66 entregas cerradas de unas
> 328 el 2026-11-11), así que la dependencia de sprint de la planificación original no se cumplía. Este sprint se
> queda con las filas que **no** necesitan entregas de quantdesk SPRINT-02 (1b, 2b, 5, 6, 7, con su etiqueta original
> para no romper las referencias de planes y fichas). Las filas 1 (LAB-00-ENV re-fijado), 2 (HMM causal y corpus
> FG-16-hmmcop en el banco), 3 (TS-00-PREC con FG-16-hmmcop) y 4 (cruce con universo59) pasan a
> [SPRINT-03](../../next/SPRINT.md) §0 como filas S02-1…S02-4, con la tabla de entregas de quantdesk que
> consumen. La «cobertura del archivo» de TI-09-ARCH (decisión 12-A: lee del lago, no copia a diario) sigue
> condicionada (fila 6).

## 1. Objetivo

Lo que el laboratorio puede hacer **ya**, sin esperar a quantdesk SPRINT-02: leer sólo `market.ohlcv.v2` con
selección por fuente, repetir la tabla FX del banco sobre el 1d de MT5 (resuelve el close de yfinance desplazado y
confirma o revisa los umbrales provisionales de TS-00-OBJ), añadir FinCast al banco, ampliar MT5 con más símbolos y
periodos y consumir lo que publique el backend. El motor sigue siendo el de la rueda `69fdb39d` de SPRINT-01.

## 2. Responsabilidades y gobernanza

Filas de [GOBERNANZA.md](../../GOBERNANZA.md) que afectan a este sprint (revisadas el 2026-11-11).

| Cosa | Dueño | Escribe | Decide | Cambios desde otro proyecto |
|---|---|---|---|---|
| Backlog, sprints, `.venv`, `requirements.lock`, venvs auxiliares (`E:/quantdesk-lab/venvs/`, FinCast), datasets, informes del banco | quantdesk-model | sesiones del laboratorio | usuario | issue en este repo |
| `PLAN_TSFM_FINANZAS` (umbrales de TS-00-OBJ, D14; FinCast en D-08) | quantdesk (backlog) | el laboratorio registra allí las decisiones del usuario, con enlace al informe | usuario | edición directa del plan; nunca `current/` ni código de quantdesk |
| Rueda `69fdb39d`, `data_py`, bindings HMM | quantdesk | quantdesk | usuario | tarea en el backlog de quantdesk |
| Publicador MT5 → qn `market.ohlcv.v2` y copia local del intradía | quantdesk-model | sesiones del laboratorio | usuario | issue en este repo |
| Publicadores públicos en qn (fila 7) / scraper de cadenas (fila 6) / esquema y retención del lago | backend / backend / network | sus sesiones | usuario | sus planes de backlog |
| Credenciales (MT5, `QN_TOKEN`) | usuario | usuario | usuario | nunca en repo, informes ni chat |

## 3. Tareas

Especificación: [PLAN_DATOS_VIA_QN](../../backlog/PLAN_DATOS_VIA_QN.md), [PLAN_ARCHIVO_OPCIONES](../../backlog/PLAN_ARCHIVO_OPCIONES.md)
y los planes TSFM de `quantdesk` (sólo lectura). Nivel con `difficulty-v3-10`: el del mismo ID en SPRINT-01 (no baja
al partir la tarea).

| Orden | ID | Nivel | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|---|
| 1b | **TI-02-DATA-V2** y **repetición de la tabla FX del banco sobre el 1d de MT5** (usuario, 2026-11-10, revisión de planes, D2, D15) | L6 | • **TI-02-DATA-V2:** `scripts/descarga_lago.py` lee sólo `market.ohlcv.v2` (hoy `TOPICS_DEFECTO`, línea 57, lee v1), con selección por `source` (el FX diario sólo con `source=mt5`) y fallo si un (símbolo, intervalo, ts) llega de dos fuentes sin regla; los cuatro datasets de TI-02-DATA se regeneran desde `0e67465` para reproducir hashes ([PLAN_DATOS_VIA_QN](../../backlog/PLAN_DATOS_VIA_QN.md) §4).<br>• **Repetición de la tabla FX** de TS-00-BENCH sobre el 1d de MT5 leído de qn (cierra [ISSUE-LAGO-FX-1D-CLOSE](issues/ISSUE-LAGO-FX-1D-CLOSE.md)), **en dos tablas (D15):** (i) de cabecera, con la misma ventana y rejilla que hoy (desde 2024-11), comparable con los umbrales de TS-00-OBJ; (ii) de ampliación, con toda la historia MT5 1d desde 2000, para TS-06-FT y la brecha sintético-real, sin mover umbrales.<br>• Los umbrales de TS-00-OBJ quedan «provisionales hasta la tabla MT5» (D14); esta fila debe estar hecha antes del punto de control de 20 M. | Un corte nuevo con `source=mt5` cuadra con `scripts/cuadre_mt5.py`; selftest que falla si el topic por defecto vuelve a v1; informe que declara la incidencia sobre la tabla anterior y revisa los umbrales con la tabla de cabecera (si cambia la conclusión, se avisa al usuario); las dos tablas con hash de dataset | Rueda `69fdb39d` del `.venv` (LAB-00-ENV de SPRINT-01; la re-fijada pasó a SPRINT-03, usuario, 2026-11-11); 1d de MT5 en qn sin velas a medias en el rango usado ([ISSUE-TI12-MT5-VELA-A-MEDIAS](../../issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md)) |
| 2b | **TS-00-BENCH** (FinCast) | L6 | Pedido del usuario el 2026-11-09: FinCast (`Vincent05R/FinCast`, decoder MoE de 1B parámetros, pesos `v1.pth` de 3,97 GB) como cuarto modelo público del banco y candidato a profesor (D-08).<br>• **Licencia:** Apache-2.0 en pesos y código, a confirmar en la revisión fijada.<br>• **Venv:** propio, `E:/quantdesk-lab/venvs/fincast`, con dependencias mínimas (no las de `requirement_v2.txt`: tensorflow y jax).<br>• **Pesos:** se cargan con `torch.load(weights_only=True)` y sha256 fijado.<br>• **Integración:** subproceso con el contrato de 21 cuantiles, como Toto. Sus cuantiles nativos (deciles) se declaran; las colas 1 %/99 % se marcan como extrapoladas.<br>• **Fuga:** su preentrenamiento (FX, crypto y acciones, más de 20B puntos) no declara fecha de corte, así que se evalúa también en una **ventana limpia posterior al 2025-08-27** (fecha de publicación) para todos los modelos: un segundo cálculo de los mismos criterios, no un criterio nuevo.<br>• **Criterios de FinCast (usuario, 2026-11-10, revisión de planes, D13):** sólo **CRPS y QLIKE** y sólo en la ventana limpia; **nunca** en los criterios de colas (Kupiec, pinball 1 %/99 %), porque sus colas son extrapoladas. | La tabla del banco incluye FinCast en la rejilla o en una submuestra declarada, con una tabla aparte de la ventana limpia, coste de CPU por origen y licencia verificada | Venv propio de FinCast (no usa la rueda de `quantdesk`); los modelos de referencia, con la rueda `69fdb39d`; con GPU si DL-02-GATES la habilita, porque en CPU cuesta unas 7 veces Toto |
| 5 | **TI-12-MT5** (más símbolos y periodos) | L6 | Más símbolos y periodos. **La descarga incremental reanudable ya no es de esta fila:** se hace fuera de sprint, ya, en [ISSUE-TI12-MT5-INTRADIA-LOCAL](../../issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md) (usuario, 2026-11-10, revisión de planes, D3) | Mismo hash para el mismo rango en los símbolos y periodos nuevos, con manifiesto (la reanudación sin duplicados se acepta en la ficha de INTRA-LOCAL) | — |
| 6 | **TI-09-ARCH** (cobertura) | L5 | **Condicionada:** TI-09-ARCH salió de SPRINT-01 el 2026-11-08 por falta de datos en qn; antes de medir cobertura hay que entregar la parte de laboratorio (fila 3 de SPRINT-01) cuando el backend publique la cadena. Medición de cobertura del mes siguiente a la entrega; adoptar la captura al cierre si el backend ya entregó OC-03 | Cobertura ≥ 98 % de días hábiles (aceptación del plan) o causa documentada | — |
| 7 | **TI-13-PUB** (ampliación) | L5 | **Consumir y exportar lo que publique el backend** (Yahoo/Stooq, FRED, cripto desde qn, vía TI-02-DATA); refresco del filtro de fugas sobre esas series. Ya no es ingesta propia: A16 bis y decisión del usuario del 2026-11-09 (C-10 de la revisión de planes; [PLAN_DATOS_VIA_QN](../../backlog/PLAN_DATOS_VIA_QN.md) §3) | Informe del filtro actualizado; licencias en la tabla; datasets con hash exportados desde qn | `quantdesk-backend` `PLAN_PUBLICADORES_MERCADO_PUBLICO`; **fila 1b** (TI-02-DATA-V2) |

## 4. Dependencias externas

Ninguna dependencia de sprint: la que había con quantdesk SPRINT-02 se fue con las filas 1–4 a SPRINT-03
(usuario, 2026-11-11; [DEPENDENCIAS.md](../../DEPENDENCIAS.md)).

Dependencias de tarea (no bloquean la activación):

| Tarea local | Espera a | Mientras tanto |
|---|---|---|
| Fila 6, TI-09-ARCH | Datos de cadenas en qn ([ISSUE-TI09-SONDA-CADENAS](../../issues/ISSUE-TI09-SONDA-CADENAS.md)) y OC-03 del backend | No se empieza; si al final del sprint no hay datos, sale con causa documentada |
| Fila 7, TI-13-PUB | quantdesk-backend `PLAN_PUBLICADORES_MERCADO_PUBLICO` (backlog, sin sprint) | Sólo lo que ya esté publicado en qn; si no hay nada, sale con causa documentada |
| Fila 2b, FinCast | DL-02-GATES (GPU) de quantdesk, opcional | En CPU sobre una submuestra declarada |
| Fila 1b, tabla FX | [ISSUE-TI12-MT5-VELA-A-MEDIAS](../../issues/ISSUE-TI12-MT5-VELA-A-MEDIAS.md) (fuera de sprint) | Elegir un rango ya verificado en qn |

## 5. Exclusiones

| Qué | Motivo | Destino |
|---|---|---|
| Filas 1–4 originales (LAB-00-ENV re-fijado, HMM causal, TS-00-PREC con FG-16-hmmcop, cruce con universo59) | Necesitan quantdesk SPRINT-02 cerrado (usuario, 2026-11-11) | [SPRINT-03](../../next/SPRINT.md) §0 |
| TS-02-DISC, consumo de TI-03-FMT y TS-01-SIM | SPRINT-03 de `quantdesk` | [SPRINT-03](../../next/SPRINT.md) |
| Descarga incremental reanudable de MT5 | Fuera de sprint (D3) | [ISSUE-TI12-MT5-INTRADIA-LOCAL](../../issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md) |

## 6. Orden

Fila 1b primero (de ella dependen la tabla FX, los umbrales provisionales de TS-00-OBJ y la fila 7); la 2b (FinCast)
y la 5 (MT5) en paralelo desde el principio; la 7 tras la 1b; la 6 sólo si hay datos de cadenas en qn.
Mutex: el terminal MT5 (filas 1b y 5, y la descarga fuera de sprint de INTRA-LOCAL) lo usa una sola tarea cada vez,
despacio y una serie cada vez (el bróker bloqueó la cuenta una vez).

## 7. Definition of Done

La de [SPRINT-01](../SPRINT-01_2026-11-07_2026-11-09/SPRINT.md#8-definition-of-done).

## 8. Capacidad y presupuesto

Suscripciones compartidas con `quantdesk` (SPRINT-02 activo), `quantdesk-backend` y `quantdesk-network`, sin tope ni
reserva (SPRINT_PROJECT §7). Cinco tareas L5–L6 sin GPU; el tiempo de pared lo dominan la descarga de MT5 y el
zero-shot de FinCast en CPU (unas 7 veces Toto), no los tokens. Sin calibración propia todavía: SPRINT-01 hizo 9
tareas L3–L6 en 3 días con la misma cuota; se toma como escenario de confianza baja y se recalibra al cerrar. Antes de
cada ola se lee la cuota (`claude-or quota --weekly`); si no alcanza, se espera al reinicio en lugar de recortar
alcance.

Cuota de Codex ×2 esta semana (decisión del usuario del 2026-11-11, retransmitida por la raíz de
`reinforcement_learning`): «Tengo 1 reset semanal en codex, así que considera que puedo usarlo el doble, una vez
agotado, calíbralo esta semana, al elegir claude o codex». Al repartir autores y revisores se inclina el reparto hacia
Codex hasta agotar la primera cuota semanal; tras usar el reinicio se recalibra esta misma semana con el consumo real.
Autor y revisor siguen siendo de proveedores distintos.

Modelos: el LAUNCH aplica la decisión del usuario del 2026-11-10 (Haiku 5.5 ni autor ni revisor; L3–L6 con Sonnet 5.5
high o gpt-6.1-sol high hasta L5; tabla «caso borde → test» y revisión obligatoria en L3–L4 hasta el 2026-11-24),
recogida en [SPRINT_PROJECT §6](../../SPRINT_PROJECT.md#6-delegación).

## 9. Cierre (2026-11-13)

**Estado:** Cerrado con arrastres. Fin real: 2026-11-13. Decisión del usuario del 2026-11-13 (AskUserQuestion, raíz
del relevo 2): «Cerrar y arrastrar» y fila 7 «Backlog» ([EXECUTION](EXECUTION.md), «Registro»). No hay release
(SPRINT_PROJECT §10): se pasa de cerrado a planificación.

**Freeze:** no aplica (sin release); el proyecto pasa a planificación el 2026-11-13.

| Fila | ID | Commits (rama `main`, empujados) | Veredicto | Destino / evidencia |
|---|---|---|---|---|
| 2b | TS-00-BENCH (FinCast) | `f3f8a4d`, `a98cea8`, `84fe1a9`, `d422e48`, `c0c7633`, corrección `ce1150d`+`05c27cf`; cierre `09befb8` | CERRADA 2026-11-11 (A4 ronda 2 ACEPTAR) | `execution/TS-00-BENCH-FINCAST/` |
| 1b | TI-02-DATA-V2 y tabla FX sobre MT5 | A: `27cfb2b`…`3e35ed5` (4 correcciones), informe `565f9a0`; B: volcado en mini por la raíz `fb11457` (BDD 262); C: `f0995d0`+`d6bc45d`; cierre `778d0e3` | CERRADA 2026-11-13 (A4 ACEPTAR en A y C); ningún modelo cambia de conclusión en TS-00-OBJ | `execution/TI-02-DATA-V2/`, `execution/TS-00-BENCH-MT5/`; datasets `sha256:a5015bc9…893da` y `sha256:47d79b39…67d32` |
| — | TS-00-OBJ (puerta 2) | quantdesk `3077fddd` | Umbrales confirmados por el usuario el 2026-11-13 | `PLAN_TSFM_FINANZAS` «Fase 0» |
| 5 | TI-12-MT5 (más símbolos y periodos) | `f333e4d` (espera) | ARRASTRADA: cuenta MT5 bloqueada; sin empezar | SPRINT-03 §0, fila S02-5 |
| 6 | TI-09-ARCH (cobertura) | `1b92162`, `fba4279`, `722effa`, `c6c7b5b` (código), `a62d78f` (aceptación), `a80ad40` (primer dataset) | PARCIAL: parte de laboratorio aceptada (A4 ACEPTAR tras 2 correcciones) y dataset `oc03_s20261112_c20261113` (`sha256:eb98ac6a…eea1`); la medición de cobertura, ARRASTRADA | `execution/TI-09-ARCH/`; SPRINT-03 §0, fila S02-6 |
| 7 | TI-13-PUB (ampliación) | `96ed9c0` | SALE con causa documentada: el backend no publica nada propio en qn hasta su SPRINT-03 | Backlog, [PLAN_DATOS_VIA_QN](../../backlog/PLAN_DATOS_VIA_QN.md) |

- **Suite del DoD.** `run_selftests.py` sobre el HEAD `fb5d21f` (scripts idénticos a `a80ad40`; sólo cambian
  documentos): 14 OK y 0 FALLO, `smoke_env` con 21 comprobaciones y 0 saltadas. Salida en
  `E:/quantdesk-lab/tmp/verif_cierre_s02_fb5d21f.log`.
- **Datasets e informes:** cada uno con hash, corte y procedencia en sus informes. Tokens de qn emitidos por la raíz con
  confirmación del usuario (ids 38, 39 y 40), los tres revocados el mismo día; ningún secreto en el repo ni en los
  volcados (búsqueda de patrón `qn_` = 0).
- **Incidencias:**
  - [ISSUE-LAGO-FX-1D-CLOSE](issues/ISSUE-LAGO-FX-1D-CLOSE.md): **resuelta** el 2026-11-13 (fila 1b), criterios 1–3
    marcados con evidencia.
  - Fuera de sprint, siguen vivas en [issues/](../../issues/index.md): ISSUE-TI09-SONDA-CADENAS (criterio 1 pide la cifra
    por día hábil desde el 2026-11-09; la sonda del 2026-11-13 y el primer dataset no la cubren), ISSUE-TI12-MT5-INTRADIA-LOCAL,
    ISSUE-TI12-MT5-SYNC e ISSUE-TI12-MT5-VELA-A-MEDIAS. No son del sprint y no se archivan.
- **Interrupción:** la raíz del relevo 1 murió el 2026-11-13 tras su último commit (`a80ad40`, ya empujado); la
  recuperación en frío no encontró hijos interrumpidos ni WIP.
- **Costes:** no hay `USAGE.md` del sprint. Cuota semanal al cierre (2026-11-13 22:25 local, fuente api): Claude 73 %
  con el 55,7 % de la ventana (al inicio 28 % con el 18,7 %); Codex 57 % con el 36,6 % (al inicio 0 %). Es cuota de
  cuenta compartida con `quantdesk`, `quantdesk-backend`, `quantdesk-network` y `reinforcement_learning`, no
  atribuible a este sprint. Intentos en la BDD de sprints (`sprint_db`, SPRINT-02): autores Codex `gpt-6.1-sol` 13
  intentos (≈ 9,2 h de pared: TI-02-DATA-V2 7, TS-00-BENCH 2, TI-09-ARCH 4), revisores Sonnet 5.5 10 intentos
  (≈ 3,0 h), raíz Opus 5.5. Sin pp aislados por tarea: no entran en la media de calibración (hueco, no cero).
- **Calibración frente a lo previsto (§8):** se previó «como SPRINT-01, 9 tareas en 3 días, confianza baja». Se
  cerraron 2 de 5 en 3 días; lo que alargó no fueron los tokens sino las rondas de corrección (TI-02-DATA-V2: 4; TI-09-ARCH: 2
  más una interrupción por memoria) y las esperas externas (cuenta MT5, OC-03 del backend, publicadores del backend).

### Retrospectiva y trinquete

| Fallo repetido o grave | Causa | Control añadido | Prueba de que lo detecta | ¿Bloquea o avisa? |
|---|---|---|---|---|
| 4 rondas de corrección en TI-02-DATA-V2 (A) | 2 por errores de la ficha de la raíz (horas de cierre; regla de disponibilidad contra DPOL-AVL-002) y 2 por efectos de un cambio de semántica de datos que sólo vio un diferencial | Skill global `references/ficha.md` (usuario, 2026-11-11): test diferencial contra `Base` sobre fixture realista y contraste de cada ejemplo numérico de la ficha con su fuente antes de lanzar | Aplicado en 1b-C (diferencial frente a la tabla antigua detectó el desfase de una barra) | Bloquea (A4) |
| El autor de TI-09-ARCH murió por falta de memoria (`exit 127`) y luego quedó bloqueado (8,8 GB residentes) | Archivador que cargaba todas las sesiones en memoria, con otras corridas en la máquina | Corrección 2: archivador sesión a sesión y columnar, presupuesto ≤ 3 GB por sesión medido en la entrega | `medidas_c2.json`: pico 1,15 GB con 1 sesión y 1,24 GB con 5 | Bloquea (aceptación) |
| 9 de 40 mutantes sobrevivieron en la primera entrega de TI-09-ARCH | Aserciones vacuas y casos borde sin probar | Revisión A4 con mutantes obligatoria; corrección 1 los mata | A4 de `c6c7b5b` | Bloquea (A4) |
| Vigías y bucles de espera de varias raíces dejaron el PC inusable (~460 procesos) | `until ssh … pgrep` que no terminaba y vigías con subprocesos | Regla global de la skill (usuario, 2026-11-13): un vigía por raíz, pasadas ≥ 120 s, sin subprocesos por pasada | Sin control automático | Avisa (regla escrita) |
| Un push ajeno sin autorización comprobada (2026-11-12) | Otra sesión empujó este repo diciendo que el usuario lo autorizó | El usuario confirmó y fijó la regla «la raíz commitea y empuja en cada checkpoint» (`859697e`) | Sin control automático | Avisa (regla escrita) |

Reglas que se retiran: ninguna.
