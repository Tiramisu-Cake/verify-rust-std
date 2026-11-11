#!/usr/bin/env python3
"""Finite offset-algebra sanity; does not execute or prove the Rust implementation."""
import json
from itertools import product


def mask(size, chunks):
    return [any(start <= byte < start + count for start, count in chunks) for byte in range(size)]


def shift(chunks, offset):
    return [(start + offset, count) for start, count in chunks]


def compose(size, chunks, offset):
    return [(offset, 1)] + shift(chunks, offset)


cases = 0
old_false_equalities = 0
for size in range(2, 9):
    # Exhaust all masks whose tag byte is outside the variant field data.
    layouts = [[(i + 1, 1) for i, bit in enumerate(bits) if bit]
               for bits in product((False, True), repeat=size - 1)]
    for left, right in product(layouts, repeat=2):
        equal = mask(size, left) == mask(size, right)
        for offset in (0, 1, size - 1, size, size + 16):
            old_equal = mask(size, shift(left, offset)) == mask(size, shift(right, offset))
            old_false_equalities += old_equal and not equal
            if equal:
                result = mask(offset + size + 1, compose(size, left, offset))
                assert not any(result[:offset])
                assert result[offset:offset + size] == mask(size, [(0, 1)] + left)
                assert not result[-1]
            cases += 1

# The distinguishing fixture: Different::A data at 4..9, B at 4..8.
a, b = [(4, 4), (8, 1)], [(4, 4)]
assert mask(12, shift(a, 16)) == mask(12, shift(b, 16))
assert mask(12, a) != mask(12, b)
# Pat over a wide pointer: prefix byte 0, pointer bytes 8..24, padding 1..8.
pat = mask(24, [(0, 1)] + shift([(0, 8), (8, 8)], 8))
assert pat == [True] + [False] * 7 + [True] * 16
old_pat = mask(24, [(0, 1), (0, 8), (8, 8)])
assert old_pat[1] and not pat[1] and not old_pat[16] and pat[16]
# Two levels of enum composition, then an array's second element stride.
inner = compose(8, [(4, 4)], 4)
outer = compose(16, inner, 16)
assert outer == [(16, 1), (20, 1), (24, 4)]
assert shift(outer, 32) == [(48, 1), (52, 1), (56, 4)]
print(json.dumps({"cases": cases, "old_false_equalities": old_false_equalities,
                  "result": "PASS", "assurance": "finite offset algebra only; no Rust/proof credit"}))
