"""Registro de fuentes de TI-13-PUB: que se ingiere, con que licencia esperada y de que clase D-11 es cada dataset.

La clase D-11 y la fiabilidad de las fechas son DECISIONES de este registro (documentadas en `motivo` y `fechas_evid`);
cambiarlas solo exige reejecutar `procesar` sobre lo crudo. Licencia no verificada contra la evidencia => excluida.
"""
from __future__ import annotations

CORTE_DEFECTO = "2016-10-01"  # decision provisional de la raiz: inicio del historico local de 10 anos (D-07)
SAL = "TI-13-PUB/SPRINT-01/v1"  # sal de la particion train/val
FRAC_VAL = 0.10  # proporcion de series (por hash del id) que van a validacion

# Clases D-11. no_fin: tronco intacto. fin: se corta en --corte (fechas reales) o se excluye (fechas no verificables).
# real: datos reales con fecha que solo van a adaptadores (Binance, FRED, Stooq, Yahoo).
NO_FIN, FIN, REAL = "no_fin", "fin", "real"
FECHAS_REALES, FECHAS_NO_VERIFICABLES = "reales", "no_verificables"

CRITERIO_D11 = (
    "Financiera: serie de precios, rendimientos, tipos de interes o de cambio, indices, credito o macroeconomia "
    "financiera, y todo subconjunto marcado Finance, Econ, Macro o banca en sus metadatos o documentacion (en LOTSA, "
    "el dominio 'Econ/Fin' de la Tabla 14 del paper). Los mixtos (M4, M3, M1) cuentan como financieros enteros salvo "
    "que traigan el dominio por serie. Una serie financiera con fechas reales fiables se corta en --corte (antes: "
    "tronco; desde el corte: adaptadores); sin fechas reales verificables se excluye entera del tronco. Fechas "
    "reales solo si la documentacion del origen describe una base de datos o fuente fechada Y las marcas de los datos "
    "pasan las comprobaciones de plausibilidad; ninguna documentacion consultada lo afirma para las competiciones "
    "M1, M3, M4, NN5, CIF 2016 y Tourism, ni para exchange_rate (el origen no publica fechas)."
)

# Valores de dominio por serie que cuentan como financieros (criterio conservador: lo desconocido tambien).
DOMINIOS_NO_FIN = {"demographic"}  # unico dominio de M4/M3/M1 claramente no economico

_CHRONOS_REPO = "autogluon/chronos_datasets"
_LOTSA_REPO = "Salesforce/lotsa_data"
LOTSA_REPO = _LOTSA_REPO
_ZEN_FMT = "Monash Time Series Forecasting Archive (Zenodo, CC BY 4.0)"


def _ch(config, *, lic, dominio, clase, motivo, fechas=None, fevid="", zenodo=None, freq="", archivos=None):
    return {
        "id": f"chronos__{config}", "fuente": "chronos", "repo": _CHRONOS_REPO, "nombre": config,
        "archivos": archivos or [f"{config}/train-00000-of-00001.parquet"], "extras": [],
        "lic_tarjeta": lic, "zenodo": zenodo, "dominio": dominio, "clase": clase, "motivo": motivo,
        "fechas": fechas, "fechas_evid": fevid, "freq": freq, "formato": "chronos",
        "dominio_col": None,
    }


def _lo(nombre, *, zenodo, dominio, clase, motivo, fechas=None, fevid="", freq=""):
    return {
        "id": f"lotsa__{nombre}", "fuente": "lotsa", "repo": _LOTSA_REPO, "nombre": nombre,
        "archivos": [f"{nombre}/data-00000-of-00001.arrow"],
        "extras": [f"{nombre}/dataset_info.json", f"{nombre}/state.json"],
        "lic_tarjeta": "apache-2.0", "zenodo": zenodo, "dominio": dominio, "clase": clase, "motivo": motivo,
        "fechas": fechas, "fechas_evid": fevid, "freq": freq, "formato": "lotsa", "dominio_col": None,
    }


_NF = "No financiera (energia, transporte, clima, naturaleza, ventas, web o salud)."
_COMP = ("Competicion sin fechas verificables: la documentacion consultada (Zenodo/Monash, tarjeta del corpus) no "
         "afirma que las marcas de fecha sean reales; se excluye entera del tronco (D-11).")
_FRED_MD = "FRED-MD: base de datos fechada del Federal Reserve Bank de St. Louis; la ficha de Zenodo la cita como origen."
_BTC = "bitinfocharts.com: graficos web fechados, segun la ficha de Zenodo."

# Zenodo: id del registro Monash de origen de cada subconjunto (el paper de LOTSA, Tabla 14, atribuye estos
# subconjuntos al repositorio Monash; la correspondencia es por nombre y se declara en licencias.md).
DATASETS = [
    # --- Chronos (lista cerrada de la ficha) ---
    _ch("monash_electricity_hourly", lic="CC BY 4.0", zenodo=4656140, dominio="Energy", clase=NO_FIN, motivo=_NF, freq="h"),
    _ch("monash_traffic", lic="CC BY 4.0", zenodo=4656132, dominio="Transport", clase=NO_FIN, motivo=_NF, freq="h"),
    _ch("taxi_30min", lic="Apache 2.0", dominio="Transport", clase=NO_FIN, motivo=_NF, freq="30min"),
    _ch("monash_hospital", lic="CC BY 4.0", zenodo=4656014, dominio="Healthcare", clase=NO_FIN, motivo=_NF, freq="MS"),
    _ch("monash_weather", lic="CC BY 4.0", zenodo=4654822, dominio="Climate", clase=NO_FIN, motivo=_NF, freq="D"),
    _ch("monash_tourism_monthly", lic="CC BY 4.0", zenodo=4656096, dominio="Econ/Fin (LOTSA)", clase=FIN,
        motivo="Reclasificada a financiera (adicion conservadora): LOTSA la marca Econ/Fin en su Tabla 14.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="MS"),
    _ch("exchange_rate", lic="MIT", dominio="Finance (tipos de cambio)", clase=FIN,
        motivo="Tipos de cambio diarios de 8 divisas: serie financiera.",
        fechas=FECHAS_NO_VERIFICABLES,
        fevid="El origen (laiguokun/multivariate-time-series-data) publica 7588 dias de 1990 a 2016 sin marcas de fecha; "
              "el corpus asigna un inicio.", freq="D"),
    _ch("monash_fred_md", lic="CC BY 4.0", zenodo=4654833, dominio="Macro (FRED-MD)", clase=FIN,
        motivo="Indicadores macroeconomicos del Federal Reserve Bank: macroeconomia financiera.",
        fechas=FECHAS_REALES, fevid=_FRED_MD, freq="MS"),
    _ch("monash_cif_2016", lic="CC BY 4.0", zenodo=4656042, dominio="Banking", clase=FIN,
        motivo="Banca (CIF 2016); 48 de las 72 series son artificiales segun Zenodo.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP + " 48 de 72 series son artificiales.", freq="MS"),
    _ch("monash_nn5_weekly", lic="CC BY 4.0", zenodo=4656125, dominio="Banking (ATM)", clase=FIN,
        motivo="Dominio banca (retiradas de cajeros).", fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="W"),
    # Sin licencia declarada en la tarjeta (ni en el origen M4-methods, sin LICENSE): se bloquean antes de bajar.
    _ch("m4_daily", lic=None, dominio="Econ/Fin mixto (M4)", clase=FIN, motivo="M4 mixto con 'category' por serie.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="D"),
    _ch("m4_monthly", lic=None, dominio="Econ/Fin mixto (M4)", clase=FIN, motivo="M4 mixto con 'category' por serie.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="MS"),
    _ch("training_corpus_kernel_synth_1m", lic=None, dominio="Sintetico (KernelSynth)", clase=NO_FIN,
        motivo="Sintetico: 1M series generadas, sin datos reales.",
        archivos=[f"training_corpus/kernel_synth_1m/train-{i:05d}-of-00020.parquet" for i in range(20)]),
    # --- LOTSA: subconjuntos de varios dominios (todos del repositorio Monash, licencia de origen verificable) ---
    _lo("elecdemand", zenodo=4656069, dominio="Energy", clase=NO_FIN, motivo=_NF, freq="30min"),
    _lo("australian_electricity_demand", zenodo=4659727, dominio="Energy", clase=NO_FIN, motivo=_NF, freq="30min"),
    _lo("solar_power", zenodo=4656027, dominio="Energy", clase=NO_FIN, motivo=_NF, freq="4s"),
    _lo("wind_power", zenodo=4656032, dominio="Energy", clase=NO_FIN, motivo=_NF, freq="4s"),
    _lo("pedestrian_counts", zenodo=4656626, dominio="Transport", clase=NO_FIN, motivo=_NF, freq="h"),
    _lo("traffic_weekly", zenodo=4656135, dominio="Transport", clase=NO_FIN, motivo=_NF, freq="W"),
    _lo("covid_mobility", zenodo=4663809, dominio="Transport", clase=NO_FIN, motivo=_NF, freq="D"),
    _lo("oikolab_weather", zenodo=5184708, dominio="Climate", clase=NO_FIN, motivo=_NF, freq="h"),
    _lo("temperature_rain_with_missing", zenodo=5129073, dominio="Climate", clase=NO_FIN, motivo=_NF, freq="D"),
    _lo("sunspot_with_missing", zenodo=4654773, dominio="Nature", clase=NO_FIN, motivo=_NF, freq="D"),
    _lo("saugeenday", zenodo=4656058, dominio="Nature", clase=NO_FIN, motivo=_NF, freq="D"),
    _lo("car_parts_with_missing", zenodo=4656022, dominio="Sales", clase=NO_FIN, motivo=_NF, freq="MS"),
    _lo("kaggle_web_traffic_weekly", zenodo=4656664, dominio="Web", clase=NO_FIN, motivo=_NF, freq="W"),
    _lo("fred_md", zenodo=4654833, dominio="Econ/Fin", clase=FIN, motivo="Macro (FRED-MD): Econ/Fin en LOTSA.",
        fechas=FECHAS_REALES, fevid=_FRED_MD, freq="ME"),
    _lo("bitcoin_with_missing", zenodo=5121965, dominio="Econ/Fin", clase=FIN,
        motivo="Series asociadas al precio del bitcoin: Econ/Fin en LOTSA.", fechas=FECHAS_REALES, fevid=_BTC, freq="D"),
    _lo("cif_2016_6", zenodo=4656042, dominio="Econ/Fin", clase=FIN, motivo="Banca (CIF 2016), horizonte 6.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP + " 48 de 72 series son artificiales.", freq="ME"),
    _lo("cif_2016_12", zenodo=4656042, dominio="Econ/Fin", clase=FIN, motivo="Banca (CIF 2016), horizonte 12.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP + " 48 de 72 series son artificiales.", freq="ME"),
    _lo("nn5_weekly", zenodo=4656125, dominio="Econ/Fin", clase=FIN, motivo="Dominio banca (retiradas de cajeros).",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="W"),
    _lo("nn5_daily_with_missing", zenodo=4656110, dominio="Econ/Fin", clase=FIN, motivo="Dominio banca (retiradas de cajeros).",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="D"),
    _lo("m1_monthly", zenodo=4656159, dominio="Econ/Fin", clase=FIN, motivo="M1 mixto (macro/micro/industria/demografia) sin dominio por serie.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="ME"),
    _lo("monash_m3_monthly", zenodo=4656298, dominio="Econ/Fin", clase=FIN, motivo="M3 mixto sin dominio por serie en LOTSA.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="ME"),
    _lo("tourism_monthly", zenodo=4656096, dominio="Econ/Fin", clase=FIN, motivo="Econ/Fin en LOTSA (Tabla 14).",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="ME"),
    _lo("m4_daily", zenodo=4656548, dominio="Econ/Fin", clase=FIN, motivo="M4 mixto sin dominio por serie en LOTSA.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="D"),
    _lo("m4_monthly", zenodo=4656480, dominio="Econ/Fin", clase=FIN, motivo="M4 mixto sin dominio por serie en LOTSA.",
        fechas=FECHAS_NO_VERIFICABLES, fevid=_COMP, freq="ME"),
]

# Cripto (data.binance.vision, klines al contado). Intervalo 1d para todos los pares; 1h para los principales.
BINANCE_PARES_1D = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "SOLUSDT", "LTCUSDT", "TRXUSDT", "LINKUSDT"]
BINANCE_PARES_1H = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
BINANCE_BASE = "https://data.binance.vision"
BINANCE_S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
BINANCE = [
    {"id": "binance__klines_1d", "fuente": "binance", "nombre": "klines 1d (spot)", "intervalo": "1d",
     "pares": BINANCE_PARES_1D, "dominio": "Cripto (precios)", "clase": REAL, "fechas": FECHAS_REALES,
     "fechas_evid": "Marcas de apertura de vela publicadas por Binance.", "freq": "D", "formato": "binance",
     "motivo": "Datos reales con fecha: solo adaptadores.", "dominio_col": None},
    {"id": "binance__klines_1h", "fuente": "binance", "nombre": "klines 1h (spot)", "intervalo": "1h",
     "pares": BINANCE_PARES_1H, "dominio": "Cripto (precios)", "clase": REAL, "fechas": FECHAS_REALES,
     "fechas_evid": "Marcas de apertura de vela publicadas por Binance.", "freq": "h", "formato": "binance",
     "motivo": "Datos reales con fecha: solo adaptadores.", "dominio_col": None},
]

# Fuentes que la ficha pide y que no se obtienen: estado y motivo se rellenan con la evidencia en `licencias`.
NO_OBTENIDAS = ["stooq", "yahoo", "fred"]

# Evidencias externas (id -> url). Los registros de Zenodo y las API del Hub se derivan de DATASETS.
URL_EVIDENCIAS = {
    "hf_chronos_api": f"https://huggingface.co/api/datasets/{_CHRONOS_REPO}?blobs=true",
    "hf_chronos_readme": f"https://huggingface.co/datasets/{_CHRONOS_REPO}/raw/main/README.md",
    "hf_lotsa_api": f"https://huggingface.co/api/datasets/{_LOTSA_REPO}?blobs=true",
    "hf_lotsa_readme": f"https://huggingface.co/datasets/{_LOTSA_REPO}/raw/main/README.md",
    "github_m4_licencia": "https://api.github.com/repos/Mcompetitions/M4-methods/license",
    "binance_terms": "https://raw.githubusercontent.com/binance/binance-public-data/master/TERMS_AND_CONDITIONS.md",
    "binance_readme": "https://raw.githubusercontent.com/binance/binance-public-data/master/README.md",
    "yahoo_robots": "https://query1.finance.yahoo.com/robots.txt",
    "yahoo_terms": "https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html",
    "stooq_robots": "https://stooq.com/robots.txt",
    "fred_robots": "https://fred.stlouisfed.org/robots.txt",
    "fred_terms": "https://fred.stlouisfed.org/legal/",
    "fred_csv_muestra": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
}


def por_id(dataset_id: str) -> dict:
    for d in DATASETS + BINANCE:
        if d["id"] == dataset_id:
            return d
    raise KeyError(dataset_id)


def zenodo_ids() -> list:
    return sorted({d["zenodo"] for d in DATASETS if d.get("zenodo")})
