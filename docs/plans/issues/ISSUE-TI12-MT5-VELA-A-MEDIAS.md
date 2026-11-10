# [ISSUE-TI12-MT5-VELA-A-MEDIAS] El publicador MT5 publicó la vela 1d del 2026-11-09 a medias en 23 de 28 pares

> **Tipo:** Incidencia\
> **Estado:** En resolución (guarda hecha, 23 velas republicadas y verificadas en qn, ClickHouse y API; falta reactivar la tarea)\
> **Fecha de detección:** 2026-11-10\
> **Origen:** publicador MT5 → qn (TI-12-MT5, fase B), ejecución de las 23:01 UTC del 2026-11-09\
> **Componente afectado:** `scripts/publicador_mt5_lib/nucleo.py` (`barras_cerradas`); objetos 1d del 2026-11-09 en
> `market.ohlcv.v2` (`source=mt5`)\
> **Severidad:** Alta (el backend sirve el FX diario desde MT5 por defecto)\
> **Destino:** Fuera de sprint — urgente\
> **Responsable:** raíz del laboratorio

## 1. Comportamiento observado

A las 23:01 UTC del 2026-11-09 el publicador publicó la vela diaria de ese día en 23 de los 28 pares con la historia
que el terminal tenía guardada, sin sincronizar. Ejemplo AUDCAD: en qn high 0,97713, close 0,9768, volumen 68 104; en
MT5 después, high 0,97831, close 0,97762, volumen 75 560. EURUSD salió bien. La comprobación de la cola detecta la
diferencia (`revisiones_detectadas`) pero, por diseño (fase-b.md), no republica.

## 2. Causa

Para un símbolo fuera del Market Watch, `copy_rates_range` devuelve la historia guardada y el terminal la sincroniza
después. El publicador daba la vela por cerrada solo por la hora (cierre de las 17:00 de Nueva York ≤ ahora).

## 3. Arreglo (2026-11-10)

- **Guarda de historia al día** en `barras_cerradas`: una vela solo se publica si MT5 devuelve también alguna vela que
  abre en su cierre o después (la siguiente, aunque esté en curso). Las retenidas se cuentan en
  `retenidas_sin_historia` de cada serie y salen en una pasada posterior. Coste: la última vela antes de un cierre de
  mercado (viernes, festivo) espera a que abra la sesión siguiente.
- El trozo leído llega hasta hoy + 2 días para incluir la vela en curso.
- MT5 falso: opción `historia_hasta` (historia guardada hasta un instante). Selftest nuevo `prueba_guarda_historia`
  (reproduce el caso del 2026-11-09) y `prueba_regla_1d_igual_que_v2` admite solo la vela retenida de fin de semana.
- Tarea programada: una vez al día a las 23:30 hora local y al iniciar sesión (`1fff755`), por el bloqueo de la
  cuenta por exceso de descargas. Queda **desactivada** hasta que acabe el bloqueo.

## 4. Criterios de aceptación

- [x] 1. El selftest del publicador y el del extractor pasan con la guarda.
- [x] 2. Acabado el bloqueo: republicar las 23 velas del 2026-11-09 con su contenido de MT5 ya sincronizado, despacio
      (una a una), y avisar al backend para que compruebe ClickHouse (network y backend dieron el visto bueno).
      **Hecho el 2026-11-10 ~09:35 UTC** con `--republicar-revisiones` (`9e2a9eb`): `publicador_mt5.py --ejecutar
      --sin-credenciales --topic market.ohlcv.v2 --intervalos 1d --ventana 8 --pausa-serie-s 10
      --republicar-revisiones` → 23 publicadas, 5 sin revisión, 0 errores. En qn (`E:/quantdesk-lab/tmp/
      verif_republicacion.py`, solo lectura): las 23 tienen 2 versiones y `latest` da la nueva (AUDCAD close 0,9768 →
      0,97762, volumen 68 104 → 75 560); 28/28 correctas. Backend y network avisados; falta que el backend confirme
      ClickHouse (`fx_spot_1d`, criterio 4 de [ISSUE-TI12-MT5-SYNC](ISSUE-TI12-MT5-SYNC.md)).
      **ClickHouse y API verificados** (backend, 2026-11-10, su EXECUTION `9d63c68`): en `default.fx_spot_1d`
      (source=mt5, 2026-11-09) las 23 tienen 2–3 filas sin fusionar y `FINAL` devuelve la última, con 0 diferencias;
      las 5 sin tocar tienen 1 fila. `/api/fxspot/ohlc/AUDCAD?timeframe=1d`, con y sin `source=mt5`, da c=0,97762.
      Todas las consultas del backend llevan `FINAL`.
      **Horizonte de revisión** (network, 2026-11-10; criterio 5 de ISSUE-TI12-MT5-SYNC): `QN_BARS_REVISION_HORIZON_MS`
      (6 h por defecto) solo afecta a las barras que calcula qn. `market.ohlcv.v2` no declara `timeframes`, así que no
      le aplica: los objetos crudos se aceptan con cualquier `ts` en vivo, en `latest`, en el log y en el lago, que solo
      añade y conserva las dos versiones. Si algún día se piden barras de qn sobre este topic, sí aplicaría (subirlo,
      con máximo 7 d, o republicar dentro de las 6 h).
- [ ] 3. Reactivar la tarea (`run_scheduler.cmd`) y comprobar en `ultimo.json` de la primera pasada nocturna que no
      hay `revisiones_detectadas` nuevas.

## 5. Resolución y verificación

- **Commit(s):** `1fff755` (horario), `2ac3f8f` (guarda), `9e2a9eb` (`--republicar-revisiones`, comparación con la
  versión vigente de qn y `--pausa-serie-s`, 5 s por defecto).
- **Verificación:** `.venv/Scripts/python -X utf8 scripts/publicador_mt5.py --selftest` y
  `scripts/extractor_mt5.py --selftest`, ambos «selftest ok» (2026-11-10).
- **Pendientes:** criterio 3 (el usuario reactiva la tarea y la primera pasada nocturna no deja revisiones nuevas).
