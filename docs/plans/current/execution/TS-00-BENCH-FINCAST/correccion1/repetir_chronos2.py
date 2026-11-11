import json, os, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
repo = Path(__file__).resolve().parents[6]
os.chdir(repo)
os.environ['HF_HUB_OFFLINE'] = '1'
sys.path.insert(0, str(repo / 'scripts'))
from banco_walkforward_lib import banco, datos, modelos, rutas
out=Path('E:/quantdesk-lab/runs/TS-00-BENCH-FINCAST/correccion1/chronos2')
out.mkdir(parents=True, exist_ok=True)
ref=Path('E:/quantdesk-lab/runs/TS-00-BENCH/lago_cierre_c20261101')
p=pd.read_parquet(ref/'predicciones.parquet')
tiempos=[1789603200000,1789689600000,1789776000000]
series, ds=datos.cargar_dataset(rutas.dataset_dir('lago_cierre_c20261101'),'lago_ohlcv_1d')
cortes,_=datos.cortes_de_serie(series['AUDCHF'],tiempos,250,banco.HMAX)
assert len(cortes)==3
m=modelos.Chronos2(2)
inicio=time.perf_counter()
pred=pd.DataFrame(banco.correr_serie(series['AUDCHF'],cortes,[m],banco.SEMILLA))
assert pred.ok.all(),pred.error.tolist()
pred.to_parquet(out/'predicciones.parquet',index=False)
met=banco.metricas_tabla(pred,['chronos2'])
met.to_csv(out/'metricas.csv',index=False,float_format='%.10g')
meta={'dataset':ds,'config':{'modelos':['chronos2'],'ventana':250,'horizontes':list(banco.HORIZONTES),'semilla':banco.SEMILLA,'hilos_torch':2},'cruces_cuantiles':banco.contar_cruces(pred),'versiones':banco.versiones()}
meta['comparacion']=banco.comparar(str(out),str(ref))
assert meta['comparacion']['predicciones_identicas'] and meta['comparacion']['metricas_identicas'] and meta['comparacion']['metricas_limpias_identicas'],meta
meta['pared_inferencia_s']=time.perf_counter()-inicio
(out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta['comparacion']))
print(json.dumps(meta['cruces_cuantiles']))
