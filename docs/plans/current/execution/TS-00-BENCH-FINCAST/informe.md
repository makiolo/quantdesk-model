# TS-00-BENCH — FinCast, sub-entrega A (SPRINT-02, fila 2b)

Autor: `autor-2b-A`; padre: raíz inicial. Base: `934d9af`. Inicio: 2026-11-11 08:20 UTC.
Nivel L6, riesgo numérico-silencioso/integración, atención M. Sin GPU, sin credenciales ni push.
Motor **quantdesk 69fdb39d0b67969dbdafa77f5da656511342f175**, rueda SHA-256
`28c1ed662a79a1075a11e544a0f4fe3f10be70d0a9917a4abbf6eccad4c3c3fd`.
Semilla **20261101**. Fecha de corte limpio: **2025-08-27T00:00:00Z**, comparación estricta `origen > corte`.
Al verificar la afirmación heredada, `nvidia-smi` sí existe en esta sesión, pero falla al comunicarse con el
driver y no identifica una GPU utilizable. DL-02-GATES no está habilitado y el alcance exige CPU.

## Estado

Integración en `f3f8a4d`. Selftest del banco en verde, dos pilotos reales sin fallos y regresión exacta frente a
SPRINT-01. Corridas completas y repeticiones en curso, secuenciales, en segundo plano. Cierre de la suite global
pendiente hasta el final. Este estado se sustituye por las cifras finales al terminar; no se declara completada
una corrida mientras siga ejecutándose.

## Puerta, revisiones, licencia y carga segura

Se comprobó la existencia de `.git/sprint-runtime/s02/TS-00-BENCH-FINCAST/autorizacion-descarga.md` inmediatamente
antes de descargar código y pesos. Su autorización incluye ambos orígenes. No se usaron credenciales.
Las revisiones se resolvieron el 2026-11-11 a las 08:20:15 UTC y se fijaron en `modelos.py`:

| Objeto | Revisión inmutable | Ubicación / SHA-256 |
|---|---|---|
| Código `vincent05r/FinCast-fts` | `488b19d1d85fa2b3d4b93469530cefdcf1cc97a4` | `E:/quantdesk-lab/src/FinCast-fts@488b19d1d85fa2b3d4b93469530cefdcf1cc97a4` |
| Pesos `Vincent05R/FinCast` | `2d7d90b159db8961d27c2cf165d51195902ef92b` | `E:/quantdesk-lab/cache/hf/hub/models--Vincent05R--FinCast/snapshots/2d7d90b159db8961d27c2cf165d51195902ef92b/v1.pth` |
| `v1.pth`, 3 966 703 063 bytes | revisión anterior | `d5ca999b02c944effa60d2b94174dc4d5a0cd2c0543ae289b2e36f37431492a8` |
| LICENSE del código | revisión anterior del código | `1eb85fc97224598dad1852b5d6483bbcf0aa8608790dcc657a5a2a761ae9c8c6` |
| README/tarjeta de los pesos | revisión anterior de HF | `cbc5c2eb63cd9cc2ff8baa1ed888cd062e81ec170413ffe9827b920bc726794d` |

Licencia verificada: [LICENSE Apache-2.0 del código](https://github.com/vincent05r/FinCast-fts/blob/488b19d1d85fa2b3d4b93469530cefdcf1cc97a4/LICENSE)
y [metadato `license: apache-2.0` de la tarjeta de pesos](https://huggingface.co/Vincent05R/FinCast/blob/2d7d90b159db8961d27c2cf165d51195902ef92b/README.md).
HF no contiene un LICENSE separado; la evidencia de los pesos es la tarjeta fijada. Huellas de los ficheros
ejecutables auditados en [procedencia.json](procedencia.json); el trabajador comprueba sus cuatro hashes antes
de importarlos y vuelve a comprobar el SHA-256 de pesos en cada arranque.

Se leyeron el decoder, MoE, distribución, API y preprocesado antes de ejecutarlos. Solo se ejecuta el decoder
oficial y `st_moe_pytorch`, sin modificar el checkout descargado. La importación directa evita `ffm.__init__`,
que arrastra JAX por la API de covariables. No se usa esa API. El proceso arranca con el intérprete del venv
FinCast, `-I -X utf8`, cwd temporal en E:, HF offline, sin importar módulos del repositorio del banco.

`torch.load(map_location="cpu", weights_only=True)` devolvió un `OrderedDict` puro de **1713 tensores**.
Se exige que todas las claves sean cadenas y todos los valores tensores; se quitan solamente los prefijos
DDP/compile admitidos por la carga oficial y se exige `load_state_dict(strict=True)`. No existe fallback
a `weights_only=False`, ni allowlist de objetos pickle. Evidencia: `pesos-seguros.log` en la raíz de corridas.

Un primer arranque detectó estrictamente una configuración incorrecta de 3 expertos (valor por defecto del
decoder). La configuración oficial de v1 en `src/tools/inference_utils.py:229` fija **4 expertos y top-2**;
se corrigió el adaptador, conservando `strict=True`. El intento fallido queda en `piloto_fx.log` y no produjo
previsiones; el piloto válido es `piloto_fx_v1`.

## Contrato, criterios y ventana limpia

El contrato sigue siendo `predecir(precios, semilla, hmax) -> (Q[hmax,21], info)` en log-rendimiento acumulado.
FinCast recibe los W log-precios visibles, lote 1, frecuencia diaria 0, padding frontal de ceros y máscara 1
hasta el múltiplo siguiente de patch=32 (250→256; 1000→1024), sin eliminar observaciones. Arquitectura v1:
50 capas, dimensión 1280, 16 cabezas, 4 expertos/top-2, patch de salida 128; CPU float32. La transformación
interna es la del decoder oficial; se resta el último log-precio a sus previsiones. No se usan objetivos
ni índices de la serie fuera del contexto.

`info` declara por nivel 9 deciles nativos, 8 niveles interpolados y 4 extrapolados. Para un p no nativo:
`q(p)=q_i+(Phi^-1(p)-z_i)/(z_(i+1)-z_i)*(q_(i+1)-q_i)`, con deciles adyacentes y `z_i=Phi^-1(p_i)`.
Para 0.01/0.05 se usa el par 0.1–0.2 y para 0.95/0.99 el par 0.8–0.9. Los valores nativos quedan intactos.
La salida se rechaza por origen si no tiene forma correcta, finitud o monotonía no decreciente.

| Tabla | Selección | Criterios de FinCast |
|---|---|---|
| Principal | Orígenes comunes de los modelos pedidos **excluyendo FinCast** | FinCast no tiene filas |
| Limpia | Origen estrictamente posterior al corte y común a **todos** los modelos que entran en la comparación | Solo `crps_deciles` y QLIKE |

`crps_deciles = 2/9 * suma pinball(p)` para p=0.1,…,0.9, para **todos** los modelos. No es el CRPS continuo
ni el CRPS de los 21 niveles del banco. QLIKE conserva exactamente la fórmula previa:
`log(s2)+RV/s2`, `s2=((q90-q10)/(2*1.2815515655446004))²`.
FinCast nunca calcula CRPS de 21 niveles, pinball 1 %/99 %, excedencias, Kupiec ni Christoffersen. Sus celdas
son vacías en CSV y — en Markdown, con `criterios_no_aplicables` explicando la exclusión. `n_test` y recuentos
de colas también quedan vacíos. La ausencia de orígenes limpios o comunes se declara en `ventana_limpia.json`
y en el informe; el CSV vacío conserva la cabecera. No se inventan ceros ni resultados de VaR.

La tarjeta de pesos no declara fecha final de preentrenamiento. Se aplica la decisión A12 de evaluar por
instante de origen, permitiendo contexto anterior. El corte posterior a la publicación no demuestra por sí
solo que una revisión posterior de los pesos esté libre de contaminación.

Timeout FinCast por petición **600 s**, configurable con `--fincast-timeout`; arranque **300 s**. El timeout
mata el trabajador, marca ese origen fallido y reinicia en el siguiente. El contador y el ejemplo de error
llegan al informe. Una respuesta JSON de error o de cuantiles inválidos conserva el trabajador sincronizado
y la CPU externa devuelta; no requiere recargar los pesos. La CPU de una petición sin respuesta no es
recuperable y queda fuera de la suma, pero la pared incluye la espera. Toto conserva su comportamiento.
La corrida FX ya estaba en curso con el primer driver al añadir esta mejora: en ella los errores normales
reinician el modelo y no conservan su CPU externa. Se declara esa limitación, se muestran los fallos y se
registra aparte la CPU por origen válido. No cambia ninguna predicción ni se reparan cuantiles. Las corridas
posteriores y el gate usan el driver corregido. La CPU de carga inicial está separada de la de predicción;
las recargas del primer driver están incluidas en pared, sin una medición acumulada de CPU de carga.

## Entorno y reproducción

Venv `E:/quantdesk-lab/venvs/fincast`, Python 3.12.3, torch **2.7.0+cpu**, numpy 2.1.3, einops 0.8.1,
einx 0.3.0, beartype 0.20.2, CoLT5-attention 0.11.1 y sus transitivas. **Sin JAX ni TensorFlow**.
[requirements-fincast.txt](requirements-fincast.txt) fija los 20 paquetes instalados con hashes de sus wheels;
[entorno.json](entorno.json) registra además pip 24.0, herramienta de bootstrap. Plataforma de los hashes:
Windows x64 / CPython 3.12.3. `.venv` y `requirements.lock` no se instalaron ni modificaron.

```powershell
$env:HF_HOME='E:/quantdesk-lab/cache/hf'
$env:TMP='E:/quantdesk-lab/tmp/TS-00-BENCH-FINCAST'; $env:TEMP=$env:TMP
# Reconstrucción del venv auxiliar; no es el del banco:
D:/miniconda312/python.exe -m venv E:/quantdesk-lab/venvs/fincast
E:/quantdesk-lab/venvs/fincast/Scripts/python -I -X utf8 -m pip install --require-hashes -r docs/plans/current/execution/TS-00-BENCH-FINCAST/requirements-fincast.txt
```

Solo CPU. `eval()`, `torch.use_deterministic_algorithms(True)` y semilla del banco por origen;
`torch.manual_seed(semilla)` antes de cada llamada, incluido el ruteo MoE que sortea aun en eval.
Los ficheros `meta.json` incluyen motor, rueda, versiones de ambos venvs, revisión/hash de pesos y semilla.

## Piloto, presupuesto y órdenes

Piloto válido total: **4 pares activo-origen** (≤10), dos EURUSD y dos BTCUSDT.
FX: **1.71875 CPU s/origen**, pared de inferencia 3.13 s en total; pared de carga no registrada en ese primer
piloto (se registra por separado desde el piloto Binance y en las corridas siguientes).
Binance: **2.734375 CPU s/origen**, pared de inferencia **4.72 s**, pared total **52.53 s**, cero fallos.
Las órdenes y hashes íntegros están en sus `meta.json` y logs bajo `E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/`.

Submuestra determinista elegida: **FX `--cada 5`, 1400 pares / 28 activos**; **Binance `--cada 10`, 130 pares
limpios / 10 activos**. Se aplica `--cada` a los cortes válidos de la rejilla original **antes** del corte
limpio; `--max-origenes` va después. Así se alinea exactamente con las submuestras previas de Toto sin
reducir los orígenes de los otros modelos en la tabla principal. Binance limpia empieza 2025-09-21 y acaba
2026-09-16, 13 orígenes por activo. No se cambian presets ni semilla.
Estimación con la pared del piloto: ~36.5 min FX y ~5.1 min Binance, más carga; cada tabla queda holgadamente
por debajo de ~8 h. Es un presupuesto, no una promesa de tiempo en una máquina compartida. El lote 1 evita
las 32 copias de padding que ejecutaría la API oficial por defecto; el coste medido es menor que la
estimación previa de «7 veces Toto», que no era una medición de este adaptador.

```powershell
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos fincast --activos EURUSD --max-origenes 2 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_fx_v1
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --modelos fincast --activos BTCUSDT --max-origenes 2 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_binance
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos fincast --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/fincast_fx
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --modelos fincast --cada 10 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/fincast_binance
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset lago_cierre_c20261101 --modelos fincast --activos EURUSD --max-origenes 2 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/repeticion_fx --comparar E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_fx_v1
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset binance_c20261101 --modelos fincast --activos BTCUSDT --max-origenes 2 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/repeticion_binance --comparar E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/piloto_binance
```

Controlador secuencial: `E:/quantdesk-lab/tmp/TS-00-BENCH-FINCAST/corridas.py`; lanzador PID **15200**, proceso
controlador real **46048**, primera corrida PID **19044**. Estado y PIDs exactos de cada tanda en
`E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/estado_corridas.json`; logs `controlador.log`, `fincast_fx.log`,
`fincast_binance.log`, `repeticion_fx.log`, `repeticion_binance.log`. Nunca hay dos corridas propias a la vez.

## Verificación y casos borde

**Hallazgo previo de monotonía:** las predicciones archivadas de Chronos-2 contienen 187 filas cruzadas en FX y
890 en Binance, aceptadas por el banco de SPRINT-01 sin comprobación. HMM/GARCH/Toto no presentan cruces en
los archivos auditados. [regresion-s01.json](regresion-s01.json) recoge conteos, ejemplos y hashes completos.
El recálculo actual de los criterios principales de las cuatro corridas archivadas reproduce **exactamente**
sus hashes originales. No se ordenan/reparan cuantiles ni se modifican archivos o tablas principales históricas.
La tabla limpia aplica la nueva comprobación también a esos archivos: un cruce en cualquier horizonte
almacenado excluye ese origen-modelo completo de los tres horizontes y, por intersección, de los demás modelos;
los conteos y motivos quedan declarados. Solo se pueden comprobar los horizontes almacenados (1/5/20),
mientras que una corrida nueva comprueba 1..20. Una repetición nueva de todo Chronos-2 puede rechazar también
orígenes antes aceptados: es efecto de la validación obligatoria de monotonía, no de añadir FinCast ni de cambiar
fórmulas. La comparación real corta HMM/GARCH (3 orígenes EURUSD, 18 filas) da diferencias **0** de predicciones
y criterios frente a SPRINT-01, con `--comparar`; log `regresion_s01.log`.

Prueba roja antes de añadir la métrica: `test-rojo.log`, AttributeError por ausencia de `crps_deciles`.
Oráculo independiente escalar con `statistics.NormalDist.inv_cdf`, sin llamar a pinball del banco para el
esperado, y [fórmula de pinball de scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html#pinball-loss).
Se contrasta la suma directa de los nueve pinball; no una integral continua con distinto peso.

| Caso borde | Test nuevo que lo cubre |
|---|---|
| Origen igual al corte fuera; +1 ms y +1 día dentro | `prueba_ventana_limpia` |
| Todos los orígenes anteriores/iguales: tabla vacía declarada, también al persistir | `prueba_ventana_limpia`, `prueba_informe_limpia`, `prueba_ventana_vacia_persistida` |
| Trabajador silencioso: timeout, origen fallido y continuación | `prueba_fincast`, `prueba_timeout_persistido` |
| Respuesta `error` o cuantiles no monótonos | `prueba_fincast`, `prueba_monotonia_banco` |
| Falta venv o pesos: ModeloSaltado | `prueba_fincast` |
| FinCast no aparece ni reduce orígenes principales | `prueba_ventana_limpia` |
| CRPS deciles de una normal contra cálculo independiente | `prueba_deciles_independientes` |
| Las tres copias de NIVELES coinciden; interpolación/extrapolación z preserva deciles | `prueba_fincast` |
| Unión de corridas con distinto hash de dataset se rechaza | `prueba_informe_limpia` |
| Cruces en archivos antiguos: exclusión limpia declarada y tabla principal histórica intacta | `prueba_informe_limpia` |

Los tests previos no se modifican ni se borran; se añaden funciones e invocaciones en el selftest del banco.
La implementación abarca proceso, métricas e informe con más de 400 líneas porque el contrato atraviesa esas
tres capas; se separan el commit funcional verificado y el dossier de corridas/evidencia, sin delegar fuera
de esta sub-entrega. La revisión independiente corresponde a la raíz que integra A.

## Sub-entrega B preparada

Esta tabla FX sigue siendo **provisional y proxy** de `lago_cierre_c20261101`; no se mueven umbrales.
Cuando la fila 1b entregue los presets MT5, la raíz sustituirá `<PRESET_MT5_CABECERA>` y
`<PRESET_MT5_AMPLIACION>` por sus nombres reales. No existen aún aquí ni se añaden en esta entrega:

```powershell
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset <PRESET_MT5_CABECERA> --modelos fincast --solo-limpia --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/mt5_cabecera
.venv/Scripts/python -X utf8 scripts/banco_walkforward.py --dataset <PRESET_MT5_AMPLIACION> --modelos fincast --solo-limpia --cada 5 --out E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/mt5_ampliacion
```

Medir primero ≤10 orígenes MT5 y ajustar `--cada` según su coste y la cobertura común. El comando con
placeholders no es ejecutable hasta existir esos presets; pendiente concreto de B, no una corrida omitida de A.
