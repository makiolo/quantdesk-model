# SPRINT-02 — Rueda fijada, HMM causal y ampliación de datos y banco

**Estado:** En planificación
**Inicio de planificación:** 2026-11-07
**Inicio:** pendiente
**Fin:** pendiente

> Promovido de `future/SPRINT-02/` al activar SPRINT-01 (2026-11-07). Sus premisas se revalidan contra lo que
> entregue SPRINT-01 y contra el cierre real de SPRINT-02 de `quantdesk` (dependencia `decidido`, DEPENDENCIAS.md).
> Decisión 12-A: TI-09-ARCH ya no copia a diario (lee del lago); revisar aquí la «cobertura del archivo».

## 1. Objetivo

Lo que el laboratorio puede hacer **cuando cierre SPRINT-02 de `quantdesk`** (decisión del usuario, 2026-11-07).
Es sobre todo **continuación de SPRINT-01** (MT5: más símbolos y periodos, cobertura del archivo de opciones, ampliación del
banco y de las fuentes públicas), más tres cosas que SPRINT-02 de `quantdesk` entrega y el laboratorio puede
consumir. Revalidar al planificar qué entregó de verdad (SPRINT-02 es muy grande y puede cerrar con arrastres).

## 2. Qué entrega SPRINT-02 de `quantdesk` que el laboratorio consume

Leído de `S:/projects/quantdesk/docs/plans/current/SPRINT.md` y sus planes de grupo (2026-11-07):

| Entrega de `quantdesk` | Para qué le sirve al laboratorio |
|---|---|
| E-RELEASE-WF (-probes): ruedas cp312/cp313/cp314 reparadas e instaladas en venvs limpios por `run_release` | Sustituir la instalación editable por una rueda versionada en `requirements.lock` |
| E15-filter: filtro predictivo de régimen HMM (probabilidad filtrada en `t` con datos ≤ `t`) expuesto a Python | Referencia HMM **causal** en el banco, además del muestreo condicionado de SPRINT-01 |
| FG-16-hmmcop: corpus HMM/cópula/GBM_P con oráculos independientes | Datos sintéticos con verdad conocida para TS-00-PREC (medida 1: probabilidades de régimen) y para validar la referencia HMM |
| G-MKT05-RAW-a: manifiesto y hashes del universo59 (59 series diarias, 2016–2026) | Cruce de TI-02-DATA con el histórico local de `quantdesk` |

**G-AG64** (netting/CSA, puente no lineal) no aporta nada al laboratorio: es de XVA y se consume en `quantdesk`.
`data_py` ya está disponible hoy (lo usa SPRINT-01).

## 3. Tareas

| Orden | ID | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|
| 1 | **LAB-00-ENV** (re-fijado) | Rueda cp312 de la release de SPRINT-02 en el lock en lugar del editable | Venv limpio desde el lock; los informes de SPRINT-01 se reproducen con el mismo hash de dataset y métricas dentro de la tolerancia declarada (o se explica la diferencia) | quantdesk SPRINT-02 cerrado |
| 1b | **TI-02-DATA-V2** y **repetición de la tabla FX del banco sobre el 1d de MT5** (usuario, 2026-11-10, revisión de planes, D2, D15) | • **TI-02-DATA-V2:** `scripts/descarga_lago.py` lee sólo `market.ohlcv.v2` (hoy `TOPICS_DEFECTO`, línea 57, lee v1), con selección por `source` (el FX diario sólo con `source=mt5`) y fallo si un (símbolo, intervalo, ts) llega de dos fuentes sin regla; los cuatro datasets de TI-02-DATA se regeneran desde `0e67465` para reproducir hashes ([PLAN_DATOS_VIA_QN](../backlog/PLAN_DATOS_VIA_QN.md) §4).<br>• **Repetición de la tabla FX** de TS-00-BENCH sobre el 1d de MT5 leído de qn (cierra [ISSUE-LAGO-FX-1D-CLOSE](../issues/ISSUE-LAGO-FX-1D-CLOSE.md)), **en dos tablas (D15):** (i) de cabecera, con la misma ventana y rejilla que hoy (desde 2024-11), comparable con los umbrales de TS-00-OBJ; (ii) de ampliación, con toda la historia MT5 1d desde 2000, para TS-06-FT y la brecha sintético-real, sin mover umbrales.<br>• Los umbrales de TS-00-OBJ quedan «provisionales hasta la tabla MT5» (D14); esta fila debe estar hecha antes del punto de control de 20 M. | Un corte nuevo con `source=mt5` cuadra con `scripts/cuadre_mt5.py`; selftest que falla si el topic por defecto vuelve a v1; informe que declara la incidencia sobre la tabla anterior y revisa los umbrales con la tabla de cabecera (si cambia la conclusión, se avisa al usuario); las dos tablas con hash de dataset | LAB-00-ENV (re-fijado, rueda `69fdb39d` válida mientras tanto) |
| 2 | **TS-00-BENCH** (ampliación) | Referencia HMM filtrada causal (E15-filter); validación de la referencia HMM con el corpus FG-16-hmmcop; más activos y horizontes con los datos nuevos | Tabla ampliada con las mismas métricas; prueba de que perturbar el futuro no cambia la señal pasada del HMM filtrado | LAB-00-ENV (re-fijado), TI-02-DATA, **fila 1b** |
| 2b | **TS-00-BENCH** (FinCast) | Pedido del usuario el 2026-11-09: FinCast (`Vincent05R/FinCast`, decoder MoE de 1B parámetros, pesos `v1.pth` de 3,97 GB) como cuarto modelo público del banco y candidato a profesor (D-08).<br>• **Licencia:** Apache-2.0 en pesos y código, a confirmar en la revisión fijada.<br>• **Venv:** propio, `E:/quantdesk-lab/venvs/fincast`, con dependencias mínimas (no las de `requirement_v2.txt`: tensorflow y jax).<br>• **Pesos:** se cargan con `torch.load(weights_only=True)` y sha256 fijado.<br>• **Integración:** subproceso con el contrato de 21 cuantiles, como Toto. Sus cuantiles nativos (deciles) se declaran; las colas 1 %/99 % se marcan como extrapoladas.<br>• **Fuga:** su preentrenamiento (FX, crypto y acciones, más de 20B puntos) no declara fecha de corte, así que se evalúa también en una **ventana limpia posterior al 2025-08-27** (fecha de publicación) para todos los modelos: un segundo cálculo de los mismos criterios, no un criterio nuevo.<br>• **Criterios de FinCast (usuario, 2026-11-10, revisión de planes, D13):** sólo **CRPS y QLIKE** y sólo en la ventana limpia; **nunca** en los criterios de colas (Kupiec, pinball 1 %/99 %), porque sus colas son extrapoladas. | La tabla del banco incluye FinCast en la rejilla o en una submuestra declarada, con una tabla aparte de la ventana limpia, coste de CPU por origen y licencia verificada | LAB-00-ENV (re-fijado); con GPU si DL-02-GATES la habilita, porque en CPU cuesta unas 7 veces Toto |
| 3 | **TS-00-PREC** (ampliación) | Medida 1 de §4.5 con regímenes conocidos del corpus FG-16-hmmcop | Recuperación de probabilidades de régimen por tipo, con dispersión entre semillas | LAB-00-ENV (re-fijado) |
| 4 | **TI-02-DATA** (ampliación) | Cruce con el manifiesto del universo59 (G-MKT05-RAW-a); nuevas fuentes de TI-12/TI-13 | Diferencias con el universo59 explicadas; mismas garantías de hash y look-ahead | **fila 1b** (TI-02-DATA-V2) |
| 5 | **TI-12-MT5** (más símbolos y periodos) | Más símbolos y periodos. **La descarga incremental reanudable ya no es de esta fila:** se hace fuera de sprint, ya, en [ISSUE-TI12-MT5-INTRADIA-LOCAL](../issues/ISSUE-TI12-MT5-INTRADIA-LOCAL.md) (usuario, 2026-11-10, revisión de planes, D3) | Mismo hash para el mismo rango en los símbolos y periodos nuevos, con manifiesto (la reanudación sin duplicados se acepta en la ficha de INTRA-LOCAL) | — |
| 6 | **TI-09-ARCH** (cobertura) | **Condicionada:** TI-09-ARCH salió de SPRINT-01 el 2026-11-08 por falta de datos en qn; antes de medir cobertura hay que entregar la parte de laboratorio (fila 3 de SPRINT-01) cuando el backend publique la cadena. Medición de cobertura del mes siguiente a la entrega; adoptar la captura al cierre si el backend ya entregó OC-03 | Cobertura ≥ 98 % de días hábiles (aceptación del plan) o causa documentada | — |
| 7 | **TI-13-PUB** (ampliación) | **Consumir y exportar lo que publique el backend** (Yahoo/Stooq, FRED, cripto desde qn, vía TI-02-DATA); refresco del filtro de fugas sobre esas series. Ya no es ingesta propia: A16 bis y decisión del usuario del 2026-11-09 (C-10 de la revisión de planes; [PLAN_DATOS_VIA_QN](../backlog/PLAN_DATOS_VIA_QN.md) §3) | Informe del filtro actualizado; licencias en la tabla; datasets con hash exportados desde qn | `quantdesk-backend` `PLAN_PUBLICADORES_MERCADO_PUBLICO`; **fila 1b** (TI-02-DATA-V2) |

## 4. Dependencias externas

| Sprint local | Depende de | Condición | Estado |
|---|---|---|---|
| SPRINT-02 | quantdesk SPRINT-02 | cerrado | decidido (usuario, 2026-11-07) |

Si alguna entrega de §2 queda arrastrada, su fila sale de este sprint y lo demás sigue.

## 5. Exclusiones

| Qué | Motivo | Destino |
|---|---|---|
| TS-02-DISC, consumo de TI-03-FMT y TS-01-SIM | SPRINT-03 de `quantdesk` | [future/SPRINT-03](../future/SPRINT-03/SPRINT.md) |

## 6. Orden

LAB-00-ENV re-fijado primero (barrera); luego la fila 1b (TI-02-DATA-V2 y tabla FX sobre MT5), de la que dependen las filas 2, 4 y 7; después banco y datos en paralelo, como en SPRINT-01.

## 7. Definition of Done

La de [SPRINT-01](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md#8-definition-of-done).

## 8. Capacidad y presupuesto

«rellenar al planificar».

Modelos: el LAUNCH de este sprint aplica la decisión del usuario del 2026-11-10 (Haiku 5.5 ni autor ni revisor;
L3–L6 con Sonnet 5.5 high o gpt-6.1-sol high hasta L5; tabla «caso borde → test» y revisión obligatoria en L3–L4
hasta el 2026-11-24), recogida en [SPRINT_PROJECT §6](../SPRINT_PROJECT.md#6-delegación). Al iniciar, se anota
en EXECUTION como decisión del usuario retransmitida.
