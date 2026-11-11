"""Aceptacion C3: archive recibido por argv; sin red, originales historicos solo en lectura."""
import ast
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

REPO = Path('S:/Projects/quantdesk-model')
ROOT = Path(__file__).parent
CODE = Path(sys.argv[1])
BASE = '5b70106'
sys.path.insert(0, str(CODE / 'scripts'))
import data_py
import exportar_market_history as E
from exportar_market_history_lib import selftests as T, validacion as V
import pyarrow.parquet as pq


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob('*')) if p.is_file()}


def run(code, dump, name, mode, group):
    out, runs = ROOT / (group + '_out'), ROOT / (group + '_runs')
    command = [sys.executable, '-X', 'utf8', str(code / 'scripts/exportar_market_history.py'), '--lago', str(dump),
               '--corte', T.CORTE, '--nombre', name, '--salida-raiz', str(out), '--disponibilidad-ohlcv', mode,
               '--runs', str(runs), '--sobrescribir']
    result = subprocess.run(command, cwd=code, capture_output=True, text=True, encoding='utf8')
    assert result.returncode == 0, (command, result.stdout, result.stderr)
    record = read(runs / (name + '.json'))
    assert record['validacion']['ok'] and not record['validacion']['lookahead']['violaciones']
    return dict(comando=command, dataset_hash=T.leer(str(out), name)['dataset_hash'],
                ficheros_sha256=record['ficheros_sha256'], validacion_ok=True)


before_code = ROOT / 'codigo_antes'
before_code.mkdir(exist_ok=True)
archive = subprocess.check_output(['git', 'archive', BASE, 'scripts'], cwd=REPO)
with tarfile.open(fileobj=io.BytesIO(archive)) as package:
    package.extractall(before_code, filter='data')

commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=CODE).decode().strip() if (CODE / '.git').exists() else CODE.name.removeprefix('codigo_')
common = dict(fecha='2026-11-11', base_correccion=BASE, codigo_verificado=commit, motor=E.MOTOR, semilla=None)
fixtures = {}
for name, old_dump in (('sin_mt5', ROOT.parent / 'correccion1/sin_mt5'),
                       ('mt5_tardia', ROOT.parent / 'correccion2/mt5_tardia')):
    dump = ROOT / name
    shutil.copytree(old_dump, dump, dirs_exist_ok=True)
    assert files(dump) == files(old_dump)
    modes = {}
    for mode in ('recepcion', 'cierre'):
        before, after = [run(code, dump, name + '_' + mode, mode, group) for code, group in
                         ((before_code, 'hash_antes'), (CODE, 'hash_despues'))]
        assert before['dataset_hash'] == after['dataset_hash'], (before, after)
        modes[mode] = dict(antes=before, despues=after, coincide=True)
    fixtures[name] = dict(fixture_sha256=files(dump), modos=modes, coincidencias='2/2')
    print(name + ': 2/2 hashes iguales contra git archive ' + BASE, flush=True)

previous = read(REPO / 'docs/plans/current/execution/TI-02-DATA-V2/regeneracion.json')
original_root = Path('E:/quantdesk-lab/datasets/TI-02-DATA')
history = []
for case in previous['resultados']:
    name = case['dataset']
    hashes = []
    for dataset in (original_root / name, ROOT.parent / 'regen' / name):
        desc = json.loads(data_py.dataset_describe_json(str(dataset), True))
        assert desc['ok'] and all(t['hash_verified'] for t in desc['description']['tables'])
        hashes.append(T.leer(str(dataset.parent), name)['dataset_hash'])
    assert hashes[0] == hashes[1] == case['original'] == case['regenerado']
    history.append(dict(dataset=name, original=hashes[0], regenerado=hashes[1], coincide=True, base_codigo='0e67465'))
for path, expected in previous['ficheros_originales_sha256'].items():
    assert sha(original_root / path) == expected, path
write('invariantes.json', {**common, 'corte': T.CORTE, 'fixtures': fixtures, 'historicos_sin_rehacer': history,
                          'historicos_coincidencias': '4/4', 'originales_bytes_intactos': True})
print('Historicos: 4/4, exportador 0e67465; sin rehacer; originales byte a byte intactos.', flush=True)

nuevos = ROOT / 'nuevos'
nuevos.mkdir(exist_ok=True)
T.prueba_revisiones_mt5(str(nuevos))
T.prueba_rejilla_mt5(str(nuevos))
records = []
for dataset in sorted((nuevos / 'revisiones_motor').iterdir()):
    name = dataset.name
    cutoff = T.ms(11, 10, 10) if 'tres_intermedio' in name else T.ms(11, 10, 5) if 'intermedio' in name else T.ms(11, 10, 9, 35) if 'corte_exacto' in name else T.ms(11, 11)
    m = read(dataset / 'manifest.json')
    v = V.validar(str(dataset), str(dataset.parent), name, m['tables'], cutoff, E.hash_dataset(m['tables']))
    f = pq.read_table(dataset / 'lago_ohlcv_1d.parquet').to_pandas()
    assert v['ok'] and not v['lookahead']['violaciones'] and v['lookahead']['violaciones_por_fila'] == 0
    policy = v['politica_con_lag_admitido'] if name.endswith('_cierre') else v['politica']
    assert policy['ok'] and not policy['violaciones']
    records.append(dict(caso=name, corte_ms=cutoff, close=float(f['close'].iloc[0]), volume=float(f['volume'].iloc[0]),
                        available_at_ms=None if name.endswith('_cierre') else int(f['available_at_ms'].iloc[0]),
                        disponibilidad_efectiva_ms=T.ms(11, 10) if name.endswith('_cierre') else int(f['available_at_ms'].iloc[0]),
                        dataset_hash=E.hash_dataset(m['tables']), ficheros_sha256=files(dataset),
                        motor_ok=v['ok'], politica_ok=policy['ok'], violaciones=policy['violaciones'],
                        violaciones_lookahead=v['lookahead']['violaciones_por_fila']))
write('A12.json', {**common, 'tests': ['prueba_revisiones_mt5', 'prueba_rejilla_mt5'], 'casos': records,
                   'CLI_revisor_y_revision_futura': '2 modos; mismo hash, manifest y parquet al anadir revision futura',
                   'otras_fuentes_intervalos': 'market_scraper 1d y mt5 1h: primera completa', 'rejilla': '6 rechazos CLI; guarda directa; otras fuentes/intervalos sin cambio'})
print('A12 C3: 10/10 datasets, motor y look-ahead sin violaciones; CLI, futuras y rejilla OK.', flush=True)

old = subprocess.check_output(['git', 'show', BASE + ':scripts/exportar_market_history_lib/selftests.py'], cwd=REPO).decode()
new = (CODE / 'scripts/exportar_market_history_lib/selftests.py').read_text(encoding='utf8')
replacements = [
    ('ti-02-data.fuentes/v2', 'ti-02-data.fuentes/v3'),
    ("assert t['limpieza']['excluidas'] == {'version_en_curso': 1, 'version_posterior_descartada': 1}", "assert t['limpieza']['excluidas'] == {'version_en_curso': 1, 'version_mt5_revisada': 1}"),
    ("assert fila['close'] == 1.1 and fila['available_at_ms'] == ms(10, 28, 0, 10)", "assert fila['close'] == 1.15 and fila['available_at_ms'] == ms(10, 29)"),
    ("assert f['close'].tolist() == [1.1]\n    assert t['contador']", "assert f['close'].tolist() == [1.15]\n    assert t['contador']"),
    ("assert f['close'].tolist() == [1.1] and f['available_at_ms'].tolist() == [ms(1, 14)]", "assert f['close'].tolist() == [1.15] and f['available_at_ms'].tolist() == [ms(1, 14, 1)]"),
    ("assert t['contador']['excluidas'] == {'version_en_curso': 1, 'version_posterior_descartada': 1}", "assert t['contador']['excluidas'] == {'version_en_curso': 1, 'version_mt5_revisada': 1}"),
    ("'version_en_curso': 1, 'version_posterior_descartada': 1, 'posterior_al_corte_por_fecha': 1}", "'version_en_curso': 1, 'posterior_al_corte_por_fecha': 2}"),
]
normalized = old
for a, b in replacements:
    normalized = normalized.replace(a, b)
assertions = lambda s: Counter(ast.dump(n) for n in ast.walk(ast.parse(s)) if isinstance(n, ast.Assert))
assert not assertions(normalized) - assertions(new), 'asercion previa cambiada fuera de la decision A12/v3'
changed = sum((assertions(old) - assertions(new)).values())
assert changed == 9, changed
(ROOT / 'aserciones.log').write_text(
    f'Exportador: {sum(assertions(old).values())} previas; {sum(assertions(new).values())} actuales; 9 sustituciones declaradas.\n'
    '2 literales fuentes/v2 -> v3 (CNH y exclusion de fondos).\n'
    '2 aserciones versiones_mt5: ultima completa y motivo version_mt5_revisada.\n'
    '2 aserciones prueba_cierre_real_mt5 (antes lineas 799-803): close 1.1 -> 1.15 y motivo de revision.\n'
    '3 aserciones prueba_disponibilidad_recepcion_mt5: close/recepcion de la revision, motivo, y corte nominal anterior cuenta las 2 versiones por fecha.\n'
    'Las otras 188 aserciones siguen intactas; las 9 sustituciones son consecuencia exacta de A12/v3.\n'
    'Descarga: cardinalidad 164 -> 156 (9 fondos excluidos + CNH); casos previos conservados y lista de casos ampliada.\n', encoding='utf8')
print(f'Aserciones: {changed} sustituciones exactas A12/v3; otras 188 intactas; nuevas verificadas.', flush=True)
