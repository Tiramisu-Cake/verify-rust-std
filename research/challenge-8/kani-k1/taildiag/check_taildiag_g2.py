#!/usr/bin/env python3
"""G2 source and request checks; compiler inventory/proof remain Cloud-only."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'g2'
spec = importlib.util.spec_from_file_location('static', HERE.parent / 'codefix/trimpart_static.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
G1 = '1c99acce330d708961571bd593ecc322768f690f'
BASE = '7a68931f59'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
MODULE = s.VERIFY_DIR + 'taildiag.rs'
old, new = s.Source(G1), s.Source(None)
off, on = new.roots(False), new.roots(True)
assert set(off) == set(old.roots(False)) and len(off) == 219 and len(on) == 268
for name, (_, item) in old.roots(True).items():
    assert item.text() == on[name][1].text(), f'G1 root changed: {name}'
for path, text in old.files.items():
    if path != MODULE:
        assert new.files[path] == text, f'G1 source changed: {path}'
prior_items = {i.key(): i for i in old.items[MODULE] if i.kind != 'use'}
new_items = {i.key(): i for i in new.items[MODULE] if i.kind != 'use'}
for key, item in prior_items.items():
    assert new_items[key].text() == item.text(), f'G1 helper changed: {key}'
assert new.file_gate[MODULE]
added = set(on) - set(old.roots(True))
expected = {'taildiag::u64_backing17_tail8_to15_no_explicit_frame'} | {
    f'taildiag::insertion_stubbed_u64_backing17_len{lo}_to{hi}'
    for lo, hi in [(1, 4), (5, 8), (9, 12), (13, 16)]}
assert added == expected
for name in added:
    item = on[name][1]
    attrs = s.ser(item.all_attrs)
    assert s.proof_kind(item.all_attrs) == 'proof_for_contract'
    assert 'unwind ( 32 )' in attrs
    if 'insertion_stubbed' in name:
        assert 'insertion_sort_shift_left' in attrs
        assert 'stub_verified ( insert_tail )' in attrs
        assert 'stub ( comparison_covers , omit_comparison_covers )' in attrs
    else:
        assert 'insert_tail' in attrs and 'stub' not in attrs
request_path = HERE.parent / 'RUN-REQUEST.json'
request = json.loads(request_path.read_text())
assert request['request_id'] == 'taildiag-g2-20261105-01'
assert request['agent'] == 'k1-network' and request['controls'] is True
assert request['kind'] == 'diagnostic' and request['runner'] == 'gcb-e2-standard-4'
assert request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 4
assert request['inventory'] is False and len(request['harnesses']) == 5
assert {r['name'] for r in request['harnesses']} == {s.PREFIX + n for n in added}
assert all(r['expect'] == 'SUCCESS' for r in request['harnesses'])
lanes = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
         'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh', 'tool_config/kani-version.toml',
         'rust-toolchain.toml', '.gitmodules', '.cargo', 'library/.cargo',
         'library/Cargo.toml', 'library/Cargo.lock']
subprocess.run(['git', 'diff', '--exit-code', BASE, '--', s.SMALLSORT], check=True)
subprocess.run(['git', 'diff', '--exit-code', TOOLING, '--', *lanes], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)
subprocess.run(['git', 'diff', '--cached', '--check'], check=True)
for path in [s.VERIFY_ROOT, MODULE]:
    assert all(len(line) <= 100 for line in Path(path).read_text().splitlines())
for filename, names in [('ordinary-expected.txt', off), ('cfg-on-expected.txt', on),
                        ('g2-expected.txt', added)]:
    (OUT / filename).write_text(''.join(s.PREFIX + n + '\n' for n in sorted(names)))
(OUT / 'expected-covers.json').write_text(json.dumps(
    {s.PREFIX + n: 5 for n in sorted(added)}, indent=2) + '\n')
report = dict(validation='PASS', scope='source only; not compiler inventory or proof',
              g1_source=G1, tooling_base=TOOLING, ordinary=len(off), cfg_on=len(on),
              added=len(added), all_g1_roots_and_helpers_unchanged=True,
              request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
              expected_covers=25, watchdog_minutes=20, build_timeout_minutes=50,
              maximum_reservation_usd=0.675, own_spent_usd=0.4185,
              own_spent_plus_max_reservation_usd=1.0935)
(OUT / 'check-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
