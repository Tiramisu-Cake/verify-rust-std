"""CORR14 source/domain checks, not a Rust compiler or proof-evidence substitute."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = '7c0c345b857bca90cfebed4f204251b6e30eee9c'
PATH = 'library/core/src/slice/sort/shared/smallsort/verify/correct.rs'
OUT = Path('research/challenge-8/kani-k1/corr14')
source = Path(PATH).read_text()
old = subprocess.check_output(['git', 'show', f'{BASE}:{PATH}'], text=True)
assert source.startswith(old), 'existing symbols must remain byte-for-byte unchanged'
new = source[len(old):]
assert max(map(len, source.splitlines())) <= 100
assert not re.search(r'\bpub\b|\bselector\b|kani::any::<bool>|let stable|assume_init\(', new)


def body(name):
    return re.search(r'fn ' + name + r'\b[^\{]*\{(.*?)^\}', source, re.S | re.M)[1]


def compact(s):
    return re.sub(r'\s+', '', s)


baseline = body('general_stable_stub')
setup = baseline[baseline.index('set_value_probe'):baseline.index('let stable:')]
setup = setup.replace('::<T>', '::<u8>').replace('[T; N]', '[u8; 14]')
setup += 'let mut cmp = lt_u8;'
oracle = baseline[baseline.index('for i in 1..N'):baseline.index('kani::cover(stable')]
oracle = oracle.replace('::<T>', '::<u8>').replace('..N', '..14').replace(', N)', ', 14)')
checker_call = compact('corr14_check_u8_n14(&input, &output, &mut cmp);')
assert compact(body('corr14_check_u8_n14')) == compact(oracle)
assert new.count('probe_count_unrolled(input.as_ptr(), 14)') == 1
assert compact(new).count(checker_call) == 5
routes = ['general', 'stable_nonconst', 'stable_const', 'stable_aggregate']
for route in routes:
    b = compact(body(f'corr14_{route}_stub_u8_n14'))
    assert compact(setup) in b
    assert b.count(checker_call) == 1
    assert b.count('kani::cover(true,') == 1
    call = ('super::super::small_sort_general(&mut output, &mut cmp);' if route == 'general'
            else '<u8 as StableSmallSortTypeImpl>::small_sort(&mut output, '
                 + ('scratch' if route == 'stable_aggregate' else '&mut scratch') + ', &mut cmp);')
    assert compact(call) in b
    assert b.index(compact(call)) < b.index(checker_call) < b.index('kani::cover(true,')
assert '[MaybeUninit::<u8>::uninit();48]' in compact(body('corr14_stable_nonconst_stub_u8_n14'))
assert '[const{MaybeUninit::<u8>::uninit()};48]' in compact(body('corr14_stable_const_stub_u8_n14'))
a = compact(body('corr14_stable_aggregate_stub_u8_n14'))
assert 'MaybeUninit::<[u8;48]>::uninit()' in a and 'corr14_scratch_view(&mutholder)' in a
c = compact(body('stable_aggregate_value_corruption_control_u8_n14'))
assert compact(setup) in c and c.count(checker_call) == 1
assert c.index('::small_sort(') < c.index('output[0]^=1;') < c.index(checker_call)
b = compact(body('stable_aggregate_allocation_bounds_control_u8'))
assert '.cast::<u8>().wrapping_add(48)' in b and 'crate::ptr::write(outside,0)' in b
assert 'scratch[' not in b and 'ptr::read' not in b
# Every new top-level item/invocation is private and explicitly opt-in.
for m in re.finditer(r'^(?:fn |macro_rules! |corr14_stub_harness!\()', new, re.M):
    preceding = new[:m.start()].split('\n\n')[-1]
    assert '#[cfg(kani_smallsort_controls)]' in preceding
attrs = ['#[kani::proof]', '#[kani::solver(cadical)]', '#[kani::unwind(50)]']
attrs += [f'#[kani::stub_verified(crate::slice::sort::shared::smallsort::{t})]'
          for t in ['insert_tail', 'bidirectional_merge']]
for attr in attrs:
    expected = 2 if 'stub_verified' in attr else 3
    assert new.count(attr) == expected  # bounds performs no sort/callee call
production = Path('library/core/src/slice/sort/shared/smallsort.rs').read_text()
assert 'const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;' in production
assert 'SMALL_SORT_GENERAL_SCRATCH_LEN: usize = SMALL_SORT_GENERAL_THRESHOLD + 16;' in production
merge = Path('library/core/src/slice/sort/shared/smallsort/verify/merge.rs').read_text()
assert 'pub(crate) fn lt_u8(a: &u8, b: &u8) -> bool {\n    (*a >> 1) < (*b >> 1)' in merge
request = json.loads((OUT / 'g1.request.json').read_text())
assert len(request['harnesses']) == 7 and request['kani_jobs'] == 1 and request['controls']
assert request['harness_timeout_minutes'] == 10
result = dict(status='PASS', base=BASE, file=PATH, sha256=hashlib.sha256(source.encode()).hexdigest(),
              existing_source_unchanged=True, new_ordinary_harnesses=0, new_opt_in_harnesses=6,
              shared_checker_matches_baseline_oracle=True, positive_checker_calls=4,
              corruption_checker_call_after_mutation=True,
              max_columns=max(map(len, source.splitlines())), scratch_extent=48,
              rust_compilation='NOT_RUN_LOCAL', warnings_both_cfg='PENDING_CLOUD',
              interpretation='Static source check only; no AST/MIR equivalence or proof transfer.')
(OUT / 'static-check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
