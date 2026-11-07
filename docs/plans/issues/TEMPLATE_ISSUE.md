# [ISSUE-XXX] Título conciso del problema

> **Tipo:** Incidencia | Mejora\
> **Estado:** Abierto | En investigación | Bloqueado | Parcial | Pendiente de verificación | Resuelto y verificado\
> **Fecha de detección:** YYYY-MM-DD\
> **Origen:** SPRINT-NN / plan / tarea, o Fuera de sprint\
> **Componente afectado:** (módulo, servicio o cliente)\
> **Especificación de referencia:** (plan y tarea, documento de diseño)\
> **Severidad:** Crítica | Alta | Media | Baja\
> **Destino:** Sprint actual | Fuera de sprint — urgente | Backlog\
> **Prioridad y motivo:** urgencia, impacto y plazo conocido (si existe)\
> **Responsable:** área/persona conocida, o por asignar\
> **Seguimiento:** enlace a tarea del sprint o entrada del plan de backlog; para urgente, próxima acción\

Mantener una única ficha por problema y actualizar `index.md` al cambiar estado o destino.
Registrar el hallazgo aunque aún falte reproducción o causa, indicando qué falta. Para mejoras,
describir la capacidad propuesta en lugar de afirmar una divergencia confirmada. Registrar no
incluye automáticamente trabajo nuevo en el sprint.

---

## 1. Contexto y comportamiento observado
- Entorno o cliente utilizado, entradas y datos involucrados.
- Comportamiento observado frente al esperado.

## 2. Divergencia respecto a la especificación
- ¿Qué invariante o contrato se ha roto? ¿Qué norma de diseño se ha violado?

## 3. Caso mínimo reproducible
Fragmento de código, test o comando mínimo que evidencia el problema de forma aislada.

## 4. Análisis de causa raíz
Capa responsable, ficheros y líneas sospechosas, limitación implicada.

## 5. Criterios de aceptación y resolución
- [ ] 1. Test de regresión añadido (rojo antes, verde después).
- [ ] 2. Sin impacto negativo en rendimiento de los caminos críticos.
- [ ] 3. Paridad verificada entre los clientes afectados.
- [ ] 4. Documentación o especificación actualizada si procede.

Adaptar estos criterios a las capas realmente afectadas; justificar los que no apliquen.

## 6. Resolución y verificación
- **Sprint de resolución:** SPRINT-NN o Fuera de sprint (independiente del origen).
- **Fecha de resolución:** pendiente hasta completar la aceptación; después YYYY-MM-DD.
- **Commit(s) / diagnóstico:** referencias del arreglo o evidencia de cierre sin cambio de código.
- **Verificación:** fecha, comandos/escenarios, resultados y evidencia de cada criterio aplicable.
- **Pendientes:** enumerarlos; escribir ninguno sólo si está totalmente resuelta y verificada.

Al cerrar el sprint, conservar la ficha/evidencia en `docs/plans/archive/SPRINT-NN_<inicio>_<fin>/issues/`.
Una issue parcial, bloqueada o pendiente conserva ficha viva en la cola de issues y snapshot
**NO RESUELTA** en el archivo, con enlaces entre ambos. Si se resuelve fuera de sprint, usar
`docs/plans/archive/FUERA-SPRINT_<detección>_<resolución>/`.
