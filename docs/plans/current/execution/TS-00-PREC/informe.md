# TS-00-PREC — Banco de precisión emulado (fp8 e4m3/e5m2, bf16, f16, f32 frente a f64)

Informe generado por `scripts/banco_precision.py` desde `resultados.json`; no se edita a mano. `--verificar DIR` regenera este texto desde el JSON y exige que coincida cifra por cifra.

## 1. Evidencia

- Perfil: `completo`. Semillas: 11, 22, 33, 44, 55 (n = 5); semilla de las entradas de evaluación (fijas, comunes a todas): 9999.
- Fecha UTC: 2026-11-08T12:03:57Z. Tiempo de pared: 3109.9 s.
- Versiones: python 3.12.3, torch 2.15.0+cpu, ml_dtypes 0.6.0, arch 8.0.0, numpy 2.5.4, scipy 1.18.1; motor quantdesk commit `69fdb39d` (paquete 0.0.0).
- Determinismo: `torch.manual_seed` por semilla, `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)` (también `OMP/MKL/OPENBLAS_NUM_THREADS=1`); aleatoriedad de datos con `numpy.random.default_rng([semilla, flujo])`.
- SHA-256 canónico de `resultados.json` (JSON con claves ordenadas, floats a 10 cifras significativas, sin el bloque `meta`): `5760df75ab902e7bebc09d9bb8f4cc6f5bea95d1f6d62521243f3896b4916e1c`.
- Comando exacto para reproducir (dos ejecuciones con las mismas semillas deben dar el mismo hash): `.venv/Scripts/python -X utf8 scripts/banco_precision.py --out E:/quantdesk-lab/runs/TS-00-PREC/completo`.
- Verificación: `.venv/Scripts/python -X utf8 scripts/banco_precision.py --verificar <DIR>`.

## 2. Diseño (decisiones de diseño declaradas)

### 2.1 Datos sintéticos con verdad conocida

- (a) GARCH(1,1) normal, r_t = sqrt(h_t) z_t, h_t = ω + α r²_(t-1) + β h_(t-1): ω = 2e-06, α = 0.08, β = 0.9 (persistencia 0.98, vol diaria incondicional 1 %). 10000 puntos por semilla.
- (b) Cambio de régimen de 2 estados (cadena de Markov diaria; log-rendimiento = (μ_s − σ_s²/2)/252 + σ_s/√252 · z): P = [[0.98, 0.02], [0.04, 0.96]], μ anual = [0.08, -0.1], σ anual = [0.08, 0.3]. 2500 puntos por semilla. Estado inicial de la distribución estacionaria.
- (c) Volatilidad estocástica («vol de la vol»): **no medida**, motivo en 3.1.
- Entrenamiento del transformer: por semilla, 8 series de cada familia de 5000 puntos (generadas con flujos de aleatoriedad distintos de los de recuperación y evaluación).
- Entradas de evaluación de las medidas 2 y 3: 512 ventanas fijas (mitad GARCH, mitad régimen), idénticas para las 5 semillas.

### 2.2 Transformer y cono

Transformer pre-LN solo codificador: ventana W=64 log-rendimientos, d_model=32, 4 cabezas, MLP 64 con GELU, 2 bloques, atencion completa y lectura = ultimo token + media de tokens; entrada (x, |x|)/0.01; cabeza lineal a H x J = 20 x 41 salidas (J cuantiles por horizonte h = 1..20); mediana + huecos softplus acumulados en ambos sentidos (monotono en alfa por construccion).

Parámetros: 46356. Rejilla de α (J = 41): 0,005; 0,01; 0,025; 0,05; de 0,10 a 0,90 cada 0,025; 0,95; 0,975; 0,99; 0,995. Salida en unidades del modelo (1 unidad = 1 % de log-rendimiento acumulado); el log-rendimiento físico es 0,01 × salida. Pérdida pinball media sobre α y h, AdamW (lr 0.003, coseno hasta el 5 %), lote 128, 800 pasos, f32 en CPU.

| Semilla | Pinball medio, primeros pasos | Pinball medio, últimos pasos | CRPS GARCH modelo | CRPS GARCH gauss. incond. | CRPS régimen modelo | CRPS régimen gauss. incond. | Corr. ancho del cono (h = 10) con vol. de la ventana |
|---|---|---|---|---|---|---|---|
| 11 | 0.8421 | 0.8337 | 1.641e-02 | 1.653e-02 | 1.482e-02 | 1.569e-02 | 0.55 |
| 22 | 0.8404 | 0.8271 | 1.587e-02 | 1.605e-02 | 1.627e-02 | 1.724e-02 | 0.57 |
| 33 | 0.8588 | 0.8608 | 1.572e-02 | 1.580e-02 | 1.698e-02 | 1.792e-02 | 0.61 |
| 44 | 0.8877 | 0.8584 | 1.722e-02 | 1.740e-02 | 1.850e-02 | 1.940e-02 | 0.60 |
| 55 | 0.8420 | 0.8427 | 1.562e-02 | 1.575e-02 | 2.016e-02 | 2.097e-02 | 0.61 |

Pinball medio: de los primeros y de los últimos pasos de entrenamiento (lotes ruidosos; el cono inicial ya es gaussiano de σ diaria 1 %). El cono gaussiano incondicional (σ = desviación típica de la propia serie) sólo da contexto: en estos procesos la predictibilidad del CRPS acumulado es pequeña, así que el listón es que el modelo no sea peor que él y que su cono responda a la volatilidad reciente (última columna: correlación, sobre las entradas de evaluación, del ancho q(0,995) − q(0,005) del cono f64 con la volatilidad realizada de la ventana).

### 2.3 Redondeo

Una sola función para todo el banco: `redondear(x, tipo)` = recorte a ±(máximo finito del tipo) y después ida y vuelta f64 → tipo → f64 con `ml_dtypes` (`float8_e4m3fn`, `float8_e5m2`, `bfloat16`, `float16`) o numpy (`float32`). El recorte emula fp8 con saturación y evita los NaN de desbordamiento de e4m3fn (máx. 448, sin infinitos). Variante «con escala»: se escala por una potencia de 2 (sin error de escalado) para que el máximo absoluto del tensor quepa en el máximo del tipo, se redondea y se desescala; se publica junto a «sin escala», nunca en su lugar. Las activaciones se escalan por muestra (eje 0 = una ventana), los pesos y la serie de entrada por tensor.

| Tipo | Máx. finito | Bits de mantisa | Error relativo máx. teórico |
|---|---|---|---|
| f32 | 3.40282e+38 | 23 | 2^-24 |
| bf16 | 3.38953e+38 | 7 | 2^-8 |
| f16 | 65504 | 10 | 2^-11 |
| e4m3 | 448 | 3 | 2^-4 |
| e5m2 | 57344 | 2 | 2^-3 |

Porcentaje de valores recortados y de valores no nulos que acaban en cero (suma sobre semillas):

| Celda | Medida 1 recortados % | Medida 1 a cero % | Medida 2 recortados % | Medida 2 a cero % |
|---|---|---|---|---|
| f32 sin escala | 0.00 | 0.00 | 0.00 | 0.00 |
| f32 con escala | 0.00 | 0.00 | 0.00 | 0.00 |
| bf16 sin escala | 0.00 | 0.00 | 0.00 | 0.00 |
| bf16 con escala | 0.00 | 0.00 | 0.00 | 0.00 |
| f16 sin escala | 0.00 | 0.00 | 0.00 | 0.18 |
| f16 con escala | 0.00 | 0.00 | 0.00 | 0.00 |
| e4m3 sin escala | 0.00 | 9.33 | 0.00 | 7.98 |
| e4m3 con escala | 0.00 | 0.00 | 0.00 | 1.58 |
| e5m2 sin escala | 0.00 | 0.08 | 0.00 | 2.40 |
| e5m2 con escala | 0.00 | 0.00 | 0.00 | 0.00 |


### 2.4 Definición de la dispersión entre semillas (umbral)

n = 5 semillas; cada semilla cambia los datos sintéticos, la inicialización y el orden del entrenamiento. Dispersión = desviación típica muestral (ddof = 1) entre semillas.

- Medida 1: métrica m (error de recuperación, CRPS) por tipo T y semilla s. Umbral = max(sd_s(m_T), sd_s(m_f64)). Pierde si |media_s(m_T) − media_s(m_f64)| > umbral.
- Medidas 2 y 3: magnitud x (cada grupo de cuantiles, diferencias contiguas, σ_loc) sobre el conjunto fijo de entradas de evaluación. Umbral = RMS sobre entradas (y horizontes, α, K) de la desviación típica entre los modelos f64 de las semillas. Error del tipo T = mediana sobre semillas del RMS de (x_T − x_f64) en el mismo modelo. Pierde si error > umbral.
- Se publica también el cociente error / umbral.

### 2.5 Procedimiento de la medida 3 (Dupire, fijo)

S0 = 1, tipos cero, h = días/252; S_h(α) = exp(q(α, h)) con recentrado multiplicativo para que la media discreta Σ w_j S_j sea 1 (forward = S0; los factores se publican en 3.3). C(K, h) = Σ_j w_j (S_j − K)⁺ con pesos trapezoidales en α y la masa de las colas asignada al cuantil extremo (error declarado: no se extrapola fuera de [0,005; 0,995]). Rejilla de K: 9 puntos equiespaciados en [máx S_h(0,10), mín S_h(0,90)] sobre los horizontes k−1, k, k+1; ∂C/∂h por diferencias centradas entre k−1 y k+1; ∂²C/∂K² por diferencias centradas en K; σ_loc² = 2 ∂C/∂h / (K² ∂²C/∂K²) sólo donde ∂²C/∂K² > 0.5 y ∂C/∂h > 0 (región válida; los puntos fuera se cuentan, no se rellenan). Para comparar tipos la rejilla de K se fija con el cono medio de los modelos f64 (consenso), así todos los modelos y tipos se evalúan en los mismos K; σ_loc se evalúa en los 7 K interiores y en los horizontes de 2 a 19 días. El error se calcula sobre los puntos válidos en los 5 modelos f64 y en el tipo; la cobertura (fracción de esos puntos que el tipo conserva) se publica y, si baja de 90 %, el tipo pierde aunque el RMS de los puntos que quedan sea pequeño.

## 3. Resultados por medida (valor, umbral, veredicto)

### 3.1 Medida 1 — entrada

Se redondean sólo los log-rendimientos de entrada (unidades físicas, ~1e-2; la serie entera es el tensor de la variante «con escala»); el transformer f32 entrenado **no se reentrena**: se evalúa sobre las series sin redondear con las entradas redondeadas. «Media» es la media entre semillas de la métrica con ese tipo; «Dif.» es |media_T − media_f64|.

- GARCH: `arch` (normal, media cero) sobre 100·r; persistencia α+β y ω (reescalado a unidades de r).
- Régimen: HMM de 2 estados `GBM_P` del motor quantdesk (`Engine.calibrate`, `HmmCalibrationOptions(seed=7)`) sobre niveles S0·exp(cumsum(r redondeado)) con S0 = 100 y tiempos i/252; estados ordenados por σ estimada creciente; probabilidad de régimen = posterior suavizada (`gamma_by_step`), medida con el Brier frente al estado verdadero de cada día.
- CRPS aproximado por cuantiles: 2 Σ_j w_j pinball_α_j(y − q_j) con los pesos trapezoidales de la rejilla de α (colas al cuantil extremo), media sobre ventanas (una cada 10 días: GARCH 10000 puntos, régimen 2500) y horizontes h = 1..20; el objetivo es el log-rendimiento acumulado realizado sin redondear.

**garch_persistencia** — GARCH: |alfa+beta estimado - verdadero| (arch, normal, media cero) (unidad: abs). Referencia f64: media 3.943e-03, sd 1.515e-03.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 3.943e-03 | 2.420e-09 | 1.515e-03 | 0.00 | no pierde |
| f32 con escala | 3.943e-03 | 2.420e-09 | 1.515e-03 | 0.00 | no pierde |
| bf16 sin escala | 3.947e-03 | 3.956e-06 | 1.515e-03 | 0.00 | no pierde |
| bf16 con escala | 3.947e-03 | 3.956e-06 | 1.515e-03 | 0.00 | no pierde |
| f16 sin escala | 3.942e-03 | 2.811e-07 | 1.516e-03 | 0.00 | no pierde |
| f16 con escala | 3.942e-03 | 2.805e-07 | 1.516e-03 | 0.00 | no pierde |
| e4m3 sin escala | 3.998e-03 | 5.491e-05 | 1.554e-03 | 0.04 | no pierde |
| e4m3 con escala | 3.980e-03 | 3.770e-05 | 1.515e-03 | 0.02 | no pierde |
| e5m2 sin escala | 3.935e-03 | 7.772e-06 | 1.530e-03 | 0.01 | no pierde |
| e5m2 con escala | 3.936e-03 | 7.167e-06 | 1.530e-03 | 0.00 | no pierde |

**garch_omega** — GARCH: |omega estimado / omega verdadero - 1| (unidad: relativo). Referencia f64: media 1.149e-01, sd 4.472e-02.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 1.149e-01 | 5.640e-08 | 4.472e-02 | 0.00 | no pierde |
| f32 con escala | 1.149e-01 | 5.640e-08 | 4.472e-02 | 0.00 | no pierde |
| bf16 sin escala | 1.151e-01 | 2.281e-04 | 4.502e-02 | 0.01 | no pierde |
| bf16 con escala | 1.151e-01 | 2.281e-04 | 4.502e-02 | 0.01 | no pierde |
| f16 sin escala | 1.149e-01 | 1.832e-05 | 4.472e-02 | 0.00 | no pierde |
| f16 con escala | 1.149e-01 | 1.823e-05 | 4.472e-02 | 0.00 | no pierde |
| e4m3 sin escala | 1.206e-01 | 5.722e-03 | 4.590e-02 | 0.12 | no pierde |
| e4m3 con escala | 1.156e-01 | 7.522e-04 | 4.472e-02 | 0.02 | no pierde |
| e5m2 sin escala | 1.123e-01 | 2.598e-03 | 5.678e-02 | 0.05 | no pierde |
| e5m2 con escala | 1.123e-01 | 2.586e-03 | 5.677e-02 | 0.05 | no pierde |

**hmm_matriz** — HMM: max |P estimada - P verdadera| (estados ordenados por sigma) (unidad: abs). Referencia f64: media 4.226e-03, sd 1.633e-03.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 4.226e-03 | 6.527e-12 | 1.633e-03 | 0.00 | no pierde |
| f32 con escala | 4.226e-03 | 6.527e-12 | 1.633e-03 | 0.00 | no pierde |
| bf16 sin escala | 4.225e-03 | 2.902e-07 | 1.635e-03 | 0.00 | no pierde |
| bf16 con escala | 4.225e-03 | 2.902e-07 | 1.635e-03 | 0.00 | no pierde |
| f16 sin escala | 4.226e-03 | 5.107e-07 | 1.633e-03 | 0.00 | no pierde |
| f16 con escala | 4.226e-03 | 5.107e-07 | 1.633e-03 | 0.00 | no pierde |
| e4m3 sin escala | 4.186e-03 | 3.912e-05 | 1.633e-03 | 0.02 | no pierde |
| e4m3 con escala | 4.285e-03 | 5.907e-05 | 1.645e-03 | 0.04 | no pierde |
| e5m2 sin escala | 4.295e-03 | 6.989e-05 | 1.721e-03 | 0.04 | no pierde |
| e5m2 con escala | 4.295e-03 | 6.989e-05 | 1.721e-03 | 0.04 | no pierde |

**hmm_regimen** — HMM: Brier de la probabilidad suavizada de regimen frente al estado verdadero (unidad: brier). Referencia f64: media 3.773e-02, sd 8.582e-03.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 3.773e-02 | 1.221e-10 | 8.582e-03 | 0.00 | no pierde |
| f32 con escala | 3.773e-02 | 1.221e-10 | 8.582e-03 | 0.00 | no pierde |
| bf16 sin escala | 3.773e-02 | 2.666e-07 | 8.598e-03 | 0.00 | no pierde |
| bf16 con escala | 3.773e-02 | 2.666e-07 | 8.598e-03 | 0.00 | no pierde |
| f16 sin escala | 3.773e-02 | 9.964e-07 | 8.582e-03 | 0.00 | no pierde |
| f16 con escala | 3.773e-02 | 9.964e-07 | 8.582e-03 | 0.00 | no pierde |
| e4m3 sin escala | 3.776e-02 | 3.115e-05 | 8.582e-03 | 0.00 | no pierde |
| e4m3 con escala | 3.787e-02 | 1.438e-04 | 8.582e-03 | 0.02 | no pierde |
| e5m2 sin escala | 3.789e-02 | 1.624e-04 | 8.971e-03 | 0.02 | no pierde |
| e5m2 con escala | 3.789e-02 | 1.624e-04 | 8.971e-03 | 0.02 | no pierde |

**hmm_sigma** — HMM: max_k |sigma_k estimada / sigma_k verdadera - 1| (unidad: relativo). Referencia f64: media 2.127e-02, sd 4.442e-03.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 2.127e-02 | 3.327e-10 | 4.442e-03 | 0.00 | no pierde |
| f32 con escala | 2.127e-02 | 3.327e-10 | 4.442e-03 | 0.00 | no pierde |
| bf16 sin escala | 2.127e-02 | 6.175e-06 | 4.473e-03 | 0.00 | no pierde |
| bf16 con escala | 2.127e-02 | 6.175e-06 | 4.473e-03 | 0.00 | no pierde |
| f16 sin escala | 2.127e-02 | 2.299e-06 | 4.442e-03 | 0.00 | no pierde |
| f16 con escala | 2.127e-02 | 2.299e-06 | 4.442e-03 | 0.00 | no pierde |
| e4m3 sin escala | 2.034e-02 | 9.361e-04 | 5.815e-03 | 0.16 | no pierde |
| e4m3 con escala | 2.202e-02 | 7.467e-04 | 4.442e-03 | 0.17 | no pierde |
| e5m2 sin escala | 1.978e-02 | 1.488e-03 | 6.324e-03 | 0.24 | no pierde |
| e5m2 con escala | 1.978e-02 | 1.488e-03 | 6.324e-03 | 0.24 | no pierde |

**crps_garch** — CRPS del cono del transformer sobre rendimientos GARCH (media sobre ventanas y h) (unidad: log-rend.). Referencia f64: media 1.617e-02, sd 6.634e-04.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 1.617e-02 | 0.000e+00 | 6.634e-04 | 0.00 | no pierde |
| f32 con escala | 1.617e-02 | 0.000e+00 | 6.634e-04 | 0.00 | no pierde |
| bf16 sin escala | 1.617e-02 | 3.981e-08 | 6.634e-04 | 0.00 | no pierde |
| bf16 con escala | 1.617e-02 | 3.981e-08 | 6.634e-04 | 0.00 | no pierde |
| f16 sin escala | 1.617e-02 | 3.976e-09 | 6.634e-04 | 0.00 | no pierde |
| f16 con escala | 1.617e-02 | 3.980e-09 | 6.634e-04 | 0.00 | no pierde |
| e4m3 sin escala | 1.617e-02 | 1.882e-06 | 6.643e-04 | 0.00 | no pierde |
| e4m3 con escala | 1.617e-02 | 2.614e-07 | 6.636e-04 | 0.00 | no pierde |
| e5m2 sin escala | 1.617e-02 | 2.176e-06 | 6.636e-04 | 0.00 | no pierde |
| e5m2 con escala | 1.617e-02 | 2.176e-06 | 6.636e-04 | 0.00 | no pierde |

**crps_regimen** — CRPS del cono del transformer sobre rendimientos con cambio de regimen (unidad: log-rend.). Referencia f64: media 1.735e-02, sd 2.058e-03.

| Celda | Media | Dif. | Umbral | Cociente | Veredicto |
|---|---|---|---|---|---|
| f32 sin escala | 1.735e-02 | 0.000e+00 | 2.058e-03 | 0.00 | no pierde |
| f32 con escala | 1.735e-02 | 0.000e+00 | 2.058e-03 | 0.00 | no pierde |
| bf16 sin escala | 1.735e-02 | 1.080e-07 | 2.058e-03 | 0.00 | no pierde |
| bf16 con escala | 1.735e-02 | 1.080e-07 | 2.058e-03 | 0.00 | no pierde |
| f16 sin escala | 1.735e-02 | 1.455e-09 | 2.058e-03 | 0.00 | no pierde |
| f16 con escala | 1.735e-02 | 1.452e-09 | 2.058e-03 | 0.00 | no pierde |
| e4m3 sin escala | 1.735e-02 | 2.330e-06 | 2.058e-03 | 0.00 | no pierde |
| e4m3 con escala | 1.735e-02 | 2.102e-07 | 2.060e-03 | 0.00 | no pierde |
| e5m2 sin escala | 1.735e-02 | 7.481e-07 | 2.058e-03 | 0.00 | no pierde |
| e5m2 con escala | 1.735e-02 | 7.486e-07 | 2.058e-03 | 0.00 | no pierde |

**vol_de_la_vol** — Vol de la vol (volatilidad estocastica): veredicto **no medida**. la ficha pide parametros conocidos de GARCH y de regimen y deja la vol estocastica como opcional; estimar la vol de la vol exige un estimador propio (QML/Kalman sobre log r^2 o MCMC) que no esta en arch ni en el motor, y con rendimientos redondeados a cero el log r^2 no existe sin un desplazamiento arbitrario (el resultado dependeria de ese desplazamiento, no del tipo). No se inventa ningun numero.

Ajustes que no convergieron (optimizador de arch o del motor), por celda: ninguno.

Ajustes fallidos (la métrica correspondiente queda «no medida»): ninguno.

### 3.2 Medida 2 — inferencia

El mismo modelo (pesos entrenados) con pesos (todos los parámetros) y activaciones redondeados al tipo en cada frontera de capa, frente a la referencia del mismo modelo en f64. La entrada del modelo es el rendimiento ya dividido por 0,01 (la medida 1 ya cubre el redondeo del rendimiento físico); la salida se mide en log-rendimiento físico (0,01 × salida del modelo, sin redondeo posterior). Error = mediana entre semillas del RMS sobre las entradas de evaluación.

**q_todos** — todos los cuantiles q(alfa, h). Umbral (ruido de semilla del modelo f64): 2.909e-03.

| Celda | Error | Umbral | Cociente | Veredicto |
|---|---|---|---|---|
| f32 sin escala | 1.379e-09 | 2.909e-03 | 0.00 | no pierde |
| f32 con escala | 1.379e-09 | 2.909e-03 | 0.00 | no pierde |
| bf16 sin escala | 9.693e-05 | 2.909e-03 | 0.03 | no pierde |
| bf16 con escala | 9.693e-05 | 2.909e-03 | 0.03 | no pierde |
| f16 sin escala | 1.212e-05 | 2.909e-03 | 0.00 | no pierde |
| f16 con escala | 1.210e-05 | 2.909e-03 | 0.00 | no pierde |
| e4m3 sin escala | 1.544e-03 | 2.909e-03 | 0.53 | no pierde |
| e4m3 con escala | 1.532e-03 | 2.909e-03 | 0.53 | no pierde |
| e5m2 sin escala | 3.219e-03 | 2.909e-03 | 1.11 | pierde |
| e5m2 con escala | 3.220e-03 | 2.909e-03 | 1.11 | pierde |

**q_0005** — cuantil q(0,005, h). Umbral (ruido de semilla del modelo f64): 7.891e-03.

| Celda | Error | Umbral | Cociente | Veredicto |
|---|---|---|---|---|
| f32 sin escala | 3.251e-09 | 7.891e-03 | 0.00 | no pierde |
| f32 con escala | 3.251e-09 | 7.891e-03 | 0.00 | no pierde |
| bf16 sin escala | 2.294e-04 | 7.891e-03 | 0.03 | no pierde |
| bf16 con escala | 2.294e-04 | 7.891e-03 | 0.03 | no pierde |
| f16 sin escala | 2.805e-05 | 7.891e-03 | 0.00 | no pierde |
| f16 con escala | 2.803e-05 | 7.891e-03 | 0.00 | no pierde |
| e4m3 sin escala | 3.739e-03 | 7.891e-03 | 0.47 | no pierde |
| e4m3 con escala | 3.689e-03 | 7.891e-03 | 0.47 | no pierde |
| e5m2 sin escala | 7.876e-03 | 7.891e-03 | 1.00 | no pierde |
| e5m2 con escala | 7.889e-03 | 7.891e-03 | 1.00 | no pierde |

**q_0995** — cuantil q(0,995, h). Umbral (ruido de semilla del modelo f64): 6.595e-03.

| Celda | Error | Umbral | Cociente | Veredicto |
|---|---|---|---|---|
| f32 sin escala | 3.107e-09 | 6.595e-03 | 0.00 | no pierde |
| f32 con escala | 3.107e-09 | 6.595e-03 | 0.00 | no pierde |
| bf16 sin escala | 2.208e-04 | 6.595e-03 | 0.03 | no pierde |
| bf16 con escala | 2.208e-04 | 6.595e-03 | 0.03 | no pierde |
| f16 sin escala | 2.690e-05 | 6.595e-03 | 0.00 | no pierde |
| f16 con escala | 2.692e-05 | 6.595e-03 | 0.00 | no pierde |
| e4m3 sin escala | 3.631e-03 | 6.595e-03 | 0.55 | no pierde |
| e4m3 con escala | 3.591e-03 | 6.595e-03 | 0.54 | no pierde |
| e5m2 sin escala | 7.102e-03 | 6.595e-03 | 1.08 | pierde |
| e5m2 con escala | 7.105e-03 | 6.595e-03 | 1.08 | pierde |

**dq_todas** — diferencias de cuantiles contiguos q(alfa_j+1, h) - q(alfa_j, h). Umbral (ruido de semilla del modelo f64): 7.664e-04.

| Celda | Error | Umbral | Cociente | Veredicto |
|---|---|---|---|---|
| f32 sin escala | 1.433e-09 | 7.664e-04 | 0.00 | no pierde |
| f32 con escala | 1.433e-09 | 7.664e-04 | 0.00 | no pierde |
| bf16 sin escala | 9.419e-05 | 7.664e-04 | 0.12 | no pierde |
| bf16 con escala | 9.419e-05 | 7.664e-04 | 0.12 | no pierde |
| f16 sin escala | 1.177e-05 | 7.664e-04 | 0.02 | no pierde |
| f16 con escala | 1.177e-05 | 7.664e-04 | 0.02 | no pierde |
| e4m3 sin escala | 1.495e-03 | 7.664e-04 | 1.95 | pierde |
| e4m3 con escala | 1.495e-03 | 7.664e-04 | 1.95 | pierde |
| e5m2 sin escala | 2.864e-03 | 7.664e-04 | 3.74 | pierde |
| e5m2 con escala | 2.863e-03 | 7.664e-04 | 3.74 | pierde |

**dq_cola_inf** — diferencia contigua de la cola inferior q(0,01, h) - q(0,005, h). Umbral (ruido de semilla del modelo f64): 1.874e-03.

| Celda | Error | Umbral | Cociente | Veredicto |
|---|---|---|---|---|
| f32 sin escala | 3.618e-09 | 1.874e-03 | 0.00 | no pierde |
| f32 con escala | 3.618e-09 | 1.874e-03 | 0.00 | no pierde |
| bf16 sin escala | 2.389e-04 | 1.874e-03 | 0.13 | no pierde |
| bf16 con escala | 2.389e-04 | 1.874e-03 | 0.13 | no pierde |
| f16 sin escala | 2.979e-05 | 1.874e-03 | 0.02 | no pierde |
| f16 con escala | 2.976e-05 | 1.874e-03 | 0.02 | no pierde |
| e4m3 sin escala | 3.781e-03 | 1.874e-03 | 2.02 | pierde |
| e4m3 con escala | 3.812e-03 | 1.874e-03 | 2.03 | pierde |
| e5m2 sin escala | 7.489e-03 | 1.874e-03 | 4.00 | pierde |
| e5m2 con escala | 7.490e-03 | 1.874e-03 | 4.00 | pierde |

**dq_cola_sup** — diferencia contigua de la cola superior q(0,995, h) - q(0,99, h). Umbral (ruido de semilla del modelo f64): 1.924e-03.

| Celda | Error | Umbral | Cociente | Veredicto |
|---|---|---|---|---|
| f32 sin escala | 3.408e-09 | 1.924e-03 | 0.00 | no pierde |
| f32 con escala | 3.408e-09 | 1.924e-03 | 0.00 | no pierde |
| bf16 sin escala | 2.241e-04 | 1.924e-03 | 0.12 | no pierde |
| bf16 con escala | 2.241e-04 | 1.924e-03 | 0.12 | no pierde |
| f16 sin escala | 2.808e-05 | 1.924e-03 | 0.01 | no pierde |
| f16 con escala | 2.800e-05 | 1.924e-03 | 0.01 | no pierde |
| e4m3 sin escala | 3.723e-03 | 1.924e-03 | 1.94 | pierde |
| e4m3 con escala | 3.709e-03 | 1.924e-03 | 1.93 | pierde |
| e5m2 sin escala | 6.533e-03 | 1.924e-03 | 3.40 | pierde |
| e5m2 con escala | 6.535e-03 | 1.924e-03 | 3.40 | pierde |

**Diferencias contiguas que se anulan o cambian de signo** (porcentaje sobre todas las diferencias q(α_j+1, h) − q(α_j, h); media entre semillas):

| Celda | Se anulan % | Cambian de signo % |
|---|---|---|
| f32 sin escala | 0.00 | 0.00 |
| f32 con escala | 0.00 | 0.00 |
| bf16 sin escala | 0.00 | 0.00 |
| bf16 con escala | 0.00 | 0.00 |
| f16 sin escala | 0.00 | 0.00 |
| f16 con escala | 0.00 | 0.00 |
| e4m3 sin escala | 0.17 | 0.00 |
| e4m3 con escala | 0.16 | 0.00 |
| e5m2 sin escala | 14.77 | 0.00 |
| e5m2 con escala | 14.77 | 0.00 |

**Error relativo por capa** (norma, ‖x_T − x_f64‖ / ‖x_f64‖ sobre las entradas de evaluación; mediana entre semillas; sin umbral entre semillas porque las activaciones internas de modelos distintos no comparten base, así que sólo se publican):

| Capa | f32 sin escala | f32 con escala | bf16 sin escala | bf16 con escala | f16 sin escala | f16 con escala | e4m3 sin escala | e4m3 con escala | e5m2 sin escala | e5m2 con escala |
|---|---|---|---|---|---|---|---|---|---|---|
| emb | 4.1e-08 | 4.1e-08 | 3.2e-03 | 3.2e-03 | 4.0e-04 | 4.0e-04 | 5.0e-02 | 5.0e-02 | 9.9e-02 | 9.9e-02 |
| b0.attn | 5.8e-08 | 5.8e-08 | 5.3e-03 | 5.3e-03 | 5.9e-04 | 5.9e-04 | 8.4e-02 | 8.4e-02 | 1.6e-01 | 1.6e-01 |
| b0.res1 | 5.8e-08 | 5.8e-08 | 4.8e-03 | 4.8e-03 | 5.6e-04 | 5.6e-04 | 7.6e-02 | 7.6e-02 | 1.4e-01 | 1.4e-01 |
| b0.mlp | 5.9e-08 | 5.9e-08 | 5.3e-03 | 5.3e-03 | 6.1e-04 | 6.1e-04 | 7.7e-02 | 7.6e-02 | 1.4e-01 | 1.4e-01 |
| b0.res2 | 6.0e-08 | 6.0e-08 | 5.0e-03 | 5.0e-03 | 5.8e-04 | 5.8e-04 | 7.6e-02 | 7.6e-02 | 1.5e-01 | 1.5e-01 |
| b1.attn | 4.8e-08 | 4.8e-08 | 4.2e-03 | 4.2e-03 | 5.6e-04 | 5.6e-04 | 7.0e-02 | 6.6e-02 | 1.2e-01 | 1.2e-01 |
| b1.res1 | 6.1e-08 | 6.1e-08 | 4.8e-03 | 4.8e-03 | 5.9e-04 | 5.9e-04 | 7.6e-02 | 7.7e-02 | 1.5e-01 | 1.5e-01 |
| b1.mlp | 6.4e-08 | 6.4e-08 | 5.2e-03 | 5.2e-03 | 6.5e-04 | 6.5e-04 | 8.2e-02 | 8.2e-02 | 1.7e-01 | 1.7e-01 |
| b1.res2 | 6.2e-08 | 6.2e-08 | 4.8e-03 | 4.8e-03 | 5.9e-04 | 5.9e-04 | 7.5e-02 | 7.6e-02 | 1.5e-01 | 1.5e-01 |
| ln_final | 6.0e-08 | 6.0e-08 | 5.5e-03 | 5.5e-03 | 6.5e-04 | 6.5e-04 | 8.7e-02 | 8.9e-02 | 1.6e-01 | 1.6e-01 |
| cabeza | 3.0e-08 | 3.0e-08 | 2.6e-03 | 2.6e-03 | 3.2e-04 | 3.2e-04 | 4.2e-02 | 4.1e-02 | 8.4e-02 | 8.4e-02 |
| salida | 3.2e-08 | 3.2e-08 | 2.4e-03 | 2.4e-03 | 2.8e-04 | 2.8e-04 | 3.6e-02 | 3.6e-02 | 7.6e-02 | 7.6e-02 |

### 3.3 Medida 3 — derivados de la salida

σ_loc (H1) por Dupire desde el cono de cada tipo (el de la medida 2). Puntos de la rejilla: 64512; válidos en los modelos f64: 100.00 % (por modelo: 100.00, 100.00, 100.00, 100.00, 100.00 %); σ_loc f64 mediana 1.435e-01; factor de recentrado f64: mediana 0.999341, mín 0.994717, máx 1.008944. Umbral (ruido de semilla de σ_loc f64): 1.198e-02.

| Celda | Error σ_loc | Umbral | Cociente | Cobertura % | Factor recentrado T/f64 (mediana) | Factor T/f64 máx. desviación absoluta | Veredicto |
|---|---|---|---|---|---|---|---|
| f32 sin escala | 1.459e-08 | 1.198e-02 | 0.00 | 100.00 | 1.000000 | 1.621e-09 | no pierde |
| f32 con escala | 1.459e-08 | 1.198e-02 | 0.00 | 100.00 | 1.000000 | 1.621e-09 | no pierde |
| bf16 sin escala | 1.023e-03 | 1.198e-02 | 0.09 | 100.00 | 1.000002 | 1.740e-04 | no pierde |
| bf16 con escala | 1.023e-03 | 1.198e-02 | 0.09 | 100.00 | 1.000002 | 1.740e-04 | no pierde |
| f16 sin escala | 1.270e-04 | 1.198e-02 | 0.01 | 100.00 | 1.000000 | 2.160e-05 | no pierde |
| f16 con escala | 1.269e-04 | 1.198e-02 | 0.01 | 100.00 | 1.000000 | 2.160e-05 | no pierde |
| e4m3 sin escala | 1.741e-02 | 1.198e-02 | 1.45 | 100.00 | 1.000004 | 2.288e-03 | pierde |
| e4m3 con escala | 1.734e-02 | 1.198e-02 | 1.45 | 100.00 | 1.000000 | 1.921e-03 | pierde |
| e5m2 sin escala | 3.506e-02 | 1.198e-02 | 2.93 | 99.76 | 1.000009 | 5.160e-03 | pierde |
| e5m2 con escala | 3.505e-02 | 1.198e-02 | 2.92 | 99.77 | 1.000009 | 5.144e-03 | pierde |

**Delta por AAD** según el tipo del cono: no medida: requiere AAD (engine-nn); no hay diferenciacion automatica del cono hasta engine-nn.

## 4. Tabla final tipo × medida

Por celda y medida: número de métricas que pierden entre las medidas, la de peor cociente (valor, umbral) y el veredicto global (pierde si alguna métrica medida pierde; «no medida» si ninguna se pudo medir).

**Medida 1 (entrada)**

| Celda | Pierden / medidas | Peor métrica | Veredicto |
|---|---|---|---|
| f32 sin escala | 0/7 | garch_persistencia: valor 2.420e-09, umbral 1.515e-03, cociente 0.00 | no pierde |
| f32 con escala | 0/7 | garch_persistencia: valor 2.420e-09, umbral 1.515e-03, cociente 0.00 | no pierde |
| bf16 sin escala | 0/7 | garch_omega: valor 2.281e-04, umbral 4.502e-02, cociente 0.01 | no pierde |
| bf16 con escala | 0/7 | garch_omega: valor 2.281e-04, umbral 4.502e-02, cociente 0.01 | no pierde |
| f16 sin escala | 0/7 | hmm_sigma: valor 2.299e-06, umbral 4.442e-03, cociente 0.00 | no pierde |
| f16 con escala | 0/7 | hmm_sigma: valor 2.299e-06, umbral 4.442e-03, cociente 0.00 | no pierde |
| e4m3 sin escala | 0/7 | hmm_sigma: valor 9.361e-04, umbral 5.815e-03, cociente 0.16 | no pierde |
| e4m3 con escala | 0/7 | hmm_sigma: valor 7.467e-04, umbral 4.442e-03, cociente 0.17 | no pierde |
| e5m2 sin escala | 0/7 | hmm_sigma: valor 1.488e-03, umbral 6.324e-03, cociente 0.24 | no pierde |
| e5m2 con escala | 0/7 | hmm_sigma: valor 1.488e-03, umbral 6.324e-03, cociente 0.24 | no pierde |

**Medida 2 (inferencia)**

| Celda | Pierden / medidas | Peor métrica | Veredicto |
|---|---|---|---|
| f32 sin escala | 0/6 | dq_cola_inf: valor 3.618e-09, umbral 1.874e-03, cociente 0.00 | no pierde |
| f32 con escala | 0/6 | dq_cola_inf: valor 3.618e-09, umbral 1.874e-03, cociente 0.00 | no pierde |
| bf16 sin escala | 0/6 | dq_cola_inf: valor 2.389e-04, umbral 1.874e-03, cociente 0.13 | no pierde |
| bf16 con escala | 0/6 | dq_cola_inf: valor 2.389e-04, umbral 1.874e-03, cociente 0.13 | no pierde |
| f16 sin escala | 0/6 | dq_cola_inf: valor 2.979e-05, umbral 1.874e-03, cociente 0.02 | no pierde |
| f16 con escala | 0/6 | dq_cola_inf: valor 2.976e-05, umbral 1.874e-03, cociente 0.02 | no pierde |
| e4m3 sin escala | 3/6 | dq_cola_inf: valor 3.781e-03, umbral 1.874e-03, cociente 2.02 | pierde |
| e4m3 con escala | 3/6 | dq_cola_inf: valor 3.812e-03, umbral 1.874e-03, cociente 2.03 | pierde |
| e5m2 sin escala | 5/6 | dq_cola_inf: valor 7.489e-03, umbral 1.874e-03, cociente 4.00 | pierde |
| e5m2 con escala | 5/6 | dq_cola_inf: valor 7.490e-03, umbral 1.874e-03, cociente 4.00 | pierde |

**Medida 3 (σ_loc)**

| Celda | Pierden / medidas | Peor métrica | Veredicto |
|---|---|---|---|
| f32 sin escala | 0/1 | sigma_loc: valor 1.459e-08, umbral 1.198e-02, cociente 0.00 | no pierde |
| f32 con escala | 0/1 | sigma_loc: valor 1.459e-08, umbral 1.198e-02, cociente 0.00 | no pierde |
| bf16 sin escala | 0/1 | sigma_loc: valor 1.023e-03, umbral 1.198e-02, cociente 0.09 | no pierde |
| bf16 con escala | 0/1 | sigma_loc: valor 1.023e-03, umbral 1.198e-02, cociente 0.09 | no pierde |
| f16 sin escala | 0/1 | sigma_loc: valor 1.270e-04, umbral 1.198e-02, cociente 0.01 | no pierde |
| f16 con escala | 0/1 | sigma_loc: valor 1.269e-04, umbral 1.198e-02, cociente 0.01 | no pierde |
| e4m3 sin escala | 1/1 | sigma_loc: valor 1.741e-02, umbral 1.198e-02, cociente 1.45 | pierde |
| e4m3 con escala | 1/1 | sigma_loc: valor 1.734e-02, umbral 1.198e-02, cociente 1.45 | pierde |
| e5m2 sin escala | 1/1 | sigma_loc: valor 3.506e-02, umbral 1.198e-02, cociente 2.93 | pierde |
| e5m2 con escala | 1/1 | sigma_loc: valor 3.505e-02, umbral 1.198e-02, cociente 2.92 | pierde |

**Delta por AAD**: no medida: requiere AAD (engine-nn).

## 5. ¿Basta fp8?

Primera respuesta, mecánica (reglas de 2.4 aplicadas a las cifras de arriba), por medida y por variante. «Basta» = ninguna métrica medida pierde; no es una afirmación sobre el entrenamiento ni sobre hardware real (ver 6).

| Celda fp8 | Medida 1 (entrada) | Medida 2 (inferencia) | Medida 3 (σ_loc) | Delta por AAD |
|---|---|---|---|---|
| e4m3 sin escala | basta | no basta | no basta | no medida (requiere AAD) |
| e4m3 con escala | basta | no basta | no basta | no medida (requiere AAD) |
| e5m2 sin escala | basta | no basta | no basta | no medida (requiere AAD) |
| e5m2 con escala | basta | no basta | no basta | no medida (requiere AAD) |

- **Medida 1 (entrada)**
  - sin escala: e4m3: no pierde en ninguna métrica medida; e5m2: no pierde en ninguna métrica medida. Comparación: e4m3 y e5m2 pierden igual número de métricas.
  - con escala: e4m3: no pierde en ninguna métrica medida; e5m2: no pierde en ninguna métrica medida. Comparación: e4m3 y e5m2 pierden igual número de métricas.
- **Medida 2 (inferencia)**
  - sin escala: e4m3: pierde en 3 de 6 (dq_todas, dq_cola_inf, dq_cola_sup); e5m2: pierde en 5 de 6 (q_todos, q_0995, dq_todas, dq_cola_inf, dq_cola_sup). Comparación: e4m3 pierde menos métricas que e5m2.
  - con escala: e4m3: pierde en 3 de 6 (dq_todas, dq_cola_inf, dq_cola_sup); e5m2: pierde en 5 de 6 (q_todos, q_0995, dq_todas, dq_cola_inf, dq_cola_sup). Comparación: e4m3 pierde menos métricas que e5m2.
- **Medida 3 (σ_loc)**
  - sin escala: e4m3: pierde en 1 de 1 (sigma_loc); e5m2: pierde en 1 de 1 (sigma_loc). Comparación: e4m3 y e5m2 pierden igual número de métricas.
  - con escala: e4m3: pierde en 1 de 1 (sigma_loc); e5m2: pierde en 1 de 1 (sigma_loc). Comparación: e4m3 y e5m2 pierden igual número de métricas.

**Respuesta corta** (por celda fp8; la delta por AAD queda sin medir hasta `engine-nn`):

- e4m3 sin escala: basta en M1; no basta en M2 (dq_todas, dq_cola_inf, dq_cola_sup); M3 (sigma_loc).
- e4m3 con escala: basta en M1; no basta en M2 (dq_todas, dq_cola_inf, dq_cola_sup); M3 (sigma_loc).
- e5m2 sin escala: basta en M1; no basta en M2 (q_todos, q_0995, dq_todas, dq_cola_inf, dq_cola_sup); M3 (sigma_loc).
- e5m2 con escala: basta en M1; no basta en M2 (q_todos, q_0995, dq_todas, dq_cola_inf, dq_cola_sup); M3 (sigma_loc).

- e4m3 frente a e5m2 sin escala: e4m3 pierde en 4 métricas y e5m2 en 6 (suma de las tres medidas): e4m3 pierde menos métricas que e5m2.
- e4m3 frente a e5m2 con escala: e4m3 pierde en 4 métricas y e5m2 en 6 (suma de las tres medidas): e4m3 pierde menos métricas que e5m2.

Salvedades: (1) emulación en CPU, no hardware fp8: la acumulación interna del producto matricial sigue en f64 y el hardware real acumula en f32/bf16 con sus propios redondeos; (2) los modelos son pequeños y las series sintéticas, sin colas gruesas ni microestructura; (3) con n = 5 semillas la desviación típica muestral es ella misma ruidosa, así que un cociente cercano a 1 es indeciso; (4) la medida 1 no reentrena, por lo que mide sólo desajuste de entrada, no lo que ganaría un modelo entrenado con esa entrada (medidas 4–5, TS-05-PREC); (5) la medida 2 redondea todos los tensores entre operaciones (más severo que una receta mixta con softmax, LayerNorm y acumuladores en mayor precisión); (6) σ_loc depende de la discretización de α (J = 41) y de K (nK = 9) y no extrapola colas; (7) la variante con escala usa potencias de 2 y máximos por tensor (por muestra en activaciones), no la calibración por canal ni la escala diferida de las recetas de hardware.

## 6. Limitaciones de la emulación y alcance

- La emulación redondea con `ml_dtypes` (f64 → tipo → f64) en cada frontera de capa; la acumulación interna sigue en f64. TS-05-PREC lo corrige en hardware real.
- `ml_dtypes` 0.6.0 convierte f64 → fp8/bf16 pasando por f32: un valor a menos de 2^-24 (relativo) de un empate se redondea como si estuviera en él (doble redondeo). Afecta a ~1e-6 de los valores y no mueve el error relativo máximo por encima de u·(1 + 2^-23).
- Fuera de alcance: medidas 4–5 (entrenamiento por tipo, mezclas), GPU, hardware fp8 real, AAD. La vol de la vol no se mide (3.1).
- Sin red, sin dependencias nuevas; salidas bajo `E:/quantdesk-lab/runs/TS-00-PREC/`.
