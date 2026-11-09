# TI-12-MT5 · Fase C: universo ampliado (continuo, cripto y acciones US) en 1d

Estado: código y selftest. En local, las descargas las lanza la raíz. En qn no se publica nada nuevo hasta que network
dé el visto bueno: la tarea programada sigue con fx28 y 1d (`--simbolos` por defecto `@fx28`, `--intervalos 1d`).

## Qué hay

| Fichero | Qué es |
|---|---|
| `scripts/extractor_mt5_lib/universos.py` | reglas de selección, cruce del S&P 500, carga del fichero y `--simbolos @...` |
| `scripts/extractor_mt5_lib/universos/universos.json` | universos resueltos contra el inventario real del 2026-11-09 (versionado) |
| `scripts/extractor_mt5_lib/universos/sp500.csv` | instantánea de los componentes del S&P 500 con su fuente y fecha |
| `scripts/extractor_mt5_lib/calendarios.py` | clases de sesión, festivos por bolsa y huecos de 1d por clase |
| `scripts/publicador_mt5_lib/nucleo.py` | vela 1d por clase (`sesion_1d`) y ritmo de publicación (`Ritmo`) |

Órdenes nuevas (no tocan el terminal):

```
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --universos E:/quantdesk-lab/data/mt5/inventario/inventario_20261109T111300Z.json
.venv/Scripts/python -X utf8 scripts/extractor_mt5.py --sp500 RESPUESTA_API_WIKIPEDIA.json
```

`--sp500` rehace el CSV desde la respuesta JSON de
`https://en.wikipedia.org/w/api.php?action=parse&page=List_of_S%26P_500_companies&prop=wikitext|revid&format=json&formatversion=2`.
Después hay que volver a lanzar `--universos`.

## Universos con nombre

`--simbolos` del extractor y del publicador acepta `@fx28` (los 28 cruces del lago, fijos en el código como siempre) y
estos grupos. Las reglas van sobre `ruta`, la carpeta del símbolo en el terminal:

| Grupo | Regla | Símbolos |
|---|---|---|
| `@fx60` | `Forex\*` (Majors, Minors, Exotics) | 60 |
| `@metales_energia` | `Commodities\Metals\*` y `Commodities\Energies\Energies Spot\*` | 16 |
| `@indices` | `Indices\Indices Spot\*` | 23 |
| `@crypto` | lo que cuelga directamente de `Crypto\` (las 17 grandes del broker) | 17 |
| `@crypto_alts` | `Crypto\Crypto Alts\*` | 77 |
| `@continuo` | unión de los cinco anteriores | 193 |
| `@us_grandes` | S&P 500 con su versión de sesión normal (`.NYSE`, `.NAS`, `.US`) | 484 |

Fuera siempre:
- Lo que tiene vencimiento: 35 símbolos. Son los sufijos de mes y año (`_Z6`, `_H7`, `_Z6_CFD`, `GCG27_CFD`) y todo lo
  de las carpetas de futuros (`Metal Futures`, `Energies Futures`, `Indices Futures`, también `SIN26`). Los `Softs` son
  todos futuros.
- Los 12 bonos (`Bonds CFDs`), todos con vencimiento.
- Los 12 `Stohastic`, índices sintéticos del broker.

`universos.json` guarda:
- la fecha y el inventario del que sale;
- la regla de cada grupo y los excluidos;
- los grupos;
- el mapeo del S&P 500 y las etiquetas de qn.

Si el broker cambia, se vuelve a lanzar `--universos` con un inventario nuevo y se commitea el fichero.

## S&P 500 → símbolos del broker (`@us_grandes`)

Fuente: Wikipedia, «List of S&P 500 companies», revisión 1384572480, leída el 2026-11-09. Son 503 componentes (500
empresas; Alphabet y otras tienen dos clases). La instantánea está en `universos/sp500.csv` (ticker, nombre, bolsa,
sector, fecha de alta).

**Qué es `-24` según el inventario.** Hay 5.173 símbolos `.NAS-24`, `.NYSE-24` y `.US-24`, en las carpetas `24HR NAS`,
`24HR NYSE` y `24HR Other US`. Su descripción dice «24/5 CFD»: es la misma acción cotizada 24 horas, 5 días a la semana
(preapertura, sesión, después del cierre y nocturna). Su vela 1d no acaba en el cierre oficial de las 16:00 de Nueva
York. Por eso se usa siempre la versión de sesión normal, sin `-24`.

**Regla de cruce.**
- Para cada ticker se busca primero el sufijo de su bolsa: `.NYSE` para NYSE y `.NAS` para Nasdaq. Luego los otros dos,
  y por último `.US`.
- La bolsa del broker no siempre es la del índice, pero la sesión sí: HON y PANW están como `.NYSE`, y GPC y HLT como
  `.NAS`. CBOE está como `CBOE.US`.
- Clases de acción: el punto del ticker se busca como `-`, como `/` y sin separador. Así `BRK.B` da `BRK-B.NYSE` y
  `BF.B` da `BF/B.NYSE`. El broker no es uniforme: en sesión normal usa `BRK-B` y `BF/B`, y en `-24` usa `BRK/B`.
- El tag `symbol` de qn de una acción es su ticker con la clase separada por `-` (`BRK-B`, `BF-B`), como yfinance. Las
  demás clases llevan la base normalizada (`EURUSD`, `XAUUSD`, `DE40`, `BTCUSD`), igual que fx28.

**Casados: 484 de 503.** Sin casar, 19:

| Motivo | Tickers |
|---|---|
| sólo existe la versión `-24` (13) | ARES, BDX, CPAY, CRH, ECHO, FERG, FIX, META, Q, SHW, SKYD, SNDK, WDC |
| el broker no lo tiene (6) | FDXF (FedEx Freight), GOOGL (Alphabet clase A; está GOOG), HONA, MDT (Medtronic), OKE (Oneok), VYLR |

**Decisión pendiente.** Meta Platforms sólo está en `-24`. Si se quiere en el universo, la opción es tomar su `-24`
marcada aparte, sabiendo que su 1d no cierra a las 16:00. No lo hago sin que se decida.

## Vela 1d publicable por clase

**Medido en la caché real** (496.225 velas 1d de los símbolos de `@continuo` ya descargados el 2026-11-09, de 1990 a
hoy): todas abren a las 00:00 del servidor. Lo mismo vale para índices, cripto y metales. El servidor va a Nueva York + 7 h todo el año.

**Regla para todas las clases** (`nucleo.sesion_1d`), que es la sugerencia de la raíz:
- `date` = fecha del SERVIDOR de la apertura de la vela, y `ts` = 00:00 UTC de `date` (opción b).
- La vela está cerrada cuando el servidor pasa al día siguiente: 00:00 del servidor = 17:00 de Nueva York.

| Clase | Días con vela | Cierre de la vela 1d | Festivos (sin vela, no son huecos) |
|---|---|---|---|
| forex | lunes a viernes | 17:00 NY | como hasta ahora (método de siempre de `descarga.huecos`) |
| metales_energia | lunes a viernes | 17:00 NY | CME: 1 ene, Viernes Santo, 25 dic |
| indices | lunes a viernes | 17:00 NY (después de la sesión de cualquier bolsa) | los de la bolsa de cada índice |
| crypto | los siete días | 17:00 NY, también sábado y domingo | ninguno |
| acciones_us | lunes a viernes | 17:00 NY; la sesión acaba a las 16:00 | NYSE |

Las acciones se publican una hora después del cierre de la bolsa, a propósito. El día del servidor acaba a las 17:00 NY y
así la subasta de cierre ya está dentro de la vela. Es la misma regla para todas las clases.

**Con fx28 es idéntica a la publicada.**
- Antes, `date` era la fecha de Nueva York del cierre de las 17:00. Como servidor = NY + 7 h, esa es la fecha del
  servidor de la apertura.
- El cierre era apertura UTC + 1 d, que es el mismo instante salvo en una vela que contenga un cambio de hora.
- Comprobado en la caché real: 338.639 velas 1d de fx60, 0 `ts` distintos.
- Hay 25 velas con el cierre una hora distinto. Son todas velas de domingo en días de cambio de hora (2006 y 2015) de
  algunos cruces. Llevan veinte años cerradas, así que no cambia lo que se publica.
- La caché tiene exactamente 178.522 velas 1d de fx28 desde 2000, las mismas que se publicaron.

**Tests que lo garantizan** (selftest del publicador):
- `prueba_regla_1d_igual_que_v2`: la regla de v2, congelada en el test, frente a la nueva. Mismas velas, mismo `ts` y
  mismo instante de cierre en cada media hora alrededor de las 17:00 NY, tres semanas en cada cambio de hora.
- Re-run sobre v2: un qn con las 1d de fx28 publicadas con la regla congelada. La fase C da 0 nuevas, 0 publicadas, 0
  revisiones y 0 huecos de cola, y después sigue igual que v2.

## Huecos de mercado por clase

En 1d, para todo menos fx, cada día que falta entre dos sesiones se clasifica (`calendarios.huecos_sesiones`):
- **fin de semana**: sábado o domingo. En cripto también: el broker no daba cripto en fin de semana en su historia
  antigua.
- **festivo**: está en el calendario de la bolsa.
- **festivo probable**: una racha de 1 a 3 laborables fuera del calendario, en una clase con bolsa. Cubre las fiestas
  lunares (Hong Kong, China) y los festivos que el CFD hereda de su futuro.
- **otros**: el resto, que es un hueco de verdad.

Fx sigue con el método de siempre, para no cambiar sus informes. El intradía de las clases nuevas también, porque queda
para cuando se amplíen los periodos.

Los huecos sólo se informan, en el manifest de la descarga y en el registro del publicador. Ni paran la descarga ni la
publicación, ni la de esa serie ni la de las demás. El test lo comprueba con un martes sin cripto.

Calendarios por reglas (fechas fijas con su traslado, Pascua, n-ésimo día de la semana; NYSE con sus cierres
extraordinarios desde 1990). Contra la caché real, últimos 3 años:

| Índices | Festivos | Probables | Otros |
|---|---|---|---|
| AUS200, CA60, DE40, MidDE50, STOXX50, ES35, F40, NETH25, IT40, UK100, SWI20, US30, US500, USTEC, US2000 | 8 a 33 | 0 | 0 |
| HK50, CHINAH (fiestas lunares) | 24 | 22 | 0 |
| JP225 (cierra como su futuro de Chicago: 25 dic, Viernes Santo) | 3 | 5 | 0 |
| CHINA50, SA40, SE30, TecDE30 | 8 a 32 | 1 a 4 | 0 |
| NOR25 | 32 | 2 | 1 (la semana del 28-sep al 2-oct de 2026 sin velas) |

En cripto, las alts no tienen vela el 2025-12-05 en el broker. Ese día sale como hueco `otros`, y lo es.

## Ritmo de publicación (para el Bento del backend)

El Bento del backend aguanta unos 180.000 objetos por sondeo de 5 minutos. El publicador tiene dos topes, los dos sin
límite por defecto, así que la tarea diaria no cambia:
- `--max-objetos-por-5min N`: como mucho N objetos enviados en cualquier ventana deslizante de 300 s. Si no caben,
  espera a que caduquen los más antiguos.
- `--max-objetos N`: como mucho N objetos por ejecución. El resto queda para la siguiente pasada.
  - Se publica un prefijo en orden de `ts`, así que no deja huecos por detrás de `L`.
  - La siguiente pasada sigue desde lo que qn confirma, por el diseño idempotente.
  - Las series que no llegan a empezar quedan marcadas `parada_por_tope`.

Los dos cuentan todo lo enviado, también lo que qn da por duplicado. El registro lleva `ritmo` con lo enviado, el tiempo
esperado y si se alcanzó el tope. El selftest lo comprueba:
- con `--max-objetos 100` cada pasada publica como mucho 100 y la serie acaba igual que MT5, sin duplicados;
- con `--max-objetos-por-5min 100`, con un reloj falso, nunca hay más de 100 en 300 s.

Para una carga histórica propongo dejar margen:
- `--max-objetos-por-5min 150000` en una ejecución a mano;
- o `--max-objetos 150000` en pasadas cada 15 min, que son 50.000 por 5 min.

## Volumen estimado en qn

Velas 1d desde 2000. Lo medido sale de la caché local de la descarga del 2026-11-09; lo estimado se escala desde los
símbolos ya descargados.

| Grupo | Símbolos | 1d (velas) | Cómo |
|---|---|---|---|
| fx28 (ya publicado) | 28 | 178.522 | medido |
| resto de fx60 | 32 | 125.555 | medido |
| metales_energia | 16 | ~60.000 | estimado (2 de 16 descargados; desde ~2012) |
| indices | 23 | 73.525 | medido |
| crypto | 17 | ~41.500 | 14 de 17 medidos |
| crypto_alts | 77 | ~50.600 | 74 de 77 medidos (casi todas desde dic-2024) |
| **nuevo de `@continuo`** | 165 | **~351.000** | |
| `@us_grandes` | 484 | 1,2 a 3,3 M | sin medir: 252 sesiones/año durante 10 a 26,8 años |

Incremento diario en 1d: unos 680 objetos (193 + 484, y la cripto también en fin de semana).

**Duración de la carga 1d al ritmo del Bento.**
- A 180.000 por 5 min (600 objetos/s), si el publicador da para tanto:
  - `@continuo` nuevo: 2 ventanas, unos 10 min;
  - `@us_grandes`: 7 a 19 ventanas, de 35 min a 1,5 h.
- A 150.000 por 5 min (con margen):
  - `@continuo`: unos 12 min;
  - `@us_grandes`: de 40 min a 1 h 50 min.
- Si el publicador real no pasa de unos 200 objetos/s (el ritmo de la primera publicación de fx28 da la cifra real), el
  tope no llega a actuar:
  - `@continuo`: unos 30 min;
  - `@us_grandes`: de 1 h 40 min a 4 h 30 min.

**1h, para pedir el visto bueno más adelante.** El terminal sólo sirve 100.000 velas por serie (`maxbars`; unos 16 años
de fx en 1h).

| Grupo | Velas 1h/año | Carga histórica (≤ 100.000 por serie) | Diario |
|---|---|---|---|
| fx60 | ~6.200 | ~6,0 M | ~1.440 |
| metales_energia | ~6.000 | ~1,4 M | ~370 |
| indices | ~5.000 | ~1,6 M | ~460 |
| crypto + alts | 8.760 | ~2,1 M | ~2.260 |
| us_grandes (7 velas por sesión) | ~1.760 | 8,5 M (10 años) a 23 M (desde 2000) | ~3.400 |

Totales:
- `@continuo` en 1h: ~11 M, que son ~5 h 10 min a 180.000 por 5 min.
- `@us_grandes` en 1h: de 4 h a 11 h a ese ritmo.
- El incremento diario de 1h de todo es de unos 8.000 objetos.

Queda por medir en el terminal real (riesgo de la entrega 6b): si `copy_rates_range` da 1h más atrás de `maxbars`.

## Descarga local de las acciones

`--descargar --simbolos @us_grandes --periodos d1 --desde ... --hasta ...` funciona igual que con fx:
- el nombre de fichero de `BF/B.NYSE` se sanea a `BF_B.NYSE~<hash>`;
- el manifest lleva por serie `clase` y `bolsa`, y en 1d los huecos por clase con el método `sesiones 1d por clase`.

Una descarga con las claves nuevas no da el mismo `hash_conjunto` que una anterior a la fase C. Fx sin clase (rutas de
fuera del terminal real) no cambia.

## Evidencia (selftest)

- Extractor:
  - `prueba_calendarios`: Pascua; la NYSE de 2026 completa; los traslados de 2021 y 2022; los festivos medidos en el
    terminal real de ASX y TSX; huecos de índice, cripto y acciones.
  - `prueba_universos`: un broker falso con las carpetas del real da los grupos, los excluidos, el cruce del S&P 500
    (`-24`, clases con `-` y `/`, la bolsa cambiada) y las etiquetas. También se comprueban `@fx28`, un universo
    desconocido, el wikitext y el fichero del repo (60/16/23/17/77/193, 503 = 484 + 19).
  - `prueba_clases_extremo_a_extremo`: `--descargar --simbolos @us_grandes,@continuo --periodos d1` con huecos por clase.
    Las acciones y los índices tienen festivos y 0 otros; la cripto tiene velas de fin de semana; un martes sin cripto
    es 1 otro; fx sigue con el método de siempre.
- Publicador:
  - `prueba_regla_1d_igual_que_v2` y el re-run sobre v2 (arriba);
  - `prueba_ritmo_unitario`;
  - `prueba_fase_c_extremo_a_extremo`: los topes de ritmo; las etiquetas `BRK-B` y `BF-B`; la vela de acciones del
    miércoles, que no sale a las 16:30 NY y sí a las 17:30 NY; la cripto de sábado y domingo con su `ts`; el contrato
    de v2; un hueco de cripto que no para nada; sin secretos ni funciones prohibidas.
