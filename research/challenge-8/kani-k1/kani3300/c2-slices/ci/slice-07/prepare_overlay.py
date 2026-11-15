#!/usr/bin/env python3
"""Install only reviewed CI payload on exact clean F7 head. No build/push/dispatch."""
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
REPO = Path('/root/kani-fix-3300-c2-slices-w15')


def main():
    config = json.loads((HERE / 'inputs.json').read_text())
    def git(*args):
        return subprocess.check_output(['git', '-C', str(REPO), *args])
    assert git('rev-parse', 'HEAD').decode().strip() == config['source_sha']
    assert not git('status', '--porcelain')
    target = REPO / '.github/c2-slices'
    target.mkdir(parents=True, exist_ok=True)
    files = ['inputs.json', 'slice07_ci.py', 'sensitivity.py', 'sensitivity-manifest.json',
             'structural.py', 'structural_compare.py', 'structural_observation.py',
             'structural-manifest.json', 'structural-mixed.rs']
    for name in files:
        (target / name).write_bytes((HERE / name).read_bytes())
    (target / 'test-manifest.json').write_bytes((HERE.parent.parent / 'f7/TEST-MANIFEST.json').read_bytes())
    for source in (HERE / 'sensitivity').glob('*.patch'):
        path = target / 'sensitivity' / source.name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(source.read_bytes())
    for name in git('ls-tree', '-r', '--name-only', config['source_sha'], '--', '.github/workflows').decode().splitlines():
        (REPO / name).unlink()
    (REPO / '.github/workflows/uninit-quick.yml').write_bytes((HERE / 'uninit-quick.yml').read_bytes())
    print('CI-only overlay prepared; native execution NOT_RUN')


if __name__ == '__main__':
    main()
