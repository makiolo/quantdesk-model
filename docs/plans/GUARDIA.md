# GUARDIA — quantdesk-model

Notas de la raíz de guardia (skill global `sprint`, `references/guardia.md`). Como mucho 80 líneas.

## Estado (2026-11-13 22:55 local)
- **Sin sprint activo; fase: planificación** (sin release, SPRINT_PROJECT §10).
- **SPRINT-02 cerrado con arrastres** el 2026-11-13 por la raíz del relevo 2 (sesión 3c744740), por decisión del usuario
  («Cerrar y arrastrar»; fila 7 «Backlog»). Archivo: `archive/SPRINT-02_2026-11-11_2026-11-13/` (SPRINT.md §9,
  ARCHIVE_MANIFEST, tag `sprint-02`). Suite del DoD 14 OK / 0 FALLO. BDD: SPRINT-02 «Cerrado con arrastres».
- Cerradas: 2b (FinCast) y 1b (TI-02-DATA-V2 + tabla FX sobre MT5; umbrales TS-00-OBJ confirmados por el usuario).
- Arrastradas a SPRINT-03 §0 (`next/SPRINT.md`): **S02-5** TI-12-MT5 (espera al desbloqueo de la cuenta MT5) y
  **S02-6** medición de cobertura de TI-09-ARCH (20 días hábiles NYSE hasta el 2026-12-10; token nuevo, puerta de usuario).
- Fila 7 (TI-13-PUB) al backlog, `backlog/PLAN_DATOS_VIA_QN.md`: espera a que el backend publique (su SPRINT-03).
- Push hecho; árbol limpio salvo `bash.exe.stackdump` (ajeno, no tocar).

## Dependencias
- Entrada: SPRINT-03 y SPRINT-04 esperan a quantdesk SPRINT-03 y SPRINT-04 cerrados (`deps.py`: quantdesk sigue en su
  SPRINT-02). Ningún proyecto depende de quantdesk-model SPRINT-02 (salidas vacías).
- Backend: OC-03 servida (cadenas en qn desde la sesión 2026-11-12); publicadores públicos en su SPRINT-03.

## Compromisos con otras raíces
- Guardia actual: sesión `quantdesk-model-c4` (2026-11-13). Raíces vivas: `quantdesk-c3` (relevo 55, SPRINT-02 activo),
  `quantdesk-backend-d4`, `quantdesk-network-f0` (guardia).
- quantdesk avisará al cerrar su SPRINT-02 y si cambia algo de la rueda, de TI-03-FMT o de DL-02-GATES. Al backend se le pidió aviso
  cuando publique el mercado público (su SPRINT-03) o si cambia OC-03.
- Network recordó que hay que tener «copia propia antes de `lake delete`». Respuesta: no, por D7 (usuario, 2026-11-10): la copia es la común
  (PLAN_COPIA_PERIODICA_LAGO), y `lake delete` no se usa sobre `market.*` hasta que esa copia exista. En su PLAN_RETIRADA_TOPICS_EVENTOS,
  Fase 3, las líneas 99-100 contradicen a D7; las concilia network. Se le pasó la lista de lo que depende aquí de qn.

## Preguntas abiertas al usuario
1. **S02-6 frente al bloqueo de SPRINT-03.** La medición de TI-09-ARCH puede hacerse tras el 2026-12-10, pero SPRINT-03
   no puede activarse hasta que cierre quantdesk SPRINT-03. ¿Se hace como encargo fuera de sprint cuando llegue la fecha
   (registrado igual que en un sprint), o espera a SPRINT-03? Lo mismo vale para S02-5 si se desbloquea la cuenta MT5.
2. ISSUE-TI09-SONDA-CADENAS (fuera de sprint) sigue abierta: su criterio 1 pide la cifra por día hábil desde el
   2026-11-09; podría cerrarse con la medición de S02-6.

## Siguiente paso
Presentarse a las raíces vivas (ListAgents) y proponer al usuario la pregunta 1. Sin vigías periódicos.
