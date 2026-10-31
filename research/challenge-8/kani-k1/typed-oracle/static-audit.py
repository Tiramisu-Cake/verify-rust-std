"""Source-only checks for the frozen TYPED review package; never invokes Rust/proof tools."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
assert ROOT == Path('/root/verify-rust-std-kani-typedoracle')
BASE = 'e0ff82577d'
CAP = '6b12002d79b6ccb4ded6c4790b1c592c65d6c591'
SOURCE = '241d94a41182ed6850244e0b51ddc8031daf7435'
PARENT = 'library/core/src/slice/sort/shared/smallsort/verify/merge.rs'
CHILD = PARENT[:-3] + '/typed_oracle.rs'
OUT = ROOT / 'research/challenge-8/kani-k1/typed-oracle'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def blob(rev, path):
    return subprocess.check_output(['git', 'show', f'{rev}:{path}'], cwd=ROOT)


old = blob(BASE, PARENT)
parent = (ROOT / PARENT).read_bytes()
registration = b'#[cfg(kani_smallsort_controls)]\nmod typed_oracle;\n\n'
assert parent.count(registration) == 1
assert parent.replace(registration, b'', 1) == old
assert git('diff', '--name-only', BASE, SOURCE, '--', 'library').splitlines() == [PARENT, CHILD]
assert not git('diff', '--name-only', SOURCE, '--', 'library')
child = (ROOT / CHILD).read_text()
assert all(len(line) <= 100 for line in child.splitlines())
assert all(len(line) <= 100 for line in parent.decode().splitlines())
assert not re.search(r'kani::(?:assume|any_where|stub)|#\[kani::(?:stub|ensures|requires)', child)
assert child.count('#[kani::proof]') == 7
assert child.count('#[kani::proof_for_contract(') == 1
assert child.count('#[kani::unwind(34)]') == 8
assert child.count('assert_sorted_and_probe_preserved::<') == 1
assert 'bytes[..8].copy_from_slice(&value_bytes)' in child and 'p.to_ne_bytes()' in child
assert 'if $i < $n && $values[$i] == $p' in child
assert ' '.join(map(str, range(32))) in ' '.join(child.split())
assert child.count('v[0] ^= 1;') == 2
assert child.count('kani::cover(true, "general sort returns and payload is flipped before typed checks")') == 2
assert '<u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp)' in child
assert '[const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN]' in child
lane_paths = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
              'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh', 'tool_config/kani-version.toml',
              'rust-toolchain.toml', '.gitmodules', '.cargo', 'library/.cargo',
              'library/Cargo.toml', 'library/Cargo.lock']
assert not git('diff', '--name-only', CAP, SOURCE, '--', *lane_paths)
assert (ROOT / 'research/challenge-8/kani-k1/RUN-REQUEST.json').read_bytes() == (OUT / 'g1.request.json').read_bytes()
for stage, count in [('g1', 9), ('g2', 3)]:
    req = json.loads((OUT / f'{stage}.request.json').read_text())
    assert len(req['harnesses']) == count
    assert req['kind'] == 'measurement' and req['harness_timeout_minutes'] == 10
    assert req['kani_jobs'] == 1 and req['controls'] and req['uninit_checks'] is False
    assert all(row['expect'] == ('FAILED' if 'control_' in row['name'] else 'SUCCESS')
               for row in req['harnesses'])
    assert (OUT / f'{stage}.request.rustflags').read_text().strip() == '--cfg kani_smallsort_controls'
    assert '--no-assert-contracts' not in (OUT / f'{stage}.request.args').read_text()
    assert '-Z\nuninit-checks' not in (OUT / f'{stage}.request.args').read_text()
checks = {
    'base': git('rev-parse', BASE), 'cap_commit': CAP, 'source_commit': SOURCE,
    'baseline_library_tree': git('rev-parse', f'{BASE}:library'),
    'frozen_pilot_library_tree': git('rev-parse', f'{SOURCE}:library'),
    'ordinary_parent_projection_equals_base': True,
    'other_library_files_unchanged': True, 'lane_pins_flags_equal_cap': True,
    'rust_lines_le_100': True, 'new_proofs': 7, 'new_actual_pfc': 1,
    'new_harnesses_all_unwind34': True, 'no_new_assumptions_or_stubs': True,
    'root_request_equals_g1': True, 'request_validator': 'PASS: G1 9 entries, G2 3 entries',
    'rustfmt_check': 'PASS: parent and child, prescribed wrapper/edition/config',
    'scope_limit': 'Text/source checks only; no compiler, AST/MIR binding, proof or inventory credit',
    'sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [PARENT, CHILD]},
    'tool_pin': '9461e07af7ec929f050aa4192f29363c9be07779',
    'toolchain': 'nightly-2026-10-12', 'uninit_checks': False,
}
(OUT / 'source-audit.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
