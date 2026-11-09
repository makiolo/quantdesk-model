**NO RESUELTA** (pendiente al cierre de SPRINT-01, 2026-11-09). Snapshot congelado; la ficha viva es [issues/ISSUE-LAGO-FX-1D-CLOSE.md](../../../issues/ISSUE-LAGO-FX-1D-CLOSE.md).

# [ISSUE-LAGO-FX-1D-CLOSE] El «close» del FX diario del lago (yfinance) es el precio de las 00:00 UTC del día

> **Tipo:** Incidencia\
> **Estado:** Abierto\
> **Fecha de detección:** 2026-11-09\
> **Origen:** SPRINT-01 / TI-12-MT5 (cuadre 1m contra diario, `fdfa3a7`)\
> **Componente afectado:** dataset `lago_cierre_c20261101` (TI-02-DATA) y la tabla de cabecera de TS-00-BENCH; en
> origen, el publicador yfinance de `quantdesk-backend`\
> **Especificación de referencia:** SPRINT-01 TS-00-BENCH y TI-02-DATA; en el backend, ISSUE-FX-1D-CLOSE-YFINANCE (`c68547d`)\
> **Severidad:** Media\
> **Destino:** Backlog (SPRINT-02 del laboratorio)\
> **Prioridad y motivo:** no hay look-ahead, pero la tabla de cabecera del banco usa una serie con la fecha corrida un
> día y con artefactos de captura\
> **Responsable:** raíz del laboratorio; el arreglo en origen lo decide el usuario con el backend\
> **Seguimiento:** SPRINT-02, fila 2 (TS-00-BENCH, ampliación): repetir la tabla FX sobre el 1d de MT5

---

## 1. Contexto y comportamiento observado

- En `lago_cierre_c20261101` (14 448 filas, 28 pares), el 41,7 % de las filas tienen `open == close` exactamente.
  Lo midió la raíz con pyarrow sobre `E:/quantdesk-lab/datasets/TI-02-DATA/lago_cierre_c20261101/lago_ohlcv_1d.parquet`.
- Cuadre contra el 1m de MT5, del 2026-08-06 al 2026-11-07 (1459 días-par):
  - el `close` del día D cuadra con el precio de MT5 a las 00:00 UTC de D: error mediano de 0,81 pb, y el 98,6 % de
    los días dentro de 0,1 veces el rango diario;
  - no cuadra con el final del día: error mediano de 19,8 pb.
  - `open`, `high` y `low` sí corresponden al día UTC.
- El backend lo confirma en ClickHouse: el close de yfinance del día D cuadra con el close de MT5 de D-1, con 3–6,5 pb
  de diferencia, en toda la historia desde 2025. Además, su captura diaria corre a las 23:00 UTC, antes del cierre, y
  la revisión llega fuera del horizonte de revisión de qn (6 h).

## 2. Divergencia respecto a la especificación

El `close` de una barra 1d debe ser el último precio del intervalo, no el del instante de apertura. No hay look-ahead:
la disponibilidad que usa el banco (`ts` + 1 día) es conservadora. Pero los rendimientos de la tabla de cabecera de
TS-00-BENCH miden de 00:00 UTC a 00:00 UTC, con la etiqueta corrida un día, y además mezclan artefactos de captura.

## 3. Caso mínimo reproducible

```
.venv/Scripts/python -X utf8 scripts/cuadre_mt5.py ...   (comandos en execution/TI-12-MT5/cuadre.md)
```
También: proporción de filas con `open == close` en `lago_ohlcv_1d.parquet`, que da 0,417.

## 4. Análisis de causa raíz

La causa está en el origen, en el publicador yfinance del backend y su hora de captura, no en el laboratorio. Lo
sigue la ficha del backend ISSUE-FX-1D-CLOSE-YFINANCE. Opciones que el backend presenta al usuario:
- MT5 como fuente por defecto del 1d;
- construir el 1d desde su 1h;
- corregir la hora de captura y republicar.

## 5. Criterios de aceptación y resolución

- [ ] 1. La tabla FX de TS-00-BENCH se repite sobre el 1d de MT5 (`source=mt5`, con cuadre exacto contra su 1m) y pasa
      a ser la tabla de cabecera. El informe declara esta incidencia sobre la tabla anterior.
- [ ] 2. Los umbrales de TS-00-OBJ (relativos a GARCH) se revisan con la tabla nueva; si cambia la conclusión, se avisa
      al usuario.
- [ ] 3. Cuando el backend corrija el origen, un nuevo corte del lago da `open == close` en < 5 % de las filas y el close
      cuadra con el final del día.

## 6. Resolución y verificación

- **Sprint de resolución:** pendiente (SPRINT-02 del laboratorio, previsto).
- **Fecha de resolución:** pendiente.
- **Commit(s) / diagnóstico:** `fdfa3a7` (cuadre); backend `c68547d` (su ficha).
- **Verificación:** pendiente.
- **Pendientes:** los criterios 1–3.
