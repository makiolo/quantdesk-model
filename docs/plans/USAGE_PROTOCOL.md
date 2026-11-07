# Medición de cuota y costes por tarea, raíl y sprint — quantdesk-model

Protocolo de la skill global `sprint`, vigente desde 2026-11-07. Objetivo: presupuestar cada sprint
con evidencia de los anteriores. Mensualidades y herramientas de lectura: SPRINT_PROJECT «Costes».
Preparar registros no activa un sprint.

## 1. Qué medimos y dónde

La unidad es el **punto porcentual (pp) de una cuota semanal de un proveedor**: pasar de 20 % a 23 %
consume 3 pp. Cada proveedor, cuenta, barra y régimen de límites se conserva por separado. No sumar
proveedores distintos ni una barra general con una subcuota que mide parte del mismo uso. Las
ventanas cortas (p. ej. 5 h) se registran para disponibilidad, nunca se convierten en semanas.

Registro canónico de cuenta en [usage/](usage/README.md), compartido entre sprints para que un
intervalo concurrente no se contabilice dos veces: `observations.csv` (lecturas de cuota),
`intervals.csv` (pares no solapados y su diferencia), `allocations.csv` (una sola distribución de
cada intervalo), `tokens.csv` (tokens por segmento y equivalente API), `tariffs.csv` (tarifas
versionadas), `subscriptions.csv` (mensualidades) y `tasks.csv` (aceptación y cobertura por tarea).

Cada dossier tiene `USAGE.md`, informe derivado con presupuesto/real/desviación, cobertura y enlaces
al registro, fecha de corte y commit. El registro no se mueve al archivar. Evidencia privada fuera
de Git (`.git/sprint-usage/`), sin prompts, credenciales ni datos de autenticación.

## 2. Responsables y momentos de captura

Un **coordinador de medición por cuenta** integra los CSV; los subagentes no escriben el registro a
la vez. Capturar lectura fresca: al iniciar sesión/raíl; antes de asignar cada tarea o intento; cada
~30 min con trabajo concurrente o al cambiar tarea/modelo/proveedor; al terminar, pausar, fallar o
relevar; y en cierre de jornada, reinicio o cierre de sprint. Si el agente no puede leer una barra,
pedir al usuario porcentaje usado, hora y próximo reinicio; sin dato, `missing` (nunca 0).

## 3. Intervalos

Un intervalo medible requiere misma cuenta/barra/régimen/reinicio, lecturas frescas y orden temporal.
`delta_pp = usado_final − usado_inicial`; negativo o cruzando un reinicio sin extremos → `gap`. Una
diferencia de 0 pp con barra de resolución 1 pp no prueba coste cero. Redondear sólo al mostrar.

## 4. Atribución sin duplicar el paralelismo

Repartir cada delta **una sola vez**, con fracciones que suman 1: `isolated` (una sola tarea ocupa la
cuenta), `estimated` (concurrentes, reparto por un peso documentado), `unattributed` (residuo).
`quota_pp = delta_pp × share`. Destinos reservados: `OVERHEAD` (coordinación), `COORD` (raíl
transversal), `UNATTRIBUTED`, `EXTERNAL` (actividad ajena acreditada). Fases `planning`,
`execution`, `close`, `release`, reportadas por separado.

## 5. Dólares

- Suscripción imputada: `USD = mensualidad × (7/30) × (pp/100)`. Reparte la mensualidad para
  comparar tareas; no es factura.
- Equivalente API: tokens × tarifa versionada, por segmento y deduplicado por respuesta. Sin tarifa →
  hueco, nunca 0 USD.
- Gasto real (`billed_usd`): sólo lo acreditado. Las cuatro magnitudes no se suman entre sí.

## 6. Informe y presupuesto

Por tarea, sumar todos sus segmentos (hijos, roles, intentos) con columnas por proveedor; agrupar
después por raíl y sprint. `Σ delta_pp medidos = Σ quota_pp asignados` por proveedor. Publicar
subtotal atribuible, residuo y huecos. Para presupuestar el siguiente sprint, usar sólo tareas
aceptadas con cobertura completa y comparables (mismo esquema de dificultad, proveedor, régimen y
perfil): n, mínimo, mediana, máximo (P75 con n ≥ 5). Base = mediana; prudente = P75 o rango.
Coordinación/cierre aparte y reserva explícita para novedades. Semanas equivalentes no son plazo.
