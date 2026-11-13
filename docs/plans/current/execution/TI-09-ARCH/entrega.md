TI-09-ARCH · autor-6 · 2026-11-13 · base d6bc45d · motor quantdesk 69fdb39d · semilla 0 · S = scripts/archivo_opciones_lib/selftests.py; D = scripts/descarga_opciones.py.

- Verificación: `D:/miniconda312/python.exe -B -X utf8 scripts/descarga_opciones.py --selftest` y `.venv/Scripts/python.exe -B -X utf8 scripts/archivo_opciones.py --selftest` → `selftest ok`; Python 3.12.3, auditoría AST: solo stdlib en D; oráculo manual call/put de cinco strikes S:34, punto fijo independiente S:91. Logs: `E:/quantdesk-lab/tmp/TI-09-ARCH/{descarga,archivo}_selftest.log`.
- Evidencia: `E:/quantdesk-lab/tmp/TI-09-ARCH/selftest_hgu9_uhz/evidencia.json`; dataset `E:/quantdesk-lab/datasets/TI-09-ARCH/fixture_ti09_5b8619eb2d8b`, SHA-256 `4341ec598ace5cd1b865c14f16859bff21fcc8611551ee57b2798ca8ceac8412`; informe.md SHA-256 `85dfb2498d8afae502977069d0fec51f95961e29759fa27d14ad2b0378fdf40a`. Corte fixture `2026-11-28T06:00:00Z`; S:239 verifica doble ejecución con hash y bytes idénticos y validación data_py de esquema, hash, disponibilidad y política feed.
- Fixture diferencial (S:133): cruda 204 = 12/11 universo100() call K100 vencimiento 2027-01-15 + SPY K110/120/130/150 de igual vencimiento + SPY K140 vencido 2026-11-10, y 13/11 reintento de 99 subyacentes (sin NVR), call K100; limpia 201 = cruda menos SPY K110 (ask=0), K120 (bid>ask), K140 (vencido), todos del 12/11. SPY K130/K150 conservan bid=0 y volume=0, IV/last cero pasan a null. Fuera: parcial 80, captura única 90, dos filas viejas, dos pilotos; un duplicado exacto se colapsa. Reglas y tolerancia: `scripts/archivo_opciones_lib/lector.py:1`; selección `:193`, filtro `:283`; calendario explícito hasta 2027-02-28, ampliable con --calendario; cobertura de 20 días corresponde a la raíz.
- Raíz, mini (última sesión cerrada al 2026-11-13 07:37 UTC: 2026-11-12): copiar solo D; QN_URLS/QN_TOKEN ya en entorno, TI09_LAB = montaje en mini de E:/quantdesk-lab; autoprueba `TI09_TMP="${TI09_LAB:?montaje de E:/quantdesk-lab}/tmp/TI-09-ARCH" python3 descarga_opciones.py --selftest`; volcado `QN_ENV=main python3 descarga_opciones.py --desde 2026-11-12 --hasta 2026-11-12 --salida "${TI09_LAB:?montaje de E:/quantdesk-lab}/tmp/TI-09-ARCH/oc03_s20261112"` (directorio nuevo).
- Raíz, PowerShell en el repo, sin red: `.venv/Scripts/python.exe -X utf8 scripts/archivo_opciones.py --volcado E:/quantdesk-lab/tmp/TI-09-ARCH/oc03_s20261112 --corte 2026-11-13T06:00:00Z --nombre oc03_s20261112_c20261113`; escribe dataset nuevo en datasets/TI-09-ARCH/ e informe/checksums. Implementación: `scripts/archivo_opciones.py:88`. No se han descargado datos reales ni usado credenciales; solo rutas autorizadas, tests nuevos, sin push.

| Caso borde | Test que lo cubre |
|---|---|
| Parcial 80 % + reintento 99 %; dos completas, desempate por captured_at y empate total | S:153 `test_capturas_universo_huecos`; S:177 `test_empates_95_y_cinco_previas` |
| Única captura 90 % → sin válida, tablas vacías; frontera 95 % inclusiva | S:153, S:177 y S:239 `test_dataset_doble_offline` |
| Festivo 26/11 sin hueco; hábil sin captura con hueco en todo el universo; medias sesiones hábiles | S:153 y S:225 `test_corte_ns_calendario` |
| SPY/QQQ EQUITY CALL sin capture_id y pilotos 11/11, todos fuera | S:153; D:322 `selftest` |
| Ask cero, bid>ask, IV/last cero, bid/volume cero; duplicado exacto/distinto contenido | S:206 `test_ceros_vix_expirado_duplicados` |
| ^VIX conserva spot de índice, sin precio de respaldo ni comparación exacta contra otro precio | S:206; informe.md del fixture nombra ^VIX |
| Vencimiento pasado excluido con motivo único | S:206 y S:239 |
| qn rechaza por filas: dividir hasta día; día indivisible → error; reintento 19 NY al día UTC siguiente | D:322 `selftest`; S:225 y S:239 comprueban ns y ceil a ms; mismo D prueba 401/403, 302, 429/500, ausencia de token en salidas, contexto y catálogo vacío, sin sockets |

Dudas para revisión: ninguna
