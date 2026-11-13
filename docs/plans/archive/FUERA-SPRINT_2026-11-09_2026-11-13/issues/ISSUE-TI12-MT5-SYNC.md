# [ISSUE-TI12-MT5-SYNC] Publicar el 1d de MT5 sólo con la historia sincronizada, poder reenviar velas ya publicadas y republicar las 23 incompletas

> **Tipo:** Incidencia\
> **Estado:** **Resuelta** el 2026-11-13 (usuario, 2026-11-13, revisión de planes, R3): cerrada fusionando [ISSUE-TI12-MT5-VELA-A-MEDIAS](ISSUE-TI12-MT5-VELA-A-MEDIAS.md); la verificación 28/28 en qn y ClickHouse sustituye al cuadre de 0 puntos (criterio 3); lo operativo (reactivar la tarea programada, primera pasada limpia y carga nocturna de `@continuo`) pasa a la fila 4 de MT5 (4c, TI-12-MT5-OPS) de [SPRINT-03](../../../next/SPRINT.md). Ficha archivada en `archive/FUERA-SPRINT_2026-11-09_2026-11-13/` ([manifiesto](../ARCHIVE_MANIFEST.md)). *Estado anterior:* En resolución vía ISSUE-TI12-MT5-VELA-A-MEDIAS, con la que se fusiona al cerrar: guarda de historia (`2ac3f8f`), modo `--republicar-revisiones` (`9e2a9eb`), 23 velas republicadas y verificadas en qn 28/28 (`b9cbbbe`), el horizonte de revisión de qn no aplica a `market.ohlcv.v2` (`f660654`) y ClickHouse/API con el cierre nuevo (`d6d7a55`). Quedan: reactivar la tarea programada y la carga de `@continuo` (aplazada). Estado a las 10:41 del 2026-11-10\
> **Fecha de detección:** 2026-11-09 (aviso del laboratorio al backend ~23:45 UTC; ficha el 2026-11-10)\
> **Origen:** Fuera de sprint (TI-12-MT5, fase B, ejecución de las 23:01 UTC del 2026-11-09)\
> **Componente afectado:** `scripts/publicador_mt5.py` y `scripts/publicador_mt5_lib/nucleo.py` (`serie`, `barras_cerradas`); objetos 1d del 2026-11-09 en `market.ohlcv.v2` (`source=mt5`)\
> **Especificación de referencia:** [PLAN_DATOS_VIA_QN.md](../../../backlog/PLAN_DATOS_VIA_QN.md) §2, filas TI-12-MT5-SYNC y TI-12-MT5 (fase C); backend `ISSUE-FX-1D-CLOSE-YFINANCE` (aviso `e90eb03`)\
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

- [x] 1. **Guarda de historia.** *(HECHO, revisión 2026-11-13: `2ac3f8f`, `prueba_guarda_historia` en
      `publicador_mt5_lib/selftests.py:548`; reverificado en la suite del DoD de SPRINT-02, `publicador_mt5.py: selftest ok`,
      `E:/quantdesk-lab/tmp/verif_cierre_s02_fb5d21f.log`.)* El publicador publica el 1d de un símbolo sólo con la historia D1 sincronizada y la
      vela del día cerrada y completa. Selftest con un MT5 falso que devuelve el D1 parcial («Call failed» o menos
      barras que el 1m agregado): 0 velas publicadas y aviso. (ISSUE-TI12-MT5-VELA-A-MEDIAS declara hecha la guarda y
      su selftest `prueba_guarda_historia`; reverificar con `scripts/publicador_mt5.py --selftest` al cerrar.)
- [x] 2. **Modo de reenvío.** *(HECHO, revisión 2026-11-13: `--republicar-revisiones`, `9e2a9eb`; selftest
      `publicador_mt5_lib/selftests.py:430-443`: sin la opción no reenvía (`revisiones_detectadas` 1, 0 POST nuevos); con
      ella reenvía 1 y la pasada siguiente ve 0.)* Un modo explícito del publicador (nombre por fijar al implementarlo) reenvía velas ya
      publicadas cuyo contenido de MT5 difiere de lo confirmado en qn, sin tocar las demás. Selftest: con valores
      distintos reenvía sólo las diferentes; una segunda ejecución reenvía 0 (idempotente); no se activa en el modo
      normal.
- [x] 3. *(ACEPTADO por R3 (usuario, 2026-11-13, revisión de planes): la verificación 28/28 en qn (`b9cbbbe`) y en
      ClickHouse/API (backend `9d63c68`) sustituye al «cuadre con 0 puntos»; GAP-ISSUES-02 resuelto con su opción (a). El
      cuadre `cuadre_mt5.py --m1 --d1` se puede repetir gratis tras la próxima incremental de INTRA-LOCAL, sin que sea
      condición de esta ficha.)* *(Revisión 2026-11-13: republicación HECHA el 2026-11-10 09:24 UTC, 23 publicadas, 0 errores, verificadas 28/28 en
      qn con `E:/quantdesk-lab/tmp/verif_republicacion.py` (`b9cbbbe`; registro: `publicador_2026-11-10.jsonl`, línea 9);
      avisos a backend y network dados. Falta sólo el «cuadre con 0 puntos»: `cuadre_mt5.py --m1 --d1` no puede cubrir el
      2026-11-09 con las descargas locales actuales (m1 de fx28 llega al 2026-11-07), ver GAP-ISSUES-02.)*
      **Republicación de las 23 velas** 1d de fx28 del 2026-11-09 (aprobada por el usuario el 2026-11-10, D1),
      una a una y con aviso previo al backend y a network. Después, `scripts/cuadre_mt5.py --m1 --d1` da 0 puntos de
      diferencia en las 28 velas del 2026-11-09. (La tarea programada está desactivada hasta que acabe el bloqueo de
      la cuenta por exceso de descargas, según ISSUE-TI12-MT5-VELA-A-MEDIAS: la republicación espera a ese fin.)
- [x] 4. *(HECHO, revisión 2026-11-13: backend `9d63c68`, 2026-11-10, «velas 1d de MT5 del 2026-11-09 republicadas,
      comprobadas en ClickHouse y API»; detalle en ISSUE-TI12-MT5-VELA-A-MEDIAS §4.)* **La revisión llega** a qn, al lago y a ClickHouse: lo comprueba el backend con la lectura de
      `/api/fxspot?source=mt5` y `fx_spot_1d`; el resultado se anota aquí.
- [x] 5. *(HECHO, revisión 2026-11-13: respuesta de network del 2026-11-10 (`f660654`): `QN_BARS_REVISION_HORIZON_MS`
      sólo afecta a las barras que calcula qn y `market.ohlcv.v2` no declara `timeframes`, así que no le aplica; la
      variable existe con tope de 7 d en `quantdesk-network/crates/qn-server/src/config.rs:663,941`. No hizo falta
      excepción. SIN VERIFICAR contra el código de agregación de qn: se acepta la respuesta de network.)* **Horizonte de
      revisión de qn.** Se verifica la hipótesis H2 del backend (horizonte de revisión de barras de
      ~6 h y desde cuándo cuenta). Si ya venció, esta ficha pide a `quantdesk-network` la excepción para aceptar las
      23 revisiones en el lago y anota la respuesta; sin excepción, el lago conservaría la primera versión y la
      incidencia queda **Parcial** con ClickHouse corregido y el lago no.
- [x] 6. *(HECHO en lo que pide esta ficha, revisión 2026-11-13: las 25 pasadas del publicador registradas del 2026-11-09
      al 2026-11-13 usan los símbolos por defecto (`@fx28`); ninguna lleva `--simbolos @continuo`, y no hay pasada entre las
      23:45 UTC del 11-09 y las 06:03 UTC del 11-10, así que la noche de las 02:03 CET **no salió** (registros
      `E:/quantdesk-lab/runs/TI-12-MT5/publicador/`). La condición «1–5 cumplidos» ya se da; la reprogramación de la carga
      es de TI-12-MT5 fase C en [PLAN_DATOS_VIA_QN](../../../backlog/PLAN_DATOS_VIA_QN.md), con aviso a backend y network, y
      espera al desbloqueo de la cuenta.)* **Carga nocturna de `@continuo` aplazada** hasta cerrar esta ficha: no se lanza la noche 1 (ni las 2 y 3
      de acciones) antes de que 1–5 estén cumplidos; se reprograma con el aviso habitual a backend y network (≤ 40 000
      objetos por 5 min, 02:00–05:00 CET). Se confirma por escrito que la noche del 02:03 del 2026-11-10 no salió.
- [ ] 7. **TRASLADADO a SPRINT-03, fila 4c (TI-12-MT5-OPS)** por R3 (usuario, 2026-11-13, revisión de planes); no es
      condición de cierre de esta ficha. Estado de la tarea (R2): `quantdesk\publicador_mt5` **desactivada** por la raíz de
      guardia el 2026-11-13 (~23:55 local, `schtasks /Change /DISABLE`, verificado «Disabled») hasta el desbloqueo de la
      cuenta; C-ISSUES-01 resuelta por regla (estaba activa y fallando). *(Revisión 2026-11-13, ver C-ISSUES-01: los registros muestran pasadas automáticas el 11-11 y 11-12 a las 23:30 y el
      11-13 al iniciar sesión, todas «Authorization failed»; la tarea parece activa, SIN VERIFICAR en el Programador. La
      primera pasada limpia sólo ocurrirá tras el desbloqueo de la cuenta.)* **Tarea programada.** Cuando acabe el bloqueo de la cuenta, el usuario reactiva `quantdesk\publicador_mt5`
      (`run_scheduler.cmd`) y la primera pasada nocturna no deja `revisiones_detectadas` nuevas en `ultimo.json`.
- [x] 8. *(HECHO en la aplicación de la revisión del 2026-11-13: `PLAN_DATOS_VIA_QN.md` §2 puesto al día (fila
      TI-12-MT5-SYNC cerrada, tarea programada desactivada) e `issues/index.md` rehecho con esta ficha como resuelta;
      C-08 y C-ISSUES-02 resueltas por regla.)* *(Revisión 2026-11-13: `issues/index.md` ya la lista; `PLAN_DATOS_VIA_QN.md` l. 44, 47 y 139 siguen diciendo
      «nueva», «sin commit en este repo» y «cada 15 min»: ver C-ISSUES-02.)* Documentación actualizada: [PLAN_DATOS_VIA_QN.md](../../../backlog/PLAN_DATOS_VIA_QN.md) §2 (fila TI-12-MT5-SYNC) y
      esta ficha en `issues/index.md`.

## 6. Resolución y verificación

- **Sprint de resolución:** Fuera de sprint (`archive/FUERA-SPRINT_2026-11-09_2026-11-13/`).
- **Fecha de resolución:** 2026-11-13 (usuario, 2026-11-13, revisión de planes, R3: cerrar fusionando VELA-A-MEDIAS).
- **Commit(s) / diagnóstico:** guarda de historia `2ac3f8f` (criterio 1); `--republicar-revisiones` y `--pausa-serie-s`
  `9e2a9eb` (criterio 2); republicación de las 23 velas verificada 28/28 en qn `b9cbbbe` (criterio 3, aceptado por R3);
  ClickHouse y API `d6d7a55` del laboratorio y backend `9d63c68` (criterio 4); horizonte de revisión `f660654` (criterio 5);
  registros del publicador en `E:/quantdesk-lab/runs/TI-12-MT5/publicador/` sin `--simbolos @continuo` (criterio 6);
  horario de la tarea `1fff755`. Aviso inicial: backend `e90eb03`.
- **Verificación:** selftests del publicador y del extractor en la suite del DoD de SPRINT-02 (`fb5d21f`, 14 OK,
  `E:/quantdesk-lab/tmp/verif_cierre_s02_fb5d21f.log`, según el informe de la revisión de issues; no se reejecutó al
  archivar).
- **Lo que pasa a SPRINT-03 (fila 4c, TI-12-MT5-OPS):** reactivar `quantdesk\publicador_mt5` tras el desbloqueo de la
  cuenta (desactivada desde el 2026-11-13, R2), primera pasada sin `revisiones_detectadas` nuevas y con los huecos del 1d
  rellenados (FX 1d de MT5 parado desde el 2026-11-10), y la carga nocturna de `@continuo` con el aviso habitual a backend
  y network (≤ 40 000 objetos por 5 min, 02:00–05:00 CET).
- **Pendientes (texto anterior a la resolución):** criterios 1–8. Decisiones del usuario ya tomadas (2026-11-10, revisión de planes, D1): republicar las
  23 velas, aplazar la carga nocturna de `@continuo` hasta cerrar esta ficha, y pedir la excepción a network si el
  horizonte de revisión ya venció.

## Revisión de planes (2026-11-13)

Veredicto: **FUSIONAR con ISSUE-TI12-MT5-VELA-A-MEDIAS (esta ficha sobrevive) y dejar un residuo a SPRINT-03** · Motivo:
6 de 8 criterios están acreditados con commit y registro; los dos que faltan (7: primera pasada nocturna limpia; 8:
documentación ajena) dependen de la cuenta MT5 y de otros documentos. Se mantiene esta ficha como superviviente porque
la citan PLAN_DATOS_VIA_QN, DEPENDENCIAS y la D1 del usuario, y es el superconjunto de criterios de la otra.

| Criterio | Clasificación | Evidencia |
|---|---|---|
| 1. Guarda de historia | HECHO | `2ac3f8f`; `selftests.py:548`; suite del DoD 14 OK (`fb5d21f`) |
| 2. Modo de reenvío | HECHO | `9e2a9eb`; `selftests.py:430-443` |
| 3. 23 velas republicadas | HECHO con salvedad | `b9cbbbe`, `publicador_2026-11-10.jsonl` l. 9; verificación 28/28 en qn. El «cuadre 0 puntos» exacto no consta (GAP-ISSUES-02) |
| 4. Llega a lago y ClickHouse | HECHO | backend `9d63c68` |
| 5. Horizonte de revisión | HECHO | network, 2026-11-10 (`f660654`); no aplica a `market.ohlcv.v2` |
| 6. Carga de `@continuo` aplazada | HECHO (la reprogramación sale a fase C) | registros del publicador sin `@continuo` |
| 7. Tarea programada y primera pasada limpia | VIGENTE, **bloqueado por puerta de usuario** (cuenta MT5) | última pasada buena: 2026-11-10 09:24 UTC; desde el 11-10 22:35 UTC todas bloqueadas |
| 8. Documentación | MODIFICADO | índice hecho; PLAN_DATOS_VIA_QN desactualizado (no es de esta ficha) |

Hallazgo que la ficha no recoge: **desde el 2026-11-10 no se ha publicado ninguna vela 1d de MT5** (todas las pasadas
bloqueadas), así que en qn faltarían las sesiones 2026-11-10, 11-11 y 11-12 de las 28 series FX (SIN VERIFICAR en qn: sólo
consta por los registros del publicador). El backend sirve el FX diario desde MT5 por defecto (severidad Alta de la
ficha). El relleno de huecos del publicador las recuperará solo tras el desbloqueo; conviene avisar al backend de que el
FX 1d de MT5 está parado desde el 2026-11-09 (GAP-ISSUES-03).

Cierre: se puede **CERRAR** cuando (i) una pasada tras el desbloqueo termine con `codigo` 0, 28 series, huecos rellenados
y 0 `revisiones_detectadas` en `ultimo.json`; (ii) el usuario acepte la salvedad del criterio 3; (iii) se actualice
PLAN_DATOS_VIA_QN. VELA-A-MEDIAS se borra entonces (todo su contenido ya vive aquí o en los commits).

**Decisión (usuario, 2026-11-13, revisión de planes, R3):** se **cierra ya**, fusionando VELA-A-MEDIAS; (ii) aceptado
(GAP-ISSUES-02 (a)) y (i) pasa a SPRINT-03 fila 4c. VELA-A-MEDIAS no se borra: se archiva junto a esta ficha en
`archive/FUERA-SPRINT_2026-11-09_2026-11-13/issues/` (el archivo conserva todos los hallazgos).
