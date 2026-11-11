# Aceptación — Corrección 1

Commit de código y tablas probado: `ce1150dbbff2e769e848299d1ef54165b0d2ac4e`.
Se creó con `git archive --format=zip --output=E:/quantdesk-lab/tmp/TS-00-BENCH-FINCAST/correccion1/ce1150d.zip ce1150d`.
Archivo expandido en `E:/quantdesk-lab/tmp/TS-00-BENCH-FINCAST/correccion1/archive-ce1150d`;
`.venv` es una junction al venv existente del proyecto, sin instalar paquetes.
Todos los comandos siguientes se ejecutaron desde ese archivo, con `.venv/Scripts/python -X utf8`.

| Comando | Resultado | Evidencia |
|---|---|---|
| `scripts/banco_walkforward.py --selftest` | salida 0; selftest ok | [log del banco](selftest-banco.log) |
| `scripts/run_selftests.py` | salida 0; **12 OK, 0 FALLO** | [log global](selftests.log) |
| `scripts/banco_walkforward.py --informe … --destino E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/correccion1/tablas_archive` | salida 0; ambos CSV regenerados idénticos byte a byte a los entregados | [log de tablas](tablas.log) |

La orden completa de tablas y las seis corridas fuente figuran en [tablas/informe.md](../tablas/informe.md); solo cambia el destino anterior.
Principal: 798 filas, idéntica byte a byte a SPRINT-01, SHA-256 `9b8ab8b073e012ec7e7530f56258c74c8fc6c4eb6f9e9c873878a88b1b558294`.
Limpia: 570 filas, SHA-256 `8dd0dc0f880a674b1def213c46292bd20002bddda81b8db8c5aa493cdd14c8d7`.
Fuentes del archivo intactas tras la suite; código del banco sin cambios respecto a `ce1150d`.
El otro autor incorporó `e211f31` durante el gate: sus cambios del exportador no forman parte del archivo probado.
Los 19 ficheros de `ce1150d` pertenecen a rutas autorizadas. No se incluyeron ficheros del otro autor.
[Hashes del archivo, fuentes y logs](archive.json). [Casos borde y conclusiones](../informe.md#corrección-1).
Dudas para revisión: ninguna.
