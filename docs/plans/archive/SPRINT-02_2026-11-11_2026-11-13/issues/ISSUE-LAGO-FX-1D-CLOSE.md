# [ISSUE-LAGO-FX-1D-CLOSE] El «close» del FX diario del lago (yfinance) es el precio de las 00:00 UTC del día

> **Tipo:** Incidencia\
> **Estado:** Resuelto (2026-11-13, SPRINT-02 fila 1b)\
> **Fecha de detección:** 2026-11-09\
> **Origen:** SPRINT-01 / TI-12-MT5 (cuadre 1m contra diario, `fdfa3a7`)\
> **Componente afectado:** dataset `lago_cierre_c20261101` (TI-02-DATA) y la tabla de cabecera de TS-00-BENCH; en
> origen, el publicador yfinance de `quantdesk-backend`\
> **Especificación de referencia:** SPRINT-01 TS-00-BENCH y TI-02-DATA; en el backend, ISSUE-FX-1D-CLOSE-YFINANCE (`c68547d`)\
> **Severidad:** Media\
> **Destino:** Sprint actual (SPRINT-02, activo desde el 2026-11-11)\
> **Prioridad y motivo:** no hay look-ahead, pero la tabla de cabecera del banco usa una serie con la fecha corrida un
> día y con artefactos de captura\
> **Responsable:** raíz del laboratorio; el arreglo en origen lo decide el usuario con el backend\
> **Seguimiento:** SPRINT-02, fila 1b de [current/SPRINT.md](../SPRINT.md) (TI-02-DATA-V2 y repetición de la tabla FX sobre el 1d de MT5, en dos tablas): usuario, 2026-11-10, revisión de planes (D2, D15). Sustituye el seguimiento anterior «fila 2», que no contenía este trabajo

**Snapshot al cierre de SPRINT-01 (2026-11-09, NO RESUELTA):** [archive/SPRINT-01_2026-11-07_2026-11-09/issues/ISSUE-LAGO-FX-1D-CLOSE.md](../../SPRINT-01_2026-11-07_2026-11-09/issues/ISSUE-LAGO-FX-1D-CLOSE.md)

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

- [x] 1. La tabla FX de TS-00-BENCH se repite sobre el 1d de MT5 (`source=mt5`, con cuadre exacto contra su 1m) y pasa
      a ser la tabla de cabecera. El informe declara esta incidencia sobre la tabla anterior. **En dos tablas (usuario,
      2026-11-10, revisión de planes, D15):** la de cabecera con la misma ventana y rejilla que hoy (desde 2024-11),
      comparable con los umbrales, y una de ampliación con toda la historia MT5 1d desde 2000 (para TS-06-FT y la
      brecha sintético-real), sin mover umbrales. Hecha antes del punto de control de 20 M (D14).
- [x] 2. Los umbrales de TS-00-OBJ (relativos a GARCH) se revisan con la tabla nueva; si cambia la conclusión, se avisa
      al usuario.
- [x] 3. ~~Cuando el backend corrija el origen, un nuevo corte del lago da `open == close` en < 5 % de las filas y el
      close cuadra con el final del día.~~ **Sustituido (usuario, vía backend, 2026-11-09):** MT5 pasa a ser la fuente
      por defecto del FX diario (backend `6425e29`): `/api/fxspot` y `/api/modeling` sin `?source=` sirven el 1d de MT5 y
      el 1h de yfinance. El 1d de yfinance **no se corrige en el lago**. Nuevo criterio: el exportador TI-02-DATA filtra
      `source=mt5` para el FX diario y un corte nuevo del lago con ese filtro cuadra con `cuadre_mt5.py`.

## 6. Resolución y verificación

- **Sprint de resolución:** SPRINT-02 del laboratorio, fila 1b.
- **Fecha de resolución:** 2026-11-13.
- **Commit(s) / diagnóstico:** `fdfa3a7` (cuadre); backend `c68547d`; `3e35ed5` (TI-02-DATA-V2, `source=mt5`); `f0995d0` y `d6bc45d` (banco sobre MT5); informe `docs/plans/current/execution/TS-00-BENCH-MT5/completo/informe.md` (sha256 `8088b3e5…79cd`).
- **Verificación:** (3) volcado `source=mt5` de qn → `mt5_fx28_cierre_c20261101` (`sha256:a5015bc9…893da`) cuadra con `cuadre_mt5.py`: lago 1459/1459 al cierre de sesión a 0,0 pb y D1 1507/1507 frente al 1m. (1) Dos tablas: cabecera MT5 (misma ventana, rejilla y horizontes; HMM/GARCH/Chronos-2 6.944 orígenes, Toto 1.400, FinCast limpia 1.400) y ampliación desde 2001 (12.037 orígenes, paso 20, sin mover umbrales); el informe declara la incidencia y el desfase de una barra entre etiquetas (corr. h=1 alineada 0,89–0,98). (2) Revisión por código de TS-00-OBJ: **ningún modelo cambia de conclusión** (Chronos-2, Toto, HMM y FinCast no pasan con ninguna de las dos tablas); cambian detalles: HMM C2 en h1 pasa→no pasa (4/28) y el orden HMM/Chronos-2 en h5. Revisión A4 del código: ACEPTAR (Sonnet 5.5).
- **Pendientes:** ninguno. El usuario confirmó los umbrales el 2026-11-13 («Confirmarlos»): dejan de ser provisionales en `PLAN_TSFM_FINANZAS` (quantdesk `3077fddd`).
