"""Rulează notebookurile laboratoarelor de la prima la ultima celulă și păstrează rezultatele pentru site.

Workflow-ul .github/workflows/verificare-laboratoare.yml îl folosește în fiecare săptămână, în două feluri:

    python scripts/verificare-laboratoare.py rulare public/laboratoare/<lab>/<lab>.ipynb rezultate/
    python scripts/verificare-laboratoare.py combinare rezultate/ verificari.json

`rulare` execută notebookul cu nbclient, într-un director de lucru gol, ca într-un runtime Colab nou, și scrie
rezultate/<lab>.json (starea, data, durata, celula la care s-a oprit, mediul) și notebookul rulat, cu rezultatele
celulelor, în rezultate/<lab>.ipynb. Iese cu codul 1 dacă rularea nu ajunge la ultima celulă.

`combinare` adaugă rezultatele în verificari.json, păstrat pe ramura `verificari` a repozitoriului. deploy.yml copiază
fișierul în src/data/, iar site-ul arată ultima rulare pe pagina de introducere a fiecărui laborator, sub butonul
Colab (src/components/Colab.astro).

`rulare` are nevoie de nbclient, nbformat și ipykernel, în mediul Python în care rulează și notebookul.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

# Versiunile acestor pachete, dacă notebookul le-a instalat, ajung în rezultat.
PACKAGES = ['torch', 'numpy', 'transformers', 'diffusers', 'accelerate', 'gymnasium', 'mujoco']
# Câte rulări păstrează istoricul fiecărui laborator (un an, la o rulare pe săptămână).
HISTORY = 52

# Rulat de IPython la pornirea kernelului, înainte de prima celulă (IPYTHONDIR/profile_default/startup/).
# O comandă `!...` sau `%pip` care eșuează doar afișează eroarea, iar notebookul merge mai departe. Pentru verificare,
# un cod de ieșire diferit de zero oprește rularea, ca orice excepție. `%%bash` face deja asta. Variabilele sunt
# legate ca argumente implicite, pentru că `%reset -f`, din notebookurile generate, golește spațiul de nume.
KERNEL_STARTUP = """
def _verificare_comenzi(ip=get_ipython()):
    import subprocess

    def system(cmd, _system=ip.system, _ip=ip, _error=subprocess.CalledProcessError):
        _system(cmd)
        code = _ip.user_ns.get('_exit_code', 0)
        if code:
            raise _error(code, cmd)

    ip.system = system


_verificare_comenzi()
del _verificare_comenzi
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def first_line(source: str) -> str:
    """Primul rând cu cod al celulei, fără comentarii, pentru mesajul de pe site."""
    lines = [line.strip() for line in source.splitlines()]
    code = [line for line in lines if line and not line.startswith('#')]
    line = (code or lines or [''])[0]
    return line if len(line) <= 80 else line[:79] + '…'


def gpu() -> str | None:
    if not shutil.which('nvidia-smi'):
        return None
    try:
        out = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    names = out.stdout.strip().splitlines()
    return names[0] if out.returncode == 0 and names else None


def environment() -> dict:
    memory = None
    try:
        with open('/proc/meminfo') as f:
            kib = int(next(line for line in f if line.startswith('MemTotal:')).split()[1])
        memory = round(kib / 2**20)
    except (OSError, StopIteration, ValueError):
        pass
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pass
    return {
        'sistem': f'{platform.system()} {platform.machine()}',
        'python': platform.python_version(),
        'procesoare': os.cpu_count(),
        'memorie': memory,
        'placaGrafica': gpu(),
        'pachete': packages,
    }


def run_log() -> str | None:
    server, repo, run = (os.environ.get(k) for k in ('GITHUB_SERVER_URL', 'GITHUB_REPOSITORY', 'GITHUB_RUN_ID'))
    return f'{server}/{repo}/actions/runs/{run}' if server and repo and run else None


def run(notebook: Path, out: Path, limit_minutes: float) -> int:
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError, CellTimeoutError, DeadKernelError

    lab = notebook.stem
    nb = nbformat.read(notebook, as_version=4)
    work = Path(tempfile.mkdtemp(prefix=f'{lab}-'))
    ipython_dir = Path(tempfile.mkdtemp(prefix='ipython-'))
    startup = ipython_dir / 'profile_default' / 'startup'
    startup.mkdir(parents=True)
    (startup / '00-verificare.py').write_text(KERNEL_STARTUP, encoding='utf-8')
    os.environ['IPYTHONDIR'] = str(ipython_dir)

    started = now()
    start = time.monotonic()
    deadline = start + limit_minutes * 60
    current: dict = {}

    def on_cell_start(cell, cell_index):
        if cell.cell_type != 'code':
            return
        current.update(index=cell_index, cell=cell)
        print(f'[{(time.monotonic() - start) / 60:6.1f} min] celula {cell_index}: {first_line(cell.source)}', flush=True)

    client = NotebookClient(
        nb,
        kernel_name='python3',
        resources={'metadata': {'path': str(work)}},
        # Limita de timp a celulei este timpul rămas din limita întregului notebook.
        timeout_func=lambda cell: max(60, int(deadline - time.monotonic())),
        on_cell_start=on_cell_start,
    )

    error = None
    try:
        client.execute()
    except CellExecutionError as e:
        error = f'{e.ename}: {e.evalue}'
    except CellTimeoutError:
        error = f'Notebookul a depășit limita de timp ({limit_minutes:g} min).'
    except DeadKernelError:
        error = 'Kernelul s-a oprit (de obicei, din lipsă de memorie).'
    except Exception as e:  # orice altă eroare, de exemplu la pornirea kernelului, este tot un eșec
        error = f'{type(e).__name__}: {e}'
    duration = round(time.monotonic() - start)

    result = {
        'laborator': lab,
        'notebook': str(notebook),
        'stare': 'esuata' if error else 'reusita',
        'data': started,
        'durata': duration,
        'celule': sum(1 for c in nb.cells if c.cell_type == 'code'),
        'mediu': environment(),
        'jurnal': run_log(),
    }
    if error:
        cell = current.get('cell')
        result['eroare'] = {
            'celula': current.get('index'),
            'sursa': first_line(cell.source) if cell is not None else None,
            'mesaj': error[:500],
        }

    out.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, out / f'{lab}.ipynb')
    (out / f'{lab}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if error else 0


def combine(results: Path, data_file: Path) -> None:
    data = json.loads(data_file.read_text(encoding='utf-8')) if data_file.exists() else {}
    labs = data.setdefault('laboratoare', {})
    for path in sorted(results.glob('*.json')):
        result = json.loads(path.read_text(encoding='utf-8'))
        lab = result['laborator']
        entry = labs.setdefault(lab, {})
        entry['ultimaRulare'] = result
        if result['stare'] == 'reusita':
            entry['ultimaRulareReusita'] = result
        short = {k: result[k] for k in ('data', 'stare', 'durata')}
        entry['istoric'] = [short, *entry.get('istoric', [])][:HISTORY]
        print(f'{lab}: {result["stare"]}, {result["durata"] / 60:.0f} min')
    data['actualizat'] = now()
    data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('rulare', help='rulează un notebook și scrie rezultatul')
    p.add_argument('notebook', type=Path)
    p.add_argument('rezultate', type=Path)
    p.add_argument('--limita', type=float, default=300, help='limita de timp a întregului notebook, în minute')
    p = commands.add_parser('combinare', help='adaugă rezultatele în verificari.json')
    p.add_argument('rezultate', type=Path)
    p.add_argument('verificari', type=Path)
    args = parser.parse_args()

    if args.command == 'rulare':
        return run(args.notebook, args.rezultate, args.limita)
    combine(args.rezultate, args.verificari)
    return 0


if __name__ == '__main__':
    sys.exit(main())
