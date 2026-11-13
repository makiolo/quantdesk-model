"""Ejecuta los checks sobre un git archive; la suite completa es el ultimo check."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys

root = Path(__file__).parent
code = Path((root / 'archivo.txt').read_text(encoding='utf8'))
log = root / 'aceptacion.log'
head = ('fecha=2026-11-11 motor=quantdesk 69fdb39d semilla=no_aplica\n'
        f'git archive {code.name.removeprefix("codigo_")} -> {code}\n'
        '.venv es junction al venv existente; no se instalan paquetes ni se modifica el archive.\n'
        'Cortes A12: 2026-11-11T00:00Z, 2026-11-10T05:00Z/09:35Z/10:00Z; invariantes 2026-11-01.\n'
        f'cwd={code}\n')
log.write_text(head, encoding='utf8')


def run(args):
    command = [sys.executable, '-X', 'utf8', '-u', *map(str, args)]
    result = subprocess.run(command, cwd=code, capture_output=True, text=True, encoding='utf8', timeout=1200)
    return command, result


checks = [('scripts/descarga_lago.py', '--selftest'), ('scripts/exportar_market_history.py', '--selftest'),
          (root / 'verificar.py', code)]
with ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(run, checks))
for command, result in results:
    block = '\n> ' + subprocess.list2cmdline(command) + '\n' + result.stdout + result.stderr + f'exit={result.returncode}\n'
    with log.open('a', encoding='utf8') as f:
        f.write(block)
    print(block, flush=True)
assert all(result.returncode == 0 for _, result in results), 'check previo fallo; suite no lanzada'
command, result = run(('scripts/run_selftests.py',))
block = '\n> ' + subprocess.list2cmdline(command) + '\n' + result.stdout + result.stderr + f'exit={result.returncode}\n'
with log.open('a', encoding='utf8') as f:
    f.write(block)
print(block, flush=True)
assert result.returncode == 0, 'suite fallo'
