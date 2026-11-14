# Contrato de TI-02-DIARIO: propuesta conjunta para el usuario

SPRINT-03, fila 1. Consolidado por la raíz `quantdesk-model-4d` el 2026-11-14 a partir del
[borrador a1](borrador-contrato-a1.md) y de las respuestas de las raíces del backend (`quantdesk-backend-24`),
`quantdesk` (`quantdesk-f1`) y network (`quantdesk-network-21`), recogidas en ese mismo fichero. **Estado: APROBADO (usuario, 2026-11-14)**,
con las cuatro respuestas recomendadas:
- A2, tarea de Windows;
- sólo OHLCV + history (los JSON siguen con sus productores);
- topic `ops.export.status` y token combinado;
- el resto, tal cual.

Escrito en GOBERNANZA, DEPENDENCIAS y PLAN_DATOS_VIA_QN §4.

> **Nota de diseño (raíz, 2026-11-14):** la cuenta MT5 sigue bloqueada y el usuario estudia pagar por datos (lo
> retransmitió `quantdesk-f1` el 2026-11-14 ~01:30). La fuente del FX diario va en el código como **parámetro versionado
> de la política de fuentes** (hoy `source=mt5`, igual que `POLITICA_FUENTES` de `descarga_lago.py`), no fija.
> Cambiar de fuente sigue siendo una decisión del usuario que se registra en este contrato. Mientras no la haya, sin MT5
> el resultado es `sin_mt5`.

## 1. Qué hace y qué no

- **Hace:** cada día hábil lee de qn el 1d de `market.ohlcv.v2` y escribe dos salidas:
  - `desktop.daily-ohlcv/v1`, que abre el desktop de `quantdesk`;
  - `engine.market-history/v1`, que abre el motor (XVA-03-DATA).
- **Fuentes:** FX diario sólo `source=mt5`, sin rellenar con yfinance.
- **No hace** los JSON del «mercado del día» (`market_fx28_spx30.json`, `option_chains_spx30.json`,
  `rate_curves_g8.json`, `dividends_credit_fx_forwards.json`): siguen con sus productores actuales, los notebooks
  28 y 92–95 de `quantdesk`.
- **Los OAS** (`BAMLC0A0CM`, `BAMLC0A4CBBB`, en percent) se añaden en la fila 7, cuando el backend los publique en qn
  (PUB-02). Hasta entonces, D-I4 y XVA-03-DATA no quedan cerrados sólo con esto (aviso de `quantdesk`).

## 2. Dónde y cuándo corre (opción A2, la que prefieren el backend y `quantdesk`)

- **Dónde:** tarea programada de Windows en el PC del usuario, que el backend registra desde su repo con
  `run_scheduler.cmd` (skill `programador-tareas`). El código es del laboratorio y el backend no lo modifica.
- **Horario:** `15 0 * * 2-6` UTC (martes a sábado 00:15, para las sesiones de lunes a viernes). Corte C = D+1 00:00 UTC.
- **Comprobación previa:** `/api/v1/topics/market.ohlcv.v2/latest` con `interval=1d` y `source=mt5`, con
  `_ts = D 00:00 UTC` y `_recv_ts < C` (`to` es exclusivo). No hay señal de fin del publicador MT5.
- **Señal para Dagster:** tras validar, el exportador publica un objeto de estado en el topic nuevo `ops.export.status`
  (esquema de network: `session`, `cut_head_cycle`, `manifest_sha256`, `status` `ok|sin_mt5|error`, `detail`,
  `exporter_version`, `host`; `max_staleness` 2d; `batch_id` determinista). Un sensor del backend alimenta
  `DagsterJobStale` con la última salida válida, nunca con el último run.
- **Descartada, A1:** Dagster lanza el exportador por SSH. Exige un servidor SSH en el PC y una credencial en mini para
  entrar en él, y el ejecutor de Dagster sólo conoce Linux con Docker.

## 3. Rutas y formatos

- **Desktop:** `%USERPROFILE%/EngineQuantDesktop/data/YYYYMMDD/ohlcv/{ohlcv_daily.parquet,index.json}`, con
  YYYYMMDD = sesión completada.
  - Esquema existente de `quantdesk`, sin cambiarlo: `symbol`, `ts_ms` (UTC 00:00), OHLCV `float64` no nulos, Parquet
    Snappy, clave `(symbol, ts_ms)` única y ordenada.
  - `sources` explícitas en `index.json`.
  - El tipo de volumen (MT5 da `tick_volume`) va en metadatos laterales: no se extiende su contrato.
- **Motor:** `E:/quantdesk-lab/datasets/TI-02-DIARIO/diario_sYYYYMMDD_cYYYYMMDD_<hash8>/` con `manifest.json` de
  `engine.market-history/v1`. Se abre con `open_vendor_dataset(root, dataset_id)` verificando hashes; `volume_kind`
  pasa a `tick_count` (corrige `traded`).
- **Símbolos:** mapa versionado derivado de `daily.universe()` de `quantdesk`, conservando el símbolo de qn en la
  procedencia.
- **Integridad:** manifiesto lateral con sesión, corte, `x-qn-head-cycle` (H), versiones, mapa de símbolos, fuentes y
  SHA-256. Para reproducir el corte: releer y quedarse con las filas de `_cycle <= H`, sin `fresh=true` (receta de network).
- **Un único escritor por producto y fecha:** se construye fuera de la carpeta visible y se publica tras validar; no se
  sobrescribe un corte ya publicado sin una revisión identificada.

## 4. Datos que faltan y limpieza

- **Sin 1d de MT5 en un día de FX esperado** (por ejemplo, con el publicador desactivado): aviso, estado `sin_mt5`, no
  se publica y se conserva la salida anterior. Nunca un fichero vacío ni barras inventadas.
- **Calendario por instrumento:** un festivo NYSE no cierra el FX. Festivo conocido = ausencia esperada registrada;
  calendario desconocido = aviso. Cobertura: la historia disponible, con los huecos publicados.
- **Limpieza:** se rechaza o se pone en cuarentena, nunca se repara (no se usa `repair_ohlcv_range`).
  - Duplicados `(symbol, ts_ms)` con valores iguales: se deja uno.
  - Duplicados con valores distintos: cuarentena de esa serie y día, con aviso.
  - Volumen ausente: 0 con marca `volumen_ausente` en los metadatos laterales, porque el desktop no admite nulos.

## 5. Credencial

- Token exclusivo del exportador con `--grant sub:market.ohlcv.v2 --grant pub:ops.export.status --envs main`.
- Lo emite network con `qn-token` y el usuario lo pone en el `.env` privado del PC, fuera de repos.
- `quantdesk` no recibe credencial. El backend pide aparte su `sub:ops.export.status`.
- Al llegar los OAS (fila 7) se emite otro token con su `sub` y se sustituye.

## 6. Qué se hace al aprobarlo

1. Escribir el contrato en GOBERNANZA, DEPENDENCIAS y PLAN_DATOS_VIA_QN §4 como «decidido (usuario, fecha)».
2. Abrir un issue en network con el JSON de `ops.export.status` (lo registran con `register.sh`) y pedir el token.
3. Avisar al backend: registrar la tarea de Windows y el sensor de frescura, en su PUB-05-EXPORT.
4. Encargar la fila 2 (código, L6) con este contrato como ficha, incluidas las correcciones de `volume_kind` y del
   docstring de `descarga_lago.py` («lectura sobre `market.>`»).
