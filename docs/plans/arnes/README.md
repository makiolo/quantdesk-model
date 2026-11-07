# Arnés de ejecución — quantdesk-model

Reglas mínimas para todo trabajo delegado (skill global `sprint`, references/delegation.md y
ficha.md). Cada regla dice cómo se comprueba. Una regla crítica que sólo vive en el texto se
convierte en control mecánico en cuanto haya forma (A9). Ajustarlas al proyecto con fecha y motivo;
los análisis que las justifiquen se guardan en esta carpeta (`ANALISIS_<fecha>.md`…).

- **A1. Salida de datos.** Enviar código a una API ya es sacar datos. Credenciales, `.env` y datos
  reales sensibles no salen nunca. Destinos autorizados: «suscripciones del proyecto». Lista
  restringida: «rellenar». *Comprobación:* la marca `Salida:` de la ficha y la ruta usada.
- **A2. Ficha completa y comprobada antes de lanzar** ([plantilla](~/.claude/skills/sprint/references/ficha.md)):
  resultado observable, fuera de alcance, restricciones, invariantes, casos borde, aceptación
  verificable, rutas autorizadas, condición de parada y extracto de reglas. Un modelo barato de sólo
  lectura lista antes las dudas que cambiarían contrato, seguridad o aceptación.
  *Comprobación:* su salida se guarda junto a la ficha.
- **A3. Tres etiquetas por tarea:** dificultad L, riesgo (`bajo`, `medio`, `alto`,
  `numérico-silencioso`) y atención humana (`S`, `M`, `L`).
- **A4. Revisor independiente con contexto limpio:** otro modelo concreto que el autor; recibe ficha,
  diff y código relacionado, nunca la conversación ni el informe del autor.
- **A5. Aceptación protegida contra el autor:** puede añadir tests, no modificar ni borrar los
  existentes ni la configuración del gate/CI, salvo `Cambios de tests: permitidos (motivo)` revisado
  aparte. *Comprobación:* `git diff --name-status <base>` antes de aceptar.
- **A6. La evidencia es del gate y de una versión fija del código:** salida del gate con `HEAD` y
  huella del árbol antes y después; si cambiaron entre medias, no vale.
- **A7. Riesgo numérico-silencioso:** un oráculo distinto del autor prepara antes casos de referencia;
  la regresión falla en rojo antes del arreglo.
- **A8. Entregas revisables:** dividir por comportamiento verificable; atención `L` o > 400 líneas
  obliga a dividir o justificar.
- **A9. Trinquete en cada cierre:** «fallo → causa → control → prueba de que lo detecta».
- **A10. Medir la consistencia, no el mejor intento:** se registran intentos, rechazos y escalados.
- **A11. Relevo de la raíz antes de que se llene su contexto** (references/handoff.md): zonas 70/80/85 %,
  HANDOFF ≤ 200 líneas con sólo estado volátil, una sola raíz escribiendo, latido de caché.
  Arranque de la sucesora: [ARRANQUE.md](ARRANQUE.md); tras un apagado: [ARRANQUE_FRIO.md](ARRANQUE_FRIO.md).
- **A12. Decide la raíz** lo que tiene opción recomendada clara dentro de lo autorizado y lo anota;
  sigue preguntando alcance, contratos públicos, datos, publicar e irreversibles.
