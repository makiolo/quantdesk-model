# [ISSUE-TI12-MT5-SYNC] Publicar el 1d de MT5 sólo con la historia sincronizada, poder reenviar velas ya publicadas y republicar las 23 incompletas

> **Tipo:** Incidencia\
> **Estado:** En resolución vía [ISSUE-TI12-MT5-VELA-A-MEDIAS](ISSUE-TI12-MT5-VELA-A-MEDIAS.md), con la que se fusiona al cerrar: guarda de historia (`2ac3f8f`), modo `--republicar-revisiones` (`9e2a9eb`), 23 velas republicadas y verificadas en qn 28/28 (`b9cbbbe`), el horizonte de revisión de qn no aplica a `market.ohlcv.v2` (`f660654`) y ClickHouse/API con el cierre nuevo (`d6d7a55`). Quedan: reactivar la tarea programada y la carga de `@continuo` (aplazada). Estado a las 10:41 del 2026-11-10\
> **Fecha de detección:** 2026-11-09 (aviso del laboratorio al backend ~23:45 UTC; ficha el 2026-11-10)\
> **Origen:** Fuera de sprint (TI-12-MT5, fase B, ejecución de las 23:01 UTC del 2026-11-09)\
> **Componente afectado:** `scripts/publicador_mt5.py` y `scripts/publicador_mt5_lib/nucleo.py` (`serie`, `barras_cerradas`); objetos 1d del 2026-11-09 en `market.ohlcv.v2` (`source=mt5`)\
> **Especificación de referencia:** [PLAN_DATOS_VIA_QN.md](../backlog/PLAN_DATOS_VIA_QN.md) §2, filas TI-12-MT5-SYNC y TI-12-MT5 (fase C); backend `ISSUE-FX-1D-CLOSE-YFINANCE` (aviso `e90eb03`)\
> **Severidad:** Alta (el backend sirve el FX diario desde MT5 por defecto y la vela del 2026-11-09 está mal en 23 de 28 pares)\
> **Destino:** Fuera de sprint — urgente\
> **Prioridad y motivo:** urgente. Si el horizonte de revisión de barras de qn es de ~6 h (hipótesis H2 del backend, sin verificar), la ventana para corregir el lago puede estar vencida o a punto de vencer; mientras tanto la carga nocturna de `@continuo` (193 símbolos) sigue aplazada con el mismo riesgo de velas parciales\
> **Responsable:** raíz del laboratorio\
> **Seguimiento:** próxima acción: verificar el horizonte de revisión de qn (criterio 5), añadir el modo de reenvío (criterio 2) y republicar las 23 velas (criterio 3). Decisión del usuario: «Republicar y aplazar» (usuario, 2026-11-10, revisión de planes, D1)

Relacionada con [ISSUE-TI12-MT5-VELA-A-MEDIAS](ISSUE-TI12-MT5-VELA-A-MEDIAS.md), abierta antes por otra sesión del
laboratorio sobre el mismo defecto: esa ficha registra la guarda de historia ya escrita (criterio 1 de esta) y la tarea
programada desactivada por el bloqueo de la cuenta; **esta ficha añade la decisión D1 del usuario (modo de reenvío,
aprobación de las 23 republicaciones, horizonte de revisión y aplazamiento de la carga nocturna)**. Al cerrar, se
fusionan en una sola (una ficha por problema).

---

## 1. Contexto y comportamiento observado

- La vela 1d de MT5 del 2026-11-09, publicada a las 23:01 UTC, salió incompleta en 23 de los 28 pares de fx28 porque
  la historia D1 del terminal no estaba sincronizada (EURUSD salió bien). El laboratorio avisó al backend (commit
  `e90eb03` de `quantdesk-backend`, 00:48 del 2026-11-10).
- La comprobación de la cola detecta la diferencia (`revisiones_detectadas`) pero `nucleo.py::serie` sólo publica
  `huecos + ts > ultimo`: **hoy no existe camino de reenvío** de una vela ya publicada con valores distintos.
- La carga nocturna de `@continuo` (noche 1, ~369 000 objetos, programada a las 02:03 del 2026-11-10) queda aplazada
  (aviso del backend); si el 02:03 era una tarea o comando ya lanzado, no consta su cancelación (SIN VERIFICAR).

## 2. Divergencia respecto a la especificación

La vela 1d publicada debe estar cerrada y completa. El publicador la daba por cerrada sólo por la hora (cierre de las
17:00 de Nueva York ≤ ahora), sin comprobar que la historia del terminal estuviera sincronizada.

## 3. Caso mínimo reproducible

MT5 falso con historia D1 guardada hasta un instante anterior (`historia_hasta`) y 1m más reciente: el publicador
emite la vela del día con high, close y volumen parciales. Ejemplo real (AUDCAD, 2026-11-09): en qn high 0,97713,
close 0,9768, volumen 68 104; en MT5 después, high 0,97831, close 0,97762, volumen 75 560.

## 4. Análisis de causa raíz

Para un símbolo fuera del Market Watch, `copy_rates_range` devuelve la historia guardada y el terminal la sincroniza
después. Falta (a) una guarda de historia al día antes de publicar y (b) un camino de republicación de velas ya
publicadas cuya versión cambia.

## 5. Criterios de aceptación y resolución

- [ ] 1. **Guarda de historia.** El publicador publica el 1d de un símbolo sólo con la historia D1 sincronizada y la
      vela del día cerrada y completa. Selftest con un MT5 falso que devuelve el D1 parcial («Call failed» o menos
      barras que el 1m agregado): 0 velas publicadas y aviso. (ISSUE-TI12-MT5-VELA-A-MEDIAS declara hecha la guarda y
      su selftest `prueba_guarda_historia`; reverificar con `scripts/publicador_mt5.py --selftest` al cerrar.)
- [ ] 2. **Modo de reenvío.** Un modo explícito del publicador (nombre por fijar al implementarlo) reenvía velas ya
      publicadas cuyo contenido de MT5 difiere de lo confirmado en qn, sin tocar las demás. Selftest: con valores
      distintos reenvía sólo las diferentes; una segunda ejecución reenvía 0 (idempotente); no se activa en el modo
      normal.
- [ ] 3. **Republicación de las 23 velas** 1d de fx28 del 2026-11-09 (aprobada por el usuario el 2026-11-10, D1),
      una a una y con aviso previo al backend y a network. Después, `scripts/cuadre_mt5.py --m1 --d1` da 0 puntos de
      diferencia en las 28 velas del 2026-11-09. (La tarea programada está desactivada hasta que acabe el bloqueo de
      la cuenta por exceso de descargas, según ISSUE-TI12-MT5-VELA-A-MEDIAS: la republicación espera a ese fin.)
- [ ] 4. **La revisión llega** a qn, al lago y a ClickHouse: lo comprueba el backend con la lectura de
      `/api/fxspot?source=mt5` y `fx_spot_1d`; el resultado se anota aquí.
- [ ] 5. **Horizonte de revisión de qn.** Se verifica la hipótesis H2 del backend (horizonte de revisión de barras de
      ~6 h y desde cuándo cuenta). Si ya venció, esta ficha pide a `quantdesk-network` la excepción para aceptar las
      23 revisiones en el lago y anota la respuesta; sin excepción, el lago conservaría la primera versión y la
      incidencia queda **Parcial** con ClickHouse corregido y el lago no.
- [ ] 6. **Carga nocturna de `@continuo` aplazada** hasta cerrar esta ficha: no se lanza la noche 1 (ni las 2 y 3
      de acciones) antes de que 1–5 estén cumplidos; se reprograma con el aviso habitual a backend y network (≤ 40 000
      objetos por 5 min, 02:00–05:00 CET). Se confirma por escrito que la noche del 02:03 del 2026-11-10 no salió.
- [ ] 7. **Tarea programada.** Cuando acabe el bloqueo de la cuenta, el usuario reactiva `quantdesk\publicador_mt5`
      (`run_scheduler.cmd`) y la primera pasada nocturna no deja `revisiones_detectadas` nuevas en `ultimo.json`.
- [ ] 8. Documentación actualizada: [PLAN_DATOS_VIA_QN.md](../backlog/PLAN_DATOS_VIA_QN.md) §2 (fila TI-12-MT5-SYNC) y
      esta ficha en `issues/index.md`.

## 6. Resolución y verificación

- **Sprint de resolución:** Fuera de sprint.
- **Fecha de resolución:** pendiente.
- **Commit(s) / diagnóstico:** pendiente (backend `e90eb03` es el aviso; los commits de la guarda están en
  ISSUE-TI12-MT5-VELA-A-MEDIAS).
- **Verificación:** pendiente.
- **Pendientes:** criterios 1–8. Decisiones del usuario ya tomadas (2026-11-10, revisión de planes, D1): republicar las
  23 velas, aplazar la carga nocturna de `@continuo` hasta cerrar esta ficha, y pedir la excepción a network si el
  horizonte de revisión ya venció.
