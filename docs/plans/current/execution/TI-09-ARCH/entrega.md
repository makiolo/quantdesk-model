TI-09-ARCH C2 · OK · base fba4279 · rama ti-09-arch-c2-memoria · motor quantdesk 69fdb39d · semilla 0.
`scripts/archivo_opciones_lib/flujo.py:217`: Arrow por sesión; contexto de cinco sets (symbol,asset_type); filtro original por subyacente: máximo medido 10.416 filas frente a 432.000 de la sesión.
Parquet/hash incremental (4.096 filas), ledger en disco; `scripts/archivo_opciones_lib/validacion.py:23`: data_py por bloques ≤8.192 de una sesión y comprobaciones globales de manifest/hash/orden/disponibilidad. Un dataset por rango; N/índice de particiones no aplican.
`.venv/Scripts/python.exe -B -X utf8 scripts/archivo_opciones.py --selftest` y `D:/miniconda312/python.exe -B -X utf8 scripts/descarga_opciones.py --selftest` → ambos `selftest ok`, exit 0; salida en selftests_c2.txt.
Nuevos tests en scripts/archivo_opciones_lib/selftests.py:433 (weakrefs reales, siete sesiones, 100 filas máximas y motor ≤una sesión) y :486 (hash, manifest, frontera de orden y ledger grande).
Reglas, calendario, descarga y aserciones anteriores conservados; casos borde y ocho mutantes de C1: `git show fba4279:docs/plans/current/execution/TI-09-ARCH/entrega.md`.
`.venv/Scripts/python.exe -B -X utf8 scripts/archivo_opciones_lib/equivalencia.py --base fba4279` → `equivalencia ok`; cruda 204 y limpia 201 idénticas fila a fila, motivos, capturas y huecos idénticos.
SHA-256 de dataset, base y entrega: `sha256:4341ec598ace5cd1b865c14f16859bff21fcc8611551ee57b2798ca8ceac8412` (sin cambio de formato lógico).

| Sesiones | Filas | Pico residente GB | Pico comprometido GB | Pared s |
|---|---:|---:|---:|---:|
| 1 | 432000 | 1.146 | 1.491 | 332.29 |
| 5 | 2160000 | 1.239 | 1.570 | 1763.62 |
GB decimales; psutil Windows PeakWorkingSetSize/PeakPagefileUsage, intérprete hijo + launcher; pared del hijo completo, generación excluida. Corte sintético 2026-11-19T06:00:00Z.
Orden medida ejecutada: `.venv/Scripts/python.exe -B -X utf8 scripts/archivo_opciones_lib/medidas.py --base E:/quantdesk-lab/tmp/TI-09-ARCH/memoria_c2_realista_20261113 --solo-medir`; órdenes exactas de ambos hijos y picos en bytes en medidas_c2.json.
Reproducción integral: `.venv/Scripts/python.exe -B -X utf8 scripts/archivo_opciones_lib/medidas.py --base E:/quantdesk-lab/tmp/TI-09-ARCH/memoria_c2_repro` (directorio nuevo; genera, mide y borra volcados/datasets grandes). Forma: 509 subyacentes; SPY 5.208/tipo, 31 vencimientos ×168 strikes; AAPL 1.432/tipo; VIX 449/tipo.
Evidencias congeladas: medidas_c2.json, equivalencia_c2.json, fixture_c2.json, selftests_c2.txt y SHA256SUMS_c2; sintéticos grandes de C2 borrados. `git diff fba4279 ti-09-arch-c2-memoria --stat`: solo rutas autorizadas; sin push.
Mini (raíz, credenciales ya en entorno): `scp scripts/descarga_opciones.py mini:descarga_opciones.py`; en mini `QN_ENV=main python3 descarga_opciones.py --desde 2026-11-12 --hasta 2026-11-12 --salida ./tmp-ti09/oc03_s20261112`; copia PowerShell `Push-Location E:/quantdesk-lab/tmp/TI-09-ARCH; scp -r mini:tmp-ti09/oc03_s20261112 .; Pop-Location`.
Raíz offline: `.venv/Scripts/python.exe -B -X utf8 scripts/archivo_opciones.py --volcado E:/quantdesk-lab/tmp/TI-09-ARCH/oc03_s20261112 --corte 2026-11-13T06:00:00Z --nombre oc03_s20261112_c20261113`; el rango completo del manifest se procesa en una orden, también para cortes de veinte sesiones.
Dudas para revisión: ninguna
