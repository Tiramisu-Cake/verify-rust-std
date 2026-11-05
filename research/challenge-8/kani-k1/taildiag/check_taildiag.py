#!/usr/bin/env python3
"""Historical G1 source/packet checks pinned to its approved commit; no proof tools."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('static', HERE.parent / 'codefix/trimpart_static.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
BASE = '7a68931f59'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
MODULE = s.VERIFY_DIR + 'taildiag.rs'
LANES = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
         'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh',
         'tool_config/kani-version.toml', 'rust-toolchain.toml', '.gitmodules', '.cargo',
         'library/.cargo', 'library/Cargo.toml', 'library/Cargo.lock']
old, new = s.Source(BASE), s.Source('1c99acce330d708961571bd593ecc322768f690f')
off, on = new.roots(False), new.roots(True)
assert set(off) == set(old.roots(False)), 'ordinary inventory changed'
assert len(off) == 219 and len(on) == 263
for name, (_, item) in old.roots(True).items():
    assert item.text() == on[name][1].text(), f'prior root changed: {name}'
for path, text in old.files.items():
    if path != s.VERIFY_ROOT:
        assert text == new.files[path], f'prior source changed: {path}'
assert new.files[s.VERIFY_ROOT].replace(
    '#[cfg(kani_smallsort_controls)]\nmod taildiag;\n', '') == old.files[s.VERIFY_ROOT]
added = set(on) - set(old.roots(True))
assert len(added) == 10 and all(n.startswith('taildiag::') for n in added)
assert new.file_gate[MODULE], 'new module must be entirely opt-in'
for name in added:
    item = on[name][1]
    assert s.proof_kind(item.all_attrs) == 'proof_for_contract'
    assert 'insert_tail' in s.ser(item.all_attrs)
    assert 'unwind ( 32 )' in s.ser(item.all_attrs)
request_path = HERE / 'g1/RUN-REQUEST.json'
request = json.loads(request_path.read_text())
assert request['request_id'] == 'taildiag-g1-20261105-01'
assert request['agent'] == 'k1-network' and request['controls'] is True
assert request['kind'] == 'diagnostic' and request['runner'] == 'gcb-e2-standard-4'
assert request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 4
assert request['inventory'] is False
assert len(request['harnesses']) == len(added)
assert {r['name'] for r in request['harnesses']} == {s.PREFIX + n for n in added}
assert all(r['expect'] == 'SUCCESS' for r in request['harnesses'])
subprocess.run(['git', 'diff', '--exit-code', BASE, '--', s.SMALLSORT], check=True)
subprocess.run(['git', 'diff', '--exit-code', TOOLING, '--', *LANES], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'diff', '--cached', '--check'], check=True)
for filename, names in [('ordinary-expected.txt', off), ('cfg-on-expected.txt', on),
                        ('g1-expected.txt', added)]:
    (HERE / filename).write_text(''.join(s.PREFIX + n + '\n' for n in sorted(names)))
covers = {s.PREFIX + n: 5 for n in sorted(added)}
(HERE / 'expected-covers.json').write_text(json.dumps(covers, indent=2) + '\n')
report = dict(validation='PASS', scope='source only; not compiler inventory or proof',
              base=subprocess.check_output(['git', 'rev-parse', BASE], text=True).strip(),
              tooling_base=TOOLING, ordinary=len(off), cfg_on=len(on), added=len(added),
              previous_opt_in=len(old.roots(True)) - len(off),
              request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
              expected_covers=sum(covers.values()),
              watchdog_minutes=40, build_timeout_minutes=70, maximum_reservation_usd=0.945)
(HERE / 'check-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
