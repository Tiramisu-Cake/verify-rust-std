"""Run each relevant selection once. Retain any failure, never retry for green."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
C = Path('/root/kani-ch8-s2-diagnostics-r2-r1-w11')
G = HERE.parents[5]
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}

def run(name, argv, cwd, input=None):
    result = subprocess.run(argv, cwd=cwd, env=env, input=input, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE/name).write_text(result.stdout)
    return {'output': name, 'argv': argv, 'cwd': str(cwd), 'exit': result.returncode, 'selection_runs': 1}

results = []
results.append(run('COMPONENT-BINDINGS.json', [sys.executable, str(HERE/'verify_components.py')], G))
results.append(run('REPRODUCTIONS.json', [sys.executable, str(HERE/'reproduce_repairs.py')], C))
results.append(run('RUNNER-PREFLIGHT.json', [sys.executable, str(HERE.parent/'runner-diagnostics-r2-r1/validate_package.py')], G))
recipe = (HERE.parent/'runner-diagnostics-r2-r1/FINAL-TEST-COMMAND.py').read_text()
recipe = recipe.replace("    'test_rustc_diagnostics',", "    'test_runner.CompileTests.test_single_process_compile_then_two_harnesses_and_bounded_previews',\n    'test_rustc_diagnostics',")
(HERE/'RUNNER-33-RECIPE.py').write_text(recipe)
results.append(run('RUNNER-33-TESTS.txt', [sys.executable, '-'], C/'ch8-s1-control', recipe))
# Materialize source code only from exact historical draft-control objects;
# the composer may be using its own worktree concurrently. No worktree mutation.
with tempfile.TemporaryDirectory(prefix='w14-static-control-') as tmp:
    root = Path(tmp)
    pin = '2d00b9cc14f5a093ccaa0288a0f691fddf3ee84a'
    names = subprocess.check_output(['git', '-C', str(C), 'ls-tree', '-r', '--name-only', pin, '--',
                                     'ch8-s1-control', '.github/workflows/ch8-s2.yml']).decode().splitlines()
    for name in names:
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(subprocess.check_output(['git', '-C', str(C), 'show', pin+':'+name]))
    results.append(run('SOURCE-CFG-MODEL-TESTS.txt', [sys.executable, '-m', 'unittest', '-v', 'test_cfg_pfc'], root/'ch8-s1-control'))
(HERE/'CHECK-RUNS.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, indent=2))
raise SystemExit(any(r['exit'] for r in results))
