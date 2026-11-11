# HANDOFF de la raíz — relevo 1

## Relevo
- Número: 1
- Sale: sesión 94a84b92-a920-4b9a-96e1-3ee168da18ba, claude-opus-5-5, contexto 66.5 %
- Escrito: 2026-11-11T13:06:56+01:00
- HEAD al escribir: 8bbc05773792fc190ef8dfdb66f97dcd8994c037
- LAUNCH: docs/plans/current/LAUNCH.md · bloque del coordinador: «8. Prompt de la raíz»
- Relevos anteriores: `git log --follow -- docs/plans/current/HANDOFF.md`
- Aceptado: sesión 138afa9a-12f1-4261-8404-25aedb87920b, 2026-11-11T13:09:28+01:00, contexto inicial 21.3 %

## Arranque
1. `D:/miniconda312/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/tools/claude_or.py handoff accept docs/plans/current/HANDOFF.md`: valida este archivo y anota tu sesión.
2. Lee sólo esto: este archivo, el bloque del coordinador del LAUNCH, `docs/plans/SPRINT_PROJECT.md` (y las
   políticas que liste), la skill global `sprint` (`C:/Users/makiolo/.claude/skills/sprint/SKILL.md`, `references/launch.md`,
   `references/handoff.md`) y las fichas de los hijos en vuelo. El resto, cuando haga falta y delegando.
3. `git status`, el estado del gate o candados de SPRINT_PROJECT «Comandos» y `git log --oneline 8bbc05773792..HEAD`.
4. Adopta los hijos en vuelo: comprueba su proceso y su salida y vigílala; no relances un ID vivo.
5. Lanza el vigía de caché con `run_in_background` desde la raíz del repo:
   `D:/miniconda312/python.exe -X utf8 C:/Users/makiolo/.claude/skills/sprint/scripts/cache_heartbeat.py` (`references/handoff.md`, «Latido de caché»).
6. Busca en la memoria del proyecto (SPRINT_PROJECT «Identidad») las palabras clave del siguiente paso.
7. Commit del HANDOFF con la aceptación y continúa con «Siguiente paso».

## Estado
Ola 1 de SPRINT-02 (detalle completo en `docs/plans/current/EXECUTION.md`, sección «Raíz inicial» y tabla «Registro»).

| Fila | ID | Estado | Evidencia |
|---|---|---|---|
| 2b | TS-00-BENCH (FinCast) | **CERRADA** (A4 ronda 2 ACEPTAR) | código `f3f8a4d`…`05c27cf`, cierre `09befb8`; informe `current/execution/TS-00-BENCH-FINCAST/informe.md` |
| 1b-A | TI-02-DATA-V2, código + regeneración de los 4 datasets con `0e67465` (4/4 idénticos) | **ACEPTADA** (A4 ronda 4 ACEPTAR) | código `3e35ed5`, informe `565f9a0`, registro `8bbc057`; informe `current/execution/TI-02-DATA-V2/informe.md` (órdenes del paso 1 en `:89-97` y del paso 2 en `:104-110`) |
| 1b-B | volcado v2 del FX 1d de MT5 desde qn + exportación de `mt5_fx28_cierre_c20261101` y `mt5_fx28_hist_cierre_c20261101` + cuadre | **espera al usuario** (necesita su `QN_TOKEN`; ver Preguntas) | — |
| 1b-C | dos tablas del banco (cabecera y ampliación, con FinCast) + informe + umbrales TS-00-OBJ | sin empezar (tras 1b-B) | — |
| 5 | TI-12-MT5 | **en espera**: cuenta MT5 bloqueada (usuario, 2026-11-11). Alcance fijado: h1 de `@continuo`, sin símbolos nuevos | — |
| 6 | TI-09-ARCH | **en espera** de OC-03 del backend (avisarán) | — |
| 7 | TI-13-PUB | ola 2 desbloqueada (1b-A aceptada); **pregunta enviada** a `quantdesk-backend-fe` sobre qué hay publicado en qn (topic, `source`, intervalos, rango) | mensaje entre sesiones 2026-11-11 ~13:05 |

BDD de sprints: TS-00-BENCH cerrada; TI-02-DATA-V2 sigue en curso (B y C). Filas viejas LAB-00-ENV, TI-02-DATA,
TS-00-PREC marcadas `arrastrada` (están en SPRINT-03). Último intento abierto: ninguno (148…189 cerrados).

## En vuelo
Ninguno. (El vigía de caché de la saliente se apaga con ella; la sucesora lanza el suyo.)

## Decisiones
- Usuario (2026-11-11, chat): Codex disponible al 100 %; **sin IA local** hasta nuevo aviso; FinCast «Sí, pesos y
  código»; fila 5 = h1 de `@continuo`, sin símbolos nuevos; cuenta MT5 bloqueada otra vez; ofreció
  `D:\dev\deeplearning_dev\dataset\h1_period-1h_fa79d8045dce76d4.parquet` (h1 fx28 desde 2010, export MT5 sin zona
  declarada): **no** sirve para la tabla FX 1d; candidato para el h1 de fx28 de la fila 5 si el usuario lo decide.
  Versionado en EXECUTION «Raíz inicial».
- Retransmitidas: L7–L10 con astra/Opus (sin efecto, sprint L5–L6); cola global de compilación `e83badb` (rechazada
  de momento; este proyecto no empuja). EXECUTION «Registro».
- Raíz (A12), en fichas y EXECUTION: ventana limpia > 2025-08-27T00:00Z; CRPS de FinCast sólo deciles nativos
  (`crps_deciles` para todos); monotonía estricta sólo para FinCast (los modelos de SPRINT-01 cuentan cruces, no fallan:
  si no, chronos2 pierde el 20 % de orígenes al reejecutarse); fila 1b partida A/B/C; FX = ISO 4217 + CNH, sin fondos;
  `mt5` 1d: versión completa desde el cierre real 17:00 NY, última versión completa ≤ corte si existe (si no, la
  conducta de `5b70106`, proxy en `cierre`), disponibilidad en `recepcion` = max(`_recv_ts`, `ts`+intervalo); fallo
  «dos fuentes» por (instrumento, intervalo), más estricto que por ts (desviación declarada).
- Modelos usados: autores Codex `gpt-6.1-sol` xhigh (`codex exec`, fichas en `.git/sprint-runtime/s02/<ID>/`);
  revisores Sonnet 5.5 xhigh (Agent); revisión A2 de fichas con Codex `gpt-6-luna` high (`-s read-only`).

## Preguntas abiertas al usuario
1. **Fila 1b-B, volcado de qn (bloquea 1b-B y 1b-C).** El volcado no usa el terminal MT5 (el 1d ya está en qn), sólo
   `QN_URLS`/`QN_TOKEN`/`QN_ENV=main` en el entorno del usuario. Orden (informe de TI-02-DATA-V2 `:92`), con el
   `descarga_lago.py` **nuevo** (`git -C S:/Projects/quantdesk-model show 3e35ed5:scripts/descarga_lago.py`, sólo
   biblioteca estándar): `python3 descarga_lago.py --topics market.ohlcv.v2 --source mt5 --interval 1d --symbols
   <los 28 de fx28, ver informe :92> --desde 2000-01-01 --hasta 2026-11-10 --trozo-dias 10000 --salida <dir>`, y
   copiar el volcado con su `manifest.json` a `E:/quantdesk-lab/data/lago/mt5_fx28_20000101_20261110/` (preferible a la
   ruta `tmp/` del informe; ajustar `--lago` del paso 2). Opciones: (a) en mini como en SPRINT-01 (recomendado);
   (b) aquí, en su terminal, con `! <orden>`. Tras el volcado, la raíz exporta, cuadra y lanza 1b-C.
2. **Propuesta de mejora del arnés (raíz, delegation §8):** en esta sub-entrega hubo 4 rondas de corrección, 2 por
   errores de la ficha de la raíz (horas de cierre; regla de disponibilidad incompatible con DPOL-AVL-002) y 2 por
   efectos de un cambio de semántica de datos que sólo vio un diferencial. Propuesta: en toda ficha que cambie la
   semántica de datos (limpieza, disponibilidad, versiones, fuentes), exigir al autor un **test diferencial contra el
   commit anterior sobre un fixture realista** (forma de la publicación real, p. ej. historia publicada después del
   corte) y que la raíz contraste sus ejemplos numéricos con la fuente antes de lanzar. Coste: ~30 min de autor por
   ficha; ahorro estimado: 2 rondas de revisión aquí. Si acepta, aplicarlo en `references/ficha.md` de la skill (copia
   `.bak-<fecha>`) y avisar a las demás raíces.

## Conocimiento promovido
- Memoria del proyecto: trampa del Bash de Claude en este equipo (variables vacías con `%s` en `--format` o con
  backticks en `printf`; mensajes de commit sólo con `git commit -F <fichero escrito con Write>`); script
  `E:/quantdesk-lab/tmp/verif-archive.sh <commit> <script.py>…` para verificar selftests sobre `git archive`.
- Bloqueo de la cuenta MT5 el 2026-11-11 añadido a la memoria `mt5-descargas-prudentes`.

## Siguiente paso
Comprobar si llegó la respuesta de `quantdesk-backend-fe` (fila 7) y la del usuario sobre el volcado (pregunta 1, que
retransmite la saliente). Si el backend tiene datos publicados, redactar la ficha de la fila 7 (L5, autor Codex
`gpt-6.1-sol` high, revisor `gpt-5.6-terra` high; pasa por TI-02-DATA-V2 con una regla de fuente por clase y también
necesita un volcado del usuario: juntarlo con el de 1b-B si se puede). Si no, la fila 7 sale con causa documentada.
