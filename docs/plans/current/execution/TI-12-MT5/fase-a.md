# TI-12-MT5 · Fase A: extractor MetaTrader 5 de sólo lectura (código y selftest, sin terminal real)

Fecha: 2026-11-09 · Base: 82d7f4f · Autor: Claude Opus 5.5 (intento BDD 124)

En la fase A no me conecté al terminal real. No llamé a ninguna función del paquete contra un terminal, no arranqué
`terminal64.exe` y no leí credenciales. Todo se prueba con un módulo `MetaTrader5` falso que pasa por la misma
envoltura de sólo lectura.

## Qué hay

| Ruta | Contenido |
|---|---|
| `scripts/extractor_mt5.py` | CLI: `--inventario`, `--descargar`, `--comparar`, `--selftest`; guardas de disco y de secretos, y registro en `runs/` |
| `scripts/extractor_mt5_lib/lectura.py` | lista blanca, envoltura `TerminalSoloLectura`, enganche al terminal y credenciales |
| `scripts/extractor_mt5_lib/hora.py` | reglas de hora del servidor, conversión a UTC y los dos métodos de detección del desfase |
| `scripts/extractor_mt5_lib/simbolos.py` | sufijos, base normalizada, nombres de fichero sin colisión y resolución de nombres |
| `scripts/extractor_mt5_lib/inventario.py` | inventario: símbolos, dígitos, punto, precio de las velas, profundidad por periodo y ticks |
| `scripts/extractor_mt5_lib/descarga.py` | trozos con caché, consolidación en parquet, huecos, `manifest.json` y comparación |
| `scripts/extractor_mt5_lib/falso.py` | módulo `MetaTrader5` falso con datos sintéticos deterministas |
| `scripts/extractor_mt5_lib/selftests.py` | selftest y **lista negra**, el único sitio de estas rutas donde se nombran las funciones prohibidas |

## Decisiones

**Sólo lectura, garantizada por código.**
- `lectura.py` es el único módulo que importa el paquete. Lo envuelve en el acto en `TerminalSoloLectura`, que **no
  guarda el módulo**: sólo copia las funciones y las constantes de la lista blanca.
- Funciones de la lista blanca: `initialize`, `login`, `shutdown`, `version`, `last_error`, `terminal_info`,
  `account_info`, `symbols_total`, `symbols_get`, `symbol_info`, `symbol_info_tick`, `copy_rates_range`,
  `copy_rates_from_pos` y `copy_ticks_range`.
- Si se pide otro nombre, la envoltura lanza `FuncionNoPermitida`, exista o no en el paquete. `initialize` sólo acepta
  `path=`.
- Las funciones que mandan, comprueban o calculan órdenes, las de posiciones, las del historial de operaciones, las de
  profundidad de mercado y las que tocan el Market Watch quedan fuera. El selftest las nombra en su lista negra.

**Pruebas de la lista blanca.**
- Estática: ni la fuente de estas rutas ni este documento nombran nada de la lista negra fuera de ese bloque, y sólo
  `lectura.py` importa el paquete.
- Dinámica, sobre el paquete **real**, del que sólo se leen atributos: los 246 nombres que no están en la lista blanca
  lanzan error. La envoltura no contiene el módulo.
- El falso trae trampas con los nombres de la lista negra. En todo el selftest no se llama a ninguna.

**El falso reproduce el paquete real.**
- Comparé el falso con el paquete instalado (5.0.6231) leyendo su API, sin llamarla.
- Firmas: las saqué de la primera línea del docstring de cada función.
- Campos de `TerminalInfo` (22), `AccountInfo` (28), `SymbolInfo` (96) y `Tick` (8).
- Las constantes de la lista blanca.
- Orden de los campos de MqlRates: el binario `_core` contiene `open/high/low/close/tick_volume/real_volume` en ese
  orden (leí el fichero, no lo ejecuté).
- En la fase B, `descarga.py` comprueba en cada respuesta que los campos sean exactamente los esperados. Si no lo son,
  se para.

**Credenciales.**
- Origen del cambio: un mensaje de la raíz del 2026-11-09 (puerta 2). Ver el apartado de alcance más abajo.
- Si existe `E:/quantdesk-lab/secrets/mt5.json` (o la ruta de `QDL_MT5_SECRETS`), el extractor hace
  `initialize(path=…)` y `login(…)`. Con `--sin-credenciales`, o si no hay fichero, sólo se engancha a un terminal que el
  usuario ya abrió y autenticó.
- En ese caso comprueba antes, con `tasklist`, que `terminal64.exe` está en ejecución, porque `initialize()` lo
  arrancaría.
- Ningún valor de las credenciales se imprime ni se guarda:
  - `Credenciales` oculta su `repr`.
  - Los errores pasan por `censurar`.
  - Toda salida (consola, JSON y manifest) pasa por `comprobar_sin_secretos`, que la rechaza si contiene el número de
    cuenta, la contraseña, el servidor o la ruta.
- La procedencia lleva:
  - el tipo de cuenta (demo, concurso o real);
  - el bróker (`company`);
  - la versión y el build del terminal, el nombre, `maxbars` y la versión del paquete.
- En la fase A llevaba además un hash con sal del número de cuenta y otro del servidor. La raíz decidió en la fase B que
  no se guarde ningún hash, y se quitaron.
- El selftest busca los cuatro valores falsos en la consola y en los bytes de los 387 ficheros que escribe, incluidos
  los parquet.

**Hora del servidor a UTC** (`hora.py`).
- MT5 da las marcas en la hora del servidor, escritas como si fueran UTC.
- Regla por defecto, `ny+7`: servidor = hora de Nueva York + 7 h. Es decir, UTC+2, y UTC+3 mientras rige el verano de
  EE. UU.:
  - desde 2007, del segundo domingo de marzo a las 07:00 UTC al primer domingo de noviembre a las 06:00 UTC;
  - de 1987 a 2006 y antes, las reglas de entonces.
- Alternativas: `ue+2` (EET con el verano de la UE) y `fija:+N`.
- Hora repetida al volver al invierno (domingo de 08:00 a 08:59 del servidor): se toma la primera aparición.
- Hora inexistente al pasar al verano: se convierte con el desfase de invierno.
- Las dos se cuentan en el manifest. Sólo aparecen en símbolos que cotizan en fin de semana.
- Pruebas:
  - Casos explícitos de marzo y noviembre de 2026, 2006 y 1985.
  - Cada hora de 1987 a 2035 contra `zoneinfo` (`America/New_York` + 7 h).
  - Cada hora de 1997 a 2035 contra `Europe/Athens`.
  - Cada 3 h de 1976 a 1986.
  - La vuelta exacta, salvo la hora repetida.

**Detección del desfase.** Hay dos métodos y ninguno usa credenciales.
1. En vivo: el último tick (`symbol_info_tick`) de EURUSD, USDJPY y GBPUSD frente al reloj UTC, redondeado a media hora.
   - Sólo vale con el FX abierto y un residuo de menos de 5 min.
   - Si es concluyente y no coincide con la regla, la descarga se para y pide `--regla`.
2. Histórico, sólo en símbolos FX: el fin de la última vela antes de cada hueco de fin de semana, llevado a la hora de NY
   con cada regla candidata.
   - Coherencia de una regla: fracción de semanas que cierran a las 17:00 NY.
   - La regla correcta da 1,0. Una fija equivocada acierta sólo en una estación; `ue+2` falla unas 4 semanas al año.
   - El resultado va al manifest por serie (m1, m5, h1). Si la regla usada queda claramente por debajo de la mejor, el
     extractor sale con 1.
   - Probado con brókers falsos en `ny+7`, `fija:+2` y `ue+2` durante casi dos años de velas de 1 h.

**Rango, velas cerradas y trozos.**
- Rango: `--desde` incluido y `--hasta` excluido, en UTC, con `hasta` <= hoy.
- Un tick entra si su marca está en [desde, hasta). Una vela entra si su **cierre** está en (desde, hasta]. Así:
  - sólo entran velas cerradas;
  - ninguna queda partida entre trozos;
  - la vela diaria del día D del servidor, que abre el D-1 a las 21:00 o 22:00 UTC, no se pierde en los bordes.
- Trozos: un mes para 1 m y 5 m, un año para 1 h y 1 d, y un día para los ticks.
- Cada trozo va ya convertido a la caché `data/mt5/_trozos/<bróker>/<regla>/…`, con un `.json` de filas y
  SHA-256. Los dos se escriben de forma atómica.
- **Reanudar** es relanzar la misma orden: no se vuelven a pedir los trozos que ya tienen `.json`.
- **Incremental**: con un `hasta` posterior se reutilizan los trozos cerrados de la caché.
- `--refrescar` vuelve a pedirlo todo.
- La petición al terminal se amplía 6 h más un periodo por cada lado y después se filtra en UTC. Así el resultado no
  depende de si el terminal lee las fechas como UTC o como hora del servidor.

**Salida.**
- Ficheros: `data/mt5/<hasta>/<símbolo>__<periodo>.parquet` (snappy, un grupo de filas por trozo) y `manifest.json`.
- El manifest lleva:
  - los parámetros, la regla y la procedencia;
  - por serie: filas, bytes, SHA-256, primera y última marca UTC, desfases vistos, horas ambiguas e inexistentes,
    huecos y cierre semanal;
  - `hash_conjunto`.
- No lleva ninguna marca de la ejecución. La duración, los trozos pedidos y reutilizados y la detección en vivo van a
  `runs/TI-12-MT5/`.
- Si la carpeta de salida ya tiene una descarga con otros parámetros, el extractor la rechaza.
- `--comparar A B` recalcula los SHA-256 en disco y compara los manifests.

**Columnas.**
- Velas: `time_servidor`, `ts_utc_ms`, `desfase_s`, `open`, `high`, `low`, `close`, `tick_volume`, `real_volume`,
  `spread_puntos`, `spread`, `ask_close_est` y `mid_close_est`.
- Ticks: `time_msc_servidor`, `ts_utc_ms`, `desfase_s`, `bid`, `ask`, `last`, `mid`, `spread`, `volume`, `volume_real` y
  `flags`.

**Precio de las velas.**
- MT5 construye las velas con el Bid (`chart_mode` BID: FX y CFD) o con el Last (bolsa). Se guardan tal cual y se declara
  `precio_velas`.
- `spread_puntos` es el campo `spread` de MqlRates. MetaQuotes no documenta qué spread de la barra es, así que es
  indicativo.
- `ask_close_est` = close + spread y `mid_close_est` = close + spread / 2 son estimaciones. Quedan nulas con velas de Last.
- En los ticks, `mid` y `spread` salen del bid y el ask reales.

**Huecos.** Se informan y no se rellenan:
- fin de semana: contiene el sábado a las 12:00 UTC y dura 2,5 días o menos;
- fin de semana ampliado: festivo pegado al fin de semana;
- otros, por tamaño, con los 5 mayores.

**Sufijos.** Sigue este orden:
1. `#`/`!` como prefijo.
2. Par `currency_base` + `currency_profit`.
3. El primer separador.
4. Una cola de minúsculas.

Dos símbolos con la misma base se marcan. Pedir por base (`--simbolos EURUSD`) resuelve al único símbolo con esa base,
o falla si hay varios. Los nombres de fichero no colisionan aunque el disco no distinga mayúsculas.

## Evidencia de la fase A

- `.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --selftest` termina en `selftest ok` en unos 20 s, sin terminal
  ni red.
- Cubre:
  - las dos descargas idénticas byte a byte (`--refrescar`), con el mismo `hash_conjunto`;
  - una reanudación tras un fallo en la consulta 24 (23 trozos reutilizados y 41 pedidos, con el mismo hash);
  - una descarga incremental (20 trozos pedidos y 48 reutilizados);
  - los cambios de hora de marzo y noviembre en 1 m;
  - el hueco de fin de semana, la cripto 24x7 con 60 minutos ambiguos y el símbolo de bolsa sin ticks;
  - el bloqueo con terminal cerrado, sin arrancarlo;
  - la parada si el desfase en vivo no casa con la regla.
- `.venv/Scripts/python -X utf8 scripts/run_selftests.py` da 10 OK y 0 FALLO.

## Cambio de alcance del 2026-11-09 y lo que no hice

- La raíz me comunicó que el usuario abrió la puerta 2 y que las credenciales están en `E:/quantdesk-lab/secrets/mt5.json`.
  Por eso añadí el enganche con credenciales (`login` en la lista blanca), con las guardas descritas.
- **No he ejecutado el extractor contra el terminal real.** Ejecutarlo con ese fichero supone autenticar una cuenta de
  bróker con una contraseña, y como agente no lo hago.
- Por tanto no hay todavía inventario real, detección real del desfase ni cifras de descarga.
- No he leído el fichero de credenciales ni `config_pro.py`.
- Las órdenes de abajo las tiene que lanzar el usuario, o la raíz con su aprobación explícita.

## Fase B: órdenes exactas (en este orden)

Antes de empezar:
- El terminal tiene que estar instalado en la ruta del fichero de credenciales.
- En el terminal, conviene poner «Herramientas > Opciones > Gráficos > Máx. barras en el gráfico» a *Unlimited*. Si no,
  `copy_*` sólo sirve hasta `maxbars` velas por símbolo y periodo. El inventario lo marca como `limitada_por_maxbars`.

```
df -h /c /e
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --inventario --sin-profundidad
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --inventario --simbolos @fx28
```

- El primer inventario es el catálogo completo, sin profundidad: unos segundos.
- El segundo mide la profundidad de los 28 cruces en m1, m5, h1 y d1 y los ticks de 3 días: una consulta de hasta
  `maxbars` - 1 velas por símbolo y periodo (entrega 6b, ver fase-b.md), y de 1 a 10 min si el terminal tiene que bajarse
  la historia.
- Mirar en la salida:
  - el desfase en vivo: tiene que ser «concluyente=True coincide=True» con el FX abierto. Si no, `--regla`;
  - `limitadas por maxbars`;
  - la primera vela de m1.

Prueba de repetibilidad sobre un mes:

```
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --descargar --simbolos @fx28 --periodos d1,h1,m5,m1 --desde 2026-10-01 --hasta 2026-11-01 --salida E:/quantdesk-lab/data/mt5/prueba_2026-10
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --descargar --simbolos @fx28 --periodos d1,h1,m5,m1 --desde 2026-10-01 --hasta 2026-11-01 --salida E:/quantdesk-lab/data/mt5/prueba_2026-10_r2 --refrescar
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --comparar E:/quantdesk-lab/data/mt5/prueba_2026-10 E:/quantdesk-lab/data/mt5/prueba_2026-10_r2
```

- Tamaño: unas 0,9 M filas de 1 m más 0,2 M de 5 m, unos 40 MB, y el doble contando la caché.
- Tiempo: minutos.
- El registro de `runs/TI-12-MT5/` da la duración real. Con esa medida se reescala la estimación de la descarga completa.

Descarga completa, después de `df -h` (E: muy por debajo de 50 GB de uso, C: > 2 GB):

```
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --descargar --simbolos @fx28 --periodos d1,h1,m5,m1 --desde 2016-01-01 --hasta 2026-11-01
```

- `--desde` se ajusta a la primera vela de m1 del inventario. Si la historia empieza más tarde, el fichero empieza más
  tarde y el manifest lo dice.
- Para d1 y h1 con más historia que m1, hay que lanzar otra orden con `--periodos d1,h1`, un `--desde` anterior y otra
  `--salida`.
- Estimación con 10,8 años y unos 40 B por fila de 1 m:
  - 28 × 4,0 M filas de 1 m ≈ 4,5 GB, y 1 m + 5 m ≈ 5,5 GB;
  - con la caché de trozos, ≈ 11 GB. Si la historia de m1 empieza en 2010, ≈ 17 GB;
  - 28 × 140 meses × 2 periodos ≈ 7.800 trozos. A 0,5-2 s por trozo, entre 1 y 4 h.
- Si se corta, se relanza la misma orden.

## Lo que queda para la fase B

- Inventario real publicado, con la detección del desfase con evidencia (en vivo y cierre del viernes en el manifest).
- Las dos descargas del mismo rango con el mismo hash.
- Tiempo y disco medidos.
- En espera, por decisión de la raíz: la fuente MT5 en el exportador a `engine.market-history/v1` y el cuadre de 1 m
  agregado a diario contra el diario del lago, con la tolerancia propuesta y justificada.

Riesgos que mirar con el terminal real:
- Si `copy_rates_from_pos` devuelve None fuera de la historia con otro código, la bisección lo trata como «no hay».
  Medido después (entrega 6b): da -1 «Call failed», como la sincronización. La bisección se ha sustituido por una sola
  consulta; ver fase-b.md.
- La primera petición de historia larga puede volver incompleta mientras el terminal sincroniza. Relanzar con
  `--refrescar` y comparar.
- Un símbolo 24x7 con dos velas en la hora repetida pararía la consolidación por marcas UTC repetidas. Se ve y se decide
  entonces.
