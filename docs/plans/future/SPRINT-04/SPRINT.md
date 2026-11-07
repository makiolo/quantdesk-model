# SPRINT-04 — Escalera de entrenamiento, ajuste fino y adaptadores

**Estado:** En planificación
**Inicio de planificación:** 2026-11-07
**Inicio:** pendiente
**Fin:** pendiente

## 1. Objetivo

Lo que el laboratorio puede hacer **cuando cierre SPRINT-04 de `quantdesk`** (decisión del usuario, 2026-11-07),
que entrega la base de entrenamiento e inferencia (DL-07-TRAIN, TI-06-CLI, TI-14-REG, TS-05-PREC…). Aquí se lanzan
las ejecuciones con el código de `quantdesk` (el laboratorio sólo aporta configuraciones `engine.train-request/v1`,
datos, recibos e informes). Según el calendario del backlog (§3.3), TS-05-PRE puede no arrancar hasta SPRINT-05 de
`quantdesk` si DL-07-TRAIN llega tarde: revalidar al planificar.

## 2. Tareas

Especificación y aceptación: PLAN_TSFM_FINANZAS §5, fases 2 y 6.

| Orden | ID | Qué se hace aquí | Aceptación | Depende de |
|---|---|---|---|---|
| 1 | **TS-05-PRE** (ejecuciones) | Preentrenamiento conjunto (cono y camino) en escalera 4 M → 20 M → 80 M en las dos GPU, precisión según §4.5; curvas, MFU y coste. **Prueba de interferencia en 20 M:** mismo tronco sólo con cabeza de cono, 3 semillas por variante. **Punto de control D-08 en 20 M:** frente a Chronos-2/Toto zero-shot en el banco de TS-00-BENCH | Pérdida monótona con el tamaño; MFU medido; recibo completo. CRPS del cono conjunto dentro de la dispersión entre semillas del de cabeza única; si no, opción C de D-03 antes de 80 M. Si el 20 M pierde claramente frente a los públicos, destilación antes de 80 M | TS-05-PREC, TS-02-GEN, DL-07-TRAIN, TI-06-CLI (`quantdesk`) |
| 2 | **TS-05-FREQ** | Ablación de frecuencias en 20 M (3 semillas): (a) diario, (b) diario + covariables desde intradía, (c) multifrecuencia peso intradía bajo, (d) alto | Tabla sobre objetivos diarios (CRPS, colas, QLIKE) y secundarios intradía; peso elegido por medición; si (c) no mejora a (b), intradía sólo como covariables | TS-05-PRE, TI-12-MT5 |
| 3 | **TS-06-FT** | Ajuste fino con datos reales; `TRAINED_UNTIL` en el manifiesto | Mejora sobre zero-shot en el banco de TS-00 sin fuga temporal (embargo verificado) | TS-05-PRE, TI-02-DATA |
| 4 | **TS-18-WF** (adaptadores) | Un adaptador por trimestre con su `TRAINED_UNTIL` sobre el tronco congelado; ejecuciones trimestrales y mensuales | Ningún adaptador ve datos posteriores a su corte y el tronco no contiene series financieras posteriores al primer corte; backtest de 10 años encadenado; coste por adaptador medido (objetivo: horas) | TS-06-FT, TI-14-REG, TI-13-PUB |
| 5 | **TS-15-FINAL** | Ejecución larga del tamaño elegido, ficha del modelo, recibo, cuantización si procede (DL-08) | Supera los umbrales de TS-00-OBJ; artefacto publicado según TI-03-FMT | TS-06-FT, TS-00-OBJ; **puerta de usuario** |

**Recordatorio D-13 (pagar datos):** cuando el banco tras TS-06-FT (o el discriminador TS-02-DISC) muestre que el dato
real es el cuello de botella, recordárselo al usuario (petición del usuario, 2026-11-07); se decide junto con los CDS
de pago de PLAN_XVA_BANCARIO X-04.

## 3. Dependencias externas

| Sprint local | Depende de | Condición | Estado |
|---|---|---|---|
| SPRINT-04 | quantdesk SPRINT-04 | cerrado | decidido (usuario, 2026-11-07) |

GPU: entrenamiento con tope de VRAM y carriles de DL-02-GATES (D-I5, opción C; reparto fijo si TI-11-COEX falló).

## 4. Exclusiones

| Qué | Motivo | Destino |
|---|---|---|
| Código de entrenamiento, inferencia, TS-05-PREC, TS-06-CAL, TS-07…TS-17 | Son de `quantdesk` | backlog de `quantdesk` |

## 5. Orden

Escalera estrictamente en serie (4 M → 20 M → interferencia y punto de control → 80 M); TS-05-FREQ en 20 M en paralelo
a la decisión de 80 M; TS-06-FT tras el tamaño elegido; TS-18-WF y TS-15-FINAL al final (pueden pasar a SPRINT-05).

## 6. Definition of Done

La de [SPRINT-01](../../current/SPRINT.md#8-definition-of-done), más recibo completo por ejecución (hash del dataset,
ventana, semilla, versión del código, métricas fuera de muestra).

## 7. Capacidad y presupuesto

«rellenar al planificar»: días de GPU por escalón; presupuesto orientativo en PLAN_TSFM_FINANZAS §3.
