#!/usr/bin/env python3
"""Small synthetic cross-check only; never invokes a Rust/proof toolchain."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('/root/verify-rust-std-ch8-s1-w11')
SOURCE = ROOT / 'library/core/src/slice/sort/shared/smallsort/verify'
OUT = Path(__file__).resolve().parent
CAP = 32


def snapshot(values, active=True):
    if not active:
        return (False, 0, ())
    if len(values) > CAP:
        return (False, 0, ())
    return (True, len(values), tuple(values))


def post(before, values, active=True):
    if not active:
        return True
    valid, old_len, old = before
    if not valid or old_len > CAP or len(values) > CAP or old_len != len(values):
        return False
    for i in range(1, old_len):
        if values[i] < values[i - 1]:
            return False
    for query in old:
        old_count = sum(value == query for value in old)
        new_count = sum(value == query for value in values)
        if old_count != new_count:
            return False
    return True


class NoRead:
    def __len__(self):
        raise AssertionError('inactive length read')

    def __iter__(self):
        raise AssertionError('inactive element read')


def main():
    # Reference oracle is Counter equality + standard adjacency, independent of
    # counting only queries from old input as the candidate algorithm does.
    alphabet = (0, 1, 2, 255)
    sequences = [p for n in range(4) for p in product(alphabet, repeat=n)]
    checked = 0
    for before in sequences:
        for after in sequences:
            expected = (len(before) == len(after)
                        and all(a <= b for a, b in zip(after, after[1:]))
                        and Counter(before) == Counter(after))
            assert post(snapshot(before), after) == expected
            checked += 1
    for n in (0, 1, 2, 3, 16, 31, 32):
        before = [255 if i % 2 else 0 for i in range(n)]
        assert post(snapshot(before), sorted(before))
        if n > 1:
            assert not post(snapshot(before), [0] * n)
    for a in range(256):
        for b in range(a + 1, 256):
            before = snapshot([a, b])
            assert post(before, [a, b])
            assert not post(before, [b, a])
            assert not post(before, [a, a])
    assert not post(snapshot([], active=False), [])
    assert snapshot([7] * 33)[0] is False
    assert not post(snapshot([7] * 33), [])
    assert not post(snapshot([7] * 32), [7] * 33)
    assert not post(snapshot([7] * 32), [7] * 31)
    assert post(snapshot(NoRead(), active=False), NoRead(), active=False)
    # Owned pre-state, rather than a borrowed list after mutation.
    mutable = [1, 2]
    before = snapshot(mutable)
    mutable[1] = 1
    assert not post(before, mutable)

    model = (SOURCE / 'sorting_model.rs').read_text()
    controls = (SOURCE / 'sorting_model_controls.rs').read_text()
    assert re.findall(r'^active_model!\((.+)\);$', model, re.M) == [
        'u8', 'Cell<u8>', 'NonCopyByte']
    assert re.findall(r'^key_less!\((.+)\);$', model, re.M) == [
        'u8', 'Cell<u8>', 'NonCopyByte']
    assert 'const CAP: usize = 32;' in model
    assert 'default fn snapshot(_values: &[T]) -> Snapshot { Snapshot::invalid() }' in model
    assert 'default fn post(_before: Snapshot, _values: &[T]) -> bool { true }' in model
    assert 'default fn enabled() -> bool { false }' in model
    assert 'pub(in crate::slice::sort::shared::smallsort) fn enabled<T, F>()' in model
    assert 'pub(in crate::slice::sort::shared::smallsort) fn snapshot<T, F>(values: &[T])' in model
    assert 'pub(in crate::slice::sort::shared::smallsort) fn post<T, F>(before: Snapshot, values: &[T])' in model
    assert 'unsafe' not in model
    assert 'use crate::kani;' in controls
    names = re.findall(r'^fn (\w+)\(', controls, re.M)
    roots = [n for n in names if n not in ('byte', 'sorted_prefix', 'strict_pair')]
    roots += re.findall(r'^positive!\((\w+),', controls, re.M)
    assert len(roots) == len(set(roots)) == 12, roots
    result = {
        'assurance': 'STATIC_AND_PYTHON_SYNTHETIC_ONLY',
        'rust_compilation': 'NOT_RUN', 'kani': 'NOT_RUN', 'ci': 'NOT_RUN',
        'sequence_pairs_n0_3': checked, 'strict_byte_pairs': 32640,
        'boundary_lengths': [0, 1, 2, 3, 16, 31, 32, 33],
        'opt_in_roots': sorted(roots),
        'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(SOURCE.glob('sorting_model*.rs'))},
        'result': 'PASS',
        'limits': 'Python is an independent finite sanity check, not Rust/Kani qualification.'
    }
    (OUT / 'synthetic-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
