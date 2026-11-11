"""Aceptacion C4 sobre archive: datos y salidas solo bajo el temporal autorizado; historicos solo lectura."""
import ast
from collections import Counter
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

REPO = Path('S:/Projects/quantdesk-model')
CODE = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
BASE = '5b70106'
sys.path.insert(0, str(CODE / 'scripts'))
import data_py
import exportar_market_history as E
from exportar_market_history_lib import selftests as T, validacion as V
import pyarrow.parquet as pq


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def files(p):
    return {f.relative_to(p).as_posix(): sha(f) for f in sorted(p.rglob('*')) if f.is_file()}


def run(code, dump, name, mode, group):
    out, runs = ROOT / (group + '_out'), ROOT / (group + '_runs')
    command = [sys.executable, '-X', 'utf8', str(code / 'scripts/exportar_market_history.py'), '--lago', str(dump),
               '--corte', T.CORTE, '--nombre', name, '--salida-raiz', str(out), '--disponibilidad-ohlcv', mode,
               '--runs', str(runs), '--sobrescribir']
    r = subprocess.run(command, cwd=code, capture_output=True, text=True, encoding='utf8', timeout=180)
    assert r.returncode == 0, (command, r.stdout, r.stderr)
    record = read(runs / (name + '.json'))
    v = record['validacion']
    assert v['ok'] and not v['lookahead']['violaciones'] and v['lookahead']['violaciones_por_fila'] == 0
    policy = v.get('politica_con_lag_admitido', v['politica'])
    assert policy['ok'] and not policy['violaciones']
    proc = T.leer(str(out), name)
    return proc, dict(comando=command, dataset_hash=proc['dataset_hash'], filas=proc['tablas'][0]['filas'],
                      ficheros_sha256=files(out / name), motor_ok=True, politica_ok=True, violaciones_por_fila=0)


before_code = ROOT / 'codigo_antes'
before_code.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(subprocess.check_output(['git', 'archive', BASE, 'scripts'], cwd=REPO))) as p:
    p.extractall(before_code, filter='data')
common = dict(fecha='2026-11-11', base_correccion=BASE, codigo_verificado=CODE.name.removeprefix('codigo_'),
              motor=E.MOTOR, semilla=None)
fixtures = {}
for name, old in (('sin_mt5', ROOT.parent / 'correccion1/sin_mt5'),
                  ('mt5_tardia', ROOT.parent / 'correccion2/mt5_tardia'), ('mt5_tardia_posterior', None)):
    dump = ROOT / name
    if old:
        shutil.copytree(old, dump, dirs_exist_ok=True)
        assert files(dump) == files(old)
    else:
        et = {'symbol': 'EURUSD', 'interval': '1d', 'source': 'mt5'}
        rows = [{**T.barra(T.ns(10, d), T.ns(11, 9, 12)), **et} for d in range(15, 27)]
        T.escribir_volcado(str(dump), {'market.ohlcv.v2': [(et, rows)]})
    modes = {}
    for mode in ('recepcion', 'cierre'):
        (a, before), (b, after) = [run(c, dump, name + '_' + mode, mode, group)
                                  for c, group in ((before_code, 'antes'), (CODE, 'despues'))]
        assert before['dataset_hash'] == after['dataset_hash'], (before, after)
        assert [t['limpieza'] for t in a['tablas']] == [t['limpieza'] for t in b['tablas']]
        if name == 'mt5_tardia_posterior':
            assert after['filas'] == (12 if mode == 'cierre' else 0)
        # Identificacion del productor y politica v3 de C3 son las unicas diferencias admisibles frente a v2.
        # Se conserva el JSON original; la comparacion normalizada se guarda aparte y verifica TODOS los demas campos.
        x, y = deepcopy(a), deepcopy(b)
        code_before, code_after = x.pop('codigo_sha256'), y.pop('codigo_sha256')
        p_before, p_after = x['origenes'][0]['fuente'].pop('politica_fuentes'), y['origenes'][0]['fuente'].pop('politica_fuentes')
        assert p_before['version'] == 'ti-02-data.fuentes/v2' and p_after['version'] == 'ti-02-data.fuentes/v3'
        assert {k: v for k, v in p_before.items() if k not in ('version', 'divisas_fx', 'clasificacion')} == {
            k: v for k, v in p_after.items() if k not in ('version', 'divisas_fx', 'clasificacion')}
        for t in x['tablas']:
            assert t['carga']['seleccion_fuentes'].pop('politica_version') == p_before['version']
        for t in y['tablas']:
            assert t['carga']['seleccion_fuentes'].pop('politica_version') == p_after['version']
        assert x == y, (name, mode, x, y)
        normalized = json.dumps(x, ensure_ascii=False, sort_keys=True).encode()
        modes[mode] = dict(antes=before, despues=after, hash_coincide=True, contadores_identicos=True,
                          procedencia_igual_salvo_identificacion=True, procedencia_normalizada_sha256=hashlib.sha256(normalized).hexdigest(),
                          diferencias_identificacion=dict(codigo_sha256_antes=code_before, codigo_sha256_despues=code_after,
                              politica_antes=p_before['version'], politica_despues=p_after['version'],
                              campos_politica_cambiados=['version', 'divisas_fx', 'clasificacion']))
    fixtures[name] = dict(fixture_sha256=files(dump), modos=modes, coincidencias='2/2')
    print(name + ': hash 2/2; contadores identicos; procedencia igual salvo identificacion de codigo/politica C3.', flush=True)

previous = read(REPO / 'docs/plans/current/execution/TI-02-DATA-V2/regeneracion.json')
original = Path('E:/quantdesk-lab/datasets/TI-02-DATA')
history = []
for case in previous['resultados']:
    name = case['dataset']
    hashes = []
    for ds in (original / name, ROOT.parent / 'regen' / name):
        d = json.loads(data_py.dataset_describe_json(str(ds), True))
        assert d['ok'] and all(t['hash_verified'] for t in d['description']['tables'])
        hashes.append(T.leer(str(ds.parent), name)['dataset_hash'])
    assert hashes[0] == hashes[1] == case['original'] == case['regenerado']
    history.append(dict(dataset=name, original=hashes[0], regenerado=hashes[1], coincide=True, base_codigo='0e67465'))
for path, expected in previous['ficheros_originales_sha256'].items():
    assert sha(original / path) == expected, path
write('invariantes.json', {**common, 'corte': T.CORTE, 'fixtures': fixtures, 'historicos_sin_rehacer': history,
                          'historicos_coincidencias': '4/4', 'originales_bytes_intactos': True})
print('Historicos: 4/4; exportador 0e67465; sin rehacer; originales byte a byte intactos.', flush=True)

nuevos = ROOT / 'nuevos'
nuevos.mkdir(exist_ok=True)
T.prueba_mt5_sin_version_al_corte(str(nuevos))
T.prueba_revisiones_mt5(str(nuevos))
records = []
for ds in sorted((nuevos / 'revisiones_motor').iterdir()):
    name = ds.name
    cutoff = T.ms(11, 10, 10) if 'tres_intermedio' in name else T.ms(11, 10, 5) if 'intermedio' in name else T.ms(11, 10, 9, 35) if 'corte_exacto' in name else T.ms(11, 11)
    m = read(ds / 'manifest.json')
    v = V.validar(str(ds), str(ds.parent), name, m['tables'], cutoff, E.hash_dataset(m['tables']))
    f = pq.read_table(ds / 'lago_ohlcv_1d.parquet').to_pandas()
    assert v['ok'] and not v['lookahead']['violaciones'] and v['lookahead']['violaciones_por_fila'] == 0
    policy = v.get('politica_con_lag_admitido', v['politica'])
    assert policy['ok'] and not policy['violaciones']
    records.append(dict(caso=name, corte_ms=cutoff, close=float(f['close'].iloc[0]), volume=float(f['volume'].iloc[0]),
                        available_at_ms=None if name.endswith('_cierre') else int(f['available_at_ms'].iloc[0]),
                        dataset_hash=E.hash_dataset(m['tables']), ficheros_sha256=files(ds), motor_ok=True,
                        politica_ok=True, violaciones_lookahead=0))
late = [dict(caso=p.stem, validacion=read(p)['validacion']) for p in sorted((nuevos / 'c4_runs').glob('*.json'))]
write('A12.json', {**common, 'casos_AUDCAD': records, 'casos_revisor': late,
                   'tests': ['prueba_mt5_sin_version_al_corte', 'prueba_revisiones_mt5']})
print('A12 C4: 12/12 datasets con motor sin violaciones; proxy usa politica que admite lag 0.', flush=True)

old = subprocess.check_output(['git', 'show', '2021763:scripts/exportar_market_history_lib/selftests.py'], cwd=REPO).decode()
new = (CODE / 'scripts/exportar_market_history_lib/selftests.py').read_text(encoding='utf8')
assertions = lambda s: Counter(ast.dump(n) for n in ast.walk(ast.parse(s)) if isinstance(n, ast.Assert))
assert not assertions(old) - assertions(new), 'asercion previa alterada'
(ROOT / 'aserciones.log').write_text(f'Exportador: {sum(assertions(old).values())} previas intactas; {sum(assertions(new).values())} actuales. Ninguna sustituida, relajada ni eliminada.\n', encoding='utf8')
print('Aserciones previas intactas; solo casos nuevos.', flush=True)
