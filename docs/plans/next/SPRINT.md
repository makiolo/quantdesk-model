# SPRINT-03 — Ciclo sintético-real y procedencia en el manifiesto

**Estado:** En planificación
**Inicio de planificación:** 2026-11-07
**Inicio:** pendiente
**Fin:** pendiente

> Promovido de `future/SPRINT-03/` al activar SPRINT-02 (2026-11-11). Sus premisas se revalidan contra lo que
> entregue SPRINT-02 y contra los cierres de quantdesk SPRINT-02 (filas S02-*) y SPRINT-03.

## 0. Filas recibidas de SPRINT-02 (usuario, 2026-11-11)

Al partir SPRINT-02 del laboratorio para activarlo sin esperar a quantdesk SPRINT-02, las filas que necesitan sus
entregas pasan aquí con su texto íntegro y la etiqueta `S02-n` (n = su fila original). Se ejecutan **antes** que las
de §3. Si alguna entrega queda arrastrada en quantdesk, su fila sale de este sprint y lo demás sigue.

| Entrega de quantdesk SPRINT-02 | Para qué le sirve al laboratorio |
|---|---|
| E-RELEASE-WF (-probes): ruedas cp312/cp313/cp314 reparadas e instaladas en venvs limpios por `run_release` | Sustituir la rueda `69fdb39d` construida a mano en SPRINT-01 por una rueda versionada en `requirements.lock` |
| E15-filter: filtro predictivo de régimen HMM (probabilidad filtrada en `t` con datos ≤ `t`) expuesto a Python | Referencia HMM **causal** en el banco, además del muestreo condicionado de SPRINT-01 |
| FG-16-hmmcop: corpus HMM/cópula/GBM_P con oráculos independientes | Datos sintéticos con verdad conocida para TS-00-PREC (medida 1: probabilidades de régimen) y para validar la referencia HMM |
| G-MKT05-RAW-a: manifiesto y hashes del universo59 (59 series diarias, 2016–2026) | Cruce de TI-02-DATA con el histórico local de `quantdesk` |

Estado el 2026-11-11: E-RELEASE-WF-tu hecha; -probes y -perf esperando; E15-filter, FG-16-hmmcop y G-MKT05-RAW-a sin
entregar. En S02-1, «en lugar del editable» se lee «en lugar de la rueda `69fdb39d`» (C-27, revisión del 2026-11-09).

| Orden | ID | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|
| S02-1 | **LAB-00-ENV** (re-fijado) | Rueda cp312 de la release de SPRINT-02 en el lock en lugar del editable | Venv limpio desde el lock; los informes de SPRINT-01 se reproducen con el mismo hash de dataset y métricas dentro de la tolerancia declarada (o se explica la diferencia) | quantdesk SPRINT-02 cerrado |
| S02-2 | **TS-00-BENCH** (ampliación) | Referencia HMM filtrada causal (E15-filter); validación de la referencia HMM con el corpus FG-16-hmmcop; más activos y horizontes con los datos nuevos | Tabla ampliada con las mismas métricas; prueba de que perturbar el futuro no cambia la señal pasada del HMM filtrado | LAB-00-ENV (re-fijado), TI-02-DATA, **fila 1b** |
| S02-3 | **TS-00-PREC** (ampliación) | Medida 1 de §4.5 con regímenes conocidos del corpus FG-16-hmmcop | Recuperación de probabilidades de régimen por tipo, con dispersión entre semillas | LAB-00-ENV (re-fijado) |
| S02-4 | **TI-02-DATA** (ampliación) | Cruce con el manifiesto del universo59 (G-MKT05-RAW-a); nuevas fuentes de TI-12/TI-13 | Diferencias con el universo59 explicadas; mismas garantías de hash y look-ahead | **fila 1b** (TI-02-DATA-V2) |

## 1. Objetivo

Lo que el laboratorio puede hacer **cuando cierre SPRINT-03 de `quantdesk`** (alcance en
`S:/projects/quantdesk/docs/plans/next/README.md`, tres olas, usuario 2026-11-07). Medir la brecha sintético-real con
el discriminador, pasar la procedencia de los datasets al manifiesto y usar los simuladores nuevos del motor como
verdad conocida en los bancos.

## 2. Qué entrega SPRINT-03 de `quantdesk` que el laboratorio consume

| Entrega (ola) | Para qué le sirve al laboratorio |
|---|---|
| TI-03-FMT (1): campo de procedencia sintética y escritor por fragmentos | Procedencia en el manifiesto en lugar del fichero adjunto de SPRINT-01; corpus sintéticos legibles por el mismo lector |
| TI-00-ADR (1): frontera de repositorios, almacén de artefactos, topic de publicación | Tabla de licencias de TI-13-PUB en el ADR (aceptación del plan) y ruta definitiva del almacén (D-I2) |
| TS-01-SIM (1): Heston, Bergomi rugoso, Merton/Bates, GARCH, Hawkes en `engine-core` | Datos sintéticos con parámetros conocidos para TS-00-PREC (medida 1) y para comprobar el banco, si están expuestos en Python |
| TS-02-GEN (3, **si hay capacidad**): generador de corpus | Imprescindible para TS-02-DISC |
| DL-02-GATES (2): carriles de GPU | Zero-shot de Chronos-2/Toto en GPU respetando los carriles, si PyTorch con ROCm funciona en Windows |

## 3. Tareas

| Orden | ID | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|
| 1 | **TI-02-DATA / TI-12-MT5 / TI-13-PUB** (re-exportación) | Re-exportar los datasets con la procedencia en el manifiesto (TI-03-FMT) | Mismo hash de las filas de datos; el manifiesto nuevo carga en `quant-data`; adjuntos de procedencia retirados | TI-03-FMT |
| 2 | **TI-13-PUB** (licencias al ADR) | Entregar la tabla de licencias para TI-00-ADR (se pide a `quantdesk`, no se edita desde aquí) y adoptar el almacén decidido | Tabla en el ADR; artefactos movidos al almacén con sus hashes | TI-00-ADR |
| 3 | **TS-00-PREC** (sintéticos del motor) | Medida 1 de §4.5 con TS-01-SIM: persistencia GARCH, vol de la vol | Recuperación de parámetros por tipo con dispersión entre semillas | TS-01-SIM |
| 4 | **TS-02-DISC** (parte laboratorio) | Clasificador de ventanas reales frente a sintéticas; informe de rasgos que faltan (colas, huecos de apertura, saltos por resultados, calendario, microestructura) que se traducen en familias o priors para TS-02-GEN; se repite | AUC del discriminador por clase de activo y por iteración, decreciente hasta un umbral fijado; un informe por iteración | TS-02-GEN, TI-02-DATA |
| 5 | **TS-00-BENCH** (GPU) | Zero-shot en GPU con carriles DL-02-GATES, si procede | Mismas métricas que en CPU dentro de tolerancia | DL-02-GATES |

Si TS-02-GEN no llega en SPRINT-03 de `quantdesk` (ola 3 condicionada a capacidad), TS-02-DISC pasa a SPRINT-04 y
el resto sigue. Si el discriminador muestra que el dato real es el cuello de botella, recordar **D-13** (pagar datos)
al usuario.

## 4. Dependencias externas

| Sprint local | Depende de | Condición | Estado |
|---|---|---|---|
| SPRINT-03 | quantdesk SPRINT-03 | cerrado | decidido (usuario, 2026-11-07); cubre también las filas S02-* (quantdesk cierra sus sprints en orden) |

## 5. Exclusiones

| Qué | Motivo | Destino |
|---|---|---|
| Ejecuciones de entrenamiento | Necesitan TI-06-CLI, DL-07-TRAIN y TS-05-PREC (SPRINT-04 de `quantdesk`) | [future/SPRINT-04](../future/SPRINT-04/SPRINT.md) |
| XVA (XVA-03-DATA/CDS/CURVE…) | Se ejecuta en `quantdesk` | — |

## 6. Orden

Las filas S02-* primero, empezando por S02-1 (rueda re-fijada: barrera de las demás). Re-exportación primero (los bancos citan hashes de dataset); TS-00-PREC y TS-02-DISC en paralelo después.

## 7. Definition of Done

La de [SPRINT-01](../archive/SPRINT-01_2026-11-07_2026-11-09/SPRINT.md#8-definition-of-done).

## 8. Capacidad y presupuesto

«rellenar al planificar».
