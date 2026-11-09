# TI-01-INV: anexo de la raíz (puerta 1, 2026-11-08)

`informe.md` es la salida del script sin tocar: sha256 `75095098a093cc79fdc83ccc6e49619be920a3c739ce717d88c37efdfd7dc4fe`.
Este anexo recoge cómo se obtuvo, lo que el script no mide y lo que significa para el sprint.

## Procedencia

- Script `scripts/inventario_options_chain.py` en `cb46ce2`, sha256 `7a9811c7…f9310`. Es el mismo fichero que se copió
  a mini, y su selftest dio `ok` en mini (Python 3.12.3, sólo biblioteca estándar).
- Credencial: token `ti01-inventario-20261108` (id 32), `--envs main`, `--grant "sub:market.>"`. Lo emitió en mini la
  raíz a petición del usuario («puedes generar un token de qn, siguiendo la docu de quantdesk-network»), que confirmó
  nombre, entorno y concesión. Se siguió la skill `qn-token` de quantdesk-network: `--out` a un fichero 600 en mini, y el
  secreto no salió de mini ni pasó por la conversación, los argumentos, los logs ni git.
  - Emitido a las 2026-11-08T15:48:58Z.
  - Revocado a las 2026-11-08T15:58:26Z: `revocado`, el listado da 0 y el fichero se borró con `shred`.
  - Las dos salidas se comprobaron y no contienen el secreto.
- Ejecución en mini contra `http://192.168.1.48:8790/qn` (réplica macold, `/health` 200, metadatos de Postgres,
  recuperación completa). Empezó a las 15:56:59Z y duró unos 4 min, con 7816 GET.
- Ficheros en `E:/quantdesk-lab/runs/TI-01-INV/`:
  - `inventario-macold.json`, sha256 `99dcc5cddfb31d393ea9e1bd325cb52b2e7d7b871c18ff19cf9fcb42e13d67fc` (no va a git:
    2,2 MB, con la lista de peticiones);
  - `informe-macold.md` (igual que `informe.md`);
  - `run-macold.log`.
- **Ejecución descartada:** la primera, de 15:49 a 15:53Z, se hizo contra mini mientras la réplica estaba en
  `stopping` (un redespliegue ajeno a esta tarea). `market.rates.quotes` dio HTTP 503 «los metadatos no están
  disponibles». Se guarda como evidencia en `E:/quantdesk-lab/runs/TI-01-INV/mini-1549-replica-parando/`; sus cifras de
  ohlcv y performance coinciden con las de macold.

## Comprobación directa de las cadenas de opciones

El script lista los instrumentos con `/latest`, y para `market.options.*` ese listado sale vacío. Para descartar que el
vacío fuera del listado y no del lago, una sonda de sólo lectura con el mismo token consultó macold sin filtro de
etiquetas:

| topic | esquema | `/latest` | `/objects` 2024-01-01 → 2027-01-01 | `/objects` 2026-10-01 → 2026-11-09 |
|---|---|---|---|---|
| market.options.chain | v2 (object; symbol, asset_type, opt_type; con `captured_at`, `capture_id` y `underlying_price` de OCS-01) | 0 items | 200, 0 filas | 200, 0 filas |
| market.options.fx | v1 (object; symbol, provider) | 0 items | 200, 0 filas | 200, 0 filas |

La misma consulta sin etiquetas sobre `market.rates.quotes` devuelve filas: supera `limit=5`. Por tanto, **no hay
ninguna fila de cadenas de opciones en el entorno `main` de qn**. El token sólo cubre `main`, así que otros entornos no
se miraron.

## GPU de los nodos de la flota

Se miró por ssh, sólo leyendo: `nvidia-smi` no está instalado y `lspci` sólo muestra gráficos integrados de Intel.

| nodo | IP | GPU |
|---|---|---|
| mini | 192.168.1.46 | Intel Apollo Lake HD Graphics 505 |
| silver | 192.168.1.45 | Intel GeminiLake UHD Graphics 600 |
| macold | 192.168.1.48 | Intel 3rd Gen Core Graphics |

Ningún nodo de la flota de qn tiene GPU para entrenar o inferir.

## Lectura para el sprint

1. **TI-09-ARCH no tiene qué leer.** `market.options.chain` está vacío en el lago, de 2024 a hoy. El plan daba por hecho
   que había capturas intradía («última captura de cada día») mientras llegaba OC-03. Lo que no llegó a qn no se puede
   recuperar (decisión 12-A), así que la serie histórica de cadenas de opciones empieza cuando el productor publique.
2. **Datos reales disponibles para TI-02-DATA:**
   - OHLCV diario de 28 cruces FX desde 2024-11-01, con una cobertura del 99 % y sin huecos de 3 o más días.
   - OHLCV horario de esos 28 cruces, sólo desde 2026-10-18.
   - Curvas de tipos (103 nodos) y rendimientos (64) desde 2025-12-04, con un hueco de unos 118–120 días hábiles entre
     2026-04-06 y 2026-09-16/18. Su cobertura queda en el 34–44 %.
3. **Calidad que debe tratar el exportador:**
   - ohlcv tiene 6047 duplicados por clave y marca, de 30 665 filas.
   - En 140 filas de 1 h el campo `date` cae en el día siguiente a `_ts`: marcas de las 23:00 UTC.
   - `_clock_offset_ns` es nulo en todas las filas de los tres topics.
