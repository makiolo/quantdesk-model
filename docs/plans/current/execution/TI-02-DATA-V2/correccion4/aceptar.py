"""Ejecuta los checks en un git archive fijo; run_selftests.py es el ultimo check."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys

code, out = [Path(p).resolve() for p in sys.argv[1:3]]
out.mkdir(parents=True, exist_ok=True)
log = out / 'aceptacion.log'
log.write_text('fecha=2026-11-11 motor=quantdesk 69fdb39d semilla=no_aplica\n'
               f'git archive {code.name.removeprefix("codigo_")} -> {code}\n'
               '.venv es junction al venv existente; no se instalan paquetes.\n'
               'Cortes: invariantes y revisor 2026-11-01; AUDCAD 2026-11-11 y 2026-11-10T05:00Z/09:35Z/10:00Z.\n'
               f'cwd={code}\n', encoding='utf8')


def run(args):
    command = [sys.executable, '-X', 'utf8', '-u', *map(str, args)]
    r = subprocess.run(command, cwd=code, capture_output=True, text=True, encoding='utf8', timeout=1800)
    return command, r


def record(command, r):
    block = '\n> ' + subprocess.list2cmdline(command) + '\n' + r.stdout + r.stderr + f'exit={r.returncode}\n'
    with log.open('a', encoding='utf8') as f:
        f.write(block)
    print(block, flush=True)


checks = [('scripts/descarga_lago.py', '--selftest'), ('scripts/exportar_market_history.py', '--selftest'),
          (Path(__file__).with_name('verificar.py'), code, out)]
results = []
with ThreadPoolExecutor(max_workers=3) as pool:
    for future in as_completed([pool.submit(run, args) for args in checks]):
        command, r = future.result()
        record(command, r)
        results.append(r)
assert all(r.returncode == 0 for r in results), 'check previo fallo; suite no lanzada'
command, r = run(('scripts/run_selftests.py',))
record(command, r)
assert r.returncode == 0, 'suite fallo'
