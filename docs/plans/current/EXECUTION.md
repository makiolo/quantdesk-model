# EXECUTION — SPRINT-02 de quantdesk-model

Registro de ejecución del sprint. Lo crea la activación; la raíz del [LAUNCH](LAUNCH.md) lo continúa.

## Activación (2026-11-11)

- **Decisión del usuario (2026-11-11):** partir SPRINT-02 y activarlo ya, sin esperar al cierre de quantdesk
  SPRINT-02 (activo, 66 entregas cerradas de unas 328). Las filas 1–4 pasan a SPRINT-03 como S02-1…S02-4
  (elegido frente a crear un sprint nuevo o devolverlas al backlog). Commit `bb809e4`, etiqueta
  `archive/2026-11-11/sprint-02-sources`.
- **Decisión del usuario retransmitida (2026-11-10, vía la raíz de `quantdesk`, relevo 44):** Haiku 5.5 ni autor ni
  revisor; L3–L6 con Sonnet 5.5 high o `gpt-6.1-sol` high hasta L5; tabla «caso borde → test» y revisión obligatoria
  en L3–L4 hasta el 2026-11-24 (SPRINT_PROJECT §6). Aplicada en LAUNCH §2.
- `deps.py --sprint SPRINT-02`: LISTO (0 dependencias de entrada).
- Revalidación: fuentes sin cambios desde la revisión de planes del 2026-11-10; `scripts/descarga_lago.py:57` sigue
  leyendo `market.ohlcv` (v1), como describe la fila 1b.
- Cuota (`claude-or quota --weekly`, 2026-11-11 07:27 UTC, api): Claude 28 % con el 18,7 % de la ventana (reinicio
  2026-11-16 23:59 UTC); Codex 0 %, ventana sin empezar. Coordinador de costes: la raíz del LAUNCH.
- Issue que entra al sprint: ISSUE-LAGO-FX-1D-CLOSE (fila 1b), movida a [issues/](issues/index.md).

## Raíz inicial (2026-11-11)

- Arranque de la raíz inicial del LAUNCH (Opus 5.5 high, sin relevo previo), ~08:00 UTC.
- `deps.py --repo . --sprint SPRINT-02`: **LISTO**, 0 dependencias de entrada.
- Cuota antes de la ola 1 (`claude-or quota --weekly`, 2026-11-11 08:01 UTC, api): Claude 28 % con el 19,1 % de la
  ventana (reinicio 2026-11-17 00:00 UTC); Codex 0 %, ventana sin empezar. `claude-or route --level 6` → Codex
  `gpt-6.1-sol` xhigh.
- Aviso de quantdesk-backend (raíz de su SPRINT-02, relevo 1, mensaje entre sesiones, 2026-11-11): OC-01 y OC-02
  cerradas en su SPRINT-01; para la fila 6 (TI-09-ARCH) sigue pendiente OC-03 (entregas b y c tras la sonda de bid/ask
  de Yahoo de esta noche, 22:20–23:00 hora local). Avisarán al cerrar OC-03. Fila 6 sigue sin empezar.
- **Decisiones del usuario (2026-11-11, chat de la raíz):** «Ya se puede usar modelos de codex, 100% disponible»;
  «De momento seguimos con la prohibicion de no usar IA local, hay que terminar las suscripciones». Efecto: autores L5–L6
  por Codex mientras tenga margen; ningún autor local (`claude-local`) en este sprint hasta nuevo aviso.
- Decisiones de la raíz (A12) para la fila 2b, en su ficha: ventana limpia = orígenes > 2025-08-27T00:00Z para todos
  los modelos; CRPS de FinCast sólo sobre sus 9 deciles nativos, con columna `crps_deciles` para todos en la tabla
  limpia; criterios de colas de FinCast no aplicables (declarados); submuestra fijada tras un piloto (≤ ~8 h por tabla).
- Fila 1b partida en sub-entregas: **A** código TI-02-DATA-V2 y regeneración de los 4 datasets con el código de
  `0e67465` (sin qn); **B** volcado v2 del FX 1d de MT5 desde qn (lo ejecuta el usuario con su credencial) y exportación
  de los datasets de cabecera y ampliación, con cuadre; **C** las dos tablas del banco, informe y revisión de umbrales.
- **Respuestas del usuario a las puertas (2026-11-11, AskUserQuestion de la raíz):**
  - Fila 2b: «Sí, pesos y código» (FinCast `v1.pth` 3,97 GB de huggingface.co/Vincent05R/FinCast y código de
    github.com/vincent05r/FinCast-fts, por revisión fijada, a `E:/quantdesk-lab`). Puerta 3 cumplida.
  - Fila 5: periodos nuevos = **h1 de @continuo**; símbolos nuevos = **ninguno** (sólo periodos).
  - Fila 1b, volcado de qn: «Ahora mismo MT5 nos ha bloqueado la cuenta, hay que esperar un poco, para ver si la
    recuperamos. Pero tal vez te pueda servir D:\dev\deeplearning_dev\dataset\h1_period-1h_fa79d8045dce76d4.parquet
    son 28 pares de FX desde 2010». Efecto: **fila 5 en espera** (necesita el terminal MT5) hasta que el usuario
    recupere la cuenta. El parquet ofrecido (leído sólo su esquema: 2 799 685 filas, `time, open, high, low, close,
    tick_volume, spread, symbol`; formato de exportación de MT5, zona horaria sin declarar) es h1, no 1d, y no viene de
    qn: no sustituye a la tabla FX 1d de la fila 1b; queda anotado como fuente candidata del h1 de fx28 (fila 5) si el
    usuario lo decide. El volcado de qn de la sub-entrega 1b-B no usa el terminal MT5 (el 1d ya está en qn): se le
    preguntará de nuevo dónde lo ejecuta cuando 1b-A esté aceptada.
- Revisión A2 de las fichas 1b-A y 2b-A (Codex `gpt-6-luna` high, sólo lectura): 2 preguntas cada una (filtros y
  nombres del volcado y la exportación; revisiones fijadas y método de cuantiles no nativos), resueltas por la raíz en
  las fichas antes de lanzar.
- **Decisión del usuario retransmitida (2026-11-11, vía la raíz de `quantdesk-backend`, relevo 1):** en L7–L10,
  `gpt-6-astra` xhigh es autor posible junto a Opus 5.5 high; escribe el del proveedor con más margen
  (`claude-or route --level N`) y revisa el otro; L7–L8 siguen con sol/Sonnet xhigh por defecto; L10 lo decide la
  raíz. Ya en la skill global (`niveles-y-modelos.md`, `claude_route.py`). Sin efecto en este sprint (todas sus
  tareas son L5–L6); el LAUNCH no cambia.
- Ola 1: auditorías de sólo lectura (Sonnet 5.5, Explore) de las filas 1b, 2b y 5 para redactar las fichas.

## Registro

| Fecha | ID | Evento | Commit / evidencia |
|---|---|---|---|
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | Autor lanzado: Codex `gpt-6.1-sol` xhigh, `codex exec` en segundo plano; ficha en `.git/sprint-runtime/s02/TI-02-DATA-V2-A/` | base `934d9af`; intento 148 |
| 2026-11-11 | TS-00-BENCH (2b-A, FinCast) | Autor lanzado: Codex `gpt-6.1-sol` xhigh, `codex exec` en segundo plano; ficha en `.git/sprint-runtime/s02/TS-00-BENCH-FINCAST/` (con autorización de descarga) | base `934d9af`; intento 149 |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | Autor entrega `27cfb2b` (15 rutas autorizadas). Verificación de la raíz en `git archive 27cfb2b` (`E:/quantdesk-lab/tmp/verif-27cfb2b`): `descarga_lago.py --selftest` y `exportar_market_history.py --selftest` «selftest ok»; 4/4 datasets regenerados con el código de `0e67465` idénticos byte a byte a los originales (sha256 de parquet + manifest). Revisión A4 lanzada: Sonnet 5.5 xhigh (Agent), sin el informe del autor | `27cfb2b`; intentos 148 (autor) y 159 (A4) |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | A4 (Sonnet 5.5 xhigh): **ACEPTAR CON CONDICIONES**, confianza alta, A5 legítimo. MEDIA reproducidos: clasificación FX con sólo 8 divisas (USDMXN de `market_scraper` pasaría como no FX); velas 1d de MT5 publicadas en vivo (recepción ~21:30 UTC, antes de `ts`+1 d) descartadas como `version_en_curso` por `limpieza.py:126`. BAJA: dos ramas sin test; ruta fija en el selftest. Desviación aceptada por la raíz (A12): el fallo «dos fuentes» por (instrumento, intervalo), más estricto que por ts, declarado. Decisión de la raíz (A12): para `source=mt5` 1d, «versión completa» desde el cierre real de la sesión (17:00 NY de D); la disponibilidad no cambia. Corrección 1 lanzada (mismo autor) | intentos 159 (A4), 161 (corrección) |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | Corrección 1 entregada `0684a93`: FX ISO 4217 (164 códigos), tests de tags, temporal portable; cierre real MT5 1d aplicado y contrastado con `publicador_mt5_lib.nucleo.sesion_1d`. **BLOQUEADA** por error de la raíz en la ficha: horas de ejemplo equivocadas (cierre 22:00Z invierno / 21:00Z verano) y «la disponibilidad no cambia» choca con DPOL-AVL-002 del motor (recepción anterior a `ts`+1 d). Decisión de la raíz (A12): en `recepcion`, disponibilidad = max(`_recv_ts`, `ts`+intervalo). Corrección 2 lanzada | `0684a93`; intentos 161 (bloqueado), 167 |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | Corrección 2 entregada `f48dfe9` (código) + `5b70106` (informe): disponibilidad en `recepcion` = max(`_recv_ts`, `ts`+intervalo); A12 sin violaciones DPOL-AVL-002; hashes sin MT5 2/2, MT5 tardío 2/2, históricos 4/4 (según el autor). Verificación de la raíz en `git archive 5b70106`: los dos `--selftest` «selftest ok». A4 ronda 2 lanzada (Sonnet 5.5 xhigh) sobre `27cfb2b..5b70106` | intentos 167, 172 |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | A4 ronda 2 (Sonnet 5.5 xhigh): **ACEPTAR CON CONDICIONES**, confianza alta, A5 legítimo. Sin look-ahead (regla de cierre real contrastada con `nucleo.sesion_1d` en 9811 fechas, 0 diferencias); hashes sin MT5 temprano idénticos; 7 mutaciones detectadas. **ALTA latente reproducida:** la versión incompleta de las 23:01Z del 2026-11-09 gana a su republicación (cortes ≥ 2026-11-10, 23 pares). BAJA: CNH, códigos ISO de fondos, guarda de `ts` 00:00Z. Decisión de la raíz (A12): en `mt5` 1d, la última versión completa antes del corte, con su recepción como disponibilidad (`version_mt5_revisada`). Corrección 3 lanzada | intentos 172 (A4), 177 |
| 2026-11-11 | TS-00-BENCH (2b-A, FinCast) | Autor entrega `f3f8a4d`, `a98cea8`, `84fe1a9`, `d422e48`, `c0c7633`. Pesos `v1.pth` sha256 `d5ca999b…` (`torch.load(weights_only=True)`, `OrderedDict` de 1713 tensores, `strict=True`); código `FinCast-fts@488b19d`, pesos HF `@2d7d90b`; Apache-2.0 verificada en ambas revisiones. CPU por origen: FX 1,72 s, Binance 2,73 s (no 7× Toto). Submuestra FX `--cada 5` (1391/1400 válidos), Binance `--cada 10` (110/130). Verificación de la raíz en `git archive c0c7633`: `banco_walkforward.py --selftest` «selftest ok». A4 lanzada (Sonnet 5.5 xhigh) | intentos 149, 178 |
| 2026-11-11 | TS-00-BENCH (2b-A, FinCast) | A4 (Sonnet 5.5 xhigh): **ACEPTAR CON CONDICIONES**, confianza alta, A5 legítimo. Recalculadas las 570 celdas limpias (Δ ≤ 5e-9); tabla principal byte a byte igual a SPRINT-01; máscara, CRPS deciles, cuantiles en z y carga segura correctos. MEDIA: ventana limpia de Binance condicionada (90/130 orígenes comunes; FinCast falla 20 por deciles no monótonos); la comprobación de monotonía para todos los modelos (error de la ficha de la raíz) haría fallar a Chronos-2 en una reejecución (cruces en h=1, 20,7 %). Decisión de la raíz (A12): fallo por monotonía sólo para FinCast; en los modelos de SPRINT-01, cruces contados y declarados. 5 BAJA. Corrección 1 lanzada | intentos 178 (A4), 179 |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | Corrección 3 entregada `d4103ad` (código) + `2021763` (informe): última versión completa de `mt5` 1d antes del corte (AUDCAD 0.97762 con corte 2026-11-11; 0.9768 con corte 2026-11-10T05:00Z), CNH, fondos fuera, guarda `ts` 00:00Z. Verificación de la raíz en `git archive 2021763`: los dos `--selftest` «selftest ok». A4 ronda 3 lanzada (Sonnet 5.5 xhigh) | intentos 177, 180 |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | A4 ronda 3 (Sonnet 5.5 xhigh): **ACEPTAR CON CONDICIONES**, confianza alta, A5 legítimo. Regla AUDCAD, look-ahead (4 cortes × 2 modos, 237 casos aleatorios), CNH/fondos/guarda correctos. **ALTA reproducida:** en `cierre` desaparecen las barras `mt5` 1d cuya única versión completa llegó tras el corte (toda la historia MT5 se publicó el 2026-11-09 → los datasets de la parte B saldrían vacíos). Decisión (A12): la última versión ≤ corte sólo si existe; si no, el comportamiento de `5b70106`. Corrección 4 lanzada | intentos 180 (A4), 181 |
| 2026-11-11 | TS-00-BENCH (2b-A, FinCast) | Corrección 1 entregada `ce1150d` + `05c27cf`: monotonía estricta sólo para FinCast, cruces de los modelos de SPRINT-01 contados; tabla limpia regenerada (n por horizonte 1391 FX / 110 Binance; efecto de selección +1,55–2,50 % en CRPS deciles base a h=1; sha256 `8dd0dc0f…`). Verificación de la raíz en `git archive 05c27cf`: `--selftest` del banco «selftest ok»; `tablas/metricas.csv` idéntico byte a byte a SPRINT-01. A4 ronda 2 lanzada (Sonnet 5.5 xhigh) | intentos 179, 184 |
| 2026-11-11 | TS-00-BENCH (2b-A, FinCast) | A4 ronda 2 (Sonnet 5.5 xhigh): **ACEPTAR**, confianza alta, A5 legítimo. 570 celdas recalculadas (Δ ≤ 4,9e-10 rel.), cruces recontados (chronos2 h=1: 187 FX, 283 Binance), reejecución de chronos2 idéntica bit a bit, 5 mutantes de monotonía y 6 de interpolación detectados, puertas de seguridad probadas. BAJA no bloqueantes: `verificacion.md` refleja `c0c7633` (la evidencia vigente está en `correccion1/`); purga de submódulos y chequeo de `cfg.quantiles` sin test; `repetir_chronos2.py` sin `OMP/MKL_NUM_THREADS=1`. **FILA 2b CERRADA** (sub-entrega A; FinCast entrará en la tabla FX de cabecera de MT5 dentro de la fila 1b-C). Commits `f3f8a4d`, `a98cea8`, `84fe1a9`, `d422e48`, `c0c7633`, `ce1150d`, `05c27cf`; selftest del banco verificado por la raíz en `git archive 05c27cf`; principal idéntica a SPRINT-01 (`cmp`); tabla limpia sha256 `8dd0dc0f…` | intentos 149, 178, 179, 184 |
| 2026-11-11 | — | Commit ajeno `e83badb` (otra sesión, SPRINT_PROJECT: `maturin build` por la cola global de compilación, decisión del usuario): no afecta a este sprint (sin builds) | `e83badb` |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | Corrección 4 entregada `e211f31` + `3e35ed5` (código) + `565f9a0` (informe): en `mt5` 1d sin versión completa antes del corte, comportamiento de `5b70106` (proxy en `cierre`); contadores sin cambios si no hay revisión. Verificación de la raíz en `git archive 565f9a0`: los dos `--selftest` «selftest ok». A4 ronda 4 lanzada | intentos 181, 189 |
| 2026-11-11 | — | Aviso de quantdesk-backend-01 (mensaje entre sesiones): `e83badb` es suyo (cola global de compilación `build_queue.py`, pedida por el usuario); la revisión independiente rechazó la primera versión de la cola, así que se sigue compilando como hasta ahora hasta su aviso. Pide subirlo «con tu próximo push»: este proyecto **no empuja** (SPRINT_PROJECT §2, usuario 2026-11-08), así que queda en el commit local; sin builds en este sprint | `e83badb` |
| 2026-11-11 | TI-02-DATA-V2 (1b-A) | A4 ronda 4 (Sonnet 5.5 xhigh): **ACEPTAR**, confianza alta, A5 legítimo. Caso del ALTA: 12 filas en `cierre` con el hash de `5b70106`; a escala real (28 pares, 140 031 filas, corte 2026-11-01) 136 024 filas idénticas a `5b70106`; AUDCAD correcto (incluido el corte exacto 09:35); 1 200 casos aleatorios sin look-ahead nuevo (las 69 violaciones de `cierre` son el proxy declarado, idénticas en `5b70106`). BAJA no bloqueantes: `version_mayor_diferencia` de `procedencia.json` ya no refleja revisiones posteriores al corte (más causal; fuera del hash); dos completas idénticas cuentan como `version_mt5_revisada`. **SUB-ENTREGA 1b-A ACEPTADA** en `3e35ed5` (código) / `565f9a0` (informe). Siguiente: 1b-B (volcado de qn por el usuario) | intentos 181, 189 |
| 2026-11-11 | TI-12-MT5 (5) | En espera: cuenta MT5 bloqueada (usuario); alcance fijado: h1 de @continuo, sin símbolos nuevos | — |
| 2026-11-11 | TI-09-ARCH (6) | No empieza: OC-03 del backend pendiente (aviso del backend) | — |
| 2026-11-11 | — | Relevo 1 de la raíz: sucesora `quantdesk-model-76` (sesión 138afa9a), HANDOFF aceptado; `deps.py --sprint SPRINT-02` LISTO; cuota semanal 13:15 local: Claude 34 % (ventana 21,6 %, reinicio 2026-11-17 00:00), Codex 6 % (ventana 2,4 %, reinicio 2026-11-18 08:07). Pedida a la saliente la respuesta de `quantdesk-backend-fe` (fila 7) y avisado el backend del cambio de raíz | `9745ea6`, `c1fa7ff` |
| 2026-11-11 | TI-02-DATA-V2 (1b-B) | **Decisión del usuario retransmitida por la sesión saliente** (AskUserQuestion, relevo 1): el volcado de qn lo ejecuta el usuario «En mini, como en SPRINT-01», con el `descarga_lago.py` de `3e35ed5`, y lo copia con su `manifest.json` a `E:/quantdesk-lab/data/lago/mt5_fx28_20000101_20261110/`; avisará. Después la raíz exporta (paso 2 del informe, `--lago` a esa ruta), cuadra y lanza 1b-C | — |
| 2026-11-11 | — (arnés) | **Decisión del usuario retransmitida por la sesión saliente**: «Sí, aplicarlo globalmente» a la propuesta del HANDOFF. Aplicado en la skill global `references/ficha.md` (copia `ficha.md.bak-20261111b`): test diferencial contra `Base` sobre fixture realista en toda tarea que cambie la semántica de datos, y contraste por la raíz de cada ejemplo numérico, hora o regla de la ficha con su fuente antes de lanzar. Aviso entregado a `quantdesk-backend-f5`; `quantdesk-69` y `quantdesk-network-5f` (de `relevos.json`) no están conectadas: la regla ya vale para ellas por estar en la skill global | — |
